"""
MCP Server for paper2latex.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from mcp.server.mcpserver import MCPServer, Context

from .core.config import load_config, Config
from .core.models import SourceType, OutputFormat, ConversionMode, ConversionResult
from .pipeline import Pipeline


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create MCP server
mcp = MCPServer(name="paper2latex")


@mcp.tool()
def convert(
    source: Dict[str, str],
    output: Dict[str, str] = None,
    mode: str = "balanced",
    options: Dict[str, Any] = None,
) -> ConversionResult:
    """
    Convert a scientific paper (PDF) to a compilable LaTeX project.
    
    Args:
        source: Source specification with 'type' and 'value' keys
            - type: "path" | "url" | "arxiv" | "doi"
            - value: source identifier (file path, URL, etc.)
        output: Output specification with 'format' and optional 'path'
            - format: "zip" | "dir" (default: "zip")
            - path: output location (optional, uses temp dir if not specified)
        mode: Conversion mode "quality" | "balanced" | "fast" (default: "balanced")
        options: Optional configuration overrides
            - use_grobid: bool (default: true)
            - grobid_endpoint: str (default: "http://localhost:8070")
            - enable_coordinates: bool (default: true)
            - enable_compile_check: bool (default: false)
            - formula_ocr: str (default: "none")
            - formula_dpi: int (default: 300)
            - figure_extract: bool (default: true)
            - keep_intermediates: bool (default: true)
            - language_hint: str (default: "auto")
            - max_pages: int (optional)
            - timeout_sec: int (default: 600)
    
    Returns:
        ConversionResult with status, artifact path, summary, and quality report
    """
    logger.info(f"Converting paper: {source}")
    
    # Load configuration
    config = load_config()
    
    # Apply option overrides
    if options:
        for key, value in options.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    # Parse source
    source_type = SourceType(source.get("type", "path"))
    source_value = source["value"]
    
    # Get PDF path (for now, only support local paths)
    if source_type == SourceType.PATH:
        pdf_path = os.path.expanduser(source_value)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
    else:
        raise NotImplementedError(f"Source type {source_type} not yet supported")
    
    # Determine output directory
    if output is None:
        output = {"format": "dir"}
    
    output_format = OutputFormat(output.get("format", "dir"))
    output_path = output.get("path")
    
    if output_path is None:
        # Use temp directory
        output_dir = tempfile.mkdtemp(prefix="paper2latex_")
    else:
        output_dir = os.path.expanduser(output_path)
    
    # Run conversion pipeline
    pipeline = Pipeline(config)
    result = pipeline.run_conversion(pdf_path, output_dir)
    
    logger.info(f"Conversion result: {result.status}")
    
    return result


@mcp.tool()
def extract_bib(
    source: Dict[str, str],
    output: Dict[str, str] = None,
    options: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Extract bibliography from a paper (PDF) and output BibTeX.
    
    This is a lightweight tool that only extracts references without
    full document conversion.
    
    Args:
        source: Source specification (same as convert)
        output: Output specification with optional 'path' for .bib file
        options: Optional configuration overrides
            - grobid_endpoint: str
    
    Returns:
        Dictionary with status, bibtex_path, bib_entries count, and errors
    """
    logger.info(f"Extracting bibliography: {source}")
    
    # Load configuration
    config = load_config()
    
    # Apply option overrides
    if options:
        for key, value in options.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    # Parse source
    source_type = SourceType(source.get("type", "path"))
    source_value = source["value"]
    
    # Get PDF path
    if source_type == SourceType.PATH:
        pdf_path = os.path.expanduser(source_value)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
    else:
        raise NotImplementedError(f"Source type {source_type} not yet supported")
    
    # Determine output path
    if output and "path" in output:
        bib_path = os.path.expanduser(output["path"])
    else:
        # Use temp file
        bib_path = tempfile.mktemp(suffix=".bib", prefix="refs_")
    
    try:
        # Use new pipeline components to extract
        from .converters.layout_analysis import PaddleOCR
        from .converters.structure_parser import StructureParser
        from .generators.latex_generator import LaTeXGenerator
        
        # 1. OCR
        converter = PaddleOCR(config)
        # We need detailed mode for structure parsing
        json_response = converter.convert(pdf_path, output_mode="detailed")
        
        import json
        try:
            layout_data = json.loads(json_response)
        except json.JSONDecodeError:
            # Fallback if JSON fails
            layout_data = [[{"type": "text", "res": [{"text": json_response}]}]]
        
        # 2. Structure
        parser = StructureParser()
        doc = parser.parse(layout_data)
        
        # 3. Generate BibTeX
        latex_gen = LaTeXGenerator(config)
        bib_content = latex_gen.generate_bibtex(doc)
        
        # Write to file
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write(bib_content)
        
        return {
            "status": "ok",
            "bibtex_path": bib_path,
            "bib_entries": len(doc.references),
            "warnings": [],
            "errors": [],
        }
        
    except Exception as e:
        logger.error(f"Bibliography extraction failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "bibtex_path": None,
            "bib_entries": 0,
            "warnings": [],
            "errors": [str(e)],
        }




def main():
    """Main entry point for paper2latex CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="paper2latex MCP Server - Convert PDFs to LaTeX"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--config",
        help="Path to config file (default: ~/.config/paper2latex/config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Load config if specified
    if args.config:
        from .config import load_config
        config = load_config(args.config)
        logger.info(f"Loaded config from {args.config}")
    
    # Run MCP server
    logger.info(f"Starting paper2latex MCP server on http://{args.host}:{args.port}/mcp")
    logger.info("Press Ctrl+C to stop")
    
    try:
        mcp.run(transport="streamable-http", json_response=True)
    except KeyboardInterrupt:
        logger.info("Shutting down server")


if __name__ == "__main__":
    main()
