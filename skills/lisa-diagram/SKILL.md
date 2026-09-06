---
name: lisa-diagram
description: "Use when a diagram has to be validated, explorable, or grounded in real code rather than drawn by hand — including phrases like /lisa-diagram, \"an interactive architecture diagram\", \"a sequence diagram from this API\", \"a data pipeline map\", \"a state machine\", \"diagram this repository\", \"convert this Mermaid\", or \"show what changed between these two architectures\". Runs the vendored Archify compiler, producing a self-contained interactive HTML diagram from typed JSON."
---

# Hi Ted, Meet Lisa diagram

> Every path below — `vendor/`, `assets/`, `references/` — is relative to the
> **Hi Ted, Meet Lisa repository root**, which is this skill's own parent
> directory when installed as a plugin. Resolve them there, not against
> whatever project you happen to be working in.

The second way to make something here that is not built from a MonoMind
template. Lisa's diagram templates are *drawn*: an agent writes the SVG by
hand, and what it says is only as true as the writing. Archify is *compiled*:
the topology is a typed JSON specification, a validator refuses a diagram whose
geometry or facts do not hold, and the reader gets a viewer that can search,
focus, and trace the graph.

| Use this when | Use `/lisa` when |
| --- | --- |
| The diagram must be checked, not just drawn | The diagram illustrates an argument |
| It maps a real system — a repo, a request path, a pipeline | It is one figure inside a deck or a document |
| The reader will explore it: search, focus, trace, compare | The reader will read it once, in place |
| Two versions need a before / after delta | There is one version |
| A sequence, data-flow, or state machine is the right shape | Neither `architecture` nor `mermaid-master` fits |

`architecture` and `mermaid-master` are still the right answer for a diagram
that lives inside a larger document, carries MonoMind's own look, and needs no
runtime. Reach here when the diagram *is* the deliverable.

## What this wraps

`vendor/archify/` is [Archify](https://github.com/tt-a1i/archify) by `tt-a1i`,
MIT licensed, copied into this repository at tag `v2.16.0`. It is a renderer
and validator, not a prompt: agents author typed JSON, and Archify compiles it
deterministically into HTML with inline SVG.

`vendor/archify/VENDORED.md` records the upstream tag, what was copied, and
what was deliberately left out. Read it before you assume a file is missing.

Five diagram types, one per shape:

| Type | Use for |
| --- | --- |
| `architecture` | Components, services, cloud / security boundaries, infrastructure |
| `workflow` | Processes, approval gates, tool calls, runbooks, CI/CD |
| `sequence` | API call chains, request lifecycles, async traces, returns |
| `dataflow` | Pipelines, ETL/ELT, lineage, governance, consumers |
| `lifecycle` | State and status transitions, retries, waiting and terminal states |

## Procedure

1. **Check the compiler is present and can run.** `vendor/archify/bin/` must
   contain `archify.mjs`, and `node --version` must report 18 or newer.
   Both are committed or already on the machine, so a failure here is an
   install problem — say so rather than improvising a substitute or falling
   back to hand-drawn SVG without telling the user.

   ```sh
   node vendor/archify/bin/archify.mjs doctor
   ```

   **This is the only path in the repository that wants Node.** Nothing else
   here does (`CLAUDE.md`), and no `npm install` is needed or run — upstream's
   two dependencies are code generators whose output is committed.

2. **Read the vendored skill and follow it as written.**
   `vendor/archify/SKILL.md` is the entry point and owns the authoring
   contract. Where it says `bin/`, `schemas/`, `examples/` or
   `references/`, resolve them under `vendor/archify/`. Where it refers to
   `scripts/check-update.mjs`, that script is deliberately not vendored;
   upstream's own instruction covers this — continue without mentioning the
   check.

3. **Author, validate, deliver.** Never hand-edit the compiled HTML. Every
   node position, arrow route, and label anchor in that file is solver output,
   and editing it desynchronises the artifact from the specification it was
   checked against. Changes go into the JSON and are recompiled.

   ```sh
   node vendor/archify/bin/archify.mjs validate <type> spec.json --quality showcase --json
   node vendor/archify/bin/archify.mjs deliver  <type> spec.json out.html
   ```

   A showcase pass is 9 artifact checks with 0 errors and 0 warnings. Do not
   hand over on a 4-check basic pass and call it verified.

4. **Keep the JSON with the HTML.** The specification is the editable source;
   the artifact is output. Hand over both, and say which one to change.

5. **Hand over** with both paths, the diagram type, the validation receipt, and
   anything the user asked for that Archify's contract would not let you assert.

## Applying the intake answers

When the user came through the intake panel, the payload's `handoff` named this
skill and the answers were already filtered to the questions this path asks.
They do not all map onto a compiler, and inventing a mapping is worse than
saying so:

| Answer | What it does here |
| --- | --- |
| `contract` | Shapes the wording of labels, the title, and the handover — never the topology. A relationship label is semantic data; it says what actually happens, whatever the brief wanted to emphasise. |
| `theme` | Archify ships both grounds and a switch. `dark` or `light` picks the opening mode; `toggle` is what the artifact already does. |
| `accent` | Colour is **semantic** here — it encodes component type, not decoration, the same reason the `architecture` template honours accents only partially. Do not repaint node types to a brand colour. Say so in the handover rather than silently recolouring meaning. |
| `logo` | An optional, explicit `brand` fact on a node that names a real product. Never infer one from a role like "database". A badge never replaces the node's type or label. |
| `credit` | `true` keeps the "Made with Hi Ted, Meet Lisa" colophon; add it as authored content, not by editing the compiled file. |
| `languages` | See below — this is the one that needs a straight answer. |
| `slideCount`, `backgrounds`, `menu`, `export`, `delivery` | Deck and document machinery. They have no counterpart in a compiled diagram; do not simulate them. |

## Languages

Say this plainly rather than discovering it at handover. Archify's
`meta.locale` translates the **viewer's own UI** and supports `en` and `zh-CN`.
Authored content — every node label, relationship, and title — is written in
whatever language you author it in; the renderer never translates it.

So for MonoMind's usual English + Korean: author the content in the requested
language, omit `meta.locale`, and **tell the user** that the viewer chrome and
`<html lang>` fall back to English. There is no inline dual-language mechanism
here the way `web-document` has one, and one artifact carries one authored
language. Two languages means two artifacts, and `/lisa-lang` does not apply —
it edits templates, not compiler output.

## What not to do

- Do not edit anything under `vendor/`. It is a copy of an upstream tag; local
  edits silently fork it and are lost on the next re-copy. Fixes belong
  upstream.
- Do not hand-edit the delivered HTML. See step 3.
- Do not reach for this skill for a figure inside a deck or a document — that
  is what `architecture` and `mermaid-master` are for, and they cost no
  runtime.
- Do not assert topology the user did not give you. Archify's whole claim is
  that what it draws is authored or verified; a plausible-looking invented
  service breaks that, quietly, in a file that looks checked.
