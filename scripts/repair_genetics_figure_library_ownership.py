"""Repair book ownership overwritten by the Genetics logical-boundary pass.

Figure ids such as ``5.1`` occur in both books.  The logical Genetics
repartition must only move records cropped from Genetics PDFs; an earlier pass
also relabelled Evolution records with matching ids.  Restore those records to
the chapter encoded by their immutable source-PDF path, then assert that each
``(chapter, figure id)`` lookup is unambiguous for the textbook exporter.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "figure_library.json"


def main() -> None:
    payload = json.loads(LIBRARY.read_text(encoding="utf-8"))
    figures = payload.get("figures")
    if not isinstance(figures, dict):
        raise TypeError("figure_library.json must use a figure dictionary")

    restored = 0
    owners: dict[tuple[str, str], list[str]] = defaultdict(list)
    for key, figure in figures.items():
        if not isinstance(figure, dict):
            continue
        source_chapter = Path(str(figure.get("source_pdf") or "")).stem
        if source_chapter.lower().startswith("evolution_"):
            if figure.get("chapter") != source_chapter:
                figure["chapter"] = source_chapter
                restored += 1
        chapter = str(figure.get("chapter") or "")
        figure_id = str(figure.get("id") or "")
        if chapter and figure_id:
            owners[(chapter, figure_id)].append(key)

    duplicates = {pair: keys for pair, keys in owners.items() if len(keys) > 1}
    if duplicates:
        raise ValueError(f"Ambiguous chapter-local figure records: {duplicates}")

    LIBRARY.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Restored {restored} Evolution figure owners; no chapter-local duplicates remain.")


if __name__ == "__main__":
    main()
