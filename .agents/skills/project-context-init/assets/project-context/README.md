# Project Context

This directory is the harness-neutral context pipeline for a repo-bound
collaborative project or consistently shared project folder. It works for
software, documents, research, writing, and mixed work by recording current
state, decisions that constrain future work, reusable learnings, and linked
supporting evidence.

## Read order

1. Read [`SKILL.md`](SKILL.md) for the operating protocol and the update triggers.
2. Read [`NOW.md`](NOW.md) for current state, active work, blockers, and next actions.
3. Search [`DECISIONS.md`](DECISIONS.md) and [`LEARNINGS.md`](LEARNINGS.md) by topic.
4. Open only the linked decision, design, incident, task, primary artifact, and
   evidence needed for the current work.

## Artifact roles

| Location | Authority and purpose | Update rule |
| --- | --- | --- |
| `NOW.md` | Current snapshot and handoff | Replace stale state; keep concise |
| `DECISIONS.md` | Accepted and superseded decisions | Append or supersede; never silently reverse |
| `LEARNINGS.md` | Verified, reusable lessons | Promote only evidence-backed lessons |
| `decisions/` | Detailed decision records (full profile) | Link from the registry; preserve status |
| `designs/` | Designs and alternatives (full profile) | Keep decisions separate from proposals |
| `incidents/` | Root cause, remediation, prevention (full profile) | Preserve history; promote reusable lessons |
| `tasks/` | Plans, progress, validation, outcomes (full profile) | Keep completed records immutable |

The repository's primary artifacts and verified evidence remain authoritative:
for example source and tests, approved documents, citations and data, or the
manuscript and editorial record. Generated indexes and wikis are auxiliary views.

## Update triggers

Documents are updated when a trigger fires, as work lands — not when someone
asks for an update. Each document has its own trigger, defined in full in
[`SKILL.md`](SKILL.md):

| Document | Fires when |
| --- | --- |
| `NOW.md` | The state a next contributor would act on changed: work landed, status moved, a blocker appeared or cleared, a recorded next action was done, or a session ends with work in flight |
| `DECISIONS.md` | A choice now constrains future work: an option taken over a viable alternative, a convention or interface or dependency fixed, a standing rule stated, scope deliberately excluded, or an earlier decision superseded |
| `LEARNINGS.md` | Verified evidence changed what is believed and will recur: a non-obvious root cause, an approach that failed in a repeatable way, a disproved assumption, or a tool behaving unlike its documentation |

When no trigger fired, say so and write nothing. Silence keeps the registries
readable.

## Skills

| Skill | What it does | Use it when |
| --- | --- | --- |
| `project-context` | The operating protocol: what to read before work, the per-document triggers, and how to record decisions and learnings. Ships `scripts/context_triggers.py`. | Automatically, before meaningful work and as work lands. This is the default skill — it needs no invocation. |
| `session-end` | Walks the triggers deliberately, then writes the handoff into `NOW.md`, `DECISIONS.md`, and `LEARNINGS.md`, verifies it, and reports what fired. | Ending, pausing, compacting, or handing off a session to another agent, a new session, or another person. Invoke as `/session-end`. |
| `project-context-init` | Installs, adopts, repairs, and health-checks this pipeline. Classifies the repository, plans create-only changes, consolidates prior context, and runs `doctor`. | Setting the pipeline up in a new repository, upgrading the scaffold, or diagnosing context that has gone stale, contradictory, or hard to navigate. |

Skills live under `.agents/skills/` so any harness can read them. Claude Code
additionally discovers `.claude/skills/`; Codex and similar agents read the
`AGENTS.md` pointer.

## Automation

`scripts/context_triggers.py` in the `project-context` skill detects the trigger
*window* — work has landed since project context was last updated — from commits
since the last context change, uncommitted paths outside this directory, and
untouched template placeholders. It reports rather than writes: it cannot judge
whether a decision or a learning fired, and that judgment stays with the agent.

Check the current state at any time:

```sh
python3 .agents/skills/project-context/scripts/context_triggers.py status
```

Where the harness supports lifecycle hooks, wire the same script so the check is
automatic. For Claude Code, in `.claude/settings.json`:

- `SessionStart` → `context_triggers.py report` injects pending triggers and the
  trigger table into the session's context.
- `Stop` → `context_triggers.py gate` blocks the end of a turn once, with the
  specific evidence, when context is behind the repository.

The gate blocks at most once per session and never twice for the same session,
so it cannot loop. Its session state lives in `.claude/project-context-state.json`
and should not be committed.

### Upstream release check

At session start the same script asks whether
[`monomind-ai-lab/project-context`](https://github.com/monomind-ai-lab/project-context)
has published a release newer than the `template_version` in
`.project-context.json`, and reports it in one line. It checks at most once a
day, caches the answer alongside the session state, and stays silent when
offline, rate-limited, or unreachable. It never upgrades anything on its own —
that is `project-context-init`'s create-only job, and it needs the user's
go-ahead.

| Variable | Effect |
| --- | --- |
| `PROJECT_CONTEXT_UPDATE_CHECK=0` | Turn the check off entirely |
| `PROJECT_CONTEXT_REPO=owner/name` | Follow a different upstream source |

The request is an unauthenticated call to the public GitHub releases API. It
sends nothing about the repository it runs in.

## Promotion workflow

At a meaningful milestone or handoff:

1. Update the active task record with progress and validation evidence.
2. Update `NOW.md` when active state, blockers, or next actions changed.
3. Add a decision only when it constrains future work.
4. Add a learning only when verified and reusable beyond one task.
5. Link promoted knowledge to its source task, artifact, citation, review,
   incident, result, or commit.
6. Mark replaced knowledge `superseded` and link both directions.

Do not store raw chat transcripts, credentials, private host paths, sensitive
customer data, ambient profiles, or unverified speculation here.
