---
name: session-end
description: Use when ending, pausing, or handing off a working session so another agent, a new session, or another person can take the work over — walks the project-context triggers deliberately and writes the handoff into NOW.md, DECISIONS.md, and LEARNINGS.md.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---

# Session End

Close a session so the next one starts informed instead of re-deriving what
this one learned. Triggers normally fire as work lands; this walks the same
evaluation on purpose, at the moment the work stops.

Run it before handing off to another agent, starting a fresh session,
compacting a long one, or stepping away with work in flight.

## 1. Establish what actually happened

Do not reconstruct the session from memory. Gather evidence first:

```sh
python3 .agents/skills/project-context/scripts/context_triggers.py status
git status --short
git log --oneline -15
```

Read `project-context/NOW.md` and skim `DECISIONS.md` and `LEARNINGS.md` for
the IDs already used and for entries this session contradicted.

If the repository is not under Git, list what changed by inspecting the working
tree and the task records instead.

## 2. Evaluate each trigger

Walk the trigger list in `project-context/SKILL.md` document by document and
decide, explicitly, whether each one fired. Name the evidence for every "yes".

- `NOW.md` — almost always fires at session end. State changed, or work is in
  flight, and either is a handoff.
- `DECISIONS.md` — only when a choice now constrains future work. A decision the
  next contributor may freely reverse without asking anyone is not one.
- `LEARNINGS.md` — only with evidence, and only when it recurs beyond this task.

## 3. Write the updates

**`NOW.md`** — replace stale state; do not append. Set `Last reviewed` to
today. It must answer, in a form a stranger can act on:

- what state the project is in now, with links to primary artifacts;
- what is actively in progress and its status;
- what is blocked, and on what;
- the next action, specifically enough to start without asking;
- anything half-finished, unverified, or deliberately left broken.

**`DECISIONS.md`** — append with the next unused `D-NNN`, `accepted` status,
today's date, the decision, its rationale, its consequences, and evidence. To
change an earlier decision, mark it `superseded`, link both directions, and
leave its original meaning intact.

**`LEARNINGS.md`** — append with the next unused `L-NNN`, its scope, the lesson,
the concrete action a future contributor should take, and the evidence.

Record uncertainty as uncertainty. An unverified claim written as fact costs the
next session more than an honest gap.

## 4. Verify before handing off

```sh
python3 .agents/skills/project-context-init/scripts/project_context_init.py doctor --target .
python3 .agents/skills/project-context/scripts/context_triggers.py status
git diff -- project-context
```

Read the diff for secrets, tokens, private host paths, customer data, and raw
transcripts. None of those belong in tracked context.

## 5. Report and stop

Tell the user what changed, which triggers did not fire and why, and what the
next session should do first.

Committing is the user's call: offer it, name the files, and wait. Do not
commit, push, or open a pull request unless asked.
