from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from scripts.build_genetics_staging import (
    apply_source_block_correction,
    apply_source_block_split,
    apply_source_text_corrections,
    choose_figure_deskew,
    choose_page_deskew,
    clean_text,
    is_source_heading,
    starts_example_unit,
    mark_index_terms,
    merge_cross_page_hyphenations,
    normalize_heading_text,
    join_adjacent_source_text,
    rotate_expanded,
    estimate_axis_skew,
    source_caption_match,
    FIGURE_CAPTION_RE,
    TABLE_CAPTION_RE,
    SOURCE_FORMULA_CORRECTIONS,
    NON_FORMULA_DISPLAY_BLOCKS,
    NON_BODY_FIGURE_LABEL_BLOCKS,
)
from scripts.audit_genetics_accuracy import source_text_for_comparison
from scripts.rebuild_genetics_book import ROOT as PROJECT_ROOT, RANGES, is_genetics_install_target, non_genetics_examples
from textbook_exporter import export_textbooks


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_genetics_ranges_end_chapter27_before_combined_appendix() -> None:
    assert RANGES["chapter27"] == (791, 818)
    assert RANGES["appendix1"] == (819, 992)
    covered = {page for start, end in RANGES.values() for page in range(start, end + 1)}
    assert not ({96, 266, 306, 698} & covered)


def test_install_target_scope_excludes_master_pdf_and_other_books() -> None:
    assert is_genetics_install_target(PROJECT_ROOT / "data/structured/Genetics_chapter1_001.json")
    assert is_genetics_install_target(PROJECT_ROOT / "data/figures/Genetics_1.1.png")
    assert is_genetics_install_target(PROJECT_ROOT / "data/figures/examples/Genetics_p138_b7.png")
    assert is_genetics_install_target(PROJECT_ROOT / "data/textbook/figures/examples/Genetics_p138_b7.png")
    assert not is_genetics_install_target(PROJECT_ROOT / "data/背景资料/Genetics.pdf")
    assert not is_genetics_install_target(PROJECT_ROOT / "data/figures/Evolution_1.1.png")


def test_staging_builder_mirrors_example_images_into_textbook() -> None:
    source = (PROJECT_ROOT / "scripts/build_genetics_staging.py").read_text(encoding="utf-8")
    assert 'shutil.rmtree(textbook_example_images)' in source
    assert 'shutil.copytree(example_images, textbook_example_images)' in source


def test_non_genetics_example_hash_ignores_genetics_rows(tmp_path: Path) -> None:
    path = tmp_path / "example_library.json"
    write_json(path, {"examples": [
        {"book": "Evolution", "id": "E1"},
        {"book": "Genetics", "id": "G1"},
    ]})
    count, digest = non_genetics_examples(path)
    write_json(path, {"examples": [
        {"book": "Evolution", "id": "E1"},
        {"book": "Genetics", "id": "G2", "content": "changed"},
    ]})
    assert count == 1
    assert non_genetics_examples(path) == (count, digest)


def test_exporter_remains_backward_compatible_with_heading_only_and_table_notes(tmp_path: Path) -> None:
    structured = tmp_path / "structured"
    out = tmp_path / "textbook"
    write_json(
        structured / "Genetics_chapter4_001.json",
        {
            "id": "Genetics_chapter4_001",
            "node_kind": "heading",
            "allow_empty": True,
            "metadata": {
                "chapter": "Genetics_chapter4",
                "heading_path": ["THE TRANSMISSION OF GENETIC INFORMATION"],
                "display_heading": "THE TRANSMISSION OF GENETIC INFORMATION",
            },
            "blocks": [],
        },
    )
    write_json(
        structured / "Genetics_chapter4_002.json",
        {
            "id": "Genetics_chapter4_002",
            "metadata": {
                "chapter": "Genetics_chapter4",
                "heading_path": ["THE TRANSMISSION OF GENETIC INFORMATION", "The Hardy-Weinberg Principle"],
                "display_heading": "THE TRANSMISSION OF GENETIC INFORMATION / The Hardy-Weinberg Principle",
            },
            "blocks": [{"type": "table", "content": "[[TABLE:2.1]]"}],
        },
    )
    write_json(
        structured / "Genetics_table_library.json",
        {
            "tables": [
                {
                    "id": "2.1",
                    "title": "Table 2.1 Test",
                    "rows": [["A", "B"], ["1", "2"]],
                    "notes": [{"marker": "*", "content": "This belongs to the table."}],
                    "source": {"chapter": "Genetics_chapter4", "unit_id": "Genetics_chapter4_002", "page": 1},
                }
            ]
        },
    )
    write_json(structured / "Genetics_formula_library.json", {"formulas": []})
    write_json(structured / "example_library.json", {"examples": []})
    export_textbooks(structured_dir=structured, out_dir=out, chapters={"Genetics_chapter4"}, book_id="Genetics")
    rendered = (out / "Genetics_chapter4_textbook.md").read_text(encoding="utf-8")
    assert "THE TRANSMISSION OF GENETIC INFORMATION" in rendered
    assert "* This belongs to the table." in rendered


def test_genetics_delivery_has_only_nonempty_contiguous_content_units() -> None:
    structured = PROJECT_ROOT / "data" / "structured"
    units = []
    by_chapter: dict[str, list[dict]] = {}
    for path in sorted(structured.glob("Genetics_*_[0-9][0-9][0-9].json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        units.append(unit)
        by_chapter.setdefault(unit["metadata"]["chapter"], []).append(unit)

    assert len(units) == 441
    assert all(unit.get("blocks") for unit in units)
    assert all(unit.get("node_kind") != "heading" for unit in units)
    assert all(not unit.get("allow_empty") for unit in units)
    for chapter, chapter_units in by_chapter.items():
        assert [unit["id"] for unit in chapter_units] == [
            f"{chapter}_{index:03d}" for index in range(1, len(chapter_units) + 1)
        ]


def test_genetics_pdf_confirmed_heading_merges_are_installed() -> None:
    structured = PROJECT_ROOT / "data" / "structured"
    units = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(structured.glob("Genetics_*_[0-9][0-9][0-9].json"))
    ]
    headings = {
        unit["metadata"]["display_heading"]: unit
        for unit in units
    }

    hardy_heading = "THE TRANSMISSION OF GENETIC INFORMATION / The Hardy-Weinberg Principle"
    assert headings[hardy_heading]["blocks"]
    assert set(headings[hardy_heading]["metadata"]["heading_source"]["source_block_ids"]) == {
        "p70:b2", "p70:b3",
    }

    wrapped = "FINE MAPPING OF MAJOR GENES USING POPULATION-LEVEL DISEQUILIBRIUM"
    assert headings[wrapped]["blocks"]
    assert set(headings[wrapped]["metadata"]["heading_source"]["source_block_ids"]) == {
        "p427:b3", "p427:b4",
    }

    for unit in units:
        path = unit["metadata"].get("heading_path") or []
        normalized = [normalize_heading_text(item).casefold() for item in path]
        assert len(normalized) == len(set(normalized))
        chapter_number = unit["metadata"]["chapter"].removeprefix("Genetics_chapter")
        if chapter_number.isdigit():
            assert not path or path[0] != chapter_number


def test_page_deskew_chooses_improving_sign_and_expands_canvas() -> None:
    source = np.full((500, 800, 3), 255, dtype=np.uint8)
    for y in range(80, 430, 45):
        cv2.line(source, (80, y), (720, y), (0, 0, 0), 3)
    tilted = rotate_expanded(source, -2.0)
    evidence = choose_page_deskew(tilted)
    assert evidence["status"] == "page_deskew_candidate"
    assert abs(float(evidence["page_skew_after"])) < abs(float(evidence["page_skew_before"]))
    corrected = rotate_expanded(tilted, float(evidence["angle"]))
    assert corrected.shape[0] >= tilted.shape[0]
    assert corrected.shape[1] >= tilted.shape[1]


def test_page_deskew_ignores_design_diagonals_without_axis_evidence() -> None:
    source = np.full((400, 600, 3), 255, dtype=np.uint8)
    cv2.line(source, (60, 340), (540, 60), (0, 0, 0), 4)
    evidence = choose_page_deskew(source)
    assert evidence["status"] in {"no_page_axis_evidence", "page_unchanged"}
    assert float(evidence["angle"]) == 0.0


def test_figure_deskew_uses_figure_baseline_and_rejects_bad_page_angle() -> None:
    source = np.full((420, 620, 3), 255, dtype=np.uint8)
    for y in range(70, 370, 50):
        cv2.line(source, (70, y), (550, y), (0, 0, 0), 3)
    evidence = choose_figure_deskew(
        source,
        {"status": "page_deskew_candidate", "angle": 2.0},
    )
    assert evidence["status"] == "figure_already_aligned"
    assert evidence["angle"] == 0.0


def test_figure_deskew_does_not_rotate_large_design_angle() -> None:
    source = np.full((420, 620, 3), 255, dtype=np.uint8)
    for offset in range(0, 220, 45):
        cv2.line(source, (60, 350 - offset), (560, 60 - offset), (0, 0, 0), 3)
    evidence = choose_figure_deskew(source, {"status": "page_unchanged", "angle": 0.0})
    assert evidence["status"] in {"no_figure_axis_evidence", "figure_direction_unreliable"}
    assert evidence["angle"] == 0.0


def test_figure_deskew_reports_residual_for_applied_rounded_angle() -> None:
    source = np.full((500, 800, 3), 255, dtype=np.uint8)
    for y in range(80, 430, 45):
        cv2.line(source, (80, y), (720, y), (0, 0, 0), 3)
    tilted = rotate_expanded(source, -2.0037)
    evidence = choose_figure_deskew(tilted, {"status": "page_unchanged", "angle": 0.0})
    assert evidence["status"] == "figure_deskew_candidate"
    actual, _ = estimate_axis_skew(rotate_expanded(tilted, float(evidence["angle"])))
    assert float(evidence["figure_skew_after"]) == pytest.approx(actual, abs=0.001)
    assert abs(actual) <= 0.5


def test_cross_page_hyphenation_can_join_across_a_table_block() -> None:
    units = [{
        "blocks": [
            {"type": "discussion", "content": "lethal equiv-", "source_page": 295, "source_block_ids": ["p295:b8"]},
            {"type": "table", "content": "[[TABLE:10.6]]", "source_page": 296},
            {"type": "discussion", "content": "alents expressed", "source_page": 296, "source_block_ids": ["p296:b5"]},
        ]
    }]
    assert merge_cross_page_hyphenations(units) == 1
    assert units[0]["blocks"][0]["content"] == "lethal equivalents expressed"
    assert len(units[0]["blocks"]) == 2


def test_source_verified_ocr_correction_is_page_scoped() -> None:
    assert apply_source_text_corrections(393, "1 his chapter introduces") == "This chapter introduces"
    assert apply_source_text_corrections(392, "1 his chapter introduces") == "1 his chapter introduces"
    assert apply_source_text_corrections(593, "1nus, we see") == "Thus, we see"
    assert apply_source_text_corrections(592, "1nus, we see") == "1nus, we see"
    assert apply_source_text_corrections(
        507, "where i, j, k, and l denote different marker alleles"
    ) == r"where $ i, j, k, $ and $ \ell $ denote different marker alleles"
    assert apply_source_text_corrections(
        506, "where i, j, k, and l denote different marker alleles"
    ) == "where i, j, k, and l denote different marker alleles"


def test_source_verified_heritability_line_break_removes_layout_hyphen() -> None:
    source = (
        "Examination of this formula reveals several undesirable properties of heri-\n"
        "tability estimates on the observed scale:"
    )
    assert apply_source_text_corrections(754, source) == (
        "Examination of this formula reveals several undesirable properties of "
        "heritability estimates on the observed scale:"
    )
    assert apply_source_text_corrections(753, source) == source


def test_source_verified_em_iterations_ocr_correction_is_page_scoped() -> None:
    source = "the whole procedure continues until the interactions converge."
    expected = "the whole procedure continues until the iterations converge."
    assert apply_source_text_corrections(877, source) == expected
    assert apply_source_text_corrections(876, source) == source


def test_source_verified_noncentral_chi_square_removes_duplicated_prior_block() -> None:
    source = (
        "In this last case, subtraction of the mean causes the loss of the degree of freedom.\n"
        "A noncentral  $ \\chi^{2} $ arises when the random variables have nonzero means."
    )
    expected = "A noncentral  $ \\chi^{2} $ arises when the random variables have nonzero means."
    assert apply_source_text_corrections(890, source) == expected
    assert apply_source_text_corrections(889, source) == source


def test_source_verified_possible_cross_page_join_is_bbox_scoped() -> None:
    previous = {
        "content": "Where selfing is not pos-",
        "source_page": 419,
        "source_block_ids": ["p419:b6"],
        "bbox": [70.0, 1281.0, 1032.0, 1516.0],
    }
    current = {
        "content": "sible, after several generations",
        "source_page": 420,
        "source_block_ids": ["p420:b2"],
        "bbox": [117.0, 133.0, 1077.0, 328.0],
    }
    joined, correction = join_adjacent_source_text(previous, current)
    assert joined == "Where selfing is not possible, after several generations"
    assert correction and correction["replacement"] == "possible"

    current["bbox"] = [0.0, 0.0, 1.0, 1.0]
    with pytest.raises(RuntimeError, match="evidence drifted"):
        join_adjacent_source_text(previous, current)


def test_source_verified_frequency_cross_page_join_removes_ocr_duplication() -> None:
    previous = {
        "content": "is often compared with the fre-",
        "source_page": 433,
        "source_block_ids": ["p433:b6"],
        "bbox": [83.0, 1458.0, 1046.0, 1536.0],
    }
    current = {
        "content": "frequency of this allele",
        "source_page": 434,
        "source_block_ids": ["p434:b2"],
        "bbox": [132.0, 136.0, 1095.0, 416.0],
    }
    joined, correction = join_adjacent_source_text(previous, current)
    assert joined == "is often compared with the frequency of this allele"
    assert correction and "duplicate word" in correction["reason"]


def test_source_verified_fundamental_cross_page_join_removes_layout_hyphen() -> None:
    previous = {
        "content": "covariance matrix similarity, a funda-",
        "source_page": 663,
        "source_block_ids": ["p663:b6"],
        "bbox": [104.0, 1471.0, 1010.0, 1507.0],
    }
    current = {
        "content": "mental issue that needs to be dealt with",
        "source_page": 664,
        "source_block_ids": ["p664:b2"],
        "bbox": [139.0, 138.0, 1102.0, 583.0],
    }
    joined, correction = join_adjacent_source_text(previous, current)
    assert joined == "covariance matrix similarity, a fundamental issue that needs to be dealt with"
    assert correction and correction["replacement"] == "fundamental"


def test_example_26_10_continuation_header_has_exact_source_override() -> None:
    row = {
        "block_id": 2,
        "block_bbox": [114, 128, 957, 177],
        "block_content": "which gives the same estimates as obtained with the permanent-effects model.",
    }
    kind, correction = apply_source_block_correction(785, row, "header", row["block_content"])
    assert kind == "text"
    assert correction and "Example 26.10" in correction["reason"]
    unchanged, absent = apply_source_block_correction(784, row, "header", row["block_content"])
    assert unchanged == "header"
    assert absent is None


def test_example_4_continuation_paragraph_title_has_exact_source_override() -> None:
    row = {
        "block_id": 2,
        "block_bbox": [169, 144, 498, 175],
        "block_content": "different marker genotypes as",
    }
    kind, correction = apply_source_block_correction(
        460, row, "paragraph_title", row["block_content"]
    )
    assert kind == "text"
    assert correction and "Example 4 continuation" in correction["reason"]


def test_page_481_merged_heading_and_body_has_exact_source_split() -> None:
    text = (
        "Detecting Multiple Linked QTLs Using Standard Marker-Trait Regressions\n"
        "Consider the standard multiple regression of trait value on the single-locus genotypes at each of n markers,"
    )
    row = {"block_id": 3, "block_bbox": [75, 193, 1036, 310], "block_content": text}
    split = apply_source_block_split(481, row, "text", text)
    assert split and split["heading"].startswith("Detecting Multiple Linked QTLs")
    assert split["body"].startswith("Consider the standard multiple regression")

    with pytest.raises(RuntimeError, match="split evidence drifted"):
        apply_source_block_split(481, row, "paragraph_title", text)


def test_page_106_formula_corrections_are_bbox_scoped_and_clean() -> None:
    page_106 = {
        key: value for key, value in SOURCE_FORMULA_CORRECTIONS.items() if key[0] == 106
    }
    assert len(page_106) == 11
    joined = "\n".join(SOURCE_FORMULA_CORRECTIONS.values())
    assert r"G_{B_M\cdot U_{TT}}=63.80" in joined
    assert r"(\delta\delta)_{B_{TT}U_{TT}}=-4.5125" in joined
    assert not any(token in joined for token in ("underbrace", "boldmath", "Ш", "爻", "·Ў"))


def test_katex_formula_repairs_are_source_page_and_bbox_scoped() -> None:
    repaired_pages = {177, 214, 386, 786, 789, 808, 856, 900}
    assert repaired_pages <= {page for page, _ in SOURCE_FORMULA_CORRECTIONS}
    joined = "\n".join(
        latex for (page, _), latex in SOURCE_FORMULA_CORRECTIONS.items() if page in repaired_pages
    )
    assert r"\[" not in joined
    assert "$" not in joined
    assert "夢" not in joined
    assert r"\widehat{\mathbf{c}}}" not in joined
    assert r"\end{array}\right." not in joined


def test_inline_katex_repairs_follow_visually_verified_pdf_text() -> None:
    assert r"$\sqrt{\mathrm{Var}(A)}$" in apply_source_text_corrections(
        282, r"two standard errors equal $\sqrt{\mathrm{Var}(A)$"
    )
    assert r"$SE(b) = \sqrt{\mathrm{Var}(b)}$" in apply_source_text_corrections(
        557, r"where $SE(b) = \sqrt{\overline{Var}(b)$"
    )
    page_840 = apply_source_text_corrections(
        840,
        "it produces $ (G_f $ and $ H_f $ $ will; produced it $ (G_o $ and $ H_f $ $.",
    )
    assert "it produces ($ G_f $ and $ H_f $) will" in page_840
    assert "produced it ($ G_o $ and $ H_f $)." in page_840
    assert r"\widehat{\sigma}^{2(0)}" in apply_source_text_corrections(
        877, r"\widehat{\sigma}^2^{(0)}"
    )


def test_figure_5_6_chromosome_panels_are_not_formulas() -> None:
    assert NON_FORMULA_DISPLAY_BLOCKS == {(117, 3), (117, 5)}


def test_composite_figure_panel_labels_are_not_emitted_as_prose() -> None:
    assert NON_BODY_FIGURE_LABEL_BLOCKS == {
        (53, 2): {
            "expected_text": "(A)",
            "bbox": [91.0, 124.0, 126.0, 152.0],
            "reason": "Figure 3.1 panel label split from the composite figure",
        },
        (59, 2): {
            "expected_text": "(A)",
            "bbox": [191.0, 130.0, 226.0, 159.0],
            "reason": "Figure 3.4 panel label split from the composite figure",
        },
        (150, 3): {
            "expected_text": "Probability",
            "bbox": [264.0, 134.0, 378.0, 164.0],
            "reason": "Figure 7.2 internal column label split from the figure",
        },
        (181, 2): {
            "expected_text": "Monozygotic twins",
            "bbox": [449.0, 133.0, 646.0, 163.0],
            "reason": "Figure 7.8 internal relationship label split from the figure",
        },
        (181, 3): {
            "expected_text": "Raised by own parents",
            "bbox": [226.0, 163.0, 453.0, 193.0],
            "reason": "Figure 7.8 internal environment label split from the figure",
        },
        (181, 4): {
            "expected_text": "Raised by different parents",
            "bbox": [643.0, 166.0, 908.0, 198.0],
            "reason": "Figure 7.8 internal environment label split from the figure",
        },
        (181, 6): {
            "expected_text": "Full sibs",
            "bbox": [498.0, 524.0, 591.0, 557.0],
            "reason": "Figure 7.8 internal relationship label split from the figure",
        },
    }


def test_paragraph_title_examples_remain_examples() -> None:
    assert not is_source_heading("paragraph_title", "Example 2. Compute the product L = MN where")
    assert starts_example_unit("paragraph_title", "Example 2. Compute the product L = MN where")
    assert not starts_example_unit("paragraph_title", "Partitioned Matrices")
    assert is_source_heading("paragraph_title", "Partitioned Matrices")


def test_appendix_example_f_quantile_subscript_correction() -> None:
    source = "so that the critical value is $ F_{3,16}, [0.95] = 3.24 $."
    corrected = apply_source_text_corrections(894, source)
    assert r"F_{3,16,[0.95]} = 3.24" in corrected
    assert r"F_{3,16}, [0.95]" not in corrected


def test_prose_starting_with_figure_or_table_is_not_a_caption() -> None:
    assert source_caption_match("text", "Figure 5.3 illustrates two analyses", FIGURE_CAPTION_RE) is None
    assert source_caption_match("text", "Table 11.1 gives the values", TABLE_CAPTION_RE) is None
    assert source_caption_match("figure_title", "Figure 5.3 Growth rate", FIGURE_CAPTION_RE)
    assert source_caption_match("figure_title", "Table 11.1 Probability", TABLE_CAPTION_RE)


def test_clean_text_preserves_tex_alignment_not_token() -> None:
    assert clean_text(r"0&not attending") == r"0&not attending"
    assert clean_text("Spiess &amp; Allen") == "Spiess & Allen"


def test_index_markup_prefers_longest_non_overlapping_terms() -> None:
    rendered, count = mark_index_terms(
        "fluctuating asymmetry is measured",
        {"fluctuating", "asymmetry", "fluctuating asymmetry"},
    )
    assert rendered == "[[fluctuating asymmetry]] is measured"
    assert count == 1
    assert "[[[[" not in rendered


def test_exporter_merges_continued_table_parts_at_section_sink(tmp_path: Path) -> None:
    structured = tmp_path / "structured"
    out = tmp_path / "textbook"
    write_json(
        structured / "Genetics_chapter6_001.json",
        {
            "id": "Genetics_chapter6_001",
            "metadata": {"chapter": "Genetics_chapter6", "heading_path": ["SECTION"]},
            "blocks": [{"type": "table", "content": "[[TABLE:6.1]]"}],
        },
    )
    write_json(
        structured / "Genetics_table_library.json",
        {
            "tables": [{
                "id": "6.1",
                "title": "Table 6.1 Test",
                "parts": [
                    {"page": 130, "rows": [["A", "B"], ["first", "1"]], "notes": []},
                    {"page": 131, "rows": [["A", "B"], ["continued", "2"]], "notes": []},
                ],
                "source": {"chapter": "Genetics_chapter6", "unit_id": "Genetics_chapter6_001", "page": 130, "pages": [130, 131]},
            }]
        },
    )
    write_json(structured / "Genetics_formula_library.json", {"formulas": []})
    write_json(structured / "example_library.json", {"examples": []})
    export_textbooks(structured_dir=structured, out_dir=out, chapters={"Genetics_chapter6"}, book_id="Genetics")
    rendered = (out / "Genetics_chapter6_textbook.md").read_text(encoding="utf-8")
    assert rendered.count("**Table 6.1**") == 1
    assert "See Table 6.1 at the end of this section." in rendered
    assert "[[SEE_TABLE:6.1]]" not in rendered
    assert "first" in rendered
    assert "continued" in rendered
    assert "continued, page 131" in rendered


def test_auditor_compares_split_source_block_with_body_only() -> None:
    source_id = "p481:b3"
    raw_by_id = {
        source_id: {
            "block_content": (
                "Detecting Multiple Linked QTLs Using Standard Marker-Trait Regressions\n"
                "Consider the standard multiple regression"
            )
        }
    }
    split_bodies = {source_id: "Consider the standard multiple regression"}
    assert source_text_for_comparison([source_id], raw_by_id, split_bodies) == (
        "Consider the standard multiple regression"
    )


def test_auditor_compares_p890_against_source_verified_corrected_text() -> None:
    source_id = "p890:b17"
    raw_by_id = {
        source_id: {
            "block_bbox": [150.0, 1135.0, 1111.0, 1263.0],
            "block_content": (
                "In this last case, subtraction of the mean causes the loss of the degree of freedom.\n"
                "A noncentral chi-square arises"
            ),
        }
    }
    assert source_text_for_comparison([source_id], raw_by_id, {}) == "A noncentral chi-square arises"
