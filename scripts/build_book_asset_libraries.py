"""Build book-scoped formula, table, and figure libraries.

The Genetics formula labels and table bodies are recovered exclusively from
the saved PaddleOCR Cloud/API layout responses.  The script refuses to write
if a numbered equation or formal table cannot be mapped without ambiguity.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
PADDLE = ROOT / "data" / "paddle_output"
GLOBAL_FORMULAS = STRUCTURED / "formula_library.json"
GLOBAL_TABLES = STRUCTURED / "table_library.json"
GLOBAL_FIGURES = ROOT / "data" / "figure_library.json"
BOOKS = ("Evolution", "Genetics")
NUMBER_RE = re.compile(r"^\(?\s*(?P<number>[A-Za-z]?\d+\.\d+[A-Za-z]?)\s*\)?$")
FORMULA_ID_RE = re.compile(r"^(?P<book>[A-Za-z]+)_chapter(?P<chapter>\d+)_formula(?P<ordinal>\d+)$")
TABLE_TITLE_RE = re.compile(r"^\s*Table\s+(?P<id>(?:A\d+|\d+)\.\d+[A-Za-z]?)\b", re.I)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_math(value: str) -> str:
    """Make API and library LaTex comparable without changing stored LaTex."""
    value = str(value or "").lower()
    value = re.sub(r"\$", "", value)
    value = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", value)
    value = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\operatorname\{([^}]*)\}", r"\1", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def number_from_id(value: str) -> tuple[int, int]:
    match = FORMULA_ID_RE.match(str(value))
    if not match:
        return (9999, 999999)
    return int(match.group("chapter")), int(match.group("ordinal"))


def chapter_from_formula_id(value: str) -> int | None:
    match = FORMULA_ID_RE.match(str(value))
    return int(match.group("chapter")) if match else None


def book_for_formula(formula: dict[str, Any]) -> str | None:
    value = str(formula.get("id") or "")
    for book in BOOKS:
        if value.startswith(f"{book}_"):
            return book
    source = formula.get("source") if isinstance(formula.get("source"), dict) else {}
    chapter = str(source.get("chapter") or "")
    return next((book for book in BOOKS if chapter.startswith(f"{book}_")), None)


def book_for_table(table: dict[str, Any]) -> str | None:
    source = table.get("source") if isinstance(table.get("source"), dict) else {}
    chapter = str(source.get("chapter") or "")
    return next((book for book in BOOKS if chapter.startswith(f"{book}_")), None)


def book_for_figure(figure: dict[str, Any]) -> str | None:
    chapter = str(figure.get("chapter") or "")
    return next((book for book in BOOKS if chapter.startswith(f"{book}_")), None)


def api_pages(chapter: int) -> list[list[dict[str, Any]]]:
    path = PADDLE / f"Genetics_chapter{chapter}_full" / "intermediate" / "paddle_raw_api_response.json"
    payload = read(path)
    results = payload["result"]["layoutParsingResults"]
    return [
        [block for block in result.get("prunedResult", {}).get("parsing_res_list", []) if isinstance(block, dict)]
        for result in results
    ]


def center_y(block: dict[str, Any]) -> float:
    bbox = block.get("block_bbox") or [0, 0, 0, 0]
    return (float(bbox[1]) + float(bbox[3])) / 2


def pair_formula_numbers(blocks: list[dict[str, Any]], page: int, chapter: int) -> list[dict[str, Any]]:
    formulas = [block for block in blocks if block.get("block_label") == "display_formula"]
    labels = []
    for block in blocks:
        if block.get("block_label") != "formula_number":
            continue
        match = NUMBER_RE.fullmatch(str(block.get("block_content") or "").strip())
        if match:
            labels.append((block, match.group("number")))

    paired: dict[int, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    used_labels: set[int] = set()
    for label_index, (label, number) in enumerate(labels):
        candidates = [
            (abs(center_y(formula) - center_y(label)), formula_index, formula)
            for formula_index, formula in enumerate(formulas)
            if abs(center_y(formula) - center_y(label)) <= 150
        ]
        if not candidates:
            raise ValueError(f"Genetics chapter {chapter} PDF page {page}: unpaired formula number ({number})")
        _, formula_index, formula = min(candidates, key=lambda item: item[0])
        paired[formula_index].append((number, label))
        used_labels.add(label_index)

    entries: list[dict[str, Any]] = []
    for formula_index, formula in enumerate(formulas):
        matches = paired.get(formula_index, [])
        number, label = matches[0] if len(matches) == 1 else (None, None)
        entries.append(
            {
                "latex": str(formula.get("block_content") or ""),
                "canonical": canonical_math(str(formula.get("block_content") or "")),
                "page": page,
                "formula_bbox": formula.get("block_bbox"),
                "equation_number": number,
                "label_bbox": label.get("block_bbox") if label else None,
                "label_text": label.get("block_content") if label else None,
                "equation_numbers": [item[0] for item in matches],
                "label_bboxes": [item[1].get("block_bbox") for item in matches],
            }
        )
    if len(used_labels) != len(labels):
        raise ValueError(f"Genetics chapter {chapter} PDF page {page}: unconsumed formula number label")
    return entries


def genetics_api_formulas(chapter: int) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for page, blocks in enumerate(api_pages(chapter), start=1):
        entries.extend(pair_formula_numbers(blocks, page, chapter))
    return entries


def map_formula_records(records: list[dict[str, Any]], api_entries: list[dict[str, Any]], chapter: int) -> dict[str, dict[str, Any]]:
    """Map formula library records to API displays with exact canonical LaTex.

    SequenceMatcher handles the known pages that have an extra/missing display
    block.  Remaining records must have one unambiguous canonical match.
    """
    record_keys = [canonical_math(str(record.get("latex") or "")) for record in records]
    api_keys = [entry["canonical"] for entry in api_entries]
    mapping: dict[int, int] = {}
    matcher = difflib.SequenceMatcher(a=record_keys, b=api_keys, autojunk=False)
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            mapping.update({index: b0 + index - a0 for index in range(a0, a1)})

    # In the normal case the source PDF and library have identical display
    # counts.  Positional pairing is then deterministic even if the legacy
    # library dropped a term from a formula (for example a parenthesized SE).
    if len(records) == len(api_entries):
        for index in range(len(records)):
            mapping.setdefault(index, index)

    unmatched_records = [index for index in range(len(records)) if index not in mapping]
    used_api = set(mapping.values())
    for record_index in unmatched_records:
        candidates = [
            api_index
            for api_index, api_key in enumerate(api_keys)
            if api_index not in used_api and api_key == record_keys[record_index]
        ]
        if len(candidates) == 1:
            mapping[record_index] = candidates[0]
            used_api.add(candidates[0])
            continue
        if candidates:
            api_index = min(candidates, key=lambda candidate: abs(candidate - record_index))
            mapping[record_index] = api_index
            used_api.add(api_index)
            continue
        # A small number of legacy library formulas were themselves damaged by
        # OCR.  Accept a positional fuzzy match only when it is clearly the
        # nearest remaining API formula; the API LaTex will then replace it.
        fuzzy = [
            (
                difflib.SequenceMatcher(a=record_keys[record_index], b=api_key, autojunk=False).ratio(),
                api_index,
            )
            for api_index, api_key in enumerate(api_keys)
            if api_index not in used_api
        ]
        fuzzy.sort(reverse=True)
        if fuzzy and fuzzy[0][0] >= 0.88 and (len(fuzzy) == 1 or fuzzy[0][0] - fuzzy[1][0] >= 0.08):
            mapping[record_index] = fuzzy[0][1]
            used_api.add(fuzzy[0][1])
            continue
        raise ValueError(
            f"Genetics chapter {chapter}: formula {records[record_index].get('id')} has no exact PaddleOCR API match"
        )
    if len(mapping) != len(records):
        raise ValueError(f"Genetics chapter {chapter}: incomplete formula mapping")
    return {str(records[record_index]["id"]): api_entries[api_index] for record_index, api_index in mapping.items()}


def latex_without_display_delimiters(value: str) -> str:
    value = str(value or "").strip()
    if value.startswith("$$") and value.endswith("$$"):
        return value[2:-2].strip()
    return value


def strip_embedded_equation_tags(value: str) -> str:
    """PaddleOCR may place a printed right-margin number inside LaTex."""
    return re.sub(r"\\tag\{[^}\n]*(?:\}|$)", "", str(value or "")).strip()


def is_legacy_non_display_formula(record: dict[str, Any]) -> bool:
    """Identify a legacy OCR record that contains prose, not a display math item."""
    return str(record.get("id") or "") in {
        "Genetics_chapter9_formula061",
        "Genetics_chapter27_formula153",
    }


def split_known_multi_number_formula(latex: str, numbers: list[str]) -> list[dict[str, str]]:
    """Split the one API display that contains two separately numbered rows."""
    if numbers != ["A1.11", "A1.12"]:
        raise ValueError(f"Unsupported multi-number display formula: {numbers}")
    inner = latex_without_display_delimiters(latex)
    if not (inner.startswith(r"\begin{align*}") and inner.endswith(r"\end{align*}")):
        raise ValueError("A1.11/A1.12 API formula is not an align block")
    inner = inner[len(r"\begin{align*}") : -len(r"\end{align*}")]
    pieces = re.split(r"\\{2,}(?=\\sigma\(m_\{r\},m_\{q\}\))", inner, maxsplit=1)
    if len(pieces) != 2:
        raise ValueError("Could not split A1.11/A1.12 API align rows")
    return [
        {"latex": pieces[0].replace("&", ""), "equation_number": "A1.11"},
        {"latex": r"\begin{aligned}" + pieces[1] + r"\end{aligned}", "equation_number": "A1.12"},
    ]


def raw_table_rows(value: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", value, flags=re.I | re.S):
        cells = []
        for cell in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, flags=re.I | re.S):
            cell = re.sub(r"<[^>]+>", "", cell)
            cells.append(html.unescape(re.sub(r"\s+", " ", cell)).strip())
        if cells:
            rows.append(cells)
    return rows


def merge_table_html(first: str, continuation: str) -> str:
    def inner(value: str) -> str:
        value = re.sub(r"^\s*<table\b[^>]*>", "", value, flags=re.I)
        return re.sub(r"</table>\s*$", "", value, flags=re.I)

    return "<table>" + inner(first) + inner(continuation) + "</table>"


def genetics_api_tables() -> dict[str, dict[str, Any]]:
    tables: dict[str, dict[str, Any]] = {}
    for chapter in range(1, 28):
        for page, blocks in enumerate(api_pages(chapter), start=1):
            captions = [block for block in blocks if block.get("block_label") in {"figure_title", "table_caption"}]
            page_tables = [block for block in blocks if block.get("block_label") == "table"]
            for caption in captions:
                match = TABLE_TITLE_RE.search(str(caption.get("block_content") or ""))
                if not match:
                    continue
                table_id = match.group("id")
                candidates = [
                    table
                    for table in page_tables
                    if center_y(table) >= center_y(caption) - 50
                ]
                if not candidates:
                    raise ValueError(f"Table {table_id}: API caption has no table body on PDF page {page}")
                table = min(candidates, key=lambda item: abs(center_y(item) - center_y(caption)))
                body = str(table.get("block_content") or "").strip()
                if not body.lower().startswith("<table"):
                    raise ValueError(f"Table {table_id}: API body is not HTML")
                if table_id in tables:
                    previous = tables[table_id]
                    previous["html"] = merge_table_html(str(previous["html"]), body)
                    previous["rows"].extend(raw_table_rows(body))
                    previous.setdefault("continued_pages", []).append(page)
                    previous.setdefault("continued_bboxes", []).append(table.get("block_bbox"))
                    continue
                tables[table_id] = {
                    "title": str(caption.get("block_content") or "").strip(),
                    "html": body,
                    "rows": raw_table_rows(body),
                    "page": page,
                    "bbox": table.get("block_bbox"),
                    "caption_bbox": caption.get("block_bbox"),
                    "source_pdf": f"Genetics_chapter{chapter}.pdf",
                }
    return tables


def library_payload(book: str, asset_type: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    key = {"formula": "formulas", "table": "tables", "figure": "figures"}[asset_type]
    return {
        "version": 1,
        "book": book,
        "asset_type": asset_type,
        "authority": "book-scoped source of truth",
        key: records,
    }


def make_libraries() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    global_formulas = read(GLOBAL_FORMULAS)
    global_tables = read(GLOBAL_TABLES)
    global_figures = read(GLOBAL_FIGURES)
    figures_payload = global_figures.get("figures", {})
    figures = list(figures_payload.values()) if isinstance(figures_payload, dict) else list(figures_payload)

    formula_by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for formula in global_formulas.get("formulas", []):
        if not isinstance(formula, dict):
            continue
        book = book_for_formula(formula)
        if book:
            formula_by_book[book].append(copy.deepcopy(formula))
    table_by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table in global_tables.get("tables", []):
        if not isinstance(table, dict):
            continue
        book = book_for_table(table)
        if book:
            table_by_book[book].append(copy.deepcopy(table))
    figure_by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for figure in figures:
        if not isinstance(figure, dict):
            continue
        book = book_for_figure(figure)
        if book:
            figure_by_book[book].append(copy.deepcopy(figure))

    genetics = sorted(formula_by_book["Genetics"], key=lambda record: number_from_id(str(record.get("id") or "")))
    by_chapter: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for formula in genetics:
        chapter = chapter_from_formula_id(str(formula.get("id") or ""))
        if chapter is None:
            raise ValueError(f"Malformed Genetics formula id: {formula.get('id')}")
        by_chapter[chapter].append(formula)
    for chapter, records in by_chapter.items():
        records.sort(key=lambda record: number_from_id(str(record.get("id") or ""))[1])
        active_records = [record for record in records if not is_legacy_non_display_formula(record)]
        mapping = map_formula_records(active_records, genetics_api_formulas(chapter), chapter)
        for formula in active_records:
            api = mapping[str(formula["id"])]
            formula["book"] = "Genetics"
            api_latex = strip_embedded_equation_tags(latex_without_display_delimiters(api["latex"]))
            previous_latex = strip_embedded_equation_tags(str(formula.get("latex") or ""))
            if canonical_math(previous_latex) != canonical_math(api_latex):
                formula["latex"] = api_latex
                formula["latex_recovery"] = "verified_paddleocr_api_display_formula"
            else:
                formula["latex"] = previous_latex
            formula["source_evidence"] = {
                "evidence_type": "paddleocr_cloud_api_layout",
                "source_pdf": api["page"] and f"Genetics_chapter{chapter}.pdf",
                "pdf_page": api["page"],
                "formula_bbox": api["formula_bbox"],
                "label_bbox": api["label_bbox"],
                "label_bboxes": api["label_bboxes"],
                "api_label": api["label_text"],
                "api_labels": api["equation_numbers"],
                "api_response": f"data/paddle_output/Genetics_chapter{chapter}_full/intermediate/paddle_raw_api_response.json",
            }
            if len(api["equation_numbers"]) > 1:
                formula["equation_numbers"] = api["equation_numbers"]
                formula["label_format"] = [f"({number})" for number in api["equation_numbers"]]
                formula["number_status"] = "verified_paddleocr_api"
                formula["render_mode"] = "multi_numbered_equation"
                formula["render_parts"] = split_known_multi_number_formula(api["latex"], api["equation_numbers"])
            elif api["equation_number"]:
                formula["equation_number"] = api["equation_number"]
                formula["label_format"] = f"({api['equation_number']})"
                formula["number_status"] = "verified_paddleocr_api"
                formula["render_mode"] = "numbered_equation"
            else:
                formula.pop("equation_number", None)
                formula["label_format"] = None
                formula["number_status"] = "verified_unnumbered_paddleocr_api"
                formula["render_mode"] = "display_equation"
        for formula in records:
            if formula in active_records:
                continue
            formula["book"] = "Genetics"
            formula["record_status"] = "excluded_legacy_non_display_formula"
            formula["number_status"] = "not_a_pdf_display_formula"
            formula["render_mode"] = "exclude"

    for book, records in formula_by_book.items():
        if book != "Genetics":
            for formula in records:
                formula["book"] = book
                formula.setdefault("render_mode", "legacy")

    table_api = genetics_api_tables()
    for table in table_by_book["Genetics"]:
        table_id = str(table.get("id") or "")
        recovered = table_api.get(table_id)
        if not recovered:
            raise ValueError(f"Genetics table {table_id} has no PaddleOCR API table/caption pair")
        if not recovered["rows"]:
            raise ValueError(f"Genetics table {table_id} has no recoverable table rows")
        source = table.get("source") if isinstance(table.get("source"), dict) else {}
        source.update(
            {
                "page": recovered["page"],
                "bbox": recovered["bbox"],
                "caption_bbox": recovered["caption_bbox"],
                "source_pdf": recovered["source_pdf"],
                "extraction_channel": "paddleocr_cloud_api_layout",
                "needs_review": False,
            }
        )
        table["book"] = "Genetics"
        table["label_format"] = f"Table {table_id}"
        table["title"] = recovered["title"]
        table["table_type"] = "numbered"
        table["html"] = recovered["html"]
        table["rows"] = recovered["rows"]
        table["source"] = source
        table["description"] = None
    for book, records in table_by_book.items():
        if book != "Genetics":
            for table in records:
                table["book"] = book

    for book, records in figure_by_book.items():
        for figure in records:
            figure["book"] = book
            figure["asset_key"] = f"{book}:{figure.get('chapter')}:{figure.get('id')}"

    return formula_by_book, table_by_book, figure_by_book


def write_libraries(formulas: dict[str, list[dict[str, Any]]], tables: dict[str, list[dict[str, Any]]], figures: dict[str, list[dict[str, Any]]]) -> None:
    for book in BOOKS:
        formula_records = sorted(formulas[book], key=lambda item: str(item.get("id") or ""))
        table_records = sorted(tables[book], key=lambda item: (str((item.get("source") or {}).get("chapter") or ""), str(item.get("id") or "")))
        figure_records = sorted(figures[book], key=lambda item: (str(item.get("chapter") or ""), str(item.get("id") or "")))
        write(STRUCTURED / f"{book}_formula_library.json", library_payload(book, "formula", formula_records))
        write(STRUCTURED / f"{book}_table_library.json", library_payload(book, "table", table_records))
        write(STRUCTURED / f"{book}_figure_library.json", library_payload(book, "figure", figure_records))

    # Compatibility indexes are regenerated only from the book-scoped sources.
    all_formulas = [record for book in BOOKS for record in formulas[book]]
    all_tables = [record for book in BOOKS for record in tables[book]]
    all_figures = [record for book in BOOKS for record in figures[book]]
    write(GLOBAL_FORMULAS, {"metadata": {"version": 2, "authority": "generated compatibility index"}, "formulas": all_formulas})
    write(GLOBAL_TABLES, {"metadata": {"version": 2, "authority": "generated compatibility index"}, "tables": all_tables})
    write(
        GLOBAL_FIGURES,
        {
            "version": 2,
            "authority": "generated compatibility index",
            "figures": {
                str(record["asset_key"]): record
                for record in all_figures
            },
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate recovery without writing files.")
    args = parser.parse_args()
    formulas, tables, figures = make_libraries()
    summary = {
        "formulas": {book: len(formulas[book]) for book in BOOKS},
        "numbered_genetics_formulas": sum(1 for record in formulas["Genetics"] if record.get("equation_number")),
        "tables": {book: len(tables[book]) for book in BOOKS},
        "figures": {book: len(figures[book]) for book in BOOKS},
        "genetics_table_stubs": sum(1 for table in tables["Genetics"] if not table.get("rows") or table.get("table_type") == "missing"),
    }
    print(json.dumps(summary, ensure_ascii=False))
    if not args.check:
        write_libraries(formulas, tables, figures)


if __name__ == "__main__":
    main()
