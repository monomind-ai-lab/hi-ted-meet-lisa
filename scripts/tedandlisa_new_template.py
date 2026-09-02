#!/usr/bin/env python3
"""Tools for turning a finished HTML document into a reusable template.

    python3 scripts/tedandlisa_new_template.py analyze SOURCE.html
    python3 scripts/tedandlisa_new_template.py register --id ID --name NAME \
        --file assets/FILE.html --kind slides|document \
        --type present|read|diagram|site [--layout reflow|stage] [--tagline ...]

`analyze` is read-only. It reports what a document is made of — tokens, class
inventory, chrome, scripts, external dependencies, how it handles language, and
a best guess at its `layout` (`stage` when a fixed canvas is scaled uniformly
from the viewport, else `reflow`) with the evidence it rests on — so the
skeleton keeps the machinery and replaces only the content. It cannot decide
what is content and what is chrome; that judgment stays with the agent.

`register` adds an entry to templates/templates.json. It refuses to overwrite an
existing id.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "templates" / "templates.json"


def analyze(path: pathlib.Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")

    tokens = re.findall(r"(--[a-z0-9-]+)\s*:", html)
    classes = collections.Counter(
        c for attr in re.findall(r'class="([^"]*)"', html) for c in attr.split() if c
    )
    bodies = [m.group(1) for m in re.finditer(
        r"<script(?![^>]*\bsrc=)(?![^>]*text/plain)[^>]*>(.*?)</script>", html, re.S)]
    scripts = [
        {"chars": len(b),
         "first_line": next((l.strip() for l in b.split("\n") if l.strip()), "")[:90]}
        for b in bodies
    ]
    external = sorted(set(
        re.findall(r'<script[^>]*src="([^"]+)"', html)
        + re.findall(r'<link[^>]*href="(https?://[^"]+)"', html)
    ))
    sections = re.findall(r'<section[^>]*class="([^"]*)"[^>]*id="([^"]*)"', html)
    if not sections:
        sections = [(c, i) for i, c in re.findall(r'<section[^>]*id="([^"]*)"[^>]*class="([^"]*)"', html)]

    if re.search(r'body\[data-lang', html):
        i18n = "inline dual-language spans toggled by body[data-lang] — offline, no service"
    elif "translate.google" in html or "googleTranslateElement" in html:
        i18n = "Google Translate, loaded on demand"
    else:
        i18n = "single language"

    inline_media = re.findall(r"data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]{200,})", html)
    layout, layout_evidence = guess_layout(html, bodies)
    return {
        "file": str(path),
        "bytes": len(html.encode()),
        "lang": (re.search(r'<html[^>]*lang="([^"]+)"', html) or [None, None])[1],
        "title": (re.search(r"<title>(.*?)</title>", html, re.S) or [None, ""])[1].strip(),
        "design_tokens": {"count": len(set(tokens)), "sample": sorted(set(tokens))[:14]},
        "top_classes": classes.most_common(24),
        "section_containers": [{"class": c, "id": i} for c, i in sections],
        "script_blocks": scripts,
        "external_dependencies": external,
        "i18n": i18n,
        "layout": layout,
        "layout_evidence": layout_evidence,
        "inline_media": [{"type": t, "approx_kb": len(b) * 3 // 4 // 1024} for t, b in inline_media],
        "self_contained": not [e for e in external if "fonts.googleapis" not in e and "fonts.gstatic" not in e],
    }


# A uniform fit — the scale being the smaller of the two *viewport* ratios —
# is the signature of a letterboxed stage; a single-axis ratio is responsive
# maths, and a fit against some container's clientWidth (the web document's
# diagram viewer fits an SVG to its own panel that way) is a viewer, not a
# stage. So only the window's own measures count. The argument list is
# bounded so a `;` or a brace ends the match.
UNIFORM_FIT = re.compile(r"Math\.min\(([^;{}]{0,240})\)")
VIEWPORT_W = re.compile(r"(?<![\w.])innerWidth|window\.innerWidth|documentElement\.clientWidth")
VIEWPORT_H = re.compile(r"(?<![\w.])innerHeight|window\.innerHeight|documentElement\.clientHeight")


def guess_layout(html: str, scripts: list[str]) -> tuple[str, str]:
    """Best guess at the registry's `layout`, with the evidence it rests on.

    `stage`: a <deck-stage> element (the frontend-slides model), or a script
    that scales something by `Math.min(innerWidth / W, innerHeight / H)` and
    applies it as a transform — a fixed canvas that letterboxes rather than
    re-laying out. Anything else is `reflow`, which is what every first-party
    template is. It is a guess: read the stylesheet before registering.
    """
    if re.search(r"<deck-stage[\s>]", html) or \
            re.search(r"customElements\.define\(\s*['\"]deck-stage", html):
        return "stage", "a <deck-stage> element — the frontend-slides deck-stage.js model"
    for n, body in enumerate(scripts, 1):
        for m in UNIFORM_FIT.finditer(body):
            arg = m.group(1)
            if not (VIEWPORT_W.search(arg) and VIEWPORT_H.search(arg)):
                continue
            if not re.search(r"scale\(|\bzoom\b", body):
                continue
            dims = re.findall(r"/\s*(\d{3,4})\b", arg)
            if len(dims) >= 2:
                size = f"{dims[0]}×{dims[1]}"
            else:
                size = "unknown size"
                for block in re.findall(r"\{([^{}]*)\}", html):
                    w = re.search(r"(?<![-\w])width:\s*(\d{3,4})px", block)
                    h = re.search(r"(?<![-\w])height:\s*(\d{3,4})px", block)
                    if w and h and int(w.group(1)) >= 960 and int(h.group(1)) >= 540:
                        size = f"{w.group(1)}×{h.group(1)} (from the stylesheet)"
                        break
            return "stage", (f"script block {n} scales a fixed {size} canvas uniformly "
                             f"from {m.group(0)[:80]} and applies it as a transform")
    media = len(re.findall(r"@media\b", html))
    clamp = len(re.findall(r"\bclamp\(", html))
    return "reflow", (f"no fixed canvas scaled from the viewport; {media} @media rule(s) "
                      f"and {clamp} clamp() value(s) re-lay the content out instead")


def register(args) -> int:
    reg = json.loads(REGISTRY.read_text()) if REGISTRY.is_file() else {"version": 1, "templates": []}
    if any(t["id"] == args.id for t in reg["templates"]):
        print(f"error: template id {args.id!r} already registered; pick another id", file=sys.stderr)
        return 1
    if not (ROOT / args.file).is_file():
        print(f"error: {args.file} not found", file=sys.stderr)
        return 1

    reg["templates"].append({
        "id": args.id,
        "name": args.name,
        "tagline": args.tagline or "",
        "file": args.file,
        "patterns": args.patterns or "",
        "thumb": f"templates/thumbs/{args.id}.png",
        "kind": args.kind,
        "type": args.type,
        "layout": args.layout,
        "best_for": args.best_for or "",
        "navigation": args.navigation or "",
        "languages": args.languages or "",
        "dependencies": args.dependencies or "",
        "features": args.feature or [],
    })
    REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n")
    print(f"registered {args.id}. Now run:\n"
          f"  python3 scripts/tedandlisa_thumbs.py --only {args.id}\n"
          f"  python3 scripts/tedandlisa_intake_fallback.py")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    a = sp.add_parser("analyze", help="read-only structural report")
    a.add_argument("source")

    r = sp.add_parser("register", help="add an entry to the template registry")
    r.add_argument("--id", required=True)
    r.add_argument("--name", required=True)
    r.add_argument("--file", required=True, help="repo-relative path to the skeleton")
    r.add_argument("--kind", required=True, choices=["slides", "document"],
                   help="the shape — it decides which intake questions are asked")
    r.add_argument("--type", required=True,
                   choices=["present", "read", "diagram", "site"],
                   help="what it is for — the gallery flag and filter, never "
                        "the payload")
    r.add_argument("--layout", default="reflow", choices=["reflow", "stage"],
                   help="how it meets the viewport — reflow re-lays content out "
                        "for any width (the default); stage is a fixed 1920×1080 "
                        "canvas scaled uniformly and letterboxed. Marked on the "
                        "gallery card, never in the payload")
    r.add_argument("--tagline")
    r.add_argument("--patterns")
    r.add_argument("--best-for", dest="best_for")
    r.add_argument("--navigation")
    r.add_argument("--languages")
    r.add_argument("--dependencies")
    r.add_argument("--feature", action="append")

    args = ap.parse_args()
    if args.cmd == "analyze":
        src = pathlib.Path(args.source).expanduser()
        if not src.is_file():
            print(f"error: {src} not found", file=sys.stderr)
            return 2
        json.dump(analyze(src), sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0
    return register(args)


if __name__ == "__main__":
    raise SystemExit(main())
