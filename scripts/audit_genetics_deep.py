"""Write a repeatable integrity audit for the logical Genetics textbook set."""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
TEXTBOOK = ROOT / "data" / "textbook"
FIGURES = ROOT / "data" / "figure_library.json"
OUT = ROOT / "tmp" / "genetics_accuracy_audit"

FIGURE_RE = re.compile(r"\[\[FIGURE:([^\]]+)\]\]")
MARKDOWN_FIGURE_RE = re.compile(r"!\[Figure [^\]]+\]\((figures/[^)]+)\)")
DIRECT_PLACEHOLDER_RE = re.compile(r"\[\[(?:FIGURE|FORMULA|TABLE|EXAMPLE):[^\]]+\]\]")
CORRUPT_MARKERS = (
    "_ 3 &=",
    "_ G (x,y)=",
    "(y,z_ i)&=",
    "z_ o &=",
    "(g_ f =1",
    "(.qq |",
    "(qq g_ f",
    "(z_ i)&=",
    "& (z_ i",
    "_ M_ 1 -",
    "^ 2 (_ 1i)",
    "(G_ Mx,G_ My)",
    "(G_ Fx,G_ Fy)",
    "E(f) f(_ x_ 1",
    "^ 2 (u/v)",
    "_ &= ^ T ^ -1/2",
    "(Q_ k m,z,c)",
    "n&= (8(1-r^ 2)",
    "F&= _ t",
)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def chapter_number(value: str) -> int:
    match = re.search(r"chapter(\d+)", value, re.I)
    return int(match.group(1)) if match else 9999


def issue(issues: list[dict[str, str]], kind: str, severity: str, location: str, evidence: str, fix: str) -> None:
    issues.append(
        {
            "type": kind,
            "severity": severity,
            "location": location,
            "pdf_page": "",
            "evidence": evidence,
            "recommended_fix": fix,
        }
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    evidence_dir = OUT / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    # Preserve the source-PDF visual checks alongside the machine-readable
    # report, without treating terminal rendering as evidence of encoding.
    existing_evidence = ROOT / "tmp" / "genetics_deep_audit"
    for relative in (
        "evidence/chapter27_page6.png",
        "evidence/chapter27_page66.png",
        "boundary_evidence/c14_p55.png",
        "boundary_evidence/c19_p19.png",
        "boundary_evidence/c22_p2.png",
    ):
        source = existing_evidence / relative
        if source.exists():
            shutil.copy2(source, evidence_dir / source.name)
    issues: list[dict[str, str]] = []
    chunks_by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    units: dict[str, dict[str, Any]] = {}

    paths = sorted(STRUCTURED.glob("Genetics_chapter*_*.json"), key=lambda p: (chapter_number(p.name), p.name))
    for path in paths:
        data = read(path)
        unit_id = str(data.get("id") or "")
        chapter = str((data.get("metadata") or {}).get("chapter") or "")
        units[unit_id] = data
        chunks_by_chapter[chapter].append(data)
        expected_filename = f"{unit_id}.json"
        if path.name != expected_filename or not chapter or not unit_id.startswith(f"{chapter}_"):
            issue(issues, "chunk_identity", "critical", path.name, "Chunk id/metadata/file name disagree.", "Regenerate logical chapter chunk ids.")
        if not (data.get("metadata") or {}).get("logical_chapter_repartition"):
            issue(issues, "logical_boundary", "major", unit_id, "Missing printed-boundary provenance.", "Repartition from verified source PDF boundaries.")
        for index, block in enumerate(data.get("blocks") or []):
            content = str(block.get("content") or "")
            if "\ufffd" in content:
                issue(issues, "encoding", "critical", f"{unit_id}:block{index}", "Contains U+FFFD replacement character.", "Restore UTF-8 source text.")
            for marker in CORRUPT_MARKERS:
                if marker in content:
                    issue(issues, "formula_ocr", "critical", f"{unit_id}:block{index}", f"Damaged-formula marker: {marker}", "Restore from formula library/PDF.")

    for number in range(1, 28):
        chapter = f"Genetics_chapter{number}"
        chunks = chunks_by_chapter.get(chapter, [])
        if not chunks:
            issue(issues, "coverage", "critical", chapter, "No logical structured chunks.", "Rebuild the chapter.")
            continue
        ids = [str(chunk.get("id") or "") for chunk in chunks]
        expected = [f"{chapter}_{index:03d}" for index in range(1, len(chunks) + 1)]
        if ids != expected:
            issue(issues, "chunk_sequence", "critical", chapter, "Chunk ids are not contiguous.", "Reindex logical chapter chunks.")

    formula_records = [f for f in read(STRUCTURED / "formula_library.json").get("formulas", []) if str(f.get("id") or "").startswith("Genetics_")]
    for formula in formula_records:
        source = formula.get("source") if isinstance(formula.get("source"), dict) else {}
        unit_id = str(source.get("unit_id") or "")
        chapter = str(source.get("chapter") or "")
        if unit_id not in units or not unit_id.startswith(f"{chapter}_"):
            issue(issues, "formula_provenance", "major", str(formula.get("id") or ""), "Formula source unit is absent or chapter-mismatched.", "Relink formula source to its logical chunk.")

    table_records = [t for t in read(STRUCTURED / "table_library.json").get("tables", []) if str((t.get("source") or {}).get("chapter") or "").startswith("Genetics_")]
    for table in table_records:
        source = table.get("source") if isinstance(table.get("source"), dict) else {}
        unit_id = str(source.get("unit_id") or "")
        if unit_id not in units:
            issue(issues, "table_provenance", "major", str(table.get("id") or ""), "Table source unit is absent.", "Relink table source to its logical chunk.")

    figures = read(FIGURES).get("figures", {})
    if not isinstance(figures, dict):
        raise TypeError("Figure library must be a dictionary")
    figure_records = [f for f in figures.values() if isinstance(f, dict) and str(f.get("chapter") or "").startswith("Genetics_")]
    owners: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for figure in figure_records:
        chapter = str(figure.get("chapter") or "")
        figure_id = str(figure.get("id") or "")
        owners[(chapter, figure_id)].append(figure)
        asset = TEXTBOOK / str(figure.get("asset_path") or "")
        if not asset.exists() or asset.stat().st_size == 0:
            issue(issues, "figure_asset", "critical", f"{chapter}:Figure {figure_id}", "Referenced source crop is missing/empty.", "Re-crop from source PDF.")
        if not asset.name.startswith("Genetics_"):
            issue(issues, "figure_asset_owner", "critical", f"{chapter}:Figure {figure_id}", f"Asset is not a Genetics asset: {asset.name}", "Relink chapter-local figure record.")
    for (chapter, figure_id), matches in owners.items():
        if len(matches) != 1:
            issue(issues, "figure_collision", "critical", f"{chapter}:Figure {figure_id}", "More than one chapter-local figure record.", "Deduplicate by book and chapter.")

    structured_figures: dict[str, set[str]] = defaultdict(set)
    for unit in units.values():
        chapter = str((unit.get("metadata") or {}).get("chapter") or "")
        for block in unit.get("blocks") or []:
            structured_figures[chapter].update(FIGURE_RE.findall(str(block.get("content") or "")))
    library_figures = {chapter: {figure_id for (owner, figure_id) in owners if owner == chapter} for chapter in chunks_by_chapter}
    for chapter in chunks_by_chapter:
        if structured_figures[chapter] != library_figures.get(chapter, set()):
            issue(issues, "figure_anchors", "critical", chapter, "Structured figure anchors do not exactly match chapter-local figure library.", "Add/relink explicit figure anchors.")

    markdown_figure_cards = 0
    block_type_counts: Counter[str] = Counter()
    markdown_type_counts: Counter[str] = Counter()
    for chapter, chunks in chunks_by_chapter.items():
        markdown_path = TEXTBOOK / f"{chapter}_textbook.md"
        if not markdown_path.exists():
            issue(issues, "textbook_coverage", "critical", chapter, "Textbook Markdown missing.", "Export this logical chapter.")
            continue
        markdown = markdown_path.read_text(encoding="utf-8")
        if "\ufffd" in markdown:
            issue(issues, "encoding", "critical", markdown_path.name, "Contains U+FFFD replacement character.", "Restore UTF-8 source text.")
        if DIRECT_PLACEHOLDER_RE.search(markdown):
            issue(issues, "unexpanded_placeholder", "major", markdown_path.name, "Contains unresolved direct content placeholder.", "Re-export after relinking libraries.")
        expected_ids = {str(chunk.get("id") or "") for chunk in chunks}
        rendered_ids = set(re.findall(r"^## (Genetics_chapter\d+_\d+)", markdown, flags=re.MULTILINE))
        if rendered_ids != expected_ids:
            issue(issues, "textbook_chunks", "critical", chapter, "Markdown chunk headings do not match structured chunks.", "Re-export textbook chapter.")
        cards = MARKDOWN_FIGURE_RE.findall(markdown)
        markdown_figure_cards += len(cards)
        if any(not Path(asset).name.startswith("Genetics_") for asset in cards):
            issue(issues, "figure_export", "critical", markdown_path.name, "Markdown emits a non-Genetics figure asset.", "Repair figure-library ownership and export.")
        if len(cards) != len(structured_figures.get(chapter, set())):
            issue(issues, "figure_export", "critical", markdown_path.name, "Figure-card count differs from structured anchors.", "Re-export with chapter-local figure map.")
        for table in table_records:
            source = table.get("source") if isinstance(table.get("source"), dict) else {}
            if source.get("chapter") != chapter:
                continue
            table_id = re.escape(str(table.get("id") or ""))
            marker = re.compile(rf"^>\s+\*\*Table\s+{table_id}\*\*", re.MULTILINE)
            match = marker.search(markdown)
            if not match:
                issue(issues, "table_export", "critical", markdown_path.name, f"Table {table.get('id')} is missing from Markdown.", "Re-export/relink table.")
                continue
            next_markers = [
                position
                for position in (
                    markdown.find("\n> **Table ", match.end()),
                    markdown.find("\n> **Unnumbered table**", match.end()),
                    markdown.find("\n## ", match.end()),
                )
                if position >= 0
            ]
            rendered_table_block = markdown[match.start() : min(next_markers) if next_markers else len(markdown)]
            has_html_table = "<table" in rendered_table_block.lower()
            has_markdown_table = bool(
                re.search(r"^>\s*[^\n|]+\|[^\n]+\n>\s*---(?:\s*\|\s*---)+\s*$", rendered_table_block, re.MULTILINE)
            )
            blockquote_lines = rendered_table_block.splitlines()[3:]
            has_textual_table = any(
                line.startswith("> ") and line.strip() != ">"
                for line in blockquote_lines
            )
            if not has_html_table and not has_markdown_table and not has_textual_table:
                issue(
                    issues,
                    "table_export",
                    "critical",
                    markdown_path.name,
                    f"Table {table.get('id')} has no rendered HTML, Markdown, or textual table body.",
                    "Relink the raw table body.",
                )
            rows = table.get("rows") if isinstance(table.get("rows"), list) else []
            probes = [str(cell).strip() for row in rows for cell in (row if isinstance(row, list) else []) if str(cell).strip()]
            if probes and not any(probe in markdown for probe in probes[:3]):
                issue(issues, "table_export", "major", markdown_path.name, f"Table {table.get('id')} has no source-cell probe in Markdown.", "Re-export/relink table.")
        for chunk in chunks:
            for block in chunk.get("blocks") or []:
                block_type = str(block.get("type") or "discussion")
                if block_type != "discussion":
                    block_type_counts[block_type] += 1
                    # The exporter emits a visible type label for every non-discussion block.
                    marker = {
                        "definition": "Definition]**",
                        "derivation": "Derivation]**",
                        "proposition": "Proposition]**",
                        "example": "Example]**",
                    }.get(block_type, f"{block_type.capitalize()}]**")
                    if marker not in markdown:
                        issue(issues, "block_boundary", "major", markdown_path.name, f"Missing rendered {block_type} marker.", "Re-export block boundaries.")
        for kind, marker in (("definition", "Definition]**"), ("derivation", "Derivation]**"), ("proposition", "Proposition]**"), ("example", "Example]**")):
            markdown_type_counts[kind] += markdown.count(marker)

    metrics = {
        "logical_chapters": len(chunks_by_chapter),
        "structured_chunks": len(units),
        "genetics_formula_records": len(formula_records),
        "genetics_table_records": len(table_records),
        "genetics_figure_records": len(figure_records),
        "markdown_figure_cards": markdown_figure_cards,
        "structured_block_types": dict(block_type_counts),
        "markdown_block_type_markers": dict(markdown_type_counts),
        "issues": len(issues),
        "acceptable_table_position_offset": "Tables may be materialized at the end of their owning section.",
        "utf8_check": "UTF-8 decoded; U+FFFD scanned. Terminal glyph rendering was not used as evidence.",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / "issues.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["type", "severity", "location", "pdf_page", "evidence", "recommended_fix"])
        writer.writeheader()
        writer.writerows(issues)

    lines = [
        "# Genetics 结构化解析深度审计",
        "",
        f"- 逻辑章节：{metrics['logical_chapters']} / 27",
        f"- 结构化分块：{metrics['structured_chunks']}",
        f"- 公式库记录：{metrics['genetics_formula_records']}",
        f"- 表格库记录：{metrics['genetics_table_records']}",
        f"- 图记录 / Markdown 图卡：{metrics['genetics_figure_records']} / {metrics['markdown_figure_cards']}",
        f"- 自动完整性问题：{len(issues)}",
        "",
        "## 审计规则",
        "",
        "- 逐章检查 27 个逻辑章节的分块连续性、章节归属与 Markdown 覆盖。",
        "- 图按 `(chapter, figure id)` 解析；图号跨书同名不会共享资产。",
        "- 表格仅检查内容和归属；完整表格沉到所属小节末尾按允许的位置偏移处理。",
        "- UTF-8 以 Unicode 码位检查，未将终端显示差异作为乱码证据。",
        "- 已扫描本轮定位到的公式 OCR 损坏标记及 U+FFFD。",
        "",
        "## 结论",
        "",
        "通过：本轮自动结构、导出、图表资产、公式来源和编码检查未发现遗留问题。"
        if not issues
        else "未通过：请以 issues.csv 中的条目为准。",
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
