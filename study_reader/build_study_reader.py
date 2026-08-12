from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
CONFIG_PATH = APP_DIR / "source_config.json"
OUTPUT_DIR = APP_DIR / "data" / "generated"
STUDY_DATASET_PATH = OUTPUT_DIR / "study_dataset.json"
PREREQUISITE_AUDIT_PATH = OUTPUT_DIR / "prerequisite_audit.json"
CHAPTER_DATA_DIR = OUTPUT_DIR / "chapters"
BUILD_PROVENANCE_PATH = OUTPUT_DIR / "build_provenance.json"
FORMULA_CORRECTIONS_PATH = APP_DIR / "formula_corrections.json"
logger = logging.getLogger(__name__)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from knowledge_engineering.core.runtime import LLMClient
except ImportError:  # pragma: no cover
    LLMClient = None  # type: ignore[assignment]


DEFAULT_BOOK_PREFIX = "Evolution"
DEFAULT_CHAPTER = "Evolution_chapter28"
REFERENCE_WINDOW_CHARS = 420

SECTION_PATTERN = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$")
UNIT_TITLE_PATTERN = re.compile(
    r"^(?P<unit>[A-Za-z]+_(?:chapter|appendix)\d+_\d{3})\s*(?:·|路|-|–|—|\|)\s*(?P<title>.+)$",
    re.IGNORECASE,
)
CHAPTER_ID_PATTERN = re.compile(r"^(?P<book>[A-Za-z]+)_(?P<kind>chapter|appendix)(?P<num>\d+)$", re.IGNORECASE)
UNIT_TITLE_PATTERN = re.compile(
    r"^(?P<unit>[A-Za-z]+_(?:chapter|appendix)\d+_\d{3})\s*(?:·|路|-|—|\|)\s*(?P<title>.+)$",
    re.IGNORECASE,
)
CHAPTER_MD_PATTERN = re.compile(r"^(?P<id>(?P<book>[A-Za-z]+)_(?:chapter|appendix)\d+)_textbook\.md$", re.IGNORECASE)
CHAPTER_REF_PATTERN = re.compile(
    r"\b(?P<lw>LW\s+)?Chapters?\s+"
    r"(?P<numbers>\d{1,2}(?:\s*(?:,|and|&)\s*\d{1,2})*)"
    r"(?!\s*,\s*\d{3,4})",
    re.IGNORECASE,
)
NUMBERED_REF_PATTERN = re.compile(
    r"\b(?P<kind>Equation|Figure|Table|Example)s?\s+"
    r"(?P<id>(?:A?\d+)\.\d+(?:\.\d+)?[a-z]?)",
    re.IGNORECASE,
)
PLACEHOLDER_REF_PATTERN = re.compile(r"\[\[SEE_(?P<kind>FIGURE|TABLE|EXAMPLE|FORMULA):(?P<id>[^\]]+)\]\]")
FORMULA_HEADER_PATTERN = re.compile(r"\*\*Formula\s+\((?P<id>[^)]+)\)\*\*", re.IGNORECASE)
FIGURE_HEADER_PATTERN = re.compile(r"\*\*Figure\s+(?P<id>A?\d+\.\d+[a-z]?)\*\*", re.IGNORECASE)
TABLE_HEADER_PATTERN = re.compile(r"\*\*Table\s+(?P<id>A?\d+\.\d+[a-z]?)\*\*", re.IGNORECASE)
EXAMPLE_HEADER_PATTERN = re.compile(r"(?:\*\*)?Example\s+(?P<id>A?\d+\.\d+[a-z]?)(?:\*\*)?", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_repo_path(raw_path: str | None, fallback: str) -> Path:
    value = str(raw_path or fallback).strip() or fallback
    path = Path(value)
    return path if path.is_absolute() else (ROOT_DIR / path).resolve()


def markdown_url(path: Path) -> str:
    try:
        return "/" + path.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_anchor(value: str) -> str:
    text = re.sub(r"\s+", "-", value.strip().lower())
    text = re.sub(r"[^a-z0-9_\-.]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def asset_anchor(kind: str, ref_id: str) -> str:
    safe_id = str(ref_id or "").strip().lower().replace("(", "").replace(")", "")
    safe_id = re.sub(r"[^a-z0-9.]+", "-", safe_id).strip("-")
    return normalize_anchor(f"{kind}-{safe_id}")


def chapter_parts(chapter_id: str) -> tuple[str, str, int] | None:
    match = CHAPTER_ID_PATTERN.fullmatch(str(chapter_id or "").strip())
    if not match:
        return None
    return (match.group("book"), match.group("kind").lower(), int(match.group("num")))


def chapter_sort_key(chapter_id: str) -> tuple[str, int, int, str]:
    parts = chapter_parts(chapter_id)
    if not parts:
        return ("", 9, 9999, chapter_id)
    book, kind, number = parts
    return (book.lower(), 0 if kind == "chapter" else 1, number, chapter_id)


def chapter_sort_key_for_books(chapter_id: str, book_order: dict[str, int]) -> tuple[int, int, int, str]:
    parts = chapter_parts(chapter_id)
    if not parts:
        return (999, 9, 9999, chapter_id)
    book, kind, number = parts
    return (book_order.get(book, 999), 0 if kind == "chapter" else 1, number, chapter_id)


def target_book_for_reference(reference: dict[str, str], current_book: str) -> str:
    hint = str(reference.get("book_hint") or "").strip()
    if hint:
        return hint
    return current_book or DEFAULT_BOOK_PREFIX


def chapter_ref_id(ref_id: str, book_prefix: str = DEFAULT_BOOK_PREFIX) -> str | None:
    value = str(ref_id or "").strip()
    if not value:
        return None
    if value.lower().startswith("a"):
        match = re.match(r"a(?P<num>\d+)", value, flags=re.IGNORECASE)
        return f"{book_prefix}_appendix{int(match.group('num'))}" if match else None
    match = re.match(r"(?P<num>\d+)", value)
    return f"{book_prefix}_chapter{int(match.group('num'))}" if match else None


def is_prerequisite_source(current_chapter_id: str, source_chapter_id: str) -> bool:
    current_parts = chapter_parts(current_chapter_id)
    source_parts = chapter_parts(source_chapter_id)
    if not current_parts or not source_parts:
        return True
    current_book, current_kind, current_number = current_parts
    source_book, source_kind, source_number = source_parts
    if current_book.lower() != source_book.lower():
        return True
    if current_kind == "chapter" and source_kind == "chapter":
        return source_number < current_number
    if current_kind == "appendix" and source_kind == "appendix":
        return source_number < current_number
    return True


def chapter_label(chapter_id: str) -> str:
    parts = chapter_parts(chapter_id)
    if not parts:
        return chapter_id
    _, kind, number = parts
    return f"Chapter {number}" if kind == "chapter" else f"Appendix {number}"


def markdown_path_for_chapter(textbook_dir: Path, chapter_id: str) -> Path:
    return textbook_dir / f"{chapter_id}_textbook.md"


def plain_text(markdown: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", markdown)
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[\[SEE_[A-Z]+:[^\]]+\]\]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_>#|`]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def trim_text(value: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    return text if len(text) <= limit else text[: max(0, limit - 1)].rstrip() + "…"


def display_section_title(raw_title: str) -> str:
    match = UNIT_TITLE_PATTERN.match(raw_title.strip())
    if match:
        return match.group("title").strip()
    return raw_title.strip()


def short_nav_label(raw_title: str, limit: int = 64) -> str:
    title = display_section_title(raw_title)
    title = re.sub(r"^Chapter\s+\d+\s*[·:\-]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^Appendix\s+\d+\s*[·:\-]\s*", "", title, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"\s*/\s*", title) if part.strip()]
    label = parts[-1] if parts else title
    label = re.sub(r"\s+", " ", label).strip()
    return label[:limit].rstrip()


def split_markdown_sections(markdown: str, chapter_id: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal current, body
        if not current:
            return
        raw_text = "\n".join(body).strip()
        current["text"] = raw_text
        current["text_preview"] = trim_text(plain_text(raw_text), 320)
        sections.append(current)
        body = []

    for line in markdown.splitlines():
        match = SECTION_PATTERN.match(line)
        if match:
            flush()
            raw_title = match.group("title").strip()
            unit_match = UNIT_TITLE_PATTERN.match(raw_title)
            section_id = (
                unit_match.group("unit")
                if unit_match
                else f"{chapter_id}_section_{len(sections) + 1:03d}"
            )
            current = {
                "id": section_id,
                "title": display_section_title(raw_title),
                "nav_label": short_nav_label(raw_title),
                "raw_title": raw_title,
                "level": len(match.group("level")),
                "anchor": normalize_anchor(section_id),
            }
            body = []
            continue
        if current:
            body.append(line)

    flush()
    return sections


def parse_chapter_numbers(raw_value: str) -> list[int]:
    values: list[int] = []
    for part in re.split(r",|\band\b|\s+", raw_value):
        part = part.strip()
        if part.isdigit():
            number = int(part)
            if number not in values:
                values.append(number)
    return values


def references_in_text(text: str) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for match in CHAPTER_REF_PATTERN.finditer(text):
        book_hint = "Genetics" if match.group("lw") else ""
        for number in parse_chapter_numbers(match.group("numbers")):
            key = ("chapter", str(number), book_hint)
            if key not in seen:
                seen.add(key)
                label = f"LW Chapter {number}" if book_hint else f"Chapter {number}"
                references.append(
                    {
                        "kind": "chapter",
                        "id": str(number),
                        "label": label,
                        "book_hint": book_hint,
                        "link_scope": "lw" if book_hint else "current-book",
                    }
                )

    for match in NUMBERED_REF_PATTERN.finditer(text):
        kind = match.group("kind").lower()
        ref_id = match.group("id")
        prefix = text[max(0, match.start() - 8) : match.start()]
        book_hint = "Genetics" if re.search(r"\bLW\s*$", prefix, flags=re.IGNORECASE) else ""
        key = (kind, ref_id.lower(), book_hint)
        if key not in seen:
            seen.add(key)
            label = f"{'LW ' if book_hint else ''}{match.group('kind')} {ref_id}"
            references.append(
                {
                    "kind": kind,
                    "id": ref_id,
                    "label": label,
                    "book_hint": book_hint,
                    "link_scope": "lw" if book_hint else "current-book",
                }
            )

    for match in PLACEHOLDER_REF_PATTERN.finditer(text):
        raw_kind = match.group("kind").lower()
        kind = "equation" if raw_kind == "formula" else raw_kind
        ref_id = match.group("id")
        prefix = text[max(0, match.start() - 8) : match.start()]
        book_hint = "Genetics" if re.search(r"\bLW\s*$", prefix, flags=re.IGNORECASE) else ""
        key = (kind, ref_id.lower(), book_hint)
        if key not in seen:
            seen.add(key)
            label = f"{'LW ' if book_hint else ''}{kind.title()} {ref_id}"
            references.append(
                {
                    "kind": kind,
                    "id": ref_id,
                    "label": label,
                    "book_hint": book_hint,
                    "link_scope": "lw" if book_hint else "current-book",
                }
            )

    return references


def section_reference_index(sections: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    return {
        section["id"]: references_in_text(f"{section.get('title', '')}\n{section.get('text', '')}")
        for section in sections
    }


def context_window(markdown: str, needle: str, limit: int = REFERENCE_WINDOW_CHARS) -> str:
    if not markdown:
        return ""
    if not needle:
        return trim_text(plain_text(markdown), limit)
    match = re.search(re.escape(needle), markdown, flags=re.IGNORECASE)
    if not match:
        return trim_text(plain_text(markdown), limit)
    start = max(0, match.start() - limit // 2)
    end = min(len(markdown), match.end() + limit // 2)
    return trim_text(plain_text(markdown[start:end]), limit)


def dequote(line: str) -> str:
    text = line.strip()
    while text.startswith(">"):
        text = text[1:].strip()
    return text


def extract_latex_from_quote(quote: list[str]) -> str:
    chunks: list[str] = []
    in_math = False
    for raw_line in quote:
        line = raw_line.strip()
        if "$$" not in line and not in_math:
            continue
        if "$$" in line:
            parts = line.split("$$")
            if not in_math and len(parts) >= 3:
                chunks.append(parts[1].strip())
                continue
            if not in_math:
                chunks.append(parts[1].strip())
                in_math = True
                continue
            chunks.append(parts[0].strip())
            in_math = False
            continue
        if in_math:
            chunks.append(line)
    return "\n".join(part for part in chunks if part).strip()


def extract_display_math_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    for match in re.finditer(r"\$\$([\s\S]+?)\$\$", text or ""):
        latex = match.group(1).strip()
        if latex:
            chunks.append(latex)
    return chunks


def normalize_latex_for_katex(latex: str) -> str:
    """Apply conservative KaTeX-oriented cleanup without changing formula meaning."""
    value = str(latex or "").strip()
    if not value:
        return ""
    replacements = {
        "\u2212": "-",
        "\u00d7": r"\times",
        "\u22c5": r"\cdot",
        "\u2026": r"\ldots",
        "\u03bc": r"\mu",
        "\u03c3": r"\sigma",
        "\u03b1": r"\alpha",
        "\u03b2": r"\beta",
        "\u03b3": r"\gamma",
        "\u03c4": r"\tau",
        "\u03b8": r"\theta",
        "\u03c1": r"\rho",
        "\u03c9": r"\omega",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"(\\(?:qquad|quad|;|,|:))(?=[A-Za-z])", r"\1 ", value)
    value = re.sub(r"\\begin\{align\*\}", r"\\begin{aligned}", value)
    value = re.sub(r"\\end\{align\*\}", r"\\end{aligned}", value)
    value = re.sub(r"\\begin\{align\}", r"\\begin{aligned}", value)
    value = re.sub(r"\\end\{align\}", r"\\end{aligned}", value)
    value = re.sub(r"\\begin\{eqnarray\*?\}", r"\\begin{aligned}", value)
    value = re.sub(r"\\end\{eqnarray\*?\}", r"\\end{aligned}", value)
    value = re.sub(r"\\label\{[^}]*\}", "", value)
    value = re.sub(r"\\notag\b", "", value)
    value = re.sub(r"\\nonumber\b", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def latex_key(latex: str) -> str:
    value = re.sub(r"^\s*\$\$|\$\$\s*$", "", str(latex or "").strip())
    return re.sub(r"\s+", "", value)


def formula_ref_sort_key(ref_id: str) -> tuple[int, int, int, str]:
    match = re.match(r"^a?(?P<chapter>\d+)\.(?P<body>\d+(?:\.\d+)?)(?P<suffix>[a-z]?)$", str(ref_id or ""), re.IGNORECASE)
    if not match:
        return (9999, 9999, 9999, str(ref_id))
    body_parts = [int(part) for part in match.group("body").split(".")]
    return (
        int(match.group("chapter")),
        body_parts[0] if body_parts else 0,
        body_parts[1] if len(body_parts) > 1 else 0,
        match.group("suffix").lower(),
    )


def is_formula_ref_valid_for_chapter(ref_id: str, chapter_id: str) -> bool:
    parts = chapter_parts(chapter_id)
    if not parts:
        return False
    book, kind, number = parts
    value = str(ref_id or "").strip()
    appendix = re.match(r"^a(?P<num>\d+)\.", value, re.IGNORECASE)
    if appendix:
        if kind == "appendix":
            return int(appendix.group("num")) == number
        return book.lower() == "genetics" and kind == "chapter" and number == 27
    numeric = re.match(r"^(?P<num>\d+)\.", value)
    return bool(numeric and kind == "chapter" and int(numeric.group("num")) == number)


def formula_ref_ids_from_record(record: dict[str, Any], chapter_id: str) -> list[str]:
    values = [
        record.get("id", ""),
        record.get("label_format", ""),
        record.get("label", ""),
        (record.get("source") or {}).get("source_label", "") if isinstance(record.get("source"), dict) else "",
    ]
    refs: list[str] = []
    for value in values:
        for match in re.finditer(r"(?<![A-Za-z0-9])(?:Formula\s*)?\(?((?:A?\d+)\.\d+(?:\.\d+)?[a-z]?)\)?", str(value), re.IGNORECASE):
            ref_id = match.group(1)
            if is_formula_ref_valid_for_chapter(ref_id, chapter_id) and ref_id.lower() not in {item.lower() for item in refs}:
                refs.append(ref_id)
    return refs


def load_formula_library_by_chapter(structured_dir: Path) -> dict[str, list[dict[str, Any]]]:
    payload = load_json(structured_dir / "formula_library.json")
    formulas = payload.get("formulas", [])
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not isinstance(formulas, list):
        return by_chapter
    for formula in formulas:
        if not isinstance(formula, dict):
            continue
        source = formula.get("source")
        if not isinstance(source, dict):
            continue
        chapter_id = str(source.get("chapter") or "").strip()
        if chapter_id:
            by_chapter[chapter_id].append(formula)
    return by_chapter


def extract_formula_library_assets(
    chapter_id: str,
    formula_library_by_chapter: dict[str, list[dict[str, Any]]],
    existing_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_formula_ids = {
        str(asset.get("id", "")).lower()
        for asset in existing_assets
        if asset.get("kind") == "formula"
    }
    assets: list[dict[str, Any]] = []
    corrections: dict[str, dict[str, str]] = {}
    if FORMULA_CORRECTIONS_PATH.is_file():
        payload = json.loads(FORMULA_CORRECTIONS_PATH.read_text(encoding="utf-8"))
        corrections = {
            str(key): value
            for key, value in (payload.get("corrections") or {}).items()
            if isinstance(value, dict)
        }
    for record in formula_library_by_chapter.get(chapter_id, []):
        latex = str(record.get("latex") or "").strip()
        if not latex:
            continue
        source = record.get("source") if isinstance(record.get("source"), dict) else {}
        section_id = str(source.get("unit_id") or "").strip()
        for ref_id in formula_ref_ids_from_record(record, chapter_id):
            if ref_id.lower() in existing_formula_ids:
                continue
            correction = corrections.get(f"{chapter_id}:{ref_id}")
            if correction:
                source_hash = hashlib.sha256(latex.encode("utf-8")).hexdigest()
                replacement = str(correction.get("replacement") or "")
                if source_hash != correction.get("source_sha256") and latex != replacement:
                    raise RuntimeError(
                        f"Formula-library record drifted before correction: {chapter_id}:{ref_id}"
                    )
                latex = replacement
            assets.append(
                {
                    "kind": "formula",
                    "id": ref_id,
                    "anchor": asset_anchor("formula", ref_id),
                    "label": f"Formula ({ref_id})",
                    "section_id": section_id,
                    "latex": latex,
                    "latex_render": normalize_latex_for_katex(latex),
                    "origin": "formula-library",
                    "source_label": source.get("source_label", ""),
                }
            )
            existing_formula_ids.add(ref_id.lower())
    return sorted(assets, key=lambda item: formula_ref_sort_key(str(item.get("id", ""))))


def load_table_library_by_chapter(structured_dir: Path) -> dict[str, list[dict[str, Any]]]:
    payload = load_json(structured_dir / "table_library.json")
    tables = payload.get("tables", [])
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not isinstance(tables, list):
        return by_chapter
    for table in tables:
        if not isinstance(table, dict):
            continue
        source = table.get("source")
        if not isinstance(source, dict):
            continue
        chapter_id = str(source.get("chapter") or "").strip()
        if chapter_id:
            by_chapter[chapter_id].append(table)
    return by_chapter


def extract_table_library_assets(
    chapter_id: str,
    table_library_by_chapter: dict[str, list[dict[str, Any]]],
    existing_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_table_ids = {
        str(asset.get("id", "")).lower()
        for asset in existing_assets
        if asset.get("kind") == "table"
    }
    assets: list[dict[str, Any]] = []
    for record in table_library_by_chapter.get(chapter_id, []):
        ref_id = str(record.get("id") or "").strip()
        if not ref_id or not is_formula_ref_valid_for_chapter(ref_id, chapter_id):
            continue
        if ref_id.lower() in existing_table_ids:
            continue
        source = record.get("source") if isinstance(record.get("source"), dict) else {}
        title = str(record.get("title") or record.get("label_format") or f"Table {ref_id}").strip()
        assets.append(
            {
                "kind": "table",
                "id": ref_id,
                "anchor": asset_anchor("table", ref_id),
                "label": f"Table {ref_id}",
                "section_id": str(source.get("unit_id") or "").strip(),
                "caption": title,
                "rows": record.get("rows") if isinstance(record.get("rows"), list) else [],
                "html": str(record.get("html") or ""),
                "origin": "table-library",
            }
        )
        existing_table_ids.add(ref_id.lower())
    return assets


def load_example_library_by_chapter(structured_dir: Path) -> dict[str, list[dict[str, Any]]]:
    payload = load_json(structured_dir / "example_library.json")
    examples = payload.get("examples", [])
    by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not isinstance(examples, list):
        return by_chapter
    for example in examples:
        if not isinstance(example, dict):
            continue
        chapter_id = str(example.get("chapter") or "").strip()
        if chapter_id:
            by_chapter[chapter_id].append(example)
    return by_chapter


def extract_example_library_assets(
    chapter_id: str,
    example_library_by_chapter: dict[str, list[dict[str, Any]]],
    existing_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_example_ids = {
        str(asset.get("id", "")).lower()
        for asset in existing_assets
        if asset.get("kind") == "example"
    }
    assets: list[dict[str, Any]] = []
    for record in example_library_by_chapter.get(chapter_id, []):
        ref_id = str(record.get("example_id") or "").strip()
        if not ref_id or not is_formula_ref_valid_for_chapter(ref_id, chapter_id):
            continue
        if ref_id.lower() in existing_example_ids:
            continue
        content = str(record.get("content_markdown") or "").strip()
        assets.append(
            {
                "kind": "example",
                "id": ref_id,
                "anchor": asset_anchor("example", ref_id),
                "label": f"Example {ref_id}",
                "section_id": str(record.get("source_file") or "").replace(".json", ""),
                "excerpt": trim_text(plain_text(content or str(record.get("title") or "")), 480),
                "content_markdown": content,
                "origin": "example-library",
            }
        )
        existing_example_ids.add(ref_id.lower())
    return assets


def formula_needs_llm_repair(latex: str) -> bool:
    value = str(latex or "")
    if not value:
        return False
    if re.search(r"[^\x00-\x7f]", value):
        return True
    if value.count(r"\begin{") != value.count(r"\end{"):
        return True
    if re.search(r"\\(eqnarray|align\*?)\b", value):
        return True
    return False


def repair_formula_with_llm(client: Any, latex: str) -> str:
    payload = {
        "task": "Convert this LaTeX formula to KaTeX-compatible display math.",
        "constraints": [
            "Preserve mathematical meaning.",
            "Return strict JSON only.",
            "Do not include surrounding $$ delimiters.",
            "Prefer aligned, cases, matrix, frac, sum, int, left/right constructs supported by KaTeX.",
        ],
        "latex": latex,
        "output_schema": {"latex_render": "KaTeX-compatible LaTeX string"},
    }
    messages = [
        {
            "role": "system",
            "content": "Return strict JSON only. Do not explain. Do not invent new math.",
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    raw = client._post_chat_completion(messages=messages, json_mode=True)  # noqa: SLF001
    parsed = json.loads(raw)
    repaired = str(parsed.get("latex_render", "")).strip()
    return normalize_latex_for_katex(repaired) if repaired else ""


def enhance_formula_assets_with_llm(assets: list[dict[str, Any]], *, skip_llm: bool) -> list[dict[str, Any]]:
    if skip_llm or LLMClient is None:
        return assets
    suspect_indexes = [
        index for index, asset in enumerate(assets)
        if asset.get("kind") == "formula" and formula_needs_llm_repair(str(asset.get("latex_render") or asset.get("latex") or ""))
    ]
    if not suspect_indexes:
        return assets
    try:
        client = LLMClient()
    except Exception:
        return assets
    if getattr(client, "provider", "local") == "local":
        return assets
    next_assets = [dict(asset) for asset in assets]
    for index in suspect_indexes:
        original = str(next_assets[index].get("latex_render") or next_assets[index].get("latex") or "")
        try:
            repaired = repair_formula_with_llm(client, original)
        except Exception as exc:
            logger.warning("Formula LLM repair failed at asset %s: %s", index, exc)
            continue
        if repaired:
            next_assets[index]["latex_render"] = repaired
            next_assets[index]["latex_repair_status"] = "llm"
    return next_assets


def extract_blockquote(lines: list[str], start: int) -> tuple[list[str], int]:
    quote: list[str] = []
    index = start
    while index < len(lines) and lines[index].strip().startswith(">"):
        quote.append(dequote(lines[index]))
        index += 1
    return quote, index


def first_asset_header(quote: list[str]) -> str:
    return next((line.strip() for line in quote if line.strip()), "")


def nested_asset_segments(quote: list[str]) -> list[list[str]]:
    segments: list[list[str]] = []
    header_pattern = re.compile(
        r"\*\*(?:Formula\s+\([^)]+\)|Figure\s+A?\d+\.\d+[a-z]?|Table\s+A?\d+\.\d+[a-z]?)\*\*",
        re.IGNORECASE,
    )
    index = 0
    while index < len(quote):
        line = quote[index].strip()
        if not header_pattern.search(line):
            index += 1
            continue
        segment, index = collect_nested_asset_segment(quote, index, header_pattern)
        segments.append(segment)
    return segments


def collect_nested_asset_segment(
    quote: list[str],
    start: int,
    header_pattern: re.Pattern[str],
) -> tuple[list[str], int]:
    first = quote[start]
    formula = FORMULA_HEADER_PATTERN.search(first)
    figure = FIGURE_HEADER_PATTERN.search(first)
    segment = [first]
    index = start + 1
    in_math = False
    saw_math = False
    saw_figure_caption = False

    while index < len(quote):
        line = quote[index]
        stripped = line.strip()
        if header_pattern.search(stripped):
            break
        segment.append(line)
        index += 1

        if formula:
            if "$$" in stripped:
                count = stripped.count("$$")
                saw_math = True
                if count >= 2 and not in_math:
                    break
                in_math = not in_math
                if saw_math and not in_math:
                    break
            continue

        if figure:
            if stripped.startswith(f"Figure {figure.group('id')}"):
                saw_figure_caption = True
            if saw_figure_caption:
                break

    return segment, index


def parse_table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
    return rows


def extract_assets(markdown: str, chapter_id: str) -> list[dict[str, Any]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    sections = split_markdown_sections(markdown, chapter_id)
    section_by_line: list[tuple[int, dict[str, Any]]] = []
    line_no = 0
    for line in lines:
        match = SECTION_PATTERN.match(line)
        if match:
            raw_title = match.group("title").strip()
            unit_match = UNIT_TITLE_PATTERN.match(raw_title)
            section_id = unit_match.group("unit") if unit_match else ""
            section = next((item for item in sections if item["id"] == section_id), None)
            if section:
                section_by_line.append((line_no, section))
        line_no += 1

    def section_for_line(target_line: int) -> dict[str, Any] | None:
        current = None
        for line_index, section in section_by_line:
            if line_index <= target_line:
                current = section
            else:
                break
        return current

    assets: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith(">"):
            quote, next_index = extract_blockquote(lines, index)
            quote_text = "\n".join(quote)
            section = section_for_line(index)
            section_id = section["id"] if section else ""

            header = first_asset_header(quote)
            formula = FORMULA_HEADER_PATTERN.search(header)
            figure = FIGURE_HEADER_PATTERN.search(header)
            table = TABLE_HEADER_PATTERN.search(header)
            example = EXAMPLE_HEADER_PATTERN.search(header)

            if formula:
                ref_id = formula.group("id")
                latex = extract_latex_from_quote(quote)
                assets.append(
                    {
                        "kind": "formula",
                        "id": ref_id,
                        "anchor": asset_anchor("formula", ref_id),
                        "label": f"Formula ({ref_id})",
                        "section_id": section_id,
                        "latex": latex,
                        "latex_render": normalize_latex_for_katex(latex),
                    }
                )
            elif figure:
                ref_id = figure.group("id")
                image_match = re.search(r"!\[[^\]]*\]\((?P<src>[^)]+)\)", quote_text)
                caption = " ".join(line for line in quote if line.startswith(f"Figure {ref_id}"))
                assets.append(
                    {
                        "kind": "figure",
                        "id": ref_id,
                        "anchor": asset_anchor("figure", ref_id),
                        "label": f"Figure {ref_id}",
                        "section_id": section_id,
                        "src": image_match.group("src") if image_match else "",
                        "caption": caption,
                    }
                )
            elif table:
                ref_id = table.group("id")
                caption = " ".join(line for line in quote if line.startswith(f"Table {ref_id}"))
                rows = parse_table_rows(quote)
                assets.append(
                    {
                        "kind": "table",
                        "id": ref_id,
                        "anchor": asset_anchor("table", ref_id),
                        "label": f"Table {ref_id}",
                        "section_id": section_id,
                        "caption": caption,
                        "rows": rows,
                    }
                )
            elif example:
                ref_id = example.group("id")
                assets.append(
                    {
                        "kind": "example",
                        "id": ref_id,
                        "anchor": asset_anchor("example", ref_id),
                        "label": f"Example {ref_id}",
                        "section_id": section_id,
                        "excerpt": trim_text(plain_text(quote_text), 480),
                    }
                )
                for segment in nested_asset_segments(quote[1:]):
                    segment_text = "\n".join(segment)
                    nested_formula = FORMULA_HEADER_PATTERN.search(first_asset_header(segment))
                    nested_figure = FIGURE_HEADER_PATTERN.search(first_asset_header(segment))
                    nested_table = TABLE_HEADER_PATTERN.search(first_asset_header(segment))
                    if nested_formula:
                        nested_ref_id = nested_formula.group("id")
                        if any(item["kind"] == "formula" and item["id"] == nested_ref_id for item in assets):
                            continue
                        latex = extract_latex_from_quote(segment)
                        assets.append(
                            {
                                "kind": "formula",
                                "id": nested_ref_id,
                                "anchor": asset_anchor("formula", nested_ref_id),
                                "label": f"Formula ({nested_ref_id})",
                                "section_id": section_id,
                                "latex": latex,
                                "latex_render": normalize_latex_for_katex(latex),
                            }
                        )
                    elif nested_figure:
                        nested_ref_id = nested_figure.group("id")
                        if any(item["kind"] == "figure" and item["id"] == nested_ref_id for item in assets):
                            continue
                        image_match = re.search(r"!\[[^\]]*\]\((?P<src>[^)]+)\)", segment_text)
                        caption = " ".join(line for line in segment if line.strip().startswith(f"Figure {nested_ref_id}"))
                        assets.append(
                            {
                                "kind": "figure",
                                "id": nested_ref_id,
                                "anchor": asset_anchor("figure", nested_ref_id),
                                "label": f"Figure {nested_ref_id}",
                                "section_id": section_id,
                                "src": image_match.group("src") if image_match else "",
                                "caption": caption,
                            }
                        )
                    elif nested_table:
                        nested_ref_id = nested_table.group("id")
                        if any(item["kind"] == "table" and item["id"] == nested_ref_id for item in assets):
                            continue
                        caption = " ".join(line for line in segment if line.strip().startswith(f"Table {nested_ref_id}"))
                        assets.append(
                            {
                                "kind": "table",
                                "id": nested_ref_id,
                                "anchor": asset_anchor("table", nested_ref_id),
                                "label": f"Table {nested_ref_id}",
                                "section_id": section_id,
                                "caption": caption,
                                "rows": parse_table_rows(segment),
                            }
                        )
            index = next_index
            continue
        index += 1

    return assets


def extract_placeholder_formula_assets(
    markdown: str,
    chapter_id: str,
    structured_dir: Path,
    existing_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    current_parts = chapter_parts(chapter_id)
    current_book = current_parts[0] if current_parts else DEFAULT_BOOK_PREFIX
    existing_formula_ids = {
        str(asset.get("id", "")).lower()
        for asset in existing_assets
        if asset.get("kind") == "formula"
    }
    assets: list[dict[str, Any]] = []

    for section in split_markdown_sections(markdown, chapter_id):
        placeholders: list[str] = []
        for match in PLACEHOLDER_REF_PATTERN.finditer(section.get("text", "")):
            if match.group("kind").lower() != "formula":
                continue
            ref_id = match.group("id").strip()
            if chapter_ref_id(ref_id, current_book) != chapter_id:
                continue
            if ref_id.lower() in existing_formula_ids:
                continue
            placeholders.append(ref_id)
        if not placeholders:
            continue

        structured_path = structured_dir / f"{section['id']}.json"
        payload = load_json(structured_path)
        blocks = payload.get("blocks", []) if payload else []
        formulas: list[str] = []
        for block in blocks:
            formulas.extend(extract_display_math_chunks(str(block.get("content", ""))))

        for ref_id, latex in zip(placeholders, formulas):
            if not latex or ref_id.lower() in existing_formula_ids:
                continue
            assets.append(
                {
                    "kind": "formula",
                    "id": ref_id,
                    "anchor": asset_anchor("formula", ref_id),
                    "label": f"Formula ({ref_id})",
                    "section_id": section["id"],
                    "latex": latex,
                    "latex_render": normalize_latex_for_katex(latex),
                    "origin": "placeholder",
                }
            )
            existing_formula_ids.add(ref_id.lower())

    return assets


def section_lookup_for_formulas(chapter_id: str, structured_dir: Path) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for path in sorted(structured_dir.glob(f"{chapter_id}_*.json")):
        payload = load_json(path)
        section_id = str(payload.get("id") or path.stem)
        for block in payload.get("blocks", []):
            for latex in extract_display_math_chunks(str(block.get("content", ""))):
                lookup.setdefault(latex_key(latex), section_id)
    return lookup


def paddle_blocks_for_page(page: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = page.get("parsing_res_list")
    if not isinstance(blocks, list):
        pruned = page.get("prunedResult")
        if isinstance(pruned, dict):
            blocks = pruned.get("parsing_res_list")
    if not isinstance(blocks, list):
        return []
    indexed: list[tuple[int, dict[str, Any]]] = []
    for fallback_order, item in enumerate(blocks):
        if not isinstance(item, dict):
            continue
        raw_order = item.get("block_order")
        if raw_order is None:
            raw_order = item.get("order")
        try:
            order = int(raw_order)
        except (TypeError, ValueError):
            order = fallback_order
        indexed.append((order, item))
    return [item for _, item in sorted(indexed, key=lambda pair: pair[0])]


def block_center_y(block: dict[str, Any], fallback: int) -> float:
    bbox = block.get("block_bbox") or block.get("bbox")
    if isinstance(bbox, list) and len(bbox) >= 4:
        try:
            return (float(bbox[1]) + float(bbox[3])) / 2
        except (TypeError, ValueError):
            pass
    return float(fallback * 100)


def extract_paddle_formula_assets(
    chapter_id: str,
    structured_dir: Path,
    existing_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_formula_ids = {
        str(asset.get("id", "")).lower()
        for asset in existing_assets
        if asset.get("kind") == "formula"
    }
    corrections: dict[str, dict[str, str]] = {}
    if FORMULA_CORRECTIONS_PATH.is_file():
        payload = json.loads(FORMULA_CORRECTIONS_PATH.read_text(encoding="utf-8"))
        corrections = {
            str(key): value
            for key, value in (payload.get("corrections") or {}).items()
            if isinstance(value, dict)
        }

    def corrected_latex(ref_id: str, latex: str) -> str:
        key = f"{chapter_id}:{ref_id}"
        correction = corrections.get(key)
        if not correction:
            return latex
        old_hash = hashlib.sha256(latex.encode("utf-8")).hexdigest()
        replacement = str(correction.get("replacement") or "")
        if old_hash != correction.get("source_sha256") and latex != replacement:
            raise RuntimeError(f"Paddle formula drifted before correction: {key}")
        return replacement
    paddle_path = structured_dir.parent / "paddle_output" / f"{chapter_id}_full" / "intermediate" / "paddle_raw_response.json"
    try:
        pages = json.loads(paddle_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(pages, list):
        return []

    section_lookup = section_lookup_for_formulas(chapter_id, structured_dir)
    assets: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        blocks = paddle_blocks_for_page(page)
        display_blocks: list[tuple[int, dict[str, Any], str]] = []
        number_blocks: list[tuple[int, dict[str, Any], str]] = []
        for index, block in enumerate(blocks):
            if block.get("block_label") != "display_formula":
                if block.get("block_label") == "formula_number":
                    number = re.search(r"\(?\s*([A]?\d+(?:\.\d+)+(?:[a-z])?)\s*\)?", str(block.get("block_content", "")), re.IGNORECASE)
                    if number:
                        number_blocks.append((index, block, number.group(1)))
                continue
            latex_chunks = extract_display_math_chunks(str(block.get("block_content", "")))
            if not latex_chunks:
                continue
            display_blocks.append((index, block, latex_chunks[0]))
            ref_id = ""
            for follower in blocks[index + 1 : index + 4]:
                if follower.get("block_label") == "display_formula":
                    break
                if follower.get("block_label") == "formula_number":
                    number = re.search(r"\(?\s*([A]?\d+(?:\.\d+)+(?:[a-z])?)\s*\)?", str(follower.get("block_content", "")), re.IGNORECASE)
                    if number:
                        ref_id = number.group(1)
                    break
            if not ref_id or ref_id.lower() in existing_formula_ids:
                continue
            latex = corrected_latex(ref_id, latex_chunks[0])
            assets.append(
                {
                    "kind": "formula",
                    "id": ref_id,
                    "anchor": asset_anchor("formula", ref_id),
                    "label": f"Formula ({ref_id})",
                    "section_id": section_lookup.get(latex_key(latex), ""),
                    "latex": latex,
                    "latex_render": normalize_latex_for_katex(latex),
                    "origin": "paddle",
                }
            )
            existing_formula_ids.add(ref_id.lower())

        for number_index, number_block, ref_id in number_blocks:
            if ref_id.lower() in existing_formula_ids or not display_blocks:
                continue
            number_y = block_center_y(number_block, number_index)
            nearest = min(
                display_blocks,
                key=lambda item: (
                    abs(block_center_y(item[1], item[0]) - number_y),
                    abs(item[0] - number_index),
                ),
            )
            display_index, display_block, latex = nearest
            latex = corrected_latex(ref_id, latex)
            distance = abs(block_center_y(display_block, display_index) - number_y)
            if distance > 240:
                continue
            assets.append(
                {
                    "kind": "formula",
                    "id": ref_id,
                    "anchor": asset_anchor("formula", ref_id),
                    "label": f"Formula ({ref_id})",
                    "section_id": section_lookup.get(latex_key(latex), ""),
                    "latex": latex,
                    "latex_render": normalize_latex_for_katex(latex),
                    "origin": "paddle",
                }
            )
            existing_formula_ids.add(ref_id.lower())
    return assets


def discover_chapters(textbook_dir: Path, book_ids: set[str] | None = None) -> list[str]:
    ids: list[str] = []
    normalized_book_ids = {book_id.lower() for book_id in (book_ids or set())}
    for path in textbook_dir.glob("*_textbook.md"):
        match = CHAPTER_MD_PATTERN.fullmatch(path.name)
        if match and (not normalized_book_ids or match.group("book").lower() in normalized_book_ids):
            ids.append(match.group("id"))
    return sorted(ids, key=chapter_sort_key)


def asset_matches_reference(asset: dict[str, Any], ref_kind: str, ref_id: str) -> bool:
    asset_kind = str(asset.get("kind") or "").lower()
    wanted_kind = "formula" if str(ref_kind or "").lower() in {"equation", "formula"} else str(ref_kind or "").lower()
    if asset_kind != wanted_kind:
        return False
    asset_id = str(asset.get("id") or "").strip().lower()
    wanted_id = str(ref_id or "").strip().lower()
    if asset_id == wanted_id:
        return True
    if wanted_kind == "figure" and asset_id == re.sub(r"[a-z]$", "", wanted_id, flags=re.IGNORECASE):
        return True
    if wanted_kind == "formula" and re.fullmatch(r"a?\d+\.\d+(?:\.\d+)?", wanted_id, re.IGNORECASE):
        return bool(re.fullmatch(re.escape(wanted_id) + r"[a-z]", asset_id, re.IGNORECASE))
    return False


def find_asset_for_reference(assets: list[dict[str, Any]], ref_kind: str, ref_id: str) -> dict[str, Any] | None:
    exact = [
        asset for asset in assets
        if str(asset.get("id") or "").strip().lower() == str(ref_id or "").strip().lower()
        and asset_matches_reference(asset, ref_kind, ref_id)
    ]
    if exact:
        return exact[0]
    matches = [asset for asset in assets if asset_matches_reference(asset, ref_kind, ref_id)]
    if not matches:
        return None
    if str(ref_kind or "").lower() in {"equation", "formula"}:
        return sorted(matches, key=lambda item: formula_ref_sort_key(str(item.get("id", ""))))[0]
    return matches[0]


def resolve_chapter_id_for_ref(ref_id: str, book_prefix: str, chapter_cache: dict[str, dict[str, Any]]) -> str | None:
    target = chapter_ref_id(ref_id, book_prefix)
    if target in chapter_cache:
        return target
    if str(book_prefix or "").lower() == "genetics" and re.match(r"^a\d+", str(ref_id or ""), re.IGNORECASE):
        fallback = "Genetics_chapter27"
        if fallback in chapter_cache:
            return fallback
    return target


def build_source_link(
    *,
    textbook_dir: Path,
    source_chapter_id: str,
    reference: dict[str, str],
    chapter_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_payload = chapter_cache.get(source_chapter_id)
    markdown = source_payload.get("markdown", "") if source_payload else ""
    sections = source_payload.get("sections", []) if source_payload else []
    assets = source_payload.get("assets", []) if source_payload else []

    ref_kind = reference["kind"]
    ref_id = reference["id"]
    target_anchor = ""
    section_title = chapter_label(source_chapter_id)
    excerpt = ""

    if ref_kind != "chapter":
        asset = find_asset_for_reference(assets, ref_kind, ref_id)
        if asset:
            target_anchor = asset["anchor"]
            section_id = asset.get("section_id")
            section = next((item for item in sections if item["id"] == section_id), None)
            section_title = section.get("title") if section else asset.get("label", section_title)
            excerpt = asset.get("caption") or asset.get("excerpt") or context_window(markdown, reference["label"])

    if not target_anchor:
        needle = reference["label"] if ref_kind != "chapter" else ""
        for section in sections:
            body = f"{section.get('title', '')}\n{section.get('text', '')}"
            if not needle or re.search(re.escape(needle), body, flags=re.IGNORECASE):
                target_anchor = section["anchor"]
                section_title = section["title"]
                excerpt = context_window(body, needle)
                break

    if not target_anchor and sections:
        target_anchor = sections[0]["anchor"]
        section_title = sections[0]["title"]
        excerpt = sections[0].get("text_preview", "")

    return {
        "chapter_id": source_chapter_id,
        "label": reference["label"],
        "markdown_path": markdown_url(markdown_path_for_chapter(textbook_dir, source_chapter_id)),
        "anchor": target_anchor,
        "section_title": section_title,
        "ref_type": ref_kind,
        "ref_id": ref_id,
        "book_hint": reference.get("book_hint", ""),
        "link_scope": reference.get("link_scope", "current-book"),
        "excerpt": trim_text(excerpt, REFERENCE_WINDOW_CHARS),
    }


def external_reference_groups(
    *,
    current_chapter_id: str,
    refs_by_section: dict[str, list[dict[str, str]]],
    sections: list[dict[str, Any]],
    textbook_dir: Path,
    chapter_cache: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    current_parts = chapter_parts(current_chapter_id)
    current_book = current_parts[0] if current_parts else DEFAULT_BOOK_PREFIX

    for section_id, refs in refs_by_section.items():
        section = next((item for item in sections if item["id"] == section_id), None)
        for reference in refs:
            source_chapter_id = resolve_chapter_id_for_ref(
                reference["id"],
                target_book_for_reference(reference, current_book),
                chapter_cache,
            )
            if not source_chapter_id or source_chapter_id == current_chapter_id:
                continue
            if not is_prerequisite_source(current_chapter_id, source_chapter_id):
                continue
            if source_chapter_id not in chapter_cache:
                continue
            group = groups.setdefault(
                source_chapter_id,
                {
                    "id": f"prereq-{source_chapter_id.lower()}",
                    "title": f"{chapter_label(source_chapter_id)} prerequisites",
                    "source_chapter_id": source_chapter_id,
                    "used_in_sections": [],
                    "why_needed": "",
                    "key_points": [],
                    "source_links": [],
                    "source_excerpt": "",
                    "evidence_contexts": [],
                    "summary_status": "rules",
                },
            )
            if section_id not in group["used_in_sections"]:
                group["used_in_sections"].append(section_id)
                if section:
                    group["evidence_contexts"].append(
                        {
                            "section_id": section_id,
                            "section_title": section.get("title", ""),
                            "section_anchor": section.get("anchor", ""),
                            "current_excerpt": trim_text(plain_text(section.get("text", "")), 520),
                        }
                    )
            link = build_source_link(
                textbook_dir=textbook_dir,
                source_chapter_id=source_chapter_id,
                reference=reference,
                chapter_cache=chapter_cache,
            )
            link_key = (link["chapter_id"], link["ref_type"], link["ref_id"], link.get("link_scope", ""))
            existing = {
                (item["chapter_id"], item["ref_type"], item["ref_id"], item.get("link_scope", ""))
                for item in group["source_links"]
            }
            if link_key not in existing:
                group["source_links"].append(link)
            if not group["source_excerpt"] and link.get("excerpt"):
                group["source_excerpt"] = link["excerpt"]

    prerequisites = []
    for source_chapter_id, group in groups.items():
        labels = [link["label"] for link in group["source_links"][:6]]
        chapter_name = chapter_label(source_chapter_id)
        explicit_asset_refs = sum(1 for link in group["source_links"] if link.get("ref_type") != "chapter")
        usage_count = len(group["used_in_sections"])
        link_count = len(group["source_links"])
        group["usage_count"] = usage_count
        group["explicit_asset_refs"] = explicit_asset_refs
        group["priority_score"] = usage_count * 10 + link_count * 2 + explicit_asset_refs
        group["why_needed"] = f"本章引用了 {chapter_name} 的 {', '.join(labels) or '基础内容'}，阅读当前章节前需要回顾这些外部知识。"
        group["key_points"] = [
            f"先定位 {chapter_name} 中被引用的公式、图表或例子。",
            "重点复习这些来源如何定义变量、假设和结论。",
            "回到当前章节时，把它们作为后续模型推导的前提。"
        ]
        prerequisites.append(group)

    return sorted(
        prerequisites,
        key=lambda item: (
            -int(item.get("priority_score", 0)),
            chapter_sort_key(item["source_chapter_id"]),
        ),
    )


def default_concept_title(item: dict[str, Any]) -> str:
    chapter = chapter_label(str(item.get("source_chapter_id", "")))
    first_asset = next(
        (link for link in item.get("source_links", []) if link.get("ref_type") != "chapter"),
        None,
    )
    section_title = str((first_asset or {}).get("section_title", "")).strip()
    if section_title and not section_title.lower().startswith(chapter.lower()):
        tail = [part.strip() for part in section_title.split("/") if part.strip()]
        if tail:
            return f"{chapter} · {tail[-1][:58]}"
    return chapter


def link_matches_keep(link: dict[str, Any], keep_item: Any, index: int) -> bool:
    if isinstance(keep_item, int):
        return keep_item == index
    value = str(keep_item or "").strip().lower()
    if not value:
        return False
    candidates = {
        str(index).lower(),
        str(index + 1).lower(),
        str(link.get("label", "")).lower(),
        str(link.get("ref_id", "")).lower(),
        f"{link.get('ref_type', '')} {link.get('ref_id', '')}".strip().lower(),
    }
    return value in candidates


def filter_links_from_llm(item: dict[str, Any], keep_values: Any) -> list[dict[str, Any]]:
    links = list(item.get("source_links", []))
    if not links:
        return []
    if isinstance(keep_values, list) and keep_values:
        kept = [
            link
            for index, link in enumerate(links)
            if any(link_matches_keep(link, keep_item, index) for keep_item in keep_values)
        ]
        if kept:
            return kept
    explicit = [link for link in links if link.get("ref_type") != "chapter"]
    return explicit or links[:1]


def parse_keep_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    text = str(value or "").strip().lower()
    return text in {"keep", "true", "yes", "y", "1", "valid", "prerequisite"}


def bounded_priority(value: Any, fallback: int) -> int:
    try:
        score = int(float(value))
    except (TypeError, ValueError):
        return fallback
    return max(1, min(200, score))


def enhance_prerequisites_with_llm(
    *,
    prerequisites: list[dict[str, Any]],
    current_chapter: str,
    skip_llm: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if skip_llm or not prerequisites or LLMClient is None:
        return [], {"provider": "skipped", "model": "", "validated_only": True}
    try:
        client = LLMClient()
    except Exception as exc:  # pragma: no cover
        return [], {"provider": "unavailable", "error": str(exc), "validated_only": True}
    if getattr(client, "provider", "local") == "local":
        metrics = client.get_metrics()
        metrics["validated_only"] = True
        return [], metrics

    enhanced: list[dict[str, Any]] = []
    for item in prerequisites:
        source_links = [
            {
                "index": index,
                "label": link.get("label", ""),
                "ref_type": link.get("ref_type", ""),
                "ref_id": link.get("ref_id", ""),
                "section_title": link.get("section_title", ""),
                "excerpt": link.get("excerpt", ""),
            }
            for index, link in enumerate(item.get("source_links", [])[:12])
        ]
        payload = {
            "task": (
                "Decide whether this external chapter is a real prerequisite learning scaffold "
                "for the current textbook chapter. Drop coincidental, weak, or self-evident references."
            ),
            "current_chapter": current_chapter,
            "source_chapter": item["source_chapter_id"],
            "current_contexts": item.get("evidence_contexts", [])[:6],
            "candidate_source_links": source_links,
            "rules": [
                "Keep only if the current chapter relies on concepts, formulas, examples, tables, or figures from the source chapter.",
                "Drop if the evidence is only a generic chapter mention with no reusable concept.",
                "Keep source_links_keep small: choose only the links a student should click first.",
                "Write Chinese explanations for a student or teacher preparing this chapter.",
            ],
            "output_schema": {
                "keep": "boolean",
                "concept_title": "short title like 'Chapter 7 · Mutation-selection balance'",
                "nav_label": "very short label for navigation",
                "why_needed": "1-2 concise Chinese sentences",
                "key_points": ["2-4 concise Chinese review points"],
                "source_links_keep": ["0-based indices, labels, or ref_ids from candidate_source_links"],
                "evidence_summary": "one concise Chinese sentence explaining the evidence",
                "priority_score": "1-200 integer",
            },
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Return strict JSON only. Do not invent citations. "
                    "If evidence is weak or generic, set keep=false. "
                    "All Chinese text must be valid UTF-8."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
        try:
            raw = client._post_chat_completion(messages=messages, json_mode=True)  # noqa: SLF001
            parsed = json.loads(raw)
        except Exception as exc:
            logger.warning("Prerequisite LLM adjudication failed for %s: %s", item.get("id"), exc)
            continue
        if not parse_keep_flag(parsed.get("keep")):
            continue

        kept_links = filter_links_from_llm(item, parsed.get("source_links_keep"))
        if not kept_links:
            continue

        fallback_score = int(item.get("priority_score", 0) or 0)
        next_item = {
            key: value
            for key, value in item.items()
            if key not in {"evidence_contexts"}
        }
        next_item["source_links"] = kept_links
        next_item["validated_by_llm"] = True
        next_item["summary_status"] = "llm-validated"
        next_item["concept_title"] = str(parsed.get("concept_title") or default_concept_title(item)).strip()
        next_item["title"] = next_item["concept_title"]
        next_item["nav_label"] = str(parsed.get("nav_label") or next_item["concept_title"]).strip()[:72]
        next_item["why_needed"] = str(parsed.get("why_needed") or "").strip()
        next_item["evidence_summary"] = str(parsed.get("evidence_summary") or "").strip()
        next_item["priority_score"] = bounded_priority(parsed.get("priority_score"), fallback_score)

        points = parsed.get("key_points")
        if isinstance(points, list):
            clean_points = [str(point).strip() for point in points if str(point).strip()]
            next_item["key_points"] = clean_points[:4]
        else:
            next_item["key_points"] = []
        enhanced.append(next_item)

    enhanced.sort(
        key=lambda entry: (
            -int(entry.get("priority_score", 0)),
            chapter_sort_key(entry["source_chapter_id"]),
        )
    )
    metrics = client.get_metrics()
    metrics["validated_only"] = True
    return enhanced, metrics


def choose_semantic_source_link(
    prerequisite: dict[str, Any] | None,
    source_sections: list[dict[str, Any]],
) -> dict[str, Any] | None:
    links = list((prerequisite or {}).get("source_links", []))
    if not links:
        return None
    overview_anchor = str(source_sections[0].get("anchor", "")) if source_sections else ""
    explicit_links = [link for link in links if link.get("ref_type") != "chapter" and link.get("anchor")]
    non_overview_explicit = [
        link for link in explicit_links
        if str(link.get("anchor", "")) != overview_anchor
    ]
    for candidates in (non_overview_explicit, explicit_links, links):
        for link in candidates:
            if link.get("anchor"):
                return link
    return None


def fallback_semantic_link(
    *,
    textbook_dir: Path,
    source_chapter_id: str,
    source_sections: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not source_sections:
        return None
    first = source_sections[0]
    return {
        "chapter_id": source_chapter_id,
        "label": chapter_label(source_chapter_id),
        "markdown_path": markdown_url(markdown_path_for_chapter(textbook_dir, source_chapter_id)),
        "anchor": first.get("anchor", ""),
        "section_title": first.get("title", chapter_label(source_chapter_id)),
        "ref_type": "chapter",
        "ref_id": str(chapter_parts(source_chapter_id)[2]) if chapter_parts(source_chapter_id) else "",
        "excerpt": first.get("text_preview", ""),
    }


def build_semantic_chapter_links(
    *,
    current_chapter_id: str,
    refs_by_section: dict[str, list[dict[str, str]]],
    sections: list[dict[str, Any]],
    prerequisites: list[dict[str, Any]],
    textbook_dir: Path,
    chapter_cache: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    current_parts = chapter_parts(current_chapter_id)
    current_book = current_parts[0] if current_parts else DEFAULT_BOOK_PREFIX
    prereqs_by_source = {
        item.get("source_chapter_id"): item
        for item in prerequisites
        if item.get("validated_by_llm") is True
    }
    section_by_id = {section["id"]: section for section in sections}
    semantic_links: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for section_id, refs in refs_by_section.items():
        section = section_by_id.get(section_id)
        for reference in refs:
            if reference.get("kind") != "chapter":
                continue
            source_chapter_id = resolve_chapter_id_for_ref(
                reference.get("id", ""),
                target_book_for_reference(reference, current_book),
                chapter_cache,
            )
            if not source_chapter_id or source_chapter_id == current_chapter_id:
                continue
            if source_chapter_id not in chapter_cache:
                continue
            key = (section_id, source_chapter_id)
            if key in seen:
                continue
            seen.add(key)

            source_sections = chapter_cache[source_chapter_id].get("sections", [])
            prerequisite = prereqs_by_source.get(source_chapter_id)
            target = None
            if prerequisite and section_id in set(prerequisite.get("used_in_sections", [])):
                target = choose_semantic_source_link(prerequisite, source_sections)
            if target is None and prerequisite:
                target = choose_semantic_source_link(prerequisite, source_sections)
            if target is None:
                target = fallback_semantic_link(
                    textbook_dir=textbook_dir,
                    source_chapter_id=source_chapter_id,
                    source_sections=source_sections,
                )
            if not target:
                continue
            body = f"{section.get('title', '')}\n{section.get('text', '')}" if section else ""
            semantic_links.append(
                {
                    "current_section_id": section_id,
                    "current_anchor": section.get("anchor", "") if section else "",
                    "source_chapter_id": source_chapter_id,
                    "label": reference.get("label", chapter_label(source_chapter_id)),
                    "target_anchor": target.get("anchor", ""),
                    "target_label": target.get("label", chapter_label(source_chapter_id)),
                    "target_ref_type": target.get("ref_type", "chapter"),
                    "target_ref_id": target.get("ref_id", reference.get("id", "")),
                    "target_section_title": target.get("section_title", ""),
                    "book_hint": reference.get("book_hint", ""),
                    "link_scope": reference.get("link_scope", "current-book"),
                    "context_excerpt": context_window(body, reference.get("label", "")),
                    "match_source": "llm-prerequisite" if prerequisite else "chapter-overview",
                }
            )

    return semantic_links


def load_config() -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    return config if config else {}


def configured_books(config: dict[str, Any], selected_books: set[str] | None = None) -> list[dict[str, str]]:
    raw_books = config.get("books")
    books: list[dict[str, str]] = []
    if isinstance(raw_books, list):
        for item in raw_books:
            if not isinstance(item, dict):
                continue
            book_id = str(item.get("id") or "").strip()
            if not book_id:
                continue
            if selected_books and book_id not in selected_books:
                continue
            books.append(
                {
                    "id": book_id,
                    "label": str(item.get("label") or book_id).strip(),
                    "default_chapter": str(item.get("default_chapter") or f"{book_id}_chapter1").strip(),
                }
            )
    if not books:
        fallback_id = str(config.get("book_prefix") or DEFAULT_BOOK_PREFIX)
        books = [
            {
                "id": fallback_id,
                "label": "Evolution and Selection of Quantitative Traits" if fallback_id == "Evolution" else fallback_id,
                "default_chapter": str(config.get("default_chapter") or DEFAULT_CHAPTER),
            }
        ]
    return books


def parse_csv_arg(raw_value: str) -> set[str]:
    return {part.strip() for part in raw_value.split(",") if part.strip()}


def existing_generated_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    return load_json(STUDY_DATASET_PATH), load_json(PREREQUISITE_AUDIT_PATH)


def existing_chapter_payload(existing_dataset: dict[str, Any], chapter_id: str) -> dict[str, Any]:
    data = existing_dataset.get("data")
    if isinstance(data, dict):
        payload = data.get(chapter_id)
        if isinstance(payload, dict):
            return payload
    split_payload = load_json(CHAPTER_DATA_DIR / f"{chapter_id}.json")
    if split_payload:
        return split_payload
    return {}


def load_legacy_dataset(spec: str) -> dict[str, Any]:
    """Load an old inline dataset from a path or an explicit git revision spec."""
    value = str(spec or "").strip()
    if not value:
        return {}
    if value.startswith("git:"):
        revision_path = value[4:]
        if ":" not in revision_path:
            raise ValueError("Git legacy spec must be git:<revision>:<repo-path>")
        revision, repo_path = revision_path.split(":", 1)
        raw = subprocess.check_output(["git", "show", f"{revision}:{repo_path}"], cwd=ROOT_DIR)
        payload = json.loads(raw.decode("utf-8-sig"))
        return payload if isinstance(payload, dict) else {}
    return load_json(resolve_repo_path(value, value))


def existing_audit_row(existing_audit: dict[str, Any], chapter_id: str) -> dict[str, Any]:
    rows = existing_audit.get("rows")
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get("chapter_id") == chapter_id:
                return row
    return {}


def should_preserve_existing_prerequisites(
    *,
    existing_payload: dict[str, Any],
    llm_enabled: bool,
    skip_llm: bool,
) -> bool:
    # A no-LLM rebuild must retain previously validated decisions.  Only an
    # explicitly enabled LLM pass is allowed to replace them.
    if llm_enabled:
        return False
    prerequisites = existing_payload.get("prerequisites")
    if not isinstance(prerequisites, list) or not prerequisites:
        return False
    return all(isinstance(item, dict) and item.get("validated_by_llm") is True for item in prerequisites)


def build_dataset(
    config: dict[str, Any],
    *,
    llm_chapters: set[str],
    selected_books: set[str] | None,
    all_llm: bool,
    skip_llm: bool,
    existing_dataset_override: dict[str, Any] | None = None,
    release: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    existing_dataset, existing_audit = existing_generated_payloads()
    if existing_dataset_override:
        existing_dataset = existing_dataset_override
    textbook_dir = resolve_repo_path(config.get("textbook_dir"), "data/textbook")
    structured_dir = resolve_repo_path(config.get("structured_dir"), "data/structured")
    formula_library_by_chapter = load_formula_library_by_chapter(structured_dir)
    table_library_by_chapter = load_table_library_by_chapter(structured_dir)
    example_library_by_chapter = load_example_library_by_chapter(structured_dir)
    books = configured_books(config, selected_books)
    book_order = {book["id"]: index for index, book in enumerate(books)}
    book_ids = set(book_order)
    default_chapter = str(config.get("default_chapter") or DEFAULT_CHAPTER)
    chapter_ids = sorted(discover_chapters(textbook_dir, book_ids), key=lambda chapter_id: chapter_sort_key_for_books(chapter_id, book_order))
    prerequisite_llm_chapters = set(chapter_ids) if all_llm else (llm_chapters or {default_chapter})
    formula_llm_chapters = llm_chapters or {default_chapter}

    chapter_cache: dict[str, dict[str, Any]] = {}
    for chapter_id in chapter_ids:
        path = markdown_path_for_chapter(textbook_dir, chapter_id)
        markdown = path.read_text(encoding="utf-8-sig")
        sections = split_markdown_sections(markdown, chapter_id)
        assets = extract_assets(markdown, chapter_id)
        assets.extend(extract_formula_library_assets(chapter_id, formula_library_by_chapter, assets))
        assets.extend(extract_table_library_assets(chapter_id, table_library_by_chapter, assets))
        assets.extend(extract_example_library_assets(chapter_id, example_library_by_chapter, assets))
        assets.extend(extract_paddle_formula_assets(chapter_id, structured_dir, assets))
        assets.extend(extract_placeholder_formula_assets(markdown, chapter_id, structured_dir, assets))
        assets = enhance_formula_assets_with_llm(
            assets,
            skip_llm=skip_llm or chapter_id not in formula_llm_chapters,
        )
        refs = section_reference_index(sections)
        chapter_cache[chapter_id] = {
            "markdown": markdown,
            "sections": sections,
            "assets": assets,
            "references": refs,
        }

    chapters: list[dict[str, Any]] = []
    data: dict[str, Any] = {}
    audit_rows: list[dict[str, Any]] = []
    for index, chapter_id in enumerate(chapter_ids, start=1):
        cached = chapter_cache[chapter_id]
        candidate_prerequisites = external_reference_groups(
            current_chapter_id=chapter_id,
            refs_by_section=cached["references"],
            sections=cached["sections"],
            textbook_dir=textbook_dir,
            chapter_cache=chapter_cache,
        )
        llm_enabled = not skip_llm and chapter_id in prerequisite_llm_chapters
        prerequisites, llm_metrics = enhance_prerequisites_with_llm(
            prerequisites=candidate_prerequisites,
            current_chapter=chapter_label(chapter_id),
            skip_llm=not llm_enabled,
        )
        existing_payload = existing_chapter_payload(existing_dataset, chapter_id)
        preserved_existing = should_preserve_existing_prerequisites(
            existing_payload=existing_payload,
            llm_enabled=llm_enabled,
            skip_llm=skip_llm,
        )
        if preserved_existing:
            prerequisites = list(existing_payload.get("prerequisites", []))
            previous_llm = existing_payload.get("llm")
            if isinstance(previous_llm, dict):
                llm_metrics = {**previous_llm, "preserved_from_previous_build": True}
        if release and isinstance(llm_metrics, dict):
            cache_dir = str(llm_metrics.get("cache_dir") or "")
            if cache_dir:
                try:
                    llm_metrics["cache_dir"] = Path(cache_dir).resolve().relative_to(ROOT_DIR).as_posix()
                except (OSError, ValueError):
                    llm_metrics["cache_dir"] = "external-cache"
        print(
            f"[{index}/{len(chapter_ids)}] {chapter_id}: "
            f"candidates={len(candidate_prerequisites)} validated={len(prerequisites)} "
            f"llm={'yes' if llm_enabled else 'preserve' if preserved_existing else 'no'}",
            flush=True,
        )
        audit_rows.append(
            {
                "chapter_id": chapter_id,
                "book": chapter_parts(chapter_id)[0] if chapter_parts(chapter_id) else "",
                "candidate_count": len(candidate_prerequisites),
                "validated_count": len(prerequisites),
                "dropped_count": max(0, len(candidate_prerequisites) - len(prerequisites)),
                "llm_requested": llm_enabled,
                "preserved_from_previous_build": preserved_existing,
                "llm": llm_metrics,
            }
        )
        semantic_chapter_links = build_semantic_chapter_links(
            current_chapter_id=chapter_id,
            refs_by_section=cached["references"],
            sections=cached["sections"],
            prerequisites=prerequisites,
            textbook_dir=textbook_dir,
            chapter_cache=chapter_cache,
        )
        chapter_meta = chapter_parts(chapter_id)
        chapter_book = chapter_meta[0] if chapter_meta else ""
        chapter_kind = chapter_meta[1] if chapter_meta else "chapter"
        chapters.append(
            {
                "id": chapter_id,
                "label": chapter_label(chapter_id),
                "book": chapter_book,
                "book_id": chapter_book,
                "kind": chapter_kind,
                "markdown_path": markdown_url(markdown_path_for_chapter(textbook_dir, chapter_id)),
                "data_path": f"./data/generated/chapters/{chapter_id}.json",
                "section_count": len(cached["sections"]),
                "asset_count": len(cached["assets"]),
                "prerequisite_count": len(prerequisites),
            }
        )
        data[chapter_id] = {
            "sections": [
                {
                    "id": section["id"],
                    "title": section["title"],
                    "nav_label": section.get("nav_label") or short_nav_label(section["title"]),
                    "raw_title": section["raw_title"],
                    "level": section["level"],
                    "depth": max(0, int(section["level"]) - 1),
                    "anchor": section["anchor"],
                    "text_preview": section["text_preview"],
                }
                for section in cached["sections"]
            ],
            "assets": cached["assets"],
            "references": cached["references"],
            "semantic_chapter_links": semantic_chapter_links,
            "prerequisites": prerequisites,
            "llm": llm_metrics,
        }

    generated_at = (
        datetime.fromtimestamp(int(os.environ.get("SOURCE_DATE_EPOCH", "0")), timezone.utc).isoformat()
        if release else datetime.now().isoformat(timespec="seconds")
    )
    dataset = {
        "generated_at": generated_at,
        "version": 4,
        "build_mode": "offline-release" if release else "development",
        "remote_llm_calls_allowed": not release,
        "books": books,
        "textbook_dir": markdown_url(textbook_dir),
        "default_book": str(config.get("default_book") or (books[0]["id"] if books else DEFAULT_BOOK_PREFIX)),
        "default_chapter": default_chapter,
        "chapters": chapters,
        "data_mode": "split",
        "_chapter_data": data,
    }
    audit = {
        "generated_at": dataset["generated_at"],
        "books": [book["id"] for book in books],
        "llm_mode": "offline-release" if release else ("all" if all_llm else ("chapters" if llm_chapters else "default")),
        "remote_llm_calls_allowed": not release,
        "rows": audit_rows,
    }
    return dataset, audit


def write_split_dataset(dataset: dict[str, Any], chapter_data: dict[str, Any]) -> None:
    CHAPTER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    expected = {f"{chapter_id}.json" for chapter_id in chapter_data}
    for stale in CHAPTER_DATA_DIR.glob("*.json"):
        if stale.name not in expected:
            stale.unlink()
    for chapter_id, payload in chapter_data.items():
        write_json(CHAPTER_DATA_DIR / f"{chapter_id}.json", payload)
    write_json(STUDY_DATASET_PATH, dataset)


def parse_chapter_arg(raw_value: str) -> set[str]:
    return parse_csv_arg(raw_value)


def release_cache_fingerprint() -> dict[str, Any]:
    files = [STUDY_DATASET_PATH, PREREQUISITE_AUDIT_PATH, FORMULA_CORRECTIONS_PATH]
    files.extend(sorted(CHAPTER_DATA_DIR.glob("*.json")))
    entries = {}
    for path in files:
        if path.is_file():
            entries[path.relative_to(ROOT_DIR).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema": "study_reader_release_cache.v1",
        "prompt_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model": "cached-results-only",
        "cache_sha256": hashlib.sha256(
            json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "entries": entries,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the Study Reader dataset.")
    parser.add_argument("--books", default="", help="Comma-separated book ids to index, e.g. Evolution,Genetics.")
    parser.add_argument("--chapters", default="", help="Comma-separated chapters that should receive LLM summaries.")
    parser.add_argument("--all-llm", action="store_true", help="Run LLM prerequisite adjudication for every indexed chapter.")
    parser.add_argument("--skip-llm", action="store_true", help="Build rules-only prerequisites.")
    parser.add_argument(
        "--release", action="store_true",
        help="Deterministic offline release build; forbids remote LLM calls and records cache provenance.",
    )
    parser.add_argument(
        "--legacy-dataset",
        default="",
        help="Optional v3 inline dataset path or git:<revision>:<repo-path> used only to preserve prior LLM results.",
    )
    args = parser.parse_args(argv)
    if args.release and (args.all_llm or args.chapters or not args.skip_llm):
        parser.error("--release requires --skip-llm and cannot be combined with --all-llm/--chapters")
    if args.release:
        for name in (
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
            "AZURE_OPENAI_API_KEY", "DEEPSEEK_API_KEY",
        ):
            os.environ.pop(name, None)

    config = load_config()
    selected_books = parse_csv_arg(args.books) or None
    llm_chapters = parse_chapter_arg(args.chapters)
    dataset, audit = build_dataset(
        config,
        llm_chapters=llm_chapters,
        selected_books=selected_books,
        all_llm=args.all_llm,
        skip_llm=args.skip_llm,
        existing_dataset_override=load_legacy_dataset(args.legacy_dataset),
        release=args.release,
    )
    chapter_data = dataset.pop("_chapter_data", {})
    write_split_dataset(dataset, chapter_data)
    write_json(PREREQUISITE_AUDIT_PATH, audit)
    if args.release:
        write_json(BUILD_PROVENANCE_PATH, release_cache_fingerprint())
    print(f"Study dataset written: {STUDY_DATASET_PATH}")
    print(f"Prerequisite audit written: {PREREQUISITE_AUDIT_PATH}")
    print(f"Chapters indexed: {len(dataset['chapters'])}")
    if args.skip_llm:
        print("LLM chapters: skipped")
    elif args.all_llm:
        print("LLM chapters: all indexed chapters")
    else:
        print(f"LLM chapters: {', '.join(sorted(llm_chapters or {dataset['default_chapter']}))}")


if __name__ == "__main__":
    main()
