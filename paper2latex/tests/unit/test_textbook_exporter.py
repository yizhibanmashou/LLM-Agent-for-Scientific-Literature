import json
import os
import unittest
from pathlib import Path
from uuid import uuid4

from textbook_exporter import export_textbooks
from textbook_exporter.exporter import canonicalize_display_math, inline_table_math


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
    def test_table_cells_convert_display_delimiters_to_inline_math(self):
        source = "<table><tr><td>$$ x^2 $$</td><td>$ y $</td></tr></table>"
        self.assertEqual(
            inline_table_math(source),
            "<table><tr><td>$ x^2 $</td><td>$ y $</td></tr></table>",
        )

    def test_canonicalizes_display_math_without_absorbing_inline_prose(self):
        source = "Before $ p=1 $. Given by $$ x=y $$ where $ y=1 $. $$ a=b $$ $$ c=d $$"
        rendered = canonicalize_display_math(source)
        self.assertIn("Before $ p=1 $. Given by\n\n$$\nx=y\n$$\n\nwhere $ y=1 $.", rendered)
        self.assertIn("$$\na=b\n$$\n\n$$\nc=d\n$$", rendered)
        self.assertNotIn("$$ $$", rendered)

    def test_canonicalizer_preserves_unclosed_delimiter_for_validation(self):
        source = "Text before $$ x=y without a close"
        self.assertEqual(canonicalize_display_math(source), source)

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
                            "It also cites [[SEE_EXAMPLE:25.1]]. "
                            "Now expand [[TABLE:inline_2]] and [[EXAMPLE:25.1]]."
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
        self.assertNotIn("> **Formula (25.1)** · `25.1` · source: `chapter25_block_001`", output)
        self.assertIn(
            "Opening text *(See Equation 25.1.)* cites *[See Table 25.1 at the end of this section.]*.",
            output,
        )
        self.assertNotIn("[[SEE_TABLE:25.1]]", output)
        self.assertIn("It also cites *(See Example 25.1.)*.", output)
        self.assertIn("> **Inline Table 2** · `inline_2` · page 6 · source: `chapter25_001`", output)
        self.assertIn("> Correct chapter inline table", output)
        self.assertIn("Population | Value", output)
        self.assertIn("> **Example 25.1** · ref: `25.1`", output)
        self.assertGreaterEqual(output.count("**Inline Table 2** · `inline_2` · page 6 · source: `chapter25_001`"), 2)
        self.assertNotIn("Wrong chapter table", output)

    def test_sinks_numbered_tables_to_end_of_subsection_but_keeps_inline_tables_in_place(self):
        root = make_test_workspace("sink_numbered_tables")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter2_001.json",
            {
                "id": "chapter2_001",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Moments"],
                    "display_heading": "Moments",
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "Opening cites [[TABLE:2.1]] and expands [[TABLE:inline_1]].",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter2_002.json",
            {
                "id": "chapter2_002",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Moments"],
                    "display_heading": "Moments",
                },
                "blocks": [{"type": "discussion", "content": "Last paragraph in same subsection."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "2.1",
                        "label_format": "Table 2.1",
                        "title": "Numbered table",
                        "rows": [["Trait", "Value"], ["weight", "10"]],
                        "source": {
                            "chapter": "chapter2",
                            "unit_id": "chapter2_001",
                            "subsection": "Moments",
                            "page": 3,
                        },
                    },
                    {
                        "id": "inline_1",
                        "label_format": "Inline Table 1",
                        "title": "Inline table",
                        "table_type": "inline",
                        "rows": [["A", "B"], ["1", "2"]],
                        "source": {
                            "chapter": "chapter2",
                            "unit_id": "chapter2_001",
                            "subsection": "Moments",
                            "page": 4,
                        },
                    },
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter2"})

        output = (out_dir / "chapter2_textbook.md").read_text(encoding="utf-8")
        self.assertIn("Opening cites", output)
        self.assertIn("*[See Table 2.1 at the end of this section.]*", output)
        self.assertNotIn("[[SEE_TABLE:2.1]]", output)
        self.assertIn("and expands", output)
        self.assertIn("> **Inline Table 1**", output)
        self.assertEqual(output.count("> **Table 2.1**"), 1)
        self.assertLess(output.index("## chapter2_002"), output.index("> **Table 2.1**"))
        self.assertLess(output.index("> **Inline Table 1**"), output.index("## chapter2_002"))

    def test_moves_owned_raw_html_table_to_subsection_end(self):
        root = make_test_workspace("sink_raw_html_table")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        raw_html = "<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>"
        inline_raw_html = "<table><tr><td>example</td><td>value</td></tr></table>"
        write_json(
            structured_dir / "chapter2_001.json",
            {
                "id": "chapter2_001",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Distribution", "Moments"],
                    "display_heading": "Moments",
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            f"Text before. {raw_html} Text after still in subsection. "
                            f"Example keeps {inline_raw_html} in place."
                        ),
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter2_002.json",
            {
                "id": "chapter2_002",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Distribution", "Moments"],
                    "display_heading": "Moments",
                },
                "blocks": [{"type": "discussion", "content": "Final prose."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "2.1",
                        "label_format": "Table 2.1",
                        "title": "Recovered from raw html",
                        "table_type": "missing",
                        "rows": [],
                        "html": "",
                        "source": {
                            "chapter": "chapter2",
                            "unit_id": "chapter2_001",
                            "subsection": "Moments",
                        },
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter2"})

        output = (out_dir / "chapter2_textbook.md").read_text(encoding="utf-8")
        self.assertIn("Text before.", output)
        self.assertIn("Text after still in subsection.", output)
        self.assertLess(output.index("## chapter2_002"), output.index("> **Table 2.1**"))
        self.assertIn("> <table><tr><td>A</td><td>B</td></tr>", output)
        self.assertIn("Example keeps", output)
        self.assertLess(output.index("Example keeps"), output.index("## chapter2_002"))
        self.assertEqual(output.count("<table>"), 2)

    def test_recovers_late_split_raw_html_table_for_previous_formal_table(self):
        root = make_test_workspace("sink_late_split_raw_html_table")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        first_half = "<table><tr><td>first</td></tr></table>"
        second_half = "<table><tr><td>second</td></tr></table>"
        example_table = "<table><tr><td>example</td></tr></table>"
        write_json(
            structured_dir / "chapter2_001.json",
            {
                "id": "chapter2_001",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Distribution", "Moments"],
                    "display_heading": "Moments",
                },
                "blocks": [{"type": "discussion", "content": "The owner section cites a formal table."}],
            },
        )
        write_json(
            structured_dir / "chapter2_002.json",
            {
                "id": "chapter2_002",
                "metadata": {
                    "chapter": "chapter2",
                    "heading_path": ["Distribution", "Next"],
                    "display_heading": "Next",
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            f"{first_half} {second_half} "
                            f"Example 1. This calculation keeps {example_table} inline."
                        ),
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "2.1",
                        "label_format": "Table 2.1",
                        "title": "Late recovered table",
                        "table_type": "missing",
                        "rows": [],
                        "html": "",
                        "source": {
                            "chapter": "chapter2",
                            "unit_id": "chapter2_001",
                            "subsection": "Moments",
                        },
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter2"})

        output = (out_dir / "chapter2_textbook.md").read_text(encoding="utf-8")
        table_block_pos = output.index("> **Table 2.1**")
        self.assertLess(table_block_pos, output.index("## chapter2_002"))
        self.assertGreater(output.index("> <table><tr><td>first</td></tr></table>"), table_block_pos)
        self.assertGreater(output.index("> <table><tr><td>second</td></tr></table>"), table_block_pos)
        self.assertIn("Example 1. This calculation keeps <table><tr><td>example</td></tr></table> inline.", output)

    def test_renders_chapter_heading_with_metadata_title(self):
        root = make_test_workspace("chapter_heading_metadata")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter22_001.json",
            {
                "id": "chapter22_001",
                "metadata": {
                    "chapter": "chapter22",
                    "chapter_title": "Associative Effects: Competition, Social Interactions, Group and Kin Selection",
                    "section": "Introduction",
                    "heading_path": ["Introduction"],
                },
                "blocks": [{"type": "discussion", "content": "Opening."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter22"})

        output = (out_dir / "chapter22_textbook.md").read_text(encoding="utf-8")
        self.assertTrue(
            output.startswith(
                "# Chapter 22 · Associative Effects: Competition, Social Interactions, Group and Kin Selection"
            )
        )

    def test_exports_prefixed_chapter_files_with_numeric_filter(self):
        root = make_test_workspace("prefixed_chapter")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "Evolution_chapter1_001.json",
            {
                "id": "Evolution_chapter1_001",
                "metadata": {
                    "chapter": "Evolution_chapter1",
                    "chapter_title": "Changes in Quantitative Traits Over Time",
                    "heading_path": [
                        "1: Changes in Quantitative Traits Over Time",
                        "Introduction",
                    ],
                    "display_heading": "Introduction",
                },
                "blocks": [{"type": "discussion", "content": "Opening [[FIGURE:1.1]]."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})
        write_json(
            structured_dir / "figure_library.json",
            {
                "figures": {
                    "1.1": {
                        "id": "1.1",
                        "chapter": "Evolution_chapter1",
                        "display_ref": "1.1",
                        "caption": "Figure 1.1 Caption.",
                        "page": 4,
                    }
                }
            },
        )

        results = export_textbooks(structured_dir, out_dir, chapters={"1"})

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chapter, "Evolution_chapter1")
        output_path = out_dir / "Evolution_chapter1_textbook.md"
        self.assertTrue(output_path.exists())
        output = output_path.read_text(encoding="utf-8")
        self.assertIn("# Chapter 1", output)
        self.assertIn("## Evolution_chapter1_001", output)
        self.assertNotIn("1: Changes in Quantitative Traits Over Time / Introduction", output)
        self.assertIn("source: `Evolution_chapter1`", output)
        self.assertNotIn("source: `evolution_chapter1`", output)

    def test_expands_figure_placeholders_from_figure_library(self):
        root = make_test_workspace("figure_placeholders")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        figure_root = root / "figure_library_output"
        figures_dir = figure_root / "figures"
        figures_dir.mkdir(parents=True)
        (figures_dir / "A5.1.png").write_bytes(b"png")

        write_json(
            structured_dir / "appendix5_001.json",
            {
                "id": "appendix5_001",
                "metadata": {
                    "chapter": "appendix5",
                    "section": "Vectors",
                    "heading_path": ["Vectors"],
                },
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "See [[SEE_FIGURE:A5.1]].\n\n[[FIGURE:A5.1]]",
                    },
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})
        write_json(
            figure_root / "figure_library.json",
            {
                "figures": {
                    "A5.1": {
                        "id": "A5.1",
                        "chapter": "appendix5",
                        "asset_path": "figures/A5.1.png",
                        "caption": "Figure A5.1 Some basic geometric concepts of vectors.",
                        "page": 2,
                    }
                }
            },
        )

        export_textbooks(
            structured_dir,
            out_dir,
            chapters={"appendix5"},
            figure_library=figure_root / "figure_library.json",
        )

        output = (out_dir / "appendix5_textbook.md").read_text(encoding="utf-8")
        self.assertIn("See Figure A5.1.", output)
        self.assertIn("> **Figure A5.1** · page 2 · source: `appendix5`", output)
        self.assertIn("![Figure A5.1](", output)
        self.assertIn("figures/A5.1.png", output)
        self.assertIn("> Figure A5.1 Some basic geometric concepts of vectors.", output)
        self.assertTrue((out_dir / "figures" / "A5.1.png").exists())

    def test_see_example_placeholder_stays_reference_even_in_example_block(self):
        root = make_test_workspace("example_block_see_example_reference")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {"chapter": "chapter6", "display_heading": "Price"},
                "blocks": [
                    {"type": "discussion", "content": "Plain prose cites [[SEE_EXAMPLE:6.1]]."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:6.1]]"},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "examples": [
                    {
                        "example_id": "6.1",
                        "chapter": "chapter6",
                        "label": "Example 6.1",
                        "source_file": "chapter6_001.json",
                        "content_markdown": "Example 6.1. Expanded body.",
                    }
                ]
            },
        )

        export_textbooks(structured_dir, out_dir, chapters={"chapter6"})

        output = (out_dir / "chapter6_textbook.md").read_text(encoding="utf-8")
        self.assertIn("Plain prose cites *(See Example 6.1.)*.", output)
        self.assertNotIn("[[SEE_EXAMPLE:6.1]]", output)
        self.assertNotIn("> **Example 6.1**", output)

    def test_example_block_expands_example_placeholder(self):
        root = make_test_workspace("example_block_example")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {"chapter": "chapter6", "display_heading": "Price"},
                "blocks": [{"type": "example", "content": "[[EXAMPLE:6.1]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "examples": [
                    {
                        "example_id": "6.1",
                        "chapter": "chapter6",
                        "label": "Example 6.1",
                        "source_file": "chapter6_001.json",
                        "content_markdown": "Example 6.1. Expanded body.",
                    }
                ]
            },
        )

        export_textbooks(structured_dir, out_dir, chapters={"chapter6"})

        output = (out_dir / "chapter6_textbook.md").read_text(encoding="utf-8")
        self.assertIn("> **Example 6.1**", output)
        self.assertIn("> Example 6.1. Expanded body.", output)

    def test_skips_empty_structured_chunks(self):
        root = make_test_workspace("skip_empty_chunks")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {"chapter": "chapter6", "display_heading": "Empty"},
                "blocks": [],
            },
        )
        write_json(
            structured_dir / "chapter6_002.json",
            {
                "id": "chapter6_002",
                "metadata": {"chapter": "chapter6", "display_heading": "Real"},
                "blocks": [{"type": "discussion", "content": "Real content."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter6"})

        output = (out_dir / "chapter6_textbook.md").read_text(encoding="utf-8")
        self.assertNotIn("chapter6_001", output)
        self.assertIn("chapter6_002", output)
        self.assertIn("Real content.", output)

    def test_example_internal_figure_counts_as_explicit_placement(self):
        root = make_test_workspace("example_internal_figure")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        figure_root = root / "figure_library_output"
        figures_dir = figure_root / "figures"
        figures_dir.mkdir(parents=True)
        (figures_dir / "28.4.png").write_bytes(b"png")

        write_json(
            structured_dir / "chapter28_001.json",
            {
                "id": "chapter28_001",
                "metadata": {"chapter": "chapter28", "display_heading": "Examples"},
                "blocks": [{"type": "example", "content": "[[EXAMPLE:28.8]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "examples": [
                    {
                        "example_id": "28.8",
                        "chapter": "chapter28",
                        "label": "Example 28.8",
                        "source_file": "chapter28_001.json",
                        "content_markdown": (
                            "Example 28.8. As Figure 28.4A shows one panel. "
                            "[[FIGURE:28.4]] Figure 28.4B is discussed again."
                        ),
                    }
                ]
            },
        )
        write_json(
            figure_root / "figure_library.json",
            {
                "figures": {
                    "28.4": {
                        "id": "28.4",
                        "chapter": "chapter28",
                        "asset_path": "figures/28.4.png",
                        "caption": "Figure 28.4 Caption.",
                        "page": 35,
                    }
                }
            },
        )

        export_textbooks(
            structured_dir,
            out_dir,
            chapters={"chapter28"},
            figure_library=figure_root / "figure_library.json",
        )

        output = (out_dir / "chapter28_textbook.md").read_text(encoding="utf-8")
        self.assertEqual(output.count("> **Figure 28.4**"), 1)
        self.assertIn("![Figure 28.4](figures/28.4.png)", output)

    def test_auto_expands_first_in_chapter_text_figure_reference(self):
        root = make_test_workspace("auto_text_figure")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        figure_asset = root / "figures" / "26.1.png"
        figure_asset.parent.mkdir(parents=True, exist_ok=True)
        figure_asset.write_bytes(b"png")

        write_json(
            structured_dir / "chapter26_001.json",
            {
                "id": "chapter26_001",
                "metadata": {"chapter": "chapter26", "display_heading": "Figures"},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "Values are plotted in Figure 26.1. Figure 26.1 is discussed again.",
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})
        write_json(
            root / "figure_library.json",
            {
                "figures": {
                    "26.1": {
                        "id": "26.1",
                        "chapter": "chapter26",
                        "asset_path": "figures/26.1.png",
                        "caption": "Figure 26.1 Fixation probability.",
                        "page": 3,
                    }
                }
            },
        )

        export_textbooks(structured_dir, out_dir, chapters={"chapter26"})

        output = (out_dir / "chapter26_textbook.md").read_text(encoding="utf-8")
        self.assertEqual(output.count("> **Figure 26.1**"), 1)
        self.assertIn("![Figure 26.1](figures/26.1.png)", output)
        self.assertTrue((out_dir / "figures" / "26.1.png").exists())

    def test_renders_chapter_heading_from_intro_heading_fallback(self):
        root = make_test_workspace("chapter_heading_intro_fallback")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter27_001.json",
            {
                "id": "chapter27_001",
                "metadata": {
                    "chapter": "chapter27",
                    "section": "Long-term Response: Introduction",
                    "section_level_1": "Long-term Response: Introduction",
                    "display_heading": "Long-term Response: Introduction",
                    "heading_path": ["Long-term Response: Introduction"],
                },
                "blocks": [{"type": "discussion", "content": "Opening."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter27"})

        output = (out_dir / "chapter27_textbook.md").read_text(encoding="utf-8")
        self.assertTrue(output.startswith("# Chapter 27 · Long-term Response"))

    def test_renders_chapter_heading_from_raw_multiline_doc_title(self):
        root = make_test_workspace("chapter_heading_raw_doc_title")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        source_file = root / "paddle_output" / "chapter27_full" / "main.tex"
        raw_file = source_file.parent / "intermediate" / "paddle_raw_response.json"

        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text("\\title{Long-term Response:}\n", encoding="utf-8")
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_text(
            json.dumps(
                [
                    {
                        "parsing_res_list": [
                            {
                                "block_label": "doc_title",
                                "block_content": "27",
                                "block_order": 1,
                                "block_bbox": [486, 200, 551, 248],
                            },
                            {
                                "block_label": "doc_title",
                                "block_content": "Long-term Response:",
                                "block_order": 2,
                                "block_bbox": [328, 306, 713, 346],
                            },
                            {
                                "block_label": "doc_title",
                                "block_content": "3. Adaptive Walks",
                                "block_order": 3,
                                "block_bbox": [371, 359, 667, 397],
                            },
                        ]
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        write_json(
            structured_dir / "chapter27_001.json",
            {
                "id": "chapter27_001",
                "metadata": {
                    "chapter": "chapter27",
                    "source_file": str(source_file),
                    "section": "Long-term Response: Introduction",
                },
                "blocks": [{"type": "discussion", "content": "Opening."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter27"})

        output = (out_dir / "chapter27_textbook.md").read_text(encoding="utf-8")
        self.assertTrue(output.startswith("# Chapter 27 · Long-term Response: 3. Adaptive Walks"))

    def test_renders_chapter_heading_from_data_paddle_output_when_source_file_is_stale_tmp_path(self):
        root = make_test_workspace("chapter_heading_stale_tmp_source")
        structured_dir = root / "structured"
        out_dir = root / "textbook"
        source_file = root / "data" / "paddle_output" / "chapter25_full" / "main.tex"
        raw_file = source_file.parent / "intermediate" / "paddle_raw_response.json"

        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text("\\title{25}\n", encoding="utf-8")
        raw_file.parent.mkdir(parents=True, exist_ok=True)
        raw_file.write_text(
            json.dumps(
                [
                    {
                        "parsing_res_list": [
                            {
                                "block_label": "doc_title",
                                "block_content": "25",
                                "block_order": 1,
                                "block_bbox": [486, 200, 551, 248],
                            },
                            {
                                "block_label": "doc_title",
                                "block_content": "Long-term Response:\n1. Deterministic Aspects",
                                "block_order": 2,
                                "block_bbox": [328, 306, 713, 397],
                            },
                        ]
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {
                    "chapter": "chapter25",
                    "source_file": "tmp\\paddle_output\\chapter25_full\\main.tex",
                    "section": "Introduction",
                },
                "blocks": [{"type": "discussion", "content": "Opening."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        previous_cwd = Path.cwd()
        try:
            os.chdir(root)
            export_textbooks(structured_dir, out_dir, chapters={"chapter25"})
        finally:
            os.chdir(previous_cwd)

        output = (out_dir / "chapter25_textbook.md").read_text(encoding="utf-8")
        self.assertTrue(output.startswith("# Chapter 25 · Long-term Response: 1. Deterministic Aspects"))

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
                        "markdown_body": "| Scheme | Formula |\n| --- | --- |\n| Directional | [[SEE_FORMULA:16.11a]] |",
                        "html": "",
                        "source": {"chapter": "chapter16", "unit_id": "chapter16_001"},
                    }
                ]
            },
        )
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter16"})
        output = (out_dir / "chapter16_textbook.md").read_text(encoding="utf-8")

        self.assertIn("Directional | $\\kappa=a$", output)
        self.assertNotIn("[[SEE_FORMULA:16.11a]]", output)
        self.assertEqual(output.count("Directional | $\\kappa=a$"), 1)

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

    def test_table_markdown_body_is_rendered_after_html_table(self):
        root = make_test_workspace("table_markdown_body")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {"chapter": "chapter25", "section": "Tables"},
                "blocks": [{"type": "table", "content": "[[TABLE:25.2]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "example_library.json", {"examples": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "25.2",
                        "label_format": "Table 25.2",
                        "title": "Major locus parameters.",
                        "rows": [["Genotype"], ["bb", "$ \\overline{W}_{0} $"]],
                        "html": "<table><tr><td>Genotype</td><td>Fitness</td></tr></table>",
                        "markdown_body": (
                            "$$ \\overline{W}_{i}=a $$\n\n"
                            "Mean fitness:\n\n"
                            "$$ \\overline{W}=b $$\n\n"
                            "Mean phenotype:\n\n"
                            "$$ \\overline{z}=c $$"
                        ),
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_001", "page": 11},
                    }
                ]
            },
        )

        export_textbooks(structured_dir, out_dir, chapters={"chapter25"})
        output = (out_dir / "chapter25_textbook.md").read_text(encoding="utf-8")

        self.assertIn("> <table><tr><td>Genotype</td><td>Fitness</td></tr></table>", output)
        self.assertIn("> Mean fitness:", output)
        self.assertIn("> $$ \\overline{W}=b $$", output)
        self.assertIn("> Mean phenotype:", output)
        self.assertIn("> $$ \\overline{z}=c $$", output)

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

    def test_strips_placeholder_chapter_intro_parent_from_heading_path(self):
        root = make_test_workspace("placeholder_intro_parent")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter25_004.json",
            {
                "id": "chapter25_004",
                "metadata": {
                    "chapter": "chapter25",
                    "heading_path": [
                        "25: Introduction",
                        "DETERMINISTIC SINGLE-LOCUS THEORY",
                        "Expected Contribution From a Single Locus",
                    ],
                    "display_heading": "Expected Contribution From a Single Locus",
                },
                "blocks": [{"type": "discussion", "content": "Body."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter25"})
        output = (out_dir / "chapter25_textbook.md").read_text(encoding="utf-8")

        self.assertIn(
            "## chapter25_004 · DETERMINISTIC SINGLE-LOCUS THEORY / Expected Contribution From a Single Locus",
            output,
        )
        self.assertNotIn("25: Introduction / DETERMINISTIC", output)

    def test_strips_numbered_chapter_title_parent_from_heading_path(self):
        root = make_test_workspace("chapter_title_parent")
        structured_dir = root / "structured"
        out_dir = root / "textbook"

        write_json(
            structured_dir / "chapter21_006.json",
            {
                "id": "chapter21_006",
                "metadata": {
                    "chapter": "chapter21",
                    "chapter_title": "Family-Based Selection",
                    "heading_path": [
                        "21: Family-Based Selection",
                        "DETAILS OF FAMILY-BASED SELECTION SCHEMES",
                        "Selection and Recombination Units",
                    ],
                    "display_heading": "Selection and Recombination Units",
                },
                "blocks": [{"type": "discussion", "content": "Body."}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(structured_dir / "example_library.json", {"examples": []})

        export_textbooks(structured_dir, out_dir, chapters={"chapter21"})
        output = (out_dir / "chapter21_textbook.md").read_text(encoding="utf-8")

        self.assertIn(
            "## chapter21_006 · DETAILS OF FAMILY-BASED SELECTION SCHEMES / Selection and Recombination Units",
            output,
        )
        self.assertNotIn("21: Family-Based Selection / DETAILS", output)


if __name__ == "__main__":
    unittest.main()
