#!/usr/bin/env python3
"""Build and verify a chapter-separated Evolution delivery package."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BOOK = "Evolution"
SECTIONS = [f"chapter{number}" for number in range(1, 31)] + [f"appendix{number}" for number in range(1, 7)]
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((figures/[^)]+)\)")
ABSOLUTE_WINDOWS_PATH_RE = re.compile(r"^[A-Za-z]:[\\/]")
PATH_KEYS = {
    "source_file",
    "source_pdf",
    "package_source_pdf",
    "source_paddle_raw",
    "package_source_paddle_raw",
    "physical_evidence_path",
    "api_response",
    "package_api_response",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chapter_id(section: str) -> str:
    return f"{BOOK}_{section}"


def delivery_dir_name(section: str) -> str:
    match = re.fullmatch(r"(chapter|appendix)(\d+)", section)
    if not match:
        raise ValueError(f"Invalid section name: {section}")
    return f"{match.group(1)}{int(match.group(2)):02d}"


def sanitize_paths(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, nested in value.items():
            if key in PATH_KEYS:
                continue
            result[key] = sanitize_paths(nested)
        return result
    if isinstance(value, list):
        return [sanitize_paths(item) for item in value]
    return value


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from iter_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_strings(nested)
    elif isinstance(value, str):
        yield value


def load_libraries() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    structured = ROOT / "data" / "structured"
    formulas = read_json(structured / "Evolution_formula_library.json").get("formulas", [])
    tables = read_json(structured / "Evolution_table_library.json").get("tables", [])
    figures_payload = read_json(structured / "Evolution_figure_library.json").get("figures", [])
    figures = list(figures_payload.values()) if isinstance(figures_payload, dict) else figures_payload
    examples = read_json(structured / "example_library.json").get("examples", [])
    return formulas, tables, figures, examples


def records_for_chapter(records: list[dict[str, Any]], chapter: str, *, source_owned: bool) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        owner = record.get("source", {}).get("chapter") if source_owned else record.get("chapter")
        if owner == chapter:
            selected.append(sanitize_paths(copy.deepcopy(record)))
    return selected


def resolve_figure_source(asset_path: str) -> Path:
    name = Path(asset_path).name
    candidates = [
        ROOT / "data" / "textbook" / "figures" / name,
        ROOT / "data" / "figures" / name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Evolution figure asset not found: {asset_path}")


def copy_section(
    section: str,
    output: Path,
    formulas: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> dict[str, int]:
    chapter = chapter_id(section)
    directory = output / delivery_dir_name(section)
    structured_dir = directory / "structured"
    libraries_dir = directory / "libraries"
    figures_dir = directory / "figures"
    structured_dir.mkdir(parents=True)
    libraries_dir.mkdir()
    figures_dir.mkdir()

    source_chunks: list[Path] = []
    for path in sorted((ROOT / "data" / "structured").glob(f"{chapter}_*.json")):
        payload = read_json(path)
        if payload.get("metadata", {}).get("chapter") == chapter:
            source_chunks.append(path)
    if not source_chunks:
        raise RuntimeError(f"No structured chunks found for {chapter}")

    structured_paths: list[str] = []
    for source in source_chunks:
        target = structured_dir / source.name
        write_json(target, sanitize_paths(read_json(source)))
        structured_paths.append(f"structured/{source.name}")

    selected_formulas = records_for_chapter(formulas, chapter, source_owned=True)
    selected_tables = records_for_chapter(tables, chapter, source_owned=True)
    selected_figures = records_for_chapter(figures, chapter, source_owned=False)
    selected_examples = records_for_chapter(examples, chapter, source_owned=False)

    textbook_source = ROOT / "data" / "textbook" / f"{chapter}_textbook.md"
    if not textbook_source.is_file():
        raise FileNotFoundError(textbook_source)
    textbook = textbook_source.read_text(encoding="utf-8")
    linked_images = set(IMAGE_RE.findall(textbook))
    copied_images: set[str] = set()

    for figure in selected_figures:
        source = resolve_figure_source(str(figure.get("asset_path") or ""))
        target = figures_dir / source.name
        if not target.exists():
            shutil.copy2(source, target)
        copied_images.add(f"figures/{source.name}")
        figure["asset_path"] = f"../figures/{source.name}"
        figure["package_asset_path"] = f"figures/{source.name}"

    for relative in linked_images:
        source = ROOT / "data" / "textbook" / relative
        if not source.is_file():
            raise FileNotFoundError(f"Textbook references missing image: {source}")
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        copied_images.add(relative)

    write_json(libraries_dir / "formulas.json", {
        "book": BOOK, "chapter": chapter, "asset_type": "formula", "count": len(selected_formulas), "formulas": selected_formulas,
    })
    write_json(libraries_dir / "tables.json", {
        "book": BOOK, "chapter": chapter, "asset_type": "table", "count": len(selected_tables), "tables": selected_tables,
    })
    write_json(libraries_dir / "figures.json", {
        "book": BOOK, "chapter": chapter, "asset_type": "figure", "count": len(selected_figures), "figures": selected_figures,
    })
    write_json(libraries_dir / "examples.json", {
        "book": BOOK, "chapter": chapter, "asset_type": "example", "count": len(selected_examples), "examples": selected_examples,
    })
    (directory / "textbook.md").write_text(textbook, encoding="utf-8")

    manifest = {
        "book": BOOK,
        "chapter": chapter,
        "address_base": "this section directory",
        "textbook": "textbook.md",
        "structured": structured_paths,
        "libraries": {
            "formulas": "libraries/formulas.json",
            "tables": "libraries/tables.json",
            "figures": "libraries/figures.json",
            "examples": "libraries/examples.json",
        },
        "figures": sorted(copied_images),
    }
    write_json(directory / "manifest.json", manifest)
    return {
        "structured": len(source_chunks),
        "formulas": len(selected_formulas),
        "tables": len(selected_tables),
        "figures": len(selected_figures),
        "examples": len(selected_examples),
        "image_files": len(copied_images),
    }


def source_totals() -> Counter[str]:
    formulas, tables, figures, examples = load_libraries()
    valid_chapters = {chapter_id(section) for section in SECTIONS}
    counts: Counter[str] = Counter()
    counts["structured"] = sum(
        1
        for path in (ROOT / "data" / "structured").glob("Evolution_*_*.json")
        if read_json(path).get("metadata", {}).get("chapter") in valid_chapters
    )
    counts["formulas"] = sum(1 for item in formulas if item.get("source", {}).get("chapter") in valid_chapters)
    counts["tables"] = sum(1 for item in tables if item.get("source", {}).get("chapter") in valid_chapters)
    counts["figures"] = sum(1 for item in figures if item.get("chapter") in valid_chapters)
    counts["examples"] = sum(1 for item in examples if item.get("chapter") in valid_chapters)
    counts["sections"] = len(SECTIONS)
    return counts


def build(output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing delivery directory: {output}")
    formulas, tables, figures, examples = load_libraries()
    output.mkdir(parents=True)
    per_section: dict[str, dict[str, int]] = {}
    totals: Counter[str] = Counter()
    for section in SECTIONS:
        counts = copy_section(section, output, formulas, tables, figures, examples)
        per_section[section] = counts
        totals.update(counts)
    manifest = {
        "book": BOOK,
        "format": "uncompressed chapter-separated delivery package",
        "section_count": len(SECTIONS),
        "sections": [f"{delivery_dir_name(section)}/manifest.json" for section in SECTIONS],
        "totals": dict(totals),
        "per_section": per_section,
    }
    write_json(output / "manifest.json", manifest)
    lines = [
        "# Evolution delivery package",
        "",
        "This package contains 30 chapters and 6 appendices. Each directory is self-contained and uses package-relative paths.",
        "",
        "## Contents",
        "",
    ]
    lines.extend(
        f"- [{chapter_id(section)}]({delivery_dir_name(section)}/textbook.md)"
        for section in SECTIONS
    )
    lines.append("")
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")


def verify(output: Path) -> dict[str, Any]:
    errors: list[str] = []
    package_totals: Counter[str] = Counter()
    if not (output / "manifest.json").is_file():
        raise FileNotFoundError(output / "manifest.json")

    for section in SECTIONS:
        directory = output / delivery_dir_name(section)
        manifest_path = directory / "manifest.json"
        if not manifest_path.is_file():
            errors.append(f"{section}: missing manifest.json")
            continue
        manifest = read_json(manifest_path)
        required = [manifest.get("textbook"), *manifest.get("structured", []), *manifest.get("libraries", {}).values(), *manifest.get("figures", [])]
        for relative in required:
            if not relative or not (directory / relative).is_file():
                errors.append(f"{section}: missing {relative}")
        textbook_path = directory / "textbook.md"
        if textbook_path.is_file():
            textbook = textbook_path.read_text(encoding="utf-8")
            for relative in IMAGE_RE.findall(textbook):
                if not (directory / relative).is_file():
                    errors.append(f"{section}: broken textbook image {relative}")
        for file_name, key in (("formulas.json", "formulas"), ("tables.json", "tables"), ("figures.json", "figures"), ("examples.json", "examples")):
            path = directory / "libraries" / file_name
            if not path.is_file():
                continue
            payload = read_json(path)
            records = payload.get(key, [])
            if payload.get("count") != len(records):
                errors.append(f"{section}: count mismatch in {file_name}")
            package_totals[key] += len(records)
            for value in iter_strings(payload):
                if ABSOLUTE_WINDOWS_PATH_RE.match(value):
                    errors.append(f"{section}: absolute path remains in {file_name}")
                    break
        for path in (directory / "structured").glob("*.json"):
            package_totals["structured"] += 1
            for value in iter_strings(read_json(path)):
                if ABSOLUTE_WINDOWS_PATH_RE.match(value):
                    errors.append(f"{section}: absolute path remains in {path.name}")
                    break

    package_totals["sections"] = len(SECTIONS)
    expected = source_totals()
    for key in ("structured", "formulas", "tables", "figures", "examples", "sections"):
        if package_totals[key] != expected[key]:
            errors.append(f"total {key}={package_totals[key]}, expected {expected[key]}")
    result = {
        "output": str(output),
        "valid": not errors,
        "package_totals": dict(package_totals),
        "source_totals": dict(expected),
        "errors": errors,
    }
    write_json(output / "verification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Pack" / "EvoPack")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        build(args.output)
    result = verify(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
