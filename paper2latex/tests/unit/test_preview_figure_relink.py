import json
import unittest
from pathlib import Path
from uuid import uuid4

from scripts.preview_figure_relink import patch_chapter


TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "preview_figure_relink"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class PreviewFigureRelinkTests(unittest.TestCase):
    def test_explicit_text_reference_beats_neighboring_following_heading(self):
        root = make_test_workspace("text_reference_beats_neighbor_heading")
        structured_dir = root / "structured"
        out_dir = root / "patched"
        raw_path = root / "paddle_raw_response.json"

        write_json(
            raw_path,
            [
                {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Figure 25.3 plots the total contribution from a diallelic locus.",
                            "block_bbox": [100, 700, 900, 760],
                        },
                        {
                            "block_label": "paragraph_title",
                            "block_content": "Dudley's Estimators of a, n, and p0",
                            "block_bbox": [100, 970, 900, 1000],
                        },
                    ]
                }
            ],
        )
        write_json(
            structured_dir / "chapter25_004.json",
            {
                "id": "chapter25_004",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "DETERMINISTIC SINGLE-LOCUS THEORY",
                    "section_level_2": "Expected Contribution From a Single Locus",
                    "display_heading": "Expected Contribution From a Single Locus",
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "Figure 25.3 plots the total contribution from a diallelic locus.",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_005.json",
            {
                "id": "chapter25_005",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "DETERMINISTIC SINGLE-LOCUS THEORY",
                    "section_level_2": "Dudley's Estimators of a, n, and p0",
                    "display_heading": "Dudley's Estimators of a, n, and p0",
                    "heading_path": [
                        "DETERMINISTIC SINGLE-LOCUS THEORY",
                        "Dudley's Estimators of a, n, and p0",
                    ],
                },
                "blocks": [{"type": "discussion", "content": "Next subsection text."}],
            },
        )

        audit = patch_chapter(
            chapter="chapter25",
            figures=[
                {
                    "id": "25.3",
                    "chapter": "chapter25",
                    "source_paddle_raw": str(raw_path),
                    "page": 1,
                    "raw_bbox": [120, 200, 880, 560],
                    "caption_block": {
                        "bbox": [120, 580, 880, 690],
                        "label": "figure_title",
                        "content": "Figure 25.3 Caption.",
                    },
                }
            ],
            structured_dir=structured_dir,
            out_dir=out_dir,
        )

        self.assertEqual(audit["placed"][0]["figure_id"], "25.3")
        self.assertEqual(audit["placed"][0]["chunk"], "chapter25_004")
        self.assertEqual(audit["placed"][0]["method"], "near_text_reference")

        chunk_004 = json.loads((out_dir / "chapter25_004.json").read_text(encoding="utf-8"))
        chunk_005 = json.loads((out_dir / "chapter25_005.json").read_text(encoding="utf-8"))
        self.assertIn("[[FIGURE:25.3]]", [block["content"] for block in chunk_004["blocks"]])
        self.assertNotIn("[[FIGURE:25.3]]", json.dumps(chunk_005, ensure_ascii=False))

    def test_far_text_reference_does_not_beat_neighboring_heading(self):
        root = make_test_workspace("far_reference_keeps_neighbor_heading")
        structured_dir = root / "structured"
        out_dir = root / "patched"
        raw_path = root / "paddle_raw_response.json"

        write_json(
            raw_path,
            [
                {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "This overview briefly mentions Figure 25.10.",
                            "block_bbox": [100, 100, 900, 180],
                        }
                    ]
                },
                {
                    "parsing_res_list": [
                        {
                            "block_label": "paragraph_title",
                            "block_content": "Rare Alleles",
                            "block_bbox": [100, 970, 900, 1000],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The result can be an increase in response many generations after the start of selection (Figure 25.10).",
                            "block_bbox": [100, 1010, 900, 1090],
                        },
                    ]
                },
            ],
        )
        write_json(
            structured_dir / "chapter25_002.json",
            {
                "id": "chapter25_002",
                "metadata": {"chapter": "chapter25", "display_heading": "Introduction"},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "This overview briefly mentions Figure 25.10.",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_019.json",
            {
                "id": "chapter25_019",
                "metadata": {
                    "chapter": "chapter25",
                    "section_level_2": "Rare Alleles",
                    "display_heading": "Rare Alleles",
                    "heading_path": ["INCREASES IN VARIANCES AND ACCELERATED RESPONSES", "Rare Alleles"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The result can be an increase in response many generations after the start of selection (Figure 25.10).",
                    }
                ],
            },
        )

        audit = patch_chapter(
            chapter="chapter25",
            figures=[
                {
                    "id": "25.10",
                    "chapter": "chapter25",
                    "source_paddle_raw": str(raw_path),
                    "page": 2,
                    "raw_bbox": [120, 200, 880, 560],
                    "caption_block": {
                        "bbox": [120, 580, 880, 690],
                        "label": "figure_title",
                        "content": "Figure 25.10 Caption.",
                    },
                }
            ],
            structured_dir=structured_dir,
            out_dir=out_dir,
        )

        self.assertEqual(audit["placed"][0]["figure_id"], "25.10")
        self.assertEqual(audit["placed"][0]["chunk"], "chapter25_019")
        self.assertEqual(audit["placed"][0]["method"], "near_text_reference")

        early_chunk = json.loads((out_dir / "chapter25_002.json").read_text(encoding="utf-8"))
        target_chunk = json.loads((out_dir / "chapter25_019.json").read_text(encoding="utf-8"))
        self.assertNotIn("[[FIGURE:25.10]]", json.dumps(early_chunk, ensure_ascii=False))
        self.assertIn("[[FIGURE:25.10]]", [block["content"] for block in target_chunk["blocks"]])

    def test_near_coordinate_text_anchor_beats_following_heading(self):
        root = make_test_workspace("near_coordinate_text_beats_heading")
        structured_dir = root / "structured"
        out_dir = root / "patched"
        raw_path = root / "paddle_raw_response.json"

        overview_text = (
            "smooth response with considerable sampling noise, initially linear, but eventually "
            "asymptotes to a selection limit as base-population genetic variance becomes exhausted."
        )
        heading = "Estimating Selection Limits and Half-lives"
        subsection_text = "Because the selection limit is approached asymptotically, the typical measure is the half-life."

        write_json(
            raw_path,
            [
                {
                    "parsing_res_list": [
                        {
                            "block_label": "chart",
                            "block_content": "",
                            "block_bbox": [200, 200, 880, 560],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Figure 25.7 Caption.",
                            "block_bbox": [200, 580, 880, 690],
                        },
                        {
                            "block_label": "text",
                            "block_content": overview_text,
                            "block_bbox": [100, 735, 900, 820],
                        },
                        {
                            "block_label": "paragraph_title",
                            "block_content": heading,
                            "block_bbox": [100, 930, 900, 960],
                        },
                        {
                            "block_label": "text",
                            "block_content": subsection_text,
                            "block_bbox": [100, 970, 900, 1060],
                        },
                    ]
                }
            ],
        )
        write_json(
            structured_dir / "chapter25_013.json",
            {
                "id": "chapter25_013",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS",
                    "display_heading": "AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS",
                },
                "blocks": [{"type": "discussion", "content": overview_text}],
            },
        )
        write_json(
            structured_dir / "chapter25_014.json",
            {
                "id": "chapter25_014",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS",
                    "section_level_2": heading,
                    "display_heading": heading,
                    "heading_path": ["AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS", heading],
                },
                "blocks": [{"type": "discussion", "content": subsection_text}],
            },
        )

        audit = patch_chapter(
            chapter="chapter25",
            figures=[
                {
                    "id": "25.7",
                    "chapter": "chapter25",
                    "source_paddle_raw": str(raw_path),
                    "page": 1,
                    "raw_bbox": [200, 200, 880, 560],
                    "caption_block": {
                        "bbox": [200, 580, 880, 690],
                        "label": "figure_title",
                        "content": "Figure 25.7 Caption.",
                    },
                }
            ],
            structured_dir=structured_dir,
            out_dir=out_dir,
        )

        self.assertEqual(audit["placed"][0]["figure_id"], "25.7")
        self.assertEqual(audit["placed"][0]["chunk"], "chapter25_013")
        self.assertEqual(audit["placed"][0]["method"], "near_coordinate_text_anchor")

        overview_chunk = json.loads((out_dir / "chapter25_013.json").read_text(encoding="utf-8"))
        subsection_chunk = json.loads((out_dir / "chapter25_014.json").read_text(encoding="utf-8"))
        self.assertIn("[[FIGURE:25.7]]", [block["content"] for block in overview_chunk["blocks"]])
        self.assertNotIn("[[FIGURE:25.7]]", json.dumps(subsection_chunk, ensure_ascii=False))

    def test_figure_before_table_uses_physical_table_position(self):
        root = make_test_workspace("figure_before_table")
        structured_dir = root / "structured"
        out_dir = root / "patched"
        raw_path = root / "paddle_raw_response.json"

        followup_text = (
            "Expressions for p beta as a function of initial allele frequency are given in "
            "Table 25.1 and plotted in Figure 25.3."
        )
        heading = "Dudley's Estimators of a, n, and p0"
        next_text = "In a similar fashion to the Wright-Castle estimator for the number of loci."

        write_json(
            raw_path,
            [
                {
                    "parsing_res_list": [
                        {
                            "block_label": "chart",
                            "block_content": "",
                            "block_bbox": [120, 185, 916, 538],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Figure 25.3 Caption.",
                            "block_bbox": [167, 545, 881, 676],
                        },
                        {
                            "block_label": "table_title",
                            "block_content": "Table 25.1 Total contribution.",
                            "block_bbox": [133, 700, 905, 746],
                        },
                        {
                            "block_label": "table",
                            "block_content": "",
                            "block_bbox": [136, 750, 904, 910],
                        },
                        {
                            "block_label": "text",
                            "block_content": followup_text,
                            "block_bbox": [133, 944, 903, 1062],
                        },
                        {
                            "block_label": "paragraph_title",
                            "block_content": heading,
                            "block_bbox": [133, 1080, 444, 1104],
                        },
                        {
                            "block_label": "text",
                            "block_content": next_text,
                            "block_bbox": [132, 1108, 905, 1273],
                        },
                    ]
                }
            ],
        )
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "25.1",
                        "source": {
                            "page": 1,
                            "bbox": [136, 750, 904, 910],
                            "caption_bbox": [133, 700, 905, 746],
                            "unit_id": "chapter25_004",
                        },
                    }
                ]
            },
        )
        write_json(
            structured_dir / "chapter25_004.json",
            {
                "id": "chapter25_004",
                "metadata": {
                    "chapter": "chapter25",
                    "display_heading": "Expected Contribution From a Single Locus",
                },
                "blocks": [
                    {"type": "derivation", "content": "Earlier paragraph."},
                    {"type": "table", "content": "[[TABLE:25.1]]"},
                    {"type": "discussion", "content": followup_text},
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_005.json",
            {
                "id": "chapter25_005",
                "metadata": {
                    "chapter": "chapter25",
                    "section_level_2": heading,
                    "display_heading": heading,
                    "heading_path": ["DETERMINISTIC SINGLE-LOCUS THEORY", heading],
                },
                "blocks": [{"type": "discussion", "content": next_text}],
            },
        )

        audit = patch_chapter(
            chapter="chapter25",
            figures=[
                {
                    "id": "25.3",
                    "chapter": "chapter25",
                    "source_paddle_raw": str(raw_path),
                    "page": 1,
                    "raw_bbox": [120, 185, 916, 538],
                    "caption_block": {
                        "bbox": [167, 545, 881, 676],
                        "label": "figure_title",
                        "content": "Figure 25.3 Caption.",
                    },
                }
            ],
            structured_dir=structured_dir,
            out_dir=out_dir,
        )

        self.assertEqual(audit["placed"][0]["figure_id"], "25.3")
        self.assertEqual(audit["placed"][0]["chunk"], "chapter25_004")
        self.assertEqual(audit["placed"][0]["before_block"], 1)
        self.assertEqual(audit["placed"][0]["method"], "near_coordinate_object_anchor")

        chunk_004 = json.loads((out_dir / "chapter25_004.json").read_text(encoding="utf-8"))
        contents = [block["content"] for block in chunk_004["blocks"]]
        self.assertLess(contents.index("[[FIGURE:25.3]]"), contents.index("[[TABLE:25.1]]"))

    def test_existing_standalone_figure_block_is_relinked_without_duplicate(self):
        root = make_test_workspace("existing_figure_relinked")
        structured_dir = root / "structured"
        out_dir = root / "patched"
        raw_path = root / "paddle_raw_response.json"

        overview_text = "This overview text is the nearest coordinate anchor for Figure 25.7."
        heading = "Estimating Selection Limits and Half-lives"

        write_json(
            raw_path,
            [
                {
                    "parsing_res_list": [
                        {
                            "block_label": "chart",
                            "block_content": "",
                            "block_bbox": [200, 200, 880, 560],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Figure 25.7 Caption.",
                            "block_bbox": [200, 580, 880, 690],
                        },
                        {
                            "block_label": "text",
                            "block_content": overview_text,
                            "block_bbox": [100, 735, 900, 820],
                        },
                        {
                            "block_label": "paragraph_title",
                            "block_content": heading,
                            "block_bbox": [100, 930, 900, 960],
                        },
                    ]
                }
            ],
        )
        write_json(
            structured_dir / "chapter25_013.json",
            {
                "id": "chapter25_013",
                "metadata": {"chapter": "chapter25", "display_heading": "Overview"},
                "blocks": [{"type": "discussion", "content": overview_text}],
            },
        )
        write_json(
            structured_dir / "chapter25_014.json",
            {
                "id": "chapter25_014",
                "metadata": {"chapter": "chapter25", "display_heading": heading},
                "blocks": [
                    {"type": "figure", "content": "[[FIGURE:25.7]]"},
                    {"type": "discussion", "content": "Subsection text."},
                ],
            },
        )

        audit = patch_chapter(
            chapter="chapter25",
            figures=[
                {
                    "id": "25.7",
                    "chapter": "chapter25",
                    "source_paddle_raw": str(raw_path),
                    "page": 1,
                    "raw_bbox": [200, 200, 880, 560],
                    "caption_block": {"bbox": [200, 580, 880, 690]},
                }
            ],
            structured_dir=structured_dir,
            out_dir=out_dir,
        )

        self.assertEqual(audit["placed"][0]["chunk"], "chapter25_013")
        self.assertEqual(audit["removed_existing_figure_blocks"][0]["chunk"], "chapter25_014")

        combined = ""
        for path in out_dir.glob("chapter25_*.json"):
            combined += path.read_text(encoding="utf-8")
        self.assertEqual(combined.count("[[FIGURE:25.7]]"), 1)


if __name__ == "__main__":
    unittest.main()
