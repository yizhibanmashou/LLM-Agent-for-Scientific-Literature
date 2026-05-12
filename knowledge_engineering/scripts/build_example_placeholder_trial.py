from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter, defaultdict
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
from knowledge_engineering.core.common import write_json
from knowledge_engineering.pipeline.example_pipeline import (
    candidate_key,
    count_blocks,
    example_to_library_row,
    make_example_ref,
    replace_examples_in_file,
    select_non_overlapping_examples,
    write_example_library,
)
from knowledge_engineering.processors.example_extraction import (
    ExampleCandidate,
    extract_examples_for_structured_dir,
    natural_key,
)


DEFAULT_OUTPUT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "example_placeholder_trial"
DEFAULT_INPUT_STRUCTURED = PROJECT_ROOT / "data" / "structured"


def run_audit_to_paths(structured_dir: Path, label: str, out_dir: Path) -> tuple[dict[str, Any], str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return run_audit(structured_dir, label, out_dir)


def build_report(
    *,
    output_candidate: Path,
    input_structured: Path,
    baseline_audit: dict[str, Any],
    trial_audit: dict[str, Any],
    examples: list[dict[str, Any]],
    file_comparison: dict[str, Any],
    replacement_stats: list[dict[str, Any]],
    command_log: list[dict[str, str]],
) -> str:
    status_counts = Counter(row["replacement"]["status"] for row in examples)
    review_count = sum(1 for row in examples if row.get("metadata", {}).get("needs_review"))
    duplicate_id_count = sum(1 for _, count in Counter(row["example_id"] for row in examples).items() if count > 1)
    replaced_files = sum(1 for item in replacement_stats if item["replaced"])
    before_blocks = sum(item["before_blocks"] for item in replacement_stats)
    after_blocks = sum(item["after_blocks"] for item in replacement_stats)
    removed_blocks = sum(item["removed_blocks"] for item in replacement_stats)

    lines: list[str] = []
    lines.append("# Example Placeholder Trial Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(render_table(
        ["metric", "value"],
        [
            ["input_structured", input_structured],
            ["output_candidate", output_candidate],
            ["total_examples", len(examples)],
            ["replaced_examples", status_counts.get("replaced", 0)],
            ["skipped_examples", len(examples) - status_counts.get("replaced", 0)],
            ["needs_review_examples", review_count],
            ["duplicate_example_ids", duplicate_id_count],
            ["files_with_replacements", replaced_files],
            ["blocks_before", before_blocks],
            ["blocks_after", after_blocks],
            ["blocks_removed_by_example_fold", removed_blocks],
        ],
    ))
    lines.append("")
    lines.append("## Replacement Status")
    lines.append("")
    lines.append(render_table(["status", "count"], [[status, count] for status, count in sorted(status_counts.items())]))
    lines.append("")
    lines.append("## Audit Comparison")
    lines.append("")
    lines.append(render_table(
        ["severity", "baseline", "trial"],
        [[key, baseline_audit["severity_counts"].get(key, 0), trial_audit["severity_counts"].get(key, 0)] for key in ("fatal", "error", "warning", "info")],
    ))
    lines.append("")
    lines.append(render_table(
        ["metric", "baseline", "trial"],
        [[key, baseline_audit["quality_metrics"].get(key), trial_audit["quality_metrics"].get(key)] for key in sorted(set(baseline_audit["quality_metrics"]) | set(trial_audit["quality_metrics"]))],
    ))
    lines.append("")
    lines.append("## Library Integrity")
    lines.append("")
    lines.append(render_table(
        ["check", "result"],
        [
            ["formula_library changed", "no" if "formula_library.json" not in file_comparison["modified"] else "yes"],
            ["table_library changed", "no" if "table_library.json" not in file_comparison["modified"] else "yes"],
            ["example_library.json", "written"],
            ["chapterXX_example_library.json", "not written"],
        ],
    ))
    lines.append("")
    lines.append("## Skipped Examples")
    lines.append("")
    skipped = [row for row in examples if row["replacement"]["status"] != "replaced"]
    if skipped:
        lines.append(render_table(
            ["example_ref", "example_id", "source_file", "span", "reason"],
            [
                [
                    row["example_ref"],
                    row["example_id"],
                    row["source_file"],
                    f"{row['start_block_index']}-{row['end_block_index']}",
                    row["replacement"]["reason"],
                ]
                for row in skipped[:80]
            ],
        ))
    else:
        lines.append("No examples skipped.")
    lines.append("")
    lines.append("## Modified Structured Files")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-structured", default=str(DEFAULT_INPUT_STRUCTURED))
    parser.add_argument("--output-candidate", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    input_structured = Path(args.input_structured).resolve()
    output_candidate = Path(args.output_candidate).resolve()
    output_structured = output_candidate / "structured"
    artifacts_dir = output_candidate / "artifacts"

    if not input_structured.exists():
        raise SystemExit(f"Input structured directory missing: {input_structured}")
    if output_candidate.exists():
        if not args.force:
            raise SystemExit(f"Output candidate already exists: {output_candidate}")
        shutil.rmtree(output_candidate)

    output_candidate.mkdir(parents=True, exist_ok=False)
    shutil.copytree(input_structured, output_structured)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    compile_log = run_py_compile_checks([Path(__file__).resolve(), AUDIT_SCRIPT])
    baseline_audit, baseline_audit_command = run_audit_to_paths(input_structured, "example_placeholder_baseline", artifacts_dir / "baseline_audit")

    all_examples, _, _ = extract_examples_for_structured_dir(output_structured)

    id_counts = Counter(item.example_id for item in all_examples)
    selected_keys, selection_reasons = select_non_overlapping_examples(all_examples)
    example_refs = {candidate_key(item): make_example_ref(item, id_counts) for item in all_examples}

    library_rows: list[dict[str, Any]] = []
    replace_by_file: dict[str, list[ExampleCandidate]] = defaultdict(list)
    for item in all_examples:
        key = candidate_key(item)
        selected = key in selected_keys
        status = "replaced" if selected else "skipped"
        reason = "placeholder_block_written" if selected else selection_reasons.get(key, "not_selected")
        library_rows.append(
            example_to_library_row(
                item,
                example_ref=example_refs[key],
                replacement_status=status,
                replacement_reason=reason,
            )
        )
        if selected:
            replace_by_file[item.source_file].append(item)

    replacement_stats: list[dict[str, Any]] = []
    for file_name, examples in sorted(replace_by_file.items(), key=lambda item: natural_key(item[0])):
        replacement_stats.append(replace_examples_in_file(output_structured / file_name, examples, example_refs))

    write_example_library(output_structured, library_rows)

    trial_audit, trial_audit_command = run_audit_to_paths(output_structured, "example_placeholder_trial", artifacts_dir)
    file_comparison = compare_structured_dirs(input_structured, output_structured)
    write_json(artifacts_dir / "example_placeholder_summary.json", {
        "total_examples": len(library_rows),
        "replacement_status_counts": dict(Counter(row["replacement"]["status"] for row in library_rows)),
        "replacement_stats": replacement_stats,
        "baseline_total_blocks": count_blocks(input_structured),
        "trial_total_blocks": count_blocks(output_structured),
        "file_comparison": file_comparison,
    })
    write_json(artifacts_dir / "example_library_items.json", library_rows)

    command_log = [
        *compile_log,
        {"command": baseline_audit_command, "result": "ok"},
        {"command": trial_audit_command, "result": "ok"},
    ]
    write_text(
        artifacts_dir / "example_placeholder_report.md",
        build_report(
            output_candidate=output_candidate,
            input_structured=input_structured,
            baseline_audit=baseline_audit,
            trial_audit=trial_audit,
            examples=library_rows,
            file_comparison=file_comparison,
            replacement_stats=replacement_stats,
            command_log=command_log,
        ),
    )

    print(json.dumps({
        "output_candidate": str(output_candidate),
        "examples": len(library_rows),
        "replaced": Counter(row["replacement"]["status"] for row in library_rows).get("replaced", 0),
        "skipped": Counter(row["replacement"]["status"] for row in library_rows).get("skipped", 0),
        "baseline_blocks": count_blocks(input_structured),
        "trial_blocks": count_blocks(output_structured),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
