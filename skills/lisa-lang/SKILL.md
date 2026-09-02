---
name: lisa-lang
description: "Use when a finished Hi Ted, Meet Lisa HTML file needs another language — including phrases like /lisa-lang, \"add Korean to this deck\", \"translate this deck\", \"translate this document\", or \"add a language\". Layers new languages onto a deck, document, or page /lisa already produced, using that template's own language mechanism, and wires each one into the language switch."
---

# Hi Ted, Meet Lisa languages

> Every path below — `references/`, `templates/`, `skills/` — is relative to
> the **Hi Ted, Meet Lisa root**: the plugin's own directory when installed as
> a plugin (`${CLAUDE_PLUGIN_ROOT}` in Claude Code), or the repository checkout
> when you are reading this from source. With neither, every path is fetchable
> at `https://raw.githubusercontent.com/monomind-ai-lab/hi-ted-meet-lisa/main/<path>`.

The intake promises that `languages` is stageable: build in one language now,
layer more onto the finished file later. This skill is the layering. It edits a
delivered file in place — it never rebuilds one.

## Invocation

    /lisa-lang [path/to/file.html] [language …]

No path? The file this session just built, or the most recent generated deck
in the working directory — ask if more than one is plausible. No language?
Ask; never guess which one was meant.

## Procedure

1. **Identify the template family.** The design tokens and chrome give it
   away, and `templates/templates.json` names them all. The language mechanism
   differs per family, and the mechanism decides the work. A file from no Lisa
   template still qualifies — find how *it* does language and extend that.

2. **State the cost up front, per language** — the same way `/lisa` does. For
   `monomind-deck` a new language is minutes: it machine-translates on demand.
   For every inline-language template each language is roughly a full writing
   pass — every reader-visible string, written again. One line, then start.

3. **`monomind-deck`: extend the switch, protect the terms.** Add the language
   to the switch in script block 1 (never rewrite the block — the same rule
   `/lisa` builds under) and extend the known-terms TERMS regex for any name
   the deck introduced. The translation-safety rules in `skills/lisa/SKILL.md`
   (step 6 and its checklist) apply unchanged: filenames, commands, paths, and
   product names must survive Google Translate — read the translated output,
   do not assume. Nothing else needs writing.

4. **Inline-language templates: write each language as a full pass** over the
   `LISA:CONTENT` fenced regions — and only those, plus the edit points the
   file's `LISA:CONTENT-MAP` names. Read how **this file** carries its
   existing languages and mirror that structure exactly; do not import another
   template's mechanism. The shapes in the shipped families:
   - paired per-language spans toggled by `body[data-lang]` (`web-document`,
     `project-website`, `sitemap-ia`, `architecture`) — every placeholder that
     holds two spans gets a third;
   - per-language slide sets (`mermaid-master`: `s-en-NN` / `s-ko-NN`) — a
     whole new set per language, **including the script arrays the
     CONTENT-MAP names** (`ROUTES`, `TITLES`), which must stay in step;
   - per-language labels and titles (`evidence-deck`, `paper-brief`:
     `data-label-en/ko`, `body data-title-*`) alongside the paired text.
   The pattern reference (`references/slide-patterns-<id>.md`) shows the
   markup; the file itself is the authority. A Korean or Traditional Chinese
   pass also follows `references/cjk-typography.md`, whichever mechanism
   carries it.

5. **Give every language a reachable control.** Extend the language switch —
   toggle buttons, the `langToggle` chip cycle, whatever this file uses — so
   each new language can actually be selected. Count controls against
   languages by hand, the same rule as `/lisa` step 8: content nobody can
   reach is the same as not writing it.

## Verify

Open the file and switch into every language, new and old: full prose in each,
no string left in the wrong language, filenames and product names untouched,
switching back restores the original, nothing overflows at 375px. In a sandbox
the browser checks cannot run: say which you skipped rather than implying a
clean pass, and tell the reader how — serve over http, cycle the switch, look
for console errors and horizontal overflow at 375px — the same convention as
`/lisa-review`. Never call a language added on the strength of the checks that
happened to be possible.
