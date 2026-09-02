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
PAYLOAD_DIRS = ("assets", "references", "scripts", "templates")

# Carried only by the bundles that actually use them, and at their original
# paths, because the skills name those paths.
#
# The bundled design reviewer is deliberately NOT here. It is 156 files, which
# put /lisa at 230 against Claude's stated 200. The panel warns rather than
# refuses, so the upload proceeds — but it does not say what happens to the
# excess, and a bundle whose contents you cannot account for is not one to
# ship. An uploaded /lisa therefore runs the tooling-free floor of
# references/design-review.md, which is a supported tier, not a breakage.
# `vendor/` is here rather than in PAYLOAD_DIRS because only /lisa-design reads
# it, and it carries three SKILL.md files of its own — which an upload cannot
# take (see ONE_SKILL_MD below). /lisa names it once, in a descriptive table
# row, and never reads it.
EXTRA_PAYLOAD = {
    "lisa-design": ("vendor",),
}

# Claude requires a bundle to contain EXACTLY ONE SKILL.md. That is a hard
# refusal, not a warning: "Zip must contain exactly one SKILL.md file."
#
# /lisa-design cannot satisfy it. Its entire job is to drive the vendored
# Slides AI skill tree, which is three skills each with their own SKILL.md,
# and renaming them would both fork upstream and contradict the skill's own
# "do not edit anything under vendor/" rule. So no bundle is built for it —
# better than emitting a zip the panel will reject.
#
# /lisa-review fails it the same way, one step removed. The skill exists to
# run the bundled reviewer, and `.agents/skills/impeccable/` carries a
# SKILL.md of its own — besides which its 156 files would put the bundle at
# 203 against the 200-file line. A bundle without the reviewer would only
# repeat the tooling-free floor the /lisa bundle already carries, which is
# not worth a panel slot.
NOT_UPLOADABLE = {
    "lisa-design": "drives the vendored skill tree, which carries three more "
                   "SKILL.md files; an upload permits exactly one. Use the "
                   "plugin or a checkout.",
    "lisa-review": "exists to run the bundled reviewer, which cannot ride "
                   "along: .agents/skills/impeccable/ carries its own "
                   "SKILL.md (an upload permits exactly one) and would push "
                   "the bundle past 200 files besides. Without it the skill "
                   "is the same floor an uploaded /lisa already runs. Use "
                   "the plugin or a checkout.",
}

# Built for completeness, but say plainly which ones are worth uploading. A
# bundle is only worth a panel slot if the skill can finish its job there.
UPLOAD_NOTES = {
    "lisa-new-template": "registry writes and thumbnails need a local checkout — "
                         "a hosted upload can only hand back a skeleton",
}

# Bundled WITHOUT the shared payload. /lisa-help answers from its own text and
# reads no other file unless asked to go deeper — deeper reading is a checkout
# or plugin concern, not an upload one. A help command is worth a panel slot
# precisely because it costs a few kilobytes, so it gets a bundle, just not
# 2.6 MB of templates it never opens. (Contrast /lisa-lang, which is NOT here:
# it reads templates/templates.json, the pattern references, and the template
# files to mirror a family's language mechanism, so it rides with the full
# payload like /lisa. It also cites skills/lisa/SKILL.md, which no bundle
# carries — the skill names the raw.githubusercontent fallback for that.)
NO_PAYLOAD = {
    "lisa-help": "self-contained: it answers from its own SKILL.md, so the "
                 "shared payload stays out and the bundle is a few kilobytes",
}

# Bundled with a SLICE of the payload: only the files the skill actually
# reads, at their original paths, so every `references/...` and `assets/...`
# path in its SKILL.md resolves unchanged. /lisa-brand reads its contract and
# its A4 skeleton and nothing else — it writes into the user's working
# directory, never into a template — so the 2.6 MB of templates it never
# opens would only push the bundle toward the limits for nothing. It is
# worth a panel slot: the extraction and both HTML files complete in a
# sandbox, and only the PDF render waits for a local Chrome, which the skill
# says so about.
SLICED_PAYLOAD = {
    "lisa-brand": ("references/brand-extraction.md",
                   "assets/lisa-brand-book-a4.html"),
}
PAYLOAD_FILES = ("LICENSE", "NOTICE")

# Claude caps a custom skill upload at 30 MB uncompressed and states a 200-file
# maximum. The file number is not in the published docs — it surfaced as a
# "Zip contains too many files (maximum 200)" warning from the upload panel.
# It is a warning, not a rejection, and the panel does not say whether the
# excess is dropped or kept. Hold the line anyway: shipping past a stated
# maximum means shipping a bundle whose contents you cannot verify.
MAX_UNCOMPRESSED = 30 * 1024 * 1024
MAX_FILES = 200
ONE_SKILL_MD = 1

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

    if skill.name in SLICED_PAYLOAD:
        for rel in SLICED_PAYLOAD[skill.name]:
            src = ROOT / rel
            if not src.is_file():
                sys.exit(f"sliced payload missing for {skill.name}: {rel}")
            dest = folder / rel              # original path preserved on purpose
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    elif skill.name not in NO_PAYLOAD:
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
    skills = [s for s in discover_skills() if s.name not in NOT_UPLOADABLE]
    oversize = []
    toomany = []
    multiskill = []

    with tempfile.TemporaryDirectory() as tmp:
        staged = [(s, stage(s, pathlib.Path(tmp))) for s in skills]

        if not args.check:
            out.mkdir(parents=True, exist_ok=True)

        for skill, folder in staged:
            size = uncompressed_size(folder)
            files = sum(1 for f in folder.rglob("*") if f.is_file())
            skillmds = sum(1 for f in folder.rglob("SKILL.md"))
            if skillmds != ONE_SKILL_MD:
                multiskill.append(f"{skill.name} ({skillmds})")
            if size > MAX_UNCOMPRESSED:
                oversize.append(skill.name)
            if files > MAX_FILES:
                toomany.append(f"{skill.name} ({files})")

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

    for name, why in NOT_UPLOADABLE.items():
        print(f"\nskipped: {name} — {why}")

    for name, note in UPLOAD_NOTES.items():
        if any(s.name == name for s in skills):
            print(f"\nnote: {name} — {note}")

    for name, why in NO_PAYLOAD.items():
        if any(s.name == name for s in skills):
            print(f"\nno payload: {name} — {why}")

    for name, rels in SLICED_PAYLOAD.items():
        if any(s.name == name for s in skills):
            print(f"\nsliced payload: {name} — only {', '.join(rels)}, "
                  f"at their original paths")

    if oversize:
        print(f"\nover the {MAX_UNCOMPRESSED//1024//1024} MB upload limit: "
              f"{', '.join(oversize)}", file=sys.stderr)
    if multiskill:
        print(f"\nmore than one SKILL.md: {', '.join(multiskill)}. The panel "
              f"refuses these outright — a bundle must contain exactly one. "
              f"Scope the payload that carries the extras to the skills that "
              f"actually read it.", file=sys.stderr)
    if toomany:
        print(f"\nover the {MAX_FILES}-file upload limit: {', '.join(toomany)}. "
              f"The panel warns rather than refuses, and does not say what "
              f"happens to the excess — drop a payload directory rather than "
              f"ship a bundle whose contents you cannot account for.",
              file=sys.stderr)
    return 1 if (oversize or toomany or multiskill) else 0


if __name__ == "__main__":
    raise SystemExit(main())
