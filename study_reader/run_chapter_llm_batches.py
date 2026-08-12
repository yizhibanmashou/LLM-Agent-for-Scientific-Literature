from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATASET_PATH = APP_DIR / "data" / "generated" / "study_dataset.json"
RUN_DIR = ROOT_DIR / "tmp" / "study_reader_chapter_llm"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def has_validated_prerequisites(dataset: dict[str, Any], chapter_id: str) -> bool:
    payload = dataset.get("data", {}).get(chapter_id, {})
    prerequisites = payload.get("prerequisites", []) if isinstance(payload, dict) else []
    return bool(prerequisites) and all(
        isinstance(item, dict) and item.get("validated_by_llm") is True
        for item in prerequisites
    )


def chapter_ids_for_books(dataset: dict[str, Any], books: set[str]) -> list[str]:
    chapters = dataset.get("chapters", [])
    return [
        str(chapter.get("id"))
        for chapter in chapters
        if isinstance(chapter, dict)
        and chapter.get("id")
        and (not books or str(chapter.get("book")) in books)
    ]


def run_chapter(chapter_id: str, books_arg: str, logs_dir: Path) -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"{timestamp}_{chapter_id}.log"
    command = [
        sys.executable,
        str(APP_DIR / "build_study_reader.py"),
        "--books",
        books_arg,
        "--chapters",
        chapter_id,
    ]
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"$ {' '.join(command)}\n\n")
        log.flush()
        process = subprocess.run(
            command,
            cwd=ROOT_DIR,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        log.write(f"\nexit_code={process.returncode}\n")
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Study Reader prerequisite LLM review chapter by chapter.")
    parser.add_argument("--books", default="Evolution,Genetics", help="Comma-separated books to process.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of chapters to process.")
    parser.add_argument("--force", action="store_true", help="Re-run chapters even if validated prerequisites already exist.")
    args = parser.parse_args()

    dataset = load_json(DATASET_PATH)
    if not dataset:
        print(f"Missing dataset: {DATASET_PATH}", file=sys.stderr)
        return 2

    books = {part.strip() for part in args.books.split(",") if part.strip()}
    chapters = chapter_ids_for_books(dataset, books)
    if not args.force:
        chapters = [chapter_id for chapter_id in chapters if not has_validated_prerequisites(dataset, chapter_id)]
    if args.limit > 0:
        chapters = chapters[: args.limit]

    logs_dir = RUN_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = RUN_DIR / "manifest.jsonl"

    print(f"chapters_to_process={len(chapters)}")
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for index, chapter_id in enumerate(chapters, start=1):
            print(f"[{index}/{len(chapters)}] {chapter_id}", flush=True)
            code = run_chapter(chapter_id, args.books, logs_dir)
            row = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "chapter_id": chapter_id,
                "exit_code": code,
            }
            manifest.write(json.dumps(row, ensure_ascii=False) + "\n")
            manifest.flush()
            if code != 0:
                return code
    print(f"done logs={logs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
