#!/usr/bin/env python3
"""Repartition Genetics units by the logical chapter printed in the source book.

The source PDFs are contiguous page ranges rather than perfectly clipped
chapters.  This script moves only verified boundary material and keeps each
block verbatim.  It also relinks source metadata in the supporting libraries.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def unit_id(chapter: int, index: int) -> str:
    return f"Genetics_chapter{chapter}_{index:03d}"


def source_id(chapter: int, index: int) -> str:
    return unit_id(chapter, index)


def source_path(root: Path, chapter: int, index: int) -> Path:
    return root / f"{source_id(chapter, index)}.json"


def load_source(root: Path, chapter: int, index: int) -> dict[str, Any]:
    path = source_path(root, chapter, index)
    return json.loads(path.read_text(encoding="utf-8"))


def source_count(root: Path, chapter: int) -> int:
    return len(list(root.glob(f"Genetics_chapter{chapter}_*.json")))


def whole(chapter: int, start: int | None = None, end: int | None = None) -> list[tuple[int, int, slice | None]]:
    if end is None:
        return [(chapter, -(start or 1), None)]
    return [(chapter, number, None) for number in range(start or 1, end + 1)]


def expand(root: Path, items: list[tuple[int, int, slice | None]]) -> list[tuple[int, int, slice | None]]:
    expanded: list[tuple[int, int, slice | None]] = []
    for chapter, number, block_slice in items:
        limit = source_count(root, chapter)
        if number < 0:
            expanded.extend((chapter, current, block_slice) for current in range(-number, limit + 1))
            continue
        if number > limit:
            continue
        expanded.append((chapter, number, block_slice))
    return expanded


def plan(root: Path) -> dict[int, list[tuple[int, int, slice | None]]]:
    """Boundary ownership from the printed chapter-title pages, checked visually."""
    return {
        1: whole(1),
        2: whole(2),
        3: whole(3, 1, 12),
        4: whole(3, 13) + whole(4, 1, 14),
        5: whole(4, 15) + whole(5, 1, 7),
        6: whole(5, 8) + whole(6, 1, 7),
        7: whole(6, 8) + whole(7, 1, 12),
        8: whole(7, 13) + whole(8),
        9: whole(9),
        10: whole(10),
        11: whole(11, 1, 16),
        12: whole(11, 17) + whole(12) + whole(13, 1, 1),
        13: whole(13, 2) + whole(14, 1, 1) + [(14, 2, slice(0, 3))],
        14: [(14, 2, slice(3, None))] + whole(14, 3, 28),
        15: whole(14, 29) + whole(15, 1, 27),
        16: whole(15, 28) + whole(16),
        17: whole(17),
        18: whole(18) + whole(19, 1, 2),
        19: whole(19, 3, 7),
        20: whole(19, 8) + whole(20),
        21: whole(21) + whole(22, 1, 1),
        22: whole(22, 2) + whole(23, 1, 1),
        23: whole(23, 2) + whole(24, 1, 1),
        24: whole(24, 2) + whole(25, 1, 2),
        25: whole(25, 3) + whole(26, 1, 1),
        26: whole(26, 2),
        27: whole(27),
    }


def materialize(root: Path) -> tuple[dict[int, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    groups: dict[int, list[dict[str, Any]]] = {}
    origin_index: dict[str, list[dict[str, Any]]] = {}
    for target, items in plan(root).items():
        rows: list[dict[str, Any]] = []
        for source_chapter, source_number, block_slice in expand(root, items):
            original = load_source(root, source_chapter, source_number)
            row = copy.deepcopy(original)
            if block_slice is not None:
                row["blocks"] = row.get("blocks", [])[block_slice]
            if not row.get("blocks"):
                raise ValueError(f"Empty fragment from {original.get('id')}")
            row["_origin_id"] = str(original.get("id") or source_id(source_chapter, source_number))
            row["_origin_block_slice"] = None if block_slice is None else [block_slice.start, block_slice.stop]
            rows.append(row)
        groups[target] = rows
    for target, rows in groups.items():
        for index, row in enumerate(rows, 1):
            row["_new_id"] = unit_id(target, index)
            origin_index.setdefault(row["_origin_id"], []).append(row)
    return groups, origin_index


def pick_relinked_row(rows: list[dict[str, Any]], signature: str = "") -> dict[str, Any]:
    if len(rows) == 1 or not signature:
        return rows[0]
    for row in rows:
        content = "\n".join(str(block.get("content") or "") for block in row.get("blocks", []) if isinstance(block, dict))
        if signature in content:
            return row
    return rows[0]


def update_library_sources(root: Path, origin_index: dict[str, list[dict[str, Any]]]) -> None:
    for name, key, signature_key in (
        ("formula_library.json", "formulas", "latex"),
        ("table_library.json", "tables", "html"),
    ):
        path = root / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record in payload.get(key, []):
            if not isinstance(record, dict):
                continue
            source = record.get("source") if isinstance(record.get("source"), dict) else {}
            old_id = str(source.get("unit_id") or "")
            candidates = origin_index.get(old_id, [])
            if not candidates:
                continue
            row = pick_relinked_row(candidates, str(record.get(signature_key) or ""))
            source["chapter"] = row["_new_id"].rsplit("_", 1)[0]
            source["unit_id"] = row["_new_id"]
            record["source"] = source
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    figure_path = root.parent / "figure_library.json"
    figure_payload = json.loads(figure_path.read_text(encoding="utf-8"))
    figures = figure_payload.get("figures", {})
    values = figures.values() if isinstance(figures, dict) else figures
    owners: dict[str, set[str]] = {}
    for rows in origin_index.values():
        for row in rows:
            chapter = row["_new_id"].rsplit("_", 1)[0]
            for block in row.get("blocks", []):
                content = str(block.get("content") or "") if isinstance(block, dict) else ""
                for part in content.split("[[FIGURE:")[1:]:
                    figure_id = part.split("]]", 1)[0].strip()
                    if figure_id:
                        owners.setdefault(figure_id, set()).add(chapter)
    for figure in values:
        if not isinstance(figure, dict):
            continue
        # Figure numbers are only unique within a book.  Do not relabel an
        # Evolution asset merely because Genetics has the same Figure N.M.
        source_stem = Path(str(figure.get("source_pdf") or "")).stem
        if not source_stem.lower().startswith("genetics_"):
            continue
        figure_id = str(figure.get("id") or "").strip()
        owned_by = owners.get(figure_id, set())
        if len(owned_by) == 1:
            figure["chapter"] = next(iter(owned_by))
    figure_path.write_text(json.dumps(figure_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_groups(root: Path, groups: dict[int, list[dict[str, Any]]]) -> None:
    for chapter, rows in groups.items():
        for stale in root.glob(f"Genetics_chapter{chapter}_*.json"):
            stale.unlink()
        for index, row in enumerate(rows, 1):
            payload = copy.deepcopy(row)
            payload.pop("_new_id", None)
            origin_id = payload.pop("_origin_id")
            origin_slice = payload.pop("_origin_block_slice")
            new_id = unit_id(chapter, index)
            payload["id"] = new_id
            metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
            metadata["chapter"] = f"Genetics_chapter{chapter}"
            metadata["logical_chapter_repartition"] = {
                "source_unit": origin_id,
                "source_block_slice": origin_slice,
                "basis": "printed chapter title and source-PDF page-boundary audit",
            }
            payload["metadata"] = metadata
            (root / f"{new_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structured-dir", type=Path, default=Path("data/structured"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    groups, origin_index = materialize(args.structured_dir)
    total = sum(len(rows) for rows in groups.values())
    source_total = sum(source_count(args.structured_dir, chapter) for chapter in range(1, 28))
    print(f"logical units: {total}; source units: {source_total}; split source units: {sum(len(rows) > 1 for rows in origin_index.values())}")
    for chapter, rows in groups.items():
        print(f"chapter {chapter}: {len(rows)}")
    if args.dry_run:
        return
    write_groups(args.structured_dir, groups)
    update_library_sources(args.structured_dir, origin_index)


if __name__ == "__main__":
    main()
