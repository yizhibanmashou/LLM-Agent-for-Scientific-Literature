
import logging
import json
import pytest
from pathlib import Path
from paper2latex.converters.structure_parser import StructureParser
from paper2latex.generators.latex_generator import LaTeXGenerator
from paper2latex.core.config import Config

logger = logging.getLogger(__name__)

def test_step_03_latex_generation(case_fixture, tmp_path, request):
    """
    Step 3: Test LaTeX Generation (Document -> .tex).
    CHAINS StructureParser to get Document, then tests LaTeXGenerator.
    Output is compared with 'expect/main.tex'.
    """
    case_id, input_pdf, expect_dir = case_fixture
    logger.info(f"Step 3: Testing LaTeX Generation for {case_id}")
    
    layout_json_path = expect_dir / "layout_analysis.json"
    expected_tex_path = expect_dir / "main.tex"
    
    if not layout_json_path.exists():
        pytest.skip("Missing layout_analysis.json source for step 3")
        
    # 1. Prepare Document (Reuse logic from Step 2)
    with open(layout_json_path, 'r', encoding='utf-8') as f:
        layout_data = json.load(f)
    parser = StructureParser()
    doc = parser.parse(layout_data)
    
    # 2. Execute Generator
    config = Config()
    gen = LaTeXGenerator(config) # Config optional for now?
    
    # Generate content
    tex_content = gen._generate_latex_content(doc)
    
    # 3. Verify
    # Save to tmp for inspection
    out_file = tmp_path / "main.tex"
    with open(out_file, "w", encoding='utf-8') as f:
        f.write(tex_content)
        
    # Save Output if requested
    output_path = request.config.getoption("--step-output")
    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding='utf-8') as f:
            f.write(tex_content)
        logger.info(f"Saved Step 3 output to {output_path}")
        
    if expected_tex_path.exists():
        with open(expected_tex_path, 'r', encoding='utf-8') as f:
            expected = f.read().strip()
        
        # Normalize?
        actual = tex_content.strip()
        
        # We might need looser comparison if generation involves timestamps or IDs
        # But for now, direct comparison if artifacts are stable
        assert expected == actual, f"LaTeX content mismatch. See {out_file}"
    else:
        logger.warning(f"No expected main.tex found for {case_id}, skipping comparison.")
