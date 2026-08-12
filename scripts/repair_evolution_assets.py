"""Apply PDF-verified math repairs to Evolution table and figure assets."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
TABLES_PATH = STRUCTURED / "Evolution_table_library.json"
FIGURES_PATH = STRUCTURED / "Evolution_figure_library.json"
REPORT = ROOT / "tmp" / "book_audits" / "Evolution" / "asset_corrections" / "report.json"

OLD_HASHES = {
    "table:11.3": "d3c3a07d2b8886613983458b76fd8006e2ba568e484a7400816076b362c8b083",
    "table:21.3": "767a18d481e0b049923107346c7c57c1ff61aa32f389b1b1d41fa9a25027612d",
    "table:21.4": "5e3056c91fba07db674732b0fa2e9ceb4f1ec483f7c912476547db7187ae1701",
    "figure:29.12": "9fb53c9867e7b8a6bf6345a4773d8db960e04a0520269ff1c8dba00f0ba36aec",
}

TABLE_11_3_ROWS = [
    ["Source", "$ \\sigma_A^2 $", "$ \\sigma_D^2 $", "$ \\sigma_{ADI} $", "$ \\sigma_{DI}^2 $"],
    ["Within", "$ 1-f $", "$ 1-f-2(\\Delta-\\delta) $", "$ 2(f-\\gamma) $", "$ f-\\delta $"],
    ["A", "$ 1-f $", "$ 2[f-\\gamma-2(\\Delta-\\delta)] $", "$ 2(f-\\gamma) $", "$ 2(\\gamma-\\delta) $"],
    ["D", "$ 0 $", "$ 1-3f+2(\\Delta+\\gamma-\\delta) $", "$ 0 $", "$ f+\\delta-2\\gamma $"],
    ["AA", "$ 0 $", "$ 0 $", "$ 0 $", "$ 0 $"],
    ["Among", "$ 2f $", "$ 2(\\Delta-\\delta) $", "$ 2\\gamma $", "$ \\delta $"],
    ["Total", "$ 1+f $", "$ 1-f $", "$ 2f $", "$ f $"],
    ["", "Source", "$ \\iota^* $", "$ \\iota^2-\\iota^* $", "$ \\sigma_{AA}^2 $"],
    ["", "Within", "$ f-\\Delta $", "$ \\widetilde{f}-\\widetilde{\\Delta} $", "$ 1+2f-2\\widetilde{\\gamma}-\\widetilde{\\Delta} $"],
    ["", "A", "$ 2(\\gamma-\\Delta) $", "$ 2(\\widetilde{\\gamma}-\\widetilde{\\Delta}) $", "$ 4f-\\widetilde{f}-2\\widetilde{\\gamma}-\\widetilde{\\Delta} $"],
    ["", "D", "$ f+\\Delta-2\\gamma $", "$ \\widetilde{f}-2\\widetilde{\\gamma}+\\widetilde{\\Delta} $", "$ 0 $"],
    ["", "AA", "$ 0 $", "$ 0 $", "$ 1-2f+\\widetilde{f} $"],
    ["", "Among", "$ \\Delta-f^2 $", "$ \\widetilde{\\Delta}-f^2 $", "$ \\widetilde{f}+2\\widetilde{\\gamma}+\\Delta $"],
    ["", "Total", "$ f(1-f) $", "$ \\widetilde{f}-f^2 $", "$ 1+2f+\\widetilde{f} $"],
]

FAMILY_DEVIATION_FORMULA = (
    "$ \\sigma(z_{ij}-\\overline{z}_{i},y\\mid\\mathcal{R}_{1})="
    "(1-r_{n})(\\sigma_{A}^{2}/2)=\\left\\{\\begin{array}{ll}"
    "(1-1/n)(3/8)\\sigma_{A}^{2}&\\text{half-sibs}\\\\"
    "(1-1/n)(\\sigma_{A}^{2}/4)&\\text{full-sibs}\\end{array}\\right. $"
)
STRICT_WITHIN_FORMULA = (
    "$ \\sigma(z_{ij}-\\mu_i,y\\mid\\mathcal{R}_{1})="
    "(1-r)(\\sigma_A^2/2)=\\left\\{\\begin{array}{ll}"
    "(3/8)\\sigma_A^2&\\text{half-sibs}\\\\"
    "\\sigma_A^2/4&\\text{full-sibs}\\end{array}\\right. $"
)
NESTED_LABEL = (
    "Half-sib with nested full-sibs (nested sibs) among-family variance "
    "($ n_f $ females per male, $ n_s $ offspring per female, "
    "$ n=n_fn_s $ offspring per male)"
)


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find(items: list[dict[str, Any]], asset_id: str) -> dict[str, Any]:
    matches = [item for item in items if str(item.get("id")) == asset_id]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one asset {asset_id}, found {len(matches)}")
    return matches[0]


def table_html(rows: list[list[str]]) -> str:
    return "<table>" + "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell, quote=True)}</td>" for cell in row) + "</tr>"
        for row in rows
    ) + "</table>"


def table_markdown(rows: list[list[str]]) -> str:
    escaped = [[cell.replace("|", r"\|") for cell in row] for row in rows]
    header = escaped[0]
    body = escaped[1:]
    return "\n".join(
        [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
            *("| " + " | ".join(row) + " |" for row in body),
        ]
    )


def sync_table(entry: dict[str, Any], rows: list[list[str]]) -> None:
    entry["rows"] = rows
    entry["html"] = table_html(rows)
    if "markdown_body" in entry:
        entry["markdown_body"] = table_markdown(rows)


def assert_original_or_repaired(key: str, entry: dict[str, Any], repaired: bool) -> str:
    before = canonical_hash(entry)
    if before != OLD_HASHES[key] and not repaired:
        raise RuntimeError(f"Asset drifted before repair: {key} ({before})")
    return before


def main() -> None:
    tables = json.loads(TABLES_PATH.read_text(encoding="utf-8"))
    figures = json.loads(FIGURES_PATH.read_text(encoding="utf-8"))
    evidence: list[dict[str, Any]] = []

    table_11_3 = find(tables["tables"], "11.3")
    before = assert_original_or_repaired("table:11.3", table_11_3, table_11_3.get("rows") == TABLE_11_3_ROWS)
    sync_table(table_11_3, TABLE_11_3_ROWS)
    evidence.append({"asset": "table:11.3", "old_or_current_sha256": before, "new_sha256": canonical_hash(table_11_3), "source_pdf_page": 7})

    table_21_3 = find(tables["tables"], "21.3")
    repaired_21_3 = any(row and row[0] == "Selection on family deviations (FD)" and row[1] == FAMILY_DEVIATION_FORMULA for row in table_21_3["rows"])
    before = assert_original_or_repaired("table:21.3", table_21_3, repaired_21_3)
    rows_21_3 = table_21_3["rows"]
    for row in rows_21_3:
        if row and row[0] == "Selection on family deviations (FD)":
            row[1] = FAMILY_DEVIATION_FORMULA
        elif row and row[0] == "Strict within-family selection (FW)":
            row[1] = STRICT_WITHIN_FORMULA
    sync_table(table_21_3, rows_21_3)
    evidence.append({"asset": "table:21.3", "old_or_current_sha256": before, "new_sha256": canonical_hash(table_21_3), "source_pdf_page": 14})

    table_21_4 = find(tables["tables"], "21.4")
    repaired_21_4 = any(row and row[0] == NESTED_LABEL for row in table_21_4["rows"])
    before = assert_original_or_repaired("table:21.4", table_21_4, repaired_21_4)
    old_label = str(table_21_4["rows"][3][0])
    table_21_4["rows"][3][0] = NESTED_LABEL
    sync_table(table_21_4, table_21_4["rows"])
    for field in ("raw_body",):
        if isinstance(table_21_4.get(field), str):
            table_21_4[field] = table_21_4[field].replace(old_label, NESTED_LABEL)
    evidence.append({"asset": "table:21.4", "old_or_current_sha256": before, "new_sha256": canonical_hash(table_21_4), "source_pdf_page": 16})

    figure = find(figures["figures"], "29.12")
    repaired_figure = "($ M_2 $ is zero)" in str(figure.get("caption") or "")
    before = assert_original_or_repaired("figure:29.12", figure, repaired_figure)
    old = "$ (M_2 $ is zero $"
    new = "($ M_2 $ is zero)"
    figure["caption"] = str(figure["caption"]).replace(old, new)
    if isinstance(figure.get("caption_block"), dict):
        figure["caption_block"]["content"] = str(figure["caption_block"].get("content") or "").replace(old, new)
    evidence.append({"asset": "figure:29.12", "old_or_current_sha256": before, "new_sha256": canonical_hash(figure), "source_pdf_page": 53})

    TABLES_PATH.write_text(json.dumps(tables, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    FIGURES_PATH.write_text(json.dumps(figures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for item in evidence:
        chapter = str(item["asset"]).split(":", 1)[1].split(".", 1)[0]
        pdf = next((ROOT / "data").rglob(f"Evolution_chapter{chapter}.pdf"))
        item["source_pdf"] = pdf.relative_to(ROOT).as_posix()
        item["source_pdf_sha256"] = file_hash(pdf)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps({"schema": "evolution_asset_corrections.v1", "repairs": evidence}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"repaired": len(evidence), "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
