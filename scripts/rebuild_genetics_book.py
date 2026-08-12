#!/usr/bin/env python3
"""Stage, verify, and atomically install a rule-only Genetics rebuild.

Every intermediate artifact remains below tmp/genetics_rebuild.  The command
never writes to data/ unless --install is supplied and staging verification
has passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[1]
RANGES: dict[str, tuple[int, int]] = {
    **{
        f"chapter{number}": pages
        for number, pages in enumerate(
            [
                (21, 35), (36, 50), (51, 66), (67, 95), (97, 122),
                (123, 146), (147, 192), (193, 220), (221, 265), (267, 305),
                (307, 334), (335, 366), (367, 392), (393, 444), (445, 504),
                (505, 550), (551, 566), (567, 593), (594, 608), (609, 640),
                (641, 668), (669, 697), (699, 726), (727, 738), (739, 756),
                (757, 790), (791, 818),
            ],
            start=1,
        )
    },
    "appendix1": (819, 992),
}
OCR_SUPPLEMENT_RANGES = {
    "appendix1_part2": (919, 955),
    "appendix1_part3": (956, 992),
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_pdfs(source: Path, workspace: Path) -> dict[str, Any]:
    target_dir = workspace / "split_pdfs"
    target_dir.mkdir(parents=True, exist_ok=True)
    source_doc = fitz.open(source)
    records = []
    try:
        if source_doc.page_count != 992:
            raise ValueError(f"Expected 992 source pages, found {source_doc.page_count}")
        for label, (start, end) in RANGES.items():
            target = target_dir / f"Genetics_{label}.pdf"
            temporary = target.with_suffix(".pdf.tmp")
            out = fitz.open()
            try:
                out.insert_pdf(source_doc, from_page=start - 1, to_page=end - 1)
                out.save(temporary, garbage=4, deflate=True)
            finally:
                out.close()
            os.replace(temporary, target)
            check = fitz.open(target)
            try:
                actual = check.page_count
                evidence_dir = workspace / "split_evidence"
                evidence_dir.mkdir(parents=True, exist_ok=True)
                for page_index, suffix in ((0, "first"), (actual - 1, "last")):
                    check[page_index].get_pixmap(matrix=fitz.Matrix(0.8, 0.8), alpha=False).save(
                        evidence_dir / f"Genetics_{label}_{suffix}.png"
                    )
            finally:
                check.close()
            expected = end - start + 1
            if actual != expected:
                raise RuntimeError(f"{target.name}: pages={actual}, expected={expected}")
            records.append({
                "label": label, "source_pages": [start, end],
                "page_count": actual, "path": str(target), "sha256": sha256(target),
            })
        supplement_dir = workspace / "ocr_supplement"
        supplement_dir.mkdir(parents=True, exist_ok=True)
        for label, (start, end) in OCR_SUPPLEMENT_RANGES.items():
            target = supplement_dir / f"Genetics_{label}.pdf"
            temporary = target.with_suffix(".pdf.tmp")
            out = fitz.open()
            try:
                out.insert_pdf(source_doc, from_page=start - 1, to_page=end - 1)
                out.save(temporary, garbage=4, deflate=True)
            finally:
                out.close()
            os.replace(temporary, target)
            records.append({
                "label": label, "source_pages": [start, end], "page_count": end - start + 1,
                "path": str(target), "sha256": sha256(target), "ocr_supplement": True,
            })
    finally:
        source_doc.close()
    report = {"valid": True, "source": str(source), "source_sha256": sha256(source), "outputs": records}
    write_json(workspace / "split_report.json", report)
    return report


def run_ocr(workspace: Path, env_name: str) -> None:
    direct_python = Path(sys.executable).resolve().parent / "envs" / env_name / "python.exe"
    for input_dir in (workspace / "split_pdfs", workspace / "ocr_supplement"):
        command = (
            [str(direct_python), str(ROOT / "scripts" / "run_paddleocr_batch.py")]
            if direct_python.exists()
            else ["conda", "run", "-n", env_name, "python", str(ROOT / "scripts" / "run_paddleocr_batch.py")]
        )
        command += ["--input", str(input_dir), "--output", str(workspace / "paddle_output")]
        subprocess.run(command, cwd=ROOT, check=True)


def verify_split(workspace: Path) -> list[str]:
    errors = []
    for label, (start, end) in RANGES.items():
        path = workspace / "split_pdfs" / f"Genetics_{label}.pdf"
        if not path.exists():
            errors.append(f"missing {path}")
            continue
        doc = fitz.open(path)
        try:
            actual = doc.page_count
        finally:
            doc.close()
        expected = end - start + 1
        if actual != expected:
            errors.append(f"{path.name}: {actual} != {expected}")
    return errors


def verify_ocr(workspace: Path) -> list[str]:
    errors = []
    for label in RANGES:
        root = workspace / "paddle_output" / f"Genetics_{label}_full"
        for relative in (Path("main.tex"), Path("intermediate/paddle_raw_response.json")):
            if not (root / relative).is_file():
                errors.append(f"missing {root / relative}")
        raw = root / "intermediate" / "paddle_raw_response.json"
        if raw.exists():
            payload = json.loads(raw.read_text(encoding="utf-8"))
            actual = len(payload) if isinstance(payload, list) else 0
            start, end = RANGES[label]
            expected = min(100, end - start + 1) if label == "appendix1" else end - start + 1
            if actual != expected or not all(isinstance(page, dict) for page in payload):
                errors.append(f"{label} OCR pages={actual}, expected={expected}")
    for label, (start, end) in OCR_SUPPLEMENT_RANGES.items():
        supplement = workspace / "paddle_output" / f"Genetics_{label}_full"
        for relative in (Path("main.tex"), Path("intermediate/paddle_raw_response.json")):
            if not (supplement / relative).is_file():
                errors.append(f"missing {supplement / relative}")
        raw = supplement / "intermediate" / "paddle_raw_response.json"
        if raw.exists():
            payload = json.loads(raw.read_text(encoding="utf-8"))
            if not isinstance(payload, list) or len(payload) != end - start + 1 or not all(isinstance(page, dict) for page in payload):
                errors.append(f"{label} OCR payload is not {end-start+1} page-layout records")
    appendix_counts = []
    for name in ("Genetics_appendix1_full", "Genetics_appendix1_part2_full", "Genetics_appendix1_part3_full"):
        raw = workspace / "paddle_output" / name / "intermediate" / "paddle_raw_response.json"
        if raw.exists():
            payload = json.loads(raw.read_text(encoding="utf-8"))
            appendix_counts.append(len(payload) if isinstance(payload, list) else 0)
    if appendix_counts and sum(appendix_counts) != 174:
        errors.append(f"combined appendix OCR pages={sum(appendix_counts)}, expected=174")
    return errors


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.genetics-rebuild-tmp")
    shutil.copy2(source, temporary)
    for attempt in range(10):
        try:
            os.replace(temporary, target)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(0.1 * (attempt + 1))


def snapshot_genetics(workspace: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    snapshot = workspace / "preinstall_snapshots" / stamp
    for relative, patterns in {
        Path("structured"): ("Genetics_*",),
        Path("textbook"): ("Genetics_*_textbook.md",),
        Path("figures"): ("Genetics_*.png",),
        Path("figures/examples"): ("Genetics_*.png",),
        Path("textbook/figures"): ("Genetics_*.png",),
        Path("textbook/figures/examples"): ("Genetics_*.png",),
        Path("背景资料"): ("Genetics_*.pdf",),
    }.items():
        source_dir = ROOT / "data" / relative
        target_dir = snapshot / "data" / relative
        target_dir.mkdir(parents=True, exist_ok=True)
        for pattern in patterns:
            for path in source_dir.glob(pattern):
                shutil.copy2(path, target_dir / path.name)
    example = ROOT / "data" / "structured" / "example_library.json"
    if example.exists():
        shutil.copy2(example, snapshot / "data" / "structured" / example.name)
    return snapshot


def is_genetics_install_target(path: Path) -> bool:
    relative = path.relative_to(ROOT / "data")
    name = path.name
    return (
        (relative.parent == Path("structured") and name.startswith("Genetics_") and name.endswith(".json"))
        or (relative.parent == Path("textbook") and name.startswith("Genetics_") and name.endswith("_textbook.md"))
        or (relative.parent == Path("figures") and name.startswith("Genetics_") and name.endswith(".png"))
        or (relative.parent == Path("figures/examples") and name.startswith("Genetics_") and name.endswith(".png"))
        or (relative.parent == Path("textbook/figures") and name.startswith("Genetics_") and name.endswith(".png"))
        or (relative.parent == Path("textbook/figures/examples") and name.startswith("Genetics_") and name.endswith(".png"))
        or (relative.parent == Path("鑳屾櫙璧勬枡") and name.startswith("Genetics_") and name.endswith(".pdf"))
    )


def protected_hashes() -> dict[str, str]:
    shared_examples = ROOT / "data" / "structured" / "example_library.json"
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in sorted((ROOT / "data").rglob("*"))
        if path.is_file() and path != shared_examples and not is_genetics_install_target(path)
    }


def non_genetics_examples(path: Path) -> tuple[int, str]:
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"examples": []}
    rows = [
        row for row in payload.get("examples", [])
        if str(row.get("book") or "").lower() != "genetics"
        and not str(row.get("chapter") or "").lower().startswith("genetics_")
    ]
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(rows), hashlib.sha256(canonical).hexdigest()


def install_stage(workspace: Path) -> dict[str, Any]:
    stage_data = workspace / "staging" / "data"
    verification = json.loads((workspace / "verification.json").read_text(encoding="utf-8"))
    if not verification.get("valid"):
        raise ValueError("Refusing install: staging verification is not valid")
    protected_before = protected_hashes()
    shared_examples_path = ROOT / "data" / "structured" / "example_library.json"
    non_genetics_count_before, non_genetics_hash_before = non_genetics_examples(shared_examples_path)
    snapshot = snapshot_genetics(workspace)
    groups = {
        "structured": (stage_data / "structured", ROOT / "data" / "structured", "Genetics_*"),
        "textbook": (stage_data / "textbook", ROOT / "data" / "textbook", "Genetics_*_textbook.md"),
        "figures": (stage_data / "figures", ROOT / "data" / "figures", "Genetics_*.png"),
        "example_figures": (stage_data / "figures" / "examples", ROOT / "data" / "figures" / "examples", "Genetics_*.png"),
        "textbook_figures": (stage_data / "textbook" / "figures", ROOT / "data" / "textbook" / "figures", "Genetics_*.png"),
        "textbook_example_figures": (stage_data / "textbook" / "figures" / "examples", ROOT / "data" / "textbook" / "figures" / "examples", "Genetics_*.png"),
        "background_pdfs": (stage_data / "背景资料", ROOT / "data" / "背景资料", "Genetics_*.pdf"),
    }
    installed = {}
    for name, (source_dir, target_dir, pattern) in groups.items():
        staged = sorted(source_dir.glob(pattern))
        staged_names = {path.name for path in staged}
        for stale in target_dir.glob(pattern):
            if stale.name not in staged_names:
                stale.unlink()
        for source in staged:
            atomic_copy(source, target_dir / source.name)
        installed[name] = len(staged)
    staged_examples_path = stage_data / "structured" / "example_library.json"
    staged_examples = json.loads(staged_examples_path.read_text(encoding="utf-8")).get("examples", [])
    shared_payload = json.loads(shared_examples_path.read_text(encoding="utf-8")) if shared_examples_path.exists() else {"schema": "example_library.v1", "examples": []}
    retained = [
        row for row in shared_payload.get("examples", [])
        if str(row.get("book") or "").lower() != "genetics"
        and not str(row.get("chapter") or "").lower().startswith("genetics_")
    ]
    shared_payload["schema"] = "example_library.v1"
    shared_payload["examples"] = retained + staged_examples
    temporary = shared_examples_path.with_name(".example_library.json.genetics-rebuild-tmp")
    write_json(temporary, shared_payload)
    os.replace(temporary, shared_examples_path)
    installed["examples"] = len(staged_examples)
    protected_after = protected_hashes()
    non_genetics_count_after, non_genetics_hash_after = non_genetics_examples(shared_examples_path)
    stage_matches_install = {}
    for name, (source_dir, target_dir, pattern) in groups.items():
        staged_hashes = {path.name: sha256(path) for path in sorted(source_dir.glob(pattern))}
        installed_hashes = {path.name: sha256(path) for path in sorted(target_dir.glob(pattern))}
        stage_matches_install[name] = staged_hashes == installed_hashes
    protected_changed = sorted(
        path for path in set(protected_before) | set(protected_after)
        if protected_before.get(path) != protected_after.get(path)
    )
    report = {
        "valid": (
            not protected_changed
            and non_genetics_count_before == non_genetics_count_after
            and non_genetics_hash_before == non_genetics_hash_after
            and all(stage_matches_install.values())
        ),
        "installed": installed,
        "snapshot": str(snapshot),
        "protected_files_checked": len(protected_before),
        "protected_changed": protected_changed,
        "non_genetics_examples_count_before": non_genetics_count_before,
        "non_genetics_examples_count_after": non_genetics_count_after,
        "non_genetics_examples_hash_unchanged": non_genetics_hash_before == non_genetics_hash_after,
        "stage_matches_install": stage_matches_install,
    }
    write_json(workspace / "postinstall_verification.json", report)
    if not report["valid"]:
        raise RuntimeError("Genetics post-install protection verification failed")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, default=ROOT / "data" / "背景资料" / "Genetics.pdf")
    parser.add_argument("--workspace", type=Path, default=ROOT / "tmp" / "genetics_rebuild")
    parser.add_argument("--ocr-env", default="py312")
    parser.add_argument("--split-only", action="store_true")
    parser.add_argument("--ocr-only", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--install", action="store_true")
    # Compatibility switches: the Genetics builder is always rule-only.
    parser.add_argument("--skip-llm-cleaning", action="store_true")
    parser.add_argument("--llm-phase", default="0")
    parser.add_argument("--structured-fusion", action="store_true")
    parser.add_argument("--example-pipeline", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    allowed = (ROOT / "tmp").resolve()
    if workspace != allowed and allowed not in workspace.parents:
        raise ValueError(f"workspace must be below {allowed}")
    if args.install:
        print(json.dumps(install_stage(workspace), ensure_ascii=False, indent=2))
        return 0
    if args.verify_only:
        errors = verify_split(workspace) + verify_ocr(workspace)
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    if not args.ocr_only:
        split_pdfs(args.source_pdf.resolve(), workspace)
    if not args.split_only:
        run_ocr(workspace, args.ocr_env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
