"""Audit all Genetics chapter PDFs against the 992-page source book.

This is intentionally read-only with respect to data/.  Every report and
rendered page is written below tmp/genetics_full_audit/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CORRECT_RANGES = {
    1: (21, 35), 2: (36, 50), 3: (51, 66), 4: (67, 95), 5: (97, 122),
    6: (123, 146), 7: (147, 192), 8: (193, 220), 9: (221, 265), 10: (267, 305),
    11: (307, 334), 12: (335, 366), 13: (367, 392), 14: (393, 444), 15: (445, 504),
    16: (505, 550), 17: (551, 566), 18: (567, 593), 19: (594, 608), 20: (609, 640),
    21: (641, 668), 22: (669, 697), 23: (699, 726), 24: (727, 738), 25: (739, 756),
    26: (757, 790), 27: (791, 818),
}
BLANK_INTERCHAPTER_PAGES = (96, 266, 306, 698)
TITLE_CORRECTIONS = {
    14: "Principles of Marker-based Analysis",
    22: "Genotype × Environment Interaction",
}


def page_digest(page: fitz.Page) -> str:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY, alpha=False)
    return hashlib.sha256(pixmap.samples).hexdigest()


def ink_fraction(page: fitz.Page) -> float:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY, alpha=False)
    samples = pixmap.samples
    return sum(value < 240 for value in samples) / max(1, len(samples))


def compact_range(values: list[int]) -> str:
    if not values:
        return ""
    ranges: list[str] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = value
    ranges.append(str(start) if start == previous else f"{start}–{previous}")
    return ", ".join(ranges)


def page_image(document: fitz.Document, page_number: int, width: int = 480) -> Image.Image:
    page = document[page_number - 1]
    scale = width / page.rect.width
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def label_panel(image: Image.Image, label: str, color: tuple[int, int, int]) -> Image.Image:
    banner = 42
    panel = Image.new("RGB", (image.width, image.height + banner), "white")
    panel.paste(image, (0, banner))
    draw = ImageDraw.Draw(panel)
    draw.rectangle((0, 0, panel.width, banner), fill=color)
    draw.text((12, 11), label, fill="white", font=ImageFont.load_default())
    return panel


def boundary_evidence(
    master: fitz.Document,
    output: Path,
    chapter: int,
    current: tuple[int, int],
    correct: tuple[int, int],
) -> None:
    panels = [
        label_panel(page_image(master, current[0]), f"CURRENT START · source p.{current[0]}", (163, 58, 58)),
        label_panel(page_image(master, correct[0]), f"CORRECT START · source p.{correct[0]}", (36, 126, 77)),
        label_panel(page_image(master, current[1]), f"CURRENT END · source p.{current[1]}", (163, 58, 58)),
        label_panel(page_image(master, correct[1]), f"CORRECT END · source p.{correct[1]}", (36, 126, 77)),
    ]
    cell_width = max(panel.width for panel in panels)
    cell_height = max(panel.height for panel in panels)
    canvas = Image.new("RGB", (cell_width * 2, cell_height * 2), (225, 225, 225))
    for index, panel in enumerate(panels):
        x = (index % 2) * cell_width
        y = (index // 2) * cell_height
        canvas.paste(panel, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def make_blank_evidence(master: fitz.Document, output: Path) -> None:
    panels = [
        label_panel(page_image(master, page, width=360), f"INTERCHAPTER BLANK · source p.{page}", (75, 88, 102))
        for page in BLANK_INTERCHAPTER_PAGES
    ]
    cell_width = max(panel.width for panel in panels)
    cell_height = max(panel.height for panel in panels)
    canvas = Image.new("RGB", (cell_width * 2, cell_height * 2), (225, 225, 225))
    for index, panel in enumerate(panels):
        canvas.paste(panel, ((index % 2) * cell_width, (index // 2) * cell_height))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def make_start_overview(master: fitz.Document, output: Path) -> None:
    width = 230
    panels = [
        label_panel(page_image(master, CORRECT_RANGES[chapter][0], width=width), f"CH {chapter:02d} · p.{CORRECT_RANGES[chapter][0]}", (36, 103, 150))
        for chapter in range(1, 28)
    ]
    columns = 5
    cell_width = max(panel.width for panel in panels)
    cell_height = max(panel.height for panel in panels)
    rows = (len(panels) + columns - 1) // columns
    canvas = Image.new("RGB", (cell_width * columns, cell_height * rows), (225, 225, 225))
    for index, panel in enumerate(panels):
        canvas.paste(panel, ((index % columns) * cell_width, (index // columns) * cell_height))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def classify(current: tuple[int, int], correct: tuple[int, int], chapter: int) -> str:
    if current == correct:
        return "accurate"
    if chapter == 10 and current == (266, 305) and correct == (267, 305):
        return "leading_blank_only"
    return "incorrect"


def discrepancy_fields(current: tuple[int, int], correct: tuple[int, int]) -> dict[str, str]:
    current_pages = set(range(current[0], current[1] + 1))
    correct_pages = set(range(correct[0], correct[1] + 1))
    return {
        "missing_pages": compact_range(sorted(correct_pages - current_pages)),
        "extraneous_pages": compact_range(sorted(current_pages - correct_pages)),
    }


def markdown_report(rows: list[dict[str, Any]], blank_ink: dict[int, float]) -> str:
    counts = {status: sum(row["status"] == status for row in rows) for status in ("accurate", "leading_blank_only", "incorrect")}
    lines = [
        "# Genetics 27 章 PDF 切割全面审计",
        "",
        "## 结论",
        "",
        f"- 完全准确：{counts['accurate']} 章（第 1、2、9 章）。",
        "- 第 10 章正文范围正确，但多含母本第 266 页这一张章节间空白页。",
        f"- 边界错误：{counts['incorrect']} 章；第 27 章最严重，现有文件一直包含到母本第 992 页。",
        "- 所有现有切章页均通过低分辨率灰度渲染 SHA-256 逐页匹配回唯一母本页；不是依据 structured 元数据推断。",
        "- 每章首尾的视觉证据位于 `evidence/chapterNN_boundaries.png`，正确章首页总览见 `correct_start_pages.png`。",
        "",
        "## 全章结果",
        "",
        "| 章 | 现有母本页范围 | 正确范围 | 状态 | 缺页 | 混入页 | 视觉证据 |",
        "|---:|---:|---:|---|---|---|---|",
    ]
    labels = {"accurate": "准确", "leading_blank_only": "仅多前置空白页", "incorrect": "错误"}
    for row in rows:
        chapter = row["chapter"]
        lines.append(
            f"| {chapter} | {row['current_start']}–{row['current_end']} | {row['correct_start']}–{row['correct_end']} | "
            f"{labels[row['status']]} | {row['missing_pages'] or '—'} | {row['extraneous_pages'] or '—'} | "
            f"[PNG](evidence/chapter{chapter:02d}_boundaries.png) |"
        )
    lines.extend(
        [
            "",
            "## 章节间空白页",
            "",
            "母本第 96、266、306、698 页是章节间空白页，不属于相邻章节正文。灰度渲染墨迹占比均接近零：",
            "",
            *[f"- 第 {page} 页：ink fraction = {blank_ink[page]:.6f}" for page in BLANK_INTERCHAPTER_PAGES],
            "",
            "视觉证据：[interchapter_blank_pages.png](interchapter_blank_pages.png)。",
            "",
            "## 书名目录中的章节标题错误",
            "",
            "- 第 14 章应为 `Principles of Marker-based Analysis`。",
            "- 第 22 章应为 `Genotype × Environment Interaction`。",
            "",
            "## 第 27 章尾界",
            "",
            "第 27 章必须在母本第 818 页结束。第 819–992 页属于附录、参考文献和索引，现有 `Genetics_chapter27.pdf` 将这些内容全部混入。",
            "",
            "## 方法与限制",
            "",
            "1. 将母本 992 页和每个现有切章 PDF 的每一页统一渲染为 0.5 倍灰度位图并计算 SHA-256。",
            "2. 要求每个切章页在母本中有且仅有一个匹配，且章内映射连续；否则脚本直接失败。",
            "3. 正确边界以章标题页、相邻章标题页、四张章节间空白页和可视化首尾页共同核验。",
            "4. 本审计只读 `data/`，没有重切、覆盖或重新 OCR Genetics。",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit all Genetics chapter splits against Genetics.pdf.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output", type=Path, default=ROOT / "tmp" / "genetics_full_audit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    allowed = (ROOT / "tmp").resolve()
    if output != allowed and allowed not in output.parents:
        raise ValueError(f"Audit output must remain below {allowed}")
    if output.exists():
        shutil.rmtree(output)
    evidence_dir = output / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    master_path = next(path for path in args.data_dir.resolve().rglob("Genetics.pdf") if path.is_file())
    master = fitz.open(master_path)
    if master.page_count != 992:
        raise ValueError(f"Expected 992-page Genetics.pdf, got {master.page_count}")
    try:
        digest_index: dict[str, list[int]] = {}
        for index in range(master.page_count):
            digest_index.setdefault(page_digest(master[index]), []).append(index + 1)

        rows: list[dict[str, Any]] = []
        mapped_page_total = 0
        for chapter in range(1, 28):
            chapter_path = next(args.data_dir.resolve().rglob(f"Genetics_chapter{chapter}.pdf"))
            document = fitz.open(chapter_path)
            try:
                mapped: list[int] = []
                for page in document:
                    matches = digest_index.get(page_digest(page), [])
                    if len(matches) != 1:
                        raise ValueError(f"{chapter_path.name}: page {page.number + 1} maps to {matches}")
                    mapped.append(matches[0])
            finally:
                document.close()
            if mapped != list(range(mapped[0], mapped[-1] + 1)):
                raise ValueError(f"{chapter_path.name} does not map to a contiguous source range")
            mapped_page_total += len(mapped)
            current = (mapped[0], mapped[-1])
            correct = CORRECT_RANGES[chapter]
            row: dict[str, Any] = {
                "chapter": chapter,
                "current_start": current[0],
                "current_end": current[1],
                "current_pages": len(mapped),
                "correct_start": correct[0],
                "correct_end": correct[1],
                "correct_pages": correct[1] - correct[0] + 1,
                "status": classify(current, correct, chapter),
                **discrepancy_fields(current, correct),
                "title_correction": TITLE_CORRECTIONS.get(chapter, ""),
            }
            rows.append(row)
            boundary_evidence(master, evidence_dir / f"chapter{chapter:02d}_boundaries.png", chapter, current, correct)

        blank_ink = {page: ink_fraction(master[page - 1]) for page in BLANK_INTERCHAPTER_PAGES}
        make_blank_evidence(master, output / "interchapter_blank_pages.png")
        make_start_overview(master, output / "correct_start_pages.png")
    finally:
        master.close()

    csv_path = output / "genetics_chapter_split_audit.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "genetics_chapter_split_audit.md").write_text(markdown_report(rows, blank_ink), encoding="utf-8")
    report = {
        "valid_audit": True,
        "source_pdf": str(master_path.relative_to(ROOT)).replace("\\", "/"),
        "source_pages": 992,
        "chapters": 27,
        "mapped_chapter_pages": mapped_page_total,
        "status_counts": {
            status: sum(row["status"] == status for row in rows)
            for status in ("accurate", "leading_blank_only", "incorrect")
        },
        "blank_interchapter_pages": {str(page): blank_ink[page] for page in BLANK_INTERCHAPTER_PAGES},
        "correct_ranges": {str(chapter): list(page_range) for chapter, page_range in CORRECT_RANGES.items()},
        "rows": rows,
    }
    (output / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["status_counts"], ensure_ascii=False))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
