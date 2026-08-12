import json
import unittest
from pathlib import Path
from uuid import uuid4

from knowledge_engineering.processors.latex_overlay_repair import (
    apply_overlay_patch,
    build_overlay_patch,
)

TEST_RUNTIME_ROOT = Path(__file__).resolve().parents[3] / "tmp" / "test_runtime" / "latex_overlay_repair"
TEST_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)


def make_test_workspace(prefix: str) -> Path:
    workspace = TEST_RUNTIME_ROOT / f"{prefix}_{uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LatexOverlayRepairTests(unittest.TestCase):
    def test_overlay_repairs_inline_math_only_and_preserves_prose(self):
        root = make_test_workspace("inline_overlay")
        structured_dir = root / "structured"
        source_dir = root / "fresh"
        old_content = (
            "For $z = (x - _x)^2$ and $z = (x - _x)^4$, weights $ n_ i $ and $ W_ i $ "
            "define $ w_ i = W_ i / $. [[SEE_FORMULA:6.3a]] The transformed term is $ q_ i ^ $."
        )
        source_content = (
            "For $z = (x - \\mu_x)^2$ and $z = (x - \\mu_x)^4$, weights $ n_{i} $ and $ W_{i} $ "
            "define $ w_{i} = W_{i}/\\overline{W} $. [[SEE_FORMULA:6.3a]] "
            "The transformed term is $ q_{i}^{\\prime} $."
        )
        payload = {
            "id": "chapter6_003",
            "metadata": {"chapter": "chapter6", "section": "Price", "subsections": ["Price"]},
            "blocks": [{"type": "derivation", "content": old_content}],
        }
        write_json(structured_dir / "chapter6_003.json", payload)
        write_json(
            source_dir / "chapter6_003.json",
            {**payload, "blocks": [{"type": "derivation", "content": source_content}]},
        )

        patch = build_overlay_patch(structured_dir=structured_dir, source_dir=source_dir)

        self.assertEqual(patch["metadata"]["item_count"], 1)
        item = patch["items"][0]
        self.assertEqual(item["status"], "accepted")
        self.assertEqual(item["action"], "auto_apply")
        self.assertEqual(len(item["replacements"]), 6)
        self.assertIn("[[SEE_FORMULA:6.3a]]", item["new_content"])
        self.assertIn("For ", item["new_content"])
        self.assertIn("\\mu_x", item["new_content"])
        self.assertIn("W_{i}/\\overline{W}", item["new_content"])
        self.assertIn("q_{i}^{\\prime}", item["new_content"])
        self.assertNotIn("W_ i /", item["new_content"])

        result = apply_overlay_patch(patch, structured_dir)
        repaired = read_json(structured_dir / "chapter6_003.json")["blocks"][0]["content"]
        self.assertEqual(result["applied"], 1)
        self.assertEqual(repaired, item["new_content"])
        self.assertIn("[[SEE_FORMULA:6.3a]]", repaired)

    def test_placeholder_mismatch_is_reported_but_not_auto_applied(self):
        root = make_test_workspace("placeholder_mismatch")
        structured_dir = root / "structured"
        source_dir = root / "fresh"
        old_content = "Let $ _ i $ denote descendants as [[SEE_FORMULA:6.3a]] in the original chunk."
        source_content = "Let $ \\overline{z}_{i} $ denote descendants as Equation 6.3a in the fresh chunk."
        payload = {
            "id": "chapter6_003",
            "metadata": {"chapter": "chapter6", "section": "Price", "subsections": ["Price"]},
            "blocks": [{"type": "derivation", "content": old_content}],
        }
        write_json(structured_dir / "chapter6_003.json", payload)
        write_json(
            source_dir / "chapter6_003.json",
            {**payload, "blocks": [{"type": "derivation", "content": source_content}]},
        )

        patch = build_overlay_patch(structured_dir=structured_dir, source_dir=source_dir)

        self.assertEqual(patch["metadata"]["item_count"], 1)
        item = patch["items"][0]
        self.assertEqual(item["status"], "rejected")
        self.assertEqual(item["action"], "no_apply")
        self.assertEqual(item["new_content"], old_content)
        self.assertTrue(any("placeholder" in reason for reason in item["reasons"]))

        result = apply_overlay_patch(patch, structured_dir)
        unchanged = read_json(structured_dir / "chapter6_003.json")["blocks"][0]["content"]
        self.assertEqual(result["applied"], 0)
        self.assertEqual(unchanged, old_content)

    def test_table_overlay_preserves_rows_and_html_shape(self):
        root = make_test_workspace("table_overlay")
        structured_dir = root / "structured"
        source_dir = root / "fresh"
        target_table = {
            "id": "6.1",
            "title": "Moments $ _x $",
            "html": "<table><tr><td>$ w_ i = W_ i / $</td><td>plain</td></tr></table>",
            "rows": [["$ w_ i = W_ i / $", "plain"]],
        }
        source_table = {
            "id": "6.1",
            "title": "Moments $ \\mu_x $",
            "html": "<table><tr><td>$ w_{i} = W_{i}/\\overline{W} $</td><td>plain</td></tr></table>",
            "rows": [["$ w_{i} = W_{i}/\\overline{W} $", "plain"]],
        }
        write_json(structured_dir / "table_library.json", {"tables": [target_table]})
        write_json(source_dir / "table_library.json", {"tables": [source_table]})

        patch = build_overlay_patch(structured_dir=structured_dir, source_dir=source_dir)

        self.assertEqual(patch["metadata"]["item_count"], 1)
        item = patch["items"][0]
        self.assertEqual(item["kind"], "table")
        self.assertEqual(item["action"], "auto_apply")
        self.assertEqual(item["new_entry"]["rows"][0][1], "plain")
        self.assertEqual(item["new_entry"]["html"].count("<td>"), 2)
        self.assertIn("\\overline{W}", item["new_entry"]["html"])

        result = apply_overlay_patch(patch, structured_dir)
        repaired = read_json(structured_dir / "table_library.json")["tables"][0]
        self.assertEqual(result["applied"], 1)
        self.assertEqual(repaired["rows"][0][1], "plain")
        self.assertEqual(repaired["html"].count("<td>"), 2)
        self.assertIn("\\mu_x", repaired["title"])

    def test_table_overlay_does_not_whole_replace_prose_cell(self):
        root = make_test_workspace("table_prose_guard")
        structured_dir = root / "structured"
        source_dir = root / "fresh"
        target_table = {
            "id": "6.2",
            "title": "unchanged",
            "html": "<table><tr><td>Mean _x estimate</td></tr></table>",
            "rows": [["Mean _x estimate"]],
        }
        source_table = {
            "id": "6.2",
            "title": "unchanged",
            "html": "<table><tr><td>Mean \\mu_x estimate</td></tr></table>",
            "rows": [["Mean \\mu_x estimate"]],
        }
        write_json(structured_dir / "table_library.json", {"tables": [target_table]})
        write_json(source_dir / "table_library.json", {"tables": [source_table]})

        patch = build_overlay_patch(structured_dir=structured_dir, source_dir=source_dir)

        self.assertEqual(patch["metadata"]["item_count"], 0)


if __name__ == "__main__":
    unittest.main()
