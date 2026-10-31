# Single-purpose calculator pages: /calculators/<slug>/. exec()'d by build.py after the blog is built,
# so it can link only to blog posts that are already published (POSTS).
_LIVE = {p["slug"] for p in POSTS}

def _tsex(p, opts=(("male", "Male"), ("female", "Female")), legend="Sex", hint=None):
    ch = "".join(f'<label class="choice"><input type="radio" name="{p}-sex" value="{v}" data-field="sex"><span>{l}</span></label>' for v, l in opts)
    h = f'<div class="hint" id="{p}-sex-h">{hint}</div>' if hint else ""
    return (f'<fieldset aria-describedby="{p}-sex-e"><legend class="l">{legend}</legend><div class="choices">{ch}</div>{h}'
            f'<p class="err" id="{p}-sex-e" data-err="sex" role="alert" hidden></p></fieldset>')

def _tsel(p, name, label, opts):
    o = "".join(f'<option value="{v}">{e(l)}</option>' for v, l in opts)
    return (f'<div class="f"><label class="l" for="{p}-{name}">{label}</label><select id="{p}-{name}" data-field="{name}" aria-describedby="{p}-{name}-e">'
            f'<option value="">Choose one</option>{o}</select><p class="err" id="{p}-{name}-e" data-err="{name}" role="alert" hidden></p></div>')

def _tlen(p, name, label, ph_cm, ph_in, extra=""):
    return (f'<div class="f"{extra}><label class="l" for="{p}-{name}">{label} <span data-metric>(cm)</span><span data-imperial>(inches)</span></label>'
            f'<div class="inwrap"><input type="text" inputmode="decimal" autocomplete="off" id="{p}-{name}" data-field="{name}" placeholder="e.g. {ph_cm}" aria-describedby="{p}-{name}-e">'
            f'<span class="u" data-metric>cm</span><span class="u" data-imperial>in</span></div>'
            f'<p class="err" id="{p}-{name}-e" data-err="{name}" role="alert" hidden></p></div>')

_ACTS = [("sedentary", "Sedentary: desk job, little exercise"), ("light", "Light: exercise 1–3 days a week"),
         ("moderate", "Moderate: exercise 3–5 days a week"), ("very", "Very active: hard exercise 6–7 days a week"),
         ("extra", "Extra active: hard training and a physical job")]

def _src(items): return "<h2>Sources</h2><ul>" + "".join(f'<li><a href="{u}" rel="noopener">{e(t)}</a> ({e(p)})</li>' for t, u, p in items) + "</ul>"

TOOLS = [
dict(slug="protein-calculator", short="Protein", card="Grams of protein a day for your goal",
 title="Protein Calculator: How Much Protein Do You Need a Day?",
 desc="Free protein calculator. Find how many grams of protein you need a day to build muscle, lose fat or stay healthy, based on your weight and goal.",
 h1="Protein <em>Calculator</em>",
 lead="Find out how many grams of protein you need each day, based on your body weight and your goal, with per-meal targets and everyday food examples.",
 form=lambda: f"""{_calc_weight("protein")}
{_tsel("protein", "goal", "Your goal", [("general","Stay healthy (little exercise)"),("active","Stay fit (regular exercise or sport)"),("muscle","Build muscle"),("cut","Lose fat and keep muscle"),("older","Healthy ageing (65 and over)")])}""",
 about="""<h2>How much protein do you need?</h2>
<p>The basic recommendation for healthy adults is <b>0.8 g of protein per kg of body weight a day</b>. That is the minimum to avoid deficiency, not the best amount for people who train. Research on people doing strength training points to higher intakes:</p>
<table><thead><tr><th>Goal</th><th>Protein per kg per day</th><th>Example for 70 kg</th></tr></thead><tbody>
<tr><td>Little exercise</td><td>0.8 g</td><td>56 g</td></tr>
<tr><td>Regular exercise or sport</td><td>1.2–1.6 g</td><td>84–112 g</td></tr>
<tr><td>Building muscle</td><td>1.6–2.2 g</td><td>112–154 g</td></tr>
<tr><td>Losing fat while lifting</td><td>1.8–2.2 g</td><td>126–154 g</td></tr>
<tr><td>Adults over 65</td><td>1.0–1.2 g (more if training)</td><td>70–84 g</td></tr>
</tbody></table>
<p>A large meta-analysis found that muscle gains from strength training levelled off at around <b>1.6 g per kg a day</b>, with an upper confidence limit of about 2.2 g. The International Society of Sports Nutrition recommends 1.4–2.0 g per kg for most exercising people.</p>
<h2>How to use your result</h2>
<ul><li><b>Spread it out.</b> Three or four meals with 20–40 g of protein each works well for most people.</li>
<li><b>Food first.</b> Eggs, chicken, fish, meat, dal, chana, rajma, paneer, curd, milk, tofu and soybeans all count.</li>
<li><b>Use a shake only to fill the gap.</b> Whey or plant protein is convenient, not essential.</li>
<li><b>Overweight?</b> Use a goal weight, or your weight minus some of the extra fat, rather than your current weight, or the target will be higher than you need.</li></ul>
<h2>Is too much protein harmful?</h2>
<p>For healthy adults, intakes in these ranges are considered safe. People with kidney disease, or at high risk of it, should follow their doctor's advice, because they may need to limit protein.</p>""",
 faq=[("How much protein do I need to build muscle?", "Most research suggests about 1.6 g of protein per kg of body weight a day, and up to 2.2 g for some people. For a 70 kg person that is about 112–154 g a day, alongside regular strength training."),
      ("Is 100 g of protein a day enough?", "It depends on your weight and goal. For a 60–65 kg person building muscle, 100 g is close to the target. A heavier person or someone dieting while lifting may need more."),
      ("Should I use my current weight or goal weight?", "Use your current weight if you are fairly lean. If you are carrying a lot of extra fat, use a goal weight so the target is realistic."),
      ("Can vegetarians get enough protein?", "Yes. Combine dal, chana, rajma, soybeans, paneer, curd, milk and tofu across the day, and add a protein powder if needed."),
      ("Can I eat all my protein in one meal?", "You can, but spreading it across three or four meals is easier to digest and may be slightly better for building muscle.")],
 sources=[("Protein supplementation and resistance training: systematic review and meta-analysis","https://bjsm.bmj.com/content/52/6/376","Morton et al., British Journal of Sports Medicine, 2018"),
          ("ISSN position stand: protein and exercise","https://pubmed.ncbi.nlm.nih.gov/28642676/","Jäger et al., 2017")],
 posts=["how-much-protein-do-you-need","protein-rich-vegetarian-foods-nepal","high-protein-nepali-diet-plan-for-muscle-gain","best-whey-protein-in-nepal","creatine-vs-whey-which-first","high-protein-breakfast-ideas-nepal","protein-on-glp-1-medication","high-protein-nepali-meals-australia"]),

dict(slug="one-rep-max-calculator", short="One-rep max", card="Estimate your 1RM and training weights",
 title="One Rep Max Calculator (1RM): Bench, Squat, Deadlift",
 desc="Free one rep max calculator. Estimate your 1RM for bench press, squat or deadlift from any set of 1–12 reps, with a percentage chart for training.",
 h1="One-Rep Max <em>Calculator</em>",
 lead="Estimate the most weight you could lift for one rep, without testing it, then get a percentage chart to plan your training weights.",
 form=lambda: f"""{_calc_num("orm-lift", '<span data-metric>Weight lifted (kg)</span><span data-imperial>Weight lifted (lb)</span>', "lift", "kg", "lb", "e.g. 60", "decimal")}
{_calc_num("orm-reps", "Reps completed with good form", "reps", "reps", None, "e.g. 8", "numeric", hint="Use a hard set of 1 to 12 reps. 3 to 8 reps gives the most reliable estimate.")}""",
 about="""<h2>What is a one-rep max?</h2>
<p>Your <b>one-rep max (1RM)</b> is the heaviest weight you can lift once with good technique. Coaches use it to set training weights as a percentage, for example 3 sets of 5 at 80% of 1RM.</p>
<p>Testing a true 1RM is tiring and carries more risk, especially for beginners. Estimating it from a harder set of several reps is safer and close enough for planning.</p>
<h2>How the calculator works</h2>
<p>We use two of the most common formulas and show the average:</p>
<ul><li><b>Epley:</b> 1RM = weight × (1 + reps ÷ 30)</li>
<li><b>Brzycki:</b> 1RM = weight × 36 ÷ (37 − reps)</li></ul>
<p>Both are most accurate when the set is close to failure and between about 2 and 10 reps. With high reps the estimates spread out, because muscular endurance varies a lot from person to person.</p>
<h2>Using percentages in your training</h2>
<table><thead><tr><th>Goal</th><th>Typical intensity</th><th>Reps per set</th></tr></thead><tbody>
<tr><td>Maximal strength</td><td>80–95% of 1RM</td><td>1–6</td></tr>
<tr><td>Muscle growth</td><td>60–85% of 1RM</td><td>6–15</td></tr>
<tr><td>Technique and warm-ups</td><td>40–60% of 1RM</td><td>5–10</td></tr></tbody></table>
<p>Recalculate every 4–6 weeks using a recent hard set, so your training weights keep up with your progress.</p>
<h2>Safety tips</h2>
<ul><li>Warm up with lighter sets first.</li><li>Use safety bars or a spotter for bench press and squats.</li><li>Stop a set when your form breaks down.</li></ul>""",
 faq=[("How accurate is a one rep max calculator?", "For sets of about 2 to 10 reps taken close to failure, estimates are usually within a few kilograms of a tested max. They are less accurate for very high-rep sets."),
      ("Which formula is best for 1RM?", "Epley and Brzycki give similar results at low reps. We average them. No formula is perfect for everyone."),
      ("Should beginners test their 1RM?", "Usually not. Beginners improve quickly and benefit more from learning technique. An estimate from a set of 5 to 8 reps is safer."),
      ("Does this work for deadlift and squat?", "Yes. It works for most big barbell and dumbbell lifts, as long as the set was hard and done with good form."),
      ("What percentage of my max should I train at?", "Muscle growth usually works well at 60 to 85% of your max for 6 to 15 reps. Strength training often uses 80 to 95% for 1 to 6 reps.")],
 sources=[("ACSM position stand: progression models in resistance training for healthy adults","https://pubmed.ncbi.nlm.nih.gov/19204579/","American College of Sports Medicine, 2009")],
 posts=["how-to-bench-press-safely","how-to-squat-properly","beginner-gym-workout-plan-first-3-months","how-many-sets-and-reps-to-build-muscle","progressive-overload-explained","powerlifting-in-nepal-getting-started","leg-day-for-beginners"]),

dict(slug="body-fat-calculator", short="Body fat", card="Body fat % with a tape measure",
 title="Body Fat Calculator (US Navy Method) with a Tape",
 desc="Free body fat calculator using the US Navy tape method. Estimate your body fat percentage from height, neck, waist and hip measurements.",
 h1="Body Fat <em>Calculator</em>",
 lead="Estimate your body fat percentage with just a tape measure, using the US Navy method, and see which range you fall into.",
 form=lambda: f"""{_tsex("bodyfat")}
{_calc_height("bodyfat")}
{_tlen("bodyfat", "neck", "Neck", "38", "15")}
{_tlen("bodyfat", "waist", "Waist", "85", "33")}
{_tlen("bodyfat", "hip", "Hips", "100", "39", ' data-female style="display:none"')}
{_calc_num("bodyfat-weight", '<span data-metric>Weight (kg)</span><span data-imperial>Weight (lb)</span>', "weight", "kg", "lb", "e.g. 70", "decimal", opt=True, hint="Add your weight to see fat mass and lean mass.")}""",
 about="""<h2>How to measure</h2>
<p>Use a soft tape measure, keep it snug but not tight, and measure in the morning before eating. Take each measurement twice and use the average.</p>
<ul><li><b>Neck:</b> just below the Adam's apple, with the tape sloping slightly down at the front.</li>
<li><b>Waist (men):</b> horizontally at the level of the belly button, relaxed, after breathing out.</li>
<li><b>Waist (women):</b> at the narrowest point of the waist.</li>
<li><b>Hips (women):</b> around the widest part of the buttocks.</li></ul>
<h2>How the calculator works</h2>
<p>The US Navy method estimates body fat from body circumferences and height. It was developed by Hodgdon and Beckett for the US Navy and is still used by the US military for body composition checks. Like all field methods, it is an estimate: it can be several percentage points away from lab methods such as DEXA, especially for very lean or very muscular people.</p>
<h2>Body fat ranges</h2>
<table><thead><tr><th>Category</th><th>Men</th><th>Women</th></tr></thead><tbody>
<tr><td>Essential fat</td><td>2–5%</td><td>10–13%</td></tr>
<tr><td>Athletes</td><td>6–13%</td><td>14–20%</td></tr>
<tr><td>Fitness</td><td>14–17%</td><td>21–24%</td></tr>
<tr><td>Average</td><td>18–24%</td><td>25–31%</td></tr>
<tr><td>Above average</td><td>25% and over</td><td>32% and over</td></tr></tbody></table>
<p>Ranges from the American Council on Exercise. Women naturally carry more essential fat than men.</p>
<h2>Use it to track progress</h2>
<p>The real value is in the trend. Measure once a month in the same way. If your body fat estimate and waist are going down while your strength goes up, you are losing fat and keeping muscle.</p>""",
 faq=[("How accurate is the US Navy body fat method?", "It is usually within a few percentage points of lab methods for most people, but can be less accurate for very lean, very muscular or very large bodies. It is best for tracking change over time."),
      ("What is a healthy body fat percentage?", "For many adults, roughly 14 to 24% for men and 21 to 31% for women falls in the fitness to average ranges. What is healthy also depends on age, waist size and other health markers."),
      ("Why does the calculator need my neck size?", "Neck size helps the formula separate body size from fat stored around the waist. A thicker neck usually reflects more muscle and a larger frame."),
      ("Is BMI or body fat better?", "Body fat percentage tells you more about body composition, because BMI cannot tell muscle from fat. Using both, plus waist size, gives a fuller picture."),
      ("How often should I measure body fat?", "Once every 4 weeks is enough. Body fat changes slowly, and daily or weekly readings mostly show measurement noise.")],
 sources=[("Prediction of percent body fat for US Navy men and women from body circumferences and height","https://apps.dtic.mil/sti/pdfs/ADA143890.pdf","Hodgdon and Beckett, Naval Health Research Center, 1984"),
          ("WHO fact sheet: obesity and overweight","https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight","World Health Organization")],
 posts=["body-recomposition-lose-fat-build-muscle","how-to-lose-belly-fat","why-am-i-not-losing-weight","fat-loss-vs-weight-loss","weight-loss-diet-plan-nepali-food","calorie-deficit-explained"]),

dict(slug="calorie-deficit-calculator", short="Calorie deficit", card="Calories to eat to lose weight",
 title="Calorie Deficit Calculator: Calories to Lose Weight",
 desc="Free calorie deficit calculator. Find your maintenance calories and how much to eat for mild, moderate or faster weight loss, with weekly estimates.",
 h1="Calorie Deficit <em>Calculator</em>",
 lead="Work out your maintenance calories, then see how much to eat each day for steady, sustainable fat loss, with an estimate of how fast you may lose weight.",
 form=lambda: f"""{_calc_age("deficit")}
{_tsex("deficit", legend="Sex used in the equation")}
{_calc_weight("deficit")}
{_calc_height("deficit")}
{_tsel("deficit", "activity", "Activity level", _ACTS)}
{_calc_preg("deficit", "calorie targets")}""",
 about="""<h2>What is a calorie deficit?</h2>
<p>A calorie deficit means eating less energy than your body uses. Your body makes up the difference from stored energy, mainly body fat. It is the basic principle behind every diet that works, whether it is called low-carb, intermittent fasting or clean eating.</p>
<h2>How the calculator works</h2>
<ol><li>We estimate your resting energy use (BMR) with the <b>Mifflin-St Jeor equation</b>, one of the most accurate equations for healthy adults.</li>
<li>We multiply it by an activity factor to estimate your <b>maintenance calories</b> (TDEE).</li>
<li>We subtract 250, 500 or 750 kcal a day for a mild, moderate or faster plan, never going below 1,200 kcal for women or 1,500 kcal for men.</li>
<li>We estimate weekly loss using roughly 7,700 kcal per kg of body fat. Real loss is usually a little slower than this simple rule, because your body adapts as you lose weight.</li></ol>
<h2>Which deficit should you choose?</h2>
<ul><li><b>Mild (−250 kcal):</b> easiest to stick to, good if you are already fairly lean or want to build muscle at the same time.</li>
<li><b>Moderate (−500 kcal):</b> the most common choice; steady loss without extreme hunger for most people.</li>
<li><b>Faster (−750 kcal):</b> harder to sustain and more likely to cost muscle. Keep protein high and lift weights if you choose it.</li></ul>
<p>A loss of about 0.5–1% of body weight a week is a sensible target for most people.</p>
<h2>Make the deficit work</h2>
<ul><li><b>Keep protein high:</b> about 1.6 g per kg of body weight helps protect muscle. Try our <a href="../protein-calculator/">protein calculator</a>.</li>
<li><b>Strength train 2–3 times a week</b> so the weight you lose is mostly fat.</li>
<li><b>Walk more.</b> Daily steps add up and are easy to recover from.</li>
<li><b>Track the trend.</b> Weigh yourself a few mornings a week and compare weekly averages. If nothing changes in 2–3 weeks, reduce by another 100–200 kcal or add more steps.</li></ul>""",
 faq=[("How big should my calorie deficit be?", "For most people, 300 to 500 kcal a day below maintenance is a good start. It usually gives steady loss of about 0.25 to 0.5 kg a week without extreme hunger."),
      ("Is a 1,000 calorie deficit safe?", "It is aggressive for many people and harder to sustain. It may be suitable for some people with a lot of weight to lose, ideally with medical advice. Smaller deficits are easier to keep."),
      ("Why am I not losing weight in a calorie deficit?", "Usually the deficit is smaller than you think: portions, cooking oil, drinks and weekends add up. Water retention can also hide fat loss for a week or two. Track honestly and check weekly averages."),
      ("Do I need to count calories forever?", "No. Many people count for a few weeks to learn portion sizes, then switch to simple habits such as the plate method."),
      ("Can I build muscle in a calorie deficit?", "Beginners and people returning to training often can, with high protein and strength training. This is called body recomposition.")],
 sources=[("A new predictive equation for resting energy expenditure in healthy individuals","https://pubmed.ncbi.nlm.nih.gov/2305711/","Mifflin et al., 1990"),
          ("WHO fact sheet: obesity and overweight","https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight","World Health Organization"),
          ("Effects of aerobic and/or resistance training on body mass and fat mass in overweight or obese adults","https://pubmed.ncbi.nlm.nih.gov/23019316/","Willis et al., Journal of Applied Physiology, 2012")],
 posts=["why-am-i-not-losing-weight","weight-loss-diet-plan-nepali-food","how-to-lose-belly-fat","calorie-deficit-explained","how-many-calories-do-i-need","weight-loss-plateau","body-recomposition-lose-fat-build-muscle","walking-for-weight-loss-steps"]),

dict(slug="water-intake-calculator", short="Water intake", card="How much water to drink a day",
 title="Water Intake Calculator: How Much Water to Drink a Day",
 desc="Free water intake calculator. Find how much water to drink each day, with extra for exercise and hot weather, based on European health guidance.",
 h1="Water Intake <em>Calculator</em>",
 lead="Estimate how much water to drink each day, with extra for your workouts and for hot weather.",
 form=lambda: f"""{_tsex("water", opts=(("male","Male"),("female","Female"),("unspecified","Prefer not to say")), legend="Sex", hint="Average needs differ slightly. Choose “Prefer not to say” to use the midpoint.")}
{_calc_num("water-ex", "Minutes of exercise today", "exercise", "min", None, "e.g. 45", "numeric")}
{_tsel("water", "climate", "Weather", [("mild","Mild or cool"),("hot","Hot or humid")])}""",
 about="""<h2>How much water do you need?</h2>
<p>The European Food Safety Authority (EFSA) sets adequate total water intakes of about <b>2.0 litres a day for women</b> and <b>2.5 litres a day for men</b>. That includes water from food, which usually provides around 20–30% of the total. The rest comes from drinks: water, tea, milk and other beverages all count.</p>
<h2>How the calculator works</h2>
<ul><li>Baseline from drinks: about 80% of the EFSA total (1.6 L for women, 2.0 L for men).</li>
<li>Exercise: about 0.6 L extra per hour. Sweat losses vary widely, often 0.5–1.5 L an hour or more in the heat.</li>
<li>Hot weather: about 0.5 L extra.</li></ul>
<p>These are averages. Your needs depend on body size, sweat rate, diet and health.</p>
<h2>Simple ways to stay hydrated</h2>
<ul><li><b>Check your urine:</b> pale yellow usually means you are drinking enough.</li>
<li><b>Drink with every meal</b> and keep a bottle with you.</li>
<li><b>Before training:</b> a glass of water 1–2 hours before.</li>
<li><b>During long or hot sessions:</b> sip regularly, and consider electrolytes if you sweat heavily for over an hour.</li></ul>
<h2>Can you drink too much?</h2>
<p>Yes. Drinking very large amounts quickly, especially during long endurance events, can dilute blood sodium (hyponatraemia), which is dangerous. Drink to thirst and use the guide above rather than forcing litres. People with heart or kidney conditions should follow their doctor's fluid advice.</p>""",
 faq=[("How much water should I drink a day?", "Most adults need about 2 to 2.5 litres of total water a day from food and drinks, which usually means around 1.6 to 2 litres from drinks, plus more when exercising or in hot weather."),
      ("Does tea or coffee count towards water intake?", "Yes. Tea, coffee and milk all count. Caffeine has a mild effect on urine, but moderate amounts still hydrate you overall."),
      ("How much water should I drink when working out?", "Drink a glass before training and sip during it. Around 0.5 to 1 litre per hour of exercise is common, more in hot weather."),
      ("Is 3 litres of water a day too much?", "For many active people, especially in hot weather, 3 litres is fine. Problems usually only happen with very large amounts in a short time."),
      ("Do I need more water to build muscle?", "Not specifically, but active people and those eating more protein usually feel better drinking a little more through the day.")],
 sources=[("EFSA scientific opinion on dietary reference values for water","https://doi.org/10.2903/j.efsa.2010.1459","European Food Safety Authority, 2010"),
          ("Heat exhaustion and heatstroke","https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/","NHS")],
 posts=["how-much-water-should-you-drink","exercising-in-hot-weather","best-time-to-go-to-the-gym","muscle-soreness-after-gym"]),

dict(slug="ideal-weight-calculator", short="Ideal weight", card="Healthy weight range for your height",
 title="Ideal Weight Calculator: Healthy Weight for Your Height",
 desc="Free ideal weight calculator. See the healthy weight range for your height, including South Asian BMI cut-offs, plus the Robinson, Miller and Devine formulas.",
 h1="Ideal Weight <em>Calculator</em>",
 lead="See the healthy weight range for your height, plus the classic ideal-weight formulas, in kg or lb.",
 form=lambda: f"""{_tsex("ideal")}
{_calc_height("ideal")}""",
 about="""<h2>What is an ideal weight?</h2>
<p>There is no single perfect weight for any height. Instead, health bodies use a <b>healthy weight range</b>, based on a body mass index (BMI) of 18.5 to 24.9 for adults. Within that range, the right weight for you depends on your muscle, frame size, age and health.</p>
<h2>South Asian cut-offs</h2>
<p>People of South Asian background, including Nepali, Indian and Bangladeshi people, tend to develop type 2 diabetes and heart disease at a lower BMI. That is why the World Health Organization expert consultation and some national guidelines use <b>lower action points, such as a BMI of 23</b>. The calculator shows this range too.</p>
<h2>The classic formulas</h2>
<p>Older formulas such as Devine (1974), Robinson (1983), Miller (1983) and Hamwi (1964) were developed mainly to calculate medicine doses. They give a single number from height and sex, and differ from each other by several kilograms. We show them for comparison, but the BMI range is a better guide.</p>
<h2>Weight is only part of the story</h2>
<ul><li><b>Waist size:</b> fat around the middle carries more health risk. Many guidelines suggest keeping your waist under half your height.</li>
<li><b>Muscle:</b> people who lift weights can be heavier than the formulas suggest and still be lean and healthy. Our <a href="../body-fat-calculator/">body fat calculator</a> gives a better picture.</li>
<li><b>Habits matter more than the number:</b> activity, sleep, food quality and strength all improve health at any weight.</li></ul>""",
 faq=[("What is the ideal weight for my height?", "For adults, a healthy weight is usually the range that gives a BMI of 18.5 to 24.9. For example, at 170 cm that is about 53 to 72 kg. For South Asian adults, staying under a BMI of 23 (about 66 kg at 170 cm) is often advised."),
      ("Which ideal weight formula is most accurate?", "None is precise for everyone. The formulas were designed for medicine dosing and give single numbers. The BMI-based healthy range is more useful for most people."),
      ("Can I be healthy above my ideal weight?", "Yes, especially if you carry a lot of muscle. Waist size, fitness, blood pressure, blood sugar and cholesterol tell you more than weight alone."),
      ("Is the ideal weight different for women?", "The BMI range is the same for adult men and women, but the classic formulas give women slightly lower numbers because they were based on average body size differences."),
      ("Does this work for teenagers?", "No. Children and teenagers are still growing and should be assessed with growth charts for their age and sex.")],
 sources=[("Appropriate body-mass index for Asian populations and its implications for policy and intervention strategies","https://pubmed.ncbi.nlm.nih.gov/14726171/","WHO Expert Consultation, The Lancet, 2004"),
          ("WHO fact sheet: obesity and overweight","https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight","World Health Organization")],
 posts=["weight-loss-diet-plan-nepali-food","how-to-gain-weight-fast-for-skinny-people","why-am-i-not-losing-weight","fat-loss-vs-weight-loss","how-to-lose-belly-fat"]),
]

_TBY = {t["slug"]: t for t in TOOLS}
_K = {'protein-calculator':'protein','one-rep-max-calculator':'orm','calorie-deficit-calculator':'deficit','body-fat-calculator':'bodyfat','water-intake-calculator':'water','ideal-weight-calculator':'ideal'}
_POSTBY = {p["slug"]: p for p in POSTS}

def build_tools():
    for t in TOOLS:
        d = 2; path = f"calculators/{t['slug']}/"
        cr = [("Home", ""), ("Fitness Calculators", "calculators/"), (t["short"] + " calculator", path)]
        name = re.sub(r"<[^>]+>", "", t["h1"])
        j = ld({"@context": "https://schema.org", "@graph": [crumbs(cr),
                {"@type": "WebApplication", "name": name, "url": BASE + "/" + path, "description": t["desc"], "applicationCategory": "HealthApplication",
                 "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                 "publisher": {"@id": BASE + "/#org"}, "inLanguage": "en"},
                faq_ld(t["faq"])]})
        extra = '<link rel="stylesheet" href="../../assets/calc.css">\n' + j
        posts = [_POSTBY[s] for s in t["posts"] if s in _LIVE][:4]
        reads = (f'<section class="csec"><div class="wrap"><h2 class="h2c">Read next</h2><div class="bgrid">{"".join(_postcard(x, "../../blog/") for x in posts)}</div></div></section>') if posts else ""
        others = "".join(f'<a href="../{o["slug"]}/"><b>{e(o["short"])} calculator</b><span>{e(o["card"])}</span></a>' for o in TOOLS if o is not t)
        others += '<a href="../"><b>BMI, BMR, TDEE and macros</b><span>All our core calculators</span></a>'
        toolbar = """<div class="toolbar"><div class="seg" role="radiogroup" aria-label="Units"><label><input type="radio" name="units" value="metric" checked><span>Metric (kg, cm)</span></label><label><input type="radio" name="units" value="imperial"><span>Imperial (lb, in)</span></label></div></div>"""
        body = f"""<body class="calcs" data-root="../../" data-units="metric">
{nav(d, "calculators")}
<main>
<section class="chero"><div class="wrap">
{crumb_html(cr, d)}
<span class="eyebrow">Free tool from Apex Fitness Centre</span>
<h1>{t['h1']}</h1>
<p class="lead">{e(t['lead'])}</p>
{toolbar}
</div></section>
<div class="wrap cwrap">
<section class="cx-card" aria-labelledby="{t['slug']}-h"><h2 id="{t['slug']}-h" class="sr-only">{e(name)}</h2>
<div class="cgrid2"><form novalidate data-tool="{_K[t['slug']]}" aria-labelledby="{t['slug']}-h">
{t['form']()}
{_calc_actions()}
</form>
<div>{_calc_res(_K[t['slug']])}</div></div>
</section>
</div>
<section class="csec"><div class="wrap narrow"><div class="abody">
{t['about']}
<h2>Frequently asked questions</h2>
{faq_html(t['faq'])}
{_src(t['sources'])}
<p class="fine" style="text-align:left">Estimates only, not medical advice. Talk to a doctor or registered dietitian if you are pregnant, under 18, or have a medical condition.</p>
</div></div></section>
{('<div class="wrap narrow">' + newsletter_box("tool") + '</div>') if newsletter_box("tool") else ""}
{reads}
<section class="csec"><div class="wrap"><h2 class="h2c">More free calculators</h2><div class="links">{others}</div></div></section>
</main>
{footer(d)}{drawer()}{tail(d).replace("</body>", '<script src="../../assets/tools.js"></script>\\n</body>')}"""
        pages[path] = head(t["title"], t["desc"], path, d, extra=extra) + body
        sitemap.append((path, "0.8"))
    # hub: link every tool from /calculators/
    cards = "".join(f'<a href="{x["slug"]}/"><b>{e(x["short"])} calculator</b><span>{e(x["card"])}</span></a>' for x in TOOLS)
    hub = f'<section class="csec"><div class="wrap"><h2 class="h2c">More free calculators</h2><div class="links">{cards}</div></div></section>'
    pages["calculators/"] = pages["calculators/"].replace('<section class="csec"><div class="wrap">\n<h2 class="h2c">Keep going with Apex</h2>', hub + '\n<section class="csec"><div class="wrap">\n<h2 class="h2c">Keep going with Apex</h2>', 1)
    # blog posts: a short "try the calculator" box before the author box
    RULES = [("protein-calculator", ("protein", "whey", "egg", "breakfast", "vegetarian", "muscle-gain", "glp-1", "build-muscle")),
             ("calorie-deficit-calculator", ("calorie", "weight-loss", "losing-weight", "belly-fat", "lose-face", "plateau", "fat-loss", "intermittent", "walking")),
             ("one-rep-max-calculator", ("bench", "squat", "deadlift", "powerlifting", "sets-and-reps", "progressive-overload", "leg-day", "strength-training")),
             ("body-fat-calculator", ("recomposition", "body-fat")),
             ("water-intake-calculator", ("water", "hot-weather")),
             ("ideal-weight-calculator", ("gain-weight", "skinny"))]
    for p in POSTS:
        slug = p["slug"]
        tool = next((t for t, keys in RULES if any(k in slug for k in keys)), None)
        if not tool: continue
        T = _TBY[tool]
        box = (f'<aside class="pask"><p><b>Free tool: {e(T["short"])} calculator.</b> {e(T["card"])}, in seconds.</p>'
               f'<a class="btn" href="../../calculators/{tool}/">Open the calculator</a></aside>\n')
        k = f"blog/{slug}/"
        if k in pages and '<aside class="author">' in pages[k]:
            pages[k] = pages[k].replace('<aside class="author">', box + '<aside class="author">', 1)

build_tools()
