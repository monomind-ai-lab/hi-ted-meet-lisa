/**
 * POST /e — the five funnel events, counted and nothing more.
 *
 * Cloudflare Web Analytics gives this site pageviews and referrers; it has
 * no custom events. This is the whole of the custom-event path: one
 * Cloudflare Pages Function whose entire input is an event name from the
 * allow-list below, sent by `navigator.sendBeacon` from site/index.html and
 * (web mode only) assets/tedandlisa-intake.html.
 *
 * The ethos is load-bearing, so it is enforced here rather than trusted:
 *   · The event name is the only thing read. The URL, the query string, the
 *     referrer, the body beyond 64 bytes and every header are ignored.
 *   · Nothing is stored that could identify a visitor — no ip, no user
 *     agent, no id, no cookie is set or read. Cookieless, so still no
 *     consent banner.
 *   · The name must be one of five. An arbitrary string is never recorded,
 *     so a stray beacon cannot turn this endpoint into a log of free text.
 *
 * Always 204 with no body, whatever happens — a bad name, a huge body, a
 * missing binding, a failing write. The client neither reads nor waits for
 * the response, and a measurement path must never be able to break a visit.
 *
 * WHERE THE DATA GOES. Nowhere, until someone binds it. `env.WAE` is a
 * Workers Analytics Engine dataset binding added by hand in the Cloudflare
 * dashboard (Workers & Pages → hi-ted-meet-lisa → Settings → Bindings →
 * Add → Analytics engine → Variable name `WAE`, Dataset `tedlisa_events`,
 * then redeploy). Until that exists this endpoint answers 204 and records
 * nothing, which is also how it degrades forever if the binding is never
 * added. Deploying this file changes nothing a visitor can see either way.
 *
 * Wrangler compiles `functions/` from the *current working directory*, not
 * from the deploy directory — `wrangler pages deploy site` run at the
 * repository root finds this file here. Do not move it under site/: that
 * folder is assembled by site/sync.sh and wrangler would upload it as a
 * static asset instead of building it. (Wrangler 4:
 * `functionsDirectory = customFunctionsDirectory || path.join(process.cwd(), "functions")`.)
 */

const EVENTS = new Set([
  "ref-file",      /* arrived from a generated file's colophon — the loop */
  "intake-open",   /* the intake overlay was opened */
  "prompt-copy",   /* the paste-ready prompt was copied */
  "cta-teams",     /* a paid CTA was clicked */
  "preview-open"   /* a gallery preview was opened */
]);

/* 64 bytes is generous for names of at most twelve characters; anything
   larger is not one of ours and is dropped without being read. */
const MAX_BODY = 64;

function noContent() {
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "POST") return noContent();
  if (Number(request.headers.get("content-length") || 0) > MAX_BODY) return noContent();

  let name;
  try {
    name = (await request.text()).trim();
  } catch (e) {
    return noContent();
  }
  if (!EVENTS.has(name)) return noContent();

  /* One row per event, carrying the name and nothing else. `indexes` is the
     sampling key, so the counts stay honest per event under load. */
  try {
    if (env && env.WAE && typeof env.WAE.writeDataPoint === "function") {
      env.WAE.writeDataPoint({ blobs: [name], indexes: [name], doubles: [1] });
    }
  } catch (e) {
    /* A measurement failure is not a visitor's problem. */
  }

  return noContent();
}
