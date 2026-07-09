import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PATH = PROJECT_ROOT / "tmp" / "structured_boundary_audit" / "audit_boundaries.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("structured_boundary_audit_for_tests", AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load audit_boundaries.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StructuredBoundaryAuditTests(unittest.TestCase):
    def test_chapter_scope_supports_filter_and_exclusion(self):
        audit = load_audit_module()
        audit.CHAPTER_FILTER = audit.parse_chapter_list("27,28")
        audit.CHAPTER_EXCLUDE = audit.parse_chapter_list("chapter28")

        try:
            self.assertTrue(audit.chapter_in_scope("chapter27"))
            self.assertFalse(audit.chapter_in_scope("chapter28"))
            self.assertFalse(audit.chapter_in_scope("chapter29"))
        finally:
            audit.CHAPTER_FILTER = None
            audit.CHAPTER_EXCLUDE = set()

    def test_pdf_rule_extended_examples_do_not_trigger_longer_than_raw_suspect(self):
        audit = load_audit_module()
        row = {
            "evidence": {
                "existing_library_repair": "raw_layout_pdf_rule_boundary_extension",
                "visual_stop_source": "pdf_rendered_horizontal_rule",
                "raw_layout_refresh": {
                    "evidence_codes": ["pdf_rendered_horizontal_rule_extends_example"],
                },
            }
        }

        self.assertTrue(audit.row_has_pdf_rule_extension(row))
        self.assertFalse(
            audit.example_longer_than_raw_suspect(
                visual=True,
                ratio=1.92,
                raw_tail_present=True,
                pdf_rule_extension=audit.row_has_pdf_rule_extension(row),
            )
        )

    def test_flags_example_body_duplicated_in_nearby_prose(self):
        audit = load_audit_module()
        repeated = (
            "An interesting analysis using this approach was provided by Eyre Walker for analytic "
            "tractability he assumed that the trait effect alpha of a mutation was related to its "
            "deleterious selection coefficient and that this relationship controlled the fraction "
            "of equilibrium additive genetic variance contributed by alleles at frequency x."
        )
        units = [
            (
                Path("chapter28_034.json"),
                {
                    "id": "chapter28_034",
                    "metadata": {"chapter": "chapter28", "display_heading": "HK model"},
                    "blocks": [{"type": "example", "content": "[[EXAMPLE:28.13]]"}],
                },
            ),
            (
                Path("chapter28_035.json"),
                {
                    "id": "chapter28_035",
                    "metadata": {"chapter": "chapter28", "display_heading": "HK model"},
                    "blocks": [{"type": "discussion", "content": repeated}],
                },
            ),
        ]
        rows = [
            {
                "example_id": "28.13",
                "example_ref": "28.13",
                "chapter": "chapter28",
                "source_file": "chapter28_034.json",
                "content_markdown": f"Example 28.13. {repeated}",
            }
        ]

        issues = []
        stats = audit.audit_example_body_duplicate_prose(issues, units, rows)

        self.assertEqual(stats["examples_checked"], 1)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "example_body_duplicate_in_prose")
        self.assertEqual(issues[0]["evidence"]["duplicate_unit_id"], "chapter28_035")

    def test_flags_example_heading_unit_but_not_bottomed_example_in_real_prose_unit(self):
        audit = load_audit_module()
        previous_body = (
            "The joint effects model keeps real prose before the worked example and explains "
            "why the equilibrium variance remains biologically plausible under moderate apparent selection."
        )
        bad_units = [
            (
                Path("chapter28_037.json"),
                {
                    "id": "chapter28_037",
                    "metadata": {"chapter": "chapter28", "display_heading": "Joint-effects Models"},
                    "blocks": [{"type": "discussion", "content": previous_body}],
                },
            ),
            (
                Path("chapter28_038.json"),
                {
                    "id": "chapter28_038",
                    "metadata": {
                        "chapter": "chapter28",
                        "display_heading": "Example 28.15. As an application of the joint-effects model",
                    },
                    "blocks": [{"type": "example", "content": "[[EXAMPLE:28.15]]"}],
                },
            ),
        ]
        rows = [
            {
                "example_id": "28.15",
                "example_ref": "28.15",
                "chapter": "chapter28",
                "source_file": "chapter28_038.json",
                "start_block_index": 0,
                "content_markdown": "Example 28.15. Thus, a reasonable amount of genetic variation is maintained.",
            }
        ]

        bad_issues = []
        bad_placements = audit.scan_current_placements(bad_units)
        audit.audit_example_section_ownership(bad_issues, bad_units, bad_placements, rows)

        self.assertEqual(len(bad_issues), 1)
        self.assertEqual(bad_issues[0]["code"], "example_section_owner_mismatch")
        self.assertEqual(bad_issues[0]["evidence"]["recommended_unit_id"], "chapter28_037")

        good_units = [
            (
                Path("chapter28_037.json"),
                {
                    "id": "chapter28_037",
                    "metadata": {"chapter": "chapter28", "display_heading": "Joint-effects Models"},
                    "blocks": [
                        {"type": "discussion", "content": previous_body},
                        {"type": "example", "content": "[[EXAMPLE:28.15]]"},
                    ],
                },
            )
        ]
        good_issues = []
        good_placements = audit.scan_current_placements(good_units)
        rows[0]["source_file"] = "chapter28_037.json"
        audit.audit_example_section_ownership(good_issues, good_units, good_placements, rows)

        self.assertEqual(good_issues, [])

    def test_flags_example_in_short_new_heading_chunk(self):
        audit = load_audit_module()
        units = [
            (
                Path("chapter12_010.json"),
                {
                    "id": "chapter12_010",
                    "metadata": {"chapter": "chapter12", "display_heading": "Migration and Selection"},
                    "blocks": [
                        {
                            "type": "discussion",
                            "content": (
                                "This real prose introduces the model and is the nearest preceding "
                                "subsection body that should own the worked example."
                            ),
                        }
                    ],
                },
            ),
            (
                Path("chapter12_011.json"),
                {
                    "id": "chapter12_011",
                    "metadata": {"chapter": "chapter12", "display_heading": "A New Heading"},
                    "blocks": [
                        {"type": "discussion", "content": "A short bridge phrase"},
                        {"type": "example", "content": "[[SEE_EXAMPLE:12.4]]"},
                    ],
                },
            ),
        ]
        rows = [
            {
                "example_id": "12.4",
                "example_ref": "12.4",
                "chapter": "chapter12",
                "source_file": "chapter12_011.json",
                "start_block_index": 1,
                "content_markdown": "Example 12.4. Short-heading placement should move backward.",
            }
        ]

        issues = []
        placements = audit.scan_current_placements(units)
        audit.audit_example_section_ownership(issues, units, placements, rows)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "example_section_owner_mismatch")
        self.assertEqual(issues[0]["evidence"]["recommended_unit_id"], "chapter12_010")
        self.assertEqual(issues[0]["evidence"]["reason"], "short_non_prose_heading_chunk")

    def test_caption_like_matches_ignores_ordinary_figure_references(self):
        audit = load_audit_module()
        content = (
            "These expressions approach 4N generations (Figure 2.2). "
            "As Figure 2.3 shows, the approximation is accurate. "
            "Figure 2.4 The expected absorption time under neutrality."
        )
        matches = audit.caption_like_matches(
            content,
            audit.FIGURE_CAPTION_TEXT_RE,
            library_text_by_id={"2.4": "The expected absorption time under neutrality."},
            known_ids={"2.2", "2.3", "2.4"},
        )

        self.assertEqual(matches, ["2.4"])

    def test_caption_like_matches_ignores_subject_figure_reference(self):
        audit = load_audit_module()
        content = (
            "To apply this approach, Tenesa et al. scored SNPs, and Figure 4.3a shows the "
            "result for a Utah population of European ancestry. "
            "Figure 4.3 Estimates of historical values of Ne using linkage disequilibrium."
        )
        matches = audit.caption_like_matches(
            content,
            audit.FIGURE_CAPTION_TEXT_RE,
            library_text_by_id={"4.3": "Estimates of historical values of Ne using linkage disequilibrium."},
            known_ids={"4.3", "4.3a"},
        )

        self.assertEqual(matches, ["4.3"])

    def test_figure_audit_does_not_recommend_forward_owner(self):
        audit = load_audit_module()
        self.assertTrue(audit.figure_recommendation_is_forward("chapter20_005", "chapter20_010"))
        self.assertFalse(audit.figure_recommendation_is_forward("chapter20_010", "chapter20_005"))
        self.assertFalse(audit.figure_recommendation_is_forward("", "chapter20_005"))

    def test_figure_anchor_tie_breaks_to_later_structured_unit(self):
        audit = load_audit_module()
        anchors = [
            {"chunk": "appendix5_006", "distance": 791.0, "score": 1.0},
            {"chunk": "appendix5_009", "distance": 791.0, "score": 1.0},
        ]

        best = sorted(anchors, key=audit.figure_anchor_sort_key)[0]

        self.assertEqual(best["chunk"], "appendix5_009")

    def test_formula_library_ids_accept_legacy_formula_prefix(self):
        audit = load_audit_module()
        ids = audit.load_library_ids(Path("missing.json"), "formulas")
        self.assertEqual(ids, set())

        original_load_json = audit.load_json
        audit.load_json = lambda _path, _default=None: {"formulas": [{"id": "formula_8.4d"}]}
        try:
            self.assertIn("8.4d", audit.load_library_ids(Path("formula_library.json"), "formulas"))
        finally:
            audit.load_json = original_load_json

    def test_formula_missing_audit_only_requires_current_chapter_numbered_formulas(self):
        audit = load_audit_module()

        self.assertFalse(audit.ref_belongs_to_chapter("0.3", "chapter2"))
        self.assertFalse(audit.ref_belongs_to_chapter("29.39d", "chapter26"))
        self.assertTrue(audit.ref_belongs_to_chapter("26.39d", "chapter26"))
        self.assertTrue(audit.ref_belongs_to_chapter("A6.1a", "appendix6"))

    def test_fragment_residue_flags_standalone_body_see_reference(self):
        audit = load_audit_module()
        units = [
            (
                Path("chapter28_001.json"),
                {
                    "id": "chapter28_001",
                    "metadata": {"chapter": "chapter28"},
                    "blocks": [
                        {"type": "discussion", "content": "Plain text cites [[SEE_EXAMPLE:28.1]]."},
                        {"type": "example", "content": "[[SEE_EXAMPLE:28.1]]"},
                    ],
                },
            )
        ]
        issues = []

        audit.audit_fragment_residue(issues, units)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["evidence"]["reason"], "standalone_body_uses_see_reference")

    def test_inline_tables_are_not_expanded_for_example_boundary_word_counts(self):
        audit = load_audit_module()
        large_table = " ".join(f"value{i}" for i in range(200))

        self.assertTrue(audit.inline_table_id("inline_1"))
        self.assertFalse(audit.inline_table_id("26.2"))
        self.assertEqual(
            audit.table_boundary_text("inline_1", {"inline_1": large_table}),
            "table inline_1",
        )
        self.assertEqual(audit.table_boundary_text("26.2", {"26.2": "numbered table"}), "numbered table")

    def test_table_audit_flags_body_row_residue_in_prose(self):
        audit = load_audit_module()
        units = [
            (
                Path("chapter16_006.json"),
                {
                    "id": "chapter16_006",
                    "metadata": {"chapter": "chapter16"},
                    "blocks": [
                        {
                            "type": "discussion",
                            "content": (
                                "If parental phenotypes are uncorrelated, Directional Truncation "
                                "Selection: Uppermost p saved $$ kappa=a $$"
                            ),
                        },
                        {"type": "table", "content": "[[TABLE:16.1]]"},
                    ],
                },
            )
        ]
        table_payload = {
            "tables": [
                {
                    "id": "16.1",
                    "table_type": "numbered",
                    "rows": [
                        ["Selection scheme", "Formula"],
                        ["Directional Truncation Selection: Uppermost p saved", "[[SEE_FORMULA:16.11a]]"],
                    ],
                    "source": {"chapter": "chapter16", "unit_id": "chapter16_006"},
                }
            ]
        }
        original_load_json = audit.load_json
        original_load_library_rows = audit.load_library_rows
        audit.load_json = lambda _path, _default=None: table_payload
        audit.load_library_rows = lambda _path, _key: [{"id": "16.11a", "latex": "kappa=a"}]
        try:
            issues = []
            placements = audit.scan_current_placements(units)
            audit.audit_tables(issues, units, placements, [])
        finally:
            audit.load_json = original_load_json
            audit.load_library_rows = original_load_library_rows

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "table_body_residue_in_prose")
        self.assertEqual(issues[0]["evidence"]["residue_unit_id"], "chapter16_006")

    def test_boundary_compare_text_distinguishes_references_from_object_bodies(self):
        audit = load_audit_module()
        large_table = " ".join(f"value{i}" for i in range(80))
        formula = r"x = y"

        reference_text = audit.example_boundary_compare_text(
            "See [[SEE_TABLE:9.1]] and [[SEE_FORMULA:9.22a]].",
            formula_latex_by_id={"9.22a": formula},
            figure_text_by_id={},
            figure_ids=set(),
            table_text_by_id={"9.1": large_table},
        )
        body_text = audit.example_boundary_compare_text(
            "[[TABLE:9.1]] [[FORMULA:9.22a]]",
            formula_latex_by_id={"9.22a": formula},
            figure_text_by_id={},
            figure_ids=set(),
            table_text_by_id={"9.1": large_table},
        )

        self.assertEqual(reference_text, "See Table 9.1 and Equation 9.22a.")
        self.assertIn("value79", body_text)
        self.assertIn("$$ x = y $$ (9.22a)", body_text)

    def test_visual_boundary_mismatch_ignores_placeholder_length_noise(self):
        audit = load_audit_module()

        self.assertFalse(
            audit.example_visual_boundary_mismatch(
                visual=True,
                ratio=0.73,
                missing_head=False,
                missing_tail=False,
            )
        )
        self.assertFalse(
            audit.example_visual_boundary_mismatch(
                visual=True,
                ratio=1.0,
                missing_head=True,
                missing_tail=False,
            )
        )
        self.assertTrue(
            audit.example_visual_boundary_mismatch(
                visual=True,
                ratio=0.62,
                missing_head=False,
                missing_tail=True,
            )
        )

    def test_anchor_present_allows_pdf_right_aligned_formula_number(self):
        audit = load_audit_module()
        content_norm = (
            "rho s frac c s sqrt v s 1 v s 2 frac rho e sigma e 1 sigma e 2 "
            "rho omega omega 1 omega 2 sqrt v s 1 v s 2 formula 28 39b"
        )

        self.assertTrue(
            audit.anchor_present_in_content(
                "rho omega omega 1 omega 2 sqrt v s 1 v s 2 28 39b",
                content_norm,
            )
        )
        self.assertFalse(
            audit.anchor_present_in_content(
                "rho omega omega 1 omega 2 sqrt v s 1 v s 2 28 40",
                content_norm,
            )
        )

    def test_embedded_example_heading_detection_ignores_ordinary_see_references(self):
        audit = load_audit_module()

        ordinary = "This uses Metropolis-Hastings (see Example A3.5 for the details)."
        absorbed = "The first example ends. Example 14.4. This should be a separate worked example."

        self.assertEqual(audit.EXAMPLE_HEADING_IN_TEXT_RE.findall(ordinary), [])
        self.assertEqual(audit.EXAMPLE_HEADING_IN_TEXT_RE.findall(absorbed), ["14.4"])

    def test_longer_than_raw_suspect_requires_visual_stop(self):
        audit = load_audit_module()

        self.assertFalse(
            audit.example_longer_than_raw_suspect(
                visual=False,
                ratio=3.0,
                raw_tail_present=True,
            )
        )
        self.assertTrue(
            audit.example_longer_than_raw_suspect(
                visual=True,
                ratio=3.0,
                raw_tail_present=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
