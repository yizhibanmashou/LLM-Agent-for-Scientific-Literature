"""Core local runtime for knowledge_engineering."""

from __future__ import annotations

import json
import os
import re
import socket
import time
import hashlib
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest


DEFAULT_SOURCE_TITLE = "Evolution and Selection of Quantitative Traits"
CHAPTER_NAME_PATTERN = re.compile(r"^chapter(?P<num>\d+)$", re.IGNORECASE)
APPENDIX_NAME_PATTERN = re.compile(r"^appendix(?P<num>\d+)$", re.IGNORECASE)
LABEL_ID_PATTERN = re.compile(
    r"^(?P<chapter>A?\d+)\.(?P<index>\d+)(?:\.(?P<subindex>\d+))?(?P<suffix>[A-Za-z]?)$",
    re.IGNORECASE,
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _default_dotenv_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / ".env"


def _load_dotenv_into_environ(dotenv_path: str | Path | None = None) -> None:
    path = Path(dotenv_path) if dotenv_path is not None else _default_dotenv_path()
    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if os.getenv(key) is None:
            os.environ[key] = value


def _chapter_sort_key(chapter_name: str) -> tuple[int, int, str]:
    value = str(chapter_name or "").strip().lower()
    chapter_match = CHAPTER_NAME_PATTERN.fullmatch(value)
    if chapter_match:
        return (0, int(chapter_match.group("num")), value)
    appendix_match = APPENDIX_NAME_PATTERN.fullmatch(value)
    if appendix_match:
        return (1, int(appendix_match.group("num")), value)
    return (2, 9999, value)


def _label_sort_key(label: str) -> tuple[int, int, int, int, str]:
    value = str(label or "").strip().lower()
    match = LABEL_ID_PATTERN.fullmatch(value)
    if not match:
        return (9999, 9999, 9999, 9999, value)
    suffix = match.group("suffix").lower()
    suffix_rank = 0 if not suffix else ord(suffix) - 96
    subindex = int(match.group("subindex")) if match.group("subindex") else 0
    chapter = match.group("chapter").lower()
    chapter_rank = 1000 + int(chapter[1:]) if chapter.startswith("a") else int(chapter)
    return (
        chapter_rank,
        int(match.group("index")),
        subindex,
        suffix_rank,
        value,
    )


class LLMClient:
    """Lightweight DeepSeek client with rules-only fallback."""

    def __init__(self) -> None:
        _load_dotenv_into_environ()
        provider_hint = (os.getenv("KE_LLM_PROVIDER") or "").strip().lower()
        deepseek_key = (
            os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("KE_LLM_API_KEY")
            or os.getenv("API_KEY")
            or ""
        ).strip()

        if provider_hint == "local":
            self.provider = "local"
        elif deepseek_key:
            # Default all LLM calls to DeepSeek.
            self.provider = "deepseek"
        else:
            self.provider = "local"

        api_key = deepseek_key
        default_base = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1"
        default_model = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"
        self.base_url = (
            os.getenv("KE_LLM_BASE_URL")
            or default_base
        ).rstrip("/")
        self.model = (
            os.getenv("KE_LLM_MODEL")
            or default_model
        ).strip()
        self.clean_batch_size = max(1, int((os.getenv("KE_LLM_CLEAN_BATCH_SIZE") or "1").strip() or "1"))
        self.timeout_sec = max(5, int((os.getenv("KE_LLM_TIMEOUT_SEC") or "45").strip() or "45"))
        self.max_retries = max(0, int((os.getenv("KE_LLM_MAX_RETRIES") or "3").strip() or "3"))
        self.retry_base_sec = max(1, int((os.getenv("KE_LLM_RETRY_BASE_SEC") or "2").strip() or "2"))
        self.max_remote_calls = max(0, int((os.getenv("KE_LLM_MAX_REMOTE_CALLS") or "0").strip() or "0"))
        self.max_prompt_chars_total = max(
            0,
            int((os.getenv("KE_LLM_MAX_PROMPT_CHARS_TOTAL") or "0").strip() or "0"),
        )
        self.max_response_chars_total = max(
            0,
            int((os.getenv("KE_LLM_MAX_RESPONSE_CHARS_TOTAL") or "0").strip() or "0"),
        )
        cache_enabled_raw = (os.getenv("KE_LLM_CACHE_ENABLED") or "1").strip().lower()
        self.cache_enabled = cache_enabled_raw not in {"0", "false", "no", "off"}
        default_cache_dir = PROJECT_ROOT / "tmp" / "llm_cache"
        self.cache_dir = Path((os.getenv("KE_LLM_CACHE_DIR") or str(default_cache_dir)).strip() or str(default_cache_dir))
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._metrics_lock = threading.Lock()
        self._metrics: dict[str, int] = {
            "requests_total": 0,
            "cache_hits": 0,
            "cache_writes": 0,
            "remote_calls": 0,
            "budget_rejections": 0,
            "prompt_chars_sent": 0,
            "response_chars_received": 0,
            "api_prompt_tokens": 0,
            "api_completion_tokens": 0,
            "api_total_tokens": 0,
        }
        self._api_key = api_key

        if self.provider == "local":
            self.model = "rules-only"

    @staticmethod
    def _estimate_message_chars(messages: list[dict]) -> int:
        total = 0
        for message in messages:
            content = message.get("content")
            if isinstance(content, str):
                total += len(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        text = part.get("text")
                        if isinstance(text, str):
                            total += len(text)
        return total

    def _cache_key(self, *, messages: list[dict], json_mode: bool) -> str:
        payload = {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "json_mode": json_mode,
            "messages": messages,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _cache_read(self, key: str) -> str:
        if not self.cache_enabled:
            return ""
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            return ""
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ""
        content = cached.get("content")
        if isinstance(content, str):
            return content
        return ""

    def _cache_write(self, *, key: str, content: str, prompt_chars: int, json_mode: bool) -> None:
        if not self.cache_enabled:
            return
        payload = {
            "model": self.model,
            "provider": self.provider,
            "json_mode": bool(json_mode),
            "prompt_chars": prompt_chars,
            "content": content,
        }
        path = self.cache_dir / f"{key}.json"
        temp_path = path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(path)
        except OSError:
            return
        with self._metrics_lock:
            self._metrics["cache_writes"] += 1

    def _reserve_budget(self, prompt_chars: int) -> str:
        with self._metrics_lock:
            if self.max_remote_calls and self._metrics["remote_calls"] >= self.max_remote_calls:
                self._metrics["budget_rejections"] += 1
                return f"LLM budget exceeded: max remote calls {self.max_remote_calls}"
            if (
                self.max_prompt_chars_total
                and self._metrics["prompt_chars_sent"] + prompt_chars > self.max_prompt_chars_total
            ):
                self._metrics["budget_rejections"] += 1
                return (
                    "LLM budget exceeded: max prompt chars "
                    f"{self.max_prompt_chars_total}"
                )
        return ""

    def _consume_response_budget(self, response_chars: int) -> str:
        with self._metrics_lock:
            if (
                self.max_response_chars_total
                and self._metrics["response_chars_received"] + response_chars > self.max_response_chars_total
            ):
                self._metrics["budget_rejections"] += 1
                return (
                    "LLM budget exceeded: max response chars "
                    f"{self.max_response_chars_total}"
                )
        return ""

    def get_metrics(self) -> dict:
        with self._metrics_lock:
            metrics = dict(self._metrics)
        metrics["provider"] = self.provider
        metrics["model"] = self.model
        metrics["cache_enabled"] = self.cache_enabled
        metrics["cache_dir"] = str(self.cache_dir)
        metrics["max_remote_calls"] = self.max_remote_calls
        metrics["max_prompt_chars_total"] = self.max_prompt_chars_total
        metrics["max_response_chars_total"] = self.max_response_chars_total
        return metrics

    def _post_chat_completion(self, *, messages: list[dict], json_mode: bool = False) -> str:
        with self._metrics_lock:
            self._metrics["requests_total"] += 1

        prompt_chars = self._estimate_message_chars(messages)
        cache_key = self._cache_key(messages=messages, json_mode=json_mode)
        cached_content = self._cache_read(cache_key)
        if cached_content:
            with self._metrics_lock:
                self._metrics["cache_hits"] += 1
            return cached_content

        budget_error = self._reserve_budget(prompt_chars)
        if budget_error:
            raise RuntimeError(budget_error)

        endpoint = self.base_url
        if not endpoint.lower().endswith("/chat/completions"):
            endpoint = f"{endpoint}/chat/completions"

        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": messages,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urlrequest.Request(
            url=endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        raw = ""
        for attempt in range(self.max_retries + 1):
            try:
                with urlrequest.urlopen(req, timeout=self.timeout_sec) as response:
                    raw = response.read().decode("utf-8")
                break
            except urlerror.HTTPError as exc:
                details = exc.read().decode("utf-8", errors="ignore")
                retryable = exc.code in {429, 500, 502, 503, 504}
                if retryable and attempt < self.max_retries:
                    sleep_sec = self.retry_base_sec * (2**attempt)
                    time.sleep(sleep_sec)
                    continue
                raise RuntimeError(f"LLM HTTP {exc.code}: {details[:240]}") from exc
            except urlerror.URLError as exc:
                if attempt < self.max_retries:
                    sleep_sec = self.retry_base_sec * (2**attempt)
                    time.sleep(sleep_sec)
                    continue
                raise RuntimeError(f"LLM network error: {exc.reason}") from exc
            except (TimeoutError, socket.timeout, OSError) as exc:
                if attempt < self.max_retries:
                    sleep_sec = self.retry_base_sec * (2**attempt)
                    time.sleep(sleep_sec)
                    continue
                raise RuntimeError(f"LLM network error: {exc}") from exc

        with self._metrics_lock:
            self._metrics["remote_calls"] += 1
            self._metrics["prompt_chars_sent"] += prompt_chars

        try:
            parsed = json.loads(raw)
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("LLM response format invalid") from exc

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            content = "\n".join(parts)
        if not isinstance(content, str):
            raise RuntimeError("LLM response content is not text")
        content = content.strip()

        response_budget_error = self._consume_response_budget(len(content))
        if response_budget_error:
            raise RuntimeError(response_budget_error)

        usage = parsed.get("usage", {}) if isinstance(parsed, dict) else {}
        with self._metrics_lock:
            self._metrics["response_chars_received"] += len(content)
            if isinstance(usage, dict):
                self._metrics["api_prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
                self._metrics["api_completion_tokens"] += int(usage.get("completion_tokens") or 0)
                self._metrics["api_total_tokens"] += int(usage.get("total_tokens") or 0)

        self._cache_write(
            key=cache_key,
            content=content,
            prompt_chars=prompt_chars,
            json_mode=json_mode,
        )
        return content

    def call(self, prompt: str) -> dict:
        if self.provider == "local":
            return {"cleaned_text": prompt}

        messages = [
            {
                "role": "system",
                "content": "You clean OCR text conservatively. Preserve formulas and references exactly.",
            },
            {"role": "user", "content": prompt},
        ]
        cleaned = self._post_chat_completion(messages=messages, json_mode=False)
        return {"cleaned_text": cleaned or prompt}

    def review_block_semantics(
        self,
        *,
        block_text: str,
        subsection: str,
        default_type: str,
        rule_formula_labels: List[str],
        candidate_formula_labels: List[str],
    ) -> dict:
        if self.provider == "local":
            return {}

        candidate_sample = candidate_formula_labels[:200]
        payload = {
            "task": "Classify one semantic block and verify formula references.",
            "constraints": {
                "allowed_types": ["discussion", "definition", "proposition", "derivation"],
                "formula_labels_must_come_from_candidates": True,
                "candidate_formula_labels": candidate_sample,
                "do_not_rewrite_block_content": True,
            },
            "input": {
                "subsection": subsection,
                "block_text": block_text,
                "rule_default_type": default_type,
                "rule_formula_labels": rule_formula_labels,
            },
            "output_schema": {
                "type": "discussion|definition|proposition|derivation",
                "formula_reference_labels": ["6.17a"],
                "notes": "brief reason",
            },
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Return strict JSON only. Do not include markdown. "
                    "Keep formula_reference_labels minimal and exact. "
                    "Never rewrite block content."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]

        raw = self._post_chat_completion(messages=messages, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}\s*$", raw)
            if not match:
                raise RuntimeError("LLM semantic review did not return valid JSON")
            return json.loads(match.group(0))

    def review_chunk_semantics(
        self,
        *,
        chapter_name: str,
        chunk_index: int,
        subsection_hints: List[str],
        chunk_blocks: List[dict],
        formulas: List[dict],
        phase: int = 1,
        allow_type_override: bool = True,
        allow_new_formula_refs: bool = True,
    ) -> dict:
        if self.provider == "local":
            return {}

        payload = {
            "task": "Audit one chunk: verify each block type and formula references.",
            "constraints": {
                "allowed_types": ["discussion", "definition", "proposition", "derivation"],
                "formula_references_must_come_from_formulas_list": True,
                "do_not_rewrite_block_content": True,
                "allow_type_override": bool(allow_type_override),
                "allow_new_formula_references_for_empty_blocks": bool(allow_new_formula_refs),
            },
            "chunk": {
                "chapter": chapter_name,
                "chunk_index": chunk_index,
                "phase": int(phase),
                "subsection_hints": subsection_hints,
                "blocks": chunk_blocks,
                "formulas": formulas,
            },
            "output_schema": {
                "blocks": [
                    {
                        "index": 1,
                        "type": "discussion|definition|proposition|derivation",
                        "formula_reference_labels": ["6.17a"],
                        "confidence": 0.93,
                        "reason": "short reason",
                    }
                ]
            },
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Return strict JSON only. One output item per input block index. "
                    "Keep formula_reference_labels minimal and exact. "
                    "Never rewrite, summarize, or alter any block content."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
        raw = self._post_chat_completion(messages=messages, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}\s*$", raw)
            if not match:
                raise RuntimeError("LLM chunk semantic review did not return valid JSON")
            return json.loads(match.group(0))


@dataclass
class KnowledgeBlock:
    type: str
    content: str

    def to_dict(self) -> dict:
        return {"type": self.type, "content": self.content}


@dataclass
class KnowledgeUnit:
    id: str
    chapter: str
    section: str
    subsections: List[str]
    source_file: str
    blocks: List[KnowledgeBlock] = field(default_factory=list)
    formula_references: List[str] = field(default_factory=list)
    table_references: List[str] = field(default_factory=list)
    source_title: str | None = None
    table_reference_keys: List[str] = field(default_factory=list)
    section_level_1: str | None = None
    section_level_2: str | None = None
    heading_path: List[str] = field(default_factory=list)
    display_heading: str | None = None
    chapter_title: str | None = None

    def _canonical_heading_metadata(self) -> tuple[str, list[str], str | None, str | None, list[str], str]:
        def clean(value: object) -> str:
            return str(value or "").strip()

        heading_path = [clean(item) for item in self.heading_path if clean(item)]
        level_1 = clean(self.section_level_1) or (heading_path[0] if heading_path else "")
        level_2 = clean(self.section_level_2) or (heading_path[1] if len(heading_path) > 1 else "")
        display = clean(self.display_heading)

        if not level_1:
            legacy_section = clean(self.section)
            if legacy_section:
                level_1 = legacy_section
            elif heading_path:
                level_1 = heading_path[0]
            elif display:
                level_1 = display

        if level_2 and level_2 == level_1:
            level_2 = ""

        canonical_path = [item for item in [level_1, level_2] if item]
        if not canonical_path and heading_path:
            canonical_path = heading_path
            level_1 = canonical_path[0]
            level_2 = canonical_path[1] if len(canonical_path) > 1 else ""

        if not display:
            display = level_2 or level_1 or clean(self.section) or "Introduction"

        section = level_1 or display
        subsections = [level_2] if level_2 else []
        return section, subsections, level_1 or None, level_2 or None, canonical_path, display

    def to_dict(self) -> dict:
        (
            section,
            subsections,
            section_level_1,
            section_level_2,
            heading_path,
            display_heading,
        ) = self._canonical_heading_metadata()
        metadata = {
            "chapter": self.chapter,
            "section": section,
            "subsections": subsections,
            "source_file": self.source_file,
            "source_title": self.source_title or DEFAULT_SOURCE_TITLE,
            "formula_references": self.formula_references,
            "table_references": self.table_references,
        }
        if self.chapter_title:
            metadata["chapter_title"] = self.chapter_title
        if section_level_1 is not None:
            metadata["section_level_1"] = section_level_1
        if section_level_2 is not None:
            metadata["section_level_2"] = section_level_2
        elif section_level_1 is not None:
            metadata["section_level_2"] = None
        if heading_path:
            metadata["heading_path"] = heading_path
        if display_heading:
            metadata["display_heading"] = display_heading
        if self.table_reference_keys:
            metadata["table_reference_keys"] = self.table_reference_keys
        return {
            "id": self.id,
            "metadata": metadata,
            "blocks": [block.to_dict() for block in self.blocks],
        }

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class TableEntry:
    id: str
    label_format: str
    title: str
    table_type: str
    html: str
    rows: list[list[str]] = field(default_factory=list)
    source: dict = field(default_factory=dict)
    description: str | None = None
    raw_body: str | None = None
    markdown_body: str | None = None

    def to_dict(self) -> dict:
        payload = {
            "id": self.id,
            "label_format": self.label_format,
            "title": self.title,
            "table_type": self.table_type,
            "html": self.html,
            "rows": self.rows,
            "source": self.source,
            "description": self.description,
        }
        if self.raw_body is not None:
            payload["raw_body"] = self.raw_body
        if self.markdown_body is not None:
            payload["markdown_body"] = self.markdown_body
        return payload


@dataclass
class TableLibrary:
    tables: list[TableEntry] = field(default_factory=list)

    @classmethod
    def load(cls, input_path: str) -> "TableLibrary":
        path = Path(input_path)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        tables = [
            TableEntry(
                id=item.get("id", ""),
                label_format=item.get("label_format", ""),
                title=item.get("title", ""),
                table_type=item.get("table_type", "numbered"),
                html=item.get("html", ""),
                rows=item.get("rows", []),
                source=item.get("source", {}),
                description=item.get("description"),
                raw_body=item.get("raw_body"),
                markdown_body=item.get("markdown_body"),
            )
            for item in data.get("tables", [])
            if item.get("id")
        ]
        return cls(tables=tables)

    def remove_by_chapter(self, chapter_name: str) -> int:
        before = len(self.tables)
        self.tables = [entry for entry in self.tables if entry.source.get("chapter") != chapter_name]
        return before - len(self.tables)

    def to_dict(self) -> dict:
        numbered_tables = sum(1 for table in self.tables if table.table_type == "numbered")
        inline_tables = sum(1 for table in self.tables if table.table_type == "inline")
        return {
            "metadata": {
                "total_tables": len(self.tables),
                "numbered_tables": numbered_tables,
                "inline_tables": inline_tables,
            },
            "tables": [table.to_dict() for table in self.tables],
        }

    def save(self, output_path: str) -> None:
        self.tables = sorted(
            self.tables,
            key=lambda entry: (
                _chapter_sort_key(entry.source.get("chapter", "")),
                _label_sort_key(entry.id),
                str(entry.id).lower(),
            ),
        )
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def get_stats(self) -> dict:
        return {
            "total": len(self.tables),
            "numbered": sum(1 for entry in self.tables if entry.table_type == "numbered"),
            "inline": sum(1 for entry in self.tables if entry.table_type == "inline"),
        }


@dataclass
class Formula:
    id: str
    latex: str
    formula_type: str
    label_format: str
    source: dict
    context: str = ""
    description: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label_format": self.label_format,
            "latex": self.latex,
            "formula_type": self.formula_type,
            "source": self.source,
            "context": self.context,
            "description": self.description,
        }


@dataclass
class FormulaLibrary:
    formulas: List[Formula] = field(default_factory=list)

    LABEL_PATTERN = re.compile(r"^(?:a\d+|\d+)\.\d+(?:\.\d+)?[a-zA-Z]?$", re.IGNORECASE)
    FORMULA_BLOCK_PATTERN = re.compile(
        r"\$\$\s*(?P<latex>[\s\S]*?)\s*\$\$\s*(?:\((?P<label>(?:A\d+|\d+)\.\d+(?:\.\d+)?[A-Za-z]?)\))?",
        re.IGNORECASE,
    )
    PLACEHOLDER_PATTERN = re.compile(r"__FORMULA_REF_(?P<label>[0-9A-Za-z._]+)__")

    @classmethod
    def reference_id(cls, label: str) -> str:
        return f"formula_{label.lower()}"

    @classmethod
    def placeholder_for_label(cls, label: str) -> str:
        return f"__FORMULA_REF_{label.lower()}__"

    @classmethod
    def _render_reference(cls, label: str) -> str:
        return f"见公式({label.lower()})"

    @staticmethod
    def _canonical_latex(latex: str) -> str:
        cleaned = (latex or "").strip()
        cleaned = cleaned.replace("\\left", "").replace("\\right", "")
        cleaned = re.sub(r"\s+", "", cleaned)
        return cleaned

    @staticmethod
    def _build_context(text: str, start: int, end: int, window: int = 200) -> str:
        left = max(0, start - window)
        right = min(len(text), end + window)
        return text[left:right].strip()

    @staticmethod
    def _label_matches_chapter(label: str, source_chapter: str) -> bool:
        chapter_match = re.search(r"chapter\s*(\d+)", source_chapter, flags=re.IGNORECASE)
        appendix_match = re.search(r"appendix\s*(\d+)", source_chapter, flags=re.IGNORECASE)
        try:
            label_chapter = str(label or "").split(".", 1)[0].lower()
            if chapter_match:
                return label_chapter == chapter_match.group(1).lower()
            if appendix_match:
                return label_chapter == f"a{appendix_match.group(1).lower()}"
            return True
        except (ValueError, IndexError):
            return False

    def get_formula(self, label: str, source_chapter: str = "") -> Formula | None:
        wanted = (label or "").strip().lower()
        for formula in self.formulas:
            if formula.id != wanted:
                continue
            if source_chapter and formula.source.get("chapter") != source_chapter:
                continue
            return formula
        return None

    def get_labels(self, source_chapter: str = "") -> List[str]:
        labels: List[str] = []
        for formula in self.formulas:
            label = (formula.id or "").strip().lower()
            if not label:
                continue
            if source_chapter and formula.source.get("chapter") != source_chapter:
                continue
            if label not in labels:
                labels.append(label)
        return labels

    def add_formula(
        self,
        *,
        label: str,
        label_format: str,
        latex: str,
        formula_type: str,
        source_unit_id: str,
        source_chapter: str,
        source_subsection: str,
        context: str = "",
    ) -> Formula | None:
        normalized_label = (label or "").strip().lower()
        if not self.LABEL_PATTERN.fullmatch(normalized_label):
            return None
        if not self._label_matches_chapter(normalized_label, source_chapter):
            return None

        existing = self.get_formula(normalized_label, source_chapter=source_chapter)
        if existing:
            if self._canonical_latex(existing.latex) == self._canonical_latex(latex):
                return existing
            return None

        formula = Formula(
            id=normalized_label,
            label_format=label_format or f"({normalized_label})",
            latex=(latex or "").strip(),
            formula_type=formula_type or "block",
            source={
                "unit_id": source_unit_id,
                "chapter": source_chapter,
                "subsection": source_subsection,
            },
            context=context,
        )
        self.formulas.append(formula)
        return formula

    def _find_known_label_by_latex(self, latex: str, source_chapter: str) -> str:
        canonical = self._canonical_latex(latex)
        for formula in self.formulas:
            if formula.source.get("chapter") != source_chapter:
                continue
            if self._canonical_latex(formula.latex) == canonical:
                return formula.id
        return ""

    def consume_formula_placeholders(self, text: str) -> tuple[str, List[str]]:
        refs: List[str] = []

        def _replace(match: re.Match[str]) -> str:
            label = match.group("label").lower()
            ref_id = self.reference_id(label)
            if ref_id not in refs:
                refs.append(ref_id)
            return self._render_reference(label)

        rendered = self.PLACEHOLDER_PATTERN.sub(_replace, text or "")
        return rendered, refs

    def extract_add_and_replace(
        self,
        *,
        text: str,
        source_unit_id: str,
        source_chapter: str,
        source_subsection: str,
    ) -> tuple[str, List[str]]:
        refs: List[str] = []
        replacements: list[tuple[int, int, str]] = []

        for match in self.FORMULA_BLOCK_PATTERN.finditer(text or ""):
            latex = (match.group("latex") or "").strip()
            label = (match.group("label") or "").strip().lower()
            if not latex:
                continue
            if not label:
                label = self._find_known_label_by_latex(latex, source_chapter)
            if not label:
                continue
            if not self._label_matches_chapter(label, source_chapter):
                continue

            self.add_formula(
                label=label,
                label_format=f"({label})",
                latex=latex,
                formula_type="block",
                source_unit_id=source_unit_id,
                source_chapter=source_chapter,
                source_subsection=source_subsection,
                context=self._build_context(text, match.start(), match.end()),
            )

            ref_id = self.reference_id(label)
            if ref_id not in refs:
                refs.append(ref_id)
            replacements.append((match.start(), match.end(), self.placeholder_for_label(label)))

        working = text or ""
        for start, end, replacement in sorted(replacements, key=lambda item: item[0], reverse=True):
            working = f"{working[:start]}{replacement}{working[end:]}"

        for ref_id in refs:
            label = ref_id.removeprefix("formula_")
            working = working.replace(self.placeholder_for_label(label), self._render_reference(label))

        working = re.sub(r"[ \t]+", " ", working)
        working = re.sub(r" *\n *", "\n", working)
        working = re.sub(r"\n{3,}", "\n\n", working)
        return working.strip(), refs

    def replace_known_formula_references(
        self,
        *,
        text: str,
        source_chapter: str,
    ) -> tuple[str, List[str]]:
        refs: List[str] = []
        replacements: list[tuple[int, int, str]] = []

        for match in self.FORMULA_BLOCK_PATTERN.finditer(text or ""):
            latex = (match.group("latex") or "").strip()
            if not latex:
                continue
            label = self._find_known_label_by_latex(latex, source_chapter=source_chapter)
            if not label:
                continue
            ref_id = self.reference_id(label)
            if ref_id not in refs:
                refs.append(ref_id)
            replacements.append((match.start(), match.end(), self.placeholder_for_label(label)))

        working = text or ""
        for start, end, replacement in sorted(replacements, key=lambda item: item[0], reverse=True):
            working = f"{working[:start]}{replacement}{working[end:]}"
        for ref_id in refs:
            label = ref_id.removeprefix("formula_")
            working = working.replace(self.placeholder_for_label(label), self._render_reference(label))
        return working.strip(), refs

    @classmethod
    def load(cls, input_path: str) -> "FormulaLibrary":
        path = Path(input_path)
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        formulas = [
            Formula(
                id=item.get("id", ""),
                latex=item.get("latex", ""),
                formula_type=item.get("formula_type", "block"),
                label_format=item.get("label_format", ""),
                source=item.get("source", {}),
                context=item.get("context", ""),
                description=item.get("description"),
            )
            for item in data.get("formulas", [])
            if item.get("id")
        ]
        return cls(formulas=formulas)

    def remove_by_chapter(self, chapter_name: str) -> int:
        before = len(self.formulas)
        self.formulas = [f for f in self.formulas if f.source.get("chapter") != chapter_name]
        return before - len(self.formulas)

    def save(self, output_path: str) -> None:
        self.formulas = sorted(
            self.formulas,
            key=lambda formula: (
                _chapter_sort_key(formula.source.get("chapter", "")),
                _label_sort_key(formula.id),
                str(formula.id).lower(),
            ),
        )
        payload = {
            "metadata": {
                "total_formulas": len(self.formulas),
                "block_formulas": sum(1 for f in self.formulas if f.formula_type == "block"),
                "inline_formulas": sum(1 for f in self.formulas if f.formula_type == "inline"),
            },
            "formulas": [f.to_dict() for f in self.formulas],
        }
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_stats(self) -> dict:
        return {
            "total": len(self.formulas),
            "block": sum(1 for f in self.formulas if f.formula_type == "block"),
            "inline": sum(1 for f in self.formulas if f.formula_type == "inline"),
        }


@dataclass
class SemanticBlock:
    type: str
    content: str
    subsection: str
    formula_references: List[str] = field(default_factory=list)
    section_level_1: str | None = None
    section_level_2: str | None = None
    heading_path: List[str] = field(default_factory=list)
    display_heading: str | None = None

    @property
    def word_count(self) -> int:
        return len((self.content or "").split())


@dataclass
class CompositeChunk:
    blocks: List[SemanticBlock]

    @property
    def subsections(self) -> List[str]:
        seen: List[str] = []
        for block in self.blocks:
            subsection = (block.subsection or block.display_heading or "").strip()
            if subsection and subsection not in seen:
                seen.append(subsection)
        return seen

    @property
    def section_level_1(self) -> str | None:
        for block in self.blocks:
            value = (block.section_level_1 or "").strip()
            if value:
                return value
        return None

    @property
    def section_level_2(self) -> str | None:
        for block in self.blocks:
            value = (block.section_level_2 or "").strip()
            if value:
                return value
        return None

    @property
    def heading_path(self) -> List[str]:
        seen: List[str] = []
        for block in self.blocks:
            candidates = block.heading_path or [
                item for item in [block.section_level_1, block.section_level_2] if item
            ]
            for item in candidates:
                heading = (item or "").strip()
                if heading and heading not in seen:
                    seen.append(heading)
        if seen:
            return seen
        return self.subsections

    @property
    def display_heading(self) -> str:
        for block in self.blocks:
            value = (block.display_heading or block.subsection or "").strip()
            if value:
                return value
        path = self.heading_path
        return path[-1] if path else "Introduction"

    @property
    def word_count(self) -> int:
        return sum(block.word_count for block in self.blocks)


CAPTION_PARAGRAPH_PATTERN = re.compile(
    r"^(?:Figure|Fig\.|Table)\s+\d+(?:\.\d+)?[A-Za-z]?(?:[:.\-])?\s+(?P<rest>.+)$",
    re.IGNORECASE,
)
BODY_REFERENCE_LEAD_VERBS = {
    "show",
    "shows",
    "illustrate",
    "illustrates",
    "depict",
    "depicts",
    "summarize",
    "summarizes",
    "present",
    "presents",
    "compare",
    "compares",
    "report",
    "reports",
    "give",
    "gives",
}


def _normalize_heading(line: str) -> str:
    return re.sub(r"^#+\s*", "", line).strip()


ORDERED_LIST_ITEM_PATTERN = re.compile(r"^\d{1,2}[.)]\s+\S.*[.!?]\s*$")


def _looks_like_ordered_list_item(line: str) -> bool:
    return bool(ORDERED_LIST_ITEM_PATTERN.match(_normalize_heading(line)))


def _is_major_heading(line: str) -> bool:
    normalized = _normalize_heading(line)
    if not normalized:
        return False
    alpha_ratio = sum(char.isalpha() for char in normalized) / max(len(normalized), 1)
    return len(normalized) > 8 and normalized.isupper() and "$" not in normalized and alpha_ratio > 0.65


def _markdown_heading_level(line: str) -> tuple[int | None, str]:
    match = re.match(r"^(?P<marks>#{1,6})\s*(?P<title>.+?)\s*$", line or "")
    if not match:
        return None, _normalize_heading(line)
    return len(match.group("marks")), _normalize_heading(match.group("title"))


def _semantic_heading_level(title: str, markdown_level: int | None, current_level_1: str) -> int:
    normalized = _normalize_heading(title)
    if not normalized:
        return 2
    if _looks_like_ordered_list_item(normalized):
        return 2
    if markdown_level is not None and markdown_level >= 2:
        return 2
    if _is_major_heading(normalized):
        return 1
    if not current_level_1 or current_level_1 == "Introduction":
        return 1
    return 2


def _split_sections(text: str) -> List[dict]:
    sections = []
    current_level_1 = "Introduction"
    current_level_2: str | None = None
    current_heading = "Introduction"
    current_lines: List[str] = []

    def flush() -> None:
        content = "\n".join(current_lines).strip()
        if content:
            level_1 = (current_level_1 or current_heading or "Introduction").strip()
            level_2 = (current_level_2 or "").strip() or None
            heading_path = [level_1]
            if level_2 and level_2 != level_1:
                heading_path.append(level_2)
            display_heading = level_2 or level_1
            sections.append(
                {
                    "subsection": display_heading,
                    "content": content,
                    "section_level_1": level_1,
                    "section_level_2": level_2,
                    "heading_path": heading_path,
                    "display_heading": display_heading,
                }
            )

    for raw_line in (text or "").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("--- Page"):
            continue
        if stripped.startswith("#"):
            markdown_level, title = _markdown_heading_level(stripped)
            title = title or current_heading
            if _looks_like_ordered_list_item(title):
                current_lines.append(title)
                continue
            flush()
            semantic_level = _semantic_heading_level(title, markdown_level, current_level_1)
            if semantic_level == 1:
                current_level_1 = title
                current_level_2 = None
            else:
                if not current_level_1:
                    current_level_1 = "Introduction"
                current_level_2 = title
            current_heading = current_level_2 or current_level_1 or title
            current_lines = []
            continue
        if _is_major_heading(stripped):
            flush()
            current_level_1 = _normalize_heading(stripped)
            current_level_2 = None
            current_heading = current_level_1
            current_lines = []
            continue
        current_lines.append(raw_line)

    flush()
    return sections


def _normalize_paragraph(text: str) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return " ".join(lines).strip()


def _is_caption_paragraph(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip()
    match = CAPTION_PARAGRAPH_PATTERN.match(normalized)
    if not match:
        return False

    rest = match.group("rest").strip()
    if not rest:
        return False

    first_word_match = re.search(r"[A-Za-z][A-Za-z-]*", rest)
    if not first_word_match:
        return False

    first_word = first_word_match.group(0).lower()
    if first_word in BODY_REFERENCE_LEAD_VERBS:
        return False

    return rest[:1].isupper()


def _is_formula_dense(text: str) -> bool:
    formula_markers = ["$$", "\\begin", "\\frac", "\\sum", "\\int", "\\left", "\\right"]
    return any(marker in text for marker in formula_markers)


def _should_merge(previous: str, current: str) -> bool:
    if not previous:
        return False

    if re.match(r"^(Example|Theorem|Lemma|Proposition|Assumption|Corollary|Note)\s+\w*", current):
        return False

    continuation_prefixes = (
        "where ",
        "which ",
        "that ",
        "and ",
        "or ",
        "but ",
        "because ",
        "thus ",
        "therefore ",
        "hence ",
        "whereas ",
        "namely ",
        "with ",
        "from ",
        "as ",
        "in which ",
    )
    lower_current = current.lower()

    if current[:1].islower():
        return True
    if lower_current.startswith(continuation_prefixes):
        return True
    if previous.endswith(("=", ",", ";", ":", "(")):
        return True
    if len(current.split()) < 80 and _is_formula_dense(current):
        return True
    return False


def _split_section_into_paragraphs(content: str) -> List[str]:
    raw_paragraphs = [_normalize_paragraph(part) for part in re.split(r"\n\s*\n+", content or "")]
    raw_paragraphs = [part for part in raw_paragraphs if part and not _is_caption_paragraph(part)]

    merged: List[str] = []
    for paragraph in raw_paragraphs:
        if merged and _should_merge(merged[-1], paragraph):
            merged[-1] = f"{merged[-1]} {paragraph}".strip()
        else:
            merged.append(paragraph)
    return merged


def _classify_block_type(text: str, formula_refs: List[str]) -> str:
    lower = (text or "").lower()
    if formula_refs or "见公式(" in lower:
        return "derivation"
    if re.search(r"\b(theorem|lemma|proposition|corollary|assumption)\b", lower):
        return "proposition"
    if re.search(r"\bdefinition\b", lower):
        return "definition"
    return "discussion"


def extract_semantic_blocks(
    text: str,
    chapter_name: str,
    client: LLMClient | None,
    formula_library: FormulaLibrary,
) -> tuple[List[SemanticBlock], dict]:
    del client
    raw_blocks: List[SemanticBlock] = []

    for section in _split_sections(text):
        for paragraph in _split_section_into_paragraphs(section["content"]):
            block_index = len(raw_blocks) + 1
            content, placeholder_refs = formula_library.consume_formula_placeholders(paragraph)
            content, extracted_refs = formula_library.extract_add_and_replace(
                text=content,
                source_unit_id=f"{chapter_name}_block_{block_index:03d}",
                source_chapter=chapter_name,
                source_subsection=section["subsection"],
            )
            content, known_refs = formula_library.replace_known_formula_references(
                text=content,
                source_chapter=chapter_name,
            )

            refs: List[str] = []
            for ref in [*placeholder_refs, *extracted_refs, *known_refs]:
                if ref not in refs:
                    refs.append(ref)

            raw_blocks.append(
                SemanticBlock(
                    type=_classify_block_type(content, refs),
                    content=content,
                    subsection=section["subsection"],
                    formula_references=refs,
                    section_level_1=section.get("section_level_1"),
                    section_level_2=section.get("section_level_2"),
                    heading_path=list(section.get("heading_path") or []),
                    display_heading=section.get("display_heading") or section["subsection"],
                )
            )

    counts: Dict[str, int] = {}
    for block in raw_blocks:
        counts[block.type] = counts.get(block.type, 0) + 1

    return raw_blocks, {"classification_stats": {"counts": counts, "warnings": []}}


def build_composite_chunks(blocks: List[SemanticBlock]) -> List[CompositeChunk]:
    """Group blocks into chunks by heading boundary. One subsection = one chunk."""
    if not blocks:
        return []
    chunks: List[CompositeChunk] = []
    current: List[SemanticBlock] = []
    current_heading_key = tuple(blocks[0].heading_path or [blocks[0].subsection])
    def flush() -> None:
        nonlocal current
        if current:
            chunks.append(CompositeChunk(blocks=current))
            current = []
    for block in blocks:
        block_heading_key = tuple(block.heading_path or [block.subsection])
        if current and block_heading_key != current_heading_key:
            flush()
            current_heading_key = block_heading_key
        elif not current:
            current_heading_key = block_heading_key
        current.append(block)
    flush()
    return chunks


def clean_page_batch(pages: List[str], client: LLMClient | None, batch_size: int = 1) -> List[str]:
    del client, batch_size
    return pages


TOC_SKIP_PATTERNS = [
    r"^!?\[\]\(page=.*bbox=.*\)$",
    r"^\${1,2}.*\${1,2}$",
    r"^[A-Z]{8,}$",
    r"photo\s+credits?",
    r"photo\s+by",
    r"copyright",
    r"all rights reserved",
    r"university press",
    r"isbn",
    r"^doi",
    r"published in",
]


def _normalize_line(text: str) -> str:
    text = (text or "").replace("\t", " ").strip()
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s*\.\.{2,}\s*", " ", text)
    return text


def _extract_toc_lines(lines: List[str]) -> List[str]:
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r"^contents$", line, flags=re.IGNORECASE):
            start_idx = i + 1
            break

    filtered: List[str] = []
    for line in lines[start_idx:]:
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in TOC_SKIP_PATTERNS):
            continue
        if re.match(r"^.+\s+\d{1,4}$", line):
            filtered.append(line)
    return filtered


def _classify_entry(title: str) -> Tuple[str, int]:
    if re.match(r"^[IVXLCDM]+\.\s+[A-Z]", title):
        return "part", 0
    if re.match(r"^\d+\.\s+[A-Z]", title):
        return "chapter", 1
    if re.search(r"appendix|appendices|附录", title, re.IGNORECASE):
        return "appendix", 1
    if re.search(r"index|索引", title, re.IGNORECASE):
        return "index", 1
    if re.search(r"reference|literature|cited", title, re.IGNORECASE):
        return "literature_cited", 1
    if title and title[0].islower():
        return "subsection", 3
    return "section", 2


def _parse_toc_entries(lines: List[str]) -> List[dict]:
    entries = []
    for line in lines:
        match = re.match(r"^(?P<title>.+?)\s+(?P<page>\d{1,4})$", line)
        if not match:
            continue
        page = int(match.group("page"))
        if page >= 1900:
            continue
        title = match.group("title").strip(" -")
        entry_type, level = _classify_entry(title)
        entries.append({"title": title, "page": page, "entry_type": entry_type, "level": level})
    return entries


def _build_tree(entries: List[dict]) -> Tuple[Dict[str, dict], List[str]]:
    nodes: Dict[str, dict] = {}
    root_nodes: List[str] = []
    level_stack: Dict[int, str] = {}

    for idx, entry in enumerate(entries, start=1):
        node_id = f"toc_l{entry['level']}_{idx:04d}"
        parent_id = None
        for parent_level in range(entry["level"] - 1, -1, -1):
            if parent_level in level_stack:
                parent_id = level_stack[parent_level]
                break

        nodes[node_id] = {
            "id": node_id,
            "title": entry["title"],
            "level": entry["level"],
            "entry_type": entry["entry_type"],
            "page": entry["page"],
            "parent_id": parent_id,
            "children": [],
            "unit_id": None,
        }

        if parent_id:
            nodes[parent_id]["children"].append(node_id)
        else:
            root_nodes.append(node_id)

        level_stack[entry["level"]] = node_id
        for key in list(level_stack.keys()):
            if key > entry["level"]:
                del level_stack[key]

    return nodes, root_nodes


def _build_navigation_units(
    nodes: Dict[str, dict],
    root_nodes: List[str],
    chapter_name: str,
    source_file: str,
    source_title: str,
) -> List[dict]:
    del root_nodes
    units: List[dict] = []
    seq = 1

    for node_id, node in sorted(nodes.items(), key=lambda item: (item[1]["page"], item[0])):
        if not node["children"]:
            continue
        if node["level"] > 2:
            continue

        child_ids = sorted(node["children"], key=lambda cid: nodes[cid]["page"])
        child_lines = [f"- {nodes[cid]['title']} (p.{nodes[cid]['page']})" for cid in child_ids]
        content = (
            f"TOC Navigation Node\n"
            f"Title: {node['title']}\n"
            f"Type: {node['entry_type']}\n"
            f"Page: {node['page']}\n"
            f"Children:\n" + "\n".join(child_lines)
        )

        unit_id = f"{chapter_name}_nav_{seq:03d}"
        units.append(
            {
                "id": unit_id,
                "type": "toc",
                "metadata": {
                    "chapter": chapter_name,
                    "section": "",
                    "subsection": "toc_navigation",
                    "source_file": source_file,
                    "source_title": source_title or DEFAULT_SOURCE_TITLE,
                    "toc_node_id": node_id,
                },
                "content": content,
                "formula_references": [],
            }
        )
        nodes[node_id]["unit_id"] = unit_id
        seq += 1
    return units
