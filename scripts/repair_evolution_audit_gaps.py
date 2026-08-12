#!/usr/bin/env python3
"""Recover Evolution Example gaps from the authoritative chapter PDFs.

The formal example pipeline is intentionally rerun only for Evolution.  Its
raw-layout evidence comes from the checked-in Paddle responses for the chapter
PDFs that the project designates as the authoritative source.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from knowledge_engineering.pipeline.example_pipeline import (  # noqa: E402, I001
    apply_example_pipeline,
)
from knowledge_engineering.processors.example_extraction import (  # noqa: E402, I001
    collapse_ws,
    strip_html,
    strip_structured_refs,
)


STRUCTURED = ROOT / "data" / "structured"
REPORT_DIR = ROOT / "tmp" / "evolution_example_repair"
TARGET_EXAMPLE_IDS = {
    "8.17", "10.1", "10.2", "12.10", "12.11", "13.1", "13.2",
    "14.5", "18.1", "18.2", "18.12", "19.11", "30.13",
}
A2_2_TAIL = (
    "Because $ p(3) = \\sum_{G} \\operatorname{Pr}(G) \\cdot p(3|G) = 0.195 $, "
    "Bayes' theorem gives the posterior probabilities for the genotypes given the observed value of 3 as: "
    "$$ \\Pr(QQ\\mid x=3)=0.078/0.195=0.400 $$ "
    "$$ \\Pr(Qq\\mid x=3)=0.070/0.195=0.359 $$ "
    "$$ \\Pr(qq\\mid x=3)=0.047/0.195=0.241 $$ "
    "Thus, there is a 40 percent chance that this individual has a genotype of QQ, a 36 percent chance it is Qq, "
    "and a 24 percent chance it is qq."
)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def example_locations(chapter: str, reference: str) -> list[tuple[Path, int]]:
    pattern = re.compile(rf"\[\[(?:SEE_)?EXAMPLE\s*:\s*{re.escape(reference)}\s*\]\]", re.I)
    hits: list[tuple[Path, int]] = []
    for path in sorted(STRUCTURED.glob(f"{chapter}_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for index, block in enumerate(data.get("blocks") or []):
            if pattern.search(str(block.get("content") or "")):
                hits.append((path, index))
    return hits


def insert_missing_placeholder(row: dict) -> None:
    chapter = str(row["chapter"])
    reference = str(row.get("example_ref") or row["example_id"])
    if example_locations(chapter, reference):
        return
    source = STRUCTURED / str(row["source_file"])
    data = json.loads(source.read_text(encoding="utf-8"))
    blocks = data.get("blocks") or []
    index = min(len(blocks), max(0, int(row.get("start_block_index") or 0)))
    blocks.insert(index, {"type": "example", "content": f"[[SEE_EXAMPLE:{reference}]]"})
    write_json(source, data)
    row["start_block_index"] = index
    row["end_block_index"] = index
    row.setdefault("replacement", {}).update({
        "status": "replaced",
        "reason": "placeholder_block_written",
        "placeholder_block_index": index,
        "placeholder_source_file": source.name,
    })


def remove_duplicate_placeholders(rows: list[dict]) -> None:
    for row in rows:
        chapter = str(row.get("chapter") or "")
        reference = str(row.get("example_ref") or row.get("example_id") or "")
        hits = example_locations(chapter, reference)
        for path, index in reversed(hits[1:]):
            data = json.loads(path.read_text(encoding="utf-8"))
            data["blocks"].pop(index)
            write_json(path, data)


def repair_a2_2(rows: list[dict]) -> None:
    matches = [
        row for row in rows
        if str(row.get("chapter") or "").lower() == "evolution_appendix2"
        and str(row.get("example_id") or "").upper() == "A2.2"
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one Evolution Example A2.2, found {len(matches)}")
    row = matches[0]
    if "0.078/0.195=0.400" not in str(row.get("content_markdown") or ""):
        row["content_markdown"] = f"{str(row.get('content_markdown') or '').rstrip()} {A2_2_TAIL}"
    row["content_plain"] = collapse_ws(strip_structured_refs(strip_html(row["content_markdown"])))
    row["block_ids"] = list(dict.fromkeys([
        *(row.get("block_ids") or []),
        "p1191:b18", "p1192:b2", "p1192:b3", "p1192:b4", "p1192:b5", "p1192:b6", "p1192:b7",
    ]))
    row["formula_refs"] = list(row.get("formula_refs") or [])
    row.setdefault("evidence", {})["authoritative_chapter_pdf_tail_recovery"] = {
        "source_pages": [1191, 1192],
        "source_block_ids": row["block_ids"],
    }
    row.setdefault("metadata", {})["needs_review"] = False
    row["metadata"]["word_count"] = len(row["content_plain"].split())


def finalize() -> dict:
    path = STRUCTURED / "example_library.json"
    library = json.loads(path.read_text(encoding="utf-8"))
    rows = library.get("examples") or []
    evolution = [row for row in rows if str(row.get("chapter") or "").lower().startswith("evolution_")]
    for row in evolution:
        chapter = str(row.get("chapter") or "")
        if chapter.lower().startswith("evolution_"):
            row["chapter"] = "Evolution_" + chapter.split("_", 1)[1]
        if str(row.get("example_id") or "") in TARGET_EXAMPLE_IDS:
            insert_missing_placeholder(row)
    remove_duplicate_placeholders(evolution)
    repair_a2_2(evolution)
    library["example_count"] = len(rows)
    write_json(path, library)
    unresolved = []
    for row in evolution:
        replacement = row.get("replacement") if isinstance(row.get("replacement"), dict) else {}
        if replacement.get("status") == "restored":
            continue
        reference = str(row.get("example_ref") or row.get("example_id") or "")
        count = len(example_locations(str(row.get("chapter") or ""), reference))
        if count != 1:
            unresolved.append(f"{row.get('chapter')}:{reference}:{count}")
    return {
        "evolution_examples": len(evolution),
        "new_examples": sorted(TARGET_EXAMPLE_IDS),
        "unresolved_placeholder_locations": unresolved,
        "a2_2_tail_restored": True,
    }


def main() -> int:
    library = json.loads((STRUCTURED / "example_library.json").read_text(encoding="utf-8"))
    excluded = {
        str(row.get("chapter") or "").strip().lower()
        for row in library.get("examples", [])
        if not str(row.get("chapter") or "").strip().lower().startswith("evolution_")
    }
    missing_before = [
        row for row in library.get("examples", [])
        if str(row.get("chapter") or "").lower().startswith("evolution_")
        and str(row.get("example_id") or "") in TARGET_EXAMPLE_IDS
    ]
    pipeline_result = None
    if len(missing_before) != len(TARGET_EXAMPLE_IDS):
        pipeline_result = apply_example_pipeline(
            STRUCTURED,
            project_root=ROOT,
            artifacts_dir=REPORT_DIR,
            dry_run=False,
            exclude_chapters=excluded,
        )
    result = {"schema": "evolution_audit_gap_repair.v1", "pipeline": pipeline_result, **finalize()}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(REPORT_DIR / "finalize_report.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["unresolved_placeholder_locations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
