"""Finalize the rule-only PopGen chapters from temporary Paddle artifacts.

The script deliberately stages every derived artifact below tmp/popgen before
installing only the verified, book-prefixed deliverables into data/.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from textbook_exporter import export_textbooks

CHAPTERS = (2, 3, 4, 6)
FORMULA_NUMBER_RE = re.compile(
    r"^[\[({]\s*(?P<number>\d+\.\d+[a-z]?)\s*[\])}]$",
    re.IGNORECASE,
)
DIRECT_PLACEHOLDER_RE = re.compile(r"\[\[(?:FORMULA|TABLE|FIGURE|EXAMPLE):[^\]]+\]\]", re.IGNORECASE)
FIGURE_LINK_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")

EXPECTED_FIGURES = {
    2: {f"2.{number}" for number in range(1, 12)},
    3: {f"3.{number}" for number in range(1, 19)},
    4: {f"4.{number}" for number in range(1, 19)} - {"4.19"},
    6: {f"6.{number}" for number in range(1, 27)},
}

# Paddle merged these three captions into chart blocks.  The crop still comes
# from the original PDF and its bbox; only the human-readable caption is
# transcribed from the same visible page.
MERGED_CHART_FIGURES = {
    (4, "4.1"): {
        "page": 3,
        "bbox": [109, 175, 636, 505],
        "caption": (
            "FIGURE 4.1 Change in allele frequency under mutation pressure. In this example, an allele A mutates "
            "to a at a rate of μ = 1 × 10^-4 per generation; p_t is the allele frequency of A in generation t. "
            "We assume that p_0 = 1. With the given value of μ, the allele frequency decreases by half every "
            "6931 generations."
        ),
    },
    (4, "4.4"): {
        "page": 7,
        "bbox": [156, 174, 906, 482],
        "caption": (
            "FIGURE 4.4 Theoretical change in allele frequency under pressure of reversible mutation. The "
            "attainment of near-equilibrium values requires tens of thousands of generations for realistic "
            "mutation rates. In this example, the forward mutation rate (A to a) is μ = 10^-4 and the reverse "
            "mutation rate (a to A) is ν = 10^-5. The equilibrium allele frequency of A is 0.091."
        ),
    },
    (6, "6.22"): {
        "page": 47,
        "bbox": [113, 182, 864, 510],
        "caption": (
            "FIGURE 6.22 Distribution of estimated values of F_ST for 61 genes among natural populations of "
            "Drosophila melanogaster. Although the average value of F_ST suggests migration at a level of Nm "
            "between 1 and 2, about one-third of the genes have F_ST values greater than 0.20. (From Singh and "
            "Rhomberg 1987.)"
        ),
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_formula(value: str) -> str:
    value = str(value or "")
    value = re.sub(r"\$", "", value)
    value = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", value)
    value = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\operatorname\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\tag\{[^}]*\}", "", value)
    return re.sub(r"\s+", "", value)


def without_display_delimiters(value: str) -> str:
    value = str(value or "").strip()
    return value[2:-2].strip() if value.startswith("$$") and value.endswith("$$") else value


def center_y(block: dict[str, Any]) -> float:
    bbox = block.get("block_bbox") or [0, 0, 0, 0]
    return (float(bbox[1]) + float(bbox[3])) / 2


def chapter_units(source_dir: Path, chapter: int) -> list[tuple[dict[str, Any], str]]:
    units = []
    for path in sorted(source_dir.glob(f"PopGen_chapter{chapter}_*.json")):
        unit = read_json(path)
        content = "\n".join(str(block.get("content") or "") for block in unit.get("blocks", []))
        units.append((unit, content))
    return units


def context_excerpt(content: str, latex: str, limit: int = 1400) -> str:
    needle = without_display_delimiters(latex).strip()
    position = content.find(needle)
    if position < 0:
        return content[:limit]
    start = max(0, position - limit // 2)
    return content[start : start + limit]


def build_formula_library(source_dir: Path, paddle_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    formulas: list[dict[str, Any]] = []
    raw_label_count = 0
    canonical_occurrences: defaultdict[str, int] = defaultdict(int)
    per_chapter: dict[str, int] = {}

    for chapter in CHAPTERS:
        units = chapter_units(source_dir, chapter)
        raw_path = paddle_dir / f"PopGen_chapter{chapter}_full" / "intermediate" / "paddle_raw_response.json"
        pages = read_json(raw_path)
        chapter_count = 0
        for page_number, page in enumerate(pages, start=1):
            blocks = page.get("parsing_res_list") or page.get("prunedResult", {}).get("parsing_res_list", [])
            displays = [block for block in blocks if block.get("block_label") == "display_formula"]
            for label in (block for block in blocks if block.get("block_label") == "formula_number"):
                match = FORMULA_NUMBER_RE.fullmatch(str(label.get("block_content") or "").strip())
                if not match:
                    continue
                raw_label_count += 1
                chapter_count += 1
                number = match.group("number")
                candidates = sorted(
                    (
                        (abs(center_y(display) - center_y(label)), display)
                        for display in displays
                        if abs(center_y(display) - center_y(label)) <= 160
                    ),
                    key=lambda item: item[0],
                )
                if not candidates:
                    raise ValueError(f"PopGen chapter {chapter} page {page_number}: formula [{number}] has no display")
                distance, display = candidates[0]
                raw_latex = str(display.get("block_content") or "")
                canonical = canonical_formula(raw_latex)
                matching_units = [(unit, content) for unit, content in units if canonical in canonical_formula(content)]
                if not matching_units:
                    raise ValueError(f"PopGen chapter {chapter}: formula [{number}] has no structured owner")
                occurrence = canonical_occurrences[canonical]
                canonical_occurrences[canonical] += 1
                unit, content = matching_units[min(occurrence, len(matching_units) - 1)]
                metadata = unit.get("metadata") if isinstance(unit.get("metadata"), dict) else {}
                formulas.append(
                    {
                        "id": number,
                        "label_format": f"[{number}]",
                        "latex": without_display_delimiters(raw_latex),
                        "formula_type": "block",
                        "source": {
                            "unit_id": unit["id"],
                            "chapter": f"PopGen_chapter{chapter}",
                            "subsection": metadata.get("display_heading") or metadata.get("section"),
                        },
                        "context": context_excerpt(content, raw_latex),
                        "description": None,
                        "book": "PopGen",
                        "source_evidence": {
                            "evidence_type": "paddleocr_vl_layout",
                            "source_pdf": f"data/背景资料/PopGen_chapter{chapter}.pdf",
                            "pdf_page": page_number,
                            "formula_bbox": display.get("block_bbox"),
                            "label_bbox": label.get("block_bbox"),
                            "api_label": label.get("block_content"),
                            "raw_response": (
                                f"tmp/popgen/paddle_output/PopGen_chapter{chapter}_full/intermediate/"
                                "paddle_raw_response.json"
                            ),
                            "vertical_pairing_distance": round(distance, 2),
                        },
                        "equation_number": number,
                        "number_status": "verified_paddleocr_layout",
                        "render_mode": "numbered_equation",
                    }
                )
        per_chapter[str(chapter)] = chapter_count

    numbers = [formula["equation_number"].lower() for formula in formulas]
    if len(numbers) != len(set(numbers)):
        duplicates = sorted(number for number in set(numbers) if numbers.count(number) > 1)
        raise ValueError(f"Duplicate PopGen equation labels: {duplicates}")
    if len(formulas) != raw_label_count:
        raise ValueError("Not every Paddle formula label was restored")
    return (
        {
            "version": 1,
            "book": "PopGen",
            "asset_type": "formula",
            "authority": "book-scoped source of truth",
            "formulas": formulas,
        },
        {"total": len(formulas), "per_chapter": per_chapter, "raw_labels": raw_label_count},
    )


def normalize_chunks(source_dir: Path, target_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for chapter in CHAPTERS:
        paths = sorted(source_dir.glob(f"PopGen_chapter{chapter}_*.json"))
        expected_ids = [f"PopGen_chapter{chapter}_{index:03d}" for index in range(1, len(paths) + 1)]
        actual_ids = []
        for path in paths:
            unit = read_json(path)
            actual_ids.append(str(unit.get("id") or ""))
            metadata = unit.setdefault("metadata", {})
            metadata["chapter"] = f"PopGen_chapter{chapter}"
            write_json(target_dir / path.name, unit)
        if actual_ids != expected_ids:
            raise ValueError(f"PopGen chapter {chapter} chunk ids are not continuous")
        counts[str(chapter)] = len(paths)
    return counts


def build_table_library(source_path: Path) -> dict[str, Any]:
    payload = read_json(source_path)
    tables = []
    for table in payload.get("tables", []):
        table = copy.deepcopy(table)
        source = table.setdefault("source", {})
        match = re.search(r"chapter(\d+)", str(source.get("chapter") or ""), re.IGNORECASE)
        if not match:
            raise ValueError(f"Table {table.get('id')} has no chapter source")
        source["chapter"] = f"PopGen_chapter{int(match.group(1))}"
        table["book"] = "PopGen"
        table["asset_key"] = f"PopGen:{source['chapter']}:{table.get('id')}"
        tables.append(table)
    return {
        "version": 1,
        "book": "PopGen",
        "asset_type": "table",
        "authority": "book-scoped source of truth",
        "tables": tables,
    }


def crop_manual_figure(
    stage_data: Path,
    paddle_dir: Path,
    pdf_dir: Path,
    chapter: int,
    figure_id: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    page_number = int(spec["page"])
    raw_path = paddle_dir / f"PopGen_chapter{chapter}_full" / "intermediate" / "paddle_raw_response.json"
    raw_page = read_json(raw_path)[page_number - 1]
    raw_width = float(raw_page["width"])
    raw_height = float(raw_page["height"])
    pdf_path = pdf_dir / f"PopGen_chapter{chapter}.pdf"
    document = fitz.open(pdf_path)
    try:
        page = document[page_number - 1]
        bbox = [float(value) for value in spec["bbox"]]
        margin = 14.0
        bbox = [
            max(0.0, bbox[0] - margin),
            max(0.0, bbox[1] - margin),
            min(raw_width, bbox[2] + margin),
            min(raw_height, bbox[3] + margin),
        ]
        rect = fitz.Rect(
            bbox[0] * page.rect.width / raw_width,
            bbox[1] * page.rect.height / raw_height,
            bbox[2] * page.rect.width / raw_width,
            bbox[3] * page.rect.height / raw_height,
        ) & page.rect
        asset_name = f"PopGen_{figure_id}.png"
        asset_path = stage_data / "figures" / asset_name
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(clip=rect, dpi=300, alpha=False).save(asset_path)
    finally:
        document.close()
    return {
        "id": figure_id,
        "chapter": f"PopGen_chapter{chapter}",
        "placeholder": f"[[FIGURE:{figure_id}]]",
        "see_placeholder": f"[[SEE_FIGURE:{figure_id}]]",
        "asset_path": f"figures/{asset_name}",
        "caption": spec["caption"],
        "source_pdf": f"data/背景资料/PopGen_chapter{chapter}.pdf",
        "source_paddle_raw": (
            f"tmp/popgen/paddle_output/PopGen_chapter{chapter}_full/intermediate/paddle_raw_response.json"
        ),
        "page": page_number,
        "raw_bbox": [round(value, 2) for value in bbox],
        "pdf_bbox": [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)],
        "bbox_source": "Paddle chart block with caption merged into layout region",
        "confidence": 0.9,
        "book": "PopGen",
        "asset_key": f"PopGen:PopGen_chapter{chapter}:{figure_id}",
    }


def build_figure_library(
    source_path: Path,
    source_figures: Path,
    stage_data: Path,
    paddle_dir: Path,
    pdf_dir: Path,
) -> dict[str, Any]:
    payload = read_json(source_path)
    records = payload.get("figures", {})
    records = list(records.values()) if isinstance(records, dict) else list(records)
    figures: list[dict[str, Any]] = []
    for figure in records:
        figure = copy.deepcopy(figure)
        asset_name = Path(str(figure.get("asset_path") or "")).name
        source_asset = source_figures / asset_name
        if not source_asset.exists():
            raise ValueError(f"Missing cropped figure {source_asset}")
        target_asset = stage_data / "figures" / asset_name
        target_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_asset, target_asset)
        figure["asset_path"] = f"figures/{asset_name}"
        figure["source_pdf"] = f"data/背景资料/{figure['chapter']}.pdf"
        figure["source_paddle_raw"] = (
            f"tmp/popgen/paddle_output/{figure['chapter']}_full/intermediate/paddle_raw_response.json"
        )
        figure["book"] = "PopGen"
        figure["asset_key"] = f"PopGen:{figure['chapter']}:{figure['id']}"
        figures.append(figure)

    existing = {(int(re.search(r"chapter(\d+)", figure["chapter"]).group(1)), figure["id"]) for figure in figures}
    for (chapter, figure_id), spec in MERGED_CHART_FIGURES.items():
        if (chapter, figure_id) not in existing:
            figures.append(crop_manual_figure(stage_data, paddle_dir, pdf_dir, chapter, figure_id, spec))

    for chapter, expected in EXPECTED_FIGURES.items():
        actual = {figure["id"] for figure in figures if figure["chapter"] == f"PopGen_chapter{chapter}"}
        if actual != expected:
            raise ValueError(
                f"PopGen chapter {chapter} figure coverage mismatch; missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
            )
    return {
        "version": 1,
        "book": "PopGen",
        "asset_type": "figure",
        "authority": "book-scoped source of truth",
        "figures": sorted(figures, key=lambda item: [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", item["id"])],),
    }


def verify_textbooks(stage_data: Path, formula_library: dict[str, Any]) -> dict[str, Any]:
    textbook_dir = stage_data / "textbook"
    unresolved: list[str] = []
    missing_images: list[str] = []
    combined = ""
    for path in sorted(textbook_dir.glob("PopGen_chapter*_textbook.md")):
        content = path.read_text(encoding="utf-8")
        combined += "\n" + content
        unresolved.extend(f"{path.name}:{match.group(0)}" for match in DIRECT_PLACEHOLDER_RE.finditer(content))
        for match in FIGURE_LINK_RE.finditer(content):
            if not (path.parent / match.group("path")).resolve().exists():
                missing_images.append(f"{path.name}:{match.group('path')}")
    missing_formula_tags = [
        formula["equation_number"]
        for formula in formula_library["formulas"]
        if f"\\tag{{{formula['equation_number']}}}" not in combined
    ]
    if unresolved or missing_images or missing_formula_tags:
        raise ValueError(
            f"Textbook verification failed: unresolved={len(unresolved)} missing_images={len(missing_images)} "
            f"missing_formula_tags={len(missing_formula_tags)}"
        )
    return {
        "chapters": len(list(textbook_dir.glob("PopGen_chapter*_textbook.md"))),
        "unresolved_direct_placeholders": unresolved,
        "missing_images": missing_images,
        "missing_formula_tags": missing_formula_tags,
    }


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.popgen-tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)


def install(stage_data: Path) -> dict[str, int]:
    groups = {
        "structured": (stage_data / "structured", ROOT / "data" / "structured", "PopGen_*"),
        "figures": (stage_data / "figures", ROOT / "data" / "figures", "PopGen_*.png"),
        "textbook": (stage_data / "textbook", ROOT / "data" / "textbook", "PopGen_*_textbook.md"),
        "textbook_figures": (
            stage_data / "textbook" / "figures",
            ROOT / "data" / "textbook" / "figures",
            "PopGen_*.png",
        ),
    }
    counts: dict[str, int] = {}
    for name, (source_dir, target_dir, pattern) in groups.items():
        paths = sorted(source_dir.glob(pattern))
        for source in paths:
            atomic_copy(source, target_dir / source.name)
        counts[name] = len(paths)
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize verified PopGen structured/textbook assets.")
    parser.add_argument("--source-structured", type=Path, default=ROOT / "tmp" / "popgen" / "structured")
    parser.add_argument("--paddle-dir", type=Path, default=ROOT / "tmp" / "popgen" / "paddle_output")
    parser.add_argument("--figure-build", type=Path, default=ROOT / "tmp" / "popgen" / "figure_build_v4")
    parser.add_argument("--pdf-dir", type=Path, default=ROOT / "data" / "背景资料")
    parser.add_argument("--stage", type=Path, default=ROOT / "tmp" / "popgen" / "final_stage")
    parser.add_argument("--install", action="store_true", help="Atomically copy verified PopGen-prefixed outputs into data/.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stage = args.stage.resolve()
    allowed = (ROOT / "tmp" / "popgen").resolve()
    if stage != allowed and allowed not in stage.parents:
        raise ValueError(f"Staging directory must remain under {allowed}")
    if stage.exists():
        shutil.rmtree(stage)
    stage_data = stage / "data"
    structured_target = stage_data / "structured"
    structured_target.mkdir(parents=True, exist_ok=True)

    chunk_counts = normalize_chunks(args.source_structured.resolve(), structured_target)
    formulas, formula_audit = build_formula_library(args.source_structured.resolve(), args.paddle_dir.resolve())
    tables = build_table_library(args.source_structured.resolve() / "table_library.json")
    figures = build_figure_library(
        args.figure_build.resolve() / "figure_library.json",
        args.figure_build.resolve() / "figures",
        stage_data,
        args.paddle_dir.resolve(),
        args.pdf_dir.resolve(),
    )
    write_json(structured_target / "PopGen_formula_library.json", formulas)
    write_json(structured_target / "PopGen_table_library.json", tables)
    write_json(structured_target / "PopGen_figure_library.json", figures)
    write_json(stage_data / "figure_library.json", {"version": 1, "figures": {}})

    export_textbooks(
        structured_dir=structured_target,
        out_dir=stage_data / "textbook",
        chapters={f"PopGen_chapter{chapter}" for chapter in CHAPTERS},
        figure_library=stage_data / "figure_library.json",
        book_id="PopGen",
    )
    textbook_audit = verify_textbooks(stage_data, formulas)
    example_heading_count = sum(
        len(re.findall(r"^\s*Example\s+\d+", path.read_text(encoding="utf-8"), flags=re.IGNORECASE | re.MULTILINE))
        for path in args.paddle_dir.resolve().glob("PopGen_chapter*_full/main.tex")
    )
    if example_heading_count:
        raise ValueError(f"Found {example_heading_count} raw Example headings but no PopGen examples were extracted")

    installed = install(stage_data) if args.install else {}
    report = {
        "valid": True,
        "rule_only": True,
        "remote_llm_calls": 0,
        "chunks": chunk_counts,
        "formulas": formula_audit,
        "tables": len(tables["tables"]),
        "figures": len(figures["figures"]),
        "examples": 0,
        "raw_example_headings": example_heading_count,
        "textbook": textbook_audit,
        "installed": installed,
    }
    write_json(stage / "verification.json", report)
    write_json(ROOT / "tmp" / "popgen" / "final_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
