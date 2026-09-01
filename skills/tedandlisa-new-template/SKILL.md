---
name: tedandlisa-new-template
description: "Use when the user wants to turn an existing HTML deck, document, or page into a reusable Hi Ted, Meet Lisa template — including phrases like /tedandlisa-new-template, \"make a template from this\", \"add this design as a template\", or when they hand over an HTML file and ask for its style to be reusable. Extracts the visual system and machinery into a placeholder skeleton, registers it, and captures its gallery thumbnail."
---

# New Hi Ted, Meet Lisa template

> Every path below — `assets/`, `references/`, `scripts/`, `templates/` —
> is relative to the **Hi Ted, Meet Lisa root**: the plugin's own
> directory when installed as a plugin (`${CLAUDE_PLUGIN_ROOT}` in Claude
> Code), or the repository checkout when you are reading this from source.
> Resolve them there, not against whatever project you happen to be working
> in.

Turn one finished HTML file into a template `/tedandlisa` can build from.

A template is the **machinery without the content**: the stylesheet, the design
tokens, the chrome, the scripts, and one example of every component — with every
piece of the original's subject matter replaced by a bracketed slot.

## The rule that matters most

**The source file is almost always someone's real work.** Client architecture,
internal costs, unreleased plans, personal material. The skeleton goes into a
repository that may be public; the source does not.

- Never copy the source file into the repository.
- Never leave a client name, project name, hostname, price, headcount, date, or
  internal URL in the skeleton — not in markup, comments, `<title>`, mermaid
  diagrams, or example table rows.
- Grep the finished skeleton for the specifics you saw in the source and prove
  they are gone before registering it.
- Embedded images carry EXIF. Either drop the artwork from the skeleton or strip
  the metadata; do not ship someone's camera and authorship data by accident.

If the user asks for the source itself to be committed, say what it contains and
confirm before doing it.

## Procedure

1. **Take the file and read it.** Ask for a path if none was given.
2. **Analyze it**, which is read-only:

   ```sh
   python3 scripts/tedandlisa_new_template.py analyze SOURCE.html
   ```

   You get the token set, class inventory, section containers, script blocks,
   external dependencies, and how the file handles language. Read the actual
   stylesheet and scripts too — the report tells you what is there, not what it
   means.
3. **Decide chrome versus content, and say so.** Chrome is everything that would
   be identical in a different document by the same author: head, stylesheet,
   nav, footer, modals, and every script. Content is what changes. Show the user
   this split before building anything, along with the template's `kind`:
   `slides` for a presentation, `document` for something read and linked to.
4. **Build the skeleton** at `assets/tedandlisa-template-ID.html`:
   - Keep the head, the stylesheet, and **every script block verbatim.** Scripts
     in a working deck encode fixes for problems you cannot see. Do not tidy them.
   - Replace the content with 3–5 pages or slides that between them use every
     component worth keeping, each filled with `[BRACKETED]` slots.
   - Rewrite any hardcoded page register in the scripts — routing arrays, page
     id lists, nav entries — to match the skeleton's own sections.
   - Keep the original's language mechanism exactly as it is. A file with inline
     dual-language spans must keep both spans in every placeholder.
   - Annotate the traps in HTML comments: which ids must agree, what renders
     lazily, what must not be rewritten.
5. **Write the pattern reference** at `references/slide-patterns-ID.md` —
   verbatim markup for every component, plus the rules that are easy to get
   wrong. Model it on `references/slide-patterns-web-document.md`.
6. **Register it:**

   ```sh
   python3 scripts/tedandlisa_new_template.py register --id ID --name "NAME" \
     --file assets/tedandlisa-template-ID.html --kind slides|document \
     --type present|read|diagram|site \
     --tagline "..." --patterns references/slide-patterns-ID.md \
     --best-for "..." --dependencies "..."
   ```

   `--kind` is the **shape** and decides which intake questions are asked
   (`D-007`, `D-017`). `--type` is what the template is **for** — it is the
   flag on the gallery card and the filter above it, and it never reaches
   the payload (`D-034`). They are separate axes and cut across each other:
   `paper-brief` is `slides` you `read`, `architecture` is a `document` you
   `diagram` in. Pick the type from the reader's purpose, not the file's
   shape.
7. **Capture its thumbnail** so it appears in the intake gallery, and
   regenerate the panel's `file://` fallback list so the template is
   offerable with nothing injected:

   ```sh
   python3 scripts/tedandlisa_thumbs.py --only ID
   python3 scripts/tedandlisa_intake_fallback.py
   ```
8. **Verify in a browser**, served over http, not `file://`:
   - Every page or slide reachable; navigation, routing, and deep links work.
   - The language mechanism switches both ways and restores the original.
   - Diagrams, menus, modals, and viewers still function.
   - No console errors; nothing overflows horizontally at 375px.
   - No `[PLACEHOLDER]` renders as literal machinery — bracket characters inside
     mermaid or template syntax must be quoted.
   - Grep for the source's subject matter one last time.
9. **Report** the template's id, what it is for, its dependencies, and anything
   from the original you deliberately dropped.

## Registering a template the user already has

If they hand over a finished skeleton rather than a source document, skip to
step 6. Registration is create-only and refuses to overwrite an existing id.

## What not to do

- Do not restyle the source. A template preserves its author's system, including
  choices you would have made differently.
- Do not merge two sources into one template.
- Do not add a dependency the source did not have.
- Do not register a template you have not opened in a browser.
