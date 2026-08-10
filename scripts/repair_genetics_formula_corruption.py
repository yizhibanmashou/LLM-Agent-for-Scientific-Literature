"""Restore verified Genetics display formulas that were damaged by OCR.

The formula library retains the original, normalized LaTeX for these formulas.
Each entry below is tied to the damaged structured block and is deliberately
asserted before replacement, so this script cannot silently rewrite a similar
but unrelated expression.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
FORMULAS_PATH = STRUCTURED / "formula_library.json"

# (structured file, zero-based block index, distinctive damaged text, formula id)
REPAIRS = [
    ("Genetics_chapter2_002.json", 20, "_ 3 &=", "Genetics_chapter2_formula012"),
    ("Genetics_chapter7_007.json", 9, "_ G (x,y)=", "Genetics_chapter7_formula014"),
    ("Genetics_chapter8_002.json", 3, "(y,z_ i)&=", "Genetics_chapter7_formula049"),
    ("Genetics_chapter8_020.json", 8, "z_ o &=", "Genetics_chapter8_formula095"),
    ("Genetics_chapter13_012.json", 6, "(g_ f =1", "Genetics_chapter13_formula025"),
    ("Genetics_chapter13_012.json", 10, "(.qq |", "Genetics_chapter13_formula028"),
    ("Genetics_chapter13_012.json", 12, "(qq g_ f", "Genetics_chapter13_formula029"),
    ("Genetics_chapter13_013.json", 4, "(z_ i)&=", "Genetics_chapter13_formula034"),
    ("Genetics_chapter13_014.json", 4, "& (z_ i", "Genetics_chapter13_formula038"),
    ("Genetics_chapter16_007.json", 3, "_ M_ 1 -", "Genetics_chapter16_formula025"),
    ("Genetics_chapter21_006.json", 2, "^ 2 (_ 1i)", "Genetics_chapter21_formula018"),
    ("Genetics_chapter23_009.json", 4, "(M,O)&=", "Genetics_chapter23_formula029"),
    ("Genetics_chapter24_005.json", 3, "(G_ Mx,G_ My)", "Genetics_chapter24_formula012"),
    ("Genetics_chapter24_005.json", 8, "(G_ Fx,G_ Fy)", "Genetics_chapter24_formula014"),
    ("Genetics_chapter27_016.json", 5, "E(f) f(_ x_ 1", "Genetics_chapter27_formula107"),
    ("Genetics_chapter27_021.json", 2, "^ 2 (u/v)", "Genetics_chapter27_formula152"),
    ("Genetics_chapter27_042.json", 8, "_ &= ^ T ^ -1/2", "Genetics_chapter27_formula272"),
    ("Genetics_chapter27_042.json", 10, "_ &= ^ T ^ -1 \\\\&=", "Genetics_chapter27_formula273"),
    ("Genetics_chapter27_057.json", 2, "(Q_ k m,z,c)", "Genetics_chapter27_formula351"),
    ("Genetics_chapter27_061.json", 6, "n&= (8(1-r^ 2)", "Genetics_chapter27_formula375"),
    ("Genetics_chapter27_069.json", 2, "F&= _ t", "Genetics_chapter27_formula444"),
]


def replace_damaged_formula(content: str, fragment: str, latex: str) -> str:
    """Replace the malformed formula span around *fragment* with one display."""
    position = content.find(fragment)
    if position < 0:
        raise ValueError(f"Damaged formula marker not found: {fragment!r}")

    # Broken formulas either start the block or are preceded by an empty display
    # marker in the immediately preceding prose block.
    opening = content.rfind("$$ $$", 0, position)
    start = opening if opening >= 0 else 0
    closing = content.find("$$ $$", position)
    if closing < 0:
        raise ValueError(f"Damaged formula has no closing marker: {fragment!r}")
    end = closing + len("$$ $$")
    return content[:start] + f"$$\n{latex}\n$$" + content[end:]


def main() -> None:
    library = json.loads(FORMULAS_PATH.read_text(encoding="utf-8"))
    formulas = {formula["id"]: formula for formula in library["formulas"]}
    changed_files: dict[Path, dict] = {}

    for filename, block_index, fragment, formula_id in REPAIRS:
        if formula_id not in formulas:
            raise KeyError(f"Formula library record missing: {formula_id}")
        path = STRUCTURED / filename
        data = changed_files.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        matches = [
            block for block in data["blocks"] if fragment in block.get("content", "")
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one damaged formula in {filename} for {fragment!r}; "
                f"found {len(matches)}"
            )
        content = matches[0]["content"]
        matches[0]["content"] = replace_damaged_formula(
            content, fragment, formulas[formula_id]["latex"]
        )

        source = formulas[formula_id]["source"]
        source["unit_id"] = data["id"]
        source["chapter"] = data["metadata"]["chapter"]

    for path, data in changed_files.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    FORMULAS_PATH.write_text(json.dumps(library, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Restored {len(REPAIRS)} formulas in {len(changed_files)} structured chunks.")


if __name__ == "__main__":
    main()
