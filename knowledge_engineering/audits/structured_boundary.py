"""Structured object-boundary checks used by the textbook pipeline.

This module intentionally contains no network or model calls.  It is the
version-controlled replacement for the former ``tmp/structured_boundary_audit``
helper so the same checks run in clean clones and CI.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHAPTER_FILTER: set[str] | None = None
CHAPTER_EXCLUDE: set[str] = set()

FIGURE_CAPTION_TEXT_RE = re.compile(
    r"\bFigure\s+([A-Z]?\d+(?:\.\d+)+(?:[a-z])?)\s+([^\n]{4,400}?[.!?])",
    re.IGNORECASE,
)
EXAMPLE_HEADING_IN_TEXT_RE = re.compile(
    r"(?<!see )\bExample\s+([A-Z]?\d+(?:\.\d+)+)\s*[.:]",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"\[\[(SEE_)?(FORMULA|TABLE|FIGURE|EXAMPLE):([^\]]+)\]\]",
    re.IGNORECASE,
)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_library_rows(path: Path, key: str) -> list[dict[str, Any]]:
    payload = load_json(path, {})
    rows = payload.get(key, []) if isinstance(payload, dict) else []
    return [row for row in rows if isinstance(row, dict)]


def _chapter_name(value: str) -> str:
    match = re.fullmatch(r"(?:chapter)?(\d+)", value.strip(), re.IGNORECASE)
    if match:
        return f"chapter{int(match.group(1))}"
    match = re.fullmatch(r"(?:appendix)?([a-z]?\d+)", value.strip(), re.IGNORECASE)
    if match:
        return f"appendix{match.group(1).lower().lstrip('a')}"
    return value.strip().lower()


def parse_chapter_list(value: str | None) -> set[str] | None:
    if value is None or not value.strip():
        return None
    return {_chapter_name(item) for item in value.split(",") if item.strip()}


def chapter_in_scope(chapter: str) -> bool:
    name = _chapter_name(chapter)
    return (CHAPTER_FILTER is None or name in CHAPTER_FILTER) and name not in CHAPTER_EXCLUDE


def row_has_pdf_rule_extension(row: dict[str, Any]) -> bool:
    evidence = row.get("evidence") or {}
    refresh = evidence.get("raw_layout_refresh") or {}
    codes = refresh.get("evidence_codes") or []
    return (
        evidence.get("existing_library_repair") == "raw_layout_pdf_rule_boundary_extension"
        or evidence.get("visual_stop_source") == "pdf_rendered_horizontal_rule"
        or "pdf_rendered_horizontal_rule_extends_example" in codes
    )


def example_longer_than_raw_suspect(
    *, visual: bool, ratio: float, raw_tail_present: bool,
    pdf_rule_extension: bool = False,
) -> bool:
    return visual and raw_tail_present and ratio > 1.5 and not pdf_rule_extension


def _plain(value: Any) -> str:
    text = PLACEHOLDER_RE.sub(" ", str(value or ""))
    return re.sub(r"\s+", " ", re.sub(r"[^0-9A-Za-z]+", " ", text)).strip().lower()


def _unit_text(unit: dict[str, Any]) -> str:
    return " ".join(
        str(block.get("content") or "")
        for block in unit.get("blocks", [])
        if isinstance(block, dict) and block.get("type") not in {"example", "table", "figure", "formula"}
    )


def scan_current_placements(
    units: list[tuple[Path, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    placements: dict[str, dict[str, Any]] = {}
    for position, (path, unit) in enumerate(units):
        for block_index, block in enumerate(unit.get("blocks", [])):
            if not isinstance(block, dict):
                continue
            for match in PLACEHOLDER_RE.finditer(str(block.get("content") or "")):
                if match.group(2).upper() != "EXAMPLE":
                    continue
                placements[match.group(3)] = {
                    "unit_id": str(unit.get("id") or path.stem),
                    "unit_position": position,
                    "block_index": block_index,
                    "path": path,
                }
    return placements


def _append_issue(
    issues: list[dict[str, Any]], code: str, row: dict[str, Any], evidence: dict[str, Any]
) -> None:
    issues.append({
        "code": code,
        "chapter": row.get("chapter"),
        "resource_id": row.get("example_id") or row.get("id"),
        "source_file": row.get("source_file"),
        "evidence": evidence,
    })


def audit_example_body_duplicate_prose(
    issues: list[dict[str, Any]],
    units: list[tuple[Path, dict[str, Any]]],
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    checked = 0
    for row in rows:
        body = _plain(re.sub(r"^\s*Example\s+[A-Z]?\d+(?:\.\d+)+\s*[.:]?", "", str(row.get("content_markdown") or ""), flags=re.I))
        if len(body.split()) < 20:
            continue
        checked += 1
        for path, unit in units:
            unit_id = str(unit.get("id") or path.stem)
            if path.name == row.get("source_file") or unit_id == Path(str(row.get("source_file") or "")).stem:
                continue
            prose = _plain(_unit_text(unit))
            if body and (body in prose or prose in body) and len(prose.split()) >= 20:
                _append_issue(issues, "example_body_duplicate_in_prose", row, {
                    "duplicate_unit_id": unit_id,
                    "duplicate_source_file": path.name,
                })
                break
    return {"examples_checked": checked, "duplicates": sum(issue.get("code") == "example_body_duplicate_in_prose" for issue in issues)}


def audit_example_section_ownership(
    issues: list[dict[str, Any]],
    units: list[tuple[Path, dict[str, Any]]],
    placements: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
) -> None:
    by_name = {path.name: (index, unit) for index, (path, unit) in enumerate(units)}
    for row in rows:
        source_file = str(row.get("source_file") or "")
        current = by_name.get(source_file)
        if current is None:
            placement = placements.get(str(row.get("example_ref") or row.get("example_id") or ""))
            if placement:
                index = int(placement["unit_position"])
                current = (index, units[index][1])
        if current is None:
            continue
        index, unit = current
        if index <= 0:
            continue
        heading = str((unit.get("metadata") or {}).get("display_heading") or "")
        prose_words = len(_plain(_unit_text(unit)).split())
        reason = None
        if re.match(r"^\s*Example\s+[A-Z]?\d+(?:\.\d+)+", heading, re.I):
            reason = "example_heading_split_from_owner"
        elif prose_words and prose_words < 12 and int(row.get("start_block_index") or 0) > 0:
            reason = "short_non_prose_heading_chunk"
        if reason:
            previous_path, previous = units[index - 1]
            _append_issue(issues, "example_section_owner_mismatch", row, {
                "current_unit_id": str(unit.get("id") or Path(source_file).stem),
                "recommended_unit_id": str(previous.get("id") or previous_path.stem),
                "reason": reason,
            })


def caption_like_matches(
    content: str,
    pattern: re.Pattern[str],
    *,
    library_text_by_id: dict[str, str],
    known_ids: set[str],
) -> list[str]:
    found: list[str] = []
    for match in pattern.finditer(content):
        figure_id, candidate = match.group(1), match.group(2)
        if figure_id not in known_ids or figure_id not in library_text_by_id:
            continue
        expected = _plain(library_text_by_id[figure_id])
        actual = _plain(candidate)
        prefix = expected[: min(48, len(expected))]
        if prefix and prefix in actual:
            found.append(figure_id)
    return found


def _chunk_key(value: str) -> tuple[int, int]:
    match = re.search(r"(\d+)_([0-9]+)$", value)
    return (int(match.group(1)), int(match.group(2))) if match else (-1, -1)


def figure_recommendation_is_forward(current: str, recommended: str) -> bool:
    return bool(current and recommended and _chunk_key(recommended) > _chunk_key(current))


def figure_anchor_sort_key(row: dict[str, Any]) -> tuple[float, float, tuple[int, int]]:
    chapter, unit = _chunk_key(str(row.get("chunk") or ""))
    return (-float(row.get("score") or 0), float(row.get("distance") or 0), (-chapter, -unit))


def load_library_ids(path: Path, key: str) -> set[str]:
    ids = set()
    for row in load_library_rows(path, key):
        value = str(row.get("id") or "")
        ids.add(re.sub(r"^(?:formula|table|figure|example)_", "", value, flags=re.I))
    return {value for value in ids if value}


def ref_belongs_to_chapter(reference: str, chapter: str) -> bool:
    name = _chapter_name(chapter)
    if name.startswith("chapter"):
        match = re.match(r"(\d+)\.", reference)
        return bool(match and int(match.group(1)) == int(name.removeprefix("chapter")))
    if name.startswith("appendix"):
        number = name.removeprefix("appendix")
        return bool(re.match(rf"A{re.escape(number)}\.", reference, re.I))
    return False


def audit_fragment_residue(
    issues: list[dict[str, Any]], units: list[tuple[Path, dict[str, Any]]]
) -> None:
    marker = re.compile(r"\[\[SEE_EXAMPLE:([^\]]+)\]\]", re.I)
    for path, unit in units:
        for block_index, block in enumerate(unit.get("blocks", [])):
            if not isinstance(block, dict) or block.get("type") == "example":
                continue
            for match in marker.finditer(str(block.get("content") or "")):
                issues.append({
                    "code": "structured_fragment_residue",
                    "source_file": path.name,
                    "resource_id": match.group(1),
                    "evidence": {"reason": "standalone_body_uses_see_reference", "block_index": block_index},
                })


def inline_table_id(table_id: str) -> bool:
    return bool(re.match(r"^inline(?:_|$)", table_id, re.I))


def table_boundary_text(table_id: str, table_text_by_id: dict[str, str]) -> str:
    if inline_table_id(table_id):
        return f"table {table_id}"
    return "numbered table"


def example_boundary_compare_text(
    content: str,
    *,
    formula_latex_by_id: dict[str, str],
    figure_text_by_id: dict[str, str],
    figure_ids: set[str],
    table_text_by_id: dict[str, str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        see = bool(match.group(1))
        kind = match.group(2).upper()
        resource_id = match.group(3)
        if see:
            labels = {"FORMULA": "Equation", "TABLE": "Table", "FIGURE": "Figure", "EXAMPLE": "Example"}
            return f"{labels[kind]} {resource_id}"
        if kind == "FORMULA":
            return f"$$ {formula_latex_by_id.get(resource_id, resource_id)} $$ ({resource_id})"
        if kind == "TABLE":
            return table_text_by_id.get(resource_id, f"Table {resource_id}")
        if kind == "FIGURE":
            return figure_text_by_id.get(resource_id, f"Figure {resource_id}")
        return f"Example {resource_id}"

    return PLACEHOLDER_RE.sub(replace, content)


def example_visual_boundary_mismatch(
    *, visual: bool, ratio: float, missing_head: bool, missing_tail: bool,
) -> bool:
    del missing_head
    return visual and missing_tail and ratio < 0.7


def anchor_present_in_content(anchor: str, content_norm: str) -> bool:
    normalized_anchor = _plain(anchor)
    normalized_content = re.sub(r"\bformula\b", " ", _plain(content_norm))
    normalized_content = re.sub(r"\s+", " ", normalized_content).strip()
    return bool(normalized_anchor and normalized_anchor in normalized_content)


def audit_tables(
    issues: list[dict[str, Any]],
    units: list[tuple[Path, dict[str, Any]]],
    placements: dict[str, dict[str, Any]],
    table_rows: list[dict[str, Any]],
) -> None:
    del placements
    if not table_rows:
        payload = load_json(ROOT / "data" / "structured" / "table_library.json", {})
        table_rows = payload.get("tables", []) if isinstance(payload, dict) else []
    for table in table_rows:
        rows = table.get("rows") or []
        body_cells = [str(cell) for row in rows[1:] for cell in row if len(_plain(cell).split()) >= 4]
        if not body_cells:
            continue
        table_id = str(table.get("id") or "")
        owner = str((table.get("source") or {}).get("unit_id") or "")
        for path, unit in units:
            unit_id = str(unit.get("id") or path.stem)
            for block_index, block in enumerate(unit.get("blocks", [])):
                if not isinstance(block, dict) or block.get("type") in {"table", "example"}:
                    continue
                prose = _plain(block.get("content"))
                residue = next((cell for cell in body_cells if _plain(cell) in prose), None)
                if residue:
                    issues.append({
                        "code": "table_body_residue_in_prose",
                        "resource_id": table_id,
                        "source_file": path.name,
                        "evidence": {
                            "owner_unit_id": owner,
                            "residue_unit_id": unit_id,
                            "block_index": block_index,
                            "residue": residue,
                        },
                    })
                    break
