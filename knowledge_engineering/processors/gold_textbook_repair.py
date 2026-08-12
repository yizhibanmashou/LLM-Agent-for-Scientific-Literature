"""Gold textbook comparison and guarded structured repair helpers.

The gold Markdown reviewed by a human is useful as a semantic fixture, but it
can still contain small presentation mistakes such as a skipped chunk number.
This module therefore treats the gold file as evidence about headings, example
boundaries, and table ownership, while keeping the structured directory as the
source of stable unit ids.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from knowledge_engineering.core.common import (
    read_json,
    sort_table_ref_keys,
    sort_table_refs,
    table_reference_key,
    utc_now_iso,
    write_json,
)

CHUNK_FILE_RE = re.compile(r"^((?:chapter|appendix)\d+)_(\d+)\.json$", re.IGNORECASE)
HEADING_RE = re.compile(r"^##\s+(?P<unit>\S+)\s+[·路]\s+(?P<heading>.+?)\s*$")
EXAMPLE_RE = re.compile(
    r"^>\s+\*\*Example\s+(?P<example_id>[^*]+?)\*\*\s+[·路]\s+ref:\s+`(?P<ref>[^`]+)`"
    r"\s+[·路]\s+source:\s+`(?P<source>[^`]+)`\s+[·路]\s+blocks\s+"
    r"(?P<start>\d+)\s*[–-]\s*(?P<end>\d+)"
)
TABLE_RE = re.compile(
    r"^>+\s+\*\*(?P<label>(?:Table\s+\d+\.\d+[A-Za-z]?|Inline Table\s+\d+))\*\*"
    r"\s+[·路]\s+`(?P<table_id>[^`]+)`\s+[·路]\s+page\s+(?P<page>.+?)"
    r"\s+[·路]\s+source:\s+`(?P<source>[^`]+)`"
)
TABLE_PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?TABLE:(?P<table_id>[^\]]+)\]\]", re.IGNORECASE)
CANONICAL_TABLE_RE = re.compile(r"\[\[TABLE:(?P<table_id>[^\]]+)\]\]", re.IGNORECASE)
EXAMPLE_PLACEHOLDER_RE = re.compile(r"\[\[SEE_EXAMPLE:(?P<example_ref>[^\]]+)\]\]", re.IGNORECASE)
ASSET_LINE_RE = re.compile(r"^>+\s+\*\*(?:Formula|Table|Inline Table)\b", re.IGNORECASE)


@dataclass(frozen=True)
class GoldChunk:
    gold_unit_id: str
    heading: str
    text: str
    order: int


@dataclass(frozen=True)
class GoldExample:
    example_id: str
    example_ref: str
    gold_source_file: str
    start_block_index: int
    end_block_index: int
    order: int


@dataclass(frozen=True)
class GoldTable:
    table_id: str
    label: str
    gold_source_unit_id: str
    page: str
    order: int


@dataclass(frozen=True)
class GoldTextbookSignals:
    chunks: list[GoldChunk]
    examples: list[GoldExample]
    tables: list[GoldTable]


def parse_gold_textbook(path: str | Path) -> GoldTextbookSignals:
    text = Path(path).read_text(encoding="utf-8")
    chunks: list[GoldChunk] = []
    examples: list[GoldExample] = []
    tables: list[GoldTable] = []

    current_unit = ""
    current_heading = ""
    current_lines: list[str] = []
    chunk_order = 0

    def flush_chunk() -> None:
        nonlocal current_lines
        if not current_unit:
            return
        chunks.append(
            GoldChunk(
                gold_unit_id=current_unit,
                heading=current_heading,
                text=_normalize_match_text("\n".join(current_lines)),
                order=chunk_order,
            )
        )
        current_lines = []

    for raw_line in text.splitlines():
        heading_match = HEADING_RE.match(raw_line)
        if heading_match:
            flush_chunk()
            chunk_order += 1
            current_unit = heading_match.group("unit").strip()
            current_heading = heading_match.group("heading").strip()
            continue

        example_match = EXAMPLE_RE.match(raw_line)
        if example_match:
            examples.append(
                GoldExample(
                    example_id=example_match.group("example_id").strip(),
                    example_ref=example_match.group("ref").strip(),
                    gold_source_file=example_match.group("source").strip(),
                    start_block_index=int(example_match.group("start")),
                    end_block_index=int(example_match.group("end")),
                    order=len(examples),
                )
            )

        table_match = TABLE_RE.match(raw_line)
        if table_match:
            source_file = table_match.group("source").strip()
            tables.append(
                GoldTable(
                    table_id=table_match.group("table_id").strip(),
                    label=table_match.group("label").strip(),
                    gold_source_unit_id=Path(source_file).stem,
                    page=table_match.group("page").strip(),
                    order=len(tables),
                )
            )

        if current_unit:
            current_lines.append(raw_line)

    flush_chunk()
    return GoldTextbookSignals(chunks=chunks, examples=examples, tables=tables)


def compare_gold_to_textbook(gold_path: str | Path, candidate_path: str | Path) -> dict[str, Any]:
    gold = parse_gold_textbook(gold_path)
    candidate = parse_gold_textbook(candidate_path)
    return {
        "generated_at": utc_now_iso(),
        "gold_path": str(gold_path),
        "candidate_path": str(candidate_path),
        "heading_mismatches": _compare_headings_by_order(gold.chunks, candidate.chunks),
        "example_mismatches": _compare_examples(gold.examples, candidate.examples),
        "table_mismatches": _compare_tables(gold.tables, candidate.tables),
    }


def apply_gold_textbook_repair(
    *,
    structured_dir: str | Path,
    gold_path: str | Path,
    chapter: str = "chapter25",
    artifacts_dir: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Apply guarded heading/example/table repairs inferred from a gold textbook.

    The function does not rename chunk files. Gold chunk ids are mapped back to
    structured units by content similarity first and ordinal position second, so
    a skipped number in the gold file does not cause a destructive renumbering.
    """

    structured_path = Path(structured_dir)
    gold = parse_gold_textbook(gold_path)
    unit_paths = _chapter_unit_paths(structured_path, chapter)
    units = [_read_unit(path) for path in unit_paths]
    unit_by_id = {str(unit.get("id") or Path(path).stem): unit for path, unit in zip(unit_paths, units)}
    unit_id_by_gold_id, heading_repairs = _repair_headings(units, gold.chunks)
    example_repairs = _repair_examples(
        structured_path,
        unit_by_id,
        unit_id_by_gold_id,
        gold.examples,
        dry_run=dry_run,
    )
    table_repairs = _repair_tables(
        structured_path,
        units,
        unit_id_by_gold_id,
        gold.tables,
        chapter,
        dry_run=dry_run,
    )

    touched_units = set(heading_repairs["touched_units"])
    touched_units.update(example_repairs.get("touched_units", []))
    touched_units.update(table_repairs.get("touched_units", []))

    if not dry_run:
        for path, unit in zip(unit_paths, units):
            unit_id = str(unit.get("id") or path.stem)
            if unit_id in touched_units:
                write_json(path, unit)

    summary = {
        "schema": "gold_textbook_repair.v1",
        "generated_at": utc_now_iso(),
        "structured_dir": str(structured_path),
        "gold_path": str(gold_path),
        "chapter": chapter,
        "dry_run": dry_run,
        "unit_id_by_gold_id": unit_id_by_gold_id,
        "heading_repairs": heading_repairs,
        "example_repairs": example_repairs,
        "table_repairs": table_repairs,
    }
    if artifacts_dir:
        artifact_path = Path(artifacts_dir)
        artifact_path.mkdir(parents=True, exist_ok=True)
        write_json(artifact_path / "gold_textbook_repair_summary.json", summary)
    return summary


def render_compare_report(diff: dict[str, Any]) -> str:
    gap_matches = [
        item
        for item in diff.get("heading_mismatches") or []
        if isinstance(item, dict) and item.get("status") == "matched_after_id_gap"
    ]
    lines = [
        "# Gold Textbook Comparison",
        "",
        f"Gold: `{diff.get('gold_path')}`",
        f"Candidate: `{diff.get('candidate_path')}`",
        "",
        "## Summary",
        "",
        f"- Heading mismatches: {len(diff.get('heading_mismatches') or [])}",
        f"- Example mismatches: {len(diff.get('example_mismatches') or [])}",
        f"- Table mismatches: {len(diff.get('table_mismatches') or [])}",
    ]
    if gap_matches:
        lines.append(f"- Heading id-gap matches: {len(gap_matches)}")
    for section, key in [
        ("Heading Mismatches", "heading_mismatches"),
        ("Example Mismatches", "example_mismatches"),
        ("Table Mismatches", "table_mismatches"),
    ]:
        rows = diff.get(key) or []
        if not rows:
            continue
        lines.extend(["", f"## {section}", ""])
        for row in rows[:50]:
            if key == "heading_mismatches" and row.get("status") == "matched_after_id_gap":
                lines.append(
                    f"- `{row.get('key')}`: gold=`{row.get('gold')}` matched candidate order `{row.get('candidate_order')}` after id gap"
                )
                continue
            lines.append(f"- `{row.get('key')}`: gold=`{row.get('gold')}` candidate=`{row.get('candidate')}`")
    return "\n".join(lines).strip() + "\n"


def _chapter_unit_paths(structured_dir: Path, chapter: str) -> list[Path]:
    chapter = str(chapter or "").strip().lower()
    paths: list[Path] = []
    for path in structured_dir.glob(f"{chapter}_*.json"):
        if CHUNK_FILE_RE.fullmatch(path.name):
            paths.append(path)
    return sorted(paths, key=_unit_path_sort_key)


def _unit_path_sort_key(path: Path) -> tuple[int, str]:
    match = CHUNK_FILE_RE.fullmatch(path.name)
    return (int(match.group(2)) if match else 999999, path.name)


def _read_unit(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def _repair_headings(units: list[dict[str, Any]], gold_chunks: list[GoldChunk]) -> tuple[dict[str, str], dict[str, Any]]:
    unit_texts = {
        str(unit.get("id") or ""): _normalize_unit_text(unit)
        for unit in units
    }
    used_units: set[str] = set()
    unit_id_by_gold_id: dict[str, str] = {}
    changes: list[dict[str, Any]] = []

    for order, gold_chunk in enumerate(gold_chunks):
        unit_id = _best_unit_for_gold_chunk(gold_chunk, units, unit_texts, used_units, fallback_index=order)
        if not unit_id:
            continue
        used_units.add(unit_id)
        unit_id_by_gold_id[gold_chunk.gold_unit_id] = unit_id
        unit = next(item for item in units if str(item.get("id") or "") == unit_id)
        metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
        before = {
            "section": metadata.get("section"),
            "section_level_1": metadata.get("section_level_1"),
            "section_level_2": metadata.get("section_level_2"),
            "heading_path": metadata.get("heading_path"),
            "display_heading": metadata.get("display_heading"),
        }
        _set_heading_metadata(unit, gold_chunk.heading)
        after_metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
        after = {
            "section": after_metadata.get("section"),
            "section_level_1": after_metadata.get("section_level_1"),
            "section_level_2": after_metadata.get("section_level_2"),
            "heading_path": after_metadata.get("heading_path"),
            "display_heading": after_metadata.get("display_heading"),
        }
        if before != after:
            changes.append(
                {
                    "unit_id": unit_id,
                    "gold_unit_id": gold_chunk.gold_unit_id,
                    "before": before,
                    "after": after,
                }
            )

    return unit_id_by_gold_id, {
        "changed": len(changes),
        "changes": changes,
        "touched_units": sorted({str(item["unit_id"]) for item in changes}),
    }


def _repair_examples(
    structured_dir: Path,
    unit_by_id: dict[str, dict[str, Any]],
    unit_id_by_gold_id: dict[str, str],
    gold_examples: list[GoldExample],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    path = structured_dir / "example_library.json"
    if not path.exists():
        return {"changed": 0, "changes": [], "touched_units": []}
    payload = read_json(path)
    rows = payload.get("examples") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {"changed": 0, "changes": [], "touched_units": []}

    gold_by_id = {item.example_id: item for item in gold_examples}
    touched_units: set[str] = set()
    changes: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        example_id = str(row.get("example_id") or row.get("example_ref") or "").strip()
        gold = gold_by_id.get(example_id)
        if gold is None:
            continue
        source_unit = _map_gold_unit_id(gold.gold_source_file, unit_id_by_gold_id)
        source_file = f"{source_unit}.json" if source_unit else gold.gold_source_file
        before = {
            "source_file": row.get("source_file"),
            "start_block_index": row.get("start_block_index"),
            "end_block_index": row.get("end_block_index"),
        }
        row["source_file"] = source_file
        row["start_block_index"] = gold.start_block_index
        row["end_block_index"] = gold.end_block_index
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        replacement["source_block_span"] = [gold.start_block_index, gold.end_block_index]
        row["replacement"] = replacement

        unit = unit_by_id.get(source_unit)
        if unit is not None:
            touched_units.add(source_unit)
            _ensure_example_placeholder(unit, example_id, gold.start_block_index)

        after = {
            "source_file": row.get("source_file"),
            "start_block_index": row.get("start_block_index"),
            "end_block_index": row.get("end_block_index"),
        }
        if before != after:
            changes.append({"example_id": example_id, "before": before, "after": after})

    if not dry_run:
        write_json(path, payload)
    return {
        "changed": len(changes),
        "changes": changes,
        "touched_units": sorted(touched_units),
    }


def _repair_tables(
    structured_dir: Path,
    units: list[dict[str, Any]],
    unit_id_by_gold_id: dict[str, str],
    gold_tables: list[GoldTable],
    chapter: str,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    path = structured_dir / "table_library.json"
    if not path.exists():
        return {"changed": 0, "changes": [], "touched_units": []}
    payload = read_json(path)
    rows = payload.get("tables") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {"changed": 0, "changes": [], "touched_units": []}

    unit_by_id = {str(unit.get("id") or ""): unit for unit in units}
    canonical_by_table = _canonical_table_units(units)
    gold_by_id = {table.table_id: table for table in gold_tables}
    touched_units: set[str] = set()
    changes: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue
        table_id = str(row.get("id") or "").strip()
        gold = gold_by_id.get(table_id)
        if gold is None:
            continue
        mapped_source = _map_gold_unit_id(gold.gold_source_unit_id, unit_id_by_gold_id)
        source_unit = canonical_by_table.get(table_id) or mapped_source
        if not source_unit:
            continue
        source = row.get("source") if isinstance(row.get("source"), dict) else {}
        before = dict(source)
        source["chapter"] = chapter
        source["unit_id"] = source_unit
        source["subsection"] = _unit_subsection(unit_by_id.get(source_unit) or {})
        row["source"] = source
        if str(row.get("label_format") or "").strip() != gold.label:
            row["label_format"] = gold.label
        if source_unit in unit_by_id:
            _ensure_canonical_table_placeholder(unit_by_id[source_unit], table_id)
            touched_units.add(source_unit)
        if before != source:
            changes.append({"table_id": table_id, "before": before, "after": dict(source)})

    if not dry_run:
        write_json(path, payload)
    for unit_id in touched_units:
        _refresh_unit_table_metadata(unit_by_id[unit_id], chapter)
    return {
        "changed": len(changes),
        "changes": changes,
        "touched_units": sorted(touched_units),
    }


def _compare_headings_by_order(gold: list[GoldChunk], candidate: list[GoldChunk]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    matched_candidate_indexes: set[int] = set()
    for gold_index, gold_chunk in enumerate(gold):
        candidate_index = gold_index
        if (
            candidate_index < len(candidate)
            and candidate_index not in matched_candidate_indexes
            and candidate[candidate_index].heading == gold_chunk.heading
        ):
            matched_candidate_indexes.add(candidate_index)
            continue

        shifted_index = next(
            (
                idx
                for idx, candidate_chunk in enumerate(candidate)
                if idx not in matched_candidate_indexes and candidate_chunk.heading == gold_chunk.heading
            ),
            None,
        )
        if shifted_index is not None:
            matched_candidate_indexes.add(shifted_index)
            rows.append(
                {
                    "key": f"order:{gold_index + 1}",
                    "gold": gold_chunk.heading,
                    "candidate": candidate[shifted_index].heading,
                    "status": "matched_after_id_gap",
                    "candidate_order": shifted_index + 1,
                }
            )
            continue

        candidate_heading = candidate[candidate_index].heading if candidate_index < len(candidate) else None
        rows.append({"key": f"order:{gold_index + 1}", "gold": gold_chunk.heading, "candidate": candidate_heading})

    for index, candidate_chunk in enumerate(candidate):
        if index not in matched_candidate_indexes and index >= len(gold):
            rows.append({"key": f"order:{index + 1}", "gold": None, "candidate": candidate_chunk.heading})
    return rows


def _compare_examples(gold: list[GoldExample], candidate: list[GoldExample]) -> list[dict[str, Any]]:
    candidate_by_id = {item.example_id: item for item in candidate}
    rows: list[dict[str, Any]] = []
    for item in gold:
        current = candidate_by_id.get(item.example_id)
        gold_value = {
            "source": item.gold_source_file,
            "span": [item.start_block_index, item.end_block_index],
        }
        candidate_value = None
        if current is not None:
            candidate_value = {
                "source": current.gold_source_file,
                "span": [current.start_block_index, current.end_block_index],
            }
        if gold_value != candidate_value:
            rows.append({"key": item.example_id, "gold": gold_value, "candidate": candidate_value})
    return rows


def _compare_tables(gold: list[GoldTable], candidate: list[GoldTable]) -> list[dict[str, Any]]:
    candidate_by_id = {item.table_id: item for item in candidate}
    rows: list[dict[str, Any]] = []
    for item in gold:
        current = candidate_by_id.get(item.table_id)
        gold_value = {"source": item.gold_source_unit_id, "label": item.label}
        candidate_value = None
        if current is not None:
            candidate_value = {"source": current.gold_source_unit_id, "label": current.label}
        if gold_value != candidate_value:
            rows.append({"key": item.table_id, "gold": gold_value, "candidate": candidate_value})
    return rows


def _set_heading_metadata(unit: dict[str, Any], heading: str) -> None:
    metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
    unit["metadata"] = metadata
    parts = [part.strip() for part in str(heading or "").split(" / ") if part.strip()]
    level_1 = parts[0] if parts else "Introduction"
    level_2 = parts[1] if len(parts) > 1 else None
    metadata["section"] = level_1
    metadata["subsections"] = [level_2] if level_2 else []
    metadata["section_level_1"] = level_1
    metadata["section_level_2"] = level_2
    metadata["heading_path"] = [level_1, level_2] if level_2 else [level_1]
    metadata["display_heading"] = level_2 or level_1


def _best_unit_for_gold_chunk(
    gold_chunk: GoldChunk,
    units: list[dict[str, Any]],
    unit_texts: dict[str, str],
    used_units: set[str],
    *,
    fallback_index: int,
) -> str:
    best: tuple[float, str] | None = None
    gold_text = gold_chunk.text
    for unit in units:
        unit_id = str(unit.get("id") or "")
        if not unit_id or unit_id in used_units:
            continue
        score = _match_score(gold_text, unit_texts.get(unit_id, ""))
        if best is None or score > best[0]:
            best = (score, unit_id)
    if best is not None and best[0] >= 0.08:
        return best[1]
    if fallback_index < len(units):
        fallback_id = str(units[fallback_index].get("id") or "")
        if fallback_id not in used_units:
            return fallback_id
    return best[1] if best else ""


def _match_score(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    left_tokens = left.split()
    right_tokens = right.split()
    if not left_tokens or not right_tokens:
        return 0.0
    anchors = [
        " ".join(left_tokens[:24]),
        " ".join(left_tokens[max(0, len(left_tokens) // 2 - 12) : max(0, len(left_tokens) // 2 + 12)]),
    ]
    anchor_hits = sum(1 for anchor in anchors if anchor and anchor in right)
    overlap = len(set(left_tokens[:160]) & set(right_tokens[:160])) / max(1, len(set(left_tokens[:160])))
    ratio = SequenceMatcher(None, " ".join(left_tokens[:120]), " ".join(right_tokens[:120])).ratio()
    return anchor_hits * 2.0 + overlap + ratio * 0.25


def _normalize_unit_text(unit: dict[str, Any]) -> str:
    blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
    return _normalize_match_text("\n".join(str(block.get("content") or "") for block in blocks if isinstance(block, dict)))


def _normalize_match_text(text: str) -> str:
    value = str(text or "")
    value = re.sub(r"`[^`]*`", " ", value)
    value = re.sub(r"\[\[(?:SEE_)?(?:FORMULA|TABLE|EXAMPLE):([^\]]+)\]\]", r" \1 ", value, flags=re.IGNORECASE)
    value = re.sub(r"^>+\s?", " ", value, flags=re.MULTILINE)
    value = re.sub(r"\*\*|\$+|<[^>]+>", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def _map_gold_unit_id(gold_source: str, unit_id_by_gold_id: dict[str, str]) -> str:
    gold_unit = Path(str(gold_source or "")).stem
    return unit_id_by_gold_id.get(gold_unit, gold_unit)


def _ensure_example_placeholder(unit: dict[str, Any], example_id: str, block_index: int) -> None:
    placeholder = f"[[SEE_EXAMPLE:{example_id}]]"
    blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
    if not blocks:
        return
    for block in blocks:
        if isinstance(block, dict) and placeholder in str(block.get("content") or ""):
            block["type"] = "example"
            block["content"] = placeholder
            return
    if 0 <= block_index < len(blocks) and isinstance(blocks[block_index], dict):
        blocks[block_index]["type"] = "example"
        blocks[block_index]["content"] = placeholder


def _ensure_canonical_table_placeholder(unit: dict[str, Any], table_id: str) -> None:
    blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
    if not blocks:
        return
    for block in blocks:
        if not isinstance(block, dict):
            continue
        content = str(block.get("content") or "")
        for match in TABLE_PLACEHOLDER_RE.finditer(content):
            if match.group("table_id").strip() == table_id:
                block["content"] = (
                    content[: match.start()]
                    + f"[[TABLE:{table_id}]]"
                    + content[match.end() :]
                ).strip()
                block["type"] = "table" if block["content"] == f"[[TABLE:{table_id}]]" else block.get("type", "discussion")
                return
    blocks.append({"type": "table", "content": f"[[TABLE:{table_id}]]"})


def _canonical_table_units(units: list[dict[str, Any]]) -> dict[str, str]:
    canonical: dict[str, str] = {}
    for unit in units:
        unit_id = str(unit.get("id") or "")
        blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            for match in CANONICAL_TABLE_RE.finditer(str(block.get("content") or "")):
                canonical.setdefault(match.group("table_id").strip(), unit_id)
    return canonical


def _unit_subsection(unit: dict[str, Any]) -> str:
    metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
    return str(metadata.get("display_heading") or metadata.get("section_level_2") or metadata.get("section") or "").strip()


def _refresh_unit_table_metadata(unit: dict[str, Any], chapter: str) -> None:
    metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
    unit["metadata"] = metadata
    refs: list[str] = []
    blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        for match in TABLE_PLACEHOLDER_RE.finditer(str(block.get("content") or "")):
            table_id = match.group("table_id").strip()
            if table_id and table_id not in refs:
                refs.append(table_id)
    metadata["table_references"] = sort_table_refs(refs)
    keys = [table_reference_key(chapter, table_id) for table_id in refs]
    metadata["table_reference_keys"] = sort_table_ref_keys([key for key in keys if key])


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare or repair structured output using a reviewed textbook Markdown fixture.")
    parser.add_argument("--structured-dir", default="data/structured", type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--candidate", type=Path, default=None)
    parser.add_argument("--chapter", default="chapter25")
    parser.add_argument("--artifacts-dir", type=Path, default=Path("tmp/structured_quality_probe/gold_textbook_repair"))
    parser.add_argument("--mode", choices=["compare", "repair"], default="compare")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "compare":
        if args.candidate is None:
            raise SystemExit("--candidate is required in compare mode")
        diff = compare_gold_to_textbook(args.gold, args.candidate)
        write_json(args.artifacts_dir / "gold_textbook_diff.json", diff)
        (args.artifacts_dir / "gold_textbook_diff.md").write_text(render_compare_report(diff), encoding="utf-8")
        print(f"[gold-textbook] wrote diff to {args.artifacts_dir}")
        return
    summary = apply_gold_textbook_repair(
        structured_dir=args.structured_dir,
        gold_path=args.gold,
        chapter=args.chapter,
        artifacts_dir=args.artifacts_dir,
        dry_run=args.dry_run,
    )
    print(
        "[gold-textbook] repair "
        f"headings={summary['heading_repairs']['changed']} "
        f"examples={summary['example_repairs']['changed']} "
        f"tables={summary['table_repairs']['changed']}"
    )


if __name__ == "__main__":
    main()
