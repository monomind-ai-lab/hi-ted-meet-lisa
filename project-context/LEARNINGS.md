# Learning Registry

Promote a learning only when evidence supports reuse beyond one task. Use
stable IDs such as `L-001`.

## L-001: Google Translate rewrites product names and filenames

- Status: `accepted`
- Scope: Any deck or page that ships the language switch.
- Learning: The translator rendered *MonoMind AI Lab* as 人工智慧實驗室 and *MIT* as 麻省理工學院, the university. Filenames such as `NOW.md` and product names such as GitNexus were rewritten too.
- Action: Mark identifiers `translate="no"`. The protection pass marks structural blocks and regex-matched paths and filenames before the translator loads; extend its term list whenever a deck introduces a new product name.
- Evidence: `HANDOFF.md` (`fbe8cec`), [`../assets/tedandlisa-template.html`](../assets/tedandlisa-template.html)

## L-002: CJK output runs flush against protected spans

- Status: `accepted`
- Scope: Translated rendering of any deck using `.nt-term`.
- Learning: Translated text collided with protected identifiers, producing `目前狀態NOW.md限制` with no separation.
- Action: Apply `margin-inline: 0.15em` to `.nt-term`, scoped to `html.translated-ltr` and `html.translated-rtl` so English spacing is untouched.
- Evidence: `HANDOFF.md` (`fbe8cec`)

## L-003: The browser pane misreports fixed chrome on this deck

- Status: `accepted`
- Scope: Verifying any horizontally scroll-snapped layout in an emulated viewport.
- Learning: With a narrow viewport emulated, every `position: fixed` element — progress bar, counter, language switch, menu — reported coordinates far off-screen, and `innerWidth` returned 1500 against a 375 layout viewport. Loading the live site, which has no hamburger, showed its shipped `#deck-counter` displaced identically. The displacement is a measurement artifact, not a layout bug.
- Action: Read `document.documentElement.clientWidth`, not `innerWidth`. Do not "fix" displaced fixed chrome on the strength of pane coordinates, and do not treat the pane as evidence about phone layout — check a real device.
- Evidence: `HANDOFF.md` (`fbe8cec`)

## L-004: Google Translate applies slowly and only while compositing

- Status: `accepted`
- Scope: Verifying the language switch in any automated browser surface.
- Learning: Translation took 10–20 seconds in the pane and ran only while the tab was actually compositing; taking a screenshot forced it.
- Action: Force a paint and wait before judging the switch broken. Translation also needs a served origin — the language cookie will not stick on `file://`.
- Evidence: `HANDOFF.md` (`fbe8cec`)

## L-005: Maintenance instructions need observable triggers and a check

- Status: `accepted`
- Scope: Any instruction that asks an agent to maintain a document alongside its real work.
- Learning: "Update project context at meaningful milestones and handoffs" produced no updates at all. Nothing defined a milestone, so the condition was never evaluated: this repository accumulated three commits, a second template, an intake contract, and a design review while `NOW.md`, `DECISIONS.md`, and `LEARNINGS.md` all still held their installed example entries.
- Action: Give each document a list of observable events, evaluated as work lands, and back it with a harness check that reports the evidence. Keep the check to detecting that work happened — judging whether a decision or a learning fired needs the agent, and a check that guesses will fill the registries with noise.
- Evidence: [`DECISIONS.md`](DECISIONS.md) `D-005`, [`SKILL.md`](SKILL.md)

## L-006: Contrast has to be measured by painting, not by parsing

- Status: `accepted`
- Scope: Any automated accessibility or contrast check in a browser.
- Learning: A naive numeric parse of `getComputedStyle().color` reports the wrong answer for modern CSS colour functions. `color(srgb 1 1 1 / 0.92)` uses 0–1 floats, so white parsed as near-black; `oklab(0.43 -0.02 -0.12)` parsed as black too. Three separate readings were wrong before the method changed — one of them a false FAIL on a panel that was actually white, another a false 19.25:1 on a mid-blue. A second error compounded it: walking DOM ancestors to find the backdrop of `position: fixed` chrome lands on `body`, whose background is only visible where no slide covers it, producing an inverted verdict in dark theme.
- Action: Paint the colour into a 1×1 canvas over the known backdrop and read the pixel back. For fixed chrome, seed the backdrop with the element actually behind it — the current slide — not the DOM ancestor. Impeccable's own detector cannot substitute for this: it reported `DEGRADED — computed contrast is NOT evaluated`.
- Evidence: `f9b77e4`, [`../references/design-review.md`](../references/design-review.md)

## L-007: A theme that flips text must flip its surfaces, and generated content defeats both

- Status: `accepted`
- Scope: Any template offering a light/dark toggle.
- Learning: Two distinct failures with the same symptom. `.deck-menu-panel` hardcoded a deep-ink fill while its text colour came from a token, so light theme produced dark-on-dark at 1.12:1 — an invisible menu that every structural check passed. Separately, mermaid renders to a palette fixed at `initialize()` time, and the placeholder diagram sources carried `classDef default fill:#181818`, so diagrams stayed black boxes on a white page no matter what the CSS said.
- Action: When adding a theme, audit every hardcoded surface, not just text tokens. For generated content, define both palettes, re-initialise the generator on toggle, and re-render — an SVG already painted cannot be restyled. Never hardcode colour inside diagram source; style only by classes that carry meaning.
- Evidence: `f9b77e4`, `b859a4c`, [`../references/slide-patterns-web-document.md`](../references/slide-patterns-web-document.md)

## L-008: `var()` does not resolve inside an SVG presentation attribute

- Status: `accepted`
- Scope: Any SVG themed with CSS custom properties.
- Learning: `stroke="var(--grid)"` on a `<pattern>` path silently produced no stroke — the background grid was simply absent, with no error anywhere. The same value works from a CSS rule.
- Action: Style SVG through CSS selectors (`#grid path { stroke: var(--grid) }`) or classes, never through `var()` in a presentation attribute. This is also what makes a themed diagram a token swap rather than a redraw.
- Evidence: `e4b5c71`, [`../references/slide-patterns-architecture.md`](../references/slide-patterns-architecture.md)

## L-009: Headless Chrome writes the screenshot and may then hang

- Status: `accepted`
- Scope: Any scripted screenshot capture.
- Learning: `--headless --screenshot` wrote a complete 228 KB PNG and never exited, so a subprocess call with a timeout raised `TimeoutExpired` on a capture that had in fact succeeded.
- Action: Treat the file on disk as the result. Catch the timeout, then check the output path exists and is non-empty before reporting failure. `--headless=new` behaves better but the guard is still worth keeping.
- Evidence: [`../scripts/tedandlisa_thumbs.py`](../scripts/tedandlisa_thumbs.py)

## L-010: An unrecognised flag can run an interactive installer at its defaults

- Status: `accepted`
- Scope: Any first-time invocation of an unfamiliar CLI installer.
- Learning: `npx impeccable@latest install --help` did not print help. The flag was ignored, the real installer ran, and with empty stdin it took every default — installing into the project instead of globally, and enabling hooks that the user's profile keeps off.
- Action: Do not probe an installer's flags by running its mutating subcommand. Read the project's README or `--version` first, and pass explicit flags for every choice that matters (`--scope`, `--providers`, `--no-hooks`). Check what landed before continuing; here it was recoverable only because nothing had been committed yet.
- Evidence: `NOTICE`, [`../.agents/skills/impeccable/VENDORED.md`](../.agents/skills/impeccable/VENDORED.md)

## L-011: Anonymisation must be case-insensitive and verified by grep

- Status: `accepted`
- Scope: Any normalisation of real material before publishing it.
- Learning: A replacement pass handled a client product name in upper case but not its capitalised or lower-case forms, and eleven occurrences reached a public commit. The visible labels had all been changed; what survived were lower-case attribute values, where nobody was looking. A separate attempt to scrub metadata with a greedy regex (`Canva doc=[^\x00]*`) ran past the field boundary and corrupted a JPEG — `sips` reported no dimensions.
- Action: Replace case-insensitively, then prove it with a case-insensitive grep across the whole tree before committing. When editing inside a binary, match an exact known literal and preserve its byte length rather than using a greedy pattern, and verify the file still decodes.
- Evidence: `437b628`, `0a1ad69`

## L-012: Verifying through the function hides a dead interface

- Status: `accepted`
- Scope: Any UI verified from a console or a test harness rather than by using it.
- Learning: The intake gallery was checked repeatedly by calling `choose('template', id)` from the console, and it passed every time — state changed, questions filtered, the payload was right. Clicking a card did nothing at all: the cards render as `.tpl` and the click handler only matched `.opt`, so the entire selection path was dead from the moment the gallery shipped. The user found it, not the checks.
- Action: Drive the interface the way a person does at least once per feature — a real click on a real element — before reporting it works. Calling the handler proves the handler; only the click proves the wiring. The same applies to keyboard paths and links.
- Evidence: `4849661`

## L-013: An embedded browser turns `target="_blank"` into a same-tab navigation

- Status: `accepted`
- Scope: Any link offered from a page that holds unsaved state, previewed in an in-app browser.
- Learning: A preview link with `target="_blank" rel="noopener"` navigated the current tab instead of opening a new one, and a `window.open(href, "_blank")` fallback behaved the same way — `tabs_context` showed one tab throughout, with its title changed. In a panel holding a half-answered form, that silently discards every answer.
- Action: Do not rely on a new tab to protect unsaved state. Frame same-origin content in an overlay the page controls, and offer the new-tab link from inside it. Where framing is impossible — a site sending `X-Frame-Options` — either persist the state first or accept the navigation deliberately.
- Evidence: `4849661`, [`DECISIONS.md`](DECISIONS.md) `D-014`

## L-014: Measure what a dependency does before replacing it

- Status: `accepted`
- Scope: Any migration away from a third-party library.
- Learning: A deck loaded GSAP from a CDN and named GSAP timelines, SplitText, and ScrollTrigger on its own slides, which made replacing it look like a real port. Grepping the source first showed two `gsap.from` calls in a 3.3 KB script, already behind an `if (window.gsap)` guard; SplitText and ScrollTrigger appeared only as marketing copy. Everything else was CSS classes toggled by an `IntersectionObserver`. The replacement was four lines of Web Animations API, not a library swap.
- Action: Count the actual call sites before choosing a replacement. A library's advertised feature set describes what it *can* do, not what this codebase asked of it, and prose inside the artifact is not evidence of use.
- Evidence: `d03ec4e`, [`DECISIONS.md`](DECISIONS.md) `D-015`

## L-015: Gradient text clips its own descenders

- Status: `accepted`
- Scope: Any heading using `background-clip: text`, which is most gradient display type.
- Learning: A hero title showed its *g* and *y* sliced off along a flat line. The cause is not overflow or a clipping ancestor: `background-clip: text` paints the gradient only within the element's box, and the glyphs reached past it. Measured, Plus Jakarta Sans needs a line-height of 1.262em to contain its own glyph box; the title ran at 1.05 for tight display leading, leaving 18.6px of descender outside the paint box at 80px. The bug only appears on words that have descenders, so it reads as a font rendering quirk rather than a CSS error, and a reviewer who skims the layout will miss it.
- Action: Treat `background-clip: text` and tight leading as a pair that must be checked. Extend the paint box with `padding-bottom` and cancel it with an equal negative margin, so the leading and the layout both survive; raising line-height past the font's own ratio also works but changes how every multi-line title reads. Verify by comparing measured ink bottom against the paint box, not by eye — the review reference carries the snippet.
- Evidence: [`../references/design-review.md`](../references/design-review.md), [`../previews/slide-design.html`](../previews/slide-design.html)

## L-016: The `web-document` nav has no narrow breakpoint, and the burger is what falls off

- Status: `accepted`
- Scope: `assets/tedandlisa-template-web-document.html`, and any deck generated from it.
- Learning: At 375px the nav row measured 614px wide. The overflow is invisible in a screenshot of the page body — `document.documentElement.scrollWidth === clientWidth` still passed, because `.nav` is fixed and clips rather than widening the document. What ran off the right edge was the language toggle and, past it, the burger: the only control that opens the navigation on a phone. So the failure mode is not "the header looks cramped", it is "a phone reader cannot navigate the document at all", and the standard horizontal-overflow check does not catch it. The template's only nav media query is at 1120px, which moves `.links` into a dropdown but leaves the mark text, the three-button utilbar, the language pair and the burger sharing one 64px row. Arithmetic alone condemns it: utilbar 181 + language 90 + burger 40 + gaps and padding ≈ 399px before the mark contributes anything, so the shipped template overflows a 375px phone even with an empty mark.
- Action: When auditing fixed chrome, measure each control's `getBoundingClientRect().right` against `window.innerWidth` rather than trusting a document-level overflow check. The repair that fits the template's idiom is a `max-width:640px` block that drops the mark to its logo and the utilbar to its icons — nothing removed, every control still reachable, measured at 284px. Both `assets/tedandlisa-template-web-document.html` and `previews/web-document.html` now carry that block, verified at 375px: the nav row went from 590px to 375px, the burger from 215px off screen to a right edge of 293px, and the menu opens with every link reachable. The 640/641 boundary was checked in both directions.
- Evidence: [`../assets/tedandlisa-template-web-document.html`](../assets/tedandlisa-template-web-document.html), [`../references/design-review.md`](../references/design-review.md)

## L-017: A themed value read straight after the toggle is the transition, not the theme

- Status: `accepted`
- Scope: Any automated contrast or colour check run against a template with a theme control.
- Learning: A contrast sweep over the light theme reported the utilbar buttons at 3.54:1 and failing AA. The colour it measured was `#888888` — the *dark* theme's `--muted` — while `getComputedStyle(document.documentElement).getPropertyValue('--muted')` at the same instant already returned the light `#656c7a`. The cause is `.utilbar button { transition: color .15s }`: setting `data-theme` starts an interpolation, and a synchronous read samples it at t≈0. Settled, the same element measures 5.23:1 and passes. A related trap sat in the harness itself — priming the probe canvas with an opaque fill makes every colour read back with alpha 1, so a transparent background is reported as that fill and every ancestor walk stops at the first element; that alone turned dark-on-white into a fabricated 1.08:1. Both produce confident, specific, entirely false findings.
- Action: Separate the theme switch from the measurement by at least one animation frame plus the longest transition — in practice a second — and assert the settled value before sweeping. Detect a colour's real alpha by painting it over black *and* white and solving for it, never by priming a single ground. Sanity-check any sweep whose failures cluster near 1.0:1: that is the signature of a broken probe, not a broken design.
- Evidence: [`../references/design-review.md`](../references/design-review.md)

## L-018: Swapping the inline language pair touches five coupled places, none of them the content

- Status: `accepted`
- Scope: `web-document` and any template whose second language is written inline.
- Learning: Building a document in English and Traditional Chinese from a template that ships English and Korean is not a find-and-replace on the spans. The pair is encoded in five places that fail independently and mostly fail quietly: the Google Fonts URL and the `--sans` stack (`Noto Sans KR`), the two visibility rules plus the `body[data-lang]` font rule, the language button's id and label (`btnKo` / `한국어`), the routing regex `#/(en|ko)/` — which silently falls back to English for every deep link in the new language rather than erroring — and the `documentElement.lang` assignment, which otherwise announces the wrong language to a screen reader while the visible text is correct. Missing the regex is the worst of them, because the language button still appears to work; only a pasted deep link exposes it.
- Action: Treat the language pair as one change with a five-point checklist, and verify it by loading a deep link in the new language from a cold start, then asserting `document.documentElement.lang` after the switch has settled — not by looking at the page, which is the one check all five failures survive.
- Evidence: [`../references/slide-patterns-web-document.md`](../references/slide-patterns-web-document.md), [`../assets/tedandlisa-template-web-document.html`](../assets/tedandlisa-template-web-document.html)

## L-019: `document.open()` reuses the frame's Window, so a re-mounted script redeclares its own consts

- Status: `accepted`
- Scope: Any template that assembles a document at runtime and writes it into an
  iframe — currently `sitemap-ia`, and anything that copies its mount script.
- Learning: Writing a document into a same-origin iframe with
  `document.open()` / `write()` / `close()` clears the DOM but **keeps the
  frame's `Window`**, and with it the global lexical environment. The prototype
  script opens with `const nl = …` and `const site = …`, so the second mount is
  a redeclaration — a *parse-time* `SyntaxError` that stops the entire script
  before a line of it runs. The failure is silent and looks like success: the
  markup is all there, element counts are right, `footer` is present, and only
  the rendered content is missing. The giveaway is stale state — the frame
  still held the previous mount's `page` object, which is impossible if the
  script had re-run. Assertions on structure pass on the broken document; only
  reading rendered text catches it.
- Action: Give every mount a new realm by replacing the iframe element
  (`freshFrame()`), not by reusing it. When verifying an iframe-mounted
  prototype, assert on rendered content — a title, a breadcrumb, a route — never
  on element counts alone.
- Evidence: [`../assets/tedandlisa-template-sitemap-ia.html`](../assets/tedandlisa-template-sitemap-ia.html), [`../references/slide-patterns-sitemap-ia.md`](../references/slide-patterns-sitemap-ia.md)

## L-020: A class rule outranks `[hidden]`, so a styled panel paints over a working page

- Status: `accepted`
- Scope: Any component toggled with the `hidden` attribute that also carries a
  class-level `display`.
- Learning: `.mmfallback{display:flex}` beats the UA stylesheet's
  `[hidden]{display:none}` on specificity, so setting `hidden` did nothing and
  the prototype's error panel covered a prototype that was working perfectly.
  Every DOM assertion agreed with the code — `el.hidden` was `true` — while
  `getComputedStyle(el).display` said `flex`. Only a screenshot showed it.
- Action: Any rule that sets `display` on a class must ship
  `.thing[hidden]{display:none}` beside it. Assert on `getComputedStyle`, not on
  the attribute, and look at the page at least once before calling it verified.
- Evidence: [`../assets/tedandlisa-template-sitemap-ia.html`](../assets/tedandlisa-template-sitemap-ia.html)

## L-021: Extracting a template leaves registers pointing at the source's shape

- Status: `accepted`
- Scope: `/tedandlisa-new-template`, and any extraction from a data-driven document.
- Learning: Replacing a source document's data with placeholder data is not
  enough when its *chrome* indexes into that data. The desktop footer picked
  groups by hardcoded index (`[1,2,4,5,7,8]`) — fine for the source's tree,
  out of bounds in a smaller placeholder one. It dereferenced `undefined`,
  threw inside `applyLanguage()`, and took the whole prototype down with it,
  producing exactly the same silent half-loaded page as L-019. The same class of
  register also covers `PAGES`, nav entries, and any lookup keyed by section id.
- Action: After swapping a template's data, grep the retained chrome for numeric
  indexes and key names that came from the source, and rewrite them to the
  skeleton's own shape. The `new-template` procedure already says to rewrite
  routing arrays and page registers; index-based lookups belong in that list.
- Evidence: [`../skills/tedandlisa-new-template/SKILL.md`](../skills/tedandlisa-new-template/SKILL.md), [`../assets/tedandlisa-template-sitemap-ia.html`](../assets/tedandlisa-template-sitemap-ia.html)

## L-022: Reveal-on-scroll renders a blank page wherever IntersectionObserver never fires

- Status: `accepted`
- Scope: Any template using the `.reveal` / `IntersectionObserver` pattern —
  `project-website` today, and any extraction that inherits it.
- Learning: `.reveal` starts at `opacity:0` and is only made visible by an
  observer callback, so any context that never delivers those callbacks renders
  a page that is structurally perfect and visually empty. This is not
  hypothetical: in a hidden browser tab a freshly constructed probe observer
  fired zero times over 600ms while the observed element sat 187px inside a
  720px viewport, and `document.visibilityState` was `hidden`. The same tab also
  throttles `setTimeout`, so a naive timer fallback does not run either. Two
  earlier confusions traced to the same root — scrolled screenshots of the
  source site came back blank, and a second page of the template looked broken
  when it was not.
- Action: Never let an observer be the only path to visible. Arm reveals per
  page activation, and pair them with a fail-visible timer that checks whether
  *any* element in that scope was reported and reveals the lot if none was —
  which leaves the animation untouched wherever the observer does work. Add
  `@media print{.reveal{opacity:1}}` beside it. When a page looks blank, check
  `document.hidden` before believing the markup is wrong.
- Evidence: [`../assets/tedandlisa-template-project-website.html`](../assets/tedandlisa-template-project-website.html)

## L-023: The browser pane serves stale CSS and defers style recalc, so palettes must be measured off-browser

- Status: `accepted`
- Scope: Any contrast or token verification done through the preview pane.
- Learning: Three consecutive contrast measurements of the same light palette
  disagreed with each other and with the file. Two causes, both invisible from
  inside the page: the pane re-served a cached copy of the HTML after the file
  on disk had been patched twice, and setting `data-theme` then reading
  `getComputedStyle` in the same task returned the *old* custom-property values
  — one probe reported the dark `--fg-muted` (`rgb(161,161,161)`) against the
  light background, a pairing that exists nowhere in the stylesheet. The
  contradiction was only caught because the returned colour was checked against
  the token file rather than trusted.
- Action: Measure palette contrast analytically from the token values — the
  inputs are hex strings and the formula is twelve lines of Python — and use the
  browser only for layout and behaviour. When the browser must be used, bust the
  cache with a query string and assert the theme by reading back a known token
  colour before trusting any ratio computed alongside it.
- Evidence: [`../assets/tedandlisa-template-project-website.html`](../assets/tedandlisa-template-project-website.html), `D-019`
