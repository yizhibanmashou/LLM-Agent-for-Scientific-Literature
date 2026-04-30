"""
Structure Parser for paper2latex.

Converts PaddleOCR JSON output into a structured Document model.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF

from ..core.models import (
    Document, Section, Block, BlockType, 
    BibEntry, Figure, FormulaCoord
)

logger = logging.getLogger(__name__)

class StructureParser:
    """Parses PaddleOCR layout JSON into a Document model."""
    
    def __init__(self, config=None):
        self.config = config

    def parse(
        self, 
        json_data: List[Any], 
        pdf_path: Optional[str] = None, 
        output_dir: Optional[str] = None
    ) -> Document:
        """
        Parse PaddleOCR output into a Document.
        
        Args:
            json_data: List of pages (dicts) or layout elements.
            pdf_path: Path to source PDF (required for image extraction).
            output_dir: Directory to save extracted images.
            
        Returns:
            Document: Structured document model.
        """
        
        # 1. Flatten into sequential Blocks
        all_blocks = self._flatten_to_blocks(json_data)
        
        # Initialize Document
        doc = Document(
            title="Untitled",
            abstract="",
            authors=[],
            affiliations=[],
            sections=[],
            references=[],
            figures=[],
            formulas=[],
            pages=len(json_data)
        )
        
        # 2. Extract Metadata (Title, Authors, Abstract)
        content_blocks = self._extract_metadata(doc, all_blocks)
        
        # Open PDF for extraction if available
        pdf_doc = None
        if pdf_path:
            try:
                pdf_doc = fitz.open(pdf_path)
            except Exception as e:
                logger.error(f"Failed to open PDF for image extraction: {e}")
                
        # Prepare figures output directory
        figures_dir = None
        if output_dir:
            figures_dir = Path(output_dir) / "figures"
            figures_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Group into Sections (and extract Figures)
        self._group_into_sections(doc, content_blocks, pdf_doc, figures_dir)
        
        if pdf_doc:
            pdf_doc.close()
            
        return doc

    def _flatten_to_blocks(self, json_data: List[Any]) -> List[Block]:
        """Convert varied JSON structure into flat list of Block objects."""
        blocks = []
        
        for page_idx, page_item in enumerate(json_data):
            # Page item could be a list (old format) or dict (new format)
            items = []
            page_w = None
            page_h = None
            
            if isinstance(page_item, dict):
                # Look for common content keys
                items = page_item.get("regions", []) or \
                        page_item.get("layout_dets", []) or \
                        page_item.get("res", []) or \
                        page_item.get("parsing_res_list", [])
                
                # Capture dimensions
                page_w = page_item.get("width")
                page_h = page_item.get("height")
                
            elif isinstance(page_item, list):
                items = page_item
            else:
                continue
                
            for item in items:
                # Handle different field names
                # Priority: block_content (Paddle cloud), text, ocr_text
                text = item.get("block_content") or item.get("text") or item.get("ocr_text") or ""
                # Some formats nest text in 'res' list
                if not text and "res" in item and isinstance(item["res"], list):
                    text = " ".join([r.get("text", "") for r in item["res"]])
                    
                bbox = item.get("bbox") or item.get("block_bbox") or []
                
                # Determine type: check 'block_label', 'label', then 'type'
                type_str = item.get("block_label") or item.get("label") or item.get("type") or "text"
                score = item.get("score", 1.0)
                
                block = Block(
                    text=text,
                    type=self._map_block_type(type_str),
                    bbox=bbox,
                    page=page_idx + 1,
                    confidence=score,
                    json_width=page_w,
                    json_height=page_h
                )
                blocks.append(block)
                
        return blocks

    def _map_block_type(self, type_str: str) -> BlockType:
        """Map raw PaddleOCR type string to BlockType enum."""
        type_str = type_str.lower()
        
        # Specific mappings first
        if "doc_title" in type_str: return BlockType.TITLE
        if "figure_title" in type_str: return BlockType.CAPTION
        if "paragraph_title" in type_str: return BlockType.SECTION_HEADER # Heuristic? Or Text?
        
        # Section Header
        if "header" in type_str and "image" not in type_str: 
            # Paddle "header" usually means Page Header, but current code mapped it to SECTION_HEADER.
            # Let's keep existing behavior if it was intentional, BUT "header_image" should probably be HEADER (ignored content)
            # Actually, let's map "header" to HEADER (Page Header) to avoid it being section text?
            # Existing code: if "header" in type_str: return BlockType.SECTION_HEADER
            # If we change this, we might break section detection if it relies on "header".
            # But let's assume "header" = Page Header.
            return BlockType.HEADER
            
        if "footer" in type_str: return BlockType.FOOTER
        
        # Content types
        if "image" in type_str: return BlockType.FIGURE
        if "chart" in type_str: return BlockType.FIGURE
        if "figure" in type_str: return BlockType.FIGURE
        
        if "title" in type_str: return BlockType.TITLE # Fallback for other titles
        
        if "table" in type_str: return BlockType.TABLE
        if "formula" in type_str or "equation" in type_str: return BlockType.FORMULA
        if "list" in type_str: return BlockType.LIST_ITEM
        if "reference" in type_str: return BlockType.REFERENCE
        if "caption" in type_str: return BlockType.CAPTION
        if "text" in type_str: return BlockType.TEXT
        return BlockType.TEXT

    def _extract_metadata(self, doc: Document, blocks: List[Block]) -> List[Block]:
        """
        Extract Title/Authors/Abstract from the beginning of blocks.
        Returns the remaining blocks that are effectively "content".
        """
        if not blocks:
            return []
            
        start_idx = 0
        
        # 1. Find Title (First TITLE block or first block if not found)
        title_found = False
        for i in range(min(10, len(blocks))):
            if blocks[i].type == BlockType.TITLE:
                doc.title = blocks[i].text
                start_idx = i + 1
                title_found = True
                break
        
        if not title_found and blocks:
            # Fallback: first block is title
            doc.title = blocks[0].text
            blocks[0].type = BlockType.TITLE
            start_idx = 1
            
        # 2. Find Abstract Start
        abstract_start_idx = -1
        # Scan next 30 blocks for abstract keyword
        for i in range(start_idx, min(start_idx + 30, len(blocks))):
            text_lower = blocks[i].text.lower().strip()
            if "abstract" in text_lower or text_lower.startswith("abstract"):
                abstract_start_idx = i
                break
        
        # 3. Authors (Between Title and Abstract)
        if abstract_start_idx > start_idx:
            # blocks between title and abstract are likely authors or affiliations
            for i in range(start_idx, abstract_start_idx):
                text = blocks[i].text.strip()
                if len(text) > 2 and "@" not in text: 
                     doc.authors.append(text)
                elif "@" in text:
                     doc.affiliations.append(text)
                     
        # 4. Extract Abstract
        if abstract_start_idx != -1:
             abstract_parts = []
             i = abstract_start_idx
             while i < len(blocks):
                 b = blocks[i]
                 text_lower = b.text.lower().strip()
                 
                 # Stop if we hit a Section Header OR "Introduction" (but allow the abstract header itself)
                 is_intro = (i > abstract_start_idx and (text_lower.startswith("1. intro") or text_lower == "introduction"))
                 if (i > abstract_start_idx and b.type == BlockType.SECTION_HEADER) or is_intro:
                     content_start_idx = i
                     break
                 
                 # Clean "Abstract" prefix
                 if i == abstract_start_idx:
                      clean = re.sub(r'^abstract[:\.]?\s*', '', b.text, flags=re.IGNORECASE)
                      if clean: abstract_parts.append(clean)
                 else:
                      abstract_parts.append(b.text)
                 i += 1
                 content_start_idx = i
             
             doc.abstract = " ".join(abstract_parts)
        else:
             content_start_idx = start_idx

        return blocks[content_start_idx:]

        return blocks[content_start_idx:]

    def _group_into_sections(
        self, 
        doc: Document, 
        blocks: List[Block],
        pdf_doc: Optional[fitz.Document] = None,
        figures_dir: Optional[Path] = None
    ):
        """Group blocks into Sections based on headers."""
        
        # Create a default section for content before the first header
        current_section = Section(title="Introduction", level=1, content="")
        doc.sections.append(current_section)
        
        for b in blocks:
            # Check if this block is a new Section Header
            # Logic: Explicit type OR (Text type AND regex match like "1. Introduction")
            is_header = False
            if b.type == BlockType.SECTION_HEADER:
                is_header = True
            elif b.type == BlockType.TEXT:
                # Heuristic: Starts with number and capital letter, short length
                if len(b.text) < 100 and re.match(r'^\d+\.?\s+[A-Z]', b.text):
                    is_header = True
            
            # Special handling for References header
            if "references" == b.text.lower().strip() or "bibliography" == b.text.lower().strip():
                # Switch to a "References" section
                is_header = True
                
            if is_header:
                # Avoid empty sections if previous was empty (unlikely duplicate)
                if not current_section.content.strip() and not current_section.blocks:
                     current_section.title = b.text
                else:
                    current_section = Section(title=b.text, level=1, content="")
                    doc.sections.append(current_section)
            else:
                # Add to current section
                current_section.blocks.append(b)
                
                # Extract structured elements
                if b.type == BlockType.FIGURE:
                    fig_id = f"fig_{len(doc.figures)}"
                    image_path = None
                    
                    # Extract Image if possible
                    if pdf_doc and figures_dir and b.bbox:
                        try:
                            page_idx = b.page - 1 # 0-indexed for fitz, 1-indexed for blocks
                            if 0 <= page_idx < len(pdf_doc):
                                page = pdf_doc[page_idx]
                                
                                # Calculate scaling if JSON pag dims are known
                                scale_x = 1.0
                                scale_y = 1.0
                                if b.json_width and b.json_height:
                                    pdf_rect = page.rect
                                    if b.json_width > 0:
                                        scale_x = pdf_rect.width / b.json_width
                                    if b.json_height > 0:
                                        scale_y = pdf_rect.height / b.json_height
                                        
                                # Scale the bbox
                                x1, y1, x2, y2 = b.bbox
                                scaled_bbox = fitz.Rect(
                                    x1 * scale_x,
                                    y1 * scale_y,
                                    x2 * scale_x,
                                    y2 * scale_y
                                )
                                
                                # Clip to page
                                scaled_bbox = scaled_bbox & page.rect
                                
                                pix = page.get_pixmap(clip=scaled_bbox, dpi=300)
                                
                                # Save
                                output_filename = f"{fig_id}.png"
                                save_path = figures_dir / output_filename
                                pix.save(str(save_path))
                                image_path = str(save_path)
                        except Exception as e:
                            logger.warning(f"Failed to extract figure {fig_id}: {e}")
                    
                    fig = Figure(
                        figure_id=fig_id,
                        page=b.page,
                        image_path=image_path,
                        bbox=tuple(b.bbox) if b.bbox else None,
                        caption=""
                    )
                    doc.figures.append(fig)

                elif b.type == BlockType.CAPTION:
                     current_section.content += f"\n[CAPTION: {b.text}]\n"
                     # Heuristic: Attach to last figure if on same page
                     if doc.figures and doc.figures[-1].page == b.page:
                         doc.figures[-1].caption = b.text
                         
                elif b.type == BlockType.FORMULA:
                     current_section.content += f"\n$$ {b.text} $$\n"
                     f_coord = FormulaCoord(
                         formula_id=f"eq_{len(doc.formulas)}",
                         page=b.page,
                         bbox=tuple(b.bbox) if b.bbox else (0,0,0,0),
                         latex=b.text
                     )
                     doc.formulas.append(f_coord)
                
                elif b.type == BlockType.REFERENCE or (current_section.title.lower().startswith("ref") and b.type == BlockType.LIST_ITEM):
                    self._parse_bib_entry(doc, b)

                else:
                    # Text / List Item
                    current_section.content += b.text + "\n"

    def _parse_bib_entry(self, doc: Document, block: Block):
        """Parse a block as a bibliography entry."""
        text = block.text.strip()
        if not text: return
        
        # Check for [1] or 1. pattern
        match = re.match(r'^\[?(\d+)\]?[\.\s]*(.*)', text)
        if match:
            ref_id = match.group(1)
            content = match.group(2)
            
            # Try to extract year
            year_match = re.search(r'\((\d{4})\)|[\.,]\s+(\d{4})[a-z]?[\.,]', content)
            year = year_match.group(1) or year_match.group(2) if year_match else None
            
            # Heuristic for authors (first part before title/year)
            # This is very rough
            
            doc.references.append(BibEntry(
                xml_id=f"b{ref_id}",
                authors=[], # TODO: improved author parsing
                title=content[:50] + "...",
                year=year,
                raw_text=content
            ))
