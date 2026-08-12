#!/usr/bin/env python3
"""Run reproducible fast or release verification and emit one JSON report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tmp" / "release_check"
REPORT_PATH = REPORT_DIR / "report.json"
BOOKS = ("Evolution", "Genetics", "PopGen")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def command_result(name: str, command: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = utcnow()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        return {
            "name": name,
            "command": command,
            "started_at_utc": started,
            "finished_at_utc": utcnow(),
            "returncode": completed.returncode,
            "valid": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except OSError as exc:
        return {
            "name": name,
            "command": command,
            "started_at_utc": started,
            "finished_at_utc": utcnow(),
            "returncode": 127,
            "valid": False,
            "stdout": "",
            "stderr": str(exc),
        }


def tree_digest(root: Path) -> str:
    entries = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    return hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def reader_determinism_result(env: dict[str, str]) -> dict[str, Any]:
    command = [sys.executable, "study_reader/build_study_reader.py", "--release", "--skip-llm"]
    first = command_result("reader-release-first", command, env=env)
    generated = ROOT / "study_reader" / "data" / "generated"
    first_digest = tree_digest(generated) if first["valid"] else None
    second = command_result("reader-release-second", command, env=env) if first["valid"] else None
    second_digest = tree_digest(generated) if second and second["valid"] else None
    valid = bool(first["valid"] and second and second["valid"] and first_digest == second_digest)
    return {
        "name": "reader-determinism",
        "command": command,
        "valid": valid,
        "returncode": 0 if valid else 1,
        "first_sha256": first_digest,
        "second_sha256": second_digest,
        "runs": [item for item in (first, second) if item is not None],
    }


def version_result() -> dict[str, Any]:
    node = command_result("node-version", [shutil.which("node") or "node", "--version"])
    python_valid = sys.version_info[:2] == (3, 12)
    node_major = None
    if node["valid"]:
        try:
            node_major = int(node["stdout"].strip().lstrip("v").split(".", 1)[0])
        except ValueError:
            pass
    errors = []
    if not python_valid:
        errors.append(f"Python 3.12 required, found {platform.python_version()}")
    if node_major != 24:
        errors.append(f"Node 24 required, found {node.get('stdout', '').strip() or 'unavailable'}")
    return {
        "name": "runtime-versions",
        "valid": not errors,
        "python": platform.python_version(),
        "python_required": "3.12.x",
        "node": node["stdout"].strip() if node["valid"] else None,
        "node_required": "24.x",
        "errors": errors,
    }


def fast_checks() -> list[dict[str, Any]]:
    pytest_base = REPORT_DIR / "pytest"
    pytest_base.parent.mkdir(parents=True, exist_ok=True)
    test_env = os.environ.copy()
    test_env["PYTHONUTF8"] = "1"
    test_env["PYTHONIOENCODING"] = "utf-8"
    test_temp = ROOT / "tmp" / "test_runtime" / "system_temp"
    test_temp.mkdir(parents=True, exist_ok=True)
    for name in ("TMP", "TEMP", "TMPDIR"):
        test_env[name] = str(test_temp)
    uv = shutil.which("uv") or "uv"
    npm = shutil.which("npm") or "npm"
    commands: list[tuple[str, list[str]]] = [
        ("uv-lock", [uv, "lock", "--check"]),
        ("compile", [sys.executable, "-m", "compileall", "-q", "knowledge_engineering", "textbook_exporter", "scripts", "study_reader", "paper2latex/tests"]),
        ("ruff", [sys.executable, "-m", "ruff", "check", "knowledge_engineering", "textbook_exporter", "scripts", "study_reader", "paper2latex/tests", "--config", "pyproject.toml"]),
        ("python-tests", [sys.executable, "-m", "pytest", "paper2latex/tests", "-q", "--basetemp", str(pytest_base), "-p", "no:cacheprovider"]),
        ("node-tests", [npm, "run", "test:math", "--silent"]),
        ("pip-check", [sys.executable, "-m", "pip", "check"]),
        ("pip-audit", [sys.executable, "-m", "pip_audit", "--progress-spinner", "off", "--format", "json"]),
        ("npm-audit", [npm, "audit", "--audit-level=moderate", "--json"]),
    ]
    return [
        version_result(),
        *(
            command_result(name, command, env=test_env)
            for name, command in commands
        ),
    ]


def pack_commands(build_packs: bool) -> list[tuple[str, list[str]]]:
    commands: list[tuple[str, list[str]]] = []
    for book in BOOKS:
        output = ROOT / "Pack" / f"{book}Pack"
        if build_packs:
            command = [
                sys.executable, "scripts/package_book_delivery.py", "--book", book,
                "--output", str(output), "--replace", "--provenance-report",
                str(ROOT / "tmp" / "book_audits" / book / "reports" / "installation.json"),
            ]
            commands.append((f"pack-build-{book}", command))
        else:
            command = [sys.executable, "scripts/package_book_delivery.py", "--book", book, "--output", str(output), "--verify-only"]
            commands.append((f"pack-verify-{book}", command))
    return commands


def release_checks(build_packs: bool) -> list[dict[str, Any]]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["SOURCE_DATE_EPOCH"] = "0"
    env["NO_PROXY"] = "*"
    env["no_proxy"] = "*"
    for name in (
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY", "GEMINI_API_KEY", "AZURE_OPENAI_API_KEY", "DEEPSEEK_API_KEY",
    ):
        env.pop(name, None)
        env.pop(name.lower(), None)
    node = shutil.which("node") or "node"
    commands: list[tuple[str, list[str]]] = [
        ("book-audits", [sys.executable, "scripts/audit_book_accuracy.py", "verify", "--book", "all"]),
        ("textbook-math", [node, "scripts/validate_textbook_math.js", "--books", ",".join(BOOKS)]),
    ]
    results = [command_result(name, command, env=env) for name, command in commands]
    results.append(reader_determinism_result(env))
    results.append(command_result("reader-assets", [sys.executable, "scripts/build_study_reader_assets.py"], env=env))
    results.extend(
        command_result(name, command, env=env)
        for name, command in pack_commands(build_packs)
    )
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("fast", "release"))
    parser.add_argument("--build-packs", action="store_true", help="Build local Packs after all source gates are evaluated.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    checks = fast_checks()
    if args.mode == "release":
        checks.extend(release_checks(args.build_packs))
    report = {
        "schema": "project_verification.v1",
        "mode": args.mode,
        "generated_at_utc": utcnow(),
        "valid": all(check.get("valid", False) for check in checks),
        "build_packs": bool(args.build_packs),
        "checks": checks,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": report["schema"], "mode": report["mode"], "valid": report["valid"],
        "report": str(REPORT_PATH.relative_to(ROOT)),
        "checks": [{"name": item["name"], "valid": item["valid"], "returncode": item.get("returncode")} for item in checks],
    }, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
