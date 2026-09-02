---
name: lisa-motion
description: "Use when a finished HTML file should move — including phrases like /lisa-motion, \"animate this page\", \"add a reveal on scroll\", \"make the numbers count up\", \"add a typewriter to the command\", or \"give this deck some motion\". Applies dependency-free animation patterns (CSS and the Web Animations API, no library) from the Hi Ted, Meet Lisa motion library to a file /lisa produced, or to any standalone HTML page the user points at, and composes a new pattern under the same rules when none fits."
---

# Hi Ted, Meet Lisa motion

> Every path below — `references/`, `assets/`, `templates/` — is relative to
> the **Hi Ted, Meet Lisa root**: the plugin's own directory when installed as
> a plugin (`${CLAUDE_PLUGIN_ROOT}` in Claude Code), or the repository checkout
> when you are reading this from source. Resolve them there, not against
> whatever project you happen to be working in. With neither, every path is
> fetchable at
> `https://raw.githubusercontent.com/monomind-ai-lab/hi-ted-meet-lisa/main/<path>`.

Yes: animation here is generated without a library. Everything this skill
adds is CSS, or the Web Animations API where CSS cannot do it (`D-015` —
no GSAP, no Anime.js, no Motion, nothing loaded), so the file stays one
standalone HTML file (`D-001`). The patterns live in
`references/motion-patterns.md`: thirty-nine of them, each verbatim, each
verified in a browser under reduced motion, in print, in a hidden tab, and
at 375px. This skill applies them, and when none fits it composes a new one
under the same rules and offers to add it to the library.

## Invocation

    /lisa-motion [path/to/file.html] [what to animate]

No path? If this session just built a file, that file is the target;
otherwise the most recently generated deck, document, or page in the
working directory — and if more than one is plausible, ask. No brief?
Propose one moment (see step 2) rather than animating everything.

## Procedure

1. **Read the library first** — `references/motion-patterns.md`, the
   opening rules and the runtime section in full, then the patterns that
   match the brief. Nothing is invented from memory: every snippet in the
   file is known-good, and re-deriving one is how reduced motion, print, or
   the fail-visible timer gets dropped.

2. **Identify the file and pick the moment.** Work out which template
   family it comes from (`templates/templates.json` names them; the design
   tokens give it away) or whether it is a page of the user's own. Then
   decide *the one place* a reader should notice: a site is read, not
   watched (rule 10). Say the plan in a few lines before editing — which
   patterns, on which elements, and what stays still — and adjust to what
   the user says.

3. **Wire the runtime once.** Three blocks, verbatim from the library's
   runtime section: the **bridge** (`--lm-*` mapped onto *this file's* own
   tokens — read its `:root` and point each name at the right one; never at
   a hex), the **base**, and the **script**. In a hash-routed file
   (`project-website`, `web-document`, `sitemap-ia`, `motion-website`) the
   script goes in its own `<script>` block **after** the router; it hooks
   `hashchange` one registration later and never edits `apply()`. A file
   that has both `lm-*` patterns and the self-download control also gets
   the strip block from "Applying a pattern to a hash-routed file". A file
   built from `motion-website` already carries all of this — skip to 4.

4. **Apply the patterns inside the fences.** Edit only between the file's
   `LISA:CONTENT-START` / `END` markers plus the edit points its
   `LISA:CONTENT-MAP` names; add pattern CSS and JS as **new** style and
   script blocks, never inside the file's own. Copy each pattern's markup,
   CSS, and JS verbatim; the only things you change are the content, the
   `--i` / `--h` / `data-lm-*` values, and the bridge. Anything already
   animated by the file (a `.reveal` fade, a flowing track) stays as it is
   unless the brief says otherwise — two mechanisms on one element is the
   commonest mistake.

5. **When no pattern fits, compose one under the same rules** — all
   eleven of them, in the library's opening section, with the runtime's
   `lm.onActivate` / `lm.whenIn` as the only hooks. Write it in the
   library's form: markup, CSS, JS if any, the trap, the rule. Verify it
   exactly as step 6 does. Then **offer** to add it to
   `references/motion-patterns.md`, numbered after the last pattern and
   listed in "Known gaps" if it has a browser-support or reduced-motion
   caveat. Adding is a contribution to the shared library and is never
   silent: ask, and only write it when the user says yes.

6. **Verify** — every box, in a browser, over `http://`:
   - [ ] No console errors on load, on every route, and in both languages
         where the file has two.
   - [ ] **Reduced motion** (Chrome `--force-prefers-reduced-motion`, or the
         OS setting): the finished state, nothing moving, every control
         still working. `document.getAnimations()` is empty apart from
         scroll-linked indicators.
   - [ ] **Print** (`--print-to-pdf`): every page in its finished state,
         gradient text solid.
   - [ ] **Hidden tab / no observer** (`L-022`): open the file in a
         background tab, wait two seconds, switch to it — nothing blank.
         Stub `IntersectionObserver` and reload — still nothing blank after
         1.2s.
   - [ ] **375px**: no horizontal overflow (`scripts/check_overflow.py`
         where the checkout has it); cursor patterns absent, their keyboard
         or button path present.
   - [ ] **Route away** from a page (hash-routed files): every
         `requestAnimationFrame` loop and WAAPI animation cancelled —
         `document.getAnimations()` empty, the frame counter back to idle.
   - [ ] **Scroll through** every page: every `lm-on` / `lm-reveal`
         element ends up `.is-in` (rule 11 if one does not).
   - [ ] **Keyboard**: every clickable pattern reachable with Tab, a
         visible ring, and Enter or Space doing what a click does.

7. **Report**: the moment you chose and why, which patterns went where,
   what you deliberately left still, which checks ran and which did not,
   and — if you composed a pattern — the offer to contribute it.

## In a sandbox

A hosted chat sandbox has no browser, and every check in step 6 needs one.
Wire the runtime, apply the patterns, run the static checks (the bridge
names real tokens; every `lm-on` element has content; no `clip-path` on an
observed element; the script block sits after the router), then say
plainly which checks you skipped and how the user runs them — serve the
file over http, open it in a background tab, print it, emulate reduced
motion, look for console errors and horizontal overflow at 375px — the same
convention as `/lisa-review`. Never call a file animated on the strength of
the checks that happened to be possible.

## What not to do

- Do not load an animation library, inline one, or write a helper that is
  one in disguise (`D-015`). If the brief needs sequenced timelines or
  spring physics that CSS and WAAPI cannot give, say so and stop.
- Do not put a pattern on every section. The library's rule 10 is the whole
  craft; the source demos this library re-implements were single-effect
  pages for a reason.
- Do not rewrite the file's router, deck navigation, or diagram viewer to
  make room for motion — add blocks beside them (`D-002`, `D-041`).
- Do not let an observer be the only path to visible, and do not put the
  hiding geometry on the observed element (rules 4 and 11).
- Do not change the file's design tokens. The bridge maps onto them; it
  never adds a value of its own.
