"""Repair structured OCR chunks using GLM OCR as a guarded text reference.

This module intentionally treats paper2latex/structured JSON as the source of
structure, numbering, formulas, and tables. GLM OCR is only used as a candidate
source for repairing prose-like block content that already has quality issues.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
import html
import json
import re
from pathlib import Path
from typing import Any, Iterable


AUTO_THRESHOLD = 0.90
REVIEW_THRESHOLD = 0.75
MAX_WINDOW_PARAGRAPHS = 3
DEFAULT_LLM_BATCH_SIZE = 8

STRUCTURED_PLACEHOLDER_RE = re.compile(
    r"\[\[(?P<kind>SEE_TABLE|TABLE|SEE_FORMULA|FORMULA):(?P<label>[^\]]+)\]\]"
)
TABLE_TEXT_RE_TEMPLATE = r"\bTable\s+{label}\b"
FORMULA_TEXT_RE_TEMPLATE = r"\b(?:Equations?|Eq\.?)\s*\(?{label}\)?\b|\({label}\)"
FLOAT_PLACEHOLDER_RE = re.compile(r"\[(?:h|t|b|p)\]", re.IGNORECASE)
DUMMY_TABLE_RE = re.compile(
    r"\|?\s*c\s*\|\s*c\s*\|?\s*Cell\s+1\s*&\s*Cell\s+2\s*\\\\\s*"
    r"Cell\s+3\s*&\s*Cell\s+4\s*\\\\?",
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
DISPLAY_MATH_RE = re.compile(r"\$\$|\\\[|\\begin\{(?:equation|align|gather|multline)")
STRUCTURAL_ONLY_RE = re.compile(
    r"^\s*\[\[(?:FORMULA|TABLE):[^\]]+\]\]\s*(?:\[[ht]\]\s*)?$",
    re.IGNORECASE,
)
CHAPTER_ID_RE = re.compile(r"^(?P<chapter>(?:chapter|appendix)\d+)_?(?P<ordinal>\d+)?", re.IGNORECASE)

REPAIRABLE_ISSUES = {
    "placeholder_leak",
    "ocr_residual_marker",
    "broken_hyphen_word",
    "unbalanced_inline_math",
    "tex_command_leak",
    "truncated_parenthetical_tail",
    "suspicious_truncation",
    "empty_inline_math",
    "leading_underscore_math",
    "leading_caret_math",
    "missing_left_operand_math",
    "separated_subscript_math",
    "separated_superscript_math",
    "spaced_script_math",
    "bare_underscore_math",
    "likely_missing_operator",
    "empty_expectation",
    "truncated_residual",
    "missing_table_reference",
    "formula_reference_missing",
    "table_reference_missing",
}

SHORT_MATCH_RELAXED_ISSUES = {
    "empty_inline_math",
    "leading_underscore_math",
    "leading_caret_math",
    "missing_left_operand_math",
    "separated_subscript_math",
    "separated_superscript_math",
    "spaced_script_math",
    "bare_underscore_math",
    "likely_missing_operator",
    "empty_expectation",
    "formula_reference_missing",
    "table_reference_missing",
    "unbalanced_inline_math",
    "suspicious_truncation",
}

LLM_REVIEW_DECISIONS = {"accept", "review", "reject"}
LLM_TRIAGE_LABELS = {
    "recoverable_prose",
    "inline_math_candidate",
    "structure_protected",
    "insufficient_evidence",
    "manual_review",
}
LLM_TRIAGE_NEXT_ACTIONS = {
    "keep_rejected",
    "send_to_second_pass",
    "manual_review",
}

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "from",
    "are",
    "was",
    "were",
    "has",
    "have",
    "had",
    "not",
    "but",
    "can",
    "into",
    "than",
    "then",
    "such",
    "these",
    "those",
    "over",
    "under",
    "between",
    "which",
    "where",
    "when",
    "while",
    "also",
    "only",
    "any",
    "all",
    "one",
    "two",
    "its",
    "their",
    "there",
    "using",
    "used",
}


@dataclass(frozen=True)
class GLMParagraph:
    chapter: str
    text: str
    source_path: str
    source_format: str
    page_index: int | None
    block_index: int | None
    bbox: list[Any] | None
    order: int
    label: str = ""


@dataclass(frozen=True)
class GLMSpan:
    chapter: str
    text: str
    paragraphs: tuple[GLMParagraph, ...]

    @property
    def order(self) -> float:
        if not self.paragraphs:
            return 0.0
        return sum(paragraph.order for paragraph in self.paragraphs) / len(self.paragraphs)

    def source_payload(self) -> dict[str, Any]:
        if not self.paragraphs:
            return {}
        first = self.paragraphs[0]
        last = self.paragraphs[-1]
        payload: dict[str, Any] = {
            "chapter": self.chapter,
            "source_path": first.source_path,
            "source_format": first.source_format,
            "start_order": first.order,
            "end_order": last.order,
        }
        if first.page_index is not None:
            payload["start_page_index"] = first.page_index
        if last.page_index is not None:
            payload["end_page_index"] = last.page_index
        if first.block_index is not None:
            payload["start_block_index"] = first.block_index
        if last.block_index is not None:
            payload["end_block_index"] = last.block_index
        if first.bbox is not None:
            payload["start_bbox"] = first.bbox
        if last.bbox is not None and last.bbox != first.bbox:
            payload["end_bbox"] = last.bbox
        return payload


@dataclass
class GLMChapterIndex:
    chapter: str
    spans: list[GLMSpan]
    token_index: dict[str, list[int]]
    span_norms: list[str]
    span_tokens: list[set[str]]

    @classmethod
    def build(cls, chapter: str, spans: list[GLMSpan]) -> "GLMChapterIndex":
        postings: dict[str, list[int]] = defaultdict(list)
        span_norms: list[str] = []
        span_tokens: list[set[str]] = []
        for index, span in enumerate(spans):
            normalized = normalize_for_matching(span.text)
            tokens = tokenize_normalized_text(normalized)
            span_norms.append(normalized)
            span_tokens.append(tokens)
            for token in tokens:
                postings[token].append(index)
        return cls(
            chapter=chapter,
            spans=spans,
            token_index=dict(postings),
            span_norms=span_norms,
            span_tokens=span_tokens,
        )

    def candidate_indices(
        self,
        query_text: str,
        expected_order: float | None = None,
        *,
        max_candidates: int = 90,
    ) -> list[int]:
        if not self.spans:
            return []
        query_tokens = tokenize_for_matching(query_text)
        if not query_tokens:
            return list(range(min(len(self.spans), max_candidates)))

        token_counts = {
            token: len(self.token_index.get(token, []))
            for token in query_tokens
            if self.token_index.get(token)
        }
        counter: Counter[int] = Counter()
        for token, _count in sorted(token_counts.items(), key=lambda item: (item[1], item[0]))[:28]:
            for span_index in self.token_index[token]:
                counter[span_index] += 1

        candidate_set = set(counter.keys())
        if expected_order is not None:
            radius = max(10, int(len(self.spans) * 0.18))
            center = int(round(expected_order))
            for span_index in range(max(0, center - radius), min(len(self.spans), center + radius + 1)):
                candidate_set.add(span_index)

        if not candidate_set:
            return list(range(min(len(self.spans), max_candidates)))

        def sort_key(span_index: int) -> tuple[int, float]:
            order_distance = abs(self.spans[span_index].order - expected_order) if expected_order is not None else 0.0
            return (-counter.get(span_index, 0), order_distance)

        return sorted(candidate_set, key=sort_key)[:max_candidates]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def clean_glm_text(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"</?div[^>]*>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"^#+\s*", "", value.strip())
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def trim_for_llm(text: str, limit: int = 1800) -> str:
    value = str(text or "")
    if len(value) <= limit:
        return value
    head = max(1, limit // 2)
    tail = max(1, limit - head - 80)
    omitted = len(value) - head - tail
    return f"{value[:head]}\n...[omitted {omitted} chars]...\n{value[-tail:]}"


def is_useful_glm_paragraph(text: str, label: str = "") -> bool:
    value = clean_glm_text(text)
    normalized_label = str(label or "").strip().lower()
    if normalized_label in {"number", "header", "footer", "formula_number", "display_formula", "table"}:
        return False
    if len(value) < 12:
        return False
    if re.fullmatch(r"\d{1,4}", value):
        return False
    if "<table" in value.lower() or "</table" in value.lower():
        return False
    if re.fullmatch(r"\$\$[\s\S]*\$\$", value.strip()):
        return False
    return True


def iter_glm_json_blocks(payload: Any) -> Iterable[tuple[int | None, dict[str, Any]]]:
    pages: list[Any]
    if isinstance(payload, list):
        pages = payload
    elif isinstance(payload, dict):
        pages = payload.get("pages") or payload.get("data") or payload.get("result") or []
    else:
        pages = []

    for page_index, page in enumerate(pages):
        if isinstance(page, list):
            blocks = page
        elif isinstance(page, dict):
            blocks = page.get("parsing_res_list") or page.get("blocks") or page.get("items") or []
        else:
            blocks = []
        for block in blocks:
            if isinstance(block, dict):
                yield page_index, block


def load_glm_paragraphs(glmocr_dir: str | Path, chapter: str) -> list[GLMParagraph]:
    """Load useful GLM OCR paragraphs for one chapter."""
    root = Path(glmocr_dir)
    paragraphs: list[GLMParagraph] = []
    json_path = root / f"{chapter}.json"
    md_path = root / f"{chapter}.md"

    if json_path.exists():
        try:
            payload = read_json(json_path)
        except (OSError, json.JSONDecodeError):
            payload = []
        for order, (page_index, block) in enumerate(iter_glm_json_blocks(payload)):
            raw_text = block.get("content") or block.get("block_content") or ""
            label = str(block.get("label") or block.get("block_label") or "")
            if not is_useful_glm_paragraph(raw_text, label):
                continue
            block_index = block.get("index")
            if not isinstance(block_index, int):
                block_index = block.get("block_id")
            if not isinstance(block_index, int):
                block_index = None
            bbox = block.get("bbox_2d") or block.get("block_bbox")
            paragraphs.append(
                GLMParagraph(
                    chapter=chapter,
                    text=clean_glm_text(raw_text),
                    source_path=str(json_path),
                    source_format="json",
                    page_index=page_index,
                    block_index=block_index,
                    bbox=bbox if isinstance(bbox, list) else None,
                    order=len(paragraphs),
                    label=label,
                )
            )

    if not paragraphs and md_path.exists():
        try:
            raw_md = md_path.read_text(encoding="utf-8")
        except OSError:
            raw_md = ""
        for text in split_markdown_paragraphs(raw_md):
            if not is_useful_glm_paragraph(text):
                continue
            paragraphs.append(
                GLMParagraph(
                    chapter=chapter,
                    text=clean_glm_text(text),
                    source_path=str(md_path),
                    source_format="md",
                    page_index=None,
                    block_index=None,
                    bbox=None,
                    order=len(paragraphs),
                )
            )

    return paragraphs


def load_glm_chapter(glmocr_dir: str | Path, chapter: str, max_window: int = MAX_WINDOW_PARAGRAPHS) -> list[GLMSpan]:
    """Load one GLM OCR chapter as searchable paragraph spans."""
    paragraphs = load_glm_paragraphs(glmocr_dir, chapter)
    return build_glm_spans(paragraphs, max_window=max_window)


def split_markdown_paragraphs(raw_md: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    in_table = False
    for raw_line in raw_md.splitlines():
        line = raw_line.strip()
        if "<table" in line.lower():
            in_table = True
        if in_table:
            if "</table" in line.lower():
                in_table = False
            continue
        if not line or line.lower().startswith("<div") or line.lower().startswith("</div"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if line.startswith("$$"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current).strip())
    return paragraphs


def build_glm_spans(paragraphs: list[GLMParagraph], max_window: int = MAX_WINDOW_PARAGRAPHS) -> list[GLMSpan]:
    spans: list[GLMSpan] = []
    window_size = max(1, int(max_window))
    for start in range(len(paragraphs)):
        collected: list[GLMParagraph] = []
        for offset in range(window_size):
            pos = start + offset
            if pos >= len(paragraphs):
                break
            collected.append(paragraphs[pos])
            text = "\n\n".join(paragraph.text for paragraph in collected).strip()
            if len(text) > 5000:
                break
            spans.append(GLMSpan(chapter=paragraphs[start].chapter, text=text, paragraphs=tuple(collected)))
    return spans


def load_glm_index(
    glmocr_dir: str | Path,
    chapters: Iterable[str],
    max_window: int = MAX_WINDOW_PARAGRAPHS,
) -> dict[str, GLMChapterIndex]:
    return {
        chapter: GLMChapterIndex.build(
            chapter,
            load_glm_chapter(glmocr_dir, chapter, max_window=max_window),
        )
        for chapter in sorted(set(chapters))
    }


def chapter_from_unit_id(unit_id: str) -> str:
    match = CHAPTER_ID_RE.match(str(unit_id or ""))
    if match:
        return match.group("chapter").lower()
    return str(unit_id or "").split("_", 1)[0].lower()


def resolve_glm_source_text(
    item: dict[str, Any],
    glmocr_dir: str | Path | None,
    paragraph_cache: dict[str, list[GLMParagraph]] | None = None,
) -> str:
    if not glmocr_dir:
        return ""
    source = item.get("glm_source")
    if not isinstance(source, dict):
        return ""
    chapter = str(source.get("chapter") or chapter_from_unit_id(str(item.get("unit_id") or ""))).strip().lower()
    if not chapter:
        return ""
    if paragraph_cache is None:
        paragraph_cache = {}
    if chapter not in paragraph_cache:
        paragraph_cache[chapter] = load_glm_paragraphs(glmocr_dir, chapter)
    paragraphs = paragraph_cache.get(chapter) or []
    start_order = source.get("start_order")
    end_order = source.get("end_order")
    if not isinstance(start_order, int):
        return ""
    if not isinstance(end_order, int):
        end_order = start_order
    selected = [paragraph.text for paragraph in paragraphs if start_order <= paragraph.order <= end_order]
    return "\n\n".join(selected).strip()


def render_placeholder_as_text(match: re.Match[str]) -> str:
    kind = match.group("kind")
    label = match.group("label")
    if "TABLE" in kind:
        return f"Table {label}"
    return f"Equation {label}"


def _normalize_context_fragment(fragment: str) -> str:
    return re.sub(r"\s+", " ", str(fragment or "")).strip()


def _context_fragments(fragment: str, *, from_end: bool) -> list[str]:
    normalized = _normalize_context_fragment(fragment)
    if not normalized:
        return []

    tokens = normalized.split()
    fragments: list[str] = []
    for size in (12, 8, 6, 4, 3, 2, 1):
        size = min(size, len(tokens))
        if size <= 0:
            continue
        candidate = " ".join(tokens[-size:] if from_end else tokens[:size])
        if candidate and candidate not in fragments:
            fragments.append(candidate)
    return fragments


def _fragment_pattern(fragment: str) -> str:
    parts = [re.escape(part) for part in _normalize_context_fragment(fragment).split(" ") if part]
    return r"\s+".join(parts)


def _splice_placeholder(text: str, start: int, end: int, placeholder: str) -> str:
    prefix = text[:start].rstrip()
    suffix = text[end:].lstrip()
    if prefix and suffix:
        return f"{prefix} {placeholder} {suffix}"
    if prefix:
        return f"{prefix} {placeholder}"
    if suffix:
        return f"{placeholder} {suffix}"
    return placeholder


def _replace_placeholder_by_context(old_content: str, repaired: str, placeholder: str, kind: str) -> str:
    placeholder_index = (old_content or "").find(placeholder)
    if placeholder_index < 0:
        return repaired

    is_table_placeholder = "TABLE" in kind
    prefix_fragments = _context_fragments(old_content[:placeholder_index], from_end=True)
    suffix_fragments = _context_fragments(old_content[placeholder_index + len(placeholder) :], from_end=False)
    if not prefix_fragments:
        return repaired

    for prefix_fragment in prefix_fragments:
        prefix_pattern = _fragment_pattern(prefix_fragment)
        prefix_matches = list(re.finditer(prefix_pattern, repaired, flags=re.IGNORECASE))
        if not prefix_matches:
            continue

        for prefix_match in reversed(prefix_matches):
            insertion_start = prefix_match.end()
            if not suffix_fragments:
                return _splice_placeholder(repaired, insertion_start, insertion_start, placeholder)

            suffix_found = False
            for suffix_fragment in suffix_fragments:
                suffix_pattern = _fragment_pattern(suffix_fragment)
                suffix_match = re.search(suffix_pattern, repaired[insertion_start:], flags=re.IGNORECASE)
                if not suffix_match:
                    continue
                suffix_found = True

                insertion_end = insertion_start + suffix_match.start()
                between = repaired[insertion_start:insertion_end].strip()
                if not between:
                    return _splice_placeholder(repaired, insertion_start, insertion_end, placeholder)

                if is_table_placeholder:
                    between_hint = re.search(r"\btable\b", between, flags=re.IGNORECASE)
                else:
                    between_hint = re.search(r"[\\$^_=]|\b(?:equation|table|formula)\b", between, flags=re.IGNORECASE)
                if len(between) <= 220 or between_hint:
                    return _splice_placeholder(repaired, insertion_start, insertion_end, placeholder)

            if not suffix_found:
                return _splice_placeholder(repaired, insertion_start, insertion_start, placeholder)

    return repaired


def normalize_for_matching(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = STRUCTURED_PLACEHOLDER_RE.sub(render_placeholder_as_text, value)
    value = FLOAT_PLACEHOLDER_RE.sub(" ", value)
    value = DUMMY_TABLE_RE.sub(" ", value)
    value = HTML_TAG_RE.sub(" ", value)
    value = re.sub(r"\\([A-Za-z]+)", r" \1 ", value)
    value = re.sub(r"[_^{}$()[\],.;:!?/\\|+=<>*-]+", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def tokenize_for_matching(text: str) -> set[str]:
    return tokenize_normalized_text(normalize_for_matching(text))


def tokenize_normalized_text(normalized_text: str) -> set[str]:
    return {
        token
        for token in normalized_text.split()
        if len(token) > 2 and token not in STOPWORDS
    }


def placeholder_counter(text: str) -> Counter[str]:
    return Counter(match.group(0) for match in STRUCTURED_PLACEHOLDER_RE.finditer(text or ""))


def single_dollar_count(text: str) -> int:
    return len(re.findall(r"(?<!\$)\$(?!\$)", text or ""))


def has_balanced_inline_math(text: str) -> bool:
    return single_dollar_count(text) % 2 == 0


def bracket_delta(text: str) -> int:
    value = text or ""
    return (value.count("(") - value.count(")")) + (value.count("[") - value.count("]"))


def is_structural_protected_block(text: str) -> bool:
    value = str(text or "")
    return bool(STRUCTURAL_ONLY_RE.fullmatch(value.strip()) or DISPLAY_MATH_RE.search(value))


def issue_codes_for_block(issues: Iterable[dict[str, Any]]) -> list[str]:
    codes = sorted({str(issue.get("code", "")).strip() for issue in issues if issue.get("code")})
    return [code for code in codes if code]


def parse_unit_identity(path: Path, data: dict[str, Any]) -> tuple[str, str, int]:
    unit_id = str(data.get("id") or path.stem)
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    chapter = str(metadata.get("chapter") or "").strip()
    ordinal = 0
    match = CHAPTER_ID_RE.match(unit_id)
    if match:
        chapter = chapter or match.group("chapter").lower()
        if match.group("ordinal"):
            ordinal = int(match.group("ordinal"))
    if not chapter:
        chapter = unit_id.split("_", 1)[0].lower()
    return unit_id, chapter.lower(), ordinal


def iter_structured_units(structured_dir: str | Path) -> Iterable[tuple[Path, dict[str, Any], str, str, int]]:
    root = Path(structured_dir)
    for path in sorted(root.glob("*.json")):
        if path.name in {"formula_library.json", "table_library.json"}:
            continue
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or not isinstance(data.get("blocks"), list):
            continue
        unit_id, chapter, ordinal = parse_unit_identity(path, data)
        yield path, data, unit_id, chapter, ordinal


def simple_audit_block(content: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    value = str(content or "")

    def add(code: str, message: str, matched_value: str = "") -> None:
        issues.append(
            {
                "severity": "error",
                "code": code,
                "message": message,
                "value": matched_value,
            }
        )

    if FLOAT_PLACEHOLDER_RE.search(value):
        add("ocr_residual_marker", "Floating-position marker leaked into block content.")
    if FLOAT_PLACEHOLDER_RE.search(value) or DUMMY_TABLE_RE.search(value):
        add("placeholder_leak", "Floating/table placeholder leaked into block content.")
    if re.search(r"\b[A-Za-z]{3,}-\s+[a-z]{2,}\b", value):
        add("broken_hyphen_word", "Word appears split by a line-break hyphen.")
    if not has_balanced_inline_math(value):
        add("unbalanced_inline_math", "Inline math dollar delimiters are unbalanced.")
    if re.search(r"\$[^$]*\s[_^]\s+[A-Za-z0-9]", value):
        add("spaced_script_math", "Inline math contains whitespace after a subscript or superscript marker.")
    if re.search(r"\$\s*[_^][A-Za-z0-9]", value):
        add("missing_left_operand_math", "Inline math appears to start with a detached script marker.")
    if re.search(r"\([^)]*$", value.strip()) or re.search(r"\[[^\]]*$", value.strip()):
        add("truncated_parenthetical_tail", "Block appears to end inside a parenthetical expression.")
    return issues


def load_audit_issue_map(
    structured_dir: str | Path,
    audit_dir: str | Path | None = None,
) -> dict[tuple[str, int], list[dict[str, Any]]]:
    """Return a map keyed by (unit_id, zero_based_block_index)."""
    if audit_dir:
        report_path = Path(audit_dir) / "structured_quality_audit_report.json"
        if report_path.exists():
            try:
                report = read_json(report_path)
            except (OSError, json.JSONDecodeError):
                report = {}
            issue_map: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
            for file_result in report.get("file_results", []):
                if not isinstance(file_result, dict):
                    continue
                unit_id = str(file_result.get("chunk_id") or Path(str(file_result.get("file", ""))).stem)
                for issue in file_result.get("issues", []):
                    if not isinstance(issue, dict):
                        continue
                    block_index = issue.get("block_index")
                    if isinstance(block_index, int):
                        issue_map[(unit_id, block_index)].append(issue)
            if issue_map:
                return dict(issue_map)

    issue_map = defaultdict(list)
    for _path, data, unit_id, _chapter, _ordinal in iter_structured_units(structured_dir):
        for index, block in enumerate(data.get("blocks", [])):
            if not isinstance(block, dict):
                continue
            for issue in simple_audit_block(str(block.get("content") or "")):
                issue["file"] = f"{unit_id}.json"
                issue["chunk_id"] = unit_id
                issue["block_index"] = index
                issue_map[(unit_id, index)].append(issue)
    return dict(issue_map)


def collect_chapter_ordinals(structured_dir: str | Path) -> tuple[dict[str, int], dict[str, str]]:
    max_ordinal: dict[str, int] = defaultdict(int)
    unit_chapter: dict[str, str] = {}
    for _path, _data, unit_id, chapter, ordinal in iter_structured_units(structured_dir):
        unit_chapter[unit_id] = chapter
        if ordinal > max_ordinal[chapter]:
            max_ordinal[chapter] = ordinal
    return dict(max_ordinal), unit_chapter


def expected_order_for_unit(
    unit_id: str,
    chapter: str,
    max_ordinal_by_chapter: dict[str, int],
    span_count: int,
) -> float | None:
    match = CHAPTER_ID_RE.match(unit_id)
    if not match or not match.group("ordinal") or span_count <= 0:
        return None
    ordinal = int(match.group("ordinal"))
    max_ordinal = max_ordinal_by_chapter.get(chapter, 0)
    if max_ordinal <= 1:
        return None
    return ((ordinal - 1) / max(1, max_ordinal - 1)) * max(0, span_count - 1)


def score_span(
    query_text: str,
    span: GLMSpan,
    expected_order: float | None = None,
    span_count: int = 0,
) -> tuple[float, dict[str, float]]:
    query_norm = normalize_for_matching(query_text)
    span_norm = normalize_for_matching(span.text)
    if not query_norm or not span_norm:
        return 0.0, {"sequence": 0.0, "token": 0.0, "order": 0.0}

    if len(query_norm) > 48 and (query_norm in span_norm or span_norm in query_norm):
        sequence_score = 0.98
    else:
        sequence_score = SequenceMatcher(None, query_norm[:900], span_norm[:900]).ratio()

    query_tokens = tokenize_for_matching(query_text)
    span_tokens = tokenize_for_matching(span.text)
    if query_tokens:
        containment = len(query_tokens & span_tokens) / len(query_tokens)
        union = len(query_tokens | span_tokens) or 1
        jaccard = len(query_tokens & span_tokens) / union
        token_score = 0.72 * containment + 0.28 * jaccard
    else:
        token_score = 0.0

    order_score = 0.5
    if expected_order is not None and span_count > 0:
        tolerance = max(3.0, span_count * 0.22)
        order_score = max(0.0, 1.0 - abs(span.order - expected_order) / tolerance)

    final = 0.56 * sequence_score + 0.34 * token_score + 0.10 * order_score
    return round(final, 4), {
        "sequence": round(sequence_score, 4),
        "token": round(token_score, 4),
        "order": round(order_score, 4),
    }


def score_indexed_span(
    *,
    query_norm: str,
    query_tokens: set[str],
    index: GLMChapterIndex,
    span_index: int,
    expected_order: float | None = None,
) -> tuple[float, dict[str, float]]:
    span_norm = index.span_norms[span_index]
    if not query_norm or not span_norm:
        return 0.0, {"sequence": 0.0, "token": 0.0, "order": 0.0}

    if len(query_norm) > 48 and (query_norm in span_norm or span_norm in query_norm):
        sequence_score = 0.98
    else:
        sequence_score = SequenceMatcher(None, query_norm[:900], span_norm[:900]).ratio()

    span_tokens = index.span_tokens[span_index]
    if query_tokens:
        overlap = len(query_tokens & span_tokens)
        containment = overlap / len(query_tokens)
        union = len(query_tokens | span_tokens) or 1
        jaccard = overlap / union
        token_score = 0.72 * containment + 0.28 * jaccard
    else:
        token_score = 0.0

    order_score = 0.5
    if expected_order is not None and index.spans:
        tolerance = max(3.0, len(index.spans) * 0.22)
        order_score = max(0.0, 1.0 - abs(index.spans[span_index].order - expected_order) / tolerance)

    final = 0.56 * sequence_score + 0.34 * token_score + 0.10 * order_score
    return round(final, 4), {
        "sequence": round(sequence_score, 4),
        "token": round(token_score, 4),
        "order": round(order_score, 4),
    }


def find_best_glm_span(
    old_content: str,
    spans: list[GLMSpan] | GLMChapterIndex,
    expected_order: float | None = None,
) -> tuple[GLMSpan | None, float, dict[str, float]]:
    if isinstance(spans, GLMChapterIndex):
        span_list = spans.spans
        candidate_indices = spans.candidate_indices(old_content, expected_order=expected_order)
        query_norm = normalize_for_matching(old_content)
        query_tokens = tokenize_normalized_text(query_norm)
    else:
        span_list = spans
        candidate_indices = list(range(len(span_list)))
        query_norm = ""
        query_tokens = set()
    best_span: GLMSpan | None = None
    best_score = 0.0
    best_parts: dict[str, float] = {"sequence": 0.0, "token": 0.0, "order": 0.0}
    for span_index in candidate_indices:
        span = span_list[span_index]
        if isinstance(spans, GLMChapterIndex):
            score, parts = score_indexed_span(
                query_norm=query_norm,
                query_tokens=query_tokens,
                index=spans,
                span_index=span_index,
                expected_order=expected_order,
            )
        else:
            score, parts = score_span(old_content, span, expected_order=expected_order, span_count=len(span_list))
        if score > best_score:
            best_span = span
            best_score = score
            best_parts = parts
    return best_span, best_score, best_parts


def replace_label_text_once(text: str, label: str, replacement: str, kind: str) -> str:
    escaped_label = re.escape(label)
    if "TABLE" in kind:
        pattern = rf"{TABLE_TEXT_RE_TEMPLATE.format(label=escaped_label)}|\bTables?\s*\(?{escaped_label}\)?\b|\({escaped_label}\)"
    else:
        pattern = FORMULA_TEXT_RE_TEMPLATE.format(label=escaped_label)
    return re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)


def transfer_structural_placeholders(old_content: str, new_content: str) -> str:
    repaired = new_content
    for match in STRUCTURED_PLACEHOLDER_RE.finditer(old_content or ""):
        placeholder = match.group(0)
        label = match.group("label")
        kind = match.group("kind")
        if placeholder in repaired:
            continue
        repaired_next = replace_label_text_once(repaired, label, placeholder, kind)
        if placeholder not in repaired_next:
            repaired_next = _replace_placeholder_by_context(old_content, repaired_next, placeholder, kind)
        if placeholder not in repaired_next:
            repaired_next = f"{repaired_next.rstrip()} {placeholder}".strip()
        repaired = repaired_next
    return repaired


def candidate_quality_issues(text: str) -> set[str]:
    return {issue["code"] for issue in simple_audit_block(text)}


def validate_candidate(
    old_content: str,
    new_content: str,
    issue_codes: list[str],
    match_score: float,
    review_threshold: float,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    old = str(old_content or "")
    new = str(new_content or "").strip()
    if not new:
        reasons.append("candidate content is empty")
    if is_structural_protected_block(old):
        reasons.append("block contains protected display math or structural-only placeholder")
    if "<table" in new.lower() or "</table" in new.lower():
        reasons.append("candidate contains raw table html")
    if not has_balanced_inline_math(new):
        reasons.append("candidate has unbalanced inline math delimiters")
    if abs(bracket_delta(new)) > max(2, abs(bracket_delta(old)) + 1):
        reasons.append("candidate bracket balance is worse than source")
    old_placeholders = placeholder_counter(old)
    new_placeholders = placeholder_counter(new)
    missing_placeholders = old_placeholders - new_placeholders
    if missing_placeholders:
        reasons.append("candidate drops structured placeholders: " + ", ".join(sorted(missing_placeholders)))
    if ("placeholder_leak" in issue_codes or "ocr_residual_marker" in issue_codes) and FLOAT_PLACEHOLDER_RE.search(new):
        reasons.append("candidate still contains floating placeholder residue")
    if match_score < review_threshold:
        reasons.append(f"match_score {match_score:.2f} below review threshold {review_threshold:.2f}")

    if len(old) >= 80 and new:
        ratio = len(new) / max(1, len(old))
        if ratio < 0.35:
            reasons.append(f"candidate too short compared with source ({ratio:.2f}x)")
        if ratio > 2.60:
            reasons.append(f"candidate too long compared with source ({ratio:.2f}x)")
    return not reasons, reasons


def confidence_for_candidate(
    old_content: str,
    new_content: str,
    issue_codes: list[str],
    match_score: float,
) -> float:
    confidence = match_score
    old_issues = candidate_quality_issues(old_content)
    new_issues = candidate_quality_issues(new_content)
    if (
        ("placeholder_leak" in issue_codes and "placeholder_leak" not in new_issues)
        or ("ocr_residual_marker" in issue_codes and "ocr_residual_marker" not in new_issues)
    ):
        confidence += 0.055
    if old_issues and len(new_issues) < len(old_issues):
        confidence += min(0.08, 0.02 * (len(old_issues) - len(new_issues)))
    if placeholder_counter(old_content) and not (placeholder_counter(old_content) - placeholder_counter(new_content)):
        confidence += 0.025
    return round(max(0.0, min(0.99, confidence)), 4)


def make_rejected_item(
    *,
    unit_id: str,
    block_index: int,
    issue_codes: list[str],
    old_content: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "block_index": block_index,
        "issue_codes": issue_codes,
        "old_content": old_content,
        "new_content": old_content,
        "glm_source": {},
        "match_score": 0.0,
        "confidence": 0.0,
        "action": "no_apply",
        "status": "rejected",
        "reasons": [reason],
        "candidate_content": old_content,
    }


def build_candidate_for_block(
    *,
    unit_id: str,
    chapter: str,
    block_index: int,
    old_content: str,
    issue_codes: list[str],
    spans: list[GLMSpan] | GLMChapterIndex,
    expected_order: float | None,
    auto_threshold: float,
    review_threshold: float,
) -> dict[str, Any]:
    repairable = sorted(set(issue_codes) & REPAIRABLE_ISSUES)
    if not repairable:
        return make_rejected_item(
            unit_id=unit_id,
            block_index=block_index,
            issue_codes=issue_codes,
            old_content=old_content,
            reason="block issue codes are not repairable by GLM prose matching",
        )
    if is_structural_protected_block(old_content):
        return make_rejected_item(
            unit_id=unit_id,
            block_index=block_index,
            issue_codes=issue_codes,
            old_content=old_content,
            reason="protected display math/table/formula block",
        )
    span_count = len(spans.spans) if isinstance(spans, GLMChapterIndex) else len(spans)
    if span_count == 0:
        return make_rejected_item(
            unit_id=unit_id,
            block_index=block_index,
            issue_codes=issue_codes,
            old_content=old_content,
            reason=f"no GLM OCR paragraphs found for {chapter}",
        )
    token_count = len(tokenize_for_matching(old_content))
    relaxed_short_match = bool(set(issue_codes) & SHORT_MATCH_RELAXED_ISSUES) or bool(placeholder_counter(old_content))
    min_tokens = 2 if relaxed_short_match else 4
    if token_count < min_tokens:
        return make_rejected_item(
            unit_id=unit_id,
            block_index=block_index,
            issue_codes=issue_codes,
            old_content=old_content,
            reason=f"not enough source tokens to match safely ({token_count} < {min_tokens})",
        )
    effective_review_threshold = review_threshold
    if relaxed_short_match:
        effective_review_threshold = max(0.0, review_threshold - 0.04)
        if placeholder_counter(old_content):
            effective_review_threshold = min(effective_review_threshold, 0.50)

    span, match_score, score_parts = find_best_glm_span(old_content, spans, expected_order=expected_order)
    if span is None:
        return make_rejected_item(
            unit_id=unit_id,
            block_index=block_index,
            issue_codes=issue_codes,
            old_content=old_content,
            reason="no matching GLM span found",
        )

    new_content = transfer_structural_placeholders(old_content, clean_glm_text(span.text))
    valid, validation_reasons = validate_candidate(
        old_content=old_content,
        new_content=new_content,
        issue_codes=issue_codes,
        match_score=match_score,
        review_threshold=effective_review_threshold,
    )
    confidence = confidence_for_candidate(old_content, new_content, issue_codes, match_score) if valid else 0.0

    if valid and confidence >= auto_threshold:
        action = "auto_apply"
        status = "accepted"
        reasons = [f"matched GLM span with confidence {confidence:.2f}"]
    elif valid and confidence >= effective_review_threshold:
        action = "review"
        status = "needs_review"
        reasons = [f"matched GLM span with confidence {confidence:.2f}"]
    else:
        action = "no_apply"
        status = "rejected"
        reasons = validation_reasons or [f"confidence {confidence:.2f} below review threshold {effective_review_threshold:.2f}"]

    return {
        "unit_id": unit_id,
        "block_index": block_index,
        "issue_codes": issue_codes,
        "old_content": old_content,
        "new_content": new_content if valid else old_content,
        "glm_source": span.source_payload(),
        "match_score": match_score,
        "confidence": confidence,
        "action": action,
        "status": status,
        "reasons": reasons,
        "score_parts": score_parts,
        "candidate_content": new_content,
    }


def should_verify_with_llm(item: dict[str, Any], scope: str = "review") -> bool:
    if isinstance(item.get("llm_verifier"), dict):
        return False
    if item.get("status") not in {"needs_review", "accepted"}:
        return False
    if scope == "review":
        return item.get("action") == "review"
    if scope == "all":
        return True
    content = str(item.get("new_content") or "")
    issue_codes = set(item.get("issue_codes") or [])
    return item.get("action") == "review" or bool(
        {"empty_inline_math", "leading_underscore_math", "spaced_script_math", "unbalanced_inline_math"} & issue_codes
    ) or "$" in content


def patch_item_id(item: dict[str, Any]) -> str:
    return f"{item.get('unit_id')}#{item.get('block_index')}"


def parse_llm_json(raw: str) -> dict[str, Any]:
    text = str(raw or "").strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
        if fence:
            text = fence.group(1).strip()
        else:
            match = re.search(r"\{[\s\S]*\}", text)
            text = match.group(0) if match else text
        parsed = json.loads(text)
    if isinstance(parsed, list):
        return {"items": parsed}
    if not isinstance(parsed, dict):
        raise ValueError("LLM JSON response is not an object")
    return parsed


def review_payload_for_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": patch_item_id(item),
        "unit_id": item.get("unit_id"),
        "block_index": item.get("block_index"),
        "issue_codes": item.get("issue_codes"),
        "old_content": trim_for_llm(str(item.get("old_content") or ""), limit=1200),
        "new_content": trim_for_llm(str(item.get("new_content") or ""), limit=1200),
        "confidence": item.get("confidence"),
        "match_score": item.get("match_score"),
        "reasons": item.get("reasons") or [],
    }


def apply_llm_review_decision(item: dict[str, Any], decision_payload: dict[str, Any]) -> dict[str, Any]:
    decision = str(decision_payload.get("decision") or "").strip().lower()
    reason = str(decision_payload.get("reason") or "llm verifier decision").strip()
    if decision not in LLM_REVIEW_DECISIONS:
        item.setdefault("reasons", []).append(f"llm verifier returned invalid decision: {decision or '<empty>'}")
        return item
    item["llm_verifier"] = {"decision": decision, "reason": reason}
    if decision == "reject":
        item["status"] = "rejected"
        item["action"] = "no_apply"
        item.setdefault("reasons", []).append(f"llm verifier rejected: {reason}")
    elif decision == "review" and item.get("action") == "auto_apply":
        item["status"] = "needs_review"
        item["action"] = "review"
        item.setdefault("reasons", []).append(f"llm verifier requested review: {reason}")
    elif decision == "accept":
        if item.get("action") == "review":
            item["status"] = "accepted"
            item["action"] = "auto_apply"
        item.setdefault("reasons", []).append(f"llm verifier accepted: {reason}")
    return item


def verify_candidate_with_llm(item: dict[str, Any], client: Any) -> dict[str, Any]:
    """Optionally verify one candidate with an LLMClient-like object.

    The hook is intentionally conservative and disabled unless the CLI flag is
    provided. If verification is unavailable or malformed, the deterministic
    decision is left untouched and a note is added.
    """
    if client is None or not hasattr(client, "_post_chat_completion"):
        return item
    payload = {
        "task": "Verify whether a GLM OCR prose repair preserves meaning and structured placeholders.",
        "constraints": [
            "Do not rewrite text.",
            "Reject if formula/table placeholders are dropped or changed.",
            "Reject if display formulas or tables are being replaced.",
            "Return accept, review, or reject only.",
        ],
        "candidate": review_payload_for_item(item),
        "output_schema": {"decision": "accept|review|reject", "reason": "short reason"},
    }
    messages = [
        {"role": "system", "content": "Return strict JSON only. Do not rewrite candidate content."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    try:
        raw = client._post_chat_completion(messages=messages, json_mode=True)
        decision_payload = parse_llm_json(raw)
    except Exception as exc:  # pragma: no cover - remote verifier is optional.
        item.setdefault("reasons", []).append(f"llm verifier unavailable: {exc}")
        return item

    return apply_llm_review_decision(item, decision_payload)


def verify_candidates_with_llm_batch(items: list[dict[str, Any]], client: Any) -> list[dict[str, Any]]:
    if client is None or not hasattr(client, "_post_chat_completion") or not items:
        return items
    payload = {
        "task": "Verify candidate GLM OCR repairs for structured textbook blocks.",
        "constraints": [
            "Return strict JSON only.",
            "Do not rewrite text.",
            "Accept only when new_content is a safer, cleaner version of old_content.",
            "Reject if formula/table placeholders are dropped or changed.",
            "Reject if display formulas, tables, or structural numbering are being replaced.",
            "Use review when evidence is plausible but not decisive.",
        ],
        "items": [review_payload_for_item(item) for item in items],
        "output_schema": {
            "decisions": [
                {"id": "same id from input", "decision": "accept|review|reject", "reason": "short reason"}
            ]
        },
    }
    messages = [
        {"role": "system", "content": "Return strict JSON only. Do not rewrite candidate content."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    try:
        raw = client._post_chat_completion(messages=messages, json_mode=True)
        parsed = parse_llm_json(raw)
    except Exception as exc:  # pragma: no cover - remote verifier is optional.
        for item in items:
            item.setdefault("reasons", []).append(f"llm verifier unavailable: {exc}")
        return items

    decisions = parsed.get("decisions") or parsed.get("items") or []
    by_id = {
        str(decision.get("id") or "").strip(): decision
        for decision in decisions
        if isinstance(decision, dict)
    }
    updated_items: list[dict[str, Any]] = []
    for item in items:
        decision_payload = by_id.get(patch_item_id(item))
        if isinstance(decision_payload, dict):
            updated_items.append(apply_llm_review_decision(item, decision_payload))
        else:
            item.setdefault("reasons", []).append("llm verifier returned no decision for item")
            updated_items.append(item)
    return updated_items


def should_triage_with_llm(item: dict[str, Any], scope: str = "rejected") -> bool:
    if isinstance(item.get("llm_triage"), dict):
        return False
    if item.get("status") != "rejected" or item.get("action") != "no_apply":
        return False
    return scope in {"rejected", "review_rejected", "all"}


def triage_payload_for_item(
    item: dict[str, Any],
    *,
    glmocr_dir: str | Path | None = None,
    paragraph_cache: dict[str, list[GLMParagraph]] | None = None,
) -> dict[str, Any]:
    candidate_content = str(item.get("candidate_content") or "")
    old_content = str(item.get("old_content") or "")
    if not candidate_content or candidate_content == old_content:
        candidate_content = str(item.get("new_content") or "")
    glm_reference_text = resolve_glm_source_text(item, glmocr_dir, paragraph_cache)
    return {
        "id": patch_item_id(item),
        "unit_id": item.get("unit_id"),
        "block_index": item.get("block_index"),
        "issue_codes": item.get("issue_codes"),
        "old_content": trim_for_llm(old_content, limit=1200),
        "candidate_content": trim_for_llm(candidate_content, limit=1200),
        "glm_reference_text": trim_for_llm(glm_reference_text, limit=800),
        "match_score": item.get("match_score"),
        "confidence": item.get("confidence"),
        "rejection_reasons": item.get("reasons") or [],
        "glm_source": item.get("glm_source") or {},
    }


def apply_llm_triage_decision(item: dict[str, Any], decision_payload: dict[str, Any]) -> dict[str, Any]:
    label = str(decision_payload.get("label") or "").strip().lower()
    next_action = str(decision_payload.get("next_action") or "").strip().lower()
    reason = str(decision_payload.get("reason") or "llm triage decision").strip()
    if label not in LLM_TRIAGE_LABELS:
        label = "manual_review"
        reason = f"invalid triage label from LLM; {reason}"
    if next_action not in LLM_TRIAGE_NEXT_ACTIONS:
        if label == "recoverable_prose":
            next_action = "send_to_second_pass"
        elif label == "manual_review":
            next_action = "manual_review"
        else:
            next_action = "keep_rejected"
    item["llm_triage"] = {"label": label, "next_action": next_action, "reason": reason}
    item.setdefault("reasons", []).append(f"llm triage {label}: {reason}")
    return item


def triage_rejected_with_llm(
    item: dict[str, Any],
    client: Any,
    *,
    glmocr_dir: str | Path | None = None,
    paragraph_cache: dict[str, list[GLMParagraph]] | None = None,
) -> dict[str, Any]:
    if client is None or not hasattr(client, "_post_chat_completion"):
        return item
    payload = {
        "task": "Triage a rejected OCR repair candidate. Do not repair it.",
        "constraints": [
            "Do not rewrite text.",
            "Do not add facts.",
            "Do not change structure, numbering, formula blocks, table blocks, or placeholders.",
            "Classify only whether this rejected item should remain rejected or enter a later, more specialized pass.",
        ],
        "labels": sorted(LLM_TRIAGE_LABELS),
        "next_actions": sorted(LLM_TRIAGE_NEXT_ACTIONS),
        "candidate": triage_payload_for_item(
            item,
            glmocr_dir=glmocr_dir,
            paragraph_cache=paragraph_cache,
        ),
        "output_schema": {
            "label": "recoverable_prose|inline_math_candidate|structure_protected|insufficient_evidence|manual_review",
            "next_action": "keep_rejected|send_to_second_pass|manual_review",
            "reason": "short reason",
        },
    }
    messages = [
        {"role": "system", "content": "Return strict JSON only. Do not rewrite candidate content."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    try:
        raw = client._post_chat_completion(messages=messages, json_mode=True)
        decision_payload = parse_llm_json(raw)
    except Exception as exc:  # pragma: no cover - remote verifier is optional.
        item.setdefault("reasons", []).append(f"llm triage unavailable: {exc}")
        return item
    return apply_llm_triage_decision(item, decision_payload)


def triage_rejected_with_llm_batch(
    items: list[dict[str, Any]],
    client: Any,
    *,
    glmocr_dir: str | Path | None = None,
    paragraph_cache: dict[str, list[GLMParagraph]] | None = None,
) -> list[dict[str, Any]]:
    if client is None or not hasattr(client, "_post_chat_completion") or not items:
        return items
    if paragraph_cache is None:
        paragraph_cache = {}
    payload = {
        "task": "Triage rejected OCR repair candidates. Do not repair them.",
        "constraints": [
            "Return strict JSON only.",
            "Do not rewrite text.",
            "Do not add facts.",
            "Keep structure-protected display formula/table blocks rejected.",
            "Use recoverable_prose only for prose blocks that should enter a later deterministic second pass.",
            "Use inline_math_candidate for prose blocks whose main issue is inline math OCR damage.",
            "Use insufficient_evidence when the GLM match or source evidence is too weak.",
        ],
        "labels": sorted(LLM_TRIAGE_LABELS),
        "next_actions": sorted(LLM_TRIAGE_NEXT_ACTIONS),
        "items": [
            triage_payload_for_item(item, glmocr_dir=glmocr_dir, paragraph_cache=paragraph_cache)
            for item in items
        ],
        "output_schema": {
            "decisions": [
                {
                    "id": "same id from input",
                    "label": "recoverable_prose|inline_math_candidate|structure_protected|insufficient_evidence|manual_review",
                    "next_action": "keep_rejected|send_to_second_pass|manual_review",
                    "reason": "short reason",
                }
            ]
        },
    }
    messages = [
        {"role": "system", "content": "Return strict JSON only. Do not rewrite candidate content."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    try:
        raw = client._post_chat_completion(messages=messages, json_mode=True)
        parsed = parse_llm_json(raw)
    except Exception as exc:  # pragma: no cover - remote verifier is optional.
        for item in items:
            item.setdefault("reasons", []).append(f"llm triage unavailable: {exc}")
        return items

    decisions = parsed.get("decisions") or parsed.get("items") or []
    by_id = {
        str(decision.get("id") or "").strip(): decision
        for decision in decisions
        if isinstance(decision, dict)
    }
    updated_items: list[dict[str, Any]] = []
    for item in items:
        decision_payload = by_id.get(patch_item_id(item))
        if isinstance(decision_payload, dict):
            updated_items.append(apply_llm_triage_decision(item, decision_payload))
        else:
            item.setdefault("reasons", []).append("llm triage returned no decision for item")
            updated_items.append(item)
    return updated_items



def verify_patch_with_llm(
    patch_payload: dict[str, Any],
    client: Any,
    *,
    llm_scope: str = "review",
    llm_limit: int = 0,
    llm_batch_size: int = 1,
) -> dict[str, Any]:
    if client is None:
        return patch_payload
    updated_items = [dict(item) for item in patch_payload.get("items", []) if isinstance(item, dict)]
    eligible_indices = [
        index for index, item in enumerate(updated_items) if should_verify_with_llm(item, scope=llm_scope)
    ]
    if llm_limit > 0:
        eligible_indices = eligible_indices[:llm_limit]
    batch_size = max(1, int(llm_batch_size or 1))
    attempted = len(eligible_indices)
    for start in range(0, len(eligible_indices), batch_size):
        chunk_indices = eligible_indices[start : start + batch_size]
        chunk = [updated_items[index] for index in chunk_indices]
        if batch_size == 1:
            chunk = [verify_candidate_with_llm(chunk[0], client)]
        else:
            chunk = verify_candidates_with_llm_batch(chunk, client)
        for index, updated in zip(chunk_indices, chunk):
            updated_items[index] = updated
    verified = sum(
        1
        for index in eligible_indices
        if isinstance(updated_items[index].get("llm_verifier"), dict)
    )
    patch_payload = {**patch_payload, "items": updated_items}
    metadata = dict(patch_payload.get("metadata") or {})
    metadata["verified_at"] = utc_now_iso()
    metadata["llm_scope"] = llm_scope
    metadata["llm_attempted"] = int(metadata.get("llm_attempted", 0) or 0) + attempted
    metadata["llm_verified"] = int(metadata.get("llm_verified", 0) or 0) + verified
    metadata["llm_batch_size"] = batch_size
    status_counts = Counter(str(item.get("status") or "unknown") for item in updated_items)
    action_counts = Counter(str(item.get("action") or "unknown") for item in updated_items)
    metadata["status_counts"] = dict(sorted(status_counts.items()))
    metadata["action_counts"] = dict(sorted(action_counts.items()))
    patch_payload["metadata"] = metadata
    return patch_payload


def triage_patch_with_llm(
    patch_payload: dict[str, Any],
    client: Any,
    *,
    glmocr_dir: str | Path | None = None,
    llm_scope: str = "rejected",
    llm_limit: int = 0,
    llm_batch_size: int = DEFAULT_LLM_BATCH_SIZE,
) -> dict[str, Any]:
    if client is None:
        return patch_payload
    updated_items = [dict(item) for item in patch_payload.get("items", []) if isinstance(item, dict)]
    eligible_indices = [
        index for index, item in enumerate(updated_items) if should_triage_with_llm(item, scope=llm_scope)
    ]
    if llm_limit > 0:
        eligible_indices = eligible_indices[:llm_limit]
    batch_size = max(1, int(llm_batch_size or 1))
    paragraph_cache: dict[str, list[GLMParagraph]] = {}
    attempted = len(eligible_indices)
    for start in range(0, len(eligible_indices), batch_size):
        chunk_indices = eligible_indices[start : start + batch_size]
        chunk = [updated_items[index] for index in chunk_indices]
        if batch_size == 1:
            chunk = [
                triage_rejected_with_llm(
                    chunk[0],
                    client,
                    glmocr_dir=glmocr_dir,
                    paragraph_cache=paragraph_cache,
                )
            ]
        else:
            chunk = triage_rejected_with_llm_batch(
                chunk,
                client,
                glmocr_dir=glmocr_dir,
                paragraph_cache=paragraph_cache,
        )
        for index, updated in zip(chunk_indices, chunk):
            updated_items[index] = updated
    triaged = sum(
        1
        for index in eligible_indices
        if isinstance(updated_items[index].get("llm_triage"), dict)
    )

    patch_payload = {**patch_payload, "items": updated_items}
    metadata = dict(patch_payload.get("metadata") or {})
    metadata["triaged_at"] = utc_now_iso()
    metadata["llm_scope"] = llm_scope
    metadata["llm_triage_attempted"] = int(metadata.get("llm_triage_attempted", 0) or 0) + attempted
    metadata["llm_triaged"] = int(metadata.get("llm_triaged", 0) or 0) + triaged
    metadata["llm_batch_size"] = batch_size
    status_counts = Counter(str(item.get("status") or "unknown") for item in updated_items)
    action_counts = Counter(str(item.get("action") or "unknown") for item in updated_items)
    triage_counts = Counter()
    triage_next_action_counts = Counter()
    for item in updated_items:
        triage = item.get("llm_triage")
        if isinstance(triage, dict):
            triage_counts.update([str(triage.get("label") or "unknown")])
            triage_next_action_counts.update([str(triage.get("next_action") or "unknown")])
    metadata["status_counts"] = dict(sorted(status_counts.items()))
    metadata["action_counts"] = dict(sorted(action_counts.items()))
    metadata["llm_triage_counts"] = dict(sorted(triage_counts.items()))
    metadata["llm_triage_next_action_counts"] = dict(sorted(triage_next_action_counts.items()))
    patch_payload["metadata"] = metadata
    return patch_payload


def build_repair_patch(
    *,
    structured_dir: str | Path,
    glmocr_dir: str | Path,
    audit_dir: str | Path | None = None,
    auto_threshold: float = AUTO_THRESHOLD,
    review_threshold: float = REVIEW_THRESHOLD,
    max_window_paragraphs: int = MAX_WINDOW_PARAGRAPHS,
    limit: int | None = None,
    llm_client: Any = None,
    llm_scope: str = "review",
    llm_limit: int = 0,
) -> dict[str, Any]:
    issue_map = load_audit_issue_map(structured_dir, audit_dir=audit_dir)
    max_ordinal_by_chapter, unit_chapter = collect_chapter_ordinals(structured_dir)
    issue_units = {unit_id for unit_id, _block_index in issue_map}
    chapters = {unit_chapter[unit_id] for unit_id in issue_units if unit_id in unit_chapter}
    glm_index = load_glm_index(glmocr_dir, chapters, max_window=max_window_paragraphs)

    items: list[dict[str, Any]] = []
    processed = 0
    llm_verified = 0
    for _path, data, unit_id, chapter, _ordinal in iter_structured_units(structured_dir):
        blocks = data.get("blocks", [])
        expected_order = expected_order_for_unit(
            unit_id=unit_id,
            chapter=chapter,
            max_ordinal_by_chapter=max_ordinal_by_chapter,
            span_count=len(glm_index.get(chapter).spans) if glm_index.get(chapter) else 0,
        )
        for block_index, block in enumerate(blocks):
            block_issues = issue_map.get((unit_id, block_index), [])
            if not block_issues:
                continue
            issue_codes = issue_codes_for_block(block_issues)
            old_content = str(block.get("content") or "")
            item = build_candidate_for_block(
                unit_id=unit_id,
                chapter=chapter,
                block_index=block_index,
                old_content=old_content,
                issue_codes=issue_codes,
                spans=glm_index.get(chapter) or GLMChapterIndex.build(chapter, []),
                expected_order=expected_order,
                auto_threshold=auto_threshold,
                review_threshold=review_threshold,
            )
            if (
                llm_client is not None
                and should_verify_with_llm(item, scope=llm_scope)
                and (llm_limit <= 0 or llm_verified < llm_limit)
            ):
                item = verify_candidate_with_llm(item, llm_client)
                llm_verified += 1
            items.append(item)
            processed += 1
            if limit is not None and processed >= limit:
                return make_patch_payload(
                    items=items,
                    structured_dir=structured_dir,
                    glmocr_dir=glmocr_dir,
                    audit_dir=audit_dir,
                    auto_threshold=auto_threshold,
                    review_threshold=review_threshold,
                    max_window_paragraphs=max_window_paragraphs,
                    llm_verified=llm_verified,
                    llm_scope=llm_scope if llm_client is not None else "off",
                )

    return make_patch_payload(
        items=items,
        structured_dir=structured_dir,
        glmocr_dir=glmocr_dir,
        audit_dir=audit_dir,
        auto_threshold=auto_threshold,
        review_threshold=review_threshold,
        max_window_paragraphs=max_window_paragraphs,
        llm_verified=llm_verified,
        llm_scope=llm_scope if llm_client is not None else "off",
    )


def make_patch_payload(
    *,
    items: list[dict[str, Any]],
    structured_dir: str | Path,
    glmocr_dir: str | Path,
    audit_dir: str | Path | None,
    auto_threshold: float,
    review_threshold: float,
    max_window_paragraphs: int,
    llm_verified: int = 0,
    llm_scope: str = "off",
) -> dict[str, Any]:
    status_counts = Counter(str(item.get("status") or "unknown") for item in items)
    action_counts = Counter(str(item.get("action") or "unknown") for item in items)
    issue_counts: Counter[str] = Counter()
    for item in items:
        issue_counts.update(item.get("issue_codes") or [])
    return {
        "metadata": {
            "generated_at": utc_now_iso(),
            "structured_dir": str(structured_dir),
            "glmocr_dir": str(glmocr_dir),
            "audit_dir": str(audit_dir) if audit_dir else None,
            "auto_threshold": auto_threshold,
            "review_threshold": review_threshold,
            "max_window_paragraphs": max_window_paragraphs,
            "llm_scope": llm_scope,
            "llm_verified": llm_verified,
            "item_count": len(items),
            "status_counts": dict(sorted(status_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "issue_counts": dict(sorted(issue_counts.items())),
            "block_index_base": 0,
        },
        "items": items,
    }


def apply_repair_patch(
    patch_payload: dict[str, Any],
    structured_dir: str | Path,
    *,
    include_review: bool = False,
) -> dict[str, Any]:
    root = Path(structured_dir)
    applied = 0
    skipped = 0
    touched_files: set[str] = set()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in patch_payload.get("items", []):
        if not isinstance(item, dict):
            continue
        grouped[str(item.get("unit_id") or "")].append(item)

    for unit_id, items in grouped.items():
        if not unit_id:
            skipped += len(items)
            continue
        path = root / f"{unit_id}.json"
        if not path.exists():
            skipped += len(items)
            continue
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            skipped += len(items)
            continue
        blocks = data.get("blocks")
        if not isinstance(blocks, list):
            skipped += len(items)
            continue
        changed = False
        for item in items:
            action = item.get("action")
            if action != "auto_apply" and not (include_review and action == "review"):
                skipped += 1
                continue
            block_index = item.get("block_index")
            if not isinstance(block_index, int) or block_index < 0 or block_index >= len(blocks):
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
    return {
        "applied": applied,
        "skipped": skipped,
        "touched_files": sorted(touched_files),
    }


def render_report(patch_payload: dict[str, Any], apply_result: dict[str, Any] | None = None) -> str:
    metadata = patch_payload.get("metadata", {})
    lines = [
        "# Structured Repair Report",
        "",
        f"Generated at: `{metadata.get('generated_at', '')}`",
        f"Structured dir: `{metadata.get('structured_dir', '')}`",
        f"GLM OCR dir: `{metadata.get('glmocr_dir', '')}`",
        "",
        "## Summary",
        "",
        f"- Items: {metadata.get('item_count', 0)}",
        f"- LLM verifier scope: `{metadata.get('llm_scope', 'off')}`",
        f"- LLM verify attempted: {metadata.get('llm_attempted', 0)}",
        f"- LLM verified: {metadata.get('llm_verified', 0)}",
        f"- LLM triage attempted: {metadata.get('llm_triage_attempted', 0)}",
        f"- LLM triaged: {metadata.get('llm_triaged', 0)}",
    ]
    for key, value in sorted((metadata.get("status_counts") or {}).items()):
        lines.append(f"- Status `{key}`: {value}")
    for key, value in sorted((metadata.get("action_counts") or {}).items()):
        lines.append(f"- Action `{key}`: {value}")
    triage_counts = metadata.get("llm_triage_counts") or {}
    if triage_counts:
        for key, value in sorted(triage_counts.items()):
            lines.append(f"- LLM triage `{key}`: {value}")
    triage_action_counts = metadata.get("llm_triage_next_action_counts") or {}
    if triage_action_counts:
        for key, value in sorted(triage_action_counts.items()):
            lines.append(f"- LLM triage next `{key}`: {value}")
    if apply_result is not None:
        lines.extend(
            [
                "",
                "## Apply Result",
                "",
                f"- Applied: {apply_result.get('applied', 0)}",
                f"- Skipped: {apply_result.get('skipped', 0)}",
                f"- Touched files: {len(apply_result.get('touched_files', []))}",
            ]
        )

    issue_counts = metadata.get("issue_counts") or {}
    if issue_counts:
        lines.extend(["", "## Issue Counts", ""])
        for key, value in sorted(issue_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{key}`: {value}")

    examples = patch_payload.get("items", [])[:12]
    if examples:
        lines.extend(["", "## Examples", ""])
        for item in examples:
            reasons = "; ".join(item.get("reasons") or [])
            lines.append(
                f"- `{item.get('unit_id')}#{item.get('block_index')}` "
                f"{item.get('status')} / {item.get('action')} "
                f"confidence={float(item.get('confidence') or 0):.2f}: {reasons}"
            )
    return "\n".join(lines).strip() + "\n"


def iter_llm_decision_rows(patch_payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for item in patch_payload.get("items", []):
        if not isinstance(item, dict):
            continue
        verifier = item.get("llm_verifier")
        triage = item.get("llm_triage")
        if not isinstance(verifier, dict) and not isinstance(triage, dict):
            continue
        yield {
            "unit_id": item.get("unit_id"),
            "block_index": item.get("block_index"),
            "status": item.get("status"),
            "action": item.get("action"),
            "issue_codes": item.get("issue_codes") or [],
            "llm_verifier": verifier if isinstance(verifier, dict) else None,
            "llm_triage": triage if isinstance(triage, dict) else None,
            "confidence": item.get("confidence"),
            "match_score": item.get("match_score"),
        }


def write_repair_outputs(
    patch_payload: dict[str, Any],
    out_dir: str | Path,
    apply_result: dict[str, Any] | None = None,
) -> None:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    append_jsonl(root / "repair_candidates.jsonl", patch_payload.get("items", []))
    write_json(root / "repair_patch.json", patch_payload)
    (root / "repair_report.md").write_text(render_report(patch_payload, apply_result=apply_result), encoding="utf-8")
    llm_decisions = list(iter_llm_decision_rows(patch_payload))
    if llm_decisions:
        append_jsonl(root / "llm_decisions.jsonl", llm_decisions)
    if apply_result is not None:
        write_json(root / "apply_result.json", apply_result)


def maybe_create_llm_client(enabled: bool) -> Any:
    if not enabled:
        return None
    try:
        from knowledge_engineering.runtime import LLMClient
    except Exception:
        return None
    client = LLMClient()
    if str(getattr(client, "provider", "")).strip().lower() == "local":
        return None
    return client


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair structured OCR chunks using GLM OCR reference text.")
    parser.add_argument("--structured-dir", default="data/structured", help="Structured JSON directory.")
    parser.add_argument("--glmocr-dir", default="data/glmocr_output", help="GLM OCR output directory.")
    parser.add_argument(
        "--audit-dir",
        default="tmp/structured_review/current_2026_04_24",
        help="Directory containing structured_quality_audit_report.json.",
    )
    parser.add_argument("--out", default="tmp/structured_repair/current", help="Output directory for patch/report.")
    parser.add_argument(
        "--mode",
        choices=["patch", "verify", "triage", "apply"],
        default="patch",
        help="Generate patch, verify review items with LLM, triage rejected items with LLM, or apply repairs.",
    )
    parser.add_argument("--patch-path", default="", help="Existing repair_patch.json to apply instead of rebuilding.")
    parser.add_argument("--include-review", action="store_true", help="Apply review items as well as auto_apply items.")
    parser.add_argument("--auto-threshold", type=float, default=AUTO_THRESHOLD)
    parser.add_argument("--review-threshold", type=float, default=REVIEW_THRESHOLD)
    parser.add_argument("--max-window-paragraphs", type=int, default=MAX_WINDOW_PARAGRAPHS)
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum issue blocks to process.")
    parser.add_argument("--llm-verifier", action="store_true", help="Use an optional LLM verifier for selected candidates.")
    parser.add_argument(
        "--llm-scope",
        choices=["review", "risky", "all", "rejected", "review_rejected"],
        default="review",
        help="Candidate set sent to the LLM verifier when --llm-verifier is enabled.",
    )
    parser.add_argument(
        "--llm-limit",
        type=int,
        default=0,
        help="Maximum LLM verifier calls; 0 means no verifier-specific limit.",
    )
    parser.add_argument(
        "--llm-batch-size",
        type=int,
        default=DEFAULT_LLM_BATCH_SIZE,
        help="Number of repair items per LLM request for verify/triage modes.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    patch_path = Path(args.patch_path) if args.patch_path else None
    if args.mode in {"verify", "triage", "apply"} and patch_path and patch_path.exists():
        patch_payload = read_json(patch_path)
    else:
        llm_client = maybe_create_llm_client(args.llm_verifier)
        patch_payload = build_repair_patch(
            structured_dir=args.structured_dir,
            glmocr_dir=args.glmocr_dir,
            audit_dir=args.audit_dir,
            auto_threshold=args.auto_threshold,
            review_threshold=args.review_threshold,
            max_window_paragraphs=args.max_window_paragraphs,
            limit=args.limit or None,
            llm_client=llm_client,
            llm_scope=args.llm_scope,
            llm_limit=max(0, int(args.llm_limit)),
        )

    if args.mode == "verify":
        llm_client = maybe_create_llm_client(True)
        if llm_client is None:
            print("[structured-repair] LLM verifier unavailable; writing patch unchanged")
        patch_payload = verify_patch_with_llm(
            patch_payload,
            llm_client,
            llm_scope=args.llm_scope,
            llm_limit=max(0, int(args.llm_limit)),
            llm_batch_size=max(1, int(args.llm_batch_size)),
        )

    if args.mode == "triage":
        llm_client = maybe_create_llm_client(True)
        if llm_client is None:
            print("[structured-repair] LLM triage unavailable; writing patch unchanged")
        patch_payload = triage_patch_with_llm(
            patch_payload,
            llm_client,
            glmocr_dir=args.glmocr_dir,
            llm_scope=args.llm_scope if args.llm_scope in {"rejected", "review_rejected", "all"} else "rejected",
            llm_limit=max(0, int(args.llm_limit)),
            llm_batch_size=max(1, int(args.llm_batch_size)),
        )

    apply_result = None
    if args.mode == "apply":
        apply_result = apply_repair_patch(
            patch_payload,
            args.structured_dir,
            include_review=bool(args.include_review),
        )

    write_repair_outputs(patch_payload, args.out, apply_result=apply_result)
    print(f"[structured-repair] wrote patch/report to {args.out}")
    if apply_result is not None:
        print(
            "[structured-repair] apply result: "
            f"applied={apply_result['applied']}, skipped={apply_result['skipped']}"
        )


if __name__ == "__main__":
    main()
