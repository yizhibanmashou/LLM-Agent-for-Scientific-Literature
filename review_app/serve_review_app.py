from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[1]
REVIEW_RECORDS_PATH = APP_DIR / "data" / "local" / "review_records.json"
API_PATH = "/knowledge_engineering/review_app/api/review-records"
ALLOWED_STATUS = {"pending", "pass", "fail"}


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

    return {
        "status": status,
        "status_updated_at": status_updated_at,
        "notes": notes,
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


class ShowingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        if request_path == API_PATH:
            self._send_json(load_payload())
            return
        super().do_GET()

    def do_POST(self) -> None:
        request_path = urlparse(self.path).path
        if request_path != API_PATH:
            self.send_error(HTTPStatus.NOT_FOUND, "Unsupported endpoint")
            return

        body_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(body_length) if body_length > 0 else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
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
    server = ThreadingHTTPServer((args.host, args.port), ShowingHandler)
    print(f"Serving KE review app at http://{args.host}:{args.port}/knowledge_engineering/review_app/")
    print(f"Review records file: {REVIEW_RECORDS_PATH}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
