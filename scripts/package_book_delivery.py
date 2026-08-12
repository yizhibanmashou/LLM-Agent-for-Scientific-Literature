"""Create a verified, self-contained structured textbook package for a book or chapter range."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PACK_ROOT = ROOT / "Pack"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
SECTION_RE = re.compile(r"^(chapter|appendix)(\d+)$", re.IGNORECASE)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_numbers(raw: str) -> list[int]:
    values: set[int] = set()
    for part in str(raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if match:
            start, end = map(int, match.groups())
            if start > end:
                raise ValueError(f"Invalid descending range: {part}")
            values.update(range(start, end + 1))
        elif part.isdigit():
            values.add(int(part))
        else:
            raise ValueError(f"Invalid section selector: {part}")
    return sorted(values)


def selected_sections(book: str, chapters: str, appendices: str) -> list[str]:
    sections = [f"chapter{number}" for number in parse_numbers(chapters)]
    sections.extend(f"appendix{number}" for number in parse_numbers(appendices))
    if sections:
        return sections
    discovered: set[str] = set()
    pattern = re.compile(rf"^{re.escape(book)}_((?:chapter|appendix)\d+)_\d+\.json$", re.IGNORECASE)
    for path in (DATA / "structured").glob(f"{book}_*.json"):
        match = pattern.fullmatch(path.name)
        if match:
            discovered.add(match.group(1).lower())
    return sorted(discovered, key=section_sort_key)


def section_sort_key(section: str) -> tuple[int, int]:
    match = SECTION_RE.fullmatch(section)
    if not match:
        return (9, 9999)
    return (0 if match.group(1).lower() == "chapter" else 1, int(match.group(2)))


def chapter_id(book: str, section: str) -> str:
    return f"{book}_{section.lower()}"


def folder_name(section: str) -> str:
    match = SECTION_RE.fullmatch(section)
    if not match:
        raise ValueError(section)
    return f"{match.group(1).lower()}{int(match.group(2)):02d}"


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        normalized = value.replace("\\", "/")
        if re.match(r"^[A-Za-z]:/", normalized) or normalized.startswith("/"):
            return Path(normalized).name
    return value


def load_library(book: str, kind: str, *, data_root: Path = DATA) -> list[dict[str, Any]]:
    dedicated = data_root / "structured" / f"{book}_{kind}_library.json"
    shared = data_root / "structured" / f"{kind}_library.json"
    path = dedicated if dedicated.is_file() else shared
    if not path.is_file():
        return []
    payload = read_json(path)
    key = f"{kind}s" if kind != "example" else "examples"
    rows = payload.get(key, []) if isinstance(payload, dict) else []
    if isinstance(rows, dict):
        rows = list(rows.values())
    return [row for row in rows if isinstance(row, dict)]


def record_chapter(record: dict[str, Any]) -> str:
    source = record.get("source") if isinstance(record.get("source"), dict) else {}
    return str(record.get("chapter") or source.get("chapter") or "")


def resolve_image(relative: str, *, data_root: Path = DATA) -> Path:
    clean = relative.split("?", 1)[0].split("#", 1)[0].strip()
    if clean.startswith("/data/") or clean.startswith("data/"):
        source = (data_root.parent / clean.lstrip("/")).resolve()
    else:
        source = (data_root / "textbook" / clean).resolve()
    root = data_root.resolve()
    try:
        source.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Image path escapes data/: {relative}") from exc
    return source


def source_snapshot(book: str, sections: list[str], *, data_root: Path = DATA) -> dict[str, Any]:
    """Fingerprint exactly the formal inputs used by the selected package."""
    entries: dict[str, str] = {}
    libraries = {kind: load_library(book, kind, data_root=data_root) for kind in ("formula", "table", "figure", "example")}
    selected_chapters = {chapter_id(book, section).lower() for section in sections}
    image_relatives: set[str] = set()
    for section in sections:
        current = chapter_id(book, section)
        units = sorted((data_root / "structured").glob(f"{current}_*.json"))
        units = [path for path in units if re.search(r"_\d{3}\.json$", path.name)]
        if not units:
            raise FileNotFoundError(f"No structured units for {current}")
        for path in units:
            entries[f"structured/{path.name}"] = sha256(path)
        textbook = data_root / "textbook" / f"{current}_textbook.md"
        if not textbook.is_file():
            raise FileNotFoundError(textbook)
        entries[f"textbook/{textbook.name}"] = sha256(textbook)
        image_relatives.update(match.group("path") for match in IMAGE_RE.finditer(textbook.read_text(encoding="utf-8-sig")))
    for kind, rows in libraries.items():
        selected = [sanitize(copy.deepcopy(row)) for row in rows if record_chapter(row).lower() in selected_chapters]
        payload = json.dumps(selected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        entries[f"resources/{kind}"] = hashlib.sha256(payload).hexdigest()
        if kind == "figure":
            for row in selected:
                relative = str(row.get("asset_path") or row.get("image_path") or "").strip()
                if relative:
                    image_relatives.add(relative)
    for relative in sorted(image_relatives):
        if "://" in relative or relative.startswith("data:"):
            continue
        path = resolve_image(relative, data_root=data_root)
        if not path.is_file():
            raise FileNotFoundError(f"Missing formal image input: {path}")
        entries[f"images/{path.relative_to(data_root).as_posix()}"] = sha256(path)
    digest = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"schema": "formal_data_source.v1", "sha256": digest, "entry_count": len(entries), "entries": entries}


def source_snapshot_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return bool(expected) and expected.get("schema") == actual.get("schema") and expected.get("sha256") == actual.get("sha256")


def release_provenance(report_path: Path | None) -> dict[str, Any] | None:
    if report_path is None:
        return None
    path = report_path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        relative = path.relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("Provenance report must stay inside the repository") from exc
    report = read_json(path)
    automated_valid = bool(report.get("automated_valid", report.get("automatic_verification_valid", report.get("valid", False))))
    installed = bool(report.get("installed", automated_valid))
    waived = bool(report.get("automatic_findings_waived", False))
    if not installed or not automated_valid or waived:
        raise ValueError("Release Pack requires an installed, automatically valid, waiver-free audit report")
    return {
        "status": "automatic_valid",
        "installed": installed,
        "automated_valid": automated_valid,
        "automatic_findings_waived": False,
        "waived_findings_count": 0,
        "report": relative,
        "report_sha256": sha256(path),
    }


def copy_section(book: str, section: str, output: Path, libraries: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    current = chapter_id(book, section)
    destination = output / folder_name(section)
    structured_target = destination / "structured"
    structured_target.mkdir(parents=True)

    structured_files = sorted((DATA / "structured").glob(f"{current}_*.json"))
    structured_files = [path for path in structured_files if re.search(r"_\d{3}\.json$", path.name)]
    if not structured_files:
        raise FileNotFoundError(f"No structured units for {current}")
    for source in structured_files:
        write_json(structured_target / source.name, sanitize(read_json(source)))

    selected: dict[str, list[dict[str, Any]]] = {}
    for kind, rows in libraries.items():
        selected[kind] = [sanitize(copy.deepcopy(row)) for row in rows if record_chapter(row).lower() == current.lower()]
        write_json(
            destination / "libraries" / f"{kind}_library.json",
            {"book": book, "chapter": current, "count": len(selected[kind]), f"{kind}s" if kind != "example" else "examples": selected[kind]},
        )

    textbook_source = DATA / "textbook" / f"{current}_textbook.md"
    if not textbook_source.is_file():
        raise FileNotFoundError(textbook_source)
    textbook = textbook_source.read_text(encoding="utf-8-sig")
    image_relatives = {match.group("path") for match in IMAGE_RE.finditer(textbook)}
    for figure in selected["figure"]:
        relative = str(figure.get("asset_path") or figure.get("image_path") or "").strip()
        if relative:
            image_relatives.add(relative)

    copied_images: list[str] = []
    for relative in sorted(image_relatives):
        if "://" in relative or relative.startswith("data:"):
            continue
        source = resolve_image(relative)
        if not source.is_file():
            raise FileNotFoundError(f"Missing image for {current}: {source}")
        target = destination / "figures" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_images.append(f"figures/{source.name}")

    packaged_textbook = re.sub(
        r"(!\[[^\]]*\]\()([^)]+)(\))",
        lambda match: f"{match.group(1)}figures/{Path(match.group(2).split('#', 1)[0]).name}{match.group(3)}"
        if "://" not in match.group(2) and not match.group(2).startswith("data:")
        else match.group(0),
        textbook,
    )
    (destination / "textbook.md").write_text(packaged_textbook, encoding="utf-8")
    counts = {
        "structured": len(structured_files),
        "formulas": len(selected["formula"]),
        "tables": len(selected["table"]),
        "figures": len(selected["figure"]),
        "examples": len(selected["example"]),
        "image_files": len(copied_images),
    }
    write_json(destination / "manifest.json", {"book": book, "chapter": current, "counts": counts, "textbook": "textbook.md", "figures": copied_images})
    return counts


def file_hashes(root: Path, *, exclude: Iterable[str] = ()) -> dict[str, str]:
    excluded = set(exclude)
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    }


def verify(output: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = read_json(manifest_path)
    expected_hashes = manifest.get("sha256", {})
    actual_hashes = file_hashes(output, exclude={"verification.json", "manifest.json"})
    if expected_hashes != actual_hashes:
        errors.append("file hash manifest differs from package contents")
    expected_book = str(manifest.get("book") or "")
    if manifest.get("schema") == "book_delivery.v2":
        sections = [str(item) for item in manifest.get("selected_sections", [])]
        expected_source = manifest.get("source_snapshot") if isinstance(manifest.get("source_snapshot"), dict) else {}
        try:
            current_source = source_snapshot(expected_book, sections)
            if not source_snapshot_matches(expected_source, current_source):
                errors.append("package is stale: formal data source fingerprint differs")
        except Exception as exc:
            errors.append(f"formal data source fingerprint could not be checked: {exc}")
        provenance = manifest.get("release_provenance")
        if not isinstance(provenance, dict):
            errors.append("release Pack has no accuracy-audit provenance")
        elif not provenance.get("installed") or not provenance.get("automated_valid") or provenance.get("automatic_findings_waived"):
            errors.append("release Pack provenance is not installed, automatic-valid, and waiver-free")
        elif provenance.get("report"):
            report_path = ROOT / str(provenance["report"])
            if not report_path.is_file():
                errors.append("release provenance report is missing")
            elif sha256(report_path) != provenance.get("report_sha256"):
                errors.append("release provenance report changed after packaging")
    for section_manifest in manifest.get("sections", []):
        directory = output / Path(section_manifest).parent
        if not (directory / "textbook.md").is_file():
            errors.append(f"{directory.name}: missing textbook.md")
            continue
        text = (directory / "textbook.md").read_text(encoding="utf-8")
        for relative in IMAGE_RE.findall(text):
            if "://" not in relative and not (directory / relative).is_file():
                errors.append(f"{directory.name}: broken image {relative}")
        local_manifest = read_json(directory / "manifest.json") if (directory / "manifest.json").is_file() else {}
        expected_chapter = str(local_manifest.get("chapter") or "")
        figure_paths = local_manifest.get("figures", [])
        if isinstance(figure_paths, list) and len(figure_paths) != len(set(map(str, figure_paths))):
            errors.append(f"{directory.name}: duplicate figure file")
        for path in directory.rglob("*.json"):
            payload = read_json(path)
            for value in iter_strings(payload):
                normalized = value.replace("\\", "/")
                if re.match(r"^[A-Za-z]:/", normalized):
                    errors.append(f"{path.relative_to(output)}: absolute path")
                    break
            if path.parent.name == "structured":
                unit_id = str(payload.get("id") or "")
                metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
                source_chapter = str(metadata.get("chapter") or "")
                if not unit_id.lower().startswith(expected_chapter.lower() + "_"):
                    errors.append(f"{path.relative_to(output)}: cross-book/unit pollution")
                if source_chapter and source_chapter.lower() != expected_chapter.lower():
                    errors.append(f"{path.relative_to(output)}: chapter metadata mismatch")
            if path.parent.name == "libraries":
                rows = next((value for key, value in payload.items() if key in {"formulas", "tables", "figures", "examples"}), [])
                rows = rows if isinstance(rows, list) else []
                identities: list[str] = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    owner = record_chapter(row)
                    if owner and owner.lower() != expected_chapter.lower():
                        errors.append(f"{path.relative_to(output)}: cross-book resource {owner}")
                    identities.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
                if len(identities) != len(set(identities)):
                    errors.append(f"{path.relative_to(output)}: duplicate resource record")
        if expected_book and expected_chapter and not expected_chapter.lower().startswith(expected_book.lower() + "_"):
            errors.append(f"{directory.name}: package book/chapter mismatch")
    result = {"valid": not errors, "output": str(output), "book": manifest.get("book"), "section_count": len(manifest.get("sections", [])), "errors": errors}
    write_json(output / "verification.json", result)
    return result


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def update_pack_manifest(pack_root: Path) -> None:
    packages = []
    for path in sorted(pack_root.iterdir()):
        if not path.is_dir() or not (path / "manifest.json").is_file() or not (path / "verification.json").is_file():
            continue
        verification = read_json(path / "verification.json")
        manifest = read_json(path / "manifest.json")
        packages.append({"directory": path.name, "book": manifest.get("book"), "section_count": len(manifest.get("sections", [])), "valid": verification.get("valid"), "tree_sha256": hashlib.sha256(json.dumps(file_hashes(path), sort_keys=True).encode()).hexdigest()})
    write_json(pack_root / "manifest.json", {"schema": "book_pack_index.v1", "packages": packages})


def build(book: str, sections: list[str], output: Path, *, replace: bool, provenance_report: Path | None = None) -> dict[str, Any]:
    output = output.resolve()
    pack_root = PACK_ROOT.resolve()
    if output != pack_root and pack_root not in output.parents:
        raise ValueError(f"Output must stay inside {pack_root}: {output}")
    if output.exists() and not replace:
        raise FileExistsError(f"Refusing to overwrite existing package without --replace: {output}")
    staging = (ROOT / "tmp" / "pack_staging" / f"{output.name}.new").resolve()
    allowed_tmp = (ROOT / "tmp" / "pack_staging").resolve()
    if allowed_tmp not in staging.parents:
        raise ValueError(staging)
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    libraries = {kind: load_library(book, kind) for kind in ("formula", "table", "figure", "example")}
    formal_source = source_snapshot(book, sections)
    provenance = release_provenance(provenance_report)
    totals = {key: 0 for key in ("structured", "formulas", "tables", "figures", "examples", "image_files")}
    per_section = {}
    for section in sections:
        counts = copy_section(book, section, staging, libraries)
        per_section[section] = counts
        for key, value in counts.items():
            totals[key] += value
    section_manifests = [f"{folder_name(section)}/manifest.json" for section in sections]
    hashes = file_hashes(staging)
    write_json(staging / "manifest.json", {"schema": "book_delivery.v2", "book": book, "selected_sections": sections, "sections": section_manifests, "totals": totals, "per_section": per_section, "source_snapshot": formal_source, "release_provenance": provenance, "sha256": hashes})
    result = verify(staging)
    if not result["valid"]:
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    output.parent.mkdir(parents=True, exist_ok=True)
    backup = output.with_name(f"{output.name}.previous")
    if backup.exists():
        shutil.rmtree(backup)
    if output.exists():
        os.replace(output, backup)
    try:
        os.replace(staging, output)
    except Exception:
        if backup.exists() and not output.exists():
            os.replace(backup, output)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    result = verify(output)
    update_pack_manifest(output.parent)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", required=True)
    parser.add_argument("--chapters", default="", help="Numbers/ranges such as 3-8,12.")
    parser.add_argument("--appendices", default="", help="Appendix numbers/ranges.")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--provenance-report", type=Path, default=None, help="Verified install/audit report recorded in the package manifest.")
    args = parser.parse_args()
    output = args.output or (PACK_ROOT / f"{args.book}Pack")
    if args.verify_only:
        result = verify(output)
    else:
        sections = selected_sections(args.book, args.chapters, args.appendices)
        if not sections:
            raise SystemExit(f"No structured sections found for {args.book}")
        result = build(args.book, sections, output, replace=args.replace, provenance_report=args.provenance_report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
