"""Build a figure library from Paddle raw layout and original PDFs."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
FIGURE_CAPTION_RE = re.compile(
    r"^\s*(?:Figure|Fig\.)\s+(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\b(?P<caption>.*)",
    re.IGNORECASE,
)
PANEL_LABEL_RE = re.compile(r"^\s*\(?[A-Z]\)(?:\s+.+)?\s*$")
BODY_LABELS = {"image", "chart", "display_formula"}
FALLBACK_BODY_LABELS = {"paragraph_title", "table", "text"}
PANEL_LABELS = {"figure_title"}


@dataclass
class RawRow:
    page_number: int
    index: int
    label: str
    content: str
    bbox: list[float]
    block_id: Any
    block_order: Any

    @property
    def top(self) -> float:
        return float(self.bbox[1])

    @property
    def bottom(self) -> float:
        return float(self.bbox[3])

    @property
    def left(self) -> float:
        return float(self.bbox[0])


@dataclass
class BodyMatch:
    rows: list[RawRow]
    bbox_rows: list[RawRow]
    bbox_source: str
    confidence: float


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name.lower())]


def book_prefix_from_chapter(chapter: str) -> str:
    match = re.match(r"^(?P<prefix>[A-Za-z]+)_(?:chapter|appendix)\d+\b", chapter.strip(), flags=re.IGNORECASE)
    return match.group("prefix") if match else ""


def figure_library_key(figure_id: str, chapter: str, existing_keys: set[str]) -> str:
    prefix = book_prefix_from_chapter(chapter)
    base = f"{prefix}_{figure_id}" if prefix else figure_id
    key = base
    counter = 2
    while key in existing_keys:
        key = f"{base}#{counter}"
        counter += 1
    existing_keys.add(key)
    return key


def figure_asset_name(figure_id: str, chapter: str, used_names: set[str]) -> str:
    base = re.sub(r'[<>:"/\\|?*\s]+', "_", figure_id.strip()).strip("._")
    if not base:
        base = re.sub(r'[<>:"/\\|?*\s]+', "_", chapter.strip()).strip("._") or "figure"
    prefix = book_prefix_from_chapter(chapter)
    if prefix:
        base = f"{prefix}_{base}"
    asset_name = f"{base}.png"
    if asset_name.lower() not in used_names:
        used_names.add(asset_name.lower())
        return asset_name

    chapter_suffix = re.sub(r'[<>:"/\\|?*\s]+', "_", chapter.strip()).strip("._")
    fallback_base = f"{base}_{chapter_suffix}" if chapter_suffix else base
    asset_name = f"{fallback_base}.png"
    if asset_name.lower() not in used_names:
        used_names.add(asset_name.lower())
        return asset_name

    counter = 2
    while True:
        asset_name = f"{fallback_base}_{counter}.png"
        if asset_name.lower() not in used_names:
            used_names.add(asset_name.lower())
            return asset_name
        counter += 1


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def page_rows(page: dict[str, Any], page_number: int) -> list[RawRow]:
    rows = page.get("parsing_res_list")
    if not isinstance(rows, list):
        pruned = page.get("prunedResult", {})
        rows = pruned.get("parsing_res_list") if isinstance(pruned, dict) else []
    result: list[RawRow] = []
    for index, row in enumerate(rows or []):
        if not isinstance(row, dict):
            continue
        bbox = row.get("block_bbox") or row.get("bbox")
        if not (isinstance(bbox, list) and len(bbox) >= 4):
            continue
        try:
            numeric_bbox = [float(value) for value in bbox[:4]]
        except (TypeError, ValueError):
            continue
        result.append(
            RawRow(
                page_number=page_number,
                index=index,
                label=str(row.get("block_label") or row.get("label") or "").strip().lower(),
                content=str(row.get("block_content") or row.get("text") or "").strip(),
                bbox=numeric_bbox,
                block_id=row.get("block_id"),
                block_order=row.get("block_order"),
            )
        )
    return sorted(result, key=lambda item: (item.top, item.left, item.index))


def is_figure_caption(row: RawRow) -> re.Match[str] | None:
    if row.label != "figure_title":
        return None
    return FIGURE_CAPTION_RE.match(row.content)


def is_previous_figure_boundary(row: RawRow) -> bool:
    return bool(is_figure_caption(row))


def is_panel_label(row: RawRow) -> bool:
    return row.label in PANEL_LABELS and bool(PANEL_LABEL_RE.match(row.content))


def is_short_figure_body_label(row: RawRow, selected: list[RawRow]) -> bool:
    if row.label != "text" or not selected:
        return False
    if len(row.content.strip()) > 120:
        return False
    nearest_top = min(item.top for item in selected)
    return 0 <= nearest_top - row.bottom <= 80


def union_bbox(rows: list[RawRow]) -> list[float]:
    return [
        min(row.bbox[0] for row in rows),
        min(row.bbox[1] for row in rows),
        max(row.bbox[2] for row in rows),
        max(row.bbox[3] for row in rows),
    ]


def expand_bbox(bbox: list[float], width: float, height: float, margin: float) -> list[float]:
    return [
        max(0.0, bbox[0] - margin),
        max(0.0, bbox[1] - margin),
        min(width, bbox[2] + margin),
        min(height, bbox[3] + margin),
    ]


def scale_bbox_to_pdf(raw_bbox: list[float], raw_width: float, raw_height: float, page: fitz.Page) -> fitz.Rect:
    scale_x = page.rect.width / raw_width if raw_width else 1.0
    scale_y = page.rect.height / raw_height if raw_height else 1.0
    rect = fitz.Rect(
        raw_bbox[0] * scale_x,
        raw_bbox[1] * scale_y,
        raw_bbox[2] * scale_x,
        raw_bbox[3] * scale_y,
    )
    return rect & page.rect


def raw_page_size(page_payload: dict[str, Any], rows: list[RawRow], page: fitz.Page) -> tuple[float, float]:
    raw_width = float(page_payload.get("width") or 0)
    raw_height = float(page_payload.get("height") or 0)
    if raw_width > 0 and raw_height > 0:
        return raw_width, raw_height

    max_x = max((row.bbox[2] for row in rows), default=page.rect.width)
    max_y = max((row.bbox[3] for row in rows), default=page.rect.height)
    scale_hint = max(
        max_x / page.rect.width if page.rect.width else 1.0,
        max_y / page.rect.height if page.rect.height else 1.0,
        1.0,
    )
    if scale_hint > 1.15:
        scale_hint = math.ceil(scale_hint * 2.0) / 2.0
    return page.rect.width * scale_hint, page.rect.height * scale_hint


def find_fallback_body_rows(rows: list[RawRow], caption_index: int) -> list[RawRow]:
    caption = rows[caption_index]
    selected: list[RawRow] = []
    previous_top = caption.top
    for row in reversed(rows[:caption_index]):
        if is_previous_figure_boundary(row):
            break
        if row.bottom > caption.top + 8:
            continue
        gap = previous_top - row.bottom
        if gap > (150.0 if not selected else 90.0):
            break
        if row.label not in FALLBACK_BODY_LABELS:
            if selected:
                break
            continue
        if (row.bbox[2] - row.bbox[0]) < 80 or (row.bbox[3] - row.bbox[1]) < 25:
            if selected:
                break
            continue
        selected.append(row)
        previous_top = row.top
        if len(selected) >= 4:
            break
    selected.sort(key=lambda item: (item.top, item.left, item.index))
    return selected


def find_body_rows(rows: list[RawRow], caption_index: int) -> BodyMatch | None:
    caption = rows[caption_index]
    selected: list[RawRow] = []
    saw_body = False
    for row in reversed(rows[:caption_index]):
        if is_previous_figure_boundary(row):
            break
        if row.bottom > caption.top + 8:
            continue
        if row.label in BODY_LABELS:
            selected.append(row)
            saw_body = True
            continue
        if saw_body and is_short_figure_body_label(row, selected):
            selected.append(row)
            continue
        if is_panel_label(row):
            selected.append(row)
            continue
        if saw_body:
            break
    body_rows = [row for row in selected if row.label in BODY_LABELS]
    if body_rows:
        selected.sort(key=lambda item: (item.top, item.left, item.index))
        bbox_rows = selected if all(row.label == "display_formula" for row in body_rows) else body_rows
        return BodyMatch(
            rows=selected,
            bbox_rows=bbox_rows,
            bbox_source="union of preceding figure body blocks",
            confidence=0.95,
        )
    fallback_rows = find_fallback_body_rows(rows, caption_index)
    if fallback_rows:
        return BodyMatch(
            rows=fallback_rows,
            bbox_rows=fallback_rows,
            bbox_source="nearest preceding non-caption layout block fallback",
            confidence=0.72,
        )
    return None


def body_match_summary(match: BodyMatch) -> str:
    labels = ",".join(row.label for row in match.bbox_rows)
    pages = sorted({row.page_number for row in match.bbox_rows})
    return f"{match.bbox_source}; labels={labels}; pages={pages}"


def chapter_from_output_dir(path: Path) -> str:
    name = path.name
    return name[: -len("_full")] if name.endswith("_full") else name


def pdf_for_chapter(pdf_dir: Path, chapter: str) -> Path | None:
    direct = pdf_dir / f"{chapter}.pdf"
    if direct.exists():
        return direct
    for candidate in pdf_dir.glob("*.pdf"):
        if candidate.stem.lower() == chapter.lower():
            return candidate
    matches = sorted(pdf_dir.rglob(f"{chapter}.pdf"), key=natural_key)
    return matches[0] if matches else None


def summarize_row(row: RawRow) -> dict[str, Any]:
    return {
        "page": row.page_number,
        "label": row.label,
        "content": row.content,
        "bbox": [round(value, 2) for value in row.bbox],
        "block_id": row.block_id,
        "block_order": row.block_order,
    }


def render_audit_md(audit: dict[str, Any]) -> str:
    lines = [
        "# Figure Library Audit",
        "",
        f"- generated_at: {audit.get('generated_at', '')}",
        f"- figures: {audit.get('figures', 0)}",
        f"- cropped: {audit.get('cropped', 0)}",
        f"- missing_body: {len(audit.get('missing_body', []))}",
        f"- fallback_body: {len(audit.get('fallback_body', []))}",
        f"- missing_pdf: {len(audit.get('missing_pdf', []))}",
        f"- crop_failed: {len(audit.get('crop_failed', []))}",
        "",
    ]
    for key in ("missing_pdf", "missing_body", "fallback_body", "crop_failed"):
        items = audit.get(key, [])
        if not items:
            continue
        lines.append(f"## {key}")
        lines.append("")
        for item in items[:100]:
            lines.append(f"- {item}")
        if len(items) > 100:
            lines.append(f"- ... {len(items) - 100} more")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build figure_library.json and cropped figure assets.")
    parser.add_argument("--paddle-output-dir", type=Path, default=ROOT / "data" / "paddle_output")
    parser.add_argument("--pdf-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "figure_relink_probe")
    parser.add_argument("--chapters", default="", help="Comma-separated chapter ids, e.g. chapter21,appendix4.")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--margin", type=float, default=14.0)
    return parser.parse_args()


def discover_pdf_dir(pdf_dir: Path | None) -> Path:
    if pdf_dir is not None:
        return pdf_dir.resolve()
    preferred = ROOT / "data" / "背景资料"
    if preferred.exists():
        return preferred.resolve()
    candidates = [
        path
        for path in (ROOT / "data").iterdir()
        if path.is_dir() and any(path.glob("*.pdf"))
    ]
    if len(candidates) == 1:
        return candidates[0].resolve()
    return preferred.resolve()


def main() -> int:
    args = parse_args()
    paddle_dir = args.paddle_output_dir.resolve()
    pdf_dir = discover_pdf_dir(args.pdf_dir)
    output_dir = args.output.resolve()
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    chapter_filter = {item.strip().lower() for item in args.chapters.split(",") if item.strip()}
    raw_paths = sorted(paddle_dir.glob("*_full/intermediate/paddle_raw_response.json"), key=natural_key)
    library: dict[str, Any] = {
        "version": 1,
        "generated_at": utc_now(),
        "source": {
            "source_of_truth": "Original PDFs under data/背景资料.",
            "paddle_output_dir": str(paddle_dir),
            "pdf_dir": str(pdf_dir),
            "bbox_source": "Paddle raw layout; original PDF crop",
        },
        "figures": {},
    }
    audit: dict[str, Any] = {
        "generated_at": library["generated_at"],
        "figures": 0,
        "cropped": 0,
        "missing_pdf": [],
        "missing_body": [],
        "fallback_body": [],
        "crop_failed": [],
        "duplicate_ids": [],
    }

    used_asset_names: set[str] = set()
    used_library_keys: set[str] = set()
    for raw_path in raw_paths:
        chapter = chapter_from_output_dir(raw_path.parents[1])
        if chapter_filter and chapter.lower() not in chapter_filter:
            continue
        pdf_path = pdf_for_chapter(pdf_dir, chapter)
        if pdf_path is None:
            audit["missing_pdf"].append(chapter)
            continue

        pages = load_json(raw_path)
        if not isinstance(pages, list):
            audit["crop_failed"].append(f"{chapter}: raw payload is not a page list")
            continue

        pdf = fitz.open(pdf_path)
        try:
            for page_index, page_payload in enumerate(pages):
                if not isinstance(page_payload, dict):
                    continue
                page_number = page_index + 1
                if page_number > pdf.page_count:
                    audit["crop_failed"].append(
                        f"{chapter}:page{page_number}: raw page exceeds pdf page count {pdf.page_count}"
                    )
                    continue
                page = pdf[page_number - 1]
                rows = page_rows(page_payload, page_number)
                raw_width, raw_height = raw_page_size(page_payload, rows, page)
                for row_index, row in enumerate(rows):
                    match = is_figure_caption(row)
                    if not match:
                        continue
                    figure_id = match.group("id")
                    caption = row.content
                    key = figure_library_key(figure_id, chapter, used_library_keys)
                    base_key = f"{book_prefix_from_chapter(chapter)}_{figure_id}" if book_prefix_from_chapter(chapter) else figure_id
                    if key != base_key:
                        audit["duplicate_ids"].append(f"{chapter}:{figure_id}")
                    body_match = find_body_rows(rows, row_index)
                    if not body_match:
                        audit["missing_body"].append(f"{chapter}:{figure_id}:page{page_number}")
                        continue
                    if body_match.confidence < 0.9:
                        audit["fallback_body"].append(
                            f"{chapter}:{figure_id}:page{page_number}:{body_match_summary(body_match)}"
                        )
                    raw_bbox = expand_bbox(union_bbox(body_match.bbox_rows), raw_width, raw_height, args.margin)
                    asset_name = figure_asset_name(figure_id, chapter, used_asset_names)
                    asset_path = figures_dir / asset_name

                    try:
                        pdf_rect = scale_bbox_to_pdf(raw_bbox, raw_width, raw_height, page)
                        if pdf_rect.is_empty or not math.isfinite(pdf_rect.width) or not math.isfinite(pdf_rect.height):
                            raise RuntimeError("empty crop rect")
                        pix = page.get_pixmap(clip=pdf_rect, dpi=args.dpi, alpha=False)
                        pix.save(str(asset_path))
                        audit["cropped"] += 1
                    except Exception as exc:
                        audit["crop_failed"].append(f"{chapter}:{figure_id}:page{page_number}:{exc}")
                        continue

                    library["figures"][key] = {
                        "id": figure_id,
                        "chapter": chapter,
                        "placeholder": f"[[FIGURE:{figure_id}]]",
                        "see_placeholder": f"[[SEE_FIGURE:{figure_id}]]",
                        "asset_path": str(asset_path.relative_to(output_dir)).replace("\\", "/"),
                        "caption": caption,
                        "source_pdf": str(pdf_path),
                        "source_paddle_raw": str(raw_path),
                        "page": page_number,
                        "raw_bbox": [round(value, 2) for value in raw_bbox],
                        "pdf_bbox": [round(value, 2) for value in pdf_rect],
                        "bbox_source": body_match.bbox_source,
                        "body_blocks": [summarize_row(item) for item in body_match.rows],
                        "caption_block": summarize_row(row),
                        "confidence": body_match.confidence,
                    }
        finally:
            pdf.close()

    audit["figures"] = len(library["figures"])
    (output_dir / "figure_library.json").write_text(
        json.dumps(library, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "audit.md").write_text(render_audit_md(audit), encoding="utf-8")
    print(
        f"figures={audit['figures']} cropped={audit['cropped']} "
        f"missing_body={len(audit['missing_body'])} crop_failed={len(audit['crop_failed'])}"
    )
    print(output_dir)
    return 0 if not audit["crop_failed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
