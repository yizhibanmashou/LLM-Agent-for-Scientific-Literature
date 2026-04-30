import unittest

import pytest

pytest.importorskip(
    "knowledge_engineering.src.models.formula",
    reason="legacy knowledge_engineering.src package is not present in the simplified pipeline",
)
from knowledge_engineering.src.models.formula import FormulaLibrary, OCRFormulaOccurrence


class FormulaAnchorAnalysisTests(unittest.TestCase):
    def test_explicit_result_label_wins_over_input_references(self):
        text = (
            "Using Equation 6.3a to combine the first two covariances in "
            "Equation 6.7b gives Equation 6.7c."
        )

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.7b")
        self.assertEqual(anchor["next_label"], "6.7c")
        self.assertEqual(anchor["source_hint"], "text_anchor_explicit_result")

    def test_multiple_input_equations_can_infer_next_result(self):
        text = (
            "Substituting Equations 6.5a and 6.5b into Equation 6.4 yields "
            "the more traditional form of the Price equation."
        )

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.5b")
        self.assertEqual(anchor["next_label"], "6.6")
        self.assertEqual(anchor["source_hint"], "text_anchor_multi_reference_result")

    def test_mixed_base_equations_advance_to_next_integer_result(self):
        text = (
            "Recalling Equations 6.1, 6.2b, and 6.3b, the response in trait "
            "value becomes"
        )

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.3b")
        self.assertEqual(anchor["next_label"], "6.4")
        self.assertEqual(anchor["source_hint"], "text_anchor_multi_reference_result")

    def test_single_back_reference_with_yields_does_not_force_increment(self):
        text = "Putting these results together into Equation 6.6 yields the response to selection."

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "")
        self.assertEqual(anchor["next_label"], "")

    def test_multiple_result_hint_does_not_force_single_next_label(self):
        text = (
            "The same logic leading to Equation 6.33f (Example 6.8) can be "
            "used to obtain two useful identities:"
        )

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.33f")
        self.assertEqual(anchor["next_label"], "")
        self.assertEqual(anchor["source_hint"], "text_anchor_current_only")

    def test_post_formula_current_reference_can_bind_previous_formula(self):
        text = "Equation 6.7c relates the selection response to the covariance between fitness and descendants."

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.7c")
        self.assertEqual(anchor["next_label"], "")
        self.assertEqual(anchor["source_hint"], "text_anchor_post_formula_current")

    def test_of_equation_reference_can_bind_previous_formula(self):
        text = "The middle two expressions of Equation 6.8 can be rewritten using the selection differential."

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.8")
        self.assertEqual(anchor["next_label"], "")
        self.assertEqual(anchor["source_hint"], "text_anchor_post_formula_current")

    def test_parenthesized_equation_reference_can_bind_previous_formula(self):
        text = (
            "Thus, the exact version of Fisher's theorem (Equation 6.21c) "
            "simply concerns the partial evolutionary response."
        )

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.21c")
        self.assertEqual(anchor["next_label"], "")
        self.assertEqual(anchor["source_hint"], "text_anchor_post_formula_current")

    def test_equation_becomes_can_anchor_local_sequence(self):
        text = "The average of Equation 6.14 becomes"

        anchor = FormulaLibrary._analyze_text_anchor(text)

        self.assertEqual(anchor["current_label"], "6.14")
        self.assertEqual(anchor["next_label"], "6.15")
        self.assertEqual(anchor["source_hint"], "text_anchor_self_transform")

    def test_intermediate_labels_can_fill_suffix_before_next_integer(self):
        labels = FormulaLibrary._infer_intermediate_labels("6.13b", "6.14", 1)
        self.assertEqual(labels, ["6.13c"])

    def test_intermediate_labels_can_expand_middle_family(self):
        labels = FormulaLibrary._infer_intermediate_labels("6.14", "6.16a", 4)
        self.assertEqual(labels, ["6.15a", "6.15b", "6.15c", "6.15d"])

    def test_intermediate_labels_can_fill_suffix_family_from_plain_number(self):
        labels = FormulaLibrary._infer_intermediate_labels("6.6", "6.7b", 1)
        self.assertEqual(labels, ["6.7a"])

    def test_subsection_universe_can_absorb_candidate_family(self):
        library = FormulaLibrary()
        occurrence = OCRFormulaOccurrence(
            order=0,
            page_index=0,
            block_index=0,
            latex="x=y",
            subsection="The Breeder's Equation",
            previous_text="",
            next_text="",
        )
        occurrence.candidates = [
            {"label": "6.13b", "score": 7, "source_hint": "text"},
            {"label": "6.13c", "score": 6, "source_hint": "text"},
        ]

        augmented = library._augment_subsection_label_universe_from_candidates(
            [occurrence],
            {"The Breeder's Equation": ["6.13a", "6.14", "6.16a"]},
            source_chapter="Chapter 6",
        )

        self.assertEqual(
            augmented["The Breeder's Equation"],
            ["6.13a", "6.13b", "6.13c", "6.14", "6.16a"],
        )

    def test_subsection_universe_propagation_uses_ordered_labels(self):
        library = FormulaLibrary()
        occurrences = [
            OCRFormulaOccurrence(0, 0, 0, "f1", "Life", "", ""),
            OCRFormulaOccurrence(1, 0, 1, "f2", "Life", "", ""),
            OCRFormulaOccurrence(2, 0, 2, "f3", "Life", "", ""),
        ]
        occurrences[2].label = "6.3a"
        occurrences[2].label_format = "Equation 6.3a"

        library._propagate_within_subsection_universe(
            occurrences,
            {"Life": ["6.1", "6.2a", "6.2b", "6.3a"]},
            "Chapter 6",
        )

        self.assertEqual(
            [occurrence.label for occurrence in occurrences],
            ["6.2a", "6.2b", "6.3a"],
        )

    def test_small_subsection_head_gap_can_bridge_from_previous_group(self):
        occurrences = [
            OCRFormulaOccurrence(0, 0, 0, "f0", "Intro", "", ""),
            OCRFormulaOccurrence(1, 0, 1, "f1", "Next", "", ""),
            OCRFormulaOccurrence(2, 0, 2, "f2", "Next", "", ""),
            OCRFormulaOccurrence(3, 0, 3, "f3", "Next", "", ""),
        ]
        occurrences[0].label = "6.10"
        occurrences[0].label_format = "Equation 6.10"
        occurrences[3].label = "6.13a"
        occurrences[3].label_format = "Equation 6.13a"

        FormulaLibrary._bridge_small_subsection_head_gaps(
            occurrences,
            source_chapter="Chapter 6",
        )

        self.assertEqual(
            [occurrence.label for occurrence in occurrences],
            ["6.10", "6.11", "6.12", "6.13a"],
        )


if __name__ == "__main__":
    unittest.main()
