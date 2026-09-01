#!/usr/bin/env python3
"""Regenerate the intake panel's no-registry fallback template list.

assets/tedandlisa-intake.html is one standalone file that has to work when it
is opened straight from file:// with nothing injected — no runner, no deploy
step, so no window.__MONOMIND_INTAKE__ and no fetch (file:// forbids it). That
is the only reason the panel carries its own copy of the template list at all:

    var TEMPLATES = CTX.templates || [ ... ];

Because it cannot be derived at runtime, it is derived here instead. This
script rewrites that block from templates/templates.json so the copy is
generated rather than hand-maintained, and --check fails when the two have
drifted apart:

    python3 scripts/tedandlisa_intake_fallback.py            # rewrite in place
    python3 scripts/tedandlisa_intake_fallback.py --check    # exit 1 on drift

The fallback carries only the fields a card needs before anything is injected
(id, name, kind, type, tagline, plus skill and badge where the registry sets
them) — the same projection scripts/tedandlisa_intake.py and the website
repository's sync.sh make, minus the keys that are meaningless without a
served site: thumb, preview,
best_for and dependencies. Dropping `skill` is not cosmetic — payload()'s
`handoff` reads it, so an `external` entry without one sends the agent off to
copy a template that does not exist.
"""

from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "templates" / "templates.json"
PANEL = ROOT / "assets" / "tedandlisa-intake.html"

# The generated span: the assignment's opening line through the `];` that
# closes it. Anchored to the start of a line so a `[` inside a tagline cannot
# end the match early.
BLOCK = re.compile(
    r"^var TEMPLATES = CTX\.templates \|\| \[\n.*?^\];$",
    re.MULTILINE | re.DOTALL,
)

# Written onto the first line of an entry, in this order; `tagline` gets the
# second line to itself because it is the long one.
HEAD_KEYS = ("id", "name", "kind", "type", "skill", "badge")


def js(value: str) -> str:
    """A JS double-quoted literal. The panel is UTF-8, so text stays literal."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(entries: list[dict]) -> str:
    lines = ["var TEMPLATES = CTX.templates || ["]
    for t in entries:
        head = ", ".join(f"{k}: {js(t[k])}" for k in HEAD_KEYS if t.get(k))
        lines.append(f"  {{ {head},")
        lines.append(f"    tagline: {js(t.get('tagline', ''))} }},")
    if entries:
        # The last entry closes the array rather than continuing it.
        lines[-1] = lines[-1][:-1]
    lines.append("];")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 instead of rewriting")
    args = ap.parse_args()

    entries = json.loads(REGISTRY.read_text())["templates"]
    html = PANEL.read_text()

    if not BLOCK.search(html):
        print("error: fallback template block not found in "
              "assets/tedandlisa-intake.html — has the assignment been reworded?",
              file=sys.stderr)
        return 2

    wanted = render(entries)
    current = BLOCK.search(html).group(0)

    if current == wanted:
        print(f"fallback list is in step with the registry ({len(entries)} templates)")
        return 0

    if args.check:
        print("error: the intake panel's fallback template list has drifted from "
              "templates/templates.json.\n"
              "       Run: python3 scripts/tedandlisa_intake_fallback.py",
              file=sys.stderr)
        diff = difflib.unified_diff(
            current.splitlines(), wanted.splitlines(),
            fromfile="assets/tedandlisa-intake.html",
            tofile="templates/templates.json", lineterm="", n=1)
        for line in diff:
            print(f"  {line}", file=sys.stderr)
        return 1

    PANEL.write_text(BLOCK.sub(lambda _: wanted, html, count=1))
    print(f"rewrote the fallback list in assets/tedandlisa-intake.html "
          f"({len(entries)} templates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
