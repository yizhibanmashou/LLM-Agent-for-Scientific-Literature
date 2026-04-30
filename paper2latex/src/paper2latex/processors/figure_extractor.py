"""
Figure extraction from PDF.
"""

import logging
from pathlib import Path
from typing import List
import fitz  # PyMuPDF

from ..core.models import Figure


logger = logging.getLogger(__name__)


class FigureExtractor:
    """Extract figures (images) from PDF."""
    
    def __init__(self, pdf_path: str, output_dir: str):
        """
        Initialize extractor.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for figure images
        """
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_figures(self) -> List[Figure]:
        """
        Extract embedded images from PDF.
        
        Returns:
            List of extracted figures
        """
        figures = []
        
        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            return figures
        
        figure_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get images on page
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    
                    # Extract image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Save image
                    figure_id = f"fig_{page_num:03d}_{img_index:03d}"
                    image_path = self.output_dir / f"{figure_id}.{image_ext}"
                    
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    figures.append(Figure(
                        figure_id=figure_id,
                        page=page_num,
                        image_path=str(image_path),
                    ))
                    
                    figure_count += 1
                    logger.debug(f"Extracted figure: {image_path}")
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image on page {page_num}: {e}")
        
        doc.close()
        logger.info(f"Extracted {figure_count} figures")
        
        return figures
