#!/usr/bin/env python3
"""Apply the deterministic intake answers to a copied template file.

The /lisa skill copies a template from assets/ and then works through the
"Applying the answers" table in skills/lisa/SKILL.md. Many of those rows are
pure text surgery — delete the light-theme block, prune the menu, drop the
self-download control — and doing them by hand is slow and error-prone. This
script performs exactly the mechanical rows and reports everything else, so
the building agent knows precisely what remains:

    python3 scripts/tedandlisa_apply.py --answers intake.json --file deck.html
    python3 scripts/tedandlisa_apply.py --answers intake.json --file deck.html --dry-run

Input is the intake payload described in references/intake-contract.md —
either the full wrapper ({version, answers, ...}) or the bare answers object.

Every answer prints one report line:

    APPLIED           — the file was changed (or was already in the asked-for
                        state and needed nothing).
    SKIPPED (reason)  — the transform did not run: its anchor was not found,
                        it was already applied, or it does not exist in this
                        template. The file is left untouched for that row.
    NOT-MECHANICAL    — a judgment row the building agent must do by hand.

The script never guesses: a transform whose anchor markup is missing is
skipped and reported, not approximated. Running it twice is safe — the second
run finds its work already done and changes nothing.

Exit status is 0 unless the input itself is unusable (missing/invalid JSON,
unknown payload version, unknown template id, unreadable HTML file).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# ────────────────────────────────────────────────────────────────────
# Template knowledge. Anchors below are read from the shipped templates
# in assets/ — if a template's chrome is reworked, update this table.
# ────────────────────────────────────────────────────────────────────

LIGHT_MARKER = 'html[data-theme="light"]'
CREDIT_MARKER = "html.monomind.one/?ref=file"

# ids of the eight first-party templates (registry: templates/templates.json)
KNOWN = {
    "monomind-deck", "web-document", "mermaid-master", "architecture",
    "sitemap-ia", "project-website", "evidence-deck", "paper-brief",
}

# A string that survives every transform here, used only to warn when the
# file does not look like the template the answers claim.
FINGERPRINT = {
    "monomind-deck": 'id="deck-progress"',
    "web-document": 'id="page-overview"',
    "mermaid-master": 'id="langToggle"',
    "architecture": "monomind-arch-theme",
    "sitemap-ia": "nav-primary-k4v9m2",
    "project-website": "data-nav-mobile",
    "evidence-deck": "--sig-dim",
    "paper-brief": "--red-wash",
}

# theme: which ground the template ships, and its theme control (if any).
# "dual" templates carry the html[data-theme="light"] block.
THEME = {
    "monomind-deck": {"dual": True, "control": "deck-menu-theme"},
    "web-document": {"dual": True, "control": "btnTheme"},
    "sitemap-ia": {"dual": True, "control": "btnTheme"},
    "project-website": {"dual": True, "control": "btnTheme"},
    "architecture": {"dual": True, "control": "btnTheme"},
    "evidence-deck": {"dual": False, "ships": "dark"},
    "paper-brief": {"dual": False, "ships": "light"},
    "mermaid-master": {"dual": False, "ships": "light"},
}

# export: the live self-download control, where one ships. evidence-deck and
# paper-brief ship it commented out (needs a pasted handler), mermaid-master
# not at all — adding one there is the agent's work.
EXPORT_CONTROL = {
    "monomind-deck": "deck-menu-html",
    "web-document": "btnHtml",
    "sitemap-ia": "btnHtml",
    "project-website": "btnHtml",
    "architecture": "btnHtml",
}

# credit: how much markup around the ?ref=file link the template's own
# comment says to remove.
#   a        — the <a> element only
#   span     — the enclosing <span> wrapper
#   p        — the enclosing <p> (monomind-deck: "Made with" text sits
#              outside the anchor)
#   a+middot — the <a> plus the "&middot;" separator before it
CREDIT_SCOPE = {
    "monomind-deck": "p",
    "web-document": "a",
    "sitemap-ia": "span",
    "project-website": "a",
    "architecture": "a+middot",
    "evidence-deck": "a",
    "paper-brief": "span",
    "mermaid-master": "a",
}

# menu families: which chrome the template ships.
#   monomind — nav#deck-menu + hidden button#deck-restart (kebab-case ids)
#   evidence — nav#deckMenu (camelCase ids); home/github/html ship as
#              commented snippets to paste back
#   none     — no deck-menu chrome at all (site nav is content)
MENU_FAMILY = {
    "monomind-deck": "monomind",
    "evidence-deck": "evidence",
    "paper-brief": "evidence",
    "web-document": "none",
    "sitemap-ia": "none",
    "project-website": "none",
    "architecture": "none",
    "mermaid-master": "none",
}

LANG_LABEL = {"en": "EN", "ko": "KR", "zh-TW": "ZH-TW"}
LANG_TAG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "source", "track", "wbr"}


# ────────────────────────────────────────────────────────────────────
# Colour helpers (accent derivations are simple channel math so they
# stay deterministic; the design-review pass re-measures contrast).
# ────────────────────────────────────────────────────────────────────

def parse_hex(value: str) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        v = "#" + "".join(c * 2 for c in v[1:])
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        return None
    return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def darken(rgb, f):
    return tuple(max(0, round(c * (1 - f))) for c in rgb)


def lighten(rgb, f):
    return tuple(min(255, round(c + (255 - c) * f)) for c in rgb)


def rgba(rgb, a):
    return "rgba(%d,%d,%d,%s)" % (rgb[0], rgb[1], rgb[2], a)


# accent: per template, the design tokens that carry the accent, with how
# each value is derived from the picked hex. architecture is deliberately
# absent — its colours are semantic (frontend/backend/data/...), so the
# builder must report rather than repaint.
def accent_edits(template: str, rgb) -> list[tuple[str, str, str]]:
    """[(block, css-var, new-value)] — block is 'root' or 'light'."""
    h = to_hex(rgb)
    if template == "monomind-deck":
        return [("root", "--accent", h), ("root", "--meta", h)]
    if template in ("web-document", "sitemap-ia"):
        return [("root", "--primary", h),
                ("root", "--primary-active", to_hex(darken(rgb, 0.20))),
                ("root", "--primary-glow", to_hex(lighten(rgb, 0.18)))]
    if template == "project-website":
        return [("root", "--accent", h),
                ("root", "--accent-strong", to_hex(darken(rgb, 0.20))),
                ("root", "--glow", rgba(rgb, ".14")),
                ("light", "--accent", to_hex(darken(rgb, 0.20))),
                ("light", "--accent-strong", to_hex(darken(rgb, 0.35))),
                ("light", "--glow", rgba(darken(rgb, 0.20), ".10"))]
    if template == "evidence-deck":
        return [("root", "--sig", h), ("root", "--sig-dim", rgba(rgb, ".13"))]
    if template == "paper-brief":
        return [("root", "--red", h), ("root", "--red-wash", rgba(rgb, ".07"))]
    if template == "mermaid-master":
        return [("root", "--accent", h),
                ("root", "--accent-tint", rgba(rgb, ".08"))]
    return []


# monomind-deck carries two accent-derived rgba() literals in its token
# block (--elev-raised, --focus-ring); they follow the accent hex.
MONOMIND_ACCENT_LITERAL = "rgba(79, 140, 255,"


# ────────────────────────────────────────────────────────────────────
# Text surgery. Anchor on stable ids/classes; when an anchor is not
# found, do nothing and let the caller report SKIPPED.
# ────────────────────────────────────────────────────────────────────

class Editor:
    def __init__(self, text: str):
        self.text = text
        self.changed = False

    # -- comments -----------------------------------------------------
    def comment_spans(self):
        return [(m.start(), m.end())
                for m in re.finditer(r"<!--.*?-->", self.text, re.S)]

    def in_comment(self, pos, spans=None):
        for s, e in (spans if spans is not None else self.comment_spans()):
            if s <= pos < e:
                return True
        return False

    # -- element location ---------------------------------------------
    def element_span(self, lt: int):
        """(start, end) of the whole element whose '<' is at lt."""
        m = re.match(r"<([a-zA-Z][\w-]*)", self.text[lt:])
        if not m:
            return None
        tag = m.group(1).lower()
        gt = self.text.find(">", lt)
        if gt == -1:
            return None
        if self.text[gt - 1] == "/" or tag in VOID_TAGS:
            return (lt, gt + 1)
        spans = self.comment_spans()
        pat = re.compile(r"<%s\b|</%s\s*>" % (tag, tag), re.I)
        depth, pos = 1, gt + 1
        while depth:
            m2 = pat.search(self.text, pos)
            if not m2:
                return None
            if self.in_comment(m2.start(), spans):
                pos = m2.end()
                continue
            if m2.group(0).startswith("</"):
                depth -= 1
            else:
                depth += 1
            pos = m2.end()
        return (lt, pos)

    def find_by_id(self, elem_id: str):
        pat = re.compile(r'<[a-zA-Z][\w-]*\b[^>]*\bid="%s"' % re.escape(elem_id))
        spans = self.comment_spans()
        for m in pat.finditer(self.text):
            if not self.in_comment(m.start(), spans):
                return self.element_span(m.start())
        return None

    def find_by_class(self, tag: str, cls: str, start=0, end=None):
        pat = re.compile(r'<%s\b[^>]*\bclass="[^"]*\b%s\b[^"]*"'
                         % (tag, re.escape(cls)))
        spans = self.comment_spans()
        end = len(self.text) if end is None else end
        for m in pat.finditer(self.text, start, end):
            if not self.in_comment(m.start(), spans):
                return self.element_span(m.start())
        return None

    # -- deletion ------------------------------------------------------
    def _tidy(self, s: int, e: int):
        line_start = self.text.rfind("\n", 0, s) + 1
        if self.text[line_start:s].strip() == "":
            s = line_start
        nl = self.text.find("\n", e)
        if nl != -1 and self.text[e:nl].strip() == "":
            e = nl + 1
        return s, e

    def delete_span(self, s: int, e: int):
        s, e = self._tidy(s, e)
        self.text = self.text[:s] + self.text[e:]
        self.changed = True

    def delete_preceding_comment(self, s: int, keyword: str):
        """Remove a '<!-- keyword ... -->' sitting right above position s."""
        before = self.text[:s]
        stripped = before.rstrip()
        if not stripped.endswith("-->"):
            return s
        cs = stripped.rfind("<!--")
        if cs == -1 or keyword not in stripped[cs:]:
            return s
        new_s, _ = self._tidy(cs, len(stripped))
        self.text = self.text[:new_s] + self.text[s:]
        self.changed = True
        return new_s

    def delete_element_by_id(self, elem_id: str, comment_kw: str | None = None):
        span = self.find_by_id(elem_id)
        if not span:
            return False
        self.delete_span(*span)
        if comment_kw:
            self.delete_preceding_comment(self._tidy(span[0], span[0])[0],
                                          comment_kw)
        return True

    # -- attributes ----------------------------------------------------
    def open_tag_span(self, lt: int):
        return (lt, self.text.find(">", lt) + 1)

    def set_attr_in_open_tag(self, lt: int, attr: str, value: str):
        s, e = self.open_tag_span(lt)
        tag = self.text[s:e]
        pat = re.compile(r'\b%s="[^"]*"' % re.escape(attr))
        if pat.search(tag):
            new = pat.sub('%s="%s"' % (attr, value), tag, count=1)
        else:
            new = tag[:-1].rstrip()
            if new.endswith("/"):
                new = new[:-1].rstrip() + ' %s="%s"/>' % (attr, value)
            else:
                new += ' %s="%s">' % (attr, value)
        if new != tag:
            self.text = self.text[:s] + new + self.text[e:]
            self.changed = True
        return new != tag


def delete_light_css(ed: Editor) -> int:
    """Delete every top-level CSS rule whose selector group starts with
    html[data-theme="light"]. Returns the number of rules removed."""
    removed = 0
    guard = 0
    while True:
        guard += 1
        if guard > 500:
            break
        idx = -1
        spans = ed.comment_spans()
        search = 0
        while True:
            cand = ed.text.find(LIGHT_MARKER, search)
            if cand == -1:
                break
            if ed.in_comment(cand, spans):
                search = cand + 1
                continue
            prev = ed.text[:cand].rstrip()
            if prev.endswith(","):
                # mid-group selector; the group's first selector will be
                # found instead on the next pass (all shipped groups lead
                # with the light selector).
                search = cand + 1
                continue
            idx = cand
            break
        if idx == -1:
            break
        brace = ed.text.find("{", idx)
        if brace == -1:
            break
        depth, pos = 1, brace + 1
        while depth and pos < len(ed.text):
            c = ed.text[pos]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            pos += 1
        ed.delete_span(idx, pos)
        removed += 1
    return removed


def find_token_block(ed: Editor, which: str):
    """Span of the declarations inside the first :root{...} or the first
    html[data-theme="light"]{...} block."""
    pat = (re.compile(r":root\s*\{") if which == "root"
           else re.compile(re.escape(LIGHT_MARKER) + r"\s*\{"))
    m = pat.search(ed.text)
    if not m:
        return None
    depth, pos = 1, m.end()
    while depth and pos < len(ed.text):
        c = ed.text[pos]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        pos += 1
    return (m.end(), pos - 1)


def set_css_token(ed: Editor, block, var: str, value: str):
    s, e = block
    seg = ed.text[s:e]
    m = re.search(r"(%s\s*:\s*)([^;}]+)" % re.escape(var), seg)
    if not m:
        return None
    old = m.group(2).strip()
    if old == value:
        return False
    seg = seg[:m.start(2)] + value + seg[m.end(2):]
    ed.text = ed.text[:s] + seg + ed.text[e:]
    ed.changed = True
    return True


# ────────────────────────────────────────────────────────────────────
# Report
# ────────────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.rows = []

    def applied(self, key, detail):
        self.rows.append((key, "APPLIED", detail))

    def skipped(self, key, reason):
        self.rows.append((key, "SKIPPED", reason))

    def manual(self, key, detail="left to the agent"):
        self.rows.append((key, "NOT-MECHANICAL", detail))

    def print(self):
        width = max((len(k) for k, _, _ in self.rows), default=0)
        for key, status, detail in self.rows:
            print("  %-*s  %-15s %s" % (width, key, status,
                                        ("(%s)" % detail) if detail else ""))


# ────────────────────────────────────────────────────────────────────
# Per-answer transforms
# ────────────────────────────────────────────────────────────────────

def apply_theme(ed, template, theme, rep):
    key = "theme=%s" % theme
    info = THEME[template]
    if not info["dual"]:
        ships = info["ships"]
        if theme == ships:
            rep.applied(key, "template ships %s; nothing to remove" % ships)
        else:
            rep.manual(key, "template carries no second palette — "
                            "left to the agent")
        return
    control = info["control"]
    if theme == "dark":
        n = delete_light_css(ed)
        gone = ed.delete_element_by_id(control, "theme")
        if n or gone:
            rep.applied(key, "removed %d light-theme rule%s%s"
                        % (n, "" if n == 1 else "s",
                           " and #%s" % control if gone else ""))
        else:
            rep.skipped(key, "already applied — no light block or control found")
    elif theme == "light":
        m = re.search(r"<html\b[^>]*>", ed.text)
        pinned = False
        if m and 'data-theme="light"' not in m.group(0):
            pinned = ed.set_attr_in_open_tag(m.start(), "data-theme", "light")
        gone = ed.delete_element_by_id(control, "theme")
        if pinned or gone:
            rep.applied(key, 'set data-theme="light" on <html>%s'
                        % (" and removed #%s" % control if gone else ""))
        else:
            rep.skipped(key, "already applied")
    elif theme == "toggle":
        rep.applied(key, "both palettes and the control kept as shipped")
    else:
        rep.skipped(key, "unknown theme value")


def apply_export(ed, template, export, rep):
    wants = isinstance(export, list) and "html" in export
    key = "export=%s" % (export if isinstance(export, list) else [export])
    control = EXPORT_CONTROL.get(template)
    if wants:
        if control and ed.find_by_id(control):
            rep.applied(key, "self-download control #%s kept" % control)
        elif control:
            rep.skipped(key, "control #%s not found — was it deleted?" % control)
        else:
            rep.manual(key, "this template ships no live self-download "
                            "control; the agent must add one")
        return
    if not control:
        rep.applied(key, "no live self-download control ships in this template")
        return
    if ed.delete_element_by_id(control, "html"):
        rep.applied(key, "removed #%s (the @media print block stays)" % control)
    else:
        rep.skipped(key, "already absent")


def _menu_anchors(ed, nav_span):
    """Real (uncommented) <a role="menuitem"> elements inside the nav,
    classified as ('github'|'home', span)."""
    out = []
    spans = ed.comment_spans()
    pat = re.compile(r'<a\s[^>]*\brole="menuitem"[^>]*>')
    for m in pat.finditer(ed.text, nav_span[0], nav_span[1]):
        if ed.in_comment(m.start(), spans):
            continue
        el = ed.element_span(m.start())
        if not el or el[1] > nav_span[1]:
            continue
        body = ed.text[el[0]:el[1]]
        kind = "github" if ('viewBox="0 0 16 16"' in body
                            or "github.com" in body) else "home"
        out.append((kind, el))
    return out


def _set_href(ed, el_span, url):
    tag_end = ed.text.find(">", el_span[0])
    tag = ed.text[el_span[0]:tag_end + 1]
    new = re.sub(r'\bhref="[^"]*"', 'href="%s"' % url, tag, count=1)
    if new != tag:
        ed.text = ed.text[:el_span[0]] + new + ed.text[tag_end + 1:]
        ed.changed = True
        return True
    return False


def apply_menu_monomind(ed, menu, rep):
    mode = menu.get("mode")
    if mode == "minimal":
        restart = ed.find_by_id("deck-restart")
        did = []
        if restart:
            s, e = ed.open_tag_span(restart[0])
            tag = ed.text[s:e]
            new = re.sub(r"\s+hidden\b", "", tag)
            if new != tag:
                ed.text = ed.text[:s] + new + ed.text[e:]
                ed.changed = True
                did.append("unhid #deck-restart")
        if ed.delete_element_by_id("deck-menu", "menu"):
            did.append("deleted nav.deck-menu")
        if did:
            rep.applied("menu.mode=minimal", ", ".join(did))
        else:
            rep.skipped("menu.mode=minimal", "already applied")
        return
    if mode == "none":
        did = []
        if ed.delete_element_by_id("deck-restart", "menu"):
            did.append("deleted #deck-restart")
        if ed.delete_element_by_id("deck-menu", "menu"):
            did.append("deleted nav.deck-menu")
        if did:
            rep.applied("menu.mode=none", ", ".join(did))
        else:
            rep.skipped("menu.mode=none", "already applied")
        return
    if mode != "full":
        rep.skipped("menu.mode=%s" % mode, "unknown menu mode")
        return

    # full: the standalone restart button serves minimal only.
    if ed.delete_element_by_id("deck-restart", "minimal"):
        rep.applied("menu.mode=full", "removed the minimal-menu #deck-restart")
    else:
        rep.skipped("menu.mode=full", "#deck-restart already absent")

    items = menu.get("items") or ["start"]
    if "contents" not in items:
        a = ed.delete_element_by_id("deck-menu-contents", "contents")
        b = ed.delete_element_by_id("deck-contents")
        if a or b:
            rep.applied("menu.items-contents", "removed the Contents item")
        else:
            rep.skipped("menu.items-contents", "already absent")
    else:
        rep.applied("menu.items+contents", "kept (built from data-screen-label)")

    # theme / html items follow the theme and export answers (reported there).

    for kind in ("home", "github"):
        url = menu.get(kind)
        wanted = kind in items and bool(url)
        nav = ed.find_by_id("deck-menu")
        anchor = None
        if nav:
            for k, el in _menu_anchors(ed, nav):
                if k == kind:
                    anchor = el
                    break
        rkey = "menu.items%s%s" % ("+" if wanted else "-", kind)
        if wanted:
            if anchor:
                if _set_href(ed, anchor, url):
                    rep.applied(rkey, "pointed the %s item at %s" % (kind, url))
                else:
                    rep.applied(rkey, "%s item already points at %s" % (kind, url))
            else:
                rep.skipped(rkey, "anchor not found")
        else:
            if anchor:
                ed.delete_span(*anchor)
                rep.applied(rkey, "removed the %s item%s" % (
                    kind, " (URL empty)" if kind in items else ""))
                if kind == "github":
                    nav = ed.find_by_id("deck-menu")
                    if nav:
                        sep = ed.find_by_class("div", "deck-menu-sep",
                                               nav[0], nav[1])
                        if sep:
                            ed.delete_span(*sep)
            else:
                rep.skipped(rkey, "already absent")

    if "language" in items:
        rep.skipped("menu.items+language",
                    "this template has no in-menu language item — "
                    "the fixed switch serves it")


def apply_menu_evidence(ed, menu, rep):
    mode = menu.get("mode")
    if mode == "none":
        if ed.delete_element_by_id("deckMenu", "menu"):
            rep.applied("menu.mode=none", "deleted nav#deckMenu")
        else:
            rep.skipped("menu.mode=none", "already applied")
        return
    if mode == "minimal":
        rep.manual("menu.mode=minimal",
                   "this template ships no standalone restart control — "
                   "replace the menu by hand per the template comment")
        return
    if mode != "full":
        rep.skipped("menu.mode=%s" % mode, "unknown menu mode")
        return

    items = menu.get("items") or ["start"]
    if "contents" not in items:
        a = ed.delete_element_by_id("deckMenuContents", "contents")
        b = ed.delete_element_by_id("deckContents")
        if a or b:
            rep.applied("menu.items-contents", "removed the Contents item")
        else:
            rep.skipped("menu.items-contents", "already absent")
    else:
        rep.applied("menu.items+contents", "kept (built from data-label-*)")
    if "language" not in items:
        if ed.delete_element_by_id("deckMenuLang", "language"):
            rep.applied("menu.items-language", "removed the in-menu language item")
        else:
            rep.skipped("menu.items-language", "already absent")

    placeholders = {"home": "[HOME URL]", "github": "[REPOSITORY URL]"}
    for kind in ("home", "github"):
        url = menu.get(kind)
        wanted = kind in items and bool(url)
        rkey = "menu.items%s%s" % ("+" if wanted else "-", kind)
        if not wanted:
            rep.applied(rkey, "ships absent; nothing to remove")
            continue
        if ('href="%s"' % url) in ed.text:
            rep.skipped(rkey, "already present")
            continue
        # materialise the anchor from the template's own commented snippet
        ph = placeholders[kind]
        spans = ed.comment_spans()
        snippet = None
        host = None
        for s, e in spans:
            body = ed.text[s:e]
            m = re.search(r'<a role="menuitem" href="%s".*?</a>'
                          % re.escape(ph), body, re.S)
            if m:
                snippet = m.group(0).replace(ph, url)
                host = s
                break
        if snippet and host is not None:
            line_start = ed.text.rfind("\n", 0, host) + 1
            indent = ed.text[line_start:host]
            if indent.strip():
                indent = "      "
            ed.text = (ed.text[:line_start] + indent + snippet + "\n"
                       + ed.text[line_start:])
            ed.changed = True
            rep.applied(rkey, "inserted the %s item pointing at %s" % (kind, url))
        else:
            rep.skipped(rkey, "anchor not found — commented snippet missing")

    if "html" in items:
        rep.manual("menu.items+html",
                   "the download item ships commented out and needs its "
                   "handler pasted in — see the template comment")


def apply_menu(ed, template, menu, rep):
    if not isinstance(menu, dict):
        rep.skipped("menu", "malformed menu object")
        return
    family = MENU_FAMILY[template]
    if family == "monomind":
        apply_menu_monomind(ed, menu, rep)
    elif family == "evidence":
        apply_menu_evidence(ed, menu, rep)
    else:
        mode = menu.get("mode")
        if mode == "full":
            rep.applied("menu.mode=full",
                        "this template's navigation is its content nav; "
                        "no deck-menu chrome to prune")
        else:
            rep.manual("menu.mode=%s" % mode,
                       "no deck-menu chrome in this template — any trimming "
                       "of its navigation is the agent's judgment")


def apply_languages(ed, template, langs, rep):
    if not isinstance(langs, list) or not langs:
        rep.skipped("languages", "malformed languages value")
        return
    ordered = []
    for tag in langs:
        if tag not in ordered:
            ordered.append(tag)
    if "en" not in ordered:
        ordered.insert(0, "en")
    key = "languages=%s" % ",".join(ordered)

    if template != "monomind-deck":
        if ordered == ["en"]:
            rep.manual(key, "inline-bilingual template — deleting the second "
                            "language's spans/sections is content work")
        else:
            rep.manual(key, "inline-bilingual template — each language is "
                            "written content, not chrome")
        return

    if ordered == ["en"]:
        did = []
        sw = ed.find_by_class("div", "lang-switch")
        if sw:
            ed.delete_span(*sw)
            did.append("lang-switch")
        if ed.delete_element_by_id("google_translate_element"):
            did.append("#google_translate_element")
        # the whole translate script block goes with them
        gpos = ed.text.find("googleTranslateElementInit")
        if gpos != -1 and not ed.in_comment(gpos):
            spos = ed.text.rfind("<script", 0, gpos)
            if spos != -1:
                span = ed.element_span(spos)
                if span:
                    ed.delete_span(*span)
                    did.append("translate script")
        if did:
            rep.applied(key, "removed " + ", ".join(did))
        else:
            rep.skipped(key, "already applied")
        return

    # trim / extend the switch, and keep includedLanguages in agreement
    sw = ed.find_by_class("div", "lang-switch")
    if not sw:
        rep.skipped(key, "anchor not found — .lang-switch missing")
        return
    bad = [t for t in ordered if not LANG_TAG.fullmatch(t)]
    keep = [t for t in ordered if t not in bad]
    seg = ed.text[sw[0]:sw[1]]
    existing = re.findall(r'<button[^>]*\bdata-lang="([^"]+)"', seg)
    new_seg = seg
    for tag in existing:
        if tag not in keep:
            new_seg = re.sub(
                r'\s*<button[^>]*\bdata-lang="%s"[^>]*>.*?</button>'
                % re.escape(tag), "", new_seg, flags=re.S)
    additions = [t for t in keep if t not in existing]
    if additions:
        btns = "".join(
            '\n    <button type="button" data-lang="%s">%s</button>'
            % (t, LANG_LABEL.get(t, t.upper())) for t in additions)
        new_seg = re.sub(r"\s*</div>\s*$", btns + "\n  </div>", new_seg)
    if new_seg != seg:
        ed.text = ed.text[:sw[0]] + new_seg + ed.text[sw[1]:]
        ed.changed = True
    inc = re.search(r"includedLanguages:\s*'([^']*)'", ed.text)
    inc_changed = False
    if inc:
        wanted = ",".join(keep)
        if inc.group(1) != wanted:
            ed.text = (ed.text[:inc.start(1)] + wanted + ed.text[inc.end(1):])
            ed.changed = True
            inc_changed = True
    if new_seg != seg or inc_changed:
        rep.applied(key, "switch trimmed to %s%s" % (
            ",".join(keep),
            "; includedLanguages updated" if inc_changed else ""))
    else:
        rep.skipped(key, "already in the asked-for state")
    for t in bad:
        rep.skipped("languages:%s" % t,
                    "not a BCP-47-shaped tag — left to the agent")


JS_REGEX_SPECIALS = r"\/^$.|?*+()[]{}"


def escape_js_regex(term: str) -> str:
    return "".join("\\" + c if c in JS_REGEX_SPECIALS else c for c in term)


def apply_notranslate(ed, template, terms, rep):
    if isinstance(terms, str):
        terms = [t.strip() for t in terms.split(",") if t.strip()]
    if not isinstance(terms, list):
        rep.skipped("noTranslate", "malformed value")
        return
    terms = [t for t in terms if isinstance(t, str) and t.strip()]
    key = "noTranslate(%d terms)" % len(terms)
    if template != "monomind-deck":
        rep.applied(key, "nothing is machine-translated in this template; "
                         "no protection list to extend")
        return
    if not terms:
        rep.applied(key, "no terms to add")
        return
    m = re.search(r"var TERMS = /\((.*?)\)/g;", ed.text, re.S)
    if not m:
        if "googleTranslateElementInit" not in ed.text:
            rep.skipped(key, "translate script removed (English-only deck) — "
                             "nothing to protect")
        else:
            rep.skipped(key, "anchor not found — TERMS list missing")
        return
    body = m.group(1)
    new_terms = []
    for t in terms:
        esc = escape_js_regex(t)
        if esc in body or t in body:
            continue
        new_terms.append(esc)
    if not new_terms:
        rep.applied(key, "every term already protected")
        return
    insert = "|".join(new_terms) + "|"
    ed.text = ed.text[:m.start(1)] + insert + ed.text[m.start(1):]
    ed.changed = True
    rep.applied(key, "added %d term%s to the protection list"
                % (len(new_terms), "" if len(new_terms) == 1 else "s"))


def apply_credit(ed, template, credit, rep):
    if credit is True or credit is None:
        rep.applied("credit=true", "colophon kept")
        return
    scope = CREDIT_SCOPE[template]
    removed = 0
    while True:
        spans = ed.comment_spans()
        pos, search = -1, 0
        while True:
            cand = ed.text.find(CREDIT_MARKER, search)
            if cand == -1:
                break
            if ed.in_comment(cand, spans):
                search = cand + 1
                continue
            pos = cand
            break
        if pos == -1:
            break
        a_start = ed.text.rfind("<a", 0, pos)
        if a_start == -1:
            break
        el = ed.element_span(a_start)
        if not el:
            break
        s, e = el
        if scope in ("span", "p"):
            # take the enclosing wrapper element: walk back over <span>/<p>
            # openings until one's element actually contains the anchor.
            tag, look = scope, s
            for _ in range(6):
                w = ed.text.rfind("<" + tag, 0, look)
                if w == -1:
                    break
                wspan = ed.element_span(w)
                if wspan and wspan[0] < s and wspan[1] >= e:
                    s, e = wspan
                    break
                look = w
        elif scope == "a+middot":
            before = ed.text[:s]
            m = re.search(r"&middot;\s*$", before)
            if m:
                s = m.start()
        ed.delete_span(s, e)
        ed.delete_preceding_comment(ed.text.rfind("\n", 0, s) + 1, "credit")
        removed += 1
        if removed > 8:
            break
    if removed:
        rep.applied("credit=false", "removed %d colophon line%s"
                    % (removed, "" if removed == 1 else "s"))
    else:
        rep.skipped("credit=false", "colophon already absent")


def apply_backgrounds(ed, template, bg, rep):
    mode = bg.get("mode") if isinstance(bg, dict) else bg
    key = "backgrounds=%s" % mode
    if mode == "monomind":
        rep.applied(key, "embedded artwork kept as shipped")
        return
    if mode == "upload":
        rep.manual(key, "swapping the cover/closing data: URIs for the "
                        "supplied files is the agent's work")
        return
    if mode != "gradient":
        rep.skipped(key, "unknown backgrounds mode")
        return
    if template != "monomind-deck":
        rep.applied(key, "this template embeds no cover photography")
        return
    # 1. drop is-photo from the slide class lists
    stripped = 0

    def strip_cls(m):
        nonlocal stripped
        cls = m.group(1)
        if "is-photo" in cls.split():
            stripped += 1
            kept = " ".join(t for t in cls.split() if t != "is-photo")
            return 'class="%s"' % kept
        return m.group(0)

    new = re.sub(r'class="([^"]*\bis-photo\b[^"]*)"', strip_cls, ed.text)
    if new != ed.text:
        ed.text = new
        ed.changed = True
    # 2. delete the .slide.is-photo rule that embeds the artwork
    deleted_rule = False
    for m in re.finditer(r"\.slide\.is-photo\s*\{", ed.text):
        depth, pos = 1, m.end()
        while depth and pos < len(ed.text):
            c = ed.text[pos]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            pos += 1
        if "data:image" in ed.text[m.start():pos]:
            ed.delete_span(m.start(), pos)
            deleted_rule = True
            break
    if stripped or deleted_rule:
        rep.applied(key, "removed is-photo from %d slide%s%s"
                    % (stripped, "" if stripped == 1 else "s",
                       " and deleted the embedded artwork rule"
                       if deleted_rule else ""))
    else:
        rep.skipped(key, "already applied — no photographic slides found")


def apply_accent(ed, template, accent, rep):
    # accept "default" | "#hex" (the contract) and a defensive
    # {mode, hex} object should the panel serialise it that way.
    if isinstance(accent, dict):
        value = accent.get("hex") if accent.get("mode") == "custom" else "default"
    else:
        value = accent
    if value in (None, "", "default"):
        rep.applied("accent=default", "template's own accent kept")
        return
    rgb = parse_hex(value)
    key = "accent=%s" % value
    if rgb is None:
        rep.skipped(key, "not a hex colour")
        return
    if template == "architecture":
        rep.skipped(key, "WARNING: this template's colours are semantic "
                         "(component families) — not applied; the builder "
                         "should report this to the user")
        return
    edits = accent_edits(template, rgb)
    root = find_token_block(ed, "root")
    light = find_token_block(ed, "light")
    done, already, missed = [], [], []
    for block_name, var, val in edits:
        block = root if block_name == "root" else light
        if block is None:
            # a deleted light block (theme: dark) is expected, not an error
            already.append("%s (%s block absent)" % (var, block_name))
            continue
        r = set_css_token(ed, block, var, val)
        # spans shift after an edit; re-find the blocks
        root = find_token_block(ed, "root")
        light = find_token_block(ed, "light")
        if r is None:
            missed.append(var)
        elif r:
            done.append("%s=%s" % (var, val))
        else:
            already.append(var)
    if template == "monomind-deck":
        lit = MONOMIND_ACCENT_LITERAL
        if lit in ed.text:
            ed.text = ed.text.replace(lit, "rgba(%d, %d, %d," % rgb)
            ed.changed = True
            done.append("accent rgba() in --elev-raised/--focus-ring")
    if done:
        detail = "set " + ", ".join(done)
        if missed:
            detail += "; not found: " + ", ".join(missed)
        detail += (" — derived shades are channel math; "
                   "design review re-checks contrast")
        rep.applied(key, detail)
    elif already and not missed:
        rep.skipped(key, "already applied")
    else:
        rep.skipped(key, "anchor not found: " + ", ".join(missed))


# ────────────────────────────────────────────────────────────────────
# Driver
# ────────────────────────────────────────────────────────────────────

# answers this script owns; everything else is reported, not touched.
MECHANICAL = ("theme", "export", "menu", "languages", "noTranslate",
              "credit", "backgrounds", "accent")

# answers that are judgment calls by design (see the SKILL.md table).
# `contract` — audience, purpose, outcome, core message, delivery, afterlife,
# divergence — shapes the writing and never the chrome, so it is reported
# here for the agent rather than silently ignored the way `review` is.
JUDGMENT = ("contract", "slideCount", "elements", "style", "logo", "siteType",
            "projectStage", "sitemapSource", "benchmarks", "evidence",
            "prototype", "delivery", "format")


def judgment_hint(key, value):
    """The NOT-MECHANICAL detail for a judgment row.

    Plain "left to the agent" for all of them except the one whose next
    step is a different skill: `style` in `brand` mode means the brand has
    to be extracted (skills/lisa-brand/) before there is a design.md to
    apply, and a one-line pointer here is cheaper than a missed step.
    """
    if key == "style" and isinstance(value, dict) and value.get("mode") == "brand":
        return ("left to the agent — mode brand: run /lisa-brand on style.url / "
                "style.file first, then apply its brand/design.md as style: "
                "designmd, through the tokens")
    return "left to the agent"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--answers", required=True,
                    help="intake payload JSON (full wrapper or bare answers)")
    ap.add_argument("--file", required=True,
                    help="the copied template HTML file to edit in place")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the report without writing the file")
    args = ap.parse_args()

    try:
        data = json.loads(pathlib.Path(args.answers).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("error: cannot read answers: %s" % exc, file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: answers JSON is not an object", file=sys.stderr)
        return 2

    if "answers" in data and isinstance(data["answers"], dict):
        version = data.get("version")
        if version is not None and version != 1:
            print("error: unknown payload version %r — refusing to guess"
                  % version, file=sys.stderr)
            return 2
        if data.get("handoff"):
            print("handoff payload (%s): nothing to apply here — invoke the "
                  "named skill instead" % data["handoff"])
            return 0
        answers = data["answers"]
    else:
        answers = data

    template = answers.get("template")
    if template not in KNOWN:
        print("error: unknown template id %r — cannot pick anchors"
              % template, file=sys.stderr)
        return 2

    path = pathlib.Path(args.file)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("error: cannot read file: %s" % exc, file=sys.stderr)
        return 2

    print("applying %s answers to %s (template: %s)%s"
          % (args.answers, args.file, template,
             " [dry-run]" if args.dry_run else ""))
    if FINGERPRINT[template] not in text:
        print("  warning: file does not look like the %s template "
              "(fingerprint %r missing) — anchors may not match"
              % (template, FINGERPRINT[template]))

    ed = Editor(text)
    rep = Report()
    rep.applied("template=%s" % template, "decides the anchors used below")

    # order matters: control deletions inside the menu run before the menu
    # itself may be deleted, and accent runs after theme has settled the
    # token blocks.
    if "theme" in answers:
        apply_theme(ed, template, answers["theme"], rep)
    if "export" in answers:
        apply_export(ed, template, answers["export"], rep)
    if "menu" in answers:
        apply_menu(ed, template, answers["menu"], rep)
    if "languages" in answers:
        apply_languages(ed, template, answers["languages"], rep)
    if "noTranslate" in answers:
        apply_notranslate(ed, template, answers["noTranslate"], rep)
    if "credit" in answers:
        apply_credit(ed, template, answers["credit"], rep)
    if "backgrounds" in answers:
        apply_backgrounds(ed, template, answers["backgrounds"], rep)
    if "accent" in answers:
        apply_accent(ed, template, answers["accent"], rep)

    for key in JUDGMENT:
        if key in answers:
            rep.manual("%s" % key, judgment_hint(key, answers[key]))
    handled = set(MECHANICAL) | set(JUDGMENT) | {"template", "review"}
    for key in answers:
        if key not in handled:
            rep.skipped(key, "unknown answer key — left to the agent")
    # `review` steers the build process, not the file: ignored by design.

    rep.print()

    if ed.changed and not args.dry_run:
        path.write_text(ed.text, encoding="utf-8")
        print("wrote %s" % args.file)
    elif ed.changed:
        print("dry-run: %s left unchanged" % args.file)
    else:
        print("no changes needed in %s" % args.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
