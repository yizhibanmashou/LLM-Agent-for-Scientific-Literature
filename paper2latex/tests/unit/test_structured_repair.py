import json
import unittest
from pathlib import Path
from uuid import uuid4

from knowledge_engineering.processors.structured_repair import (
    apply_repair_patch,
    build_repair_patch,
    load_glm_chapter,
    transfer_structural_placeholders,
    triage_patch_with_llm,
    verify_patch_with_llm,
)

TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "structured_repair"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class StructuredRepairTests(unittest.TestCase):
    def test_glm_json_index_preserves_order_and_source_locator(self):
        tmp = make_test_workspace("glm_json_index")
        glm_dir = tmp / "glm"
        write_json(
            glm_dir / "chapter6.json",
            [
                [
                    {"index": 0, "label": "header", "content": "CHAPTER 6"},
                    {
                        "index": 1,
                        "label": "text",
                        "content": "The first useful paragraph mentions Price's theorem.",
                        "bbox_2d": [1, 2, 3, 4],
                    },
                ],
                [
                    {
                        "index": 2,
                        "label": "text",
                        "content": "The second useful paragraph discusses selection response.",
                        "bbox_2d": [5, 6, 7, 8],
                    }
                ],
            ],
        )

        spans = load_glm_chapter(glm_dir, "chapter6", max_window=2)

        self.assertGreaterEqual(len(spans), 3)
        self.assertEqual(spans[0].paragraphs[0].page_index, 0)
        self.assertEqual(spans[0].paragraphs[0].block_index, 1)
        self.assertEqual(spans[0].paragraphs[0].bbox, [1, 2, 3, 4])
        self.assertIn("The first useful paragraph", spans[0].text)
        self.assertIn("The second useful paragraph", spans[1].text)

    def test_patch_uses_glm_text_and_preserves_table_placeholder(self):
        root = make_test_workspace("patch_glm_text")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        old_content = (
            "This damaged paragraph [h] is summarized in [[SEE_TABLE:6.1]] "
            "with cross-generational change $ (S + E[w _z]) $."
        )
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {
                    "chapter": "chapter6",
                    "section": "Introduction",
                    "subsections": ["Introduction"],
                    "source_file": "main.tex",
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": [],
                    "table_references": ["6.1"],
                },
                "blocks": [{"type": "discussion", "content": old_content}],
            },
        )
        write_json(
            glm_dir / "chapter6.json",
            [
                [
                    {
                        "index": 0,
                        "label": "text",
                        "content": (
                            "This damaged paragraph is summarized in Table 6.1 "
                            "with cross-generational change $ (S + E[w\\delta_z]) $."
                        ),
                    }
                ]
            ],
        )

        patch = build_repair_patch(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            audit_dir=None,
            max_window_paragraphs=1,
        )

        self.assertEqual(patch["metadata"]["item_count"], 1)
        item = patch["items"][0]
        self.assertEqual(item["unit_id"], "chapter6_001")
        self.assertEqual(item["block_index"], 0)
        self.assertEqual(item["status"], "accepted")
        self.assertEqual(item["action"], "auto_apply")
        self.assertIn("[[SEE_TABLE:6.1]]", item["new_content"])
        self.assertIn("\\delta_z", item["new_content"])
        self.assertNotIn("[h]", item["new_content"])

    def test_short_math_heavy_block_can_still_be_repaired(self):
        root = make_test_workspace("short_math_repair")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        old_content = "Price's Theorem, $ R_ z = (w_ i, z_ i) + E(w_ i _ i) $."
        write_json(
            structured_dir / "chapter6_003.json",
            {
                "id": "chapter6_003",
                "metadata": {
                    "chapter": "chapter6",
                    "section": "The Life and Times of George Price",
                    "subsections": ["The Life and Times of George Price"],
                    "source_file": "main.tex",
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": [],
                    "table_references": [],
                },
                "blocks": [{"type": "proposition", "content": old_content}],
            },
        )
        write_json(
            glm_dir / "chapter6.json",
            [
                [
                    {
                        "index": 0,
                        "label": "text",
                        "content": "Price's Theorem, $R_{z} = \\sigma(w_{i}, z_{i}) + E(w_{i} \\bar{\\delta}_{i})$.",
                    }
                ]
            ],
        )

        patch = build_repair_patch(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            audit_dir=None,
            max_window_paragraphs=1,
        )

        item = patch["items"][0]
        self.assertIn(item["status"], {"accepted", "needs_review"})
        self.assertNotEqual(item["new_content"], old_content)
        self.assertIn("\\sigma", item["candidate_content"])
        self.assertIn("\\bar{\\delta}", item["candidate_content"])

    def test_placeholder_heavy_truncated_candidate_enters_review(self):
        root = make_test_workspace("placeholder_truncated")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        old_content = (
            "Now consider the transmission phase (which more generally includes everything other than selection). "
            "Let $ _ i $ denote the mean value of the descendants from category i, which we can decompose as "
            "[[SEE_FORMULA:6.3a]] namely, the mean value, $ z_ i $, of their ancestors plus a deviation, $ _ i $, "
            "due to imperfect transmission. Taking the average over all ancestral categories, the average trait "
            "value over all the descendants becomes [[SEE_FORMULA:6.3b]]"
        )
        write_json(
            structured_dir / "chapter6_003.json",
            {
                "id": "chapter6_003",
                "metadata": {
                    "chapter": "chapter6",
                    "section": "The Life and Times of George Price",
                    "subsections": ["The Life and Times of George Price"],
                    "source_file": "main.tex",
                    "source_title": "Evolution and Selection of Quantitative Traits",
                    "formula_references": ["formula_6.3a", "formula_6.3b"],
                    "table_references": [],
                },
                "blocks": [{"type": "derivation", "content": old_content}],
            },
        )
        write_json(
            glm_dir / "chapter6.json",
            [
                [
                    {
                        "index": 0,
                        "label": "text",
                        "content": (
                            "Now consider the transmission phase (which more generally includes everything other "
                            "than selection). Let $ \\overline{z}_{i} $ denote the mean value of the descendants "
                            "from category i, which we can decompose as"
                        ),
                    }
                ]
            ],
        )

        patch = build_repair_patch(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            audit_dir=None,
            max_window_paragraphs=1,
        )

        item = patch["items"][0]
        self.assertEqual(item["status"], "needs_review")
        self.assertEqual(item["action"], "review")
        self.assertIn("[[SEE_FORMULA:6.3a]]", item["new_content"])
        self.assertIn("[[SEE_FORMULA:6.3b]]", item["new_content"])
        self.assertIn("as [[SEE_FORMULA:6.3a]]", item["new_content"])
        self.assertIn("\\overline{z}", item["new_content"])

    def test_transfer_structural_placeholders_recovers_placeholder_by_context(self):
        old_content = (
            "Messer and Petrov (2013b) suggested that one simple solution is to estimate "
            "[[SEE_FORMULA:10.9d]] using different cutoff levels."
        )
        new_content = (
            "Messer and Petrov (2013b) suggested that one simple solution is to estimate "
            "\\overline{\\alpha} using different cutoff levels."
        )

        repaired = transfer_structural_placeholders(old_content, new_content)

        self.assertIn("[[SEE_FORMULA:10.9d]]", repaired)
        self.assertNotIn("\\overline{\\alpha}", repaired)

    def test_low_similarity_match_is_rejected(self):
        root = make_test_workspace("low_similarity")
        structured_dir = root / "structured"
        glm_dir = root / "glm"
        old_content = "The selection response [h] is driven by covariance and transmission terms."
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {"chapter": "chapter6", "section": "Intro", "subsections": []},
                "blocks": [{"type": "discussion", "content": old_content}],
            },
        )
        write_json(
            glm_dir / "chapter6.json",
            [[{"index": 0, "label": "text", "content": "A short unrelated paragraph about numerical recipes."}]],
        )

        patch = build_repair_patch(
            structured_dir=structured_dir,
            glmocr_dir=glm_dir,
            audit_dir=None,
            max_window_paragraphs=1,
        )

        self.assertEqual(patch["metadata"]["item_count"], 1)
        item = patch["items"][0]
        self.assertEqual(item["status"], "rejected")
        self.assertEqual(item["action"], "no_apply")
        self.assertEqual(item["new_content"], old_content)

    def test_apply_patch_changes_only_auto_items_and_leaves_libraries(self):
        structured_dir = make_test_workspace("apply_patch") / "structured"
        write_json(
            structured_dir / "chapter6_001.json",
            {
                "id": "chapter6_001",
                "metadata": {"chapter": "chapter6", "section": "Intro", "subsections": []},
                "blocks": [
                    {"type": "discussion", "content": "old auto"},
                    {"type": "discussion", "content": "old review"},
                ],
            },
        )
        formula_payload = {"metadata": {"total_formulas": 1}, "formulas": [{"id": "formula_6.1"}]}
        table_payload = {"metadata": {"total_tables": 1}, "tables": [{"id": "6.1"}]}
        write_json(structured_dir / "formula_library.json", formula_payload)
        write_json(structured_dir / "table_library.json", table_payload)
        patch = {
            "metadata": {},
            "items": [
                {
                    "unit_id": "chapter6_001",
                    "block_index": 0,
                    "old_content": "old auto",
                    "new_content": "new auto",
                    "action": "auto_apply",
                },
                {
                    "unit_id": "chapter6_001",
                    "block_index": 1,
                    "old_content": "old review",
                    "new_content": "new review",
                    "action": "review",
                },
            ],
        }

        result = apply_repair_patch(patch, structured_dir)

        data = json.loads((structured_dir / "chapter6_001.json").read_text(encoding="utf-8"))
        self.assertEqual(result["applied"], 1)
        self.assertEqual(data["blocks"][0]["content"], "new auto")
        self.assertEqual(data["blocks"][1]["content"], "old review")
        self.assertEqual(
            json.loads((structured_dir / "formula_library.json").read_text(encoding="utf-8")),
            formula_payload,
        )
        self.assertEqual(
            json.loads((structured_dir / "table_library.json").read_text(encoding="utf-8")),
            table_payload,
        )

    def test_verify_patch_with_llm_promotes_review_acceptance(self):
        class MockVerifier:
            def _post_chat_completion(self, *, messages, json_mode=False):
                return json.dumps({"decision": "accept", "reason": "candidate preserves meaning"})

        patch = {
            "metadata": {"status_counts": {"needs_review": 1}, "action_counts": {"review": 1}},
            "items": [
                {
                    "unit_id": "chapter6_001",
                    "block_index": 0,
                    "issue_codes": ["placeholder_leak"],
                    "old_content": "Old text [h]",
                    "new_content": "Old text",
                    "action": "review",
                    "status": "needs_review",
                    "confidence": 0.82,
                    "reasons": [],
                }
            ],
        }

        verified = verify_patch_with_llm(patch, MockVerifier(), llm_scope="review", llm_limit=1)

        item = verified["items"][0]
        self.assertEqual(item["status"], "accepted")
        self.assertEqual(item["action"], "auto_apply")
        self.assertEqual(verified["metadata"]["llm_verified"], 1)
        self.assertEqual(verified["metadata"]["status_counts"]["accepted"], 1)

    def test_triage_patch_with_llm_labels_rejected_without_promoting(self):
        class MockTriage:
            def _post_chat_completion(self, *, messages, json_mode=False):
                payload = json.loads(messages[-1]["content"])
                return json.dumps(
                    {
                        "decisions": [
                            {
                                "id": payload["items"][0]["id"],
                                "label": "inline_math_candidate",
                                "next_action": "send_to_second_pass",
                                "reason": "inline math needs a specialized pass",
                            }
                        ]
                    }
                )

        patch = {
            "metadata": {"status_counts": {"rejected": 1}, "action_counts": {"no_apply": 1}},
            "items": [
                {
                    "unit_id": "chapter6_001",
                    "block_index": 0,
                    "issue_codes": ["spaced_script_math"],
                    "old_content": "Damaged $ E[w _z] $ text",
                    "new_content": "Damaged $ E[w _z] $ text",
                    "action": "no_apply",
                    "status": "rejected",
                    "confidence": 0.0,
                    "match_score": 0.7,
                    "reasons": ["match_score 0.70 below review threshold 0.75"],
                }
            ],
        }

        triaged = triage_patch_with_llm(patch, MockTriage(), llm_batch_size=4)

        item = triaged["items"][0]
        self.assertEqual(item["status"], "rejected")
        self.assertEqual(item["action"], "no_apply")
        self.assertEqual(item["llm_triage"]["label"], "inline_math_candidate")
        self.assertEqual(item["llm_triage"]["next_action"], "send_to_second_pass")
        self.assertEqual(triaged["metadata"]["llm_triaged"], 1)
        self.assertEqual(triaged["metadata"]["llm_triage_counts"]["inline_math_candidate"], 1)


if __name__ == "__main__":
    unittest.main()
