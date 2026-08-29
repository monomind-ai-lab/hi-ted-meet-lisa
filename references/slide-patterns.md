# Hi Ted, Meet Lisa — component reference

Every snippet below is lifted verbatim from the reference deck, so the markup
is known-good. Compose slides from these; do not invent new class names — the
stylesheet in the template is the whole design system.

## Slide anatomy

```
section.slide.dark.dg-slide.dg-center
  a.brand-mark            ← required on every slide
  p.eyebrow               ← kicker, e.g. "Part 2 · Install"
  h2.h-md                 ← the slide's point, as a statement
  p.lead                  ← optional supporting line
  div.dg-canvas           ← everything below lives here
```

## Slide shell (every content slide)

```html
<section class="slide dark dg-slide dg-center" data-screen-label="02 Why it matters" role="group" aria-label="Slide 02 Why it matters">
    <a class="brand-mark" href="https://monomind.one" target="_blank" rel="noopener noreferrer" aria-label="MonoMind AI Lab — opens monomind.one in a new tab"></a>
    <p class="eyebrow">Part 1 · Why</p>
    <h2 class="h-md">A collaborator returning after three weeks should not rebuild the project from stale chats.</h2>
    <p class="lead">Project Context answers four questions through a small set of typed Markdown records and a maintenance protocol that works across repositories and agent harnesses.</p>

    <div class="dg-canvas">
```

## Card grid — qcard

```html
<div class="grid-4">
      <div class="qcard"><div class="qn">Q1</div><h4>What is true now?</h4><p>Active state, blockers, and what happens next.</p></div>
      <div class="qcard"><div class="qn">Q2</div><h4>Which decisions constrain the work?</h4><p>Accepted choices, with the rationale intact.</p></div>
      <div class="qcard"><div class="qn">Q3</div><h4>What has already been learned?</h4><p>Verified lessons future collaborators should reuse.</p></div>
      <div class="qcard"><div class="qn">Q4</div><h4>Where is the evidence?</h4><p>Links to the source, dataset, review, or record.</p></div>
      </div>
```

## Table — tbl / td.k

```html
<table class="tbl">
      <thead><tr>
      <th style="width:44%"><span class="th-lbl"><svg class="th-ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="5.2" r="2.6"/><path d="M2.9 13.4a5.1 5.1 0 0 1 10.2 0"/></svg>Person</span></th>
      <th><span class="th-lbl"><svg class="th-ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.4" y="3.4" width="9.2" height="9.2" rx="2.2"/><rect x="6.4" y="6.4" width="3.2" height="3.2" rx="0.8"/></svg>AI agent</span></th>
      </tr></thead>
      <tbody>
      <tr><td>Pastes the short installation prompt</td><td>Loads and follows <b>project-context-init/SKILL.md</b></td></tr>
      <tr><td>Answers whether the project is new and what it is f
```

## Panel — dg-frame

```html
<div class="dg-frame is-accent">
      <div class="dg-frame-label">Three suggested approaches</div>
```

## Chip row — dg-chip / .nm

```html
<div class="dg-chip-row">
      <div class="dg-chip"><div class="nm">NOW.md</div><p class="ds">Current state &amp; blockers</p></div>
      <div class="dg-chip"><div class="nm">DECISIONS.md</div><p class="ds">Constraints &amp; rationale</p></div>
      <div class="dg-chip"><div class="nm">LEARNINGS.md</div><p class="ds">Verified, reusable lessons</p></div>
      </div>
```

## File tree — dg-treeview

```html
<ul class="dg-treeview">
      <li class="root"><span class="nm">monomind-ai-lab/project-context/</span></li>
      <li>
      <span class="nm">skills/</span>
      <ul>
      <li>
      <span class="nm">project-context-init/</span>
      <ul>
      <li><span class="nm">SKILL.md</span><span class="dsc">Init protocol (7 steps)</span></li>
      <li><span class="nm">scripts/project_context_init.py</span><span class="dsc">inspect · review · doctor · init</span></li>
      <li><span class="nm">assets/project-context/</span><span class="dsc">Profile templates</span></li>
      <li><span class="nm">references/optional-tools.md</span><span class="dsc">Add-on integration notes</span></li>
      </ul>
```

## Leader rows — dg-leader-row

```html
<div class="dg-leader-row"><span class="dg-leader-name">README.md</span><span class="dg-leader-desc">Context file read order</span></div>
      <div class="dg-leader-row"><span class="dg-leader-name">SKILL.md</span><span class="dg-leader-desc">Agent operating protocol</span></div>
      <div class="dg-leader-row"><span class="dg-leader-name">NOW.md</span><span class="dg-leader-desc">Current state &amp; blockers</span></div>
      <div class="dg-leader-row"><span class="dg-leader-name">DECISIONS.md</span><span class="dg-leader-desc">Constraints &amp; rationale</span></div>
      <div class="dg-
```

## Numbered steps — dg-step

```html
<div class="dg-step"><span class="nb-circle">1</span><div><h4>Read project-context/NOW.md</h4><p>Current state, active work, next actions</p></div></div>
```

## Workflow — wf-row / wf-node

```html
<div class="wf-row">
      <div class="wf-phase">Install<br><span>once</span></div>
      <div class="wf-track">
      <div class="wf-node"><span class="n">1</span><h4>The user prompts the agent</h4><p>A short installation prompt points to the canonical initializer skill.</p></div>
      <span class="wf-link" aria-hidden="true"></span>
      <div class="wf-node"><span class="n">2</span><h4>The agent reviews and classifies</h4><p>Asks onboarding questions, identifies project type, finds overlapping context.</p></div>
      <span class="wf-link" aria-hidden="true"></span>
      <div class="wf-node"><span class="n">3</span><h4>The user approves the plan</h4><p>Profile, exact file changes, and any optional tools — proposed before writing.</p></div>
      <span class="wf-link" aria-hidden="true"></span>
      <div class="wf-node"><span class="n">4</span><h4>The agent installs the pipeline</h4><p>Creates only approved files, preserves existing material, verifies idempotency.</p></div>
      </div>
      </div>
      <div class="wf-row">
      <div class="wf-phase">Operate<br><span>every session</span></div>
      <div class="wf-track">
      <div class="wf-node"><span class="n">5</span><h4>Agents read before later work</h4><p>Routed throu
```

## Bullets

```html
<ul class="bullets">
      <li>Existing context files are preserved <b>byte-for-byte</b>.</li>
      <li>Existing <b>AGENTS.md</b> and <b>CLAUDE.md</b> content is preserved outside one managed block — including file mode and CRLF endings.</li>
      <li>Unknown or overlapping memory is reviewed and classified, <b>not migrated</b>.</li>
      <li>Malformed blocks, unsafe symlinks, non-file harness paths, and non-UTF-8 instructions <b>stop apply mode before any write</b>.</li>
      <li>Add-ons are filtered by repository type, then installed only after an independent informed opt-in.</li>
```

## Code / prompt block

```html
<p class="code" id="install-prompt">Install Project Context in the current repository or project folder using
https://github.com/monomind-ai-lab/project-context. Read and follow
`skills/project-context-init/SKILL.md`, starting with its required onboarding
question. Show me the proposed plan and wait for my approval before making changes.</p>
```

## Callout — dg-loop

```html
<div class="dg-loop">↻ <b>Project Context does not copy the whole project into a second knowledge base.</b> Primary artifacts stay where they belong.</div>
```

## Flag — dg-flag

```html
<div class="dg-flag"><div class="fl">--dry-run</div><div class="fd">Inspect the exact changes first</div></div>
```

## Arrow connector — dg-arrow

```html
<div class="dg-arrow"><span class="cap">install &amp; operate via SKILL.md</span><span class="ln"></span></div>
```
