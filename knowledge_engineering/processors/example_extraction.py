"""Example extraction and raw-layout recovery helpers.

This module owns the production example-detection rules used by the formal
example pipeline. Trial scripts may call these helpers, but production code
should not depend on trial scripts for extraction behavior.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
import hashlib
import html
import re

from knowledge_engineering.core.common import read_json
from knowledge_engineering.processors.ocr_evidence import (
    _detect_visual_horizontal_rules,
    _page_size_from_payload_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_HEAD_RE = re.compile(
    r"Example\s+(?P<example_id>(?:A\d+|\d+)\.\d+[a-z]?)(?P<trailing>\.)?",
    re.IGNORECASE,
)
STRUCTURED_REF_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE|FIGURE):([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
FORMULA_MARKER_RE = re.compile(r"\[\[(?:SEE_)?FORMULA\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
TABLE_MARKER_RE = re.compile(r"\[\[(?:SEE_)?TABLE\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
FIGURE_MARKER_RE = re.compile(r"\[\[(?:SEE_)?FIGURE\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
STANDALONE_NUMBERED_TABLE_RE = re.compile(
    r"^\s*\[\[TABLE\s*:\s*(?P<label>(?:A\d+|\d+)\.\d+[A-Za-z]?)\s*\]\]\s*$",
    re.IGNORECASE,
)
FIGURE_REF_RE = re.compile(r"\b(?:Figure|Fig\.)\s+([A-Z]?\d+\.\d+[a-z]?)\b", re.IGNORECASE)
LW_EXTERNAL_RE = re.compile(
    r"\b(?:LW|Lynch and Walsh)\s+(Chapter|Equation|Table|Figure)\s+([A-Z]?\d+(?:\.\d+)?[a-z]?)\b",
    re.IGNORECASE,
)
LW_PLACEHOLDER_RE = re.compile(r"\b(?:LW|Lynch and Walsh)\s+\[\[(?:SEE_)?TABLE:([^\]\n\r]+?)\]\]", re.IGNORECASE)
NATURAL_FORMULA_RE = re.compile(
    r"\bEquations?\s+(?P<label>(?:A\d+|\d+)\.\d+[a-z]?)\b",
    re.IGNORECASE,
)
NATURAL_FORMULA_RANGE_RE = re.compile(
    r"\bEquations?\s+(?P<start>(?:A\d+|\d+)\.\d+[a-z]?)\s*[–-]\s*(?P<end>(?:A\d+|\d+)\.\d+[a-z]?)",
    re.IGNORECASE,
)
NATURAL_TABLE_RE = re.compile(
    r"(?<!LW\s)(?<!Lynch and Walsh\s)\bTables?\s+([A-Z]?\d+\.\d+[a-z]?)\b",
    re.IGNORECASE,
)
EXAMPLE_PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?EXAMPLE:([^\]\n\r]+?)\]\]", re.IGNORECASE)
FIGURE_CAPTION_START_RE = re.compile(r"^\s*(?:Figure|Fig\.)\s+(?:A\d+|\d+)\.\d+[a-z]?\b", re.IGNORECASE)
PADDLE_RAW_FILE_NAMES = (
    "paddle_raw_api_response.json",
    "paddle_raw_response.json",
)
PADDLE_EXAMPLE_LABELS = {"text", "figure_title", "footer", "paragraph_title", "reference_content", "footnote"}
PADDLE_EXAMPLE_BODY_LABELS = {
    "text",
    "figure_title",
    "footer",
    "paragraph_title",
    "reference_content",
    "footnote",
    "table",
    "display_formula",
    "formula_number",
}
PADDLE_PAGE_NOISE_LABELS = {"header", "number", "page_number"}
PADDLE_PUBLICATION_FOOTER_RE = re.compile(
    r"(?:Evolution and Selection of Quantitative Traits|Oxford University Press|Published 20\d{2}|"
    r"Bruce Walsh|Michael Lynch|DOI\s+10\.)",
    re.IGNORECASE,
)
OCR_GARBAGE_RE = re.compile(r"\s+(?:are\s+not)?[\u4e00-\u9fff\uac00-\ud7af]+(?=\s|$)")
SAME_EXAMPLE_BACK_REFERENCE_RE = re.compile(
    r"^\s*(?:(?:As|Thus|Hence|Therefore|This|These)\s+)?"
    r"Example\s+(?P<example_id>(?:A\d+|\d+)\.\d+[a-z]?)\s+"
    r"(?:illustrates|highlights|shows|showed|demonstrates|suggests|indicates|makes|reveals)\b",
    re.IGNORECASE,
)
AUTHOR_YEAR_PARAGRAPH_RE = re.compile(
    r"^\s*[A-Z][A-Za-z'鈥?-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'鈥?-]+|\s+et\s+al\.)?\s*"
    r"\((?:18|19|20)\d{2}[a-z]?(?:,\s*(?:18|19|20)\d{2}[a-z]?)*\)\s+"
    r"(?:examined|showed|found|used|presented|developed|considered|reported|observed|extended|suggested)\b",
    re.IGNORECASE,
)
BODY_PARAGRAPH_OPENING_RE = re.compile(
    r"^\s*(?:"
    r"A number of|A partial|A final|A cautionary|A common|A simple|"
    r"An additional|An increasingly|"
    r"In addition|In general|In the|In this|In these|"
    r"For example|For starters|However|Moreover|Nevertheless|Finally|Conversely|Although|As a result|Thus|"
    r"This|These|The|Why|Recall|Consider|Suppose|When|While|If"
    r")\b",
    re.IGNORECASE,
)


@dataclass
class BlockSpan:
    block_index: int
    start: int
    end: int
    text: str


@dataclass
class ExampleCandidate:
    example_id: str
    chapter: str
    label: str
    title: str
    source_file: str
    start_block_index: int
    end_block_index: int
    block_ids: list[str]
    content_markdown: str
    content_plain: str
    formula_refs: list[str]
    table_refs: list[str]
    figure_refs: list[str]
    external_refs: list[str]
    evidence: dict[str, Any]
    metadata: dict[str, Any]
    _order_key: tuple[Any, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "example_id": self.example_id,
            "chapter": self.chapter,
            "label": self.label,
            "title": self.title,
            "source_file": self.source_file,
            "start_block_index": self.start_block_index,
            "end_block_index": self.end_block_index,
            "block_ids": self.block_ids,
            "content_markdown": self.content_markdown,
            "content_plain": self.content_plain,
            "formula_refs": self.formula_refs,
            "table_refs": self.table_refs,
            "figure_refs": self.figure_refs,
            "external_refs": self.external_refs,
            "evidence": self.evidence,
            "metadata": self.metadata,
        }
        return payload


@dataclass
class StructuredContext:
    units_by_chapter: dict[str, list[tuple[Path, dict[str, Any]]]]
    placeholder_locations: dict[tuple[str, str], tuple[str, int]]
    placeholder_order: dict[str, list[tuple[str, str, int]]]
    block_locations: dict[str, list[tuple[Path, int, str]]]


@dataclass
class RawRecord:
    chapter: str
    page_index: int
    row_index: int
    label: str
    content: str
    bbox: list[Any] | None
    order: Any


@dataclass
class RawExampleVisualStop:
    example_id: str
    included_tail: str
    stop_text: str
    page_index: int
    row_index: int
    vertical_gap: float
    source: str = "paddle_raw_layout_gap"
    rule_bbox: list[Any] | None = None
    rule_coverage: float | None = None


def natural_key(value: str) -> list[Any]:
    parts = re.split(r"(\d+)", value)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def chapter_sort_key(chapter: str) -> tuple[Any, ...]:
    text = chapter.lower()
    match = re.fullmatch(r"chapter(\d+)", text)
    if match:
        return (0, int(match.group(1)), text)
    match = re.fullmatch(r"appendix(\d+)", text)
    if match:
        return (1, int(match.group(1)), text)
    return (9, *natural_key(text))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_ref_id(raw: str) -> str:
    return str(raw or "").strip().strip(" \t\r\n.,;:)")


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        cleaned = clean_ref_id(value)
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return seen


def normalize_match_text(text: str) -> str:
    value = strip_structured_refs(strip_html(str(text or "")))
    value = re.sub(r"\\([A-Za-z]+)", r" \1 ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return collapse_ws(value).lower()


def strip_html(text: str) -> str:
    value = re.sub(r"<[^>]+>", " ", str(text or ""))
    return html.unescape(value)


def clean_ocr_residue(text: str) -> str:
    value = OCR_GARBAGE_RE.sub(" ", str(text or ""))
    return collapse_ws(value)


def expand_formula_range(start: str, end: str) -> list[str]:
    start = clean_ref_id(start)
    end = clean_ref_id(end)
    start_match = re.fullmatch(r"((?:A\d+|\d+)\.\d+)([a-z]?)", start, re.IGNORECASE)
    end_match = re.fullmatch(r"((?:A\d+|\d+)\.\d+)([a-z]?)", end, re.IGNORECASE)
    if not start_match or not end_match:
        return [start, end]
    if start_match.group(1).lower() != end_match.group(1).lower():
        return [start, end]
    start_suffix = start_match.group(2).lower()
    end_suffix = end_match.group(2).lower()
    if not start_suffix and not end_suffix:
        return [start, end] if start != end else [start]
    if not start_suffix or not end_suffix:
        return [start, end]
    if len(start_suffix) != 1 or len(end_suffix) != 1:
        return [start, end]
    if ord(start_suffix) > ord(end_suffix):
        start_suffix, end_suffix = end_suffix, start_suffix
    base = start_match.group(1)
    return [f"{base}{chr(code)}" for code in range(ord(start_suffix), ord(end_suffix) + 1)]


def strip_structured_refs(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        kind = match.group(0)
        label = clean_ref_id(match.group(1))
        if "FORMULA" in kind.upper():
            return f"Equation {label}"
        if "FIGURE" in kind.upper():
            return f"Figure {label}"
        return f"Table {label}"

    return STRUCTURED_REF_RE.sub(repl, text or "")


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def normalize_heading_prefix(text: str) -> str:
    value = str(text or "")
    value = re.sub(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?\s*(?:\[\s*[htbp]\s*\]\s*)?", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s*(?:\*\*)\s*$", "", value)
    return value


def is_heading_context(prefix: str) -> bool:
    if not prefix:
        return True
    paragraph_prefix = re.split(r"\n\s*\n", prefix)[-1]
    stripped = paragraph_prefix.strip()
    if not stripped:
        return True
    if re.fullmatch(r"(?:#{1,6}\s*)?(?:\*\*)?(?:\[\s*[htbp]\s*\])?", stripped, flags=re.IGNORECASE):
        return True
    return False


def is_example_heading_match(text: str, match: re.Match[str]) -> bool:
    if not is_heading_context(str(text or "")[: match.start()]):
        return False
    if match.groupdict().get("trailing") == ".":
        return True
    suffix = str(text or "")[match.end() :].lstrip()
    return suffix.startswith(":")


def looks_truncated(text: str) -> bool:
    value = collapse_ws(text)
    if not value:
        return True
    if value.endswith(("...", "…", ",", ";", ":")):
        return True
    if value.endswith((" and", " or", " to", " of", " the", " for", " with", " as", " in", " on", " at", " by", " from")):
        return True
    if value.count("(") > value.count(")") or value.count("[") > value.count("]") or value.count("{") > value.count("}"):
        return True
    if value.count("$$") % 2 != 0:
        return True
    if value.count("$") % 2 != 0:
        return True
    if re.search(r"\[\[(?:SEE_)?(?:FORMULA|TABLE):[^]]*$", value, flags=re.IGNORECASE):
        return True
    return False


def extract_formula_refs(text: str) -> list[str]:
    ordered: list[tuple[int, str]] = []
    for match in FORMULA_MARKER_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group(1))))
    for match in NATURAL_FORMULA_RANGE_RE.finditer(text or ""):
        for label in expand_formula_range(match.group("start"), match.group("end")):
            ordered.append((match.start(), clean_ref_id(label)))
    for match in NATURAL_FORMULA_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group("label"))))
    ordered.sort(key=lambda item: item[0])
    return dedupe_preserve_order([label for _, label in ordered])


def extract_table_refs(text: str) -> list[str]:
    ordered: list[tuple[int, str]] = []
    for match in TABLE_MARKER_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group(1))))
    for match in NATURAL_TABLE_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group(1))))
    ordered.sort(key=lambda item: item[0])
    return dedupe_preserve_order([label for _, label in ordered])


def extract_figure_refs(text: str) -> list[str]:
    ordered: list[tuple[int, str]] = []
    for match in FIGURE_MARKER_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group(1))))
    for match in FIGURE_REF_RE.finditer(text or ""):
        ordered.append((match.start(), clean_ref_id(match.group(1))))
    ordered.sort(key=lambda item: item[0])
    return dedupe_preserve_order([label for _, label in ordered])


def extract_external_refs(text: str) -> list[str]:
    ordered: list[tuple[int, str]] = []
    for match in LW_EXTERNAL_RE.finditer(text or ""):
        kind, label = match.groups()
        ordered.append((match.start(), f"LW {kind.title()} {clean_ref_id(label)}"))
    for match in LW_PLACEHOLDER_RE.finditer(text or ""):
        ordered.append((match.start(), f"LW Table {clean_ref_id(match.group(1))}"))
    ordered.sort(key=lambda item: item[0])
    return dedupe_preserve_order([label for _, label in ordered])


def chapter_from_path(path: Path, data: dict[str, Any]) -> str:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    chapter = str(metadata.get("chapter") or path.stem.split("_", 1)[0]).strip().lower()
    return chapter


def load_unit_files(structured_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(structured_dir.glob("*.json"), key=lambda item: natural_key(item.name)):
        if path.name in {"formula_library.json", "table_library.json", "example_library.json"}:
            continue
        if path.name.endswith("_example_library.json") or path.name in {"all_example_library.json"}:
            continue
        try:
            data = read_json(path)
        except Exception:
            continue
        if isinstance(data, dict) and isinstance(data.get("blocks"), list):
            files.append(path)
    return files


def build_structured_context(structured_dir: Path) -> StructuredContext:
    units_by_chapter: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    placeholder_locations: dict[tuple[str, str], tuple[str, int]] = {}
    placeholder_order: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    block_locations: dict[str, list[tuple[Path, int, str]]] = defaultdict(list)

    for path in load_unit_files(structured_dir):
        try:
            data = read_json(path)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        chapter = chapter_from_path(path, data)
        units_by_chapter.setdefault(chapter, []).append((path, data))
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            block_locations[chapter].append((path, block_index, content))
            for match in EXAMPLE_PLACEHOLDER_RE.finditer(content):
                ref = clean_ref_id(match.group(1))
                if not ref:
                    continue
                placeholder_locations.setdefault((chapter, ref), (path.name, block_index))
                placeholder_order[chapter].append((ref, path.name, block_index))

    for chapter in units_by_chapter:
        units_by_chapter[chapter].sort(key=lambda item: natural_key(item[0].name))
    for chapter in placeholder_order:
        placeholder_order[chapter].sort(key=lambda item: (natural_key(item[1]), item[2], natural_key(item[0])))
    return StructuredContext(
        units_by_chapter=units_by_chapter,
        placeholder_locations=placeholder_locations,
        placeholder_order=placeholder_order,
        block_locations=block_locations,
    )


def build_spans(blocks: list[dict[str, Any]]) -> tuple[list[BlockSpan], str]:
    spans: list[BlockSpan] = []
    parts: list[str] = []
    offset = 0
    for index, block in enumerate(blocks):
        text = str(block.get("content") or "")
        start = offset
        end = start + len(text)
        spans.append(BlockSpan(block_index=index, start=start, end=end, text=text))
        parts.append(text)
        offset = end + 2
        if index != len(blocks) - 1:
            parts.append("\n\n")
    return spans, "".join(parts)


def is_standalone_numbered_table_placeholder(text: str) -> bool:
    return STANDALONE_NUMBERED_TABLE_RE.fullmatch(str(text or "")) is not None


def first_standalone_numbered_table_boundary(
    spans: list[BlockSpan],
    *,
    start: int,
    end: int,
) -> BlockSpan | None:
    for span in spans:
        if span.start <= start:
            continue
        if span.start >= end:
            break
        if is_standalone_numbered_table_placeholder(span.text):
            return span
    return None


def find_example_anchors(spans: list[BlockSpan], block_text: str) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    for span in spans:
        for match in EXAMPLE_HEAD_RE.finditer(span.text):
            local_start = match.start()
            prefix = span.text[:local_start]
            if not is_example_heading_match(span.text, match):
                continue
            suffix = span.text[match.end() :].lstrip()
            if suffix and suffix[0] in ",;.)]}":
                continue
            example_id = match.group("example_id")
            if match.start() > 0:
                prefix_tail = span.text[max(0, local_start - 40):local_start]
                if re.search(r"\b(?:see|example|as in|in example)\s*$", prefix_tail, flags=re.IGNORECASE):
                    continue
            anchors.append(
                {
                    "example_id": example_id,
                    "start": span.start + match.start(),
                    "match_end": span.start + match.end(),
                    "block_index": span.block_index,
                }
            )
    anchors.sort(key=lambda item: item["start"])
    return anchors


def span_blocks(spans: list[BlockSpan], start: int, end: int) -> tuple[int, int]:
    covered = [span.block_index for span in spans if span.end > start and span.start < end]
    if not covered:
        return 0, 0
    return min(covered), max(covered)


def span_blocks_until_next_anchor(spans: list[BlockSpan], start: int, end: int) -> tuple[int, int]:
    """Return source blocks covered by an example's full pre-fold span.

    ``end`` is normally the next example anchor or end of unit.  This is
    intentionally wider than a visual-stop-clipped replacement interval: the
    visual stop controls what content is folded into the example, while the
    source span records the original structured block range associated with the
    example before folding.
    """

    return span_blocks(spans, start, end)


def sliced_text(block_text: str, start: int, end: int) -> str:
    return block_text[start:end]


def find_structured_visual_stop_end(
    raw_content: str,
    visual_stop: RawExampleVisualStop | None,
) -> int | None:
    if visual_stop is None:
        return None
    content_norm = normalize_match_text(raw_content)
    tail_norm = normalize_match_text(visual_stop.included_tail)
    stop_norm = normalize_match_text(visual_stop.stop_text)
    if not content_norm or not tail_norm or not stop_norm:
        return None
    tail_pos_norm = content_norm.find(tail_norm)
    stop_pos_norm = content_norm.find(stop_norm)
    if tail_pos_norm < 0 or stop_pos_norm < 0 or stop_pos_norm <= tail_pos_norm:
        return None

    stop_tokens = _tokenize_match_text(visual_stop.stop_text)
    if not stop_tokens:
        return None
    content_tokens = _token_spans_for_match(raw_content)
    stop_start_token = _find_subsequence([token for token, _, _ in content_tokens], stop_tokens)
    if stop_start_token is None:
        return None
    stop_start_char = content_tokens[stop_start_token][1]
    if stop_start_char <= 0:
        return None
    return stop_start_char


def _tokenize_match_text(text: str) -> list[str]:
    return [match.group(0).lower() for match in re.finditer(r"[0-9A-Za-z]+", str(text or ""))]


def _token_spans_for_match(text: str) -> list[tuple[str, int, int]]:
    tokens: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[0-9A-Za-z]+", str(text or "")):
        tokens.append((match.group(0).lower(), match.start(), match.end()))
    return tokens


def _find_subsequence(haystack: list[str], needle: list[str]) -> int | None:
    if not needle or len(needle) > len(haystack):
        return None
    last_start = len(haystack) - len(needle)
    for index in range(last_start + 1):
        if haystack[index : index + len(needle)] == needle:
            return index
    return None


def extract_examples_for_file(
    path: Path,
    data: dict[str, Any],
    visual_stops: dict[str, list[RawExampleVisualStop]] | None = None,
) -> list[ExampleCandidate]:
    blocks = [block for block in data.get("blocks", []) if isinstance(block, dict)]
    spans, block_text = build_spans(blocks)
    anchors = find_example_anchors(spans, block_text)
    if not anchors:
        return []

    chapter = chapter_from_path(path, data)
    examples: list[ExampleCandidate] = []
    stop_indexes: dict[str, int] = defaultdict(int)
    for index, anchor in enumerate(anchors):
        start = anchor["start"]
        semantic_end = anchors[index + 1]["start"] if index + 1 < len(anchors) else len(block_text)
        table_boundary = first_standalone_numbered_table_boundary(
            spans,
            start=start,
            end=semantic_end,
        )
        end = table_boundary.start if table_boundary is not None else semantic_end
        source_start_block, source_end_block = span_blocks_until_next_anchor(spans, start, end)
        raw_content = sliced_text(block_text, start, end).strip()
        visual_stop = None
        stop_candidates = (visual_stops or {}).get(anchor["example_id"], [])
        if stop_candidates:
            stop_index = stop_indexes[anchor["example_id"]]
            if stop_index < len(stop_candidates):
                visual_stop = stop_candidates[stop_index]
                stop_indexes[anchor["example_id"]] = stop_index + 1
        visual_stop_end = find_structured_visual_stop_end(raw_content, visual_stop)
        if visual_stop_end is not None:
            end = start + visual_stop_end
            raw_content = sliced_text(block_text, start, end).strip()
        content_markdown = normalize_heading_prefix(raw_content)
        content_markdown = re.sub(
            r"^\s*(Example\s+(?:A\d+|\d+)\.\d+[a-z]?\.)\s*\*\*",
            r"\1",
            content_markdown,
            count=1,
            flags=re.IGNORECASE,
        )
        content_markdown = collapse_ws(content_markdown) if "\n" not in raw_content else content_markdown.strip()
        content_plain = collapse_ws(strip_structured_refs(content_markdown))
        after_heading = collapse_ws(re.sub(r"^\s*Example\s+(?:A\d+|\d+)\.\d+[a-z]?\.\s*", "", content_markdown, count=1, flags=re.IGNORECASE))
        title = after_heading[:160].strip()
        formula_refs = extract_formula_refs(content_markdown)
        table_refs = extract_table_refs(content_markdown)
        figure_refs = extract_figure_refs(content_markdown)
        external_refs = extract_external_refs(content_markdown)
        start_block, end_block = span_blocks(spans, start, end)
        block_ids: list[str] = []
        evidence = {
            "source": "structured_blocks",
            "detection_method": "example_heading_regex",
            "confidence": 0.97 if start == spans[start_block].start else 0.94,
        }
        if table_boundary is not None:
            evidence["standalone_numbered_table_boundary_stop"] = True
            evidence["standalone_numbered_table_boundary_block_index"] = table_boundary.block_index
        if visual_stop_end is not None and visual_stop is not None:
            evidence = {
                **evidence,
                "visual_stop_clipped": True,
                "visual_stop_source": visual_stop.source,
                "visual_stop_page": visual_stop.page_index + 1,
                "visual_stop_row_index": visual_stop.row_index,
                "visual_stop_vertical_gap": visual_stop.vertical_gap,
            }
            if visual_stop.rule_bbox:
                evidence["visual_stop_rule_bbox"] = visual_stop.rule_bbox
            if visual_stop.rule_coverage is not None:
                evidence["visual_stop_rule_coverage"] = visual_stop.rule_coverage
        needs_review = looks_truncated(content_markdown)
        if end == len(block_text) and needs_review is False:
            needs_review = looks_truncated(content_markdown)
        metadata = {
            "has_formula": bool(formula_refs),
            "has_table": bool(table_refs),
            "has_figure": bool(figure_refs),
            "word_count": len(content_plain.split()) if content_plain else 0,
            "needs_review": needs_review,
            "source_block_span": [source_start_block, source_end_block],
        }
        if table_boundary is not None:
            metadata["standalone_numbered_table_boundary_stop"] = True
            metadata["standalone_numbered_table_boundary_block_index"] = table_boundary.block_index
        if visual_stop_end is not None:
            metadata["replacement_end_char"] = end - spans[end_block].start
        examples.append(
            ExampleCandidate(
                example_id=anchor["example_id"],
                chapter=chapter,
                label=f"Example {anchor['example_id']}",
                title=title,
                source_file=path.name,
                start_block_index=start_block,
                end_block_index=end_block,
                block_ids=block_ids,
                content_markdown=content_markdown,
                content_plain=content_plain,
                formula_refs=formula_refs,
                table_refs=table_refs,
                figure_refs=figure_refs,
                external_refs=external_refs,
                evidence=evidence,
                metadata=metadata,
                _order_key=(chapter_sort_key(chapter), natural_key(path.name), start_block, start),
            )
        )
    return examples


def load_paddle_raw_pages(project_root: Path, chapter: str) -> list[dict[str, Any]]:
    raw_dirs = [
        project_root / "data" / "paddle_output" / f"{chapter}_full" / "intermediate",
        project_root / "tmp" / "paddle_output" / f"{chapter}_full" / "intermediate",
    ]
    for raw_dir in raw_dirs:
        for file_name in PADDLE_RAW_FILE_NAMES:
            raw_path = raw_dir / file_name
            if not raw_path.exists():
                continue
            try:
                payload = read_json(raw_path)
            except Exception:
                continue
            if isinstance(payload, list):
                return [page for page in payload if isinstance(page, dict)]
            result = payload.get("result", {}) if isinstance(payload, dict) else {}
            pages = result.get("layoutParsingResults", []) if isinstance(result, dict) else []
            if isinstance(pages, list) and pages:
                return [page for page in pages if isinstance(page, dict)]
    return []


def paddle_page_rows(page_payload: dict[str, Any]) -> list[dict[str, Any]]:
    pruned = page_payload.get("prunedResult", {}) if isinstance(page_payload.get("prunedResult"), dict) else page_payload
    rows = pruned.get("parsing_res_list", [])
    return rows if isinstance(rows, list) else []


def paddle_block_top(row: dict[str, Any]) -> float:
    bbox = row.get("block_bbox")
    if isinstance(bbox, list) and len(bbox) >= 2:
        try:
            return float(bbox[1])
        except (TypeError, ValueError):
            return 999999.0
    return 999999.0


def ordered_paddle_records(project_root: Path, chapter: str) -> list[RawRecord]:
    records: list[RawRecord] = []
    for page_index, page in enumerate(load_paddle_raw_pages(project_root, chapter)):
        rows = [
            row
            for row in paddle_page_rows(page)
            if isinstance(row, dict) and str(row.get("block_content") or "").strip()
        ]
        rows.sort(
            key=lambda row: (
                paddle_block_top(row),
                row.get("block_order") is None,
                row.get("block_order") if row.get("block_order") is not None else 999999,
            )
        )
        for row_index, row in enumerate(rows):
            records.append(
                RawRecord(
                    chapter=chapter,
                    page_index=page_index,
                    row_index=row_index,
                    label=str(row.get("block_label") or "").strip().lower(),
                    content=clean_ocr_residue(str(row.get("block_content") or "")),
                    bbox=row.get("block_bbox") if isinstance(row.get("block_bbox"), list) else None,
                    order=row.get("block_order"),
                )
            )
    return records


def chapter_pdf_path(project_root: Path, chapter: str) -> Path | None:
    data_dir = project_root / "data"
    if not data_dir.exists():
        return None
    direct_matches = list(data_dir.glob(f"*/{chapter}.pdf"))
    if direct_matches:
        return direct_matches[0]
    for path in data_dir.rglob(f"{chapter}.pdf"):
        return path
    return None


@lru_cache(maxsize=128)
def raw_example_pdf_visual_rules(project_root: Path, chapter: str) -> dict[int, list[dict[str, Any]]]:
    pdf_path = chapter_pdf_path(project_root, chapter)
    if pdf_path is None:
        return {}
    pages = load_paddle_raw_pages(project_root, chapter)
    rules_by_page: dict[int, list[dict[str, Any]]] = {}
    for page_index, page in enumerate(pages):
        width, height = _page_size_from_payload_page(page)
        rules = _detect_visual_horizontal_rules(
            pdf_path=pdf_path,
            page_index=page_index + 1,
            expected_width=width,
            expected_height=height,
        )
        strong_rules = [
            rule
            for rule in rules
            if float(rule.get("coverage") or 0.0) >= 0.55
            and float(rule.get("max_row_dark_ratio") or 0.0) >= 0.45
        ]
        if strong_rules:
            rules_by_page[page_index] = strong_rules
    return rules_by_page


def bbox_horizontal_overlap_ratio(left_bbox: list[Any] | None, right_bbox: list[Any] | None) -> float:
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


def looks_like_post_rule_body(record: RawRecord) -> bool:
    if looks_like_example_start(record.content):
        return True
    if record.label == "paragraph_title":
        return True
    if record.label not in {"text", "reference_content", "figure_title", "header"}:
        return False
    return looks_like_new_body_paragraph_allowing_inline_math(record)


def pdf_visual_rule_between_records(
    previous: RawRecord,
    current: RawRecord,
    rules_by_page: dict[int, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    if previous.page_index != current.page_index:
        return None
    previous_bottom = raw_record_bottom(previous)
    current_top = raw_record_top(current)
    if previous_bottom is None or current_top is None:
        return None
    if current_top <= previous_bottom:
        return None
    previous_left = raw_record_left(previous)
    current_left = raw_record_left(current)
    margin_reset = (
        previous_left is not None
        and current_left is not None
        and current_left <= previous_left - 20
        and current.label in {"text", "reference_content", "figure_title"}
    )
    if not looks_like_post_rule_body(current) and not margin_reset:
        return None
    previous_can_end = text_ends_sentence(previous.content) or previous.label in {
        "display_formula",
        "formula_number",
        "table",
        "figure_title",
    }
    if not previous_can_end:
        return None
    for rule in rules_by_page.get(previous.page_index, []):
        bbox = rule.get("bbox")
        if not isinstance(bbox, list) or len(bbox) < 4:
            continue
        try:
            center_y = (float(bbox[1]) + float(bbox[3])) / 2.0
        except (TypeError, ValueError):
            continue
        if not (previous_bottom + 4 <= center_y <= current_top - 4):
            continue
        if bbox_horizontal_overlap_ratio(bbox, previous.bbox) < 0.40:
            continue
        if bbox_horizontal_overlap_ratio(bbox, current.bbox) < 0.40:
            continue
        return rule
    return None


def pdf_visual_rule_before_record(
    current: RawRecord,
    rules_by_page: dict[int, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    """Return a rendered horizontal rule immediately above ``current``.

    Example boxes often continue across pages.  In that layout the visual end
    rule can be at the top of the continuation page, with only page header/folio
    rows between the rule and the first post-example paragraph.  The ordinary
    same-page "between records" check cannot see that boundary, so this helper
    treats a strong rule above a body paragraph as a stop even when the previous
    in-example record is on the prior page.
    """

    current_top = raw_record_top(current)
    current_left = raw_record_left(current)
    page_left_body = (
        current_left is not None
        and current_left <= 180
        and current.label in {"text", "reference_content", "figure_title", "header"}
    )
    if current_top is None or (not looks_like_post_rule_body(current) and not page_left_body):
        return None
    for rule in rules_by_page.get(current.page_index, []):
        bbox = rule.get("bbox")
        if not isinstance(bbox, list) or len(bbox) < 4:
            continue
        try:
            center_y = (float(bbox[1]) + float(bbox[3])) / 2.0
        except (TypeError, ValueError):
            continue
        if not (center_y < current_top - 4):
            continue
        if current_top - center_y > 90:
            continue
        if bbox_horizontal_overlap_ratio(bbox, current.bbox) < 0.40:
            continue
        return rule
    return None


def raw_record_bottom(record: RawRecord) -> float | None:
    if isinstance(record.bbox, list) and len(record.bbox) >= 4:
        try:
            return float(record.bbox[3])
        except (TypeError, ValueError):
            return None
    return None


def raw_record_left(record: RawRecord) -> float | None:
    if isinstance(record.bbox, list) and len(record.bbox) >= 1:
        try:
            return float(record.bbox[0])
        except (TypeError, ValueError):
            return None
    return None


def raw_record_top(record: RawRecord) -> float | None:
    if isinstance(record.bbox, list) and len(record.bbox) >= 2:
        try:
            return float(record.bbox[1])
        except (TypeError, ValueError):
            return None
    return None


def raw_vertical_gap(left: RawRecord, right: RawRecord) -> float | None:
    if left.page_index != right.page_index:
        return None
    left_bottom = raw_record_bottom(left)
    right_top = raw_record_top(right)
    if left_bottom is None or right_top is None:
        return None
    return right_top - left_bottom


def text_ends_sentence(text: str) -> bool:
    return collapse_ws(text).endswith((".", "?", "!", ".)", ".]", '."'))


def looks_like_new_body_paragraph(record: RawRecord) -> bool:
    value = collapse_ws(record.content)
    if not value or raw_example_start_match(value):
        return False
    if re.search(r"(?:\[\[|\$\$?|\b\\begin\{|\b\\end\{)", value):
        return False
    if BODY_PARAGRAPH_OPENING_RE.match(value):
        return True
    if not re.match(r"^[A-Z][A-Za-z-]+\b", value):
        return False
    if re.match(r"^(?:And|As|But|Or|Thus|Hence|This|These|The|Why|Recall|Consider|Suppose|When|While|If)\b", value):
        return True
    return False


def looks_like_new_body_paragraph_allowing_inline_math(record: RawRecord) -> bool:
    value = collapse_ws(record.content)
    if not value or raw_example_start_match(value):
        return False
    if re.match(r"^\s*(?:\[\[|\$\$|\\begin\{|\\end\{)", value):
        return False
    value = re.sub(r"\$[^$]*\$", " MATH ", value)
    value = re.sub(r"\[\[[^\]]+\]\]", " REF ", value)
    if BODY_PARAGRAPH_OPENING_RE.match(value):
        return True
    if not re.match(r"^[A-Z][A-Za-z-]+\b", value):
        return False
    if re.match(r"^(?:And|As|But|Or|Thus|Hence|This|These|The|Why|Recall|Consider|Suppose|When|While|If)\b", value):
        return True
    return False


def is_strong_visual_stop(previous: RawRecord, current: RawRecord) -> tuple[bool, float]:
    gap = raw_vertical_gap(previous, current)
    if gap is None or gap < 45:
        return False, gap if gap is not None else 0.0
    previous_left = raw_record_left(previous)
    current_left = raw_record_left(current)
    margin_reset = previous_left is not None and current_left is not None and current_left <= previous_left - 20
    if margin_reset and current.label == "text" and looks_like_new_body_paragraph(current) and text_ends_sentence(previous.content):
        return True, gap
    return False, gap


def raw_example_visual_stops(
    records: list[RawRecord],
    *,
    rules_by_page: dict[int, list[dict[str, Any]]] | None = None,
) -> dict[str, list[RawExampleVisualStop]]:
    stops: dict[str, list[RawExampleVisualStop]] = defaultdict(list)
    rules_by_page = rules_by_page or {}
    index = 0
    while index < len(records):
        record = records[index]
        match = raw_example_start_match(record.content) if record.label in PADDLE_EXAMPLE_LABELS else None
        if not match:
            index += 1
            continue

        example_id = clean_ref_id(match.group("example_id"))
        last_content_record = record
        cursor = index + 1
        while cursor < len(records):
            current = records[cursor]
            if looks_like_example_start(current.content):
                break
            if current.label in PADDLE_PAGE_NOISE_LABELS or is_publication_footer(current.content):
                cursor += 1
                continue
            if current.label not in PADDLE_EXAMPLE_BODY_LABELS:
                break
            if current.label in {"paragraph_title"}:
                break
            pdf_rule = pdf_visual_rule_between_records(last_content_record, current, rules_by_page)
            if pdf_rule is None:
                pdf_rule = pdf_visual_rule_before_record(current, rules_by_page)
            if pdf_rule is not None:
                stops[example_id].append(
                    RawExampleVisualStop(
                        example_id=example_id,
                        included_tail=last_content_record.content,
                        stop_text=current.content,
                        page_index=current.page_index,
                        row_index=current.row_index,
                        vertical_gap=raw_vertical_gap(last_content_record, current) or 0.0,
                        source="pdf_rendered_horizontal_rule",
                        rule_bbox=pdf_rule.get("bbox") if isinstance(pdf_rule.get("bbox"), list) else None,
                        rule_coverage=float(pdf_rule.get("coverage") or 0.0),
                    )
                )
                break
            is_stop, gap = is_strong_visual_stop(last_content_record, current)
            if is_stop:
                stops[example_id].append(
                    RawExampleVisualStop(
                        example_id=example_id,
                        included_tail=last_content_record.content,
                        stop_text=current.content,
                        page_index=current.page_index,
                        row_index=current.row_index,
                        vertical_gap=gap,
                    )
                )
                break
            if current.label in {"text", "figure_title", "footer", "reference_content", "table", "display_formula", "formula_number"}:
                last_content_record = current
            cursor += 1
        index += 1
    return stops


def is_publication_footer(text: str) -> bool:
    return bool(PADDLE_PUBLICATION_FOOTER_RE.search(text or ""))


def raw_example_start_match(text: str) -> re.Match[str] | None:
    if is_publication_footer(text):
        return None
    value = str(text or "")
    match = EXAMPLE_HEAD_RE.search(value)
    if not match:
        return None
    if not is_example_heading_match(value, match):
        return None
    suffix = collapse_ws(value[match.end() :])
    if SAME_EXAMPLE_BACK_REFERENCE_RE.match(value[match.start() :]):
        return None
    if suffix and not match.group("trailing") and re.match(r"^[a-z]\b", suffix):
        return None
    return match


def looks_like_example_start(text: str) -> bool:
    return raw_example_start_match(text) is not None


def looks_like_post_example_body(record: RawRecord | dict[str, Any], example_id: str) -> bool:
    label = str(getattr(record, "label", "") if not isinstance(record, dict) else record.get("label") or "").lower()
    if label not in {"text", "reference_content"}:
        return False
    content = collapse_ws(str(getattr(record, "content", "") if not isinstance(record, dict) else record.get("content") or ""))
    if not content:
        return False
    back_ref = SAME_EXAMPLE_BACK_REFERENCE_RE.match(content)
    if back_ref and clean_ref_id(back_ref.group("example_id")).lower() == clean_ref_id(example_id).lower():
        return True
    return bool(AUTHOR_YEAR_PARAGRAPH_RE.match(content))


def looks_like_figure_reference_sentence(record: RawRecord) -> bool:
    if record.label != "text":
        return False
    content = collapse_ws(record.content)
    return bool(
        re.match(
            r"^\s*(?:Figure|Fig\.)\s+(?:A\d+|\d+)\.\d+[a-z]?\s+"
            r"(?:plots|shows|illustrates|summarizes|summarises|gives|provides|reports|contains)\b",
            content,
            flags=re.IGNORECASE,
        )
    )


def looks_like_in_example_figure_caption(record: RawRecord) -> bool:
    if record.label != "figure_title":
        return False
    content = collapse_ws(record.content)
    if not FIGURE_CAPTION_START_RE.match(content):
        return False
    return bool(re.search(r"\b(?:Example|Equation)\s+(?:A\d+|\d+)\.\d+[a-z]?\b", content, flags=re.IGNORECASE))


def raw_figure_caption_ref(record: RawRecord) -> str:
    if record.label != "figure_title":
        return ""
    match = re.match(
        r"^\s*(?:Figure|Fig\.)\s+((?:A\d+|\d+)\.\d+[a-z]?)\b",
        collapse_ws(record.content),
        flags=re.IGNORECASE,
    )
    return clean_ref_id(match.group(1)) if match else ""


def is_potential_example_continuation(record: RawRecord, parts: list[str]) -> bool:
    if not parts:
        return False
    if record.label in {"display_formula", "formula_number", "table"}:
        return True
    if record.label in {"text", "reference_content", "footnote"}:
        return True
    if record.label == "figure_title":
        content = collapse_ws(record.content)
        previous = parts[-1] if parts else ""
        if previous.endswith(("-", "‐", "‑", "‒", "–")) and is_lowercase_continuation(content):
            return True
        if raw_figure_caption_ref(record):
            return True
        if not FIGURE_CAPTION_START_RE.match(content):
            return True
    if looks_like_in_example_figure_caption(record):
        return True
    return False


def is_lowercase_continuation(text: str) -> bool:
    return bool(re.match(r"^[a-z][A-Za-z-]+\b", collapse_ws(text)))


def join_hyphenated(left: str, right: str) -> str:
    left = collapse_ws(left)
    right = collapse_ws(right)
    if not left:
        return right
    if not right:
        return left
    if left.endswith(("-", "‐", "‑", "‒", "–")) and re.match(r"^[a-z]", right):
        return left[:-1] + right
    left_words = re.findall(r"[A-Za-z]+", left)
    right_match = re.match(r"([A-Za-z]+)(\b.*)", right)
    if left_words and right_match and left_words[-1].lower() == right_match.group(1).lower():
        return f"{left}{right_match.group(2)}"
    return f"{left} {right}"


def raw_table_placeholder(table_index: int) -> str:
    return f"[[TABLE:inline_{table_index}]]"


def source_table_refs(chapter: str, source_file: str, context: StructuredContext) -> list[str]:
    for path, data in context.units_by_chapter.get(chapter, []):
        if path.name != source_file:
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        refs = metadata.get("table_references") if isinstance(metadata.get("table_references"), list) else []
        return dedupe_preserve_order([str(ref) for ref in refs])
    return []


def raw_table_placeholder_for_source(
    record: RawRecord,
    chapter_records: list[RawRecord],
    *,
    chapter: str,
    source_file: str,
    context: StructuredContext,
    used_table_refs: set[str],
) -> str:
    del chapter, source_file, context, used_table_refs
    return raw_table_placeholder(table_index_for_raw_record(record, chapter_records))


def table_index_for_raw_record(record: RawRecord, chapter_records: list[RawRecord]) -> int:
    table_count = 0
    for item in chapter_records:
        if item.label == "table" and "<table" in item.content.lower() and not raw_table_has_numbered_caption(
            item,
            chapter_records,
        ):
            table_count += 1
        if item is record:
            return table_count
    return table_count


def raw_table_has_numbered_caption(record: RawRecord, chapter_records: list[RawRecord]) -> bool:
    try:
        index = chapter_records.index(record)
    except ValueError:
        return False
    for previous in reversed(chapter_records[max(0, index - 3) : index]):
        if previous.page_index != record.page_index:
            continue
        if previous.label in PADDLE_PAGE_NOISE_LABELS:
            continue
        if previous.label == "table":
            return False
        if previous.label in {"figure_title", "paragraph_title", "text"}:
            return bool(
                re.match(
                    r"^\s*Table\s+(?:A\d+|\d+)\.\d+[A-Za-z]?\b",
                    previous.content,
                    flags=re.IGNORECASE,
                )
            )
    return False


def should_continue_raw_example(next_record: RawRecord, parts: list[str]) -> bool:
    if is_publication_footer(next_record.content):
        return False
    if looks_like_example_start(next_record.content):
        return True
    if is_lowercase_continuation(next_record.content):
        return True
    previous = parts[-1] if parts else ""
    if TABLE_MARKER_RE.search(previous) and next_record.label == "text":
        after_table = TABLE_MARKER_RE.sub("", previous).strip()
        return not after_table
    return False


def raw_example_stop_for_body(
    record: RawRecord,
    parts: list[str],
    chapter_records: list[RawRecord] | None = None,
    *,
    visual_box_active: bool = False,
) -> bool:
    if record.label in PADDLE_PAGE_NOISE_LABELS or is_publication_footer(record.content):
        return False
    current_example_id = ""
    if parts:
        head_match = raw_example_start_match(parts[0])
        current_example_id = clean_ref_id(head_match.group("example_id")) if head_match else ""
    if (
        current_example_id
        and not visual_box_active
        and looks_like_post_example_body(record, current_example_id)
    ):
        return True
    if looks_like_example_start(record.content):
        return True
    if re.match(
        r"^\s*Table\s+(?:A\d+|\d+)\.\d+[A-Za-z]?\b",
        record.content,
        flags=re.IGNORECASE,
    ):
        return True
    if FIGURE_CAPTION_START_RE.match(record.content) and not (
        looks_like_figure_reference_sentence(record)
        or visual_box_active
        or looks_like_in_example_figure_caption(record)
    ):
        return True
    if chapter_records is not None and raw_table_has_numbered_caption(record, chapter_records):
        return True
    if record.label == "paragraph_title":
        return True
    if record.label not in PADDLE_EXAMPLE_BODY_LABELS:
        return True
    if parts:
        previous = parts[-1]
        if record.label == "text":
            current = collapse_ws(record.content)
            if re.match(r"^As\s+Example\s+(?:A\d+|\d+)\.\d+\b", current, flags=re.IGNORECASE):
                return True
        if (
            record.label == "text"
            and not visual_box_active
            and not should_continue_raw_example(record, parts)
        ):
            previous_text = next((part for part in reversed(parts) if not TABLE_MARKER_RE.fullmatch(part.strip())), previous)
            if text_ends_sentence(previous_text) and looks_like_new_body_paragraph(record):
                return True
    return False


def append_raw_record_to_example_parts(
    record: RawRecord,
    parts: list[str],
    chapter_records: list[RawRecord],
    *,
    chapter: str,
    source_file: str,
    context: StructuredContext,
    used_table_refs: set[str],
) -> None:
    if record.label == "table" and "<table" in record.content.lower():
        if raw_table_has_numbered_caption(record, chapter_records):
            return
        parts.append(
            raw_table_placeholder_for_source(
                record,
                chapter_records,
                chapter=chapter,
                source_file=source_file,
                context=context,
                used_table_refs=used_table_refs,
            )
        )
        return
    if record.label == "display_formula":
        parts.append(record.content)
        return
    figure_ref = raw_figure_caption_ref(record)
    if figure_ref:
        parts.append(f"[[FIGURE:{figure_ref}]]")
        return
    if parts and should_continue_raw_example(record, parts):
        parts[-1] = join_hyphenated(parts[-1], record.content)
        return
    parts.append(record.content)


def next_placeholder_source(
    chapter: str,
    example_id: str,
    context: StructuredContext,
) -> tuple[str, int]:
    direct = context.placeholder_locations.get((chapter, example_id))
    if direct:
        return direct

    ordered = context.placeholder_order.get(chapter, [])
    for ref, file_name, block_index in ordered:
        if natural_key(ref) > natural_key(example_id):
            return file_name, block_index

    units = context.units_by_chapter.get(chapter, [])
    if units:
        path, data = units[-1]
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        return path.name, max(0, len(blocks) - 1)
    return f"{chapter}_001.json", 0


def raw_example_matches_structured_content(
    raw_text: str,
    chapter: str,
    context: StructuredContext,
    threshold_tokens: int = 10,
) -> bool:
    raw_norm = normalize_match_text(raw_text)
    if not raw_norm:
        return False
    raw_tokens = raw_norm.split()
    if len(raw_tokens) < threshold_tokens:
        return False
    anchors = [
        " ".join(raw_tokens[:threshold_tokens]),
        " ".join(raw_tokens[max(0, len(raw_tokens) // 2 - 3) : max(0, len(raw_tokens) // 2 - 3) + threshold_tokens]),
    ]
    for _, _, content in context.block_locations.get(chapter, []):
        content_norm = normalize_match_text(content)
        if any(anchor and anchor in content_norm for anchor in anchors):
            return True
    return False


def raw_example_to_candidate(
    *,
    chapter: str,
    example_id: str,
    raw_parts: list[str],
    source_file: str,
    source_block_index: int,
    source_page: int,
    visual_stop: RawExampleVisualStop | None = None,
) -> ExampleCandidate:
    content_markdown = collapse_ws(" ".join(part for part in raw_parts if part.strip()))
    content_markdown = normalize_heading_prefix(content_markdown)
    content_plain = collapse_ws(strip_structured_refs(strip_html(content_markdown)))
    after_heading = collapse_ws(
        re.sub(
            r"^\s*Example\s+(?:A\d+|\d+)\.\d+[a-z]?\.\s*",
            "",
            content_markdown,
            count=1,
            flags=re.IGNORECASE,
        )
    )
    title = after_heading[:160].strip()
    formula_refs = extract_formula_refs(content_markdown)
    table_refs = extract_table_refs(content_markdown)
    figure_refs = extract_figure_refs(content_markdown)
    external_refs = extract_external_refs(content_markdown)
    evidence = {
        "source": "paddle_raw_layout+structured_blocks",
        "detection_method": "raw_layout_example_recovery",
        "confidence": 0.93,
        "source_page": source_page,
    }
    metadata = {
        "has_formula": bool(formula_refs),
        "has_table": bool(table_refs),
        "has_figure": bool(figure_refs),
        "word_count": len(content_plain.split()) if content_plain else 0,
        "needs_review": looks_truncated(content_markdown),
    }
    if visual_stop is not None:
        evidence = {
            **evidence,
            "visual_stop_clipped": True,
            "visual_stop_source": visual_stop.source,
            "visual_stop_page": visual_stop.page_index + 1,
            "visual_stop_row_index": visual_stop.row_index,
            "visual_stop_vertical_gap": visual_stop.vertical_gap,
        }
        if visual_stop.rule_bbox:
            evidence["visual_stop_rule_bbox"] = visual_stop.rule_bbox
        if visual_stop.rule_coverage is not None:
            evidence["visual_stop_rule_coverage"] = visual_stop.rule_coverage
        metadata["visual_stop_clipped"] = True
        metadata["visual_stop"] = {
            "included_tail": visual_stop.included_tail,
            "stop_text": visual_stop.stop_text,
            "page_index": visual_stop.page_index,
            "row_index": visual_stop.row_index,
            "source": visual_stop.source,
        }
    return ExampleCandidate(
        example_id=example_id,
        chapter=chapter,
        label=f"Example {example_id}",
        title=title,
        source_file=source_file,
        start_block_index=source_block_index,
        end_block_index=source_block_index,
        block_ids=[],
        content_markdown=content_markdown,
        content_plain=content_plain,
        formula_refs=formula_refs,
        table_refs=table_refs,
        figure_refs=figure_refs,
        external_refs=external_refs,
        evidence=evidence,
        metadata=metadata,
        _order_key=(chapter_sort_key(chapter), natural_key(source_file), source_block_index, natural_key(example_id)),
    )


def existing_library_row_to_candidate(row: dict[str, Any]) -> ExampleCandidate | None:
    example_id = clean_ref_id(str(row.get("example_id") or row.get("example_ref") or ""))
    chapter = str(row.get("chapter") or "").strip().lower()
    source_file = str(row.get("source_file") or f"{chapter}_001.json")
    content_markdown = str(row.get("content_markdown") or "")
    if not example_id or not chapter or not content_markdown.strip():
        return None

    content_plain = str(row.get("content_plain") or collapse_ws(strip_structured_refs(strip_html(content_markdown))))
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    start_block_index = int(row.get("start_block_index") or 0)
    end_block_index = int(row.get("end_block_index") if row.get("end_block_index") is not None else start_block_index)
    formula_refs = row.get("formula_refs") if isinstance(row.get("formula_refs"), list) else extract_formula_refs(content_markdown)
    table_refs = row.get("table_refs") if isinstance(row.get("table_refs"), list) else extract_table_refs(content_markdown)
    figure_refs = row.get("figure_refs") if isinstance(row.get("figure_refs"), list) else extract_figure_refs(content_markdown)
    external_refs = row.get("external_refs") if isinstance(row.get("external_refs"), list) else extract_external_refs(content_markdown)
    return ExampleCandidate(
        example_id=example_id,
        chapter=chapter,
        label=str(row.get("label") or f"Example {example_id}"),
        title=str(row.get("title") or collapse_ws(content_plain)[:160]),
        source_file=source_file,
        start_block_index=start_block_index,
        end_block_index=end_block_index,
        block_ids=[str(item) for item in row.get("block_ids", [])] if isinstance(row.get("block_ids"), list) else [],
        content_markdown=content_markdown,
        content_plain=content_plain,
        formula_refs=dedupe_preserve_order([str(item) for item in formula_refs]),
        table_refs=dedupe_preserve_order([str(item) for item in table_refs]),
        figure_refs=dedupe_preserve_order([str(item) for item in figure_refs]),
        external_refs=dedupe_preserve_order([str(item) for item in external_refs]),
        evidence={
            **evidence,
            "library_merge_source": "existing_example_library",
        },
        metadata={
            **metadata,
            "has_formula": bool(formula_refs),
            "has_table": bool(table_refs),
            "has_figure": bool(figure_refs),
            "word_count": metadata.get("word_count") or (len(content_plain.split()) if content_plain else 0),
            "needs_review": metadata.get("needs_review", looks_truncated(content_markdown)),
        },
        _order_key=(chapter_sort_key(chapter), natural_key(source_file), start_block_index, natural_key(example_id)),
    )


def align_candidate_to_placeholder(item: ExampleCandidate, context: StructuredContext) -> ExampleCandidate:
    direct = context.placeholder_locations.get((item.chapter, item.example_id))
    if not direct:
        return item
    source_file, block_index = direct
    item.source_file = source_file
    item.start_block_index = block_index
    item.end_block_index = block_index
    item._order_key = (
        chapter_sort_key(item.chapter),
        natural_key(item.source_file),
        item.start_block_index,
        natural_key(item.example_id),
    )
    return item


def load_existing_example_library_candidates(
    structured_dir: Path,
    context: StructuredContext,
) -> list[ExampleCandidate]:
    path = structured_dir / "example_library.json"
    if not path.exists():
        return []
    try:
        payload = read_json(path)
    except Exception:
        return []
    rows = payload.get("examples") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return []
    candidates: list[ExampleCandidate] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        candidate = existing_library_row_to_candidate(row)
        if candidate is not None:
            candidates.append(align_candidate_to_placeholder(candidate, context))
    return candidates


def example_quality_score(item: ExampleCandidate) -> tuple[int, int, int, int]:
    metadata = item.metadata if isinstance(item.metadata, dict) else {}
    content_plain = item.content_plain or collapse_ws(strip_structured_refs(strip_html(item.content_markdown)))
    return (
        0 if metadata.get("needs_review") else 1,
        int(bool(item.formula_refs)) + int(bool(item.table_refs)),
        len(content_plain.split()),
        len(item.content_markdown),
    )


def merge_existing_library_candidates(
    examples: list[ExampleCandidate],
    existing_library_examples: list[ExampleCandidate],
) -> list[ExampleCandidate]:
    merged: dict[tuple[str, str], ExampleCandidate] = {}
    for item in [*examples, *existing_library_examples]:
        key = (item.chapter, item.example_id)
        current = merged.get(key)
        if current is None or example_quality_score(item) > example_quality_score(current):
            merged[key] = item
    return sorted(merged.values(), key=lambda item: item._order_key)


def recover_examples_from_paddle_raw(
    *,
    project_root: Path,
    chapter: str,
    context: StructuredContext,
    existing_ids: set[str],
    target_ids: set[str] | None = None,
    skip_structured_matches: bool = True,
) -> list[ExampleCandidate]:
    records = ordered_paddle_records(project_root, chapter)
    if not records:
        return []

    rules_by_page = raw_example_pdf_visual_rules(project_root, chapter)
    normalized_target_ids = {clean_ref_id(item).lower() for item in target_ids} if target_ids is not None else None
    recovered: list[ExampleCandidate] = []
    index = 0
    while index < len(records):
        record = records[index]
        if record.label not in PADDLE_EXAMPLE_LABELS or not looks_like_example_start(record.content):
            index += 1
            continue

        match = raw_example_start_match(record.content)
        if not match:
            index += 1
            continue
        example_id = clean_ref_id(match.group("example_id"))
        if not example_id or example_id in existing_ids:
            index += 1
            continue
        if normalized_target_ids is not None and example_id.lower() not in normalized_target_ids:
            index += 1
            continue

        source_file, source_block_index = next_placeholder_source(chapter, example_id, context)
        parts = [record.content]
        used_table_refs: set[str] = set()
        visual_stop = None
        last_content_record = record
        visual_box_active = bool(
            pdf_visual_rule_before_record(record, rules_by_page)
            or any(
                isinstance(rule.get("bbox"), list)
                and len(rule.get("bbox")) >= 4
                and raw_record_top(record) is not None
                and raw_record_top(record) > float(rule.get("bbox")[3])
                and raw_record_top(record) - float(rule.get("bbox")[3]) <= 90
                and bbox_horizontal_overlap_ratio(rule.get("bbox"), record.bbox) >= 0.40
                for rule in rules_by_page.get(record.page_index, [])
            )
        )
        cursor = index + 1
        while cursor < len(records):
            next_record = records[cursor]
            if next_record.label in PADDLE_PAGE_NOISE_LABELS or is_publication_footer(next_record.content):
                cursor += 1
                continue
            pdf_rule = pdf_visual_rule_between_records(last_content_record, next_record, rules_by_page)
            if pdf_rule is None:
                pdf_rule = pdf_visual_rule_before_record(next_record, rules_by_page)
            if pdf_rule is not None:
                visual_stop = RawExampleVisualStop(
                    example_id=example_id,
                    included_tail=last_content_record.content,
                    stop_text=next_record.content,
                    page_index=next_record.page_index,
                    row_index=next_record.row_index,
                    vertical_gap=raw_vertical_gap(last_content_record, next_record) or 0.0,
                    source="pdf_rendered_horizontal_rule",
                    rule_bbox=pdf_rule.get("bbox") if isinstance(pdf_rule.get("bbox"), list) else None,
                    rule_coverage=float(pdf_rule.get("coverage") or 0.0),
                )
                break
            if raw_example_stop_for_body(
                next_record,
                parts,
                records,
                visual_box_active=visual_box_active,
            ):
                break
            if visual_box_active and not is_potential_example_continuation(next_record, parts):
                break
            append_raw_record_to_example_parts(
                next_record,
                parts,
                records,
                chapter=chapter,
                source_file=source_file,
                context=context,
                used_table_refs=used_table_refs,
            )
            if next_record.label in {
                "text",
                "figure_title",
                "footer",
                "reference_content",
                "footnote",
                "table",
                "display_formula",
                "formula_number",
            }:
                last_content_record = next_record
            cursor += 1

        raw_text = " ".join(parts)
        if skip_structured_matches and raw_example_matches_structured_content(raw_text, chapter, context):
            index += 1
            continue

        recovered.append(
            raw_example_to_candidate(
                chapter=chapter,
                example_id=example_id,
                raw_parts=parts,
                source_file=source_file,
                source_block_index=source_block_index,
                source_page=record.page_index + 1,
                visual_stop=visual_stop,
            )
        )
        existing_ids.add(example_id)
        index = max(cursor, index + 1)

    return recovered


def extract_examples_for_structured_dir(
    structured_dir: Path,
    *,
    project_root: Path = PROJECT_ROOT,
) -> tuple[list[ExampleCandidate], list[tuple[str, int]], StructuredContext]:
    context = build_structured_context(structured_dir)
    all_examples: list[ExampleCandidate] = []
    per_file_counts: list[tuple[str, int]] = []

    for chapter, units in sorted(context.units_by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        chapter_examples: list[ExampleCandidate] = []
        chapter_records = ordered_paddle_records(project_root, chapter)
        rules_by_page = raw_example_pdf_visual_rules(project_root, chapter) if chapter_records else {}
        visual_stops = raw_example_visual_stops(chapter_records, rules_by_page=rules_by_page) if chapter_records else {}
        for path, data in units:
            examples = extract_examples_for_file(path, data, visual_stops=visual_stops)
            chapter_examples.extend(examples)
            per_file_counts.append((path.name, len(examples)))

        existing_ids = {item.example_id for item in chapter_examples}
        placeholder_ids = {
            ref
            for ref, _, _ in context.placeholder_order.get(chapter, [])
            if ref not in existing_ids
        }
        raw_recovered = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=existing_ids,
            target_ids=placeholder_ids,
        )
        if raw_recovered:
            per_file_counts.append((f"{chapter}:paddle_raw_layout", len(raw_recovered)))
        all_examples.extend(chapter_examples)
        all_examples.extend(raw_recovered)

    all_examples.sort(key=lambda item: item._order_key)
    existing_library_examples = load_existing_example_library_candidates(structured_dir, context)
    if existing_library_examples:
        per_file_counts.append(("example_library.json:existing", len(existing_library_examples)))
        all_examples = merge_existing_library_candidates(all_examples, existing_library_examples)
    else:
        all_examples.sort(key=lambda item: item._order_key)
    return all_examples, per_file_counts, context


def example_numeric_parts(example_id: str) -> tuple[str, int] | None:
    match = re.fullmatch(r"((?:A\d+|\d+))\.(\d+)[a-z]?", clean_ref_id(example_id), flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower(), int(match.group(2))


def find_example_sequence_gaps(examples: list[ExampleCandidate]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    for item in examples:
        parts = example_numeric_parts(item.example_id)
        if parts is None:
            continue
        prefix, number = parts
        grouped[(item.chapter, prefix)].add(number)

    gaps: list[dict[str, Any]] = []
    for (chapter, prefix), numbers in sorted(
        grouped.items(),
        key=lambda item: (chapter_sort_key(item[0][0]), natural_key(item[0][1])),
    ):
        if len(numbers) < 2:
            continue
        minimum = min(numbers)
        maximum = max(numbers)
        missing = [number for number in range(minimum, maximum + 1) if number not in numbers]
        if not missing:
            continue
        gaps.append(
            {
                "chapter": chapter,
                "prefix": prefix,
                "first": minimum,
                "last": maximum,
                "missing": missing,
            }
        )
    return gaps


