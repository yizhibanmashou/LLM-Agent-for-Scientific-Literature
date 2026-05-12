import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from knowledge_engineering.core.runtime import (
    CompositeChunk,
    build_composite_chunks,
    extract_semantic_blocks,
    FormulaLibrary,
    KnowledgeBlock,
    KnowledgeUnit,
    SemanticBlock,
    TableEntry,
    TableLibrary,
)
from knowledge_engineering.pipeline.process import (
    _create_missing_table_body_stubs,
    _extract_table_envs_and_replace,
    _extract_tables_from_paddle_raw,
    _table_reference_key,
    _review_chunks_with_llm,
    assign_table_sources_to_units,
    build_toc_outputs_from_text,
    derive_chapter_name,
    extract_tables_and_replace,
    preprocess_extracted_text,
    refine_chunks_for_output,
    recover_paddle_footer_body_text,
    split_tex_book,
    strip_latex_markup,
)


class TestKnowledgeEngineeringLatexProcess(unittest.TestCase):
    def test_strip_latex_markup_preserves_tagged_equation_labels(self):
        sample = (
            "\\begin{document}\n"
            "Leading text.\n"
            "\\begin{equation}\n"
            "x = y + z\n"
            "\\tag{6.1a}\n"
            "\\label{eq:6_1a}\n"
            "\\end{equation}\n"
            "\\end{document}\n"
        )

        processed = strip_latex_markup(sample)

        self.assertIn("$$\nx = y + z\n$$\n(6.1a)", processed)
        self.assertNotIn("\\tag", processed)
        self.assertNotIn("\\label", processed)

    def test_strip_latex_markup_uses_document_title_as_parent_heading(self):
        sample = (
            "\\title{Short-term Changes in the Mean:}\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\section{2. Truncation and Threshold Selection}\n"
            "Opening prose.\n\n"
            "\\section{TRUNCATION SELECTION}\n"
            "Body prose.\n"
            "\\end{document}\n"
        )

        processed = strip_latex_markup(sample)

        self.assertIn("# Short-term Changes in the Mean: 2. Truncation and Threshold Selection", processed)
        self.assertIn("## TRUNCATION SELECTION", processed)

    def test_derive_chapter_name_from_chapter_full_dir(self):
        tex_path = str(Path("data") / "paddle_output" / "chapter6_full" / "main.tex")
        self.assertEqual(derive_chapter_name(tex_path), "chapter6")

    def test_derive_chapter_name_from_appendix_full_dir(self):
        tex_path = str(Path("data") / "paddle_output" / "appendix2_full" / "main.tex")
        self.assertEqual(derive_chapter_name(tex_path), "appendix2")

    def test_recover_paddle_footer_body_text_restores_body_footer_before_next_anchor(self):
        pages = [
            {
                "parsing_res_list": [
                    {
                        "block_label": "text",
                        "block_content": "Putting these results together into Equation 6.6 yields",
                        "block_order": 1,
                        "block_bbox": [0, 100, 100, 120],
                    },
                    {
                        "block_label": "footer",
                        "block_content": "The Robertson-Price Identity, $ S = \\sigma(w, z) $",
                        "block_bbox": [0, 700, 100, 720],
                    },
                    {
                        "block_label": "footer",
                        "block_content": (
                            "When our concern is strictly on the within-generation change in trait value, "
                            "then $ \\Delta\\overline{z} = \\mu_{z}^{*} - \\mu_{z} $."
                        ),
                        "block_bbox": [0, 730, 100, 750],
                    },
                ]
            },
            {
                "parsing_res_list": [
                    {
                        "block_label": "text",
                        "block_content": (
                            "fitness-weighted mean after selection continues here with enough tokens "
                            "for anchor matching"
                        ),
                        "block_order": 1,
                        "block_bbox": [0, 100, 100, 120],
                    }
                ]
            },
        ]
        plain_text = (
            "Putting these results together into Equation 6.6 yields\n\n"
            "fitness-weighted mean after selection continues here with enough tokens for anchor matching"
        )

        with patch("knowledge_engineering.pipeline.process._load_paddle_raw_pages", return_value=pages):
            recovered = recover_paddle_footer_body_text(plain_text, "chapter6_full/main.tex")

        self.assertIn("## The Robertson-Price Identity, $ S = \\sigma(w, z) $", recovered)
        self.assertIn("When our concern is strictly on the within-generation change", recovered)
        self.assertLess(
            recovered.index("When our concern is strictly"),
            recovered.index("fitness-weighted mean after selection"),
        )

    def test_recover_paddle_footer_body_text_skips_hyphen_fragment_without_lowercase_anchor(self):
        pages = [
            {
                "parsing_res_list": [
                    {
                        "block_label": "text",
                        "block_content": "Newly arising lethals could be due to new mutation.",
                        "block_order": 1,
                        "block_bbox": [0, 100, 100, 120],
                    },
                    {
                        "block_label": "footer",
                        "block_content": (
                            "Example 25.9. Consider the following estimated variance components from "
                            "a selection ex-"
                        ),
                        "block_bbox": [0, 730, 100, 750],
                    },
                ]
            },
            {
                "parsing_res_list": [
                    {
                        "block_label": "text",
                        "block_content": (
                            "The selected line shows large increases in additive variance and "
                            "heritability relative to the base population."
                        ),
                        "block_order": 1,
                        "block_bbox": [0, 100, 100, 120],
                    }
                ]
            },
        ]
        plain_text = (
            "Newly arising lethals could be due to new mutation.\n\n"
            "The selected line shows large increases in additive variance and heritability "
            "relative to the base population."
        )

        with patch("knowledge_engineering.pipeline.process._load_paddle_raw_pages", return_value=pages):
            recovered = recover_paddle_footer_body_text(plain_text, "chapter25_full/main.tex")

        self.assertNotIn("Example 25.9", recovered)
        self.assertEqual(recovered, plain_text)

    def test_strip_latex_markup_extracts_inline_tail_equation_labels(self):
        sample = (
            "\\begin{document}\n"
            "\\begin{equation}\n"
            "\\begin{aligned}\n"
            "\\sigma(x,y)=\\sigma(x,z)\\quad(6.33\\mathrm{d})\n"
            "\\end{aligned}\n"
            "\\end{equation}\n"
            "\\end{document}\n"
        )

        processed = strip_latex_markup(sample)

        self.assertIn("(6.33d)", processed)
        self.assertNotIn("(6.33\\mathrm{d})", processed)

    def test_preprocess_wraps_numbered_ocr_formula(self):
        sample = (
            "same parental gene is [1-(1/2N)], the expected inbreeding coefficient in generation t is\n"
            "f=+(1-)f-1\n"
            "(2.3)\n"
            "Subtracting both sides from one yields the recursion formula\n"
            "(1-f)=(1-)(1-f-1)\n"
            "(2.4a)\n"
        )

        processed = preprocess_extracted_text(sample)

        self.assertIn("$$\nf=+(1-)f-1\n$$\n(2.3)", processed)
        self.assertIn("$$\n(1-f)=(1-)(1-f-1)\n$$\n(2.4a)", processed)

        formula_library = FormulaLibrary()
        replaced_text, reference_ids = formula_library.extract_add_and_replace(
            text=processed,
            source_unit_id="paper1_block_001",
            source_chapter="paper1",
            source_subsection="CHAPTER 2",
        )

        self.assertEqual(formula_library.get_stats()["total"], 2)
        self.assertIn("见公式(2.3)", replaced_text)
        self.assertIn("见公式(2.4a)", replaced_text)
        self.assertEqual(reference_ids, ["formula_2.3", "formula_2.4a"])

    def test_preprocess_wraps_multiline_ocr_formula_with_fragments(self):
        sample = (
            "This rate of decay of heterozygosity may be approximated as\n"
            "Ht=Ho\n"
            "(1-)\n"
            "(2.5)\n"
            "Performing the double integration with respect to p leads to the solution\n"
            "ta(po)＞-4N[poln(po)+(1-po)ln(1-po)]\n"
            "(2.11a)\n"
        )

        processed = preprocess_extracted_text(sample)

        self.assertIn("$$\nHt=Ho\n(1-)\n$$\n(2.5)", processed)
        self.assertIn("$$\nta(po)＞-4N[poln(po)+(1-po)ln(1-po)]\n$$\n(2.11a)", processed)

        formula_library = FormulaLibrary()
        _, reference_ids = formula_library.extract_add_and_replace(
            text=processed,
            source_unit_id="paper1_block_002",
            source_chapter="paper1",
            source_subsection="CHAPTER 2",
        )

        self.assertEqual(reference_ids, ["formula_2.5", "formula_2.11a"])
        self.assertEqual(formula_library.get_stats()["total"], 2)

    def test_preprocess_does_not_absorb_prose_into_formula_block(self):
        sample = (
            "Substituting into Equations 5.17a and 5.17b and recalling that fw(z)p(z)dz=1 yields the\n"
            "average excess in relative fitness (Equation 5.8b) as\n"
            "s1=w1-1>-a4fw(2)d\n"
            "(5.19a)\n"
        )

        processed = preprocess_extracted_text(sample)

        self.assertIn("average excess in relative fitness", processed)
        self.assertIn("$$\ns1=w1-1>-a4fw(2)d\n$$\n(5.19a)", processed)
        self.assertNotIn(
            "$$\nSubstituting into Equations 5.17a and 5.17b",
            processed,
        )

    def test_preprocess_filters_toc_and_figure_noise(self):
        sample = (
            "CONTENTS\n"
            "Price's theorem, R2=σ(wi,zi)+E(wiδi)..............\n"
            "147\n"
            "1992:y=0.082x-151(r2=0.84)\n"
            "1993:y=0.059x-112(r2=0.87)\n"
            "EVOLUTION OF QUANTITATIVE TRAITS\n"
            "Year of hybrid introduction\n"
            "32 CHAPTER 2\n"
            "Figure 1.1 A striking example of the power of artificial selection is seen in lines of broilers,\n"
            "chickens selected for meat production.\n"
            "A BRIEF HISTORY OF THE STUDY OF THE EVOLUTION OF\n"
            "QUANTITATIVE TRAITS\n"
            "Although the histories of population and quantitative genetics are highly intertwined,\n"
        )

        processed = preprocess_extracted_text(sample)

        self.assertNotIn("CONTENTS", processed)
        self.assertNotIn("Price's theorem", processed)
        self.assertNotIn("1992:y=0.082x-151(r2=0.84)", processed)
        self.assertNotIn("Year of hybrid introduction", processed)
        self.assertNotIn("32 CHAPTER 2", processed)
        self.assertNotIn("Figure 1.1", processed)
        self.assertNotIn("chickens selected for meat production", processed)
        self.assertIn("A BRIEF HISTORY OF THE STUDY OF THE EVOLUTION OF", processed)
        self.assertIn("Although the histories of population and quantitative genetics", processed)

    def test_preprocess_keeps_body_references_to_figures_and_tables(self):
        sample = (
            "Figure 5.3 shows this for the three-allele case, which is a section of a two-dimensional plane\n"
            "Table 1.1 and expanded upon in the following chapters, the structure of evolutionary theory\n"
            "Table 8.1 summarizes expressions for f and also for the population-genetic impacts of a sweep.\n"
            "Table 8.1 Summary of various features associated with a hard sweep of a favorable allele A with\n"
            "continued caption text.\n"
        )

        processed = preprocess_extracted_text(sample)

        self.assertIn("Figure 5.3 shows this for the three-allele case", processed)
        self.assertIn("Table 1.1 and expanded upon in the following chapters", processed)
        self.assertIn("Table 8.1 summarizes expressions for f", processed)
        self.assertNotIn("Table 8.1 Summary of various features associated with a hard sweep", processed)
        self.assertNotIn("continued caption text", processed)

    def test_refine_chunks_for_output_trims_frontmatter_and_infers_sections(self):
        source_title = "Evolution and Selection of Quantitative Traits"
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="Introduction",
                        content="Evolution and Selection of Quantitative Traits Bruce Walsh Oxford University Press",
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="3. THE GENETIC EFFECTIVE SIZE OF A POPULATION",
                        content="Partial Inbreeding Population Subdivision",
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="CHAPTER I",
                        content="The Fusion of Population and Quantitative Genetics. "
                        "This long introductory paragraph keeps real prose intact. " * 4,
                    ),
                    SemanticBlock(
                        type="discussion",
                        subsection="EVOLUTION OF OUANTITATIVE TRAITS",
                        content="EVOLUTION AND SELECTION OF QUANTITATIVE TRAITS is a page header. "
                        "The remainder of the block should stay readable.",
                    ),
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="derivation",
                        subsection="THE WRIGHT-FISHER MODEL",
                        content="The probability transition yields 见公式(2.1) (2.1) in the classical model.",
                        formula_references=["formula_2.1"],
                    ),
                    SemanticBlock(
                        type="discussion",
                        subsection="NEUTRAL EVOLUTION",
                        content="This block should inherit the major section title.",
                    ),
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="NEUTRAL EVOLUTION",
                        content="Follow-up prose without a new formula should keep the previous section.",
                    )
                ]
            ),
        ]

        refined_chunks, sections = refine_chunks_for_output(chunks, source_title=source_title)

        self.assertEqual(len(refined_chunks), 3)
        self.assertEqual(sections[0], "Chapter 1: EVOLUTION OF QUANTITATIVE TRAITS")
        self.assertEqual(sections[1], "Chapter 2: NEUTRAL EVOLUTION")
        self.assertEqual(sections[2], "Chapter 2: NEUTRAL EVOLUTION")
        self.assertEqual(
            refined_chunks[0].subsections,
            ["CHAPTER I", "EVOLUTION OF QUANTITATIVE TRAITS"],
        )
        self.assertNotIn(
            "EVOLUTION AND SELECTION OF QUANTITATIVE TRAITS",
            refined_chunks[0].blocks[1].content,
        )
        self.assertIn("见公式(2.1)", refined_chunks[1].blocks[0].content)
        self.assertNotIn("(2.1)", refined_chunks[1].blocks[0].content.replace("见公式(2.1)", ""))

    def test_heading_hierarchy_records_l1_l2_and_null_l2(self):
        text = (
            "# DETERMINISTIC SINGLE-LOCUS THEORY\n"
            "The contribution to the selection limit from a single locus depends on genetic parameters.\n\n"
            "# Expected Contribution From a Single Locus\n"
            "We start with the expected total contribution from a given diallelic locus.\n"
        )
        formula_library = FormulaLibrary()

        blocks, _ = extract_semantic_blocks(text, "chapter25", None, formula_library)
        chunks = build_composite_chunks(blocks)
        refined_chunks, _ = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(len(refined_chunks), 2)
        self.assertEqual(refined_chunks[0].section_level_1, "DETERMINISTIC SINGLE-LOCUS THEORY")
        self.assertIsNone(refined_chunks[0].section_level_2)
        self.assertEqual(refined_chunks[0].heading_path, ["DETERMINISTIC SINGLE-LOCUS THEORY"])
        self.assertEqual(refined_chunks[0].display_heading, "DETERMINISTIC SINGLE-LOCUS THEORY")

        self.assertEqual(refined_chunks[1].section_level_1, "DETERMINISTIC SINGLE-LOCUS THEORY")
        self.assertEqual(refined_chunks[1].section_level_2, "Expected Contribution From a Single Locus")
        self.assertEqual(
            refined_chunks[1].heading_path,
            ["DETERMINISTIC SINGLE-LOCUS THEORY", "Expected Contribution From a Single Locus"],
        )
        self.assertEqual(refined_chunks[1].display_heading, "Expected Contribution From a Single Locus")

    def test_long_title_case_l2_updates_inferred_section(self):
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="Lerner's Model of Genetic Homeostasis",
                        content="Homeostasis discussion.",
                        formula_references=["formula_25.16"],
                        section_level_1="CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION",
                        section_level_2="Lerner's Model of Genetic Homeostasis",
                        heading_path=[
                            "CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION",
                            "Lerner's Model of Genetic Homeostasis",
                        ],
                        display_heading="Lerner's Model of Genetic Homeostasis",
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="Artificial Selection Countered by Natural Stabilizing Selection",
                        content="Stabilizing selection discussion.",
                        formula_references=["formula_25.17a"],
                        section_level_1="CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION",
                        section_level_2="Artificial Selection Countered by Natural Stabilizing Selection",
                        heading_path=[
                            "CONFLICTS BETWEEN NATURAL AND ARTIFICIAL SELECTION",
                            "Artificial Selection Countered by Natural Stabilizing Selection",
                        ],
                        display_heading="Artificial Selection Countered by Natural Stabilizing Selection",
                    )
                ]
            ),
        ]

        refined_chunks, sections = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(
            sections,
            [
                "Chapter 25: Lerner's Model of Genetic Homeostasis",
                "Chapter 25: Artificial Selection Countered by Natural Stabilizing Selection",
            ],
        )
        self.assertEqual(
            refined_chunks[1].display_heading,
            "Artificial Selection Countered by Natural Stabilizing Selection",
        )

    def test_short_l2_heading_metadata_updates_inferred_section(self):
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="Linkage Effects",
                        content="Linkage discussion.",
                        formula_references=["formula_25.11"],
                        section_level_1="INCREASES IN VARIANCES AND ACCELERATED RESPONSES",
                        section_level_2="Linkage Effects",
                        heading_path=[
                            "INCREASES IN VARIANCES AND ACCELERATED RESPONSES",
                            "Linkage Effects",
                        ],
                        display_heading="Linkage Effects",
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="proposition",
                        subsection="Epistasis",
                        content="Epistasis proposition.",
                        formula_references=["formula_25.12"],
                        section_level_1="INCREASES IN VARIANCES AND ACCELERATED RESPONSES",
                        section_level_2="Epistasis",
                        heading_path=[
                            "INCREASES IN VARIANCES AND ACCELERATED RESPONSES",
                            "Epistasis",
                        ],
                        display_heading="Epistasis",
                    )
                ]
            ),
        ]

        _, sections = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(
            sections,
            [
                "Chapter 25: Linkage Effects",
                "Chapter 25: Epistasis",
            ],
        )

    def test_single_l1_heading_metadata_updates_inferred_section(self):
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="derivation",
                        subsection="WHY ALL THE FOCUS ON $ h^{2} $?",
                        content="The slope is given by a formula.",
                        formula_references=["formula_15.1a"],
                        section_level_1="WHY ALL THE FOCUS ON $ h^{2} $?",
                        section_level_2=None,
                        heading_path=["WHY ALL THE FOCUS ON $ h^{2} $?"],
                        display_heading="WHY ALL THE FOCUS ON $ h^{2} $?",
                    )
                ]
            )
        ]

        _, sections = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(sections, ["Chapter 15: WHY ALL THE FOCUS ON $ h^{2} $?"])

    def test_numbered_sentence_heading_remains_under_current_section(self):
        text = (
            "# AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS\n"
            "# General Features of Long-term Selection Experiments\n"
            "1. Selection routinely results in mean phenotypes far outside the base population.\n\n"
            "# 3. Reproductive fitness usually declines as selection proceeds.\n"
            "4. Most laboratory populations approach a selection limit.\n"
        )
        formula_library = FormulaLibrary()

        blocks, _ = extract_semantic_blocks(text, "chapter25", None, formula_library)
        chunks = build_composite_chunks(blocks)
        refined_chunks, _ = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(len(refined_chunks), 1)
        self.assertEqual(refined_chunks[0].section_level_1, "AN OVERVIEW OF LONG-TERM SELECTION EXPERIMENTS")
        self.assertEqual(refined_chunks[0].section_level_2, "General Features of Long-term Selection Experiments")
        self.assertEqual(refined_chunks[0].display_heading, "General Features of Long-term Selection Experiments")
        content = " ".join(block.content for block in refined_chunks[0].blocks)
        self.assertIn("3. Reproductive fitness usually declines as selection proceeds.", content)
        self.assertIn("4. Most laboratory populations approach a selection limit.", content)

    def test_refine_chunks_for_output_canonicalizes_similar_subsections(self):
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="SELECTION SIGNATURES FROM RECENT SINGLE EVENTS",
                        content="Main section anchor.",
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="SELECTION SIGNATURES EROM RECENT SINGLE EVENTS",
                        content="OCR-variant heading should collapse to the canonical title.",
                    ),
                    SemanticBlock(
                        type="derivation",
                        subsection="HITCHHIKING AND SWEEPS",
                        content="Likelihood details are attached to 见公式(9.16a) (9.16a).",
                        formula_references=["formula_9.16a"],
                    ),
                ]
            ),
        ]

        refined_chunks, sections = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(
            refined_chunks[1].subsections[0],
            "SELECTION SIGNATURES FROM RECENT SINGLE EVENTS",
        )
        self.assertEqual(
            sections,
            [
                "Chapter 9: SELECTION SIGNATURES FROM RECENT SINGLE EVENTS",
                "Chapter 9: SELECTION SIGNATURES FROM RECENT SINGLE EVENTS",
            ],
        )
        self.assertIn("见公式(9.16a)", refined_chunks[1].blocks[1].content)
        self.assertNotIn("(9.16a)", refined_chunks[1].blocks[1].content.replace("见公式(9.16a)", ""))

    def test_refine_chunks_for_output_removes_page_suffixes_and_publisher_snippets(self):
        source_title = "Evolution and Selection of Quantitative Traits"
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="proposition",
                        subsection="SELECTION, MUTATION, AND DRIFT 177",
                        content=(
                            "Evolution and Selection of Quantitative Traits. Bruce Walsh Michael Lynch "
                            "Published 2018 by Oxford University Press. O Bruce Walsh & Michael Lynch 2018 "
                            "As discussed in Chapter 5, mutation-selection balance remains important."
                        ),
                        formula_references=["formula_7.2"],
                    )
                ]
            )
        ]

        refined_chunks, sections = refine_chunks_for_output(chunks, source_title=source_title)

        self.assertEqual(
            refined_chunks[0].subsections,
            ["SELECTION, MUTATION, AND DRIFT"],
        )
        self.assertEqual(
            sections,
            ["Chapter 7: SELECTION, MUTATION, AND DRIFT"],
        )
        self.assertNotIn("Oxford University Press", refined_chunks[0].blocks[0].content)
        self.assertNotIn("Published 2018", refined_chunks[0].blocks[0].content)
        self.assertNotIn("Bruce Walsh", refined_chunks[0].blocks[0].content)
        self.assertNotIn("Michael Lynch", refined_chunks[0].blocks[0].content)
        self.assertIn("As discussed in Chapter 5", refined_chunks[0].blocks[0].content)

    def test_refine_chunks_for_output_interpolates_section_numbers_between_neighbors(self):
        chunks = [
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="EFFECTIVE POPULATION SIZE",
                        content="Population-size overview.",
                        formula_references=["formula_3.1"],
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="NONADAPTIVE FORCES OF EVOLUTION",
                        content="Carries stale references from earlier discussion only.",
                        formula_references=["formula_3.7", "formula_2.3"],
                    )
                ]
            ),
            CompositeChunk(
                blocks=[
                    SemanticBlock(
                        type="discussion",
                        subsection="POPULATION GENETICS OF SELECTION",
                        content="Selection chapter anchor.",
                        formula_references=["formula_5.1a"],
                    )
                ]
            ),
        ]

        _, sections = refine_chunks_for_output(chunks, source_title=None)

        self.assertEqual(
            sections,
            [
                "Chapter 3: EFFECTIVE POPULATION SIZE",
                "Chapter 4: NONADAPTIVE FORCES OF EVOLUTION",
                "Chapter 5: POPULATION GENETICS OF SELECTION",
            ],
        )

    def test_build_composite_chunks_keeps_subsection_boundaries_strict(self):
        blocks = [
            SemanticBlock(
                type="discussion",
                subsection="CHAPTER 1: FIRST SECTION",
                content="First block content stays with the first subsection.",
            ),
            SemanticBlock(
                type="discussion",
                subsection="CHAPTER 1: SECOND SECTION",
                content="Second block content starts a new chunk at the subsection boundary.",
            ),
        ]

        chunks = build_composite_chunks(blocks)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].subsections, ["CHAPTER 1: FIRST SECTION"])
        self.assertEqual(chunks[1].subsections, ["CHAPTER 1: SECOND SECTION"])

    def test_split_tex_book_extracts_toc_and_chapters_one_to_nine(self):
        filler = "\n".join(f"body line {index}" for index in range(60))
        sample = (
            "Cover noise\n"
            "Contents\n"
            "I. INTRODUCTION 1\n"
            "1. CHANGES IN QUANTITATIVE TRAITS OVER TIME 3\n"
            "II. EVOLUTION AT ONE AND TWO LOCI 23\n"
            "2. NEUTRAL EVOLUTION IN ONE- AND TWO-LOCUS SYSTEMS 25\n"
            "CHAPTER I\n"
            "The Fusion of Population and Quantitative Genetics\n"
            "Real chapter one prose.\n"
            f"{filler}\n"
            "CHAPTER 2\n"
            "The Wright-Fisher Model\n"
            "Real chapter two prose.\n"
            f"{filler}\n"
            "CHAPTER 9\n"
            "Selection Signatures from Recent Single Events\n"
            "Real chapter nine prose.\n"
            f"{filler}\n"
            "CHAPTER 10\n"
            "Multiple Historical Events\n"
        )

        toc_text, chapter_segments, toc_end = split_tex_book(sample, chapter_start=1, chapter_end=9)

        self.assertIsNotNone(toc_end)
        self.assertIn("Contents", toc_text)
        self.assertIn("1. CHANGES IN QUANTITATIVE TRAITS OVER TIME 3", toc_text)
        self.assertEqual(sorted(chapter_segments.keys()), ["chapter1", "chapter2", "chapter9"])
        self.assertIn("Real chapter one prose.", chapter_segments["chapter1"])
        self.assertIn("Real chapter two prose.", chapter_segments["chapter2"])
        self.assertNotIn("CHAPTER 10", chapter_segments["chapter9"])

    def test_extract_tables_and_replace_places_known_raw_table_without_creating_text_entry(self):
        sample = (
            "Discussion before table.\n"
            "Table 5.1 Genotype frequencies after viability selection. Here, p is the frequency of allele A\n"
            "are in Hardy-Weinberg frequencies before selection.\n"
            "Genotype\n"
            "AA\n"
            "Aa\n"
            "aa\n"
            "Frequency before selection\n"
            "As shown in Table 5.1, the number of AA individuals following selection is proportional.\n"
        )

        replaced, tables = extract_tables_and_replace(
            sample,
            chapter_name="chapter5",
            known_table_ids={"5.1"},
        )

        self.assertEqual(tables, [])
        self.assertIn("[[TABLE:5.1]]", replaced)
        self.assertIn("[[SEE_TABLE:5.1]]", replaced)
        self.assertNotIn("Genotype\nAA\nAa", replaced)

    def test_extract_tables_and_replace_uses_dummy_latex_table_as_location_only(self):
        sample = (
            "We summarize key values in Table 21.6 below.\n"
            "\\begin{table}[h]\n"
            "\\centering\n"
            "\\begin{tabular}{|c|c|}\n"
            "\\hline\n"
            "Cell 1 & Cell 2 \\\\\n"
            "\\hline\n"
            "Cell 3 & Cell 4 \\\\\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\caption{Table Placeholder}\n"
            "\\end{table}\n"
            "As shown in Table 21.6, the selection intensity differs.\n"
        )

        replaced, tables = extract_tables_and_replace(
            sample,
            chapter_name="chapter21",
            known_table_ids={"21.6"},
        )

        self.assertEqual(tables, [])
        self.assertIn("[[TABLE:21.6]]", replaced)
        self.assertIn("[[SEE_TABLE:21.6]]", replaced)
        self.assertNotIn("Cell 1", replaced)
        self.assertNotIn("Cell 2", replaced)

    def test_latex_table_environment_survives_strip_pipeline_with_pre_extract(self):
        sample = (
            "As shown in Table 21.6 below.\n"
            "\\begin{table}[h]\n"
            "\\centering\n"
            "\\begin{tabular}{|c|c|}\n"
            "\\hline\n"
            "Cell 1 & Cell 2 \\\\\n"
            "\\hline\n"
            "\\end{tabular}\n"
            "\\caption{Table Placeholder}\n"
            "\\end{table}\n"
            "Table 21.6 supports this point.\n"
        )

        tex_with_placeholder, latex_tables = _extract_table_envs_and_replace(sample, "chapter21")
        stripped = strip_latex_markup(tex_with_placeholder)
        replaced, post_tables = extract_tables_and_replace(
            stripped,
            "chapter21",
            known_table_ids={"21.6"},
        )

        self.assertEqual(latex_tables, [])
        self.assertIn("[[TABLE:21.6]]", replaced)
        self.assertIn("[[SEE_TABLE:21.6]]", replaced)
        self.assertEqual(post_tables, [])

    def test_paddle_raw_table_creates_real_entry_with_bbox_not_dummy_cells(self):
        caption = "Table 25.1 Total contribution to the selection limit."
        table_html = (
            "<table><tr><td>Allele action</td><td>Total contribution</td></tr>"
            "<tr><td>additive</td><td>2a(1-p0)</td></tr></table>"
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": caption,
                            "block_bbox": [10, 10, 200, 30],
                        },
                        {
                            "block_label": "table",
                            "block_content": table_html,
                            "block_bbox": [10, 35, 220, 120],
                        },
                    ]
                }
            }
        ]

        with patch("knowledge_engineering.pipeline.process._load_paddle_raw_pages", return_value=pages):
            tables = _extract_tables_from_paddle_raw("chapter25_full/main.tex", "chapter25")

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].id, "25.1")
        self.assertEqual(tables[0].rows[0], ["Allele action", "Total contribution"])
        self.assertEqual(tables[0].source["page"], 1)
        self.assertEqual(tables[0].source["bbox"], [10, 35, 220, 120])
        self.assertEqual(tables[0].source["extraction_channel"], "paddle_raw_layout")
        self.assertNotIn("Cell 1", tables[0].html)

    def test_paddle_raw_table_reference_text_does_not_bind_numbered_table_id(self):
        table_html = "<table><tr><td>n</td><td>R</td></tr><tr><td>5</td><td>31.6</td></tr></table>"
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "text",
                            "block_content": "From Table 25.1, the selection limit becomes larger as n increases.",
                            "block_bbox": [10, 10, 220, 35],
                        },
                        {
                            "block_label": "table",
                            "block_content": table_html,
                            "block_bbox": [10, 40, 220, 120],
                        },
                    ]
                }
            }
        ]

        with patch("knowledge_engineering.pipeline.process._load_paddle_raw_pages", return_value=pages):
            tables = _extract_tables_from_paddle_raw("chapter25_full/main.tex", "chapter25")

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].id, "inline_1")
        self.assertNotEqual(tables[0].id, "25.1")

    def test_paddle_raw_numbered_caption_does_not_cross_example_boundary(self):
        formula_table = (
            "<table><tr><td>Selection Scheme</td><td>R/(sigma_A^2 i)</td></tr>"
            "<tr><td>Half-sibs, remnant seed</td><td>formula</td></tr></table>"
        )
        example_table = (
            "<table><tr><td>Selection</td><td>R/i</td><td>f=1/8</td></tr>"
            "<tr><td>Half-sib</td><td>1.581</td><td>1.111</td></tr></table>"
        )
        pages = [
            {
                "prunedResult": {
                    "parsing_res_list": [
                        {
                            "block_label": "figure_title",
                            "block_content": "Table 23.1 The response to family selection.",
                            "block_bbox": [10, 10, 220, 40],
                            "block_order": 1,
                        },
                        {
                            "block_label": "table",
                            "block_content": formula_table,
                            "block_bbox": [10, 50, 220, 120],
                            "block_order": 2,
                        },
                        {
                            "block_label": "figure_title",
                            "block_content": "Example 23.1. Using the expression summarized in Table 23.1.",
                            "block_bbox": [10, 150, 220, 180],
                            "block_order": 3,
                        },
                        {
                            "block_label": "table",
                            "block_content": example_table,
                            "block_bbox": [10, 190, 220, 260],
                            "block_order": 4,
                        },
                    ]
                }
            }
        ]

        with patch("knowledge_engineering.pipeline.process._load_paddle_raw_pages", return_value=pages):
            tables = _extract_tables_from_paddle_raw("chapter23_full/main.tex", "chapter23")

        self.assertEqual([table.id for table in tables], ["23.1", "inline_1"])
        self.assertEqual(tables[0].rows[0], ["Selection Scheme", "R/(sigma_A^2 i)"])
        self.assertEqual(tables[1].rows[0], ["Selection", "R/i", "f=1/8"])

    def test_inline_table_placeholder_assigns_table_source_unit(self):
        unit = KnowledgeUnit(
            id="chapter25_006",
            chapter="chapter25",
            section="Dynamics of Allele-frequency Change",
            subsections=["Dynamics of Allele-frequency Change"],
            source_file="chapter25_full/main.tex",
            blocks=[
                KnowledgeBlock(
                    type="discussion",
                    content="The resulting values become [[TABLE:inline_1]]",
                )
            ],
        )
        table = TableEntry(
            id="inline_1",
            label_format="Inline Table 1",
            title="The resulting values of these various quantities for 5 to 500 loci become",
            table_type="inline",
            html="<table><tr><td>n</td><td>R</td></tr></table>",
            rows=[["n", "R"], ["5", "31.6"]],
            source={"chapter": "chapter25", "page": 9},
        )

        assigned = assign_table_sources_to_units([unit], [table])

        self.assertEqual(assigned[0].source["unit_id"], "chapter25_006")
        self.assertEqual(assigned[0].source["subsection"], "Dynamics of Allele-frequency Change")

    def test_table_reference_key_scopes_numbered_tables_to_source_chapter(self):
        self.assertEqual(_table_reference_key("chapter25", "6.1"), "chapter6:6.1")
        self.assertEqual(_table_reference_key("chapter25", "25.4"), "chapter25:25.4")
        self.assertEqual(_table_reference_key("chapter25", "inline_2"), "chapter25:inline_2")

    def test_missing_local_table_stub_keeps_reference_resolvable_without_dummy_body(self):
        text = (
            "[[TABLE:11.1]]\n"
            "The components are summarized in Table 11.1, while Table 9.1 is a cross-chapter reference."
        )

        stubs = _create_missing_table_body_stubs(text, "chapter11", existing_table_ids=set())

        self.assertEqual([entry.id for entry in stubs], ["11.1"])
        self.assertEqual(stubs[0].table_type, "missing")
        self.assertEqual(stubs[0].rows, [])
        self.assertEqual(stubs[0].html, "")
        self.assertTrue(stubs[0].source["has_physical_placeholder"])
        self.assertTrue(stubs[0].source["needs_review"])

    def test_table_library_merges_globally_and_replaces_only_target_chapter(self):
        output_dir = Path.cwd() / "tmp" / "paper2latex_tests" / "table_lib_outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "table_library_merge_test.json"

        base = TableLibrary(
            tables=[
                TableEntry(
                    id="5.1",
                    label_format="Table 5.1",
                    title="old chapter5 table",
                    table_type="numbered",
                    html="<table></table>",
                    rows=[],
                    source={"chapter": "chapter5", "unit_id": "chapter5_001"},
                ),
                TableEntry(
                    id="6.1",
                    label_format="Table 6.1",
                    title="chapter6 table",
                    table_type="numbered",
                    html="<table></table>",
                    rows=[],
                    source={"chapter": "chapter6", "unit_id": "chapter6_001"},
                ),
            ]
        )
        base.save(str(path))

        loaded = TableLibrary.load(str(path))
        removed = loaded.remove_by_chapter("chapter5")
        self.assertEqual(removed, 1)

        loaded.tables.extend(
            [
                TableEntry(
                    id="5.2",
                    label_format="Table 5.2",
                    title="new chapter5 table",
                    table_type="numbered",
                    html="<table></table>",
                    rows=[],
                    source={"chapter": "chapter5", "unit_id": "chapter5_002"},
                )
            ]
        )
        loaded.save(str(path))
        reloaded = TableLibrary.load(str(path))
        chapter_ids = {(entry.source.get("chapter"), entry.id) for entry in reloaded.tables}
        self.assertIn(("chapter6", "6.1"), chapter_ids)
        self.assertIn(("chapter5", "5.2"), chapter_ids)
        self.assertNotIn(("chapter5", "5.1"), chapter_ids)

    def test_build_toc_outputs_from_text_matches_navigation_schema(self):
        toc_text = (
            "Contents\n"
            "I. INTRODUCTION 1\n"
            "1. CHANGES IN QUANTITATIVE TRAITS OVER TIME 3\n"
            "A Brief History of the Study of the Evolution of Quantitative Traits 4\n"
            "II. EVOLUTION AT ONE AND TWO LOCI 23\n"
            "2. NEUTRAL EVOLUTION IN ONE- AND TWO-LOCUS SYSTEMS 25\n"
        )

        output_dir = Path.cwd() / "tmp" / "paper2latex_tests" / f"unit_toc_outputs_{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=True)

        count = build_toc_outputs_from_text(
            toc_text=toc_text,
            output_dir=str(output_dir),
            toc_name="toc1",
            source_file="tmp/paddle_output/chapter1_full/main.tex",
            source_title="Evolution and Selection of Quantitative Traits",
        )

        self.assertGreaterEqual(count, 2)
        tree_path = output_dir / "toc1_toc_tree.json"
        self.assertTrue(tree_path.exists())
        nav_files = sorted(output_dir.glob("toc1_nav_*.json"))
        self.assertTrue(nav_files)

    def test_review_chunks_with_llm_overrides_type_and_formula_refs_per_chunk(self):
        class MockChunkClient:
            def review_chunk_semantics(self, **kwargs):
                self.kwargs = kwargs
                return {
                    "blocks": [
                        {
                            "index": 1,
                            "type": "definition",
                            "formula_reference_labels": ["6.18a"],
                            "confidence": 0.99,
                        },
                        {
                            "index": 2,
                            "type": "discussion",
                            "formula_reference_labels": [],
                            "confidence": 0.99,
                        },
                    ]
                }

        formula_library = FormulaLibrary()
        formula_library.add_formula(
            label="6.18a",
            label_format="(6.18a)",
            latex="\\Delta \\bar{W}",
            formula_type="block",
            source_unit_id="chapter6_block_001",
            source_chapter="chapter6",
            source_subsection="SECTION",
        )
        chunk = CompositeChunk(
            blocks=[
                SemanticBlock(
                    type="derivation",
                    subsection="SECTION",
                    content="From Equation (6.18a) we derive a bound.",
                    formula_references=["formula_6.18a"],
                ),
                SemanticBlock(
                    type="proposition",
                    subsection="SECTION",
                    content="This statement has no equation reference.",
                    formula_references=[],
                ),
            ]
        )
        chunks = [chunk]
        client = MockChunkClient()

        stats = _review_chunks_with_llm(
            chunks=chunks,
            chapter_name="chapter6",
            formula_library=formula_library,
            client=client,
            llm_policy={
                "phase": 3,
                "phase2_chapters": {"chapter6"},
                "phase3_chapters": {"chapter6"},
                "max_chunk_change_ratio": 1.0,
                "max_type_override_ratio": 1.0,
            },
            artifacts_dir=str(Path("tmp") / "test_runtime" / "llm_review"),
        )

        self.assertEqual(stats["attempted"], 1)
        self.assertEqual(stats["applied"], 1)
        self.assertEqual(stats["failed"], 0)
        self.assertEqual(stats["type_overrides"], 2)
        self.assertEqual(stats["formula_ref_overrides"], 0)
        self.assertEqual(chunks[0].blocks[0].type, "definition")
        self.assertEqual(chunks[0].blocks[0].formula_references, ["formula_6.18a"])
        self.assertEqual(chunks[0].blocks[1].type, "discussion")
        self.assertEqual(chunks[0].blocks[1].formula_references, [])

    def test_review_chunks_with_llm_falls_back_to_rules_on_failure(self):
        class FailingChunkClient:
            def review_chunk_semantics(self, **kwargs):
                raise RuntimeError("timeout")

        formula_library = FormulaLibrary()
        chunk = CompositeChunk(
            blocks=[
                SemanticBlock(
                    type="derivation",
                    subsection="SECTION",
                    content="Keeps original type and refs.",
                    formula_references=["formula_6.1"],
                )
            ]
        )
        chunks = [chunk]

        stats = _review_chunks_with_llm(
            chunks=chunks,
            chapter_name="chapter6",
            formula_library=formula_library,
            client=FailingChunkClient(),
            llm_policy={
                "phase": 3,
                "phase2_chapters": {"chapter6"},
                "phase3_chapters": {"chapter6"},
                "max_chunk_change_ratio": 1.0,
                "max_type_override_ratio": 1.0,
            },
            artifacts_dir=str(Path("tmp") / "test_runtime" / "llm_review"),
        )

        self.assertEqual(stats["attempted"], 1)
        self.assertEqual(stats["applied"], 0)
        self.assertEqual(stats["failed"], 1)
        self.assertTrue(stats["warnings"])
        self.assertEqual(chunks[0].blocks[0].type, "derivation")
        self.assertEqual(chunks[0].blocks[0].formula_references, ["formula_6.1"])


if __name__ == "__main__":
    unittest.main()
