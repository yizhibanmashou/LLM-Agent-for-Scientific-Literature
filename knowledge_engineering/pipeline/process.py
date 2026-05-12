"""Process paddle_output LaTeX with the knowledge engineering pipeline.

Usage:
    python -m knowledge_engineering.pipeline.process \
      -i tmp/paddle_output/chapter2_full/main.tex \
      -o data/structured \
      --title "Evolution and Selection of Quantitative Traits"
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable, List

# Ensure repo root is importable when running as a script.
_THIS_FILE = Path(__file__).resolve()


def _detect_repo_root(file_path: Path) -> Path:
    """Locate repo root for both legacy and relocated script paths."""
    for parent in file_path.parents:
        if (parent / "paper2latex").exists() and (parent / "data").exists():
            return parent
    # Fallback for atypical layouts.
    return file_path.parents[1]


REPO_ROOT = _detect_repo_root(_THIS_FILE)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from knowledge_engineering.core.common import (
    chapter_sort_key,
    formula_sort_key,
    normalize_formula_reference_id,
    rows_from_html_table,
    sort_formula_refs,
    sort_table_ref_keys,
    sort_table_refs,
    table_reference_key,
    table_sort_key,
)
from knowledge_engineering.pipeline.process_io import (
    clear_directory,
    derive_chapter_name,
    find_latex_inputs,
    get_split_artifact_dir,
    save_split_artifacts,
)
from knowledge_engineering.pipeline.process_runtime import (
    append_jsonl as _append_jsonl,
    clamp_float as _clamp_float,
    ensure_dir as _ensure_dir,
    numeric_dict_delta as _numeric_dict_delta,
    parse_chapter_allowlist as _parse_chapter_allowlist,
    resolve_effective_llm_phase as _resolve_effective_llm_phase,
    utc_now as _utc_now_iso,
    write_json as _write_json,
)
from knowledge_engineering.core.runtime import (
    DEFAULT_SOURCE_TITLE,
    FormulaLibrary,
    KnowledgeBlock,
    KnowledgeUnit,
    LLMClient,
    TableEntry,
    TableLibrary,
    _build_navigation_units,
    _build_tree,
    _extract_toc_lines,
    _normalize_line,
    _parse_toc_entries,
    build_composite_chunks,
    clean_page_batch,
    extract_semantic_blocks,
)


NOISE_PATTERNS = [
    r"^\d{1,4}$",
    r"^[ivxlcdmIVXLCDM]{1,6}$",
    r"^\[(?:h|t|b|p)\]$",
    r"(?:ISBN|DOI|Copyright|All rights reserved)",
    r"^\d{4}\s*$",
    r"^\\$",
]

FORMULA_LABEL_LINE_PATTERN = re.compile(r"^\((\d+\.\d+(?:\.\d+)?[a-zA-Z]?)\)$")
FIGURE_TABLE_PATTERN = re.compile(
    r"^(?:Figure|Fig\.|Table)\s+\d+(?:\.\d+)?[A-Za-z]?\b",
    re.IGNORECASE,
)
FIGURE_TABLE_PREFIX_PATTERN = re.compile(
    r"^(?P<label>(?:Figure|Fig\.|Table)\s+\d+(?:\.\d+)?[A-Za-z]?)(?P<rest>.*)$",
    re.IGNORECASE,
)
CHAPTER_HEADER_PATTERN = re.compile(r"^CHAPTER\s+\d+\b", re.IGNORECASE)
TOC_LEADER_PATTERN = re.compile(r"(?:\.{4,}|·{4,})")
PLOT_REGRESSION_PATTERN = re.compile(
    r"^\d{4}\s*:\s*[A-Za-z]?\s*=?[-+0-9A-Za-z().=/*^]+\s*$"
)
SHORT_NUMERIC_NOISE_PATTERN = re.compile(r"^[0-9xXyYrR=().,:;+\-/*\s]{5,}$")
NUMBERED_SECTION_PATTERN = re.compile(r"^(?:\d+|[IVXLC]+)\.\s+[A-Z]")
ORDERED_LIST_ITEM_PATTERN = re.compile(r"^\d{1,2}[.)]\s+\S.*[.!?]\s*$")
TITLE_CASE_HEADING_SMALL_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "versus",
    "via",
    "with",
    "without",
}
SAME_LINE_FORMULA_PATTERN = re.compile(
    r"^(?P<formula>.+?)\s*(?P<label>\((?:\d+\.\d+(?:\.\d+)?[a-zA-Z]?)\))$"
)
PAGE_CHAPTER_HEADER_PATTERN = re.compile(r"^\d+\s+CHAPTER\s+\d+\b", re.IGNORECASE)
PAGE_TITLE_PATTERN = re.compile(r"^[A-Z][A-Z\s]{8,}$")

MATH_SYMBOL_HINTS = (
    "=",
    "+",
    "-",
    "/",
    "*",
    "^",
    "<",
    ">",
    "~",
    "|",
    "×",
    "·",
    "≤",
    "≥",
    "≈",
    "≒",
    "＜",
    "＞",
    "﹉",
    "﹍",
    "∑",
    "∫",
    "∏",
    "√",
    "σ",
    "μ",
    "λ",
    "δ",
    "α",
    "β",
    "γ",
    "θ",
    "π",
    "ω",
)
BODY_REFERENCE_LEAD_WORDS = {
    "show",
    "shows",
    "shown",
    "illustrate",
    "illustrates",
    "illustrated",
    "depict",
    "depicts",
    "depicted",
    "summarize",
    "summarizes",
    "summarized",
    "present",
    "presents",
    "presented",
    "provide",
    "provides",
    "provided",
    "compare",
    "compares",
    "compared",
    "give",
    "gives",
    "given",
    "offer",
    "offers",
    "offered",
    "list",
    "lists",
    "listed",
    "plot",
    "plots",
    "plotted",
    "display",
    "displays",
    "displayed",
    "indicate",
    "indicates",
    "indicated",
    "suggest",
    "suggests",
    "suggested",
    "and",
    "or",
    "which",
    "that",
    "while",
    "whereas",
}

SECTION_COMMAND_PATTERN = re.compile(
    r"\\(?P<name>chapter|section|subsection|subsubsection)\*?\{(?P<title>[^{}]+)\}"
)
SECTION_COMMAND_START_PATTERN = re.compile(
    r"\\(?P<name>chapter|section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\]\s*)?\{"
)
BLOCK_MATH_PATTERN = re.compile(
    r"\\begin\{(?P<env>equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?)\}"
    r"(?P<body>[\s\S]*?)"
    r"\\end\{(?P=env)\}"
)
DUMMY_TABLE_ENV_PATTERN = re.compile(
    r"\\begin\{table\}[\s\S]*?Cell\s+1\s*&\s*Cell\s+2[\s\S]*?\\end\{table\}",
    re.IGNORECASE,
)
DISPLAY_BRACKET_MATH_PATTERN = re.compile(r"\\\[(?P<body>[\s\S]*?)\\\]")
DISPLAY_DOLLAR_MATH_PATTERN = re.compile(r"(?<!\$)\$\$(?!\$)[\s\S]*?(?<!\$)\$\$(?!\$)")
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$(?!\$)([^\n$]*?)(?<!\$)\$(?!\$)")
INLINE_STYLE_COMMAND_PATTERN = re.compile(
    r"\\(?:textbf|textit|emph|underline|textrm|textsf|texttt)\{([^{}]*)\}"
)
REFERENCE_COMMAND_PATTERN = re.compile(
    r"\\(?:cite|citet|citep|ref|eqref|pageref)\*?(?:\[[^\]]*\])?\{([^{}]*)\}"
)
LABEL_COMMAND_PATTERN = re.compile(r"\\label\{([^{}]*)\}")
EQUATION_TAG_PATTERN = re.compile(r"\\tag\*?\s*\{\s*([^{}]+?)\s*\}")
EQUATION_ID_PATTERN = re.compile(r"^\d+\.\d+(?:\.\d+)?[a-zA-Z]?$")
INLINE_EQUATION_LABEL_TAIL_PATTERN = re.compile(
    r"\(\s*(\d+\.\d+(?:\.\d+)?)"
    r"(?:\s*\\mathrm\{\s*([a-zA-Z])\s*\}|\s*([a-zA-Z]))?\s*\)\s*$"
)
INLINE_EQUATION_LABEL_BEFORE_ENV_TAIL_PATTERN = re.compile(
    r"\(\s*(\d+\.\d+(?:\.\d+)?)"
    r"(?:\s*\\mathrm\{\s*([a-zA-Z])\s*\}|\s*([a-zA-Z]))?\s*\)"
    r"(?=\s*(?:\\end\{[A-Za-z*]+\}\s*)*$)"
)
GENERIC_COMMAND_PATTERN = re.compile(
    r"\\[A-Za-z@]+(?:\*?)\s*(?:\[[^\]]*\])?\s*(?:\{[^{}]*\})?"
)
DOCUMENT_BODY_PATTERN = re.compile(
    r"\\begin\{document\}(?P<body>[\s\S]*?)\\end\{document\}",
    re.IGNORECASE,
)
TRAILING_PAGE_NUMBER_PATTERN = re.compile(r"^(?P<title>.+?)\s+\d{1,4}$")
NUMBERED_HEADING_PREFIX_PATTERN = re.compile(r"^(?:[A-Z]?\d+|[IVXLC]+)\.\s+", re.IGNORECASE)
ROMAN_CHAPTER_ONLY_PATTERN = re.compile(r"^CHAPTER\s+[IVXLC]+\b$", re.IGNORECASE)
FORMULA_REFERENCE_DUPLICATE_PATTERN = re.compile(
    r"(见公式\((?P<label>\d+\.\d+(?:\.\d+)?[a-zA-Z]?)\))\s*\((?P=label)\)"
)
REPEATED_FORMULA_REFERENCE_PATTERN = re.compile(
    r"(见公式\((?P<label>\d+\.\d+(?:\.\d+)?[a-zA-Z]?)\))(?:\s+\1)+"
)
MID_BLOCK_ROMAN_CHAPTER_PATTERN = re.compile(r"\bCHAPTER\s+[IVXLC]+\b", re.IGNORECASE)
UPPERCASE_SOURCE_TITLE_PATTERN_TEMPLATE = r"(?<![A-Za-z]){title}(?![A-Za-z])"
FRONT_MATTER_HINTS = (
    "OXFORD",
    "UNIVERSITY PRESS",
    "SINAUER",
    "ASSOCIATES",
    "CONTENTS",
)
HEADING_OCR_REPLACEMENTS = {
    "OUANTITATIVE": "QUANTITATIVE",
    "EROM": "FROM",
    "BREEDERS": "BREEDER'S",
    "BURIS": "BURI'S",
}
PUBLISHER_SNIPPET_PATTERN = re.compile(
    r"(?:Published\s+\d{4}\s+by\s+Oxford\s+University\s+Press\.?\s*)?"
    r"(?:O\s+Bruce\s+Walsh\s*&?\s*Michael\s+Lynch\s+\d{4}\.?\s*)?"
    r"(?:Bruce\s+Walsh\s*&?\s*Michael\s+Lynch\s*)?"
    r"(?:Oxford\s+University\s+Press\.?\s*)",
    re.IGNORECASE,
)
PUBLISHER_RESIDUE_PATTERN = re.compile(r"Published\s+\d{4}\s+by\b", re.IGNORECASE)
AUTHOR_BYLINE_PATTERN = re.compile(
    r"(?:Evolution\s+and\s+Selection\s+of\s+[A-Za-z\s]+?)?"
    r"(?:O\s+)?Bruce\s+Walsh\s*[&r]*\s*Michael\s+L\w+\s*"
    r"(?:\d{4}\.?\s*)?",
    re.IGNORECASE,
)
BOOK_CHAPTER_PATTERN = re.compile(r"^(?:\d+\s+)?CHAPTER\s+(?P<num>[0-9IVXLC]+)\s*$", re.IGNORECASE)
TABLE_LABEL_PATTERN = re.compile(r"^Table\s+(?P<label>\d+\.\d+[A-Za-z]?)\b", re.IGNORECASE)
TABLE_REFERENCE_PATTERN = re.compile(
    r"(?<!LW\s)(?<!Lynch and Walsh\s)\bTable\s+(\d+\.\d+[A-Za-z]?)\b",
    re.IGNORECASE,
)
FORMULA_PLACEHOLDER_PATTERN = re.compile(r"^见公式\((?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\)$")
FORMULA_REFERENCE_PATTERN = re.compile(r"见公式\((?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\)")
TABLE_REF_ID_PATTERN = r"(?:\d+\.\d+[A-Za-z]?|inline_\d+)"
TABLE_PLACEHOLDER_PATTERN = re.compile(rf"\[\[TABLE:(?P<label>{TABLE_REF_ID_PATTERN})\]\]", re.IGNORECASE)
TABLE_REFERENCE_PLACEHOLDER_PATTERN = re.compile(rf"\[\[SEE_TABLE:(?P<label>{TABLE_REF_ID_PATTERN})\]\]", re.IGNORECASE)


def extract_command_payload(tex_text: str, command: str) -> str:
    """Extract balanced-brace payload for command like \\title{...}."""
    marker = f"\\{command}" + "{"
    start = tex_text.find(marker)
    if start < 0:
        return ""

    index = start + len(marker)
    depth = 1
    chars: list[str] = []
    while index < len(tex_text):
        ch = tex_text[index]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return "".join(chars)
        chars.append(ch)
        index += 1
    return ""


def is_noise_line(line: str) -> bool:
    """Return True if a line is obvious page/header/footer noise."""
    return any(re.search(pattern, line) for pattern in NOISE_PATTERNS)


def _is_major_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    alpha_ratio = sum(char.isalpha() for char in stripped) / max(len(stripped), 1)
    return (
        len(stripped) > 8
        and stripped.isupper()
        and "$" not in stripped
        and alpha_ratio > 0.65
    )


def _is_structural_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    numbered_section = bool(NUMBERED_SECTION_PATTERN.match(stripped))
    if numbered_section and ORDERED_LIST_ITEM_PATTERN.match(stripped):
        numbered_section = False
    return (
        stripped.startswith("#")
        or _is_major_heading_line(stripped)
        or numbered_section
    )


def _classify_formula_line(line: str) -> str:
    """Classify one OCR line as strong/weak/non-formula for equation reconstruction."""
    stripped = line.strip()
    if not stripped:
        return "non_formula"
    if len(stripped) > 180:
        return "non_formula"
    if FORMULA_LABEL_LINE_PATTERN.fullmatch(stripped):
        return "non_formula"
    if FIGURE_TABLE_PATTERN.match(stripped):
        return "non_formula"
    if CHAPTER_HEADER_PATTERN.match(stripped) or PAGE_CHAPTER_HEADER_PATTERN.match(stripped):
        return "non_formula"
    if TOC_LEADER_PATTERN.search(stripped):
        return "non_formula"

    lower_word_count = len(re.findall(r"\b[a-z]{3,}\b", stripped))
    title_word_count = len(re.findall(r"\b[A-Z][a-z]{2,}\b", stripped))
    alpha_word_count = len(re.findall(r"[A-Za-z]{3,}", stripped))
    digit_count = sum(char.isdigit() for char in stripped)
    bracket_count = sum(stripped.count(char) for char in "()[]{}")
    math_symbol_score = sum(stripped.count(marker) for marker in MATH_SYMBOL_HINTS)
    has_letter_equals = bool(re.search(r"[A-Za-z]\s*=\s*[^ ]", stripped))
    has_dense_parenthetical = bool(re.search(r"[A-Za-z0-9]\([A-Za-z0-9]", stripped))
    contains_math_hint = any(marker in stripped for marker in MATH_SYMBOL_HINTS)
    compact = re.sub(r"\s+", "", stripped)
    line_length = len(stripped)

    if stripped.endswith(".") and alpha_word_count > 6 and "," in stripped:
        return "non_formula"
    if stripped.endswith((".", "?", "!")) and lower_word_count >= 5:
        return "non_formula"
    if title_word_count >= 3 and lower_word_count >= 2:
        return "non_formula"
    if alpha_word_count >= 8 and not contains_math_hint:
        return "non_formula"

    score = 0
    if "=" in stripped:
        score += 3
    if math_symbol_score >= 2:
        score += 1
    if bracket_count >= 2:
        score += 1
    if digit_count >= 1:
        score += 1
    if has_letter_equals:
        score += 1
    if has_dense_parenthetical:
        score += 1
    if compact.startswith(("(", "[", "{")) and bracket_count >= 1:
        score += 1
    if re.search(r"[A-Za-z]{1,3}\([A-Za-z0-9]", stripped):
        score += 1
    if re.search(r"\d+/\d+|\d+\.\d+|\d+[A-Za-z]", stripped):
        score += 1
    if re.search(r"[﹉﹍≈≒≤≥＜＞∑∫σμλαβγδθπω]", stripped):
        score += 2

    if alpha_word_count >= 7:
        score -= 2
    if "," in stripped and alpha_word_count >= 5:
        score -= 2
    if re.fullmatch(r"[A-Za-z ]+", stripped):
        score -= 3
    if lower_word_count >= 5 and "Equation" not in stripped:
        score -= 2

    if line_length <= 40 and contains_math_hint and lower_word_count <= 2:
        score += 1
    if line_length <= 28 and digit_count >= 1 and alpha_word_count <= 1:
        score += 1

    if score >= 4 and lower_word_count <= 3 and alpha_word_count <= 5:
        return "strong"
    if score >= 3 and line_length <= 90 and lower_word_count <= 2 and alpha_word_count <= 4:
        return "strong"
    if score >= 2 and line_length <= 36 and lower_word_count <= 1 and alpha_word_count <= 3:
        return "weak"
    if score >= 1 and line_length <= 24 and lower_word_count == 0 and contains_math_hint:
        return "weak"
    return "non_formula"


def _looks_like_formula_line(line: str) -> bool:
    return _classify_formula_line(line) == "strong"


def _looks_like_formula_fragment(line: str) -> bool:
    return _classify_formula_line(line) in {"strong", "weak"}


def _wrap_same_line_numbered_formula(line: str) -> str:
    stripped = line.strip()
    match = SAME_LINE_FORMULA_PATTERN.match(stripped)
    if not match:
        return line

    formula = match.group("formula").strip()
    label = match.group("label").strip()
    if not _looks_like_formula_line(formula):
        return line

    return f"$$\n{formula}\n$$\n{label}"


def wrap_numbered_formula_lines(text: str) -> str:
    """Convert OCR-style numbered equations into $$...$$ blocks."""
    lines = text.splitlines()
    replacements: dict[int, tuple[list[str], str]] = {}
    consumed: set[int] = set()

    for index, raw_line in enumerate(lines):
        label_line = raw_line.strip()
        if not FORMULA_LABEL_LINE_PATTERN.fullmatch(label_line):
            continue

        formula_lines: list[str] = []
        saw_strong_formula_line = False
        cursor = index - 1
        while cursor >= 0 and len(formula_lines) < 5:
            candidate = lines[cursor].strip()
            if not candidate:
                break
            if cursor in consumed:
                break
            line_kind = _classify_formula_line(candidate)
            if line_kind == "strong":
                saw_strong_formula_line = True
            elif line_kind == "non_formula":
                break
            formula_lines.insert(0, candidate)
            cursor -= 1

        if not formula_lines or not saw_strong_formula_line:
            continue

        while formula_lines and _classify_formula_line(formula_lines[0]) == "weak":
            if len(formula_lines) > 1 and _classify_formula_line(formula_lines[1]) == "strong":
                break
            formula_lines.pop(0)

        while formula_lines and _classify_formula_line(formula_lines[-1]) == "weak":
            if len(formula_lines) > 1 and _classify_formula_line(formula_lines[-2]) == "strong":
                break
            formula_lines.pop()

        if not formula_lines or not any(_classify_formula_line(line) == "strong" for line in formula_lines):
            continue

        start_index = index - len(formula_lines)
        replacements[start_index] = (formula_lines, label_line)
        for consumed_index in range(start_index, index + 1):
            consumed.add(consumed_index)

    normalized_lines: list[str] = []
    index = 0
    while index < len(lines):
        if index in replacements:
            formula_lines, label_line = replacements[index]
            normalized_lines.append("$$")
            normalized_lines.extend(formula_lines)
            normalized_lines.append("$$")
            normalized_lines.append(label_line)
            index += len(formula_lines) + 1
            continue

        if index in consumed:
            index += 1
            continue

        normalized_lines.append(_wrap_same_line_numbered_formula(lines[index]))
        index += 1

    return "\n".join(normalized_lines)


def _looks_like_plot_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped or FORMULA_LABEL_LINE_PATTERN.fullmatch(stripped):
        return False
    if PLOT_REGRESSION_PATTERN.fullmatch(stripped):
        return True
    if stripped in {"x", "y", "X", "Y"}:
        return True
    if SHORT_NUMERIC_NOISE_PATTERN.fullmatch(stripped):
        digit_ratio = sum(char.isdigit() for char in stripped) / max(
            len(stripped.replace(" ", "")),
            1,
        )
        return digit_ratio >= 0.55
    compact = stripped.replace(" ", "")
    if len(compact) >= 8 and sum(char.isdigit() for char in compact) / len(compact) >= 0.75:
        return True
    return False


def _looks_like_toc_entry(title_line: str, next_line: str) -> bool:
    stripped = title_line.strip()
    following = next_line.strip()
    if not stripped:
        return False
    if TOC_LEADER_PATTERN.search(stripped):
        return True
    if (
        following
        and re.fullmatch(r"\d{1,4}", following)
        and 8 <= len(stripped) <= 180
        and not _is_structural_heading_line(stripped)
        and not _looks_like_formula_line(stripped)
        and not FIGURE_TABLE_PATTERN.match(stripped)
    ):
        return True
    return False


def _classify_figure_table_line(line: str) -> str:
    """Return 'caption', 'reference', or 'other' for figure/table-prefixed lines."""
    stripped = line.strip()
    match = FIGURE_TABLE_PREFIX_PATTERN.match(stripped)
    if not match:
        return "other"

    rest = match.group("rest")
    normalized_rest = rest.lstrip(" \t:.-,;")
    if not normalized_rest:
        return "caption"

    words = re.findall(r"[A-Za-z]+", normalized_rest)
    leading_words = [word.lower() for word in words[:3]]

    if rest.lstrip().startswith(","):
        return "reference"
    if leading_words and leading_words[0] in BODY_REFERENCE_LEAD_WORDS:
        return "reference"
    if any(word in BODY_REFERENCE_LEAD_WORDS for word in leading_words[:2]):
        return "reference"
    if normalized_rest[:1].islower():
        return "reference"
    return "caption"


def filter_noise_lines(text: str) -> str:
    """Remove OCR artifacts such as TOC entries, captions, and plot junk."""
    lines = text.splitlines()
    filtered: list[str] = []
    index = 0
    in_caption = False
    last_caption_line = ""
    caption_line_count = 0
    plot_context_budget = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        next_line = lines[index + 1] if index + 1 < len(lines) else ""

        if in_caption:
            if not stripped:
                in_caption = False
                caption_line_count = 0
                plot_context_budget = 0
                index += 1
                continue
            if _is_structural_heading_line(stripped):
                in_caption = False
                caption_line_count = 0
            else:
                continuation = (
                    not re.search(r"[.!?)]\s*$", last_caption_line)
                    or last_caption_line.endswith("-")
                    or stripped.startswith(("(", "["))
                )
                if continuation:
                    last_caption_line = stripped
                    caption_line_count += 1
                    index += 1
                    continue
                in_caption = False
                caption_line_count = 0

        if not stripped:
            if filtered and filtered[-1] != "":
                filtered.append("")
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue

        if is_noise_line(stripped):
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue
        if stripped in {"Contents", "CONTENTS"}:
            plot_context_budget = 0
            index += 1
            continue
        if CHAPTER_HEADER_PATTERN.fullmatch(stripped) or PAGE_CHAPTER_HEADER_PATTERN.fullmatch(stripped):
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue
        if PAGE_TITLE_PATTERN.fullmatch(stripped) and plot_context_budget > 0:
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue
        figure_table_role = _classify_figure_table_line(stripped)
        if figure_table_role == "caption":
            in_caption = True
            last_caption_line = stripped
            caption_line_count = 1
            plot_context_budget = 0
            index += 1
            continue
        if figure_table_role == "reference":
            filtered.append(stripped)
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue
        if _looks_like_plot_noise(stripped):
            plot_context_budget = 4
            index += 1
            continue
        if (
            plot_context_budget > 0
            and not _is_structural_heading_line(stripped)
            and 2 <= len(stripped.split()) <= 8
            and stripped[:1].isupper()
            and stripped[-1:].isalpha()
            and "," not in stripped
            and not re.search(r"[.!?]$", stripped)
        ):
            plot_context_budget = max(plot_context_budget - 1, 0)
            index += 1
            continue
        if _looks_like_toc_entry(stripped, next_line):
            plot_context_budget = 0
            if re.fullmatch(r"\d{1,4}", next_line.strip()):
                index += 2
            else:
                index += 1
            continue

        filtered.append(stripped)
        plot_context_budget = max(plot_context_budget - 1, 0)
        index += 1

    cleaned = "\n".join(filtered)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def preprocess_extracted_text(text: str) -> str:
    """Apply OCR-aware preprocessing before page splitting / LLM cleaning."""
    text = wrap_numbered_formula_lines(text)
    text = filter_noise_lines(text)
    return text.strip()


def clean_text(text: str) -> str:
    """Apply conservative rule-based cleanup before LLM cleaning."""
    lines = text.splitlines()
    cleaned = [line for line in lines if not is_noise_line(line)]
    return "\n".join(cleaned)


def extract_document_body(tex_text: str) -> str:
    """Extract body between \\begin{document} and \\end{document} when present."""
    match = DOCUMENT_BODY_PATTERN.search(tex_text)
    if match:
        return match.group("body")
    return tex_text


def _render_section_heading(name: str, title: str) -> str:
    """Convert a section-like LaTeX title to a markdown-like heading line."""
    level_map = {
        "chapter": "#",
        "section": "#",
        "subsection": "##",
        "subsubsection": "###",
    }
    prefix = level_map.get(name.lower(), "#")
    title = title.strip()
    if not title:
        return "\n"
    return f"\n{prefix} {title}\n"


def replace_section_command(match: re.Match[str]) -> str:
    """Convert simple section-like LaTeX commands to markdown-like headings."""
    return _render_section_heading(match.group("name"), match.group("title"))


def replace_section_commands(text: str) -> str:
    """Convert section commands, including titles with nested math braces."""
    output: list[str] = []
    cursor = 0
    while True:
        match = SECTION_COMMAND_START_PATTERN.search(text, cursor)
        if not match:
            output.append(text[cursor:])
            break

        brace_start = match.end() - 1
        depth = 1
        index = brace_start + 1
        while index < len(text) and depth:
            char = text[index]
            if char == "{" and (index == 0 or text[index - 1] != "\\"):
                depth += 1
            elif char == "}" and (index == 0 or text[index - 1] != "\\"):
                depth -= 1
            index += 1

        if depth:
            output.append(text[cursor:])
            break

        output.append(text[cursor : match.start()])
        title = text[brace_start + 1 : index - 1]
        output.append(_render_section_heading(match.group("name"), title))
        cursor = index

    return "".join(output)


def _combine_document_title_and_first_heading(document_title: str, first_heading: str) -> str:
    title = re.sub(r"\s+", " ", str(document_title or "")).strip()
    heading = re.sub(r"\s+", " ", str(first_heading or "")).strip()
    if not title:
        return heading
    if not heading:
        return title
    if heading.lower().startswith(title.lower()):
        return heading
    separator = " " if title.endswith(":") else ": "
    return f"{title}{separator}{heading}"


def apply_document_title_heading_context(text: str, document_title: str) -> str:
    """Use a TeX document title as the parent of OCR-emitted section headings."""
    title = _normalize_heading_display(document_title)
    if not title:
        return text

    lines = text.splitlines()
    first_heading_index = None
    first_heading_title = ""
    for index, line in enumerate(lines):
        match = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", line.strip())
        if not match:
            continue
        first_heading_index = index
        first_heading_title = match.group("title").strip()
        break

    if first_heading_index is None or not first_heading_title:
        return text
    if _heading_similarity_key(first_heading_title) == _heading_similarity_key(title):
        return text

    lines[first_heading_index] = "# " + _combine_document_title_and_first_heading(title, first_heading_title)
    for index in range(first_heading_index + 1, len(lines)):
        stripped = lines[index].strip()
        if re.match(r"^#(?!#)\s+\S", stripped):
            lines[index] = re.sub(r"^(\s*)#\s+", r"\1## ", lines[index], count=1)
    return "\n".join(lines)


def _extract_equation_id_from_math(math_body: str) -> tuple[str, str]:
    """Extract a normalized equation id from math body and record source."""
    for raw in EQUATION_TAG_PATTERN.findall(math_body or ""):
        candidate = re.sub(r"\s+", "", raw.strip().strip("()"))
        if EQUATION_ID_PATTERN.fullmatch(candidate):
            return candidate, "tag"

    tail = (math_body or "").strip()
    tail_wo_env = re.sub(r"(?:\\end\{[A-Za-z*]+\}\s*)+$", "", tail).rstrip()
    inline_match = INLINE_EQUATION_LABEL_TAIL_PATTERN.search(tail_wo_env)
    if inline_match:
        base = inline_match.group(1)
        suffix = (inline_match.group(2) or inline_match.group(3) or "").strip()
        candidate = f"{base}{suffix}"
        if EQUATION_ID_PATTERN.fullmatch(candidate):
            return candidate, "inline"
    return "", ""


def _render_display_math_block(math_body: str) -> str:
    """Render one display-math block, preserving numbered-equation hints."""
    equation_id, equation_id_source = _extract_equation_id_from_math(math_body)
    cleaned = EQUATION_TAG_PATTERN.sub("", math_body or "")
    cleaned = LABEL_COMMAND_PATTERN.sub("", cleaned)
    if equation_id and equation_id_source == "inline":
        cleaned = INLINE_EQUATION_LABEL_BEFORE_ENV_TAIL_PATTERN.sub("", cleaned).rstrip()
    cleaned = cleaned.strip()
    if not cleaned:
        return "\n"

    rendered = f"\n$$\n{cleaned}\n$$\n"
    if equation_id:
        rendered += f"({equation_id})\n"
    return rendered


def strip_latex_markup(tex_text: str) -> str:
    """Convert LaTeX-heavy text into plain text suitable for downstream chunking."""
    body = extract_document_body(tex_text)
    document_title = extract_command_payload(tex_text, "title")
    # Some paper2latex outputs put the whole OCR text into \title{...}.
    if len(body.strip()) < 200:
        if len(document_title.strip()) > len(body.strip()):
            text = document_title
        else:
            text = body
    else:
        text = body

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = DUMMY_TABLE_ENV_PATTERN.sub("\n\n", text)

    # OCR-derived LaTeX frequently contains literal percentages such as "49% of
    # the time"; stripping inline "%" as comments would truncate prose.
    text = re.sub(r"(?m)^\s*(?<!\\)%.*(?:\n|$)", "\n", text)
    text = text.replace(r"\%", "%")

    # Keep display-math content in $$...$$ so formula extraction can still work.
    text = BLOCK_MATH_PATTERN.sub(
        lambda m: _render_display_math_block(m.group("body")),
        text,
    )
    text = DISPLAY_BRACKET_MATH_PATTERN.sub(
        lambda m: _render_display_math_block(m.group("body")),
        text,
    )

    # Preserve coarse document structure.
    text = replace_section_commands(text)
    text = apply_document_title_heading_context(text, document_title)

    # Protect display-math blocks from plain-text cleanup regexes below.
    protected_math_blocks: list[str] = []

    def _stash_math_block(match: re.Match[str]) -> str:
        token = f"__P2L_DISPLAY_MATH_{len(protected_math_blocks)}__"
        protected_math_blocks.append(match.group(0))
        return f"\n{token}\n"

    text = DISPLAY_DOLLAR_MATH_PATTERN.sub(_stash_math_block, text)

    # Protect inline math before generic LaTeX command cleanup. Without this,
    # commands such as \overline, \sigma, \beta, and \delta collapse into bare
    # underscores in downstream chunk prose.
    protected_inline_math: list[str] = []

    def _stash_inline_math(match: re.Match[str]) -> str:
        token = f"__P2L_INLINE_MATH_{len(protected_inline_math)}__"
        protected_inline_math.append(match.group(0))
        return token

    text = INLINE_MATH_PATTERN.sub(_stash_inline_math, text)

    # Preserve simple formatting commands by keeping their argument text.
    previous = None
    while previous != text:
        previous = text
        text = INLINE_STYLE_COMMAND_PATTERN.sub(r"\1", text)

    # Preserve reference hints as plain tokens.
    text = REFERENCE_COMMAND_PATTERN.sub(lambda m: f" ({m.group(1).strip()}) ", text)
    text = LABEL_COMMAND_PATTERN.sub("", text)

    # Drop remaining generic commands.
    text = GENERIC_COMMAND_PATTERN.sub(" ", text)

    # Remove most remaining braces and normalize whitespace.
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"[ \t]+", " ", text)

    # Restore display-math blocks after generic text cleanup.
    for index, math_block in enumerate(protected_inline_math):
        text = text.replace(f"__P2L_INLINE_MATH_{index}__", math_block)

    # Restore display-math blocks after generic text cleanup.
    for index, math_block in enumerate(protected_math_blocks):
        text = text.replace(f"__P2L_DISPLAY_MATH_{index}__", math_block)

    # Keep equation labels immediately after display formulas so label extraction
    # can bind "(6.x)" to the preceding $$...$$ block.
    text = re.sub(
        r"\$\$\n+\((\d+\.\d+(?:\.\d+)?[A-Za-z]?)\)",
        r"$$\n(\1)",
        text,
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text_for_cleaning(text: str, max_chars: int = 3800) -> List[str]:
    """Split long plain text into pseudo-pages for cleaner/classifier batching."""
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]
    if not paragraphs:
        return []

    pages: List[str] = []
    current_parts: List[str] = []
    current_len = 0

    for paragraph in paragraphs:
        paragraph_len = len(paragraph)
        if current_parts and current_len + paragraph_len + 2 > max_chars:
            pages.append("\n\n".join(current_parts))
            current_parts = [paragraph]
            current_len = paragraph_len
            continue

        current_parts.append(paragraph)
        current_len += paragraph_len + (2 if current_parts else 0)

    if current_parts:
        pages.append("\n\n".join(current_parts))

    return pages


def parse_chapter_range(chapter_range: str) -> tuple[int, int]:
    """Parse CLI range like '1-9' into inclusive numeric bounds."""
    match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", str(chapter_range).strip())
    if not match:
        raise ValueError(f"Invalid chapter range: {chapter_range}")
    start_num = int(match.group(1))
    end_num = int(match.group(2))
    if start_num <= 0 or end_num < start_num:
        raise ValueError(f"Invalid chapter range: {chapter_range}")
    return start_num, end_num


def _extract_book_chapter_number(line: str) -> int | None:
    match = BOOK_CHAPTER_PATTERN.match(line.strip())
    if not match:
        return None

    token = match.group("num")
    if token.isdigit():
        return int(token)
    return _roman_to_int(token)


def split_tex_book(
    plain_text: str,
    chapter_start: int,
    chapter_end: int,
) -> tuple[str, dict[str, str], int | None]:
    """Split one OCR-heavy book text into TOC text and chapter slices."""
    lines = plain_text.splitlines()
    toc_start = next(
        (index for index, line in enumerate(lines) if line.strip().lower() == "contents"),
        None,
    )

    chapter_markers: list[tuple[int, int]] = []
    current_chapter = chapter_start - 1
    scan_start = toc_start + 1 if toc_start is not None else 0
    min_gap = 40

    for index in range(scan_start, len(lines)):
        chapter_num = _extract_book_chapter_number(lines[index])
        if chapter_num is None:
            continue
        if chapter_num < chapter_start:
            continue
        if chapter_num == current_chapter:
            continue
        if not chapter_markers:
            if chapter_num != chapter_start:
                continue
        elif chapter_num <= current_chapter:
            continue
        if chapter_markers and index - chapter_markers[-1][0] < min_gap:
            continue
        chapter_markers.append((index, chapter_num))
        current_chapter = chapter_num
        if chapter_num >= chapter_end + 1:
            break

    relevant_markers = [(idx, num) for idx, num in chapter_markers if chapter_start <= num <= chapter_end]
    stop_marker = next((idx for idx, num in chapter_markers if num == chapter_end + 1), None)
    toc_end = relevant_markers[0][0] if relevant_markers else stop_marker
    if toc_start is not None and toc_end is None:
        # TOC-only input (e.g. standalone 目录 PDF): keep lines until file end.
        toc_end = len(lines)

    toc_text = ""
    if toc_start is not None and toc_end is not None and toc_end > toc_start:
        toc_text = "\n".join(lines[toc_start:toc_end]).strip()

    chapter_segments: dict[str, str] = {}
    for marker_index, (start_index, chapter_num) in enumerate(relevant_markers):
        end_index = stop_marker if marker_index == len(relevant_markers) - 1 else relevant_markers[marker_index + 1][0]
        segment_lines = lines[start_index:end_index]
        chapter_segments[f"chapter{chapter_num}"] = "\n".join(segment_lines).strip()

    return toc_text, chapter_segments, toc_end


def build_toc_outputs_from_text(
    toc_text: str,
    output_dir: str,
    toc_name: str,
    source_file: str,
    source_title: str,
) -> int:
    """Create TOC navigation units and toc_tree.json directly from split OCR text."""
    os.makedirs(output_dir, exist_ok=True)
    normalized_lines = [_normalize_line(line) for line in toc_text.splitlines() if _normalize_line(line)]

    stitched_lines: list[str] = []
    index = 0
    while index < len(normalized_lines):
        current = normalized_lines[index]
        next_line = normalized_lines[index + 1] if index + 1 < len(normalized_lines) else ""
        if _looks_like_toc_entry(current, next_line):
            stitched_lines.append(f"{current} {next_line}".strip())
            index += 2
            continue
        stitched_lines.append(current)
        index += 1

    toc_lines = _extract_toc_lines(stitched_lines)
    entries = _parse_toc_entries(toc_lines)
    nodes, root_nodes = _build_tree(entries)
    units = _build_navigation_units(
        nodes=nodes,
        root_nodes=root_nodes,
        chapter_name=toc_name,
        source_file=source_file,
        source_title=source_title,
    )

    for unit in units:
        output_path = os.path.join(output_dir, f"{unit['id']}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unit, f, ensure_ascii=False, indent=2)

    tree_path = os.path.join(output_dir, f"{toc_name}_toc_tree.json")
    tree_payload = {
        "metadata": {
            "chapter": toc_name,
            "source_file": source_file,
            "total_nodes": len(nodes),
            "root_count": len(root_nodes),
            "navigation_units": len(units),
        },
        "nodes": nodes,
        "root_nodes": root_nodes,
    }
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree_payload, f, ensure_ascii=False, indent=2)

    print(f"\n[TOC] {toc_name}")
    print(f"  Entries: {len(entries)}")
    print(f"  Navigation units: {len(units)}")
    return len(units)


def _normalize_formula_reference_id(reference: str) -> str:
    return normalize_formula_reference_id(reference)


def _formula_sort_key(reference: str) -> tuple[int, int, str]:
    return formula_sort_key(reference)


def sort_formula_reference_ids(references: Iterable[str]) -> list[str]:
    return sort_formula_refs(references)


def _table_sort_key(reference: str) -> tuple[int, int, int, int, int, str]:
    return table_sort_key(reference)


def _chapter_reference_sort_key(chapter_name: str) -> tuple[int, int, str]:
    return chapter_sort_key(chapter_name)


def _table_reference_key(chapter_name: str, table_id: str) -> str:
    return table_reference_key(chapter_name, table_id)


def sort_table_reference_keys(reference_keys: Iterable[str]) -> list[str]:
    return sort_table_ref_keys(reference_keys)


def _backfill_table_references_from_sources(
    units: List[KnowledgeUnit],
    tables: list[TableEntry],
    output_dir: str,
) -> dict[str, int]:
    unit_map = {unit.id: unit for unit in units}
    touched_units: set[str] = set()
    stats = {
        "added_table_references": 0,
        "added_table_reference_keys": 0,
        "units_touched": 0,
    }

    for entry in tables:
        source = entry.source if isinstance(entry.source, dict) else {}
        table_id = str(entry.id or "").strip()
        unit_id = str(source.get("unit_id") or "").strip()
        chapter_name = str(source.get("chapter") or "").strip().lower()
        if not table_id or not unit_id:
            continue
        unit = unit_map.get(unit_id)
        if unit is None:
            continue

        if table_id not in unit.table_references:
            unit.table_references.append(table_id)
            stats["added_table_references"] += 1
            touched_units.add(unit.id)

        key = _table_reference_key(chapter_name or unit.chapter, table_id)
        if key and key not in unit.table_reference_keys:
            unit.table_reference_keys.append(key)
            stats["added_table_reference_keys"] += 1
            touched_units.add(unit.id)

    for unit_id in touched_units:
        unit = unit_map[unit_id]
        unit.table_references = sort_table_reference_ids(unit.table_references)
        unit.table_reference_keys = sort_table_reference_keys(unit.table_reference_keys)
        output_path = os.path.join(output_dir, f"{unit.id}.json")
        unit.save(output_path)

    stats["units_touched"] = len(touched_units)
    return stats


def sort_table_reference_ids(references: Iterable[str]) -> list[str]:
    return sort_table_refs(references)


def _looks_like_table_caption_continuation(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and stripped[:1].islower() and len(stripped.split()) >= 4


def _looks_like_table_body_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if BOOK_CHAPTER_PATTERN.match(stripped) or _is_structural_heading_line(stripped):
        return False
    if TABLE_LABEL_PATTERN.match(stripped) or stripped.startswith("Figure "):
        return False
    if FORMULA_LABEL_LINE_PATTERN.fullmatch(stripped):
        return False
    if len(stripped) > 220 and re.search(r"[.!?]\s*$", stripped):
        return False
    word_count = len(stripped.split())
    if stripped[:1].islower() and word_count >= 7:
        return False
    if word_count >= 8 and re.search(r"[.!?]\s*$", stripped):
        return False
    return True


def _render_simple_table_html(rows: list[list[str]]) -> str:
    cells: list[str] = []
    for row in rows:
        cell_html = "".join(f"<td>{value}</td>" for value in row)
        cells.append(f"<tr>{cell_html}</tr>")
    return "<table border=\"1\">" + "".join(cells) + "</table>"


def _normalize_match_text(text: str) -> str:
    normalized = str(text or "").lower()
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", normalized, flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def _extract_rows_from_html_table(table_html: str) -> list[list[str]]:
    return rows_from_html_table(table_html)


def _bbox_center_from_list(bbox: list[float] | None) -> tuple[float, float] | None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    try:
        x1, y1, x2, y2 = (float(item) for item in bbox)
    except (TypeError, ValueError):
        return None
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return ((left + right) / 2.0, (top + bottom) / 2.0)


def _bbox_distance(left_bbox: list[float] | None, right_bbox: list[float] | None) -> float:
    left_center = _bbox_center_from_list(left_bbox)
    right_center = _bbox_center_from_list(right_bbox)
    if not left_center or not right_center:
        return 9999.0
    return abs(left_center[1] - right_center[1]) + abs(left_center[0] - right_center[0]) * 0.25


def _layout_order(block: dict[str, Any], fallback: int = 0) -> float:
    for key in ("order", "block_order", "index", "block_id"):
        value = block.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return float(fallback)


def _caption_table_boundary_crossed(
    caption: dict[str, Any],
    table_block: dict[str, Any],
    page_blocks: list[dict[str, Any]],
) -> bool:
    caption_order = _layout_order(caption)
    table_order = _layout_order(table_block)
    if table_order <= caption_order:
        return True

    for block in page_blocks:
        if block is caption or block is table_block:
            continue
        order = _layout_order(block)
        if not (caption_order < order < table_order):
            continue
        content = _collapse_ws(str(block.get("content") or block.get("block_content") or ""))
        if not content:
            continue
        if re.match(r"^(?:Example|Figure)\s+\d+(?:\.\d+)?[A-Za-z]?\b", content, flags=re.IGNORECASE):
            return True
        if TABLE_LABEL_PATTERN.match(content):
            return True
    return False


def _select_numbered_caption_for_table(
    table_block: dict[str, Any],
    table_index: int,
    caption_blocks: list[dict[str, Any]],
    page_blocks: list[dict[str, Any]],
    used_caption_indices: set[int],
) -> tuple[dict[str, Any], str, int] | None:
    candidates: list[tuple[float, float, int, dict[str, Any], str]] = []
    table_order = _layout_order(table_block, table_index)
    for caption_index, caption in enumerate(caption_blocks):
        if caption_index in used_caption_indices:
            continue
        label_match = TABLE_LABEL_PATTERN.match(str(caption.get("content") or ""))
        if not label_match:
            continue
        caption_order = _layout_order(caption, caption_index)
        if caption_order > table_order:
            continue
        if _caption_table_boundary_crossed(caption, table_block, page_blocks):
            continue
        candidates.append(
            (
                table_order - caption_order,
                _bbox_distance(table_block.get("bbox"), caption.get("bbox")),
                caption_index,
                caption,
                label_match.group("label"),
            )
        )
    if not candidates:
        return None
    _gap, _distance, caption_index, caption, label = sorted(candidates)[0]
    return caption, label, caption_index


def _table_entry_sort_key(entry: TableEntry) -> tuple[int, int, int, int, str]:
    numbered = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?([A-Za-z]?)", str(entry.id))
    if numbered:
        suffix = numbered.group(4).lower()
        suffix_rank = 0 if not suffix else ord(suffix) - 96
        subindex = int(numbered.group(3)) if numbered.group(3) else 0
        return (0, int(numbered.group(1)), int(numbered.group(2)), subindex * 100 + suffix_rank, str(entry.id))

    inline = re.fullmatch(r"inline_(\d+)", str(entry.id), flags=re.IGNORECASE)
    if inline:
        return (1, int(inline.group(1)), 0, 0, str(entry.id))

    return (2, 9999, 9999, 9999, str(entry.id))


def _table_entry_quality_score(entry: TableEntry) -> float:
    if str(entry.table_type or "").lower() == "missing":
        return -1000.0
    row_count = len(entry.rows or [])
    cell_count = sum(len(row) for row in (entry.rows or []))
    content_size = sum(len(str(cell)) for row in (entry.rows or []) for cell in row)
    title_size = len(str(entry.title or ""))
    html_size = len(str(entry.html or ""))

    score = (
        row_count * 20.0
        + cell_count * 6.0
        + min(240.0, content_size / 8.0)
        + min(90.0, title_size / 6.0)
        + min(50.0, html_size / 60.0)
    )
    if re.search(r"\bCell\s+1\b", str(entry.html or ""), flags=re.IGNORECASE):
        score -= 120.0
    if str(entry.table_type or "").lower() == "inline":
        score += 8.0
    return score


def _merge_table_entries_by_quality(entries: Iterable[TableEntry]) -> list[TableEntry]:
    merged: dict[str, TableEntry] = {}
    for entry in entries:
        table_id = str(entry.id or "").strip()
        if not table_id:
            continue
        existing = merged.get(table_id)
        if existing is None:
            merged[table_id] = entry
            continue
        if _table_entry_quality_score(entry) > _table_entry_quality_score(existing):
            merged[table_id] = entry
    return sorted(merged.values(), key=_table_entry_sort_key)


def _create_missing_table_body_stubs(
    text: str,
    chapter_name: str,
    existing_table_ids: set[str],
) -> list[TableEntry]:
    """Create explicit review stubs for referenced local tables with no raw body."""
    chapter_number = _chapter_number_from_name(chapter_name)
    if chapter_number is None:
        return []

    local_prefix = f"{chapter_number}."
    candidate_ids: set[str] = set()
    physical_ids: set[str] = set()

    for match in TABLE_PLACEHOLDER_PATTERN.finditer(text or ""):
        table_id = match.group("label")
        if table_id.startswith(local_prefix):
            candidate_ids.add(table_id)
            physical_ids.add(table_id)
    for match in TABLE_REFERENCE_PLACEHOLDER_PATTERN.finditer(text or ""):
        table_id = match.group("label")
        if table_id.startswith(local_prefix):
            candidate_ids.add(table_id)
    for match in TABLE_REFERENCE_PATTERN.finditer(text or ""):
        table_id = match.group(1)
        if table_id.startswith(local_prefix):
            candidate_ids.add(table_id)

    stubs: list[TableEntry] = []
    for table_id in sorted(candidate_ids - set(existing_table_ids), key=_table_sort_key):
        stubs.append(
            TableEntry(
                id=table_id,
                label_format=f"Table {table_id}",
                title=f"Table {table_id} (body not recovered from raw layout)",
                table_type="missing",
                html="",
                rows=[],
                source={
                    "chapter": chapter_name,
                    "extraction_channel": "missing_table_body_stub",
                    "needs_review": True,
                    "has_physical_placeholder": table_id in physical_ids,
                    "reason": "referenced_or_positioned_but_no_raw_table_body",
                },
                description="Placeholder entry to keep table references resolvable while raw table-body recovery is pending.",
            )
        )
    return stubs


PADDLE_RAW_FILE_NAMES = (
    "paddle_raw_api_response.json",
    "paddle_raw_response.json",
)
PADDLE_BODY_ANCHOR_LABELS = {
    "text",
    "paragraph_title",
    "display_formula",
    "formula_number",
    "figure_title",
}
PADDLE_RECOVERABLE_FOOTER_LABELS = {"footer"}
PADDLE_PUBLICATION_FOOTER_PATTERN = re.compile(
    r"(?:Evolution and Selection of Quantitative Traits|Oxford University Press|Published 20\d{2}|"
    r"Bruce Walsh|Michael Lynch|DOI\s+10\.)",
    re.IGNORECASE,
)


def _load_paddle_raw_pages(tex_path: str) -> list[dict[str, Any]]:
    intermediate_dir = Path(tex_path).resolve().parent / "intermediate"
    for file_name in PADDLE_RAW_FILE_NAMES:
        raw_path = intermediate_dir / file_name
        if not raw_path.exists():
            continue
        try:
            payload = json.loads(raw_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if isinstance(payload, list):
            return [page for page in payload if isinstance(page, dict)]

        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        pages = result.get("layoutParsingResults", []) if isinstance(result, dict) else []
        if isinstance(pages, list) and pages:
            return [page for page in pages if isinstance(page, dict)]

    return []


def _paddle_page_rows(page_payload: dict[str, Any]) -> list[dict[str, Any]]:
    pruned = page_payload.get("prunedResult", {}) if isinstance(page_payload.get("prunedResult"), dict) else page_payload
    rows = pruned.get("parsing_res_list", [])
    return rows if isinstance(rows, list) else []


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _block_top(row: dict[str, Any]) -> float:
    bbox = row.get("block_bbox")
    if isinstance(bbox, list) and len(bbox) >= 2:
        try:
            return float(bbox[1])
        except (TypeError, ValueError):
            return 999999.0
    return 999999.0


def _is_recoverable_footer_text(content: str) -> bool:
    text = _collapse_ws(content)
    if len(text) < 24:
        return False
    if is_noise_line(text):
        return False
    if PADDLE_PUBLICATION_FOOTER_PATTERN.search(text):
        return False
    if CHAPTER_HEADER_PATTERN.fullmatch(text) or PAGE_CHAPTER_HEADER_PATTERN.fullmatch(text):
        return False
    if PAGE_TITLE_PATTERN.fullmatch(text):
        return False

    alpha_count = sum(char.isalpha() for char in text)
    if alpha_count < 12:
        return False

    has_sentence_shape = bool(re.search(r"[.!?;,)]", text)) or text[:1].islower()
    has_math = "$" in text or "\\" in text or any(symbol in text for symbol in ("σ", "μ", "δ", "="))
    title_words = re.findall(r"\b[A-Z][A-Za-z'’-]*\b", text)
    all_words = re.findall(r"\b[A-Za-z][A-Za-z'’-]*\b", text)
    title_like = 2 <= len(all_words) <= 14 and len(title_words) / max(1, len(all_words)) >= 0.45
    return has_sentence_shape or has_math or title_like


def _looks_like_recovered_heading(content: str) -> bool:
    text = _collapse_ws(content)
    if not text or text.endswith((".", "?", "!", ";", ",")):
        return False
    if text.lower().startswith(("when ", "where ", "which ", "that ", "and ", "or ", "but ", "because ")):
        return False
    words = re.findall(r"\b[A-Za-z][A-Za-z'’-]*\b", text)
    if not 2 <= len(words) <= 14:
        return False
    title_words = [word for word in words if word[:1].isupper()]
    return len(title_words) / max(1, len(words)) >= 0.45


def _format_recovered_footer_text(content: str) -> str:
    text = _collapse_ws(content)
    if _looks_like_recovered_heading(text):
        return f"## {text}"
    return text


def _ends_with_hyphenated_fragment(content: str) -> bool:
    return _collapse_ws(content).rstrip().endswith(("-", "‐", "‑", "‒", "–"))


def _anchor_starts_with_lowercase_word(anchor: str) -> bool:
    match = re.search(r"[A-Za-z]+", _collapse_ws(anchor))
    return bool(match and match.group(0)[:1].islower())


def _body_anchor_from_rows(rows: list[dict[str, Any]], reverse: bool = False) -> str:
    ordered = sorted(
        (row for row in rows if isinstance(row, dict)),
        key=lambda row: (
            row.get("block_order") is None,
            row.get("block_order") if row.get("block_order") is not None else 999999,
            _block_top(row),
        ),
        reverse=reverse,
    )
    for row in ordered:
        label = str(row.get("block_label") or "").strip().lower()
        content = _collapse_ws(str(row.get("block_content") or ""))
        if label not in PADDLE_BODY_ANCHOR_LABELS or not content:
            continue
        if is_noise_line(content) or PADDLE_PUBLICATION_FOOTER_PATTERN.search(content):
            continue
        if label == "figure_title" and _classify_figure_table_line(content) == "caption":
            continue
        return content
    return ""


def _find_anchor_span(text: str, anchor: str, reverse: bool = False) -> tuple[int, int] | None:
    anchor_text = _collapse_ws(anchor)
    tokens = anchor_text.split()
    if len(tokens) < 4:
        return None
    for token_count in (18, 14, 10, 7, 5):
        if len(tokens) < token_count:
            continue
        pattern = r"\s+".join(re.escape(token) for token in tokens[:token_count])
        matches = list(re.finditer(pattern, text))
        if matches:
            match = matches[-1] if reverse else matches[0]
            return match.start(), match.end()
    return None


def recover_paddle_footer_body_text(plain_text: str, tex_path: str) -> str:
    pages = _load_paddle_raw_pages(tex_path)
    if not pages:
        return plain_text

    updated_text = plain_text
    normalized_seen = _collapse_ws(updated_text)
    recovered_count = 0

    for page_index, page_payload in enumerate(pages):
        rows = _paddle_page_rows(page_payload)
        next_anchor = ""
        if page_index + 1 < len(pages):
            next_anchor = _body_anchor_from_rows(_paddle_page_rows(pages[page_index + 1]))
        candidates = [
            row
            for row in rows
            if isinstance(row, dict)
            and str(row.get("block_label") or "").strip().lower() in PADDLE_RECOVERABLE_FOOTER_LABELS
            and _is_recoverable_footer_text(str(row.get("block_content") or ""))
        ]
        if not candidates:
            continue

        recovered_parts: list[str] = []
        for row in sorted(candidates, key=_block_top):
            content = _collapse_ws(str(row.get("block_content") or ""))
            if _collapse_ws(content) in normalized_seen:
                continue
            if _ends_with_hyphenated_fragment(content) and not _anchor_starts_with_lowercase_word(next_anchor):
                continue
            recovered_parts.append(_format_recovered_footer_text(content))

        if not recovered_parts:
            continue

        insertion = "\n\n".join(recovered_parts).strip()
        inserted = False

        if page_index + 1 < len(pages):
            span = _find_anchor_span(updated_text, next_anchor) if next_anchor else None
            if span:
                start, _ = span
                updated_text = f"{updated_text[:start].rstrip()}\n\n{insertion}\n\n{updated_text[start:].lstrip()}"
                inserted = True

        if not inserted:
            previous_anchor = _body_anchor_from_rows(rows, reverse=True)
            span = _find_anchor_span(updated_text, previous_anchor, reverse=True) if previous_anchor else None
            if span:
                _, end = span
                updated_text = f"{updated_text[:end].rstrip()}\n\n{insertion}\n\n{updated_text[end:].lstrip()}"
                inserted = True

        if inserted:
            recovered_count += len(recovered_parts)
            normalized_seen = _collapse_ws(updated_text)

    if recovered_count:
        print(f"  Paddle footer recovery: restored {recovered_count} body-like footer blocks")
    return updated_text


def _extract_tables_from_paddle_raw(tex_path: str, chapter_name: str) -> list[TableEntry]:
    pages = _load_paddle_raw_pages(tex_path)
    if not pages:
        return []

    entries: list[TableEntry] = []
    inline_index = 0

    for page_index, page_payload in enumerate(pages, start=1):
        rows = _paddle_page_rows(page_payload)
        if not rows:
            continue

        page_blocks: list[dict] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            label = str(row.get("block_label") or "").strip().lower()
            content = str(row.get("block_content") or "").strip()
            bbox = row.get("block_bbox") if isinstance(row.get("block_bbox"), list) else None
            if not content:
                continue
            page_blocks.append(
                {
                    "label": label,
                    "content": content,
                    "bbox": bbox,
                    "order": _layout_order(row, index),
                    "index": index,
                }
            )

        table_blocks = [
            block
            for block in page_blocks
            if block["label"] == "table" and "<table" in block["content"].lower()
        ]
        if not table_blocks:
            continue

        caption_blocks = [
            block
            for block in page_blocks
            if block["label"] in {"figure_title", "text", "paragraph_title"}
            and _classify_figure_table_line(block["content"]) == "caption"
        ]

        used_caption_indices: set[int] = set()
        for table_index, table_block in enumerate(table_blocks):
            table_html = table_block["content"]
            rows = _extract_rows_from_html_table(table_html)
            if not rows:
                continue

            best_caption = None
            best_label: str | None = None
            selected_caption = _select_numbered_caption_for_table(
                table_block=table_block,
                table_index=table_index,
                caption_blocks=caption_blocks,
                page_blocks=page_blocks,
                used_caption_indices=used_caption_indices,
            )
            if selected_caption is not None:
                best_caption, best_label, caption_index = selected_caption
                used_caption_indices.add(caption_index)

            if best_label:
                table_id = best_label
                label_format = f"Table {table_id}"
                table_type = "numbered"
            else:
                inline_index += 1
                table_id = f"inline_{inline_index}"
                label_format = f"Inline Table {inline_index}"
                table_type = "inline"

            title = (best_caption or {}).get("content", "").strip() if isinstance(best_caption, dict) else ""
            if not title:
                title = label_format

            entries.append(
                TableEntry(
                    id=table_id,
                    label_format=label_format,
                    title=title,
                    table_type=table_type,
                    html=table_html,
                    rows=rows,
                    source={
                        "chapter": chapter_name,
                        "page": page_index,
                        "bbox": table_block.get("bbox"),
                        "caption_bbox": (best_caption or {}).get("bbox") if isinstance(best_caption, dict) else None,
                        "extraction_channel": "paddle_raw_layout",
                    },
                )
            )

    return _merge_table_entries_by_quality(entries)


TABLE_ENV_PATTERN = re.compile(
    r"\\begin\{table\*?\}(?P<body>[\s\S]*?)\\end\{table\*?\}",
    re.IGNORECASE,
)
TABULAR_ENV_PATTERN = re.compile(
    r"\\begin\{tabular\*?\}(?:\{[^{}]*\})?(?P<body>[\s\S]*?)\\end\{tabular\*?\}",
    re.IGNORECASE,
)
CAPTION_COMMAND_PATTERN = re.compile(r"\\caption\{(?P<text>[^{}]*)\}", re.IGNORECASE)
TABLE_LABEL_IN_LINE_PATTERN = re.compile(r"\bTable\s+(?P<label>\d+\.\d+[A-Za-z]?)\b", re.IGNORECASE)


def _chapter_number_from_name(chapter_name: str) -> int | None:
    match = re.search(r"chapter(\d+)", str(chapter_name or ""), re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def _line_text_at_position(text: str, position: int) -> str:
    start = text.rfind("\n", 0, position)
    end = text.find("\n", position)
    if start < 0:
        start = 0
    else:
        start += 1
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def _normalize_table_cell(cell: str) -> str:
    value = (cell or "").strip()
    value = re.sub(r"\\hline", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\\(textbf|textit|emph|mathbf|mathrm)\{([^{}]*)\}", r"\2", value)
    value = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _extract_rows_from_table_block(block_text: str) -> list[list[str]]:
    tabular_match = TABULAR_ENV_PATTERN.search(block_text or "")
    if not tabular_match:
        return []

    tabular_body = tabular_match.group("body")
    raw_rows = re.split(r"\\\\\s*", tabular_body)
    rows: list[list[str]] = []
    for raw_row in raw_rows:
        cleaned_row = raw_row.strip()
        if not cleaned_row or cleaned_row == "&":
            continue
        cells = [_normalize_table_cell(cell) for cell in cleaned_row.split("&")]
        cells = [cell for cell in cells if cell]
        if cells:
            rows.append(cells)
    return rows


def _is_dummy_latex_table_block(block_text: str, caption_text: str = "") -> bool:
    normalized = re.sub(r"\s+", " ", block_text or "").strip().lower()
    if "cell 1" in normalized and "cell 2" in normalized:
        return True
    if (caption_text or "").strip().lower() == "table placeholder":
        return True
    return False


def _extract_table_envs_and_replace(
    text: str,
    chapter_name: str,
    *,
    create_table_entries: bool = False,
) -> tuple[str, list[TableEntry]]:
    chapter_number = _chapter_number_from_name(chapter_name)
    label_occurrences: list[dict] = []
    for match in TABLE_REFERENCE_PATTERN.finditer(text or ""):
        label = match.group(1)
        if chapter_number is not None and not label.startswith(f"{chapter_number}."):
            continue
        label_occurrences.append({"label": label, "pos": match.start()})

    tables: list[TableEntry] = []
    used_labels: set[str] = set()
    replacements: list[tuple[int, int, str]] = []

    for match in TABLE_ENV_PATTERN.finditer(text or ""):
        start = match.start()
        end = match.end()
        block_text = match.group(0)

        nearby = sorted(
            label_occurrences,
            key=lambda item: abs(item["pos"] - start),
        )
        table_id = ""
        title_line = ""
        for candidate in nearby:
            if abs(candidate["pos"] - start) > 5000:
                continue
            if candidate["label"] in used_labels:
                continue
            table_id = candidate["label"]
            title_line = _line_text_at_position(text, candidate["pos"])
            break
        if not table_id and nearby:
            candidate = nearby[0]
            if abs(candidate["pos"] - start) <= 5000:
                table_id = candidate["label"]
                title_line = _line_text_at_position(text, candidate["pos"])

        if not table_id:
            continue
        used_labels.add(table_id)

        caption_match = CAPTION_COMMAND_PATTERN.search(block_text)
        caption_text = caption_match.group("text").strip() if caption_match else ""
        is_dummy_table = _is_dummy_latex_table_block(block_text, caption_text)
        if caption_text.lower() == "table placeholder":
            caption_text = ""

        title_text = title_line or caption_text or f"Table {table_id}"
        if not TABLE_LABEL_IN_LINE_PATTERN.search(title_text):
            title_text = f"Table {table_id} {title_text}".strip()
        title_without_label = re.sub(r"^.*?\bTable\s+\d+\.\d+[A-Za-z]?\s*", "", title_text).strip()

        if create_table_entries and not is_dummy_table:
            rows = _extract_rows_from_table_block(block_text)
            if not rows:
                rows = [[title_without_label or f"Table {table_id}"]]
            tables.append(
                TableEntry(
                    id=table_id,
                    label_format=f"Table {table_id}",
                    title=title_text,
                    table_type="numbered",
                    html=_render_simple_table_html(rows),
                    rows=rows,
                    source={"chapter": chapter_name, "extraction_channel": "latex_table_env"},
                )
            )
        placeholder = f"[[TABLE:{table_id}]]"
        replacements.append((start, end, placeholder))

    rewritten = text or ""
    for start, end, replacement in sorted(replacements, key=lambda item: item[0], reverse=True):
        rewritten = f"{rewritten[:start]}{replacement}{rewritten[end:]}"
    return rewritten, tables


def _extract_ocr_table_lines_and_replace(
    text: str,
    chapter_name: str,
    *,
    known_table_ids: set[str] | None = None,
    create_table_entries: bool = False,
) -> tuple[str, list[TableEntry]]:
    known_table_ids = known_table_ids or set()
    lines = text.splitlines()
    rewritten: list[str] = []
    tables: list[TableEntry] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        table_match = TABLE_LABEL_PATTERN.match(stripped)
        if not table_match:
            rewritten.append(lines[index])
            index += 1
            continue

        table_id = table_match.group("label")
        title_lines = [stripped]
        cursor = index + 1
        while cursor < len(lines) and _looks_like_table_caption_continuation(lines[cursor]):
            title_lines.append(lines[cursor].strip())
            cursor += 1

        body_lines: list[str] = []
        while cursor < len(lines):
            candidate = lines[cursor].strip()
            if not candidate:
                if body_lines:
                    cursor += 1
                    break
                cursor += 1
                continue
            if TABLE_LABEL_PATTERN.match(candidate) or candidate.startswith("Figure "):
                break
            if not _looks_like_table_body_line(candidate):
                break
            body_lines.append(candidate)
            cursor += 1

        title_text = " ".join(title_lines)
        if body_lines:
            if create_table_entries:
                rows = [[line] for line in body_lines]
                tables.append(
                    TableEntry(
                        id=table_id,
                        label_format=f"Table {table_id}",
                        title=title_text,
                        table_type="numbered",
                        html=_render_simple_table_html(rows),
                        rows=rows,
                        source={"chapter": chapter_name, "extraction_channel": "ocr_text_lines"},
                    )
                )
            if create_table_entries or table_id in known_table_ids:
                title_without_label = re.sub(r"^Table\s+\d+\.\d+[A-Za-z]?\s*", "", title_text).strip()
                placeholder = f"[[TABLE:{table_id}]]"
                rewritten.append(f"{placeholder} {title_without_label}".strip())
                index = cursor
                continue

        rewritten.append(lines[index])
        index += 1

    return "\n".join(rewritten), tables


def extract_tables_and_replace(
    text: str,
    chapter_name: str,
    *,
    known_table_ids: set[str] | None = None,
    create_text_table_entries: bool = False,
) -> tuple[str, list[TableEntry]]:
    """Place table-location markers and rewrite prose mentions to table references."""
    known_table_ids = known_table_ids or set()
    env_replaced_text, env_tables = _extract_table_envs_and_replace(text, chapter_name)
    replaced_text, ocr_tables = _extract_ocr_table_lines_and_replace(
        env_replaced_text,
        chapter_name,
        known_table_ids=known_table_ids,
        create_table_entries=create_text_table_entries,
    )

    table_map: dict[str, TableEntry] = {}
    for entry in env_tables + ocr_tables:
        existing = table_map.get(entry.id)
        if existing is None:
            table_map[entry.id] = entry
            continue
        existing_score = len(existing.rows) + len(existing.title)
        incoming_score = len(entry.rows) + len(entry.title)
        if incoming_score > existing_score:
            table_map[entry.id] = entry

    tables = list(table_map.values())
    valid_table_ids = {entry.id for entry in tables} | set(known_table_ids)

    def replace_table_reference(match: re.Match[str]) -> str:
        table_id = match.group(1)
        if table_id in valid_table_ids:
            return f"[[SEE_TABLE:{table_id}]]"
        return match.group(0)

    replaced_text = TABLE_REFERENCE_PATTERN.sub(replace_table_reference, replaced_text)
    replaced_text = re.sub(
        r"(\[\[TABLE:\d+\.\d+[A-Za-z]?\]\])\s*\[\[SEE_TABLE:(\d+\.\d+[A-Za-z]?)\]\]",
        r"\1",
        replaced_text,
    )
    return replaced_text, sorted(tables, key=lambda entry: _table_sort_key(entry.id))


def cleanup_chapter_outputs(output_dir: str, chapter_name: str) -> int:
    """Remove stale structured JSON outputs for one chapter before rerun."""
    if not os.path.isdir(output_dir):
        return 0

    removed = 0
    prefix = f"{chapter_name}_"
    for filename in os.listdir(output_dir):
        if filename.startswith(prefix) and filename.endswith(".json"):
            try:
                os.remove(os.path.join(output_dir, filename))
                removed += 1
            except OSError:
                pass
    return removed


def cleanup_toc_outputs(output_dir: str, toc_name: str) -> int:
    """Remove stale TOC navigation/tree outputs for one toc logical name."""
    if not os.path.isdir(output_dir):
        return 0

    removed = 0
    nav_prefix = f"{toc_name}_nav_"
    tree_name = f"{toc_name}_toc_tree.json"
    for filename in os.listdir(output_dir):
        if filename == tree_name or (
            filename.startswith(nav_prefix) and filename.endswith(".json")
        ):
            try:
                os.remove(os.path.join(output_dir, filename))
                removed += 1
            except OSError:
                pass
    return removed


def _roman_to_int(token: str) -> int | None:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    token = token.strip().upper()
    if not token or any(char not in values for char in token):
        return None

    total = 0
    previous = 0
    for char in reversed(token):
        value = values[char]
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total or None


def _normalize_heading_display(text: str) -> str:
    heading = re.sub(r"^#+\s*", "", (text or "").strip())
    if not heading:
        return ""

    heading = re.sub(r"\bCHAPTER\s*([0-9IVXLC]+)\b", r"CHAPTER \1", heading, flags=re.IGNORECASE)

    page_match = TRAILING_PAGE_NUMBER_PATTERN.match(heading)
    if page_match:
        candidate = page_match.group("title").strip()
        if candidate:
            alpha_ratio = sum(char.isalpha() for char in candidate) / max(len(candidate), 1)
            if alpha_ratio > 0.5:
                heading = candidate

    heading = re.sub(r"\s+", " ", heading)
    for wrong, correct in HEADING_OCR_REPLACEMENTS.items():
        heading = re.sub(rf"\b{re.escape(wrong)}\b", correct, heading, flags=re.IGNORECASE)
    return heading.strip()


def _heading_similarity_key(text: str) -> str:
    normalized = _normalize_heading_display(text).upper()
    normalized = normalized.replace("’", "'").replace("‘", "'")
    normalized = normalized.replace("—", " ").replace("-", " ")
    normalized = normalized.replace(".", " ").replace(",", " ")
    normalized = normalized.replace(":", " ").replace(";", " ")
    normalized = TRAILING_PAGE_NUMBER_PATTERN.sub(r"\g<title>", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _canonicalize_chunk_subsections(chunks: List, source_title: str | None = None) -> None:
    seen: list[str] = []
    canonical_by_key: dict[str, str] = {}
    source_title_key = _heading_similarity_key(source_title or "")

    for chunk in chunks:
        for block in chunk.blocks:
            raw_heading = block.subsection or ""
            cleaned = _normalize_heading_display(raw_heading)
            if not cleaned:
                block.subsection = ""
                continue

            current_key = _heading_similarity_key(cleaned)
            if source_title_key and current_key == source_title_key:
                block.subsection = source_title or cleaned
                continue

            best_key = current_key
            best_score = 0.0
            if len(current_key) >= 12:
                current_prefix_match = NUMBERED_HEADING_PREFIX_PATTERN.match(current_key)
                current_prefix = current_prefix_match.group(0).strip() if current_prefix_match else ""
                for existing_key in seen:
                    existing_prefix_match = NUMBERED_HEADING_PREFIX_PATTERN.match(existing_key)
                    existing_prefix = (
                        existing_prefix_match.group(0).strip() if existing_prefix_match else ""
                    )
                    if current_prefix != existing_prefix:
                        continue
                    score = SequenceMatcher(None, current_key, existing_key).ratio()
                    if score > best_score:
                        best_key = existing_key
                        best_score = score

            if best_key != current_key and best_score >= 0.92:
                block.subsection = canonical_by_key[best_key]
                continue

            if current_key not in canonical_by_key:
                canonical_by_key[current_key] = cleaned
                seen.append(current_key)
            block.subsection = canonical_by_key[current_key]


def _normalize_block_heading_metadata(block: Any) -> None:
    subsection = _normalize_heading_display(getattr(block, "subsection", "") or "")
    level_1 = _normalize_heading_display(getattr(block, "section_level_1", "") or "")
    level_2 = _normalize_heading_display(getattr(block, "section_level_2", "") or "")
    display = _normalize_heading_display(getattr(block, "display_heading", "") or subsection)

    if not level_1:
        level_1 = level_2 or display or subsection
    if level_2 and level_2 == level_1:
        level_2 = ""
    if not display:
        display = level_2 or level_1 or subsection
    if not subsection:
        subsection = display

    block.subsection = subsection
    block.section_level_1 = level_1 or None
    block.section_level_2 = level_2 or None
    block.display_heading = display or subsection or level_2 or level_1 or None
    path = [item for item in [block.section_level_1, block.section_level_2] if item]
    block.heading_path = path or ([block.display_heading] if block.display_heading else [])


def _sync_canonicalized_heading_metadata(chunks: List) -> None:
    for chunk in chunks:
        for block in chunk.blocks:
            display = _normalize_heading_display(block.subsection)
            if not display:
                continue
            if getattr(block, "section_level_2", None):
                block.section_level_2 = display
            else:
                block.section_level_1 = display
            block.display_heading = display
            block.heading_path = [
                item for item in [getattr(block, "section_level_1", None), getattr(block, "section_level_2", None)]
                if item
            ]


def _cleanup_formula_reference_artifacts(text: str) -> str:
    text = FORMULA_REFERENCE_DUPLICATE_PATTERN.sub(r"\1", text)
    text = REPEATED_FORMULA_REFERENCE_PATTERN.sub(r"\1", text)
    return text


def _cleanup_block_content(text: str, source_title: str | None = None) -> str:
    cleaned = text or ""
    cleaned = _cleanup_formula_reference_artifacts(cleaned)
    cleaned = MID_BLOCK_ROMAN_CHAPTER_PATTERN.sub(" ", cleaned)
    cleaned = PUBLISHER_SNIPPET_PATTERN.sub(" ", cleaned)
    cleaned = PUBLISHER_RESIDUE_PATTERN.sub(" ", cleaned)
    cleaned = AUTHOR_BYLINE_PATTERN.sub(" ", cleaned)

    if source_title:
        cleaned = re.sub(re.escape(source_title), " ", cleaned, flags=re.IGNORECASE)
        upper_source_title = re.escape(source_title.upper())
        cleaned = re.sub(
            UPPERCASE_SOURCE_TITLE_PATTERN_TEMPLATE.format(title=upper_source_title),
            " ",
            cleaned,
        )

    cleaned = re.sub(r"\s+([,.;:?!])", r"\1", cleaned)
    cleaned = re.sub(r"([(\[])\s+", r"\1", cleaned)
    cleaned = re.sub(r"\s+([)\]])", r"\1", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


def _looks_like_major_section_heading(heading: str) -> bool:
    stripped = _normalize_heading_display(heading)
    if not stripped:
        return False
    if NUMBERED_HEADING_PREFIX_PATTERN.match(stripped):
        return False
    if ROMAN_CHAPTER_ONLY_PATTERN.fullmatch(stripped):
        return False
    if any(hint in stripped.upper() for hint in FRONT_MATTER_HINTS):
        return False
    return (
        _is_major_heading_line(stripped)
        or _looks_like_title_case_section_heading(stripped)
        or (len(stripped.split()) <= 6 and stripped[:1].isupper() and len(stripped) >= 10)
    )


def _usable_metadata_section_heading(heading: str) -> str:
    stripped = _normalize_heading_display(heading)
    if not stripped:
        return ""
    if ROMAN_CHAPTER_ONLY_PATTERN.fullmatch(stripped):
        return ""
    if any(hint in stripped.upper() for hint in FRONT_MATTER_HINTS):
        return ""
    return stripped


def _looks_like_title_case_section_heading(heading: str) -> bool:
    stripped = _normalize_heading_display(heading)
    if not stripped or len(stripped) > 140:
        return False
    if re.search(r"[.!?]\s*$", stripped):
        return False
    text_without_math = INLINE_MATH_PATTERN.sub(" ", stripped)
    words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text_without_math)
    if not 2 <= len(words) <= 14:
        return False
    content_words = [word for word in words if word.lower().strip("'’-") not in TITLE_CASE_HEADING_SMALL_WORDS]
    if len(content_words) < 2:
        return False
    title_like = sum(1 for word in content_words if word[:1].isupper() or word.isupper())
    return title_like >= max(2, int(len(content_words) * 0.8))


def _chunk_formula_chapter_number(formula_refs: List[str]) -> int | None:
    counts: Counter[int] = Counter()
    for reference in formula_refs:
        match = re.match(r"(?:formula_)?(\d+)\.\d+", reference, re.IGNORECASE)
        if match:
            counts[int(match.group(1))] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def _chunk_formula_chapter_counts(formula_refs: List[str]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for reference in formula_refs:
        match = re.match(r"(?:formula_)?(\d+)\.\d+", reference, re.IGNORECASE)
        if match:
            counts[int(match.group(1))] += 1
    return counts


def _explicit_chapter_number_from_subsections(subsections: List[str]) -> int | None:
    for subsection in subsections:
        match = ROMAN_CHAPTER_ONLY_PATTERN.fullmatch(subsection.strip())
        if match:
            roman_token = subsection.strip().split()[-1]
            return _roman_to_int(roman_token)
    return None


def _looks_like_front_matter_chunk(chunk, source_title: str | None = None) -> bool:
    subsections = [_normalize_heading_display(item) for item in chunk.subsections if item.strip()]
    subsection_blob = " ".join(subsections).upper()
    content = " ".join(block.content for block in chunk.blocks).strip()
    content_upper = content.upper()

    numbered_headings = sum(bool(NUMBERED_HEADING_PREFIX_PATTERN.match(item)) for item in subsections)
    long_blocks = sum(block.word_count >= 80 for block in chunk.blocks)
    sentence_like_blocks = sum(bool(re.search(r"[.!?]", block.content)) for block in chunk.blocks)
    short_heading_like_blocks = sum(
        block.word_count <= 20 and not re.search(r"[.!?]", block.content)
        for block in chunk.blocks
    )

    if any(hint in subsection_blob or hint in content_upper for hint in FRONT_MATTER_HINTS):
        return True
    if source_title and source_title.lower() in content.lower() and chunk.word_count < 90:
        return True
    if numbered_headings >= 1 and chunk.word_count < 140 and long_blocks == 0:
        return True
    if (
        chunk.word_count < 80
        and short_heading_like_blocks == len(chunk.blocks)
        and sentence_like_blocks == 0
    ):
        return True
    return False


def _trim_leading_front_matter_chunks(chunks: List, source_title: str | None = None) -> List:
    start_index = 0
    while start_index < len(chunks) and _looks_like_front_matter_chunk(
        chunks[start_index],
        source_title=source_title,
    ):
        start_index += 1

    trimmed = chunks[start_index:]
    return trimmed or chunks


def _infer_chunk_sections(chunks: List) -> List[str]:
    subsection_counts: Counter[str] = Counter()
    for chunk in chunks:
        for subsection in chunk.subsections:
            if _looks_like_major_section_heading(subsection):
                subsection_counts[subsection] += 1

    section_titles: list[str] = []
    chunk_formula_counters: list[Counter[int]] = []
    title_number_votes: dict[str, Counter[int]] = {}
    explicit_title_numbers: dict[str, int] = {}
    current_section_title = ""

    for chunk in chunks:
        metadata_heading = _usable_metadata_section_heading(getattr(chunk, "section_level_2", None) or "")
        if not metadata_heading:
            level_1_heading = _normalize_heading_display(getattr(chunk, "section_level_1", None) or "")
            display_heading = _normalize_heading_display(getattr(chunk, "display_heading", "") or "")
            chunk_subsections = [_normalize_heading_display(item) for item in chunk.subsections if str(item).strip()]
            if (
                level_1_heading
                and len(chunk_subsections) == 1
                and chunk_subsections[0] == level_1_heading
                and display_heading == level_1_heading
            ):
                metadata_heading = _usable_metadata_section_heading(level_1_heading)
        candidates = [item for item in chunk.subsections if _looks_like_major_section_heading(item)]
        selected_title = ""
        if metadata_heading:
            selected_title = metadata_heading
        elif candidates:
            selected_title = max(
                candidates,
                key=lambda item: (
                    subsection_counts.get(item, 0),
                    -len(item),
                    item,
                ),
            )
        elif current_section_title:
            selected_title = current_section_title
        elif chunk.subsections:
            selected_title = chunk.subsections[0]
        else:
            selected_title = "Introduction"

        if selected_title != current_section_title:
            current_section_title = selected_title

        section_titles.append(current_section_title)
        formula_counter = _chunk_formula_chapter_counts(
            [reference for block in chunk.blocks for reference in block.formula_references]
        )
        explicit_number = _explicit_chapter_number_from_subsections(chunk.subsections)
        if explicit_number is not None:
            explicit_title_numbers[current_section_title] = explicit_number
            formula_counter[explicit_number] += 100
        if formula_counter:
            title_number_votes.setdefault(current_section_title, Counter()).update(formula_counter)
        chunk_formula_counters.append(formula_counter)

    ordered_titles: list[str] = []
    for title in section_titles:
        if not ordered_titles or ordered_titles[-1] != title:
            ordered_titles.append(title)

    title_numbers: dict[str, int | None] = {title: None for title in ordered_titles}
    for title, number in explicit_title_numbers.items():
        title_numbers[title] = number

    for title in ordered_titles:
        if title_numbers[title] is not None:
            continue
        votes = title_number_votes.get(title, Counter())
        if not votes:
            continue
        ranked = votes.most_common()
        if len(ranked) == 1:
            title_numbers[title] = ranked[0][0]
            continue
        top_number, top_count = ranked[0]
        second_count = ranked[1][1]
        if top_count >= second_count * 3 and top_count >= 3:
            title_numbers[title] = top_number

    known_positions = [
        (index, title_numbers[title])
        for index, title in enumerate(ordered_titles)
        if title_numbers[title] is not None
    ]
    for left_index in range(len(known_positions) - 1):
        start_pos, start_number = known_positions[left_index]
        end_pos, end_number = known_positions[left_index + 1]
        gap = end_pos - start_pos
        if gap <= 1:
            continue
        if end_number - start_number != gap:
            continue
        for offset in range(1, gap):
            title_numbers[ordered_titles[start_pos + offset]] = start_number + offset

    for index, title in enumerate(ordered_titles):
        if title_numbers[title] is not None:
            continue
        previous_known = next(
            (
                title_numbers[ordered_titles[cursor]]
                for cursor in range(index - 1, -1, -1)
                if title_numbers[ordered_titles[cursor]] is not None
            ),
            None,
        )
        next_known = next(
            (
                title_numbers[ordered_titles[cursor]]
                for cursor in range(index + 1, len(ordered_titles))
                if title_numbers[ordered_titles[cursor]] is not None
            ),
            None,
        )
        if previous_known is not None and next_known is not None and next_known == previous_known + 2:
            title_numbers[title] = previous_known + 1

    chapter_numbers = [title_numbers.get(title) for title in section_titles]

    rendered_sections: list[str] = []
    for title, chapter_number in zip(section_titles, chapter_numbers):
        if chapter_number is not None and title:
            rendered_sections.append(f"Chapter {chapter_number}: {title}")
        else:
            rendered_sections.append(title or "Introduction")
    return rendered_sections


def refine_chunks_for_output(chunks: List, source_title: str | None = None) -> tuple[List, List[str]]:
    """Apply output-focused fixes to chunk metadata and content."""
    for chunk in chunks:
        for block in chunk.blocks:
            block.subsection = _normalize_heading_display(block.subsection)
            _normalize_block_heading_metadata(block)
            block.content = _cleanup_block_content(block.content, source_title=source_title)

    _canonicalize_chunk_subsections(chunks, source_title=source_title)
    _sync_canonicalized_heading_metadata(chunks)
    refined_chunks = _trim_leading_front_matter_chunks(chunks, source_title=source_title)
    sections = _infer_chunk_sections(refined_chunks)
    return refined_chunks, sections


CHUNK_REVIEW_BLOCK_TYPES = {"discussion", "definition", "proposition", "derivation"}
CHUNK_REVIEW_FORMULA_LABEL_PATTERN = re.compile(r"^\d+\.\d+(?:\.\d+)?[A-Za-z]?$")


def _normalize_formula_label_for_review(label: str) -> str:
    value = _normalize_formula_reference_id(label).strip().lower()
    if CHUNK_REVIEW_FORMULA_LABEL_PATTERN.fullmatch(value):
        return value
    return ""


def _extract_formula_labels_for_chunk_review(
    chunk,
    chapter_name: str,
    formula_library: FormulaLibrary,
    max_candidates: int = 0,
) -> list[str]:
    labels: list[str] = []
    for block in chunk.blocks:
        for ref in block.formula_references:
            normalized = _normalize_formula_label_for_review(ref)
            if normalized and normalized not in labels:
                labels.append(normalized)
                if max_candidates > 0 and len(labels) >= max_candidates:
                    return labels[:max_candidates]
        for match in FORMULA_REFERENCE_PATTERN.finditer(block.content or ""):
            normalized = _normalize_formula_label_for_review(match.group("label"))
            if normalized and normalized not in labels:
                labels.append(normalized)
                if max_candidates > 0 and len(labels) >= max_candidates:
                    return labels[:max_candidates]
    for label in formula_library.get_labels(source_chapter=chapter_name):
        normalized = _normalize_formula_label_for_review(label)
        if normalized and normalized not in labels:
            labels.append(normalized)
            if max_candidates > 0 and len(labels) >= max_candidates:
                return labels[:max_candidates]
    if max_candidates > 0:
        return labels[:max_candidates]
    return labels


def _resolve_chunk_review_workers(client: LLMClient | None) -> int:
    raw = (os.getenv("KE_LLM_REVIEW_WORKERS") or "").strip()
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            return 1

    provider = (getattr(client, "provider", "") or "").strip().lower()
    if provider == "deepseek":
        return 8
    return 1


def _resolve_phase_min_confidence(review_phase: int, llm_policy: dict[str, Any]) -> float:
    if review_phase >= 3:
        return float(llm_policy.get("min_confidence_phase3", 0.9))
    if review_phase >= 2:
        return float(llm_policy.get("min_confidence_phase2", 0.78))
    return float(llm_policy.get("min_confidence_phase1", 0.82))


def _apply_chunk_review_result(
    *,
    chunk,
    reviewed_blocks: list,
    allowlist: set[str],
    stats: dict,
    policy: dict[str, Any],
    remaining_type_override_budget: int,
) -> dict[str, Any]:
    result = {
        "applied_any": False,
        "type_overrides_used": 0,
        "accepted_changes": 0,
        "rejected_changes": 0,
        "rejections": [],
    }

    if not isinstance(reviewed_blocks, list):
        result["rejections"].append("review result is not a list")
        return result

    min_confidence = float(policy.get("min_confidence", 0.82))
    allow_type_override = bool(policy.get("allow_type_override", False))
    allow_new_formula_refs = bool(policy.get("allow_new_formula_refs", False))
    max_formula_refs_per_block = max(1, int(policy.get("max_formula_refs_per_block", 4)))
    max_chunk_change_ratio = float(policy.get("max_chunk_change_ratio", 0.6))

    seen_block_positions: set[int] = set()
    pending_changes: list[dict[str, Any]] = []
    type_budget_left = max(0, int(remaining_type_override_budget))

    for item in reviewed_blocks:
        if not isinstance(item, dict):
            result["rejected_changes"] += 1
            result["rejections"].append("item is not a dict")
            continue
        block_pos = item.get("index")
        if not isinstance(block_pos, int) or block_pos < 1 or block_pos > len(chunk.blocks):
            result["rejected_changes"] += 1
            result["rejections"].append(f"invalid block index: {block_pos}")
            continue
        if block_pos in seen_block_positions:
            result["rejected_changes"] += 1
            result["rejections"].append(f"duplicate block index: {block_pos}")
            continue
        seen_block_positions.add(block_pos)

        block = chunk.blocks[block_pos - 1]
        confidence = _clamp_float(item.get("confidence"), default=0.0)
        if confidence < min_confidence:
            result["rejected_changes"] += 1
            result["rejections"].append(
                f"block {block_pos}: confidence {confidence:.2f} < {min_confidence:.2f}"
            )
            continue

        current_type = block.type
        current_refs = list(block.formula_references)

        reviewed_type = item.get("type")
        proposed_type = current_type
        if isinstance(reviewed_type, str) and reviewed_type in CHUNK_REVIEW_BLOCK_TYPES:
            if reviewed_type != current_type:
                if allow_type_override and type_budget_left > 0:
                    proposed_type = reviewed_type
                    type_budget_left -= 1
                else:
                    result["rejected_changes"] += 1
                    if not allow_type_override:
                        result["rejections"].append(
                            f"block {block_pos}: type override disabled for phase"
                        )
                    else:
                        result["rejections"].append(
                            f"block {block_pos}: type override budget exhausted"
                        )

        proposed_refs = current_refs
        if "formula_reference_labels" in item and isinstance(item.get("formula_reference_labels"), list):
            reviewed_refs: list[str] = []
            for raw_label in item["formula_reference_labels"]:
                normalized = _normalize_formula_label_for_review(str(raw_label))
                if not normalized or normalized not in allowlist:
                    continue
                ref_id = f"formula_{normalized}"
                if ref_id not in reviewed_refs:
                    reviewed_refs.append(ref_id)
                if len(reviewed_refs) >= max_formula_refs_per_block:
                    break
            if (
                not allow_new_formula_refs
                and not current_refs
                and reviewed_refs
                and reviewed_refs != current_refs
            ):
                result["rejected_changes"] += 1
                result["rejections"].append(
                    f"block {block_pos}: adding new refs disabled for phase"
                )
            else:
                proposed_refs = reviewed_refs

        if proposed_type == current_type and proposed_refs == current_refs:
            continue

        pending_changes.append(
            {
                "block": block,
                "old_type": current_type,
                "new_type": proposed_type,
                "old_refs": current_refs,
                "new_refs": proposed_refs,
            }
        )

    if len(pending_changes) / max(1, len(chunk.blocks)) > max_chunk_change_ratio:
        stats["guardrail_rejected_chunks"] += 1
        result["rejections"].append(
            "chunk rejected: pending changes exceed max_chunk_change_ratio"
        )
        result["rejected_changes"] += len(pending_changes)
        return result

    for change in pending_changes:
        block = change["block"]
        old_type = change["old_type"]
        new_type = change["new_type"]
        old_refs = change["old_refs"]
        new_refs = change["new_refs"]

        if new_type != old_type:
            stats["type_overrides"] += 1
            result["type_overrides_used"] += 1
        if new_refs != old_refs:
            stats["formula_ref_overrides"] += 1
            stats["formula_ref_added"] += len(set(new_refs) - set(old_refs))
            stats["formula_ref_removed"] += len(set(old_refs) - set(new_refs))
            if not old_refs and new_refs:
                stats["formula_ref_backfills"] += 1

        block.type = new_type
        block.formula_references = new_refs
        result["accepted_changes"] += 1
        result["applied_any"] = True

    return result


def _review_chunks_with_llm(
    *,
    chunks: List,
    chapter_name: str,
    formula_library: FormulaLibrary,
    client: LLMClient | None,
    llm_policy: dict[str, Any],
    artifacts_dir: str,
) -> dict:
    review_phase = _resolve_effective_llm_phase(chapter_name, llm_policy)
    min_confidence = _resolve_phase_min_confidence(review_phase, llm_policy)
    allow_type_override = review_phase >= 3
    allow_new_formula_refs = review_phase >= 2
    max_formula_candidates = max(1, int(llm_policy.get("max_formula_candidates", 120)))

    chapter_block_count = sum(len(chunk.blocks) for chunk in chunks)
    type_override_budget = 0
    if allow_type_override:
        max_type_override_ratio = float(llm_policy.get("max_type_override_ratio", 0.2))
        type_override_budget = max(1, int(chapter_block_count * max_type_override_ratio))

    policy = {
        "phase": review_phase,
        "min_confidence": min_confidence,
        "allow_type_override": allow_type_override,
        "allow_new_formula_refs": allow_new_formula_refs,
        "max_chunk_change_ratio": float(llm_policy.get("max_chunk_change_ratio", 0.6)),
        "max_formula_refs_per_block": max(1, int(llm_policy.get("max_formula_refs_per_block", 4))),
        "max_formula_candidates": max_formula_candidates,
        "type_override_budget": type_override_budget,
    }
    audit_path = os.path.join(
        os.path.abspath(artifacts_dir),
        "llm_audit",
        f"{chapter_name}_chunk_review_phase{review_phase}.jsonl",
    )

    stats = {
        "phase": review_phase,
        "policy": policy,
        "attempted": 0,
        "applied": 0,
        "failed": 0,
        "invalid_output": 0,
        "guardrail_rejected_chunks": 0,
        "type_overrides": 0,
        "formula_ref_overrides": 0,
        "formula_ref_added": 0,
        "formula_ref_removed": 0,
        "formula_ref_backfills": 0,
        "accepted_changes": 0,
        "rejected_changes": 0,
        "reviewed_blocks": chapter_block_count,
        "audit_path": audit_path,
        "warnings": [],
    }
    if review_phase <= 0:
        return stats
    if (
        client is None
        or not hasattr(client, "review_chunk_semantics")
        or str(getattr(client, "provider", "")).strip().lower() == "local"
    ):
        return stats

    jobs: list[dict] = []
    for chunk_index, chunk in enumerate(chunks, start=1):
        candidate_labels = _extract_formula_labels_for_chunk_review(
            chunk=chunk,
            chapter_name=chapter_name,
            formula_library=formula_library,
            max_candidates=max_formula_candidates,
        )
        allowlist = set(candidate_labels)

        block_payload: list[dict] = []
        for block_idx, block in enumerate(chunk.blocks, start=1):
            block_payload.append(
                {
                    "index": block_idx,
                    "rule_type": block.type,
                    "content": block.content,
                    "rule_subsection": block.subsection,
                    "rule_formula_reference_labels": sort_formula_reference_ids(
                        [_normalize_formula_reference_id(ref) for ref in block.formula_references]
                    ),
                }
            )

        formula_payload: list[dict] = []
        for label in candidate_labels:
            formula = formula_library.get_formula(label, source_chapter=chapter_name)
            if formula is None:
                formula = formula_library.get_formula(label, source_chapter="")
            formula_payload.append(
                {
                    "label": label,
                    "latex": formula.latex if formula else "",
                    "formula_type": formula.formula_type if formula else "",
                }
            )

        jobs.append(
            {
                "chunk_index": chunk_index,
                "chunk": chunk,
                "allowlist": allowlist,
                "subsection_hints": chunk.subsections,
                "block_payload": block_payload,
                "formula_payload": formula_payload,
            }
        )

    stats["attempted"] = len(jobs)
    if not jobs:
        return stats

    remaining_type_override_budget = type_override_budget
    audit_records: list[dict[str, Any]] = []

    def _record_audit(job: dict[str, Any], review: Any, apply_result: dict[str, Any], error: str = "") -> None:
        audit_records.append(
            {
                "timestamp_utc": _utc_now_iso(),
                "chapter": chapter_name,
                "chunk_index": job["chunk_index"],
                "phase": review_phase,
                "policy": policy,
                "input": {
                    "subsection_hints": job["subsection_hints"],
                    "blocks": job["block_payload"],
                    "formula_labels": [item.get("label") for item in job["formula_payload"]],
                },
                "llm_output": review if not error else {"error": error},
                "apply_result": apply_result,
            }
        )

    def _process_review(job: dict[str, Any], review: Any) -> None:
        nonlocal remaining_type_override_budget
        reviewed_blocks = review.get("blocks") if isinstance(review, dict) else None
        if not isinstance(reviewed_blocks, list):
            stats["invalid_output"] += 1
            raise ValueError("LLM output missing 'blocks' list")
        apply_result = _apply_chunk_review_result(
            chunk=job["chunk"],
            reviewed_blocks=reviewed_blocks,
            allowlist=job["allowlist"],
            stats=stats,
            policy=policy,
            remaining_type_override_budget=remaining_type_override_budget,
        )
        remaining_type_override_budget = max(
            0,
            remaining_type_override_budget - int(apply_result["type_overrides_used"]),
        )
        stats["accepted_changes"] += int(apply_result["accepted_changes"])
        stats["rejected_changes"] += int(apply_result["rejected_changes"])
        if apply_result["applied_any"]:
            stats["applied"] += 1
        if apply_result["rejections"] and len(stats["warnings"]) < 8:
            stats["warnings"].append(
                f"chunk {chapter_name}_{job['chunk_index']:03d} guardrail: {apply_result['rejections'][0]}"
            )
        _record_audit(job, review, apply_result)

    workers = _resolve_chunk_review_workers(client)
    if workers <= 1 or len(jobs) == 1:
        for job in jobs:
            try:
                review = client.review_chunk_semantics(
                    chapter_name=chapter_name,
                    chunk_index=job["chunk_index"],
                    subsection_hints=job["subsection_hints"],
                    chunk_blocks=job["block_payload"],
                    formulas=job["formula_payload"],
                    phase=review_phase,
                    allow_type_override=allow_type_override,
                    allow_new_formula_refs=allow_new_formula_refs,
                )
                _process_review(job, review)
            except Exception as exc:
                stats["failed"] += 1
                if len(stats["warnings"]) < 5:
                    stats["warnings"].append(
                        f"chunk {chapter_name}_{job['chunk_index']:03d} semantic review failed: {exc}"
                    )
                _record_audit(
                    job,
                    {},
                    {
                        "applied_any": False,
                        "type_overrides_used": 0,
                        "accepted_changes": 0,
                        "rejected_changes": 1,
                        "rejections": [str(exc)],
                    },
                    error=str(exc),
                )
        for record in audit_records:
            _append_jsonl(audit_path, record)
        return stats

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                client.review_chunk_semantics,
                chapter_name=chapter_name,
                chunk_index=job["chunk_index"],
                subsection_hints=job["subsection_hints"],
                chunk_blocks=job["block_payload"],
                formulas=job["formula_payload"],
                phase=review_phase,
                allow_type_override=allow_type_override,
                allow_new_formula_refs=allow_new_formula_refs,
            ): job
            for job in jobs
        }
        for future in as_completed(futures):
            job = futures[future]
            try:
                review = future.result()
                _process_review(job, review)
            except Exception as exc:
                stats["failed"] += 1
                if len(stats["warnings"]) < 5:
                    stats["warnings"].append(
                        f"chunk {chapter_name}_{job['chunk_index']:03d} semantic review failed: {exc}"
                    )
                _record_audit(
                    job,
                    {},
                    {
                        "applied_any": False,
                        "type_overrides_used": 0,
                        "accepted_changes": 0,
                        "rejected_changes": 1,
                        "rejections": [str(exc)],
                    },
                    error=str(exc),
                )

    for record in audit_records:
        _append_jsonl(audit_path, record)

    return stats


def _format_block_content_for_output(block_type: str, content: str) -> str:
    """Rewrite formula/table reference text into structured chunk placeholders."""
    normalized = content.strip()

    def replace_formula_reference(match: re.Match[str]) -> str:
        label = match.group("label")
        return f"[[SEE_FORMULA:{label}]]"

    normalized = FORMULA_REFERENCE_PATTERN.sub(replace_formula_reference, normalized)
    normalized = TABLE_REFERENCE_PATTERN.sub(lambda match: f"[[SEE_TABLE:{match.group(1)}]]", normalized)
    normalized = re.sub(
        r"(\[\[TABLE:(?P<label>\d+\.\d+[A-Za-z]?)\]\])\s*\[\[SEE_TABLE:(?P=label)\]\]",
        r"\1",
        normalized,
    )
    if block_type == "derivation":
        match = re.fullmatch(r"\[\[SEE_FORMULA:(?P<label>\d+\.\d+(?:\.\d+)?[A-Za-z]?)\]\]", normalized)
        if match:
            return f"[[FORMULA:{match.group('label')}]]"

    normalized = re.sub(r"\s{2,}", " ", normalized)
    return normalized.strip()


def assign_table_sources_to_units(units: List[KnowledgeUnit], tables: list[TableEntry]) -> list[TableEntry]:
    """Attach unit/subsection provenance to tables using placeholders and plain mentions."""
    table_map = {entry.id: entry for entry in tables}
    best_candidate: dict[str, tuple[float, int, str, str]] = {}

    for unit_index, unit in enumerate(units):
        subsection = unit.subsections[0] if unit.subsections else ""
        for block in unit.blocks:
            content = block.content or ""
            for match in TABLE_PLACEHOLDER_PATTERN.finditer(content):
                table_id = match.group("label")
                if table_id not in table_map:
                    continue
                score = 3.0
                current = best_candidate.get(table_id)
                if current is None or score > current[0]:
                    best_candidate[table_id] = (score, unit_index, unit.id, subsection)

            for match in TABLE_REFERENCE_PLACEHOLDER_PATTERN.finditer(content):
                table_id = match.group("label")
                if table_id not in table_map:
                    continue
                score = 2.0
                current = best_candidate.get(table_id)
                if current is None or score > current[0]:
                    best_candidate[table_id] = (score, unit_index, unit.id, subsection)

            for match in TABLE_REFERENCE_PATTERN.finditer(content):
                table_id = match.group(1)
                if table_id not in table_map:
                    continue
                score = 1.5 if re.match(rf"^\s*Table\s+{re.escape(table_id)}\b", content) else 1.0
                current = best_candidate.get(table_id)
                if current is None or score > current[0]:
                    best_candidate[table_id] = (score, unit_index, unit.id, subsection)

    unit_match_cache: list[tuple[int, str, str, str]] = []
    for unit_index, unit in enumerate(units):
        subsection = unit.subsections[0] if unit.subsections else ""
        unit_text = " ".join(block.content or "" for block in unit.blocks)
        normalized_unit = _normalize_match_text(f"{subsection} {unit_text}")
        unit_match_cache.append((unit_index, unit.id, subsection, normalized_unit))

    for table_id, entry in table_map.items():
        if table_id in best_candidate:
            continue
        token_source = [entry.title]
        for row in (entry.rows or [])[:4]:
            token_source.extend(str(cell) for cell in row[:4])
        tokens = [
            token
            for token in _normalize_match_text(" ".join(token_source)).split(" ")
            if len(token) >= 3 and token not in {"table", "inline"}
        ]
        if not tokens:
            continue

        best_score = 0.0
        best_match: tuple[int, str, str] | None = None
        for unit_index, unit_id, subsection, normalized_unit in unit_match_cache:
            if not normalized_unit:
                continue
            hit_count = sum(1 for token in tokens if token in normalized_unit)
            if hit_count == 0:
                continue
            score = hit_count / max(1, len(tokens))
            if score > best_score:
                best_score = score
                best_match = (unit_index, unit_id, subsection)

        if best_match and best_score >= 0.16:
            unit_index, unit_id, subsection = best_match
            best_candidate[table_id] = (best_score, unit_index, unit_id, subsection)

    for table_id, entry in table_map.items():
        candidate = best_candidate.get(table_id)
        if candidate is None:
            continue
        _, _, unit_id, subsection = candidate
        entry.source.update(
            {
                "unit_id": unit_id,
                "chapter": entry.source.get("chapter"),
                "subsection": subsection,
            }
        )
    return list(table_map.values())


def _normalize_table_physical_placeholders_to_sources(
    units: List[KnowledgeUnit],
    tables: list[TableEntry],
) -> None:
    """Keep physical table markers only in the table's source unit.

    Later mentions of the same table should remain references, otherwise the
    textbook exporter expands the same physical table in multiple locations.
    """
    source_unit_by_table = {
        str(entry.id): str((entry.source or {}).get("unit_id") or "")
        for entry in tables
        if str(entry.id or "") and str((entry.source or {}).get("unit_id") or "")
    }
    if not source_unit_by_table:
        return

    for unit in units:
        kept_blocks: list[KnowledgeBlock] = []
        for block in unit.blocks:
            content = block.content or ""
            changed = False

            def replace_duplicate(match: re.Match[str]) -> str:
                nonlocal changed
                table_id = match.group("label")
                source_unit = source_unit_by_table.get(table_id)
                if not source_unit or source_unit == unit.id:
                    return match.group(0)
                changed = True
                return f"[[SEE_TABLE:{table_id}]]"

            normalized = TABLE_PLACEHOLDER_PATTERN.sub(replace_duplicate, content)
            normalized = re.sub(
                r"^\s*\[\[SEE_TABLE:(?P<label>\d+\.\d+[A-Za-z]?)\]\]\s*$",
                "",
                normalized,
            ).strip()
            if changed and not normalized:
                continue
            if changed:
                block.content = normalized
            kept_blocks.append(block)
        unit.blocks = kept_blocks


def save_structured_units(
    chunks: List,
    output_dir: str,
    chapter_name: str,
    source_file: str,
    source_title: str | None = None,
    chapter_tables: list[TableEntry] | None = None,
) -> List[KnowledgeUnit]:
    """Write composite chunks to structured JSON files."""
    units: List[KnowledgeUnit] = []
    chunks, inferred_sections = refine_chunks_for_output(chunks, source_title=source_title)
    known_table_ids = {entry.id for entry in (chapter_tables or [])}

    for index, (chunk, inferred_section) in enumerate(zip(chunks, inferred_sections), start=1):
        unit_id = f"{chapter_name}_{index:03d}"
        subsection_preview = " | ".join(chunk.subsections[:2]) or "Introduction"
        print(f"  [{index}/{len(chunks)}] {subsection_preview[:60]}...")

        output_blocks: List[KnowledgeBlock] = []
        formula_refs: List[str] = []
        table_refs: List[str] = []
        for block in chunk.blocks:
            block_content = _format_block_content_for_output(block.type, block.content)
            output_blocks.append(KnowledgeBlock(type=block.type, content=block_content))
            for reference in block.formula_references:
                normalized_formula = _normalize_formula_reference_id(reference)
                if normalized_formula and normalized_formula not in formula_refs:
                    formula_refs.append(normalized_formula)
            for match in TABLE_PLACEHOLDER_PATTERN.finditer(block_content):
                table_id = match.group("label")
                if table_id in known_table_ids and table_id not in table_refs:
                    table_refs.append(table_id)
            for match in TABLE_REFERENCE_PLACEHOLDER_PATTERN.finditer(block_content):
                table_id = match.group("label")
                if table_id in known_table_ids and table_id not in table_refs:
                    table_refs.append(table_id)
            for match in TABLE_REFERENCE_PATTERN.finditer(block_content):
                table_id = match.group(1)
                if table_id in known_table_ids and table_id not in table_refs:
                    table_refs.append(table_id)

        if formula_refs:
            print(f"    formulas: {len(formula_refs)}")
        if table_refs:
            print(f"    tables: {len(table_refs)}")

        sorted_table_refs = sort_table_reference_ids(table_refs)
        sorted_table_ref_keys = sort_table_reference_keys(
            [_table_reference_key(chapter_name, table_id) for table_id in sorted_table_refs]
        )

        unit = KnowledgeUnit(
            id=unit_id,
            chapter=chapter_name,
            section=inferred_section,
            subsections=chunk.subsections,
            source_file=source_file,
            blocks=output_blocks,
            formula_references=sort_formula_reference_ids(formula_refs),
            table_references=sorted_table_refs,
            source_title=source_title,
            table_reference_keys=sorted_table_ref_keys,
            section_level_1=chunk.section_level_1,
            section_level_2=chunk.section_level_2,
            heading_path=chunk.heading_path,
            display_heading=chunk.display_heading,
        )

        output_path = os.path.join(output_dir, f"{unit.id}.json")
        unit.save(output_path)
        units.append(unit)

    return units


def rewrite_structured_units(units: List[KnowledgeUnit], output_dir: str) -> None:
    for unit in units:
        output_path = os.path.join(output_dir, f"{unit.id}.json")
        unit.save(output_path)


def process_text_chapter(
    raw_text: str,
    output_dir: str,
    artifacts_dir: str,
    client: LLMClient | None,
    formula_library: FormulaLibrary,
    chapter_name: str,
    source_file: str,
    source_title: str | None = None,
    skip_llm_cleaning: bool = False,
    initial_table_entries: list[TableEntry] | None = None,
    llm_policy: dict[str, Any] | None = None,
) -> tuple[List[KnowledgeUnit], list[TableEntry]]:
    """Process one split OCR text segment into structured knowledge units and tables."""
    os.makedirs(output_dir, exist_ok=True)
    llm_policy = llm_policy or {}

    wrapped_text = wrap_numbered_formula_lines(raw_text)
    initial_table_ids = {entry.id for entry in (initial_table_entries or []) if entry.id}
    table_ready_text, extracted_table_entries = extract_tables_and_replace(
        wrapped_text,
        chapter_name=chapter_name,
        known_table_ids=initial_table_ids,
    )
    table_entries = _merge_table_entries_by_quality(
        [*(initial_table_entries or []), *extracted_table_entries]
    )
    missing_table_stubs = _create_missing_table_body_stubs(
        table_ready_text,
        chapter_name=chapter_name,
        existing_table_ids={entry.id for entry in table_entries if entry.id},
    )
    if missing_table_stubs:
        table_entries = _merge_table_entries_by_quality([*table_entries, *missing_table_stubs])
    plain_text = filter_noise_lines(table_ready_text)
    pseudo_pages = [clean_text(page) for page in split_text_for_cleaning(plain_text)]
    pseudo_pages = [page for page in pseudo_pages if page.strip()]

    print(f"\n[PROCESS] {chapter_name}")
    print(f"  Source: {source_file}")
    effective_phase = _resolve_effective_llm_phase(chapter_name, llm_policy)
    if client is not None:
        print(f"  LLM provider: {client.provider} | model: {client.model}")
        print(f"  LLM chunk review workers: {_resolve_chunk_review_workers(client)}")
        print(f"  LLM review phase (effective): {effective_phase}")
    else:
        print("  LLM provider: unavailable (rules-only fallback)")
    print(f"  Pseudo pages: {len(pseudo_pages)}")

    if not pseudo_pages:
        print("  [WARN] No text extracted from LaTeX source.")
        return [], []

    if skip_llm_cleaning or client is None:
        print("  LLM cleaning: skipped")
        cleaned_pages = pseudo_pages
    else:
        print("  LLM cleaning...")
        cleaned_pages = clean_page_batch(
            pseudo_pages,
            client,
            batch_size=client.clean_batch_size,
        )

    full_text = "\n\n".join(cleaned_pages)
    print(f"  Cleaned length: {len(full_text)} chars")
    if table_entries:
        print(f"  Tables extracted: {len(table_entries)}")
        if missing_table_stubs:
            print(f"  Table body stubs pending raw recovery: {len(missing_table_stubs)}")

    semantic_blocks, classification_stats = extract_semantic_blocks(
        full_text,
        chapter_name,
        client,
        formula_library,
    )
    print(f"  Semantic blocks: {len(semantic_blocks)}")
    stats_body = classification_stats.get("classification_stats", {})
    if stats_body:
        print(f"  Classification counts: {stats_body.get('counts', {})}")
        if stats_body.get("warnings"):
            for warning in stats_body["warnings"]:
                print(f"   {warning}")
    total_formula_refs = sum(len(block.formula_references) for block in semantic_blocks)
    if total_formula_refs:
        print(f"  Formula references in blocks: {total_formula_refs}")

    chunks = build_composite_chunks(semantic_blocks)
    print(f"  Composite chunks: {len(chunks)}")

    llm_metrics_before = {}
    if client is not None and hasattr(client, "get_metrics"):
        llm_metrics_before = client.get_metrics()

    review_stats = _review_chunks_with_llm(
        chunks=chunks,
        chapter_name=chapter_name,
        formula_library=formula_library,
        client=client,
        llm_policy=llm_policy,
        artifacts_dir=artifacts_dir,
    )
    if review_stats["attempted"] > 0:
        print(
            "  LLM chunk review: "
            f"phase={review_stats.get('phase', 0)}, "
            f"attempted={review_stats['attempted']}, "
            f"applied={review_stats['applied']}, "
            f"failed={review_stats['failed']}, "
            f"type_overrides={review_stats['type_overrides']}, "
            f"formula_ref_overrides={review_stats['formula_ref_overrides']}, "
            f"backfills={review_stats['formula_ref_backfills']}"
        )
        for warning in review_stats["warnings"]:
            print(f"   [WARN] {warning}")

    llm_metrics_after = {}
    llm_metrics_delta = {}
    if client is not None and hasattr(client, "get_metrics"):
        llm_metrics_after = client.get_metrics()
        llm_metrics_delta = _numeric_dict_delta(llm_metrics_before, llm_metrics_after)

    eval_path = os.path.join(
        _ensure_dir(os.path.join(os.path.abspath(artifacts_dir), "llm_eval")),
        f"{chapter_name}_phase{review_stats.get('phase', 0)}.json",
    )
    eval_payload = {
        "timestamp_utc": _utc_now_iso(),
        "chapter": chapter_name,
        "source_file": source_file,
        "phase": review_stats.get("phase", 0),
        "review_stats": review_stats,
        "llm_metrics_delta": llm_metrics_delta,
        "llm_metrics_after": llm_metrics_after,
    }
    _write_json(eval_path, eval_payload)
    print(f"  LLM eval report: {eval_path}")

    units = save_structured_units(
        chunks=chunks,
        output_dir=output_dir,
        chapter_name=chapter_name,
        source_file=source_file,
        source_title=source_title,
        chapter_tables=table_entries,
    )
    table_entries = assign_table_sources_to_units(units, table_entries)
    _normalize_table_physical_placeholders_to_sources(units, table_entries)
    rewrite_structured_units(units, output_dir)
    backfill_stats = _backfill_table_references_from_sources(units, table_entries, output_dir)
    if backfill_stats["added_table_references"] > 0 or backfill_stats["added_table_reference_keys"] > 0:
        print(
            "  table backfill: "
            f"refs+={backfill_stats['added_table_references']}, "
            f"keys+={backfill_stats['added_table_reference_keys']}, "
            f"units={backfill_stats['units_touched']}"
        )

    print(f"  [OK] {chapter_name}: {len(units)} units")
    return units, table_entries


def process_tex_chapter(
    tex_path: str,
    output_dir: str,
    artifacts_dir: str,
    client: LLMClient | None,
    formula_library: FormulaLibrary,
    chapter_name: str | None = None,
    source_title: str | None = None,
    skip_llm_cleaning: bool = False,
    llm_policy: dict[str, Any] | None = None,
) -> tuple[List[KnowledgeUnit], list[TableEntry]]:
    """Process one paper2latex main.tex into structured knowledge units."""
    if not chapter_name:
        chapter_name = derive_chapter_name(tex_path)

    with open(tex_path, encoding="utf-8") as f:
        raw_tex = f.read()

    relative_source = os.path.relpath(tex_path, start=os.getcwd())
    tex_with_table_placeholders, latex_table_entries = _extract_table_envs_and_replace(
        raw_tex,
        chapter_name=chapter_name,
    )
    paddle_table_entries = _extract_tables_from_paddle_raw(tex_path, chapter_name)
    initial_table_entries = _merge_table_entries_by_quality([*latex_table_entries, *paddle_table_entries])
    plain_text = strip_latex_markup(tex_with_table_placeholders)
    plain_text = recover_paddle_footer_body_text(plain_text, tex_path)
    return process_text_chapter(
        raw_text=plain_text,
        output_dir=output_dir,
        artifacts_dir=artifacts_dir,
        client=client,
        formula_library=formula_library,
        chapter_name=chapter_name,
        source_file=relative_source,
        source_title=source_title,
        skip_llm_cleaning=skip_llm_cleaning,
        initial_table_entries=initial_table_entries,
        llm_policy=llm_policy,
    )


def main() -> None:
    # Force UTF-8 stdout/stderr on Windows when running as a script.
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", buffering=1)

    parser = argparse.ArgumentParser(description="Process paddle_output LaTeX")
    parser.add_argument(
        "--input",
        "-i",
        default=str(REPO_ROOT / "tmp" / "paddle_output" / "chapter1_full"),
        help="Input .tex file or directory containing main.tex files",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(REPO_ROOT / "data" / "structured"),
        help="Output directory",
    )
    parser.add_argument(
        "--title",
        "-t",
        default=DEFAULT_SOURCE_TITLE,
        help="Source title (optional)",
    )
    parser.add_argument(
        "--chapter-range",
        default="1-9",
        help="Inclusive chapter range to extract from 1_full style book inputs",
    )
    parser.add_argument(
        "--toc-name",
        default="1目录",
        help="Logical TOC chapter name for generated navigation units",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(REPO_ROOT / "tmp" / "knowledge_engineering"),
        help="Directory for all smoke/diagnostic/intermediate artifacts",
    )
    parser.add_argument(
        "--chapter-name",
        default=None,
        help="Override chapter name (recommended only for single-file input)",
    )
    parser.add_argument(
        "--no-clear-output",
        action="store_true",
        help="Preserve existing output files instead of clearing the output directory first",
    )
    parser.add_argument(
        "--skip-llm-cleaning",
        action="store_true",
        help="Skip cleaner step; chunk-level semantic review still runs when LLM is available",
    )
    parser.add_argument(
        "--llm-phase",
        type=int,
        default=int((os.getenv("KE_LLM_PHASE") or "2").strip() or "2"),
        help="LLM semantic review phase: 0=off, 1=conservative, 2=ref-backfill, 3=type+ref (guardrailed)",
    )
    parser.add_argument(
        "--llm-phase2-chapters",
        default=(os.getenv("KE_LLM_PHASE2_CHAPTERS") or "all"),
        help="Comma-separated chapters allowed to run phase2; use 'all' for global enable",
    )
    parser.add_argument(
        "--llm-phase3-chapters",
        default=(os.getenv("KE_LLM_PHASE3_CHAPTERS") or ""),
        help="Comma-separated chapters allowed to run phase3",
    )
    parser.add_argument(
        "--llm-min-confidence-phase1",
        type=float,
        default=float((os.getenv("KE_LLM_MIN_CONFIDENCE_PHASE1") or "0.82").strip() or "0.82"),
        help="Minimum LLM confidence for phase1 changes",
    )
    parser.add_argument(
        "--llm-min-confidence-phase2",
        type=float,
        default=float((os.getenv("KE_LLM_MIN_CONFIDENCE_PHASE2") or "0.78").strip() or "0.78"),
        help="Minimum LLM confidence for phase2 changes",
    )
    parser.add_argument(
        "--llm-min-confidence-phase3",
        type=float,
        default=float((os.getenv("KE_LLM_MIN_CONFIDENCE_PHASE3") or "0.90").strip() or "0.90"),
        help="Minimum LLM confidence for phase3 changes",
    )
    parser.add_argument(
        "--llm-max-chunk-change-ratio",
        type=float,
        default=float((os.getenv("KE_LLM_MAX_CHUNK_CHANGE_RATIO") or "0.60").strip() or "0.60"),
        help="Hard guardrail: reject chunk if accepted changes exceed this ratio",
    )
    parser.add_argument(
        "--llm-max-type-override-ratio",
        type=float,
        default=float((os.getenv("KE_LLM_MAX_TYPE_OVERRIDE_RATIO") or "0.20").strip() or "0.20"),
        help="Hard guardrail: chapter-level max type override ratio for phase3",
    )
    parser.add_argument(
        "--llm-max-formula-candidates",
        type=int,
        default=int((os.getenv("KE_LLM_MAX_FORMULA_CANDIDATES") or "120").strip() or "120"),
        help="Cost-control: max formula candidates sent to LLM per chunk",
    )
    parser.add_argument(
        "--llm-max-refs-per-block",
        type=int,
        default=int((os.getenv("KE_LLM_MAX_REFS_PER_BLOCK") or "4").strip() or "4"),
        help="Hard guardrail: max formula refs adopted per block",
    )
    parser.add_argument(
        "--structured-fusion",
        action="store_true",
        help="Run generic post-generation structured fusion before finishing the output.",
    )
    parser.add_argument(
        "--glmocr-dir",
        default=(os.getenv("KE_GLMOCR_DIR") or ""),
        help="Optional GLM OCR directory used by --structured-fusion as guarded prose evidence.",
    )
    parser.add_argument(
        "--reference-structured-dir",
        default=(os.getenv("KE_REFERENCE_STRUCTURED_DIR") or ""),
        help="Optional earlier structured directory used by --structured-fusion for evidence-backed table recovery.",
    )
    parser.add_argument(
        "--fusion-auto-threshold",
        type=float,
        default=float((os.getenv("KE_FUSION_AUTO_THRESHOLD") or "0.90").strip() or "0.90"),
        help="Minimum confidence for automatic GLM prose repairs in structured fusion.",
    )
    parser.add_argument(
        "--fusion-review-threshold",
        type=float,
        default=float((os.getenv("KE_FUSION_REVIEW_THRESHOLD") or "0.75").strip() or "0.75"),
        help="Minimum confidence for review-queue GLM prose repairs in structured fusion.",
    )
    parser.add_argument(
        "--fusion-enable-glm-prose-repair",
        action="store_true",
        help="Allow structured fusion to auto-apply high-confidence GLM OCR prose replacements.",
    )
    parser.add_argument(
        "--replace-weaker-tables",
        action="store_true",
        help="Allow structured fusion to replace existing weaker table entries with reference versions.",
    )
    parser.add_argument(
        "--disable-ocr-table-evidence",
        action="store_true",
        help="Skip Paddle/GLM OCR table evidence binding audit during structured fusion.",
    )
    parser.add_argument(
        "--enable-ocr-table-repair",
        action="store_true",
        help="Allow structured fusion to apply two-channel high-confidence OCR table replacements.",
    )
    parser.add_argument(
        "--example-pipeline",
        action="store_true",
        help="Run formal example-library extraction and placeholder folding before finishing the output.",
    )
    parser.add_argument(
        "--example-reference-structured-dir",
        default=(os.getenv("KE_EXAMPLE_REFERENCE_STRUCTURED_DIR") or ""),
        help="Optional structured directory whose example_library.json seeds guarded example recovery.",
    )
    parser.add_argument(
        "--llm-example-boundaries",
        action="store_true",
        help="Run guarded LLM Example boundary pilot and write a separate candidate structured directory.",
    )
    parser.add_argument(
        "--llm-example-chapters",
        default=(os.getenv("KE_LLM_EXAMPLE_CHAPTERS") or "chapter6"),
        help="Chapter allowlist for --llm-example-boundaries, e.g. chapter6.",
    )
    parser.add_argument(
        "--llm-example-max-windows",
        type=int,
        default=int((os.getenv("KE_LLM_EXAMPLE_MAX_WINDOWS") or "20").strip() or "20"),
        help="Maximum LLM Example boundary windows to review.",
    )
    parser.add_argument(
        "--llm-example-workers",
        type=int,
        default=int((os.getenv("KE_LLM_EXAMPLE_WORKERS") or "1").strip() or "1"),
        help="Parallel LLM workers for --llm-example-boundaries.",
    )
    parser.add_argument(
        "--llm-example-output-structured-dir",
        default=(os.getenv("KE_LLM_EXAMPLE_OUTPUT_STRUCTURED_DIR") or ""),
        help="Output structured directory for --llm-example-boundaries candidate.",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.artifacts_dir, exist_ok=True)
    llm_policy = {
        "phase": max(0, min(3, int(args.llm_phase))),
        "phase2_chapters": _parse_chapter_allowlist(args.llm_phase2_chapters, {"*"}),
        "phase3_chapters": _parse_chapter_allowlist(args.llm_phase3_chapters, set()),
        "min_confidence_phase1": _clamp_float(args.llm_min_confidence_phase1, default=0.82),
        "min_confidence_phase2": _clamp_float(args.llm_min_confidence_phase2, default=0.78),
        "min_confidence_phase3": _clamp_float(args.llm_min_confidence_phase3, default=0.90),
        "max_chunk_change_ratio": _clamp_float(args.llm_max_chunk_change_ratio, default=0.60),
        "max_type_override_ratio": _clamp_float(args.llm_max_type_override_ratio, default=0.20),
        "max_formula_candidates": max(10, int(args.llm_max_formula_candidates)),
        "max_formula_refs_per_block": max(1, int(args.llm_max_refs_per_block)),
    }
    print(
        "[LLM] Review policy: "
        f"phase={llm_policy['phase']}, "
        f"phase2={sorted(llm_policy['phase2_chapters'])}, "
        f"phase3={sorted(llm_policy['phase3_chapters'])}"
    )

    if not args.no_clear_output:
        removed = clear_directory(args.output)
        if removed > 0:
            print(f"[CLEANUP] Cleared {removed} existing entries from {args.output}")

    try:
        client = LLMClient()
        print(f"[LLM] Connected to API via {client.provider} ({client.model})")
        if hasattr(client, "get_metrics"):
            llm_runtime = client.get_metrics()
            print(
                "[LLM] Runtime controls: "
                f"cache_enabled={llm_runtime.get('cache_enabled')}, "
                f"cache_dir={llm_runtime.get('cache_dir')}, "
                f"max_remote_calls={llm_runtime.get('max_remote_calls')}, "
                f"max_prompt_chars_total={llm_runtime.get('max_prompt_chars_total')}"
            )
    except Exception as exc:
        client = None
        print(f"[WARN] LLM unavailable, continuing with rules-only fallback: {exc}")

    formula_output = os.path.join(args.output, "formula_library.json")
    table_output = os.path.join(args.output, "table_library.json")
    formula_library = FormulaLibrary.load(formula_output)
    table_library = TableLibrary.load(table_output)
    existing_stats = formula_library.get_stats()
    existing_table_stats = table_library.get_stats()
    print(
        f"[FORMULA] Loaded existing library: {existing_stats['total']} formulas "
        f"(block: {existing_stats['block']}, inline: {existing_stats['inline']})"
    )
    print(
        f"[TABLE] Loaded existing library: {existing_table_stats['total']} tables "
        f"(numbered: {existing_table_stats['numbered']}, inline: {existing_table_stats['inline']})"
    )

    tex_files = find_latex_inputs(args.input)
    if not tex_files:
        raise ValueError(f"No .tex input found under: {args.input}")

    print(f"[INPUT] {len(tex_files)} tex files")
    print(f"[TITLE] {args.title}")

    chapter_start, chapter_end = parse_chapter_range(args.chapter_range)

    all_units: list[KnowledgeUnit] = []
    all_tables: list[TableEntry] = []

    if len(tex_files) == 1:
        tex_path = tex_files[0]
        with open(tex_path, encoding="utf-8") as f:
            raw_tex = f.read()

        stripped_text = strip_latex_markup(raw_tex)
        toc_text, chapter_segments, _ = split_tex_book(
            stripped_text,
            chapter_start=chapter_start,
            chapter_end=chapter_end,
        )

        if chapter_segments:
            relative_source = os.path.relpath(tex_path, start=os.getcwd())
            save_split_artifacts(
                artifacts_dir=args.artifacts_dir,
                toc_name=args.toc_name,
                toc_text=toc_text,
                chapter_segments=chapter_segments,
            )
            if toc_text:
                build_toc_outputs_from_text(
                    toc_text=toc_text,
                    output_dir=args.output,
                    toc_name=args.toc_name,
                    source_file=relative_source,
                    source_title=args.title,
                )

            for chapter_name, chapter_text in sorted(
                chapter_segments.items(),
                key=lambda item: int(re.search(r"\d+", item[0]).group(0)),
            ):
                removed_count = cleanup_chapter_outputs(args.output, chapter_name)
                if removed_count > 0:
                    print(f"[CLEANUP] Removed {removed_count} stale units for {chapter_name}")

                removed_formula_count = formula_library.remove_by_chapter(chapter_name)
                if removed_formula_count > 0:
                    print(f"[FORMULA] Removed {removed_formula_count} stale formulas for {chapter_name}")
                removed_table_count = table_library.remove_by_chapter(chapter_name)
                if removed_table_count > 0:
                    print(f"[TABLE] Removed {removed_table_count} stale tables for {chapter_name}")

                units, tables = process_text_chapter(
                    raw_text=chapter_text,
                    output_dir=args.output,
                    artifacts_dir=args.artifacts_dir,
                    client=client,
                    formula_library=formula_library,
                    chapter_name=chapter_name,
                    source_file=relative_source,
                    source_title=args.title,
                    skip_llm_cleaning=args.skip_llm_cleaning,
                    llm_policy=llm_policy,
                )
                all_units.extend(units)
                all_tables.extend(tables)
        else:
            relative_source = os.path.relpath(tex_path, start=os.getcwd())
            fallback_toc_text = toc_text
            fallback_chapter_name = args.chapter_name if args.chapter_name else derive_chapter_name(tex_path)
            if not fallback_toc_text and re.search(r"(\\u76ee\\u5f55|toc)", fallback_chapter_name, re.IGNORECASE):
                fallback_toc_text = stripped_text

            if fallback_toc_text:
                save_split_artifacts(
                    artifacts_dir=args.artifacts_dir,
                    toc_name=args.toc_name,
                    toc_text=fallback_toc_text,
                    chapter_segments={},
                )
                removed_toc = cleanup_toc_outputs(args.output, args.toc_name)
                if removed_toc > 0:
                    print(f"[CLEANUP] Removed {removed_toc} stale TOC outputs for {args.toc_name}")

                generated = build_toc_outputs_from_text(
                    toc_text=fallback_toc_text,
                    output_dir=args.output,
                    toc_name=args.toc_name,
                    source_file=relative_source,
                    source_title=args.title,
                )
                if generated > 0:
                    # Prevent stale chapter-style TOC chunks from mixed old runs.
                    removed_count = cleanup_chapter_outputs(args.output, fallback_chapter_name)
                    if removed_count > 0:
                        print(
                            f"[CLEANUP] Removed {removed_count} chapter-style TOC chunks for {fallback_chapter_name}"
                        )
                    print(f"[DONE] Generated {generated} TOC navigation units -> {args.output}")
                    return

            chapter_name = args.chapter_name if args.chapter_name else derive_chapter_name(tex_path)
            removed_count = cleanup_chapter_outputs(args.output, chapter_name)
            if removed_count > 0:
                print(f"[CLEANUP] Removed {removed_count} stale units for {chapter_name}")

            removed_formula_count = formula_library.remove_by_chapter(chapter_name)
            if removed_formula_count > 0:
                print(f"[FORMULA] Removed {removed_formula_count} stale formulas for {chapter_name}")
            removed_table_count = table_library.remove_by_chapter(chapter_name)
            if removed_table_count > 0:
                print(f"[TABLE] Removed {removed_table_count} stale tables for {chapter_name}")

            units, tables = process_tex_chapter(
                tex_path=tex_path,
                output_dir=args.output,
                artifacts_dir=args.artifacts_dir,
                client=client,
                formula_library=formula_library,
                chapter_name=chapter_name,
                source_title=args.title,
                skip_llm_cleaning=args.skip_llm_cleaning,
                llm_policy=llm_policy,
            )
            all_units.extend(units)
            all_tables.extend(tables)
    else:
        for tex_path in tex_files:
            chapter_name = args.chapter_name if len(tex_files) == 1 and args.chapter_name else derive_chapter_name(tex_path)

            removed_count = cleanup_chapter_outputs(args.output, chapter_name)
            if removed_count > 0:
                print(f"[CLEANUP] Removed {removed_count} stale units for {chapter_name}")

            removed_formula_count = formula_library.remove_by_chapter(chapter_name)
            if removed_formula_count > 0:
                print(f"[FORMULA] Removed {removed_formula_count} stale formulas for {chapter_name}")
            removed_table_count = table_library.remove_by_chapter(chapter_name)
            if removed_table_count > 0:
                print(f"[TABLE] Removed {removed_table_count} stale tables for {chapter_name}")

            units, tables = process_tex_chapter(
                tex_path=tex_path,
                output_dir=args.output,
                artifacts_dir=args.artifacts_dir,
                client=client,
                formula_library=formula_library,
                chapter_name=chapter_name,
                source_title=args.title,
                skip_llm_cleaning=args.skip_llm_cleaning,
                llm_policy=llm_policy,
            )
            all_units.extend(units)
            all_tables.extend(tables)

    formula_library.save(formula_output)
    stats = formula_library.get_stats()
    print(
        f"\n[FORMULA] Saved library: {stats['total']} formulas "
        f"(block: {stats['block']}, inline: {stats['inline']})"
    )
    table_library.tables.extend(all_tables)
    table_library.tables = sorted(table_library.tables, key=lambda entry: _table_sort_key(entry.id))
    table_library.save(table_output)
    table_stats = table_library.get_stats()
    print(
        f"[TABLE] Saved library: {table_stats['total']} tables "
        f"(numbered: {table_stats['numbered']}, inline: {table_stats['inline']}, "
        f"updated_this_run: {len(all_tables)})"
    )

    fusion_summary = None
    if args.structured_fusion:
        from knowledge_engineering.pipeline.structured_fusion import apply_structured_fusion

        print("\n[FUSION] Running generic structured fusion...")
        fusion_summary = apply_structured_fusion(
            structured_dir=args.output,
            pdf_dir="data/背景资料",
            glmocr_dir=args.glmocr_dir or None,
            paddle_output_dir=args.input or None,
            reference_structured_dir=args.reference_structured_dir or None,
            artifacts_dir=args.artifacts_dir,
            auto_threshold=float(args.fusion_auto_threshold),
            review_threshold=float(args.fusion_review_threshold),
            enable_glm_prose_repair=bool(args.fusion_enable_glm_prose_repair),
            replace_weaker_tables=bool(args.replace_weaker_tables),
            enable_ocr_table_evidence=not bool(args.disable_ocr_table_evidence),
            enable_ocr_table_repair=bool(args.enable_ocr_table_repair),
        )
        block_stats = fusion_summary.get("block_stats", {})
        table_fusion_stats = fusion_summary.get("table_stats", {})
        table_binding_stats = fusion_summary.get("table_binding_stats", {})
        ref_stats = fusion_summary.get("reference_stats", {})
        print(
            "  structured fusion: "
            f"removed_blocks={block_stats.get('blocks_removed', 0)}, "
            f"glm_repairs={block_stats.get('glm_repair_applied', 0)}, "
            f"tables_recovered={table_fusion_stats.get('table_entries_recovered_from_reference', 0)}, "
            f"table_binding_mismatch={table_binding_stats.get('table_binding_mismatch', 0)}, "
            f"table_refs_backfilled={ref_stats.get('table_references_backfilled', 0)}, "
            f"manual_queue={fusion_summary.get('manual_queue_count', 0)}"
        )
        if fusion_summary.get("artifact_dir"):
            print(f"  structured fusion artifacts: {fusion_summary['artifact_dir']}")

    example_pipeline_summary = None
    if args.example_pipeline:
        from knowledge_engineering.pipeline.example_pipeline import apply_example_pipeline

        print("\n[EXAMPLE] Running formal example-library pipeline...")
        example_pipeline_summary = apply_example_pipeline(
            structured_dir=args.output,
            project_root=REPO_ROOT,
            reference_structured_dir=args.example_reference_structured_dir or None,
            artifacts_dir=Path(args.artifacts_dir) / "example_pipeline",
        )
        print(
            "  example pipeline: "
            f"examples={example_pipeline_summary.get('total_examples', 0)}, "
            f"replaced={example_pipeline_summary.get('replaced_examples', 0)}, "
            f"skipped={example_pipeline_summary.get('skipped_examples', 0)}, "
            f"blocks_removed={example_pipeline_summary.get('blocks_removed_by_example_fold', 0)}, "
            f"elapsed={example_pipeline_summary.get('elapsed_seconds', 0)}s"
        )
        if example_pipeline_summary.get("artifacts_dir"):
            print(f"  example pipeline artifacts: {example_pipeline_summary['artifacts_dir']}")

    llm_example_boundary_summary = None
    if args.llm_example_boundaries:
        from knowledge_engineering.processors.llm_example_boundary import (
            DEFAULT_OUTPUT as LLM_EXAMPLE_DEFAULT_OUTPUT,
            parse_chapter_list,
            run_llm_example_boundary_trial,
        )

        llm_example_output = (
            Path(args.llm_example_output_structured_dir)
            if args.llm_example_output_structured_dir
            else REPO_ROOT / LLM_EXAMPLE_DEFAULT_OUTPUT
        )
        print("\n[EXAMPLE] Running guarded LLM Example boundary pilot...")
        llm_example_boundary_summary = run_llm_example_boundary_trial(
            structured_dir=Path(args.output),
            project_root=REPO_ROOT,
            output_structured_dir=llm_example_output,
            artifacts_dir=Path(args.artifacts_dir) / "llm_example_boundary",
            chapters=parse_chapter_list(args.llm_example_chapters),
            max_windows=max(0, int(args.llm_example_max_windows)),
            workers=max(1, int(args.llm_example_workers)),
        )
        print(
            "  llm example boundary: "
            f"windows={llm_example_boundary_summary.get('windows', 0)}, "
            f"auto_applied={llm_example_boundary_summary.get('auto_applied', 0)}, "
            f"review_queue={llm_example_boundary_summary.get('review_queue', 0)}, "
            f"candidate={llm_example_boundary_summary.get('output_structured_dir')}"
        )

    llm_eval_dir = _ensure_dir(os.path.join(os.path.abspath(args.artifacts_dir), "llm_eval"))
    chapter_eval_files = sorted(
        file_name
        for file_name in os.listdir(llm_eval_dir)
        if file_name.endswith(".json") and "_phase" in file_name
    )
    chapter_eval_summary: list[dict[str, Any]] = []
    for file_name in chapter_eval_files:
        path = os.path.join(llm_eval_dir, file_name)
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        review_stats = payload.get("review_stats", {})
        chapter_eval_summary.append(
            {
                "chapter": payload.get("chapter"),
                "phase": payload.get("phase"),
                "attempted": review_stats.get("attempted", 0),
                "applied": review_stats.get("applied", 0),
                "failed": review_stats.get("failed", 0),
                "type_overrides": review_stats.get("type_overrides", 0),
                "formula_ref_overrides": review_stats.get("formula_ref_overrides", 0),
                "formula_ref_backfills": review_stats.get("formula_ref_backfills", 0),
            }
        )
    run_summary = {
        "timestamp_utc": _utc_now_iso(),
        "input": args.input,
        "output": args.output,
        "artifacts_dir": os.path.abspath(args.artifacts_dir),
        "llm_policy": {
            key: sorted(value) if isinstance(value, set) else value
            for key, value in llm_policy.items()
        },
        "chapters": chapter_eval_summary,
    }
    if client is not None and hasattr(client, "get_metrics"):
        run_summary["llm_metrics_final"] = client.get_metrics()
    if fusion_summary is not None:
        run_summary["structured_fusion"] = fusion_summary
    if example_pipeline_summary is not None:
        run_summary["example_pipeline"] = example_pipeline_summary
    if llm_example_boundary_summary is not None:
        run_summary["llm_example_boundary"] = llm_example_boundary_summary
    run_summary_path = os.path.join(llm_eval_dir, "run_summary.json")
    _write_json(run_summary_path, run_summary)
    print(f"[LLM] Eval summary: {run_summary_path}")

    print(f"\n[DONE] Generated {len(all_units)} knowledge units -> {args.output}")


if __name__ == "__main__":
    main()



