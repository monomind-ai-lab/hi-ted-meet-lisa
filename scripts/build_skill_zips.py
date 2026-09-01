#!/usr/bin/env python3
"""Build one uploadable ZIP per skill, for Claude and ChatGPT.

Claude Code and Codex install this repository as a plugin and read the skills
straight out of `skills/`. The two chat surfaces cannot: they take a skill as a
ZIP through a settings panel, one skill at a time.

    Claude    Customize -> Skills -> + -> Create skill -> Upload a skill
    ChatGPT   Plugins -> Skills -> Create -> Upload from your computer

Both want the same shape — a single top-level folder whose name matches the
skill, with `SKILL.md` at its top:

    lisa/
      SKILL.md
      assets/  references/  scripts/  templates/
      LICENSE  NOTICE

That flattening is the whole reason this script exists. In the repository a
skill's paths resolve against the *repository root*, one level above
`skills/<name>/`; inside a ZIP the skill folder is the only root there is. So
the shared payload is copied in beside SKILL.md, which makes every
`assets/...` and `references/...` path in the skill resolve unchanged.

Each skill gets its own copy of the payload. That duplicates a few megabytes
across the bundles, which is the right trade: an uploaded skill is sandboxed
and cannot reach a sibling.

    python3 scripts/build_skill_zips.py            # write dist/*.zip
    python3 scripts/build_skill_zips.py --check    # validate, write nothing

Not in the payload: the public website. `site/`, `functions/` and the nine
preview decks under `previews/` moved to monomind-ai-lab/ted-and-lisa, so
there is nothing left in this repository to leave out. `previews/` was never
purely a website artifact — the intake runner used to serve those decks to the
panel's "Preview" links — but it points them at html.monomind.one now, so a
bundle without them is still a bundle that works. `.git/` is left out too:
14 MB of history the panels have no use for.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Copied into every bundle: the four directories the skills actually read,
# plus the licence files, because a ZIP is a redistribution.
# `vendor/` matters: /lisa-design reads vendor/slides-ai-plugin/, so an
# uploaded bundle without it is a skill that cannot run.
PAYLOAD_DIRS = ("assets", "references", "scripts", "templates", "vendor")

# Carried only by the bundles that actually use them, and at their original
# paths, because the skills name those paths. The bundled design reviewer is
# 3.5 MB and only /lisa runs the design pass (step 10); without it an uploaded
# /lisa silently drops to the tooling-free floor of references/design-review.md.
EXTRA_PAYLOAD = {
    "lisa": (".agents/skills/impeccable",),
}

# Built for completeness, but say plainly which ones are worth uploading. A
# bundle is only worth a panel slot if the skill can finish its job there.
UPLOAD_NOTES = {
    "lisa-new-template": "registry writes and thumbnails need a local checkout — "
                         "a hosted upload can only hand back a skeleton",
}
PAYLOAD_FILES = ("LICENSE", "NOTICE")

# Claude caps a custom skill upload at 30 MB uncompressed. ChatGPT does not
# publish a number; this is the tighter of the two, so it is the one to hold.
MAX_UNCOMPRESSED = 30 * 1024 * 1024

IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "intake.json")


def discover_skills() -> list[pathlib.Path]:
    found = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    if not found:
        sys.exit("no skills found under skills/ — is this the repository root?")
    return found


def stage(skill: pathlib.Path, into: pathlib.Path) -> pathlib.Path:
    """Lay out one skill the way the upload panels expect it."""
    folder = into / skill.name
    folder.mkdir(parents=True)

    shutil.copy2(skill / "SKILL.md", folder / "SKILL.md")
    # Anything else the skill directory carries of its own (references, assets
    # belonging to just that skill) rides along under the same name.
    for extra in skill.iterdir():
        if extra.name == "SKILL.md":
            continue
        dest = folder / extra.name
        if extra.is_dir():
            shutil.copytree(extra, dest, ignore=IGNORE)
        else:
            shutil.copy2(extra, dest)

    for name in PAYLOAD_DIRS:
        src = ROOT / name
        if not src.is_dir():
            sys.exit(f"payload directory missing: {name}/")
        shutil.copytree(src, folder / name, ignore=IGNORE)
    for name in PAYLOAD_FILES:
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, folder / name)

    for rel in EXTRA_PAYLOAD.get(skill.name, ()):
        src = ROOT / rel
        if not src.is_dir():
            sys.exit(f"extra payload missing for {skill.name}: {rel}")
        dest = folder / rel               # original path preserved on purpose
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest, ignore=IGNORE)

    return folder


def uncompressed_size(folder: pathlib.Path) -> int:
    return sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="dist", help="output directory (default: dist)")
    ap.add_argument("--check", action="store_true",
                    help="stage and validate without writing any ZIP")
    args = ap.parse_args()

    out = ROOT / args.out
    skills = discover_skills()
    oversize = []

    with tempfile.TemporaryDirectory() as tmp:
        staged = [(s, stage(s, pathlib.Path(tmp))) for s in skills]

        if not args.check:
            out.mkdir(parents=True, exist_ok=True)

        for skill, folder in staged:
            size = uncompressed_size(folder)
            files = sum(1 for f in folder.rglob("*") if f.is_file())
            if size > MAX_UNCOMPRESSED:
                oversize.append(skill.name)

            if args.check:
                print(f"{skill.name:26} {files:4d} files  "
                      f"{size/1024/1024:5.1f} MB uncompressed  (not written)")
                continue

            target = out / f"{skill.name}.zip"
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(folder.rglob("*")):
                    if f.is_file():
                        z.write(f, f.relative_to(folder.parent))
            print(f"{skill.name:26} {files:4d} files  "
                  f"{size/1024/1024:5.1f} MB uncompressed  -> "
                  f"{target.relative_to(ROOT)} ({target.stat().st_size/1024/1024:.1f} MB)")

    for name, note in UPLOAD_NOTES.items():
        if any(s.name == name for s in skills):
            print(f"\nnote: {name} — {note}")

    if oversize:
        print(f"\nover the {MAX_UNCOMPRESSED//1024//1024} MB upload limit: "
              f"{', '.join(oversize)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
