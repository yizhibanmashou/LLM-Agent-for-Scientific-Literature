#!/usr/bin/env python3
"""Recover Evolution source blocks that are absent from the formal delivery.

The input is the audit-produced uncovered-source ledger.  Every inserted block
keeps the exact source id, page and bbox; visual rows are deliberately rejected
because they must be attached to an existing Figure/Table resource instead.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
DEFAULT_LEDGER = ROOT / "tmp" / "book_audits" / "Evolution" / "reports" / "uncovered_source_blocks.json"
DEFAULT_BLOCK_LEDGER = ROOT / "tmp" / "book_audits" / "Evolution" / "ledgers" / "blocks.json"
UNIT_RE = re.compile(r"^Evolution_(?:chapter|appendix)\d+_\d{3}\.json$", re.I)
TEXT_LABELS = {
    "abstract", "display_formula", "doc_title", "footnote", "inline_formula",
    "paragraph_title", "text", "vision_footnote",
}
VISUAL_LABELS = {"chart", "figure_title", "image", "table"}
RESOURCE_OWNERS = {
    "Evolution_appendix2:p014:b2": ("table", "Evolution_appendix2", "inline_2"),
    "Evolution_appendix4:p018:b2": ("table", "Evolution_appendix4", "inline_4"),
    "Evolution_chapter18:p025:b2": ("figure", "Evolution_chapter18", "18.9"),
    "Evolution_chapter21:p012:b3": ("figure", "Evolution_chapter21", "21.3"),
    "Evolution_chapter21:p012:b5": ("figure", "Evolution_chapter21", "21.3"),
    "Evolution_chapter21:p012:b7": ("figure", "Evolution_chapter21", "21.3"),
    "Evolution_chapter21:p012:b8": ("figure", "Evolution_chapter21", "21.3"),
    "Evolution_chapter21:p012:b11": ("figure", "Evolution_chapter21", "21.3"),
    "Evolution_chapter23:p013:b3": ("table", "Evolution_chapter23", "23.2"),
    "Evolution_chapter23:p015:b6": ("example", "Evolution_chapter23", "23.2"),
    "Evolution_chapter28:p049:b3": ("table", "Evolution_chapter28", "inline_1"),
    "Evolution_chapter6:p025:b5": ("figure", "Evolution_chapter6", "6.5"),
    "Evolution_chapter8:p019:b4": ("figure", "Evolution_chapter8", "8.6"),
    "Evolution_chapter9:p012:b3": ("figure", "Evolution_chapter9", "9.1"),
    "Evolution_chapter9:p050:b2": ("example", "Evolution_chapter9", "9.13"),
    "Evolution_chapter9:p050:b3": ("example", "Evolution_chapter9", "9.13"),
    "Evolution_chapter12:p047:b18": ("example", "Evolution_chapter12", "12.9"),
    "Evolution_chapter22:p042:b3": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b4": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b12": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b13": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b14": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b16": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter22:p042:b17": ("example", "Evolution_chapter22", "22.16"),
    "Evolution_chapter25:p014:b10": ("example", "Evolution_chapter25", "25.5"),
    "Evolution_chapter25:p014:b11": ("example", "Evolution_chapter25", "25.5"),
    "Evolution_chapter25:p014:b12": ("example", "Evolution_chapter25", "25.5"),
}
BLOCK_OWNERS = {
    "Evolution_appendix1:p014:b14": ("Evolution_appendix1_015", 0),
    "Evolution_appendix1:p017:b5": ("Evolution_appendix1_016", 0),
    "Evolution_appendix3:p009:b2": ("Evolution_appendix3_005", 3),
    "Evolution_chapter11:p010:b5": ("Evolution_chapter11_007", 0),
    "Evolution_chapter13:p011:b7": ("Evolution_chapter13_002", 0),
    "Evolution_chapter15:p007:b8": ("Evolution_chapter15_006", 1),
    "Evolution_chapter21:p014:b14": ("Evolution_chapter21_013", 0),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_order(source_id: str) -> tuple[int, str]:
    match = re.search(r":p(\d+):b(.+)$", source_id)
    if not match:
        raise ValueError(f"invalid source id: {source_id}")
    return int(match.group(1)), match.group(2)


def block_type(label: str) -> str:
    if label in {"display_formula", "inline_formula"}:
        return "derivation"
    return "discussion"


def provenance(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_page": row["master_page"],
        "source_pages": [row["master_page"]],
        "source_block_ids": [row["source_block_id"]],
        "source_bboxes": [row["bbox"]],
        "provenance_score": 1.0,
    }


def append_provenance(target: dict[str, Any], row: dict[str, Any]) -> None:
    source_id = row["source_block_id"]
    if source_id in (target.get("source_block_ids") or []):
        return
    target["source_block_ids"] = list(dict.fromkeys([*(target.get("source_block_ids") or []), source_id]))
    target["source_pages"] = sorted(set(target.get("source_pages") or []) | {row["master_page"]})
    target["source_page"] = target["source_pages"][0]
    target["source_bboxes"] = [*(target.get("source_bboxes") or []), row["bbox"]]
    target["provenance_score"] = 1.0
    target["coverage_repair"] = "authoritative_chapter_pdf_source_block"


def resource_library(kind: str) -> tuple[Path, str]:
    if kind == "figure":
        return STRUCTURED / "Evolution_figure_library.json", "figures"
    if kind == "table":
        return STRUCTURED / "Evolution_table_library.json", "tables"
    return STRUCTURED / "example_library.json", "examples"


def load_units() -> dict[str, list[tuple[Path, dict[str, Any]]]]:
    by_chapter: dict[str, list[tuple[Path, dict[str, Any]]]] = defaultdict(list)
    for path in sorted(STRUCTURED.glob("Evolution_*.json")):
        if not UNIT_RE.fullmatch(path.name):
            continue
        unit = read_json(path)
        by_chapter[str(unit.get("metadata", {}).get("chapter") or "")].append((path, unit))
    return by_chapter


def explicit_ids(unit: dict[str, Any]) -> list[str]:
    block_ids = [
        source_id
        for block in unit.get("blocks") or []
        for source_id in block.get("source_block_ids") or []
        if isinstance(source_id, str)
    ]
    heading_ids = unit.get("metadata", {}).get("heading_source", {}).get("source_block_ids") or []
    return [*block_ids, *(source_id for source_id in heading_ids if isinstance(source_id, str))]


def target_unit(
    units: list[tuple[Path, dict[str, Any]]], source_id: str,
    block_anchors: list[tuple[tuple[int, str], str, int]],
) -> tuple[Path, dict[str, Any], int]:
    target_order = source_order(source_id)
    anchors: list[tuple[tuple[int, str], Path, dict[str, Any], int]] = []
    for path, unit in units:
        for index, block in enumerate(unit.get("blocks") or []):
            for anchor in block.get("source_block_ids") or []:
                if isinstance(anchor, str) and ":p" in anchor:
                    anchors.append((source_order(anchor), path, unit, index))
    later = [item for item in anchors if item[0] > target_order]
    if later:
        _, path, unit, index = min(later, key=lambda item: item[0])
        return path, unit, index
    if anchors:
        _, path, unit, index = max(anchors, key=lambda item: item[0])
        return path, unit, index + 1
    unit_by_id = {unit["id"]: (path, unit) for path, unit in units}
    later_ledger = [item for item in block_anchors if item[0] > target_order and item[1] in unit_by_id]
    if later_ledger:
        _, unit_id, index = min(later_ledger, key=lambda item: item[0])
        path, unit = unit_by_id[unit_id]
        return path, unit, min(index, len(unit.get("blocks") or []))
    earlier_ledger = [item for item in block_anchors if item[0] < target_order and item[1] in unit_by_id]
    if earlier_ledger:
        _, unit_id, index = max(earlier_ledger, key=lambda item: item[0])
        path, unit = unit_by_id[unit_id]
        return path, unit, min(index + 1, len(unit.get("blocks") or []))
    path, unit = units[0]
    return path, unit, 0


def repair(ledger: Path, block_ledger: Path, *, check: bool) -> dict[str, Any]:
    rows = read_json(ledger)
    units_by_chapter = load_units()
    units_by_id = {
        unit["id"]: (path, unit)
        for units in units_by_chapter.values()
        for path, unit in units
    }
    profile = read_json(ROOT / "book_audits" / "Evolution.json")
    excluded = {entry["source_block_id"] for entry in profile.get("source_block_exclusions") or []}
    resource_data: dict[str, tuple[Path, str, dict[str, Any]]] = {}
    for kind in {owner[0] for owner in RESOURCE_OWNERS.values()}:
        path, key = resource_library(kind)
        resource_data[kind] = (path, key, read_json(path))
    anchors_by_chapter: dict[str, list[tuple[tuple[int, str], str, int]]] = defaultdict(list)
    for row in read_json(block_ledger):
        for source_id in row.get("source_block_ids") or []:
            if isinstance(source_id, str) and ":p" in source_id:
                anchors_by_chapter[str(row.get("chapter") or "")].append(
                    (source_order(source_id), str(row.get("unit_id") or ""), int(row.get("block_index") or 0))
                )
    present = {
        source_id
        for units in units_by_chapter.values()
        for _, unit in units
        for source_id in explicit_ids(unit)
    }
    present.update(
        source_id
        for _, key, data in resource_data.values()
        for item in (data[key].values() if isinstance(data[key], dict) else data[key])
        for source_id in item.get("source_block_ids") or []
        if isinstance(source_id, str)
    )
    inserted: list[str] = []
    attached: list[str] = []
    visual: list[str] = []
    changed: dict[Path, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: (item["chapter"], source_order(item["source_block_id"]))):
        source_id = row["source_block_id"]
        if source_id in excluded:
            continue
        if source_id in present:
            continue
        if source_id in BLOCK_OWNERS:
            unit_id, block_index = BLOCK_OWNERS[source_id]
            path, unit = units_by_id[unit_id]
            append_provenance(unit["blocks"][block_index], row)
            changed[path] = unit
            present.add(source_id)
            attached.append(source_id)
            continue
        if source_id in RESOURCE_OWNERS:
            kind, chapter, resource_id = RESOURCE_OWNERS[source_id]
            _, key, data = resource_data[kind]
            resources = data[key]
            candidates = resources.values() if isinstance(resources, dict) else resources
            matches = [
                item for item in candidates
                if str(item.get("chapter") or (item.get("source") or {}).get("chapter") or "") == chapter
                and str(item.get("example_id") or item.get("id")) == resource_id
            ]
            if len(matches) != 1:
                raise ValueError(f"resource owner is ambiguous: {source_id} -> {kind}:{chapter}:{resource_id}")
            append_provenance(matches[0], row)
            present.add(source_id)
            attached.append(source_id)
            continue
        if row.get("label") in {"doc_title", "paragraph_title"} and row.get("chapter_page") == 1:
            path, unit = units_by_chapter[row["chapter"]][0]
            heading = unit.setdefault("metadata", {}).setdefault("heading_source", {})
            heading["source_block_ids"] = list(dict.fromkeys([
                *(heading.get("source_block_ids") or []), source_id,
            ]))
            unit["metadata"]["source_heading_aliases"] = list(dict.fromkeys([
                *(unit["metadata"].get("source_heading_aliases") or []), row["content"],
            ]))
            changed[path] = unit
            present.add(source_id)
            attached.append(source_id)
            continue
        label = row["label"]
        if label in VISUAL_LABELS:
            visual.append(source_id)
            continue
        if label not in TEXT_LABELS or not str(row.get("content") or "").strip():
            raise ValueError(f"unsupported uncovered source row: {source_id} ({label})")
        units = units_by_chapter.get(row["chapter"])
        if not units:
            raise ValueError(f"chapter has no structured units: {row['chapter']}")
        path, unit, index = target_unit(units, source_id, anchors_by_chapter.get(row["chapter"], []))
        unit.setdefault("blocks", []).insert(index, {
            "type": block_type(label),
            "content": row["content"],
            **provenance(row),
            "coverage_repair": "authoritative_chapter_pdf_source_block",
        })
        present.add(source_id)
        inserted.append(source_id)
        changed[path] = unit
    if visual:
        raise ValueError(
            "visual source blocks require explicit Figure/Table ownership: "
            + ", ".join(visual)
        )
    if not check:
        for path, unit in changed.items():
            write_json(path, unit)
        for path, _, data in resource_data.values():
            write_json(path, data)
    return {
        "schema": "evolution_source_coverage_repair.v1",
        "ledger": str(ledger.relative_to(ROOT)),
        "inserted": inserted,
        "attached": attached,
        "changed_files": [str(path.relative_to(ROOT)) for path in sorted(changed)],
        "valid": not visual,
        "check_only": check,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--block-ledger", type=Path, default=DEFAULT_BLOCK_LEDGER)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        report = repair(args.ledger.resolve(), args.block_ledger.resolve(), check=args.check)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
