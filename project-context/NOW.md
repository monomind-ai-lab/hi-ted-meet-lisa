# Current Project State

Last reviewed: 2026-08-29

## Snapshot

| Area | Current state | Evidence |
| --- | --- | --- |
| Skill | `/tedandlisa` runs end to end: intake, template, content, answer application, design review, hand-off. Every intake answer now changes the generated file. | [`../SKILL.md`](../SKILL.md) |
| Templates | Six registered: `monomind-deck` (horizontal slides, Google Translate on demand), `web-document` (hash-routed pages, inline bilingual, mermaid), `mermaid-master` (diagram-first on light paper, inline SVG), `architecture` (one system diagram on slate, semantic colour), `sitemap-ia` (pages arguing a site structure, plus a clickable navigation prototype at two breakpoints), `project-website` (a project's public face: sticky nav, eight hash-routed pages behind five inline links and a More dropdown, one shared footer, Google Fonts only). A seventh registry entry, `slide-design`, is a handoff rather than a template — see `D-013`. | [`../templates/templates.json`](../templates/templates.json) |
| Fifth path | `/tedandlisa-design` wraps the vendored Slides AI pipeline for decks the templates cannot shape — style presets and animated HTML only, since `D-020` retired the `.pptx` output everywhere. It is offered as option five in the intake gallery and reached through the payload's `handoff` field. | [`../skills/tedandlisa-design/SKILL.md`](../skills/tedandlisa-design/SKILL.md) |
| Intake | Gallery of seven options first, then questions filtered by the chosen option's kind and, since `D-017`, by template id — seven for the handoff, nine for a document, sixteen for `sitemap-ia`, eleven for a deck. The prompt is editable, references can be attached, and previews open in an overlay that cannot discard a half-answered form (`D-014`). | [`../assets/tedandlisa-intake.html`](../assets/tedandlisa-intake.html), [`../references/intake-contract.md`](../references/intake-contract.md) |
| Previews | Six of the seven gallery options have a live preview, each the real thing rather than a placeholder: the shipped Project Context guide for `monomind-deck`, a normalised architecture document for `web-document`, proyecto26's onboarding deck rebranded for `slide-design`, and three written about Hi Ted, Meet Lisa itself — the newest being `project-website`, which is the project's own site in English and Korean across eight pages. Every one is self-contained apart from Google Fonts. | [`../previews/`](../previews), [`../templates/templates.json`](../templates/templates.json) |
| Design review | Prefers the user's own Impeccable, falls back to the bundled copy, then a tooling-free floor. | [`../references/design-review.md`](../references/design-review.md) |
| Narrow screens | `web-document` and its preview carry a `max-width:640px` nav block: below 640px the mark falls back to its logo and the utilbar to its icons, so the burger and the language pair stay on screen. Measured at 375px — a 590px nav row before, 375px after (`L-016`). | [`../assets/tedandlisa-template-web-document.html`](../assets/tedandlisa-template-web-document.html) |
| Nav width budget | `project-website` states its nav budget in the stylesheet: the row is capped at 1120px on every viewport, the default configuration spends ~1040, and the remaining ~80px is what a longer project name and longer labels consume. Labels are `white-space:nowrap` so an over-full row fails visibly instead of wrapping, and the utilbar's word labels are off by default because they cost 56px. Measured at 1280px with the preview's real labels: 1045 used, 75 spare (`L-024`). | [`../assets/tedandlisa-template-project-website.html`](../assets/tedandlisa-template-project-website.html) |
| Public face | `README.md` opens with **Start here** — the copy-paste prompt and what a reader gets — then the five ways to make a deck (`D-016`). The intake panel is shown rather than only described, using a captured screenshot of the real panel with its template gallery. | [`../README.md`](../README.md), [`../assets/tedandlisa-intake-panel.jpg`](../assets/tedandlisa-intake-panel.jpg) |
| Project context | Trigger-driven on scaffold `0.3.0`; doctor reports healthy. | [`SKILL.md`](SKILL.md), [`../.claude/settings.json`](../.claude/settings.json) |

## Active work

| Initiative | Status | Next action | Evidence |
| --- | --- | --- | --- |
| Public site for `html.monomind.one` | `in-progress` | `site/` holds a dark-cinematic landing page (visual language from the Canva brand deck: blurred-poppy atmosphere, white frame device, cream ink) with hero, a three-path chooser for new users (try once / install / both, tabbed with hash deep-links), the seven-card gallery of real previews, and a closing Ted-and-Lisa scene. The intake panel gained a **web mode** (`CTX.mode === "web"`, injected only by `site/sync.sh`): the end state reads "Prompt is ready.", the payload is one complete paste-ready prompt (preamble + answers), and the copy names the agents it works with — runner and `file://` behaviour untouched. Figure art: `assets/ted-figure.png` / `lisa-figure.png` are grayscale luminance figures extracted from the Canva SVG export; the `-cream` variants are pre-tinted RGBA renders the site uses. `site/sync.sh` assembles the deployable folder from canonical artifacts at deploy time; copies are gitignored. The page carries a searchable language dropdown (English default; Korean and Traditional Chinese preferred; ~40 more) driven by the same cookie-based Google Translate machinery as the deck template, with the same term-protection pass. The topbar mark is a deploy-derived solid-white copy of the currentColor SVG, and both the mark and the footer's "MonoMind AI Lab" link to monomind.one. The gallery ends in a "Your Template" card (more on the way + install to add your own), and the medium section is figure-free with a `deck.html` spec card. `README.md` now opens with the website as the no-terminal path. Verified over `http://` end to end, including Korean translation with protected terms. Deployed with wrangler to the `hi-ted-meet-lisa` Pages project (direct upload, not git-connected — run `bash site/sync.sh && wrangler pages deploy site --project-name hi-ted-meet-lisa` to ship; live at hi-ted-meet-lisa.pages.dev). The custom domain html.monomind.one is attached to the project but `pending`: wrangler's OAuth offers no DNS scope, so the `html` → `hi-ted-meet-lisa.pages.dev` proxied CNAME in the monomind.one zone must be added in the dashboard, after which it activates on its own. Next: release zips for the claude.ai path, which the page marks "coming soon". | [`../site/index.html`](../site/index.html), [`../site/sync.sh`](../site/sync.sh), [`../assets/tedandlisa-intake.html`](../assets/tedandlisa-intake.html) |
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

- An agent that skips the intake panel has to read `templates.json` to learn
  that `slide-design` exists at all. The gallery and `README.md` both show it;
  nothing else does.
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
- `project-website`'s dark `--fg-faint` is 2.86:1 and carries four selectors of 11–13px text. Kept on
  purpose with the fix written next to it (`D-019`); the design-review step should expect to raise it on
  every site generated from this template until someone acts on the comment.
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
