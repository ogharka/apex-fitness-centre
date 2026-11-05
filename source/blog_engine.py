# Blog + AdSense-required pages. Loaded by build.py with exec(), so it shares its helpers
# (head, nav, footer, drawer, tail, crumbs, crumb_html, ld, e, money, card, PRODUCTS, pages, sitemap, BASE, WA).
#
# HOW POSTS WORK: every .md file in source/content/blog/ becomes /blog/<slug>/.
#   - Files starting with "_" are ignored (templates, notes).
#   - "draft: true" keeps a post off the site.
#   - A date in the future keeps it hidden until that day (the site rebuilds every morning).
import datetime as _dt, glob as _glob, markdown as _md

NPT = _dt.timezone(_dt.timedelta(hours=5, minutes=45))
TODAY = _dt.date.fromisoformat(os.environ["BLOG_TODAY"]) if os.environ.get("BLOG_TODAY") else _dt.datetime.now(NPT).date()  # BLOG_TODAY only for testing schedules
REQUIRED = ("title", "description", "date")
# Topics shown as chips on the blog. A post's "category:" should be one of these (any other name still works and gets its own page).
TOPICS = ["Training", "Diet", "Weight loss", "Supplements", "Trekking", "Gyms in Nepal", "Fitness careers", "Competitions", "Influencers and athletes"]
TOPIC_INTRO = {
 "Supplements": "Prices, real vs fake products, what works and what is a waste of money, for buyers in Nepal.",
 "Training": "Workout plans, technique and programming for beginners and experienced lifters.",
 "Diet": "High-protein eating with Nepali food: dal bhat, eggs, chicken, paneer and more.",
 "Weight loss": "Realistic fat loss for Nepali lifestyles, without crash diets: diet plans with Nepali food, walking, training and why the scale stalls.",
 "Gyms in Nepal": "Gym fees, what to look for, and guides to training in cities across Nepal.",
 "Fitness careers": "How to become a trainer in Nepal: courses, certifications, academies and salaries.",
 "Influencers and athletes": "Nepali fitness creators, bodybuilders and powerlifters worth following.",
 "Competitions": "Bodybuilding and powerlifting championships, results and how to compete from Nepal.",
 "Trekking": "How to get fit for a trek in Nepal: training plans for Everest Base Camp, the Annapurna Circuit and other Himalayan routes, from a trainer who lives here.",
}
# Longer hub text shown under a category's post list (only link to live pages).
TOPIC_HUB = {
 "Training": """<section class="abody" style="max-width:760px;margin:8px 0 40px">
<h2>Start here if you are new to the gym</h2>
<p>Most beginners get the best results from a simple plan done consistently: three full-body sessions a week, good technique on a few big lifts, and a little more weight over time. Read these in order.</p>
<ol><li><a href="../why-start-going-to-the-gym/">Why start going to the gym</a></li><li><a href="../beginner-gym-workout-plan-first-3-months/">Beginner gym workout plan for your first 3 months</a></li><li><a href="../how-to-squat-properly/">How to squat properly</a></li><li><a href="../how-to-bench-press-safely/">How to bench press safely</a></li><li><a href="../how-to-deadlift-for-beginners/">How to deadlift for beginners</a></li><li><a href="../muscle-soreness-after-gym/">Muscle soreness after the gym: what is normal</a></li><li><a href="../zone-2-training/">Zone 2 training: easy cardio that works</a></li></ol>
<p>Training at home? Start with the <a href="../home-workout-without-equipment/">home workout without equipment</a>. For your numbers, use the <a href="../../calculators/one-rep-max-calculator/">one-rep max calculator</a>.</p>
<p class="fine">Written by <a href="../../author/suman-limbu/">Suman Limbu</a>, owner and trainer at Apex Fitness Centre in Morang, Nepal.</p>
</section>""",
 "Diet": """<section class="abody" style="max-width:760px;margin:8px 0 40px">
<h2>Eat well with Nepali and South Asian food</h2>
<p>You do not need special foods to eat well. Dal, rice, eggs, chicken, curd and vegetables can cover everything a training body needs, if the portions are right and protein is high enough. Start with these.</p>
<ol><li><a href="../how-much-protein-do-you-need/">How much protein do you need?</a></li><li><a href="../dal-bhat-protein/">How much protein is in dal bhat</a></li><li><a href="../protein-rich-vegetarian-foods-nepal/">Protein-rich vegetarian foods in Nepal</a></li><li><a href="../high-protein-nepali-diet-plan-for-muscle-gain/">High-protein Nepali diet plan for muscle gain</a></li><li><a href="../roti-vs-naan-vs-puri-calories/">Roti vs naan vs puri calories</a></li><li><a href="../how-much-water-should-you-drink/">How much water should you drink?</a></li></ol>
<p>Look up any dish on our <a href="../../food/">food calorie chart</a>, and find your daily target with the <a href="../../calculators/protein-calculator/">protein calculator</a>.</p>
<p class="fine">Written by <a href="../../author/suman-limbu/">Suman Limbu</a>, owner and trainer at Apex Fitness Centre in Morang, Nepal.</p>
</section>""",
 "Weight loss": """<section class="abody" style="max-width:760px;margin:8px 0 40px">
<h2>Lose fat without giving up Nepali food</h2>
<p>Fat loss comes from eating a little less energy than you use, every day, for weeks, while keeping protein high and staying active. Crash diets rarely last. These guides show the steady way.</p>
<ol><li><a href="../weight-loss-diet-plan-nepali-food/">Nepali diet plan for weight loss (7-day meal plan)</a></li><li><a href="../walking-for-weight-loss-steps/">Walking for weight loss: how many steps a day</a></li><li><a href="../how-to-lose-belly-fat/">How to lose belly fat</a></li><li><a href="../body-recomposition-lose-fat-build-muscle/">Body recomposition: lose fat and build muscle</a></li><li><a href="../why-am-i-not-losing-weight/">Why am I not losing weight?</a></li></ol>
<p>Find your calorie target with the <a href="../../calculators/calorie-deficit-calculator/">calorie deficit calculator</a>.</p>
<p class="fine">Written by <a href="../../author/suman-limbu/">Suman Limbu</a>, owner and trainer at Apex Fitness Centre in Morang, Nepal.</p>
</section>""",
 "Fitness careers": """<section class="abody" style="max-width:760px;margin:8px 0 40px">
<h2>Become a gym trainer from Nepal</h2>
<p>Good trainers combine knowledge, people skills and real experience on the gym floor. These guides cover how to start in Nepal, work abroad, and handle your first clients.</p>
<ol><li><a href="../how-to-become-a-gym-trainer-in-nepal/">How to become a gym trainer in Nepal</a></li><li><a href="../gym-trainer-jobs-in-gulf-for-nepalis/">Gym trainer jobs in the Gulf for Nepalis</a></li><li><a href="../how-to-assess-your-first-gym-client/">How to assess your first gym client</a></li></ol>
<p class="fine">Written by <a href="../../author/suman-limbu/">Suman Limbu</a>, owner and trainer at Apex Fitness Centre in Morang, Nepal.</p>
</section>""",
 "Trekking": """<section class="abody" style="max-width:760px;margin:8px 0 40px">
<h2>How fit do you need to be for a trek in Nepal?</h2>
<p>Most popular treks in Nepal do not need climbing skills, but they do need legs and lungs that can handle 5 to 7 hours of walking a day, many days in a row, with long climbs and longer descents. The people who struggle are rarely the ones who lack strength. They are the ones who never trained for hours on their feet, or who go up too fast.</p>
<h2>Pick your trek, then your plan</h2>
<ul>
<li><a href="../everest-base-camp-trek-training-plan/">Everest Base Camp training plan</a>: Base Camp sits at about 5,364 m, reached by a slow climb over many days from Lukla at about 2,860 m.</li>
<li><a href="../annapurna-circuit-trek-fitness/">Annapurna Circuit fitness guide</a>: the hardest day is the crossing of Thorong La pass, about 5,416 m, with a long descent after it.</li>
</ul>
<h2>What every trek plan has in common</h2>
<ol>
<li><b>Long, easy walks.</b> Build up to 4 to 6 hours on your feet, mostly at a pace where you can still talk. Our <a href="../zone-2-training/">zone 2 training guide</a> explains how easy is easy enough.</li>
<li><b>Hills and stairs.</b> Climbing and especially descending are what make trekkers sore. Train on stairs or hills at least once a week, with a pack.</li>
<li><b>Leg strength.</b> Squats, lunges and step-ups twice a week protect your knees on the way down. Start with <a href="../how-to-squat-properly/">how to squat properly</a>.</li>
<li><b>Carry your real pack.</b> Train with the weight you will carry, and break in your boots before you fly.</li>
<li><b>Go up slowly.</b> Fitness does not protect you from altitude sickness. Follow your guide's acclimatisation days, and descend if symptoms get worse.</li>
</ol>
<h2>Food and water on the trail</h2>
<p>Trek days burn a lot of energy, and appetite often drops at altitude. Dal bhat is the trekker's staple for good reason: it is filling, easy to digest, and teahouses often give a second helping. See <a href="../dal-bhat-protein/">how much protein is in dal bhat</a>, and use the <a href="../../calculators/water-intake-calculator/">water intake calculator</a> as a starting point for your daily water. To see how much energy a trek day takes, try the <a href="../../calculators/trekking-calorie-calculator/">trekking calorie calculator</a>.</p>
<p class="fine">Written by <a href="../../author/suman-limbu/">Suman Limbu</a>, owner and trainer at Apex Fitness Centre in Morang, Nepal. General information, not medical advice: talk to a doctor before a high-altitude trek if you have a heart, lung or blood pressure condition.</p>
</section>""",
}

def slugify(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def _front(path):
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    if not raw.startswith("---\n"):
        raise SystemExit(f"\n[blog] {os.path.basename(path)}: the file must start with a --- line (see _TEMPLATE.md)\n")
    top, body = raw[4:].split("\n---", 1)
    meta = {}
    for line in top.split("\n"):
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1); meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta, body.lstrip("-").lstrip("\n")

from PIL import Image as _BIm
BLOG_IMG = {}  # original file name -> (base name, width, height) after resizing to max 1200 px
COVERS = {}    # key -> arguments for covers.make_cover (auto covers for posts without their own image)
import covers as _covers

def _bimg(name, post):
    """Check an image exists in content/blog/images and return (web name, w, h)."""
    if name in BLOG_IMG: return BLOG_IMG[name]
    f = os.path.join(BLOG_DIR, "images", name)
    if not os.path.exists(f):
        raise SystemExit(f"\n[blog] {post}: image '{name}' not found. Upload it to source/content/blog/images/ (names are case-sensitive)\n")
    im = _BIm.open(f); w, h = im.size
    if w > 1200: w, h = 1200, round(h * 1200 / w)
    BLOG_IMG[name] = (os.path.splitext(name)[0], w, h)
    return BLOG_IMG[name]

def copy_blog_images():
    od = os.path.join(OUT, "blog", "images"); os.makedirs(od, exist_ok=True)
    for key, args in COVERS.items():
        _covers.make_cover(os.path.join(od, BLOG_IMG[key][0]), **args)
    for name, (base, w, h) in BLOG_IMG.items():
        if name in COVERS: continue
        im = _BIm.open(os.path.join(BLOG_DIR, "images", name)).convert("RGB")
        if im.width > 1200: im = im.resize((w, h), _BIm.LANCZOS)
        im.save(os.path.join(od, base + ".webp"), "WEBP", quality=80, method=6)
        im.save(os.path.join(od, base + ".jpg"), "JPEG", quality=82, optimize=True, progressive=True)

def load_posts():
    posts = []
    for f in sorted(_glob.glob(os.path.join(BLOG_DIR, "*.md"))):
        name = os.path.basename(f)
        if name.startswith("_"): continue
        m, body = _front(f)
        miss = [k for k in REQUIRED if not m.get(k)]
        if miss: raise SystemExit(f"\n[blog] {name}: missing {', '.join(miss)} at the top of the file (see _TEMPLATE.md)\n")
        try: d = _dt.date.fromisoformat(m["date"])
        except ValueError: raise SystemExit(f"\n[blog] {name}: date must look like 2026-10-23, got '{m['date']}'\n")
        if m.get("draft", "").lower() in ("true", "yes", "1") or d > TODAY: continue
        slug = m.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name[:-3])
        slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
        if len(m["description"]) > 160:
            print(f"[blog] note: {name} description is {len(m['description'])} characters; Google shows about 155.")
        _conv = _md.Markdown(extensions=["extra", "sane_lists", "smarty", "toc"], extension_configs={"toc": {"toc_depth": "2"}}, output_format="html5")
        html_ = _conv.convert(body)
        toc = [(t["id"], t["name"]) for t in _conv.toc_tokens]
        # FAQ: a "## Frequently asked questions" (or "## Common questions") section with ### questions becomes FAQPage data
        faq = []
        fm = re.search(r'<h2 id="[^"]*">(?:Frequently asked questions|Common questions|FAQ)</h2>(.*?)(?=<h2 |$)', html_, re.S | re.I)
        if fm:
            for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)", fm.group(1), re.S):
                faq.append((re.sub(r"<[^>]+>", "", q).strip(), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()))
        def _swap(mm):
            base, w, h = _bimg(mm.group(1), name)
            return f'src="../images/{base}.webp" width="{w}" height="{h}"'
        html_ = re.sub(r'src="images/([^"]+)"', _swap, html_)
        if m.get("image"): _bimg(m["image"], name)
        words = len(re.sub(r"<[^>]+>", " ", html_).split())
        prods = [p for s in (m.get("products") or "").split(",") for p in PRODUCTS if p["slug"] == s.strip()]
        upd = m.get("updated")
        m["author"] = m.get("author") or "suman-limbu"  # Suman writes or approves every post
        posts.append(dict(m, slug=slug, d=d, updated=_dt.date.fromisoformat(upd) if upd else d, html=html_, words=words,
                          mins=max(1, round(words / 200)), category=m.get("category") or "Training", prods=prods, file=name, toc=toc, faq=faq))
        posts[-1]["cat_slug"] = slugify(posts[-1]["category"])
        if not m.get("image"):
            # automatic branded cover, so every post has an image (Google Discover, social shares, AdSense quality)
            key = f"__cover__{slug}"
            ph = m.get("cover_photo")
            if ph:
                ph = os.path.join(HERE, ph) if ph.startswith("assets/") else os.path.join(BLOG_DIR, "images", ph)
                if not os.path.exists(ph): raise SystemExit(f"\n[blog] {name}: cover_photo '{m.get('cover_photo')}' not found\n")
            art = m.get("cover_art")
            if art and art not in _covers.ARTS:
                raise SystemExit(f"\n[blog] {name}: cover_art must be one of: {', '.join(_covers.ARTS)}\n")
            COVERS[key] = dict(category=posts[-1]["category"], art=art, photo=ph)
            BLOG_IMG[key] = (f"cover-{slug}", 1200, 675)
            posts[-1]["image"] = key
            posts[-1]["image_alt"] = m.get("image_alt") or m["title"]
    slugs = [p["slug"] for p in posts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup: raise SystemExit(f"\n[blog] two posts use the same slug: {', '.join(dup)}\n")
    return sorted(posts, key=lambda p: p["d"], reverse=True)

def _date(d): return f"{d.day} {d.strftime('%B %Y')}"

def _postcard(p, r):
    # r is the path from the current page to /blog/
    img = ""
    if p.get("image"):
        base, w, h = BLOG_IMG[p["image"]]
        img = f'<span class="bimg"><img src="{r}images/{base}.webp" alt="{e(p.get("image_alt") or p["title"])}" width="{w}" height="{h}"></span>'
    return (f'<a class="bcard" href="{r}{p["slug"]}/">{img}<span class="bmeta"><span>{e(p["category"])}</span><span>{p["mins"]} min read</span></span>'
            f'<b>{e(p["title"])}</b><span class="bdesc">{e(p["description"])}</span></a>')

# Named authors. Fill in real details (only facts the person has confirmed), then put
# `author: suman-limbu` (the key) in a post's front matter, and optionally `reviewed_by: <key>`.
AUTHORS = {
    "suman-limbu": {"name": "Suman Limbu", "job": "Owner and trainer, Apex Fitness Centre",
                    "bio": "Suman runs Apex Fitness Centre in Urlabari, Morang. Before opening the gym he played football, and he kept training through his years working abroad. Training has been part of his life ever since, and he keeps studying fitness and nutrition research. In more than 2 years of coaching at the gym he has helped over 100 members, especially beginners, people losing weight and women starting strength training. His motto: \u201cFitness is a journey.\u201d",
                    "same": ["https://www.facebook.com/Phyaak/"], "photo": "team-suman-limbu.jpg"},
    # "suman-limbu": {"name": "Suman Limbu", "job": "Morning trainer, Apex Fitness Centre",
    #                 "bio": "…years training members, certifications…", "photo": "team-suman-limbu.jpg"},
}
def _author_ld(key):
    a = AUTHORS.get(key)
    if not a: return {"@type": "Organization", "name": SITE, "url": BASE + "/about/"}
    o = {"@type": "Person", "name": a["name"], "jobTitle": a["job"], "url": BASE + "/author/" + key + "/", "worksFor": {"@id": BASE + "/#org"}}
    if a.get("photo"): o["image"] = BASE + "/assets/" + a["photo"]
    if a.get("same"): o["sameAs"] = a["same"]
    return o
def _author_name(key): return AUTHORS[key]["name"] if key in AUTHORS else "the Apex Fitness Centre team"

_STOP = set("a an and are can do does for from how i in is it my of on or should the to what when which why with you your vs best guide beginners beginner nepal nepali".split())
def _words(p): return {w for w in re.findall(r"[a-z0-9]+", (p["slug"] + " " + p["title"]).lower()) if w not in _STOP and len(w) > 2}
def _rel_score(p, x):
    # shared topic words matter most, then same category, then recency as a tie-break
    return len(_words(p) & _words(x)) * 3 + (2 if x["category"] == p["category"] else 0) + x["d"].toordinal() / 1e7


# ---- Comments (own service on Cloudflare; see source/comments/). Off until source/comments-endpoint.txt exists. ----
_CEP = os.path.join(HERE, "comments-endpoint.txt")
COMMENTS_API = open(_CEP, encoding="utf-8").read().strip().rstrip("/") if os.path.exists(_CEP) else ""
COMMENTS_SCRIPT = '<script src="../../assets/comments.js" defer></script>\n' if COMMENTS_API else ""
def comments_section(slug):
    if not COMMENTS_API: return ""
    return (f'<section class="cmts" id="comments" data-api="{e(COMMENTS_API)}" data-post="{e(slug)}" aria-labelledby="cm-h">'
            '<h2 id="cm-h">Comments <span class="cm-count"></span></h2>'
            '<form class="cm-form" novalidate>'
            '<label for="cm-name">Your name</label><input id="cm-name" name="name" maxlength="60" autocomplete="name" required>'
            '<label for="cm-body">Your comment or question</label><textarea id="cm-body" name="body" maxlength="1500" rows="4" required></textarea>'
            '<div class="cm-hp" aria-hidden="true"><label for="cm-web">Leave this empty</label><input id="cm-web" name="website" tabindex="-1" autocomplete="off"></div>'
            '<div class="cm-row"><button class="btn" type="submit">Post comment</button><span class="cm-note">Please be kind. The Apex team removes spam and abusive comments. Don\'t share private health details.</span></div>'
            '<p class="cm-msg" role="status" aria-live="polite"></p></form>'
            '<div class="cm-list"><p class="cm-empty">Loading comments…</p></div>'
            '<noscript><p class="cm-empty">Turn on JavaScript to read and post comments.</p></noscript></section>')

def build_blog():
    posts = load_posts()
    for i, p in enumerate(posts):
        d = 2; path = f"blog/{p['slug']}/"
        cr = [("Home", ""), ("Blog", "blog/"), (p["category"], f"blog/{p['cat_slug']}/"), (p["title"], path)]
        img_abs = BASE + "/blog/images/" + BLOG_IMG[p["image"]][0] + ".jpg" if p.get("image") else BASE + "/assets/og-image.jpg"
        art = {"@type": "BlogPosting", "headline": p["title"], "description": p["description"], "datePublished": p["d"].isoformat(),
               "dateModified": p["updated"].isoformat(), "author": _author_ld(p.get("author")),
               "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + "/" + path, "image": img_abs, "wordCount": p["words"],
               "articleSection": p["category"]}
        graph = [crumbs(cr), art]
        if p["faq"]: graph.append(faq_ld(p["faq"]))
        j = ld({"@context": "https://schema.org", "@graph": graph})
        tocb = ""
        if len(p["toc"]) >= 3:
            tocb = '<nav class="ptoc" aria-label="In this article"><b>In this article</b><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in p["toc"]) + "</ol></nav>"
        hero = ""
        if p.get("image"):
            base, w, h = BLOG_IMG[p["image"]]
            _pin = os.path.exists(os.path.join(BLOG_DIR, "pins", p["slug"] + ".jpg"))
            _pm = f' data-pin-media="{BASE}/blog/pins/{p["slug"]}.jpg" data-pin-description="{e(p["title"])}"' if _pin else ""
            hero = f'<figure class="phero"><img src="../images/{base}.webp" alt="{e(p.get("image_alt") or p["title"])}" width="{w}" height="{h}" fetchpriority="high"{_pm}></figure>'
        shop = ""
        if p["prods"]:
            shop = f'<section><h2 class="h2s">Products in this post</h2><div class="pgrid">{"".join(card(x, d) for x in p["prods"])}</div></section>'
        more = sorted((x for x in posts if x is not p), key=lambda x: -_rel_score(p, x))[:3]
        more_html = f'<section class="gl"><h2 class="h2s">More from the blog</h2><div class="bgrid">{"".join(_postcard(x, "../") for x in more)}</div></section>' if more else ""
        _pinimg = f"{BASE}/blog/pins/{p['slug']}.jpg" if os.path.exists(os.path.join(BLOG_DIR, "pins", p["slug"] + ".jpg")) else (BASE + "/blog/images/" + BLOG_IMG[p["image"]][0] + ".jpg" if p.get("image") else BASE + "/assets/og-image.jpg")
        _q = __import__("urllib.parse").parse.quote
        _u = _q(BASE + "/" + path, safe="")
        _FB = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M13.5 22v-8.2h2.8l.5-3.3h-3.3V8.4c0-.95.3-1.6 1.6-1.6h1.8V3.9c-.3 0-1.4-.15-2.6-.15-2.6 0-4.3 1.55-4.3 4.4v2.35H7.1v3.3H10V22h3.5Z"/></svg>'
        _WA = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-3.3-.8-2.8-1.1-4.5-3.9-4.7-4.1-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.1 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.2Z"/></svg>'
        _PI = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 0a12 12 0 0 0-4.37 23.17c-.1-.94-.2-2.4.04-3.43l1.4-5.96s-.36-.72-.36-1.78c0-1.66.97-2.9 2.17-2.9 1.02 0 1.52.77 1.52 1.7 0 1.03-.66 2.57-1 4-.28 1.2.6 2.17 1.78 2.17 2.13 0 3.77-2.25 3.77-5.5 0-2.87-2.06-4.88-5.01-4.88-3.41 0-5.42 2.56-5.42 5.21 0 1.03.4 2.14.9 2.74.1.12.11.22.08.34l-.33 1.37c-.05.22-.18.27-.4.16-1.5-.7-2.43-2.89-2.43-4.65 0-3.78 2.75-7.26 7.92-7.26 4.16 0 7.4 2.97 7.4 6.93 0 4.13-2.6 7.46-6.22 7.46-1.21 0-2.36-.63-2.75-1.38l-.75 2.85c-.27 1.04-1 2.35-1.49 3.15A12 12 0 1 0 12 0z"/></svg>'
        _X = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M17.75 3h3.07l-6.7 7.66L22 21h-6.17l-4.83-6.32L5.47 21H2.4l7.17-8.2L2 3h6.33l4.37 5.78L17.75 3Zm-1.08 16.2h1.7L7.42 4.73H5.6l11.07 14.47Z"/></svg>'
        _IN = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9.75h4V21H3V9.75Zm6.5 0h3.83v1.54h.06c.53-1.01 1.84-2.08 3.79-2.08 4.05 0 4.8 2.67 4.8 6.13V21h-4v-5c0-1.2-.02-2.73-1.66-2.73-1.67 0-1.92 1.3-1.92 2.64V21h-4V9.75Z"/></svg>'
        _LK = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5"/></svg>'
        _full = BASE + "/" + path
        def _share(label):
            def btn(cls, href, name, svg):
                return f'<a class="shc {cls}" href="{href}" target="_blank" rel="noopener" aria-label="{name}" title="{name}">{svg}</a>'
            return (f'<div class="sharebar"><span class="sh-l">{label}</span>'
                    + btn("sh-fb", f"https://www.facebook.com/sharer/sharer.php?u={_u}", "Share on Facebook", _FB)
                    + btn("sh-wa", f"https://wa.me/?text={_q(p['title'] + ' ' + _full, safe='')}", "Share on WhatsApp", _WA)
                    + btn("sh-pi", f"https://www.pinterest.com/pin/create/button/?url={_u}&media={_q(_pinimg, safe='')}&description={_q(p['title'], safe='')}", "Save to Pinterest", _PI)
                    + btn("sh-x", f"https://twitter.com/intent/tweet?url={_u}&text={_q(p['title'], safe='')}", "Share on X", _X)
                    + btn("sh-in", f"https://www.linkedin.com/sharing/share-offsite/?url={_u}", "Share on LinkedIn", _IN)
                    + f'<button class="shc sh-copy" type="button" data-copy="{_full}" aria-label="Copy link" title="Copy link">{_LK}<span class="sh-ok" aria-live="polite"></span></button>'
                    + '</div>')
        pinbtn = _share("Share")
        sharebottom = _share("Found this useful? Share it")
        upd = f' &middot; Updated {_date(p["updated"])}' if p["updated"] != p["d"] else ""
        ask = wa(f"Hi Apex Fitness Centre, I read your post \"{p['title']}\" and I have a question: ")
        body = f"""<body data-root="../../">
{nav(d, "blog")}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="post">
<header class="phead"><a class="label" href="../{p['cat_slug']}/">{e(p['category'])}</a><h1>{e(p['title'])}</h1><p class="lead">{e(p['description'])}</p>
<p class="byline">By {('<a href="../../author/' + p['author'] + '/">' + e(_author_name(p['author'])) + '</a>') if p.get('author') in AUTHORS else e(_author_name(p.get('author')))}{(' &middot; Reviewed by ' + e(_author_name(p['reviewed_by']))) if p.get('reviewed_by') in AUTHORS else ''} &middot; {_date(p['d'])}{upd} &middot; {p['mins']} min read</p></header>
{hero}
{pinbtn}
{tocb}
<div class="abody">{p['html']}</div>
<aside class="author">{('<img class="aphoto" src="../../assets/' + AUTHORS[p["author"]]["photo"] + '" alt="' + e(AUTHORS[p["author"]]["name"]) + '" width="64" height="64" loading="lazy" style="width:64px;height:64px">') if AUTHORS.get(p.get("author"), {}).get("photo") else ""}<b>About this article</b><p>{(e(AUTHORS[p['author']]['name']) + ', ' + e(AUTHORS[p['author']]['job']) + '. ' + e(AUTHORS[p['author']]['bio']) + ' ') if p.get('author') in AUTHORS else ''}Written by the team at <a href="../../about/">Apex Fitness Centre</a>, a gym and supplement store in Urlabari, Morang, Nepal. We research every article from the sources linked in the text and update it when facts change. Read our <a href="../../editorial-policy/">editorial policy</a>{(' or <a href="../../author/' + p['author'] + '/">more about ' + e(AUTHORS[p['author']]['name']) + '</a>') if p.get('author') in AUTHORS else ''}.</p></aside>
{sharebottom}
{newsletter_box()}
<aside class="pask" data-product="Blog: {e(p['title'])}"><p><b>Have a question about this?</b> Message us. We reply from the gym in Urlabari.</p><a class="btn wa" href="{ask}" target="_blank" rel="noopener">Ask on WhatsApp</a></aside>
<p class="fine" style="text-align:left">General information, not medical advice. Ask a doctor if you have a health condition. Results vary from person to person.</p>
{comments_section(p["slug"])}
</article>
{shop}
{more_html}
</div></main>
{footer(d)}{drawer()}{tail(d).replace("</body>", COMMENTS_SCRIPT + "</body>", 1)}"""
        ttl = p.get("seo_title") or (p["title"] + " | Apex Fitness" if len(p["title"]) <= 50 else p["title"])
        pages[path] = head(ttl, p["description"], path, d, image=("blog/images/" + BLOG_IMG[p["image"]][0] + ".jpg") if p.get("image") else None,
                           extra=j, ptype="article") + body
        sitemap.append((path, "0.7"))
    # topic pages
    cats = {}
    for p in posts: cats.setdefault(p["category"], []).append(p)
    def chips(r, active=None):
        names = [t for t in TOPICS if t in cats] + [c for c in cats if c not in TOPICS]
        return '<div class="chips">' + f'<a class="chip{" on" if active is None else ""}" href="{r or "./"}">All posts</a>' + "".join(
            f'<a class="chip{" on" if active == c else ""}" href="{r}{slugify(c)}/">{e(c)}</a>' for c in names) + "</div>"
    clash = {slugify(c) for c in cats} & {p["slug"] for p in posts}
    if clash: raise SystemExit(f"\n[blog] a post web name is the same as a topic page: {', '.join(clash)}. Rename the post file.\n")
    for c, ps in cats.items():
        d = 2; path = f"blog/{slugify(c)}/"; cr = [("Home", ""), ("Blog", "blog/"), (c, path)]
        intro = TOPIC_INTRO.get(c, f"Articles about {c.lower()} in Nepal.")
        j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "CollectionPage", "name": f"{c} | Apex Fitness Blog", "url": BASE + "/" + path}]})
        body = f"""<body data-root="../../">
{nav(d, "blog")}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="shead left"><h1>{e(c)}</h1><p>{e(intro)}</p></div>
{chips("../", c)}
<div class="bgrid">{"".join(_postcard(x, "../") for x in ps)}</div>
{TOPIC_HUB.get(c, "")}
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
        pages[path] = head(f"{c} in Nepal | Apex Fitness Blog", intro, path, d, extra=j) + body
        sitemap.append((path, "0.6"))
    # index
    d = 1; cr = [("Home", ""), ("Blog", "blog/")]
    cards = "".join(_postcard(p, "") for p in posts) or '<p class="fine">First posts coming soon.</p>'
    gcards = "".join(f'<a class="gcard" href="../guides/{x["slug"]}/"><b>{e(x["h1"])}</b><span>{e(x["desc"])}</span></a>' for x in GUIDES if x["slug"] not in MERGED_GUIDE_SLUGS)
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "Blog", "name": "Apex Fitness Blog", "url": BASE + "/blog/",
            "publisher": {"@id": BASE + "/#org"}, "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": BASE + f"/blog/{p['slug']}/", "datePublished": p["d"].isoformat(),
            "dateModified": p["updated"].isoformat(), "author": _author_ld(p.get("author")),
            "image": BASE + "/blog/images/" + BLOG_IMG[p["image"]][0] + ".jpg" if p.get("image") else BASE + "/assets/og-image.jpg"} for p in posts[:20]]}]})
    body = f"""<body data-root="../">
{nav(d, "blog")}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="shead left"><h1>Fitness in Nepal</h1><p>Training, diet, supplements, gyms, fitness careers and the people shaping Nepal's fitness scene. Researched, honest and written for Nepal by the team at Apex Fitness Centre.</p></div>
{chips("")}
<div class="bgrid">{cards}</div>
<section class="gl"><h2 class="h2s">Supplement buying guides</h2><div class="ggrid">{gcards}</div></section>
<p class="fine" style="text-align:left"><a class="tl" href="feed.xml">RSS feed</a></p>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
    pages["blog/"] = head("Fitness in Nepal Blog: Training, Supplements, Gyms and Careers",
                          "Fitness in Nepal: training, diet, supplements, gyms, trainer courses, influencers and competitions. Honest guides from Apex Fitness Centre.", "blog/", d, extra=j) + body
    sitemap.append(("blog/", "0.8"))
    # RSS
    items = "".join(f"<item><title>{e(p['title'])}</title><link>{BASE}/blog/{p['slug']}/</link><guid>{BASE}/blog/{p['slug']}/</guid>"
                    f"<pubDate>{_dt.datetime.combine(p['d'], _dt.time(6, 0), NPT).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate><description>{e(p['description'])}</description></item>" for p in posts[:30])
    BLOG_RSS[0] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Apex Fitness Blog</title><link>{BASE}/blog/</link>'
                   f'<description>Training, diet and supplement advice for Nepal</description><language>en</language>{items}</channel></rss>\n')
    build_author_pages(posts)
    home_latest(posts)
    return posts
BLOG_RSS = [""]

def build_author_pages(posts):
    for key, a in AUTHORS.items():
        mine = [p for p in posts if p.get("author") == key]
        path = f"author/{key}/"; d = 2; cr = [("Home", ""), ("Blog", "blog/"), (a["name"], path)]
        person = dict(_author_ld(key), description=a["bio"])
        j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "ProfilePage", "mainEntity": person, "url": BASE + "/" + path}]})
        pic = f'<img class="aphoto" src="../../assets/{a["photo"]}" alt="{e(a["name"])}" width="140" height="140" style="width:140px;height:140px;border-radius:50%;object-fit:cover">' if a.get("photo") else ""
        links = "".join(f'<a href="{u}" target="_blank" rel="noopener me">{"Facebook" if "facebook" in u else u}</a> ' for u in a.get("same", []))
        body = f"""<body data-root="../../">
{nav(d, "blog")}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="post"><header class="phead"><span class="label">Author</span><h1>{e(a["name"])}</h1><p class="lead">{e(a["job"])}</p></header>
<div class="abody">{pic}<p>{e(a["bio"])}</p>
<p>Suman writes or checks every article on this blog against the sources linked in it, and updates articles when the facts change. How we work: <a href="../../editorial-policy/">editorial policy</a>. Where he trains members: <a href="../../gym/">Apex Fitness Centre, Urlabari</a>.</p>
{('<p>' + links + '</p>') if links else ''}
<h2>Articles by {e(a["name"])} ({len(mine)})</h2></div></article>
<div class="bgrid">{"".join(_postcard(x, "../../blog/") for x in mine)}</div>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
        pages[path] = head(f"{a['name']}: {a['job']} | Apex Fitness Blog", f"{a['name']}, {a['job']}. Articles on training, diet and fitness in Nepal.", path, d, extra=j) + body
        sitemap.append((path, "0.5"))

def home_latest(posts):
    marker = '<section class="sec alt"><div class="wrap two">\n<div><span class="label">About Apex</span>'
    if marker not in pages.get("", ""): print("[blog] note: homepage marker not found, latest articles not added"); return
    sec = ('<section class="sec"><div class="wrap"><div class="shead"><span class="label">From the blog</span><h2>Latest articles</h2></div>'
           f'<div class="bgrid">{"".join(_postcard(x, "blog/") for x in posts[:6])}</div>'
           '<p style="margin-top:20px"><a class="btn line" href="blog/">All articles</a> <a class="btn line" href="food/">Food calorie chart</a> <a class="btn line" href="calculators/">Fitness calculators</a></p></div></section>\n\n')
    pages[""] = pages[""].replace(marker, sec + marker, 1)

def _simple(path, title, desc, h1, inner, prio="0.3"):
    d = path.count("/"); cr = [("Home", ""), (h1, path)]
    body = f"""<body data-root="{'../'*d}">
{nav(d)}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="post"><header class="phead"><h1>{e(h1)}</h1></header><div class="abody">{inner}</div></article>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
    pages[path] = head(title, desc, path, d, extra=ld({"@context": "https://schema.org", "@graph": [crumbs(cr)]})) + body
    sitemap.append((path, prio))

def build_info_pages():
    _simple("about/", "About Apex Fitness Centre | Gym and Supplement Store, Urlabari", "Who we are: Apex Fitness Centre, a gym and supplement store in Urlabari-9, Durgapuri, Morang, Nepal.", "About Apex Fitness Centre", f"""
<p>Apex Fitness Centre is a gym in Urlabari-9, Durgapuri, Morang, Nepal. We are open 4:30 AM to 8:30 PM, Sunday to Friday (closed on Saturday), with trainers on the floor and a front desk to help members.</p>
<p>Next to the gym we run this online store. We sell authentic supplements bought from authorised sellers, with free delivery all over Nepal. Orders come to us on WhatsApp, and a real person from the gym confirms stock, payment and delivery.</p>
<p>The <a href="../blog/">blog</a> and <a href="../guides/">guides</a> are written by our team from what members ask us every day: how to start training, how much protein you need, which supplements are worth the money and how to avoid fakes. We keep advice simple and honest, and we do not make medical claims.</p>
<h2>Visit or contact us</h2>
<p>Apex Fitness Centre, Urlabari-9, Durgapuri, Morang, Nepal<br>WhatsApp and phone: <a href="https://wa.me/{WA}" target="_blank" rel="noopener">9708819605</a><br>Facebook: <a href="https://www.facebook.com/apexfitcentre" target="_blank" rel="noopener">apexfitcentre</a></p>
<h2 id="suman-limbu">Who writes our training guides</h2>
<p><b>Suman Limbu</b>, owner and trainer at Apex Fitness Centre. Before opening the gym he played football and kept training through his years working abroad. In more than 2 years of coaching at the gym he has helped over 100 members, especially beginners, people losing weight and women starting strength training. His motto: &ldquo;Fitness is a journey.&rdquo; <a href="https://www.facebook.com/Phyaak/" target="_blank" rel="noopener">Suman on Facebook</a>.</p>
<p>See <a href="../gym/">the gym, plans and team</a>.</p>""")
    _simple("contact/", "Contact Apex Fitness Centre | WhatsApp 9708819605", "Contact Apex Fitness Centre in Urlabari, Morang: WhatsApp or call 9708819605. Open 4:30 AM to 8:30 PM, Sunday to Friday.", "Contact us", f"""
<p>The fastest way to reach us is WhatsApp. We reply from the gym during opening hours.</p>
<p><a class="btn wa" href="https://wa.me/{WA}?text=Hi%20Apex%20Fitness%20Centre%2C%20" target="_blank" rel="noopener">Message us on WhatsApp</a></p>
<ul><li><b>WhatsApp and phone:</b> <a href="tel:+9779708819605">9708819605</a></li>
<li><b>Address:</b> Apex Fitness Centre, Urlabari-9, Durgapuri, Morang, Nepal</li>
<li><b>Opening hours:</b> 4:30 AM to 8:30 PM, Sunday to Friday. Closed on Saturday.</li>
<li><b>Facebook:</b> <a href="https://www.facebook.com/apexfitcentre" target="_blank" rel="noopener">facebook.com/apexfitcentre</a></li></ul>
<p>For orders, delivery, returns of sealed items, gym memberships, gym software demos, or questions about anything on the blog, send us a message.</p>""")
    _simple("editorial-policy/", "Editorial Policy | Apex Fitness Centre", "How the Apex Fitness Centre blog researches, writes, fact-checks and updates articles about fitness, supplements and gyms in Nepal.", "Editorial policy", """
<p>The Apex Fitness Centre blog publishes practical articles about fitness in Nepal: training, diet, supplements, gyms, fitness careers and the people in Nepal's fitness scene. This page explains how we work.</p>
<h2>Who writes the articles</h2><p>Articles are produced by the team at Apex Fitness Centre, a gym and supplement store in Urlabari-9, Durgapuri, Morang. Topics come from what members ask us every day. When an article is written or reviewed by a named trainer, their name appears at the top of the article.</p><h2>How articles are made</h2><p>We use research and writing tools, including AI, to help gather research and draft articles. Before publishing, every article is checked against the sources linked in it, edited for Nepal (local foods, prices, weather and gyms), and given its sources section. We do not publish made-up quotes, reviews or personal stories, and real member stories are shared only with the member's consent.</p>
<h2>How we research</h2><ul><li>Facts about health and nutrition are based on published research and reviews, and we link to our main sources in the article.</li><li>Prices, fees, salaries and rules are checked from official or primary sources where possible, and every article shows the date it was checked.</li><li>Information about real people, gyms and businesses comes only from public sources such as news reports and their own public profiles. We do not publish rumours or negative claims.</li></ul>
<h2>Health information</h2><p>Our articles are general information, not medical advice. We avoid promises about results and we tell readers to speak to a doctor when a topic needs it, for example for medical conditions, pregnancy or young people.</p>
<h2>Our products and independence</h2><p>We sell supplements in our store. When an article mentions products we sell, we say so, and we apply the same honest checks to our own products as to anyone else's. Nobody pays to be included in our lists or articles.</p>
<h2>Advertising</h2><p>Some pages show ads from Google AdSense. Ads are kept separate from our writing, and advertisers have no say in what we publish.</p>
<h2>Corrections</h2><p>If you find a mistake, or you are mentioned in an article and something is wrong, message us on WhatsApp at 9708819605. We check every report and correct mistakes quickly, and we update the date on the article.</p>""")
    ads = ("<h2>Advertising</h2><p>We show ads from Google AdSense. Google and its partners use cookies to show ads based on your visits to this and other websites. "
           "You can turn off personalised ads at <a href=\"https://adssettings.google.com\" target=\"_blank\" rel=\"noopener\">Google Ad Settings</a>, and read how Google uses data at "
           "<a href=\"https://policies.google.com/technologies/partner-sites\" target=\"_blank\" rel=\"noopener\">policies.google.com/technologies/partner-sites</a>.</p>")
    _simple("privacy/", "Privacy Policy | Apex Fitness Centre", "How apexfitnesscentre.shop uses cookies, analytics, ads and the details you send us on WhatsApp.", "Privacy policy", f"""
<p>Last updated: {TODAY.isoformat()}. This policy covers apexfitnesscentre.shop, run by Apex Fitness Centre, Urlabari-9, Durgapuri, Morang, Nepal.</p>
<h2>What we collect</h2>
<p>We do not have accounts or sign-ups on this website. When you order or ask a question, you send us a message on WhatsApp. That message, with your name, phone number and delivery address if you give them, is used only to answer you, deliver your order and keep simple sales records. We do not sell it to anyone.</p>
<h2>Your cart</h2><p>Your cart is saved in your own browser (local storage) so it is still there when you come back. It is not sent to us until you send the WhatsApp message yourself.</p>
<h2>Analytics</h2><p>We use Google Analytics to count visits and see which pages and buttons are used, for example how many people tap Order on WhatsApp. Google Analytics uses cookies and collects information such as your device, browser, approximate location and the pages you view. It does not give us your name or phone number.</p>
{ads}
<h2>Your choices</h2><p>You can block or delete cookies in your browser settings, and the site still works. To ask us to delete messages or details you sent us, message us on WhatsApp at 9708819605.</p>
<h2>Health information</h2><p>Articles on this site are general information, not medical advice. Ask a doctor if you have a health condition.</p>
<h2>Changes</h2><p>If we change this policy we will update the date at the top of this page.</p>""")
