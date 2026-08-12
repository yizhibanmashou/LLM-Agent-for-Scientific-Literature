
import logging
from pathlib import Path

import pytest
from paper2latex.core.config import Config
from paper2latex.pipeline import Pipeline

logger = logging.getLogger(__name__)

# Mock the PaddleCloudConverter for integration tests to avoid network calls?
# Ideally, integration tests SHOULD test the full stack, but if we don't want to hit the API every time,
# we might want to mock ONLY the network part or allow it to be skipped.
# However, the user provided 'expect/layout_analysis.json'. This suggests we might optionally
# MOCK the Layout Analysis stage using this JSON if we want a deterministic test of the LATER stages.
# Or if we run the full pipeline, we expect the API to return something similar.
# Given 'case001' has 'expect/layout_analysis.json', it implies we might want to inject this JSON 
# to test StructureParser -> LaTeXGenerator without network flakiness.
# Let's support a mode where we mock the converter using the expected JSON if available.

@pytest.fixture
def mock_converter(monkeypatch, case_fixture, request):
    """
    Control PaddleOCR mocking based on --start-step.
    
    --start-step 1 (default): 
        - If 'expect/layout_analysis.json' exists AND no token, mock it (so we can run without token).
        - If token exists, run real OCR? Or should correct behavior be:
          Step 1 implies "Test OCR". If we want to use cached, we go to Step 2.
          BUT, previously we auto-mocked if JSON existed to be safe.
          Let's enforce: 
          - Start Step 1: Try Real if Token, else Skip or Mock? 
            -> If user explicitly asks for Pipeline test, they usually want integration.
            -> Default behavior: If JSON exists, Use Mock (deterministic). If not, Real.
            -> WAIT: User wants "Start from Step X". 
            -> "Start from Step 2" = Force Mock (Skip OCR).
            -> "Start from Step 1" = Real OCR (if possible).
    """
    case_id, input_pdf, expect_dir = case_fixture
    layout_json_path = expect_dir / "layout_analysis.json"
    
    start_step = int(request.config.getoption("--start-step") or 1)
    
    should_mock = False
    
    if start_step >= 2:
        # Step 2+ implies we SKIP OCR, so we MUST Mock it using expected JSON
        if not layout_json_path.exists():
            pytest.fail(f"--start-step {start_step} requires {layout_json_path} to exist.")
        should_mock = True
        logger.info(f"Start Step {start_step} >= 2: Forcing Mock OCR using {layout_json_path}")
        
    elif start_step == 1:
        # Step 1: We WANT to run OCR.
        # However, for CI stability, if we lack a token but have JSON, should we mock?
        # The user's request implies control.
        # If I say start-step 1, I likely WANT to verify the OCR connectivity/result if I have a token.
        # If I don't have a token, I can't run Step 1 Real.
        # So: If No Token AND JSON Exists -> Warn and Mock? Or better:
        # Let's assume Start Step 1 means "Execute connection if possible".
        # But if we have no token, we can't.
        import os
        token = os.getenv("PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN")
        if not token:
            if layout_json_path.exists():
                logger.warning("No Token for Step 1, falling back to Mock JSON.")
                should_mock = True
            else:
                 logger.warning("No Token and No JSON. Step 1 will likely fail.")
        else:
            # We have token. Should we Mock?
            # If we want a deterministic "Full Pipeline" test using cached data, we might want to mock even at step 1?
            # No, that's what Step 2 is for ("Skip OCR").
            # Step 1 implies "Test OCR".
            should_mock = False

    if should_mock and layout_json_path.exists():
        from paper2latex.converters.layout_analysis import PaddleOCR
        
        with open(layout_json_path, 'r', encoding='utf-8') as f:
            mock_data = f.read()
            
        def mock_convert(self, pdf_path, output_mode="detailed"):
            logger.info(f"Mocking PaddleOCR to simulate Start Step {start_step}")
            return mock_data
            
        monkeypatch.setattr(PaddleOCR, "convert", mock_convert)
        return True
    return False

def test_pipeline_case(case_fixture, tmp_path, mock_converter):
    """
    Run pipeline on a test case and verify output.
    """
    case_id, input_pdf, expect_dir = case_fixture
    logger.info(f"Running test case: {case_id}")
    
    # 1. Setup Config
    config = Config()
    # Ensure options are set for testing
    config.paddle_pipeline = "PaddleOCR-VL" 
    
    # 2. Run Pipeline
    pipeline = Pipeline(config)
    output_dir = tmp_path / "output"
    
    result = pipeline.run_conversion(str(input_pdf), str(output_dir))
    
    # 3. Assertions
    assert result.status == "success", f"Pipeline failed: {result.summary}"
    
    # 4. Compare Outputs
    # Check main.tex
    expected_tex = expect_dir / "main.tex"
    if expected_tex.exists():
        actual_tex = output_dir / "main.tex"
        assert actual_tex.exists(), "main.tex not generated"
        _compare_text_files(expected_tex, actual_tex)
        
    # Check refs.bib
    expected_bib = expect_dir / "refs.bib"
    if expected_bib.exists():
        actual_bib = output_dir / "refs.bib"
        assert actual_bib.exists(), "refs.bib not generated"
        _compare_text_files(expected_bib, actual_bib)
        
    # Check layout_analysis.json (only if we didn't mock it, or to verify flow)
    # If we mocked it, it's trivial, but good to check intermediate file exists
    # intermediate_json = output_dir / "intermediate" / "layout_analysis.json"
    # if intermediate_json.exists():
    #     pass

def _compare_text_files(expected_path: Path, actual_path: Path):
    """Compare two text files ignoring strict whitespace/newline diffs if possible."""
    with open(expected_path, 'r', encoding='utf-8') as f:
        expect = f.read().strip()
    with open(actual_path, 'r', encoding='utf-8') as f:
        actual = f.read().strip()
        
    # Simple assertion for now. Can be enhanced with difflib if needed.
    # To avoid failures on minor formatting changes, we might want normalization.
    assert expect == actual, f"Content mismatch for {expected_path.name}"
