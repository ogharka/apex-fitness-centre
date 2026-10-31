import zlib
import os, re, json, html, sys, shutil
BASE = os.environ.get("BASE_URL", "https://apexfitnesscentre.shop").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.join(HERE, "..", "_site"))
SRC = os.path.join(HERE, "assets")
GYM_SRC = os.path.join(HERE, "gym-source.html")
BLOG_DIR = os.path.join(HERE, "content", "blog")
WA = "9779708819605"
SITE = "Apex Fitness Centre"
# GOOGLE ANALYTICS 4: paste your real Measurement ID here (GA4 > Admin > Data streams > your web stream),
# then rebuild. Every page reads it from this one line.
GA_ID = "G-F70PH8VMHW"
# GOOGLE ADSENSE: paste your publisher ID when AdSense gives it to you, e.g. "ca-pub-1234567890123456".
# Leave it empty until then. When set, every page gets the AdSense Auto ads code and /ads.txt is created.
ADSENSE_CLIENT = ""
# Ads only on content pages, so they never distract buyers on shop and product pages.
ADS_ON = ("blog/", "guides/", "calculators/", "food/")
# EMAIL NEWSLETTER: create a free form at Kit (kit.com) or Mailchimp, then paste the form's "action" URL here,
# e.g. "https://app.kit.com/forms/1234567/subscriptions". Leave empty to hide the sign-up box everywhere.
NEWSLETTER_ACTION = ""
NEWSLETTER_FIELD = "email_address"  # Kit uses "email_address"; Mailchimp uses "EMAIL"
def newsletter_box(where="post"):
    if not NEWSLETTER_ACTION: return ""
    return (f'<aside class="nl" aria-labelledby="nl-h-{where}"><p class="nl-k">Free weekly email</p>'
            f'<h2 id="nl-h-{where}">One useful fitness tip a week</h2>'
            f'<p>Simple training and food tips from the trainers at Apex Fitness Centre. No spam, unsubscribe any time.</p>'
            f'<form action="{NEWSLETTER_ACTION}" method="post" target="_blank" rel="noopener">'
            f'<label class="sr-only" for="nl-e-{where}">Email address</label>'
            f'<input id="nl-e-{where}" type="email" name="{NEWSLETTER_FIELD}" required autocomplete="email" placeholder="Your email address">'
            f'<button class="btn" type="submit">Subscribe</button></form></aside>')
# GOOGLE SEARCH CONSOLE: when Search Console asks you to verify with an "HTML tag", paste only the
# content="..." value here, e.g. "abc123XYZ". Leave empty if you verify another way.
GSC_VERIFY = ""
# PINTEREST: website claim code (Pinterest > Settings > Claimed accounts > Websites)
PINTEREST_VERIFY = "67c45828ef91f9681356e1974e5102bc"
# STOCK per product. Default is in stock. To mark one product out of stock, add its slug here:
#   STOCK = {"scitron-volcano-pre-workout": "out"}
STOCK = {}
e = html.escape

PRODUCTS = [
 dict(slug="muscleblaze-creatine-monohydrate-320g-citrus-blast", brand="MuscleBlaze", name="MuscleBlaze Creatine Monohydrate", size="320 g", flavour="Citrus Blast",
      cat="creatine", price=2000, img="muscleblaze-creatine-320g.jpg",
      short="Creatine monohydrate, 320 g tub in Citrus Blast flavour.",
      title="MuscleBlaze Creatine Price in Nepal: {price} (320 g)",
      desc="MuscleBlaze creatine price in Nepal: {price} for Creatine Monohydrate 320 g (Citrus Blast). Authentic, free delivery all over Nepal. Order on WhatsApp.",
      about=["Creatine monohydrate is one of the most widely studied supplements for strength and power in high-intensity training such as lifting and sprinting.",
             "This 320 g tub comes in a Citrus Blast flavour, so it mixes into water or a shake without an unflavoured taste.",
             "Stocked and sold by Apex Fitness Centre, the gym in Urlabari-9, Morang. Delivery is free all over Nepal."],
      facts=[("Brand","MuscleBlaze"),("Product","Creatine Monohydrate"),("Pack size","320 g"),("Flavour","Citrus Blast"),("Price","Rs. 2,000")],
      use="Follow the serving size and directions printed on the tub label. Mix with water or a shake, drink enough water through the day, and check with a doctor first if you have a medical condition."),
 dict(slug="muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme", brand="MuscleBlaze", name="MuscleBlaze Biozyme Performance Whey", size="2 kg", flavour="French Vanilla Crème",
      cat="protein", price=15000, img="muscleblaze-biozyme-whey-2kg.jpg",
      short="Whey protein, 2 kg tub in French Vanilla Crème flavour.",
      title="MuscleBlaze Protein Price in Nepal: Biozyme Whey {price}",
      desc="MuscleBlaze protein price in Nepal: {price} for Biozyme Performance Whey 2 kg (French Vanilla Crème). Authentic, free delivery all over Nepal.",
      about=["Whey protein is a convenient way to add protein to your day, especially after training or when meals are short on protein.",
             "The 2 kg tub is the value size for regular lifters. Flavour is French Vanilla Crème, which mixes well with water or milk.",
             "Stocked and sold by Apex Fitness Centre, the gym in Urlabari-9, Morang. Delivery is free all over Nepal."],
      facts=[("Brand","MuscleBlaze"),("Product","Biozyme Performance Whey"),("Pack size","2 kg"),("Flavour","French Vanilla Crème"),("Price","Rs. 15,000")],
      use="Use the scoop provided and follow the serving size on the label. Mix with water or milk. Whey is a food supplement and does not replace a balanced diet."),
 dict(slug="scitron-volcano-pre-workout", brand="Scitron", name="Scitron Volcano Pre-Workout", size="30 packets", flavour="",
      cat="pre-workout", price=5000, img="scitron-volcano-pre-workout.jpg",
      short="Pre-workout with 30 packets per box, 300 mg caffeine per packet.",
      title="Scitron Volcano Pre-Workout 30 Packets Price in Nepal",
      desc="Buy Scitron Volcano Pre-Workout (30 packets, 300 mg caffeine each) in Nepal for Rs. 5,000. Free delivery across Nepal. Order on WhatsApp.",
      about=["A pre-workout supplement taken before training to help you start a session with focus and energy. Each box has 30 packets, so it is a month of single-serve packets for daily training.",
             "Each packet contains 300 mg of caffeine, which is a strong dose. Read the label, avoid taking it late in the evening, and do not combine it with other caffeine.",
             "Stocked and sold by Apex Fitness Centre, the gym in Urlabari-9, Morang. Delivery is free all over Nepal."],
      facts=[("Brand","Scitron"),("Product","Volcano Pre-Workout"),("Pack size","30 packets"),("Caffeine","300 mg per packet"),("Price","Rs. 5,000")],
      use="Follow the directions on the label. Each packet has 300 mg of caffeine. Avoid taking it late in the evening, and it is not meant for people under 18, pregnant or breastfeeding women, or anyone with a heart condition or high blood pressure."),
]
from newprods import NEW
PRODUCTS += NEW
WHO={"muscleblaze-creatine-monohydrate-320g-citrus-blast":["Lifters who want a flavoured creatine that is easy to drink","Anyone who wants the most grams per rupee: Rs. 6.25 per gram of product","People adding creatine to a daily routine with a shake or juice"],
"muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme":["Lifters who find it hard to eat enough protein from food","Members training most days who want the big, long-lasting 2 kg tub","Anyone who wants a quick shake after training"],
"scitron-volcano-pre-workout":["Lifters who need a push to start a hard session","Early-morning trainers: pre-workout helps when you wake up flat","Experienced users who are comfortable with 300 mg of caffeine"]}
PAIR={"muscleblaze-creatine-monohydrate-320g-citrus-blast":"muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme":"muscleblaze-creatine-monohydrate-320g-citrus-blast","scitron-volcano-pre-workout":"muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme"}
for p in PRODUCTS:
    p.setdefault("who", WHO.get(p["slug"])); p.setdefault("pair", PAIR.get(p["slug"]))
for p in PRODUCTS:
    for _k in ("title", "desc"): p[_k] = p[_k].replace("{price}", "Rs. {:,}".format(p["price"])) if "{price}" in p[_k] else p[_k]
    p["url"] = f"products/{p['slug']}/"
    p["full"] = " ".join(x for x in [p["name"], p["size"], ("(%s)" % p["flavour"]) if p["flavour"] else ""] if x)
    p["label"] = " ".join(x for x in [p["size"], p["flavour"]] if x)

CATS = [
 dict(slug="creatine", name="Creatine", h1="Buy Creatine in Nepal",
      title="Buy Creatine Monohydrate in Nepal | Apex Fitness Centre",
      desc="Buy creatine monohydrate in Nepal from Rs. 2,000: MuscleBlaze, Wellcore and BPI Sports. Free delivery all over Nepal. Order on WhatsApp.",
      intro="Creatine monohydrate is a staple for lifters who want strength and power from their training. We stock MuscleBlaze, Wellcore and BPI Sports creatine, from Rs. 2,000.",
      body=["Creatine is stored in your muscles and helps supply quick energy for short, hard efforts like heavy sets and sprints. It is one of the most studied sports supplements.",
            "Which one should you pick? Choose a flavoured tub (MuscleBlaze Citrus Blast or Wellcore Fruit Fusion) if you like a taste in your drink. Choose the unflavoured BPI Sports tub if you want to mix it into anything without changing the flavour."],
      faq=[("Which creatine is cheapest?","MuscleBlaze 320 g and Wellcore 307 g are each Rs. 2,000. BPI Sports Micronised Creatine 300 g is Rs. 5,000. Message us on WhatsApp to check what is in stock."),
           ("Can I get creatine delivered outside Urlabari?","Yes. Delivery is free all over Nepal. Order on WhatsApp and we confirm the delivery details with you."),
           ("How do I take creatine?","Follow the serving size on the label of the product you buy and drink enough water. If you have a medical condition, ask your doctor first."),
           ("Does creatine need a loading phase?","No. A small daily serving works. Loading is optional and just gets you there faster."),
           ("Do I take creatine on rest days?","Yes. Take it every day so the level in your muscles stays up."),
           ("Which creatine is better value?","Per gram, MuscleBlaze 320 g is Rs. 6.25, Wellcore 307 g is Rs. 6.51 and BPI Sports 300 g is Rs. 16.67. Pick the BPI tub if you prefer the brand.")]),
 dict(slug="protein", name="Protein", h1="Buy Whey Protein in Nepal",
      title="Buy Whey Protein in Nepal | MuscleBlaze, BigMan, BPI",
      desc="Buy whey protein in Nepal: MuscleBlaze Biozyme (Rs. 15,000), BigMan Forza (Rs. 17,500), BPI Hydro HD (Rs. 23,000), 2 kg each. Free delivery, order on WhatsApp.",
      intro="Whey protein makes it easier to reach your daily protein target. We stock MuscleBlaze Biozyme Performance Whey (Rs. 15,000), BigMan Forza Protein (Rs. 17,500) and BPI Sports Hydro HD Hydrolyzed Whey (Rs. 23,000), all in 2 kg tubs.",
      body=["Whey is a quick-mixing protein that many lifters use after training or between meals. It does not replace food, it adds to it.",
            "The 2 kg size is built for regular training and lasts longer than a small tub, so it suits members who train most days.",
            "BigMan Forza is a protein blend that, according to its label, also contains creatine and MCT. Check the label before adding a separate creatine so you do not double up."],
      faq=[("What is the price of MuscleBlaze Biozyme Whey 2 kg in Nepal?","At Apex Fitness Centre the MuscleBlaze Biozyme Performance Whey 2 kg is Rs. 15,000."),
           ("Do you deliver whey protein all over Nepal?","Yes, delivery is free all over Nepal. Order on WhatsApp and we confirm the details."),
           ("Which flavour is available?","French Vanilla Crème. Message us on WhatsApp to confirm current stock."),
           ("How much protein should I eat a day?","Lifters are often advised roughly 1.6 to 2.2 g per kg of body weight a day. Get most of it from food and use whey to fill the gap."),
           ("When should I drink whey?","Many people have a shake after training or between meals. Total protein across the day matters most."),
           ("Can I take whey and creatine together?","Yes. They are commonly taken together, for example in the same post-workout shake.")]),
 dict(slug="pre-workout", name="Pre-workout", h1="Buy Pre-Workout in Nepal",
      title="Buy Pre-Workout in Nepal | Scitron Volcano | Apex Fitness",
      desc="Buy pre-workout in Nepal: Scitron Volcano, 30 single-serve packets with 300 mg caffeine, Rs. 5,000. How to use it safely. Free delivery, order on WhatsApp.",
      intro="A pre-workout is for the days you need extra focus and energy to start training. We stock Scitron Volcano Pre-Workout, 30 packets per box, at Rs. 5,000.",
      body=["Scitron Volcano has 300 mg of caffeine in each of its 30 packets, a strong dose. Read the label and avoid taking it late in the evening.",
            "Pre-workout is not meant for under 18s, pregnant or breastfeeding women, or anyone with heart conditions or high blood pressure."],
      faq=[("What is the price of Scitron Volcano Pre-Workout in Nepal?","At Apex Fitness Centre, Scitron Volcano Pre-Workout is Rs. 5,000."),
           ("Is pre-workout safe for everyone?","No. Scitron Volcano has 300 mg of caffeine per packet. Read the label and speak to a doctor if you have a medical condition."),
           ("How many packets are in a box?","30 packets per box."),
           ("When should I take it?","About 20 to 30 minutes before training, and not late in the evening.")]),
]
from newcats import NEWCATS
CATS += NEWCATS
for c in CATS:
    c["products"] = [p for p in PRODUCTS if p["cat"] == c["slug"]]
    c["url"] = c["slug"] + "/"

HOME_FAQ = [
 ("Do you deliver supplements all over Nepal?","Yes, and delivery is free all over Nepal. Delivery is free. Order on WhatsApp and we confirm your address and delivery time before dispatch."),
 ("How do I order?","Add products to your cart and tap Order on WhatsApp. Your cart arrives in our WhatsApp chat as a ready message. We confirm stock and delivery with you."),
 ("How do I pay?","We accept Khalti and bank transfer. We send you the payment details on WhatsApp when you order."),
 ("What brands do you sell?","MuscleBlaze, Wellcore, BPI Sports, BigMan, Scitron, Pole Nutrition, Pintola and Valeo: creatine, protein, pre-workout, BCAA, L-carnitine, omega-3, protein oats and lifting belts. All products are authentic, bought from authorised sellers."),
 ("Where are you based?","Apex Fitness Centre, Urlabari-9, Durgapuri, Morang. We are a gym first, open 4:30 AM to 8:30 PM Sunday to Friday, and you can also pick up supplements in person."),
 ("Can I check stock before ordering?","Yes. Message us on WhatsApp at 9708819605 and we will tell you what is in stock today."),
]

RULES = [  # applied in order, best first
 dict(name="Complete Training Stack", slugs=["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast","scitron-volcano-pre-workout"], off=1000),
 dict(name="Muscle Gain Stack", slugs=["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast"], off=500),
 dict(name="Whey + Wellcore creatine", slugs=["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","wellcore-micronised-creatine-monohydrate-307g-fruit-fusion"], off=500),
 dict(name="Whey + Volcano pre-workout", slugs=["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","scitron-volcano-pre-workout"], off=500),
 # "Frequently bought together" pairs on product pages: every pair gets a real discount (Rs. 300-500)
 dict(name="BigMan Forza + Volcano", slugs=["bigman-forza-protein-2kg","scitron-volcano-pre-workout"], off=500),
 dict(name="BPI creatine + whey", slugs=["bpi-sports-micronized-creatine-300g-unflavored","muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme"], off=500),
 dict(name="BCAA + creatine", slugs=["bpi-sports-best-bcaa-30-servings-grape","muscleblaze-creatine-monohydrate-320g-citrus-blast"], off=400),
 dict(name="L-carnitine + CLA", slugs=["muscleblaze-l-carnitine-pro-liquid-450ml-key-lime","bpi-sports-cla-carnitine-370g-fruit-punch"], off=400),
 dict(name="Omega-3 + whey", slugs=["pole-nutrition-omega-3-fish-oil-1000mg","muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme"], off=500),
 dict(name="Protein oats + whey", slugs=["pintola-high-protein-oats-chocolate-1kg","muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme"], off=300),
 dict(name="Lifting belt + BigMan Forza", slugs=["valeo-weightlifting-belt","bigman-forza-protein-2kg"], off=500),
 dict(name="Hydro HD whey + creatine", slugs=["bpi-sports-hydro-hd-hydrolyzed-whey-2kg-chocolate-lava-cake","muscleblaze-creatine-monohydrate-320g-citrus-blast"], off=500),
]
# Every bundle discount must stay within the site banner "Stack and save up to Rs. 1,000"
assert max(r["off"] for r in RULES) == 1000
def save_for(slugs):
    s = set(slugs)
    for rl in RULES:
        if set(rl["slugs"]) == s: return rl["off"]
    return 0
def money(n): return "Rs. {:,}".format(n)
def wa(msg): return f"https://wa.me/{WA}?text=" + __import__("urllib.parse").parse.quote(msg)
def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>"

ORG = {"@type": "Organization", "@id": BASE + "/#org", "name": SITE, "url": BASE + "/", "publishingPrinciples": BASE + "/editorial-policy/", "logo": BASE + "/assets/apex-icon-512.png",
       "telephone": "+977-9708819605", "sameAs": ["https://www.facebook.com/apexfitcentre"]}
STORE = {"@type": ["SportsActivityLocation", "Store"], "@id": BASE + "/#store", "name": SITE, "url": BASE + "/",
         "image": BASE + "/assets/og-image.jpg", "telephone": "+977-9708819605", "priceRange": "Rs. 1,500 - Rs. 15,000",
         "address": {"@type": "PostalAddress", "streetAddress": "Urlabari-9, Durgapuri", "addressLocality": "Urlabari", "addressRegion": "Morang", "addressCountry": "NP"},
         "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "04:30", "closes": "20:30"}],
         "areaServed": {"@type": "Country", "name": "Nepal"}, "sameAs": ["https://www.facebook.com/apexfitcentre"]}

def head(title, desc, path, depth, image=None, extra="", ptype="website"):
    root = "../" * depth
    canon = BASE + "/" + path
    img = image or "assets/og-image.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{ga_tag()}{adsense_tag(path)}{gsc_tag()}<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#ffffff">
<link rel="apple-touch-icon" href="{root}assets/apex-icon-180.png">
<meta property="og:site_name" content="{SITE}">
<meta property="og:type" content="{ptype}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/{img}">
<meta property="og:locale" content="en_NP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}/{img}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/store.css">
<link rel="stylesheet" href="{root}assets/premium.css">
{extra}
</head>
"""

def gsc_tag():
    t = f'<meta name="google-site-verification" content="{GSC_VERIFY}">\n' if GSC_VERIFY else ""
    if PINTEREST_VERIFY: t += f'<meta name="p:domain_verify" content="{PINTEREST_VERIFY}"/>\n'
    return t

def adsense_tag(path=""):
    if not ADSENSE_CLIENT or not path.startswith(ADS_ON): return ""
    return f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>\n<meta name="google-adsense-account" content="{ADSENSE_CLIENT}">\n'

def ga_tag():
    """GA4 tag plus a 'whatsapp_order' event on every click of a wa.me link.
    The product name comes from data-product on the link (or its nearest parent), else the page H1.
    Nothing is added until a real ID is set, so no wasted requests with the placeholder."""
    if not re.fullmatch(r"G-[A-Z0-9]{6,12}", GA_ID) or GA_ID == "G-XXXXXXXXXX": return ""
    return f"""<!-- Google tag (gtag.js). Real ID goes in GA_ID at the top of build.py -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA_ID}');
document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href*="wa.me/"]');if(!a)return;var s=a.closest('[data-product]'),h=document.querySelector('h1');
var v=s&&parseFloat(s.getAttribute('data-value'));var p={{product_name:(s&&s.getAttribute('data-product'))||(h&&h.textContent.replace(/\\s+/g,' ').trim())||document.title,link_url:a.href,page_path:location.pathname,transport_type:'beacon'}};if(v){{p.value=v;p.currency='NPR'}}
gtag('event','whatsapp_order',p)}},true);</script>
"""

def nav(depth, active=""):
    r = "../" * depth
    def a(href, label, key):
        return f'<a href="{r}{href}"' + (' class="on"' if active == key else "") + f">{label}</a>"
    return f"""<div class="ann">Free delivery all over Nepal &middot; Authentic products &middot; Bundles save up to Rs. 1,000</div>
<header class="top"><div class="wrap">
<a class="brand" href="/"><span class="wm">APEX</span><span class="wm2">Fitness<br>Centre</span></a>
<nav aria-label="Main"><ul>
<li>{a("shop/","Shop","shop")}</li><li>{a("creatine/","Creatine","creatine")}</li><li>{a("protein/","Protein","protein")}</li><li>{a("pre-workout/","Pre-workout","pre-workout")}</li><li>{a("blog/","Blog","blog")}</li><li>{a("gym/","The gym","gym")}</li><li>{a("software/","For gyms","software")}</li><li>{a("calculators/","Calculators","calculators")}</li>
</ul></nav>
<button class="cartbtn" id="cartOpen" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h2l2.4 11h10.2L20 7H6.2"/><circle cx="9" cy="19" r="1.4"/><circle cx="17" cy="19" r="1.4"/></svg><span>Cart</span><b id="cartCount">0</b></button>
</div></header>
"""

def drawer():
    return """<div class="scrim" id="scrim" hidden></div>
<aside class="drawer" id="drawer" aria-label="Your cart" aria-hidden="true">
<div class="dh"><h2>Your cart</h2><button type="button" id="cartClose" aria-label="Close cart">Close</button></div>
<div class="db" id="cartBody"></div>
<div class="df" id="cartFoot"></div>
</aside>
"""

def footer(depth, pdp=None):
    r = "../" * depth
    if pdp:
        pm = f"Hi Apex Fitness Centre, I want to order: {pdp['full']} for {money(pdp['price'])}. Please confirm stock and send payment details."
        mbar = f'<div class="mbar pdpbar" data-product="{e(pdp["full"])}" data-value="{pdp["price"]}"><a class="btn wa" href="{wa(pm)}" target="_blank" rel="noopener">Order on WhatsApp</a><button class="btn line" type="button" data-add="{pdp["slug"]}">Add &middot; {money(pdp["price"])}</button><button class="btn" type="button" id="cartOpen2">Cart <b id="cartCount2">0</b></button></div>'
    else:
        mbar = f'<div class="mbar"><a class="btn wa" href="https://wa.me/{WA}?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20have%20a%20question%20about%20supplements." target="_blank" rel="noopener">WhatsApp</a><button class="btn" type="button" id="cartOpen2">Cart <b id="cartCount2">0</b></button></div>'
    cat_links = "".join(f'<a href="{r}{c["url"]}">{c["name"]}</a>' for c in CATS)
    return f"""<footer><div class="wrap">
<div class="fgrid">
<div><div class="fname brand"><span class="wm">APEX</span><span class="wm2">Fitness<br>Centre</span></div><p>Authentic supplements with free delivery all over Nepal. Gym in Urlabari-9, Durgapuri, Morang, open 4:30 AM to 8:30 PM, Sunday to Friday.</p></div>
<div><h3>Shop</h3><a href="{r}shop/">All products</a>{cat_links}</div>
<div><h3>Apex</h3><a href="{r}blog/">Blog</a><a href="{r}guides/">Supplement guides</a><a href="{r}gym/">The gym and membership</a><a href="{r}gym/#team">Team</a><a href="{r}gym/#plans">Plans</a><a href="{r}calculators/">Fitness calculators</a><a href="{r}food/">Food calorie chart</a><a href="{r}software/">Gym management software Nepal</a><a href="{r}software/#pricing">Gym software price</a></div>
<div><h3>Contact</h3><a href="https://wa.me/{WA}" rel="noopener" target="_blank">WhatsApp 9708819605</a><a href="tel:+9779708819605">Call 9708819605</a><a href="https://www.facebook.com/apexfitcentre" rel="noopener" target="_blank">Facebook</a><a href="{r}about/">About us</a><a href="{r}contact/">Contact</a><a href="{r}privacy/">Privacy policy</a><a href="{r}editorial-policy/">Editorial policy</a></div>
</div>
<div class="fcopy"><span>© <span id="yr">2026</span> Apex Fitness Centre. All rights reserved.</span><span>Free delivery all over Nepal</span></div>
</div></footer>
{mbar}"""

def tail(depth):
    return f'<script src="{"../"*depth}assets/store-data.js"></script>\n<script src="{"../"*depth}assets/store.js"></script>\n</body></html>\n'

def card(p, depth):
    r = "../" * depth
    price = money(p["price"])
    return f"""<article class="pcard" data-slug="{p['slug']}">
<a class="pimg" href="{r}{p['url']}"><img src="{r}assets/{p['img']}" alt="{e(p['full'])}" width="640" height="640" loading="lazy"></a>
<div class="pbody">
<span class="pbrand">{e(p['brand'])}</span>
<h3><a href="{r}{p['url']}">{e(p['name'])}</a></h3>
<p class="plabel">{e(p['label']) if p['label'] else e(p['short'])}</p>
<div class="prow"><span class="price">{price}</span><button class="add" type="button" data-add="{p['slug']}">Add to cart</button></div>
</div></article>"""

def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"

def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + "/" + u} for i, (n, u) in enumerate(items)]}

def crumb_html(items, depth):
    r = "../" * depth
    parts = []
    for i, (n, u) in enumerate(items):
        parts.append(f'<a href="{r}{u}">{e(n)}</a>' if i < len(items) - 1 else f"<span>{e(n)}</span>")
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

pages = {}  # path -> html
sitemap = []  # (path, priority)

# HOME
def stack(name, text, slugs):
    ps = [next(x for x in PRODUCTS if x["slug"] == s) for s in slugs]
    full = sum(x["price"] for x in ps)
    off = save_for(slugs)
    tot = full - off
    imgs = "".join(f'<img src="assets/{x["img"]}" alt="{e(x["full"])}" width="640" height="640" loading="lazy">' for x in ps)
    lis = "".join(f'<li><a href="{x["url"]}">{e(x["name"])}</a><span>{money(x["price"])}</span></li>' for x in ps)
    return f'''<div class="stack"><div class="simgs">{imgs}</div><h3>{name}</h3><p>{text}</p><ul>{lis}</ul><div class="stot"><span>Stack price <s>{money(full)}</s></span><b class="price">{money(tot)}</b></div><p class="save">You save {money(off)}</p><button class="btn gold full" type="button" data-bundle="{",".join(slugs)}">Add the stack to cart</button></div>'''

def marquee():
    # Prices come from PRODUCTS, the same list that builds /shop/, so they cannot drift apart.
    def item(p, dup):
        alt = "" if dup else e(p["full"])
        tab = ' tabindex="-1"' if dup else ""
        return (f'<a href="{p["url"]}"{tab}><img src="assets/{p["img"]}" alt="{alt}" width="160" height="160" loading="lazy">'
                f'<span>{e(p["brand"])}</span><b class="mqp">{money(p["price"])}</b></a>')
    one = "".join(item(p, False) for p in PRODUCTS)
    two = "".join(item(p, True) for p in PRODUCTS)
    # The second copy only exists to make the scroll loop seamless, so screen readers skip it.
    return (f'<div class="mq" role="region" aria-label="Products we sell"><div class="mqt">'
            f'<div class="mqg">{one}</div><div class="mqg" aria-hidden="true">{two}</div></div></div>')

def build_home():
    d = 0
    p0 = PRODUCTS[2]
    title = "Buy Authentic Supplements Online in Nepal | Apex Fitness"
    desc = "Buy authentic creatine, whey protein, pre-workout and BCAA online in Nepal: MuscleBlaze, BPI Sports, Wellcore. Free delivery across Nepal, order on WhatsApp."
    j = ld({"@context": "https://schema.org", "@graph": [ORG, STORE,
        {"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": SITE, "publisher": {"@id": BASE + "/#org"}},
        faq_ld(HOME_FAQ)]})
    h = head(title, desc, "", d, extra=j)
    cats = "".join(f"""<a class="ccard" href="{c['url']}"><span class="cimg"><img src="assets/{c['products'][0]['img']}" alt="{e(c['name'])} supplements" width="640" height="640" loading="lazy"></span><span class="ctext"><b>{c['name']}</b><small>{len(c['products'])} product{'s' if len(c['products'])>1 else ''} from {money(min(x['price'] for x in c['products']))}</small></span></a>""" for c in CATS)
    FEAT = ["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","bigman-forza-protein-2kg","muscleblaze-creatine-monohydrate-320g-citrus-blast","wellcore-micronised-creatine-monohydrate-307g-fruit-fusion","scitron-volcano-pre-workout","bpi-sports-best-bcaa-30-servings-grape","muscleblaze-l-carnitine-pro-liquid-450ml-key-lime","valeo-weightlifting-belt"]
    feat = "".join(card(next(x for x in PRODUCTS if x["slug"] == s), d) for s in FEAT) + ''

    body = f"""<body data-root="">
{nav(d)}
<main>
<section class="hero"><div class="wrap hgrid">
<div class="htext">
<span class="label">Supplements store, Nepal</span>
<h1>Genuine supplements.<br><em>Free delivery all over Nepal.</em></h1>
<p class="lead">Creatine, protein, pre-workout, BCAA and more from MuscleBlaze, BPI Sports, Wellcore and other brands. Pick your products, send the order on WhatsApp, and we confirm delivery with you.</p>
<div class="cta"><a class="btn gold" href="shop/">Shop all products</a><a class="btn wa" href="https://wa.me/{WA}?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%20supplements." target="_blank" rel="noopener">Order on WhatsApp</a></div>
<ul class="ticks"><li>Free delivery all over Nepal</li><li>Authentic products</li><li>Pay by Khalti or bank</li></ul>
</div>
<div class="hfeat"><span class="hbadge">Customer reviewed</span><a class="hshow" href="{PRODUCTS[2]['url']}"><img src="assets/{PRODUCTS[2]['img']}" alt="{e(PRODUCTS[2]['full'])}" width="640" height="640" fetchpriority="high"></a>
<div class="hcap"><span class="pbrand">Featured</span><b>{e(PRODUCTS[2]['name'])}</b><span class="price">{money(PRODUCTS[2]['price'])}</span></div></div>
</div></section>

{marquee()}
<section class="trust"><div class="wrap"><ul>
<li><b>100% authentic</b><span>Bought from authorised sellers</span></li>
<li><b>Free delivery</b><span>All over Nepal, no minimum</span></li>
<li><b>Khalti and bank</b><span>Easy, safe payment</span></li>
<li><b>A real gym</b><span>Urlabari-9, Morang, open Sun to Fri</span></li>
</ul></div></section>
<section class="sec"><div class="wrap">
<div class="shead"><span class="label">What is your goal?</span><h2>Start with what you want</h2><p>Not sure what to buy? Pick your goal and we will point you to the right product.</p></div>
<div class="goals">
<a class="goal" href="protein/"><h3>Build muscle and recover</h3><p>Hit your daily protein with a whey shake after training.</p><span>Whey protein &rarr;</span></a>
<a class="goal" href="creatine/"><h3>Get stronger, lift more</h3><p>The most researched supplement for strength and power.</p><span>Creatine &rarr;</span></a>
<a class="goal" href="pre-workout/"><h3>More energy to train</h3><p>Focus and drive for early mornings and hard sessions.</p><span>Pre-workout &rarr;</span></a>
</div></div></section>

<section class="sec alt"><div class="wrap">
<div class="shead"><span class="label">Best value stacks</span><h2>Buy the pair that works together</h2><p>Buy together and save. The discount is applied automatically in your cart.</p></div>
<div class="stacks">
{stack("Muscle Gain Stack","Whey protein for recovery and creatine for strength. The classic starter pair.",["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast"])}
{stack("Complete Training Stack","Protein, creatine and a pre-workout. Everything for training, in one order.",["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast","scitron-volcano-pre-workout"])}
</div></div></section>

<section class="sec"><div class="wrap">
<div class="shead"><span class="label">Shop by category</span><h2>Find your supplement</h2></div>
<div class="cgrid">{cats}</div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="shead"><span class="label">Popular</span><h2>Best sellers and new arrivals</h2><p>Prices in Nepali rupees. Free delivery all over Nepal.</p></div>
<div class="pgrid">{feat}</div>
<p class="more"><a class="btn line" href="shop/">View all {len(PRODUCTS)} products</a></p>
</div></section>

{home_reviews()}

<section class="sec alt"><div class="wrap">
<div class="shead"><span class="label">How it works</span><h2>Order in three steps</h2></div>
<ol class="steps">
<li><b>1</b><div><h3>Add to cart</h3><p>Choose your products and quantity. No sign up needed.</p></div></li>
<li><b>2</b><div><h3>Send on WhatsApp</h3><p>Tap Order on WhatsApp. Your cart arrives as a ready message.</p></div></li>
<li><b>3</b><div><h3>We confirm and deliver</h3><p>We confirm stock, payment and your address, then ship anywhere in Nepal.</p></div></li>
</ol>
</div></section>

<section class="sec swteaser"><div class="wrap two">
<div><span class="label">For gym owners</span><h2>Run your own gym like we run ours</h2>
<p>Apex Gym Management is the software behind Apex Fitness Centre: members, dues, freeze, WhatsApp reminders, sales and automatic backup in one program. Rs. 25,000 one-time, no monthly fee. Ask for a free demo.</p>
<div class="cta"><a class="btn gold" href="software/">See gym software and price</a></div></div>
<figure class="shot"><img src="assets/software-dashboard.jpg" alt="Apex Gym Management dashboard" width="1200" height="720" loading="lazy"><figcaption>Apex Gym Management (sample data)</figcaption></figure>
</div></section>

<section class="sec alt"><div class="wrap two">
<div><span class="label">About Apex</span><h2>A gym first, so we know what we sell</h2>
<p>Apex Fitness Centre is a gym in Urlabari-9, Durgapuri, Morang. The supplements we sell here are the ones we know members ask for every day. You can order online from anywhere in Nepal or pick up in person.</p>
<a class="btn line" href="gym/">Visit the gym page</a></div>
<figure class="shot"><img src="assets/gym-free-weights.jpg" alt="Free weights area at Apex Fitness Centre, Urlabari" width="1000" height="750" loading="lazy"><figcaption>Free weights at Apex Fitness Centre</figcaption></figure>
</div></section>

<section class="sec alt"><div class="wrap narrow">
<div class="shead"><span class="label">Questions</span><h2>Ordering and delivery</h2></div>
{faq_html(HOME_FAQ)}
</div></section>
</main>
{footer(d)}{drawer()}{tail(d)}"""
    pages[""] = h + body
    sitemap.append(("", "1.0"))

def build_shop():
    d = 1
    title = "Shop Supplements Online in Nepal | Apex Fitness Centre"
    desc = "All supplements at Apex Fitness Centre: creatine, protein, pre-workout, BCAA, L-carnitine, omega-3 and more from Rs. 1,300. Free delivery, order on WhatsApp."
    items = [{"@type": "ListItem", "position": i + 1, "url": BASE + "/" + p["url"], "name": p["full"]} for i, p in enumerate(PRODUCTS)]
    cr = [("Home", ""), ("Shop", "shop/")]
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "CollectionPage", "name": "Shop supplements", "url": BASE + "/shop/", "mainEntity": {"@type": "ItemList", "itemListElement": items}}]})
    chips = "".join(f'<a class="chip" href="../{c["url"]}">{c["name"]}</a>' for c in CATS)
    body = f"""<body data-root="../">
{nav(d,"shop")}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="shead left"><h1>Shop supplements</h1><p>Creatine, protein, pre-workout, BCAA, L-carnitine, omega-3, oats and gym gear. Free delivery all over Nepal, order on WhatsApp.</p></div>
<div class="chips">{chips}</div>
<h2 class="sr-only">All products</h2>
<div class="pgrid">{''.join(card(p, d) for p in PRODUCTS)}</div>
<div class="note"><b>Not sure what to pick?</b> Message us on WhatsApp and we will help you choose.<a class="btn wa" href="https://wa.me/{WA}" target="_blank" rel="noopener">Ask on WhatsApp</a></div>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
    pages["shop/"] = head(title, desc, "shop/", d, extra=j) + body
    sitemap.append(("shop/", "0.9"))

CAT_EXTRA = {
"creatine": '''<section class="guide"><h2 class="h2s">What creatine does for you</h2>
<div class="gg"><div><b>More strength and power</b><p>Creatine helps your muscles make quick energy for heavy sets and sprints, so you can often squeeze out extra reps over time.</p></div>
<div><b>Better lean mass over time</b><p>Used with training and enough protein, creatine is linked with greater lean muscle gains.</p></div>
<div><b>Simple and cheap</b><p>One small serving a day. No cycling needed and no timing tricks. Consistency is what counts.</p></div></div></section>
<section class="guide"><h2 class="h2s">Which creatine should you buy?</h2>
@@CMP@@
<p class="fine">Best value per gram: the MuscleBlaze 320 g, then the Wellcore 307 g. BPI Sports costs more and suits people who prefer that brand.</p></section>
<section class="guide"><h2 class="h2s">How to take creatine</h2>
<ol class="how"><li><b>Take a small serving every day.</b> Studies commonly use 3 to 5 g a day. Follow the label.</li><li><b>Any time works.</b> Pick a time you will remember, like with your post-workout shake.</li><li><b>Stay consistent.</b> Take it on rest days too. Creatine builds up in your muscles over a few weeks.</li><li><b>Drink water through the day.</b> Check with a doctor first if you have a kidney or other medical condition.</li></ol></section>''',
"protein": '''<section class="guide"><h2 class="h2s">Why add whey to your day</h2>
<div class="gg"><div><b>Hit your protein target</b><p>Lifters are often advised to eat roughly 1.6 to 2.2 g of protein per kg of body weight a day. A shake makes that easier.</p></div>
<div><b>Quick after training</b><p>Whey mixes in seconds, with no cooking, so it is easy straight after the gym.</p></div>
<div><b>Great value in 2 kg</b><p>The big tub lasts weeks of daily training and keeps your protein steady.</p></div></div></section>
<section class="guide"><h2 class="h2s">How to use whey</h2>
<ol class="how"><li><b>After training.</b> One serving in water or milk within a couple of hours of your workout.</li><li><b>Between meals.</b> A shake is a quick way to add protein on busy days.</li><li><b>Mix it into food.</b> Stir into oats, curd or a smoothie for a high-protein snack.</li><li><b>Keep food first.</b> Whey adds to a balanced diet. It does not replace meals.</li></ol></section>
<section class="guide"><h2 class="h2s">Build a stronger stack</h2><p class="fine" style="text-align:left">Most lifters pair whey with creatine for strength and recovery.</p><div class="stacks one">@@MG@@</div></section>''',
"pre-workout": '''<section class="guide"><h2 class="h2s">How to use pre-workout safely</h2>
<ol class="how"><li><b>Take it 20 to 30 minutes before training.</b> One packet, mixed as the label says.</li><li><b>Know the dose.</b> Each Volcano packet has 300 mg of caffeine, which is a high dose. Do not add coffee or other caffeine on top.</li><li><b>Keep it for the morning and afternoon.</b> Taking it late can ruin your sleep.</li><li><b>Not for everyone.</b> Skip it if you are under 18, pregnant or breastfeeding, or have heart problems or high blood pressure.</li></ol></section>
<section class="guide"><h2 class="h2s">Pair it with</h2><div class="stacks one">@@CT@@</div></section>'''}

def stack_rel(name, text, slugs):
    return stack(name, text, slugs).replace('src="assets/','src="../assets/').replace('href="products/','href="../products/')

def build_cat(c):
    d = 1
    cr = [("Home", ""), ("Shop", "shop/"), (c["name"], c["url"])]
    items = [{"@type": "ListItem", "position": i + 1, "url": BASE + "/" + p["url"], "name": p["full"]} for i, p in enumerate(c["products"])]
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "CollectionPage", "name": c["h1"], "url": BASE + "/" + c["url"], "mainEntity": {"@type": "ItemList", "itemListElement": items}}, faq_ld(c["faq"])]})
    others = "".join(f'<a class="chip" href="../{x["url"]}">{x["name"]}</a>' for x in CATS if x is not c)
    extra = CAT_EXTRA.get(c["slug"], "")
    if "@@CMP@@" in extra:
        cps = c["products"]
        def pg(x):
            g = float(re.search(r"(\d+)", x["size"]).group(1)); return "Rs. %.2f" % (x["price"] / g)
        head_ = "".join(f"<th>{e(x['brand'])}<br><span class='cs'>{e(x['size'])}</span></th>" for x in cps)
        rows = "".join(f"<tr><th>{lab}</th>{''.join(f'<td>{v(x)}</td>' for x in cps)}</tr>" for lab, v in [("Flavour", lambda x: e(x["flavour"])), ("Price", lambda x: money(x["price"])), ("Price per gram", pg)])
        btns = "".join(f"<td><button class='add' type='button' data-add='{x['slug']}'>Add to cart</button></td>" for x in cps)
        tbl = f'<div class="tw"><table class="cmp"><thead><tr><th></th>{head_}</tr></thead><tbody>{rows}<tr><th></th>{btns}</tr></tbody></table></div>'
        extra = extra.replace("@@CMP@@", tbl)
    extra = extra.replace("@@MG@@", stack_rel("Muscle Gain Stack","Whey protein and creatine, the classic pair.",["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast"])).replace("@@CT@@", stack_rel("Complete Training Stack","Protein, creatine and a pre-workout in one order.",["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme","muscleblaze-creatine-monohydrate-320g-citrus-blast","scitron-volcano-pre-workout"]))
    body = f"""<body data-root="../">
{nav(d, c['slug'])}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="shead left"><h1>{e(c['h1'])}</h1><p>{e(c['intro'])}</p></div>
<h2 class="sr-only">Products</h2>
<div class="pgrid">{''.join(card(p, d) for p in c['products'])}</div>
<section class="prose"><h2>Choosing {c['name'].lower()}</h2>{''.join(f'<p>{e(t)}</p>' for t in c['body'])}</section>
{extra}
{guide_links(d, c['slug'])}
<section class="narrow"><h2 class="h2s">Questions</h2>{faq_html(c['faq'])}</section>
<div class="chips"><span>Also shop:</span>{others}<a class="chip" href="../shop/">All products</a></div>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
    pages[c["url"]] = head(c["title"], c["desc"], c["url"], d, image="assets/" + c["products"][0]["img"], extra=j) + body
    sitemap.append((c["url"], "0.8"))

# Real customer reviews only. Add entries like:
# dict(product="slug", name="Rohan", town="Biratnagar", text="...", date="2026-10-20", image="reviews/rohan.jpg")
REVIEWS = [
 dict(product="scitron-volcano-pre-workout", name="Rupak Shrestha", rating=5, image="reviews/rupak-shrestha.jpg", alt="Rupak Shrestha with Scitron Volcano pre-workout",
      text="Aila market ma vayeko aru preworkout vanda yo linu thalexi mero energy level nai beglai xa. Malai lagxa Nepal ma paune sabse best preworkout nai yoi ho.",
      en="My energy level has been completely different since I started this, compared with the other pre-workouts on the market. I think this is the best pre-workout available in Nepal."),
 dict(product="muscleblaze-l-carnitine-pro-liquid-450ml-key-lime", name="Nugen Limbu", rating=4, image="reviews/nugen-limbu.jpg", alt="Nugen Limbu with MuscleBlaze L-Carnitine",
      text="Thankyou Apex for selling genuine product in such affordable price.", en=""),
 dict(product="pintola-high-protein-oats-chocolate-1kg", name="Ranjeet Shrestha", rating=4, image="reviews/ranjeet-shrestha.jpg", alt="Ranjeet Shrestha with Pintola High Protein Oats",
      text="Yesle weight loss progress ma malai ramro help garyo.", en="This helped me well with my weight loss progress.", note="Personal experience. Results vary from person to person."),
 dict(product="muscleblaze-creatine-monohydrate-320g-citrus-blast", name="Hemraj Ojha", rating=5, image="reviews/hemraj-ojha.jpg", alt="Hemraj Ojha with MuscleBlaze Creatine",
      text="Ma aru supplement kai use gardina tara creatine chai linxu. Yo MB creatine ko taste chai malai man parxa.",
      en="I don't use other supplements, but I do take creatine. I like the taste of this MB creatine."),
 dict(product="wellcore-micronised-creatine-monohydrate-307g-fruit-fusion", name="Devi Ghising", rating=5, town="Lives in Hong Kong", image="reviews/devi-ghising.jpg", alt="Devi Ghising with Wellcore Micronised Creatine",
      text="Ma Hong Kong basxu, yearly ek chuti auxu. Jaila auda Apex bata 3-4 pc lagera janchu, malai saal bhar pugxa.",
      en="I live in Hong Kong and come home once a year. Whenever I come, I take 3-4 pieces from Apex, and it lasts me the whole year."),
]
_PNAME = {p["slug"]: p["name"] for p in PRODUCTS}

def rev_card(x, d, link=True):
    pn = _PNAME[x["product"]]
    prod = next(p for p in PRODUCTS if p["slug"] == x["product"])
    who = e(x["name"]) + (f", {e(x['town'])}" if x.get("town") else "")
    img = f'<img src="{"../"*d}assets/{x["image"]}" alt="{e(x["alt"])}" width="450" height="450" loading="lazy">'
    en = f'<p class="en"><span>English:</span> {e(x["en"])}</p>' if x.get("en") else ""
    note = f'<p class="fine" style="text-align:left">{e(x["note"])}</p>' if x.get("note") else ""
    pl = f'<a class="tl" href="{"../"*d}{prod["url"]}">{e(pn)}</a>' if link else e(pn)
    return f'<figure class="rv1">{img}<div class="stars" role="img" aria-label="Rated {x["rating"]} out of 5">{"&#9733;"*x["rating"]}<span>{"&#9733;"*(5-x["rating"])}</span> <b>{x["rating"]}/5</b></div><blockquote>&ldquo;{e(x["text"])}&rdquo;</blockquote>{en}{note}<figcaption><b>{who}</b><br>Bought: {pl}</figcaption></figure>'

def reviews_block(p):
    rv = [x for x in REVIEWS if x["product"] == p["slug"]]
    msg = f"Hi Apex Fitness Centre, I bought {p['full']} and here is my review: "
    ask = f'<p class="fine">Bought this from us? <a class="tl" href="{wa(msg)}" target="_blank" rel="noopener">Send us your review on WhatsApp</a> and we will show it here.</p>'
    if not rv:
        return f'<div class="revask"><p>Bought this? Send us a review on WhatsApp.</p><a class="btn line" href="{wa(msg)}" target="_blank" rel="noopener">Send a review</a></div>'
    items = "".join(rev_card(x, 2, link=False) for x in rv)
    return f'<section class="rev"><h2 class="h2s">Customer reviews</h2><div class="rvg one">{items}</div>{ask}</section>'

def home_reviews():
    items = "".join(rev_card(x, 0) for x in REVIEWS)
    tr = "".join(f'<figure><img src="assets/reviews/{n}.jpg" alt="{a}" width="400" height="400" loading="lazy"><figcaption>{c}</figcaption></figure>' for n, a, c in [("ashish-before","Ashis Neupane in school uniform, before training at Apex","Before"),("ashish-after-1","Ashis Neupane training at Apex Fitness Centre","After joining Apex"),("ashish-after-2","Ashis Neupane in the gym at Apex Fitness Centre","After joining Apex"),("ashish-after-3","Ashis Neupane working out at Apex Fitness Centre","After joining Apex")])
    items += f'</div><div class="trf"><h3>Member story: Ashis Neupane</h3><p class="fine" style="text-align:left">Ashis is 20 and trains at Apex Fitness Centre. Photos and words shared with his permission. His results come from his own training and vary from person to person.</p><blockquote class="trq">&ldquo;I joined Apex Fitness Centre when I was very thin, and in just 5 months of dedicated hard work and consistency, I have seen tremendous changes in my physique. Thanks to Apex Fitness Centre and its trainers for guiding and motivating me throughout my transformation journey. Highly recommended!&rdquo;<p class="trqn">Ashis Neupane, 20</p></blockquote><div class="trg">{tr}</div>'
    return f'<section class="sec" id="reviews"><div class="wrap"><div class="shead"><span class="label">Real customers</span><h2>What our customers say</h2><p class="fine">Reviews and photos shared by customers who bought from Apex Fitness Centre. Experience varies from person to person.</p></div><div class="rvg">{items}</div></div></section>'

def together(p):
    q = next(x for x in PRODUCTS if x["slug"] == p["pair"])
    full = p["price"] + q["price"]
    off = save_for([p["slug"], q["slug"]])
    tot = full - off
    assert 300 <= off <= 500 or off == 1000, ("bundle without a real discount", p["slug"], q["slug"])
    return f'''<section class="tog"><h2 class="h2s">Frequently bought together</h2><div class="togr">
<div class="ti"><img src="../../assets/{p['img']}" alt="{e(p['full'])}" width="640" height="640" loading="lazy"><span>{e(p['name'])}</span></div><b class="plus">+</b>
<div class="ti"><a href="../../{q['url']}"><img src="../../assets/{q['img']}" alt="{e(q['full'])}" width="640" height="640" loading="lazy"></a><span>{e(q['name'])}</span></div>
<div class="tbuy" data-product="{e(p['full'])} + {e(q['full'])}" data-value="{tot}"><span class="was">Both for <s>{money(full)}</s></span><b class="price">{money(tot)}</b><span class="save">You save {money(off)}</span><a class="btn wa" href="{wa(f"Hi Apex Fitness Centre, I want to order this bundle: {p['full']} ({money(p['price'])}) + {q['full']} ({money(q['price'])}). Bundle price {money(tot)} (was {money(full)}, I save {money(off)}). Please confirm stock and send payment details.")}" target="_blank" rel="noopener">Order both on WhatsApp</a><button class="btn line" type="button" data-bundle="{p['slug']},{q['slug']}">Add both to cart</button></div>
</div></section>'''

def stock_line(p):
    # Switch a product with STOCK = {"slug": "out"} at the top of this file.
    if STOCK.get(p["slug"]) == "out":
        m = wa(f"Hi Apex Fitness Centre, is {p['full']} back in stock?")
        return f'<p class="stock out"><span><b>Out of stock</b> &ndash; <a class="tl" href="{m}" target="_blank" rel="noopener">message us</a></span></p>'
    return '<p class="stock"><span><b>In stock</b> &ndash; ships same day, delivery in 1&ndash;2 days (confirm on WhatsApp)</span></p>'

def build_product(p):
    d = 2
    c = next(x for x in CATS if x["slug"] == p["cat"])
    cr = [("Home", ""), ("Shop", "shop/"), (c["name"], c["url"]), (p["name"], p["url"])]
    pfaq = [(f"Do you deliver {p['name']} all over Nepal?", "Yes. Delivery is free all over Nepal. Order on WhatsApp and we confirm your address and delivery details."),
            (f"What is the price of {p['name']}{' ' + p['size'] if p['size'] else ''} in Nepal?", f"At Apex Fitness Centre the price is {money(p['price'])}."),
            ("How do I order?", "Tap Order on WhatsApp or add it to your cart. Your order arrives in our WhatsApp chat and we confirm stock and delivery with you.")]
    prod = {"@type": "Product", "@id": BASE + "/" + p["url"] + "#product", "name": p["full"], "image": [BASE + "/assets/" + p["img"]],
            "description": p["desc"], "sku": p["slug"], "brand": {"@type": "Brand", "name": p["brand"]}, "category": c["name"],
            "offers": {"@type": "Offer", "url": BASE + "/" + p["url"], "priceCurrency": "NPR", "price": str(p["price"]),
                       "availability": "https://schema.org/" + ("OutOfStock" if STOCK.get(p["slug"]) == "out" else "InStock"), "priceValidUntil": f"{__import__('datetime').date.today().year + 1}-12-31", "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "NPR"}, "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "NP"}, "deliveryTime": {"@type": "ShippingDeliveryTime", "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"}, "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 1, "unitCode": "DAY"}}}, "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "NP", "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 7, "returnMethod": "https://schema.org/ReturnByMail", "returnFees": "https://schema.org/ReturnShippingFees", "description": "Sealed, unopened items only. Opened supplements cannot be returned."}, "itemCondition": "https://schema.org/NewCondition",
                       "seller": {"@type": "Organization", "name": SITE}}}
    rvs = [x for x in REVIEWS if x["product"] == p["slug"]]
    if rvs:
        prod["review"] = [{"@type": "Review", "author": {"@type": "Person", "name": x["name"]}, "reviewRating": {"@type": "Rating", "ratingValue": str(x["rating"]), "bestRating": "5", "worstRating": "1"}, "reviewBody": x.get("en") or x["text"]} for x in rvs]
        prod["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": str(round(sum(x["rating"] for x in rvs) / len(rvs), 1)), "reviewCount": str(len(rvs)), "bestRating": "5", "worstRating": "1"}
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), prod, faq_ld(pfaq)]})
    msg = f"Hi Apex Fitness Centre, I want to order: {p['full']} for {money(p['price'])}. Please confirm stock and delivery to my address."
    facts = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in p["facts"])
    rel = ([x for x in PRODUCTS if x is not p and x['cat'] == p['cat']] + [x for x in PRODUCTS if x['cat'] != p['cat']])[:4]
    body = f"""<body data-root="../../">
{nav(d, c['slug'])}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="pdp">
<div class="pgal"><img src="../../assets/{p['img']}" alt="{e(p['full'])}" width="640" height="640" fetchpriority="high"></div>
<div class="pinfo">
<span class="pbrand">{e(p['brand'])}</span>
<h1>{e(p['full'])}</h1>
<div class="pprice"><span class="price big">{money(p['price'])}</span><span class="tag">Free delivery all over Nepal</span></div>
{stock_line(p)}
<p class="lead">{e(p['short'])}</p>
<a class="btn wa full order-main" href="{wa(msg)}" target="_blank" rel="noopener" data-product="{e(p['full'])}" data-value="{p['price']}">Order on WhatsApp &ndash; {money(p['price'])}</a>
<div class="buy">
<div class="qty" role="group" aria-label="Quantity"><button type="button" id="qm" aria-label="Decrease">-</button><input id="qv" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" id="qp" aria-label="Increase">+</button></div>
<button class="btn line" type="button" id="addBtn" data-add="{p['slug']}">Add to cart</button>
</div>
<ul class="ticks"><li>Pay by Khalti or bank transfer</li><li>Free delivery all over Nepal, usually in 1-2 days</li><li>Returns: sealed, unopened items only. Opened supplements cannot be returned.</li><li>Sold by Apex Fitness Centre, Urlabari</li></ul>
</div>
</div>
<div class="pdetail">
<section><h2>About this product</h2>{''.join(f'<p>{e(t)}</p>' for t in p['about'])}</section>
<section><h2>Product details</h2><table class="facts">{facts}</table></section>
<section><h2>How to use</h2><p>{e(p['use'])}</p></section>
<section class="auth"><h2>How to check it is genuine</h2><p>We buy from authorised sellers, not unknown resellers. When your order arrives, check these:</p><ul><li><b>Seal:</b> the inner seal under the lid is intact.</li><li><b>Batch number and dates:</b> printed clearly, and the expiry date is in the future.</li><li><b>Scratch code or QR code:</b> if the brand uses one, check it on the brand's official website or app.</li><li><b>Importer label:</b> the importer's name and address are on the pack.</li></ul><p>Want to see it first? Message us on WhatsApp and we will send a photo of the seal and batch number before you pay. Read our full guide: <a href="{"../" * d}guides/how-to-spot-fake-supplements-in-nepal/">how to spot fake supplements in Nepal</a>.</p></section>
</div>
<section class="who"><h2 class="h2s">Who it is for</h2><ul class="who-l">{''.join(f'<li>{e(t)}</li>' for t in p['who'])}</ul></section>
{together(p)}
{reviews_block(p)}
<section class="how2"><h2 class="h2s">How your order works</h2><ol class="how"><li><b>Order on WhatsApp.</b> Tap the green button. We confirm stock and your address.</li><li><b>Pay your way.</b> Khalti or bank transfer. Details come on WhatsApp.</li><li><b>We ship the same day.</b> Nepal Can sends it with a tracking number, free of charge.</li><li><b>Delivered in 1 to 2 days.</b> Check the seals, then message us if anything looks wrong.</li></ol></section>
<section class="why"><h2 class="h2s">Why order from Apex</h2><div class="whyg">
<div><b>Authentic products</b><p>Bought from authorised sellers, not unknown resellers.</p></div>
<div><b>Free delivery all over Nepal</b><p>No delivery charge, wherever you live.</p></div>
<div><b>Khalti or bank transfer</b><p>Pay the way you prefer. Details come on WhatsApp.</p></div>
<div><b>Real people on WhatsApp</b><p>Ask anything before you buy. We reply from the gym.</p></div>
</div></section>
{guide_links(d, p['cat'])}
<section class="narrow"><h2 class="h2s">Questions</h2>{faq_html(pfaq)}</section>
<section><h2 class="h2s">You may also like</h2><div class="pgrid">{''.join(card(x, d) for x in rel)}</div></section>
</div></main>
{footer(d, p)}{drawer()}{tail(d)}"""
    pages[p["url"]] = head(p["title"], p["desc"], p["url"], d, image="assets/" + p["img"], extra=j, ptype="product") + body
    sitemap.append((p["url"], "0.9"))

# GYM page from the existing site
def build_gym():
    s = open(GYM_SRC).read()
    uris = []
    for m in re.finditer(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+', s):
        if m.group(0) not in uris: uris.append(m.group(0))
    names = ["gym-hero.jpg","gym-free-weights.jpg","gym-machines.jpg","gym-plate-loaded.jpg","gym-cardio.jpg","team-sanju-phombo-limbu.jpg","team-manita-yongya.jpg","team-dipika-phyak.jpg"]
    for u, n in zip(uris[:8], names):
        s = s.replace(u, "../assets/" + n)
    # remove product data (last 4 uris) and the shop render script
    s = re.sub(r'\n\s*/\* shop: add products here.*?\}\)\(\);\n', "\n", s, flags=re.S)
    s = re.sub(r'<section id="shop">.*?</section>', '''<section id="shop"><div class="wrap"><div class="head"><span class="label">Supplements</span><h2>Shop supplements online</h2><p>Creatine, whey protein and pre-workout, delivered all over Nepal. Order on WhatsApp.</p></div><div class="actions"><a class="btn" href="../shop/">Open the store</a></div></div></section>''', s, flags=re.S)
    s = s.replace('<li><a href="#shop">Shop</a></li>', '<li><a href="../shop/">Shop</a></li>').replace('<a href="#shop">Shop</a>', '<a href="../shop/">Shop</a>')
    s = s.replace("$$('nav ul a')", "$$('nav ul a[href^=\"#\"]')")
    s = s.replace("Delivery all over Nepal","Free delivery all over Nepal")
    # Apex red theme (the page's --red variables held gold values)
    s = s.replace('--red:#e2b023', '--red:#e11f37').replace('--red2:#f1c658', '--red2:#ff4d5e').replace('--red-d:#b88408', '--red-d:#b5122a')
    s = s.replace('#f6d36a', '#ff6b7a').replace('#c99512', '#c8102e').replace('#15130c', '#ffffff').replace('#221a08', '#2a0a0f')
    s = s.replace('rgba(226,176,35', 'rgba(225,31,55').replace('226,176,35', '225,31,55')
    s = s.replace('<a class="logo" href="#top">Apex Fitness Centre</a>', '<a class="logo" href="/"><span class="wm">APEX</span><span class="wm2">Fitness<br>Centre</span></a>')
    s = s.replace('<a class="logo" href="#top">', '<a class="logo" href="/">')
    # --- Oct 2026 fixes ---
    def must(a, b):
        nonlocal s
        assert a in s, ("gym source changed, fix not applied:", a[:70]); s = s.replace(a, b)
    # H1: the two lines are separate spans, so text readers saw "Earn yourpeak". Add a real space.
    must('<span class="l"><span>Earn your</span></span><span class="l">', '<span class="l"><span>Earn your</span></span> <span class="l">')
    # 12-month first-time price Rs. 12,500 confirmed by the owner (23 Oct 2026): the 12-month plan has a lower joining cost.
    must("For example, 1 month is Rs. 2,500: Rs. 1,500 membership and Rs. 1,000 one-time.</p>",
         "For example, 1 month is Rs. 2,500: Rs. 1,500 membership and Rs. 1,000 one-time. The 12-month plan has a lower joining cost: Rs. 12,500 in total for new members.</p>")
    # Trainer cards: same layout for both (name, shift and time, experience)
    must('<div class="cap"><span class="sub">Trainer</span><div class="role">Morning shift</div><div class="time">4:30 AM – 12:30 PM</div><p>2+ years of deep study in the fitness field.</p></div>',
         '<div class="cap"><span class="sub">Trainer</span>'
         '<div class="role">Suman Limbu</div>'
         '<div class="meta">Morning shift · 4:30 AM – 12:30 PM</div><div class="meta">2+ years of study in the fitness field</div></div>')
    must('<div class="role">Sanju Phombo Limbu</div><div class="meta">Day shift · 30 years of experience</div>',
         '<div class="role">Sanju Phombo Limbu</div>'
         '<div class="meta">Evening shift · 4:30 PM – 8:30 PM</div>'
         '<div class="meta">30 years of experience</div>')
    for anchor in ('id="plans"', 'id="connect"', 'id="team"'):
        assert anchor in s, anchor
    title = "Gym in Urlabari, Morang | Apex Fitness Centre"
    desc = "Gym in Urlabari-9, Durgapuri, Morang. Open Sunday to Friday, 4:30 AM to 8:30 PM. Memberships from Rs. 1,500 a month, trainers on morning and evening shifts."
    cr = [("Home", ""), ("The gym", "gym/")]
    gj = dict(STORE); gj["@context"] = "https://schema.org"; gj["@type"] = ["HealthClub", "SportsActivityLocation"]
    gj["@id"] = BASE + "/gym/#gym"; gj["url"] = BASE + "/gym/"
    gj.pop("areaServed", None)
    jl = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {k: v for k, v in gj.items() if k != "@context"}]})
    new_head = head(title, desc, "gym/", 1, extra=jl).replace('<link rel="stylesheet" href="../assets/store.css">\n', '').replace('<link rel="stylesheet" href="../assets/premium.css">\n', '')
    # strip the original head tags (title, fonts) and keep style
    s = re.sub(r'^<title>.*?</title>\n', '', s)
    s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
    s = re.sub(r'<link href="https://fonts[^>]*>\n', '', s)
    s = re.sub(r'<meta name="description"[^>]*>\n?', '', s)
    s = s.replace('<script>', '<script>', 1)
    s = s.replace('</head>', '<link rel="stylesheet" href="../assets/gym-premium.css">\n</head>', 1) if '</head>' in s else s
    out = new_head.replace("</head>\n", "") + s
    if 'gym-premium.css' not in out: out = out.replace('<body', '<link rel="stylesheet" href="../assets/gym-premium.css">\n<body', 1)
    if "</html>" not in out: out += "\n"
    if "<body" not in out:
        out = out.replace("<nav id=\"nav\">", "</head>\n<body>\n<nav id=\"nav\">", 1)
    if "</body>" not in out:
        out = out.rstrip() + "\n</body>\n</html>\n"
    out = out.replace('</head>', '<link rel="stylesheet" href="../assets/gym-premium.css">\n</head>', 1)
    pages["gym/"] = out
    sitemap.append(("gym/", "0.7"))


# SOFTWARE page: selling Apex Gym Management to other gym owners
SW_FAQ = [
 ("How much does gym management software cost in Nepal?","Apex Gym Management costs Rs. 25,000 as a one-time payment. There is no monthly fee and no per-member fee. Many online gym systems charge every month, so a one-time price usually works out cheaper within a year or two."),
 ("What is included in the Rs. 25,000?","The full program with members, renewals, freeze, dues, WhatsApp reminders, sales, attendance, staff, expenses, reports, bills and automatic daily backup. We also install it, add your plans and prices, and train your staff."),
 ("Is there a monthly fee?","No. You pay Rs. 25,000 once. You do not pay again each month or each year to keep using the program you bought."),
 ("What is Apex Gym Management?","It is the same software we use every day to run Apex Fitness Centre in Urlabari, Morang. It handles members, renewals, attendance, payments, dues, product sales, expenses, bills, staff and reports in one program."),
 ("Do I need internet to use it?","No. It runs on your gym computer and keeps your data on that computer. You only need internet to open WhatsApp links when you send reminders."),
 ("Which computers does it work on?","Windows and Mac. Most gyms use one Windows computer at the front desk."),
 ("Can it send WhatsApp reminders to members?","It prepares the message with the member's name and the exact amount due and opens WhatsApp with the text ready. You press Send. WhatsApp does not allow any software to send messages fully automatically, so we do not pretend it can."),
 ("How does the gym membership freeze feature work?","Press Freeze on a member, write a short note, and the days stop counting from that day. When the member returns, press Unfreeze and the paused days are added back to their end date."),
 ("What happens to my data? Is there a backup?","The program saves a backup by itself every morning when the computer is on. You can also pick a second folder, for example a USB drive or a Google Drive folder, so a copy is always somewhere else."),
 ("Can I control what my staff can do?","Yes. Every staff member has their own login and you choose which buttons they can use. For example, only the owner can cancel a payment. Every correction and cancellation is kept in a history with the reason."),
 ("Is it better than Excel or a notebook for a gym?","Excel and notebooks cannot tell you who is expiring this week, who owes money, or who changed a receipt. This software does that automatically, backs itself up, and reminds members on WhatsApp."),
 ("Can you set it up for my gym?","Yes. We install it, add your plans and prices, and show you and your staff how to use it. You also get a simple step-by-step guide in PDF. Message us on WhatsApp at 9708819605 for a live demo."),
]

SW_FEATURES = [
 ("Members and renewals","Add a member in under a minute. Renew in two clicks. Every member shows a clear status: Active, Expiring soon with days left, Expired or Frozen."),
 ("Freeze and unfreeze","Sick or travelling? Freeze the membership with a note. The days stop, and are added back when they return. No more arguments about lost days."),
 ("Dues you can actually collect","Membership dues and product dues are shown separately and collected on one screen. Everything, membership only or products only. Receipts are made for you."),
 ("WhatsApp reminders","Due, expiring and expired reminders with the real name and amount filled in. English and Nepali templates. Send to one person or a whole list."),
 ("Sales and Quick Tab","Sell drinks and supplements, track stock, and keep a credit tab for regular members. Stock goes down on sale and back on cancel."),
 ("Payments and receipts","Search every payment by name, ID, phone or receipt number. Filter by date and mode: cash, bank or eSewa. Totals update as you filter. Print receipts as PDF."),
 ("Attendance","Check members in by name, ID or phone. Each member is counted once per day. See any past day."),
 ("Staff, clock-in and tasks","Staff check in and out, follow a daily checklist and read your messages. You see who has seen them."),
 ("Expenses and reports","Record rent, salary and bills. See income, expenses, profit and dues for any date range."),
 ("Daily auto backup","A backup is saved every morning by itself, with an optional second copy on a USB drive or Drive folder."),
 ("Staff permissions and history","Every user has a login. You choose what each person can do. Cancelled and corrected records are never lost; they stay with the reason."),
 ("Customer bills in PDF","Make a clean bill with your gym name, address and PAN and download it as PDF."),
]

def build_software():
    d = 1; path = "software/"
    title = "Gym Management Software in Nepal | Rs. 25,000 One-Time | Apex"
    desc = "Gym management software in Nepal: Rs. 25,000 one-time, no monthly fee. Members, dues, freeze, WhatsApp reminders, attendance, staff and backup. Free demo."
    cr = [("Home", ""), ("Gym software", path)]
    app = {"@type": "SoftwareApplication", "name": "Apex Gym Management", "applicationCategory": "BusinessApplication", "operatingSystem": "Windows, macOS",
           "description": desc, "url": BASE + "/" + path, "image": BASE + "/assets/software-dashboard.jpg", "publisher": {"@id": BASE + "/#org"}, "inLanguage": "en-NP", "featureList": [a for a, _ in SW_FEATURES],
           "offers": {"@type": "Offer", "price": "25000", "priceCurrency": "NPR", "availability": "https://schema.org/InStock", "priceValidUntil": "2027-12-31", "url": BASE + "/" + path + "#pricing", "seller": {"@id": BASE + "/#org"}, "eligibleRegion": {"@type": "Country", "name": "Nepal"}}}
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), app, faq_ld(SW_FAQ)]})
    demo = wa("Hi Apex Fitness Centre, I own a gym and I want a demo of Apex Gym Management (Rs. 25,000).")
    feats = "".join(f'<div class="swf"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in SW_FEATURES)
    def shot(img, alt, cap):
        return f'<figure class="swshot"><img src="../assets/{img}" alt="{e(alt)}" width="1200" height="{int(1200*820/1366)}" loading="lazy"><figcaption>{e(cap)}</figcaption></figure>'
    body = f"""<body data-root="../">
{nav(d, "software")}
<main>
<section class="hero swhero"><div class="wrap hgrid">
<div class="htext">
<span class="label">Gym management software in Nepal</span>
<h1>Run your gym.<br><em>Not your notebook.</em></h1>
<p class="lead"><b>Rs. 25,000 one-time. No monthly fee.</b> Apex Gym Management is the gym software we built to run our own gym in Urlabari. Members, renewals, dues, WhatsApp reminders, sales, staff and daily backup in one simple program. No more lost registers, forgotten dues or arguments about expiry dates.</p>
<div class="cta"><a class="btn wa" href="{demo}" target="_blank" rel="noopener">Get a free demo on WhatsApp</a><a class="btn line" href="#features">See what it does</a></div>
<ul class="ticks"><li>One-time Rs. 25,000</li><li>Used daily at Apex Fitness Centre</li><li>Works without internet</li><li>Windows and Mac</li></ul>
</div>
<div class="hfeat swhf"><img src="../assets/software-dashboard.jpg" alt="Apex Gym Management dashboard showing members, collection and dues" width="1200" height="{int(1200*820/1366)}" fetchpriority="high"><div class="hcap"><span class="pbrand">Dashboard</span><b>Your whole gym, on one screen</b></div></div>
</div></section>

<section class="trust"><div class="wrap"><ul>
<li><b>Built in a real gym</b><span>Made for how Nepal gyms work</span></li>
<li><b>Dues under control</b><span>See who owes what, and why</span></li>
<li><b>Auto backup</b><span>Saved every morning</span></li>
<li><b>Rs. 25,000 once</b><span>No monthly fee, setup included</span></li>
</ul></div></section>

<section class="sec"><div class="wrap">
<div class="shead"><span class="label">Sound familiar?</span><h2>The problems every gym owner has</h2></div>
<div class="swprob">
<div><h3>"Who still owes money?"</h3><p>Dues hidden in a notebook. Some members never pay, and you only remember when it is too late.</p><span>Fixed: one Dues list with a Remind button.</span></div>
<div><h3>"My membership should still be valid!"</h3><p>Arguments about expiry dates, sick members, and days nobody counted.</p><span>Fixed: exact dates, days left and Freeze.</span></div>
<div><h3>"The computer broke. All records gone."</h3><p>One crash and years of members and payments disappear.</p><span>Fixed: automatic daily backup, with a second copy.</span></div>
<div><h3>"Staff changed the amount."</h3><p>Receipts edited, money does not match, and you cannot tell who did it.</p><span>Fixed: logins, permissions and a full history.</span></div>
</div></div></section>

<section class="sec alt" id="features"><div class="wrap">
<div class="shead"><span class="label">Everything in one program</span><h2>What Apex Gym Management does</h2><p>Simple enough for a front desk on a busy morning. Complete enough for the owner at night.</p></div>
<div class="swgrid">{feats}</div>
</div></section>

<section class="sec" id="pricing"><div class="wrap">
<div class="shead center"><span class="label">Pricing</span><h2>One price. Pay once. Use it for years.</h2><p>Most gym software in Nepal and abroad charges every month. Apex Gym Management is a single payment.</p></div>
<div class="swprice">
<div class="swpc">
<span class="pbrand">Apex Gym Management</span>
<div class="swamt"><b>Rs. 25,000</b><span>one-time payment</span></div>
<ul>
<li>Unlimited members</li>
<li>Members, renewals, freeze and unfreeze</li>
<li>Dues, receipts and payment filters</li>
<li>WhatsApp reminders, English and Nepali</li>
<li>Sales, stock and Quick Tab</li>
<li>Attendance, staff clock-in and daily tasks</li>
<li>Expenses, reports and customer bills in PDF</li>
<li>Automatic daily backup</li>
<li>Staff logins and permissions</li>
<li>Installation, setup of your plans and staff training</li>
<li>Step-by-step PDF guide</li>
</ul>
<a class="btn wa full" href="{demo}" target="_blank" rel="noopener">Get a free demo and buy on WhatsApp</a>
<p class="fine">Pay by Khalti or bank transfer. Questions? Call 9708819605.</p>
</div>
<div class="swcmp">
<h3>Compare the cost</h3>
<table class="cmp"><thead><tr><th></th><th>Notebook or Excel</th><th>Monthly gym app</th><th>Apex Gym Management</th></tr></thead><tbody>
<tr><td>Price</td><td>Free</td><td>Pay every month</td><td><b>Rs. 25,000 once</b></td></tr>
<tr><td>Knows who is expiring</td><td>No</td><td>Yes</td><td>Yes</td></tr>
<tr><td>Dues list and reminders</td><td>No</td><td>Sometimes extra</td><td>Yes, included</td></tr>
<tr><td>Freeze membership</td><td>By hand</td><td>Sometimes</td><td>Yes</td></tr>
<tr><td>Works without internet</td><td>Yes</td><td>No</td><td>Yes</td></tr>
<tr><td>Daily backup</td><td>No</td><td>Yes</td><td>Yes, automatic</td></tr>
<tr><td>Staff permissions and history</td><td>No</td><td>Sometimes</td><td>Yes</td></tr>
</tbody></table>
<p class="fine">Comparison is general. Prices of other products change, so check the current price of any monthly app you are considering.</p>
</div>
</div></div></section>

<section class="sec alt"><div class="wrap narrow" id="nepali">
<div class="shead"><span class="label">नेपालका जिमका लागि</span><h2>जिम म्यानेजमेन्ट सफ्टवेयर, एकपटक रु. २५,०००</h2></div>
<p class="prose" style="max-width:none">सदस्य दर्ता, नवीकरण, म्याद सकिने मिति, बाँकी रकम (उधारो), WhatsApp रिमाइन्डर, बिक्री, स्टक, कर्मचारी र दैनिक ब्याकअप, सबै एउटै प्रोग्राममा। इन्टरनेट बिना चल्छ। हरेक महिना शुल्क तिर्नु पर्दैन। निःशुल्क डेमोका लागि WhatsApp गर्नुहोस्: 9708819605।</p>
</div></section>

<section class="sec"><div class="wrap">
<div class="shead"><span class="label">See it</span><h2>Clean screens your staff can learn in a day</h2><p>Screens below use sample names and numbers, not real members.</p></div>
<div class="swshots">
{shot("software-members.jpg","Members list with Active, Expiring soon, Expired and Frozen statuses","Members: status and days left at a glance")}
{shot("software-payments.jpg","Payments page with search, filters and totals","Payments: search, filters and totals")}
{shot("software-collect.jpg","Collect Due screen choosing membership, products or everything","One Collect screen for membership and product dues")}
{shot("software-whatsapp.jpg","WhatsApp Messages screen with a ready due reminder","WhatsApp reminders with real name and amount")}
</div></div></section>

<section class="sec alt"><div class="wrap">
<div class="shead"><span class="label">Getting started</span><h2>Ready in three steps</h2></div>
<ol class="steps">
<li><b>1</b><div><h3>Message us</h3><p>Tell us about your gym on WhatsApp. We show you a live demo. The price is Rs. 25,000, one time.</p></div></li>
<li><b>2</b><div><h3>We set it up</h3><p>We install it, add your plans and prices, and bring in your member list.</p></div></li>
<li><b>3</b><div><h3>Your staff learn it</h3><p>We train your front desk and give you a simple PDF guide. Questions? We reply on WhatsApp.</p></div></li>
</ol>
</div></section>

<section class="sec"><div class="wrap two">
<div><span class="label">Why Apex</span><h2>Software made by a gym, not a software company</h2>
<p>We run Apex Fitness Centre in Urlabari-9, Morang. Every feature here exists because we needed it at our own front desk: freezing a sick member, collecting a part payment, reminding someone about dues. You get a tool that has been tested on real mornings with real members.</p>
<a class="btn line" href="../gym/">See our gym</a></div>
<figure class="shot"><img src="../assets/gym-machines.jpg" alt="Machines area at Apex Fitness Centre, Urlabari" width="1000" height="750" loading="lazy"><figcaption>Where it is used every day: Apex Fitness Centre</figcaption></figure>
</div></section>

<section class="sec alt"><div class="wrap narrow">
<div class="shead"><span class="label">Questions</span><h2>Before you decide</h2></div>
{faq_html(SW_FAQ)}
</div></section>

<section class="sec"><div class="wrap"><div class="shead"><span class="label">Guides for gym owners</span><h2>Read before you buy</h2></div>
<div class="ggrid"><a class="gcard" href="../guides/gym-management-software-price-in-nepal/"><b>Gym management software price in Nepal</b><span>Monthly vs one-time, and what to check</span></a><a class="gcard" href="../guides/how-to-choose-gym-software-in-nepal/"><b>How to choose gym software</b><span>A simple checklist for owners</span></a><a class="gcard" href="../guides/gym-membership-management-excel-vs-software/"><b>Excel vs gym software</b><span>Where notebooks and sheets fail</span></a></div></div></section>

<section class="sec swcta"><div class="wrap">
<h2>Gym software for Rs. 25,000, one time</h2>
<p>Send us one WhatsApp message. We will show you a live demo on a real gym setup.</p>
<div class="cta"><a class="btn wa" href="{demo}" target="_blank" rel="noopener">Message us on WhatsApp</a><a class="btn line" href="tel:+9779708819605">Call 9708819605</a></div>
</div></section>
</main>
{footer(d)}{drawer()}{tail(d)}"""
    pages[path] = head(title, desc, path, d, image="assets/software-dashboard.jpg", extra=j) + body
    sitemap.append((path, "0.8"))


# FITNESS CALCULATORS page (self-contained: own CSS and JS, does not touch cart or shop scripts)
CALC_FAQ = [
 ("Are these calculators medical advice?","No. They give general estimates from standard formulas. They cannot diagnose anything or replace a doctor, midwife or registered dietitian."),
 ("Why does the page ask for my age before calculating?","Adult BMI categories and the Mifflin-St Jeor equation are designed for adults. For under 18s we show a BMI number with no category and we do not give calorie or macro targets, because growing bodies need individual advice."),
 ("Why is sex asked for BMR and TDEE?","The Mifflin-St Jeor equation has one version for men and one for women, based on the groups studied. It cannot account for body composition, hormones or medical treatment. If you prefer not to say, you will see both results as a range, or you can type a BMR you already know."),
 ("How accurate is the calorie estimate?","It is a starting point. Real energy use differs between people of the same age, size and sex, and changes from day to day. Use the number for a few weeks, watch what happens to your weight and energy, and adjust with professional advice if needed."),
 ("Do the macro percentages have to add up to 100?","Yes. The calculator checks this and tells you how far off you are. Protein and carbohydrate count 4 kcal per gram and fat counts 9 kcal per gram."),
 ("Is my information saved or sent anywhere?","No. Everything is worked out inside your browser on your device. Nothing you type here is sent to us or stored."),
]

def _calc_num(fid, label, name, unit_metric=None, unit_imp=None, ph="", mode="decimal", hint=None, opt=False, err=None):
    err = err or name
    ulab = ""
    if unit_metric:
        ulab = f'<span class="u" data-metric>{unit_metric}</span><span class="u" data-imperial>{unit_imp}</span>' if unit_imp else f'<span class="u">{unit_metric}</span>'
    h = f'<div class="hint" id="{fid}-h">{hint}</div>' if hint else ""
    desc = f'{fid}-e' + (f' {fid}-h' if hint else "")
    optl = ' <span class="opt">(optional)</span>' if opt else ""
    return (f'<div class="f"><label class="l" for="{fid}">{label}{optl}</label>'
            f'<div class="inwrap"><input type="text" inputmode="{mode}" autocomplete="off" id="{fid}" data-field="{name}" placeholder="{ph}" aria-describedby="{desc}">{ulab}</div>'
            f'{h}<p class="err" id="{fid}-e" data-err="{err}" role="alert" hidden></p></div>')

def _calc_weight(p):
    return (f'<div class="f"><label class="l" for="{p}-weight"><span data-metric>Weight (kg)</span><span data-imperial>Weight (lb)</span></label>'
            f'<div class="inwrap"><input type="text" inputmode="decimal" autocomplete="off" id="{p}-weight" data-field="weight" placeholder="e.g. 70" aria-describedby="{p}-weight-e">'
            f'<span class="u" data-metric>kg</span><span class="u" data-imperial>lb</span></div>'
            f'<p class="err" id="{p}-weight-e" data-err="weight" role="alert" hidden></p></div>')

def _calc_height(p):
    return (f'<div class="f" data-metric><label class="l" for="{p}-height">Height (cm)</label>'
            f'<div class="inwrap"><input type="text" inputmode="decimal" autocomplete="off" id="{p}-height" data-field="height" placeholder="e.g. 170" aria-describedby="{p}-height-e"><span class="u">cm</span></div></div>'
            f'<div class="f" data-imperial><fieldset><legend class="l">Height (feet and inches)</legend><div class="row2">'
            f'<div class="inwrap"><input type="text" inputmode="numeric" autocomplete="off" id="{p}-feet" data-field="feet" placeholder="5" aria-label="Feet" aria-describedby="{p}-height-e"><span class="u">ft</span></div>'
            f'<div class="inwrap"><input type="text" inputmode="decimal" autocomplete="off" id="{p}-inches" data-field="inches" placeholder="7" aria-label="Inches" aria-describedby="{p}-height-e"><span class="u">in</span></div>'
            f'</div></fieldset></div>'
            f'<p class="err" id="{p}-height-e" data-err="height" role="alert" hidden></p>')

def _calc_sex(p):
    opts = [("male","Male"),("female","Female"),("unspecified","Prefer not to say")]
    ch = "".join(f'<label class="choice"><input type="radio" name="{p}-sex" value="{v}" data-field="sex"><span>{l}</span></label>' for v, l in opts)
    return (f'<fieldset aria-describedby="{p}-sex-e {p}-sex-h"><legend class="l">Sex used in the equation</legend><div class="choices">{ch}</div>'
            f'<div class="hint" id="{p}-sex-h">The Mifflin-St Jeor equation has a male and a female version. If you prefer not to say, you will see both as a range.</div>'
            f'<p class="err" id="{p}-sex-e" data-err="sex" role="alert" hidden></p></fieldset>')

def _calc_age(p, label="Age (years)", ph="e.g. 28"):
    return _calc_num(f"{p}-age", label, "age", "yrs", None, ph, "numeric")

def _calc_preg(p, what):
    return (f'<label class="check" for="{p}-preg"><input type="checkbox" id="{p}-preg" data-field="pregnant">'
            f'<span>I am pregnant or breastfeeding. <span class="opt">We will not show {what} because these formulas were not made for that time.</span></span></label>')

def _calc_actions(label="Calculate"):
    return f'<div class="actions"><button class="cbtn" type="submit">{label}</button><button class="cbtn ghost" type="reset">Clear</button></div>'

def _calc_res(p):
    return f'<div class="res" id="{p}-result" aria-live="polite" aria-atomic="true"><p class="cx-empty">Your result will appear here.</p></div>'

def build_calculators():
    d = 1; path = "calculators/"
    title = "Fitness Calculators: BMI, BMR, TDEE and Macros | Apex Fitness"
    desc = "Free BMI, BMR, TDEE (maintenance calories) and macro calculators from Apex Fitness Centre. Metric and imperial units. Estimates only, not medical advice."
    cr = [("Home", ""), ("Fitness Calculators", path)]
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr),
            {"@type": "WebPage", "name": "Fitness Calculators", "url": BASE + "/" + path, "description": desc, "isPartOf": {"@id": BASE + "/#org"}, "inLanguage": "en-NP"},
            faq_ld(CALC_FAQ)]})
    extra = '<link rel="stylesheet" href="../assets/calc.css">\n' + j

    bmi = f"""<section class="cx-card" id="bmi" aria-labelledby="bmi-h"><h2 id="bmi-h">BMI calculator</h2>
<p class="sub">Body Mass Index compares your weight with your height: weight in kg divided by height in metres squared. It is a quick screening number for adults, not a measure of health or body fat.</p>
<div class="cgrid2"><form novalidate aria-labelledby="bmi-h">
{_calc_age("bmi")}
{_calc_weight("bmi")}
{_calc_height("bmi")}
{_calc_preg("bmi", "a BMI category")}
{_calc_actions()}
</form>
<div>{_calc_res("bmi")}</div></div>
<details><summary>Assumptions and limits</summary><ul>
<li>Formula: BMI = weight (kg) / height (m)<sup>2</sup>.</li>
<li>Categories follow the World Health Organization adult bands: under 18.5, 18.5 to 24.9, 25 to 29.9, and 30 and over.</li>
<li>Adult categories are not used for children and teenagers. Under 18s are compared with growth charts for their age and sex.</li>
<li>BMI cannot tell muscle from fat, and does not show where fat is carried. Athletes and people with a lot of muscle can have a high BMI and be healthy.</li>
<li>Some health bodies use lower cut-offs for people of South Asian background.</li>
<li>BMI categories are not a reliable guide in pregnancy or while breastfeeding.</li>
</ul></details></section>"""

    bmr = f"""<section class="cx-card" id="bmr" aria-labelledby="bmr-h"><h2 id="bmr-h">BMR calculator</h2>
<p class="sub">Basal Metabolic Rate is the energy your body uses at complete rest. We use the Mifflin-St Jeor equation, for adults aged 18 and over.</p>
<div class="cgrid2"><form novalidate aria-labelledby="bmr-h">
{_calc_age("bmr")}
{_calc_sex("bmr")}
{_calc_weight("bmr")}
{_calc_height("bmr")}
{_calc_preg("bmr", "an estimate")}
{_calc_actions()}
</form>
<div>{_calc_res("bmr")}</div></div>
<details><summary>Assumptions and limits of the Mifflin-St Jeor equation</summary><ul>
<li>Male: <code>10 x weight(kg) + 6.25 x height(cm) - 5 x age + 5</code></li>
<li>Female: <code>10 x weight(kg) + 6.25 x height(cm) - 5 x age - 161</code></li>
<li>It was worked out from measurements of healthy adults at rest, mainly aged about 19 to 78. It is less reliable outside that range.</li>
<li>It uses only weight, height, age and sex. It cannot see your muscle, body fat, hormones, thyroid health, medicines or genetics, which all change real energy use.</li>
<li>The two versions come from studying men and women as groups. Sex here means the groups used in that research, not a statement about anyone. If neither version fits you, choose "Prefer not to say" to see a range, or use a BMR measured or estimated by a health professional.</li>
<li>It is an average for people like you. Your own value can be higher or lower by a few hundred calories.</li>
<li>Not for under 18s, and not for pregnancy or breastfeeding.</li>
</ul></details></section>"""

    acts = "".join(f'<option value="{k}">{v["label"]}</option>' for k, v in [
        ("sedentary", {"label": "Sedentary: little or no exercise, desk job (x 1.2)"}),
        ("light", {"label": "Lightly active: light exercise 1 to 3 days a week (x 1.375)"}),
        ("moderate", {"label": "Moderately active: exercise 3 to 5 days a week (x 1.55)"}),
        ("very", {"label": "Very active: hard exercise 6 to 7 days a week (x 1.725)"}),
        ("extra", {"label": "Extra active: very hard exercise and a physical job (x 1.9)"})])
    tdee = f"""<section class="cx-card" id="tdee" aria-labelledby="tdee-h"><h2 id="tdee-h">Daily maintenance calories (TDEE)</h2>
<p class="sub">Total Daily Energy Expenditure is your BMR multiplied by an activity factor. It estimates the calories that would keep your weight steady.</p>
<div class="cgrid2"><form novalidate aria-labelledby="tdee-h">
{_calc_age("tdee")}
<div class="f"><label class="l" for="tdee-activity">Activity level</label>
<select id="tdee-activity" data-field="activity" aria-describedby="tdee-activity-e"><option value="">Choose one</option>{acts}</select>
<p class="err" id="tdee-activity-e" data-err="activity" role="alert" hidden></p></div>
<div class="f"><label class="l" for="tdee-manual">Already know your BMR? <span class="opt">(optional)</span></label>
<div class="inwrap"><input type="text" inputmode="numeric" autocomplete="off" id="tdee-manual" data-field="manualBmr" placeholder="e.g. 1600" aria-describedby="tdee-manual-h tdee-manual-e"><span class="u">kcal</span></div>
<div class="hint" id="tdee-manual-h" data-manualhint>Optional. If you already know your BMR, type it here and skip sex, weight and height.</div>
<p class="err" id="tdee-manual-e" data-err="manualBmr" role="alert" hidden></p></div>
<div data-bodygroup class="cwrap" style="padding:0;gap:16px">
{_calc_sex("tdee")}
{_calc_weight("tdee")}
{_calc_height("tdee")}
</div>
{_calc_preg("tdee", "an estimate")}
{_calc_actions()}
</form>
<div>{_calc_res("tdee")}</div></div>
<details><summary>Assumptions and limits</summary><ul>
<li>TDEE = BMR x activity factor. Factors used: 1.2, 1.375, 1.55, 1.725 and 1.9.</li>
<li>BMR comes from the Mifflin-St Jeor equation above, or from the BMR you type in.</li>
<li>Activity factors are rounded averages. People who think they are "moderately active" often differ a lot, so pick the level that matches an ordinary week.</li>
<li>The result is approximate. Use it as a starting point and watch how your body responds over a few weeks.</li>
<li>This page shows maintenance only. It does not prescribe weight-loss or weight-gain targets.</li>
<li>Not for under 18s, and not for pregnancy or breastfeeding.</li>
</ul></details></section>"""

    macros = f"""<section class="cx-card" id="macros" aria-labelledby="macros-h"><h2 id="macros-h">Macronutrient calculator</h2>
<p class="sub">Turn a daily calorie target into grams of protein, carbohydrate and fat. You choose the target and the split. We do the maths and check the percentages add up to 100.</p>
<div class="cgrid2"><form novalidate aria-labelledby="macros-h">
{_calc_age("macros", "Age (years)")}
{_calc_num("macros-cal", "Daily calorie target", "calories", "kcal", None, "e.g. 2200", "numeric", hint="Use a number from your dietitian or doctor, or the maintenance estimate above.")}
<div class="presets"><span class="l">Quick split</span><div class="p3">
<button type="button" class="cbtn small ghost" data-preset="30-40-30">Balanced 30/40/30</button>
<button type="button" class="cbtn small ghost" data-preset="35-40-25">Higher protein 35/40/25</button>
<button type="button" class="cbtn small ghost" data-preset="25-50-25">Higher carb 25/50/25</button></div></div>
<div class="row2" style="grid-template-columns:repeat(3,minmax(0,1fr))">
{_calc_num("macros-p", "Protein %", "proteinPct", "%", None, "30", "decimal")}
{_calc_num("macros-c", "Carbs %", "carbPct", "%", None, "40", "decimal")}
{_calc_num("macros-f", "Fat %", "fatPct", "%", None, "30", "decimal")}
</div>
<p class="err" id="macros-total-e" data-err="total" role="alert" hidden></p>
<div class="cx-tot" data-total aria-live="polite">Total: 0% of 100%.</div>
{_calc_actions()}
</form>
<div>{_calc_res("macros")}</div></div>
<details><summary>Assumptions and limits</summary><ul>
<li>Protein 4 kcal per gram, carbohydrate 4 kcal per gram, fat 9 kcal per gram.</li>
<li>Grams = calories x percentage / kcal per gram. Percentages must add up to 100.</li>
<li>This splits a target you choose. It does not decide what your target should be.</li>
<li>Alcohol, fibre and food label rounding mean real meals will not match exactly.</li>
<li>Not for under 18s. People with diabetes, kidney, liver or heart conditions, or an eating disorder history, should get a plan from a professional.</li>
</ul></details></section>"""

    toolbar = """<div class="toolbar">
<div class="seg" role="radiogroup" aria-label="Units"><label><input type="radio" name="units" value="metric" checked><span>Metric (kg, cm)</span></label><label><input type="radio" name="units" value="imperial"><span>Imperial (lb, ft)</span></label></div>
<nav class="jump" aria-label="Calculators"><a href="#bmi">BMI</a><a href="#bmr">BMR</a><a href="#tdee">TDEE</a><a href="#macros">Macros</a></nav>
</div>"""
    notice = """<div class="notice" role="note"><b>Estimates only. This is not medical advice.</b> These tools use general formulas and cannot know your health history. Please talk to a doctor, midwife or registered dietitian before changing how you eat or train, especially if you:
<ul><li>are pregnant or breastfeeding</li><li>are under 18</li><li>have diabetes, kidney, liver, heart or thyroid conditions, or take medicines that affect weight or appetite</li><li>have, or have had, an eating disorder</li></ul></div>"""

    links = f"""<div class="links">
<a href="../shop/"><b>Shop supplements</b><span>All products, free delivery all over Nepal</span></a>
<a href="../guides/"><b>Supplement guides</b><span>Plain guides on prices and how to use them</span></a>
<a href="../gym/"><b>Join the gym</b><span>Memberships and trainers in Urlabari</span></a>
<a href="https://wa.me/{WA}?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20used%20your%20fitness%20calculators%20and%20have%20a%20question." target="_blank" rel="noopener"><b>Ask on WhatsApp</b><span>9708819605, we reply from the gym</span></a>
</div>"""

    body = f"""<body class="calcs" data-root="../" data-units="metric">
{nav(d, "calculators")}
<main>
<section class="chero"><div class="wrap">
{crumb_html(cr, d)}
<span class="eyebrow">Free tools from Apex Fitness Centre</span>
<h1>Fitness <em>Calculators</em></h1>
<p class="lead">Work out your BMI, resting calories, daily maintenance calories and macros. Simple forms, clear results, and every step shown so you can see how each number was made.</p>
{toolbar}
{notice}
</div></section>
<div class="wrap cwrap">
{bmi}
{bmr}
{tdee}
{macros}
</div>
<section class="csec"><div class="wrap">
<h2 class="h2c">Keep going with Apex</h2>
{links}
</div></section>
<section class="csec"><div class="wrap narrow faqc">
<h2 class="h2c">Questions about the calculators</h2>
{faq_html(CALC_FAQ)}
<p class="fine" style="margin-top:18px;color:var(--muted)">General information only. Results are estimates and do not replace advice from a qualified health professional.</p>
</div></section>
</main>
{footer(d)}{drawer()}{tail(d).replace("</body>", '<script src="../assets/calc-core.js"></script>\\n<script src="../assets/calc.js"></script>\\n</body>')}"""
    pages[path] = head(title, desc, path, d, extra=extra) + body
    sitemap.append((path, "0.7"))


build_home(); build_shop()

from guides import GUIDES
# Guides whose topic now lives in a fuller blog post (see MERGED near the end); hidden from guide lists.
MERGED_GUIDE_SLUGS = {"how-much-protein-do-you-need", "how-to-spot-fake-supplements-in-nepal"}
_GBY = {g["slug"]: g for g in GUIDES}
GUIDE_FOR_CAT = {"creatine": ["creatine-price-in-nepal", "how-to-take-creatine", "how-to-spot-fake-supplements-in-nepal"],
                 "protein": ["whey-protein-price-in-nepal", "how-much-protein-do-you-need", "how-to-spot-fake-supplements-in-nepal"],
                 "pre-workout": ["how-to-choose-a-pre-workout-in-nepal", "supplements-for-beginners-in-nepal", "buy-supplements-online-in-nepal"]}
_GDEF = ["how-to-spot-fake-supplements-in-nepal", "supplements-for-beginners-in-nepal", "buy-supplements-online-in-nepal"]

def guide_links(depth, cat=None):
    r = "../" * depth
    sl = GUIDE_FOR_CAT.get(cat, _GDEF)
    items = "".join(f'<a class="gcard" href="{r}guides/{x}/"><b>{e(_GBY[x]["h1"])}</b><span>Read the guide</span></a>' for x in sl)
    return f'<section class="gl"><h2 class="h2s">Helpful guides</h2><div class="ggrid">{items}</div></section>'

def _unit(p):
    m = re.search(r"([\d.]+)\s*(kg|g|packets)", p["size"])
    if not m: return "-"
    n, u = float(m.group(1)), m.group(2)
    if u == "kg": return "Rs. {:,.0f} per kg".format(p["price"] / n)
    if u == "g": return "Rs. {:.2f} per gram".format(p["price"] / n)
    return "Rs. {:,.0f} per packet".format(p["price"] / n)

def build_guides():
    today_ = __import__("datetime").date.today().isoformat()
    for g in GUIDES:
        d = 2; path = f"guides/{g['slug']}/"
        cr = [("Home", ""), ("Guides", "guides/"), (g["h1"], path)]
        secs = ""
        for h2, parts in g["body"]:
            inner = ""
            for t in parts:
                if isinstance(t, dict): inner += "<ul>" + "".join(f"<li>{e(x)}</li>" for x in t["list"]) + "</ul>"
                else: inner += f"<p>{e(t)}</p>"
            secs += f"<section class='prose'><h2>{e(h2)}</h2>{inner}</section>"
        if g.get('sw'): secs += "<section class='prose swg'><h2>See the software</h2><p>Apex Gym Management is Rs. 25,000, one-time, with no monthly fee. It runs without internet and includes setup and staff training.</p><p><a class='btn wa' href='../../software/'>See features and price</a></p></section>"
        tbl = ""
        if g.get("table"):
            ps = [p for p in PRODUCTS if p["cat"] == g["table"]]
            rows = "".join(f'<tr><td><a href="../../{p["url"]}">{e(p["full"])}</a></td><td>{e(p["size"])}</td><td>{money(p["price"])}</td><td>{_unit(p)}</td></tr>' for p in ps)
            tbl = f'<section class="prose"><h2>Our current prices</h2><div class="tw"><table class="cmp"><thead><tr><th>Product</th><th>Pack</th><th>Price</th><th>Unit price</th></tr></thead><tbody>{rows}</tbody></table></div><p class="fine">Prices checked {today_}. Free delivery all over Nepal. <a class="tl" href="../../{g["table"]}/">See all {e(g["table"].replace("-", " "))} products</a>.</p></section>'
        rel = "".join(f'<a class="gcard" href="../{x}/"><b>{e(_GBY[x]["h1"])}</b><span>Read the guide</span></a>' for x in g["rel"])
        art = {"@type": "Article", "headline": g["h1"], "description": g["desc"], "datePublished": "2026-10-14", "dateModified": today_,
               "author": {"@id": BASE + "/#org"}, "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + "/" + path, "image": BASE + "/assets/og-image.jpg"}
        j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), art, faq_ld(g["faq"])]})
        body = f"""<body data-root="../../">
{nav(d)}
<main><div class="wrap">
{crumb_html(cr, d)}
<article class="guide">
<div class="shead left"><h1>{e(g['h1'])}</h1><p>{e(g['intro'])}</p></div>
{tbl}{secs}
</article>
<section class="narrow"><h2 class="h2s">Questions</h2>{faq_html(g['faq'])}</section>
<section class="gl"><h2 class="h2s">More guides</h2><div class="ggrid">{rel}</div></section>
{"" if g.get("sw") else '<p class="fine">General information, not medical advice. Ask a doctor if you have a health condition. Results vary from person to person.</p>'}
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
        pages[path] = head(g["title"], g["desc"], path, d, extra=j, ptype="article") + body
        sitemap.append((path, "0.8"))
    d = 1; cr = [("Home", ""), ("Guides", "guides/")]
    cards = "".join(f'<a class="gcard" href="{x["slug"]}/"><b>{e(x["h1"])}</b><span>{e(x["desc"])}</span></a>' for x in GUIDES if x["slug"] not in MERGED_GUIDE_SLUGS)
    j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr), {"@type": "CollectionPage", "name": "Supplement guides for Nepal", "url": BASE + "/guides/"}]})
    body = f"""<body data-root="../">
{nav(d)}
<main><div class="wrap">
{crumb_html(cr, d)}
<div class="shead left"><h1>Supplement guides for Nepal</h1><p>Plain, honest guides on prices, how to take supplements, and how to avoid fake products. Written by Apex Fitness Centre, Urlabari.</p></div>
<div class="ggrid big">{cards}</div>
</div></main>
{footer(d)}{drawer()}{tail(d)}"""
    pages["guides/"] = head("Supplement Guides for Nepal | Apex Fitness Centre", "Honest guides on supplement prices in Nepal, how to take creatine and protein, and how to spot fake supplements.", "guides/", d, extra=j) + body
    sitemap.append(("guides/", "0.8"))

for c in CATS: build_cat(c)
for p in PRODUCTS: build_product(p)
build_gym()
build_software()
build_calculators()
build_guides()
exec(open(os.path.join(HERE, "blog_engine.py"), encoding="utf-8").read())
POSTS = build_blog()
exec(open(os.path.join(HERE, "tools.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "foods.py"), encoding="utf-8").read())
build_info_pages()

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT + "/assets")

# ---- SPEED: WebP copies (max 800 px wide) of every JPG, and clean <img> tags ----
from PIL import Image as _Im
WEBP = {}  # "name.jpg" (relative to assets) -> (webp name, w, h)
for _root, _dirs, _files in os.walk(SRC):
    for _f in _files:
        if not _f.lower().endswith((".jpg", ".jpeg", ".png")) or _f.startswith("apex-"): continue
        _rel = os.path.relpath(os.path.join(_root, _f), SRC)
        _im = _Im.open(os.path.join(_root, _f)).convert("RGB")
        if _im.width > 800: _im = _im.resize((800, round(_im.height * 800 / _im.width)), _Im.LANCZOS)
        _wn = os.path.splitext(_rel)[0] + ".webp"
        os.makedirs(os.path.dirname(os.path.join(OUT, "assets", _wn)), exist_ok=True)
        _im.save(os.path.join(OUT, "assets", _wn), "WEBP", quality=80, method=6)
        WEBP[_rel.replace(os.sep, "/")] = (_wn.replace(os.sep, "/"), _im.width, _im.height)

def _fix_imgs(html_):
    def one(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]*?)assets/([^"]+)"', tag)
        if src and src.group(2) in WEBP:
            wn, w, h = WEBP[src.group(2)]
            tag = tag.replace(src.group(0), f'src="{src.group(1)}assets/{wn}"')
            if " width=" not in tag: tag = tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)
        if 'fetchpriority="high"' in tag:
            tag = re.sub(r'\sloading="lazy"', "", tag)
            if "loading=" not in tag: tag = tag.replace("<img ", '<img loading="eager" ', 1)
        elif "loading=" not in tag:
            tag = tag.replace("<img ", '<img loading="lazy" ', 1)
        if "decoding=" not in tag: tag = tag.replace("<img ", '<img decoding="async" ', 1)
        return tag
    html_ = re.sub(r"<img\s[^>]*>", one, html_)
    # CSS backgrounds (gym hero)
    html_ = re.sub(r'url\((["\']?)([^)"\']*?)assets/([^)"\']+\.jpg)\1\)', lambda m: f'url({m.group(1)}{m.group(2)}assets/{WEBP[m.group(3)][0] if m.group(3) in WEBP else m.group(3)}{m.group(1)})', html_)
    return html_

# Guides replaced by fuller blog posts on the same topic: one page per topic, so they don't compete in Google.
MERGED = {"guides/how-much-protein-do-you-need/": "blog/how-much-protein-do-you-need/",
          "guides/how-to-spot-fake-supplements-in-nepal/": "blog/fake-supplements-in-nepal-how-to-spot-them/"}
for old, new in MERGED.items():
    for k in list(pages):
        pages[k] = pages[k].replace(old, new)
    pages[old] = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>'
                  f'<link rel="canonical" href="{BASE}/{new}">'
                  f'<meta http-equiv="refresh" content="0; url=/{new}"></head><body><p>This guide has moved: '
                  f'<a href="/{new}">{BASE}/{new}</a></p></body></html>')
sitemap[:] = [x for x in sitemap if x[0] not in MERGED]
for k in list(pages):
    pages[k] = _fix_imgs(pages[k])
# gym hero is a CSS background above the fold: preload it with high priority
pages["gym/"] = pages["gym/"].replace("</head>", '<link rel="preload" as="image" href="../assets/gym-hero.webp" fetchpriority="high">\n</head>', 1)

for k, v in pages.items():
    path = os.path.join(OUT, k, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(v)
for f in os.listdir(SRC):
    if f.startswith("team-") or f.startswith("gym-") or f.endswith(".jpg"):
        shutil.copy(os.path.join(SRC, f), OUT + "/assets/" + f)
shutil.copytree(os.path.join(SRC, "reviews"), OUT + "/assets/reviews", dirs_exist_ok=True)
shutil.copy(HERE + "/store.css", OUT + "/assets/store.css")
shutil.copy(HERE + "/store.js", OUT + "/assets/store.js")
shutil.copy(HERE + "/premium.css", OUT + "/assets/premium.css")
shutil.copy(HERE + "/gym-premium.css", OUT + "/assets/gym-premium.css")
shutil.copy(SRC + "/apex-icon-512.png", OUT + "/assets/apex-icon-512.png")
shutil.copy(SRC + "/apex-icon-180.png", OUT + "/assets/apex-icon-180.png")
for _f in ("calc-core.js", "calc.js", "calc.css", "tools.js"): shutil.copy(HERE + "/" + _f, OUT + "/assets/" + _f)
# Pinterest pins (1000x1500): only for published posts, so scheduled titles stay private
os.makedirs(OUT + "/blog/pins", exist_ok=True)
for _p in POSTS:
    _pin = os.path.join(HERE, "content", "blog", "pins", _p["slug"] + ".jpg")
    if os.path.exists(_pin): shutil.copy(_pin, OUT + "/blog/pins/" + _p["slug"] + ".jpg")
open(OUT + "/assets/store-data.js", "w").write("window.APEX_PRODUCTS=" + json.dumps([dict({k: p[k] for k in ("slug","name","full","price","url","brand")}, img=WEBP.get(p["img"], (p["img"],))[0]) for p in PRODUCTS], ensure_ascii=False) + ";window.APEX_RULES=" + json.dumps([{"name": x["name"], "slugs": x["slugs"], "off": x["off"]} for x in RULES]) + ";window.APEX_PAIRS=" + json.dumps({p["slug"]: p["pair"] for p in PRODUCTS}) + ";window.APEX_WA=" + json.dumps(WA) + ";")
open(OUT + "/assets/favicon.svg", "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#d3132b"/><path d="M14 48 32 14l18 34h-8l-10-20-10 20z" fill="#ffffff"/></svg>')
today = __import__("datetime").date.today().isoformat()
# lastmod = the date a page's content last changed. Compare each freshly built page with the
# copy already published at the repo root; if it is identical, keep the date from the live sitemap.
_ROOT = os.path.join(HERE, "..")
try: _old_lm = dict(re.findall(r"<loc>" + re.escape(BASE) + r"/([^<]*)</loc><lastmod>([^<]+)</lastmod>", open(os.path.join(_ROOT, "sitemap.xml")).read()))
except Exception: _old_lm = {}
def _lastmod(u):
    try:
        if os.path.abspath(OUT) != os.path.abspath(_ROOT) and u in _old_lm and open(os.path.join(_ROOT, u, "index.html"), encoding="utf-8").read() == pages[u]:
            return _old_lm[u]
    except Exception: pass
    return today
open(OUT + "/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>{_lastmod(u)}</lastmod><priority>{pr}</priority></url>\n" for u, pr in sitemap) + "</urlset>\n")
def _x(t): return html.escape(str(t), quote=False)
os.makedirs(OUT + "/feeds", exist_ok=True)
_items = ""
for p in PRODUCTS:
    _items += ("<item><g:id>%s</g:id><title>%s</title><description>%s</description><link>%s/%s</link><g:image_link>%s/assets/%s</g:image_link>"
               "<g:availability>in_stock</g:availability><g:price>%.2f NPR</g:price><g:brand>%s</g:brand><g:condition>new</g:condition>"
               "<g:identifier_exists>no</g:identifier_exists><g:shipping><g:country>NP</g:country><g:service>Nepal Can</g:service><g:price>0.00 NPR</g:price></g:shipping></item>\n") % (
        "APEX-%06X" % (zlib.crc32(p["slug"].encode()) & 0xFFFFFF), _x(p["full"]), _x(p["desc"]), BASE, p["url"], BASE, p["img"], p["price"], _x(p["brand"]))
open(OUT + "/feeds/google-products.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel><title>Apex Fitness Centre</title><link>' + BASE + '/</link><description>Authentic supplements in Nepal</description>\n' + _items + '</channel></rss>\n')
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
open(OUT + "/404.html", "w").write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Apex Fitness Centre</title><meta name="robots" content="noindex">' + ga_tag() + '<style>body{background:#0e0f11;color:#f4f2ed;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0;text-align:center;padding:24px}a{color:#ff4d5e}</style></head><body><div><h1>Page not found</h1><p><a href="' + BASE + '/">Go to the store</a> or <a href="' + BASE + '/shop/">see all products</a>.</p></div></body></html>')
open(OUT + "/.nojekyll", "w").write("")
open(OUT + "/blog/feed.xml", "w", encoding="utf-8").write(BLOG_RSS[0])
copy_blog_images()
if ADSENSE_CLIENT:
    open(OUT + "/ads.txt", "w").write(f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
print("blog posts:", len(POSTS))
print("pages:", len(pages), "base:", BASE)
