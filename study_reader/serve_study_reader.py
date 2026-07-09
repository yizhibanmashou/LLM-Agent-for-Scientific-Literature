from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
APP_PATH = "/study_reader"
REVIEW_APP_PATH = "/review_app"
LEGACY_APP_PATH = "/knowledge_engineering/review_app"


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


class StudyReaderHandler(SimpleHTTPRequestHandler):
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

    def _redirect_old_app_path(self, request_path: str) -> bool:
        old_prefix = ""
        if request_path == REVIEW_APP_PATH or request_path.startswith(f"{REVIEW_APP_PATH}/"):
            old_prefix = REVIEW_APP_PATH
        elif request_path == LEGACY_APP_PATH or request_path.startswith(f"{LEGACY_APP_PATH}/"):
            old_prefix = LEGACY_APP_PATH
        if old_prefix:
            suffix = request_path.removeprefix(old_prefix)
            target = f"{APP_PATH}{suffix}"
            if not target.endswith("/") and not Path(target).suffix:
                target = f"{target}/"
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header("Location", target)
            self.end_headers()
            return True
        return False

    def do_HEAD(self) -> None:
        if self._redirect_old_app_path(urlparse(self.path).path):
            return
        super().do_HEAD()

    def do_GET(self) -> None:
        if self._redirect_old_app_path(urlparse(self.path).path):
            return
        super().do_GET()

    def do_POST(self) -> None:
        self.send_error(HTTPStatus.NOT_FOUND, "Study Reader is a static app.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the Study Reader.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), StudyReaderHandler)
    print(f"Serving Study Reader at http://{args.host}:{args.port}{APP_PATH}/")
    print(f"Old review_app redirects from http://{args.host}:{args.port}{REVIEW_APP_PATH}/")
    print(f"Legacy alias redirects from http://{args.host}:{args.port}{LEGACY_APP_PATH}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
