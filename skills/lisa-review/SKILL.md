---
name: lisa-review
description: "Use when a finished HTML deck, document, or page needs a design review — including phrases like /lisa-review, \"review the deck\", \"design review this HTML\", or \"polish the deck\". Runs the Hi Ted, Meet Lisa design pass on a file /lisa produced, or on any standalone HTML deck or page the user points at: picks the reviewer, runs the deck-specific checks, applies the fixes, and reports the findings."
---

# Hi Ted, Meet Lisa review

> Every path below — `references/`, `templates/`, `.agents/` — is relative to
> the **Hi Ted, Meet Lisa root**: the plugin's own directory when installed as
> a plugin (`${CLAUDE_PLUGIN_ROOT}` in Claude Code), or the repository checkout
> when you are reading this from source. Resolve them there, not against
> whatever project you happen to be working in.

The design pass, as its own command. `/lisa` used to run this inside every
build; the intake's `review` answer now schedules it, and the default —
`after` — delivers the draft first and leaves the pass to this skill. Run it
right after a build when the user asks, or weeks later against any standalone
HTML deck or page they point at.

Everything about **what** to check lives in `references/design-review.md`.
That file is the single source; this skill only decides when, and on what.

## Invocation

    /lisa-review [path/to/file.html]

No path? If this session just built a deck, that file is the target. Otherwise
look for the most recently generated deck in the working directory — and if
more than one candidate is plausible, ask rather than guess.

## Procedure

1. **Identify what you are reviewing.** Work out which template family the
   file comes from — the design tokens and chrome give it away, and
   `templates/templates.json` names them all. It changes what correct means:
   the MonoMind deck machine-translates and needs its protection list checked;
   the web document writes both languages inline and needs none of that. A
   file that is not from a Lisa template at all still gets the pass — judge it
   against its own system, not against ours.
2. **Run the review** exactly as `references/design-review.md` specifies:
   reviewer selection first — the user's own Impeccable, then the bundled copy
   at `.agents/skills/impeccable/`, then the checklist floor — followed by the
   deck-specific checks. Say which reviewer ran; never imply a full review
   when only the floor happened.
3. **Apply the fix-now findings.** Never rewrite the template's design tokens
   or load-bearing scripts — the same rule `/lisa` builds under. A finding
   against the shipped system is reported, not silently applied.
4. **Re-run the responsive check** after the fixes. Layout fixes are exactly
   what regress it.
5. **Report** the findings grouped as the reference specifies — fix now, worth
   considering, left alone — with a reason for anything in the third group.

## In a sandbox

A hosted chat sandbox has no browser, and most of the review needs one: the
responsive check, measured contrast, translated output. Run the static checks,
then say plainly which ones you skipped and how the user runs them — serve the
file over http, look for console errors and horizontal overflow at 375px — the
same convention as `/lisa`'s own verification step. Never call a deck reviewed
on the strength of the checks that happened to be possible.
