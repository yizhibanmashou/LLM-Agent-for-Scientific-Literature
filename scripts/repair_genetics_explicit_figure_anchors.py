#!/usr/bin/env python3
"""Restore explicit structured figure anchors that the Markdown exporter inferred."""

from __future__ import annotations

import json
from pathlib import Path


ANCHORS = {
    "Genetics_chapter5_008.json": ("5.6", "This point is made clear with the extreme example in Figure 5.6"),
    "Genetics_chapter7_013.json": ("7.8", "path diagrams for four specific relationships (Figure 7.8)."),
    "Genetics_chapter10_002.json": ("10.2", "Figure 10.2 Change in mean phenotypes"),
    "Genetics_chapter14_006.json": ("14.2", "Shrimpton and Robertson (Figure 14.2)"),
    "Genetics_chapter15_020.json": ("15.7", "Figure 15.7 plots the ratio"),
    "Genetics_chapter21_012.json": ("21.3", "selected populations (Figure 21.3)."),
    "Genetics_chapter27_025.json": ("A2.1", "Figure A2.1 Path diagram"),
    "Genetics_chapter27_025.json#A2.2": ("A2.2", "Figure A2.2 Path diagram"),
    "Genetics_chapter27_028.json": ("A2.3", "Figure A2.3 Wright's"),
    "Genetics_chapter27_029.json": ("A2.4", "Figure A2.4 Path diagram"),
    "Genetics_chapter27_030.json": ("A2.5", "Figure A2.5 Path diagram"),
    "Genetics_chapter27_058.json": ("A5.1", "Figure A5.1 Power"),
    "Genetics_chapter27_060.json": ("A5.2", "Figure A5.2 Areas"),
    "Genetics_chapter27_065.json": ("A5.3", "Figure A5.3 The probability"),
}


def main() -> None:
    root = Path("data/structured")
    for raw_name, (figure_id, needle) in ANCHORS.items():
        name = raw_name.split("#", 1)[0]
        path = root / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        marker = f"[[FIGURE:{figure_id}]]"
        if any(marker in str(block.get("content") or "") for block in payload.get("blocks", [])):
            continue
        for block in payload.get("blocks", []):
            content = str(block.get("content") or "")
            if needle in content:
                block["content"] = content.replace(needle, f"{marker}\n{needle}", 1)
                break
        else:
            raise ValueError(f"Anchor text not found for Figure {figure_id} in {name}")
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    formula_path = root / "formula_library.json"
    formulas = json.loads(formula_path.read_text(encoding="utf-8"))
    for formula in formulas.get("formulas", []):
        if formula.get("id") == "Genetics_chapter3_formula063":
            source = formula.get("source", {})
            source["unit_id"] = "Genetics_chapter4_003"
            source["chapter"] = "Genetics_chapter4"
            formula["source"] = source
    formula_path.write_text(json.dumps(formulas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
