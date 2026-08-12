"""Run paper2latex/PaddleOCR for every source PDF into data/paddle_output."""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER2LATEX_SRC = ROOT / "paper2latex" / "src"
if str(PAPER2LATEX_SRC) not in sys.path:
    sys.path.insert(0, str(PAPER2LATEX_SRC))


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def natural_key(path: Path) -> list[object]:
    import re

    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name.lower())]


def output_complete(out_dir: Path) -> bool:
    return (
        (out_dir / "main.tex").is_file()
        and (out_dir / "intermediate" / "paddle_raw_response.json").is_file()
    )


def write_progress(output_dir: Path, payload: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    temp = output_dir / "_progress.json.tmp"
    final = output_dir / "_progress.json"
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(final)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch paper2latex/PaddleOCR runner.")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "背景资料")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "paddle_output")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    from paper2latex.core.config import Config
    from paper2latex.pipeline import Pipeline

    args = parse_args()
    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob("*.pdf"), key=natural_key)
    if args.limit:
        files = files[: args.limit]
    started_at = utc_now()
    records: list[dict[str, object]] = []
    for pdf in files:
        out_dir = output_dir / f"{pdf.stem}_full"
        records.append(
            {
                "name": pdf.name,
                "output": str(out_dir),
                "status": "skipped_existing" if output_complete(out_dir) and not args.overwrite else "pending",
            }
        )

    def refresh(message: str = "", current_file: str = "") -> None:
        write_progress(
            output_dir,
            {
                "status": "running",
                "started_at": started_at,
                "updated_at": utc_now(),
                "total_files": len(files),
                "processed": sum(1 for item in records if item.get("status") == "done"),
                "skipped": sum(1 for item in records if item.get("status") == "skipped_existing"),
                "failed": sum(1 for item in records if item.get("status") == "failed"),
                "current_file": current_file,
                "message": message,
                "files": records,
            },
        )

    print(f"Input:  {input_dir}", flush=True)
    print(f"Output: {output_dir}", flush=True)
    print(f"Found {len(files)} PDF(s).", flush=True)
    refresh("Starting PaddleOCR batch.")

    config = Config()
    for index, pdf in enumerate(files, 1):
        out_dir = output_dir / f"{pdf.stem}_full"
        record = records[index - 1]
        if output_complete(out_dir) and not args.overwrite:
            record["status"] = "skipped_existing"
            record["finished_at"] = utc_now()
            print(f"[{index}/{len(files)}] skip {pdf.name}", flush=True)
            refresh(f"Skipped {pdf.name}.")
            continue

        record["status"] = "running"
        record["started_at"] = utc_now()
        refresh(f"Processing {pdf.name}.", pdf.name)
        print(f"[{index}/{len(files)}] processing {pdf.name}", flush=True)
        started = time.time()
        try:
            pipeline = Pipeline(config)
            result = pipeline.run_conversion(str(pdf), str(out_dir))
            elapsed = time.time() - started
            if result.status != "success" or not output_complete(out_dir):
                raise RuntimeError(f"Paddle conversion did not produce complete output: {result}")
            record["status"] = "done"
            record["finished_at"] = utc_now()
            record["elapsed_seconds"] = round(elapsed, 1)
            print(f"[{index}/{len(files)}] done {pdf.name} in {elapsed:.1f}s", flush=True)
            refresh(f"Finished {pdf.name}.")
        except Exception as exc:
            elapsed = time.time() - started
            record["status"] = "failed"
            record["finished_at"] = utc_now()
            record["elapsed_seconds"] = round(elapsed, 1)
            record["error"] = str(exc)
            print(f"[{index}/{len(files)}] failed {pdf.name}: {exc}", flush=True)
            traceback.print_exc()
            refresh(f"Failed {pdf.name}: {exc}")

    failed = sum(1 for item in records if item.get("status") == "failed")
    write_progress(
        output_dir,
        {
            "status": "failed" if failed else "done",
            "started_at": started_at,
            "updated_at": utc_now(),
            "total_files": len(files),
            "processed": sum(1 for item in records if item.get("status") == "done"),
            "skipped": sum(1 for item in records if item.get("status") == "skipped_existing"),
            "failed": failed,
            "current_file": "",
            "message": "Run finished.",
            "files": records,
        },
    )
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
