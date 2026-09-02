# Paper brief — component reference

Markup for `assets/tedandlisa-template-paper-brief.html`. A light scroll-snap
deck that reads like a printed briefing paper: white ground under a faint
twelve-column grid, Archivo over Noto Sans TC, red and blue doing the arguing,
and chapter pages that invert to near-black so a long report has visible seams.

**Density — a `read` template, in slide shape.** Read at desk distance and
forwarded, so four to eight items on a page is fine — an eight-row table, a
bar chart of six, a spec list of eight — and one conclusion per page rather
than one idea. It is still a page that clips, so the count is bounded by
375px wide and 600px tall in both languages, not by a projector.

Use it when the deck will be read at desk distance and forwarded — a planning
input, a review, a recommendation someone prints. Use `evidence-deck` when the
same argument has to survive a projector, and `web-document` when it wants a
URL per section.

## Language — Traditional Chinese and English, written inline

The house inline-bilingual mechanism: both languages are written into the
markup and one of them is hidden by CSS. No translation service, so the switch
is instant and the file still opens with no network.

**The pair is `zh-TW` + `en`, and `zh-TW` is what it opens in.** `D-010` makes
English and Korean the default pair for the inline-bilingual shapes, but this
template already had a language when it arrived: Traditional Chinese is half
its type system — `Noto Sans TC` is not decoration here, it is the body face —
and deleting it to satisfy a default would throw away the identity the template
exists to carry. English is the second language because English is the one
language `languages` always ships. Korean is an addition like any other: a
third set of spans, a third button, and `Noto Sans KR` appended to both stacks.

```css
body[data-lang="zh-TW"] .en{display:none !important}
body[data-lang="en"] .zh{display:none !important}
/* Latin body copy moves to Archivo, so English is set in the same family as
   the display face rather than in the Latin of a CJK font. */
body[data-lang="en"]{--font-body:'Archivo','Noto Sans TC',sans-serif}
```

```html
<p class="lead reveal"><span class="zh">[中文句子。]</span><span class="en">[The English sentence.]</span></p>
```

Four things that go wrong:

- **A string written once shows in both languages.** No fallback, no warning.
  Table cells, bar labels, card headings, the `data-label-*` menu names and the
  署名 all need the pair.
- **The spans go INSIDE the reveal, never around it.** The stagger is
  `nth-child`; a language span wrapped around a reveal steals its delay.
- **English is longer than Chinese, and the pages clip.** `.slide` and
  `.slide-content` both `overflow:hidden`, so a page that fits in Chinese can
  lose its bottom in English without a scrollbar to say so. Check every page in
  both languages at 375px wide and 600px tall.
- **Mixed CJK and Latin numerals are the point.** `font-feature-settings:"tnum"`
  on `body` keeps the Latin figures aligned inside CJK sentences, in both
  languages.

A term that must survive translation — a product name, a command, an identifier
— is written **identically in both spans** and wrapped
`<span class="notranslate" translate="no">`. That is what the `noTranslate`
answer means here; see the answers section at the foot.

Dropping a language means deleting its spans *and* its button; every control is
guarded in the script, so nothing breaks when one is gone.

## The shape of a slide

`data-label-zh` / `data-label-en` are what the 目錄 menu lists.

```html
<section class="slide" data-label-zh="[頁面名稱]" data-label-en="[PAGE NAME]">
  <div class="slide-content">
    <p class="eyebrow reveal"><span class="zh">[這一頁在談什麼]</span><span class="en">[WHAT THIS PAGE IS ABOUT]</span></p>
    <h2 class="reveal"><span class="zh">[把結論寫成一句話]</span><span class="en">[The conclusion, as a sentence]</span></h2>
    <p class="body reveal"><span class="zh">[支持這個結論的一段話。]</span><span class="en">[The paragraph that supports it.]</span></p>
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

## The chrome — mark, language switch, menu

One fixed cluster at the top right, clear of the nav dots (right edge, centred)
and the page number (bottom left). `--chrome-clear` is the headroom every page
leaves for it: `.slide` sets `padding-top:max(var(--slide-padding),
var(--chrome-clear))`. That is also what keeps the title pages' red rule below
the cluster on a narrow screen, where `--slide-padding` bottoms out at 1.4rem.

```html
<div class="deck-chrome">
  <!-- logo -->
  <a class="deck-mark" href="https://monomind.one/?ref=deck-mark" target="_blank" rel="noopener noreferrer" aria-label="MonoMind">
    <svg viewBox="0 0 512 512" fill="currentColor" aria-hidden="true"><!-- the mark's two paths --></svg>
  </a>

  <!-- languages -->
  <div class="seg" role="group" id="langSeg" aria-label="語言">
    <button type="button" id="btnZh" aria-pressed="true">繁中</button>
    <button type="button" id="btnEn" aria-pressed="false">EN</button>
  </div>

  <!-- menu: "full" -->
  <nav class="deck-menu" id="deckMenu" data-open="false">
    <button class="deck-menu-btn" type="button" id="deckMenuBtn"
            aria-expanded="false" aria-controls="deckMenuPanel" aria-label="選單">
      <span></span><span></span><span></span>
    </button>
    <div class="deck-menu-panel" id="deckMenuPanel" role="menu" aria-labelledby="deckMenuBtn">
      <button type="button" role="menuitem" id="deckMenuStart">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 17.5 11 12l7-5.5v11Z" fill="currentColor" stroke="none"/><path d="M6.5 6v12"/></svg>
        <span class="zh">回到第一頁</span><span class="en">Back to the start</span>
      </button>
      <button type="button" role="menuitem" id="deckMenuContents" aria-expanded="false" aria-controls="deckContents">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
        <span class="zh">目錄</span><span class="en">Contents</span>
      </button>
      <div class="deck-menu-sub" id="deckContents" role="none" hidden></div>
      <button type="button" role="menuitem" id="deckMenuLang">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 3 2.6 15 0 18M12 3c-2.6 3-2.6 15 0 18"/></svg>
        <span class="zh">Read in English</span><span class="en">改看繁體中文</span>
      </button>
    </div>
  </nav>
</div>
```

**目錄 is generated, never hand-written.** The script walks
`document.querySelectorAll('.slide')` and builds one button per page from its
`data-label-zh` / `data-label-en`, writing *both* spans so the language switch
moves the menu too. It cannot drift out of sync with the page list.

**Applying the `menu` answer is deleting markup, not editing script.** Every
control is looked up by id and guarded:

| Answer | What to do |
| --- | --- |
| `menu: full` | Ships as above. |
| `menu: minimal` | Delete `<nav class="deck-menu">` and put one back-to-the-start button in the cluster, wired to `window.__deckGo(0)`. |
| `menu: none` | Delete `<nav class="deck-menu">`. The language segment is a different answer and stays. |
| `menu.items` without `contents` | Delete `#deckMenuContents` and `#deckContents`. |
| `menu.items` without `language` | Delete `#deckMenuLang`; the chrome segment is unaffected. |
| `menu.items` with `home` / `github` | Both ship commented out, because their URLs default to `null` and an item pointing nowhere is worse than no item. Uncomment and set a real `href`. |
| `menu.items` with `html` | Also commented out; uncomment it to ship the self-download. |

Three keyboard details, already handled — do not undo them:

- **One capture-phase `keydown` listener on `.deck-chrome` stops propagation.**
  The controller listens on `document`, so without it a Space press on a
  focused chrome button would be swallowed by the controller's `preventDefault`
  and turn the page instead. `stopPropagation` does not cancel a default
  action, so Enter and Space still activate the buttons.
- **Escape closes the menu and returns focus to the hamburger**; Arrow
  Up/Down/Home/End rove between the open panel's `[role="menuitem"]`s.
- **Nothing here reimplements scrolling.** `window.__deckGo(i)` is published by
  the controller's own last two lines.

## Chrome — do not rewrite

- The controller is one class at the foot of the file — `IntersectionObserver`
  for `.visible`, plus keyboard, touch, progress bar and nav dots. It counts
  `.slide` itself; never hand-write dots.
- The class body is untouched from the source system. Its only extension is the
  last two lines, publishing `window.__deckGo` so the menu reuses `goTo`. New
  behaviour goes in a **new script block**.
- `html{scroll-snap-type:y mandatory}` with `body{overflow:hidden}` is the snap.
  A consequence worth knowing when measuring: **`body` is the scroller, not
  `documentElement`** — a check reading `document.scrollingElement.scrollTop`
  reports 0 forever.
- `.slide` and `.slide-content` both clip: an overflowing page loses its bottom
  in silence. Check every page at 375px wide and 600px tall, in both languages.
- The grid field is `background-size:calc(100vw/12)`, so it is genuinely twelve
  columns at any width. Chapter pages switch it off; nothing else should.

## Colophon — the maker's credit

The closing page's meta row carries the credit as its last item, in the row's
own micro type. It ships by default; remove that last `<span>` (only) when the
intake answered `credit: false` — the `monomind ai lab` span before it belongs
to the `logo` answer. It is written once per language — the Chinese form keeps
its Chinese wording — with the product name identical in both and wrapped
`notranslate` so a reader's browser translation leaves it alone.

```html
<span><a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer"><span class="zh">以 <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span> 製作</span><span class="en">Made with <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span></span></a></span>
```

## The intake answers this template cannot take at face value

Four answers reach a `slides` template whose wording assumes `monomind-deck`.
What each one actually means here:

- **`backgrounds`.** Its default reads "the two images already embedded in the
  template". **Nothing is embedded here** — this brief is paper and type — so
  `monomind` and `gradient` produce the same file. `upload` is real: put the
  data URI on the cover and closing pages and the white scrim keeps the type
  legible.

  ```html
  <section class="slide title-slide" data-bg style="--bg-img:url(data:image/jpeg;base64,…)">
  ```
- **`noTranslate`.** The question is written for Google Translate, which this
  template does not use — but the list still applies twice over. Every term on
  it must be written **identically in both language spans**, and wrapped
  `<span class="notranslate" translate="no">` so a reader's own browser
  translation leaves it alone.
- **`theme`.** The question's hint says "It ships dark". **This one ships
  light** — white paper is the template, not a setting — so `theme: light` is
  the no-op and `theme: dark` is the work. The tokens now cover the whole
  ground, including the ones that used to be hardcoded: `--track` (the bar
  channel), `--decision-bg`, and `--invert-bg` / `--invert-ink` /
  `--invert-soft` for the chapter pages, which are already the inverse and must
  invert *back* if the deck goes dark. **`theme: toggle` is not supported**: a
  runtime switch would need a second full palette reviewed on every page,
  chapter inversions included. Say so rather than shipping a half switch.
- **`export`.** It does not ship. `html` is a few lines (clone the
  document, clear the generated 目錄, Blob it).

## Dependencies

Google Fonts only — Archivo (300 through 900; the 300 is what English body copy
is set in) and Noto Sans TC. `delivery: standalone` inlines both, and Noto Sans
TC is the expensive half: subset it to the glyphs the deck actually uses or the
file gains several megabytes.

There is no print stylesheet.

## When unsure, default to

- **A text page:** `.eyebrow` + the conclusion in `h2` + one `.body` paragraph.
- **Proportions:** `.bars`, scaled to the largest value; one figure: `.mega`;
  two compared: `.split`.
- **Evidence:** `table.data` with one `tr.flag`.
- **A seam in a long report:** a chapter page.
- **An ending:** `.decision`, with a verb in `.da`.
- **Requirements:** `.specs`; questions: `.pts`.
- **Emphasis:** `hl`; `red` only for the problem.

## Known gaps

Evidenced, not imagined — each line names its record.

- **There is no fail-visible path for `.reveal`.** Content becomes visible
  only when the controller's `IntersectionObserver` adds `.visible`; the
  sole unconditional reveal is the `prefers-reduced-motion` block, and there
  is no `@media print` block. Anywhere the observer never fires — a hidden
  tab, a print preview — the page is structurally perfect and visually
  empty (`L-022`).
- **No print stylesheet, on the template whose `best_for` says "a
  recommendation someone prints"** (`templates/templates.json`; Dependencies
  above). Printing is the browser's own, and a scroll-snap deck of `100dvh`
  pages paginates only by accident.
- **English is longer than Chinese, and the pages clip.** `.slide` and
  `.slide-content` both `overflow:hidden`, so a page that fits in Chinese
  can lose its bottom in English with no scrollbar to say so — check both
  languages at 375px wide and 600px tall.
- **`theme: dark` is the work and `theme: toggle` is not supported** (the
  answers section above): the chapter pages are already the inverse and
  must invert *back*.
- **Noto Sans TC is the expensive half under `delivery: standalone`** —
  several megabytes unsubsetted — and a subset holds only the glyphs rendered
  at build time (`references/applying-answers.md`,
  `references/cjk-typography.md`).
- **`.pagenum` is hand-written**, and the title and closing pages carry none;
  renumber the rest by hand after any edit.
