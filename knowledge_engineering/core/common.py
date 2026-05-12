"""Core shared utilities for the knowledge engineering pipeline.

The pipeline modules are intentionally conservative about behavior.  Keep this
module limited to small, deterministic helpers that already existed in more
than one place.
"""

from __future__ import annotations

from datetime import datetime, timezone
import html
import json
import re
from pathlib import Path
from typing import Any, Iterable


HTML_TAG_RE = re.compile(r"<[^>]+>")
HTML_TABLE_ROW_RE = re.compile(r"<tr[^>]*>(?P<body>.*?)</tr>", re.IGNORECASE | re.DOTALL)
HTML_TABLE_CELL_RE = re.compile(r"<t[dh][^>]*>(?P<body>.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)


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


def append_jsonl_row(path: str | Path, payload: dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False))
        handle.write("\n")


def write_json_path(path: str | Path, payload: Any) -> None:
    write_json(Path(path), payload)


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_html(text: str) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = HTML_TAG_RE.sub(" ", value)
    return collapse_ws(value)


def rows_from_html_table(table_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_match in HTML_TABLE_ROW_RE.finditer(str(table_html or "")):
        row_cells: list[str] = []
        for cell_match in HTML_TABLE_CELL_RE.finditer(row_match.group("body")):
            row_cells.append(strip_html(cell_match.group("body")))
        if row_cells and any(cell for cell in row_cells):
            rows.append(row_cells)
    return rows


def table_body_text_from_rows(rows: Iterable[Iterable[Any]]) -> str:
    cells: list[str] = []
    for row in rows:
        if not isinstance(row, (list, tuple)):
            continue
        for cell in row:
            value = collapse_ws(str(cell or ""))
            if value:
                cells.append(value)
    return collapse_ws(" ".join(cells))


def normalize_formula_reference_id(reference: str) -> str:
    value = str(reference or "").strip()
    if value.startswith("formula_"):
        return value.removeprefix("formula_")
    return value


def formula_sort_key(reference: str) -> tuple[int, int, int, int, str]:
    label = normalize_formula_reference_id(reference)
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?([A-Za-z]?)", label)
    if not match:
        return (9999, 9999, 9999, 9999, label)
    suffix = match.group(4).lower()
    suffix_rank = 0 if not suffix else ord(suffix) - 96
    subindex = int(match.group(3)) if match.group(3) else 0
    return (int(match.group(1)), int(match.group(2)), subindex, suffix_rank, label)


def sort_formula_refs(references: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for reference in references:
        value = normalize_formula_reference_id(reference)
        if value and value not in seen:
            seen.append(value)
    return sorted(seen, key=formula_sort_key)


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

    chapter_inline_match = re.fullmatch(r"inline_([A-Za-z]+)(\d+)", value, flags=re.IGNORECASE)
    if chapter_inline_match:
        suffix = chapter_inline_match.group(1).lower()
        suffix_rank = 0 if not suffix else ord(suffix[0]) - 96
        return (1, int(chapter_inline_match.group(2)), 0, 0, suffix_rank, value)

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


def table_reference_key(current_chapter: str, table_id: str) -> str:
    table = str(table_id or "").strip()
    if not table:
        return ""
    numbered = re.fullmatch(r"(\d+)\.\d+(?:\.\d+)?[A-Za-z]?", table)
    if numbered:
        return f"chapter{int(numbered.group(1))}:{table}"

    chapter = str(current_chapter or "").strip().lower()
    if not chapter:
        return ""
    return f"{chapter}:{table}"


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
