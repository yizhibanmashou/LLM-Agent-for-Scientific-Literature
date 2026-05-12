"""Runtime policy and artifact helpers for the processing pipeline."""

from __future__ import annotations

import os
from typing import Any

from knowledge_engineering.core.common import append_jsonl_row, utc_now_iso, write_json_path


def utc_now() -> str:
    return utc_now_iso()


def ensure_dir(path: str) -> str:
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def append_jsonl(path: str, payload: dict[str, Any]) -> None:
    append_jsonl_row(path, payload)


def write_json(path: str, payload: dict[str, Any]) -> None:
    write_json_path(path, payload)


def numeric_dict_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, int]:
    keys = set(before.keys()) | set(after.keys())
    delta: dict[str, int] = {}
    always_keep = {"requests_total", "remote_calls", "cache_hits", "budget_rejections"}
    for key in keys:
        if key.startswith("max_") or key == "cache_enabled":
            continue
        before_value = before.get(key, 0)
        after_value = after.get(key, 0)
        if isinstance(before_value, bool) or isinstance(after_value, bool):
            continue
        if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
            delta_value = int(after_value - before_value)
            if delta_value != 0 or key in always_keep:
                delta[key] = delta_value
    return delta


def clamp_float(raw: Any, *, default: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = default
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def parse_chapter_allowlist(raw: str, fallback: set[str]) -> set[str]:
    values = [part.strip().lower() for part in (raw or "").split(",")]
    cleaned = {value for value in values if value}
    if "all" in cleaned or "*" in cleaned:
        return {"*"}
    if cleaned:
        return cleaned
    return set(fallback)


def chapter_in_allowlist(chapter_name: str, allowlist: set[str]) -> bool:
    chapter = (chapter_name or "").strip().lower()
    if "*" in allowlist:
        return True
    return chapter in allowlist


def resolve_effective_llm_phase(chapter_name: str, llm_policy: dict[str, Any]) -> int:
    base_phase = int(llm_policy.get("phase", 0))
    if base_phase <= 0:
        return 0
    chapter = (chapter_name or "").strip().lower()

    if base_phase >= 3:
        phase3_chapters = llm_policy.get("phase3_chapters", set())
        if chapter_in_allowlist(chapter, phase3_chapters):
            return 3
    if base_phase >= 2:
        phase2_chapters = llm_policy.get("phase2_chapters", set())
        if chapter_in_allowlist(chapter, phase2_chapters):
            return 2
    return 1
