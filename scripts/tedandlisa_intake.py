#!/usr/bin/env python3
"""Serve the /lisa intake panel and capture its answers.

The panel is a standalone HTML file, so it also works when opened straight from
disk -- in that mode it falls back to a copy-paste payload. This runner is the
convenient path: it serves the panel over loopback, waits for the browser to
POST the answers to /intake, writes them to a file, and exits. The gallery's
"Preview" links point at the hosted previews on html.monomind.one, so they —
and only they — need a network connection.

    python3 scripts/tedandlisa_intake.py --prompt "a deck about X" --out intake.json

Stdlib only, binds 127.0.0.1, and never writes outside --out.
"""

from __future__ import annotations

import argparse
import base64
import json
import pathlib
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PANEL = ROOT / "assets" / "tedandlisa-intake.html"
REGISTRY = ROOT / "templates" / "templates.json"

# The registry names each preview by its repository-relative path
# ("previews/<id>.html"), but the previews themselves now live in the website
# repository (monomind-ai-lab/ted-and-lisa) and are only published at
# html.monomind.one. This runner therefore has nothing local to serve, so it
# rewrites each card's `preview` to the hosted copy below. Behaviour change on
# purpose: the gallery's "Preview" links now need a network connection, where
# they used to open a file served from this checkout. The panel already treats
# an absolute http(s) preview as external — it opens in a real new tab instead
# of the framing overlay — so no change to the panel is needed.
PREVIEW_BASE = "https://html.monomind.one/previews/"
MAX_BODY = 64 * 1024 * 1024  # generous: backgrounds arrive as base64 data URIs


def load_templates() -> list[dict]:
    """Registry entries for the panel's gallery, thumbnails inlined.

    A missing registry or thumbnail is not fatal: the panel falls back to its
    built-in list, and a card without a thumbnail renders as a text card.
    """
    if not REGISTRY.is_file():
        return []
    try:
        entries = json.loads(REGISTRY.read_text())["templates"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        print(f"warning: unreadable template registry ({exc})", file=sys.stderr)
        return []

    out = []
    for t in entries:
        card = {k: t.get(k) for k in
                ("id", "name", "tagline", "kind", "type", "best_for", "dependencies",
                 "languages", "preview", "skill", "badge")}
        if card.get("preview"):
            card["preview"] = PREVIEW_BASE + pathlib.PurePosixPath(card["preview"]).name
        thumb = ROOT / t.get("thumb", "")
        if t.get("thumb") and thumb.is_file():
            card["thumb"] = "data:image/png;base64," + base64.b64encode(thumb.read_bytes()).decode()
        else:
            print(f"note: no thumbnail for {t.get('id')} — run scripts/tedandlisa_thumbs.py",
                  file=sys.stderr)
        out.append(card)
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "monomind-intake/1.0"
    payload: dict | None = None
    context: dict = {}

    def log_message(self, fmt, *args):  # keep the console clean
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]
        # This server used to also serve the preview decks under /previews/ so
        # the gallery could frame them. They live in the website repository
        # now (see PREVIEW_BASE), so the panel is the only thing served here.
        if path not in ("/", "/index.html"):
            self._send(404, b'{"error":"not found"}')
            return
        try:
            html = PANEL.read_text(encoding="utf-8")
        except OSError as exc:
            self._send(500, json.dumps({"error": str(exc)}).encode())
            return
        # Hand the brief to the page before its own script runs. The registry
        # is read per request, not cached at startup: a template added while
        # the panel is open should appear on reload, not need a restart.
        context = dict(Handler.context)
        context["templates"] = load_templates()
        inject = (
            "<script>window.__MONOMIND_INTAKE__ = "
            + json.dumps(context)
            + ";</script>\n"
        )
        html = html.replace("<script>\n\"use strict\";", inject + "<script>\n\"use strict\";", 1)
        self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path.split("?")[0] != "/intake":
            self._send(404, b'{"error":"not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, b'{"error":"bad length"}')
            return
        if length <= 0 or length > MAX_BODY:
            self._send(413, b'{"error":"payload too large"}')
            return
        raw = self.rfile.read(length)
        try:
            Handler.payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send(400, json.dumps({"error": f"bad json: {exc}"}).encode())
            return
        self._send(200, b'{"ok":true}')


def summarize(payload: dict) -> dict:
    """Answers with file bodies replaced by descriptors, safe to print."""
    def strip(node):
        if isinstance(node, dict):
            if "thumb" in node and isinstance(node.get("thumb"), str):
                node = dict(node, thumb=f"<{len(node['thumb'])} chars omitted>")
            if "dataUri" in node:
                return {k: v for k, v in node.items() if k != "dataUri"} | {
                    "dataUri": f"<{len(node.get('dataUri') or '')} chars omitted>"
                }
            return {k: strip(v) for k, v in node.items()}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    return strip(payload)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompt", default="", help="the deck brief, shown in the panel")
    ap.add_argument("--out", default="intake.json", help="where to write the answers")
    ap.add_argument("--port", type=int, default=0, help="0 picks a free port")
    ap.add_argument("--timeout", type=int, default=900, help="seconds to wait")
    ap.add_argument("--no-open", action="store_true", help="do not launch a browser")
    args = ap.parse_args()

    if not PANEL.is_file():
        print(f"error: panel not found at {PANEL}", file=sys.stderr)
        return 2

    Handler.context = {}
    if args.prompt:
        Handler.context["prompt"] = args.prompt
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    print(f"intake panel: {url}", file=sys.stderr)
    print(f"waiting up to {args.timeout}s for answers…", file=sys.stderr)
    if not args.no_open:
        webbrowser.open(url)

    deadline = time.time() + args.timeout
    try:
        while Handler.payload is None and time.time() < deadline:
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        return 130
    finally:
        httpd.shutdown()

    if Handler.payload is None:
        print("error: timed out; re-run, or open the panel and paste the JSON back",
              file=sys.stderr)
        return 1

    out = pathlib.Path(args.out)
    out.write_text(json.dumps(Handler.payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)", file=sys.stderr)
    json.dump(summarize(Handler.payload), sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
