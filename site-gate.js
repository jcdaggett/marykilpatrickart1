// Mary Kilpatrick Art — site password gate (Cloudflare Worker in front of the static assets).
//
// How it works
//   * Every request (pages, images, everything) passes through this Worker first
//     (wrangler.toml: assets.run_worker_first = true).
//   * If the secret SITE_PASSWORD is NOT set, the Worker does nothing and the site is public.
//   * If it IS set, visitors get the browser's password prompt. The username is ignored;
//     only the password is checked.
//
// Turn on:  Cloudflare dashboard > Workers > nameless-frog-2a1d > Settings > Variables and Secrets
//           > add secret  SITE_PASSWORD  (Deploy).
// Turn off: delete that secret. No code change or redeploy of the site is needed.

const REALM = 'Mary Kilpatrick Art - private preview';

async function sha256(text) {
  return new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)));
}

// Constant-time comparison of two strings (compares fixed-length digests).
async function safeEqual(a, b) {
  const [x, y] = await Promise.all([sha256(a), sha256(b)]);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function passwordFrom(request) {
  const header = request.headers.get('Authorization') || '';
  if (!header.startsWith('Basic ')) return null;
  try {
    const decoded = new TextDecoder().decode(
      Uint8Array.from(atob(header.slice(6).trim()), (c) => c.charCodeAt(0))
    );
    const i = decoded.indexOf(':');
    return i === -1 ? decoded : decoded.slice(i + 1);
  } catch (e) {
    return null;
  }
}

export default {
  async fetch(request, env) {
    // Gate is off until the secret exists.
    if (!env.SITE_PASSWORD) return env.ASSETS.fetch(request);

    // Let CORS preflights through untouched.
    if (request.method === 'OPTIONS') return env.ASSETS.fetch(request);

    const supplied = passwordFrom(request);
    if (supplied !== null && (await safeEqual(supplied, env.SITE_PASSWORD))) {
      const res = await env.ASSETS.fetch(request);
      const out = new Response(res.body, res);
      out.headers.set('X-Robots-Tag', 'noindex, nofollow');
      return out;
    }

    return new Response('Password required.', {
      status: 401,
      headers: {
        'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
        'Cache-Control': 'private, no-store',
        'X-Robots-Tag': 'noindex, nofollow',
        'Content-Type': 'text/plain; charset=utf-8',
      },
    });
  },
};
