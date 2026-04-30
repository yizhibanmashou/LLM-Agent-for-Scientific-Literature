import unittest

import pytest

pytest.importorskip(
    "knowledge_engineering.src.processors.ocr_layout_normalizer",
    reason="legacy knowledge_engineering.src package is not present in the simplified pipeline",
)
from knowledge_engineering.src.processors.ocr_layout_normalizer import normalize_ocr_pages


class OCRLayoutNormalizerTests(unittest.TestCase):
    def test_preserves_table_caption_but_drops_table_body(self):
        pages = [
            [
                {
                    "index": 0,
                    "label": "text",
                    "content": '<div align="center">\n\nTable 6.1 General expressions for selection response.\n\n</div>',
                },
                {
                    "index": 1,
                    "label": "table",
                    "content": "<table><tr><td>a</td></tr></table>",
                },
            ]
        ]

        normalized, stats = normalize_ocr_pages(pages)

        self.assertEqual(len(normalized[0]), 1)
        self.assertEqual(normalized[0][0]["label"], "text")
        self.assertIn("Table 6.1", normalized[0][0]["content"])
        self.assertEqual(stats["kept"]["table_caption"], 1)
        self.assertEqual(stats["removed"]["table_body"], 1)

    def test_drops_publisher_line(self):
        pages = [
            [
                {
                    "index": 0,
                    "label": "text",
                    "content": (
                        "Evolution and Selection of Quantitative Traits. "
                        "Bruce Walsh & Michael Lynch. Published 2018 by Oxford University Press. "
                        "DOI 10.1093/test"
                    ),
                }
            ]
        ]

        normalized, stats = normalize_ocr_pages(pages)

        self.assertEqual(normalized[0], [])
        self.assertEqual(stats["removed"]["publisher"], 1)

    def test_promotes_all_caps_heading(self):
        pages = [[{"index": 0, "label": "text", "content": "PRICE'S GENERAL THEOREM OF SELECTION"}]]

        normalized, _ = normalize_ocr_pages(pages)

        self.assertEqual(normalized[0][0]["content"], "## PRICE'S GENERAL THEOREM OF SELECTION")


if __name__ == "__main__":
    unittest.main()
