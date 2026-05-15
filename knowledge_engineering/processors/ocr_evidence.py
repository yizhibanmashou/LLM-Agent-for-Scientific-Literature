"""Cross-channel OCR evidence extraction and scoring.

The structured JSON remains the primary artifact.  This module only normalizes
Paddle raw layout and GLM OCR output into comparable evidence records so fusion
and audits can reason about caption/body binding without channel-specific code.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any, Iterable

from knowledge_engineering.core.common import (
    collapse_ws,
    HTML_TAG_RE,
    rows_from_html_table,
    strip_html,
    table_body_text_from_rows,
)
from knowledge_engineering.core.runtime import TableEntry


TABLE_LABEL_RE = re.compile(r"\bTable\s+(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\b", re.IGNORECASE)
FORMULA_NUMBER_RE = re.compile(r"\(\s*(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\s*\)")
HTML_TABLE_RE = re.compile(r"<table\b[\s\S]*?</table>", re.IGNORECASE)
STRUCTURED_PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE):[^\]]+\]\]", re.IGNORECASE)
TEX_COMMAND_RE = re.compile(r"\\[A-Za-z@]+(?:\*?)")
PADDLE_RAW_FILE_NAMES = (
    "paddle_raw_api_response.json",
    "paddle_raw_response.json",
)
TABLE_CAPTION_LABELS = {"figure_title", "text", "paragraph_title"}
FORMULA_LABELS = {"display_formula", "formula_number"}
TABLE_BODY_LABELS = {"table"}
TABLE_CONTINUATION_LABELS = {"text", "display_formula", "formula", "inline_formula"}
TABLE_CONTINUATION_FORMULA_LABELS = {"display_formula", "formula", "inline_formula"}
TABLE_CONTINUATION_TEXT_LABELS = {"text"}
FORMULA_TABLE_LABEL_TEXT_RE = re.compile(r"^[A-Z][^.!?]{8,220}(?::\s+[^.!?]{1,220})?$")
FORMULA_TABLE_FORMULA_ID_RE = re.compile(r"^\d+\.\d+[A-Za-z]$")
STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "from",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "not",
    "but",
    "can",
    "into",
    "than",
    "then",
    "such",
    "these",
    "those",
    "over",
    "under",
    "between",
    "which",
    "where",
    "when",
    "while",
    "also",
    "only",
    "any",
    "all",
    "one",
    "two",
    "its",
    "their",
    "there",
    "using",
    "used",
    "table",
}
VISUAL_TABLE_SCHEMA = "visual_table_evidence.v1"


@dataclass(frozen=True)
class OCREvidence:
    object_type: str
    object_id: str
    chapter: str
    source_channel: str
    source_path: str
    page: int | None
    order: float
    caption_text: str = ""
    body_html: str = ""
    body_text: str = ""
    bbox: list[Any] | None = None
    rows: tuple[tuple[str, ...], ...] = ()
    source_payload: dict[str, Any] = field(default_factory=dict)

    def stable_hash(self) -> str:
        payload = {
            "object_type": self.object_type,
            "object_id": self.object_id,
            "chapter": self.chapter,
            "source_channel": self.source_channel,
            "caption_text": self.caption_text,
            "body_html": self.body_html,
            "body_text": self.body_text,
            "rows": self.rows,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class OCREvidenceIndex:
    evidences: list[OCREvidence] = field(default_factory=list)

    def by_type_and_id(self, object_type: str, object_id: str) -> list[OCREvidence]:
        normalized_id = str(object_id or "").strip()
        normalized_type = str(object_type or "").strip().lower()
        return [
            evidence
            for evidence in self.evidences
            if evidence.object_type == normalized_type and evidence.object_id == normalized_id
        ]

    def tables(self, table_id: str | None = None, chapter: str | None = None) -> list[OCREvidence]:
        table_id_value = str(table_id or "").strip()
        chapter_value = str(chapter or "").strip().lower()
        return [
            evidence
            for evidence in self.evidences
            if evidence.object_type == "table"
            and (not table_id_value or evidence.object_id == table_id_value)
            and (not chapter_value or evidence.chapter == chapter_value)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_count": len(self.evidences),
            "by_channel": dict(sorted(_count_by_channel(self.evidences).items())),
            "evidences": [evidence_to_dict(evidence) for evidence in self.evidences],
        }


def evidence_to_dict(evidence: OCREvidence) -> dict[str, Any]:
    return {
        "object_type": evidence.object_type,
        "object_id": evidence.object_id,
        "chapter": evidence.chapter,
        "source_channel": evidence.source_channel,
        "source_path": evidence.source_path,
        "page": evidence.page,
        "order": evidence.order,
        "caption_text": evidence.caption_text,
        "body_text": evidence.body_text,
        "body_html": evidence.body_html,
        "bbox": evidence.bbox,
        "rows": [list(row) for row in evidence.rows],
        "source_payload": evidence.source_payload,
        "hash": evidence.stable_hash(),
    }


def _count_by_channel(evidences: Iterable[OCREvidence]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for evidence in evidences:
        counts[evidence.source_channel] += 1
    return dict(counts)


def clean_ocr_text(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"</?div[^>]*>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"^#+\s*", "", value.strip())
    return collapse_ws(value)


def table_body_text(entry_or_html: TableEntry | str, rows: Iterable[Iterable[Any]] | None = None) -> str:
    if isinstance(entry_or_html, TableEntry):
        entry_rows = entry_or_html.rows or []
        row_text = table_body_text_from_rows(entry_rows)
        html_text = strip_html(entry_or_html.html or "")
        raw_text = str(getattr(entry_or_html, "raw_body", "") or "")
        markdown_text = str(getattr(entry_or_html, "markdown_body", "") or "")
        return collapse_ws(f"{row_text} {html_text} {raw_text} {markdown_text}")
    if rows is not None:
        row_text = table_body_text_from_rows(rows)
        html_text = strip_html(str(entry_or_html or ""))
        return collapse_ws(f"{row_text} {html_text}")
    return strip_html(str(entry_or_html or ""))


def _is_short_table_header(rows: list[list[str]], body_text: str) -> bool:
    if not rows:
        return False
    cell_count = sum(len(row) for row in rows)
    return len(rows) <= 3 and cell_count <= 8 and len(normalize_for_similarity(body_text).split()) <= 32


def _table_continuation_stop(
    *,
    block: dict[str, Any],
    table_id: str,
    collected_blocks: list[dict[str, Any]],
) -> bool:
    label = str(block.get("label") or "").strip().lower()
    content = clean_ocr_text(str(block.get("content") or ""))
    if not content:
        return False
    if label in {"doc_title", "paragraph_title"}:
        return True
    if re.match(r"^#{1,6}\s+", content):
        return True
    caption_label = _caption_label(content)
    if caption_label and caption_label != table_id:
        return True
    if len(collected_blocks) >= 4 and label in TABLE_CONTINUATION_TEXT_LABELS:
        if re.match(r"^[a-z]", content) and len(content) >= 80:
            return True
        if len(content) >= 180 and re.search(r"\.\s+[A-Z]", content):
            return True
    return False


def _collect_table_continuation_blocks(
    *,
    page_blocks: list[dict[str, Any]],
    table_block: dict[str, Any],
    table_id: str,
) -> list[dict[str, Any]]:
    table_index = int(table_block.get("index") or 0)
    continuation: list[dict[str, Any]] = []
    for block in page_blocks:
        try:
            block_index = int(block.get("index") or 0)
        except (TypeError, ValueError):
            block_index = 0
        if block_index <= table_index:
            continue
        label = str(block.get("label") or "").strip().lower()
        if _table_continuation_stop(block=block, table_id=table_id, collected_blocks=continuation):
            break
        if label not in TABLE_CONTINUATION_LABELS:
            continue
        content = clean_ocr_text(str(block.get("content") or ""))
        if not content:
            continue
        continuation.append({"label": label, "content": content, "bbox": block.get("bbox"), "index": block_index})
    return continuation


def _continuation_supports_table_expansion(blocks: list[dict[str, Any]]) -> bool:
    formula_count = sum(1 for block in blocks if block["label"] in TABLE_CONTINUATION_FORMULA_LABELS)
    text_count = sum(1 for block in blocks if block["label"] in TABLE_CONTINUATION_TEXT_LABELS)
    token_count = len(normalize_for_similarity(" ".join(block["content"] for block in blocks)).split())
    return formula_count >= 2 and text_count >= 2 and token_count >= 24


def _render_rows_as_html(rows: list[list[str]]) -> str:
    rendered_rows: list[str] = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(cell or '')).replace(chr(10), '<br>')}</td>" for cell in row)
        rendered_rows.append(f"<tr>{cells}</tr>")
    return "<table>" + "".join(rendered_rows) + "</table>"


def _markdown_escape_cell(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def _render_rows_as_markdown(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [list(row) + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(_markdown_escape_cell(cell) for cell in normalized[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    for row in normalized[1:]:
        lines.append("| " + " | ".join(_markdown_escape_cell(cell) for cell in row) + " |")
    return "\n".join(lines)


def _expanded_rows_from_continuation(
    *,
    rows: list[list[str]],
    continuation_blocks: list[dict[str, Any]],
) -> list[list[str]]:
    expanded_rows = [list(row) for row in rows]
    label_parts: list[str] = []
    formula_parts: list[str] = []

    def flush() -> None:
        nonlocal label_parts, formula_parts
        if label_parts or formula_parts:
            expanded_rows.append([collapse_ws(" ".join(label_parts)), "\n\n".join(formula_parts).strip()])
        label_parts = []
        formula_parts = []

    for block in continuation_blocks:
        label = block["label"]
        content = str(block["content"] or "").strip()
        if not content:
            continue
        if label in TABLE_CONTINUATION_FORMULA_LABELS:
            formula_parts.append(content)
            continue
        if label in TABLE_CONTINUATION_TEXT_LABELS:
            if label_parts and formula_parts:
                flush()
            label_parts.append(content)
    flush()
    return expanded_rows


def _maybe_expand_table_body_from_continuation(
    *,
    page_blocks: list[dict[str, Any]],
    table_block: dict[str, Any],
    table_id: str,
    table_html: str,
    rows: list[list[str]],
) -> tuple[str, list[list[str]], str, dict[str, Any]]:
    body_text = table_body_text(table_html, rows)
    if not _is_short_table_header(rows, body_text):
        return table_html, rows, body_text, {}

    continuation_blocks = _collect_table_continuation_blocks(
        page_blocks=page_blocks,
        table_block=table_block,
        table_id=table_id,
    )
    if not _continuation_supports_table_expansion(continuation_blocks):
        return table_html, rows, body_text, {}

    expanded_rows = _expanded_rows_from_continuation(rows=rows, continuation_blocks=continuation_blocks)
    raw_body = "\n\n".join([body_text, *[block["content"] for block in continuation_blocks]]).strip()
    markdown_body = _render_rows_as_markdown(expanded_rows)
    expanded_html = _render_rows_as_html(expanded_rows)
    return (
        expanded_html,
        expanded_rows,
        table_body_text(expanded_html, expanded_rows),
        {
            "table_body_expanded_from_following_blocks": True,
            "expanded_block_count": len(continuation_blocks),
            "raw_body": raw_body,
            "markdown_body": markdown_body,
        },
    )


def _normalize_formula_table_label(text: str) -> str:
    value = clean_ocr_text(text)
    value = re.sub(r"\s+([:;,])", r"\1", value)
    first_sentence = re.match(r"^(Selection\b[^.]{8,160}|Divergent\b[^.]{8,160})\.\s+", value)
    if first_sentence:
        value = first_sentence.group(1)
    return value.rstrip(".")


def _is_formula_table_label_block(block: dict[str, Any]) -> bool:
    if str(block.get("label") or "").strip().lower() != "text":
        return False
    content = _normalize_formula_table_label(str(block.get("content") or ""))
    if not content:
        return False
    if TABLE_LABEL_RE.search(content) or FORMULA_NUMBER_RE.fullmatch(content):
        return False
    if len(content) > 240:
        return False
    visible_prefix = re.sub(r"^\s*\$[^$]+\$\s*", "", content).strip()
    if re.match(
        r"^(?:Using|Considering|Likewise|The|This|These|Those|Thus|Hence|Where|When|If|For|In|As)\b",
        visible_prefix,
    ):
        return False
    if re.match(r"^[a-z]", content):
        return False
    if re.search(r"\.\s+[A-Z]", content):
        return False
    if FORMULA_TABLE_LABEL_TEXT_RE.match(_normalize_formula_table_label(content)):
        return True
    if len(content) <= 180 and re.match(r"^\s*(?:\$[^$]+\$\s+)?[A-Za-z0-9][^.!?]+(?:\([^)]{1,80}\))?$", content):
        return True
    return False


def _is_formula_table_label_continuation_block(block: dict[str, Any]) -> bool:
    if str(block.get("label") or "").strip().lower() != "text":
        return False
    content = clean_ocr_text(str(block.get("content") or ""))
    if not content or len(content) > 180:
        return False
    if TABLE_LABEL_RE.search(content) or FORMULA_NUMBER_RE.fullmatch(content):
        return False
    if re.search(r"\.\s+[A-Z]", content):
        return False
    stripped = content.lstrip()
    return (
        stripped.startswith(("$", "(", "["))
        or bool(re.search(r"\b(?:where|with|for)\b", content, flags=re.IGNORECASE))
    ) and bool(re.search(r"[$\\_{}=]|\bn\s*=", content))


def _is_formula_table_split_label_tail(block: dict[str, Any]) -> bool:
    if str(block.get("label") or "").strip().lower() != "text":
        return False
    content = _normalize_formula_table_label(str(block.get("content") or ""))
    if not content or len(content) > 90:
        return False
    if TABLE_LABEL_RE.search(content) or FORMULA_NUMBER_RE.fullmatch(content):
        return False
    if re.search(r"[$\\_{}=]|\.\s+[A-Z]", content):
        return False
    return bool(re.match(r"^[a-z]", content))


def _block_left(block: dict[str, Any]) -> float | None:
    bbox = block.get("bbox")
    if not isinstance(bbox, (list, tuple)) or len(bbox) < 1:
        return None
    try:
        return float(bbox[0])
    except (TypeError, ValueError):
        return None


def _block_top(block: dict[str, Any]) -> float | None:
    bbox = block.get("bbox")
    if not isinstance(bbox, (list, tuple)) or len(bbox) < 2:
        return None
    try:
        return float(bbox[1])
    except (TypeError, ValueError):
        return None


def _split_label_tail_matches_layout(
    *,
    tail_block: dict[str, Any],
    label_blocks: list[dict[str, Any]],
    formula_block: dict[str, Any] | None,
) -> bool:
    tail_left = _block_left(tail_block)
    if tail_left is None:
        return True
    label_lefts = [left for block in label_blocks if (left := _block_left(block)) is not None]
    formula_left = _block_left(formula_block or {})
    if label_lefts and tail_left <= max(label_lefts) + 80:
        return True
    return formula_left is not None and tail_left < formula_left - 40


def _formula_id_supports_table(table_id: str, formula_id: str) -> bool:
    table_match = re.match(r"^(?P<chapter>\d+)\.(?P<table>\d+)", str(table_id or ""))
    formula_match = re.match(r"^(?P<chapter>\d+)\.(?P<formula>\d+)(?P<suffix>[A-Za-z]?)$", str(formula_id or ""))
    if not table_match or not formula_match:
        return False
    if table_match.group("chapter") != formula_match.group("chapter"):
        return False
    return bool(re.fullmatch(r"\d+\.\d+[A-Za-z]?", formula_id))


def _formula_table_stop(
    *,
    block: dict[str, Any],
    table_id: str,
    collected_rows: list[list[str]],
    visual_bottom: float | None = None,
) -> bool:
    label = str(block.get("label") or "").strip().lower()
    content = clean_ocr_text(str(block.get("content") or ""))
    if not content:
        return False
    if label in {"doc_title", "paragraph_title", "figure_title", "table"}:
        if TABLE_LABEL_RE.search(content):
            return True
        if label != "figure_title":
            return True
    caption_label = _caption_label(content)
    if caption_label and caption_label != table_id:
        return True
    if label == "text" and collected_rows:
        if re.match(r"^[a-z]", content):
            return True
        if len(content) >= 120 and re.search(r"\.\s+[A-Z]", content):
            return True
    top = _block_top(block)
    if visual_bottom is not None and top is not None and top > visual_bottom + 8 and collected_rows:
        return True
    return False


def _collect_formula_table_rows(
    *,
    page_blocks: list[dict[str, Any]],
    caption: dict[str, Any],
    table_id: str,
    visual_bottom: float | None = None,
) -> tuple[list[list[str]], list[dict[str, Any]]]:
    try:
        caption_index = int(caption.get("index") or 0)
    except (TypeError, ValueError):
        caption_index = 0

    rows: list[list[str]] = []
    source_blocks: list[dict[str, Any]] = []
    pending_label = ""
    pending_formula = ""
    pending_formula_block: dict[str, Any] | None = None
    pending_label_blocks: list[dict[str, Any]] = []

    def flush(formula_id: str = "") -> None:
        nonlocal pending_label, pending_formula, pending_formula_block, pending_label_blocks
        if pending_label and pending_formula:
            formula_cell = (
                f"[[SEE_FORMULA:{formula_id}]]"
                if formula_id and _formula_id_supports_table(table_id, formula_id)
                else pending_formula
            )
            rows.append([pending_label, formula_cell])
            if pending_formula_block is not None:
                source_blocks.append(pending_formula_block)
        pending_label = ""
        pending_formula = ""
        pending_formula_block = None
        pending_label_blocks = []

    for block in page_blocks:
        try:
            block_index = int(block.get("index") or 0)
        except (TypeError, ValueError):
            block_index = 0
        if block_index <= caption_index:
            continue
        label = str(block.get("label") or "").strip().lower()
        content = clean_ocr_text(str(block.get("content") or ""))
        if not content:
            continue
        if label == "paragraph_title" and content.rstrip().endswith(":"):
            top = _block_top(block)
            if visual_bottom is None or top is None or top <= visual_bottom + 8:
                flush()
                rows.append([content, ""])
                source_blocks.append(block)
                continue
        is_split_label_tail = (
            pending_label
            and pending_formula
            and _is_formula_table_split_label_tail(block)
            and _split_label_tail_matches_layout(
                tail_block=block,
                label_blocks=pending_label_blocks,
                formula_block=pending_formula_block,
            )
        )
        if not is_split_label_tail and _formula_table_stop(
            block=block,
            table_id=table_id,
            collected_rows=rows,
            visual_bottom=visual_bottom,
        ):
            break
        if is_split_label_tail:
            pending_label = collapse_ws(f"{pending_label} {_normalize_formula_table_label(content)}")
            source_blocks.append(block)
            continue
        if pending_label and not pending_formula and _is_formula_table_label_continuation_block(block):
            pending_label = collapse_ws(f"{pending_label} {_normalize_formula_table_label(content)}")
            pending_label_blocks.append(block)
            source_blocks.append(block)
            continue
        if _is_formula_table_label_block(block):
            if pending_label and pending_formula:
                flush()
            pending_label = _normalize_formula_table_label(content)
            pending_label_blocks = [block]
            source_blocks.append(block)
            continue
        if label in TABLE_CONTINUATION_FORMULA_LABELS and pending_label:
            pending_formula = content
            pending_formula_block = block
            continue
        if label == "formula_number" and pending_label and pending_formula:
            match = FORMULA_NUMBER_RE.search(content)
            if not match:
                break
            flush(match.group("label"))
            continue
        if rows:
            break
    if pending_label and pending_formula:
        flush()
    return rows, source_blocks


def _extract_formula_table_evidences_from_page(
    *,
    page_blocks: list[dict[str, Any]],
    captions: list[dict[str, Any]],
    visual_rules: list[dict[str, Any]] | None = None,
    chapter: str,
    source_channel: str,
    source_path: Path,
    page_index: int,
    occupied_table_ids: set[str],
) -> list[OCREvidence]:
    evidences: list[OCREvidence] = []
    for caption in captions:
        table_id = str(caption.get("object_id") or "").strip()
        if not table_id or table_id in occupied_table_ids:
            continue
        caption_top = _block_top(caption)
        visual_bottom = None
        if caption_top is not None:
            rule_tops: list[float] = []
            for rule in visual_rules or []:
                bbox = rule.get("bbox")
                if not isinstance(bbox, (list, tuple)) or len(bbox) < 2:
                    continue
                try:
                    top = float(bbox[1])
                except (TypeError, ValueError):
                    continue
                if top > caption_top + 12:
                    rule_tops.append(top)
            if rule_tops:
                visual_bottom = min(rule_tops)
        rows, source_blocks = _collect_formula_table_rows(
            page_blocks=page_blocks,
            caption=caption,
            table_id=table_id,
            visual_bottom=visual_bottom,
        )
        if len(rows) < 2:
            continue
        header = ["Selection scheme", "Formula"]
        table_rows = [header, *rows]
        body_html = _render_rows_as_html(table_rows)
        markdown_body = _render_rows_as_markdown(table_rows)
        raw_body = "\n\n".join(
            [str(caption.get("content") or ""), *[str(block.get("content") or "") for block in source_blocks]]
        ).strip()
        following_start = max(
            [int(block.get("index") or 0) for block in source_blocks]
            or [int(caption.get("index") or 0)]
        )
        following_body = _first_following_body_text(
            page_blocks=page_blocks,
            start_index=following_start,
        )
        evidences.append(
            OCREvidence(
                object_type="table",
                object_id=table_id,
                chapter=chapter,
                source_channel=source_channel,
                source_path=str(source_path),
                page=page_index,
                order=float(caption.get("order") or 0.0),
                caption_text=str(caption.get("content") or "").strip(),
                body_html=body_html,
                body_text=table_body_text(body_html, table_rows),
                bbox=caption.get("bbox"),
                rows=tuple(tuple(str(cell) for cell in row) for row in table_rows),
                source_payload={
                    "table_special_type": "formula_table",
                    "formula_table_recovered_from_caption_following_blocks": True,
                    "formula_table_row_count": len(rows),
                    "visual_bottom_rule_y": visual_bottom,
                    "following_body": following_body,
                    "raw_body": raw_body,
                    "markdown_body": markdown_body,
                },
            )
        )
    return evidences


def normalize_for_similarity(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = STRUCTURED_PLACEHOLDER_RE.sub(" ", value)
    value = HTML_TAG_RE.sub(" ", value)
    value = TEX_COMMAND_RE.sub(" ", value)
    value = re.sub(r"[_^{}$()[\],.;:!?/\\|+=<>*\"'`~\-]+", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return collapse_ws(value).lower()


def token_set(text: str) -> set[str]:
    normalized = normalize_for_similarity(text)
    return {
        token
        for token in normalized.split()
        if len(token) > 1 and token not in STOPWORDS
    }


def token_overlap_score(left: str, right: str) -> float:
    left_tokens = token_set(left)
    right_tokens = token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    containment = max(overlap / len(left_tokens), overlap / len(right_tokens))
    jaccard = overlap / max(1, len(left_tokens | right_tokens))
    return round(0.72 * containment + 0.28 * jaccard, 4)


def sequence_score(left: str, right: str) -> float:
    left_norm = normalize_for_similarity(left)
    right_norm = normalize_for_similarity(right)
    if not left_norm or not right_norm:
        return 0.0
    if len(left_norm) > 32 and (left_norm in right_norm or right_norm in left_norm):
        return 0.98
    return round(SequenceMatcher(None, left_norm[:1200], right_norm[:1200]).ratio(), 4)


def _bbox_center(bbox: list[Any] | None) -> tuple[float, float] | None:
    if not isinstance(bbox, list) or len(bbox) < 4:
        return None
    try:
        x1, y1, x2, y2 = (float(item) for item in bbox[:4])
    except (TypeError, ValueError):
        return None
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return ((left + right) / 2.0, (top + bottom) / 2.0)


def _bbox_distance(left_bbox: list[Any] | None, right_bbox: list[Any] | None) -> float:
    left_center = _bbox_center(left_bbox)
    right_center = _bbox_center(right_bbox)
    if not left_center or not right_center:
        return 999999.0
    return abs(left_center[1] - right_center[1]) + abs(left_center[0] - right_center[0]) * 0.25


def _bbox_horizontal_overlap_ratio(left_bbox: list[Any] | None, right_bbox: list[Any] | None) -> float:
    if not isinstance(left_bbox, list) or len(left_bbox) < 4:
        return 0.0
    if not isinstance(right_bbox, list) or len(right_bbox) < 4:
        return 0.0
    try:
        left_x1, _left_y1, left_x2, _left_y2 = (float(item) for item in left_bbox[:4])
        right_x1, _right_y1, right_x2, _right_y2 = (float(item) for item in right_bbox[:4])
    except (TypeError, ValueError):
        return 0.0
    left_min, left_max = sorted((left_x1, left_x2))
    right_min, right_max = sorted((right_x1, right_x2))
    overlap = max(0.0, min(left_max, right_max) - max(left_min, right_min))
    return overlap / max(min(left_max - left_min, right_max - right_min), 1.0)


def _block_order(block: dict[str, Any], fallback: int) -> float:
    for key in ("block_order", "order", "index", "block_id"):
        value = block.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return float(fallback)


def _block_label(block: dict[str, Any]) -> str:
    return str(block.get("block_label") or block.get("label") or "").strip().lower()


def _block_content(block: dict[str, Any]) -> str:
    return str(block.get("block_content") or block.get("content") or "").strip()


def _block_bbox(block: dict[str, Any]) -> list[Any] | None:
    bbox = block.get("block_bbox") or block.get("bbox_2d") or block.get("bbox")
    return bbox if isinstance(bbox, list) else None


def _iter_page_blocks(payload: Any) -> Iterable[tuple[int, list[dict[str, Any]]]]:
    pages: list[Any]
    if isinstance(payload, list):
        pages = payload
    elif isinstance(payload, dict):
        result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
        pages = (
            result.get("layoutParsingResults")
            or payload.get("layoutParsingResults")
            or payload.get("pages")
            or payload.get("data")
            or payload.get("result")
            or []
        )
    else:
        pages = []

    if not isinstance(pages, list):
        return

    for page_index, page in enumerate(pages, start=1):
        if isinstance(page, list):
            blocks = page
        elif isinstance(page, dict):
            pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else page
            blocks = (
                pruned.get("parsing_res_list")
                or page.get("parsing_res_list")
                or page.get("blocks")
                or page.get("items")
                or []
            )
        else:
            blocks = []
        if isinstance(blocks, list):
            yield page_index, [block for block in blocks if isinstance(block, dict)]


def _load_json_payload(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _caption_label(caption_text: str) -> str:
    match = TABLE_LABEL_RE.search(caption_text or "")
    return str(match.group("label") or "").strip() if match else ""


def _caption_crosses_another_table_label(caption_text: str, table_id: str) -> bool:
    labels = [str(match.group("label") or "").strip() for match in TABLE_LABEL_RE.finditer(caption_text or "")]
    return any(label and label != table_id for label in labels)


def _caption_candidates(page_blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, block in enumerate(page_blocks):
        label = _block_label(block)
        content = clean_ocr_text(_block_content(block))
        table_id = _caption_label(content)
        if not table_id:
            continue
        if not TABLE_LABEL_RE.match(content):
            continue
        if label not in TABLE_CAPTION_LABELS and "table" not in content.lower():
            continue
        candidates.append(
            {
                "content": content,
                "object_id": table_id,
                "bbox": _block_bbox(block),
                "order": _block_order(block, index),
                "index": index,
            }
        )
    return candidates


def _normalized_block_order(block: dict[str, Any], fallback: int = 0) -> float:
    for key in ("order", "block_order", "index", "block_id"):
        value = block.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return float(fallback)


def _caption_table_boundary_crossed(
    caption: dict[str, Any],
    table_block: dict[str, Any],
    page_blocks: list[dict[str, Any]],
) -> bool:
    caption_order = _normalized_block_order(caption)
    table_order = _normalized_block_order(table_block)
    if table_order <= caption_order:
        return True
    for block in page_blocks:
        if block is caption or block is table_block:
            continue
        order = _normalized_block_order(block)
        if not (caption_order < order < table_order):
            continue
        content = clean_ocr_text(str(block.get("content") or ""))
        if not content:
            continue
        if re.match(r"^(?:Example|Figure)\s+\d+(?:\.\d+)?[A-Za-z]?\b", content, flags=re.IGNORECASE):
            return True
        if TABLE_LABEL_RE.match(content):
            return True
    return False


def _select_caption_for_table(
    table_block: dict[str, Any],
    table_index: int,
    captions: list[dict[str, Any]],
    page_blocks: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    if not captions:
        return None
    table_bbox = table_block.get("bbox")
    table_order = float(table_block.get("order") or table_index)

    def caption_sort_key(caption: dict[str, Any]) -> tuple[int, float, float]:
        caption_order = float(caption.get("order") or 0.0)
        after_penalty = 0 if caption_order <= table_order + 1.0 else 1
        return (
            after_penalty,
            _bbox_distance(table_bbox, caption.get("bbox")),
            abs(caption_order - table_order),
        )

    valid_captions = [
        caption
        for caption in captions
        if page_blocks is None or not _caption_table_boundary_crossed(caption, table_block, page_blocks)
    ]
    if not valid_captions:
        return None
    return sorted(valid_captions, key=caption_sort_key)[0]


def _caption_table_pairs_by_reading_order(
    *,
    captions: list[dict[str, Any]],
    table_blocks: list[dict[str, Any]],
    page_blocks: list[dict[str, Any]] | None = None,
) -> dict[int, dict[str, Any]]:
    if len(captions) < 2 or len(table_blocks) < 2:
        return {}
    ordered_captions = sorted(captions, key=lambda item: float(item.get("order") or 0.0))
    ordered_tables = sorted(enumerate(table_blocks), key=lambda item: float(item[1].get("order") or item[0]))
    if len(ordered_captions) != len(ordered_tables):
        return {}

    pairs: dict[int, dict[str, Any]] = {}
    previous_table_order = -1.0
    for caption, (table_index, table_block) in zip(ordered_captions, ordered_tables):
        caption_order = float(caption.get("order") or 0.0)
        table_order = float(table_block.get("order") or table_index)
        if table_order <= caption_order or table_order <= previous_table_order:
            return {}
        if page_blocks is not None and _caption_table_boundary_crossed(caption, table_block, page_blocks):
            return {}
        pairs[table_index] = caption
        previous_table_order = table_order
    return pairs


def _page_size_from_payload_page(page: Any) -> tuple[int | None, int | None]:
    if not isinstance(page, dict):
        return None, None
    width = page.get("width")
    height = page.get("height")
    if (width is None or height is None) and isinstance(page.get("prunedResult"), dict):
        width = page["prunedResult"].get("width", width)
        height = page["prunedResult"].get("height", height)
    try:
        return int(width), int(height)
    except (TypeError, ValueError):
        return None, None


def _iter_payload_pages(payload: Any) -> Iterable[tuple[int, Any]]:
    if isinstance(payload, list):
        pages = payload
    elif isinstance(payload, dict):
        result = payload.get("result", {}) if isinstance(payload.get("result"), dict) else {}
        pages = (
            result.get("layoutParsingResults")
            or payload.get("layoutParsingResults")
            or payload.get("pages")
            or payload.get("data")
            or payload.get("result")
            or []
        )
    else:
        pages = []
    if isinstance(pages, list):
        for page_index, page in enumerate(pages, start=1):
            yield page_index, page


def _nearest_caption_above_table(
    table_block: dict[str, Any],
    page_blocks: list[dict[str, Any]],
) -> dict[str, Any] | None:
    table_bbox = table_block.get("bbox")
    if not isinstance(table_bbox, list):
        return None
    candidates: list[tuple[float, dict[str, Any]]] = []
    for block in page_blocks:
        if block is table_block:
            continue
        if str(block.get("label") or "") != "figure_title":
            continue
        content = clean_ocr_text(str(block.get("content") or ""))
        if not TABLE_LABEL_RE.match(content):
            continue
        if _caption_table_boundary_crossed(block, table_block, page_blocks):
            continue
        bbox = block.get("bbox")
        if not isinstance(bbox, list) or len(bbox) < 4:
            continue
        try:
            distance = float(table_bbox[1]) - float(bbox[3])
        except (TypeError, ValueError):
            continue
        if distance < 0 or distance > 220:
            continue
        if _bbox_horizontal_overlap_ratio(table_bbox, bbox) < 0.40:
            continue
        candidates.append((distance, block))
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1] if candidates else None


def _extract_table_evidences_from_payload(
    *,
    payload: Any,
    chapter: str,
    source_channel: str,
    source_path: Path,
) -> list[OCREvidence]:
    evidences: list[OCREvidence] = []
    for page_index, raw_blocks in _iter_page_blocks(payload):
        page_blocks: list[dict[str, Any]] = []
        for index, block in enumerate(raw_blocks):
            content = _block_content(block)
            if not content:
                continue
            page_blocks.append(
                {
                    "label": _block_label(block),
                    "content": content,
                    "bbox": _block_bbox(block),
                    "order": _block_order(block, index),
                    "index": index,
                }
            )

        captions = _caption_candidates(raw_blocks)
        table_blocks = [
            block
            for block in page_blocks
            if block["label"] in TABLE_BODY_LABELS or HTML_TABLE_RE.search(block["content"])
        ]
        occupied_table_ids: set[str] = set()
        reading_order_pairs = _caption_table_pairs_by_reading_order(
            captions=captions,
            table_blocks=table_blocks,
            page_blocks=page_blocks,
        )
        for table_index, table_block in enumerate(table_blocks):
            table_html_match = HTML_TABLE_RE.search(table_block["content"])
            table_html = table_html_match.group(0) if table_html_match else table_block["content"]
            rows = rows_from_html_table(table_html)
            if not rows:
                continue
            caption = reading_order_pairs.get(table_index) or _select_caption_for_table(
                table_block,
                table_index,
                captions,
                page_blocks,
            )
            table_id = str((caption or {}).get("object_id") or "").strip()
            if not table_id:
                continue
            occupied_table_ids.add(table_id)
            caption_text = str((caption or {}).get("content") or "").strip()
            table_html, rows, body_text, expansion_payload = _maybe_expand_table_body_from_continuation(
                page_blocks=page_blocks,
                table_block=table_block,
                table_id=table_id,
                table_html=table_html,
                rows=rows,
            )
            following_body = _first_following_body_text(
                page_blocks=page_blocks,
                start_index=int(table_block.get("index") or 0),
            )
            preceding_body = _last_preceding_body_text(
                page_blocks=page_blocks,
                end_index=int((caption or table_block).get("index") or 0),
            )
            row_tuple = tuple(tuple(str(cell) for cell in row) for row in rows)
            evidences.append(
                OCREvidence(
                    object_type="table",
                    object_id=table_id,
                    chapter=chapter,
                    source_channel=source_channel,
                    source_path=str(source_path),
                    page=page_index,
                    order=float(table_block.get("order") or table_index),
                    caption_text=caption_text,
                    body_html=table_html,
                    body_text=body_text,
                    bbox=table_block.get("bbox"),
                    rows=row_tuple,
                    source_payload={
                        "caption_bbox": (caption or {}).get("bbox"),
                        "caption_order": (caption or {}).get("order"),
                        "table_order": table_block.get("order"),
                        "preceding_body": preceding_body,
                        "following_body": following_body,
                        **expansion_payload,
                    },
                )
            )
        evidences.extend(
            _extract_formula_table_evidences_from_page(
                page_blocks=page_blocks,
                captions=[caption for caption in captions if str(caption.get("object_id") or "").strip() not in occupied_table_ids],
                visual_rules=None,
                chapter=chapter,
                source_channel=source_channel,
                source_path=source_path,
                page_index=page_index,
                occupied_table_ids=occupied_table_ids,
            )
        )
    return evidences


def _longest_dark_span(row: Any, *, max_gap: int = 8) -> tuple[int, int, int]:
    try:
        import numpy as np
    except ImportError:
        return 0, 0, 0
    dark_idx = np.flatnonzero(row)
    if dark_idx.size == 0:
        return 0, 0, 0
    best_left = int(dark_idx[0])
    best_right = int(dark_idx[0])
    left = int(dark_idx[0])
    previous = int(dark_idx[0])
    for raw_value in dark_idx[1:]:
        value = int(raw_value)
        if value - previous <= max_gap + 1:
            previous = value
            continue
        if previous - left > best_right - best_left:
            best_left, best_right = left, previous
        left = value
        previous = value
    if previous - left > best_right - best_left:
        best_left, best_right = left, previous
    return best_right - best_left + 1, best_left, best_right


def _detect_visual_horizontal_rules(
    *,
    pdf_path: Path,
    page_index: int,
    expected_width: int | None,
    expected_height: int | None,
) -> list[dict[str, Any]]:
    try:
        import fitz
        import numpy as np
        from PIL import Image
    except ImportError:
        return []
    if not pdf_path.exists():
        return []
    try:
        with fitz.open(pdf_path) as doc:
            if page_index < 1 or page_index > doc.page_count:
                return []
            page = doc.load_page(page_index - 1)
            zoom = 1.0
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    except Exception:
        return []

    arr = np.asarray(image.convert("L"))
    height, width = arr.shape
    dark = arr < 125
    x0 = int(width * 0.08)
    x1 = int(width * 0.92)
    y0 = int(height * 0.06)
    y1 = int(height * 0.94)
    if x1 <= x0 or y1 <= y0:
        return []
    body = dark[y0:y1, x0:x1]
    body_width = body.shape[1]
    row_candidates: list[dict[str, Any]] = []
    for rel_y, row in enumerate(body):
        span, left, right = _longest_dark_span(row, max_gap=8)
        if span < body_width * 0.52:
            continue
        row_candidates.append(
            {
                "rel_y": rel_y,
                "left": left,
                "right": right,
                "span": span,
                "dark_ratio": float(row.mean()),
            }
        )

    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    previous_y: int | None = None
    for candidate in row_candidates:
        rel_y = int(candidate["rel_y"])
        if previous_y is None or rel_y - previous_y <= 2:
            current.append(candidate)
        else:
            if current:
                runs.append(current)
            current = [candidate]
        previous_y = rel_y
    if current:
        runs.append(current)

    scale_x = float(expected_width or width) / max(width, 1)
    scale_y = float(expected_height or height) / max(height, 1)
    rules: list[dict[str, Any]] = []
    for run in runs:
        top = int(min(item["rel_y"] for item in run)) + y0
        bottom = int(max(item["rel_y"] for item in run)) + y0
        left = int(min(item["left"] for item in run)) + x0
        right = int(max(item["right"] for item in run)) + x0
        rule_width = right - left + 1
        rule_height = bottom - top + 1
        coverage = rule_width / max(width, 1)
        if not (1 <= rule_height <= 12):
            continue
        if coverage < 0.45:
            continue
        if rule_width / max(rule_height, 1) < 45:
            continue
        rules.append(
            {
                "bbox": [
                    round(left * scale_x, 2),
                    round(top * scale_y, 2),
                    round(right * scale_x, 2),
                    round(bottom * scale_y, 2),
                ],
                "coverage": round(coverage, 4),
                "max_continuous_span": int(max(item["span"] for item in run)),
                "max_row_dark_ratio": round(float(max(item["dark_ratio"] for item in run)), 4),
            }
        )
    return rules


def _visual_rule_relation(rule: dict[str, Any], bbox: list[Any] | None) -> str | None:
    if not isinstance(bbox, list) or len(bbox) < 4:
        return None
    rule_bbox = rule.get("bbox")
    if not isinstance(rule_bbox, list) or len(rule_bbox) < 4:
        return None
    try:
        left, top, right, bottom = (float(item) for item in rule_bbox[:4])
        box = [float(item) for item in bbox[:4]]
    except (TypeError, ValueError):
        return None
    rule_bbox_for_overlap = [left, top, right, bottom]
    if _bbox_horizontal_overlap_ratio(rule_bbox_for_overlap, box) < 0.42:
        return None
    center_y = (top + bottom) / 2.0
    if box[1] - 24 <= center_y <= box[1] + 24:
        return "top_edge"
    if box[3] - 24 <= center_y <= box[3] + 24:
        return "bottom_edge"
    if box[1] < center_y < box[3]:
        return "inside_table"
    if center_y < box[1]:
        return "above_table"
    return "below_table"


def _visual_table_quality(rows: list[list[str]], caption_text: str, visual_rules: list[dict[str, Any]]) -> dict[str, Any]:
    column_counts = [len(row) for row in rows]
    has_body = bool(rows) and any(any(str(cell).strip() for cell in row) for row in rows)
    consistent_columns = bool(column_counts) and len(set(column_counts)) == 1
    has_caption = bool(caption_text.strip())
    has_top = any(rule.get("relation") == "top_edge" for rule in visual_rules)
    has_bottom = any(rule.get("relation") == "bottom_edge" for rule in visual_rules)
    confidence = 0.0
    confidence += 0.35 if has_body else 0.0
    confidence += 0.20 if consistent_columns else 0.08 if rows else 0.0
    confidence += 0.20 if has_caption else 0.0
    confidence += 0.15 if has_top else 0.0
    confidence += 0.10 if has_bottom else 0.0
    return {
        "has_body_rows": has_body,
        "row_count": len(rows),
        "column_counts": column_counts,
        "consistent_columns": consistent_columns,
        "has_caption": has_caption,
        "has_visual_top_edge": has_top,
        "has_visual_bottom_edge": has_bottom,
        "confidence": round(confidence, 3),
    }


def _has_physical_table_rule_support(visual_rules: list[dict[str, Any]]) -> bool:
    relations = {
        str(rule.get("relation") or "").strip()
        for rule in visual_rules
        if isinstance(rule, dict)
    }
    return bool(relations & {"top_edge", "bottom_edge", "inside_table"})


def _first_following_body_text(
    *,
    page_blocks: list[dict[str, Any]],
    start_index: int,
) -> dict[str, Any] | None:
    for block in page_blocks:
        try:
            block_index = int(block.get("index") or 0)
        except (TypeError, ValueError):
            continue
        if block_index <= start_index:
            continue
        label = str(block.get("label") or "").strip().lower()
        if label in {"header", "number", "page_number", "footer"}:
            continue
        content = clean_ocr_text(str(block.get("content") or ""))
        if not content:
            continue
        if label in {"text", "paragraph_title", "figure_title"} and not TABLE_LABEL_RE.match(content):
            return {
                "label": label,
                "content": content,
                "bbox": block.get("bbox"),
                "order": block.get("order"),
                "index": block_index,
            }
    return None


def _last_preceding_body_text(
    *,
    page_blocks: list[dict[str, Any]],
    end_index: int,
) -> dict[str, Any] | None:
    for block in reversed(page_blocks):
        try:
            block_index = int(block.get("index") or 0)
        except (TypeError, ValueError):
            continue
        if block_index >= end_index:
            continue
        label = str(block.get("label") or "").strip().lower()
        if label in {"header", "number", "page_number", "footer"}:
            continue
        content = clean_ocr_text(str(block.get("content") or ""))
        if not content:
            continue
        if label in {"text", "paragraph_title", "figure_title"} and not TABLE_LABEL_RE.match(content):
            return {
                "label": label,
                "content": content,
                "bbox": block.get("bbox"),
                "order": block.get("order"),
                "index": block_index,
            }
    return None


def _extract_visual_table_evidences_from_payload(
    *,
    payload: Any,
    chapter: str,
    source_path: Path,
    pdf_path: Path | None,
) -> list[OCREvidence]:
    if pdf_path is None or not pdf_path.exists():
        return []
    evidences: list[OCREvidence] = []
    for page_index, raw_page in _iter_payload_pages(payload):
        width, height = _page_size_from_payload_page(raw_page)
        rules = _detect_visual_horizontal_rules(
            pdf_path=pdf_path,
            page_index=page_index,
            expected_width=width,
            expected_height=height,
        )
        if not rules:
            rules = _detect_visual_horizontal_rules(
                pdf_path=pdf_path,
                page_index=page_index + 1,
                expected_width=width,
                expected_height=height,
            )
        page_blocks: list[dict[str, Any]] = []
        raw_blocks = []
        if isinstance(raw_page, list):
            raw_blocks = raw_page
        elif isinstance(raw_page, dict):
            pruned = raw_page.get("prunedResult") if isinstance(raw_page.get("prunedResult"), dict) else raw_page
            raw_blocks = (
                pruned.get("parsing_res_list")
                or raw_page.get("parsing_res_list")
                or raw_page.get("blocks")
                or raw_page.get("items")
                or []
            )
        for index, block in enumerate(raw_blocks if isinstance(raw_blocks, list) else []):
            if not isinstance(block, dict):
                continue
            content = _block_content(block)
            if not content:
                continue
            page_blocks.append(
                {
                    "label": _block_label(block),
                    "content": content,
                    "bbox": _block_bbox(block),
                    "order": _block_order(block, index),
                    "index": index,
                }
            )

        for table_index, table_block in enumerate([block for block in page_blocks if block["label"] in TABLE_BODY_LABELS]):
            table_html_match = HTML_TABLE_RE.search(table_block["content"])
            table_html = table_html_match.group(0) if table_html_match else table_block["content"]
            rows = rows_from_html_table(table_html)
            if not rows:
                continue
            caption_block = _nearest_caption_above_table(table_block, page_blocks)
            caption_text = str((caption_block or {}).get("content") or "").strip()
            table_id = _caption_label(caption_text)
            if not table_id:
                continue
            visual_rules: list[dict[str, Any]] = []
            for rule in rules:
                relation = _visual_rule_relation(rule, table_block.get("bbox"))
                if not relation:
                    continue
                visual_rules.append(
                    {
                        "relation": relation,
                        "bbox": rule.get("bbox"),
                        "coverage": rule.get("coverage"),
                        "max_continuous_span": rule.get("max_continuous_span"),
                        "max_row_dark_ratio": rule.get("max_row_dark_ratio"),
                    }
                )
            quality = _visual_table_quality(rows, caption_text, visual_rules)
            if not quality["has_body_rows"]:
                continue
            if not _has_physical_table_rule_support(visual_rules):
                continue
            following_body = _first_following_body_text(
                page_blocks=page_blocks,
                start_index=int(table_block.get("index") or 0),
            )
            preceding_body = _last_preceding_body_text(
                page_blocks=page_blocks,
                end_index=int((caption_block or table_block).get("index") or 0),
            )
            row_tuple = tuple(tuple(str(cell) for cell in row) for row in rows)
            evidences.append(
                OCREvidence(
                    object_type="table",
                    object_id=table_id,
                    chapter=chapter,
                    source_channel="paddle_visual",
                    source_path=str(source_path),
                    page=page_index,
                    order=float(table_block.get("order") or table_index),
                    caption_text=caption_text,
                    body_html=table_html,
                    body_text=table_body_text(table_html, rows),
                    bbox=table_block.get("bbox"),
                    rows=row_tuple,
                    source_payload={
                        "schema": VISUAL_TABLE_SCHEMA,
                        "pdf_path": str(pdf_path),
                        "caption_bbox": (caption_block or {}).get("bbox"),
                        "caption_order": (caption_block or {}).get("order"),
                        "table_order": table_block.get("order"),
                        "preceding_body": preceding_body,
                        "following_body": following_body,
                        "visual_rules": visual_rules,
                        "visual_quality": quality,
                    },
                )
            )
        occupied_table_ids = {
            evidence.object_id
            for evidence in evidences
            if evidence.chapter == chapter and evidence.page == page_index
        }
        evidences.extend(
            _extract_formula_table_evidences_from_page(
                page_blocks=page_blocks,
                captions=_caption_candidates(raw_blocks),
                visual_rules=rules,
                chapter=chapter,
                source_channel="paddle_visual",
                source_path=source_path,
                page_index=page_index,
                occupied_table_ids=occupied_table_ids,
            )
        )
    return evidences


def _extract_formula_evidences_from_payload(
    *,
    payload: Any,
    chapter: str,
    source_channel: str,
    source_path: Path,
) -> list[OCREvidence]:
    evidences: list[OCREvidence] = []
    for page_index, raw_blocks in _iter_page_blocks(payload):
        formula_blocks: list[dict[str, Any]] = []
        number_blocks: list[dict[str, Any]] = []
        for index, block in enumerate(raw_blocks):
            label = _block_label(block)
            if label not in FORMULA_LABELS:
                continue
            content = _block_content(block)
            if not content:
                continue
            row = {
                "label": label,
                "content": content,
                "bbox": _block_bbox(block),
                "order": _block_order(block, index),
                "index": index,
            }
            if label == "formula_number":
                number_blocks.append(row)
            else:
                formula_blocks.append(row)

        for number in number_blocks:
            match = FORMULA_NUMBER_RE.search(number["content"])
            if not match:
                continue
            formula_id = match.group("label")
            nearest = None
            nearest_distance = 999999.0
            for formula in formula_blocks:
                distance = _bbox_distance(formula.get("bbox"), number.get("bbox"))
                if distance < nearest_distance:
                    nearest = formula
                    nearest_distance = distance
            body_text = clean_ocr_text(str((nearest or {}).get("content") or ""))
            evidences.append(
                OCREvidence(
                    object_type="formula",
                    object_id=formula_id,
                    chapter=chapter,
                    source_channel=source_channel,
                    source_path=str(source_path),
                    page=page_index,
                    order=float(number.get("order") or 0.0),
                    caption_text=number["content"],
                    body_text=body_text,
                    bbox=(nearest or number).get("bbox"),
                    source_payload={"formula_number_order": number.get("order")},
                )
            )
    return evidences


def extract_evidences_from_json(
    path: str | Path,
    *,
    chapter: str,
    source_channel: str,
) -> list[OCREvidence]:
    source_path = Path(path)
    payload = _load_json_payload(source_path)
    if payload is None:
        return []
    evidences = _extract_table_evidences_from_payload(
        payload=payload,
        chapter=chapter,
        source_channel=source_channel,
        source_path=source_path,
    )
    evidences.extend(
        _extract_formula_evidences_from_payload(
            payload=payload,
            chapter=chapter,
            source_channel=source_channel,
            source_path=source_path,
        )
    )
    return evidences


def extract_table_evidences_from_markdown(
    path: str | Path,
    *,
    chapter: str,
    source_channel: str,
) -> list[OCREvidence]:
    source_path = Path(path)
    try:
        text = source_path.read_text(encoding="utf-8")
    except OSError:
        return []

    evidences: list[OCREvidence] = []
    pattern = re.compile(
        r"^\s*(?P<caption>Table\s+\d+\.\d+(?:\.\d+)?[A-Za-z]?[\s\S]{0,900}?)"
        r"(?P<table><table\b[\s\S]*?</table>)",
        re.IGNORECASE | re.MULTILINE,
    )
    for order, match in enumerate(pattern.finditer(text)):
        caption = clean_ocr_text(match.group("caption"))
        table_id = _caption_label(caption)
        if not table_id:
            continue
        if _caption_crosses_another_table_label(caption, table_id):
            continue
        table_html = match.group("table")
        rows = rows_from_html_table(table_html)
        if not rows:
            continue
        evidences.append(
            OCREvidence(
                object_type="table",
                object_id=table_id,
                chapter=chapter,
                source_channel=source_channel,
                source_path=str(source_path),
                page=None,
                order=float(order),
                caption_text=caption,
                body_html=table_html,
                body_text=table_body_text(table_html, rows),
                rows=tuple(tuple(str(cell) for cell in row) for row in rows),
            )
        )
    occupied = {evidence.object_id for evidence in evidences}
    evidences.extend(
        _extract_list_table_evidences_from_markdown(
            text,
            chapter=chapter,
            source_channel=source_channel,
            source_path=source_path,
            occupied_table_ids=occupied,
            start_order=len(evidences),
        )
    )
    return evidences


def _markdown_paragraphs(text: str) -> list[str]:
    normalized = str(text or "").replace("\r\n", "\n")
    return [clean_ocr_text(part) for part in re.split(r"\n\s*\n+", normalized) if clean_ocr_text(part)]


def _caption_from_markdown_paragraph(paragraph: str) -> tuple[str, str] | None:
    value = clean_ocr_text(re.sub(r"</?div[^>]*>", " ", paragraph, flags=re.IGNORECASE))
    match = TABLE_LABEL_RE.search(value)
    if not match:
        return None
    if not re.match(r"^Table\s+", value, flags=re.IGNORECASE):
        return None
    return match.group("label"), value


def _list_table_body_stop(paragraph: str, collected_rows: list[list[str]]) -> bool:
    value = clean_ocr_text(paragraph)
    if not value:
        return False
    if re.match(r"^(?:#{1,6}\s+|Table\s+\d+\.\d+|Figure\s+\d+\.\d+|Example\s+\d+\.\d+)", value, flags=re.IGNORECASE):
        return True
    if re.match(r"^[a-z]", value):
        return True
    if collected_rows and re.match(r"^(?:The|This|These|Those|As|When|While|If|A|An)\b", value):
        return True
    if collected_rows and len(value) > 320 and re.search(r"\.\s+[A-Z]", value):
        return True
    return False


def _extract_list_table_evidences_from_markdown(
    text: str,
    *,
    chapter: str,
    source_channel: str,
    source_path: Path,
    occupied_table_ids: set[str],
    start_order: int = 0,
) -> list[OCREvidence]:
    paragraphs = _markdown_paragraphs(text)
    evidences: list[OCREvidence] = []
    for index, paragraph in enumerate(paragraphs):
        caption = _caption_from_markdown_paragraph(paragraph)
        if caption is None:
            continue
        table_id, caption_text = caption
        if table_id in occupied_table_ids:
            continue
        rows: list[list[str]] = []
        cursor = index + 1
        while cursor < len(paragraphs):
            current = paragraphs[cursor]
            if _list_table_body_stop(current, rows):
                break
            if len(current) < 6:
                cursor += 1
                continue
            rows.append([current])
            cursor += 1
        token_count = len(normalize_for_similarity(" ".join(cell for row in rows for cell in row)).split())
        if len(rows) < 3 or token_count < 18:
            continue
        table_rows = rows
        body_html = _render_rows_as_html(table_rows)
        markdown_body = _render_rows_as_markdown(table_rows)
        raw_body = "\n\n".join([caption_text, *[row[0] for row in rows]])
        evidences.append(
            OCREvidence(
                object_type="table",
                object_id=table_id,
                chapter=chapter,
                source_channel=source_channel,
                source_path=str(source_path),
                page=None,
                order=float(start_order + len(evidences)),
                caption_text=caption_text,
                body_html=body_html,
                body_text=table_body_text(body_html, table_rows),
                rows=tuple(tuple(str(cell) for cell in row) for row in table_rows),
                source_payload={
                    "table_special_type": "list_table",
                    "list_table_recovered_from_markdown": True,
                    "raw_body": raw_body,
                    "markdown_body": markdown_body,
                },
            )
        )
        occupied_table_ids.add(table_id)
    return evidences


def _chapter_from_path(path: Path) -> str:
    stem = path.stem.lower()
    if stem.endswith("_full"):
        stem = stem[: -len("_full")]
    if stem == "toc":
        return "toc"
    return stem


def _discover_paddle_raw_paths(root: Path, chapters: set[str] | None = None) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    if not root.exists():
        return paths

    roots: list[Path] = []
    if root.is_file():
        roots = [root]
    else:
        roots.extend(root.glob("*_full/intermediate/*.json"))
        roots.extend(root.glob("*/intermediate/*.json"))
        roots.extend(root.glob("*.json"))

    for path in roots:
        if path.name not in PADDLE_RAW_FILE_NAMES and path.is_file():
            continue
        parent_name = path.parent.parent.name if path.parent.name == "intermediate" else path.stem
        chapter = _chapter_from_path(Path(parent_name))
        if chapters and chapter not in chapters:
            continue
        if chapter not in paths or path.name == "paddle_raw_response.json":
            paths[chapter] = path
    return paths


def _discover_glm_paths(root: Path, chapters: set[str] | None = None) -> dict[tuple[str, str], Path]:
    paths: dict[tuple[str, str], Path] = {}
    if not root.exists():
        return paths
    for path in sorted([*root.glob("*.json"), *root.glob("*.md")]):
        chapter = path.stem.lower()
        if chapters and chapter not in chapters:
            continue
        paths[(chapter, path.suffix.lower())] = path
    return paths


def _chapter_pdf_path(pdf_dir: Path | None, chapter: str) -> Path | None:
    chapter = str(chapter or "").strip().lower()
    if not chapter or pdf_dir is None:
        return None
    direct = pdf_dir / f"{chapter}.pdf"
    if direct.exists():
        return direct
    for path in pdf_dir.rglob(f"{chapter}.pdf"):
        return path
    return None


def build_ocr_evidence_index(
    *,
    pdf_dir: str | Path | None = None,
    paddle_output_dir: str | Path | None = None,
    glmocr_dir: str | Path | None = None,
    chapters: Iterable[str] | None = None,
) -> OCREvidenceIndex:
    chapter_set = {str(chapter).strip().lower() for chapter in chapters or [] if str(chapter).strip()} or None
    evidences: list[OCREvidence] = []

    if paddle_output_dir:
        for chapter, path in sorted(_discover_paddle_raw_paths(Path(paddle_output_dir), chapter_set).items()):
            evidences.extend(extract_evidences_from_json(path, chapter=chapter, source_channel="paddle"))
            pdf_root = Path(pdf_dir) if pdf_dir else None
            pdf_path = _chapter_pdf_path(pdf_root, chapter)
            if pdf_path is not None and pdf_path.exists():
                try:
                    payload = _load_json_payload(path)
                except Exception:
                    payload = None
                if payload is not None:
                    evidences.extend(
                        _extract_visual_table_evidences_from_payload(
                            payload=payload,
                            chapter=chapter,
                            source_path=path,
                            pdf_path=pdf_path,
                        )
                    )

    if glmocr_dir:
        glm_paths = _discover_glm_paths(Path(glmocr_dir), chapter_set)
        json_chapters: set[str] = set()
        for (chapter, suffix), path in sorted(glm_paths.items()):
            if suffix != ".json":
                continue
            evidences.extend(extract_evidences_from_json(path, chapter=chapter, source_channel="glm"))
            json_chapters.add(chapter)
        for (chapter, suffix), path in sorted(glm_paths.items()):
            if suffix == ".md":
                evidences.extend(extract_table_evidences_from_markdown(path, chapter=chapter, source_channel="glm"))

    return OCREvidenceIndex(evidences=evidences)


def table_entry_hash(entry: TableEntry) -> str:
    payload = entry.to_dict()
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def table_entry_caption_label(entry: TableEntry) -> str:
    title = str(entry.title or "")
    match = TABLE_LABEL_RE.search(title)
    return str(match.group("label") or "").strip() if match else ""


def table_entry_has_own_caption(entry: TableEntry) -> bool:
    table_id = str(entry.id or "").strip()
    if not table_id:
        return False
    title = str(entry.title or "")
    return bool(re.search(rf"\bTable\s+{re.escape(table_id)}\b", title, flags=re.IGNORECASE))


def score_table_entry_against_evidence(entry: TableEntry, evidence: OCREvidence) -> dict[str, Any]:
    entry_id = str(entry.id or "").strip()
    id_score = 1.0 if entry_id and entry_id == evidence.object_id else 0.0
    title_text = str(entry.title or "")
    structured_body = table_body_text(entry)
    caption_score = token_overlap_score(title_text, evidence.caption_text)
    body_token_score = token_overlap_score(structured_body, evidence.body_text)
    body_sequence_score = sequence_score(structured_body, evidence.body_text)
    body_score = round(0.62 * body_token_score + 0.38 * body_sequence_score, 4)
    overall = round(0.25 * id_score + 0.30 * caption_score + 0.45 * body_score, 4)
    return {
        "overall": overall,
        "id": id_score,
        "caption": caption_score,
        "body": body_score,
        "body_token": body_token_score,
        "body_sequence": body_sequence_score,
        "evidence_hash": evidence.stable_hash(),
        "source_channel": evidence.source_channel,
        "source_path": evidence.source_path,
        "page": evidence.page,
    }


def score_table_evidence_pair(left: OCREvidence, right: OCREvidence) -> dict[str, Any]:
    id_score = 1.0 if left.object_id and left.object_id == right.object_id else 0.0
    caption_score = token_overlap_score(left.caption_text, right.caption_text)
    body_token_score = token_overlap_score(left.body_text, right.body_text)
    body_sequence_score = sequence_score(left.body_text, right.body_text)
    body_score = round(0.62 * body_token_score + 0.38 * body_sequence_score, 4)
    overall = round(0.25 * id_score + 0.25 * caption_score + 0.50 * body_score, 4)
    return {
        "overall": overall,
        "id": id_score,
        "caption": caption_score,
        "body": body_score,
        "body_token": body_token_score,
        "body_sequence": body_sequence_score,
        "left_hash": left.stable_hash(),
        "right_hash": right.stable_hash(),
    }


def table_entry_from_evidence(evidence: OCREvidence) -> TableEntry:
    raw_body = None
    markdown_body = None
    table_type = "numbered"
    if isinstance(evidence.source_payload, dict):
        raw_body = evidence.source_payload.get("raw_body")
        markdown_body = evidence.source_payload.get("markdown_body")
        if str(evidence.source_payload.get("table_special_type") or "") == "formula_table":
            table_type = "formula_table"
        elif str(evidence.source_payload.get("table_special_type") or "") == "list_table":
            table_type = "list_table"
    source = {
        "chapter": evidence.chapter,
        "page": evidence.page,
        "source_channel": evidence.source_channel,
        "source_path": evidence.source_path,
        "evidence_hash": evidence.stable_hash(),
        "table_body_expanded_from_following_blocks": bool(
            isinstance(evidence.source_payload, dict)
            and evidence.source_payload.get("table_body_expanded_from_following_blocks")
        ),
    }
    if isinstance(evidence.source_payload, dict):
        for key in ("caption_bbox", "table_order", "caption_order", "preceding_body", "following_body", "visual_bottom_rule_y"):
            if evidence.source_payload.get(key) is not None:
                source[key] = evidence.source_payload.get(key)
    if evidence.bbox is not None:
        source["bbox"] = evidence.bbox
    if table_type == "formula_table":
        source["table_special_type"] = "formula_table"
    elif table_type == "list_table":
        source["table_special_type"] = "list_table"
    return TableEntry(
        id=evidence.object_id,
        label_format=f"Table {evidence.object_id}",
        title=evidence.caption_text or f"Table {evidence.object_id}",
        table_type=table_type,
        html=evidence.body_html,
        rows=[list(row) for row in evidence.rows],
        source=source,
        raw_body=str(raw_body) if raw_body is not None else None,
        markdown_body=str(markdown_body) if markdown_body is not None else None,
    )
