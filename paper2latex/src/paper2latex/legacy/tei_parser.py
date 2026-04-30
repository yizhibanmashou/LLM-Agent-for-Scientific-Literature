"""
TEI XML parser for GROBID output.
"""

import logging
from typing import List, Optional
from lxml import etree

from ..core.models import TEIDocument, Section, BibEntry, FormulaCoord, Document


logger = logging.getLogger(__name__)


class TEIParser:
    """Parser for GROBID TEI XML."""
    
    # TEI namespace
    NS = {"tei": "http://www.tei-c.org/ns/1.0"}
    
    def __init__(self, tei_xml: str):
        """
        Initialize parser with TEI XML string.
        
        Args:
            tei_xml: TEI XML content
        """
        self.root = etree.fromstring(tei_xml.encode("utf-8"))
    
    def parse(self) -> TEIDocument:
        """
        Parse TEI XML to structured document.
        
        Returns:
            TEIDocument
        """
        return TEIDocument(
            title=self._extract_title(),
            abstract=self._extract_abstract(),
            authors=self._extract_authors(),
            sections=self._extract_sections(),
            bib_entries=self._extract_bibliography(),
            formulas=self._extract_formulas(),
            metadata=self._extract_metadata(),
        )
    
    def _extract_title(self) -> str:
        """Extract document title."""
        title_elem = self.root.find(".//tei:titleStmt/tei:title[@type='main']", self.NS)
        if title_elem is not None:
            return self._get_text(title_elem)
        return "Untitled"
    
    def _extract_abstract(self) -> str:
        """Extract abstract."""
        abstract_elem = self.root.find(".//tei:profileDesc/tei:abstract", self.NS)
        if abstract_elem is not None:
            return self._get_text(abstract_elem)
        return ""
    
    def _extract_authors(self) -> List[str]:
        """Extract author names."""
        authors = []
        author_elems = self.root.findall(".//tei:sourceDesc//tei:author/tei:persName", self.NS)
        
        for elem in author_elems:
            forename = elem.find("tei:forename", self.NS)
            surname = elem.find("tei:surname", self.NS)
            
            name_parts = []
            if forename is not None:
                name_parts.append(self._get_text(forename))
            if surname is not None:
                name_parts.append(self._get_text(surname))
            
            if name_parts:
                authors.append(" ".join(name_parts))
        
        return authors
    
    def _extract_sections(self) -> List[Section]:
        """Extract document sections."""
        sections = []
        
        # Find all divs in body
        body = self.root.find(".//tei:text/tei:body", self.NS)
        if body is None:
            return sections
        
        for div in body.findall("tei:div", self.NS):
            section = self._parse_section(div, level=1)
            if section:
                sections.append(section)
        
        return sections
    
    def _parse_section(self, div_elem, level: int) -> Optional[Section]:
        """Parse a single section div."""
        # Extract section title
        head_elem = div_elem.find("tei:head", self.NS)
        title = self._get_text(head_elem) if head_elem is not None else f"Section {level}"
        
        # Extract paragraphs
        paragraphs = []
        for p in div_elem.findall("tei:p", self.NS):
            text = self._get_text(p)
            if text:
                paragraphs.append(text)
        
        content = "\n\n".join(paragraphs)
        
        # Extract subsections
        subsections = []
        for subdiv in div_elem.findall("tei:div", self.NS):
            subsection = self._parse_section(subdiv, level + 1)
            if subsection:
                subsections.append(subsection)
        
        return Section(
            title=title,
            level=level,
            content=content,
            subsections=subsections,
        )
    
    def _extract_bibliography(self) -> List[BibEntry]:
        """Extract bibliography entries."""
        entries = []
        
        bib_list = self.root.find(".//tei:text/tei:back/tei:div[@type='references']/tei:listBibl", self.NS)
        if bib_list is None:
            return entries
        
        for bibl in bib_list.findall("tei:biblStruct", self.NS):
            entry = self._parse_bib_entry(bibl)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _parse_bib_entry(self, bibl_elem) -> Optional[BibEntry]:
        """Parse a single biblStruct element."""
        xml_id = bibl_elem.get("{http://www.w3.org/XML/1998/namespace}id", "")
        
        # Extract authors
        authors = []
        for author in bibl_elem.findall(".//tei:author/tei:persName", self.NS):
            forename = author.find("tei:forename", self.NS)
            surname = author.find("tei:surname", self.NS)
            
            name_parts = []
            if forename is not None:
                name_parts.append(self._get_text(forename))
            if surname is not None:
                name_parts.append(self._get_text(surname))
            
            if name_parts:
                authors.append(" ".join(name_parts))
        
        # Extract title
        title_elem = bibl_elem.find(".//tei:title[@level='a']", self.NS)
        if title_elem is None:
            title_elem = bibl_elem.find(".//tei:title", self.NS)
        title = self._get_text(title_elem) if title_elem is not None else "Untitled"
        
        # Extract year
        date_elem = bibl_elem.find(".//tei:date[@type='published']", self.NS)
        year = date_elem.get("when", "") if date_elem is not None else None
        if year:
            year = year[:4]  # Extract year part
        
        # Extract venue
        venue_elem = bibl_elem.find(".//tei:title[@level='j']", self.NS)
        if venue_elem is None:
            venue_elem = bibl_elem.find(".//tei:title[@level='m']", self.NS)
        venue = self._get_text(venue_elem) if venue_elem is not None else None
        
        # Extract DOI
        doi_elem = bibl_elem.find(".//tei:idno[@type='DOI']", self.NS)
        doi = self._get_text(doi_elem) if doi_elem is not None else None
        
        return BibEntry(
            xml_id=xml_id,
            authors=authors,
            title=title,
            year=year,
            venue=venue,
            doi=doi,
        )
    
    def _extract_formulas(self) -> List[FormulaCoord]:
        """Extract formula coordinates."""
        formulas = []
        
        for idx, formula_elem in enumerate(self.root.findall(".//tei:formula", self.NS)):
            # Get coordinates attribute
            coords = formula_elem.get("coords", "")
            if not coords:
                continue
            
            # Parse coordinates: "page,x0,y0,x1,y1"
            try:
                parts = coords.split(",")
                if len(parts) >= 5:
                    page = int(parts[0])
                    bbox = tuple(map(float, parts[1:5]))
                    
                    formulas.append(FormulaCoord(
                        formula_id=f"eq_{page}_{idx}",
                        page=page,
                        bbox=bbox,
                    ))
            except ValueError as e:
                logger.warning(f"Failed to parse formula coordinates: {coords}, {e}")
        
        return formulas
    
    def _extract_metadata(self) -> dict:
        """Extract document metadata."""
        metadata = {}
        
        # Extract keywords if available
        keywords = []
        for keyword in self.root.findall(".//tei:keywords/tei:term", self.NS):
            text = self._get_text(keyword)
            if text:
                keywords.append(text)
        
        if keywords:
            metadata["keywords"] = keywords
        
        return metadata
    
    def _get_text(self, elem) -> str:
        """Extract all text from an element, preserving some structure."""
        if elem is None:
            return ""
        
        # Use itertext to get all text content
        texts = []
        for text in elem.itertext():
            text = text.strip()
            if text:
                texts.append(text)
        
        return " ".join(texts)
