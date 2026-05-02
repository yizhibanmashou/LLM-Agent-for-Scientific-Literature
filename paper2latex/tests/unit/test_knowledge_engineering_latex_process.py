import unittest
from pathlib import Path
from uuid import uuid4

from knowledge_engineering.runtime import (
    CompositeChunk,
    build_composite_chunks,
    FormulaLibrary,
    SemanticBlock,
    TableEntry,
    TableLibrary,
)
from knowledge_engineering.process import (
    _extract_table_envs_and_replace,
    _review_chunks_with_llm,
    build_toc_outputs_from_text,
    derive_chapter_name,
    extract_tables_and_replace,
    preprocess_extracted_text,
    refine_chunks_for_output,
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

    def test_derive_chapter_name_from_chapter_full_dir(self):
        tex_path = str(Path("data") / "paddle_output" / "chapter6_full" / "main.tex")
        self.assertEqual(derive_chapter_name(tex_path), "chapter6")

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

    def test_extract_tables_and_replace_creates_placeholders_and_table_entries(self):
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

        replaced, tables = extract_tables_and_replace(sample, chapter_name="chapter5")

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].id, "5.1")
        self.assertIn("[[TABLE:5.1]]", replaced)
        self.assertIn("[[SEE_TABLE:5.1]]", replaced)
        self.assertNotIn("Genotype\nAA\nAa", replaced)
        self.assertGreaterEqual(len(tables[0].rows), 4)

    def test_extract_tables_and_replace_parses_latex_table_environment(self):
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

        replaced, tables = extract_tables_and_replace(sample, chapter_name="chapter21")

        ids = [entry.id for entry in tables]
        self.assertIn("21.6", ids)
        self.assertIn("[[TABLE:21.6]]", replaced)
        self.assertIn("[[SEE_TABLE:21.6]]", replaced)
        table = next(entry for entry in tables if entry.id == "21.6")
        self.assertGreaterEqual(len(table.rows), 2)
        self.assertIn("Cell 1", table.html)

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
        replaced, post_tables = extract_tables_and_replace(stripped, "chapter21")

        self.assertIn("[[TABLE:21.6]]", replaced)
        self.assertTrue(any(entry.id == "21.6" for entry in latex_tables))
        self.assertEqual(post_tables, [])

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
            artifacts_dir=str(Path("tmp") / "test_artifacts" / "llm_review"),
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
            artifacts_dir=str(Path("tmp") / "test_artifacts" / "llm_review"),
        )

        self.assertEqual(stats["attempted"], 1)
        self.assertEqual(stats["applied"], 0)
        self.assertEqual(stats["failed"], 1)
        self.assertTrue(stats["warnings"])
        self.assertEqual(chunks[0].blocks[0].type, "derivation")
        self.assertEqual(chunks[0].blocks[0].formula_references, ["formula_6.1"])


if __name__ == "__main__":
    unittest.main()
