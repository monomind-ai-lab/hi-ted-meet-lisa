#!/usr/bin/env python3
"""Detect project-context update triggers and report them to the harness.

The trigger contract lives in project-context/SKILL.md. This script only
detects that a trigger *window* is open: work has landed since project context
was last updated. Deciding which documents actually fire is the agent's job,
because only the agent knows whether a choice constrained future work or an
observation generalises beyond one task.

Commands:
  report  read hook JSON on stdin, emit SessionStart additionalContext
  gate    read hook JSON on stdin, emit a Stop decision (blocks at most once
          per session so it can never loop)
  status  human-readable summary for manual runs

Read-only except for its own session state file. Never fails a session: any
unexpected error exits 0 with no decision.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime

CONTEXT_DIR = "project-context"
UPSTREAM_REPO = os.environ.get("PROJECT_CONTEXT_REPO", "monomind-ai-lab/project-context")
RELEASE_CACHE_HOURS = 24
STATE_RELATIVE = Path(".claude") / "project-context-state.json"
EXCLUDED = {
    ".git", "node_modules", "vendor", "dist", "build", "coverage", ".venv",
    "venv", "__pycache__", ".next", "target", "out", ".claude", ".agents",
    ".wrangler", ".gitnexus", "openwiki", "graphify-out",
}
PLACEHOLDERS = (
    "Describe the current stable state.",
    "## D-000: Example decision",
    "## L-000: Example learning",
)

TRIGGER_TABLE = """\
NOW.md — the state a next contributor would act on changed:
  work landed that changes what happens next; an initiative started, finished,
  or changed status; a blocker appeared or cleared; a recorded next action was
  done; the session is ending with work in flight.
DECISIONS.md — a choice now constrains future work:
  one option was taken over a viable alternative; a convention, boundary,
  interface, format, dependency, or tool was fixed; the user stated a standing
  rule; something was deliberately ruled out of scope; an earlier decision was
  reversed or narrowed (supersede it, do not rewrite it).
LEARNINGS.md — evidence changed what is believed, and it will recur:
  a root cause the code did not make obvious; an approach that failed in a way
  that would repeat; an assumption disproved by an observed result; a tool,
  API, or platform behaving unlike its documentation; a rule that would have
  prevented a review finding or incident. Evidence required, and it must apply
  beyond this one task."""


def run(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    # rstrip only newlines: git status --porcelain encodes state in leading columns
    return result.stdout.rstrip("\n") if result.returncode == 0 else ""


def is_git(target: Path) -> bool:
    return bool(run(["git", "rev-parse", "--is-inside-work-tree"], target))


def newest_mtime(root: Path, inside: bool) -> float:
    """Newest file mtime inside project-context/ (inside=True) or outside it."""
    newest = 0.0
    for current, directories, files in os.walk(root):
        directories[:] = [
            d for d in directories if d not in EXCLUDED and not d.startswith(".")
        ]
        relative = Path(current).relative_to(root)
        if (relative.parts[:1] == (CONTEXT_DIR,)) != inside:
            continue
        for name in files:
            if name.startswith("."):
                continue
            try:
                newest = max(newest, (Path(current) / name).stat().st_mtime)
            except OSError:
                continue
    return newest


def evaluate(target: Path) -> dict:
    context = target / CONTEXT_DIR
    state: dict = {
        "target": str(target),
        "installed": context.is_dir(),
        "work_commits": [],
        "dirty_paths": [],
        "context_touched": False,
        "placeholders": [],
        "last_reviewed": None,
        "review_age_days": None,
        "git": False,
    }
    if not state["installed"]:
        return state

    now_file = context / "NOW.md"
    if now_file.is_file():
        text = now_file.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^Last reviewed:\s*(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
        if match:
            state["last_reviewed"] = match.group(1)
            try:
                parsed = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                state["review_age_days"] = (date.today() - parsed).days
            except ValueError:
                pass

    for relative in ("NOW.md", "DECISIONS.md", "LEARNINGS.md"):
        candidate = context / relative
        if not candidate.is_file():
            continue
        body = candidate.read_text(encoding="utf-8", errors="replace")
        if any(marker in body for marker in PLACEHOLDERS):
            state["placeholders"].append(relative)

    state["git"] = is_git(target)
    if state["git"]:
        porcelain = run(["git", "status", "--porcelain"], target)
        for line in porcelain.splitlines():
            path = line[3:].strip().strip('"')
            path = path.split(" -> ")[-1]
            if path.startswith(f"{CONTEXT_DIR}/"):
                state["context_touched"] = True
            elif path:
                state["dirty_paths"].append(path)

        anchor = run(
            ["git", "log", "-1", "--format=%H", "--", CONTEXT_DIR], target
        )
        head = run(["git", "rev-parse", "HEAD"], target)
        if anchor and anchor == head:
            state["context_touched"] = True
        span = f"{anchor}..HEAD" if anchor else "HEAD"
        log = run(
            ["git", "log", span, "--format=%h %s", "--", ".", f":(exclude){CONTEXT_DIR}"],
            target,
        )
        state["work_commits"] = [line for line in log.splitlines() if line.strip()]
    else:
        outside = newest_mtime(target, inside=False)
        inside = newest_mtime(target, inside=True)
        if outside > inside:
            state["dirty_paths"].append("files changed more recently than project-context/")

    return state


def parse_version(value: str) -> tuple:
    """Leading numeric components of a version, tolerant of a v prefix."""
    parts: list[int] = []
    for chunk in re.split(r"[.\-+]", str(value).strip().lstrip("vV")):
        if not chunk.isdigit():
            break
        parts.append(int(chunk))
    return tuple(parts)


def installed_version(target: Path) -> str:
    metadata = target / CONTEXT_DIR / ".project-context.json"
    try:
        return str(json.loads(metadata.read_text(encoding="utf-8")).get("template_version", ""))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return ""


def fetch_latest_release() -> dict:
    """Latest published release of the upstream scaffold. Never raises."""
    url = f"https://api.github.com/repos/{UPSTREAM_REPO}/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "project-context-triggers",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return {}
    tag = payload.get("tag_name")
    if not tag:
        return {}
    return {
        "tag": str(tag),
        "name": str(payload.get("name") or tag),
        "url": str(payload.get("html_url") or ""),
        "published": str(payload.get("published_at") or "")[:10],
    }


def release_status(target: Path, sessions: dict) -> dict:
    """Cached upstream release check. Opt out with PROJECT_CONTEXT_UPDATE_CHECK=0."""
    if os.environ.get("PROJECT_CONTEXT_UPDATE_CHECK", "1") in {"0", "false", "no"}:
        return {}
    installed = installed_version(target)
    if not installed:
        return {}
    cached = sessions.get("_release") or {}
    fresh = False
    checked = cached.get("checked")
    if checked:
        try:
            age = datetime.now() - datetime.fromisoformat(checked)
            fresh = age.total_seconds() < RELEASE_CACHE_HOURS * 3600
        except ValueError:
            fresh = False
    if not fresh:
        latest = fetch_latest_release()
        cached = {"checked": datetime.now().isoformat(timespec="seconds"), **latest}
        sessions["_release"] = cached
    if not cached.get("tag"):
        return {}
    newer = parse_version(cached["tag"]) > parse_version(installed)
    return {
        "installed": installed,
        "latest": cached["tag"],
        "name": cached.get("name", cached["tag"]),
        "url": cached.get("url", ""),
        "published": cached.get("published", ""),
        "newer": newer,
    }


def release_line(release: dict) -> str:
    if not release or not release.get("newer"):
        return ""
    published = f", released {release['published']}" if release.get("published") else ""
    location = f"\n  {release['url']}" if release.get("url") else ""
    return (
        f"Project Context {release['latest']} is available"
        f" (this repository has {release['installed']}{published})."
        f" Ask before upgrading: the `project-context-init` skill plans a"
        f" create-only upgrade and preserves what is already written.{location}"
    )


def due(state: dict) -> list[str]:
    if not state["installed"] or state["context_touched"]:
        return []
    reasons: list[str] = []
    if state["placeholders"]:
        reasons.append(
            "project context is still at its installed template values ("
            + ", ".join(state["placeholders"])
            + ")"
        )
    if state["work_commits"]:
        count = len(state["work_commits"])
        reasons.append(
            f"{count} commit{'s' if count != 1 else ''} since project context was last updated"
        )
    if state["dirty_paths"]:
        count = len(state["dirty_paths"])
        reasons.append(f"{count} uncommitted path{'s' if count != 1 else ''} outside project-context/")
    return reasons


def detail(state: dict) -> str:
    lines: list[str] = []
    if state["work_commits"]:
        lines.append("Unrecorded commits:")
        lines.extend(f"  {entry}" for entry in state["work_commits"][:10])
        if len(state["work_commits"]) > 10:
            lines.append(f"  … and {len(state['work_commits']) - 10} more")
    if state["dirty_paths"]:
        lines.append("Uncommitted work:")
        lines.extend(f"  {path}" for path in state["dirty_paths"][:10])
        if len(state["dirty_paths"]) > 10:
            lines.append(f"  … and {len(state['dirty_paths']) - 10} more")
    if state["last_reviewed"]:
        age = state["review_age_days"]
        plural = "" if age == 1 else "s"
        suffix = f" ({age} day{plural} ago)" if isinstance(age, int) else ""
        lines.append(f"NOW.md last reviewed: {state['last_reviewed']}{suffix}")
    return "\n".join(lines)


def load_state(target: Path) -> dict:
    path = target / STATE_RELATIVE
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def save_state(target: Path, sessions: dict) -> None:
    path = target / STATE_RELATIVE
    reserved = {key: value for key, value in sessions.items() if key.startswith("_")}
    entries = {key: value for key, value in sessions.items() if not key.startswith("_")}
    trimmed = dict(list(entries.items())[-20:])
    trimmed.update(reserved)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(trimmed, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def read_hook_input() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except (OSError, UnicodeDecodeError):
        return {}
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def resolve_target(hook: dict) -> Path:
    for candidate in (
        os.environ.get("CLAUDE_PROJECT_DIR"),
        hook.get("cwd"),
        os.getcwd(),
    ):
        if not candidate:
            continue
        path = Path(candidate).resolve()
        if (path / CONTEXT_DIR).is_dir():
            return path
        for parent in path.parents:
            if (parent / CONTEXT_DIR).is_dir():
                return parent
    return Path(os.getcwd()).resolve()


def command_report(hook: dict, target: Path) -> int:
    state = evaluate(target)
    if not state["installed"]:
        return 0
    reasons = due(state)
    session = str(hook.get("session_id") or "unknown")
    sessions = load_state(target)
    sessions[session] = {"opened": datetime.now().isoformat(timespec="seconds"), "blocked": 0}
    release = release_status(target, sessions)
    save_state(target, sessions)

    blocks: list[str] = []
    if reasons:
        blocks.append(
            "\n".join(
                [
                    "Project context has pending updates: " + "; ".join(reasons) + ".",
                    "",
                    detail(state),
                    "",
                    "Read project-context/NOW.md, then evaluate these triggers as this",
                    "session's work lands — do not wait to be asked:",
                    "",
                    TRIGGER_TABLE,
                ]
            )
        )
    upstream = release_line(release)
    if upstream:
        blocks.append(upstream)
    if not blocks:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n\n".join(blocks),
            }
        },
        sys.stdout,
    )
    return 0


def command_gate(hook: dict, target: Path) -> int:
    if hook.get("stop_hook_active"):
        return 0
    state = evaluate(target)
    reasons = due(state)
    if not reasons:
        return 0
    session = str(hook.get("session_id") or "unknown")
    sessions = load_state(target)
    entry = sessions.get(session) or {"opened": datetime.now().isoformat(timespec="seconds"), "blocked": 0}
    if entry.get("blocked", 0) >= 1:
        return 0
    entry["blocked"] = entry.get("blocked", 0) + 1
    entry["last_block"] = datetime.now().isoformat(timespec="seconds")
    sessions[session] = entry
    save_state(target, sessions)
    reason = "\n".join(
        [
            "Project context is behind the repository: " + "; ".join(reasons) + ".",
            "",
            detail(state),
            "",
            "Evaluate each document's trigger and update the ones that fired:",
            "",
            TRIGGER_TABLE,
            "",
            "Update project-context/NOW.md at minimum — set `Last reviewed` to",
            "today and make the snapshot, active work, and blockers match the",
            "repository. Add a decision or a learning only where its trigger",
            "actually fired; say so briefly if none did. This check does not",
            "block again in this session.",
        ]
    )
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


def command_status(target: Path) -> int:
    state = evaluate(target)
    if not state["installed"]:
        print(f"no {CONTEXT_DIR}/ in {target}")
        return 0
    reasons = due(state)
    print(f"target: {target}")
    print(f"status: {'update due' if reasons else 'current'}")
    for reason in reasons:
        print(f"  - {reason}")
    body = detail(state)
    if body:
        print(body)
    sessions = load_state(target)
    release = release_status(target, sessions)
    save_state(target, sessions)
    if release:
        marker = "update available" if release["newer"] else "current"
        print(f"upstream: {release['latest']} ({marker}); installed: {release['installed']}")
    return 0


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "status"
    hook = read_hook_input() if command in {"report", "gate"} else {}
    target = resolve_target(hook)
    if command == "report":
        return command_report(hook, target)
    if command == "gate":
        return command_gate(hook, target)
    return command_status(target)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # never break a session over a context check
        sys.exit(0)
