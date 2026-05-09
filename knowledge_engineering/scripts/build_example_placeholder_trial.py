from __future__ import annotations

import argparse
import json
import py_compile
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_example_library_trial import (
    AUDIT_SCRIPT,
    PROJECT_ROOT,
    ExampleCandidate,
    chapter_sort_key,
    compare_structured_dirs,
    extract_examples_for_file,
    extract_examples_for_structured_dir,
    load_unit_files,
    natural_key,
    read_json,
    render_table,
    run_audit,
    run_py_compile_checks,
    sha256_file,
    write_json,
    write_text,
)


DEFAULT_OUTPUT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "candidates" / "example_placeholder_trial"
DEFAULT_INPUT_STRUCTURED = PROJECT_ROOT / "data" / "structured"


def make_example_ref(item: ExampleCandidate, id_counts: Counter[str]) -> str:
    if id_counts[item.example_id] == 1:
        return item.example_id
    source_stem = Path(item.source_file).stem
    return f"{item.example_id}@{source_stem}_{item.start_block_index}"


def example_to_library_row(
    item: ExampleCandidate,
    *,
    example_ref: str,
    replacement_status: str,
    replacement_reason: str,
) -> dict[str, Any]:
    row = item.to_dict()
    row["example_ref"] = example_ref
    row["placeholder"] = f"[[SEE_EXAMPLE:{example_ref}]]"
    row["replacement"] = {
        "status": replacement_status,
        "reason": replacement_reason,
        "source_block_span": [item.start_block_index, item.end_block_index],
    }
    return row


def select_non_overlapping_examples(examples: list[ExampleCandidate]) -> tuple[set[str], dict[str, str]]:
    selected_keys: set[str] = set()
    reasons: dict[str, str] = {}
    by_file: dict[str, list[ExampleCandidate]] = defaultdict(list)
    for item in examples:
        by_file[item.source_file].append(item)

    for file_examples in by_file.values():
        occupied: set[int] = set()
        for item in sorted(file_examples, key=lambda ex: (ex.start_block_index, ex.end_block_index, natural_key(ex.example_id))):
            key = candidate_key(item)
            span = set(range(item.start_block_index, item.end_block_index + 1))
            if occupied & span:
                reasons[key] = "overlaps_selected_example_span"
                continue
            selected_keys.add(key)
            occupied.update(span)
            reasons[key] = "selected"
    return selected_keys, reasons


def candidate_key(item: ExampleCandidate) -> str:
    return f"{item.source_file}#{item.start_block_index}-{item.end_block_index}#{item.example_id}"


def replace_examples_in_file(path: Path, examples: list[ExampleCandidate], example_refs: dict[str, str]) -> dict[str, Any]:
    data = read_json(path)
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return {"file": path.name, "before_blocks": 0, "after_blocks": 0, "replaced": 0, "removed_blocks": 0}

    by_start = {item.start_block_index: item for item in examples}
    skip_until = -1
    new_blocks: list[Any] = []
    replaced = 0
    removed_blocks = 0
    for index, block in enumerate(blocks):
        if index <= skip_until:
            continue
        item = by_start.get(index)
        if item is None:
            new_blocks.append(block)
            continue
        ref = example_refs[candidate_key(item)]
        new_blocks.append(
            {
                "type": "example",
                "content": f"[[SEE_EXAMPLE:{ref}]]",
            }
        )
        replaced += 1
        removed_blocks += item.end_block_index - item.start_block_index
        skip_until = item.end_block_index

    data["blocks"] = new_blocks
    write_json(path, data)
    return {
        "file": path.name,
        "before_blocks": len(blocks),
        "after_blocks": len(new_blocks),
        "replaced": replaced,
        "removed_blocks": removed_blocks,
    }


def count_blocks(structured_dir: Path) -> int:
    total = 0
    for path in load_unit_files(structured_dir):
        data = read_json(path)
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if isinstance(blocks, list):
            total += len(blocks)
    return total


def run_audit_to_paths(structured_dir: Path, label: str, out_dir: Path) -> tuple[dict[str, Any], str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return run_audit(structured_dir, label, out_dir)


def write_example_library(output_structured: Path, rows: list[dict[str, Any]]) -> None:
    write_json(
        output_structured / "example_library.json",
        {
            "schema": "example_library.v1",
            "example_count": len(rows),
            "examples": rows,
        },
    )


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
