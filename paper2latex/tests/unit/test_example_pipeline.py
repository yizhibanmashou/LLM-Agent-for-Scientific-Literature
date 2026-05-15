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

    def test_numbered_table_expansion_after_example_is_not_folded_into_example(self):
        root = make_test_workspace("numbered_table_after_example")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter27_001.json",
            {
                "id": "chapter27_001",
                "metadata": {"chapter": "chapter27", "formula_references": [], "table_references": ["27.1"]},
                "blocks": [
                    {"type": "discussion", "content": "Before the worked example."},
                    {
                        "type": "discussion",
                        "content": (
                            "Example 27.4. The examination of adaptive walks starts here. "
                            "The expected successful trajectories are not equally likely."
                        ),
                    },
                    {"type": "table", "content": "[[TABLE:27.1]]"},
                    {"type": "discussion", "content": "The Fitness Distribution of Beneficial Alleles"},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(
            structured_dir / "table_library.json",
            {
                "tables": [
                    {
                        "id": "27.1",
                        "table_type": "numbered",
                        "title": "Table 27.1 Summary of experiments.",
                        "rows": [["Species", "Fixed?"], ["E. coli", "Yes"]],
                        "source": {"chapter": "chapter27", "unit_id": "chapter27_001"},
                    }
                ]
            },
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["total_examples"], 1)
        unit = read_json(structured_dir / "chapter27_001.json")
        self.assertEqual(
            [block["content"] for block in unit["blocks"]],
            [
                "Before the worked example.",
                "[[SEE_EXAMPLE:27.4]]",
                "[[TABLE:27.1]]",
                "The Fitness Distribution of Beneficial Alleles",
            ],
        )
        library = read_json(structured_dir / "example_library.json")
        example = library["examples"][0]
        self.assertNotIn("[[TABLE:27.1]]", example["content_markdown"])
        self.assertEqual(example["table_refs"], [])

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

    def test_existing_library_uses_placeholder_index_not_source_span_for_validation(self):
        root = make_test_workspace("existing_library_placeholder_index")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Original source residue that is no longer the placeholder."},
                    {"type": "discussion", "content": "Continuation covered by the original source span."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:25.1]]"},
                ],
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
                        "example_id": "25.1",
                        "example_ref": "25.1",
                        "placeholder": "[[SEE_EXAMPLE:25.1]]",
                        "chapter": "chapter25",
                        "label": "Example 25.1",
                        "source_file": "chapter25_001.json",
                        "start_block_index": 0,
                        "end_block_index": 1,
                        "content_markdown": "Example 25.1. A valid visual example.",
                        "content_plain": "Example 25.1. A valid visual example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [0, 1],
                            "placeholder_block_index": 2,
                            "placeholder_source_file": "chapter25_001.json",
                        },
                    }
                ],
            },
        )

        summary = apply_example_pipeline(
            structured_dir,
            project_root=root,
            artifacts_dir=artifacts_dir,
        )

        self.assertTrue(summary["existing_example_library_used"])
        self.assertEqual(summary["total_examples"], 1)
        self.assertEqual(summary["existing_placeholder_stats"]["placeholder_blocks_missing"], 0)
        self.assertEqual(
            summary["existing_library_repair_stats"]["index_validation"]["stale"],
            0,
        )

    def test_existing_library_is_preserved_when_some_placeholders_need_audit(self):
        root = make_test_workspace("existing_library_audit_warning")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter25_001.json",
            {
                "id": "chapter25_001",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [{"type": "discussion", "content": "The stale row placeholder is absent here."}],
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
                        "example_id": "25.1",
                        "example_ref": "25.1",
                        "placeholder": "[[SEE_EXAMPLE:25.1]]",
                        "chapter": "chapter25",
                        "label": "Example 25.1",
                        "source_file": "chapter25_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "content_markdown": "Example 25.1. Existing verified content.",
                        "content_plain": "Example 25.1. Existing verified content.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [0, 0],
                            "placeholder_block_index": 0,
                            "placeholder_source_file": "chapter25_001.json",
                        },
                    }
                ],
            },
        )

        summary = apply_example_pipeline(
            structured_dir,
            project_root=root,
            artifacts_dir=artifacts_dir,
        )

        self.assertTrue(summary["existing_example_library_used"])
        self.assertEqual(summary["total_examples"], 1)
        self.assertFalse(summary["example_library_preserved"] is False)
        self.assertEqual(read_json(structured_dir / "example_library.json")["example_count"], 1)

    def test_existing_library_restores_missing_placeholder_from_raw_neighbor_anchor(self):
        root = make_test_workspace("existing_library_restore_missing_placeholder")
        structured_dir = root / "structured"
        artifacts_dir = root / "artifacts"
        write_json(
            structured_dir / "chapter24_003.json",
            {
                "id": "chapter24_003",
                "metadata": {"chapter": "chapter24", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "By using mixed-model approaches that allow all SNPs to be incorporated, "
                            "Yang et al. could account for additive variance."
                        ),
                    },
                    {"type": "discussion", "content": "The next section starts after the example."},
                ],
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
                        "example_id": "24.1",
                        "example_ref": "24.1",
                        "placeholder": "[[SEE_EXAMPLE:24.1]]",
                        "chapter": "chapter24",
                        "label": "Example 24.1",
                        "source_file": "chapter24_003.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "content_markdown": "Example 24.1. Verified raw-layout example content.",
                        "content_plain": "Example 24.1. Verified raw-layout example content.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "metadata": {"needs_review": False},
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [1, 1],
                            "placeholder_block_index": 1,
                            "placeholder_source_file": "chapter24_003.json",
                        },
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
                            "block_content": (
                                "By using mixed-model approaches that allow all SNPs to be incorporated, "
                                "Yang et al. could account for additive variance."
                            ),
                            "block_bbox": [0, 100, 100, 120],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Example 24.1. Verified raw-layout example content.",
                            "block_bbox": [0, 140, 100, 160],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The next section starts after the example.",
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
                artifacts_dir=artifacts_dir,
            )

        self.assertEqual(
            summary["existing_library_repair_stats"]["missing_placeholder_restore"]["placeholders_inserted"],
            1,
        )
        unit = read_json(structured_dir / "chapter24_003.json")
        self.assertEqual(unit["blocks"][1], {"type": "example", "content": "[[SEE_EXAMPLE:24.1]]"})
        library = read_json(structured_dir / "example_library.json")
        row = library["examples"][0]
        self.assertEqual(row["replacement"]["placeholder_block_index"], 1)
        self.assertEqual(summary["existing_placeholder_stats"]["placeholder_blocks_missing"], 0)

    def test_existing_library_relocates_sequence_gap_placeholder_to_visual_stop_neighbor(self):
        root = make_test_workspace("existing_library_sequence_gap_neighbor")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter26_007.json",
            {
                "id": "chapter26_007",
                "metadata": {"chapter": "chapter26", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Discussion before the examples."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:26.2]]"},
                ],
            },
        )
        write_json(
            structured_dir / "chapter26_014.json",
            {
                "id": "chapter26_014",
                "metadata": {"chapter": "chapter26", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Later discussion."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:26.3]]"},
                    {"type": "example", "content": "[[SEE_EXAMPLE:26.4]]"},
                ],
            },
        )
        write_json(structured_dir / "formula_library.json", {"formulas": []})
        write_json(structured_dir / "table_library.json", {"tables": []})
        write_json(
            structured_dir / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 3,
                "examples": [
                    {
                        "example_id": "26.2",
                        "chapter": "chapter26",
                        "label": "Example 26.2",
                        "title": "Previous",
                        "source_file": "chapter26_007.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "block_ids": [],
                        "content_markdown": "Example 26.2. Previous example.",
                        "content_plain": "Example 26.2. Previous example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {"source_page": 8},
                        "metadata": {
                            "needs_review": False,
                            "visual_stop": {
                                "stop_text": "Example 26.3. Cohan and Hoffmann examined divergence."
                            },
                        },
                        "example_ref": "26.2",
                        "placeholder": "[[SEE_EXAMPLE:26.2]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [1, 1],
                            "placeholder_block_index": 1,
                            "placeholder_source_file": "chapter26_007.json",
                        },
                    },
                    {
                        "example_id": "26.3",
                        "chapter": "chapter26",
                        "label": "Example 26.3",
                        "title": "Cohan and Hoffmann examined divergence.",
                        "source_file": "chapter26_014.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "block_ids": [],
                        "content_markdown": "Example 26.3. Cohan and Hoffmann examined divergence.",
                        "content_plain": "Example 26.3. Cohan and Hoffmann examined divergence.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {
                            "source_page": 8,
                            "detection_method": "sequence_gap_raw_layout_neighbor_insert_placeholder",
                        },
                        "metadata": {
                            "needs_review": False,
                            "insert_placeholder_only": True,
                            "sequence_gap_neighbor_insert": True,
                        },
                        "example_ref": "26.3",
                        "placeholder": "[[SEE_EXAMPLE:26.3]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [1, 1],
                            "placeholder_block_index": 1,
                            "placeholder_source_file": "chapter26_014.json",
                        },
                    },
                    {
                        "example_id": "26.4",
                        "chapter": "chapter26",
                        "label": "Example 26.4",
                        "title": "Next",
                        "source_file": "chapter26_014.json",
                        "start_block_index": 2,
                        "end_block_index": 2,
                        "block_ids": [],
                        "content_markdown": "Example 26.4. Next example.",
                        "content_plain": "Example 26.4. Next example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "26.4",
                        "placeholder": "[[SEE_EXAMPLE:26.4]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [2, 2],
                            "placeholder_block_index": 2,
                            "placeholder_source_file": "chapter26_014.json",
                        },
                    },
                ],
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {"block_label": "text", "block_content": "Example 26.2. Previous example."},
                        {
                            "block_label": "figure_title",
                            "block_content": "Example 26.3. Cohan and Hoffmann examined divergence.",
                        },
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {"block_label": "text", "block_content": "Example 26.4. Next example."},
                    ]
                }
            },
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]["sequence_gap_neighbor_relocation"]
        self.assertEqual(repair["rows_relocated"], 1)
        self.assertEqual(repair["visual_stop_matches"], 1)
        self.assertEqual(
            read_json(structured_dir / "chapter26_007.json")["blocks"][2],
            {"type": "example", "content": "[[SEE_EXAMPLE:26.3]]"},
        )
        self.assertEqual(
            read_json(structured_dir / "chapter26_014.json")["blocks"],
            [
                {"type": "discussion", "content": "Later discussion."},
                {"type": "example", "content": "[[SEE_EXAMPLE:26.4]]"},
            ],
        )
        rows_by_ref = {
            row["example_ref"]: row
            for row in read_json(structured_dir / "example_library.json")["examples"]
        }
        self.assertEqual(rows_by_ref["26.3"]["source_file"], "chapter26_007.json")
        self.assertEqual(rows_by_ref["26.3"]["replacement"]["placeholder_source_file"], "chapter26_007.json")
        self.assertEqual(rows_by_ref["26.3"]["replacement"]["placeholder_block_index"], 2)

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

    def test_sequence_gap_source_spans_overlap_when_structured_blocks_merge_neighbors(self):
        root = make_test_workspace("sequence_gap_overlap_source_span")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_024.json",
            {
                "id": "chapter25_024",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Context before examples."},
                    {"type": "discussion", "content": "Example 25.6. First example body."},
                    {"type": "discussion", "content": "Continuation for first example."},
                    {
                        "type": "discussion",
                        "content": (
                            "Tail for first example. At least some of the alleles for increased pupal weight "
                            "thus appear to be associated with reduced fitness."
                        ),
                    },
                    {"type": "discussion", "content": "Example 25.8. Third example body."},
                    {"type": "discussion", "content": "Third example continuation."},
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
                            "block_label": "text",
                            "block_content": "Example 25.7. Enfield selected beetles for increased pupal weight.",
                            "block_bbox": [0, 100, 100, 120],
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "At least some of the alleles for increased pupal weight "
                                "thus appear to be associated with reduced fitness."
                            ),
                            "block_bbox": [0, 150, 100, 170],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["sequence_gap_recovery_stats"]["aligned"], 1)
        library = read_json(structured_dir / "example_library.json")
        rows = {row["example_id"]: row for row in library["examples"]}
        self.assertEqual(rows["25.6"]["replacement"]["source_block_span"], [1, 2])
        self.assertEqual(rows["25.7"]["replacement"]["source_block_span"], [2, 3])
        self.assertEqual(rows["25.8"]["replacement"]["source_block_span"], [3, 4])

    def test_raw_visual_stop_source_span_uses_stop_block_not_next_example(self):
        root = make_test_workspace("visual_stop_source_span")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_025.json",
            {
                "id": "chapter25_025",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Intro."},
                    {"type": "discussion", "content": "Example 25.8. Previous example."},
                    {
                        "type": "discussion",
                        "content": "The selected line shows large increases in additive variance.",
                    },
                    {
                        "type": "derivation",
                        "content": (
                            "Why do lethal alleles persist in some selected populations? "
                            "This derivation starts after the visual rule."
                        ),
                    },
                    {"type": "discussion", "content": "Later derivation continuation."},
                    {"type": "discussion", "content": "Example 25.10. Next example."},
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
                            "block_label": "text",
                            "block_content": (
                                "Example 25.9. Consider variance components from a selection experiment. "
                                "The selected line shows large increases in additive variance."
                            ),
                            "block_bbox": [300, 100, 900, 150],
                        },
                        {
                            "block_label": "text",
                            "block_content": (
                                "Why do lethal alleles persist in some selected populations? "
                                "This derivation starts after the visual rule."
                            ),
                            "block_bbox": [100, 260, 900, 300],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Later derivation continuation.",
                            "block_bbox": [100, 320, 900, 360],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Example 25.10. Next example.",
                            "block_bbox": [100, 400, 900, 440],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["sequence_gap_recovery_stats"]["aligned"], 1)
        library = read_json(structured_dir / "example_library.json")
        row = [item for item in library["examples"] if item["example_id"] == "25.9"][0]
        self.assertEqual(row["replacement"]["source_block_span"], [2, 3])

    def test_raw_layout_example_continues_inside_pdf_box_across_figure_and_formula(self):
        root = make_test_workspace("raw_box_continuation")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter27_011.json",
            {
                "id": "chapter27_011",
                "metadata": {"chapter": "chapter27", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:27.2]]"},
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
                                "Example 27.2. The body of extreme-value theory begins here. "
                                "There is another Fisherian irony here in that the field of EVT, which"
                            ),
                            "block_bbox": [166, 1271, 881, 1443],
                        },
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": (
                                "Figure 27.4 Top: Extreme-value theory applied to beneficial alleles. "
                                "The trinity theorem (Example 27.2) states that the limiting distribution has three domains."
                            ),
                            "block_bbox": [322, 621, 1036, 940],
                        },
                        {
                            "block_label": "text",
                            "block_content": "provides the basis of an alternative model to Fisher's geometric model.",
                            "block_bbox": [322, 973, 1035, 1058],
                        },
                        {
                            "block_label": "display_formula",
                            "block_content": "$$ F(x)=1-exp(-x/tau) $$",
                            "block_bbox": [354, 1282, 995, 1365],
                        },
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "The following ordinary discussion starts after the example box.",
                            "block_bbox": [167, 850, 881, 960],
                        },
                    ]
                }
            },
        ]
        rules = {
            0: [{"bbox": [137.88, 1236.0, 903.24, 1238.0], "coverage": 0.64, "max_row_dark_ratio": 0.77}],
            2: [{"bbox": [137.88, 790.0, 903.24, 790.0], "coverage": 0.64, "max_row_dark_ratio": 0.77}],
        }

        with (
            patch.object(example_trial, "load_paddle_raw_pages", return_value=pages),
            patch.object(example_trial, "raw_example_pdf_visual_rules", return_value=rules),
        ):
            context = example_trial.build_structured_context(structured_dir)
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter27",
                context=context,
                existing_ids=set(),
                target_ids={"27.2"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        content = recovered[0].content_markdown
        self.assertIn("Figure 27.4 Top", content)
        self.assertIn("provides the basis", content)
        self.assertIn("F(x)", content)
        self.assertNotIn("following ordinary discussion", content)
        self.assertTrue(recovered[0].evidence["visual_stop_clipped"])

    def test_raw_layout_merge_preserves_inline_table_inside_structured_example(self):
        root = make_test_workspace("raw_layout_inline_table_merge")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_006.json",
            {
                "id": "chapter25_006",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before."},
                    {
                        "type": "discussion",
                        "content": (
                            "Example 25.4. The selection limit is computed as $$ R=n a $$. "
                            "At the selection limit, the mean phenotype is extreme."
                        ),
                    },
                ],
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
                        "rows": [["n", "R"], ["5", "31.6"]],
                        "html": "",
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_006", "page": 9},
                    }
                ]
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Example 25.4. The selection limit is computed as",
                            "block_bbox": [160, 100, 880, 150],
                        },
                        {
                            "block_label": "display_formula",
                            "block_content": "$$ R=n a $$",
                            "block_bbox": [230, 170, 820, 210],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "The resulting values of these various quantities become",
                            "block_bbox": [160, 230, 720, 250],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>n</td><td>R</td></tr><tr><td>5</td><td>31.6</td></tr></table>",
                            "block_bbox": [230, 260, 820, 360],
                        },
                        {
                            "block_label": "text",
                            "block_content": "At the selection limit, the mean phenotype is extreme.",
                            "block_bbox": [160, 380, 880, 430],
                        },
                    ]
                }
            }
        ]

        with patch.object(example_trial, "load_paddle_raw_pages", return_value=pages):
            summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["raw_layout_merge_stats"]["rows_merged"], 1)
        library = read_json(structured_dir / "example_library.json")
        row = [item for item in library["examples"] if item["example_id"] == "25.4"][0]
        self.assertIn("[[TABLE:inline_1]]", row["content_markdown"])
        self.assertEqual(row["replacement"]["source_block_span"], [1, 2])

    def test_raw_box_allows_figure_title_continuation_before_inline_table(self):
        root = make_test_workspace("raw_box_figure_title_continuation")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_006.json",
            {
                "id": "chapter25_006",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": (
                            "Example 25.4. The selection limit is computed as $$ R=n a $$. "
                            "At the selection limit, the mean phenotype is extreme."
                        ),
                    },
                ],
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
                        "rows": [["n", "R"], ["25", "70.7"]],
                        "html": "",
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_006", "page": 9},
                    }
                ]
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "Example 25.4. The selection limit is computed as",
                            "block_bbox": [168, 746, 881, 990],
                        },
                        {
                            "block_label": "display_formula",
                            "block_content": "$$ R=n a $$",
                            "block_bbox": [236, 1009, 810, 1060],
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "The resulting values of these various quantities become",
                            "block_bbox": [168, 1081, 719, 1103],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>n</td><td>R</td></tr><tr><td>25</td><td>70.7</td></tr></table>",
                            "block_bbox": [238, 1107, 816, 1289],
                        },
                        {
                            "block_label": "text",
                            "block_content": "At the selection limit, the mean phenotype is extreme.",
                            "block_bbox": [167, 1300, 880, 1450],
                        },
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "paragraph_title",
                            "block_content": "NEXT SECTION",
                            "block_bbox": [133, 340, 700, 365],
                        }
                    ]
                }
            },
        ]
        rules = {0: [{"bbox": [137.88, 720.0, 903.24, 722.0], "coverage": 0.64}]}

        with (
            patch.object(example_trial, "load_paddle_raw_pages", return_value=pages),
            patch.object(example_trial, "raw_example_pdf_visual_rules", return_value=rules),
        ):
            context = example_trial.build_structured_context(structured_dir)
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter25",
                context=context,
                existing_ids=set(),
                target_ids={"25.4"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        self.assertIn("The resulting values", recovered[0].content_markdown)
        self.assertIn("[[TABLE:inline_1]]", recovered[0].content_markdown)
        self.assertIn("At the selection limit", recovered[0].content_markdown)

    def test_raw_box_joins_hyphenated_footer_example_on_next_page(self):
        root = make_test_workspace("raw_box_footer_hyphen_continuation")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter25_025.json",
            {
                "id": "chapter25_025",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Intro."},
                    {
                        "type": "discussion",
                        "content": (
                            "The selected line shows large increases in additive variance. "
                            "Why do lethal alleles persist in some selected populations?"
                        ),
                    },
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
                        "title": "Inline Table 2",
                        "table_type": "inline",
                        "rows": [["Population", "h2"], ["Selected", "0.54"]],
                        "html": "",
                        "source": {"chapter": "chapter25", "unit_id": "chapter25_025", "page": 35},
                    }
                ]
            },
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "footer",
                            "block_content": "Example 25.9. Consider variance components from a selection ex-",
                            "block_bbox": [323, 1429, 1035, 1452],
                        }
                    ]
                }
            },
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {"block_label": "header", "block_content": "CHAPTER TITLE", "block_bbox": [543, 160, 1004, 183]},
                        {"block_label": "number", "block_content": "947", "block_bbox": [1034, 161, 1069, 181]},
                        {
                            "block_label": "figure_title",
                            "block_content": "periment by Reeve and Robertson.",
                            "block_bbox": [168, 208, 880, 231],
                        },
                        {
                            "block_label": "table",
                            "block_content": "<table><tr><td>Population</td><td>h2</td></tr><tr><td>Selected</td><td>0.54</td></tr></table>",
                            "block_bbox": [250, 236, 800, 335],
                        },
                        {
                            "block_label": "text",
                            "block_content": "The selected line shows large increases in additive variance.",
                            "block_bbox": [168, 348, 882, 582],
                        },
                        {
                            "block_label": "text",
                            "block_content": "Why do lethal alleles persist in some selected populations?",
                            "block_bbox": [132, 644, 905, 944],
                        },
                    ]
                }
            },
        ]
        rules = {
            0: [{"bbox": [293.75, 1394.0, 1059.11, 1396.0], "coverage": 0.64}],
            1: [{"bbox": [137.88, 608.0, 903.24, 610.0], "coverage": 0.64}],
        }

        with (
            patch.object(example_trial, "load_paddle_raw_pages", return_value=pages),
            patch.object(example_trial, "raw_example_pdf_visual_rules", return_value=rules),
        ):
            context = example_trial.build_structured_context(structured_dir)
            recovered = example_trial.recover_examples_from_paddle_raw(
                project_root=root,
                chapter="chapter25",
                context=context,
                existing_ids=set(),
                target_ids={"25.9"},
                skip_structured_matches=False,
            )

        self.assertEqual(len(recovered), 1)
        self.assertIn("selection experiment by Reeve", recovered[0].content_markdown)
        self.assertRegex(recovered[0].content_markdown, r"\[\[TABLE:inline_\d+\]\]")
        self.assertIn("The selected line shows", recovered[0].content_markdown)
        self.assertNotIn("Why do lethal alleles persist", recovered[0].content_markdown)
        self.assertTrue(recovered[0].evidence["visual_stop_clipped"])

    def test_raw_layout_refresh_preserves_existing_owner_when_adding_inline_table(self):
        root = make_test_workspace("raw_refresh_preserves_owner")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter25_full" / "intermediate"
        write_json(
            structured_dir / "chapter25_006.json",
            {
                "id": "chapter25_006",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "example", "content": "[[SEE_EXAMPLE:25.4]]"},
                    {
                        "type": "discussion",
                        "content": "Example 25.4. As an example of the consequences for the limit, R, and half-life, t0.5, consider many loci.",
                    },
                    {"type": "discussion", "content": "The resulting values for n loci are summarized in an inline table."},
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_015.json",
            {
                "id": "chapter25_015",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {
                        "type": "discussion",
                        "content": "Later discussion repeats the consequences for the limit and half-life, but it is not the example owner.",
                    },
                ],
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
                        "example_id": "25.4",
                        "chapter": "chapter25",
                        "label": "Example 25.4",
                        "title": "Existing owner",
                        "source_file": "chapter25_006.json",
                        "start_block_index": 1,
                        "end_block_index": 2,
                        "block_ids": [],
                        "content_markdown": "Example 25.4. As an example of the consequences for the limit, R, and half-life, t0.5, consider many loci.",
                        "content_plain": "Example 25.4. As an example of the consequences for the limit, R, and half-life, t0.5, consider many loci.",
                        "formula_refs": [],
                        "table_refs": ["25.1"],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False, "source_block_span": [1, 2]},
                        "example_ref": "25.4",
                        "placeholder": "[[SEE_EXAMPLE:25.4]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [1, 2],
                            "placeholder_block_index": 0,
                            "placeholder_source_file": "chapter25_006.json",
                        },
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
                                "block_label": "figure_title",
                                "block_content": "Example 25.4. As an example of the consequences for the limit, R, and half-life, t0.5, consider many loci.",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "table",
                                "block_content": "<table><tr><td>n</td><td>R</td></tr><tr><td>10</td><td>2.1</td></tr></table>",
                                "block_bbox": [100, 140, 500, 180],
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "The resulting values show that the limit increases with the number of loci.",
                                "block_bbox": [100, 190, 500, 220],
                            },
                            {
                                "block_label": "text",
                                "block_content": "MAJOR GENES VERSUS POLYGENIC RESPONSE: THEORY",
                                "block_bbox": [100, 320, 500, 350],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        refresh = summary["existing_library_repair_stats"]["raw_layout_refresh"]
        self.assertEqual(refresh["rows_replaced"], 1)
        row = read_json(structured_dir / "example_library.json")["examples"][0]
        self.assertEqual(row["source_file"], "chapter25_006.json")
        self.assertEqual(row["replacement"]["source_block_span"], [1, 2])
        self.assertEqual(row["replacement"]["placeholder_source_file"], "chapter25_006.json")
        self.assertIn("[[TABLE:inline_1]]", row["content_markdown"])

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

    def test_existing_library_repair_preserves_cross_unit_nonmonotonic_placeholders(self):
        root = make_test_workspace("nonmonotonic_examples")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter9_001.json",
            {
                "id": "chapter9_001",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.2]]"}],
            },
        )
        write_json(
            structured_dir / "chapter9_002.json",
            {
                "id": "chapter9_002",
                "metadata": {"chapter": "chapter9", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:9.1]]"}],
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
                        "example_id": "9.1",
                        "chapter": "chapter9",
                        "label": "Example 9.1",
                        "title": "First",
                        "source_file": "chapter9_002.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 9.1. First example.",
                        "content_plain": "Example 9.1. First example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.1",
                        "placeholder": "[[SEE_EXAMPLE:9.1]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                    {
                        "example_id": "9.2",
                        "chapter": "chapter9",
                        "label": "Example 9.2",
                        "title": "Second",
                        "source_file": "chapter9_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 9.2. Second example.",
                        "content_plain": "Example 9.2. Second example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "9.2",
                        "placeholder": "[[SEE_EXAMPLE:9.2]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                ],
            },
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]["monotonic_order"]
        self.assertEqual(repair["rows_relocated"], 0)
        self.assertEqual(read_json(structured_dir / "chapter9_001.json")["blocks"], [{"type": "example", "content": "[[SEE_EXAMPLE:9.2]]"}])
        self.assertEqual(read_json(structured_dir / "chapter9_002.json")["blocks"], [{"type": "example", "content": "[[SEE_EXAMPLE:9.1]]"}])
        rows_by_ref = {row["example_ref"]: row for row in read_json(structured_dir / "example_library.json")["examples"]}
        self.assertEqual(rows_by_ref["9.2"]["source_file"], "chapter9_001.json")
        self.assertEqual(rows_by_ref["9.2"]["start_block_index"], 0)

    def test_existing_library_repair_orders_placeholders_with_intervening_text(self):
        root = make_test_workspace("nonmonotonic_with_intervening_text")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter30_001.json",
            {
                "id": "chapter30_001",
                "metadata": {"chapter": "chapter30", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before path analysis."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:30.8]]"},
                    {"type": "discussion", "content": "Middle discussion."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:30.7]]"},
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
                        "example_id": "30.8",
                        "chapter": "chapter30",
                        "label": "Example 30.8",
                        "title": "Later",
                        "source_file": "chapter30_001.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "block_ids": [],
                        "content_markdown": "Example 30.8. Later path example.",
                        "content_plain": "Example 30.8. Later path example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "30.8",
                        "placeholder": "[[SEE_EXAMPLE:30.8]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [1, 1]},
                    },
                    {
                        "example_id": "30.7",
                        "chapter": "chapter30",
                        "label": "Example 30.7",
                        "title": "Earlier",
                        "source_file": "chapter30_001.json",
                        "start_block_index": 3,
                        "end_block_index": 3,
                        "block_ids": [],
                        "content_markdown": "Example 30.7. Earlier projection-pursuit example.",
                        "content_plain": "Example 30.7. Earlier projection-pursuit example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "30.7",
                        "placeholder": "[[SEE_EXAMPLE:30.7]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [3, 3]},
                    },
                ],
            },
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["existing_library_repair_stats"]["monotonic_order"]["rows_relocated"], 1)
        unit = read_json(structured_dir / "chapter30_001.json")
        self.assertEqual(
            [block["content"] for block in unit["blocks"] if block["type"] == "example"],
            ["[[SEE_EXAMPLE:30.7]]", "[[SEE_EXAMPLE:30.8]]"],
        )
        rows = {row["example_id"]: row for row in read_json(structured_dir / "example_library.json")["examples"]}
        self.assertEqual(rows["30.7"]["start_block_index"], 2)
        self.assertEqual(rows["30.8"]["start_block_index"], 3)

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

    def test_raw_layout_global_order_repairs_same_chunk_reversed_placeholders(self):
        root = make_test_workspace("raw_global_order_same_chunk")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter30_full" / "intermediate"
        write_json(
            structured_dir / "chapter30_001.json",
            {
                "id": "chapter30_001",
                "metadata": {"chapter": "chapter30", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before path analysis."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:30.8]]"},
                    {"type": "discussion", "content": "Middle discussion."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:30.7]]"},
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
                        "example_id": "30.8",
                        "chapter": "chapter30",
                        "label": "Example 30.8",
                        "title": "Later",
                        "source_file": "chapter30_001.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "block_ids": [],
                        "content_markdown": "Example 30.8. Later path example.",
                        "content_plain": "Example 30.8. Later path example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "30.8",
                        "placeholder": "[[SEE_EXAMPLE:30.8]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [1, 1]},
                    },
                    {
                        "example_id": "30.7",
                        "chapter": "chapter30",
                        "label": "Example 30.7",
                        "title": "Earlier",
                        "source_file": "chapter30_001.json",
                        "start_block_index": 3,
                        "end_block_index": 3,
                        "block_ids": [],
                        "content_markdown": "Example 30.7. Earlier projection-pursuit example.",
                        "content_plain": "Example 30.7. Earlier projection-pursuit example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "30.7",
                        "placeholder": "[[SEE_EXAMPLE:30.7]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [3, 3]},
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
                                "block_label": "figure_title",
                                "block_content": "Example 30.7. Earlier projection-pursuit example.",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "Example 30.8. Later path example.",
                                "block_bbox": [100, 220, 500, 250],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]
        self.assertEqual(repair["monotonic_order"]["rows_relocated"], 1)
        unit = read_json(structured_dir / "chapter30_001.json")
        self.assertEqual(
            [block["content"] for block in unit["blocks"] if block["type"] == "example"],
            ["[[SEE_EXAMPLE:30.7]]", "[[SEE_EXAMPLE:30.8]]"],
        )
        rows = {row["example_id"]: row for row in read_json(structured_dir / "example_library.json")["examples"]}
        self.assertLess(rows["30.7"]["start_block_index"], rows["30.8"]["start_block_index"])

    def test_raw_layout_global_order_repairs_example_heading_unit(self):
        root = make_test_workspace("raw_global_order_heading_unit")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter28_full" / "intermediate"
        write_json(
            structured_dir / "chapter28_001.json",
            {
                "id": "chapter28_001",
                "metadata": {"chapter": "chapter28", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:28.15]]"}],
            },
        )
        write_json(
            structured_dir / "chapter28_002.json",
            {
                "id": "chapter28_002",
                "metadata": {
                    "chapter": "chapter28",
                    "section_level_1": "Joint-effects Models",
                    "section_level_2": "Example 28.15. As an application of the joint-effects model, suppose that",
                    "display_heading": "Example 28.15. As an application of the joint-effects model, suppose that",
                    "heading_path": [
                        "Joint-effects Models",
                        "Example 28.15. As an application of the joint-effects model, suppose that",
                    ],
                    "formula_references": [],
                    "table_references": [],
                },
                "blocks": [
                    {"type": "discussion", "content": "Thus, a reasonable amount of genetic variation is maintained."},
                ],
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
                        "example_id": "28.15",
                        "chapter": "chapter28",
                        "label": "Example 28.15",
                        "title": "Wrong early owner",
                        "source_file": "chapter28_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 28.15. Wrong early owner.",
                        "content_plain": "Example 28.15. Wrong early owner.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "28.15",
                        "placeholder": "[[SEE_EXAMPLE:28.15]]",
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
                            {"block_label": "text", "block_content": "Earlier theory.", "block_bbox": [100, 100, 500, 130]},
                            {
                                "block_label": "paragraph_title",
                                "block_content": "Example 28.15. As an application of the joint-effects model, suppose that",
                                "block_bbox": [100, 220, 500, 250],
                            },
                            {
                                "block_label": "text",
                                "block_content": "Thus, a reasonable amount of genetic variation is maintained.",
                                "block_bbox": [100, 280, 500, 310],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]["raw_layout_global_order"]
        self.assertEqual(repair["heading_units_repaired"], 1)
        early = read_json(structured_dir / "chapter28_001.json")
        self.assertEqual(early["blocks"], [])
        fixed = read_json(structured_dir / "chapter28_002.json")
        self.assertEqual(fixed["blocks"], [{"type": "example", "content": "[[SEE_EXAMPLE:28.15]]"}])
        self.assertEqual(fixed["metadata"]["display_heading"], "Joint-effects Models")
        rows = read_json(structured_dir / "example_library.json")["examples"]
        self.assertEqual(rows[0]["source_file"], "chapter28_002.json")
        self.assertIn("As an application", rows[0]["content_markdown"])

    def test_raw_layout_global_order_keeps_stable_cross_unit_placeholder(self):
        root = make_test_workspace("raw_global_order_stable_placeholder")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter25_full" / "intermediate"
        write_json(
            structured_dir / "chapter25_006.json",
            {
                "id": "chapter25_006",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Before the fourth example."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:25.4]]"},
                ],
            },
        )
        write_json(
            structured_dir / "chapter25_015.json",
            {
                "id": "chapter25_015",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "example", "content": "[[SEE_EXAMPLE:25.3]]"},
                    {"type": "discussion", "content": "Later unrelated discussion."},
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
                        "example_id": "25.3",
                        "chapter": "chapter25",
                        "label": "Example 25.3",
                        "title": "Earlier raw example",
                        "source_file": "chapter25_015.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 25.3. Earlier raw example.",
                        "content_plain": "Example 25.3. Earlier raw example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "25.3",
                        "placeholder": "[[SEE_EXAMPLE:25.3]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                    {
                        "example_id": "25.4",
                        "chapter": "chapter25",
                        "label": "Example 25.4",
                        "title": "Stable owner",
                        "source_file": "chapter25_006.json",
                        "start_block_index": 1,
                        "end_block_index": 1,
                        "block_ids": [],
                        "content_markdown": "Example 25.4. Stable owner with an inline table.",
                        "content_plain": "Example 25.4. Stable owner with an inline table.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "25.4",
                        "placeholder": "[[SEE_EXAMPLE:25.4]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [1, 1]},
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
                                "block_label": "figure_title",
                                "block_content": "Example 25.3. Earlier raw example.",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "Example 25.4. Stable owner with an inline table.",
                                "block_bbox": [100, 220, 500, 250],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        repair = summary["existing_library_repair_stats"]["raw_layout_global_order"]
        self.assertEqual(repair["rows_relocated"], 0)
        early = read_json(structured_dir / "chapter25_006.json")
        later = read_json(structured_dir / "chapter25_015.json")
        self.assertIn({"type": "example", "content": "[[SEE_EXAMPLE:25.4]]"}, early["blocks"])
        self.assertIn({"type": "example", "content": "[[SEE_EXAMPLE:25.3]]"}, later["blocks"])
        rows = {row["example_id"]: row for row in read_json(structured_dir / "example_library.json")["examples"]}
        self.assertEqual(rows["25.4"]["source_file"], "chapter25_006.json")

    def test_missing_placeholder_restore_preserves_source_span(self):
        root = make_test_workspace("missing_placeholder_preserves_source_span")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter25_full" / "intermediate"
        write_json(
            structured_dir / "chapter25_025.json",
            {
                "id": "chapter25_025",
                "metadata": {"chapter": "chapter25", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Previous body anchor."},
                    {"type": "discussion", "content": "Example 25.10. This example source body continues."},
                    {"type": "discussion", "content": "The tail remains part of the example source span."},
                    {"type": "discussion", "content": "Following section body."},
                ],
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
                        "example_id": "25.10",
                        "chapter": "chapter25",
                        "label": "Example 25.10",
                        "title": "Missing placeholder",
                        "source_file": "chapter25_025.json",
                        "start_block_index": 1,
                        "end_block_index": 2,
                        "block_ids": [],
                        "content_markdown": "Example 25.10. This example source body continues. The tail remains part of the example source span.",
                        "content_plain": "Example 25.10. This example source body continues. The tail remains part of the example source span.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False, "source_block_span": [1, 2]},
                        "example_ref": "25.10",
                        "placeholder": "[[SEE_EXAMPLE:25.10]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [1, 2],
                        },
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
                                "block_content": "Previous body anchor.",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "figure_title",
                                "block_content": "Example 25.10. This example source body continues.",
                                "block_bbox": [100, 220, 500, 250],
                            },
                            {
                                "block_label": "text",
                                "block_content": "Following section body.",
                                "block_bbox": [100, 360, 500, 390],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        restore = summary["existing_library_repair_stats"]["missing_placeholder_restore"]
        self.assertEqual(restore["placeholders_inserted"], 1)
        row = read_json(structured_dir / "example_library.json")["examples"][0]
        self.assertEqual(row["source_file"], "chapter25_025.json")
        self.assertEqual(row["start_block_index"], 1)
        self.assertEqual(row["end_block_index"], 2)
        self.assertEqual(row["replacement"]["source_block_span"], [1, 2])
        self.assertEqual(row["replacement"]["placeholder_source_file"], "chapter25_025.json")

    def test_raw_layout_heading_unit_repair_preserves_trailing_body(self):
        root = make_test_workspace("raw_global_order_heading_trailing")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter28_full" / "intermediate"
        write_json(
            structured_dir / "chapter28_001.json",
            {
                "id": "chapter28_001",
                "metadata": {"chapter": "chapter28", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:28.15]]"}],
            },
        )
        write_json(
            structured_dir / "chapter28_002.json",
            {
                "id": "chapter28_002",
                "metadata": {
                    "chapter": "chapter28",
                    "section_level_1": "Joint-effects Models",
                    "display_heading": "Example 28.15. As an application of the joint-effects model, suppose that",
                    "formula_references": [],
                    "table_references": [],
                },
                "blocks": [
                    {"type": "discussion", "content": "Thus, a reasonable amount of genetic variation is maintained."},
                    {"type": "discussion", "content": "The following section should remain ordinary body text."},
                ],
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
                        "example_id": "28.15",
                        "chapter": "chapter28",
                        "label": "Example 28.15",
                        "title": "Wrong early owner",
                        "source_file": "chapter28_001.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 28.15. Wrong early owner.",
                        "content_plain": "Example 28.15. Wrong early owner.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "28.15",
                        "placeholder": "[[SEE_EXAMPLE:28.15]]",
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
                                "block_label": "paragraph_title",
                                "block_content": "Example 28.15. As an application of the joint-effects model, suppose that",
                                "block_bbox": [100, 220, 500, 250],
                            },
                            {
                                "block_label": "text",
                                "block_content": "Thus, a reasonable amount of genetic variation is maintained.",
                                "block_bbox": [100, 280, 500, 310],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        self.assertEqual(summary["existing_library_repair_stats"]["raw_layout_global_order"]["heading_units_repaired"], 1)
        fixed = read_json(structured_dir / "chapter28_002.json")
        self.assertEqual(
            fixed["blocks"],
            [
                {"type": "example", "content": "[[SEE_EXAMPLE:28.15]]"},
                {"type": "discussion", "content": "The following section should remain ordinary body text."},
            ],
        )

    def test_existing_library_repair_removes_duplicate_placeholder_copies(self):
        root = make_test_workspace("duplicate_placeholder_cleanup")
        structured_dir = root / "structured"
        write_json(
            structured_dir / "chapter10_001.json",
            {
                "id": "chapter10_001",
                "metadata": {"chapter": "chapter10", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Previous discussion."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:10.11]]"},
                ],
            },
        )
        write_json(
            structured_dir / "chapter10_002.json",
            {
                "id": "chapter10_002",
                "metadata": {"chapter": "chapter10", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "example", "content": "[[SEE_EXAMPLE:10.11]]"},
                    {"type": "discussion", "content": "Following discussion."},
                ],
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
                        "example_id": "10.11",
                        "chapter": "chapter10",
                        "label": "Example 10.11",
                        "title": "Duplicate placeholder",
                        "source_file": "chapter10_002.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 10.11. Canonical body.",
                        "content_plain": "Example 10.11. Canonical body.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "10.11",
                        "placeholder": "[[SEE_EXAMPLE:10.11]]",
                        "replacement": {
                            "status": "replaced",
                            "reason": "placeholder_block_written",
                            "source_block_span": [0, 0],
                            "placeholder_block_index": 0,
                            "placeholder_source_file": "chapter10_002.json",
                        },
                    }
                ],
            },
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        cleanup = summary["existing_library_repair_stats"]["duplicate_placeholders"]
        self.assertEqual(cleanup["duplicate_placeholders_removed"], 1)
        previous = read_json(structured_dir / "chapter10_001.json")
        canonical = read_json(structured_dir / "chapter10_002.json")
        self.assertNotIn("[[SEE_EXAMPLE:10.11]]", str(previous["blocks"]))
        self.assertIn("[[SEE_EXAMPLE:10.11]]", str(canonical["blocks"]))

    def test_reextract_adds_library_row_for_orphan_placeholder_from_raw_layout(self):
        root = make_test_workspace("orphan_placeholder_raw_recovery")
        structured_dir = root / "structured"
        raw_dir = root / "tmp" / "paddle_output" / "chapter3_full" / "intermediate"
        write_json(
            structured_dir / "chapter3_013.json",
            {
                "id": "chapter3_013",
                "metadata": {"chapter": "chapter3", "formula_references": [], "table_references": []},
                "blocks": [
                    {"type": "discussion", "content": "Background selection discussion."},
                    {"type": "example", "content": "[[SEE_EXAMPLE:3.6]]"},
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
                        "example_id": "3.5",
                        "chapter": "chapter3",
                        "label": "Example 3.5",
                        "title": "Previous",
                        "source_file": "chapter3_012.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 3.5. Previous example.",
                        "content_plain": "Example 3.5. Previous example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "3.5",
                        "placeholder": "[[SEE_EXAMPLE:3.5]]",
                        "replacement": {"status": "replaced", "reason": "placeholder_block_written", "source_block_span": [0, 0]},
                    },
                    {
                        "example_id": "3.7",
                        "chapter": "chapter3",
                        "label": "Example 3.7",
                        "title": "Next",
                        "source_file": "chapter3_014.json",
                        "start_block_index": 0,
                        "end_block_index": 0,
                        "block_ids": [],
                        "content_markdown": "Example 3.7. Next example.",
                        "content_plain": "Example 3.7. Next example.",
                        "formula_refs": [],
                        "table_refs": [],
                        "figure_refs": [],
                        "external_refs": [],
                        "evidence": {},
                        "metadata": {"needs_review": False},
                        "example_ref": "3.7",
                        "placeholder": "[[SEE_EXAMPLE:3.7]]",
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
                                "block_content": "Example 3.6. Because natural populations are subject to both positive and negative selective forces.",
                                "block_bbox": [100, 100, 500, 130],
                            },
                            {
                                "block_label": "text",
                                "block_content": "Consider a large monoecious population of constant breeding size.",
                                "block_bbox": [100, 150, 500, 180],
                            },
                        ]
                    }
                }
            ],
        )

        summary = apply_example_pipeline(structured_dir, project_root=root)

        orphan_stats = summary.get("orphan_placeholder_stats")
        if orphan_stats is None:
            orphan_stats = summary["existing_library_repair_stats"]["orphan_placeholders"]
        self.assertEqual(orphan_stats["rows_added"], 1)
        rows = {row["example_id"]: row for row in read_json(structured_dir / "example_library.json")["examples"]}
        self.assertIn("3.6", rows)
        self.assertIn("positive and negative", rows["3.6"]["content_markdown"])


if __name__ == "__main__":
    unittest.main()
