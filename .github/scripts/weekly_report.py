#!/usr/bin/env python3
"""Weekly growth report for apexfitnesscentre.shop.

Runs on GitHub Actions every Sunday (no Claude needed). It reads the repo, builds the site,
checks the live site and comments, looks at Google Trends, and writes report.md + report.html.
Every number comes from a real source; anything it cannot measure is said plainly.
"""
import datetime as dt, glob, html, json, os, re, subprocess, sys, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "source")
BLOG = os.path.join(SRC, "content", "blog")
SITE = "https://apexfitnesscentre.shop"
NPT = dt.timezone(dt.timedelta(hours=5, minutes=45))
TODAY = dt.datetime.now(NPT).date()
WEEK_AGO, WEEK_AHEAD = TODAY - dt.timedelta(days=7), TODAY + dt.timedelta(days=7)
ADSENSE_APPLY = dt.date(2026, 12, 15)
REPO = os.environ.get("GITHUB_REPOSITORY", "ogharka/apex-fitness-centre")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
UA = {"User-Agent": "ApexWeeklyReport/1.0 (+https://apexfitnesscentre.shop)"}


def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def safe(fn, default=None):
    try:
        return fn()
    except Exception as e:  # report what failed instead of crashing
        print("warn:", fn.__name__ if hasattr(fn, "__name__") else fn, e, file=sys.stderr)
        return default


# ---------- 1. Posts and schedule ----------
posts = []
for f in sorted(glob.glob(os.path.join(BLOG, "20*.md"))):
    name = os.path.basename(f)
    try:
        d = dt.date.fromisoformat(name[:10])
    except ValueError:
        continue
    text = open(f, encoding="utf-8").read()
    fm = text.split("---", 2)[1] if text.startswith("---") else ""
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", fm, re.M))
    if meta.get("draft", "").lower() in ("true", "yes", "1"):
        continue
    body = text.split("---", 2)[2] if text.startswith("---") else text
    posts.append(dict(date=d, slug=name[11:-3], title=meta.get("title", name).strip(),
                      words=len(re.sub(r"[#*>\-|`\[\]()!]", " ", body).split())))
live = [p for p in posts if p["date"] <= TODAY]
scheduled = [p for p in posts if p["date"] > TODAY]
this_week = [p for p in live if p["date"] > WEEK_AGO]
next_week = [p for p in scheduled if p["date"] <= WEEK_AHEAD]
last_sched = max((p["date"] for p in scheduled), default=None)
runway_weeks = ((last_sched - TODAY).days / 7) if last_sched else 0
short_live = [p for p in live if p["words"] < 600]

# ---------- 2. Config ----------
build_py = open(os.path.join(SRC, "build.py"), encoding="utf-8").read()
def conf(name):
    m = re.search(rf'^{name}\s*=\s*"([^"]*)"', build_py, re.M)
    return m.group(1) if m else ""
GA_ID, ADSENSE_CLIENT, NEWSLETTER = conf("GA_ID"), conf("ADSENSE_CLIENT"), conf("NEWSLETTER_ACTION")
cep = os.path.join(SRC, "comments-endpoint.txt")
COMMENTS_API = open(cep).read().strip().rstrip("/") if os.path.exists(cep) else ""

# ---------- 3. GitHub Actions health (last 7 days) ----------
def actions_health():
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).strftime("%Y-%m-%d")
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    _, body = get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=100&created=%3E%3D{since}", h)
    runs = json.loads(body).get("workflow_runs", [])
    out = {}
    for r in runs:  # newest first
        n = r.get("name") or "?"
        if n in ("pages build and deployment", "Weekly site report") or r.get("status") != "completed":
            continue
        s = out.setdefault(n, {"ok": 0, "fail": 0, "latest": r.get("conclusion")})
        if r.get("conclusion") == "success":
            s["ok"] += 1
        elif r.get("conclusion") in ("failure", "timed_out", "startup_failure"):
            s["fail"] += 1
    return out
health = safe(actions_health, None)

# ---------- 4. Build the site and check links / required pages ----------
def build_and_check():
    out = "/tmp/apex-site"
    r = subprocess.run([sys.executable, os.path.join(SRC, "build.py")], env={**os.environ, "OUT": out},
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        return {"ok": False, "error": (r.stderr or r.stdout)[-400:]}
    m = re.search(r"pages:\s*(\d+)", r.stdout)
    broken = set()
    for f in glob.glob(out + "/**/*.html", recursive=True):
        page_dir = os.path.dirname(f)
        for href in re.findall(r'href="([^"#?]+)', open(f, encoding="utf-8", errors="ignore").read()):
            if href.startswith(("http:", "https:", "mailto:", "tel:", "data:", "javascript:", "//")):
                continue
            tgt = os.path.normpath(os.path.join(out, href.lstrip("/")) if href.startswith("/") else os.path.join(page_dir, href))
            if not (os.path.exists(tgt) or os.path.exists(os.path.join(tgt, "index.html"))):
                broken.add(os.path.relpath(f, out) + " -> " + href)
    need = {p: os.path.exists(os.path.join(out, p, "index.html")) for p in ("about", "contact", "privacy", "editorial-policy")}
    return {"ok": True, "pages": int(m.group(1)) if m else None, "broken": sorted(broken)[:10], "broken_n": len(broken), "need": need}
site = safe(build_and_check, {"ok": False, "error": "build check did not run"})

# ---------- 5. Live site ----------
def live_check():
    res = {}
    for path in ("", "blog/", "food/", "calculators/", "gym/"):
        try:
            code, _ = get(f"{SITE}/{path}")
        except Exception as e:
            code = getattr(e, "code", "error")
        res["/" + path] = code
    try:
        _, sm = get(f"{SITE}/sitemap.xml")
        res["sitemap_urls"] = sm.count("<loc>")
    except Exception:
        res["sitemap_urls"] = None
    try:
        code, _ = get(f"{SITE}/ads.txt")
        res["ads_txt"] = code == 200
    except Exception:
        res["ads_txt"] = False
    return res
livec = safe(live_check, {})

# ---------- 6. Comments ----------
def comments():
    if not COMMENTS_API:
        return None
    total = new = unanswered = reached = 0
    unans = []
    for p in live:
        try:
            _, body = get(f"{COMMENTS_API}/api/comments?post={urllib.parse.quote(p['slug'])}", timeout=15)
            reached += 1
        except Exception:
            continue
        cs = json.loads(body).get("comments", [])
        top = [c for c in cs if not c.get("parent_id")]
        replied = {c["parent_id"] for c in cs if c.get("owner") and c.get("parent_id")}
        total += len(top)
        for c in top:
            created = dt.datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).astimezone(NPT).date()
            if created > WEEK_AGO:
                new += 1
            if c["id"] not in replied:
                unanswered += 1
                unans.append(f'{c["name"]} on "{p["title"][:60]}"')
    if not reached:
        return None
    return {"total": total, "new": new, "unanswered": unanswered, "list": unans[:5]}
cm = safe(comments, None)

# ---------- 7. Trends (Google Trends daily searches) ----------
FIT = re.compile(r"\b(gym|workout|fitness|protein|creatine|diet|weight|fat|muscle|calorie|run|running|marathon|walk|yoga|pilates|"
                 r"keto|fasting|ozempic|wegovy|mounjaro|glp|supplement|vitamin|sleep|cardio|hiit|strength|nutrition|health|"
                 r"exercise|steps|hyrox|bodybuilding|trek|hike|everest)\b", re.I)
def trends():
    found, seen = [], set()
    for geo in ("US", "GB", "AU", "CA"):
        try:
            _, xml_ = get(f"https://trends.google.com/trending/rss?geo={geo}")
            for item in ET.fromstring(xml_).iter("item"):
                t = (item.findtext("title") or "").strip()
                if t and FIT.search(t) and t.lower() not in seen:
                    seen.add(t.lower())
                    found.append(f"{t} ({geo})")
        except Exception:
            continue
    return found[:8]
trend_list = safe(trends, [])

# Evergreen, high-paying-country ideas; the report only suggests ones not already on the blog.
IDEAS = [
    ("high-protein-indian-vegetarian-meal-plan", "High-protein Indian vegetarian meal plan", "Huge US/UK/Canada search demand from South Asian vegetarians."),
    ("south-asian-bmi-and-waist-size", "South Asian BMI and waist size: why the cut-offs are lower", "Health topic with high ad rates; fits the ideal-weight calculator."),
    ("prediabetes-exercise-plan", "Exercise plan for prediabetes", "High-RPM health search; South Asians are at higher risk."),
    ("roti-vs-rice-for-weight-loss", "Roti vs rice for weight loss", "Common search from Nepali and Indian readers abroad; links to the food chart."),
    ("best-time-to-take-creatine", "Best time to take creatine", "Large global search volume; links to the creatine guides."),
    ("how-to-lose-10-kg", "How to lose 10 kg safely: a realistic plan", "Very high search volume in English-speaking countries."),
    ("protein-for-vegetarians-without-supplements", "Protein for vegetarians without supplements", "Strong demand in the UK, US and Gulf."),
    ("walking-vs-running-for-weight-loss", "Walking vs running for weight loss", "Evergreen, high search volume in the US/UK/Australia."),
    ("strength-training-for-runners", "Strength training for runners", "Popular with US/UK/Australian readers; fits the 5K and hybrid posts."),
    ("ramadan-and-fasting-workouts", "How to train while fasting", "Gulf and UK audiences; seasonal spikes."),
    ("dal-protein-per-cup", "How much protein is in dal?", "Food-chart traffic; South Asian diaspora searches."),
    ("gym-workout-for-shift-workers", "Gym workouts for night-shift workers", "Nurses and workers abroad (UK, Australia, Gulf)."),
]
slugs = {p["slug"] for p in posts}
titles = " ".join(p["title"].lower() for p in posts)
def is_new(slug, title):
    key = [w for w in re.findall(r"[a-z]+", title.lower()) if len(w) > 4][:3]
    return slug not in slugs and not all(k in titles for k in key)
idea_pick = [i for i in IDEAS if is_new(i[0], i[1])][:3]

# ---------- 8. AdSense readiness ----------
need = (site or {}).get("need", {})
checks = [
    ("Custom domain on HTTPS", "Done" if (livec or {}).get("/") == 200 else "Check: homepage did not load"),
    (f"30+ original live posts (now {len(live)})", "Done" if len(live) >= 30 else "Not yet"),
    ("About, Contact, Privacy and Editorial policy pages", "Done" if need and all(need.values()) else "Not yet: " + ", ".join(k for k, v in need.items() if not v) if need else "Not checked"),
    ("No broken internal links", "Done" if site.get("ok") and site.get("broken_n") == 0 else (f"{site.get('broken_n')} broken links" if site.get("ok") else "Not checked (build failed)")),
    (f"Thin posts under 600 words: {len(short_live)}", "Done" if not short_live else "Improve: " + ", ".join(p["slug"] for p in short_live[:4])),
    ("Pages indexed in Google", "Owner action: check Search Console > Pages"),
    ("Applied in AdSense", "Done" if ADSENSE_CLIENT else f"Owner action: apply around {ADSENSE_APPLY:%d %b %Y} ({(ADSENSE_APPLY - TODAY).days} days)"),
    ("ADSENSE_CLIENT set and ads.txt live", "Done" if ADSENSE_CLIENT and (livec or {}).get("ads_txt") else "After approval: paste the ca-pub ID into ADSENSE_CLIENT"),
]

# ---------- 9. Actions for the owner ----------
actions = []
if runway_weeks < 3:
    actions.append(f"Only {runway_weeks:.1f} weeks of posts are scheduled (last one {last_sched}). Add new posts so publishing doesn't stop.")
if health and any(v["latest"] != "success" for v in health.values()):
    actions.append("A GitHub Actions workflow is failing right now. Open the Actions tab and check the latest red run.")
if cm and cm["unanswered"]:
    actions.append(f"Reply to {cm['unanswered']} unanswered comment(s) on your comments admin page ({COMMENTS_API}/admin).")
if not ADSENSE_CLIENT and TODAY >= ADSENSE_APPLY - dt.timedelta(days=7):
    actions.append("It's time to apply for Google AdSense (adsense.google.com) with apexfitnesscentre.shop.")
if short_live:
    actions.append(f"Expand {len(short_live)} short post(s) to 700+ words before AdSense review.")
if not NEWSLETTER:
    actions.append("Create a free Kit (kit.com) form so the email sign-up box can switch on.")
actions += ["Post 3 Facebook and 3 Pinterest posts linking to this week's articles.",
            "Send this week's Search Console > Performance (last 7 days) numbers so traffic can be tracked.",
            "Get one backlink: answer a journalist on Qwoted/Featured.com or pitch a Nepali news site."]
actions = actions[:3]

# ---------- 10. Write the report ----------
rng = f"{WEEK_AGO + dt.timedelta(days=1):%d %b} – {TODAY:%d %b %Y}"
L = []
def sec(t): L.append(f"\n## {t}\n")
top = actions[0] if actions else "Keep publishing and sharing."
L.append(f"# Apex weekly report – {rng}\n")
L.append(f"**Top line:** {len(this_week)} new post(s) went live this week; {len(live)} live in total. Most important: {top}")
sec("This week")
L += [f"- {p['date']:%a %d %b}: {p['title']}" for p in this_week] or ["- No new posts went live."]
if health is None:
    L.append("- GitHub Actions: could not be checked.")
else:
    broken_now = {k: v for k, v in health.items() if v["latest"] != "success"}
    fixed = {k: v for k, v in health.items() if v["fail"] and v["latest"] == "success"}
    if not broken_now and not fixed:
        L.append("- GitHub Actions: all runs succeeded.")
    if broken_now:
        L.append("- GitHub Actions FAILING now: " + "; ".join(broken_now))
    if fixed:
        L.append("- GitHub Actions: " + "; ".join(f"{k} had {v['fail']} failed run(s) but the latest run succeeded" for k, v in fixed.items()) + ".")
if cm is None:
    L.append("- Comments: not set up or not reachable.")
else:
    L.append(f"- Comments: {cm['new']} new this week, {cm['total']} in total, {cm['unanswered']} without a reply from you.")
    L += [f"  - {x}" for x in cm["list"]]
sec("Next week")
L += [f"- {p['date']:%a %d %b}: {p['title']}" for p in next_week] or ["- Nothing scheduled."]
L.append(f"- Content runway: {len(scheduled)} posts scheduled, last one on {last_sched or 'n/a'} (about {runway_weeks:.1f} weeks)." + (" **Add more posts soon.**" if runway_weeks < 3 else ""))
sec("Site health")
if site.get("ok"):
    L.append(f"- Site builds fine: {site['pages']} pages. Broken internal links: {site['broken_n']}.")
    L += [f"  - {b}" for b in site["broken"][:5]]
else:
    L.append(f"- Build check failed: {site.get('error', '')[:200]}")
if livec:
    L.append("- Live pages: " + ", ".join(f"{k} {v}" for k, v in livec.items() if k.startswith("/")) + f". Sitemap URLs: {livec.get('sitemap_urls')}.")
sec("Trending now (Google Trends, US/UK/Australia/Canada)")
L += [f"- {t}" for t in trend_list] or ["- No fitness or health topics in today's top trending searches."]
L.append("\n**Post ideas not yet on the blog:**")
L += [f"- **{t}**: {why}" for _, t, why in idea_pick]
sec("AdSense readiness")
L += [f"- {name}: {status}" for name, status in checks]
sec("Goal tracker: USD 1,000/month from AdSense")
stage = "Stage 1: build content and get indexed (AdSense not applied yet)" if not ADSENSE_CLIENT else "Stage 2: AdSense live, grow traffic"
L += [f"- Current stage: {stage}.",
      "- Next milestones: AdSense approval → 1,000 sessions/month (Journey by Mediavine) → 25,000 pageviews/month with 50%+ US/UK/CA/AU/NZ traffic (Raptive) → about 50,000+ pageviews/month for ~USD 1,000.",
      "- Visitor and earnings numbers are not read automatically. Check Search Console > Performance and GA4 > Reports > Acquisition each week."]
sec("Top 3 actions this week")
L += [f"{i}. {a}" for i, a in enumerate(actions, 1)]
L.append("\n_Automatic report from GitHub Actions (repo: " + REPO + "). It runs every Sunday morning, Nepal time._")
md = "\n".join(L)

def md_to_html(s):
    out, in_list = [], False
    for line in s.split("\n"):
        t = html.escape(line)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"_(.+?)_$", r"<i>\1</i>", t)
        if line.startswith("# "):
            out.append(f"<h1 style='font-size:20px;color:#141416'>{t[2:]}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2 style='font-size:16px;color:#c8102e;margin:18px 0 6px'>{t[3:]}</h2>")
        elif re.match(r"^\s*- ", line) or re.match(r"^\d+\. ", line):
            ind = "padding-left:18px;" if line.startswith("  ") else ""
            out.append(f"<div style='{ind}margin:3px 0'>• {re.sub(r'^\s*(- |\d+\. )', '', t)}</div>")
        elif line.strip():
            out.append(f"<p style='margin:6px 0'>{t}</p>")
    return ("<div style='font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.5;color:#141416;max-width:640px'>"
            + "\n".join(out) + "</div>")

open("report.md", "w", encoding="utf-8").write(md)
open("report.html", "w", encoding="utf-8").write(md_to_html(md))
open("report_subject.txt", "w", encoding="utf-8").write(f"Apex weekly report – {rng}")
print(md)
