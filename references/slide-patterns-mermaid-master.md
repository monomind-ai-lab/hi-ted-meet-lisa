# Mermaid master — component reference

Markup for `assets/tedandlisa-template-mermaid-master.html`. This template is
**diagram-first**: each slide is one large drawing with a title above it and a
footer below. If a slide has no diagram, it probably belongs in a different
template.

Three things make it unlike the other two:

- **Light paper**, not dark. `--paper: #f5f5f5`, `--ink: #2d3142`, one orange
  accent `#eb6c36`. Instrument Serif for headings, Geist for text, Geist Mono
  for every label and chip.
- **Fully self-contained.** Diagrams are inline SVG, already rendered — there is
  no mermaid runtime and no CDN. Export from mermaid, then paste the SVG in.
- **Bilingual by parallel slides.** Every slide exists twice, `s-en-NN` and
  `s-zh-NN`, so even the text inside a diagram is translated.

## The three registers that must agree

Routing breaks silently when these drift apart. After adding or removing a
slide, check all three:

| Register | Where | What it holds |
| --- | --- | --- |
| `ROUTES` | script at the foot | `["01", "02", …]` in order |
| `TITLES` | script at the foot | `{en: [...], zh: [...]}` — **index title first**, then one per route |
| Sections | markup | `s-en-NN` **and** `s-zh-NN` for every route |

A route with no `s-zh-NN` falls back to the index when a reader switches
language, which looks like the deck losing their place.

## Slide

```html
<section class="slide" id="s-en-01" data-lang="en" data-route="01">
  <p class="eyebrow">§2 SECTION</p>
  <h1>The claim this diagram makes.</h1>
  <p class="subtitle">One or two sentences. Not a caption — the point.</p>
  <div class="diagram"><svg viewBox="0 0 1000 420" role="img" aria-label="…">…</svg></div>
  <footer>DOCUMENT · SECTION · NOTE</footer>
</section>
```

## Index

```html
<section class="slide" id="s-en-index" data-lang="en" data-route="index">
  <header><div class="head-l">
    <p class="eyebrow">PROJECT · VISUAL INDEX</p>
    <h1>Deck title</h1>
    <p class="subtitle">What this set covers.</p>
  </div></header>
  <p class="section-label">SECTION NAME</p>
  <div class="grid">
    <a class="card focal" href="#en/01">
      <div class="card-num"><span>01</span><span class="tag">TAG</span></div>
      <h3>Slide title</h3>
      <p>one-line summary</p>
    </a>
  </div>
  <footer>DOCUMENT · VERSION · DATE</footer>
</section>
```

`.card.focal` marks the one diagram a reader should open first. Use it once.
Index cards link by hash (`#en/01`), so they keep working in the saved file.

## Diagrams — the rules that matter

- **`viewBox`, never `width`/`height`.** The stylesheet sets `width:100%;
  height:auto`; a hardcoded size defeats it and breaks on phones.
- **Paint the background**: `<rect width="100%" height="100%" fill="#f5f5f5"/>`
  as the first child, or the diagram is transparent in print and in exports.
- **Reuse the shared arrow markers.** They are defined once in a zero-size
  `<svg>` at the top of `<body>`: `url(#arrow)`, `#arrow-start`, `#arrow-accent`,
  `#arrow-accent-start`, `#arrow-soft`, `#arrow-dashed`. Do not redefine them
  per diagram, and do not delete that block.
- **Draw arrows before nodes.** SVG has no z-index; paint order is document
  order, so connectors drawn last cut across the boxes.
- **Every label is a `<text>` element**, never text baked into a path or image —
  the Chinese copy of the slide has to be able to say something different.
- **Palette**: nodes `#ffffff` on `rgba(45,49,66,0.12)` rule; the one focal node
  gets `rgba(235,108,54,0.08)` on `#eb6c36`. Body text `#2d3142`, secondary
  `#7a8399`.
- Slides with `data-lang="zh"` re-font SVG text to Noto Sans TC automatically.

## Chrome — do not rewrite

- `#topbar` holds the language toggle; `#dnav` holds counter, Prev, Index, Next.
  Chips disable themselves at the ends of the deck.
- Keyboard: `←` / `→`, PageUp / PageDown, `Esc` or `Home` for the index, and
  `L` toggles language.
- `@media print` shows every slide, one per page — the deck prints as a set.

## Colophon — the maker's credit

Each language's index footer ends with the credit link — the slide sets are
parallel, so the line exists once per copy and the two must stay in step. It
ships by default; remove the `<a>` (only) when the intake answered
`credit: false`.

```html
<footer><span>[DOCUMENT · VERSION · DATE]</span> <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener">Made with Hi Ted, Meet Lisa</a></footer>
<footer><span>[문서 · 버전 · 날짜]</span> <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener">Hi Ted, Meet Lisa로 제작</a></footer>
```

## Dependencies

Google Fonts only. Everything else is inline, so the file works offline and
survives being emailed.
