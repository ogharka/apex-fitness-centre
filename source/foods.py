# South Asian food calorie database: /food/ (hub) and /food/<slug>-calories/ (one page per food).
# exec()'d by build.py after the blog and tools, so it can link only to published posts (POSTS).
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("foods_data", os.path.join(HERE, "foods_data.py"))
_fd = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_fd)
FOODS, GROUP_ORDER = _fd.FOODS, _fd.GROUP_ORDER
_FBY = {f["slug"]: f for f in FOODS}
_LIVE_POSTS = {p["slug"]: p for p in POSTS}

def _fdc_link(src, fid):
    if src == "sr": return f"https://fdc.nal.usda.gov/food-details/{fid}/nutrients"
    return "https://fdc.nal.usda.gov/download-datasets/"

def _per100(f):
    """Per-100 g values; composite foods are summed from their parts."""
    if "composite" in f:
        tot = sum(g for _, _, g in f["composite"])
        v = {k: sum(g / 100 * _FBY[s][k] for _, s, g in f["composite"]) for k in ("k", "p", "f", "c", "fb")}
        return {k: v[k] * 100 / tot for k in v}, tot
    return {k: f[k] for k in ("k", "p", "f", "c", "fb")}, None

def _n(x, d=0):
    s = f"{x:,.{d}f}"
    return s[:-2] if d and s.endswith(".0") else s

def _servings(f):
    per, tot = _per100(f)
    out = []
    for lab, g in f["servings"]:
        g = g if g is not None else tot
        out.append((lab, g, {k: per[k] * g / 100 for k in per}))
    return per, out

def food_path(slug): return f"food/{slug}-calories/"

_FOOD_POSTS = {
    "Breads and grains": ["weight-loss-diet-plan-nepali-food", "how-to-gain-weight-fast-for-skinny-people", "high-protein-nepali-diet-plan-for-muscle-gain"],
    "Rice dishes": ["weight-loss-diet-plan-nepali-food", "why-am-i-not-losing-weight", "high-protein-nepali-diet-plan-for-muscle-gain"],
    "Dal and legumes": ["protein-rich-vegetarian-foods-nepal", "how-much-protein-do-you-need", "high-protein-nepali-diet-plan-for-muscle-gain"],
    "Dairy and eggs": ["how-much-protein-do-you-need", "protein-rich-vegetarian-foods-nepal", "how-many-eggs-per-day", "high-protein-breakfast-ideas-nepal"],
    "Meat and fish": ["how-much-protein-do-you-need", "high-protein-nepali-diet-plan-for-muscle-gain", "body-recomposition-lose-fat-build-muscle"],
    "Dishes and snacks": ["momo-and-fitness", "weight-loss-diet-plan-nepali-food", "why-am-i-not-losing-weight", "healthy-nepali-snacks-for-gym"],
    "Vegetables, fruit and fats": ["weight-loss-diet-plan-nepali-food", "how-to-lose-belly-fat", "how-to-gain-weight-fast-for-skinny-people"],
}

def build_foods():
    for f in FOODS:
        d = 2; path = food_path(f["slug"])
        per, serv = _servings(f)
        lab0, g0, v0 = serv[0]
        name = f["name"]
        short = name.split(" (")[0]
        cr = [("Home", ""), ("Food calorie chart", "food/"), (name, path)]
        title = f"{name} Calories, Protein and Nutrition"
        if len(title) > 60: title = f"{short} Calories, Protein and Nutrition"
        low = short.lower()
        if low.startswith("boiled"): low = "a " + low
        desc = f"How many calories in {low}? {lab0[0].upper()+lab0[1:]}: {_n(v0['k'])} kcal and {_n(v0['p'],1)} g protein. Full nutrition from USDA data, plus diet tips."
        desc = desc if len(desc) <= 155 else f"{short} calories: {_n(v0['k'])} kcal and {_n(v0['p'],1)} g protein per serving. Full nutrition from USDA data, plus weight loss and muscle tips."
        kcal_from = {"Protein": per["p"] * 4, "Carbs": per["c"] * 4, "Fat": per["f"] * 9}
        tk = sum(kcal_from.values()) or 1
        split = " · ".join(f"{k} {round(v / tk * 100)}%" for k, v in kcal_from.items())
        rows = "".join(f"<tr><td>{e(l)}</td><td>{_n(v['k'])}</td><td>{_n(v['p'],1)} g</td><td>{_n(v['c'],1)} g</td><td>{_n(v['f'],1)} g</td><td>{_n(v['fb'],1)} g</td></tr>" for l, g, v in serv)
        rows += f"<tr><td><b>Per 100 g</b></td><td>{_n(per['k'])}</td><td>{_n(per['p'],1)} g</td><td>{_n(per['c'],1)} g</td><td>{_n(per['f'],1)} g</td><td>{_n(per['fb'],1)} g</td></tr>"
        table = f"<table><thead><tr><th>Serving</th><th>Calories (kcal)</th><th>Protein</th><th>Carbs</th><th>Fat</th><th>Fibre</th></tr></thead><tbody>{rows}</tbody></table>"
        tiles = "".join(f'<div class="ft"><b>{x}</b><span>{y}</span></div>' for x, y in [
            (_n(v0["k"]), "calories"), (_n(v0["p"], 1) + " g", "protein"), (_n(v0["c"], 1) + " g", "carbs"), (_n(v0["f"], 1) + " g", "fat")])
        alt = ""
        if f.get("alt"):
            s, fid, dsc, k, p, fa, c, fb = f["alt"]
            alt = (f"<h2>Without added oil</h2><p>Cooked plainly with no oil or ghee, {e(low)} has about <b>{_n(k)} kcal</b>, {_n(p,1)} g protein, {_n(c,1)} g carbs and {_n(fa,1)} g fat per 100 g "
                   f"(USDA: {e(dsc)}). The difference is almost entirely the cooking fat.</p>")
        comp = ""
        if "composite" in f:
            crow = "".join(f"<tr><td><a href=\"../{x}-calories/\">{e(lab)}</a></td><td>{_n(g)} g</td><td>{_n(_FBY[x]['k']*g/100)}</td><td>{_n(_FBY[x]['p']*g/100,1)} g</td></tr>" for lab, x, g in f["composite"])
            tot = sum(_FBY[x]['k'] * g / 100 for _, x, g in f["composite"]); tp = sum(_FBY[x]['p'] * g / 100 for _, x, g in f["composite"])
            comp = (f"<h2>What's on the plate</h2><table><thead><tr><th>Part</th><th>Amount</th><th>Calories</th><th>Protein</th></tr></thead><tbody>{crow}"
                    f"<tr><td><b>Total</b></td><td></td><td><b>{_n(tot)}</b></td><td><b>{_n(tp,1)} g</b></td></tr></tbody></table>"
                    f"<p>Add achar (a few calories), a fried papad (about 40–60 kcal), a katori of curd (about 90 kcal, 5 g protein) or a meat curry to match your own plate.</p>")
        cmp_rows = "".join(f"<tr><td><a href=\"../{x}-calories/\">{e(_FBY[x]['name'])}</a></td><td>{_n(_per100(_FBY[x])[0]['k'])}</td><td>{_n(_per100(_FBY[x])[0]['p'],1)} g</td></tr>" for x in f["compare"])
        cmp = (f"<h2>How it compares</h2><p>Per 100 g:</p><table><thead><tr><th>Food</th><th>Calories</th><th>Protein</th></tr></thead><tbody>"
               f"<tr><td><b>{e(name)}</b></td><td><b>{_n(per['k'])}</b></td><td><b>{_n(per['p'],1)} g</b></td></tr>{cmp_rows}</tbody></table>")
        to25 = ""
        if per["p"] >= 5 and "composite" not in f:
            g25 = 25 / per["p"] * 100
            to25 = f"<p>To get <b>25 g of protein</b> from {e(low)} alone you would need about {_n(g25)} g, which is {_n(g25 / 100 * per['k'])} kcal.</p>"
        tips = "".join(f"<li>{e(t)}</li>" for t in f["tips"])
        proxy = f'<p class="fine" style="text-align:left"><b>About this estimate:</b> {e(f["proxy"])}</p>' if f.get("proxy") else ""
        if "composite" in f:
            src = "<ul>" + "".join(f'<li>{e(_FBY[x]["name"])}: <a href="{_fdc_link(_FBY[x]["usda"][0], _FBY[x]["usda"][1])}" rel="noopener">USDA FoodData Central</a>, “{e(_FBY[x]["usda"][2])}” (FDC ID {_FBY[x]["usda"][1]})</li>' for _, x, _g in f["composite"]) + "</ul>"
        else:
            s, fid, dsc = f["usda"][:3]
            src = f'<ul><li><a href="{_fdc_link(s, fid)}" rel="noopener">USDA FoodData Central</a>: “{e(dsc)}”, FDC ID {fid} ({"SR Legacy, 2018" if s == "sr" else "FNDDS survey foods, 2019 release"}).</li>'
            if f.get("alt"): src += f'<li>Without oil: “{e(f["alt"][2])}”, FDC ID {f["alt"][1]}.</li>'
            src += "</ul>"
        faq = [(f"How many calories are in {lab0}?" if not lab0.startswith("1 typical") else f"How many calories are in a plate of {low}?",
                f"About {_n(v0['k'])} calories, with {_n(v0['p'],1)} g of protein, {_n(v0['c'],1)} g of carbohydrate and {_n(v0['f'],1)} g of fat, based on USDA data. Home recipes and portion sizes vary."),
               (f"How much protein is in {low}?", f"About {_n(per['p'],1)} g per 100 g, or {_n(v0['p'],1)} g in {lab0}."),
               (f"Is {low} good for weight loss?", f["wl"]),
               (f"Is {low} good for building muscle?", f["mg"])]
        posts = [_LIVE_POSTS[s] for s in _FOOD_POSTS.get(f["group"], []) if s in _LIVE_POSTS][:3]
        reads = (f'<section class="gl"><h2 class="h2s">Read next</h2><div class="bgrid">{"".join(_postcard(x, "../../blog/") for x in posts)}</div></section>') if posts else ""
        same = [x for x in FOODS if x["group"] == f["group"] and x is not f][:8]
        more = "".join(f'<a class="gcard" href="../{x["slug"]}-calories/"><b>{e(x["name"])}</b><span>{_n(_servings(x)[1][0][2]["k"])} kcal · {e(_servings(x)[1][0][0])}</span></a>' for x in same)
        j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr),
                {"@type": "WebPage", "name": title, "url": BASE + "/" + path, "description": desc, "isPartOf": {"@id": BASE + "/#org"}, "inLanguage": "en",
                 "about": {"@type": "Thing", "name": name}},
                faq_ld(faq)]})
        body = f"""<body data-root="../../">
{nav(d)}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="post food">
<header class="phead"><a class="label" href="../">Food calorie chart</a><h1>{e(name)} Calories and Protein</h1>
<p class="lead">{e(lab0[0].upper() + lab0[1:])} has about <b>{_n(v0['k'])} calories</b> and <b>{_n(v0['p'],1)} g of protein</b>. {e(f['aka'])}.</p></header>
<div class="ftiles" aria-label="Nutrition for {e(lab0)}">{tiles}</div>
<div class="abody">
<p>{e(f['intro'])}</p>
<h2>{e(short)} nutrition per serving</h2>
{table}
<p>Calories come from: {split}.</p>
{to25}
{comp}
{alt}
<h2>Is {e(low)} good for weight loss?</h2>
<p>{e(f['wl'])}</p>
<h2>Is it good for building muscle?</h2>
<p>{e(f['mg'])}</p>
<h2>Tips from the Apex trainers</h2>
<ul>{tips}</ul>
{cmp}
<aside class="pask"><p><b>Plan your day:</b> find your daily calories and protein target, then build meals from this chart.</p><a class="btn" href="../../calculators/calorie-deficit-calculator/">Calorie calculator</a> <a class="btn ghost" href="../../calculators/protein-calculator/">Protein calculator</a></aside>
<h2>Frequently asked questions</h2>
{faq_html(faq)}
<h2>Source</h2>
{src}
{proxy}
<p class="fine" style="text-align:left">Values are averages. Real dishes vary with the recipe, the cook and the portion. General information, not medical advice.</p>
</div>
{newsletter_box("food")}
</article>
<section class="gl"><h2 class="h2s">More {e(f['group'].lower())}</h2><div class="ggrid">{more}</div></section>
{reads}
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
        pages[path] = head(title, desc, path, d, extra=j, ptype="article") + body
        sitemap.append((path, "0.7"))

    # ---- hub: /food/ ----
    d = 1; cr = [("Home", ""), ("Food calorie chart", "food/")]
    trs = []
    for g in GROUP_ORDER:
        items = [x for x in FOODS if x["group"] == g]
        if not items: continue
        trs.append(f'<tr class="fg"><th colspan="5" scope="colgroup">{e(g)}</th></tr>')
        for x in items:
            per, serv = _servings(x); lab, gg, v = serv[0]
            trs.append(f'<tr data-q="{e((x["name"] + " " + x["aka"]).lower())}"><td><a href="{x["slug"]}-calories/">{e(x["name"])}</a></td><td>{e(lab)}</td><td>{_n(v["k"])}</td><td>{_n(v["p"],1)} g</td><td>{_n(per["k"])}</td></tr>')
    table = ('<table class="fchart"><thead><tr><th>Food</th><th>Serving</th><th>Calories</th><th>Protein</th><th>kcal per 100 g</th></tr></thead><tbody>'
             + "".join(trs) + "</tbody></table>")
    hub_faq = [("How many calories are in dal bhat?", "A typical plate with 2 cups of rice, 1 cup of dal and 1 cup of saag has about 790 calories and 28 g of protein. Reducing the rice to 1 cup saves about 200 calories."),
               ("Which South Asian foods are highest in protein?", "Per 100 g: chicken breast (about 31 g), goat meat (27 g), soybeans (18 g), eggs (12.5 g) and paneer (about 18 g on typical labels). Dal, rajma and chana have about 8–9 g per 100 g cooked."),
               ("Where do these numbers come from?", "From USDA FoodData Central, the US government's food composition database. Each food page names the exact USDA entry and its ID. Where USDA has no entry, such as momo, we use the closest match and say so."),
               ("Why do my home-cooked dishes differ?", "Recipes, oil and portion sizes vary. Cooking oil is the biggest variable: each teaspoon adds about 40 calories.")]
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "CollectionPage", "name": "South Asian Food Calorie Chart", "url": BASE + "/food/",
            "hasPart": [{"@type": "WebPage", "name": x["name"] + " calories", "url": BASE + "/" + food_path(x["slug"])} for x in FOODS]}, faq_ld(hub_faq)]})
    body = f"""<body data-root="../">
{nav(d)}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="post food">
<header class="phead"><span class="label">Free nutrition guide</span><h1>South Asian Food Calorie Chart</h1>
<p class="lead">Calories and protein in {len(FOODS)} everyday Nepali and Indian foods, from roti and dal to momo and biryani, per normal serving and per 100 g. Every number comes from USDA FoodData Central.</p></header>
<div class="abody">
<p><label for="fq"><b>Search the chart</b></label><br><input id="fq" class="fq" type="search" placeholder="Try momo, roti, paneer…" autocomplete="off"></p>
{table}
<p class="fine" style="text-align:left">Tap a food for full nutrition, serving sizes, weight-loss and muscle-gain advice. Values are averages; your recipe may differ.</p>
<h2>How to use this chart</h2>
<ul><li><b>Losing weight?</b> Find your calorie target with the <a href="../calculators/calorie-deficit-calculator/">calorie deficit calculator</a>, then watch the big-ticket items: rice portions, cooking oil, ghee, fried snacks and sugary tea.</li>
<li><b>Building muscle?</b> Use the <a href="../calculators/protein-calculator/">protein calculator</a> and build each meal around a protein food: eggs, chicken, goat, fish, soybeans, dal, curd or paneer.</li>
<li><b>Cooking oil is the hidden calorie.</b> Each teaspoon adds about 40 calories, so measuring it is the easiest change most families can make.</li></ul>
<h2>Frequently asked questions</h2>
{faq_html(hub_faq)}
<h2>Source</h2>
<p><a href="https://fdc.nal.usda.gov/" rel="noopener">USDA FoodData Central</a>: SR Legacy (2018) and FNDDS survey foods (2019 release). Each food page lists its USDA entry and ID.</p>
</div>
{newsletter_box("foodhub")}
</article>
</div></main>
<script>(function(){{var q=document.getElementById('fq');if(!q)return;q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase();var rows=document.querySelectorAll('.fchart tbody tr');var last=null,shown=0;rows.forEach(function(r){{if(r.classList.contains('fg')){{if(last)last.style.display=shown?'':'none';last=r;shown=0;return;}}var ok=!v||r.getAttribute('data-q').indexOf(v)>-1;r.style.display=ok?'':'none';if(ok)shown++;}});if(last)last.style.display=shown?'':'none';}});}})();</script>
{footer(d)}{drawer()}{tail(d)}"""
    pages["food/"] = head("South Asian Food Calorie Chart (Nepali and Indian Foods)", f"Calories and protein in {len(FOODS)} Nepali and Indian foods: roti, rice, dal, momo, biryani, paneer and more. Per serving and per 100 g, from USDA data.", "food/", d, extra=j) + body
    sitemap.append(("food/", "0.8"))

    # ---- link food pages from relevant blog posts ----
    POSTMAP = {"momo-and-fitness": ["momo", "fried-momo", "chowmein"], "weight-loss-diet-plan-nepali-food": ["dal-bhat", "rice-white", "roti", "dal"],
               "how-many-eggs-per-day": ["egg", "milk", "curd"], "protein-rich-vegetarian-foods-nepal": ["soybeans", "dal", "chana", "palak-paneer"],
               "high-protein-nepali-diet-plan-for-muscle-gain": ["chicken-breast", "egg", "soybeans", "dal"], "how-much-protein-do-you-need": ["chicken-breast", "egg", "dal", "soybeans"],
               "high-protein-breakfast-ideas-nepal": ["egg", "oats", "curd", "milk"], "calorie-deficit-explained": ["dal-bhat", "mustard-oil", "chai"],
               "why-am-i-not-losing-weight": ["mustard-oil", "chai", "dal-bhat"], "how-to-gain-weight-fast-for-skinny-people": ["peanuts", "buffalo-milk", "banana", "ghee"],
               "healthy-nepali-snacks-for-gym": ["peanuts", "soybeans", "chana", "banana"], "how-many-calories-do-i-need": ["dal-bhat", "roti", "rice-white"],
               "how-to-lose-belly-fat": ["mustard-oil", "chai", "dal-bhat"]}
    for slug, fl in POSTMAP.items():
        k = f"blog/{slug}/"
        if k not in pages: continue
        links = " · ".join(f'<a href="../../{food_path(x)}">{e(_FBY[x]["name"])}</a>' for x in fl)
        box = f'<aside class="pask"><p><b>Calories in the foods in this article:</b> {links}. <a href="../../food/">See the full South Asian food calorie chart</a>.</p></aside>\n'
        pages[k] = pages[k].replace('<aside class="author">', box + '<aside class="author">', 1)

build_foods()
