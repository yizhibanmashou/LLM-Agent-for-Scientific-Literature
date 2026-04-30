"""
Formula extraction and processing.
"""

import logging
from pathlib import Path
from typing import List
import fitz  # PyMuPDF

from ..core.models import FormulaCoord, TEIDocument


logger = logging.getLogger(__name__)


class FormulaExtractor:
    """Extract and process formulas from PDF."""
    
    def __init__(self, pdf_path: str, output_dir: str, dpi: int = 300):
        """
        Initialize extractor.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for equation images
            dpi: DPI for rendering
        """
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
    
    def extract_formulas(self, tei_doc: TEIDocument) -> List[FormulaCoord]:
        """
        Extract formula images from PDF based on TEI coordinates.
        
        Args:
            tei_doc: Parsed TEI document with formula coordinates
            
        Returns:
            List of formula coordinates with image paths
        """
        formulas = []
        
        if not tei_doc.formulas:
            logger.info("No formulas found in TEI document")
            return formulas
        
        # Open PDF
        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            return formulas
        
        for formula in tei_doc.formulas:
            try:
                image_path = self._crop_formula(doc, formula)
                formula.image_path = image_path
                formulas.append(formula)
            except Exception as e:
                logger.warning(f"Failed to extract formula {formula.formula_id}: {e}")
                formulas.append(formula)
        
        doc.close()
        return formulas
    
    def _crop_formula(self, doc: fitz.Document, formula: FormulaCoord) -> str:
        """
        Crop formula region from PDF page.
        
        Args:
            doc: PyMuPDF document
            formula: Formula coordinates
            
        Returns:
            Path to saved image
        """
        page = doc[formula.page]
        
        # Convert bbox to PyMuPDF rect
        # TEI coordinates are in PDF units (points)
        x0, y0, x1, y1 = formula.bbox
        rect = fitz.Rect(x0, y0, x1, y1)
        
        # Render page region at high DPI
        zoom = self.dpi / 72  # 72 DPI is default
        mat = fitz.Matrix(zoom, zoom)
        
        pix = page.get_pixmap(matrix=mat, clip=rect)
        
        # Save image
        image_path = self.output_dir / f"{formula.formula_id}.png"
        pix.save(str(image_path))
        
        logger.debug(f"Saved formula image: {image_path}")
        return str(image_path)
    
    def generate_placeholder(self, formula: FormulaCoord, use_image: bool = True) -> str:
        """
        Generate LaTeX placeholder for formula.
        
        Args:
            formula: Formula coordinates
            use_image: If True and image exists, use includegraphics
            
        Returns:
            LaTeX placeholder string
        """
        if use_image and formula.image_path:
            # Use figure environment with image
            return (
                r"\begin{figure}[h]" + "\n"
                r"  \centering" + "\n"
                f"  \\includegraphics[width=0.8\\textwidth]{{{formula.image_path}}}" + "\n"
                f"  \\caption{{Formula: {formula.formula_id}}}" + "\n"
                r"\end{figure}"
            )
        else:
            # Simple placeholder
            return r"\fbox{FORMULA:" + formula.formula_id + "}"
