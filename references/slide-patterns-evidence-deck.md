# Evidence deck — component reference

Markup for `assets/tedandlisa-template-evidence-deck.html`. A dark, full-bleed
scroll-snap deck for an argument made out of measurements: tables that flag
their own bad rows, stat rows, one number at display size, and a bar of orange
that says what to do about it.

Use it when the deck's job is to make a case from data someone will push back
on. Use `monomind-deck` when the job is a talk, and `web-document` when the
reader will link to it rather than sit through it.

## The shape of a slide

Every slide is the same three-part frame. `.slide` is the snap target and the
grid field; `.slide-content` is the flex column that staggers; `.pagenum` sits
outside the content so it does not join the stagger.

```html
<section class="slide">
  <div class="slide-content">
    <p class="eyebrow reveal">[WHAT THIS SLIDE IS]</p>
    <h2 class="reveal">[The claim as a sentence]</h2>
    <p class="body reveal">[The supporting paragraph.]</p>
  </div>
  <span class="pagenum">03 / 09</span>
</section>
```

Three rules that are easy to break and hard to see:

- **`.reveal` must be a direct child of `.slide-content`.** The stagger is
  `nth-child`, so wrapping one in a spare `<div>` gives the wrapper that delay
  and pushes every sibling after it by one step.
- **Seven reveals, maximum.** The delays stop at `:nth-child(7)`; an eighth
  arrives with no delay and reads as a jump. Group rather than extend.
- **`.pagenum` is hardcoded.** Nothing computes it. Renumber every slide after
  adding or removing one — the nav dots and progress bar *are* computed, so a
  stale page number is the only thing that will disagree.

## Emphasis

Three classes, three meanings. Using them interchangeably is what makes a
data-heavy slide unreadable.

| Class | Means | Colour |
| --- | --- | --- |
| `hl` | This is the load-bearing phrase | `--fg`, full white |
| `sig` | This is the alarming part | `--sig`, orange |
| `cyan` | This part is already working | `--cyan` |
| `code` / `mono` | A path, an identifier, a command | `--warn`, amber |

## Section card

An orange full-bleed card that opens a new part of the argument.

```html
<div class="slide-content" style="align-items:flex-start">
  <div class="section-card reveal">
    <p class="sfor">[WHAT THIS SECTION FEEDS]</p>
    <div class="sn">01</div>
    <h2>[The section's claim<br>in two short lines]</h2>
    <p>[One supporting sentence.]</p>
  </div>
</div>
```

`align-items:flex-start` on the content is what stops the card stretching to
the full width. One per section; four in a nine-slide deck is wallpaper.

## Data table

```html
<table class="data reveal">
  <thead><tr><th>[COLUMN]</th><th>[COLUMN]</th><th style="text-align:right">[NUMBER]</th></tr></thead>
  <tbody>
    <tr><td class="k">[Row label]</td><td>[Plain reading]</td><td class="num">000</td></tr>
    <tr><td class="m">[/path/or/identifier]</td><td>[Plain reading]</td><td class="num">000</td></tr>
    <tr class="flag"><td class="k">[The problem row]</td><td><span class="sig">[Why]</span></td><td class="num">000</td></tr>
    <tr class="good"><td class="k">[The working row]</td><td>[Why]</td><td class="num">000</td></tr>
  </tbody>
</table>
```

- `td.k` is the key column — full white. `td.m` is monospace, for paths and
  identifiers. `td.num` is Archivo Black, right-aligned, `white-space:nowrap`.
- `tr.flag` tints the whole row orange; `tr.good` tints it cyan. A table where
  every row is flagged has flagged nothing.
- Right-align the header cell of a numeric column by hand
  (`style="text-align:right"`); only the `td` picks it up from the class.

## Split and split3 cards

```html
<div class="split reveal">
  <div class="card"><div class="ct">[WHAT WAS CLAIMED]</div><div class="cn">000</div><div class="cd">[Where it comes from.]</div></div>
  <div class="card bad"><div class="ct">[WHAT IS THERE]</div><div class="cn">0,000</div><div class="cd">[Why this is the one to trust.]</div></div>
</div>
```

`.bad` is orange, `.good` is cyan, a plain `.card` is neutral. `.split3` takes
three; both collapse to one column under 820px.

When `.cn` holds text rather than a figure, override the display size inline
and switch to mono — a long label at 3.2rem Archivo Black overruns the card:

```html
<div class="cn" style="font-size:clamp(.9rem,2.1vw,1.5rem);letter-spacing:0;font-family:var(--font-mono)">[short<br>label]</div>
```

## Mega number

```html
<div class="reveal" style="display:flex;flex-direction:column;gap:.45rem">
  <div class="mega">0,000</div>
  <p class="mega-note">[What it counts, over what period, from which source.]</p>
</div>
```

The wrapper is the reveal, so the number and its note arrive together. Add
`.compact` to `.mega` for a figure long enough to wrap at the full size. A mega
number with no provenance in its note is decoration.

## Stat row

```html
<div class="statrow reveal">
  <div class="stat accent"><div class="n">0,000</div><div class="l">[what it counts,<br>over what period]</div></div>
  <div class="stat warn"><div class="n">00s</div><div class="l">[the worrying figure]</div></div>
  <div class="stat cyan"><div class="n">00%</div><div class="l">[the healthy figure]</div></div>
  <div class="stat"><div class="n">0</div><div class="l">[the missing figure]</div></div>
</div>
```

The modifier colours the rule above the number and the number itself: `.accent`
orange, `.cyan` cyan, `.warn` amber, none for neutral. Four fit; six wrap and
stop being scannable.

## Verdict bar

The deck's full stop. One per slide at most.

```html
<div class="verdict reveal">[The sentence you want remembered.]</div>
<div class="verdict cyan-v reveal">[Something already settled — cyan means resolved.]</div>
<div class="verdict dark reveal">[A quieter closing note.]</div>
```

## Spec list

```html
<div class="specs">
  <div class="spec reveal"><span class="si">01</span><span class="st">[The requirement as an instruction]<em>[The measurement that justifies it]</em></span></div>
</div>
```

`<em>` is restyled as a block sub-line, not italics. This is the slide that gets
copied into a specification document, so write each `.st` as something a
developer can act on without the deck.

## Numbered points

```html
<ul class="pts">
  <li data-n="Q1" class="reveal"><span class="hl">[The question.]</span> [What it decides.]</li>
</ul>
```

`data-n` is the marker, drawn by `::before`, so it can be `Q1`, `01`, `—`, or
anything short. Each `<li>` is its own reveal; five is the comfortable maximum.

## Chrome — do not rewrite

- The controller is one class at the foot of the file: an `IntersectionObserver`
  adds `.visible` (which fires the reveals), plus keyboard, touch, progress and
  nav dots. It reads `document.querySelectorAll('.slide')`, so it follows the
  slide count on its own — never hand-write nav dots.
- `html{scroll-snap-type:y mandatory}` with `body{overflow:hidden}` is what
  makes the deck snap. Both are load-bearing.
- `.slide` and `.slide-content` both clip. An overflowing slide loses its bottom
  silently rather than scrolling, so check every slide at 375px wide and at
  600px tall.
- `font-feature-settings:"tnum"` on `body` is what keeps columns of digits
  aligned — Archivo Black has no tabular figures of its own.

## Colophon — the maker's credit

The closing slide ends with the credit line, in the deck's own micro type. It
ships by default; remove the second `<a>` (only) when the intake answered
`credit: false` — the `monomind ai lab` link before it belongs to the `logo`
answer, not to this one. The product name is wrapped `notranslate` so a
reader's browser translation leaves it alone.

```html
<p class="colophon reveal">
  <a href="https://monomind.one/?ref=deck-mark" target="_blank" rel="noopener noreferrer">monomind ai lab</a>
  <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer">Made with <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span></a>
</p>
```

## Dependencies

Google Fonts only — Archivo Black, Space Grotesk, JetBrains Mono. No diagram
runtime, no CDN library, nothing inline but the deck itself. `delivery:
standalone` means subsetting and inlining those three families.

There is no print stylesheet. A scroll-snap deck of `100dvh` sections prints as
one slide per page only by accident; answering `export: pdf` on this template
means writing the `@media print` block, not enabling one.
