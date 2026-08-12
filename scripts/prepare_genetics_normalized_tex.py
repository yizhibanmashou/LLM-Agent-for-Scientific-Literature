"""Prepare Genetics normalized OCR blocks as process.py-compatible main.tex files."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "paddle_output"
DEFAULT_OUTPUT = ROOT / "tmp" / "genetics_process_input"

FIGURE_CAPTION_RE = re.compile(
    r"^\s*(?:<div[^>]*>\s*)?(?:Figure|Fig\.)\s+(?P<id>\d+\.\d+[a-z]?)\b(?P<caption>.*?)(?:</div>\s*)?$",
    re.IGNORECASE | re.DOTALL,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
IMAGE_BOX_RE = re.compile(r"img_in_(?:chart|image)_box_(?P<x0>\d+)_(?P<y0>\d+)_(?P<x1>\d+)_(?P<y1>\d+)", re.IGNORECASE)

MOJIBAKE_REPLACEMENTS = {
    "鈥檚": "'s",
    "鈥檛": "'t",
    "鈥檙": "'r",
    "鈥檝": "'v",
    "鈥檒": "'l",
    "鈥檇": "'d",
    "鈥攂": "-b",
    "鈥攖": "-t",
    "鈥攁": "-a",
    "鈥攊": "-i",
    "鈥?": '"',
    "鈥渉": '"h',
    "鈥渨": '"w',
    "鈥淲": '"W',
    "鈥減": '"p',
    "鈥渕": '"m',
    "鈥渃": '"c',
    "鈥渂": '"b',
    "鈥渁": '"a',
    "鈥渢": '"t',
    "鈥渟": '"s',
    "鈥渋": '"i',
    "鈥渞": '"r',
}


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: str) -> str:
    text = html.unescape(str(value or "")).replace("\r\n", "\n").replace("\r", "\n")
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(bad, good)
    text = re.sub(r"<div[^>]*>\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*</div>\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def is_image_block(text: str) -> bool:
    return bool(re.search(r"<img\b", text or "", flags=re.IGNORECASE))


def figure_caption_id(text: str) -> str | None:
    cleaned = clean_text(text)
    match = FIGURE_CAPTION_RE.match(cleaned)
    return match.group("id") if match else None


def strip_markdown_heading(text: str) -> tuple[int, str] | None:
    match = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>.+)$", text.strip())
    if not match:
        return None
    return len(match.group("marks")), match.group("title").strip()


def render_heading(level: int, title: str) -> str:
    if level <= 1:
        return rf"\section{{{title}}}"
    if level == 2:
        return rf"\subsection{{{title}}}"
    return rf"\subsubsection{{{title}}}"


def render_block(block: dict[str, Any]) -> str:
    kind = str(block.get("kind") or "text").lower()
    text = clean_text(str(block.get("text") or ""))
    if not text:
        return ""

    if kind == "formula":
        return f"$$\n{text}\n$$"

    heading = strip_markdown_heading(text)
    if heading:
        level, title = heading
        if title.isdigit():
            return ""
        return render_heading(level, title)

    if kind == "heading":
        return render_heading(2, text)

    return text


def convert_chapter(source_dir: Path, output_root: Path) -> dict[str, Any]:
    chapter = source_dir.name.removesuffix("_full")
    blocks = read_json(source_dir / "normalized" / "normalized_blocks.json")
    if not isinstance(blocks, list):
        raise ValueError(f"{source_dir}: normalized_blocks.json is not a list")

    raw_pages = prepare_intermediate_raw(source_dir)
    out_dir = output_root / source_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = out_dir / "main.tex"

    lines: list[str] = [
        r"\begin{document}",
        "",
    ]
    figure_placeholders = 0
    skipped_image_blocks = 0
    index = 0
    while index < len(blocks):
        block = blocks[index]
        raw_text = str(block.get("text") or "")
        if is_image_block(raw_text):
            skipped_image_blocks += 1
            caption_id = None
            if index + 1 < len(blocks):
                caption_id = figure_caption_id(str(blocks[index + 1].get("text") or ""))
            if caption_id:
                lines.append(f"[[FIGURE:{caption_id}]]")
                lines.append("")
                figure_placeholders += 1
                index += 2
                continue
            index += 1
            continue

        rendered = render_block(block)
        if rendered:
            lines.append(rendered)
            lines.append("")
        index += 1

    lines.extend([r"\end{document}", ""])
    tex_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "chapter": chapter,
        "source": str(source_dir),
        "main_tex": str(tex_path),
        "blocks": len(blocks),
        "raw_pages": len(raw_pages),
        "image_blocks": skipped_image_blocks,
        "figure_placeholders": figure_placeholders,
    }


def prepare_intermediate_raw(source_dir: Path) -> list[dict[str, Any]]:
    result_path = source_dir / "ocr_raw" / "result.jsonl"
    pages: list[dict[str, Any]] = []
    if result_path.exists():
        for line in result_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            result = payload.get("result") if isinstance(payload, dict) else {}
            layout_pages = result.get("layoutParsingResults") if isinstance(result, dict) else []
            if isinstance(layout_pages, list):
                pages.extend(page for page in layout_pages if isinstance(page, dict))

    intermediate_dir = source_dir / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    (intermediate_dir / "paddle_raw_response.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    api_payload = {"result": {"layoutParsingResults": pages}}
    (intermediate_dir / "paddle_raw_api_response.json").write_text(
        json.dumps(api_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--chapters", default="", help="Comma-separated chapter names, e.g. Genetics_chapter1.")
    args = parser.parse_args()

    chapter_filter = {item.strip() for item in args.chapters.split(",") if item.strip()}
    source_dirs = sorted(args.input_dir.glob("Genetics_chapter*_full"), key=natural_key)
    if chapter_filter:
        source_dirs = [path for path in source_dirs if path.name.removesuffix("_full") in chapter_filter]
    if not source_dirs:
        raise SystemExit("No Genetics normalized OCR directories matched.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = [convert_chapter(path, args.output_dir) for path in source_dirs]
    summary_path = args.output_dir / "prepare_summary.json"
    summary_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"prepared={len(summaries)} summary={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
