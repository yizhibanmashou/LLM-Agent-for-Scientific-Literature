#!/usr/bin/env python3
"""Split and verify selected Principles of Population Genetics chapters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAME = "Principle of population genetics 4th ed - Hartl and Clark.pdf"
RANGES = {
    2: (59, 106),
    3: (109, 162),
    4: (165, 210),
    6: (271, 329),
}


def split(source: Path, output_dir: Path) -> dict[str, object]:
    source_document = fitz.open(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    try:
        for chapter, (start, end) in RANGES.items():
            target = output_dir / f"PopGen_chapter{chapter}.pdf"
            temporary = target.with_suffix(".pdf.tmp")
            output_document = fitz.open()
            try:
                output_document.insert_pdf(source_document, from_page=start - 1, to_page=end - 1)
                output_document.save(temporary, garbage=4, deflate=True)
            finally:
                output_document.close()
            temporary.replace(target)
            check = fitz.open(target)
            try:
                expected_pages = end - start + 1
                if check.page_count != expected_pages:
                    raise RuntimeError(f"{target.name}: wrote {check.page_count} pages, expected {expected_pages}")
            finally:
                check.close()
            records.append({
                "chapter": chapter,
                "source_pages": [start, end],
                "page_count": expected_pages,
                "output": str(target),
            })
        return {
            "source": str(source),
            "source_page_count": source_document.page_count,
            "chapters": records,
        }
    finally:
        source_document.close()


def verify(output_dir: Path) -> dict[str, object]:
    errors: list[str] = []
    records: list[dict[str, object]] = []
    for chapter, (start, end) in RANGES.items():
        path = output_dir / f"PopGen_chapter{chapter}.pdf"
        expected = end - start + 1
        if path.is_file():
            document = fitz.open(path)
            try:
                actual = document.page_count
            finally:
                document.close()
        else:
            actual = 0
        if actual != expected:
            errors.append(f"{path.name}: pages={actual}, expected={expected}")
        records.append({"chapter": chapter, "path": str(path), "page_count": actual, "expected": expected})
    return {"valid": not errors, "chapters": records, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "背景资料" / SOURCE_NAME)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "背景资料")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--report", type=Path, default=ROOT / "tmp" / "popgen" / "split_report.json")
    args = parser.parse_args()
    result = verify(args.output_dir) if args.verify_only else split(args.source, args.output_dir)
    if not args.verify_only:
        result["verification"] = verify(args.output_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    verification = result if args.verify_only else result["verification"]
    if not verification["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
