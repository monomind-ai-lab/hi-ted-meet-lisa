# Vendored: Archify

Copied from [tt-a1i/archify](https://github.com/tt-a1i/archify), MIT licensed,
at tag `v2.16.0` — commit `c826e6c3a7abad19c0f3cd1ca57207d54b1ad8de`
(2026-08-30).

Copied for the same reason `slides-ai-plugin` is: a submodule does not travel
with a plugin install, and a diagram skill that cannot find its renderer is
worse than no skill. The files are copied in, so `/lisa-diagram` always has a
compiler to run.

**A released tag, not `main`.** Upstream's default branch carries a
`-dev` version (`2.17.0-dev.1` when this was copied). Vendor releases only —
a dev HEAD inside a shipped plugin is someone else's work in progress.

**Do not edit anything in this directory.** Fixes belong upstream. To update,
re-copy from a newer *tag* and change the commit above.

## What this needs to run

Node 18 or newer, and nothing else. Upstream's `ajv` and `simple-icons` are
`devDependencies` used by two code generators; their output is committed at
`renderers/shared/generated-validators.mjs` and
`renderers/shared/generated-brand-marks.mjs`, so **no `npm install` is
required** and none is run. Verified against this copy:
`node bin/archify.mjs validate architecture examples/web-app.architecture.json
--quality showcase` passes all 9 artifact checks, and `render` writes a
complete 715 KB artifact.

This is the one place in the repository that wants Node. Every other path here
is Python stdlib and a Chromium binary, as `CLAUDE.md` says — the dependency is
scoped to this card and does not reach the templates.

## Copied

`SKILL.md`, `bin/`, `renderers/`, `schemas/`, `references/`, `recipes/`,
`brand-marks/`, `assets/`, `delta/`, `migrations/`, `LICENSE`, `package.json`,
and the two `scripts/` the CLI actually shells out to
(`check-render-output.mjs`, `render-examples.mjs`).

`examples/` is copied **as JSON only**. The fast-authoring path in `SKILL.md`
reads one example per diagram type for field shape, so the specs are load-bearing;
upstream's rendered `.html` beside them are ~700 KB each and are output, not input.

## Deliberately not copied

| Omitted | Why |
| --- | --- |
| `test/` (1.6 MB) | Upstream's golden-file suite. Nothing here runs it, and it is the largest thing in the skill. |
| `examples/*.html` (3.5 MB) | Rendered output. `archify demo` regenerates any of them from the JSON that is here. |
| `scripts/generate-validators.mjs`, `scripts/generate-brand-marks.mjs` | Code generators, not runtime. They are the only importers of `ajv` and `simple-icons`; omitting them is what keeps this install-free. |
| `scripts/check-update.mjs`, `scripts/update-contract.mjs` | Upstream's self-update machinery. Updating this copy is a re-copy from a tag, not a command the skill runs. |
| `package-lock.json`, `skill-release.json` | Lockfile for devDependencies that are not installed, and upstream's own release metadata. |
| `THIRD_PARTY_NOTICES.md` | Not present at `v2.16.0`; upstream added it later. `LICENSE` is copied and is the operative notice. |

## Attribution

Archify is by `tt-a1i`, and is itself based on
[Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator)
(MIT, v1.0) — see the `based_on` field in `SKILL.md`.
