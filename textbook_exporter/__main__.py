from __future__ import annotations

import argparse
from pathlib import Path

from .exporter import export_textbooks, parse_chapter_filter


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export data/structured chapter JSON files into readable textbook Markdown."
    )
    parser.add_argument(
        "--structured-dir",
        default="data/structured",
        type=Path,
        help="Directory containing chapter JSON files and asset libraries.",
    )
    parser.add_argument(
        "--out-dir",
        default="data/textbook",
        type=Path,
        help="Directory where chapter*_textbook.md files will be written.",
    )
    parser.add_argument(
        "--chapters",
        default=None,
        help="Optional comma-separated chapter filter, e.g. chapter25,chapter30 or 25,30.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    chapters = parse_chapter_filter(args.chapters)
    results = export_textbooks(
        structured_dir=args.structured_dir,
        out_dir=args.out_dir,
        chapters=chapters,
    )
    if not results:
        raise SystemExit("No chapter files matched the requested export.")

    for result in results:
        print(f"Generated: {result.output_path} ({result.chunk_count} chunks)")


if __name__ == "__main__":
    main()
