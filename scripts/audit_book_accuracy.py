#!/usr/bin/env python3
"""Build, verify, and install source-PDF-grounded textbook audits.

The public interface is intentionally book-generic.  Book-specific inputs live
in ``book_audits/<Book>.json``; generated evidence lives only below
``tmp/book_audits/<Book>``.  Human review records are optional spot-check
metadata; automatic verification is the sole installation gate.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import platform
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from textbook_exporter.exporter import export_textbooks

AUDIT_ROOT = ROOT / "tmp" / "book_audits"
KINDS = ("pages", "blocks", "formulas", "tables", "figures", "examples")
RESOURCE_KINDS = ("formulas", "tables", "figures", "examples")
PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE|FIGURE|EXAMPLE):[^\]]+\]\]")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
MOJIBAKE_RE = re.compile(r"(?:鈥|銆|锟|闁|鏂|馃|璇|澶|绔|娴|褰|鍥|缁|瀹|閿)")
SUBSTANTIVE_LABELS = {
    "abstract", "chart", "display_formula", "doc_title", "figure_title",
    "footnote", "image", "inline_formula", "paragraph_title", "table",
    "text", "vision_footnote",
}
PROFILE_SCHEMA = "book_accuracy_profile.v2"
MANIFEST_SCHEMA = "book_accuracy_audit.v2"
AUDIT_SCRIPT = Path(__file__).resolve()
EXPORTER_SCRIPT = Path(export_textbooks.__code__.co_filename).resolve()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_json(value: Any) -> str:
    return hash_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bind_files(paths: Iterable[Path], base: Path) -> dict[str, Any]:
    """Return a deterministic, path-addressed hash binding for existing files."""
    files: dict[str, str] = {}
    for path in sorted({item.resolve() for item in paths}):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(base.resolve()).as_posix()
        except ValueError as exc:
            raise ValueError(f"bound file escapes base directory: {path}") from exc
        files[relative] = sha256(path)
    return {"files": files, "sha256": hash_json(files), "count": len(files)}


def bind_tree(root: Path) -> dict[str, Any]:
    paths = [path for path in root.rglob("*") if path.is_file()] if root.is_dir() else []
    return bind_files(paths, root)


def binding_errors(binding: dict[str, Any], base: Path, label: str) -> list[str]:
    expected = binding.get("files") or {}
    errors: list[str] = []
    current: dict[str, str] = {}
    for relative, expected_hash in expected.items():
        path = (base / relative).resolve()
        if not inside(path, base):
            errors.append(f"{label} binding escapes base: {relative}")
        elif not path.is_file():
            errors.append(f"{label} file missing: {relative}")
        else:
            current[relative] = sha256(path)
            if current[relative] != expected_hash:
                errors.append(f"{label} file drifted: {relative}")
    if hash_json(current) != binding.get("sha256"):
        errors.append(f"{label} digest mismatch")
    return errors


def tree_binding_errors(binding: dict[str, Any], base: Path, label: str) -> list[str]:
    current = bind_tree(base)
    if current == binding:
        return []
    expected_files = set((binding.get("files") or {}).keys())
    current_files = set((current.get("files") or {}).keys())
    errors = [f"{label} artifact digest mismatch"]
    errors.extend(f"{label} artifact missing: {path}" for path in sorted(expected_files - current_files))
    errors.extend(f"{label} unexpected artifact: {path}" for path in sorted(current_files - expected_files))
    errors.extend(
        f"{label} artifact drifted: {path}"
        for path in sorted(expected_files & current_files)
        if binding["files"][path] != current["files"][path]
    )
    return errors


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_book(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise ValueError(f"unsafe book identifier: {value!r}")
    return value


def profile_for(book: str) -> tuple[dict[str, Any], Path]:
    book = safe_book(book)
    path = ROOT / "book_audits" / f"{book}.json"
    if not path.is_file():
        raise FileNotFoundError(f"book audit profile not found: {path}")
    profile = read_json(path)
    if profile.get("book") != book:
        raise ValueError(f"profile book mismatch: {profile.get('book')!r} != {book!r}")
    if profile.get("schema") != PROFILE_SCHEMA:
        raise ValueError(f"profile must use {PROFILE_SCHEMA}: {path}")
    if profile.get("profile_state") == "blocked_missing_master_pdf":
        raise ValueError(str(profile.get("blocked_reason") or "profile is blocked: master PDF is missing"))
    return profile, path


def one_glob(pattern: str) -> Path:
    matches = sorted(path for path in ROOT.glob(pattern) if path.is_file())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one file for {pattern!r}, found {len(matches)}")
    return matches[0]


def master_part_paths(profile: dict[str, Any]) -> list[Path]:
    """Validate and return every authoritative part of a composite master."""
    paths: list[Path] = []
    parts = profile.get("master_pdf_parts") or []
    if profile.get("master_pdf_mode") == "ordered_parts" and not parts:
        parts = [
            {
                "path": chapter.get("chapter_pdf_glob"),
                "sha256": chapter.get("chapter_pdf_sha256"),
                "page_count": chapter.get("chapter_pdf_page_count"),
            }
            for chapter in profile.get("chapters") or []
        ]
    for index, part in enumerate(parts, 1):
        relative = str(part.get("path") or "")
        path = (ROOT / relative).resolve()
        if not relative or not inside(path, ROOT) or not path.is_file():
            raise ValueError(f"composite master part {index} is missing or unsafe: {relative!r}")
        expected_hash = str(part.get("sha256") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or sha256(path) != expected_hash:
            raise ValueError(f"composite master part hash differs from profile: {relative}")
        with fitz.open(path) as document:
            expected_pages = int(part.get("page_count") or 0)
            if expected_pages <= 0 or len(document) != expected_pages:
                raise ValueError(
                    f"composite master part page count differs from profile: "
                    f"{relative} ({len(document)} != {expected_pages})"
                )
        paths.append(path)
    return paths


def materialize_master(profile: dict[str, Any]) -> Path:
    """Resolve a single master or deterministically derive one from trusted parts."""
    parts = master_part_paths(profile)
    if not parts:
        return one_glob(profile["master_pdf_glob"])
    relative = str(profile.get("master_pdf_glob") or "")
    if not relative or any(token in relative for token in "*?["):
        raise ValueError("a composite master requires an exact master_pdf_glob output path")
    master = (ROOT / relative).resolve()
    if not inside(master, AUDIT_ROOT / safe_book(str(profile["book"]))):
        raise ValueError("derived composite master must live inside its tmp/book_audits directory")
    expected_hash = str(profile.get("master_pdf_sha256") or "")
    if master.is_file() and re.fullmatch(r"[0-9a-f]{64}", expected_hash) and sha256(master) == expected_hash:
        return master
    master.parent.mkdir(parents=True, exist_ok=True)
    temporary = master.with_name(f".{master.name}.building-{os.getpid()}")
    temporary.unlink(missing_ok=True)
    document = fitz.open()
    try:
        for part in parts:
            with fitz.open(part) as source:
                document.insert_pdf(source)
        document.set_metadata({})
        document.save(temporary, garbage=4, deflate=True, clean=True, no_new_id=True)
    finally:
        document.close()
    os.replace(temporary, master)
    return master


def page_rows(page: dict[str, Any]) -> list[dict[str, Any]]:
    pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else {}
    rows = pruned.get("parsing_res_list") or page.get("parsing_res_list") or []
    return [row for row in rows if isinstance(row, dict)]


def row_bbox(row: dict[str, Any]) -> list[float] | None:
    value = row.get("block_bbox") or row.get("bbox")
    if isinstance(value, list) and len(value) == 4:
        return [float(item) for item in value]
    return None


def clean(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = PLACEHOLDER_RE.sub(" ", text)
    text = re.sub(r"[`*_#>|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalized(value: Any) -> str:
    text = clean(value).replace("‐", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"-\s+([a-z])", r"\1", text)
    return re.sub(r"[^0-9A-Za-z]+", "", text).lower()


def block_core(block: dict[str, Any]) -> dict[str, Any]:
    """Strip generated provenance before comparing a correction payload."""
    generated = {
        "source_page", "source_pages", "source_block_ids", "source_bboxes",
        "provenance_score", "content_sha256",
    }
    return {key: value for key, value in block.items() if key not in generated}


def metadata_source_ids(
    unit: dict[str, Any], source_ids: list[str], raw_by_id: dict[str, dict[str, Any]],
    consumed: set[str], anchor: int,
) -> list[str]:
    """Bind structural headings stored as unit metadata to their exact source blocks."""
    metadata = unit.get("metadata") or {}
    heading_source = metadata.get("heading_source") if isinstance(metadata.get("heading_source"), dict) else {}
    declared_locators = list(heading_source.get("source_block_ids") or [])
    declared_blocks = heading_source.get("source_blocks") if isinstance(heading_source.get("source_blocks"), list) else []
    for record in declared_blocks:
        if isinstance(record, dict):
            declared_locators.extend(record.get("source_block_ids") or [])
            if record.get("source_block_id"):
                declared_locators.append(record["source_block_id"])
    selected: list[str] = []
    for locator in declared_locators:
        value = str(locator)
        if value in raw_by_id and value in source_ids:
            selected.append(value)
            continue
        match = re.fullmatch(r"p(\d+):b(.+)", value, re.I)
        if not match:
            continue
        page, block = int(match.group(1)), match.group(2)
        candidates = [
            source_id for source_id in source_ids
            if source_id.endswith(f":b{block}")
            and page in {
                int(raw_by_id[source_id]["master_page"]),
                int(raw_by_id[source_id]["chapter_page"]),
            }
        ]
        if len(candidates) == 1:
            selected.append(candidates[0])
    labels = list(metadata.get("heading_path") or [])
    labels.extend([
        metadata.get("display_heading"), metadata.get("source_title"),
        *(metadata.get("source_heading_aliases") or []),
    ])
    chapter_match = re.search(r"(?:chapter|appendix)(\d+)$", str(metadata.get("chapter") or ""), re.I)
    if chapter_match:
        labels.append(f"CHAPTER {chapter_match.group(1)}")
    order = {source_id: index for index, source_id in enumerate(source_ids)}
    for label in labels:
        needle = normalized(label)
        if not needle:
            continue
        candidates = [
            source_id for source_id in source_ids
            if source_id not in consumed and source_id not in selected
            and raw_by_id[source_id]["label"] in {"doc_title", "paragraph_title", "text"}
            and (
                normalized(raw_by_id[source_id]["content"]) == needle
                or normalized(raw_by_id[source_id]["content"]) in needle
            )
        ]
        if candidates:
            selected.append(min(candidates, key=lambda source_id: (abs(order[source_id] - anchor), order[source_id])))
    return selected


def resource_source_ids(
    item: dict[str, Any], singular: str, chapter: str,
    raw_by_id: dict[str, dict[str, Any]], ids_by_chapter: dict[str, list[str]],
    *, page_mode: str = "local",
) -> list[str]:
    """Recover exact Paddle blocks from resource metadata and visible labels."""
    evidence = item.get("source_evidence") or {}
    source = item.get("source") or {}
    locators = [
        *(item.get("source_block_ids") or []),
        *(evidence.get("source_block_ids") or []),
        *(source.get("source_block_ids") or []),
    ]
    for record in [
        *(item.get("parts") or []), *(item.get("notes") or []),
        item.get("caption_block"),
    ]:
        if not isinstance(record, dict):
            continue
        locators.extend(record.get("source_block_ids") or [])
        locators.extend(record.get("caption_source_block_ids") or [])
    selected = explicit_source_ids(chapter, locators, raw_by_id, ids_by_chapter)

    # Figure extraction already records the original body and caption block IDs.
    for record in [*(item.get("body_blocks") or []), item.get("caption_block")]:
        if not isinstance(record, dict) or record.get("page") is None or record.get("block_id") is None:
            continue
        source_id = f"{chapter}:p{int(record['page']):03d}:b{record['block_id']}"
        if source_id in raw_by_id:
            selected.append(source_id)

    if singular == "figure":
        master_page_mode = page_mode == "master"
        page_values = {
            int(record["page"])
            for record in [*(item.get("body_blocks") or []), item.get("caption_block")]
            if isinstance(record, dict) and record.get("page") is not None
        }
        for value in [item.get("page"), source.get("page")]:
            if isinstance(value, int):
                page_values.add(value)
        recorded_boxes = [
            [float(value) for value in record["bbox"]]
            for record in [*(item.get("body_blocks") or []), item.get("caption_block")]
            if isinstance(record, dict) and isinstance(record.get("bbox"), list)
        ]
        if isinstance(item.get("raw_bbox"), list):
            recorded_boxes.append([float(value) for value in item["raw_bbox"]])
        for source_id in ids_by_chapter.get(chapter, []):
            source = raw_by_id[source_id]
            source_page = source["master_page"] if master_page_mode else source["chapter_page"]
            if source_page not in page_values:
                continue
            source_box = source.get("bbox")
            if source_box and any(
                overlap_ratio(source_box, box) >= 0.2
                or overlap_ratio(box, source_box) >= 0.2
                for box in recorded_boxes
            ):
                selected.append(source_id)

        # Some figures continue on the immediately following page while the
        # original library records only the caption page. Associate a blank
        # graphic block only when it is the sole adjacent-page candidate and
        # its page contains a unique matching figure reference.
        if page_values:
            for adjacent_page in {min(page_values) - 1, max(page_values) + 1}:
                graphic_ids = [
                    source_id for source_id in ids_by_chapter.get(chapter, [])
                    if raw_by_id[source_id]["chapter_page"] == adjacent_page
                    and raw_by_id[source_id]["label"] in {"image", "chart"}
                ]
                if len(graphic_ids) != 1:
                    continue
                marker_text = normalized(f"figure {item.get('id')}")
                page_text = "".join(
                    normalized(raw_by_id[source_id]["content"])
                    for source_id in ids_by_chapter.get(chapter, [])
                    if raw_by_id[source_id]["chapter_page"] == adjacent_page
                )
                if marker_text and marker_text in page_text:
                    selected.extend(graphic_ids)

    chapter_ids = ids_by_chapter.get(chapter, [])
    marker = normalized(item.get("label_format") or item.get("id"))
    if singular == "formula" and marker:
        aliases = {marker}
        if marker.endswith("l"):
            # OCR commonly confuses the lowercase equation suffix l with 1.
            aliases.add(f"{marker[:-1]}1")
        if marker[-1:].isalpha():
            aliases.add(f"{marker[:-1]}mathrm{marker[-1]}")
        numbered = [
            source_id for source_id in chapter_ids
            if raw_by_id[source_id]["label"] == "formula_number"
            and normalized(raw_by_id[source_id]["content"]) in aliases
        ]
        displayed = [
            source_id for source_id in chapter_ids
            if raw_by_id[source_id]["label"] == "display_formula"
            and any(alias in normalized(raw_by_id[source_id]["content"]) for alias in aliases)
        ]
        selected.extend(numbered or displayed)
        order = {source_id: index for index, source_id in enumerate(chapter_ids)}
        for number_id in numbered:
            number = raw_by_id[number_id]
            previous = [
                source_id for source_id in chapter_ids
                if order[source_id] < order[number_id]
                and raw_by_id[source_id]["master_page"] == number["master_page"]
                and raw_by_id[source_id]["label"] == "display_formula"
            ]
            if previous:
                selected.append(previous[-1])

    if singular == "formula" and not selected:
        # Unnumbered equations have no formula_number block.  Their formal
        # master-page bbox is sufficient to bind the exact Paddle display
        # block, but ambiguity is never accepted.
        page = source.get("page") or evidence.get("pdf_page")
        box = source.get("bbox") or evidence.get("formula_bbox")
        if isinstance(page, int) and isinstance(box, list) and len(box) == 4:
            candidates = []
            for source_id in chapter_ids:
                source_box = raw_by_id[source_id].get("bbox")
                if (
                    raw_by_id[source_id]["master_page"] != page
                    or raw_by_id[source_id]["label"] != "display_formula"
                    or not source_box
                ):
                    continue
                forward = overlap_ratio(source_box, [float(value) for value in box])
                reverse = overlap_ratio([float(value) for value in box], source_box)
                if max(forward, reverse) >= 0.45:
                    candidates.append((max(forward, reverse), source_id))
            if candidates:
                candidates.sort(reverse=True)
                if len(candidates) == 1 or candidates[0][0] - candidates[1][0] >= 0.05:
                    selected.append(candidates[0][1])

    if singular == "table" and marker:
        title = normalized(item.get("title"))
        title_ids = [
            source_id for source_id in chapter_ids
            if raw_by_id[source_id]["label"] in {"figure_title", "table", "text"}
            and (
                marker in normalized(raw_by_id[source_id]["content"])
                or (title and normalized(raw_by_id[source_id]["content"]) in title)
            )
        ]
        if title_ids:
            # Prefer an explicit table caption over prose that merely cites it.
            title_id = min(
                title_ids,
                key=lambda source_id: (
                    raw_by_id[source_id]["label"] != "figure_title",
                    len(normalized(raw_by_id[source_id]["content"])) < len(marker) + 5,
                ),
            )
            selected.append(title_id)
            page = raw_by_id[title_id]["master_page"]
            delivery = normalized(" ".join([
                str(item.get("title") or ""), str(item.get("html") or ""),
                json.dumps(item.get("rows") or [], ensure_ascii=False),
            ]))
            selected.extend(
                source_id for source_id in chapter_ids
                if page <= raw_by_id[source_id]["master_page"] <= page + 1
                and raw_by_id[source_id]["label"] == "table"
                and len(normalized(raw_by_id[source_id]["content"])) >= 10
                and normalized(raw_by_id[source_id]["content"]) in delivery
            )
    return list(dict.fromkeys(selected))


def resolve_page_span(start_page: int, end_page: int, chapter_profile: dict[str, Any]) -> tuple[int, int]:
    """Resolve chapter-local evidence pages while preserving explicit master pages."""
    chapter_size = chapter_profile["master_end"] - chapter_profile["master_start"] + 1
    if 1 <= start_page <= chapter_size:
        start_page = chapter_profile["master_start"] + start_page - 1
    if 1 <= end_page <= chapter_size:
        end_page = chapter_profile["master_start"] + end_page - 1
    return start_page, end_page


def example_boundary_source_ids(
    item: dict[str, Any], row: dict[str, Any], chapter_profile: dict[str, Any],
    raw_by_id: dict[str, dict[str, Any]], chapter_ids: list[str],
) -> list[str]:
    """Return every source block inside a PDF-rule-delimited formal Example."""
    evidence = item.get("evidence") if isinstance(item.get("evidence"), dict) else {}
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    lower_rule = evidence.get("lower_rule") if isinstance(evidence.get("lower_rule"), dict) else {}
    visual_rule = evidence.get("visual_stop_rule_bbox")
    trusted_boundary = bool(lower_rule) or (
        bool(evidence.get("visual_stop_clipped"))
        and isinstance(visual_rule, list)
        and len(visual_rule) >= 2
    )
    if not trusted_boundary:
        return []
    start_page = int(metadata.get("source_page") or evidence.get("source_page") or 0)
    end_page = int(lower_rule.get("page") or evidence.get("visual_stop_page") or start_page or 0)
    if not start_page:
        return []
    start_page, end_page = resolve_page_span(start_page, end_page, chapter_profile)
    end_y = float(
        lower_rule.get("y")
        or (visual_rule[1] if visual_rule else float("inf"))
    )
    marker = normalized(item.get("label") or f"Example {row.get('id')}")
    start_candidates = [
        source_id for source_id in chapter_ids
        if raw_by_id[source_id]["master_page"] == start_page
        and marker in normalized(raw_by_id[source_id].get("content"))
    ]
    if not start_candidates:
        start_candidates = [
            source_id for source_id in row.get("source_block_ids") or []
            if raw_by_id[source_id]["master_page"] == start_page
        ]
    start_y = min(
        (float(raw_by_id[source_id]["bbox"][1]) for source_id in start_candidates if raw_by_id[source_id].get("bbox")),
        default=float("-inf"),
    )
    selected = []
    for source_id in chapter_ids:
        source = raw_by_id[source_id]
        page = int(source["master_page"])
        box = source.get("bbox")
        if not start_page <= page <= end_page or not box:
            continue
        if page == start_page and float(box[1]) < start_y:
            continue
        if page == end_page and float(box[1]) >= end_y:
            continue
        selected.append(source_id)
    return selected


def explicit_source_ids(
    chapter: str, locators: Iterable[Any], raw_by_id: dict[str, dict[str, Any]],
    ids_by_chapter: dict[str, list[str]],
) -> list[str]:
    """Resolve exact local or master-page block locators used by older ledgers."""
    selected: list[str] = []
    for value in locators:
        locator = str(value)
        if locator in raw_by_id and raw_by_id[locator].get("chapter") == chapter:
            selected.append(locator)
            continue
        match = re.fullmatch(r"p(\d+):b(.+)", locator, re.I)
        if not match:
            continue
        page, block = int(match.group(1)), match.group(2)
        candidates = [
            source_id for source_id in ids_by_chapter.get(chapter, [])
            if source_id.endswith(f":b{block}")
            and page in {
                int(raw_by_id[source_id]["master_page"]),
                int(raw_by_id[source_id]["chapter_page"]),
            }
        ]
        if len(candidates) == 1:
            selected.append(candidates[0])
    return list(dict.fromkeys(selected))


def rows_from_html(value: str) -> list[list[str]]:
    rows = []
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", value, flags=re.I | re.S):
        cells = [clean(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.I | re.S)]
        if cells:
            rows.append(cells)
    return rows


def raw_dimensions(page: dict[str, Any]) -> tuple[float, float]:
    pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else {}
    boxes = [box for box in (row_bbox(row) for row in page_rows(page)) if box]
    width = float(pruned.get("width") or page.get("width") or max((box[2] for box in boxes), default=1))
    height = float(pruned.get("height") or page.get("height") or max((box[3] for box in boxes), default=1))
    return width, height


def load_source(profile: dict[str, Any]) -> tuple[Path, dict[int, dict[str, Any]], list[dict[str, Any]]]:
    master = materialize_master(profile)
    expected_hash = str(profile.get("master_pdf_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or sha256(master) != expected_hash:
        raise ValueError("master PDF does not match the SHA-256 fixed by the v2 profile")
    with fitz.open(master) as master_doc:
        expected_pages = int(profile.get("master_page_count") or 0)
        if expected_pages <= 0 or len(master_doc) != expected_pages:
            raise ValueError(f"master PDF page count differs from profile: {len(master_doc)} != {expected_pages}")
    raw_pages: dict[int, dict[str, Any]] = {}
    page_map: list[dict[str, Any]] = []
    covered_pages: set[int] = set()
    for chapter in profile["chapters"]:
        expected = chapter["master_end"] - chapter["master_start"] + 1
        raw_dirs = chapter.get("raw_dirs") or [chapter["raw_dir"]]
        raw: list[dict[str, Any]] = []
        raw_paths_by_page: list[Path] = []
        for raw_dir in raw_dirs:
            raw_path = ROOT / raw_dir / "intermediate" / "paddle_raw_response.json"
            part = read_json(raw_path)
            raw.extend(part)
            raw_paths_by_page.extend([raw_path] * len(part))
        if len(raw) != expected:
            raise ValueError(f"{chapter['id']}: expected {expected} raw pages, found {len(raw)}")
        slice_pdf = one_glob(chapter["chapter_pdf_glob"])
        for local, page in enumerate(raw, 1):
            master_page = chapter["master_start"] + local - 1
            if master_page in covered_pages:
                raise ValueError(f"profile page ranges overlap at master page {master_page}")
            covered_pages.add(master_page)
            raw_pages[master_page] = page
            page_map.append({
                "book": profile["book"], "chapter": chapter["id"],
                "chapter_page": local, "master_page": master_page,
                "slice_pdf": str(slice_pdf.relative_to(ROOT)),
                "raw_response": str(raw_paths_by_page[local - 1].relative_to(ROOT)),
            })
    excluded_pages: set[int] = set()
    for exclusion in profile.get("excluded_page_ranges") or []:
        start, end = int(exclusion.get("start") or 0), int(exclusion.get("end") or 0)
        if start <= 0 or end < start or not str(exclusion.get("reason") or "").strip():
            raise ValueError(f"invalid excluded page range: {exclusion}")
        excluded_pages.update(range(start, end + 1))
    expected_master_pages = set(range(1, int(profile["master_page_count"]) + 1))
    if covered_pages & excluded_pages:
        raise ValueError("profile has pages that are both in scope and excluded")
    if covered_pages | excluded_pages != expected_master_pages:
        missing = sorted(expected_master_pages - covered_pages - excluded_pages)
        raise ValueError(f"profile does not classify every master page; missing={missing[:20]}")
    return master, raw_pages, page_map


def create_tree(audit: Path) -> None:
    for relative in (
        "source/pages", "source/normalized_layout", "evidence/page_contacts",
        "evidence/crops/formulas", "evidence/crops/tables", "evidence/crops/figures",
        "evidence/crops/examples", "evidence/contacts/formulas", "evidence/contacts/tables",
        "evidence/contacts/figures", "evidence/contacts/examples", "evidence/figure_pairs",
        "ledgers", "review", "corrections", "staging/data", "snapshots/preinstall",
        "reports", "logs", "failures",
    ):
        (audit / relative).mkdir(parents=True, exist_ok=True)


def copy_delivery(book: str, stage_data: Path) -> None:
    structured = stage_data / "structured"
    textbook = stage_data / "textbook"
    figures = stage_data / "figures"
    for target in (structured, textbook / "figures", figures):
        target.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / "data" / "structured").glob(f"{book}_*.json")):
        shutil.copy2(path, structured / path.name)
    for path in sorted((ROOT / "data" / "textbook").glob(f"{book}_*_textbook.md")):
        shutil.copy2(path, textbook / path.name)
    for path in sorted((ROOT / "data" / "figures").rglob(f"{book}_*")):
        if path.is_file():
            relative = path.relative_to(ROOT / "data" / "figures")
            (figures / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, figures / relative)
    for path in sorted((ROOT / "data" / "textbook" / "figures").rglob(f"{book}_*")):
        if path.is_file():
            relative = path.relative_to(ROOT / "data" / "textbook" / "figures")
            target = textbook / "figures" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    dedicated_examples = structured / f"{book}_example_library.json"
    if not dedicated_examples.is_file():
        shared_examples = ROOT / "data" / "structured" / "example_library.json"
        rows: list[dict[str, Any]] = []
        if shared_examples.is_file():
            payload = read_json(shared_examples)
            candidates = payload.get("examples", []) if isinstance(payload, dict) else []
            rows = [
                row for row in candidates if isinstance(row, dict)
                and str(row.get("book") or row.get("chapter") or "").lower().startswith(book.lower())
            ]
        write_json(dedicated_examples, {"schema": "book_example_library.v1", "book": book, "count": len(rows), "examples": rows})


def render_and_compare(master: Path, profile: dict[str, Any], page_map: list[dict[str, Any]], audit: Path, dpi: int) -> list[str]:
    errors: list[str] = []
    master_doc = fitz.open(master)
    slice_docs: dict[str, fitz.Document] = {}
    try:
        for item in page_map:
            master_page = item["master_page"]
            page = master_doc[master_page - 1]
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            target = audit / "source" / "pages" / f"page_{master_page:04d}.png"
            pix.save(target)
            item["page_image_sha256"] = sha256(target)
            slice_key = item["slice_pdf"]
            if slice_key not in slice_docs:
                slice_docs[slice_key] = fitz.open(ROOT / slice_key)
            slice_page = slice_docs[slice_key][item["chapter_page"] - 1]
            # Raster equality is authoritative here.  Text-only comparison can
            # falsely accept two different scanned pages with empty text layers.
            slice_pix = slice_page.get_pixmap(dpi=dpi, alpha=False)
            master_raster = hash_bytes(pix.samples)
            slice_raster = hash_bytes(slice_pix.samples)
            item["master_raster_sha256"] = master_raster
            item["slice_raster_sha256"] = slice_raster
            item["slice_matches_master"] = (
                (pix.width, pix.height, pix.n) == (slice_pix.width, slice_pix.height, slice_pix.n)
                and master_raster == slice_raster
            )
            if not item["slice_matches_master"]:
                errors.append(f"chapter slice differs from master page {master_page}: {slice_key} page {item['chapter_page']}")
    finally:
        master_doc.close()
        for document in slice_docs.values():
            document.close()
    return errors


def normalize_layout(raw_pages: dict[int, dict[str, Any]], page_map: list[dict[str, Any]], audit: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    raw_by_id: dict[str, dict[str, Any]] = {}
    ids_by_chapter: dict[str, list[str]] = defaultdict(list)
    mapping = {row["master_page"]: row for row in page_map}
    for master_page, page in sorted(raw_pages.items()):
        out = []
        for index, source in enumerate(page_rows(page)):
            source_id = f"{mapping[master_page]['chapter']}:p{mapping[master_page]['chapter_page']:03d}:b{source.get('block_id', index)}"
            row = {
                "source_block_id": source_id,
                "chapter": mapping[master_page]["chapter"],
                "master_page": master_page,
                "chapter_page": mapping[master_page]["chapter_page"],
                "label": str(source.get("block_label") or "").lower(),
                "bbox": row_bbox(source),
                "block_order": source.get("block_order"),
                "content": clean(source.get("block_content")),
                "raw_content": str(source.get("block_content") or ""),
            }
            row["content_sha256"] = hash_bytes(row["content"].encode("utf-8"))
            raw_by_id[source_id] = row
            ids_by_chapter[row["chapter"]].append(source_id)
            out.append(row)
        write_json(audit / "source" / "normalized_layout" / f"page_{master_page:04d}.json", out)
    return raw_by_id, ids_by_chapter


def span_for_content(content: str, source_ids: list[str], raw_by_id: dict[str, dict[str, Any]], cursor: int) -> tuple[list[str], float, int]:
    needle = normalized(content)
    if not needle:
        return [], 1.0, cursor
    chunks = [normalized(raw_by_id[item]["content"]) for item in source_ids]
    stream_parts: list[str] = []
    boundaries: list[tuple[int, int]] = []
    position = 0
    for chunk in chunks:
        start = position
        stream_parts.append(chunk)
        position += len(chunk)
        boundaries.append((start, position))
    stream = "".join(stream_parts)
    start_char = boundaries[min(cursor, len(boundaries) - 1)][0] if boundaries else 0
    exact = stream.find(needle, start_char)
    if exact >= 0:
        match_start, match_end, score = exact, exact + len(needle), 1.0
        matched_ranges = [(match_start, match_end)]
    else:
        # Corrections usually alter only a few characters.  Locate a stable
        # internal anchor first, then compare a bounded window.  Running
        # SequenceMatcher against an entire chapter for every block is both
        # slow and liable to jump to a repeated phrase on another page.
        anchor_hits: list[tuple[int, int]] = []
        anchor_size = min(32, max(12, len(needle) // 8))
        for offset in range(0, max(1, len(needle) - anchor_size + 1), anchor_size):
            anchor = needle[offset:offset + anchor_size]
            hit = stream.find(anchor, start_char)
            if hit < 0:
                hit = stream.find(anchor)
            if hit >= 0:
                anchor_hits.append((hit, offset))
        if anchor_hits:
            forward = [item for item in anchor_hits if item[0] - item[1] >= start_char]
            anchor_hit = min(forward or anchor_hits, key=lambda item: abs((item[0] - item[1]) - start_char))
            approximate = max(0, anchor_hit[0] - anchor_hit[1])
            window_start = max(0, approximate - max(100, len(needle) // 8))
            window_end = min(len(stream), approximate + max(500, int(len(needle) * 1.35)))
        else:
            window_start = start_char
            window_end = min(len(stream), window_start + max(2500, len(needle) * 2))
        matcher = SequenceMatcher(None, needle, stream[window_start:window_end], autojunk=False)
        blocks = [item for item in matcher.get_matching_blocks() if item.size]
        if blocks:
            first = min(blocks, key=lambda item: item.a)
            last_match = max(blocks, key=lambda item: item.a + item.size)
            match_start = window_start + first.b
            match_end = window_start + last_match.b + last_match.size
            score = sum(item.size for item in blocks) / max(1, len(needle))
            # Attribute only source blocks that contributed matched
            # characters.  The first-to-last-match envelope may contain a
            # running header and page number between two paragraph fragments.
            matched_ranges = [
                (window_start + item.b, window_start + item.b + item.size)
                for item in blocks if item.size >= 4
            ]
        else:
            match_start = window_start
            match_end = min(window_end, window_start + max(1, len(needle)))
            score = 0.0
            matched_ranges = [(match_start, match_end)]
    selected = [
        source_ids[i] for i, (left, right) in enumerate(boundaries)
        if any(right > range_left and left < range_right for range_left, range_right in matched_ranges)
    ]
    if not selected and source_ids:
        selected = [source_ids[min(cursor, len(source_ids) - 1)]]
    last = max((source_ids.index(item) for item in selected), default=cursor)
    return selected, round(score, 6), last


def library(stage_data: Path, book: str, singular: str) -> list[dict[str, Any]]:
    data = read_json(stage_data / "structured" / f"{book}_{singular}_library.json")
    return list(data[f"{singular}s"])


def attach_source_hashes(item: dict[str, Any], raw_by_id: dict[str, dict[str, Any]]) -> None:
    item["source_content_sha256"] = {
        source_id: raw_by_id[source_id]["content_sha256"]
        for source_id in item.get("source_block_ids") or []
        if source_id in raw_by_id
    }


def evidence_hash(item: dict[str, Any], master_hash: str, page_hashes: dict[int, str]) -> str:
    pages = item.get("source_pages") or ([item["source_page"]] if isinstance(item.get("source_page"), int) else [])
    payload = {
        "master_pdf_sha256": master_hash,
        "page_images": {str(page): page_hashes.get(page) for page in pages},
        "delivery_sha256": item.get("delivery_sha256") or item.get("content_sha256"),
        "source_block_ids": item.get("source_block_ids") or [],
        "source_bboxes": item.get("source_bboxes") or [],
        "source_content_sha256": item.get("source_content_sha256") or {},
    }
    return hash_json(payload)


def resource_delivery_text(kind: str, item: dict[str, Any]) -> str:
    """Expose the actual delivered object on per-page evidence sheets."""
    if kind == "formulas":
        return str(item.get("latex") or item.get("content") or "")
    if kind == "tables":
        return "\n".join(
            str(value) for value in (
                item.get("title"), item.get("source_note"),
                json.dumps(item.get("rows") or item.get("html") or [], ensure_ascii=False),
            ) if value
        )
    if kind == "figures":
        return str(item.get("caption") or item.get("title") or item.get("description") or item.get("asset_path") or "")
    return str(item.get("content_markdown") or item.get("content") or item.get("title") or "")


def source_exclusions(
    profile: dict[str, Any], raw_by_id: dict[str, dict[str, Any]], errors: list[str]
) -> dict[str, dict[str, Any]]:
    exclusions: dict[str, dict[str, Any]] = {}
    for entry in profile.get("source_block_exclusions") or []:
        source_id = str(entry.get("source_block_id") or "")
        source = raw_by_id.get(source_id)
        reason = str(entry.get("reason") or "").strip()
        bbox = entry.get("bbox")
        if not source or not reason or bbox != source.get("bbox"):
            errors.append(f"invalid or drifted source-block exclusion: {source_id or '[missing id]'}")
            continue
        if entry.get("source_content_sha256") != source.get("content_sha256"):
            errors.append(f"source-block exclusion content drifted: {source_id}")
            continue
        exclusions[source_id] = entry
    return exclusions


def persisted_build_findings(audit: Path) -> list[str]:
    path = audit / "reports" / "build_findings.json"
    if not path.is_file():
        return ["persisted build findings are missing"]
    payload = read_json(path)
    return [str(item) for item in payload.get("findings") or []]


def uncovered_source_blocks(
    raw_by_id: dict[str, dict[str, Any]], consumed: set[str],
    exclusions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return substantive source blocks that have no final delivery mapping."""
    return [
        row for key, row in raw_by_id.items()
        if key not in consumed and key not in exclusions
        and row["label"] in SUBSTANTIVE_LABELS
        and (row["content"] or row["label"] in {"image", "chart"})
    ]


def font(size: int) -> ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/consola.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def mono_font(size: int) -> ImageFont.ImageFont:
    for path in (Path("C:/Windows/Fonts/consola.ttf"), Path("C:/Windows/Fonts/cour.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return font(size)


def wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


PAGE_CONTACT_COLORS = [
    "#c62828", "#1565c0", "#2e7d32", "#9c5a00", "#7b1fa2", "#00838f",
    "#ad1457", "#455a64", "#6d4c41", "#5e35b1", "#0277bd", "#558b2f",
]


def page_contact(
    source: Path,
    page: int,
    rows: list[dict[str, Any]],
    target: Path,
    raw_by_id: dict[str, dict[str, Any]],
    source_size: tuple[float, float],
) -> None:
    """Render the canonical bbox-linked RAW LOCATOR / DELIVERY review sheet."""
    original = Image.open(source).convert("RGB")
    original.thumbnail((900, 1550))
    left_margin, top_margin, bottom_margin = 18, 58, 18
    left_width = original.width + left_margin * 2
    right_width = 1540
    body_font = mono_font(18)
    header_font = mono_font(22)
    line_height = 25

    rendered: list[tuple[str, str, ImageFont.ImageFont]] = [
        (f"PDF page {page} - original with source block boxes | structured delivery", "#111111", header_font)
    ]
    for index, row in enumerate(rows, 1):
        color = PAGE_CONTACT_COLORS[(index - 1) % len(PAGE_CONTACT_COLORS)]
        source_ids = list(row.get("source_block_ids") or [])
        locators = []
        raw_parts = []
        for source_id in source_ids:
            raw = raw_by_id.get(source_id)
            if not raw:
                continue
            block_id = source_id.rsplit(":b", 1)[-1]
            locators.append(f"p{raw['master_page']}:b{block_id}")
            raw_parts.append(str(raw.get("raw_content") or raw.get("content") or ""))
        source_label = ",".join(locators) if locators else "UNLOCATED"
        block_type = row.get("block_type") or "resource"
        rendered.append((
            f"[{index}] {row.get('unit_id')}#{row.get('block_index')}  type={block_type}  source={source_label}",
            color,
            body_font,
        ))
        if row.get("heading_path"):
            rendered.append(("HEADING: " + " > ".join(str(item) for item in row["heading_path"]), "#333333", body_font))
        raw_text = " | ".join(part.strip() for part in raw_parts if part.strip()) or "[no source text; inspect boxed asset]"
        for line in wrap_text("RAW LOCATOR: " + raw_text, 132):
            rendered.append((line, "#222222", body_font))
        for line in wrap_text("DELIVERY: " + str(row.get("content") or ""), 132):
            rendered.append((line, "#222222", body_font))
        rendered.append(("", "#222222", body_font))

    right_height = 22 + len(rendered) * line_height
    height = max(top_margin + original.height + bottom_margin, right_height)
    canvas = Image.new("RGB", (left_width + right_width, height), "white")
    canvas.paste(original, (left_margin, top_margin))
    draw = ImageDraw.Draw(canvas)
    draw.text((left_margin, 14), f"PDF page {page} - ORIGINAL", fill="#111111", font=header_font)

    raw_width, raw_height = source_size
    scale_x = original.width / max(1.0, raw_width)
    scale_y = original.height / max(1.0, raw_height)
    for index, row in enumerate(rows, 1):
        color = PAGE_CONTACT_COLORS[(index - 1) % len(PAGE_CONTACT_COLORS)]
        for source_id in row.get("source_block_ids") or []:
            raw = raw_by_id.get(source_id)
            if not raw or raw.get("master_page") != page:
                continue
            x0, y0, x1, y1 = raw["bbox"]
            box = (
                left_margin + int(x0 * scale_x), top_margin + int(y0 * scale_y),
                left_margin + int(x1 * scale_x), top_margin + int(y1 * scale_y),
            )
            draw.rectangle(box, outline=color, width=3)
            badge = (box[0], max(top_margin, box[1] - 24), box[0] + 31, max(top_margin, box[1] - 24) + 24)
            draw.rectangle(badge, fill="white", outline=color, width=2)
            draw.text((badge[0] + 4, badge[1] + 1), str(index), fill=color, font=mono_font(16))

    x = left_width + 18
    for line_index, (line, color, line_font) in enumerate(rendered):
        draw.text((x, 14 + line_index * line_height), line, fill=color, font=line_font)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, quality=93)


def crop(document: fitz.Document, raw_pages: dict[int, dict[str, Any]], page: int, box: list[float], target: Path, dpi: int = 180) -> None:
    pdf_page = document[page - 1]
    width, height = raw_dimensions(raw_pages[page])
    x0, y0, x1, y1 = box
    rect = fitz.Rect(max(0, x0 - 12) * pdf_page.rect.width / width, max(0, y0 - 12) * pdf_page.rect.height / height,
                     min(width, x1 + 12) * pdf_page.rect.width / width, min(height, y1 + 12) * pdf_page.rect.height / height) & pdf_page.rect
    target.parent.mkdir(parents=True, exist_ok=True)
    pdf_page.get_pixmap(clip=rect, dpi=dpi, alpha=False).save(target)


def contact_sheets(entries: list[tuple[str, Path]], target_dir: Path, per_sheet: int, cell: tuple[int, int]) -> list[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    for old in target_dir.glob("sheet_*.jpg"):
        old.unlink()
    result = []
    columns = 4 if per_sheet == 16 else 2
    rows = per_sheet // columns
    for offset in range(0, len(entries), per_sheet):
        canvas = Image.new("RGB", (columns * cell[0], rows * cell[1]), (225, 225, 225))
        for slot, (label, path) in enumerate(entries[offset:offset + per_sheet]):
            panel = Image.new("RGB", cell, "white")
            image = Image.open(path).convert("RGB")
            image.thumbnail((cell[0] - 16, cell[1] - 42))
            panel.paste(image, ((cell[0] - image.width) // 2, 34 + (cell[1] - 42 - image.height) // 2))
            ImageDraw.Draw(panel).text((8, 6), label, fill="black", font=font(17))
            canvas.paste(panel, ((slot % columns) * cell[0], (slot // columns) * cell[1]))
        path = target_dir / f"sheet_{offset // per_sheet + 1:03d}.jpg"
        canvas.save(path, quality=90)
        result.append(path)
    return result


def comparison_image(label: str, source_crop: Path | None, target: Path, *, delivery_image: Path | None = None, delivery_text: str = "") -> None:
    if source_crop and source_crop.is_file():
        source = Image.open(source_crop).convert("RGB")
        source.thumbnail((950, 900))
    else:
        source = Image.new("RGB", (950, 300), "white")
        ImageDraw.Draw(source).text((20, 20), "SOURCE CROP MISSING", fill="red", font=font(28))
    if delivery_image and delivery_image.exists():
        right = Image.open(delivery_image).convert("RGB")
        right.thumbnail((950, 900))
    else:
        lines = []
        for paragraph in delivery_text.splitlines() or [delivery_text]:
            lines.extend(wrap_text(paragraph, 90))
        height = max(300, 70 + len(lines) * 25)
        right = Image.new("RGB", (950, height), "white")
        draw = ImageDraw.Draw(right)
        for index, line in enumerate(lines):
            draw.text((15, 15 + index * 25), line, fill="black", font=font(18))
    height = max(source.height, right.height) + 45
    canvas = Image.new("RGB", (source.width + right.width, height), "white")
    canvas.paste(source, (0, 45))
    canvas.paste(right, (source.width, 45))
    ImageDraw.Draw(canvas).text((10, 8), f"{label} | master PDF crop (left) vs delivery (right)", fill="black", font=font(22))
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, quality=92)


def overlap_ratio(first: list[float], second: list[float]) -> float:
    x0, y0 = max(first[0], second[0]), max(first[1], second[1])
    x1, y1 = min(first[2], second[2]), min(first[3], second[3])
    intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    denominator = max(1.0, min((first[2] - first[0]) * (first[3] - first[1]), (second[2] - second[0]) * (second[3] - second[1])))
    return intersection / denominator


def protected_hashes(book: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((ROOT / "data").rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.name.startswith(f"{book}_"):
            continue
        if path.name in {"formula_library.json", "table_library.json", "figure_library.json", "example_library.json"}:
            # Shared libraries are protected entry-wise during install and are not installed by this implementation.
            continue
        result[rel] = sha256(path)
    return result


def book_delivery_binding(book: str, *, root: Path | None = None) -> dict[str, Any]:
    """Bind only the installed files owned by one book prefix."""
    base = root or ROOT
    paths = [
        path
        for relative_dir in ("structured", "figures", "textbook")
        for path in (base / "data" / relative_dir).rglob(f"{book}_*")
        if path.is_file()
    ]
    return bind_files(paths, base)


def installed_delivery_errors(book: str, audit: Path) -> list[str]:
    installation_path = audit / "reports" / "installation.json"
    if not installation_path.is_file():
        return []
    installation = read_json(installation_path)
    if not installation.get("installed"):
        return []
    expected = installation.get("delivery")
    if not expected:
        return ["installation report lacks a formal delivery hash binding; reinstall the book"]
    if expected != book_delivery_binding(book):
        return [f"installed {book} delivery differs from the transaction report"]
    return []


def load_status(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {kind: {} for kind in KINDS}
    value = read_json(path)
    return {kind: dict(value.get(kind) or {}) for kind in KINDS}


def validate_corrections(corrections: dict[str, Any], raw_by_id: dict[str, dict[str, Any]]) -> list[str]:
    errors = []
    required = {"source_block_id", "master_page", "chapter_page", "bbox", "original", "replacement", "reason", "source_content_sha256"}
    for index, item in enumerate(corrections.get("corrections") or [], 1):
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"correction {index} missing fields: {missing}")
            continue
        source = raw_by_id.get(str(item["source_block_id"]))
        if not source:
            errors.append(f"correction {index} source block drifted or is missing")
            continue
        if source["master_page"] != item["master_page"] or source["chapter_page"] != item["chapter_page"] or source["bbox"] != [float(x) for x in item["bbox"]]:
            errors.append(f"correction {index} page/bbox evidence drifted")
        if hash_bytes(source["content"].encode("utf-8")) != item["source_content_sha256"]:
            errors.append(f"correction {index} source content evidence drifted")
    return errors


def apply_structured_corrections(units: list[dict[str, Any]], corrections: dict[str, Any]) -> list[str]:
    errors = []
    by_id = {unit["id"]: unit for unit in units}
    for index, item in enumerate(corrections.get("corrections") or [], 1):
        operation = item.get("operation")
        if operation not in {"replace_block", "merge_adjacent_blocks", "replace_block_range"}:
            continue
        unit = by_id.get(item.get("unit_id"))
        if not unit:
            errors.append(f"correction {index} target unit is missing")
            continue
        block_index = item.get("block_index")
        if not isinstance(block_index, int) or not 0 <= block_index < len(unit.get("blocks") or []):
            errors.append(f"correction {index} target block drifted")
            continue
        if operation == "replace_block":
            actual = unit["blocks"][block_index].get("content")
            if actual == item["replacement"]:
                continue
            if actual != item["original"]:
                errors.append(f"correction {index} original delivery text drifted")
                continue
            unit["blocks"][block_index]["content"] = item["replacement"]
        elif operation == "merge_adjacent_blocks":
            originals = item["original"]
            if unit["blocks"][block_index].get("content") == item["replacement"]:
                continue
            actual = [block.get("content") for block in unit["blocks"][block_index:block_index + len(originals)]]
            if actual != originals:
                errors.append(f"correction {index} adjacent source blocks drifted")
                continue
            merged = dict(unit["blocks"][block_index])
            merged["content"] = item["replacement"]
            unit["blocks"][block_index:block_index + len(originals)] = [merged]
        else:
            originals = item["original"]
            replacement = item["replacement"]
            if [block_core(block) for block in unit["blocks"][block_index:block_index + len(replacement)]] == replacement:
                continue
            actual = [block_core(block) for block in unit["blocks"][block_index:block_index + len(originals)]]
            if actual != originals:
                errors.append(f"correction {index} structured block range drifted")
                continue
            unit["blocks"][block_index:block_index + len(originals)] = item["replacement"]
    return errors


def apply_table_corrections(stage_data: Path, book: str, corrections: dict[str, Any]) -> list[str]:
    path = stage_data / "structured" / f"{book}_table_library.json"
    data = read_json(path)
    errors = []
    for index, correction in enumerate(corrections.get("corrections") or [], 1):
        operation = correction.get("operation")
        if operation == "patch_table":
            matches = [item for item in data["tables"] if item.get("id") == correction.get("table_id") and (item.get("source") or {}).get("chapter") == correction.get("chapter")]
            if len(matches) == 1 and all(matches[0].get(key) == value for key, value in correction["replacement"].items()):
                continue
            if len(matches) != 1 or hash_json(matches[0]) != correction.get("original_delivery_sha256"):
                errors.append(f"correction {index} table delivery evidence drifted")
                continue
            matches[0].update(correction["replacement"])
        elif operation == "add_inline_table":
            entry = correction["table_entry"]
            existing = [item for item in data["tables"] if item.get("id") == entry["id"] and (item.get("source") or {}).get("chapter") == (entry.get("source") or {}).get("chapter")]
            if existing == [entry]:
                continue
            if existing:
                errors.append(f"correction {index} inline table already exists with different content")
                continue
            data["tables"].append(entry)
    write_json(path, data)
    return errors


def sync_status(status: dict[str, dict[str, Any]], ledgers: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    for kind, rows in ledgers.items():
        updated = {}
        for row in rows:
            key = str(row["review_key"])
            old = status.get(kind, {}).get(key, {})
            state = old.get("status", "pending")
            if old.get("evidence_sha256") != row["evidence_sha256"]:
                state = "stale" if old.get("status") == "verified" else "pending"
            updated[key] = {"status": state, "evidence_sha256": row["evidence_sha256"]}
        status[kind] = updated
    return status


def build(book: str, dpi: int) -> dict[str, Any]:
    profile, profile_path = profile_for(book)
    audit = AUDIT_ROOT / book
    if not inside(audit, AUDIT_ROOT):
        raise ValueError("audit path escapes tmp/book_audits")
    create_tree(audit)
    master, raw_pages, page_map = load_source(profile)
    master_hash = sha256(master)
    errors = render_and_compare(master, profile, page_map, audit, dpi)
    page_hashes = {item["master_page"]: item["page_image_sha256"] for item in page_map}
    raw_by_id, ids_by_chapter = normalize_layout(raw_pages, page_map, audit)
    write_json(audit / "source" / "chapter_page_map.json", page_map)

    stage_data = audit / "staging" / "data"
    if stage_data.exists():
        shutil.rmtree(stage_data)
    copy_delivery(book, stage_data)
    correction_profile = ROOT / "book_audits" / f"{book}_corrections.json"
    corrections = read_json(correction_profile) if correction_profile.exists() else {"schema": "book_corrections.v1", "book": book, "corrections": []}
    errors.extend(validate_corrections(corrections, raw_by_id))

    units = []
    for chapter in profile["chapters"]:
        units.extend(read_json(path) for path in sorted((stage_data / "structured").glob(f"{chapter['id']}_*.json")))
    errors.extend(apply_structured_corrections(units, corrections))
    for unit in units:
        write_json(stage_data / "structured" / f"{unit['id']}.json", unit)
    errors.extend(apply_table_corrections(stage_data, book, corrections))
    block_rows: list[dict[str, Any]] = []
    consumed: set[str] = set()
    cursor_by_chapter: dict[str, int] = defaultdict(int)
    seen_chapters: set[str] = set()
    unit_files = {path.stem: path for path in (stage_data / "structured").glob(f"{book}_*.json")}
    for unit in units:
        chapter = unit.get("metadata", {}).get("chapter")
        source_ids = ids_by_chapter.get(chapter, [])
        for index, block in enumerate(unit.get("blocks") or []):
            selected, score, cursor = span_for_content(block.get("content", ""), source_ids, raw_by_id, cursor_by_chapter[chapter])
            declared = explicit_source_ids(
                chapter,
                block.get("source_block_ids") or [],
                raw_by_id,
                ids_by_chapter,
            )
            if declared:
                selected = list(dict.fromkeys([*declared, *selected]))
                score = 1.0
                cursor = max(cursor, *(source_ids.index(source_id) for source_id in declared))
            cursor_by_chapter[chapter] = cursor
            if index == 0:
                anchor = source_ids.index(selected[0]) if selected else cursor
                headings = metadata_source_ids(unit, source_ids, raw_by_id, consumed, anchor)
                if chapter in seen_chapters:
                    headings = [
                        source_id for source_id in headings
                        if normalized(raw_by_id[source_id]["content"]) != normalized(
                            f"CHAPTER {re.search(r'(\d+)$', str(chapter)).group(1)}"
                        )
                    ]
                selected = list(dict.fromkeys([*headings, *selected]))
                seen_chapters.add(chapter)
            consumed.update(selected)
            pages = sorted({raw_by_id[item]["master_page"] for item in selected})
            boxes = [raw_by_id[item]["bbox"] for item in selected]
            delivery_hash = hash_json({"block": block, "metadata": unit.get("metadata") or {}})
            row = {
                "review_key": f"{unit['id']}:{index}", "unit_id": unit["id"], "block_index": index,
                "chapter": chapter,
                "block_type": block.get("type"), "content": block.get("content"),
                "heading_path": (unit.get("metadata") or {}).get("heading_path") or [],
                "source_page": pages[0] if pages else None, "source_pages": pages,
                "source_block_ids": selected, "source_bboxes": boxes,
                "provenance_score": score, "delivery_sha256": delivery_hash,
            }
            attach_source_hashes(row, raw_by_id)
            row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
            block_rows.append(row)
            block.update({
                "source_page": row["source_page"], "source_pages": pages,
                "source_block_ids": selected, "source_bboxes": boxes,
                "provenance_score": score, "content_sha256": hash_bytes(str(block.get("content") or "").encode("utf-8")),
            })
        write_json(unit_files[unit["id"]], unit)
    doc = fitz.open(master)
    ledgers: dict[str, list[dict[str, Any]]] = {kind: [] for kind in KINDS}
    formula_contacts: list[tuple[str, Path]] = []
    table_contacts: list[tuple[str, Path]] = []
    figure_contacts: list[tuple[str, Path]] = []
    chapter_by_id = {item["id"]: item for item in profile["chapters"]}
    try:
        for singular, target_rows, contacts, per_sheet in (
            ("formula", ledgers["formulas"], formula_contacts, 16),
            ("table", ledgers["tables"], table_contacts, 4),
            ("figure", ledgers["figures"], figure_contacts, 4),
        ):
            for item in library(stage_data, book, singular):
                chapter = item.get("chapter") or (item.get("source") or {}).get("chapter")
                evidence = item.get("source_evidence") or {}
                source_meta = item.get("source") or {}
                local_page = (
                    evidence.get("pdf_page") or source_meta.get("page")
                    if singular == "formula"
                    else source_meta.get("page") if singular == "table" else item.get("page")
                )
                page_modes = profile.get("resource_page_modes") or {}
                page_mode = page_modes.get(
                    f"{singular}s",
                    page_modes.get(singular, profile.get("resource_page_mode", "local")),
                )
                source_ids = resource_source_ids(
                    item, singular, chapter, raw_by_id, ids_by_chapter,
                    page_mode=page_mode,
                )
                if local_page is None and source_ids:
                    local_page = min(raw_by_id[source_id]["chapter_page"] for source_id in source_ids)
                if local_page is None and singular == "table":
                    marker = f"table{item.get('id')}".lower().replace(" ", "")
                    candidates = [
                        raw_by_id[source_id] for source_id in ids_by_chapter[chapter]
                        if marker in re.sub(r"\s+", "", raw_by_id[source_id]["content"].lower())
                        and raw_by_id[source_id]["label"] == "table"
                    ]
                    if len(candidates) == 1:
                        local_page = candidates[0]["chapter_page"]
                        item.setdefault("source", {})["page"] = local_page
                        item["source"]["bbox"] = candidates[0]["bbox"]
                        item["source"]["extraction_channel"] = "recovered_exact_raw_table_marker"
                        raw_html = candidates[0]["raw_content"]
                        item["title"] = "TABLE 6.2 Correlation between Uniting Gametes"
                        item["table_type"] = "numbered"
                        item["html"] = raw_html
                        item["rows"] = rows_from_html(raw_html)
                        item["description"] = None
                        item["source"].pop("needs_review", None)
                        item["source"].pop("reason", None)
                        library_path = stage_data / "structured" / f"{book}_table_library.json"
                        library_data = read_json(library_path)
                        for staged_item in library_data["tables"]:
                            if staged_item.get("id") == item.get("id") and (staged_item.get("source") or {}).get("chapter") == chapter:
                                staged_item.update(item)
                                break
                        write_json(library_path, library_data)
                    else:
                        errors.append(f"resource has no uniquely recoverable source page: {singular} {chapter}:{item.get('id')}")
                        continue
                if local_page is None:
                    errors.append(f"resource has no uniquely recoverable source page: {singular} {chapter}:{item.get('id')}")
                    continue
                chapter_profile = chapter_by_id[chapter]
                page_value = int(local_page)
                chapter_size = chapter_profile["master_end"] - chapter_profile["master_start"] + 1
                if page_mode == "master":
                    if not chapter_profile["master_start"] <= page_value <= chapter_profile["master_end"]:
                        errors.append(f"resource master page is outside its chapter: {singular} {chapter}:{item.get('id')} p{page_value}")
                        continue
                    master_page = page_value
                    local_page = page_value - chapter_profile["master_start"] + 1
                else:
                    if not 1 <= page_value <= chapter_size:
                        errors.append(f"resource local page is outside its chapter: {singular} {chapter}:{item.get('id')} p{page_value}")
                        continue
                    master_page = chapter_profile["master_start"] + page_value - 1
                explicit_pages = item.get("source_pages") or evidence.get("source_pages") or source_meta.get("source_pages") or []
                master_pages = []
                for value in explicit_pages:
                    page_value = int(value)
                    if page_mode != "master" and 1 <= page_value <= chapter_size:
                        page_value = chapter_profile["master_start"] + page_value - 1
                    master_pages.append(page_value)
                master_pages = sorted(set(master_pages or [master_page]))
                box = (
                    evidence.get("formula_bbox") or source_meta.get("bbox")
                    if singular == "formula"
                    else source_meta.get("bbox") if singular == "table" else item.get("raw_bbox")
                )
                explicit_boxes = item.get("source_bboxes") or evidence.get("source_bboxes") or source_meta.get("source_bboxes") or []
                boxes = explicit_boxes if explicit_boxes else ([box] if box else [])
                if not box and source_ids:
                    page_boxes = [
                        raw_by_id[source_id]["bbox"] for source_id in source_ids
                        if raw_by_id[source_id]["chapter_page"] == int(local_page)
                        and raw_by_id[source_id].get("bbox")
                    ]
                    if page_boxes:
                        box = [
                            min(value[0] for value in page_boxes), min(value[1] for value in page_boxes),
                            max(value[2] for value in page_boxes), max(value[3] for value in page_boxes),
                        ]
                        boxes = page_boxes
                if box and not source_ids:
                    for source_id in ids_by_chapter[chapter]:
                        source = raw_by_id[source_id]
                        if source["master_page"] in master_pages and source["bbox"] and overlap_ratio(source["bbox"], [float(x) for x in box]) >= 0.45:
                            source_ids.append(source_id)
                if box:
                    crop_path = audit / "evidence" / "crops" / f"{singular}s" / f"{chapter}_{item['id']}.png"
                    crop(doc, raw_pages, master_page, [float(x) for x in box], crop_path)
                else:
                    crop_path = None
                if source_ids:
                    master_pages = sorted(set(master_pages) | {raw_by_id[source_id]["master_page"] for source_id in source_ids})
                    boxes = boxes or [raw_by_id[source_id]["bbox"] for source_id in source_ids]
                consumed.update(source_ids)
                delivery_hash = hash_json(item)
                row = {
                    "review_key": f"{chapter}:{item['id']}", "id": item["id"], "chapter": chapter,
                    "source_page": master_pages[0], "source_pages": master_pages, "chapter_page": local_page,
                    "source_block_ids": source_ids, "source_bboxes": boxes,
                    "source_crop": str(crop_path.relative_to(ROOT)) if crop_path else None,
                    "delivery_sha256": delivery_hash, "delivery_content": resource_delivery_text(f"{singular}s", item),
                }
                if not source_ids:
                    errors.append(f"resource lacks source-block provenance: {singular} {chapter}:{item.get('id')}")
                if singular == "figure":
                    asset = stage_data / str(item.get("asset_path"))
                    textbook_asset = stage_data / "textbook" / "figures" / asset.name
                    row["asset"] = str(asset.relative_to(ROOT))
                    row["asset_sha256"] = sha256(asset) if asset.exists() else None
                    row["textbook_asset_sha256"] = sha256(textbook_asset) if textbook_asset.exists() else None
                    row["delivery_sha256"] = hash_json({"metadata": item, "asset_sha256": row["asset_sha256"], "textbook_asset_sha256": row["textbook_asset_sha256"]})
                    if row["asset_sha256"] != row["textbook_asset_sha256"] or not row["asset_sha256"]:
                        errors.append(f"figure asset missing or differs: {item['id']}")
                    compare = audit / "evidence" / "figure_pairs" / f"{chapter}_{item['id']}.jpg"
                    comparison_image(f"{chapter}:{item['id']} p{master_page}", crop_path, compare, delivery_image=asset)
                elif singular == "formula":
                    compare = audit / "evidence" / "crops" / "formulas" / f"{chapter}_{item['id']}_comparison.jpg"
                    comparison_image(f"{chapter}:{item['id']} p{master_page}", crop_path, compare, delivery_text=str(item.get("latex") or ""))
                else:
                    compare = audit / "evidence" / "crops" / "tables" / f"{chapter}_{item['id']}_comparison.jpg"
                    comparison_image(f"{chapter}:{item['id']} p{master_page}", crop_path, compare, delivery_text=json.dumps(item.get("rows") or item.get("html"), ensure_ascii=False, indent=2))
                contacts.append((f"{chapter}:{item['id']} p{master_page}", compare))
                attach_source_hashes(row, raw_by_id)
                row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
                target_rows.append(row)
    finally:
        doc.close()

    export_textbooks(
        structured_dir=stage_data / "structured", out_dir=stage_data / "textbook",
        books={book}, book_id=book,
    )
    for path in (stage_data / "textbook").glob(f"{book}_*_textbook.md"):
        content = path.read_text(encoding="utf-8").replace("](../structured/figures/", "](figures/")
        path.write_text(content, encoding="utf-8")

    formal_examples = library(stage_data, book, "example")
    if formal_examples:
        for item in formal_examples:
            chapter = str(item.get("chapter") or (item.get("source") or {}).get("chapter") or "")
            raw_candidates = [str(value) for value in (item.get("source_block_ids") or item.get("block_ids") or [])]
            source_ids = explicit_source_ids(chapter, raw_candidates, raw_by_id, ids_by_chapter)
            pages = sorted({raw_by_id[source_id]["master_page"] for source_id in source_ids})
            if not pages:
                local_page = (item.get("metadata") or {}).get("source_page") or ((item.get("evidence") or {}).get("lower_rule") or {}).get("page")
                chapter_profile = chapter_by_id.get(chapter)
                if isinstance(local_page, int) and chapter_profile:
                    if local_page in raw_pages:
                        pages = [local_page]
                    elif 1 <= local_page <= chapter_profile["master_end"] - chapter_profile["master_start"] + 1:
                        pages = [chapter_profile["master_start"] + local_page - 1]
            if not source_ids:
                example_label = item.get("label") or item.get("title")
                if not example_label:
                    reference = str(item.get("example_id") or item.get("example_ref") or item.get("id") or "")
                    example_label = f"Example {reference.rsplit(':', 1)[-1]}"
                marker = normalized(example_label)
                candidates = [
                    source_id for source_id in ids_by_chapter.get(chapter, [])
                    if marker and marker in normalized(raw_by_id[source_id]["content"])
                ]
                if candidates:
                    first = candidates[0]
                    first_index = ids_by_chapter[chapter].index(first)
                    delivery = normalized(item.get("content_markdown") or item.get("content_plain") or "")
                    for source_id in ids_by_chapter[chapter][first_index:]:
                        source = raw_by_id[source_id]
                        if source_id != first and normalized(source["content"]).startswith("example"):
                            break
                        needle = normalized(source["content"])
                        if source_id == first or (len(needle) >= 6 and needle in delivery):
                            source_ids.append(source_id)
                    pages = sorted({raw_by_id[source_id]["master_page"] for source_id in source_ids})
            row = {
                "review_key": str(item.get("example_id") or item.get("example_ref") or item.get("id")),
                "id": str(item.get("example_id") or item.get("example_ref") or item.get("id")),
                "chapter": chapter, "formal_resource": True,
                "source_page": pages[0] if pages else None, "source_pages": pages,
                "source_block_ids": source_ids,
                "source_bboxes": [raw_by_id[source_id]["bbox"] for source_id in source_ids],
                "source_file": item.get("source_file"), "end_source_file": item.get("end_source_file"),
                "delivery_sha256": hash_json(item), "delivery_content": resource_delivery_text("examples", item),
            }
            attach_source_hashes(row, raw_by_id)
            row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
            ledgers["examples"].append(row)
    else:
        # The evidence row proves absence but is deliberately excluded from the formal Example count.
        example_absence = {
            "review_key": f"{book}:no_formal_examples", "id": "no_formal_examples", "formal_resource": False,
            "source_pages": sorted(raw_pages), "source_block_ids": [key for key, row in raw_by_id.items() if "example" in row["content"].lower()],
            "source_bboxes": [], "delivery_sha256": hash_json({"examples": 0, "pages": sorted(raw_pages)}),
            "conclusion": "No formally delimited Example resources are present in the audited source pages; mentions of examples in prose are not formal Example blocks.",
        }
        attach_source_hashes(example_absence, raw_by_id)
        example_absence["evidence_sha256"] = evidence_hash(example_absence, master_hash, page_hashes)
        ledgers["examples"] = [example_absence]

    # Placeholder blocks intentionally contain no source prose of their own.
    # Their provenance is exactly the provenance of the formal resource they
    # reference, so propagate it before applying the generic resource mapping.
    resources_by_marker: dict[str, dict[str, Any]] = {}
    for kind in ("formulas", "tables", "figures", "examples"):
        singular = kind[:-1]
        for resource in ledgers[kind]:
            if kind == "examples" and not resource.get("formal_resource"):
                continue
            resources_by_marker[f"[[{singular.upper()}:{resource['id']}]]"] = resource
            resources_by_marker[f"[[SEE_{singular.upper()}:{resource['id']}]]"] = resource
    for row in block_rows:
        content = str(row.get("content") or "")
        matched = [resource for marker, resource in resources_by_marker.items() if marker in content]
        if not matched:
            continue
        source_ids = list(dict.fromkeys(
            [*(row.get("source_block_ids") or [])]
            + [source_id for resource in matched for source_id in resource.get("source_block_ids") or []]
        ))
        if not source_ids:
            continue
        row["source_block_ids"] = source_ids
        row["source_pages"] = sorted({raw_by_id[source_id]["master_page"] for source_id in source_ids})
        row["source_page"] = row["source_pages"][0]
        row["source_bboxes"] = [raw_by_id[source_id]["bbox"] for source_id in source_ids]
        row["provenance_score"] = 1.0
        attach_source_hashes(row, raw_by_id)
        row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
        consumed.update(source_ids)

    resource_by_placeholder: dict[str, dict[str, Any]] = {}
    for kind in ("formulas", "tables", "figures", "examples"):
        singular = kind[:-1]
        for row in ledgers[kind]:
            if kind == "examples" and not row.get("formal_resource"):
                continue
            resource_by_placeholder[f"[[{singular.upper()}:{row['id']}]]"] = row
            resource_by_placeholder[f"[[SEE_{singular.upper()}:{row['id']}]]"] = row
    for row in block_rows:
        matches = [resource for marker, resource in resource_by_placeholder.items() if marker in str(row.get("content") or "")]
        if not matches:
            continue
        source_ids = sorted(
            set(row.get("source_block_ids") or [])
            | {source_id for resource in matches for source_id in resource.get("source_block_ids") or []}
        )
        if not source_ids:
            continue
        row["source_block_ids"] = source_ids
        row["source_pages"] = sorted({raw_by_id[source_id]["master_page"] for source_id in source_ids})
        row["source_page"] = row["source_pages"][0]
        row["source_bboxes"] = [raw_by_id[source_id]["bbox"] for source_id in source_ids]
        row["provenance_score"] = 1.0
        attach_source_hashes(row, raw_by_id)
        row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
        consumed.update(source_ids)
        unit = next(item for item in units if item["id"] == row["unit_id"])
        unit["blocks"][row["block_index"]].update({
            "source_page": row["source_page"], "source_pages": row["source_pages"],
            "source_block_ids": row["source_block_ids"], "source_bboxes": row["source_bboxes"],
            "provenance_score": row["provenance_score"],
        })
        write_json(unit_files[unit["id"]], unit)

    # Visual blocks contained inside a formally delimited Example may not have
    # standalone figure captions (worked scatterplots and probability plots
    # are common).  Associate them with that Example only when their bbox lies
    # inside the same PDF rule box recorded by the extractor.  This preserves
    # the actual visual evidence without pretending it is a numbered figure.
    for row in ledgers["examples"]:
        if not row.get("formal_resource"):
            continue
        item = next(
            (
                candidate for candidate in formal_examples
                if str(candidate.get("example_id") or candidate.get("example_ref") or candidate.get("id")) == row["id"]
                and str(candidate.get("chapter") or "") == str(row.get("chapter") or "")
            ),
            None,
        )
        if not item:
            continue
        chapter = str(row.get("chapter") or "")
        chapter_profile = chapter_by_id.get(chapter)
        if not chapter_profile:
            continue
        for source_id in example_boundary_source_ids(
            item, row, chapter_profile, raw_by_id, ids_by_chapter.get(chapter, []),
        ):
            row["source_block_ids"] = list(dict.fromkeys([*(row.get("source_block_ids") or []), source_id]))
            consumed.add(source_id)
        if row.get("source_block_ids"):
            row["source_pages"] = sorted({raw_by_id[item]["master_page"] for item in row["source_block_ids"]})
            row["source_page"] = row["source_pages"][0]
            row["source_bboxes"] = [raw_by_id[item]["bbox"] for item in row["source_block_ids"]]
            attach_source_hashes(row, raw_by_id)
            row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)

    # Bind source fragments that are already delivered verbatim but were not
    # selected by the sequential paragraph matcher (notably page continuations
    # and compact OCR table rows).  The mapping is still exact and local to the
    # same chapter; no fuzzy acceptance is introduced.
    bindable_rows = [*block_rows]
    for kind in ("formulas", "tables", "figures", "examples"):
        bindable_rows.extend(
            row for row in ledgers[kind]
            if kind != "examples" or row.get("formal_resource")
        )
    for source_id, source in raw_by_id.items():
        if source_id in consumed:
            continue
        needle = normalized(source.get("content"))
        if len(needle) < 6:
            continue
        candidates = []
        for row in bindable_rows:
            if row.get("chapter") != source.get("chapter"):
                continue
            delivery = normalized(row.get("content") or row.get("delivery_content") or "")
            if needle in delivery:
                candidates.append((len(delivery) - len(needle), row))
        if not candidates:
            continue
        row = min(candidates, key=lambda value: value[0])[1]
        row["source_block_ids"] = list(dict.fromkeys([*(row.get("source_block_ids") or []), source_id]))
        row["source_pages"] = sorted(
            set(row.get("source_pages") or []) | {raw_by_id[item]["master_page"] for item in row["source_block_ids"]}
        )
        row["source_page"] = row["source_pages"][0]
        row["source_bboxes"] = [raw_by_id[item]["bbox"] for item in row["source_block_ids"]]
        if "provenance_score" in row:
            row["provenance_score"] = max(1.0, float(row["provenance_score"]))
        attach_source_hashes(row, raw_by_id)
        row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
        consumed.add(source_id)

    # Bind short equation connectors ("where", "then", "hence", ...)
    # to the immediately following displayed formula on the same page.  OCR
    # frequently emits these as isolated text blocks even though the formal
    # delivery correctly keeps the connector with the equation paragraph.
    connector_words = {"where", "then", "hence", "thus", "while"}
    formula_owners = {
        source_id: row
        for row in [*block_rows, *ledgers["formulas"], *ledgers["examples"]]
        for source_id in row.get("source_block_ids") or []
    }
    for chapter, chapter_ids in ids_by_chapter.items():
        for index, source_id in enumerate(chapter_ids[:-1]):
            if source_id in consumed:
                continue
            source = raw_by_id[source_id]
            if normalized(source.get("content")) not in connector_words:
                continue
            next_id = next(
                (
                    candidate for candidate in chapter_ids[index + 1:]
                    if raw_by_id[candidate]["master_page"] == source["master_page"]
                    and raw_by_id[candidate]["label"] not in {"header", "number", "formula_number"}
                ),
                None,
            )
            if not next_id or raw_by_id[next_id]["label"] not in {"display_formula", "inline_formula"}:
                continue
            owner = formula_owners.get(next_id)
            if not owner:
                continue
            owner["source_block_ids"] = list(dict.fromkeys([*(owner.get("source_block_ids") or []), source_id]))
            owner["source_pages"] = sorted({raw_by_id[item]["master_page"] for item in owner["source_block_ids"]})
            owner["source_page"] = owner["source_pages"][0]
            owner["source_bboxes"] = [raw_by_id[item]["bbox"] for item in owner["source_block_ids"]]
            attach_source_hashes(owner, raw_by_id)
            owner["evidence_sha256"] = evidence_hash(owner, master_hash, page_hashes)
            consumed.add(source_id)

    # A correction ledger is itself a formal source-to-delivery mapping.  Add
    # its exact IDs to the affected block/resource row so page sheets expose
    # the evidence rather than merely suppressing an uncovered finding.
    for correction in corrections.get("corrections") or []:
        correction_ids = [
            source_id for source_id in [
                correction.get("source_block_id"),
                *(correction.get("additional_source_block_ids") or []),
            ] if source_id in raw_by_id
        ]
        if not correction_ids:
            continue
        targets = []
        if correction.get("unit_id"):
            targets = [row for row in block_rows if row.get("unit_id") == correction["unit_id"]]
            if isinstance(correction.get("block_index"), int):
                exact = [row for row in targets if row.get("block_index") == correction["block_index"]]
                targets = exact or targets
        table_id = correction.get("table_id") or (correction.get("table_entry") or {}).get("id")
        if table_id:
            targets.extend(row for row in ledgers["tables"] if row.get("id") == table_id)
        if not targets:
            continue
        target = targets[0]
        target["source_block_ids"] = list(dict.fromkeys([*(target.get("source_block_ids") or []), *correction_ids]))
        target["source_pages"] = sorted({raw_by_id[item]["master_page"] for item in target["source_block_ids"]})
        target["source_page"] = target["source_pages"][0]
        target["source_bboxes"] = [raw_by_id[item]["bbox"] for item in target["source_block_ids"]]
        if "provenance_score" in target:
            target["provenance_score"] = 1.0
        attach_source_hashes(target, raw_by_id)
        target["evidence_sha256"] = evidence_hash(target, master_hash, page_hashes)
        consumed.update(correction_ids)

    for row in block_rows:
        unit = next(item for item in units if item["id"] == row["unit_id"])
        unit["blocks"][row["block_index"]].update({
            "source_page": row["source_page"], "source_pages": row["source_pages"],
            "source_block_ids": row["source_block_ids"], "source_bboxes": row["source_bboxes"],
            "provenance_score": row["provenance_score"],
        })
        write_json(unit_files[unit["id"]], unit)
    low_provenance = [row["review_key"] for row in block_rows if row["provenance_score"] < 0.5 or not row["source_block_ids"]]
    if low_provenance:
        # Coverage of an extracted block is judged by exact source locators.
        # The similarity score remains useful diagnostic metadata but can be
        # low for PDF-corrected text without indicating missing provenance.
        no_source = [row for row in block_rows if not row["source_block_ids"]]
        if no_source:
            errors.append(f"structured blocks with insufficient source provenance: {len(no_source)}")
    exclusions = source_exclusions(profile, raw_by_id, errors)

    uncovered = uncovered_source_blocks(raw_by_id, consumed, exclusions)
    write_json(audit / "reports" / "uncovered_source_blocks.json", uncovered)
    if uncovered:
        errors.append(f"substantive Paddle source blocks remain uncovered: {len(uncovered)}")

    page_blocks: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in block_rows:
        for page in row["source_pages"]:
            page_blocks[page].append(row)
    page_resources: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for kind in ("formulas", "tables", "figures", "examples"):
        for resource in ledgers[kind]:
            if kind == "examples" and not resource.get("formal_resource"):
                continue
            if resource.get("source_page") is None:
                continue
            for resource_page in resource.get("source_pages") or [resource["source_page"]]:
                page_resources[resource_page].append({
                    "unit_id": f"RESOURCE {kind[:-1].upper()}:{resource['id']}",
                    "block_index": "asset", "provenance_score": 1.0,
                    "block_type": kind[:-1],
                    "heading_path": [resource["chapter"]],
                    "source_block_ids": resource.get("source_block_ids") or [],
                    "source_bboxes": resource.get("source_bboxes") or [],
                    "content": resource.get("delivery_content") or "[empty resource delivery]",
                    "delivery_sha256": resource["evidence_sha256"],
                })
    for item in page_map:
        page = item["master_page"]
        delivery_rows = page_blocks[page] + page_resources[page]
        represented = {
            source_id for delivery in delivery_rows
            for source_id in delivery.get("source_block_ids") or []
            if raw_by_id.get(source_id, {}).get("master_page") == page
        }
        page_source_ids = [source_id for source_id, source in raw_by_id.items() if source["master_page"] == page]
        for source_id in page_source_ids:
            if source_id in represented:
                continue
            source = raw_by_id[source_id]
            exclusion = exclusions.get(source_id)
            status = "EXCLUDED" if exclusion else "MISSING"
            reason = f" — {exclusion['reason']}" if exclusion else " — source block has no delivery mapping"
            delivery_rows.append({
                "unit_id": f"SOURCE {source_id}", "block_index": "source",
                "provenance_score": 1.0 if exclusion else 0.0,
                "block_type": source.get("label") or "source",
                "source_block_ids": [source_id], "source_bboxes": [source.get("bbox")],
                "content": status + reason,
                "delivery_sha256": hash_json({"status": status, "reason": reason, "source": source_id}),
            })
        row = {
            "review_key": str(page), "master_page": page, "chapter": item["chapter"],
            "chapter_page": item["chapter_page"], "source_pages": [page],
            "source_block_ids": page_source_ids,
            "source_bboxes": [source["bbox"] for source in raw_by_id.values() if source["master_page"] == page],
            "delivery_sha256": hash_json([block["delivery_sha256"] for block in delivery_rows]),
            "page_image": f"source/pages/page_{page:04d}.png",
        }
        attach_source_hashes(row, raw_by_id)
        row["evidence_sha256"] = evidence_hash(row, master_hash, page_hashes)
        ledgers["pages"].append(row)
        page_contact(
            audit / row["page_image"], page, delivery_rows,
            audit / "evidence" / "page_contacts" / f"sheet_{len(ledgers['pages']):03d}.jpg",
            raw_by_id, raw_dimensions(raw_pages[page]),
        )
    ledgers["blocks"] = block_rows

    contact_sheets(formula_contacts, audit / "evidence" / "contacts" / "formulas", 16, (500, 250))
    contact_sheets(table_contacts, audit / "evidence" / "contacts" / "tables", 4, (750, 700))
    contact_sheets(figure_contacts, audit / "evidence" / "contacts" / "figures", 4, (750, 600))
    example_sheet = Image.new("RGB", (1400, max(500, 115 + 42 * len(ledgers["examples"]))), "white")
    draw = ImageDraw.Draw(example_sheet)
    draw.text((30, 25), f"{book} formal Example review", fill="black", font=font(30))
    y = 85
    if formal_examples:
        for row in ledgers["examples"]:
            draw.text((30, y), f"{row['id']} | page(s) {row['source_pages']} | {row.get('source_file')}", fill="black", font=font(22))
            y += 42
    else:
        for line in wrap_text(example_absence["conclusion"], 100):
            draw.text((30, y), line, fill="black", font=font(22))
            y += 34
        draw.text((30, y + 20), f"Audited master pages: {len(raw_pages)}; keyword candidates: {len(example_absence['source_block_ids'])}", fill="black", font=font(22))
    example_sheet.save(audit / "evidence" / "contacts" / "examples" / "sheet_001.jpg", quality=92)

    for kind, rows in ledgers.items():
        write_json(audit / "ledgers" / f"{kind}.json", rows)
    status_path = audit / "review" / "status.json"
    status = sync_status(load_status(status_path), ledgers)
    write_json(status_path, status)
    events = audit / "review" / "events.jsonl"
    events.touch(exist_ok=True)

    write_json(audit / "corrections" / "applied_corrections.json", corrections)
    write_json(audit / "reports" / "build_findings.json", {
        "schema": "book_accuracy_build_findings.v2",
        "book": book,
        "findings": sorted(set(errors)),
    })
    input_paths = [profile_path, AUDIT_SCRIPT, EXPORTER_SCRIPT, master, *master_part_paths(profile)]
    if correction_profile.is_file():
        input_paths.append(correction_profile)
    input_paths.extend(ROOT / item["slice_pdf"] for item in page_map)
    input_paths.extend(ROOT / item["raw_response"] for item in page_map)
    manifest = {
        "schema": MANIFEST_SCHEMA, "book": book, "built_at_utc": utcnow(),
        "profile": str(profile_path.relative_to(ROOT)), "profile_sha256": sha256(profile_path),
        "master_pdf": str(master.relative_to(ROOT)), "master_pdf_sha256": master_hash,
        "master_pdf_parts": [str(path.relative_to(ROOT)) for path in master_part_paths(profile)],
        "master_page_count": int(profile["master_page_count"]),
        "page_count": len(page_map), "legacy_inputs": profile.get("legacy_inputs", []),
        "render": {"renderer": "PyMuPDF", "dpi": dpi, "pixel_format": "RGB", "alpha": False},
        "tool_versions": {
            "python": platform.python_version(),
            "pymupdf": getattr(fitz, "VersionBind", "unknown"),
        },
        "inputs": bind_files(input_paths, ROOT),
        "artifacts": {
            "source": bind_tree(audit / "source"),
            "evidence": bind_tree(audit / "evidence"),
            "ledgers": bind_tree(audit / "ledgers"),
            "staging": bind_tree(audit / "staging" / "data"),
            "corrections": bind_tree(audit / "corrections"),
        },
    }
    (audit / "reports" / "installation.json").unlink(missing_ok=True)
    write_json(audit / "manifest.json", manifest)
    write_json(audit / "reports" / "protected_hashes.json", protected_hashes(book))
    return verify(book)


def verification_report(
    book: str,
    counts: dict[str, int],
    optional_spot_check_pending: dict[str, int],
    errors: list[str],
) -> dict[str, Any]:
    """Create a report whose pass/fail state depends only on automatic findings."""
    unique_errors = sorted(set(errors))
    return {
        "schema": "book_accuracy_verification.v1",
        "book": book,
        "verified_at_utc": utcnow(),
        "valid": not unique_errors,
        "automated_valid": not unique_errors,
        "counts": counts,
        "optional_spot_check_pending": optional_spot_check_pending,
        "errors": unique_errors,
    }


def expected_count_errors(counts: dict[str, int], baseline: dict[str, int]) -> list[str]:
    aliases = {"tables": "logical_tables"}
    errors = []
    for expected_key, expected_value in baseline.items():
        actual_key = aliases.get(expected_key, expected_key)
        if actual_key not in counts:
            errors.append(f"missing audited count: {actual_key}")
        elif counts[actual_key] != expected_value:
            errors.append(f"wrong {actual_key} count: {counts[actual_key]} != {expected_value}")
    return errors


def formal_example_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row.get("formal_resource", row.get("id") != "no_formal_examples"))


def audit_status(book: str, *, audit_root: Path = AUDIT_ROOT, profile_root: Path | None = None) -> dict[str, Any]:
    """Read existing reports without rebuilding evidence or mutating audit state."""
    book = safe_book(book)
    profile_dir = profile_root or (ROOT / "book_audits")
    audit = audit_root / book
    verification_path = audit / "reports" / "verification.json"
    installation_path = audit / "reports" / "installation.json"
    verification = read_json(verification_path) if verification_path.is_file() else {}
    installation = read_json(installation_path) if installation_path.is_file() else {}
    built = (audit / "manifest.json").is_file()
    automated_valid = bool(verification.get("automated_valid", verification.get("valid", False))) if verification else None
    installed = bool(installation.get("installed", False))
    waived = bool(installation.get("automatic_findings_waived", False))
    if not built:
        next_action = f"python scripts/audit_book_accuracy.py build --book {book}"
    elif not verification:
        next_action = f"python scripts/audit_book_accuracy.py verify --book {book}"
    elif not automated_valid:
        next_action = "resolve automatic findings, or install only with an explicit documented waiver"
    elif not installed:
        next_action = f"python scripts/audit_book_accuracy.py install --book {book}"
    else:
        next_action = f"optional spot check, then build and verify Pack/{book}Pack"
    return {
        "schema": "book_accuracy_status.v1", "book": book,
        "profile_exists": (profile_dir / f"{book}.json").is_file(), "built": built,
        "verification_exists": bool(verification), "automated_valid": automated_valid,
        "findings": list(verification.get("errors") or []), "installed": installed,
        "automatic_findings_waived": waived,
        "waived_findings": list(installation.get("waived_findings") or []),
        "optional_spot_check_pending": dict(verification.get("optional_spot_check_pending") or {}),
        "next_action": next_action,
    }


def verify(
    book: str,
    build_errors: list[str] | None = None,
    *,
    check_installed_delivery: bool = True,
) -> dict[str, Any]:
    profile, _ = profile_for(book)
    audit = AUDIT_ROOT / book
    errors: list[str] = []
    if not (audit / "manifest.json").exists():
        errors.append("audit has not been built")
        report = {"valid": False, "automated_valid": False, "errors": errors}
        return report
    if build_errors is not None:
        write_json(audit / "reports" / "build_findings.json", {
            "schema": "book_accuracy_build_findings.v2", "book": book,
            "findings": sorted(set(build_errors)),
        })
    manifest = read_json(audit / "manifest.json")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        errors.append(f"audit manifest must be rebuilt with {MANIFEST_SCHEMA}")
    errors.extend(persisted_build_findings(audit))
    errors.extend(binding_errors(manifest.get("inputs") or {}, ROOT, "input"))
    audit_script_key = AUDIT_SCRIPT.relative_to(ROOT).as_posix()
    if (manifest.get("inputs") or {}).get("files", {}).get(audit_script_key) != sha256(AUDIT_SCRIPT):
        errors.append("audit implementation differs from the build environment")
    exporter_script_key = EXPORTER_SCRIPT.relative_to(ROOT).as_posix()
    if (manifest.get("inputs") or {}).get("files", {}).get(exporter_script_key) != sha256(EXPORTER_SCRIPT):
        errors.append("textbook exporter differs from the build environment")
    artifact_roots = {
        "source": audit / "source",
        "evidence": audit / "evidence",
        "ledgers": audit / "ledgers",
        "staging": audit / "staging" / "data",
        "corrections": audit / "corrections",
    }
    for label, root in artifact_roots.items():
        binding = (manifest.get("artifacts") or {}).get(label)
        if not binding:
            errors.append(f"missing {label} artifact binding")
        else:
            errors.extend(tree_binding_errors(binding, root, label))
    tools = manifest.get("tool_versions") or {}
    if tools.get("python") != platform.python_version() or tools.get("pymupdf") != getattr(fitz, "VersionBind", "unknown"):
        errors.append("audit tool versions differ from the build environment")
    master = ROOT / manifest["master_pdf"]
    if not master.exists() or sha256(master) != manifest["master_pdf_sha256"]:
        errors.append("master PDF hash changed; all evidence is stale")
    elif manifest.get("master_pdf_sha256") != profile.get("master_pdf_sha256"):
        errors.append("manifest master PDF differs from the v2 profile")
    ledgers = {kind: read_json(audit / "ledgers" / f"{kind}.json") for kind in KINDS}
    page_map = read_json(audit / "source" / "chapter_page_map.json")
    page_hashes = {int(item["master_page"]): item["page_image_sha256"] for item in page_map}
    for kind, rows in ledgers.items():
        for row in rows:
            expected_evidence = evidence_hash(row, manifest.get("master_pdf_sha256", ""), page_hashes)
            if row.get("evidence_sha256") != expected_evidence:
                errors.append(f"{kind} evidence digest mismatch: {row.get('review_key')}")
    status = load_status(audit / "review" / "status.json")
    pending: dict[str, int] = {}
    for kind, rows in ledgers.items():
        count = 0
        for row in rows:
            entry = status[kind].get(str(row["review_key"]))
            if not entry or entry.get("status") != "verified" or entry.get("evidence_sha256") != row["evidence_sha256"]:
                count += 1
        pending[kind] = count
    # Human review is retained only as optional post-install spot-check metadata.
    # Missing, rejected, or stale review entries must never affect ``valid``.

    counts = {
        "pages": len(ledgers["pages"]),
        "units": len([path for path in (audit / "staging" / "data" / "structured").glob(f"{book}_*.json") if re.search(r"_\d{3}\.json$", path.name)]),
        "blocks": len(ledgers["blocks"]),
        "formulas": len(ledgers["formulas"]), "logical_tables": len(ledgers["tables"]),
        "figures": len(ledgers["figures"]),
        "examples": formal_example_count(ledgers["examples"]),
    }
    expected = profile["baseline_counts"]
    errors.extend(expected_count_errors(counts, expected))
    if any(not row["source_block_ids"] or not row["source_bboxes"] for row in ledgers["blocks"]):
        errors.append("one or more structured blocks lacks page/bbox provenance")
    uncovered_path = audit / "reports" / "uncovered_source_blocks.json"
    if uncovered_path.exists():
        still_uncovered = read_json(uncovered_path)
        if still_uncovered:
            errors.append(f"substantive Paddle source blocks remain uncovered: {len(still_uncovered)}")

    stage_data = audit / "staging" / "data"
    for path in sorted((stage_data / "textbook").glob(f"{book}_*_textbook.md")):
        content = path.read_text(encoding="utf-8")
        if PLACEHOLDER_RE.search(content):
            errors.append(f"unresolved placeholder in {path.name}")
        if MOJIBAKE_RE.search(content):
            errors.append(f"probable mojibake in {path.name}")
        for match in IMAGE_RE.finditer(content):
            if not (path.parent / match.group("path")).resolve().exists():
                errors.append(f"broken image link in {path.name}: {match.group('path')}")
    for path in sorted((stage_data / "structured").glob(f"{book}_*.json")):
        if MOJIBAKE_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"probable mojibake in {path.name}")
    if check_installed_delivery:
        errors.extend(installed_delivery_errors(book, audit))
    report = verification_report(book, counts, pending, errors)
    write_json(audit / "reports" / "verification.json", report)
    (audit / "reports" / "report.md").write_text(
        f"# {book} accuracy audit\n\n- valid: `{report['valid']}`\n- automated_valid: `{report['automated_valid']}`\n"
        f"- counts: `{json.dumps(counts, ensure_ascii=False)}`\n- optional spot checks pending: `{json.dumps(pending, ensure_ascii=False)}`\n"
        f"- errors: `{len(report['errors'])}`\n",
        encoding="utf-8",
    )
    return report


def install(book: str, allow_findings: bool = False) -> dict[str, Any]:
    if allow_findings:
        raise RuntimeError("release installation does not accept automatic-finding waivers")
    report = verify(book, check_installed_delivery=False)
    if not report.get("valid"):
        raise RuntimeError("installation blocked: verification is not valid")
    audit = AUDIT_ROOT / book
    before = protected_hashes(book)
    expected = read_json(audit / "reports" / "protected_hashes.json")
    if before != expected:
        raise RuntimeError("installation blocked: protected files changed after audit build")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    snapshot = audit / "snapshots" / "preinstall" / stamp
    snapshot.mkdir(parents=True, exist_ok=False)
    stage = audit / "staging" / "data"
    installed: list[str] = []
    # Recursive handling of ``textbook`` includes nested figure/example assets.
    relative_dirs = ("structured", "figures", "textbook")
    preinstall_files: list[Path] = []
    temporary_files: list[Path] = []
    for relative_dir in relative_dirs:
        target_dir = ROOT / "data" / relative_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        for old in target_dir.rglob(f"{book}_*"):
            if old.is_file():
                preinstall_files.append(old)
                snap = snapshot / relative_dir / old.relative_to(target_dir)
                snap.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old, snap)
    snapshot_binding = bind_tree(snapshot)
    try:
        # Pre-write every replacement before changing any formal delivery file.
        for relative_dir in relative_dirs:
            source_dir = stage / relative_dir
            target_dir = ROOT / "data" / relative_dir
            for source in source_dir.rglob(f"{book}_*"):
                if not source.is_file():
                    continue
                relative = source.relative_to(source_dir)
                temporary = target_dir / relative.parent / f".{source.name}.audit-install-{os.getpid()}"
                temporary.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, temporary)
                temporary_files.append(temporary)
        for relative_dir in relative_dirs:
            source_dir = stage / relative_dir
            target_dir = ROOT / "data" / relative_dir
            staged_names = {path.relative_to(source_dir) for path in source_dir.rglob(f"{book}_*") if path.is_file()}
            for old in target_dir.rglob(f"{book}_*"):
                if old.is_file() and old.relative_to(target_dir) not in staged_names:
                    old.unlink()
            for source in source_dir.rglob(f"{book}_*"):
                if not source.is_file():
                    continue
                relative = source.relative_to(source_dir)
                temporary = target_dir / relative.parent / f".{source.name}.audit-install-{os.getpid()}"
                target = target_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporary, target)
                installed.append((Path("data") / relative_dir / relative).as_posix())
        after = protected_hashes(book)
        if after != before:
            raise RuntimeError("protected-file hash mismatch after install")
    except Exception as exc:
        for temporary in temporary_files:
            temporary.unlink(missing_ok=True)
        for relative_dir in relative_dirs:
            target_dir = ROOT / "data" / relative_dir
            for current in target_dir.rglob(f"{book}_*"):
                if current.is_file():
                    current.unlink()
            snap_dir = snapshot / relative_dir
            for saved in snap_dir.rglob(f"{book}_*") if snap_dir.is_dir() else []:
                target = target_dir / saved.relative_to(snap_dir)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(saved, target)
        restored = [
            path for relative_dir in relative_dirs
            for path in (ROOT / "data" / relative_dir).rglob(f"{book}_*")
            if path.is_file()
        ]
        rollback_valid = (
            protected_hashes(book) == before
            and bind_files(restored, ROOT / "data")["files"] == snapshot_binding["files"]
        )
        failure = {
            "schema": "book_accuracy_install_failure.v2", "book": book,
            "failed_at_utc": utcnow(), "error": str(exc),
            "rolled_back": rollback_valid, "snapshot": str(snapshot.relative_to(ROOT)),
        }
        write_json(audit / "failures" / f"install_{stamp}.json", failure)
        if not rollback_valid:
            raise RuntimeError(f"installation failed and rollback validation failed: {exc}") from exc
        raise RuntimeError(f"installation failed and was rolled back: {exc}") from exc
    result = {
        "installed": True,
        "book": book,
        "files": sorted(set(installed)),
        "snapshot": str(snapshot.relative_to(ROOT)),
        "protected_hashes_unchanged": True,
        "automatic_verification_valid": bool(report.get("valid")),
        "automatic_findings_waived": False,
        "waived_findings": [],
        "delivery": book_delivery_binding(book),
    }
    write_json(audit / "reports" / "installation.json", result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--book", required=True)
    build_parser.add_argument("--dpi", type=int, default=110)
    for command in ("verify", "install", "status"):
        item = sub.add_parser(command)
        item.add_argument("--book", required=True)
        if command == "install":
            item.add_argument(
                "--allow-automatic-findings",
                action="store_true",
                help="install with an explicit recorded waiver when automatic findings remain",
            )
    return parser.parse_args()


def available_books() -> list[str]:
    return sorted(
        path.stem for path in (ROOT / "book_audits").glob("*.json")
        if not path.stem.endswith("_corrections")
    )


def run_command(command: str, book: str, *, dpi: int = 110, allow_findings: bool = False) -> dict[str, Any]:
    if command == "build":
        return build(book, dpi)
    if command == "verify":
        return verify(book)
    if command == "install":
        return install(book, allow_findings=allow_findings)
    return audit_status(book)


def main() -> int:
    args = parse_args()
    if args.book == "all":
        results: dict[str, Any] = {}
        for book in available_books():
            try:
                results[book] = run_command(
                    args.command, book,
                    dpi=getattr(args, "dpi", 110),
                    allow_findings=getattr(args, "allow_automatic_findings", False),
                )
            except Exception as exc:
                results[book] = {"valid": False, "automated_valid": False, "error": str(exc)}
        valid = all(
            result.get("automated_valid", result.get("valid", result.get("installed", False)))
            for result in results.values()
        ) if args.command != "status" else True
        print(json.dumps({
            "schema": "book_accuracy_multi_result.v2", "command": args.command,
            "valid": valid, "results": results,
        }, ensure_ascii=False, indent=2))
        return 0 if valid else 2
    try:
        result = run_command(
            args.command, args.book,
            dpi=getattr(args, "dpi", 110),
            allow_findings=getattr(args, "allow_automatic_findings", False),
        )
    except Exception as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if args.command == "status" or result.get("valid", result.get("installed", False)) else 2


if __name__ == "__main__":
    raise SystemExit(main())
