"""
Main conversion pipeline orchestrator.
"""

import logging
import os
import tempfile
import json
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
            json_response = self.ocr_converter.convert(pdf_path, output_mode="detailed")

            try:
                layout_data = json.loads(json_response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON layout data. Treating content as flat text.")
                layout_data = [[{"type": "text", "res": [{"text": json_response}]}]]
            self._write_paddle_intermediates(output_dir, layout_data)

            # 2. Structure Parsing
            logger.info("Stage 2: Structure Parsing")
            from .converters.structure_parser import StructureParser
            parser = StructureParser()
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

            # 5. Reporting
            quality_report.sections = len(doc.sections)
            quality_report.bib_entries = len(doc.references)
            quality_report.citations_in_text = 0

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

    def _write_paddle_intermediates(self, output_dir: str, layout_data) -> None:
        """Persist PaddleOCR raw layout evidence beside main.tex."""
        intermediate_dir = Path(output_dir) / "intermediate"
        intermediate_dir.mkdir(parents=True, exist_ok=True)

        raw_response_path = intermediate_dir / "paddle_raw_response.json"
        with raw_response_path.open("w", encoding="utf-8") as file:
            json.dump(layout_data, file, ensure_ascii=False, indent=2)

        raw_api_response_path = intermediate_dir / "paddle_raw_api_response.json"
        with raw_api_response_path.open("w", encoding="utf-8") as file:
            json.dump(layout_data, file, ensure_ascii=False, indent=2)

        raw_tool_response = getattr(self.ocr_converter, "last_raw_response", None)
        if raw_tool_response is not None:
            tool_response_path = intermediate_dir / "paddle_mcp_tool_response.json"
            with tool_response_path.open("w", encoding="utf-8") as file:
                json.dump(raw_tool_response, file, ensure_ascii=False, indent=2)

    def _check_pdf(self, pdf_path: str):
        # Deprecated / minimal check
        return PDFType.BORN_DIGITAL, 0

