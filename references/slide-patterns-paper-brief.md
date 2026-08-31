# Paper brief — component reference

Markup for `assets/tedandlisa-template-paper-brief.html`. A light scroll-snap
deck that reads like a printed briefing paper: white ground under a faint
twelve-column grid, Archivo over Noto Sans TC, red and blue doing the arguing,
and chapter pages that invert to near-black so a long report has visible seams.

Use it when the deck will be read at desk distance and forwarded — a planning
input, a review, a recommendation someone prints. Use `evidence-deck` when the
same argument has to survive a projector, and `web-document` when it wants a
URL per section.

## Language

The template ships in Traditional Chinese, single language, exactly as its
source system did — `<html lang="zh-Hant">`, `Noto Sans TC` for body copy and
`Archivo` for display. There is no toggle and no translation runtime; unlike
`web-document` and `mermaid-master` there is no second language written inline
(`D-010` covers the bilingual shapes, not this one).

Two consequences worth stating before a deck is built:

- **Changing language means changing the font stack.** `--font-body` and
  `--font-display` are the whole mechanism. A deck written in English on
  `Noto Sans TC` will render, and will look subtly wrong.
- **Mixed CJK and Latin numerals are the point.** `font-feature-settings:"tnum"`
  on `body` keeps the Latin figures aligned inside CJK sentences.

## The shape of a slide

```html
<section class="slide">
  <div class="slide-content">
    <p class="eyebrow reveal">[這一頁在談什麼]</p>
    <h2 class="reveal">[把結論寫成一句話]</h2>
    <p class="body reveal">[支持這個結論的一段話。]</p>
  </div>
  <span class="pagenum">01</span>
</section>
```

- **`.reveal` must be a direct child of `.slide-content`.** The stagger is
  `nth-child`; a wrapper takes the delay and shifts everything after it.
- **Seven reveals, maximum.** The delays stop at `:nth-child(7)`.
- **`.pagenum` is hardcoded**, and the title and closing pages carry none by
  design. Renumber the rest by hand after any edit.

## Emphasis

| Class | Means | Colour |
| --- | --- | --- |
| `hl` | The load-bearing phrase | `--ink` |
| `red` | The part that is a problem | `--red` |
| `blue` | The part that is already working | `--blue` |
| `eyebrow blue` | A section whose subject is settled, not contested | `--blue` |

## Title and closing pages

`.title-slide` switches the slide to `justify-content:space-between`, so the
red rule pins to the top and the meta row to the bottom. Both pages use it, and
neither carries a page number.

```html
<section class="slide title-slide">
  <div class="title-rule reveal"></div>
  <div class="slide-content" style="flex:1;justify-content:center">
    <p class="eyebrow reveal">[專案名稱] · [報告類型]</p>
    <h1 class="reveal">[主標第一行]<br>[主標第二行]</h1>
    <p class="lead reveal">[一句話說明這份報告是什麼。]</p>
  </div>
  <div class="title-meta reveal">
    <span>[資料來源]</span><span>[資料期間]</span><span>[日期]</span>
  </div>
</section>
```

Here `.title-rule`, `.slide-content` and `.title-meta` are siblings, so they are
the reveals — the elements inside `.slide-content` stagger against each other
separately. `flex:1` on the content is what keeps the meta row at the foot.

## Chapter page

```html
<section class="slide" style="background-color:#0d0d0d;background-image:none">
  <div class="slide-content">
    <div class="chapter reveal">
      <p class="cfor" style="color:var(--red)">章節 01 · 供 [下游工作] 使用</p>
      <div class="cnum">01</div>
      <h2 style="color:#fff;font-size:clamp(1.5rem,4.4vw,3.4rem)">[章節的主張<br>寫成兩行]</h2>
      <p class="lead" style="color:#a8a8a8">[一句補充。]</p>
    </div>
  </div>
  <span class="pagenum" style="color:#5c5c5c">03</span>
</section>
```

**`background-image:none` is not optional.** Without it the light grid draws
over the black ground and the page looks dirty rather than inverted. The text
colours are inline for the same reason: the tokens are defined for white paper,
so the chapter page overrides them rather than redefining them.

## Data table

```html
<table class="data reveal">
  <thead><tr><th>[欄位]</th><th>[欄位]</th><th style="text-align:right">[數值]</th></tr></thead>
  <tbody>
    <tr><td class="k">[列標籤]</td><td>[說明]</td><td class="num">000</td></tr>
    <tr class="flag"><td class="k">[有問題的那一列]</td><td><span class="red">[為什麼]</span></td><td class="num">000</td></tr>
    <tr class="good"><td class="k">[已經成立的那一列]</td><td>[為什麼]</td><td class="num">000</td></tr>
  </tbody>
</table>
```

`td.k` is the key column, `td.num` is Archivo, right-aligned and `nowrap`.
`tr.flag` washes the row red, `tr.good` washes it blue. Right-align a numeric
header by hand — only the `td` takes it from the class.

## Bar chart

The one animated component. Widths live in an inline `--w`; the fill is at zero
until the slide gets `.visible`, and the reduced-motion block sets the final
width directly so it is never stuck empty.

```html
<div class="bars reveal">
  <div class="bar accent"><div class="lab">[項目一]</div><div class="track"><div class="fill" style="--w:88%"></div></div><div class="val">000</div></div>
  <div class="bar blue"><div class="lab">[項目二]</div><div class="track"><div class="fill" style="--w:64%"></div></div><div class="val">000</div></div>
  <div class="bar warn"><div class="lab">[項目三]</div><div class="track"><div class="fill" style="--w:41%"></div></div><div class="val">000</div></div>
  <div class="bar"><div class="lab">[項目四]</div><div class="track"><div class="fill" style="--w:23%"></div></div><div class="val">000</div></div>
</div>
```

- **A bar with no `--w` renders at zero width** and looks like a rendering fault
  rather than an empty value. Always write one, even for a zero.
- The widths are proportions you compute; nothing normalises them. Scale to the
  largest value in the set, or the chart lies.
- `.accent` red, `.blue` blue, `.warn` amber, none for black. The `.val` on the
  right picks up `.accent` and `.blue` but not `.warn`.

## Split and split3 cards

```html
<div class="split reveal">
  <div class="card"><div class="ct">[宣稱的數字]</div><div class="cn">000</div><div class="cd">[出處。]</div></div>
  <div class="card bad"><div class="ct">[實際的數字]</div><div class="cn">0,000</div><div class="cd">[為什麼以它為準。]</div></div>
</div>
```

`.bad` red, `.good` blue, plain neutral. `.split3` takes three. Both collapse to
one column under 820px, where the bar chart also narrows its label column.

When `.cn` holds words rather than a figure, cut the display size inline —
`<div class="cn" style="font-size:clamp(1.1rem,2.6vw,1.9rem)">` — because a CJK
phrase at 3.4rem Archivo 900 overruns the card.

## Mega number

```html
<div class="reveal" style="display:flex;flex-direction:column;gap:.5rem">
  <div class="mega red">0.0×</div>
  <p class="mega-note">[這個數字算的是什麼、期間多長、來源是誰。]</p>
</div>
```

`.mega` is black by default; `.mega.red` is the accent. `.mega.compact` is the
smaller size for a long figure.

## Decision box

How this template ends an argument: an observation, then the action.

```html
<div class="decision reveal">
  <div class="dq">建議做法</div>
  <div class="da">[要做什麼、由誰做、做到什麼程度算完成。]</div>
</div>
```

`.dq` is the heading — "建議做法", "時間敏感", "範疇決策", whatever names the
kind of decision. `.da` is the action. Write an instruction, not a reflection:
a decision box with no verb in it is a summary wearing a decision's clothes.

## Spec list and numbered points

```html
<div class="specs">
  <div class="spec reveal"><span class="si">01</span><span class="st">[把要求寫成一句指令]<em>[支持它的那個觀察]</em></span></div>
</div>

<ul class="pts">
  <li data-n="Q1" class="reveal"><span class="hl">[問題本身。]</span>[答案會決定什麼。]</li>
</ul>
```

`<em>` is restyled as a block sub-line, not italics. `data-n` is the list
marker, drawn by `::before`, so it takes `Q1`, `01`, `—` or any short string.

## Chrome — do not rewrite

- The controller is one class at the foot of the file — `IntersectionObserver`
  for `.visible`, plus keyboard, touch, progress bar and nav dots. It counts
  `.slide` itself; never hand-write dots.
- `html{scroll-snap-type:y mandatory}` with `body{overflow:hidden}` is the snap.
- `.slide` and `.slide-content` both clip: an overflowing page loses its bottom
  in silence. Check every page at 375px wide and 600px tall.
- The grid field is `background-size:calc(100vw/12)`, so it is genuinely twelve
  columns at any width. Chapter pages switch it off; nothing else should.

## Colophon — the maker's credit

The closing page's meta row carries the credit as its last item, in the row's
own micro type. It ships by default; remove that last `<span>` (only) when the
intake answered `credit: false` — the `monomind ai lab` span before it belongs
to the `logo` answer. The product name is wrapped `notranslate` so a reader's
browser translation leaves it alone.

```html
<span><a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer">以 <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span> 製作</a></span>
```

## Dependencies

Google Fonts only — Archivo and Noto Sans TC. `delivery: standalone` inlines
both, and Noto Sans TC is the expensive half: subset it to the glyphs the deck
actually uses or the file gains several megabytes.

There is no print stylesheet. Answering `export: pdf` on this template means
writing the `@media print` block, not switching one on.
