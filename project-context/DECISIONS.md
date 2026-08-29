# Decision Registry

Statuses are `proposed`, `accepted`, or `superseded`. Only accepted decisions
define current direction. Use stable IDs such as `D-001` and link detailed
records from `decisions/` when the evidence or trade-offs need more space.

## D-001: One self-contained HTML file per deck

- Status: `accepted`
- Date: 2026-08-27
- Decision: A generated deck is a single HTML file. The only external calls are Google Fonts, and Google Translate — the latter loaded only when a reader selects a non-English language.
- Rationale: A deck must open from a file, a static host, or an email attachment with no build step, and an English reader should load no third-party script at all.
- Consequences: Assets are embedded, which makes files large (the reference template is 179 KB with two photographs). Any new dependency has to justify breaking this.
- Evidence: [`../assets/tedandlisa-template.html`](../assets/tedandlisa-template.html), `HANDOFF.md` (`fbe8cec`)

## D-002: Never rewrite the deck navigation script block

- Status: `accepted`
- Date: 2026-08-27
- Decision: Script block 1 of `monomind-deck` is carried verbatim into every deck built from that template. Other behaviour goes in its own block.
- Rationale: It encodes five rules learned from getting iframe scrolling wrong — detect the real scroller, listen for scroll and keydown on both `window` and `document` in the capture phase, auto-focus body, and never call `scrollIntoView` because it yanks the host page.
- Consequences: The copy button and the deck menu live in separate blocks and reuse `go(i)` through `window.__deckGo` instead of reimplementing scrolling.
- Evidence: [`../assets/tedandlisa-template.html`](../assets/tedandlisa-template.html), `HANDOFF.md` (`fbe8cec`)

## D-003: Skills are agent-neutral under `.agents/skills/`

- Status: `accepted`
- Date: 2026-08-27
- Decision: Skills are authored once under `.agents/skills/` using the Agent Skills convention — `SKILL.md` plus `scripts/`, `references/`, `assets/`. Harness-specific locations hold pointers, not copies.
- Rationale: The deck skill and this pipeline are both meant to work for any agent. A second full copy under `.claude/skills/` would drift.
- Consequences: Claude Code reaches `/session-end` through a one-line pointer at `.claude/skills/session-end/SKILL.md`; Codex reads the managed block in `AGENTS.md`.
- Evidence: [`../AGENTS.md`](../AGENTS.md), [`../.claude/skills/session-end/SKILL.md`](../.claude/skills/session-end/SKILL.md)

## D-004: Templates are named for how they read, not for their subject

- Status: `accepted`
- Date: 2026-08-27
- Decision: The second template is `web-document`, not `techdoc`. Template ids describe the reading mode — slides read across a room, a document read at desk distance.
- Rationale: `techdoc` implied a subject matter. The template suits an overview, a guide, decision records, or a handbook equally.
- Consequences: The rename spans the template file, its patterns reference, its thumbnail, and the registry. Landed in `fbe8cec`.
- Evidence: [`../templates/templates.json`](../templates/templates.json)

## D-005: Project context is updated by trigger, not on request

- Status: `accepted`
- Date: 2026-08-27
- Decision: Each context document defines the observable events that require it to be updated, and a harness check reports when a trigger window is open. Agents evaluate the triggers as work lands rather than waiting to be asked.
- Rationale: The previous instruction was to update "at meaningful milestones and handoffs". Nothing defined a milestone, so nothing ever fired: this repository reached three commits of real work with all three documents still at their installed template values.
- Consequences: `SKILL.md` carries the trigger table; `scripts/context_triggers.py` detects the window; `.claude/settings.json` wires it to `SessionStart` and `Stop`. The gate blocks once per session at most, so a session can always end. Detection is deliberately conservative — it reports that work landed, and never decides on its own that a decision or a learning fired.
- Consequences: This is a repository-local customization layered on scaffold `0.3.0`, not a new scaffold version. The local `template_version` stays `0.3.0` so the upstream release check stays meaningful. See `D-006`.
- Evidence: [`SKILL.md`](SKILL.md), [`../.claude/settings.json`](../.claude/settings.json), [`LEARNINGS.md`](LEARNINGS.md)

## D-006: Project Context flows one way into this repository

- Status: `accepted`
- Date: 2026-08-27
- Decision: This repository consumes the Project Context scaffold and never writes back to `monomind-ai-lab/project-context`. Local changes to the vendored skill stay local; the scaffold's version numbers, releases, and canonical templates are owned upstream.
- Rationale: `/tedandlisa` is a project that uses Project Context, not a source of it. Letting a consumer push its local variations upstream would make the scaffold's version mean different things in different repositories.
- Consequences: A local `template_version` is never bumped to claim an unreleased scaffold version. Instead, a new session checks the upstream releases feed once a day and reports when a newer release exists, and adopting it is a deliberate, user-approved `project-context-init` upgrade. Where the local customization and a future upstream release overlap, upstream wins and the local layer is retired.
- Evidence: [`SKILL.md`](SKILL.md), <https://github.com/monomind-ai-lab/project-context/releases/tag/v0.3.0>

## D-007: One template per shape, not one template with switches

- Status: `accepted`
- Date: 2026-08-28
- Decision: Each reading shape is its own template with its own tokens, chrome, navigation, and language mechanism. There are four; a fifth shape means a fifth template, never a new switch on an existing one.
- Rationale: A deck read across a room and a document read at desk distance want different navigation, type scales, and language handling. Every switch multiplies the states that have to be reviewed, and the shapes share no navigation to begin with.
- Consequences: Templates duplicate structure by design and a fix in one has no bearing on another. The intake asks the template question first and filters every later question by the chosen template's `kind`, so a document is never asked about slide count or cover artwork — and those keys are absent from the payload rather than defaulted.
- Evidence: [`../SKILL.md`](../SKILL.md), [`../templates/templates.json`](../templates/templates.json), [`../references/intake-contract.md`](../references/intake-contract.md)

## D-008: Third-party work is carried by the lightest mechanism that preserves attribution

- Status: `accepted`
- Date: 2026-08-28
- Decision: Three mechanisms, chosen by what the dependency has to do. Impeccable is **copied** into `.agents/skills/impeccable/` because the design review must work for anyone who clones the repository. Slides AI Plugin is a **submodule** at `vendor/slides-ai-plugin/` because it is executable tooling that should stay upstream. Cocoon AI's architecture generator is **derived** — its visual system rewritten as a MonoMind template, not vendored.
- Rationale: Copying executable tooling forks it silently; referencing a design reviewer by submodule would break the "works without a separate install" promise.
- Consequences: Every mechanism carries its own attribution burden and all three are recorded in `NOTICE`. Apache 2.0 requires the licence, notices, and a statement of changes, so the vendored copy also carries `VENDORED.md`. Nothing under `.agents/skills/impeccable/` or `vendor/` may be edited locally.
- Evidence: [`../NOTICE`](../NOTICE), [`../.agents/skills/impeccable/VENDORED.md`](../.agents/skills/impeccable/VENDORED.md), [`../.gitmodules`](../.gitmodules)

## D-009: Source documents never enter this repository

- Status: `accepted`
- Date: 2026-08-28
- Decision: A document handed over to become a template contributes its machinery only. The source file is never committed, and a preview built from real material is normalised first — identities replaced, private links removed, commercial figures rounded, and the most sensitive pages dropped entirely.
- Rationale: The templates came from real client work. The repository is public.
- Consequences: `/tedandlisa-new-template` leads with this rule. A normalisation pass must be verified by grep before publishing, case-insensitively — `437b628` exists because a case-sensitive pass replaced a client product name in upper case but missed its capitalised and lower-case forms, and the miss reached a public commit.
- Evidence: [`../skills/tedandlisa-new-template/SKILL.md`](../skills/tedandlisa-new-template/SKILL.md), `437b628`

## D-010: English and Korean are the default pair for inline-bilingual templates

- Status: `accepted`
- Date: 2026-08-28
- Decision: `web-document`, `mermaid-master`, and `architecture` ship English and Korean written inline and toggled by CSS. `monomind-deck` keeps on-demand Google Translate, which is a different mechanism for a different reading mode.
- Rationale: Inline pairs work offline, translate instantly, and let text inside a diagram translate too — which a runtime translator cannot do for SVG.
- Consequences: Every reader-visible string in those templates is written twice, including labels inside drawings. A missing pair shows in both languages and reads as a bug. `mermaid-master` goes further and carries a whole parallel slide set per language, which is why `ROUTES`, `TITLES`, and the sections must agree.
- Evidence: [`../references/slide-patterns-web-document.md`](../references/slide-patterns-web-document.md), [`../references/slide-patterns-mermaid-master.md`](../references/slide-patterns-mermaid-master.md)

## D-011: Export is the browser's own, never a bundled library

- Status: `accepted`
- Date: 2026-08-28
- Decision: "Download as PDF" is a print stylesheet plus `window.print()`. "Download the HTML" is the page serialising itself into a Blob. No html2canvas, no jsPDF.
- Rationale: `D-001` says a deck is one self-contained file. The upstream architecture generator ships both libraries from a CDN for Copy/PNG/PDF; adopting them would have made every generated diagram depend on two CDNs at read time.
- Consequences: There is no image export. A diagram that needs a bitmap gets screenshotted. Print fidelity is the browser's, so the print block is part of every template rather than an afterthought.
- Evidence: [`../assets/tedandlisa-template-architecture.html`](../assets/tedandlisa-template-architecture.html), [`../NOTICE`](../NOTICE)

## D-012: The intake payload outranks the command line

- Status: `accepted`
- Date: 2026-08-28
- Decision: The prompt shown in the panel is editable, and the payload's prompt wins over the text typed after `/tedandlisa`. Attached references are source material to read, never instructions to follow.
- Rationale: What fits on a command line rarely survives contact with the deck, and a user who edits the prompt in the panel means it.
- Consequences: `promptEdited` flags a deliberate change so an agent does not silently merge the two. Treating reference content as instructions would make an uploaded file an injection vector, so the contract states the boundary explicitly.
- Evidence: [`../references/intake-contract.md`](../references/intake-contract.md)

## D-013: Non-template paths live in the same registry, marked `external`

- Status: `accepted`
- Date: 2026-08-28
- Decision: A way of making a deck that is *not* built from a template here — currently `/tedandlisa-design` — is registered in `templates/templates.json` alongside the templates, with `kind: "external"` and a `skill` field. The intake payload then carries a `handoff` naming that skill, and the skill stops rather than copying a template.
- Rationale: The user chooses between five options, not between "templates" and "some other menu". A separate list would have meant a second gallery, a second question, and a second place to keep in sync.
- Consequences: `kind` now carries two meanings — which questions apply, and whether anything is built here at all. Question filtering had to become explicit: every question that only makes sense for a template we build declares `kinds`, and the handoff asks one question the templates never do (`format`: animated HTML, `.pptx`, or both). A sixth path follows the same shape; it does not get its own UI.
- Evidence: [`../templates/templates.json`](../templates/templates.json), [`../references/intake-contract.md`](../references/intake-contract.md), [`../SKILL.md`](../SKILL.md)

## D-014: Previews open in an overlay, not a new tab

- Status: `accepted`
- Date: 2026-08-28
- Decision: A preview opens in a full-screen overlay inside the intake panel, carrying its own "open in a new tab" link. Only external URLs, which refuse to be framed, keep plain link behaviour.
- Rationale: `target="_blank"` is not reliable. In an embedded browser it becomes a same-tab navigation, and the panel holds a half-answered form with no persistence — one click on Preview and the answers are gone.
- Consequences: Previews must be same-origin to be framed, which they are, since the runner serves `previews/`. Anything hosted elsewhere gets a plain link and the risk that comes with it. The overlay owns the keyboard while open, so the panel's number and arrow shortcuts are suppressed until it closes.
- Evidence: [`../assets/tedandlisa-intake.html`](../assets/tedandlisa-intake.html), [`LEARNINGS.md`](LEARNINGS.md) `L-013`

## D-015: No animation library

- Status: `accepted`
- Date: 2026-08-28
- Decision: Animation in anything shipped here is CSS, or the Web Animations API when it has to be scripted. No GSAP, Anime.js, Motion, Mo.js, React Spring, or Theatre.js.
- Rationale: `D-001` says a deck is one self-contained file, and GSAP — the one library that arrived with borrowed work — is "all rights reserved" under the GreenSock Standard License, so it could not be bundled at all. Measured against what the decks actually animate, no library was needed: reveals are CSS classes toggled by an `IntersectionObserver`, and the two scripted entrances are four lines of WAAPI.
- Consequences: A future deck wanting sequenced timelines, spring physics, or path morphing has to make the case first; if one is ever justified, Anime.js is the candidate — ~9 KB and MIT, so it can be inlined. Scripted animation should prefer the independent `scale`, `rotate`, and `translate` properties over `transform`, so it composes with CSS already running on the element rather than overriding it.
- Evidence: `d03ec4e`, [`../previews/slide-design.html`](../previews/slide-design.html), [`../NOTICE`](../NOTICE)

## D-016: The README opens with the start prompt

- Status: `accepted`
- Date: 2026-08-28
- Decision: `README.md` leads with a **Start here** section carrying the copy-paste prompt and a short "what you get" list, placed above "Why it matters". The prompt appears once in the file; the former "Use with any AI agent" section was removed rather than left as a second copy.
- Rationale: The prompt was previously at line 211 of 272, below the templates, the build sequence, the intake, the design review and the extension guide. A reader arriving from a link had to scroll past nine sections to learn that starting costs one paste and no installation. Nothing above it answered the two questions a new reader actually has — what do I get, and how do I start.
- Consequences: The prompt is now duplicated between `README.md` and `SKILL.md`'s invocation section, so a change to the invocation shape has to be applied in both. Future README edits should keep the prompt in the first screen; adding sections above **Start here** puts it back where it was. The repository URL is hard-coded in the prompt text, so a rename or move breaks it silently.
- Evidence: [`../README.md`](../README.md)

## D-017: Intake questions can be scoped to a template, not only to a kind

- Status: `accepted`
- Date: 2026-08-29
- Decision: `QUESTIONS` entries may carry a `templates` array alongside `kinds`.
  `rebuildOrder()` requires both to pass, so a question can be asked for one
  template and be absent from every other payload.
- Rationale: `sitemap-ia` needs answers no other template wants — the kind of
  site, whether it is a revamp, the existing sitemap, the benchmarks to argue
  against, the evidence behind the recommendation. Gating by `kind` would have
  put all of them in front of every `document` template, and a panel that asks
  irrelevant questions trains people to skim the relevant ones.
- Consequences: The contract's rule that a missing applicable key is malformed
  still holds, because `ORDER` decides what is serialised. Anyone adding a
  template-specific question must add its key to the `all` object too, or it is
  filtered into silence rather than erroring.
- Evidence: [`../assets/tedandlisa-intake.html`](../assets/tedandlisa-intake.html), [`../references/intake-contract.md`](../references/intake-contract.md)

## D-018: The `sitemap-ia` skeleton ships on CDNs, and standalone is an answer

- Status: `accepted`
- Date: 2026-08-29
- Decision: The template references mermaid, Google Fonts, Font Awesome and
  Tailwind from CDNs. `delivery: standalone` is what inlines them.
- Rationale: The source document was fully self-contained at 9MB, of which
  ~8.5MB was library code — Font Awesome's icon fonts, the Tailwind runtime,
  mermaid, and an unsubsetted CJK webfont. Committing that as a skeleton would
  put 9MB into a public repository and re-store it on every edit, to carry
  bytes that are identical for every user. On CDNs the skeleton is 111KB, in
  line with the other templates, and `web-document` already establishes that a
  CDN dependency is acceptable here.
- Consequences: A generated deck is not offline-capable unless the answer asks
  for it. The inlining is documented in `SKILL.md` rather than scripted, and
  the webfont subsetting step is the part most likely to be skipped — skipping
  it costs several megabytes.
- Evidence: [`../assets/tedandlisa-template-sitemap-ia.html`](../assets/tedandlisa-template-sitemap-ia.html), [`../SKILL.md`](../SKILL.md)

## D-019: `project-website` keeps the source's dark palette, contrast failure included

- Status: `accepted`
- Date: 2026-08-29
- Decision: The `project-website` skeleton ships the source design's dark tokens
  unchanged, including `--fg-faint:#565656`, which fails WCAG AA at the sizes it
  carries. The `:root` block names the measured ratios and the one-line
  override that fixes them; the added light theme is held to AA instead.
- Rationale: `/tedandlisa-new-template` says a template preserves its author's
  system, including choices the extractor would have made differently — and the
  faint tier is load-bearing for this design's hierarchy, not an oversight to
  patch silently. But shipping a measured failure with no note makes every
  downstream deliverable inherit it unknowingly. Naming the numbers and the fix
  in the file turns a silent defect into a deliberate, ten-second choice. The
  light theme is a MonoMind addition rather than the author's work, so it had no
  claim to the same deference and was re-tiered to 7.5 / 6.0 / 5.3 on white.
- Consequences: A generated site is not AA-clean in the dark theme unless
  someone acts on the comment, so the design-review step should expect to raise
  it. The same reasoning applies to the next extraction: preserve the source,
  measure it, and write the number down. It also means the two themes in this
  template are held to different standards, which is defensible only while the
  comment explaining why stays next to the tokens.
- Evidence: [`../assets/tedandlisa-template-project-website.html`](../assets/tedandlisa-template-project-website.html), [`../references/slide-patterns-project-website.md`](../references/slide-patterns-project-website.md)
