"""Run GLM-OCR on all supported source files."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Sequence

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "背景资料"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "glmocr_output"
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"

SUPPORTED_SUFFIXES = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
}


@dataclass
class OcrOutcome:
    source: Path
    ok: bool
    skipped: bool = False
    error: str = ""
    elapsed_seconds: float = 0.0


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.name.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def iter_inputs(input_dir: Path) -> list[Path]:
    files = [
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    return sorted(files, key=natural_key)


def env_path(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    return Path(raw).expanduser() if raw else default


def mask_secret(value: str) -> str:
    return f"<set, {len(value)} chars>"


def ensure_api_key() -> str:
    api_key = os.getenv("ZHIPU_API_KEY", "").strip()
    if api_key:
        return api_key

    key_id = os.getenv("ZHIPU_API_KEY_ID", "").strip()
    key_secret = os.getenv("ZHIPU_API_KEY_SECRET", "").strip()
    if key_id and key_secret:
        api_key = f"{key_id}.{key_secret}"
        os.environ["ZHIPU_API_KEY"] = api_key
        return api_key

    raise RuntimeError(
        "Missing GLM-OCR API key. Fill .env with either ZHIPU_API_KEY, "
        "or both ZHIPU_API_KEY_ID and ZHIPU_API_KEY_SECRET."
    )


def pdf_page_count(path: Path) -> int | None:
    if path.suffix.lower() != ".pdf":
        return None
    try:
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(str(path))
        try:
            return len(pdf)
        finally:
            pdf.close()
    except Exception:
        return None


def chunk_ranges(total_pages: int | None, chunk_size: int) -> list[tuple[int | None, int | None]]:
    if not total_pages or total_pages <= chunk_size:
        return [(None, None)]
    ranges: list[tuple[int | None, int | None]] = []
    for start in range(1, total_pages + 1, chunk_size):
        end = min(start + chunk_size - 1, total_pages)
        ranges.append((start, end))
    return ranges


def combine_markdown(parts: Sequence[str]) -> str:
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


def write_result_files(
    output_dir: Path,
    source: Path,
    json_pages: list[object],
    markdown_parts: Sequence[str],
    metadata: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = sanitize_filename(source.stem)

    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    meta_path = output_dir / f"{stem}.meta.json"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(json_pages, file, ensure_ascii=False, indent=2)

    markdown = combine_markdown(markdown_parts)
    if markdown:
        md_path.write_text(markdown, encoding="utf-8")

    with meta_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def write_progress(
    output_dir: Path,
    *,
    status: str,
    total_files: int,
    processed: int,
    skipped: int,
    failed: int,
    current_file: str = "",
    current_chunk: int | None = None,
    total_chunks: int | None = None,
    message: str = "",
    started_at: str = "",
    updated_at: str | None = None,
    files: Sequence[dict[str, object]] | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    progress = {
        "status": status,
        "started_at": started_at,
        "updated_at": updated_at or utc_now(),
        "total_files": total_files,
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "remaining": max(total_files - processed - skipped - failed, 0),
        "current_file": current_file,
        "current_chunk": current_chunk,
        "total_chunks": total_chunks,
        "message": message,
        "files": list(files or []),
    }
    temp_path = output_dir / "_progress.json.tmp"
    final_path = output_dir / "_progress.json"
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(progress, file, ensure_ascii=False, indent=2)
    temp_path.replace(final_path)


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1F]", "_", value)
    value = value.rstrip(" .")
    return value or "result"


def output_exists(output_dir: Path, source: Path) -> bool:
    stem = sanitize_filename(source.stem)
    return (output_dir / f"{stem}.json").is_file() or (output_dir / f"{stem}.md").is_file()


def process_one(
    parser,
    source: Path,
    output_dir: Path,
    chunk_size: int,
    overwrite: bool,
    on_chunk: Callable[[int, int, str], None] | None = None,
) -> OcrOutcome:
    start_time = time.time()
    if not overwrite and output_exists(output_dir, source):
        return OcrOutcome(source=source, ok=True, skipped=True)

    page_count = pdf_page_count(source)
    ranges = chunk_ranges(page_count, chunk_size)
    json_pages: list[object] = []
    markdown_parts: list[str] = []
    usages: list[object] = []
    data_infos: list[object] = []

    for index, (start_page, end_page) in enumerate(ranges, 1):
        kwargs = {"save_layout_visualization": False}
        if start_page is not None:
            kwargs["start_page_id"] = start_page
            kwargs["end_page_id"] = end_page
            print(
                f"  chunk {index}/{len(ranges)}: pages {start_page}-{end_page}",
                flush=True,
            )
            chunk_message = f"Processing pages {start_page}-{end_page}."
        else:
            chunk_message = "Processing whole file."
        if on_chunk is not None:
            on_chunk(index, len(ranges), chunk_message)

        result = parser.parse(str(source), **kwargs)
        if hasattr(result, "_error") and result._error:
            raise RuntimeError(str(result._error))

        if isinstance(result.json_result, list):
            json_pages.extend(result.json_result)
        else:
            json_pages.append(result.json_result)

        if result.markdown_result:
            markdown_parts.append(result.markdown_result)

        usage = getattr(result, "_usage", None)
        if usage is not None:
            usages.append(usage)
        data_info = getattr(result, "_data_info", None)
        if data_info is not None:
            data_infos.append(data_info)
        if on_chunk is not None:
            on_chunk(index, len(ranges), "Chunk finished.")

    metadata = {
        "source": str(source),
        "page_count": page_count,
        "chunks": [
            {"start_page_id": start, "end_page_id": end}
            for start, end in ranges
        ],
        "usage": usages,
        "data_info": data_infos,
    }
    write_result_files(output_dir, source, json_pages, markdown_parts, metadata)
    return OcrOutcome(
        source=source,
        ok=True,
        elapsed_seconds=time.time() - start_time,
    )


def write_error_log(output_dir: Path, outcomes: Iterable[OcrOutcome]) -> None:
    errors = [
        {
            "source": str(outcome.source),
            "error": outcome.error,
            "elapsed_seconds": outcome.elapsed_seconds,
        }
        for outcome in outcomes
        if not outcome.ok
    ]
    if not errors:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "_errors.json").open("w", encoding="utf-8") as file:
        json.dump(errors, file, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    if DEFAULT_ENV_FILE.is_file():
        load_dotenv(DEFAULT_ENV_FILE)

    parser = argparse.ArgumentParser(
        description="Run GLM-OCR on every supported file in the background folder."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=env_path("GLMOCR_INPUT_DIR", DEFAULT_INPUT_DIR),
        help="Input folder. Defaults to the workspace data/background-materials folder or GLMOCR_INPUT_DIR.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=env_path("GLMOCR_OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        help="Output folder. Defaults to ./data/glmocr_output or GLMOCR_OUTPUT_DIR.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="Path to the .env file. Defaults to workspace .env.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("GLMOCR_TIMEOUT", "600")),
        help="Request timeout in seconds.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=int(os.getenv("GLMOCR_PAGE_CHUNK_SIZE", "100")),
        help="PDF page chunk size. GLM-OCR supports up to 100 pages per call.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-run files that already have JSON/Markdown output.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be processed without calling the API.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file = args.env_file.resolve()
    if env_file.is_file():
        load_dotenv(env_file, override=True)

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()

    if not input_dir.is_dir():
        print(f"Input folder does not exist: {input_dir}", file=sys.stderr)
        return 1

    files = iter_inputs(input_dir)
    if not files:
        print(f"No supported files found in: {input_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Found {len(files)} file(s).")

    for path in files:
        pages = pdf_page_count(path)
        page_text = f", {pages} pages" if pages else ""
        status = "skip-existing" if output_exists(output_dir, path) and not args.overwrite else "pending"
        print(f"  - {path.relative_to(input_dir)} ({path.stat().st_size / 1024 / 1024:.1f} MB{page_text}) [{status}]")

    if args.dry_run:
        print("Dry run only. No API calls were made.")
        return 0

    api_key = ensure_api_key()
    print(f"ZHIPU_API_KEY loaded: {mask_secret(api_key)}")

    import glmocr

    outcomes: list[OcrOutcome] = []
    started_at = utc_now()
    progress_files: list[dict[str, object]] = [
        {
            "name": str(path.relative_to(input_dir)),
            "status": "skipped_existing" if output_exists(output_dir, path) and not args.overwrite else "pending",
        }
        for path in files
    ]
    write_progress(
        output_dir,
        status="running",
        total_files=len(files),
        processed=0,
        skipped=0,
        failed=0,
        started_at=started_at,
        files=progress_files,
        message="Starting GLM-OCR run.",
    )
    with glmocr.GlmOcr(mode="maas", timeout=args.timeout, env_file=str(env_file)) as parser:
        for index, source in enumerate(files, 1):
            print(f"\n=== {index}/{len(files)} {source.name} ===", flush=True)
            per_file_started = time.time()
            current_record = progress_files[index - 1]
            current_record["status"] = "running"
            current_record["started_at"] = utc_now()
            write_progress(
                output_dir,
                status="running",
                total_files=len(files),
                processed=sum(1 for item in progress_files if item.get("status") == "done"),
                skipped=sum(1 for item in progress_files if item.get("status") == "skipped_existing"),
                failed=sum(1 for item in progress_files if item.get("status") == "failed"),
                current_file=str(source.relative_to(input_dir)),
                started_at=started_at,
                files=progress_files,
                message=f"Processing {source.name}.",
            )
            try:
                def refresh_chunk(chunk_index: int, total_chunks: int, message: str) -> None:
                    write_progress(
                        output_dir,
                        status="running",
                        total_files=len(files),
                        processed=sum(1 for item in progress_files if item.get("status") == "done"),
                        skipped=sum(1 for item in progress_files if item.get("status") == "skipped_existing"),
                        failed=sum(1 for item in progress_files if item.get("status") == "failed"),
                        current_file=str(source.relative_to(input_dir)),
                        current_chunk=chunk_index,
                        total_chunks=total_chunks,
                        started_at=started_at,
                        files=progress_files,
                        message=message,
                    )

                outcome = process_one(
                    parser=parser,
                    source=source,
                    output_dir=output_dir,
                    chunk_size=args.chunk_size,
                    overwrite=args.overwrite,
                    on_chunk=refresh_chunk,
                )
                outcomes.append(outcome)
                if outcome.skipped:
                    current_record["status"] = "skipped_existing"
                    current_record["finished_at"] = utc_now()
                    print("Skipped existing output.", flush=True)
                else:
                    current_record["status"] = "done"
                    current_record["finished_at"] = utc_now()
                    current_record["elapsed_seconds"] = round(outcome.elapsed_seconds, 1)
                    print(f"Saved in {outcome.elapsed_seconds:.1f}s.", flush=True)
                write_progress(
                    output_dir,
                    status="running",
                    total_files=len(files),
                    processed=sum(1 for item in progress_files if item.get("status") == "done"),
                    skipped=sum(1 for item in progress_files if item.get("status") == "skipped_existing"),
                    failed=sum(1 for item in progress_files if item.get("status") == "failed"),
                    current_file="",
                    started_at=started_at,
                    files=progress_files,
                    message=f"Finished {source.name}.",
                )
            except Exception as exc:
                elapsed = time.time() - per_file_started
                error = str(exc)
                print(f"Failed: {error}", file=sys.stderr, flush=True)
                traceback.print_exc()
                current_record["status"] = "failed"
                current_record["finished_at"] = utc_now()
                current_record["elapsed_seconds"] = round(elapsed, 1)
                current_record["error"] = error
                outcomes.append(
                    OcrOutcome(
                        source=source,
                        ok=False,
                        error=error,
                        elapsed_seconds=elapsed,
                    )
                )
                write_progress(
                    output_dir,
                    status="running",
                    total_files=len(files),
                    processed=sum(1 for item in progress_files if item.get("status") == "done"),
                    skipped=sum(1 for item in progress_files if item.get("status") == "skipped_existing"),
                    failed=sum(1 for item in progress_files if item.get("status") == "failed"),
                    current_file="",
                    started_at=started_at,
                    files=progress_files,
                    message=f"Failed {source.name}: {error}",
                )
                continue

    write_error_log(output_dir, outcomes)
    ok_count = sum(1 for item in outcomes if item.ok and not item.skipped)
    skipped_count = sum(1 for item in outcomes if item.skipped)
    failed_count = sum(1 for item in outcomes if not item.ok)
    print(
        f"\nDone. processed={ok_count}, skipped={skipped_count}, failed={failed_count}"
    )
    write_progress(
        output_dir,
        status="failed" if failed_count else "done",
        total_files=len(files),
        processed=ok_count,
        skipped=skipped_count,
        failed=failed_count,
        started_at=started_at,
        files=progress_files,
        message="Run finished.",
    )
    if failed_count:
        print(f"See error log: {output_dir / '_errors.json'}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
