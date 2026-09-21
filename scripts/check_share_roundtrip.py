#!/usr/bin/env python3
"""Gate the Share control's hand-off, and the copy of itself a file hands over.

    python3 scripts/check_share_roundtrip.py FILE [--template ID]
    python3 scripts/check_share_roundtrip.py --registry
    python3 scripts/check_share_roundtrip.py --registry --json

Exit 1 on a finding, 2 when the harness itself failed. Stdlib only, plus a
local Chrome — the harness, the server and the Chrome plumbing are
`check_overflow.py`'s, imported rather than copied.

**What is being checked, and why a browser.** A standalone file cannot read
itself on `file://`, so the Share control rebuilds the file from the DOM
instead: it clones `document.documentElement`, drops every node the template
injected at runtime, and puts the rest back the way the author wrote it. That
rebuild is a small program with one job — produce a file that opens exactly
like the original — and the only honest way to check it is to open the rebuilt
file and look. A regular expression cannot tell a published copy that boots on
slide one in English from one that boots on slide six in Korean with the menu
open.

**Three loads per template, all on `file://`.**

  origin      the template, untouched. Records its settled state and a
              normalised dump of its DOM.
  publish     the template, deliberately dirtied — two screens in, another
              language where an inline control offers one, the other theme
              where a toggle offers one, the share menu opened and closed —
              then Publish link clicked. The hand-off is driven to completion
              against a stub receiver and the `htmlbyme:document` payload is
              captured.
  republish   that payload, written to a file and opened fresh. Records its
              settled state and DOM, proves its navigation and language
              control still work, and publishes from it again so the second
              generation can be compared with the first.

The stub receiver is the whole reason this is safe to run anywhere: nothing
contacts htmlbyme.com, and nothing needs to. `window.open` is replaced with a
fake window, the share script's own `message` listener is captured as it is
registered, and the protocol is played back into it by hand — a first
`htmlbyme:ready`, then a second standing in for the receiver being reloaded
(protocol v1.1: it must be answered too, with the identical document), then
seven hostile answers that must all be refused, then the real one.

**What makes it fail.** A console error or an uncaught exception on either
load; a payload that carries a `data-lisa-runtime` node or an open menu; a
payload missing the content fences or the content map; a published copy that
boots somewhere other than where the original boots; any normalised DOM
difference outside the documented allow-list below; a second generation that
differs from the first; a payload over 10 MB; a message accepted from the
wrong origin or the wrong window; a second `htmlbyme:ready` left unanswered,
or answered with different bytes; a link shown that did not come from
`https://link.htmlbyme.com/`; a popup-blocked click that offers no fallback.

**The allow-list.** Two subtrees are excluded from the DOM comparison, and
both are excluded because they are output rather than content:

  [data-lisa-runtime]   nodes a template injects at runtime. The payload is
                        separately asserted to contain none of them, so
                        excluding them here is not excusing anything.
  .fig-body, #vcanvas   rendered mermaid SVG. The templates that carry
                        diagrams already throw this away when they save a
                        copy of themselves; it is redrawn from the mermaid
                        source the file carries, on every load, and it is
                        drawn by a CDN script whose timing is not ours.

Nothing else is allow-listed. Attribute values longer than 120 characters are
compared by length and hash rather than in full — the MonoMind deck is 57%
base64 — which is a shortening of the diff, not a relaxation of it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from check_overflow import (  # noqa: E402  (path set above)
    ChromeRun,
    find_chrome,
    probe_chrome,
    run_chrome,
    serve,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "templates" / "templates.json"

# The pinned hand-off. These are the artifact side's constants; the gate
# repeats them so a template that quietly repointed itself is a finding.
PUBLISH_URL = "https://htmlbyme.com/publish"
PUBLISH_ORIGIN = "https://htmlbyme.com"
LINK_PREFIX = "https://link.htmlbyme.com/"
GOOD_LINK = LINK_PREFIX + "gate-fixture"
MAX_BYTES = 10 * 1024 * 1024

# Subtrees left out of the DOM comparison. See the allow-list note above.
EXCLUDED = ["[data-lisa-runtime]", ".fig-body", "#vcanvas"]

# How long to let a file settle after `load` before it is measured. Webfonts
# and, on two templates, a CDN mermaid have to land first.
SETTLE_MS = 1200


# ────────────────────────────────────────────────────────────────────
# The in-page harness.
# ────────────────────────────────────────────────────────────────────

HARNESS_JS = r"""
(function () {
  "use strict";
  var MODE = %(mode)s;
  var POST = %(post)s;
  var PUBLISH_ORIGIN = %(publish_origin)s;
  var GOOD_LINK = %(good_link)s;
  var EXCLUDED = %(excluded)s;
  var SETTLE_MS = %(settle)d;

  var errors = [];

  /* Installed with the real addEventListener, before it is wrapped below. */
  window.addEventListener("error", function (e) {
    errors.push("uncaught: " + (e.message || String(e.error)));
  });
  window.addEventListener("unhandledrejection", function (e) {
    var r = e.reason;
    errors.push("unhandled rejection: " + (r && r.message ? r.message : String(r)));
  });
  var realConsoleError = console.error;
  console.error = function () {
    errors.push("console.error: " + Array.prototype.join.call(arguments, " "));
    return realConsoleError.apply(console, arguments);
  };

  /* ---- the stub receiver -------------------------------------------
     Nothing here reaches the network. window.open hands back a fake
     window, and the protocol is played into the share script's own
     listener by hand. */
  var opened = [];
  var posted = [];
  var blockPopup = false;
  var FAKE = {
    closed: false,
    focus: function () {},
    close: function () { FAKE.closed = true; },
    postMessage: function (msg, target) { posted.push({ msg: msg, target: target }); }
  };
  window.open = function (url) {
    opened.push({ url: url, argc: arguments.length,
                  features: arguments.length > 2 ? String(arguments[2]) : null });
    return blockPopup ? null : FAKE;
  };

  var handlers = [];
  var addReal = window.addEventListener.bind(window);
  var removeReal = window.removeEventListener.bind(window);
  window.addEventListener = function (type, fn, opts) {
    if (type === "message") { handlers.push(fn); }
    return addReal(type, fn, opts);
  };
  window.removeEventListener = function (type, fn, opts) {
    if (type === "message") {
      var i = handlers.indexOf(fn);
      if (i >= 0) { handlers.splice(i, 1); }
    }
    return removeReal(type, fn, opts);
  };
  function deliver(data, origin, source) {
    var ev = { data: data, origin: origin, source: source };
    handlers.slice().forEach(function (h) {
      try { h(ev); } catch (e) { errors.push("message handler threw: " + e); }
    });
  }

  /* ---- small helpers ------------------------------------------------ */
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function vis(el) {
    if (!el || el.hidden) { return false; }
    if (!el.getClientRects || !el.getClientRects().length) { return false; }
    var s = getComputedStyle(el);
    return s.visibility !== "hidden" && s.display !== "none";
  }
  function describe(el) {
    return el.nodeName.toLowerCase() + (el.id ? "#" + el.id : "") +
           (el.className && typeof el.className === "string"
              ? "." + el.className.trim().split(/\s+/).join(".") : "");
  }
  function key(k) {
    var init = { key: k, bubbles: true, cancelable: true };
    try { document.body.dispatchEvent(new KeyboardEvent("keydown", init)); } catch (e) {}
    try { window.dispatchEvent(new KeyboardEvent("keydown", init)); } catch (e) {}
    try { document.dispatchEvent(new KeyboardEvent("keydown", init)); } catch (e) {}
  }
  function hash(s) {
    var h = 5381, i;
    for (i = 0; i < s.length; i++) { h = ((h * 33) ^ s.charCodeAt(i)) >>> 0; }
    return h.toString(16);
  }

  /* ---- what "where the file opens" means ---------------------------- */
  function screens() {
    var list = document.querySelectorAll(".slide, .page, .screen, section[data-screen-label]");
    var i, active = -1;
    for (i = 0; i < list.length; i++) {
      if (list[i].classList.contains("active")) { active = i; break; }
    }
    return { count: list.length, active: active };
  }
  function state() {
    var doc = document.documentElement;
    return {
      lang: doc.lang || "",
      dir: doc.getAttribute("dir") || "",
      theme: doc.getAttribute("data-theme") || "",
      bodyLang: document.body.getAttribute("data-lang") || "",
      title: document.title,
      hash: location.hash,
      /* Both axes: the MonoMind deck's track scrolls sideways, the evidence
         deck and the paper brief snap downwards, and either is "where the
         file is open". */
      scrollX: Math.round(window.pageXOffset || doc.scrollLeft || document.body.scrollLeft || 0),
      scrollY: Math.round(window.pageYOffset || doc.scrollTop || document.body.scrollTop || 0),
      screens: screens()
    };
  }

  /* ---- the normalised DOM ------------------------------------------- */
  function excluded(el) {
    var i;
    for (i = 0; i < EXCLUDED.length; i++) {
      try { if (el.matches(EXCLUDED[i])) { return true; } } catch (e) {}
    }
    return false;
  }
  function dump() {
    var lines = [];
    function attrs(node) {
      var names = [], i, v, out = [];
      for (i = 0; i < node.attributes.length; i++) { names.push(node.attributes[i].name); }
      names.sort();
      for (i = 0; i < names.length; i++) {
        v = node.getAttribute(names[i]);
        if (v && v.length > 120) { v = "<" + v.length + ":" + hash(v) + ">"; }
        out.push(names[i] + "=" + v);
      }
      return out.join("|");
    }
    function walk(node, path) {
      var i, tag, text, kids;
      if (node.nodeType === 3) {
        text = node.nodeValue.replace(/\s+/g, " ").trim();
        if (text) { lines.push(path + " #text " + text); }
        return;
      }
      if (node.nodeType !== 1) { return; }
      if (excluded(node)) { return; }
      tag = node.nodeName.toLowerCase();
      path = path + "/" + tag;
      if (tag === "script" || tag === "style") {
        lines.push(path + " [" + attrs(node) + "] {" +
                   node.textContent.length + ":" + hash(node.textContent) + "}");
        return;
      }
      lines.push(path + " [" + attrs(node) + "]");
      kids = node.childNodes;
      for (i = 0; i < kids.length; i++) { walk(kids[i], path); }
    }
    walk(document.documentElement, "");
    return lines;
  }

  /* ---- the share control, however this template shapes it ----------- */
  function sroot() { return document.querySelector('[data-lisa-share="root"]'); }
  function spart(name) {
    var r = sroot();
    return r ? r.querySelector('[data-lisa-share="' + name + '"]') : null;
  }
  function openShare() {
    var t = spart("toggle");
    if (!t) { return false; }
    if (!vis(t)) {
      /* on the two templates where Share lives inside the deck menu */
      var mb = document.querySelector("#deckMenuBtn, #deck-menu-btn");
      if (mb) { mb.click(); }
    }
    t.click();
    return true;
  }
  function closeShare() {
    var t = spart("toggle");
    if (t) { t.click(); }
  }
  function resultOf() {
    var res = spart("result");
    if (!res) { return { present: false }; }
    return {
      present: true,
      hidden: !!res.hidden,
      text: res.textContent.replace(/\s+/g, " ").trim().slice(0, 400),
      hrefs: Array.prototype.map.call(res.querySelectorAll("a"),
                                      function (a) { return a.getAttribute("href"); }),
      linkTexts: Array.prototype.map.call(res.querySelectorAll("a"),
                                          function (a) { return a.textContent; }),
      images: res.querySelectorAll("img").length,
      buttons: res.querySelectorAll("button").length
    };
  }

  /* ---- deliberately dirtying the state ------------------------------ */
  /* Only things that actually move the reader: a routed link, a chip, a
     generated nav dot. `.dot` alone would also catch architecture's
     decorative legend swatches, which are spans and navigate nowhere. */
  var NAV_SELECTOR = "[data-page],[data-route],[data-nav],button.dot,a.dot";
  var navTargets = 0;

  function navigate() {
    var done = [];
    var cand = document.querySelectorAll(NAV_SELECTOR);
    var picked = [], i;
    for (i = 0; i < cand.length && picked.length < 3; i++) {
      if (vis(cand[i]) && !cand[i].hasAttribute("disabled")) { picked.push(cand[i]); }
    }
    navTargets = picked.length;
    for (i = 1; i < picked.length; i++) {
      picked[i].click();
      done.push("clicked " + describe(picked[i]));
    }
    /* Both axes again: one of these is "next screen" on every template. */
    key("ArrowRight"); key("ArrowRight");
    key("ArrowDown"); key("ArrowDown");
    done.push("ArrowRight x2, ArrowDown x2");
    return done;
  }
  /* Named language controls only. A bare `.seg button` also matched
     architecture's theme/export cluster, which sits before its language
     pair in document order — the gate then toggled the theme twice and
     never switched language at all. */
  function switchLang() {
    var list = document.querySelectorAll(
      "#langToggle, #langSeg button, .lang-toggle button, " +
      ".lang-switch button, #btnEn, #btnKo, #btnZh");
    var i, el;
    for (i = 0; i < list.length; i++) {
      el = list[i];
      if (!vis(el)) { continue; }
      if (el.getAttribute("aria-disabled") === "true") { continue; }
      if (el.classList.contains("active")) { continue; }
      if (el.getAttribute("aria-pressed") === "true") { continue; }
      el.click();
      return "clicked " + describe(el);
    }
    return "no inline language control was reachable";
  }
  function toggleTheme() {
    var t = document.querySelector("#btnTheme");
    if (vis(t)) { t.click(); return "clicked #btnTheme"; }
    var mb = document.querySelector("#deck-menu-btn, #deckMenuBtn");
    var item = document.querySelector("#deck-menu-theme, #deckMenuTheme");
    if (mb && item) {
      mb.click(); item.click(); mb.click();
      return "toggled the theme through the deck menu";
    }
    return "no theme control";
  }

  /* ---- the hand-off, played against the stub ------------------------ */
  function publishRun() {
    var r = { opened: [], hostile: [] };
    r.state0 = state();
    r.navigated = navigate();
    return sleep(150).then(function () {
      r.language = switchLang();
      return sleep(150);
    }).then(function () {
      r.theme = toggleTheme();
      return sleep(150);
    }).then(function () {
      /* open and close the menu, so its open state has been in the DOM */
      openShare();
      return sleep(80);
    }).then(function () {
      closeShare();
      return sleep(80);
    }).then(function () {
      r.dirtyState = state();
      r.navTargets = navTargets;
      openShare();
      return sleep(80);
    }).then(function () {
      var pub = spart("publish");
      if (!pub) { r.fatal = "the share menu offers no Publish link item"; return null; }
      r.publishVisible = vis(pub);
      pub.click();
      return sleep(80);
    }).then(function () {
      if (r.fatal) { return null; }
      r.opened = opened.slice();
      if (!handlers.length) {
        r.fatal = "the share script registered no message listener";
        return null;
      }
      deliver({ type: "htmlbyme:ready", v: 1 }, PUBLISH_ORIGIN, FAKE);
      return waitFor(function () { return posted.length > 0; }, 6000);
    }).then(function () {
      if (r.fatal) { return null; }
      if (!posted.length) { r.fatal = "nothing was handed to the receiver"; return null; }
      r.postTarget = posted[0].target;
      var msg = posted[0].msg;
      r.envelope = { type: msg.type, v: msg.v, title: msg.title,
                     generator: msg.generator, template: msg.template,
                     keys: Object.keys(msg).sort() };
      r.payload = typeof msg.html === "string" ? msg.html : null;
      /* The receiver reloads: it comes back and says ready again. Protocol
         v1.1 answers every ready until the exchange ends, so a second
         document must arrive — and it must be the same document, because
         it was built once per click and that one promise is reused. */
      deliver({ type: "htmlbyme:ready", v: 1 }, PUBLISH_ORIGIN, FAKE);
      return waitFor(function () { return posted.length > 1; }, 4000);
    }).then(function () {
      if (r.fatal) { return null; }
      r.postedAfterReload = posted.length;
      r.reloadPayloadIdentical = posted.length > 1
        && posted[1].msg.html === posted[0].msg.html
        && posted[1].target === posted[0].target;
      return hostileAnswers(r);
    }).then(function () {
      if (r.fatal) { return null; }
      var expires = new Date(Date.now() + 15 * 86400000).toISOString();
      deliver({ type: "htmlbyme:published", v: 1, url: GOOD_LINK, expires_at: expires },
              PUBLISH_ORIGIN, FAKE);
      return sleep(150);
    }).then(function () {
      if (r.fatal) { return r; }
      r.published = resultOf();
      r.listenersLeft = handlers.length;
      /* and what a blocked popup leaves behind */
      blockPopup = true;
      openShare();
      return sleep(60).then(function () {
        var pub = spart("publish");
        if (pub) { pub.click(); }
        return sleep(150);
      }).then(function () {
        r.popupBlocked = resultOf();
        blockPopup = false;
        return r;
      });
    });
  }

  function hostileAnswers(r) {
    var cases = [
      ["wrong origin", { type: "htmlbyme:published", v: 1, url: GOOD_LINK },
       "https://evil.example.test", FAKE],
      ["wrong source", { type: "htmlbyme:published", v: 1, url: GOOD_LINK },
       PUBLISH_ORIGIN, { postMessage: function () {} }],
      ["plain http", { type: "htmlbyme:published", v: 1, url: "http://link.htmlbyme.com/x" },
       PUBLISH_ORIGIN, FAKE],
      ["lookalike host", { type: "htmlbyme:published", v: 1,
                           url: "https://link.htmlbyme.com.evil.test/x" },
       PUBLISH_ORIGIN, FAKE],
      ["another host", { type: "htmlbyme:published", v: 1, url: "https://evil.test/x" },
       PUBLISH_ORIGIN, FAKE],
      ["markup for a url", { type: "htmlbyme:published", v: 1,
                             url: '<img src=x onerror="window.__gateXSS=1">' },
       PUBLISH_ORIGIN, FAKE],
      ["a javascript: url", { type: "htmlbyme:published", v: 1,
                              url: "javascript:window.__gateXSS=1" },
       PUBLISH_ORIGIN, FAKE]
    ];
    var i = 0;
    function next() {
      if (i >= cases.length) { r.xss = !!window.__gateXSS; return Promise.resolve(null); }
      var c = cases[i++];
      deliver(c[1], c[2], c[3]);
      return sleep(60).then(function () {
        var res = resultOf();
        res.name = c[0];
        r.hostile.push(res);
        return next();
      });
    }
    return next();
  }

  function waitFor(pred, ms) {
    var waited = 0;
    function tick() {
      if (pred() || waited >= ms) { return Promise.resolve(null); }
      waited += 50;
      return sleep(50).then(tick);
    }
    return tick();
  }

  /* ---- drive ---------------------------------------------------------- */
  function loaded() {
    return new Promise(function (res) {
      if (document.readyState === "complete") { res(null); return; }
      addReal("load", function () { res(null); }, { once: true });
    });
  }

  function report(payload) {
    payload.errors = errors;
    payload.mode = MODE;
    try {
      fetch(POST, { method: "POST", mode: "no-cors",
                    headers: { "Content-Type": "text/plain" },
                    body: JSON.stringify(payload) }).catch(function () {});
    } catch (e) {}
  }

  loaded().then(function () {
    return sleep(SETTLE_MS);
  }).then(function () {
    if (MODE === "origin") {
      /* The panel is display:none until it is opened, so "is the Publish
         item offered" is a question about the markup's `hidden`, not about
         a box on screen. And on the two templates whose idiom for "a control
         that opens a small menu" is an item inside the deck menu, the Share
         button is legitimately not on screen until that menu is opened — so
         what is asked is whether a reader can reach it, not whether it is
         already in view. Measured after the DOM dump, so opening the deck
         menu to check cannot contaminate it. */
      var pub = spart("publish"), cp = spart("copy"), tg = spart("toggle");
      var snapshotOfState = state(), snapshotOfDom = dump();
      var reach = { visible: vis(tg), throughMenu: false };
      if (!reach.visible && tg) {
        var mb = document.querySelector("#deckMenuBtn, #deck-menu-btn");
        if (mb) {
          mb.click();
          reach.throughMenu = vis(tg);
          mb.click();
        }
      }
      return { state: snapshotOfState, dom: snapshotOfDom,
               shareFound: !!sroot(),
               shareReach: reach,
               toggleAria: tg ? {
                 haspopup: tg.getAttribute("aria-haspopup"),
                 expanded: tg.getAttribute("aria-expanded"),
                 controls: tg.getAttribute("aria-controls")
               } : null,
               publishOffered: !!pub && !pub.hidden,
               copyOffered: !!cp && !cp.hidden,
               resultHidden: !spart("result") || !!spart("result").hidden };
    }
    if (MODE === "republish") {
      var first = { state: state(), dom: dump() };
      return publishRun().then(function (r) {
        r.bootState = first.state;
        r.dom = first.dom;
        return r;
      });
    }
    return publishRun();
  }).then(function (r) {
    report(r || { fatal: "the harness produced nothing" });
  }, function (e) {
    report({ fatal: "the harness threw: " + (e && e.message ? e.message : String(e)) });
  });
})();
"""


# ────────────────────────────────────────────────────────────────────
# Driving one file.
# ────────────────────────────────────────────────────────────────────

def harness_for(mode: str, post_url: str) -> str:
    return HARNESS_JS % {
        "mode": json.dumps(mode),
        "post": json.dumps(post_url),
        "publish_origin": json.dumps(PUBLISH_ORIGIN),
        "good_link": json.dumps(GOOD_LINK),
        "excluded": json.dumps(EXCLUDED),
        "settle": SETTLE_MS,
    }


BODY_OPEN = re.compile(r"<body\b[^>]*>", re.I)


def instrument(html: str, mode: str, post_url: str) -> str | None:
    """The harness, injected as the first thing inside <body>.

    It has to run before the share script — which every template carries in
    its chrome — so that `window.open` and the `message` registration are
    already wrapped when it does. It is marked `data-lisa-runtime`, which is
    exactly what it is: a node that was not in the file. The share control's
    own rule then strips it from the payload, and the gate asserts that it
    did.
    """
    m = BODY_OPEN.search(html)
    if not m:
        return None
    js = harness_for(mode, post_url)
    # No whitespace around the tag. Removing the element must leave the
    # document byte-identical to the one that never had it, or the gate's own
    # instrumentation would show up as an idempotence failure.
    tag = '<script data-lisa-runtime="share-roundtrip-gate">' + js + "</script>"
    return html[:m.end()] + tag + html[m.end():]


def drive(chrome: str, html: str, mode: str, workdir: pathlib.Path,
          name: str) -> tuple[dict | None, list[ChromeRun]]:
    """Write an instrumented copy, open it on file://, return what it POSTed."""
    attempts: list[ChromeRun] = []
    srv = serve(str(workdir), str(workdir))
    try:
        port = srv.server_address[1]
        page = instrument(html, mode, f"http://127.0.0.1:{port}/r/result")
        if page is None:
            return {"fatal": "no <body> tag to instrument"}, attempts
        target = workdir / name
        target.write_text(page, encoding="utf-8")
        for flag, tmo in (("--headless=new", 120.0), ("--headless", 90.0)):
            run = run_chrome(chrome, target.as_uri(), srv, flag, tmo)
            attempts.append(run)
            if run.result is not None:
                try:
                    return json.loads(run.result), attempts
                except ValueError:
                    return {"fatal": "the harness POSTed unparseable JSON"}, attempts
    finally:
        srv.shutdown()
    return None, attempts


# ────────────────────────────────────────────────────────────────────
# The rules.
# ────────────────────────────────────────────────────────────────────

def fences(html: str) -> dict:
    return {
        "start": html.count("<!-- LISA:CONTENT-START"),
        "end": html.count("<!-- LISA:CONTENT-END"),
        "map": "LISA:CONTENT-MAP" in html,
    }


class TagScan(HTMLParser):
    """Counts attributes on real start tags only.

    A plain substring search cannot answer "does the payload carry a
    data-lisa-runtime node": every share script contains the literal string
    twice, in its own source. HTMLParser knows that a <script> body is text,
    so it answers the question that was actually asked.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.runtime: list[str] = []
        self.open_menus: list[str] = []
        self.share_roots = 0
        self.elements = 0

    def handle_starttag(self, tag, attrs):
        self.elements += 1
        a = dict(attrs)
        if "data-lisa-runtime" in a:
            self.runtime.append(f"<{tag} data-lisa-runtime="
                                f"{a.get('data-lisa-runtime')!r}>")
        if a.get("data-open") == "true":
            self.open_menus.append(f"<{tag} id={a.get('id')!r}>")
        if a.get("data-lisa-share") == "root":
            self.share_roots += 1


def scan(html: str) -> TagScan:
    p = TagScan()
    p.feed(html)
    p.close()
    return p


def first_difference(a: str, b: str, window: int = 90) -> str:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    lo = max(0, i - window // 2)
    return (f"first difference at char {i}:\n"
            f"          first : …{a[lo:i + window]!r}…\n"
            f"          second: …{b[lo:i + window]!r}…")


def check_errors(where: str, result: dict) -> list[str]:
    out = []
    for e in result.get("errors") or []:
        out.append(f"{where}: {e}")
    if result.get("fatal"):
        out.append(f"{where}: {result['fatal']}")
    return out


def check_payload(payload: str | None, original: str, template: str) -> list[str]:
    problems = []
    if not payload:
        return ["the payload carried no html"]
    size = len(payload.encode("utf-8"))
    if size > MAX_BYTES:
        problems.append(f"the payload is {size / 1048576:.1f} MB, over the 10 MB cap")
    if not payload.lstrip().lower().startswith("<!doctype"):
        problems.append("the payload does not open with a doctype")
    if not payload.rstrip().endswith("</html>"):
        problems.append("the payload does not end with </html>")
    found = scan(payload)
    if found.runtime:
        problems.append("the payload carries " + str(len(found.runtime)) +
                        " data-lisa-runtime node(s) — something injected at "
                        "runtime was published: " + ", ".join(found.runtime[:4]))
    if found.open_menus:
        problems.append('the payload carries data-open="true" — a menu was '
                        "published open: " + ", ".join(found.open_menus[:4]))
    if found.share_roots != 1:
        problems.append(f"the payload carries {found.share_roots} share roots, "
                        "expected exactly 1")
    want, got = fences(original), fences(payload)
    for key, label in (("start", "LISA:CONTENT-START"), ("end", "LISA:CONTENT-END")):
        if got[key] != want[key]:
            problems.append(f"the payload has {got[key]} {label} fences, "
                            f"the file on disk has {want[key]}")
    if want["map"] and not got["map"]:
        problems.append("the payload lost the LISA:CONTENT-MAP header — "
                        "it sits between the doctype and <html>, outside the clone")
    if "LISA:SHARE-START" in original and "LISA:SHARE-START" not in payload:
        problems.append("the payload lost the LISA:SHARE fences, so the published "
                        "copy cannot be published from or have its control removed")
    return problems


def check_envelope(env: dict | None, template: str) -> list[str]:
    if not env:
        return ["no htmlbyme:document envelope was captured"]
    problems = []
    if env.get("type") != "htmlbyme:document":
        problems.append(f"envelope type is {env.get('type')!r}, not 'htmlbyme:document'")
    if env.get("v") != 1:
        problems.append(f"envelope v is {env.get('v')!r}, not 1")
    if env.get("generator") != "hi-ted-meet-lisa":
        problems.append(f"envelope generator is {env.get('generator')!r}")
    if template and env.get("template") != template:
        problems.append(f"envelope template is {env.get('template')!r}, "
                        f"the registry id is {template!r}")
    return problems


def check_handoff(run: dict) -> list[str]:
    problems = []
    opened = run.get("opened") or []
    if not opened:
        problems.append("the click opened no window")
    else:
        first = opened[0]
        if first.get("url") != PUBLISH_URL:
            problems.append(f"the window was opened at {first.get('url')!r}, "
                            f"not {PUBLISH_URL}")
        if first.get("features"):
            problems.append("window.open was given window features "
                            f"({first['features']!r}) — noopener would break the hand-off")
    if run.get("postTarget") != PUBLISH_ORIGIN:
        problems.append(f"the document was posted to {run.get('postTarget')!r}, "
                        f"not the pinned {PUBLISH_ORIGIN}")
    # Protocol v1.1: the receiver may reload and ask again, and must be
    # answered — with the same document, to the same pinned origin.
    if run.get("postedAfterReload", 0) < 2:
        problems.append("a second htmlbyme:ready went unanswered — a reader who "
                        "reloads the receiving tab is stranded until the timeout")
    elif not run.get("reloadPayloadIdentical"):
        problems.append("the second answer differed from the first: the document "
                        "is built once per click and that one promise is reused, "
                        "so the bytes and the target origin must be identical")
    for case in run.get("hostile") or []:
        hrefs = case.get("hrefs") or []
        if any(h and h.startswith(LINK_PREFIX) for h in hrefs):
            problems.append(f"a hostile answer ({case.get('name')}) was shown as a link")
        if case.get("images"):
            problems.append(f"a hostile answer ({case.get('name')}) injected an element")
        for h in hrefs:
            if h and not h.startswith(LINK_PREFIX) and h != PUBLISH_URL:
                problems.append(f"a hostile answer ({case.get('name')}) left an "
                                f"unexpected link: {h!r}")
    if run.get("xss"):
        problems.append("a url carrying markup ran script — it must be rendered as text")
    pub = run.get("published") or {}
    if GOOD_LINK not in (pub.get("hrefs") or []):
        problems.append("the real answer did not put the link in the menu")
    if GOOD_LINK not in (pub.get("linkTexts") or []):
        problems.append("the link is not shown as its own text")
    if not pub.get("buttons"):
        problems.append("the published link came with no Copy action")
    if "15" not in (pub.get("text") or "") and "day" not in (pub.get("text") or "").lower():
        problems.append("the expiry is not stated in words beside the link")
    if run.get("listenersLeft"):
        problems.append(f"{run['listenersLeft']} message listener(s) left registered "
                        "after the exchange finished")
    blocked = run.get("popupBlocked") or {}
    if PUBLISH_URL not in (blocked.get("hrefs") or []):
        problems.append("a blocked popup offered no fallback link to " + PUBLISH_URL)
    return problems


def check_boot(origin: dict, republished: dict) -> list[str]:
    a = origin.get("state") or {}
    b = republished.get("bootState") or {}
    problems = []
    for field, label in (("lang", "<html lang>"), ("dir", "<html dir>"),
                         ("theme", "the theme attribute"),
                         ("bodyLang", "body[data-lang]"), ("title", "the title"),
                         ("hash", "the route")):
        if a.get(field) != b.get(field):
            problems.append(f"the published copy opens with {label} "
                            f"{b.get(field)!r}; the original opens with {a.get(field)!r}")
    sa = (a.get("screens") or {})
    sb = (b.get("screens") or {})
    if sa.get("active") != sb.get("active"):
        problems.append(f"the published copy opens on screen {sb.get('active')}, "
                        f"the original on {sa.get('active')}")
    if sa.get("count") != sb.get("count"):
        problems.append(f"the published copy has {sb.get('count')} screens, "
                        f"the original {sa.get('count')}")
    for axis in ("scrollX", "scrollY"):
        if a.get(axis) != b.get(axis):
            problems.append(f"the published copy opens at {axis} {b.get(axis)}px, "
                            f"the original at {a.get(axis)}px")
    return problems


def check_dom(origin: dict, republished: dict) -> list[str]:
    import difflib
    a = origin.get("dom") or []
    b = republished.get("dom") or []
    if a == b:
        return []
    diff = [ln for ln in difflib.unified_diff(a, b, "original", "published", lineterm="", n=1)]
    head = diff[:40]
    more = len(diff) - len(head)
    return (["the published copy's DOM differs from the original's after load:"]
            + ["    " + ln for ln in head]
            + ([f"    … {more} more diff lines"] if more > 0 else []))


def check_live(republished: dict) -> tuple[list[str], list[str]]:
    """The published copy must still navigate and still switch language.

    Both checks only fire where there is something to check: a template with
    one screen and no routed control (architecture is one static diagram
    page) cannot move, and a template whose only language control is hidden
    on file:// (the MonoMind deck) cannot be switched. Saying so is a note;
    inventing a finding out of it would be a lie.
    """
    problems: list[str] = []
    notes: list[str] = []
    before = republished.get("state0") or {}
    after = republished.get("dirtyState") or {}
    screens = (before.get("screens") or {}).get("count") or 0
    navigable = (republished.get("navTargets") or 0) > 0 or screens > 1
    moved = (before.get("hash") != after.get("hash")
             or (before.get("screens") or {}).get("active")
                != (after.get("screens") or {}).get("active")
             or before.get("scrollX") != after.get("scrollX")
             or before.get("scrollY") != after.get("scrollY"))
    if not navigable:
        notes.append("no routed control and one screen — navigation was not "
                     "exercised on the published copy")
    elif not moved:
        problems.append("nothing in the published copy moved when its navigation "
                        "was driven — primary navigation may be dead")

    clicked = str(republished.get("language") or "").startswith("clicked")
    langed = (before.get("lang") != after.get("lang")
              or before.get("bodyLang") != after.get("bodyLang"))
    if not clicked:
        notes.append("no inline language control was reachable on the published "
                     "copy — the language check was not exercised")
    elif not langed:
        problems.append("the published copy's language control was clicked and "
                        "nothing changed language")
    return problems, notes


def check_file(chrome: str, target: pathlib.Path, template: str) -> tuple[list[str], list[str]]:
    """Returns (problems, notes). A HARNESS ERROR line makes it a harness failure."""
    original = target.read_text(encoding="utf-8")
    notes: list[str] = []
    problems: list[str] = []

    if "LISA:SHARE-START" not in original:
        return ([f"{target.name} carries no LISA:SHARE region — the Share control "
                 "is missing from this template"], notes)

    with tempfile.TemporaryDirectory(prefix="share-gate-") as td:
        work = pathlib.Path(td)
        # The target's own directory is copied so relative assets resolve.
        for sibling in target.parent.iterdir():
            if sibling.is_file() and sibling != target:
                try:
                    shutil.copyfile(sibling, work / sibling.name)
                except OSError:
                    pass

        origin, tries = drive(chrome, original, "origin", work, "origin.html")
        if origin is None:
            return (harness_error("origin", tries), notes)
        problems += check_errors("on the original", origin)
        if not origin.get("shareFound"):
            problems.append("no [data-lisa-share=\"root\"] element after load")
        reach = origin.get("shareReach") or {}
        if not (reach.get("visible") or reach.get("throughMenu")):
            problems.append("the Share button is neither on screen after load "
                            "nor reachable by opening the template's own menu")
        elif reach.get("throughMenu"):
            notes.append("the Share button lives inside this template's deck "
                         "menu; reached by opening it")
        if not origin.get("publishOffered"):
            problems.append("the Publish link item is not offered on file://")
        if origin.get("copyOffered"):
            problems.append("the Copy link item is offered although the page is "
                            "not sandboxed")
        if not origin.get("resultHidden"):
            problems.append("the result region ships visible; it should be hidden "
                            "until something has been published")
        aria = origin.get("toggleAria") or {}
        if aria.get("haspopup") not in ("true", "menu"):
            problems.append(f"the Share button's aria-haspopup is {aria.get('haspopup')!r}")
        if aria.get("expanded") != "false":
            problems.append(f"the Share button's aria-expanded is {aria.get('expanded')!r} "
                            "at rest")
        if not aria.get("controls"):
            problems.append("the Share button names no aria-controls")

        first, tries = drive(chrome, original, "publish", work, "publish.html")
        if first is None:
            return (harness_error("publish", tries), notes)
        problems += check_errors("while publishing", first)
        if first.get("fatal"):
            return (problems, notes)
        problems += check_handoff(first)
        problems += check_envelope(first.get("envelope"), template)
        payload = first.get("payload")
        problems += [f"first generation: {p}" for p in check_payload(payload, original, template)]
        notes.append("dirtied before publishing: "
                     + "; ".join(first.get("navigated") or [])
                     + "; " + str(first.get("language"))
                     + "; " + str(first.get("theme")))
        if not payload:
            return (problems, notes)

        second, tries = drive(chrome, payload, "republish", work, "republished.html")
        if second is None:
            return (harness_error("republish", tries), notes)
        problems += check_errors("on the published copy", second)
        if second.get("fatal"):
            return (problems, notes)
        problems += check_boot(origin, second)
        problems += check_dom(origin, second)
        live_problems, live_notes = check_live(second)
        problems += live_problems
        notes += live_notes
        problems += check_handoff(second)
        payload2 = second.get("payload")
        problems += [f"second generation: {p}"
                     for p in check_payload(payload2, original, template)]
        notes.append("the published copy was dirtied with: "
                     + "; ".join(second.get("navigated") or [])
                     + "; " + str(second.get("language"))
                     + "; " + str(second.get("theme")))
        if payload2 and payload2 != payload:
            problems.append(
                "publishing the published copy produced different bytes — the "
                "snapshot is not idempotent "
                f"(first {len(payload)} chars / {sha(payload)}, "
                f"second {len(payload2)} chars / {sha(payload2)})\n        "
                + first_difference(payload, payload2))
        elif payload2:
            notes.append(f"payload {len(payload.encode('utf-8'))} bytes, "
                         f"stable across two generations ({sha(payload)})")

    return (problems, notes)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def harness_error(phase: str, attempts: list[ChromeRun]) -> list[str]:
    report = [f"HARNESS ERROR: the {phase} load never POSTed a result under any "
              "headless mode — an infrastructure failure, not a finding. "
              "Per-attempt diagnostics follow:"]
    for run in attempts:
        report.append("-- attempt:")
        report.extend("   " + line for line in run.diagnose())
    return report


# ────────────────────────────────────────────────────────────────────
# Entry points.
# ────────────────────────────────────────────────────────────────────

def registry_templates() -> list[tuple[str, pathlib.Path]]:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    out = []
    for t in reg["templates"]:
        if t.get("kind") == "external" or not t.get("file"):
            continue
        out.append((t["id"], ROOT / t["file"]))
    return out


def template_for(path: pathlib.Path) -> str:
    for tid, f in registry_templates():
        if f.resolve() == path.resolve():
            return tid
    return ""


def report(name: str, problems: list[str], notes: list[str]) -> int:
    harness = any(p.startswith("HARNESS ERROR") for p in problems)
    if problems:
        for p in problems:
            print(f"FAIL: {name}: {p}")
    else:
        print(f"ok: {name}")
    for n in notes:
        print(f"      {n}")
    return 2 if harness else (1 if problems else 0)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="the HTML file to check")
    ap.add_argument("--template", help="its registry id (default: looked up, else blank)")
    ap.add_argument("--registry", action="store_true",
                    help="check every first-party template in templates/templates.json")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("HARNESS ERROR: no Chrome or Chromium found (set CHROME_BIN)",
              file=sys.stderr)
        return 2

    if args.registry:
        targets = registry_templates()
    elif args.file:
        p = pathlib.Path(args.file)
        if not p.is_file():
            print(f"error: no such file: {p}", file=sys.stderr)
            return 2
        targets = [(args.template or template_for(p), p)]
    else:
        print("error: a file is required unless --registry is given", file=sys.stderr)
        return 2

    worst = 0
    results = []
    probed = False
    for tid, path in targets:
        problems, notes = check_file(chrome, path, tid)
        if any(p.startswith("HARNESS ERROR") for p in problems) and not probed:
            probed = True
            ok, msgs = probe_chrome(chrome)
            if not ok:
                problems = ["HARNESS ERROR: Chrome itself is not usable here."] + msgs
                if args.as_json:
                    results.append({"template": tid, "file": str(path),
                                    "problems": problems, "notes": notes})
                else:
                    report(tid or path.name, problems, notes)
                return 2
        results.append({"template": tid, "file": str(path),
                        "problems": problems, "notes": notes})
        if not args.as_json:
            worst = max(worst, report(tid or path.name, problems, notes))

    if args.as_json:
        print(json.dumps(results, indent=2))
        for r in results:
            if any(p.startswith("HARNESS ERROR") for p in r["problems"]):
                worst = 2
            elif r["problems"]:
                worst = max(worst, 1)
    else:
        clean = sum(1 for r in results if not r["problems"])
        print(f"\nchecked {len(results)} template(s), {clean} clean")
    return worst


if __name__ == "__main__":
    sys.exit(main())
