# Vendored: Slides AI Plugin

Copied verbatim from [proyecto26/slides-ai-plugin](https://github.com/proyecto26/slides-ai-plugin),
MIT licensed, at commit `1f8505f3a89e6cafd863ebbd0ed8b465db4f3820` (2026-04-13).

This was a git submodule until it became clear that submodules do not travel
with a plugin install: anyone who installed the plugin got an empty directory
and a design skill that could not run. The files are copied in instead.

**Do not edit anything in this directory.** Fixes belong upstream. To update,
re-copy from a newer upstream commit and change the commit above.

Copied: `skills/`, `LICENSE`, `README.md`.

Deliberately not copied:

| Omitted | Why |
| --- | --- |
| `.claude-plugin/` | Upstream's own `plugin.json` and `marketplace.json`. A second manifest inside this plugin would be ambiguous at best. |
| `hooks/` | Upstream hooks would run inside our plugin. Nothing here needs them. |
| `.gitignore` | Ignores `templates/`, which would apply to this subtree. |

`skills/pptx-slides/` is copied for fidelity but unused: its TypeScript needs
`bun`, and `/lisa-design` retires the `.pptx` path in favour of standalone
HTML. See `skills/lisa-design/SKILL.md`.
