"""Create tmp-only structured/textbook previews with figure placeholders."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from textbook_exporter import export_textbooks


CHUNK_FILE_RE = re.compile(r"^((?:chapter|appendix)\d+)_(\d+)\.json$", re.IGNORECASE)
FIGURE_REF_RE = re.compile(r"\bFigure(?:s)?\s+(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\b", re.IGNORECASE)
TEXT_ANCHOR_LABELS = {"abstract", "display_formula", "doc_title", "paragraph_title", "text"}
MIN_COORDINATE_ANCHOR_SCORE = 0.34
MAX_COORDINATE_ANCHORS_PER_BLOCK = 10
MAX_RAW_MATCH_CANDIDATES = 80
MAX_INDEX_TOKENS_PER_BLOCK = 48
MIN_RELIABLE_BLOCK_PAGE_SCORE = 0.85
NEAR_TEXT_REFERENCE_DISTANCE = 900.0


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(value))]


def clean_ref_id(value: Any) -> str:
    return str(value or "").strip().strip(".,;:()[]")


def base_figure_id(value: str, known_ids: set[str]) -> str:
    figure_id = clean_ref_id(value)
    if figure_id in known_ids:
        return figure_id
    match = re.fullmatch(r"((?:A\d+|\d+)\.\d+)[A-Za-z]", figure_id)
    if match and match.group(1) in known_ids:
        return match.group(1)
    return figure_id


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_asset_libraries(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in ("formula_library.json", "table_library.json", "example_library.json"):
        src = source / name
        if src.exists():
            shutil.copy2(src, target / name)
        else:
            write_json(target / name, {"formulas": [], "tables": [], "examples": []})


def repair_copied_formula_library_metadata(patch_dir: Path, records: list[dict[str, str]]) -> None:
    if not records:
        return
    formula_path = patch_dir / "formula_library.json"
    if not formula_path.exists():
        return
    try:
        payload = load_json(formula_path)
    except Exception:
        return
    formulas = payload.get("formulas") if isinstance(payload, dict) else []
    if not isinstance(formulas, list):
        return

    formula_headings: dict[str, str] = {}
    for chunk_path in sorted(patch_dir.glob("*.json"), key=natural_key):
        if not CHUNK_FILE_RE.fullmatch(chunk_path.name):
            continue
        try:
            chunk = load_json(chunk_path)
        except Exception:
            continue
        metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
        heading = str(metadata.get("display_heading") or metadata.get("section_level_2") or "").strip()
        if not heading:
            continue
        for formula_id in metadata.get("formula_references") or []:
            formula_headings.setdefault(clean_ref_id(formula_id), heading)
        for block in chunk.get("blocks") or []:
            if not isinstance(block, dict):
                continue
            for match in re.finditer(r"\[\[(?:SEE_)?FORMULA:(?P<id>[^\]]+)\]\]", str(block.get("content") or "")):
                formula_headings.setdefault(clean_ref_id(match.group("id")), heading)

    changed = False
    for formula in formulas:
        if not isinstance(formula, dict):
            continue
        source = formula.get("source") if isinstance(formula.get("source"), dict) else {}
        subsection = str(source.get("subsection") or "")
        if not matching_body_artifact_heading(subsection, records):
            continue
        formula_id = clean_ref_id(formula.get("id"))
        replacement = formula_headings.get(formula_id)
        if not replacement:
            continue
        source["subsection"] = replacement
        formula["source"] = source
        changed = True
    if changed:
        write_json(formula_path, payload)


def load_figure_library(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    figures = payload.get("figures") if isinstance(payload, dict) else {}
    if isinstance(figures, dict):
        return [item for item in figures.values() if isinstance(item, dict)]
    if isinstance(figures, list):
        return [item for item in figures if isinstance(item, dict)]
    return []


def load_example_reference_texts(structured_dir: Path) -> dict[tuple[str, str], str]:
    payload = load_json(structured_dir / "example_library.json") if (structured_dir / "example_library.json").exists() else {}
    examples = payload.get("examples") if isinstance(payload, dict) else []
    result: dict[tuple[str, str], str] = {}
    for example in examples if isinstance(examples, list) else []:
        if not isinstance(example, dict):
            continue
        chapter = str(example.get("chapter") or "").strip().lower()
        ref = clean_ref_id(example.get("example_ref") or example.get("example_id"))
        text = str(example.get("content_markdown") or example.get("content_plain") or "")
        if chapter and ref and text:
            result[(chapter, ref)] = text
    return result


def figure_ids_in_text(text: str, known_ids: set[str]) -> set[str]:
    found: set[str] = set()
    for match in FIGURE_REF_RE.finditer(text or ""):
        figure_id = base_figure_id(match.group("id"), known_ids)
        if figure_id in known_ids:
            found.add(figure_id)
        tail = text[match.end() : match.end() + 120]
        for candidate in known_ids:
            if candidate in found:
                continue
            if re.search(rf"(?:,|and)\s+{re.escape(candidate)}\b", tail, flags=re.IGNORECASE):
                found.add(candidate)
    return found


def normalize_body_artifact_text(value: str) -> str:
    value = re.sub(r"\\underline\{([^}]*)\}", r"\1", str(value or ""), flags=re.IGNORECASE)
    value = re.sub(r"\$+", " ", value)
    value = re.sub(r"\\[A-Za-z]+", " ", value)
    value = re.sub(r"[{}]", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", "", value).lower()
    return value


def body_artifact_records(figures: list[dict[str, Any]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for figure in figures:
        figure_id = clean_ref_id(figure.get("id"))
        body_blocks = figure.get("body_blocks") if isinstance(figure.get("body_blocks"), list) else []
        for block in body_blocks:
            if not isinstance(block, dict):
                continue
            label = str(block.get("label") or "").strip().lower()
            if label not in {"paragraph_title", "text"}:
                continue
            content = str(block.get("content") or "").strip()
            normalized = normalize_body_artifact_text(content)
            if len(normalized) < 12:
                continue
            records.append({"figure_id": figure_id, "text": content, "normalized": normalized})
    return records


def matching_body_artifact(value: str, records: list[dict[str, str]]) -> dict[str, str] | None:
    normalized = normalize_body_artifact_text(value)
    if len(normalized) < 12:
        return None
    for record in records:
        artifact = record["normalized"]
        if normalized in artifact or artifact in normalized:
            return record
        if difflib.SequenceMatcher(None, normalized, artifact).ratio() >= 0.9:
            return record
    return None


def matching_body_artifact_heading(value: str, records: list[dict[str, str]]) -> dict[str, str] | None:
    normalized = normalize_body_artifact_text(value)
    if len(normalized) < 6:
        return None
    for record in records:
        artifact = record["normalized"]
        if normalized in artifact and set(normalized) <= set("acgtu"):
            return record
    return None


def repair_body_artifact_metadata(
    chunk: dict[str, Any],
    previous_metadata: dict[str, Any] | None,
    records: list[dict[str, str]],
) -> bool:
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    if not metadata or not previous_metadata:
        return False
    display_heading = str(metadata.get("display_heading") or metadata.get("section_level_2") or "")
    if not matching_body_artifact_heading(display_heading, records):
        return False

    repaired = dict(metadata)
    for key in ("section", "section_level_1", "section_level_2", "display_heading"):
        if previous_metadata.get(key):
            repaired[key] = previous_metadata.get(key)
    previous_subsections = previous_metadata.get("subsections")
    if isinstance(previous_subsections, list):
        repaired["subsections"] = list(previous_subsections)
    previous_heading_path = previous_metadata.get("heading_path")
    if isinstance(previous_heading_path, list):
        repaired["heading_path"] = list(previous_heading_path)
    chunk["metadata"] = repaired
    return True


def replace_figure_references(text: str, known_ids: set[str]) -> str:
    if "[[FIGURE:" in text or "[[SEE_FIGURE:" in text:
        return text

    def replace_direct(match: re.Match[str]) -> str:
        figure_id = base_figure_id(match.group("id"), known_ids)
        if figure_id not in known_ids:
            return match.group(0)
        return f"[[SEE_FIGURE:{figure_id}]]"

    updated = FIGURE_REF_RE.sub(replace_direct, text)
    for figure_id in sorted(known_ids, key=lambda item: (-len(item), natural_key(item))):
        updated = re.sub(
            rf"(?P<prefix>\[\[SEE_FIGURE:[^\]]+\]\](?:\s*(?:,|and)\s*)+){re.escape(figure_id)}\b",
            lambda match, figure_id=figure_id: f"{match.group('prefix')}[[SEE_FIGURE:{figure_id}]]",
            updated,
            flags=re.IGNORECASE,
        )
    return updated


def chapter_files(structured_dir: Path, chapter: str) -> list[Path]:
    return sorted(
        [
            path
            for path in structured_dir.glob(f"{chapter}_*.json")
            if CHUNK_FILE_RE.fullmatch(path.name)
        ],
        key=lambda path: natural_key(path.name),
    )


def structured_chapters(structured_dir: Path) -> set[str]:
    chapters: set[str] = set()
    for path in structured_dir.glob("*_*.json"):
        match = CHUNK_FILE_RE.fullmatch(path.name)
        if match:
            chapters.add(match.group(1).lower())
    return chapters


def normalize_anchor_text(value: str) -> str:
    value = re.sub(r"\[\[(?:SEE_)?(?:FIGURE|FORMULA|TABLE|EXAMPLE):[^\]]+\]\]", " ", str(value or ""))
    value = re.sub(r"\$+", " ", value)
    value = re.sub(r"\\[A-Za-z]+", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value).lower()
    return re.sub(r"\s+", " ", value).strip()


def anchor_tokens(value: str) -> list[str]:
    return [token for token in normalize_anchor_text(value).split() if len(token) > 2]


def anchor_match_score(anchor: str, content: str) -> float:
    anchor_norm = normalize_anchor_text(anchor)
    content_norm = normalize_anchor_text(content)
    if not anchor_norm or not content_norm:
        return 0.0
    if anchor_norm in content_norm or content_norm in anchor_norm:
        return 1.0
    tokens = anchor_tokens(anchor_norm)
    if len(tokens) < 4:
        return 0.0
    content_tokens = set(anchor_tokens(content_norm))
    overlap = sum(1 for token in tokens[:28] if token in content_tokens)
    token_score = overlap / min(len(tokens[:28]), 28)
    fuzzy_score = difflib.SequenceMatcher(None, anchor_norm[:360], content_norm[:1200]).ratio()
    return max(token_score, fuzzy_score)


def row_text(row: dict[str, Any]) -> str:
    return str(row.get("block_content") or row.get("content") or row.get("text") or "").strip()


def row_bbox(row: dict[str, Any]) -> list[float] | None:
    bbox = row.get("block_bbox") or row.get("bbox")
    if not (isinstance(bbox, list) and len(bbox) >= 4):
        return None
    try:
        return [float(value) for value in bbox[:4]]
    except (TypeError, ValueError):
        return None


def raw_page_rows(raw_path: Path, page: int) -> list[dict[str, Any]]:
    try:
        payload = load_json(raw_path)
    except Exception:
        return []
    if not isinstance(payload, list) or page < 1 or page > len(payload):
        return []
    page_payload = payload[page - 1]
    if not isinstance(page_payload, dict):
        return []
    rows = page_payload.get("parsing_res_list")
    if not isinstance(rows, list):
        pruned = page_payload.get("prunedResult", {})
        rows = pruned.get("parsing_res_list") if isinstance(pruned, dict) else []
    rows = [row for row in rows or [] if isinstance(row, dict) and row_bbox(row)]
    return sorted(rows, key=lambda row: (row_bbox(row)[1], row_bbox(row)[0]))


def raw_pages(raw_path: Path) -> list[dict[str, Any]]:
    try:
        payload = load_json(raw_path)
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def text_anchor_rows(raw_path: Path, page: int) -> list[dict[str, Any]]:
    rows = raw_page_rows(raw_path, page)
    result: list[dict[str, Any]] = []
    for row in rows:
        label = str(row.get("block_label") or row.get("label") or "").strip().lower()
        if label not in TEXT_ANCHOR_LABELS:
            continue
        text = row_text(row)
        if len(anchor_tokens(text)) < 4:
            continue
        result.append(row)
    return result


def raw_anchor_rows(raw_path: Path) -> list[dict[str, Any]]:
    pages = raw_pages(raw_path)
    anchors: list[dict[str, Any]] = []
    for page_index, _ in enumerate(pages):
        page_number = page_index + 1
        for row in text_anchor_rows(raw_path, page_number):
            bbox = row_bbox(row)
            text = row_text(row)
            if not bbox or not text:
                continue
            anchors.append(
                {
                    "text": text,
                    "page": page_number,
                    "bbox": bbox,
                    "label": str(row.get("block_label") or row.get("label") or "").strip().lower(),
                }
            )
    return anchors


def raw_anchor_index(raw_rows: list[dict[str, Any]]) -> dict[str, Any]:
    postings: dict[str, set[int]] = defaultdict(set)
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(raw_rows):
        tokens = set(anchor_tokens(str(row.get("text") or "")))
        indexed = dict(row)
        indexed["_tokens"] = tokens
        rows.append(indexed)
        for token in tokens:
            postings[token].add(index)
    return {"rows": rows, "postings": postings}


def candidate_raw_rows(content: str, raw_index: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    if not raw_index:
        return None
    rows = raw_index.get("rows")
    postings = raw_index.get("postings")
    if not isinstance(rows, list) or not isinstance(postings, dict):
        return None
    token_counts = Counter(anchor_tokens(content))
    if not token_counts:
        return []
    scored: Counter[int] = Counter()
    for token, count in token_counts.most_common(MAX_INDEX_TOKENS_PER_BLOCK):
        for row_index in postings.get(token, set()):
            scored[row_index] += count
    if not scored:
        return []
    best_indices = [
        row_index
        for row_index, _ in scored.most_common(MAX_RAW_MATCH_CANDIDATES)
        if isinstance(row_index, int) and 0 <= row_index < len(rows)
    ]
    return [rows[row_index] for row_index in best_indices]


def figure_anchor_candidates(figure: dict[str, Any]) -> list[dict[str, Any]]:
    source = Path(str(figure.get("source_paddle_raw") or ""))
    page = int(figure.get("page") or 0)
    caption_block = figure.get("caption_block") if isinstance(figure.get("caption_block"), dict) else {}
    caption_bbox = caption_block.get("bbox") if isinstance(caption_block.get("bbox"), list) else None
    body_bbox = figure.get("raw_bbox") if isinstance(figure.get("raw_bbox"), list) else None
    if not source.exists() or not caption_bbox:
        return []

    zone_boxes = [caption_bbox]
    if body_bbox:
        zone_boxes.append(body_bbox)
    zone_top = min(float(bbox[1]) for bbox in zone_boxes)
    zone_bottom = max(float(bbox[3]) for bbox in zone_boxes)

    candidates: list[dict[str, Any]] = []
    for row in text_anchor_rows(source, page):
        bbox = row_bbox(row)
        if not bbox:
            continue
        text = row_text(row)
        if bbox[1] >= zone_bottom:
            candidates.append(
                {
                    "text": text,
                    "page": page,
                    "bbox": bbox,
                    "label": str(row.get("block_label") or row.get("label") or "").strip().lower(),
                    "side": "before",
                    "distance": bbox[1] - zone_bottom,
                    "source": "same_page_after_figure",
                }
            )
        elif bbox[3] <= zone_top:
            candidates.append(
                {
                    "text": text,
                    "page": page,
                    "bbox": bbox,
                    "label": str(row.get("block_label") or row.get("label") or "").strip().lower(),
                    "side": "after",
                    "distance": zone_top - bbox[3],
                    "source": "same_page_before_figure",
                }
            )

    pages = raw_pages(source)
    page_gap = 2000.0
    if page > 1:
        previous_rows = text_anchor_rows(source, page - 1)
        if previous_rows:
            row = previous_rows[-1]
            bbox = row_bbox(row)
            if bbox:
                candidates.append(
                    {
                        "text": row_text(row),
                        "page": page - 1,
                        "bbox": bbox,
                        "label": str(row.get("block_label") or row.get("label") or "").strip().lower(),
                        "side": "after",
                        "distance": page_gap + bbox[3],
                        "source": "previous_page_before_figure",
                    }
                )
    if page < len(pages):
        next_rows = text_anchor_rows(source, page + 1)
        if next_rows:
            row = next_rows[0]
            bbox = row_bbox(row)
            if bbox:
                candidates.append(
                    {
                        "text": row_text(row),
                        "page": page + 1,
                        "bbox": bbox,
                        "label": str(row.get("block_label") or row.get("label") or "").strip().lower(),
                        "side": "before",
                        "distance": page_gap + bbox[1],
                        "source": "next_page_after_figure",
                    }
                )

    return sorted(candidates, key=lambda item: (float(item["distance"]), item["page"]))


def best_anchor_position(
    figure: dict[str, Any],
    chunk_payloads: list[tuple[Path, dict[str, Any]]],
    already_placed: set[str],
    block_coordinate_lookup: dict[tuple[str, int], list[dict[str, Any]]] | None = None,
) -> dict[str, Any] | None:
    figure_id = clean_ref_id(figure.get("id"))
    if figure_id in already_placed:
        return None
    candidates = figure_anchor_candidates(figure)
    best: dict[str, Any] | None = None
    for _, chunk in chunk_payloads:
        chunk_id = str(chunk.get("id") or "")
        for candidate in candidates:
            if str(candidate.get("label") or "") != "paragraph_title":
                continue
            score = metadata_anchor_match_score(str(candidate.get("text") or ""), chunk)
            if score < 0.86:
                continue
            block_coordinates = (block_coordinate_lookup or {}).get((chunk_id, 0), [])
            reliable_coordinates = [
                anchor for anchor in block_coordinates
                if float(anchor.get("score") or 0.0) >= MIN_RELIABLE_BLOCK_PAGE_SCORE
            ]
            if reliable_coordinates:
                nearest_page_gap = min(
                    abs(int(anchor.get("page") or 0) - int(candidate.get("page") or 0))
                    for anchor in reliable_coordinates
                )
                if nearest_page_gap > 1:
                    continue
            combined = score + 0.2 - min(float(candidate.get("distance") or 0.0), 4000.0) / 10000.0
            if best is None or combined > float(best["combined"]):
                best = {
                    "chunk": chunk_id,
                    "block_index": 0,
                    "side": "before",
                    "method": "caption_heading_metadata",
                    "score": score,
                    "distance": float(candidate["distance"]),
                    "raw_page": candidate["page"],
                    "raw_bbox": candidate["bbox"],
                    "anchor_source": candidate["source"],
                    "combined": combined,
                }

        blocks = chunk.get("blocks") if isinstance(chunk.get("blocks"), list) else []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            for candidate in candidates:
                if str(candidate.get("label") or "") == "paragraph_title":
                    continue
                block_coordinates = (block_coordinate_lookup or {}).get((str(chunk.get("id") or ""), block_index), [])
                reliable_coordinates = [
                    anchor for anchor in block_coordinates
                    if float(anchor.get("score") or 0.0) >= MIN_RELIABLE_BLOCK_PAGE_SCORE
                ]
                if reliable_coordinates:
                    nearest_page_gap = min(
                        abs(int(anchor.get("page") or 0) - int(candidate.get("page") or 0))
                        for anchor in reliable_coordinates
                    )
                    if nearest_page_gap > 1:
                        continue
                score = anchor_match_score(str(candidate.get("text") or ""), content)
                if score < 0.42:
                    continue
                combined = score - min(float(candidate.get("distance") or 0.0), 2000.0) / 10000.0
                if best is None or combined > float(best["combined"]):
                    best = {
                        "chunk": str(chunk.get("id") or ""),
                        "block_index": block_index,
                        "side": candidate["side"],
                        "method": "caption_neighbor_anchor",
                        "score": score,
                        "distance": float(candidate["distance"]),
                        "raw_page": candidate["page"],
                        "raw_bbox": candidate["bbox"],
                        "anchor_source": candidate["source"],
                        "combined": combined,
                    }
    return best


def metadata_anchor_match_score(anchor: str, chunk: dict[str, Any]) -> float:
    metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
    values: list[str] = []
    for key in ("display_heading", "section", "section_level_1", "section_level_2"):
        values.append(str(metadata.get(key) or ""))
    for key in ("heading_path", "subsections"):
        items = metadata.get(key)
        if isinstance(items, list):
            values.extend(str(item) for item in items)
    return max((heading_anchor_score(anchor, value) for value in values), default=0.0)


def heading_anchor_score(anchor: str, value: str) -> float:
    anchor_norm = normalize_anchor_text(anchor)
    value_norm = normalize_anchor_text(value)
    if not anchor_norm or not value_norm:
        return 0.0
    if anchor_norm == value_norm:
        return 1.0
    if anchor_norm in value_norm or value_norm in anchor_norm:
        return 0.92
    return difflib.SequenceMatcher(None, anchor_norm, value_norm).ratio()


def best_raw_match_for_block(content: str, raw_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = raw_matches_for_block(content, raw_rows, limit=1)
    return matches[0] if matches else None


def raw_matches_for_block(
    content: str,
    raw_rows: list[dict[str, Any]],
    *,
    limit: int = MAX_COORDINATE_ANCHORS_PER_BLOCK,
    raw_index: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not anchor_tokens(content):
        return []
    matches: list[dict[str, Any]] = []
    candidates = candidate_raw_rows(content, raw_index)
    scan_rows = candidates if candidates is not None else raw_rows
    for row in scan_rows:
        score = anchor_match_score(str(row.get("text") or ""), content)
        if score < MIN_COORDINATE_ANCHOR_SCORE:
            continue
        matches.append(
            {
                "page": int(row["page"]),
                "bbox": row["bbox"],
                "score": score,
                "label": row.get("label"),
            }
        )
    return sorted(
        matches,
        key=lambda item: (-float(item["score"]), int(item["page"]), item["bbox"][1], item["bbox"][0]),
    )[:limit]


def build_structured_coordinate_index(
    figures: dict[str, dict[str, Any]],
    chunk_payloads: list[tuple[Path, dict[str, Any]]],
) -> list[dict[str, Any]]:
    raw_paths = {
        Path(str(figure.get("source_paddle_raw") or ""))
        for figure in figures.values()
        if str(figure.get("source_paddle_raw") or "")
    }
    raw_rows: list[dict[str, Any]] = []
    for raw_path in sorted(raw_paths, key=lambda item: str(item)):
        if raw_path.exists():
            raw_rows.extend(raw_anchor_rows(raw_path))
    if not raw_rows:
        return []
    raw_index = raw_anchor_index(raw_rows)

    anchors: list[dict[str, Any]] = []
    for _, chunk in chunk_payloads:
        blocks = chunk.get("blocks") if isinstance(chunk.get("blocks"), list) else []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            matches = raw_matches_for_block(content, raw_rows, raw_index=raw_index)
            if not matches:
                continue
            for match in matches:
                anchors.append(
                    {
                        "chunk": str(chunk.get("id") or ""),
                        "block_index": block_index,
                        "page": match["page"],
                        "bbox": match["bbox"],
                        "score": match["score"],
                        "label": match.get("label"),
                    }
                )
    return anchors


def block_coordinate_lookup(block_anchors: list[dict[str, Any]]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    lookup: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for anchor in block_anchors:
        try:
            block_index = int(anchor.get("block_index"))
        except (TypeError, ValueError):
            continue
        lookup[(str(anchor.get("chunk") or ""), block_index)].append(anchor)
    return lookup


def bbox_gap(
    *,
    figure_page: int,
    figure_bbox: list[float],
    block_page: int,
    block_bbox: list[float],
) -> tuple[float, str]:
    page_gap = 2000.0
    if block_page < figure_page:
        return (
            (figure_page - block_page) * page_gap
            - float(block_bbox[3])
            + float(figure_bbox[1])
        ), "after"
    if block_page > figure_page:
        return (
            (block_page - figure_page) * page_gap
            + float(block_bbox[1])
            - float(figure_bbox[3])
        ), "before"

    figure_top = float(figure_bbox[1])
    figure_bottom = float(figure_bbox[3])
    block_top = float(block_bbox[1])
    block_bottom = float(block_bbox[3])
    if block_top >= figure_bottom:
        return block_top - figure_bottom, "before"
    if block_bottom <= figure_top:
        return figure_top - block_bottom, "after"

    figure_mid = (figure_top + figure_bottom) / 2.0
    block_mid = (block_top + block_bottom) / 2.0
    return 0.0, "before" if block_mid >= figure_mid else "after"


def coordinate_nearest_positions(
    figures: dict[str, dict[str, Any]],
    chunk_payloads: list[tuple[Path, dict[str, Any]]],
    block_anchors: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    if block_anchors is None:
        block_anchors = build_structured_coordinate_index(figures, chunk_payloads)
    positions: dict[str, dict[str, Any]] = {}
    if not block_anchors:
        return positions

    for figure_id, figure in figures.items():
        raw_bbox = figure.get("raw_bbox")
        figure_page = int(figure.get("page") or 0)
        if not (isinstance(raw_bbox, list) and len(raw_bbox) >= 4 and figure_page > 0):
            continue
        best: dict[str, Any] | None = None
        for block_anchor in block_anchors:
            distance, side = bbox_gap(
                figure_page=figure_page,
                figure_bbox=[float(value) for value in raw_bbox[:4]],
                block_page=int(block_anchor["page"]),
                block_bbox=[float(value) for value in block_anchor["bbox"][:4]],
            )
            combined = distance - float(block_anchor["score"]) * 10.0
            if best is None or combined < float(best["combined"]):
                best = {
                    "chunk": block_anchor["chunk"],
                    "block_index": block_anchor["block_index"],
                    "side": side,
                    "method": "raw_layout_nearest_block",
                    "distance": distance,
                    "block_page": block_anchor["page"],
                    "block_bbox": block_anchor["bbox"],
                    "block_match_score": block_anchor["score"],
                    "figure_page": figure_page,
                    "figure_bbox": raw_bbox,
                    "combined": combined,
                }
        if best:
            positions[figure_id] = best
    return positions


def fallback_text_reference_positions(
    known_ids: set[str],
    chunk_payloads: list[tuple[Path, dict[str, Any]]],
    example_texts: dict[tuple[str, str], str] | None = None,
    figures: dict[str, dict[str, Any]] | None = None,
    block_coordinate_lookup: dict[tuple[str, int], list[dict[str, Any]]] | None = None,
) -> dict[str, dict[str, Any]]:
    positions: dict[str, dict[str, Any]] = {}
    for _, chunk in chunk_payloads:
        chapter = str((chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}).get("chapter") or "").strip().lower()
        chunk_id = str(chunk.get("id") or "")
        blocks = chunk.get("blocks") if isinstance(chunk.get("blocks"), list) else []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            texts = [content]
            for match in re.finditer(r"\[\[SEE_EXAMPLE:(?P<id>[^\]]+)\]\]", content, flags=re.IGNORECASE):
                example_text = (example_texts or {}).get((chapter, clean_ref_id(match.group("id"))))
                if example_text:
                    texts.append(example_text)
            mentioned: set[str] = set()
            for text in texts:
                mentioned.update(figure_ids_in_text(text, known_ids))
            for figure_id in sorted(mentioned, key=natural_key):
                position = text_reference_position(
                    figure_id=figure_id,
                    chunk_id=chunk_id,
                    block_index=block_index,
                    figures=figures or {},
                    block_coordinates=(block_coordinate_lookup or {}).get((chunk_id, block_index), []),
                )
                current = positions.get(figure_id)
                if current is None or is_better_position(position, current):
                    positions[figure_id] = position
    return positions


def text_reference_position(
    *,
    figure_id: str,
    chunk_id: str,
    block_index: int,
    figures: dict[str, dict[str, Any]],
    block_coordinates: list[dict[str, Any]],
) -> dict[str, Any]:
    position = {
        "chunk": chunk_id,
        "block_index": block_index,
        "side": "after",
        "method": "text_reference_fallback",
    }
    figure = figures.get(figure_id)
    raw_bbox = figure.get("raw_bbox") if isinstance(figure, dict) else None
    figure_page = int(figure.get("page") or 0) if isinstance(figure, dict) else 0
    if not (isinstance(raw_bbox, list) and len(raw_bbox) >= 4 and figure_page > 0):
        return position

    best_distance: float | None = None
    best_side = "after"
    for anchor in block_coordinates:
        if float(anchor.get("score") or 0.0) < MIN_RELIABLE_BLOCK_PAGE_SCORE:
            continue
        distance, side = bbox_gap(
            figure_page=figure_page,
            figure_bbox=[float(value) for value in raw_bbox[:4]],
            block_page=int(anchor.get("page") or 0),
            block_bbox=[float(value) for value in anchor.get("bbox")[:4]],
        )
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_side = side

    if best_distance is None:
        return position
    position["distance"] = best_distance
    position["side"] = best_side
    if best_distance <= NEAR_TEXT_REFERENCE_DISTANCE:
        position["method"] = "near_text_reference"
    return position


def position_block_index(position: dict[str, Any]) -> int:
    value = position.get("block_index")
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def position_distance(position: dict[str, Any]) -> float:
    value = position.get("distance")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def position_priority(position: dict[str, Any]) -> int:
    method = str(position.get("method") or "raw_layout_coordinate")
    priorities = {
        "near_text_reference": 7,
        "caption_heading_metadata": 6,
        "caption_neighbor_anchor": 5,
        "text_reference_fallback": 2,
        "raw_layout_nearest_block": 3,
        "raw_layout_coordinate": 2,
    }
    return priorities.get(method, 0)


def is_better_position(candidate: dict[str, Any], current: dict[str, Any]) -> bool:
    candidate_priority = position_priority(candidate)
    current_priority = position_priority(current)
    if candidate_priority >= 5 and current_priority < candidate_priority:
        return True
    if current_priority >= 5 and candidate_priority < current_priority:
        return False
    if candidate_priority >= 4 and candidate_priority > current_priority:
        return True
    if current_priority >= 4 and current_priority > candidate_priority:
        return False
    candidate_distance = position_distance(candidate)
    current_distance = position_distance(current)
    if candidate_distance + 150.0 < current_distance:
        return True
    if current_distance + 150.0 < candidate_distance:
        return False
    return candidate_priority > current_priority


def set_best_position(
    positions: dict[str, dict[str, Any]],
    figure_id: str,
    candidate: dict[str, Any] | None,
) -> None:
    if not candidate:
        return
    current = positions.get(figure_id)
    if current is None or is_better_position(candidate, current):
        positions[figure_id] = candidate


def patch_chapter(
    *,
    chapter: str,
    figures: list[dict[str, Any]],
    structured_dir: Path,
    out_dir: Path,
    example_texts: dict[tuple[str, str], str] | None = None,
) -> dict[str, Any]:
    known_ids = {clean_ref_id(item.get("id")) for item in figures if clean_ref_id(item.get("id"))}
    placed: set[str] = set()
    referenced: set[str] = set()
    audit: dict[str, Any] = {
        "chapter": chapter,
        "figures": sorted(known_ids, key=natural_key),
        "placed": [],
        "unplaced": [],
        "placement_methods": {},
        "references": defaultdict(list),
    }

    files = chapter_files(structured_dir, chapter)
    chunk_payloads = [(path, load_json(path)) for path in files]
    if not known_ids:
        for path, chunk in chunk_payloads:
            write_json(out_dir / path.name, chunk)
        audit["placement_methods"] = {}
        audit["references"] = {}
        return audit

    figure_by_id = {clean_ref_id(item.get("id")): item for item in figures if clean_ref_id(item.get("id"))}
    artifact_records = body_artifact_records(figures)
    anchor_positions: dict[str, dict[str, Any]] = {}
    block_anchors = build_structured_coordinate_index(figure_by_id, chunk_payloads)
    coordinate_lookup = block_coordinate_lookup(block_anchors)
    for figure_id, position in coordinate_nearest_positions(figure_by_id, chunk_payloads, block_anchors).items():
        set_best_position(anchor_positions, figure_id, position)
    for figure_id, figure in figure_by_id.items():
        match = best_anchor_position(figure, chunk_payloads, placed, coordinate_lookup)
        set_best_position(anchor_positions, figure_id, match)
    fallback_positions = fallback_text_reference_positions(
        known_ids,
        chunk_payloads,
        example_texts,
        figures=figure_by_id,
        block_coordinate_lookup=coordinate_lookup,
    )
    for figure_id, position in fallback_positions.items():
        set_best_position(anchor_positions, figure_id, position)

    for path in files:
        chunk = next(payload for candidate_path, payload in chunk_payloads if candidate_path == path)
        path_index = next(index for index, (candidate_path, _) in enumerate(chunk_payloads) if candidate_path == path)
        previous_metadata = None
        if path_index > 0:
            previous_chunk = chunk_payloads[path_index - 1][1]
            previous_metadata = (
                previous_chunk.get("metadata") if isinstance(previous_chunk.get("metadata"), dict) else None
            )
        repair_body_artifact_metadata(chunk, previous_metadata, artifact_records)
        blocks = chunk.get("blocks") if isinstance(chunk.get("blocks"), list) else []
        new_blocks: list[dict[str, Any]] = []
        for block_index, block in enumerate(blocks):
            if not isinstance(block, dict):
                new_blocks.append(block)
                continue
            content = str(block.get("content") or "")
            artifact_match = matching_body_artifact(content, artifact_records)
            if artifact_match:
                audit.setdefault("removed_body_artifact_blocks", []).append(
                    {
                        "figure_id": artifact_match["figure_id"],
                        "chunk": chunk.get("id"),
                        "block_index": block_index,
                    }
                )
                continue
            mentioned = figure_ids_in_text(content, known_ids)
            referenced.update(mentioned)
            for figure_id in mentioned:
                audit["references"][figure_id].append(
                    {"chunk": chunk.get("id"), "block_index": block_index}
                )
            patched = dict(block)
            patched["content"] = replace_figure_references(content, known_ids)
            for figure_id, position in sorted(anchor_positions.items(), key=lambda item: natural_key(item[0])):
                if (
                    figure_id in placed
                    or str(position.get("chunk") or "") != str(chunk.get("id") or "")
                    or position_block_index(position) != block_index
                    or position.get("side") != "before"
                ):
                    continue
                new_blocks.append({"type": "figure", "content": f"[[FIGURE:{figure_id}]]"})
                placed.add(figure_id)
                placement = {
                    "figure_id": figure_id,
                    "chunk": chunk.get("id"),
                    "before_block": block_index,
                    "method": position.get("method", "raw_layout_coordinate"),
                }
                if "score" in position:
                    placement["score"] = round(float(position["score"]), 3)
                if "distance" in position:
                    placement["distance"] = round(float(position["distance"]), 2)
                if "anchor_source" in position:
                    placement["anchor_source"] = position["anchor_source"]
                audit["placed"].append(placement)
            new_blocks.append(patched)
            for figure_id, position in sorted(anchor_positions.items(), key=lambda item: natural_key(item[0])):
                if (
                    figure_id in placed
                    or str(position.get("chunk") or "") != str(chunk.get("id") or "")
                    or position_block_index(position) != block_index
                    or position.get("side") != "after"
                ):
                    continue
                new_blocks.append({"type": "figure", "content": f"[[FIGURE:{figure_id}]]"})
                placed.add(figure_id)
                placement = {
                    "figure_id": figure_id,
                    "chunk": chunk.get("id"),
                    "after_block": block_index,
                    "method": position.get("method", "raw_layout_coordinate"),
                }
                if "score" in position:
                    placement["score"] = round(float(position["score"]), 3)
                if "distance" in position:
                    placement["distance"] = round(float(position["distance"]), 2)
                if "anchor_source" in position:
                    placement["anchor_source"] = position["anchor_source"]
                audit["placed"].append(placement)
        chunk["blocks"] = new_blocks
        write_json(out_dir / path.name, chunk)

    for figure_id in sorted(known_ids - placed, key=natural_key):
        audit["unplaced"].append(figure_id)
    method_counts: dict[str, int] = defaultdict(int)
    for placement in audit["placed"]:
        method_counts[str(placement.get("method") or "unknown")] += 1
    audit["placement_methods"] = dict(sorted(method_counts.items()))
    audit["references"] = dict(audit["references"])
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tmp-only figure relink preview builder.")
    parser.add_argument("--structured-dir", type=Path, default=ROOT / "data" / "structured")
    parser.add_argument("--figure-root", type=Path, default=ROOT / "tmp" / "figure_relink_probe")
    parser.add_argument("--chapters", default="", help="Comma-separated chapter ids. Defaults to all structured chapters.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    structured_dir = args.structured_dir.resolve()
    figure_root = args.figure_root.resolve()
    figure_library = figure_root / "figure_library.json"
    figures = load_figure_library(figure_library)
    figures_by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for figure in figures:
        chapter = str(figure.get("chapter") or "").strip().lower()
        if chapter:
            figures_by_chapter[chapter].append(figure)

    requested = {item.strip().lower() for item in args.chapters.split(",") if item.strip()}
    chapters = sorted(requested or structured_chapters(structured_dir), key=natural_key)
    patch_dir = figure_root / "structured_patch_preview"
    textbook_dir = figure_root / "textbook_preview"
    example_texts = load_example_reference_texts(structured_dir)
    copy_asset_libraries(structured_dir, patch_dir)
    artifact_records = body_artifact_records(figures)

    audits = []
    for chapter in chapters:
        audits.append(
            patch_chapter(
                chapter=chapter,
                figures=figures_by_chapter.get(chapter, []),
                structured_dir=structured_dir,
                out_dir=patch_dir,
                example_texts=example_texts,
            )
        )

    repair_copied_formula_library_metadata(patch_dir, artifact_records)
    export_textbooks(
        structured_dir=patch_dir,
        out_dir=textbook_dir,
        chapters=set(chapters),
        figure_library=figure_library,
    )
    write_json(figure_root / "preview_audit.json", {"chapters": audits})
    write_json(
        figure_root / "preview_source_policy.json",
        {
            "source_of_truth": "Original PDFs in data background-materials directory plus Paddle raw layout.",
            "structured_dir_role": "Read-only preview scaffold; may be incomplete or stale.",
            "textbook_role": "Generated tmp preview only; formal data/textbook is not written.",
        },
    )

    print(f"structured_patch_preview={patch_dir}")
    print(f"textbook_preview={textbook_dir}")
    for audit in audits:
        print(
            f"{audit['chapter']}: figures={len(audit['figures'])} "
            f"placed={len(audit['placed'])} unplaced={len(audit['unplaced'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
