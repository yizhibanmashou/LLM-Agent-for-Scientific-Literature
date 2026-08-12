"""Replace three verified OCR-corrupted display regions with formula-library links."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"


def load(name: str) -> dict:
    return json.loads((STRUCTURED / name).read_text(encoding="utf-8"))


def save(name: str, payload: dict) -> None:
    (STRUCTURED / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_once(value: str, pattern: str, replacement: str, label: str) -> str:
    replaced, count = re.subn(pattern, replacement, value, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError(f"{label}: expected exactly one matched corrupted display, got {count}")
    return replaced


def main() -> None:
    chapter13 = load("Genetics_chapter13_014.json")
    content = chapter13["blocks"][4]["content"]
    chapter13["blocks"][4]["content"] = replace_once(
        content,
        r"\$\$\s*\\begin\{align\*\}.*?\\end\{align\*\}\s*\$\$",
        "[[FORMULA:Genetics_chapter13_formula038]]",
        "Genetics_chapter13_formula038",
    )
    save("Genetics_chapter13_014.json", chapter13)

    chapter27 = load("Genetics_chapter27_019.json")
    content = chapter27["blocks"][9]["content"]
    where_index = content.find("where $\\mu_{0}")
    if where_index < 0:
        raise ValueError("Genetics_chapter27_formula135: trailing prose marker not found")
    chapter27["blocks"][9]["content"] = "[[FORMULA:Genetics_chapter27_formula135]]\n\n" + content[where_index:]
    save("Genetics_chapter27_019.json", chapter27)

    chapter27 = load("Genetics_chapter27_003.json")
    content = chapter27["blocks"][2]["content"]
    chapter27["blocks"][2]["content"] = replace_once(
        content,
        r"\$\$\s*\\begin\{aligned\}\\sum_\{i=1\}\^\{n\}\(y_\{i\}-\\mu\)\^\{2\}.*?\\tag\{2\s*\$\$",
        "[[FORMULA:Genetics_chapter27_formula005]]",
        "Genetics_chapter27_formula005",
    )
    save("Genetics_chapter27_003.json", chapter27)


if __name__ == "__main__":
    main()
