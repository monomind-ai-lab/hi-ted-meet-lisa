# Sitemap and IA proposal — component reference

Markup for `assets/tedandlisa-template-sitemap-ia.html`. Every snippet is
lifted from a shipped document, so it is known-good. Compose from these; do not
invent class names.

This template is a **document**, not a slide deck: pages are hash-routed, each
page scrolls, and both languages are written into the file rather than
translated at read time. What separates it from `web-document` is the last
page — the proposed sitemap wired up as a working navigation, at two
breakpoints, that a reviewer can click through.

Use it to argue for an information architecture: state the diagnosis, show the
structure, record the contested calls, and let the reader try the result.

## Page shell

Each page is a `section.page` whose id must match its `data-page` nav entry and
an entry in the `PAGES` array in the script at the foot of the file. Miss any of
the three and the page becomes unreachable.

```html
<section class="page" id="page-ID">
  <div class="band"><div class="wrap">
    <span class="eyebrow"><span class="en">EYEBROW</span><span class="zh">標籤</span></span>
    <h2 class="sec"><span class="en">HEADING</span><span class="zh">標題</span></h2>
    <p><span class="en">BODY</span><span class="zh">內文</span></p>
  </div></div>
</section>
```

The skeleton ships five: `overview`, `today`, `structure`, `megamenu`,
`records`. That order is the argument — claim, evidence, proposal, proof,
open questions. Drop one before adding a sixth.

## Bilingual text — the rule that governs everything

Every reader-visible string is written twice, `.en` then `.zh`, in that order.
The switch shows one and hides the other; a string written once shows up in
both languages, which is how this template fails most often.

```html
<span class="en">English</span><span class="zh">中文</span>
```

This applies inside table cells, captions, buttons, checklist items, mermaid
labels, and the prototype's own label table. It does not apply to numbers,
routes, or code.

To ship a language other than Traditional Chinese, rename the `.zh` class
throughout — markup, the two CSS rules that hide it, and the `setLang` calls.
The `languages` intake answer decides which.

## Hero and counts

The counts are the proposal's credibility. Use real ones or delete the row.

```html
<div class="statrow">
  <div class="stat"><b>000</b><span class="en">pages today</span><span class="zh">現有頁面</span></div>
</div>
```

## Table

For the diagnosis: one row per problem, with the evidence beside it.
`.pill-ok` and `.pill-p2` mark phasing.

```html
<div class="tblwrap"><table class="tbl">
  <thead><tr><th><span class="en">Problem</span><span class="zh">問題</span></th></tr></thead>
  <tbody><tr><td>NAME</td><td><span class="pill-ok">P1</span></td></tr></tbody>
</table></div>
```

## Mermaid figure

`data-fig` and the body's `id` must agree, and the source lives in a
`script.mmd` inside the same `.fig`. Diagrams render lazily, once, when their
page first becomes active.

```html
<div class="fig" data-fig="ID">
  <div class="fig-bar">
    <span class="fig-title">FIG 1 · TITLE</span>
    <div class="fig-actions"><button class="figbtn" onclick="openViewer('ID')"><span class="en">Expand</span><span class="zh">放大</span></button></div>
  </div>
  <div class="fig-body" id="fig-ID"></div>
  <div class="cap"><span class="en">CAPTION</span><span class="zh">說明</span></div>
  <script type="text/plain" class="mmd">flowchart TD
  A["LABEL"] --> B["LABEL"]
</script>
</div>
```

**Quote every label.** `A[Products]` is mermaid node syntax; `A["Products"]` is
text. A bracketed placeholder left unquoted renders as machinery or fails the
whole diagram.

## Decision record, contents, checklist

```html
<h3 class="sub" id="dec-01"><span class="en">DEC-01 · CLAIM</span><span class="zh">DEC-01 · 主張</span></h3>
<div class="decision"><b><span class="en">Decision.</span><span class="zh">決策。</span></b><span class="en"> WHAT</span><span class="zh"> 內容</span></div>
<ul class="bul">
  <li><span class="en"><b>Why.</b> REASONING</span><span class="zh"><b>理由。</b> 推論</span></li>
</ul>

<div class="toc">
  <h5><span class="en">On this page</span><span class="zh">本頁目錄</span></h5>
  <a onclick="jump('dec-01')"><span class="n">01</span><span class="en">TITLE</span><span class="zh">標題</span></a>
</div>

<ul class="chk">
  <li><span class="cid">Q-01</span><span class="en">OPEN QUESTION</span><span class="zh">待確認事項</span></li>
</ul>
```

A proposal that lists its gaps is easier to trust than one that hides them.
Keep the open questions honest.

## The navigation prototype

The last page carries two cards. The desktop view mounts in an iframe scaled to
the column; the mobile view opens in its own tab so it gets a real viewport.

Both run in **their own document**, assembled at runtime from the inert
`<script type="text/plain">` payload blocks at the foot of the file. This is not
stylistic. The prototype loads Tailwind, whose preflight resets `h1`–`h6`, `a`,
`ul` and `ol` — most of this document's typography — and it defines a global
`go()`, which is also the name of this document's router. Inlined, it would
break the page around it in two ways at once.

### Editing the structure

The taxonomy lives in three constants inside `mmScriptDesktop` and
`mmScriptMobile`, which must stay **identical in both**:

- `nl` — the label table. Every `data-nl` attribute in the markup must name a
  key that exists here. A missing key throws inside `applyLanguage()` and takes
  the whole prototype down with it, leaving bare markup and no behaviour.
- `site` — the tree. `{ key: { accent, large, title:[zh,en], groups:[ [ [zh,en], [ [zh,en], … ] ] ] } }`.
  `large: true` gives a section the two-column mega menu; use it for the two
  widest. A group with an empty children array renders as a single link.
- `DESC` — optional per-page summaries, matched fuzzily against the labels.
  Leave the array empty and the summary card never shows.

Section keys (`s1`…`s7`) appear in **four** places. Rename in all of them or the
prototype half-loads:

1. `nl` and `site` keys
2. `DESC_L1`
3. the `sets` register in `renderFooter()` — its group indices must exist in
   your tree, or it dereferences undefined
4. `data-menu` / `data-nl` / `data-nav` in `mmBodyDesktop` and `mmBodyMobile`

### Traps

- **Use `.mmfig`, never `.fig`, for the prototype cards.** `renderFigsIn()`
  walks every `.fig` on the active page and dereferences its `.mmd` child; a
  mermaid-less `.fig` throws and stops the diagrams after it.
- **`.mmfallback[hidden]{display:none}` is load-bearing.** A class rule beats
  the UA's `[hidden]` rule, so without it the fallback panel paints over a
  perfectly working prototype.
- **Each mount needs a fresh iframe element.** `document.open()` clears the DOM
  but reuses the frame's `Window`, so the previous mount's `const nl` / `const
  site` bindings survive. Re-running the script in that realm is a
  redeclaration — a parse-time `SyntaxError` that silently stops everything.
  `freshFrame()` replaces the element for exactly this reason; do not
  "simplify" it away.
- **The frame measures its own content height.** The prototype gets taller as a
  reader uses it, so the frame never scrolls internally and never captures the
  reader's wheel.

## Chrome you must not rewrite

The mermaid init, the `#/{lang}/{page}` router, the pan-and-zoom viewer, the
theme/PDF/HTML controls, the reduced-motion wrapper, and the prototype mount
script. They encode fixes for problems that are not visible in the markup.
Rewrite only the registers: `PAGES`, the nav entries, and the prototype's
`sets` indices.

## Colophon — the maker's credit

Every document footer carries a third `.mono` span with the credit link — the
prototype's own footers are the proposed site's content and never carry it. It
ships by default; remove the span (only) when the intake answered
`credit: false`.

```html
<span class="mono"><a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener"><span class="en">Made with Hi Ted, Meet Lisa</span><span class="zh">以 Hi Ted, Meet Lisa 製作</span></a></span>
```

## Dependencies

Google Fonts and mermaid from a CDN for the document; Font Awesome and Tailwind
from a CDN for the prototype. The `delivery: standalone` intake answer replaces
all four with inlined copies — subset the webfonts to the glyphs the document
actually uses, or Noto Sans TC alone runs to several megabytes.
