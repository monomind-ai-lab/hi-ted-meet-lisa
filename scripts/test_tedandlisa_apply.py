#!/usr/bin/env python3
"""Tests for scripts/tedandlisa_apply.py.

For every first-party template: copy it to a temp dir, apply a representative
intake fixture (dark theme, pruned menu, English-only languages, no export,
credit off, custom accent), and assert the mechanical transforms landed —
theme block gone, menu chrome gone where the template makes that mechanical,
no self-download control, no colophon line, accent token changed where mapped
— while the file stays structurally whole (closing </html>, script count only
moving where expected). Then apply the same answers again and require the
result to be byte-identical.

    python3 scripts/test_tedandlisa_apply.py
"""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "tedandlisa_apply.py"
ASSETS = ROOT / "assets"

TEMPLATES = {
    "monomind-deck": "tedandlisa-template.html",
    "web-document": "tedandlisa-template-web-document.html",
    "mermaid-master": "tedandlisa-template-mermaid-master.html",
    "architecture": "tedandlisa-template-architecture.html",
    "sitemap-ia": "tedandlisa-template-sitemap-ia.html",
    "project-website": "tedandlisa-template-project-website.html",
    "evidence-deck": "tedandlisa-template-evidence-deck.html",
    "paper-brief": "tedandlisa-template-paper-brief.html",
}

ACCENT = "#e8590c"

# templates that carry the html[data-theme="light"] block + a theme control
DUAL_THEME = {"monomind-deck", "web-document", "sitemap-ia",
              "project-website", "architecture"}

# where the accent hex must land after apply (regex), or None for
# architecture, whose colours are semantic and must NOT be repainted
ACCENT_TOKEN = {
    "monomind-deck": r"--accent:\s*#e8590c",
    "web-document": r"--primary:\s*#e8590c",
    "sitemap-ia": r"--primary:\s*#e8590c",
    "project-website": r"--accent:\s*#e8590c",
    "evidence-deck": r"--sig:\s*#e8590c",
    "paper-brief": r"--red:\s*#e8590c",
    "mermaid-master": r"--accent:\s*#e8590c",
    "architecture": None,
}

# expected change in the number of <script blocks: only the MonoMind deck
# loses one (the Google Translate script goes with the English-only answer)
SCRIPT_DELTA = {"monomind-deck": -1}


def fixture(template: str) -> dict:
    """A representative answers object for the given template."""
    answers = {
        "template": template,
        "theme": "dark",
        "languages": ["en"],
        "noTranslate": ["Acme Corp", "release.tar.gz"],
        "export": [],
        "credit": False,
        "accent": ACCENT,
        "review": "after",
        "style": {"mode": "default", "designFile": None, "notes": None},
        "logo": {"mode": "monomind", "file": None, "href": None},
        "elements": [],
    }
    if template == "monomind-deck":
        answers["menu"] = {"mode": "minimal"}
        answers["backgrounds"] = {"mode": "gradient",
                                  "cover": None, "closing": None}
        answers["slideCount"] = "auto"
    elif template in ("evidence-deck", "paper-brief"):
        # `none` is the mechanical menu deletion on this family
        # (`minimal` is a judgment row there)
        answers["menu"] = {"mode": "none"}
        answers["backgrounds"] = {"mode": "gradient",
                                  "cover": None, "closing": None}
        answers["slideCount"] = "auto"
    else:
        answers["menu"] = {"mode": "full", "items": ["start", "contents"],
                           "home": None, "github": None}
    return answers


def run_apply(answers_path, file_path, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT),
         "--answers", str(answers_path), "--file", str(file_path), *extra],
        capture_output=True, text=True)


class ApplyTemplates(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="tedandlisa-apply-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def prepare(self, template):
        src = ASSETS / TEMPLATES[template]
        dst = self.tmp / ("%s.html" % template)
        shutil.copyfile(src, dst)
        answers = self.tmp / ("%s.json" % template)
        answers.write_text(json.dumps({
            "version": 1, "handoff": None, "prompt": "test",
            "promptEdited": False, "references": [],
            "answers": fixture(template)}), encoding="utf-8")
        return src, dst, answers

    def check_template(self, template):
        src, dst, answers = self.prepare(template)
        original = src.read_text(encoding="utf-8")

        proc = run_apply(answers, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        out = dst.read_text(encoding="utf-8")
        report = proc.stdout

        # structurally whole
        self.assertTrue(out.rstrip().endswith("</html>"),
                        "%s: closing </html> lost" % template)

        # theme: the light block and its control go on the dual templates
        if template in DUAL_THEME:
            self.assertNotIn('html[data-theme="light"]', out,
                             "%s: light-theme CSS survived" % template)
            self.assertNotRegex(
                out, r'<button[^>]*id="(btnTheme|deck-menu-theme)"',
                "%s: theme control survived" % template)
        else:
            # single-palette templates: the row is reported, never guessed at
            self.assertIn("theme=dark", report)

        # menu: gone where the deletion is mechanical
        if template == "monomind-deck":
            self.assertNotIn('<nav class="deck-menu"', out)
            self.assertNotIn('id="deck-menu-panel"', out)
            # minimal keeps the restart control, unhidden
            m = re.search(r'<button class="deck-restart"[^>]*>', out)
            self.assertIsNotNone(m, "restart control missing")
            self.assertNotIn("hidden", m.group(0))
        elif template in ("evidence-deck", "paper-brief"):
            self.assertNotIn('id="deckMenu"', out)
        elif template == "architecture":
            # no deck-menu chrome; the language segment must survive
            self.assertIn('id="btnEn"', out)
        elif template != "mermaid-master":
            # no deck-menu chrome ships; the row must not delete the site nav
            self.assertIn("<nav", out)

        # export: no live self-download control remains
        self.assertNotRegex(
            out, r'<button[^>]*id="(btnHtml|deck-menu-html)"',
            "%s: self-download control survived" % template)

        # credit: the colophon line is gone everywhere
        self.assertNotIn("html.monomind.one/?ref=file", out,
                         "%s: colophon survived" % template)

        # accent
        pattern = ACCENT_TOKEN[template]
        if pattern is None:
            self.assertNotIn(ACCENT, out,
                             "architecture must not be repainted")
            self.assertIn("WARNING", report)
        else:
            self.assertRegex(out, pattern,
                             "%s: accent token not set" % template)

        # script count only moves where expected
        delta = SCRIPT_DELTA.get(template, 0)
        self.assertEqual(out.count("<script"),
                         original.count("<script") + delta,
                         "%s: unexpected script-count change" % template)

        # idempotent: a second run must change nothing
        first = dst.read_bytes()
        proc2 = run_apply(answers, dst)
        self.assertEqual(proc2.returncode, 0, proc2.stderr or proc2.stdout)
        self.assertEqual(first, dst.read_bytes(),
                         "%s: second apply changed the file" % template)

        return out, report


# one test method per template so failures name the template directly
def _make(template):
    def test(self):
        self.check_template(template)
    return test


for _t in TEMPLATES:
    setattr(ApplyTemplates, "test_%s" % _t.replace("-", "_"), _make(_t))


class ApplyDetails(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="tedandlisa-apply-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _copy(self, template):
        dst = self.tmp / "doc.html"
        shutil.copyfile(ASSETS / TEMPLATES[template], dst)
        return dst

    def _answers(self, obj):
        p = self.tmp / "answers.json"
        p.write_text(json.dumps(obj), encoding="utf-8")
        return p

    def test_monomind_deck_english_only_removes_translate_machinery(self):
        dst = self._copy("monomind-deck")
        a = self._answers({"template": "monomind-deck", "languages": ["en"]})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = dst.read_text(encoding="utf-8")
        self.assertNotIn('<div class="lang-switch', out)
        self.assertNotIn('id="google_translate_element"', out)
        self.assertNotIn("googleTranslateElementInit", out)

    def test_monomind_deck_language_trim_and_terms(self):
        dst = self._copy("monomind-deck")
        a = self._answers({"template": "monomind-deck",
                           "languages": ["en", "ko"],
                           "noTranslate": ["Acme Corp"]})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = dst.read_text(encoding="utf-8")
        self.assertNotIn('data-lang="zh-TW"', out)
        self.assertIn('data-lang="ko"', out)
        self.assertIn("includedLanguages: 'en,ko'", out)
        self.assertIn("Acme Corp|", out)

    def test_light_theme_pins_html_attribute(self):
        dst = self._copy("web-document")
        a = self._answers({"template": "web-document", "theme": "light"})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = dst.read_text(encoding="utf-8")
        m = re.search(r"<html\b[^>]*>", out)
        self.assertIn('data-theme="light"', m.group(0))
        self.assertNotRegex(out, r'<button[^>]*id="btnTheme"')
        # the light palette itself stays
        self.assertIn('html[data-theme="light"]', out)

    def test_evidence_menu_full_materialises_github(self):
        dst = self._copy("evidence-deck")
        url = "https://github.com/acme/widgets"
        a = self._answers({"template": "evidence-deck",
                           "menu": {"mode": "full",
                                    "items": ["start", "contents", "github"],
                                    "home": None, "github": url}})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = dst.read_text(encoding="utf-8")
        m = re.search(r'<a role="menuitem" href="%s"' % re.escape(url), out)
        self.assertIsNotNone(m)
        # inserted as live markup, not inside the comment
        cspans = [(c.start(), c.end())
                  for c in re.finditer(r"<!--.*?-->", out, re.S)]
        self.assertFalse(any(s <= m.start() < e for s, e in cspans))

    def test_style_brand_is_reported_with_the_extraction_hint(self):
        # `style: brand` is never mechanical: the file is left alone, the
        # row is NOT-MECHANICAL, and the detail names the skill to run first.
        dst = self._copy("web-document")
        before = dst.read_bytes()
        a = self._answers({"template": "web-document",
                           "style": {"mode": "brand", "designFile": None,
                                     "notes": None,
                                     "url": "https://example.com", "file": None}})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, dst.read_bytes())
        line = [l for l in proc.stdout.splitlines() if l.strip().startswith("style")]
        self.assertEqual(len(line), 1, proc.stdout)
        self.assertIn("NOT-MECHANICAL", line[0])
        self.assertIn("/lisa-brand", line[0])
        self.assertIn("designmd", line[0])
        # the other modes keep the plain detail — no hint to follow
        a2 = self._answers({"template": "web-document",
                            "style": {"mode": "designmd", "designFile": None,
                                      "notes": None, "url": None, "file": None}})
        proc2 = run_apply(a2, dst)
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        line2 = [l for l in proc2.stdout.splitlines() if l.strip().startswith("style")]
        self.assertIn("NOT-MECHANICAL", line2[0])
        self.assertNotIn("/lisa-brand", line2[0])

    def test_dry_run_leaves_file_untouched(self):
        dst = self._copy("monomind-deck")
        before = dst.read_bytes()
        a = self._answers({"template": "monomind-deck", "theme": "dark",
                           "credit": False})
        proc = run_apply(a, dst, "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, dst.read_bytes())
        self.assertIn("APPLIED", proc.stdout)

    def test_unreadable_input_is_nonzero(self):
        dst = self._copy("monomind-deck")
        bad = self.tmp / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        self.assertNotEqual(run_apply(bad, dst).returncode, 0)
        wrong_version = self._answers({"version": 7, "answers":
                                       {"template": "monomind-deck"}})
        self.assertNotEqual(run_apply(wrong_version, dst).returncode, 0)
        unknown = self._answers({"template": "no-such-template"})
        self.assertNotEqual(run_apply(unknown, dst).returncode, 0)

    def test_handoff_payload_is_a_clean_no_op(self):
        dst = self._copy("monomind-deck")
        before = dst.read_bytes()
        a = self._answers({"version": 1, "handoff": "/lisa-design",
                           "answers": {"template": "monomind-deck"}})
        proc = run_apply(a, dst)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, dst.read_bytes())
        self.assertIn("handoff", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
