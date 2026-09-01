# Hi Ted, Meet Lisa

<p align="left">
  <img src="assets/tedmeetslisa.jpg" alt="Hi Ted, Meet Lisa — Turn ideas into compelling slide decks" style="width: 100%; max-width: 100%;">
</p>

> **Turn ideas into compelling slide decks — one standalone HTML file, no build step.**

Hi Ted, Meet Lisa is an agent skill that generates a finished, self-contained HTML
deck. You describe the deck; the agent asks what it cannot infer, builds from a
template, applies your answers, reviews the result, and hands you a single file
you can open, present, print, or email.

The design system is not improvised per deck. It ships in the repository as
templates: design tokens, a typographic scale, a component library, navigation,
and the language switch. The agent fills a template with content rather than
inventing a look each time — so two decks made months apart still look related.

Hi Ted, Meet Lisa is **agent-operated and human-readable**. People provide the
brief and answer a short visual intake; agents read the skill, build the deck,
and verify it. Every template is plain HTML and CSS that a person can open and
edit at any time.


---

## ✅ Start here

**No terminal? Start at the website.** [html.monomind.one](https://html.monomind.one)
is the whole front door in a browser: preview every template live, answer the
intake panel, and copy one paste-ready prompt for any coding agent — Claude
Code, Codex, Pi, OpenCode, Hermes, or anything else that reads a public URL.
Nothing to install.

Prefer it as a standing command? Install it once, then it is three commands
you have for good.

```sh
git clone --recurse-submodules \
  https://github.com/monomind-ai-lab/hi-ted-meet-lisa.git \
  ~/.claude/skills/tedandlisa

ln -s ~/.claude/skills/tedandlisa/skills/tedandlisa-design \
      ~/.claude/skills/tedandlisa-design
ln -s ~/.claude/skills/tedandlisa/skills/tedandlisa-new-template \
      ~/.claude/skills/tedandlisa-new-template
```

`~/.claude/skills/` makes them available in every project. For one project only,
clone into that project's `.claude/skills/` instead. Other agents have their own
skills directory — the layout is the same: one directory per skill, each with a
`SKILL.md` at its top.

**Then, whenever you need something:**

```text
/tedandlisa a 12-slide deck on our Q3 roadmap, for the exec team
```

Opens the intake panel, asks its questions — nine to sixteen depending on the
template, every one with a default — builds from the template you picked, runs a
design review, and hands back one file.

```text
/tedandlisa-new-template ./that-deck-i-like.html
```

Turns a finished HTML file into a reusable template: extracts its stylesheet and
machinery into a placeholder skeleton, strips the original's subject matter,
registers it, and captures its gallery thumbnail. It is then one of your choices
in the panel, permanently.

```text
/tedandlisa-design a launch deck, glassmorphism, with animated slides
```

For when the house templates are the wrong shape — style presets and
animated HTML.

**Just trying it once?** You do not have to install anything. The
[website](https://html.monomind.one) hands you a finished prompt — or paste
this to any agent that can read a URL:

```text
Build me a deck using https://github.com/monomind-ai-lab/hi-ted-meet-lisa.
Read and follow `SKILL.md`, starting with its intake panel. The deck is about
[YOUR SUBJECT], for [AUDIENCE].
```

**What you get**

- **One standalone `.html` file** — open it, present it, print it, email it. No
  build step and no dependencies to install.
- **A choice of five shapes** — a presentation deck, a web document, a
  diagram-first deck, a single architecture diagram, or a sitemap and IA
  proposal with a clickable navigation prototype. Preview each in the gallery
  before you choose.
- **Two languages in the file**, with filenames, commands, and product names
  protected from translation.
- **Light and dark**, a deck menu, keyboard and touch navigation, and optional
  PDF and HTML download — whichever of these you asked for.
- **A design pass before handover** that measures contrast in both themes and
  behaviour at phone width, then reports what it fixed.

Want a look the house style does not cover? The gallery's last
card hands off to [`tedandlisa-design`](skills/tedandlisa-design/), which drives
a vendored Slides AI pipeline with MonoMind branding applied.


---

## ✅ Why it matters

A deck produced by an agent usually fails in the same three ways: it invents a
new visual language on every slide, it quietly translates the words that must
never be translated, and it looks fine on a laptop and breaks on a phone.

Hi Ted, Meet Lisa answers those directly:

1. **One system per deck.** Components come from a pattern reference lifted
   verbatim from shipped decks, so slides agree with each other.
2. **Identifiers survive translation.** Filenames, commands, and product names
   are protected before any translation runs.
3. **Both themes and both widths are measured, not assumed.** A design review
   pass checks contrast and responsive behaviour before handover.



---

## ✅ What this repository does

This repository is an agent-facing package: two skills, three templates, a
visual intake panel, a template registry, and the tooling that ties them
together. An agent uses them to produce a deck without asking you to run
anything yourself.

It also carries its own public face: [`site/`](site/) is the source of
[html.monomind.one](https://html.monomind.one), a static page assembled at
deploy time by `site/sync.sh` from the same previews, thumbnails, and intake
panel this repository ships — so the website and the skill can never drift
apart.

### How agents find the instructions

1. Harnesses that support the Agent Skills convention discover `SKILL.md` at the
   repository root as `/tedandlisa`, and
   `skills/tedandlisa-new-template/SKILL.md` as its companion.
2. Any other agent can be pointed at `SKILL.md` directly; it is plain Markdown
   and carries the whole procedure.



---

## ✅ Templates

Five templates, chosen at the start of the intake. They are not variations of
one look — they differ in shape, navigation, and how they handle language.

The intake gallery offers a sixth card beside them, listed here for the same
reason it appears there: you are choosing how the deck gets made, not first
choosing between two menus. It is not a template, and nothing in this
repository builds it — see [when a template is the wrong shape](#-when-a-template-is-the-wrong-shape).

| Template | Shape | Language | Preview |
| --- | --- | --- | --- |
| **MonoMind deck** | Horizontal slides, one idea each, read across a room | Google Translate, loaded only when a reader picks another language | [Live preview →](previews/monomind-deck.html) |
| **Web document** | Hash-routed pages that scroll, read at desk distance | English and Korean written inline, toggled instantly — works offline | [Live preview →](previews/web-document.html) |
| **Multi-page Diagrams** | Diagram-first on light paper, one drawing per slide | Every slide written twice, so diagram labels translate too | [Live preview →](previews/mermaid-master.html) |
| **Architecture diagram** | System diagrams on slate, where colour means something — one view or several | Both languages inline, including the labels inside the drawing | [Live preview →](previews/architecture.html) |
| **Sitemap & IA proposal** | Pages that argue a site structure, plus the navigation wired up to click through | Both languages written inline | [Live preview →](previews/sitemap-ia.html) |
| **Slide design** — *a handoff, not a template* | Twelve style presets and animated HTML | One language per deck — the presets carry no toggle | [Live preview →](previews/slide-design.html) |

All six have a live preview linked from the intake gallery, so you can look
before you choose.

Each of the five templates has a pattern reference in `references/` giving
verbatim markup for every component, plus the rules that are easy to get wrong.
The handoff has none — it is not built from markup here.

A template is a **scaffold, not a cage**. Agents extend it — new components, new
slide shapes — in the template's own design tokens. What they may not rewrite is
the load-bearing machinery: the deck navigation script, the hash routing, and
the diagram viewer each encode fixes for problems that are invisible until they
break.



---

<p align="left">
  <img src="assets/tedlisaidea.jpg" alt="When Ted meets Lisa, ideas come to life in HTML" style="width: 100%; max-width: 100%;">
</p>

## ✅ How a deck gets built

1. **You describe the deck.** `/tedandlisa [what the deck is about]`
2. **The agent opens the intake panel** in your browser: which template, theme,
   artwork, logo, style, required components, languages, protected terms, menu,
   and what a reader can download. Every question has a default, and questions
   that do not apply to the chosen template are not asked — some templates add
   their own. **Sitemap & IA proposal** asks what kind of site it is, whether
   this is a new build or a revamp, what sitemap or crawl you already have,
   which benchmarks and competitors to argue against, and what evidence backs
   the recommendation.
3. **The agent builds from the chosen template**, composing only from that
   template's component library.
4. **The agent applies your answers** — theme, artwork, logo, menu shape, export
   controls, language set, and the protected-term list.
5. **The agent reviews the result** for cross-slide consistency, contrast in
   both themes, and behaviour at phone width, then reports what it fixed.
6. **You get one HTML file.** No build step, no dependencies to install.



---

## ✅ The intake panel

`assets/tedandlisa-intake.html` is a standalone page that collects the deck
settings. It runs as a short wizard: your prompt, then a gallery of template
screenshots, then one screen per chapter — Grounds, Shape, Look, Language,
Handover — each holding its two to five questions open at once, and finally
the finished payload. A progress rail across the top names the chapters and
sticks while a screen scrolls. Chapters with nothing to ask never appear, so
the rail is shorter for a slide handoff than for a sitemap proposal.

<p align="left">
  <img src="assets/tedandlisa-intake-panel.jpg" alt="The Hi Ted, Meet Lisa intake panel: an editable prompt field with a reference drop zone, an eleven-step progress bar, and the template gallery showing MonoMind deck, Web document, and Mermaid master as selectable cards" style="width: 100%; max-width: 100%;">
</p>

The runner serves it on loopback and captures the answers:

```sh
python3 scripts/tedandlisa_intake.py --prompt "the deck brief" --out intake.json
```

If Python or a browser is unavailable, the panel opens straight from disk and
falls back to a **Copy JSON** button you paste back into the conversation. The
payload is identical either way, and its contract is documented in
[`references/intake-contract.md`](references/intake-contract.md).

Uploads — cover artwork, a logo, a `design.md` — arrive as base64 data URIs,
which is the form the templates already embed.



---

## ✅ Design review

Before handover, the agent runs a design pass described in
[`references/design-review.md`](references/design-review.md). It uses your own
[Impeccable](https://github.com/pbakaus/impeccable) install when your agent has
one, the copy bundled at `.agents/skills/impeccable/` when it does not, and a
tooling-free checklist as the floor. The agent must say which reviewer ran.

The deck-specific checks are the ones that break first when slides are generated
one at a time: a single type scale, consistent slide anatomy, the brand mark in
the same place, no horizontal overflow at 375px, and contrast measured rather
than eyeballed.



---

## ✅ When a template is the wrong shape

Some decks should not be a MonoMind template at all: the look needs to be
someone else's.

```text
/tedandlisa-design
```

This wraps [Slides AI Plugin](https://github.com/proyecto26/slides-ai-plugin)
(MIT), carried here as a git submodule at `vendor/slides-ai-plugin/`. It brings
twelve style presets and animated single-file HTML decks — with MonoMind
branding applied unless you pick a
preset. PPTX generation needs `bun`.

The install above uses `--recurse-submodules`, so this is already populated. If
you cloned without it:

```sh
git submodule update --init --recursive
```

One thing it will not do: edit anything under `vendor/` — fixes belong
upstream. Every deliverable stays a standalone HTML file; the pipeline's
`.pptx` output is retired here.

## ✅ Add your own template

Any finished HTML page can become a template:

```text
/tedandlisa-new-template path/to/your-deck.html
```

The skill analyses the file, separates chrome from content, builds a placeholder
skeleton, writes its pattern reference, registers it, and captures its gallery
thumbnail. The source document is never copied into the repository — templates
carry the machinery, never the material.



---

## ✅ What is included

- **`tedandlisa`** — builds a deck: intake, template, content, review.
- **`tedandlisa-new-template`** — turns an existing HTML page into a template.
- **Four templates** with a pattern reference each, and a live preview.
- **A visual intake panel** with a template gallery, plus its payload contract.
- **A template registry** (`templates/templates.json`) and thumbnail tooling.
- **A bundled design reviewer**, so the review works without a separate install.
- **`tedandlisa-design`** — a branded wrapper over the vendored Slides AI
  pipeline, for decks that need a different look or animation.



---

## ✅ Agent implementation reference

The agent normally runs these itself; they are documented for transparency.

```sh
# collect the deck settings
python3 scripts/tedandlisa_intake.py --prompt "THE BRIEF" --out intake.json

# inspect an HTML file before turning it into a template (read-only)
python3 scripts/tedandlisa_new_template.py analyze SOURCE.html

# register a new template, then capture its gallery thumbnail
python3 scripts/tedandlisa_new_template.py register --id ID --name "NAME" \
  --file assets/tedandlisa-template-ID.html --kind slides
python3 scripts/tedandlisa_thumbs.py --only ID

# regenerate the intake panel's file:// fallback list from the registry
python3 scripts/tedandlisa_intake_fallback.py
```

Everything is Python standard library. Thumbnail capture uses headless Chrome
when it is present; without it the gallery falls back to text cards.



---

## ✅ Safety guarantees

- **Placeholders are never shipped.** A figure the agent does not have stays a
  bracketed slot for you to fill, rather than becoming an invented number.
- **Identifiers are protected before translation runs.** Google Translate once
  rendered *MonoMind AI Lab* as 人工智慧實驗室 and *MIT* as the university; the
  protection list exists because of it.
- **Source documents stay out of this repository.** Turning a real deck into a
  template extracts its system, not its content.
- **Load-bearing scripts are not rewritten quietly.** An agent that believes one
  must change is instructed to say so instead.



---

## ✅ License

[MIT + Commons Clause](LICENSE)

Use it freely, including commercially — build with it, ship what you make with
it. The one thing the Commons Clause withholds is selling the components
themselves: not alone, not bundled, not as a port.

This distribution bundles some awesome projects:  

- [Impeccable](https://github.com/pbakaus/impeccable) under the Apache License 2.0
- derives the architecture template's visual system from [Architecture Diagram Generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT)
- and carries [Slides AI Plugin](https://github.com/proyecto26/slides-ai-plugin) (MIT) as a submodule.

See [NOTICE](NOTICE) and [`.agents/skills/impeccable/VENDORED.md`](.agents/skills/impeccable/VENDORED.md).
