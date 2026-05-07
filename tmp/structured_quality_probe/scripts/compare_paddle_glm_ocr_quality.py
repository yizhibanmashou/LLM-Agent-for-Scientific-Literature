from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import (
    FALLBACK_GLMOCR_DIR,
    FALLBACK_PADDLE_DIR,
    PROJECT_ROOT,
    REQUESTED_GLMOCR_DIR,
    REQUESTED_PADDLE_DIR,
    chapter_sort_key,
    discover_ocr_text_sources,
    ensure_output_dirs,
    extract_json_text,
    formula_marker_count,
    has_unbalanced_math,
    latex_environment_mismatches,
    load_json,
    markdown_table,
    normalize_text_for_comparison,
    natural_key,
    possible_ocr_garbled_text,
    read_text,
    relpath,
    suspicious_non_english_noise,
    tex_command_leak,
    write_json,
    write_jsonl,
    write_text,
)


SEED = 20260505


def select_root(requested: Path, fallback: Path) -> tuple[Path, str]:
    if fallback.exists():
        return fallback, "fallback_tmp"
    return requested, "requested"


def load_source_document(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    raw_text = read_text(path)
    if suffix == ".json":
        try:
            data = load_json(path)
            content_text = extract_json_text(data)
        except Exception:
            content_text = raw_text
    else:
        content_text = raw_text
    normalized_text = normalize_text_for_comparison(content_text)
    return {
        "path": relpath(path),
        "extension": suffix,
        "raw_text": raw_text,
        "content_text": content_text,
        "normalized_text": normalized_text,
        "normalized_length": len(normalized_text),
        "raw_length": len(raw_text),
        "formula_count": formula_marker_count(content_text),
        "math_unbalanced": has_unbalanced_math(content_text),
        "latex_residue": tex_command_leak(content_text, "")[0],
        "latex_residue_hits": tex_command_leak(content_text, "")[1],
        "env_mismatches": latex_environment_mismatches(content_text),
        "garbled": possible_ocr_garbled_text(normalized_text)[0],
        "garbled_details": possible_ocr_garbled_text(normalized_text)[1],
        "noise": suspicious_non_english_noise(normalized_text),
    }


def chapter_issue_flags(doc: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    text = doc["normalized_text"]
    if len(text.strip()) == 0:
        issues.append({"issue_type": "empty_content", "severity": "error", "details": {"reason": "empty_after_normalization"}})
    elif len(text.strip()) < 250:
        issues.append(
            {
                "issue_type": "very_short_content",
                "severity": "warning",
                "details": {"normalized_length": len(text.strip())},
            }
        )
    if doc["math_unbalanced"]:
        issues.append({"issue_type": "unbalanced_inline_math", "severity": "error", "details": {"formula_count": doc["formula_count"]}})
    if doc["latex_residue"]:
        issues.append(
            {
                "issue_type": "latex_command_residue",
                "severity": "warning",
                "details": {"hits": doc["latex_residue_hits"][:12]},
            }
        )
    if doc["env_mismatches"]:
        issues.append(
            {
                "issue_type": "formula_env_mismatch",
                "severity": "error",
                "details": doc["env_mismatches"],
            }
        )
    if doc["noise"]:
        issues.append({"issue_type": "suspicious_non_english_noise", "severity": "warning", "details": {}})
    if doc["garbled"]:
        issues.append({"issue_type": "possible_ocr_garbled_text", "severity": "warning", "details": doc["garbled_details"]})
    return issues


def paired_window_snippet(
    left: str,
    right: str,
    width: int = 240,
    rng: random.Random | None = None,
) -> tuple[str, str, str]:
    if not left and not right:
        return "", "", "both_empty"
    if rng is None:
        rng = random.Random(SEED + len(left) + len(right))
    if not left:
        return "", random_window(right, width, rng), "left_empty"
    if not right:
        return random_window(left, width, rng), "", "right_empty"
    ratio = rng.uniform(0.08, 0.92)
    left_start = int(max(0, len(left) - width) * ratio)
    right_start = int(max(0, len(right) - width) * ratio)
    tag = "paired_window_identical" if left == right else "paired_window_different"
    return snippet_window(left, left_start, width), snippet_window(right, right_start, width), tag


def snippet_window(text: str, start: int, width: int) -> str:
    if not text:
        return ""
    end = min(len(text), start + width)
    return " ".join(text[start:end].split())


def random_window(text: str, width: int, rng: random.Random | None = None) -> str:
    if not text:
        return ""
    if len(text) <= width:
        return " ".join(text.split())
    if rng is None:
        rng = random.Random(SEED + len(text))
    start = rng.randint(0, max(0, len(text) - width))
    return " ".join(text[start : start + width].split())


def format_issue_summary(issue_map: dict[str, Counter]) -> list[list[Any]]:
    rows = []
    for source_name, counts in issue_map.items():
        for issue_type, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            rows.append([source_name, issue_type, count])
    return rows


def compare_chapter_docs(
    chapter: str,
    paddle_doc: dict[str, Any],
    glm_doc: dict[str, Any],
) -> dict[str, Any]:
    paddle_len = paddle_doc["normalized_length"]
    glm_len = glm_doc["normalized_length"]
    length_gap = abs(paddle_len - glm_len)
    length_gap_ratio = length_gap / max(paddle_len, glm_len, 1)
    formula_gap = abs(paddle_doc["formula_count"] - glm_doc["formula_count"])
    formula_gap_ratio = formula_gap / max(paddle_doc["formula_count"], glm_doc["formula_count"], 1)
    env_gap = abs(len(paddle_doc["env_mismatches"]) - len(glm_doc["env_mismatches"]))
    combined_score = round(length_gap_ratio * 100 + formula_gap * 4 + env_gap * 10, 4)
    paddle_issues = chapter_issue_flags(paddle_doc)
    glm_issues = chapter_issue_flags(glm_doc)
    return {
        "chapter": chapter,
        "paddle": {
            "path": paddle_doc["path"],
            "normalized_length": paddle_len,
            "raw_length": paddle_doc["raw_length"],
            "formula_count": paddle_doc["formula_count"],
            "issues": paddle_issues,
        },
        "glmocr": {
            "path": glm_doc["path"],
            "normalized_length": glm_len,
            "raw_length": glm_doc["raw_length"],
            "formula_count": glm_doc["formula_count"],
            "issues": glm_issues,
        },
        "length_gap": length_gap,
        "length_gap_ratio": length_gap_ratio,
        "formula_gap": formula_gap,
        "formula_gap_ratio": formula_gap_ratio,
        "env_gap": env_gap,
        "combined_score": combined_score,
        "flags": {
            "paddle_problem": bool(paddle_issues),
            "glmocr_problem": bool(glm_issues),
            "any_problem": bool(paddle_issues or glm_issues or length_gap_ratio >= 0.2 or formula_gap >= 5),
        },
    }


def build_sample_record(
    chapter: str,
    comp: dict[str, Any],
    paddle_doc: dict[str, Any],
    glm_doc: dict[str, Any],
) -> dict[str, Any]:
    left_snippet, right_snippet, diff_tag = paired_window_snippet(
        paddle_doc.get("normalized_text", ""),
        glm_doc.get("normalized_text", ""),
        width=260,
        rng=random.Random(SEED + sum(ord(ch) for ch in chapter)),
    )
    if not left_snippet:
        left_snippet = random_window(paddle_doc.get("normalized_text", ""), 260)
    if not right_snippet:
        right_snippet = random_window(glm_doc.get("normalized_text", ""), 260)
    reason = []
    if comp["length_gap_ratio"] >= 0.2:
        reason.append("length_gap")
    if comp["formula_gap"] >= 5:
        reason.append("formula_gap")
    if comp["env_gap"] > 0:
        reason.append("env_gap")
    if comp["paddle"]["issues"] or comp["glmocr"]["issues"]:
        reason.append("source_issue")
    if not reason:
        reason.append("random_fragment")
    return {
        "chapter": chapter,
        "paddle_path": paddle_doc["path"],
        "glmocr_path": glm_doc["path"],
        "paddle_snippet": left_snippet,
        "glmocr_snippet": right_snippet,
        "diff_tag": diff_tag,
        "reason": reason,
        "length_gap_ratio": comp["length_gap_ratio"],
        "formula_gap": comp["formula_gap"],
        "env_gap": comp["env_gap"],
        "combined_score": comp["combined_score"],
        "paddle_formula_count": paddle_doc["formula_count"],
        "glmocr_formula_count": glm_doc["formula_count"],
        "paddle_length": paddle_doc["normalized_length"],
        "glmocr_length": glm_doc["normalized_length"],
        "seed": SEED,
    }


def main() -> None:
    ensure_output_dirs()

    paddle_root, paddle_root_kind = select_root(REQUESTED_PADDLE_DIR, FALLBACK_PADDLE_DIR)
    glmocr_root, glmocr_root_kind = select_root(REQUESTED_GLMOCR_DIR, FALLBACK_GLMOCR_DIR)

    paddle_sources = discover_ocr_text_sources(paddle_root)
    glmocr_sources = discover_ocr_text_sources(glmocr_root)
    paddle_docs = {chapter: load_source_document(info["path"]) for chapter, info in paddle_sources.items() if chapter != "toc"}
    glmocr_docs = {chapter: load_source_document(info["path"]) for chapter, info in glmocr_sources.items() if chapter != "toc"}

    shared_chapters = sorted(set(paddle_docs) & set(glmocr_docs), key=chapter_sort_key)
    paddle_only = sorted(set(paddle_docs) - set(glmocr_docs), key=chapter_sort_key)
    glmocr_only = sorted(set(glmocr_docs) - set(paddle_docs), key=chapter_sort_key)

    chapter_comparisons = [compare_chapter_docs(chapter, paddle_docs[chapter], glmocr_docs[chapter]) for chapter in shared_chapters]

    source_issue_unique_chapters: dict[str, dict[str, set[str]]] = {
        "paddle": defaultdict(set),
        "glmocr": defaultdict(set),
    }
    source_issue_occurrences: dict[str, Counter] = {
        "paddle": Counter(),
        "glmocr": Counter(),
    }
    source_problem_chapters: dict[str, set[str]] = {
        "paddle": set(),
        "glmocr": set(),
    }
    for chapter, comp in zip(shared_chapters, chapter_comparisons):
        for issue in comp["paddle"]["issues"]:
            source_issue_unique_chapters["paddle"][issue["issue_type"]].add(chapter)
            source_issue_occurrences["paddle"][issue["issue_type"]] += 1
            source_problem_chapters["paddle"].add(chapter)
        for issue in comp["glmocr"]["issues"]:
            source_issue_unique_chapters["glmocr"][issue["issue_type"]].add(chapter)
            source_issue_occurrences["glmocr"][issue["issue_type"]] += 1
            source_problem_chapters["glmocr"].add(chapter)

    coverage_summary = {
        "shared_chapters": len(shared_chapters),
        "paddle_only_chapters": paddle_only,
        "glmocr_only_chapters": glmocr_only,
        "paddle_missing_against_glmocr_count": len(glmocr_only),
        "glmocr_missing_against_paddle_count": len(paddle_only),
    }

    length_gap_threshold = 0.2
    formula_gap_threshold = 5
    env_gap_threshold = 1
    length_gap_outliers = [item for item in chapter_comparisons if item["length_gap_ratio"] >= length_gap_threshold]
    formula_gap_outliers = [item for item in chapter_comparisons if item["formula_gap"] >= formula_gap_threshold]
    env_gap_outliers = [item for item in chapter_comparisons if item["env_gap"] >= env_gap_threshold]

    comparison_outliers = sorted(chapter_comparisons, key=lambda item: (-item["combined_score"], chapter_sort_key(item["chapter"])))
    sample_pool = comparison_outliers[: min(20, len(comparison_outliers))]
    sample_rng = random.Random(SEED)
    selected_for_samples = sample_rng.sample(sample_pool, k=min(10, len(sample_pool)))
    selected_for_samples.sort(key=lambda item: (-item["combined_score"], chapter_sort_key(item["chapter"])))
    samples = [
        build_sample_record(
            item["chapter"],
            item,
            paddle_docs[item["chapter"]],
            glmocr_docs[item["chapter"]],
        )
        for item in selected_for_samples
    ]

    sample_path = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "samples" / "paddle_glm_disagreement_samples.jsonl"
    json_path = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "reports" / "02_ocr_source_comparison.json"
    md_path = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "reports" / "02_ocr_source_comparison.md"

    report = {
        "project_root": relpath(PROJECT_ROOT),
        "source_roots": {
            "paddle": {
                "requested": relpath(REQUESTED_PADDLE_DIR),
                "selected": relpath(paddle_root),
                "selection_kind": paddle_root_kind,
                "chapter_count": len(paddle_docs),
                "paths": {chapter: doc["path"] for chapter, doc in paddle_docs.items()},
            },
            "glmocr": {
                "requested": relpath(REQUESTED_GLMOCR_DIR),
                "selected": relpath(glmocr_root),
                "selection_kind": glmocr_root_kind,
                "chapter_count": len(glmocr_docs),
                "paths": {chapter: doc["path"] for chapter, doc in glmocr_docs.items()},
            },
        },
        "coverage": coverage_summary,
        "source_issue_summary": {
            "problem_chapter_count": {
                "paddle": len(source_problem_chapters["paddle"]),
                "glmocr": len(source_problem_chapters["glmocr"]),
            },
            "unique_chapter_counts": {
                "paddle": dict(sorted(((k, len(v)) for k, v in source_issue_unique_chapters["paddle"].items()), key=lambda item: (-item[1], item[0]))),
                "glmocr": dict(sorted(((k, len(v)) for k, v in source_issue_unique_chapters["glmocr"].items()), key=lambda item: (-item[1], item[0]))),
            },
            "occurrence_counts": {
                "paddle": dict(sorted(source_issue_occurrences["paddle"].items(), key=lambda item: (-item[1], item[0]))),
                "glmocr": dict(sorted(source_issue_occurrences["glmocr"].items(), key=lambda item: (-item[1], item[0]))),
            },
        },
        "chapter_comparisons": chapter_comparisons,
        "outlier_summary": {
            "length_gap_threshold": length_gap_threshold,
            "formula_gap_threshold": formula_gap_threshold,
            "env_gap_threshold": env_gap_threshold,
            "length_gap_outlier_count": len(length_gap_outliers),
            "formula_gap_outlier_count": len(formula_gap_outliers),
            "env_gap_outlier_count": len(env_gap_outliers),
            "top_disagreements": comparison_outliers[:10],
        },
        "samples": samples,
        "conclusion_points": [
            "PaddleOCR 可作为 structured 生产源，但不等于 ground truth。",
            "GLM-OCR 可作为修复参考源，但也不等于 ground truth。",
            "因此 structured 准确率不能用 Paddle vs GLM 简单互相比对得出。",
            "更合理的方法是全量自动质量审计 + 分层人工抽样验证。",
        ],
    }
    write_json(json_path, report)
    write_jsonl(sample_path, samples)

    source_rows = [
        [
            "PaddleOCR",
            report["source_roots"]["paddle"]["selected"],
            report["source_roots"]["paddle"]["chapter_count"],
            report["source_issue_summary"]["problem_chapter_count"]["paddle"],
        ],
        [
            "GLM-OCR",
            report["source_roots"]["glmocr"]["selected"],
            report["source_roots"]["glmocr"]["chapter_count"],
            report["source_issue_summary"]["problem_chapter_count"]["glmocr"],
        ],
    ]
    coverage_rows = [
        ["shared chapters", coverage_summary["shared_chapters"]],
        ["paddle only", len(paddle_only)],
        ["glmocr only", len(glmocr_only)],
    ]
    issue_rows = []
    for source_name in ("paddle", "glmocr"):
        for issue_type, count in report["source_issue_summary"]["unique_chapter_counts"][source_name].items():
            issue_rows.append([source_name, issue_type, count])
    issue_rows = sorted(issue_rows, key=lambda row: (-row[2], row[0], row[1]))
    outlier_rows = [
        [
            item["chapter"],
            f"{item['length_gap_ratio']:.3f}",
            item["formula_gap"],
            item["env_gap"],
            item["paddle"]["normalized_length"],
            item["glmocr"]["normalized_length"],
            item["paddle"]["formula_count"],
            item["glmocr"]["formula_count"],
        ]
        for item in comparison_outliers[:10]
    ]
    sample_rows = []
    for sample in samples:
        sample_rows.append(
            [
                sample["chapter"],
                ", ".join(sample["reason"]),
                sample["diff_tag"],
                sample["paddle_snippet"],
                sample["glmocr_snippet"],
            ]
        )

    md = [
        "# 02 OCR Source Comparison",
        "",
        "本报告说明：PaddleOCR 和 GLM-OCR 都有问题，因此不能直接把任一边当作绝对 ground truth。",
        "",
        "## 来源与覆盖",
        "",
        markdown_table(["source", "selected root", "chapter_count", "problem_chapter_count"], source_rows),
        "",
        markdown_table(["coverage item", "count"], coverage_rows),
        "",
        "## 源内问题概览",
        "",
        markdown_table(["source", "issue_type", "chapter_count"], issue_rows),
        "",
        "## 章节差异最大的前 10 项",
        "",
        markdown_table(["chapter", "length_gap_ratio", "formula_gap", "env_gap", "paddle_len", "glmocr_len", "paddle_formula", "glmocr_formula"], outlier_rows),
        "",
        "## 抽样片段",
        "",
        markdown_table(["chapter", "reason", "diff_tag", "paddle snippet", "glmocr snippet"], sample_rows),
        "",
        "## 结论",
        "",
        "- PaddleOCR 可作为 structured 生产源，但不等于 ground truth。",
        "- GLM-OCR 可作为修复参考源，但也不等于 ground truth。",
        "- 因此 structured 准确率不能用 Paddle vs GLM 简单互相比对得出。",
        "- 更合理的方法是全量自动质量审计 + 分层人工抽样验证。",
    ]
    write_text(md_path, "\n".join(md) + "\n")


if __name__ == "__main__":
    main()
