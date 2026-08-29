---
name: project-context
description: "Use when a repository or project folder contains project-context/, especially before meaningful work, when resuming or handing off, or when current state, decisions, learnings, and linked evidence need to be read or maintained."
---

# Project Context

Use this protocol when a repository or organized project folder contains
`project-context/` and collaborative work needs memory that survives any one
person, agent, or chat session. It applies to software, document, research,
writing, mixed, and folder-based projects.

## Start

1. Read `project-context/NOW.md`.
2. Search `project-context/DECISIONS.md` and `project-context/LEARNINGS.md` for
   the current topic.
3. Follow only relevant links into detailed decisions, designs, incidents,
   tasks, primary artifacts, and evidence.
4. Treat entries marked `superseded` as historical evidence only.

Do not load every historical task or generated page. Current primary artifacts
and evidence—such as source and tests, approved documents, citations and data,
or the manuscript and editorial record—take precedence over summaries alongside
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

### Detection

`scripts/context_triggers.py` in this skill detects the trigger *window* — work
has landed since project context was last updated — and reports it to the
harness at session start and again before a session ends. It cannot judge
whether a decision or a learning fired; that judgment stays here. Run
`python3 scripts/context_triggers.py status` from the repository root to see the
current state, or `/session-end` to walk the evaluation deliberately.

A new session also checks whether the upstream scaffold at
`monomind-ai-lab/project-context` has published a release newer than the
`template_version` recorded in `.project-context.json`. The check runs at most
once a day, caches its answer, fails silently when offline, and only reports:
upgrading is the `project-context-init` skill's create-only job and needs the
user's go-ahead. Set `PROJECT_CONTEXT_UPDATE_CHECK=0` to turn it off, or
`PROJECT_CONTEXT_REPO` to follow a different source.

## Maintain

Triggers decide *when* to write. These rules decide *how*:

- Use `tasks/` for plans, progress, validation, and outcomes when the full
  profile is present; otherwise link the repository's existing task system.
- Keep `NOW.md` concise and actionable; remove stale state after linking its
  durable result.
- Record decisions with stable IDs, status, date, statement, rationale,
  consequences, and evidence. Supersede instead of silently reversing meaning.
- Record learnings only when evidence supports reuse beyond one task.
- In the full profile, create detailed designs or incident records when their
  evidence will help future work.
- Preserve completed historical records. Correct interpretation through status
  and supersession links instead of rewriting history.

## Safety

Never store secrets, sensitive personal or customer data, raw chat transcripts,
private host paths, ambient user profiles, copyrighted source material copied
without need, or unverified claims. Generated wikis and indexes are auxiliary
discovery systems; they do not replace tracked Markdown authority.

## Health

When context appears stale, contradictory, or hard to navigate, use the sibling
`project-context-init` skill's `doctor` workflow. It checks core files, scaffold
version, review freshness, duplicate decision/learning IDs, and broken relative
links without rewriting content.
