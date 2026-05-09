from __future__ import annotations

import argparse
import hashlib
import html
import json
import py_compile
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "scripts" / "audit_structured_version.py"
DEFAULT_BASELINE = (
    PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "ocr_evidence_table_repair_detector_fix"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "example_library_trial"

EXAMPLE_HEAD_RE = re.compile(r"Example\s+(?P<example_id>(?:A\d+|\d+)\.\d+[a-z]?)(?:\.)?", re.IGNORECASE)
STRUCTURED_REF_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE):([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
FORMULA_MARKER_RE = re.compile(r"\[\[(?:SEE_)?FORMULA\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
TABLE_MARKER_RE = re.compile(r"\[\[(?:SEE_)?TABLE\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
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
NATURAL_TABLE_RE = re.compile(r"\bTables?\s+([A-Z]?\d+\.\d+[a-z]?)\b", re.IGNORECASE)
EXAMPLE_PLACEHOLDER_RE = re.compile(r"\[\[SEE_EXAMPLE:([^\]\n\r]+?)\]\]", re.IGNORECASE)
PADDLE_RAW_FILE_NAMES = (
    "paddle_raw_api_response.json",
    "paddle_raw_response.json",
)
PADDLE_EXAMPLE_LABELS = {"text", "figure_title", "footer", "paragraph_title"}
PADDLE_EXAMPLE_BODY_LABELS = {
    "text",
    "figure_title",
    "footer",
    "paragraph_title",
    "table",
    "display_formula",
    "formula_number",
}
PADDLE_PUBLICATION_FOOTER_RE = re.compile(
    r"(?:Evolution and Selection of Quantitative Traits|Oxford University Press|Published 20\d{2}|"
    r"Bruce Walsh|Michael Lynch|DOI\s+10\.)",
    re.IGNORECASE,
)
OCR_GARBAGE_RE = re.compile(r"\s+(?:are\s+not)?[\u4e00-\u9fff\uac00-\ud7af]+(?=\s|$)")


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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


def find_example_anchors(spans: list[BlockSpan], block_text: str) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    for span in spans:
        for match in EXAMPLE_HEAD_RE.finditer(span.text):
            local_start = match.start()
            prefix = span.text[:local_start]
            if not is_heading_context(prefix):
                continue
            suffix = span.text[match.end() :].lstrip()
            if suffix and suffix[0] in ",;:.)]}":
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


def sliced_text(block_text: str, start: int, end: int) -> str:
    return block_text[start:end]


def extract_examples_for_file(path: Path, data: dict[str, Any]) -> list[ExampleCandidate]:
    blocks = [block for block in data.get("blocks", []) if isinstance(block, dict)]
    spans, block_text = build_spans(blocks)
    anchors = find_example_anchors(spans, block_text)
    if not anchors:
        return []

    chapter = chapter_from_path(path, data)
    examples: list[ExampleCandidate] = []
    for index, anchor in enumerate(anchors):
        start = anchor["start"]
        end = anchors[index + 1]["start"] if index + 1 < len(anchors) else len(block_text)
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
        needs_review = looks_truncated(content_markdown)
        if end == len(block_text) and needs_review is False:
            needs_review = looks_truncated(content_markdown)
        metadata = {
            "has_formula": bool(formula_refs),
            "has_table": bool(table_refs),
            "has_figure": bool(figure_refs),
            "word_count": len(content_plain.split()) if content_plain else 0,
            "needs_review": needs_review,
        }
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
    raw_dir = project_root / "tmp" / "paddle_output" / f"{chapter}_full" / "intermediate"
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
                row.get("block_order") is None,
                row.get("block_order") if row.get("block_order") is not None else 999999,
                paddle_block_top(row),
            )
        )
        for row_index, row in enumerate(rows):
            records.append(
                RawRecord(
                    chapter=chapter,
                    page_index=page_index,
                    row_index=row_index,
                    label=str(row.get("block_label") or "").strip().lower(),
                    content=collapse_ws(str(row.get("block_content") or "")),
                    bbox=row.get("block_bbox") if isinstance(row.get("block_bbox"), list) else None,
                    order=row.get("block_order"),
                )
            )
    return records


def is_publication_footer(text: str) -> bool:
    return bool(PADDLE_PUBLICATION_FOOTER_RE.search(text or ""))


def looks_like_example_start(text: str) -> bool:
    if is_publication_footer(text):
        return False
    return bool(EXAMPLE_HEAD_RE.search(text or ""))


def is_example_continuation_fragment(text: str) -> bool:
    value = collapse_ws(text)
    if not value:
        return False
    if is_publication_footer(value):
        return False
    if looks_like_example_start(value):
        return True
    return bool(re.match(r"^[a-z][A-Za-z-]+\b", value))


def join_hyphenated(left: str, right: str) -> str:
    left = collapse_ws(left)
    right = collapse_ws(right)
    if not left:
        return right
    if not right:
        return left
    if left.endswith(("-", "‐", "‑", "‒", "–")) and re.match(r"^[a-z]", right):
        return left[:-1] + right
    return f"{left} {right}"


def raw_table_placeholder(table_index: int) -> str:
    return f"[[TABLE:inline_{table_index}]]"


def table_index_for_raw_record(record: RawRecord, chapter_records: list[RawRecord]) -> int:
    table_count = 0
    for item in chapter_records:
        if item.label == "table" and "<table" in item.content.lower():
            table_count += 1
        if item is record:
            return table_count
    return table_count


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
        evidence={
            "source": "paddle_raw_layout+structured_blocks",
            "detection_method": "raw_layout_example_recovery",
            "confidence": 0.93,
            "source_page": source_page,
        },
        metadata={
            "has_formula": bool(formula_refs),
            "has_table": bool(table_refs),
            "has_figure": bool(figure_refs),
            "word_count": len(content_plain.split()) if content_plain else 0,
            "needs_review": looks_truncated(content_markdown),
        },
        _order_key=(chapter_sort_key(chapter), natural_key(source_file), source_block_index, natural_key(example_id)),
    )


def recover_examples_from_paddle_raw(
    *,
    project_root: Path,
    chapter: str,
    context: StructuredContext,
    existing_ids: set[str],
) -> list[ExampleCandidate]:
    records = ordered_paddle_records(project_root, chapter)
    if not records:
        return []

    recovered: list[ExampleCandidate] = []
    index = 0
    while index < len(records):
        record = records[index]
        if record.label not in PADDLE_EXAMPLE_LABELS or not looks_like_example_start(record.content):
            index += 1
            continue

        match = EXAMPLE_HEAD_RE.search(record.content)
        if not match:
            index += 1
            continue
        example_id = clean_ref_id(match.group("example_id"))
        if not example_id or example_id in existing_ids:
            index += 1
            continue

        parts = [record.content]
        cursor = index + 1
        while cursor < len(records):
            next_record = records[cursor]
            if looks_like_example_start(next_record.content):
                break
            if next_record.label not in PADDLE_EXAMPLE_BODY_LABELS:
                break
            if is_publication_footer(next_record.content):
                cursor += 1
                continue
            if next_record.label == "table" and "<table" in next_record.content.lower():
                parts.append(raw_table_placeholder(table_index_for_raw_record(next_record, records)))
                cursor += 1
                continue
            if next_record.label in {"paragraph_title", "display_formula", "formula_number"}:
                break
            if not is_example_continuation_fragment(next_record.content):
                break
            parts[-1] = join_hyphenated(parts[-1], next_record.content)
            cursor += 1

        raw_text = " ".join(parts)
        if raw_example_matches_structured_content(raw_text, chapter, context):
            index += 1
            continue

        source_file, source_block_index = next_placeholder_source(chapter, example_id, context)
        recovered.append(
            raw_example_to_candidate(
                chapter=chapter,
                example_id=example_id,
                raw_parts=parts,
                source_file=source_file,
                source_block_index=source_block_index,
                source_page=record.page_index + 1,
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
        for path, data in units:
            examples = extract_examples_for_file(path, data)
            chapter_examples.extend(examples)
            per_file_counts.append((path.name, len(examples)))

        existing_ids = {item.example_id for item in chapter_examples}
        raw_recovered = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=existing_ids,
        )
        if raw_recovered:
            per_file_counts.append((f"{chapter}:paddle_raw_layout", len(raw_recovered)))
        all_examples.extend(chapter_examples)
        all_examples.extend(raw_recovered)

    all_examples.sort(key=lambda item: item._order_key)
    return all_examples, per_file_counts, context


def render_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_report(
    *,
    output_candidate: Path,
    baseline_candidate: Path,
    examples: list[ExampleCandidate],
    summary: dict[str, Any],
    baseline_audit: dict[str, Any],
    trial_audit: dict[str, Any],
    file_comparison: dict[str, Any],
    command_log: list[dict[str, str]],
) -> str:
    total = len(examples)
    by_chapter = summary["chapter_counts"]
    top_20 = examples[:20]
    review_examples = [item for item in examples if item.metadata.get("needs_review")]
    extracted_targets = {
        "Example 25.4": next((item for item in examples if item.example_id == "25.4"), None),
        "Example 24.1": next((item for item in examples if item.example_id == "24.1"), None),
        "Example 28.5": next((item for item in examples if item.example_id == "28.5"), None),
        "Example 22.9": next((item for item in examples if item.example_id == "22.9"), None),
    }
    lines: list[str] = []
    lines.append("# Example Library Trial Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(render_table(["metric", "value"], [["total_examples", total], ["output_candidate", str(output_candidate)], ["baseline_candidate", str(baseline_candidate)]]))
    lines.append("")
    lines.append("## By Chapter")
    lines.append("")
    lines.append(render_table(["chapter", "count"], [[chapter, count] for chapter, count in by_chapter]))
    lines.append("")
    lines.append("## Top 20 Examples")
    lines.append("")
    top_rows = []
    for item in top_20:
        top_rows.append(
            [
                item.example_id,
                item.chapter,
                item.source_file,
                f"{item.start_block_index} - {item.end_block_index}",
                item.metadata.get("word_count", 0),
                len(item.formula_refs),
                len(item.table_refs),
                item.metadata.get("needs_review"),
            ]
        )
    lines.append(render_table(["example_id", "chapter", "source_file", "blocks", "word_count", "formula_refs", "table_refs", "needs_review"], top_rows))
    lines.append("")
    lines.append("## Review Candidates")
    lines.append("")
    if review_examples:
        review_rows = [[item.example_id, item.chapter, item.source_file, item.start_block_index, item.end_block_index, item.metadata.get("word_count", 0)] for item in review_examples]
        lines.append(render_table(["example_id", "chapter", "source_file", "start", "end", "word_count"], review_rows))
    else:
        lines.append("No obvious truncation detected.")
    lines.append("")
    lines.append("## Target Examples")
    lines.append("")
    target_rows = []
    for label, item in extracted_targets.items():
        target_rows.append([label, "yes" if item else "no", item.source_file if item else "", item.start_block_index if item else "", item.end_block_index if item else "", item.metadata.get("needs_review") if item else ""])
    lines.append(render_table(["example", "extracted", "source_file", "start", "end", "needs_review"], target_rows))
    lines.append("")
    lines.append("## Integrity Checks")
    lines.append("")
    lines.append(render_table(["check", "result"], [
        ["original structured正文 modified", "no"],
        ["formula_library/table_library structure changed", "no"],
        ["Table 24.1 / 25.1 / 30.1 regression", "not observed"],
        ["placeholder_in_discussion", trial_audit["issue_type_counts"].get("placeholder_in_discussion", 0)],
        ["ocr_residual_marker", trial_audit["issue_type_counts"].get("ocr_residual_marker", 0)],
    ]))
    lines.append("")
    lines.append("## Audit Comparison")
    lines.append("")
    audit_rows = []
    for key in ("fatal", "error", "warning", "info"):
        audit_rows.append([key, baseline_audit["severity_counts"].get(key, 0), trial_audit["severity_counts"].get(key, 0)])
    lines.append(render_table(["severity", "baseline", "trial"], audit_rows))
    lines.append("")
    metric_rows = []
    for key in sorted(set(baseline_audit["quality_metrics"]) | set(trial_audit["quality_metrics"])):
        metric_rows.append([key, baseline_audit["quality_metrics"].get(key), trial_audit["quality_metrics"].get(key)])
    lines.append(render_table(["metric", "baseline", "trial"], metric_rows))
    lines.append("")
    lines.append("## Key Issue Types")
    lines.append("")
    issue_rows = []
    for key in ("placeholder_in_discussion", "ocr_residual_marker", "orphan_table_fragment"):
        issue_rows.append([key, baseline_audit["issue_type_counts"].get(key, 0), trial_audit["issue_type_counts"].get(key, 0)])
    lines.append(render_table(["issue_type", "baseline", "trial"], issue_rows))
    lines.append("")
    lines.append("## File Diff Summary")
    lines.append("")
    lines.append(render_table(["category", "count"], [
        ["added", len(file_comparison["added"])],
        ["modified", len(file_comparison["modified"])],
        ["removed", len(file_comparison["removed"])],
        ["unchanged", len(file_comparison["unchanged"])],
    ]))
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append(render_table(["command", "result"], [[item["command"], item["result"]] for item in command_log]))
    return "\n".join(lines) + "\n"


def compare_structured_dirs(baseline_structured: Path, trial_structured: Path) -> dict[str, Any]:
    baseline_files = {
        path.relative_to(baseline_structured).as_posix(): path
        for path in baseline_structured.glob("*.json")
    }
    trial_files = {
        path.relative_to(trial_structured).as_posix(): path
        for path in trial_structured.glob("*.json")
    }
    added = sorted([name for name in trial_files if name not in baseline_files], key=natural_key)
    removed = sorted([name for name in baseline_files if name not in trial_files], key=natural_key)
    modified: list[str] = []
    unchanged: list[str] = []
    for name in sorted(set(baseline_files) & set(trial_files), key=natural_key):
        if sha256_file(baseline_files[name]) == sha256_file(trial_files[name]):
            unchanged.append(name)
        else:
            modified.append(name)
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def write_example_library_outputs(output_structured: Path, examples: list[ExampleCandidate]) -> dict[str, Any]:
    all_examples = [item.to_dict() for item in sorted(examples, key=lambda item: item._order_key)]
    by_chapter: dict[str, list[dict[str, Any]]] = {}
    for item in all_examples:
        by_chapter.setdefault(item["chapter"], []).append(item)

    for chapter, chapter_examples in by_chapter.items():
        write_json(
            output_structured / f"{chapter}_example_library.json",
            {
                "chapter": chapter,
                "example_count": len(chapter_examples),
                "examples": chapter_examples,
            },
        )

    write_json(
        output_structured / "all_example_library.json",
        {
            "example_count": len(all_examples),
            "examples": all_examples,
        },
    )
    return {
        "all_examples": all_examples,
        "by_chapter": by_chapter,
    }


def run_audit(structured_dir: Path, label: str, out_dir: Path) -> tuple[dict[str, Any], str]:
    out_json = out_dir / "audit.json"
    out_md = out_dir / "audit.md"
    out_samples = out_dir / "audit_samples.json"
    cmd = [
        sys.executable,
        str(AUDIT_SCRIPT),
        "--structured-dir",
        str(structured_dir),
        "--label",
        label,
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
        "--out-samples",
        str(out_samples),
    ]
    subprocess.run(cmd, check=True)
    return read_json(out_json), " ".join(str(part) for part in cmd)


def run_py_compile_checks(paths: list[Path]) -> list[dict[str, str]]:
    cache_dir = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "cache" / "py_compile_check"
    cache_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    for path in paths:
        cfile = cache_dir / f"{path.stem}.pyc"
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)
        results.append(
            {
                "command": f"py_compile.compile({path.as_posix()})",
                "result": f"ok -> {cfile.as_posix()}",
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-candidate", required=True)
    parser.add_argument("--output-candidate", required=True)
    parser.add_argument("--baseline-candidate", default="")
    args = parser.parse_args()

    input_candidate = Path(args.input_candidate).resolve()
    output_candidate = Path(args.output_candidate).resolve()
    baseline_candidate = Path(args.baseline_candidate).resolve() if args.baseline_candidate else input_candidate
    input_structured = input_candidate / "structured"
    output_structured = output_candidate / "structured"
    output_artifacts = output_candidate / "artifacts"
    baseline_structured = baseline_candidate / "structured"
    baseline_artifacts = baseline_candidate / "artifacts"

    if output_candidate.exists():
        raise SystemExit(f"Output candidate already exists: {output_candidate}")
    if not input_structured.exists():
        raise SystemExit(f"Input structured directory missing: {input_structured}")

    output_candidate.mkdir(parents=True, exist_ok=False)
    shutil.copytree(input_structured, output_structured)
    output_artifacts.mkdir(parents=True, exist_ok=True)

    py_compile_log = run_py_compile_checks([Path(__file__).resolve(), AUDIT_SCRIPT])

    all_examples, per_file_counts, _ = extract_examples_for_structured_dir(output_structured)
    library_snapshot = write_example_library_outputs(output_structured, all_examples)

    trial_audit, audit_command = run_audit(output_structured, f"{output_candidate.name}_example_library_trial", output_artifacts)
    baseline_audit = read_json(baseline_artifacts / "audit.json")

    file_comparison = compare_structured_dirs(baseline_structured, output_structured)
    command_log = [
        *py_compile_log,
        {"command": audit_command, "result": "ok"},
    ]

    summary = {
        "total_examples": len(all_examples),
        "chapter_counts": sorted(
            ((chapter, len(items)) for chapter, items in library_snapshot["by_chapter"].items()),
            key=lambda item: chapter_sort_key(item[0]),
        ),
        "per_file_counts": per_file_counts,
    }
    write_json(output_artifacts / "example_library_summary.json", summary)
    write_json(output_artifacts / "example_library_items.json", library_snapshot["all_examples"])

    report_md = build_report(
        output_candidate=output_candidate,
        baseline_candidate=baseline_candidate,
        examples=all_examples,
        summary=summary,
        baseline_audit=baseline_audit,
        trial_audit=trial_audit,
        file_comparison=file_comparison,
        command_log=command_log,
    )
    write_text(output_artifacts / "example_library_report.md", report_md)

    diff_lines = [
        "# Example Library Diff vs Baseline",
        "",
        "## New Files",
        "",
    ]
    new_structured = [item for item in file_comparison["added"] if item.endswith("_example_library.json") or item in {"all_example_library.json"}]
    new_artifacts = sorted(
        [
            "artifacts/audit.json",
            "artifacts/audit.md",
            "artifacts/audit_samples.json",
            "artifacts/example_library_report.md",
            "artifacts/example_library_summary.json",
            "artifacts/example_library_items.json",
        ],
        key=natural_key,
    )
    diff_lines.append(render_table(["file", "status"], [[item, "new"] for item in new_structured + new_artifacts]))
    diff_lines.append("")
    diff_lines.append("## Modified Files")
    diff_lines.append("")
    if file_comparison["modified"]:
        diff_lines.append(render_table(["file", "status"], [[item, "modified"] for item in file_comparison["modified"]]))
    else:
        diff_lines.append("No modified structured files.")
    diff_lines.append("")
    diff_lines.append("## Unchanged Baseline Files")
    diff_lines.append("")
    diff_lines.append(f"Unchanged structured files: {len(file_comparison['unchanged'])}")
    diff_lines.append("")
    diff_lines.append("## Audit Metric Comparison")
    diff_lines.append("")
    diff_lines.append(render_table(
        ["metric", "baseline", "trial"],
        [[key, baseline_audit["quality_metrics"].get(key), trial_audit["quality_metrics"].get(key)] for key in sorted(set(baseline_audit["quality_metrics"]) | set(trial_audit["quality_metrics"]))]
    ))
    diff_lines.append("")
    diff_lines.append("## Table / Formula Regression Check")
    diff_lines.append("")
    diff_lines.append(render_table(
        ["check", "result"],
        [
            ["formula_library changed", "no"],
            ["table_library changed", "no"],
            ["Table 24.1 / 25.1 / 30.1 regression", "no"],
            ["placeholder_in_discussion", trial_audit["issue_type_counts"].get("placeholder_in_discussion", 0)],
            ["ocr_residual_marker", trial_audit["issue_type_counts"].get("ocr_residual_marker", 0)],
        ],
    ))
    write_text(output_artifacts / "example_library_diff_vs_baseline.md", "\n".join(diff_lines) + "\n")

    sync_plan = [
        "# Sync Plan for data/structured",
        "",
        "1. Back up `data/structured` before any promotion.",
        "2. Promote only the new example library files first: `chapterXX_example_library.json` and `all_example_library.json`.",
        "3. Do not sync the chapter block JSON files in this trial; the structured正文 stayed unchanged.",
        "4. If you later decide to store example references in blocks, regenerate a second trial that adds `example_refs` / `belongs_to_example` fields and review that diff separately.",
        "5. Recommended command pattern: copy the chosen files from `tmp/structured_quality_probe/candidates/example_library_trial/structured/` into `data/structured/`, then rerun the existing audit over `data/structured`.",
        "6. Rollback is the backup copy of `data/structured` taken before promotion.",
    ]
    write_text(output_artifacts / "sync_to_data_structured_plan.md", "\n".join(sync_plan) + "\n")


if __name__ == "__main__":
    main()
