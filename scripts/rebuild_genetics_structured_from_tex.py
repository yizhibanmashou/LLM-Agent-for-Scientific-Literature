#!/usr/bin/env python3
"""Losslessly rebuild selected Genetics structured chapters from their LaTeX source.

This intentionally does not perform semantic summarisation.  Every section or
subsection becomes one JSON unit, preserving prose, display mathematics,
figure placeholders and raw HTML tables from the normalized chapter source.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r"(?m)^\\section\{(?P<title>[^{}]+)\}")
SUBSECTION_RE = re.compile(r"(?m)^\\subsection\{(?P<title>[^{}]+)\}")
CHAPTER_RE = re.compile(r"(?m)^\\chapter\*?\{(?P<title>[^{}]+)\}")
DOCUMENT_RE = re.compile(r"\\begin\{document\}(?P<body>.*?)(?:\\end\{document\}|\Z)", re.DOTALL)
FIGURE_REF_RE = re.compile(r"\[\[FIGURE:([^\]]+)\]\]")
FORMULA_REF_RE = re.compile(r"\[\[(?:FORMULA|SEE_FORMULA):([^\]]+)\]\]")
TABLE_REF_RE = re.compile(r"\[\[(?:TABLE|SEE_TABLE):([^\]]+)\]\]")


def clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_content(value: str) -> str:
    value = value.replace("\r\n", "\n")
    value = re.sub(r"(?m)^\s*%.*$", "", value)
    value = re.sub(r"\\(?:begin|end)\{(?:figure\*?|center)\}(?:\[[^\]]*\])?", "", value)
    value = re.sub(r"\\(?:centering|noindent)\b", "", value)
    value = re.sub(r"\\label\{[^{}]*\}", "", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def chapter_units(tex: str) -> list[tuple[str, list[str], str]]:
    document = DOCUMENT_RE.search(tex)
    body = document.group("body") if document else tex
    sections = list(SECTION_RE.finditer(body))
    if not sections:
        chapter_matches = list(CHAPTER_RE.finditer(body))
        subsection_matches = list(SUBSECTION_RE.finditer(body))
        if not chapter_matches and not subsection_matches:
            raise ValueError("No LaTeX section, chapter, or subsection headings found in source")
        root = clean_title(chapter_matches[0].group("title")) if chapter_matches else "Chapter content"
        boundaries = chapter_matches + subsection_matches
        boundaries.sort(key=lambda match: match.start())
        units: list[tuple[str, list[str], str]] = []
        for index, match in enumerate(boundaries):
            end = boundaries[index + 1].start() if index + 1 < len(boundaries) else len(body)
            title = clean_title(match.group("title"))
            is_chapter = match.re is CHAPTER_RE
            heading_path = [title] if is_chapter else [root, title]
            content = clean_content(body[match.end() : end])
            if content:
                units.append((heading_path[0], heading_path, content))
        return units
    units: list[tuple[str, list[str], str]] = []
    for section_index, section_match in enumerate(sections):
        section = clean_title(section_match.group("title"))
        section_end = sections[section_index + 1].start() if section_index + 1 < len(sections) else len(body)
        section_body = body[section_match.end() : section_end]
        subsections = list(SUBSECTION_RE.finditer(section_body))
        if not subsections:
            content = clean_content(section_body)
            if content:
                units.append((section, [section], content))
            continue
        preamble = clean_content(section_body[: subsections[0].start()])
        if preamble:
            units.append((section, [section], preamble))
        for subsection_index, subsection_match in enumerate(subsections):
            subsection = clean_title(subsection_match.group("title"))
            subsection_end = subsections[subsection_index + 1].start() if subsection_index + 1 < len(subsections) else len(section_body)
            content = clean_content(section_body[subsection_match.end() : subsection_end])
            if content:
                units.append((section, [section, subsection], content))
    return units


def reference_metadata(reference_dir: Path, chapter: str) -> dict[str, Any]:
    files = sorted(reference_dir.glob(f"{chapter}_*.json"))
    if not files:
        return {}
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def write_chapter(source_root: Path, output_dir: Path, reference_dir: Path, chapter_number: int) -> int:
    chapter = f"Genetics_chapter{chapter_number}"
    source_path = source_root / f"{chapter}_full" / "main.tex"
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    units = chapter_units(source_path.read_text(encoding="utf-8"))
    if not units:
        raise ValueError(f"No units generated for {chapter}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob(f"{chapter}_*.json"):
        stale.unlink()
    reference = reference_metadata(reference_dir, chapter)
    source_title = str(reference.get("source_title") or "Genetics and Analysis of Quantitative Traits")
    source_file = str(reference.get("source_file") or source_path)
    for index, (section, heading_path, content) in enumerate(units, start=1):
        references = {
            "formula_references": sorted(set(FORMULA_REF_RE.findall(content))),
            "table_references": sorted(set(TABLE_REF_RE.findall(content))),
        }
        metadata = {
            "chapter": chapter,
            "section": section,
            "subsections": heading_path[1:],
            "source_file": source_file,
            "source_title": source_title,
            **references,
            "section_level_1": heading_path[0],
            "section_level_2": heading_path[1] if len(heading_path) > 1 else None,
            "heading_path": heading_path,
            "display_heading": " / ".join(heading_path),
            "rebuild_provenance": {
                "method": "lossless_tex_section_rebuild",
                "source": str(source_path),
                "preserves": ["prose", "display_math", "figure_placeholders", "raw_html_tables"],
            },
        }
        payload = {
            "id": f"{chapter}_{index:03d}",
            "metadata": metadata,
            "blocks": [{"type": "discussion", "content": content}],
        }
        target = output_dir / f"{chapter}_{index:03d}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(units)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("tmp/genetics_process_input"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-structured", type=Path, default=Path("data/structured"))
    parser.add_argument("--chapters", required=True, help="Comma-separated chapter numbers")
    args = parser.parse_args()
    chapters = [int(item.strip()) for item in args.chapters.split(",") if item.strip()]
    for chapter in chapters:
        count = write_chapter(args.source_root, args.output, args.reference_structured, chapter)
        source_path = args.source_root / f"Genetics_chapter{chapter}_full" / "main.tex"
        rebuilt_chars = sum(
            len(json.loads(path.read_text(encoding="utf-8"))["blocks"][0]["content"])
            for path in args.output.glob(f"Genetics_chapter{chapter}_*.json")
        )
        print(f"{chapter}: wrote {count} lossless units ({rebuilt_chars} content chars from {source_path})")


if __name__ == "__main__":
    main()
