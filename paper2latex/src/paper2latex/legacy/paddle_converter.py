
"""
PaddleOCR integration for paper2latex.
Provides document structure analysis and OCR capabilities.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

try:
    try:
        from paddleocr import PPStructure
    except ImportError:
        from paddleocr.ppstructure.predict_system import PPStructureSystem as PPStructure
        
    from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

logger = logging.getLogger(__name__)

class PaddleConverter:
    def __init__(self, lang='en', use_gpu=False):
        if not PADDLE_AVAILABLE:
            raise ImportError("paddleocr not installed. Please install with: pip install paddlepaddle paddleocr")
        
        logger.info(f"Initializing PaddleOCR (lang={lang}, use_gpu={use_gpu})...")
        # Initialize PP-Structure
        # table=False to speed up if not needed, but typically we want it
        self.engine = PPStructure(
            show_log=True,
            image_orientation=True,
            lang=lang,
            use_gpu=use_gpu
        )
        logger.info("PaddleOCR initialized successfully")

    def convert_to_markdown(self, pdf_path: str, output_dir: Optional[Path] = None) -> str:
        """
        Convert PDF to Markdown using PaddleOCR.
        """
        logger.info(f"Running PaddleOCR on {pdf_path}")
        
        # PPStructure returns a list of dictionaries, one per page
        # Each page contains structure regions
        result = self.engine(pdf_path)
        
        markdown_content = []
        
        for i, page_res in enumerate(result):
            logger.info(f"Processing page {i+1}")
            
            # Sort regions (header, footer, title, text, table, figure)
            h, w, _ = page_res[0]['img'].shape
            sorted_res = sorted_layout_boxes(page_res, w)
            
            page_md = []
            
            for region in sorted_res:
                r_type = region.get('type', '').lower()
                res = region.get('res', [])
                
                text_content = ""
                if isinstance(res, list):
                    # Combine text lines
                    text_content = " ".join([line.get('text', '') for line in res])
                elif isinstance(res, tuple):
                    # Table parsing result might be tuple
                    text_content = str(res)
                
                if not text_content:
                    continue
                
                # Simple Markdown mapping
                if r_type == 'title':
                    page_md.append(f"# {text_content}")
                elif r_type == 'header':
                    # Skip headers or make them small
                    pass 
                elif r_type == 'footer':
                    pass
                elif r_type == 'figure':
                    # TODO: extract image
                    page_md.append(f"![Figure]({text_content})")
                elif r_type == 'table':
                    # TODO: Convert table HTML/structure to Markdown
                    page_md.append(f"\n{text_content}\n") # Simplified
                else: # text, etc.
                    page_md.append(text_content)
            
            markdown_content.append(f"\n\n<!-- Page {i+1} -->\n\n")
            markdown_content.append("\n\n".join(page_md))
            
        full_md = "\n".join(markdown_content)
        
        return full_md

    def extract_figures(self, pdf_path: str, output_dir: Path):
        """
        Extract figures using layout analysis.
        """
        # This can complement the existing figure extractor
        pass
