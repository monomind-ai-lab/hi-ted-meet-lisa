#!/usr/bin/env bash
# Assemble the deployable site/ folder from the repository's real artifacts.
#
# The site duplicates nothing in git: previews, the intake panel, and the
# brand images live at their canonical paths and are copied in here at
# deploy time. Cloudflare Pages runs this as its build command with
# build output directory `site`:
#
#   build command:     bash site/sync.sh
#   output directory:  site
#
# Run it locally before previewing site/index.html.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p site/previews site/assets

# Live previews (the real generated files) + their gallery thumbnails.
cp previews/*.html site/previews/
cp templates/thumbs/*.png site/previews/

# The intake panel — built to run from static hosting, falling back to a
# copy-answers payload when there is no runner. We inject the same
# window.__MONOMIND_INTAKE__ context the runner would (templates from the
# registry), with thumbnails as relative URLs instead of data URIs since
# the site serves the PNGs anyway. The canonical panel stays untouched.
python3 - <<'PY'
import json, pathlib
root = pathlib.Path(".")
entries = json.loads((root / "templates/templates.json").read_text())["templates"]
cards = []
for t in entries:
    card = {k: t.get(k) for k in
            ("id", "name", "tagline", "kind", "best_for", "dependencies",
             "languages", "preview", "skill", "badge") if t.get(k) is not None}
    thumb = root / t.get("thumb", "")
    if t.get("thumb") and thumb.is_file():
        card["thumb"] = "previews/" + thumb.name
    if card.get("preview"):
        card["preview"] = "previews/" + pathlib.Path(card["preview"]).name
    cards.append(card)
html = (root / "assets/tedandlisa-intake.html").read_text()
inject = ("<script>window.__MONOMIND_INTAKE__ = "
          + json.dumps({"mode": "web", "templates": cards}) + ";</script>\n")
marker = '<script>\n"use strict";'
assert marker in html, "intake panel script marker not found"
(root / "site/intake.html").write_text(
    html.replace(marker, inject + marker, 1))
print("site/intake.html written with", len(cards), "template cards")
PY

# Brand images referenced by the landing page. The two -cream figure PNGs
# are pre-tinted RGBA renders (cream fill, luminance-as-alpha) of the
# grayscale figure art extracted from the Canva brand deck.
cp assets/tedlisaidea.jpg assets/tedmeetslisa.jpg assets/monomind-mark-white.svg \
   assets/ted-figure-cream.png assets/lisa-figure-cream.png site/assets/

echo "site/ assembled:"
find site -type f | sort
