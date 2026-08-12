#!/usr/bin/env python3
"""Recover PDF-grounded PopGen problem blocks and problem figures.

Every repair is anchored to an exact Paddle page/block and is safe to rerun.
The resulting resources are formal delivery data; nothing here is an audit
waiver or a source-block exclusion.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
FIGURES = ROOT / "data" / "figures"
TEXTBOOK_FIGURES = ROOT / "data" / "textbook" / "figures"
REPORT = ROOT / "tmp" / "book_audits" / "PopGen" / "reports" / "problem_resource_repairs.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_page(chapter: str, page: int) -> tuple[dict[str, Any], Path]:
    path = ROOT / "tmp" / "popgen" / "paddle_output" / f"{chapter}_full" / "intermediate" / "paddle_raw_response.json"
    return read_json(path)[page - 1], path


def raw_rows(page: dict[str, Any]) -> list[dict[str, Any]]:
    result = page.get("prunedResult") or page
    return list(result.get("parsing_res_list") or [])


def row(chapter: str, page: int, block_id: int) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    payload, path = raw_page(chapter, page)
    matches = [item for item in raw_rows(payload) if int(item.get("block_id", -1)) == block_id]
    if len(matches) != 1:
        raise ValueError(f"expected one raw block: {chapter} p{page} b{block_id}")
    return matches[0], path, payload


def content(record: dict[str, Any]) -> str:
    return str(record.get("block_content") or "").strip()


def dimensions(page: dict[str, Any]) -> tuple[float, float]:
    result = page.get("prunedResult") or page
    boxes = [item.get("block_bbox") for item in raw_rows(page) if item.get("block_bbox")]
    return (
        float(result.get("width") or max(box[2] for box in boxes)),
        float(result.get("height") or max(box[3] for box in boxes)),
    )


def ensure_marker(block: dict[str, Any], marker: str) -> None:
    text = str(block.get("content") or "").rstrip()
    if marker not in text:
        block["content"] = f"{text}\n\n{marker}"


def recover_problem_blocks() -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []

    unit_path = STRUCTURED / "PopGen_chapter6_004.json"
    unit = read_json(unit_path)
    left, _, _ = row("PopGen_chapter6", 9, 2)
    right, _, _ = row("PopGen_chapter6", 9, 3)
    question = f"{content(left)} {content(right)}"
    tail = content(right)
    base = unit["blocks"][12]["content"]
    if base.endswith(tail):
        unit["blocks"][12]["content"] = base[: -len(tail)].rstrip()
    marker = "[[FIGURE:problem_6.1]]"
    if not any(marker in str(block.get("content") or "") for block in unit["blocks"]):
        unit["blocks"].insert(13, {"type": "problem", "content": f"{question}\n\n{marker}"})
        changes.append({"unit": unit["id"], "operation": "restore_problem_6.1"})
    write_json(unit_path, unit)

    unit_path = STRUCTURED / "PopGen_chapter6_006.json"
    unit = read_json(unit_path)
    title, _, _ = row("PopGen_chapter6", 15, 8)
    continuation, _, _ = row("PopGen_chapter6", 15, 10)
    answer, _, _ = row("PopGen_chapter6", 15, 11)
    inline_a, _, _ = row("PopGen_chapter6", 15, 12)
    inline_b, _, _ = row("PopGen_chapter6", 15, 13)
    existing = unit["blocks"][3]["content"]
    split_at = existing.find(content(continuation))
    if split_at >= 0:
        unit["blocks"][3]["content"] = existing[:split_at].rstrip()
    marker = "[[FIGURE:problem_6.2]]"
    if not any(marker in str(block.get("content") or "") for block in unit["blocks"]):
        problem = " ".join(content(item) for item in (title, continuation, answer, inline_a, inline_b))
        unit["blocks"].insert(4, {"type": "problem", "content": f"{problem}\n\n{marker}"})
        changes.append({"unit": unit["id"], "operation": "restore_problem_6.2"})
    write_json(unit_path, unit)
    return changes


PROBLEM_FIGURES = (
    ("problem_2.10", "PopGen_chapter2", 46, 13, "PopGen_chapter2_024", 8),
    ("problem_4.20", "PopGen_chapter4", 45, 9, "PopGen_chapter4_024", 11),
    ("problem_6.2", "PopGen_chapter6", 15, 9, "PopGen_chapter6_006", 4),
    ("problem_6.7", "PopGen_chapter6", 56, 6, "PopGen_chapter6_029", 5),
    ("problem_6.8", "PopGen_chapter6", 56, 8, "PopGen_chapter6_029", 6),
    ("problem_6.9", "PopGen_chapter6", 57, 13, "PopGen_chapter6_029", 7),
    ("problem_6.27", "PopGen_chapter6", 58, 14, "PopGen_chapter6_030", 6),
    ("problem_6.28", "PopGen_chapter6", 59, 10, "PopGen_chapter6_030", 11),
)


def crop_asset(chapter: str, page_number: int, bbox: list[float], target: Path, raw: dict[str, Any]) -> None:
    source_pdf = next((ROOT / "data").rglob(f"{chapter}.pdf"))
    with fitz.open(source_pdf) as document:
        page = document[page_number - 1]
        width, height = dimensions(raw)
        x0, y0, x1, y1 = [float(value) for value in bbox]
        margin = 10
        rect = fitz.Rect(
            max(0, x0 - margin) * page.rect.width / width,
            max(0, y0 - margin) * page.rect.height / height,
            min(width, x1 + margin) * page.rect.width / width,
            min(height, y1 + margin) * page.rect.height / height,
        ) & page.rect
        target.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(clip=rect, dpi=220, alpha=False).save(target)


def recover_problem_figures() -> list[dict[str, Any]]:
    library_path = STRUCTURED / "PopGen_figure_library.json"
    library = read_json(library_path)
    by_id = {str(item["id"]): item for item in library["figures"]}
    changes: list[dict[str, Any]] = []
    for figure_id, chapter, page_number, block_id, unit_id, block_index in PROBLEM_FIGURES:
        source, raw_path, raw = row(chapter, page_number, block_id)
        bbox = [float(value) for value in source["block_bbox"]]
        asset = FIGURES / f"PopGen_{figure_id}.png"
        crop_asset(chapter, page_number, bbox, asset, raw)
        TEXTBOOK_FIGURES.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset, TEXTBOOK_FIGURES / asset.name)
        unit_path = STRUCTURED / f"{unit_id}.json"
        unit = read_json(unit_path)
        marker = f"[[FIGURE:{figure_id}]]"
        ensure_marker(unit["blocks"][block_index], marker)
        write_json(unit_path, unit)
        entry = {
            "id": figure_id,
            "chapter": chapter,
            "placeholder": marker,
            "see_placeholder": f"[[SEE_FIGURE:{figure_id}]]",
            "asset_path": f"figures/{asset.name}",
            "caption": f"Problem {figure_id.removeprefix('problem_')} diagram from the authoritative chapter PDF.",
            "source_pdf": str(next((ROOT / "data").rglob(f"{chapter}.pdf")).relative_to(ROOT)),
            "source_paddle_raw": str(raw_path.relative_to(ROOT)),
            "page": page_number,
            "raw_bbox": bbox,
            "bbox_source": "exact Paddle problem graphic block",
            "body_blocks": [{
                "page": page_number,
                "label": source.get("block_label"),
                "content": content(source),
                "bbox": bbox,
                "block_id": block_id,
                "block_order": source.get("block_order"),
            }],
            "caption_block": None,
            "confidence": 1.0,
            "book": "PopGen",
            "asset_key": f"PopGen:{chapter}:{figure_id}",
        }
        by_id[figure_id] = entry
        changes.append({
            "figure": figure_id,
            "source_block_id": f"{chapter}:p{page_number:03d}:b{block_id}",
            "asset_sha256": sha256(asset),
        })

    # Correct two pre-existing multi-part figure provenance records.
    for figure_id, chapter, page_number, block_id in (
        ("3.12", "PopGen_chapter3", 25, 5),
        ("6.16", "PopGen_chapter6", 39, 10),
    ):
        source, _, _ = row(chapter, page_number, block_id)
        record = {
            "page": page_number, "label": source.get("block_label"),
            "content": content(source), "bbox": [float(value) for value in source["block_bbox"]],
            "block_id": block_id, "block_order": source.get("block_order"),
        }
        bodies = by_id[figure_id].setdefault("body_blocks", [])
        if not any(item.get("page") == page_number and item.get("block_id") == block_id for item in bodies):
            bodies.append(record)
            changes.append({"figure": figure_id, "operation": "bind_missing_figure_panel", "block_id": block_id})

    library["figures"] = sorted(
        by_id.values(),
        key=lambda item: (str(item.get("chapter")), int(item.get("page") or 0), str(item.get("id"))),
    )
    write_json(library_path, library)
    return changes


def main() -> None:
    changes = [*recover_problem_blocks(), *recover_problem_figures()]
    report = {
        "schema": "popgen_problem_resource_repairs.v1",
        "book": "PopGen",
        "change_count": len(changes),
        "figure_count": len(read_json(STRUCTURED / "PopGen_figure_library.json")["figures"]),
        "changes": changes,
    }
    write_json(REPORT, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
