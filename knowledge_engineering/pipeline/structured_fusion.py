"""Evidence-based structured fusion pipeline for production candidate outputs.

This stage runs after the baseline paper2latex -> structured conversion.  It is
deliberately conservative:

- paper2latex structured output remains the structural source of truth;
- GLM OCR is only used as a guarded secondary source for prose-like blocks;
- reference structured directories are only used to recover table-library
  entries when the current output already contains matching table references.

The goal is to make the candidate-quality cleanup reproducible without
chapter-specific patches. Candidate findings are promoted only when they can be
expressed as generic reusable repair rules for future scanned books.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from knowledge_engineering.core.common import (
    chapter_sort_key,
    collapse_ws,
    read_json,
    sort_formula_refs,
    sort_table_ref_keys,
    sort_table_refs,
    table_reference_key,
    table_sort_key,
)
from knowledge_engineering.core.runtime import (
    DEFAULT_SOURCE_TITLE,
    FormulaLibrary,
    KnowledgeBlock,
    KnowledgeUnit,
    TableEntry,
    TableLibrary,
)
from knowledge_engineering.processors.ocr_evidence import (
    OCREvidence,
    OCREvidenceIndex,
    build_ocr_evidence_index,
    evidence_to_dict,
    score_table_entry_against_evidence,
    score_table_evidence_pair,
    table_body_text,
    table_entry_caption_label,
    table_entry_from_evidence,
    table_entry_has_own_caption,
    table_entry_hash,
)
from knowledge_engineering.processors.structured_repair import (
    AUTO_THRESHOLD,
    MAX_WINDOW_PARAGRAPHS,
    REPAIRABLE_ISSUES,
    REVIEW_THRESHOLD,
    GLMChapterIndex,
    build_candidate_for_block,
    expected_order_for_unit,
    load_glm_index,
    simple_audit_block,
)
from knowledge_engineering.reports.fusion_reporting import (
    build_structured_fusion_summary,
    write_structured_fusion_artifacts,
)

FORMULA_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_FORMULA|FORMULA):(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\]\]"
)
TABLE_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_TABLE|TABLE):(?P<label>(?:\d+\.\d+[A-Za-z]?|inline_\d+))\]\]",
    re.IGNORECASE,
)
PHYSICAL_TABLE_PLACEHOLDER_RE = re.compile(
    r"\[\[TABLE:(?P<label>(?:\d+\.\d+[A-Za-z]?|inline_\d+))\]\]",
    re.IGNORECASE,
)
TABLE_TEXT_RE = re.compile(r"\bTable\s+(?P<label>\d+\.\d+[A-Za-z]?)\b", re.IGNORECASE)
BROKEN_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_)?(?:FORMULA|TABLE|EXAMPLE|FIGURE)\s*(?::(?:(?!\]\]).)*)?$",
    re.IGNORECASE | re.DOTALL,
)
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)[^\n$]*?(?<!\$)\$(?!\$)")
DISPLAY_MATH_RE = re.compile(
    r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}[\s\S]*?\\end\{(?:equation|align|gather|multline)\*?\}",
    re.IGNORECASE,
)
TEX_COMMAND_RE = re.compile(r"\\[A-Za-z@]+(?:\*?)")
NOISE_SYMBOLS_RE = re.compile(r"^[\s.\-_,;:|/\\*+=~^'\"`()[\]{}<>]+$")
PAGE_NUMBER_RE = re.compile(r"^\s*(?:page\s*)?\d{1,4}\s*$", re.IGNORECASE)
H_ONLY_RE = re.compile(r"^\s*\[\s*h\s*\]\s*$", re.IGNORECASE)
OCR_RESIDUAL_MARKER_RE = re.compile(r"(^|\s)\[(?:h|t|b|p)\](?=\s|$)", re.IGNORECASE)
LEADING_FLOAT_MARKER_RE = re.compile(r"^\s*\[(?P<marker>[htbp])\]\s+(?P<rest>.+)$", re.IGNORECASE)
STRUCTURED_REF_RE = re.compile(r"\[\[(?:SEE_FORMULA|FORMULA|SEE_TABLE|TABLE):[^\]]+\]\]")
NON_ENGLISH_NOISE_CHARS = "锕鈭鈮蟽渭伪尾纬未胃蟺蠅路脳�"
ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d]")
FORMULA_SPACING_COMMAND_RE = re.compile(r"(\\(?:qquad|quad|;|,|:))(?=[A-Za-z])")
NESTED_SUBSCRIPT_RE = re.compile(
    r"\\(?P<command>[A-Za-z]+)_(?P<first>[A-Za-z0-9]+)_(?P<second>[A-Za-z0-9]+)(?=(?:\^|[\s,.;:)\]}]|$))"
)
NESTED_ACCENT_COMMANDS = ("overline", "underline", "bar", "hat", "tilde", "vec")
PUBLICATION_FOOTER_TAIL_RE = re.compile(
    r"(?:Evolution and Selection of Quantitative Traits\.|Published\s+2018\s+by\s+Oxford\s+University\s+Press\.|"
    r"©\s*Bruce\s+Walsh\s*&\s*Michael\s+Lynch\s+2018\.?)",
    re.IGNORECASE,
)

DETERMINISTIC_DROP_ISSUES = {"empty_content", "h_only_block", "ghost_block", "broken_placeholder"}
REPAIR_ATTEMPT_ISSUES = set(REPAIRABLE_ISSUES)
REFERENCE_ONLY_ISSUES = {"formula_reference_missing", "table_reference_missing"}

TABLE_EVIDENCE_MIN_BODY_CHARS = 24
TABLE_EVIDENCE_STRONG_QUALITY = 0.74
TABLE_STRUCTURED_CONFLICT_SCORE = 0.62
TABLE_CHANNEL_AGREEMENT_SCORE = 0.72
TABLE_CHANNEL_CONFLICT_SCORE = 0.50


@dataclass
class UnitRecord:
    path: Path
    unit: KnowledgeUnit


def normalize_match_text(text: str) -> str:
    value = str(text or "")
    value = STRUCTURED_REF_RE.sub(" ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\\([A-Za-z]+)", r" \1 ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def _copy_structured_dir(source_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in source_dir.glob("*.json"):
        target = output_dir / path.name
        if path.resolve() == target.resolve():
            continue
        shutil.copy2(path, target)


def _load_unit_records(structured_dir: Path) -> list[UnitRecord]:
    records: list[UnitRecord] = []
    for path in sorted(structured_dir.glob("*.json")):
        if path.name in {"formula_library.json", "table_library.json"}:
            continue
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            continue
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        unit_id = str(data.get("id") or path.stem)
        chapter = str(metadata.get("chapter") or unit_id.split("_", 1)[0]).strip().lower()
        blocks = [
            KnowledgeBlock(
                type=str(block.get("type") or "discussion"),
                content=str(block.get("content") or ""),
            )
            for block in data.get("blocks", [])
            if isinstance(block, dict)
        ]
        unit = KnowledgeUnit(
            id=unit_id,
            chapter=chapter,
            section=str(metadata.get("section") or ""),
            subsections=[
                str(item)
                for item in (metadata.get("subsections") or [])
                if str(item).strip()
            ],
            source_file=str(metadata.get("source_file") or ""),
            source_title=str(metadata.get("source_title") or DEFAULT_SOURCE_TITLE),
            blocks=blocks,
            formula_references=[
                str(item)
                for item in (metadata.get("formula_references") or [])
                if str(item).strip()
            ],
            table_references=[
                str(item)
                for item in (metadata.get("table_references") or [])
                if str(item).strip()
            ],
            table_reference_keys=[
                str(item)
                for item in (metadata.get("table_reference_keys") or [])
                if str(item).strip()
            ],
            section_level_1=(
                str(metadata.get("section_level_1")).strip()
                if metadata.get("section_level_1") is not None
                else None
            ),
            section_level_2=(
                str(metadata.get("section_level_2")).strip()
                if metadata.get("section_level_2") is not None
                else None
            ),
            heading_path=[
                str(item)
                for item in (metadata.get("heading_path") or [])
                if str(item).strip()
            ],
            display_heading=(
                str(metadata.get("display_heading")).strip()
                if metadata.get("display_heading") is not None
                else None
            ),
        )
        records.append(UnitRecord(path=path, unit=unit))
    return records


def _save_unit_records(records: Iterable[UnitRecord]) -> None:
    for record in records:
        record.unit.save(str(record.path))


def _formula_ids(formula_library: FormulaLibrary) -> set[str]:
    return {str(formula.id or "").strip().lower() for formula in formula_library.formulas if formula.id}


def _table_ids(table_library: TableLibrary) -> set[str]:
    return {str(table.id or "").strip() for table in table_library.tables if table.id}


def _strip_math_segments(text: str) -> str:
    value = DISPLAY_MATH_RE.sub(" ", str(text or ""))
    return INLINE_MATH_RE.sub(" ", value)


def _has_unclosed_short_tail(text: str) -> bool:
    stripped = str(text or "").strip()
    if len(stripped) >= 90:
        return False
    if stripped.count("(") > stripped.count(")"):
        return True
    if stripped.count("[") > stripped.count("]"):
        return True
    if stripped.count('"') % 2 == 1:
        return True
    if stripped.count("'") % 2 == 1 and len(stripped.split()) <= 8:
        return True
    return False


def _is_ghost_block(text: str) -> bool:
    stripped = str(text or "").strip()
    if not stripped:
        return False
    if H_ONLY_RE.fullmatch(stripped):
        return False
    if stripped in {"©", "..", "...", ".", "·", "•", "-", "--", "—", "_", "*", "#"}:
        return True
    if PAGE_NUMBER_RE.fullmatch(stripped):
        return True
    compact = re.sub(r"\s+", "", stripped)
    if len(compact) <= 6 and NOISE_SYMBOLS_RE.fullmatch(compact):
        return True
    if len(compact) <= 4 and not re.search(r"[A-Za-z0-9]", compact):
        return True
    return False


def _has_ocr_residual_marker(text: str) -> bool:
    return bool(OCR_RESIDUAL_MARKER_RE.search(str(text or "")))


def _strip_structured_refs_math_and_residue(text: str) -> str:
    value = STRUCTURED_REF_RE.sub(" ", str(text or ""))
    value = _strip_math_segments(value)
    value = OCR_RESIDUAL_MARKER_RE.sub(" ", value)
    return collapse_ws(value)


def _is_residual_only_text(text: str) -> bool:
    stripped = str(text or "").strip()
    if not stripped:
        return True
    if H_ONLY_RE.fullmatch(stripped):
        return True
    compact = re.sub(r"\s+", "", stripped)
    return bool(compact and re.fullmatch(r"[\[\]().,;:|/\\{}<>_\-]+", compact))


def _has_natural_language(text: str) -> bool:
    return bool(re.search(r"[A-Za-z][A-Za-z'-]*", str(text or "")))


def _is_short_heading_like(text: str) -> bool:
    stripped = str(text or "").strip()
    if not stripped or STRUCTURED_REF_RE.search(stripped) or "$" in stripped:
        return False
    if re.search(r"[.;:!?()[\]{}]", stripped):
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", stripped)
    if not (1 <= len(words) <= 6):
        return False
    plain = re.sub(r"[-\s]+", " ", stripped).strip()
    if plain != " ".join(words):
        return False
    return all(word[:1].isupper() or word.isupper() for word in words if len(word) > 2)


def _orphan_reference_fragment_code(text: str) -> str:
    stripped = collapse_ws(text)
    if not stripped:
        return ""
    matches = list(STRUCTURED_REF_RE.finditer(stripped))
    if not matches:
        return ""

    first = matches[0]
    marker = first.group(0).upper()
    prefix = stripped[: first.start()].strip()
    tail = stripped[first.end() :].strip()
    is_table_marker = "TABLE:" in marker
    is_attach_marker = marker.startswith("[[TABLE:") or marker.startswith("[[FORMULA:")
    is_table_body_anchor = marker.startswith("[[TABLE:")
    continuation_start = re.match(r"^[A-Za-z]+", tail)
    continuation_raw_word = continuation_start.group(0) if continuation_start else ""
    continuation_word = continuation_raw_word.lower()
    allowed_reference_verbs = {"summarizes", "summarises", "shows", "gives", "lists", "presents", "reports", "contains", "provides", "illustrates"}
    tail_starts_as_fragment = bool(re.match(r"^[).,;:]+", tail)) or (
        bool(continuation_word)
        and continuation_word
        not in allowed_reference_verbs
        and (continuation_raw_word[:1].islower() or continuation_word in {"and", "or", "but"})
    )
    if (
        is_table_body_anchor
        and not prefix
        and tail
        and not re.match(r"^[).,;:]+", tail)
        and _has_natural_language(tail)
    ):
        return ""

    if prefix and _is_residual_only_text(prefix) and not _has_ocr_residual_marker(prefix):
        return "orphan_table_fragment" if is_table_marker else "orphan_reference_fragment"
    if is_attach_marker and tail_starts_as_fragment:
        return "orphan_table_fragment" if is_table_marker else "orphan_reference_fragment"

    residual_tail = STRUCTURED_REF_RE.sub(" ", stripped)
    residual_tail = OCR_RESIDUAL_MARKER_RE.sub(" ", residual_tail)
    if re.search(r"[).,;:]", residual_tail) and _is_residual_only_text(residual_tail):
        return (
            "orphan_table_fragment"
            if any("TABLE:" in match.group(0).upper() for match in matches)
            else "orphan_reference_fragment"
        )
    return ""


def _strip_leading_float_marker(text: str) -> tuple[str, str]:
    value = str(text or "")
    match = LEADING_FLOAT_MARKER_RE.match(value)
    if not match:
        return value, ""
    rest = str(match.group("rest") or "").lstrip()
    if len(rest) < 16:
        return value, ""
    if len(normalize_match_text(rest).split()) < 2:
        return value, ""
    return rest, str(match.group("marker") or "").lower()


def _normalize_formula_latex(latex: str) -> tuple[str, list[str]]:
    value = ZERO_WIDTH_RE.sub("", str(latex or ""))
    reasons: list[str] = []
    if not value:
        return value, reasons

    updated = FORMULA_SPACING_COMMAND_RE.sub(r"\1 ", value)
    if updated != value:
        reasons.append("spaced_command_suffix")
        value = updated

    while True:
        updated = NESTED_SUBSCRIPT_RE.sub(
            lambda match: (
                f"\\{match.group('command')}"
                f"_{{{match.group('first')}_{match.group('second')}}}"
            ),
            value,
        )
        if updated == value:
            break
        value = updated
        reasons.append("nested_subscript_normalized")

    for command in NESTED_ACCENT_COMMANDS:
        pattern = re.compile(rf"\\{command}\{{\\{command}\{{([^{{}}]+)\}}\}}")
        while True:
            updated = pattern.sub(rf"\\{command}{{\1}}", value)
            if updated == value:
                break
            value = updated
            reasons.append(f"collapse_nested_{command}")

    return value, reasons


def _normalize_latex_in_text(text: str) -> tuple[str, list[str]]:
    value = ZERO_WIDTH_RE.sub("", str(text or ""))
    reasons: list[str] = []
    if not value:
        return value, reasons
    updated = re.sub(r"\s*\$\$\s*E\s*=\s*mc\^2\s*\$\$\s*", " ", value)
    if updated != value:
        reasons.append("placeholder_formula_pollution_removed")
        value = re.sub(r"\s{2,}", " ", updated).strip()
    updated = FORMULA_SPACING_COMMAND_RE.sub(r"\1 ", value)
    if updated != value:
        reasons.append("spaced_command_suffix")
        value = updated
    updated = re.sub(r"\\sigma_e_s\^2", r"\\sigma_{e_s}^2", value)
    if updated != value:
        reasons.append("nested_subscript_normalized")
        value = updated
    while True:
        updated = NESTED_SUBSCRIPT_RE.sub(
            lambda match: (
                f"\\{match.group('command')}"
                f"_{{{match.group('first')}_{match.group('second')}}}"
            ),
            value,
        )
        if updated == value:
            break
        value = updated
        reasons.append("nested_subscript_normalized")
    updated = re.sub(r"\\sqrt\{\\ln\(([^{}$]+)\)(?=\$)", r"\\sqrt{\\ln(\1)}", value)
    if updated != value:
        reasons.append("sqrt_ln_missing_closing_brace")
        value = updated
    return value, reasons


def _strip_leading_publication_footer_tail(text: str) -> tuple[str, list[str]]:
    value = str(text or "")
    reasons: list[str] = []
    updated = re.sub(
        r"^\s*(?:©|Â©)\s+(?=[A-Za-z])",
        "",
        value,
        count=1,
    )
    if updated != value:
        reasons.append("leading_copyright_symbol_stripped")
        value = updated
    updated = re.sub(r"^\s*\d{1,4}\s+(?=[A-Za-z])", "", value, count=1)
    if updated != value:
        reasons.append("leading_page_number_stripped")
        value = updated
    while True:
        match = PUBLICATION_FOOTER_TAIL_RE.search(value)
        if not match:
            break
        before = value[: match.start()].rstrip()
        after = value[match.end() :].lstrip()
        if before and after:
            break
        value = (before + (" " if before and after else "") + after).strip()
        reasons.append("publication_footer_tail_stripped")
    return value, sorted(set(reasons))


def _sanitize_table_entry(entry: TableEntry) -> tuple[TableEntry, list[str]]:
    reasons: list[str] = []
    source = entry.source if isinstance(entry.source, dict) else {}
    if str(entry.table_type or "").strip().lower() == "inline" and re.match(
        r"^\s*Figure\s+\d+\.\d+\b",
        str(entry.title or ""),
        flags=re.IGNORECASE,
    ):
        entry.title = entry.label_format or f"Inline Table {entry.id}"
        source = dict(source)
        source["title_sanitized_from_figure_caption"] = True
        entry.source = source
        reasons.append("inline_table_title_sanitized_from_figure_caption")

    normalized_rows: list[list[str]] = []
    rows_changed = False
    for row in entry.rows or []:
        if not isinstance(row, list):
            normalized_rows.append(row)
            continue
        new_row: list[str] = []
        for cell in row:
            normalized_cell, cell_reasons = _normalize_latex_in_text(str(cell))
            if normalized_cell != str(cell):
                rows_changed = True
                reasons.extend(cell_reasons)
            new_row.append(normalized_cell)
        normalized_rows.append(new_row)
    if rows_changed:
        entry.rows = normalized_rows

    for attr in ("title", "html", "raw_body", "markdown_body"):
        current = getattr(entry, attr, None)
        if current is None:
            continue
        normalized_value, value_reasons = _normalize_latex_in_text(str(current))
        if normalized_value != str(current):
            setattr(entry, attr, normalized_value)
            reasons.extend(value_reasons)

    return entry, sorted(set(reasons))


def _sanitize_table_library(table_library: TableLibrary) -> tuple[TableLibrary, Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    for entry in table_library.tables:
        before_hash = table_entry_hash(entry)
        entry, reasons = _sanitize_table_entry(entry)
        if not reasons:
            continue
        after_hash = table_entry_hash(entry)
        if after_hash == before_hash:
            continue
        for reason in reasons:
            stats[reason] += 1
        events.append(
            {
                "table_id": str(entry.id or "").strip(),
                "chapter": str((entry.source or {}).get("chapter") or "").strip(),
                "action": "sanitize_table_entry",
                "reason_codes": reasons,
                "entry_hash_before": before_hash,
                "entry_hash_after": after_hash,
            }
        )
    return table_library, stats, events


def _sanitize_example_library(root: Path) -> tuple[Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    path = root / "example_library.json"
    if not path.exists():
        return stats, events
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return stats, events
    examples = payload.get("examples") if isinstance(payload, dict) else None
    if not isinstance(examples, list):
        return stats, events
    changed = False
    for example in examples:
        if not isinstance(example, dict):
            continue
        example_id = str(example.get("example_id") or example.get("example_ref") or "").strip()
        for key in ("content_markdown", "content_plain"):
            original = str(example.get(key) or "")
            normalized, reasons = _normalize_latex_in_text(original)
            if normalized == original:
                continue
            example[key] = normalized
            changed = True
            stats["example_text_normalized"] += 1
            events.append(
                {
                    "example_id": example_id,
                    "field": key,
                    "action": "normalize_latex_text",
                    "reason_codes": reasons,
                }
            )
    if changed:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return stats, events


def _non_english_noise_ratio(text: str) -> float:
    compact = re.sub(r"\s+", "", str(text or ""))
    if not compact:
        return 0.0
    hits = sum(1 for char in compact if char in NON_ENGLISH_NOISE_CHARS)
    return hits / max(1, len(compact))


def _extract_formula_refs_from_content(content: str) -> list[str]:
    return sort_formula_refs(match.group("label") for match in FORMULA_PLACEHOLDER_RE.finditer(content or ""))


def _extract_table_refs_from_content(content: str) -> list[str]:
    labels = [match.group("label") for match in TABLE_PLACEHOLDER_RE.finditer(content or "")]
    labels.extend(match.group("label") for match in TABLE_TEXT_RE.finditer(content or ""))
    return sort_table_refs(labels)


def _is_external_table_reference(content: str, label: str) -> bool:
    value = str(content or "")
    table_id = re.escape(str(label or "").strip())
    if not table_id:
        return False
    placeholder = rf"\[\[\s*(?:SEE_)?TABLE\s*:\s*{table_id}\s*\]\]"
    table_text = rf"\bTables?\s+{table_id}\b"
    target = rf"(?:{placeholder}|{table_text})"
    patterns = [
        rf"\bLW\s+(?:{target})",
        rf"\bLynch\s+and\s+Walsh\s+(?:{target})",
        rf"\b(?:Vol\.?|Volume)\s+[A-Za-z0-9IVXLCivxlc.-]+\s+(?:{target})",
        rf"\b(?:previous|companion|external)\s+(?:volume|book|chapter)\b[^.\n]{{0,80}}(?:{target})",
    ]
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def audit_block_content(
    *,
    content: str,
    block_type: str,
    known_formula_ids: set[str],
    known_table_ids: set[str],
) -> list[dict[str, Any]]:
    issues = list(simple_audit_block(content))
    value = str(content or "")
    stripped = value.strip()

    def add(severity: str, code: str, message: str, matched_value: str = "") -> None:
        issues.append(
            {
                "severity": severity,
                "code": code,
                "message": message,
                "value": matched_value,
            }
        )

    if not stripped:
        add("fatal", "empty_content", "Block content is empty.")
    if H_ONLY_RE.fullmatch(stripped):
        add("error", "h_only_block", "Floating-position marker leaked as a block.")
    elif _is_ghost_block(stripped):
        add("error", "ghost_block", "Block contains only page/symbol noise.", stripped)
    if _has_ocr_residual_marker(stripped):
        add("error", "ocr_residual_marker", "OCR/layout float marker residue leaked into block content.", "[h]")
    if BROKEN_PLACEHOLDER_RE.search(stripped) or re.search(r"\[\[\s*SEE_?\s*$", stripped, flags=re.IGNORECASE):
        add("error", "broken_placeholder", "Structured placeholder appears incomplete.")
    orphan_code = _orphan_reference_fragment_code(stripped)
    if orphan_code:
        add("error", orphan_code, "Structured reference appears as an orphaned split fragment.")
    if _has_unclosed_short_tail(stripped):
        add("error", "suspicious_truncation", "Short block appears to end inside punctuation.")

    prose_without_math = _strip_math_segments(stripped)
    if TEX_COMMAND_RE.search(prose_without_math):
        add("error", "tex_command_leak", "LaTeX command remains outside math spans.")

    if len(stripped) < 20 and stripped and not _is_short_heading_like(stripped) and not orphan_code:
        add("warning", "very_short_block", "Block is very short.")
    if re.search(r"\s{4,}", value) or "\n\n\n" in value:
        add("warning", "excessive_whitespace", "Block contains excessive whitespace.")
    if _non_english_noise_ratio(stripped) >= 0.08 and len(stripped) >= 30:
        add("warning", "suspicious_non_english_noise", "Block contains a high OCR-noise character ratio.")
    if "�" in stripped or re.search(r"[鈥锟]{2,}", stripped):
        add("warning", "possible_ocr_garbled_text", "Block contains likely mojibake/OCR residue.")

    formula_refs = _extract_formula_refs_from_content(stripped)
    table_refs = _extract_table_refs_from_content(stripped)
    for label in formula_refs:
        if label.lower() not in known_formula_ids:
            add("fatal", "formula_reference_missing", f"Formula reference is not in formula_library: {label}", label)
    for label in table_refs:
        if label not in known_table_ids:
            if _is_external_table_reference(stripped, label):
                add("info", "external_reference", f"External table reference is outside local table_library: {label}", label)
                continue
            # table/formula 同号归一：同号公式存在且同号表不存在，说明是公式引用被误写成 table
            if label.lower() in known_formula_ids:
                continue
            add("fatal", "table_reference_missing", f"Table reference is not in table_library: {label}", label)

    if block_type == "derivation":
        if len(formula_refs) > 8:
            add("warning", "derivation_reference_overload", "Derivation references unusually many formulas.")
        duplicated_formula_refs = sorted(ref for ref, count in Counter(formula_refs).items() if count >= 3)
        if duplicated_formula_refs:
            add(
                "warning",
                "derivation_repeated_formula_reference",
                "Derivation repeats the same formula reference unusually many times.",
                ", ".join(duplicated_formula_refs),
            )
        readable = _strip_structured_refs_math_and_residue(stripped)
        if formula_refs and (_is_residual_only_text(readable) or not _has_natural_language(readable)):
            add("warning", "derivation_placeholder_only_text", "Derivation has little readable text beyond formula refs.")

    return issues


def _issue_codes(issues: Iterable[dict[str, Any]]) -> list[str]:
    return sorted({str(issue.get("code") or "").strip() for issue in issues if issue.get("code")})


def _should_drop_block(issues: list[dict[str, Any]]) -> bool:
    return bool(DETERMINISTIC_DROP_ISSUES & set(_issue_codes(issues)))


def _unit_ordinal(unit_id: str) -> int:
    match = re.match(r"^(?:chapter|appendix)\d+_(\d+)$", str(unit_id or ""), flags=re.IGNORECASE)
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0


def _chapter_ordinals(records: Iterable[UnitRecord]) -> dict[str, int]:
    max_by_chapter: dict[str, int] = defaultdict(int)
    for record in records:
        ordinal = _unit_ordinal(record.unit.id)
        if ordinal > max_by_chapter[record.unit.chapter]:
            max_by_chapter[record.unit.chapter] = ordinal
    return dict(max_by_chapter)


def _record_chapters(records: Iterable[UnitRecord]) -> set[str]:
    return {record.unit.chapter for record in records if record.unit.chapter}


def _repair_blocks_with_glm(
    *,
    records: list[UnitRecord],
    glmocr_dir: Path | None,
    known_formula_ids: set[str],
    known_table_ids: set[str],
    auto_threshold: float,
    review_threshold: float,
    max_window_paragraphs: int,
    include_review: bool,
) -> tuple[Counter[str], list[dict[str, Any]], list[dict[str, Any]], Counter[str]]:
    stats: Counter[str] = Counter()
    repair_items: list[dict[str, Any]] = []
    manual_queue: list[dict[str, Any]] = []
    issue_counts: Counter[str] = Counter()

    glm_index: dict[str, GLMChapterIndex] = {}
    if glmocr_dir and glmocr_dir.exists():
        glm_index = load_glm_index(
            glmocr_dir,
            _record_chapters(records),
            max_window=max_window_paragraphs,
        )

    max_ordinal_by_chapter = _chapter_ordinals(records)
    for record in records:
        span_index = glm_index.get(record.unit.chapter) or GLMChapterIndex.build(record.unit.chapter, [])
        expected_order = expected_order_for_unit(
            unit_id=record.unit.id,
            chapter=record.unit.chapter,
            max_ordinal_by_chapter=max_ordinal_by_chapter,
            span_count=len(span_index.spans),
        )
        kept_blocks: list[KnowledgeBlock] = []
        for block_index, block in enumerate(record.unit.blocks):
            footer_stripped_content, footer_strip_reasons = _strip_leading_publication_footer_tail(block.content)
            if footer_stripped_content != block.content:
                stats["publication_footer_tail_stripped"] += 1
                repair_items.append(
                    {
                        "unit_id": record.unit.id,
                        "block_index": block_index,
                        "action": "strip_publication_footer_tail",
                        "reason_codes": footer_strip_reasons,
                        "content_before": block.content,
                        "content_after": footer_stripped_content,
                    }
                )
                block = KnowledgeBlock(type=block.type, content=footer_stripped_content)
            text_normalized_content, text_normalize_reasons = _normalize_latex_in_text(block.content)
            if text_normalized_content != block.content:
                stats["block_latex_text_normalized"] += 1
                repair_items.append(
                    {
                        "unit_id": record.unit.id,
                        "block_index": block_index,
                        "action": "normalize_latex_text",
                        "reason_codes": text_normalize_reasons,
                        "content_before": block.content,
                        "content_after": text_normalized_content,
                    }
                )
                block = KnowledgeBlock(type=block.type, content=text_normalized_content)
            normalized_content, float_marker = _strip_leading_float_marker(block.content)
            if float_marker:
                stats["leading_float_marker_stripped"] += 1
                repair_items.append(
                    {
                        "unit_id": record.unit.id,
                        "block_index": block_index,
                        "action": "strip_leading_float_marker",
                        "marker": float_marker,
                        "content_before": block.content,
                        "content_after": normalized_content,
                    }
                )
                block = KnowledgeBlock(type=block.type, content=normalized_content)

            issues = audit_block_content(
                content=block.content,
                block_type=block.type,
                known_formula_ids=known_formula_ids,
                known_table_ids=known_table_ids,
            )
            codes = _issue_codes(issues)
            issue_counts.update(codes)
            if _should_drop_block(issues):
                stats["blocks_removed"] += 1
                manual_queue.append(
                    {
                        "unit_id": record.unit.id,
                        "block_index": block_index,
                        "action": "auto_removed",
                        "issue_codes": codes,
                        "content": block.content,
                    }
                )
                continue

            repairable = sorted((set(codes) & REPAIR_ATTEMPT_ISSUES) - REFERENCE_ONLY_ISSUES)
            if repairable and span_index.spans:
                stats["glm_repair_attempted"] += 1
                item = build_candidate_for_block(
                    unit_id=record.unit.id,
                    chapter=record.unit.chapter,
                    block_index=block_index,
                    old_content=block.content,
                    issue_codes=repairable,
                    spans=span_index,
                    expected_order=expected_order,
                    auto_threshold=auto_threshold,
                    review_threshold=review_threshold,
                )
                repair_items.append(item)
                action = str(item.get("action") or "")
                if action == "auto_apply" or (include_review and action == "review"):
                    new_content = str(item.get("new_content") or "").strip()
                    if new_content and new_content != block.content:
                        block = KnowledgeBlock(type=block.type, content=new_content)
                        stats["glm_repair_applied"] += 1
                    else:
                        stats["glm_repair_noop"] += 1
                elif action == "review":
                    stats["glm_repair_review_queued"] += 1
                    manual_queue.append(item)
                else:
                    stats["glm_repair_rejected"] += 1
                    manual_queue.append(item)
            elif codes:
                manual_queue.append(
                    {
                        "unit_id": record.unit.id,
                        "block_index": block_index,
                        "action": "manual_queue",
                        "issue_codes": codes,
                        "content": block.content,
                    }
                )

            kept_blocks.append(block)

        if kept_blocks or not record.unit.blocks:
            record.unit.blocks = kept_blocks
        else:
            stats["units_with_only_noise_kept_original"] += 1

    return stats, repair_items, manual_queue, issue_counts


def _all_unit_text_by_label(records: Iterable[UnitRecord]) -> dict[str, list[str]]:
    mentions: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for block in record.unit.blocks:
            for label in _extract_table_refs_from_content(block.content):
                mentions[label].append(record.unit.id)
    return {label: sorted(set(unit_ids)) for label, unit_ids in mentions.items()}


def _table_entry_quality(entry: TableEntry) -> float:
    rows = entry.rows or []
    row_count = len(rows)
    cell_count = sum(len(row) for row in rows if isinstance(row, list))
    content_size = sum(len(str(cell)) for row in rows for cell in row)
    html_size = len(str(entry.html or ""))
    title_size = len(str(entry.title or ""))
    score = row_count * 20.0 + cell_count * 5.0 + min(240.0, content_size / 8.0)
    score += min(80.0, html_size / 60.0) + min(80.0, title_size / 6.0)
    if re.search(r"\bCell\s+1\b", str(entry.html or ""), flags=re.IGNORECASE):
        score -= 120.0
    return score


def _copy_table_entry(entry: TableEntry) -> TableEntry:
    return TableEntry(
        id=str(entry.id or "").strip(),
        label_format=str(entry.label_format or ""),
        title=str(entry.title or ""),
        table_type=str(entry.table_type or "numbered"),
        html=str(entry.html or ""),
        rows=[list(row) for row in (entry.rows or [])],
        source=dict(entry.source or {}),
        description=entry.description,
        raw_body=getattr(entry, "raw_body", None),
        markdown_body=getattr(entry, "markdown_body", None),
    )


def _recover_reference_tables(
    *,
    current_library: TableLibrary,
    records: list[UnitRecord],
    reference_structured_dir: Path | None,
    replace_weaker_tables: bool = False,
) -> tuple[TableLibrary, Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    if not reference_structured_dir:
        return current_library, stats, events

    reference_path = reference_structured_dir / "table_library.json"
    if not reference_path.exists():
        return current_library, stats, events

    reference_library = TableLibrary.load(str(reference_path))
    current_tables = list(current_library.tables)
    numbered_index_by_id: dict[str, int] = {}
    for index, entry in enumerate(current_tables):
        table_id = str(entry.id or "").strip()
        if _is_numbered_table_id(table_id) and table_id not in numbered_index_by_id:
            numbered_index_by_id[table_id] = index
    mentions_by_table = _all_unit_text_by_label(records)

    for reference_entry in reference_library.tables:
        table_id = str(reference_entry.id or "").strip()
        if not _is_numbered_table_id(table_id):
            continue

        current_index = numbered_index_by_id.get(table_id)
        current_entry = current_tables[current_index] if current_index is not None else None
        mentioned_units = mentions_by_table.get(table_id, [])
        if not mentioned_units:
            continue

        if current_entry is not None:
            if not replace_weaker_tables:
                continue
            if _table_entry_quality(reference_entry) <= _table_entry_quality(current_entry) + 20.0:
                continue
            stats["table_entries_replaced_with_reference"] += 1
        else:
            stats["table_entries_recovered_from_reference"] += 1

        recovered = _copy_table_entry(reference_entry)
        source = dict(recovered.source or {})
        source.setdefault("chapter", _chapter_from_table_id(table_id))
        source["recovered_from"] = str(reference_path)
        source["recovery_method"] = "reference_table_library_with_current_mentions"
        source["current_reference_units"] = mentioned_units[:20]
        recovered.source = source
        if current_index is not None:
            current_tables[current_index] = recovered
        else:
            numbered_index_by_id[table_id] = len(current_tables)
            current_tables.append(recovered)
        events.append(
            {
                "table_id": table_id,
                "action": "replace" if current_entry is not None else "recover",
                "mentioned_units": mentioned_units,
                "source_title": recovered.title,
                "reference_path": str(reference_path),
            }
        )

    current_library.tables = sorted(
        current_tables,
        key=lambda entry: (
            chapter_sort_key((entry.source or {}).get("chapter", "")),
            table_sort_key(entry.id),
            str(entry.id or "").lower(),
        ),
    )
    return current_library, stats, events


def _is_numbered_table_id(table_id: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+(?:\.\d+)?[A-Za-z]?", str(table_id or "").strip()))


def _chapter_from_table_id(table_id: str) -> str:
    match = re.match(r"^(\d+)\.", str(table_id or ""))
    if match:
        return f"chapter{int(match.group(1))}"
    return ""


def _table_evidence_quality(evidence: OCREvidence) -> float:
    caption_match = 1.0 if re.search(rf"\bTable\s+{re.escape(evidence.object_id)}\b", evidence.caption_text, re.IGNORECASE) else 0.0
    row_score = min(1.0, len(evidence.rows) / 3.0)
    body_token_count = len(normalize_match_text(evidence.body_text).split())
    body_score = min(1.0, body_token_count / 12.0)
    html_score = 1.0 if "<table" in str(evidence.body_html or "").lower() else 0.0
    return round(0.42 * caption_match + 0.28 * row_score + 0.22 * body_score + 0.08 * html_score, 4)


def _is_missing_table_stub(entry: TableEntry) -> bool:
    if str(entry.table_type or "").strip().lower() == "missing":
        return True
    source = entry.source if isinstance(entry.source, dict) else {}
    return str(source.get("extraction_channel") or "") == "missing_table_body_stub"


def _header_like_rows(rows: Iterable[Iterable[Any]]) -> list[list[str]]:
    header_rows: list[list[str]] = []
    for raw_row in list(rows or [])[:4]:
        row = [str(cell or "").strip() for cell in raw_row]
        nonempty = [cell for cell in row if cell]
        if header_rows and nonempty and sum(1 for cell in nonempty if re.fullmatch(r"\$?\s*-?\d+(?:\.\d+)?\s*\$?", cell)) >= max(1, len(nonempty) // 2):
            break
        header_rows.append(row)
    return header_rows


def _latex_math_tokens(text: str) -> set[str]:
    raw = str(text or "")
    tokens: set[str] = set()
    for match in re.finditer(r"\\[A-Za-z]+(?:_\{[^}]+\}|_[A-Za-z0-9]+)?(?:\^\{[^}]+\}|\^[A-Za-z0-9]+)?", raw):
        token = re.sub(r"[^A-Za-z0-9]+", "", match.group(0)).lower()
        if len(token) >= 4:
            tokens.add(token)
    return tokens


def _data_rows_text(rows: Iterable[Iterable[Any]]) -> str:
    header_count = len(_header_like_rows(rows))
    data_rows = list(rows or [])[header_count:]
    return collapse_ws(" ".join(" ".join(str(cell or "") for cell in row) for row in data_rows))


def _evidence_has_stronger_grouped_math_header(entry: TableEntry, evidence: OCREvidence, score: dict[str, Any]) -> bool:
    if float(score.get("id", 0.0)) < 1.0 or float(score.get("caption", 0.0)) < 0.65:
        return False
    if str(entry.table_type or "").strip().lower() != str(table_entry_from_evidence(evidence).table_type or "").strip().lower():
        return False
    entry_headers = _header_like_rows(entry.rows or [])
    evidence_headers = _header_like_rows(evidence.rows or [])
    if len(entry_headers) < 1 or len(evidence_headers) < 2:
        return False
    entry_header_text = collapse_ws(" ".join(" ".join(row) for row in entry_headers))
    evidence_header_text = collapse_ws(" ".join(" ".join(row) for row in evidence_headers))
    entry_tokens = _latex_math_tokens(entry_header_text)
    evidence_tokens = _latex_math_tokens(evidence_header_text)
    caption_tokens = _latex_math_tokens(f"{entry.title or ''} {evidence.caption_text or ''}")
    missing_caption_tokens = (evidence_tokens - entry_tokens) & caption_tokens
    if not missing_caption_tokens:
        return False
    entry_data = _data_rows_text(entry.rows or [])
    evidence_data = _data_rows_text(evidence.rows or [])
    if not entry_data or not evidence_data:
        return False
    data_overlap = score_table_evidence_pair(
        OCREvidence("table", str(entry.id or ""), "", "structured", "", None, 0.0, body_text=entry_data),
        OCREvidence("table", evidence.object_id, "", evidence.source_channel, "", None, 0.0, body_text=evidence_data),
    )
    return float(data_overlap.get("body_token", 0.0)) >= 0.82


def _strip_math_dollars(value: str) -> str:
    stripped = str(value or "").strip()
    stripped = re.sub(r"^\$+\s*", "", stripped)
    stripped = re.sub(r"\s*\$+$", "", stripped)
    return stripped.strip()


def _coefficient_group_variable(group_label: str) -> str | None:
    match = re.search(r"Coefficient\s+on\s+(.+?)\s+for\s+\$?\s*j\s*=", str(group_label or ""), flags=re.IGNORECASE)
    if not match:
        return None
    variable = match.group(1).strip()
    if not variable.startswith("$"):
        variable = f"$ {variable} $"
    return collapse_ws(variable)


def _normalize_grouped_header_prefix_cell(value: str) -> str:
    stripped = str(value or "").strip()
    if stripped.startswith("$") and not stripped.endswith("$"):
        return _strip_math_dollars(stripped)
    return stripped


def _flatten_grouped_header_rows(rows: Iterable[Iterable[Any]]) -> list[list[str]]:
    normalized = [[str(cell or "").strip() for cell in row] for row in rows or []]
    if len(normalized) < 3 or len(normalized[1]) < 3:
        return normalized
    first, second = normalized[0], normalized[1]
    group_labels = [cell for cell in first if cell.strip()]
    if len(group_labels) != 1:
        return normalized
    variable = _coefficient_group_variable(group_labels[0])
    if not variable:
        return normalized
    prefix_count = max(0, len(second) - (len(normalized[2]) - 2 if len(normalized[2]) >= 3 else len(second)))
    prefix_count = min(max(prefix_count, 2), len(second))
    header = [_normalize_grouped_header_prefix_cell(cell) for cell in second[:prefix_count]]
    for cell in second[prefix_count:]:
        subheader = _strip_math_dollars(cell)
        if subheader:
            header.append(f"{variable}, $ j={subheader} $")
        else:
            header.append(variable)
    if len(header) != len(normalized[2]):
        return normalized
    return [header, *normalized[2:]]


def _table_entry_from_grouped_header_evidence(evidence: OCREvidence) -> TableEntry:
    replacement = table_entry_from_evidence(evidence)
    replacement.rows = _flatten_grouped_header_rows(replacement.rows or [])
    return replacement


def _best_grouped_header_evidence(
    entry: TableEntry,
    scored_evidences: list[tuple[OCREvidence, float, dict[str, Any]]],
) -> tuple[OCREvidence, float, dict[str, Any]] | None:
    candidates = [
        (evidence, quality, score)
        for evidence, quality, score in scored_evidences
        if _evidence_has_stronger_grouped_math_header(entry, evidence, score)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[1], 1 if item[0].source_channel == "glm" else 0, item[2]["overall"]))


def _is_stronger_ocr_table_evidence(entry: TableEntry, evidence: OCREvidence, score: dict[str, Any]) -> bool:
    if str(entry.table_type or "").strip().lower() != str(table_entry_from_evidence(evidence).table_type or "").strip().lower():
        return False
    if float(score.get("id", 0.0)) < 1.0 or float(score.get("caption", 0.0)) < 0.65:
        return False
    entry_rows = entry.rows or []
    evidence_rows = list(evidence.rows or [])
    if len(evidence_rows) >= len(entry_rows) + 2:
        return True
    entry_body = table_body_text(entry)
    evidence_body = table_body_text(evidence.body_html, evidence.rows)
    entry_tokens = set(normalize_match_text(entry_body).split())
    evidence_tokens = set(normalize_match_text(evidence_body).split())
    if not entry_tokens or not evidence_tokens:
        return False
    coverage = len(entry_tokens & evidence_tokens) / len(entry_tokens)
    growth = len(evidence_tokens - entry_tokens) / max(1, len(entry_tokens))
    return coverage >= 0.72 and growth >= 0.35


def _best_evidence_by_channel(evidences: Iterable[OCREvidence]) -> dict[str, OCREvidence]:
    best: dict[str, OCREvidence] = {}
    for evidence in evidences:
        current = best.get(evidence.source_channel)
        if current is None or _table_evidence_quality(evidence) > _table_evidence_quality(current):
            best[evidence.source_channel] = evidence
    return best


def _table_replacement_candidate_payload(
    *,
    entry: TableEntry,
    evidence: OCREvidence,
    score: dict[str, Any],
    agreed_with: OCREvidence | None = None,
) -> dict[str, Any]:
    replacement = table_entry_from_evidence(evidence)
    return {
        "table_id": str(entry.id or "").strip(),
        "candidate_entry": replacement.to_dict(),
        "source_evidence": evidence_to_dict(evidence),
        "agreed_evidence": evidence_to_dict(agreed_with) if agreed_with else None,
        "structured_entry_hash": table_entry_hash(entry),
        "candidate_entry_hash": table_entry_hash(replacement),
        "structured_score": score,
    }


def _evidence_order_key(evidence: OCREvidence) -> tuple[int, float, int]:
    page = evidence.page if evidence.page is not None else 10**9
    try:
        order = float(evidence.order)
    except (TypeError, ValueError):
        order = 10**9
    channel_rank = 0 if evidence.source_channel in {"paddle_visual", "paddle"} else 1
    return int(page), order, channel_rank


def _best_physical_table_evidence(evidences: list[OCREvidence]) -> OCREvidence | None:
    physical = [
        evidence
        for evidence in evidences
        if evidence.page is not None and (evidence.bbox is not None or evidence.source_channel in {"paddle_visual", "paddle"})
    ]
    if not physical:
        return None
    def score(evidence: OCREvidence) -> tuple[int, int, int, tuple[int, float, int]]:
        payload = evidence.source_payload if isinstance(evidence.source_payload, dict) else {}
        has_following = 1 if isinstance(payload.get("following_body"), dict) else 0
        channel_rank = 2 if evidence.source_channel == "paddle_visual" else 1 if evidence.source_channel == "paddle" else 0
        has_bbox = 1 if evidence.bbox is not None else 0
        return has_following, channel_rank, has_bbox, tuple(-part if isinstance(part, int) else -part for part in _evidence_order_key(evidence))

    return max(physical, key=score)


def _audit_ocr_table_bindings(
    *,
    table_library: TableLibrary,
    ocr_evidence_index: OCREvidenceIndex,
    auto_apply_replacements: bool,
) -> tuple[TableLibrary, Counter[str], list[dict[str, Any]], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    manual_queue: list[dict[str, Any]] = []
    updated_tables = list(table_library.tables)

    for index, entry in enumerate(list(updated_tables)):
        table_id = str(entry.id or "").strip()
        if not _is_numbered_table_id(table_id):
            continue

        issue_codes: list[str] = []
        caption_label = table_entry_caption_label(entry)
        if caption_label and caption_label != table_id:
            issue_codes.append("table_binding_mismatch")
        elif str(entry.title or "").strip() and not table_entry_has_own_caption(entry):
            issue_codes.append("table_binding_mismatch")

        chapter = _chapter_from_table_id(table_id)
        evidences = ocr_evidence_index.tables(table_id=table_id, chapter=chapter)
        if not evidences and not chapter:
            evidences = ocr_evidence_index.tables(table_id=table_id)

        scored_evidences: list[tuple[OCREvidence, float, dict[str, Any]]] = []
        for evidence in evidences:
            if len(table_body_text(evidence.body_html, evidence.rows)) < TABLE_EVIDENCE_MIN_BODY_CHARS:
                continue
            quality = _table_evidence_quality(evidence)
            score = score_table_entry_against_evidence(entry, evidence)
            scored_evidences.append((evidence, quality, score))

        scored_evidences.sort(key=lambda item: (item[1], item[2]["overall"]), reverse=True)
        physical_evidence = _best_physical_table_evidence([evidence for evidence, _quality, _score in scored_evidences])
        if physical_evidence is not None:
            source = dict(entry.source or {})
            old_page = source.get("page")
            old_order = source.get("table_order")
            source["page"] = physical_evidence.page
            source["table_order"] = physical_evidence.order
            if physical_evidence.bbox is not None:
                source["bbox"] = physical_evidence.bbox
            payload = physical_evidence.source_payload if isinstance(physical_evidence.source_payload, dict) else {}
            if payload.get("caption_bbox") is not None:
                source["caption_bbox"] = payload.get("caption_bbox")
            if isinstance(payload.get("preceding_body"), dict):
                source["preceding_body"] = payload.get("preceding_body")
            if isinstance(payload.get("following_body"), dict):
                source["following_body"] = payload.get("following_body")
            source["physical_evidence_channel"] = physical_evidence.source_channel
            source["physical_evidence_path"] = physical_evidence.source_path
            source["physical_evidence_hash"] = physical_evidence.stable_hash()
            if old_page != source.get("page") or old_order != source.get("table_order"):
                source["fusion_repair_physical_source"] = "ocr_physical_table_evidence"
                stats["table_physical_source_rebound"] += 1
            entry.source = source
        best_structured_score = scored_evidences[0][2] if scored_evidences else {}
        if _is_missing_table_stub(entry) and scored_evidences and scored_evidences[0][1] >= TABLE_EVIDENCE_STRONG_QUALITY:
            primary_evidence = scored_evidences[0][0]
            replacement = table_entry_from_evidence(primary_evidence)
            original_source = entry.source if isinstance(entry.source, dict) else {}
            source = dict(replacement.source or {})
            for key in ("unit_id", "subsection", "has_physical_placeholder"):
                if original_source.get(key) is not None:
                    source[key] = original_source.get(key)
            source["fusion_repair"] = "missing_stub_recovered_from_ocr_table_evidence"
            source["original_entry_hash"] = table_entry_hash(entry)
            source["structured_score"] = best_structured_score
            replacement.source = source
            updated_tables[index] = replacement
            stats["missing_table_stub_recovered"] += 1
            events.append(
                {
                    "severity": "info",
                    "issue_codes": ["missing_table_stub_recovered"],
                    "table_id": table_id,
                    "chapter": chapter,
                    "action": "auto_replace_applied",
                    "caption_label": table_entry_caption_label(replacement),
                    "structured_title": str(entry.title or ""),
                    "structured_entry_hash": table_entry_hash(entry),
                    "structured_body_text": table_body_text(entry)[:600],
                    "best_structured_score": best_structured_score,
                    "channel_agreement": None,
                    "evidence_candidates": [
                        {
                            "quality": quality,
                            "structured_score": score,
                            "evidence": evidence_to_dict(evidence),
                        }
                        for evidence, quality, score in scored_evidences[:4]
                    ],
                    "replacement_candidate": _table_replacement_candidate_payload(
                        entry=entry,
                        evidence=primary_evidence,
                        score=score_table_entry_against_evidence(entry, primary_evidence),
                    ),
                }
            )
            continue
        grouped_header_evidence = _best_grouped_header_evidence(entry, scored_evidences)
        if auto_apply_replacements and grouped_header_evidence and grouped_header_evidence[1] >= TABLE_EVIDENCE_STRONG_QUALITY:
            primary_evidence, _quality, header_score = grouped_header_evidence
            replacement = _table_entry_from_grouped_header_evidence(primary_evidence)
            original_source = entry.source if isinstance(entry.source, dict) else {}
            source = dict(replacement.source or {})
            for key in ("unit_id", "subsection", "has_physical_placeholder"):
                if original_source.get(key) is not None:
                    source[key] = original_source.get(key)
            source["fusion_repair"] = "stronger_ocr_grouped_math_header"
            source["original_entry_hash"] = table_entry_hash(entry)
            source["structured_score"] = header_score
            replacement.source = source
            updated_tables[index] = replacement
            stats["stronger_ocr_grouped_header_replacements_applied"] += 1
            events.append(
                {
                    "severity": "info",
                    "issue_codes": ["stronger_ocr_grouped_math_header"],
                    "table_id": table_id,
                    "chapter": chapter,
                    "action": "auto_replace_applied",
                    "caption_label": table_entry_caption_label(replacement),
                    "structured_title": str(entry.title or ""),
                    "structured_entry_hash": table_entry_hash(entry),
                    "structured_body_text": table_body_text(entry)[:600],
                    "best_structured_score": best_structured_score,
                    "channel_agreement": None,
                    "evidence_candidates": [
                        {
                            "quality": quality,
                            "structured_score": score,
                            "evidence": evidence_to_dict(evidence),
                        }
                        for evidence, quality, score in scored_evidences[:4]
                    ],
                    "replacement_candidate": _table_replacement_candidate_payload(
                        entry=entry,
                        evidence=primary_evidence,
                        score=score_table_entry_against_evidence(entry, primary_evidence),
                    ),
                }
            )
            continue
        if (
            auto_apply_replacements
            and scored_evidences
            and scored_evidences[0][1] >= TABLE_EVIDENCE_STRONG_QUALITY
            and _is_stronger_ocr_table_evidence(entry, scored_evidences[0][0], best_structured_score)
        ):
            primary_evidence = scored_evidences[0][0]
            replacement = table_entry_from_evidence(primary_evidence)
            original_source = entry.source if isinstance(entry.source, dict) else {}
            source = dict(replacement.source or {})
            for key in ("unit_id", "subsection", "has_physical_placeholder"):
                if original_source.get(key) is not None:
                    source[key] = original_source.get(key)
            source["fusion_repair"] = "stronger_ocr_table_evidence"
            source["original_entry_hash"] = table_entry_hash(entry)
            source["structured_score"] = best_structured_score
            replacement.source = source
            updated_tables[index] = replacement
            stats["stronger_ocr_table_replacements_applied"] += 1
            events.append(
                {
                    "severity": "info",
                    "issue_codes": ["stronger_ocr_table_evidence"],
                    "table_id": table_id,
                    "chapter": chapter,
                    "action": "auto_replace_applied",
                    "caption_label": table_entry_caption_label(replacement),
                    "structured_title": str(entry.title or ""),
                    "structured_entry_hash": table_entry_hash(entry),
                    "structured_body_text": table_body_text(entry)[:600],
                    "best_structured_score": best_structured_score,
                    "channel_agreement": None,
                    "evidence_candidates": [
                        {
                            "quality": quality,
                            "structured_score": score,
                            "evidence": evidence_to_dict(evidence),
                        }
                        for evidence, quality, score in scored_evidences[:4]
                    ],
                    "replacement_candidate": _table_replacement_candidate_payload(
                        entry=entry,
                        evidence=primary_evidence,
                        score=score_table_entry_against_evidence(entry, primary_evidence),
                    ),
                }
            )
            continue
        if scored_evidences and float(best_structured_score.get("overall", 1.0)) < TABLE_STRUCTURED_CONFLICT_SCORE:
            issue_codes.append("cross_channel_table_conflict")
            if "table_binding_mismatch" not in issue_codes:
                issue_codes.append("table_binding_mismatch")

        by_channel = _best_evidence_by_channel(evidence for evidence, quality, _score in scored_evidences if quality >= TABLE_EVIDENCE_STRONG_QUALITY)
        channel_agreement: dict[str, Any] | None = None
        agreed_pair: tuple[OCREvidence, OCREvidence] | None = None
        if "paddle" in by_channel and "glm" in by_channel:
            channel_agreement = score_table_evidence_pair(by_channel["paddle"], by_channel["glm"])
            if float(channel_agreement.get("overall", 0.0)) >= TABLE_CHANNEL_AGREEMENT_SCORE:
                agreed_pair = (by_channel["paddle"], by_channel["glm"])
            elif float(channel_agreement.get("overall", 1.0)) < TABLE_CHANNEL_CONFLICT_SCORE:
                issue_codes.append("cross_channel_table_conflict")

        replacement_payload: dict[str, Any] | None = None
        replacement_action = ""
        if issue_codes and scored_evidences:
            primary_evidence = scored_evidences[0][0]
            agreed_with = None
            if agreed_pair:
                primary_evidence = max(agreed_pair, key=_table_evidence_quality)
                agreed_with = agreed_pair[0] if primary_evidence is agreed_pair[1] else agreed_pair[1]
                replacement_action = "auto_replace"
            elif scored_evidences[0][1] >= TABLE_EVIDENCE_STRONG_QUALITY:
                if (
                    auto_apply_replacements
                    and float(best_structured_score.get("id", 0.0)) >= 1.0
                    and float(best_structured_score.get("caption", 0.0)) >= 0.65
                    and float(best_structured_score.get("body", 1.0)) < 0.45
                ):
                    replacement_action = "auto_replace"
                else:
                    replacement_action = "manual_review"

            if replacement_action:
                replacement_payload = _table_replacement_candidate_payload(
                    entry=entry,
                    evidence=primary_evidence,
                    agreed_with=agreed_with,
                    score=score_table_entry_against_evidence(entry, primary_evidence),
                )

        if not issue_codes:
            continue

        issue_codes = sorted(set(issue_codes))
        severity = "fatal" if "table_binding_mismatch" in issue_codes else "error"
        event = {
            "severity": severity,
            "issue_codes": issue_codes,
            "table_id": table_id,
            "chapter": chapter,
            "action": replacement_action or "manual_review",
            "caption_label": caption_label,
            "structured_title": str(entry.title or ""),
            "structured_entry_hash": table_entry_hash(entry),
            "structured_body_text": table_body_text(entry)[:600],
            "best_structured_score": best_structured_score,
            "channel_agreement": channel_agreement,
            "evidence_candidates": [
                {
                    "quality": quality,
                    "structured_score": score,
                    "evidence": evidence_to_dict(evidence),
                }
                for evidence, quality, score in scored_evidences[:4]
            ],
            "replacement_candidate": replacement_payload,
        }

        if replacement_action == "auto_replace" and replacement_payload and auto_apply_replacements:
            replacement = TableEntry(**replacement_payload["candidate_entry"])
            original_source = entry.source if isinstance(entry.source, dict) else {}
            source = dict(replacement.source or {})
            for key in ("unit_id", "subsection", "has_physical_placeholder"):
                if original_source.get(key) is not None:
                    source[key] = original_source.get(key)
            source["fusion_repair"] = "ocr_table_evidence_binding"
            source["source_channels"] = sorted({candidate["evidence"]["source_channel"] for candidate in event["evidence_candidates"]})
            source["matching"] = {
                "best_structured_score": best_structured_score,
                "channel_agreement": channel_agreement,
            }
            source["original_entry_hash"] = table_entry_hash(entry)
            replacement.source = source
            updated_tables[index] = replacement
            event["action"] = "auto_replace_applied"
            stats["table_binding_replacements_applied"] += 1
        else:
            manual_queue.append(
                {
                    "scope": "table_binding",
                    "table_id": table_id,
                    "action": event["action"],
                    "issue_codes": issue_codes,
                    "severity": severity,
                    "replacement_candidate": replacement_payload,
                }
            )

        for issue_code in issue_codes:
            stats[issue_code] += 1
        if replacement_payload:
            stats["table_replacement_candidates"] += 1
        events.append(event)

    table_library.tables = sorted(
        updated_tables,
        key=lambda entry: (
            chapter_sort_key((entry.source or {}).get("chapter", "")),
            table_sort_key(entry.id),
            str(entry.id or "").lower(),
        ),
    )
    return table_library, stats, events, manual_queue


def _table_text_anchor(entry: TableEntry) -> str:
    rows = entry.rows or []
    cells = [str(cell) for row in rows for cell in row if str(cell).strip()]
    return " ".join(cells[: min(len(cells), 8)]).strip()


def _find_token_subsequence(values: list[str], needle: list[str]) -> int | None:
    if not needle or len(needle) > len(values):
        return None
    for pos in range(0, len(values) - len(needle) + 1):
        if values[pos : pos + len(needle)] == needle:
            return pos
    return None


def _content_token_spans(content: str) -> list[tuple[str, int, int]]:
    return [
        (match.group(0).lower(), match.start(), match.end())
        for match in re.finditer(r"[0-9A-Za-z]+", content or "")
    ]


def _fuzzy_token_match_end(
    values: list[str],
    needle: list[str],
    *,
    start: int,
    min_needle_tokens: int,
) -> int | None:
    """Return the exclusive value-token end for a compact token match.

    OCR/LaTeX cleanup sometimes turns a normalized table token sequence like
    ``2 n e s`` into structured text tokens such as ``2n e s``.  Table-body
    residue detection should survive those harmless joins without treating a
    mere prose mention as the table body.
    """

    if not needle or start >= len(values):
        return None
    matched_needle = 0
    value_index = start
    while matched_needle < len(needle) and value_index < len(values):
        value = values[value_index]
        current = needle[matched_needle]
        if value == current:
            matched_needle += 1
            value_index += 1
            continue

        compact = ""
        compact_index = matched_needle
        while compact_index < len(needle) and len(compact) < len(value):
            compact += needle[compact_index]
            compact_index += 1
            if compact == value:
                matched_needle = compact_index
                value_index += 1
                break
        else:
            break

    if matched_needle >= min_needle_tokens:
        return value_index
    return None


def _find_fuzzy_token_span(
    values: list[str],
    needle: list[str],
    *,
    start_token: int = 0,
    min_needle_tokens: int | None = None,
) -> tuple[int, int] | None:
    if not needle:
        return None
    min_tokens = min_needle_tokens if min_needle_tokens is not None else len(needle)
    min_tokens = max(1, min(min_tokens, len(needle)))
    for pos in range(max(0, start_token), len(values)):
        end = _fuzzy_token_match_end(values, needle, start=pos, min_needle_tokens=min_tokens)
        if end is not None:
            return pos, end
    return None


def _record_matching_anchor(
    *,
    records: list[UnitRecord],
    chapter: str,
    anchor_text: str,
) -> UnitRecord | None:
    anchor_tokens = normalize_match_text(anchor_text).split()
    if len(anchor_tokens) < 3:
        return None
    anchor = anchor_tokens[: min(16, len(anchor_tokens))]
    for record in records:
        if chapter and record.unit.chapter != chapter:
            continue
        heading_texts = [
            record.unit.section,
            record.unit.section_level_1 or "",
            record.unit.section_level_2 or "",
            record.unit.display_heading or "",
            *record.unit.subsections,
            *record.unit.heading_path,
        ]
        for heading_text in heading_texts:
            heading_tokens = normalize_match_text(heading_text).split()
            if heading_tokens and _find_token_subsequence(heading_tokens, anchor) is not None:
                return record
            if len(heading_tokens) >= 3 and _find_token_subsequence(anchor_tokens, heading_tokens[: min(16, len(heading_tokens))]) is not None:
                return record
        if len(anchor_tokens) < 6:
            continue
        for block in record.unit.blocks:
            block_tokens = normalize_match_text(block.content).split()
            if _find_token_subsequence(block_tokens, anchor) is not None:
                return record
    return None


def _physical_owner_record_for_table(
    *,
    records: list[UnitRecord],
    table_entry: TableEntry,
) -> tuple[UnitRecord | None, str]:
    physical_record = _first_record_after_table_evidence(records=records, table_entry=table_entry)
    if physical_record is not None:
        return physical_record, "structured_fusion_table_following_body_anchor"
    source = table_entry.source if isinstance(table_entry.source, dict) else {}
    if not _table_is_page_top_float(source):
        return None, ""
    physical_record = _record_before_table_evidence(records=records, table_entry=table_entry)
    if physical_record is not None:
        return physical_record, "structured_fusion_table_preceding_body_anchor"
    physical_record = _record_before_following_heading(records=records, table_entry=table_entry)
    if physical_record is not None:
        return physical_record, "structured_fusion_table_before_following_heading"
    return None, ""


def _table_is_page_top_float(source: dict[str, Any]) -> bool:
    caption_bbox = source.get("caption_bbox") if isinstance(source.get("caption_bbox"), list) else None
    table_bbox = source.get("bbox") if isinstance(source.get("bbox"), list) else None
    try:
        top = float(caption_bbox[1] if caption_bbox and len(caption_bbox) >= 2 else table_bbox[1])
    except (TypeError, ValueError, IndexError):
        return False
    return top <= 260


def _first_record_after_table_evidence(
    *,
    records: list[UnitRecord],
    table_entry: TableEntry,
) -> UnitRecord | None:
    source = table_entry.source if isinstance(table_entry.source, dict) else {}
    if str(table_entry.table_type or "").strip().lower() == "formula_table":
        return None
    following_body = source.get("following_body") if isinstance(source.get("following_body"), dict) else None
    following_label = str((following_body or {}).get("label") or "").strip().lower()
    if following_label == "paragraph_title" and _table_is_page_top_float(source):
        return None
    chapter = str(source.get("chapter") or _chapter_from_table_id(str(table_entry.id or ""))).strip().lower()
    return _record_matching_anchor(
        records=records,
        chapter=chapter,
        anchor_text=str((following_body or {}).get("content") or ""),
    )


def _record_before_table_evidence(
    *,
    records: list[UnitRecord],
    table_entry: TableEntry,
) -> UnitRecord | None:
    source = table_entry.source if isinstance(table_entry.source, dict) else {}
    preceding_body = source.get("preceding_body") if isinstance(source.get("preceding_body"), dict) else None
    if not preceding_body:
        return None
    chapter = str(source.get("chapter") or _chapter_from_table_id(str(table_entry.id or ""))).strip().lower()
    return _record_matching_anchor(
        records=records,
        chapter=chapter,
        anchor_text=str(preceding_body.get("content") or ""),
    )


def _record_before_following_heading(
    *,
    records: list[UnitRecord],
    table_entry: TableEntry,
) -> UnitRecord | None:
    source = table_entry.source if isinstance(table_entry.source, dict) else {}
    following_body = source.get("following_body") if isinstance(source.get("following_body"), dict) else None
    following_label = str((following_body or {}).get("label") or "").strip().lower()
    if following_label != "paragraph_title" or not _table_is_page_top_float(source):
        return None
    chapter = str(source.get("chapter") or _chapter_from_table_id(str(table_entry.id or ""))).strip().lower()
    following_record = _record_matching_anchor(
        records=records,
        chapter=chapter,
        anchor_text=str((following_body or {}).get("content") or ""),
    )
    if following_record is None:
        return None
    previous: UnitRecord | None = None
    for record in records:
        if chapter and record.unit.chapter != chapter:
            continue
        if record is following_record:
            return previous
        previous = record
    return None


def _materialize_list_tables_in_units(
    *,
    records: list[UnitRecord],
    table_library: TableLibrary,
) -> tuple[Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    records_by_unit = {record.unit.id: record for record in records}
    for entry in table_library.tables:
        if str(entry.table_type or "").strip().lower() != "list_table":
            continue
        source = entry.source if isinstance(entry.source, dict) else {}
        unit_id = str(source.get("unit_id") or "").strip()
        physical_record, owner_reason = _physical_owner_record_for_table(records=records, table_entry=entry)
        if physical_record is not None:
            unit_id = physical_record.unit.id
            source = {
                **source,
                "unit_id": physical_record.unit.id,
                "chapter": physical_record.unit.chapter,
                "subsection": physical_record.unit.subsections[-1] if physical_record.unit.subsections else source.get("subsection"),
                "physical_owner_rebound_by": owner_reason,
            }
            entry.source = source
        record = records_by_unit.get(unit_id)
        table_id = str(entry.id or "").strip()
        if not record or not table_id:
            continue
        placeholder = f"[[TABLE:{table_id}]]"
        if any(placeholder in block.content for block in record.unit.blocks):
            continue
        for block_index, block in enumerate(record.unit.blocks):
            token_spans = _content_token_spans(block.content)
            values = [token for token, _, _ in token_spans]
            if not values:
                continue
            first_row_tokens = normalize_match_text(" ".join(str(cell) for cell in (entry.rows or [[""]])[0])).split()
            if not first_row_tokens:
                continue
            first_span = _find_fuzzy_token_span(
                values,
                first_row_tokens,
                min_needle_tokens=min(6, len(first_row_tokens)),
            )
            if first_span is None:
                continue
            start_token, first_end_token = first_span
            end_token = first_end_token - 1
            cursor = first_end_token
            matched_rows = 1
            for row in (entry.rows or [])[1:]:
                row_tokens = normalize_match_text(" ".join(str(cell) for cell in row)).split()
                if len(row_tokens) < 3:
                    continue
                row_span = _find_fuzzy_token_span(
                    values,
                    row_tokens,
                    start_token=cursor,
                    min_needle_tokens=min(6, len(row_tokens)),
                )
                if row_span is None:
                    continue
                matched_rows += 1
                cursor = row_span[1]
                end_token = row_span[1] - 1
            if len(entry.rows or []) >= 3 and matched_rows < 3:
                continue
            following_body = source.get("following_body") if isinstance(source.get("following_body"), dict) else None
            following_tokens = normalize_match_text(str((following_body or {}).get("content") or "")).split()
            if following_tokens:
                following_span = _find_fuzzy_token_span(
                    values,
                    following_tokens[: min(16, len(following_tokens))],
                    start_token=end_token + 1,
                    min_needle_tokens=min(8, len(following_tokens)),
                )
                if following_span is not None:
                    end_token = following_span[0] - 1
            start_char = token_spans[start_token][1]
            end_char = token_spans[end_token][2]
            while end_char < len(block.content) and block.content[end_char] in ".;:,":
                end_char += 1
            prefix = block.content[:start_char].strip()
            suffix = block.content[end_char:].strip()
            new_blocks: list[KnowledgeBlock] = []
            if prefix and normalize_match_text(prefix):
                new_blocks.append(KnowledgeBlock(type=block.type, content=prefix))
            placeholder_offset = len(new_blocks)
            new_blocks.append(KnowledgeBlock(type="table", content=placeholder))
            if suffix and normalize_match_text(suffix):
                new_blocks.append(KnowledgeBlock(type=block.type, content=suffix))
            record.unit.blocks = [
                *record.unit.blocks[:block_index],
                *new_blocks,
                *record.unit.blocks[block_index + 1 :],
            ]
            source = dict(source)
            source["has_physical_placeholder"] = True
            source["physical_placeholder_inserted_by"] = "structured_fusion_list_table_materializer"
            source["physical_placeholder_block_index"] = block_index + placeholder_offset
            entry.source = source
            stats["list_table_placeholders_inserted"] += 1
            events.append(
                {
                    "table_id": table_id,
                    "unit_id": record.unit.id,
                    "action": "insert_list_table_placeholder",
                    "block_index": block_index,
                    "matched_rows": matched_rows,
                }
            )
            break
    return stats, events


def _materialize_numbered_tables_in_units(
    *,
    records: list[UnitRecord],
    table_library: TableLibrary,
) -> tuple[Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    records_by_unit = {record.unit.id: record for record in records}
    physical_table_locations: dict[str, tuple[UnitRecord, int]] = {}
    demoted_table_locations: dict[str, UnitRecord] = {}

    def remove_or_demote_physical_placeholder(record: UnitRecord, table_id: str) -> int:
        placeholder = f"[[TABLE:{table_id}]]"
        see_placeholder = f"[[SEE_TABLE:{table_id}]]"
        removed = 0
        kept_blocks: list[KnowledgeBlock] = []
        for block in record.unit.blocks:
            if block.type == "table" and block.content.strip() == placeholder:
                removed += 1
                continue
            if placeholder in block.content:
                new_content = block.content.replace(placeholder, see_placeholder)
                if new_content != block.content:
                    removed += 1
                    block = KnowledgeBlock(type=block.type, content=new_content)
            kept_blocks.append(block)
        if removed:
            record.unit.blocks = kept_blocks
        return removed

    def append_physical_placeholder(record: UnitRecord, table_id: str) -> int:
        placeholder = f"[[TABLE:{table_id}]]"
        record.unit.blocks.append(KnowledgeBlock(type="table", content=placeholder))
        return len(record.unit.blocks) - 1

    def table_location_is_unit_end(location: tuple[UnitRecord, int]) -> bool:
        location_record, location_block_index = location
        return location_block_index == len(location_record.unit.blocks) - 1

    for record in records:
        block_index = 0
        while block_index < len(record.unit.blocks):
            block = record.unit.blocks[block_index]
            matches = list(PHYSICAL_TABLE_PLACEHOLDER_RE.finditer(block.content))
            if not matches:
                block_index += 1
                continue
            if block.type == "table" and len(matches) == 1 and block.content.strip() == matches[0].group(0):
                table_id = matches[0].group(1).strip()
                physical_table_locations.setdefault(table_id, (record, block_index))
                block_index += 1
                continue
            if block.content.strip() in {match.group(0) for match in matches}:
                table_id = matches[0].group(1).strip()
                record.unit.blocks[block_index] = KnowledgeBlock(type="table", content=f"[[TABLE:{table_id}]]")
                physical_table_locations.setdefault(table_id, (record, block_index))
                stats["standalone_table_placeholders_typed"] += 1
                block_index += 1
                continue
            if block.type != "table":
                new_content = block.content
                for match in matches:
                    table_id = match.group(1).strip()
                    new_content = new_content.replace(match.group(0), f"[[SEE_TABLE:{table_id}]]")
                    demoted_table_locations.setdefault(table_id, record)
                record.unit.blocks[block_index] = KnowledgeBlock(type=block.type, content=new_content)
                stats["embedded_table_placeholders_demoted_to_see_refs"] += 1
                events.append(
                    {
                        "unit_id": record.unit.id,
                        "action": "demote_embedded_table_placeholder_to_see_ref",
                        "block_index": block_index,
                    }
                )
                block_index += 1
                continue
            new_blocks: list[KnowledgeBlock] = []
            cursor = 0
            for match in matches:
                prefix = block.content[cursor : match.start()].strip()
                if prefix:
                    new_blocks.append(KnowledgeBlock(type=block.type, content=prefix))
                table_id = match.group(1).strip()
                new_blocks.append(KnowledgeBlock(type="table", content=f"[[TABLE:{table_id}]]"))
                cursor = match.end()
            suffix = block.content[cursor:].strip()
            if suffix:
                new_blocks.append(KnowledgeBlock(type=block.type, content=suffix))
            record.unit.blocks = [
                *record.unit.blocks[:block_index],
                *new_blocks,
                *record.unit.blocks[block_index + 1 :],
            ]
            for offset, new_block in enumerate(new_blocks):
                table_match = PHYSICAL_TABLE_PLACEHOLDER_RE.fullmatch(new_block.content.strip())
                if new_block.type == "table" and table_match:
                    physical_table_locations.setdefault(table_match.group(1).strip(), (record, block_index + offset))
            stats["embedded_table_placeholders_split"] += 1
            events.append(
                {
                    "unit_id": record.unit.id,
                    "action": "split_embedded_table_placeholder",
                    "block_index": block_index,
                }
            )
            block_index += len(new_blocks)
    for entry in table_library.tables:
        if str(entry.table_type or "").strip().lower() not in {"numbered", "formula_table"}:
            continue
        source = entry.source if isinstance(entry.source, dict) else {}
        unit_id = str(source.get("unit_id") or "").strip()
        physical_record, owner_reason = _physical_owner_record_for_table(records=records, table_entry=entry)
        if physical_record is not None:
            unit_id = physical_record.unit.id
            source = {
                **source,
                "unit_id": physical_record.unit.id,
                "chapter": physical_record.unit.chapter,
                "subsection": physical_record.unit.subsections[-1] if physical_record.unit.subsections else source.get("subsection"),
                "physical_owner_rebound_by": owner_reason,
            }
            entry.source = source
        record = records_by_unit.get(unit_id)
        table_id = str(entry.id or "").strip()
        if not table_id or not entry.rows:
            continue
        placeholder = f"[[TABLE:{table_id}]]"
        existing_location = physical_table_locations.get(table_id)
        if existing_location is not None:
            existing_record, existing_block_index = existing_location
            desired_unit_id = physical_record.unit.id if physical_record is not None else existing_record.unit.id
            if existing_record.unit.id == desired_unit_id and table_location_is_unit_end(existing_location):
                updated_source = dict(source)
                updated_source["unit_id"] = existing_record.unit.id
                updated_source["chapter"] = existing_record.unit.chapter
                if existing_record.unit.subsections:
                    updated_source["subsection"] = existing_record.unit.subsections[-1]
                updated_source["has_physical_placeholder"] = True
                updated_source["physical_placeholder_verified_by"] = "structured_fusion_numbered_table_materializer"
                updated_source["physical_placeholder_block_index"] = existing_block_index
                entry.source = updated_source
                stats["numbered_table_existing_physical_placeholder_verified"] += 1
                events.append(
                    {
                        "table_id": table_id,
                        "unit_id": existing_record.unit.id,
                        "action": "verify_numbered_table_placeholder_at_unit_end",
                        "block_index": existing_block_index,
                    }
                )
                existing_location = (existing_record, existing_block_index)
            else:
                removed = remove_or_demote_physical_placeholder(existing_record, table_id)
                if existing_record.unit.id != desired_unit_id:
                    stats["numbered_table_wrong_physical_placeholder_removed"] += removed
                    action = "remove_wrong_numbered_table_placeholder"
                else:
                    stats["numbered_table_physical_placeholder_moved_to_unit_end"] += removed
                    if removed > 1:
                        stats["duplicate_physical_table_placeholder_removed_same_unit"] += removed - 1
                    action = "move_numbered_table_placeholder_to_unit_end"
                events.append(
                    {
                        "table_id": table_id,
                        "unit_id": existing_record.unit.id,
                        "target_unit_id": desired_unit_id,
                        "action": action,
                        "removed": removed,
                    }
                )
                existing_location = None
                physical_table_locations.pop(table_id, None)
            if existing_location is not None:
                continue
            record = records_by_unit.get(desired_unit_id) or record
        if existing_location is None and physical_record is None and table_id in demoted_table_locations:
            record = demoted_table_locations[table_id]
            source = {
                **source,
                "unit_id": record.unit.id,
                "chapter": record.unit.chapter,
                "subsection": record.unit.subsections[-1] if record.unit.subsections else source.get("subsection"),
                "physical_owner_rebound_by": "structured_fusion_embedded_table_reference_owner",
            }
            entry.source = source
        if not record:
            continue
        if source.get("has_physical_placeholder"):
            stats["numbered_table_source_claimed_placeholder_missing"] += 1
        if existing_location is None and record is not None:
            already_has_physical_placeholder = any(
                block.type == "table" and block.content.strip() == placeholder
                for block in record.unit.blocks
            )
            if not already_has_physical_placeholder and (physical_record is not None or table_id in {str(ref) for ref in record.unit.table_references}):
                insert_index = append_physical_placeholder(record, table_id)
                source = dict(source)
                source["unit_id"] = record.unit.id
                source["chapter"] = record.unit.chapter
                if record.unit.subsections:
                    source["subsection"] = record.unit.subsections[-1]
                source["has_physical_placeholder"] = True
                source["physical_placeholder_inserted_by"] = (
                    "structured_fusion_physical_owner_unit_end"
                    if physical_record is not None
                    else "structured_fusion_numbered_table_materializer"
                )
                source["physical_placeholder_insert_mode"] = "append_to_owner_unit"
                source["physical_placeholder_block_index"] = insert_index
                entry.source = source
                if physical_record is not None:
                    stats["numbered_table_placeholders_inserted_by_physical_owner"] += 1
                else:
                    stats["numbered_table_placeholders_appended"] += 1
                events.append(
                    {
                        "table_id": table_id,
                        "unit_id": record.unit.id,
                        "action": "append_numbered_table_placeholder_to_owner_end",
                        "block_index": insert_index,
                    }
                )
                continue
        has_unit_reference = table_id in {str(ref) for ref in record.unit.table_references}
        has_explicit_see_ref = any(
            re.search(
                rf"\[\[\s*SEE_TABLE\s*:\s*{re.escape(table_id)}\s*\]\]",
                block.content,
                flags=re.IGNORECASE,
            )
            for block in record.unit.blocks
        )
        extracted_from_raw = bool(
            source.get("bbox")
            or source.get("caption_bbox")
            or source.get("extraction_channel")
            or source.get("source_channel")
            or source.get("source_path")
            or source.get("evidence_hash")
            or source.get("fusion_repair")
        )
        caption = str(entry.title or entry.label_format or "")
        caption_tokens = normalize_match_text(caption).split()
        if len(caption_tokens) < 6:
            continue
        anchor_tokens = caption_tokens[: min(16, len(caption_tokens))]
        inserted = False
        for block_index, block in enumerate(record.unit.blocks):
            token_spans = [
                (match.group(0).lower(), match.start(), match.end())
                for match in re.finditer(r"[0-9A-Za-z]+", block.content)
            ]
            values = [token for token, _, _ in token_spans]
            start_token = _find_token_subsequence(values, anchor_tokens)
            if start_token is None:
                continue
            start_char = token_spans[start_token][1]
            table_text = _table_text_anchor(entry)
            combined_anchor = normalize_match_text(f"{caption} {table_text}").split()
            end_char = token_spans[min(len(token_spans) - 1, start_token + len(anchor_tokens) - 1)][2]
            if len(combined_anchor) > len(anchor_tokens):
                combined_start = _find_token_subsequence(values, combined_anchor[: min(len(combined_anchor), len(values) - start_token)])
                if combined_start is not None and combined_start == start_token:
                    end_token = min(len(token_spans) - 1, start_token + min(len(combined_anchor), len(values) - start_token) - 1)
                    end_char = token_spans[end_token][2]
            while end_char < len(block.content) and block.content[end_char] in ".;:,":
                end_char += 1
            prefix = block.content[:start_char].strip()
            suffix = block.content[end_char:].strip()
            new_blocks: list[KnowledgeBlock] = []
            if prefix:
                new_blocks.append(KnowledgeBlock(type=block.type, content=prefix))
            if suffix:
                new_blocks.append(KnowledgeBlock(type=block.type, content=suffix))
            record.unit.blocks = [
                *record.unit.blocks[:block_index],
                *new_blocks,
                *record.unit.blocks[block_index + 1 :],
            ]
            placeholder_index = append_physical_placeholder(record, table_id)
            source = dict(source)
            source["has_physical_placeholder"] = True
            source["physical_placeholder_inserted_by"] = "structured_fusion_numbered_table_materializer"
            source["physical_placeholder_insert_mode"] = "append_to_owner_unit"
            source["physical_placeholder_block_index"] = placeholder_index
            entry.source = source
            stats["numbered_table_placeholders_inserted"] += 1
            events.append(
                {
                    "table_id": table_id,
                    "unit_id": record.unit.id,
                    "action": "insert_numbered_table_placeholder_at_unit_end",
                    "block_index": placeholder_index,
                }
            )
            inserted = True
            break
        if not inserted and physical_record is not None:
            insert_index = append_physical_placeholder(record, table_id)
            source = dict(source)
            source["has_physical_placeholder"] = True
            source["physical_placeholder_inserted_by"] = "structured_fusion_physical_owner_unit_end"
            source["physical_placeholder_insert_mode"] = "append_to_owner_unit"
            source["physical_placeholder_block_index"] = insert_index
            entry.source = source
            stats["numbered_table_placeholders_inserted_by_physical_owner"] += 1
            events.append(
                {
                    "table_id": table_id,
                    "unit_id": record.unit.id,
                    "action": "insert_numbered_table_placeholder_at_physical_owner_end",
                    "block_index": insert_index,
                }
            )
            inserted = True
        if inserted or not extracted_from_raw:
            continue
        if not (has_unit_reference or has_explicit_see_ref):
            stats["numbered_table_placeholders_deferred_no_unit_evidence"] += 1
            events.append(
                {
                    "table_id": table_id,
                    "unit_id": record.unit.id,
                    "action": "defer_numbered_table_placeholder",
                    "reason": "no_unit_reference_or_caption_anchor",
                }
            )
            continue
        insert_index = append_physical_placeholder(record, table_id)
        source = dict(source)
        source["has_physical_placeholder"] = True
        source["physical_placeholder_inserted_by"] = "structured_fusion_numbered_table_materializer"
        source["physical_placeholder_insert_mode"] = "append_to_source_unit"
        source["physical_placeholder_block_index"] = insert_index
        entry.source = source
        stats["numbered_table_placeholders_appended"] += 1
        events.append(
            {
                "table_id": table_id,
                "unit_id": record.unit.id,
                "action": "append_numbered_table_placeholder",
                "block_index": insert_index,
            }
        )
    return stats, events


def _table_row_label_anchors(entry: TableEntry) -> list[str]:
    anchors: list[str] = []
    for row in entry.rows or []:
        if len(row) < 2:
            continue
        label = normalize_match_text(str(row[0]))
        if len(label.split()) < 2:
            continue
        if label in {"selection scheme", "formula"}:
            continue
        anchors.append(label)
    return anchors


def _matched_table_row_labels(blocks: list[KnowledgeBlock], anchors: list[str]) -> set[str]:
    matched: set[str] = set()
    for block in blocks:
        if block.type == "table":
            continue
        block_text = normalize_match_text(block.content)
        if not block_text:
            continue
        for anchor in anchors:
            anchor_tokens = anchor.split()
            prefix = " ".join(anchor_tokens[: min(len(anchor_tokens), 6)])
            if block_text.startswith(anchor) or (prefix and block_text.startswith(prefix)):
                matched.add(anchor)
    return matched


def _remove_duplicate_physical_table_placeholders(
    *,
    records: list[UnitRecord],
    table_id: str,
    keep_record: UnitRecord,
) -> int:
    removed = 0
    placeholder = f"[[TABLE:{table_id}]]"
    for record in records:
        if record is keep_record:
            continue
        kept_blocks: list[KnowledgeBlock] = []
        for block in record.unit.blocks:
            if block.type == "table" and block.content.strip() == placeholder:
                removed += 1
                continue
            kept_blocks.append(block)
        if removed:
            record.unit.blocks = kept_blocks
    return removed


def _remove_duplicate_physical_table_placeholders_within_units(
    *,
    records: list[UnitRecord],
) -> tuple[Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    for record in records:
        seen: set[str] = set()
        kept_blocks: list[KnowledgeBlock] = []
        for block_index, block in enumerate(record.unit.blocks):
            match = PHYSICAL_TABLE_PLACEHOLDER_RE.fullmatch(block.content.strip())
            if block.type == "table" and match:
                table_id = match.group("label").strip()
                if table_id in seen:
                    stats["duplicate_physical_table_placeholder_removed_same_unit"] += 1
                    events.append(
                        {
                            "unit_id": record.unit.id,
                            "table_id": table_id,
                            "block_index": block_index,
                            "action": "remove_duplicate_physical_table_placeholder_same_unit",
                        }
                    )
                    continue
                seen.add(table_id)
            kept_blocks.append(block)
        record.unit.blocks = kept_blocks
    return stats, events


def _replace_table_body_residue_with_placeholder(
    *,
    records: list[UnitRecord],
    table_library: TableLibrary,
) -> tuple[Counter[str], list[dict[str, Any]]]:
    stats: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    for entry in table_library.tables:
        table_id = str(entry.id or "").strip()
        if not _is_numbered_table_id(table_id) or not entry.rows:
            continue
        anchors = _table_row_label_anchors(entry)
        if len(anchors) < 2:
            continue
        source = entry.source if isinstance(entry.source, dict) else {}
        if source.get("physical_placeholder_inserted_by") == "structured_fusion_table_body_residue_rebinder":
            continue
        chapter = str(source.get("chapter") or _chapter_from_table_id(table_id)).strip().lower()
        placeholder = f"[[TABLE:{table_id}]]"
        is_formula_table = str(entry.table_type or "").strip().lower() == "formula_table"
        min_matches = 2 if len(anchors) <= 3 else 3

        for record in records:
            if chapter and record.unit.chapter != chapter:
                continue
            block_matches: list[tuple[int, set[str]]] = []
            for block_index, block in enumerate(record.unit.blocks):
                matched = _matched_table_row_labels([block], anchors)
                if matched:
                    block_matches.append((block_index, matched))
            if not block_matches:
                continue
            all_matches = set().union(*(matched for _, matched in block_matches))
            if len(all_matches) < min_matches:
                continue

            first_index = block_matches[0][0]
            last_index = block_matches[-1][0]
            local_placeholder_index = next(
                (
                    index
                    for index, block in enumerate(record.unit.blocks[: first_index + 1])
                    if block.type == "table" and block.content.strip() == placeholder
                ),
                None,
            )
            any_placeholder_index = next(
                (
                    index
                    for index, block in enumerate(record.unit.blocks)
                    if block.type == "table" and block.content.strip() == placeholder
                ),
                None,
            )
            if record.unit.id != str(source.get("unit_id") or "").strip() and not is_formula_table:
                continue
            if local_placeholder_index is None and any_placeholder_index is None and not is_formula_table:
                continue
            has_local_placeholder = local_placeholder_index is not None or any_placeholder_index is not None
            new_blocks = list(record.unit.blocks[:first_index])
            inserted_index = any_placeholder_index if any_placeholder_index is not None else first_index
            if not has_local_placeholder:
                new_blocks.append(KnowledgeBlock(type="table", content=placeholder))
            for block in record.unit.blocks[last_index + 1 :]:
                if block.type == "table" and block.content.strip() == placeholder:
                    continue
                new_blocks.append(block)
            if has_local_placeholder:
                new_blocks.append(KnowledgeBlock(type="table", content=placeholder))
                inserted_index = len(new_blocks) - 1
            record.unit.blocks = new_blocks

            removed_duplicates = _remove_duplicate_physical_table_placeholders(
                records=records,
                table_id=table_id,
                keep_record=record,
            )
            updated_source = dict(source)
            updated_source["unit_id"] = record.unit.id
            updated_source["chapter"] = record.unit.chapter
            if record.unit.subsections:
                updated_source["subsection"] = record.unit.subsections[-1]
            updated_source["has_physical_placeholder"] = True
            updated_source["physical_placeholder_inserted_by"] = "structured_fusion_table_body_residue_rebinder"
            updated_source["physical_placeholder_block_index"] = inserted_index
            entry.source = updated_source
            stats["table_body_residue_blocks_removed"] += last_index - first_index + 1
            stats["table_body_residue_placeholders_rebound"] += 1
            if removed_duplicates:
                stats["duplicate_table_placeholders_removed"] += removed_duplicates
            events.append(
                {
                    "table_id": table_id,
                    "unit_id": record.unit.id,
                    "action": "replace_table_body_residue_with_placeholder",
                    "block_start": first_index,
                    "block_end": last_index,
                    "matched_row_labels": len(all_matches),
                    "duplicate_placeholders_removed": removed_duplicates,
                }
            )
            break
    return stats, events


def _refresh_unit_references(
    *,
    records: list[UnitRecord],
    formula_library: FormulaLibrary,
    table_library: TableLibrary,
) -> Counter[str]:
    stats: Counter[str] = Counter()
    known_formula_ids = _formula_ids(formula_library)
    known_table_ids = _table_ids(table_library)

    for record in records:
        old_formula_refs = list(record.unit.formula_references)
        old_table_refs = list(record.unit.table_references)
        formula_refs = list(old_formula_refs)
        table_refs = list(old_table_refs)
        table_ref_keys = list(record.unit.table_reference_keys)
        external_table_refs: set[str] = set()

        for block in record.unit.blocks:
            for label in _extract_formula_refs_from_content(block.content):
                if label.lower() in known_formula_ids and label not in formula_refs:
                    formula_refs.append(label)
                    stats["formula_references_backfilled"] += 1
            for label in _extract_table_refs_from_content(block.content):
                if label not in known_table_ids and _is_external_table_reference(block.content, label):
                    external_table_refs.add(label)
                    stats["external_table_references_skipped"] += 1
                    continue
                # table/formula 同号归一：同号公式存在且同号表不存在，转为 formula reference
                if label not in known_table_ids and label.lower() in known_formula_ids:
                    if label not in formula_refs:
                        formula_refs.append(label)
                        stats["table_to_formula_normalized"] += 1
                    continue
                if label in known_table_ids and label not in table_refs:
                    table_refs.append(label)
                    stats["table_references_backfilled"] += 1
                if label in known_table_ids:
                    key = table_reference_key(record.unit.chapter, label)
                    if key not in table_ref_keys:
                        table_ref_keys.append(key)
                        stats["table_reference_keys_backfilled"] += 1

        if external_table_refs:
            kept_table_refs = [label for label in table_refs if label not in external_table_refs or label in known_table_ids]
            removed_count = len(table_refs) - len(kept_table_refs)
            if removed_count:
                stats["external_table_references_removed_from_local_metadata"] += removed_count
                table_refs = kept_table_refs
            table_ref_keys = [
                key
                for key in table_ref_keys
                if not any(key.endswith(f":{label}") for label in external_table_refs)
            ]

        record.unit.formula_references = sort_formula_refs(formula_refs)
        record.unit.table_references = sort_table_refs(table_refs)
        record.unit.table_reference_keys = sort_table_ref_keys(table_ref_keys)
        if record.unit.formula_references != old_formula_refs:
            stats["units_with_formula_reference_updates"] += 1
        if record.unit.table_references != old_table_refs:
            stats["units_with_table_reference_updates"] += 1

    return stats


def apply_structured_fusion(
    *,
    structured_dir: str | Path,
    output_dir: str | Path | None = None,
    pdf_dir: str | Path | None = None,
    glmocr_dir: str | Path | None = None,
    paddle_output_dir: str | Path | None = None,
    reference_structured_dir: str | Path | None = None,
    artifacts_dir: str | Path | None = None,
    auto_threshold: float = AUTO_THRESHOLD,
    review_threshold: float = REVIEW_THRESHOLD,
    max_window_paragraphs: int = MAX_WINDOW_PARAGRAPHS,
    include_review: bool = False,
    replace_weaker_tables: bool = False,
    enable_glm_prose_repair: bool = False,
    enable_ocr_table_evidence: bool = True,
    enable_ocr_table_repair: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    source_root = Path(structured_dir)
    target_root = Path(output_dir) if output_dir else source_root
    if output_dir and target_root.resolve() != source_root.resolve() and not dry_run:
        _copy_structured_dir(source_root, target_root)

    root = target_root if not dry_run else source_root
    records = _load_unit_records(root)
    formula_library = FormulaLibrary.load(str(root / "formula_library.json"))
    table_library = TableLibrary.load(str(root / "table_library.json"))
    known_formula_ids = _formula_ids(formula_library)
    known_table_ids = _table_ids(table_library)

    block_stats, repair_items, manual_queue, issue_counts = _repair_blocks_with_glm(
        records=records,
        glmocr_dir=Path(glmocr_dir) if glmocr_dir and enable_glm_prose_repair else None,
        known_formula_ids=known_formula_ids,
        known_table_ids=known_table_ids,
        auto_threshold=auto_threshold,
        review_threshold=review_threshold,
        max_window_paragraphs=max_window_paragraphs,
        include_review=include_review,
    )

    formula_events: list[dict[str, Any]] = []
    formula_stats: Counter[str] = Counter()
    for formula in formula_library.formulas:
        original_latex = str(formula.latex or "")
        normalized_latex, reasons = _normalize_formula_latex(original_latex)
        original_context = str(getattr(formula, "context", "") or "")
        normalized_context, context_reasons = _normalize_latex_in_text(original_context)
        changed = False
        if normalized_latex != original_latex:
            formula.latex = normalized_latex
            formula_stats["latex_normalized"] += 1
            changed = True
        if normalized_context != original_context:
            formula.context = normalized_context
            formula_stats["formula_context_normalized"] += 1
            changed = True
        if not changed:
            continue
        formula_events.append(
            {
                "formula_id": str(formula.id or "").strip(),
                "chapter": str((formula.source or {}).get("chapter") or "").strip(),
                "unit_id": str((formula.source or {}).get("unit_id") or "").strip(),
                "subsection": str((formula.source or {}).get("subsection") or "").strip(),
                "action": "normalize_latex",
                "reason_codes": sorted(set([*reasons, *context_reasons])),
                "latex_before": original_latex,
                "latex_after": normalized_latex,
                "context_before": original_context if normalized_context != original_context else None,
                "context_after": normalized_context if normalized_context != original_context else None,
            }
        )

    table_library, table_stats, table_events = _recover_reference_tables(
        current_library=table_library,
        records=records,
        reference_structured_dir=Path(reference_structured_dir) if reference_structured_dir else None,
        replace_weaker_tables=replace_weaker_tables,
    )
    table_library, table_sanitize_stats, table_sanitize_events = _sanitize_table_library(table_library)
    table_stats.update(table_sanitize_stats)
    table_events.extend(table_sanitize_events)

    ocr_evidence_index = OCREvidenceIndex()
    table_binding_stats: Counter[str] = Counter()
    table_binding_events: list[dict[str, Any]] = []
    table_binding_manual_queue: list[dict[str, Any]] = []
    if enable_ocr_table_evidence:
        ocr_evidence_index = build_ocr_evidence_index(
            pdf_dir=Path(pdf_dir) if pdf_dir else None,
            paddle_output_dir=Path(paddle_output_dir) if paddle_output_dir else None,
            glmocr_dir=Path(glmocr_dir) if glmocr_dir else None,
            chapters=_record_chapters(records),
        )
        table_library, table_binding_stats, table_binding_events, table_binding_manual_queue = _audit_ocr_table_bindings(
            table_library=table_library,
            ocr_evidence_index=ocr_evidence_index,
            auto_apply_replacements=enable_ocr_table_repair and not dry_run,
        )
        manual_queue.extend(table_binding_manual_queue)

    list_table_stats, list_table_events = _materialize_list_tables_in_units(
        records=records,
        table_library=table_library,
    )
    table_stats.update(list_table_stats)
    table_events.extend(list_table_events)
    numbered_table_stats, numbered_table_events = _materialize_numbered_tables_in_units(
        records=records,
        table_library=table_library,
    )
    table_stats.update(numbered_table_stats)
    table_events.extend(numbered_table_events)
    same_unit_duplicate_stats, same_unit_duplicate_events = _remove_duplicate_physical_table_placeholders_within_units(
        records=records,
    )
    table_stats.update(same_unit_duplicate_stats)
    table_events.extend(same_unit_duplicate_events)
    residue_table_stats, residue_table_events = _replace_table_body_residue_with_placeholder(
        records=records,
        table_library=table_library,
    )
    table_stats.update(residue_table_stats)
    table_events.extend(residue_table_events)
    same_unit_duplicate_stats, same_unit_duplicate_events = _remove_duplicate_physical_table_placeholders_within_units(
        records=records,
    )
    table_stats.update(same_unit_duplicate_stats)
    table_events.extend(same_unit_duplicate_events)

    ref_stats = _refresh_unit_references(
        records=records,
        formula_library=formula_library,
        table_library=table_library,
    )
    example_sanitize_stats, example_sanitize_events = _sanitize_example_library(root)

    if not dry_run:
        _save_unit_records(records)
        table_library.save(str(root / "table_library.json"))
        formula_library.save(str(root / "formula_library.json"))

    total_blocks = sum(len(record.unit.blocks) for record in records)
    summary = build_structured_fusion_summary(
        structured_dir=source_root,
        output_dir=target_root,
        glmocr_dir=glmocr_dir,
        paddle_output_dir=paddle_output_dir,
        reference_structured_dir=reference_structured_dir,
        dry_run=dry_run,
        include_review=include_review,
        replace_weaker_tables=replace_weaker_tables,
        enable_glm_prose_repair=enable_glm_prose_repair,
        enable_ocr_table_evidence=enable_ocr_table_evidence,
        enable_ocr_table_repair=enable_ocr_table_repair,
        auto_threshold=auto_threshold,
        review_threshold=review_threshold,
        max_window_paragraphs=max_window_paragraphs,
        units_scanned=len(records),
        blocks_after_fusion=total_blocks,
        block_stats=block_stats,
        table_stats=table_stats,
        table_binding_stats=table_binding_stats,
        formula_stats=formula_stats,
        reference_stats=ref_stats,
        issue_counts=issue_counts,
        manual_queue=manual_queue,
        repair_items=repair_items,
        formula_events=formula_events,
        table_events=table_events,
        table_binding_events=table_binding_events,
        ocr_evidence_index=ocr_evidence_index,
        table_library=table_library,
        formula_library=formula_library,
    )
    summary["example_sanitize_stats"] = dict(sorted(example_sanitize_stats.items()))
    summary["example_sanitize_event_count"] = len(example_sanitize_events)

    if artifacts_dir:
        summary["artifact_dir"] = write_structured_fusion_artifacts(
            artifacts_dir=artifacts_dir,
            summary=summary,
            repair_items=repair_items,
            formula_events=formula_events,
            manual_queue=manual_queue,
            table_events=table_events,
            table_binding_events=table_binding_events,
            ocr_evidence_index=ocr_evidence_index,
        )

    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply generic structured fusion to a baseline structured directory.")
    parser.add_argument("--structured-dir", default="data/structured")
    parser.add_argument("--out", default="", help="Write a fused copy here. Empty means in-place.")
    parser.add_argument("--pdf-dir", default=(os.getenv("KE_PDF_DIR") or "data/背景资料"), help="PDF directory for visual table evidence.")
    parser.add_argument("--glmocr-dir", default="", help="Optional GLM OCR reference directory.")
    parser.add_argument("--paddle-output-dir", default="", help="Optional Paddle raw output directory for table/formula evidence.")
    parser.add_argument("--reference-structured-dir", default="", help="Optional earlier structured directory for table recovery.")
    parser.add_argument("--artifacts-dir", default="tmp/knowledge_engineering")
    parser.add_argument("--auto-threshold", type=float, default=AUTO_THRESHOLD)
    parser.add_argument("--review-threshold", type=float, default=REVIEW_THRESHOLD)
    parser.add_argument("--max-window-paragraphs", type=int, default=MAX_WINDOW_PARAGRAPHS)
    parser.add_argument("--include-review", action="store_true", help="Also apply review-threshold GLM repairs.")
    parser.add_argument("--replace-weaker-tables", action="store_true", help="Allow reference tables to replace existing weaker table entries.")
    parser.add_argument("--enable-glm-prose-repair", action="store_true", help="Allow high-confidence GLM OCR prose replacements.")
    parser.add_argument("--disable-ocr-table-evidence", action="store_true", help="Skip Paddle/GLM OCR evidence indexing for table binding audit.")
    parser.add_argument("--enable-ocr-table-repair", action="store_true", help="Apply two-channel high-confidence OCR table replacement candidates.")
    parser.add_argument("--dry-run", action="store_true", help="Build reports without writing structured output.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    summary = apply_structured_fusion(
        structured_dir=args.structured_dir,
        output_dir=args.out or None,
        pdf_dir=args.pdf_dir or None,
        glmocr_dir=args.glmocr_dir or None,
        paddle_output_dir=args.paddle_output_dir or None,
        reference_structured_dir=args.reference_structured_dir or None,
        artifacts_dir=args.artifacts_dir,
        auto_threshold=args.auto_threshold,
        review_threshold=args.review_threshold,
        max_window_paragraphs=args.max_window_paragraphs,
        include_review=bool(args.include_review),
        replace_weaker_tables=bool(args.replace_weaker_tables),
        enable_glm_prose_repair=bool(args.enable_glm_prose_repair),
        enable_ocr_table_evidence=not bool(args.disable_ocr_table_evidence),
        enable_ocr_table_repair=bool(args.enable_ocr_table_repair),
        dry_run=bool(args.dry_run),
    )
    print(
        "[structured-fusion] "
        f"units={summary['units_scanned']} "
        f"blocks={summary['blocks_after_fusion']} "
        f"removed={summary['block_stats'].get('blocks_removed', 0)} "
        f"tables_recovered={summary['table_stats'].get('table_entries_recovered_from_reference', 0)} "
        f"missing_table_stubs_recovered={summary.get('table_binding_stats', {}).get('missing_table_stub_recovered', 0)} "
        f"table_binding_events={summary.get('table_binding_event_count', 0)}"
    )
    if summary.get("artifact_dir"):
        print(f"[structured-fusion] artifacts: {summary['artifact_dir']}")


if __name__ == "__main__":
    main()
