# Design review for a generated deck

The design pass for a generated file. It has two entry points — the final step
of a `/lisa` build, and the standalone `/lisa-review` skill — and reads the
same from either. A deck is a presentation surface, not an app screen, so this
reference names what actually matters here and hands the general craft work to
Impeccable.

## When this runs

The intake's `review` answer schedules the pass:

- **`after`** — the default. `/lisa` delivers the draft first, and the pass
  runs as `/lisa-review`: immediately afterwards when the user asks, or any
  time later against the finished file. The reasoning: the review adds minutes
  to every build, and a draft in hand is worth more than a reviewed file still
  building.
- **`inline`** — the pass runs as `/lisa`'s final step, before the file is
  handed over.
- **`none`** — only the floor checks below run, inside the build, and the
  handover must say so. Skipping the review is a choice to state, never one to
  hide.

Everything below applies unchanged from either entry point.

## Which reviewer runs

1. **The user's own Impeccable**, if their agent already has the skill. Prefer
   it — it is the copy they maintain and configure.
2. **The bundled copy** at `.agents/skills/impeccable/`, present in a plugin
   install or a repository checkout. Read its `SKILL.md` and follow it as
   written. Apache 2.0; see `VENDORED.md` before touching anything in there.
   It is **not** in an uploaded zip — it alone is 156 files, and Claude states
   a 200-file maximum — so a skill running from a chat-app upload goes to 3.
3. **This file alone**, if neither can run. The checks below are the floor and
   need no tooling.

Say which reviewer ran. Never claim a deck was design-reviewed when only the
manual checks happened.

## What to ask Impeccable for

Decks are the **Read** and **Persuade** modes, never Operate. Useful commands:

| Command | When |
| --- | --- |
| `/impeccable critique` | Hierarchy and clarity on a deck that is content-complete. |
| `/impeccable audit` | Contrast, responsive behaviour, and technical quality. |
| `/impeccable polish` | Final pass before handing the file over. |
| `/impeccable typeset` | The type scale fights itself across slides. |
| `/impeccable layout` | Spacing and rhythm drift between slides. |

Target the generated `.html` file. Do not run `/impeccable init`, `document`, or
`extract` against a deck — those write project design context, and a deck is an
output, not the project's design system. Never let a review rewrite the
template's design tokens; a finding against the shipped MonoMind system is a
finding to report, not to silently apply.

## Deck-specific checks — the floor

**Visual consistency across slides.** These are what break first when slides are
generated one at a time:

- One type scale. Every `h2` is the same size; no slide invents its own.
- Eyebrow, headline, and lead appear in the same order and position throughout.
- Vertical rhythm holds — content starts at the same height on every slide.
- The brand mark is present, identical, and in the same corner on every slide.
- No orphan component styles: every class comes from `slide-patterns.md`.
- Colour is used for the same meaning everywhere — accent means emphasis, not
  decoration on one slide and structure on another.
- Slide count matches the counter, and `data-screen-label` values are sequential.
- No workflow text survives on a slide: no template or preset name, file
  name, path, "option A/B" or requirement note ("safe option", "for internal
  sharing") — chrome is the deck title, section, date, author, page number,
  or nothing.

**Responsive behaviour.** The deck is horizontal on desktop and vertical on
phones; check both:

- At phone width nothing overflows horizontally. Verify with
  `document.documentElement.scrollWidth === clientWidth`, not by eye.
- Tables and code blocks scroll inside their own container rather than the page.
- Text stays readable at 375px without a horizontal scrollbar appearing.
- Fixed chrome (counter, progress, language switch, menu) stays reachable.
- Nothing depends on hover alone.

**Gradient text clips its own descenders.** `background-clip: text` paints the
gradient only inside the element's box, so any glyph reaching past that box
renders transparent — the *g*, *y*, and *p* look sliced off, and only on the
words that happen to have descenders, which is why it survives a quick look.

Display headings are where this bites, because they are the ones set with tight
leading. A font needs roughly `(ascent + descent) / em` of line-height to
contain its own glyph box — 1.26 for Plus Jakarta Sans — and a display title
often runs at 1.05. Check it, rather than trusting the eye:

```js
const cs = getComputedStyle(el), c = document.createElement('canvas').getContext('2d');
c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
const m = c.measureText(el.textContent);
const fs = parseFloat(cs.fontSize), lh = parseFloat(cs.lineHeight);
const inkBottom = (lh - fs) / 2 + m.fontBoundingBoxAscent + m.actualBoundingBoxDescent;
inkBottom > lh + parseFloat(cs.paddingBottom);   // true = clipped
```

The fix that keeps the leading is to extend the paint box and take the height
straight back, so nothing moves:

```css
padding-bottom: 0.3em;
margin-bottom: calc(<original margin> - 0.3em);
```

Loosening `line-height` to 1.3 also works, but it changes how every multi-line
title in the deck reads, which is a design change rather than a fix.

**Measuring contrast — do not eyeball it, and do not parse colour strings.**
Modern CSS computes to `color(srgb 1 1 1 / 0.92)` and `oklab(0.43 -0.02 -0.12)`,
whose numbers are not 0-255 RGB. Reading them with a naive regex reports white as
black and a mid blue as near-black. Paint the colour into a 1x1 canvas and read
the pixel back instead; that is the only reading that matches what a reader sees.

Two further traps specific to this deck:

- **Fixed chrome sits over the current slide, not over `body`.** Walking the DOM
  ancestors of the counter or the menu lands on `body`, whose background is only
  visible where no slide covers it. Composite against the slide.
- **A theme that flips text must flip its surfaces too.** `.deck-menu-panel`
  hardcodes a deep-ink fill; flipping only the token that drives its text
  produced dark-on-dark at 1.12:1 while every automated check still passed.

**Projection legibility** — decks are read across a room, not at desk distance:

- Body text never falls below the template's `--text-base`.
- Contrast holds on the photographic slides, where artwork sits under text.
- No more than one idea per slide.

## Reporting

The pass applies its findings by default, then reports what it did. Group
them as **fix now** (always applied), **worth considering** (applied too,
when the change is safe and stays inside the template's own system), and
**left alone** — anything that would change the design system, change what
the content says, or needs the user's call — with a reason for each item in
the third group. After the fixes, re-run the responsive check, because layout
fixes are what regress it. The report then reads as what was improved and
what was left alone and why.
