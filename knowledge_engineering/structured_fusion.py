"""Evidence-based structured fusion for production candidate outputs.

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
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

from knowledge_engineering.runtime import (
    DEFAULT_SOURCE_TITLE,
    FormulaLibrary,
    KnowledgeBlock,
    KnowledgeUnit,
    TableEntry,
    TableLibrary,
)
from knowledge_engineering.ocr_evidence import (
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
from knowledge_engineering.structured_repair import (
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


FORMULA_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_FORMULA|FORMULA):(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\]\]"
)
TABLE_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_TABLE|TABLE):(?P<label>(?:\d+\.\d+[A-Za-z]?|inline_\d+))\]\]",
    re.IGNORECASE,
)
TABLE_TEXT_RE = re.compile(r"\bTable\s+(?P<label>\d+\.\d+[A-Za-z]?)\b", re.IGNORECASE)
BROKEN_PLACEHOLDER_RE = re.compile(
    r"\[\[(?:SEE_FORMULA|FORMULA|SEE_TABLE|TABLE):(?:(?!\]\]).)*$",
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
NESTED_ACCENT_COMMANDS = ("overline", "underline", "bar", "hat", "tilde", "vec")

DETERMINISTIC_DROP_ISSUES = {"empty_content", "h_only_block", "ghost_block"}
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


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def normalize_match_text(text: str) -> str:
    value = str(text or "")
    value = STRUCTURED_REF_RE.sub(" ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\\([A-Za-z]+)", r" \1 ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def table_sort_key(reference: str) -> tuple[int, int, int, int, int, str]:
    value = str(reference or "").strip()
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?([A-Za-z]?)", value)
    if match:
        suffix = match.group(4).lower()
        suffix_rank = 0 if not suffix else ord(suffix) - 96
        subindex = int(match.group(3)) if match.group(3) else 0
        return (0, int(match.group(1)), int(match.group(2)), subindex, suffix_rank, value)

    inline_match = re.fullmatch(r"inline_(\d+)", value, flags=re.IGNORECASE)
    if inline_match:
        return (1, int(inline_match.group(1)), 0, 0, 0, value)
    return (9, 9999, 9999, 9999, 9999, value)


def chapter_sort_key(chapter_name: str) -> tuple[int, int, str]:
    value = str(chapter_name or "").strip().lower()
    chapter_match = re.fullmatch(r"chapter(\d+)", value)
    if chapter_match:
        return (0, int(chapter_match.group(1)), value)
    appendix_match = re.fullmatch(r"appendix(\d+)", value)
    if appendix_match:
        return (1, int(appendix_match.group(1)), value)
    return (9, 9999, value)


def sort_table_refs(references: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for reference in references:
        value = str(reference or "").strip()
        if value and value not in seen:
            seen.append(value)
    return sorted(seen, key=table_sort_key)


def sort_table_ref_keys(reference_keys: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for reference_key in reference_keys:
        value = str(reference_key or "").strip()
        if value and value not in seen:
            seen.append(value)

    def _key_sort(item: str) -> tuple:
        parts = item.split(":", 1)
        if len(parts) != 2:
            return (chapter_sort_key(""), table_sort_key(""), item)
        chapter_name, table_id = parts
        return (chapter_sort_key(chapter_name), table_sort_key(table_id), item)

    return sorted(seen, key=_key_sort)


def sort_formula_refs(references: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for reference in references:
        value = str(reference or "").strip().lower()
        if value.startswith("formula_"):
            value = value.removeprefix("formula_")
        if value and value not in seen:
            seen.append(value)

    def _formula_sort_key(value: str) -> tuple[int, int, int, int, str]:
        match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?([A-Za-z]?)", value)
        if match:
            suffix = match.group(4).lower()
            suffix_rank = 0 if not suffix else ord(suffix) - 96
            subindex = int(match.group(3)) if match.group(3) else 0
            return (int(match.group(1)), int(match.group(2)), subindex, suffix_rank, value)
        return (9999, 9999, 9999, 9999, value)

    return sorted(seen, key=_formula_sort_key)


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

    for command in NESTED_ACCENT_COMMANDS:
        pattern = re.compile(rf"\\{command}\{{\\{command}\{{([^{{}}]+)\}}\}}")
        while True:
            updated = pattern.sub(rf"\\{command}{{\1}}", value)
            if updated == value:
                break
            value = updated
            reasons.append(f"collapse_nested_{command}")

    return value, reasons


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
    if BROKEN_PLACEHOLDER_RE.search(stripped):
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
        best_structured_score = scored_evidences[0][2] if scored_evidences else {}
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
            source = dict(replacement.source or {})
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
                    key = f"{record.unit.chapter}:{label}"
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
        if normalized_latex == original_latex:
            continue
        formula.latex = normalized_latex
        formula_stats["latex_normalized"] += 1
        formula_events.append(
            {
                "formula_id": str(formula.id or "").strip(),
                "chapter": str((formula.source or {}).get("chapter") or "").strip(),
                "unit_id": str((formula.source or {}).get("unit_id") or "").strip(),
                "subsection": str((formula.source or {}).get("subsection") or "").strip(),
                "action": "normalize_latex",
                "reason_codes": reasons,
                "latex_before": original_latex,
                "latex_after": normalized_latex,
            }
        )

    table_library, table_stats, table_events = _recover_reference_tables(
        current_library=table_library,
        records=records,
        reference_structured_dir=Path(reference_structured_dir) if reference_structured_dir else None,
        replace_weaker_tables=replace_weaker_tables,
    )

    ocr_evidence_index = OCREvidenceIndex()
    table_binding_stats: Counter[str] = Counter()
    table_binding_events: list[dict[str, Any]] = []
    table_binding_manual_queue: list[dict[str, Any]] = []
    if enable_ocr_table_evidence:
        ocr_evidence_index = build_ocr_evidence_index(
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

    ref_stats = _refresh_unit_references(
        records=records,
        formula_library=formula_library,
        table_library=table_library,
    )

    if not dry_run:
        _save_unit_records(records)
        table_library.save(str(root / "table_library.json"))
        formula_library.save(str(root / "formula_library.json"))

    total_blocks = sum(len(record.unit.blocks) for record in records)
    summary = {
        "timestamp_utc": utc_now_iso(),
        "structured_dir": str(source_root),
        "output_dir": str(target_root),
        "glmocr_dir": str(glmocr_dir) if glmocr_dir else "",
        "paddle_output_dir": str(paddle_output_dir) if paddle_output_dir else "",
        "reference_structured_dir": str(reference_structured_dir) if reference_structured_dir else "",
        "dry_run": bool(dry_run),
        "include_review": bool(include_review),
        "replace_weaker_tables": bool(replace_weaker_tables),
        "enable_glm_prose_repair": bool(enable_glm_prose_repair),
        "enable_ocr_table_evidence": bool(enable_ocr_table_evidence),
        "enable_ocr_table_repair": bool(enable_ocr_table_repair),
        "auto_threshold": auto_threshold,
        "review_threshold": review_threshold,
        "max_window_paragraphs": max_window_paragraphs,
        "units_scanned": len(records),
        "blocks_after_fusion": total_blocks,
        "block_stats": dict(sorted(block_stats.items())),
        "table_stats": dict(sorted(table_stats.items())),
        "table_binding_stats": dict(sorted(table_binding_stats.items())),
        "formula_stats": dict(sorted(formula_stats.items())),
        "reference_stats": dict(sorted(ref_stats.items())),
        "issue_counts": dict(sorted(issue_counts.items())),
        "manual_queue_count": len(manual_queue),
        "repair_item_count": len(repair_items),
        "formula_event_count": len(formula_events),
        "table_event_count": len(table_events),
        "table_binding_event_count": len(table_binding_events),
        "ocr_evidence_count": len(ocr_evidence_index.evidences),
        "table_library_entries": len(table_library.tables),
        "formula_library_entries": len(formula_library.formulas),
    }

    if artifacts_dir:
        out_dir = Path(artifacts_dir) / "structured_fusion"
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_dir / "structured_fusion_summary.json", summary)
        write_jsonl(out_dir / "structured_fusion_repair_items.jsonl", repair_items)
        write_jsonl(out_dir / "structured_fusion_formula_events.jsonl", formula_events)
        write_jsonl(out_dir / "structured_fusion_manual_queue.jsonl", manual_queue)
        write_jsonl(out_dir / "structured_fusion_table_events.jsonl", table_events)
        write_jsonl(out_dir / "structured_fusion_table_binding_events.jsonl", table_binding_events)
        write_json(out_dir / "structured_fusion_ocr_evidence_index.json", ocr_evidence_index.to_dict())
        summary["artifact_dir"] = str(out_dir)

    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply generic structured fusion to a baseline structured directory.")
    parser.add_argument("--structured-dir", default="data/structured")
    parser.add_argument("--out", default="", help="Write a fused copy here. Empty means in-place.")
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
        f"table_binding_events={summary.get('table_binding_event_count', 0)}"
    )
    if summary.get("artifact_dir"):
        print(f"[structured-fusion] artifacts: {summary['artifact_dir']}")


if __name__ == "__main__":
    main()
