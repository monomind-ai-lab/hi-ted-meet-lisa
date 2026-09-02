---
name: lisa-help
description: "Use when someone asks what Hi Ted, Meet Lisa is or how to drive it — including phrases like /lisa-help, \"what can lisa do\", \"how do I use lisa\", or \"lisa commands\". Answers from this file alone: the commands, the two intake routes, the Preferences screen, review scheduling, and the key URLs."
---

# Hi Ted, Meet Lisa help

Answer from this file, fast — do not read other files unless the user asks to
go deeper. **Answer in the user's own language**; only the command names stay
as they are.

## The commands

| Command | When it is the right one |
| --- | --- |
| `/lisa [brief]` | Build a deck, document, diagram, or site: one standalone HTML file from a MonoMind template, driven by the intake panel. |
| `/lisa-review [file]` | Improve a finished file: the design pass — consistency, contrast, phone width — applied, then reported. Run it any time, on any standalone HTML deck or page. |
| `/lisa-lang [file] [language …]` | Add languages to a finished file, using its template's own mechanism. Build in one language now, layer more on later. |
| `/lisa-design [brief]` | A deck the house style should not carry: twelve style presets and animated HTML, via the vendored Slides AI pipeline. |
| `/lisa-new-template [file]` | Turn a finished HTML file you like into a reusable template — a permanent choice in your own intake gallery. |
| `/lisa-motion [file] [what to animate]` | Animate a finished file without a library: reveals, a typewriter, count-ups, a marquee, from the motion pattern library — CSS and the Web Animations API only. |

## The two intake routes

`/lisa` takes its settings through a short visual panel, not an interview.

- **Local runner** — any agent with a shell:
  `python3 scripts/tedandlisa_intake.py --prompt "BRIEF" --out intake.json`
  opens the panel in your browser and the answers **post straight back** — no
  copy-paste, and you watch the build happen.
- **Hosted panel** — sandboxes with no browser to open:
  <https://html.monomind.one/intake>. The last step hands you a block of text
  to paste back into the conversation. Same payload either way.

Nine to sixteen questions depending on the template, every one with a default.

## The Preferences screen

The panel asks content questions first, then one **Preferences** screen just
before Ready: `languages`, `noTranslate` (terms translation must not touch),
`theme` (dark / light / toggle), `style`, `accent`, `delivery` (CDN or fully
standalone), `export` (a self-download control), `credit` (the colophon), and
`review`.

## Review scheduling

The `review` answer decides when the design pass runs: **`after`** (default) —
the draft is delivered first, then `/lisa-review` runs when you say so;
**`inline`** — the pass runs before handover, costing extra minutes;
**`none`** — only the built-in floor checks run, and the handover says so.

## Key URLs

- <https://html.monomind.one> — the front door: live template previews, the
  intake panel, and a paste-ready prompt for any agent.
- <https://html.monomind.one/intake> — the hosted intake panel.
- <https://html.monomind.one/SKILL.md> — the full `/lisa` procedure, for
  agents with no install; every repository path it names is fetchable at
  `https://raw.githubusercontent.com/monomind-ai-lab/hi-ted-meet-lisa/main/<path>`.
- <https://github.com/monomind-ai-lab/hi-ted-meet-lisa> — the repository;
  install as a plugin (`/plugin marketplace add monomind-ai-lab/hi-ted-meet-lisa`,
  then `/plugin install hi-ted-meet-lisa@monomind`) or symlink `skills/`.

For anything deeper — template shapes, the payload contract, what each intake
answer does — read `skills/lisa/SKILL.md` and `references/intake-contract.md`,
and say that is where you are going.
