# Web document — component reference

Markup for `assets/tedandlisa-template-web-document.html`. Every snippet is
lifted from a shipped document, so it is known-good. Compose from these; do not
invent class names.

**Density — a `read` template.** Read at desk distance, so four to eight
items on a page or in a section is fine — a table of eight rows, a grid of
six cards, a checklist of eight. One argument per page rather than one idea:
the eye scans, returns, and links to it.

This template is a **document**, not a slide deck: pages are hash-routed, each
page scrolls, and both languages are written into the file rather than
translated at read time.

## Page shell

Each page is a `section.page` whose id must match its `data-page` nav entry and
an entry in the `PAGES` array in the script at the foot of the file. Miss any of
the three and the page becomes unreachable.

```html
<section class="page" id="page-ID">
  <div class="band"><div class="wrap">
    <span class="eyebrow"><span class="en">EYEBROW</span><span class="zh">標籤</span></span>
    <h2 class="sec"><span class="en">HEADLINE.</span><span class="zh">標題。</span></h2>
    <p class="lede"><span class="en">Lede.</span><span class="zh">前言。</span></p>
  </div></div>
</section>
```

`.band` is one vertical section; consecutive bands get a hairline between them.
`.wrap` centres content at 1200px. Headings: `h1.mega`, `h2.sec`, `h3.sub`,
`h4.subsub`.

## Bilingual text — the rule that governs everything

Every reader-visible string carries **both** languages as sibling spans:

```html
<span class="en">English text</span><span class="zh">中文文字</span>
```

`body[data-lang]` hides one set. Consequences to respect:

- **Never write a bare string** in page content. A string without a `.en`/`.zh`
  pair shows in both languages and looks like a bug.
- No whitespace between the two spans, or the hidden one leaves a gap.
- Identifiers that must not be translated — filenames, commands, product names —
  are simply written once, outside any `.en`/`.zh` span. There is no translation
  service to defend against, which is why this template needs no `notranslate`.
- Nav labels, buttons, captions, and table headers all follow the same rule.

## Cards

```html
<div class="grid3">
  <div class="fcard">
    <h4><span class="en">Title</span><span class="zh">標題</span></h4>
    <p><span class="en">Body.</span><span class="zh">內文。</span></p>
  </div>
</div>
```

`.grid2`, `.grid3`, `.grid4` collapse to one column on small screens.
`.tcard` is the compact variant with a mono `.icon` chip.

## Table

```html
<div class="tblwrap"><table class="tbl">
  <thead><tr><th>Column</th></tr></thead>
  <tbody><tr><td>Row</td><td><code>value</code></td><td><span class="pill-ok">ok</span></td></tr></tbody>
</table></div>
```

Always keep the `.tblwrap`: it is what stops a wide table scrolling the page.
Status pills: `.pill-ok` (green), `.pill-p2` (cyan), `.pill-warn` (amber).

## Mermaid figure

```html
<div class="fig" data-fig="ID">
  <div class="fig-bar">
    <span class="fig-title">FIG · CAPTION</span>
    <div class="fig-actions"><button class="figbtn" onclick="openViewer('ID')">Expand</button></div>
  </div>
  <div class="fig-body" id="fig-ID"></div>
  <div class="cap"><span class="en">Caption.</span><span class="zh">圖說。</span></div>
  <script type="text/plain" class="mmd">flowchart LR
  A["Node"] --> B["Node"]
  classDef default fill:#181818,stroke:#333333,color:#ffffff</script>
</div>
```

Rules that are easy to get wrong:

- `data-fig`, the `#fig-ID` body, and `openViewer('ID')` must use the same id.
- The source lives in `script[type="text/plain"].mmd` so the browser never runs
  it as JavaScript. Keep that type.
- Diagrams render **lazily on first visit** to their page and are cached for the
  fullscreen viewer. A diagram on a page nobody opens never renders.
- Square brackets are mermaid syntax. A placeholder must be quoted —
  `A["[NODE]"]`, not `A[[NODE]]` — or the brackets disappear.
- **Never hardcode node colours.** `classDef default fill:#181818,…` looks
  right until the reader switches to the light theme, at which point the
  diagram is a set of black boxes on a white page. The palette comes from
  `MERMAID_DARK` / `MERMAID_LIGHT` at the top of the script, and the toggle
  re-initialises mermaid and re-renders every figure. Style a diagram only
  through `classDef` names you define for *meaning* (a focal node, a
  deprecated path), and give those colours that work on both grounds.

## Decision record

```html
<div class="docmeta"><span class="tag">DOC-001</span><span class="tag">Accepted</span></div>
<div class="decision"><b>Decision.</b> What was decided.</div>
<ul class="bul"><li><strong>Option A.</strong> Why.</li></ul>
<ul class="chk">
  <li class="done"><span class="cid">C-01</span>Done.</li>
  <li><span class="cid">C-02</span>Outstanding.</li>
</ul>
<div class="codeblk">command --flag</div>
```

`.decision` has a green left rule; `.callout` has an accent one. `.chk` renders
☐ / ☑ from `li.done`.

## Per-page contents

```html
<div class="deck">
  <div><!-- lede and decision --></div>
  <div class="toc">
    <h5>On this page</h5>
    <a onclick="jump('anchor-id')"><span class="n">01</span>Section</a>
  </div>
</div>
```

`jump()` offsets for the fixed nav. Anchor targets need `h3.sub` or `h4.subsub`,
which already carry `scroll-margin-top`.

## Chrome you must not rewrite

- **Routing** — `#/{lang}/{page}`. `go(id)` changes page, `setLang(l)` changes
  language, both preserving the other half. Deep links must keep working.
- **Fullscreen viewer** — drag to pan, wheel to zoom, Esc to close, plus native
  fullscreen. It reads from the same SVG cache the page rendered.
- **Nav** — collapses to a burger under 1120px; the Documents dropdown flattens
  into the mobile list. The link row can neither shrink nor scroll (the
  dropdown lives inside it, so its overflow must stay `visible`): when the
  filled-in document carries enough pages to outgrow the bar at laptop widths,
  raise both burger breakpoints until the full row fits — thirteen links
  measured 43px too wide for a 1280px bar and ran over the language toggle;
  the shipped preview collapses at 1450px for that reason.

## Colophon — the maker's credit

The footer's `.mono` line ends with the credit link, written in both languages
like every other reader-visible string. It ships by default; remove the `<a>`
(only) when the intake answered `credit: false`.

```html
<div class="mono">[OWNER] · [YYYY-MM] · <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener"><span class="en">Made with Hi Ted, Meet Lisa</span><span class="ko">Hi Ted, Meet Lisa로 제작</span></a></div>
```

## Dependencies

Google Fonts, and **mermaid from a CDN**. Unlike the MonoMind deck, this
template is not fully self-contained: with no network, diagrams do not render
and the rest of the document still does. Say so when handing a file over.

## When unsure, default to

- **A page:** the shell — `.band` > `.wrap` with an eyebrow, `h2.sec` and a
  `.lede`.
- **A set of things:** `.fcard`s in `.grid3`; `.tcard` when they are small.
- **A comparison:** `.tblwrap` + `.tbl`.
- **A diagram:** a mermaid `.fig`, `flowchart LR`, colour only through named
  `classDef`s.
- **A decision:** `.decision` + `.chk`; a page with anchors: `.toc`.

## Known gaps

Evidenced, not imagined — each line names its record.

- **The language pair is coupled across five places, none of them the
  content** (`L-018`): the Google Fonts URL and `--sans`, the two visibility
  rules plus the `body[data-lang]` font rule, the button id and label, the
  routing regex `#/(en|ko)/` — which falls back to English on every deep link
  in the new language rather than erroring — and `documentElement.lang`.
  Nothing in the template or this reference lists them together (`NOW.md`).
- **`footer .mono` measures 3.34:1 on the dark ground**, below AA at its 13px
  (`NOW.md`). `html[data-theme="light"] footer .mono` repairs the same
  selector for the light theme and nothing repairs it for dark, which reads
  as an omission rather than a `D-019`-style decision.
- **The nav's link row can neither shrink nor scroll**, so the burger
  breakpoint is a per-document number — 1120px in the template, 1450px in the
  preview (`L-016`; `NOW.md`, 2026-09-02). `scripts/check_overflow.py` fails
  when the escape returns; nothing tells you the row needed the breakpoint
  raised until you look.
- **mermaid loads from a CDN.** With no network the diagrams do not render
  and the rest of the document does — say so at handover, or answer
  `delivery: standalone`.
- **Mermaid's palette is fixed at `initialize()`** (`L-007`): the toggle
  re-initialises and re-renders, but a `classDef` colour hardcoded in a
  diagram's source still defeats it — black boxes on white paper.
- **The shipped preview is English and Chinese; the template is English and
  Korean** (`D-010`, `NOW.md`). Converting the preview is a translation
  project, so the two will keep disagreeing.
