from __future__ import annotations

import json
import os
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CHUNK_FILE_RE = re.compile(r"^((?:(?:[A-Za-z]+)_)?(?:chapter|appendix)\d+)_(\d+)\.json$", re.IGNORECASE)
NUMBERED_REF_RE = re.compile(r"^(\d+)\.\d+")
FIGURE_TEXT_REF_RE = re.compile(r"\bFigure(?:s)?\s+(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"\[\[(?P<tag>SEE_FORMULA|SEE_TABLE|SEE_EXAMPLE|SEE_FIGURE|TABLE|FORMULA|EXAMPLE|FIGURE):(?P<id>[^\]]+)\]\]",
    re.IGNORECASE,
)
HTML_TABLE_RE = re.compile(
    r"<table\b.*?</table>(?:\s+\*\s+[^<]{1,1000}?\.)?",
    re.IGNORECASE | re.DOTALL,
)
SUPPORTED_OPERATOR_MACROS = {
    "logit",
}
NESTED_SUBSCRIPT_RE = re.compile(
    r"\\(?P<command>[A-Za-z]+)_(?P<first>[A-Za-z0-9]+)_(?P<second>[A-Za-z0-9]+)(?=(?:\^|[\s,.;:)\]}]|$))"
)


@dataclass(frozen=True)
class TextbookExportResult:
    chapter: str
    output_path: Path
    chunk_count: int


def book_id_from_chapter(chapter: str) -> str:
    match = re.match(r"^(?P<book>[A-Za-z]+)_(?:chapter|appendix)\d+", str(chapter or ""), re.IGNORECASE)
    return match.group("book") if match else ""


def canonical_formula_latex(value: str) -> str:
    value = str(value or "")
    value = re.sub(r"\$", "", value)
    value = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", value)
    value = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\operatorname\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\tag\{[^}]*\}", "", value)
    return re.sub(r"\s+", "", value)


def parse_chapter_filter(raw: str | None) -> set[str] | None:
    if raw is None or not str(raw).strip():
        return None
    chapters = {
        normalize_chapter_id(part)
        for part in str(raw).split(",")
        if normalize_chapter_id(part)
    }
    return chapters or None


def chapter_matches_filter(chapter: str, chapter_filter: set[str]) -> bool:
    normalized = normalize_chapter_id(chapter)
    if normalized in chapter_filter:
        return True
    unprefixed = re.sub(r"^[A-Za-z]+_", "", normalized)
    return unprefixed in chapter_filter


def export_textbooks(
    structured_dir: str | Path,
    out_dir: str | Path,
    chapters: Iterable[str] | None = None,
    figure_library: str | Path | None = None,
    book_id: str | None = None,
    books: Iterable[str] | None = None,
) -> list[TextbookExportResult]:
    structured_path = Path(structured_dir)
    output_path = Path(out_dir)
    figure_library_path = Path(figure_library) if figure_library else default_figure_library_path(structured_path)
    chapter_filter = (
        {normalize_chapter_id(chapter) for chapter in chapters if normalize_chapter_id(chapter)}
        if chapters is not None
        else None
    )
    book_filter = {str(book).strip().lower() for book in (books or []) if str(book).strip()}

    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in structured_path.glob("*_*.json"):
        match = CHUNK_FILE_RE.fullmatch(path.name)
        if not match:
            continue
        chapter = match.group(1)
        if book_filter and book_id_from_chapter(chapter).lower() not in book_filter:
            continue
        if chapter_filter is not None and not chapter_matches_filter(chapter, chapter_filter):
            continue
        grouped[chapter].append(path)

    output_path.mkdir(parents=True, exist_ok=True)
    renderer = TextbookRenderer(
        structured_path,
        figure_library=figure_library_path,
        output_dir=output_path,
        book_id=book_id,
    )

    results: list[TextbookExportResult] = []
    for chapter in sorted(grouped, key=chapter_sort_key):
        chunk_paths = sorted(grouped[chapter], key=chunk_file_sort_key)
        chunks = [read_json(path) for path in chunk_paths]
        markdown = renderer.render_chapter(chapter, chunks)
        target = output_path / f"{chapter}_textbook.md"
        target.write_text(markdown, encoding="utf-8")
        results.append(
            TextbookExportResult(chapter=chapter, output_path=target, chunk_count=len(chunks))
        )
    return results


class TextbookRenderer:
    def __init__(
        self,
        structured_dir: Path,
        figure_library: Path | None = None,
        output_dir: Path | None = None,
        book_id: str | None = None,
    ):
        self.structured_dir = structured_dir
        self.figure_library_path = figure_library
        self.figure_library_root = figure_library.parent if figure_library else structured_dir
        self.output_dir = output_dir
        self.book_id_override = str(book_id or "").strip()
        self.active_book_id: str | None = None
        self.formula_map: dict[str, dict[str, Any]] = {}
        self.formulas_by_canonical: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.figure_map: dict[tuple[str, str], dict[str, Any]] = {}
        self.figure_ids_by_chapter: dict[str, set[str]] = defaultdict(set)
        self.tables_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.tables_by_chapter_id: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        (
            self.examples_by_ref,
            self.examples_by_chapter_ref,
            self.examples_by_chapter_label,
        ) = self._load_example_maps()
        self.chapter_titles_by_source_file: dict[str, str] = {}
        self.raw_table_overrides: dict[str, str] = {}
        self.raw_table_replaced_ids: set[str] = set()
        self.raw_table_last_replacement_by_chapter: dict[str, str] = {}
        self.unowned_raw_tables_by_section: dict[str, list[str]] = defaultdict(list)
        self.embedded_formula_occurrences: dict[str, int] = defaultdict(int)

    def render_chapter(self, chapter: str, chunks: list[dict[str, Any]]) -> str:
        self.activate_book(self.book_id_override or book_id_from_chapter(chapter))
        self.raw_table_overrides = {}
        self.raw_table_replaced_ids = set()
        self.raw_table_last_replacement_by_chapter = {}
        self.unowned_raw_tables_by_section = defaultdict(list)
        self.embedded_formula_occurrences = defaultdict(int)
        chapter_label = render_chapter_label(chapter)
        chapter_title = self.chapter_title_for_render(chapter, chunks)
        lines = [
            f"# {render_chapter_heading(chapter_label, chapter_title)}",
            "",
        ]

        expanded_figures: set[str] = set()
        explicitly_placed_figures = explicit_figure_ids(chunks, self.examples_by_ref)
        section_keys = [self.table_sink_section_key(chunk) for chunk in chunks]
        last_chunk_index_by_section = {
            section_key: index for index, section_key in enumerate(section_keys)
        }
        sink_tables_by_section = self.sink_tables_by_section(chapter, chunks, section_keys)
        source_index_by_table_id = self.source_index_by_table_id(chapter, chunks)
        chunks = self.prepare_chunks_for_render(
            chapter=chapter,
            chunks=chunks,
            source_index_by_table_id=source_index_by_table_id,
        )

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = str(chunk.get("id") or "")
            metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
            display_section = display_heading_for_chunk(
                chunk_id,
                metadata,
                document_title=self.document_title_for_chunk(metadata),
            )

            expanded_assets: set[str] = set()
            chunk_lines: list[str] = []
            for block in chunk.get("blocks", []):
                if not isinstance(block, dict):
                    continue
                block_type = str(block.get("type") or "discussion")
                content = str(block.get("content") or "")
                rendered = self.process_content(
                    content=content,
                    expanded_assets=expanded_assets,
                    current_chapter=chapter,
                    current_chunk_id=chunk_id,
                    force_expand_tables=block_type == "table",
                    expanded_figures=expanded_figures,
                    explicitly_placed_figures=explicitly_placed_figures,
                )
                if not rendered.strip():
                    continue

                if block_type != "discussion":
                    chunk_lines.append(f"**[{block_type_label(block_type)}]**")
                    chunk_lines.append("")
                chunk_lines.append(rendered)
                chunk_lines.append("")

            heading_only = (
                str(chunk.get("node_kind") or "").strip().lower() == "heading"
                and bool(chunk.get("allow_empty"))
            )
            if not chunk_lines and not heading_only:
                continue
            lines.append(f"## {chunk_id} · {display_section}")
            lines.append("")
            if chunk_lines:
                lines.extend(chunk_lines)
            section_key = section_keys[chunk_index] if chunk_index < len(section_keys) else ""
            if last_chunk_index_by_section.get(section_key) == chunk_index:
                for table_id in sink_tables_by_section.get(section_key, []):
                    table_block = self.render_table_block(table_id, chapter).strip()
                    if table_block:
                        lines.append(table_block)
                        lines.append("")
                for raw_table in self.unowned_raw_tables_by_section.get(section_key, []):
                    table_block = self.render_unowned_raw_table_block(raw_table).strip()
                    if table_block:
                        lines.append(table_block)
                        lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def prepare_chunks_for_render(
        self,
        chapter: str,
        chunks: list[dict[str, Any]],
        source_index_by_table_id: dict[str, int],
    ) -> list[dict[str, Any]]:
        rendered_chunks: list[dict[str, Any]] = []
        for chunk_index, chunk in enumerate(chunks):
            chunk_id = str(chunk.get("id") or "")
            rendered_chunk = dict(chunk)
            rendered_blocks: list[dict[str, Any]] = []
            for block in chunk.get("blocks", []):
                if not isinstance(block, dict):
                    continue
                rendered_block = dict(block)
                content = str(rendered_block.get("content") or "")
                rendered_block["content"] = self.replace_owned_raw_tables(
                    content=content,
                    chapter=chapter,
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    section_key=self.table_sink_section_key(chunk),
                    source_index_by_table_id=source_index_by_table_id,
                )
                rendered_blocks.append(rendered_block)
            rendered_chunk["blocks"] = rendered_blocks
            rendered_chunks.append(rendered_chunk)
        return rendered_chunks

    def table_sink_section_key(self, chunk: dict[str, Any]) -> str:
        chunk_id = str(chunk.get("id") or "")
        metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
        heading_path = metadata.get("heading_path") if isinstance(metadata.get("heading_path"), list) else []
        path_parts = [str(item).strip() for item in heading_path if str(item).strip()]
        if path_parts:
            return "\n".join(path_parts)
        for key in ("section_level_1", "section_level_2", "display_heading", "section"):
            value = str(metadata.get(key) or "").strip()
            if value:
                return value
        return chunk_id

    def sink_tables_by_section(
        self,
        chapter: str,
        chunks: list[dict[str, Any]],
        section_keys: list[str],
    ) -> dict[str, list[str]]:
        chapter_key = normalize_chapter_id(chapter)
        if not chunks:
            return {}

        chunk_key_by_id: dict[str, str] = {}
        section_key_by_title: dict[str, str] = {}
        for chunk, section_key in zip(chunks, section_keys):
            chunk_id = str(chunk.get("id") or "").strip()
            if chunk_id:
                chunk_key_by_id[chunk_id] = section_key
            metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
            for key in ("section", "display_heading", "section_level_1", "section_level_2"):
                title_key = normalize_match_text(str(metadata.get(key) or ""))
                if title_key:
                    section_key_by_title.setdefault(title_key, section_key)

        fallback_section_key = section_keys[-1] if section_keys else ""
        grouped: dict[str, list[str]] = defaultdict(list)
        seen: set[tuple[str, str]] = set()
        table_items: list[tuple[str, dict[str, Any]]] = []
        for (table_chapter, table_id), matches in self.tables_by_chapter_id.items():
            if table_chapter != chapter_key:
                continue
            for table in matches:
                resolved_id = clean_ref_id(table.get("id") or table_id)
                if resolved_id:
                    table_items.append((resolved_id, table))

        for table_id, table in sorted(table_items, key=lambda item: natural_key(item[0])):
            if self.table_entry_is_inline(table, table_id):
                continue
            source = table.get("source") if isinstance(table.get("source"), dict) else {}
            unit_id = str(source.get("unit_id") or "").strip()
            section_key = chunk_key_by_id.get(unit_id)
            if not section_key:
                subsection_key = normalize_match_text(str(source.get("subsection") or ""))
                section_key = section_key_by_title.get(subsection_key)
            if not section_key:
                section_key = fallback_section_key
            dedupe_key = (section_key, table_id)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            grouped[section_key].append(table_id)
        return grouped

    def source_index_by_table_id(
        self,
        chapter: str,
        chunks: list[dict[str, Any]],
    ) -> dict[str, int]:
        chapter_key = normalize_chapter_id(chapter)
        chunk_index_by_id = {
            str(chunk.get("id") or "").strip(): index
            for index, chunk in enumerate(chunks)
            if str(chunk.get("id") or "").strip()
        }
        result: dict[str, int] = {}
        for (table_chapter, table_id), matches in self.tables_by_chapter_id.items():
            if table_chapter != chapter_key:
                continue
            for table in matches:
                resolved_id = clean_ref_id(table.get("id") or table_id)
                if not resolved_id or self.table_entry_is_inline(table, resolved_id):
                    continue
                source = table.get("source") if isinstance(table.get("source"), dict) else {}
                unit_id = str(source.get("unit_id") or "").strip()
                if unit_id in chunk_index_by_id:
                    result.setdefault(resolved_id, chunk_index_by_id[unit_id])
        return result

    def owned_non_inline_table_ids(self, chapter: str, chunk_id: str) -> list[str]:
        chapter_key = normalize_chapter_id(chapter)
        result: list[str] = []
        seen: set[str] = set()
        for (table_chapter, table_id), matches in self.tables_by_chapter_id.items():
            if table_chapter != chapter_key:
                continue
            for table in matches:
                resolved_id = clean_ref_id(table.get("id") or table_id)
                if not resolved_id or resolved_id in seen:
                    continue
                if self.table_entry_is_inline(table, resolved_id):
                    continue
                replacement_key = f"{chapter_key}:{resolved_id}"
                if replacement_key in self.raw_table_replaced_ids:
                    continue
                source = table.get("source") if isinstance(table.get("source"), dict) else {}
                if str(source.get("unit_id") or "").strip() != chunk_id:
                    continue
                seen.add(resolved_id)
                result.append(resolved_id)
        return sorted(result, key=natural_key)

    def replace_owned_raw_tables(
        self,
        content: str,
        chapter: str,
        chunk_id: str,
        chunk_index: int = 0,
        section_key: str = "",
        source_index_by_table_id: dict[str, int] | None = None,
    ) -> str:
        if "<table" not in content.lower():
            return content
        chapter_key = normalize_chapter_id(chapter)
        source_index_by_table_id = source_index_by_table_id or {}
        table_ids = self.owned_non_inline_table_ids(chapter, chunk_id)
        table_iter = iter(table_ids)

        def replace(match: re.Match[str]) -> str:
            table_id: str | None = None
            try:
                table_id = next(table_iter)
            except StopIteration:
                table_id = self.raw_table_id_from_nearby_reference(
                    content=content,
                    table_start=match.start(),
                    chapter=chapter,
                )
                if not table_id:
                    table_id = self.next_unfilled_table_id(
                        chapter=chapter,
                        chunk_index=chunk_index,
                        source_index_by_table_id=source_index_by_table_id,
                    )
                if not table_id:
                    table_id = self.previous_unfilled_table_id(
                        chapter=chapter,
                        chunk_index=chunk_index,
                        source_index_by_table_id=source_index_by_table_id,
                    )
                if not table_id and not self.raw_table_looks_inline_example(content, match.start()):
                    table_id = self.raw_table_last_replacement_by_chapter.get(chapter_key)
                if not table_id:
                    if not self.raw_table_looks_inline_example(content, match.start()) and section_key:
                        self.unowned_raw_tables_by_section[section_key].append(match.group(0).strip())
                        return ""
                    return match.group(0)
            raw_table = match.group(0).strip()
            if raw_table:
                self.record_raw_table_override(chapter_key, table_id, raw_table)
                self.raw_table_last_replacement_by_chapter[chapter_key] = clean_ref_id(table_id)
            if clean_ref_id(table_id) in table_ids:
                return f"*[See Table {clean_ref_id(table_id)} at the end of this section.]*"
            return ""

        return HTML_TABLE_RE.sub(replace, content)

    def record_raw_table_override(self, chapter_key: str, table_id: str, raw_table: str) -> None:
        replacement_key = f"{chapter_key}:{clean_ref_id(table_id)}"
        existing = self.raw_table_overrides.get(replacement_key)
        if existing and raw_table not in existing:
            self.raw_table_overrides[replacement_key] = f"{existing}\n{raw_table}"
        elif not existing:
            self.raw_table_overrides[replacement_key] = raw_table
        self.raw_table_replaced_ids.add(replacement_key)

    def raw_table_id_from_nearby_reference(
        self,
        content: str,
        table_start: int,
        chapter: str,
    ) -> str | None:
        nearby = content[max(0, table_start - 1200) : table_start]
        matches = list(PLACEHOLDER_RE.finditer(nearby))
        for match in reversed(matches):
            tag = match.group("tag").upper()
            table_id = clean_ref_id(match.group("id"))
            if tag not in {"SEE_TABLE", "TABLE"}:
                continue
            if self.table_is_inline(table_id, chapter):
                continue
            replacement_key = f"{normalize_chapter_id(chapter)}:{table_id}"
            if replacement_key in self.raw_table_replaced_ids:
                continue
            return table_id
        return None

    def previous_unfilled_table_id(
        self,
        chapter: str,
        chunk_index: int,
        source_index_by_table_id: dict[str, int],
    ) -> str | None:
        chapter_key = normalize_chapter_id(chapter)
        candidates = [
            (source_index, table_id)
            for table_id, source_index in source_index_by_table_id.items()
            if source_index < chunk_index
            and f"{chapter_key}:{clean_ref_id(table_id)}" not in self.raw_table_replaced_ids
        ]
        if not candidates:
            return None
        _, table_id = sorted(candidates, key=lambda item: (item[0], natural_key(item[1])))[-1]
        return table_id

    def next_unfilled_table_id(
        self,
        chapter: str,
        chunk_index: int,
        source_index_by_table_id: dict[str, int],
    ) -> str | None:
        chapter_key = normalize_chapter_id(chapter)
        candidates = [
            (source_index, table_id)
            for table_id, source_index in source_index_by_table_id.items()
            if source_index == chunk_index + 1
            and f"{chapter_key}:{clean_ref_id(table_id)}" not in self.raw_table_replaced_ids
        ]
        if not candidates:
            return None
        _, table_id = sorted(candidates, key=lambda item: (item[0], natural_key(item[1])))[0]
        return table_id

    def raw_table_looks_inline_example(self, content: str, table_start: int) -> bool:
        nearby = content[max(0, table_start - 1600) : table_start]
        if re.search(r"\bExample\s+\d+\.", nearby, re.IGNORECASE):
            return True
        if re.search(r"\bExample\b", nearby[-240:]):
            return True
        lower = nearby.lower()
        return any(
            cue in lower
            for cue in (
                "conditional probabilities",
                "following hypothetical",
                "consider the following hypothetical",
                "using f ratios",
                "following table shows how",
            )
        )

    def document_title_for_chunk(self, metadata: dict[str, Any]) -> str:
        source_file = str(metadata.get("source_file") or "").strip()
        if not source_file:
            return ""
        if source_file not in self.chapter_titles_by_source_file:
            self.chapter_titles_by_source_file[source_file] = extract_tex_title(source_file)
        return self.chapter_titles_by_source_file[source_file]

    def chapter_title_for_render(self, chapter: str, chunks: list[dict[str, Any]]) -> str:
        chapter_label = render_chapter_label(chapter)
        metadata_items = [
            chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
            for chunk in chunks
        ]

        candidates: list[str] = []
        for metadata in metadata_items:
            candidates.append(str(metadata.get("chapter_title") or ""))
        for metadata in metadata_items:
            candidates.append(self.document_title_for_chunk(metadata))
        if metadata_items:
            first_metadata = metadata_items[0]
            candidates.extend(
                str(first_metadata.get(key) or "")
                for key in ("section_level_1", "display_heading", "section")
            )

        for candidate in candidates:
            title = normalize_chapter_title_for_heading(candidate, chapter_label)
            if title:
                return title
        return ""

    def process_content(
        self,
        content: str,
        expanded_assets: set[str],
        current_chapter: str | None,
        *,
        current_chunk_id: str | None = None,
        force_expand_tables: bool = False,
        inline_table_scope: str | None = None,
        expanded_figures: set[str] | None = None,
        explicitly_placed_figures: set[str] | None = None,
    ) -> str:
        content = normalize_latex_for_katex(content)
        content = self.render_embedded_book_formulas(content, current_chapter, current_chunk_id)
        content = canonicalize_display_math(content)
        protected_references: list[str] = []

        def protect_reference(match: re.Match[str]) -> str:
            token = f"@@TEXTBOOK_REFERENCE_{len(protected_references)}@@"
            tag = match.group("tag").upper()
            ref = clean_ref_id(match.group("id"))
            if tag == "SEE_TABLE":
                protected_references.append(self.render_table_reference(ref, current_chapter))
            elif tag == "SEE_FORMULA":
                protected_references.append(f"*(See Equation {ref}.)*")
            elif tag == "SEE_FIGURE":
                protected_references.append(f"*(See Figure {ref}.)*")
            elif tag == "SEE_EXAMPLE":
                protected_references.append(f"*(See Example {ref}.)*")
            else:
                protected_references.append(f"*({ref})*")
            return token

        content = PLACEHOLDER_RE.sub(
            lambda match: protect_reference(match)
            if match.group("tag").upper().startswith("SEE_")
            else match.group(0),
            content,
        )
        figure_assets = expanded_figures if expanded_figures is not None else expanded_assets

        parts: list[str] = []
        last_end = 0
        for match in PLACEHOLDER_RE.finditer(content):
            tag = match.group("tag").upper()
            raw_id = match.group("id").strip()
            before = content[last_end : match.start()].strip()
            if before:
                parts.append(before)

            if tag == "TABLE" and self.numbered_table_cross_owner(raw_id, current_chapter, current_chunk_id) and not force_expand_tables:
                parts.append(self.render_table_reference(raw_id, current_chapter))
                last_end = match.end()
                continue
            if tag == "TABLE" and not self.table_is_inline(raw_id, current_chapter):
                parts.append(self.render_table_reference(raw_id, current_chapter))
                last_end = match.end()
                continue
            asset_key = self.asset_key(tag, raw_id, current_chapter)
            if tag == "TABLE" and inline_table_scope and self.table_is_inline(raw_id, current_chapter):
                asset_key = f"{asset_key}:{inline_table_scope}"

            if tag == "FIGURE":
                if asset_key in figure_assets:
                    parts.append(self.render_repeat_reference(tag, raw_id))
                else:
                    expanded_assets.add(asset_key)
                    figure_assets.add(asset_key)
                    parts.append(self.render_figure_block(raw_id, current_chapter))
            elif asset_key in expanded_assets:
                parts.append(self.render_repeat_reference(tag, raw_id))
            else:
                expanded_assets.add(asset_key)
                if tag in {"SEE_FORMULA", "FORMULA"}:
                    parts.append(self.render_formula_block(raw_id))
                elif tag == "TABLE":
                    parts.append(self.render_table_block(raw_id, current_chapter))
                elif tag in {"SEE_EXAMPLE", "EXAMPLE"}:
                    parts.append(
                        self.render_example_block(
                            raw_id,
                            expanded_assets,
                            current_chapter,
                            figure_assets,
                            explicitly_placed_figures or set(),
                        )
                    )
                else:
                    parts.append(match.group(0))
            last_end = match.end()

        remaining = content[last_end:].strip()
        if remaining:
            parts.append(remaining)
        rendered = "\n\n".join(parts) if parts else content
        for index, reference in enumerate(protected_references):
            rendered = rendered.replace(f"@@TEXTBOOK_REFERENCE_{index}@@", reference)
        rendered = self.replace_inline_figure_references(rendered)
        return self.append_auto_figure_blocks(
            rendered,
            figure_assets,
            current_chapter,
            explicitly_placed_figures or set(),
        )

    def table_is_inline(self, table_id: str, current_chapter: str | None) -> bool:
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return False
        return self.table_entry_is_inline(table, table_id)

    def table_entry_is_inline(self, table: dict[str, Any], table_id: str) -> bool:
        table_type = str(table.get("table_type") or "").strip().lower()
        return table_type == "inline" or clean_ref_id(table.get("id") or table_id).lower().startswith("inline_")

    def table_owned_by_chunk(
        self,
        table_id: str,
        current_chapter: str | None,
        current_chunk_id: str | None,
    ) -> bool:
        if not current_chunk_id:
            return False
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return False
        source = table.get("source") if isinstance(table.get("source"), dict) else {}
        return str(source.get("unit_id") or "").strip() == str(current_chunk_id).strip()

    def numbered_table_cross_owner(
        self,
        table_id: str,
        current_chapter: str | None,
        current_chunk_id: str | None,
    ) -> bool:
        if not current_chunk_id:
            return False
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return False
        table_type = str(table.get("table_type") or "").strip().lower()
        if table_type and table_type != "numbered":
            return False
        return not self.table_owned_by_chunk(table_id, current_chapter, current_chunk_id)

    def render_formula_block(self, formula_id: str) -> str:
        formula = self.formula_map.get(clean_ref_id(formula_id))
        if not formula:
            return f"> **[UNRESOLVED FORMULA: {formula_id}]**\n"

        source = formula.get("source") if isinstance(formula.get("source"), dict) else {}
        label = str(formula.get("label_format") or f"({formula_id})")
        unit_id = str(source.get("unit_id") or "")
        subsection = str(source.get("subsection") or "")
        latex = str(formula.get("latex") or "")
        latex = normalize_latex_math(latex)
        if formula.get("book") and str(formula.get("render_mode") or "") in {
            "numbered_equation",
            "display_equation",
            "multi_numbered_equation",
        }:
            return self.render_book_formula(formula, latex)
        return "\n".join(
            [
                f"> **Formula {label}** · `{clean_ref_id(formula_id)}` · source: `{unit_id}` · {subsection}",
                ">",
                "> $$",
                f"> {latex}",
                "> $$",
                "",
            ]
        )

    def render_book_formula(self, formula: dict[str, Any], fallback_latex: str | None = None) -> str:
        """Render book-scoped equations as textbook math, never as debug cards."""
        mode = str(formula.get("render_mode") or "")
        if mode == "multi_numbered_equation":
            parts = formula.get("render_parts") if isinstance(formula.get("render_parts"), list) else []
            rendered = []
            for part in parts:
                if not isinstance(part, dict):
                    continue
                latex = normalize_latex_math(str(part.get("latex") or ""))
                number = str(part.get("equation_number") or "")
                if latex and number:
                    rendered.append(f"$$\n{latex}\n\\tag{{{number}}}\n$$")
            if rendered:
                return "\n\n".join(rendered) + "\n"
        latex = normalize_latex_math(str(formula.get("latex") or fallback_latex or ""))
        number = str(formula.get("equation_number") or "")
        if number:
            return f"$$\n{latex}\n\\tag{{{number}}}\n$$\n"
        return f"$$\n{latex}\n$$\n"

    def render_table_block(self, table_id: str, current_chapter: str | None) -> str:
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return f"> **[UNRESOLVED TABLE: {table_id}]** - possibly cross-chapter reference\n"

        source = table.get("source") if isinstance(table.get("source"), dict) else {}
        label = str(table.get("label_format") or f"Table {table_id}")
        title = normalize_latex_for_katex(str(table.get("title") or label))
        page = source.get("page", "?")
        unit_id = str(source.get("unit_id") or "?")
        rows = normalize_table_rows(table.get("rows"))
        resolved_id = clean_ref_id(table.get("id") or table_id)
        override_key = f"{normalize_chapter_id(current_chapter or source.get('chapter') or '')}:{resolved_id}"
        html = inline_table_math(str(table.get("html") or self.raw_table_overrides.get(override_key) or ""))
        markdown_body = normalize_latex_for_katex(str(table.get("markdown_body") or "").strip())
        notes = table.get("notes") if isinstance(table.get("notes"), list) else []
        table_type = str(table.get("table_type") or "").strip().lower()

        lines = [
            f"> **{label}** · `{resolved_id}` · page {page} · source: `{unit_id}`",
            f"> {title}",
            ">",
        ]

        parts = table.get("parts") if isinstance(table.get("parts"), list) else []
        if parts:
            for index, part in enumerate(parts):
                if not isinstance(part, dict):
                    continue
                if index:
                    part_page = part.get("page", "?")
                    lines.extend([">", f"> *(continued, page {part_page})*", ">"])
                self.append_table_payload(
                    lines,
                    rows=normalize_table_rows(part.get("rows")),
                    html=inline_table_math(str(part.get("html") or "")),
                    notes=part.get("notes") if isinstance(part.get("notes"), list) else [],
                    markdown_body=normalize_latex_for_katex(str(part.get("markdown_body") or "").strip()),
                    table_type=table_type,
                )
            lines.append("")
            return "\n".join(lines)

        self.append_table_payload(
            lines,
            rows=rows,
            html=html,
            notes=notes,
            markdown_body=markdown_body,
            table_type=table_type,
        )
        lines.append("")
        return "\n".join(lines)

    def append_table_payload(
        self,
        lines: list[str],
        *,
        rows: list[list[str]],
        html: str,
        notes: list[dict[str, Any]],
        markdown_body: str,
        table_type: str,
    ) -> None:
        if rows:
            column_count = len(rows[0])
            consistent = column_count > 0 and all(len(row) == column_count for row in rows)
            if consistent:
                render_cell = self.markdown_asset_table_cell if table_type == "formula_table" else markdown_table_cell
                if table_type == "list_table" or column_count == 1:
                    for row in rows:
                        cell = render_cell(row[0]).strip()
                        if cell:
                            lines.append(f"> {cell}")
                    self.append_table_notes(lines, notes)
                    self.append_table_markdown_body(lines, markdown_body)
                    return
                lines.append(("> " + " | ".join(render_cell(cell) for cell in rows[0])).rstrip())
                lines.append(("> " + " | ".join("---" for _ in range(column_count))).rstrip())
                for row in rows[1:]:
                    lines.append(("> " + " | ".join(render_cell(cell) for cell in row)).rstrip())
                self.append_table_notes(lines, notes)
                self.append_table_markdown_body(lines, markdown_body)
                return
        if html:
            for line in html.splitlines() or [html]:
                lines.append(f"> {line}")
            self.append_table_notes(lines, notes)
            self.append_table_markdown_body(lines, markdown_body)
            return
        lines.append("> [Table data not available]")
        self.append_table_notes(lines, notes)
        self.append_table_markdown_body(lines, markdown_body)

    def append_table_notes(self, lines: list[str], notes: list[dict[str, Any]]) -> None:
        rendered = []
        for note in notes:
            if not isinstance(note, dict):
                continue
            marker = str(note.get("marker") or "").strip()
            content = normalize_latex_for_katex(str(note.get("content") or "").strip())
            if content:
                rendered.append(f"{marker} {content}".strip())
        if not rendered:
            return
        lines.append(">")
        for note in rendered:
            lines.append(f"> {note}")

    def append_table_markdown_body(self, lines: list[str], markdown_body: str) -> None:
        if not markdown_body:
            return
        # Some legacy records store a full Markdown copy of the same table.
        # Rows/HTML are authoritative; only append body text that is not a
        # duplicate table representation.
        body_lines = [line.strip() for line in markdown_body.splitlines() if line.strip()]
        if body_lines and sum("|" in line for line in body_lines) >= 2:
            return
        lines.append(">")
        for line in markdown_body.splitlines():
            rendered = self.render_inline_asset_references(line)
            lines.append(f"> {rendered}" if rendered else ">")

    def markdown_asset_table_cell(self, value: str) -> str:
        return markdown_table_cell(self.render_inline_asset_references(str(value or "")))

    def render_inline_asset_references(self, value: str) -> str:
        def repl(match: re.Match[str]) -> str:
            tag = match.group("tag").upper()
            raw_id = match.group("id").strip()
            if tag in {"SEE_FORMULA", "FORMULA"}:
                formula = self.formula_map.get(clean_ref_id(raw_id))
                if not formula:
                    return match.group(0)
                latex = normalize_latex_math(str(formula.get("latex") or ""))
                return f"$${latex}$$"
            return match.group(0)

        return PLACEHOLDER_RE.sub(repl, value)

    def render_table_reference(self, table_id: str, current_chapter: str | None) -> str:
        ref = clean_ref_id(table_id)
        # Audited textbooks sink each complete table to the end of its owning
        # section. Preserve the semantic position as readable prose.
        return f"*[See Table {ref} at the end of this section.]*"

    def render_unowned_raw_table_block(self, raw_table: str) -> str:
        lines = [
            "> **Unnumbered table**",
            ">",
        ]
        for line in raw_table.splitlines() or [raw_table]:
            lines.append(f"> {line}")
        lines.append("")
        return "\n".join(lines)

    def render_figure_block(self, figure_id: str, current_chapter: str | None) -> str:
        figure = self.resolve_figure(figure_id, current_chapter)
        if not figure:
            return f"> **[UNRESOLVED FIGURE: {figure_id}]**\n"

        figure_ref = str(figure.get("display_ref") or clean_ref_id(figure.get("id") or figure_id))
        caption = normalize_latex_for_katex(str(figure.get("caption") or f"Figure {figure_ref}"))
        asset_path = str(figure.get("asset_path") or "").strip()
        asset_target = self.figure_library_root / asset_path if asset_path else None
        image_path = self.markdown_asset_path(asset_target) if asset_target else ""
        page = figure.get("page", "?")
        chapter = str(figure.get("chapter") or current_chapter or "").strip()
        if not chapter:
            chapter = normalize_chapter_id(chapter_from_numbered_ref(figure_ref) or "")
        lines = [
            f"> **Figure {figure_ref}** · page {page} · source: `{chapter}`",
        ]
        if image_path:
            lines.extend([">", f"> ![Figure {figure_ref}]({image_path})"])
        lines.extend([">", f"> {caption}", ""])
        return "\n".join(lines)

    def markdown_asset_path(self, asset_target: Path) -> str:
        if self.output_dir is None:
            return str(asset_target).replace("\\", "/")
        if asset_target.exists():
            try:
                relative = asset_target.resolve().relative_to(self.figure_library_root.resolve())
            except ValueError:
                relative = Path(asset_target.name)
            output_target = self.output_dir / relative
            output_target.parent.mkdir(parents=True, exist_ok=True)
            if asset_target.resolve() != output_target.resolve(strict=False):
                shutil.copy2(asset_target, output_target)
            return relative.as_posix()
        relative = os.path.relpath(asset_target.resolve(strict=False), start=self.output_dir.resolve())
        return relative.replace("\\", "/")

    def render_figure_reference(self, figure_id: str) -> str:
        return f"Figure {clean_ref_id(figure_id)}"

    def replace_inline_figure_references(self, value: str) -> str:
        return re.sub(
            r"\[\[SEE_FIGURE:(?P<id>[^\]]+)\]\]",
            lambda match: self.render_figure_reference(match.group("id").strip()),
            value,
            flags=re.IGNORECASE,
        )

    def append_auto_figure_blocks(
        self,
        rendered: str,
        expanded_figures: set[str],
        current_chapter: str | None,
        explicitly_placed_figures: set[str],
    ) -> str:
        figure_ids = self.figure_refs_in_text(rendered, current_chapter)
        additions: list[str] = []
        for figure_id in figure_ids:
            if figure_id in explicitly_placed_figures:
                continue
            asset_key = self.asset_key("FIGURE", figure_id, current_chapter)
            if asset_key in expanded_figures:
                continue
            expanded_figures.add(asset_key)
            additions.append(self.render_figure_block(figure_id, current_chapter).strip())
        if not additions:
            return rendered
        return "\n\n".join([rendered, *additions])

    def figure_refs_in_text(self, value: str, current_chapter: str | None) -> list[str]:
        chapter = normalize_chapter_id(current_chapter or "")
        known_ids = self.figure_ids_by_chapter.get(chapter, set())
        if not chapter or not known_ids:
            return []

        found: list[str] = []
        seen: set[str] = set()

        def add(raw_id: str) -> None:
            figure_id = self.base_figure_id(raw_id, known_ids)
            if figure_id not in known_ids or figure_id in seen:
                return
            figure = self.resolve_figure(figure_id, chapter)
            figure_chapter = normalize_chapter_id((figure or {}).get("chapter") or "")
            if figure_chapter != chapter:
                return
            seen.add(figure_id)
            found.append(figure_id)

        for match in FIGURE_TEXT_REF_RE.finditer(value or ""):
            add(match.group("id"))
            tail = value[match.end() : match.end() + 120]
            for candidate in sorted(known_ids, key=natural_key):
                if candidate in seen:
                    continue
                if re.search(rf"(?:,|and)\s+{re.escape(candidate)}\b", tail, flags=re.IGNORECASE):
                    add(candidate)
        return found

    def base_figure_id(self, value: str, known_ids: set[str]) -> str:
        figure_id = clean_ref_id(value).strip(".,;:()[]")
        if figure_id in known_ids:
            return figure_id
        match = re.fullmatch(r"((?:A\d+|\d+)\.\d+)[A-Za-z]", figure_id)
        if match and match.group(1) in known_ids:
            return match.group(1)
        return figure_id

    def render_example_block(
        self,
        example_ref: str,
        expanded_assets: set[str],
        current_chapter: str | None,
        expanded_figures: set[str] | None = None,
        explicitly_placed_figures: set[str] | None = None,
    ) -> str:
        example = self.resolve_example(example_ref, current_chapter)
        if not example:
            return f"> **[UNRESOLVED EXAMPLE: {example_ref}]**\n"

        example_chapter = normalize_chapter_id(example.get("chapter") or current_chapter or "")
        label = str(example.get("label") or f"Example {example_ref}")
        source_file = str(example.get("source_file") or "")
        replacement = example.get("replacement") if isinstance(example.get("replacement"), dict) else {}
        source_span = replacement.get("source_block_span") if isinstance(replacement.get("source_block_span"), list) else []
        if len(source_span) == 2:
            start, end = source_span
        else:
            start = example.get("start_block_index", "?")
            end = example.get("end_block_index", "?")
        content = str(example.get("content_markdown") or example.get("content_plain") or "[No content]")
        content = self.process_content(
            content,
            expanded_assets,
            example_chapter,
            inline_table_scope=f"example:{clean_ref_id(example_ref)}",
            expanded_figures=expanded_figures,
            explicitly_placed_figures=explicitly_placed_figures or set(),
        )

        lines = [
            f"> **{label}** · ref: `{clean_ref_id(example_ref)}` · source: `{source_file}` · blocks {start}–{end}",
            ">",
        ]
        for line in content.split("\n"):
            lines.append(f"> {line}")
        lines.append("")
        return "\n".join(lines)

    def resolve_table(self, table_id: str, current_chapter: str | None) -> dict[str, Any] | None:
        table_key = clean_ref_id(table_id)
        chapter = normalize_chapter_id(current_chapter or "")
        if chapter:
            chapter_matches = self.tables_by_chapter_id.get((chapter, table_key))
            if chapter_matches:
                return chapter_matches[0]

        numbered_chapter = chapter_from_numbered_ref(table_key)
        if numbered_chapter:
            chapter_matches = self.tables_by_chapter_id.get((numbered_chapter, table_key))
            if chapter_matches:
                return chapter_matches[0]

        matches = self.tables_by_id.get(table_key)
        return matches[0] if matches else None

    def resolve_example(self, example_ref: str, current_chapter: str | None) -> dict[str, Any] | None:
        ref = clean_ref_id(example_ref)
        chapters = [
            normalize_chapter_id(current_chapter or ""),
            chapter_from_numbered_ref(ref) or "",
        ]
        for chapter in chapters:
            if not chapter:
                continue
            match = self.examples_by_chapter_ref.get((chapter, ref))
            if match:
                return match
            label_match = self.examples_by_chapter_label.get((chapter, f"Example {ref.split('@')[0]}"))
            if label_match:
                return label_match
        return self.examples_by_ref.get(ref)

    def resolve_figure(self, figure_ref: str, current_chapter: str | None) -> dict[str, Any] | None:
        ref = clean_ref_id(figure_ref)
        chapter = normalize_chapter_id(current_chapter or chapter_from_numbered_ref(ref) or "")
        if chapter:
            match = self.figure_map.get((chapter, ref))
            if match:
                return match
        return self.figure_map.get(("", ref))

    def asset_key(self, tag: str, raw_id: str, current_chapter: str | None) -> str:
        ref = clean_ref_id(raw_id)
        if tag == "TABLE":
            table = self.resolve_table(ref, current_chapter)
            source = table.get("source") if table and isinstance(table.get("source"), dict) else {}
            chapter = normalize_chapter_id(source.get("chapter") or current_chapter or "")
            return f"{chapter}:table:{ref}"
        if tag in {"SEE_EXAMPLE", "EXAMPLE"}:
            example = self.resolve_example(ref, current_chapter)
            chapter = normalize_chapter_id(
                (example or {}).get("chapter") or current_chapter or chapter_from_numbered_ref(ref) or ""
            )
            return f"{chapter}:example:{ref}"
        if tag in {"SEE_FIGURE", "FIGURE"}:
            figure = self.resolve_figure(ref, current_chapter)
            chapter = normalize_chapter_id(
                (figure or {}).get("chapter") or current_chapter or chapter_from_numbered_ref(ref) or ""
            )
            return f"{chapter}:figure:{ref}"
        if tag in {"SEE_FORMULA", "FORMULA"}:
            return f"formula:{ref}"
        return f"{tag.lower()}:{ref}"

    def render_repeat_reference(self, tag: str, raw_id: str) -> str:
        ref = clean_ref_id(raw_id)
        if tag in {"SEE_FORMULA", "FORMULA"}:
            return f"*({ref})*"
        if tag in {"SEE_TABLE", "TABLE"}:
            return f"*[See Table {ref} at the end of this section.]*"
        if tag in {"SEE_EXAMPLE", "EXAMPLE"}:
            return f"*[See Example {ref} in this section.]*"
        if tag in {"SEE_FIGURE", "FIGURE"}:
            return f"*[Figure {ref} - see above]*"
        return f"*[{ref} - see above]*"

    def activate_book(self, book_id: str | None) -> None:
        book = str(book_id or "").strip()
        if self.active_book_id is not None and book == self.active_book_id:
            return
        self.active_book_id = book
        self.formula_map = self._load_formula_map(book)
        self.formulas_by_canonical = defaultdict(list)
        for formula in self.formula_map.values():
            key = canonical_formula_latex(str(formula.get("latex") or ""))
            if key:
                self.formulas_by_canonical[key].append(formula)
        self.figure_map = self._load_figure_map(book)
        self.figure_ids_by_chapter = defaultdict(set)
        for chapter, figure_id in self.figure_map:
            if chapter:
                self.figure_ids_by_chapter[chapter].add(figure_id)
        self.tables_by_id, self.tables_by_chapter_id = self._load_table_maps(book)

    def render_embedded_book_formulas(
        self,
        content: str,
        current_chapter: str | None,
        current_chunk_id: str | None,
    ) -> str:
        if not self.active_book_id or not self.formulas_by_canonical:
            return content

        def replace(match: re.Match[str]) -> str:
            raw_latex = match.group(1)
            formula = self.resolve_embedded_formula(raw_latex, current_chapter, current_chunk_id)
            if not formula:
                return match.group(0)
            return self.render_book_formula(formula, raw_latex).strip()

        return re.sub(r"\$\$(.*?)\$\$", replace, content, flags=re.DOTALL)

    def resolve_embedded_formula(
        self,
        latex: str,
        current_chapter: str | None,
        current_chunk_id: str | None,
    ) -> dict[str, Any] | None:
        candidates = self.formulas_by_canonical.get(canonical_formula_latex(latex), [])
        candidates = [item for item in candidates if str(item.get("render_mode") or "") != "exclude"]
        if not candidates:
            return None
        chapter = normalize_chapter_id(current_chapter or "")

        def same_chapter(formula: dict[str, Any]) -> bool:
            source = formula.get("source") if isinstance(formula.get("source"), dict) else {}
            return normalize_chapter_id(source.get("chapter") or "") == chapter

        chapter_candidates = [formula for formula in candidates if same_chapter(formula)]
        ordered = sorted(
            chapter_candidates or candidates,
            key=lambda formula: clean_ref_id(formula.get("id") or ""),
        )
        key = canonical_formula_latex(latex)
        occurrence = self.embedded_formula_occurrences[key]
        self.embedded_formula_occurrences[key] += 1
        return ordered[occurrence] if occurrence < len(ordered) else None

    def _load_formula_map(self, book_id: str | None = None) -> dict[str, dict[str, Any]]:
        dedicated = self.structured_dir / f"{book_id}_formula_library.json" if book_id else None
        path = dedicated if dedicated and dedicated.exists() else self.structured_dir / "formula_library.json"
        library = read_json_if_exists(path, {"formulas": []})
        formulas = library.get("formulas") if isinstance(library, dict) else []
        return {
            clean_ref_id(formula.get("id")): formula
            for formula in formulas
            if isinstance(formula, dict) and clean_ref_id(formula.get("id"))
        }

    def _load_figure_map(self, book_id: str | None = None) -> dict[tuple[str, str], dict[str, Any]]:
        dedicated = self.structured_dir / f"{book_id}_figure_library.json" if book_id else None
        path = dedicated if dedicated and dedicated.exists() else (self.figure_library_path or (self.structured_dir / "figure_library.json"))
        library = read_json_if_exists(path, {"figures": {}})
        figures_payload = library.get("figures") if isinstance(library, dict) else {}
        if isinstance(figures_payload, dict):
            figures = [figure for figure in figures_payload.values() if isinstance(figure, dict)]
        elif isinstance(figures_payload, list):
            figures = [figure for figure in figures_payload if isinstance(figure, dict)]
        else:
            figures = []
        by_key: dict[tuple[str, str], dict[str, Any]] = {}
        for figure in figures:
            figure_id = clean_ref_id(figure.get("id"))
            if not figure_id:
                continue
            chapter = normalize_chapter_id(figure.get("chapter") or chapter_from_numbered_ref(figure_id) or "")
            by_key.setdefault((chapter, figure_id), figure)
            by_key.setdefault(("", figure_id), figure)
        return by_key

    def _load_table_maps(
        self,
        book_id: str | None = None,
    ) -> tuple[dict[str, list[dict[str, Any]]], dict[tuple[str, str], list[dict[str, Any]]]]:
        dedicated = self.structured_dir / f"{book_id}_table_library.json" if book_id else None
        path = dedicated if dedicated and dedicated.exists() else self.structured_dir / "table_library.json"
        library = read_json_if_exists(path, {"tables": []})
        tables = library.get("tables") if isinstance(library, dict) else []
        by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
        by_chapter: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for table in tables:
            if not isinstance(table, dict):
                continue
            table_id = clean_ref_id(table.get("id"))
            if not table_id:
                continue
            by_id[table_id].append(table)
            source = table.get("source") if isinstance(table.get("source"), dict) else {}
            chapter = normalize_chapter_id(source.get("chapter") or "")
            if chapter:
                by_chapter[(chapter, table_id)].append(table)
        return by_id, by_chapter

    def _load_example_maps(
        self,
    ) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
        library = read_json_if_exists(self.structured_dir / "example_library.json", {"examples": []})
        examples = library.get("examples") if isinstance(library, dict) else []
        by_ref: dict[str, dict[str, Any]] = {}
        by_chapter_ref: dict[tuple[str, str], dict[str, Any]] = {}
        by_chapter_label: dict[tuple[str, str], dict[str, Any]] = {}
        for example in examples:
            if not isinstance(example, dict):
                continue
            ref = clean_ref_id(example.get("example_ref") or example.get("example_id"))
            chapter = normalize_chapter_id(example.get("chapter") or chapter_from_numbered_ref(ref) or "")
            label = str(example.get("label") or "")
            if ref and ref not in by_ref:
                by_ref[ref] = example
            if chapter and ref and (chapter, ref) not in by_chapter_ref:
                by_chapter_ref[(chapter, ref)] = example
            if chapter and label and (chapter, label) not in by_chapter_label:
                by_chapter_label[(chapter, label)] = example
        return by_ref, by_chapter_ref, by_chapter_label


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return read_json(path)


def explicit_figure_ids(chunks: list[dict[str, Any]], examples_by_ref: dict[str, dict[str, Any]] | None = None) -> set[str]:
    figure_ids: set[str] = set()
    examples_by_ref = examples_by_ref or {}

    def add_from_content(content: str) -> None:
        for match in re.finditer(r"\[\[FIGURE:(?P<id>[^\]]+)\]\]", content, re.IGNORECASE):
            figure_id = clean_ref_id(match.group("id"))
            figure_ids.add(figure_id)
            base_match = re.fullmatch(r"((?:A\d+|\d+)\.\d+)[A-Za-z]", figure_id)
            if base_match:
                figure_ids.add(base_match.group(1))

    for chunk in chunks:
        blocks = chunk.get("blocks") if isinstance(chunk, dict) else []
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict):
                continue
            content = str(block.get("content") or "")
            add_from_content(content)
            for example_match in re.finditer(r"\[\[EXAMPLE:(?P<id>[^\]]+)\]\]", content, re.IGNORECASE):
                example = examples_by_ref.get(clean_ref_id(example_match.group("id")))
                if example:
                    add_from_content(str(example.get("content_markdown") or example.get("content_plain") or ""))
    return figure_ids


def default_figure_library_path(structured_dir: Path) -> Path | None:
    candidates = [
        structured_dir / "figure_library.json",
        structured_dir.parent / "figure_library.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def natural_key(value: Any) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", str(value))]


def normalize_match_text(value: Any) -> str:
    lowered = str(value or "").strip().lower()
    lowered = re.sub(r"[^\w]+", " ", lowered, flags=re.UNICODE)
    return re.sub(r"\s+", " ", lowered).strip()


def normalize_chapter_id(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if re.fullmatch(r"\d+", text):
        return f"chapter{text}"
    match = re.fullmatch(r"chapter\s*(\d+)", text)
    if match:
        return f"chapter{match.group(1)}"
    return text


def chapter_from_numbered_ref(value: str) -> str | None:
    match = NUMBERED_REF_RE.match(str(value or "").strip())
    return f"chapter{match.group(1)}" if match else None


def clean_ref_id(value: Any) -> str:
    return str(value or "").strip()


def chapter_sort_key(chapter: str) -> tuple[int, int, str]:
    normalized = normalize_chapter_id(chapter)
    unprefixed = re.sub(r"^[a-z]+_", "", normalized)
    match = re.fullmatch(r"chapter(\d+)", unprefixed)
    if match:
        return (0, int(match.group(1)), chapter)
    appendix_match = re.fullmatch(r"appendix(\d+)", unprefixed)
    if appendix_match:
        return (1, int(appendix_match.group(1)), chapter)
    return (9, 9999, chapter)


def chunk_file_sort_key(path: Path) -> tuple[int, int, str]:
    match = CHUNK_FILE_RE.fullmatch(path.name)
    if not match:
        return (9999, 9999, path.name)
    chapter = normalize_chapter_id(match.group(1))
    return (chapter_sort_key(chapter)[1], int(match.group(2)), path.name)


def render_chapter_label(chapter: str) -> str:
    normalized = normalize_chapter_id(chapter)
    unprefixed = re.sub(r"^[a-z]+_", "", normalized)
    match = re.fullmatch(r"chapter(\d+)", unprefixed)
    if match:
        return f"Chapter {match.group(1)}"
    appendix_match = re.fullmatch(r"appendix(\d+)", unprefixed)
    if appendix_match:
        return f"Appendix {appendix_match.group(1)}"
    return chapter


def render_chapter_heading(chapter_label: str, chapter_title: str = "") -> str:
    title = str(chapter_title or "").strip()
    if not title:
        return f"{chapter_label} Textbook Mapping"
    return f"{chapter_label} · {title}"


def normalize_chapter_title_for_heading(value: str, chapter_label: str = "") -> str:
    title = re.sub(r"\s+", " ", str(value or "")).strip()
    title = title.strip(" -–—")
    if not title:
        return ""

    if chapter_label:
        title = re.sub(
            rf"^{re.escape(chapter_label)}\s*[:.\-–—]\s*",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
    title = re.sub(r"^(?:Chapter|Appendix)\s+\d+\s*[:.\-–—]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\d+\s*:\s*", "", title).strip()
    title = re.sub(r"\s*:\s*Introduction\s*$", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\s*/\s*Introduction\s*$", "", title, flags=re.IGNORECASE).strip()

    if title and title.lower() not in {"introduction", "unknown authors"}:
        return title
    return ""


def display_heading_for_chunk(chunk_id: str, metadata: dict[str, Any], document_title: str = "") -> str:
    heading_path = metadata.get("heading_path") if isinstance(metadata.get("heading_path"), list) else []
    heading_path = [str(part).strip() for part in heading_path if str(part).strip()]
    heading_path = strip_placeholder_chapter_heading_path(chunk_id, heading_path, metadata)
    display = " / ".join(heading_path)
    display = display or str(metadata.get("display_heading") or metadata.get("section") or chunk_id)
    title = str(document_title or "").strip()
    if title and display and not heading_contains_title(display, title):
        first = str(heading_path[0]).strip() if heading_path else display
        if looks_like_chapter_subtitle(first):
            display = f"{title}{' ' if title.endswith(':') else ' / '}{display}"
    chapter_match = re.match(r"(?:[A-Za-z]+_)?chapter(\d+)_", chunk_id, flags=re.IGNORECASE)
    if chapter_match:
        prefix = f"Chapter {chapter_match.group(1)}: "
        if display.startswith(prefix):
            display = display[len(prefix) :]
    return display


def strip_placeholder_chapter_heading_path(
    chunk_id: str,
    heading_path: list[str],
    metadata: dict[str, Any] | None = None,
) -> list[str]:
    if len(heading_path) < 2:
        if len(heading_path) == 1 and looks_like_numbered_chapter_title(chunk_id, heading_path[0], metadata):
            return []
        return heading_path
    first = heading_path[0].strip()
    if not (
        looks_like_placeholder_chapter_intro(chunk_id, first)
        or looks_like_numbered_chapter_title(chunk_id, first, metadata)
    ):
        return heading_path
    return heading_path[1:]


def looks_like_placeholder_chapter_intro(chunk_id: str, heading: str) -> bool:
    chapter_match = re.match(r"(?:[A-Za-z]+_)?chapter(\d+)_", str(chunk_id or ""), flags=re.IGNORECASE)
    if not chapter_match:
        return False
    chapter_number = chapter_match.group(1)
    return bool(
        re.fullmatch(
            rf"(?:Chapter\s+)?0*{re.escape(chapter_number)}\s*:\s*Introduction",
            str(heading or "").strip(),
            flags=re.IGNORECASE,
        )
    )


def looks_like_numbered_chapter_title(
    chunk_id: str,
    heading: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    chapter_match = re.match(r"(?:[A-Za-z]+_)?chapter(\d+)_", str(chunk_id or ""), flags=re.IGNORECASE)
    if not chapter_match:
        return False
    value = str(heading or "").strip()
    match = re.fullmatch(rf"0*{re.escape(chapter_match.group(1))}\s*:\s*(?P<title>.+)", value)
    if not match:
        return False
    chapter_title = str((metadata or {}).get("chapter_title") or "").strip()
    if not chapter_title:
        return True
    return normalize_heading_compare(chapter_title) == normalize_heading_compare(match.group("title"))


def extract_tex_title(source_file: str) -> str:
    path = resolve_source_file_path(source_file)
    raw_title = extract_raw_doc_title(path)
    if not path.exists():
        return raw_title
    tex_title = ""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return raw_title
    match = re.search(r"\\title\s*\{(?P<title>[^{}]+)\}", text)
    if match:
        tex_title = re.sub(r"\s+", " ", match.group("title")).strip()
    if raw_title and is_more_specific_title(raw_title, tex_title):
        return raw_title
    return tex_title or raw_title


def resolve_source_file_path(source_file: str) -> Path:
    path = Path(source_file)
    if not path.is_absolute():
        path = Path.cwd() / path
    if path.exists():
        return path

    fallback = resolve_paddle_output_source_path(path)
    return fallback or path


def resolve_paddle_output_source_path(path: Path) -> Path | None:
    parts = path.parts
    lowered = [part.lower() for part in parts]
    if "paddle_output" not in lowered:
        return None
    paddle_index = lowered.index("paddle_output")
    suffix = Path(*parts[paddle_index + 1 :])
    if not str(suffix):
        return None
    candidate = Path.cwd() / "data" / "paddle_output" / suffix
    if candidate.exists() or (candidate.parent / "intermediate" / "paddle_raw_response.json").exists():
        return candidate
    return None


def extract_raw_doc_title(source_file: Path) -> str:
    raw_path = source_file.parent / "intermediate" / "paddle_raw_response.json"
    if not raw_path.exists():
        return ""
    try:
        payload = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(payload, list) or not payload:
        return ""
    first_page = payload[0] if isinstance(payload[0], dict) else {}
    blocks = first_page.get("parsing_res_list")
    if not isinstance(blocks, list):
        return ""
    title_blocks: list[tuple[float, float, str]] = []
    for block in blocks:
        if not isinstance(block, dict) or block.get("block_label") != "doc_title":
            continue
        content = re.sub(r"\s+", " ", str(block.get("block_content") or "")).strip()
        if not content or re.fullmatch(r"(?:chapter\s*)?\d+", content, flags=re.IGNORECASE):
            continue
        bbox = block.get("block_bbox") if isinstance(block.get("block_bbox"), list) else []
        y0 = float(bbox[1]) if len(bbox) >= 2 and isinstance(bbox[1], (int, float)) else 0.0
        order = block.get("block_order")
        order_value = float(order) if isinstance(order, (int, float)) else y0
        title_blocks.append((order_value, y0, content))
    if not title_blocks:
        return ""
    parts = [content for _, _, content in sorted(title_blocks)]
    title = parts[0]
    for part in parts[1:]:
        title = f"{title}{' ' if title.endswith(':') else ' / '}{part}"
    return re.sub(r"\s+", " ", title).strip()


def is_more_specific_title(candidate: str, baseline: str) -> bool:
    candidate_text = str(candidate or "").strip()
    baseline_text = str(baseline or "").strip()
    if not candidate_text:
        return False
    if not baseline_text:
        return True
    candidate_key = normalize_heading_compare(candidate_text)
    baseline_key = normalize_heading_compare(baseline_text)
    if not candidate_key or candidate_key == baseline_key:
        return False
    return candidate_key.startswith(baseline_key) or len(candidate_key) > len(baseline_key)


def heading_contains_title(display: str, title: str) -> bool:
    return normalize_heading_compare(title) in normalize_heading_compare(display)


def normalize_heading_compare(value: str) -> str:
    return re.sub(r"[^0-9a-z]+", " ", str(value or "").lower()).strip()


def looks_like_chapter_subtitle(value: str) -> bool:
    text = str(value or "").strip()
    return bool(re.match(r"^\d+\.\s+\S", text))


def block_type_label(block_type: str) -> str:
    labels = {
        "derivation": "推导 Derivation",
        "definition": "定义 Definition",
        "proposition": "命题 Proposition",
        "example": "示例 Example",
    }
    return labels.get(block_type, block_type.capitalize())


def normalize_table_rows(raw_rows: Any) -> list[list[str]]:
    if not isinstance(raw_rows, list):
        return []
    rows: list[list[str]] = []
    for row in raw_rows:
        if isinstance(row, list):
            rows.append(["" if cell is None else str(cell) for cell in row])
    return rows


def markdown_table_cell(value: str) -> str:
    return inline_table_math(normalize_latex_for_katex(str(value))).replace("\n", "<br>").replace("|", r"\|")


def inline_table_math(text: str) -> str:
    """Keep table-cell math inline; block delimiters are invalid inside one HTML/Markdown row."""
    return re.sub(r"(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$", r"$\1$", str(text or ""))


def normalize_latex_math(latex: str) -> str:
    value = str(latex or "")
    value = re.sub(r"(\\(?:qquad|quad|;|,|:))(?=[A-Za-z])", r"\1 ", value)
    value = re.sub(r"\\sigma_e_s\^2", r"\\sigma_{e_s}^2", value)
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
    for macro in SUPPORTED_OPERATOR_MACROS:
        value = re.sub(rf"\\{macro}\b", rf"\\operatorname{{{macro}}}", value)
    return value


def normalize_latex_for_katex(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        open_delim = match.group(1)
        body = match.group(2)
        close_delim = match.group(3)
        return f"{open_delim}{normalize_latex_math(body)}{close_delim}"

    return re.sub(r"(\${1,2})([\s\S]*?)(\1)", repl, str(text or ""))


def canonicalize_display_math(text: str) -> str:
    """Put every balanced ``$$`` delimiter on its own line without changing TeX."""
    value = str(text or "")
    parts: list[str] = []
    cursor = 0
    text_start = 0

    def escaped(index: int) -> bool:
        slashes = 0
        probe = index - 1
        while probe >= 0 and value[probe] == "\\":
            slashes += 1
            probe -= 1
        return slashes % 2 == 1

    while cursor < len(value) - 1:
        if value[cursor : cursor + 2] != "$$" or escaped(cursor):
            cursor += 1
            continue
        end = cursor + 2
        while end < len(value) - 1:
            if value[end : end + 2] == "$$" and not escaped(end):
                break
            end += 1
        else:
            cursor += 2
            continue

        body = value[cursor + 2 : end].strip()
        if not body:
            cursor = end + 2
            continue
        before = value[text_start:cursor].strip()
        if before:
            parts.append(before)
        parts.append(f"$$\n{body}\n$$")
        cursor = end + 2
        text_start = cursor

    remaining = value[text_start:].strip()
    if remaining:
        parts.append(remaining)
    if not parts:
        return value
    return "\n\n".join(parts)
