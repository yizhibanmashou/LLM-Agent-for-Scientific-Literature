from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import (
    FALLBACK_GLMOCR_DIR,
    FALLBACK_PADDLE_DIR,
    PROJECT_ROOT,
    PROBE_ROOT,
    REPORTS_DIR,
    REQUESTED_GLMOCR_DIR,
    REQUESTED_PADDLE_DIR,
    SAMPLES_DIR,
    clean_ref_id,
    discover_ocr_text_sources,
    ensure_output_dirs,
    extract_json_text,
    extract_table_refs,
    is_ghost_block,
    load_json,
    markdown_table,
    natural_key,
    read_text,
    relpath,
    snippet,
    write_json,
    write_jsonl,
    write_text,
)


CURRENT_STRUCTURED_DIR = PROJECT_ROOT / "data" / "structured"
OLD_STRUCTURED_DIR = PROBE_ROOT / "old_structured"
SNAPSHOT_DIR = PROBE_ROOT / "cache" / "current_delivery_snapshot"
CANDIDATE_ROOT = PROBE_ROOT / "candidates" / "current_plus_p0p1"
CANDIDATE_STRUCTURED_DIR = CANDIDATE_ROOT / "structured"

CHANGE_MANIFEST_PATH = CANDIDATE_ROOT / "change_manifest.json"
CHANGES_JSONL_PATH = CANDIDATE_ROOT / "changes.jsonl"
BLOCK_MAPPING_JSONL_PATH = CANDIDATE_ROOT / "block_index_mapping.jsonl"
MANUAL_QUEUE_PATH = CANDIDATE_ROOT / "manual_review_queue.jsonl"
SNAPSHOT_MANIFEST_PATH = SNAPSHOT_DIR / "manifest.json"
SNAPSHOT_REPORT_PATH = REPORTS_DIR / "08_current_delivery_snapshot.md"
CANDIDATE_REPORT_PATH = REPORTS_DIR / "08_candidate_optimization_manifest.md"

REVIEW_QUEUE_ISSUES = {
    "unbalanced_inline_math",
    "suspicious_truncation",
    "derivation_placeholder_only_text",
    "placeholder_in_discussion",
    "broken_placeholder",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file_with_manifest(source: Path, dest: Path) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return {
        "source": relpath(source),
        "dest": relpath(dest),
        "sha256": sha256_file(dest),
        "size_bytes": dest.stat().st_size,
    }


def snapshot_current_delivery() -> dict[str, Any]:
    copied: list[dict[str, Any]] = []

    structured_snapshot = SNAPSHOT_DIR / "structured"
    for source in sorted(CURRENT_STRUCTURED_DIR.glob("*.json"), key=lambda p: natural_key(p.name)):
        copied.append(copy_file_with_manifest(source, structured_snapshot / source.name))

    code_snapshot = SNAPSHOT_DIR / "knowledge_engineering"
    code_sources = sorted((PROJECT_ROOT / "knowledge_engineering").glob("*.py"), key=lambda p: natural_key(p.name))
    readme = PROJECT_ROOT / "knowledge_engineering" / "README.md"
    if readme.exists():
        code_sources.append(readme)
    for source in code_sources:
        copied.append(copy_file_with_manifest(source, code_snapshot / source.name))

    manifest = {
        "created_at": utc_now(),
        "purpose": "Freeze current delivery structured and generation logic before tmp-only candidate optimization.",
        "source_structured_dir": relpath(CURRENT_STRUCTURED_DIR),
        "snapshot_dir": relpath(SNAPSHOT_DIR),
        "copied_file_count": len(copied),
        "copied_files": copied,
        "note": "This snapshot is local evidence only; it does not modify data/structured or knowledge_engineering.",
    }
    write_json(SNAPSHOT_MANIFEST_PATH, manifest)
    return manifest


def copy_current_to_candidate() -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for source in sorted(CURRENT_STRUCTURED_DIR.glob("*.json"), key=lambda p: natural_key(p.name)):
        copied.append(copy_file_with_manifest(source, CANDIDATE_STRUCTURED_DIR / source.name))
    return copied


def removal_reason(content: str) -> str | None:
    stripped = (content or "").strip()
    if stripped == "[h]":
        return "h_only_block"
    if is_ghost_block(stripped):
        return "ghost_block"
    return None


def remove_deterministic_noise_blocks() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    changes: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    for path in sorted(CANDIDATE_STRUCTURED_DIR.glob("*.json"), key=lambda p: natural_key(p.name)):
        if path.name in {"formula_library.json", "table_library.json"}:
            continue
        try:
            data = load_json(path)
        except Exception:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            continue

        old_blocks = data["blocks"]
        new_blocks: list[Any] = []
        old_to_new: dict[int, int | None] = {}
        chapter = ""
        metadata = data.get("metadata")
        if isinstance(metadata, dict):
            chapter = str(metadata.get("chapter", "")).lower()
        if not chapter:
            chapter = path.stem.split("_", 1)[0].lower()

        for old_index, block in enumerate(old_blocks):
            content = ""
            block_type = "unknown"
            if isinstance(block, dict):
                raw_content = block.get("content")
                content = raw_content if isinstance(raw_content, str) else "" if raw_content is None else json.dumps(raw_content, ensure_ascii=False)
                block_type = str(block.get("type", "unknown"))
            reason = removal_reason(content)
            if reason:
                old_to_new[old_index] = None
                changes.append(
                    {
                        "action": "remove_block",
                        "reason": reason,
                        "chapter": chapter,
                        "file": relpath(path),
                        "old_block_index": old_index,
                        "block_type": block_type,
                        "content_snippet": snippet(content, 260),
                    }
                )
                continue
            new_index = len(new_blocks)
            old_to_new[old_index] = new_index
            new_blocks.append(block)

        if len(new_blocks) != len(old_blocks):
            data["blocks"] = new_blocks
            write_json(path, data)

        for old_index, new_index in old_to_new.items():
            mappings.append(
                {
                    "file": relpath(path),
                    "chapter": chapter,
                    "old_block_index": old_index,
                    "candidate_block_index": new_index,
                    "status": "removed" if new_index is None else "retained",
                }
            )
    return changes, mappings


def table_id_map(table_library: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tables = table_library.get("tables") if isinstance(table_library, dict) else []
    if not isinstance(tables, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for table in tables:
        if not isinstance(table, dict):
            continue
        table_id = clean_ref_id(str(table.get("id", "")))
        if table_id:
            out[table_id] = table
    return out


def select_ocr_root(requested: Path, fallback: Path) -> Path:
    return fallback if fallback.exists() else requested


def load_ocr_text_by_chapter() -> dict[str, dict[str, str]]:
    sources: dict[str, dict[str, str]] = {"paddle": {}, "glmocr": {}}
    for label, root in {
        "paddle": select_ocr_root(REQUESTED_PADDLE_DIR, FALLBACK_PADDLE_DIR),
        "glmocr": select_ocr_root(REQUESTED_GLMOCR_DIR, FALLBACK_GLMOCR_DIR),
    }.items():
        for chapter, record in discover_ocr_text_sources(root).items():
            path = record.get("path")
            if not isinstance(path, Path):
                continue
            raw = read_text(path)
            if path.suffix.lower() == ".json":
                try:
                    text = extract_json_text(load_json(path))
                except Exception:
                    text = raw
            else:
                text = raw
            sources[label][chapter] = text
    return sources


def ref_to_chapter(ref: str) -> str | None:
    match = re.match(r"^(\d+)\.", ref)
    if not match:
        return None
    return f"chapter{int(match.group(1))}"


def ocr_confirms_table_ref(ref: str, issue_chapter: str, ocr_texts: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    chapters = {issue_chapter}
    inferred = ref_to_chapter(ref)
    if inferred:
        chapters.add(inferred)
    pattern = re.compile(rf"\bTable\s+{re.escape(ref)}\b|\[\[(?:SEE_)?TABLE\s*:\s*{re.escape(ref)}\s*\]\]", re.IGNORECASE)
    evidence: list[dict[str, Any]] = []
    for source_name, by_chapter in ocr_texts.items():
        for chapter in sorted(chapters):
            text = by_chapter.get(chapter, "")
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 160)
                end = min(len(text), match.end() + 260)
                evidence.append(
                    {
                        "source": source_name,
                        "chapter": chapter,
                        "matched_text": match.group(0),
                        "context_snippet": snippet(text[start:end], 360),
                    }
                )
    return evidence


def scan_missing_table_refs(structured_dir: Path, table_ids: set[str]) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    for path in sorted(structured_dir.glob("*.json"), key=lambda p: natural_key(p.name)):
        if path.name in {"formula_library.json", "table_library.json"}:
            continue
        try:
            data = load_json(path)
        except Exception:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            continue
        metadata = data.get("metadata")
        chapter = str(metadata.get("chapter", "")).lower() if isinstance(metadata, dict) else ""
        if not chapter:
            chapter = path.stem.split("_", 1)[0].lower()
        for idx, block in enumerate(data["blocks"]):
            if not isinstance(block, dict):
                continue
            content = block.get("content")
            if not isinstance(content, str):
                continue
            for ref in extract_table_refs(content):
                if ref not in table_ids:
                    missing.append(
                        {
                            "chapter": chapter,
                            "file": relpath(path),
                            "block_index": idx,
                            "missing_ref": ref,
                            "content_snippet": snippet(content, 300),
                        }
                    )
    return missing


def update_table_metadata(table_library: dict[str, Any]) -> None:
    tables = table_library.get("tables")
    if not isinstance(tables, list):
        return
    counter = Counter(str(table.get("table_type", "unknown")) for table in tables if isinstance(table, dict))
    table_library["metadata"] = {
        "total_tables": len(tables),
        "numbered_tables": counter.get("numbered", 0),
        "inline_tables": counter.get("inline", 0),
        "candidate_added_from_old_structured": sum(
            1
            for table in tables
            if isinstance(table, dict) and isinstance(table.get("_structured_quality_probe_provenance"), dict)
        ),
    }


def add_recoverable_old_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_table_path = CANDIDATE_STRUCTURED_DIR / "table_library.json"
    old_table_path = OLD_STRUCTURED_DIR / "table_library.json"
    table_changes: list[dict[str, Any]] = []
    manual_queue: list[dict[str, Any]] = []
    if not candidate_table_path.exists() or not old_table_path.exists():
        manual_queue.append(
            {
                "queue_type": "table_reference_missing",
                "reason": "candidate_or_old_table_library_missing",
                "candidate_table_library": relpath(candidate_table_path),
                "old_table_library": relpath(old_table_path),
            }
        )
        return table_changes, manual_queue

    candidate_library = load_json(candidate_table_path)
    old_library = load_json(old_table_path)
    current_tables = table_id_map(candidate_library)
    old_tables = table_id_map(old_library)
    missing_refs = scan_missing_table_refs(CANDIDATE_STRUCTURED_DIR, set(current_tables))
    ocr_texts = load_ocr_text_by_chapter()

    by_ref: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in missing_refs:
        by_ref[item["missing_ref"]].append(item)

    table_list = candidate_library.get("tables")
    if not isinstance(table_list, list):
        return table_changes, manual_queue

    for ref, occurrences in sorted(by_ref.items(), key=lambda item: natural_key(item[0])):
        old_table = old_tables.get(ref)
        evidence: list[dict[str, Any]] = []
        for occurrence in occurrences:
            evidence.extend(ocr_confirms_table_ref(ref, occurrence["chapter"], ocr_texts))
        if old_table and evidence:
            recovered = copy.deepcopy(old_table)
            recovered["_structured_quality_probe_provenance"] = {
                "action": "candidate_recover_table_from_old_structured",
                "source_table_library": relpath(old_table_path),
                "reason": "current blocks reference this table, current table_library lacks it, old table_library has it, OCR text mentions it.",
                "occurrence_count": len(occurrences),
                "ocr_evidence": evidence[:6],
            }
            table_list.append(recovered)
            table_changes.append(
                {
                    "action": "add_table_entry_from_old_structured",
                    "table_id": ref,
                    "occurrence_count": len(occurrences),
                    "ocr_evidence_count": len(evidence),
                    "occurrences": occurrences,
                    "old_table_title": str(old_table.get("title", ""))[:300],
                }
            )
        else:
            manual_queue.append(
                {
                    "queue_type": "table_reference_missing",
                    "reason": "not_auto_recovered",
                    "missing_ref": ref,
                    "old_table_found": bool(old_table),
                    "ocr_evidence_count": len(evidence),
                    "occurrences": occurrences,
                }
            )

    if table_changes:
        update_table_metadata(candidate_library)
        write_json(candidate_table_path, candidate_library)
    return table_changes, manual_queue


def read_existing_issue_samples() -> list[dict[str, Any]]:
    path = REPORTS_DIR / "01_structured_issue_samples.jsonl"
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_manual_queue_from_existing_issues() -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    seen: set[tuple[str, int | None, str]] = set()
    for issue in read_existing_issue_samples():
        issue_type = issue.get("issue_type")
        if issue_type not in REVIEW_QUEUE_ISSUES:
            continue
        key = (str(issue.get("file", "")), issue.get("block_index"), str(issue_type))
        if key in seen:
            continue
        seen.add(key)
        queue.append(
            {
                "queue_type": "manual_review_issue",
                "reason": "not_auto_changed_by_candidate_builder",
                "issue_type": issue_type,
                "severity": issue.get("severity"),
                "chapter": issue.get("chapter"),
                "file": issue.get("file"),
                "block_index": issue.get("block_index"),
                "block_type": issue.get("block_type"),
                "content_snippet": issue.get("sample_snippet"),
                "details": issue.get("details", {}),
            }
        )
    return queue


def write_snapshot_report(snapshot_manifest: dict[str, Any]) -> None:
    md = [
        "# 08 Current Delivery Snapshot",
        "",
        "本快照用于冻结当前已经达到交付标准的 `data/structured` 和核心结构化代码逻辑。它只写入 tmp，不修改正式数据。",
        "",
        markdown_table(
            ["item", "value"],
            [
                ["snapshot_dir", snapshot_manifest["snapshot_dir"]],
                ["copied_file_count", snapshot_manifest["copied_file_count"]],
                ["manifest", relpath(SNAPSHOT_MANIFEST_PATH)],
                ["source_structured_dir", snapshot_manifest["source_structured_dir"]],
            ],
        ),
        "",
        "## 说明",
        "",
        "- GitHub 提交作为外层回滚保险；本地 tmp 快照用于审计、三版对比和报告引用。",
        "- 快照包含 `data/structured/*.json` 和 `knowledge_engineering` 的核心 `.py` / README 文件。",
    ]
    write_text(SNAPSHOT_REPORT_PATH, "\n".join(md) + "\n")


def write_candidate_report(manifest: dict[str, Any]) -> None:
    block_rows = [[reason, count] for reason, count in manifest["summary"]["removed_blocks_by_reason"].items()]
    table_rows = [
        [
            change["table_id"],
            change["occurrence_count"],
            change["ocr_evidence_count"],
            change["old_table_title"],
        ]
        for change in manifest["table_recovery"]["added_table_entries"]
    ]
    manual_rows = []
    queue_counts = Counter(item.get("queue_type", "unknown") for item in manifest["manual_queue_preview"])
    for key, value in queue_counts.items():
        manual_rows.append([key, value])
    md = [
        "# 08 Candidate Optimization Manifest",
        "",
        "本报告记录候选优化版的确定性改动。候选版只写入 tmp，不覆盖 `data/structured`。",
        "",
        "## 输出位置",
        "",
        markdown_table(
            ["item", "path"],
            [
                ["candidate_structured_dir", manifest["candidate_structured_dir"]],
                ["change_manifest", relpath(CHANGE_MANIFEST_PATH)],
                ["changes_jsonl", relpath(CHANGES_JSONL_PATH)],
                ["block_index_mapping_jsonl", relpath(BLOCK_MAPPING_JSONL_PATH)],
                ["manual_review_queue_jsonl", relpath(MANUAL_QUEUE_PATH)],
            ],
        ),
        "",
        "## 自动改动概览",
        "",
        markdown_table(
            ["metric", "value"],
            [
                ["copied_structured_files", manifest["summary"]["copied_structured_files"]],
                ["removed_blocks", manifest["summary"]["removed_blocks"]],
                ["added_table_entries", manifest["summary"]["added_table_entries"]],
                ["manual_queue_items", manifest["summary"]["manual_queue_items"]],
            ],
        ),
        "",
        "## 删除的确定性噪声 block",
        "",
        markdown_table(["reason", "count"], block_rows or [["无", 0]]),
        "",
        "## 旧库证据补入的表格",
        "",
        markdown_table(["table_id", "occurrences", "ocr_evidence", "old_table_title"], table_rows or [["无", 0, 0, ""]]),
        "",
        "## manual queue 类型预览",
        "",
        markdown_table(["queue_type", "preview_count"], manual_rows or [["无", 0]]),
        "",
        "## 边界",
        "",
        "- 没有修改 `data/structured`。",
        "- 没有把 PaddleOCR 或 GLM-OCR 当作 ground truth；它们只用于判断旧版表格是否有文本证据。",
        "- 不确定的数学、截断、derivation 和无法证据补表的问题全部进入 manual queue。",
    ]
    write_text(CANDIDATE_REPORT_PATH, "\n".join(md) + "\n")


def main() -> None:
    ensure_output_dirs()
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_manifest = snapshot_current_delivery()
    copied_candidate_files = copy_current_to_candidate()
    block_changes, block_mappings = remove_deterministic_noise_blocks()
    table_changes, table_manual_queue = add_recoverable_old_tables()
    manual_queue = table_manual_queue + build_manual_queue_from_existing_issues()

    all_changes = block_changes + table_changes
    removed_by_reason = Counter(change["reason"] for change in block_changes if change.get("action") == "remove_block")
    manifest = {
        "created_at": utc_now(),
        "source_structured_dir": relpath(CURRENT_STRUCTURED_DIR),
        "old_structured_dir": relpath(OLD_STRUCTURED_DIR),
        "candidate_structured_dir": relpath(CANDIDATE_STRUCTURED_DIR),
        "snapshot_manifest": relpath(SNAPSHOT_MANIFEST_PATH),
        "summary": {
            "copied_structured_files": len(copied_candidate_files),
            "removed_blocks": len(block_changes),
            "removed_blocks_by_reason": dict(sorted(removed_by_reason.items())),
            "added_table_entries": len(table_changes),
            "manual_queue_items": len(manual_queue),
        },
        "table_recovery": {
            "policy": "Only add a missing table when old_structured has the same table id and Paddle/GLM OCR text mentions the table.",
            "added_table_entries": table_changes,
        },
        "manual_queue_preview": manual_queue[:50],
        "outputs": {
            "changes_jsonl": relpath(CHANGES_JSONL_PATH),
            "block_index_mapping_jsonl": relpath(BLOCK_MAPPING_JSONL_PATH),
            "manual_review_queue_jsonl": relpath(MANUAL_QUEUE_PATH),
            "candidate_report": relpath(CANDIDATE_REPORT_PATH),
        },
        "note": "Candidate optimization is tmp-only and is not applied to data/structured.",
    }
    write_json(CHANGE_MANIFEST_PATH, manifest)
    write_jsonl(CHANGES_JSONL_PATH, all_changes)
    write_jsonl(BLOCK_MAPPING_JSONL_PATH, block_mappings)
    write_jsonl(MANUAL_QUEUE_PATH, manual_queue)
    write_snapshot_report(snapshot_manifest)
    write_candidate_report(manifest)


if __name__ == "__main__":
    main()
