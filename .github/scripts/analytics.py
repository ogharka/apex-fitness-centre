"""Reads real traffic numbers for the weekly report.

Google Analytics 4 (views, visits, visitors, countries, sources, top pages) and
Search Console (Google searches: clicks, impressions, queries). It needs two GitHub secrets:
  GOOGLE_SA_JSON  - the JSON key of a Google Cloud service account
  GA_PROPERTY_ID  - the GA4 property number (Admin > Property details), not the G-... ID
The service account must be added as Viewer in GA4 and as a user in Search Console.
If they are missing, fetch() returns None and the report says how to connect.
"""
import datetime as dt, json, os, sys, urllib.parse, urllib.request

GA_URL = "https://analyticsdata.googleapis.com/v1beta/properties/{pid}:runReport"
GSC_URL = "https://searchconsole.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
GSC_SITES = ["sc-domain:apexfitnesscentre.shop", "https://apexfitnesscentre.shop/"]
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly", "https://www.googleapis.com/auth/webmasters.readonly"]

TIER1 = {"United States", "United Kingdom", "Canada", "Australia", "New Zealand", "Ireland"}
GULF = {"United Arab Emirates", "Qatar", "Saudi Arabia", "Kuwait", "Oman", "Bahrain"}


def _token():
    raw = os.environ.get("GOOGLE_SA_JSON", "").strip()
    if not raw:
        return None
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    creds.refresh(Request())
    return creds.token


def _post(url, body, token):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def _ga(token, pid, start, end, dims=(), mets=("screenPageViews",), order=None, limit=10, filt=None):
    body = {"dateRanges": [{"startDate": str(start), "endDate": str(end)}],
            "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets], "limit": limit}
    if order:
        body["orderBys"] = [{"metric": {"metricName": order}, "desc": True}] if order in mets else [{"dimension": {"dimensionName": order}}]
    if filt:
        body["dimensionFilter"] = filt
    res = _post(GA_URL.format(pid=pid), body, token)
    rows = []
    for r in res.get("rows", []):
        row = {d: v["value"] for d, v in zip(dims, r.get("dimensionValues", []))}
        for m, v in zip(mets, r.get("metricValues", [])):
            row[m] = float(v["value"])
        rows.append(row)
    return rows


def _gsc(token, start, end, dims, limit=10):
    last = None
    for site in GSC_SITES:
        try:
            res = _post(GSC_URL.format(site=urllib.parse.quote(site, safe="")),
                        {"startDate": str(start), "endDate": str(end), "dimensions": dims, "rowLimit": limit}, token)
            return [dict(zip(dims, r.get("keys", [])), clicks=r["clicks"], impressions=r["impressions"],
                         ctr=r["ctr"], position=r["position"]) for r in res.get("rows", [])]
        except Exception as e:
            last = e
    raise last


def fetch(today):
    """Return a dict of real numbers, or None if not connected. Errors are reported in d['errors']."""
    pid = os.environ.get("GA_PROPERTY_ID", "").strip()
    token = _token()
    if not token:
        return None
    d = {"errors": []}
    end, start = today - dt.timedelta(days=1), today - dt.timedelta(days=7)
    pend, pstart = today - dt.timedelta(days=8), today - dt.timedelta(days=14)
    d["range"] = (start, end)
    KPI = ("screenPageViews", "sessions", "totalUsers", "newUsers", "userEngagementDuration", "engagementRate")

    def ga_part(name, fn):
        try:
            d[name] = fn()
        except Exception as e:
            d["errors"].append(f"Google Analytics ({name}): {str(e)[:160]}")
            print("warn GA", name, e, file=sys.stderr)

    if pid:
        zero = {m: 0.0 for m in KPI}
        ga_part("kpi", lambda: (_ga(token, pid, start, end, (), KPI, limit=1) or [zero])[0])
        ga_part("kpi_prev", lambda: (_ga(token, pid, pstart, pend, (), KPI, limit=1) or [zero])[0])
        ga_part("daily", lambda: _ga(token, pid, pstart, end, ("date",), ("screenPageViews", "sessions"), order="date", limit=20))
        ga_part("countries", lambda: _ga(token, pid, start, end, ("country",), ("screenPageViews", "sessions", "totalUsers"), order="screenPageViews", limit=12))
        ga_part("channels", lambda: _ga(token, pid, start, end, ("sessionDefaultChannelGroup",), ("sessions", "screenPageViews"), order="sessions", limit=8))
        ga_part("sources", lambda: _ga(token, pid, start, end, ("sessionSource",), ("sessions",), order="sessions", limit=10))
        ga_part("pages", lambda: _ga(token, pid, start, end, ("pagePath", "pageTitle"), ("screenPageViews", "userEngagementDuration"), order="screenPageViews", limit=10))
        ga_part("devices", lambda: _ga(token, pid, start, end, ("deviceCategory",), ("sessions",), order="sessions", limit=5))
        ga_part("month", lambda: (_ga(token, pid, today - dt.timedelta(days=28), end, (), ("screenPageViews", "sessions"), limit=1) or [{}])[0])
        ga_part("month_countries", lambda: _ga(token, pid, today - dt.timedelta(days=28), end, ("country",), ("screenPageViews",), order="screenPageViews", limit=200))
    else:
        d["errors"].append("GA_PROPERTY_ID secret is missing, so Google Analytics numbers were skipped.")

    # Search Console data arrives 2-3 days late, so use the latest complete 7 days.
    gend = today - dt.timedelta(days=3)
    gstart, gpend, gpstart = gend - dt.timedelta(days=6), gend - dt.timedelta(days=7), gend - dt.timedelta(days=13)
    d["gsc_range"] = (gstart, gend)
    try:
        tot = _gsc(token, gstart, gend, ["date"], 10)
        ptot = _gsc(token, gpstart, gpend, ["date"], 10)
        def summ(rows):
            c, i = sum(r["clicks"] for r in rows), sum(r["impressions"] for r in rows)
            pos = sum(r["position"] * r["impressions"] for r in rows) / i if i else 0
            return {"clicks": c, "impressions": i, "ctr": c / i if i else 0, "position": pos}
        d["gsc"], d["gsc_prev"] = summ(tot), summ(ptot)
        d["gsc_queries"] = _gsc(token, gstart, gend, ["query"], 25)
        d["gsc_pages"] = _gsc(token, gstart, gend, ["page"], 25)
        d["gsc_countries"] = _gsc(token, gstart, gend, ["country"], 8)
    except Exception as e:
        d["errors"].append(f"Search Console: {str(e)[:160]}")
        print("warn GSC", e, file=sys.stderr)
    return d


def sample(today):
    """Example numbers for previewing the PDF design only (clearly marked in the PDF)."""
    end, start = today - dt.timedelta(days=1), today - dt.timedelta(days=7)
    import random
    random.seed(4)
    daily = []
    for i in range(14):
        day = today - dt.timedelta(days=14 - i)
        pv = int((40 if i < 7 else 62) * random.uniform(.8, 1.25))
        daily.append({"date": day.strftime("%Y%m%d"), "screenPageViews": pv, "sessions": int(pv * .7)})
    return {"errors": [], "sample": True, "range": (start, end), "gsc_range": (today - dt.timedelta(days=9), today - dt.timedelta(days=3)),
            "kpi": {"screenPageViews": 431, "sessions": 302, "totalUsers": 251, "newUsers": 214, "userEngagementDuration": 302 * 58, "engagementRate": .61},
            "kpi_prev": {"screenPageViews": 296, "sessions": 214, "totalUsers": 180, "newUsers": 160, "userEngagementDuration": 214 * 51, "engagementRate": .57},
            "daily": daily,
            "countries": [{"country": c, "screenPageViews": v, "sessions": int(v * .7), "totalUsers": int(v * .6)} for c, v in
                          [("Nepal", 214), ("United States", 61), ("India", 48), ("Australia", 37), ("United Kingdom", 24), ("United Arab Emirates", 15), ("Canada", 12), ("Qatar", 8)]],
            "channels": [{"sessionDefaultChannelGroup": c, "sessions": v} for c, v in [("Organic Search", 118), ("Direct", 84), ("Organic Social", 71), ("Referral", 19), ("Unassigned", 10)]],
            "sources": [{"sessionSource": s, "sessions": v} for s, v in [("google", 112), ("(direct)", 84), ("facebook.com", 41), ("pinterest.com", 22), ("bing", 6)]],
            "pages": [{"pagePath": p, "pageTitle": t, "screenPageViews": v, "userEngagementDuration": v * s} for p, t, v, s in [
                ("/food/momo-calories/", "Momo Calories", 58, 64), ("/", "Apex Fitness Centre", 51, 30), ("/blog/creatine-for-women/", "Creatine for Women", 39, 95),
                ("/calculators/protein-calculator/", "Protein Calculator", 33, 70), ("/gym/", "Gym in Urlabari", 27, 41), ("/blog/zone-2-training/", "Zone 2 Training", 22, 88)]],
            "devices": [{"deviceCategory": "mobile", "sessions": 241}, {"deviceCategory": "desktop", "sessions": 55}, {"deviceCategory": "tablet", "sessions": 6}],
            "month": {"screenPageViews": 1180, "sessions": 840},
            "month_countries": [{"country": "Nepal", "screenPageViews": 640}, {"country": "United States", "screenPageViews": 170}, {"country": "Australia", "screenPageViews": 95},
                                {"country": "United Kingdom", "screenPageViews": 70}, {"country": "India", "screenPageViews": 140}, {"country": "United Arab Emirates", "screenPageViews": 65}],
            "gsc": {"clicks": 96, "impressions": 4210, "ctr": 96 / 4210, "position": 21.4},
            "gsc_prev": {"clicks": 61, "impressions": 2890, "ctr": 61 / 2890, "position": 24.9},
            "gsc_queries": [{"query": q, "clicks": c, "impressions": i, "ctr": c / i, "position": p} for q, c, i, p in [
                ("momo calories", 21, 380, 6.2), ("creatine for women nepal", 9, 140, 4.1), ("gym in urlabari", 8, 30, 1.3),
                ("zone 2 heart rate", 2, 410, 14.8), ("how much protein do i need", 1, 520, 18.2), ("dal bhat calories", 6, 190, 9.4), ("hyrox weights", 0, 260, 22.5)]],
            "gsc_pages": [{"page": "https://apexfitnesscentre.shop" + p, "clicks": c, "impressions": i, "ctr": c / i, "position": pos} for p, c, i, pos in [
                ("/food/momo-calories/", 24, 610, 7.1), ("/blog/zone-2-training/", 3, 640, 13.9), ("/calculators/protein-calculator/", 4, 590, 16.3)]],
            "gsc_countries": []}
