#!/usr/bin/env python3
"""Tools for turning a finished HTML document into a reusable template.

    python3 scripts/tedandlisa_new_template.py analyze SOURCE.html
    python3 scripts/tedandlisa_new_template.py register --id ID --name NAME \
        --file assets/FILE.html --kind slides|document [--tagline ...]

`analyze` is read-only. It reports what a document is made of — tokens, class
inventory, chrome, scripts, external dependencies, and how it handles language —
so the skeleton keeps the machinery and replaces only the content. It cannot
decide what is content and what is chrome; that judgment stays with the agent.

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
    scripts = [
        {"chars": len(m.group(1)),
         "first_line": next((l.strip() for l in m.group(1).split("\n") if l.strip()), "")[:90]}
        for m in re.finditer(r"<script(?![^>]*\bsrc=)(?![^>]*text/plain)[^>]*>(.*?)</script>", html, re.S)
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
        "inline_media": [{"type": t, "approx_kb": len(b) * 3 // 4 // 1024} for t, b in inline_media],
        "self_contained": not [e for e in external if "fonts.googleapis" not in e and "fonts.gstatic" not in e],
    }


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
        "best_for": args.best_for or "",
        "navigation": args.navigation or "",
        "languages": args.languages or "",
        "dependencies": args.dependencies or "",
        "features": args.feature or [],
    })
    REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n")
    print(f"registered {args.id}. Now run:\n"
          f"  python3 scripts/tedandlisa_thumbs.py --only {args.id}")
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
    r.add_argument("--kind", required=True, choices=["slides", "document"])
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
