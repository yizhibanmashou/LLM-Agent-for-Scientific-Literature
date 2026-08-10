#!/usr/bin/env python3
"""Build source-PDF-grounded audit ledgers for the Genetics delivery.

All generated evidence is written below tmp/genetics_accuracy_audit.  The
script never modifies data/ and deliberately keeps automated checks separate
from the visual review ledger: a rendered page is not considered reviewed
until its status is explicitly recorded as verified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import sys
import textwrap
from collections import defaultdict
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.rebuild_genetics_book import RANGES, write_json
from scripts.build_genetics_staging import SOURCE_TEXT_CORRECTION_EVIDENCE, clean_text

UNIT_RE = re.compile(r"^Genetics_(?:chapter\d+|appendix1)_\d{3}\.json$")
PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE|FIGURE|EXAMPLE):[^\]]+\]\]")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
SKIP_LABELS = {"header", "footer", "page_number", "number", "formula_number"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_rows(page: dict[str, Any]) -> list[dict[str, Any]]:
    pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else {}
    rows = pruned.get("parsing_res_list") or page.get("parsing_res_list") or []
    return [row for row in rows if isinstance(row, dict)]


def bbox(row: dict[str, Any]) -> list[float] | None:
    value = row.get("block_bbox")
    if isinstance(value, list) and len(value) == 4:
        return [float(item) for item in value]
    return None


def raw_dimensions(page: dict[str, Any]) -> tuple[float, float]:
    pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else {}
    boxes = [bbox(row) for row in page_rows(page)]
    boxes = [item for item in boxes if item]
    width = float(pruned.get("width") or page.get("width") or max((item[2] for item in boxes), default=1))
    height = float(pruned.get("height") or page.get("height") or max((item[3] for item in boxes), default=1))
    return width, height


def clean_source(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"<div[^>]*>|</div>", "", text, flags=re.I)
    text = re.sub(
        r"&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);",
        lambda match: html.unescape(match.group(0)),
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def normalize_comparison(value: Any) -> str:
    text = clean_source(value)
    text = text.replace("[[", "").replace("]]", "")
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"-\s+([a-z])", r"\1", text)
    return re.sub(r"[^0-9A-Za-z]+", "", text).lower()


def source_text_for_comparison(
    source_ids: Iterable[str],
    raw_by_id: dict[str, dict[str, Any]],
    split_body_by_source_id: dict[str, str],
) -> str:
    """Return the delivered portion of each raw block for similarity checks.

    A visually verified source block may contain both a heading and its first
    body paragraph.  Once that block is deliberately split, the structured
    prose must be compared with the recorded body portion rather than with the
    original combined block.
    """
    portions = []
    for source_id in source_ids:
        if source_id not in raw_by_id:
            continue
        raw = raw_by_id[source_id]
        text = split_body_by_source_id.get(source_id, raw.get("block_content"))
        match = re.fullmatch(r"p(\d+):b(\d+)", source_id)
        correction = SOURCE_TEXT_CORRECTION_EVIDENCE.get(
            (int(match.group(1)), int(match.group(2))) if match else (-1, -1)
        )
        if correction:
            # The builder applies corrections after ``clean_text`` has folded
            # Paddle's variable horizontal spacing.  Mirror that order so the
            # audit checks the exact same source-normalized text.
            text = clean_text(text)
            if bbox(raw) != correction["bbox"]:
                raise RuntimeError(f"source correction evidence drifted at {source_id}")
            for old, new in correction["replacements"]:
                if old not in str(text):
                    raise RuntimeError(f"source correction text drifted at {source_id}")
                text = str(text).replace(old, new)
        portions.append(clean_source(text))
    return " ".join(portions)


def load_raw_pages(workspace: Path) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for label, (start, end) in RANGES.items():
        chapter = f"Genetics_{label}"
        names = [f"{chapter}_full"]
        if label == "appendix1":
            names += ["Genetics_appendix1_part2_full", "Genetics_appendix1_part3_full"]
        pages: list[dict[str, Any]] = []
        for name in names:
            path = workspace / "paddle_output" / name / "intermediate" / "paddle_raw_response.json"
            pages += read_json(path)
        expected = end - start + 1
        if len(pages) != expected:
            raise ValueError(f"{chapter}: expected {expected} raw pages, found {len(pages)}")
        for offset, page in enumerate(pages):
            result[start + offset] = page
    return result


def render_pages(source_pdf: Path, output: Path, dpi: int) -> None:
    output.mkdir(parents=True, exist_ok=True)
    document = fitz.open(source_pdf)
    try:
        for index, page in enumerate(document):
            target = output / f"page_{index + 1:04d}.png"
            if target.exists():
                continue
            page.get_pixmap(dpi=dpi, alpha=False, colorspace=fitz.csGRAY).save(target)
    finally:
        document.close()


def contact_sheets(
    images: Iterable[tuple[str, Path]],
    output: Path,
    *,
    columns: int,
    rows: int,
    cell: tuple[int, int],
) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    entries = list(images)
    per_sheet = columns * rows
    sheets: list[Path] = []
    for sheet_index in range(0, len(entries), per_sheet):
        canvas = Image.new("RGB", (columns * cell[0], rows * cell[1]), (225, 225, 225))
        for local, (label, path) in enumerate(entries[sheet_index : sheet_index + per_sheet]):
            image = Image.open(path).convert("RGB")
            image.thumbnail((cell[0] - 16, cell[1] - 38))
            panel = Image.new("RGB", cell, "white")
            panel.paste(image, ((cell[0] - image.width) // 2, 30 + (cell[1] - 38 - image.height) // 2))
            ImageDraw.Draw(panel).text((8, 8), label, fill="black")
            canvas.paste(panel, ((local % columns) * cell[0], (local // columns) * cell[1]))
        target = output / f"sheet_{sheet_index // per_sheet + 1:03d}.jpg"
        canvas.save(target, quality=88)
        sheets.append(target)
    return sheets


def render_bbox_crop(
    document: fitz.Document,
    raw_pages: dict[int, dict[str, Any]],
    source_page: int,
    raw_bbox: list[float],
    target: Path,
    *,
    dpi: int = 180,
    margin: float = 10,
) -> None:
    page = document[source_page - 1]
    raw_width, raw_height = raw_dimensions(raw_pages[source_page])
    x0, y0, x1, y1 = raw_bbox
    rect = fitz.Rect(
        max(0, x0 - margin) * page.rect.width / raw_width,
        max(0, y0 - margin) * page.rect.height / raw_height,
        min(raw_width, x1 + margin) * page.rect.width / raw_width,
        min(raw_height, y1 + margin) * page.rect.height / raw_height,
    ) & page.rect
    target.parent.mkdir(parents=True, exist_ok=True)
    page.get_pixmap(clip=rect, dpi=dpi, alpha=False).save(target)


def pair_image(label: str, source: Path, delivery: Path, target: Path) -> None:
    left = Image.open(source).convert("RGB")
    right = Image.open(delivery).convert("RGB")
    max_height = max(left.height, right.height)
    left = ImageOps.pad(left, (max(1, int(left.width * max_height / left.height)), max_height), color="white")
    right = ImageOps.pad(right, (max(1, int(right.width * max_height / right.height)), max_height), color="white")
    canvas = Image.new("RGB", (left.width + right.width, max_height + 34), "white")
    canvas.paste(left, (0, 34))
    canvas.paste(right, (left.width, 34))
    ImageDraw.Draw(canvas).text((8, 8), f"{label}: source PDF | delivery", fill="black")
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def combine_vertical(label: str, sources: list[Path], target: Path, max_width: int = 1200) -> None:
    images = [Image.open(path).convert("RGB") for path in sources]
    resized = []
    for item in images:
        if item.width > max_width:
            height = max(1, round(item.height * max_width / item.width))
            item = item.resize((max_width, height))
        resized.append(item)
    width = max((item.width for item in resized), default=1)
    height = 34 + sum(item.height for item in resized) + max(0, len(resized) - 1) * 8
    canvas = Image.new("RGB", (width, height), "white")
    ImageDraw.Draw(canvas).text((8, 8), label, fill="black")
    y = 34
    for item in resized:
        canvas.paste(item, ((width - item.width) // 2, y))
        y += item.height + 8
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


@lru_cache(maxsize=None)
def audit_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_page_evidence(
    page: int,
    source_image: Path,
    evidence_rows: list[dict[str, Any]],
    raw_by_id: dict[str, dict[str, Any]],
    raw_page: dict[str, Any] | None,
    target: Path,
) -> None:
    """Render one readable source-vs-delivery page used for human approval."""
    source = Image.open(source_image).convert("RGB")
    overlay = source.copy()
    draw = ImageDraw.Draw(overlay)
    raw_width, raw_height = raw_dimensions(raw_page or {})
    colors = ((196, 0, 0), (0, 90, 180), (0, 130, 50), (160, 80, 0), (120, 0, 150))
    for index, item in enumerate(evidence_rows, 1):
        color = colors[(index - 1) % len(colors)]
        for source_id in item.get("source_block_ids") or []:
            raw = raw_by_id.get(str(source_id))
            box = bbox(raw or {})
            if not box:
                continue
            x0, y0, x1, y1 = box
            scaled = (
                round(x0 * overlay.width / raw_width), round(y0 * overlay.height / raw_height),
                round(x1 * overlay.width / raw_width), round(y1 * overlay.height / raw_height),
            )
            draw.rectangle(scaled, outline=color, width=3)
            label_y = max(0, scaled[1] - 24)
            draw.rectangle((scaled[0], label_y, scaled[0] + 34, label_y + 24), fill="white", outline=color)
            draw.text((scaled[0] + 3, label_y + 1), str(index), fill=color, font=audit_font(18))

    body_font = audit_font(19)
    heading_font = audit_font(24)
    lines: list[tuple[str, tuple[int, int, int], ImageFont.ImageFont]] = [
        (f"PDF page {page} — original with source block boxes | structured delivery", (0, 0, 0), heading_font)
    ]
    if not evidence_rows:
        lines.append(("No structured body blocks on this page (front matter/index/source-only page).", (80, 80, 80), body_font))
    for index, item in enumerate(evidence_rows, 1):
        color = colors[(index - 1) % len(colors)]
        key = item.get("key")
        ids = ", ".join(str(value) for value in item.get("source_block_ids") or [])
        lines.append((f"[{index}] {key}  type={item.get('type')}  source={ids}", color, body_font))
        raw_text = " ".join(
            clean_source(raw_by_id[source_id].get("block_content"))
            for source_id in item.get("source_block_ids") or []
            if source_id in raw_by_id and str(source_id).startswith(f"p{page}:")
        )
        for prefix, value in (("RAW LOCATOR", raw_text), ("DELIVERY", str(item.get("content") or ""))):
            wrapped = textwrap.wrap(
                f"{prefix}: {value}", width=112, replace_whitespace=False,
                drop_whitespace=False, break_long_words=True, break_on_hyphens=False,
            ) or [f"{prefix}:"]
            lines.extend((part, (25, 25, 25), body_font) for part in wrapped)
        lines.append(("", (0, 0, 0), body_font))

    line_height = 26
    text_height = 60 + line_height * len(lines)
    header_height = 46
    right_width = 1550
    canvas = Image.new(
        "RGB",
        (overlay.width + right_width, max(overlay.height + header_height, text_height)),
        "white",
    )
    canvas.paste(overlay, (0, header_height))
    out = ImageDraw.Draw(canvas)
    out.text((10, 10), f"PDF page {page} — ORIGINAL", fill="black", font=heading_font)
    y = 12
    for value, color, font in lines:
        out.text((overlay.width + 24, y), value, fill=color, font=font)
        y += line_height
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, quality=92)


def union_bbox(boxes: Iterable[list[float]]) -> list[float]:
    values = list(boxes)
    return [
        min(item[0] for item in values), min(item[1] for item in values),
        max(item[2] for item in values), max(item[3] for item in values),
    ]


def load_visual_review(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {"pages": {}, "figures": {}, "tables": {}, "formulas": {}, "examples": {}}
    value = read_json(path)
    return {
        key: dict(value.get(key) or {})
        for key in ("pages", "figures", "tables", "formulas", "examples")
    }


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    stage_data = args.stage.resolve() / "data"
    structured = stage_data / "structured"
    raw_pages = load_raw_pages(args.rebuild_workspace.resolve())
    correction_path = args.rebuild_workspace.resolve() / "manual_source_corrections.json"
    source_corrections = read_json(correction_path).get("corrections", []) if correction_path.exists() else []
    split_body_by_source_id = {
        str(item["source_block_id"]): str(item["split_body"])
        for item in source_corrections
        if item.get("source_block_id") and item.get("split_body") is not None
    }
    formula_corrections = {
        (
            int(item["source_page"]),
            tuple(float(value) for value in item["bbox"]),
        ): item
        for item in source_corrections
        if item.get("replacement_latex") and isinstance(item.get("bbox"), list)
    }
    pages_dir = output / "pages"
    if not args.skip_render:
        render_pages(args.source_pdf.resolve(), pages_dir, args.dpi)

    review_path = output / "visual_review.json"
    review = load_visual_review(review_path)
    page_records: dict[int, dict[str, Any]] = {
        page: {
            "page": page,
            "classification": "front_matter" if page <= 20 else "chapter" if page <= 818 else "appendix",
            "render": str((pages_dir / f"page_{page:04d}.png").relative_to(output)),
            "visual_status": review["pages"].get(str(page), "pending"),
            "units": [], "blocks": 0, "formulas": [], "tables": [], "figures": [], "examples": [],
        }
        for page in range(1, 993)
    }
    errors: list[str] = []
    warnings: list[str] = []
    raw_by_id: dict[str, dict[str, Any]] = {}
    for page, raw in raw_pages.items():
        for row in page_rows(raw):
            raw_by_id[f"p{page}:b{row.get('block_id', '?')}"] = row
    # Human corrections are themselves source-grounded dispositions.  A block
    # intentionally suppressed from the delivery (for example a panel label
    # already contained in its figure) must remain auditable without being
    # reported as an uncovered source block.
    consumed_raw_ids: set[str] = {
        str(item["source_block_id"])
        for item in source_corrections
        if item.get("source_block_id")
    }

    unit_rows: list[dict[str, Any]] = []
    page_evidence_rows: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    units = []
    for path in sorted(structured.glob("Genetics_*.json")):
        if not UNIT_RE.match(path.name):
            continue
        unit = read_json(path)
        units.append(unit)
        heading_source = (unit.get("metadata") or {}).get("heading_source") or {}
        heading_ids = [str(item) for item in heading_source.get("source_block_ids") or []]
        consumed_raw_ids.update(heading_ids)
        for heading_page in sorted({
            int(match.group(1))
            for source_id in heading_ids
            if (match := re.match(r"^p(\d+):b", source_id))
        }):
            page_evidence_rows[heading_page].append({
                "key": f"{unit.get('id')}#heading",
                "type": "heading",
                "source_block_ids": [item for item in heading_ids if item.startswith(f"p{heading_page}:b")],
                "content": (unit.get("metadata") or {}).get("display_heading"),
            })
        if unit.get("blocks") and unit.get("node_kind") == "heading":
            errors.append(f"nonempty heading node: {unit.get('id')}")
        for block_index, block in enumerate(unit.get("blocks", [])):
            block_key = f"{unit.get('id')}#{block_index}"
            source_ids = [str(item) for item in block.get("source_block_ids") or []]
            consumed_raw_ids.update(source_ids)
            missing_ids = [item for item in source_ids if item not in raw_by_id]
            if missing_ids:
                errors.append(f"{unit.get('id')} block {block_index}: missing raw ids {missing_ids}")
            page = block.get("source_page")
            source_pages = sorted({
                int(match.group(1))
                for source_id in source_ids
                if (match := re.match(r"^p(\d+):b", source_id))
            })
            if not source_pages and isinstance(page, int):
                source_pages = [page]
            for evidence_page in source_pages:
                if evidence_page not in page_records:
                    continue
                page_records[evidence_page]["blocks"] += 1
                if unit.get("id") not in page_records[evidence_page]["units"]:
                    page_records[evidence_page]["units"].append(unit.get("id"))
                page_evidence_rows[evidence_page].append({
                    "key": block_key,
                    "type": block.get("type"),
                    "source_block_ids": [item for item in source_ids if item.startswith(f"p{evidence_page}:b")],
                    "content": block.get("content"),
                })
            content = str(block.get("content") or "")
            source_text = source_text_for_comparison(source_ids, raw_by_id, split_body_by_source_id)
            ratio = None
            if source_text and not PLACEHOLDER_RE.fullmatch(content):
                ratio = round(SequenceMatcher(None, normalize_comparison(source_text), normalize_comparison(content)).ratio(), 4)
                if ratio < 0.90:
                    warnings.append(f"low block/source similarity {ratio}: {unit.get('id')}#{block_index}")
            unit_rows.append({
                "unit_id": unit.get("id"), "block_index": block_index, "type": block.get("type"),
                "source_page": page, "source_page_end": block.get("source_page_end"),
                "source_pages": source_pages,
                "source_block_ids": source_ids, "bbox": block.get("bbox"),
                "source_similarity": ratio, "content": content,
                "visual_status": "verified" if source_pages and all(
                    review["pages"].get(str(value)) == "verified" for value in source_pages
                ) else "pending",
            })

    libraries = {
        "formula": read_json(structured / "Genetics_formula_library.json").get("formulas", []),
        "table": read_json(structured / "Genetics_table_library.json").get("tables", []),
        "figure": read_json(structured / "Genetics_figure_library.json").get("figures", []),
    }
    examples = [row for row in read_json(structured / "example_library.json").get("examples", []) if row.get("book") == "Genetics"]

    formula_rows = []
    formula_contact_entries: list[tuple[str, Path]] = []
    evidence_document = fitz.open(args.source_pdf.resolve())
    try:
        for formula in libraries["formula"]:
            source = formula.get("source") or {}
            page = source.get("page")
            formula_id = str(formula.get("id"))
            raw_match = None
            if isinstance(page, int) and isinstance(source.get("bbox"), list):
                raw_match = next((
                    row for row in page_rows(raw_pages[page])
                    if bbox(row) == [float(value) for value in source["bbox"]]
                ), None)
            source_text = clean_source(raw_match.get("block_content")) if raw_match else ""
            correction = None
            if isinstance(page, int) and isinstance(source.get("bbox"), list):
                correction = formula_corrections.get((page, tuple(float(value) for value in source["bbox"])))
            source_match = bool(source_text) and (
                normalize_comparison(source_text) == normalize_comparison(formula.get("latex"))
                or (
                    correction is not None
                    and normalize_comparison(correction.get("replacement_latex"))
                    == normalize_comparison(formula.get("latex"))
                )
            )
            if not source_match:
                errors.append(f"formula/source mismatch: {formula_id}")
            if raw_match:
                consumed_raw_ids.add(f"p{page}:b{raw_match.get('block_id', '?')}")
            crop = output / "formula_crops" / f"{formula_id}.png"
            if isinstance(page, int) and isinstance(source.get("bbox"), list):
                render_bbox_crop(evidence_document, raw_pages, page, source["bbox"], crop, dpi=160, margin=14)
                formula_contact_entries.append((f"{formula_id} | p{page} | {formula.get('latex')}", crop))
            item = {
                "id": formula_id, "page": page, "unit_id": source.get("unit_id"),
                "bbox": source.get("bbox"), "equation_number": formula.get("equation_number"),
                "latex": formula.get("latex"), "source_text": source_text,
                "source_match": source_match, "source_crop": str(crop),
                "manual_correction": correction,
                "visual_status": review["formulas"].get(formula_id, "pending"),
            }
            formula_rows.append(item)
            if isinstance(page, int):
                page_records[page]["formulas"].append(formula.get("id"))

        table_rows = []
        table_contact_entries: list[tuple[str, Path]] = []
        for table in libraries["table"]:
            source = table.get("source") or {}
            pages = source.get("pages") or [source.get("page")]
            key = f"{source.get('chapter')}:{table.get('id')}"
            part_rows = []
            part_crops: list[Path] = []
            for part_index, part in enumerate(table.get("parts") or [table], 1):
                page = part.get("page") or source.get("page")
                part_bbox = part.get("bbox") or source.get("bbox")
                caption_bbox = part.get("caption_bbox") or source.get("caption_bbox")
                ids = list(part.get("source_block_ids") or [])
                if not ids and isinstance(page, int) and isinstance(part_bbox, list):
                    match = next((
                        row for row in page_rows(raw_pages[page])
                        if bbox(row) == [float(value) for value in part_bbox]
                    ), None)
                    if match:
                        ids = [f"p{page}:b{match.get('block_id', '?')}"]
                raw_text = " ".join(clean_source(raw_by_id[item].get("block_content")) for item in ids if item in raw_by_id)
                manual_correction = part.get("manual_correction") if isinstance(part.get("manual_correction"), dict) else None
                consumed_raw_ids.update(str(item) for item in ids)
                consumed_raw_ids.update(str(item) for item in part.get("caption_source_block_ids") or [])
                for note in part.get("notes") or []:
                    consumed_raw_ids.update(str(item) for item in note.get("source_block_ids") or [])
                if ids and isinstance(page, int) and not manual_correction:
                    raw_rows = page_rows(raw_pages[page])
                    table_block_id = ids[0].split(":b", 1)[-1]
                    table_position = next(
                        (index for index, candidate in enumerate(raw_rows) if str(candidate.get("block_id")) == table_block_id),
                        None,
                    )
                    expected_note_ids: list[str] = []
                    if table_position is not None:
                        for candidate in raw_rows[table_position + 1 :]:
                            candidate_kind = str(candidate.get("block_label") or "").lower()
                            candidate_text = clean_source(candidate.get("block_content"))
                            is_note = candidate_kind in {"vision_footnote", "footnote"} or (
                                candidate_kind == "text" and re.match(r"^(?:Note|Source):\s*", candidate_text, re.I)
                            )
                            if not is_note:
                                break
                            expected_note_ids.append(f"p{page}:b{candidate.get('block_id', '?')}")
                        if expected_note_ids:
                            last_id = expected_note_ids[-1]
                            combined_note_text = clean_source(raw_by_id[last_id].get("block_content"))
                            continuation_page = page + 1
                            while not re.search(r"[.!?][\"')\]]?$", combined_note_text.rstrip()):
                                next_rows = [
                                    candidate for candidate in page_rows(raw_pages.get(continuation_page, {}))
                                    if str(candidate.get("block_label") or "").lower()
                                    not in {"header", "number", "footer", "page_number"}
                                    and clean_source(candidate.get("block_content"))
                                ]
                                if not next_rows or str(next_rows[0].get("block_label") or "").lower() != "text":
                                    break
                                continuation = next_rows[0]
                                continuation_id = f"p{continuation_page}:b{continuation.get('block_id', '?')}"
                                expected_note_ids.append(continuation_id)
                                combined_note_text += " " + clean_source(continuation.get("block_content"))
                                continuation_page += 1
                    actual_note_ids = [
                        str(item)
                        for note in part.get("notes") or []
                        for item in note.get("source_block_ids") or []
                    ]
                    if expected_note_ids != actual_note_ids:
                        errors.append(
                            f"table footnote association mismatch: {key} part {part_index}: "
                            f"expected {expected_note_ids}, got {actual_note_ids}"
                        )
                source_match = bool(raw_text) and normalize_comparison(raw_text) == normalize_comparison(part.get("html") or table.get("html"))
                correction_ids = set(str(item) for item in (manual_correction or {}).get("source_block_ids", []))
                all_evidence_ids = (
                    set(str(item) for item in ids)
                    | {
                        str(item)
                        for note in part.get("notes") or []
                        for item in note.get("source_block_ids") or []
                    }
                )
                manual_source_valid = (
                    bool(manual_correction)
                    and bool(correction_ids)
                    and correction_ids.issubset(all_evidence_ids)
                    and all_evidence_ids.issubset(raw_by_id)
                )
                if not source_match and not manual_source_valid:
                    errors.append(f"table/source mismatch: {key} part {part_index}")
                crop = output / "table_crops" / f"{source.get('chapter')}_{table.get('id')}_part{part_index}.png"
                crop_boxes = [box for box in (caption_bbox, part_bbox) if isinstance(box, list)]
                crop_boxes += [note["bbox"] for note in part.get("notes") or [] if isinstance(note.get("bbox"), list)]
                if isinstance(page, int) and crop_boxes:
                    render_bbox_crop(evidence_document, raw_pages, page, union_bbox(crop_boxes), crop, dpi=150, margin=14)
                    part_crops.append(crop)
                for note_index, note in enumerate(part.get("notes") or [], 1):
                    for continuation_index, continuation in enumerate(note.get("continuation_bboxes") or [], 1):
                        continuation_page = continuation.get("source_page")
                        continuation_bbox = continuation.get("bbox")
                        if isinstance(continuation_page, int) and isinstance(continuation_bbox, list):
                            continuation_crop = output / "table_crops" / (
                                f"{source.get('chapter')}_{table.get('id')}_part{part_index}_"
                                f"note{note_index}_continuation{continuation_index}.png"
                            )
                            render_bbox_crop(
                                evidence_document,
                                raw_pages,
                                continuation_page,
                                continuation_bbox,
                                continuation_crop,
                                dpi=150,
                                margin=14,
                            )
                            part_crops.append(continuation_crop)
                part_rows.append({
                    "part": part_index, "page": page, "bbox": part_bbox,
                    "source_block_ids": ids, "source_text": raw_text,
                    "source_match": source_match,
                    "manual_source_valid": manual_source_valid,
                    "manual_correction": manual_correction,
                    "source_crop": str(crop),
                })
            combined = output / "table_crops" / "combined" / f"{source.get('chapter')}_{table.get('id')}.jpg"
            combine_vertical(key, part_crops, combined)
            table_contact_entries.append((key, combined))
            item = {
                "id": table.get("id"), "chapter": source.get("chapter"), "unit_id": source.get("unit_id"),
                "pages": pages, "parts": len(table.get("parts") or [table]),
                "part_evidence": part_rows, "source_composite": str(combined),
                "visual_status": review["tables"].get(key, "pending"),
            }
            table_rows.append(item)
            for page in pages:
                if isinstance(page, int):
                    page_records[page]["tables"].append(table.get("id"))
    finally:
        evidence_document.close()

    figure_rows = []
    figure_pair_entries: list[tuple[str, Path]] = []
    document = fitz.open(args.source_pdf.resolve())
    try:
        for figure in libraries["figure"]:
            page = figure.get("page")
            asset = stage_data / str(figure.get("asset_path") or "")
            textbook_asset = stage_data / "textbook" / "figures" / asset.name
            figure_id = str(figure.get("id"))
            key = f"{figure.get('chapter')}:{figure_id}"
            source_crop = output / "figure_pairs" / "source" / asset.name
            pair = output / "figure_pairs" / "paired" / asset.name
            if isinstance(page, int) and isinstance(figure.get("raw_bbox"), list):
                render_bbox_crop(document, raw_pages, page, figure["raw_bbox"], source_crop)
                pair_image(key, source_crop, asset, pair)
                figure_pair_entries.append((key, pair))
                page_records[page]["figures"].append(figure_id)
            hashes_match = asset.exists() and textbook_asset.exists() and sha256(asset) == sha256(textbook_asset)
            if not hashes_match:
                errors.append(f"figure/textbook mismatch: {asset.name}")
            figure_rows.append({
                "id": figure_id, "key": key, "page": page, "asset": str(asset),
                "source_crop": str(source_crop), "pair": str(pair), "hashes_match": hashes_match,
                "visual_status": review["figures"].get(key, "pending"),
            })
            consumed_raw_ids.update(str(item) for item in figure.get("source_block_ids") or [])
            consumed_raw_ids.update(str(item) for item in (figure.get("caption_block") or {}).get("source_block_ids") or [])
    finally:
        document.close()

    example_rows = []
    example_contact_entries: list[tuple[str, Path]] = []
    document = fitz.open(args.source_pdf.resolve())
    try:
        for example in examples:
            example_id = str(example.get("example_id"))
            source_page = (example.get("metadata") or {}).get("source_page")
            block_ids = list(example.get("block_ids") or [])
            consumed_raw_ids.update(str(item) for item in block_ids)
            missing_ids = [item for item in block_ids if item not in raw_by_id]
            if missing_ids:
                errors.append(f"example missing raw ids: {example_id}: {missing_ids}")
            by_page: defaultdict[int, list[list[float]]] = defaultdict(list)
            for block_id in block_ids:
                match = re.match(r"p(\d+):b", block_id)
                raw_row = raw_by_id.get(block_id)
                raw_box = bbox(raw_row) if raw_row else None
                if match and raw_box:
                    by_page[int(match.group(1))].append(raw_box)
            page_crops: list[Path] = []
            for page, boxes in sorted(by_page.items()):
                crop = output / "example_crops" / example_id.replace(":", "_") / f"page_{page}.png"
                render_bbox_crop(document, raw_pages, page, union_bbox(boxes), crop, dpi=145, margin=16)
                page_crops.append(crop)
            combined = output / "example_crops" / "combined" / f"{example_id.replace(':', '_')}.jpg"
            combine_vertical(example_id, page_crops, combined)
            example_contact_entries.append((example_id, combined))
            evidence = example.get("evidence") or {}
            lower_rule = evidence.get("lower_rule")
            boundary_verified = (
                isinstance(lower_rule, dict)
                and isinstance(lower_rule.get("page"), int)
                and isinstance(lower_rule.get("y"), (int, float))
                and not bool((example.get("metadata") or {}).get("needs_review"))
            )
            if not boundary_verified:
                errors.append(f"example lacks source-PDF lower-rule evidence: {example_id}")
            if isinstance(source_page, int):
                page_records[source_page]["examples"].append(example_id)
            example_rows.append({
                "id": example_id, "source_page": source_page, "source_file": example.get("source_file"),
                "end_source_file": example.get("end_source_file"), "block_ids": block_ids,
                "lower_rule": lower_rule, "boundary_verified": boundary_verified,
                "source_composite": str(combined),
                "visual_status": review["examples"].get(example_id, "pending"),
            })
    finally:
        document.close()

    nested = []
    unresolved = []
    missing_links = []
    for path in sorted((stage_data / "textbook").glob("Genetics_*_textbook.md")):
        content = path.read_text(encoding="utf-8")
        if "[[[[" in content or "]]]]" in content:
            nested.append(path.name)
        unresolved += [f"{path.name}:{match.group(0)}" for match in PLACEHOLDER_RE.finditer(content)]
        for match in IMAGE_LINK_RE.finditer(content):
            if not (path.parent / match.group("path")).resolve().exists():
                missing_links.append(f"{path.name}:{match.group('path')}")
    if nested:
        errors.append(f"nested style markers: {nested}")
    if unresolved:
        errors.append(f"unresolved direct placeholders: {len(unresolved)}")
    if missing_links:
        errors.append(f"missing textbook image links: {len(missing_links)}")

    substantive_labels = {
        "abstract", "chart", "display_formula", "doc_title", "figure_title",
        "footnote", "image", "paragraph_title", "reference_content", "table",
        "text", "vision_footnote",
    }
    uncovered_source_blocks = [
        {
            "source_block_id": raw_id,
            "label": row.get("block_label"),
            "bbox": row.get("block_bbox"),
            "content": clean_source(row.get("block_content")),
        }
        for raw_id, row in raw_by_id.items()
        if raw_id not in consumed_raw_ids
        and str(row.get("block_label") or "").lower() in substantive_labels
        and (clean_source(row.get("block_content")) or str(row.get("block_label") or "").lower() in {"image", "chart"})
    ]
    if uncovered_source_blocks:
        errors.append(f"uncovered substantive source blocks: {len(uncovered_source_blocks)}")

    identity_sets = {
        "units": [str(row.get("id")) for row in units],
        "formulas": [str(row.get("id")) for row in formula_rows],
        "tables": [f"{row.get('chapter')}:{row.get('id')}" for row in table_rows],
        "figures": [str(row.get("key")) for row in figure_rows],
        "examples": [str(row.get("id")) for row in example_rows],
    }
    for kind, identities in identity_sets.items():
        if len(identities) != len(set(identities)):
            errors.append(f"duplicate {kind} identities")
    # PDF page 460's former synthetic heading was removed, while PDF page 481's
    # visually bold subsection was recovered from a merged text block.  The net
    # count remains 456, now with the two source-grounded semantics corrected.
    expected_counts = {"units": 456, "formulas": 1813, "tables": 75, "figures": 152, "examples": 157}
    for kind, expected in expected_counts.items():
        if len(identity_sets[kind]) != expected:
            errors.append(f"wrong {kind} count: {len(identity_sets[kind])} != {expected}")

    write_json(output / "page_ledger.json", list(page_records.values()))
    write_json(output / "block_ledger.json", unit_rows)
    write_json(output / "formula_ledger.json", formula_rows)
    write_json(output / "table_ledger.json", table_rows)
    write_json(output / "figure_ledger.json", figure_rows)
    write_json(output / "example_ledger.json", example_rows)
    write_json(output / "uncovered_source_blocks.json", uncovered_source_blocks)
    write_json(review_path, review)
    with (output / "page_ledger.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["page", "classification", "visual_status", "blocks", "formulas", "tables", "figures", "examples"])
        writer.writeheader()
        for row in page_records.values():
            writer.writerow({key: row[key] if key not in {"formulas", "tables", "figures", "examples"} else len(row[key]) for key in writer.fieldnames})

    page_contact_dir = output / "page_contacts"
    if page_contact_dir.exists():
        shutil.rmtree(page_contact_dir)
    page_contact_dir.mkdir(parents=True)
    page_contacts = []
    for page in range(1, 993):
        target = page_contact_dir / f"sheet_{page:03d}.jpg"
        render_page_evidence(
            page,
            pages_dir / f"page_{page:04d}.png",
            page_evidence_rows.get(page, []),
            raw_by_id,
            raw_pages.get(page),
            target,
        )
        page_contacts.append(target)
    figure_contacts = contact_sheets(
        figure_pair_entries, output / "figure_contacts", columns=2, rows=2, cell=(700, 520),
    )
    formula_contacts = contact_sheets(
        formula_contact_entries, output / "formula_contacts", columns=4, rows=4, cell=(500, 240),
    )
    table_contacts = contact_sheets(
        table_contact_entries, output / "table_contacts", columns=2, rows=2, cell=(700, 700),
    )
    example_contacts = contact_sheets(
        example_contact_entries, output / "example_contacts", columns=2, rows=2, cell=(700, 700),
    )

    pending = {
        "pages": sum(row["visual_status"] != "verified" for row in page_records.values()),
        "blocks": sum(row["visual_status"] != "verified" for row in unit_rows),
        "figures": sum(row["visual_status"] != "verified" for row in figure_rows),
        "tables": sum(row["visual_status"] != "verified" for row in table_rows),
        "formulas": sum(row["visual_status"] != "verified" for row in formula_rows),
        "examples": sum(row["visual_status"] != "verified" for row in example_rows),
    }
    report = {
        "valid": not errors and not any(pending.values()),
        "automated_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "source_pdf": str(args.source_pdf.resolve()),
        "source_pdf_sha256": sha256(args.source_pdf.resolve()),
        "counts": {
            "pages": 992, "units": len(units), "blocks": len(unit_rows),
            "formulas": len(formula_rows), "logical_tables": len(table_rows),
            "figures": len(figure_rows), "examples": len(example_rows),
            "page_contact_sheets": len(page_contacts), "figure_contact_sheets": len(figure_contacts),
            "formula_contact_sheets": len(formula_contacts), "table_contact_sheets": len(table_contacts),
            "example_contact_sheets": len(example_contacts),
        },
        "pending_visual_review": pending,
        "low_similarity_blocks": len(warnings),
        "uncovered_substantive_source_blocks": len(uncovered_source_blocks),
    }
    write_json(output / "report.json", report)
    (output / "report.md").write_text(
        "# Genetics accuracy audit\n\n"
        f"- automated_valid: `{report['automated_valid']}`\n"
        f"- valid (including visual review): `{report['valid']}`\n"
        f"- counts: `{json.dumps(report['counts'], ensure_ascii=False)}`\n"
        f"- pending visual review: `{json.dumps(pending, ensure_ascii=False)}`\n"
        f"- automated errors: `{len(errors)}`\n"
        f"- low-similarity source comparisons: `{len(warnings)}`\n",
        encoding="utf-8",
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, default=ROOT / "data" / "背景资料" / "Genetics.pdf")
    parser.add_argument("--stage", type=Path, default=ROOT / "tmp" / "genetics_rebuild" / "staging")
    parser.add_argument("--rebuild-workspace", type=Path, default=ROOT / "tmp" / "genetics_rebuild")
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "genetics_accuracy_audit")
    parser.add_argument("--dpi", type=int, default=96)
    parser.add_argument("--skip-render", action="store_true")
    return parser.parse_args()


def main() -> int:
    report = build_audit(parse_args())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
