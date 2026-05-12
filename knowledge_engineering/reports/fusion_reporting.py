"""Summary and artifact helpers for structured fusion reports."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from knowledge_engineering.core.common import utc_now_iso, write_json, write_jsonl
from knowledge_engineering.core.runtime import FormulaLibrary, TableLibrary
from knowledge_engineering.processors.ocr_evidence import OCREvidenceIndex


def build_structured_fusion_summary(
    *,
    structured_dir: str | Path,
    output_dir: str | Path,
    glmocr_dir: str | Path | None,
    paddle_output_dir: str | Path | None,
    reference_structured_dir: str | Path | None,
    dry_run: bool,
    include_review: bool,
    replace_weaker_tables: bool,
    enable_glm_prose_repair: bool,
    enable_ocr_table_evidence: bool,
    enable_ocr_table_repair: bool,
    auto_threshold: float,
    review_threshold: float,
    max_window_paragraphs: int,
    units_scanned: int,
    blocks_after_fusion: int,
    block_stats: Counter[str],
    table_stats: Counter[str],
    table_binding_stats: Counter[str],
    formula_stats: Counter[str],
    reference_stats: Counter[str],
    issue_counts: Counter[str],
    manual_queue: list[dict[str, Any]],
    repair_items: list[dict[str, Any]],
    formula_events: list[dict[str, Any]],
    table_events: list[dict[str, Any]],
    table_binding_events: list[dict[str, Any]],
    ocr_evidence_index: OCREvidenceIndex,
    table_library: TableLibrary,
    formula_library: FormulaLibrary,
) -> dict[str, Any]:
    """Build the stable summary payload emitted by structured fusion."""
    return {
        "timestamp_utc": utc_now_iso(),
        "structured_dir": str(structured_dir),
        "output_dir": str(output_dir),
        "glmocr_dir": str(glmocr_dir) if glmocr_dir else "",
        "paddle_output_dir": str(paddle_output_dir) if paddle_output_dir else "",
        "reference_structured_dir": str(reference_structured_dir) if reference_structured_dir else "",
        "dry_run": bool(dry_run),
        "include_review": bool(include_review),
        "replace_weaker_tables": bool(replace_weaker_tables),
        "enable_glm_prose_repair": bool(enable_glm_prose_repair),
        "enable_ocr_table_evidence": bool(enable_ocr_table_evidence),
        "enable_ocr_table_repair": bool(enable_ocr_table_repair),
        "auto_threshold": auto_threshold,
        "review_threshold": review_threshold,
        "max_window_paragraphs": max_window_paragraphs,
        "units_scanned": units_scanned,
        "blocks_after_fusion": blocks_after_fusion,
        "block_stats": dict(sorted(block_stats.items())),
        "table_stats": dict(sorted(table_stats.items())),
        "table_binding_stats": dict(sorted(table_binding_stats.items())),
        "formula_stats": dict(sorted(formula_stats.items())),
        "reference_stats": dict(sorted(reference_stats.items())),
        "issue_counts": dict(sorted(issue_counts.items())),
        "manual_queue_count": len(manual_queue),
        "repair_item_count": len(repair_items),
        "formula_event_count": len(formula_events),
        "table_event_count": len(table_events),
        "table_binding_event_count": len(table_binding_events),
        "ocr_evidence_count": len(ocr_evidence_index.evidences),
        "table_library_entries": len(table_library.tables),
        "formula_library_entries": len(formula_library.formulas),
    }


def write_structured_fusion_artifacts(
    *,
    artifacts_dir: str | Path,
    summary: dict[str, Any],
    repair_items: list[dict[str, Any]],
    formula_events: list[dict[str, Any]],
    manual_queue: list[dict[str, Any]],
    table_events: list[dict[str, Any]],
    table_binding_events: list[dict[str, Any]],
    ocr_evidence_index: OCREvidenceIndex,
) -> str:
    """Write structured-fusion artifacts and return the artifact directory."""
    out_dir = Path(artifacts_dir) / "structured_fusion"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "structured_fusion_summary.json", summary)
    write_jsonl(out_dir / "structured_fusion_repair_items.jsonl", repair_items)
    write_jsonl(out_dir / "structured_fusion_formula_events.jsonl", formula_events)
    write_jsonl(out_dir / "structured_fusion_manual_queue.jsonl", manual_queue)
    write_jsonl(out_dir / "structured_fusion_table_events.jsonl", table_events)
    write_jsonl(out_dir / "structured_fusion_table_binding_events.jsonl", table_binding_events)
    write_json(out_dir / "structured_fusion_ocr_evidence_index.json", ocr_evidence_index.to_dict())
    return str(out_dir)
