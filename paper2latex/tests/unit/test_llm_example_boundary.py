import shutil
import unittest
from pathlib import Path

from knowledge_engineering.core.common import read_json, write_json
from knowledge_engineering.processors.llm_example_boundary import (
    build_example_candidate_from_decision,
    collect_example_boundary_windows,
    run_llm_example_boundary_trial,
    validate_llm_example_decision,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEST_RUNTIME_ROOT = PROJECT_ROOT / "tmp" / "test_runtime" / "llm_example_boundary"


class FakeBoundaryClient:
    def __init__(self, decisions):
        self.decisions = list(decisions)

    def _post_chat_completion(self, *, messages, json_mode=False):
        del messages, json_mode
        if not self.decisions:
            raise AssertionError("No fake LLM decision left")
        import json

        return json.dumps(self.decisions.pop(0), ensure_ascii=False)

    def get_metrics(self):
        return {"provider": "fake", "model": "fake-boundary"}


def _raw_row(label, content, *, top):
    return {
        "block_label": label,
        "block_content": content,
        "block_bbox": [100, top, 500, top + 20],
        "block_order": top,
    }


def _write_raw_project(root: Path, chapter: str, rows: list[dict]) -> None:
    raw_dir = root / "tmp" / "paddle_output" / f"{chapter}_full" / "intermediate"
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_json(raw_dir / "paddle_raw_response.json", [{"prunedResult": {"parsing_res_list": rows}}])


def _write_structured(root: Path, chapter8: bool = False) -> Path:
    structured = root / "structured"
    structured.mkdir(parents=True, exist_ok=True)
    write_json(
        structured / "chapter6_005.json",
        {
            "id": "chapter6_005",
            "metadata": {
                "chapter": "chapter6",
                "section": "SECTION",
                "subsections": ["SUBSECTION"],
                "source_title": "Book",
                "formula_references": ["6.20"],
                "table_references": ["inline_1"],
            },
            "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:6.2]]"}],
        },
    )
    write_json(
        structured / "chapter6_008.json",
        {
            "id": "chapter6_008",
            "metadata": {
                "chapter": "chapter6",
                "section": "SECTION",
                "subsections": ["SUBSECTION"],
                "source_title": "Book",
                "formula_references": ["6.30a", "6.30b"],
                "table_references": [],
            },
            "blocks": [
                {"type": "discussion", "content": "Bridge text before the missing example."},
                {
                    "type": "discussion",
                    "content": (
                        "The exact model begins with a rare dominant allele and then follows the "
                        "population-genetic recursion across generations."
                    ),
                },
                {
                    "type": "derivation",
                    "content": (
                        "The trait mean before selection is discussed here [[SEE_FORMULA:6.30a]] "
                        "and the predicted response follows [[SEE_FORMULA:6.30b]]."
                    ),
                },
            ],
        },
    )
    write_json(
        structured / "formula_library.json",
        {
            "metadata": {},
            "formulas": [
                {"id": "6.20", "source": {"chapter": "chapter6"}, "latex": "x"},
                {"id": "6.21", "source": {"chapter": "chapter6"}, "latex": "y"},
                {"id": "6.30a", "source": {"chapter": "chapter6"}, "latex": "a"},
                {"id": "6.30b", "source": {"chapter": "chapter6"}, "latex": "b"},
            ],
        },
    )
    write_json(
        structured / "table_library.json",
        {
            "metadata": {},
            "tables": [
                {"id": "inline_1", "source": {"chapter": "chapter6", "unit_id": "chapter6_005"}},
                {"id": "inline_2", "source": {"chapter": "chapter6", "unit_id": "chapter6_008"}},
            ],
        },
    )
    examples = [
        {
            "example_id": "6.2",
            "chapter": "chapter6",
            "label": "Example 6.2",
            "title": "short",
            "source_file": "chapter6_005.json",
            "start_block_index": 0,
            "end_block_index": 0,
            "block_ids": [],
            "content_markdown": "Example 6.2. Short incomplete example text.",
            "content_plain": "Example 6.2. Short incomplete example text.",
            "formula_refs": [],
            "table_refs": [],
            "figure_refs": [],
            "external_refs": [],
            "evidence": {},
            "metadata": {"needs_review": True, "word_count": 6},
            "example_ref": "6.2",
            "placeholder": "[[SEE_EXAMPLE:6.2]]",
            "replacement": {"status": "replaced", "reason": "fixture", "source_block_span": [0, 0]},
        }
    ]
    if chapter8:
        examples.append(
            {
                "example_id": "6.8",
                "chapter": "chapter6",
                "label": "Example 6.8",
                "title": "later",
                "source_file": "chapter6_009.json",
                "start_block_index": 0,
                "end_block_index": 0,
                "block_ids": [],
                "content_markdown": "Example 6.8. Later example.",
                "content_plain": "Example 6.8. Later example.",
                "formula_refs": [],
                "table_refs": [],
                "figure_refs": [],
                "external_refs": [],
                "evidence": {},
                "metadata": {"needs_review": False, "word_count": 4},
                "example_ref": "6.8",
                "placeholder": "[[SEE_EXAMPLE:6.8]]",
                "replacement": {"status": "replaced", "reason": "fixture", "source_block_span": [0, 0]},
            }
        )
    write_json(structured / "example_library.json", {"schema": "example_library.v1", "example_count": len(examples), "examples": examples})
    return structured


class LLMExampleBoundaryTest(unittest.TestCase):
    def setUp(self):
        if TEST_RUNTIME_ROOT.exists():
            shutil.rmtree(TEST_RUNTIME_ROOT)
        TEST_RUNTIME_ROOT.mkdir(parents=True)

    def tearDown(self):
        if TEST_RUNTIME_ROOT.exists():
            shutil.rmtree(TEST_RUNTIME_ROOT)

    def test_mock_llm_applies_complete_example_with_table_and_formulas(self):
        rows = [
            _raw_row("figure_title", "Example 6.2. A complete boundary starts here.", top=10),
            _raw_row("table", "<table><tr><td>Genotype</td></tr></table>", top=40),
            _raw_row("text", "The exact model text continues after the inline table.", top=70),
            _raw_row("display_formula", "$$ x=y $$", top=100),
            _raw_row("formula_number", "(6.20)", top=130),
            _raw_row("text", "More explanation belongs inside this example.", top=160),
            _raw_row("display_formula", "$$ y=z $$", top=190),
            _raw_row("formula_number", "(6.21)", top=220),
            _raw_row("text", "which recovers the previous equation.", top=250),
            _raw_row("paragraph_title", "Next Section Title", top=320),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter6", rows)
        structured = _write_structured(TEST_RUNTIME_ROOT)
        output = TEST_RUNTIME_ROOT / "candidate" / "structured"
        artifacts = TEST_RUNTIME_ROOT / "candidate" / "artifacts"

        summary = run_llm_example_boundary_trial(
            structured_dir=structured,
            project_root=TEST_RUNTIME_ROOT,
            output_structured_dir=output,
            artifacts_dir=artifacts,
            chapters=["chapter6"],
            max_windows=5,
            client=FakeBoundaryClient(
                [
                    {
                        "example_id": "6.2",
                        "start_row_index": 0,
                        "end_row_index": 8,
                        "include_table_rows": [1],
                        "include_formula_rows": [3, 4, 6, 7],
                        "is_complete": True,
                        "confidence": 0.95,
                        "reason": "Stops before paragraph_title.",
                        "apply_mode": "auto",
                    }
                ]
            ),
        )

        self.assertEqual(summary["auto_applied"], 1)
        library = read_json(output / "example_library.json")
        example = next(row for row in library["examples"] if row["example_id"] == "6.2")
        self.assertIn("[[TABLE:inline_1]]", example["content_markdown"])
        self.assertIn("[[SEE_FORMULA:6.20]]", example["content_markdown"])
        self.assertIn("[[SEE_FORMULA:6.21]]", example["content_markdown"])
        self.assertIn("which recovers the previous equation", example["content_markdown"])

    def test_missing_example_can_be_added_from_raw_title(self):
        rows = [
            _raw_row("figure_title", "Example 6.3. The missing example starts here.", top=10),
            _raw_row(
                "text",
                "The exact model begins with a rare dominant allele and then follows the population-genetic recursion across generations.",
                top=40,
            ),
            _raw_row("table", "<table><tr><td>Genotype</td><td>QQ</td></tr></table>", top=70),
            _raw_row("text", "The trait mean before selection is discussed here", top=100),
            _raw_row("display_formula", "$$ a=b $$", top=130),
            _raw_row("formula_number", "(6.30a)", top=160),
            _raw_row("text", "and the predicted response follows", top=190),
            _raw_row("display_formula", "$$ b=c $$", top=220),
            _raw_row("formula_number", "(6.30b)", top=250),
            _raw_row("paragraph_title", "FISHER'S FUNDAMENTAL THEOREM", top=300),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter6", rows)
        structured = _write_structured(TEST_RUNTIME_ROOT, chapter8=True)
        output = TEST_RUNTIME_ROOT / "candidate" / "structured"
        artifacts = TEST_RUNTIME_ROOT / "candidate" / "artifacts"

        summary = run_llm_example_boundary_trial(
            structured_dir=structured,
            project_root=TEST_RUNTIME_ROOT,
            output_structured_dir=output,
            artifacts_dir=artifacts,
            chapters=["chapter6"],
            max_windows=5,
            client=FakeBoundaryClient(
                [
                    {
                        "example_id": "6.3",
                        "start_row_index": 0,
                        "end_row_index": 8,
                        "include_table_rows": [2],
                        "include_formula_rows": [4, 5, 7, 8],
                        "is_complete": True,
                        "confidence": 0.96,
                        "reason": "Complete until next section.",
                        "apply_mode": "auto",
                    }
                ]
            ),
        )

        self.assertEqual(summary["auto_applied"], 1)
        library = read_json(output / "example_library.json")
        example = next(row for row in library["examples"] if row["example_id"] == "6.3")
        self.assertIn("[[TABLE:inline_1]]", example["content_markdown"])
        self.assertIn("[[SEE_FORMULA:6.30a]]", example["content_markdown"])
        chapter = read_json(output / "chapter6_008.json")
        self.assertTrue(any("[[SEE_EXAMPLE:6.3]]" in block.get("content", "") for block in chapter["blocks"]))

    def test_inline_reference_is_not_collected_as_example_heading(self):
        rows = [
            _raw_row("text", "Example 6.1 used the linear regression from the previous section.", top=10),
            _raw_row("display_formula", "$$ x=y $$", top=40),
            _raw_row("formula_number", "(6.11)", top=70),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter6", rows)
        structured = _write_structured(TEST_RUNTIME_ROOT)

        windows = collect_example_boundary_windows(
            structured,
            project_root=TEST_RUNTIME_ROOT,
            chapters=["chapter6"],
            max_windows=5,
            suspicious_only=False,
        )

        self.assertEqual(windows, [])

    def test_reference_content_example_heading_is_collected(self):
        rows = [
            _raw_row("text", "Context before the missing example.", top=10),
            _raw_row("reference_content", "Example 14.3. Consider a threshold trait whose liability starts here.", top=40),
            _raw_row("text", "The worked example continues on the next page.", top=70),
            _raw_row("text", "Example 14.4. The next example starts here.", top=110),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter14", rows)
        structured = TEST_RUNTIME_ROOT / "structured"
        structured.mkdir(parents=True, exist_ok=True)
        write_json(
            structured / "chapter14_001.json",
            {
                "id": "chapter14_001",
                "metadata": {"chapter": "chapter14", "formula_references": [], "table_references": []},
                "blocks": [{"type": "discussion", "content": "Context before the missing example."}],
            },
        )
        write_json(structured / "formula_library.json", {"formulas": []})
        write_json(structured / "table_library.json", {"tables": []})
        write_json(structured / "example_library.json", {"schema": "example_library.v1", "example_count": 0, "examples": []})

        windows = collect_example_boundary_windows(
            structured,
            project_root=TEST_RUNTIME_ROOT,
            chapters=["chapter14"],
            max_windows=5,
            suspicious_only=False,
        )

        self.assertEqual([window["expected_example_id"] for window in windows], ["14.3", "14.4"])
        self.assertEqual(windows[0]["rows"][0]["label"], "reference_content")

    def test_guardrail_rejects_decision_crossing_next_section_title(self):
        window = {
            "window_id": "chapter6:6.2:0-3",
            "expected_example_id": "6.2",
            "rows": [
                {"raw_row_index": 0, "label": "figure_title", "content": "Example 6.2. Starts here."},
                {"raw_row_index": 1, "label": "text", "content": "Body text."},
                {"raw_row_index": 2, "label": "paragraph_title", "content": "Next Section"},
            ],
        }
        decision = {
            "example_id": "6.2",
            "start_row_index": 0,
            "end_row_index": 2,
            "include_table_rows": [],
            "include_formula_rows": [],
            "is_complete": True,
            "confidence": 0.99,
            "apply_mode": "auto",
        }

        validation = validate_llm_example_decision(window, decision)

        self.assertEqual(validation["status"], "rejected")
        self.assertIn("includes_next_section_title", validation["errors"])

    def test_suspicious_window_stops_before_same_example_back_reference(self):
        rows = [
            _raw_row("text", "Example 24.4. The worked example starts here.", top=10),
            _raw_row("text", "The example body ends with a complete sentence.", top=40),
            _raw_row("text", "As Example 24.4 illustrates, this is normal body discussion.", top=70),
            _raw_row("paragraph_title", "Next Section", top=100),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter24", rows)
        structured = TEST_RUNTIME_ROOT / "structured"
        structured.mkdir(parents=True, exist_ok=True)
        write_json(
            structured / "chapter24_001.json",
            {
                "id": "chapter24_001",
                "metadata": {"chapter": "chapter24", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:24.4]]"}],
            },
        )
        write_json(structured / "formula_library.json", {"formulas": []})
        write_json(structured / "table_library.json", {"tables": []})
        write_json(
            structured / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "24.4",
                        "chapter": "chapter24",
                        "content_markdown": (
                            "Example 24.4. The worked example starts here. "
                            "The example body ends with a complete sentence. "
                            "As Example 24.4 illustrates, this is normal body discussion."
                        ),
                        "content_plain": (
                            "Example 24.4. The worked example starts here. "
                            "The example body ends with a complete sentence. "
                            "As Example 24.4 illustrates, this is normal body discussion."
                        ),
                        "metadata": {"needs_review": False},
                    }
                ],
            },
        )

        windows = collect_example_boundary_windows(
            structured,
            project_root=TEST_RUNTIME_ROOT,
            chapters=["chapter24"],
            max_windows=5,
        )

        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["end_raw_index"], 1)

    def test_suspicious_window_stops_before_same_example_back_reference_without_as(self):
        rows = [
            _raw_row("text", "Example 17.4. The worked example starts here.", top=10),
            _raw_row("text", "The example body ends with a complete sentence.", top=40),
            _raw_row("text", "Example 17.4 illustrates the fact that this is following discussion.", top=70),
            _raw_row("paragraph_title", "Next Section", top=100),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter17", rows)
        structured = TEST_RUNTIME_ROOT / "structured"
        structured.mkdir(parents=True, exist_ok=True)
        write_json(
            structured / "chapter17_001.json",
            {
                "id": "chapter17_001",
                "metadata": {"chapter": "chapter17", "formula_references": [], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:17.4]]"}],
            },
        )
        write_json(structured / "formula_library.json", {"formulas": []})
        write_json(structured / "table_library.json", {"tables": []})
        write_json(
            structured / "example_library.json",
            {
                "schema": "example_library.v1",
                "example_count": 1,
                "examples": [
                    {
                        "example_id": "17.4",
                        "chapter": "chapter17",
                        "content_markdown": (
                            "Example 17.4. The worked example starts here. "
                            "The example body ends with a complete sentence. "
                            "Example 17.4 illustrates the fact that this is following discussion."
                        ),
                        "content_plain": (
                            "Example 17.4. The worked example starts here. "
                            "The example body ends with a complete sentence. "
                            "Example 17.4 illustrates the fact that this is following discussion."
                        ),
                        "metadata": {"needs_review": False},
                    }
                ],
            },
        )

        windows = collect_example_boundary_windows(
            structured,
            project_root=TEST_RUNTIME_ROOT,
            chapters=["chapter17"],
            max_windows=5,
        )

        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["end_raw_index"], 1)

    def test_guardrail_rejects_included_post_example_body(self):
        window = {
            "window_id": "chapter24:24.4:0-2",
            "expected_example_id": "24.4",
            "rows": [
                {"raw_row_index": 0, "label": "text", "content": "Example 24.4. Starts here."},
                {"raw_row_index": 1, "label": "text", "content": "Body text."},
                {
                    "raw_row_index": 2,
                    "label": "text",
                    "content": "As Example 24.4 illustrates, this belongs to the following discussion.",
                },
            ],
        }
        decision = {
            "example_id": "24.4",
            "start_row_index": 0,
            "end_row_index": 2,
            "include_table_rows": [],
            "include_formula_rows": [],
            "is_complete": True,
            "confidence": 0.99,
            "apply_mode": "auto",
        }

        validation = validate_llm_example_decision(window, decision)

        self.assertEqual(validation["status"], "rejected")
        self.assertIn("includes_post_example_body", validation["errors"])

    def test_candidate_can_shrink_author_year_contamination(self):
        rows = [
            _raw_row("text", "Example 24.12. The example starts here.", top=10),
            _raw_row("display_formula", "$$ x=y $$", top=40),
            _raw_row("formula_number", "(24.33a)", top=70),
            _raw_row("text", "which recovers the known equation.", top=100),
            _raw_row("text", "Turelli and Barton (1994) examined the broader model.", top=130),
        ]
        _write_raw_project(TEST_RUNTIME_ROOT, "chapter24", rows)
        structured = TEST_RUNTIME_ROOT / "structured"
        structured.mkdir(parents=True, exist_ok=True)
        write_json(
            structured / "chapter24_001.json",
            {
                "id": "chapter24_001",
                "metadata": {"chapter": "chapter24", "formula_references": ["24.33a"], "table_references": []},
                "blocks": [{"type": "example", "content": "[[SEE_EXAMPLE:24.12]]"}],
            },
        )
        write_json(structured / "formula_library.json", {"formulas": [{"id": "24.33a", "source": {"chapter": "chapter24"}}]})
        write_json(structured / "table_library.json", {"tables": []})
        write_json(structured / "example_library.json", {"schema": "example_library.v1", "example_count": 0, "examples": []})

        windows = collect_example_boundary_windows(
            structured,
            project_root=TEST_RUNTIME_ROOT,
            chapters=["chapter24"],
            max_windows=5,
            suspicious_only=False,
        )
        candidate = build_example_candidate_from_decision(
            windows[0],
            {
                "example_id": "24.12",
                "start_row_index": 0,
                "end_row_index": 3,
                "include_table_rows": [],
                "include_formula_rows": [1, 2],
                "is_complete": True,
                "confidence": 0.95,
                "reason": "stop before literature paragraph",
                "apply_mode": "auto",
            },
            structured_dir=structured,
        )

        self.assertIn("[[SEE_FORMULA:24.33a]]", candidate.content_markdown)
        self.assertNotIn("Turelli and Barton", candidate.content_markdown)


if __name__ == "__main__":
    unittest.main()
