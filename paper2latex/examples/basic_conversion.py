"""
Example: Basic PDF to LaTeX conversion using paper2latex MCP server.
"""

from paper2latex.server import convert


def main():
    """Convert a sample PDF to LaTeX."""
    
    # Example 1: Convert PDF to LaTeX project
    print("Example 1: Converting PDF to LaTeX...")
    
    result = convert(
        source={
            "type": "path",
            "value": "/path/to/your/paper.pdf"  # Replace with actual PDF path
        },
        output={
            "format": "dir",
            "path": "./output/example1"
        },
        mode="balanced",
        options={
            "keep_intermediates": True,
            "figure_extract": True,
        }
    )
    
    print(f"✓ Status: {result.status}")
    print(f"✓ Output: {result.artifact['path']}")
    print(f"✓ Title: {result.summary.get('title', 'N/A')}")
    print(f"✓ Sections: {result.summary['sections']}")
    print(f"✓ Bibliography entries: {result.summary['bib_entries']}")
    print(f"✓ Formulas detected: {result.summary['formulas_total']}")
    print(f"✓ Figures extracted: {result.summary['figures_extracted']}")
    print()
    
    # Example 2: Extract bibliography only
    print("Example 2: Extracting bibliography only...")
    
    from paper2latex.server import extract_bib
    
    bib_result = extract_bib(
        source={
            "type": "path",
            "value": "/path/to/your/paper.pdf"
        },
        output={
            "path": "./output/refs.bib"
        }
    )
    
    print(f"✓ Status: {bib_result['status']}")
    print(f"✓ BibTeX path: {bib_result['bibtex_path']}")
    print(f"✓ Entries: {bib_result['bib_entries']}")
    print()
    
    # Check for errors
    if result.quality_report.get('errors'):
        print("⚠️  Errors encountered:")
        for error in result.quality_report['errors']:
            print(f"  - {error}")
    
    if result.quality_report.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result.quality_report['warnings']:
            print(f"  - {warning}")


if __name__ == "__main__":
    main()
