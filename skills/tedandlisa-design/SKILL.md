---
name: tedandlisa-design
description: "Use when a deck needs more freedom than the MonoMind templates allow — including phrases like /tedandlisa-design, \"a deck in a different style\", \"pick a style preset\", \"animated slides\", or \"convert this deck\". Runs the vendored Slides AI pipeline with MonoMind branding applied, producing an animated single-file HTML deck."
---

# Hi Ted, Meet Lisa design

> Every path below — `scripts/`, `assets/`, `references/`, `vendor/` — is
> relative to the **Hi Ted, Meet Lisa repository root**, which is this skill's
> own directory when installed as `~/.claude/skills/tedandlisa`. Resolve them
> there, not against whatever project you happen to be working in.

The fifth way to make a deck here, and the only one that is not built from a
MonoMind template. Use it when the house templates are the wrong shape:

| Use this when | Use `/tedandlisa` when |
| --- | --- |
| The deck needs a look the templates do not have | The deck should look like MonoMind |
| The user wants to pick from many style presets | The house style is the point |
| An existing deck needs converting | Starting from a brief |

## What this wraps

`vendor/slides-ai-plugin/` is a git submodule — [Slides AI
Plugin](https://github.com/proyecto26/slides-ai-plugin) by proyecto26, MIT
licensed, vendored by reference rather than copied. It brings three skills:

| Skill | What it does |
| --- | --- |
| `slide-design` | The entry pipeline: plans content, then dispatches to one of the two below |
| `html-slides` | Animated single-file HTML deck (GSAP + CSS, viewport-fitted) |

If the directory is empty, the submodule was never initialised:

```sh
git submodule update --init --recursive
```

Say so and run it rather than improvising a substitute.

## Procedure

1. **Check the submodule is present.** `vendor/slides-ai-plugin/skills/` must
   contain the three skill folders.
2. **The output is animated HTML.** The vendored pipeline also carries a
   `.pptx` path — it is retired here; do not offer it. Every deliverable is
   one standalone HTML file.
3. **Read the vendored skill** you are about to run and follow it as written —
   `vendor/slides-ai-plugin/skills/slide-design/SKILL.md` is the entry point.
   Where it refers to `${CLAUDE_PLUGIN_ROOT}`, substitute the submodule path.
4. **Apply MonoMind branding** unless the user picked a different preset — see
   below. A deck made here should still be recognisable as ours.
5. **Hand over** with the file path, the format, and which style was used.

## MonoMind branding

The vendored pipeline offers twelve style presets. When the user wants a
MonoMind deck rather than one of those, supply these values instead of a preset:

| Token | Value |
| --- | --- |
| Ground | `#102033` deep ink |
| Page | `#eef6ff` |
| Accent | `#4f8cff` |
| Body text on ink | `#ffffff` at 72% for secondary |
| Display / body | Plus Jakarta Sans |
| Mono | JetBrains Mono |

The mark is `assets/monomind-mark-white.svg` — `currentColor`, so it takes the
colour of whatever chrome it sits in. Put it in the same corner on every slide
and link it to `https://monomind.one`.

## Languages

English and Korean are the MonoMind defaults, as in the templates. The vendored
pipeline has no bilingual mechanism of its own, so:

- **HTML output** — write both languages as sibling elements and toggle them,
  the way `assets/tedandlisa-template-web-document.html` does. Never machine
  translate at read time here; the animation timing assumes stable text.

Ask which languages before generating; do not assume bilingual.

## What not to do

- Do not copy the vendored skills into this repository. They are a submodule so
  that upstream stays upstream; a copy silently forks it.
- Do not edit anything under `vendor/`. Fixes belong upstream, and local edits
  are lost on the next update.
- Do not reach for this skill when the user asked for a MonoMind deck. The
  templates exist because the house style should not be re-derived per deck.
