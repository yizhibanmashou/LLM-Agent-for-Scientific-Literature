"""Build and validate static assets for the Study Reader Cloudflare Worker."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
READER_DIR = REPO_ROOT / "study_reader"
OUTPUT_DIR = REPO_ROOT / ".cloudflare-assets"
GENERATED_DIR = READER_DIR / "data" / "generated"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def referenced_images(markdown: str, chapter_payload: dict[str, Any]) -> set[str]:
    paths = {match.group("path").split("#", 1)[0].strip() for match in IMAGE_RE.finditer(markdown)}
    for asset in chapter_payload.get("assets", []):
        if not isinstance(asset, dict):
            continue
        path = str(asset.get("image_path") or asset.get("asset_path") or "").strip()
        if path:
            paths.add(path)
    return {path for path in paths if path and "://" not in path and not path.startswith("data:")}


def resolve_textbook_asset(markdown_path: Path, relative: str) -> tuple[Path, Path]:
    clean = relative.split("?", 1)[0].split("#", 1)[0].strip()
    if clean.startswith("/data/") or clean.startswith("data/"):
        source = (REPO_ROOT / clean.lstrip("/")).resolve()
    else:
        source = (markdown_path.parent / clean).resolve()
    data_root = (REPO_ROOT / "data").resolve()
    try:
        packaged_relative = source.relative_to(data_root)
    except ValueError as exc:
        raise ValueError(f"Textbook asset escapes data/: {relative}") from exc
    return source, Path("data") / packaged_relative


def build() -> dict[str, Any]:
    config = read_json(READER_DIR / "source_config.json")
    strict_books = [str(book).strip() for book in config.get("strict_math_books", []) if str(book).strip()]
    if strict_books:
        subprocess.run(
            ["node", "scripts/validate_textbook_math.js", "--books", ",".join(strict_books)],
            cwd=REPO_ROOT,
            check=True,
        )

    dataset = read_json(GENERATED_DIR / "study_dataset.json")
    chapters = dataset.get("chapters") if isinstance(dataset.get("chapters"), list) else []
    if len(chapters) != 68:
        raise ValueError(f"Expected 68 configured chapters/appendices, found {len(chapters)}")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    for filename in ("index.html", "math_parser.js", "app.js", "styles.css"):
        copy_file(READER_DIR / filename, OUTPUT_DIR / filename)
    for filename in ("study_dataset.json", "prerequisite_audit.json"):
        copy_file(GENERATED_DIR / filename, OUTPUT_DIR / "data" / "generated" / filename)

    copied_images: set[Path] = set()
    for chapter in chapters:
        chapter_id = str(chapter.get("id") or "")
        data_source = GENERATED_DIR / "chapters" / f"{chapter_id}.json"
        data_target = OUTPUT_DIR / "data" / "generated" / "chapters" / data_source.name
        copy_file(data_source, data_target)
        payload = read_json(data_source)

        markdown_source = REPO_ROOT / str(chapter.get("markdown_path") or "").lstrip("/")
        markdown_target = OUTPUT_DIR / "data" / "textbook" / markdown_source.name
        copy_file(markdown_source, markdown_target)
        markdown = markdown_source.read_text(encoding="utf-8-sig")
        for relative in referenced_images(markdown, payload):
            source, packaged_relative = resolve_textbook_asset(markdown_source, relative)
            target = OUTPUT_DIR / packaged_relative
            if target not in copied_images:
                copy_file(source, target)
                copied_images.add(target)

    files = sorted(path for path in OUTPUT_DIR.rglob("*") if path.is_file())
    manifest = {
        "schema": "study_reader_assets.v1",
        "books": [book.get("id") for book in dataset.get("books", [])],
        "chapter_count": len(chapters),
        "image_count": len(copied_images),
        "file_count": len(files) + 1,
        "files": {
            path.relative_to(OUTPUT_DIR).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files
        },
    }
    manifest_path = OUTPUT_DIR / "asset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    manifest = build()
    print(json.dumps({key: value for key, value in manifest.items() if key != "files"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
