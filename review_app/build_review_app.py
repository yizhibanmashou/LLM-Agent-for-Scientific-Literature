from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
CONFIG_PATH = APP_DIR / "source_config.json"
OUTPUT_DIR = APP_DIR / "data" / "generated"
TMP_DIR = APP_DIR / "tmp"
REVIEW_DATASET_PATH = OUTPUT_DIR / "review_dataset.json"
FLOW_GRAPH_PATH = OUTPUT_DIR / "flow_graph.json"
FORMULA_OCR_INDEX_PATH = TMP_DIR / "formula_ocr_index.json"
REVIEW_LOCATOR_INDEX_PATH = TMP_DIR / "review_locator_index.json"
CHUNK_LINE_INDEX_PATH = TMP_DIR / "chunk_line_index.json"
BUILD_TRACE_PATH = TMP_DIR / "review_build_trace.json"
TOC_TREE_PATH = ROOT_DIR / "data" / "structured" / "1目录_toc_tree.json"
PADDLE_OUTPUT_DIR = ROOT_DIR / "tmp" / "paddle_output"

CHAPTER_ID_PATTERN = re.compile(r"^(chapter\d+|appendix\d+)$", flags=re.IGNORECASE)
CHUNK_FILE_PATTERN = re.compile(r"^(chapter\d+|appendix\d+)_(\d{3})\.json$", flags=re.IGNORECASE)
FORMULA_ID_PATTERN = re.compile(r"^(\d+)\.(\d+)([a-z]?)$", flags=re.IGNORECASE)
CHUNK_SEMANTIC_TYPES = ("discussion", "derivation", "proposition", "definition")
CHUNK_LAYOUT_LABELS = {"text", "paragraph_title", "doc_title", "figure_title"}
CHUNK_LINE_POC_CHAPTERS = {"chapter6"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {}


def structured_source_version(structured_dir: Path) -> str:
    normalized = structured_dir.resolve().as_posix().lower()
    if normalized.endswith("/tmp/structured_quality_probe/candidates/current_plus_p0p1/structured"):
        return "candidate_current_plus_p0p1"
    if normalized.endswith("/tmp/structured_quality_probe/cache/fusion_smoke_claude_check/structured"):
        return "fusion_smoke_claude_check"
    if normalized.endswith("/data/structured"):
        return "current_data"
    if normalized.endswith("/tmp/structured_quality_probe/old_structured"):
        return "early_paper2latex"
    return re.sub(r"[^a-z0-9]+", "_", structured_dir.name.lower()).strip("_") or "unknown"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_repo_path(relative_path: str) -> Path:
    return (ROOT_DIR / relative_path).resolve()


def chapter_id_from_source_file(source_file: str) -> str | None:
    normalized = str(source_file or "").replace("\\", "/").strip().lower()
    if not normalized:
        return None
    match = re.search(r"(chapter\d+|appendix\d+)_full", normalized)
    return match.group(1) if match else None


def resolve_formula_ocr_raw_path(source_file: str) -> Path | None:
    normalized = str(source_file or "").strip().replace("\\", "/")
    if not normalized:
        return None

    source_path = Path(normalized)
    if not source_path.is_absolute():
        source_path = (ROOT_DIR / source_path).resolve()

    candidates: list[Path] = []
    if source_path.name == "paddle_raw_api_response.json":
        candidates.append(source_path)
    if source_path.suffix.lower() == ".tex":
        candidates.append(source_path.parent / "intermediate" / "paddle_raw_api_response.json")
    if source_path.name.lower() == "intermediate":
        candidates.append(source_path / "paddle_raw_api_response.json")
    if source_path.name.lower().endswith("_full"):
        candidates.append(source_path / "intermediate" / "paddle_raw_api_response.json")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def trim_text(text: str, limit: int = 280) -> str:
    normalized = normalize_space(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 1)].rstrip() + "…"


def unique_preserve_order(values: list[str], max_items: int) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = value.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(value.strip())
        if len(ordered) >= max_items:
            break
    return ordered


def normalize_match_text(text: str) -> str:
    lowered = str(text or "").lower()
    lowered = re.sub(r"[^\w\u4e00-\u9fff]+", " ", lowered, flags=re.UNICODE)
    return re.sub(r"\s+", " ", lowered).strip()


def normalize_title_key(text: str) -> str:
    cleaned = normalize_match_text(text)
    cleaned = re.sub(r"\b(equation|table|section|chapter|appendix)\b", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def token_set(text: str) -> set[str]:
    return {token for token in normalize_title_key(text).split(" ") if len(token) >= 2}


def tokenize(text: str, min_len: int = 4, max_items: int = 10) -> list[str]:
    normalized = normalize_match_text(text)
    tokens = [token for token in normalized.split(" ") if len(token) >= min_len]
    return unique_preserve_order(tokens, max_items)


def build_search_keys(parts: list[str], max_items: int = 8) -> list[str]:
    candidates: list[str] = []
    for part in parts:
        value = normalize_space(part)
        if not value:
            continue
        if 4 <= len(value) <= 90:
            candidates.append(value)
        elif len(value) > 90:
            candidates.append(value[:90].rstrip())
        token_join = " ".join(tokenize(value, min_len=4, max_items=8))
        if token_join:
            candidates.append(token_join)
    return unique_preserve_order(candidates, max_items)


def title_similarity(left: str, right: str) -> float:
    left_norm = normalize_title_key(left)
    right_norm = normalize_title_key(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    if left_norm in right_norm or right_norm in left_norm:
        return 0.92

    left_tokens = token_set(left_norm)
    right_tokens = token_set(right_norm)
    if not left_tokens or not right_tokens:
        return 0.0

    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    jaccard = intersection / union if union else 0.0
    seq = SequenceMatcher(a=left_norm, b=right_norm).ratio()
    return max(jaccard, seq * 0.9)


def chapter_sort_key(chapter_id: str) -> tuple[int, int, str]:
    chapter_text = str(chapter_id or "").strip().lower()
    chapter_match = re.fullmatch(r"chapter(\d+)", chapter_text)
    if chapter_match:
        return (0, int(chapter_match.group(1)), "")
    appendix_match = re.fullmatch(r"appendix(\d+)", chapter_text)
    if appendix_match:
        return (1, int(appendix_match.group(1)), "")
    return (2, 9999, chapter_text)


def chapter_label(chapter_id: str) -> str:
    text = chapter_id.lower()
    chapter_match = re.fullmatch(r"chapter(\d+)", text)
    if chapter_match:
        return f"Chapter {chapter_match.group(1)}"
    appendix_match = re.fullmatch(r"appendix(\d+)", text)
    if appendix_match:
        return f"Appendix {appendix_match.group(1)}"
    return chapter_id


def formula_sort_key(formula_id: str) -> tuple[int, int, int, str]:
    text = str(formula_id or "").strip().lower()
    match = FORMULA_ID_PATTERN.fullmatch(text)
    if not match:
        return (9999, 9999, 9999, text)
    suffix = match.group(3)
    suffix_idx = 0 if not suffix else ord(suffix) - ord("a") + 1
    return (int(match.group(1)), int(match.group(2)), suffix_idx, "")


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def parse_formula_number_id(text: str) -> str | None:
    match = re.search(r"(\d+\.\d+[a-z]?)", str(text or "").strip().lower())
    return match.group(1) if match else None


def parse_table_number_id(text: str) -> str | None:
    match = re.search(r"\btable\s+(\d+\.\d+)\b", str(text or "").strip(), flags=re.IGNORECASE)
    return match.group(1).lower() if match else None


def normalize_bbox(bbox: list[float], width: float, height: float) -> dict[str, float] | None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    if not width or not height:
        return None
    x1, y1, x2, y2 = (float(item) for item in bbox)
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    box_w = max(0.0, right - left)
    box_h = max(0.0, bottom - top)
    if box_w <= 0.0 or box_h <= 0.0:
        return None
    return {
        "x": round(clamp01(left / width), 6),
        "y": round(clamp01(top / height), 6),
        "w": round(clamp01(box_w / width), 6),
        "h": round(clamp01(box_h / height), 6),
    }


def bbox_center(bbox: dict[str, float]) -> tuple[float, float]:
    return (bbox["x"] + bbox["w"] / 2.0, bbox["y"] + bbox["h"] / 2.0)


def bbox_union(first: dict[str, float], second: dict[str, float]) -> dict[str, float]:
    left = min(first["x"], second["x"])
    top = min(first["y"], second["y"])
    right = max(first["x"] + first["w"], second["x"] + second["w"])
    bottom = max(first["y"] + first["h"], second["y"] + second["h"])
    return {
        "x": round(clamp01(left), 6),
        "y": round(clamp01(top), 6),
        "w": round(clamp01(max(0.0, right - left)), 6),
        "h": round(clamp01(max(0.0, bottom - top)), 6),
    }


def bbox_area(bbox: dict[str, float]) -> float:
    return max(0.0, float(bbox.get("w", 0.0)) * float(bbox.get("h", 0.0)))


def bbox_distance(first: dict[str, float], second: dict[str, float]) -> float:
    left_center = bbox_center(first)
    right_center = bbox_center(second)
    return abs(left_center[1] - right_center[1]) + abs(left_center[0] - right_center[0]) * 0.35


def normalize_candidate_box(raw_box: Any) -> dict[str, Any] | None:
    if not isinstance(raw_box, dict):
        return None
    x = raw_box.get("x")
    y = raw_box.get("y")
    w = raw_box.get("w")
    h = raw_box.get("h")
    try:
        x_f = float(x)
        y_f = float(y)
        w_f = float(w)
        h_f = float(h)
    except (TypeError, ValueError):
        return None
    if w_f <= 0.0 or h_f <= 0.0:
        return None
    return {
        "kind": str(raw_box.get("kind") or "ocr").strip() or "ocr",
        "x": round(clamp01(x_f), 6),
        "y": round(clamp01(y_f), 6),
        "w": round(clamp01(w_f), 6),
        "h": round(clamp01(h_f), 6),
    }


def make_candidate(
    page: int,
    score: float,
    source: str,
    boxes: list[dict[str, Any]],
    matched: list[str] | None = None,
    max_boxes: int = 12,
) -> dict[str, Any]:
    normalized_boxes = [box for box in (normalize_candidate_box(box) for box in boxes) if box]
    return {
        "page": int(page),
        "score": round(max(0.01, min(0.99, float(score))), 4),
        "source": str(source or "layout").strip() or "layout",
        "boxes": normalized_boxes[:max_boxes],
        "matched": unique_preserve_order([str(token) for token in (matched or [])], 8),
    }


def dedupe_candidates(candidates: list[dict[str, Any]], max_items: int = 3) -> list[dict[str, Any]]:
    chosen: dict[int, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        page = candidate.get("page")
        score = candidate.get("score")
        if not isinstance(page, int):
            continue
        if not isinstance(score, (int, float)):
            continue
        existing = chosen.get(page)
        if not existing or float(score) > float(existing.get("score", 0.0)):
            chosen[page] = candidate
    return sorted(chosen.values(), key=lambda row: (-float(row.get("score", 0.0)), int(row.get("page", 0))))[:max_items]


def chapter_raw_layout_path(chapter_id: str) -> Path:
    return PADDLE_OUTPUT_DIR / f"{chapter_id}_full" / "intermediate" / "paddle_raw_api_response.json"


def load_chapter_layout_blocks(chapter_id: str) -> dict[str, Any]:
    raw_path = chapter_raw_layout_path(chapter_id)
    if not raw_path.exists():
        return {"source_file": "", "page_count": 0, "pages": {}}

    raw_payload = load_json(raw_path)
    result = raw_payload.get("result", {}) if isinstance(raw_payload.get("result"), dict) else {}
    pages = result.get("layoutParsingResults", []) if isinstance(result.get("layoutParsingResults"), list) else []

    page_blocks: dict[int, list[dict[str, Any]]] = {}
    for page_idx, page_payload in enumerate(pages, start=1):
        pruned = page_payload.get("prunedResult", {}) if isinstance(page_payload, dict) else {}
        page_width = float(pruned.get("width") or 0.0)
        page_height = float(pruned.get("height") or 0.0)
        parsing_rows = pruned.get("parsing_res_list", []) if isinstance(pruned.get("parsing_res_list"), list) else []
        rows: list[dict[str, Any]] = []
        for row in parsing_rows:
            if not isinstance(row, dict):
                continue
            bbox = normalize_bbox(row.get("block_bbox") or [], page_width, page_height)
            if not bbox:
                continue
            content = normalize_space(str(row.get("block_content") or ""))
            content_norm = normalize_match_text(content)
            rows.append(
                {
                    "page": page_idx,
                    "label": str(row.get("block_label") or "").strip().lower(),
                    "content": content,
                    "content_norm": content_norm,
                    "bbox": bbox,
                    "page_width": page_width,
                    "page_height": page_height,
                }
            )
        if rows:
            page_blocks[page_idx] = rows

    return {
        "source_file": str(raw_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "page_count": len(pages),
        "pages": page_blocks,
    }


def find_formula_candidates_from_layout(item: dict[str, Any], chapter_layout: dict[str, Any]) -> list[dict[str, Any]]:
    formula_id = str(item.get("id") or "").strip().lower()
    if not formula_id:
        return []

    collected: list[dict[str, Any]] = []
    for page, blocks in chapter_layout.get("pages", {}).items():
        number_blocks: list[dict[str, Any]] = []
        for block in blocks:
            if block.get("label") != "formula_number":
                continue
            parsed_id = parse_formula_number_id(str(block.get("content") or ""))
            if parsed_id and parsed_id == formula_id:
                number_blocks.append(block)
        if not number_blocks:
            continue

        formula_blocks = [block for block in blocks if block.get("label") in {"display_formula", "inline_formula"}]
        for number_block in number_blocks[:3]:
            number_bbox = number_block["bbox"]
            boxes: list[dict[str, Any]] = [{"kind": "formula_number", **number_bbox}]
            score = 0.74
            nearest_formula = None
            nearest_distance = 999.0

            for formula_block in formula_blocks:
                distance = bbox_distance(number_bbox, formula_block["bbox"])
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_formula = formula_block

            if nearest_formula and nearest_distance <= 0.26:
                boxes.insert(0, {"kind": nearest_formula["label"], **nearest_formula["bbox"]})
                score = 0.96 - min(0.35, nearest_distance)

            collected.append(make_candidate(page=page, score=score, source="layout_formula", boxes=boxes, matched=[formula_id]))

    if collected:
        return dedupe_candidates(collected)

    latex_norm = normalize_match_text(str(item.get("latex") or ""))
    latex_tokens = tokenize(latex_norm, min_len=2, max_items=24)
    if len(latex_tokens) < 4:
        return []

    query_token_set = set(latex_tokens)
    for page, blocks in chapter_layout.get("pages", {}).items():
        for block in blocks:
            if block.get("label") != "display_formula":
                continue
            content_norm = normalize_match_text(str(block.get("content") or ""))
            if not content_norm:
                continue
            block_tokens = tokenize(content_norm, min_len=2, max_items=32)
            matched = [token for token in latex_tokens if token in set(block_tokens)]
            overlap = len(set(matched)) / max(1.0, float(len(query_token_set)))
            seq_ratio = SequenceMatcher(a=latex_norm[:520], b=content_norm[:520]).ratio()
            score_value = overlap * 0.52 + seq_ratio * 0.43
            if overlap < 0.34 or seq_ratio < 0.32 or score_value < 0.42:
                continue
            collected.append(
                make_candidate(
                    page=page,
                    score=0.54 + min(0.34, score_value * 0.38),
                    source="layout_formula_content",
                    boxes=[{"kind": "display_formula", **block["bbox"]}],
                    matched=[formula_id, *matched],
                )
            )

    return dedupe_candidates(collected)


def table_anchor_score(content_norm: str, table_id: str, title_tokens: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    matched: list[str] = []
    for token in title_tokens:
        if token and token in content_norm:
            score += min(12.0, len(token) * 1.3)
            matched.append(token)
    return score, unique_preserve_order(matched, 6)


def find_table_candidates_from_layout(item: dict[str, Any], chapter_layout: dict[str, Any]) -> list[dict[str, Any]]:
    raw_table_id = str(item.get("id") or "").strip().lower()
    table_id = normalize_match_text(raw_table_id)
    expected_page = item.get("source_page")
    expected_page = int(expected_page) if isinstance(expected_page, int) and expected_page > 0 else None
    title_tokens = tokenize(
        " ".join(
            [
                str(item.get("title") or ""),
                str(item.get("excerpt") or ""),
                str(item.get("subtitle") or ""),
            ]
        ),
        min_len=4,
        max_items=8,
    )

    collected: list[dict[str, Any]] = []
    for page, blocks in chapter_layout.get("pages", {}).items():
        anchor = None
        anchor_score = 0.0
        anchor_matched: list[str] = []

        for block in blocks:
            label = str(block.get("label") or "")
            if label not in {"figure_title", "table", "text", "paragraph_title"}:
                continue
            if not raw_table_id.startswith("inline_") and label == "text" and expected_page and int(page) != expected_page:
                continue
            content_norm = str(block.get("content_norm") or "")
            block_score = 0.0
            matched: list[str] = []

            parsed_table_id = parse_table_number_id(str(block.get("content") or ""))
            if raw_table_id and raw_table_id.startswith("inline_"):
                if expected_page and int(page) == expected_page:
                    if label in {"figure_title", "table"}:
                        block_score += 34.0
                    elif label == "text":
                        block_score += 10.0
            elif parsed_table_id and parsed_table_id == raw_table_id:
                block_score += 96.0
                matched.extend([raw_table_id, "table"])
            elif label == "text" and parsed_table_id:
                continue

            title_score, title_matched = table_anchor_score(content_norm, table_id, title_tokens)
            if title_matched:
                block_score += title_score
                matched.extend(title_matched)

            if expected_page:
                distance = abs(int(page) - expected_page)
                if distance == 0:
                    block_score += 28.0
                else:
                    block_score -= min(42.0, distance * 10.0)

            if label == "table":
                block_score += 10.0
            elif label == "figure_title":
                block_score += 8.0
            elif label == "text":
                block_score -= 22.0

            if block_score > anchor_score:
                anchor = block
                anchor_score = block_score
                anchor_matched = matched

        if not anchor or anchor_score < 38:
            continue

        boxes: list[dict[str, Any]] = [{"kind": str(anchor.get("label") or "text"), **anchor["bbox"]}]
        if str(anchor.get("label") or "") != "table":
            nearest_table = None
            nearest_distance = 999.0
            for block in blocks:
                if str(block.get("label") or "") != "table":
                    continue
                distance = bbox_distance(anchor["bbox"], block["bbox"])
                if distance < nearest_distance:
                    nearest_table = block
                    nearest_distance = distance
            if nearest_table and nearest_distance <= 0.42:
                boxes.append({"kind": "table", **nearest_table["bbox"]})

        candidate_score = 0.42 + min(0.55, anchor_score / 150.0)
        collected.append(make_candidate(page=page, score=candidate_score, source="layout_table", boxes=boxes, matched=anchor_matched))

    return dedupe_candidates(collected)


def build_chunk_tokens(item: dict[str, Any]) -> list[str]:
    sources: list[str] = [
        str(item.get("id") or ""),
        str(item.get("title") or ""),
        str(item.get("subtitle") or ""),
        str(item.get("excerpt") or ""),
    ]
    for key in item.get("search_keys", []) if isinstance(item.get("search_keys"), list) else []:
        sources.append(str(key))
    return tokenize(" ".join(sources), min_len=4, max_items=14)


def normalize_chunk_semantic_kind(raw_type: str) -> str | None:
    normalized = normalize_match_text(raw_type).replace(" ", "_")
    if normalized in CHUNK_SEMANTIC_TYPES:
        return normalized
    return None


def is_chunk_layout_noise(label: str, content_norm: str, bbox: dict[str, float] | None) -> bool:
    if not bbox:
        return False
    if label == "text" and float(bbox.get("y") or 0.0) >= 0.82:
        footer_terms = ("published", "doi", "oxford university press", "evolution and selection")
        if any(term in content_norm for term in footer_terms):
            return True
    return False


def split_block_sentences(text: str, max_parts: int = 24) -> list[str]:
    normalized = normalize_space(text)
    if not normalized:
        return []
    parts = [part.strip() for part in re.split(r"(?<=[\.\!\?。！？；;:])\s+", normalized) if part.strip()]
    if len(parts) <= 1:
        return [normalized]
    trimmed = [part for part in parts if len(normalize_match_text(part)) >= 8]
    return (trimmed or [normalized])[:max_parts]


def nearest_space_split(text: str, target: int, start: int, end: int) -> int:
    lower_bound = max(start + 12, min(end - 1, target - 36))
    upper_bound = min(end - 1, max(start + 12, target + 36))
    if lower_bound >= upper_bound:
        return max(start + 1, min(end - 1, target))

    best_index = -1
    best_distance = 9999
    for index in range(lower_bound, upper_bound + 1):
        if text[index].isspace():
            distance = abs(index - target)
            if distance < best_distance:
                best_index = index
                best_distance = distance
    if best_index >= 0:
        return best_index
    return max(start + 1, min(end - 1, target))


def split_text_into_visual_lines(text: str, line_count: int) -> list[str]:
    normalized = normalize_space(text)
    if not normalized:
        return []
    line_count = max(1, min(int(line_count), 48))
    if line_count == 1 or len(normalized) <= 32:
        return [normalized]

    parts: list[str] = []
    cursor = 0
    total_length = len(normalized)
    for line_index in range(1, line_count):
        remaining_lines = line_count - line_index + 1
        remaining_chars = total_length - cursor
        if remaining_chars <= remaining_lines * 18:
            break
        target = round(total_length * line_index / line_count)
        split_at = nearest_space_split(normalized, target, cursor, total_length)
        part = normalized[cursor:split_at].strip()
        if part:
            parts.append(part)
        cursor = split_at + 1

    tail = normalized[cursor:].strip()
    if tail:
        parts.append(tail)
    return parts or [normalized]


def estimate_block_visual_lines(block: dict[str, Any]) -> list[dict[str, Any]]:
    content = normalize_space(str(block.get("content") or ""))
    content_norm = normalize_match_text(content)
    bbox = block.get("bbox") if isinstance(block.get("bbox"), dict) else None
    page_height = float(block.get("page_height") or 0.0)
    if not content or not content_norm or not bbox or page_height <= 0.0:
        return []

    raw_height = max(1.0, float(bbox.get("h") or 0.0) * page_height)
    height_guess = max(1, round(raw_height / 22.0))
    text_guess = max(1, round(len(content) / 92.0))
    line_count = max(height_guess, min(text_guess, height_guess + 2))
    visual_texts = split_text_into_visual_lines(content, line_count)
    if not visual_texts:
        return []

    line_height = float(bbox["h"]) / max(1, len(visual_texts))
    rows: list[dict[str, Any]] = []
    for line_index, line_text in enumerate(visual_texts):
        line_y = float(bbox["y"]) + line_height * line_index
        line_box = {
            "x": float(bbox["x"]),
            "y": round(clamp01(line_y + line_height * 0.08), 6),
            "w": float(bbox["w"]),
            "h": round(clamp01(line_height * 0.84), 6),
        }
        rows.append(
            {
                "text": line_text,
                "content_norm": normalize_match_text(line_text),
                "bbox": line_box,
                "line_index": line_index,
            }
        )
    return rows


def score_line_window(query_norm: str, query_tokens: list[str], line_rows: list[dict[str, Any]]) -> tuple[float, list[str]]:
    window_norm = normalize_space(" ".join(str(row.get("content_norm") or "") for row in line_rows))
    if not window_norm:
        return 0.0, []

    query_token_set = {str(token) for token in query_tokens if str(token)}
    window_token_set: set[str] = set()
    for row in line_rows:
        window_token_set.update(tokenize(str(row.get("content_norm") or ""), min_len=3, max_items=32))

    matched = [token for token in query_tokens if token in window_token_set]
    overlap = len(set(matched)) / max(1.0, float(len(query_token_set)))
    seq_ratio = SequenceMatcher(a=query_norm[:420], b=window_norm[:420]).ratio() if query_norm else 0.0
    score = overlap * 58.0 + seq_ratio * 44.0 + len(set(matched)) * 2.4
    score -= max(0, len(line_rows) - 4) * 1.6
    return score, unique_preserve_order(matched, 10)


def trim_line_box_to_token_span(line: dict[str, Any], query_tokens: list[str], line_index: int, line_count: int) -> dict[str, float]:
    bbox = line.get("bbox") if isinstance(line.get("bbox"), dict) else {}
    line_norm = str(line.get("content_norm") or "")
    if not bbox or not line_norm:
        return dict(bbox)

    spans: list[tuple[int, int]] = []
    for token in query_tokens:
        token_text = str(token or "")
        if len(token_text) < 3:
            continue
        pos = line_norm.find(token_text)
        if pos >= 0:
            spans.append((pos, pos + len(token_text)))
    if not spans:
        return dict(bbox)

    text_len = max(1, len(line_norm))
    if line_count == 1:
        start_pos = max(0, min(start for start, _ in spans) - 5)
        end_pos = min(text_len, max(end for _, end in spans) + 5)
    elif line_index == 0:
        start_pos = max(0, min(start for start, _ in spans) - 5)
        end_pos = text_len
    elif line_index == line_count - 1:
        start_pos = 0
        end_pos = min(text_len, max(end for _, end in spans) + 5)
    else:
        start_pos = 0
        end_pos = text_len

    left = float(bbox["x"]) + float(bbox["w"]) * (start_pos / text_len)
    right = float(bbox["x"]) + float(bbox["w"]) * (end_pos / text_len)
    pad = min(0.006, float(bbox["w"]) * 0.04)
    left = max(float(bbox["x"]), left - pad)
    right = min(float(bbox["x"]) + float(bbox["w"]), right + pad)
    if right - left < min(0.055, float(bbox["w"])):
        return dict(bbox)

    return {
        "x": round(clamp01(left), 6),
        "y": round(clamp01(float(bbox["y"])), 6),
        "w": round(clamp01(right - left), 6),
        "h": round(clamp01(float(bbox["h"])), 6),
    }


def find_sentence_line_boxes(
    query_norm: str,
    query_tokens: list[str],
    span_blocks: list[dict[str, Any]],
) -> tuple[list[dict[str, float]], list[str]]:
    line_rows: list[dict[str, Any]] = []
    for block in span_blocks:
        for line in block.get("lines", []) if isinstance(block.get("lines"), list) else []:
            if isinstance(line, dict) and line.get("bbox"):
                line_rows.append(line)
    if not line_rows:
        return [], []

    best_score = 0.0
    best_window: list[dict[str, Any]] = []
    best_matched: list[str] = []
    max_window = min(9, len(line_rows))
    for start_index in range(len(line_rows)):
        for window_len in range(1, max_window + 1):
            end_index = start_index + window_len
            if end_index > len(line_rows):
                break
            window = line_rows[start_index:end_index]
            score, matched = score_line_window(query_norm, query_tokens, window)
            if score > best_score:
                best_score = score
                best_window = window
                best_matched = matched

    if not best_window or best_score < 34.0:
        return [], []

    boxes = [
        trim_line_box_to_token_span(line, query_tokens, index, len(best_window))
        for index, line in enumerate(best_window)
    ]
    return boxes, best_matched


def build_chunk_semantic_queries(item: dict[str, Any], split_all_blocks: bool = False) -> list[dict[str, Any]]:
    typed_blocks: list[dict[str, Any]] = []
    for block_index, block in enumerate(item.get("blocks", []) if isinstance(item.get("blocks"), list) else []):
        if not isinstance(block, dict):
            continue
        semantic = normalize_chunk_semantic_kind(str(block.get("type") or ""))
        if not semantic:
            continue
        text_value = str(block.get("text") or "").strip()
        if not text_value:
            text_value = str(block.get("text_zh") or "").strip()
        if not text_value:
            continue
        typed_blocks.append({"semantic": semantic, "text": text_value, "block_index": block_index})

    queries: list[dict[str, Any]] = []
    query_index = 0
    only_discussion = bool(typed_blocks) and all(str(block["semantic"]) == "discussion" for block in typed_blocks)
    for typed in typed_blocks:
        text_parts = (
            split_block_sentences(str(typed["text"]))
            if split_all_blocks or only_discussion
            else [str(typed["text"])]
        )
        for text_part in text_parts:
            block_tokens = tokenize(text_part, min_len=4, max_items=12)
            if not block_tokens:
                continue
            query_index += 1
            queries.append(
                {
                    "semantic": str(typed["semantic"]),
                    "tokens": block_tokens,
                    "text_norm": normalize_match_text(text_part),
                    "query_index": query_index,
                    "block_index": int(typed["block_index"]),
                }
            )

    return queries[:96]


def build_chunk_layout_pool(chapter_layout: dict[str, Any], enable_sentence_lines: bool = False) -> dict[str, Any]:
    pool_blocks: list[dict[str, Any]] = []
    token_index: dict[str, list[int]] = defaultdict(list)
    global_index = 0
    for page in sorted(chapter_layout.get("pages", {}).keys()):
        page_blocks = chapter_layout.get("pages", {}).get(page, [])
        if not isinstance(page_blocks, list):
            continue
        for block in page_blocks:
            label = str(block.get("label") or "")
            content_norm = str(block.get("content_norm") or "")
            if label not in CHUNK_LAYOUT_LABELS or not content_norm:
                continue
            if is_chunk_layout_noise(label, content_norm, block.get("bbox") if isinstance(block.get("bbox"), dict) else None):
                continue
            tokens = tokenize(content_norm, min_len=3, max_items=24)
            row = {
                "global_index": global_index,
                "page": int(page),
                "label": label,
                "content_norm": content_norm,
                "bbox": block.get("bbox"),
                "tokens": tokens,
                "token_set": set(tokens),
                "lines": estimate_block_visual_lines(block) if enable_sentence_lines else [],
            }
            pool_blocks.append(row)
            for token in tokens:
                token_index[token].append(global_index)
            global_index += 1
    return {"blocks": pool_blocks, "token_index": token_index}


def candidate_start_positions(
    query_tokens: list[str], pool: dict[str, Any], last_global_index: int | None
) -> list[int]:
    blocks = pool.get("blocks", []) if isinstance(pool, dict) else []
    token_index = pool.get("token_index", {}) if isinstance(pool, dict) else {}
    if not isinstance(blocks, list) or not blocks:
        return []
    if not isinstance(token_index, dict):
        token_index = {}

    positions: set[int] = set()
    anchor_tokens = sorted(set(str(token) for token in query_tokens if str(token)), key=len, reverse=True)[:6]
    for token in anchor_tokens:
        hits = token_index.get(token) or []
        for global_idx in hits[:360]:
            positions.add(int(global_idx))
            if len(positions) >= 520:
                break
        if len(positions) >= 520:
            break

    if last_global_index is not None and last_global_index >= 0:
        start = max(0, last_global_index - 5)
        end = min(len(blocks) - 1, last_global_index + 140)
        for idx in range(start, end + 1):
            positions.add(idx)

    if not positions:
        limit = min(len(blocks), 240)
        positions = set(range(limit))

    return sorted(positions)


def score_chunk_span(
    query_norm: str,
    query_tokens: list[str],
    span_blocks: list[dict[str, Any]],
    start_global_index: int,
    last_global_index: int | None,
) -> tuple[float, list[str]]:
    if not span_blocks:
        return 0.0, []

    span_text_norm = normalize_space(" ".join(str(block.get("content_norm") or "") for block in span_blocks))
    if not span_text_norm:
        return 0.0, []

    query_token_set = {str(token) for token in query_tokens if str(token)}
    if not query_token_set:
        return 0.0, []

    span_token_set: set[str] = set()
    for block in span_blocks:
        span_token_set.update(str(token) for token in block.get("tokens", []) if str(token))

    matched = [token for token in query_tokens if token in span_token_set]
    if not matched:
        return 0.0, []

    overlap_ratio = len(set(matched)) / max(1.0, float(len(query_token_set)))
    if len(set(matched)) < 2 and overlap_ratio < 0.24:
        return 0.0, []

    seq_ratio = SequenceMatcher(a=query_norm[:520], b=span_text_norm[:520]).ratio() if query_norm else 0.0
    token_weight = sum(min(2.8, max(0.8, len(token) / 4.0)) for token in set(matched))
    score = token_weight * 2.35 + overlap_ratio * 52.0 + seq_ratio * 42.0

    title_penalty = 0.0
    for block in span_blocks:
        label = str(block.get("label") or "")
        if label in {"paragraph_title", "doc_title"}:
            title_penalty += 0.8
    score -= title_penalty

    if last_global_index is not None and last_global_index >= 0:
        distance = start_global_index - last_global_index
        if distance < 0:
            score -= 11.0 + abs(distance) * 1.45
        else:
            score -= min(12.0, distance * 0.16)
            score += max(0.0, 3.2 - distance * 0.09)

    span_len = len(span_blocks)
    score -= max(0, span_len - 1) * 0.55
    return score, unique_preserve_order([token for token in matched], 10)


def union_span_bbox(span_blocks: list[dict[str, Any]]) -> dict[str, float] | None:
    boxes = [block.get("bbox") for block in span_blocks if isinstance(block.get("bbox"), dict)]
    if not boxes:
        return None
    merged = boxes[0]
    for box in boxes[1:]:
        merged = bbox_union(merged, box)
    return merged


def find_chunk_candidates_legacy(item: dict[str, Any], chapter_layout: dict[str, Any]) -> list[dict[str, Any]]:
    tokens = build_chunk_tokens(item)
    if not tokens:
        return []

    toc_hint = item.get("locator", {}).get("toc_page_hint") if isinstance(item.get("locator"), dict) else None
    toc_hint = int(toc_hint) if isinstance(toc_hint, int) else None
    collected: list[dict[str, Any]] = []

    for page, blocks in chapter_layout.get("pages", {}).items():
        block_hits: list[tuple[float, dict[str, Any], list[str]]] = []
        for block in blocks:
            label = str(block.get("label") or "")
            if label not in {"text", "paragraph_title", "doc_title", "figure_title"}:
                continue
            content_norm = str(block.get("content_norm") or "")
            matched = [token for token in tokens if token in content_norm]
            if not matched:
                continue
            block_score = float(len(matched) * 3)
            if label in {"paragraph_title", "doc_title"}:
                block_score += 1.8
            block_score += min(2.2, len(content_norm) / 180.0)
            block_hits.append((block_score, block, matched))

        if not block_hits:
            continue

        block_hits.sort(key=lambda row: (-row[0], -bbox_area(row[1]["bbox"])))
        top_hits = block_hits[:3]
        page_score = sum(hit[0] for hit in top_hits[:2])
        if toc_hint:
            page_score += max(0.0, 6.0 - abs(page - toc_hint))

        boxes = [{"kind": str(hit[1].get("label") or "text"), **hit[1]["bbox"]} for hit in top_hits]
        matched_tokens = unique_preserve_order([token for _, _, matched in top_hits for token in matched], 8)
        candidate_score = 0.36 + min(0.52, page_score / 24.0)
        collected.append(make_candidate(page=page, score=candidate_score, source="layout_chunk_legacy", boxes=boxes, matched=matched_tokens))

    return dedupe_candidates(collected)


def find_chunk_candidates_semantic(
    item: dict[str, Any],
    chapter_layout: dict[str, Any],
    chunk_pool: dict[str, Any] | None = None,
    enable_sentence_lines: bool = False,
) -> list[dict[str, Any]]:
    semantic_queries = build_chunk_semantic_queries(item, split_all_blocks=enable_sentence_lines)
    if not semantic_queries:
        return []

    toc_hint = item.get("locator", {}).get("toc_page_hint") if isinstance(item.get("locator"), dict) else None
    toc_hint = int(toc_hint) if isinstance(toc_hint, int) else None
    chunk_pool = chunk_pool or build_chunk_layout_pool(chapter_layout)
    pool_blocks = chunk_pool.get("blocks", []) if isinstance(chunk_pool, dict) else []
    if not isinstance(pool_blocks, list) or not pool_blocks:
        return []

    ordered_queries = sorted(semantic_queries, key=lambda query: int(query.get("query_index") or 0))
    used_global_indexes: set[int] = set()
    last_global_index: int | None = None
    matched_hits: list[dict[str, Any]] = []

    for query in ordered_queries:
        semantic = str(query.get("semantic") or "")
        tokens = query.get("tokens") if isinstance(query.get("tokens"), list) else []
        query_norm = str(query.get("text_norm") or "")
        query_index = int(query.get("query_index") or 0)
        if not semantic or not tokens:
            continue

        best_match: dict[str, Any] | None = None
        best_span_blocks: list[dict[str, Any]] = []
        best_score = 0.0
        start_positions = candidate_start_positions(tokens, chunk_pool, last_global_index)
        for start_global_index in start_positions:
            if start_global_index < 0 or start_global_index >= len(pool_blocks):
                continue
            if enable_sentence_lines and last_global_index is not None:
                if start_global_index < max(0, last_global_index - 2) or start_global_index > min(
                    len(pool_blocks) - 1, last_global_index + 4
                ):
                    continue
            for span_len in (1, 2, 3):
                end_global_index = start_global_index + span_len - 1
                if end_global_index >= len(pool_blocks):
                    break

                span_blocks = pool_blocks[start_global_index : end_global_index + 1]
                if not span_blocks:
                    continue
                pages = {int(block.get("page") or 0) for block in span_blocks}
                if len(pages) != 1:
                    continue
                span_indexes = {int(block.get("global_index") or -1) for block in span_blocks}
                if not enable_sentence_lines and any(idx in used_global_indexes for idx in span_indexes):
                    continue

                score, matched_tokens = score_chunk_span(
                    query_norm=query_norm,
                    query_tokens=tokens,
                    span_blocks=span_blocks,
                    start_global_index=start_global_index,
                    last_global_index=last_global_index,
                )
                if score <= 0.0:
                    continue

                bbox = union_span_bbox(span_blocks)
                if not bbox:
                    continue
                if score > best_score:
                    best_score = score
                    best_span_blocks = span_blocks
                    best_match = {
                        "semantic": semantic,
                        "query_index": query_index,
                        "start_global_index": start_global_index,
                        "page": int(span_blocks[0].get("page") or 0),
                        "bbox": bbox,
                        "boxes": [bbox],
                        "score": score,
                        "matched": matched_tokens,
                        "global_indexes": sorted(span_indexes),
                        "line_box_count": 0,
                    }

        if best_match and best_score >= 20.0:
            line_boxes, line_matched = find_sentence_line_boxes(query_norm, tokens, best_span_blocks)
            if line_boxes:
                best_match["boxes"] = line_boxes
                best_match["matched"] = line_matched or best_match.get("matched", [])
                best_match["line_box_count"] = len(line_boxes)
            matched_hits.append(best_match)
            if not enable_sentence_lines:
                for idx in best_match["global_indexes"]:
                    used_global_indexes.add(int(idx))
            last_global_index = int(best_match["start_global_index"])

    if not matched_hits:
        return []

    page_hits: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for hit in matched_hits:
        page = int(hit.get("page") or 0)
        if page > 0:
            page_hits[page].append(hit)

    collected: list[dict[str, Any]] = []
    for page, hits in page_hits.items():
        ordered_hits = sorted(hits, key=lambda row: int(row.get("query_index") or 0))
        boxes = [
            {"kind": f"chunk_{hit['semantic']}", **box}
            for hit in ordered_hits
            for box in (hit.get("boxes") if isinstance(hit.get("boxes"), list) else [hit.get("bbox")])
            if isinstance(box, dict)
        ]
        matched_tokens = unique_preserve_order([token for hit in ordered_hits for token in hit.get("matched", [])], 10)
        semantic_coverage = len({str(hit.get("semantic") or "") for hit in ordered_hits})
        page_score = float(sum(float(hit.get("score") or 0.0) for hit in ordered_hits))
        page_score += semantic_coverage * 8.0
        page_score += len(ordered_hits) * 2.2
        if toc_hint:
            page_score += max(0.0, 7.0 - abs(page - toc_hint))
        candidate_score = 0.32 + min(0.66, page_score / 116.0)
        collected.append(
            make_candidate(
                page=page,
                score=candidate_score,
                source="layout_chunk_sentence_lines"
                if any(int(hit.get("line_box_count") or 0) > 0 for hit in ordered_hits)
                else "layout_chunk_precise",
                boxes=boxes,
                matched=matched_tokens,
                max_boxes=180,
            )
        )

    return dedupe_candidates(collected, max_items=3)


def find_chunk_candidates_from_layout(
    item: dict[str, Any],
    chapter_layout: dict[str, Any],
    chunk_pool: dict[str, Any] | None = None,
    enable_sentence_lines: bool = False,
) -> list[dict[str, Any]]:
    semantic_candidates = find_chunk_candidates_semantic(
        item,
        chapter_layout,
        chunk_pool=chunk_pool,
        enable_sentence_lines=enable_sentence_lines,
    )
    if semantic_candidates:
        return semantic_candidates
    return find_chunk_candidates_legacy(item, chapter_layout)


def normalize_formula_index_candidates(raw_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for candidate in raw_candidates:
        if not isinstance(candidate, dict):
            continue
        page = candidate.get("page")
        score = candidate.get("score")
        if not isinstance(page, int):
            continue
        score_value = float(score) if isinstance(score, (int, float)) else 0.72
        raw_boxes = candidate.get("boxes") if isinstance(candidate.get("boxes"), list) else []
        if not raw_boxes and isinstance(candidate.get("bbox"), dict):
            raw_boxes = [candidate.get("bbox")]
        boxes = [box for box in (normalize_candidate_box(box) for box in raw_boxes) if box]
        if not boxes:
            continue
        source = str(candidate.get("source") or "ocr_formula_number")
        candidates.append(make_candidate(page=page, score=score_value, source=source, boxes=boxes, matched=[]))
    return dedupe_candidates(candidates)


def build_review_locator_index(review_dataset: dict[str, Any], formula_ocr_index: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "version": 2,
        "chapters": {},
    }

    chapter_layout_cache: dict[str, dict[str, Any]] = {}
    chapter_chunk_pool_cache: dict[str, dict[str, Any]] = {}
    for chapter in review_dataset.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = str(chapter.get("id") or "").strip().lower()
        if not chapter_id:
            continue
        chapter_layout = load_chapter_layout_blocks(chapter_id)
        chapter_layout_cache[chapter_id] = chapter_layout
        chapter_chunk_pool_cache[chapter_id] = build_chunk_layout_pool(
            chapter_layout,
            enable_sentence_lines=chapter_id in CHUNK_LINE_POC_CHAPTERS,
        )

    for chapter in review_dataset.get("chapters", []):
        if not isinstance(chapter, dict):
            continue
        chapter_id = str(chapter.get("id") or "").strip().lower()
        if not chapter_id:
            continue

        chapter_layout = chapter_layout_cache.get(chapter_id) or {}
        chapter_chunk_pool = chapter_chunk_pool_cache.get(chapter_id) or {}
        chapter_payload: dict[str, Any] = {
            "meta": {
                "source_file": chapter_layout.get("source_file") or "",
                "page_count": int(chapter_layout.get("page_count") or 0),
            },
            "formulas": {},
            "tables": {},
            "chunks": {},
        }

        chapter_rows = review_dataset.get("data", {}).get(chapter_id, {})
        formula_rows = chapter_rows.get("formulas", []) if isinstance(chapter_rows.get("formulas"), list) else []
        table_rows = chapter_rows.get("tables", []) if isinstance(chapter_rows.get("tables"), list) else []
        chunk_rows = chapter_rows.get("chunks", []) if isinstance(chapter_rows.get("chunks"), list) else []

        ocr_formula_map = (
            formula_ocr_index.get("chapters", {}).get(chapter_id, {}).get("formulas", {})
            if isinstance(formula_ocr_index.get("chapters"), dict)
            else {}
        )

        for item in formula_rows:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id") or "").strip().lower()
            if not item_id:
                continue
            formula_candidates: list[dict[str, Any]] = []
            formula_entry = ocr_formula_map.get(item_id)
            if isinstance(formula_entry, dict) and isinstance(formula_entry.get("candidates"), list):
                formula_candidates.extend(normalize_formula_index_candidates(formula_entry["candidates"]))
            formula_candidates.extend(find_formula_candidates_from_layout(item, chapter_layout))
            formula_candidates = dedupe_candidates(formula_candidates)
            if formula_candidates:
                chapter_payload["formulas"][item_id] = {"candidates": formula_candidates}

        for item in table_rows:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id") or "").strip().lower()
            if not item_id:
                continue
            table_candidates = find_table_candidates_from_layout(item, chapter_layout)
            if table_candidates:
                chapter_payload["tables"][item_id] = {"candidates": table_candidates}

        for item in chunk_rows:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id") or "").strip().lower()
            if not item_id:
                continue
            chunk_candidates = find_chunk_candidates_from_layout(
                item,
                chapter_layout,
                chunk_pool=chapter_chunk_pool,
                enable_sentence_lines=chapter_id in CHUNK_LINE_POC_CHAPTERS,
            )
            if chunk_candidates:
                chapter_payload["chunks"][item_id] = {"candidates": chunk_candidates}

        payload["chapters"][chapter_id] = chapter_payload

    return payload


def build_chunk_line_index(chapter_ids: set[str]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "method": "estimated_lines_from_paddle_layout_blocks",
        "chapters": {},
    }
    for chapter_id in sorted(chapter_ids, key=chapter_sort_key):
        chapter_layout = load_chapter_layout_blocks(chapter_id)
        chapter_payload: dict[str, Any] = {
            "source_file": chapter_layout.get("source_file") or "",
            "page_count": int(chapter_layout.get("page_count") or 0),
            "pages": {},
            "line_count": 0,
        }
        for page, blocks in chapter_layout.get("pages", {}).items():
            page_lines: list[dict[str, Any]] = []
            for block_index, block in enumerate(blocks if isinstance(blocks, list) else []):
                label = str(block.get("label") or "")
                if label not in CHUNK_LAYOUT_LABELS:
                    continue
                content_norm = str(block.get("content_norm") or "")
                if is_chunk_layout_noise(label, content_norm, block.get("bbox") if isinstance(block.get("bbox"), dict) else None):
                    continue
                for line in estimate_block_visual_lines(block):
                    page_lines.append(
                        {
                            "block_index": block_index,
                            "label": label,
                            "line_index": int(line.get("line_index") or 0),
                            "text": str(line.get("text") or ""),
                            "bbox": line.get("bbox"),
                        }
                    )
            if page_lines:
                chapter_payload["pages"][str(page)] = page_lines
                chapter_payload["line_count"] += len(page_lines)
        payload["chapters"][chapter_id] = chapter_payload
    return payload


def build_formula_ocr_index(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, set[str]]]:
    payload: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "chapters": {},
    }
    coverage: dict[str, set[str]] = defaultdict(set)

    review_config = config.get("review", {}) if isinstance(config.get("review"), dict) else {}
    structured_dir = resolve_repo_path(str(review_config.get("structured_dir", "data/structured")))

    source_path_map: dict[str, Path] = {}
    structured_chapter_ids: set[str] = set()
    if structured_dir.exists():
        for chapter_path in sorted(structured_dir.glob("*.json")):
            match = CHUNK_FILE_PATTERN.fullmatch(chapter_path.name)
            if not match:
                continue
            chapter_id = match.group(1).lower()
            if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
                continue
            structured_chapter_ids.add(chapter_id)
            if chapter_id in source_path_map:
                continue

            chunk_payload = load_json(chapter_path)
            metadata = chunk_payload.get("metadata", {}) if isinstance(chunk_payload.get("metadata"), dict) else {}
            source_file = str(metadata.get("source_file") or "")
            raw_path = resolve_formula_ocr_raw_path(source_file)
            if raw_path and raw_path.exists():
                source_chapter_id = chapter_id_from_source_file(source_file)
                if not source_chapter_id or source_chapter_id == chapter_id:
                    source_path_map[chapter_id] = raw_path

    if structured_chapter_ids:
        for chapter_id in sorted(structured_chapter_ids, key=chapter_sort_key):
            fallback_path = PADDLE_OUTPUT_DIR / f"{chapter_id}_full" / "intermediate" / "paddle_raw_api_response.json"
            if fallback_path.exists():
                source_path_map.setdefault(chapter_id, fallback_path)
    else:
        for raw_path in sorted(PADDLE_OUTPUT_DIR.glob("*_full/intermediate/paddle_raw_api_response.json")):
            folder_name = raw_path.parent.parent.name
            if not folder_name.endswith("_full"):
                continue
            chapter_id = folder_name[: -len("_full")].strip().lower()
            if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
                continue
            source_path_map[chapter_id] = raw_path

    source_paths = sorted(source_path_map.items(), key=lambda row: chapter_sort_key(row[0]))

    for chapter_id, raw_path in source_paths:
        raw = load_json(raw_path)
        result = raw.get("result", {})
        pages = result.get("layoutParsingResults", []) if isinstance(result, dict) else []
        if not isinstance(pages, list) or not pages:
            continue

        chapter_rows: dict[str, Any] = {
            "source_file": str(raw_path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "page_count": len(pages),
            "formulas": {},
        }

        grouped_candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for page_index, page_payload in enumerate(pages, start=1):
            pruned = page_payload.get("prunedResult", {}) if isinstance(page_payload, dict) else {}
            page_width = float(pruned.get("width") or 0.0)
            page_height = float(pruned.get("height") or 0.0)
            parsing_rows = pruned.get("parsing_res_list", []) if isinstance(pruned.get("parsing_res_list"), list) else []

            formula_blocks: list[dict[str, Any]] = []
            number_blocks: list[dict[str, Any]] = []
            for row in parsing_rows:
                if not isinstance(row, dict):
                    continue
                label = str(row.get("block_label") or "").strip().lower()
                bbox = normalize_bbox(row.get("block_bbox") or [], page_width, page_height)
                if not bbox:
                    continue
                score = float(row.get("score") or 0.0) if row.get("score") is not None else 0.0
                entry = {
                    "label": label,
                    "bbox": bbox,
                    "score": score,
                    "content": str(row.get("block_content") or ""),
                }
                if label in {"display_formula", "inline_formula"}:
                    formula_blocks.append(entry)
                elif label == "formula_number":
                    formula_id = parse_formula_number_id(entry["content"])
                    if formula_id:
                        entry["formula_id"] = formula_id
                        number_blocks.append(entry)

            for number_block in number_blocks:
                formula_id = number_block["formula_id"]
                number_bbox = number_block["bbox"]
                number_center = bbox_center(number_bbox)
                nearest_formula = None
                nearest_distance = 999.0
                for formula_block in formula_blocks:
                    formula_center = bbox_center(formula_block["bbox"])
                    distance = abs(formula_center[1] - number_center[1]) + abs(formula_center[0] - number_center[0]) * 0.35
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_formula = formula_block

                boxes = [{"kind": "formula_number", **number_bbox}]
                score = 0.62
                merged_bbox = number_bbox
                if nearest_formula and nearest_distance <= 0.22:
                    formula_bbox = nearest_formula["bbox"]
                    boxes.insert(0, {"kind": nearest_formula["label"], **formula_bbox})
                    merged_bbox = bbox_union(formula_bbox, number_bbox)
                    score = 0.92 - min(0.32, nearest_distance)

                grouped_candidates[formula_id].append(
                    {
                        "page": page_index,
                        "score": round(max(0.01, min(0.99, score)), 4),
                        "source": "ocr_formula_number",
                        "bbox": merged_bbox,
                        "boxes": boxes,
                    }
                )

        for formula_id, rows in grouped_candidates.items():
            rows.sort(key=lambda row: (-float(row.get("score", 0.0)), int(row.get("page", 0))))
            chapter_rows["formulas"][formula_id] = {"candidates": rows[:3]}
            coverage[chapter_id].add(formula_id)

        payload["chapters"][chapter_id] = chapter_rows

    return payload, coverage


def build_toc_locator_index() -> dict[str, dict[str, Any]]:
    if not TOC_TREE_PATH.exists():
        return {}

    payload = load_json(TOC_TREE_PATH)
    nodes = payload.get("nodes", {})
    if not isinstance(nodes, dict):
        return {}

    index: dict[str, dict[str, Any]] = {}
    for node in nodes.values():
        if not isinstance(node, dict):
            continue

        raw_title = str(node.get("title") or "").strip()
        entry_type = str(node.get("entry_type") or "").strip().lower()
        page = node.get("page")
        if not raw_title or not isinstance(page, int) or page <= 0:
            continue

        chapter_key = None
        chapter_match = re.search(r"\b(\d+)\.", raw_title)
        appendix_match = re.search(r"\bA(\d+)\.", raw_title, flags=re.IGNORECASE)
        if entry_type == "chapter" and chapter_match:
            chapter_key = f"chapter{int(chapter_match.group(1))}"
        elif entry_type == "appendix" and appendix_match:
            chapter_key = f"appendix{int(appendix_match.group(1))}"

        if chapter_key:
            index.setdefault(
                chapter_key,
                {
                    "chapter_page": page,
                    "chapter_title": raw_title,
                    "terms": [],
                },
            )
            index[chapter_key]["chapter_page"] = page
            index[chapter_key]["chapter_title"] = raw_title

    for node in nodes.values():
        if not isinstance(node, dict):
            continue
        raw_title = str(node.get("title") or "").strip()
        page = node.get("page")
        if not raw_title or not isinstance(page, int) or page <= 0:
            continue

        lineage_titles = [raw_title]
        parent_id = node.get("parent_id")
        visited: set[str] = set()
        while isinstance(parent_id, str) and parent_id and parent_id not in visited:
            visited.add(parent_id)
            parent = nodes.get(parent_id)
            if not isinstance(parent, dict):
                break
            parent_title = str(parent.get("title") or "").strip()
            if parent_title:
                lineage_titles.append(parent_title)
            parent_id = parent.get("parent_id")

        chapter_id = None
        for title in lineage_titles:
            chapter_match = re.search(r"\b(\d+)\.", title)
            if chapter_match:
                chapter_id = f"chapter{int(chapter_match.group(1))}"
                break
            appendix_match = re.search(r"\bA(\d+)\.", title, flags=re.IGNORECASE)
            if appendix_match:
                chapter_id = f"appendix{int(appendix_match.group(1))}"
                break
        if not chapter_id or chapter_id not in index:
            continue

        term_norm = normalize_title_key(raw_title)
        if not term_norm:
            continue
        index[chapter_id]["terms"].append(
            {
                "title": raw_title,
                "title_norm": term_norm,
                "page": page,
            }
        )

    for chapter_id, chapter_payload in index.items():
        unique_terms: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        for term in chapter_payload["terms"]:
            key = (term["title_norm"], int(term["page"]))
            if key in seen:
                continue
            seen.add(key)
            unique_terms.append(term)
        unique_terms.sort(key=lambda item: (item["page"], item["title_norm"]))
        chapter_payload["terms"] = unique_terms

    return index


def lookup_toc_hint(chapter_id: str, subsection: str, toc_index: dict[str, dict[str, Any]]) -> tuple[int | None, str | None, float]:
    chapter_payload = toc_index.get(chapter_id)
    if not chapter_payload:
        return None, None, 0.0

    chapter_page = chapter_payload.get("chapter_page")
    if not subsection:
        return chapter_page if isinstance(chapter_page, int) else None, None, 0.0

    best_page: int | None = None
    best_title: str | None = None
    best_score = 0.0
    for term in chapter_payload.get("terms", []):
        score = title_similarity(subsection, term.get("title", ""))
        if score > best_score:
            best_score = score
            best_page = term.get("page")
            best_title = term.get("title")

    if best_score >= 0.38 and isinstance(best_page, int):
        return best_page, best_title, best_score

    return chapter_page if isinstance(chapter_page, int) else None, None, best_score


def build_locator(
    chapter_id: str,
    subsection: str,
    source_unit_id: str,
    search_keys: list[str],
    toc_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    toc_page_hint, matched_title, matched_score = lookup_toc_hint(chapter_id, subsection, toc_index)
    terms = build_search_keys([subsection, source_unit_id, *search_keys], max_items=10)
    chapter_payload = toc_index.get(chapter_id, {})
    chapter_page = chapter_payload.get("chapter_page")
    return {
        "subsection": subsection or "",
        "toc_page_hint": toc_page_hint if isinstance(toc_page_hint, int) else None,
        "toc_match_title": matched_title,
        "toc_match_score": round(float(matched_score), 4),
        "toc_chapter_page": chapter_page if isinstance(chapter_page, int) else None,
        "terms": terms,
        "source_unit_id": source_unit_id or "",
    }


def infer_chunk_unit_id(chunk_id: str) -> str:
    return chunk_id.replace("_", "_block_", 1) if "_" in chunk_id else chunk_id


def strip_latex(latex: str) -> str:
    text = str(latex or "")
    text = text.replace("$$", " ").replace("$", " ")
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    text = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_chunk_item(payload: dict[str, Any], chapter_id: str, file_name: str, toc_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metadata = payload.get("metadata", {}) if isinstance(payload.get("metadata"), dict) else {}
    blocks = payload.get("blocks", []) if isinstance(payload.get("blocks"), list) else []
    chunk_id = str(payload.get("id") or Path(file_name).stem).strip()
    section = str(metadata.get("section", "")).strip()
    subsections = metadata.get("subsections", []) if isinstance(metadata.get("subsections"), list) else []
    subsection_path = " / ".join(str(item).strip() for item in subsections if str(item).strip())
    block_rows: list[dict[str, str]] = []
    for raw_block in blocks[:48]:
        if not isinstance(raw_block, dict):
            continue
        text_zh = normalize_space(
            str(
                raw_block.get("content_zh")
                or raw_block.get("text_zh")
                or raw_block.get("translation_zh")
                or ""
            )
        )
        block_rows.append(
            {
                "type": str(raw_block.get("type") or "unknown"),
                "text": normalize_space(str(raw_block.get("content") or "")),
                "text_zh": normalize_space(text_zh) if text_zh else "",
            }
        )
    preview_text = trim_text(" ".join(row["text"] for row in block_rows), 340)
    formula_refs = metadata.get("formula_references", []) if isinstance(metadata.get("formula_references"), list) else []
    table_refs = metadata.get("table_references", []) if isinstance(metadata.get("table_references"), list) else []
    search_keys = build_search_keys(
        [
            chunk_id,
            section,
            subsection_path,
            preview_text,
            " ".join(str(ref) for ref in formula_refs[:8]),
            " ".join(str(ref) for ref in table_refs[:8]),
        ]
    )
    source_unit_id = infer_chunk_unit_id(chunk_id)
    return {
        "id": chunk_id,
        "chapter": chapter_id,
        "item_key": f"{chapter_id}::chunks::{chunk_id}",
        "title": section or chunk_id,
        "subtitle": subsection_path or "No subsection",
        "excerpt": preview_text,
        "source_unit_id": source_unit_id,
        "source_file": str(metadata.get("source_file") or ""),
        "formula_references": [str(ref) for ref in formula_refs[:24]],
        "table_references": [str(ref) for ref in table_refs[:24]],
        "block_count": len(blocks),
        "blocks": block_rows,
        "search_keys": search_keys,
        "locator": build_locator(chapter_id, subsection_path or section, source_unit_id, search_keys, toc_index),
    }


def normalize_formula_item(
    raw_item: dict[str, Any], toc_index: dict[str, dict[str, Any]], ocr_coverage: dict[str, set[str]]
) -> dict[str, Any]:
    source = raw_item.get("source", {}) if isinstance(raw_item.get("source"), dict) else {}
    chapter_id = str(source.get("chapter") or "").strip().lower()
    formula_id = str(raw_item.get("id") or "").strip()
    label_format = str(raw_item.get("label_format") or "").strip()
    latex = str(raw_item.get("latex") or "")
    subsection = str(source.get("subsection") or "").strip()
    context = str(raw_item.get("context") or "")
    context_preview = trim_text(context, 340)
    search_keys = build_search_keys(
        [
            formula_id,
            label_format,
            strip_latex(latex),
            subsection,
            context_preview,
        ]
    )
    source_unit_id = str(source.get("unit_id") or "")
    source_page = source.get("page")
    row = {
        "id": formula_id,
        "chapter": chapter_id,
        "item_key": f"{chapter_id}::formulas::{formula_id}",
        "title": label_format or formula_id,
        "subtitle": subsection or "No subsection",
        "excerpt": context_preview,
        "latex": latex,
        "formula_type": str(raw_item.get("formula_type") or ""),
        "source_unit_id": source_unit_id,
        "source_page": source_page if isinstance(source_page, int) and source_page > 0 else None,
        "search_keys": search_keys,
        "locator": build_locator(chapter_id, subsection, source_unit_id, search_keys, toc_index),
    }
    row["locator"]["ocr_available"] = formula_id.lower() in ocr_coverage.get(chapter_id, set())
    return row


def normalize_table_item(raw_item: dict[str, Any], toc_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = raw_item.get("source", {}) if isinstance(raw_item.get("source"), dict) else {}
    chapter_id = str(source.get("chapter") or "").strip().lower()
    table_id = str(raw_item.get("id") or "").strip()
    label_format = str(raw_item.get("label_format") or "").strip()
    title = str(raw_item.get("title") or "").strip()
    subsection = str(source.get("subsection") or "").strip()
    rows = raw_item.get("rows", []) if isinstance(raw_item.get("rows"), list) else []
    row_count = len(rows)
    col_count = max((len(row) for row in rows if isinstance(row, list)), default=0)
    row_preview_parts: list[str] = []
    for row in rows[:4]:
        if isinstance(row, list):
            row_preview_parts.append(" | ".join(trim_text(str(cell), 60) for cell in row[:6]))
    row_preview = " ; ".join(row_preview_parts)
    search_keys = build_search_keys(
        [
            table_id,
            label_format,
            title,
            subsection,
            row_preview,
        ]
    )
    source_unit_id = str(source.get("unit_id") or "")
    source_page = source.get("page")
    return {
        "id": table_id,
        "chapter": chapter_id,
        "item_key": f"{chapter_id}::tables::{table_id}",
        "title": label_format or table_id,
        "subtitle": subsection or "No subsection",
        "excerpt": trim_text(title, 300),
        "table_type": str(raw_item.get("table_type") or ""),
        "row_count": row_count,
        "column_count": col_count,
        "source_unit_id": source_unit_id,
        "source_page": source_page if isinstance(source_page, int) and source_page > 0 else None,
        "html": str(raw_item.get("html") or ""),
        "search_keys": search_keys,
        "locator": build_locator(chapter_id, subsection, source_unit_id, search_keys, toc_index),
    }


def parse_risk_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    match = re.search(r"##\s*5\.\s*风险点(.*)$", text, flags=re.DOTALL)
    if not match:
        return rows
    section = match.group(1)
    table_match = re.search(r"\| 风险 \| 描述 \| 当前状态 \|\s*\n\|[-\s|]+\|\s*\n((?:\|.*\|\s*\n?)+)", section)
    if not table_match:
        return rows
    for line in table_match.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) >= 3:
            rows.append({"risk": parts[0], "description": parts[1], "status": parts[2]})
    return rows


def build_review_dataset(config: dict[str, Any], ocr_coverage: dict[str, set[str]] | None = None) -> dict[str, Any]:
    review_config = config.get("review", {}) if isinstance(config.get("review"), dict) else {}
    structured_dir = resolve_repo_path(str(review_config.get("structured_dir", "data/structured")))
    pdf_dir = resolve_repo_path(str(review_config.get("pdf_dir", "data/背景资料")))
    preferred_default_chapter = str(review_config.get("default_chapter") or "").strip().lower()
    ocr_coverage = ocr_coverage or {}

    toc_index = build_toc_locator_index()
    chapter_ids: set[str] = set()
    chapter_chunks: dict[str, list[dict[str, Any]]] = defaultdict(list)
    chapter_formulas: dict[str, list[dict[str, Any]]] = defaultdict(list)
    chapter_tables: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(structured_dir.glob("*.json")):
        match = CHUNK_FILE_PATTERN.fullmatch(path.name)
        if not match:
            continue
        chapter_id = match.group(1).lower()
        chapter_ids.add(chapter_id)
        chapter_chunks[chapter_id].append(normalize_chunk_item(load_json(path), chapter_id, path.name, toc_index))

    formula_library_path = structured_dir / "formula_library.json"
    if formula_library_path.exists():
        formula_payload = load_json(formula_library_path)
        formulas = formula_payload.get("formulas", []) if isinstance(formula_payload.get("formulas"), list) else []
        for raw_item in formulas:
            if not isinstance(raw_item, dict):
                continue
            normalized = normalize_formula_item(raw_item, toc_index, ocr_coverage)
            chapter_id = normalized["chapter"]
            if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
                continue
            chapter_ids.add(chapter_id)
            chapter_formulas[chapter_id].append(normalized)

    table_library_path = structured_dir / "table_library.json"
    if table_library_path.exists():
        table_payload = load_json(table_library_path)
        tables = table_payload.get("tables", []) if isinstance(table_payload.get("tables"), list) else []
        for raw_item in tables:
            if not isinstance(raw_item, dict):
                continue
            normalized = normalize_table_item(raw_item, toc_index)
            chapter_id = normalized["chapter"]
            if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
                continue
            chapter_ids.add(chapter_id)
            chapter_tables[chapter_id].append(normalized)

    filtered_chapters = sorted((chapter_id for chapter_id in chapter_ids if CHAPTER_ID_PATTERN.fullmatch(chapter_id)), key=chapter_sort_key)

    for chapter_id in filtered_chapters:
        chapter_chunks[chapter_id].sort(key=lambda row: row["id"])
        chapter_formulas[chapter_id].sort(key=lambda row: formula_sort_key(row["id"]))
        chapter_tables[chapter_id].sort(key=lambda row: formula_sort_key(row["id"]))

    chapters: list[dict[str, Any]] = []
    data: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for chapter_id in filtered_chapters:
        pdf_file = pdf_dir / f"{chapter_id}.pdf"
        pdf_path = f"/{pdf_file.relative_to(ROOT_DIR).as_posix()}" if pdf_file.exists() else ""
        chapter_rows = {
            "chunks": chapter_chunks.get(chapter_id, []),
            "formulas": chapter_formulas.get(chapter_id, []),
            "tables": chapter_tables.get(chapter_id, []),
        }
        counts = {view_id: len(rows) for view_id, rows in chapter_rows.items()}
        chapters.append(
            {
                "id": chapter_id,
                "label": chapter_label(chapter_id),
                "pdf_path": pdf_path,
                "pdf_exists": bool(pdf_path),
                "counts": counts,
                "toc_chapter_page": toc_index.get(chapter_id, {}).get("chapter_page"),
                "toc_chapter_title": toc_index.get(chapter_id, {}).get("chapter_title"),
            }
        )
        data[chapter_id] = chapter_rows

    chapter_id_set = {chapter["id"] for chapter in chapters}
    default_chapter = (
        preferred_default_chapter
        if preferred_default_chapter in chapter_id_set
        else "chapter5"
        if "chapter5" in chapter_id_set
        else chapters[0]["id"]
        if chapters
        else None
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "structured_dir": str(structured_dir.relative_to(ROOT_DIR)).replace("\\", "/") if structured_dir.exists() else str(structured_dir),
        "structured_source_version": structured_source_version(structured_dir),
        "views": [
            {"id": "formulas", "label": "公式库"},
            {"id": "tables", "label": "表格库"},
            {"id": "chunks", "label": "Chunk（中英）"},
        ],
        "chapters": chapters,
        "default_chapter": default_chapter,
        "data": data,
        "locator_version": 2,
    }


def build_flow_graph(config: dict[str, Any]) -> dict[str, Any]:
    flow_config = config.get("flow", {}) if isinstance(config.get("flow"), dict) else {}
    docs_path = resolve_repo_path(str(flow_config.get("docs_path", "docs/architecture.md")))
    docs_text = docs_path.read_text(encoding="utf-8-sig") if docs_path.exists() else ""

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_doc": str(docs_path.relative_to(ROOT_DIR)).replace("\\", "/") if docs_path.exists() else "",
        "overview_nodes": [
            {
                "id": "ocr_input",
                "title": "OCR Input",
                "subtitle": "PDF -> OCR pages",
                "detail": "原始 PDF 经 OCR 后形成页面级文本与布局信息。",
            },
            {
                "id": "layout_normalizer",
                "title": "Layout Normalizer",
                "subtitle": "block sequence",
                "detail": "统一页面 block 表示，保留结构线索，供后续模块复用。",
            },
            {
                "id": "markdown_structurer",
                "title": "Markdown Structurer",
                "subtitle": "main orchestrator",
                "detail": "负责 heading、chunk 切分、内容分类与库对象装配。",
            },
            {
                "id": "library_builder",
                "title": "Library Builder",
                "subtitle": "formula/table assets",
                "detail": "生成 formula_library 与 table_library，并写回 chunk 引用。",
            },
            {
                "id": "structured_output",
                "title": "Structured Output",
                "subtitle": "chunk/formula/table JSON",
                "detail": "形成可检索、可审核、可追溯的结构化产物。",
            },
        ],
        "subflows": {
            "formulas": [
                {
                    "title": "Candidate Builder",
                    "detail": "从局部上下文、编号线索、版面邻近性生成候选公式编号。",
                },
                {
                    "title": "Evidence Scorer",
                    "detail": "融合局部证据与全局提及频次，形成候选优先级。",
                },
                {
                    "title": "Assignment + Repair",
                    "detail": "通过约束求解与后处理修复编号跳变、缺失、冲突问题。",
                },
                {
                    "title": "Formula Library Output",
                    "detail": "输出稳定编号公式对象，并关联 source.unit_id 与上下文。",
                },
            ],
            "tables": [
                {
                    "title": "Table Detection",
                    "detail": "检测表格块并提取标题、行列结构与 HTML 表示。",
                },
                {
                    "title": "Canonicalization",
                    "detail": "统一表格 ID 与编号形式，减少跨版本命名漂移。",
                },
                {
                    "title": "Chunk Linking",
                    "detail": "把 table 引用写回 chunk metadata，建立前后向关系。",
                },
                {
                    "title": "Table Library Output",
                    "detail": "输出表格资产，供检索与对照审核使用。",
                },
            ],
            "chunks": [
                {
                    "title": "Section Parsing",
                    "detail": "按章节层级解析标题，建立 section/subsection 路径。",
                },
                {
                    "title": "Chunk Segmentation",
                    "detail": "按语义与长度切分 chunk，并保留 block 序列信息。",
                },
                {
                    "title": "Reference Enrichment",
                    "detail": "填充 formula_references/table_references 与 source_file。",
                },
                {
                    "title": "Chunk JSON Output",
                    "detail": "输出可下游消费的 chunk JSON 列表。",
                },
            ],
        },
        "risks": parse_risk_rows(docs_text),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build review_app generated datasets from structured assets.")
    parser.add_argument("--structured-dir", default="", help="Override review.structured_dir (repo-relative or absolute).")
    parser.add_argument("--pdf-dir", default="", help="Override review.pdf_dir (repo-relative or absolute).")
    parser.add_argument("--docs-path", default="", help="Override flow.docs_path (repo-relative or absolute).")
    parser.add_argument(
        "--chapters",
        default="",
        help="Restrict generated review_dataset.json to comma-separated chapter ids, e.g. chapter5,chapter13.",
    )
    parser.add_argument(
        "--locator-chapters",
        default="",
        help="Refresh only tmp locator artifacts for comma-separated chapters, reusing generated review_dataset.json.",
    )
    parser.add_argument(
        "--skip-locator",
        action="store_true",
        help="Refresh generated review datasets without rebuilding the slower PDF locator index.",
    )
    return parser.parse_args(argv)


def apply_config_overrides(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    effective = dict(config)
    review = dict(effective.get("review", {})) if isinstance(effective.get("review"), dict) else {}
    flow = dict(effective.get("flow", {})) if isinstance(effective.get("flow"), dict) else {}

    if str(args.structured_dir or "").strip():
        review["structured_dir"] = str(args.structured_dir).strip()
    if str(args.pdf_dir or "").strip():
        review["pdf_dir"] = str(args.pdf_dir).strip()
    if str(args.docs_path or "").strip():
        flow["docs_path"] = str(args.docs_path).strip()

    effective["review"] = review
    effective["flow"] = flow
    return effective


def parse_chapter_filter(raw_value: str) -> set[str]:
    values: set[str] = set()
    for part in str(raw_value or "").split(","):
        chapter_id = part.strip().lower()
        if CHAPTER_ID_PATTERN.fullmatch(chapter_id):
            values.add(chapter_id)
    return values


def filter_review_dataset(review_dataset: dict[str, Any], chapter_ids: set[str]) -> dict[str, Any]:
    chapters = [
        chapter
        for chapter in review_dataset.get("chapters", [])
        if isinstance(chapter, dict) and str(chapter.get("id") or "").strip().lower() in chapter_ids
    ]
    data_source = review_dataset.get("data", {}) if isinstance(review_dataset.get("data"), dict) else {}
    ordered_chapter_ids = [str(chapter.get("id") or "").strip().lower() for chapter in chapters]
    data = {chapter_id: data_source.get(chapter_id, {}) for chapter_id in ordered_chapter_ids if chapter_id in data_source}
    return {
        **review_dataset,
        "chapters": chapters,
        "data": data,
        "default_chapter": chapters[0]["id"] if chapters else "",
        "chapter_filter": ordered_chapter_ids,
        "prepared_scope": "targeted_chapters" if chapter_ids else "all_chapters",
    }


def formula_ocr_coverage_from_index(formula_ocr_index: dict[str, Any]) -> dict[str, set[str]]:
    coverage: dict[str, set[str]] = defaultdict(set)
    chapters = formula_ocr_index.get("chapters", {}) if isinstance(formula_ocr_index.get("chapters"), dict) else {}
    for chapter_id, chapter_payload in chapters.items():
        if not isinstance(chapter_payload, dict):
            continue
        formulas = chapter_payload.get("formulas", {}) if isinstance(chapter_payload.get("formulas"), dict) else {}
        coverage[str(chapter_id).lower()].update(str(formula_id).lower() for formula_id in formulas.keys())
    return coverage


def refresh_library_rows_for_chapters(
    review_dataset: dict[str, Any],
    config: dict[str, Any],
    chapter_ids: set[str],
    formula_ocr_index: dict[str, Any],
) -> dict[str, Any]:
    review_config = config.get("review", {}) if isinstance(config.get("review"), dict) else {}
    structured_dir = resolve_repo_path(str(review_config.get("structured_dir", "data/structured")))
    toc_index = build_toc_locator_index()
    ocr_coverage = formula_ocr_coverage_from_index(formula_ocr_index)

    data = review_dataset.setdefault("data", {})
    if not isinstance(data, dict):
        review_dataset["data"] = {}
        data = review_dataset["data"]

    formula_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    formula_library_path = structured_dir / "formula_library.json"
    if formula_library_path.exists():
        formula_payload = load_json(formula_library_path)
        for raw_item in formula_payload.get("formulas", []) if isinstance(formula_payload.get("formulas"), list) else []:
            if not isinstance(raw_item, dict):
                continue
            normalized = normalize_formula_item(raw_item, toc_index, ocr_coverage)
            chapter_id = normalized.get("chapter")
            if chapter_id in chapter_ids:
                formula_rows[chapter_id].append(normalized)

    table_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    table_library_path = structured_dir / "table_library.json"
    if table_library_path.exists():
        table_payload = load_json(table_library_path)
        for raw_item in table_payload.get("tables", []) if isinstance(table_payload.get("tables"), list) else []:
            if not isinstance(raw_item, dict):
                continue
            normalized = normalize_table_item(raw_item, toc_index)
            chapter_id = normalized.get("chapter")
            if chapter_id in chapter_ids:
                table_rows[chapter_id].append(normalized)

    for chapter_id in chapter_ids:
        chapter_data = data.setdefault(chapter_id, {})
        if not isinstance(chapter_data, dict):
            chapter_data = {}
            data[chapter_id] = chapter_data
        if chapter_id in formula_rows:
            chapter_data["formulas"] = sorted(formula_rows[chapter_id], key=lambda row: formula_sort_key(row["id"]))
        if chapter_id in table_rows:
            chapter_data["tables"] = sorted(table_rows[chapter_id], key=lambda row: formula_sort_key(row["id"]))

    return review_dataset


def refresh_locator_artifacts_for_chapters(config: dict[str, Any], chapter_ids: set[str]) -> None:
    if not chapter_ids:
        raise SystemExit("--locator-chapters did not contain any valid chapter ids.")
    if not REVIEW_DATASET_PATH.exists():
        raise SystemExit(f"Missing {REVIEW_DATASET_PATH}; run a full build once before partial locator refresh.")

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    formula_ocr_index = load_json(FORMULA_OCR_INDEX_PATH) if FORMULA_OCR_INDEX_PATH.exists() else build_formula_ocr_index(config)[0]
    review_dataset = load_json(REVIEW_DATASET_PATH)
    partial_dataset = filter_review_dataset(review_dataset, chapter_ids)
    if not partial_dataset.get("chapters"):
        raise SystemExit(f"No selected chapters found in {REVIEW_DATASET_PATH}: {', '.join(sorted(chapter_ids))}")
    partial_dataset = refresh_library_rows_for_chapters(partial_dataset, config, chapter_ids, formula_ocr_index)
    partial_locator_index = build_review_locator_index(partial_dataset, formula_ocr_index)

    locator_index = (
        load_json(REVIEW_LOCATOR_INDEX_PATH)
        if REVIEW_LOCATOR_INDEX_PATH.exists()
        else {"generated_at": "", "version": 2, "chapters": {}}
    )
    locator_chapters = locator_index.setdefault("chapters", {})
    for chapter_id, chapter_payload in partial_locator_index.get("chapters", {}).items():
        locator_chapters[chapter_id] = chapter_payload
    locator_index["generated_at"] = datetime.now().isoformat(timespec="seconds")
    locator_index["version"] = 2

    partial_chunk_line_index = build_chunk_line_index(chapter_ids & CHUNK_LINE_POC_CHAPTERS)
    chunk_line_index = (
        load_json(CHUNK_LINE_INDEX_PATH)
        if CHUNK_LINE_INDEX_PATH.exists()
        else {
            "generated_at": "",
            "method": "estimated_lines_from_paddle_layout_blocks",
            "chapters": {},
        }
    )
    line_chapters = chunk_line_index.setdefault("chapters", {})
    for chapter_id, chapter_payload in partial_chunk_line_index.get("chapters", {}).items():
        line_chapters[chapter_id] = chapter_payload
    chunk_line_index["generated_at"] = datetime.now().isoformat(timespec="seconds")
    chunk_line_index["method"] = "estimated_lines_from_paddle_layout_blocks"

    write_json(REVIEW_LOCATOR_INDEX_PATH, locator_index)
    write_json(CHUNK_LINE_INDEX_PATH, chunk_line_index)
    write_json(
        BUILD_TRACE_PATH,
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "partial_locator_refresh": sorted(chapter_ids, key=chapter_sort_key),
            "review_locator_coverage": {
                chapter_id: {
                    "formulas": len((chapter_payload.get("formulas") or {}).keys()),
                    "tables": len((chapter_payload.get("tables") or {}).keys()),
                    "chunks": len((chapter_payload.get("chunks") or {}).keys()),
                }
                for chapter_id, chapter_payload in (partial_locator_index.get("chapters") or {}).items()
                if isinstance(chapter_payload, dict)
            },
            "chunk_line_index": {
                chapter_id: {
                    "pages": len((chapter_payload.get("pages") or {}).keys()),
                    "lines": int(chapter_payload.get("line_count") or 0),
                    "source_file": chapter_payload.get("source_file") or "",
                }
                for chapter_id, chapter_payload in (partial_chunk_line_index.get("chapters") or {}).items()
                if isinstance(chapter_payload, dict)
            },
        },
    )

    print("Refreshed tmp locator artifacts:")
    print(f"  {REVIEW_LOCATOR_INDEX_PATH}")
    print(f"  {CHUNK_LINE_INDEX_PATH}")
    print(f"  {BUILD_TRACE_PATH}")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_json(CONFIG_PATH) if CONFIG_PATH.exists() else {}
    config = apply_config_overrides(config, args)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    locator_chapters = parse_chapter_filter(args.locator_chapters)
    if locator_chapters:
        refresh_locator_artifacts_for_chapters(config, locator_chapters)
        return

    formula_ocr_index, ocr_coverage = build_formula_ocr_index(config)
    review_dataset = build_review_dataset(config, ocr_coverage=ocr_coverage)
    target_chapters = parse_chapter_filter(args.chapters)
    if target_chapters:
        review_dataset = filter_review_dataset(review_dataset, target_chapters)
        if not review_dataset.get("chapters"):
            raise SystemExit(f"No selected chapters found in structured data: {', '.join(sorted(target_chapters, key=chapter_sort_key))}")
    flow_graph = build_flow_graph(config)
    review_locator_index = (
        load_json(REVIEW_LOCATOR_INDEX_PATH)
        if args.skip_locator and REVIEW_LOCATOR_INDEX_PATH.exists()
        else build_review_locator_index(review_dataset, formula_ocr_index)
    )
    chunk_line_chapters = (target_chapters or CHUNK_LINE_POC_CHAPTERS) & CHUNK_LINE_POC_CHAPTERS
    chunk_line_index = build_chunk_line_index(chunk_line_chapters)

    write_json(REVIEW_DATASET_PATH, review_dataset)
    write_json(FLOW_GRAPH_PATH, flow_graph)
    write_json(FORMULA_OCR_INDEX_PATH, formula_ocr_index)
    if not args.skip_locator:
        write_json(REVIEW_LOCATOR_INDEX_PATH, review_locator_index)
    write_json(CHUNK_LINE_INDEX_PATH, chunk_line_index)
    write_json(
        BUILD_TRACE_PATH,
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "review_locator_skipped": bool(args.skip_locator),
            "chapter_count": len(review_dataset.get("chapters", [])),
            "chapters_without_pdf": [
                chapter.get("id")
                for chapter in review_dataset.get("chapters", [])
                if not chapter.get("pdf_exists")
            ],
            "counts": {
                chapter.get("id"): chapter.get("counts", {})
                for chapter in review_dataset.get("chapters", [])
            },
            "formula_ocr_coverage": {
                chapter_id: len(sorted(ids))
                for chapter_id, ids in ocr_coverage.items()
            },
            "review_locator_coverage": {
                chapter_id: {
                    "formulas": len((chapter_payload.get("formulas") or {}).keys()),
                    "tables": len((chapter_payload.get("tables") or {}).keys()),
                    "chunks": len((chapter_payload.get("chunks") or {}).keys()),
                }
                for chapter_id, chapter_payload in (review_locator_index.get("chapters") or {}).items()
                if isinstance(chapter_payload, dict)
            },
            "chunk_line_index": {
                chapter_id: {
                    "pages": len((chapter_payload.get("pages") or {}).keys()),
                    "lines": int(chapter_payload.get("line_count") or 0),
                    "source_file": chapter_payload.get("source_file") or "",
                }
                for chapter_id, chapter_payload in (chunk_line_index.get("chapters") or {}).items()
                if isinstance(chapter_payload, dict)
            },
        },
    )

    print("Generated:")
    print(f"  {REVIEW_DATASET_PATH}")
    print(f"  {FLOW_GRAPH_PATH}")
    print(f"  {FORMULA_OCR_INDEX_PATH}")
    if args.skip_locator:
        print(f"  {REVIEW_LOCATOR_INDEX_PATH} (reused; locator rebuild skipped)")
    else:
        print(f"  {REVIEW_LOCATOR_INDEX_PATH}")
    print(f"  {CHUNK_LINE_INDEX_PATH}")
    print(f"  {BUILD_TRACE_PATH}")


if __name__ == "__main__":
    main()
