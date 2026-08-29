# Project website — component reference

Markup for `assets/tedandlisa-template-project-website.html`. Every snippet is
lifted from the skeleton, so it is known-good. Compose from these; do not invent
class names.

This template is a **website**, not a deck and not a single page: several pages
are hash-routed behind a sticky nav, each page scrolls, one footer is shared by
all of them, and both languages are written into the file rather than translated
at read time.

Reach for it when the deliverable is a project's public face — a launch page, a
tool's home, a programme's site — rather than something read start to finish.

## The three registers that must agree

A page exists only if all three name it. Miss one and it is unreachable:

1. `<section class="page" id="page-ID">`
2. `data-page="ID"` on a nav entry — in **both** the desktop `.nav-links` list
   and the `.nav-mobile` list, which are separate DOM
3. an entry in the `PAGES` array at the head of the script

`apply()` drives both nav lists from one loop, so their active states cannot
drift — but only over the entries you actually added to each.

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
  any language span**. There is no translation service to defend against, which
  is why this template needs no `notranslate`.
- Nav labels, buttons, card footnotes, and footer columns all follow the rule.

## Reveal on scroll

Any block can carry `.reveal` and it fades up when scrolled to. Two things to
know:

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
row that does not navigate.

## Callout

```html
<div class="callout"><b><span class="en">Note.</span><span class="ko">참고.</span></b> <span class="en">…</span><span class="ko">…</span></div>
```

The one component the source design did not have, added because a project site
always needs to say "note this". Built from existing tokens only.

## Chrome you must not rewrite

- **Routing** — `#/{lang}/{page}`. `go(id)` changes page, `setLang(l)` changes
  language, each preserving the other half, so deep links carry both. An unknown
  page or language falls back to `home` / `en` rather than rendering nothing.
- **The utility cluster** — theme, PDF (`window.print()`), and HTML
  self-download. Every control is guarded in the script: deleting its button in
  the nav is the supported way to switch that feature off.
- **The theme toggle** persists to `localStorage` under `monomind-doc-theme`
  and announces the theme it switches *to*, because the control is an icon.
- **The footer** sits outside the pages, so it renders on all of them and is
  armed for reveal once, on its own.

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

## Dependencies

**Google Fonts only** — Geist and Geist Mono carry the look, Noto Sans KR gives
the Korean half a face. Nothing else loads from the network: no diagram runtime,
no CDN, no analytics. With no network the type falls back to the system stack
and everything else still works.
