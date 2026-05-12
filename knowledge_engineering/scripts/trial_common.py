from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from knowledge_engineering.core.common import read_json
from knowledge_engineering.processors.example_extraction import natural_key, sha256_file

AUDIT_SCRIPT = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "scripts" / "audit_structured_version.py"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def render_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def compare_structured_dirs(baseline_structured: Path, trial_structured: Path) -> dict[str, Any]:
    baseline_files = {
        path.relative_to(baseline_structured).as_posix(): path
        for path in baseline_structured.glob("*.json")
    }
    trial_files = {
        path.relative_to(trial_structured).as_posix(): path
        for path in trial_structured.glob("*.json")
    }
    added = sorted([name for name in trial_files if name not in baseline_files], key=natural_key)
    removed = sorted([name for name in baseline_files if name not in trial_files], key=natural_key)
    modified: list[str] = []
    unchanged: list[str] = []
    for name in sorted(set(baseline_files) & set(trial_files), key=natural_key):
        if sha256_file(baseline_files[name]) == sha256_file(trial_files[name]):
            unchanged.append(name)
        else:
            modified.append(name)
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def run_audit(structured_dir: Path, label: str, out_dir: Path) -> tuple[dict[str, Any], str]:
    out_json = out_dir / "audit.json"
    out_md = out_dir / "audit.md"
    out_samples = out_dir / "audit_samples.json"
    cmd = [
        sys.executable,
        str(AUDIT_SCRIPT),
        "--structured-dir",
        str(structured_dir),
        "--label",
        label,
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
        "--out-samples",
        str(out_samples),
    ]
    subprocess.run(cmd, check=True)
    return read_json(out_json), " ".join(str(part) for part in cmd)


def run_py_compile_checks(paths: list[Path]) -> list[dict[str, str]]:
    cache_dir = PROJECT_ROOT / "tmp" / "structured_quality_probe" / "cache" / "py_compile_check"
    cache_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []
    for path in paths:
        cfile = cache_dir / f"{path.stem}.pyc"
        py_compile.compile(str(path), cfile=str(cfile), doraise=True)
        results.append(
            {
                "command": f"py_compile.compile({path.as_posix()})",
                "result": f"ok -> {cfile.as_posix()}",
            }
        )
    return results
