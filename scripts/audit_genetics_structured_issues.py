"""Create a read-only diagnosis of the reported Genetics structure issues."""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tmp" / "genetics_full_audit" / "structured_diagnosis"
FIGURE_GLOB = ("Genetics_3.*.png", "Genetics_4.*.png")
EXAMPLE_HEADING_RE = re.compile(r"^\s*Example\s+(?P<number>\d+(?:\.\d+)?)[.:]", re.IGNORECASE | re.MULTILINE)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def weighted_median(values: list[tuple[float, float]]) -> float:
    values = sorted(values)
    total = sum(weight for _, weight in values)
    cursor = 0.0
    for value, weight in values:
        cursor += weight
        if cursor >= total / 2:
            return value
    return 0.0


def estimate_skew(image: np.ndarray) -> tuple[float, int, float]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 50, 160)
    minimum = min(gray.shape)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 1800,
        threshold=max(20, minimum // 24),
        minLineLength=max(35, minimum // 12),
        maxLineGap=18,
    )
    candidates: list[tuple[float, float]] = []
    for x1, y1, x2, y2 in ([] if lines is None else lines.reshape(-1, 4)):
        angle = math.degrees(math.atan2(float(y2 - y1), float(x2 - x1)))
        deviation = ((angle + 45) % 90) - 45
        length = math.hypot(float(x2 - x1), float(y2 - y1))
        if abs(deviation) <= 6:
            candidates.append((deviation, length))
    if not candidates:
        raise ValueError("No near-horizontal or near-vertical line evidence for skew estimation")
    return weighted_median(candidates), len(candidates), sum(weight for _, weight in candidates)


def rotate_expanded(image: np.ndarray, angle: float) -> np.ndarray:
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    new_width = int(abs(matrix[0, 0]) * width + abs(matrix[0, 1]) * height)
    new_height = int(abs(matrix[0, 1]) * width + abs(matrix[0, 0]) * height)
    matrix[0, 2] += new_width / 2 - center[0]
    matrix[1, 2] += new_height / 2 - center[1]
    return cv2.warpAffine(
        image,
        matrix,
        (new_width, new_height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def panel(path: Path, label: str, width: int = 380, height: int = 300) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail((width - 16, height - 42))
    result = Image.new("RGB", (width, height), "white")
    result.paste(image, ((width - image.width) // 2, 34 + (height - 42 - image.height) // 2))
    ImageDraw.Draw(result).text((8, 8), label, fill="black")
    return result


def deskew_probe() -> list[dict[str, Any]]:
    deskew_dir = OUTPUT / "deskew"
    deskew_dir.mkdir(parents=True, exist_ok=True)
    source_paths = sorted(
        {path for pattern in FIGURE_GLOB for path in (ROOT / "data" / "figures").glob(pattern)},
        key=lambda path: [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name)],
    )
    rows: list[dict[str, Any]] = []
    contact_panels: list[Image.Image] = []
    for source in source_paths:
        image = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Could not read {source}")
        before, segments, line_weight = estimate_skew(image)
        corrected = rotate_expanded(image, before)
        target = deskew_dir / source.name
        encoded, buffer = cv2.imencode(target.suffix, corrected)
        if not encoded:
            raise ValueError(f"Could not encode {target}")
        buffer.tofile(target)
        after, after_segments, _ = estimate_skew(corrected)
        rows.append(
            {
                "figure": source.name,
                "estimated_skew_degrees": round(before, 3),
                "correction_degrees": round(before, 3),
                "residual_degrees": round(after, 3),
                "supporting_segments": segments,
                "line_weight": round(line_weight, 1),
                "source": str(source.relative_to(ROOT)).replace("\\", "/"),
                "probe_copy": str(target.relative_to(ROOT)).replace("\\", "/"),
                "formal_asset_replaced": False,
            }
        )
        contact_panels.extend(
            [
                panel(source, f"BEFORE · {source.name} · {before:+.2f}°"),
                panel(target, f"DESKEW PROBE · residual {after:+.2f}°"),
            ]
        )

    columns = 4
    cell_width, cell_height = contact_panels[0].size
    contact = Image.new(
        "RGB",
        (columns * cell_width, ((len(contact_panels) + columns - 1) // columns) * cell_height),
        (225, 225, 225),
    )
    for index, item in enumerate(contact_panels):
        contact.paste(item, ((index % columns) * cell_width, (index // columns) * cell_height))
    contact.save(OUTPUT / "deskew_comparison.png")
    with (OUTPUT / "deskew_angles.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def example_evidence() -> dict[str, Any]:
    occurrences: list[dict[str, Any]] = []
    for chapter in range(1, 28):
        page_dir = ROOT / "data" / "paddle_output" / f"Genetics_chapter{chapter}_full" / "ocr_raw" / "markdown_pages"
        for path in sorted(page_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            occurrences.extend(
                {
                    "ocr_chapter": chapter,
                    "page_file": path.name,
                    "local_number": match.group("number"),
                    "heading": match.group(0).strip(),
                }
                for match in EXAMPLE_HEADING_RE.finditer(text)
            )
    library = read_json(ROOT / "data" / "structured" / "example_library.json")
    examples = library.get("examples", []) if isinstance(library, dict) else library
    genetics_library = [item for item in examples if str(item.get("chapter") or "").startswith("Genetics")]
    block_types: dict[str, int] = {}
    for path in (ROOT / "data" / "structured").glob("Genetics_chapter*_*.json"):
        for block in read_json(path).get("blocks", []):
            kind = str(block.get("type") or "")
            block_types[kind] = block_types.get(kind, 0) + 1
    return {
        "raw_example_heading_occurrences": len(occurrences),
        "raw_unique_ocr_chapter_and_number": len({(row["ocr_chapter"], row["local_number"]) for row in occurrences}),
        "shared_library_total": len(examples),
        "shared_library_genetics": len(genetics_library),
        "structured_block_types": block_types,
        "sample_raw_headings": occurrences[:20],
    }


def style_evidence() -> dict[str, Any]:
    master = fitz.open(next((ROOT / "data").rglob("Genetics.pdf")))
    try:
        sampled_pages = (21, 51, 67, 819, 900)
        pdf_spans = {
            str(page_number): sum(
                len(line.get("spans", []))
                for block in master[page_number - 1].get_text("dict").get("blocks", [])
                for line in block.get("lines", [])
            )
            for page_number in sampled_pages
        }
    finally:
        master.close()
    raw_files = list((ROOT / "data" / "paddle_output").glob("Genetics_chapter*_full/ocr_raw/markdown_pages/*.md"))
    raw_text = "\n".join(path.read_text(encoding="utf-8") for path in raw_files)
    return {
        "sampled_pdf_text_spans": pdf_spans,
        "raw_markdown_files": len(raw_files),
        "raw_markdown_bold_spans": len(re.findall(r"\*\*[^*\n]+\*\*", raw_text)),
        "raw_html_bold_tags": len(re.findall(r"<(?:b|strong)\b", raw_text, flags=re.IGNORECASE)),
        "raw_html_italic_tags": len(re.findall(r"<(?:i|em)\b", raw_text, flags=re.IGNORECASE)),
        "latex_style_commands_in_available_ocr": {
            "textbf": len(re.findall(r"\\textbf\{", raw_text)),
            "textit": len(re.findall(r"\\textit\{", raw_text)),
            "emph": len(re.findall(r"\\emph\{", raw_text)),
        },
        "style_stripping_code": [
            "knowledge_engineering/pipeline/process.py:245",
            "knowledge_engineering/pipeline/process.py:1894",
        ],
    }


def paragraph_evidence() -> dict[str, Any]:
    raw_path = ROOT / "data" / "paddle_output" / "Genetics_chapter2_full" / "ocr_raw" / "markdown_pages" / "page_0013.md"
    raw_lines = raw_path.read_text(encoding="utf-8").splitlines()
    normalized = read_json(
        ROOT / "data" / "paddle_output" / "Genetics_chapter2_full" / "normalized" / "normalized_blocks.json"
    )
    first = next(index for index, block in enumerate(normalized) if str(block.get("text") or "").startswith("Estimates such"))
    second = next(
        index for index, block in enumerate(normalized)
        if str(block.get("text") or "").startswith("As an example, consider an estimate")
    )
    unit = read_json(ROOT / "data" / "structured" / "Genetics_chapter2_005.json")
    merged = str(unit["blocks"][0]["content"])
    chapter4_unit = read_json(ROOT / "data" / "structured" / "Genetics_chapter4_001.json")
    chapter4_content = str(chapter4_unit["blocks"][0]["content"])
    return {
        "chapter2_raw": {
            "path": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
            "first_paragraph_line": 7,
            "blank_separator_line": 8,
            "second_paragraph_line": 9,
            "line7_prefix": raw_lines[6][:120],
            "line9_prefix": raw_lines[8][:120],
        },
        "chapter2_normalized_separate_blocks": [first, second],
        "chapter2_structured": {
            "unit": "Genetics_chapter2_005",
            "first_block_contains_both": "Estimates such" in merged and "As an example" in merged,
            "first_block_newline_count": merged.count("\n"),
        },
        "chapter4_page_break": {
            "raw_first_half": "data/paddle_output/Genetics_chapter3_full/ocr_raw/markdown_pages/page_0016.md:11",
            "raw_second_half": "data/paddle_output/Genetics_chapter3_full/ocr_raw/markdown_pages/page_0017.md:1",
            "structured_unit": "Genetics_chapter4_001",
            "has_false_paragraph_break": "Organisms\n\nwith ploidy" in chapter4_content,
            "textbook_lines": [11, 13],
        },
    }


def table_evidence() -> dict[str, Any]:
    unit = read_json(ROOT / "data" / "structured" / "Genetics_chapter2_002.json")
    footnote = next(
        (index, block)
        for index, block in enumerate(unit.get("blocks", []))
        if str(block.get("content") or "").lstrip().startswith("* Each number in the main body")
    )
    library = read_json(ROOT / "data" / "structured" / "Genetics_table_library.json")
    table = next(item for item in library["tables"] if item.get("id") == "2.1")
    return {
        "footnote_unit": "Genetics_chapter2_002",
        "footnote_block_index": footnote[0],
        "footnote_block_type": footnote[1].get("type"),
        "footnote_text": footnote[1].get("content"),
        "table_has_rows": bool(table.get("rows")),
        "table_has_markdown_body": bool(table.get("markdown_body")),
        "textbook_rendered_as_ordinary_text_line": 17,
        "exporter_rows_early_returns": [767, 773],
        "exporter_markdown_body_append": 778,
    }


def report(evidence: dict[str, Any]) -> str:
    skew_rows = evidence["deskew"]
    absolute = [abs(row["estimated_skew_degrees"]) for row in skew_rows]
    residual = [abs(row["residual_degrees"]) for row in skew_rows]
    examples = evidence["examples"]
    styles = evidence["styles"]
    paragraphs = evidence["paragraphs"]
    table = evidence["table_2_1"]
    return f"""# Genetics 结构化问题深度诊断（只读）

## 总结

这 7 类现象不是同一个错误：切章偏移首先污染了第 3/4 章输入；其后 Genetics 专用 LaTeX 重建又把示例类型、段落边界和空标题节点压平；字体样式则在 OCR 阶段已基本丢失；表注渲染还有 exporter 的第二层缺陷。本报告没有修改任何 Genetics structured、textbook、figure 或 PDF。

## 1. Table 2.1 的星号表注

- `data/structured/Genetics_chapter2_002.json` 的第 {table['footnote_block_index']} 个 block 把表注保存成 `{table['footnote_block_type']}`；教材因此在第 17 行把它当普通正文输出。
- `Genetics_table_library.json` 的 Table 2.1 有规范 rows，但 `markdown_body` 为空。正确归属应是表格脚注，而不是相邻 discussion。
- 还有第二层问题：即便未来把表注迁入 `markdown_body`，`textbook_exporter/exporter.py:756-773` 的规范 rows 分支会在 767/773 提前 return，走不到 778 的 `append_table_markdown_body`，表注仍会消失。
- 建议：给表增加 `notes: [{{marker: "*", kind: "footnote", content: ...}}]`（或补全 `markdown_body`），从 discussion 删除该块；exporter 对 rows、HTML 两条路径都统一在表体后渲染 notes，并加入 Table 2.1 回归测试。

## 2. Examples 全部没有进入 libraries

- 972 个 Paddle Markdown 页中检测到 {examples['raw_example_heading_occurrences']} 次行首 Example 标题（按 OCR 章号+局部编号去重为 {examples['raw_unique_ocr_chapter_and_number']}）；共享库共 {examples['shared_library_total']} 条，但 Genetics 条目为 {examples['shared_library_genetics']}。
- Genetics structured 的 block 类型为 `{json.dumps(examples['structured_block_types'], ensure_ascii=False)}`，没有 `example` block。
- 根因明确：`scripts/rebuild_genetics_structured_from_tex.py:134` 无条件写 `{{"type": "discussion"}}`，而这条 Genetics 专用重建路径没有执行正式 example pipeline。原 OCR 内容并未缺失 Examples。
- 建议：先按正确页界重切/重 OCR，再运行现有 example pipeline；本书使用章内局部编号（`Example 1.`），必须用逻辑章号限定引用，并验证跨页正文、图、表和公式的 span 归属。

## 3. 段落边界既有合并，也有错误断开

- `Genetics_chapter2_005`：原始 `page_0013.md` 第 7、9 行是两个段落，第 8 行为空；normalized blocks {paragraphs['chapter2_normalized_separate_blocks']} 也仍是两个独立块。但 structured 第一个 block 同时包含两段，且换行数为 {paragraphs['chapter2_structured']['first_block_newline_count']}。因此边界是在后续 Genetics 重建/重分区中压平的，不是 Paddle 原始识别失败。
- `Genetics_chapter4_001` 教材第 11/13 行是相反问题：`Organisms` 位于旧 chapter3 OCR 的 `page_0016.md:11`，`with ploidy...` 位于下一页 `page_0017.md:1`，当前输出把一个跨页句子拆成两个段落。
- 建议：structured 中保留 `source_page/source_block/source_line/paragraph_id`；同页空行保持分段；跨页仅在“上一块无句末标点 + 下一块小写开头”等高置信条件下连接，并留下 `joined_across_page` provenance。

## 4. 黑体与斜体能否补加

- 能，但不能从当前 structured 无损恢复。抽查母本页 21/51/67/819/900 的 PDF text span 全为 0：`{styles['sampled_pdf_text_spans']}`，说明这是纯扫描图，没有字体元数据。
- Paddle 原始 Markdown 共 {styles['raw_markdown_files']} 页，只出现 {styles['raw_markdown_bold_spans']} 个 Markdown bold、{styles['raw_html_bold_tags']} 个 HTML bold、{styles['raw_html_italic_tags']} 个 HTML italic；当前 OCR 几乎没有提供样式信号。
- 通用解析器还会主动抹平样式：`knowledge_engineering/pipeline/process.py:245` 匹配 `textbf/textit/emph`，`:1894` 在表格单元中直接去掉这些命令。
- 可行方案：重新基于页面图像和 OCR bbox 做 token/span 级视觉样式分类，输出 `spans:[{{text, bold, italic, confidence}}]`；subject index 只作为黑体术语候选词典，再回到页面图像确认。物种名/变量等斜体可用语义规则辅助，但不能替代视觉证据。随后修改 parser/exporter 保留 `<strong>/<em>` 或等价语义标记。

## 5. 第 3/4 章 figure 倾斜与 deskew

- 两章 manifest 均明确设置 `useDocOrientationClassify=false`、`useDocUnwarping=false`，OCR 时没有方向分类或去畸变。
- 12 幅正式图的近水平/近垂直长线加权中位角绝对值范围为 {min(absolute):.3f}°–{max(absolute):.3f}°，中位数 {float(np.median(absolute)):.3f}°；说明倾斜是系统性的，不只是主观观感。
- 已在 `tmp/.../structured_diagnosis/deskew/` 生成 OpenCV 扩边旋转副本，正式图未替换。残余绝对角最大值 {max(residual):.3f}°；对照见 `deskew_comparison.png`，逐图数据见 `deskew_angles.csv`。
- 方案可行。正式修复时应按图单独估角、扩白边避免裁损，并设置信心阈值；图内本来就有斜线，所以只使用接近水平/垂直的长线，不用全部 Hough 线。

## 6. 无正文的大节标题

- `THE TRANSMISSION OF GENETIC INFORMATION` 下没有父级引言，直接进入 `The Hardy-Weinberg Principle`，这是合法目录结构。
- `scripts/rebuild_genetics_structured_from_tex.py:69-76` 只在 content/preamble 非空时创建 unit；`textbook_exporter/exporter.py:205-224` 又会跳过没有可渲染 block 的 chunk。因此当前 schema 无法表达 heading-only 节点。
- 建议新增显式 `node_kind: "heading"`, `blocks: []`, `allow_empty: true`；exporter 先输出标题再判断正文。这样保留父子目录对应，不伪造一个空字符串正文或“Introduction”段落。

## 7. `Genetics_chapter4_004 · Introduction` 并不存在

- 全章页界审计表明真正第 4 章是母本 67–95 页；现有 `Genetics_chapter4.pdf` 却是 71–100 页。正确首页 67–70 被错误塞在旧 chapter3 中。
- 当前 chapter4 OCR 的 `page_0000.md` 从 Figure 4.1 和残句 `which is just` 开始，没有章标题/大节标题。重建/重分区只能落入默认 `Introduction`，形成 `Genetics_chapter4_004`。
- 这也解释了它为何以 `[[FIGURE:4.1]] which is just ...` 开头：不是教材真实 section，而是从图 4.1 中段开切造成的人工边界。
- 未来正确重切 67–95 后，该内容应归入 `THE TRANSMISSION OF GENETIC INFORMATION / The Hardy-Weinberg Principle`；本轮按要求不实施修复。

## 推荐修复顺序（下一轮）

1. 先按审计页界重切 27 章，至少先重做第 3/4 章；旧 structured 上直接修补会继续保留错章污染。
2. OCR 时开启方向分类/去畸变评估，并保留 token/span bbox 与视觉样式。
3. 用段落级而非整节级重建，运行 example pipeline。
4. 引入 heading-only 与 table notes schema，再修 exporter。
5. 对 examples、Table 2.1、跨页段落、空父标题、图 deskew 和第 4 章目录做回归验证。
"""


def main() -> int:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evidence = {
        "read_only": True,
        "table_2_1": table_evidence(),
        "examples": example_evidence(),
        "paragraphs": paragraph_evidence(),
        "styles": style_evidence(),
        "deskew": deskew_probe(),
        "empty_parent_heading": {
            "parent": "THE TRANSMISSION OF GENETIC INFORMATION",
            "first_child": "The Hardy-Weinberg Principle",
            "parent_has_introductory_prose": False,
            "rebuild_skips_empty_preamble": "scripts/rebuild_genetics_structured_from_tex.py:74-76",
            "exporter_skips_empty_chunks": "textbook_exporter/exporter.py:205-224",
        },
        "false_introduction": {
            "unit": "Genetics_chapter4_004",
            "current_source_range": [71, 100],
            "correct_source_range": [67, 95],
            "raw_page_0_starts_with_figure": True,
            "raw_page_0_residual_text": "which is just",
        },
    }
    write_json(OUTPUT / "evidence.json", evidence)
    (OUTPUT / "report.md").write_text(report(evidence), encoding="utf-8")
    print(OUTPUT)
    print(f"deskewed_probe_copies={len(evidence['deskew'])} genetics_examples={evidence['examples']['shared_library_genetics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
