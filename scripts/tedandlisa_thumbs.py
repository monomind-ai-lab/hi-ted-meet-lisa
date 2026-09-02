#!/usr/bin/env python3
"""Capture template thumbnails for the intake panel's template gallery.

Renders each template registered in templates/templates.json with headless
Chrome and writes a PNG into templates/thumbs/. Run it after adding a template
or changing one's opening screen:

    python3 scripts/tedandlisa_thumbs.py            # all templates
    python3 scripts/tedandlisa_thumbs.py --only techdoc

Chrome is the only requirement, and it is used read-only. If it is missing the
panel falls back to a typographic card, so a missing thumbnail degrades the
gallery rather than breaking it.

The templates whose `thumb_source` is a preview under previews/ are captured
from https://html.monomind.one/ — those files live in the website repository
now — so re-capturing those needs a network connection.

How a capture settles. Chrome is driven by command-line flags alone here — no
devtools protocol — so nothing can be injected once the page is open. Instead
each page is served from a throwaway local origin with one script appended
before </body> (the file on disk and the hosted copy are never modified): it
pins the entrance animations (`.reveal`, `[data-reveal]`) to their settled
state, forces a layout so every @font-face is actually requested, and waits
for document.fonts.ready. The --virtual-time-budget is what really waits for
the webfonts: headless Chrome pauses virtual time while a fetch is pending,
so the budget cannot expire with a font still in flight (verified — a page
whose fonts.ready fired with zero faces loaded still captured in both of its
webfonts). The budget only has to outlast the page's own entrance timing,
and 4000 virtual ms does. One consequence of the local origin: a skeleton
captured from disk shows the controls that hide themselves on file:// (the
self-download, the MonoMind deck's language switch) — the same state the
hosted previews have always been captured in.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "templates" / "templates.json"

# The nine preview decks used to sit in previews/ in this repository. They went
# with the public website when it was split out into monomind-ai-lab/ted-and-lisa,
# and the registry deliberately still names them by that canonical path — it is
# the path the website builds from too. So a `thumb_source` under previews/ that
# is not on disk is resolved to the published copy instead of skipped: headless
# Chrome screenshots a URL exactly as it screenshots a file, so the only cost is
# that re-capturing those nine thumbnails now needs a network connection.
HOSTED_BASE = "https://html.monomind.one/"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# 1200x750 at half scale: a 600x375 card, crisp on the panel, small enough to
# inline as a data URI without bloating the page.
WIDTH, HEIGHT, SCALE = 1200, 750, 0.4

# Appended before </body> of the served copy (see the module docstring). It
# settles the entrance classes first and again after the fonts, so the
# screenshot never catches a reveal mid-flight even if the font wait races
# the virtual-time budget. Its own cap stays under that budget on purpose.
SETTLE_SCRIPT = """
<script data-thumb-settle>
(function () {
  var doc = document;
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function settle() {
    Array.prototype.forEach.call(doc.querySelectorAll('.reveal, [data-reveal]'), function (el) {
      el.style.setProperty('transition', 'none', 'important');
      el.style.setProperty('animation', 'none', 'important');
      el.style.setProperty('opacity', '1', 'important');
      el.style.setProperty('transform', 'none', 'important');
      el.style.setProperty('visibility', 'visible', 'important');
    });
  }
  async function run() {
    settle();
    void doc.body.offsetHeight;            // queue every lazily requested face
    var t0 = Date.now();
    do {
      try { await Promise.race([doc.fonts.ready, sleep(%(cap)d)]); } catch (e) { break; }
      await sleep(50);
    } while (doc.fonts.status === 'loading' && Date.now() - t0 < %(cap)d);
    settle();
  }
  if (doc.readyState === 'complete') run(); else window.addEventListener('load', run);
})();
</script>
"""


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if pathlib.Path(c).is_file():
            return c
    return shutil.which("chromium") or shutil.which("google-chrome")


def settled_page(html: str, wait_ms: int) -> bytes:
    """The page with SETTLE_SCRIPT appended before </body> (or at the end)."""
    script = SETTLE_SCRIPT % {"cap": max(500, int(wait_ms * 0.6))}
    i = html.rfind("</body>")
    html = html[:i] + script + html[i:] if i >= 0 else html + script
    return html.encode("utf-8")


class ThumbHandler(http.server.SimpleHTTPRequestHandler):
    """Serves the settled copy at /<page_name>; everything else comes from
    the source file's own directory (or an empty one for a hosted page)."""

    page_name = ""
    page_bytes = b""

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?", 1)[0].split("#", 1)[0])
        if path == "/" + self.page_name:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(self.page_bytes)))
            self.end_headers()
            self.wfile.write(self.page_bytes)
            return
        super().do_GET()

    def log_message(self, *args):
        pass


def serve(name: str, page: bytes, directory: str) -> http.server.ThreadingHTTPServer:
    handler = type("Handler", (ThumbHandler,), {"page_name": name, "page_bytes": page})
    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(handler, directory=directory))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def capture(chrome: str, html: str, name: str, directory: str | None,
            out: pathlib.Path, wait_ms: int, fragment: str = "") -> bool:
    """Screenshot `html` (served as /<name> from a local origin, with the
    settle script appended) into `out`. `directory` is where the page's
    relative subresources resolve — the source file's own directory, or
    None for a hosted page, whose copy is self-contained."""
    out.parent.mkdir(parents=True, exist_ok=True)
    # ignore_cleanup_errors: a killed Chrome's helpers can briefly hold
    # profile files while the directory is removed; not a capture failure.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        www = pathlib.Path(profile) / "www"
        www.mkdir()
        srv = serve(name, settled_page(html, wait_ms), directory or str(www))
        try:
            url = (f"http://127.0.0.1:{srv.server_address[1]}/{urllib.parse.quote(name)}"
                   + (f"#{fragment}" if fragment else ""))
            cmd = [
                chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                f"--user-data-dir={profile}",
                f"--window-size={WIDTH},{HEIGHT}",
                f"--force-device-scale-factor={SCALE}",
                f"--virtual-time-budget={wait_ms}",
                f"--screenshot={out}",
                url,
            ]
            # Headless Chrome writes the PNG and then sometimes fails to exit
            # (L-009). The file on disk is the real result, so a timeout is
            # not a failure — but Chrome's helper processes would keep a
            # captured pipe open long after the parent was killed (measured:
            # 141s for one thumbnail), so stderr goes to a file and the whole
            # process group is killed on the deadline.
            errfile = pathlib.Path(profile) / "stderr.txt"
            with open(errfile, "w") as fe:
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=fe,
                                        start_new_session=True)
                try:
                    proc.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
            err = errfile.read_bytes()
        finally:
            srv.shutdown()
    if out.is_file() and out.stat().st_size > 0:
        return True
    sys.stderr.write(err.decode("utf-8", "replace")[-500:] + "\n")
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="capture just this template id")
    ap.add_argument("--wait", type=int, default=4000,
                    help="virtual time budget in ms; raise it for diagram-heavy templates")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("error: no Chrome or Chromium found; the panel will fall back to text cards",
              file=sys.stderr)
        return 2

    registry = json.loads(REGISTRY.read_text())
    failures = 0
    for t in registry["templates"]:
        if args.only and t["id"] != args.only:
            continue
        # A template may point its thumbnail at a filled-in preview instead of
        # its own placeholder skeleton, optionally at a specific view:
        #   "thumb_source": "previews/name.html#en/01"
        source, _, fragment = str(t.get("thumb_source") or t.get("file") or "").partition("#")
        local = ROOT / source if source else None
        if local is not None and local.is_file():
            html, name, directory = local.read_text(encoding="utf-8"), local.name, str(local.parent)
        elif source.startswith("previews/"):
            url = HOSTED_BASE + source              # see HOSTED_BASE above
            # The site's edge answers urllib's default User-Agent with 403;
            # a browser-shaped one is let through, as Chrome itself was.
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (tedandlisa_thumbs)"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    html = resp.read().decode("utf-8", "replace")
            except (urllib.error.URLError, OSError) as exc:
                print(f"skip {t['id']}: could not fetch {url} ({exc})", file=sys.stderr)
                failures += 1
                continue
            name, directory = source.rsplit("/", 1)[-1], None
        else:
            print(f"skip {t['id']}: {source or '(no file)'} not found", file=sys.stderr)
            failures += 1
            continue
        out = ROOT / t["thumb"]
        ok = capture(chrome, html, name, directory, out, args.wait, fragment)
        status = f"{out.stat().st_size // 1024} KB" if ok else "FAILED"
        print(f"{t['id']:16} {status}")
        failures += 0 if ok else 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
