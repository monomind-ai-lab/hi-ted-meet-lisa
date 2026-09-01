# Evidence deck — component reference

Markup for `assets/tedandlisa-template-evidence-deck.html`. A dark, full-bleed
scroll-snap deck for an argument made out of measurements: tables that flag
their own bad rows, stat rows, one number at display size, and a bar of orange
that says what to do about it.

Use it when the deck's job is to make a case from data someone will push back
on. Use `monomind-deck` when the job is a talk, and `web-document` when the
reader will link to it rather than sit through it.

It carries the two features every template here is expected to have: **English
and Korean written inline** and toggled by CSS (`D-010`), and a **full menu** —
a hamburger beside the brand mark that lists the slides and jumps to them.

## Language — both written inline

The house mechanism, the same one `web-document`, `architecture` and
`mermaid-master` use: every reader-visible string is written twice and one of
them is hidden. No translation service, so the switch is instant, the file
still opens from a USB stick, and text inside a component translates the same
way a heading does.

```css
body[data-lang="en"] .ko{display:none !important}
body[data-lang="ko"] .en{display:none !important}
```

```html
<p class="lead reveal"><span class="en">[The English sentence.]</span><span class="ko">[한국어 문장.]</span></p>
```

Four things that go wrong:

- **A string written once shows in both languages.** There is no fallback and
  no warning. Table cells, card labels, bar labels, the `data-label-*` menu
  names and the colophon all need the pair.
- **The spans go INSIDE the reveal, never around it.** The stagger is
  `nth-child` on `.slide-content`; wrapping a reveal in a language span moves
  every delay after it.
- **Archivo Black and Space Grotesk carry no Hangul.** Noto Sans KR is
  *appended* to both stacks rather than replacing them, so Latin and digits
  stay in the deck's own faces and only the Hangul falls through. The paired
  `font-weight:900` rule stops the fallback reading light beside Archivo Black.

  ```css
  body[data-lang="ko"]{
    --font-display:'Archivo Black','Noto Sans KR',sans-serif;
    --font-body:'Space Grotesk','Noto Sans KR',sans-serif;
  }
  body[data-lang="ko"] h1,body[data-lang="ko"] h2,body[data-lang="ko"] .verdict,
  body[data-lang="ko"] .section-card .sn,body[data-lang="ko"] .mega{font-weight:900}
  ```
- **A term that must survive translation is written identically in both spans**
  and wrapped `<span class="notranslate" translate="no">`. That is what the
  `noTranslate` answer is for here — see the answers table at the foot.

Dropping a language means deleting its spans *and* its button; the script
guards every control, so nothing breaks when one is gone.

## The shape of a slide

Every slide is the same three-part frame. `.slide` is the snap target and the
grid field; `.slide-content` is the flex column that staggers; `.pagenum` sits
outside the content so it does not join the stagger. `data-label-en` /
`data-label-ko` are what the menu lists.

```html
<section class="slide" data-label-en="[SLIDE NAME]" data-label-ko="[슬라이드 이름]">
  <div class="slide-content">
    <p class="eyebrow reveal"><span class="en">[WHAT THIS SLIDE IS]</span><span class="ko">[이 슬라이드가 무엇인지]</span></p>
    <h2 class="reveal"><span class="en">[The claim as a sentence]</span><span class="ko">[주장을 한 문장으로]</span></h2>
    <p class="body reveal"><span class="en">[The supporting paragraph.]</span><span class="ko">[뒷받침하는 단락.]</span></p>
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

## The chrome — mark, language switch, menu

One fixed cluster at the top right, clear of the nav dots (right edge, centred)
and the page number (bottom left). `--chrome-clear` is the headroom every slide
leaves for it: `.slide` sets `padding-top:max(var(--slide-padding),
var(--chrome-clear))`, so nothing tucks underneath at narrow widths or on a
short screen.

```html
<div class="deck-chrome">
  <!-- logo -->
  <a class="deck-mark" href="https://monomind.one/?ref=deck-mark" target="_blank" rel="noopener noreferrer" aria-label="MonoMind">
    <svg viewBox="0 0 512 512" fill="currentColor" aria-hidden="true"><!-- the mark's two paths --></svg>
  </a>

  <!-- languages -->
  <div class="seg" role="group" id="langSeg" aria-label="Language">
    <button type="button" id="btnEn" aria-pressed="true">EN</button>
    <button type="button" id="btnKo" aria-pressed="false">한국어</button>
  </div>

  <!-- menu: "full" -->
  <nav class="deck-menu" id="deckMenu" data-open="false">
    <button class="deck-menu-btn" type="button" id="deckMenuBtn"
            aria-expanded="false" aria-controls="deckMenuPanel" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <div class="deck-menu-panel" id="deckMenuPanel" role="menu" aria-labelledby="deckMenuBtn">
      <button type="button" role="menuitem" id="deckMenuStart">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 17.5 11 12l7-5.5v11Z" fill="currentColor" stroke="none"/><path d="M6.5 6v12"/></svg>
        <span class="en">Back to the start</span><span class="ko">처음으로</span>
      </button>
      <button type="button" role="menuitem" id="deckMenuContents" aria-expanded="false" aria-controls="deckContents">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
        <span class="en">Contents</span><span class="ko">목차</span>
      </button>
      <div class="deck-menu-sub" id="deckContents" role="none" hidden></div>
      <button type="button" role="menuitem" id="deckMenuLang">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 3 2.6 15 0 18M12 3c-2.6 3-2.6 15 0 18"/></svg>
        <span class="en">한국어로 보기</span><span class="ko">Read in English</span>
      </button>
    </div>
  </nav>
</div>
```

**Contents is generated, never hand-written.** The script walks
`document.querySelectorAll('.slide')` and builds one button per slide from its
`data-label-en` / `data-label-ko`, writing *both* spans so the language switch
moves the menu too. It cannot drift out of sync with the deck; a hand-written
list can.

**Applying the `menu` answer is deleting markup, not editing script.** Every
control is looked up by id and guarded:

| Answer | What to do |
| --- | --- |
| `menu: full` | Ships as above. |
| `menu: minimal` | Delete `<nav class="deck-menu">` and put a single back-to-the-start button in the cluster wired to `window.__deckGo(0)`. |
| `menu: none` | Delete `<nav class="deck-menu">`. The language segment is a separate answer and stays. |
| `menu.items` without `contents` | Delete `#deckMenuContents` and `#deckContents`. |
| `menu.items` without `language` | Delete `#deckMenuLang`. The chrome segment is unaffected. |
| `menu.items` with `home` / `github` | The template ships those two commented out, because their URLs default to `null` and an item pointing nowhere is worse than no item. Uncomment and set a real `href`. |
| `menu.items` with `html` | Also commented out — uncomment it to ship the self-download. |

Three traps in the keyboard behaviour, all of them already handled — do not
undo them:

- **One capture-phase `keydown` listener on `.deck-chrome` stops propagation.**
  The controller listens on `document`, so without it a Space press on a
  focused chrome button would be eaten by the controller's `preventDefault`
  and move the deck instead of pressing the button. `stopPropagation` does not
  cancel a default action, so Enter and Space still activate the buttons.
- **Escape closes the menu and returns focus to the hamburger**; Arrow
  Up/Down/Home/End rove between the open panel's `[role="menuitem"]`s.
- **Nothing here reimplements scrolling.** `window.__deckGo(i)` is published by
  the controller's own last two lines and is the only way the menu moves the
  deck.

## Chrome — do not rewrite

- The controller is one class at the foot of the file: an `IntersectionObserver`
  adds `.visible` (which fires the reveals), plus keyboard, touch, progress and
  nav dots. It reads `document.querySelectorAll('.slide')`, so it follows the
  slide count on its own — never hand-write nav dots.
- The class body is untouched from the source system. The only extension is its
  last two lines, which publish `window.__deckGo` so the menu can reuse `goTo`
  instead of writing new scroll code. Add behaviour in a **new script block**.
- `html{scroll-snap-type:y mandatory}` with `body{overflow:hidden}` is what
  makes the deck snap. Both are load-bearing. Note the consequence when
  measuring: **`body` is the scroller, not `documentElement`** — a check that
  reads `document.scrollingElement.scrollTop` will report 0 forever.
- `.slide` and `.slide-content` both clip. An overflowing slide loses its bottom
  silently rather than scrolling, so check every slide at 375px wide and at
  600px tall, **in both languages** — Korean and English do not wrap alike.
- `font-feature-settings:"tnum"` on `body` is what keeps columns of digits
  aligned — Archivo Black has no tabular figures of its own.

## Colophon — the maker's credit

The closing slide ends with the credit line, in the deck's own micro type. It
ships by default; remove the second `<a>` (only) when the intake answered
`credit: false` — the `monomind ai lab` link before it belongs to the `logo`
answer, not to this one. It is written once per language, with the product name
identical in both and wrapped `notranslate` so a reader's browser translation
leaves it alone; "Made with" is meant to translate.

```html
<p class="colophon reveal">
  <a href="https://monomind.one/?ref=deck-mark" target="_blank" rel="noopener noreferrer">monomind ai lab</a>
  <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer"><span class="en">Made with <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span></span><span class="ko"><span class="notranslate" translate="no">Hi Ted, Meet Lisa</span>로 제작</span></a>
</p>
```

## The intake answers this template cannot take at face value

Four answers reach a `slides` template whose wording assumes `monomind-deck`.
What each one actually means here:

- **`backgrounds`.** Its default reads "the two images already embedded in the
  template". **Nothing is embedded here** — this deck is typographic, and
  `monomind` and `gradient` therefore produce the same file. `upload` is real:
  put the data URI on the cover and closing sections and the scrim keeps the
  type legible.

  ```html
  <section class="slide" data-bg style="--bg-img:url(data:image/jpeg;base64,…)">
  ```
- **`noTranslate`.** The question is written for Google Translate, which this
  template does not use — but the list still applies twice over. Every term on
  it must be written **identically in both language spans** (a product name
  that is "translated" between the pair is the same bug by another route), and
  wrapped `<span class="notranslate" translate="no">` so a reader's own browser
  translation leaves it alone.
- **`theme`.** The question's hint says "It ships dark", and this template does
  — `--bg`, `--panel`, `--fg` and friends are the whole ground. `theme: dark`
  is a no-op. `theme: light` is a token swap at the top of the file, and the
  tokens now cover it: `--on-sig` is the ink that sits on the signal colour, so
  the section card and the verdict bar follow the palette instead of a
  hardcoded `#141414`. **`theme: toggle` is not supported**: a second full
  palette would have to be reviewed on every slide, and this deck ships one.
  Say so rather than shipping a switch that half works.
- **`export`.** It does not ship. `html` is a few lines (clone the
  document, clear the generated contents, Blob it).

## Dependencies

Google Fonts only — Archivo Black, Space Grotesk, JetBrains Mono, and Noto Sans
KR for the Hangul. No diagram runtime, no CDN library, nothing inline but the
deck itself. `delivery: standalone` means subsetting and inlining those four
families; Noto Sans KR is the expensive one.

There is no print stylesheet. A scroll-snap deck of `100dvh` sections prints as
one slide per page only by accident.
