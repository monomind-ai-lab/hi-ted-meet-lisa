# Current Project State

Last reviewed: 2026-08-29

## Snapshot

| Area | Current state | Evidence |
| --- | --- | --- |
| Skill | `/tedandlisa` runs end to end: intake, template, content, answer application, design review, hand-off. Every intake answer now changes the generated file. | [`../SKILL.md`](../SKILL.md) |
| Templates | Five registered: `monomind-deck` (horizontal slides, Google Translate on demand), `web-document` (hash-routed pages, inline bilingual, mermaid), `mermaid-master` (diagram-first on light paper, inline SVG), `architecture` (one system diagram on slate, semantic colour), `sitemap-ia` (pages arguing a site structure, plus a clickable navigation prototype at two breakpoints). A sixth registry entry, `slide-design`, is a handoff rather than a template — see `D-013`. | [`../templates/templates.json`](../templates/templates.json) |
| Fifth path | `/tedandlisa-design` wraps the vendored Slides AI pipeline for decks the templates cannot shape, and for editable `.pptx`. It is offered as option five in the intake gallery and reached through the payload's `handoff` field. | [`../skills/tedandlisa-design/SKILL.md`](../skills/tedandlisa-design/SKILL.md) |
| Intake | Gallery of six options first, then questions filtered by the chosen option's kind and, since `D-017`, by template id — seven for the handoff, nine for a document, sixteen for `sitemap-ia`, eleven for a deck. The prompt is editable, references can be attached, and previews open in an overlay that cannot discard a half-answered form (`D-014`). | [`../assets/tedandlisa-intake.html`](../assets/tedandlisa-intake.html), [`../references/intake-contract.md`](../references/intake-contract.md) |
| Previews | All five options have a live preview, each the real thing rather than a placeholder: the shipped Project Context guide for `monomind-deck`, a normalised architecture document for `web-document`, proyecto26's onboarding deck rebranded for `slide-design`, and two written about Hi Ted, Meet Lisa itself. Every one is self-contained apart from Google Fonts. | [`../previews/`](../previews) |
| Design review | Prefers the user's own Impeccable, falls back to the bundled copy, then a tooling-free floor. | [`../references/design-review.md`](../references/design-review.md) |
| Narrow screens | `web-document` and its preview carry a `max-width:640px` nav block: below 640px the mark falls back to its logo and the utilbar to its icons, so the burger and the language pair stay on screen. Measured at 375px — a 590px nav row before, 375px after (`L-016`). | [`../assets/tedandlisa-template-web-document.html`](../assets/tedandlisa-template-web-document.html) |
| Public face | `README.md` opens with **Start here** — the copy-paste prompt and what a reader gets — then the five ways to make a deck (`D-016`). The intake panel is shown rather than only described, using a captured screenshot of the real panel with its template gallery. | [`../README.md`](../README.md), [`../assets/tedandlisa-intake-panel.jpg`](../assets/tedandlisa-intake-panel.jpg) |
| Project context | Trigger-driven on scaffold `0.3.0`; doctor reports healthy. | [`SKILL.md`](SKILL.md), [`../.claude/settings.json`](../.claude/settings.json) |

## Active work

| Initiative | Status | Next action | Evidence |
| --- | --- | --- | --- |
| `sitemap-ia` verified only on CDNs | `in-progress` | The skeleton and its preview were checked over `http://` — five pages, three diagrams, both language directions, the prototype at both breakpoints, no console errors, no horizontal overflow at 375px. The `delivery: standalone` path is documented but has never been run *from the template*; it was only proven on the source document it was extracted from. | [`../assets/tedandlisa-template-sitemap-ia.html`](../assets/tedandlisa-template-sitemap-ia.html), `D-018` |
| Client product name in public git history | `blocked` | A client product name was scrubbed from the working tree in `437b628`, but earlier commits still contain it in a public repository. Removing it needs a history rewrite and a force-push — the user's call, not an agent's. | `437b628`, `b859a4c` |
| Phone layout on a real device | `not-started` | Open the deck on a physical phone. The browser pane cannot answer this; see `L-003`. | [`LEARNINGS.md`](LEARNINGS.md) |
| Design review applied to a finished deck | `in-progress` | The step 10 review ran end to end for the first time, against a generated `web-document` deck, using the user's own Impeccable plus the measured floor. It found one template defect (`L-016`) and one shipped-system contrast failure, and two of its three automated findings were harness artefacts (`L-017`). Still never run against a finished `monomind-deck`. | [`../references/design-review.md`](../references/design-review.md), [`LEARNINGS.md`](LEARNINGS.md) |

## Blockers

- Nothing is blocking new work. The seven open questions carried from the old
  hand-off are all answered: the skill lives in its own public repository,
  invocation is prompt-driven, light theme ships, the missing components were
  added, the default language pair is English and Korean, the logo is applied
  and swappable, and "Project Context" is a name that must not translate.

## Known follow-up

- `sitemap-ia` ships English and Traditional Chinese inline, while the other
  inline-bilingual templates default to English and Korean (`D-010`). The pair
  is coupled across the same five places `L-018` lists, plus the prototype's own
  `nl` table, which is a sixth.
- The `sitemap-ia` prototype's seven section keys (`s1`…`s7`) appear in four
  places across two payload scripts. The pattern reference lists them, but
  nothing enforces agreement, and a mismatch fails the way `L-019` describes —
  silently, with the markup intact.

- The gallery's five cards are the only surface where the handoff path is
  visible. An agent that skips the panel has to read `templates.json` to learn
  that `slide-design` exists at all.
- `vendor/slides-ai-plugin` is pinned at `1f8505f`. A clone needs
  `git submodule update --init --recursive` before `/tedandlisa-design`
  works; the wrapper says so, but nothing enforces it.
- PPTX generation needs `bun`. It is present on this machine and unverified
  anywhere else.
- The `web-document` preview is English and Chinese, because that is what its
  source document contains, while the templates default to English and Korean.
  Converting it would be a translation project, not a template change.
- `references/reference-deck.html` is a verbatim copy of the shipped guide. It
  is a reference, not a template, and drifts as the guide changes.
- Thumbnail capture needs a local Chrome. Without one the gallery falls back to
  text cards, which is a degradation nobody has looked at.
- `footer .mono` measures 3.34:1 on the dark ground, below AA for its 13px size.
  The template already repairs this exact selector for the light theme and not
  for the dark one, so the omission looks accidental rather than intended.
- The `web-document` language pair is coupled across five places, one of them a
  routing regex that fails silently on deep links (`L-018`). Nothing in the
  template or its pattern reference lists them together.
- `previews/web-document.html` pushes its language toggle 43px off the right
  edge at 1280px, a common laptop width. `.nav .links` is `flex:1` with the
  default `min-width:auto`, so a long link row cannot shrink and displaces the
  fixed controls instead. The template itself is clean at 1280 with four links,
  but the preview has thirteen, and any generated document with roughly eight or
  more pages would hit the same wall. The obvious repairs conflict: `min-width:0`
  lets the row spill over the controls because the nav is `overflow:visible`, and
  switching to `overflow-x:auto` would clip the Documents dropdown, which is why
  `overflow:visible` is there. Needs a design call, not a one-liner.

## Superseded state

- `HANDOFF.md` was the pre-pipeline hand-off; its durable content lives in this
  directory and it was removed from the working tree. Readable at `fbe8cec`.
- The second template was `techdoc` before `D-004` renamed it `web-document`.
- Both inline-bilingual templates were English and Chinese before `D-010` made
  English and Korean the default pair.
