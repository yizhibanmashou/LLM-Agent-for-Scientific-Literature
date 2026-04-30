import unittest

import pytest

pytest.importorskip(
    "knowledge_engineering.src.processors.semantic_cleaner",
    reason="legacy knowledge_engineering.src package is not present in the simplified pipeline",
)
from knowledge_engineering.src.processors.content_protector import ContentValidator
from knowledge_engineering.src.processors.semantic_cleaner import (
    EFFECTIVE_CLEANER_INPUT_CHARS,
    _split_long_text,
    clean_page,
)


class _EchoCleanerClient:
    def __init__(self):
        self.segment_inputs = []

    def call(self, prompt, max_retries=None, expect_json=True):
        marker = "Text:\n"
        self.assert_prompt(prompt)
        segment = prompt.split(marker, 1)[1]
        self.segment_inputs.append(segment)
        return {"cleaned_text": segment}

    @staticmethod
    def assert_prompt(prompt):
        if "Text:\n" not in prompt:
            raise AssertionError("Cleaner prompt missing text marker")


class _SoftWarningCleanerClient:
    def call(self, prompt, max_retries=None, expect_json=True):
        marker = "Text:\n"
        if marker not in prompt:
            raise AssertionError("Cleaner prompt missing text marker")
        segment = prompt.split(marker, 1)[1]
        cleaned = segment.replace("mutation-selection", "selection", 1)
        return {"cleaned_text": cleaned}


class _OverDeletingCleanerClient:
    def call(self, prompt, max_retries=None, expect_json=True):
        return {"cleaned_text": "short summary"}


class TestSemanticCleaner(unittest.TestCase):
    def test_split_long_text_hard_splits_dense_input(self):
        text = ("dense scientific prose without blank lines but with spaces " * 250).strip()

        segments = _split_long_text(text, max_chars=500)

        self.assertGreater(len(segments), 1)
        self.assertEqual("".join(segments), text)
        self.assertTrue(all(len(segment) <= 500 for segment in segments))

    def test_clean_page_processes_all_segments_for_oversized_input(self):
        client = _EchoCleanerClient()
        text = ("This is a long sentence in a dense OCR paragraph. " * 1500).strip()

        cleaned = clean_page(text, client)

        self.assertEqual(cleaned, text)
        self.assertGreater(len(client.segment_inputs), 1)
        self.assertTrue(
            all(len(segment) <= EFFECTIVE_CLEANER_INPUT_CHARS for segment in client.segment_inputs)
        )

    def test_validator_allows_header_term_removal_as_soft_warning(self):
        original = (
            "CHAPTER I\n"
            "PREFACE\n"
            "This section discusses selection in natural populations and keeps the full paragraph intact. "
            "The same paragraph continues with enough content to dominate the removed heading noise."
        )
        cleaned = (
            "This section discusses selection in natural populations and keeps the full paragraph intact. "
            "The same paragraph continues with enough content to dominate the removed heading noise."
        )

        validation = ContentValidator.validate_cleaning(original, cleaned)

        self.assertTrue(validation["valid"])
        self.assertEqual(validation["critical_warnings"], [])
        self.assertGreaterEqual(validation["stats"]["retention_ratio"], 0.72)

    def test_clean_page_rejects_domain_term_soft_warning_cleaning(self):
        client = _SoftWarningCleanerClient()
        text = (
            "This section discusses the mutation-selection balance in natural populations and keeps the full "
            "paragraph intact. The same paragraph continues with enough content to dominate the removed term."
        )

        cleaned = clean_page(text, client)

        self.assertEqual(cleaned, text)

    def test_clean_page_preserves_paragraph_breaks_via_protection(self):
        client = _EchoCleanerClient()
        text = "Paragraph one with formulas nearby.\n\nParagraph two should remain separated."

        cleaned = clean_page(text, client)

        self.assertEqual(cleaned, text)
        self.assertIn("\n\n", cleaned)

    def test_clean_page_still_rejects_over_deletion(self):
        client = _OverDeletingCleanerClient()
        text = (
            "This paragraph contains a detailed explanation of the mutation-selection balance and should not be "
            "collapsed into a tiny summary by the cleaner."
        )

        cleaned = clean_page(text, client)

        self.assertEqual(cleaned, text)


if __name__ == "__main__":
    unittest.main()
