import json
import logging
from pathlib import Path

import pytest
from paper2latex.converters.structure_parser import StructureParser

logger = logging.getLogger(__name__)

def test_step_02_structure_parsing(case_fixture, request, tmp_path):
    """
    Step 2: Test Structure Parsing (JSON -> Document).
    Uses 'expect/layout_analysis.json' as input to verify parsing logic.
    """
    case_id, input_pdf, expect_dir = case_fixture
    logger.info(f"Step 2: Testing Structure Parsing for {case_id}")
    
    layout_json_path = expect_dir / "layout_analysis.json"
    
    if not layout_json_path.exists():
        pytest.skip(f"No layout_analysis.json found in {expect_dir}")
        
    # Load JSON
    with open(layout_json_path, 'r', encoding='utf-8') as f:
        layout_data = json.load(f)
        
    # Execute
    # Execute
    parser = StructureParser()
    # Create a temp dir for figures if not provided via output option
    # Create a temp dir for figures if not provided via output option
    if request.config.getoption("--step-output"):
        out_dir = Path(request.config.getoption("--step-output")).parent
    else:
        out_dir = tmp_path

    doc = parser.parse(layout_data, pdf_path=str(input_pdf), output_dir=str(out_dir))
    
    # Verify
    assert doc is not None
    assert doc.title is not None, "Document should have a title (even if empty string)"
    assert isinstance(doc.sections, list)
    
    # Save Output if requested
    output_path = request.config.getoption("--step-output")
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        # Simple dump of structure
        data = {
            "title": doc.title,
            "abstract": doc.abstract,
            "authors": doc.authors,
            "figures": [
                {"id": f.figure_id, "page": f.page, "box": f.bbox, "caption": f.caption, "path": f.image_path}
                for f in doc.figures
            ],
            "formulas": [
                {"id": f.formula_id, "page": f.page, "box": f.bbox, "latex": f.latex}
                for f in doc.formulas
            ],
            "sections": [
                {"title": s.title, "content_len": len(s.content), "content_preview": s.content[:200]} 
                for s in doc.sections
            ],
            "references": [r.to_bibtex_key() for r in doc.references]
        }
        with open(out_p, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved Step 2 output to {output_path}")

    # Check sections if we know what to expect. 
    # For now, just ensure we parsed *something* if the input was non-trivial.
    logger.info(f"Parsed {len(doc.sections)} sections from {case_id}")
    
    # Check Figures
    if len(doc.figures) > 0:
        logger.info(f"Found {len(doc.figures)} figures.")
        # Verify first figure has image path if input_pdf was provided
        fig = doc.figures[0]
        if fig.image_path:
            assert Path(fig.image_path).exists(), f"Figure image {fig.image_path} does not exist"
            logger.info(f"Verified figure image: {fig.image_path}")
        else:
             logger.warning("Figure found but no image path (maybe no bbox or PDF access issue)")
    else:
        logger.warning("No figures found in document.")
