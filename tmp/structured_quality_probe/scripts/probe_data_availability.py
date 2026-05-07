from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from common import (
    FALLBACK_GLMOCR_DIR,
    FALLBACK_PADDLE_DIR,
    FORMULA_LIBRARY_PATH,
    PROJECT_ROOT,
    REQUESTED_GLMOCR_DIR,
    REQUESTED_PADDLE_DIR,
    STRUCTURED_DIR,
    TABLE_LIBRARY_PATH,
    discover_ocr_text_sources,
    ensure_output_dirs,
    load_json,
    markdown_table,
    natural_key,
    read_text,
    relpath,
    structured_json_files,
    write_json,
    write_text,
)


def path_info(path: Path) -> dict[str, object]:
    exists = path.exists()
    info = {
        "path": relpath(path),
        "exists": exists,
        "is_dir": path.is_dir() if exists else False,
        "is_file": path.is_file() if exists else False,
        "size_bytes": path.stat().st_size if exists and path.is_file() else None,
    }
    return info


def load_entry_count(path: Path, key: str) -> int | None:
    if not path.exists():
        return None
    try:
        data = load_json(path)
    except Exception:
        return None
    if isinstance(data, dict):
        entries = data.get(key)
        if isinstance(entries, list):
            return len(entries)
    if isinstance(data, list):
        return len(data)
    return None


def collect_structured_stats() -> dict[str, object]:
    files = structured_json_files()
    block_types = Counter()
    total_blocks = 0
    parse_errors: list[str] = []
    chapter_keys: set[str] = set()

    for path in files:
        chapter_keys.add(path.stem.split("_", 1)[0].lower())
        try:
            data = load_json(path)
        except Exception as exc:
            parse_errors.append(f"{relpath(path)}: {exc}")
            continue
        blocks = data.get("blocks") if isinstance(data, dict) else None
        if isinstance(blocks, list):
            total_blocks += len(blocks)
            for block in blocks:
                if isinstance(block, dict):
                    block_types[str(block.get("type", "unknown"))] += 1
                else:
                    block_types["unknown"] += 1
        else:
            parse_errors.append(f"{relpath(path)}: missing blocks list")

    return {
        "file_count": len(files),
        "total_blocks": total_blocks,
        "block_type_counts": dict(sorted(block_types.items(), key=lambda item: (-item[1], item[0]))),
        "chapter_keys": sorted(chapter_keys, key=natural_key),
        "parse_errors": parse_errors,
    }


def summarize_ocr_root(root: Path, structured_chapters: list[str]) -> dict[str, object]:
    sources = discover_ocr_text_sources(root)
    usable_keys = sorted([key for key in sources.keys() if key != "toc"], key=natural_key)
    missing = sorted(set(structured_chapters) - set(usable_keys), key=natural_key)
    extra = sorted(set(usable_keys) - set(structured_chapters), key=natural_key)
    toc_present = "toc" in sources
    return {
        "path": relpath(root),
        "exists": root.exists(),
        "usable_chapter_count": len(usable_keys),
        "usable_chapters": usable_keys,
        "toc_present": toc_present,
        "coverage_against_structured": {
            "matched_count": len(set(usable_keys) & set(structured_chapters)),
            "missing_count": len(missing),
            "extra_count": len(extra),
            "missing_chapters": missing,
            "extra_chapters": extra,
        },
        "candidate_sources": {
            key: {
                "relative_path": value["relative_path"],
                "candidate_count": value["candidate_count"],
            }
            for key, value in sources.items()
        },
    }


def main() -> None:
    ensure_output_dirs()

    structured_stats = collect_structured_stats()
    formula_count = load_entry_count(FORMULA_LIBRARY_PATH, "formulas")
    table_count = load_entry_count(TABLE_LIBRARY_PATH, "tables")

    requested_paddle = path_info(REQUESTED_PADDLE_DIR)
    requested_glmocr = path_info(REQUESTED_GLMOCR_DIR)
    fallback_paddle = summarize_ocr_root(FALLBACK_PADDLE_DIR, structured_stats["chapter_keys"])
    fallback_glmocr = summarize_ocr_root(FALLBACK_GLMOCR_DIR, structured_stats["chapter_keys"])

    report = {
        "project_root": relpath(PROJECT_ROOT),
        "requested_paths": {
            "structured_dir": path_info(STRUCTURED_DIR),
            "formula_library": path_info(FORMULA_LIBRARY_PATH),
            "table_library": path_info(TABLE_LIBRARY_PATH),
            "paddle_output": requested_paddle,
            "glmocr_output": requested_glmocr,
        },
        "structured_summary": {
            **structured_stats,
            "formula_library_entry_count": formula_count,
            "table_library_entry_count": table_count,
        },
        "ocr_summary": {
            "requested_paddle_output": {
                **requested_paddle,
                "usable_chapter_count": 0,
                "coverage_against_structured": None,
            },
            "requested_glmocr_output": {
                **requested_glmocr,
                "usable_chapter_count": 0,
                "coverage_against_structured": None,
            },
            "fallback_paddle_output": fallback_paddle,
            "fallback_glmocr_output": fallback_glmocr,
        },
        "availability_conclusion": {
            "structured_data_available": STRUCTURED_DIR.exists() and FORMULA_LIBRARY_PATH.exists() and TABLE_LIBRARY_PATH.exists(),
            "requested_ocr_dirs_available": requested_paddle["exists"] and requested_glmocr["exists"],
            "actual_ocr_roots_found_under_tmp": {
                "paddle": FALLBACK_PADDLE_DIR.exists(),
                "glmocr": FALLBACK_GLMOCR_DIR.exists(),
            },
            "glmocr_full_coverage_on_requested_path": bool(
                requested_glmocr["exists"]
                and requested_glmocr["is_dir"]
                and fallback_glmocr["coverage_against_structured"]["missing_count"] == 0
            ),
        },
    }

    json_path = Path(PROJECT_ROOT) / "tmp" / "structured_quality_probe" / "reports" / "00_data_availability.json"
    md_path = Path(PROJECT_ROOT) / "tmp" / "structured_quality_probe" / "reports" / "00_data_availability.md"
    write_json(json_path, report)

    rows = [
        ["结构化目录", report["requested_paths"]["structured_dir"]["exists"], report["requested_paths"]["structured_dir"]["path"]],
        ["formula_library", report["requested_paths"]["formula_library"]["exists"], report["requested_paths"]["formula_library"]["path"]],
        ["table_library", report["requested_paths"]["table_library"]["exists"], report["requested_paths"]["table_library"]["path"]],
        ["data/paddle_output", report["requested_paths"]["paddle_output"]["exists"], report["requested_paths"]["paddle_output"]["path"]],
        ["data/glmocr_output", report["requested_paths"]["glmocr_output"]["exists"], report["requested_paths"]["glmocr_output"]["path"]],
    ]

    structured_rows = [
        ["structured JSON 文件数", structured_stats["file_count"]],
        ["structured blocks 总数", structured_stats["total_blocks"]],
        ["formula_library 条目数", formula_count if formula_count is not None else "N/A"],
        ["table_library 条目数", table_count if table_count is not None else "N/A"],
    ]

    ocr_rows = [
        ["requested data/paddle_output", requested_paddle["exists"], 0, "missing" if not requested_paddle["exists"] else "present"],
        ["requested data/glmocr_output", requested_glmocr["exists"], 0, "missing" if not requested_glmocr["exists"] else "present"],
        ["tmp/paddle_output", fallback_paddle["exists"], fallback_paddle["usable_chapter_count"], "usable fallback"],
        ["tmp/glmocr_output", fallback_glmocr["exists"], fallback_glmocr["usable_chapter_count"], "usable fallback"],
    ]

    conclusion = (
        "## 可行性初判\n\n"
        f"- structured 数据目录：{'可用' if report['requested_paths']['structured_dir']['exists'] else '缺失'}\n"
        f"- formula/table 库：{'可用' if report['requested_paths']['formula_library']['exists'] and report['requested_paths']['table_library']['exists'] else '缺失'}\n"
        f"- 用户指定的 data/paddle_output 与 data/glmocr_output：{'均存在' if requested_paddle['exists'] and requested_glmocr['exists'] else '当前工作树下缺失'}\n"
        f"- 实际可用 OCR 根目录：tmp/paddle_output={'是' if FALLBACK_PADDLE_DIR.exists() else '否'}，tmp/glmocr_output={'是' if FALLBACK_GLMOCR_DIR.exists() else '否'}\n"
        "- 结论：structured 质量评估方案可做，且后续比较脚本可基于 tmp 下的实际 OCR 输出只读运行。\n"
    )

    md = [
        "# 00 Data Availability",
        "",
        "## 路径检查",
        "",
        markdown_table(["路径", "存在", "实际位置"], rows),
        "",
        "## 结构化统计",
        "",
        markdown_table(["指标", "值"], structured_rows),
        "",
        "## OCR 输出覆盖",
        "",
        markdown_table(["来源", "存在", "可用章节数", "备注"], ocr_rows),
        "",
        "## 覆盖细节",
        "",
        f"- structured 章节键：{', '.join(structured_stats['chapter_keys'][:12])}{' ...' if len(structured_stats['chapter_keys']) > 12 else ''}",
        f"- tmp/glmocr_output 是否全章节覆盖 structured：{'是' if fallback_glmocr['coverage_against_structured']['missing_count'] == 0 else '否'}",
        f"- tmp/glmocr_output 相对 structured 的缺失章节数：{fallback_glmocr['coverage_against_structured']['missing_count']}",
        f"- tmp/paddle_output 相对 structured 的缺失章节数：{fallback_paddle['coverage_against_structured']['missing_count']}",
        "",
        conclusion,
    ]
    write_text(md_path, "\n".join(md) + "\n")


if __name__ == "__main__":
    main()
