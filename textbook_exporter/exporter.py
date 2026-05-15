from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


CHUNK_FILE_RE = re.compile(r"^((?:chapter|appendix)\d+)_(\d+)\.json$", re.IGNORECASE)
NUMBERED_REF_RE = re.compile(r"^(\d+)\.\d+")
PLACEHOLDER_RE = re.compile(
    r"\[\[(?P<tag>SEE_FORMULA|SEE_TABLE|SEE_EXAMPLE|SEE_FIGURE|TABLE|FORMULA|EXAMPLE|FIGURE):(?P<id>[^\]]+)\]\]",
    re.IGNORECASE,
)
SEE_TABLE_RE = re.compile(r"\[\[SEE_TABLE:(?P<id>[^\]]+)\]\]", re.IGNORECASE)
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


def parse_chapter_filter(raw: str | None) -> set[str] | None:
    if raw is None or not str(raw).strip():
        return None
    chapters = {
        normalize_chapter_id(part)
        for part in str(raw).split(",")
        if normalize_chapter_id(part)
    }
    return chapters or None


def export_textbooks(
    structured_dir: str | Path,
    out_dir: str | Path,
    chapters: Iterable[str] | None = None,
    figure_library: str | Path | None = None,
) -> list[TextbookExportResult]:
    structured_path = Path(structured_dir)
    output_path = Path(out_dir)
    chapter_filter = (
        {normalize_chapter_id(chapter) for chapter in chapters if normalize_chapter_id(chapter)}
        if chapters is not None
        else None
    )

    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in structured_path.glob("*_*.json"):
        match = CHUNK_FILE_RE.fullmatch(path.name)
        if not match:
            continue
        chapter = normalize_chapter_id(match.group(1))
        if chapter_filter is not None and chapter not in chapter_filter:
            continue
        grouped[chapter].append(path)

    renderer = TextbookRenderer(structured_path, figure_library=Path(figure_library) if figure_library else None)
    output_path.mkdir(parents=True, exist_ok=True)

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
    def __init__(self, structured_dir: Path, figure_library: Path | None = None):
        self.structured_dir = structured_dir
        self.figure_library_path = figure_library
        self.figure_library_root = figure_library.parent if figure_library else structured_dir
        self.formula_map = self._load_formula_map()
        self.figure_map = self._load_figure_map()
        self.tables_by_id, self.tables_by_chapter_id = self._load_table_maps()
        (
            self.examples_by_ref,
            self.examples_by_chapter_ref,
            self.examples_by_chapter_label,
        ) = self._load_example_maps()
        self.chapter_titles_by_source_file: dict[str, str] = {}

    def render_chapter(self, chapter: str, chunks: list[dict[str, Any]]) -> str:
        chapter_label = render_chapter_label(chapter)
        chapter_title = self.chapter_title_for_render(chapter, chunks)
        lines = [
            f"# {render_chapter_heading(chapter_label, chapter_title)}",
            "",
        ]

        for chunk in chunks:
            chunk_id = str(chunk.get("id") or "")
            metadata = chunk.get("metadata") if isinstance(chunk.get("metadata"), dict) else {}
            display_section = display_heading_for_chunk(
                chunk_id,
                metadata,
                document_title=self.document_title_for_chunk(metadata),
            )
            lines.append(f"## {chunk_id} · {display_section}")
            lines.append("")

            expanded_assets: set[str] = set()
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
                )

                if block_type != "discussion":
                    lines.append(f"**[{block_type_label(block_type)}]**")
                    lines.append("")
                lines.append(rendered)
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

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
    ) -> str:
        content = normalize_latex_for_katex(content)
        def replace_see_table(match: re.Match[str]) -> str:
            table_id = match.group("id").strip()
            if (
                self.table_owned_by_chunk(table_id, current_chapter, current_chunk_id)
                and not content[: match.start()].strip()
            ):
                table_key = self.asset_key("TABLE", table_id, current_chapter)
                if table_key in expanded_assets:
                    return self.render_table_reference(table_id, current_chapter)
                expanded_assets.add(table_key)
                return self.render_table_block(table_id, current_chapter)
            return self.render_table_reference(table_id, current_chapter)

        content = SEE_TABLE_RE.sub(replace_see_table, content)

        parts: list[str] = []
        last_end = 0
        for match in PLACEHOLDER_RE.finditer(content):
            tag = match.group("tag").upper()
            raw_id = match.group("id").strip()
            if tag == "SEE_FIGURE":
                continue
            before = content[last_end : match.start()].strip()
            if before:
                parts.append(before)

            if tag == "TABLE" and self.numbered_table_cross_owner(raw_id, current_chapter, current_chunk_id) and not force_expand_tables:
                parts.append(self.render_table_reference(raw_id, current_chapter))
                last_end = match.end()
                continue
            asset_key = self.asset_key(tag, raw_id, current_chapter)
            if tag == "TABLE" and inline_table_scope and self.table_is_inline(raw_id, current_chapter):
                asset_key = f"{asset_key}:{inline_table_scope}"

            if asset_key in expanded_assets:
                parts.append(self.render_repeat_reference(tag, raw_id))
            else:
                expanded_assets.add(asset_key)
                if tag in {"SEE_FORMULA", "FORMULA"}:
                    parts.append(self.render_formula_block(raw_id))
                elif tag == "TABLE":
                    parts.append(self.render_table_block(raw_id, current_chapter))
                elif tag in {"SEE_EXAMPLE", "EXAMPLE"}:
                    parts.append(self.render_example_block(raw_id, expanded_assets, current_chapter))
                elif tag == "FIGURE":
                    parts.append(self.render_figure_block(raw_id, current_chapter))
                else:
                    parts.append(match.group(0))
            last_end = match.end()

        remaining = content[last_end:].strip()
        if remaining:
            parts.append(remaining)
        rendered = "\n\n".join(parts) if parts else content
        return self.replace_inline_figure_references(rendered)

    def table_is_inline(self, table_id: str, current_chapter: str | None) -> bool:
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return False
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
        return "\n".join(
            [
                f"> **Formula {label}** · `{clean_ref_id(formula_id)}` · source: `{unit_id}` · {subsection}",
                ">",
                f"> $$ {latex} $$",
                "",
            ]
        )

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
        html = str(table.get("html") or "")
        resolved_id = clean_ref_id(table.get("id") or table_id)
        table_type = str(table.get("table_type") or "").strip().lower()

        lines = [
            f"> **{label}** · `{resolved_id}` · page {page} · source: `{unit_id}`",
            f"> {title}",
            ">",
        ]

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
                    lines.append("")
                    return "\n".join(lines)
                lines.append("> " + " | ".join(render_cell(cell) for cell in rows[0]))
                lines.append("> " + " | ".join("---" for _ in range(column_count)))
                for row in rows[1:]:
                    lines.append("> " + " | ".join(render_cell(cell) for cell in row))
                lines.append("")
                return "\n".join(lines)

        if html:
            for line in html.splitlines() or [html]:
                lines.append(f"> {line}")
            lines.append("")
            return "\n".join(lines)

        lines.append("> [Table data not available]")
        lines.append("")
        return "\n".join(lines)

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
        table = self.resolve_table(table_id, current_chapter)
        if not table:
            return f"Table {clean_ref_id(table_id)}"
        return str(table.get("label_format") or f"Table {clean_ref_id(table_id)}")

    def render_figure_block(self, figure_id: str, current_chapter: str | None) -> str:
        figure = self.resolve_figure(figure_id, current_chapter)
        if not figure:
            return f"> **[UNRESOLVED FIGURE: {figure_id}]**\n"

        figure_ref = clean_ref_id(figure.get("id") or figure_id)
        caption = normalize_latex_for_katex(str(figure.get("caption") or f"Figure {figure_ref}"))
        asset_path = str(figure.get("asset_path") or "").strip()
        asset_target = self.figure_library_root / asset_path if asset_path else None
        image_path = str(asset_target).replace("\\", "/") if asset_target else ""
        page = figure.get("page", "?")
        chapter = normalize_chapter_id(figure.get("chapter") or current_chapter or "")
        lines = [
            f"> **Figure {figure_ref}** · page {page} · source: `{chapter}`",
        ]
        if image_path:
            lines.extend([">", f"> ![Figure {figure_ref}]({image_path})"])
        lines.extend([">", f"> {caption}", ""])
        return "\n".join(lines)

    def render_figure_reference(self, figure_id: str) -> str:
        return f"Figure {clean_ref_id(figure_id)}"

    def replace_inline_figure_references(self, value: str) -> str:
        return re.sub(
            r"\[\[SEE_FIGURE:(?P<id>[^\]]+)\]\]",
            lambda match: self.render_figure_reference(match.group("id").strip()),
            value,
            flags=re.IGNORECASE,
        )

    def render_example_block(
        self,
        example_ref: str,
        expanded_assets: set[str],
        current_chapter: str | None,
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
        if tag == "TABLE":
            return f"*[Table {ref} - see above]*"
        if tag in {"SEE_EXAMPLE", "EXAMPLE"}:
            return f"*[Example {ref} - see above]*"
        if tag in {"SEE_FIGURE", "FIGURE"}:
            return f"*[Figure {ref} - see above]*"
        return f"*[{ref} - see above]*"

    def _load_formula_map(self) -> dict[str, dict[str, Any]]:
        library = read_json_if_exists(self.structured_dir / "formula_library.json", {"formulas": []})
        formulas = library.get("formulas") if isinstance(library, dict) else []
        return {
            clean_ref_id(formula.get("id")): formula
            for formula in formulas
            if isinstance(formula, dict) and clean_ref_id(formula.get("id"))
        }

    def _load_figure_map(self) -> dict[tuple[str, str], dict[str, Any]]:
        path = self.figure_library_path or (self.structured_dir / "figure_library.json")
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
    ) -> tuple[dict[str, list[dict[str, Any]]], dict[tuple[str, str], list[dict[str, Any]]]]:
        library = read_json_if_exists(self.structured_dir / "table_library.json", {"tables": []})
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
    match = re.fullmatch(r"chapter(\d+)", normalize_chapter_id(chapter))
    if match:
        return (0, int(match.group(1)), chapter)
    return (9, 9999, chapter)


def chunk_file_sort_key(path: Path) -> tuple[int, int, str]:
    match = CHUNK_FILE_RE.fullmatch(path.name)
    if not match:
        return (9999, 9999, path.name)
    chapter = normalize_chapter_id(match.group(1))
    return (chapter_sort_key(chapter)[1], int(match.group(2)), path.name)


def render_chapter_label(chapter: str) -> str:
    match = re.fullmatch(r"chapter(\d+)", normalize_chapter_id(chapter))
    if match:
        return f"Chapter {match.group(1)}"
    appendix_match = re.fullmatch(r"appendix(\d+)", normalize_chapter_id(chapter))
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
    chapter_match = re.match(r"chapter(\d+)_", chunk_id, flags=re.IGNORECASE)
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
    chapter_match = re.match(r"chapter(\d+)_", str(chunk_id or ""), flags=re.IGNORECASE)
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
    chapter_match = re.match(r"chapter(\d+)_", str(chunk_id or ""), flags=re.IGNORECASE)
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
    return normalize_latex_for_katex(str(value)).replace("\n", "<br>").replace("|", r"\|")


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
