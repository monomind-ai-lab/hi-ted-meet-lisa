#!/usr/bin/env python3
"""Rendered-overflow gate: fail when any template (or given HTML file) lets
content escape sideways at any tested viewport width.

    python3 scripts/check_overflow.py                 # every first-party template
    python3 scripts/check_overflow.py previews/*.html # specific files
    CHROME_BIN=/path/to/chrome python3 scripts/check_overflow.py

Why this exists: a fixed grid track plus one long unbreakable mono token
(`tedandlisa_thumbs.py` in a 130px command column) overflows the cell and
collides with the neighbouring text without ever widening the document — so
"no horizontal scrollbar" is not enough. Each file is served over localhost,
loaded in headless Chrome inside an iframe (macOS headless Chrome clamps
windows to 500px, so true-375 needs the iframe rig; the wide widths use it
too so one Chrome run covers every width), and measured per width:

  1. document-level: documentElement.scrollWidth vs clientWidth — except when
     the body itself is a horizontal scroll-snap track (the MonoMind deck's
     by-design slide strip); there each snap child must fit the viewport
     instead. The exception is detected from computed style, not a file list.
  2. element-level: any element whose computed overflow-x is `visible` with
     scrollWidth > clientWidth + tolerance has content escaping its own box —
     this is what catches the grid-cell collision. Elements that scroll or
     clip on purpose (overflow-x auto/scroll/hidden, e.g. .tblwrap, .cmd-text)
     are exempt by that same computed style, and so is anything inside a
     horizontally scrolling ancestor (a <pre> in a scrolling code frame is
     contained, not colliding). SVG content is skipped outright — scrollWidth
     has no useful meaning there and diagram label metrics vary by font.

Files with a PAGES/ROUTES hash router keep only the routed page in layout, so
the harness walks every route (in the file's boot language) and measures each.

How the result reaches Python — an in-page completion signal, NOT
--dump-dom: the harness fetch()-POSTs its JSON verdict back to this script's
own HTTP server (same origin, since the server serves the harness too), and
Chrome is killed as soon as the POST lands. Chrome runs on real time with
--remote-debugging-port=0 to keep it alive until then. This is deliberate:
the previous --virtual-time-budget + --dump-dom mechanism hung forever on
Linux Chromium (the templates' infinite animations keep the virtual-time
budget from exhausting, a known headless failure mode), which took three CI
rounds to localize. Do not reintroduce virtual time here.

Chrome is located the way scripts/tedandlisa_thumbs.py locates it, with a
CHROME_BIN environment override for CI. Every invocation's exit code, stderr
and command line are kept for diagnostics; a harness failure is reported as
a HARNESS ERROR and counted apart from overflow findings (exit 2 vs exit 1),
and when the very first file cannot be checked a cheap browser probe decides
whether to abort the whole run instead of timing out on every file.
Stdlib only.
"""

from __future__ import annotations

import argparse
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
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

# (width, height): the two desktop widths the bug class shows at, plus a true
# 375 phone viewport. All rendered inside the iframe of one 2010px window.
WIDTHS = [(1280, 800), (2000, 1100), (375, 667)]
WINDOW = (2010, 1200)
TOLERANCE = 2  # px of sub-pixel rounding forgiven at document/slide level
# Per-element escapes under this are letter-spacing trails, focus-ring slack
# and rounding noise (3-5px was observed on healthy pages); the collision
# class this gate exists for starts well above it (35px+ observed).
ESCAPE_TOLERANCE = 8

# The harness page iframes the target (same origin, served together), walks
# its hash routes at each width, and POSTs the JSON verdict to /r/result on
# the same server. Measurement notes:
#  - PAGES/ROUTES are the templates' own global route arrays; the current
#    hash's last segment is swapped per route so the boot language is kept
#    (covers both "#/en/page" and "#en/route" shapes).
#  - inline elements report scrollWidth/clientWidth 0/0 and drop out naturally.
#  - everything runs on real time (the sleeps are milliseconds of wall clock);
#    a healthy file completes in seconds, and run_chrome kills Chrome the
#    moment the POST arrives.
HARNESS = """<!doctype html><html><head><meta charset="utf-8"><title>gate</title></head>
<body style="margin:0">
<iframe id="f" src="%(src)s" style="display:block;border:0;width:1280px;height:800px"></iframe>
<script>
var WIDTHS = %(widths)s, TOL = %(tol)d, ETOL = %(etol)d;
var frame = document.getElementById('f');
function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

function report(problems) {
  fetch('/r/result', { method: 'POST', body: JSON.stringify(problems),
                       keepalive: true }).catch(function () {});
}

function measure(win, label) {
  var doc = win.document, de = doc.documentElement, out = [];
  var bodyCS = win.getComputedStyle(doc.body);
  var snapX = /x|both/.test(bodyCS.scrollSnapType) &&
              /(auto|scroll)/.test(bodyCS.overflowX);
  if (snapX) {
    // By-design horizontal slide strip: the document scrolls sideways on
    // purpose; each snap child must fit the viewport instead.
    Array.prototype.forEach.call(doc.body.children, function (s) {
      if (s.clientWidth && s.scrollWidth > s.clientWidth + TOL)
        out.push(label + ' slide <' + s.tagName.toLowerCase() +
                 (s.className ? '.' + String(s.className).trim().split(/\\s+/).join('.') : '') +
                 '> content ' + s.scrollWidth + 'px wide in ' + s.clientWidth + 'px');
      if (s.clientWidth > de.clientWidth + TOL)
        out.push(label + ' slide wider than viewport: ' + s.clientWidth +
                 ' > ' + de.clientWidth);
    });
  } else if (de.scrollWidth > de.clientWidth + TOL) {
    out.push(label + ' document scrolls sideways: scrollWidth ' +
             de.scrollWidth + ' > viewport ' + de.clientWidth);
  }
  Array.prototype.forEach.call(doc.querySelectorAll('body *'), function (el) {
    if (el.namespaceURI !== 'http://www.w3.org/1999/xhtml') return;  // SVG etc.
    if (typeof el.scrollWidth !== 'number' || !el.clientWidth) return;
    if (el.scrollWidth <= el.clientWidth + ETOL) return;
    var cs = win.getComputedStyle(el);
    if (cs.overflowX !== 'visible') return;   // scrolls or clips on purpose
    for (var a = el.parentElement; a && a !== doc.body; a = a.parentElement) {
      var ax = win.getComputedStyle(a).overflowX;
      if (ax === 'auto' || ax === 'scroll') return;  // contained by a scroller
    }
    var name = '<' + el.tagName.toLowerCase() +
               (el.id ? '#' + el.id : '') +
               (el.className && String(el.className).trim() ?
                 '.' + String(el.className).trim().split(/\\s+/).join('.') : '') + '>';
    out.push(label + ' ' + name + ' content escapes its box by ' +
             (el.scrollWidth - el.clientWidth) + 'px');
  });
  return out;
}

async function routesOf(win) {
  var list = win.PAGES || win.ROUTES;
  if (!Array.isArray(list) || !list.length || !win.location.hash) return [null];
  return list.slice();
}

async function main() {
  await new Promise(function (r) {
    if (frame.contentDocument && frame.contentDocument.readyState === 'complete') r();
    else frame.addEventListener('load', r, { once: true });
  });
  await sleep(600);                       // boot scripts, router, reveal arming
  var win = frame.contentWindow, problems = [];
  try { await Promise.race([win.document.fonts.ready, sleep(4000)]); } catch (e) {}
  var routes = await routesOf(win);
  for (var w = 0; w < WIDTHS.length; w++) {
    frame.style.width = WIDTHS[w][0] + 'px';
    frame.style.height = WIDTHS[w][1] + 'px';
    await sleep(300);
    for (var i = 0; i < routes.length; i++) {
      var label = '@' + WIDTHS[w][0];
      if (routes[i] !== null) {
        win.location.hash = win.location.hash.replace(/[^\\/#]+$/, routes[i]);
        await sleep(400);                 // router swap + per-page layout
        label += ' page:' + routes[i];
      }
      try { problems = problems.concat(measure(win, label)); }
      catch (e) { problems.push(label + ' MEASURE ERROR ' + e); }
    }
  }
  report(problems);
}
main().catch(function (e) { report(['HARNESS ERROR ' + e]); });
</script>
</body></html>"""

PROBE_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>probe</title></head>
<body><script>
fetch('/r/result', { method: 'POST', body: JSON.stringify(['PROBE-OK']),
                     keepalive: true }).catch(function () {});
</script></body></html>"""


def find_chrome() -> str | None:
    env = os.environ.get("CHROME_BIN")
    if env:
        if pathlib.Path(env).is_file():
            return env
        # A set-but-wrong CHROME_BIN is a CI misconfiguration; falling back
        # to some other browser would hide it.
        print(f"error: CHROME_BIN is set but not a file: {env}", file=sys.stderr)
        return None
    for c in CHROME_CANDIDATES:
        if pathlib.Path(c).is_file():
            return c
    return shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("chrome")


class GateServer(http.server.ThreadingHTTPServer):
    """Serves the harness and the target file from one origin, and receives
    the harness's POSTed verdict."""

    def __init__(self, addr, handler, harness_dir: str, target_dir: str):
        super().__init__(addr, handler)
        self.harness_dir = harness_dir
        self.target_dir = target_dir
        self.result: str | None = None
        self.result_event = threading.Event()

    def reset(self):
        self.result = None
        self.result_event.clear()


class GateHandler(http.server.SimpleHTTPRequestHandler):
    """GET /h/* from the harness dir, GET /t/* from the target file's own
    directory (so the file itself is never modified), POST /r/result to
    deliver the verdict."""

    server: GateServer  # for type checkers only

    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path.startswith("/h/"):
            base, rest = self.server.harness_dir, path[3:]
        elif path.startswith("/t/"):
            base, rest = self.server.target_dir, path[3:]
        else:
            return os.path.join(self.server.harness_dir, "does-not-exist")
        rest = os.path.normpath(rest.lstrip("/"))
        if rest.startswith(".."):
            return os.path.join(base, "does-not-exist")
        return os.path.join(base, rest)

    def do_POST(self):
        if self.path.split("?", 1)[0] == "/r/result":
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            self.server.result = body.decode("utf-8", errors="replace")
            self.server.result_event.set()
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


def serve(harness_dir: str, target_dir: str) -> GateServer:
    srv = GateServer(("127.0.0.1", 0), GateHandler, harness_dir, target_dir)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class ChromeRun:
    """Everything one Chrome invocation produced, kept for diagnostics."""

    def __init__(self, cmd, result, stderr, exit_code, timed_out, seconds):
        self.cmd, self.result, self.stderr = cmd, result, stderr
        self.exit_code, self.timed_out, self.seconds = exit_code, timed_out, seconds

    def diagnose(self) -> list[str]:
        import shlex
        status = ("still running after %.0fs, killed" % self.seconds
                  if self.timed_out else
                  f"exited {self.exit_code} after {self.seconds:.1f}s")
        lines = [f"chrome {status}, no result POSTed by the harness",
                 "cmd: " + " ".join(shlex.quote(c) for c in self.cmd)]
        err = self.stderr.strip()
        lines.append("stderr: " + (err[-3000:] if err else "(empty)"))
        return lines


def chrome_flags(headless_flag: str, profile: str) -> list[str]:
    """One flag set for every invocation, probe included. Hosted Linux
    runners need --no-sandbox and --disable-dev-shm-usage or Chrome dies
    before producing output — the container has no usable sandbox and
    /dev/shm is too small for a renderer — and a per-run --user-data-dir
    under a temp dir avoids profile-lock and crashpad collisions. All of it
    is inert on a desktop macOS Chrome, so the set is unconditional.
    --remote-debugging-port=0 keeps headless Chrome alive after page load
    (without an action flag like --dump-dom it would otherwise exit before
    the harness finishes); run_chrome kills it once the result arrives."""
    return [headless_flag, "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-crash-reporter", "--disable-breakpad",
            "--remote-debugging-port=0",
            f"--user-data-dir={profile}"]


def run_chrome(chrome: str, url: str, srv: GateServer,
               headless_flag: str = "--headless=new",
               timeout: float = 90.0) -> ChromeRun:
    """Launch headless Chrome at `url` and wait for the harness to POST its
    verdict to `srv` (real wall-clock time, hard watchdog `timeout`); kill
    Chrome as soon as the result lands or the deadline passes. Nothing here
    is platform-specific: argv list (no shell quoting), temp files under
    tempfile, killpg on a fresh session — identical on Linux and macOS."""
    srv.reset()
    # ignore_cleanup_errors: a SIGKILLed Chrome's helpers can briefly hold
    # profile files while the temp dir is being removed; that race is not
    # a check failure.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        err = pathlib.Path(profile) / "stderr.txt"
        cmd = ([chrome] + chrome_flags(headless_flag, profile) +
               [f"--window-size={WINDOW[0]},{WINDOW[1]}", url])
        start = time.monotonic()
        timed_out = False
        with open(err, "w") as fe:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=fe,
                                    start_new_session=True)
            try:
                deadline = start + timeout
                while True:
                    if srv.result_event.wait(0.25):
                        break
                    if proc.poll() is not None:
                        # Chrome exited on its own; give a late POST a beat.
                        srv.result_event.wait(1.0)
                        break
                    if time.monotonic() >= deadline:
                        timed_out = True
                        break
            finally:
                if proc.poll() is None:
                    try:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
        return ChromeRun(cmd, srv.result, err.read_text(encoding="utf-8", errors="replace"),
                         proc.returncode, timed_out, time.monotonic() - start)


def parse_result(raw: str | None) -> list[str] | None:
    """The problems list out of the POSTed body, or None when nothing came."""
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(p) for p in parsed]
        return ["HARNESS ERROR: harness result was not a JSON list"]
    except ValueError:
        return ["HARNESS ERROR: harness result was not parseable JSON"]


def check_file(chrome: str, target: pathlib.Path) -> list[str]:
    widths_js = json.dumps([[w, h] for w, h in WIDTHS])
    attempts: list[tuple[str, ChromeRun]] = []
    with tempfile.TemporaryDirectory() as hd:
        harness = HARNESS % {"src": f"/t/{target.name}", "widths": widths_js,
                             "tol": TOLERANCE, "etol": ESCAPE_TOLERANCE}
        (pathlib.Path(hd) / "harness.html").write_text(harness, encoding="utf-8")
        srv = serve(hd, str(target.parent))
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}/h/harness.html"
            # Some chromium builds on CI toolcaches behave differently under
            # --headless=new; when it yields nothing, retry once with the
            # plain --headless mode before declaring the harness broken.
            for flag, tmo in (("--headless=new", 90.0), ("--headless", 60.0)):
                run = run_chrome(chrome, url, srv, flag, tmo)
                problems = parse_result(run.result)
                if problems is not None:
                    return problems
                attempts.append((flag, run))
        finally:
            srv.shutdown()
    report = ["HARNESS ERROR: the harness never POSTed a result under any "
              "headless mode — an infrastructure failure, not an overflow "
              "finding. Per-attempt diagnostics follow:"]
    for flag, run in attempts:
        report.append(f"-- attempt with {flag}:")
        report.extend("   " + line for line in run.diagnose())
    return report


def probe_chrome(chrome: str) -> tuple[bool, list[str]]:
    """Cheap environment sanity check, run only after a harness error on the
    first file: --version, then a page that POSTs immediately, in each
    headless mode. If none of it works the browser is dead and the whole run
    should abort instead of spending the full timeout on every file."""
    msgs = []
    try:
        v = subprocess.run([chrome, "--version"], capture_output=True,
                           timeout=30, text=True)
        msgs.append(f"probe `--version`: exit {v.returncode}, "
                    f"stdout: {v.stdout.strip() or '(empty)'}, "
                    f"stderr: {v.stderr.strip()[-500:] or '(empty)'}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        msgs.append(f"probe `--version` failed to run: {exc}")
    with tempfile.TemporaryDirectory() as hd:
        (pathlib.Path(hd) / "probe.html").write_text(PROBE_PAGE, encoding="utf-8")
        srv = serve(hd, hd)
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}/h/probe.html"
            for flag in ("--headless=new", "--headless"):
                run = run_chrome(chrome, url, srv, flag, timeout=30.0)
                if run.result and "PROBE-OK" in run.result:
                    msgs.append(f"probe page with {flag}: OK "
                                f"({run.seconds:.1f}s to result)")
                    return True, msgs
                msgs.append(f"probe page with {flag} produced no result:")
                msgs.extend("   " + line for line in run.diagnose())
        finally:
            srv.shutdown()
    return False, msgs


def default_targets() -> list[pathlib.Path]:
    reg = ROOT / "templates" / "templates.json"
    if reg.is_file():
        entries = json.loads(reg.read_text())["templates"]
        files = [ROOT / t["file"] for t in entries
                 if t.get("file") and t.get("kind") != "external"]
        if files:
            return files
    return sorted(ROOT.glob("assets/tedandlisa-template*.html"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Rendered horizontal-overflow gate")
    ap.add_argument("files", nargs="*", type=pathlib.Path,
                    help="HTML files to check (default: every first-party template)")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("error: no Chrome or Chromium found (set CHROME_BIN)", file=sys.stderr)
        return 2

    targets = [p.resolve() for p in (args.files or default_targets())]
    missing = [str(p) for p in targets if not p.is_file()]
    if missing:
        print("error: not a file: " + ", ".join(missing), file=sys.stderr)
        return 2

    overflowing, broken = 0, 0
    for i, target in enumerate(targets):
        problems = check_file(chrome, target)
        rel = os.path.relpath(target)
        # A harness/Chrome breakdown is an infrastructure failure and must
        # not masquerade as a design finding; report and count it apart.
        findings = [p for p in problems
                    if "HARNESS ERROR" not in p and "MEASURE ERROR" not in p
                    and not p.startswith(("-- attempt", "   "))]
        errors = [p for p in problems if p not in findings]
        if findings:
            overflowing += 1
            print(f"FAIL {rel}")
        elif errors:
            broken += 1
            print(f"ERROR {rel} — could not be checked")
        else:
            print(f"ok   {rel}")
        for p in findings + errors:
            print(f"     {p}")
        sys.stdout.flush()
        # Fail fast on a dead environment: when the very first file cannot
        # be checked, probe the browser itself; if even a trivial page
        # cannot deliver a result, every remaining file would fail the
        # same slow way.
        if i == 0 and errors and not findings and len(targets) > 1:
            ok, msgs = probe_chrome(chrome)
            for msg in msgs:
                print(msg)
            if not ok:
                print("\nABORT: the browser cannot render anything in this "
                      "environment — skipping the remaining "
                      f"{len(targets) - 1} files (infrastructure failure, "
                      "not an overflow finding)")
                return 2
            print("probe passed — the browser works; continuing with the "
                  "remaining files")
            sys.stdout.flush()
    print()
    if overflowing:
        print(f"{overflowing} of {len(targets)} files have horizontal overflow")
    if broken:
        print(f"{broken} of {len(targets)} files could not be checked "
              "(harness or Chrome failure, not an overflow finding)")
    if not overflowing and not broken:
        print(f"all {len(targets)} files clean at "
              + ", ".join(str(w) for w, _ in WIDTHS) + "px")
    return 1 if overflowing else (2 if broken else 0)


if __name__ == "__main__":
    raise SystemExit(main())
