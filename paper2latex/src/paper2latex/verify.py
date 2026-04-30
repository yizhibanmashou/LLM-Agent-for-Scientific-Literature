"""
Simple verification script to check the MCP server implementation.

Run this to verify the basic structure is correct.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from moss.mcps.pdf2latex import mcp
        print("✓ MCP server imported successfully")
        
        from moss.mcps.pdf2latex.models import (
            PDFType, TEIDocument, BibEntry, ConversionResult
        )
        print("✓ Data models imported successfully")
        
        from moss.mcps.pdf2latex.config import Config, load_config
        print("✓ Configuration module imported successfully")
        
        from moss.mcps.pdf2latex.grobid_client import GROBIDClient
        print("✓ GROBID client imported successfully")
        
        from moss.mcps.pdf2latex.tei_parser import TEIParser
        print("✓ TEI parser imported successfully")
        
        from moss.mcps.pdf2latex.latex_generator import LaTeXGenerator
        print("✓ LaTeX generator imported successfully")
        
        from moss.mcps.pdf2latex.pipeline import Pipeline
        print("✓ Pipeline imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_bib_key_generation():
    """Test BibTeX key generation."""
    print("\nTesting BibTeX key generation...")
    
    try:
        from moss.mcps.pdf2latex.models import BibEntry
        
        entry = BibEntry(
            xml_id="b0",
            authors=["John Doe", "Jane Smith"],
            title="A Test Paper",
            year="2020",
        )
        
        key = entry.to_bibtex_key()
        print(f"✓ Generated BibTeX key: {key}")
        
        # Verify key format
        assert key.startswith("doe"), "Key should start with first author's last name"
        assert "2020" in key, "Key should contain year"
        
        print("✓ BibTeX key format correct")
        return True
    except Exception as e:
        print(f"✗ BibTeX key generation failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from moss.mcps.pdf2latex.config import Config
        
        config = Config()
        print(f"✓ Default config created")
        print(f"  - GROBID endpoint: {config.grobid_endpoint}")
        print(f"  - Formula DPI: {config.formula_dpi}")
        print(f"  - Timeout: {config.timeout_sec}s")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("paper2latex MCP Server Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_bib_key_generation,
        test_config,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All verification tests passed!")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
