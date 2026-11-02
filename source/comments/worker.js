// Apex Fitness Centre blog comments: a tiny Cloudflare Worker + D1 database.
// Public:  GET  /api/comments?post=<slug>   approved comments for one post
//          POST /api/comments               {post, name, body, website (honeypot), elapsed}
// Owner:   GET  /admin                      moderation page (asks for the admin key)
//          GET  /api/admin/comments?status=pending|approved
//          POST /api/admin/approve {id} · /api/admin/delete {id} · /api/admin/reply {parent_id, body}
// Secrets: ADMIN_KEY (set by the deploy workflow). Binding: DB (D1).

const ORIGINS = ["https://apexfitnesscentre.shop", "https://www.apexfitnesscentre.shop"];
const SITE = "https://apexfitnesscentre.shop";
const OWNER_NAME = "Apex Fitness Centre";

const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", ...headers } });

function cors(req) {
  const o = req.headers.get("origin") || "";
  const allow = ORIGINS.includes(o) || o.startsWith("http://localhost") || o.startsWith("http://127.0.0.1") ? o : ORIGINS[0];
  return { "access-control-allow-origin": allow, "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "content-type", "vary": "origin" };
}

async function sha(text) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(d)].slice(0, 12).map(b => b.toString(16).padStart(2, "0")).join("");
}

function sameKey(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

const clean = s => String(s || "").replace(/\r\n?/g, "\n").replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, "").trim();
const SLUG = /^[a-z0-9][a-z0-9-]{0,119}$/;

async function listPublic(env, post) {
  const { results } = await env.DB.prepare(
    "SELECT id, name, body, created_at, owner, parent_id FROM comments WHERE post = ? AND approved = 1 ORDER BY created_at ASC LIMIT 300"
  ).bind(post).all();
  return results;
}

async function submit(req, env) {
  let d;
  try { d = await req.json(); } catch { return json({ error: "Invalid request." }, 400, cors(req)); }
  const post = clean(d.post), name = clean(d.name).replace(/\s+/g, " "), body = clean(d.body);
  if (!SLUG.test(post)) return json({ error: "Unknown article." }, 400, cors(req));
  // Spam traps: hidden field must stay empty, and real people take a few seconds to write.
  if (clean(d.website)) return json({ ok: true, pending: true }, 200, cors(req));
  if (!(Number(d.elapsed) >= 3000)) return json({ error: "Please take a moment before sending." }, 400, cors(req));
  if (name.length < 2 || name.length > 60) return json({ error: "Please enter your name (2 to 60 characters)." }, 400, cors(req));
  if (body.length < 3 || body.length > 1500) return json({ error: "Comments must be 3 to 1,500 characters." }, 400, cors(req));
  if ((body.match(/https?:\/\/|www\./gi) || []).length > 1) return json({ error: "Please include no more than one link." }, 400, cors(req));
  const ip = req.headers.get("cf-connecting-ip") || "unknown";
  const ipHash = await sha(ip + "|" + (env.ADMIN_KEY || ""));
  const since = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM comments WHERE ip_hash = ? AND created_at > ?").bind(ipHash, since).first();
  if (recent && recent.n >= 3) return json({ error: "Too many comments in a short time. Please try again later." }, 429, cors(req));
  await env.DB.prepare("INSERT INTO comments (post, name, body, created_at, approved, owner, ip_hash) VALUES (?, ?, ?, ?, 1, 0, ?)")
    .bind(post, name, body, new Date().toISOString(), ipHash).run();
  return json({ ok: true, pending: false }, 200, cors(req));
}

function authed(req, env) {
  const h = req.headers.get("authorization") || "";
  return sameKey(h.replace(/^Bearer\s+/i, ""), env.ADMIN_KEY || "");
}

async function admin(req, env, path) {
  if (!env.ADMIN_KEY) return json({ error: "ADMIN_KEY is not set." }, 500);
  if (!authed(req, env)) return json({ error: "Wrong admin key." }, 401);
  if (req.method === "GET" && path === "/api/admin/comments") {
    const status = new URL(req.url).searchParams.get("status") === "approved" ? 1 : 0;
    const { results } = await env.DB.prepare(
      "SELECT id, post, name, body, created_at, owner, parent_id FROM comments WHERE approved = ? ORDER BY created_at DESC LIMIT 200"
    ).bind(status).all();
    const pending = await env.DB.prepare("SELECT COUNT(*) AS n FROM comments WHERE approved = 0").first();
    return json({ comments: results, pending: pending ? pending.n : 0 });
  }
  if (req.method !== "POST") return json({ error: "Not found." }, 404);
  let d; try { d = await req.json(); } catch { return json({ error: "Invalid request." }, 400); }
  const id = Number(d.id || d.parent_id);
  if (!Number.isInteger(id) || id < 1) return json({ error: "Missing id." }, 400);
  if (path === "/api/admin/approve") { await env.DB.prepare("UPDATE comments SET approved = 1 WHERE id = ?").bind(id).run(); return json({ ok: true }); }
  if (path === "/api/admin/delete") { await env.DB.prepare("DELETE FROM comments WHERE id = ? OR parent_id = ?").bind(id, id).run(); return json({ ok: true }); }
  if (path === "/api/admin/reply") {
    const body = clean(d.body);
    if (body.length < 1 || body.length > 2000) return json({ error: "Reply must be 1 to 2,000 characters." }, 400);
    const parent = await env.DB.prepare("SELECT post FROM comments WHERE id = ?").bind(id).first();
    if (!parent) return json({ error: "Comment not found." }, 404);
    await env.DB.prepare("UPDATE comments SET approved = 1 WHERE id = ?").bind(id).run();
    await env.DB.prepare("INSERT INTO comments (post, name, body, created_at, approved, owner, parent_id) VALUES (?, ?, ?, ?, 1, 1, ?)")
      .bind(parent.post, OWNER_NAME, body, new Date().toISOString(), id).run();
    return json({ ok: true });
  }
  return json({ error: "Not found." }, 404);
}

const ADMIN_HTML = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Comments · Apex Fitness Centre</title><style>
:root{--ink:#141416;--mut:#5b5e66;--ln:#e6e5e1;--red:#d3132b;--ok:#15803d}*{box-sizing:border-box}
body{margin:0;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:#f7f7f5}
header{background:var(--ink);color:#fff;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
header b{color:#ff4d5e;letter-spacing:.04em}main{max-width:860px;margin:0 auto;padding:20px 16px 60px}
.tabs{display:flex;gap:8px;margin:0 0 16px}.tabs button,.btn{border:1px solid var(--ln);background:#fff;padding:9px 14px;border-radius:999px;font:600 14px system-ui;cursor:pointer}
.tabs button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.c{background:#fff;border:1px solid var(--ln);border-radius:12px;padding:16px;margin:0 0 12px}.meta{font-size:13px;color:var(--mut);margin-bottom:6px}
.meta a{color:var(--mut)}.who{font-weight:700}.body{white-space:pre-wrap;margin:0 0 12px}.own{background:#fff5f6;border-color:#f5c2c9}
.row{display:flex;gap:8px;flex-wrap:wrap}.ap{background:var(--ok);color:#fff;border-color:var(--ok)}.del{color:var(--red)}
textarea,input{width:100%;font:inherit;padding:10px;border:1px solid #c9c8c4;border-radius:8px}textarea{min-height:80px;margin:8px 0}
#login{max-width:380px;margin:60px auto;background:#fff;border:1px solid var(--ln);border-radius:12px;padding:24px}.empty{color:var(--mut)}
</style></head><body><header><div><b>APEX</b> · Blog comments</div><div id="count"></div></header><main>
<form id="login" hidden><h2>Comments admin</h2><p class="empty">Enter the admin password you saved in GitHub (COMMENTS_ADMIN_KEY).</p><input id="key" type="password" autocomplete="current-password" placeholder="Admin password"><p><button class="btn ap" type="submit">Open</button></p><p id="err" class="del"></p></form>
<div id="app" hidden><div class="tabs"><button data-s="approved" class="on">Published</button><button data-s="pending">Waiting for approval</button><button id="out" type="button">Log out</button></div><div id="list"></div></div>
</main><script>
var K=localStorage.getItem('apexCommentsKey')||'',S='approved',site='${SITE}';
function api(p,o){o=o||{};o.headers=Object.assign({'authorization':'Bearer '+K,'content-type':'application/json'},o.headers||{});return fetch(p,o).then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error(j.error||'Error');return j})})}
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function load(){api('/api/admin/comments?status='+S).then(function(j){document.getElementById('login').hidden=true;document.getElementById('app').hidden=false;
document.getElementById('count').textContent=j.pending?j.pending+' waiting':'';var L=document.getElementById('list');L.innerHTML='';
if(!j.comments.length){L.appendChild(el('p','empty',S==='pending'?'No comments waiting. Nice.':'No published comments yet.'));return}
j.comments.forEach(function(c){var d=el('div','c'+(c.owner?' own':''));var m=el('div','meta');m.appendChild(el('span','who',c.name));
m.appendChild(document.createTextNode(' · '+new Date(c.created_at).toLocaleString()+' · '));var a=el('a',null,c.post);a.href=site+'/blog/'+c.post+'/#comments';a.target='_blank';m.appendChild(a);
d.appendChild(m);d.appendChild(el('p','body',c.body));var r=el('div','row');
if(S==='pending'){var b1=el('button','btn ap','Approve');b1.onclick=function(){api('/api/admin/approve',{method:'POST',body:JSON.stringify({id:c.id})}).then(load)};r.appendChild(b1)}
if(!c.owner){var b2=el('button','btn','Reply as Apex');b2.onclick=function(){var t=el('textarea');t.placeholder='Your reply (published straight away)';var s=el('button','btn ap','Send reply');
s.onclick=function(){if(!t.value.trim())return;api('/api/admin/reply',{method:'POST',body:JSON.stringify({parent_id:c.id,body:t.value})}).then(load).catch(function(e){alert(e.message)})};d.appendChild(t);d.appendChild(s);b2.remove()};r.appendChild(b2)}
var b3=el('button','btn del','Delete');b3.onclick=function(){if(confirm('Delete this comment for good?'))api('/api/admin/delete',{method:'POST',body:JSON.stringify({id:c.id})}).then(load)};r.appendChild(b3);
d.appendChild(r);L.appendChild(d)})}).catch(function(e){document.getElementById('app').hidden=true;document.getElementById('login').hidden=false;if(K)document.getElementById('err').textContent=e.message})}
document.getElementById('login').onsubmit=function(e){e.preventDefault();K=document.getElementById('key').value.trim();localStorage.setItem('apexCommentsKey',K);load()};
document.getElementById('out').onclick=function(){localStorage.removeItem('apexCommentsKey');K='';location.reload()};
document.querySelectorAll('.tabs button[data-s]').forEach(function(b){b.onclick=function(){S=b.getAttribute('data-s');document.querySelectorAll('.tabs button[data-s]').forEach(function(x){x.classList.toggle('on',x===b)});load()}});
load();
</script></body></html>`;

export default {
  async fetch(req, env) {
    const url = new URL(req.url), path = url.pathname.replace(/\/+$/, "") || "/";
    try {
      if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
      if (path === "/api/comments" && req.method === "GET") {
        const post = clean(url.searchParams.get("post"));
        if (!SLUG.test(post)) return json({ error: "Unknown article." }, 400, cors(req));
        return json({ comments: await listPublic(env, post) }, 200, { ...cors(req), "cache-control": "no-store" });
      }
      if (path === "/api/comments" && req.method === "POST") return submit(req, env);
      if (path.startsWith("/api/admin/")) return admin(req, env, path);
      if (path === "/admin") return new Response(ADMIN_HTML, { headers: { "content-type": "text/html; charset=utf-8", "x-robots-tag": "noindex", "cache-control": "no-store" } });
      if (path === "/") return json({ ok: true, service: "Apex Fitness Centre comments" });
      return json({ error: "Not found." }, 404);
    } catch (e) {
      return json({ error: "Server error. Please try again." }, 500, cors(req));
    }
  },
};
