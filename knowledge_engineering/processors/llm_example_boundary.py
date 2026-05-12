"""LLM-assisted example-boundary trial utilities.

The LLM is only a boundary judge here.  It receives raw OCR rows and existing
structured evidence, then returns row indexes.  All content assembly and writes
are guarded by deterministic code.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import time
import threading
from typing import Any

from knowledge_engineering.core.common import read_json, table_reference_key, utc_now_iso, write_json
from knowledge_engineering.core.runtime import LLMClient
from knowledge_engineering.pipeline.example_pipeline import (
    candidate_key,
    example_to_library_row,
    make_example_ref,
    replace_examples_in_file,
)
from knowledge_engineering.processors.example_extraction import (
    PADDLE_EXAMPLE_LABELS,
    PADDLE_PAGE_NOISE_LABELS,
    ExampleCandidate,
    RawRecord,
    build_structured_context,
    chapter_sort_key,
    clean_ref_id,
    collapse_ws,
    dedupe_preserve_order,
    extract_external_refs,
    extract_figure_refs,
    extract_formula_refs,
    extract_table_refs,
    is_publication_footer,
    join_hyphenated,
    load_unit_files,
    looks_like_post_example_body,
    looks_like_example_start,
    looks_truncated,
    natural_key,
    next_placeholder_source,
    normalize_heading_prefix,
    normalize_match_text,
    ordered_paddle_records,
    raw_example_start_match,
    raw_table_has_numbered_caption,
    raw_table_placeholder_for_source,
    strip_html,
    strip_structured_refs,
)


DEFAULT_OUTPUT = Path("tmp/structured_quality_probe/candidates/llm_example_boundary_ch6/structured")
DEFAULT_ARTIFACTS = Path("tmp/structured_quality_probe/candidates/llm_example_boundary_ch6/artifacts")
AUTO_CONFIDENCE_THRESHOLD = 0.90
REVIEW_CONFIDENCE_THRESHOLD = 0.70
BOUNDARY_SCHEMA = "llm_example_boundary.v1"
EXAMPLE_PLACEHOLDER_RE = re.compile(r"\[\[SEE_EXAMPLE:[^\]\n\r]+?\]\]", re.IGNORECASE)
EXAMPLE_PLACEHOLDER_REF_RE = re.compile(r"\[\[SEE_EXAMPLE:([^\]\n\r]+?)\]\]", re.IGNORECASE)


@dataclass
class BoundaryWindow:
    window_id: str
    chapter: str
    expected_example_id: str
    start_raw_index: int
    end_raw_index: int
    rows: list[dict[str, Any]]
    existing_example: dict[str, Any] | None
    structured_context: list[dict[str, Any]]
    source_file_hint: str
    source_block_hint: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": BOUNDARY_SCHEMA,
            "window_id": self.window_id,
            "chapter": self.chapter,
            "expected_example_id": self.expected_example_id,
            "start_raw_index": self.start_raw_index,
            "end_raw_index": self.end_raw_index,
            "rows": self.rows,
            "existing_example": self.existing_example,
            "structured_context": self.structured_context,
            "source_file_hint": self.source_file_hint,
            "source_block_hint": self.source_block_hint,
        }


def parse_chapter_list(raw: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if raw is None:
        return ["chapter6"]
    if isinstance(raw, (list, tuple)):
        parts = [str(item) for item in raw]
    else:
        parts = re.split(r"[,;\s]+", str(raw))
    chapters = []
    for item in parts:
        value = item.strip().lower()
        if not value:
            continue
        if value.isdigit():
            value = f"chapter{int(value)}"
        chapters.append(value)
    return chapters or ["chapter6"]


def _load_existing_rows(structured_dir: Path) -> list[dict[str, Any]]:
    path = structured_dir / "example_library.json"
    if not path.exists():
        return []
    payload = read_json(path)
    rows = payload.get("examples") if isinstance(payload, dict) else None
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _existing_by_id(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    by_id: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = clean_ref_id(str(row.get("example_id") or ""))
        if not chapter or not example_id:
            continue
        current = by_id.get((chapter, example_id))
        if current is None or len(str(row.get("content_markdown") or "")) > len(str(current.get("content_markdown") or "")):
            by_id[(chapter, example_id)] = row
    return by_id


def _row_to_payload(
    index: int,
    record: RawRecord,
    *,
    records: list[RawRecord],
    chapter: str,
    context: Any,
    source_file_hint: str,
) -> dict[str, Any]:
    match = raw_example_start_match(record.content) if record.label in PADDLE_EXAMPLE_LABELS else None
    payload = {
        "raw_row_index": index,
        "page_index": record.page_index,
        "page_number": record.page_index + 1,
        "page_row_index": record.row_index,
        "label": record.label,
        "bbox": record.bbox,
        "content": record.content,
        "is_example_start": bool(match),
        "example_id": clean_ref_id(match.group("example_id")) if match else "",
    }
    if record.label == "table" and "<table" in record.content.lower() and not raw_table_has_numbered_caption(record, records):
        payload["table_placeholder"] = raw_table_placeholder_for_source(
            record,
            records,
            chapter=chapter,
            source_file=source_file_hint,
            context=context,
            used_table_refs=set(),
        )
    return payload


def _formula_ids_for_chapter(structured_dir: Path, chapter: str) -> set[str]:
    path = structured_dir / "formula_library.json"
    if not path.exists():
        return set()
    payload = read_json(path)
    rows = payload.get("formulas") if isinstance(payload, dict) else None
    ids: set[str] = set()
    if not isinstance(rows, list):
        return ids
    for row in rows:
        if not isinstance(row, dict):
            continue
        source = row.get("source") if isinstance(row.get("source"), dict) else {}
        if str(source.get("chapter") or "").strip().lower() == chapter:
            ids.add(clean_ref_id(str(row.get("id") or "")))
    return {item for item in ids if item}


def _example_raw_span(records: list[RawRecord], start_index: int, *, max_rows: int = 42) -> tuple[int, int]:
    match = raw_example_start_match(records[start_index].content)
    example_id = clean_ref_id(match.group("example_id")) if match else ""
    seen_body_rows = 0
    end_index = min(len(records) - 1, start_index + max_rows - 1)
    for cursor in range(start_index + 1, min(len(records), start_index + max_rows)):
        record = records[cursor]
        if looks_like_example_start(record.content):
            return start_index, cursor - 1
        if record.label == "paragraph_title":
            return start_index, cursor - 1
        if (
            example_id
            and seen_body_rows >= 1
            and _looks_like_post_example_body_row(record, example_id)
        ):
            return start_index, cursor - 1
        if record.label not in PADDLE_PAGE_NOISE_LABELS and not is_publication_footer(record.content):
            seen_body_rows += 1
    return start_index, end_index


def _raw_span_text(records: list[RawRecord], start_index: int, end_index: int) -> str:
    parts = [
        record.content
        for record in records[start_index : end_index + 1]
        if record.label not in PADDLE_PAGE_NOISE_LABELS and not is_publication_footer(record.content)
    ]
    return collapse_ws(" ".join(parts))


def _looks_like_post_example_body_row(record: RawRecord | dict[str, Any], example_id: str) -> bool:
    return looks_like_post_example_body(record, example_id)


def _raw_span_without_page_noise(records: list[RawRecord], start_index: int, end_index: int) -> list[RawRecord]:
    return [
        record
        for record in records[start_index : end_index + 1]
        if record.label not in PADDLE_PAGE_NOISE_LABELS and not is_publication_footer(record.content)
    ]


def _raw_span_before_post_example_body(
    records: list[RawRecord],
    start_index: int,
    end_index: int,
    example_id: str,
) -> int | None:
    content_seen = 0
    for index in range(start_index + 1, end_index + 1):
        record = records[index]
        if record.label in PADDLE_PAGE_NOISE_LABELS or is_publication_footer(record.content):
            continue
        if record.label in {"paragraph_title"} or looks_like_example_start(record.content):
            break
        if _looks_like_post_example_body_row(record, example_id) and content_seen >= 1:
            return index - 1
        if record.label in PADDLE_EXAMPLE_LABELS or record.label in {"table", "display_formula", "formula_number"}:
            content_seen += 1
    return None


def _existing_contains_post_example_body(existing_row: dict[str, Any] | None, example_id: str) -> bool:
    if not existing_row:
        return False
    content = str(existing_row.get("content_markdown") or existing_row.get("content_plain") or "")
    if not content:
        return False
    for part in re.split(r"(?:\n\s*\n|(?<=\.)\s+(?=[A-Z]))", content):
        pseudo = {"label": "text", "content": part}
        if _looks_like_post_example_body_row(pseudo, example_id):
            return True
    return False


def _is_suspicious_window(
    *,
    records: list[RawRecord],
    start_index: int,
    end_index: int,
    existing_row: dict[str, Any] | None,
) -> bool:
    if existing_row is None:
        return True
    replacement = existing_row.get("replacement") if isinstance(existing_row.get("replacement"), dict) else {}
    if replacement.get("status") == "restored":
        return False
    metadata = existing_row.get("metadata") if isinstance(existing_row.get("metadata"), dict) else {}
    if metadata.get("needs_review"):
        return True
    match = raw_example_start_match(records[start_index].content)
    example_id = clean_ref_id(match.group("example_id")) if match else clean_ref_id(str(existing_row.get("example_id") or ""))
    if _raw_span_before_post_example_body(records, start_index, end_index, example_id) is not None:
        return True
    if _existing_contains_post_example_body(existing_row, example_id):
        return True
    raw_words = len(normalize_match_text(_raw_span_text(records, start_index, end_index)).split())
    existing_words = len(normalize_match_text(str(existing_row.get("content_plain") or existing_row.get("content_markdown") or "")).split())
    return raw_words >= 40 and existing_words < int(raw_words * 0.78)


def _structured_context_for_window(
    context: Any,
    chapter: str,
    records: list[RawRecord],
    start_index: int,
    end_index: int,
    *,
    max_blocks: int = 12,
) -> list[dict[str, Any]]:
    anchors: list[str] = []
    for record in records[start_index : end_index + 1]:
        if record.label in PADDLE_PAGE_NOISE_LABELS or record.label in {"table", "display_formula", "formula_number"}:
            continue
        tokens = normalize_match_text(record.content).split()
        if len(tokens) >= 8:
            anchors.append(" ".join(tokens[:8]))
    matches: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for path, block_index, content in context.block_locations.get(chapter, []):
        normalized = normalize_match_text(content)
        if not normalized:
            continue
        if not any(anchor and anchor in normalized for anchor in anchors):
            continue
        key = (path.name, block_index)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            {
                "source_file": path.name,
                "block_index": block_index,
                "content": str(content)[:1200],
            }
        )
        if len(matches) >= max_blocks:
            break
    return matches


def collect_example_boundary_windows(
    structured_dir: Path,
    *,
    project_root: Path,
    chapters: list[str] | tuple[str, ...] | str | None = None,
    max_windows: int = 20,
    suspicious_only: bool = True,
) -> list[dict[str, Any]]:
    structured_dir = Path(structured_dir)
    project_root = Path(project_root)
    existing_rows = _load_existing_rows(structured_dir)
    existing_by_id = _existing_by_id(existing_rows)
    context = build_structured_context(structured_dir)
    windows: list[BoundaryWindow] = []

    for chapter in parse_chapter_list(chapters):
        records = ordered_paddle_records(project_root, chapter)
        if not records:
            continue
        for start_index, record in enumerate(records):
            if record.label not in PADDLE_EXAMPLE_LABELS:
                continue
            match = raw_example_start_match(record.content)
            if not match:
                continue
            example_id = clean_ref_id(match.group("example_id"))
            if not example_id:
                continue
            start_raw, end_raw = _example_raw_span(records, start_index)
            existing_row = existing_by_id.get((chapter, example_id))
            if suspicious_only and not _is_suspicious_window(
                records=records,
                start_index=start_raw,
                end_index=end_raw,
                existing_row=existing_row,
            ):
                continue
            source_file, source_block_index = next_placeholder_source(chapter, example_id, context)
            if existing_row is not None:
                source_file = str(existing_row.get("source_file") or source_file)
                try:
                    source_block_index = int(existing_row.get("start_block_index"))
                except (TypeError, ValueError):
                    pass
            rows = [
                _row_to_payload(
                    index,
                    records[index],
                    records=records,
                    chapter=chapter,
                    context=context,
                    source_file_hint=source_file,
                )
                for index in range(start_raw, end_raw + 1)
            ]
            window = BoundaryWindow(
                window_id=f"{chapter}:{example_id}:{start_raw}-{end_raw}",
                chapter=chapter,
                expected_example_id=example_id,
                start_raw_index=start_raw,
                end_raw_index=end_raw,
                rows=rows,
                existing_example=existing_row,
                structured_context=_structured_context_for_window(
                    context,
                    chapter,
                    records,
                    start_raw,
                    end_raw,
                ),
                source_file_hint=source_file,
                source_block_hint=source_block_index,
            )
            windows.append(window)
            if max_windows and len(windows) >= max_windows:
                return [window.to_dict() for window in windows]
    return [window.to_dict() for window in windows]


def _json_from_llm_response(content: str) -> dict[str, Any]:
    value = str(content or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value)
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response is not a JSON object")
    return parsed


def review_example_window_with_llm(window: dict[str, Any], client: Any) -> dict[str, Any]:
    prompt_payload = {
        "task": "Judge the exact raw OCR row boundary for one textbook Example.",
        "constraints": {
            "return_strict_json_only": True,
            "do_not_rewrite_content": True,
            "choose_only_raw_row_index_values_from_input_rows": True,
            "do_not_include_next_example_or_section_title": True,
            "tables_must_be_raw_rows_with_label_table": True,
            "formulas_must_be_raw_rows_with_label_display_formula_or_formula_number": True,
            "inline_mentions_like_Example_6_1_used_are_body_text_not_example_headings": True,
            "paragraphs_starting_As_Example_X_illustrates_are_after_example_body_when_X_is_this_example": True,
            "author_year_literature_paragraphs_after_a_complete_example_are_body_text_not_example_body": True,
        },
        "output_schema": {
            "example_id": "6.2",
            "start_row_index": 86,
            "end_row_index": 96,
            "include_table_rows": [87],
            "include_formula_rows": [89, 91, 93, 95],
            "is_complete": True,
            "confidence": 0.93,
            "reason": "brief boundary evidence",
            "apply_mode": "auto|review|reject",
        },
        "window": window,
    }
    messages = [
        {
            "role": "system",
            "content": (
                "Return strict JSON only. You are a boundary judge, not an editor. "
                "Use only raw_row_index values present in the input rows. "
                "Never include the next section title or the next Example."
            ),
        },
        {"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=False, indent=2)},
    ]
    content = client._post_chat_completion(messages=messages, json_mode=True)
    decision = _json_from_llm_response(content)
    decision["window_id"] = window.get("window_id")
    return decision


def _raw_row_map(window: dict[str, Any]) -> dict[int, dict[str, Any]]:
    rows = window.get("rows") if isinstance(window.get("rows"), list) else []
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            out[int(row.get("raw_row_index"))] = row
        except (TypeError, ValueError):
            continue
    return out


def _looks_like_included_section_title(row: dict[str, Any], *, is_start: bool) -> bool:
    if is_start:
        return False
    label = str(row.get("label") or "").strip().lower()
    content = collapse_ws(str(row.get("content") or ""))
    if label == "paragraph_title":
        return True
    if label == "footer" and content and len(content) < 140 and not content.endswith((".", ",", ";", ":")):
        return True
    return False


def validate_llm_example_decision(
    window: dict[str, Any],
    decision: dict[str, Any],
    *,
    auto_threshold: float = AUTO_CONFIDENCE_THRESHOLD,
    review_threshold: float = REVIEW_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    errors: list[str] = []
    rows_by_index = _raw_row_map(window)
    expected_id = clean_ref_id(str(window.get("expected_example_id") or ""))
    example_id = clean_ref_id(str(decision.get("example_id") or ""))
    if example_id != expected_id:
        errors.append(f"example_id_mismatch:{example_id}!={expected_id}")
    try:
        start = int(decision.get("start_row_index"))
        end = int(decision.get("end_row_index"))
    except (TypeError, ValueError):
        start = end = -1
        errors.append("start_or_end_row_not_integer")
    if start not in rows_by_index or end not in rows_by_index:
        errors.append("boundary_row_outside_window")
    if start > end:
        errors.append("start_after_end")
    start_row = rows_by_index.get(start)
    if start_row is not None:
        match = raw_example_start_match(str(start_row.get("content") or ""))
        if not match or clean_ref_id(match.group("example_id")) != expected_id:
            errors.append("start_row_is_not_expected_example_heading")

    included = [rows_by_index[index] for index in range(start, end + 1) if index in rows_by_index]
    for row in included[1:]:
        if looks_like_example_start(str(row.get("content") or "")):
            errors.append("includes_next_example_heading")
        if _looks_like_included_section_title(row, is_start=False):
            errors.append("includes_next_section_title")
        if _looks_like_post_example_body_row(row, expected_id):
            errors.append("includes_post_example_body")

    next_row = rows_by_index.get(end + 1)
    if isinstance(next_row, dict) and _looks_like_post_example_body_row(next_row, expected_id):
        decision["boundary_stop_reason"] = "post_example_body"

    table_rows = _coerce_int_list(decision.get("include_table_rows"))
    formula_rows = _coerce_int_list(decision.get("include_formula_rows"))
    for row_index in table_rows:
        row = rows_by_index.get(row_index)
        if row is None or not (start <= row_index <= end):
            errors.append(f"table_row_outside_boundary:{row_index}")
        elif str(row.get("label") or "").lower() != "table":
            errors.append(f"table_row_not_table:{row_index}")
    for row_index in formula_rows:
        row = rows_by_index.get(row_index)
        label = str(row.get("label") or "").lower() if row else ""
        if row is None or not (start <= row_index <= end):
            errors.append(f"formula_row_outside_boundary:{row_index}")
        elif label not in {"display_formula", "formula_number"}:
            errors.append(f"formula_row_not_formula:{row_index}")

    try:
        confidence = float(decision.get("confidence"))
    except (TypeError, ValueError):
        confidence = 0.0
        errors.append("confidence_not_number")
    apply_mode = str(decision.get("apply_mode") or "").strip().lower()
    if apply_mode not in {"auto", "review", "reject"}:
        errors.append("invalid_apply_mode")
        apply_mode = "review"
    if not bool(decision.get("is_complete")):
        errors.append("decision_not_complete")

    if errors:
        status = "rejected"
    elif apply_mode == "auto" and confidence >= auto_threshold:
        status = "auto"
    elif confidence >= review_threshold and apply_mode in {"auto", "review"}:
        status = "review"
    else:
        status = "rejected"
    return {
        "window_id": window.get("window_id"),
        "example_id": expected_id,
        "status": status,
        "errors": dedupe_preserve_order(errors),
        "confidence": confidence,
        "apply_mode": apply_mode,
    }


def _coerce_int_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    out: list[int] = []
    for item in value:
        try:
            out.append(int(item))
        except (TypeError, ValueError):
            continue
    return out


def _number_from_formula_row(content: str) -> str:
    match = re.search(r"\((?P<label>(?:A\d+|\d+)\.\d+(?:\.\d+)?[A-Za-z]?)\)", str(content or ""))
    return clean_ref_id(match.group("label")) if match else ""


def _assemble_raw_content_parts(
    *,
    window: dict[str, Any],
    decision: dict[str, Any],
    structured_dir: Path,
) -> tuple[list[str], list[int], list[int]]:
    rows_by_index = _raw_row_map(window)
    start = int(decision.get("start_row_index"))
    end = int(decision.get("end_row_index"))
    chapter = str(window.get("chapter") or "").strip().lower()
    formula_ids = _formula_ids_for_chapter(structured_dir, chapter)
    used_table_refs: set[str] = set()
    table_rows_used: list[int] = []
    formula_rows_used: list[int] = []
    parts: list[str] = []

    def append_text_part(value: str) -> None:
        text = str(value or "").strip()
        if not text:
            return
        if parts and not parts[-1].startswith("[["):
            joined = join_hyphenated(parts[-1], text)
            if joined != f"{parts[-1]} {text}":
                parts[-1] = joined
                return
        parts.append(text)

    cursor = start
    while cursor <= end:
        row = rows_by_index.get(cursor)
        if row is None:
            cursor += 1
            continue
        label = str(row.get("label") or "").strip().lower()
        content = str(row.get("content") or "").strip()
        if label in PADDLE_PAGE_NOISE_LABELS or is_publication_footer(content):
            cursor += 1
            continue
        if label == "table":
            placeholder = str(row.get("table_placeholder") or "").strip()
            if placeholder:
                parts.append(placeholder)
                used_table_refs.add(placeholder)
                table_rows_used.append(cursor)
            cursor += 1
            continue
        if label == "display_formula":
            next_row = rows_by_index.get(cursor + 1)
            next_label = str(next_row.get("label") or "").lower() if isinstance(next_row, dict) else ""
            formula_id = _number_from_formula_row(str(next_row.get("content") or "")) if next_label == "formula_number" else ""
            if formula_id and formula_id in formula_ids:
                parts.append(f"[[SEE_FORMULA:{formula_id}]]")
                formula_rows_used.extend([cursor, cursor + 1])
                cursor += 2
                continue
            append_text_part(content)
            formula_rows_used.append(cursor)
            cursor += 1
            continue
        if label == "formula_number":
            cursor += 1
            continue
        if content:
            append_text_part(content)
        cursor += 1
    return parts, table_rows_used, formula_rows_used


def build_example_candidate_from_decision(
    window: dict[str, Any],
    decision: dict[str, Any],
    *,
    structured_dir: Path,
) -> ExampleCandidate:
    parts, table_rows_used, formula_rows_used = _assemble_raw_content_parts(
        window=window,
        decision=decision,
        structured_dir=structured_dir,
    )
    content_markdown = normalize_heading_prefix(collapse_ws(" ".join(part for part in parts if part.strip())))
    content_plain = collapse_ws(strip_structured_refs(strip_html(content_markdown)))
    example_id = clean_ref_id(str(decision.get("example_id") or window.get("expected_example_id") or ""))
    chapter = str(window.get("chapter") or "").strip().lower()
    source_file, start_block, end_block = _find_structured_span_for_decision(structured_dir, window, decision)
    title = collapse_ws(
        re.sub(
            r"^\s*Example\s+(?:A\d+|\d+)\.\d+[a-z]?\.\s*",
            "",
            content_markdown,
            count=1,
            flags=re.IGNORECASE,
        )
    )[:160].strip()
    formula_refs = extract_formula_refs(content_markdown)
    table_refs = extract_table_refs(content_markdown)
    figure_refs = extract_figure_refs(content_markdown)
    external_refs = extract_external_refs(content_markdown)
    try:
        confidence = float(decision.get("confidence"))
    except (TypeError, ValueError):
        confidence = 0.0
    return ExampleCandidate(
        example_id=example_id,
        chapter=chapter,
        label=f"Example {example_id}",
        title=title,
        source_file=source_file,
        start_block_index=start_block,
        end_block_index=end_block,
        block_ids=[],
        content_markdown=content_markdown,
        content_plain=content_plain,
        formula_refs=formula_refs,
        table_refs=table_refs,
        figure_refs=figure_refs,
        external_refs=external_refs,
        evidence={
            "source": "paddle_raw_rows+llm_boundary_judge",
            "detection_method": "llm_example_boundary_review",
            "confidence": confidence,
            "window_id": window.get("window_id"),
            "start_raw_row_index": int(decision.get("start_row_index")),
            "end_raw_row_index": int(decision.get("end_row_index")),
            "table_raw_rows": table_rows_used,
            "formula_raw_rows": formula_rows_used,
            "llm_reason": str(decision.get("reason") or ""),
        },
        metadata={
            "has_formula": bool(formula_refs),
            "has_table": bool(table_refs),
            "has_figure": bool(figure_refs),
            "word_count": len(content_plain.split()) if content_plain else 0,
            "needs_review": looks_truncated(content_markdown),
            "llm_example_boundary_trial": True,
        },
        _order_key=(chapter_sort_key(chapter), natural_key(source_file), start_block, natural_key(example_id)),
    )


def _find_structured_span_for_decision(
    structured_dir: Path,
    window: dict[str, Any],
    decision: dict[str, Any],
) -> tuple[str, int, int]:
    chapter = str(window.get("chapter") or "").strip().lower()
    example_id = clean_ref_id(str(window.get("expected_example_id") or ""))
    context = build_structured_context(structured_dir)
    direct = context.placeholder_locations.get((chapter, example_id))
    if direct:
        return direct[0], direct[1], direct[1]

    rows_by_index = _raw_row_map(window)
    start = int(decision.get("start_row_index"))
    end = int(decision.get("end_row_index"))
    anchors: list[str] = []
    for row_index in range(start + 1, end + 1):
        row = rows_by_index.get(row_index)
        if row is None:
            continue
        label = str(row.get("label") or "").lower()
        if label in PADDLE_PAGE_NOISE_LABELS or label in {"table", "display_formula", "formula_number"}:
            continue
        tokens = normalize_match_text(str(row.get("content") or "")).split()
        if len(tokens) >= 8:
            anchors.append(" ".join(tokens[:8]))
    found: list[tuple[Path, int]] = []
    for anchor in anchors:
        for path, block_index, content in context.block_locations.get(chapter, []):
            if anchor and anchor in normalize_match_text(content):
                if not found or found[-1] != (path, block_index):
                    found.append((path, block_index))
                break
    if found:
        source_file = found[0][0].name
        same_file_indexes = [block_index for path, block_index in found if path.name == source_file]
        return source_file, min(same_file_indexes), max(same_file_indexes)
    return (
        str(window.get("source_file_hint") or f"{chapter}_001.json"),
        int(window.get("source_block_hint") or 0),
        int(window.get("source_block_hint") or 0),
    )


def _row_quality(row: dict[str, Any] | None) -> tuple[int, int]:
    if not isinstance(row, dict):
        return (0, 0)
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    plain = str(row.get("content_plain") or row.get("content_markdown") or "")
    return (0 if metadata.get("needs_review") else 1, len(normalize_match_text(plain).split()))


def _candidate_removes_boundary_contamination(candidate: ExampleCandidate, existing: dict[str, Any] | None) -> bool:
    if not existing:
        return False
    if not _existing_contains_post_example_body(existing, candidate.example_id):
        return False
    if _existing_contains_post_example_body(
        {
            "content_markdown": candidate.content_markdown,
            "content_plain": candidate.content_plain,
        },
        candidate.example_id,
    ):
        return False
    existing_words = len(normalize_match_text(str(existing.get("content_plain") or existing.get("content_markdown") or "")).split())
    new_words = len(normalize_match_text(candidate.content_plain).split())
    return new_words >= 20 and new_words < existing_words


def _candidate_improves_existing(candidate: ExampleCandidate, existing: dict[str, Any] | None) -> bool:
    if not existing:
        return True
    if _candidate_removes_boundary_contamination(candidate, existing):
        return True
    old_ok, old_words = _row_quality(existing)
    new_ok = 0 if candidate.metadata.get("needs_review") else 1
    new_words = len(normalize_match_text(candidate.content_plain).split())
    if new_ok > old_ok:
        return True
    return new_words >= max(old_words + 20, int(old_words * 1.18))


def _row_from_candidate(candidate: ExampleCandidate, *, example_ref: str, status: str) -> dict[str, Any]:
    row = example_to_library_row(
        candidate,
        example_ref=example_ref,
        replacement_status=status,
        replacement_reason="llm_example_boundary_candidate",
    )
    return row


def apply_llm_decisions_to_candidate(
    *,
    source_structured_dir: Path,
    output_structured_dir: Path,
    windows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output_structured_dir = Path(output_structured_dir)
    existing_rows = _load_existing_rows(output_structured_dir)
    existing_by_id = _existing_by_id(existing_rows)
    validation_by_window = {str(item.get("window_id")): item for item in validations}
    window_by_id = {str(item.get("window_id")): item for item in windows}
    auto_applied: list[dict[str, Any]] = []
    review_queue: list[dict[str, Any]] = []
    candidates: list[ExampleCandidate] = []

    for decision in decisions:
        window_id = str(decision.get("window_id") or "")
        window = window_by_id.get(window_id)
        validation = validation_by_window.get(window_id)
        if window is None or validation is None:
            continue
        if validation.get("status") != "auto":
            review_queue.append({"window_id": window_id, "decision": decision, "validation": validation})
            continue
        candidate = build_example_candidate_from_decision(window, decision, structured_dir=source_structured_dir)
        existing = existing_by_id.get((candidate.chapter, candidate.example_id))
        if not _candidate_improves_existing(candidate, existing):
            review_queue.append(
                {
                    "window_id": window_id,
                    "decision": decision,
                    "validation": {**validation, "status": "review", "errors": ["candidate_not_clear_improvement"]},
                }
            )
            continue
        candidates.append(candidate)

    if not candidates:
        return auto_applied, review_queue

    rows_by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for row in existing_rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = clean_ref_id(str(row.get("example_id") or ""))
        if chapter and example_id:
            rows_by_identity[(chapter, example_id)] = row
    id_counts = Counter(candidate.example_id for candidate in candidates)
    example_refs: dict[str, str] = {}
    for candidate in candidates:
        existing = rows_by_identity.get((candidate.chapter, candidate.example_id))
        example_ref = str(existing.get("example_ref") or candidate.example_id) if existing else make_example_ref(candidate, id_counts)
        example_refs[candidate_key(candidate)] = example_ref
        row = _row_from_candidate(candidate, example_ref=example_ref, status="replaced")
        rows_by_identity[(candidate.chapter, candidate.example_id)] = row
        auto_applied.append(
            {
                "example_id": candidate.example_id,
                "example_ref": example_ref,
                "source_file": candidate.source_file,
                "start_block_index": candidate.start_block_index,
                "end_block_index": candidate.end_block_index,
                "word_count": candidate.metadata.get("word_count"),
                "table_refs": candidate.table_refs,
                "formula_refs": candidate.formula_refs,
            }
        )

    merged_rows = sorted(
        rows_by_identity.values(),
        key=lambda row: (
            chapter_sort_key(str(row.get("chapter") or "")),
            natural_key(str(row.get("source_file") or "")),
            int(row.get("start_block_index") or 0),
            natural_key(str(row.get("example_ref") or row.get("example_id") or "")),
        ),
    )
    write_json(
        output_structured_dir / "example_library.json",
        {"schema": "example_library.v1", "example_count": len(merged_rows), "examples": merged_rows},
    )
    _apply_candidate_placeholders(output_structured_dir, candidates, example_refs)
    _refresh_source_metadata(output_structured_dir, candidates)
    return auto_applied, review_queue


def _apply_candidate_placeholders(
    output_structured_dir: Path,
    candidates: list[ExampleCandidate],
    example_refs: dict[str, str],
) -> None:
    context = build_structured_context(output_structured_dir)
    by_file: dict[str, list[ExampleCandidate]] = {}
    for candidate in candidates:
        if context.placeholder_locations.get((candidate.chapter, candidate.example_id)):
            continue
        if _merge_into_existing_placeholder_block(output_structured_dir, candidate, example_refs[candidate_key(candidate)]):
            continue
        by_file.setdefault(candidate.source_file, []).append(candidate)
    for source_file, file_candidates in by_file.items():
        path = output_structured_dir / source_file
        if path.exists():
            replace_examples_in_file(path, file_candidates, example_refs, dry_run=False)


def _merge_into_existing_placeholder_block(
    output_structured_dir: Path,
    candidate: ExampleCandidate,
    example_ref: str,
) -> bool:
    path = output_structured_dir / candidate.source_file
    if not path.exists() or candidate.start_block_index != candidate.end_block_index:
        return False
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list) or not (0 <= candidate.start_block_index < len(blocks)):
        return False
    block = blocks[candidate.start_block_index]
    if not isinstance(block, dict):
        return False
    content = str(block.get("content") or "")
    existing_placeholders = EXAMPLE_PLACEHOLDER_RE.findall(content)
    if not existing_placeholders:
        return False
    remainder = EXAMPLE_PLACEHOLDER_RE.sub("", content).strip()
    if remainder:
        return False
    merged = []
    for placeholder in [*existing_placeholders, f"[[SEE_EXAMPLE:{example_ref}]]"]:
        if placeholder not in merged:
            merged.append(placeholder)
    merged.sort(key=_placeholder_sort_key)
    block["type"] = "example"
    block["content"] = " ".join(merged)
    write_json(path, data)
    return True


def _placeholder_sort_key(placeholder: str) -> list[Any]:
    match = EXAMPLE_PLACEHOLDER_REF_RE.fullmatch(str(placeholder or "").strip())
    if not match:
        return natural_key(str(placeholder or ""))
    ref = match.group(1).split("@", 1)[0]
    return natural_key(ref)


def _refresh_source_metadata(output_structured_dir: Path, candidates: list[ExampleCandidate]) -> None:
    for candidate in candidates:
        path = output_structured_dir / candidate.source_file
        if not path.exists():
            continue
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        data["metadata"] = metadata
        metadata["formula_references"] = dedupe_preserve_order(
            [str(item) for item in metadata.get("formula_references", []) if item] + candidate.formula_refs
        )
        metadata["table_references"] = dedupe_preserve_order(
            [str(item) for item in metadata.get("table_references", []) if item] + candidate.table_refs
        )
        metadata["table_reference_keys"] = dedupe_preserve_order(
            [str(item) for item in metadata.get("table_reference_keys", []) if item]
            + [table_reference_key(candidate.chapter, ref) for ref in candidate.table_refs]
        )
        write_json(path, data)
    _refresh_table_library_sources(output_structured_dir, candidates)


def _refresh_table_library_sources(output_structured_dir: Path, candidates: list[ExampleCandidate]) -> None:
    path = output_structured_dir / "table_library.json"
    if not path.exists():
        return
    payload = read_json(path)
    rows = payload.get("tables") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return
    changed = False
    for candidate in candidates:
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("id") or "") not in set(candidate.table_refs):
                continue
            source = row.get("source") if isinstance(row.get("source"), dict) else {}
            if str(source.get("chapter") or "").strip().lower() != candidate.chapter:
                continue
            row["source"] = {
                **source,
                "unit_id": Path(candidate.source_file).stem,
                "source_rebound_by": "llm_example_boundary_trial",
            }
            changed = True
    if changed:
        write_json(path, payload)


def run_llm_example_boundary_trial(
    *,
    structured_dir: Path,
    project_root: Path,
    output_structured_dir: Path = DEFAULT_OUTPUT,
    artifacts_dir: Path = DEFAULT_ARTIFACTS,
    chapters: list[str] | tuple[str, ...] | str | None = None,
    max_windows: int = 20,
    client: Any | None = None,
    suspicious_only: bool = True,
    resume: bool = True,
    workers: int = 1,
) -> dict[str, Any]:
    started = time.time()
    structured_dir = Path(structured_dir)
    project_root = Path(project_root)
    output_structured_dir = Path(output_structured_dir)
    artifacts_dir = Path(artifacts_dir)
    if structured_dir.resolve() == output_structured_dir.resolve():
        raise ValueError("output_structured_dir must not be the same as structured_dir")

    if output_structured_dir.exists() and not resume:
        shutil.rmtree(output_structured_dir)
    if not output_structured_dir.exists():
        shutil.copytree(structured_dir, output_structured_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    windows = collect_example_boundary_windows(
        structured_dir,
        project_root=project_root,
        chapters=chapters,
        max_windows=max_windows,
        suspicious_only=suspicious_only,
    )
    write_json(artifacts_dir / "windows.json", windows)
    progress_path = artifacts_dir / "progress.json"
    decisions_path = artifacts_dir / "decisions.json"
    validations_path = artifacts_dir / "validations.json"
    previous_decisions = _load_json_list(decisions_path) if resume else []
    previous_validations = _load_json_list(validations_path) if resume else []
    decisions_by_window = {
        str(item.get("window_id")): item
        for item in previous_decisions
        if isinstance(item, dict) and item.get("window_id")
    }
    validations_by_window = {
        str(item.get("window_id")): item
        for item in previous_validations
        if isinstance(item, dict) and item.get("window_id")
    }
    llm_client = client or LLMClient()
    artifact_lock = threading.Lock()

    def record_result(offset: int, window: dict[str, Any], decision: dict[str, Any], validation: dict[str, Any]) -> None:
        window_id = str(window.get("window_id") or "")
        with artifact_lock:
            decisions_by_window[window_id] = decision
            validations_by_window[window_id] = validation
            decisions = _ordered_artifacts_for_windows(windows, decisions_by_window)
            validations = _ordered_artifacts_for_windows(windows, validations_by_window)
            write_json(decisions_path, decisions)
            write_json(validations_path, validations)
            write_json(
                progress_path,
                {
                    "schema": BOUNDARY_SCHEMA,
                    "timestamp_utc": utc_now_iso(),
                    "processed": len(decisions_by_window),
                    "total_windows": len(windows),
                    "last_window_id": window_id,
                    "last_status": validation.get("status"),
                    "offset": offset,
                    "workers": max(1, int(workers or 1)),
                    "llm_metrics": llm_client.get_metrics() if hasattr(llm_client, "get_metrics") else {},
                },
            )

    pending_windows = [
        (offset, window)
        for offset, window in enumerate(windows, start=1)
        if not (
            str(window.get("window_id") or "") in decisions_by_window
            and str(window.get("window_id") or "") in validations_by_window
        )
    ]

    effective_workers = max(1, int(workers or 1))
    if effective_workers > 1 and len(pending_windows) > 1:
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            future_map = {
                executor.submit(_review_window_with_retries, window, llm_client, attempts=3): (offset, window)
                for offset, window in pending_windows
            }
            for future in as_completed(future_map):
                offset, window = future_map[future]
                decision = future.result()
                validation = validate_llm_example_decision(window, decision)
                record_result(offset, window, decision, validation)
    else:
        for offset, window in pending_windows:
            decision = _review_window_with_retries(window, llm_client, attempts=3)
            validation = validate_llm_example_decision(window, decision)
            record_result(offset, window, decision, validation)

    for offset, window in enumerate(windows, start=1):
        window_id = str(window.get("window_id") or "")
        if window_id in decisions_by_window and window_id in validations_by_window:
            continue

    decisions = _ordered_artifacts_for_windows(windows, decisions_by_window)
    validations = _ordered_artifacts_for_windows(windows, validations_by_window)

    auto_applied, extra_review = apply_llm_decisions_to_candidate(
        source_structured_dir=structured_dir,
        output_structured_dir=output_structured_dir,
        windows=windows,
        decisions=decisions,
        validations=validations,
    )
    review_queue = extra_review
    summary = {
        "schema": BOUNDARY_SCHEMA,
        "timestamp_utc": utc_now_iso(),
        "structured_dir": str(structured_dir),
        "output_structured_dir": str(output_structured_dir),
        "artifacts_dir": str(artifacts_dir),
        "chapters": parse_chapter_list(chapters),
        "windows": len(windows),
        "decisions": len(decisions),
        "auto_applied": len(auto_applied),
        "review_queue": len(review_queue),
        "elapsed_seconds": round(time.time() - started, 3),
        "workers": effective_workers,
        "llm_metrics": llm_client.get_metrics() if hasattr(llm_client, "get_metrics") else {},
    }
    write_json(artifacts_dir / "windows.json", windows)
    write_json(decisions_path, decisions)
    write_json(validations_path, validations)
    write_json(artifacts_dir / "auto_applied.json", auto_applied)
    write_json(artifacts_dir / "review_queue.json", review_queue)
    write_json(artifacts_dir / "summary.json", summary)
    return summary


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = read_json(path)
    except Exception:
        return []
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []


def _ordered_artifacts_for_windows(
    windows: list[dict[str, Any]],
    by_window: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    ordered: list[dict[str, Any]] = []
    for window in windows:
        item = by_window.get(str(window.get("window_id") or ""))
        if item is not None:
            ordered.append(item)
    return ordered


def _review_window_with_retries(window: dict[str, Any], client: Any, *, attempts: int) -> dict[str, Any]:
    errors: list[str] = []
    for attempt in range(max(1, attempts)):
        try:
            return review_example_window_with_llm(window, client)
        except Exception as exc:
            errors.append(str(exc))
            if attempt + 1 < attempts:
                time.sleep(2 * (attempt + 1))
    return {
        "window_id": window.get("window_id"),
        "example_id": window.get("expected_example_id"),
        "apply_mode": "reject",
        "confidence": 0,
        "is_complete": False,
        "reason": "llm_call_failed:" + " | ".join(errors[-3:]),
    }
