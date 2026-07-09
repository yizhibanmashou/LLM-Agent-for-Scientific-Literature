import json
import unittest
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

import fitz

from knowledge_engineering.pipeline.structured_fusion import apply_structured_fusion, audit_block_content
from knowledge_engineering.processors.ocr_evidence import build_ocr_evidence_index
from knowledge_engineering.processors.structured_repair import validate_candidate


TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "structured_fusion"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_minimal_structured_dir(structured_dir: Path, table_title: str, table_rows: list[list[str]]) -> None:
    write_json(
        structured_dir / "chapter25_001.json",
        {
            "id": "chapter25_001",
            "metadata": {
                "chapter": "chapter25",
                "section": "Deterministic single-locus theory",
                "subsections": [],
                "source_file": "tmp/paddle_output/chapter25_full/main.tex",
                "source_title": "Evolution and Selection of Quantitative Traits",
                "formula_references": [],
                "table_references": ["25.1"],
            },
            "blocks": [
                {
                    "type": "discussion",
                    "content": "The expressions are summarized in [[SEE_TABLE:25.1]].",
                }
            ],
        },
    )
    write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
    write_json(
        structured_dir / "table_library.json",
        {
            "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
            "tables": [
                {
                    "id": "25.1",
                    "label_format": "Table 25.1",
                    "title": table_title,
                    "table_type": "numbered",
                    "html": "<table><tr><td>wrong</td><td>body</td></tr></table>",
                    "rows": table_rows,
                    "source": {"chapter": "chapter25", "unit_id": "chapter25_001"},
                    "description": None,
                }
            ],
        },
    )


class StructuredFusionTests(unittest.TestCase):
    def test_table_id_with_wrong_caption_is_binding_mismatch(self):
        root = make_test_workspace("caption_mismatch")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_minimal_structured_dir(
            structured_dir,
            "Table 25.2 Incorrect caption bound to table 25.1",
            [["wrong", "body"]],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            artifacts_dir=artifacts_dir,
            dry_run=True,
        )

        self.assertEqual(summary["table_binding_stats"].get("table_binding_mismatch"), 1)
        events = read_jsonl(artifacts_dir / "structured_fusion" / "structured_fusion_table_binding_events.jsonl")
        self.assertEqual(len(events), 1)
        self.assertIn("table_binding_mismatch", events[0]["issue_codes"])
        self.assertEqual(events[0]["severity"], "fatal")

    def test_paddle_and_glm_table_evidence_create_replacement_candidate(self):
        root = make_test_workspace("ocr_candidate")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        paddle_dir = root / "paddle"
        artifacts_dir = root / "artifacts"
        table_html = (
            "<table><tr><td></td><td>Total Contribution</td><td>p0.5</td></tr>"
            "<tr><td>B additive</td><td>2a(1-p0)</td><td>(1+p0)/2</td></tr>"
            "<tr><td>B dominant</td><td>2a(1-p0)^2</td><td>1-sqrt(...)</td></tr></table>"
        )
        caption = "Table 25.1 Total contribution to the selection limit and the allele frequency p0.5."
        write_minimal_structured_dir(
            structured_dir,
            "Table 25.2 Incorrect caption bound to table 25.1",
            [["wrong", "body"]],
        )
        write_json(
            glm_dir / "chapter25.json",
            [
                [
                    {"index": 0, "label": "text", "content": caption, "bbox_2d": [10, 10, 200, 30]},
                    {"index": 1, "label": "table", "content": table_html, "bbox_2d": [10, 35, 220, 120]},
                ]
            ],
        )
        write_json(
            paddle_dir / "chapter25_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": caption,
                                "block_bbox": [10, 10, 200, 30],
                                "block_order": 1,
                            },
                            {
                                "block_label": "table",
                                "block_content": table_html,
                                "block_bbox": [10, 35, 220, 120],
                                "block_order": 2,
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            paddle_output_dir=paddle_dir,
            artifacts_dir=artifacts_dir,
            dry_run=True,
        )

        self.assertEqual(summary["table_binding_stats"].get("table_replacement_candidates"), 1)
        events = read_jsonl(artifacts_dir / "structured_fusion" / "structured_fusion_table_binding_events.jsonl")
        self.assertEqual(events[0]["action"], "auto_replace")
        self.assertIsNotNone(events[0]["replacement_candidate"])
        self.assertGreaterEqual(events[0]["channel_agreement"]["overall"], 0.72)

    def test_glm_grouped_math_header_repairs_paddle_header_ocr_error(self):
        root = make_test_workspace("grouped_header")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        artifacts_dir = root / "artifacts"
        caption = (
            "Table 23.2 Coefficients for Equation 23.14, the selection unit-offspring covariance under $ S_{i,j} $ "
            "family selection. The $ \\sigma_{ADI} $ coefficient is also a function of j."
        )
        write_json(
            structured_dir / "chapter23_001.json",
            {
                "id": "chapter23_001",
                "metadata": {"chapter": "chapter23", "formula_references": [], "table_references": ["23.2"]},
                "blocks": [{"type": "table", "content": "[[TABLE:23.2]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "23.2",
                        "label_format": "Table 23.2",
                        "title": caption,
                        "table_type": "numbered",
                        "html": (
                            "<table><tr><td rowspan=\"2\">i</td><td rowspan=\"2\">$ \\sigma_{A}^{2} $</td>"
                            "<td colspan=\"6\">Coefficient on $ \\sigma_{A} $ for $ j=1 $</td></tr>"
                            "<tr><td>$ i+1 $</td><td>$ i+2 $</td><td>$ i+3 $</td><td>$ i+4 $</td><td>$ i+5 $</td><td>$ \\infty $</td></tr>"
                            "<tr><td>0</td><td>1.00</td><td>0.50</td><td>0.75</td><td>0.88</td><td>0.94</td><td>0.97</td><td>1.00</td></tr></table>"
                        ),
                        "rows": [
                            ["i", "$ \\sigma_{A}^{2} $", "Coefficient on $ \\sigma_{A} $ for $ j=1 $"],
                            ["$ i+1 $", "$ i+2 $", "$ i+3 $", "$ i+4 $", "$ i+5 $", "$ \\infty $"],
                            ["0", "1.00", "0.50", "0.75", "0.88", "0.94", "0.97", "1.00"],
                            ["1", "1.50", "1.25", "1.38", "1.44", "1.47", "1.48", "1.50"],
                        ],
                        "source": {"chapter": "chapter23", "unit_id": "chapter23_001"},
                    }
                ],
            },
        )
        write_json(
            glm_dir / "chapter23.json",
            [
                [
                    {"index": 0, "label": "text", "content": caption, "bbox_2d": [10, 10, 200, 30]},
                    {
                        "index": 1,
                        "label": "table",
                        "content": (
                            "<table border=\"1\"><tr><td></td><td></td><td colspan=\"6\">Coefficient on $\\sigma_{ADI}$ for $j=$</td></tr>"
                            "<tr><td>$i</td><td>$\\sigma_{A}^{2}$</td><td>$i+1$</td><td>$i+2$</td><td>$i+3$</td><td>$i+4$</td><td>$i+5$</td><td>$\\infty$</td></tr>"
                            "<tr><td>0</td><td>1.00</td><td>0.50</td><td>0.75</td><td>0.88</td><td>0.94</td><td>0.97</td><td>1.00</td></tr>"
                            "<tr><td>1</td><td>1.50</td><td>1.25</td><td>1.38</td><td>1.44</td><td>1.47</td><td>1.48</td><td>1.50</td></tr></table>"
                        ),
                        "bbox_2d": [10, 35, 220, 150],
                    },
                ]
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            artifacts_dir=artifacts_dir,
            enable_ocr_table_repair=True,
        )

        self.assertEqual(summary["table_binding_stats"].get("stronger_ocr_grouped_header_replacements_applied"), 1)
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertTrue(any("\\sigma_{ADI}" in cell for row in table["rows"] for cell in row))
        self.assertIn("$ j=i+1 $", table["rows"][0][2])
        self.assertNotIn("Coefficient on $ \\sigma_{A} $ for $ j=1 $", json.dumps(table["rows"], ensure_ascii=False))

    def test_visual_pdf_evidence_enables_paddle_visual_table_channel(self):
        root = make_test_workspace("paddle_visual")
        pdf_dir = root / "pdf"
        paddle_dir = root / "paddle"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            paddle_dir / "chapter6_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "width": 1191,
                    "height": 1684,
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 6.2 Heritabilities and coefficients of additive genetic variation.",
                                "block_bbox": [286, 208, 1059, 273],
                                "block_order": 1,
                            },
                            {
                                "block_label": "table",
                                "block_content": "<table><tr><td>Trait</td><td>n</td><td>h2</td><td>CVA</td><td>CVR</td></tr>"
                                "<tr><td>A</td><td>1</td><td>0.1</td><td>2</td><td>3</td></tr></table>",
                                "block_bbox": [369, 286, 971, 415],
                                "block_order": 2,
                            },
                        ]
                    },
                }
            ],
        )
        doc = fitz.open()
        doc.new_page(width=1191, height=1684)
        doc.save(pdf_dir / "chapter6.pdf")
        doc.close()

        with patch("knowledge_engineering.processors.ocr_evidence._detect_visual_horizontal_rules") as detect_rules:
            detect_rules.return_value = [
                {"bbox": [294.0, 281.0, 1054.0, 282.0], "coverage": 0.6, "max_continuous_span": 700, "max_row_dark_ratio": 0.8},
                {"bbox": [294.0, 418.0, 1054.0, 419.0], "coverage": 0.6, "max_continuous_span": 700, "max_row_dark_ratio": 0.8},
            ]
            index = build_ocr_evidence_index(
                pdf_dir=pdf_dir,
                paddle_output_dir=paddle_dir,
                chapters=["chapter6"],
            )

        channels = {e.source_channel for e in index.evidences}
        self.assertIn("paddle", channels)
        self.assertIn("paddle_visual", channels)

    def test_multiple_tables_on_one_page_bind_by_reading_order(self):
        root = make_test_workspace("multi_table_order")
        structured_dir = root / "structured"
        paddle_dir = root / "paddle"
        artifacts_dir = root / "artifacts"
        table_a = "<table><tr><td>Species</td><td>Total</td></tr><tr><td>Drosophila</td><td>61</td></tr></table>"
        table_b = "<table><tr><td>Generations</td><td>n</td></tr><tr><td>1-5</td><td>44</td></tr></table>"
        write_json(
            structured_dir / "chapter18_001.json",
            {
                "id": "chapter18_001",
                "metadata": {
                    "chapter": "chapter18",
                    "section": "Sheridan's Analysis",
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": [],
                    "table_references": ["18.2", "18.3"],
                },
                "blocks": [
                    {"type": "discussion", "content": "[[TABLE:18.2]]"},
                    {"type": "discussion", "content": "[[TABLE:18.3]]"},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 2, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "18.2",
                        "label_format": "Table 18.2",
                        "title": "Table 18.2 (body not recovered from raw layout)",
                        "table_type": "missing",
                        "html": "",
                        "rows": [],
                        "source": {
                            "chapter": "chapter18",
                            "unit_id": "chapter18_001",
                            "extraction_channel": "missing_table_body_stub",
                        },
                        "description": None,
                    },
                    {
                        "id": "18.3",
                        "label_format": "Table 18.3",
                        "title": "Table 18.3 Agreement by duration.",
                        "table_type": "numbered",
                        "html": table_a,
                        "rows": [["Species", "Total"], ["Drosophila", "61"]],
                        "source": {"chapter": "chapter18", "unit_id": "chapter18_001"},
                        "description": None,
                    },
                ],
            },
        )
        write_json(
            paddle_dir / "chapter18_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 18.2 Tests of significance between estimates.",
                                "block_bbox": [10, 10, 200, 40],
                                "block_order": 1,
                            },
                            {
                                "block_label": "table",
                                "block_content": table_a,
                                "block_bbox": [10, 50, 200, 100],
                                "block_order": 2,
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 18.3 Agreement by duration.",
                                "block_bbox": [10, 120, 200, 140],
                                "block_order": 3,
                            },
                            {
                                "block_label": "table",
                                "block_content": table_b,
                                "block_bbox": [10, 150, 200, 200],
                                "block_order": 4,
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            paddle_output_dir=paddle_dir,
            artifacts_dir=artifacts_dir,
            enable_ocr_table_repair=True,
            dry_run=False,
        )

        self.assertEqual(summary["table_binding_stats"].get("missing_table_stub_recovered"), 1)
        table_library = json.loads((structured_dir / "table_library.json").read_text(encoding="utf-8"))
        tables = {table["id"]: table for table in table_library["tables"]}
        self.assertEqual(tables["18.2"]["rows"][1], ["Drosophila", "61"])
        self.assertEqual(tables["18.3"]["rows"][1], ["1-5", "44"])

    def test_ocr_table_evidence_does_not_reuse_caption_across_example_boundary(self):
        root = make_test_workspace("ocr_table_example_boundary")
        paddle_dir = root / "paddle"
        formula_table = (
            "<table><tr><td>Selection Scheme</td><td>R/(sigma_A^2 i)</td></tr>"
            "<tr><td>Half-sibs, remnant seed</td><td>formula</td></tr></table>"
        )
        example_table = (
            "<table><tr><td>Selection</td><td>R/i</td><td>f=1/8</td></tr>"
            "<tr><td>Half-sib</td><td>1.581</td><td>1.111</td></tr></table>"
        )
        write_json(
            paddle_dir / "chapter23_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 23.1 The response to family selection.",
                                "block_bbox": [10, 10, 220, 40],
                                "block_order": 1,
                            },
                            {
                                "block_label": "table",
                                "block_content": formula_table,
                                "block_bbox": [10, 50, 220, 120],
                                "block_order": 2,
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "Example 23.1. Using the expression summarized in Table 23.1.",
                                "block_bbox": [10, 150, 220, 180],
                                "block_order": 3,
                            },
                            {
                                "block_label": "table",
                                "block_content": example_table,
                                "block_bbox": [10, 190, 220, 260],
                                "block_order": 4,
                            },
                        ]
                    }
                }
            ],
        )

        index = build_ocr_evidence_index(paddle_output_dir=paddle_dir, chapters=["chapter23"])

        evidences = index.tables(table_id="23.1", chapter="chapter23")
        self.assertEqual(len(evidences), 1)
        self.assertIn("Selection Scheme", evidences[0].body_text)
        self.assertNotIn("1.581", evidences[0].body_text)

    def test_duplicate_physical_table_placeholder_in_same_unit_is_removed(self):
        root = make_test_workspace("same_unit_duplicate_table")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter23_001.json",
            {
                "id": "chapter23_001",
                "metadata": {"chapter": "chapter23", "table_references": ["23.3"]},
                "blocks": [
                    {"type": "table", "content": "[[TABLE:23.3]]"},
                    {"type": "discussion", "content": "Table 23.3 shows the comparison."},
                    {"type": "table", "content": "[[TABLE:23.3]]"},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "23.3",
                        "label_format": "Table 23.3",
                        "title": "Table 23.3 Comparison.",
                        "table_type": "numbered",
                        "rows": [["Type", "R"], ["S1", "1/2"]],
                        "html": "<table><tr><td>Type</td><td>R</td></tr><tr><td>S1</td><td>1/2</td></tr></table>",
                        "source": {"chapter": "chapter23", "unit_id": "chapter23_001"},
                    }
                ]
            },
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            artifacts_dir=artifacts_dir,
            dry_run=False,
        )

        unit = read_json(structured_dir / "chapter23_001.json")
        physical_refs = [block for block in unit["blocks"] if block["content"] == "[[TABLE:23.3]]"]
        self.assertEqual(len(physical_refs), 1)
        self.assertEqual(summary["table_stats"].get("duplicate_physical_table_placeholder_removed_same_unit"), 1)

    def test_formula_table_caption_followed_by_numbered_formulas_recovers_missing_stub(self):
        root = make_test_workspace("formula_table")
        structured_dir = root / "structured"
        paddle_dir = root / "paddle"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter16_001.json",
            {
                "id": "chapter16_001",
                "metadata": {
                    "chapter": "chapter16",
                    "section": "CHANGES IN VARIANCE UNDER TRUNCATION SELECTION",
                    "subsections": [],
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": ["16.11a", "16.11b", "16.11c", "16.12a"],
                    "table_references": ["16.1"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The cases are summarized in [[SEE_TABLE:16.1]].",
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 0, "inline_tables": 0},
                "tables": [
                    {
                        "id": "16.1",
                        "label_format": "Table 16.1",
                        "title": "Table 16.1 (body not recovered from raw layout)",
                        "table_type": "missing",
                        "html": "",
                        "rows": [],
                        "source": {
                            "chapter": "chapter16",
                            "unit_id": "chapter16_001",
                            "extraction_channel": "missing_table_body_stub",
                        },
                        "description": None,
                    }
                ],
            },
        )
        write_json(
            paddle_dir / "chapter16_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 16.1 Values of kappa for truncation selection.",
                                "block_bbox": [10, 10, 300, 30],
                                "block_order": 1,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Directional Truncation Selection: Uppermost p saved",
                                "block_bbox": [10, 40, 260, 60],
                                "block_order": 2,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "\\kappa = \\bar{i}(\\bar{i}-x)",
                                "block_bbox": [10, 65, 260, 90],
                                "block_order": 3,
                            },
                            {
                                "block_label": "formula_number",
                                "block_content": "(16.11a)",
                                "block_bbox": [270, 65, 320, 90],
                                "block_order": 4,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Stabilizing Truncation Selection: Middle fraction p of the distribution saved",
                                "block_bbox": [10, 100, 260, 120],
                                "block_order": 5,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "\\kappa = 2\\phi(x)x/p",
                                "block_bbox": [10, 125, 260, 150],
                                "block_order": 6,
                            },
                            {
                                "block_label": "formula_number",
                                "block_content": "(16.11b)",
                                "block_bbox": [270, 125, 320, 150],
                                "block_order": 7,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Disruptive Truncation Selection: Uppermost and lowermost p/2 saved",
                                "block_bbox": [10, 160, 260, 180],
                                "block_order": 8,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "\\kappa = -2\\phi(x)x/p",
                                "block_bbox": [10, 185, 260, 210],
                                "block_order": 9,
                            },
                            {
                                "block_label": "formula_number",
                                "block_content": "(16.11c)",
                                "block_bbox": [270, 185, 320, 210],
                                "block_order": 10,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "d(t+1)=d(t)/2-...",
                                "block_bbox": [10, 220, 260, 245],
                                "block_order": 11,
                            },
                            {
                                "block_label": "formula_number",
                                "block_content": "(16.12a)",
                                "block_bbox": [270, 220, 320, 245],
                                "block_order": 12,
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            paddle_output_dir=paddle_dir,
            artifacts_dir=artifacts_dir,
            dry_run=False,
        )

        self.assertEqual(summary["table_binding_stats"].get("missing_table_stub_recovered"), 1)
        table_library = json.loads((structured_dir / "table_library.json").read_text(encoding="utf-8"))
        table = table_library["tables"][0]
        self.assertEqual(table["table_type"], "formula_table")
        self.assertEqual(table["source"]["table_special_type"], "formula_table")
        body_text = json.dumps(table["rows"], ensure_ascii=False)
        self.assertIn("[[SEE_FORMULA:16.11a]]", body_text)
        self.assertIn("[[SEE_FORMULA:16.11b]]", body_text)
        self.assertIn("[[SEE_FORMULA:16.11c]]", body_text)
        self.assertNotIn("16.12a", body_text)

    def test_formula_table_keeps_split_label_continuation_with_next_formula(self):
        root = make_test_workspace("formula_table_split_label")
        structured_dir = root / "structured"
        paddle_dir = root / "paddle"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter21_001.json",
            {
                "id": "chapter21_001",
                "metadata": {
                    "chapter": "chapter21",
                    "section": "Among-family Selection:",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": ["21.4"],
                },
                "blocks": [{"type": "discussion", "content": "The variances are summarized in [[SEE_TABLE:21.4]]."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 0, "inline_tables": 0},
                "tables": [
                    {
                        "id": "21.4",
                        "label_format": "Table 21.4",
                        "title": "Table 21.4 (body not recovered from raw layout)",
                        "table_type": "missing",
                        "html": "",
                        "rows": [],
                        "source": {
                            "chapter": "chapter21",
                            "unit_id": "chapter21_001",
                            "extraction_channel": "missing_table_body_stub",
                        },
                        "description": None,
                    }
                ],
            },
        )
        write_json(
            paddle_dir / "chapter21_full" / "intermediate" / "paddle_raw_api_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": "Table 21.4 Within- and among-family variances.",
                                "block_bbox": [10, 10, 300, 30],
                                "block_order": 1,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Half-sib among-family variance",
                                "block_bbox": [10, 40, 260, 60],
                                "block_order": 2,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "\\sigma^{2}(\\overline{z}_{HS})=A",
                                "block_bbox": [10, 65, 260, 90],
                                "block_order": 3,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Half-sib with nested full-sibs (nested sibs) among-family variance",
                                "block_bbox": [10, 100, 260, 120],
                                "block_order": 4,
                            },
                            {
                                "block_label": "text",
                                "block_content": "$ (n_f $ females per male, $ n_s $ offspring per female, $ n = n_f n_s $ offspring per male $",
                                "block_bbox": [10, 125, 260, 150],
                                "block_order": 5,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "\\sigma^{2}\\big(\\overline{z}_{HS(FS)}\\big)=B",
                                "block_bbox": [10, 160, 260, 180],
                                "block_order": 6,
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            paddle_output_dir=paddle_dir,
            artifacts_dir=artifacts_dir,
            dry_run=False,
        )

        self.assertEqual(summary["table_binding_stats"].get("missing_table_stub_recovered"), 1)
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["table_type"], "formula_table")
        body_text = json.dumps(table["rows"], ensure_ascii=False)
        self.assertIn("nested full-sibs", body_text)
        self.assertIn("n_f", body_text)
        self.assertIn("\\overline{z}_{HS(FS)}", body_text)

    def test_stronger_formula_table_evidence_replaces_truncated_existing_table(self):
        root = make_test_workspace("formula_table_stronger_evidence")
        structured_dir = root / "structured"
        paddle_dir = root / "paddle"
        artifacts_dir = root / "artifacts"
        caption = "Table 21.4 Within- and among-family variances."
        write_json(
            structured_dir / "chapter21_001.json",
            {
                "id": "chapter21_001",
                "metadata": {
                    "chapter": "chapter21",
                    "section": "Among-family Selection:",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": ["21.4"],
                },
                "blocks": [{"type": "table", "content": "[[TABLE:21.4]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "21.4",
                        "label_format": "Table 21.4",
                        "title": caption,
                        "table_type": "formula_table",
                        "html": "<table><tr><td>Selection scheme</td><td>Formula</td></tr><tr><td>Half-sib among-family variance</td><td>A</td></tr><tr><td>Full-sib among-family variance</td><td>B</td></tr></table>",
                        "rows": [
                            ["Selection scheme", "Formula"],
                            ["Half-sib among-family variance", "A"],
                            ["Full-sib among-family variance", "B"],
                        ],
                        "source": {
                            "chapter": "chapter21",
                            "unit_id": "chapter21_001",
                            "has_physical_placeholder": True,
                            "source_channel": "paddle",
                        },
                    }
                ],
            },
        )
        write_json(
            paddle_dir / "chapter21_full" / "intermediate" / "paddle_raw_api_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "figure_title",
                                "block_content": caption,
                                "block_bbox": [10, 10, 300, 30],
                                "block_order": 1,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Half-sib among-family variance",
                                "block_bbox": [10, 40, 260, 60],
                                "block_order": 2,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "A",
                                "block_bbox": [10, 65, 260, 90],
                                "block_order": 3,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Full-sib among-family variance",
                                "block_bbox": [10, 100, 260, 120],
                                "block_order": 4,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "B",
                                "block_bbox": [10, 125, 260, 150],
                                "block_order": 5,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Half-sib within-family variance",
                                "block_bbox": [10, 160, 260, 180],
                                "block_order": 6,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "C",
                                "block_bbox": [10, 185, 260, 210],
                                "block_order": 7,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Full-sib within-family variance",
                                "block_bbox": [10, 220, 260, 245],
                                "block_order": 8,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "D",
                                "block_bbox": [10, 250, 260, 275],
                                "block_order": 9,
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_structured_fusion(
            structured_dir=structured_dir,
            paddle_output_dir=paddle_dir,
            artifacts_dir=artifacts_dir,
            enable_ocr_table_repair=True,
            dry_run=False,
        )

        self.assertEqual(summary["table_binding_stats"].get("stronger_ocr_table_replacements_applied"), 1)
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["fusion_repair"], "stronger_ocr_table_evidence")
        body_text = json.dumps(table["rows"], ensure_ascii=False)
        self.assertIn("Half-sib within-family variance", body_text)
        self.assertIn("Full-sib within-family variance", body_text)

    def test_table_body_residue_is_replaced_by_physical_placeholder(self):
        root = make_test_workspace("table_body_residue")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter21_001.json",
            {
                "id": "chapter21_001",
                "metadata": {"chapter": "chapter21", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before the table."},
                    {"type": "discussion", "content": "Half-sib among-family variance $$ A $$"},
                    {"type": "discussion", "content": "Full-sib among-family variance $$ B $$"},
                    {"type": "discussion", "content": "Half-sib within-family variance $$ C $$"},
                    {"type": "discussion", "content": "After the table."},
                ],
            },
        )
        write_json(
            structured_dir / "chapter21_002.json",
            {
                "id": "chapter21_002",
                "metadata": {"chapter": "chapter21", "formula_references": [], "table_references": ["21.4"]},
                "blocks": [{"type": "table", "content": "[[TABLE:21.4]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "21.4",
                        "label_format": "Table 21.4",
                        "title": "Table 21.4 Family variances.",
                        "table_type": "formula_table",
                        "html": "<table></table>",
                        "rows": [
                            ["Selection scheme", "Formula"],
                            ["Half-sib among-family variance", "$$ A $$"],
                            ["Full-sib among-family variance", "$$ B $$"],
                            ["Half-sib within-family variance", "$$ C $$"],
                        ],
                        "source": {"chapter": "chapter21", "unit_id": "chapter21_002", "has_physical_placeholder": True},
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        first = read_json(structured_dir / "chapter21_001.json")
        second = read_json(structured_dir / "chapter21_002.json")
        self.assertEqual(
            [block["content"] for block in first["blocks"]],
            ["Before the table.", "[[TABLE:21.4]]", "After the table."],
        )
        self.assertNotIn("[[TABLE:21.4]]", json.dumps(second, ensure_ascii=False))
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter21_001")
        self.assertEqual(summary["table_stats"].get("table_body_residue_placeholders_rebound"), 1)
        self.assertEqual(summary["table_stats"].get("table_body_residue_blocks_removed"), 3)
        self.assertEqual(summary["table_stats"].get("duplicate_table_placeholders_removed"), 1)

    def test_table_body_residue_after_existing_placeholder_is_removed(self):
        root = make_test_workspace("table_body_residue_after_placeholder")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter30_001.json",
            {
                "id": "chapter30_001",
                "metadata": {"chapter": "chapter30", "formula_references": [], "table_references": ["30.1"]},
                "blocks": [
                    {"type": "discussion", "content": "Intro."},
                    {"type": "table", "content": "[[TABLE:30.1]]"},
                    {"type": "discussion", "content": "Differentials measure the covariance between relative fitness and phenotype $$ A $$"},
                    {"type": "discussion", "content": "Gradients measure the amount of direct selection $$ B $$"},
                    {"type": "discussion", "content": "Gradients appear as coefficients in fitness regressions $$ C $$"},
                    {"type": "discussion", "content": "Tail text."},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "30.1",
                        "label_format": "Table 30.1",
                        "title": "Table 30.1 Selection gradients.",
                        "table_type": "numbered",
                        "html": "<table></table>",
                        "rows": [
                            ["Changes in Means", "Changes in Covariances"],
                            ["Differentials measure the covariance between relative fitness and phenotype", "$$ A $$"],
                            ["Gradients measure the amount of direct selection", "$$ B $$"],
                            ["Gradients appear as coefficients in fitness regressions", "$$ C $$"],
                        ],
                        "source": {"chapter": "chapter30", "unit_id": "chapter30_001", "has_physical_placeholder": True},
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter30_001.json")
        self.assertEqual(
            [block["content"] for block in unit["blocks"]],
            ["Intro.", "Tail text.", "[[TABLE:30.1]]"],
        )
        self.assertEqual(summary["table_stats"].get("table_body_residue_placeholders_rebound"), 1)
        self.assertEqual(summary["table_stats"].get("table_body_residue_blocks_removed"), 3)

    def test_numbered_list_table_body_residue_is_replaced_without_swallowing_following_body(self):
        root = make_test_workspace("list_table_body_residue")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter10_001.json",
            {
                "id": "chapter10_001",
                "metadata": {"chapter": "chapter10", "formula_references": [], "table_references": ["10.2"]},
                "blocks": [
                    {
                        "type": "derivation",
                        "content": (
                            "$ alpha $ The fraction of substitutions that are adaptive "
                            "$ gamma $ The scaled strength of selection, $ 2Ne s $ "
                            "$ mu $ The total per-site mutation rate "
                            "$ p_b $ The fraction of new mutations at a site that are advantageous "
                            "the actual mutation rate, $ mu $. Two types of mutations contribute to replacement substitutions."
                        ),
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "10.2",
                        "label_format": "Table 10.2",
                        "title": "Table 10.2 Summary of adaptive parameters.",
                        "table_type": "list_table",
                        "html": "<table></table>",
                        "rows": [
                            ["$ alpha $ The fraction of substitutions that are adaptive"],
                            ["$ gamma $ The scaled strength of selection, $ 2 N_e s $"],
                            ["$ mu $ The total per-site mutation rate"],
                            ["$ p_b $ The fraction of new mutations at a site that are advantageous"],
                        ],
                        "source": {
                            "chapter": "chapter10",
                            "unit_id": "chapter10_001",
                            "following_body": {
                                "label": "text",
                                "content": (
                                    "the actual mutation rate, $ mu $. Two types of mutations "
                                    "contribute to replacement substitutions."
                                ),
                            },
                        },
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter10_001.json")
        self.assertEqual(unit["blocks"][0]["content"], "[[TABLE:10.2]]")
        self.assertIn("the actual mutation rate", unit["blocks"][1]["content"])
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["physical_placeholder_inserted_by"], "structured_fusion_list_table_materializer")
        self.assertEqual(summary["table_stats"].get("list_table_placeholders_inserted"), 1)

    def test_duplicate_physical_table_placeholder_created_by_residue_rebinder_is_removed(self):
        root = make_test_workspace("table_residue_late_duplicate")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter18_001.json",
            {
                "id": "chapter18_001",
                "metadata": {"chapter": "chapter18", "formula_references": [], "table_references": ["18.7"]},
                "blocks": [
                    {"type": "discussion", "content": "Intro."},
                    {"type": "table", "content": "[[TABLE:18.7]]"},
                    {"type": "discussion", "content": "Selection in a single direction without a control line $$ A $$"},
                    {"type": "discussion", "content": "Selection in a single direction with a control line $$ B $$"},
                    {"type": "discussion", "content": "Divergent selection without a control line $$ C $$"},
                    {"type": "discussion", "content": "Tail."},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "18.7",
                        "label_format": "Table 18.7",
                        "title": "Table 18.7 Coefficients.",
                        "table_type": "formula_table",
                        "html": "<table></table>",
                        "rows": [
                            ["Selection scheme", "Formula"],
                            ["Selection in a single direction without a control line", "$$ A $$"],
                            ["Selection in a single direction with a control line", "$$ B $$"],
                            ["Divergent selection without a control line", "$$ C $$"],
                        ],
                        "source": {"chapter": "chapter18", "unit_id": "chapter18_001", "has_physical_placeholder": True},
                    }
                ],
            },
        )
        unit = read_json(structured_dir / "chapter18_001.json")
        self.assertEqual(
            len([block for block in unit["blocks"] if block["content"] == "[[TABLE:18.7]]"]),
            1,
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter18_001.json")
        placeholders = [block for block in unit["blocks"] if block["content"] == "[[TABLE:18.7]]"]
        self.assertEqual(len(placeholders), 1)
        self.assertEqual(summary["table_stats"].get("table_body_residue_placeholders_rebound"), 1)

    def test_numbered_page_top_table_moves_to_physical_owner_unit_end(self):
        root = make_test_workspace("numbered_table_physical_owner_end")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter18_001.json",
            {
                "id": "chapter18_001",
                "metadata": {
                    "chapter": "chapter18",
                    "heading_path": ["EXPERIMENTAL EVALUATION", "Most Traits Respond to Selection"],
                    "formula_references": [],
                    "table_references": ["18.1"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "[[SEE_TABLE:18.1]] genetic variation) for specific combinations "
                            "of traits, despite significant heritabilities."
                        ),
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter18_002.json",
            {
                "id": "chapter18_002",
                "metadata": {
                    "chapter": "chapter18",
                    "heading_path": ["EXPERIMENTAL EVALUATION", "Sheridan's Analysis"],
                    "formula_references": [],
                    "table_references": ["18.1"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "[[TABLE:18.1]] shows the fit for the remaining experiments.",
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "18.1",
                        "label_format": "Table 18.1",
                        "title": "Table 18.1 Comparison of realized heritabilities.",
                        "table_type": "numbered",
                        "html": "<table></table>",
                        "rows": [["Species", "n"], ["Drosophila", "60"]],
                        "source": {
                            "chapter": "chapter18",
                            "unit_id": "chapter18_001",
                            "bbox": [144, 338, 890, 692],
                            "caption_bbox": [131, 206, 905, 325],
                            "following_body": {
                                "label": "text",
                                "content": (
                                    "genetic variation) for specific combinations of traits, "
                                    "despite significant heritabilities"
                                ),
                            },
                        },
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        owner = read_json(structured_dir / "chapter18_001.json")
        next_unit = read_json(structured_dir / "chapter18_002.json")
        self.assertEqual(owner["blocks"][-1], {"type": "table", "content": "[[TABLE:18.1]]"})
        self.assertIn("[[SEE_TABLE:18.1]] genetic variation", owner["blocks"][0]["content"])
        self.assertNotIn("[[TABLE:18.1]]", json.dumps(next_unit, ensure_ascii=False))
        self.assertIn("[[SEE_TABLE:18.1]] shows the fit", next_unit["blocks"][0]["content"])
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter18_001")
        self.assertEqual(
            table["source"]["physical_placeholder_inserted_by"],
            "structured_fusion_physical_owner_unit_end",
        )
        self.assertEqual(summary["table_stats"].get("embedded_table_placeholders_demoted_to_see_refs"), 1)

    def test_numbered_table_residue_does_not_rebind_across_units(self):
        root = make_test_workspace("numbered_table_residue_cross_unit_guard")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter21_001.json",
            {
                "id": "chapter21_001",
                "metadata": {"chapter": "chapter21", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Family selection is discussed here."},
                    {"type": "discussion", "content": "Half-sib family selection can be better in some settings."},
                    {"type": "discussion", "content": "Full-sib family selection is another option."},
                ],
            },
        )
        write_json(
            structured_dir / "chapter21_002.json",
            {
                "id": "chapter21_002",
                "metadata": {"chapter": "chapter21", "formula_references": [], "table_references": ["21.1"]},
                "blocks": [{"type": "table", "content": "[[TABLE:21.1]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "21.1",
                        "label_format": "Table 21.1",
                        "title": "Table 21.1 Family-based selection schemes.",
                        "table_type": "numbered",
                        "html": "<table></table>",
                        "rows": [
                            ["Among-family Selection", "Recombination Unit", "Selection Unit"],
                            ["Family selection", "Measured sib", ""],
                            ["Half-sib family selection", "", "$ \\overline{z}_{HS} $"],
                            ["Full-sib family selection", "", "$ \\overline{z}_{FS} $"],
                        ],
                        "source": {"chapter": "chapter21", "unit_id": "chapter21_002", "has_physical_placeholder": True},
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        first = read_json(structured_dir / "chapter21_001.json")
        second = read_json(structured_dir / "chapter21_002.json")
        self.assertNotIn("[[TABLE:21.1]]", json.dumps(first, ensure_ascii=False))
        self.assertEqual(second["blocks"], [{"type": "table", "content": "[[TABLE:21.1]]"}])
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter21_002")
        self.assertNotIn("table_body_residue_placeholders_rebound", summary["table_stats"])

    def test_lw_table_reference_is_external_not_missing_local_table(self):
        issues = audit_block_content(
            content="This covariance is given by LW [[SEE_TABLE:7.3]] for full sibs.",
            block_type="discussion",
            known_formula_ids=set(),
            known_table_ids=set(),
        )

        codes = [issue["code"] for issue in issues]
        self.assertIn("external_reference", codes)
        self.assertNotIn("table_reference_missing", codes)

    def test_table_body_anchor_at_block_start_is_not_orphan_fragment(self):
        issues = audit_block_content(
            content="[[TABLE:25.1]] for $ p_{\\beta} $, with expressions summarized in [[SEE_TABLE:25.1]].",
            block_type="discussion",
            known_formula_ids=set(),
            known_table_ids={"25.1"},
        )

        self.assertNotIn("orphan_table_fragment", [issue["code"] for issue in issues])

    def test_inline_table_placeholder_is_a_valid_table_reference(self):
        issues = audit_block_content(
            content="The resulting values become [[TABLE:inline_1]]",
            block_type="discussion",
            known_formula_ids=set(),
            known_table_ids={"inline_1"},
        )

        self.assertNotIn("table_reference_missing", [issue["code"] for issue in issues])
        self.assertNotIn("orphan_table_fragment", [issue["code"] for issue in issues])

    def test_fusion_preserves_section_level_metadata(self):
        root = make_test_workspace("heading_metadata")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "DETERMINISTIC SINGLE-LOCUS THEORY",
                    "subsections": ["Expected Contribution From a Single Locus"],
                    "source_file": "tmp/paddle_output/chapter25_full/main.tex",
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": [],
                    "table_references": [],
                    "section_level_1": "DETERMINISTIC SINGLE-LOCUS THEORY",
                    "section_level_2": "Expected Contribution From a Single Locus",
                    "heading_path": [
                        "DETERMINISTIC SINGLE-LOCUS THEORY",
                        "Expected Contribution From a Single Locus",
                    ],
                    "display_heading": "Expected Contribution From a Single Locus",
                },
                "blocks": [{"type": "discussion", "content": "Stable content."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {"metadata": {"total_tables": 0, "numbered_tables": 0, "inline_tables": 0}, "tables": []},
        )

        apply_structured_fusion(
            structured_dir=structured_dir,
            enable_ocr_table_evidence=False,
        )

        metadata = json.loads((structured_dir / "chapter25_001.json").read_text(encoding="utf-8"))["metadata"]
        self.assertEqual(metadata["section"], "DETERMINISTIC SINGLE-LOCUS THEORY")
        self.assertEqual(metadata["subsections"], ["Expected Contribution From a Single Locus"])
        self.assertEqual(metadata["section_level_1"], "DETERMINISTIC SINGLE-LOCUS THEORY")
        self.assertEqual(metadata["section_level_2"], "Expected Contribution From a Single Locus")
        self.assertEqual(
            metadata["heading_path"],
            [
                "DETERMINISTIC SINGLE-LOCUS THEORY",
                "Expected Contribution From a Single Locus",
            ],
        )
        self.assertEqual(metadata["display_heading"], "Expected Contribution From a Single Locus")

    def test_numbered_table_append_requires_unit_level_evidence(self):
        root = make_test_workspace("numbered_table_append_guard")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter26_001.json",
            {
                "id": "chapter26_001",
                "metadata": {"chapter": "chapter26", "formula_references": [], "table_references": []},
                "blocks": [{"type": "discussion", "content": "This unit mentions selection but not the table caption."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "26.3",
                        "label_format": "Table 26.3",
                        "title": "Table 26.3 Expected responses under different schemes.",
                        "table_type": "numbered",
                        "html": "<table><tr><td>Scheme</td><td>Response</td></tr></table>",
                        "rows": [["Scheme", "Response"], ["Mass", "1.0"]],
                        "source": {
                            "chapter": "chapter26",
                            "unit_id": "chapter26_001",
                            "extraction_channel": "paddle_raw",
                        },
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter26_001.json")
        self.assertNotIn("[[TABLE:26.3]]", json.dumps(unit, ensure_ascii=False))
        self.assertEqual(summary["table_stats"].get("numbered_table_placeholders_deferred_no_unit_evidence"), 1)

    def test_page_top_float_table_uses_preceding_body_not_following_heading(self):
        root = make_test_workspace("top_float_table_owner")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter27_011.json",
            {
                "id": "chapter27_011",
                "metadata": {
                    "chapter": "chapter27",
                    "section": "Structure of Adaptive Walks Under the SSWM Model",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": ["27.1"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "The prior section says experiments with microbes attempted to test "
                            "the Gillespie-Orr prediction."
                        ),
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter27_012.json",
            {
                "id": "chapter27_012",
                "metadata": {
                    "chapter": "chapter27",
                    "section": "The Fitness Distribution of Beneficial Alleles",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": [],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The Fitness Distribution of Beneficial Alleles",
                    },
                    {
                        "type": "discussion",
                        "content": "Much of our discussion starts a new section.",
                    },
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "27.1",
                        "label_format": "Table 27.1",
                        "title": "Table 27.1 Summary of several bacterial and viral experiments.",
                        "table_type": "numbered",
                        "html": "<table><tr><td>Species</td><td>Effects</td></tr><tr><td>Escherichia coli</td><td>Exponential</td></tr></table>",
                        "rows": [["Species", "Effects"], ["Escherichia coli", "Exponential"]],
                        "source": {
                            "chapter": "chapter27",
                            "unit_id": "chapter27_012",
                            "page": 18,
                            "bbox": [144, 503, 916, 871],
                            "caption_bbox": [133, 209, 905, 484],
                            "following_body": {
                                "label": "paragraph_title",
                                "content": "The Fitness Distribution of Beneficial Alleles",
                                "bbox": [133, 911, 537, 934],
                                "index": 4,
                            },
                            "preceding_body": {
                                "label": "text",
                                "content": (
                                    "The prior section says experiments with microbes attempted to test "
                                    "the Gillespie-Orr prediction."
                                ),
                                "bbox": [132, 100, 904, 180],
                                "index": 1,
                            },
                            "extraction_channel": "paddle_visual",
                        },
                    }
                ],
            },
        )

        apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit_011 = read_json(structured_dir / "chapter27_011.json")
        unit_012 = read_json(structured_dir / "chapter27_012.json")
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter27_011")
        self.assertIn("[[TABLE:27.1]]", json.dumps(unit_011, ensure_ascii=False))
        self.assertNotIn("[[TABLE:27.1]]", json.dumps(unit_012, ensure_ascii=False))

    def test_page_top_float_table_without_preceding_body_uses_previous_chunk(self):
        root = make_test_workspace("top_float_table_previous_chunk")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter27_011.json",
            {
                "id": "chapter27_011",
                "metadata": {
                    "chapter": "chapter27",
                    "section": "Structure of Adaptive Walks Under the SSWM Model",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": ["27.1"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The prior section ends before a page-top floating table.",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter27_012.json",
            {
                "id": "chapter27_012",
                "metadata": {
                    "chapter": "chapter27",
                    "section": "The Fitness Distribution of Beneficial Alleles",
                    "subsections": [],
                    "formula_references": [],
                    "table_references": [],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The Fitness Distribution of Beneficial Alleles",
                    },
                    {
                        "type": "discussion",
                        "content": "Much of our discussion starts a new section.",
                    },
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "27.1",
                        "label_format": "Table 27.1",
                        "title": "Table 27.1 Summary of several bacterial and viral experiments.",
                        "table_type": "numbered",
                        "html": "<table><tr><td>Species</td><td>Effects</td></tr><tr><td>Escherichia coli</td><td>Exponential</td></tr></table>",
                        "rows": [["Species", "Effects"], ["Escherichia coli", "Exponential"]],
                        "source": {
                            "chapter": "chapter27",
                            "unit_id": "chapter27_012",
                            "page": 18,
                            "bbox": [144, 503, 916, 871],
                            "caption_bbox": [133, 209, 905, 484],
                            "following_body": {
                                "label": "paragraph_title",
                                "content": "The Fitness Distribution of Beneficial Alleles",
                                "bbox": [133, 911, 537, 934],
                                "index": 4,
                            },
                            "extraction_channel": "paddle",
                        },
                    }
                ],
            },
        )

        apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit_011 = read_json(structured_dir / "chapter27_011.json")
        unit_012 = read_json(structured_dir / "chapter27_012.json")
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter27_011")
        self.assertIn("[[TABLE:27.1]]", json.dumps(unit_011, ensure_ascii=False))
        self.assertNotIn("[[TABLE:27.1]]", json.dumps(unit_012, ensure_ascii=False))

    def test_source_claimed_placeholder_is_verified_against_unit_blocks(self):
        root = make_test_workspace("claimed_placeholder_missing")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter16_001.json",
            {
                "id": "chapter16_001",
                "metadata": {"chapter": "chapter16", "formula_references": [], "table_references": ["16.1"]},
                "blocks": [{"type": "discussion", "content": "See [[SEE_TABLE:16.1]] for the coefficients."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "16.1",
                        "label_format": "Table 16.1",
                        "title": "Table 16.1 Changes in the phenotypic variance under truncation selection.",
                        "table_type": "formula_table",
                        "html": "<table><tr><td>Selection scheme</td><td>Formula</td></tr></table>",
                        "rows": [["Selection scheme", "Formula"], ["Directional", "[[SEE_FORMULA:16.11a]]"]],
                        "source": {
                            "chapter": "chapter16",
                            "unit_id": "chapter16_001",
                            "has_physical_placeholder": True,
                            "source_channel": "paddle",
                            "source_path": "tmp/paddle_output/chapter16_full/intermediate/paddle_raw_api_response.json",
                        },
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter16_001.json")
        self.assertEqual(unit["blocks"][-1]["content"], "[[TABLE:16.1]]")
        self.assertEqual(summary["table_stats"].get("numbered_table_source_claimed_placeholder_missing"), 1)
        self.assertEqual(summary["table_stats"].get("numbered_table_placeholders_appended"), 1)

    def test_placeholder_formula_pollution_and_broken_reference_residue_are_removed(self):
        root = make_test_workspace("placeholder_pollution_cleanup")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter8_001.json",
            {
                "id": "chapter8_001",
                "metadata": {"chapter": "chapter8", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "The result is $$ H=H_0 $$ $$ E = mc^2 $$ where the sweep is recent.",
                    },
                    {"type": "discussion", "content": "[[SEE_"},
                    {"type": "discussion", "content": "Tail text."},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(structured_dir / "table_library.json", {"metadata": {"total_tables": 0}, "tables": []})

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        unit = read_json(structured_dir / "chapter8_001.json")
        self.assertEqual(
            [block["content"] for block in unit["blocks"]],
            ["The result is $$ H=H_0 $$ where the sweep is recent.", "Tail text."],
        )
        self.assertEqual(summary["block_stats"].get("blocks_removed"), 1)
        self.assertEqual(summary["block_stats"].get("block_latex_text_normalized"), 1)

    def test_embedded_table_placeholder_is_split_and_prevents_duplicate_append(self):
        root = make_test_workspace("embedded_table_placeholder")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter26_001.json",
            {
                "id": "chapter26_001",
                "metadata": {"chapter": "chapter26", "formula_references": [], "table_references": ["26.1"]},
                "blocks": [{"type": "discussion", "content": "Before [[TABLE:26.1]] after."}],
            },
        )
        write_json(
            structured_dir / "chapter26_002.json",
            {
                "id": "chapter26_002",
                "metadata": {"chapter": "chapter26", "formula_references": [], "table_references": ["26.1"]},
                "blocks": [{"type": "discussion", "content": "Later unit references Table 26.1."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"metadata": {"total_formulas": 0}, "formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 1, "numbered_tables": 1, "inline_tables": 0},
                "tables": [
                    {
                        "id": "26.1",
                        "label_format": "Table 26.1",
                        "title": "Table 26.1 Observed and predicted selection limits.",
                        "table_type": "numbered",
                        "html": "<table><tr><td>A</td><td>B</td></tr></table>",
                        "rows": [["A", "B"], ["1", "2"]],
                        "source": {
                            "chapter": "chapter26",
                            "unit_id": "chapter26_002",
                            "source_channel": "paddle",
                        },
                    }
                ],
            },
        )

        summary = apply_structured_fusion(structured_dir=structured_dir, enable_ocr_table_evidence=False)

        first = read_json(structured_dir / "chapter26_001.json")
        second = read_json(structured_dir / "chapter26_002.json")
        self.assertEqual([block["content"] for block in first["blocks"]], ["Before [[SEE_TABLE:26.1]] after.", "[[TABLE:26.1]]"])
        self.assertNotIn("[[TABLE:26.1]]", json.dumps(second, ensure_ascii=False))
        table = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(table["source"]["unit_id"], "chapter26_001")
        self.assertEqual(summary["table_stats"].get("embedded_table_placeholders_demoted_to_see_refs"), 1)
        self.assertEqual(summary["table_stats"].get("numbered_table_placeholders_appended"), 1)

    def test_structured_references_are_not_placeholder_false_positives(self):
        discussion_issues = audit_block_content(
            content=(
                "See [[SEE_TABLE:17.1]], [[SEE_TABLE:17.2]], and [[SEE_FORMULA:17.3]] "
                "for the full comparison."
            ),
            block_type="discussion",
            known_formula_ids={"17.3"},
            known_table_ids={"17.1", "17.2"},
        )
        self.assertNotIn("placeholder_in_discussion", [issue["code"] for issue in discussion_issues])

        derivation_issues = audit_block_content(
            content="Hence, [[SEE_FORMULA:5.1]]",
            block_type="derivation",
            known_formula_ids={"5.1"},
            known_table_ids=set(),
        )
        self.assertNotIn("derivation_placeholder_only_text", [issue["code"] for issue in derivation_issues])

    def test_orphan_fragments_and_ocr_residue_still_flag(self):
        orphan_issues = audit_block_content(
            content="[[TABLE:5.2]]).",
            block_type="discussion",
            known_formula_ids=set(),
            known_table_ids={"5.2"},
        )
        self.assertIn("orphan_table_fragment", [issue["code"] for issue in orphan_issues])

        residue_issues = audit_block_content(
            content="[h] [[SEE_FORMULA:11.16]]",
            block_type="derivation",
            known_formula_ids={"11.16"},
            known_table_ids=set(),
        )
        codes = [issue["code"] for issue in residue_issues]
        self.assertIn("ocr_residual_marker", codes)
        self.assertIn("derivation_placeholder_only_text", codes)

    def test_short_heading_is_not_very_short_block(self):
        issues = audit_block_content(
            content="Diffusion Theory",
            block_type="discussion",
            known_formula_ids=set(),
            known_table_ids=set(),
        )
        self.assertNotIn("very_short_block", [issue["code"] for issue in issues])

    def test_short_table_header_evidence_expands_from_following_blocks(self):
        root = make_test_workspace("table_expansion")
        paddle_dir = root / "paddle"
        caption = "Table 30.1 Analogous features of directional and quadratic differentials and gradients. Details are in the text."
        table_html = (
            "<table><tr><td>Changes in Means</td><td>Changes in Covariances</td></tr>"
            "<tr><td>(Directional Selection)</td><td>(Quadratic Selection)</td></tr></table>"
        )
        write_json(
            paddle_dir / "chapter30_full" / "intermediate" / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {"block_label": "figure_title", "block_content": caption, "block_bbox": [0, 0, 200, 20]},
                            {"block_label": "table", "block_content": table_html, "block_bbox": [0, 25, 200, 50]},
                            {
                                "block_label": "text",
                                "block_content": "Differentials measure the covariance between relative fitness and phenotype",
                                "block_bbox": [0, 60, 200, 80],
                                "block_order": 1,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "$$ S_i = sigma[w,z_i] $$",
                                "block_bbox": [0, 85, 90, 105],
                                "block_order": 2,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "$$ C_ij = sigma[w,(z_i-mu_i)(z_j-mu_j)] $$",
                                "block_bbox": [100, 85, 200, 105],
                                "block_order": 3,
                            },
                            {
                                "block_label": "text",
                                "block_content": "Gradients appear as coefficients in fitness regressions",
                                "block_bbox": [0, 115, 200, 135],
                                "block_order": 4,
                            },
                            {
                                "block_label": "display_formula",
                                "block_content": "$$ w(z)=1+beta^T(z-mu) $$",
                                "block_bbox": [0, 140, 200, 160],
                                "block_order": 5,
                            },
                            {
                                "block_label": "paragraph_title",
                                "block_content": "Estimation, Hypothesis Testing, and Confidence Intervals",
                                "block_bbox": [0, 170, 200, 190],
                                "block_order": 6,
                            },
                        ]
                    }
                }
            ],
        )

        evidence_index = build_ocr_evidence_index(paddle_output_dir=paddle_dir, chapters={"chapter30"})
        evidence = evidence_index.tables(table_id="30.1", chapter="chapter30")[0]

        self.assertGreater(len(evidence.rows), 2)
        self.assertIn("Differentials measure the covariance between relative fitness and phenotype", evidence.body_text)
        self.assertIn("Gradients appear as coefficients in fitness regressions", evidence.body_text)
        self.assertTrue(evidence.source_payload["table_body_expanded_from_following_blocks"])

    def test_glm_markdown_list_table_is_evidence(self):
        root = make_test_workspace("glm_list_table")
        glm_dir = root / "glm"
        glm_dir.mkdir(parents=True)
        (glm_dir / "chapter40.md").write_text(
            """
Intro paragraph.

<div align="center">

Table 40.1 Design limitations when applying animal models.

</div>

The relationship matrix, A, must be estimated.

Pedigree errors result in bias and lower power.

Open population structure.

Immigration from outside of the study area complicates interpretation.

The next ordinary paragraph starts here and should not be table body.
""".strip(),
            encoding="utf-8",
        )

        evidence_index = build_ocr_evidence_index(glmocr_dir=glm_dir, chapters={"chapter40"})
        evidence = evidence_index.tables(table_id="40.1", chapter="chapter40")[0]

        self.assertEqual(evidence.source_payload["table_special_type"], "list_table")
        self.assertEqual(len(evidence.rows), 4)
        self.assertIn("Pedigree errors result in bias", evidence.body_text)
        self.assertNotIn("ordinary paragraph", evidence.body_text)

    def test_glm_repair_candidate_cannot_drop_structured_placeholders(self):
        valid, reasons = validate_candidate(
            old_content="This depends on [[SEE_FORMULA:12.30c]] and [[SEE_TABLE:12.2]].",
            new_content="This depends on Equation 12.30c and Table 12.2.",
            issue_codes=["unbalanced_inline_math"],
            match_score=0.95,
            review_threshold=0.75,
        )

        self.assertFalse(valid)
        self.assertTrue(any("drops structured placeholders" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
