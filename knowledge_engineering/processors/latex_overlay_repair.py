"""Repair damaged inline LaTeX by overlaying only math fragments.

This module deliberately preserves structured prose, block order, chunking,
and structural placeholders. It uses a fresh structured output as the primary
source and only copies better LaTeX fragments into already-aligned text.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

from knowledge_engineering.core.common import read_json, utc_now_iso, write_json

INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_TABLE|TABLE|SEE_FORMULA|FORMULA):[^\]]+\]\]")
TABLE_CELL_RE = re.compile(r"(<t[dh]\b[^>]*>)(.*?)(</t[dh]>)", re.IGNORECASE | re.DOTALL)

AUTO_CONFIDENCE = 0.98
EXACT_BLOCK_SIMILARITY = 0.78
FALLBACK_BLOCK_SIMILARITY = 0.92


@dataclass(frozen=True)
class MathSpan:
    start: int
    end: int
    inner: str
    full: str


def iter_unit_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.glob("*.json")):
        if path.name in {"formula_library.json", "table_library.json"}:
            continue
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("blocks"), list):
            yield path


def placeholder_counter(text: str) -> Counter[str]:
    return Counter(match.group(0) for match in PLACEHOLDER_RE.finditer(text or ""))


def inline_math_spans(text: str) -> list[MathSpan]:
    return [
        MathSpan(match.start(), match.end(), match.group(1), match.group(0))
        for match in INLINE_MATH_RE.finditer(text or "")
    ]


def text_without_inline_math(text: str) -> str:
    return INLINE_MATH_RE.sub(" $MATH$ ", text or "")


def normalize_for_similarity(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = PLACEHOLDER_RE.sub(" PLACEHOLDER ", value)
    value = text_without_inline_math(value)
    value = re.sub(r"\\[A-Za-z]+", " LATEXCMD ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def similarity(left: str, right: str) -> float:
    left_norm = normalize_for_similarity(left)
    right_norm = normalize_for_similarity(right)
    if not left_norm and not right_norm:
        return 1.0
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def math_damage_reasons(value: str) -> list[str]:
    text = str(value or "")
    stripped = text.strip()
    reasons: list[str] = []
    if not stripped:
        reasons.append("empty_math")
    if re.search(r"(^|[^A-Za-z0-9})\]])[_^]\s*[A-Za-z0-9]?", text):
        reasons.append("detached_script")
    if re.search(r"[A-Za-z0-9})\]]\s*[_^]\s+[A-Za-z0-9\\]", text):
        reasons.append("spaced_script")
    if re.search(r"/\s*$", stripped):
        reasons.append("missing_denominator")
    if re.search(r"=\s*'\s*-\s*(?:$|[,.;])", text):
        reasons.append("missing_overline_operand")
    if re.search(r"\(\s*[^)]*-\s*_[A-Za-z0-9]", text):
        reasons.append("missing_left_operand")
    if stripped in {"_", "^", "_ i", "_i", "^ i", "^i"}:
        reasons.append("bare_script")
    return sorted(set(reasons))


def has_better_latex_signal(candidate: str) -> bool:
    return bool(re.search(r"\\[A-Za-z]+|\{[^}]+\}|_[{A-Za-z0-9]|\\prime", candidate or ""))


def math_token_similarity(left: str, right: str) -> float:
    def norm(value: str) -> str:
        value = str(value or "")
        value = re.sub(r"\\[A-Za-z]+", "CMD", value)
        value = re.sub(r"[^0-9A-Za-z]+", " ", value)
        return re.sub(r"\s+", " ", value).strip().lower()

    left_norm = norm(left)
    right_norm = norm(right)
    if not left_norm and not right_norm:
        return 1.0
    if not left_norm or not right_norm:
        return 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio()


def source_math_is_better(target_math: str, source_math: str) -> tuple[bool, list[str]]:
    old_reasons = math_damage_reasons(target_math)
    if not old_reasons:
        return False, []
    new_reasons = math_damage_reasons(source_math)
    if new_reasons:
        return False, []
    if not has_better_latex_signal(source_math):
        return False, []
    if math_token_similarity(target_math, source_math) < 0.20:
        return False, []
    return True, old_reasons


def overlay_inline_math_text(target: str, source: str) -> tuple[str, list[dict[str, Any]], str]:
    target_spans = inline_math_spans(target)
    source_spans = inline_math_spans(source)
    if not target_spans:
        return target, [], "no inline math"
    if len(target_spans) != len(source_spans):
        return target, [], f"inline math count mismatch ({len(target_spans)} != {len(source_spans)})"

    replacements: list[dict[str, Any]] = []
    pieces: list[str] = []
    cursor = 0
    for index, (old_span, new_span) in enumerate(zip(target_spans, source_spans)):
        should_replace, reasons = source_math_is_better(old_span.inner, new_span.inner)
        pieces.append(target[cursor : old_span.start])
        if should_replace:
            pieces.append(new_span.full)
            replacements.append(
                {
                    "index": index,
                    "old_math": old_span.inner,
                    "new_math": new_span.inner,
                    "reasons": reasons,
                }
            )
        else:
            pieces.append(old_span.full)
        cursor = old_span.end
    pieces.append(target[cursor:])
    if not replacements:
        return target, [], "no damaged math replaced"
    return "".join(pieces), replacements, ""


def changed_math_summary(replacements: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    return (
        [str(item.get("old_math") or "") for item in replacements],
        [str(item.get("new_math") or "") for item in replacements],
    )


def block_placeholders_match(target: str, source: str) -> bool:
    return placeholder_counter(target) == placeholder_counter(source)


def load_source_units(source_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    units: dict[str, dict[str, Any]] = {}
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in iter_unit_files(source_dir):
        data = read_json(path)
        unit_id = str(data.get("id") or path.stem)
        units[unit_id] = data
        chapter = str((data.get("metadata") or {}).get("chapter") or "").strip().lower()
        if chapter:
            by_chapter[chapter].append(data)
    return units, dict(by_chapter)


def source_block_at(source_unit: dict[str, Any] | None, block_index: int) -> dict[str, Any] | None:
    if not source_unit:
        return None
    blocks = source_unit.get("blocks")
    if not isinstance(blocks, list) or block_index >= len(blocks):
        return None
    block = blocks[block_index]
    return block if isinstance(block, dict) else None


def find_fallback_block(
    *,
    target_block: dict[str, Any],
    target_content: str,
    source_units_for_chapter: list[dict[str, Any]],
    min_similarity: float,
) -> tuple[dict[str, Any] | None, float, str]:
    best_block: dict[str, Any] | None = None
    best_score = 0.0
    best_unit_id = ""
    target_type = str(target_block.get("type") or "")
    target_placeholders = placeholder_counter(target_content)
    target_math_count = len(inline_math_spans(target_content))
    for source_unit in source_units_for_chapter:
        unit_id = str(source_unit.get("id") or "")
        for source_block in source_unit.get("blocks", []) if isinstance(source_unit.get("blocks"), list) else []:
            if not isinstance(source_block, dict):
                continue
            if str(source_block.get("type") or "") != target_type:
                continue
            source_content = str(source_block.get("content") or "")
            if placeholder_counter(source_content) != target_placeholders:
                continue
            if len(inline_math_spans(source_content)) != target_math_count:
                continue
            score = similarity(target_content, source_content)
            if score > best_score:
                best_score = score
                best_block = source_block
                best_unit_id = unit_id
    if best_score < min_similarity:
        return None, best_score, best_unit_id
    return best_block, best_score, best_unit_id


def build_block_overlay_item(
    *,
    unit_id: str,
    block_index: int,
    target_block: dict[str, Any],
    source_block: dict[str, Any],
    source_unit_id: str,
    source_mode: str,
    min_similarity: float,
) -> dict[str, Any] | None:
    old_content = str(target_block.get("content") or "")
    source_content = str(source_block.get("content") or "")
    if str(target_block.get("type") or "") != str(source_block.get("type") or ""):
        return None
    if not block_placeholders_match(old_content, source_content):
        return None
    score = similarity(old_content, source_content)
    if score < min_similarity:
        return None
    new_content, replacements, reject_reason = overlay_inline_math_text(old_content, source_content)
    if not replacements or new_content == old_content:
        return None

    old_math, new_math = changed_math_summary(replacements)
    exact = source_mode == "same_unit_block"
    return {
        "kind": "block",
        "unit_id": unit_id,
        "block_index": block_index,
        "field": "blocks[].content",
        "status": "accepted" if exact else "needs_review",
        "action": "auto_apply" if exact else "review",
        "confidence": AUTO_CONFIDENCE if exact else round(score, 4),
        "old_content": old_content,
        "new_content": new_content,
        "old_math": old_math,
        "new_math": new_math,
        "replacements": replacements,
        "source": {
            "mode": source_mode,
            "unit_id": source_unit_id,
            "block_index": block_index if exact else None,
        },
        "reasons": [
            f"overlay inline LaTeX only from {source_mode}",
            f"text similarity {score:.2f}",
            reject_reason,
        ]
        if reject_reason
        else [f"overlay inline LaTeX only from {source_mode}", f"text similarity {score:.2f}"],
    }


def damaged_inline_math_values(content: str) -> list[str]:
    return [
        span.inner
        for span in inline_math_spans(content)
        if math_damage_reasons(span.inner)
    ]


def inline_math_values(content: str) -> list[str]:
    return [span.inner for span in inline_math_spans(content)]


def diagnose_block_candidate(
    *,
    target_block: dict[str, Any],
    source_block: dict[str, Any],
    min_similarity: float,
) -> tuple[list[str], float]:
    old_content = str(target_block.get("content") or "")
    source_content = str(source_block.get("content") or "")
    score = similarity(old_content, source_content)
    reasons: list[str] = []
    if str(target_block.get("type") or "") != str(source_block.get("type") or ""):
        reasons.append("block type mismatch")
    if not block_placeholders_match(old_content, source_content):
        reasons.append("placeholder set changed")
    if score < min_similarity:
        reasons.append(f"text similarity {score:.2f} below {min_similarity:.2f}")
    target_spans = inline_math_spans(old_content)
    source_spans = inline_math_spans(source_content)
    if len(target_spans) != len(source_spans):
        reasons.append(f"inline math count mismatch ({len(target_spans)} != {len(source_spans)})")
    if not reasons:
        _new_content, replacements, reject_reason = overlay_inline_math_text(old_content, source_content)
        if not replacements:
            reasons.append(reject_reason or "no damaged math replaced")
    return reasons or ["candidate rejected by safety guard"], score


def build_rejected_block_item(
    *,
    unit_id: str,
    block_index: int,
    target_block: dict[str, Any],
    source_block: dict[str, Any] | None,
    source_unit_id: str,
    source_mode: str,
    confidence: float,
    reasons: list[str],
) -> dict[str, Any]:
    old_content = str(target_block.get("content") or "")
    source_content = str(source_block.get("content") or "") if source_block else ""
    return {
        "kind": "block",
        "unit_id": unit_id,
        "block_index": block_index,
        "field": "blocks[].content",
        "status": "rejected",
        "action": "no_apply",
        "confidence": round(confidence, 4),
        "old_content": old_content,
        "new_content": old_content,
        "old_math": damaged_inline_math_values(old_content),
        "new_math": inline_math_values(source_content),
        "replacements": [],
        "source": {
            "mode": source_mode,
            "unit_id": source_unit_id,
            "block_index": block_index if source_mode == "same_unit_block" else None,
        },
        "reasons": reasons,
    }


def same_shape_rows(left: Any, right: Any) -> bool:
    if not isinstance(left, list) or not isinstance(right, list) or len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if not isinstance(left_row, list) or not isinstance(right_row, list):
            return False
        if len(left_row) != len(right_row):
            return False
    return True


def replace_formula_cell_if_safe(target: str, source: str) -> tuple[str, list[dict[str, Any]]]:
    new_text, replacements, _reason = overlay_inline_math_text(target, source)
    if replacements:
        return new_text, replacements

    old_reasons = math_damage_reasons(target)
    if not old_reasons or math_damage_reasons(source):
        return target, []
    if not looks_like_standalone_formula_fragment(target) or not looks_like_standalone_formula_fragment(source):
        return target, []
    if not has_better_latex_signal(source):
        return target, []
    if math_token_similarity(target, source) < 0.30:
        return target, []
    return source, [{"index": 0, "old_math": target, "new_math": source, "reasons": old_reasons}]


def looks_like_standalone_formula_fragment(value: str) -> bool:
    stripped = html.unescape(str(value or "")).strip()
    if not stripped:
        return False
    if INLINE_MATH_RE.fullmatch(stripped):
        return True

    without_latex_commands = re.sub(r"\\[A-Za-z]+", " ", stripped)
    if re.search(r"\b[A-Za-z]{3,}\b", without_latex_commands):
        return False
    return bool(re.search(r"[\\_^=/{}]|[≤≥≈≒∑∫σμλαβγδθπω]", stripped))


def overlay_table_html_cells(target_html: str, source_html: str) -> tuple[str, list[dict[str, Any]], str]:
    target_cells = list(TABLE_CELL_RE.finditer(target_html or ""))
    source_cells = list(TABLE_CELL_RE.finditer(source_html or ""))
    if not target_cells:
        return target_html, [], "no table cells"
    if len(target_cells) != len(source_cells):
        return target_html, [], f"table cell count mismatch ({len(target_cells)} != {len(source_cells)})"

    replacements: list[dict[str, Any]] = []
    pieces: list[str] = []
    cursor = 0
    for index, (old_cell, new_cell) in enumerate(zip(target_cells, source_cells)):
        old_inner = old_cell.group(2)
        new_inner = new_cell.group(2)
        repaired_inner, cell_replacements = replace_formula_cell_if_safe(old_inner, new_inner)
        pieces.append(target_html[cursor : old_cell.start()])
        pieces.append(old_cell.group(1))
        pieces.append(repaired_inner)
        pieces.append(old_cell.group(3))
        cursor = old_cell.end()
        for item in cell_replacements:
            replacements.append({**item, "cell_index": index})
    pieces.append(target_html[cursor:])
    if not replacements:
        return target_html, [], "no damaged table cell math replaced"
    return "".join(pieces), replacements, ""


def overlay_table_entry(target: dict[str, Any], source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    updated = json.loads(json.dumps(target, ensure_ascii=False))
    replacements: list[dict[str, Any]] = []

    for field in ("title", "html"):
        if not isinstance(target.get(field), str) or not isinstance(source.get(field), str):
            continue
        if field == "html":
            new_value, field_replacements, _reason = overlay_table_html_cells(target[field], source[field])
        else:
            new_value, field_replacements, _reason = overlay_inline_math_text(target[field], source[field])
        if field_replacements and new_value != target[field]:
            updated[field] = new_value
            replacements.extend({**item, "field": field} for item in field_replacements)

    if same_shape_rows(target.get("rows"), source.get("rows")):
        rows = json.loads(json.dumps(target.get("rows"), ensure_ascii=False))
        for row_index, (target_row, source_row) in enumerate(zip(target.get("rows"), source.get("rows"))):
            for col_index, (target_cell, source_cell) in enumerate(zip(target_row, source_row)):
                if not isinstance(target_cell, str) or not isinstance(source_cell, str):
                    continue
                repaired_cell, cell_replacements = replace_formula_cell_if_safe(target_cell, source_cell)
                if cell_replacements and repaired_cell != target_cell:
                    rows[row_index][col_index] = repaired_cell
                    replacements.extend(
                        {**item, "field": "rows", "row_index": row_index, "column_index": col_index}
                        for item in cell_replacements
                    )
        if rows != target.get("rows"):
            updated["rows"] = rows

    return updated, replacements


def build_table_items(structured_dir: Path, source_dir: Path) -> list[dict[str, Any]]:
    target_path = structured_dir / "table_library.json"
    source_path = source_dir / "table_library.json"
    if not target_path.exists() or not source_path.exists():
        return []
    target_payload = read_json(target_path)
    source_payload = read_json(source_path)
    target_tables = target_payload.get("tables")
    source_tables = source_payload.get("tables")
    if not isinstance(target_tables, list) or not isinstance(source_tables, list):
        return []

    source_by_id = {str(item.get("id")): item for item in source_tables if isinstance(item, dict)}
    items: list[dict[str, Any]] = []
    for target in target_tables:
        if not isinstance(target, dict):
            continue
        table_id = str(target.get("id") or "")
        source = source_by_id.get(table_id)
        if not isinstance(source, dict):
            continue
        updated, replacements = overlay_table_entry(target, source)
        if not replacements or updated == target:
            continue
        old_math, new_math = changed_math_summary(replacements)
        items.append(
            {
                "kind": "table",
                "table_id": table_id,
                "field": "table_library.tables[]",
                "status": "accepted",
                "action": "auto_apply",
                "confidence": AUTO_CONFIDENCE,
                "old_entry": target,
                "new_entry": updated,
                "old_math": old_math,
                "new_math": new_math,
                "replacements": replacements,
                "source": {"mode": "same_table_id", "table_id": table_id},
                "reasons": ["overlay table LaTeX only from same table id"],
            }
        )
    return items


def count_statuses(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter = Counter(str(item.get(key) or "") for item in items)
    return dict(sorted(counter.items()))


def build_overlay_patch(
    *,
    structured_dir: str | Path,
    source_dir: str | Path,
    include_tables: bool = True,
    unit_filter: set[str] | None = None,
    limit: int | None = None,
    exact_similarity: float = EXACT_BLOCK_SIMILARITY,
    fallback_similarity: float = FALLBACK_BLOCK_SIMILARITY,
) -> dict[str, Any]:
    structured_root = Path(structured_dir)
    source_root = Path(source_dir)
    source_units, source_by_chapter = load_source_units(source_root)
    items: list[dict[str, Any]] = []
    scanned_blocks = 0

    for path in iter_unit_files(structured_root):
        data = read_json(path)
        unit_id = str(data.get("id") or path.stem)
        if unit_filter and unit_id not in unit_filter:
            continue
        chapter = str((data.get("metadata") or {}).get("chapter") or "").strip().lower()
        source_unit = source_units.get(unit_id)
        blocks = data.get("blocks")
        if not isinstance(blocks, list):
            continue
        for block_index, target_block in enumerate(blocks):
            if not isinstance(target_block, dict):
                continue
            old_content = str(target_block.get("content") or "")
            if not old_content or not any(math_damage_reasons(span.inner) for span in inline_math_spans(old_content)):
                continue
            scanned_blocks += 1
            source_block = source_block_at(source_unit, block_index)
            item = None
            reject_source_block: dict[str, Any] | None = source_block
            reject_source_unit_id = unit_id if source_block is not None else ""
            reject_source_mode = "same_unit_block" if source_block is not None else "none"
            reject_confidence = 0.0
            reject_reasons: list[str] = []
            if source_block is not None:
                item = build_block_overlay_item(
                    unit_id=unit_id,
                    block_index=block_index,
                    target_block=target_block,
                    source_block=source_block,
                    source_unit_id=unit_id,
                    source_mode="same_unit_block",
                    min_similarity=exact_similarity,
                )
                if item is None:
                    reject_reasons, reject_confidence = diagnose_block_candidate(
                        target_block=target_block,
                        source_block=source_block,
                        min_similarity=exact_similarity,
                    )
            if item is None and chapter:
                fallback_block, score, fallback_unit_id = find_fallback_block(
                    target_block=target_block,
                    target_content=old_content,
                    source_units_for_chapter=source_by_chapter.get(chapter, []),
                    min_similarity=fallback_similarity,
                )
                if fallback_block is not None:
                    reject_source_block = fallback_block
                    reject_source_unit_id = fallback_unit_id
                    reject_source_mode = "chapter_text_fallback"
                    reject_confidence = score
                    item = build_block_overlay_item(
                        unit_id=unit_id,
                        block_index=block_index,
                        target_block=target_block,
                        source_block=fallback_block,
                        source_unit_id=fallback_unit_id,
                        source_mode="chapter_text_fallback",
                        min_similarity=fallback_similarity,
                    )
                    if item is None:
                        reject_reasons, reject_confidence = diagnose_block_candidate(
                            target_block=target_block,
                            source_block=fallback_block,
                            min_similarity=fallback_similarity,
                        )
                elif source_block is None:
                    reject_source_mode = "none"
                    reject_source_unit_id = fallback_unit_id
                    reject_confidence = score
                    reject_reasons = [f"no aligned source block; best fallback similarity {score:.2f}"]
            if item is not None:
                items.append(item)
            else:
                if not reject_reasons:
                    reject_reasons = ["no aligned source block"]
                items.append(
                    build_rejected_block_item(
                        unit_id=unit_id,
                        block_index=block_index,
                        target_block=target_block,
                        source_block=reject_source_block,
                        source_unit_id=reject_source_unit_id,
                        source_mode=reject_source_mode,
                        confidence=reject_confidence,
                        reasons=reject_reasons,
                    )
                )
            if limit and len(items) >= limit:
                break
        if limit and len(items) >= limit:
            break

    if include_tables and (not limit or len(items) < limit):
        table_items = build_table_items(structured_root, source_root)
        if limit:
            table_items = table_items[: max(0, limit - len(items))]
        items.extend(table_items)

    return {
        "metadata": {
            "generated_at": utc_now_iso(),
            "mode": "inline_latex_overlay",
            "structured_dir": str(structured_root),
            "source_dir": str(source_root),
            "item_count": len(items),
            "scanned_damaged_blocks": scanned_blocks,
            "status_counts": count_statuses(items, "status"),
            "action_counts": count_statuses(items, "action"),
            "kinds": count_statuses(items, "kind"),
        },
        "items": items,
    }


def apply_overlay_patch(
    patch_payload: dict[str, Any],
    structured_dir: str | Path,
    *,
    include_review: bool = False,
) -> dict[str, Any]:
    root = Path(structured_dir)
    applied = 0
    skipped = 0
    touched_files: set[str] = set()

    block_items: dict[str, list[dict[str, Any]]] = defaultdict(list)
    table_items: list[dict[str, Any]] = []
    for item in patch_payload.get("items", []):
        if not isinstance(item, dict):
            continue
        action = str(item.get("action") or "")
        if action != "auto_apply" and not (include_review and action == "review"):
            skipped += 1
            continue
        if item.get("kind") == "table":
            table_items.append(item)
        else:
            block_items[str(item.get("unit_id") or "")].append(item)

    for unit_id, items in block_items.items():
        path = root / f"{unit_id}.json"
        if not path.exists():
            skipped += len(items)
            continue
        data = read_json(path)
        blocks = data.get("blocks")
        if not isinstance(blocks, list):
            skipped += len(items)
            continue
        changed = False
        for item in items:
            block_index = item.get("block_index")
            if not isinstance(block_index, int) or block_index >= len(blocks):
                skipped += 1
                continue
            block = blocks[block_index]
            if not isinstance(block, dict):
                skipped += 1
                continue
            if str(block.get("content") or "") != str(item.get("old_content") or ""):
                skipped += 1
                continue
            block["content"] = str(item.get("new_content") or "")
            applied += 1
            changed = True
        if changed:
            write_json(path, data)
            touched_files.add(str(path))

    if table_items:
        path = root / "table_library.json"
        if path.exists():
            payload = read_json(path)
            tables = payload.get("tables")
            if isinstance(tables, list):
                table_index = {str(item.get("id") or ""): idx for idx, item in enumerate(tables) if isinstance(item, dict)}
                changed = False
                for item in table_items:
                    table_id = str(item.get("table_id") or "")
                    idx = table_index.get(table_id)
                    if idx is None:
                        skipped += 1
                        continue
                    if tables[idx] != item.get("old_entry"):
                        skipped += 1
                        continue
                    tables[idx] = item.get("new_entry")
                    applied += 1
                    changed = True
                if changed:
                    write_json(path, payload)
                    touched_files.add(str(path))
            else:
                skipped += len(table_items)
        else:
            skipped += len(table_items)

    return {
        "applied": applied,
        "skipped": skipped,
        "touched_files": sorted(touched_files),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Overlay-repair damaged inline LaTeX without replacing prose.")
    parser.add_argument("--structured-dir", default="data/structured")
    parser.add_argument("--source-dir", required=True, help="Fresh structured directory generated from current process.py.")
    parser.add_argument("--out", default="", help="Output directory for repair_patch.json and reports.")
    parser.add_argument("--apply", action="store_true", help="Apply auto_apply items after writing the patch.")
    parser.add_argument("--include-review", action="store_true", help="Apply review items too. Off by default.")
    parser.add_argument("--no-tables", action="store_true", help="Skip table_library overlay.")
    parser.add_argument("--unit", action="append", default=[], help="Limit to a structured unit id. Can repeat.")
    parser.add_argument("--limit", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out) if args.out else Path("tmp") / "structured_repair" / f"full_inline_latex_overlay_{stamp}"
    unit_filter = set(args.unit) if args.unit else None
    patch = build_overlay_patch(
        structured_dir=args.structured_dir,
        source_dir=args.source_dir,
        include_tables=not args.no_tables,
        unit_filter=unit_filter,
        limit=args.limit if args.limit > 0 else None,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "repair_patch.json", patch)
    apply_result = None
    if args.apply:
        apply_result = apply_overlay_patch(patch, args.structured_dir, include_review=args.include_review)
        write_json(out_dir / "apply_result.json", apply_result)
    summary = {
        "out_dir": str(out_dir),
        "patch": patch.get("metadata", {}),
        "apply_result": apply_result,
    }
    write_json(out_dir / "run_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
