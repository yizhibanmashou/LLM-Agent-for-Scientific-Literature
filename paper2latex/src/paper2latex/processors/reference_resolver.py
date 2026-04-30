"""
Reference Resolver for paper2latex.

Links citation markers in text to bibliography entries.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

from ..core.models import Document, Section, Block, BlockType, BibEntry

logger = logging.getLogger(__name__)

class ReferenceResolver:
    """Resolves citations in document text to BibEntry objects."""
    
    def __init__(self, config=None):
        self.config = config

    def resolve(self, doc: Document) -> Document:
        """
        Scan document blocks and replace citation markers with LaTeX \\cite{key}.
        
        Args:
            doc: The structured document with references parsed.
            
        Returns:
            Document: The modified document with linked citations.
        """
        if not doc.references:
            logger.warning("No references found in document. Skipping resolution.")
            return doc
            
        # 1. Build map from citation ID to BibEntry
        # We assume StructureParser created references with IDs like "b1", "b2" corresponding to [1], [2]
        ref_map = {}
        for ref in doc.references:
            # Extract numeric ID if possible
            match = re.search(r'b(\d+)', ref.xml_id)
            if match:
                numeric_id = match.group(1)
                ref_map[numeric_id] = ref
        
        if not ref_map:
            logger.warning("References exist but no numeric IDs parsed (e.g. 'b1'). Skipping resolution.")
            return doc

        # 2. Iterate through all text blocks
        for section in doc.sections:
            self._process_blocks(section.blocks, ref_map)
            # Recursive handling for subsections if they exist (though currently StructureParser flat)
            # if hasattr(section, 'subsections'): ... 
                        
        return doc

    def _process_blocks(self, blocks: List[Block], ref_map: Dict[str, BibEntry]):
        """Process a list of blocks in-place."""
        for block in blocks:
            if block.type == BlockType.TEXT:
                block.text = self._replace_citations(block.text, ref_map)

    def _replace_citations(self, text: str, ref_map: Dict[str, BibEntry]) -> str:
        """Replace citation markers with \\cite{key}."""
        if not text: return ""

        # Strategy 1: Replace simple [1]
        def replace_single(match):
            full_str = match.group(0)
            ref_id = match.group(1)
            if ref_id in ref_map:
                entry = ref_map[ref_id]
                try:
                    key = entry.to_bibtex_key() # Assume BibEntry has this method
                    return f"\\cite{{{key}}}"
                except Exception:
                    return full_str
            return full_str

        # Look for [1], [23]
        text = re.sub(r'\[(\d+)\]', replace_single, text)
        
        # Strategy 2: Replace ranges [1-3] or lists [1, 2]
        # This is harder to do perfectly with regex in one go for arbitrary complexity.
        # But we can try to handle comma lists like [1, 2]
        
        # TODO: Advanced citation patterns
        
        return text
