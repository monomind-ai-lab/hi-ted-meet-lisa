# Vendored copy — Impeccable

This directory is an unmodified copy of the Impeccable design skill, bundled so
that `/tedandlisa` can run its design review pass on a generated deck even
when the user has not installed Impeccable themselves.

| | |
| --- | --- |
| Upstream | https://github.com/pbakaus/impeccable |
| Author | pbakaus |
| Version | 3.6.0 |
| Vendored on | 2026-08-27 |
| License | Apache License 2.0 — see `LICENSE` |
| Modifications | None. Installed via `npx impeccable install --scope=project --no-hooks` and committed as-is. |

Hi Ted, Meet Lisa is MIT licensed; this directory is not. Everything under
`.agents/skills/impeccable/` remains under Apache 2.0, and `NOTICE.md` carries
Impeccable's own third-party attributions.

**Do not edit these files.** Local changes would make the copy a modified
derivative and would be lost on the next refresh:

```sh
npx impeccable@latest install --providers=codex --scope=project --no-hooks
```

Deck-specific review criteria live in `references/design-review.md`, outside
this directory, so MonoMind guidance never mixes into vendored files.
