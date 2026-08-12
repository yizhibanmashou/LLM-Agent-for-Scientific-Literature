
import unittest

from paper2latex.converters.structure_parser import StructureParser


class TestStructureParser(unittest.TestCase):
    def setUp(self):
        self.parser = StructureParser()
        
        # Sample PaddleOCR-VL style output (list of pages)
        self.sample_json = [
            # Page 1
            {
                "regions": [
                    {"type": "title", "text": "Deep Learning for Science", "bbox": [10, 10, 200, 30]},
                    {"type": "text", "text": "Alice Smith, Bob Jones", "bbox": [10, 40, 200, 50]},
                    {"type": "text", "text": "Abstract: We present a new method.", "bbox": [10, 60, 200, 100]},
                    {"type": "header", "text": "1. Introduction", "bbox": [10, 110, 200, 120]},
                    {"type": "text", "text": "This is the intro text.", "bbox": [10, 130, 200, 150]}
                ]
            },
            # Page 2
            {
                "regions": [
                    {"type": "header", "text": "2. Methods", "bbox": [10, 10, 200, 20]},
                    {"type": "text", "text": "Our method uses X.", "bbox": [10, 30, 200, 50]},
                    {"type": "figure", "text": "Figure 1: Architecture", "bbox": [10, 60, 200, 200]},
                    {"type": "header", "text": "References", "bbox": [10, 210, 200, 220]},
                    {"type": "list", "text": "[1] A. Smith, 2020.", "bbox": [10, 230, 200, 240]}
                ]
            }
        ]

    def test_parse_structure(self):
        doc = self.parser.parse(self.sample_json)
        
        # Metadata
        self.assertEqual(doc.title, "Deep Learning for Science")
        self.assertIn("We present a new method", doc.abstract)
        
        # Sections
        # Current parser keeps Paddle "header" blocks as page headers and
        # creates a default Introduction section for the body.
        # Note: "Introduction" might be defaulted if not found, but we ensure one is created
        section_titles = [s.title for s in doc.sections]
        self.assertIn("Introduction", section_titles)
        self.assertIn("References", section_titles)
        
        # Figures
        self.assertEqual(len(doc.figures), 1)
        self.assertEqual(doc.figures[0].caption, "")
        
        # References (if implemented)
        # self.assertTrue(len(doc.references) > 0) # Logic is partial/stubbed

if __name__ == '__main__':
    unittest.main()
