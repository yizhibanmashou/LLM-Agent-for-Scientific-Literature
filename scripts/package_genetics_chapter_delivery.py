#!/usr/bin/env python3
"""Create an uncompressed, chapter-oriented delivery package for Genetics.

The package intentionally contains only package-relative addresses.  It is a
delivery copy: source datasets are never modified, and an existing output
directory is refused so that a prior delivery cannot be overwritten.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BOOK = "Genetics"
CHAPTER_RE = re.compile(r"Genetics_chapter(\d+)\.pdf", re.IGNORECASE)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((figures/[^)]+)\)")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chapter_name(number: int) -> str:
    return f"{BOOK}_chapter{number}"


def chapter_number(value: Any) -> int | None:
    match = CHAPTER_RE.search(str(value).replace("\\", "/"))
    return int(match.group(1)) if match else None


def rel_from_library(folder: str, filename: str) -> str:
    return f"../{folder}/{filename}"


def strip_provenance_paths(record: dict[str, Any]) -> None:
    """Remove addresses to excluded source/PDF/OCR evidence from delivery copies."""
    for key in ("source_pdf", "package_source_pdf", "source_paddle_raw", "package_source_paddle_raw"):
        record.pop(key, None)
    for container_key in ("source", "source_evidence"):
        container = record.get(container_key)
        if isinstance(container, dict):
            for key in ("source_pdf", "package_source_pdf", "api_response", "package_api_response"):
                container.pop(key, None)


def copy_structured_chunks(number: int, chapter_dir: Path) -> list[str]:
    target = chapter_dir / "structured"
    target.mkdir()
    selected: list[Path] = []
    for path in sorted((ROOT / "data" / "structured").glob("Genetics_chapter*.json")):
        payload = read_json(path)
        if payload.get("metadata", {}).get("chapter") == chapter_name(number):
            selected.append(path)

    if not selected:
        raise RuntimeError(f"No structured chunks found for {chapter_name(number)}")

    paths: list[str] = []
    for source in selected:
        payload = read_json(source)
        metadata = payload.setdefault("metadata", {})
        metadata.pop("source_file", None)
        provenance = metadata.get("rebuild_provenance")
        if isinstance(provenance, dict):
            provenance.pop("source", None)
        output = target / source.name
        write_json(output, payload)
        paths.append(f"structured/{source.name}")
    return paths


def package_chapter(
    number: int,
    formulas: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    output: Path,
) -> dict[str, int]:
    name = chapter_name(number)
    chapter_dir = output / f"chapter{number:02d}"
    chapter_dir.mkdir()
    (chapter_dir / "libraries").mkdir()
    (chapter_dir / "figures").mkdir()

    structured_paths = copy_structured_chunks(number, chapter_dir)
    selected_formulas = [dict(item) for item in formulas if item.get("source", {}).get("chapter") == name]
    selected_tables = [dict(item) for item in tables if item.get("source", {}).get("chapter") == name]
    selected_figures = [dict(item) for item in figures if item.get("chapter") == name]
    selected_examples = [dict(item) for item in examples if item.get("chapter") == name]

    for item in selected_formulas + selected_tables + selected_figures:
        strip_provenance_paths(item)

    # A package-local formula/table/figure library is a small, independently usable file.
    write_json(chapter_dir / "libraries" / "formulas.json", {
        "book": BOOK, "chapter": name, "asset_type": "formula", "count": len(selected_formulas), "formulas": selected_formulas,
    })
    write_json(chapter_dir / "libraries" / "tables.json", {
        "book": BOOK, "chapter": name, "asset_type": "table", "count": len(selected_tables), "tables": selected_tables,
    })
    write_json(chapter_dir / "libraries" / "figures.json", {
        "book": BOOK, "chapter": name, "asset_type": "figure", "count": len(selected_figures), "figures": selected_figures,
    })
    write_json(chapter_dir / "libraries" / "examples.json", {
        "book": BOOK, "chapter": name, "asset_type": "example", "count": len(selected_examples), "examples": selected_examples,
    })

    # Make image addresses valid without changing textbook Markdown links.
    textbook_source = ROOT / "data" / "textbook" / f"{name}_textbook.md"
    textbook = textbook_source.read_text(encoding="utf-8")
    image_paths = sorted(set(IMAGE_RE.findall(textbook)))
    for image_path in image_paths:
        source = ROOT / "data" / "textbook" / image_path
        if not source.is_file():
            raise FileNotFoundError(f"Textbook references a missing image: {source}")
        destination = chapter_dir / image_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    # Library figure records point to their local asset from the libraries/ directory.
    for item in selected_figures:
        asset = Path(str(item.get("asset_path", ""))).name
        if asset:
            item["asset_path"] = rel_from_library("figures", asset)
            item["package_asset_path"] = f"figures/{asset}"
    write_json(chapter_dir / "libraries" / "figures.json", {
        "book": BOOK, "chapter": name, "asset_type": "figure", "count": len(selected_figures), "figures": selected_figures,
    })
    (chapter_dir / "textbook.md").write_text(textbook, encoding="utf-8")

    manifest = {
        "book": BOOK,
        "chapter": name,
        "address_base": "this chapter directory",
        "textbook": "textbook.md",
        "structured": structured_paths,
        "libraries": {
            "formulas": "libraries/formulas.json",
            "tables": "libraries/tables.json",
            "figures": "libraries/figures.json",
            "examples": "libraries/examples.json",
        },
        "figures": image_paths,
    }
    write_json(chapter_dir / "manifest.json", manifest)
    return {
        "structured": len(structured_paths), "formulas": len(selected_formulas), "tables": len(selected_tables),
        "figures": len(selected_figures), "examples": len(selected_examples), "image_files": len(image_paths),
    }


def package(output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing delivery directory: {output}")

    structured = ROOT / "data" / "structured"
    formulas = read_json(structured / "Genetics_formula_library.json")["formulas"]
    tables = read_json(structured / "Genetics_table_library.json")["tables"]
    figures = read_json(structured / "Genetics_figure_library.json")["figures"]
    examples = read_json(structured / "example_library.json")["examples"]
    output.mkdir(parents=True)

    per_chapter = {str(number): package_chapter(number, formulas, tables, figures, examples, output) for number in range(1, 28)}
    totals = Counter()
    for counts in per_chapter.values():
        totals.update(counts)
    manifest = {
        "book": BOOK,
        "format": "uncompressed chapter delivery package",
        "chapter_count": 27,
        "chapters": [f"chapter{number:02d}/manifest.json" for number in range(1, 28)],
        "totals": dict(totals),
    }
    write_json(output / "manifest.json", manifest)
    lines = [
        "# Genetics chapter delivery package", "",
        "This is an uncompressed, chapter-separated delivery package. Each `chapterNN/` folder is self-contained; open its `README.md` or `textbook.md`.",
        "", "## Chapter index", "",
    ]
    lines.extend(f"- [Chapter {number}](chapter{number:02d}/textbook.md)" for number in range(1, 28))
    lines.extend(["", "The chapter manifests and asset-library records use only paths relative to their own chapter folder.", ""])
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return manifest


def iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from iter_string_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_string_values(nested)
    elif isinstance(value, str):
        yield value


def verify(output: Path) -> dict[str, Any]:
    if not output.is_dir():
        raise FileNotFoundError(output)
    root_manifest = read_json(output / "manifest.json")
    errors: list[str] = []
    totals = Counter()
    for number in range(1, 28):
        directory = output / f"chapter{number:02d}"
        manifest_path = directory / "manifest.json"
        if not manifest_path.is_file():
            errors.append(f"chapter {number}: missing manifest")
            continue
        manifest = read_json(manifest_path)
        for relative in [manifest["textbook"], *manifest["structured"], *manifest["libraries"].values(), *manifest["figures"]]:
            if not (directory / relative).is_file():
                errors.append(f"chapter {number}: missing {relative}")
        textbook = (directory / "textbook.md").read_text(encoding="utf-8")
        for image in IMAGE_RE.findall(textbook):
            if not (directory / image).is_file():
                errors.append(f"chapter {number}: textbook image link is broken: {image}")
        for file_name, plural in [("formulas.json", "formulas"), ("tables.json", "tables"), ("figures.json", "figures"), ("examples.json", "examples")]:
            library_path = directory / "libraries" / file_name
            library = read_json(library_path)
            totals[plural] += library["count"]
            if library["count"] != len(library[plural]):
                errors.append(f"chapter {number}: count mismatch in {file_name}")
            for value in iter_string_values(library):
                if re.search(r"[A-Za-z]:[\\/]", value):
                    errors.append(f"chapter {number}: absolute Windows path remains in {file_name}")
                    break
        figure_library = read_json(directory / "libraries" / "figures.json")
        for figure in figure_library["figures"]:
            path = (directory / "libraries" / figure["asset_path"]).resolve()
            if not path.is_file():
                errors.append(f"chapter {number}: broken figure-library asset path {figure['asset_path']}")
    totals["chapters"] = 27
    if root_manifest["chapter_count"] != 27:
        errors.append("root manifest chapter count is not 27")
    expected = {"formulas": 1815, "tables": 72, "figures": 152}
    for key, count in expected.items():
        if totals[key] != count:
            errors.append(f"package total {key}={totals[key]}, expected {count}")
    result = {"output": str(output), "valid": not errors, "totals": dict(totals), "errors": errors}
    write_json(output / "verification.json", result)
    return result


def strip_existing_provenance(output: Path) -> None:
    """Apply the no-source-files delivery policy to an already-built package."""
    for number in range(1, 28):
        chapter_dir = output / f"chapter{number:02d}"
        for file_name, plural in [("formulas.json", "formulas"), ("tables.json", "tables"), ("figures.json", "figures")]:
            path = chapter_dir / "libraries" / file_name
            library = read_json(path)
            for record in library[plural]:
                strip_provenance_paths(record)
            write_json(path, library)
        for path in (chapter_dir / "structured").glob("*.json"):
            payload = read_json(path)
            metadata = payload.get("metadata")
            if isinstance(metadata, dict):
                metadata.pop("source_file", None)
                provenance = metadata.get("rebuild_provenance")
                if isinstance(provenance, dict):
                    provenance.pop("source", None)
            write_json(path, payload)
        manifest_path = chapter_dir / "manifest.json"
        manifest = read_json(manifest_path)
        manifest.pop("source_pdfs", None)
        manifest.pop("paddleocr_api_evidence", None)
        write_json(manifest_path, manifest)
        for name in ("source", "source_pdf", "evidence"):
            path = chapter_dir / name
            if path.exists():
                shutil.rmtree(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Genetics_chapter_delivery")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--strip-provenance", action="store_true")
    args = parser.parse_args()
    if args.strip_provenance:
        strip_existing_provenance(args.output)
        result = verify(args.output)
    elif args.verify_only:
        result = verify(args.output)
    else:
        package(args.output)
        result = verify(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
