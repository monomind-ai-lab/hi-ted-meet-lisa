# Framed deck — component reference

Markup for `assets/tedandlisa-template-framed-deck.html`. One slide on screen at
a time, held inside a 16:9 frame on a black ground, with a masked grid field and
a single blue accent. Geist for text, Geist Mono for anything a reader might
type.

The visual system is derived from the agent-skills teaching decks by Addy
Osmani (MIT — see `NOTICE`). What it is for: a short, spoken deck that will also
be linked, projected, and printed unchanged.

## What makes this shape different

The other slide templates here are full-bleed pages that reflow. This one is a
**canvas**. Above 820px the slide becomes a fixed 16:9 box with
`container-type:size`, and every type size on it is written in `cqh`/`cqw` — so
the whole slide scales as one object with the frame, and the deck looks
identical on a laptop and a projector.

Three consequences:

- **`container-type:size` on `.slide` is load-bearing.** Remove it and every
  desktop type size resolves to zero.
- **Only one slide is in the layout at a time** (`display:none` until
  `.active`). Anything that measures itself on load reads zero on a hidden
  slide, which is why this shape uses static markup and inline SVG.
- **Under 820px it degrades to a plain scrolling column** with fixed `rem`
  sizes, plus a "best on desktop" hint bar. That is the intended fallback, not
  a bug to fix.

## The shape of a slide

```html
<section class="slide" data-i="2"><div class="s s-bullets">
    <span class="kicker">[SECTION LABEL]</span>
    <h2>[What the slide says]</h2>
    ...
  </div>
  <footer class="brand-foot">
    <span class="bf-brand">[brand]<span class="bf-dim">[-suffix]</span></span>
    <span class="bf-mid">[DECK TITLE]</span>
    <span class="bf-page">3 / 7</span>
  </footer>
</section>
```

- `.s` is the content column and carries the slide's variant class.
- `data-i` and `.bf-page` are both **hardcoded documentation**. The script
  indexes `.slide` by document order and ignores `data-i`; nothing computes the
  page number. Renumber both after adding or deleting a slide, or the source
  misleads the next person to open it.
- `.bf-mid` is hidden on mobile and shown in the frame and in print.

## Variants

| Class on `.s` | For |
| --- | --- |
| `s-title` | The opening slide — gradient `h1`, sub, foot-note |
| `s-statement` | One claim at the largest size the frame allows |
| `s-bullets` | Four to five points with glowing accent markers |
| `s-diagram` | An inline SVG inside `.img-wrap`, plus a caption |
| `s-commands` | A two-column reference table, scrollable on mobile |
| `s-cta` | The closing slide — centred, links, colophon |

## Title

```html
<div class="s s-title">
  <span class="kicker">[SECTION LABEL]</span>
  <h1>[DECK TITLE]</h1>
  <p class="sub">[One line saying what this is.]</p>
  <p class="foot-note">[Who it is for, and when.]</p>
</div>
```

`h1` is gradient-clipped white-to-grey via `background-clip:text` with
`color:transparent`. It therefore **cannot take a colour override** — restyling
it means changing the gradient. It is also invisible to a browser that fails to
paint the gradient, so keep the deck's name in `<title>` too.

## Statement

```html
<div class="s s-statement">
  <span class="kicker">[THE PROBLEM]</span>
  <h2 class="big">[The claim, in one sentence a room can read.]</h2>
  <p class="sub">[The supporting sentence.]</p>
</div>
```

`h2.big` caps at `15ch` and `.sub` at `42ch`. Those measures are the design —
write to fit them rather than widening them.

## Bullets

```html
<div class="s s-bullets">
  <span class="kicker">[THE IDEA]</span>
  <h2>[What the list is a list of]</h2>
  <ul>
    <li>[First point, one line if possible.]</li>
    <li>[Second point.]</li>
  </ul>
</div>
```

The marker is a glowing accent square drawn by `::before` — no list bullet, no
custom markup. Four fit the frame comfortably, five fit, and a sixth starts
clipping on a short laptop screen. The frame clips silently.

## Diagram

```html
<div class="s s-diagram">
  <span class="kicker">[ANATOMY]</span>
  <h2>[What the drawing shows]</h2>
  <div class="img-wrap"><svg viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg" font-family="Geist, 'Segoe UI', Arial, sans-serif">
    ...
  </svg></div>
  <p class="caption">[What the drawing cannot say for itself.]</p>
</div>
```

- **Draw on 1280×720**, the same box the print page uses, so a slide and its
  PDF are the same picture.
- **Give the SVG its own background and grid.** `.img-wrap` is a transparent
  frame; a drawing with no ground shows the slide's radial gradient through it
  and the framing disappears.
- Colours go on the shapes as attributes here, because the drawing is exported
  as an image as often as it is read in place. Use the deck's own values:
  `#0e0e0e` fill, `#2e2e2e` border, `#52a8ff` for the accented element,
  `#ededed` / `#a1a1a1` / `#7d7d7d` for the three text weights.
- An arrow marker must be declared in `<defs>` inside the same SVG; markers do
  not cross document boundaries.
- The frame caps the drawing at `54cqh` and centres it, so a 16:9 drawing is
  letterboxed left and right inside a wider `.img-wrap`. Either accept the
  bands, or draw wider and shorter — roughly 3:1 fills the frame edge to edge.

## Command block

```html
<pre class="cmd"><span class="prompt">$</span> [the exact command]</pre>
```

`white-space:nowrap` with `overflow-x:auto` on mobile, wrapping and
shrink-wrapped inside the frame. Write a command someone can copy without
editing it first — that is the whole point of giving it a slide.

## Reference table

```html
<div class="s s-commands">
  <span class="kicker">[THE REFERENCE]</span>
  <h2>[What the table lists]</h2>
  <table>
    <tr><td class="cmd-cell">[/command]</td><td>[what it does]</td><td class="dim">[when]</td></tr>
  </table>
</div>
```

`.cmd-cell` is mono, accent-coloured, 30% wide and `nowrap`. `.dim` is the
right-aligned faint note. No `<thead>` — the table is a reference list, not a
data set. Five rows is the frame's comfortable maximum; the wrapper scrolls
sideways on a phone.

## Closing

```html
<div class="s s-cta">
  <h2>[The line you want them to leave with]</h2>
  <pre class="cmd"><span class="prompt">$</span> [the command again, or the URL]</pre>
  <div class="links"><span>[your-site.example]</span><span>[github.com/you/project]</span></div>
</div>
```

## Chrome — do not rewrite

- The controller is fifteen lines at the foot of the file: `show(n)` toggles
  `.active`, sets the progress width, and writes `location.hash`, so **every
  slide is deep-linkable** as `#3` and reload restores it.
- Keys: arrows, space and PageUp/PageDown to move, Home/End to jump, `f` for
  fullscreen, `p` to print.
- **Click-to-advance:** a click past 60% of the window width goes forward,
  before 40% goes back. It skips `.nav` and any `<a>`. A new interactive control
  must be added to that guard or it will change slide when used.
- Export is the browser's own print dialogue against a fixed 1280×720 `@page` —
  no library, per the house rule. `export: pdf` here means telling the reader
  about `p`, not adding machinery.

## Colophon — the maker's credit

The closing slide carries the credit under `.links`, in the deck's mono micro
type. It ships by default; remove the second `<a>` and its `&middot;` (only)
when the intake answered `credit: false` — the `monomind ai lab` link before it
belongs to the `logo` answer. The product name is wrapped `notranslate` so a
reader's browser translation leaves it alone.

```html
<p class="colophon">
  <a href="https://monomind.one/?ref=deck-mark" target="_blank" rel="noopener noreferrer">monomind ai lab</a>
  &middot; <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer">Made with <span class="notranslate" translate="no">Hi Ted, Meet Lisa</span></a>
</p>
```

## Dependencies

Google Fonts only — Geist and Geist Mono. Everything else is inline. Both
families have real fallbacks in the token (`'Segoe UI',system-ui` and
`ui-monospace`), so the deck degrades rather than breaks with no network;
`delivery: standalone` inlines them properly.
