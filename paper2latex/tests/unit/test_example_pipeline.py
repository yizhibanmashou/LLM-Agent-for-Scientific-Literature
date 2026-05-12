import json
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from knowledge_engineering.pipeline.example_pipeline import apply_example_pipeline
from knowledge_engineering.processors import example_extraction as example_trial


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_RUNTIME_ROOT = PROJECT_ROOT / "tmp" / "test_runtime" / "example_pipeline"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ExamplePipelineTests(unittest.TestCase):
    def test_apply_example_pipeline_writes_library_and_preserves_reference_libraries(self):
        root = make_test_workspace("formal_pipeline")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter1_001.json",
            {
                "id": "chapter1_001",
                "metadata": {"chapter": "chapter1", "formula_references": ["1.1"], "table_references": ["1.1"]},
                "blocks": [
                    {"type": "paragraph", "content": "Introductory paragraph."},
                    {
                        "type": "paragraph",
                        "content": "Example 1.1. A compact worked example uses [[SEE_FORMULA:1.1]] and [[TABLE:1.1]].",
                    },
                ],
            },
        )
        formula_library = {
            "formulas": [
                {"id": "formula_1.1", "latex": "x=y", "chapter": "chapter1", "kind": "block"},
            ],
        }
        table_library = {
            "tables": [
                {"id": "1.1", "chapter": "chapter1", "caption": "Small table", "rows": [["a", "b"]]},
            ],
        }
        write_json(structured_dir / "formula_library.json", formula_library)
        write_json(structured_dir / "table_library.json", table_library)

        summary = apply_example_pipeline(
            structured_dir,
            project_root=root,
            artifacts_dir=artifacts_dir,
        )

        self.assertEqual(summary["total_examples"], 1)
        self.assertEqual(summary["replaced_examples"], 1)
        self.assertEqual(summary["blocks_removed_by_example_fold"], 0)
        self.assertFalse(summary["formula_library_changed"])
        self.assertFalse(summary["table_library_changed"])

        unit = read_json(structured_dir / "chapter1_001.json")
        self.assertEqual(unit["blocks"][1], {"type": "example", "content": "[[SEE_EXAMPLE:1.1]]"})
        self.assertEqual(read_json(structured_dir / "formula_library.json"), formula_library)
        self.assertEqual(read_json(structured_dir / "table_library.json"), table_library)

        library = read_json(structured_dir / "example_library.json")
        self.assertEqual(library["schema"], "example_library.v1")
        self.assertEqual(library["example_count"], 1)
        self.assertEqual(library["examples"][0]["example_ref"], "1.1")
        self.assertEqual(library["examples"][0]["replacement"]["status"], "replaced")
        self.assertTrue((artifacts_dir / "example_pipeline_summary.json").exists())

    def test_existing_library_refresh_clips_direct_example_callback_tail(self):
        root = make_test_workspace("existing_library_callback_tail")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter17_001.json",
            {
                "id": "chapter17_001",
                "metadata": {"chapter": "chapter17", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:17.4]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "17.4",
                        "example_ref": "17.4",
                        "chapter": "chapter17",
                        "label": "Example 17.4",
                        "title": "Consider a trait.",
                        "source_file": "chapter17_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": (
                            "Example 17.4. Consider a trait. The calculation ends here. "
                            "Example 17.4 illustrates the fact that this is ordinary prose after the example."
                        ),
                        "content_plain": (
                            "Example 17.4. Consider a trait. The calculation ends here. "
                            "Example 17.4 illustrates the fact that this is ordinary prose after the example."
                        ),
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
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
                            "block_content": "Example 17.4. Consider a trait. The calculation ends here.",
                            "block_order": 1,
                            "block_bbox": [300, 100, 900, 150],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Example 17.4 illustrates the fact that this is ordinary prose after the example.",
                            "block_order": 2,
                            "block_bbox": [130, 220, 900, 270],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(
                structured_dir,
                project_root=root,
                artifacts_dir=artifacts_dir,
            )

        library = read_json(structured_dir / "example_library.json")
        content = library["examples"][0]["content_markdown"]
        self.assertTrue(summary["existing_library_repair_stats"]["changed"])
        self.assertEqual(
            summary["existing_library_repair_stats"]["raw_layout_refresh"]["replacement_reason_counts"].get(
                "raw_layout_boundary_clipped"
            ),
            1,
        )
        self.assertIn("The calculation ends here.", content)
        self.assertNotIn("ordinary prose after the example", content)

    def test_existing_library_refresh_stops_before_new_body_paragraph_after_example(self):
        root = make_test_workspace("existing_library_body_stop")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter9_010.json",
            {
                "id": "chapter9_010",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.2]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "9.2",
                        "example_ref": "9.2",
                        "chapter": "chapter9",
                        "label": "Example 9.2",
                        "title": "We now revisit Fisher and Ford",
                        "source_file": "chapter9_010.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": (
                            "Example 9.2. We now revisit Fisher and Ford (Example 9.1), and consider a test. "
                            "A number of generalizations, as well as increasingly sophisticated tests, have been proposed."
                        ),
                        "content_plain": (
                            "Example 9.2. We now revisit Fisher and Ford (Example 9.1), and consider a test. "
                            "A number of generalizations, as well as increasingly sophisticated tests, have been proposed."
                        ),
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.2",
                        "placeholder": "[[SEE_EXAMPLE:9.2]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
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
                            "block_content": "Example 9.2. We now revisit Fisher and Ford (Example 9.1), and consider a test.",
                            "block_bbox": [286, 700, 1060, 840],
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "A number of generalizations, as well as increasingly sophisticated tests "
                                "have been proposed, including extending this methodology."
                            ),
                            "block_bbox": [287, 853, 1060, 1059],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            context = example_trial.build_structured_context(structured_dir)
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter9",
                context=context,
                existing_ids=set(),
                target_ids={"9.2"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        content = recovered[0].content_markdown
        self.assertIn("We now revisit Fisher and Ford", content)
        self.assertNotIn("A number of generalizations", content)

    def test_reference_example_library_seeds_verified_missing_examples(self):
        root = make_test_workspace("reference_seed")
        structured_dir = root / "structured"
        reference_dir = root / "reference"
        write_json(
            structured_dir / "chapter2_001.json",
            {
                "id": "chapter2_001",
                "metadata": {"chapter": "chapter2", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": "Example 2.5. An automatically detected example starts the local sequence.",
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter2_002.json",
            {
                "id": "chapter2_002",
                "metadata": {"chapter": "chapter2", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": (
                            "A verified worked example begins here with enough unique words "
                            "for the reference anchor to locate the block safely."
                        ),
                    }
                ],
            },
        )
        write_json(
            structured_dir / "chapter2_003.json",
            {
                "id": "chapter2_003",
                "metadata": {"chapter": "chapter2", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": "Example 2.8. Another automatically detected example closes the local sequence.",
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            reference_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "2.7",
                        "example_ref": "2.7",
                        "chapter": "chapter2",
                        "label": "Example 2.7",
                        "title": "A verified worked example",
                        "source_file": "chapter2_099.json",
                        "start_block_index": 4,
                        "end_block_index": 5,
                        "content_markdown": (
                            "A verified worked example begins here with enough unique words "
                            "for the reference anchor to locate the block safely."
                        ),
                        "content_plain": (
                            "A verified worked example begins here with enough unique words "
                            "for the reference anchor to locate the block safely."
                        ),
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                    }
                ],
            },
        )

        summary = apply_example_pipeline(
            structured_dir,
            project_root=root,
            reference_structured_dir=reference_dir,
        )

        self.assertEqual(summary["total_examples"], 3)
        self.assertEqual(summary["reference_seed_stats"]["seeded"], 1)
        unit = read_json(structured_dir / "chapter2_002.json")
        self.assertEqual(unit["blocks"][0], {"type": "example", "content": "[[SEE_EXAMPLE:2.7]]"})
        library = read_json(structured_dir / "example_library.json")
        seeded = [row for row in library["examples"] if row["example_ref"] == "2.7"][0]
        self.assertEqual(seeded["source_file"], "chapter2_002.json")
        self.assertTrue(seeded["metadata"]["reference_seed"])

    def test_sequence_gap_raw_recovery_folds_inline_tail_without_losing_prefix(self):
        root = make_test_workspace("sequence_gap")
        structured_dir = root / "structured"
        reference_dir = root / "reference"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter5_001.json",
            {
                "id": "chapter5_001",
                "metadata": {"chapter": "chapter5", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": (
                            "Context before the missing example stays visible. "
                            "the recovered body continues with enough distinctive words "
                            "to align the missing example safely."
                        ),
                    },
                    {
                        "type": "paragraph",
                        "content": "Example 5.2. A normal detected example starts the sequence.",
                    },
                    {
                        "type": "paragraph",
                        "content": "Example 5.4. Another normal detected example closes the sequence.",
                    },
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            reference_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "5.3",
                        "example_ref": "5.3",
                        "chapter": "chapter5",
                        "label": "Example 5.3",
                        "source_file": "chapter5_001.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "content_markdown": (
                            "Example 5.3. The recovered body continues with enough distinctive words "
                            "to align the missing example safely."
                        ),
                        "content_plain": (
                            "Example 5.3. The recovered body continues with enough distinctive words "
                            "to align the missing example safely."
                        ),
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
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
                            "block_content": (
                                "Example 5.3. The recovered body continues with enough distinctive words"
                            ),
                            "block_bbox": [0, 100, 100, 120],
                        },
                        {
                            "block_label": "text",
                            "block_content": "to align the missing example safely.",
                            "block_order": 1,
                            "block_bbox": [0, 150, 100, 170],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Example 5.4. Another normal detected example closes the sequence.",
                            "block_order": 2,
                            "block_bbox": [0, 220, 100, 240],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(
                structured_dir,
                project_root=root,
                reference_structured_dir=reference_dir,
                artifacts_dir=artifacts_dir,
            )

        self.assertEqual(summary["total_examples"], 3)
        self.assertEqual(summary["sequence_gap_recovery_stats"]["aligned"], 1)
        unit = read_json(structured_dir / "chapter5_001.json")
        self.assertEqual(unit["blocks"][0]["type"], "paragraph")
        self.assertEqual(unit["blocks"][0]["content"], "Context before the missing example stays visible.")
        self.assertEqual(unit["blocks"][1], {"type": "example", "content": "[[SEE_EXAMPLE:5.3]]"})
        library = read_json(structured_dir / "example_library.json")
        recovered = [row for row in library["examples"] if row["example_id"] == "5.3"][0]
        self.assertEqual(recovered["replacement"]["status"], "replaced")
        self.assertIn("Example 5.3.", recovered["content_markdown"])

    def test_sequence_gap_raw_recovery_inserts_before_next_example_when_anchor_is_only_cross_reference(self):
        root = make_test_workspace("sequence_gap_cross_reference")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter24_013.json",
            {
                "id": "chapter24_013",
                "metadata": {"chapter": "chapter24", "formula_references": [], "table_references": []},
                "blocks": [{"type": "discussion", "content": "Example 24.2. A previous example starts the sequence."}],
            },
        )
        write_json(
            structured_dir / "chapter24_014.json",
            {
                "id": "chapter24_014",
                "metadata": {"chapter": "chapter24", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "Example 24.4. As an illustration of how the effective number of loci can change, "
                            "consider a later model with major and minor loci."
                        ),
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": (
                                "Example 24.3. Suppose the number of loci underlying a trait is finite. "
                                "The selection response decreases over time with a finite number of loci."
                            ),
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Figure 24.2 The impact of a finite number of loci on heritability and selection response.",
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "Example 24.4. As an illustration of how the effective number of loci can change, "
                                "consider a later model with major and minor loci."
                            ),
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["sequence_gap_recovery_stats"]["aligned"], 1)
        unit = read_json(structured_dir / "chapter24_014.json")
        self.assertEqual(unit["blocks"][0], {"type": "example", "content": "[[SEE_EXAMPLE:24.3]]"})
        self.assertEqual(unit["blocks"][1], {"type": "example", "content": "[[SEE_EXAMPLE:24.4]]"})
        library = read_json(structured_dir / "example_library.json")
        rows = {row["example_ref"]: row for row in library["examples"]}
        self.assertEqual(rows["24.3"]["replacement"]["status"], "replaced")
        self.assertNotIn("Figure 24.2", rows["24.3"]["content_markdown"])

    def test_existing_library_sequence_gap_recovers_plain_text_example_tail(self):
        root = make_test_workspace("existing_sequence_gap_plain_text")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter21_035.json",
            {
                "id": "chapter21_035",
                "metadata": {"chapter": "chapter21", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "The design can reduce environmental variance. "
                            "using single rows grown in three different locations. Based on these yield trials, "
                            "the best 44 of roughly 220 families were identified."
                        ),
                    }
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 2,
                "examples": [
                    {
                        "example_id": "21.9",
                        "example_ref": "21.9",
                        "chapter": "chapter21",
                        "label": "Example 21.9",
                        "source_file": "chapter21_034.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "content_markdown": "Example 21.9. Previous example.",
                        "content_plain": "Example 21.9. Previous example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                        "replacement": {"status": "replaced"},
                    },
                    {
                        "example_id": "21.11",
                        "example_ref": "21.11",
                        "chapter": "chapter21",
                        "label": "Example 21.11",
                        "source_file": "chapter21_037.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "content_markdown": "Example 21.11. Next example.",
                        "content_plain": "Example 21.11. Next example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                        "replacement": {"status": "replaced"},
                    },
                ],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": (
                                "Example 21.10. Webel and Lonnquist (1967) used modified ear-to-row "
                                "selection for yield in maize. Performance of each family was evaluated"
                            ),
                            "block_bbox": [0, 100, 100, 120],
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "using single rows grown in three different locations. Based on these yield trials, "
                                "the best 44 of roughly 220 families were identified."
                            ),
                            "block_order": 1,
                            "block_bbox": [0, 150, 100, 170],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The following discussion starts after the example.",
                            "block_order": 2,
                            "block_bbox": [0, 230, 100, 250],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(
                structured_dir,
                project_root=root,
                artifacts_dir=artifacts_dir,
            )

        self.assertEqual(summary["existing_library_repair_stats"]["sequence_gap_split"]["raw_recovered"], 1)
        self.assertEqual(summary["existing_library_repair_stats"]["sequence_gap_split"]["split_from_existing_rows"], 1)
        unit = read_json(structured_dir / "chapter21_035.json")
        self.assertEqual(unit["blocks"][0]["content"], "The design can reduce environmental variance.")
        self.assertEqual(unit["blocks"][1], {"type": "example", "content": "[[SEE_EXAMPLE:21.10]]"})
        self.assertNotIn("using single rows", unit["blocks"][0]["content"])
        library = read_json(structured_dir / "example_library.json")
        recovered = [row for row in library["examples"] if row["example_id"] == "21.10"][0]
        self.assertIn("Example 21.10.", recovered["content_markdown"])
        self.assertEqual(recovered["start_block_index"], 1)
        self.assertFalse(recovered["table_refs"])

    def test_example_owned_inline_table_rebinds_source_unit_and_metadata(self):
        root = make_test_workspace("inline_table_rebind")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter42_001.json",
            {
                "id": "chapter42_001",
                "metadata": {
                    "chapter": "chapter42",
                    "formula_references": [],
                    "table_references": ["inline_2"],
                    "table_reference_keys": ["chapter42:inline_2"],
                },
                "blocks": [{"type": "discussion", "content": "Unrelated discussion before the example."}],
            },
        )
        write_json(
            structured_dir / "chapter42_002.json",
            {
                "id": "chapter42_002",
                "metadata": {
                    "chapter": "chapter42",
                    "formula_references": [],
                    "table_references": [],
                    "display_heading": "Accumulation of Lethals in Selected Lines",
                },
                "blocks": [
                    {
                        "type": "paragraph",
                        "content": (
                            "Example 42.1. Consider the following estimated variance components: "
                            "[[TABLE:inline_2]] The selected line shows the expected pattern."
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
                        "id": "inline_2",
                        "label_format": "Inline Table 2",
                        "title": "Wrong chapter table",
                        "table_type": "inline",
                        "rows": [["Wrong"], ["chapter41"]],
                        "html": "",
                        "source": {"chapter": "chapter41", "unit_id": "chapter41_001"},
                    },
                    {
                        "id": "inline_2",
                        "label_format": "Inline Table 2",
                        "title": "Inline Table 2",
                        "table_type": "inline",
                        "rows": [["Population", "Value"], ["Selected", "4.65"]],
                        "html": "",
                        "source": {"chapter": "chapter42", "unit_id": "chapter42_001"},
                    },
                ],
            },
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertTrue(summary["table_library_changed"])
        self.assertEqual(summary["table_source_rebind_stats"]["table_sources_rebound"], 1)
        table_library = read_json(structured_dir / "table_library.json")
        chapter42_table = [
            table
            for table in table_library["tables"]
            if table["id"] == "inline_2" and table["source"].get("chapter") == "chapter42"
        ][0]
        self.assertEqual(chapter42_table["source"]["unit_id"], "chapter42_002")
        self.assertEqual(chapter42_table["source"]["subsection"], "Accumulation of Lethals in Selected Lines")
        self.assertEqual(
            chapter42_table["source"]["source_rebound_by"],
            "example_pipeline_inline_table_source",
        )

        old_unit_metadata = read_json(structured_dir / "chapter42_001.json")["metadata"]
        new_unit_metadata = read_json(structured_dir / "chapter42_002.json")["metadata"]
        self.assertNotIn("inline_2", old_unit_metadata["table_references"])
        self.assertIn("inline_2", new_unit_metadata["table_references"])
        self.assertIn("chapter42:inline_2", new_unit_metadata["table_reference_keys"])

    def test_existing_library_repair_restores_false_reference_and_splits_sequence_gap(self):
        root = make_test_workspace("existing_library_repair")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter9_full" / "intermediate"
        write_json(
            structured_dir / "chapter9_001.json",
            {
                "id": "chapter9_001",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.1]]"}],
            },
        )
        write_json(
            structured_dir / "chapter9_002.json",
            {
                "id": "chapter9_002",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.1@chapter9_002_0]]"}],
            },
        )
        write_json(
            structured_dir / "chapter9_003.json",
            {
                "id": "chapter9_003",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.3]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "inline_1",
                        "label_format": "Inline Table 1",
                        "title": "Inline Table 1",
                        "table_type": "inline",
                        "html": "",
                        "rows": [["Genotype", "Fitness"], ["AA", "1.0"]],
                        "source": {"chapter": "chapter9", "unit_id": "chapter9_001"},
                    }
                ]
            },
        )
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 3,
                "examples": [
                    {
                        "example_id": "9.1",
                        "chapter": "chapter9",
                        "label": "Example 9.1",
                        "title": "First example",
                        "source_file": "chapter9_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": (
                            "Example 9.1. First example text closes cleanly. "
                            "[[TABLE:9.1]] Second example body begins here with enough unique anchor words to split."
                        ),
                        "content_plain": "",
                        "formula_refs": [],
                        "table_refs": ["9.1"],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.1",
                        "placeholder": "[[SEE_EXAMPLE:9.1]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                    {
                        "example_id": "9.1",
                        "chapter": "chapter9",
                        "label": "Example 9.1",
                        "title": "Inline reference",
                        "source_file": "chapter9_002.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 9.1 used an earlier result as a sentence, not a heading.",
                        "content_plain": "",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.1@chapter9_002_0",
                        "placeholder": "[[SEE_EXAMPLE:9.1@chapter9_002_0]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                    {
                        "example_id": "9.3",
                        "chapter": "chapter9",
                        "label": "Example 9.3",
                        "title": "Third example",
                        "source_file": "chapter9_003.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 9.3. Third example.",
                        "content_plain": "",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.3",
                        "placeholder": "[[SEE_EXAMPLE:9.3]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                ],
            },
        )
        write_json(
            raw_dir / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "text",
                                "block_content": "Example 9.2. Second example title introduces a raw inline table and",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "table",
                                "block_content": "<table><tr><td>Genotype</td><td>Fitness</td></tr><tr><td>AA</td><td>1.0</td></tr></table>",
                                "block_bbox": [100, 140, 500, 180],
                            },
                            {
                                "block_label": "text",
                                "block_content": "Second example body begins here with enough unique anchor words to split.",
                                "block_bbox": [100, 190, 500, 230],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]
        self.assertEqual(repair["false_heading"]["source_blocks_restored"], 1)
        self.assertEqual(repair["sequence_gap_split"]["split_from_existing_rows"], 1)
        self.assertEqual(read_json(structured_dir / "chapter9_002.json")["blocks"][0]["type"], "discussion")
        unit = read_json(structured_dir / "chapter9_001.json")
        self.assertEqual(unit["blocks"][0]["content"], "[[SEE_EXAMPLE:9.1]] [[SEE_EXAMPLE:9.2]]")
        library = read_json(structured_dir / "example_library.json")
        rows_by_ref = {row["example_ref"]: row for row in library["examples"]}
        self.assertNotIn("[[TABLE:9.1]]", rows_by_ref["9.1"]["content_markdown"])
        self.assertIn("[[TABLE:inline_1]]", rows_by_ref["9.2"]["content_markdown"])
        self.assertTrue(rows_by_ref["9.2"]["content_markdown"].startswith("Example 9.2."))

    def test_shorter_raw_refresh_without_boundary_evidence_goes_to_review_queue(self):
        root = make_test_workspace("weak_shorter_raw_refresh")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter42_full" / "intermediate"
        write_json(
            structured_dir / "chapter42_001.json",
            {
                "id": "chapter42_001",
                "metadata": {"chapter": "chapter42", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:42.1]]"}],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        long_tail = " ".join(f"tail{i}" for i in range(90))
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "42.1",
                        "chapter": "chapter42",
                        "label": "Example 42.1",
                        "title": "Weak raw",
                        "source_file": "chapter42_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": f"Example 42.1. Raw body begins with shared words and closes cleanly. {long_tail}",
                        "content_plain": "",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "42.1",
                        "placeholder": "[[SEE_EXAMPLE:42.1]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    }
                ],
            },
        )
        write_json(
            raw_dir / "paddle_raw_response.json",
            [
                {
                    "prunedResult": {
                        "parsing_res_list": [
                            {
                                "block_label": "text",
                                "block_content": "Example 42.1. Raw body begins with shared words and closes cleanly.",
                                "block_bbox": [100, 100, 500, 130],
                            }
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        refresh = summary["existing_library_repair_stats"]["raw_layout_refresh"]
        self.assertEqual(refresh["rows_replaced"], 0)
        self.assertEqual(refresh["review_queue_count"], 1)
        library = read_json(structured_dir / "example_library.json")
        self.assertIn("tail89", library["examples"][0]["content_markdown"])


if __name__ == "__main__":
    unittest.main()
