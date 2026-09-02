# Motion patterns — dependency-free animation for any Lisa file

A library of animation patterns that need **no library**: CSS, and the Web
Animations API where CSS cannot do it (`D-015`). Every snippet here was
lifted verbatim from a page that was opened in a browser and checked under
reduced motion, in print, in a hidden tab, and at 375px — the same
"known-good markup" contract as `references/slide-patterns*.md`. Copy the
snippet; do not re-derive it.

Where a pattern has a well-known ancestor it is named. Sixteen of the
patterns re-implement the no-library demos of
[cinematic-site-components](https://github.com/robonuggets/cinematic-site-components)
(MIT, Jay from RoboLabs), and fourteen more re-implement its GSAP demos in CSS
and WAAPI. Nothing was copied: those pages carry a global `*{margin:0}`
reset, generic class names, hard-coded palettes, no ARIA and no reduced-motion
handling, and the GSAP ones cannot ship here at all. This is a derivation
under `D-008` and is credited in `NOTICE`.

## The rules, once

Every pattern in this file obeys these; anything you compose must too.

1. **Namespace.** Every class is `lm-*` (`lm-reveal`, `lm-type`). State
   classes are `is-*` (`is-in`, `is-open`, `is-live`). Custom properties are
   `--lm-*`; the two the host sets per element are `--i` (index) and `--h`
   (hue), because the house templates already use those names.
2. **Tokens, never values.** A pattern reads only `--lm-*` tokens, each with
   a fallback that is a keyword or another token — `var(--lm-accent,
   currentColor)`, never a hex. The **bridge block** below maps `--lm-*` onto
   the host template's own tokens, once per file. That is the whole reason
   the same pattern looks native in `project-website` and in `paper-brief`:
   the schema is shared, the values are the host's.
3. **Base is final.** The un-animated style of every element is its finished
   state. Everything that moves — every transition, animation, hidden start
   state and `clip-path` — lives inside
   `@media screen and (prefers-reduced-motion: no-preference)`. Two things
   fall out for free: reduced-motion readers get the finished page, and
   print gets the finished page (print is not `screen`).
4. **An observer is never the only path to visible** (`L-022`). Reveals are
   armed per page activation by the runtime, which also carries a
   fail-visible timer, shows everything when the tab is hidden or the
   observer is absent, and shows everything on `beforeprint`.
5. **Loops stop when the page does.** Anything that runs — `requestAnimationFrame`,
   a WAAPI animation, a pointer listener on `window` — is started by
   `lm.onActivate(fn)` and stopped by the function `fn` returns. The runtime
   calls it when a hash-routed page deactivates.
6. **Keyboard first.** Anything clickable is a `<button>` or an `<a href>`,
   keeps a visible `:focus-visible` ring, and has a keyboard path to every
   state a pointer can reach.
7. **Compositor only.** Animate `transform`, `opacity`, `clip-path`,
   `background-position`, `stroke-dashoffset` and registered custom
   properties. `will-change` is used on exactly the elements that move every
   frame (marquee tracks, the cursor glow), nowhere else. Two patterns are
   allowed to animate layout — the island and the accordion — and each says
   why.
8. **Cursor patterns are desktop-only.** They gate on
   `(hover: hover) and (pointer: fine)` and say what a touch reader gets
   instead. Nothing is reachable *only* by hovering.
9. **Screen readers read the finished text.** Decorative duplicates
   (marquee copies, glitch layers, odometer strips) are `aria-hidden`; the
   real number or word is in the tree once.
10. **One orchestrated moment beats scattered effects.** A site is read, not
    watched. Pick the one place a reader should notice, and leave the rest
    still.
11. **The observed element is never the hidden one.** Hiding geometry —
    `clip-path`, `scale(0)`, a zero width — goes on a child, a pseudo-element
    or a mask, never on the element that carries `lm-on` or `lm-reveal`. The
    observer measures the clipped box, and a box clipped to nothing reports
    an empty intersection (ratio 0) and is never marked. Opacity and
    `translate` do not change the box and are safe on the element itself.

## The runtime

One copy of each of these three blocks per file. In a hash-routed file
(`project-website`, `web-document`, `sitemap-ia`) the script goes in its own
`<script>` block **after** the router — the runtime hooks the router by
listening to `hashchange` one step later and reading `.page.active`; it never
edits `apply()`.

Three classes in the snippets — `.lm-btn`, `.lm-spot-card`, `.lm-stat` —
are stand-ins for the host's own button, card and stat styles and carry no
rules here; use the host's classes in their place.

### The bridge — map `--lm-*` onto the host's tokens

The names on the right are `project-website`'s. For another template, point
each at that template's equivalent (`paper-brief`: `--ink`, `--paper`,
`--accent`). Every `--lm-*` name a pattern reads is here.

```html
<style>
/* lm bridge — the motion library reads only --lm-* names; this block maps
   them onto this file's own tokens. Values stay the host's. */
:root{
  --lm-accent:var(--accent);
  --lm-accent-2:var(--accent-strong);
  --lm-fg:var(--fg);
  --lm-fg-bright:var(--fg-bright);
  --lm-fg-dim:var(--fg-dim);
  --lm-surface:var(--surface);
  --lm-surface-2:var(--surface-2);
  --lm-border:var(--border);
  --lm-glow:var(--glow);
  --lm-radius:var(--r-lg);
  --lm-ease:var(--ease);
  --lm-font-mono:var(--font-mono);
  --lm-nav-h:var(--nav-h);
  --lm-dur:.6s;
  --lm-dur-fast:.25s;
  --lm-stagger:80ms;
  --lm-marquee-duration:28s;
}
</style>
```

### The base — reveal, focus, and the media rule everything else copies

```html
<style>
/* lm base. Base styles are the finished state; motion lives inside the
   screen + no-preference media block, so reduced motion and print both get
   the finished page without a rule each. */
[class*="lm-"]:focus-visible{outline:2px solid var(--lm-accent,currentColor);outline-offset:2px}
.lm-vh{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-reveal{opacity:0;transform:translateY(14px);transition:opacity var(--lm-dur,.6s) var(--lm-ease,ease),transform var(--lm-dur,.6s) var(--lm-ease,ease)}
  .lm-reveal.is-in{opacity:1;transform:none}
}
</style>
```

### The script — arming, fail-visible, activation, cancellation

```html
<script>
/* lm — the motion runtime. Place AFTER the file's router so its hashchange
   listener runs after the router has toggled .page.active. Never edit the
   router; hook here.
     lm.onActivate(fn)  fn(scope) runs on every page activation and may
                        return stop(), called when that page deactivates
     lm.whenIn(el, fn)  fn once el has scrolled into view (or been shown)
     lm.reduced()       prefers-reduced-motion: reduce
     lm.fine()          a hovering, fine pointer (desktop) is present   */
window.lm = (function(){
  var RM   = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : { matches:false };
  var FINE = window.matchMedia ? matchMedia('(hover: hover) and (pointer: fine)') : { matches:false };
  var SEL  = '.lm-reveal:not(.is-in), .lm-on:not(.is-in)';
  var hooks = [], stops = [], current = null, looseArmed = false;

  function reduced(){ return !!RM.matches; }
  function fine(){ return !!FINE.matches; }

  function mark(el){
    if(el.classList.contains('is-in')) return;
    el.classList.add('is-in');
    if(io) io.unobserve(el);
    el.dispatchEvent(new CustomEvent('lm:in'));
  }
  var io = ('IntersectionObserver' in window)
    ? new IntersectionObserver(function(entries){
        entries.forEach(function(e){ if(e.isIntersecting) mark(e.target); });
      }, { rootMargin:'0px 0px -8% 0px', threshold:0.05 })
    : null;

  /* L-022: the observer is never the only path to visible. No observer, a
     reduced-motion reader, or a hidden tab (throttled timers, no callbacks)
     all show everything now; a live tab gets a fail-visible timer that shows
     the lot if not one element in the scope has been reported. */
  function arm(els, probe){
    if(!els.length) return;
    if(!io || reduced() || document.hidden){ els.forEach(mark); return; }
    els.forEach(function(el){ io.observe(el); });
    setTimeout(function(){ if(!probe()) els.forEach(mark); }, 1200);
  }
  function reveal(scope){
    scope = scope || document;
    var els = Array.prototype.slice.call(scope.querySelectorAll(SEL));
    arm(els, function(){ return !!scope.querySelector('.lm-reveal.is-in, .lm-on.is-in'); });
  }
  /* Elements outside every routed page (a shared footer) are armed once. */
  function revealLoose(){
    if(looseArmed) return; looseArmed = true;
    var els = Array.prototype.filter.call(document.querySelectorAll(SEL), function(el){ return !el.closest('.page'); });
    arm(els, function(){ return els.some(function(el){ return el.classList.contains('is-in'); }); });
  }
  function showAll(scope){ (scope || document).querySelectorAll(SEL).forEach(mark); }
  function whenIn(el, fn){
    if(el.classList.contains('is-in')) fn();
    else el.addEventListener('lm:in', function h(){ el.removeEventListener('lm:in', h); fn(); });
  }

  function run(fn, scope){
    var stop = null;
    try { stop = fn(scope); } catch(e){ if(window.console) console.error(e); }
    if(typeof stop === 'function') stops.push(stop);
  }
  function activate(scope){
    scope = scope || document.querySelector('.page.active') || document.body;
    if(scope === current) return;
    deactivate();
    current = scope;
    hooks.forEach(function(fn){ run(fn, scope); });   /* listeners first, */
    reveal(scope);                                     /* then the reveals */
    if(scope !== document.body) revealLoose();
  }
  function deactivate(){
    stops.splice(0).forEach(function(s){ try { s(); } catch(e){} });
    current = null;
  }
  function onActivate(fn){ hooks.push(fn); if(current) run(fn, current); }

  window.addEventListener('hashchange', function(){ activate(); });
  document.addEventListener('visibilitychange', function(){ if(!document.hidden && current) reveal(current); });
  window.addEventListener('beforeprint', function(){ showAll(document); });
  if(RM.addEventListener) RM.addEventListener('change', function(){
    if(reduced()) showAll(document);
    var s = current; deactivate(); activate(s);
  });
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ activate(); });
  else activate();

  return { reduced:reduced, fine:fine, reveal:reveal, showAll:showAll, whenIn:whenIn,
           activate:activate, deactivate:deactivate, onActivate:onActivate,
           scope:function(){ return current; } };
})();
</script>
```

**Trap.** `activate()` is skipped when the scope has not changed, so a
language switch (`#/ko/home` from `#/en/home`) does not restart loops — and
a hook registered after boot runs immediately for the current page. Elements
already `.is-in` are never re-observed, so revisiting a page does not replay
its entrance. Hooks run **before** the reveals are armed so that a
`lm.whenIn` listener is in place when a reduced-motion reader's elements are
shown synchronously.

**Rule.** Every pattern that runs code registers through `lm.onActivate`
and returns its stop. A pattern that only needs "when scrolled to" uses
`lm.whenIn(el, fn)` on an element carrying `lm-on` (trigger only) or
`lm-reveal` (trigger plus fade-up).

---

# A. Reveal and scroll

## 01 · Reveal on scroll — `lm-reveal`

Fade-up when scrolled to. The runtime arms it; there is no JS to add.

```html
<div class="lm-reveal">
  <h2>Fades up once, the first time it is scrolled to.</h2>
</div>
```

```css
/* Provided by the base block. Nothing to add. */
```

**Trap.** `.lm-reveal` starts at `opacity:0` on screen, so it is only ever
made visible by the runtime; a page that carries the class without the
runtime script renders blank. The base block and the script travel together.

**Rule.** Put `lm-reveal` on a section head or a whole group, not on every
paragraph. Use `lm-on` instead when a pattern needs the trigger without the
fade (typewriter, count-up, draw).

## 02 · Staggered list — `lm-stagger`

Children rise one after another, `--i` apart. Works on any list, grid, or row set.

```html
<ul class="lm-stagger lm-reveal">
  <li style="--i:0">First</li>
  <li style="--i:1">Second</li>
  <li style="--i:2">Third</li>
</ul>
```

```css
@media screen and (prefers-reduced-motion: no-preference){
  .lm-stagger>*{opacity:0;transform:translateY(10px);transition:opacity var(--lm-dur,.6s) var(--lm-ease,ease),transform var(--lm-dur,.6s) var(--lm-ease,ease);transition-delay:min(calc(var(--i,0)*var(--lm-stagger,80ms)),720ms)}
  .lm-stagger.is-in>*{opacity:1;transform:none}
  .lm-stagger.lm-reveal{transition:none}
  .lm-stagger>tr{transform:none}
}
```

```js
/* Numbers the children when the markup did not. */
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-stagger').forEach(function(list){
    Array.prototype.forEach.call(list.children, function(c, i){
      if(!c.style.getPropertyValue('--i')) c.style.setProperty('--i', i);
    });
  });
});
```

**Trap.** The list itself must carry `lm-reveal` (or `lm-on`) — that is what
delivers `.is-in`. `lm-reveal` on the list and on each child double-fades.
On a `<tbody>`, `--i` goes on the `<tr>`s, and rows fade without rising:
Firefox does not transform table rows, so the rule strips it for `tr`.

**Rule.** The delay is capped at 720ms whatever `--i` is: a reader waits for
the last item, and twelve items at 80ms is already a second.

## 03 · Scroll-driven reveal — `lm-view`

Progress tied to scroll position, not time, with `animation-timeline: view()`.
Where the browser has no scroll timelines the element is simply visible —
pair it with `lm-reveal` to get the timed fade there instead.

```html
<figure class="lm-view lm-reveal">
  <p>Rises as it enters the viewport; scrolls back down if you do.</p>
</figure>
```

```css
@media screen and (prefers-reduced-motion: no-preference){
  @supports (animation-timeline: view()){
    .lm-view{animation:lm-view-in linear both;animation-timeline:view();animation-range:entry 0% entry 70%}
    /* The animation wins the cascade over .lm-reveal's opacity, so the two
       classes can share an element: view() here, the IO fade elsewhere. */
    .lm-view.lm-reveal{transition:none}
  }
  @keyframes lm-view-in{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:none}}
}
```

**Trap.** Inside a hash-routed page the timeline attaches when the page is
laid out, so an element above the fold at activation is already at its
`to` state — correct, and easy to mistake for "not working". `view()`
measures the element's own box, so a zero-height wrapper never animates.

**Rule.** Use `entry` ranges for reveals and leave `exit` alone: content that
fades out as the reader reaches it is content they cannot read.

## 04 · Wipe — `lm-wipe`

A horizontal wipe from the left, on a bar, a rule, a track, or an image.

```html
<div class="lm-wipe lm-on" style="height:2px;background:var(--lm-accent,currentColor)"></div>
```

```css
.lm-wipe{-webkit-mask:linear-gradient(#000 0 0) 0 0/100% 100% no-repeat;mask:linear-gradient(#000 0 0) 0 0/100% 100% no-repeat}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-wipe{transition:-webkit-mask-size 1.2s var(--lm-ease,ease),mask-size 1.2s var(--lm-ease,ease)}
  .lm-wipe:not(.is-in){-webkit-mask-size:0% 100%;mask-size:0% 100%}
}
```

**Trap.** A mask, not `clip-path`, and it is not a style choice: the wipe
hides the element that is itself observed, and the observer measures the
clipped box — an element clipped to nothing reports `intersectionRatio: 0`
and never comes in (rule 11). A mask changes paint, not geometry. The mask
also covers borders and `box-shadow`, so a glow that should stay put goes
on the parent.

**Rule.** One wipe per screen. Two wipes running side by side read as a
loading indicator.

## 05 · Curtain — `lm-curtain`

A pane covering the stage parts from the middle. Timed on `.is-in`, or driven
by scroll when `lm-view` is added and the browser supports it.

```html
<div class="lm-curtain lm-on">
  <div class="lm-curtain-stage">
    <h3>What was behind the curtain.</h3>
  </div>
  <div class="lm-curtain-pane" aria-hidden="true"></div>
</div>
```

```css
.lm-curtain{position:relative;overflow:hidden;border-radius:var(--lm-radius,0)}
.lm-curtain-stage{position:relative}
.lm-curtain-pane{position:absolute;inset:0;background:var(--lm-surface-2,transparent);clip-path:inset(0 50% 0 50%);pointer-events:none}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-curtain:not(.is-in) .lm-curtain-pane{clip-path:inset(0 0 0 0)}
  .lm-curtain-pane{transition:clip-path 1s var(--lm-ease,ease)}
  @supports (animation-timeline: view()){
    .lm-curtain.lm-view{view-timeline-name:--lm-curtain;animation:none}
    .lm-curtain.lm-view .lm-curtain-pane{transition:none;animation:lm-curtain-open linear both;animation-timeline:--lm-curtain;animation-range:entry 30% cover 60%}
  }
  @keyframes lm-curtain-open{from{clip-path:inset(0 0 0 0)}to{clip-path:inset(0 50% 0 50%)}}
}
```

**Trap.** The pane is a real element, not a pseudo, so it can carry
`aria-hidden` — a pseudo-element cannot. Its finished state is a zero-width
strip, which is why the base rule keeps `inset(0 50% 0 50%)` and print shows
the stage.

**Rule.** Reserve it for the one reveal on a page that is a reveal: a
product, a result, an answer. A curtain on a paragraph is a delay.

## 06 · SVG path draw — `lm-draw`

A stroke draws itself. `pathLength="1"` normalises every path so no
`getTotalLength()` is needed, and several paths stagger with `--i`.

```html
<svg class="lm-draw lm-on" viewBox="0 0 600 60" aria-hidden="true" style="width:100%;height:auto">
  <path pathLength="1" d="M8 30 C 120 -10, 240 70, 360 30 S 560 -10, 592 30"/>
  <path pathLength="1" style="--i:1" d="M8 48 H 592"/>
</svg>
```

```css
.lm-draw path{fill:none;stroke:var(--lm-accent,currentColor);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 1;stroke-dashoffset:0}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-draw:not(.is-in) path{stroke-dashoffset:1}
  .lm-draw.is-in path{animation:lm-draw 1.4s var(--lm-ease,ease) both;animation-delay:calc(var(--i,0)*.35s)}
  .lm-draw.is-done path{animation:none}
  @supports (animation-timeline: view()){
    .lm-draw.lm-view{view-timeline-name:--lm-draw}
    .lm-draw.lm-view path{animation:lm-draw linear both;animation-timeline:--lm-draw;animation-range:entry 20% cover 70%;animation-delay:0s}
  }
  @keyframes lm-draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-draw').forEach(function(svg){
    if(svg.getAttribute('data-lm-ready')) return;
    svg.setAttribute('data-lm-ready', '1');
    var paths = svg.querySelectorAll('path'), done = 0;
    paths.forEach(function(p){ p.addEventListener('animationend', function(){ if(++done >= paths.length) svg.classList.add('is-done'); }); });
  });
});
```

**Trap.** `stroke-dasharray:1 1` — dash *and* gap of one path length — is
what keeps a round-capped dash from leaving a dot at the start before it
draws. The `is-done` latch is the same one the typewriter carries: a CSS
animation replays whenever a hash router re-displays the page, and a drawn
line should stay drawn. A `view()` timeline is named on the `<svg>` and referenced by the
path: the path's own box is not a view-timeline subject in every engine.

**Rule.** Diagram lines, timelines, and underlines. Not chart data: a bar
that draws itself in is an animation, a bar that grows to a value is a claim
about the value.

## 07 · Sticky narrative — `lm-sticky`

A pinned visual on the left, steps scrolling past on the right; the step in
the middle of the viewport is `is-on` and switches the visual's state.
Everything is readable with no observer at all — `is-on` only adds emphasis.

```html
<div class="lm-sticky">
  <div class="lm-sticky-pin">
    <div class="lm-sticky-state is-on" data-lm-state="1"><strong>State one</strong></div>
    <div class="lm-sticky-state" data-lm-state="2"><strong>State two</strong></div>
    <div class="lm-sticky-state" data-lm-state="3"><strong>State three</strong></div>
  </div>
  <ol class="lm-sticky-steps">
    <li class="lm-sticky-step is-on" data-lm-state="1"><h3>Step one</h3><p>Scroll and the pinned panel changes with the step under your eye.</p></li>
    <li class="lm-sticky-step" data-lm-state="2"><h3>Step two</h3><p>Each step names the state it shows.</p></li>
    <li class="lm-sticky-step" data-lm-state="3"><h3>Step three</h3><p>All steps stay fully readable; the observer only adds emphasis.</p></li>
  </ol>
</div>
```

```css
.lm-sticky{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:start}
.lm-sticky-pin{position:sticky;top:calc(var(--lm-nav-h,0px) + 24px);display:grid;min-height:260px;border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0);background:var(--lm-surface,transparent)}
.lm-sticky-state{grid-area:1/1;padding:28px;opacity:0}
.lm-sticky-state.is-on{opacity:1}
.lm-sticky-steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:32px}
.lm-sticky-step{padding:24px;border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0)}
.lm-sticky-step.is-on{border-color:var(--lm-accent,currentColor)}
.lm-sticky-step h3{margin:0 0 8px}
.lm-sticky-step p{margin:0}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-sticky-state{transition:opacity .5s var(--lm-ease,ease)}
  .lm-sticky-step{transition:border-color .3s}
}
@media (max-width:900px){.lm-sticky{grid-template-columns:1fr}.lm-sticky-pin{position:static}}
```

```js
lm.onActivate(function(scope){
  var ios = [];
  scope.querySelectorAll('.lm-sticky').forEach(function(root){
    if(!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        var k = e.target.getAttribute('data-lm-state');
        root.querySelectorAll('[data-lm-state]').forEach(function(el){
          el.classList.toggle('is-on', el.getAttribute('data-lm-state') === k);
        });
      });
    }, { rootMargin:'-40% 0px -40% 0px', threshold:0 });
    root.querySelectorAll('.lm-sticky-step').forEach(function(s){ io.observe(s); });
    ios.push(io);
  });
  return function(){ ios.forEach(function(io){ io.disconnect(); }); };
});
```

**Trap.** This observer drives *state*, not visibility, which is why it may
be the only mechanism: with no callbacks the page shows state one and every
step, all readable. The pin needs `--lm-nav-h` or it slides under a sticky
nav. Below 900px the pin becomes static — a pinned panel on a phone eats the
screen.

**Rule.** Three to five steps. The pinned states share one grid cell and
cross-fade, so they must be the same size or the pin jumps.

## 08 · Sticky card stack — `lm-stack`

Cards pin as they arrive and stack, each offset by `--i`. Pure CSS.

```html
<div class="lm-stack">
  <article class="lm-stack-card" style="--i:0"><h3>One</h3><p>The first card pins first.</p></article>
  <article class="lm-stack-card" style="--i:1"><h3>Two</h3><p>The second lands on it, a little lower.</p></article>
  <article class="lm-stack-card" style="--i:2"><h3>Three</h3><p>And so on, until the stack scrolls away.</p></article>
</div>
```

```css
.lm-stack{padding-bottom:20vh}
.lm-stack-card{position:sticky;top:calc(var(--lm-nav-h,0px) + 24px + var(--i,0)*14px);margin-bottom:24px;min-height:200px;padding:28px;background:var(--lm-surface,transparent);border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0);box-shadow:0 -8px 24px -16px var(--lm-glow,transparent)}
.lm-stack-card h3{margin:0 0 8px}
.lm-stack-card p{margin:0}
```

**Trap.** Each card must be opaque (`--lm-surface`) or the one beneath shows
through. The bottom padding is what lets the last card land before the
section ends; without it the stack never completes. Cards later in the DOM
paint on top, so no `z-index` is needed — and adding one breaks the order.

**Rule.** Two to six cards of similar height. Do not put the only copy of
an instruction in a card that another card will cover.

## 09 · Horizontal track — `lm-track`

A gallery that scrolls sideways with `scroll-snap`, wheel, touch, keyboard
and two buttons. Never hijacks the vertical scroll. A progress bar appears
where `animation-timeline: scroll()` exists.

```html
<div class="lm-track-wrap">
  <ul class="lm-track" tabindex="0" role="group" aria-label="Gallery — scrolls sideways">
    <li class="lm-track-item"><h3>01</h3><p>Snap to each item.</p></li>
    <li class="lm-track-item"><h3>02</h3><p>Wheel, swipe, arrow keys, or the buttons.</p></li>
    <li class="lm-track-item"><h3>03</h3><p>The page never scrolls sideways.</p></li>
    <li class="lm-track-item"><h3>04</h3><p>The bar below tracks the position.</p></li>
  </ul>
  <div class="lm-track-bar" aria-hidden="true"><i></i></div>
  <div class="lm-track-nav">
    <button type="button" class="lm-track-btn" data-lm-track="-1" aria-label="Previous">&larr;</button>
    <button type="button" class="lm-track-btn" data-lm-track="1" aria-label="Next">&rarr;</button>
  </div>
</div>
```

```css
.lm-track-wrap{timeline-scope:--lm-track}
.lm-track{display:flex;gap:16px;list-style:none;margin:0;padding:0 0 6px;overflow-x:auto;scroll-snap-type:x mandatory;overscroll-behavior-x:contain;scrollbar-width:none;scroll-timeline:--lm-track inline}
.lm-track::-webkit-scrollbar{display:none}
.lm-track-item{flex:0 0 min(78%,340px);scroll-snap-align:start;padding:24px;background:var(--lm-surface,transparent);border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0)}
.lm-track-item h3{margin:0 0 6px}
.lm-track-item p{margin:0}
.lm-track-bar{display:none;height:2px;margin-top:12px;background:var(--lm-border,currentColor);overflow:hidden}
.lm-track-bar i{display:block;height:100%;background:var(--lm-accent,currentColor);transform-origin:0 50%;transform:scaleX(1)}
.lm-track-nav{display:flex;gap:8px;margin-top:12px}
.lm-track-btn{width:38px;height:38px;border-radius:999px;border:1px solid var(--lm-border,currentColor);background:var(--lm-surface,transparent);color:var(--lm-fg,currentColor);cursor:pointer}
@supports (animation-timeline: scroll()){
  .lm-track-bar{display:block}
  .lm-track-bar i{animation:lm-track-bar linear both;animation-timeline:--lm-track}
  @keyframes lm-track-bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-track{scroll-behavior:smooth}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-track-wrap').forEach(function(wrap){
    if(wrap.getAttribute('data-lm-ready')) return;
    wrap.setAttribute('data-lm-ready', '1');
    var track = wrap.querySelector('.lm-track');
    wrap.querySelectorAll('[data-lm-track]').forEach(function(btn){
      btn.addEventListener('click', function(){
        var item = track.querySelector('.lm-track-item');
        var step = item ? item.getBoundingClientRect().width + 16 : track.clientWidth;
        track.scrollBy({ left: step * parseInt(btn.getAttribute('data-lm-track'), 10), behavior: lm.reduced() ? 'auto' : 'smooth' });
      });
    });
  });
});
```

**Trap.** The progress bar is scroll-driven or absent — it is hidden outside
`@supports` rather than faked with a listener. It sits outside the
reduced-motion block on purpose: it is linked to the reader's own scrolling
and never moves by itself, so like a scrollbar it stays on under reduced
motion. `overflow-x:auto` on the track
is also what exempts its contents from the repository's overflow gate: the
list scrolls itself, so the page never widens.

**Rule.** The track is a `<ul>` with `tabindex="0"` so keyboard readers can
focus and arrow through it. Keep every item's text inside the item; nothing
should depend on the bar.

## 10 · Depth parallax — `lm-parallax`

Layers at different depths move at different rates as the section passes,
`--lm-depth` apart. Scroll-driven only; a browser without `view()` shows the
layers still, which is the finished composition.

```html
<div class="lm-parallax">
  <div class="lm-parallax-layer" style="--lm-depth:-.6" aria-hidden="true"><span class="lm-parallax-orb"></span></div>
  <div class="lm-parallax-layer" style="--lm-depth:.4"><h3>Foreground moves faster</h3><p>Background barely moves.</p></div>
</div>
```

```css
.lm-parallax{position:relative;min-height:320px;display:grid;overflow:hidden;border-radius:var(--lm-radius,0);background:var(--lm-surface,transparent);view-timeline-name:--lm-parallax}
.lm-parallax-layer{grid-area:1/1;display:grid;place-items:center;text-align:center;padding:32px}
.lm-parallax-orb{width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,var(--lm-glow,transparent),transparent 70%)}
@media screen and (prefers-reduced-motion: no-preference){
  @supports (animation-timeline: view()){
    .lm-parallax-layer{animation:lm-parallax linear both;animation-timeline:--lm-parallax;animation-range:cover 0% cover 100%}
  }
  @keyframes lm-parallax{from{transform:translateY(calc(var(--lm-depth,0)*-80px))}to{transform:translateY(calc(var(--lm-depth,0)*80px))}}
}
```

**Trap.** One keyframe rule serves every layer because the amount is a
custom property — write no per-layer keyframes. `overflow:hidden` on the
section keeps the moving layers from widening the page.

**Rule.** Depths between −1 and 1. The text layer stays near 0; the reader
should never chase a paragraph.

## 11 · Split columns — `lm-split`

Two columns move in opposite directions inside a pinned viewport as the
section scrolls. Scroll-driven only: without `view()` the section is two
static columns, laid out normally.

```html
<div class="lm-split">
  <div class="lm-split-pin">
    <div class="lm-split-col">
      <div class="lm-split-cell"><h3>Strategy</h3></div>
      <div class="lm-split-cell"><h3>Design</h3></div>
      <div class="lm-split-cell"><h3>Build</h3></div>
    </div>
    <div class="lm-split-col">
      <div class="lm-split-cell"><h3>Discovery</h3></div>
      <div class="lm-split-cell"><h3>Architecture</h3></div>
      <div class="lm-split-cell"><h3>Launch</h3></div>
    </div>
  </div>
</div>
```

```css
.lm-split-pin{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--lm-border,currentColor);border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0);overflow:hidden}
.lm-split-col{background:var(--lm-surface,transparent)}
.lm-split-cell{display:grid;place-items:center;min-height:120px;padding:24px;text-align:center}
.lm-split-cell h3{margin:0}
@media screen and (prefers-reduced-motion: no-preference){
  @supports (animation-timeline: view()){
    .lm-split{height:220vh;view-timeline-name:--lm-split}
    .lm-split-pin{position:sticky;top:var(--lm-nav-h,0px);height:calc(100vh - var(--lm-nav-h,0px))}
    .lm-split-cell{height:calc(100vh - var(--lm-nav-h,0px))}
    .lm-split-col{animation:lm-split-up linear both;animation-timeline:--lm-split;animation-range:contain 0% contain 100%}
    .lm-split-col:last-child{animation-name:lm-split-down}
  }
  @keyframes lm-split-up{from{transform:translateY(0)}to{transform:translateY(calc(-100% + 100vh - var(--lm-nav-h,0px)))}}
  @keyframes lm-split-down{from{transform:translateY(calc(-100% + 100vh - var(--lm-nav-h,0px)))}to{transform:translateY(0)}}
}
```

**Trap.** The tall section and the sticky pin exist only inside
`@supports`, so the fallback is a normal grid and not a 220vh gap. The
`contain` range is what starts the motion when the pin engages rather than
when the section's top enters.

**Rule.** Every cell is a heading or an image; anything longer moves too
fast to read. Three or four cells a side.

## 12 · Section colour shift — `lm-band`

The page ground changes as each band arrives. A fixed backdrop behind the
band fades in with the band's view timeline; where there are no scroll
timelines it fades in when the band is observed, and with neither the page
keeps its own ground.

```html
<section class="lm-band lm-on" style="--lm-band-color:var(--lm-surface-2,transparent)">
  <div class="lm-band-bg" aria-hidden="true"></div>
  <h3>This band tints the whole page ground.</h3>
</section>
```

```css
.lm-band{position:relative;view-timeline-name:--lm-band}
.lm-band-bg{position:fixed;inset:0;z-index:-1;background:var(--lm-band-color,transparent);opacity:0;pointer-events:none}
.lm-band.is-in .lm-band-bg{opacity:1}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-band-bg{transition:opacity .8s var(--lm-ease,ease)}
  @supports (animation-timeline: view()){
    .lm-band.is-in .lm-band-bg,.lm-band-bg{transition:none;opacity:0;animation:lm-band linear both;animation-timeline:--lm-band;animation-range:cover 0% cover 100%}
  }
  @keyframes lm-band{0%{opacity:0}25%{opacity:1}75%{opacity:1}100%{opacity:0}}
}
```

**Trap.** `position:fixed` is contained by any ancestor with a `transform`,
`filter` or `will-change` — including a `.lm-reveal` that has not finished
its transition — so a band is never nested inside a reveal. `z-index:-1`
paints above the body background and below everything in flow; a band
inside a section that paints its own opaque ground shows nothing.

**Rule.** One tint per chapter and never on the first screen. Keep text
contrast measured against the tinted ground, not the default one.

---

# B. Text

## 13 · Text mask — `lm-textmask`

A headline's fill sweeps from faint to bright, `background-clip: text`
driven. Timed on `.is-in`; scroll-driven with `lm-view` where supported.

```html
<h2 class="lm-textmask lm-on">The fill sweeps in from the left.</h2>
```

```css
.lm-textmask{background-image:linear-gradient(90deg,var(--lm-fg-bright,currentColor) 0 50%,var(--lm-fg-dim,currentColor) 50% 100%);background-size:200% 100%;background-position:0 0;-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-textmask:not(.is-in){background-position:100% 0}
  .lm-textmask{transition:background-position 1.1s var(--lm-ease,ease)}
  @supports (animation-timeline: view()){
    .lm-textmask.lm-view{transition:none;animation:lm-textmask linear both;animation-timeline:view();animation-range:entry 10% cover 45%}
    .lm-textmask.lm-view:not(.is-in){background-position:0 0}
  }
  @keyframes lm-textmask{from{background-position:100% 0}to{background-position:0 0}}
}
@media print{.lm-textmask{background:none;color:inherit;-webkit-text-fill-color:currentColor}}
```

**Trap.** Gradient text is transparent text: a print stylesheet that drops
backgrounds prints nothing, so the print rule restores `currentColor`. A
headline that already carries a gradient (`.hero-title` in
`project-website`) cannot take this — the two `background-image`s fight.

**Rule.** Headlines only, one per page. The sweep is 1.1s; a reader who
arrives mid-sweep still reads the dim half.

## 14 · Typewriter — `lm-type`

Monospace text types itself with a moving caret. `clip-path` plus
`steps()`, so no layout moves and no timer runs; `--lm-chars` is set by the
script from the text length.

```html
<code class="lm-type lm-on"><span class="lm-type-text">npm install hi-ted-meet-lisa</span></code>
```

```css
.lm-type{position:relative;display:inline-block;font-family:var(--lm-font-mono,monospace);white-space:nowrap}
.lm-type-text{display:inline-block}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-type:not(.is-in) .lm-type-text{clip-path:inset(0 100% 0 0)}
  .lm-type.is-in .lm-type-text{animation:lm-type calc(var(--lm-chars,20)*55ms) steps(var(--lm-chars,20),end) both;animation-delay:var(--lm-type-delay,0s)}
  .lm-type.is-in::after{content:"";position:absolute;left:0;top:.1em;width:.08em;height:1.1em;background:var(--lm-accent,currentColor);animation:lm-type-caret calc(var(--lm-chars,20)*55ms) steps(var(--lm-chars,20),end) both,lm-type-blink 1s steps(2) infinite;animation-delay:var(--lm-type-delay,0s),0s}
  .lm-type.is-done .lm-type-text{animation:none}
  .lm-type.is-done::after{content:none}
  @keyframes lm-type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
  @keyframes lm-type-caret{from{transform:translateX(0)}to{transform:translateX(calc(var(--lm-chars,20)*1ch))}}
  @keyframes lm-type-blink{50%{opacity:0}}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-type').forEach(function(el){
    var t = el.querySelector('.lm-type-text');
    if(!t) return;
    el.style.setProperty('--lm-chars', t.textContent.length);
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    t.addEventListener('animationend', function(){ el.classList.add('is-done'); });
  });
});
```

**Trap.** A CSS animation restarts every time its element goes from
`display:none` back to displayed — which is what a hash router does to a
page on every revisit — so the command would go blank for the delay and
type again each time Home is opened. `animationend` latches `is-done`, which
switches the animation off and leaves the typed text; the runtime's rule
that a revisit never replays an entrance holds. The caret travels in `ch`
units, so this is for monospace Latin text — Hangul and CJK glyphs are
wider than `1ch` and the caret falls behind. A copy-to-clipboard button reading `textContent` is unaffected: the
text is all there, only clipped. Inside `project-website`'s `.cmd-text` the
element sits *inside* the `data-copy-text` code so the copied string stays
whole.

**Rule.** One command, once, on the first screen. Never on prose, never in
a loop: the source demo's cycling headline is a carousel with extra steps.
When the command sits inside a staggered hero, set `--lm-type-delay` on
the element to the moment its row has landed, so the caret starts on a
visible box rather than a fading one.

## 15 · Scramble decode — `lm-scramble`

Characters cycle through glyphs and resolve into the word. A finite rAF
loop (≤1.2s), cancelled on deactivation. The real word stays in the tree for
screen readers.

```html
<h3 class="lm-scramble lm-on" data-lm-text="Decode the signal"><span class="lm-vh">Decode the signal</span><span class="lm-scramble-run" aria-hidden="true">Decode the signal</span></h3>
```

```css
.lm-scramble{font-family:var(--lm-font-mono,monospace)}
.lm-scramble-run{display:inline-block;white-space:pre}
```

```js
lm.onActivate(function(scope){
  var frames = [];
  var GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=';
  scope.querySelectorAll('.lm-scramble').forEach(function(el){
    var run = el.querySelector('.lm-scramble-run'), text = el.getAttribute('data-lm-text') || '';
    if(!run || el.getAttribute('data-lm-done')) return;
    lm.whenIn(el, function(){
      el.setAttribute('data-lm-done', '1');
      if(lm.reduced()){ run.textContent = text; return; }
      var start = null, id;
      function frame(ts){
        if(start === null) start = ts;
        var p = Math.min((ts - start) / 1100, 1), out = '';
        for(var i = 0; i < text.length; i++){
          if(text[i] === ' '){ out += ' '; continue; }
          out += (p >= (i / text.length) * .7 + .15) ? text[i] : GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
        }
        run.textContent = out;
        if(p < 1) id = requestAnimationFrame(frame); else run.textContent = text;
      }
      id = requestAnimationFrame(frame);
      frames.push(function(){ cancelAnimationFrame(id); run.textContent = text; });
    });
  });
  return function(){ frames.forEach(function(f){ f(); }); };
});
```

**Trap.** The stop function also writes the final text, so a page left
mid-decode never shows glyph soup when it is revisited. `data-lm-done`
means it plays once — remove the attribute to replay on every visit, and
know that readers will notice.

**Rule.** Monospace only, one line, no more than about twenty characters:
proportional text jitters as glyph widths change.

## 16 · Glitch — `lm-glitch`

RGB-split flicker on hover or focus. The two offset layers are real
`aria-hidden` spans the script clones, not pseudo-elements, so the bilingual
spans inside them keep toggling with `body[data-lang]`.

```html
<a href="#" class="lm-glitch"><span class="lm-glitch-base">Glitch</span></a>
```

```css
.lm-glitch{position:relative;display:inline-block;text-decoration:none;color:inherit}
.lm-glitch-layer{position:absolute;inset:0;opacity:0;pointer-events:none}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-glitch:hover .lm-glitch-layer,.lm-glitch:focus-visible .lm-glitch-layer{opacity:1}
  .lm-glitch:hover .lm-glitch-layer:nth-child(2),.lm-glitch:focus-visible .lm-glitch-layer:nth-child(2){color:var(--lm-accent,currentColor);animation:lm-glitch-a .4s steps(2) infinite}
  .lm-glitch:hover .lm-glitch-layer:nth-child(3),.lm-glitch:focus-visible .lm-glitch-layer:nth-child(3){color:var(--lm-accent-2,currentColor);animation:lm-glitch-b .4s steps(3) infinite}
  @keyframes lm-glitch-a{0%{clip-path:inset(0 0 80% 0);transform:translate(-3px,-2px)}50%{clip-path:inset(40% 0 30% 0);transform:translate(3px,1px)}100%{clip-path:inset(0 0 80% 0);transform:translate(0)}}
  @keyframes lm-glitch-b{0%{clip-path:inset(80% 0 0 0);transform:translate(3px,1px)}50%{clip-path:inset(30% 0 40% 0);transform:translate(-3px,-2px)}100%{clip-path:inset(80% 0 0 0);transform:translate(0)}}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-glitch').forEach(function(el){
    var base = el.querySelector('.lm-glitch-base');
    if(!base || el.querySelector('.lm-glitch-layer')) return;
    for(var i = 0; i < 2; i++){
      var c = base.cloneNode(true);
      c.className = 'lm-glitch-layer'; c.setAttribute('aria-hidden', 'true');
      el.appendChild(c);
    }
  });
});
```

**Trap.** The layers are absolutely positioned over the base, so the base
must be the element's only in-flow child and the element `inline-block`;
a wrapping headline gives the layers the wrong box.

**Rule.** A word, a logotype, a nav item. Not a sentence, and never running
without a hover — constant glitching is noise.

## 17 · Gradient text — `lm-gradient-text`

A gradient of the host's accents slides along a headline, forever and
slowly. Still under reduced motion; solid in print.

```html
<h2 class="lm-gradient-text">Gradient in motion</h2>
```

```css
.lm-gradient-text{background-image:linear-gradient(90deg,var(--lm-accent,currentColor),var(--lm-fg-bright,currentColor),var(--lm-accent-2,currentColor),var(--lm-accent,currentColor));background-size:300% 100%;background-position:0 0;-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-gradient-text{animation:lm-gradient 7s linear infinite}
  @keyframes lm-gradient{to{background-position:300% 0}}
}
@media print{.lm-gradient-text{background:none;color:inherit;-webkit-text-fill-color:currentColor}}
```

**Trap.** The last stop repeats the first so the loop has no seam.
`background-position` is paint, not layout, so the loop is cheap; inside an
inactive hash-routed page it costs nothing because `display:none` stops it.

**Rule.** One element per file. It is an accent, not a body style, and it
competes with any `lm-textmask` on the same screen.

## 18 · Circular text — `lm-ring`

Text on a spinning circle, SVG `textPath`. Rotates on time; with
`lm-ring-scroll` it rotates with the document scroll where `scroll()` exists.

```html
<div class="lm-ring" aria-hidden="true">
  <svg class="lm-ring-svg" viewBox="0 0 200 200">
    <defs><path id="lm-ring-path-1" d="M100,100 m-72,0 a72,72 0 1,1 144,0 a72,72 0 1,1 -144,0"/></defs>
    <text><textPath href="#lm-ring-path-1">DESIGN · BUILD · SHIP · DESIGN · BUILD · SHIP · </textPath></text>
  </svg>
  <span class="lm-ring-centre">&rarr;</span>
</div>
```

```css
.lm-ring{position:relative;width:160px;height:160px;overflow:hidden;border-radius:50%}
.lm-ring-svg{width:100%;height:100%;display:block}
.lm-ring-svg text{fill:var(--lm-fg-dim,currentColor);font-family:var(--lm-font-mono,monospace);font-size:12.5px;letter-spacing:.22em}
.lm-ring-centre{position:absolute;inset:0;display:grid;place-items:center;font-size:24px;color:var(--lm-accent,currentColor)}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-ring-svg{animation:lm-spin 24s linear infinite}
  @supports (animation-timeline: scroll()){
    .lm-ring-scroll .lm-ring-svg{animation:lm-spin linear both;animation-timeline:scroll(root)}
  }
  @keyframes lm-spin{to{transform:rotate(360deg)}}
}
```

**Trap.** The `<path id>` must be unique in the file — two rings that share
`lm-ring-path-1` both draw on the first. The text is decorative and the
whole ring is `aria-hidden`; say the words somewhere real. `overflow:hidden`
on the wrapper is load-bearing: a rotating square's corners reach 29px past
its box and widen a 375px page — the text circle sits inside the square at
every angle, so clipping costs nothing.

**Rule.** A badge beside a CTA or a section corner. Text length is tuned to
the circumference — pad with the separator until the ring closes.

## 19 · Marquee — `lm-marquee`

An endless band, pure `@keyframes`, duration from `--lm-marquee-duration`.
Pauses on hover and focus. Under reduced motion it becomes a wrapping row
and the copy disappears.

```html
<div class="lm-marquee">
  <ul class="lm-marquee-track">
    <li>Claude Code</li><li>Codex</li><li>Pi</li><li>OpenCode</li><li>Hermes</li>
  </ul>
  <ul class="lm-marquee-track" aria-hidden="true">
    <li>Claude Code</li><li>Codex</li><li>Pi</li><li>OpenCode</li><li>Hermes</li>
  </ul>
</div>
```

```css
.lm-marquee{--lm-marquee-gap:48px;display:flex;flex-wrap:wrap;gap:var(--lm-marquee-gap);width:100%;overflow:hidden}
.lm-marquee-track{display:flex;flex-wrap:wrap;gap:var(--lm-marquee-gap);list-style:none;margin:0;padding:0;color:var(--lm-fg-dim,currentColor)}
.lm-marquee-track+.lm-marquee-track{display:none}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-marquee{flex-wrap:nowrap;-webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
  .lm-marquee-track{flex:none;flex-wrap:nowrap;min-width:100%;justify-content:space-around;will-change:transform;animation:lm-marquee var(--lm-marquee-duration,28s) linear infinite}
  .lm-marquee-track+.lm-marquee-track{display:flex}
  .lm-marquee:hover .lm-marquee-track,.lm-marquee:focus-within .lm-marquee-track{animation-play-state:paused}
  @keyframes lm-marquee{to{transform:translateX(calc(-100% - var(--lm-marquee-gap)))}}
}
```

**Trap.** The second track is the seam: it must be an exact copy and
`aria-hidden`, and the keyframe travels one track *plus one gap* so the copy
lands where the original started. `min-width:100%` keeps a short list from
leaving a hole, and `width:100%` on the band keeps it as wide as its parent
rather than its content: a nowrap track has a large min-content width, so
inside a content-sized flex item (a centred column) the band would grow to
its content and escape a 375px page — the repository's overflow gate caught
exactly that. `width:100%` needs a *definite* width to resolve against: in
a centred flex column, give the marquee's parent `align-self:stretch`, or
the percentage is cyclic and the band grows to its content anyway. The `#000` in the mask is not a colour on screen — a mask
reads luminance — and is the one literal this file allows.

**Rule.** Names, logos, tags. Not sentences: nobody reads a moving
sentence. If an item is a link it pauses the band on focus, which is the
keyboard path.

---

# C. Numbers

## 20 · Count-up — `lm-count`

A number counts to its value with `Element.animate` on a registered custom
property; a CSS counter renders it. The finished, formatted number is in the
markup and returns the moment the animation ends, so screen readers and
reduced-motion readers only ever meet the real figure.

```html
<p class="lm-stat"><span class="lm-count lm-on" data-lm-to="1284"><span class="lm-count-n" aria-hidden="true"></span><span class="lm-count-final">1,284</span></span> files built</p>
```

```css
@property --lm-n{syntax:"<integer>";inherits:false;initial-value:0}
.lm-count{font-variant-numeric:tabular-nums}
.lm-count-n{display:none}
.lm-count-n::after{counter-reset:lm-n var(--lm-n);content:counter(lm-n)}
.lm-count.is-live .lm-count-n{display:inline}
.lm-count.is-live .lm-count-final{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
```

```js
lm.onActivate(function(scope){
  var anims = [];
  var can = !!(window.CSS && CSS.registerProperty && Element.prototype.animate);
  scope.querySelectorAll('.lm-count').forEach(function(el){
    var n = el.querySelector('.lm-count-n'), to = parseInt(el.getAttribute('data-lm-to'), 10);
    if(!n || isNaN(to) || !can || lm.reduced() || el.getAttribute('data-lm-done')) return;
    lm.whenIn(el, function(){
      el.setAttribute('data-lm-done', '1');
      el.classList.add('is-live');
      var a = n.animate([{ '--lm-n': 0 }, { '--lm-n': to }], { duration: Math.min(800 + to.toString().length * 300, 2200), easing: 'cubic-bezier(.22,1,.36,1)', fill: 'forwards' });
      a.onfinish = a.oncancel = function(){ el.classList.remove('is-live'); };
      anims.push(a);
    });
  });
  return function(){ anims.forEach(function(a){ a.cancel(); }); };
});
```

**Trap.** `@property` is what makes `--lm-n` animatable; without it the
number jumps. The counter renders integers only, so decimals, separators
and units live in `.lm-count-final` and appear at the end — a value like
`99.7%` is `data-lm-to="99"` with the final text carrying the rest. A
bracketed placeholder in `data-lm-to` fails `parseInt` and the static text
shows, which is the right thing for a template.

**Rule.** Three or four numbers a page, each with its label in the same
line. A count-up on a number nobody chose is decoration; on a number that
argues something it is emphasis.

## 21 · Odometer — `lm-odometer`

Digit wheels roll to the value, each a strip of ten moved by `--d`, staggered
by `--i`. The value is announced once by `aria-label`.

```html
<span class="lm-odometer lm-on" data-lm-value="2,847"></span>
```

```css
.lm-odometer{display:inline-flex;font-family:var(--lm-font-mono,monospace);font-variant-numeric:tabular-nums;font-size:2.4rem;font-weight:600;color:var(--lm-fg-bright,currentColor);line-height:1.15}
.lm-odo-digit{display:inline-block;height:1.15em;overflow:hidden}
.lm-odo-strip{display:block;transform:translateY(calc(var(--d,0)*-1.15em))}
.lm-odo-strip>span{display:block;height:1.15em}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-odometer:not(.is-in) .lm-odo-strip{transform:translateY(0)}
  .lm-odo-strip{transition:transform 1.4s var(--lm-ease,ease);transition-delay:calc(var(--i,0)*120ms)}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-odometer').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    var value = el.getAttribute('data-lm-value') || '';
    el.setAttribute('aria-label', value);
    var digits = 0;
    value.split('').forEach(function(ch){
      if(!/\d/.test(ch)){ var s = document.createElement('span'); s.textContent = ch; s.setAttribute('aria-hidden', 'true'); el.appendChild(s); return; }
      var d = document.createElement('span'); d.className = 'lm-odo-digit'; d.setAttribute('aria-hidden', 'true');
      var strip = document.createElement('span'); strip.className = 'lm-odo-strip';
      strip.style.setProperty('--d', ch); strip.style.setProperty('--i', digits++);
      for(var i = 0; i <= 9; i++){ var n = document.createElement('span'); n.textContent = i; strip.appendChild(n); }
      d.appendChild(strip); el.appendChild(d);
    });
  });
});
```

**Trap.** Row height and `line-height` are the same `1.15em`, and the
translate uses the same number: change one and the wheel lands between
digits. The strips are built once (`data-lm-ready`), so a value that changes
later needs the element rebuilt.

**Rule.** For a number that is the point of the screen. Next to a count-up
on the same page it looks like two ideas of the same thing.

---

# D. Cursor and hover — desktop only

Every pattern here gates on `(hover: hover) and (pointer: fine)` via
`lm.fine()` and does nothing on touch beyond what the markup already does.
Reduced motion switches the movement off but leaves colour changes.

## 22 · Spotlight border — `lm-spotlight`

A card's edge lights up where the pointer is. Registered properties make the
position transition smoothly; on focus the light sits in the centre.

```html
<a href="#" class="lm-spotlight lm-spot-card"><h3>Spotlight</h3><p>Move the pointer along the edge.</p></a>
```

```css
@property --lm-mx{syntax:"<length-percentage>";inherits:true;initial-value:50%}
@property --lm-my{syntax:"<length-percentage>";inherits:true;initial-value:50%}
.lm-spotlight{position:relative}
.lm-spotlight::after{content:"";position:absolute;inset:-1px;border-radius:inherit;padding:1px;background:radial-gradient(180px circle at var(--lm-mx) var(--lm-my),var(--lm-accent,currentColor),transparent 70%);-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:0;pointer-events:none}
.lm-spotlight:focus-visible::after{opacity:1}
@media (hover: hover) and (pointer: fine){.lm-spotlight:hover::after{opacity:1}}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-spotlight::after{transition:opacity var(--lm-dur-fast,.25s) ease,--lm-mx .08s linear,--lm-my .08s linear}
}
```

```js
lm.onActivate(function(scope){
  if(!lm.fine()) return;
  scope.querySelectorAll('.lm-spotlight').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    el.addEventListener('pointermove', function(e){
      var r = el.getBoundingClientRect();
      el.style.setProperty('--lm-mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--lm-my', (e.clientY - r.top) + 'px');
    });
  });
});
```

**Trap.** `inherits:true` is not optional: a pseudo-element reads its
originating element's custom properties by inheritance, and a
non-inheriting registered property hands it the initial value instead. The
ring is `::after`; a card that already draws a hover edge with `::before`
(`project-website`'s `.item-card`) keeps it, so switch one off.

**Rule.** Grids of equal cards. Never on a lone card — a spotlight with
nothing beside it is a torch.

## 23 · Tilt card — `lm-tilt`

The card rotates a few degrees toward the pointer.

```html
<div class="lm-tilt lm-spot-card"><h3>Tilt</h3><p>Rotates toward the pointer, then settles.</p></div>
```

```css
.lm-tilt{transform:perspective(700px) rotateX(var(--lm-rx,0deg)) rotateY(var(--lm-ry,0deg))}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-tilt{transition:transform .18s ease-out}
}
```

```js
lm.onActivate(function(scope){
  if(!lm.fine() || lm.reduced()) return;
  scope.querySelectorAll('.lm-tilt').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    el.addEventListener('pointermove', function(e){
      var r = el.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      el.style.setProperty('--lm-ry', (x * 10) + 'deg');
      el.style.setProperty('--lm-rx', (-y * 10) + 'deg');
    });
    el.addEventListener('pointerleave', function(){
      el.style.removeProperty('--lm-rx'); el.style.removeProperty('--lm-ry');
    });
  });
});
```

**Trap.** The whole `transform` is owned by this pattern; a card whose
hover already sets `transform` loses one of the two. Ten degrees is the
ceiling — beyond it text shears.

**Rule.** Cards with little text. A tilting paragraph is a reading test.

## 24 · Magnetic button — `lm-magnet`

The button drifts toward the pointer and snaps back. Uses the independent
`translate` property so it composes with the host's own `:active` transform.

```html
<button type="button" class="lm-magnet lm-btn">Get started</button>
```

```css
.lm-magnet{translate:var(--lm-tx,0px) var(--lm-ty,0px)}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-magnet{transition:translate .2s var(--lm-ease,ease)}
}
```

```js
lm.onActivate(function(scope){
  if(!lm.fine() || lm.reduced()) return;
  scope.querySelectorAll('.lm-magnet').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    el.addEventListener('pointermove', function(e){
      var r = el.getBoundingClientRect();
      el.style.setProperty('--lm-tx', ((e.clientX - r.left - r.width / 2) * .3) + 'px');
      el.style.setProperty('--lm-ty', ((e.clientY - r.top - r.height / 2) * .3) + 'px');
    });
    el.addEventListener('pointerleave', function(){
      el.style.removeProperty('--lm-tx'); el.style.removeProperty('--lm-ty');
    });
  });
});
```

**Trap.** The pull is 30% of the pointer's offset, measured inside the
button only, so it can never chase a pointer across the page.

**Rule.** The primary CTA and nothing else; two magnets on one screen fight.

## 25 · Cursor glow — `lm-glow`

A soft halo follows the pointer with a little lag. A single fixed element,
one `requestAnimationFrame` loop that stops when the page does.

```html
<div class="lm-glow" aria-hidden="true"></div>
```

```css
.lm-glow{display:none;position:fixed;left:0;top:0;width:480px;height:480px;margin:-240px 0 0 -240px;border-radius:50%;background:radial-gradient(circle,var(--lm-glow,transparent),transparent 65%);pointer-events:none;z-index:0;will-change:transform}
@media screen and (prefers-reduced-motion: no-preference) and (hover: hover) and (pointer: fine){
  .lm-glow.is-live{display:block}
}
```

```js
lm.onActivate(function(){
  var glow = document.querySelector('.lm-glow');
  if(!glow || !lm.fine() || lm.reduced()) return;
  var mx = -1000, my = -1000, gx = mx, gy = my, id = 0, on = false;
  function move(e){ mx = e.clientX; my = e.clientY; if(!on){ on = true; glow.classList.add('is-live'); id = requestAnimationFrame(tick); } }
  function tick(){
    gx += (mx - gx) * .12; gy += (my - gy) * .12;
    glow.style.transform = 'translate(' + gx.toFixed(1) + 'px,' + gy.toFixed(1) + 'px)';
    id = requestAnimationFrame(tick);
  }
  window.addEventListener('pointermove', move);
  return function(){ window.removeEventListener('pointermove', move); cancelAnimationFrame(id); glow.classList.remove('is-live'); };
});
```

**Trap.** The loop starts on the first pointer move, not on load, so a page
nobody touches runs nothing. The glow sits at `z-index:0` — content that
should be above it needs `position:relative`.

**Rule.** One per file, only on a dark ground, and only where the halo is
already part of the look (the hero's `--glow`). It is atmosphere, not a
cursor.

## 26 · Dock — `lm-dock`

Items magnify as the pointer nears, scaled from the bottom. Keyboard focus
magnifies the focused item.

```html
<nav class="lm-dock" aria-label="Sections">
  <a class="lm-dock-item" href="#/en/one"><span class="lm-dock-icon" aria-hidden="true">&#9650;</span><span class="lm-dock-label">One</span></a>
  <a class="lm-dock-item" href="#/en/one"><span class="lm-dock-icon" aria-hidden="true">&#9670;</span><span class="lm-dock-label">Two</span></a>
  <a class="lm-dock-item" href="#/en/one"><span class="lm-dock-icon" aria-hidden="true">&#9632;</span><span class="lm-dock-label">Three</span></a>
  <a class="lm-dock-item" href="#/en/one"><span class="lm-dock-icon" aria-hidden="true">&#9733;</span><span class="lm-dock-label">Four</span></a>
</nav>
```

```css
.lm-dock{display:inline-flex;align-items:flex-end;gap:6px;padding:8px 10px;border:1px solid var(--lm-border,currentColor);border-radius:calc(var(--lm-radius,14px) + 6px);background:var(--lm-surface,transparent)}
.lm-dock-item{display:flex;flex-direction:column;align-items:center;gap:4px;width:48px;color:var(--lm-fg-dim,currentColor);text-decoration:none;font-size:10px;transform-origin:50% 100%;transform:scale(var(--lm-s,1))}
.lm-dock-icon{width:36px;height:36px;display:grid;place-items:center;border-radius:10px;background:var(--lm-surface-2,transparent);border:1px solid var(--lm-border,currentColor);color:var(--lm-accent,currentColor);font-size:16px}
.lm-dock-item:focus-visible{--lm-s:1.3}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-dock-item{transition:transform .2s var(--lm-ease,ease)}
}
```

```js
lm.onActivate(function(scope){
  if(!lm.fine() || lm.reduced()) return;
  scope.querySelectorAll('.lm-dock').forEach(function(dock){
    if(dock.getAttribute('data-lm-ready')) return;
    dock.setAttribute('data-lm-ready', '1');
    var items = dock.querySelectorAll('.lm-dock-item');
    dock.addEventListener('pointermove', function(e){
      items.forEach(function(it){
        var r = it.getBoundingClientRect(), d = Math.abs(e.clientX - (r.left + r.width / 2));
        it.style.setProperty('--lm-s', (1 + .5 * Math.max(0, 1 - d / 120)).toFixed(3));
      });
    });
    dock.addEventListener('pointerleave', function(){ items.forEach(function(it){ it.style.removeProperty('--lm-s'); }); });
  });
});
```

**Trap.** Scaling from the bottom edge instead of resizing the box is what
keeps neighbours from shuffling — the source demo animates `width`, which
reflows the whole dock every frame.

**Rule.** Four to seven items, icon plus a one-word label. It is a nav, so
every item is an `<a href>` that goes somewhere.

## 27 · Repel grid — `lm-repel`

A decorative field of tiles pushes away from the pointer. Loops only while
the pointer is inside; the tile positions are cached on entry.

```html
<div class="lm-repel" aria-hidden="true" data-lm-cols="12" data-lm-rows="5"></div>
```

```css
.lm-repel{display:grid;grid-template-columns:repeat(var(--lm-cols,12),1fr);gap:8px;max-width:520px}
.lm-repel i{display:block;aspect-ratio:1;border-radius:6px;background:var(--lm-surface-2,transparent);border:1px solid var(--lm-border,currentColor)}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-repel i{transition:transform .4s var(--lm-ease,ease)}
}
```

```js
lm.onActivate(function(scope){
  var stops = [];
  scope.querySelectorAll('.lm-repel').forEach(function(grid){
    if(!grid.children.length){
      var cols = parseInt(grid.getAttribute('data-lm-cols'), 10) || 12, rows = parseInt(grid.getAttribute('data-lm-rows'), 10) || 5;
      grid.style.setProperty('--lm-cols', cols);
      for(var i = 0; i < cols * rows; i++) grid.appendChild(document.createElement('i'));
    }
    if(!lm.fine() || lm.reduced()) return;
    var tiles = grid.children, centres = [], mx = 0, my = 0, id = 0;
    function enter(){
      centres = Array.prototype.map.call(tiles, function(t){ var r = t.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; });
      cancelAnimationFrame(id); id = requestAnimationFrame(tick);
    }
    function move(e){ mx = e.clientX; my = e.clientY; }
    function tick(){
      for(var i = 0; i < tiles.length; i++){
        var dx = centres[i][0] - mx, dy = centres[i][1] - my, d = Math.hypot(dx, dy);
        tiles[i].style.transform = d < 110 ? 'translate(' + (dx / d * (1 - d / 110) * 16).toFixed(1) + 'px,' + (dy / d * (1 - d / 110) * 16).toFixed(1) + 'px)' : '';
      }
      id = requestAnimationFrame(tick);
    }
    function leave(){ cancelAnimationFrame(id); Array.prototype.forEach.call(tiles, function(t){ t.style.transform = ''; }); }
    grid.addEventListener('pointerenter', enter); grid.addEventListener('pointermove', move); grid.addEventListener('pointerleave', leave);
    stops.push(function(){ leave(); grid.removeEventListener('pointerenter', enter); grid.removeEventListener('pointermove', move); grid.removeEventListener('pointerleave', leave); });
  });
  return function(){ stops.forEach(function(s){ s(); }); };
});
```

**Trap.** Reading `getBoundingClientRect` for sixty tiles every frame is
the layout thrash this file forbids; the rects are read once on
`pointerenter` and again only when the pointer re-enters, so a resize
mid-hover is off by a few pixels until the next entry — acceptable for a
decoration.

**Rule.** It is `aria-hidden` and carries no content. Sixty tiles at most.

## 28 · Image trail — `lm-trail`

Tiles appear along the pointer's path and fade. A pool of twelve elements
recycled with WAAPI; nothing is created per move.

```html
<div class="lm-trail" style="min-height:220px;display:grid;place-items:center"><h3>Move the pointer here</h3></div>
```

```css
.lm-trail{position:relative;overflow:hidden;border-radius:var(--lm-radius,0);border:1px solid var(--lm-border,currentColor)}
.lm-trail-tile{position:absolute;width:96px;height:120px;border-radius:10px;background:var(--lm-surface-2,transparent);border:1px solid var(--lm-border,currentColor);opacity:0;pointer-events:none}
.lm-trail-tile:nth-child(3n){background:var(--lm-glow,transparent)}
.lm-trail-tile:nth-child(3n+1){background:var(--lm-accent,transparent);opacity:0}
```

```js
lm.onActivate(function(scope){
  var stops = [];
  scope.querySelectorAll('.lm-trail').forEach(function(area){
    if(!lm.fine() || lm.reduced()) return;
    var pool = [], idx = 0, lx = 0, ly = 0, live = [];
    for(var i = 0; i < 12; i++){ var t = document.createElement('span'); t.className = 'lm-trail-tile'; t.setAttribute('aria-hidden', 'true'); area.appendChild(t); pool.push(t); }
    function move(e){
      var r = area.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
      if(Math.hypot(x - lx, y - ly) < 64) return;
      lx = x; ly = y;
      var t = pool[idx++ % pool.length];
      t.style.left = (x - 48) + 'px'; t.style.top = (y - 60) + 'px';
      var a = t.animate([{ opacity: .9, transform: 'scale(.8) rotate(-6deg)' }, { opacity: 0, transform: 'scale(.6) rotate(6deg)' }], { duration: 900, easing: 'ease-out' });
      live.push(a);
    }
    area.addEventListener('pointermove', move);
    stops.push(function(){ area.removeEventListener('pointermove', move); live.forEach(function(a){ a.cancel(); }); pool.forEach(function(t){ t.remove(); }); });
  });
  return function(){ stops.forEach(function(s){ s(); }); };
});
```

**Trap.** The tiles are appended inside the area (`overflow:hidden`), not
`position:fixed` on the body as the source demo does, so they can never
trail off over the nav. Supply images by setting `background-image` on
`.lm-trail-tile` in the host file; the pattern ships colour tiles.

**Rule.** A portfolio or gallery hero. Touch readers get the heading and
nothing else, so the heading has to carry the page.

## 29 · Accordion strips — `lm-accordion`

Strips widen on hover, focus, or click. The one pattern here that animates
`flex-grow` — layout — so the accordion is `contain: layout` and reflows
nothing outside itself.

```html
<div class="lm-accordion">
  <section class="lm-acc-panel is-open"><button type="button" class="lm-acc-head" aria-expanded="true">Strategy</button><div class="lm-acc-body"><p>Positioning, messaging, identity.</p></div></section>
  <section class="lm-acc-panel"><button type="button" class="lm-acc-head" aria-expanded="false">Design</button><div class="lm-acc-body"><p>Components, layouts, motion.</p></div></section>
  <section class="lm-acc-panel"><button type="button" class="lm-acc-head" aria-expanded="false">Build</button><div class="lm-acc-body"><p>Production code from the first commit.</p></div></section>
</div>
```

```css
.lm-accordion{display:flex;gap:8px;height:clamp(220px,40vh,360px);contain:layout}
.lm-acc-panel{position:relative;flex:1 1 0;min-width:0;overflow:hidden;border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0);background:var(--lm-surface,transparent)}
.lm-acc-panel.is-open{flex-grow:4}
.lm-acc-head{position:absolute;inset:0;width:100%;border:0;background:transparent;color:var(--lm-fg-bright,currentColor);font:inherit;font-weight:600;text-align:left;padding:20px;cursor:pointer;writing-mode:vertical-rl}
.lm-acc-panel.is-open .lm-acc-head{writing-mode:horizontal-tb;align-self:start;height:auto;inset:auto 0 auto 0}
.lm-acc-body{position:absolute;left:0;right:0;bottom:0;padding:20px;opacity:0;color:var(--lm-fg-dim,currentColor)}
.lm-acc-body p{margin:0}
.lm-acc-panel.is-open .lm-acc-body{opacity:1}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-acc-panel{transition:flex-grow .6s var(--lm-ease,ease)}
  .lm-acc-body{transition:opacity .4s ease .15s}
  @media (hover: hover) and (pointer: fine){.lm-acc-panel:hover{flex-grow:4}.lm-acc-panel:hover .lm-acc-body{opacity:1}}
}
@media (max-width:640px){.lm-accordion{flex-direction:column;height:auto}.lm-acc-panel{min-height:56px}.lm-acc-panel.is-open{min-height:200px}.lm-acc-head{writing-mode:horizontal-tb}}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-accordion').forEach(function(acc){
    if(acc.getAttribute('data-lm-ready')) return;
    acc.setAttribute('data-lm-ready', '1');
    acc.addEventListener('click', function(e){
      var head = e.target.closest('.lm-acc-head'); if(!head) return;
      acc.querySelectorAll('.lm-acc-panel').forEach(function(p){
        var on = p.contains(head);
        p.classList.toggle('is-open', on);
        p.querySelector('.lm-acc-head').setAttribute('aria-expanded', String(on));
      });
    });
  });
});
```

**Trap.** Hover opens a strip only on a fine pointer; click and keyboard
open it everywhere and are the state the page remembers. The body text is
absolutely positioned so the strip's own width change moves nothing in the
document — `contain:layout` guarantees it.

**Rule.** Three to five strips, a title each. It is a picker, not a place
to put the paragraph the reader needs.

## 30 · Before/after compare — `lm-compare`

A wipe between two layers, driven by an `<input type="range">` laid over
the image. Drag, touch, and arrow keys all work and none of them need code.

```html
<div class="lm-compare" style="--lm-pos:50%">
  <div class="lm-compare-layer lm-compare-after"><span>After</span></div>
  <div class="lm-compare-layer lm-compare-before"><span>Before</span></div>
  <span class="lm-compare-line" aria-hidden="true"></span>
  <input class="lm-compare-range" type="range" min="0" max="100" value="50" aria-label="Reveal the after image">
</div>
```

```css
.lm-compare{position:relative;aspect-ratio:16/9;overflow:hidden;border-radius:var(--lm-radius,0);border:1px solid var(--lm-border,currentColor)}
.lm-compare-layer{position:absolute;inset:0;font-weight:600;font-size:.85rem;letter-spacing:.08em;text-transform:uppercase}
.lm-compare-layer span{position:absolute;bottom:14px}
.lm-compare-before span{left:16px}
.lm-compare-after span{right:16px}
.lm-compare-after{background:var(--lm-surface-2,transparent);color:var(--lm-accent,currentColor)}
.lm-compare-before{background:var(--lm-surface,transparent);color:var(--lm-fg-dim,currentColor);clip-path:inset(0 calc(100% - var(--lm-pos,50%)) 0 0)}
.lm-compare-line{position:absolute;top:0;bottom:0;left:var(--lm-pos,50%);width:2px;margin-left:-1px;background:var(--lm-fg-bright,currentColor);pointer-events:none}
.lm-compare-line::after{content:"";position:absolute;top:50%;left:50%;width:36px;height:36px;margin:-18px 0 0 -18px;border-radius:50%;background:var(--lm-fg-bright,currentColor);box-shadow:0 2px 12px rgba(0,0,0,.35)}
.lm-compare-range{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0;cursor:ew-resize}
.lm-compare-range:focus-visible~.lm-compare-line{outline:2px solid var(--lm-accent,currentColor)}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-compare').forEach(function(box){
    var range = box.querySelector('.lm-compare-range');
    if(!range || range.getAttribute('data-lm-ready')) return;
    range.setAttribute('data-lm-ready', '1');
    range.addEventListener('input', function(){ box.style.setProperty('--lm-pos', range.value + '%'); });
  });
});
```

**Trap.** The range is invisible but real: it is what receives the drag,
the tap, and the keys, and it keeps its focus ring on the divider. The two
labels sit in opposite corners, never centred — centred labels meet under
the handle at 50%, which is where the divider starts. Do not
replace it with pointer maths — the source demo's four listeners are what
the input already does. Replace the two coloured layers with images by
putting an `<img>` inside each layer.

**Rule.** The line starts in the middle so both states are visible at once;
a reader should never have to move it to know there are two.

## 31 · Spot reveal — `lm-spot`

A circle around the pointer reveals the second layer; a button toggles the
whole reveal for touch and keyboard.

```html
<div class="lm-spot">
  <div class="lm-spot-layer lm-spot-base"><span>Base</span></div>
  <div class="lm-spot-layer lm-spot-top"><span>Revealed</span></div>
  <button type="button" class="lm-spot-btn" aria-pressed="false">Reveal all</button>
</div>
```

```css
.lm-spot{position:relative;aspect-ratio:16/9;overflow:hidden;border-radius:var(--lm-radius,0);border:1px solid var(--lm-border,currentColor);--lm-r:0px}
.lm-spot-layer{position:absolute;inset:0;display:grid;place-items:center;font-weight:600;font-size:1.4rem}
.lm-spot-base{background:var(--lm-surface,transparent);color:var(--lm-fg-dim,currentColor)}
.lm-spot-top{background:var(--lm-surface-2,transparent);color:var(--lm-accent,currentColor);clip-path:circle(var(--lm-r) at var(--lm-mx,50%) var(--lm-my,50%))}
.lm-spot.is-open{--lm-r:150%}
.lm-spot-btn{position:absolute;right:12px;bottom:12px;height:34px;padding:0 12px;border-radius:999px;border:1px solid var(--lm-border,currentColor);background:var(--lm-surface,transparent);color:var(--lm-fg,currentColor);font:inherit;font-size:.85rem;cursor:pointer}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-spot.is-open .lm-spot-top{transition:clip-path .6s var(--lm-ease,ease)}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-spot').forEach(function(box){
    if(box.getAttribute('data-lm-ready')) return;
    box.setAttribute('data-lm-ready', '1');
    var btn = box.querySelector('.lm-spot-btn');
    if(btn) btn.addEventListener('click', function(){ var on = box.classList.toggle('is-open'); btn.setAttribute('aria-pressed', String(on)); });
    if(!lm.fine()) return;
    box.addEventListener('pointermove', function(e){
      if(box.classList.contains('is-open')) return;
      var r = box.getBoundingClientRect();
      box.style.setProperty('--lm-mx', (e.clientX - r.left) + 'px'); box.style.setProperty('--lm-my', (e.clientY - r.top) + 'px'); box.style.setProperty('--lm-r', '90px');
    });
    box.addEventListener('pointerleave', function(){ box.style.removeProperty('--lm-r'); });
  });
});
```

**Trap.** The button is the only reason a touch reader can see the second
layer at all — it is not optional. The `clip-path` transition is enabled
only for the button's full reveal; a transitioning circle lags the pointer.

**Rule.** Two states of one thing. If the layers are different things, use
two images side by side.

---

# E. Click and tap

## 32 · Ripple — `lm-ripple`

A wave from the point of contact. One WAAPI animation per press, removed on
finish; keyboard presses ripple from the centre.

```html
<button type="button" class="lm-ripple lm-btn">Press me</button>
```

```css
.lm-ripple{position:relative;overflow:hidden}
.lm-ripple-wave{position:absolute;border-radius:50%;background:currentColor;opacity:0;pointer-events:none;transform:scale(0)}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-ripple').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    function wave(x, y){
      if(lm.reduced()) return;
      var r = el.getBoundingClientRect(), s = Math.max(r.width, r.height) * 2;
      var w = document.createElement('span'); w.className = 'lm-ripple-wave';
      w.style.width = w.style.height = s + 'px'; w.style.left = (x - s / 2) + 'px'; w.style.top = (y - s / 2) + 'px';
      el.appendChild(w);
      w.animate([{ transform: 'scale(0)', opacity: .35 }, { transform: 'scale(1)', opacity: 0 }], { duration: 600, easing: 'ease-out' }).onfinish = function(){ w.remove(); };
    }
    el.addEventListener('pointerdown', function(e){ var r = el.getBoundingClientRect(); wave(e.clientX - r.left, e.clientY - r.top); });
    el.addEventListener('keydown', function(e){ if(e.key === 'Enter' || e.key === ' ') wave(el.clientWidth / 2, el.clientHeight / 2); });
  });
});
```

**Trap.** `overflow:hidden` on the button clips the wave; a button whose
focus ring is drawn inside the box loses it — this file draws rings with
`outline`, which is outside.

**Rule.** Buttons and tappable cards. Never on links that navigate away —
the wave is cut off by the route change and reads as a glitch.

## 33 · Burst — `lm-burst`

Particles fly out of a button on click, each its own WAAPI animation, all
removed when they finish and cancelled if the page leaves.

```html
<button type="button" class="lm-burst lm-btn">Confirm</button>
```

```css
.lm-burst{position:relative}
.lm-burst-p{position:absolute;left:50%;top:50%;width:7px;height:7px;margin:-3px 0 0 -3px;border-radius:50%;background:var(--lm-accent,currentColor);pointer-events:none;opacity:0}
```

```js
lm.onActivate(function(scope){
  var live = [];
  scope.querySelectorAll('.lm-burst').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    el.addEventListener('click', function(){
      if(lm.reduced()) return;
      for(var i = 0; i < 16; i++){
        var p = document.createElement('span'); p.className = 'lm-burst-p'; el.appendChild(p);
        var a = (i / 16) * Math.PI * 2, d = 40 + Math.random() * 50;
        var an = p.animate([{ translate: '0 0', scale: '1', opacity: 1 }, { translate: Math.cos(a) * d + 'px ' + (Math.sin(a) * d - 30) + 'px', scale: '0', opacity: 0 }], { duration: 650, easing: 'cubic-bezier(.16,1,.3,1)' });
        an.onfinish = (function(p){ return function(){ p.remove(); }; })(p);
        live.push(an);
      }
    });
  });
  return function(){ live.forEach(function(a){ a.cancel(); }); document.querySelectorAll('.lm-burst-p').forEach(function(p){ p.remove(); }); };
});
```

**Trap.** Particles are children of the button, so a button with
`overflow:hidden` (a ripple button) clips them. The independent `translate`
and `scale` properties are animated, not `transform`, so nothing the host
sets on `transform` is overridden.

**Rule.** The one action that completes something — submit, confirm. Not
on every button.

## 34 · Flip card — `lm-flip`

A card turns over on hover, focus, or press. The face that is turned away is
`aria-hidden`, and the button's `aria-pressed` carries the state.

```html
<button type="button" class="lm-flip" aria-pressed="false">
  <span class="lm-flip-inner">
    <span class="lm-flip-face lm-flip-front"><strong>Front</strong><span>Hover, focus, or press.</span></span>
    <span class="lm-flip-face lm-flip-back" aria-hidden="true"><strong>Back</strong><span>The detail lives here.</span></span>
  </span>
</button>
```

```css
.lm-flip{display:block;width:100%;min-height:180px;padding:0;border:0;background:transparent;color:inherit;font:inherit;text-align:left;perspective:800px;cursor:pointer}
.lm-flip-inner{position:relative;display:block;width:100%;height:100%;min-height:inherit;transform-style:preserve-3d}
.lm-flip[aria-pressed="true"] .lm-flip-inner{transform:rotateY(180deg)}
.lm-flip-face{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;padding:22px;border-radius:var(--lm-radius,0);border:1px solid var(--lm-border,currentColor);background:var(--lm-surface,transparent);backface-visibility:hidden}
.lm-flip-back{transform:rotateY(180deg);background:var(--lm-accent,transparent);color:var(--lm-surface,currentColor);border-color:transparent}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-flip-inner{transition:transform .6s var(--lm-ease,ease)}
  @media (hover: hover) and (pointer: fine){.lm-flip:hover .lm-flip-inner{transform:rotateY(180deg)}}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-flip').forEach(function(el){
    if(el.getAttribute('data-lm-ready')) return;
    el.setAttribute('data-lm-ready', '1');
    el.addEventListener('click', function(){
      var on = el.getAttribute('aria-pressed') !== 'true';
      el.setAttribute('aria-pressed', String(on));
      el.querySelector('.lm-flip-front').setAttribute('aria-hidden', String(on));
      el.querySelector('.lm-flip-back').setAttribute('aria-hidden', String(!on));
    });
  });
});
```

**Trap.** Both faces are absolutely positioned, so the button's
`min-height` is the card's height — content taller than it is cut off.
Hover flips only on a fine pointer and does not change `aria-pressed`;
pressing does, and that state is the one that persists.

**Rule.** The front is a teaser, the back is the detail, and nothing on
the back is essential: a reader who never flips must still be served.

## 35 · Coverflow — `lm-coverflow`

The current item faces the reader, neighbours angle away. Position comes
from `--lm-o` (offset from current) so the CSS is one rule. Buttons, arrow
keys, and a swipe all move it.

```html
<div class="lm-coverflow" role="region" aria-roledescription="carousel" aria-label="Work" tabindex="0">
  <ul class="lm-cf-track">
    <li class="lm-cf-item"><h3>Brand</h3><p>Identity system</p></li>
    <li class="lm-cf-item"><h3>Website</h3><p>Responsive, fast</p></li>
    <li class="lm-cf-item"><h3>App</h3><p>iOS and Android</p></li>
    <li class="lm-cf-item"><h3>Dashboard</h3><p>Real-time</p></li>
    <li class="lm-cf-item"><h3>Platform</h3><p>Multi-tenant</p></li>
  </ul>
  <div class="lm-cf-nav">
    <button type="button" class="lm-track-btn" data-lm-cf="-1" aria-label="Previous">&larr;</button>
    <button type="button" class="lm-track-btn" data-lm-cf="1" aria-label="Next">&rarr;</button>
  </div>
</div>
```

```css
.lm-coverflow{overflow:hidden;touch-action:pan-y}
.lm-cf-track{position:relative;height:260px;margin:0;padding:0;list-style:none;perspective:1200px;transform-style:preserve-3d}
.lm-cf-item{position:absolute;left:50%;top:50%;width:min(60%,260px);height:200px;margin:-100px 0 0 min(-30%,-130px);display:flex;flex-direction:column;justify-content:flex-end;padding:22px;border-radius:var(--lm-radius,0);border:1px solid var(--lm-border,currentColor);background:var(--lm-surface-2,transparent);transform:translateX(calc(var(--lm-o,0)*58%)) translateZ(calc(var(--lm-ao,0)*-140px)) rotateY(calc(var(--lm-o,0)*-32deg));opacity:calc(1 - var(--lm-ao,0)*.3);z-index:calc(10 - var(--lm-ao,0))}
.lm-cf-item[aria-hidden="true"]{pointer-events:none}
.lm-cf-item h3{margin:0}
.lm-cf-item p{margin:4px 0 0;color:var(--lm-fg-dim,currentColor)}
.lm-cf-nav{display:flex;justify-content:center;gap:8px;margin-top:8px}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-cf-item{transition:transform .6s var(--lm-ease,ease),opacity .6s var(--lm-ease,ease)}
}
@media print{.lm-cf-track{height:auto;display:flex;flex-wrap:wrap;gap:12px;perspective:none}.lm-cf-item{position:static;margin:0;transform:none;opacity:1}}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-coverflow').forEach(function(root){
    if(root.getAttribute('data-lm-ready')) return;
    root.setAttribute('data-lm-ready', '1');
    var items = root.querySelectorAll('.lm-cf-item'), cur = Math.floor(items.length / 2), sx = null;
    function render(){
      items.forEach(function(it, i){
        var o = i - cur, ao = Math.abs(o);
        it.style.setProperty('--lm-o', o); it.style.setProperty('--lm-ao', ao);
        it.style.visibility = ao > 2 ? 'hidden' : '';
        it.setAttribute('aria-hidden', String(o !== 0));
        if(o === 0) it.setAttribute('aria-current', 'true'); else it.removeAttribute('aria-current');
      });
    }
    function move(d){ cur = Math.max(0, Math.min(items.length - 1, cur + d)); render(); }
    root.querySelectorAll('[data-lm-cf]').forEach(function(b){ b.addEventListener('click', function(){ move(parseInt(b.getAttribute('data-lm-cf'), 10)); }); });
    items.forEach(function(it, i){ it.addEventListener('click', function(){ cur = i; render(); }); });
    root.addEventListener('keydown', function(e){ if(e.key === 'ArrowLeft'){ move(-1); e.preventDefault(); } if(e.key === 'ArrowRight'){ move(1); e.preventDefault(); } });
    root.addEventListener('pointerdown', function(e){ sx = e.clientX; });
    root.addEventListener('pointerup', function(e){ if(sx !== null && Math.abs(e.clientX - sx) > 40) move(e.clientX < sx ? 1 : -1); sx = null; });
    render();
  });
});
```

**Trap.** Only the current item is exposed to assistive tech; the rest are
`aria-hidden` and un-clickable, which is why the buttons are the primary
control. `--lm-ao` is set by the script rather than computed with `abs()`
in CSS, which not every engine has yet.

**Rule.** Five to nine items with a title and one line each. It is a
picker: clicking the current item should open something.

## 36 · Island — `lm-island`

A pill that expands into a panel. Fixed, so its layout change reflows
nothing else — the second and last layout exception in this file.

```html
<div class="lm-island">
  <button type="button" class="lm-island-btn" aria-expanded="false" aria-controls="lm-island-panel-1"><span class="lm-island-dot" aria-hidden="true"></span><span>3 updates</span></button>
  <div class="lm-island-panel" id="lm-island-panel-1">
    <div class="lm-island-body">
      <p>Deploy succeeded.</p><p>Two reviews waiting.</p><p>Latency back to normal.</p>
    </div>
  </div>
</div>
```

```css
.lm-island{position:fixed;top:12px;left:50%;translate:-50% 0;z-index:60;width:max-content;max-width:min(320px,calc(100vw - 32px));border:1px solid var(--lm-border,currentColor);border-radius:24px;background:var(--lm-surface,transparent);box-shadow:0 12px 32px -12px rgba(0,0,0,.5);overflow:hidden}
.lm-island-btn{display:flex;align-items:center;gap:10px;width:100%;height:40px;padding:0 16px;border:0;background:transparent;color:var(--lm-fg,currentColor);font:inherit;font-size:.85rem;cursor:pointer}
.lm-island-dot{width:8px;height:8px;border-radius:50%;background:var(--lm-accent,currentColor)}
.lm-island-panel{display:grid;grid-template-rows:0fr}
.lm-island-body{min-height:0;overflow:hidden;padding:0 16px;color:var(--lm-fg-dim,currentColor);font-size:.85rem}
.lm-island-body p{margin:0 0 10px}
.lm-island.is-open{border-radius:16px;width:320px}
.lm-island.is-open .lm-island-panel{grid-template-rows:1fr}
.lm-island.is-open .lm-island-body{padding-top:4px}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-island{transition:border-radius .4s var(--lm-ease,ease),width .4s var(--lm-ease,ease)}
  .lm-island-panel{transition:grid-template-rows .4s var(--lm-ease,ease)}
  .lm-island-dot{animation:lm-breathe 2s ease-in-out infinite}
  @keyframes lm-breathe{50%{opacity:.5}}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-island').forEach(function(isl){
    if(isl.getAttribute('data-lm-ready')) return;
    isl.setAttribute('data-lm-ready', '1');
    var btn = isl.querySelector('.lm-island-btn');
    function set(on){ isl.classList.toggle('is-open', on); btn.setAttribute('aria-expanded', String(on)); }
    btn.addEventListener('click', function(){ set(!isl.classList.contains('is-open')); });
    document.addEventListener('click', function(e){ if(!isl.contains(e.target)) set(false); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') set(false); });
  });
});
```

**Trap.** `grid-template-rows: 0fr → 1fr` is the height animation that
needs no measured height; it works because the body has `min-height:0`.
The island is `position:fixed` inside a `.page`, so it is hidden with the
page — put it outside the pages to keep it on every route.

**Rule.** Status, not navigation. One island, three lines at most.

## 37 · Morph — `lm-morph`

A control changes shape into a panel using the View Transitions API where
it exists, and a plain class toggle where it does not.

```html
<div class="lm-morph">
  <button type="button" class="lm-morph-btn" aria-expanded="false">Recent activity</button>
  <div class="lm-morph-panel"><p>Three things happened while you were away.</p><button type="button" class="lm-morph-close">Close</button></div>
</div>
```

```css
.lm-morph{display:inline-block;view-transition-name:lm-morph;border:1px solid var(--lm-border,currentColor);border-radius:999px;background:var(--lm-surface,transparent);overflow:hidden}
.lm-morph-btn,.lm-morph-close{border:0;background:transparent;color:var(--lm-fg,currentColor);font:inherit;padding:10px 18px;cursor:pointer}
.lm-morph-panel{display:none;padding:0 18px 12px;max-width:320px;color:var(--lm-fg-dim,currentColor)}
.lm-morph.is-open{border-radius:var(--lm-radius,0)}
.lm-morph.is-open .lm-morph-panel{display:block}
@media screen and (prefers-reduced-motion: reduce){
  ::view-transition-group(*),::view-transition-old(*),::view-transition-new(*){animation:none!important}
}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-morph').forEach(function(m){
    if(m.getAttribute('data-lm-ready')) return;
    m.setAttribute('data-lm-ready', '1');
    var btn = m.querySelector('.lm-morph-btn');
    function set(on){
      var apply = function(){ m.classList.toggle('is-open', on); btn.setAttribute('aria-expanded', String(on)); };
      if(document.startViewTransition && !lm.reduced()) document.startViewTransition(apply); else apply();
    }
    btn.addEventListener('click', function(){ set(true); });
    m.querySelector('.lm-morph-close').addEventListener('click', function(){ set(false); btn.focus(); });
  });
});
```

**Trap.** A `view-transition-name` must be unique among *rendered*
elements: two open morphs on one page abort the transition. The API
snapshots the page, so the class flip is the only thing inside the callback.

**Rule.** A pill that becomes a panel, a button that becomes a form. Not
route changes — the hash router already has its own way of showing a page.

## 38 · Drag to pan — `lm-pan`

A board bigger than its frame, dragged with pointer capture or moved with
the arrow keys.

```html
<div class="lm-pan" tabindex="0" role="group" aria-label="Board — drag or use the arrow keys">
  <div class="lm-pan-canvas">
    <div class="lm-pan-item" style="--x:-40%;--y:-30%">Branding</div>
    <div class="lm-pan-item" style="--x:10%;--y:-45%">Motion</div>
    <div class="lm-pan-item" style="--x:-15%;--y:20%">Type</div>
    <div class="lm-pan-item" style="--x:35%;--y:15%">Print</div>
  </div>
</div>
```

```css
.lm-pan{position:relative;height:300px;overflow:hidden;border:1px solid var(--lm-border,currentColor);border-radius:var(--lm-radius,0);background:var(--lm-surface,transparent);cursor:grab;touch-action:none}
.lm-pan:active{cursor:grabbing}
.lm-pan-canvas{position:absolute;left:50%;top:50%;translate:var(--lm-px,0px) var(--lm-py,0px)}
.lm-pan-item{position:absolute;left:calc(var(--x,0)*4);top:calc(var(--y,0)*3);width:180px;height:120px;margin:-60px 0 0 -90px;display:flex;align-items:flex-end;padding:16px;border:1px solid var(--lm-border,currentColor);border-radius:12px;background:var(--lm-surface-2,transparent);font-weight:600;user-select:none}
```

```js
lm.onActivate(function(scope){
  scope.querySelectorAll('.lm-pan').forEach(function(pan){
    if(pan.getAttribute('data-lm-ready')) return;
    pan.setAttribute('data-lm-ready', '1');
    var x = 0, y = 0, sx = 0, sy = 0, drag = false, LIM = 360;
    function set(nx, ny){ x = Math.max(-LIM, Math.min(LIM, nx)); y = Math.max(-LIM, Math.min(LIM, ny)); pan.style.setProperty('--lm-px', x + 'px'); pan.style.setProperty('--lm-py', y + 'px'); }
    pan.addEventListener('pointerdown', function(e){ drag = true; sx = e.clientX - x; sy = e.clientY - y; pan.setPointerCapture(e.pointerId); });
    pan.addEventListener('pointermove', function(e){ if(drag) set(e.clientX - sx, e.clientY - sy); });
    pan.addEventListener('pointerup', function(){ drag = false; });
    pan.addEventListener('pointercancel', function(){ drag = false; });
    pan.addEventListener('keydown', function(e){
      var k = { ArrowLeft:[40,0], ArrowRight:[-40,0], ArrowUp:[0,40], ArrowDown:[0,-40] }[e.key];
      if(k){ set(x + k[0], y + k[1]); e.preventDefault(); }
    });
  });
});
```

**Trap.** Pointer capture means no `window` listeners and nothing to
remove on deactivation. `touch-action:none` is what lets a touch drag the
board instead of the page — and is why the board is never taller than a
phone screen.

**Rule.** Moodboards and maps. Anything with an order belongs in a list.

---

# F. Ambient

## 39 · Mesh gradient — `lm-mesh`

Three blurred blobs drifting behind a section. Pure CSS; still under
reduced motion.

```html
<div style="position:relative;min-height:240px;display:grid;place-items:center;overflow:hidden;border-radius:var(--lm-radius,0)">
  <div class="lm-mesh" aria-hidden="true"><i></i><i></i><i></i></div>
  <h3 style="position:relative">Content sits on top</h3>
</div>
```

```css
.lm-mesh{position:absolute;inset:0;overflow:hidden;pointer-events:none}
.lm-mesh i{position:absolute;width:55%;aspect-ratio:1;border-radius:50%;filter:blur(60px);opacity:.55}
.lm-mesh i:nth-child(1){left:-10%;top:-20%;background:var(--lm-accent,transparent)}
.lm-mesh i:nth-child(2){right:-15%;top:10%;background:var(--lm-accent-2,transparent)}
.lm-mesh i:nth-child(3){left:25%;bottom:-40%;background:var(--lm-glow,transparent)}
@media screen and (prefers-reduced-motion: no-preference){
  .lm-mesh i{animation:lm-mesh 18s ease-in-out infinite alternate}
  .lm-mesh i:nth-child(2){animation-duration:22s;animation-delay:-6s}
  .lm-mesh i:nth-child(3){animation-duration:26s;animation-delay:-12s}
  @keyframes lm-mesh{to{transform:translate(18%,12%) scale(1.15)}}
}
```

**Trap.** `filter:blur()` on three large elements is the most expensive
paint in this file; keep the section small and never stack two meshes. The
parent needs `overflow:hidden` and `position:relative`, and the content
above it `position:relative` so it paints on top.

**Rule.** One hero or one closing band. On a light theme drop the opacity
to `.35` — measure the text contrast against the blob, not the ground.

---

## Applying a pattern to a hash-routed file

`project-website` (and `web-document`, `sitemap-ia`) toggles `.page.active`
in `apply()` on every `hashchange`. The runtime listens to the same event
one registration later and reads `.page.active`, so:

- the runtime `<script>` goes **after** the router's block, never inside it;
- pattern hooks receive the active page as `scope` and query inside it;
- a pattern outside every page (a fixed island, the footer) is queried
  from `document` by the hook instead;
- the footer's `lm-reveal` elements are armed once by `revealLoose()`
  without any extra call.

The file's own `.reveal`/`armReveal()` mechanism keeps working beside this
one. Do not convert existing `.reveal` elements — add `lm-*` where a pattern
is wanted and leave the rest.

The self-download in `project-website` clones the document with its
transient `.in` classes stripped. A file that adds `lm-*` patterns strips
its own transient state at that moment too — `.is-in`, `.is-done`, and the
`data-lm-ready` / `data-lm-done` flags that would otherwise stop the saved
copy from wiring its patterns up again. A capture-phase click listener on
`#btnHtml` removes them before the router's handler clones, and restores
them in the same task, so no frame ever renders without them and nothing on
screen changes. The motion-website template carries this block; copy it
verbatim into any file that has both the self-download and `lm-*` patterns.

```html
<script>
/* lm — the saved copy must open the way the original does. The router's
   download handler clones the DOM on click; this capture-phase listener
   runs first, strips the motion state, and puts it back in the same task. */
document.addEventListener('click', function(e){
  if(!e.target.closest('#btnHtml')) return;
  var undo = [];
  document.querySelectorAll('.is-in, .is-done').forEach(function(el){
    ['is-in', 'is-done'].forEach(function(k){
      if(el.classList.contains(k)){ el.classList.remove(k); undo.push(function(){ el.classList.add(k); }); }
    });
  });
  document.querySelectorAll('[data-lm-ready],[data-lm-done]').forEach(function(el){
    ['data-lm-ready','data-lm-done'].forEach(function(a){
      var v = el.getAttribute(a);
      if(v !== null){ el.removeAttribute(a); undo.push(function(){ el.setAttribute(a, v); }); }
    });
  });
  setTimeout(function(){ undo.forEach(function(f){ f(); }); }, 0);
}, true);
</script>
```

## Verification

Every pattern above passed these before it was written down; a new one must
too. `/lisa-motion` carries the full checklist.

- Renders in a browser, over `http://`, with no console errors.
- Reduced motion (`--force-prefers-reduced-motion` or the OS setting): the
  finished state, nothing moving, every control still working.
- Print (`--print-to-pdf`): the finished state on every page.
- Hidden tab: open the file in a background tab, wait two seconds, switch
  to it — nothing blank (`L-022`).
- 375px: no horizontal overflow; cursor patterns absent, their keyboard or
  button path present.
- Route away from the page: every rAF loop and WAAPI animation is
  cancelled (check `document.getAnimations()` and the frame counter).
- Scroll through the whole page: every `lm-on` / `lm-reveal` element ends
  up `.is-in`. One that never does is hiding its own box from the observer
  (rule 11).

## Known gaps

- **Scroll timelines** (`animation-timeline: view()` / `scroll()`,
  patterns 03, 05, 06, 09, 10, 11, 12, 13, 18) — Chrome 115+, Edge 115+,
  Safari 26, Firefox recent (behind a flag before that). Every use is
  inside `@supports` with a static or timed fallback, so nothing breaks;
  the split columns (11) and the parallax (10) are simply still.
- **View transitions** (37) — Chrome 111+, Safari 18+, Firefox recent. The
  fallback is an instant class toggle.
- **`@property`** (20, 22) — Chrome 85+, Safari 16.4+, Firefox 128+. Without
  it the count-up shows the final number and the spotlight position jumps
  instead of easing.
- **Independent `translate`/`scale` properties** (24, 33, 36, 38) — every
  current browser; a 2021 browser ignores them and the element stays put.
- **No reduced-motion equivalent beyond "static":** glow (25), repel (27),
  trail (28), glitch (16), burst (33), ripple (32), scramble (15), mesh (39)
  and gradient text (17) have no meaningful reduced form — they switch off.
  The flip (34), island (36), morph (37), accordion (29) and coverflow
  (35) keep working and simply stop easing.
- **Touch:** spotlight, tilt, magnet, glow, dock, repel, trail and the
  hover half of accordion, flip and spot reveal do nothing on touch; each
  says what remains. The compare (30) and pan (38) work on touch through
  the range input and pointer capture.
- **Typewriter** (14) is monospace Latin only; Hangul and CJK need a wider
  caret step than `1ch`.
- **`counter()` with `var()`** (20) renders in Chrome and Safari; where it
  does not, the final number shows from the start.
