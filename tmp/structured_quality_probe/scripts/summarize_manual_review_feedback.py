from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import (
    PROJECT_ROOT,
    REPORTS_DIR,
    SAMPLES_DIR,
    ensure_output_dirs,
    load_json,
    markdown_table,
    relpath,
    snippet,
    write_json,
    write_jsonl,
    write_text,
)


REVIEW_APP_DIR = PROJECT_ROOT / "review_app"
REVIEW_DATASET_PATH = REVIEW_APP_DIR / "data" / "generated" / "review_dataset.json"
REVIEW_RECORDS_PATH = REVIEW_APP_DIR / "data" / "local" / "review_records.json"
ISSUE_TAXONOMY_PATH = REVIEW_APP_DIR / "data" / "local" / "issue_taxonomy.json"

REPORT_BASE = "13_manual_review_feedback_summary"
SAMPLE_OUTPUT = SAMPLES_DIR / "manual_review_issue_examples.jsonl"

TARGET_CHAPTERS = ["chapter5", "chapter13", "chapter16", "chapter25", "chapter26", "chapter27", "chapter28"]
TARGET_VIEW_ORDER = ["chunks", "formulas", "tables"]


def source_prefix(source_version: str) -> str:
    value = str(source_version or "").strip()
    return f"{value}::" if value else ""


def safe_json_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = load_json(path)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def normalize_record_key(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text


def infer_item_key(chapter: str, view: str, item: dict[str, Any]) -> str:
    return str(item.get("item_key") or f"{chapter}::{view}::{item.get('id') or ''}")


def build_item_index(review_dataset: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], str]:
    source_version = str(review_dataset.get("structured_source_version") or review_dataset.get("source_version") or "").strip()
    items: dict[str, dict[str, Any]] = {}
    for chapter in review_dataset.get("chapters", []) if isinstance(review_dataset.get("chapters"), list) else []:
        chapter_id = str(chapter.get("id") or "").strip().lower()
        if not chapter_id:
            continue
        chapter_data = review_dataset.get("data", {}).get(chapter_id, {}) if isinstance(review_dataset.get("data"), dict) else {}
        if not isinstance(chapter_data, dict):
            continue
        for view in TARGET_VIEW_ORDER:
            rows = chapter_data.get(view, [])
            if not isinstance(rows, list):
                continue
            for item in rows:
                if not isinstance(item, dict):
                    continue
                base_key = infer_item_key(chapter_id, view, item)
                prefixed_key = f"{source_prefix(source_version)}{base_key}" if source_version else base_key
                payload = {
                    "chapter": chapter_id,
                    "view": view,
                    "item_id": str(item.get("id") or "").strip(),
                    "item_key": base_key,
                    "source_version": source_version or "",
                    "title": str(item.get("title") or "").strip(),
                    "subtitle": str(item.get("subtitle") or "").strip(),
                    "excerpt": str(item.get("excerpt") or "").strip(),
                }
                items[base_key] = payload
                items[prefixed_key] = payload
    return items, source_version


def load_taxonomy(payload: dict[str, Any]) -> dict[str, Any]:
    categories = payload.get("categories", [])
    if not isinstance(categories, list):
        categories = []
    normalized: list[dict[str, Any]] = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        code = str(category.get("issue_code") or "").strip()
        if not code:
            continue
        normalized.append(
            {
                "issue_code": code,
                "label": str(category.get("label") or code).strip(),
                "scope": str(category.get("scope") or "text").strip(),
                "severity": str(category.get("severity") or "warning").strip().lower(),
                "status": str(category.get("status") or "manual_only").strip().lower(),
                "aliases": [str(alias).strip() for alias in category.get("aliases", []) if str(alias).strip()]
                if isinstance(category.get("aliases"), list)
                else [],
                "detector": category.get("detector") if isinstance(category.get("detector"), dict) else {"mode": "regex", "patterns": []},
            }
        )
    return {
        "version": payload.get("version", 1),
        "updated_at": str(payload.get("updated_at") or "").strip(),
        "categories": normalized,
    }


def build_taxonomy_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for category in taxonomy.get("categories", []) if isinstance(taxonomy.get("categories"), list) else []:
        if not isinstance(category, dict):
            continue
        code = str(category.get("issue_code") or "").strip()
        if code:
            result[code] = category
        for alias in category.get("aliases", []) if isinstance(category.get("aliases"), list) else []:
            alias_code = str(alias or "").strip()
            if alias_code and alias_code not in result:
                result[alias_code] = category
    return result


def chapter_sort_key(chapter_id: str) -> tuple[Any, ...]:
    text = str(chapter_id or "").lower()
    match = re.fullmatch(r"chapter(\d+)", text)
    if match:
        return (0, int(match.group(1)))
    match = re.fullmatch(r"appendix(\d+)", text)
    if match:
        return (1, int(match.group(1)))
    return (2, text)


def load_review_records() -> dict[str, Any]:
    payload = safe_json_load(REVIEW_RECORDS_PATH)
    raw_records = payload.get("records", {})
    return raw_records if isinstance(raw_records, dict) else {}


def summarize_records(
    review_dataset: dict[str, Any],
    item_index: dict[str, dict[str, Any]],
    records: dict[str, Any],
    taxonomy_index: dict[str, dict[str, Any]],
    source_version: str,
) -> dict[str, Any]:
    source_key_prefix = source_prefix(source_version)
    chapters = [str(chapter.get("id") or "").lower() for chapter in review_dataset.get("chapters", []) if isinstance(chapter, dict)]
    chapter_rows = {
        chapter_id: {view: 0 for view in TARGET_VIEW_ORDER}
        for chapter_id in chapters
    }
    chapter_reviewed = Counter()
    chapter_issue_counts = Counter()
    chapter_note_counts = Counter()
    issue_code_counts = Counter()
    severity_counts = Counter()
    status_counts = Counter()
    taxonomy_status_counts = Counter()
    issue_rows: list[dict[str, Any]] = []
    foreign_record_count = 0
    candidate_record_count = 0
    issue_id_counter = 1

    for record_key, record in records.items():
        normalized_key = normalize_record_key(record_key)
        if not normalized_key:
            continue
        if source_key_prefix and not normalized_key.startswith(source_key_prefix):
            foreign_record_count += 1
            continue
        candidate_record_count += 1
        base_key = normalized_key[len(source_key_prefix) :] if source_key_prefix and normalized_key.startswith(source_key_prefix) else normalized_key
        item = item_index.get(normalized_key) or item_index.get(base_key) or {}
        chapter = str(item.get("chapter") or "").lower()
        view = str(item.get("view") or "").lower()
        if chapter in chapter_rows and view in chapter_rows[chapter]:
            chapter_rows[chapter][view] += 1
            chapter_reviewed[chapter] += 1
        notes = record.get("notes", []) if isinstance(record, dict) else []
        issues = record.get("issues", []) if isinstance(record, dict) else []
        if isinstance(notes, list):
            chapter_note_counts[chapter] += len(notes)
        if not isinstance(issues, list):
            continue
        for issue in issues:
            if not isinstance(issue, dict):
                continue
            issue_code = str(issue.get("issue_code") or "uncategorized").strip() or "uncategorized"
            severity = str(issue.get("severity") or "warning").strip().lower()
            issue_code_counts[issue_code] += 1
            severity_counts[severity] += 1
            chapter_issue_counts[chapter] += 1
            taxonomy = taxonomy_index.get(issue_code)
            taxonomy_status = str(taxonomy.get("status") if taxonomy else "unknown").strip().lower() if taxonomy else "unknown"
            taxonomy_status_counts[taxonomy_status] += 1
            issue_rows.append(
                {
                    "sample_id": f"IR{issue_id_counter:04d}",
                    "record_key": normalized_key,
                    "base_key": base_key,
                    "chapter": chapter or str((issue.get("item_snapshot") or {}).get("chapter") or "").lower(),
                    "view": view or str((issue.get("item_snapshot") or {}).get("view") or "").lower(),
                    "item_id": item.get("item_id") or str((issue.get("item_snapshot") or {}).get("item_id") or ""),
                    "item_key": item.get("item_key") or base_key,
                    "source_version": item.get("source_version") or str((issue.get("item_snapshot") or {}).get("source_version") or source_version),
                    "issue_code": issue_code,
                    "issue_label": str(issue.get("issue_label") or (taxonomy.get("label") if taxonomy else issue_code)).strip(),
                    "severity": severity,
                    "scope": str(issue.get("scope") or (taxonomy.get("scope") if taxonomy else "")).strip(),
                    "bad_span": str(issue.get("bad_span") or "").strip(),
                    "expected": str(issue.get("expected") or "").strip(),
                    "context": str(issue.get("context") or "").strip(),
                    "target_id": str(issue.get("target_id") or "").strip(),
                    "evidence": str(issue.get("evidence") or "").strip(),
                    "note": str(issue.get("note") or "").strip(),
                    "created_at": str(issue.get("created_at") or "").strip(),
                    "taxonomy_status": taxonomy_status,
                    "record_status": str(record.get("status") or "pending").strip().lower() if isinstance(record, dict) else "pending",
                    "item_title": str(item.get("title") or "").strip(),
                    "item_excerpt": snippet(str(item.get("excerpt") or ""), 180),
                }
            )
            issue_id_counter += 1

        record_status = str(record.get("status") or "pending").strip().lower() if isinstance(record, dict) else "pending"
        status_counts[record_status] += 1

    issue_rows.sort(key=lambda row: (chapter_sort_key(row["chapter"]), row["view"], row["issue_code"], row["created_at"]))
    for index, row in enumerate(issue_rows, start=1):
        row["sample_id"] = f"IR{index:04d}"

    total_reviewed = candidate_record_count
    total_issues = len(issue_rows)
    total_notes = sum(chapter_note_counts.values())
    total_items = sum(len(view_rows) for chapter in review_dataset.get("data", {}).values() if isinstance(chapter, dict) for view_rows in chapter.values() if isinstance(view_rows, list))
    reviewed_chapters = {chapter for chapter, count in chapter_reviewed.items() if count > 0}

    target_chapter_rows = []
    for chapter in TARGET_CHAPTERS:
        chapter_data = review_dataset.get("data", {}).get(chapter, {}) if isinstance(review_dataset.get("data"), dict) else {}
        if not isinstance(chapter_data, dict):
            chapter_data = {}
        target_row = {
            "chapter": chapter,
            "label": chapter,
            "chunks": len(chapter_data.get("chunks", [])) if isinstance(chapter_data.get("chunks"), list) else 0,
            "formulas": len(chapter_data.get("formulas", [])) if isinstance(chapter_data.get("formulas"), list) else 0,
            "tables": len(chapter_data.get("tables", [])) if isinstance(chapter_data.get("tables"), list) else 0,
            "reviewed_items": chapter_reviewed.get(chapter, 0),
            "issue_count": chapter_issue_counts.get(chapter, 0),
            "note_count": chapter_note_counts.get(chapter, 0),
            "status_counts": {status: 0 for status in ["pending", "pass", "fail"]},
        }
        target_chapter_rows.append(target_row)
        for record_key, record in records.items():
            normalized_key = normalize_record_key(record_key)
            if source_key_prefix and not normalized_key.startswith(source_key_prefix):
                continue
            base_key = normalized_key[len(source_key_prefix) :] if source_key_prefix and normalized_key.startswith(source_key_prefix) else normalized_key
            item = item_index.get(normalized_key) or item_index.get(base_key) or {}
            if str(item.get("chapter") or "").lower() != chapter:
                continue
            status = str(record.get("status") or "pending").strip().lower() if isinstance(record, dict) else "pending"
            if status in target_row["status_counts"]:
                target_row["status_counts"][status] += 1

    active_categories = [row for row in taxonomy_index.values() if str(row.get("status") or "").lower() == "active"]
    candidate_categories = [row for row in taxonomy_index.values() if str(row.get("status") or "").lower() == "candidate"]
    manual_only_categories = [row for row in taxonomy_index.values() if str(row.get("status") or "").lower() == "manual_only"]

    return {
        "source_version": source_version,
        "source_prefix": source_key_prefix,
        "total_items": total_items,
        "total_reviewed_records": total_reviewed,
        "foreign_record_count": foreign_record_count,
        "total_issue_records": total_issues,
        "total_note_records": total_notes,
        "chapter_issue_counts": dict(sorted(chapter_issue_counts.items(), key=lambda item: chapter_sort_key(item[0]))),
        "chapter_note_counts": dict(sorted(chapter_note_counts.items(), key=lambda item: chapter_sort_key(item[0]))),
        "chapter_reviewed_counts": dict(sorted(chapter_reviewed.items(), key=lambda item: chapter_sort_key(item[0]))),
        "issue_code_counts": dict(sorted(issue_code_counts.items(), key=lambda item: (-item[1], item[0]))),
        "severity_counts": dict(sorted(severity_counts.items(), key=lambda item: (-item[1], item[0]))),
        "record_status_counts": dict(sorted(status_counts.items(), key=lambda item: (-item[1], item[0]))),
        "taxonomy_status_counts": dict(sorted(taxonomy_status_counts.items(), key=lambda item: (-item[1], item[0]))),
        "reviewed_chapters": sorted(reviewed_chapters, key=chapter_sort_key),
        "target_chapters": target_chapter_rows,
        "active_categories": [
            {
                "issue_code": row.get("issue_code"),
                "label": row.get("label"),
                "scope": row.get("scope"),
                "severity": row.get("severity"),
                "patterns": len((row.get("detector") or {}).get("patterns", [])),
            }
            for row in active_categories
        ],
        "candidate_categories": [
            {
                "issue_code": row.get("issue_code"),
                "label": row.get("label"),
                "scope": row.get("scope"),
                "severity": row.get("severity"),
                "patterns": len((row.get("detector") or {}).get("patterns", [])),
            }
            for row in candidate_categories
        ],
        "manual_only_categories": [
            {
                "issue_code": row.get("issue_code"),
                "label": row.get("label"),
                "scope": row.get("scope"),
                "severity": row.get("severity"),
                "patterns": len((row.get("detector") or {}).get("patterns", [])),
            }
            for row in manual_only_categories
        ],
        "issue_rows": issue_rows,
    }


def build_markdown(summary: dict[str, Any], taxonomy: dict[str, Any]) -> str:
    lines = [
        "# 手工审核反馈汇总",
        "",
        "本报告读取 `review_app/data/local/review_records.json` 与 `review_app/data/local/issue_taxonomy.json`，用于把人工审核备注反哺到后续 detector 设计。",
        "",
        "## 总览",
        "",
        markdown_table(
            ["指标", "数值"],
            [
                ["structured 源版本", summary["source_version"] or "-"],
                ["总条目数", summary["total_items"]],
                ["本次已读记录数", summary["total_reviewed_records"]],
                ["跨源旧记录数", summary["foreign_record_count"]],
                ["结构化问题记录数", summary["total_issue_records"]],
                ["备注记录数", summary["total_note_records"]],
            ],
        ),
        "",
        "## Taxonomy 状态",
        "",
        markdown_table(
            ["状态", "数量"],
            [
                ["active", len(summary["active_categories"])],
                ["candidate", len(summary["candidate_categories"])],
                ["manual_only", len(summary["manual_only_categories"])],
            ],
        ),
        "",
        "## 目标章节覆盖",
        "",
        markdown_table(
            ["章节", "chunks", "formulas", "tables", "已审核条目", "issue 数", "备注数", "pending", "pass", "fail"],
            [
                [
                    row["chapter"],
                    row["chunks"],
                    row["formulas"],
                    row["tables"],
                    row["reviewed_items"],
                    row["issue_count"],
                    row["note_count"],
                    row["status_counts"].get("pending", 0),
                    row["status_counts"].get("pass", 0),
                    row["status_counts"].get("fail", 0),
                ]
                for row in summary["target_chapters"]
            ],
        ),
        "",
        "## issue 分类分布",
        "",
        markdown_table(
            ["issue_code", "数量"],
            [[code, count] for code, count in list(summary["issue_code_counts"].items())[:20]],
        ),
        "",
        "## 严重级别分布",
        "",
        markdown_table(
            ["severity", "数量"],
            [[severity, count] for severity, count in summary["severity_counts"].items()],
        ),
        "",
        "## detector 入口建议",
        "",
        "- 只让 `status=active` 且 `detector.patterns` 非空的分类进入正式 detector。",
        "- `candidate` 与 `manual_only` 先只统计、不自动判错。",
        "- 人工审核新增的 `issue_rows` 先沉淀为样例与统计，再决定是否升格为 active。",
        "",
        "## 典型问题样例",
        "",
    ]

    for row in summary["issue_rows"][:50]:
        lines.extend(
            [
                f"- {row['sample_id']} | {row['chapter']} | {row['view']} | {row['issue_code']} | {row['severity']} | {row['bad_span'] or '-'} | 目标: {row['target_id'] or '-'}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_output_dirs()
    review_dataset = safe_json_load(REVIEW_APP_DIR / "data" / "generated" / "review_dataset.json")
    if not review_dataset:
        raise SystemExit(f"Missing review dataset: {relpath(REVIEW_DATASET_PATH)}")
    item_index, source_version = build_item_index(review_dataset)
    records = load_review_records()
    taxonomy = load_taxonomy(safe_json_load(ISSUE_TAXONOMY_PATH))
    taxonomy_index = build_taxonomy_index(taxonomy)
    summary = summarize_records(review_dataset, item_index, records, taxonomy_index, source_version)

    write_json(REPORTS_DIR / f"{REPORT_BASE}.json", summary)
    write_text(REPORTS_DIR / f"{REPORT_BASE}.md", build_markdown(summary, taxonomy))
    write_jsonl(SAMPLE_OUTPUT, summary["issue_rows"])
    print(f"Wrote {relpath(REPORTS_DIR / f'{REPORT_BASE}.json')}")
    print(f"Wrote {relpath(REPORTS_DIR / f'{REPORT_BASE}.md')}")
    print(f"Wrote {relpath(SAMPLE_OUTPUT)}")


if __name__ == "__main__":
    main()
