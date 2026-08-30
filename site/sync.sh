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
   assets/ted-and-lisa-in-frame.png site/assets/

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

# Cloudflare Web Analytics — cookieless, so no consent banner. Injected only
# when CF_BEACON_TOKEN is set: locally that means never, and the deploy
# workflow passes it from the CF_BEACON_TOKEN repository secret once it
# exists. A missing token skips silently — a placeholder token must never
# ship. The token itself is a one-time dashboard step: Cloudflare dashboard
# → Web Analytics → Add a site → html.monomind.one, then
#   gh secret set CF_BEACON_TOKEN
# The markup is Cloudflare's own snippet verbatim (type='module', which
# defers by default, wrapped in its comment markers) so a reader of the
# page source sees what it is.
# Note: index.html and 404.html are canonical files, so running this with
# the token set locally dirties the working tree — deploy-time use only.
# If you do run it locally, restore them:
#   git checkout site/index.html site/404.html
if [ -n "${CF_BEACON_TOKEN:-}" ]; then
  CF_BEACON_TOKEN="$CF_BEACON_TOKEN" python3 - <<'PY'
import os, pathlib
token = os.environ["CF_BEACON_TOKEN"]
beacon = ("<!-- Cloudflare Web Analytics -->"
          "<script type='module'"
          " src='https://static.cloudflareinsights.com/beacon.min.js'"
          " data-cf-beacon='{\"token\": \"" + token + "\"}'></script>"
          "<!-- End Cloudflare Web Analytics -->")
for name in ("index.html", "intake.html", "404.html"):
    p = pathlib.Path("site") / name
    html = p.read_text()
    if "cloudflareinsights.com/beacon.min.js" in html:
        print("site/" + name + ": beacon already present, left alone")
        continue
    assert "</body>" in html, name + " has no </body> to inject before"
    p.write_text(html.replace("</body>", beacon + "\n</body>", 1))
    print("site/" + name + ": analytics beacon injected")
PY
else
  echo "CF_BEACON_TOKEN not set — analytics beacon skipped"
fi

echo "site/ assembled:"
find site -type f | sort
