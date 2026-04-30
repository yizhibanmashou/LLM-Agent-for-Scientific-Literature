"""
Output directory management for LaTeX projects.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class OutputManager:
    """Manage LaTeX project output structure."""
    
    def __init__(self, base_dir: str):
        """
        Initialize output manager.
        
        Args:
            base_dir: Base output directory
        """
        self.base_dir = Path(base_dir)
    
    def create_structure(self) -> dict:
        """
        Create output directory structure.
        
        Returns:
            Dictionary of directory paths
        """
        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        dirs = {
            "root": self.base_dir,
            "figures": self.base_dir / "figures",
            "equations": self.base_dir / "equations",
            "intermediate": self.base_dir / "intermediate",
            "logs": self.base_dir / "intermediate" / "logs",
        }
        
        for name, path in dirs.items():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {path}")
        
        return {k: str(v) for k, v in dirs.items()}
    
    def write_main_tex(self, content: str) -> str:
        """
        Write main.tex file.
        
        Args:
            content: LaTeX content
            
        Returns:
            Path to main.tex
        """
        main_tex_path = self.base_dir / "main.tex"
        
        with open(main_tex_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Wrote main.tex: {main_tex_path}")
        return str(main_tex_path)
    
    def write_bib(self, content: str) -> str:
        """
        Write refs.bib file.
        
        Args:
            content: BibTeX content
            
        Returns:
            Path to refs.bib
        """
        bib_path = self.base_dir / "refs.bib"
        
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Wrote refs.bib: {bib_path}")
        return str(bib_path)
    
    def save_intermediate(self, name: str, content: str) -> str:
        """
        Save intermediate file.
        
        Args:
            name: Filename
            content: Content to save
            
        Returns:
            Path to saved file
        """
        intermediate_dir = self.base_dir / "intermediate"
        file_path = intermediate_dir / name
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.debug(f"Saved intermediate file: {file_path}")
        return str(file_path)
    
    def copy_pdf(self, pdf_path: str) -> str:
        """
        Copy original PDF to output directory.
        
        Args:
            pdf_path: Source PDF path
            
        Returns:
            Destination path
        """
        dest_path = self.base_dir / "original.pdf"
        shutil.copy2(pdf_path, dest_path)
        
        logger.info(f"Copied PDF to: {dest_path}")
        return str(dest_path)
    
    def get_path(self, subdir: str, filename: str) -> str:
        """
        Get path for a file in a subdirectory.
        
        Args:
            subdir: Subdirectory name (figures, equations, etc.)
            filename: Filename
            
        Returns:
            Full path
        """
        return str(self.base_dir / subdir / filename)
