# Motion website — component reference

Markup for `assets/tedandlisa-template-motion-website.html`. Every snippet is
lifted from the skeleton, so it is known-good. Compose from these; do not invent
class names.

This template is `project-website` with the **motion layer** applied: the same
tokens, chrome, router, footer and language mechanism, plus seven
dependency-free animation patterns from `references/motion-patterns.md` —
CSS and the Web Animations API only, nothing loaded (`D-015`). Every
component below is the project-website one; the "Motion" section at the end
says what moves, where, and how to switch any of it off.

It is a **website**, not a deck and not a single page: several pages are
hash-routed behind a sticky nav, each page scrolls, one footer is shared by
all of them, and both languages are written into the file rather than translated
at read time.

Reach for it when the deliverable is a project's public face that should feel
alive on the first screen — a launch page, a tool's home, a programme's site —
and reach for `project-website` when it should not move at all.

## The three registers that must agree

A page exists only if all three name it. Miss one and it is unreachable:

1. `<section class="page" id="page-ID">`
2. `data-page="ID"` on a nav entry — in **both** the desktop `.nav-links` list
   and the `.nav-mobile` list, which are separate DOM
3. an entry in the `PAGES` array at the head of the script

`apply()` drives both nav lists from one loop, so their active states cannot
drift — but only over the entries you actually added to each. A page reached
through the More dropdown is named in a fourth place too, `DROP_PAGES`, which
is only what lights the dropdown button as current — omitting it costs the
highlight, not the page.

## Page shell

```html
<section class="page" id="page-ID">
  <section class="section">
    <div class="container">
      <div class="sec-head reveal">
        <span class="eyebrow"><span class="eyebrow-num">01</span> <span class="en">EYEBROW</span><span class="ko">라벨</span></span>
        <h2 class="section-title"><span class="en">HEADLINE.</span><span class="ko">제목.</span></h2>
        <p class="section-lede"><span class="en">Lede.</span><span class="ko">리드.</span></p>
      </div>
      <!-- content -->
    </div>
  </section>
</section>
```

`.section` is one vertical band; `.container` centres content at 1120px.
`.sec-head-row` is the variant with a button pinned to the right. Separate two
bands with `<hr class="hairline">`.

## Bilingual text — the rule that governs everything

Every reader-visible string carries **both** languages as sibling spans:

```html
<span class="en">English text</span><span class="ko">한국어 텍스트</span>
```

`body[data-lang]` hides one set. Consequences to respect:

- **Never write a bare string** in page content. A string without an `.en`/`.ko`
  pair shows in both languages and looks like a bug.
- No whitespace between the two spans, or the hidden one leaves a gap.
- Identifiers that must not be translated — the project name, commands,
  filenames, the names in the compatibility strip — are written **once, outside
  any language span**, when they stand alone. There is no translation service to
  defend against, which is why this template needs no `notranslate`.
- **An identifier inside a sentence is the exception.** An inline `<code>` or
  `<strong>` must sit *inside* each language span, not between them. An element
  between `.en` and `.ko` belongs to neither, so nothing hides it and the reader
  sees it twice — once in each language's sentence. Write it once per language:

  ```html
  <p><span class="en">Run <code class="inline-cmd">/build</code> first.</span><span class="ko"><code class="inline-cmd">/build</code>를 먼저 실행하세요.</span></p>
  ```

  This is worth grepping for: `</span><code` and `</span><strong` in page
  content are almost always this bug.
- Nav labels, buttons, card footnotes, and footer columns all follow the rule.

## Reveal on scroll

Any block can carry `.reveal` and it fades up when scrolled to — this is the
project-website mechanism, kept as it is. The motion layer adds a second one,
`.lm-reveal` / `.lm-on`, driven by the `lm` runtime; the two coexist and an
element carries **one** of them, never both (see Motion). Two things to know
about `.reveal`:

- A page that has never been routed to has never been laid out, so its `.reveal`
  elements never intersected anything. `armReveal()` therefore runs on **every**
  page activation, not once at load. This is why adding a page needs no extra
  wiring.
- `.reveal` starts at `opacity:0`, so a context that never delivers
  IntersectionObserver callbacks would render a blank page. `armReveal()` carries
  a fail-visible timer: if nothing in the page has been reported after a beat,
  it reveals everything. Do not remove it — print preview and headless capture
  both depend on it.

## Copy-to-clipboard command

```html
<div class="cmd cmd-lg" data-copy-root>
  <div class="cmd-body">
    <span class="cmd-prompt" aria-hidden="true">$</span>
    <code class="cmd-text" data-copy-text>npm install thing</code>
    <button class="cmd-btn" data-copy-btn aria-label="Copy: npm install thing">
      <svg class="i-copy" …></svg>
      <svg class="i-check" …></svg>
    </button>
  </div>
</div>
```

- The three attributes are a set: `-root` is the container queried at load,
  `-text` is the string copied, `-btn` is what flips to the tick.
- `data-copy-text` is the **single source of truth**. The `aria-label` repeats
  it for screen readers; change both or the announcement lies.
- Both SVGs must stay: `.copied` swaps which one displays.
- Sizes are `.cmd-sm`, default, and `.cmd-lg`. `.cmd-label` above the body is
  optional and takes a bilingual pair.
- The textarea fallback in the script is what makes copy work from `file://`,
  where the clipboard API is unavailable. Do not tidy it away.

## Cards

```html
<div class="cards-grid">
  <a class="card item-card" style="--h:205" onclick="go('docs')">
    <div class="ic-top">
      <span class="chip phase-chip"><span class="phase-dot"></span><span class="en">Category</span><span class="ko">분류</span></span>
      <span class="ic-cmd mono">/cmd</span>
    </div>
    <h3 class="ic-name mono">item-name</h3>
    <p class="ic-summary"><span class="en">One sentence.</span><span class="ko">한 문장.</span></p>
    <div class="ic-foot">
      <span class="ic-when"><span class="en">When to use it.</span><span class="ko">언제 쓰는지.</span></span>
      <span class="ic-arrow" aria-hidden="true"><svg …></svg></span>
    </div>
  </a>
</div>
```

`--h` is the category hue and is the **only** colour you set: one number tints
the dot, the chip, the card's hover edge, and its arrow. Never paint those
separately — they will drift apart in the light theme. Drop `.ic-cmd` for a card
with no command. The grid goes 3 → 2 → 1 column.

## Pillars, split layout, people

```html
<div class="pillars">
  <article class="card pillar">
    <div class="pillar-icon"><svg …></svg></div>
    <span class="pillar-tag mono"><span class="en">TAG</span><span class="ko">태그</span></span>
    <h3 class="pillar-title">…</h3>
    <p class="pillar-body">…</p>
  </article>
</div>

<div class="split-layout">
  <div class="reveal"><!-- argument, ending in a .split-cta button --></div>
  <div class="people-grid reveal">
    <div class="card person-card">
      <div class="person-head">
        <span class="person-avatar" aria-hidden="true">AB</span>
        <div><h3 class="person-name mono">name</h3><span class="person-role">…</span></div>
      </div>
      <p class="person-note">…</p>
    </div>
  </div>
</div>
```

`.person-card` is not only for people — it is the compact "named thing plus a
line about it" card. Use `.inline-cmd` for a command mentioned inside prose.

## Process track

```html
<div class="lifecycle-wrap">
  <div class="lifecycle" role="img" aria-label="DESCRIBE THE DIAGRAM">
    <div class="lc-track" aria-hidden="true"></div>
    <ol class="lc-steps">
      <li class="lc-step" style="--h:205">
        <span class="lc-phase">…</span>
        <div class="lc-node"><span class="lc-verb">…</span><span class="lc-sub">…</span></div>
        <code class="lc-cmd">/cmd</code>
      </li>
    </ol>
  </div>
</div>
```

Six steps. The animated track is positioned for six and its spacing has to be
re-tuned for any other count; the grid drops to three columns at 720px and two
at 420px. The `role="img"` label is the only description a screen reader gets —
write it.

## Register table

```html
<div class="cmd-table">
  <a class="cmd-row" onclick="go('docs')">
    <code class="cmd-row-cmd">/cmd</code>
    <span class="cmd-row-doing">…</span>
    <span class="cmd-row-principle">…</span>
  </a>
</div>
```

Two columns of rows on desktop, one on mobile, where `.cmd-row-principle` is
dropped — put nothing there that the reader must see. Use a `div.cmd-row` for a
row that does not navigate. The command column is a fixed track: a command
longer than it (`tedandlisa_thumbs.py`) wraps inside the column via
`overflow-wrap:anywhere` on `.cmd-row-cmd` rather than running into the
description — do not remove that declaration to "fix" the wrap.

## Callout

```html
<div class="callout"><b><span class="en">Note.</span><span class="ko">참고.</span></b> <span class="en">…</span><span class="ko">…</span></div>
```

The one component the source design did not have, added because a project site
always needs to say "note this". Built from existing tokens only.

## Step list

```html
<ol class="steps">
  <li class="step">
    <h4>…</h4>
    <p>…</p>
    <div class="cmd cmd-sm" data-copy-root>…</div>
  </li>
</ol>
```

The number is a CSS counter, so inserting or deleting a step renumbers the
rest. A step with no command simply has no `.cmd` block — do not invent one to
fill the space.

## Table

```html
<div class="tblwrap"><table class="tbl">
  <thead><tr><th>Column</th></tr></thead>
  <tbody><tr>
    <td>Row</td>
    <td><span class="pill pill-ok">yes</span></td>
    <td><code>value</code></td>
  </tr></tbody>
</table></div>
```

Always keep `.tblwrap`: it is what makes a wide table scroll itself instead of
the page. Pills are `.pill-ok` (green), `.pill-warn` (amber), `.pill-no`
(faint). A comparison in which nothing loses is not read as a comparison — put
a real `.pill-no` in your own column.

## Checklist

```html
<ul class="chk">
  <li class="done"><span class="cid">C-01</span>Done.</li>
  <li><span class="cid">C-02</span>Outstanding.</li>
</ul>
```

`.chk` renders ☐ / ☑ from `li.done`. Drop the `.cid` if nothing refers to these
by id.

## Dated entries

```html
<div class="releases">
  <div class="release is-current">
    <div class="rel-head"><span class="rel-ver">1.2.0</span><span class="rel-date">2026-08-29</span></div>
    <p class="rel-note">…</p>
    <ul class="rel-list"><li>…</li></ul>
  </div>
</div>
```

`is-current` lights the marker; give it to exactly one entry, the newest. The
rule is drawn on the list rather than on each row, so the last entry needs no
special case. `.rel-ver` is a label, not necessarily a version — the preview
uses decision ids, because inventing a release history for a project that has
no versions would be inventing a record.

## Colophon — the maker's credit

`.footer-bottom` ends with the `.mm-by` credit, the mark plus the credit line
linking to the tool. It ships by default; remove the `.mm-by` link (only) when
the intake answered `credit: false`.

```html
<a class="mm-by" href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener">
  <svg viewBox="0 0 512 512" aria-hidden="true" fill="currentColor"><!-- the MonoMind mark, kept verbatim from the template --></svg>
  <span><span class="en">Made with Hi Ted, Meet Lisa</span><span class="ko">Hi Ted, Meet Lisa로 제작</span></span>
</a>
```

## Chrome you must not rewrite

- **Routing** — `#/{lang}/{page}`. `go(id)` changes page, `setLang(l)` changes
  language, each preserving the other half, so deep links carry both. An unknown
  page or language falls back to `home` / `en` rather than rendering nothing.
- **The utility cluster** — theme and HTML self-download. Every control is
  guarded in the script: deleting its button in the nav is the supported way to
  switch that feature off.
- **The theme toggle** persists to `localStorage` under `monomind-doc-theme`
  and announces the theme it switches *to*, because the control is an icon.
- **The footer** sits outside the pages, so it renders on all of them and is
  armed for reveal once, on its own.
- **The More dropdown** absorbs pages that do not fit inline. It closes on an
  outside click, on Escape, and on every route change, and its button is hidden
  on mobile so the menu flattens into the burger list.

## The nav width budget

The nav row is capped by `--maxw` at 1120px on every viewport above 1168px, so
a row that does not fit has **no wider screen to grow into**: it wraps a label
mid-word or pushes the language toggle off the edge. The default spends roughly

```
brand 183 + five links 356 + More 68 + gaps 68
+ link icon 32 + utilbar 73 + language 82 + CTA 99 + padding 48  ≈ 1009
```

leaving about 110px. The utilbar figure is measured, not estimated: it was 104
with three buttons and is 73 now that the PDF control is gone. Longer labels
and a longer project name eat that headroom.
A sixth inline link does not fit — move one into the More dropdown instead.
Two rules exist only to keep this honest: every nav label is `white-space:
nowrap`, so a too-long row fails visibly rather than quietly wrapping, and the
utilbar's HTML word is hidden by default because it costs width the row has
not got. Measure before adding; do not eyeball.

## Colour and contrast

Both palettes are token-only: every rule consumes the variables, so a new colour
belongs in `:root` or the `html[data-theme="light"]` block and nowhere else.

Two measured facts to carry forward:

- **The light theme clears WCAG AA** at every text size the template uses. Its
  dim ramp is re-tiered rather than inverted — 7.5 / 6.0 / 5.3 against white.
- **The dark theme's `--fg-faint` does not.** It is 2.86:1 on `--bg` and carries
  11–13px text (`.ic-when`, `.cmd-row-principle`, `.cmd-label`,
  `.footer-bottom`). The value is inherited from the source design and kept
  deliberately; `--fg-faint:#7a7a7a` is the lightest grey that clears 4.5:1 on
  all three dark grounds. The comment in `:root` says so. Decide, do not drift.

## Motion — what moves, where, and how to switch it off

The motion layer is three verbatim blocks from `references/motion-patterns.md`
outside the fences — the `--lm-*` **bridge** (mapped onto this file's tokens),
the **base**, and the **runtime** script placed after the router — plus the CSS
and JS of the seven patterns used, and a self-download strip block. All of it
is load-bearing: copy, never retype. Inside the fences, an `lm-*` class on an
element is the whole hook: **remove the class and that effect is gone**; add
one only from the library. The router, the language switch, the theme and
the self-download are untouched.

One orchestrated moment, then restraint: the hero rises in sequence and the
command types itself; after that a section wipes in, a grid lights up under
the pointer, rows arrive one by one, and the closing title sweeps. Every
other block keeps project-website's own `.reveal` fade or does not move.

### The hero — stagger, typewriter, marquee, stat strip

`.hero-inner` carries `lm-stagger lm-on`, so its direct children rise one
after another (the script numbers them with `--i`). The command inside the
copy block types itself: the text sits in `.lm-type-text` **inside**
`data-copy-text`, so the copied string is whole, and `--lm-type-delay` holds
the caret until the hero has landed.

```html
<div class="container hero-inner lm-stagger lm-on">
  …
  <code class="cmd-text" data-copy-text><span class="lm-type lm-on" style="--lm-type-delay:.9s"><span class="lm-type-text">[install or run command]</span></span></code>
```

The compatibility strip is an endless marquee. Two identical tracks, the
second `aria-hidden` — it is the seam. Six or more names, or the band has
holes; under reduced motion it becomes one wrapping row.

```html
<div class="hero-compat-list lm-marquee">
  <ul class="lm-marquee-track">
    <li class="hero-compat-item">[NAME 1]</li>
    …
  </ul>
  <ul class="lm-marquee-track" aria-hidden="true">
    <li class="hero-compat-item">[NAME 1]</li>
    …
  </ul>
</div>
```

The stat strip is the one component the source template did not have. Three
figures with a label; integers count up when scrolled to. `data-lm-to` takes
the integer, `.lm-count-final` carries the formatted figure with its
separators and unit and is what screen readers and reduced-motion readers
get. A bracketed slot fails `parseInt` and stays static, which is right for a
figure you do not have — delete the strip rather than invent one.

```html
<div class="hero-stats" role="list">
  <div class="stat" role="listitem">
    <span class="stat-n"><span class="lm-count lm-on" data-lm-to="[1200]"><span class="lm-count-n" aria-hidden="true"></span><span class="lm-count-final">[1,200]</span></span></span>
    <span class="stat-l"><span class="en">[WHAT IT COUNTS]</span><span class="ko">[무엇의 수]</span></span>
  </div>
</div>
```

### The process track — wipe and stagger

`.lifecycle-wrap` no longer carries `.reveal`; instead the track wipes in
left to right and the six steps rise in sequence — one moment, not a wrap
fade on top of it.

```html
<div class="lifecycle-wrap">
  <div class="lifecycle" role="img" aria-label="…">
    <div class="lc-track lm-wipe lm-on" aria-hidden="true"></div>
    <ol class="lc-steps lm-stagger lm-on">
      <li class="lc-step" style="--h:205">…</li>
```

### The card grid — stagger and spotlight

`.cards-grid` carries `lm-stagger lm-on` in place of `.reveal`, and every
`.item-card` carries `lm-spotlight`: its edge lights up where the pointer is
and sits in the centre on focus. The template's glue switches the card's
original static hover edge off (`.item-card.lm-spotlight:before{display:none}`)
so there is one ring, not two. Touch readers keep the plain card.

```html
<div class="cards-grid lm-stagger lm-on">
  <a class="card item-card lm-spotlight" style="--h:205" onclick="go('docs')">…</a>
```

### Rows, lists, and pillars — stagger

`lm-stagger lm-on` replaces `.reveal` on `.pillars`, `.people-grid`,
`.steps`, the compare table's `<tbody>` and the contribute page's `.chk`.
Table rows fade without rising — the library strips the transform for `tr`
because table rows do not transform everywhere — and the wrapper that used
to carry `.reveal` (`.tblwrap`, the checklist's column) no longer does, so
nothing double-fades.

```html
<tbody class="lm-stagger lm-on">
  <tr>…</tr>
```

### The closing title — text mask

`.final-inner` carries `lm-stagger lm-on` and `.final-title` carries
`lm-textmask lm-on` — its own trigger, because the sweep is keyed on the
title's `.is-in`, not the parent's: the fill sweeps from dim to bright as the
block rises. In print
the title is solid — both the template's print rule and the pattern's own
restore a solid colour.

```html
<div class="container final-inner lm-stagger lm-on">
  <h2 class="final-title lm-textmask lm-on">…</h2>
```

### Rules the motion layer adds

- **One mechanism per element.** `.reveal` and `.lm-reveal`/`.lm-on` never
  share an element or nest a fade inside a fade; where a pattern went on,
  `.reveal` came off the wrapper.
- **Reduced motion and print get the finished page.** Every moving rule
  lives inside `@media screen and (prefers-reduced-motion: no-preference)`;
  the base style is the final state. Do not add a `.lm-*` rule outside that
  block.
- **A hidden tab or a dead observer still renders** (`L-022`). The runtime
  shows everything when the tab is hidden, when `IntersectionObserver` is
  absent, on `beforeprint`, and after a 1.2s fail-visible timer — the same
  guarantee `armReveal()` gives `.reveal`.
- **The hero command is the only typewriter.** Monospace Latin only: the
  caret travels in `ch` units, so a Korean command would need the plain
  copy block instead.
- **The self-download keeps working.** Its strip block removes `.is-in`,
  `.is-done`, `data-lm-ready` and `data-lm-done` before the router clones the document
  and restores them in the same task, so the saved copy opens exactly like
  the original. Keep the block if the download button stays.
- **Adding a pattern** means the library: `/lisa-motion` applies one from
  `references/motion-patterns.md` under the same rules, and composes a new one
  only when none fits.

## Dependencies

**Google Fonts only** — Geist and Geist Mono carry the look, Noto Sans KR gives
the Korean half a face. Nothing else loads from the network: no diagram runtime,
no CDN, no analytics, and **no animation library** — the motion layer is CSS
and the Web Animations API. With no network the type falls back to the system
stack and everything else still works.
