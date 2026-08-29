# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the source repository for **`tedandlisa`**, a Claude Code Skill
(invoked as `/tedandlisa`) that generates a MonoMind-branded slide deck,
web document, or diagram set as **one standalone HTML file** — no build step, no bundler, no
package manager, no test suite. The only runtime dependencies are Python's
stdlib (for the two helper scripts) and, for thumbnail capture, a local Chrome
binary. Do not look for `npm`/`pip` build or lint commands — there are none.

The full skill protocol lives in [`SKILL.md`](SKILL.md) — read it before making
any change to the skill's behavior. This file only orients you to the codebase
shape and the commands you'll actually run.

## Commands

```sh
# Run the intake panel that collects deck settings (opens a browser, POSTs
# back to /intake, writes the answers to --out). Stdlib only.
python3 scripts/tedandlisa_intake.py --prompt "the deck brief" --out intake.json

# Read-only structural report on a finished HTML doc (tokens, classes, script
# blocks, external deps, i18n mechanism) — used when turning it into a template.
python3 scripts/tedandlisa_new_template.py analyze SOURCE.html

# Register a new template skeleton (create-only; refuses to overwrite an id).
python3 scripts/tedandlisa_new_template.py register --id ID --name "NAME" \
  --file assets/tedandlisa-template-ID.html --kind slides|document

# Re-capture gallery thumbnails after adding/changing a template's opening
# screen. Needs a local Chrome/Chromium; degrades to a text card if absent.
python3 scripts/tedandlisa_thumbs.py [--only ID]
```

There is no automated test suite. Verification is manual and browser-based —
see the checklists in `SKILL.md` and `skills/tedandlisa-new-template/SKILL.md`
(open the output `file://` or over `http://`, exercise navigation/menu/language
switch, check for console errors and horizontal overflow at 375px).

## Architecture

**Three independent template systems, not variations of one look.** Each is a
single self-contained HTML file with its own design tokens, chrome, scripts,
and language mechanism — they differ in shape, navigation, and how they
translate, so a change to one has no bearing on the other:

- `assets/tedandlisa-template.html` (`monomind-deck`) — horizontal
  scroll-snap slides; on-demand Google Translate driven by a
  `.notranslate`/known-terms list baked into its script.
- `assets/tedandlisa-template-web-document.html` (`web-document`) —
  hash-routed pages (`#/lang/page`) that each scroll; both languages are
  written inline as dual-language spans and toggled by `body[data-lang]`, no
  translation service, but mermaid diagrams load from a CDN so it isn't fully
  offline.
- `assets/tedandlisa-template-mermaid-master.html` (`mermaid-master`) —
  diagram-first slides on light paper (`--paper`/`--ink`/one orange accent),
  hash-routed as `#lang/route` with a visual index; diagrams are already-
  rendered inline SVG, so there is no mermaid runtime and no CDN. Every slide
  exists twice (`s-en-NN` / `s-zh-NN`) so text inside a diagram translates too,
  which means `ROUTES`, `TITLES`, and the sections must stay in agreement.

`templates/templates.json` is the registry both the intake panel and
`tedandlisa_new_template.py register` read/write; each entry points at its file,
its pattern-reference doc (`references/slide-patterns*.md` — verbatim,
known-good markup for every component), and its thumbnail in
`templates/thumbs/`.

**The generation flow spans several files by design:** `SKILL.md` drives the
process → `scripts/tedandlisa_intake.py` serves `assets/tedandlisa-intake.html`
and captures its answers as JSON per `references/intake-contract.md` → the
skill resolves `answers.template` through `templates/templates.json` → copies
that template file (never authors from blank) → fills placeholders using the
matching pattern-reference doc → applies every intake answer as a chrome edit
(theme/backgrounds/logo/menu/export — see the answers table in `SKILL.md`) →
runs the design-review pass (`references/design-review.md`).

**Load-bearing machinery must not be rewritten**, only extended: script block 1
in the MonoMind deck template, and the hash router + diagram viewer in the
web-document template. Add new script blocks and reuse `window.__deckGo(i)`
for navigation rather than writing new scroll/nav code.

**Translation safety is a first-class concern in `monomind-deck` only**:
anything that is code, a path, a filename, a command, a product name, or an
identity term must be wrapped `<span class="notranslate" translate="no">` or
added to the known-terms list in the language-switch script, or Google
Translate mangles it (real prior failures: "MonoMind AI Lab" → 人工智慧實驗室,
"MIT" → 麻省理工學院). The web-document template needs none of this — nothing
in it is machine-translated.

**Adding a template** goes through the sibling skill
`skills/tedandlisa-new-template/` (`/tedandlisa-new-template`), which
turns a finished HTML file into a placeholder skeleton + pattern-reference doc
and registers it. Its cardinal rule: the *source* document is someone's real
work and must never be committed — only the genericized skeleton, scrubbed of
every identifying detail, is.

**Design review** (`references/design-review.md`, run as the skill's step 10)
prefers the user's own Impeccable install, falls back to the copy vendored
unmodified at `.agents/skills/impeccable/` (see its `VENDORED.md`), and has a
tooling-free checklist as the floor.

## Project context system

This repo uses a local `project-context/` protocol (imported into `AGENTS.md`
and wired via `.claude/settings.json` `SessionStart`/`Stop` hooks calling
`.agents/skills/project-context/scripts/context_triggers.py`). Before
substantial work, read `project-context/SKILL.md` and `project-context/NOW.md`,
and search `project-context/DECISIONS.md` and `project-context/LEARNINGS.md`
for relevant constraints/evidence. Update `NOW.md`/`DECISIONS.md`/`LEARNINGS.md`
as their documented triggers fire (as work lands, not on request), and run
`/session-end` before handing off. Treat generated indexes/wikis as auxiliary,
not authority — confirm important claims against the repo's primary artifacts.

<!-- project-context:start -->
## Project Context

Before substantial repository work, read `project-context/SKILL.md` and
`project-context/NOW.md`, then search `project-context/DECISIONS.md` and
`project-context/LEARNINGS.md` for relevant constraints and evidence.

Update project context when a trigger defined in `project-context/SKILL.md`
fires, as work lands, rather than when an update is requested: `NOW.md` when the
state a next contributor would act on changed, `DECISIONS.md` when a choice
constrains future work, `LEARNINGS.md` when verified evidence changed what is
believed and will recur. Run `/session-end` before handing off to another agent,
session, or person. A new session reports when the upstream scaffold has a newer
release; upgrading still needs the user's go-ahead. Confirm important claims
against the repository's primary
artifacts and evidence. Treat generated indexes and wikis as auxiliary views,
not authority.
<!-- project-context:end -->
