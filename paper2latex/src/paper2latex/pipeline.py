"""
Main conversion pipeline orchestrator.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF

from .core.config import Config
from .core.models import (
    PDFType,
    TEIDocument,
    QualityReport,
    ConversionResult,
    LaTeXProject,
)
from .legacy.grobid_client import GROBIDClient
from .legacy.tei_parser import TEIParser
from .converters.layout_analysis import PaddleOCR
from .generators.latex_generator import LaTeXGenerator
from .processors.formula_extractor import FormulaExtractor
from .processors.figure_extractor import FigureExtractor
from .output import OutputManager
from .reporter import Reporter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Pipeline:
    """Main conversion pipeline."""
    
    def __init__(self, config: Config):
        """
        Initialize pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.grobid = GROBIDClient(
            endpoint=config.grobid_endpoint,
            timeout=config.timeout_sec,
        )
        # Initialize Layout Analyzer (PaddleOCR)
        self.ocr_converter = PaddleOCR(config)
    
    def run_conversion(
        self,
        pdf_path: str,
        output_dir: str,
    ) -> ConversionResult:
        """Run full conversion pipeline (PaddleOCR-First)."""
        logger.info(f"Starting conversion: {pdf_path}")
        
        quality_report = QualityReport(pdf_type=PDFType.BORN_DIGITAL, grobid_ok=True)
        output_mgr = OutputManager(output_dir)
        output_mgr.create_structure()
        
        try:
            # 1. OCR (PaddleOCR Cloud)
            logger.info("Stage 1: PaddleOCR Cloud")
            # converter = self.ocr_converter
            
            # Using detailed mode to get JSON
            json_response = self.ocr_converter.convert(pdf_path, output_mode="detailed")
            
            import json
            try:
                layout_data = json.loads(json_response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON layout data. Treating content as flat text.")
                # Fallback: Create a dummy layout with one big text block
                layout_data = [[{"type": "text", "res": [{"text": json_response}]}]]
            
            # 2. Structure Parsing
            logger.info("Stage 2: Structure Parsing")
            from .converters.structure_parser import StructureParser
            parser = StructureParser()
            # Pass PDF path and output dir for figure extraction
            doc = parser.parse(layout_data, pdf_path=pdf_path, output_dir=output_dir)
            
            # 3. Reference Resolution
            logger.info("Stage 3: Reference Resolution")
            from .processors.reference_resolver import ReferenceResolver
            resolver = ReferenceResolver()
            doc = resolver.resolve(doc)
            
            # 4. LaTeX Generation
            logger.info("Stage 4: LaTeX Generation")
            from .generators.latex_generator import LaTeXGenerator
            generator = LaTeXGenerator(self.config)
            project = generator.generate(doc, output_dir)
            
            # 5. Extract additional assets (e.g. crop figures from OCR bbox)
            # TODO: Integrate FigureExtractor to use bbox from Paddle
            
            # 6. Reporting
            # Populate basic metrics
            quality_report.sections = len(doc.sections)
            quality_report.bib_entries = len(doc.references)
            quality_report.citations_in_text = 0 # TODO: Calculate from doc
            
            from .reporter import Reporter
            Reporter.generate_report_md(quality_report, output_dir)
            
            return ConversionResult(
                status="success",
                artifact={"format": "latex", "path": project.main_tex},
                summary={
                    "title": doc.title,
                    "sections": len(doc.sections),
                    "bib_entries": len(doc.references),
                },
                quality_report={},
                trace={}
            )
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            return ConversionResult(
                status="failed",
                artifact={"format": "dir", "path": output_dir},
                summary={"error": str(e)},
                quality_report={},
                trace={}
            )

    def _check_pdf(self, pdf_path: str):
        # Deprecated / minimal check
        return PDFType.BORN_DIGITAL, 0

