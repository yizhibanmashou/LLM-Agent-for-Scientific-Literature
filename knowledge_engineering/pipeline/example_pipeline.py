"""Formal example-library post-processing pipeline for structured outputs.

This module promotes the previously trial-only example placeholder workflow into
the knowledge-engineering pipeline while keeping the extraction rules unchanged.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import time
from typing import Any

from knowledge_engineering.core.common import (
    read_json,
    sort_table_ref_keys,
    sort_table_refs,
    table_reference_key,
    utc_now_iso,
    write_json,
)
from knowledge_engineering.processors.example_extraction import (
    PROJECT_ROOT,
    ExampleCandidate,
    EXAMPLE_HEAD_RE,
    EXAMPLE_PLACEHOLDER_RE,
    PADDLE_EXAMPLE_LABELS,
    PADDLE_PAGE_NOISE_LABELS,
    build_structured_context,
    chapter_sort_key,
    collapse_ws,
    existing_library_row_to_candidate,
    extract_external_refs,
    extract_examples_for_structured_dir,
    extract_figure_refs,
    extract_formula_refs,
    extract_table_refs,
    is_example_heading_match,
    is_standalone_numbered_table_placeholder,
    load_unit_files,
    looks_truncated,
    natural_key,
    normalize_heading_prefix,
    normalize_match_text,
    ordered_paddle_records,
    recover_examples_from_paddle_raw,
    raw_example_start_match,
    sha256_file,
    source_table_refs,
    strip_html,
    strip_structured_refs,
    looks_like_post_example_body,
    clean_ref_id,
)


TOKEN_RE = re.compile(r"[0-9A-Za-z]+")
TABLE_PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?TABLE\s*:\s*([^\]\n\r]+?)\s*\]\]", re.IGNORECASE)
INLINE_TABLE_ID_RE = re.compile(r"^inline_\d+$", re.IGNORECASE)
EXAMPLE_TITLE_PREFIX_RE = re.compile(r"^\s*Example\s+(?P<example_id>(?:A\d+|\d+)\.\d+[a-z]?)", re.IGNORECASE)


def _token_spans(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(0).lower(), match.start(), match.end()) for match in TOKEN_RE.finditer(str(text or ""))]


def _find_subsequence(haystack: list[str], needle: list[str]) -> int | None:
    if not needle or len(needle) > len(haystack):
        return None
    last_start = len(haystack) - len(needle)
    for index in range(last_start + 1):
        if haystack[index : index + len(needle)] == needle:
            return index
    return None


def _int_metadata(item: ExampleCandidate, key: str, default: int | None = None) -> int | None:
    metadata = item.metadata if isinstance(item.metadata, dict) else {}
    value = metadata.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _candidate_start_point(item: ExampleCandidate) -> tuple[int, int]:
    return item.start_block_index, _int_metadata(item, "replacement_start_char", 0) or 0


def _candidate_end_point(item: ExampleCandidate) -> tuple[int, int]:
    end_char = _int_metadata(item, "replacement_end_char")
    if end_char is None:
        return item.end_block_index + 1, 0
    return item.end_block_index, end_char


def _intervals_overlap(left: tuple[tuple[int, int], tuple[int, int]], right: tuple[tuple[int, int], tuple[int, int]]) -> bool:
    left_start, left_end = left
    right_start, right_end = right
    return left_start < right_end and right_start < left_end


def _replacement_interval(item: ExampleCandidate) -> tuple[tuple[int, int], tuple[int, int]]:
    return _candidate_start_point(item), _candidate_end_point(item)


def candidate_key(item: ExampleCandidate) -> str:
    return f"{item.source_file}#{item.start_block_index}-{item.end_block_index}#{item.example_id}"


def make_example_ref(item: ExampleCandidate, id_counts: Counter[str]) -> str:
    if id_counts[item.example_id] == 1:
        return item.example_id
    source_stem = Path(item.source_file).stem
    return f"{item.example_id}@{source_stem}_{item.start_block_index}"


def _coerce_block_span(value: Any) -> list[int] | None:
    if not (isinstance(value, list) and len(value) == 2):
        return None
    start = _safe_block_index(value[0])
    end = _safe_block_index(value[1])
    if start is None or end is None:
        return None
    if end < start:
        return None
    return [start, end]


def _candidate_source_block_span(item: ExampleCandidate) -> list[int]:
    metadata = item.metadata if isinstance(item.metadata, dict) else {}
    return _coerce_block_span(metadata.get("source_block_span")) or [item.start_block_index, item.end_block_index]


def example_to_library_row(
    item: ExampleCandidate,
    *,
    example_ref: str,
    replacement_status: str,
    replacement_reason: str,
) -> dict[str, Any]:
    row = item.to_dict()
    row["example_ref"] = example_ref
    row["placeholder"] = f"[[SEE_EXAMPLE:{example_ref}]]"
    row["replacement"] = {
        "status": replacement_status,
        "reason": replacement_reason,
        "source_block_span": _candidate_source_block_span(item),
    }
    return row


def select_non_overlapping_examples(examples: list[ExampleCandidate]) -> tuple[set[str], dict[str, str]]:
    selected_keys: set[str] = set()
    reasons: dict[str, str] = {}
    by_file: dict[str, list[ExampleCandidate]] = defaultdict(list)
    for item in examples:
        by_file[item.source_file].append(item)

    for file_examples in by_file.values():
        selected_intervals: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for item in sorted(
            file_examples,
            key=lambda ex: (
                ex.start_block_index,
                _int_metadata(ex, "replacement_start_char", 0) or 0,
                ex.end_block_index,
                natural_key(ex.example_id),
            ),
        ):
            key = candidate_key(item)
            interval = _replacement_interval(item)
            if any(_intervals_overlap(interval, selected) and interval != selected for selected in selected_intervals):
                reasons[key] = "overlaps_selected_example_span"
                continue
            selected_keys.add(key)
            if interval not in selected_intervals:
                selected_intervals.append(interval)
            reasons[key] = "selected"
    return selected_keys, reasons


def replace_examples_in_file(
    path: Path,
    examples: list[ExampleCandidate],
    example_refs: dict[str, str],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return {"file": path.name, "before_blocks": 0, "after_blocks": 0, "replaced": 0, "removed_blocks": 0}

    intervals: list[tuple[int, int, int, int, ExampleCandidate]] = []
    for item in examples:
        insert_only = bool(item.metadata.get("insert_placeholder_only")) if isinstance(item.metadata, dict) else False
        if insert_only:
            if item.start_block_index < 0 or item.start_block_index > len(blocks):
                continue
            start_block = item.start_block_index
            end_block = start_block
            if start_block < len(blocks) and isinstance(blocks[start_block], dict):
                content = blocks[start_block].get("content")
                start_length = len(content) if isinstance(content, str) else 0
            else:
                start_length = 0
            end_length = start_length
        else:
            if item.start_block_index < 0 or item.end_block_index < item.start_block_index or item.end_block_index >= len(blocks):
                continue
            start_block = item.start_block_index
            end_block = item.end_block_index
            start_content = blocks[start_block].get("content") if isinstance(blocks[start_block], dict) else ""
            end_content = blocks[end_block].get("content") if isinstance(blocks[end_block], dict) else ""
            start_length = len(start_content) if isinstance(start_content, str) else 0
            end_length = len(end_content) if isinstance(end_content, str) else 0
        start_char = _int_metadata(item, "replacement_start_char", 0) or 0
        end_char = _int_metadata(item, "replacement_end_char", end_length)
        if end_char is None:
            end_char = end_length
        start_char = max(0, min(start_char, start_length))
        end_char = max(0, min(end_char, end_length))
        if insert_only:
            end_char = start_char
        if start_block == end_block and end_char <= start_char and not insert_only:
            continue
        intervals.append((start_block, start_char, end_block, end_char, item))

    intervals.sort(key=lambda entry: (entry[0], entry[1], entry[2], entry[3], natural_key(entry[4].example_id)))
    new_blocks: list[Any] = []
    remapped_indexes: dict[str, int] = {}
    cursor_block = 0
    cursor_char = 0

    def append_content_slice(block_index: int, start_char: int, end_char: int) -> None:
        block = blocks[block_index]
        if not isinstance(block, dict):
            if start_char == 0:
                new_blocks.append(block)
            return
        content = block.get("content")
        if not isinstance(content, str):
            if start_char == 0:
                new_blocks.append(block)
            return
        sliced = content[start_char:end_char].strip()
        if not sliced:
            return
        new_block = dict(block)
        new_block["content"] = sliced
        new_blocks.append(new_block)

    def append_gap_until(target_block: int, target_char: int) -> None:
        nonlocal cursor_block, cursor_char
        while cursor_block < target_block and cursor_block < len(blocks):
            block = blocks[cursor_block]
            content = block.get("content") if isinstance(block, dict) else ""
            end_char = len(content) if isinstance(content, str) else 0
            if cursor_char == 0 and not isinstance(content, str):
                new_blocks.append(block)
            elif cursor_char == 0:
                if isinstance(content, str):
                    append_content_slice(cursor_block, cursor_char, end_char)
            else:
                append_content_slice(cursor_block, cursor_char, end_char)
            cursor_block += 1
            cursor_char = 0
        if cursor_block == target_block and cursor_block < len(blocks):
            append_content_slice(cursor_block, cursor_char, target_char)

    def append_preserved_numbered_table_blocks(start_block: int, end_block: int) -> None:
        for block_index in range(start_block, min(end_block + 1, len(blocks))):
            block = blocks[block_index]
            if not isinstance(block, dict):
                continue
            if block.get("type") != "table":
                continue
            if is_standalone_numbered_table_placeholder(str(block.get("content") or "")):
                new_blocks.append(dict(block))

    interval_groups: list[tuple[int, int, int, int, list[ExampleCandidate]]] = []
    for start_block, start_char, end_block, end_char, item in intervals:
        if interval_groups and interval_groups[-1][:4] == (start_block, start_char, end_block, end_char):
            interval_groups[-1][4].append(item)
        else:
            interval_groups.append((start_block, start_char, end_block, end_char, [item]))

    for start_block, start_char, end_block, end_char, items in interval_groups:
        if (start_block, start_char) < (cursor_block, cursor_char):
            continue
        append_gap_until(start_block, start_char)
        for item in sorted(items, key=lambda candidate: natural_key(candidate.example_id)):
            ref = example_refs[candidate_key(item)]
            remapped_indexes[candidate_key(item)] = len(new_blocks)
            new_blocks.append({"type": "example", "content": f"[[SEE_EXAMPLE:{ref}]]"})
        append_preserved_numbered_table_blocks(start_block, end_block)
        cursor_block = end_block
        cursor_char = end_char

    append_gap_until(len(blocks), 0)

    if not dry_run:
        data["blocks"] = new_blocks
        write_json(path, data)
    return {
        "file": path.name,
        "before_blocks": len(blocks),
        "after_blocks": len(new_blocks),
        "replaced": len(remapped_indexes),
        "removed_blocks": len(blocks) - len(new_blocks),
        "remapped_indexes": remapped_indexes,
    }


def count_blocks(structured_dir: Path) -> int:
    total = 0
    for path in load_unit_files(structured_dir):
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if isinstance(blocks, list):
            total += len(blocks)
    return total


def write_example_library(output_structured: Path, rows: list[dict[str, Any]], *, dry_run: bool = False) -> None:
    if dry_run:
        return
    write_json(
        output_structured / "example_library.json",
        {
            "schema": "example_library.v1",
            "example_count": len(rows),
            "examples": rows,
        },
    )


def _table_reference_key(chapter: str, table_id: str) -> str:
    return table_reference_key(chapter, table_id)


def _source_unit_id(source_file: str) -> str:
    return Path(str(source_file or "")).stem


def _unit_subsection(data: dict[str, Any]) -> str:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    for key in ("display_heading", "section_level_2", "section_level_1", "section"):
        value = str(metadata.get(key) or "").strip()
        if value:
            return value
    subsections = metadata.get("subsections") if isinstance(metadata.get("subsections"), list) else []
    for item in subsections:
        value = str(item or "").strip()
        if value:
            return value
    return ""


def _unit_contains_table_ref(data: dict[str, Any], table_id: str) -> bool:
    wanted = str(table_id or "").strip().lower()
    blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        content = str(block.get("content") or "")
        for match in TABLE_PLACEHOLDER_RE.finditer(content):
            if match.group(1).strip().lower() == wanted:
                return True
    return False


def _update_unit_table_metadata(
    structured_dir: Path,
    unit_id: str,
    chapter: str,
    table_id: str,
    *,
    add: bool,
    dry_run: bool,
) -> bool:
    if not unit_id:
        return False
    path = structured_dir / f"{unit_id}.json"
    if not path.exists():
        return False
    data = read_json(path)
    if not isinstance(data, dict):
        return False
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
        data["metadata"] = metadata

    table_ref = str(table_id or "").strip()
    key = _table_reference_key(chapter, table_ref)
    refs = [
        str(item).strip()
        for item in (metadata.get("table_references") or [])
        if str(item).strip()
    ]
    keys = [
        str(item).strip()
        for item in (metadata.get("table_reference_keys") or [])
        if str(item).strip()
    ]
    before_refs = list(refs)
    before_keys = list(keys)

    if add:
        if table_ref and table_ref not in refs:
            refs.append(table_ref)
        if key and key not in keys:
            keys.append(key)
    else:
        refs = [item for item in refs if item != table_ref]
        keys = [item for item in keys if item != key]

    refs = sort_table_refs(refs)
    keys = sort_table_ref_keys(keys)
    if refs == before_refs and keys == before_keys:
        return False

    metadata["table_references"] = refs
    if keys:
        metadata["table_reference_keys"] = keys
    else:
        metadata.pop("table_reference_keys", None)
    if not dry_run:
        write_json(path, data)
    return True


def _table_example_overlap_score(entry: dict[str, Any], row: dict[str, Any]) -> float:
    token_source: list[str] = [str(entry.get("title") or "")]
    rows = entry.get("rows") if isinstance(entry.get("rows"), list) else []
    for table_row in rows[:4]:
        if isinstance(table_row, list):
            token_source.extend(str(cell) for cell in table_row[:5])
    tokens = [
        token
        for token in normalize_match_text(" ".join(token_source)).split()
        if len(token) >= 3 and token not in {"table", "inline", "example"}
    ]
    if not tokens:
        return 0.0
    example_text = normalize_match_text(
        f"{row.get('title') or ''} {row.get('content_markdown') or row.get('content_plain') or ''}"
    )
    hits = sum(1 for token in tokens if token in example_text)
    return hits / max(1, len(tokens))


def _rebind_inline_table_sources_from_examples(
    structured_dir: Path,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "example_rows_scanned": 0,
        "inline_table_refs_seen": 0,
        "table_sources_rebound": 0,
        "unit_metadata_added": 0,
        "unit_metadata_removed": 0,
    }
    table_library_path = structured_dir / "table_library.json"
    if not table_library_path.exists():
        return stats
    payload = read_json(table_library_path)
    tables = payload.get("tables") if isinstance(payload, dict) else None
    if not isinstance(tables, list):
        return stats

    changed_library = False
    processed: set[tuple[str, str, str]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        stats["example_rows_scanned"] += 1
        chapter = str(row.get("chapter") or "").strip().lower()
        source_file = str(row.get("source_file") or "").strip()
        source_unit = _source_unit_id(source_file)
        if not chapter or not source_unit:
            continue
        table_refs = [
            str(item).strip()
            for item in (row.get("table_refs") or [])
            if INLINE_TABLE_ID_RE.fullmatch(str(item).strip())
        ]
        for table_id in table_refs:
            stats["inline_table_refs_seen"] += 1
            key = (chapter, table_id, source_unit)
            if key in processed:
                continue
            processed.add(key)
            candidates: list[dict[str, Any]] = []
            for entry in tables:
                if not isinstance(entry, dict):
                    continue
                source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
                if str(entry.get("id") or "").strip().lower() != table_id.lower():
                    continue
                if str(entry.get("table_type") or "").strip().lower() != "inline":
                    continue
                if str(source.get("chapter") or "").strip().lower() != chapter:
                    continue
                candidates.append(entry)
            if not candidates:
                continue
            scored = sorted(
                ((_table_example_overlap_score(entry, row), entry) for entry in candidates),
                key=lambda item: item[0],
                reverse=True,
            )
            score, entry = scored[0]
            if len(candidates) > 1 and score < 0.10:
                continue

            source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
            old_unit = str(source.get("unit_id") or "").strip()
            if old_unit == source_unit:
                continue
            source_page = _safe_block_index((source if isinstance(source, dict) else {}).get("page"))
            row_evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row_page = _safe_block_index(row_evidence.get("source_page") or row_evidence.get("raw_source_page"))
            if source_page is not None and row_page is not None and abs(source_page - row_page) > 2:
                continue
            new_unit_path = structured_dir / source_file
            new_unit_data = read_json(new_unit_path) if new_unit_path.exists() else {}
            source["unit_id"] = source_unit
            source["chapter"] = chapter
            subsection = _unit_subsection(new_unit_data) if isinstance(new_unit_data, dict) else ""
            if subsection:
                source["subsection"] = subsection
            source["source_rebound_by"] = "example_pipeline_inline_table_source"
            entry["source"] = source
            changed_library = True
            stats["table_sources_rebound"] += 1

            if _update_unit_table_metadata(
                structured_dir,
                source_unit,
                chapter,
                table_id,
                add=True,
                dry_run=dry_run,
            ):
                stats["unit_metadata_added"] += 1

            if old_unit and old_unit != source_unit:
                old_path = structured_dir / f"{old_unit}.json"
                old_data = read_json(old_path) if old_path.exists() else {}
                if isinstance(old_data, dict) and not _unit_contains_table_ref(old_data, table_id):
                    if _update_unit_table_metadata(
                        structured_dir,
                        old_unit,
                        chapter,
                        table_id,
                        add=False,
                        dry_run=dry_run,
                    ):
                        stats["unit_metadata_removed"] += 1

    if changed_library and not dry_run:
        write_json(table_library_path, payload)
    return stats


def _library_hashes(structured_dir: Path) -> dict[str, str | None]:
    hashes: dict[str, str | None] = {}
    for file_name in ("formula_library.json", "table_library.json"):
        path = structured_dir / file_name
        hashes[file_name] = sha256_file(path) if path.exists() else None
    return hashes


def _write_artifacts(artifacts_dir: Path | None, summary: dict[str, Any], library_rows: list[dict[str, Any]]) -> None:
    if artifacts_dir is None:
        return
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifacts_dir / "example_pipeline_summary.json", summary)
    write_json(artifacts_dir / "example_library_items.json", library_rows)


def _example_identity(row: dict[str, Any]) -> tuple[str, str]:
    chapter = str(row.get("chapter") or "").strip().lower()
    ref = str(row.get("example_ref") or row.get("example_id") or "").strip()
    return chapter, ref


def _candidate_identity(item: ExampleCandidate, example_ref: str | None = None) -> tuple[str, str]:
    return item.chapter, str(example_ref or item.example_id).strip()


def _example_number_parts(example_id: str) -> tuple[str, int] | None:
    value = str(example_id or "").strip()
    parts = value.rsplit(".", 1)
    if len(parts) != 2:
        return None
    prefix, suffix = parts
    digits = ""
    for char in suffix:
        if char.isdigit():
            digits += char
        else:
            break
    if not prefix or not digits:
        return None
    return prefix.lower(), int(digits)


def _load_existing_example_library_rows(structured_dir: Path) -> list[dict[str, Any]]:
    path = structured_dir / "example_library.json"
    if not path.exists():
        return []
    payload = read_json(path)
    rows = payload.get("examples") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _row_starts_with_true_example_heading(row: dict[str, Any]) -> bool:
    content = str(row.get("content_markdown") or "")
    match = EXAMPLE_HEAD_RE.search(content)
    if not match:
        return False
    if match.start() != 0:
        return False
    if not is_example_heading_match(content, match):
        return False
    return clean_example_id(match.group("example_id")) == clean_example_id(row.get("example_id"))


def clean_example_id(value: Any) -> str:
    return str(value or "").strip()


def _example_source_page_from_evidence(
    *,
    chapter: str,
    example_id: str,
    evidence: dict[str, Any] | None,
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> int | None:
    evidence = evidence if isinstance(evidence, dict) else {}
    for key in ("source_page", "raw_source_page", "visual_stop_page"):
        page = _safe_block_index(evidence.get(key))
        if page is not None and page > 0:
            return page
    if raw_pages:
        return raw_pages.get((chapter, clean_example_id(example_id)))
    return None


def _candidate_source_page(
    item: ExampleCandidate,
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> int | None:
    return _example_source_page_from_evidence(
        chapter=item.chapter,
        example_id=item.example_id,
        evidence=item.evidence,
        raw_pages=raw_pages,
    )


def _row_source_page(
    row: dict[str, Any],
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> int | None:
    chapter = str(row.get("chapter") or "").strip().lower()
    example_id = clean_example_id(row.get("example_id") or row.get("example_ref"))
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    return _example_source_page_from_evidence(
        chapter=chapter,
        example_id=example_id,
        evidence=evidence,
        raw_pages=raw_pages,
    )


def _visual_stop_text_from_metadata(metadata: dict[str, Any] | None) -> str:
    metadata = metadata if isinstance(metadata, dict) else {}
    visual_stop = metadata.get("visual_stop") if isinstance(metadata.get("visual_stop"), dict) else {}
    return str(visual_stop.get("stop_text") or "")


def _visual_stop_mentions_example(*, stop_text: str, example_id: str, title: str = "") -> bool:
    stop_text = str(stop_text or "")
    if not stop_text:
        return False
    clean_id = clean_example_id(example_id)
    if clean_id and re.search(rf"\bExample\s+{re.escape(clean_id)}\b", stop_text, flags=re.IGNORECASE):
        return True
    title_tokens = normalize_match_text(title).split()
    stop_norm = normalize_match_text(stop_text)
    if len(title_tokens) >= 6 and " ".join(title_tokens[: min(14, len(title_tokens))]) in stop_norm:
        return True
    return False


def _candidate_visual_stop_mentions_target(previous: ExampleCandidate, target: ExampleCandidate) -> bool:
    return _visual_stop_mentions_example(
        stop_text=_visual_stop_text_from_metadata(previous.metadata),
        example_id=target.example_id,
        title=target.title or target.content_plain,
    )


def _row_visual_stop_mentions_target(previous: dict[str, Any], target: dict[str, Any]) -> bool:
    metadata = previous.get("metadata") if isinstance(previous.get("metadata"), dict) else {}
    return _visual_stop_mentions_example(
        stop_text=_visual_stop_text_from_metadata(metadata),
        example_id=str(target.get("example_id") or target.get("example_ref") or ""),
        title=str(target.get("title") or target.get("content_plain") or target.get("content_markdown") or ""),
    )


def _infer_restored_block_type(row: dict[str, Any], fallback: str = "discussion") -> str:
    content = str(row.get("content_markdown") or "")
    formula_refs = row.get("formula_refs") if isinstance(row.get("formula_refs"), list) else []
    if formula_refs or "$$" in content or "\\begin{" in content:
        return "derivation"
    return fallback


def _restore_false_example_rows(
    structured_dir: Path,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> dict[str, int]:
    stats = {"rows_scanned": len(rows), "false_heading_rows": 0, "source_blocks_restored": 0}
    for row in rows:
        if _row_starts_with_true_example_heading(row):
            continue
        source_file = str(row.get("source_file") or "").strip()
        placeholder = str(row.get("placeholder") or "")
        if not source_file or not placeholder:
            continue
        path = structured_dir / source_file
        if not path.exists():
            continue
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else None
        block_index = _safe_block_index(row.get("start_block_index"))
        if not isinstance(blocks, list) or block_index is None or block_index >= len(blocks):
            continue
        block = blocks[block_index]
        if not isinstance(block, dict):
            continue
        if str(block.get("content") or "") != placeholder:
            continue

        stats["false_heading_rows"] += 1
        fallback_type = str(block.get("type") or "discussion")
        if fallback_type == "example":
            fallback_type = "discussion"
        block["type"] = _infer_restored_block_type(row, fallback_type)
        block["content"] = str(row.get("content_markdown") or "").strip()
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        row["replacement"] = {
            **replacement,
            "status": "restored",
            "reason": "inline_example_reference_not_heading",
        }
        evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
        row["evidence"] = {
            **evidence,
            "existing_library_repair": "false_example_heading_restored_to_source_block",
        }
        stats["source_blocks_restored"] += 1
        if not dry_run:
            write_json(path, data)
    return stats


def _existing_sequence_gap_targets(rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    numbers_by_group: dict[tuple[str, str, str], set[int]] = defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        parts = _example_number_parts(example_id)
        if not chapter or parts is None:
            continue
        prefix, number = parts
        source_prefix = re.sub(r"\d+$", "", Path(str(row.get("source_file") or "").strip()).stem)
        numbers_by_group[(chapter, source_prefix, prefix)].add(number)

    targets: set[tuple[str, str]] = set()
    for (chapter, _, prefix), numbers in numbers_by_group.items():
        if len(numbers) < 2:
            continue
        first = min(numbers)
        last = max(numbers)
        lower_bound = 1 if first <= 2 else first
        for number in range(lower_bound, last + 1):
            if number not in numbers:
                targets.add((chapter, f"{prefix}.{number}"))
    return targets


def _sequence_gap_targets_from_rows(rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    numbers_by_group: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        parts = _example_number_parts(example_id)
        if not chapter or parts is None:
            continue
        prefix, number = parts
        numbers_by_group[(chapter, prefix)].add(number)

    targets: set[tuple[str, str]] = set()
    for (chapter, prefix), numbers in numbers_by_group.items():
        if len(numbers) < 2:
            continue
        first = min(numbers)
        last = max(numbers)
        lower_bound = 1 if first <= 2 else first
        for number in range(lower_bound, last + 1):
            if number not in numbers:
                targets.add((chapter, f"{prefix}.{number}"))
    return targets


def _raw_example_ids_by_chapter(project_root: Path, chapters: set[str]) -> dict[str, set[str]]:
    raw_ids: dict[str, set[str]] = defaultdict(set)
    for chapter in sorted(chapters, key=chapter_sort_key):
        for record in ordered_paddle_records(project_root, chapter):
            if record.label not in PADDLE_EXAMPLE_LABELS:
                continue
            match = raw_example_start_match(record.content)
            if not match:
                continue
            example_id = clean_ref_id(match.group("example_id"))
            if example_id:
                raw_ids[chapter].add(example_id)
    return raw_ids


def _missing_raw_sequence_targets(
    *,
    project_root: Path,
    rows: list[dict[str, Any]],
) -> set[tuple[str, str]]:
    row_targets = _sequence_gap_targets_from_rows(rows)
    if not row_targets:
        return set()
    chapters = {chapter for chapter, _ in row_targets}
    raw_ids_by_chapter = _raw_example_ids_by_chapter(project_root, chapters)
    return {
        (chapter, example_id)
        for chapter, example_id in row_targets
        if example_id in raw_ids_by_chapter.get(chapter, set())
    }


def _structured_placeholder_refs(structured_dir: Path) -> dict[str, set[str]]:
    refs_by_chapter: dict[str, set[str]] = defaultdict(set)
    for path in load_unit_files(structured_dir):
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        chapter = str(metadata.get("chapter") or path.stem.split("_", 1)[0]).strip().lower()
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            for match in EXAMPLE_PLACEHOLDER_RE.finditer(str(block.get("content") or "")):
                example_ref = clean_ref_id(match.group(1))
                if example_ref:
                    refs_by_chapter[chapter].add(example_ref)
    return refs_by_chapter


def _token_anchor_position(
    raw_text: str,
    content: str,
    *,
    min_anchor_tokens: int = 8,
) -> tuple[int, str, int] | None:
    raw_tokens = normalize_match_text(raw_text).split()
    content_norm = normalize_match_text(content)
    if len(raw_tokens) < min_anchor_tokens or not content_norm:
        return None
    for raw_offset in range(0, len(raw_tokens) - min_anchor_tokens + 1):
        anchor = " ".join(raw_tokens[raw_offset : raw_offset + min_anchor_tokens])
        norm_pos = content_norm.find(anchor)
        if norm_pos < 0:
            continue
        return raw_offset, anchor, norm_pos
    return None


def _content_char_for_anchor(content: str, anchor: str) -> int | None:
    anchor_tokens = anchor.split()
    if not anchor_tokens:
        return None
    content_tokens = _token_spans(content)
    content_values = [token for token, _, _ in content_tokens]
    index = _find_subsequence(content_values, anchor_tokens)
    if index is None:
        return None
    return content_tokens[index][1]


def _expand_split_start_to_adjacent_placeholder(content: str, split_char: int) -> int:
    candidate_start = split_char
    for match in TABLE_PLACEHOLDER_RE.finditer(content[:split_char]):
        between = content[match.end() : split_char]
        if between.strip():
            continue
        candidate_start = match.start()
    return candidate_start


def _merge_raw_layout_example_row(row: dict[str, Any], raw_item: ExampleCandidate) -> bool:
    """Refresh a structured example row with stronger raw-layout evidence.

    Structured extraction is usually better for text continuity, but Paddle raw
    layout can preserve visual-only inline tables and page-spanning tails that
    are absent after table owner normalization.  This merge keeps the existing
    structured source file and placeholder identity while importing raw content
    only when it clearly improves coverage.
    """

    before_content = str(row.get("content_markdown") or "")
    before_refs = [str(ref) for ref in (row.get("table_refs") or [])]
    raw_refs = [str(ref) for ref in raw_item.table_refs]
    added_refs = [ref for ref in raw_refs if ref and ref not in before_refs]
    changed = False

    if added_refs and all(ref.lower().startswith("inline_") for ref in added_refs):
        row["content_markdown"] = raw_item.content_markdown
        row["content_plain"] = raw_item.content_plain
        row["formula_refs"] = list(raw_item.formula_refs)
        row["table_refs"] = list(raw_item.table_refs)
        row["figure_refs"] = list(raw_item.figure_refs)
        row["external_refs"] = list(raw_item.external_refs)
        row["title"] = raw_item.title
        changed = True

    raw_words = len(str(raw_item.content_plain or "").split())
    before_words = len(collapse_ws(strip_structured_refs(strip_html(before_content))).split())
    if raw_words > before_words + 12:
        if not changed:
            row["content_markdown"] = raw_item.content_markdown
            row["content_plain"] = raw_item.content_plain
            row["formula_refs"] = list(raw_item.formula_refs)
            row["table_refs"] = list(raw_item.table_refs)
            row["figure_refs"] = list(raw_item.figure_refs)
            row["external_refs"] = list(raw_item.external_refs)
            row["title"] = raw_item.title
        changed = True

    if not changed:
        return False

    row_metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    raw_metadata = raw_item.metadata if isinstance(raw_item.metadata, dict) else {}
    content_plain = str(row.get("content_plain") or collapse_ws(strip_structured_refs(strip_html(row.get("content_markdown") or ""))))
    row["metadata"] = {
        **row_metadata,
        "has_formula": bool(row.get("formula_refs")),
        "has_table": bool(row.get("table_refs")),
        "has_figure": bool(row.get("figure_refs")),
        "word_count": len(content_plain.split()) if content_plain else 0,
        "needs_review": looks_truncated(str(row.get("content_markdown") or "")),
        "raw_layout_merged": True,
    }
    if added_refs:
        row["metadata"]["raw_layout_added_table_refs"] = added_refs
        row["metadata"]["source_span_extra_blocks"] = len(added_refs)
    if isinstance(raw_metadata.get("visual_stop"), dict):
        row["metadata"]["visual_stop"] = raw_metadata["visual_stop"]
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    row["evidence"] = {
        **evidence,
        "raw_layout_merge": {
            "added_table_refs": added_refs,
            "before_word_count": before_words,
            "raw_word_count": raw_words,
        },
    }
    return True


def _merge_rows_from_raw_layout(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    stats = {
        "chapters_scanned": 0,
        "raw_candidates": 0,
        "rows_merged": 0,
        "inline_table_refs_added": 0,
    }
    by_chapter: dict[str, set[str]] = defaultdict(set)
    rows_by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if not chapter or not example_id:
            continue
        by_chapter[chapter].add(example_id)
        rows_by_identity[(chapter, example_id)] = row
    if not by_chapter:
        return stats

    context = build_structured_context(structured_dir)
    for chapter, example_ids in sorted(by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        stats["chapters_scanned"] += 1
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(),
            target_ids=example_ids,
            skip_structured_matches=False,
        )
        stats["raw_candidates"] += len(raw_items)
        for raw_item in raw_items:
            row = rows_by_identity.get((chapter, raw_item.example_id))
            if row is None:
                continue
            before_refs = {str(ref) for ref in (row.get("table_refs") or [])}
            if _merge_raw_layout_example_row(row, raw_item):
                after_refs = {str(ref) for ref in (row.get("table_refs") or [])}
                stats["rows_merged"] += 1
                stats["inline_table_refs_added"] += len(
                    [ref for ref in after_refs - before_refs if ref.lower().startswith("inline_")]
                )
    return stats


def _join_content_parts(parts: list[str]) -> str:
    return "\n\n".join(part.strip() for part in parts if part and part.strip()).strip()


def _make_row_from_candidate(item: ExampleCandidate, *, example_ref: str) -> dict[str, Any]:
    _refresh_candidate_metadata(item)
    return example_to_library_row(
        item,
        example_ref=example_ref,
        replacement_status="replaced",
        replacement_reason="placeholder_block_written",
    )


def _split_missing_examples_from_existing_library(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    targets = _existing_sequence_gap_targets(rows)
    stats: dict[str, Any] = {
        "targeted": len(targets),
        "raw_recovered": 0,
        "split_from_existing_rows": 0,
        "unmatched": 0,
        "updated_source_blocks": 0,
        "missing_ids": sorted([example_id for _, example_id in targets], key=natural_key),
    }
    if not targets:
        return stats

    context = build_structured_context(structured_dir)
    existing_ids_by_chapter: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if chapter and example_id:
            existing_ids_by_chapter[chapter].add(example_id)

    by_chapter: dict[str, set[str]] = defaultdict(set)
    for chapter, example_id in targets:
        by_chapter[chapter].add(example_id)

    rows_to_append: list[dict[str, Any]] = []
    placeholder_updates: dict[str, list[str]] = defaultdict(list)
    raw_pages = _raw_example_pages(project_root, set(by_chapter))
    for chapter, chapter_targets in sorted(by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(existing_ids_by_chapter.get(chapter, set())),
            target_ids=chapter_targets,
            skip_structured_matches=False,
        )
        stats["raw_recovered"] += len(raw_items)
        for raw_item in raw_items:
            matched: tuple[dict[str, Any], int, str] | None = None
            _raw_table_refs_before_align = list(raw_item.table_refs)
            _raw_content_before_align = raw_item.content_markdown
            aligned_without_owner = _align_raw_candidate_to_structured_content(raw_item, structured_dir)
            aligned_without_owner = _normalize_sequence_gap_alignment(
                raw_item,
                aligned_without_owner,
                context=context,
                structured_dir=structured_dir,
                raw_pages=raw_pages,
            )
            # Fix 5: preserve table placeholders from raw layout when alignment drops them
            if aligned_without_owner is not None and _raw_table_refs_before_align and not aligned_without_owner.table_refs:
                aligned_without_owner.table_refs = _raw_table_refs_before_align
                aligned_without_owner.content_markdown = _raw_content_before_align
                aligned_without_owner.metadata["has_table"] = True
            for row in rows:
                if str(row.get("chapter") or "").strip().lower() != chapter:
                    continue
                replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
                if replacement.get("status") == "restored":
                    continue
                content = str(row.get("content_markdown") or "")
                anchor = _token_anchor_position(raw_item.content_plain, content)
                if anchor is None:
                    continue
                _, anchor_text, _ = anchor
                split_char = _content_char_for_anchor(content, anchor_text)
                if split_char is None:
                    continue
                matched = (row, split_char, anchor_text)
                break

            if matched is None:
                if aligned_without_owner is None:
                    stats["unmatched"] += 1
                    continue
                raw_item = aligned_without_owner
                raw_item.metadata = {
                    **raw_item.metadata,
                    "existing_library_sequence_gap_aligned_without_owner": True,
                }
                raw_item.evidence = {
                    **raw_item.evidence,
                    "detection_method": "sequence_gap_raw_layout_aligned_to_structured_block",
                }
                _refresh_candidate_metadata(raw_item)
                example_ref = raw_item.example_id
                if any(str(row.get("example_ref") or "") == example_ref for row in [*rows, *rows_to_append]):
                    source_stem = Path(raw_item.source_file).stem
                    example_ref = f"{raw_item.example_id}@{source_stem}_{raw_item.start_block_index}"
                rows_to_append.append(_make_row_from_candidate(raw_item, example_ref=example_ref))
                placeholder_updates[raw_item.source_file].append(f"[[SEE_EXAMPLE:{example_ref}]]")
                stats["split_from_existing_rows"] += 1
                continue

            owner_row, split_char, anchor_text = matched
            owner_content = str(owner_row.get("content_markdown") or "")
            prefix = owner_content[:split_char].strip()
            split_char = _expand_split_start_to_adjacent_placeholder(owner_content, split_char)
            prefix = owner_content[:split_char].strip()
            if not prefix:
                stats["unmatched"] += 1
                continue

            aligned_item = _align_raw_candidate_to_structured_content(raw_item, structured_dir)
            aligned_item = _normalize_sequence_gap_alignment(
                raw_item,
                aligned_item,
                context=context,
                structured_dir=structured_dir,
                raw_pages=raw_pages,
            )
            if aligned_item is not None:
                # Fix 5: preserve table placeholders from raw layout when alignment drops them
                if raw_item.table_refs and not aligned_item.table_refs:
                    aligned_item.table_refs = raw_item.table_refs
                    aligned_item.content_markdown = raw_item.content_markdown
                    aligned_item.metadata["has_table"] = True
                raw_item = aligned_item
            else:
                raw_item.source_file = str(owner_row.get("source_file") or raw_item.source_file)
                raw_item.start_block_index = int(owner_row.get("start_block_index") or 0)
                raw_item.end_block_index = int(owner_row.get("end_block_index") or raw_item.start_block_index)
            raw_item.metadata = {
                **raw_item.metadata,
                "existing_library_split_from": owner_row.get("example_ref") or owner_row.get("example_id"),
                "existing_library_split_anchor": anchor_text,
            }
            raw_item.evidence = {
                **raw_item.evidence,
                "detection_method": "sequence_gap_raw_layout_existing_library_split",
                "split_from_example_ref": owner_row.get("example_ref") or owner_row.get("example_id"),
            }
            _refresh_candidate_metadata(raw_item)

            owner_row["content_markdown"] = prefix
            owner_row["content_plain"] = collapse_ws(strip_structured_refs(strip_html(prefix)))
            owner_row["formula_refs"] = extract_formula_refs(prefix)
            owner_row["table_refs"] = extract_table_refs(prefix)
            owner_row["figure_refs"] = extract_figure_refs(prefix)
            owner_row["external_refs"] = extract_external_refs(prefix)
            owner_metadata = owner_row.get("metadata") if isinstance(owner_row.get("metadata"), dict) else {}
            owner_row["metadata"] = {
                **owner_metadata,
                "has_formula": bool(owner_row["formula_refs"]),
                "has_table": bool(owner_row["table_refs"]),
                "has_figure": bool(owner_row["figure_refs"]),
                "word_count": len(owner_row["content_plain"].split()) if owner_row["content_plain"] else 0,
                "needs_review": looks_truncated(prefix),
            }
            owner_evidence = owner_row.get("evidence") if isinstance(owner_row.get("evidence"), dict) else {}
            owner_row["evidence"] = {
                **owner_evidence,
                "existing_library_repair": "clipped_before_sequence_gap_example",
                "clipped_before_example_id": raw_item.example_id,
            }

            example_ref = raw_item.example_id
            if any(str(row.get("example_ref") or "") == example_ref for row in [*rows, *rows_to_append]):
                source_stem = Path(raw_item.source_file).stem
                example_ref = f"{raw_item.example_id}@{source_stem}_{raw_item.start_block_index}"
            rows_to_append.append(_make_row_from_candidate(raw_item, example_ref=example_ref))
            if aligned_item is None:
                placeholder_updates[raw_item.source_file].append(str(owner_row.get("placeholder") or ""))
                placeholder_updates[raw_item.source_file].append(f"[[SEE_EXAMPLE:{example_ref}]]")
            else:
                placeholder_updates[raw_item.source_file].append(f"[[SEE_EXAMPLE:{example_ref}]]")
            stats["split_from_existing_rows"] += 1

    if rows_to_append:
        rows.extend(rows_to_append)
        rows.sort(
            key=lambda row: (
                chapter_sort_key(str(row.get("chapter") or "")),
                natural_key(str(row.get("source_file") or "")),
                _safe_block_index(row.get("start_block_index")) or 0,
                natural_key(str(row.get("example_ref") or row.get("example_id") or "")),
            )
        )

    for source_file, placeholders in placeholder_updates.items():
        path = structured_dir / source_file
        if not path.exists():
            continue
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if not isinstance(blocks, list):
            continue
        seen: list[str] = []
        for placeholder in placeholders:
            if placeholder and placeholder not in seen:
                seen.append(placeholder)
        if not seen:
            continue
        target_index = None
        for index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            if str(block.get("content") or "") in seen:
                target_index = index
                break
        if target_index is None and len(seen) == 1:
            placeholder = seen[0]
            for row in rows_to_append:
                if str(row.get("placeholder") or "") != placeholder:
                    continue
                block_index = _safe_block_index(row.get("start_block_index"))
                if block_index is None:
                    continue
                metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
                if metadata.get("insert_placeholder_only"):
                    if 0 < block_index <= len(blocks):
                        previous_block = blocks[block_index - 1]
                        previous_content = str(previous_block.get("content") or "") if isinstance(previous_block, dict) else ""
                        previous_type = str(previous_block.get("type") or "") if isinstance(previous_block, dict) else ""
                        if previous_type == "example" and EXAMPLE_PLACEHOLDER_RE.search(previous_content):
                            if placeholder not in previous_content:
                                previous_block["content"] = f"{previous_content.rstrip()} {placeholder}".strip()
                                stats["updated_source_blocks"] += 1
                            target_index = block_index - 1
                    if target_index is None and block_index <= len(blocks):
                        blocks[block_index:block_index] = [{"type": "example", "content": placeholder}]
                        stats["updated_source_blocks"] += 1
                        target_index = block_index
                        for _row in rows:
                            if str(_row.get("placeholder") or "") == placeholder:
                                continue
                            if str(_row.get("source_file") or "") != source_file:
                                continue
                            _s = _safe_block_index(_row.get("start_block_index"))
                            _e = _safe_block_index(_row.get("end_block_index"))
                            if _s is not None and _s >= block_index:
                                _row["start_block_index"] = _s + 1
                            if _e is not None and _e >= block_index:
                                _row["end_block_index"] = _e + 1
                            _repl = _row.get("replacement") if isinstance(_row.get("replacement"), dict) else {}
                            _span = _repl.get("source_block_span")
                            if isinstance(_span, list) and len(_span) == 2:
                                _repl["source_block_span"] = [
                                    _span[0] + 1 if _span[0] >= block_index else _span[0],
                                    _span[1] + 1 if _span[1] >= block_index else _span[1],
                                ]
                                _row["replacement"] = _repl
                    if target_index is not None:
                        break
                    continue
                if block_index >= len(blocks):
                    continue
                block = blocks[block_index]
                if not isinstance(block, dict):
                    continue
                content = str(block.get("content") or "")
                start_char = _safe_block_index(metadata.get("replacement_start_char"))
                end_char = _safe_block_index(metadata.get("replacement_end_char"))
                if start_char is None or end_char is None or end_char <= start_char:
                    continue
                prefix = content[:start_char].strip()
                suffix = content[end_char:].strip()
                replacement_blocks = []
                if prefix:
                    replacement_blocks.append({**block, "content": prefix})
                example_index = block_index + len(replacement_blocks)
                replacement_blocks.append({"type": "example", "content": placeholder})
                if suffix:
                    replacement_blocks.append({**block, "content": suffix})
                blocks[block_index : block_index + 1] = replacement_blocks
                stats["updated_source_blocks"] += 1
                target_index = example_index
                # Fix 1: shift existing rows whose indexes are after the insertion point
                _delta = len(replacement_blocks) - 1
                if _delta != 0:
                    for _row in rows:
                        if str(_row.get("source_file") or "") != source_file:
                            continue
                        _s = _safe_block_index(_row.get("start_block_index"))
                        _e = _safe_block_index(_row.get("end_block_index"))
                        if _s is not None and _s > block_index:
                            _row["start_block_index"] = _s + _delta
                        if _e is not None and _e > block_index:
                            _row["end_block_index"] = _e + _delta
                        _repl = _row.get("replacement") if isinstance(_row.get("replacement"), dict) else {}
                        _span = _repl.get("source_block_span")
                        if isinstance(_span, list) and len(_span) == 2:
                            _repl["source_block_span"] = [
                                _span[0] + _delta if _span[0] > block_index else _span[0],
                                _span[1] + _delta if _span[1] > block_index else _span[1],
                            ]
                            _row["replacement"] = _repl
                replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
                row["replacement"] = {
                    **replacement,
                    "placeholder_block_index": example_index,
                    "placeholder_source_file": source_file,
                }
                break
            if target_index is not None:
                for row in rows_to_append:
                    if str(row.get("placeholder") or "") not in seen:
                        continue
                    row["start_block_index"] = target_index
                    row["end_block_index"] = target_index
                    replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
                    row["replacement"] = {
                        **replacement,
                        "placeholder_block_index": target_index,
                        "placeholder_source_file": source_file,
                    }
                if not dry_run:
                    write_json(path, data)
                continue
        if target_index is None:
            continue
        # Fix 2: split joined placeholders into individual blocks
        new_example_blocks = [{"type": "example", "content": ph} for ph in seen]
        blocks[target_index : target_index + 1] = new_example_blocks
        stats["updated_source_blocks"] += 1
        # Fix 1 (cont): shift existing rows whose indexes are after the insertion point
        _delta = len(new_example_blocks) - 1
        if _delta != 0:
            for _row in rows:
                if str(_row.get("source_file") or "") != source_file:
                    continue
                _s = _safe_block_index(_row.get("start_block_index"))
                _e = _safe_block_index(_row.get("end_block_index"))
                if _s is not None and _s > target_index:
                    _row["start_block_index"] = _s + _delta
                if _e is not None and _e > target_index:
                    _row["end_block_index"] = _e + _delta
                _repl = _row.get("replacement") if isinstance(_row.get("replacement"), dict) else {}
                _span = _repl.get("source_block_span")
                if isinstance(_span, list) and len(_span) == 2:
                    _repl["source_block_span"] = [
                        _span[0] + _delta if _span[0] > target_index else _span[0],
                        _span[1] + _delta if _span[1] > target_index else _span[1],
                    ]
                    _row["replacement"] = _repl
        # Update rows_to_append to point to their individual blocks
        for row in rows_to_append:
            ph = str(row.get("placeholder") or "")
            if ph not in seen:
                continue
            ph_index = target_index + seen.index(ph)
            row["start_block_index"] = ph_index
            row["end_block_index"] = ph_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            row["replacement"] = {
                **replacement,
                "placeholder_block_index": ph_index,
                "placeholder_source_file": source_file,
            }
        if not dry_run:
            write_json(path, data)
    return stats


def _status_counts_for_rows(rows: list[dict[str, Any]]) -> Counter[str]:
    statuses = []
    for row in rows:
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        statuses.append(str(replacement.get("status") or "unknown"))
    return Counter(statuses)


def _row_quality_score(row: dict[str, Any]) -> tuple[int, int, int, int]:
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    content = str(row.get("content_markdown") or row.get("content_plain") or "")
    table_refs = row.get("table_refs") if isinstance(row.get("table_refs"), list) else extract_table_refs(content)
    formula_refs = row.get("formula_refs") if isinstance(row.get("formula_refs"), list) else extract_formula_refs(content)
    plain = collapse_ws(strip_structured_refs(strip_html(content)))
    return (
        0 if metadata.get("needs_review") else 1,
        int(bool(table_refs)) * 2 + int(bool(formula_refs)),
        len(plain.split()),
        len(content),
    )


def _candidate_quality_score(item: ExampleCandidate) -> tuple[int, int, int, int]:
    _refresh_candidate_metadata(item)
    return (
        0 if item.metadata.get("needs_review") else 1,
        int(bool(item.table_refs)) * 2 + int(bool(item.formula_refs)),
        len(item.content_plain.split()) if item.content_plain else 0,
        len(item.content_markdown),
    )


def _replace_row_from_candidate(
    row: dict[str, Any],
    item: ExampleCandidate,
    *,
    reason: str,
    evidence_patch: dict[str, Any] | None = None,
) -> None:
    _refresh_candidate_metadata(item)
    old_source_file = str(row.get("source_file") or "")
    old_start = _safe_block_index(row.get("start_block_index"))
    old_end = _safe_block_index(row.get("end_block_index"))
    old_replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
    old_span = _coerce_block_span(old_replacement.get("source_block_span"))
    source_span = old_span or _coerce_block_span([old_start, old_end]) or _candidate_source_block_span(item)
    preserved = {
        key: row.get(key)
        for key in ("example_ref", "placeholder", "replacement")
        if key in row
    }
    row.clear()
    row.update(item.to_dict())
    row.update(preserved)
    if old_source_file:
        row["source_file"] = old_source_file
    row["start_block_index"] = source_span[0]
    row["end_block_index"] = source_span[1]
    row.setdefault("example_ref", item.example_id)
    row.setdefault("placeholder", f"[[SEE_EXAMPLE:{row['example_ref']}]]")
    replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
    row["replacement"] = {
        **replacement,
        "status": replacement.get("status") or "replaced",
        "reason": replacement.get("reason") or "placeholder_block_written",
        "source_block_span": source_span,
    }
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    row["evidence"] = {**evidence, "existing_library_repair": reason, **(evidence_patch or {})}


def _refresh_row_physical_span_from_raw_alignment(
    row: dict[str, Any],
    raw_item: ExampleCandidate,
    structured_dir: Path,
) -> bool:
    aligned = _align_raw_candidate_to_structured_content(raw_item, structured_dir)
    if aligned is None:
        return False
    span = _coerce_block_span(aligned.metadata.get("source_block_span"))
    if span is None:
        return False
    old_file = str(row.get("source_file") or "")
    if old_file and aligned.source_file != old_file:
        evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
        row["evidence"] = {
            **evidence,
            "physical_span_refresh_skipped": {
                "reason": "cross_file_alignment_requires_explicit_relocation",
                "current_source_file": old_file,
                "aligned_source_file": aligned.source_file,
                "aligned_source_block_span": span,
            },
        }
        return False
    path = structured_dir / aligned.source_file
    replacement_start_char = aligned.metadata.get("replacement_start_char", 0)
    replacement_end_char = aligned.metadata.get("replacement_end_char")
    try:
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else []
    except Exception:
        blocks = []
    if isinstance(blocks, list) and 0 <= span[1] < len(blocks) and isinstance(blocks[span[1]], dict):
        end_content = blocks[span[1]].get("content")
        end_length = len(end_content) if isinstance(end_content, str) else 0
        if aligned.end_block_index != span[1] or replacement_end_char is None:
            replacement_end_char = end_length
    if aligned.start_block_index != span[0]:
        replacement_start_char = 0
    if span[0] != span[1]:
        replacement_start_char = 0
    replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
    old_span = _coerce_block_span(replacement.get("source_block_span")) or _coerce_block_span(
        [row.get("start_block_index"), row.get("end_block_index")]
    )
    old_placeholder_file = str(replacement.get("placeholder_source_file") or old_file)
    old_placeholder_index = _safe_block_index(replacement.get("placeholder_block_index"))
    if (
        old_file == aligned.source_file
        and old_span == span
        and old_placeholder_file == aligned.source_file
        and old_placeholder_index == span[0]
    ):
        return False

    row["source_file"] = aligned.source_file
    row["start_block_index"] = span[0]
    row["end_block_index"] = span[1]
    row["replacement"] = {
        **replacement,
        "status": replacement.get("status") or "replaced",
        "reason": replacement.get("reason") or "placeholder_block_written",
        "source_block_span": span,
        "placeholder_block_index": span[0],
        "placeholder_source_file": aligned.source_file,
    }
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    row["evidence"] = {
        **evidence,
        "physical_span_refresh": {
            "source": "raw_layout_alignment",
            "previous_source_file": old_file,
            "previous_source_block_span": old_span,
            "source_file": aligned.source_file,
            "source_block_span": span,
            "visual_stop_clipped": bool(aligned.metadata.get("visual_stop_clipped")),
            "raw_anchor_offset": aligned.evidence.get("raw_anchor_offset"),
            "structured_anchor_offset": aligned.evidence.get("structured_anchor_offset"),
        },
    }
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    row["metadata"] = {
        **metadata,
        "replacement_start_char": replacement_start_char,
        "replacement_end_char": replacement_end_char,
        "source_block_span": span,
    }
    return True


def _candidate_from_existing_row(row: dict[str, Any]) -> ExampleCandidate | None:
    candidate = existing_library_row_to_candidate(row)
    if candidate is None:
        return None
    replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
    span = _coerce_block_span(replacement.get("source_block_span")) or _coerce_block_span(
        [row.get("start_block_index"), row.get("end_block_index")]
    )
    if span is not None:
        candidate.start_block_index = span[0]
        candidate.end_block_index = span[1]
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    candidate.metadata = {
        **candidate.metadata,
        **metadata,
    }
    return candidate


def _ref_by_placeholder(rows: list[dict[str, Any]]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        placeholder = str(row.get("placeholder") or "")
        example_ref = str(row.get("example_ref") or row.get("example_id") or "").strip()
        if placeholder and example_ref:
            refs[placeholder] = example_ref
    return refs


def _rewrite_existing_example_source_spans(
    structured_dir: Path,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "rows_scanned": 0,
        "rows_rewritten": 0,
        "files_rewritten": 0,
        "blocks_removed": 0,
    }
    by_file: dict[str, list[ExampleCandidate]] = defaultdict(list)
    example_refs: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
        physical_refresh = evidence.get("physical_span_refresh") if isinstance(evidence.get("physical_span_refresh"), dict) else {}
        if physical_refresh.get("source") != "raw_layout_alignment":
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        candidate = _candidate_from_existing_row(row)
        if candidate is None:
            continue
        source_file = str(row.get("source_file") or candidate.source_file or "")
        if not source_file:
            continue
        candidate.source_file = source_file
        by_file[source_file].append(candidate)
        example_refs[candidate_key(candidate)] = str(row.get("example_ref") or candidate.example_id)
        stats["rows_scanned"] += 1

    if not by_file:
        return stats

    placeholder_refs = _ref_by_placeholder(rows)
    for source_file, candidates in sorted(by_file.items(), key=lambda item: natural_key(item[0])):
        path = structured_dir / source_file
        if not path.exists():
            continue
        before = read_json(path)
        before_blocks = before.get("blocks") if isinstance(before, dict) else []
        before_count = len(before_blocks) if isinstance(before_blocks, list) else 0
        result = replace_examples_in_file(path, candidates, example_refs, dry_run=dry_run)
        if result.get("replaced", 0) <= 0:
            continue
        stats["rows_rewritten"] += int(result.get("replaced", 0) or 0)
        stats["files_rewritten"] += 1
        stats["blocks_removed"] += int(result.get("removed_blocks", 0) or 0)
        remapped = result.get("remapped_indexes") if isinstance(result.get("remapped_indexes"), dict) else {}
        for row in rows:
            if str(row.get("source_file") or "") != source_file:
                continue
            candidate = _candidate_from_existing_row(row)
            if candidate is None:
                continue
            new_index = remapped.get(candidate_key(candidate))
            if new_index is None:
                continue
            row["start_block_index"] = new_index
            row["end_block_index"] = new_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            replacement["placeholder_block_index"] = new_index
            replacement["placeholder_source_file"] = source_file
            row["replacement"] = replacement
            metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
            metadata.pop("replacement_start_char", None)
            metadata.pop("replacement_end_char", None)
            row["metadata"] = metadata
        if before_count and not dry_run:
            updated = read_json(path)
            blocks = updated.get("blocks") if isinstance(updated, dict) else []
            if isinstance(blocks, list):
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                    content = str(block.get("content") or "").strip()
                    if content in placeholder_refs:
                        block["type"] = "example"
    return stats


def _has_current_example_callback_tail(example_id: str, content: str) -> bool:
    example_id = str(example_id or "").strip()
    if not example_id:
        return False
    for sentence in re.split(r"(?<=[.!?])\s+", str(content or "")):
        if looks_like_post_example_body({"label": "text", "content": sentence}, example_id):
            return True
    return False


def _content_mentions_numbered_table(content: str) -> bool:
    return bool(
        re.search(
            r"\bTable\s+(?:A\d+|\d+)\.\d+[A-Za-z]?\b",
            str(content or ""),
            flags=re.IGNORECASE,
        )
    )


def _raw_candidate_boundary_evidence(raw_item: ExampleCandidate, row: dict[str, Any]) -> dict[str, Any]:
    before_content = str(row.get("content_markdown") or "")
    before_plain = collapse_ws(strip_structured_refs(strip_html(before_content)))
    raw_plain = collapse_ws(strip_structured_refs(strip_html(raw_item.content_markdown)))
    before_words = len(before_plain.split())
    raw_words = len(raw_plain.split())
    evidence: dict[str, Any] = {
        "before_word_count": before_words,
        "raw_word_count": raw_words,
        "evidence_codes": [],
    }
    if before_words <= 0 or raw_words <= 0:
        return evidence
    if raw_words + 16 >= before_words:
        return evidence
    before_tables = {str(ref) for ref in (row.get("table_refs") or [])}
    raw_tables = set(raw_item.table_refs)
    removed_tables = sorted(before_tables - raw_tables)
    if removed_tables:
        evidence["removed_table_refs"] = removed_tables
    if before_tables - raw_tables and _content_mentions_numbered_table(before_content):
        evidence["evidence_codes"].append("clips_numbered_table_from_example_body")
    if raw_words >= 60 and before_words >= int(raw_words * 1.8):
        raw_head = normalize_match_text(" ".join(raw_plain.split()[:16]))
        before_head = normalize_match_text(" ".join(before_plain.split()[:24]))
        if raw_head and raw_head in before_head and re.search(r"[.!?]\s*$", raw_item.content_markdown.strip()):
            evidence["evidence_codes"].append("strong_shorter_raw_span_same_head_sentence_end")
    if raw_words < max(20, int(before_words * 0.88)):
        raw_tail = normalize_match_text(" ".join(raw_plain.split()[-12:]))
        before_norm = normalize_match_text(before_plain)
        tail_pos = before_norm.find(raw_tail) if raw_tail else -1
        if tail_pos >= 0:
            trailing = before_norm[tail_pos + len(raw_tail) :].strip()
            evidence["trailing_after_raw_tail"] = " ".join(trailing.split()[:36])
            if re.match(
                r"^(?:the|this|these|those|as|when|while|if|because|can|where|using|larger|smaller|a|an)\b",
                trailing,
                flags=re.IGNORECASE,
            ):
                evidence["evidence_codes"].append("trailing_body_paragraph_after_raw_tail")
            if re.match(r"^table\s+(?:a\d+|\d+)\.\d+\b", trailing, flags=re.IGNORECASE):
                evidence["evidence_codes"].append("trailing_numbered_table_after_raw_tail")
    evidence["evidence_codes"] = sorted(set(evidence["evidence_codes"]))
    return evidence


def _raw_candidate_is_boundary_improvement(raw_item: ExampleCandidate, row: dict[str, Any]) -> bool:
    return bool(_raw_candidate_boundary_evidence(raw_item, row).get("evidence_codes"))


def _raw_example_pages(project_root: Path, chapters: set[str]) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for chapter in sorted(chapters, key=chapter_sort_key):
        for record in ordered_paddle_records(project_root, chapter):
            match = raw_example_start_match(record.content)
            if not match:
                continue
            example_id = clean_example_id(match.group("example_id"))
            if example_id and (chapter, example_id) not in out:
                out[(chapter, example_id)] = record.page_index + 1
    return out


def _raw_example_positions(project_root: Path, chapters: set[str]) -> dict[tuple[str, str], dict[str, int]]:
    out: dict[tuple[str, str], dict[str, int]] = {}
    for chapter in sorted(chapters, key=chapter_sort_key):
        for order_index, record in enumerate(ordered_paddle_records(project_root, chapter)):
            match = raw_example_start_match(record.content)
            if not match:
                continue
            example_id = clean_example_id(match.group("example_id"))
            if example_id and (chapter, example_id) not in out:
                out[(chapter, example_id)] = {
                    "order": order_index,
                    "page": record.page_index + 1,
                    "row": record.row_index,
                }
    return out


def _shift_row_indexes_after_insert(
    rows: list[dict[str, Any]],
    source_file: str,
    insert_index: int,
    *,
    inserted_placeholder: str,
) -> None:
    for row in rows:
        if str(row.get("source_file") or "") != source_file:
            continue
        if str(row.get("placeholder") or "") == inserted_placeholder:
            continue
        start = _safe_block_index(row.get("start_block_index"))
        end = _safe_block_index(row.get("end_block_index"))
        if start is not None and start >= insert_index:
            row["start_block_index"] = start + 1
        if end is not None and end >= insert_index:
            row["end_block_index"] = end + 1
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        span = replacement.get("source_block_span")
        if isinstance(span, list) and len(span) == 2:
            replacement["source_block_span"] = [
                span[0] + 1 if span[0] >= insert_index else span[0],
                span[1] + 1 if span[1] >= insert_index else span[1],
            ]
            row["replacement"] = replacement


def _shift_row_indexes_after_remove(
    rows: list[dict[str, Any]],
    source_file: str,
    removed_index: int,
    *,
    removed_placeholder: str,
) -> None:
    for row in rows:
        if str(row.get("source_file") or "") != source_file:
            continue
        if str(row.get("placeholder") or "") == removed_placeholder:
            continue
        start = _safe_block_index(row.get("start_block_index"))
        end = _safe_block_index(row.get("end_block_index"))
        if start is not None and start > removed_index:
            row["start_block_index"] = start - 1
        if end is not None and end > removed_index:
            row["end_block_index"] = end - 1
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        span = replacement.get("source_block_span")
        if isinstance(span, list) and len(span) == 2:
            replacement["source_block_span"] = [
                span[0] - 1 if span[0] > removed_index else span[0],
                span[1] - 1 if span[1] > removed_index else span[1],
            ]
            row["replacement"] = replacement


def _append_placeholder_to_unit(
    structured_dir: Path,
    source_file: str,
    placeholder: str,
    *,
    dry_run: bool,
) -> int | None:
    path = structured_dir / source_file
    if not source_file or not path.is_file():
        return None
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return None
    if any(isinstance(block, dict) and str(block.get("content") or "") == placeholder for block in blocks):
        return None
    new_index = len(blocks)
    blocks.append({"type": "example", "content": placeholder})
    if not dry_run:
        write_json(path, data)
    return new_index


def _insert_placeholder_at_unit(
    structured_dir: Path,
    source_file: str,
    insert_index: int,
    placeholder: str,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> int | None:
    path = structured_dir / source_file
    if not source_file or not path.is_file():
        return None
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return None
    if any(isinstance(block, dict) and placeholder in str(block.get("content") or "") for block in blocks):
        found = _read_placeholder_position(structured_dir, source_file, placeholder)
        return found[0] if found is not None else None
    insert_index = min(max(insert_index, 0), len(blocks))
    blocks[insert_index:insert_index] = [{"type": "example", "content": placeholder}]
    _shift_row_indexes_after_insert(rows, source_file, insert_index, inserted_placeholder=placeholder)
    if not dry_run:
        write_json(path, data)
    return insert_index


def _remove_placeholder_from_unit(
    structured_dir: Path,
    source_file: str,
    placeholder: str,
    *,
    dry_run: bool,
) -> bool:
    path = structured_dir / source_file
    if not source_file or not path.is_file():
        return False
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return False
    changed = False
    new_blocks: list[Any] = []
    for block in blocks:
        if not isinstance(block, dict):
            new_blocks.append(block)
            continue
        content = str(block.get("content") or "")
        if content == placeholder:
            changed = True
            continue
        if placeholder in content:
            updated = collapse_ws(content.replace(placeholder, " "))
            if updated:
                new_block = dict(block)
                new_block["content"] = updated
                new_blocks.append(new_block)
            changed = True
            continue
        new_blocks.append(block)
    if not changed:
        return False
    data["blocks"] = new_blocks
    if not dry_run:
        write_json(path, data)
    return True


def _remove_placeholder_and_shift_rows(
    structured_dir: Path,
    source_file: str,
    placeholder: str,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> tuple[bool, int | None]:
    found = _read_placeholder_position(structured_dir, source_file, placeholder)
    removed_index = found[0] if found is not None else None
    changed = _remove_placeholder_from_unit(structured_dir, source_file, placeholder, dry_run=dry_run)
    if changed and removed_index is not None:
        _shift_row_indexes_after_remove(rows, source_file, removed_index, removed_placeholder=placeholder)
    return changed, removed_index


def _first_non_noise_raw_order_after(
    *,
    project_root: Path,
    chapter: str,
    raw_order: int,
) -> int | None:
    for order_index, record in enumerate(ordered_paddle_records(project_root, chapter)):
        if order_index <= raw_order:
            continue
        if record.label in PADDLE_PAGE_NOISE_LABELS:
            continue
        return order_index
    return None


def _unit_raw_order_score(
    *,
    project_root: Path,
    chapter: str,
    source_file: str,
    data: dict[str, Any],
) -> int | None:
    text = " ".join(str(block.get("content") or "") for block in data.get("blocks", []) if isinstance(block, dict))
    tokens = normalize_match_text(text).split()
    if len(tokens) < 6:
        return None
    anchors = [" ".join(tokens[offset : offset + 8]) for offset in (0, min(12, max(0, len(tokens) - 8)))]
    anchors = [anchor for anchor in anchors if anchor]
    best: int | None = None
    for order_index, record in enumerate(ordered_paddle_records(project_root, chapter)):
        record_norm = normalize_match_text(record.content)
        if not record_norm:
            continue
        if any(anchor in record_norm for anchor in anchors):
            best = order_index if best is None else min(best, order_index)
    if best is not None:
        return best

    stem = Path(source_file).stem
    match = re.search(r"_(\d+)$", stem)
    if match:
        return int(match.group(1)) * 10000
    return None


def _candidate_source_unit_for_raw_order(
    *,
    structured_dir: Path,
    project_root: Path,
    chapter: str,
    raw_order: int,
    after_previous_file: str | None = None,
    before_next_file: str | None = None,
) -> str | None:
    units: list[tuple[str, dict[str, Any], int]] = []
    for path in load_unit_files(structured_dir):
        try:
            data = read_json(path)
        except Exception:
            continue
        metadata = data.get("metadata") if isinstance(data, dict) else {}
        unit_chapter = str(metadata.get("chapter") or path.stem.split("_", 1)[0]).strip().lower()
        if unit_chapter != chapter:
            continue
        score = _unit_raw_order_score(project_root=project_root, chapter=chapter, source_file=path.name, data=data)
        if score is not None:
            units.append((path.name, data, score))
    if not units:
        return None
    units.sort(key=lambda item: (item[2], natural_key(item[0])))

    previous_key = natural_key(after_previous_file) if after_previous_file else None
    next_key = natural_key(before_next_file) if before_next_file else None
    next_raw_order = _first_non_noise_raw_order_after(project_root=project_root, chapter=chapter, raw_order=raw_order)
    candidates: list[tuple[int, tuple[Any, ...], str]] = []
    for file_name, data, score in units:
        file_key = natural_key(file_name)
        if previous_key is not None and file_key < previous_key:
            continue
        if next_key is not None and file_key > next_key:
            continue
        if score < raw_order:
            distance = raw_order - score
            # A preceding unit is a good landing zone when it is close enough to
            # the raw start and no intervening non-noise row has already moved on.
            if next_raw_order is not None and score >= next_raw_order:
                continue
            candidates.append((distance, tuple(file_key), file_name))
        elif score == raw_order:
            candidates.append((0, tuple(file_key), file_name))
    if not candidates:
        after = [(score - raw_order, tuple(natural_key(file_name)), file_name) for file_name, _, score in units if score >= raw_order]
        candidates = after
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def _is_example_heading_unit(data: dict[str, Any]) -> bool:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    for key in ("display_heading", "section_level_2"):
        value = str(metadata.get(key) or "").strip()
        if EXAMPLE_TITLE_PREFIX_RE.match(value):
            return True
    heading_path = metadata.get("heading_path") if isinstance(metadata.get("heading_path"), list) else []
    return any(EXAMPLE_TITLE_PREFIX_RE.match(str(item or "").strip()) for item in heading_path)


def _clean_example_heading_metadata(data: dict[str, Any]) -> None:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    if not metadata:
        return
    for key in ("display_heading", "section_level_2"):
        value = str(metadata.get(key) or "").strip()
        if EXAMPLE_TITLE_PREFIX_RE.match(value):
            metadata.pop(key, None)
    subsections = metadata.get("subsections") if isinstance(metadata.get("subsections"), list) else []
    subsections = [item for item in subsections if not EXAMPLE_TITLE_PREFIX_RE.match(str(item or "").strip())]
    if subsections:
        metadata["subsections"] = subsections
        metadata.setdefault("section_level_2", str(subsections[-1]))
        metadata.setdefault("display_heading", str(subsections[-1]))
    else:
        metadata["subsections"] = []
    heading_path = metadata.get("heading_path") if isinstance(metadata.get("heading_path"), list) else []
    heading_path = [item for item in heading_path if not EXAMPLE_TITLE_PREFIX_RE.match(str(item or "").strip())]
    if heading_path:
        metadata["heading_path"] = heading_path
        fallback = str(heading_path[-1] or "").strip()
        if fallback:
            metadata.setdefault("display_heading", fallback)
    else:
        metadata.pop("heading_path", None)
    if not metadata.get("display_heading"):
        fallback = str(metadata.get("section_level_2") or metadata.get("section_level_1") or metadata.get("section") or "").strip()
        if fallback:
            metadata["display_heading"] = fallback
    data["metadata"] = metadata


def _blocks_after_example_heading_unit_span(blocks: list[Any], raw_row: dict[str, Any]) -> list[Any]:
    raw_text = str(raw_row.get("content_plain") or raw_row.get("content_markdown") or "")
    raw_tokens = [token for token, _, _ in _token_spans(raw_text)]
    raw_norm = normalize_match_text(raw_text)
    if not raw_tokens or not raw_norm:
        return []

    consumed = 0
    saw_example_body = False
    for block in blocks:
        if not isinstance(block, dict):
            if saw_example_body:
                break
            consumed += 1
            continue
        content = str(block.get("content") or "")
        content_norm = normalize_match_text(content)
        if not content_norm:
            consumed += 1
            continue
        block_matches_raw = content_norm in raw_norm or _block_anchor_in_raw(
            content,
            raw_tokens,
            min_anchor_tokens=4,
        )
        if block_matches_raw:
            consumed += 1
            saw_example_body = True
            continue
        if saw_example_body:
            break
        # If the first block is a formula fragment or badly OCR-split short
        # text, avoid preserving what is probably example body duplication.
        if len(content_norm.split()) < 4:
            consumed += 1
            continue
        break
    if not saw_example_body:
        return []
    return blocks[consumed:]


def _build_raw_rows_by_identity(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    raw_positions: dict[tuple[str, str], dict[str, int]],
) -> dict[tuple[str, str], dict[str, Any]]:
    by_chapter: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if chapter and example_id and (chapter, example_id) in raw_positions:
            by_chapter[chapter].add(example_id)
    out: dict[tuple[str, str], dict[str, Any]] = {}
    context = build_structured_context(structured_dir)
    for chapter, example_ids in sorted(by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(),
            target_ids=example_ids,
            skip_structured_matches=False,
        )
        for item in raw_items:
            out[(chapter, item.example_id)] = _make_row_from_candidate(item, example_ref=item.example_id)
    return out


def _replace_row_payload_from_raw(
    row: dict[str, Any],
    raw_row: dict[str, Any],
    *,
    source_file: str,
    block_index: int,
    reason: str,
) -> None:
    keep_ref = str(row.get("example_ref") or raw_row.get("example_ref") or row.get("example_id") or "")
    keep_placeholder = str(row.get("placeholder") or f"[[SEE_EXAMPLE:{keep_ref}]]")
    for key in (
        "label",
        "title",
        "content_markdown",
        "content_plain",
        "formula_refs",
        "table_refs",
        "figure_refs",
        "external_refs",
        "metadata",
        "evidence",
    ):
        if key in raw_row:
            row[key] = raw_row[key]
    row["example_ref"] = keep_ref
    row["placeholder"] = keep_placeholder
    row["source_file"] = source_file
    row["start_block_index"] = block_index
    row["end_block_index"] = block_index
    raw_metadata = raw_row.get("metadata") if isinstance(raw_row.get("metadata"), dict) else {}
    source_span = _coerce_block_span(raw_metadata.get("source_block_span"))
    if source_span is None:
        raw_replacement = raw_row.get("replacement") if isinstance(raw_row.get("replacement"), dict) else {}
        source_span = _coerce_block_span(raw_replacement.get("source_block_span"))
    if source_span is None:
        source_span = [block_index, block_index]
    replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
    row["replacement"] = {
        **replacement,
        "status": "replaced",
        "reason": "placeholder_block_written",
        "source_block_span": source_span,
        "placeholder_block_index": block_index,
        "placeholder_source_file": source_file,
    }
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    row["metadata"] = {
        **metadata,
        "raw_layout_order_anchor": True,
        "source_block_span": source_span,
    }
    evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
    row["evidence"] = {
        **evidence,
        "existing_library_repair": reason,
        "source_file_recomputed_from_raw_order": source_file,
    }


def _repair_example_heading_units_from_raw_order(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    raw_positions: dict[tuple[str, str], dict[str, int]],
    raw_rows: dict[tuple[str, str], dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {"units_scanned": 0, "heading_units_repaired": 0, "placeholders_moved": 0}
    rows_by_identity = {
        (str(row.get("chapter") or "").strip().lower(), str(row.get("example_id") or "").strip()): row
        for row in rows
        if isinstance(row, dict)
    }
    for path in load_unit_files(structured_dir):
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        stats["units_scanned"] += 1
        if not _is_example_heading_unit(data):
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        heading_text = " ".join(str(metadata.get(key) or "") for key in ("display_heading", "section_level_2"))
        match = EXAMPLE_TITLE_PREFIX_RE.search(heading_text)
        if not match:
            continue
        chapter = str(metadata.get("chapter") or path.stem.split("_", 1)[0]).strip().lower()
        example_id = clean_example_id(match.group("example_id"))
        row = rows_by_identity.get((chapter, example_id))
        raw_row = raw_rows.get((chapter, example_id))
        if row is None or raw_row is None or (chapter, example_id) not in raw_positions:
            continue
        placeholder = str(row.get("placeholder") or f"[[SEE_EXAMPLE:{row.get('example_ref') or example_id}]]")
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        if not isinstance(blocks, list):
            continue
        _remove_placeholder_and_shift_rows(
            structured_dir,
            str(row.get("source_file") or ""),
            placeholder,
            rows,
            dry_run=dry_run,
        )
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        trailing_blocks = _blocks_after_example_heading_unit_span(blocks, raw_row)
        _clean_example_heading_metadata(data)
        data["blocks"] = [{"type": "example", "content": placeholder}, *trailing_blocks]
        if not dry_run:
            write_json(path, data)
        _replace_row_payload_from_raw(
            row,
            raw_row,
            source_file=path.name,
            block_index=0,
            reason="example_heading_unit_repaired_from_raw_order",
        )
        stats["heading_units_repaired"] += 1
        stats["placeholders_moved"] += 1
    return stats


def _rewrite_same_file_example_placeholder_order(
    *,
    structured_dir: Path,
    source_file: str,
    ordered_placeholders: list[str],
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> bool:
    path = structured_dir / source_file
    if not path.exists() or not ordered_placeholders:
        return False
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return False
    wanted = set(ordered_placeholders)
    example_indexes: list[int] = []
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        content = str(block.get("content") or "")
        if content in wanted and str(block.get("type") or "").strip().lower() == "example":
            example_indexes.append(index)
    if len(example_indexes) != len(ordered_placeholders):
        return False
    current = [str(blocks[index].get("content") or "") for index in example_indexes if isinstance(blocks[index], dict)]
    if current == ordered_placeholders:
        return False
    for block_index, placeholder in zip(example_indexes, ordered_placeholders):
        blocks[block_index] = {"type": "example", "content": placeholder}
        for row in rows:
            if str(row.get("source_file") or "") != source_file:
                continue
            if str(row.get("placeholder") or "") != placeholder:
                continue
            row["start_block_index"] = block_index
            row["end_block_index"] = block_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            row["replacement"] = {
                **replacement,
                "placeholder_block_index": block_index,
                "placeholder_source_file": source_file,
            }
            evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row["evidence"] = {
                **evidence,
                "existing_library_repair": "raw_layout_same_file_order_rewritten",
            }
    if not dry_run:
        write_json(path, data)
    return True


def _previous_next_raw_rows(
    ordered_rows: list[dict[str, Any]],
    index: int,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    previous_row = ordered_rows[index - 1] if index > 0 else None
    next_row = ordered_rows[index + 1] if index + 1 < len(ordered_rows) else None
    return previous_row, next_row


def _row_placeholder_is_present_in_source(
    structured_dir: Path,
    row: dict[str, Any],
) -> bool:
    return (
        _read_placeholder_position(
            structured_dir,
            str(row.get("source_file") or ""),
            str(row.get("placeholder") or ""),
        )
        is not None
    )


def _source_file_distance(left: str, right: str) -> int | None:
    left_match = re.search(r"_(\d+)\.json$", str(left or ""), flags=re.IGNORECASE)
    right_match = re.search(r"_(\d+)\.json$", str(right or ""), flags=re.IGNORECASE)
    if not left_match or not right_match:
        return None
    return abs(int(left_match.group(1)) - int(right_match.group(1)))


def _should_relocate_raw_order_target(
    *,
    structured_dir: Path,
    target_row: dict[str, Any],
    source_file: str,
) -> bool:
    """Gate cross-unit raw-order moves to cases with strong placement evidence.

    Raw layout order is excellent evidence for example sequence, but too weak
    by itself to move an already materialized placeholder across unrelated
    section units.  Keep those stable and let raw-layout refresh update content
    spans; only relocate when the placeholder is missing or the current unit is
    clearly an example-heading unit that should be repaired elsewhere.
    """

    current_file = str(target_row.get("source_file") or "")
    if not current_file or current_file == source_file:
        return True
    if not _row_placeholder_is_present_in_source(structured_dir, target_row):
        return True
    current_path = structured_dir / current_file
    try:
        current_data = read_json(current_path)
    except Exception:
        current_data = {}
    if isinstance(current_data, dict) and _is_example_heading_unit(current_data):
        return True
    distance = _source_file_distance(current_file, source_file)
    if distance is not None and distance > 1:
        return False
    evidence = target_row.get("evidence") if isinstance(target_row.get("evidence"), dict) else {}
    replacement = target_row.get("replacement") if isinstance(target_row.get("replacement"), dict) else {}
    if evidence.get("raw_layout_order_anchor") or replacement.get("status") == "replaced":
        return False
    return True


def _repair_raw_layout_example_order(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "rows_scanned": 0,
        "inversions_found": 0,
        "rows_relocated": 0,
        "heading_units_repaired": 0,
        "placeholders_moved": 0,
    }
    chapters = {str(row.get("chapter") or "").strip().lower() for row in rows if isinstance(row, dict)}
    chapters = {chapter for chapter in chapters if chapter}
    raw_positions = _raw_example_positions(project_root, chapters)
    if not raw_positions:
        return stats
    raw_rows = _build_raw_rows_by_identity(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        raw_positions=raw_positions,
    )
    heading_stats = _repair_example_heading_units_from_raw_order(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        raw_positions=raw_positions,
        raw_rows=raw_rows,
        dry_run=dry_run,
    )
    stats["heading_units_repaired"] += heading_stats["heading_units_repaired"]
    stats["placeholders_moved"] += heading_stats["placeholders_moved"]

    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if chapter and (chapter, example_id) in raw_positions:
            by_chapter[chapter].append(row)

    for chapter, chapter_rows in by_chapter.items():
        ordered_rows = sorted(
            chapter_rows,
            key=lambda row: (
                raw_positions[(chapter, str(row.get("example_id") or "").strip())]["order"],
                natural_key(str(row.get("example_id") or row.get("example_ref") or "")),
            ),
        )
        changed = True
        while changed:
            changed = False
            positions: list[tuple[dict[str, Any], tuple[Any, int, int] | None]] = []
            for row in ordered_rows:
                stats["rows_scanned"] += 1
                found = _read_placeholder_position(
                    structured_dir,
                    str(row.get("source_file") or ""),
                    str(row.get("placeholder") or ""),
                )
                if found is None:
                    positions.append((row, None))
                else:
                    positions.append((row, _structured_position_sort_key(str(row.get("source_file") or ""), found[0], found[1])))
            for index, ((row, position), (_, next_position)) in enumerate(zip(positions, positions[1:])):
                if position is None or next_position is None or position <= next_position:
                    continue
                stats["inversions_found"] += 1
                next_row = positions[index + 1][0]
                same_file_span: list[dict[str, Any]] = []
                source_file = str(row.get("source_file") or "")
                if source_file and source_file == str(next_row.get("source_file") or ""):
                    left = index
                    while left > 0 and str(positions[left - 1][0].get("source_file") or "") == source_file:
                        left -= 1
                    right = index + 1
                    while right + 1 < len(positions) and str(positions[right + 1][0].get("source_file") or "") == source_file:
                        right += 1
                    same_file_span = [positions[item][0] for item in range(left, right + 1)]
                if same_file_span:
                    ordered_placeholders = [str(item.get("placeholder") or "") for item in same_file_span if str(item.get("placeholder") or "")]
                    if len(ordered_placeholders) == len(same_file_span) and _rewrite_same_file_example_placeholder_order(
                        structured_dir=structured_dir,
                        source_file=source_file,
                        ordered_placeholders=ordered_placeholders,
                        rows=rows,
                        dry_run=dry_run,
                    ):
                        stats["rows_relocated"] += 1
                        stats["placeholders_moved"] += len(ordered_placeholders)
                        changed = True
                        break
                last_target_index = len(positions) - 1
                if index == 0:
                    preferred_targets = [index]
                elif index + 1 == last_target_index:
                    preferred_targets = [index + 1]
                else:
                    preferred_targets = [index + 1, index]
                row_source = str(row.get("source_file") or "")
                next_source = str(next_row.get("source_file") or "")
                if row_source and next_source and row_source == next_source and 0 < index and index + 1 < last_target_index:
                    preferred_targets = [index, index + 1]
                for target_index in preferred_targets:
                    target_row = positions[target_index][0]
                    example_id = str(target_row.get("example_id") or "").strip()
                    raw_pos = raw_positions.get((chapter, example_id))
                    raw_row = raw_rows.get((chapter, example_id))
                    placeholder = str(target_row.get("placeholder") or f"[[SEE_EXAMPLE:{target_row.get('example_ref') or example_id}]]")
                    if raw_pos is None or raw_row is None or not placeholder:
                        continue
                    previous_row, following_row = _previous_next_raw_rows(ordered_rows, target_index)
                    previous_file = str(previous_row.get("source_file") or "") if previous_row is not None else None
                    following_file = str(following_row.get("source_file") or "") if following_row is not None else None
                    source_file = _candidate_source_unit_for_raw_order(
                        structured_dir=structured_dir,
                        project_root=project_root,
                        chapter=chapter,
                        raw_order=raw_pos["order"],
                        after_previous_file=previous_file,
                        before_next_file=following_file,
                    )
                    if not source_file:
                        continue
                    current_file_key = natural_key(str(target_row.get("source_file") or ""))
                    source_file_key = natural_key(source_file)
                    if previous_file and source_file_key < natural_key(previous_file):
                        continue
                    if following_file and source_file_key > natural_key(following_file):
                        continue
                    if source_file_key == current_file_key and str(target_row.get("source_file") or "") != source_file:
                        continue
                    if not _should_relocate_raw_order_target(
                        structured_dir=structured_dir,
                        target_row=target_row,
                        source_file=source_file,
                    ):
                        continue
                    original_file = str(target_row.get("source_file") or "")
                    original_found = _read_placeholder_position(structured_dir, original_file, placeholder)
                    changed_removed, removed_index = _remove_placeholder_and_shift_rows(
                        structured_dir,
                        original_file,
                        placeholder,
                        rows,
                        dry_run=dry_run,
                    )
                    if changed_removed:
                        stats["placeholders_moved"] += 1
                    target_path = structured_dir / source_file
                    if not target_path.exists():
                        continue
                    target_data = read_json(target_path)
                    target_blocks = target_data.get("blocks") if isinstance(target_data.get("blocks"), list) else []
                    insert_index = len(target_blocks) if isinstance(target_blocks, list) else 0
                    if previous_row is not None and str(previous_row.get("source_file") or "") == source_file:
                        previous_found = _read_placeholder_position(structured_dir, source_file, str(previous_row.get("placeholder") or ""))
                        if previous_found is not None:
                            insert_index = previous_found[0] + 1
                    elif following_row is not None and str(following_row.get("source_file") or "") == source_file:
                        following_found = _read_placeholder_position(structured_dir, source_file, str(following_row.get("placeholder") or ""))
                        if following_found is not None:
                            insert_index = following_found[0]
                    new_index = _insert_placeholder_at_unit(
                        structured_dir,
                        source_file,
                        insert_index,
                        placeholder,
                        rows,
                        dry_run=dry_run,
                    )
                    if new_index is None:
                        if changed_removed and original_found is not None:
                            _insert_placeholder_at_unit(
                                structured_dir,
                                original_file,
                                removed_index if removed_index is not None else original_found[0],
                                placeholder,
                                rows,
                                dry_run=dry_run,
                            )
                        continue
                    _replace_row_payload_from_raw(
                        target_row,
                        raw_row,
                        source_file=source_file,
                        block_index=new_index,
                        reason="raw_layout_global_order_relocated",
                    )
                    target_row["evidence"]["raw_order"] = raw_pos["order"]
                    target_row["evidence"]["raw_source_page"] = raw_pos["page"]
                    if original_file and original_file != source_file:
                        target_row["evidence"]["relocated_from_source_file"] = original_file
                    stats["rows_relocated"] += 1
                    stats["placeholders_moved"] += 1
                    changed = True
                    break
                if changed:
                    break
    if (stats["rows_relocated"] or stats["heading_units_repaired"]) and not dry_run:
        write_example_library(structured_dir, rows)
    return stats


def _read_placeholder_position(structured_dir: Path, source_file: str, placeholder: str) -> tuple[int, int] | None:
    path = structured_dir / source_file
    if not source_file or not path.is_file():
        return None
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return None
    for block_index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        content = str(block.get("content") or "")
        char_index = content.find(placeholder)
        if char_index >= 0:
            return block_index, char_index
    return None


def _structured_position_sort_key(source_file: str, block_index: int | None, char_index: int = 0) -> tuple[Any, int, int]:
    return natural_key(str(source_file or "")), block_index if block_index is not None else 10**9, char_index


def _insert_placeholder_after_unit(
    structured_dir: Path,
    source_file: str,
    after_block_index: int,
    placeholder: str,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> int | None:
    path = structured_dir / source_file
    if not source_file or not path.is_file():
        return None
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return None
    if any(isinstance(block, dict) and placeholder in str(block.get("content") or "") for block in blocks):
        found = _read_placeholder_position(structured_dir, source_file, placeholder)
        return found[0] if found is not None else None
    insert_index = min(max(after_block_index + 1, 0), len(blocks))
    blocks[insert_index:insert_index] = [{"type": "example", "content": placeholder}]
    for row in rows:
        if str(row.get("source_file") or "") != source_file:
            continue
        if str(row.get("placeholder") or "") == placeholder:
            continue
        start = _safe_block_index(row.get("start_block_index"))
        end = _safe_block_index(row.get("end_block_index"))
        if start is not None and start >= insert_index:
            row["start_block_index"] = start + 1
        if end is not None and end >= insert_index:
            row["end_block_index"] = end + 1
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        span = replacement.get("source_block_span")
        if isinstance(span, list) and len(span) == 2:
            replacement["source_block_span"] = [
                span[0] + 1 if span[0] >= insert_index else span[0],
                span[1] + 1 if span[1] >= insert_index else span[1],
            ]
            row["replacement"] = replacement
    if not dry_run:
        write_json(path, data)
    return insert_index


def _repair_nonmonotonic_existing_example_order(
    *,
    structured_dir: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {"rows_scanned": 0, "rows_relocated": 0, "placeholders_moved": 0}
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if chapter and _example_number_parts(example_id) is not None:
            by_chapter[chapter].append(row)

    for _chapter, chapter_rows in by_chapter.items():
        ordered_rows = sorted(
            chapter_rows,
            key=lambda row: natural_key(str(row.get("example_id") or row.get("example_ref") or "")),
        )
        previous_row: dict[str, Any] | None = None
        previous_position: tuple[Any, int, int] | None = None
        for row in ordered_rows:
            stats["rows_scanned"] += 1
            source_file = str(row.get("source_file") or "")
            placeholder = str(row.get("placeholder") or "")
            if not source_file or not placeholder:
                continue
            found = _read_placeholder_position(structured_dir, source_file, placeholder)
            if found is None:
                continue
            block_index, char_index = found
            current_position = _structured_position_sort_key(source_file, block_index, char_index)
            if previous_row is None or previous_position is None:
                previous_row = row
                previous_position = current_position
                continue
            if current_position >= previous_position:
                previous_row = row
                previous_position = current_position
                continue

            previous_source_file = str(previous_row.get("source_file") or "")
            previous_placeholder = str(previous_row.get("placeholder") or "")
            previous_found = _read_placeholder_position(structured_dir, previous_source_file, previous_placeholder)
            if previous_found is None:
                previous_row = row
                previous_position = current_position
                continue
            if previous_source_file != source_file and not _should_relocate_raw_order_target(
                structured_dir=structured_dir,
                target_row=row,
                source_file=previous_source_file,
            ):
                previous_row = row
                previous_position = current_position
                continue
            original_source_file = source_file
            original_block_index = block_index
            if _remove_placeholder_from_unit(structured_dir, source_file, placeholder, dry_run=dry_run):
                stats["placeholders_moved"] += 1
                for other_row in rows:
                    if str(other_row.get("source_file") or "") != original_source_file:
                        continue
                    if str(other_row.get("placeholder") or "") == placeholder:
                        continue
                    other_start = _safe_block_index(other_row.get("start_block_index"))
                    other_end = _safe_block_index(other_row.get("end_block_index"))
                    if other_start is not None and other_start > original_block_index:
                        other_row["start_block_index"] = other_start - 1
                    if other_end is not None and other_end > original_block_index:
                        other_row["end_block_index"] = other_end - 1
                    other_replacement = other_row.get("replacement") if isinstance(other_row.get("replacement"), dict) else {}
                    other_span = other_replacement.get("source_block_span")
                    if isinstance(other_span, list) and len(other_span) == 2:
                        other_replacement["source_block_span"] = [
                            other_span[0] - 1 if other_span[0] > original_block_index else other_span[0],
                            other_span[1] - 1 if other_span[1] > original_block_index else other_span[1],
                        ]
                        other_row["replacement"] = other_replacement
            insert_index = _insert_placeholder_after_unit(
                structured_dir,
                previous_source_file,
                previous_found[0],
                placeholder,
                rows,
                dry_run=dry_run,
            )
            if insert_index is None:
                previous_row = row
                previous_position = current_position
                continue
            row["source_file"] = previous_source_file
            row["start_block_index"] = insert_index
            row["end_block_index"] = insert_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            row["replacement"] = {
                **replacement,
                "placeholder_block_index": insert_index,
                "placeholder_source_file": previous_source_file,
            }
            evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row["evidence"] = {
                **evidence,
                "existing_library_repair": "nonmonotonic_placeholder_order_relocated",
                "relocated_from_source_file": source_file,
            }
            stats["rows_relocated"] += 1
            stats["placeholders_moved"] += 1
            previous_row = row
            previous_position = _structured_position_sort_key(previous_source_file, insert_index, 0)
    if stats["rows_relocated"] and not dry_run:
        write_example_library(structured_dir, rows)
    return stats


def _relocate_out_of_order_existing_examples(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {"rows_scanned": 0, "rows_relocated": 0, "placeholders_moved": 0}
    chapters = {str(row.get("chapter") or "").strip().lower() for row in rows if isinstance(row, dict)}
    chapters = {chapter for chapter in chapters if chapter}
    raw_pages = _raw_example_pages(project_root, chapters)
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, dict):
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        if chapter:
            by_chapter[chapter].append(row)

    context = build_structured_context(structured_dir)
    for chapter, chapter_rows in by_chapter.items():
        ordered_rows = sorted(
            chapter_rows,
            key=lambda row: natural_key(str(row.get("example_id") or row.get("example_ref") or "")),
        )
        for prev_row, row, next_row in zip(ordered_rows, ordered_rows[1:], ordered_rows[2:]):
            stats["rows_scanned"] += 1
            example_id = str(row.get("example_id") or row.get("example_ref") or "").strip()
            prev_page = raw_pages.get((chapter, str(prev_row.get("example_id") or "").strip()))
            page = raw_pages.get((chapter, example_id))
            next_page = raw_pages.get((chapter, str(next_row.get("example_id") or "").strip()))
            if page is None or prev_page is None or next_page is None:
                continue
            if not (prev_page <= page <= next_page):
                continue
            if page > prev_page + 1 or next_page < page + 3:
                continue
            prev_file = str(prev_row.get("source_file") or "")
            current_file = str(row.get("source_file") or "")
            next_file = str(next_row.get("source_file") or "")
            if not prev_file or not current_file:
                continue
            if current_file == prev_file:
                continue
            if current_file != next_file:
                continue
            placeholder = str(row.get("placeholder") or f"[[SEE_EXAMPLE:{row.get('example_ref') or example_id}]]")
            if not placeholder:
                continue
            next_placeholder = str(next_row.get("placeholder") or "")
            current_path = structured_dir / current_file
            if not current_path.exists():
                continue
            current_data = read_json(current_path)
            current_blocks = current_data.get("blocks") if isinstance(current_data, dict) else None
            if not isinstance(current_blocks, list) or not any(
                isinstance(block, dict)
                and placeholder in str(block.get("content") or "")
                and next_placeholder
                and next_placeholder in str(block.get("content") or "")
                for block in current_blocks
            ):
                continue
            if _remove_placeholder_from_unit(structured_dir, current_file, placeholder, dry_run=dry_run):
                stats["placeholders_moved"] += 1
            new_index = _append_placeholder_to_unit(structured_dir, prev_file, placeholder, dry_run=dry_run)
            if new_index is not None:
                stats["placeholders_moved"] += 1
            row["source_file"] = prev_file
            row["start_block_index"] = new_index
            row["end_block_index"] = new_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            row["replacement"] = {
                **replacement,
                "placeholder_block_index": new_index,
                "placeholder_source_file": prev_file,
            }
            evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row["evidence"] = {
                **evidence,
                "existing_library_repair": "raw_order_placeholder_relocated",
                "raw_source_page": page,
                "relocated_from_source_file": current_file,
            }
            stats["rows_relocated"] += 1
    if stats["rows_relocated"] and not dry_run:
        write_example_library(structured_dir, rows)
    return stats


def _repair_sequence_gap_neighbor_insert_placeholders(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "rows_scanned": 0,
        "rows_relocated": 0,
        "visual_stop_matches": 0,
        "page_distance_matches": 0,
        "placeholders_moved": 0,
    }
    chapters = {str(row.get("chapter") or "").strip().lower() for row in rows if isinstance(row, dict)}
    chapters = {chapter for chapter in chapters if chapter}
    raw_pages = _raw_example_pages(project_root, chapters)
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, dict):
            continue
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or row.get("example_ref") or "").strip()
        if not chapter or _example_number_parts(example_id) is None:
            continue
        by_chapter[chapter].append(row)

    changed = False
    for chapter, chapter_rows in by_chapter.items():
        ordered_rows = sorted(
            chapter_rows,
            key=lambda row: natural_key(str(row.get("example_id") or row.get("example_ref") or "")),
        )
        for index, row in enumerate(ordered_rows):
            metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
            evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            if not metadata.get("sequence_gap_neighbor_insert"):
                continue
            if evidence.get("detection_method") != "sequence_gap_raw_layout_neighbor_insert_placeholder":
                continue
            if index == 0:
                continue
            previous_row = ordered_rows[index - 1]
            next_row = ordered_rows[index + 1] if index + 1 < len(ordered_rows) else None
            stats["rows_scanned"] += 1
            previous_file = str(previous_row.get("source_file") or "")
            if not previous_file:
                continue
            previous_replacement = (
                previous_row.get("replacement") if isinstance(previous_row.get("replacement"), dict) else {}
            )
            previous_placeholder_index = _safe_block_index(previous_replacement.get("placeholder_block_index"))
            if previous_placeholder_index is None:
                previous_placeholder_index = _safe_block_index(previous_row.get("start_block_index"))
            if previous_placeholder_index is None:
                continue

            reason: str | None = None
            if _row_visual_stop_mentions_target(previous_row, row):
                reason = "previous_visual_stop_mentions_target"
                stats["visual_stop_matches"] += 1
            else:
                target_page = _row_source_page(row, raw_pages)
                previous_page = _row_source_page(previous_row, raw_pages)
                next_page = _row_source_page(next_row, raw_pages) if next_row is not None else None
                previous_distance = (
                    abs(target_page - previous_page)
                    if target_page is not None and previous_page is not None
                    else None
                )
                next_distance = (
                    abs(target_page - next_page)
                    if target_page is not None and next_page is not None
                    else None
                )
                if previous_distance is not None and (
                    (next_distance is not None and previous_distance < next_distance)
                    or (next_distance is None and previous_distance <= 1)
                ):
                    reason = "previous_neighbor_has_smaller_page_distance"
                    stats["page_distance_matches"] += 1
            if reason is None:
                continue

            placeholder = _example_placeholder_for_row(row)
            if not placeholder:
                continue
            current_replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            current_file = str(current_replacement.get("placeholder_source_file") or row.get("source_file") or "")
            current_found = _read_placeholder_position(structured_dir, current_file, placeholder)
            if current_file == previous_file and current_found is not None and current_found[0] == previous_placeholder_index + 1:
                continue

            original_file = current_file
            original_found = current_found
            removed, removed_index = _remove_placeholder_and_shift_rows(
                structured_dir,
                current_file,
                placeholder,
                rows,
                dry_run=dry_run,
            )
            if removed:
                stats["placeholders_moved"] += 1
            previous_found = _read_placeholder_position(
                structured_dir,
                previous_file,
                _example_placeholder_for_row(previous_row),
            )
            if previous_found is not None:
                previous_placeholder_index = previous_found[0]
            insert_index = _insert_placeholder_at_unit(
                structured_dir,
                previous_file,
                previous_placeholder_index + 1,
                placeholder,
                rows,
                dry_run=dry_run,
            )
            if insert_index is None:
                if removed and original_file and original_found is not None:
                    _insert_placeholder_at_unit(
                        structured_dir,
                        original_file,
                        removed_index if removed_index is not None else original_found[0],
                        placeholder,
                        rows,
                        dry_run=dry_run,
                    )
                continue

            row["source_file"] = previous_file
            row["start_block_index"] = insert_index
            row["end_block_index"] = insert_index
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            row["replacement"] = {
                **replacement,
                "status": replacement.get("status") or "replaced",
                "reason": replacement.get("reason") or "placeholder_block_written",
                "placeholder_block_index": insert_index,
                "placeholder_source_file": previous_file,
                "source_block_span": [insert_index, insert_index],
            }
            row_metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
            row["metadata"] = {
                **row_metadata,
                "sequence_gap_neighbor_insert": True,
                "sequence_gap_neighbor_insert_reason": reason,
            }
            row_evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row["evidence"] = {
                **row_evidence,
                "existing_library_repair": "sequence_gap_neighbor_relocated",
                "sequence_gap_neighbor_relocation_reason": reason,
                "relocated_from_source_file": original_file,
            }
            stats["rows_relocated"] += 1
            stats["placeholders_moved"] += 1
            changed = True
    if changed and not dry_run:
        write_example_library(structured_dir, rows)
    return stats


def _refresh_existing_rows_from_raw_layout(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, int]:
    stats = {
        "chapters_scanned": 0,
        "raw_candidates": 0,
        "rows_replaced": 0,
        "rows_physical_span_refreshed": 0,
        "rows_improved_with_tables": 0,
        "rows_boundary_clipped": 0,
        "replacement_reason_counts": {},
        "boundary_evidence_counts": {},
        "review_queue_count": 0,
    }
    replacement_reason_counts: Counter[str] = Counter()
    boundary_evidence_counts: Counter[str] = Counter()
    review_queue: list[dict[str, Any]] = []
    by_chapter: dict[str, set[str]] = defaultdict(set)
    rows_by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        if not chapter or not example_id:
            continue
        by_chapter[chapter].add(example_id)
        rows_by_identity[(chapter, example_id)] = row

    context = build_structured_context(structured_dir)
    for chapter, example_ids in sorted(by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        stats["chapters_scanned"] += 1
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(),
            target_ids=example_ids,
            skip_structured_matches=False,
        )
        stats["raw_candidates"] += len(raw_items)
        for raw_item in raw_items:
            row = rows_by_identity.get((chapter, raw_item.example_id))
            if row is None:
                continue
            before_content = str(row.get("content_markdown") or "")
            before_plain = collapse_ws(strip_structured_refs(strip_html(before_content)))
            before_tables = {str(ref) for ref in (row.get("table_refs") or [])}
            raw_tables = set(raw_item.table_refs)
            boundary_evidence = _raw_candidate_boundary_evidence(raw_item, row)
            should_replace = False
            reason = "raw_layout_existing_library_refresh"
            evidence_patch: dict[str, Any] = {}
            raw_evidence = raw_item.evidence if isinstance(raw_item.evidence, dict) else {}
            raw_has_visual_stop = bool(raw_evidence.get("visual_stop_clipped"))
            if (
                raw_has_visual_stop
                and len(raw_item.content_plain.split()) + 8 < len(before_plain.split())
            ):
                should_replace = True
                stats["rows_boundary_clipped"] += 1
                reason = "raw_layout_pdf_rule_boundary_refresh"
                evidence_patch = {
                    "raw_layout_refresh": {
                        "evidence_codes": ["pdf_rendered_horizontal_rule_clips_example"],
                        "before_word_count": len(before_plain.split()),
                        "raw_word_count": len(raw_item.content_plain.split()),
                        "visual_stop_source": raw_evidence.get("visual_stop_source"),
                        "visual_stop_page": raw_evidence.get("visual_stop_page"),
                        "visual_stop_row_index": raw_evidence.get("visual_stop_row_index"),
                        "visual_stop_rule_bbox": raw_evidence.get("visual_stop_rule_bbox"),
                    }
                }
            elif raw_tables - before_tables:
                should_replace = True
                stats["rows_improved_with_tables"] += 1
                reason = "raw_layout_table_placeholders_added"
                evidence_patch = {
                    "raw_layout_refresh": {
                        "evidence_codes": ["adds_missing_table_placeholders"],
                        "before_word_count": len(before_plain.split()),
                        "raw_word_count": len(raw_item.content_plain.split()),
                        "added_table_refs": sorted(raw_tables - before_tables),
                    }
                }
            elif (
                len(raw_item.content_plain.split()) + 12 < len(before_plain.split())
                and _has_current_example_callback_tail(raw_item.example_id, before_content)
            ):
                should_replace = True
                stats["rows_boundary_clipped"] += 1
                reason = "raw_layout_boundary_clipped"
                evidence_patch = {
                    "raw_layout_refresh": {
                        "evidence_codes": ["clips_current_example_callback_tail"],
                        "before_word_count": len(before_plain.split()),
                        "raw_word_count": len(raw_item.content_plain.split()),
                    }
                }
            elif boundary_evidence.get("evidence_codes"):
                should_replace = True
                stats["rows_boundary_clipped"] += 1
                reason = "raw_layout_shorter_boundary_refresh"
                evidence_patch = {"raw_layout_refresh": boundary_evidence}
            elif _candidate_quality_score(raw_item) > _row_quality_score(row):
                should_replace = True
                evidence_patch = {
                    "raw_layout_refresh": {
                        "evidence_codes": ["quality_score_improved"],
                        "before_word_count": len(before_plain.split()),
                        "raw_word_count": len(raw_item.content_plain.split()),
                        "before_quality_score": list(_row_quality_score(row)),
                        "raw_quality_score": list(_candidate_quality_score(raw_item)),
                        "added_table_refs": sorted(raw_tables - before_tables),
                        "added_formula_refs": sorted(set(raw_item.formula_refs) - {str(ref) for ref in (row.get("formula_refs") or [])}),
                    }
                }
            elif len(raw_item.content_plain.split()) + 16 < len(before_plain.split()):
                review_queue.append(
                    {
                        "chapter": chapter,
                        "example_id": raw_item.example_id,
                        "source_file": raw_item.source_file,
                        "before_word_count": len(before_plain.split()),
                        "raw_word_count": len(raw_item.content_plain.split()),
                        "reason": "raw_layout_shorter_without_strong_boundary_evidence",
                    }
                )

            if not should_replace:
                continue
            replacement_reason_counts[reason] += 1
            refresh_evidence = evidence_patch.get("raw_layout_refresh") if isinstance(evidence_patch, dict) else None
            if isinstance(refresh_evidence, dict):
                for code in refresh_evidence.get("evidence_codes") or []:
                    boundary_evidence_counts[str(code)] += 1
            _replace_row_from_candidate(row, raw_item, reason=reason, evidence_patch=evidence_patch)
            if _refresh_row_physical_span_from_raw_alignment(row, raw_item, structured_dir):
                stats["rows_physical_span_refreshed"] += 1
            stats["rows_replaced"] += 1

    if stats["rows_replaced"] and not dry_run:
        write_example_library(structured_dir, rows)
    stats["replacement_reason_counts"] = dict(sorted(replacement_reason_counts.items()))
    stats["boundary_evidence_counts"] = dict(sorted(boundary_evidence_counts.items()))
    stats["review_queue_count"] = len(review_queue)
    if review_queue:
        stats["review_queue_sample"] = review_queue[:50]
    return stats


def _validate_example_library_indexes(
    structured_dir: Path,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> dict[str, int]:
    """Verify that each library row can locate its placeholder.

    Corrects stale placeholder indexes by scanning blocks for the placeholder
    content.  ``start_block_index``/``end_block_index`` remain the source span;
    placeholder position is stored under ``replacement``.
    Rows whose placeholder cannot be found at all are marked stale.
    """
    stats: dict[str, int] = {"scanned": 0, "correct": 0, "corrected": 0, "stale": 0}
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        source_file = str(row.get("source_file") or "")
        if source_file:
            by_file[source_file].append(row)

    changed_any = False
    for source_file, file_rows in by_file.items():
        path = structured_dir / source_file
        if not path.exists():
            for row in file_rows:
                stats["stale"] += 1
            continue
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else []
        if not isinstance(blocks, list):
            for row in file_rows:
                stats["stale"] += 1
            continue

        # Build placeholder -> block_index map
        placeholder_to_index: dict[str, int] = {}
        for idx, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            if block.get("type") == "example" and "[[SEE_EXAMPLE:" in content:
                for ph_match in re.finditer(r'\[\[SEE_EXAMPLE:[^\]]+\]\]', content):
                    placeholder_to_index[ph_match.group(0)] = idx

        for row in file_rows:
            stats["scanned"] += 1
            placeholder = str(row.get("placeholder") or "")
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            start_idx = _safe_block_index(replacement.get("placeholder_block_index"))
            if start_idx is None:
                start_idx = _safe_block_index(row.get("start_block_index"))

            # Check current index is valid
            if (
                start_idx is not None
                and start_idx < len(blocks)
                and isinstance(blocks[start_idx], dict)
                and placeholder in str(blocks[start_idx].get("content") or "")
            ):
                stats["correct"] += 1
                continue

            # Search for correct index
            correct_idx = placeholder_to_index.get(placeholder)
            if correct_idx is not None:
                repl = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
                if repl.get("placeholder_block_index") == correct_idx:
                    stats["correct"] += 1
                    continue
                repl["placeholder_block_index"] = correct_idx
                repl["placeholder_source_file"] = source_file
                row["replacement"] = repl
                stats["corrected"] += 1
                changed_any = True
            else:
                stats["stale"] += 1

    if changed_any and not dry_run:
        write_example_library(structured_dir, rows)
    return stats


def _example_placeholder_for_row(row: dict[str, Any]) -> str:
    placeholder = str(row.get("placeholder") or "").strip()
    if placeholder:
        return placeholder
    example_ref = str(row.get("example_ref") or row.get("example_id") or "").strip()
    return f"[[SEE_EXAMPLE:{example_ref}]]" if example_ref else ""


def _row_placeholder_locations(structured_dir: Path, row: dict[str, Any]) -> list[tuple[str, int]]:
    placeholder = _example_placeholder_for_row(row)
    chapter = str(row.get("chapter") or "").strip().lower()
    if not placeholder or not chapter:
        return []
    hits: list[tuple[str, int]] = []
    for path in load_unit_files(structured_dir):
        if not path.name.lower().startswith(f"{chapter}_"):
            continue
        try:
            data = read_json(path)
        except Exception:
            continue
        blocks = data.get("blocks") if isinstance(data, dict) else []
        if not isinstance(blocks, list):
            continue
        for block_index, block in enumerate(blocks):
            if isinstance(block, dict) and placeholder in str(block.get("content") or ""):
                hits.append((path.name, block_index))
    return hits


def _raw_record_matches_block(raw_text: str, block_content: str, *, min_tokens: int = 8) -> bool:
    raw_tokens = normalize_match_text(raw_text).split()
    content_norm = normalize_match_text(block_content)
    if not raw_tokens or not content_norm:
        return False
    token_count = min(18, len(raw_tokens))
    if token_count < min_tokens:
        return False
    for start in (0, max(0, len(raw_tokens) // 2 - token_count // 2), max(0, len(raw_tokens) - token_count)):
        anchor = " ".join(raw_tokens[start : start + token_count])
        if anchor and anchor in content_norm:
            return True
    return False


def _find_structured_block_for_raw_record(
    *,
    structured_dir: Path,
    chapter: str,
    raw_text: str,
) -> tuple[str, int] | None:
    context = build_structured_context(structured_dir)
    for path, block_index, content in context.block_locations.get(chapter, []):
        if _raw_record_matches_block(raw_text, content):
            return path.name, block_index
    return None


def _find_missing_placeholder_insert_position(
    *,
    structured_dir: Path,
    project_root: Path,
    row: dict[str, Any],
) -> tuple[str, int, str] | None:
    chapter = str(row.get("chapter") or "").strip().lower()
    example_id = str(row.get("example_id") or row.get("example_ref") or "").strip()
    if not chapter or not example_id:
        return None

    records = ordered_paddle_records(project_root, chapter)
    anchor_index: int | None = None
    for index, record in enumerate(records):
        match = raw_example_start_match(record.content)
        if not match:
            continue
        if clean_ref_id(match.group("example_id")).lower() == example_id.lower():
            anchor_index = index
            break

    if anchor_index is not None:
        raw_example_norm = normalize_match_text(str(row.get("content_markdown") or row.get("content_plain") or ""))
        for index in range(anchor_index - 1, max(-1, anchor_index - 24), -1):
            record = records[index]
            if record.label in PADDLE_PAGE_NOISE_LABELS or raw_example_start_match(record.content):
                continue
            position = _find_structured_block_for_raw_record(
                structured_dir=structured_dir,
                chapter=chapter,
                raw_text=record.content,
            )
            if position is not None:
                file_name, block_index = position
                return file_name, block_index + 1, "after_previous_raw_body_anchor"

        for index in range(anchor_index + 1, min(len(records), anchor_index + 36)):
            record = records[index]
            if record.label in PADDLE_PAGE_NOISE_LABELS or raw_example_start_match(record.content):
                continue
            record_norm = normalize_match_text(record.content)
            if record_norm and raw_example_norm and record_norm in raw_example_norm:
                continue
            position = _find_structured_block_for_raw_record(
                structured_dir=structured_dir,
                chapter=chapter,
                raw_text=record.content,
            )
            if position is not None:
                file_name, block_index = position
                return file_name, block_index, "before_next_raw_body_anchor"

    source_file = str(row.get("source_file") or "").strip()
    if source_file and (structured_dir / source_file).exists():
        try:
            data = read_json(structured_dir / source_file)
        except Exception:
            data = {}
        blocks = data.get("blocks") if isinstance(data, dict) else []
        if isinstance(blocks, list):
            source_index = _safe_block_index(row.get("start_block_index"))
            if source_index is None:
                source_index = len(blocks)
            insert_index = min(len(blocks), source_index + 1)
            return source_file, insert_index, "row_source_file_fallback"
    return None


def _restore_missing_existing_example_placeholders(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "rows_scanned": 0,
        "missing_placeholders": 0,
        "placeholders_inserted": 0,
        "unresolved": [],
        "reason_counts": {},
    }
    reason_counts: Counter[str] = Counter()
    changed_files: set[str] = set()
    changed_rows = False

    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        placeholder = _example_placeholder_for_row(row)
        if not placeholder:
            continue
        stats["rows_scanned"] += 1
        if _row_placeholder_locations(structured_dir, row):
            continue
        stats["missing_placeholders"] += 1
        position = _find_missing_placeholder_insert_position(
            structured_dir=structured_dir,
            project_root=project_root,
            row=row,
        )
        if position is None:
            stats["unresolved"].append(
                f"{row.get('chapter')}:{row.get('example_id') or row.get('example_ref')}"
            )
            continue
        file_name, insert_index, reason = position
        path = structured_dir / file_name
        try:
            data = read_json(path)
        except Exception:
            stats["unresolved"].append(
                f"{row.get('chapter')}:{row.get('example_id') or row.get('example_ref')}"
            )
            continue
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if not isinstance(blocks, list):
            stats["unresolved"].append(
                f"{row.get('chapter')}:{row.get('example_id') or row.get('example_ref')}"
            )
            continue
        insert_index = min(max(0, insert_index), len(blocks))
        if not dry_run:
            blocks.insert(insert_index, {"type": "example", "content": placeholder})
            data["blocks"] = blocks
            write_json(path, data)
        changed_files.add(file_name)
        reason_counts[reason] += 1
        stats["placeholders_inserted"] += 1

        for other in rows:
            if not isinstance(other, dict):
                continue
            other_replacement = other.get("replacement") if isinstance(other.get("replacement"), dict) else {}
            other_file = str(other_replacement.get("placeholder_source_file") or other.get("source_file") or "")
            if other_file != file_name or other is row:
                continue
            other_index = _safe_block_index(other_replacement.get("placeholder_block_index"))
            if other_index is not None and other_index >= insert_index:
                other_replacement["placeholder_block_index"] = other_index + 1
                other["replacement"] = other_replacement
                changed_rows = True

        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        replacement["status"] = replacement.get("status") or "replaced"
        replacement["reason"] = replacement.get("reason") or "placeholder_block_written"
        replacement.setdefault(
            "source_block_span",
            _coerce_block_span([row.get("start_block_index"), row.get("end_block_index")]) or [insert_index, insert_index],
        )
        replacement["placeholder_block_index"] = insert_index
        replacement["placeholder_source_file"] = file_name
        row["replacement"] = replacement
        evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
        row["evidence"] = {
            **evidence,
            "existing_library_repair": "missing_placeholder_restored_from_raw_anchor",
            "placeholder_restore_reason": reason,
        }
        changed_rows = True

    if changed_rows and not dry_run:
        write_example_library(structured_dir, rows)
    stats["files_changed"] = len(changed_files)
    stats["reason_counts"] = dict(sorted(reason_counts.items()))
    return stats


def _remove_duplicate_existing_example_placeholders(
    structured_dir: Path,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> dict[str, int]:
    stats = {"rows_scanned": 0, "duplicate_placeholders_removed": 0, "files_changed": 0}
    canonical_positions: dict[str, tuple[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        placeholder = str(row.get("placeholder") or "")
        source_file = str(row.get("source_file") or "")
        if not placeholder or not source_file:
            continue
        canonical_index = _safe_block_index(replacement.get("placeholder_block_index"))
        if canonical_index is None:
            canonical_index = _safe_block_index(row.get("start_block_index"))
        if canonical_index is None:
            continue
        stats["rows_scanned"] += 1
        canonical_positions[placeholder] = (source_file, canonical_index)
    if not canonical_positions:
        return stats

    file_changed: set[str] = set()
    for path in load_unit_files(structured_dir):
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if not isinstance(blocks, list):
            continue
        changed = False
        new_blocks: list[Any] = []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                new_blocks.append(block)
                continue
            content = str(block.get("content") or "")
            updated_content = content
            remove_whole_block = False
            for placeholder, (source_file, canonical_index) in canonical_positions.items():
                if placeholder not in updated_content:
                    continue
                if path.name == source_file and block_index == canonical_index:
                    continue
                if updated_content.strip() == placeholder:
                    remove_whole_block = True
                    changed = True
                    stats["duplicate_placeholders_removed"] += 1
                    break
                updated_content = collapse_ws(updated_content.replace(placeholder, " "))
                changed = True
                stats["duplicate_placeholders_removed"] += 1
            if remove_whole_block:
                continue
            if updated_content != content:
                new_block = dict(block)
                new_block["content"] = updated_content
                new_blocks.append(new_block)
            else:
                new_blocks.append(block)
        if not changed:
            continue
        data["blocks"] = new_blocks
        file_changed.add(path.name)
        if not dry_run:
            write_json(path, data)
    stats["files_changed"] = len(file_changed)
    return stats


def _repair_existing_example_library(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    false_heading_stats = _restore_false_example_rows(structured_dir, rows, dry_run=dry_run)
    raw_refresh_stats = _refresh_existing_rows_from_raw_layout(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    monotonic_order_stats = _repair_nonmonotonic_existing_example_order(
        structured_dir=structured_dir,
        rows=rows,
        dry_run=dry_run,
    )
    relocate_stats = _relocate_out_of_order_existing_examples(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    sequence_gap_neighbor_stats = _repair_sequence_gap_neighbor_insert_placeholders(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    raw_global_order_stats = _repair_raw_layout_example_order(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    source_span_rewrite_stats = _rewrite_existing_example_source_spans(
        structured_dir,
        rows,
        dry_run=dry_run,
    )
    split_stats = _split_missing_examples_from_existing_library(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    duplicate_placeholder_stats = _remove_duplicate_existing_example_placeholders(
        structured_dir,
        rows,
        dry_run=dry_run,
    )
    orphan_placeholder_stats = _append_orphan_placeholder_rows_from_raw(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
    )
    missing_placeholder_restore_stats = _restore_missing_existing_example_placeholders(
        structured_dir=structured_dir,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    # Fix 3: validate that library row indexes actually point to their placeholders
    validation_stats = _validate_example_library_indexes(structured_dir, rows, dry_run=dry_run)
    changed = (
        false_heading_stats["source_blocks_restored"] > 0
        or raw_refresh_stats["rows_replaced"] > 0
        or monotonic_order_stats["rows_relocated"] > 0
        or relocate_stats["rows_relocated"] > 0
        or sequence_gap_neighbor_stats["rows_relocated"] > 0
        or raw_global_order_stats["rows_relocated"] > 0
        or raw_global_order_stats["heading_units_repaired"] > 0
        or source_span_rewrite_stats["rows_rewritten"] > 0
        or split_stats["split_from_existing_rows"] > 0
        or split_stats["updated_source_blocks"] > 0
        or duplicate_placeholder_stats["duplicate_placeholders_removed"] > 0
        or orphan_placeholder_stats["rows_added"] > 0
        or missing_placeholder_restore_stats["placeholders_inserted"] > 0
        or validation_stats["corrected"] > 0
    )
    if changed and not dry_run:
        write_example_library(structured_dir, rows)
    return {
        "changed": changed,
        "false_heading": false_heading_stats,
        "raw_layout_refresh": raw_refresh_stats,
        "monotonic_order": monotonic_order_stats,
        "raw_order_relocation": relocate_stats,
        "sequence_gap_neighbor_relocation": sequence_gap_neighbor_stats,
        "raw_layout_global_order": raw_global_order_stats,
        "source_span_rewrite": source_span_rewrite_stats,
        "sequence_gap_split": split_stats,
        "duplicate_placeholders": duplicate_placeholder_stats,
        "orphan_placeholders": orphan_placeholder_stats,
        "missing_placeholder_restore": missing_placeholder_restore_stats,
        "index_validation": validation_stats,
    }


def _first_anchor(text: str, token_count: int = 10) -> str:
    tokens = normalize_match_text(text).split()
    if len(tokens) < token_count:
        return ""
    return " ".join(tokens[:token_count])


def _find_reference_span(row: dict[str, Any], structured_dir: Path) -> tuple[str, int, int] | None:
    chapter = str(row.get("chapter") or "").strip().lower()
    content_markdown = str(row.get("content_markdown") or "")
    anchor = _first_anchor(content_markdown)
    if not chapter or not anchor:
        return None

    context = build_structured_context(structured_dir)
    for path, data in context.units_by_chapter.get(chapter, []):
        blocks = data.get("blocks") if isinstance(data.get("blocks"), list) else []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            if anchor in normalize_match_text(str(block.get("content") or "")):
                return path.name, block_index, block_index
    return None


def _reference_rows_to_candidates(
    *,
    reference_structured_dir: Path | None,
    structured_dir: Path,
    reference_rows: list[dict[str, Any]],
    existing_identities: set[tuple[str, str]],
    allowed_example_ids: set[tuple[str, str]],
) -> tuple[list[tuple[ExampleCandidate, str]], dict[str, int]]:
    if reference_structured_dir is None:
        return [], {"reference_rows": 0, "seeded": 0, "already_present": 0, "not_sequence_gap": 0, "unmatched": 0}

    stats = {
        "reference_rows": len(reference_rows),
        "seeded": 0,
        "already_present": 0,
        "not_sequence_gap": 0,
        "unmatched": 0,
    }
    seeded: list[tuple[ExampleCandidate, str]] = []
    for row in reference_rows:
        chapter, example_ref = _example_identity(row)
        example_id = str(row.get("example_id") or "").strip()
        if not chapter or not example_ref:
            stats["unmatched"] += 1
            continue
        if (chapter, example_ref) in existing_identities:
            stats["already_present"] += 1
            continue
        if (chapter, example_id) not in allowed_example_ids:
            stats["not_sequence_gap"] += 1
            continue
        candidate = existing_library_row_to_candidate(row)
        if candidate is None:
            stats["unmatched"] += 1
            continue
        span = _find_reference_span(row, structured_dir)
        if span is None:
            stats["unmatched"] += 1
            continue
        source_file, start_block_index, end_block_index = span
        candidate.source_file = source_file
        candidate.start_block_index = start_block_index
        candidate.end_block_index = end_block_index
        candidate.evidence = {
            **candidate.evidence,
            "source": "reference_example_library+structured_blocks",
            "detection_method": "reference_example_library_seed",
            "reference_structured_dir": str(reference_structured_dir),
        }
        candidate.metadata = {
            **candidate.metadata,
            "reference_seed": True,
        }
        seeded.append((candidate, example_ref))
        existing_identities.add((chapter, example_ref))
        stats["seeded"] += 1
    return seeded, stats


def _reference_sequence_gap_targets(
    automatic_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
) -> set[tuple[str, str]]:
    numbers_by_group: dict[tuple[str, str], set[int]] = defaultdict(set)
    automatic_example_ids: set[tuple[str, str]] = set()
    for row in automatic_rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        parts = _example_number_parts(example_id)
        if not chapter or parts is None:
            continue
        prefix, number = parts
        numbers_by_group[(chapter, prefix)].add(number)
        automatic_example_ids.add((chapter, example_id))

    targets: set[tuple[str, str]] = set()
    for row in reference_rows:
        chapter = str(row.get("chapter") or "").strip().lower()
        example_id = str(row.get("example_id") or "").strip()
        parts = _example_number_parts(example_id)
        if not chapter or parts is None or (chapter, example_id) in automatic_example_ids:
            continue
        prefix, number = parts
        observed = numbers_by_group.get((chapter, prefix))
        if not observed or len(observed) < 2:
            continue
        first = min(observed)
        last = max(observed)
        lower_bound = 1 if first <= 2 else first
        if lower_bound <= number <= last:
            targets.add((chapter, example_id))
    return targets


def _sequence_gap_targets_from_candidates(
    candidates: list[ExampleCandidate],
) -> dict[str, set[str]]:
    numbers_by_group: dict[tuple[str, str], set[int]] = defaultdict(set)
    for item in candidates:
        parts = _example_number_parts(item.example_id)
        if parts is None:
            continue
        prefix, number = parts
        numbers_by_group[(item.chapter, prefix)].add(number)

    targets: dict[str, set[str]] = defaultdict(set)
    for (chapter, prefix), numbers in numbers_by_group.items():
        if len(numbers) < 2:
            continue
        first = min(numbers)
        last = max(numbers)
        lower_bound = 1 if first <= 2 else first
        for number in range(lower_bound, last + 1):
            if number not in numbers:
                targets[chapter].add(f"{prefix}.{number}")
    return targets


def _sequence_gap_target_set_from_candidates(candidates: list[ExampleCandidate]) -> set[tuple[str, str]]:
    targets_by_chapter = _sequence_gap_targets_from_candidates(candidates)
    return {
        (chapter, example_id)
        for chapter, example_ids in targets_by_chapter.items()
        for example_id in example_ids
    }


def _copy_candidate(item: ExampleCandidate) -> ExampleCandidate:
    return ExampleCandidate(
        example_id=item.example_id,
        chapter=item.chapter,
        label=item.label,
        title=item.title,
        source_file=item.source_file,
        start_block_index=item.start_block_index,
        end_block_index=item.end_block_index,
        block_ids=list(item.block_ids),
        content_markdown=item.content_markdown,
        content_plain=item.content_plain,
        formula_refs=list(item.formula_refs),
        table_refs=list(item.table_refs),
        figure_refs=list(item.figure_refs),
        external_refs=list(item.external_refs),
        evidence=dict(item.evidence),
        metadata=dict(item.metadata),
        _order_key=item._order_key,
    )


def _placeholder_position_for_example(
    *,
    context: Any,
    chapter: str,
    example_id: str,
) -> tuple[str, int, int] | None:
    parts = _example_number_parts(example_id)
    if parts is None:
        return None
    _, number = parts
    ordered: list[tuple[int, str, int]] = []
    for ref, file_name, block_index in context.placeholder_order.get(chapter, []):
        ref_parts = _example_number_parts(ref)
        if ref_parts is None or ref_parts[0] != parts[0]:
            continue
        ordered.append((ref_parts[1], file_name, block_index))
    if not ordered:
        return None
    ordered.sort(key=lambda item: (item[0], natural_key(item[1]), item[2]))

    before = [item for item in ordered if item[0] < number]
    after = [item for item in ordered if item[0] > number]
    if before:
        _, file_name, block_index = before[-1]
        return file_name, block_index + 1, 0
    if after:
        _, file_name, block_index = after[0]
        return file_name, block_index, 0
    return None


def _candidate_as_insert_placeholder(
    item: ExampleCandidate,
    context: Any,
) -> ExampleCandidate | None:
    position = _placeholder_position_for_example(
        context=context,
        chapter=item.chapter,
        example_id=item.example_id,
    )
    if position is None:
        return None
    source_file, insert_block, _ = position
    inserted = _copy_candidate(item)
    inserted.source_file = source_file
    inserted.start_block_index = insert_block
    inserted.end_block_index = insert_block
    inserted.metadata = {
        **inserted.metadata,
        "insert_placeholder_only": True,
        "replacement_start_char": 0,
        "replacement_end_char": 0,
    }
    inserted.evidence = {
        **inserted.evidence,
        "detection_method": "sequence_gap_raw_layout_insert_placeholder",
    }
    inserted._order_key = (
        chapter_sort_key(inserted.chapter),
        natural_key(inserted.source_file),
        inserted.start_block_index,
        0,
        natural_key(inserted.example_id),
    )
    return inserted


def _candidate_sequence_position_for_example(
    *,
    item: ExampleCandidate,
    candidates: list[ExampleCandidate],
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> tuple[str, int, int] | None:
    parts = _example_number_parts(item.example_id)
    if parts is None:
        return None
    prefix, number = parts
    ordered: list[tuple[int, str, int, int, ExampleCandidate]] = []
    for candidate in candidates:
        if candidate.chapter != item.chapter:
            continue
        candidate_parts = _example_number_parts(candidate.example_id)
        if candidate_parts is None or candidate_parts[0] != prefix:
            continue
        candidate_number = candidate_parts[1]
        start_char = _int_metadata(candidate, "replacement_start_char", 0) or 0
        ordered.append((candidate_number, candidate.source_file, candidate.start_block_index, start_char, candidate))
    if not ordered:
        return None
    ordered.sort(key=lambda entry: (entry[0], natural_key(entry[1]), entry[2], entry[3]))

    before = [entry for entry in ordered if entry[0] < number]
    after = [entry for entry in ordered if entry[0] > number]
    previous = before[-1] if before else None
    next_entry = after[0] if after else None
    if previous is not None:
        _, file_name, block_index, _, previous_candidate = previous
        if _candidate_visual_stop_mentions_target(previous_candidate, item):
            return file_name, block_index + 1, 0
        target_page = _candidate_source_page(item, raw_pages)
        previous_page = _candidate_source_page(previous_candidate, raw_pages)
        next_page = _candidate_source_page(next_entry[4], raw_pages) if next_entry is not None else None
        previous_distance = abs(target_page - previous_page) if target_page is not None and previous_page is not None else None
        next_distance = abs(target_page - next_page) if target_page is not None and next_page is not None else None
        if previous_distance is not None and (
            (next_distance is not None and previous_distance < next_distance)
            or (next_distance is None and previous_distance <= 1)
        ):
            return file_name, block_index + 1, 0
    if after:
        _, file_name, block_index, start_char, _ = after[0]
        return file_name, block_index, start_char
    if before:
        _, file_name, block_index, _, _ = before[-1]
        return file_name, block_index + 1, 0
    return None


def _candidate_as_sequence_insert_placeholder(
    item: ExampleCandidate,
    candidates: list[ExampleCandidate],
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> ExampleCandidate | None:
    position = _candidate_sequence_position_for_example(item=item, candidates=candidates, raw_pages=raw_pages)
    if position is None:
        return None
    source_file, insert_block, insert_char = position
    inserted = _copy_candidate(item)
    inserted.source_file = source_file
    inserted.start_block_index = insert_block
    inserted.end_block_index = insert_block
    inserted.metadata = {
        **inserted.metadata,
        "insert_placeholder_only": True,
        "replacement_start_char": insert_char,
        "replacement_end_char": insert_char,
        "sequence_gap_neighbor_insert": True,
    }
    inserted.evidence = {
        **inserted.evidence,
        "detection_method": "sequence_gap_raw_layout_neighbor_insert_placeholder",
    }
    inserted._order_key = (
        chapter_sort_key(inserted.chapter),
        natural_key(inserted.source_file),
        inserted.start_block_index,
        insert_char,
        natural_key(inserted.example_id),
    )
    return inserted


def _aligned_to_different_example_block(item: ExampleCandidate, aligned: ExampleCandidate, structured_dir: Path) -> bool:
    path = structured_dir / aligned.source_file
    if not path.exists():
        return False
    try:
        data = read_json(path)
    except Exception:
        return False
    blocks = data.get("blocks") if isinstance(data, dict) else []
    if not isinstance(blocks, list):
        return False
    block_index = aligned.start_block_index
    if block_index < 0 or block_index >= len(blocks):
        return False
    block = blocks[block_index]
    if not isinstance(block, dict):
        return False
    content = str(block.get("content") or "")
    title_match = EXAMPLE_TITLE_PREFIX_RE.search(content)
    if title_match and clean_ref_id(title_match.group("example_id")).lower() != item.example_id.lower():
        return True
    if EXAMPLE_PLACEHOLDER_RE.search(content) and f"[[SEE_EXAMPLE:{item.example_id}]]" not in content:
        return True
    return False


def _normalize_sequence_gap_alignment(
    raw_item: ExampleCandidate,
    aligned: ExampleCandidate | None,
    *,
    context: Any,
    structured_dir: Path,
    candidates: list[ExampleCandidate] | None = None,
    raw_pages: dict[tuple[str, str], int] | None = None,
) -> ExampleCandidate | None:
    if aligned is not None and not _aligned_to_different_example_block(raw_item, aligned, structured_dir):
        return aligned
    inserted = _candidate_as_insert_placeholder(raw_item, context)
    if inserted is None and candidates is not None:
        inserted = _candidate_as_sequence_insert_placeholder(raw_item, candidates, raw_pages=raw_pages)
    if inserted is not None:
        inserted.evidence = {
            **inserted.evidence,
            "alignment_rejected": "different_example_block",
        }
    return inserted


def _refresh_candidate_metadata(item: ExampleCandidate) -> None:
    item.content_markdown = normalize_heading_prefix(item.content_markdown)
    content_plain = collapse_ws(strip_structured_refs(strip_html(item.content_markdown)))
    item.content_plain = content_plain
    item.title = collapse_ws(
        re.sub(
            r"^\s*Example\s+(?:A\d+|\d+)\.\d+[a-z]?\.\s*",
            "",
            item.content_markdown,
            count=1,
            flags=re.IGNORECASE,
        )
    )[:160].strip()
    item.formula_refs = extract_formula_refs(item.content_markdown)
    item.table_refs = extract_table_refs(item.content_markdown)
    item.figure_refs = extract_figure_refs(item.content_markdown)
    item.external_refs = extract_external_refs(item.content_markdown)
    item.metadata = {
        **item.metadata,
        "has_formula": bool(item.formula_refs),
        "has_table": bool(item.table_refs),
        "has_figure": bool(item.figure_refs),
        "word_count": len(content_plain.split()) if content_plain else 0,
        "needs_review": looks_truncated(item.content_markdown),
    }


def _rebind_candidate_table_refs_to_source(item: ExampleCandidate, structured_dir: Path) -> None:
    if not item.table_refs:
        return
    source_refs = source_table_refs(item.chapter, item.source_file, build_structured_context(structured_dir))
    if not source_refs:
        return
    replacements: dict[str, str] = {}
    source_iter = iter(source_refs)
    for table_ref in item.table_refs:
        if table_ref in source_refs:
            continue
        if not str(table_ref).lower().startswith("inline_"):
            continue
        replacement = next(source_iter, None)
        if replacement is None:
            break
        replacements[table_ref] = replacement
    if not replacements:
        return
    for old, new in replacements.items():
        item.content_markdown = item.content_markdown.replace(f"[[TABLE:{old}]]", f"[[TABLE:{new}]]")
    item.evidence = {
        **item.evidence,
        "table_ref_rebinding": replacements,
    }
    _refresh_candidate_metadata(item)


def _apply_reference_table_refs(item: ExampleCandidate, row: dict[str, Any] | None) -> None:
    if not isinstance(row, dict):
        return
    reference_refs = row.get("table_refs") if isinstance(row.get("table_refs"), list) else []
    reference_refs = [str(ref).strip() for ref in reference_refs if str(ref).strip()]
    if not reference_refs:
        return
    current_refs = item.table_refs
    if current_refs == reference_refs:
        return

    replacements = iter(reference_refs)

    def repl(match: re.Match[str]) -> str:
        replacement = next(replacements, None)
        if replacement is None:
            return match.group(0)
        return f"[[TABLE:{replacement}]]"

    updated = TABLE_PLACEHOLDER_RE.sub(repl, item.content_markdown, count=len(reference_refs))
    if updated == item.content_markdown:
        return
    item.content_markdown = updated
    item.evidence = {
        **item.evidence,
        "reference_table_refs": reference_refs,
    }
    _refresh_candidate_metadata(item)


def _block_anchor_in_raw(
    block_content: str,
    raw_tokens: list[str],
    *,
    min_anchor_tokens: int = 6,
) -> bool:
    block_tokens = [token for token, _, _ in _token_spans(block_content)]
    if len(block_tokens) < min_anchor_tokens:
        return False
    max_anchor_tokens = min(16, len(block_tokens))
    for anchor_size in range(max_anchor_tokens, min_anchor_tokens - 1, -1):
        for offset in range(0, min(8, len(block_tokens) - anchor_size + 1)):
            anchor = block_tokens[offset : offset + anchor_size]
            if _find_subsequence(raw_tokens, anchor) is not None:
                return True
    return False


def _extend_aligned_span_forward(
    *,
    path: Path,
    block_index: int,
    raw_tokens: list[str],
    context: Any | None = None,
) -> tuple[int, int, int]:
    del context
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else []
    if not isinstance(blocks, list):
        return block_index, 0, 0

    end_block_index = block_index
    replacement_end_char = len(str(blocks[block_index].get("content") or "")) if block_index < len(blocks) and isinstance(blocks[block_index], dict) else 0
    extended_blocks = 0
    skipped_table_blocks = 0
    cursor = block_index + 1
    while cursor < len(blocks):
        block = blocks[cursor]
        if not isinstance(block, dict):
            break
        block_type = str(block.get("type") or "").strip().lower()
        content = str(block.get("content") or "")
        if block_type == "table":
            skipped_table_blocks += 1
            break
        if block_type == "example" or EXAMPLE_PLACEHOLDER_RE.search(content):
            break
        if EXAMPLE_TITLE_PREFIX_RE.search(content):
            break
        if not _block_anchor_in_raw(content, raw_tokens):
            break
        end_block_index = cursor
        replacement_end_char = len(content)
        extended_blocks += 1
        cursor += 1
    return end_block_index, replacement_end_char, extended_blocks


def _source_span_until_next_example(
    *,
    path: Path,
    block_index: int,
    start_char: int = 0,
    visual_stop_clipped: bool = False,
) -> tuple[int, int]:
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else []
    if not isinstance(blocks, list) or block_index < 0 or block_index >= len(blocks):
        return block_index, block_index

    end_block_index = block_index
    next_example_block: int | None = None
    cursor = block_index + 1
    while cursor < len(blocks):
        block = blocks[cursor]
        if not isinstance(block, dict):
            break
        content = str(block.get("content") or "")
        if EXAMPLE_TITLE_PREFIX_RE.search(content) or EXAMPLE_PLACEHOLDER_RE.search(content):
            next_example_block = cursor
            break
        end_block_index = cursor
        cursor += 1

    current = blocks[block_index]
    if isinstance(current, dict):
        content = str(current.get("content") or "")
        for match in EXAMPLE_TITLE_PREFIX_RE.finditer(content):
            if match.start() > max(0, start_char):
                return block_index, block_index
    if visual_stop_clipped and start_char <= 0 and end_block_index > block_index:
        return block_index, min(block_index + 1, end_block_index)
    if visual_stop_clipped and next_example_block is not None and next_example_block == block_index + 1:
        return block_index, block_index
    return block_index, end_block_index


def _token_anchor_in_block(block_content: str, anchor_text: str, *, min_anchor_tokens: int = 6) -> bool:
    block_tokens = [token for token, _, _ in _token_spans(block_content)]
    anchor_tokens = [token for token, _, _ in _token_spans(anchor_text)]
    if not block_tokens or not anchor_tokens:
        return False
    max_anchor = min(16, len(anchor_tokens))
    for size in range(max_anchor, min_anchor_tokens - 1, -1):
        for offset in range(0, len(anchor_tokens) - size + 1):
            if _find_subsequence(block_tokens, anchor_tokens[offset : offset + size]) is not None:
                return True
    return False


def _raw_visual_stop_source_end_block(
    *,
    path: Path,
    start_block_index: int,
    visual_stop: dict[str, Any],
) -> int | None:
    stop_text = str(visual_stop.get("stop_text") or "").strip()
    if not stop_text:
        return None
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else []
    if not isinstance(blocks, list):
        return None
    for index in range(max(0, start_block_index + 1), len(blocks)):
        block = blocks[index]
        if not isinstance(block, dict):
            continue
        content = str(block.get("content") or "")
        if _token_anchor_in_block(content, stop_text):
            return index
        if EXAMPLE_TITLE_PREFIX_RE.search(content) or EXAMPLE_PLACEHOLDER_RE.search(content):
            break
    return None


def _align_raw_candidate_to_structured_content(
    item: ExampleCandidate,
    structured_dir: Path,
    *,
    min_anchor_tokens: int = 8,
) -> ExampleCandidate | None:
    raw_tokens = _token_spans(item.content_plain)
    if len(raw_tokens) < min_anchor_tokens:
        return None
    raw_token_values = [token for token, _, _ in raw_tokens]
    search_start_offset = 0
    expected_id_tokens = [token.lower() for token in re.findall(r"[0-9A-Za-z]+", item.example_id)]
    if (
        len(raw_token_values) > len(expected_id_tokens) + 1
        and raw_token_values[0] == "example"
        and raw_token_values[1 : 1 + len(expected_id_tokens)] == expected_id_tokens
    ):
        search_start_offset = 1 + len(expected_id_tokens)
    else:
        start_match = raw_example_start_match(item.content_markdown)
        if start_match and clean_ref_id(start_match.group("example_id")).lower() == item.example_id.lower():
            heading_end = start_match.end()
            while heading_end < len(item.content_markdown) and item.content_markdown[heading_end].isspace():
                heading_end += 1
            for token_index, (_, start, _) in enumerate(raw_tokens):
                if start >= heading_end:
                    search_start_offset = token_index
                    break
    context = build_structured_context(structured_dir)
    best_match: tuple[Path, int, str, int, int, int] | None = None
    for path, block_index, content in context.block_locations.get(item.chapter, []):
        content_tokens = _token_spans(content)
        content_values = [token for token, _, _ in content_tokens]
        for raw_offset in range(search_start_offset, len(raw_tokens) - min_anchor_tokens + 1):
            anchor_tokens = raw_token_values[raw_offset : raw_offset + min_anchor_tokens]
            content_offset = _find_subsequence(content_values, anchor_tokens)
            if content_offset is None:
                continue
            raw_start_token = raw_offset
            content_start_token = content_offset
            while (
                raw_start_token > 0
                and content_start_token > 0
                and raw_token_values[raw_start_token - 1] == content_values[content_start_token - 1]
            ):
                raw_start_token -= 1
                content_start_token -= 1
            start_char = content_tokens[content_start_token][1]
            if start_char > 0:
                while start_char < len(content) and content[start_char].isspace():
                    start_char += 1
            score = (natural_key(path.name), block_index, start_char, raw_offset)
            if best_match is None or score < (natural_key(best_match[0].name), best_match[1], best_match[3], best_match[4]):
                best_match = (path, block_index, content, start_char, raw_offset, content_offset)
            break
    if best_match is None:
        return None

    path, block_index, content, start_char, raw_offset, content_offset = best_match
    if raw_offset > 0 and start_char > 0:
        sentence_start = max(
            content.rfind(". ", 0, start_char),
            content.rfind("? ", 0, start_char),
            content.rfind("! ", 0, start_char),
        )
        if sentence_start >= 0:
            candidate_start = sentence_start + 2
            gap = content[candidate_start:start_char]
            if gap and len(gap) <= 3 and not gap.strip():
                start_char = candidate_start
    end_block_index, replacement_end_char, extended_blocks = _extend_aligned_span_forward(
        path=path,
        block_index=block_index,
        raw_tokens=raw_token_values,
    )
    source_start_block, source_end_block = _source_span_until_next_example(
        path=path,
        block_index=block_index,
        start_char=start_char,
        visual_stop_clipped=bool(item.metadata.get("visual_stop_clipped")) if isinstance(item.metadata, dict) else False,
    )
    visual_stop = item.metadata.get("visual_stop") if isinstance(item.metadata, dict) else None
    if isinstance(visual_stop, dict):
        stop_block = _raw_visual_stop_source_end_block(
            path=path,
            start_block_index=block_index,
            visual_stop=visual_stop,
        )
        if stop_block is not None:
            source_end_block = min(source_end_block, stop_block)
    if (
        item.evidence.get("source") == "paddle_raw_layout+structured_blocks"
        and start_char <= 0
        and source_end_block > block_index + 1
        and len(raw_token_values) < 80
    ):
        source_end_block = block_index + 1
    aligned = _copy_candidate(item)
    aligned.source_file = path.name
    aligned.start_block_index = block_index
    aligned.end_block_index = end_block_index
    aligned.metadata = {
        **aligned.metadata,
        "replacement_start_char": start_char,
        "replacement_end_char": replacement_end_char,
        "sequence_gap_recovery": True,
        "source_block_span": [source_start_block, source_end_block],
    }
    if extended_blocks:
        aligned.metadata["sequence_gap_extended_blocks"] = extended_blocks
    aligned.evidence = {
        **aligned.evidence,
        "detection_method": "sequence_gap_raw_layout_recovery",
        "structured_anchor_offset": content_offset,
        "raw_anchor_offset": raw_offset,
    }
    aligned._order_key = (
        chapter_sort_key(aligned.chapter),
        natural_key(aligned.source_file),
        aligned.start_block_index,
        start_char,
        natural_key(aligned.example_id),
    )
    return aligned


def _clip_candidate_at_next_example(
    item: ExampleCandidate,
    next_item: ExampleCandidate,
) -> None:
    if item.source_file != next_item.source_file:
        return
    item_end = _candidate_end_point(item)
    next_start = _candidate_start_point(next_item)
    if item.start_block_index > next_item.start_block_index or item_end <= next_start:
        return
    item.end_block_index = next_item.start_block_index
    end_char = _int_metadata(next_item, "replacement_start_char")
    if end_char is not None:
        item.metadata["replacement_end_char"] = end_char
    elif "replacement_end_char" in item.metadata:
        item.metadata.pop("replacement_end_char", None)
    item.evidence = {
        **item.evidence,
        "sequence_gap_boundary_clipped_before": next_item.example_id,
    }


def _apply_sequence_gap_boundaries(examples_with_refs: list[tuple[ExampleCandidate, str | None]]) -> None:
    by_chapter_prefix: dict[tuple[str, str], list[ExampleCandidate]] = defaultdict(list)
    for item, _ in examples_with_refs:
        parts = _example_number_parts(item.example_id)
        if parts is None:
            continue
        prefix, _ = parts
        by_chapter_prefix[(item.chapter, prefix)].append(item)

    for items in by_chapter_prefix.values():
        ordered = sorted(
            items,
            key=lambda item: (
                _example_number_parts(item.example_id)[1] if _example_number_parts(item.example_id) else 999999,
                natural_key(item.source_file),
                item.start_block_index,
            ),
        )
        for left, right in zip(ordered, ordered[1:]):
            _clip_candidate_at_next_example(left, right)
        for previous, current, next_item in zip(ordered, ordered[1:], ordered[2:]):
            if current.source_file != previous.source_file or current.source_file != next_item.source_file:
                continue
            if not (
                previous.metadata.get("sequence_gap_boundary_clipped_before") == current.example_id
                or previous.evidence.get("sequence_gap_boundary_clipped_before") == current.example_id
            ):
                continue
            current_parts = _example_number_parts(current.example_id)
            previous_parts = _example_number_parts(previous.example_id)
            next_parts = _example_number_parts(next_item.example_id)
            if current_parts is None or previous_parts is None or next_parts is None:
                continue
            if not (previous_parts[1] + 1 == current_parts[1] and current_parts[1] + 1 == next_parts[1]):
                continue
            if not current.metadata.get("sequence_gap_recovery"):
                continue
            start_char = _int_metadata(current, "replacement_start_char", 0) or 0
            if start_char <= 0:
                continue
            previous_span = previous.metadata.get("source_block_span")
            next_span = next_item.metadata.get("source_block_span")
            if not (isinstance(previous_span, list) and len(previous_span) == 2):
                continue
            if not (isinstance(next_span, list) and len(next_span) == 2):
                continue
            source_start = max(int(previous_span[0]), current.start_block_index - 1)
            source_end = min(int(next_span[0]), max(source_start, current.start_block_index))
            current.metadata["source_block_span"] = [source_start, source_end]
            current.evidence = {
                **current.evidence,
                "source_span_adjusted": "sequence_gap_between_neighbors",
            }
            if int(previous_span[1]) > source_start:
                previous.metadata["source_block_span"] = [int(previous_span[0]), source_start]
                previous.evidence = {
                    **previous.evidence,
                    "source_span_adjusted": "sequence_gap_neighbor_boundary",
                }
            if int(next_span[0]) > source_end:
                next_end = int(next_span[1])
                if (
                    next_item.evidence.get("source") == "structured_blocks"
                    and next_item.end_block_index > next_item.start_block_index
                ):
                    next_end = min(next_end, next_item.start_block_index)
                next_item.metadata["source_block_span"] = [source_end, next_end]
                next_item.evidence = {
                    **next_item.evidence,
                    "source_span_adjusted": "sequence_gap_neighbor_boundary",
                }


def _recover_sequence_gap_examples(
    *,
    structured_dir: Path,
    project_root: Path,
    examples_with_refs: list[tuple[ExampleCandidate, str | None]],
    allowed_example_ids: set[tuple[str, str]],
    reference_rows_by_id: dict[tuple[str, str], dict[str, Any]],
) -> tuple[list[tuple[ExampleCandidate, str | None]], dict[str, Any]]:
    if not allowed_example_ids:
        return [], {
            "targeted": 0,
            "raw_recovered": 0,
            "aligned": 0,
            "unaligned": 0,
        }

    existing_by_chapter: dict[str, set[str]] = defaultdict(set)
    base_candidates = [item for item, _ in examples_with_refs]
    for item in base_candidates:
        existing_by_chapter[item.chapter].add(item.example_id)
    targets_by_chapter: dict[str, set[str]] = defaultdict(set)
    for chapter, example_id in allowed_example_ids:
        targets_by_chapter[chapter].add(example_id)

    recovered: list[tuple[ExampleCandidate, str | None]] = []
    stats = {
        "targeted": 0,
        "raw_recovered": 0,
        "aligned": 0,
        "unaligned": 0,
    }
    context = build_structured_context(structured_dir)
    for chapter, target_ids in sorted(targets_by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        missing_targets = {target for target in target_ids if target not in existing_by_chapter.get(chapter, set())}
        if not missing_targets:
            continue
        stats["targeted"] += len(missing_targets)
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(existing_by_chapter.get(chapter, set())),
            target_ids=missing_targets,
            skip_structured_matches=False,
        )
        stats["raw_recovered"] += len(raw_items)
        raw_pages = _raw_example_pages(project_root, {chapter})
        for raw_item in raw_items:
            aligned = _align_raw_candidate_to_structured_content(raw_item, structured_dir)
            aligned = _normalize_sequence_gap_alignment(
                raw_item,
                aligned,
                context=context,
                structured_dir=structured_dir,
                candidates=base_candidates + [item for item, _ in recovered],
                raw_pages=raw_pages,
            )
            if aligned is None:
                stats["unaligned"] += 1
                continue
            raw_table_refs = list(raw_item.table_refs)
            raw_content = raw_item.content_markdown
            if raw_table_refs and not aligned.table_refs:
                aligned.table_refs = raw_table_refs
                aligned.content_markdown = raw_content
                aligned.metadata["has_table"] = True
            _apply_reference_table_refs(aligned, reference_rows_by_id.get((chapter, aligned.example_id)))
            _rebind_candidate_table_refs_to_source(aligned, structured_dir)
            recovered.append((aligned, None))
            existing_by_chapter[chapter].add(aligned.example_id)
            stats["aligned"] += 1

    if recovered:
        examples_with_refs.extend(recovered)
        examples_with_refs.sort(
            key=lambda item: (
                chapter_sort_key(item[0].chapter),
                natural_key(item[0].source_file),
                item[0].start_block_index,
                _int_metadata(item[0], "replacement_start_char", 0) or 0,
                natural_key(str(item[1] or item[0].example_id)),
            )
        )
        _apply_sequence_gap_boundaries(examples_with_refs)
        for item, _ in examples_with_refs:
            _refresh_candidate_metadata(item)
    return recovered, stats


def _build_rows_and_replacements(
    examples_with_refs: list[tuple[ExampleCandidate, str | None]],
) -> tuple[list[dict[str, Any]], dict[str, list[ExampleCandidate]], dict[str, str]]:
    id_counts = Counter(item.example_id for item, _ in examples_with_refs)
    selected_keys, selection_reasons = select_non_overlapping_examples([item for item, _ in examples_with_refs])
    example_refs: dict[str, str] = {}
    for item, explicit_ref in examples_with_refs:
        key = candidate_key(item)
        example_refs[key] = str(explicit_ref or make_example_ref(item, id_counts))

    library_rows: list[dict[str, Any]] = []
    replace_by_file: dict[str, list[ExampleCandidate]] = defaultdict(list)
    for item, _ in examples_with_refs:
        key = candidate_key(item)
        selected = key in selected_keys
        status = "replaced" if selected else "skipped"
        reason = "placeholder_block_written" if selected else selection_reasons.get(key, "not_selected")
        library_rows.append(
            example_to_library_row(
                item,
                example_ref=example_refs[key],
                replacement_status=status,
                replacement_reason=reason,
            )
        )
        if selected:
            replace_by_file[item.source_file].append(item)

    return library_rows, replace_by_file, example_refs


def _append_orphan_placeholder_rows_from_raw(
    *,
    structured_dir: Path,
    project_root: Path,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    refs_by_chapter = _structured_placeholder_refs(structured_dir)
    existing = {
        (
            str(row.get("chapter") or "").strip().lower(),
            str(row.get("example_ref") or row.get("example_id") or "").strip(),
        )
        for row in rows
        if isinstance(row, dict)
    }
    missing_by_chapter: dict[str, set[str]] = defaultdict(set)
    for chapter, refs in refs_by_chapter.items():
        for ref in refs:
            if (chapter, ref) not in existing:
                missing_by_chapter[chapter].add(ref)
    stats: dict[str, Any] = {
        "missing_placeholder_refs": sum(len(refs) for refs in missing_by_chapter.values()),
        "raw_recovered": 0,
        "rows_added": 0,
        "unmatched": [],
    }
    if not missing_by_chapter:
        return stats

    context = build_structured_context(structured_dir)
    for chapter, refs in sorted(missing_by_chapter.items(), key=lambda item: chapter_sort_key(item[0])):
        raw_items = recover_examples_from_paddle_raw(
            project_root=project_root,
            chapter=chapter,
            context=context,
            existing_ids=set(),
            target_ids=refs,
            skip_structured_matches=False,
        )
        recovered_by_id = {item.example_id: item for item in raw_items}
        stats["raw_recovered"] += len(raw_items)
        for ref in sorted(refs, key=natural_key):
            item = recovered_by_id.get(ref)
            if item is None:
                stats["unmatched"].append(f"{chapter}:{ref}")
                continue
            rows.append(_make_row_from_candidate(item, example_ref=ref))
            existing.add((chapter, ref))
            stats["rows_added"] += 1
    if rows:
        rows.sort(
            key=lambda row: (
                chapter_sort_key(str(row.get("chapter") or "")),
                natural_key(str(row.get("source_file") or "")),
                _safe_block_index(row.get("start_block_index")) or 0,
                natural_key(str(row.get("example_ref") or row.get("example_id") or "")),
            )
        )
    return stats


def _refresh_rows_after_replacement(
    rows: list[dict[str, Any]],
    replacement_stats: list[dict[str, Any]],
) -> None:
    remapped: dict[tuple[str, str], int] = {}
    for stat in replacement_stats:
        file_name = str(stat.get("file") or "")
        mapping = stat.get("remapped_indexes") if isinstance(stat.get("remapped_indexes"), dict) else {}
        for key, index in mapping.items():
            try:
                remapped[(file_name, str(key))] = int(index)
            except (TypeError, ValueError):
                continue

    if not remapped:
        return

    for row in rows:
        source_file = str(row.get("source_file") or "")
        key = f"{source_file}#{row.get('start_block_index')}-{row.get('end_block_index')}#{row.get('example_id')}"
        new_index = remapped.get((source_file, key))
        if new_index is None:
            continue
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        replacement["placeholder_block_index"] = new_index
        replacement["placeholder_source_file"] = source_file
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        if metadata.get("raw_layout_added_table_refs"):
            span = replacement.get("source_block_span")
            if isinstance(span, list) and len(span) == 2:
                start = _safe_block_index(span[0])
                end = _safe_block_index(span[1])
                if start is not None and end is not None:
                    replacement["source_block_span"] = [
                        start,
                        end + int(metadata.get("source_span_extra_blocks") or 0),
                    ]
        if metadata.get("sequence_gap_recovery") and metadata.get("replacement_start_char") is not None:
            span = replacement.get("source_block_span")
            if isinstance(span, list) and len(span) == 2 and span[0] == span[1] == row.get("start_block_index"):
                replacement["source_block_span"] = [new_index, new_index]
        row["replacement"] = replacement


def _safe_block_index(value: Any) -> int | None:
    try:
        index = int(value)
    except (TypeError, ValueError):
        return None
    return index if index >= 0 else None


def _existing_placeholder_stats(structured_dir: Path, rows: list[dict[str, Any]]) -> dict[str, int]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        source_file = str(replacement.get("placeholder_source_file") or row.get("source_file") or "")
        if source_file:
            by_file[source_file].append(row)

    expected = 0
    present = 0
    missing = 0
    invalid_source = 0
    for source_file, file_rows in by_file.items():
        path = structured_dir / source_file
        if not path.exists():
            invalid_source += len(file_rows)
            continue
        try:
            data = read_json(path)
        except Exception:
            invalid_source += len(file_rows)
            continue
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if not isinstance(blocks, list):
            invalid_source += len(file_rows)
            continue

        for row in file_rows:
            replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
            if replacement.get("status") not in {None, "", "replaced"}:
                continue
            placeholder = str(row.get("placeholder") or "")
            if not placeholder:
                example_ref = str(row.get("example_ref") or row.get("example_id") or "")
                placeholder = f"[[SEE_EXAMPLE:{example_ref}]]" if example_ref else ""
            block_index = _safe_block_index(replacement.get("placeholder_block_index"))
            if block_index is None:
                block_index = _safe_block_index(row.get("start_block_index"))
            if not placeholder or block_index is None:
                invalid_source += 1
                continue
            expected += 1
            if block_index >= len(blocks):
                missing += 1
                continue
            block = blocks[block_index]
            content = str(block.get("content") or "") if isinstance(block, dict) else ""
            block_type = str(block.get("type") or "") if isinstance(block, dict) else ""
            if block_type == "example" and placeholder in content:
                present += 1
            else:
                missing += 1

    return {
        "expected_placeholder_rows": expected,
        "placeholder_blocks_present": present,
        "placeholder_blocks_missing": missing,
        "placeholder_rows_with_invalid_source": invalid_source,
    }


def _summarize_existing_example_library(
    *,
    structured_path: Path,
    project_root: Path,
    artifact_path: Path | None,
    rows: list[dict[str, Any]],
    before_hashes: dict[str, str | None],
    before_blocks: int,
    started: float,
    dry_run: bool,
) -> dict[str, Any]:
    repair_stats = _repair_existing_example_library(
        structured_dir=structured_path,
        project_root=project_root,
        rows=rows,
        dry_run=dry_run,
    )
    # Fix 4: if rows have stale indexes (placeholder blocks missing), signal fallback to re-extraction
    stale_count = repair_stats.get("index_validation", {}).get("stale", 0)
    total = len(rows)
    table_source_rebind_stats = _rebind_inline_table_sources_from_examples(
        structured_path,
        rows,
        dry_run=dry_run,
    )
    status_counts = _status_counts_for_rows(rows)
    placeholder_stats = _existing_placeholder_stats(structured_path, rows)
    split_stats = repair_stats.get("sequence_gap_split", {}) if isinstance(repair_stats.get("sequence_gap_split"), dict) else {}
    row_sequence_targets = _missing_raw_sequence_targets(project_root=project_root, rows=rows)
    current_row_ids = {
        (
            str(row.get("chapter") or "").strip().lower(),
            str(row.get("example_id") or "").strip(),
        )
        for row in rows
        if isinstance(row, dict)
        and str(row.get("chapter") or "").strip()
        and str(row.get("example_id") or "").strip()
        and (row.get("replacement") if isinstance(row.get("replacement"), dict) else {}).get("status") != "restored"
    }
    unresolved_split_targets = {
        (chapter, example_id)
        for chapter, example_id in row_sequence_targets
        if (chapter, example_id) not in current_row_ids
    }
    existing_library_warnings: list[str] = []
    if placeholder_stats.get("placeholder_blocks_missing", 0) > 0:
        existing_library_warnings.append("placeholder_blocks_missing")
    if unresolved_split_targets:
        existing_library_warnings.append("raw_sequence_gap_missing_rows")
    after_blocks = count_blocks(structured_path) if not dry_run else before_blocks
    after_hashes = _library_hashes(structured_path)
    summary = {
        "schema": "example_pipeline_summary.v1",
        "timestamp_utc": utc_now_iso(),
        "structured_dir": str(structured_path),
        "artifacts_dir": str(artifact_path) if artifact_path else None,
        "dry_run": dry_run,
        "existing_example_library_used": True,
        "example_library_preserved": True,
        "total_examples": len(rows),
        "replacement_status_counts": dict(sorted(status_counts.items())),
        "replaced_examples": status_counts.get("replaced", 0),
        "skipped_examples": len(rows) - status_counts.get("replaced", 0),
        "per_file_counts": [["example_library.json:existing_preserved", len(rows)]],
        "replacement_stats": [],
        "existing_library_repair_stats": repair_stats,
        "existing_library_warnings": existing_library_warnings,
        "raw_sequence_gap_missing_ids": sorted(
            [f"{chapter}:{example_id}" for chapter, example_id in unresolved_split_targets],
            key=natural_key,
        ),
        "table_source_rebind_stats": table_source_rebind_stats,
        "blocks_before": before_blocks,
        "blocks_after": after_blocks,
        "blocks_removed_by_example_fold": before_blocks - after_blocks,
        "existing_placeholder_stats": placeholder_stats,
        "library_hashes_before": before_hashes,
        "library_hashes_after": after_hashes,
        "formula_library_changed": before_hashes.get("formula_library.json") != after_hashes.get("formula_library.json"),
        "table_library_changed": before_hashes.get("table_library.json") != after_hashes.get("table_library.json"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    _write_artifacts(artifact_path, summary, rows)
    return summary


def apply_example_pipeline(
    structured_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    reference_structured_dir: str | Path | None = None,
    artifacts_dir: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Extract examples, fold selected spans, and write ``example_library.json``.

    The function mutates ``structured_dir`` unit files and
    ``example_library.json`` unless ``dry_run`` is true. Formula libraries are
    read only. Table libraries are normally read only, except for conservative
    source-unit rebinding of inline tables that are explicitly owned by folded
    examples.
    """

    started = time.perf_counter()
    structured_path = Path(structured_dir).resolve()
    reference_path = Path(reference_structured_dir).resolve() if reference_structured_dir else None
    artifact_path = Path(artifacts_dir).resolve() if artifacts_dir else None
    before_hashes = _library_hashes(structured_path)
    before_blocks = count_blocks(structured_path)

    existing_rows = _load_existing_example_library_rows(structured_path)
    if existing_rows:
        result = _summarize_existing_example_library(
            structured_path=structured_path,
            project_root=Path(project_root).resolve(),
            artifact_path=artifact_path,
            rows=existing_rows,
            before_hashes=before_hashes,
            before_blocks=before_blocks,
            started=started,
            dry_run=dry_run,
        )
        # Fix 4: if repair found too many stale rows, delete library and re-extract
        if isinstance(result, dict) and result.get("_fallback_to_reextract"):
            lib_path = structured_path / "example_library.json"
            if lib_path.exists() and not dry_run:
                lib_path.unlink()
            # fall through to extraction path below
        else:
            return result

    all_examples, per_file_counts, _ = extract_examples_for_structured_dir(
        structured_path,
        project_root=Path(project_root).resolve(),
    )
    examples_with_refs: list[tuple[ExampleCandidate, str | None]] = [(item, None) for item in all_examples]

    automatic_rows, _, _ = _build_rows_and_replacements(examples_with_refs)
    existing_identities = {_example_identity(row) for row in automatic_rows}
    reference_rows = _load_existing_example_library_rows(reference_path) if reference_path else []
    allowed_reference_ids = _reference_sequence_gap_targets(automatic_rows, reference_rows)
    candidate_gap_ids = _sequence_gap_target_set_from_candidates([item for item, _ in examples_with_refs])
    if candidate_gap_ids:
        candidate_chapters = {chapter for chapter, _ in candidate_gap_ids}
        raw_ids_by_chapter = _raw_example_ids_by_chapter(Path(project_root).resolve(), candidate_chapters)
        raw_ids_lower_by_chapter = {
            chapter: {example_id.lower() for example_id in example_ids}
            for chapter, example_ids in raw_ids_by_chapter.items()
        }
        allowed_reference_ids.update(
            {
                (chapter, example_id)
                for chapter, example_id in candidate_gap_ids
                if example_id.lower() in raw_ids_lower_by_chapter.get(chapter, set())
            }
        )
    reference_rows_by_id = {
        (str(row.get("chapter") or "").strip().lower(), str(row.get("example_id") or "").strip()): row
        for row in reference_rows
        if isinstance(row, dict)
    }

    sequence_gap_recovered, sequence_gap_stats = _recover_sequence_gap_examples(
        structured_dir=structured_path,
        project_root=Path(project_root).resolve(),
        examples_with_refs=examples_with_refs,
        allowed_example_ids=allowed_reference_ids,
        reference_rows_by_id=reference_rows_by_id,
    )
    if sequence_gap_recovered:
        per_file_counts.append(("sequence_gap_raw_layout_recovered", len(sequence_gap_recovered)))

    automatic_rows, _, _ = _build_rows_and_replacements(examples_with_refs)
    existing_identities = {_example_identity(row) for row in automatic_rows}
    reference_seeded, reference_seed_stats = _reference_rows_to_candidates(
        reference_structured_dir=reference_path,
        structured_dir=structured_path,
        reference_rows=reference_rows,
        existing_identities=existing_identities,
        allowed_example_ids=allowed_reference_ids,
    )
    if reference_seeded:
        per_file_counts.append(("example_library.json:reference_seeded", len(reference_seeded)))
        examples_with_refs.extend(reference_seeded)
        examples_with_refs.sort(
            key=lambda item: (
                natural_key(item[0].source_file),
                item[0].start_block_index,
                natural_key(str(item[1] or item[0].example_id)),
            )
        )

    library_rows, replace_by_file, example_refs = _build_rows_and_replacements(examples_with_refs)
    orphan_placeholder_stats = _append_orphan_placeholder_rows_from_raw(
        structured_dir=structured_path,
        project_root=Path(project_root).resolve(),
        rows=library_rows,
    )
    raw_layout_merge_stats = _merge_rows_from_raw_layout(
        structured_dir=structured_path,
        project_root=Path(project_root).resolve(),
        rows=library_rows,
    )

    replacement_stats: list[dict[str, Any]] = []
    for file_name, examples in sorted(replace_by_file.items(), key=lambda item: natural_key(item[0])):
        replacement_stats.append(
            replace_examples_in_file(
                structured_path / file_name,
                examples,
                example_refs,
                dry_run=dry_run,
            )
        )
    _refresh_rows_after_replacement(library_rows, replacement_stats)

    write_example_library(structured_path, library_rows, dry_run=dry_run)
    raw_global_order_stats = _repair_raw_layout_example_order(
        structured_dir=structured_path,
        project_root=Path(project_root).resolve(),
        rows=library_rows,
        dry_run=dry_run,
    )
    table_source_rebind_stats = _rebind_inline_table_sources_from_examples(
        structured_path,
        library_rows,
        dry_run=dry_run,
    )

    after_blocks = count_blocks(structured_path) if not dry_run else before_blocks - sum(
        item["removed_blocks"] for item in replacement_stats
    )
    after_hashes = _library_hashes(structured_path)
    status_counts = Counter(row["replacement"]["status"] for row in library_rows)
    summary = {
        "schema": "example_pipeline_summary.v1",
        "timestamp_utc": utc_now_iso(),
        "structured_dir": str(structured_path),
        "artifacts_dir": str(artifact_path) if artifact_path else None,
        "dry_run": dry_run,
        "existing_example_library_used": False,
        "example_library_preserved": False,
        "reference_structured_dir": str(reference_path) if reference_path else None,
        "reference_seed_stats": reference_seed_stats,
        "sequence_gap_recovery_stats": sequence_gap_stats,
        "orphan_placeholder_stats": orphan_placeholder_stats,
        "raw_layout_merge_stats": raw_layout_merge_stats,
        "total_examples": len(library_rows),
        "replacement_status_counts": dict(sorted(status_counts.items())),
        "replaced_examples": status_counts.get("replaced", 0),
        "skipped_examples": len(library_rows) - status_counts.get("replaced", 0),
        "per_file_counts": per_file_counts,
        "replacement_stats": replacement_stats,
        "raw_layout_global_order_stats": raw_global_order_stats,
        "table_source_rebind_stats": table_source_rebind_stats,
        "blocks_before": before_blocks,
        "blocks_after": after_blocks,
        "blocks_removed_by_example_fold": before_blocks - after_blocks,
        "library_hashes_before": before_hashes,
        "library_hashes_after": after_hashes,
        "formula_library_changed": before_hashes.get("formula_library.json") != after_hashes.get("formula_library.json"),
        "table_library_changed": before_hashes.get("table_library.json") != after_hashes.get("table_library.json"),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    _write_artifacts(artifact_path, summary, library_rows)
    return summary
