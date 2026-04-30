"""
Quality reporting for conversion results.
"""

import logging
from pathlib import Path
from .core.models import QualityReport, ConversionResult


logger = logging.getLogger(__name__)


class Reporter:
    """Generate quality reports for conversion."""
    
    @staticmethod
    def generate_report_md(
        quality_report: QualityReport,
        output_dir: str,
    ) -> str:
        """
        Generate report.md file.
        
        Args:
            quality_report: Quality metrics
            output_dir: Output directory
            
        Returns:
            Path to report.md
        """
        report_path = Path(output_dir) / "report.md"
        
        lines = []
        
        # Header
        lines.append("# PDF to LaTeX Conversion Report")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **PDF Type**: {quality_report.pdf_type.value}")
        lines.append(f"- **GROBID Status**: {'✓ OK' if quality_report.grobid_ok else '✗ Failed'}")
        lines.append(f"- **Pages**: {quality_report.pages}")
        lines.append(f"- **Sections**: {quality_report.sections}")
        lines.append("")
        
        # Metrics
        lines.append("## Metrics")
        lines.append("")
        lines.append(f"- **Citations in Text**: {quality_report.citations_in_text}")
        lines.append(f"- **Bibliography Entries**: {quality_report.bib_entries}")
        lines.append(f"- **Formulas Detected**: {quality_report.formulas_total}")
        lines.append(f"- **Formulas with LaTeX**: {quality_report.formulas_latex_ok}")
        lines.append(f"- **Figures Extracted**: {quality_report.figures_extracted}")
        lines.append("")
        
        # Warnings
        if quality_report.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in quality_report.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Errors
        if quality_report.errors:
            lines.append("## Errors")
            lines.append("")
            for error in quality_report.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        if quality_report.formulas_total > 0 and quality_report.formulas_latex_ok == 0:
            lines.append("- ⚠️  No formulas were converted to LaTeX. Check formula placeholders.")
        
        if quality_report.citations_in_text < quality_report.bib_entries:
            lines.append("- ℹ️  Some bibliography entries may not be cited in text.")
        
        if not quality_report.grobid_ok:
            lines.append("- ❌ GROBID processing failed. Structure extraction may be incomplete.")
        
        if not lines[-1]:  # Remove trailing empty line
            lines.pop()
        
        # Write report
        with open(report_path, "w") as f:
            f.write("\n".join(lines))
        
        logger.info(f"Generated report: {report_path}")
        return str(report_path)
