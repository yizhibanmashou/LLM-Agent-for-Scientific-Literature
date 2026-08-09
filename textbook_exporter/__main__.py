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
        help="Directory where prefixed chapter textbook files, e.g. Evolution_chapter25_textbook.md, will be written.",
    )
    parser.add_argument(
        "--chapters",
        default=None,
        help="Optional comma-separated chapter filter, e.g. Evolution_chapter25,Evolution_chapter30 or 25,30.",
    )
    parser.add_argument(
        "--figure-library",
        default=None,
        type=Path,
        help="Optional figure_library.json used to expand [[FIGURE:*]] placeholders.",
    )
    parser.add_argument(
        "--book-id",
        default=None,
        help="Optional book library override, e.g. Genetics. Defaults to the chapter filename prefix.",
    )
    parser.add_argument(
        "--books",
        default=None,
        help="Optional comma-separated book filter, e.g. Evolution,Genetics,PopGen.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    chapters = parse_chapter_filter(args.chapters)
    books = {part.strip() for part in str(args.books or "").split(",") if part.strip()} or None
    results = export_textbooks(
        structured_dir=args.structured_dir,
        out_dir=args.out_dir,
        chapters=chapters,
        figure_library=args.figure_library,
        book_id=args.book_id,
        books=books,
    )
    if not results:
        raise SystemExit("No chapter files matched the requested export.")

    for result in results:
        print(f"Generated: {result.output_path} ({result.chunk_count} chunks)")


if __name__ == "__main__":
    main()
