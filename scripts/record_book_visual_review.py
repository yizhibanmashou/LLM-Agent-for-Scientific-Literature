#!/usr/bin/env python3
"""Optionally record a post-install human spot check for an audit contact sheet."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PER_SHEET = {"pages": 1, "blocks": 1, "formulas": 16, "tables": 4, "figures": 4, "examples": 1}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", required=True)
    parser.add_argument("--kind", required=True, choices=PER_SHEET)
    parser.add_argument("--sheet", required=True, type=int)
    parser.add_argument("--through", type=int)
    parser.add_argument("--status", choices=("verified", "rejected"), default="verified")
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", args.book):
        raise SystemExit("unsafe book identifier")
    end = args.through or args.sheet
    if args.sheet < 1 or end < args.sheet:
        raise SystemExit("invalid sheet range")
    audit = ROOT / "tmp" / "book_audits" / args.book
    ledger_path = audit / "ledgers" / f"{args.kind}.json"
    status_path = audit / "review" / "status.json"
    if not ledger_path.exists() or not status_path.exists():
        raise SystemExit("audit must be built before recording a review")
    if args.kind == "pages":
        contact_dir = audit / "evidence" / "page_contacts"
    elif args.kind == "blocks":
        contact_dir = audit / "evidence" / "page_contacts"
    else:
        contact_dir = audit / "evidence" / "contacts" / args.kind
    missing = [contact_dir / f"sheet_{sheet:03d}.jpg" for sheet in range(args.sheet, end + 1) if not (contact_dir / f"sheet_{sheet:03d}.jpg").exists()]
    if missing:
        raise SystemExit(f"contact sheet does not exist: {missing[0]}")
    ledgers = json.loads(ledger_path.read_text(encoding="utf-8"))
    first = (args.sheet - 1) * PER_SHEET[args.kind]
    last = end * PER_SHEET[args.kind]
    selected = ledgers[first:last]
    if not selected:
        raise SystemExit("selected sheets contain no ledger rows")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    for row in selected:
        key = str(row["review_key"])
        status[args.kind][key] = {"status": args.status, "evidence_sha256": row["evidence_sha256"]}
    derived_block_keys = []
    if args.kind == "pages":
        blocks = json.loads((audit / "ledgers" / "blocks.json").read_text(encoding="utf-8"))
        verified_pages = {int(key) for key, value in status["pages"].items() if value.get("status") == "verified"}
        for block in blocks:
            if block.get("source_pages") and set(block["source_pages"]).issubset(verified_pages):
                key = str(block["review_key"])
                status["blocks"][key] = {"status": "verified", "evidence_sha256": block["evidence_sha256"]}
                derived_block_keys.append(key)
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "book": args.book,
        "kind": args.kind, "sheets": [args.sheet, end], "status": args.status,
        "keys": [str(row["review_key"]) for row in selected], "evidence_sha256": [row["evidence_sha256"] for row in selected],
        "basis": "human_visual_inspection_of_master_pdf_vs_delivery_evidence", "note": args.note,
        "derived_verified_block_keys": derived_block_keys,
    }
    with (audit / "review" / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
