from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import (
    CACHE_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    SAMPLES_DIR,
    ensure_output_dirs,
    load_json,
    markdown_table,
    natural_key,
    relpath,
    snippet,
    structured_json_files,
    write_json,
    write_jsonl,
    write_text,
)


SEED = 20260505

BASELINE_FILES = [
    "00_data_availability.json",
    "00_data_availability.md",
    "01_structured_quality_audit.json",
    "01_structured_quality_audit.md",
    "01_structured_issue_samples.jsonl",
    "02_ocr_source_comparison.json",
    "02_ocr_source_comparison.md",
    "03_feasibility_conclusion.md",
    "04_detailed_report_explanation.md",
]

TARGET_COUNTS = {
    "discussion_normal": 30,
    "derivation": 30,
    "proposition_definition": 20,
    "fatal_error": 30,
    "warning": 20,
    "ocr_disagreement_chapter": 20,
}

PRIORITY_ISSUES = {
    "P0": ["table_reference_missing"],
    "P1": ["h_only_block", "tex_command_leak", "unbalanced_inline_math", "broken_placeholder", "ghost_block"],
    "P2": ["very_short_block", "derivation_placeholder_only_text", "placeholder_in_discussion", "suspicious_truncation"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def block_key(file: str, block_index: int | None) -> str:
    return f"{file}#block_{block_index}" if block_index is not None else f"{file}#file"


def stable_sample(rows: list[dict[str, Any]], count: int, seed_offset: int) -> list[dict[str, Any]]:
    rng = random.Random(SEED + seed_offset)
    if len(rows) <= count:
        return list(rows)
    return rng.sample(rows, count)


def load_all_blocks(issue_by_block: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for file_path in structured_json_files():
        try:
            data = load_json(file_path)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        chapter = str(metadata.get("chapter") or file_path.stem.split("_", 1)[0]).lower()
        raw_blocks = data.get("blocks")
        if not isinstance(raw_blocks, list):
            continue
        for idx, block in enumerate(raw_blocks):
            if not isinstance(block, dict):
                continue
            file_rel = relpath(file_path)
            key = block_key(file_rel, idx)
            content = block.get("content")
            if not isinstance(content, str):
                content = "" if content is None else json.dumps(content, ensure_ascii=False)
            issues = issue_by_block.get(key, [])
            severities = sorted({issue.get("severity", "") for issue in issues})
            issue_types = sorted({issue.get("issue_type", "") for issue in issues})
            blocks.append(
                {
                    "sample_id_base": f"{chapter}:{Path(file_rel).stem}:block_{idx:03d}",
                    "chapter": chapter,
                    "file": file_rel,
                    "block_index": idx,
                    "block_key": key,
                    "block_type": str(block.get("type", "unknown")),
                    "content": content,
                    "content_snippet": snippet(content, 260),
                    "issue_count": len(issues),
                    "severities": severities,
                    "issue_types": issue_types,
                }
            )
    return blocks


def choose_samples(
    blocks: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    ocr_report: dict[str, Any],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_keys: set[str] = set()

    def add_rows(stratum: str, rows: list[dict[str, Any]], count: int, seed_offset: int) -> None:
        nonlocal selected
        candidates = [row for row in rows if row["block_key"] not in used_keys]
        picks = stable_sample(candidates, count, seed_offset)
        for row in picks:
            used_keys.add(row["block_key"])
            sample_no = len(selected) + 1
            selected.append(
                {
                    "sample_id": f"S{sample_no:04d}",
                    "stratum": stratum,
                    "chapter": row["chapter"],
                    "file": row["file"],
                    "block_index": row["block_index"],
                    "block_key": row["block_key"],
                    "block_type": row["block_type"],
                    "issue_count": row["issue_count"],
                    "severities": row["severities"],
                    "issue_types": row["issue_types"],
                    "content_snippet": row["content_snippet"],
                    "seed": SEED,
                }
            )

    normal_blocks = [b for b in blocks if b["issue_count"] == 0]
    add_rows(
        "discussion_normal",
        [b for b in normal_blocks if b["block_type"] == "discussion"],
        TARGET_COUNTS["discussion_normal"],
        10,
    )
    add_rows(
        "derivation",
        [b for b in blocks if b["block_type"] == "derivation"],
        TARGET_COUNTS["derivation"],
        20,
    )
    add_rows(
        "proposition_definition",
        [b for b in blocks if b["block_type"] in {"proposition", "definition"}],
        TARGET_COUNTS["proposition_definition"],
        30,
    )

    fatal_error_keys = {
        block_key(issue["file"], issue.get("block_index"))
        for issue in issues
        if issue.get("severity") in {"fatal", "error"} and issue.get("block_index") is not None
    }
    add_rows(
        "fatal_error",
        [b for b in blocks if b["block_key"] in fatal_error_keys],
        TARGET_COUNTS["fatal_error"],
        40,
    )

    warning_keys = {
        block_key(issue["file"], issue.get("block_index"))
        for issue in issues
        if issue.get("severity") == "warning" and issue.get("block_index") is not None
    }
    add_rows(
        "warning",
        [b for b in blocks if b["block_key"] in warning_keys],
        TARGET_COUNTS["warning"],
        50,
    )

    high_ocr_chapters = set()
    for comp in ocr_report.get("chapter_comparisons", []):
        if comp.get("length_gap_ratio", 0) >= 0.2 or comp.get("formula_gap", 0) >= 5:
            high_ocr_chapters.add(str(comp.get("chapter", "")).lower())
    add_rows(
        "ocr_disagreement_chapter",
        [b for b in normal_blocks if b["chapter"] in high_ocr_chapters],
        TARGET_COUNTS["ocr_disagreement_chapter"],
        60,
    )

    return selected


def write_annotation_csv(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "sample_id",
        "stratum",
        "chapter",
        "file",
        "block_index",
        "block_type",
        "issue_types",
        "severities",
        "content_snippet",
        "manual_is_acceptable",
        "manual_content_accuracy",
        "manual_structure_accuracy",
        "manual_formula_table_accuracy",
        "manual_issue_type",
        "manual_notes",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for sample in samples:
            row = dict(sample)
            row["issue_types"] = ";".join(sample.get("issue_types", []))
            row["severities"] = ";".join(sample.get("severities", []))
            for col in columns:
                row.setdefault(col, "")
            writer.writerow({col: row[col] for col in columns})


def priority_for_issue(issue_type: str) -> str:
    for priority, issue_types in PRIORITY_ISSUES.items():
        if issue_type in issue_types:
            return priority
    return "P3"


def build_priority_triage(issues: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        grouped[issue.get("issue_type", "unknown")].append(issue)

    issue_groups = []
    for issue_type, rows in sorted(grouped.items(), key=lambda item: (priority_for_issue(item[0]), -len(item[1]), item[0])):
        chapter_counts = Counter(row.get("chapter", "unknown") for row in rows)
        severity_counts = Counter(row.get("severity", "unknown") for row in rows)
        issue_groups.append(
            {
                "priority": priority_for_issue(issue_type),
                "issue_type": issue_type,
                "count": len(rows),
                "severity_counts": dict(severity_counts),
                "top_chapters": chapter_counts.most_common(8),
                "samples": rows[:10],
            }
        )
    return {
        "priority_order": PRIORITY_ISSUES,
        "issue_groups": issue_groups,
    }


def main() -> None:
    ensure_output_dirs()

    availability = load_json(REPORTS_DIR / "00_data_availability.json")
    audit = load_json(REPORTS_DIR / "01_structured_quality_audit.json")
    ocr = load_json(REPORTS_DIR / "02_ocr_source_comparison.json")
    issues = read_jsonl(REPORTS_DIR / "01_structured_issue_samples.jsonl")

    baseline_dir = CACHE_DIR / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline_records = []
    for name in BASELINE_FILES:
        src = REPORTS_DIR / name
        if not src.exists():
            continue
        dst = baseline_dir / name
        shutil.copy2(src, dst)
        baseline_records.append(
            {
                "name": name,
                "source": relpath(src),
                "baseline_copy": relpath(dst),
                "sha256": sha256_file(src),
                "size_bytes": src.stat().st_size,
            }
        )

    manifest = {
        "seed": SEED,
        "baseline_records": baseline_records,
        "baseline_metrics": {
            "structured_json_files": availability["structured_summary"]["file_count"],
            "total_blocks": availability["structured_summary"]["total_blocks"],
            "formula_library_entries": availability["structured_summary"]["formula_library_entry_count"],
            "table_library_entries": availability["structured_summary"]["table_library_entry_count"],
            "strict_pass_rate": audit["quality_metrics"]["strict_pass_rate"],
            "weighted_quality_score": audit["quality_metrics"]["weighted_quality_score"],
            "formula_reference_valid_rate": audit["reference_metrics"]["formula_reference_valid_rate"],
            "table_reference_valid_rate": audit["reference_metrics"]["table_reference_valid_rate"],
            "derivation_reference_valid_rate": audit["reference_metrics"]["derivation_reference_valid_rate"],
            "ghost_block_rate": audit["reference_metrics"]["ghost_block_rate"],
        },
        "note": "This baseline manifest and copied reports live under tmp/structured_quality_probe only.",
    }
    write_json(CACHE_DIR / "baseline_manifest.json", manifest)

    issue_by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        if issue.get("block_index") is None:
            continue
        issue_by_block[block_key(issue["file"], issue.get("block_index"))].append(issue)

    blocks = load_all_blocks(issue_by_block)
    samples = choose_samples(blocks, issues, ocr)
    write_jsonl(SAMPLES_DIR / "manual_sample_ids.jsonl", samples)
    write_json(SAMPLES_DIR / "manual_sample_ids.json", samples)
    write_annotation_csv(SAMPLES_DIR / "manual_sample_annotation_template.csv", samples)

    stratum_counts = Counter(sample["stratum"] for sample in samples)
    sample_report = {
        "seed": SEED,
        "target_counts": TARGET_COUNTS,
        "actual_counts": dict(stratum_counts),
        "total_samples": len(samples),
        "samples_path": relpath(SAMPLES_DIR / "manual_sample_ids.jsonl"),
        "annotation_template_path": relpath(SAMPLES_DIR / "manual_sample_annotation_template.csv"),
        "sampling_notes": [
            "Samples are deterministic with a fixed seed.",
            "No source structured files are modified.",
            "Manual fields are intentionally blank in the CSV template.",
        ],
    }
    write_json(REPORTS_DIR / "05_sampling_plan.json", sample_report)

    sample_rows = [[k, TARGET_COUNTS[k], stratum_counts.get(k, 0)] for k in TARGET_COUNTS]
    md = [
        "# 05 Sampling Plan",
        "",
        "本报告固定 baseline 后的人工抽样 ID。抽样只读取 structured 和已有审计报告，不修改任何原始数据。",
        "",
        "## 抽样数量",
        "",
        markdown_table(["stratum", "target", "actual"], sample_rows),
        "",
        "## 输出文件",
        "",
        markdown_table(
            ["文件", "用途"],
            [
                ["samples/manual_sample_ids.jsonl", "固定抽样 ID，每行一个样本。"],
                ["samples/manual_sample_ids.json", "同一抽样清单的 JSON 数组版。"],
                ["samples/manual_sample_annotation_template.csv", "人工标注模板，UTF-8 BOM，Excel 可直接打开。"],
                ["cache/baseline_manifest.json", "baseline 报告哈希和核心指标。"],
                ["cache/baseline/", "baseline 报告副本。"],
            ],
        ),
        "",
        "## 标注口径",
        "",
        "- `manual_is_acceptable`：该 block 是否可用于下游知识库。",
        "- `manual_content_accuracy`：正文语义是否正确，可填 `correct / minor_issue / major_issue / unusable`。",
        "- `manual_structure_accuracy`：block 类型、切分、上下文是否合理。",
        "- `manual_formula_table_accuracy`：公式/表格引用和表达是否可接受。",
        "- `manual_issue_type` 和 `manual_notes`：人工发现的问题类别与说明。",
    ]
    write_text(REPORTS_DIR / "05_sampling_plan.md", "\n".join(md) + "\n")

    triage = build_priority_triage(issues)
    write_json(REPORTS_DIR / "06_priority_issue_triage.json", triage)

    triage_rows = [
        [
            group["priority"],
            group["issue_type"],
            group["count"],
            ", ".join(f"{chapter}:{count}" for chapter, count in group["top_chapters"][:5]),
        ]
        for group in triage["issue_groups"]
    ]
    p0_candidates = [
        [
            row["issue_type"],
            row["chapter"],
            row["file"],
            row.get("block_index", ""),
            row.get("block_type", ""),
            row.get("sample_snippet", ""),
        ]
        for group in triage["issue_groups"]
        if group["priority"] in {"P0", "P1"}
        for row in group["samples"][:5]
    ]
    triage_md = [
        "# 06 Priority Issue Triage",
        "",
        "本报告只整理修复候选，不执行 repair，不修改 structured。",
        "",
        "## 优先级规则",
        "",
        markdown_table(
            ["priority", "issue_types", "处理建议"],
            [
                ["P0", ", ".join(PRIORITY_ISSUES["P0"]), "引用完整性问题，先人工确认缺失表格是否应补库或改引用。"],
                ["P1", ", ".join(PRIORITY_ISSUES["P1"]), "明显结构残留或语法异常，可作为第一轮清理候选。"],
                ["P2", ", ".join(PRIORITY_ISSUES["P2"]), "需要人工判定语境，避免误删合法短文本。"],
                ["P3", "其他", "暂不进入第一轮优化。"],
            ],
        ),
        "",
        "## issue 分组",
        "",
        markdown_table(["priority", "issue_type", "count", "top_chapters"], triage_rows),
        "",
        "## P0/P1 代表候选",
        "",
        markdown_table(["issue_type", "chapter", "file", "block", "block_type", "sample"], p0_candidates),
    ]
    write_text(REPORTS_DIR / "06_priority_issue_triage.md", "\n".join(triage_md) + "\n")


if __name__ == "__main__":
    main()
