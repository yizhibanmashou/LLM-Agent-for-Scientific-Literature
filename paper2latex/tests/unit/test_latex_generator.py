"""
Tests for LaTeX generator.
"""

from paper2latex.core.models import BibEntry, Block, BlockType, Document, Section
from paper2latex.generators.latex_generator import LaTeXGenerator


def test_bibtex_generation():
    """Test BibTeX generation from Document model."""
    entry = BibEntry(
        xml_id="b0",
        authors=["Jane Smith", "John Doe"],
        title="A Great Paper",
        year="2021",
        venue="ICML",
        raw_text="Jane Smith, John Doe. A Great Paper. ICML 2021."
    )
    
    doc = Document(
        title="Test",
        abstract="",
        authors=[],
        affiliations=[],
        sections=[],
        references=[entry],
        figures=[],
        formulas=[],
        pages=1
    )
    
    gen = LaTeXGenerator()
    bib_str = gen.generate_bibtex(doc)
    
    # Check BibTeX format
    # The new generator uses @misc by default if type unparsed
    assert "@misc{" in bib_str
    # It generates key from author+year+title hash typically, or we check if basic fields are present
    assert "title = {A Great Paper}" in bib_str
    assert "author = {Jane Smith and John Doe}" in bib_str
    assert "year = {2021}" in bib_str


def test_latex_content_generation():
    """Test main tex content generation."""
    section = Section(
        title="Introduction",
        level=1,
        content="Hello World.",
        blocks=[
            Block(type=BlockType.TEXT, text="Hello World.")
        ],
        subsections=[]
    )
    
    doc = Document(
        title="My Paper",
        abstract="This is an abstract.",
        authors=["Author One"],
        affiliations=[],
        sections=[section],
        references=[],
        figures=[],
        formulas=[],
        pages=1
    )
    
    gen = LaTeXGenerator()
    tex_content = gen._generate_latex_content(doc)
    
    assert "\\title{My Paper}" in tex_content
    assert "\\author{Author One}" in tex_content
    assert "\\begin{abstract}" in tex_content
    assert "This is an abstract." in tex_content
    assert "\\section{Introduction}" in tex_content
    assert "Hello World." in tex_content
