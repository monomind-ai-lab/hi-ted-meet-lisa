#!/usr/bin/env python3
"""Tests for the pure half of scripts/check_languages.py.

The browser half is exercised against real templates by hand (and by the
skill, at handover). What is unit-tested here is `judge()` — the rules that
turn "what the reader can reach" into findings — because that is where the
answer-versus-file comparison actually lives, and it is cheap to get subtly
backwards.

    python3 scripts/test_check_languages.py
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from check_languages import judge, normalise  # noqa: E402


def found(reachable, controls=(), boot="en", errors=()):
    return {"boot": boot, "reachable": list(reachable),
            "controls": [dict(c) for c in controls], "errors": list(errors)}


CTRL_EN = {"how": "declared", "lang": "en", "label": "EN"}
CTRL_KO = {"how": "declared", "lang": "ko", "label": "한국어"}


class Normalise(unittest.TestCase):
    def test_region_is_upper_base_is_lower(self):
        self.assertEqual(normalise("zh-tw"), "zh-TW")
        self.assertEqual(normalise("ZH-Tw"), "zh-TW")
        self.assertEqual(normalise("EN"), "en")

    def test_a_region_is_not_dissolved_into_its_base(self):
        # zh and zh-TW are different answers; merging them would let a file
        # that offers only Simplified pass a Traditional request.
        self.assertNotEqual(normalise("zh"), normalise("zh-TW"))

    def test_a_script_subtag_folds_to_the_tag_the_intake_uses(self):
        # How the two Chinese templates actually declare themselves:
        # sitemap-ia sets <html lang="zh-Hant-TW">, paper-brief "zh-Hant".
        # The intake only ever says zh-TW, so both have to arrive there or a
        # correct build fails in both directions at once.
        self.assertEqual(normalise("zh-Hant-TW"), "zh-TW")
        self.assertEqual(normalise("zh-Hant"), "zh-TW")
        self.assertEqual(normalise("zh-Hans-CN"), "zh-CN")

    def test_an_ordinary_region_is_left_alone(self):
        # The fold table must not swallow tags it was not written for.
        self.assertEqual(normalise("en-GB"), "en-GB")
        self.assertEqual(normalise("pt-br"), "pt-BR")

    def test_empty_and_junk_do_not_raise(self):
        self.assertEqual(normalise(""), "")
        self.assertEqual(normalise("-"), "")


class Judge(unittest.TestCase):
    def test_exact_match_is_silent(self):
        self.assertEqual(judge(found(["en", "ko"], [CTRL_EN, CTRL_KO]), ["en", "ko"]), [])

    def test_single_language_with_no_control_is_silent(self):
        # The archify artifact and a trimmed MonoMind deck both look like this.
        self.assertEqual(judge(found(["en"]), ["en"]), [])

    def test_chosen_but_unreachable(self):
        problems = judge(found(["en"], [CTRL_EN]), ["en", "ko"])
        self.assertEqual(len(problems), 1)
        self.assertIn("ko", problems[0])
        self.assertIn("nothing in the file selects it", problems[0])

    def test_offered_but_not_chosen(self):
        problems = judge(found(["en", "ko"], [CTRL_EN, CTRL_KO]), ["en"])
        joined = " ".join(problems)
        self.assertIn("not chosen in the intake", joined)
        self.assertIn("a control that does nothing", joined)

    def test_one_language_but_a_switch_survives(self):
        # The specific failure references/applying-answers.md names.
        problems = judge(found(["en"], [CTRL_EN]), ["en"])
        self.assertEqual(len(problems), 1)
        self.assertIn("control that does nothing", problems[0])

    def test_both_directions_at_once(self):
        # Asked for en+zh-TW, built with en+ko: one missing, one surplus.
        problems = judge(found(["en", "ko"], [CTRL_EN, CTRL_KO]), ["en", "zh-TW"])
        self.assertEqual(len(problems), 2)
        self.assertTrue(any("zh-TW" in p and "nothing in the file" in p for p in problems))
        self.assertTrue(any("ko" in p and "not chosen" in p for p in problems))

    def test_case_and_region_differences_are_not_findings(self):
        self.assertEqual(judge(found(["en", "zh-tw"]), ["en", "zh-TW"]), [])

    def test_how_is_carried_into_the_message(self):
        ctrl = {"how": "observed", "lang": "ko", "label": "KO"}
        problems = judge(found(["en", "ko"], [CTRL_EN, ctrl]), ["en"])
        self.assertTrue(any("(observed)" in p for p in problems))

    def test_a_harness_error_suppresses_the_language_verdict(self):
        # A browser that never reported cannot be evidence that a language is
        # missing; saying so would be the worst kind of false finding.
        problems = judge(found([], errors=["HARNESS ERROR boom"]), ["en", "ko"])
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("HARNESS ERROR"))

    def test_a_plain_harness_message_is_labelled_as_one(self):
        problems = judge(found([], errors=["the target never became reachable"]),
                         ["en"])
        self.assertTrue(problems[0].startswith("HARNESS ERROR"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
