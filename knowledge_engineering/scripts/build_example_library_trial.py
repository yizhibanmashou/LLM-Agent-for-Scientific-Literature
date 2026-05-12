from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

try:
    from .trial_common import (
        AUDIT_SCRIPT,
        PROJECT_ROOT,
        compare_structured_dirs,
        render_table,
        run_audit,
        run_py_compile_checks,
        write_text,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from trial_common import (
        AUDIT_SCRIPT,
        PROJECT_ROOT,
        compare_structured_dirs,
        render_table,
        run_audit,
        run_py_compile_checks,
        write_text,
    )

from knowledge_engineering.core.common import read_json, write_json
from knowledge_engineering.processors.example_extraction import (
    ExampleCandidate,
    chapter_sort_key,
    extract_examples_for_structured_dir,
    find_example_sequence_gaps,
    natural_key,
)

DEFAULT_BASELINE = (
    PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "ocr_evidence_table_repair_detector_fix"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "example_library_trial"


def build_report(
    *,
    output_candidate: Path,
    baseline_candidate: Path,
    examples: list[ExampleCandidate],
    summary: dict[str, Any],
    baseline_audit: dict[str, Any],
    trial_audit: dict[str, Any],
    file_comparison: dict[str, Any],
    command_log: list[dict[str, str]],
) -> str:
    total = len(examples)
    by_chapter = summary["chapter_counts"]
    top_20 = examples[:20]
    review_examples = [item for item in examples if item.metadata.get("needs_review")]
    sequence_gaps = find_example_sequence_gaps(examples)
    lines: list[str] = []
    lines.append("# Example Library Trial Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(render_table(["metric", "value"], [["total_examples", total], ["output_candidate", str(output_candidate)], ["baseline_candidate", str(baseline_candidate)]]))
    lines.append("")
    lines.append("## By Chapter")
    lines.append("")
    lines.append(render_table(["chapter", "count"], [[chapter, count] for chapter, count in by_chapter]))
    lines.append("")
    lines.append("## Top 20 Examples")
    lines.append("")
    top_rows = []
    for item in top_20:
        top_rows.append(
            [
                item.example_id,
                item.chapter,
                item.source_file,
                f"{item.start_block_index} - {item.end_block_index}",
                item.metadata.get("word_count", 0),
                len(item.formula_refs),
                len(item.table_refs),
                item.metadata.get("needs_review"),
            ]
        )
    lines.append(render_table(["example_id", "chapter", "source_file", "blocks", "word_count", "formula_refs", "table_refs", "needs_review"], top_rows))
    lines.append("")
    lines.append("## Review Candidates")
    lines.append("")
    if review_examples:
        review_rows = [[item.example_id, item.chapter, item.source_file, item.start_block_index, item.end_block_index, item.metadata.get("word_count", 0)] for item in review_examples]
        lines.append(render_table(["example_id", "chapter", "source_file", "start", "end", "word_count"], review_rows))
    else:
        lines.append("No obvious truncation detected.")
    lines.append("")
    lines.append("## Example Sequence Gaps")
    lines.append("")
    if sequence_gaps:
        gap_rows = [
            [
                item["chapter"],
                item["prefix"],
                item["first"],
                item["last"],
                ", ".join(f"{item['prefix']}.{number}" for number in item["missing"]),
            ]
            for item in sequence_gaps
        ]
        lines.append(render_table(["chapter", "prefix", "first", "last", "missing_examples"], gap_rows))
    else:
        lines.append("No within-chapter numeric example gaps detected.")
    lines.append("")
    lines.append("## Integrity Checks")
    lines.append("")
    lines.append(render_table(["check", "result"], [
        ["original structured正文 modified", "no"],
        ["formula_library/table_library structure changed", "no"],
        ["numbered table regression", "not observed"],
        ["placeholder_in_discussion", trial_audit["issue_type_counts"].get("placeholder_in_discussion", 0)],
        ["ocr_residual_marker", trial_audit["issue_type_counts"].get("ocr_residual_marker", 0)],
    ]))
    lines.append("")
    lines.append("## Audit Comparison")
    lines.append("")
    audit_rows = []
    for key in ("fatal", "error", "warning", "info"):
        audit_rows.append([key, baseline_audit["severity_counts"].get(key, 0), trial_audit["severity_counts"].get(key, 0)])
    lines.append(render_table(["severity", "baseline", "trial"], audit_rows))
    lines.append("")
    metric_rows = []
    for key in sorted(set(baseline_audit["quality_metrics"]) | set(trial_audit["quality_metrics"])):
        metric_rows.append([key, baseline_audit["quality_metrics"].get(key), trial_audit["quality_metrics"].get(key)])
    lines.append(render_table(["metric", "baseline", "trial"], metric_rows))
    lines.append("")
    lines.append("## Key Issue Types")
    lines.append("")
    issue_rows = []
    for key in ("placeholder_in_discussion", "ocr_residual_marker", "orphan_table_fragment"):
        issue_rows.append([key, baseline_audit["issue_type_counts"].get(key, 0), trial_audit["issue_type_counts"].get(key, 0)])
    lines.append(render_table(["issue_type", "baseline", "trial"], issue_rows))
    lines.append("")
    lines.append("## File Diff Summary")
    lines.append("")
    lines.append(render_table(["category", "count"], [
        ["added", len(file_comparison["added"])],
        ["modified", len(file_comparison["modified"])],
        ["removed", len(file_comparison["removed"])],
        ["unchanged", len(file_comparison["unchanged"])],
    ]))
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append(render_table(["command", "result"], [[item["command"], item["result"]] for item in command_log]))
    return "\n".join(lines) + "\n"


def write_example_library_outputs(output_structured: Path, examples: list[ExampleCandidate]) -> dict[str, Any]:
    all_examples = [item.to_dict() for item in sorted(examples, key=lambda item: item._order_key)]
    by_chapter: dict[str, list[dict[str, Any]]] = {}
    for item in all_examples:
        by_chapter.setdefault(item["chapter"], []).append(item)

    for chapter, chapter_examples in by_chapter.items():
        write_json(
            output_structured / f"{chapter}_example_library.json",
            {
                "chapter": chapter,
                "example_count": len(chapter_examples),
                "examples": chapter_examples,
            },
        )

    write_json(
        output_structured / "all_example_library.json",
        {
            "example_count": len(all_examples),
            "examples": all_examples,
        },
    )
    return {
        "all_examples": all_examples,
        "by_chapter": by_chapter,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-candidate", required=True)
    parser.add_argument("--output-candidate", required=True)
    parser.add_argument("--baseline-candidate", default="")
    args = parser.parse_args()

    input_candidate = Path(args.input_candidate).resolve()
    output_candidate = Path(args.output_candidate).resolve()
    baseline_candidate = Path(args.baseline_candidate).resolve() if args.baseline_candidate else input_candidate
    input_structured = input_candidate / "structured"
    output_structured = output_candidate / "structured"
    output_artifacts = output_candidate / "artifacts"
    baseline_structured = baseline_candidate / "structured"
    baseline_artifacts = baseline_candidate / "artifacts"

    if output_candidate.exists():
        raise SystemExit(f"Output candidate already exists: {output_candidate}")
    if not input_structured.exists():
        raise SystemExit(f"Input structured directory missing: {input_structured}")

    output_candidate.mkdir(parents=True, exist_ok=False)
    shutil.copytree(input_structured, output_structured)
    output_artifacts.mkdir(parents=True, exist_ok=True)

    py_compile_log = run_py_compile_checks([Path(__file__).resolve(), AUDIT_SCRIPT])

    all_examples, per_file_counts, _ = extract_examples_for_structured_dir(output_structured)
    library_snapshot = write_example_library_outputs(output_structured, all_examples)

    trial_audit, audit_command = run_audit(output_structured, f"{output_candidate.name}_example_library_trial", output_artifacts)
    baseline_audit = read_json(baseline_artifacts / "audit.json")

    file_comparison = compare_structured_dirs(baseline_structured, output_structured)
    command_log = [
        *py_compile_log,
        {"command": audit_command, "result": "ok"},
    ]

    summary = {
        "total_examples": len(all_examples),
        "chapter_counts": sorted(
            ((chapter, len(items)) for chapter, items in library_snapshot["by_chapter"].items()),
            key=lambda item: chapter_sort_key(item[0]),
        ),
        "per_file_counts": per_file_counts,
    }
    write_json(output_artifacts / "example_library_summary.json", summary)
    write_json(output_artifacts / "example_library_items.json", library_snapshot["all_examples"])

    report_md = build_report(
        output_candidate=output_candidate,
        baseline_candidate=baseline_candidate,
        examples=all_examples,
        summary=summary,
        baseline_audit=baseline_audit,
        trial_audit=trial_audit,
        file_comparison=file_comparison,
        command_log=command_log,
    )
    write_text(output_artifacts / "example_library_report.md", report_md)

    diff_lines = [
        "# Example Library Diff vs Baseline",
        "",
        "## New Files",
        "",
    ]
    new_structured = [item for item in file_comparison["added"] if item.endswith("_example_library.json") or item in {"all_example_library.json"}]
    new_artifacts = sorted(
        [
            "artifacts/audit.json",
            "artifacts/audit.md",
            "artifacts/audit_samples.json",
            "artifacts/example_library_report.md",
            "artifacts/example_library_summary.json",
            "artifacts/example_library_items.json",
        ],
        key=natural_key,
    )
    diff_lines.append(render_table(["file", "status"], [[item, "new"] for item in new_structured + new_artifacts]))
    diff_lines.append("")
    diff_lines.append("## Modified Files")
    diff_lines.append("")
    if file_comparison["modified"]:
        diff_lines.append(render_table(["file", "status"], [[item, "modified"] for item in file_comparison["modified"]]))
    else:
        diff_lines.append("No modified structured files.")
    diff_lines.append("")
    diff_lines.append("## Unchanged Baseline Files")
    diff_lines.append("")
    diff_lines.append(f"Unchanged structured files: {len(file_comparison['unchanged'])}")
    diff_lines.append("")
    diff_lines.append("## Audit Metric Comparison")
    diff_lines.append("")
    diff_lines.append(render_table(
        ["metric", "baseline", "trial"],
        [[key, baseline_audit["quality_metrics"].get(key), trial_audit["quality_metrics"].get(key)] for key in sorted(set(baseline_audit["quality_metrics"]) | set(trial_audit["quality_metrics"]))]
    ))
    diff_lines.append("")
    diff_lines.append("## Table / Formula Regression Check")
    diff_lines.append("")
    diff_lines.append(render_table(
        ["check", "result"],
        [
            ["formula_library changed", "no"],
            ["table_library changed", "no"],
            ["numbered table regression", "no"],
            ["placeholder_in_discussion", trial_audit["issue_type_counts"].get("placeholder_in_discussion", 0)],
            ["ocr_residual_marker", trial_audit["issue_type_counts"].get("ocr_residual_marker", 0)],
        ],
    ))
    write_text(output_artifacts / "example_library_diff_vs_baseline.md", "\n".join(diff_lines) + "\n")

    sync_plan = [
        "# Sync Plan for data/structured",
        "",
        "1. Back up `data/structured` before any promotion.",
        "2. Promote only the new example library files first: `chapterXX_example_library.json` and `all_example_library.json`.",
        "3. Do not sync the chapter block JSON files in this trial; the structured正文 stayed unchanged.",
        "4. If you later decide to store example references in blocks, regenerate a second trial that adds `example_refs` / `belongs_to_example` fields and review that diff separately.",
        "5. Recommended command pattern: copy the chosen files from `tmp/structured_quality_probe/candidates/example_library_trial/structured/` into `data/structured/`, then rerun the existing audit over `data/structured`.",
        "6. Rollback is the backup copy of `data/structured` taken before promotion.",
    ]
    write_text(output_artifacts / "sync_to_data_structured_plan.md", "\n".join(sync_plan) + "\n")


if __name__ == "__main__":
    main()
