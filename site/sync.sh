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

# The canonical mark uses currentColor, which an <img> renders black.
# Derive a solid-white copy for the page's dark chrome (deploy artifact
# only — the canonical file keeps currentColor).
sed 's/currentColor/#ffffff/g' assets/monomind-mark-white.svg \
  > site/assets/monomind-mark-solid-white.svg

# Favicon: the white mark on the brand's dark-olive tile, so it reads on
# light and dark tab strips alike. Derived, like the mark above.
python3 - <<'PY'
import pathlib, re
mark = pathlib.Path("assets/monomind-mark-white.svg").read_text()
mark = mark.replace("currentColor", "#ffffff")
inner = re.sub(r"^.*?<svg[^>]*>", "", mark, flags=re.S)
inner = inner.replace("</svg>", "")
fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
       '<rect width="512" height="512" rx="96" fill="#15160f"/>'
       '<g transform="translate(56 56) scale(0.78125)">' + inner + "</g></svg>")
pathlib.Path("site/assets/favicon.svg").write_text(fav)
print("site/assets/favicon.svg written")
PY

# Social/SEO meta image — page one of the Canva brand deck.
cp assets/tedlisa-cover-og.jpg site/assets/

echo "site/ assembled:"
find site -type f | sort
