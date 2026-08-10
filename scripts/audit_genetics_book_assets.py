"""Audit Genetics' book-scoped asset libraries against PaddleOCR Cloud evidence."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import fitz

from build_book_asset_libraries import genetics_api_formulas, genetics_api_tables


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
TEXTBOOK = ROOT / "data" / "textbook"
OUT = ROOT / "tmp" / "genetics_accuracy_audit"
TAG_RE = re.compile(r"\\tag\{([^}]+)\}")


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def issue(rows: list[dict[str, str]], kind: str, severity: str, location: str, evidence: str, repair: str) -> None:
    rows.append(
        {
            "type": kind,
            "severity": severity,
            "location": location,
            "pdf_page": "",
            "evidence": evidence,
            "recommended_fix": repair,
        }
    )


def formula_numbers(records: list[dict[str, Any]]) -> set[str]:
    values = {str(record["equation_number"]) for record in records if record.get("equation_number")}
    for record in records:
        for part in record.get("render_parts") if isinstance(record.get("render_parts"), list) else []:
            if isinstance(part, dict) and part.get("equation_number"):
                values.add(str(part["equation_number"]))
    return values


def render_formula_page_evidence() -> int:
    evidence = OUT / "evidence" / "formula_pages"
    evidence.mkdir(parents=True, exist_ok=True)
    saved = 0
    for chapter in range(1, 28):
        entries = genetics_api_formulas(chapter)
        target = next((entry for entry in entries if entry.get("equation_numbers")), None)
        if not target:
            continue
        pdf = next((ROOT / "data").rglob(f"Genetics_chapter{chapter}.pdf"))
        if pdf is None:
            continue
        document = fitz.open(pdf)
        page = document[int(target["page"]) - 1]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pixmap.save(evidence / f"Genetics_chapter{chapter}_page{target['page']}.png")
        document.close()
        saved += 1
    return saved


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    issues: list[dict[str, str]] = []
    formula_library = read(STRUCTURED / "Genetics_formula_library.json")
    table_library = read(STRUCTURED / "Genetics_table_library.json")
    figure_library = read(STRUCTURED / "Genetics_figure_library.json")
    formulas = formula_library.get("formulas", [])
    tables = table_library.get("tables", [])
    figures = figure_library.get("figures", [])

    if len(formulas) != 1815:
        issue(issues, "formula_count", "critical", "Genetics_formula_library.json", f"Expected 1815 records; found {len(formulas)}.", "Rebuild book library.")
    if len(tables) != 72:
        issue(issues, "table_count", "critical", "Genetics_table_library.json", f"Expected 72 records; found {len(tables)}.", "Rebuild table library.")
    if len(figures) != 152:
        issue(issues, "figure_count", "critical", "Genetics_figure_library.json", f"Expected 152 records; found {len(figures)}.", "Rebuild figure library.")
    for library_name, records in (("formula", formulas), ("table", tables), ("figure", figures)):
        for record in records:
            if str(record.get("book") or "") != "Genetics":
                issue(issues, "book_isolation", "critical", library_name, "Non-Genetics record found in dedicated library.", "Rebuild book libraries.")

    api_numbers: set[str] = set()
    api_number_pages: dict[str, tuple[int, int]] = {}
    for chapter in range(1, 28):
        for entry in genetics_api_formulas(chapter):
            for number in entry.get("equation_numbers") or []:
                if number in api_numbers:
                    issue(issues, "formula_number_duplicate_pdf", "critical", number, "Duplicate PaddleOCR API formula-number label.", "Review source-page mapping.")
                api_numbers.add(number)
                api_number_pages[number] = (chapter, int(entry["page"]))
    library_numbers = formula_numbers(formulas)
    if library_numbers != api_numbers:
        for number in sorted(api_numbers - library_numbers):
            issue(issues, "formula_number_missing_library", "critical", number, "API label absent from formula library.", "Restore formula number from API response.")
        for number in sorted(library_numbers - api_numbers):
            issue(issues, "formula_number_extra_library", "critical", number, "Library label absent from API response.", "Remove incorrect inferred label.")

    rendered_numbers: list[str] = []
    for number in range(1, 28):
        path = TEXTBOOK / f"Genetics_chapter{number}_textbook.md"
        if not path.exists():
            issue(issues, "textbook_coverage", "critical", path.name, "Textbook Markdown missing.", "Re-export Genetics.")
            continue
        content = path.read_text(encoding="utf-8")
        rendered_numbers.extend(TAG_RE.findall(content))
        if "[Table data not available]" in content:
            issue(issues, "table_export", "critical", path.name, "A table fallback was rendered.", "Restore API table body and re-export.")
        if "figures/Evolution_" in content or "Formula (Genetics_chapter" in content:
            issue(issues, "cross_book_or_internal_label", "critical", path.name, "Cross-book asset or internal formula ID is visible.", "Use book-scoped renderer maps.")
        if re.search(r"\[\[(?:FORMULA|TABLE|FIGURE):", content):
            issue(issues, "unexpanded_placeholder", "critical", path.name, "Direct asset placeholder remains.", "Re-export after resolving assets.")
    rendered_set = set(rendered_numbers)
    for number in sorted(api_numbers - rendered_set):
        chapter, page = api_number_pages[number]
        issue(issues, "formula_number_missing_textbook", "critical", number, f"PaddleOCR API label exists at Genetics chapter {chapter}, PDF page {page} but not in Markdown.", "Repair formula link and re-export.")
    for number in sorted(rendered_set - api_numbers):
        issue(issues, "formula_number_extra_textbook", "critical", number, "Markdown label absent from PaddleOCR API source.", "Remove unsupported label.")
    for number, count in Counter(rendered_numbers).items():
        if count != 1:
            issue(issues, "formula_number_duplicate_textbook", "critical", number, f"Markdown renders the label {count} times.", "Fix formula occurrence mapping.")

    api_tables = genetics_api_tables()
    for table in tables:
        table_id = str(table.get("id") or "")
        expected = api_tables.get(table_id)
        if not expected:
            issue(issues, "table_missing_api", "critical", table_id, "No PaddleOCR API caption/body pair.", "Recover the table from source PDF/API.")
            continue
        if table.get("table_type") == "missing" or not table.get("rows") or not table.get("html"):
            issue(issues, "table_stub", "critical", table_id, "Dedicated table still lacks body/rows.", "Restore API table body.")
            continue
        if re.sub(r"\s+", "", str(table.get("html"))) != re.sub(r"\s+", "", str(expected.get("html"))):
            issue(issues, "table_body_mismatch", "critical", table_id, "Stored HTML differs from PaddleOCR API table evidence.", "Rebuild table library.")

    for figure in figures:
        source = figure.get("source") if isinstance(figure.get("source"), dict) else {}
        asset = TEXTBOOK / str(figure.get("asset_path") or "")
        if not asset.is_file() or asset.stat().st_size == 0:
            issue(issues, "figure_asset", "critical", str(figure.get("id") or ""), "Figure asset missing or empty.", "Restore source crop.")
        source_pdf = str(figure.get("source_pdf") or source.get("source_pdf") or "")
        if not asset.name.startswith("Genetics_") or "Genetics_chapter" not in source_pdf:
            issue(issues, "figure_owner", "critical", str(figure.get("id") or ""), "Figure asset/source is not Genetics-owned.", "Relink dedicated figure record.")

    rendered_evidence = render_formula_page_evidence()
    metrics = {
        "logical_chapters": 27,
        "formula_records": len(formulas),
        "numbered_formulas_paddleocr_api": len(api_numbers),
        "numbered_formulas_textbook": len(rendered_set),
        "table_records": len(tables),
        "figure_records": len(figures),
        "formula_page_evidence_images": rendered_evidence,
        "issues": len(issues),
        "allowed_table_position_offset": "Complete tables may be materialized at the end of their owning section.",
        "encoding_check": "UTF-8 decoded and U+FFFD is not used as terminal-display evidence.",
        "formula_evidence_source": "Saved PaddleOCR Cloud/API raw layout response, not local OCR.",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / "issues.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["type", "severity", "location", "pdf_page", "evidence", "recommended_fix"])
        writer.writeheader()
        writer.writerows(issues)
    summary = [
        "# Genetics 书籍独立资产库与公式编号审计",
        "",
        f"- 章节覆盖：27 / 27",
        f"- 公式库记录：{len(formulas)}；PaddleOCR API 编号 / Markdown 编号：{len(api_numbers)} / {len(rendered_set)}",
        f"- 表格库记录：{len(tables)}；图片库记录：{len(figures)}",
        f"- 问题数：{len(issues)}",
        "- 证据：每个含编号公式的章节保存一张原始 PDF 页渲染图；编号、坐标和表格 HTML 可追溯至保存的 PaddleOCR Cloud/API 响应。",
        "",
        "## 结论",
        "",
        "通过：所有自动可核验项均与 PaddleOCR API 和书籍专属资产库一致。" if not issues else "未通过：请按 issues.csv 修复列出的项目。",
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(summary), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
