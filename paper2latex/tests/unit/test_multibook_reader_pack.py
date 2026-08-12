import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.build_study_reader_assets import resolve_textbook_asset, validate_table_html
from scripts.package_book_delivery import (
    parse_numbers,
    release_provenance,
    selected_sections,
    source_snapshot,
    source_snapshot_matches,
)
from scripts.verify_project import tree_digest
from textbook_exporter import export_textbooks

ROOT = Path(__file__).resolve().parents[3]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class MultiBookReaderPackTests(unittest.TestCase):
    def test_multibook_export_uses_each_books_dedicated_table_library(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as raw:
            root = Path(raw)
            structured = root / "structured"
            out = root / "out"
            for book, title in (("Evolution", "Evolution-only table"), ("Genetics", "Genetics-only table")):
                chapter = f"{book}_chapter1"
                write_json(
                    structured / f"{chapter}_001.json",
                    {
                        "id": f"{chapter}_001",
                        "metadata": {"chapter": chapter, "display_heading": "Test"},
                        "blocks": [{"type": "discussion", "content": "[[TABLE:1.1]]"}],
                    },
                )
                write_json(structured / f"{book}_formula_library.json", {"formulas": []})
                write_json(structured / f"{book}_figure_library.json", {"figures": []})
                write_json(
                    structured / f"{book}_table_library.json",
                    {
                        "tables": [{
                            "id": "1.1", "title": title, "rows": [["A"], [book]],
                            "source": {"chapter": chapter, "unit_id": f"{chapter}_001"},
                        }]
                    },
                )
            write_json(structured / "example_library.json", {"examples": []})

            results = export_textbooks(structured, out, books=["Evolution", "Genetics"])

            self.assertEqual({result.chapter for result in results}, {"Evolution_chapter1", "Genetics_chapter1"})
            evolution = (out / "Evolution_chapter1_textbook.md").read_text(encoding="utf-8")
            genetics = (out / "Genetics_chapter1_textbook.md").read_text(encoding="utf-8")
            self.assertIn("Evolution-only table", evolution)
            self.assertNotIn("Genetics-only table", evolution)
            self.assertIn("Genetics-only table", genetics)
            self.assertNotIn("Evolution-only table", genetics)

    def test_catalog_is_lightweight_and_all_chapters_are_split(self):
        catalog_path = ROOT / "study_reader/data/generated/study_dataset.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        self.assertEqual(catalog.get("data_mode"), "split")
        self.assertNotIn("data", catalog)
        self.assertLess(catalog_path.stat().st_size, 100_000)
        self.assertEqual(len(catalog.get("chapters", [])), 68)
        self.assertEqual({book["id"] for book in catalog.get("books", [])}, {"Evolution", "Genetics", "PopGen"})
        for chapter in catalog["chapters"]:
            self.assertTrue((ROOT / "study_reader/data/generated/chapters" / f"{chapter['id']}.json").is_file())

    def test_asset_resolution_allows_data_figures_but_rejects_escape(self):
        markdown = ROOT / "data/textbook/PopGen_chapter2_textbook.md"
        source, packaged = resolve_textbook_asset(markdown, "../figures/PopGen_2.1.png")
        self.assertTrue(source.is_file())
        self.assertEqual(packaged.as_posix(), "data/figures/PopGen_2.1.png")
        with self.assertRaises(ValueError):
            resolve_textbook_asset(markdown, "../../../outside.png")

    def test_pack_range_parser(self):
        self.assertEqual(parse_numbers("3-5,8,5"), [3, 4, 5, 8])
        self.assertEqual(selected_sections("Genetics", "3-5,8", "1"), ["chapter3", "chapter4", "chapter5", "chapter8", "appendix1"])

    def test_release_pack_rejects_waiver_and_accepts_automatic_validity(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as raw:
            report = Path(raw) / "installation.json"
            write_json(report, {"installed": True, "automated_valid": False, "automatic_findings_waived": True})
            with self.assertRaises(ValueError):
                release_provenance(report)
            write_json(report, {"installed": True, "automated_valid": True, "automatic_findings_waived": False})
            provenance = release_provenance(report)
            self.assertEqual(provenance["status"], "automatic_valid")

    def test_pack_source_fingerprint_detects_stale_formal_data(self):
        current = {"schema": "formal_data_source.v1", "sha256": "current"}
        self.assertTrue(source_snapshot_matches(current, dict(current)))
        self.assertFalse(source_snapshot_matches({"schema": "formal_data_source.v1", "sha256": "old"}, current))
        self.assertFalse(source_snapshot_matches({}, current))

    def test_source_snapshot_changes_when_a_formal_input_changes(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as raw:
            data = Path(raw) / "data"
            structured = data / "structured"
            textbook = data / "textbook"
            structured.mkdir(parents=True)
            textbook.mkdir(parents=True)
            write_json(structured / "Book_chapter1_001.json", {"id": "Book_chapter1_001", "blocks": [{"content": "before"}]})
            (textbook / "Book_chapter1_textbook.md").write_text("before", encoding="utf-8")
            for kind in ("formula", "table", "figure", "example"):
                write_json(structured / f"Book_{kind}_library.json", {f"{kind}s" if kind != "example" else "examples": []})
            before = source_snapshot("Book", ["chapter1"], data_root=data)
            write_json(structured / "Book_chapter1_001.json", {"id": "Book_chapter1_001", "blocks": [{"content": "after"}]})
            after = source_snapshot("Book", ["chapter1"], data_root=data)
            self.assertFalse(source_snapshot_matches(before, after))

    def test_table_html_allowlist_rejects_scripts_events_and_urls(self):
        self.assertEqual(validate_table_html("<table><tr><td>safe</td></tr></table>"), [])
        errors = validate_table_html('<table onclick="x()"><tr><td><script>x()</script></td></tr></table>')
        self.assertTrue(any("attribute" in error for error in errors))
        self.assertTrue(any("tag" in error for error in errors))

    def test_tree_digest_is_stable_and_detects_generated_file_drift(self):
        with TemporaryDirectory(dir=ROOT / "tmp") as raw:
            root = Path(raw)
            (root / "nested").mkdir()
            (root / "a.json").write_text('{"a":1}\n', encoding="utf-8")
            (root / "nested" / "b.json").write_text('{"b":2}\n', encoding="utf-8")
            first = tree_digest(root)
            self.assertEqual(tree_digest(root), first)
            (root / "nested" / "b.json").write_text('{"b":3}\n', encoding="utf-8")
            self.assertNotEqual(tree_digest(root), first)


if __name__ == "__main__":
    unittest.main()
