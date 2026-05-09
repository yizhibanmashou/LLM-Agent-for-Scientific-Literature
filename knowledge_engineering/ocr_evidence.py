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

from knowledge_engineering.runtime import TableEntry


TABLE_LABEL_RE = re.compile(r"\bTable\s+(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\b", re.IGNORECASE)
FORMULA_NUMBER_RE = re.compile(r"\(\s*(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\s*\)")
HTML_TABLE_RE = re.compile(r"<table\b[\s\S]*?</table>", re.IGNORECASE)
HTML_TABLE_ROW_RE = re.compile(r"<tr[^>]*>(?P<body>.*?)</tr>", re.IGNORECASE | re.DOTALL)
HTML_TABLE_CELL_RE = re.compile(r"<t[dh][^>]*>(?P<body>.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)
HTML_TAG_RE = re.compile(r"<[^>]+>")
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


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def clean_ocr_text(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"</?div[^>]*>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"^#+\s*", "", value.strip())
    return collapse_ws(value)


def strip_html(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = HTML_TAG_RE.sub(" ", value)
    return collapse_ws(value)


def rows_from_html_table(table_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_match in HTML_TABLE_ROW_RE.finditer(str(table_html or "")):
        row_cells: list[str] = []
        for cell_match in HTML_TABLE_CELL_RE.finditer(row_match.group("body")):
            cell_text = strip_html(cell_match.group("body"))
            row_cells.append(cell_text)
        if row_cells and any(cell for cell in row_cells):
            rows.append(row_cells)
    return rows


def table_body_text_from_rows(rows: Iterable[Iterable[Any]]) -> str:
    cells: list[str] = []
    for row in rows:
        if not isinstance(row, (list, tuple)):
            continue
        for cell in row:
            value = collapse_ws(str(cell or ""))
            if value:
                cells.append(value)
    return collapse_ws(" ".join(cells))


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
    return len(rows) <= 2 and cell_count <= 6 and len(normalize_for_similarity(body_text).split()) <= 24


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


def _select_caption_for_table(
    table_block: dict[str, Any],
    table_index: int,
    captions: list[dict[str, Any]],
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

    return sorted(captions, key=caption_sort_key)[0]


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
        for table_index, table_block in enumerate(table_blocks):
            table_html_match = HTML_TABLE_RE.search(table_block["content"])
            table_html = table_html_match.group(0) if table_html_match else table_block["content"]
            rows = rows_from_html_table(table_html)
            if not rows:
                continue
            caption = _select_caption_for_table(table_block, table_index, captions)
            table_id = str((caption or {}).get("object_id") or "").strip()
            if not table_id:
                continue
            caption_text = str((caption or {}).get("content") or "").strip()
            table_html, rows, body_text, expansion_payload = _maybe_expand_table_body_from_continuation(
                page_blocks=page_blocks,
                table_block=table_block,
                table_id=table_id,
                table_html=table_html,
                rows=rows,
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
                        "caption_order": (caption or {}).get("order"),
                        "table_order": table_block.get("order"),
                        **expansion_payload,
                    },
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
        r"(?P<caption>Table\s+\d+\.\d+(?:\.\d+)?[A-Za-z]?[\s\S]{0,900}?)"
        r"(?P<table><table\b[\s\S]*?</table>)",
        re.IGNORECASE,
    )
    for order, match in enumerate(pattern.finditer(text)):
        caption = clean_ocr_text(match.group("caption"))
        table_id = _caption_label(caption)
        if not table_id:
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
        if chapter not in paths or path.name == "paddle_raw_api_response.json":
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


def build_ocr_evidence_index(
    *,
    paddle_output_dir: str | Path | None = None,
    glmocr_dir: str | Path | None = None,
    chapters: Iterable[str] | None = None,
) -> OCREvidenceIndex:
    chapter_set = {str(chapter).strip().lower() for chapter in chapters or [] if str(chapter).strip()} or None
    evidences: list[OCREvidence] = []

    if paddle_output_dir:
        for chapter, path in sorted(_discover_paddle_raw_paths(Path(paddle_output_dir), chapter_set).items()):
            evidences.extend(extract_evidences_from_json(path, chapter=chapter, source_channel="paddle"))

    if glmocr_dir:
        glm_paths = _discover_glm_paths(Path(glmocr_dir), chapter_set)
        json_chapters: set[str] = set()
        for (chapter, suffix), path in sorted(glm_paths.items()):
            if suffix != ".json":
                continue
            evidences.extend(extract_evidences_from_json(path, chapter=chapter, source_channel="glm"))
            json_chapters.add(chapter)
        for (chapter, suffix), path in sorted(glm_paths.items()):
            if suffix == ".md" and chapter not in json_chapters:
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
    if isinstance(evidence.source_payload, dict):
        raw_body = evidence.source_payload.get("raw_body")
        markdown_body = evidence.source_payload.get("markdown_body")
    return TableEntry(
        id=evidence.object_id,
        label_format=f"Table {evidence.object_id}",
        title=evidence.caption_text or f"Table {evidence.object_id}",
        table_type="numbered",
        html=evidence.body_html,
        rows=[list(row) for row in evidence.rows],
        source={
            "chapter": evidence.chapter,
            "page": evidence.page,
            "source_channel": evidence.source_channel,
            "source_path": evidence.source_path,
            "evidence_hash": evidence.stable_hash(),
            "table_body_expanded_from_following_blocks": bool(
                isinstance(evidence.source_payload, dict)
                and evidence.source_payload.get("table_body_expanded_from_following_blocks")
            ),
        },
        raw_body=str(raw_body) if raw_body is not None else None,
        markdown_body=str(markdown_body) if markdown_body is not None else None,
    )
