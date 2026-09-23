# CJK typography — Korean and Traditional Chinese in a Lisa file

Shared guidance for every file that renders Hangul or Han text: the
inline-bilingual templates (`web-document`, `sitemap-ia`, `project-website`,
`architecture`, `mermaid-master`, `evidence-deck`, `paper-brief`) and the
MonoMind deck once Google Translate has switched it. It is schema-level on
purpose: it names the properties to set and why, never a value. The values are
each template's own, and templates never share them.

## The pairing the templates already carry

No template swaps its Latin faces out for a CJK one. Each loads **one Noto
family beside them** and lets the language rule decide which face leads, so
digits and Latin words stay in the deck's own type and only the CJK glyphs
fall through to Noto:

| Template | Latin faces | CJK family | How the stack is written |
| --- | --- | --- | --- |
| `web-document` | Inter, JetBrains Mono | Noto Sans KR | `--sans` appends it; `body[data-lang="ko"]` puts it first |
| `sitemap-ia` | Inter, JetBrains Mono | Noto Sans TC | `--sans` appends it; `body[data-lang="zh"]` puts it first |
| `project-website` | Geist, Geist Mono | Noto Sans KR | `--font-sans` appends it, in both languages |
| `architecture` | JetBrains Mono | Noto Sans KR | `body[data-lang="ko"]` puts it before `var(--mono)` |
| `mermaid-master` | Instrument Serif, Geist, Geist Mono | Noto Sans KR | `body` appends it; `.slide[data-lang="ko"] svg text` puts it first |
| `evidence-deck` | Archivo Black, Space Grotesk, JetBrains Mono | Noto Sans KR | `body[data-lang="ko"]` re-points `--font-display` and `--font-body` to append it |
| `paper-brief` | Archivo | Noto Sans TC | `--font-body` leads with it (the file opens in Chinese); `body[data-lang="en"]` puts Archivo first |
| `monomind-deck` | Plus Jakarta Sans, JetBrains Mono | none | translated text renders in the named system CJK faces — see below |

The family is loaded by the same `<link>` as the Latin faces — this is the
evidence deck's:

```html
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap"
      rel="stylesheet" media="print" onload="this.media='all';this.onload=null" data-lisa-font>
<noscript><link href="…same href…" rel="stylesheet"></noscript>
```

`media="print"` is not a mistake: it is what stops the stylesheet holding the
page's first paint. The browser still fetches it, at low priority, and the
`onload` flips it live the moment it lands — so a reader whose network cannot
reach fonts.googleapis.com gets the deck in its fallback faces immediately
instead of a blank window. `data-lisa-font` is how the Share block puts
`media="print"` back before publishing: `media` is a reflected attribute, so
by then the live DOM says `"all"`, and a copy taken from it would block.

Its language rule appends rather than replaces:

```css
body[data-lang="ko"]{
  --font-display:'Archivo Black','Noto Sans KR',sans-serif;
  --font-body:'Space Grotesk','Noto Sans KR',sans-serif;
}
```

Two rules follow from the pattern. **A font change is two edits** — the token
*and* the `<link>`, per `references/applying-answers.md`: a CJK family named in
a token but absent from the link renders in the system face with no error.
**The weight has to be in the link too.** A weight the link did not load is
snapped to the nearest one that was.

### CJK families load two weights: 400 and 700

Not the three to five they used to. A CJK family is not priced like a Latin
one — Noto Sans KR is **1.78 MB across 124 slices** per weight, Noto Sans TC
**2.14 MB across 105**, against roughly 30 KB for a Latin face. Loading five
weights of Noto Sans TC, as `paper-brief` did, put over 10 MB of potential
font behind one deck; what a reader actually pulls is far less (Google serves
only the slices their text touches — about 82 KB of Korean, 159 KB of Chinese
for a normal deck, per weight), but every extra weight multiplies that, and it
buys distinctions most readers cannot see at body size.

So the cap is regular and bold, and **nothing is synthesised** — 300 and 500
resolve to 400, 900 resolves to 700. The one visible cost is a display weight
that was carrying real contrast:

> `evidence-deck` sets `body[data-lang="ko"] .mega{font-weight:900}` beside
> Archivo Black, which is a true single-weight 900. That Hangul now renders at
> 700 and reads a little lighter than the Latin it sits with. It is a
> deliberate trade, not an oversight. Putting it back is one weight in that
> template's `<link>` — `Noto+Sans+KR:wght@400;700;900` — and costs roughly
> another 80 KB of slices on a Korean deck.

Latin families keep their full weight ranges. They are small, and the
reasoning above does not apply to them.

## Set these on every CJK run

- **Line-height 15–25% looser than the Latin setting.** Han and Hangul glyphs
  fill their em square, so leading that reads as airy in Latin reads as
  crowded in CJK. Loosen body and display both, through the template's tokens
  or its `body[data-lang]` rule — never per element.
- **Letter-spacing 0.** CJK glyphs are already evenly set; the positive
  tracking every template puts on its micro type (eyebrows, table headers,
  page numbers) looks broken on them. Zero it under the CJK language rule.
- **No `text-transform: uppercase`.** It has nothing to act on in CJK, and on
  a mixed run it capitalises only the Latin words — emphasis nobody meant.
  The uppercase eyebrows stay uppercase in English; the CJK span carries its
  own wording.
- **Full-width punctuation.** Commas, full stops, brackets and colons in a CJK
  sentence are the full-width forms — `，。（）：` — not the Latin ones, which
  sit low and cramped between square glyphs. Quotation marks follow the
  language: `「」` in Traditional Chinese, `“ ”` in Korean.
- **A space between CJK and Latin or digits.** "使用 Claude", "3 個檔案",
  "Claude 사용" — not "使用Claude". Browsers do not add it, and Chinese and
  Korean typography expect it.
- **No synthesised italic.** Noto Sans KR and Noto Sans TC ship no italic, so
  `font-style: italic` makes the browser shear the glyphs. Emphasis in a CJK
  run is weight or colour. The templates already restyle `<em>` as a block
  sub-line rather than italics; that instinct is the right one.
- **One family per sentence.** A sentence that switches face mid-word — a
  Latin name in the Latin face inside a Korean sentence in Noto — reads as a
  rendering fault. Let the language rule's stack order decide the lead face
  for the whole run; do not wrap individual words in a different family.

## The MonoMind deck: translated output

`monomind-deck` loads no CJK family, so whatever Google Translate produces
renders in a system face at the deck's Latin leading and tracking. Which system
face is no longer left to chance: the token block names `--fb-jp`, `--fb-ko`
and `--fb-zh` explicitly — Hiragino, Apple SD Gothic Neo, PingFang, the
Microsoft equivalents, Noto last for Linux and Android — and reorders them so
the script on screen leads.

That reordering is not decoration. **Han is one Unicode block shared by
Japanese, Traditional Chinese and Simplified Chinese**, and the three draw a
number of characters differently (直, 骨, 次, 說). A stack resolves per
character: whichever family holds a glyph first wins, for every language. With
Japanese ahead of Chinese — and Hiragino Sans on every Mac — a Chinese reader
would get Japanese regional forms and nothing would look broken to anyone but
them. So the deck's own switch writes `data-deck-lang` on `<html>` at boot and
the stylesheet hoists the matching group. Deliberately not `lang`: Google
Translate reads that to decide the **source** language, and setting it to the
target would tell the widget the page is already translated.

Two documented failures live here:

- **Translated CJK runs flush against protected spans (`L-002`).** The
  translator drops the space either side of a `notranslate` identifier —
  `目前狀態NOW.md限制`. The template's fix is
  `html.translated-ltr .nt-term, html.translated-rtl .nt-term { margin-inline: 0.15em; }`,
  scoped to the translated state so English spacing is untouched. It reaches
  only spans that carry `nt-term`, which the protection pass adds to the ones
  it creates — give a term you wrap by hand the same class, or it collides.
- **Product names and filenames get translated (`L-001`)** unless they are on
  the `TERMS` list or wrapped `notranslate`. A translation rule rather than a
  typographic one, but the symptom looks typographic — a Latin word gone — so
  it is listed here.

## `delivery: standalone` subsets the family — say what that costs

Inlined unsubsetted, a CJK family adds several megabytes; Noto Sans KR and
Noto Sans TC are the expensive half of every template that carries them.
`references/applying-answers.md` says to subset with Google Fonts' `text=`
parameter — and to state the cost in the handover: **the subset holds only the
glyphs the file rendered at build time.** A character typed into the file
later — an edit, a new slide, a corrected name — is not in the subset and falls
back to the system face, silently, for that glyph alone. Say so; a reader
should not meet it as one mismatched character in a heading.

## Checking it

Switch into the CJK language and read the page, not the markup. Look for a
Latin comma in a Chinese sentence, an uppercase eyebrow that capitalised one
English word inside Korean, tracking on a CJK label, a sheared italic, and a
run that changed family mid-sentence. Then check both languages at 375px wide
and 600px tall: Korean and English do not wrap alike, and the snap decks clip
rather than scroll (`references/slide-patterns-evidence-deck.md`,
`references/slide-patterns-paper-brief.md`).
