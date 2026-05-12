import json
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from knowledge_engineering.processors import example_extraction as example_trial
from knowledge_engineering.scripts import build_example_library_trial as example_trial_report

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_RUNTIME_ROOT = PROJECT_ROOT / "tmp" / "test_runtime" / "example_library_trial"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ExampleLibraryTrialTests(unittest.TestCase):
    def test_raw_recovery_joins_cross_page_lowercase_fragment_after_page_noise(self):
        root = make_test_workspace("cross_page_fragment")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter31_001.json",
            {
                "id": "chapter31_001",
                "metadata": {"chapter": "chapter31", "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:31.7]]"}],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": (
                                "Example 31.7. A split example ends the page with increased pupal weight"
                            ),
                            "block_bbox": [0, 1200, 100, 1220],
                        }
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {"block_label": "number", "block_content": "947", "block_bbox": [0, 100, 10, 110]},
                        {"block_label": "header", "block_content": "CHAPTER 31", "block_bbox": [10, 100, 80, 110]},
                        {
                            "block_label": "text",
                            "block_content": "weight thus appears in the continuation sentence.",
                            "block_order": 1,
                            "block_bbox": [0, 180, 100, 200],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Example 31.8. The next example starts here.",
                            "block_order": 2,
                            "block_bbox": [0, 260, 100, 280],
                        },
                    ]
                }
            },
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        self.assertEqual([item.example_id for item in examples], ["31.7"])
        self.assertIn("pupal weight thus appears", examples[0].content_markdown)
        self.assertNotIn("weight weight", examples[0].content_markdown)
        self.assertNotIn("CHAPTER 31", examples[0].content_markdown)

    def test_raw_recovery_keeps_table_ref_chapter_scoped_and_stops_before_next_topic(self):
        root = make_test_workspace("table_and_body")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter32_001.json",
            {
                "id": "chapter32_001",
                "metadata": {"chapter": "chapter32", "table_references": ["inline_7"]},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:32.9]]"}],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>earlier</td></tr></table>",
                            "block_bbox": [0, 100, 100, 120],
                        },
                        {
                            "block_label": "footer",
                            "block_content": (
                                "Example 32.9. Consider the following values from a selection ex-"
                            ),
                            "block_bbox": [0, 1420, 100, 1440],
                        },
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {"block_label": "header", "block_content": "CHAPTER 32", "block_bbox": [0, 100, 100, 120]},
                        {
                            "block_label": "figure_title",
                            "block_content": "periment by Reeve and Robertson:",
                            "block_bbox": [0, 180, 100, 200],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>Population</td><td>Value</td></tr></table>",
                            "block_bbox": [0, 220, 100, 260],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The selected line shows the key explanatory paragraph.",
                            "block_order": 1,
                            "block_bbox": [0, 300, 100, 320],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Why do lethal alleles persist in some selected populations?",
                            "block_order": 2,
                            "block_bbox": [0, 380, 100, 400],
                        },
                    ]
                }
            },
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        self.assertEqual([item.example_id for item in examples], ["32.9"])
        content = examples[0].content_markdown
        self.assertIn("selection experiment by Reeve", content)
        self.assertIn("[[TABLE:inline_2]]", content)
        self.assertNotIn("[[TABLE:32.9]]", content)
        self.assertIn("The selected line shows the key explanatory paragraph.", content)
        self.assertNotIn("Why do lethal alleles persist", content)

    def test_raw_recovery_ignores_inline_example_references(self):
        root = make_test_workspace("inline_reference")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter33_001.json",
            {
                "id": "chapter33_001",
                "metadata": {"chapter": "chapter33", "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:33.10]]"}],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": (
                                "A more formal treatment is given in Example 33.10 and Figure 33.2."
                            ),
                            "block_order": 1,
                            "block_bbox": [0, 100, 100, 120],
                        }
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        self.assertEqual(examples, [])

    def test_existing_example_library_is_quality_preserving_fallback(self):
        root = make_test_workspace("existing_library")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter34_001.json",
            {
                "id": "chapter34_001",
                "metadata": {"chapter": "chapter34", "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:34.1]]"}],
            },
        )
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "34.1",
                        "chapter": "chapter34",
                        "label": "Example 34.1",
                        "source_file": "chapter34_001.json",
                        "start_block_index": 0,
                        "end_block_index": 2,
                        "content_markdown": "Example 34.1. Complete library text with formula $$ x = y $$ and conclusion.",
                        "content_plain": "Example 34.1. Complete library text with formula and conclusion.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False, "word_count": 10},
                    }
                ],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Example 34.1. Incomplete raw text with",
                            "block_order": 1,
                            "block_bbox": [0, 100, 100, 120],
                        }
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        self.assertEqual(len(examples), 1)
        self.assertIn("Complete library text", examples[0].content_markdown)
        self.assertEqual(examples[0].start_block_index, 0)
        self.assertEqual(examples[0].end_block_index, 0)

    def test_structured_example_boundary_uses_raw_visual_stop(self):
        root = make_test_workspace("structured_visual_stop")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter35_001.json",
            {
                "id": "chapter35_001",
                "metadata": {"chapter": "chapter35", "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": (
                            "Example 35.2. The worked example starts here and includes a displayed result. "
                            "$$ y = x $$\n\n"
                            "The final sentence closes the example in the figure.\n\n"
                            "Recall that this ordinary discussion should remain outside the example. "
                            "It has enough words to make the accidental merge visible."
                        ),
                    },
                    {
                        "type": "paragraph",
                        "content": "Example 35.3. The next example starts later.",
                    },
                ],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Example 35.2. The worked example starts here and includes a displayed result.",
                            "block_order": 1,
                            "block_bbox": [322, 1200, 1030, 1230],
                        },
                        {
                            "block_label": "display_formula",
                            "block_content": "$$ y = x $$",
                            "block_order": 2,
                            "block_bbox": [400, 1240, 700, 1270],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The final sentence closes the example in the figure.",
                            "block_order": 3,
                            "block_bbox": [322, 1280, 1030, 1310],
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "Recall that this ordinary discussion should remain outside the example. "
                                "It has enough words to make the accidental merge visible."
                            ),
                            "block_order": 4,
                            "block_bbox": [132, 1370, 905, 1430],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        by_id = {item.example_id: item for item in examples}
        self.assertIn("35.2", by_id)
        self.assertIn("final sentence closes", by_id["35.2"].content_markdown)
        self.assertNotIn("ordinary discussion", by_id["35.2"].content_markdown)
        self.assertEqual(by_id["35.2"].formula_refs, [])
        self.assertTrue(by_id["35.2"].evidence["visual_stop_clipped"])

    def test_inline_example_reference_is_not_treated_as_heading(self):
        root = make_test_workspace("inline_example_reference")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter36_001.json",
            {
                "id": "chapter36_001",
                "metadata": {"chapter": "chapter36", "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": (
                            "The opening discussion mentions Example 36.1 used the same assumptions, "
                            "but this sentence is ordinary prose and should not become an example."
                        ),
                    },
                    {
                        "type": "paragraph",
                        "content": "Example 36.2. This is the actual worked example.",
                    },
                ],
            },
        )

        examples, _, _ = example_trial.extract_examples_for_structured_dir(structured_dir)

        self.assertEqual([item.example_id for item in examples], ["36.2"])
        self.assertNotIn("ordinary prose", examples[0].content_markdown)

    def test_raw_recovered_example_table_stays_inline_not_source_numbered_table(self):
        root = make_test_workspace("raw_inline_table_not_numbered")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter37_001.json",
            {
                "id": "chapter37_001",
                "metadata": {"chapter": "chapter37", "table_references": ["37.1"]},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": "Context before a missing example with enough anchor words for alignment.",
                    }
                ],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": "Example 37.2. Context before a missing example with enough anchor words",
                            "block_order": 1,
                            "block_bbox": [100, 100, 400, 140],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>Genotype</td><td>Fitness</td></tr></table>",
                            "block_order": 2,
                            "block_bbox": [140, 150, 360, 230],
                        },
                        {
                            "block_label": "text",
                            "block_content": "for alignment.",
                            "block_order": 3,
                            "block_bbox": [100, 250, 400, 280],
                        },
                    ]
                }
            }
        ]

        context = example_trial.build_structured_context(structured_dir)
        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter37",
                context=context,
                existing_ids=set(),
                target_ids={"37.2"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        self.assertIn("[[TABLE:inline_1]]", recovered[0].content_markdown)
        self.assertNotIn("[[TABLE:37.1]]", recovered[0].content_markdown)

    def test_raw_recovered_example_keeps_multiple_tables_and_stops_at_body_callback(self):
        root = make_test_workspace("raw_multi_table_example_stop")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter38_001.json",
            {
                "id": "chapter38_001",
                "metadata": {"chapter": "chapter38", "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:38.2]]"}],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Example 38.2. The example introduces the first table.",
                            "block_order": 1,
                            "block_bbox": [300, 100, 900, 150],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>A</td></tr></table>",
                            "block_order": 2,
                            "block_bbox": [320, 160, 700, 220],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The same example then introduces the second table.",
                            "block_order": 3,
                            "block_bbox": [300, 230, 900, 280],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>B</td></tr></table>",
                            "block_order": 4,
                            "block_bbox": [320, 290, 700, 350],
                        },
                        {
                            "block_label": "text",
                            "block_content": "As Example 38.2 highlights, this is ordinary prose after the example.",
                            "block_order": 5,
                            "block_bbox": [130, 430, 900, 480],
                        },
                    ]
                }
            }
        ]

        context = example_trial.build_structured_context(structured_dir)
        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter38",
                context=context,
                existing_ids=set(),
                target_ids={"38.2"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        self.assertIn("[[TABLE:inline_1]]", recovered[0].content_markdown)
        self.assertIn("[[TABLE:inline_2]]", recovered[0].content_markdown)
        self.assertNotIn("ordinary prose after the example", recovered[0].content_markdown)

    def test_report_uses_generic_example_sequence_gaps(self):
        examples = [
            example_trial.ExampleCandidate(
                example_id="41.1",
                chapter="chapter41",
                label="Example 41.1",
                title="",
                source_file="chapter41_001.json",
                start_block_index=0,
                end_block_index=0,
                block_ids=[],
                content_markdown="Example 41.1. One.",
                content_plain="Example 41.1. One.",
                formula_refs=[],
                table_refs=[],
                figure_refs=[],
                external_refs=[],
                evidence={},
                metadata={"needs_review": False},
                _order_key=(0, 41, "chapter41"),
            ),
            example_trial.ExampleCandidate(
                example_id="41.3",
                chapter="chapter41",
                label="Example 41.3",
                title="",
                source_file="chapter41_002.json",
                start_block_index=0,
                end_block_index=0,
                block_ids=[],
                content_markdown="Example 41.3. Three.",
                content_plain="Example 41.3. Three.",
                formula_refs=[],
                table_refs=[],
                figure_refs=[],
                external_refs=[],
                evidence={},
                metadata={"needs_review": False},
                _order_key=(0, 41, "chapter41"),
            ),
        ]

        report = example_trial_report.build_report(
            output_candidate=Path("trial"),
            baseline_candidate=Path("baseline"),
            examples=examples,
            summary={"chapter_counts": [("chapter41", 2)]},
            baseline_audit={"severity_counts": {}, "quality_metrics": {}, "issue_type_counts": {}},
            trial_audit={"severity_counts": {}, "quality_metrics": {}, "issue_type_counts": {}},
            file_comparison={"added": [], "modified": [], "removed": [], "unchanged": []},
            command_log=[],
        )

        self.assertIn("## Example Sequence Gaps", report)
        self.assertIn("41.2", report)
        self.assertNotIn("Target Examples", report)
        self.assertNotIn("Example 25", report)


if __name__ == "__main__":
    unittest.main()
