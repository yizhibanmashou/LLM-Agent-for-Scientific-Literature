import json
import unittest
from pathlib import Path
from uuid import uuid4

from textbook_exporter import export_textbooks


TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "textbook_exporter"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class TextbookExporterTests(unittest.TestCase):
    def test_exports_chapter_markdown_with_expanded_assets_and_chapter_scoped_inline_table(self):
        root = make_test_workspace("expanded_assets")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "Chapter 25: Introduction",
                    "heading_path": ["Introduction"],
                    "display_heading": "Introduction",
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "Opening text [[SEE_FORMULA:25.1]] cites [[SEE_TABLE:25.1]]. "
                            "Now expand [[TABLE:inline_2]] and [[SEE_EXAMPLE:25.1]]."
                        ),
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_002.json",
            {
                "id": "chapter25_002",
                "metadata": {
                    "chapter": "chapter25",
                    "section": "Deterministic Theory",
                    "heading_path": ["Section A", "Subsection B"],
                    "display_heading": "Subsection B",
                },
                "blocks": [
                    {"type": "derivation", "content": "Second chunk text."},
                ],
            },
        )
        write_json(
            structured_dir / "formula_library.json",
            {
                "metadata": {"total_formulas": 1},
                "formulas": [
                    {
                        "id": "25.1",
                        "label_format": "(25.1)",
                        "latex": "x=y",
                        "source": {"unit_id": "chapter25_block_001", "subsection": "Introduction"},
                    }
                ],
            },
        )
        write_json(
            structured_dir / "table_library.json",
            {
                "metadata": {"total_tables": 3},
                "tables": [
                    {
                        "id": "inline_2",
                        "label_format": "Inline Table 2",
                        "title": "Wrong chapter table",
                        "rows": [["Wrong"], ["chapter30"]],
                        "html": "",
                        "source": {"chapter": "chapter30", "unit_id": "chapter30_001", "page": 30},
                    },
                    {
                        "id": "25.1",
                        "label_format": "Table 25.1",
                        "title": "Numbered table title",
                        "rows": [["A", "B"], ["1", "2"]],
                        "html": "",
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_001", "page": 5},
                    },
                    {
                        "id": "inline_2",
                        "label_format": "Inline Table 2",
                        "title": "Correct chapter inline table",
                        "rows": [["Population", "Value"], ["Selected", "4.65"]],
                        "html": "",
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_001", "page": 6},
                    },
                ],
            },
        )
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "25.1",
                        "example_ref": "25.1",
                        "chapter": "chapter25",
                        "label": "Example 25.1",
                        "source_file": "chapter25_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "content_markdown": "Example content uses [[TABLE:inline_2]] and [[SEE_FORMULA:25.1]].",
                    }
                ],
            },
        )

        results = export_textbooks(structured_dir, out_dir, chapters={"chapter25"})

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_count, 2)
        output = (out_dir / "chapter25_textbook.md").read_text(encoding="utf-8")
        self.assertIn("# Chapter 25 Textbook Mapping", output)
        self.assertNotIn("Auto-generated from", output)
        self.assertLess(output.index("## chapter25_001"), output.index("## chapter25_002"))
        self.assertIn("## chapter25_002 · Section A / Subsection B", output)
        self.assertIn("**[推导 Derivation]**", output)
        self.assertIn("> **Formula (25.1)** · `25.1` · source: `chapter25_block_001`", output)
        self.assertIn("cites Table 25.1.", output)
        self.assertIn("> **Inline Table 2** · `inline_2` · page 6 · source: `chapter25_001`", output)
        self.assertIn("> Correct chapter inline table", output)
        self.assertIn("Population | Value", output)
        self.assertIn("> **Example 25.1** · ref: `25.1`", output)
        self.assertIn("*[Table inline_2 - see above]*", output)
        self.assertNotIn("Wrong chapter table", output)

    def test_exports_katex_safe_operator_macros(self):
        root = make_test_workspace("katex_safe_macros")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter14_001.json",
            {
                "id": "chapter14_001",
                "metadata": {"chapter": "chapter14", "section": "Binary Traits"},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "If $ \\ell(z) = p $, then $ \\logit(p) = z $ and [[SEE_FORMULA:14.15a]].",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "formula_library.json",
            {
                "formulas": [
                    {
                        "id": "14.15a",
                        "label_format": "(14.15a)",
                        "latex": "\\logit(p)=\\ln(p/(1-p))",
                        "source": {"chapter": "chapter14", "unit_id": "chapter14_001"},
                    }
                ]
            },
        )
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter14"})
        output = (out_dir / "chapter14_textbook.md").read_text(encoding="utf-8")

        self.assertIn("\\operatorname{logit}(p)", output)
        self.assertNotIn("\\logit(p)", output)

    def test_exports_katex_safe_spacing_commands(self):
        root = make_test_workspace("katex_safe_spacing")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter18_001.json",
            {
                "id": "chapter18_001",
                "metadata": {"chapter": "chapter18", "section": "Variance"},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "For covariance $$ V_{ij}=i\\cdot h^2\\qquadfor i<j $$",
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter18"})
        output = (out_dir / "chapter18_textbook.md").read_text(encoding="utf-8")

        self.assertIn("\\qquad for i<j", output)
        self.assertNotIn("\\qquadfor", output)

    def test_exports_katex_safe_nested_subscripts(self):
        root = make_test_workspace("katex_safe_nested_subscripts")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter17_001.json",
            {
                "id": "chapter17_001",
                "metadata": {"chapter": "chapter17", "section": "Environmental variance"},
                "blocks": [{"type": "discussion", "content": "Expand [[TABLE:17.1]]."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "17.1",
                        "label_format": "Table 17.1",
                        "title": "Where $ A_m \\sim N(\\mu_{A_m}, \\sigma_A_m^2) $ and $ A_v \\sim N(\\mu_{A_v}, \\sigma_A_v^2) $.",
                        "rows": [["Trait"], ["$ \\sigma_A_m^2 + \\sigma_A_v^2 $"]],
                        "html": "",
                        "source": {"chapter": "chapter17", "unit_id": "chapter17_001", "page": 7},
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter17"})
        output = (out_dir / "chapter17_textbook.md").read_text(encoding="utf-8")

        self.assertIn("\\sigma_{A_m}^2", output)
        self.assertIn("\\sigma_{A_v}^2", output)
        self.assertNotIn("\\sigma_A_m^2", output)
        self.assertNotIn("\\sigma_A_v^2", output)

    def test_formula_table_cells_expand_formula_references(self):
        root = make_test_workspace("formula_table")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter16_001.json",
            {
                "id": "chapter16_001",
                "metadata": {"chapter": "chapter16", "section": "Truncation"},
                "blocks": [{"type": "discussion", "content": "Expand [[TABLE:16.1]]."}],
            },
        )
        write_json(
            structured_dir / "formula_library.json",
            {
                "formulas": [
                    {
                        "id": "16.11a",
                        "label_format": "(16.11a)",
                        "latex": "\\kappa=a",
                        "source": {"chapter": "chapter16", "unit_id": "chapter16_block_001"},
                    }
                ]
            },
        )
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "16.1",
                        "label_format": "Table 16.1",
                        "title": "Formula table",
                        "table_type": "formula_table",
                        "rows": [["Scheme", "Formula"], ["Directional", "[[SEE_FORMULA:16.11a]]"]],
                        "html": "",
                        "source": {"chapter": "chapter16", "unit_id": "chapter16_001"},
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter16"})
        output = (out_dir / "chapter16_textbook.md").read_text(encoding="utf-8")

        self.assertIn("Directional | $$\\kappa=a$$", output)
        self.assertNotIn("[[SEE_FORMULA:16.11a]]", output)

    def test_table_title_normalizes_nested_subscripts_for_katex(self):
        root = make_test_workspace("nested_subscripts")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter17_001.json",
            {
                "id": "chapter17_001",
                "metadata": {"chapter": "chapter17", "section": "Variance"},
                "blocks": [{"type": "discussion", "content": "Expand [[TABLE:17.1]]."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "17.1",
                        "label_format": "Table 17.1",
                        "title": "$ A_m \\sim N(\\mu_{A_m}, \\sigma_A_m^2) $ and $ A_v \\sim N(\\mu_{A_v}, \\sigma_A_v^2) $",
                        "table_type": "numbered",
                        "rows": [["Model", "$ \\sigma_A_m^2 $"]],
                        "html": "",
                        "source": {"chapter": "chapter17", "unit_id": "chapter17_001"},
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter17"})
        output = (out_dir / "chapter17_textbook.md").read_text(encoding="utf-8")

        self.assertIn("\\sigma_{A_m}^2", output)
        self.assertIn("\\sigma_{A_v}^2", output)
        self.assertNotIn("\\sigma_A_m^2", output)
        self.assertNotIn("\\sigma_A_v^2", output)

    def test_list_table_exports_without_markdown_header_separator(self):
        root = make_test_workspace("list_table")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter20_001.json",
            {
                "id": "chapter20_001",
                "metadata": {"chapter": "chapter20", "section": "Animal models"},
                "blocks": [{"type": "discussion", "content": "Expand [[TABLE:20.1]]."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "20.1",
                        "label_format": "Table 20.1",
                        "title": "Design limitations.",
                        "table_type": "list_table",
                        "rows": [["Pedigree ascertainment."], ["Open population structure."]],
                        "html": "",
                        "source": {"chapter": "chapter20", "unit_id": "chapter20_001"},
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter20"})
        output = (out_dir / "chapter20_textbook.md").read_text(encoding="utf-8")

        self.assertIn("> Pedigree ascertainment.", output)
        self.assertIn("> Open population structure.", output)
        self.assertNotIn("> ---", output)

    def test_html_table_fallback_stays_inside_table_block(self):
        root = make_test_workspace("html_table_block")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter23_001.json",
            {
                "id": "chapter23_001",
                "metadata": {"chapter": "chapter23", "section": "Tables"},
                "blocks": [{"type": "table", "content": "[[TABLE:23.2]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "example_library.json", {"examples": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "23.2",
                        "label_format": "Table 23.2",
                        "title": "Complex header table.",
                        "rows": [["i", "sigma", "group"], ["0", "1.00"]],
                        "html": "<table><tr><td>i</td><td>1.00</td></tr></table>",
                        "source": {"chapter": "chapter23", "unit_id": "chapter23_001", "page": 13},
                    }
                ]
            },
        )

        export_textbooks(structured_dir, out_dir, chapters={"chapter23"})
        output = (out_dir / "chapter23_textbook.md").read_text(encoding="utf-8")

        self.assertIn("> <table><tr><td>i</td><td>1.00</td></tr></table>", output)

    def test_exports_tex_title_parent_for_numbered_chapter_subtitle(self):
        root = make_test_workspace("tex_title_parent")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        tex_path = root / "chapter14_full" / "main.tex"
        tex_path.parent.mkdir(parents=True)
        tex_path.write_text(
            "\\title{Short-term Changes in the Mean:}\n"
            "\\begin{document}\n"
            "\\section{2. Truncation and Threshold Selection}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )

        write_json(
            structured_dir / "chapter14_001.json",
            {
                "id": "chapter14_001",
                "metadata": {
                    "chapter": "chapter14",
                    "section": "2. Truncation and Threshold Selection",
                    "heading_path": ["2. Truncation and Threshold Selection"],
                    "source_file": str(tex_path),
                },
                "blocks": [{"type": "discussion", "content": "Opening."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter14"})
        output = (out_dir / "chapter14_textbook.md").read_text(encoding="utf-8")

        self.assertIn(
            "## chapter14_001 · Short-term Changes in the Mean: 2. Truncation and Threshold Selection",
            output,
        )


if __name__ == "__main__":
    unittest.main()
