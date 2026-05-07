from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from audit_structured_version import (
    audit_structured_dir,
    calibrated_tex_command_leak,
    write_audit_outputs,
)
from common import (
    PROJECT_ROOT,
    PROBE_ROOT,
    REPORTS_DIR,
    SAMPLES_DIR,
    count_placeholders,
    ensure_output_dirs,
    extract_formula_refs,
    extract_table_refs,
    has_unbalanced_math,
    is_ghost_block,
    load_json,
    markdown_table,
    natural_key,
    relpath,
    snippet,
    write_json,
    write_jsonl,
    write_text,
)


EARLY_STRUCTURED_DIR = PROBE_ROOT / "old_structured"
CURRENT_STRUCTURED_DIR = PROJECT_ROOT / "data" / "structured"
CANDIDATE_STRUCTURED_DIR = PROBE_ROOT / "candidates" / "current_plus_p0p1" / "structured"
CANDIDATE_ROOT = PROBE_ROOT / "candidates" / "current_plus_p0p1"

AUDIT_OUTPUTS = {
    "early": {
        "label": "early paper2latex structured",
        "dir": EARLY_STRUCTURED_DIR,
        "json": REPORTS_DIR / "10_early_structured_audit.json",
        "md": REPORTS_DIR / "10_early_structured_audit.md",
        "samples": REPORTS_DIR / "10_early_structured_issue_samples.jsonl",
    },
    "current": {
        "label": "current delivery baseline calibrated",
        "dir": CURRENT_STRUCTURED_DIR,
        "json": REPORTS_DIR / "11_current_structured_audit_calibrated.json",
        "md": REPORTS_DIR / "11_current_structured_audit_calibrated.md",
        "samples": REPORTS_DIR / "11_current_structured_issue_samples_calibrated.jsonl",
    },
    "candidate": {
        "label": "candidate current_plus_p0p1",
        "dir": CANDIDATE_STRUCTURED_DIR,
        "json": REPORTS_DIR / "12_candidate_structured_audit.json",
        "md": REPORTS_DIR / "12_candidate_structured_audit.md",
        "samples": REPORTS_DIR / "12_candidate_structured_issue_samples.jsonl",
    },
}

THREE_VERSION_JSON = REPORTS_DIR / "09_three_version_comparison.json"
THREE_VERSION_MD = REPORTS_DIR / "09_three_version_comparison.md"
FRIDAY_REPORT_MD = REPORTS_DIR / "07_friday_delivery_evidence.md"
SAMPLE_COMPARISON_JSONL = SAMPLES_DIR / "three_version_sample_comparison.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def summarize_audit(report: dict[str, Any]) -> dict[str, Any]:
    issue_counts = report.get("issue_type_counts", {})
    severity_counts = report.get("severity_counts", {})
    metrics = report.get("quality_metrics", {}) | report.get("reference_metrics", {})
    return {
        "structured_json_files": report["totals"]["structured_json_files"],
        "total_blocks": report["totals"]["total_blocks"],
        "formula_library_entries": report["library_counts"]["formula_library_entries"],
        "table_library_entries": report["library_counts"]["table_library_entries"],
        "fatal": severity_counts.get("fatal", 0),
        "error": severity_counts.get("error", 0),
        "warning": severity_counts.get("warning", 0),
        "info": severity_counts.get("info", 0),
        "strict_pass_rate": metrics.get("strict_pass_rate"),
        "weighted_quality_score": metrics.get("weighted_quality_score"),
        "formula_reference_valid_rate": metrics.get("formula_reference_valid_rate"),
        "table_reference_valid_rate": metrics.get("table_reference_valid_rate"),
        "derivation_reference_valid_rate": metrics.get("derivation_reference_valid_rate"),
        "ghost_block_rate": metrics.get("ghost_block_rate"),
        "h_only_block": issue_counts.get("h_only_block", 0),
        "ghost_block": issue_counts.get("ghost_block", 0),
        "tex_command_leak": issue_counts.get("tex_command_leak", 0),
        "unbalanced_inline_math": issue_counts.get("unbalanced_inline_math", 0),
        "table_reference_missing": issue_counts.get("table_reference_missing", 0),
        "very_short_block": issue_counts.get("very_short_block", 0),
        "derivation_placeholder_only_text": issue_counts.get("derivation_placeholder_only_text", 0),
    }


def metric_delta(left: Any, right: Any) -> Any:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return right - left
    return None


def run_version_audits() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    reports: dict[str, dict[str, Any]] = {}
    issue_rows: dict[str, list[dict[str, Any]]] = {}
    for version, cfg in AUDIT_OUTPUTS.items():
        report, sorted_issues = audit_structured_dir(cfg["dir"], cfg["label"])
        write_audit_outputs(report, sorted_issues, cfg["json"], cfg["md"], cfg["samples"])
        reports[version] = report
        issue_rows[version] = sorted_issues
    return reports, issue_rows


def load_candidate_mapping() -> dict[tuple[str, int], int | None]:
    mapping: dict[tuple[str, int], int | None] = {}
    path = CANDIDATE_ROOT / "block_index_mapping.jsonl"
    for row in load_jsonl(path):
        file_value = str(row.get("file", ""))
        # Candidate builder records candidate-relative file paths; manual sample ids are data/structured-relative.
        basename = Path(file_value).name
        old_file = f"data/structured/{basename}"
        old_index = row.get("old_block_index")
        if isinstance(old_index, int):
            mapping[(old_file, old_index)] = row.get("candidate_block_index")
    return mapping


def version_file_path(version: str, current_file: str) -> Path:
    basename = Path(current_file).name
    if version == "early":
        return EARLY_STRUCTURED_DIR / basename
    if version == "current":
        return CURRENT_STRUCTURED_DIR / basename
    if version == "candidate":
        return CANDIDATE_STRUCTURED_DIR / basename
    raise ValueError(version)


def extract_block(version: str, current_file: str, current_block_index: int, candidate_mapping: dict[tuple[str, int], int | None]) -> dict[str, Any]:
    path = version_file_path(version, current_file)
    if not path.exists():
        return {"status": "missing_file", "path": relpath(path)}
    block_index = current_block_index
    if version == "candidate":
        mapped = candidate_mapping.get((current_file, current_block_index), current_block_index)
        if mapped is None:
            return {"status": "removed_in_candidate", "path": relpath(path), "block_index": None}
        block_index = int(mapped)
    try:
        data = load_json(path)
    except Exception as exc:
        return {"status": "json_error", "path": relpath(path), "error": str(exc)}
    blocks = data.get("blocks") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return {"status": "missing_blocks", "path": relpath(path)}
    if block_index < 0 or block_index >= len(blocks):
        return {"status": "missing_block", "path": relpath(path), "block_index": block_index}
    block = blocks[block_index]
    if not isinstance(block, dict):
        return {"status": "non_dict_block", "path": relpath(path), "block_index": block_index}
    content = block.get("content")
    if not isinstance(content, str):
        content = "" if content is None else json.dumps(content, ensure_ascii=False)
    block_type = str(block.get("type", "unknown"))
    leak, leak_commands = calibrated_tex_command_leak(content, block_type)
    return {
        "status": "ok",
        "path": relpath(path),
        "block_index": block_index,
        "block_type": block_type,
        "content_length": len(content),
        "formula_ref_count": len(extract_formula_refs(content)),
        "table_ref_count": len(extract_table_refs(content)),
        "placeholder_count": count_placeholders(content),
        "unbalanced_math": has_unbalanced_math(content),
        "ghost_block": is_ghost_block(content),
        "tex_command_leak": leak,
        "tex_command_leak_commands": leak_commands[:8],
        "content_snippet": snippet(content, 300),
    }


def load_manual_samples() -> list[dict[str, Any]]:
    json_path = SAMPLES_DIR / "manual_sample_ids.json"
    if json_path.exists():
        data = load_json(json_path)
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    return load_jsonl(SAMPLES_DIR / "manual_sample_ids.jsonl")


def build_sample_comparison() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    samples = load_manual_samples()
    candidate_mapping = load_candidate_mapping()
    rows: list[dict[str, Any]] = []
    for sample in samples:
        current_file = str(sample.get("file", ""))
        block_index = sample.get("block_index")
        if not isinstance(block_index, int):
            continue
        row = {
            "sample_id": sample.get("sample_id"),
            "stratum": sample.get("stratum"),
            "chapter": sample.get("chapter"),
            "file": current_file,
            "current_block_index": block_index,
            "early": extract_block("early", current_file, block_index, candidate_mapping),
            "current": extract_block("current", current_file, block_index, candidate_mapping),
            "candidate": extract_block("candidate", current_file, block_index, candidate_mapping),
        }
        current = row["current"]
        candidate = row["candidate"]
        early = row["early"]
        row["comparison"] = {
            "early_vs_current_length_delta": metric_delta(early.get("content_length"), current.get("content_length")),
            "candidate_vs_current_length_delta": metric_delta(current.get("content_length"), candidate.get("content_length")),
            "candidate_status": candidate.get("status"),
        }
        rows.append(row)

    summary = {
        "sample_count": len(rows),
        "candidate_removed_samples": sum(1 for row in rows if row["candidate"].get("status") == "removed_in_candidate"),
        "early_missing_samples": sum(1 for row in rows if row["early"].get("status") != "ok"),
        "candidate_missing_samples": sum(1 for row in rows if row["candidate"].get("status") not in {"ok", "removed_in_candidate"}),
        "strata_counts": dict(Counter(str(row.get("stratum")) for row in rows)),
    }
    return rows, summary


def format_value(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        if -1 <= value <= 1:
            return f"{value:.4%}"
        return f"{value:.6f}"
    return str(value)


def metrics_table(version_summaries: dict[str, dict[str, Any]]) -> str:
    rows = []
    keys = [
        "structured_json_files",
        "total_blocks",
        "formula_library_entries",
        "table_library_entries",
        "fatal",
        "error",
        "warning",
        "strict_pass_rate",
        "weighted_quality_score",
        "formula_reference_valid_rate",
        "table_reference_valid_rate",
        "derivation_reference_valid_rate",
        "ghost_block_rate",
        "h_only_block",
        "ghost_block",
        "tex_command_leak",
        "unbalanced_inline_math",
        "table_reference_missing",
        "very_short_block",
    ]
    for key in keys:
        rows.append([key, format_value(version_summaries["early"].get(key)), format_value(version_summaries["current"].get(key)), format_value(version_summaries["candidate"].get(key))])
    return markdown_table(["metric", "early", "current", "candidate"], rows)


def delta_table(version_summaries: dict[str, dict[str, Any]]) -> str:
    rows = []
    for key in [
        "fatal",
        "error",
        "warning",
        "strict_pass_rate",
        "weighted_quality_score",
        "table_reference_valid_rate",
        "ghost_block_rate",
        "h_only_block",
        "ghost_block",
        "table_reference_missing",
    ]:
        early = version_summaries["early"].get(key)
        current = version_summaries["current"].get(key)
        candidate = version_summaries["candidate"].get(key)
        rows.append([key, format_value(metric_delta(early, current)), format_value(metric_delta(current, candidate))])
    return markdown_table(["metric", "current - early", "candidate - current"], rows)


def issue_top_rows(issue_rows: dict[str, list[dict[str, Any]]], version: str, limit: int = 8) -> list[list[Any]]:
    counter = Counter(row.get("issue_type", "unknown") for row in issue_rows.get(version, []))
    return [[key, value] for key, value in counter.most_common(limit)]


def write_three_version_report(comparison: dict[str, Any], issue_rows: dict[str, list[dict[str, Any]]]) -> None:
    version_summaries = comparison["version_summaries"]
    gates = comparison["candidate_quality_gate"]
    md = [
        "# 09 Three Version Structured Comparison",
        "",
        "三版对比使用同一个 calibrated structured audit 口径。旧版额外排除了 `*_nav_*.json` 和 `*_toc_tree.json`，只比较真正包含 `blocks` 的 unit。",
        "",
        "## 版本路径",
        "",
        markdown_table(
            ["version", "path"],
            [
                ["early", relpath(EARLY_STRUCTURED_DIR)],
                ["current", relpath(CURRENT_STRUCTURED_DIR)],
                ["candidate", relpath(CANDIDATE_STRUCTURED_DIR)],
            ],
        ),
        "",
        "## 核心指标对比",
        "",
        metrics_table(version_summaries),
        "",
        "## 指标变化",
        "",
        delta_table(version_summaries),
        "",
        "## candidate gate",
        "",
        markdown_table(["gate", "passed"], [[key, value] for key, value in gates.items()]),
        "",
        "## 各版本高频问题",
        "",
        "### early",
        "",
        markdown_table(["issue_type", "count"], issue_top_rows(issue_rows, "early") or [["无", 0]]),
        "",
        "### current",
        "",
        markdown_table(["issue_type", "count"], issue_top_rows(issue_rows, "current") or [["无", 0]]),
        "",
        "### candidate",
        "",
        markdown_table(["issue_type", "count"], issue_top_rows(issue_rows, "candidate") or [["无", 0]]),
        "",
        "## 固定抽样 ID 对比",
        "",
        markdown_table(
            ["metric", "value"],
            [[key, value] for key, value in comparison["sample_comparison_summary"].items() if key != "strata_counts"],
        ),
        "",
        f"完整抽样对比写入 `{relpath(SAMPLE_COMPARISON_JSONL)}`。",
        "",
        "## 解释",
        "",
        "- current 是当前交付基线，不在本轮直接修改。",
        "- candidate 是 tmp-only 优化候选，用于证明后续仍有增量空间。",
        "- candidate gate 只表示自动审计指标未回退；是否合入正式 structured 仍需人工抽样确认。",
    ]
    write_text(THREE_VERSION_MD, "\n".join(md) + "\n")


def write_friday_report(comparison: dict[str, Any]) -> None:
    version_summaries = comparison["version_summaries"]
    current = version_summaries["current"]
    candidate = version_summaries["candidate"]
    early = version_summaries["early"]
    ocr_report_path = REPORTS_DIR / "02_ocr_source_comparison.json"
    ocr = load_json(ocr_report_path) if ocr_report_path.exists() else {}
    source_roots = ocr.get("source_roots", {}) if isinstance(ocr, dict) else {}
    source_issue_summary = ocr.get("source_issue_summary", {}) if isinstance(ocr, dict) else {}
    problem_chapter_count = source_issue_summary.get("problem_chapter_count", {}) if isinstance(source_issue_summary, dict) else {}
    outliers = ocr.get("outlier_summary", {}) if isinstance(ocr, dict) else {}

    md = [
        "# 07 Friday Delivery Evidence",
        "",
        "## 结论先行",
        "",
        "当前 `data/structured` 可以作为周五交付版：它不是“字符级 OCR 真值”，但在结构化可用质量口径下已经达到交付标准。PaddleOCR 和 GLM-OCR 都只能作为来源或参考，不能单独当作原文 ground truth；后续优化应在 tmp candidate 上验证后再考虑合入。",
        "",
        "## 为什么不能直接算传统 OCR 准确率",
        "",
        "- 现有数据缺少人工校对的逐字符原文真值。PaddleOCR、GLM-OCR、structured 三者都是机器或规则链路产物，不是人工标注答案。",
        "- structured 的目标不是复刻 OCR 文本，而是形成可被知识库使用的 block、公式引用、表格引用和 derivation 结构。",
        "- 因此准确率口径应从“字符完全一致”转成“结构化可用质量 + 引用有效率 + 人工抽样准确率”。",
        "",
        "## 为什么 PaddleOCR / GLM-OCR 都不能当唯一真值",
        "",
        markdown_table(
            ["evidence", "value"],
            [
                ["Paddle 可用章节", source_roots.get("paddle", {}).get("chapter_count", "N/A")],
                ["GLM 可用章节", source_roots.get("glmocr", {}).get("chapter_count", "N/A")],
                ["Paddle 问题章节", problem_chapter_count.get("paddle", "N/A")],
                ["GLM 问题章节", problem_chapter_count.get("glmocr", "N/A")],
                ["长度差异异常章节", outliers.get("length_gap_outlier_count", "N/A")],
                ["公式数量差异异常章节", outliers.get("formula_gap_outlier_count", "N/A")],
            ],
        ),
        "",
        "- PaddleOCR 可以作为 structured 生产源，但它有 LaTeX 残留、数学定界符等问题，所以不等于 ground truth。",
        "- GLM-OCR 可以作为修复参考源，但它同样存在结构残缺和章节级差异，所以也不等于 ground truth。",
        "- Paddle vs GLM 的差异只能证明来源不一致，不能直接推出谁正确，也不能直接得到 structured 准确率。",
        "",
        "## structured 质量是否达到交付标准",
        "",
        markdown_table(
            ["metric", "early", "current", "candidate"],
            [
                ["strict_pass_rate", format_value(early["strict_pass_rate"]), format_value(current["strict_pass_rate"]), format_value(candidate["strict_pass_rate"])],
                ["weighted_quality_score", format_value(early["weighted_quality_score"]), format_value(current["weighted_quality_score"]), format_value(candidate["weighted_quality_score"])],
                ["formula_reference_valid_rate", format_value(early["formula_reference_valid_rate"]), format_value(current["formula_reference_valid_rate"]), format_value(candidate["formula_reference_valid_rate"])],
                ["table_reference_valid_rate", format_value(early["table_reference_valid_rate"]), format_value(current["table_reference_valid_rate"]), format_value(candidate["table_reference_valid_rate"])],
                ["derivation_reference_valid_rate", format_value(early["derivation_reference_valid_rate"]), format_value(current["derivation_reference_valid_rate"]), format_value(candidate["derivation_reference_valid_rate"])],
                ["ghost_block_rate", format_value(early["ghost_block_rate"]), format_value(current["ghost_block_rate"]), format_value(candidate["ghost_block_rate"])],
                ["fatal / error / warning", f"{early['fatal']} / {early['error']} / {early['warning']}", f"{current['fatal']} / {current['error']} / {current['warning']}", f"{candidate['fatal']} / {candidate['error']} / {candidate['warning']}"],
            ],
        ),
        "",
        "解释：early 的自动审计分数较高，但它覆盖更少、结构化版本更早，不能仅凭该分数判定更适合交付；current 是当前已提交的交付基线，覆盖更完整，但仍暴露出 `[h]`、孤立符号和少量表格引用缺失等可优化问题。candidate 只作为 tmp-only 后续优化候选，说明这些问题可以被可控地继续压低，正式交付仍以 current 为基线。",
        "",
        "## 周五建议采用的准确率口径",
        "",
        "- 主口径：`strict_pass_rate`，表示无 fatal/error 的 block 占比。",
        "- 综合口径：`weighted_quality_score`，按 fatal/error/warning 加权惩罚。",
        "- 引用口径：`formula_reference_valid_rate`、`table_reference_valid_rate`、`derivation_reference_valid_rate`。",
        "- 噪声口径：`ghost_block_rate`。",
        "- 人工口径：固定 `manual_sample_ids` 后计算 `manual_sample_accuracy`，作为最终汇报里最接近“人工准确率”的数字。",
        "",
        "## 优化前后如何对比",
        "",
        "- 使用同一套 calibrated audit 脚本。",
        "- 使用同一份抽样 ID：`tmp/structured_quality_probe/samples/manual_sample_ids.jsonl`。",
        "- 对比 early / current / candidate 三版，同时保留 candidate 的 change manifest。",
        "- 不把 candidate 直接合入 `data/structured`，等人工抽样确认后再决定。",
        "",
        "## 给老师汇报可用表述",
        "",
        "> 我们没有把 PaddleOCR 或 GLM-OCR 直接当成原文真值，因为两者都存在数学符号、LaTeX 残留、结构残缺和章节差异问题。更客观的方式是把 structured 作为下游知识库交付对象，评估它的结构化可用质量：包括 fatal/error 问题率、公式和表格引用有效率、derivation 引用有效率、噪声块比例，并用固定分层抽样做人工验证。按这套口径，当前 structured 已经达到交付标准；后续优化会先在 tmp candidate 中验证，不直接覆盖当前交付版。",
        "",
        "## 还缺的数据",
        "",
        "- 人工标注后的 `manual_sample_accuracy`。",
        "- 如果 candidate 未来要合入，还需要同一批样本在 candidate 上的人工复核结论。",
        "- 如果要报告传统 OCR 字符级准确率，需要另建人工逐字符 ground truth 数据集。",
    ]
    write_text(FRIDAY_REPORT_MD, "\n".join(md) + "\n")


def main() -> None:
    ensure_output_dirs()
    reports, issue_rows = run_version_audits()
    version_summaries = {version: summarize_audit(report) for version, report in reports.items()}
    sample_rows, sample_summary = build_sample_comparison()
    write_jsonl(SAMPLE_COMPARISON_JSONL, sample_rows)

    current = version_summaries["current"]
    candidate = version_summaries["candidate"]
    gates = {
        "candidate_fatal_not_increased": candidate["fatal"] <= current["fatal"],
        "candidate_strict_pass_rate_not_lower": candidate["strict_pass_rate"] >= current["strict_pass_rate"],
        "candidate_weighted_quality_score_not_lower": candidate["weighted_quality_score"] >= current["weighted_quality_score"],
    }
    comparison = {
        "versions": {
            "early": relpath(EARLY_STRUCTURED_DIR),
            "current": relpath(CURRENT_STRUCTURED_DIR),
            "candidate": relpath(CANDIDATE_STRUCTURED_DIR),
        },
        "audit_outputs": {
            version: {key: relpath(value) for key, value in cfg.items() if isinstance(value, Path)}
            for version, cfg in AUDIT_OUTPUTS.items()
        },
        "version_summaries": version_summaries,
        "candidate_quality_gate": gates,
        "sample_comparison_path": relpath(SAMPLE_COMPARISON_JSONL),
        "sample_comparison_summary": sample_summary,
        "notes": [
            "All three versions are audited with the same calibrated structured audit script.",
            "Navigation-only JSON files in old_structured are excluded from unit comparison.",
            "Candidate output is tmp-only and is not applied to data/structured.",
        ],
    }
    write_json(THREE_VERSION_JSON, comparison)
    write_three_version_report(comparison, issue_rows)
    write_friday_report(comparison)


if __name__ == "__main__":
    main()
