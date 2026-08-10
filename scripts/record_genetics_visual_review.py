#!/usr/bin/env python3
"""Record a visually inspected Genetics contact sheet in the tmp audit ledger."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    "pages": ("page_ledger.json", 1, lambda row: str(row["page"]), "page_contacts"),
    "figures": ("figure_ledger.json", 4, lambda row: str(row["key"]), "figure_contacts"),
    "tables": ("table_ledger.json", 4, lambda row: f"{row['chapter']}:{row['id']}", "table_contacts"),
    "formulas": ("formula_ledger.json", 16, lambda row: str(row["id"]), "formula_contacts"),
    "examples": ("example_ledger.json", 4, lambda row: str(row["id"]), "example_contacts"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=KINDS)
    parser.add_argument("sheet", type=int)
    parser.add_argument(
        "--through",
        type=int,
        help="record every visually inspected sheet from SHEET through this inclusive end",
    )
    parser.add_argument("--audit-dir", type=Path, default=ROOT / "tmp" / "genetics_accuracy_audit")
    args = parser.parse_args()
    audit = args.audit_dir.resolve()
    ledger_name, per_sheet, key_for, contacts = KINDS[args.kind]
    end_sheet = args.through if args.through is not None else args.sheet
    if end_sheet < args.sheet:
        raise SystemExit("--through must be greater than or equal to SHEET")
    sheets = list(range(args.sheet, end_sheet + 1))
    sheet_paths = [audit / contacts / f"sheet_{sheet:03d}.jpg" for sheet in sheets]
    missing = [path for path in sheet_paths if not path.exists()]
    if missing:
        raise SystemExit(f"contact sheet does not exist: {missing[0]}")
    rows = json.loads((audit / ledger_name).read_text(encoding="utf-8"))
    selected = rows[(args.sheet - 1) * per_sheet : end_sheet * per_sheet]
    if not selected:
        raise SystemExit(f"sheet {args.sheet} has no ledger rows")
    review_path = audit / "visual_review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    for row in selected:
        review[args.kind][key_for(row)] = "verified"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    event_path = audit / "visual_review_events.jsonl"
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "kind": args.kind,
        "sheet": args.sheet if end_sheet == args.sheet else [args.sheet, end_sheet],
        "sheet_path": str(sheet_paths[0]) if end_sheet == args.sheet else [str(sheet_paths[0]), str(sheet_paths[-1])],
        "keys": [key_for(row) for row in selected],
        "status": "verified",
        "basis": (
            "human_visual_inspection_of_source_pdf_vs_structured_page_evidence"
            if args.kind == "pages"
            else "human_visual_inspection_of_source_pdf_contact_sheet"
        ),
    }
    with event_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
