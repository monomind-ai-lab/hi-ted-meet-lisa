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
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "templates" / "templates.json"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# 1200x750 at half scale: a 600x375 card, crisp on the panel, small enough to
# inline as a data URI without bloating the page.
WIDTH, HEIGHT, SCALE = 1200, 750, 0.4


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if pathlib.Path(c).is_file():
            return c
    return shutil.which("chromium") or shutil.which("google-chrome")


def capture(chrome: str, html: pathlib.Path, out: pathlib.Path, wait_ms: int,
            fragment: str = "") -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            f"--user-data-dir={profile}",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--force-device-scale-factor={SCALE}",
            f"--virtual-time-budget={wait_ms}",
            f"--screenshot={out}",
            html.as_uri() + (f"#{fragment}" if fragment else ""),
        ]
        # Headless Chrome writes the PNG and then sometimes fails to exit.
        # The file on disk is the real result, so a timeout is not a failure.
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=60)
            err = proc.stderr
        except subprocess.TimeoutExpired as exc:
            err = exc.stderr or b""
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
        source, _, fragment = str(t.get("thumb_source") or t["file"]).partition("#")
        html = ROOT / source
        if not html.is_file():
            print(f"skip {t['id']}: {t['file']} not found", file=sys.stderr)
            failures += 1
            continue
        out = ROOT / t["thumb"]
        ok = capture(chrome, html, out, args.wait, fragment)
        status = f"{out.stat().st_size // 1024} KB" if ok else "FAILED"
        print(f"{t['id']:16} {status}")
        failures += 0 if ok else 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
