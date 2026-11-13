# Buyer guides. Plain, honest and useful. "table" shows live product prices from PRODUCTS.
# Whey comparison data: ONLY figures printed on our product pages or on the tub labels.
# None = not on the site yet. TODO(owner): fill these from the labels; the build prints a reminder until you do.
from urllib.parse import quote as _q
WHEY = [
 dict(slug="muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme", name="MuscleBlaze Biozyme Performance Whey", full="MuscleBlaze Biozyme Performance Whey 2 kg (French Vanilla Crème)", price=15000, kg=2,
      servings=None,    # TODO(owner): servings per 2 kg tub (from the label)
      protein_g=None),  # TODO(owner): grams of protein per serving (from the label)
 dict(slug="bigman-forza-protein-2kg", name="BigMan Forza Protein", full="BigMan Forza Protein 2 kg", price=17500, kg=2,
      servings=66,      # product page: "66 per tub"
      protein_g=None),  # TODO(owner): grams of protein per serving (from the label)
 dict(slug="bpi-sports-hydro-hd-hydrolyzed-whey-2kg-chocolate-lava-cake", name="BPI Sports Hydro HD Hydrolyzed Whey", full="BPI Sports Hydro HD Hydrolyzed Whey 2 kg (Chocolate Lava Cake)", price=23000, kg=2,
      servings=None,    # TODO(owner): servings per 2 kg tub (from the label)
      protein_g=None),  # TODO(owner): grams of protein per serving (from the label)
]
WHEY_TODO = [f"{w['name']}: {k}" for w in WHEY for k in ("servings", "protein_g") if w[k] is None]
_rs = lambda n: f"Rs. {n:,.0f}"
def _whey_btn(w):
    msg = f"Hi Apex Fitness Centre, I want to order: {w['full']} for {_rs(w['price'])}. Please confirm stock. Payment: COD / Khalti / Bank"
    return (f'<p><a class="btn wa" href="https://wa.me/9779708819605?text={_q(msg)}" target="_blank" rel="noopener" data-product="{w["full"]}" data-value="{w["price"]}">'
            f'Order on WhatsApp – {_rs(w["price"])}</a> <a class="tl" href="../../products/{w["slug"]}/">See the product page</a></p>')
WHEY_BTN = {w["slug"]: _whey_btn(w) for w in WHEY}
_ask = '<span class="fine">See label</span>'
def _cell(v): return v if v else _ask
def _per100(w):
    if not (w["servings"] and w["protein_g"]): return None
    return "%.1f g" % (w["protein_g"] / (w["price"] / w["servings"]) * 100)
WHEY_TABLE = ('<div class="tw"><table class="cmp"><thead><tr><th>Product (2 kg)</th><th>Price</th><th>Price per kg</th><th>Servings</th><th>Price per serving</th><th>Protein per serving</th><th>Protein per Rs. 100</th></tr></thead><tbody>'
    + "".join(f'<tr><td><a href="../../products/{w["slug"]}/">{w["name"]}</a></td><td>{_rs(w["price"])}</td><td>{_rs(w["price"] / w["kg"])}</td>'
              f'<td>{_cell(w["servings"])}</td><td>{_cell(w["servings"] and _rs(w["price"] / w["servings"]))}</td>'
              f'<td>{_cell(w["protein_g"] and str(w["protein_g"]) + " g")}</td>'
              f'<td>{_cell(_per100(w))}</td></tr>' for w in WHEY)
    + '</tbody></table></div><p class="fine">Prices from our product pages. Servings and protein come from the product labels; where a figure is not on our site yet it says “See label” rather than a guess. Ask us on WhatsApp and we will send you a photo of the label.</p>')

GUIDES = [
dict(slug="creatine-price-in-nepal", cat="creatine",
 title="Creatine Price in Nepal 2026: MuscleBlaze, Wellcore, BPI",
 h1="Creatine Price in Nepal 2026: MuscleBlaze vs Wellcore vs BPI – Which to Buy?",
 desc="Creatine price in Nepal 2026: MuscleBlaze and Wellcore Rs. 2,000, BPI Rs. 5,000. Compare servings, how to take it and how to spot fakes.",
 intro="The creatine price in Nepal in 2026 starts at Rs. 2,000 for a MuscleBlaze or Wellcore tub and goes up to Rs. 5,000 for BPI Sports Micronised Creatine. All three are creatine monohydrate, the most studied form of creatine. The real differences are price per serving, flavour and how well the powder mixes. This guide compares them side by side and helps you pick the right one.",
 body=[
  ("Creatine price in Nepal: quick comparison", [{"html": """<div class="tw"><table class="cmp"><thead><tr><th>Product</th><th>Price</th><th>Pack</th><th>Flavour</th><th>Servings (3 g creatine)</th><th>Price per serving</th></tr></thead><tbody>
<tr><td><a href="../../products/muscleblaze-creatine-monohydrate-320g-citrus-blast/">MuscleBlaze Creatine Monohydrate</a></td><td>Rs. 2,000</td><td>320 g</td><td>Citrus Blast</td><td>See the label (flavoured tub)</td><td>See the label</td></tr>
<tr><td><a href="../../products/wellcore-micronised-creatine-monohydrate-307g-fruit-fusion/">Wellcore Micronised Creatine Monohydrate</a></td><td>Rs. 2,000</td><td>307 g</td><td>Fruit Fusion</td><td>83 (label)</td><td>about Rs. 24</td></tr>
<tr><td><a href="../../products/bpi-sports-micronized-creatine-300g-unflavored/">BPI Sports Micronised Creatine</a></td><td>Rs. 5,000</td><td>300 g</td><td>Unflavoured</td><td>100 (label: 60 servings of 5 g)</td><td>Rs. 50</td></tr>
</tbody></table></div>"""}, "Flavoured tubs contain flavouring as well as creatine, so you cannot divide the tub weight by 3 to get servings. Always check \"servings per container\" on the label."]),
  ("Why creatine prices differ in Nepal", ["Three things change the price: the brand, the pack size and the seller. Imported brands like BPI Sports cost more after shipping and import duty, while Indian brands like MuscleBlaze and Wellcore cost less to bring into Nepal.", "Flavour does not make creatine stronger. Flavoured tubs taste better in plain water, while unflavoured tubs mix into a shake without changing the taste. Micronised powder is ground finer, so it dissolves more easily, but the creatine itself is the same.", "Be careful with prices that look too good. A well-known brand selling far below the usual creatine price in Nepal can mean an old, repacked or fake tub."]),
  ("What creatine does", ["Your muscles use a fuel called phosphocreatine for short, hard efforts like a heavy set of squats or a sprint. Taking creatine every day tops up those stores. Research summarised by the International Society of Sports Nutrition shows creatine monohydrate can help you do a little more work in training, which over weeks supports strength and muscle gains. It is not a steroid and it is not a magic powder: it works only alongside regular training and enough protein."]),
  ("The three creatines, one by one", [{"html": """<h3>MuscleBlaze Creatine Monohydrate 320 g – Rs. 2,000</h3>
<p><img src="../../assets/muscleblaze-creatine-320g.jpg" alt="MuscleBlaze Creatine Monohydrate 320 g Citrus Blast" width="640" height="640" loading="lazy" style="max-width:220px;height:auto"></p>
<p>One of India's best-known sports nutrition brands, and the easiest creatine to find in Nepal. The Citrus Blast flavour means you can mix it with plain water. A good, low-cost choice for most people starting out.</p>
<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%3A%20MuscleBlaze%20Creatine%20Monohydrate%20320%20g%20%28Citrus%20Blast%29%20for%20Rs.%202%2C000.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="MuscleBlaze Creatine Monohydrate 320 g (Citrus Blast)" data-value="2000">Order on WhatsApp – Rs. 2,000</a> <a class="tl" href="../../products/muscleblaze-creatine-monohydrate-320g-citrus-blast/">See the product page</a></p>
<h3>Wellcore Micronised Creatine Monohydrate 307 g – Rs. 2,000</h3>
<p><img src="../../assets/wellcore-micronised-creatine-307g.jpg" alt="Wellcore Micronised Creatine Monohydrate 307 g Fruit Fusion" width="640" height="640" loading="lazy" style="max-width:220px;height:auto"></p>
<p>Micronised means the powder is ground finer, so it mixes more easily. The label gives 83 servings of 3 g creatine, about Rs. 24 per serving, in a Fruit Fusion flavour. Read our full <a href="../../blog/wellcore-creatine-review/">Wellcore creatine review</a>.</p>
<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%3A%20Wellcore%20Micronised%20Creatine%20Monohydrate%20307%20g%20%28Fruit%20Fusion%29%20for%20Rs.%202%2C000.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="Wellcore Micronised Creatine Monohydrate 307 g (Fruit Fusion)" data-value="2000">Order on WhatsApp – Rs. 2,000</a> <a class="tl" href="../../products/wellcore-micronised-creatine-monohydrate-307g-fruit-fusion/">See the product page</a></p>
<h3>BPI Sports Micronised Creatine 300 g – Rs. 5,000</h3>
<p><img src="../../assets/bpi-micronized-creatine-300g.jpg" alt="BPI Sports Micronised Creatine 300 g Unflavoured" width="640" height="640" loading="lazy" style="max-width:220px;height:auto"></p>
<p>An American brand, unflavoured and micronised. Because it has no flavour, you can add it to your whey shake, juice or water without changing the taste. It costs more per serving, so it suits people who already use whey and prefer an imported brand.</p>
<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%3A%20BPI%20Sports%20Micronised%20Creatine%20300%20g%20%28Unflavoured%29%20for%20Rs.%205%2C000.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="BPI Sports Micronised Creatine 300 g (Unflavoured)" data-value="5000">Order on WhatsApp – Rs. 5,000</a> <a class="tl" href="../../products/bpi-sports-micronized-creatine-300g-unflavored/">See the product page</a></p>"""}]),
  ("How to take creatine", [{"html": """<p><b>Daily dose:</b> 3 to 5 g a day, every day, including rest days. This is the maintenance dose recommended in the <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5469049/" target="_blank" rel="noopener">International Society of Sports Nutrition position stand</a>.</p>
<p><b>Loading or no loading?</b> Both work.</p>
<ul><li><b>With loading:</b> about 0.3 g per kg of body weight per day for 5 to 7 days, split into 3 or 4 doses (about 18 g a day for a 60 kg person), then 3 to 5 g a day. Your muscles fill up in about a week.</li>
<li><b>Without loading:</b> just take 3 to 5 g a day from day one. Your muscles fill up in about 3 to 4 weeks. This is simpler and easier on the stomach, so many beginners skip loading.</li></ul>
<p><b>Timing:</b> taking it every day matters far more than the exact time. Many people take it after training or with a meal because it is easy to remember.</p>
<p><b>Water:</b> mix each scoop with a full glass of water, and drink normally through the day.</p>
<p>More detail: <a href="../how-to-take-creatine/">how to take creatine</a> and <a href="../../blog/creatine-side-effects-myths-and-facts/">creatine side effects: myths and facts</a>.</p>"""}]),
  ("Best creatine in Nepal for beginners vs advanced lifters", [{"html": """<div class="tw"><table class="cmp"><thead><tr><th>You are...</th><th>Our pick</th><th>Why</th></tr></thead><tbody>
<tr><td>New to the gym, on a budget</td><td>MuscleBlaze or Wellcore, Rs. 2,000</td><td>Lowest cost, flavoured, mixes with water</td></tr>
<tr><td>You want the finest powder for water</td><td>Wellcore</td><td>Micronised and flavoured</td></tr>
<tr><td>Advanced, already taking whey</td><td>BPI Sports, Rs. 5,000</td><td>Unflavoured, blends into any shake</td></tr>
</tbody></table></div>"""}, "The honest answer: the best creatine in Nepal is the genuine one you will take every day. All three are creatine monohydrate."]),
  ("How to spot fake creatine in Nepal", ["Fake and refilled tubs are a real risk. Before you use any tub, check:",
     {"list": ["Seal: the inner foil seal must be unbroken when you open it.", "Batch number and expiry date: printed clearly on the tub, not on a loose sticker.", "Importer sticker: genuine imported tubs carry the importer's details.", "QR or authenticity code: if the label has one, scan it and check it on the brand's official website.", "Price: a tub far cheaper than the usual price in Nepal is a warning sign."]},
     {"html": """<p>At Apex, ask on WhatsApp and we send a photo of the seal and batch number before you pay. Full guide: <a href="../../blog/fake-supplements-in-nepal-how-to-spot-them/">how to spot fake supplements in Nepal</a>.</p>"""}]),
  ("Buy creatine online in Nepal: Urlabari, Jhapa, Kathmandu and everywhere", ["We are a gym in Urlabari-9, Morang, and we deliver creatine all over Nepal, including Jhapa, Itahari, Biratnagar, Kathmandu and Pokhara. Delivery is free and usually takes 1 to 2 days by Nepal Can. Tap Order on WhatsApp, we confirm stock and your address, and you pay by Cash on Delivery, Khalti or bank transfer. In Urlabari you can also pick it up at the gym."]),
  ("Starter combo: creatine + Pintola Oats – Rs. 3,100", [{"html": """<p>Get MuscleBlaze or Wellcore creatine plus <a href="../../products/pintola-high-protein-oats-chocolate-1kg/">Pintola High Protein Oats (1 kg)</a> for <b>Rs. 3,100</b> instead of Rs. 3,300, with free delivery all over Nepal. A simple start: oats for breakfast, creatine every day.</p>
<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20the%20Creatine%20%2B%20Pintola%20Oats%20starter%20combo%20for%20Rs.%203%2C100.%20Creatine%3A%20MuscleBlaze%20/%20Wellcore.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="Creatine + Pintola Oats starter combo" data-value="3100">Order the starter combo on WhatsApp – Rs. 3,100</a></p>"""}]),
  ("Sources", [{"html": """<ul><li><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5469049/" target="_blank" rel="noopener">ISSN position stand: safety and efficacy of creatine supplementation</a> (Kreider et al., 2017)</li><li><a href="https://exerciseandsportnutritionlab.com/new-issn-position-stand-on-creatine-supplementation/" target="_blank" rel="noopener">New ISSN position stand on creatine supplementation</a> (Exercise and Sport Nutrition Lab, Texas A&amp;M)</li></ul>
<p class="fine">General information, not medical advice. If you have kidney problems, are pregnant, or take regular medicine, talk to your doctor before taking creatine.</p>"""}]),
 ],
 faq=[("What is the creatine price in Nepal in 2026?", "At Apex Fitness Centre, MuscleBlaze Creatine (320 g) and Wellcore Creatine (307 g) are Rs. 2,000 each, and BPI Sports Micronised Creatine (300 g) is Rs. 5,000, with free delivery all over Nepal."),
      ("Which is the best creatine in Nepal for beginners?", "MuscleBlaze or Wellcore. Both cost Rs. 2,000, are flavoured and mix with water. All three brands are creatine monohydrate, so choose the one you will take every day."),
      ("Do I need a creatine loading phase?", "No. Loading fills your muscles in about a week; taking 3 to 5 g a day without loading fills them in about 3 to 4 weeks. Both work."),
      ("When should I take creatine?", "Any time of day. Taking it every day matters more than timing. After training or with a meal is easy to remember."),
      ("Can I buy creatine online in Nepal with free delivery?", "Yes. Order on WhatsApp and we deliver free all over Nepal by Nepal Can, usually in 1 to 2 days. Pay by Cash on Delivery, Khalti or bank transfer.")],
 rel=["how-to-take-creatine", "creatine-whey-price-nepal", "supplements-for-beginners-in-nepal"]),

dict(slug="creatine-or-whey-first", cat="creatine", table="creatine", published="2026-11-02",
 title="Creatine or Whey First? Budget Guide for Nepal (2026)",
 h1="Creatine or whey first? A budget guide for Nepal",
 desc="New to the gym with a small budget? What creatine and whey each do, the real cost per month in Nepal, and which one to buy first.",
 intro="If you are starting at the gym in Nepal and can only buy one supplement, the usual choice is between creatine and whey protein. They do different jobs and cost very different amounts each month. This guide helps you decide which one to buy first, using the prices we sell at today.",
 body=[
  ("What each one does, in plain words", ["Creatine monohydrate helps your muscles make quick energy for short, hard efforts like lifting or sprinting. Taken every day, it can help you do a little more work in training over time. It is not a protein and it does not replace food.", "Whey protein is protein from milk, made into a powder. It does nothing that food protein cannot do. Its value is convenience: one scoop in water or milk is an easy way to add protein on days when your meals fall short."]),
  ("Food first", ["Most of your protein should come from food. Dal, eggs, chicken, paneer, milk and curd are all good sources and easy to find in Nepal. If your meals already include a protein food two or three times a day, you may not need whey at all.", "Whey is worth buying when you struggle to reach your protein from food: for example if you are vegetarian with small portions, have little time to cook, or eat mostly rice and vegetables. The free protein calculator on this site shows roughly how much you need."]),
  ("What each costs per month in Nepal", ["Creatine: most people take about 3 to 5 g a day. A 320 g tub of MuscleBlaze Creatine at Rs. 2,000 lasts about 64 days at 5 g a day, or about 106 days at 3 g. That is roughly Rs. 560 to Rs. 940 a month. A 307 g tub of Wellcore Micronised Creatine at Rs. 2,000 lasts about 61 to 102 days, roughly Rs. 590 to Rs. 980 a month. BPI Sports Micronised Creatine (300 g, Rs. 5,000) works out at about Rs. 1,500 to Rs. 2,500 a month.", "Whey: a 2 kg tub at about 30 g a scoop gives roughly 66 scoops (check the scoop size on your label). At one scoop a day, MuscleBlaze Biozyme Performance Whey (2 kg, Rs. 15,000) costs about Rs. 225 a scoop, or about Rs. 6,750 a month. BigMan Forza Protein (2 kg, Rs. 17,500) is about Rs. 7,875 a month, and BPI Sports Hydro HD (2 kg, Rs. 23,000) about Rs. 10,350 a month.", "So for the same monthly budget, creatine costs a small fraction of whey."]),
  ("Our simple recommendation", ["Tight budget and you already eat protein foods most days: buy creatine first. It is cheap, one tub lasts two months or more, and food covers your protein.", "You cannot reach your protein from food: buy whey first. Protein matters more than creatine for building muscle, and whey is the easiest way to fill the gap.", "Either way, training regularly, eating enough and sleeping well matter far more than any supplement."]),
  ("If you want both", ["Our Muscle Gain Stack combines MuscleBlaze Biozyme Performance Whey (2 kg) and MuscleBlaze Creatine (320 g) for Rs. 16,500 instead of Rs. 17,000, a saving of Rs. 500. Delivery is free all over Nepal, and you can order it on WhatsApp."]),
 ],
 faq=[("Can I take creatine and whey together?", "Yes. They do different jobs and are often taken together, for example creatine mixed into your protein shake. Follow the label on each product. This is general information, not medical advice."),
      ("Which is better for beginners?", "It depends on your diet and budget. If you already eat enough protein from food, creatine is the cheaper first step. If you struggle to eat enough protein, whey helps more."),
      ("Do I need either one to build muscle?", "No. Regular training, enough food and protein, and good sleep build muscle without supplements. Creatine and whey can make it a little easier, but they are optional."),
      ("Is creatine safe?", "Creatine monohydrate is widely studied and is considered safe for healthy adults at normal doses. People with kidney problems or other conditions should ask a doctor first. This is general information, not medical advice.")],
 rel=["how-to-take-creatine", "creatine-price-in-nepal", "whey-protein-price-in-nepal"]),
dict(slug="creatine-whey-price-nepal", cat="creatine", table=["creatine", "protein"], published="2026-11-05",
 cta="Hi Apex Fitness Centre, I want to order creatine / whey protein. Please confirm what is in stock. Payment: COD / Khalti / Bank",
 title="Creatine and Whey Price in Nepal (2026) + Fake Check",
 h1="Creatine and whey protein price in Nepal (2026), and how to spot fakes",
 desc="Real creatine and whey protein prices in Nepal from Rs. 2,000, price per gram and per kg, and a simple checklist to spot fake supplements before you pay.",
 intro="Creatine and whey protein are the two supplements most gym members in Nepal buy first. Prices vary a lot between sellers, and fake or repacked tubs are a real problem. This page lists exactly what we sell today and what it costs, then shows you how to check that a tub is genuine.",
 body=[
  ("Creatine prices at a glance", ["We stock three creatine monohydrate tubs. MuscleBlaze Creatine Monohydrate 320 g (Citrus Blast) and Wellcore Micronised Creatine Monohydrate 307 g (Fruit Fusion) are both Rs. 2,000. BPI Sports Micronised Creatine 300 g (Unflavoured) is Rs. 5,000.",
   "All three are creatine monohydrate, the form with the most research behind it. The main differences are flavour and price per gram, shown in the table above."]),
  ("Whey protein prices at a glance", ["We stock three 2 kg protein tubs: MuscleBlaze Biozyme Performance Whey (French Vanilla Crème) at Rs. 15,000, BigMan Forza Protein at Rs. 17,500, and BPI Sports Hydro HD Hydrolyzed Whey (Chocolate Lava Cake) at Rs. 23,000.",
   "Check the scoop size and protein per scoop on the label of the tub you choose, because they differ between brands."]),
  ("Buying both? Save with a stack", ["MuscleBlaze Biozyme Performance Whey with MuscleBlaze Creatine, or with Wellcore Creatine, costs Rs. 16,500 instead of Rs. 17,000, a saving of Rs. 500. Add both to your cart or ask for the stack on WhatsApp."]),
  ("How to spot a fake supplement", ["Fake and repacked tubs often look almost the same as the real thing. Check these five things when your order arrives, and before you pay a new seller:",
   {"list": ["Seal: the inner seal under the lid should be intact, flat and properly stuck down, not loose, torn or re-glued.",
             "Batch number: printed clearly on the tub, matching the batch printed elsewhere on the pack. Smudged or sticker-printed numbers are a warning sign.",
             "Expiry date: printed clearly and in the future. Be careful with tubs very close to expiry sold at a big discount.",
             "Importer sticker: products sold legally in Nepal carry an importer label with the importer's name and address.",
             "QR or scratch code: if the brand uses one, scan it or check it on the brand's official website or app. A code that fails, or was already used, is a red flag."]},
   "Also be careful with prices far below normal. A Rs. 15,000 whey tub selling for Rs. 9,000 is usually old, repacked or fake. If anything looks wrong, don't open it, and message the seller straight away."]),
  ("How to order from Apex", ["Tap the button below or the Order on WhatsApp button on any product page. We confirm stock and your address, you pay by Cash on Delivery, Khalti or bank transfer, and delivery is free all over Nepal. Want to see it first? Ask on WhatsApp and we will send a photo of the seal and batch number before you pay."]),
 ],
 faq=[("What is the price of creatine in Nepal?", "At Apex Fitness Centre, creatine starts at Rs. 2,000 for MuscleBlaze Creatine Monohydrate 320 g or Wellcore Micronised Creatine 307 g. BPI Sports Micronised Creatine 300 g is Rs. 5,000."),
      ("What is the price of whey protein in Nepal?", "Our 2 kg protein tubs are Rs. 15,000 (MuscleBlaze Biozyme Performance Whey), Rs. 17,500 (BigMan Forza Protein) and Rs. 23,000 (BPI Sports Hydro HD Hydrolyzed Whey)."),
      ("How can I tell if my whey protein is fake?", "Check the inner seal, the printed batch number and expiry date, the importer sticker, and the QR or scratch code if the brand uses one. A price far below normal is also a warning sign."),
      ("Do you deliver all over Nepal?", "Yes. Delivery is free all over Nepal. Most orders arrive in 1 to 2 days.")],
 rel=["creatine-price-in-nepal", "whey-protein-price-in-nepal", "how-to-spot-fake-supplements-in-nepal"]),

dict(slug="best-protein-for-beginners-in-nepal", cat="protein", table=None, published="2026-11-10",
 title="Best Protein for Beginners in Nepal: Biozyme vs Forza",
 h1="Best protein for beginners in Nepal: MuscleBlaze Biozyme vs BigMan Forza",
 desc="Best protein for beginners in Nepal: MuscleBlaze Biozyme (Rs. 15,000) vs BigMan Forza (Rs. 17,500), how much protein you need and how to take it.",
 intro="If you are new to the gym and want your first protein powder, the two tubs most beginners ask us about are MuscleBlaze Biozyme Performance Whey at Rs. 15,000 and BigMan Forza Protein at Rs. 17,500. Both are 2 kg tubs. This guide compares them using only what is on our product pages and the labels, explains how much protein a beginner needs, and shows how to take it.",
 body=[
  ("The two tubs side by side", [{"html": """<div class="tw"><table class="cmp"><thead><tr><th></th><th><a href="../../products/muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme/">MuscleBlaze Biozyme Performance Whey</a></th><th><a href="../../products/bigman-forza-protein-2kg/">BigMan Forza Protein</a></th></tr></thead><tbody>
<tr><td>Price</td><td>Rs. 15,000</td><td>Rs. 17,500</td></tr>
<tr><td>Pack size</td><td>2 kg</td><td>2 kg (4.4 lb)</td></tr>
<tr><td>Type</td><td>Whey protein</td><td>Protein blend with creatine and MCT (per label)</td></tr>
<tr><td>Servings</td><td>See the serving size on the label</td><td>66 per tub</td></tr>
<tr><td>Flavour</td><td>French Vanilla Crème</td><td>See the label</td></tr>
<tr><td>Sugar</td><td>See the label</td><td>No added sugar (per label)</td></tr>
</tbody></table></div>"""}]),
  ("MuscleBlaze Biozyme Performance Whey (Rs. 15,000)", [
     "A whey protein in a 2 kg tub, in French Vanilla Crème flavour, which mixes well with water or milk. It is the lower-priced of the two and a simple first protein: one product that does one job.",
     "Choose it if you want a plain whey protein at the lower price, or if you plan to add creatine separately later.",
     {"html": """<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%3A%20MuscleBlaze%20Biozyme%20Performance%20Whey%202%20kg%20%28French%20Vanilla%20Cr%C3%A8me%29%20for%20Rs.%2015%2C000.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="MuscleBlaze Biozyme Performance Whey 2 kg (French Vanilla Crème)" data-value="15000">Order on WhatsApp – Rs. 15,000</a> <a class="tl" href="../../products/muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme/">See the product page</a></p>"""}]),
  ("BigMan Forza Protein (Rs. 17,500)", [
     "A protein blend that, according to its label, also contains creatine and MCT, with no added sugar. The 2 kg tub gives 66 servings, so it lasts a long time if you train most days.",
     "Choose it if you want protein and creatine in one scoop. Because it already contains creatine, check the label before adding a separate creatine product.",
     {"html": """<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20to%20order%3A%20BigMan%20Forza%20Protein%202%20kg%20for%20Rs.%2017%2C500.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="BigMan Forza Protein 2 kg" data-value="17500">Order on WhatsApp – Rs. 17,500</a> <a class="tl" href="../../products/bigman-forza-protein-2kg/">See the product page</a></p>"""}]),
  ("Which one should a beginner buy?", [
     {"list": ["On a budget, or want a simple whey: MuscleBlaze Biozyme, Rs. 15,000.", "Want protein with creatine already in it and train most days: BigMan Forza, Rs. 17,500.", "Not sure yet: start with food. A beginner who eats enough dal, eggs, paneer, soya, chicken or fish may not need powder at all in the first months."]},
     "Protein powder is a convenience, not a shortcut. The tub that helps most is the one you can afford to keep using and that fits your diet."]),
  ("How much protein does a beginner need?", [
     {"html": """<p>The International Society of Sports Nutrition suggests that most people who exercise do well on about <b>1.4 to 2.0 g of protein per kg of body weight per day</b>, from food and shakes together (<a href="https://pubmed.ncbi.nlm.nih.gov/28642676/" target="_blank" rel="noopener">Jäger et al., 2017</a>).</p>
<ul><li>A 60 kg beginner: about 84 to 120 g a day.</li><li>A 70 kg beginner: about 98 to 140 g a day.</li><li>An 80 kg beginner: about 112 to 160 g a day.</li></ul>
<p>Spread it over 3 or 4 meals. Use our free <a href="../../calculators/protein-calculator/">protein calculator</a> for your own number, and see <a href="../../blog/dal-bhat-protein/">how much protein is in dal bhat</a> and <a href="../../blog/protein-rich-vegetarian-foods-nepal/">protein-rich vegetarian foods in Nepal</a> to get more from food first.</p>"""}]),
  ("How to take protein powder", [
     {"list": ["Use the scoop in the tub and follow the serving size printed on the label.", "Mix with water or milk. Milk adds more protein and calories; water keeps it lighter.", "Most beginners only need one shake a day, after training or with a meal that is low in protein.", "Count the shake as part of your daily protein, not on top of a diet that already has plenty.", "On rest days, a shake is fine if your meals are short on protein."]},
     "If you have a kidney condition, a milk allergy or another health issue, ask your doctor before taking protein powder."]),
  ("Want both? The whey + creatine stack (Rs. 16,500)", [
     {"html": """<p>Our Muscle Gain Stack combines <a href="../../products/muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme/">MuscleBlaze Biozyme Performance Whey (2 kg)</a> with <a href="../../products/muscleblaze-creatine-monohydrate-320g-citrus-blast/">MuscleBlaze Creatine (320 g)</a> for <b>Rs. 16,500</b> instead of Rs. 17,000, a saving of Rs. 500, with free delivery all over Nepal. Whey helps you reach your daily protein; creatine supports strength in training. New to creatine? Read <a href="../how-to-take-creatine/">how to take creatine</a>.</p>
<p>If you choose BigMan Forza, you do not need this stack: Forza already contains creatine, according to its label.</p>
<p><a class="btn wa" href="https://wa.me/9779708819605?text=Hi%20Apex%20Fitness%20Centre%2C%20I%20want%20the%20Muscle%20Gain%20Stack%3A%20MuscleBlaze%20Biozyme%20Whey%202%20kg%20%2B%20MuscleBlaze%20Creatine%20320%20g%20for%20Rs.%2016%2C500.%20Please%20confirm%20stock.%20Payment%3A%20COD%20/%20Khalti%20/%20Bank" target="_blank" rel="noopener" data-product="Muscle Gain Stack: Biozyme Whey + MuscleBlaze Creatine" data-value="16500">Order the stack on WhatsApp – Rs. 16,500</a></p>"""}]),
  ("Ordering from Apex", ["Order on WhatsApp from this page or any product page. We confirm stock, you pay by Cash on Delivery, Khalti or bank transfer, and Nepal Can delivers all over Nepal, usually in 1 to 2 days, with free delivery. Every tub is authentic and comes with a bill."]),
  ("Sources", [{"html": """<ul><li><a href="https://pubmed.ncbi.nlm.nih.gov/28642676/" target="_blank" rel="noopener">ISSN position stand: protein and exercise</a> (Jäger et al., 2017)</li></ul><p class="fine">General information, not medical advice. If you have kidney problems, a milk allergy, are pregnant or take regular medicine, talk to your doctor before taking protein powder.</p>"""}]),
 ],
 faq=[("What is the best protein for beginners in Nepal?", "For most beginners, a simple whey such as MuscleBlaze Biozyme Performance Whey (Rs. 15,000, 2 kg). If you want protein with creatine already included, BigMan Forza (Rs. 17,500, 2 kg, 66 servings) is the other option."),
      ("How much protein does a beginner need per day?", "Most people who exercise do well on about 1.4 to 2.0 g of protein per kg of body weight a day from food and shakes together, according to the International Society of Sports Nutrition."),
      ("How many protein shakes should a beginner drink a day?", "Usually one. Follow the serving size on the label and count the shake as part of your daily protein from food."),
      ("Can I take creatine with BigMan Forza?", "Forza already contains creatine according to its label, so check the label before adding a separate creatine product."),
      ("Do you deliver protein all over Nepal?", "Yes. Delivery is free all over Nepal by Nepal Can, usually in 1 to 2 days, and you can pay by Cash on Delivery, Khalti or bank transfer.")],
 rel=["whey-protein-price-in-nepal", "creatine-whey-price-nepal", "supplements-for-beginners-in-nepal"]),

dict(slug="whey-protein-price-in-nepal", cat="protein", table=None, published="2026-11-13",
 title="Whey Protein Price in Nepal (2026): MuscleBlaze vs BigMan vs BPI",
 h1="Whey protein price in Nepal (2026): MuscleBlaze vs BigMan vs BPI",
 desc="Whey protein price in Nepal 2026: MuscleBlaze Biozyme Rs. 15,000, BigMan Forza Rs. 17,500, BPI Hydro HD Rs. 23,000. Price per kg and per serving compared.",
 intro="The three 2 kg protein tubs we sell cost Rs. 15,000 (MuscleBlaze Biozyme Performance Whey), Rs. 17,500 (BigMan Forza Protein) and Rs. 23,000 (BPI Sports Hydro HD Hydrolyzed Whey). The tub price is only half the story, so below we compare the price per kg and, where the serving count is on our product page, the price per serving.",
 body=[
  ("MuscleBlaze vs BigMan vs BPI: price comparison", [{"html": WHEY_TABLE}]),
  ("How to compare protein prices", ["Do not look only at the tub price. Divide the price by the kilograms in the pack to get the price per kg, then divide it by the number of servings to get the price per shake. Next, check the label for protein per serving: a cheaper tub can give less protein per scoop.", "All three tubs here are 2 kg, so the price per kg follows the tub price: about Rs. 7,500 per kg for Biozyme, Rs. 8,750 for Forza and Rs. 11,500 for Hydro HD."]),
  ("MuscleBlaze Biozyme Performance Whey 2 kg (Rs. 15,000)", ["The lowest price of the three. A whey protein in French Vanilla Crème flavour, and a simple first protein: one product that does one job.", {"html": WHEY_BTN["muscleblaze-biozyme-performance-whey-2kg-french-vanilla-creme"]}]),
  ("BigMan Forza Protein 2 kg (Rs. 17,500)", ["A protein blend that, according to its label, also contains creatine and MCT. The 2 kg tub gives 66 servings, which works out at about Rs. 265 per serving. If you take Forza, check the label before adding a separate creatine product.", {"html": WHEY_BTN["bigman-forza-protein-2kg"]}]),
  ("BPI Sports Hydro HD Hydrolyzed Whey 2 kg (Rs. 23,000)", ["A hydrolysed whey in Chocolate Lava Cake flavour. Hydrolysed whey is processed to digest faster and usually costs more than regular whey. It is the premium option of the three; most people do not need it to build muscle.", {"html": WHEY_BTN["bpi-sports-hydro-hd-hydrolyzed-whey-2kg-chocolate-lava-cake"]}]),
  ("Which one should you buy?", [{"list": ["Lowest price and a plain whey: MuscleBlaze Biozyme, Rs. 15,000.", "Protein and creatine in one scoop: BigMan Forza, Rs. 17,500.", "Want a hydrolysed whey and do not mind paying more: BPI Hydro HD, Rs. 23,000."]}, {"html": '<p>New to protein powder? Read <a href="../best-protein-for-beginners-in-nepal/">best protein for beginners in Nepal</a>, see all tubs on our <a href="../../protein/">protein page</a>, or browse all <a href="../">buying guides</a>.</p>'}]),
  ("How much protein do you need", ["Many active adults aim for about 1.4 to 2.0 g of protein per kg of body weight a day, from food and shakes together. A shake adds to your meals and does not replace them. If you eat enough protein from dal, eggs, paneer, soya and meat, you may need less powder."]),
  ("Ordering from Apex", ["Order on WhatsApp from this page or any product page. We confirm stock, you pay by Cash on Delivery, Khalti or bank transfer, and Nepal Can delivers all over Nepal, usually in 1 to 2 days, with free delivery. Every tub is authentic and comes with a bill."]),
 ],
 faq=[("How much is 2 kg whey protein in Nepal?", "At Apex Fitness Centre, 2 kg tubs cost Rs. 15,000 (MuscleBlaze Biozyme Performance Whey), Rs. 17,500 (BigMan Forza Protein) and Rs. 23,000 (BPI Sports Hydro HD Hydrolyzed Whey), with free delivery all over Nepal."),
      ("Which is cheapest per kg: MuscleBlaze, BigMan or BPI?", "MuscleBlaze Biozyme, at about Rs. 7,500 per kg. BigMan Forza is about Rs. 8,750 per kg and BPI Hydro HD about Rs. 11,500 per kg."),
      ("What is the price per serving of BigMan Forza?", "The 2 kg tub has 66 servings, so about Rs. 265 per serving at Rs. 17,500."),
      ("Is hydrolysed whey worth the extra cost?", "It digests faster, but for most people regular whey builds muscle just as well when daily protein is enough. Choose hydrolysed whey only if you prefer it and the price fits your budget."),
      ("Can I pay cash on delivery for protein?", "Yes. You can pay by Cash on Delivery, Khalti or bank transfer, and delivery is free all over Nepal, usually in 1 to 2 days.")],
 rel=["best-protein-for-beginners-in-nepal", "how-much-protein-do-you-need", "how-to-spot-fake-supplements-in-nepal"]),

dict(slug="how-to-spot-fake-supplements-in-nepal", cat="shop", table=None,
 title="How to Spot Fake Supplements in Nepal: 8-Point Check",
 h1="How to spot fake supplements in Nepal",
 desc="A simple 8-point checklist to tell genuine supplements from fake or repacked ones in Nepal, and how to buy safely online.",
 intro="Fake and repacked supplements are a real problem. They waste your money and can be unsafe. This checklist helps you protect yourself, whoever you buy from.",
 body=[
  ("The 8-point check", [
    {"list": ["Look at the seal. The inner foil seal must be unbroken, printed and neat. A missing or re-glued seal is a red flag.",
              "Find the batch number and expiry date. They should be clearly printed on the tub, not on a sticker that peels off.",
              "Check the label. Spelling mistakes, blurry print and faded colours are warning signs.",
              "Compare the price. A price far below every other seller usually means a fake, an old stock or a repack.",
              "Ask for a bill. A real seller gives you one and tells you where the stock came from.",
              "Check the brand's own verification. Some brands have a scan or code check on the pack. Use it if your product has one.",
              "Look at the seller. Check for real reviews, a real shop address and a phone number that answers.",
              "Trust your senses. Strange smell, texture or taste, or a tub that looks refilled, means stop and do not use it."]}]),
  ("What to do if you doubt a product", ["Do not use it. Keep the tub and the bill, take clear photos of the seal, label and batch number, and ask the seller for an explanation. A genuine seller will answer calmly."]),
  ("How Apex tries to earn your trust", ["We sell only authentic products and give a bill with every order. We show real customer reviews with their photos on our site. You can message us on WhatsApp before you buy and ask for photos of the exact tub you will receive."]),
 ],
 faq=[("How can I check if my whey protein is original?", "Check the seal, batch number and expiry date, the label quality, and the price. Use the brand's verification method if there is one, and buy from a seller who gives a bill."),
      ("Is cheap supplement in Nepal always fake?", "Not always, but a price far below other sellers is a warning sign. Ask where the stock came from and ask for a bill."),
      ("Can I ask for a photo before I buy?", "Yes. Message us on WhatsApp and we can send photos of the product before you order.")],
 rel=["creatine-price-in-nepal", "whey-protein-price-in-nepal", "buy-supplements-online-in-nepal"]),

dict(slug="how-to-take-creatine", cat="creatine", table=None,
 title="How to Take Creatine: Simple Guide for Beginners in Nepal",
 h1="How to take creatine",
 desc="How much creatine to take, when to take it, whether to load, and what to expect. A simple, honest guide for beginners.",
 intro="Creatine is simple to use, but there is a lot of confusing advice. Here is the plain version.",
 body=[
  ("The simple way", [{"list": ["Take about 3 to 5 g of creatine monohydrate a day. Check the scoop size on your tub.", "Take it every day, including rest days.", "Any time works. Pick a time you will remember, such as with your post-workout shake or with breakfast.", "Mix it in water, juice or a shake, and drink water through the day."]}]),
  ("Do you need to load?", ["No. Loading means taking about 20 g a day for 5 to 7 days, then dropping to a normal dose. It fills your muscles faster, but a normal daily dose reaches the same level after a few weeks."]),
  ("What to expect", ["Creatine is not a steroid and does not give instant results. Over weeks it can help you do a little more work in the gym, such as an extra rep. Results vary from person to person, and training, food and sleep matter much more."]),
  ("Who should be careful", ["Ask a doctor first if you have a kidney condition, take regular medicines, or are under 18. This is general information, not medical advice."]),
 ],
 faq=[("Should I take creatine on rest days?", "Yes. Take it every day so the level in your muscles stays up."),
      ("Does creatine make you gain weight?", "It can cause a small rise in body weight in the first weeks because muscles hold more water. This is normal and not fat gain."),
      ("Which creatine should I buy in Nepal?", "Choose creatine monohydrate from a brand you trust, in a sealed tub with a batch number, from a seller who gives a bill.")],
 rel=["creatine-price-in-nepal", "supplements-for-beginners-in-nepal", "how-to-spot-fake-supplements-in-nepal"]),

dict(slug="how-much-protein-do-you-need", cat="protein", table=None,
 title="How Much Protein Do You Need Per Day? (Nepal Food Guide)",
 h1="How much protein do you need per day",
 desc="A simple way to work out your daily protein target, with protein in common Nepali foods and when protein powder helps.",
 intro="Most people either guess or copy someone else. This is a simple way to work out your own number, and to see how much you may already get from food.",
 body=[
  ("A simple target", ["For a healthy adult who does not train, about 0.8 g of protein per kg of body weight a day is the usual minimum. For people who lift weights, many guidelines suggest about 1.4 to 2.0 g per kg a day.", "Example: if you weigh 65 kg and train regularly, that is about 90 to 130 g of protein a day."]),
  ("Protein in common foods (approximate)", [{"list": ["1 egg: about 6 g", "1 cup cooked dal (lentils): about 12 to 18 g", "100 g paneer: about 18 g", "100 g chicken breast, cooked: about 30 g", "100 g soya chunks, dry: about 50 g", "1 glass of milk (250 ml): about 8 g"]}, "These are rough values. Check labels for the exact amount."]),
  ("When protein powder helps", ["Powder is useful when you find it hard to eat enough protein from food, are busy, or want a quick shake after training. It adds to your diet and does not replace meals. If you already reach your target with food, you do not need it."]),
  ("People who should ask a doctor first", ["If you have a kidney condition or another medical problem, ask a doctor before you raise your protein. This is general information, not medical advice."]),
 ],
 faq=[("Can I get enough protein without supplements?", "Yes, many people can with eggs, dal, paneer, soya, milk and meat. Powder only makes it easier."),
      ("Is 2 g of protein per kg too much?", "It is the upper end of what many guidelines suggest for people who lift weights. Ask a doctor if you have a health condition."),
      ("When should I have a protein shake?", "Any time that helps you reach your daily total. After training is a common and convenient time.")],
 rel=["whey-protein-price-in-nepal", "supplements-for-beginners-in-nepal", "how-to-take-creatine"]),

dict(slug="supplements-for-beginners-in-nepal", cat="shop", table=None,
 title="Supplements for Beginners in Nepal: What to Buy First",
 h1="Supplements for beginners in Nepal",
 desc="What a beginner really needs, what to skip, and the order to buy supplements in Nepal if you are on a budget.",
 intro="You do not need a shelf of tubs to start. Food, training and sleep do most of the work. If you want to add supplements, here is a sensible order.",
 body=[
  ("Start with the basics", ["Eat enough protein and calories, train with a plan, and sleep well. No supplement fixes a poor routine."]),
  ("A sensible buying order", [{"list": ["Protein powder, only if you cannot reach your protein from food.", "Creatine monohydrate, the most researched and usually the best value.", "Pre-workout, only if you want extra energy for training and you handle caffeine well.", "Everything else, such as BCAAs and fat burners, can wait. Most beginners do not need them."]}]),
  ("Watch your budget", ["Spend on a good, authentic basic product before you buy many products. One well-chosen tub is better than five random ones."]),
  ("Safety", ["Follow the label. Be careful with caffeine if you are sensitive, and do not mix several products that each contain caffeine. Ask a doctor if you have a health condition or are under 18. This is general information, not medical advice."]),
 ],
 faq=[("What supplement should a beginner take first?", "Often protein powder if food falls short, or creatine monohydrate. Neither is required."),
      ("Do I need a pre-workout?", "No. It is optional. If you take one, start with a small amount and check the caffeine."),
      ("Can I start supplements at 17?", "Ask a doctor or parent first. Under 18, food and training should come first.")],
 rel=["creatine-price-in-nepal", "whey-protein-price-in-nepal", "how-much-protein-do-you-need"]),

dict(slug="buy-supplements-online-in-nepal", cat="shop", table=None,
 title="Buy Supplements Online in Nepal Safely (Delivery, Payment)",
 h1="How to buy supplements online in Nepal safely",
 desc="How to buy supplements online in Nepal without getting fake products: what to check, how payment and delivery work, and how to order from Apex.",
 intro="Buying online is convenient, but you cannot touch the tub first. These checks protect you.",
 body=[
  ("Before you pay", [{"list": ["Check that the seller has a real address, phone number and reviews.", "Ask for photos or a short video of the exact product.", "Ask if you will get a bill.", "Ask how long delivery takes and how it is sent.", "Check the price against other sellers. Be careful if it is far lower."]}]),
  ("How ordering works at Apex", ["Pick a product and tap Order on WhatsApp, or add items to your cart. We confirm stock and your address, you pay by Cash on Delivery, Khalti or bank transfer, and we send it by Nepal Can with a tracking number. Delivery is free all over Nepal and usually takes 1 to 2 days."]),
  ("When your parcel arrives", ["Check that the outer seal and the inner seal are unbroken and the batch number is printed. If anything looks wrong, take photos and message us the same day."]),
  ("Returns", ["Sealed, unopened items can be returned. Opened supplements cannot be returned, so check everything before you open the tub."]),
 ],
 faq=[("Is it safe to pay in advance?", "Pay only a seller you can verify. Check reviews, ask for photos, and keep the payment screenshot and bill."),
      ("How long does delivery take in Nepal?", "From Apex, delivery is usually 1 to 2 days all over Nepal."),
      ("Can I pay by Khalti?", "Yes. You can pay by Cash on Delivery, Khalti or bank transfer. We send Khalti and bank details on WhatsApp.")],
 rel=["how-to-spot-fake-supplements-in-nepal", "creatine-price-in-nepal", "whey-protein-price-in-nepal"]),

dict(slug="how-to-choose-a-pre-workout-in-nepal", cat="pre-workout", table="pre-workout",
 title="Pre-Workout Price in Nepal (2026) and How to Choose One",
 h1="Pre-workout price in Nepal and how to choose one",
 desc="Pre-workout price in Nepal, cost per serving, how much caffeine is safe, who should avoid it, and how to spot a genuine tub.",
 intro="A pre-workout is meant to help your energy and focus before training. It is optional, and the most important thing to check is the caffeine.",
 body=[
  ("Check the caffeine first", ["Look for caffeine per serving on the label. Many people feel fine around 150 to 300 mg. If you are new or sensitive, start with half a serving. Do not combine it with coffee, energy drinks or other caffeine products."]),
  ("Timing", ["Take it about 20 to 30 minutes before training, and avoid it late in the evening so it does not ruin your sleep."]),
  ("Who should avoid it", ["People who are under 18, pregnant, sensitive to caffeine, or who have heart, blood pressure or anxiety problems should ask a doctor first. This is general information, not medical advice."]),
  ("What we stock", ["We stock Scitron Volcano Pre-Workout. Check the label on your pack for the exact caffeine and serving details, and read the customer review on the product page."]),
 ],
 faq=[("How much caffeine is in a pre-workout?", "It varies. Check the label for caffeine per serving and start with a smaller amount if you are new."),
      ("Can I take pre-workout every day?", "Many people take it only on harder training days to avoid building up tolerance and to protect their sleep."),
      ("Do I need a pre-workout?", "No. It is optional. Sleep, food and a good plan matter more.")],
 rel=["supplements-for-beginners-in-nepal", "how-to-take-creatine", "buy-supplements-online-in-nepal"]),

dict(slug="send-supplements-to-family-in-nepal", cat="shop", table=None,
 title="Send Supplements to Family in Nepal from Abroad | Apex",
 h1="Send supplements to family in Nepal from abroad",
 desc="Living abroad? Order genuine protein, creatine and other supplements for family in Nepal. Pay by bank or Khalti from abroad, or your family pays Cash on Delivery. Free delivery all over Nepal.",
 intro="Many Nepalis abroad want to send protein or creatine home, but shipping from overseas is slow and costly, and fakes are common. You can order from Apex Fitness Centre in Nepal and we deliver to your family locally.",
 body=[
  ("How it works", [{"list": ["Message us on WhatsApp at 9708819605 and tell us which products you want.",
                              "Send your family member's name, phone number and address in Nepal.",
                              "Pay directly to our bank account or by Khalti, or your family can pay Cash on Delivery when it arrives. We send the payment details on WhatsApp.",
                              "We confirm your payment and send the parcel by Nepal Can, free of charge.",
                              "Your family receives it, usually in 1 to 2 days, and we share the tracking number with you."]}]),
  ("Why order from inside Nepal", ["The parcel does not cross a border, so there are no overseas shipping fees or customs delays. You get a local seller you can message, a bill, and delivery in days instead of weeks."]),
  ("Before you order", ["Ask us for photos of the exact products, and ask your family to check that the seals are unbroken when the parcel arrives. Tell them to message us the same day if anything looks wrong."]),
  ("What people send most", ["Protein powder, creatine monohydrate and pre-workout are the most common choices. See our price guides for current prices before you decide."]),
 ],
 faq=[("Can I pay from outside Nepal?", "Yes. You can pay directly to our bank account or by Khalti, or your family can pay Cash on Delivery when it arrives. Message us on WhatsApp and we will send the details."),
      ("Do you deliver to any part of Nepal?", "Yes. Delivery is free all over Nepal by Nepal Can, usually in 1 to 2 days."),
      ("How do I know the order reached my family?", "We send you the tracking number, and your family can confirm on WhatsApp when it arrives.")],
 rel=["buy-supplements-online-in-nepal", "creatine-price-in-nepal", "whey-protein-price-in-nepal"]),

dict(slug="gym-management-software-price-in-nepal", cat="software", table=None, sw=True,
 title="Gym Management Software Price in Nepal (2026) | What It Costs",
 h1="Gym management software price in Nepal",
 desc="What gym management software costs in Nepal in 2026: monthly plans versus one-time payment, what to check before buying, and a one-time option at Rs. 25,000.",
 intro="If you own a gym in Nepal, you will see two kinds of pricing for gym software: a monthly subscription, or one payment. This guide explains the difference, what to check before you buy, and what a one-time price looks like.",
 body=[
  ("Monthly plans versus one-time payment", ["Many gym apps charge a fee every month, often based on the number of members. That feels cheap at first, but over two or three years the total is often higher than a one-time price, and you stop having the software when you stop paying.", "A one-time payment costs more on day one, but you pay once and keep using it. For a gym that runs for many years, one payment is usually the cheaper choice."]),
  ("What Apex Gym Management costs", ["Apex Gym Management costs Rs. 25,000 as a one-time payment. There is no monthly fee and no per-member fee. It includes installation, setup of your plans and prices, staff training and a step-by-step PDF guide."]),
  ("What to check before you buy any gym software", [{"list": ["Does it show who is expiring this week, with days left?", "Does it separate membership dues from product dues?", "Can you freeze a member who is sick or travelling?", "Does it back up your data automatically?", "Can you limit what each staff member can do?", "Does it work if the internet is down?", "Who will help you set it up and train staff?"]}]),
  ("Who is it for", ["Small and medium gyms in Nepal that run on a notebook, Excel or memory, and want to stop losing money to forgotten dues and missed renewals. It is built and used every day at Apex Fitness Centre in Urlabari, Morang."]),
 ],
 faq=[("How much does gym software cost in Nepal?", "Prices vary. Monthly apps charge every month. Apex Gym Management is Rs. 25,000 one-time with no monthly fee."),
      ("Is there a free gym management software for Nepal?", "Free tools like Excel exist but do not track expiry, dues and reminders for you or back up automatically. Paid software saves time and prevents lost payments."),
      ("Can I try it before I buy?", "Yes. Message Apex Fitness Centre on WhatsApp at 9708819605 for a free demo.")],
 rel=["how-to-choose-gym-software-in-nepal", "gym-membership-management-excel-vs-software", "buy-supplements-online-in-nepal"]),

dict(slug="how-to-choose-gym-software-in-nepal", cat="software", table=None, sw=True,
 title="How to Choose Gym Software in Nepal: Owner's Checklist",
 h1="How to choose gym management software in Nepal",
 desc="A checklist for Nepal gym owners: member tracking, dues, freeze, WhatsApp reminders, backup, staff permissions and price. Pick the right gym software.",
 intro="The best gym software is the one your front desk will actually use every day. Here is a plain checklist for gym owners in Nepal.",
 body=[
  ("1. It must be simple at the front desk", ["Your staff are busy in the morning rush. Adding a member, renewing and checking in should take seconds. If staff need a long training, they will go back to the notebook."]),
  ("2. It must handle dues properly", ["Most gyms lose money to unpaid dues. Look for a dues list that shows who owes what, separates membership from product dues, and lets you collect on one screen with a receipt."]),
  ("3. Freeze and expiry must be exact", ["Members get sick, travel and exam seasons happen. You need exact end dates, days left, and a freeze that stops the days and restores them later."]),
  ("4. WhatsApp reminders", ["In Nepal most members use WhatsApp. A good system prepares the message with the name and amount. Be careful of anyone who promises fully automatic WhatsApp sending, because WhatsApp does not allow that for normal numbers."]),
  ("5. Backup and security", ["A computer can fail. Choose software that backs up by itself every day and can save a second copy to a USB drive or cloud folder. Staff should have separate logins with limited permissions."]),
  ("6. Price: monthly or one-time", ["Compare the total cost over three years, not the first month. Apex Gym Management is Rs. 25,000 one-time with no monthly fee."]),
 ],
 faq=[("What features should gym software have?", "Member records, renewals, expiry tracking, dues, freeze, attendance, sales, staff logins, reports and automatic backup."),
      ("Does gym software need internet?", "Not always. Apex Gym Management works without internet and only needs it to open WhatsApp."),
      ("Where can I get a demo?", "Message Apex Fitness Centre on WhatsApp at 9708819605.")],
 rel=["gym-management-software-price-in-nepal", "gym-membership-management-excel-vs-software", "supplements-for-beginners-in-nepal"]),

dict(slug="gym-membership-management-excel-vs-software", cat="software", table=None, sw=True,
 title="Excel vs Gym Software in Nepal: Which Is Better for Your Gym?",
 h1="Excel or notebook vs gym software",
 desc="Should a Nepal gym use Excel, a notebook or gym management software? A fair comparison of cost, dues, expiry tracking, reminders and backup.",
 intro="Many gyms start with a notebook or an Excel sheet. It works while you have few members. Here is where it starts to cost you money, and when software is worth it.",
 body=[
  ("Where notebooks and Excel work", ["They are free and familiar. For a very small gym with a few dozen members, they can be enough."]),
  ("Where they fail", [{"list": ["Nobody tells you who is expiring this week.", "Dues are easy to forget and hard to total.", "Freezing a sick member means editing dates by hand.", "Anyone can change a number and you cannot see who did it.", "One lost file or one broken computer can erase everything.", "Sending reminders means copying names and numbers one by one."]}]),
  ("When software pays for itself", ["If forgetting a few dues or renewals a month costs you more than a few thousand rupees, software pays for itself quickly. Apex Gym Management is Rs. 25,000 one-time, so it can pay itself back within months for a gym with many members."]),
  ("How to switch", ["We install the program, add your plans and prices, and help you bring in your member list. Your staff learn it in about a day."]),
 ],
 faq=[("Is Excel good enough for a gym?", "For a very small gym, yes. As members grow, Excel cannot track expiry, dues and reminders for you."),
      ("How much is gym software in Nepal?", "Apex Gym Management is Rs. 25,000, one-time, no monthly fee."),
      ("Can I move my members from Excel?", "Yes. We help you bring in your member list during setup.")],
 rel=["gym-management-software-price-in-nepal", "how-to-choose-gym-software-in-nepal", "buy-supplements-online-in-nepal"]),
]
