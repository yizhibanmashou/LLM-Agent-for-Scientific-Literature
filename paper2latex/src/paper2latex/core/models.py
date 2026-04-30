"""
Data models for paper2latex MCP server.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PDFType(str, Enum):
    """PDF document type classification."""
    BORN_DIGITAL = "born_digital"
    SCANNED = "scanned"
    MIXED = "mixed"


class SourceType(str, Enum):
    """Source input type."""
    PATH = "path"
    URL = "url"
    ARXIV = "arxiv"
    DOI = "doi"


class OutputFormat(str, Enum):
    """Output artifact format."""
    ZIP = "zip"
    DIR = "dir"


class ConversionMode(str, Enum):
    """Conversion quality mode."""
    QUALITY = "quality"
    BALANCED = "balanced"
    FAST = "fast"


@dataclass
class BibEntry:
    """Bibliography entry from TEI."""
    xml_id: str  # e.g., "b0"
    authors: List[str]
    title: str
    year: Optional[str] = None
    venue: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    entry_type: str = "article"  # article, inproceedings, book, etc.
    raw_text: Optional[str] = None
    
    def to_bibtex_key(self) -> str:
        """Generate stable BibTeX key."""
        import hashlib
        
        # First author last name
        first_author = self.authors[0] if self.authors else "unknown"
        lastname = first_author.split()[-1].lower()
        
        # Year
        year = self.year or "nd"
        
        # Title hash (first 8 chars)
        title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8]
        
        return f"{lastname}{year}{title_hash}"


@dataclass
class FormulaCoord:
    """Formula coordinates from TEI."""
    formula_id: str
    page: int
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    latex: Optional[str] = None
    confidence: Optional[float] = None
    image_path: Optional[str] = None


@dataclass
class Figure:
    """Extracted figure."""
    figure_id: str
    page: int
    image_path: str
    caption: Optional[str] = None
    bbox: Optional[tuple[float, float, float, float]] = None


@dataclass
class Section:
    """Document section."""
    title: str
    level: int  # 1=section, 2=subsection, etc.
    content: str  # Plain text content (legacy)
    blocks: List["Block"] = field(default_factory=list) # Structure blocks
    subsections: List["Section"] = field(default_factory=list)


class BlockType(str, Enum):
    """Type of content block from layout analysis."""
    TEXT = "text"
    TITLE = "title"
    SECTION_HEADER = "section_header"
    CAPTION = "caption"
    FIGURE = "figure"
    TABLE = "table"
    FORMULA = "formula"
    LIST_ITEM = "list_item"
    HEADER = "header" # Page header
    FOOTER = "footer" # Page footer
    REFERENCE = "reference"


@dataclass
class Block:
    """Atomic content block."""
    text: str
    type: BlockType = BlockType.TEXT
    bbox: Optional[List[float]] = None # [x1, y1, x2, y2]
    page: int = 0
    confidence: float = 1.0
    html: Optional[str] = None # For tables
    image_path: Optional[str] = None # For figures
    json_width: Optional[int] = None
    json_height: Optional[int] = None


@dataclass
class Document:
    """Unified document model (replacing TEIDocument)."""
    title: str
    abstract: str
    authors: List[str]
    affiliations: List[str]
    sections: List[Section]
    references: List[BibEntry]
    figures: List[Figure]
    formulas: List[FormulaCoord]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Raw layout data
    pages: int = 0


@dataclass
class TEIDocument:
    """Parsed TEI document structure (Legacy)."""
    title: str
    abstract: str
    authors: List[str]
    sections: List[Section]
    bib_entries: List[BibEntry]
    formulas: List[FormulaCoord]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Quality metrics for conversion."""
    pdf_type: PDFType
    grobid_ok: bool
    fallback_used: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Metrics
    pages: int = 0
    sections: int = 0
    citations_in_text: int = 0
    bib_entries: int = 0
    formulas_total: int = 0
    formulas_latex_ok: int = 0
    figures_extracted: int = 0


class ConversionResult(BaseModel):
    """Result of paper2latex conversion."""
    status: str  # "ok" | "partial" | "failed"
    artifact: Dict[str, str]  # {format, path}
    summary: Dict[str, Any]
    quality_report: Dict[str, Any]
    trace: Dict[str, Any]
    
    model_config = {"arbitrary_types_allowed": True}


@dataclass
class LaTeXProject:
    """Generated LaTeX project."""
    main_tex: str
    refs_bib: str
    figures: List[Figure]
    equations: List[FormulaCoord]
    output_dir: str
