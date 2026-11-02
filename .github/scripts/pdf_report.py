"""Turns the weekly numbers into a designed PDF (rendered with Chromium via Playwright)."""
import base64, datetime as dt, html, os

from analytics import TIER1, GULF

RED, INK, MUTED, LINE, GREY, SOFT = "#c8102e", "#141416", "#5f6368", "#e6e6e9", "#9aa0a6", "#f6f6f7"
# Rough AdSense earnings per 1,000 page views by audience. Real rates vary a lot by topic and season.
RPM = {"tier1": 10.0, "gulf": 5.0, "other": 1.0}
GOAL = 1000.0


def e(x):
    return html.escape(str(x))


def n(x):
    return f"{int(round(x or 0)):,}"


def pct(a, b):
    if not b:
        return None
    return (a - b) / b * 100


def delta(a, b, good_up=True):
    p = pct(a, b)
    if p is None:
        return "<span class='dl'>new</span>"
    up = p >= 0
    cls = "up" if up == good_up else "down"
    return f"<span class='dl {cls}'>{'▲' if up else '▼'} {abs(p):.0f}% vs last week</span>"


def secs(s):
    s = int(round(s or 0))
    return f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"


def short(t, lim=58):
    t = t.split(" (")[0]
    return t if len(t) <= lim else t[:lim].rsplit(" ", 1)[0] + "…"


def bucket(country):
    return "tier1" if country in TIER1 else "gulf" if country in GULF else "other"


def money(ga):
    """Rough monthly earnings estimate from the last 28 days, using the RPM assumptions above."""
    rows = (ga or {}).get("month_countries") or []
    if not rows:
        return None
    by = {"tier1": 0, "gulf": 0, "other": 0}
    for r in rows:
        by[bucket(r["country"])] += r["screenPageViews"]
    total = sum(by.values()) or 1
    scale = 30 / 28
    est = sum(by[k] * RPM[k] / 1000 for k in by) * scale
    blended = est / (total * scale) * 1000
    return {"by": by, "total": total * scale, "est": est, "blended": blended,
            "need_views": round(GOAL / blended * 1000, -3) if blended else None,
            "need_views_tier1": GOAL / RPM["tier1"] * 1000, "tier1_share": by["tier1"] / total}


# ---------------- charts (inline SVG) ----------------
def line_chart(daily):
    pts = sorted(daily, key=lambda r: r["date"])
    if len(pts) < 2:
        return ""
    prev, cur = pts[:-7][-7:], pts[-7:]
    W, H, L, R, T, B = 640, 210, 40, 92, 14, 30
    mx = max([r["screenPageViews"] for r in pts] + [5])
    step = 10 ** max(0, len(str(int(mx))) - 1)
    top = ((int(mx) // step) + 1) * step
    xs = lambda i: L + i * (W - L - R) / 6
    ys = lambda v: T + (H - T - B) * (1 - v / top)
    g = []
    for k in range(5):
        v = top * k / 4
        g.append(f"<line x1='{L}' x2='{W - R}' y1='{ys(v):.1f}' y2='{ys(v):.1f}' stroke='{LINE}' stroke-width='1'/>"
                 f"<text x='{L - 6}' y='{ys(v) + 4:.1f}' text-anchor='end' class='ax'>{n(v)}</text>")
    for i, r in enumerate(cur):
        d = dt.datetime.strptime(r["date"], "%Y%m%d")
        g.append(f"<text x='{xs(i):.1f}' y='{H - 8}' text-anchor='middle' class='ax'>{d:%a %d}</text>")

    def path(rows, col, dash=""):
        p = " ".join(f"{'M' if i == 0 else 'L'}{xs(i):.1f},{ys(r['screenPageViews']):.1f}" for i, r in enumerate(rows))
        dots = "".join(f"<circle cx='{xs(i):.1f}' cy='{ys(r['screenPageViews']):.1f}' r='4' fill='{col}' stroke='#fff' stroke-width='2'/>" for i, r in enumerate(rows))
        return f"<path d='{p}' fill='none' stroke='{col}' stroke-width='2' {dash} stroke-linejoin='round' stroke-linecap='round'/>" + dots

    yc = ys(cur[-1]["screenPageViews"]) + 4
    if len(prev) == 7:
        yp = ys(prev[-1]["screenPageViews"]) + 4
        if abs(yp - yc) < 13:  # keep the two end labels apart
            mid = (yp + yc) / 2
            yc, yp = (mid - 6.5, mid + 6.5) if yc <= yp else (mid + 6.5, mid - 6.5)
        g.append(path(prev, GREY, "stroke-dasharray='5 4'"))
        g.append(f"<text x='{W - R + 10}' y='{yp:.1f}' class='lb' fill='{MUTED}'>Last week</text>")
    g.append(path(cur, RED))
    g.append(f"<text x='{W - R + 10}' y='{yc:.1f}' class='lb b'>This week</text>")
    return f"<svg viewBox='0 0 {W} {H}' width='100%' role='img' aria-label='Daily page views'>{''.join(g)}</svg>"


def hbars(rows, label, value, color_fn=None, fmt=n, max_rows=8):
    rows = rows[:max_rows]
    if not rows:
        return "<p class='muted'>No data yet.</p>"
    mx = max(r[value] for r in rows) or 1
    out = []
    for r in rows:
        w = max(1.5, r[value] / mx * 100)
        col = color_fn(r) if color_fn else INK
        out.append(f"<div class='hb'><span class='hl'>{e(r[label])}</span><span class='ht'><span class='hf' style='width:{w:.1f}%;background:{col}'></span></span>"
                   f"<span class='hv'>{fmt(r[value])}</span></div>")
    return "".join(out)


# ---------------- strategy engine (rules from real numbers) ----------------
def strategies(ga, ctx):
    S = []
    if not ga or not ga.get("kpi"):
        S.append(("Connect Google Analytics and Search Console to this report",
                  "Without real numbers the plan below is general. Follow the setup steps sent with this report (about 10 minutes).", ""))
    k, kp = (ga or {}).get("kpi") or {}, (ga or {}).get("kpi_prev") or {}
    m = money(ga)
    countries = (ga or {}).get("countries") or []
    if m and m["tier1_share"] < 0.5:
        S.append((f"Win more readers from the US, UK, Canada and Australia (now {m['tier1_share'] * 100:.0f}% of views)",
                  f"A view from these countries earns roughly 10x a view from Nepal or India. At your current mix you would need about {n(m['need_views'])} views a month for USD 1,000; with mostly high-paying readers it would be about {n(m['need_views_tier1'])}.",
                  "Write for Nepali, Indian and other South Asian readers living abroad (food calories, meal plans with Coles/Walmart/Tesco foods, visas and gym jobs). Share pins on Pinterest, where most users are in the US."))
    gq = (ga or {}).get("gsc_queries") or []
    near = [q for q in gq if 4.5 <= q["position"] <= 20 and q["impressions"] >= 20]
    near.sort(key=lambda q: -q["impressions"])
    if near:
        S.append(("Push these Google searches onto page 1 (you are close)",
                  "Your pages already appear for these searches but sit lower on Google, where few people click:",
                  " · ".join(f"“{q['query']}” (position {q['position']:.0f}, {n(q['impressions'])} impressions)" for q in near[:5])
                  + ". Add a clear section or FAQ that answers each search, use the words in a heading, and link to the page from 2-3 related posts."))
    gp = (ga or {}).get("gsc_pages") or []
    lowctr = [p for p in gp if p["impressions"] >= 100 and p["ctr"] < 0.02]
    if lowctr:
        S.append(("Rewrite titles that Google shows but people don't click",
                  "These pages get seen in Google but under 2% of people click:",
                  " · ".join(f"{p['page'].replace('https://apexfitnesscentre.shop', '')} ({n(p['impressions'])} seen, {p['ctr'] * 100:.1f}% clicked)" for p in lowctr[:4])
                  + ". Put a number, the year or a clear benefit in the title (for example “Momo Calories: 10 Pieces = 394 kcal (Steamed vs Fried)”)."))
    pages = (ga or {}).get("pages") or []
    blogtop = [p for p in pages if p["pagePath"] not in ("/", "/gym/", "/blog/")]
    if blogtop:
        t = blogtop[0]
        S.append((f"Build on your best page: {t['pageTitle'][:60]}",
                  f"It had {n(t['screenPageViews'])} views this week, the most of any article.",
                  "Write 2 follow-up posts on the same topic, link them both ways, and make 3 new Pinterest pins for it."))
    ch = {r["sessionDefaultChannelGroup"]: r["sessions"] for r in (ga or {}).get("channels") or []}
    tot = sum(ch.values())
    if tot:
        social = ch.get("Organic Social", 0) / tot
        search = ch.get("Organic Search", 0) / tot
        src = {r["sessionSource"]: r["sessions"] for r in (ga or {}).get("sources") or []}
        pin = sum(v for s, v in src.items() if "pinterest" in s)
        if pin / tot < 0.10:
            S.append(("Use Pinterest every day",
                      f"Pinterest sent {n(pin)} visits this week ({pin / tot * 100:.0f}%). It is the fastest free way to reach US readers while Google trusts a new site.",
                      "Pin 3-5 times a day: one new pin per post and fresh pins for the food and calculator pages. Use tall 1000×1500 images with big text."))
        if search < 0.3:
            S.append(("Keep publishing; Google search is still small",
                      f"Only {search * 100:.0f}% of visits came from Google. New sites usually take 3-6 months to rank.",
                      "Keep 3-5 posts a week, and request indexing for each new post in Search Console > URL inspection."))
        if social < 0.1 and pin / tot >= 0.10:
            S.append(("Share every new post on Facebook", f"Social media sent {social * 100:.0f}% of visits.", "Post daily at 7 PM Nepal time and reply to comments in the first hour."))
    if k.get("sessions"):
        avg = k["userEngagementDuration"] / max(k.get("totalUsers") or 1, 1)
        if avg < 45:
            S.append(("Keep people reading longer", f"Average time on site is {secs(avg)}. Longer visits mean more ads seen.",
                      "Answer the question in the first 2 lines, add a table or image near the top, and link to a calculator in every post."))
    if kp.get("screenPageViews") and k.get("screenPageViews") is not None and pct(k["screenPageViews"], kp["screenPageViews"]) < -20:
        S.append(("Views dropped this week: find out why", f"Views fell {abs(pct(k['screenPageViews'], kp['screenPageViews'])):.0f}% from last week.",
                  "Check Search Console > Performance > Pages, compare with last week, and see which page lost clicks."))
    S.append(("Get 2 backlinks this month", "Links from other sites are what make Google trust a new site.",
              "Answer journalist requests on Qwoted or Featured.com, and pitch a Nepali news site an article like “What Nepalis really eat: calories in dal bhat, momo and chowmein”."))
    if ctx.get("runway_weeks", 99) < 3:
        S.insert(0, ("Schedule more posts now", f"Only {ctx['runway_weeks']:.1f} weeks of posts are left.", "Add at least 10 posts so publishing doesn't stop."))
    return S[:6]


# ---------------- page ----------------
CSS = f"""
@page{{size:A4;margin:14mm 13mm 14mm}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:'Helvetica Neue',Arial,'Liberation Sans',sans-serif;color:{INK};font-size:10.5pt;line-height:1.45;background:#fff}}
.hdr{{display:flex;align-items:center;gap:12px;border-bottom:3px solid {RED};padding-bottom:10px;margin-bottom:14px}}
.hdr img{{width:40px;height:40px;border-radius:8px}}
.hdr h1{{font-size:17pt;margin:0;letter-spacing:-.01em}} .hdr .sub{{color:{MUTED};font-size:9.5pt}}
.hdr .rt{{margin-left:auto;text-align:right;font-size:9pt;color:{MUTED}}}
h2{{font-size:12.5pt;margin:18px 0 8px;display:flex;align-items:center;gap:8px}}
h2:before{{content:'';width:4px;height:15px;background:{RED};border-radius:2px}}
.muted{{color:{MUTED}}} .small{{font-size:9pt}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}
.kpi{{border:1px solid {LINE};border-radius:10px;padding:10px 12px}}
.kpi .l{{font-size:8.5pt;color:{MUTED};text-transform:uppercase;letter-spacing:.04em}}
.kpi .v{{font-size:20pt;font-weight:700;margin:2px 0;letter-spacing:-.02em}}
.dl{{font-size:8.5pt;color:{MUTED}}} .dl.up{{color:#137333}} .dl.down{{color:#b3261e}}
.card{{border:1px solid {LINE};border-radius:10px;padding:10px 12px;break-inside:avoid}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.ax{{font-size:9px;fill:{MUTED}}} .lb{{font-size:10px}} .lb.b{{font-weight:700;fill:{RED}}}
.hb{{display:grid;grid-template-columns:38% 1fr 46px;align-items:center;gap:6px;margin:4px 0;font-size:9.5pt}}
.hl{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.ht{{background:{SOFT};border-radius:4px;height:10px;overflow:hidden}} .hf{{display:block;height:100%;border-radius:0 4px 4px 0}}
.hv{{text-align:right;font-variant-numeric:tabular-nums}}
.leg{{font-size:8.5pt;color:{MUTED};margin-top:6px}} .sw{{display:inline-block;width:9px;height:9px;border-radius:2px;margin:0 4px -1px 0}}
table{{width:100%;border-collapse:collapse;font-size:9.3pt}}
th{{text-align:left;color:{MUTED};font-weight:600;font-size:8.5pt;border-bottom:1px solid {LINE};padding:4px 4px}}
td{{padding:4px 4px;border-bottom:1px solid {SOFT};vertical-align:top}} td.r,th.r{{text-align:right;font-variant-numeric:tabular-nums}}
.strat{{counter-reset:s}} .st{{display:grid;grid-template-columns:28px 1fr;gap:8px;margin:0 0 9px;break-inside:avoid}}
.st .no{{width:24px;height:24px;border-radius:50%;background:{RED};color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:10pt}}
.st b{{display:block}} .st .do{{background:{SOFT};border-radius:6px;padding:5px 8px;margin-top:4px;font-size:9.5pt}}
.bar{{height:14px;background:{SOFT};border-radius:7px;overflow:hidden;margin:6px 0}} .bar span{{display:block;height:100%;background:{RED};border-radius:7px}}
.ok{{color:#137333;font-weight:700}} .todo{{color:#b06000;font-weight:700}}
.note{{border-left:3px solid {RED};background:#fff5f6;padding:8px 10px;border-radius:0 8px 8px 0;font-size:9.5pt}}
.sample{{background:#fff4d6;border:1px solid #f0c36d;padding:6px 10px;border-radius:8px;font-size:9pt;margin-bottom:10px}}
.pb{{break-before:page}} .blk{{break-inside:avoid}} h2{{break-after:avoid}}
.foot{{margin-top:16px;font-size:8pt;color:{MUTED};border-top:1px solid {LINE};padding-top:6px}}
"""


def build_html(ctx, ga):
    logo = ""
    lp = os.path.join(ctx["src"], "assets", "apex-icon-180.png")
    if os.path.exists(lp):
        logo = f"<img src='data:image/png;base64,{base64.b64encode(open(lp, 'rb').read()).decode()}' alt=''>"
    H = [f"<!doctype html><html><head><meta charset='utf-8'><title>{e(ctx['subject'])}</title><style>{CSS}</style></head><body>"]
    H.append(f"<div class='hdr'>{logo}<div><h1>Weekly site report</h1><div class='sub'>apexfitnesscentre.shop · {e(ctx['rng'])}</div></div>"
             f"<div class='rt'>Goal: USD 1,000 a month<br>from AdSense</div></div>")
    if ga and ga.get("sample"):
        H.append("<div class='sample'><b>Example numbers.</b> This preview shows the design only. Your real numbers appear once Google Analytics and Search Console are connected.</div>")

    k, kp = (ga or {}).get("kpi") or {}, (ga or {}).get("kpi_prev") or {}
    if k:
        avg = (k.get("userEngagementDuration") or 0) / max(k.get("totalUsers") or 1, 1)
        pavg = (kp.get("userEngagementDuration") or 0) / max(kp.get("totalUsers") or 1, 1)
        H.append("<div class='kpis'>")
        for lab, v, pv, fmt in [("Page views", k.get("screenPageViews"), kp.get("screenPageViews"), n), ("Visits", k.get("sessions"), kp.get("sessions"), n),
                                ("Visitors", k.get("totalUsers"), kp.get("totalUsers"), n), ("Time per visitor", avg, pavg, secs)]:
            H.append(f"<div class='kpi'><div class='l'>{lab}</div><div class='v'>{fmt(v)}</div>{delta(v or 0, pv or 0)}</div>")
        H.append("</div>")
        nu = k.get("newUsers") or 0
        H.append(f"<p class='small muted' style='margin:6px 2px 0'>{e(ga['range'][0].strftime('%d %b'))} – {e(ga['range'][1].strftime('%d %b'))} (Google Analytics). "
                 f"{n(nu)} new visitors · {(k.get('engagementRate') or 0) * 100:.0f}% of visits were engaged (10+ seconds or 2+ pages).</p>")
        if ga.get("daily"):
            H.append("<h2>Views per day</h2><div class='card'>" + line_chart(ga["daily"]) +
                     f"<div class='leg'><span class='sw' style='background:{RED}'></span>This week &nbsp; <span class='sw' style='background:{GREY}'></span>Last week (dashed)</div></div>")
    else:
        H.append("<div class='note'><b>Views, visits and countries are not connected yet.</b> Add the two Google secrets (GOOGLE_SA_JSON and GA_PROPERTY_ID) "
                 "described in the setup steps, and next week's report will show your real traffic here.</div>")
        for msg in (ga or {}).get("errors", []):
            H.append(f"<p class='small muted'>{e(msg)}</p>")

    if k:
        hi = lambda r: RED if bucket(r["country"]) == "tier1" else ("#e37383" if bucket(r["country"]) == "gulf" else GREY)
        H.append("<div class='two' style='margin-top:4px'>")
        H.append("<div><h2>Where readers are</h2><div class='card'>" + hbars(ga.get("countries") or [], "country", "screenPageViews", hi) +
                 f"<div class='leg'><span class='sw' style='background:{RED}'></span>US, UK, CA, AU, NZ, IE &nbsp;<span class='sw' style='background:#e37383'></span>Gulf &nbsp;"
                 f"<span class='sw' style='background:{GREY}'></span>Other · page views</div></div></div>")
        H.append("<div><h2>How they found you</h2><div class='card'>" + hbars(ga.get("channels") or [], "sessionDefaultChannelGroup", "sessions") +
                 "<div class='leg'>Visits by source</div>")
        src = ga.get("sources") or []
        if src:
            H.append("<p class='small' style='margin:8px 0 0'><b>Top sites:</b> " + ", ".join(f"{e(s['sessionSource'])} {n(s['sessions'])}" for s in src[:6]) + "</p>")
        dev = ga.get("devices") or []
        if dev:
            t = sum(d["sessions"] for d in dev) or 1
            H.append("<p class='small' style='margin:4px 0 0'><b>Devices:</b> " + ", ".join(f"{e(d['deviceCategory'])} {d['sessions'] / t * 100:.0f}%" for d in dev) + "</p>")
        H.append("</div></div></div>")

        pages = ga.get("pages") or []
        if pages:
            H.append("<h2 class='pb'>Most viewed pages</h2><div class='card'><table><tr><th>Page</th><th class='r'>Views</th><th class='r'>Avg time</th></tr>")
            for p in pages[:8]:
                H.append(f"<tr><td>{e(p['pageTitle'][:70])}<div class='small muted'>{e(p['pagePath'])}</div></td><td class='r'>{n(p['screenPageViews'])}</td>"
                         f"<td class='r'>{secs(p['userEngagementDuration'] / max(p['screenPageViews'], 1))}</td></tr>")
            H.append("</table></div>")

    g, gp = (ga or {}).get("gsc"), (ga or {}).get("gsc_prev") or {}
    if g:
        a, b = ga["gsc_range"]
        H.append(f"<h2>Google search</h2><p class='small muted' style='margin:-4px 0 6px'>{a:%d %b} – {b:%d %b} (Search Console data arrives 2-3 days late)</p><div class='kpis'>")
        for lab, v, pv, fmt, up in [("Clicks", g["clicks"], gp.get("clicks"), n, True), ("Times shown", g["impressions"], gp.get("impressions"), n, True),
                                    ("Click rate", g["ctr"] * 100, (gp.get("ctr") or 0) * 100, lambda x: f"{x:.1f}%", True),
                                    ("Avg position", g["position"], gp.get("position"), lambda x: f"{x:.1f}", False)]:
            H.append(f"<div class='kpi'><div class='l'>{lab}</div><div class='v'>{fmt(v)}</div>{delta(v, pv or 0, up)}</div>")
        H.append("</div>")
        q = ga.get("gsc_queries") or []
        if q:
            H.append("<div class='card' style='margin-top:8px'><table><tr><th>What people searched</th><th class='r'>Clicks</th><th class='r'>Shown</th><th class='r'>Position</th></tr>")
            for r in sorted(q, key=lambda r: (-r["clicks"], -r["impressions"]))[:10]:
                H.append(f"<tr><td>{e(r['query'])}</td><td class='r'>{n(r['clicks'])}</td><td class='r'>{n(r['impressions'])}</td><td class='r'>{r['position']:.1f}</td></tr>")
            H.append("</table><div class='leg'>Position 1-10 is page 1 of Google. Lower is better.</div></div>")
    elif ga and not ga.get("sample"):
        H.append("<h2>Google search</h2><p class='small muted'>Search Console could not be read. Check that the service account is added as a user in Search Console.</p>")

    # Strategy
    H.append("<h2 class='pb'>What to do this week to get more views</h2><div class='strat'>")
    for i, (t, why, do) in enumerate(strategies(ga, ctx), 1):
        H.append(f"<div class='st'><div class='no'>{i}</div><div><b>{e(t)}</b><span class='small'>{e(why)}</span>" + (f"<div class='do'>{e(do)}</div>" if do else "") + "</div></div>")
    H.append("</div>")

    # Goal tracker
    m = money(ga)
    H.append("<div class='blk'><h2>Goal tracker: USD 1,000 a month</h2><div class='card'>")
    if m:
        p = min(100, m["est"] / GOAL * 100)
        H.append(f"<div style='display:flex;justify-content:space-between'><span>Last 30 days: <b>{n(m['total'])}</b> page views</span><span>Estimated ad value: <b>USD {m['est']:,.0f}</b> of 1,000</span></div>"
                 f"<div class='bar'><span style='width:{max(p, 1):.1f}%'></span></div>"
                 f"<p class='small' style='margin:4px 0'>At your current country mix, USD 1,000 needs about <b>{n(m['need_views'])} views a month</b>. "
                 f"If most readers were in the US, UK, Canada or Australia it would need about {n(m['need_views_tier1'])}.</p>"
                 f"<p class='small muted' style='margin:2px 0'>Estimate only, before AdSense is live. It assumes about USD {RPM['tier1']:.0f} per 1,000 views from US/UK/CA/AU/NZ/IE, "
                 f"USD {RPM['gulf']:.0f} from the Gulf and USD {RPM['other']:.0f} from elsewhere. Real AdSense rates vary a lot.</p>")
    else:
        H.append("<p class='small'>Connect Google Analytics to track progress. Rough guide: USD 1,000 a month needs about 100,000 page views a month from the US, UK, Canada and Australia, or several times more from Nepal and India.</p>")
    stage = "Stage 1: build content and get indexed (AdSense not applied yet)" if not ctx["adsense_live"] else "Stage 2: AdSense live, grow traffic"
    H.append(f"<p class='small' style='margin:6px 0 0'><b>Now:</b> {e(stage)}. <b>Next:</b> AdSense approval → 1,000 visits a month (Journey by Mediavine) → 25,000 views a month with 50%+ from US/UK/CA/AU/NZ (Raptive).</p></div></div>")

    # Content + site
    H.append("<div class='two blk'><div><h2>Posts</h2><div class='card small'>")
    H.append(f"<b>Went live this week ({len(ctx['this_week'])})</b><br>" + ("<br>".join(f"{p['date']:%a %d} · {e(short(p['title']))}" for p in ctx["this_week"][:6]) or "None"))
    if len(ctx["this_week"]) > 6:
        H.append(f"<br><span class='muted'>+{len(ctx['this_week']) - 6} more</span>")
    H.append(f"<br><br><b>Next week ({len(ctx['next_week'])})</b><br>" + ("<br>".join(f"{p['date']:%a %d} · {e(short(p['title']))}" for p in ctx["next_week"][:6]) or "Nothing scheduled"))
    H.append(f"<br><br>{ctx['live_n']} live posts · {ctx['sched_n']} scheduled, last on {ctx['last_sched']} ({ctx['runway_weeks']:.1f} weeks)</div></div>")
    H.append("<div><h2>Site health</h2><div class='card small'>")
    for line in ctx["health_lines"]:
        H.append(f"<div style='margin:2px 0'>{e(line)}</div>")
    H.append("</div><h2>AdSense readiness</h2><div class='card small'>")
    for name, status in ctx["checks"]:
        cls = "ok" if status.startswith("Done") else "todo"
        H.append(f"<div style='margin:3px 0'><span class='{cls}'>{'✓' if cls == 'ok' else '•'}</span> {e(name)}: <span class='muted'>{e(status)}</span></div>")
    H.append("</div></div></div>")

    if ctx.get("ideas"):
        H.append("<div class='blk'><h2>New post ideas</h2><div class='card small'>" + "".join(f"<div style='margin:3px 0'><b>{e(t)}</b> – {e(w)}</div>" for _, t, w in ctx["ideas"]))
        if ctx.get("trends"):
            H.append("<div class='muted' style='margin-top:6px'>Trending in Google today: " + e(", ".join(ctx["trends"][:6])) + "</div>")
        H.append("</div></div>")
    H.append(f"<div class='foot'>Automatic report from GitHub Actions, every Sunday 8:37 AM Nepal time. Traffic numbers come from Google Analytics and Search Console; nothing is estimated except the clearly marked ad value.</div>")
    H.append("</body></html>")
    return "".join(H)


def write_pdf(ctx, ga, path):
    page_html = build_html(ctx, ga)
    with open(path.replace(".pdf", "_pdf.html"), "w", encoding="utf-8") as f:
        f.write(page_html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(page_html, wait_until="load")
        pg.pdf(path=path, format="A4", print_background=True, margin={"top": "14mm", "bottom": "14mm", "left": "13mm", "right": "13mm"})
        b.close()
    return path
