from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
REVIEW_RECORDS_PATH = APP_DIR / "data" / "local" / "review_records.json"
ISSUE_TAXONOMY_PATH = APP_DIR / "data" / "local" / "issue_taxonomy.json"
APP_PATH = "/review_app"
LEGACY_APP_PATH = "/knowledge_engineering/review_app"
REVIEW_RECORD_API_PATHS = {
    f"{APP_PATH}/api/review-records",
    f"{LEGACY_APP_PATH}/api/review-records",
}
ISSUE_TAXONOMY_API_PATHS = {
    f"{APP_PATH}/api/issue-taxonomy",
    f"{LEGACY_APP_PATH}/api/issue-taxonomy",
}
ALLOWED_STATUS = {"pending", "pass", "fail"}
ALLOWED_ISSUE_SEVERITY = {"info", "warning", "error", "fatal"}
ALLOWED_CATEGORY_STATUS = {"manual_only", "candidate", "active"}


DEFAULT_ISSUE_CATEGORIES = [
    {
        "issue_code": "inline_math_damage",
        "label": "inline 公式损坏",
        "scope": "inline_math",
        "description": "inline LaTeX 中出现上下标断裂、符号缺失、空公式或数学片段损坏。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {
            "mode": "regex",
            "patterns": [
                r"\$[^$\n]*\s[_^]\s+[A-Za-z0-9\\]",
                r"\$\s*\$",
            ],
        },
    },
    {
        "issue_code": "display_formula_damage",
        "label": "display 公式损坏",
        "scope": "display_math",
        "description": "独立公式、公式编号或公式环境存在缺失、断裂、错位。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "formula_reference_error",
        "label": "公式引用错误",
        "scope": "formula_reference",
        "description": "chunk 中公式占位符缺失、错指、断裂或与公式库不一致。",
        "severity": "fatal",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "formula_mention_not_linked",
        "label": "公式提及未回链",
        "scope": "formula_reference",
        "description": "正文提到 Equation/Figure/Table 编号，但没有映射成可追踪的结构化引用。",
        "severity": "warning",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "table_reference_error",
        "label": "表格引用错误",
        "scope": "table_reference",
        "description": "chunk 中表格占位符缺失、错指、断裂或与表格库不一致。",
        "severity": "fatal",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "table_row_group_misattribution",
        "label": "表格行归属错误",
        "scope": "table",
        "description": "表格中的行、公式或说明文字被归到错误的上级条目、版本或组别。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "table_cell_alignment_error",
        "label": "表格单元格错位",
        "scope": "table",
        "description": "表格单元格、行列或数学表达式对齐错误，导致含义错配。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "table_reference_target_error",
        "label": "表格引用目标错误",
        "scope": "table_reference",
        "description": "正文中的表格引用存在但指向错误表格、错误章节或错误位置。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "table_structure_error",
        "label": "表格结构问题",
        "scope": "table",
        "description": "表格标题、行列、单元格内容或 HTML 结构不正确。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "duplicate_or_leaked_block",
        "label": "重复/泄漏块",
        "scope": "structure",
        "description": "正文中出现重复内容、跨块泄漏、残留浮动参数或非正文结构片段。",
        "severity": "warning",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "chunk_split_error",
        "label": "chunk 切分问题",
        "scope": "chunk",
        "description": "block/chunk 切分过短、跨段、上下文断裂或类型不合理。",
        "severity": "warning",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "chunk_boundary_error",
        "label": "chunk 边界错误",
        "scope": "chunk",
        "description": "chunk 边界过早、过晚或跨越不应合并的语义单元。",
        "severity": "warning",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "ocr_garbled_text",
        "label": "OCR 乱码",
        "scope": "text",
        "description": "文本存在乱码、异常字符、不可读片段或明显 OCR 误识别。",
        "severity": "warning",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": [r"�|Ã|Â|ï¿½"]},
    },
    {
        "issue_code": "ghost_or_float_block",
        "label": "ghost/[h] 噪声块",
        "scope": "structure",
        "description": "正文中残留 [h]、页码、孤立符号、版权符号等无语义块。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": [r"^\s*\[h\]\s*$", r"^\s*(?:\.{1,3}|©|page\s*\d+|\d{1,4})\s*$"]},
    },
    {
        "issue_code": "truncated_text",
        "label": "文本截断",
        "scope": "text",
        "description": "句子、括号、引号或引用明显未闭合，疑似被截断。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": []},
    },
    {
        "issue_code": "placeholder_leak",
        "label": "占位符/表格浮动残留",
        "scope": "structure",
        "description": "正文中残留 LaTeX 浮动参数、dummy table、未完成 placeholder 等结构噪声。",
        "severity": "error",
        "status": "manual_only",
        "examples": [],
        "detector": {"mode": "regex", "patterns": [r"\[(?:h|t|b|p)\]", r"Cell\s+1\s*&\s*Cell\s+2"]},
    },
]


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_note(raw_note: object) -> dict | None:
    if not isinstance(raw_note, dict):
        return None

    text = str(raw_note.get("text") or "").strip()
    if not text:
        return None

    note_id = str(raw_note.get("id") or uuid.uuid4().hex).strip() or uuid.uuid4().hex
    created_at = raw_note.get("created_at")
    created_at = str(created_at).strip() if isinstance(created_at, str) and created_at.strip() else now_iso()

    return {"id": note_id, "text": text, "created_at": created_at}


def normalize_issue(raw_issue: object) -> dict | None:
    if not isinstance(raw_issue, dict):
        return None

    issue_code = str(raw_issue.get("issue_code") or "").strip()
    bad_span = str(raw_issue.get("bad_span") or "").strip()
    expected = str(raw_issue.get("expected") or "").strip()
    context = str(raw_issue.get("context") or "").strip()
    target_id = str(raw_issue.get("target_id") or "").strip()
    evidence = str(raw_issue.get("evidence") or "").strip()
    note = str(raw_issue.get("note") or "").strip()
    if not issue_code and not bad_span and not expected and not context and not target_id and not evidence and not note:
        return None

    issue_id = str(raw_issue.get("id") or uuid.uuid4().hex).strip() or uuid.uuid4().hex
    created_at = raw_issue.get("created_at")
    created_at = str(created_at).strip() if isinstance(created_at, str) and created_at.strip() else now_iso()
    severity = str(raw_issue.get("severity") or "warning").strip().lower()
    if severity not in ALLOWED_ISSUE_SEVERITY:
        severity = "warning"

    item_snapshot = raw_issue.get("item_snapshot")
    item_snapshot = item_snapshot if isinstance(item_snapshot, dict) else {}

    return {
        "id": issue_id,
        "issue_code": issue_code or "uncategorized",
        "issue_label": str(raw_issue.get("issue_label") or "").strip(),
        "scope": str(raw_issue.get("scope") or "").strip(),
        "severity": severity,
        "bad_span": bad_span,
        "expected": expected,
        "context": context,
        "target_id": target_id,
        "evidence": evidence,
        "note": note,
        "created_at": created_at,
        "item_snapshot": item_snapshot,
    }


def normalize_status(raw_status: object) -> str:
    status = str(raw_status or "").strip().lower()
    return status if status in ALLOWED_STATUS else "pending"


def normalize_record(raw_record: object) -> dict:
    source = raw_record if isinstance(raw_record, dict) else {}
    status = normalize_status(source.get("status"))
    status_updated_at = source.get("status_updated_at")
    status_updated_at = (
        str(status_updated_at).strip() if isinstance(status_updated_at, str) and status_updated_at.strip() else now_iso()
    )

    notes: list[dict] = []
    raw_notes = source.get("notes")
    if isinstance(raw_notes, list):
        for raw_note in raw_notes:
            normalized = normalize_note(raw_note)
            if normalized:
                notes.append(normalized)

    issues: list[dict] = []
    raw_issues = source.get("issues")
    if isinstance(raw_issues, list):
        for raw_issue in raw_issues:
            normalized_issue = normalize_issue(raw_issue)
            if normalized_issue:
                issues.append(normalized_issue)

    return {
        "status": status,
        "status_updated_at": status_updated_at,
        "notes": notes,
        "issues": issues,
    }


def normalize_payload(payload: object) -> dict:
    source = payload if isinstance(payload, dict) else {}
    raw_records = source.get("records")
    raw_records = raw_records if isinstance(raw_records, dict) else {}

    records: dict[str, dict] = {}
    for key, raw_record in raw_records.items():
        record_key = str(key).strip()
        if not record_key:
            continue
        records[record_key] = normalize_record(raw_record)

    updated_at = source.get("updated_at")
    updated_at = str(updated_at).strip() if isinstance(updated_at, str) and updated_at.strip() else now_iso()

    return {
        "version": 1,
        "updated_at": updated_at,
        "records": records,
    }


def save_payload(payload: dict) -> dict:
    normalized = normalize_payload(payload)
    REVIEW_RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_RECORDS_PATH.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return normalized


def load_payload() -> dict:
    if not REVIEW_RECORDS_PATH.exists():
        return save_payload({})

    try:
        raw_payload = json.loads(REVIEW_RECORDS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raw_payload = {}

    return normalize_payload(raw_payload)


def slug_issue_code(value: str) -> str:
    text = str(value or "").strip().lower()
    text = "".join(ch if ch.isalnum() else "_" for ch in text)
    text = "_".join(part for part in text.split("_") if part)
    return text or f"issue_{uuid.uuid4().hex[:8]}"


def normalize_category(raw_category: object) -> dict | None:
    if not isinstance(raw_category, dict):
        return None
    issue_code = slug_issue_code(str(raw_category.get("issue_code") or raw_category.get("label") or ""))
    label = str(raw_category.get("label") or issue_code).strip()
    scope = str(raw_category.get("scope") or "text").strip()
    severity = str(raw_category.get("severity") or "warning").strip().lower()
    if severity not in ALLOWED_ISSUE_SEVERITY:
        severity = "warning"
    status = str(raw_category.get("status") or "manual_only").strip().lower()
    if status not in ALLOWED_CATEGORY_STATUS:
        status = "manual_only"

    examples = raw_category.get("examples")
    normalized_examples = []
    if isinstance(examples, list):
        for example in examples:
            if not isinstance(example, dict):
                continue
            normalized_examples.append(
                {
                    "bad_span": str(example.get("bad_span") or "").strip(),
                    "expected": str(example.get("expected") or "").strip(),
                    "context": str(example.get("context") or "").strip(),
                    "target_id": str(example.get("target_id") or "").strip(),
                    "evidence": str(example.get("evidence") or "").strip(),
                }
            )

    aliases = raw_category.get("aliases")
    normalized_aliases = []
    if isinstance(aliases, list):
        normalized_aliases = [str(alias).strip() for alias in aliases if str(alias).strip()]

    detector = raw_category.get("detector")
    detector = detector if isinstance(detector, dict) else {}
    patterns = detector.get("patterns")
    patterns = [str(pattern) for pattern in patterns if str(pattern).strip()] if isinstance(patterns, list) else []

    return {
        "issue_code": issue_code,
        "label": label,
        "scope": scope,
        "description": str(raw_category.get("description") or "").strip(),
        "severity": severity,
        "status": status,
        "aliases": normalized_aliases,
        "examples": normalized_examples,
        "detector": {
            "mode": str(detector.get("mode") or "regex").strip() or "regex",
            "patterns": patterns,
        },
    }


def normalize_taxonomy(payload: object) -> dict:
    source = payload if isinstance(payload, dict) else {}
    raw_categories = source.get("categories")
    raw_categories = raw_categories if isinstance(raw_categories, list) else []
    seen: set[str] = set()
    categories: list[dict] = []
    for raw_category in raw_categories:
        normalized = normalize_category(raw_category)
        if not normalized or normalized["issue_code"] in seen:
            continue
        seen.add(normalized["issue_code"])
        categories.append(normalized)

    if not categories:
        for raw_category in DEFAULT_ISSUE_CATEGORIES:
            normalized = normalize_category(raw_category)
            if normalized and normalized["issue_code"] not in seen:
                seen.add(normalized["issue_code"])
                categories.append(normalized)

    updated_at = source.get("updated_at")
    updated_at = str(updated_at).strip() if isinstance(updated_at, str) and updated_at.strip() else now_iso()
    return {"version": 1, "updated_at": updated_at, "categories": categories}


def save_taxonomy(payload: dict) -> dict:
    normalized = normalize_taxonomy(payload)
    ISSUE_TAXONOMY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ISSUE_TAXONOMY_PATH.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return normalized


def load_taxonomy() -> dict:
    if not ISSUE_TAXONOMY_PATH.exists():
        return save_taxonomy({"categories": DEFAULT_ISSUE_CATEGORIES})
    try:
        raw_payload = json.loads(ISSUE_TAXONOMY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raw_payload = {}
    return normalize_taxonomy(raw_payload)


class ShowingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def translate_path(self, path: str) -> str:
        request_path = unquote(urlparse(path).path)
        if request_path == APP_PATH or request_path == f"{APP_PATH}/":
            return str(APP_DIR / "index.html")
        if request_path.startswith(f"{APP_PATH}/"):
            candidate = (APP_DIR / request_path.removeprefix(f"{APP_PATH}/")).resolve()
            if is_relative_to(candidate, APP_DIR.resolve()):
                return str(candidate)
            return str(APP_DIR / "__missing__")
        return super().translate_path(path)

    def _redirect_legacy_app_path(self, request_path: str) -> bool:
        if request_path == LEGACY_APP_PATH or request_path.startswith(f"{LEGACY_APP_PATH}/"):
            suffix = request_path.removeprefix(LEGACY_APP_PATH)
            target = f"{APP_PATH}{suffix}"
            if not target.endswith("/") and not Path(target).suffix:
                target = f"{target}/"
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", target)
            self.end_headers()
            return True
        return False

    def _send_json_head(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

    def do_HEAD(self) -> None:
        request_path = urlparse(self.path).path
        if request_path in REVIEW_RECORD_API_PATHS:
            self._send_json_head(load_payload())
            return
        if request_path in ISSUE_TAXONOMY_API_PATHS:
            self._send_json_head(load_taxonomy())
            return
        if self._redirect_legacy_app_path(request_path):
            return
        super().do_HEAD()

    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        if request_path in REVIEW_RECORD_API_PATHS:
            self._send_json(load_payload())
            return
        if request_path in ISSUE_TAXONOMY_API_PATHS:
            self._send_json(load_taxonomy())
            return
        if self._redirect_legacy_app_path(request_path):
            return
        super().do_GET()

    def do_POST(self) -> None:
        request_path = urlparse(self.path).path
        if request_path not in REVIEW_RECORD_API_PATHS and request_path not in ISSUE_TAXONOMY_API_PATHS:
            self.send_error(HTTPStatus.NOT_FOUND, "Unsupported endpoint")
            return

        body_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(body_length) if body_length > 0 else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
            return

        if request_path in ISSUE_TAXONOMY_API_PATHS:
            normalized = normalize_taxonomy(payload)
            normalized["updated_at"] = now_iso()
            saved = save_taxonomy(normalized)
            self._send_json(saved)
            return

        normalized = normalize_payload(payload)
        normalized["updated_at"] = now_iso()
        saved = save_payload(normalized)
        self._send_json(saved)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Serve the KE review app with review-record persistence support."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    save_payload(load_payload())
    save_taxonomy(load_taxonomy())
    server = ThreadingHTTPServer((args.host, args.port), ShowingHandler)
    print(f"Serving KE review app at http://{args.host}:{args.port}{APP_PATH}/")
    print(f"Legacy alias: http://{args.host}:{args.port}{LEGACY_APP_PATH}/")
    print(f"Review records file: {REVIEW_RECORDS_PATH}")
    print(f"Issue taxonomy file: {ISSUE_TAXONOMY_PATH}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
