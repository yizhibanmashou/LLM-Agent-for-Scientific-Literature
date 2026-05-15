import json
import unittest
from pathlib import Path
from uuid import uuid4

from knowledge_engineering.processors.gold_textbook_repair import (
    apply_gold_textbook_repair,
    compare_gold_to_textbook,
)


TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "gold_textbook_repair"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class GoldTextbookRepairTests(unittest.TestCase):
    def test_repair_uses_gold_order_without_renaming_structured_units(self):
        root = make_test_workspace("skipped_gold_id")
        structured = root / "structured"
        gold_path = root / "gold.md"

        write_json(
            structured / "chapter25_025.json",
            {
                "id": "chapter25_025",
                "metadata": {
                    "chapter": "chapter25",
                    "section_level_1": "25: Introduction",
                    "heading_path": ["25: Introduction", "Accumulation of Lethals in Selected Lines"],
                    "display_heading": "Accumulation of Lethals in Selected Lines",
                    "table_references": [],
                },
                "blocks": [
                    {"type": "discussion", "content": "Lethal alleles are often detected in lines."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:25.9]]"},
                ],
            },
        )
        write_json(
            structured / "chapter25_026.json",
            {
                "id": "chapter25_026",
                "metadata": {
                    "chapter": "chapter25",
                    "section_level_1": "25: Introduction",
                    "heading_path": ["25: Introduction", "Lerner's Model of Genetic Homeostasis"],
                    "display_heading": "Lerner's Model of Genetic Homeostasis",
                },
                "blocks": [{"type": "discussion", "content": "A second class of models assuming pleiotropic fitness effects."}],
            },
        )
        write_json(
            structured / "chapter25_027.json",
            {
                "id": "chapter25_027",
                "metadata": {
                    "chapter": "chapter25",
                    "section_level_1": "25: Introduction",
                    "heading_path": ["25: Introduction", "Artificial Selection Countered by Natural Stabilizing Selection"],
                    "display_heading": "Artificial Selection Countered by Natural Stabilizing Selection",
                },
                "blocks": [{"type": "discussion", "content": "Lerner's model is an example."}],
            },
        )
        write_json(
            structured / "example_library.json",
            {
                "examples": [
                    {
                        "example_id": "25.9",
                        "example_ref": "25.9",
                        "chapter": "chapter25",
                        "source_file": "chapter25_024.json",
                        "start_block_index": 2,
                        "end_block_index": 2,
                        "replacement": {"status": "replaced"},
                    }
                ]
            },
        )
        write_json(structured / "table_library.json", {"tables": []})

        gold_path.write_text(
            "\n".join(
                [
                    "# Chapter 25 Textbook Mapping",
                    "",
                    "## chapter25_025 · CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION / Accumulation of Lethals in Selected Lines",
                    "",
                    "Lethal alleles are often detected in lines.",
                    "",
                    "> **Example 25.9** · ref: `25.9` · source: `chapter25_025.json` · blocks 1–1",
                    ">",
                    "> Example content.",
                    "",
                    "---",
                    "",
                    "## chapter25_027 · CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION / Lerner's Model of Genetic Homeostasis",
                    "",
                    "A second class of models assuming pleiotropic fitness effects.",
                    "",
                    "---",
                    "",
                    "## chapter25_028 · CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION / Artificial Selection Countered by Natural Stabilizing Selection",
                    "",
                    "Lerner's model is an example.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        summary = apply_gold_textbook_repair(
            structured_dir=structured,
            gold_path=gold_path,
            chapter="chapter25",
        )

        self.assertEqual(
            summary["unit_id_by_gold_id"]["chapter25_027"],
            "chapter25_026",
        )
        self.assertEqual(
            summary["unit_id_by_gold_id"]["chapter25_028"],
            "chapter25_027",
        )
        self.assertTrue((structured / "chapter25_026.json").exists())
        self.assertFalse((structured / "chapter25_028.json").exists())

        unit_026 = json.loads((structured / "chapter25_026.json").read_text(encoding="utf-8"))
        self.assertEqual(
            unit_026["metadata"]["heading_path"],
            ["CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION", "Lerner's Model of Genetic Homeostasis"],
        )

        library = json.loads((structured / "example_library.json").read_text(encoding="utf-8"))
        row = library["examples"][0]
        self.assertEqual(row["source_file"], "chapter25_025.json")
        self.assertEqual(row["start_block_index"], 1)
        self.assertEqual(row["end_block_index"], 1)

    def test_compare_reports_example_and_table_mismatches(self):
        root = make_test_workspace("compare")
        gold = root / "gold.md"
        candidate = root / "candidate.md"
        gold.write_text(
            "\n".join(
                [
                    "# Chapter 25 Textbook Mapping",
                    "## chapter25_001 · Introduction",
                    "> **Example 25.1** · ref: `25.1` · source: `chapter25_001.json` · blocks 1–2",
                    "> **Table 25.1** · `25.1` · page 1 · source: `chapter25_001`",
                ]
            ),
            encoding="utf-8",
        )
        candidate.write_text(
            "\n".join(
                [
                    "# Chapter 25 Textbook Mapping",
                    "## chapter25_001 · 25: Introduction",
                    "> **Example 25.1** · ref: `25.1` · source: `chapter25_002.json` · blocks 1–1",
                ]
            ),
            encoding="utf-8",
        )

        diff = compare_gold_to_textbook(gold, candidate)

        self.assertEqual(len(diff["heading_mismatches"]), 1)
        self.assertEqual(len(diff["example_mismatches"]), 1)
        self.assertEqual(len(diff["table_mismatches"]), 1)


if __name__ == "__main__":
    unittest.main()
