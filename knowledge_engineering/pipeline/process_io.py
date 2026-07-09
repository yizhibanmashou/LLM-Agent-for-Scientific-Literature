"""Filesystem and input-discovery helpers for the structured pipeline package."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
from typing import List


def clear_directory(path: str) -> int:
    """Recursively clear all children under ``path`` while preserving the directory."""
    if not os.path.isdir(path):
        return 0

    removed = 0
    for entry in os.listdir(path):
        target = os.path.join(path, entry)
        try:
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
            removed += 1
        except OSError:
            pass
    return removed


def get_split_artifact_dir(artifacts_dir: str) -> str:
    """Return split-text artifact directory rooted under tmp storage."""
    return os.path.join(os.path.abspath(artifacts_dir), "split_latex")


def save_split_artifacts(
    artifacts_dir: str,
    toc_name: str,
    toc_text: str,
    chapter_segments: dict[str, str],
) -> None:
    """Persist split text snapshots for debugging and regression inspection."""
    split_dir = get_split_artifact_dir(artifacts_dir)
    os.makedirs(split_dir, exist_ok=True)

    if toc_text:
        toc_path = os.path.join(split_dir, f"{toc_name}.txt")
        with open(toc_path, "w", encoding="utf-8") as file:
            file.write(toc_text)

    for chapter_name, chapter_text in chapter_segments.items():
        chapter_path = os.path.join(split_dir, f"{chapter_name}.txt")
        with open(chapter_path, "w", encoding="utf-8") as file:
            file.write(chapter_text)


def find_latex_inputs(input_path: str) -> List[str]:
    """Resolve paddle_output-style inputs to main.tex files."""
    root = Path(input_path)
    if root.is_file():
        if root.suffix.lower() != ".tex":
            raise ValueError(f"Expected a .tex file, got: {root}")
        return [str(root)]

    if not root.is_dir():
        raise ValueError(f"Input path does not exist: {root}")

    direct_main = root / "main.tex"
    if direct_main.exists():
        return [str(direct_main)]

    chapter_candidates = []
    for path in root.glob("chapter*_full/main.tex"):
        chapter_match = re.search(r"chapter(\d+)_full", str(path).replace("\\", "/"), re.IGNORECASE)
        chapter_idx = int(chapter_match.group(1)) if chapter_match else 9999
        chapter_candidates.append((0, chapter_idx, str(path)))
    for path in root.glob("appendix*_full/main.tex"):
        appendix_match = re.search(r"appendix(\d+)_full", str(path).replace("\\", "/"), re.IGNORECASE)
        appendix_idx = int(appendix_match.group(1)) if appendix_match else 9999
        chapter_candidates.append((1, appendix_idx, str(path)))
    if chapter_candidates:
        return [path for _, _, path in sorted(chapter_candidates, key=lambda item: (item[0], item[1]))]

    nested_main = sorted(root.rglob("main.tex"))
    return [str(path) for path in nested_main]


def derive_chapter_name(tex_path: str) -> str:
    """Derive a stable chapter-like name from paper2latex output path."""
    parent_name = Path(tex_path).parent.name
    stem_name = Path(tex_path).stem

    for candidate in (parent_name, stem_name):
        chapter_match = re.match(
            r"^(?:(?P<prefix>[A-Za-z]+)_)?chapter[_-]?(?P<num>\d+)(?:_full)?$",
            candidate,
            re.IGNORECASE,
        )
        if chapter_match:
            prefix = chapter_match.group("prefix")
            chapter = f"chapter{chapter_match.group('num')}"
            return f"{prefix}_{chapter}" if prefix else chapter

        appendix_match = re.match(
            r"^(?:(?P<prefix>[A-Za-z]+)_)?appendix[_-]?(?P<num>\d+)(?:_full)?$",
            candidate,
            re.IGNORECASE,
        )
        if appendix_match:
            prefix = appendix_match.group("prefix")
            appendix = f"appendix{appendix_match.group('num')}"
            return f"{prefix}_{appendix}" if prefix else appendix

        numeric_full_match = re.match(r"^(?P<num>\d+)_full$", candidate, re.IGNORECASE)
        if numeric_full_match:
            return f"chapter{numeric_full_match.group('num')}"

    base = parent_name or Path(tex_path).stem
    slug = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_").lower()
    return slug or "latex_doc"
