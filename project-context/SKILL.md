---
name: project-context
description: "Use before meaningful work, when resuming or handing off, or when this project folder's current state, decisions, learnings, and linked evidence need to be read or maintained."
---

# Project Context

Use this local protocol whenever repository-bound work needs prior decisions,
current handoff state, verified learnings, or a durable milestone update across
software, document, research, writing, and mixed project folders.

## Start

1. Read `project-context/NOW.md`.
2. Search `project-context/DECISIONS.md` and `project-context/LEARNINGS.md` for
   the task's topics.
3. Follow only relevant links into detailed records, primary project artifacts,
   and evidence.
4. Treat entries marked `superseded` as history only.

Do not load every historical task or generated wiki page. Current primary
artifacts and verified evidence take precedence over summaries alongside
explicit user direction and repository instructions.

## Triggers

Update a document when its trigger fires — not when someone asks for an update.
Evaluate every trigger below at each point where work lands: before a commit,
before a handoff, before ending a session, and whenever something recorded here
stops being true.

### `NOW.md` — the state a next contributor would act on changed

- Work landed that changes what should happen next.
- An initiative started, finished, or changed status.
- A blocker appeared or cleared.
- A next action recorded here was completed.
- The session is ending with work in flight, uncommitted, or half-verified.
- The repository contradicts the recorded snapshot.

Replace the stale state rather than appending to it, and set `Last reviewed` to
today. `NOW.md` is a handoff, not a log.

### `DECISIONS.md` — a choice now constrains future work

- One option was taken over a viable alternative that was actually considered.
- A convention, boundary, interface, format, dependency, or tool was fixed.
- The user stated a standing rule: always, never, use X instead of Y.
- Something was deliberately ruled out of scope.
- An earlier decision was reversed or narrowed. Supersede it and link both
  directions; never rewrite its meaning in place.

Do not record an implementation detail that a future contributor may freely
change without consulting anyone.

### `LEARNINGS.md` — evidence changed what is believed, and it will recur

- A root cause was found that the code did not make obvious.
- An approach failed in a way that would repeat. Record the failed path, not
  only the fix that followed it.
- An assumption was disproved by an observed result: a test, run, log, review,
  measurement, or citation.
- A tool, API, or platform behaved unlike its documentation implied.
- A review finding or incident produced a rule that would have prevented it.

A learning needs evidence and must apply beyond the task that produced it. A
lesson that is true only here belongs in that task's record.

### When nothing fired

Say so and move on. Silence is a valid outcome. Padding the registries with
choices that constrain nothing, or lessons nobody verified, makes them
unreadable — which is the exact failure these files exist to prevent.

## Maintain

Triggers decide *when* to write. These rules decide *how*:

- Use `tasks/` for plans, progress, validation, and outcomes when the full
  profile is present; otherwise link the repository's existing task system.
- Keep `NOW.md` short and actionable.
- Record decisions with stable IDs, status, date, statement, rationale,
  consequences, and evidence. Supersede instead of silently reversing meaning.
- Record learnings with stable IDs, evidence, scope, and a concrete future action.
- After adding an entry or changing a status, regenerate the registry
  indexes with `python3 scripts/context_index.py`. They are derived
  tables; a hand-edited one is overwritten.
- In the full profile, use `designs/` and `incidents/` for evidence that will
  help future work.
- Preserve completed evidence and correct its interpretation through status and
  supersession links rather than rewriting history.

Never store secrets, sensitive customer data, raw transcripts, private host
paths, ambient profiles, or unverified claims.

## Automation

The `project-context` skill ships `scripts/context_triggers.py`, which detects
the trigger *window* — work has landed since project context was last updated —
and reports it to the harness at session start and again before a session ends.
It cannot judge whether a decision or a learning fired; that judgment stays with
the agent reading this file. `README.md` records how it is wired here.

Run `/session-end` to walk the same evaluation deliberately before handing off
to another agent, another session, or another person.

A new session also checks whether the upstream scaffold at
`monomind-ai-lab/project-context` has published a release newer than the
`template_version` recorded in `.project-context.json`. The check runs at most
once a day, caches its answer, fails silently when offline, and only reports:
upgrading is the `project-context-init` skill's create-only job and needs the
user's go-ahead. Set `PROJECT_CONTEXT_UPDATE_CHECK=0` to turn it off, or
`PROJECT_CONTEXT_REPO` to follow a different source.

## Health

When context looks stale, contradictory, or hard to navigate, run the sibling
`project-context-init` skill's doctor:

    python3 .agents/skills/project-context-init/scripts/project_context_init.py doctor --target .

It checks core files, scaffold version, review freshness, duplicate decision and
learning IDs, and broken relative links, and it never rewrites content.

To see whether a trigger window is currently open, without waiting for a hook:

    python3 .agents/skills/project-context/scripts/context_triggers.py status
