# Architecture diagram — component reference

Markup for `assets/tedandlisa-template-architecture.html`. One page, one
drawing, plus legend cards. Use it when the deliverable is a system diagram
someone will read closely and paste into a review — not a talk.

The visual system is derived from the Architecture Diagram Generator by Cocoon
AI (MIT, see `NOTICE`): slate ground, a faint grid field, JetBrains Mono
throughout, and **colour that means something**. The MonoMind chrome — the mark,
the English/Korean switch, the theme toggle, PDF and HTML export — is ours.

## Colour is semantic, and set by class

Never put `fill=` or `stroke=` on a node. The class carries the meaning, and the
theme carries the colour:

| Class | Means | Dark stroke | Light stroke |
| --- | --- | --- | --- |
| `frontend` | What the user touches | `#22d3ee` | `#0e7490` |
| `backend` | Services you run | `#34d399` | `#047857` |
| `data` | Anything that persists | `#a78bfa` | `#6d28d9` |
| `cloud` | Managed platform services | `#fbbf24` | `#b45309` |
| `security` | Auth, secrets, policy | `#fb7185` | `#be123c` |
| `bus` | Queues, topics, events | `#fb923c` | `#c2410c` |
| `generic` | Outside the system | `#94a3b8` | `#475569` |

Two consequences worth stating: a reader learns the palette once and reads every
later diagram faster, and the light theme is a token swap rather than a redraw.

## Node

```html
<g class="node backend">
  <rect x="500" y="266" width="180" height="68" rx="6"/>
  <text class="t en" x="590" y="296" text-anchor="middle">SERVICE</text>
  <text class="t ko" x="590" y="296" text-anchor="middle">서비스</text>
  <text class="s en" x="590" y="312" text-anchor="middle">runtime · region</text>
  <text class="s ko" x="590" y="312" text-anchor="middle">런타임 · 리전</text>
</g>
```

`.t` is the name, `.s` the sublabel. Both languages are written into the file
and toggled by `body[data-lang]`, so **the drawing translates too** — a diagram
whose prose switches to Korean while its boxes stay English looks broken. Both
copies carry the same `x`/`y`; only one is ever displayed.

## Boundary

```html
<g class="boundary">
  <rect x="216" y="40" width="764" height="540" rx="12"/>
  <text class="en" x="230" y="60">REGION OR ACCOUNT</text>
  <text class="ko" x="230" y="60">리전 또는 계정</text>
</g>
```

A dashed amber enclosure for a region, an account, a VPC, a trust boundary. Use
it sparingly — two nested boundaries are readable, four are wallpaper.

## Links

```html
<g class="link-layer">
  <path class="link" d="M 140 300 L 236 300" marker-end="url(#arrow)"/>
  <path class="link dashed" d="M 90 340 L 90 500 L 236 500" marker-end="url(#arrow)"/>
  <text class="link-label en" x="188" y="292" text-anchor="middle">REQUEST</text>
  <text class="link-label ko" x="188" y="292" text-anchor="middle">요청</text>
</g>
```

- **Draw the link layer before the nodes.** SVG has no z-index; paint order is
  document order, so links drawn last cut across every box.
- Prefer orthogonal paths (`L` segments that turn) over diagonals: they keep
  labels off the lines.
- `.dashed` means optional, asynchronous, or a return path — pick one meaning
  per diagram and say which in a legend card.

## Legend cards

```html
<div class="card">
  <div class="card-head"><span class="dot backend"></span><h3>SERVICES</h3></div>
  <ul><li>What runs here.</li></ul>
</div>
```

One card per family the diagram actually uses. Delete the rest — an empty
legend entry implies a component the reader then hunts for.

## Chrome — do not rewrite

- **Theme, language, PDF, HTML** all live in one guarded script at the foot of
  the file. Deleting a control's markup switches that feature off cleanly.
- Export is the browser's own print-to-PDF plus a self-download, so the file has
  **no runtime dependency** beyond Google Fonts. Do not add html2canvas or jsPDF
  to get an image export; a diagram that needs a bitmap can be screenshotted.
- The grid pattern's stroke is set in CSS (`#grid path`), not on the element: a
  `var()` inside an SVG presentation attribute never resolves, and the grid
  silently disappears.

## Colophon — the maker's credit

The footer ends with the credit link, bilingual like everything else on the
page. It ships by default; remove that last `&middot;` and `<a>` (only) when
the intake answered `credit: false` — the `monomind ai lab` identity link
before it belongs to the logo answer, not to this one.

```html
&middot; <a href="https://html.monomind.one/?ref=file" target="_blank" rel="noopener noreferrer"><span class="en">Made with Hi Ted, Meet Lisa</span><span class="ko">Hi Ted, Meet Lisa로 제작</span></a>
```

## Dependencies

Google Fonts only. Everything else is inline.
