"""Build the static-asset directory for the Study Reader Cloudflare Worker."""

from __future__ import annotations

import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
READER_DIR = REPO_ROOT / "study_reader"
OUTPUT_DIR = REPO_ROOT / ".cloudflare-assets"


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir()
    for filename in ("index.html", "app.js", "styles.css"):
        shutil.copy2(READER_DIR / filename, OUTPUT_DIR / filename)

    copy_tree(READER_DIR / "data" / "generated", OUTPUT_DIR / "data" / "generated")
    copy_tree(REPO_ROOT / "data" / "textbook", OUTPUT_DIR / "data" / "textbook")


if __name__ == "__main__":
    main()
