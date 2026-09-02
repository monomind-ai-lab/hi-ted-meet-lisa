# Applying the answers

Every answer changes the file. Work through them after the content is written,
and delete what was not asked for — an unused control left in the markup is a
feature the user did not choose.

Most rows are pure text surgery, and `scripts/tedandlisa_apply.py` performs
those:

```sh
python3 scripts/tedandlisa_apply.py --answers intake.json --file deck.html
```

It prints one line per answer — `APPLIED`, `SKIPPED (reason)`, or
`NOT-MECHANICAL (left to the agent)` — never guesses at a missing anchor, and
is safe to run twice. The agent then does by hand only the rows the report
left: every `NOT-MECHANICAL` line and any `SKIPPED` line whose reason is not
"already applied".

This file is the authority for what each answer *means*, and the manual
fallback when the script cannot run at all — a chat sandbox with no shell
applies every row by hand from the table below. Each row is marked
**[script]** (`tedandlisa_apply.py` handles it) or **[agent]** (a judgment
call the agent always does), with the exceptions noted inline.

| Answer | Who | What to do in the file |
| --- | --- | --- |
| `template` | [agent] | Decides which file you copied and which pattern reference governs. The script reads it too — it picks the anchors for everything below. |
| `theme: dark` | [script] | Delete the `html[data-theme="light"]` block and the theme control. |
| `theme: light` | [script] | Put `data-theme="light"` on `<html>`; delete the theme control. |
| `theme: toggle` | [script] | Keep both. The control persists the choice to `localStorage`. |
| `slideCount` | [agent] | `auto` sizes from the brief; a number is a target, not a quota — never pad to reach it. |
| `backgrounds: monomind` | [script] | Keep the embedded artwork as is. |
| `backgrounds: upload` | [agent] | Replace the `data:` URI in the cover and closing slides with the supplied one. |
| `backgrounds: gradient` | [script] | Delete `is-photo` from those slides and remove the embedded artwork — this is what makes a small file. |
| `logo: monomind` | [agent] | Leave the mark and its link alone. |
| `logo: custom` | [agent] | Swap the mark's `src` for the supplied file and point its link at `logo.href`. |
| `style: default` | [agent] | Change nothing. |
| `style: designmd` | [agent] | Read the supplied `design.md` and apply it to the token block, not to individual rules. Report any rule you could not honour. |
| `style: prompt` | [agent] | Apply `style.notes` the same way — through the tokens. |
| `style: brand` | [agent] | Run the `/lisa-brand` extraction first — the whole procedure in `skills/lisa-brand/SKILL.md`, confirmation included — on `style.url` / `style.file`, then apply the `brand/design.md` it wrote exactly like `style: designmd`: through the tokens, on the mapping in `references/brand-extraction.md`, never per element. Fonts follow the two-edit rule below. Precedence: an explicit hex in `accent` wins over the brand's `--accent`; `accent: default` lets the brand's `--accent` apply. Append the `design.md`'s never-translate terms to `noTranslate`. Report what was extracted, approximated, and dropped, and name the `design.md` so the next deck starts from it. |
| `style` asks for fonts | [agent] | A font change is **two edits, both required**: repoint the template's font tokens (`--font-display`, `--font-body`, `--font-mono` in the MonoMind deck; other templates name theirs differently) *and* update the Google Fonts `<link>` in the head. The link is chrome outside the fences, and this is the one sanctioned reason to touch it. Changing only the tokens is the silent failure: the requested face never loads and the fallback renders with no error. Keep a real fallback stack after the new family — never a bare name. Interactions below the table. |
| `accent` | [script] | `default` keeps the template's own accent. A hex value is repointed through the accent tokens only — never per element — with derived shades computed by channel math, so the design review re-checks contrast. On `architecture` the script deliberately does **not** apply it: that template's colour is semantic, and the report says so — the agent states in the handover that the accent was not honoured rather than silently repainting meaning. |
| `elements` | [agent] | Every named component must actually appear. If the content gives one nothing to say, say so rather than inventing filler for it. |
| `languages` | [script] on `monomind-deck`; [agent] everywhere else | Trim or extend the language switch to exactly this set. English always stays — and when English is *all* that is left, delete the switch, the `#google_translate_element` div and the translate script entirely, not just the surplus buttons; a one-language switch is a control that does nothing. The script does all of this on the MonoMind deck. On every other template each language is written inline, so trimming or adding one is content work — the script reports it `NOT-MECHANICAL`. Never infer a language from the subject: a deck *about* a Taiwanese client is not a request for Chinese. Only this answer decides. |
| `noTranslate` | [script] | Append every term to the protection list in the language-switch script (MonoMind deck). The web document needs no list — nothing is machine-translated. |
| `menu.mode: full` | [script] | Keep the menu; delete the items not in `menu.items`. |
| `menu.items` | [script] | `contents` builds itself from `data-screen-label`. `home` and `github` take their URLs from `menu.home` / `menu.github` — delete the item if its URL is empty. `theme`, `html` must agree with the theme and export answers. |
| `menu.mode: minimal` | [script] | Remove `hidden` from `#deck-restart` and delete the whole `.deck-menu` nav. |
| `menu.mode: none` | [script] | Delete both. On templates whose navigation *is* their content (the hash-routed documents), there is no deck-menu chrome; any trimming of the site nav is reported to the agent. |
| `siteType` | [agent] | Shapes the top level. A documentation site is organised around tasks; a catalogue around browse-and-compare. Do not reuse the template's default seven sections without asking whether they fit. |
| `projectStage: revamp` / `merge` | [agent] | The diagnosis page is mandatory, and the counts must be real. Redirects for the existing URLs belong in the open questions unless someone owns them. |
| `projectStage: new` | [agent] | Delete the diagnosis table rather than inventing evidence for a site that does not exist yet. |
| `sitemapSource: upload` | [agent] | Build the proposed structure **from** the attachment. Say which parts you changed and why — a reviewer who supplied a sitemap will look for their own labels first. |
| `sitemapSource: none` | [agent] | Propose one from the brief, and say plainly in the open questions that it is reasoned rather than derived. |
| `benchmarks` | [agent] | Name the sites in the document, and say what each one does that the proposal borrows or rejects. An unattributed "best practice" is not an argument. |
| `evidence` | [agent] | Every dimension picked should appear as evidence in the diagnosis table. Every one **not** picked that the argument leans on belongs in the open questions — this is the answer that keeps the proposal honest. |
| `prototype: both` | [agent] | Keep both `.mmfig` cards and all six payload blocks. |
| `prototype: desktop` | [agent] | Delete the mobile card, `mmStyleMobile`, `mmBodyMobile`, `mmScriptMobile`, and the `popup('mobile')` handler. |
| `prototype: none` | [agent] | Delete the whole `megamenu` page, its nav entry, its `PAGES` entry, the payload blocks, the mount script, and the `.mm*` CSS. |
| `delivery: cdn` | [agent] | The shipped state — leave the CDN references as they are. Nothing to do. |
| `delivery: standalone` | [agent] | Inline mermaid, the webfonts, Font Awesome and Tailwind. **Subset the webfonts to the glyphs the document actually renders** — the CJK family is several megabytes unsubsetted, and Google Fonts' `text=` parameter does the subsetting for you. Each family arrives as one variable font: declare it once across a weight range rather than once per weight. |
| `export: html` | [script] | Keep the self-download control. `mermaid-master` ships none — adding one there is the agent's work, and the script says so. |
| no export | [script] | Delete the self-download control. The `@media print` block stays — it serves the browser's own print, not an export control. |
| `credit: true` or absent | [script] | Keep the colophon — the "Made with Hi Ted, Meet Lisa" line every template carries in its footer or closing slide, linking to html.monomind.one. Each pattern reference shows the exact markup. |
| `credit: false` | [script] | Delete that one line only. The brand mark and any identity links stay — they belong to the `logo` answer, not this one. |
| `review` | [agent] | No file transform at all — the script ignores it by design. It schedules when the design pass runs relative to handover; see `references/design-review.md`. |
| `contract` | [agent] | No file transform — the script reports it `NOT-MECHANICAL`. It shapes the writing, not the chrome, so it is read **before** the content is written, not after; what each field does is below. |

**Fonts a `design.md` or `style.notes` requests.** The scaffold rule — never
a font the template does not load — forbids *inventing* fonts for new
components; it does not forbid a face the user's `design.md` asked for,
because after the swap above the template does load it. Two answers interact.
`delivery: standalone` inlines the new family, so it must be subset per that
row (Google Fonts' `text=` parameter; a CJK family is several megabytes
unsubsetted) — and subsetting has an honest cost to state in the handover:
glyphs typed into the file after the build are not in the subset and fall
back. On `monomind-deck`, if the new family's name could read as a
translatable word, add it to the `TERMS` protection list in the
language-switch script — the same class of failure that turned "MIT" into the
university.

**The contract shapes the writing.** `answers.contract` is read before the
first line is written, and each field decides something concrete:

- `audience` — pitch the vocabulary and the assumed knowledge at these
  people. `null` means infer them from the brief and name the assumption in
  the handover.
- `purpose` — `persuade`: every section closes on a verdict and shows its
  evidence. `decide`: an explicit ask slide or section — the decision, the
  options, the recommendation, and by when. `align`: the shared position
  stated, and the open disagreements named. `teach`: steps and worked
  examples over claims. `report`: what happened, where it stands, what
  changed since last time. `mobilize`: end on what to do next, and who does
  it. `record`: dates, sources and definitions written out — nothing that
  only makes sense in the room. `inform` and `explain` are the floor every
  build has.
- `outcome` and `coreMessage` — the arc is built so the outcome is what a
  reader is left holding, and the closing slide or section says the core
  message in its own words. `null` means derive them from the brief and say
  so in the handover.
- `delivery` — `presenter`: one idea per slide, larger type; the speaker
  carries the connective tissue. `reader`: denser text, captions that carry
  the point, headings that read as a summary on their own. `hybrid`: build
  for the presenter, then make every slide stand unread — a caption or a
  takeaway line each. `recorded`: no slide may depend on a voice.
- `afterlife` — `approval` and `archive`: dated, self-contained, printable —
  the decision or the record written out in full, nothing left to memory.
  `review`: numbered sections a comment can point at. `handoff`: the next
  owner's questions answered — status, contacts, open items. `reuse`:
  sections that stand alone when lifted. `share`, the default: readable by
  someone who was not there.
- `divergence` — `close`: keep the source's own labels, order and figures,
  and list in the handover what was changed and why. `moderate`: restructure
  where it reads better, keep the substance. `free`: rebuild the argument
  from the material.

After applying them, re-run the verification checklist in
`skills/lisa/SKILL.md`: these edits touch chrome, which is exactly what the
responsive and translation checks cover.
