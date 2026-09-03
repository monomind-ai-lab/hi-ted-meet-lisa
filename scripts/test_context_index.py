#!/usr/bin/env python3
"""Tests for scripts/context_index.py — the registry index generator.

The real registries live in `project-context/`, which is untracked (`D-023`)
and so absent in CI, so everything here runs against inline fixtures written to
a temp dir and passed with `--context`. The fixtures carry both status forms the
registry actually uses: the `- Status:` list field of `D-001`-`D-029` and the
prose opening line of `D-030` onward.

The case that matters is a superseded decision in the prose form. Reading only
the list form reported those as `accepted` — a silent default that left `D-033`
and `D-050` in the index as live guidance while their own bodies said they had
been superseded.

    python3 scripts/test_context_index.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "context_index.py"

sys.path.insert(0, str(ROOT / "scripts"))
import context_index as ci  # noqa: E402

DECISIONS = """\
# Decision Registry

Statuses are `proposed`, `accepted`, or `superseded`.

## D-001: The older list form

- Status: `accepted`
- Date: 2026-01-01
- Decision: Something.

## D-002: The older list form, superseded

- Status: `superseded`
- Date: 2026-01-02
- Decision: Something else.

## D-003: The newer prose form

`accepted` · 2026-02-01

Body prose.

## D-004: The newer prose form, superseded with a reason

`superseded` · 2026-02-02 — **by `D-003` the same day, at Daren's call.** The
record below stands as history.

Body prose.

## D-005: The newer prose form, proposed

`proposed` · 2026-02-03

Body prose.
"""

LEARNINGS = """\
# Learning Registry

Preamble.

## L-001: A learning with a scope field

- Status: `accepted`
- Scope: Any file in this repository.
- Learning: Something.

## L-002: A newer learning that states no scope

Prose body, no scope field, and no status either.
"""


def write(context: pathlib.Path, decisions: str = DECISIONS,
          learnings: str = LEARNINGS) -> pathlib.Path:
    context.mkdir(parents=True, exist_ok=True)
    (context / "DECISIONS.md").write_text(decisions, encoding="utf-8")
    (context / "LEARNINGS.md").write_text(learnings, encoding="utf-8")
    return context


def run(context: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "--context", str(context), *args],
                          capture_output=True, text=True)


def rows(text: str) -> dict[str, str]:
    """The generated table as {id: status cell}."""
    out = {}
    for line in text.splitlines():
        if line.startswith("| [`"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            out[cells[0].split("`")[1]] = cells[-1]
    return out


class StatusForms(unittest.TestCase):
    """`status_of` reads both forms, and refuses to guess at anything else."""

    def test_list_form(self):
        self.assertEqual(ci.status_of("\n- Status: `accepted`\n- Date: x\n")[0], "accepted")
        self.assertEqual(ci.status_of("\n- Status: `superseded`\n- Date: x\n")[0], "superseded")

    def test_prose_form(self):
        self.assertEqual(ci.status_of("\n`accepted` · 2026-09-02\n\nBody.")[0], "accepted")
        self.assertEqual(ci.status_of("\n`proposed` · 2026-09-02\n\nBody.")[0], "proposed")

    def test_prose_form_carrying_a_reason_still_reads_as_superseded(self):
        # the shape of D-033 and D-050: status, date, then an em dash and why
        body = "\n`superseded` · 2026-09-03 — **by `D-051` the same day.**\n\nBody."
        self.assertEqual(ci.status_of(body)[0], "superseded")

    def test_prose_form_with_no_date(self):
        self.assertEqual(ci.status_of("\n`superseded`\n\nBody.")[0], "superseded")

    def test_no_status_is_empty_never_a_default(self):
        for body in ("\n\nJust a body.\n", "\n\n`scripts/thing.py` gains a flag.\n", "\n"):
            self.assertEqual(ci.status_of(body), ("", ""), body)

    def test_a_status_outside_the_vocabulary_is_not_passed_through(self):
        status, raw = ci.status_of("\n`maybe` · 2026-09-03\n")
        self.assertEqual(status, "")
        self.assertEqual(raw, "maybe")


class Index(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.context = write(pathlib.Path(self.tmp.name) / "project-context")

    def test_both_forms_reach_the_table(self):
        proc = run(self.context)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        cells = rows((self.context / "DECISIONS.md").read_text(encoding="utf-8"))
        self.assertEqual(cells, {
            "D-001": "`accepted`",
            "D-002": "`superseded`",
            "D-003": "`accepted`",
            "D-004": "`superseded`",   # prose form + reason — the reported bug
            "D-005": "`proposed`",
        })

    def test_learnings_show_scope_and_an_unstated_scope_is_a_blank(self):
        run(self.context)
        cells = rows((self.context / "LEARNINGS.md").read_text(encoding="utf-8"))
        self.assertEqual(cells["L-001"], "Any file in this repository.")
        self.assertEqual(cells["L-002"], "—")

    def test_check_is_green_once_generated_and_writes_nothing(self):
        self.assertEqual(run(self.context).returncode, 0)
        before = (self.context / "DECISIONS.md").read_bytes()
        proc = run(self.context, "--check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("current (5 entries)", proc.stdout)
        self.assertEqual(before, (self.context / "DECISIONS.md").read_bytes())

    def test_check_fails_when_a_status_changes_under_it(self):
        run(self.context)
        path = self.context / "DECISIONS.md"
        path.write_text(path.read_text(encoding="utf-8")
                        .replace("`accepted` · 2026-02-01", "`superseded` · 2026-02-01"),
                        encoding="utf-8")
        proc = run(self.context, "--check")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("STALE", proc.stdout)

    def test_regeneration_is_idempotent(self):
        run(self.context)
        first = (self.context / "DECISIONS.md").read_bytes()
        run(self.context)
        self.assertEqual(first, (self.context / "DECISIONS.md").read_bytes())


class UnreadableStatus(unittest.TestCase):
    """An unreadable status is loud in the table, on stderr, and in the exit code."""

    BROKEN = DECISIONS + """
## D-006: An entry with no status in either form

Straight into the body, no status anywhere.
"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.context = write(pathlib.Path(self.tmp.name) / "project-context",
                             decisions=self.BROKEN)

    def test_it_is_reported_and_fails_rather_than_defaulting_to_accepted(self):
        proc = run(self.context)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("UNREADABLE STATUS (1)", proc.stderr)
        self.assertIn("D-006", proc.stderr)
        self.assertNotIn("D-005", proc.stderr)

    def test_the_cell_says_so_and_never_reads_as_a_status(self):
        run(self.context)
        cells = rows((self.context / "DECISIONS.md").read_text(encoding="utf-8"))
        self.assertEqual(cells["D-006"], ci.UNREADABLE)
        self.assertNotIn("accepted", cells["D-006"])
        # the other entries are still generated — one bad entry does not hold
        # the registry hostage
        self.assertEqual(cells["D-004"], "`superseded`")

    def test_check_also_fails_even_when_the_index_is_current(self):
        run(self.context)
        proc = run(self.context, "--check")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("current (6 entries)", proc.stdout)
        self.assertIn("UNREADABLE STATUS", proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
