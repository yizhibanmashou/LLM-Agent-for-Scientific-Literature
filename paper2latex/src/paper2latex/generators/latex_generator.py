"""
LaTeX Generator for paper2latex.

Converts structured Document model to LaTeX source code.
"""

import logging
import os
from pathlib import Path
from typing import List

from ..core.models import Document, Section, Block, BlockType, BibEntry, Figure, FormulaCoord, LaTeXProject

logger = logging.getLogger(__name__)

class LaTeXGenerator:
    """Generates LaTeX project from Document model."""
    
    def __init__(self, config=None):
        self.config = config

    def generate(self, doc: Document, output_dir: str) -> LaTeXProject:
        """
        Generate main.tex and refs.bib in output_dir.
        
        Args:
            doc: Structured document model.
            output_dir: Target directory path.
            
        Returns:
            List[str]: Paths to generated files.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # 1. Generate refs.bib
        bib_content = self.generate_bibtex(doc)
        bib_file = out_path / "refs.bib"
        with open(bib_file, "w", encoding="utf-8") as f:
            f.write(bib_content)
        generated_files.append(str(bib_file))
        
        # 2. Generate main.tex
        tex_content = self._generate_latex_content(doc)
        tex_file = out_path / "main.tex"
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_content)
        generated_files.append(str(tex_file))
        
        return LaTeXProject(
            main_tex=str(tex_file),
            refs_bib=str(bib_file),
            figures=doc.figures,
            equations=doc.formulas,
            output_dir=output_dir
        )

    def generate_bibtex(self, doc: Document) -> str:
        """Generate BibTeX content."""
        lines = []
        for ref in doc.references:
            key = ref.to_bibtex_key()
            # Basic fallback if structured data is missing
            # Use @misc for now as we don't have full type parsing yet
            entry_type = "misc" 
            
            lines.append(f"@{entry_type}{{{key},")
            if ref.title:
                lines.append(f"  title = {{{ref.title}}},")
            if ref.authors:
                formatted_authors = " and ".join(ref.authors)
                lines.append(f"  author = {{{formatted_authors}}},")
            if ref.year:
                lines.append(f"  year = {{{ref.year}}},")
            
            # Store raw text as note effectively
            if ref.raw_text:
                 # Escape potential latex chars?
                 clean_raw = ref.raw_text.replace("{", "\\{").replace("}", "\\}")
                 lines.append(f"  note = {{{clean_raw}}},")
                 
            lines.append("}\n")
            
        return "\n".join(lines)

    def _generate_latex_content(self, doc: Document) -> str:
        """Generate full LaTeX content."""
        
        # Preamble
        latex = [
            "\\documentclass{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{amsmath, amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "\\usepackage{geometry}",
            "\\geometry{a4paper, margin=1in}",
            "",
            f"\\title{{{doc.title}}}",
            f"\\author{{{', '.join(doc.authors) if doc.authors else 'Unknown Authors'}}}",
            "\\date{}",
            "",
            "\\begin{document}",
            "\\maketitle",
            "",
            "\\begin{abstract}",
            doc.abstract,
            "\\end{abstract}",
            ""
        ]
        
        # Sections
        for section in doc.sections:
            latex.extend(self._render_section(section))
            
        # Bibliography
        if doc.references:
            latex.extend([
                "",
                "\\bibliographystyle{plain}",
                "\\bibliography{refs}",
                ""
            ])
            
        latex.append("\\end{document}")
        
        return "\n".join(latex)

    def _render_section(self, section: Section) -> List[str]:
        """Render a section and its blocks."""
        lines = []
        
        # Section Header
        if section.level == 1:
            lines.append(f"\\section{{{section.title}}}")
        elif section.level == 2:
            lines.append(f"\\subsection{{{section.title}}}")
        elif section.level == 3:
            lines.append(f"\\subsubsection{{{section.title}}}")
            
        # Blocks
        for block in section.blocks:
            lines.extend(self._render_block(block))
            
        # Recursive subsections
        for subsec in section.subsections:
            lines.extend(self._render_section(subsec))
            
        return lines

    def _render_block(self, block: Block) -> List[str]:
        """Render individual content block."""
        if block.type == BlockType.TEXT:
            # Basic text with newline handling
            # Ensure paragraph breaks
            return [block.text, ""]
            
        elif block.type == BlockType.FIGURE:
            # Figure environment
            # Placeholder image if path empty
            img_path = block.image_path if block.image_path else "example-image"
            caption = block.text if block.text else "Figure"
            
            return [
                "\\begin{figure}[h]",
                "\\centering",
                f"\\includegraphics[width=0.8\\linewidth]{{{img_path}}}",
                f"\\caption{{{caption}}}",
                "\\end{figure}",
                ""
            ]
            
        elif block.type == BlockType.FORMULA:
            # Equation environment
            latex_code = block.text # Should be LaTeX code if detected
            if not latex_code or "$" not in latex_code:
                 return [
                     "\\begin{equation}",
                     "% TODO: OCR Formula",
                     "E = mc^2", 
                     "\\end{equation}",
                     ""
                 ]
            
            # Strip $ delimiters if present for equation environment
            clean_latex = latex_code.strip().strip("$")
            return [
                "\\begin{equation}",
                clean_latex,
                "\\end{equation}",
                ""
            ]
            
        elif block.type == BlockType.TABLE:
             # Basic table placeholder
             return [
                 "\\begin{table}[h]",
                 "\\centering",
                 "\\begin{tabular}{|c|c|}",
                 "\\hline",
                 "Cell 1 & Cell 2 \\\\",
                 "\\hline",
                 "Cell 3 & Cell 4 \\\\",
                 "\\hline",
                 "\\end{tabular}",
                 "\\caption{Table Placeholder}",
                 "\\end{table}",
                 ""
             ]

        return []
