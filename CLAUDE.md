# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the source repository for **`lisa`**, a Claude Code Skill
(invoked as `/lisa`) that generates a MonoMind-branded slide deck,
web document, or diagram set as **one standalone HTML file** — no build step, no bundler, no
package manager, no test suite. The only runtime dependencies are Python's
stdlib (for the helper scripts) and, for thumbnail capture, a local Chrome
binary. Do not look for `npm`/`pip` build or lint commands — there are none.

The full skill protocol lives in [`skills/lisa/SKILL.md`](skills/lisa/SKILL.md)
— read it before making
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

# Regenerate the intake panel's file:// fallback template list from the
# registry. Run after any change to templates/templates.json; --check fails
# when the two have drifted apart.
python3 scripts/tedandlisa_intake_fallback.py [--check]

# Build the per-skill upload bundles for the Claude and ChatGPT settings
# panels (Claude Code and Codex install the plugin instead, and need none
# of this). Writes dist/<skill>.zip; --check validates without writing.
python3 scripts/build_skill_zips.py [--check]
```

There is no automated test suite. Verification is manual and browser-based —
see the checklists in `skills/lisa/SKILL.md` and
`skills/lisa-new-template/SKILL.md`
(open the output `file://` or over `http://`, exercise navigation/menu/language
switch, check for console errors and horizontal overflow at 375px).

## Architecture

**Independent template systems, not variations of one look.** The registry
carries eight first-party templates (plus the external `slide-design` entry
that hands off to `/lisa-design`). Each is a single self-contained HTML file
with its own design tokens, chrome, scripts, and language mechanism — they
differ in shape, navigation, and how they translate, so a change to one has no
bearing on the others. Three of them show how far apart the systems sit:

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

**The public website is a separate repository.** The landing page, the live
preview decks and the Cloudflare Pages deploy live in
[`monomind-ai-lab/ted-and-lisa`](https://github.com/monomind-ai-lab/ted-and-lisa);
that build checks this repository out and reads `templates/templates.json`,
`templates/thumbs/`, `assets/tedandlisa-intake.html` and
`assets/monomind-mark-white.svg` from it, so those four are load-bearing for
the site and must keep their paths. Nothing here builds or deploys the site.
The registry's `preview` and `thumb_source` values still name the previews by
their canonical `previews/<id>.html` path — the path the website builds from —
and the two scripts that consume them resolve that to
`https://html.monomind.one/previews/<id>.html` instead: the intake runner
rewrites each card's `preview` to the hosted URL (so the gallery's "Preview"
links open over the network, in a new tab rather than the framing overlay), and
`tedandlisa_thumbs.py` screenshots the hosted page when the local file is
absent. Both paths that used to be local now need a connection.

**The generation flow spans several files by design:** `SKILL.md` drives the
process → `scripts/tedandlisa_intake.py` serves `assets/tedandlisa-intake.html`
and captures its answers as JSON per `references/intake-contract.md` → the
skill resolves `answers.template` through `templates/templates.json` → copies
that template file (never authors from blank) → fills placeholders using the
matching pattern-reference doc → applies the intake answers: the mechanical
rows (theme/backgrounds/menu/export/accent/…) by running
`scripts/tedandlisa_apply.py`, the judgment rows by hand — the answers table
in `references/applying-answers.md` is the authority for both → the design
review runs when the intake's `review` answer scheduled it (see below).

**Templates fence what may be edited.** Every first-party template wraps its
authorable regions in `LISA:CONTENT-START` / `LISA:CONTENT-END` comment pairs
and opens with a `LISA:CONTENT-MAP` header naming those regions plus the few
out-of-fence edit points (`<title>`, nav labels, script arrays). Agents `cp`
the template file and edit only the fenced regions — everything outside is
load-bearing chrome and embedded artwork, never to be retyped.

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
`skills/lisa-new-template/` (`/lisa-new-template`), which
turns a finished HTML file into a placeholder skeleton + pattern-reference doc
and registers it. Its cardinal rule: the *source* document is someone's real
work and must never be committed — only the genericized skeleton, scrubbed of
every identifying detail, is.

**Brand extraction** is the sibling skill `skills/lisa-brand/` (`/lisa-brand`):
it reads a brand off a site URL, a screenshot, or assets into
`brand/design.md` — tokens on the schema the templates share, each value
marked `fact` or `approx` with its source — plus a one-page A4 brand book
built from `assets/lisa-brand-book-a4.html`. `references/brand-extraction.md`
is the contract (the `design.md` shape, the extraction heuristics, SVG
sanitisation, the contrast rule, and the per-template token mapping). The
intake's `style: brand` answer runs the same extraction inside a `/lisa` build
and then applies the result exactly like `style: designmd`. Both files go into
the user's working directory, never into this checkout.

**Design review** (`references/design-review.md`) is scheduled by the
intake's `review` answer — default `after`: deliver the file first, then run
`/lisa-review` when the user says yes; `inline` runs the pass before handover,
`none` runs only the floor checks. Whichever way it runs, the pass
prefers the user's own Impeccable install, falls back to the copy vendored
unmodified at `.agents/skills/impeccable/` (see its `VENDORED.md`), and has a
tooling-free checklist as the floor.

## Project context system

This repo uses a local `project-context/` protocol (imported into `AGENTS.md`
and wired via `.claude/settings.json` `SessionStart`/`Stop` hooks calling
`.agents/skills/project-context/scripts/context_triggers.py`). The registry
itself lives beside the checkout and is untracked; `project-context` in the
working tree is a gitignored symlink to it, so a fresh clone will not have
it — the protocol applies to local sessions on this machine. Before
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
