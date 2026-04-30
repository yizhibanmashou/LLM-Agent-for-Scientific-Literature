
import sys
from pathlib import Path

import pytest


PAPER2LATEX_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PAPER2LATEX_ROOT.parent
for path in (PAPER2LATEX_ROOT / "src", WORKSPACE_ROOT):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--case",
        action="store",
        default=None,
        help="Run specific test case from tests/fixtures/ (e.g., case001)"
    )
    parser.addoption(
        "--start-step",
        action="store",
        default="1",
        help="Start from processing step (1=Layout/OCR, 2=Structure, 3=LaTeX). Default 1."
    )
    parser.addoption(
        "--step-output",
        action="store",
        default=None,
        help="Path to save the output of the step test (e.g., --step-output result.json)"
    )

@pytest.fixture
def test_case(request):
    """
    Fixture that yields test cases from tests/fixtures/.
    Returns tuple: (case_id, input_pdf_path, expect_dir_path)
    """
    selected_case = request.config.getoption("--case")
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    cases = []
    if fixtures_dir.exists():
        for case_dir in fixtures_dir.iterdir():
            if case_dir.is_dir() and (selected_case is None or case_dir.name == selected_case):
                input_pdf = case_dir / "input.pdf"
                expect_dir = case_dir / "expect"
                if input_pdf.exists() and expect_dir.exists():
                    cases.append((case_dir.name, input_pdf, expect_dir))
    
    # We want to parametrize tests at collection time ideally, but for simplicity
    # and since we might want dynamic discovery, we can return the list 
    # OR we can use pytest_generate_tests to parameterize.
    # A simple fixture returning the list allows the test to iterate, but that makes 1 test for all.
    # Better: use pytest_generate_tests in the test file or here.
    
    return cases

def pytest_generate_tests(metafunc):
    """Generate tests based on fixtures directory."""
    if "case_fixture" in metafunc.fixturenames:
        selected_case = metafunc.config.getoption("--case")
        fixtures_dir = Path(__file__).parent / "fixtures"
        
        argvalues = []
        ids = []
        
        if fixtures_dir.exists():
            # Sort for stability
            for case_dir in sorted(fixtures_dir.iterdir()):
                if case_dir.is_dir():
                    if selected_case and case_dir.name != selected_case:
                        continue
                        
                    input_pdf = case_dir / "input.pdf"
                    expect_dir = case_dir / "expect"
                    
                    if input_pdf.exists() and expect_dir.exists():
                        argvalues.append((case_dir.name, input_pdf, expect_dir))
                        ids.append(case_dir.name)
        
        metafunc.parametrize("case_fixture", argvalues, ids=ids)
