#!/usr/bin/env python3
"""Restore referenced Evolution formulas from authoritative chapter layouts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
PADDLE = ROOT / "data" / "paddle_output"
LIBRARY = STRUCTURED / "Evolution_formula_library.json"
REPORT = ROOT / "tmp" / "book_audits" / "Evolution" / "reports" / "missing_formula_repairs.json"
REFERENCE_RE = re.compile(r"\[\[(?:SEE_)?FORMULA:([^\]]+)\]\]")
NUMBER_RE = re.compile(r"\(?\s*((?:A\s*)?\d+(?:\.\d+)+(?:[a-z])?)\s*\)?", re.I)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def content(row: dict[str, Any]) -> str:
    return str(row.get("block_content") or "").strip()


def canonical_id(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def numbered_id(value: str) -> str | None:
    match = NUMBER_RE.search(value)
    return canonical_id(match.group(1)) if match else None


def referenced_formulas() -> dict[str, dict[str, str]]:
    """Map every formal placeholder to the unit that delivers it."""
    references: dict[str, dict[str, str]] = {}
    for path in sorted(STRUCTURED.glob("Evolution_*.json")):
        payload = read_json(path)
        if not isinstance(payload, dict) or not isinstance(payload.get("blocks"), list):
            continue
        metadata = payload.get("metadata") or {}
        chapter = str(metadata.get("chapter") or "")
        for block in payload["blocks"]:
            for formula_id in REFERENCE_RE.findall(str(block.get("content") or "")):
                references.setdefault(canonical_id(formula_id), {
                    "id": formula_id,
                    "chapter": chapter,
                    "unit_id": str(payload.get("id") or path.stem),
                    "subsection": str(metadata.get("display_heading") or metadata.get("section") or ""),
                })
    return references


def vertical_distance(first: list[float], second: list[float]) -> float:
    first_center = (float(first[1]) + float(first[3])) / 2
    second_center = (float(second[1]) + float(second[3])) / 2
    return abs(first_center - second_center)


def formula_for_number(rows: list[dict[str, Any]], number: dict[str, Any]) -> dict[str, Any]:
    """Find the display formula aligned with a number, independent of OCR order."""
    number_box = number.get("block_bbox") or []
    candidates = [
        row for row in rows
        if row.get("block_label") == "display_formula" and len(row.get("block_bbox") or []) == 4
    ]
    if len(number_box) != 4 or not candidates:
        raise ValueError(f"numbered formula has no display candidate: {content(number)}")
    aligned = [
        row for row in candidates
        if float(row["block_bbox"][1]) <= float(number_box[3])
        and float(row["block_bbox"][3]) >= float(number_box[1])
    ]
    pool = aligned or candidates
    result = min(pool, key=lambda row: vertical_distance(row["block_bbox"], number_box))
    if vertical_distance(result["block_bbox"], number_box) > 120:
        raise ValueError(f"numbered formula alignment is ambiguous: {content(number)}")
    return result


def indexed_numbered_formulas(wanted: set[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for raw_path in sorted(PADDLE.glob("Evolution_*_full/intermediate/paddle_raw_response.json")):
        chapter = raw_path.parents[1].name.removesuffix("_full")
        for page_number, page in enumerate(read_json(raw_path), 1):
            rows = (page.get("prunedResult") or page).get("parsing_res_list") or []
            for number in rows:
                if number.get("block_label") != "formula_number":
                    continue
                formula_id = numbered_id(content(number))
                if not formula_id or formula_id not in wanted:
                    continue
                formula = formula_for_number(rows, number)
                candidate = {
                    "chapter": chapter,
                    "page": page_number,
                    "number": number,
                    "formula": formula,
                }
                old = indexed.get(formula_id)
                if old and (
                    content(old["formula"]) != content(formula)
                    or old["chapter"] != chapter
                ):
                    raise ValueError(f"conflicting Paddle formulas for {formula_id}")
                indexed[formula_id] = candidate
    return indexed


def strip_display_delimiters(value: str) -> str:
    value = value.strip()
    if value.startswith("$$") and value.endswith("$$"):
        return value[2:-2].strip()
    return value


def main() -> None:
    library = read_json(LIBRARY)
    by_id = {canonical_id(str(item["id"])): item for item in library["formulas"]}
    references = referenced_formulas()
    indexed = indexed_numbered_formulas(set(references) - set(by_id))
    repairs = []
    for key, reference in sorted(references.items()):
        if key in by_id:
            continue
        source = indexed.get(key)
        if not source:
            raise ValueError(f"referenced formula is absent from Paddle evidence: {reference['id']}")
        if source["chapter"] != reference["chapter"]:
            raise ValueError(f"formula chapter mismatch: {reference['id']}")
        formula = source["formula"]
        number = source["number"]
        formula_id = reference["id"]
        latex = strip_display_delimiters(content(formula))
        page_number = int(source["page"])
        entry = {
            "id": formula_id,
            "label_format": content(number),
            "latex": latex,
            "formula_type": "block",
            "source": {
                "unit_id": reference["unit_id"],
                "chapter": source["chapter"],
                "subsection": reference["subsection"],
                "page": page_number,
                "bbox": formula["block_bbox"],
                "extraction_channel": "exact_paddle_numbered_formula_recovery",
            },
            "source_evidence": {
                "pdf_page": page_number,
                "formula_bbox": formula["block_bbox"],
                "number_bbox": number["block_bbox"],
                "source_block_ids": [
                    f"{source['chapter']}:p{page_number:03d}:b{formula['block_id']}",
                    f"{source['chapter']}:p{page_number:03d}:b{number['block_id']}",
                ],
            },
            "context": "Referenced formula restored from the authoritative chapter PDF Paddle layout.",
            "description": None,
            "book": "Evolution",
            "render_mode": "canonical",
        }
        by_id[key] = entry
        repairs.append({
            "formula_id": formula_id,
            "chapter": source["chapter"],
            "page": page_number,
            "source_block_ids": entry["source_evidence"]["source_block_ids"],
            "source_sha256": hashlib.sha256(content(formula).encode("utf-8")).hexdigest(),
        })
    library["formulas"] = sorted(
        by_id.values(),
        key=lambda item: (str((item.get("source") or {}).get("chapter")), str(item["id"])),
    )
    write_json(LIBRARY, library)
    report = {
        "schema": "evolution_missing_formula_repairs.v2",
        "book": "Evolution",
        "referenced_formula_count": len(references),
        "repair_count": len(repairs),
        "formula_count": len(library["formulas"]),
        "repairs": repairs,
    }
    write_json(REPORT, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
