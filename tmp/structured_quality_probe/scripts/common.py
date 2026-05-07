from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROBE_ROOT = PROJECT_ROOT / "tmp" / "structured_quality_probe"
REPORTS_DIR = PROBE_ROOT / "reports"
SAMPLES_DIR = PROBE_ROOT / "samples"
CACHE_DIR = PROBE_ROOT / "cache"
SCRIPTS_DIR = PROBE_ROOT / "scripts"

STRUCTURED_DIR = PROJECT_ROOT / "data" / "structured"
FORMULA_LIBRARY_PATH = STRUCTURED_DIR / "formula_library.json"
TABLE_LIBRARY_PATH = STRUCTURED_DIR / "table_library.json"

REQUESTED_PADDLE_DIR = PROJECT_ROOT / "data" / "paddle_output"
REQUESTED_GLMOCR_DIR = PROJECT_ROOT / "data" / "glmocr_output"
FALLBACK_PADDLE_DIR = PROJECT_ROOT / "tmp" / "paddle_output"
FALLBACK_GLMOCR_DIR = PROJECT_ROOT / "tmp" / "glmocr_output"


FORMULA_REF_RE = re.compile(r"\[\[(?:SEE_)?FORMULA\s*:\s*([^\]\n\r]+?)\s*\]\]", re.I)
TABLE_REF_RE = re.compile(r"\[\[(?:SEE_)?TABLE\s*:\s*([^\]\n\r]+?)\s*\]\]", re.I)
PLACEHOLDER_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE)\s*:\s*([^\]\n\r]+?)\s*\]\]", re.I)
PLACEHOLDER_START_RE = re.compile(r"\[\[(?:SEE_)?(?:FORMULA|TABLE)\s*:", re.I)
LATEX_COMMAND_RE = re.compile(r"\\([A-Za-z]+)\*?")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")

STRUCTURAL_LATEX_COMMANDS = {
    "begin",
    "end",
    "documentclass",
    "usepackage",
    "maketitle",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "label",
    "ref",
    "cite",
    "includegraphics",
    "caption",
    "centering",
    "hline",
    "item",
    "author",
    "title",
    "date",
    "geometry",
}

LATEX_LEAK_COMMANDS = {
    "documentclass",
    "usepackage",
    "maketitle",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "label",
    "ref",
    "cite",
    "includegraphics",
    "caption",
    "centering",
    "hline",
    "item",
    "author",
    "title",
    "date",
    "geometry",
    "footnote",
    "bibliography",
    "tableofcontents",
    "textbf",
    "textit",
    "emph",
}

FORMULA_LIKE_BLOCK_TYPES = {
    "formula",
    "equation",
    "math",
    "display_math",
    "derivation",
    "table",
}


def ensure_output_dirs() -> None:
    for path in (SCRIPTS_DIR, REPORTS_DIR, SAMPLES_DIR, CACHE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def relpath(path: Path | str) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def natural_key(value: str) -> list[Any]:
    parts = re.split(r"(\d+)", value)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def chapter_sort_key(chapter: str) -> tuple[Any, ...]:
    text = chapter.lower()
    if text in {"toc", "目录"}:
        return (-1, 0, text)
    m = re.match(r"chapter(\d+)$", text)
    if m:
        return (0, int(m.group(1)), text)
    m = re.match(r"appendix(\d+)$", text)
    if m:
        return (1, int(m.group(1)), text)
    return (2, *natural_key(text))


def structured_json_files() -> list[Path]:
    if not STRUCTURED_DIR.exists():
        return []
    excluded = {"formula_library.json", "table_library.json"}
    return sorted(
        [p for p in STRUCTURED_DIR.glob("*.json") if p.name not in excluded],
        key=lambda p: natural_key(p.name),
    )


def coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def snippet(text: str, limit: int = 220) -> str:
    one_line = re.sub(r"\s+", " ", text or "").strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 3].rstrip() + "..."


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        safe = [str(cell).replace("\n", "<br>").replace("|", "\\|") for cell in row]
        out.append("| " + " | ".join(safe) + " |")
    return "\n".join(out)


def clean_ref_id(raw: str) -> str:
    value = (raw or "").strip()
    return value.strip(" \t\r\n.,;:")


def extract_formula_refs(text: str) -> list[str]:
    return [clean_ref_id(m.group(1)) for m in FORMULA_REF_RE.finditer(text or "")]


def extract_table_refs(text: str) -> list[str]:
    return [clean_ref_id(m.group(1)) for m in TABLE_REF_RE.finditer(text or "")]


def count_placeholders(text: str) -> int:
    return len(PLACEHOLDER_RE.findall(text or ""))


def find_broken_placeholders(text: str) -> list[dict[str, Any]]:
    broken: list[dict[str, Any]] = []
    if not text:
        return broken
    starts = list(PLACEHOLDER_START_RE.finditer(text))
    for idx, match in enumerate(starts):
        close = text.find("]]", match.end())
        next_start = starts[idx + 1].start() if idx + 1 < len(starts) else -1
        raw = text[match.start() : min(len(text), match.start() + 100)]
        if close == -1 or (next_start != -1 and next_start < close):
            broken.append({"offset": match.start(), "reason": "missing_closing_brackets", "raw": snippet(raw, 100)})
            continue
        inside = text[match.end() : close].strip()
        if not inside:
            broken.append({"offset": match.start(), "reason": "empty_placeholder_id", "raw": snippet(raw, 100)})
        elif len(inside) > 80 or "[[" in inside or "\n" in inside:
            broken.append({"offset": match.start(), "reason": "malformed_placeholder_id", "raw": snippet(raw, 100)})
    return broken


def unescaped_dollar_counts(text: str) -> tuple[int, int, int]:
    if not text:
        return (0, 0, 0)
    total = 0
    double = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "$":
            if i + 1 < len(text) and text[i + 1] == "$":
                double += 1
                total += 2
                i += 2
                continue
            total += 1
        i += 1
    single = max(total - 2 * double, 0)
    return total, single, double


def has_unbalanced_math(text: str) -> bool:
    _total, single, double = unescaped_dollar_counts(text or "")
    return single % 2 == 1 or double % 2 == 1


def latex_environment_mismatches(text: str) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = {}
    for action, env_name in ENV_RE.findall(text or ""):
        normalized = env_name.strip()
        counts.setdefault(normalized, Counter())[action] += 1
    mismatches: dict[str, dict[str, int]] = {}
    for env_name, counter in counts.items():
        begin = counter.get("begin", 0)
        end = counter.get("end", 0)
        if begin != end:
            mismatches[env_name] = {"begin": begin, "end": end}
    return mismatches


def latex_commands(text: str) -> list[str]:
    return [m.group(1) for m in LATEX_COMMAND_RE.finditer(text or "")]


def tex_command_leak(text: str, block_type: str = "") -> tuple[bool, list[str]]:
    commands = latex_commands(text)
    if not commands:
        return False, []
    lower_commands = [cmd.lower() for cmd in commands]
    hits = sorted(set(cmd for cmd in lower_commands if cmd in STRUCTURAL_LATEX_COMMANDS))
    block_type = (block_type or "").lower()
    if hits:
        if block_type in FORMULA_LIKE_BLOCK_TYPES and set(hits).issubset({"begin", "end"}):
            return False, hits
        return True, hits
    leak_hits = sorted(set(cmd for cmd in lower_commands if cmd in LATEX_LEAK_COMMANDS))
    if block_type not in FORMULA_LIKE_BLOCK_TYPES and leak_hits:
        return True, leak_hits
    return False, sorted(set(lower_commands[:10]))


def strip_placeholders_and_math(text: str) -> str:
    cleaned = PLACEHOLDER_RE.sub(" ", text or "")
    cleaned = re.sub(r"\$\$.*?\$\$", " ", cleaned, flags=re.S)
    cleaned = re.sub(r"\$.*?\$", " ", cleaned, flags=re.S)
    cleaned = re.sub(r"\\\((.*?)\\\)", " ", cleaned, flags=re.S)
    cleaned = re.sub(r"\\\[(.*?)\\\]", " ", cleaned, flags=re.S)
    return cleaned


def has_readable_text(text: str, min_words: int = 3) -> bool:
    cleaned = strip_placeholders_and_math(text)
    words = re.findall(r"[A-Za-z][A-Za-z'-]{1,}", cleaned)
    return len(words) >= min_words


def is_ghost_block(text: str) -> bool:
    stripped = (text or "").strip()
    if not stripped:
        return False
    compact = re.sub(r"\s+", "", stripped)
    if compact in {".", "..", "...", "©", "(c)", "®", "*", "-", "--", "—", "–", "|", "||", "·", "•"}:
        return True
    if re.fullmatch(r"(?:page)?\d{1,4}", compact, re.I):
        return True
    if re.fullmatch(r"页(?:码)?\d{0,4}", compact):
        return True
    if len(compact) <= 6 and not re.search(r"[A-Za-z\u4e00-\u9fff]", compact):
        return True
    return False


def has_excessive_whitespace(text: str) -> bool:
    if not text:
        return False
    if re.search(r"[ \t]{4,}", text) or re.search(r"\n{3,}", text):
        return True
    if len(text) >= 120:
        whitespace_ratio = sum(1 for ch in text if ch.isspace()) / len(text)
        return whitespace_ratio > 0.35
    return False


def suspicious_truncation(text: str) -> bool:
    stripped = (text or "").strip()
    if not stripped or len(stripped) > 180:
        return False
    pairs = [("(", ")"), ("[", "]"), ("{", "}"), ("“", "”"), ("‘", "’")]
    for left, right in pairs:
        if stripped.count(left) > stripped.count(right):
            return True
    if stripped.count('"') % 2 == 1:
        return True
    if re.search(r"[,;:]\s*$", stripped) and len(stripped) < 120:
        return True
    return False


def suspicious_non_english_noise(text: str) -> bool:
    plain = strip_placeholders_and_math(text)
    if len(plain.strip()) < 20:
        return False
    non_latin_letters = 0
    cjk = 0
    total_letters = 0
    for ch in plain:
        if not unicodedata.category(ch).startswith("L"):
            continue
        total_letters += 1
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF:
            cjk += 1
        elif code > 127 and not (0x0370 <= code <= 0x03FF):
            non_latin_letters += 1
    if cjk >= 3:
        return True
    if total_letters >= 40 and non_latin_letters / max(total_letters, 1) > 0.08:
        return True
    return False


def possible_ocr_garbled_text(text: str) -> tuple[bool, dict[str, Any]]:
    plain = strip_placeholders_and_math(text)
    if len(plain.strip()) < 20:
        return False, {}
    mojibake_tokens = ["�", "Ã", "Â", "â€", "ï¿½", "\ufffd"]
    token_hits = {token: plain.count(token) for token in mojibake_tokens if token in plain}
    if token_hits:
        return True, {"mojibake_tokens": token_hits}
    symbol_chars = 0
    visible_chars = 0
    for ch in plain:
        if ch.isspace():
            continue
        visible_chars += 1
        category = unicodedata.category(ch)
        if category.startswith("S") and ch not in {"$", "%", "&", "+", "-", "=", "<", ">", "×", "≤", "≥", "±"}:
            symbol_chars += 1
    if visible_chars >= 80 and symbol_chars / max(visible_chars, 1) > 0.12:
        return True, {"symbol_ratio": round(symbol_chars / visible_chars, 4)}
    if re.search(r"[^A-Za-z0-9\s\[\]\(\)\{\}\.,;:'\"/$\\+\-=<>_*]{5,}", plain):
        return True, {"reason": "long_unusual_character_run"}
    return False, {}


def extract_json_text(data: Any) -> str:
    pieces: list[str] = []

    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            preferred_keys = {"content", "text", "body", "paragraph", "title", "caption", "description"}
            for child_key, child_value in value.items():
                if child_key in preferred_keys and isinstance(child_value, str):
                    pieces.append(child_value)
                elif child_key not in {"bbox", "bbox_2d", "index", "id", "source", "metadata"}:
                    walk(child_value, child_key)
        elif isinstance(value, list):
            for item in value:
                walk(item, key)
        elif isinstance(value, str) and key in {"content", "text", "body", "paragraph", "title", "caption"}:
            pieces.append(value)

    walk(data)
    if not pieces:
        def collect_all(value: Any) -> None:
            if isinstance(value, dict):
                for child_value in value.values():
                    collect_all(child_value)
            elif isinstance(value, list):
                for item in value:
                    collect_all(item)
            elif isinstance(value, str):
                pieces.append(value)

        collect_all(data)
    return "\n\n".join(piece for piece in pieces if piece is not None)


def normalize_text_for_comparison(text: str) -> str:
    cleaned = text or ""
    cleaned = re.sub(r"(?m)^\s*%.*$", " ", cleaned)
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\\(?:documentclass|usepackage|geometry|title|author|date)\{[^{}]*\}", " ", cleaned)
    cleaned = re.sub(r"\\(?:begin|end)\{(?:document|abstract)\}", " ", cleaned)
    cleaned = re.sub(r"\\(?:section|subsection|subsubsection)\*?\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\(?:caption)\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{[^{}]*\}", " ", cleaned)
    cleaned = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", cleaned)
    cleaned = re.sub(r"[$\\{}#_^~]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def formula_marker_count(text: str) -> int:
    text = text or ""
    _total, single, double = unescaped_dollar_counts(text)
    dollar_formulas = single // 2 + double // 2
    env_formulas = len(re.findall(r"\\begin\{(?:equation|align|align\*|gather|multline|split|cases|eqnarray)\}", text))
    bracket_formulas = len(re.findall(r"\\\[", text)) + len(re.findall(r"\\\(", text))
    placeholders = len(extract_formula_refs(text))
    return dollar_formulas + env_formulas + bracket_formulas + placeholders


def normalize_chapter_key(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"_full$", "", text)
    if text == "目录":
        return "toc"
    return text


def ocr_chapter_key(path: Path, root: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix not in {".tex", ".md", ".json"}:
        return None
    name = path.name.lower()
    if name in {"report.md", "refs.bib"}:
        return None
    parent = path.parent.name.lower()
    stem = path.stem.lower()
    if name == "main.tex":
        return normalize_chapter_key(parent)
    if re.fullmatch(r"(chapter\d+|appendix\d+|toc|目录)", stem):
        return normalize_chapter_key(stem)
    if parent.endswith("_full") and suffix in {".tex", ".md", ".json"}:
        return normalize_chapter_key(parent)
    return None


def ocr_candidate_priority(path: Path, key: str) -> tuple[int, str]:
    suffix = path.suffix.lower()
    name = path.name.lower()
    stem = path.stem.lower()
    if name == "main.tex":
        return (0, relpath(path))
    if re.fullmatch(r"(chapter\d+|appendix\d+|toc|目录)", stem) and suffix == ".md":
        return (1, relpath(path))
    if re.fullmatch(r"(chapter\d+|appendix\d+|toc|目录)", stem) and suffix == ".json":
        return (2, relpath(path))
    if suffix == ".tex":
        return (3, relpath(path))
    if suffix == ".md":
        return (4, relpath(path))
    if suffix == ".json":
        return (5, relpath(path))
    return (99, relpath(path))


def discover_ocr_text_sources(root: Path) -> dict[str, dict[str, Any]]:
    if not root.exists():
        return {}
    grouped: dict[str, list[Path]] = {}
    for path in sorted(root.rglob("*"), key=lambda p: relpath(p)):
        if not path.is_file():
            continue
        key = ocr_chapter_key(path, root)
        if not key:
            continue
        grouped.setdefault(key, []).append(path)

    sources: dict[str, dict[str, Any]] = {}
    for key, candidates in grouped.items():
        chosen = sorted(candidates, key=lambda p: ocr_candidate_priority(p, key))[0]
        sources[key] = {
            "key": key,
            "path": chosen,
            "relative_path": relpath(chosen),
            "candidate_count": len(candidates),
            "candidates": [relpath(p) for p in sorted(candidates, key=lambda p: ocr_candidate_priority(p, key))],
        }
    return dict(sorted(sources.items(), key=lambda item: chapter_sort_key(item[0])))
