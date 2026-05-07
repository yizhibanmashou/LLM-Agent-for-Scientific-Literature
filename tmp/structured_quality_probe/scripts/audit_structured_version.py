from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import (
    FORMULA_LIKE_BLOCK_TYPES,
    LATEX_LEAK_COMMANDS,
    PLACEHOLDER_RE,
    PROJECT_ROOT,
    STRUCTURAL_LATEX_COMMANDS,
    chapter_sort_key,
    clean_ref_id,
    count_placeholders,
    ensure_output_dirs,
    extract_formula_refs,
    extract_table_refs,
    find_broken_placeholders,
    has_excessive_whitespace,
    has_readable_text,
    has_unbalanced_math,
    is_ghost_block,
    latex_commands,
    load_json,
    markdown_table,
    natural_key,
    possible_ocr_garbled_text,
    relpath,
    suspicious_non_english_noise,
    suspicious_truncation,
    write_json,
    write_jsonl,
    write_text,
)


SEVERITY_WEIGHT = {"fatal": 0, "error": 1, "warning": 2, "info": 3}
LIBRARY_NAMES = {"formula_library.json", "table_library.json"}
NAV_RE = re.compile(r"(?:_nav_\d+|_toc_tree)$", re.IGNORECASE)


def is_navigation_json(path: Path) -> bool:
    stem = path.stem
    return bool(NAV_RE.search(stem))


def iter_unit_files(structured_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(structured_dir.glob("*.json"), key=lambda item: natural_key(item.name)):
        if path.name in LIBRARY_NAMES or is_navigation_json(path):
            continue
        # Keep chapter/appendix unit files even if malformed so audit can report them.
        stem = path.stem.lower()
        if re.match(r"^(chapter|appendix)\d+_", stem):
            files.append(path)
            continue
        try:
            data = load_json(path)
        except Exception:
            files.append(path)
            continue
        if isinstance(data, dict) and isinstance(data.get("blocks"), list):
            files.append(path)
    return files


def chapter_from_path(path: Path, data: dict[str, Any] | None) -> str:
    if isinstance(data, dict):
        metadata = data.get("metadata")
        if isinstance(metadata, dict) and metadata.get("chapter"):
            return str(metadata["chapter"]).strip().lower()
    stem = path.stem.lower()
    if "_" in stem:
        return stem.split("_", 1)[0]
    return stem


def add_issue(
    issues: list[dict[str, Any]],
    severity: str,
    issue_type: str,
    chapter: str,
    file_path: Path,
    block_index: int | None,
    block_type: str | None,
    content: str,
    details: dict[str, Any] | None = None,
) -> None:
    issues.append(
        {
            "severity": severity,
            "issue_type": issue_type,
            "chapter": chapter,
            "file": relpath(file_path),
            "block_index": block_index,
            "block_type": block_type,
            "sample": content,
            "sample_snippet": content if len(content) <= 300 else content[:297] + "...",
            "details": details or {},
        }
    )


def load_library(
    structured_dir: Path,
    filename: str,
    list_key: str,
    expected_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    path = structured_dir / filename
    issues: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    source_map: dict[str, dict[str, Any]] = {}
    if not path.exists():
        add_issue(issues, "fatal", "json_parse_error", expected_name, path, None, None, "", {"reason": "missing_file"})
        return items, issues, source_map
    try:
        data = load_json(path)
    except Exception as exc:
        add_issue(issues, "fatal", "json_parse_error", expected_name, path, None, None, "", {"error": str(exc)})
        return items, issues, source_map
    if not isinstance(data, dict) or not isinstance(data.get(list_key), list):
        add_issue(
            issues,
            "fatal",
            "missing_required_fields",
            expected_name,
            path,
            None,
            None,
            "",
            {"required_list_key": list_key},
        )
        return items, issues, source_map
    for idx, item in enumerate(data[list_key]):
        if not isinstance(item, dict):
            add_issue(
                issues,
                "fatal",
                "missing_required_fields",
                expected_name,
                path,
                None,
                None,
                "",
                {"entry_index": idx, "reason": "non_dict_entry"},
            )
            continue
        item_id = clean_ref_id(str(item.get("id", "")))
        if not item_id:
            add_issue(
                issues,
                "fatal",
                "missing_required_fields",
                expected_name,
                path,
                None,
                None,
                "",
                {"entry_index": idx, "reason": "missing_id"},
            )
            continue
        items.append(item)
        if expected_name == "formula_library":
            source = item.get("source")
            source_map[item_id] = source if isinstance(source, dict) else {}
    return items, issues, source_map


def strip_balanced_math(text: str) -> str:
    value = text or ""
    value = re.sub(r"\\\[[\s\S]*?\\\]", " ", value)
    value = re.sub(r"\\\([\s\S]*?\\\)", " ", value)
    value = re.sub(r"(?<!\$)\$\$(?!\$)[\s\S]*?(?<!\$)\$\$(?!\$)", " ", value)
    value = re.sub(r"(?<!\$)\$(?!\$)[^\n$]*?(?<!\$)\$(?!\$)", " ", value)
    value = PLACEHOLDER_RE.sub(" ", value)
    return value


def calibrated_tex_command_leak(text: str, block_type: str) -> tuple[bool, list[str]]:
    outside_math = strip_balanced_math(text)
    commands = [cmd.lower() for cmd in latex_commands(outside_math)]
    if not commands:
        return False, []
    structural_hits = sorted(set(cmd for cmd in commands if cmd in STRUCTURAL_LATEX_COMMANDS))
    leak_hits = sorted(set(cmd for cmd in commands if cmd in LATEX_LEAK_COMMANDS))
    hits = sorted(set(structural_hits + leak_hits))
    if not hits:
        return False, []
    block_type = (block_type or "").lower()
    if block_type in FORMULA_LIKE_BLOCK_TYPES and set(hits).issubset({"begin", "end"}):
        return False, hits
    return True, hits


def inspect_block(
    *,
    issues: list[dict[str, Any]],
    file_path: Path,
    chapter: str,
    block_index: int,
    block: Any,
    formula_ids: set[str],
    table_ids: set[str],
    formula_sources: dict[str, dict[str, Any]],
    severity_counts: Counter,
    issue_type_counts: Counter,
    chapter_issue_counts: Counter,
    block_severity_map: dict[tuple[str, int], set[str]],
    reference_totals: Counter,
    reference_valids: Counter,
    block_type_counts: Counter,
) -> None:
    block_key = (relpath(file_path), block_index)
    if not isinstance(block, dict):
        add_issue(
            issues,
            "fatal",
            "missing_required_fields",
            chapter,
            file_path,
            block_index,
            "unknown",
            "",
            {"reason": "non_dict_block"},
        )
        severity_counts["fatal"] += 1
        issue_type_counts["missing_required_fields"] += 1
        chapter_issue_counts[chapter] += 1
        block_severity_map[block_key].add("fatal")
        return

    block_type = str(block.get("type", "unknown")).strip() or "unknown"
    block_type_counts[block_type] += 1

    if "type" not in block or "content" not in block:
        add_issue(
            issues,
            "fatal",
            "missing_required_fields",
            chapter,
            file_path,
            block_index,
            block_type,
            "",
            {"missing_keys": [key for key in ("type", "content") if key not in block]},
        )
        severity_counts["fatal"] += 1
        issue_type_counts["missing_required_fields"] += 1
        chapter_issue_counts[chapter] += 1
        block_severity_map[block_key].add("fatal")
        return

    content = block.get("content")
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False) if content is not None else ""
    content_strip = content.strip()

    def record(severity: str, issue_type: str, details: dict[str, Any] | None = None) -> None:
        add_issue(issues, severity, issue_type, chapter, file_path, block_index, block_type, content, details)
        severity_counts[severity] += 1
        issue_type_counts[issue_type] += 1
        chapter_issue_counts[chapter] += 1
        block_severity_map[block_key].add(severity)

    if content_strip == "":
        record("fatal", "empty_content", {"reason": "blank_after_strip"})
        return
    if content_strip == "[h]":
        record("error", "h_only_block", {"matched": "[h]"})
    if is_ghost_block(content_strip):
        record("error", "ghost_block", {"reason": "symbol_only_or_page_like"})
    if has_unbalanced_math(content):
        record("error", "unbalanced_inline_math", {"dollar_count": content.count("$")})
    leak, commands = calibrated_tex_command_leak(content, block_type)
    if leak:
        record("error", "tex_command_leak", {"commands": commands[:12], "calibration": "math_spans_ignored"})
    broken = find_broken_placeholders(content)
    if broken:
        record("error", "broken_placeholder", {"count": len(broken), "examples": broken[:3]})
    if suspicious_truncation(content):
        record("error", "suspicious_truncation", {"reason": "unclosed_delimiter_or_quote"})
    if len(content_strip) < 20:
        record("warning", "very_short_block", {"length": len(content_strip)})
    if block_type.lower() == "discussion":
        placeholder_count = count_placeholders(content)
        if placeholder_count >= 3:
            record("warning", "placeholder_in_discussion", {"placeholder_count": placeholder_count})
    if has_excessive_whitespace(content):
        record("warning", "excessive_whitespace", {"length": len(content)})
    if suspicious_non_english_noise(content):
        record("warning", "suspicious_non_english_noise", {"reason": "unexpected_non_english_script_or_noise"})
    garbled, garbled_details = possible_ocr_garbled_text(content)
    if garbled:
        record("warning", "possible_ocr_garbled_text", garbled_details)

    formula_refs = extract_formula_refs(content)
    table_refs = extract_table_refs(content)
    reference_totals["formula"] += len(formula_refs)
    reference_totals["table"] += len(table_refs)
    for ref in formula_refs:
        if ref in formula_ids:
            reference_valids["formula"] += 1
        else:
            record("fatal", "formula_reference_missing", {"missing_ref": ref})
    for ref in table_refs:
        if ref in table_ids:
            reference_valids["table"] += 1
        else:
            record("fatal", "table_reference_missing", {"missing_ref": ref})

    if block_type.lower() == "derivation":
        derivation_refs = formula_refs
        reference_totals["derivation_formula"] += len(derivation_refs)
        reference_valids["derivation_formula"] += sum(1 for ref in derivation_refs if ref in formula_ids)
        if len(derivation_refs) > 8:
            record("warning", "derivation_too_many_formula_refs", {"formula_ref_count": len(derivation_refs)})
        cleaned = PLACEHOLDER_RE.sub(" ", content)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not has_readable_text(content, min_words=3):
            record("warning", "derivation_placeholder_only_text", {"cleaned_preview": cleaned[:120]})
        ref_chapters: list[str] = []
        for ref in derivation_refs:
            source = formula_sources.get(ref, {})
            ref_chapter = str(source.get("chapter", "")).strip().lower()
            if ref_chapter:
                ref_chapters.append(ref_chapter)
        if ref_chapters:
            unique_ref_chapters = sorted(set(ref_chapters), key=chapter_sort_key)
            if any(ref_chapter != chapter for ref_chapter in unique_ref_chapters):
                record(
                    "info",
                    "derivation_cross_chapter_reference",
                    {"current_chapter": chapter, "referenced_chapters": unique_ref_chapters},
                )


def build_sorted_issue_rows(issues: list[dict[str, Any]], issue_type_counts: Counter) -> list[dict[str, Any]]:
    def sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
        severity = item["severity"]
        issue_type = item["issue_type"]
        return (
            SEVERITY_WEIGHT.get(severity, 99),
            -issue_type_counts[issue_type],
            chapter_sort_key(str(item["chapter"])),
            item["file"],
            -1 if item["block_index"] is None else int(item["block_index"]),
            issue_type,
        )

    rows = sorted(issues, key=sort_key)
    for idx, row in enumerate(rows, start=1):
        row["rank"] = idx
    return rows


def audit_structured_dir(structured_dir: Path, label: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    structured_dir = structured_dir.resolve()
    issues: list[dict[str, Any]] = []
    severity_counts: Counter = Counter()
    issue_type_counts: Counter = Counter()
    chapter_issue_counts: Counter = Counter()
    block_type_counts: Counter = Counter()
    block_severity_map: dict[tuple[str, int], set[str]] = defaultdict(set)
    reference_totals: Counter = Counter()
    reference_valids: Counter = Counter()
    file_records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    formula_items, formula_issues, formula_sources = load_library(structured_dir, "formula_library.json", "formulas", "formula_library")
    table_items, table_issues, _ = load_library(structured_dir, "table_library.json", "tables", "table_library")
    issues.extend(formula_issues)
    issues.extend(table_issues)
    for lib_issue in formula_issues + table_issues:
        severity_counts[lib_issue["severity"]] += 1
        issue_type_counts[lib_issue["issue_type"]] += 1
        chapter_issue_counts[lib_issue["chapter"]] += 1

    formula_ids = {clean_ref_id(str(item.get("id", ""))) for item in formula_items if clean_ref_id(str(item.get("id", "")))}
    table_ids = {clean_ref_id(str(item.get("id", ""))) for item in table_items if clean_ref_id(str(item.get("id", "")))}

    structured_files = iter_unit_files(structured_dir)
    total_blocks = 0
    for file_path in structured_files:
        try:
            data = load_json(file_path)
        except Exception as exc:
            chapter = file_path.stem.split("_", 1)[0].lower()
            add_issue(issues, "fatal", "json_parse_error", chapter, file_path, None, None, "", {"error": str(exc)})
            severity_counts["fatal"] += 1
            issue_type_counts["json_parse_error"] += 1
            chapter_issue_counts[chapter] += 1
            parse_errors.append({"file": relpath(file_path), "error": str(exc)})
            continue

        chapter = chapter_from_path(file_path, data if isinstance(data, dict) else None)
        if not isinstance(data, dict):
            add_issue(issues, "fatal", "missing_required_fields", chapter, file_path, None, None, "", {"reason": "root_not_dict"})
            severity_counts["fatal"] += 1
            issue_type_counts["missing_required_fields"] += 1
            chapter_issue_counts[chapter] += 1
            parse_errors.append({"file": relpath(file_path), "error": "root_not_dict"})
            continue

        missing_fields = [key for key in ("id", "metadata", "blocks") if key not in data]
        metadata = data.get("metadata")
        if not isinstance(metadata, dict) or not metadata.get("chapter"):
            missing_fields.append("metadata.chapter")
        blocks = data.get("blocks")
        if missing_fields:
            add_issue(issues, "fatal", "missing_required_fields", chapter, file_path, None, None, "", {"missing_fields": missing_fields})
            severity_counts["fatal"] += 1
            issue_type_counts["missing_required_fields"] += 1
            chapter_issue_counts[chapter] += 1
        if not isinstance(blocks, list):
            parse_errors.append({"file": relpath(file_path), "error": "blocks_not_list"})
            continue

        for idx, block in enumerate(blocks):
            total_blocks += 1
            inspect_block(
                issues=issues,
                file_path=file_path,
                chapter=chapter,
                block_index=idx,
                block=block,
                formula_ids=formula_ids,
                table_ids=table_ids,
                formula_sources=formula_sources,
                severity_counts=severity_counts,
                issue_type_counts=issue_type_counts,
                chapter_issue_counts=chapter_issue_counts,
                block_severity_map=block_severity_map,
                reference_totals=reference_totals,
                reference_valids=reference_valids,
                block_type_counts=block_type_counts,
            )
            if isinstance(block, dict):
                file_records.append(
                    {
                        "file": relpath(file_path),
                        "chapter": chapter,
                        "block_index": idx,
                        "block_type": str(block.get("type", "unknown")),
                        "content": block.get("content"),
                    }
                )

    sorted_issues = build_sorted_issue_rows(issues, issue_type_counts)
    failed_blocks = {key for key, severities in block_severity_map.items() if severities & {"fatal", "error"}}
    strict_pass_rate = ((total_blocks - len(failed_blocks)) / total_blocks) if total_blocks else 1.0
    fatal = severity_counts["fatal"]
    error = severity_counts["error"]
    warning = severity_counts["warning"]
    weighted_quality_score = 1 - ((5 * fatal + 3 * error + warning) / (5 * total_blocks)) if total_blocks else 1.0
    formula_reference_valid_rate = reference_valids["formula"] / reference_totals["formula"] if reference_totals["formula"] else None
    table_reference_valid_rate = reference_valids["table"] / reference_totals["table"] if reference_totals["table"] else None
    derivation_reference_valid_rate = (
        reference_valids["derivation_formula"] / reference_totals["derivation_formula"]
        if reference_totals["derivation_formula"]
        else None
    )
    ghost_blocks = sum(1 for record in file_records if is_ghost_block(str(record["content"]) if record["content"] is not None else ""))
    ghost_block_rate = ghost_blocks / total_blocks if total_blocks else 0.0

    report = {
        "label": label,
        "project_root": relpath(PROJECT_ROOT),
        "scan_scope": {
            "structured_dir": relpath(structured_dir),
            "structured_files": [relpath(p) for p in structured_files],
            "formula_library": relpath(structured_dir / "formula_library.json"),
            "table_library": relpath(structured_dir / "table_library.json"),
            "navigation_json_excluded": True,
        },
        "totals": {
            "total_files": len(structured_files) + 2,
            "structured_json_files": len(structured_files),
            "total_blocks": total_blocks,
            "block_type_counts": dict(sorted(block_type_counts.items(), key=lambda item: (-item[1], item[0]))),
        },
        "severity_counts": {key: severity_counts[key] for key in ("fatal", "error", "warning", "info")},
        "issue_type_counts": dict(sorted(issue_type_counts.items(), key=lambda item: (-item[1], item[0]))),
        "chapter_issue_counts": dict(sorted(chapter_issue_counts.items(), key=lambda item: (-item[1], natural_key(item[0])))),
        "reference_metrics": {
            "formula_reference_valid_rate": formula_reference_valid_rate,
            "table_reference_valid_rate": table_reference_valid_rate,
            "derivation_reference_valid_rate": derivation_reference_valid_rate,
            "ghost_block_rate": ghost_block_rate,
        },
        "quality_metrics": {
            "strict_pass_rate": strict_pass_rate,
            "weighted_quality_score": weighted_quality_score,
        },
        "library_counts": {
            "formula_library_entries": len(formula_items),
            "table_library_entries": len(table_items),
        },
        "parse_errors": parse_errors,
        "top_50_issue_samples": sorted_issues[:50],
        "notes": [
            "This is a structured usable-quality audit, not OCR character accuracy.",
            "The tex_command_leak detector ignores balanced inline/display math spans to avoid penalizing valid LaTeX math.",
        ],
    }
    return report, sorted_issues


def issue_md_table(top_rows: list[dict[str, Any]]) -> str:
    rows = []
    for item in top_rows:
        rows.append(
            [
                item["rank"],
                item["severity"],
                item["issue_type"],
                item["chapter"],
                item["file"],
                item["block_index"] if item["block_index"] is not None else "",
                item["block_type"] or "",
                item["sample_snippet"],
            ]
        )
    return markdown_table(["rank", "severity", "issue_type", "chapter", "file", "block", "block_type", "sample"], rows)


def write_audit_outputs(
    report: dict[str, Any],
    sorted_issues: list[dict[str, Any]],
    json_path: Path,
    md_path: Path,
    samples_path: Path,
) -> None:
    write_json(json_path, report)
    write_jsonl(samples_path, sorted_issues)
    severity_counts = report["severity_counts"]
    block_type_counts = report["totals"]["block_type_counts"]
    issue_type_counts = report["issue_type_counts"]
    chapter_issue_counts = report["chapter_issue_counts"]
    metrics = report["quality_metrics"] | report["reference_metrics"]

    metric_rows = []
    for key, value in metrics.items():
        if value is None:
            rendered = "N/A"
        elif isinstance(value, float):
            rendered = f"{value:.6f}"
        else:
            rendered = str(value)
        metric_rows.append([key, rendered])

    md = [
        f"# Structured Quality Audit: {report['label']}",
        "",
        "本报告是 **structured 可用质量通过率** 审计，不是 OCR 字符级准确率。",
        "",
        "## 总览",
        "",
        markdown_table(
            ["指标", "值"],
            [
                ["structured_dir", report["scan_scope"]["structured_dir"]],
                ["总文件数", report["totals"]["total_files"]],
                ["structured JSON 文件数", report["totals"]["structured_json_files"]],
                ["总 block 数", report["totals"]["total_blocks"]],
                ["formula_library 条目", report["library_counts"]["formula_library_entries"]],
                ["table_library 条目", report["library_counts"]["table_library_entries"]],
            ],
        ),
        "",
        "## block.type 统计",
        "",
        markdown_table(["block.type", "数量"], [[k, v] for k, v in block_type_counts.items()]),
        "",
        "## 严重级别统计",
        "",
        markdown_table(["severity", "数量"], [[k, severity_counts.get(k, 0)] for k in ("fatal", "error", "warning", "info")]),
        "",
        "## issue_type 统计",
        "",
        markdown_table(["issue_type", "数量"], [[k, v] for k, v in issue_type_counts.items()]),
        "",
        "## chapter 统计",
        "",
        markdown_table(["chapter", "数量"], [[k, v] for k, v in chapter_issue_counts.items()]),
        "",
        "## 关键指标",
        "",
        markdown_table(["metric", "value"], metric_rows),
        "",
        "## 前 50 个问题样例",
        "",
        issue_md_table(report["top_50_issue_samples"]),
        "",
        "## 备注",
        "",
        "- 本版审计忽略平衡数学片段内部的合法 LaTeX 命令，因此更适合作为三版客观比较口径。",
        "- 引用有效率检查仍以对应版本自己的 formula/table library 为准。",
    ]
    write_text(md_path, "\n".join(md) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structured-dir", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--out-samples", required=True)
    args = parser.parse_args()

    ensure_output_dirs()
    report, sorted_issues = audit_structured_dir(Path(args.structured_dir), args.label)
    write_audit_outputs(report, sorted_issues, Path(args.out_json), Path(args.out_md), Path(args.out_samples))


if __name__ == "__main__":
    main()
