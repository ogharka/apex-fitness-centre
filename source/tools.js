/* Single-purpose calculator pages (/calculators/<tool>/). No network, no storage, no tracking. */
(function () {
  'use strict';
  var body = document.body;
  var units = 'metric';
  var KG_PER_LB = 0.45359237, CM_PER_IN = 2.54;

  function $(s, r) { return (r || document).querySelector(s); }
  function $all(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
  function fmt(n, d) { return Number(n).toLocaleString('en-US', { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }); }
  function num(form, name) {
    var f = form.querySelector('[data-field="' + name + '"]');
    if (!f) return NaN;
    var v = String(f.value).replace(/,/g, '').trim();
    return v === '' ? NaN : Number(v);
  }
  function pick(form, name) { var f = form.querySelector('[data-field="' + name + '"]:checked') || form.querySelector('select[data-field="' + name + '"]'); return f ? f.value : ''; }
  function setErr(form, name, msg) {
    var p = form.querySelector('[data-err="' + name + '"]');
    var f = form.querySelector('[data-field="' + name + '"]');
    if (p) { p.textContent = msg || ''; p.hidden = !msg; }
    if (f) f.setAttribute('aria-invalid', msg ? 'true' : 'false');
    return !msg;
  }
  function clearErrs(form) { $all('[data-err]', form).forEach(function (p) { p.hidden = true; p.textContent = ''; }); $all('[aria-invalid]', form).forEach(function (f) { f.setAttribute('aria-invalid', 'false'); }); }
  function range(form, name, lo, hi, label) {
    var v = num(form, name);
    if (isNaN(v)) { setErr(form, name, 'Please enter ' + label + '.'); return NaN; }
    if (v < lo || v > hi) { setErr(form, name, 'Please enter ' + label + ' between ' + lo + ' and ' + hi + '.'); return NaN; }
    return v;
  }
  function weightKg(form) {
    return units === 'metric' ? range(form, 'weight', 25, 300, 'your weight in kg') : range(form, 'weight', 55, 660, 'your weight in lb') * KG_PER_LB;
  }
  function liftKg(form) {
    return units === 'metric' ? range(form, 'lift', 1, 500, 'the weight lifted in kg') : range(form, 'lift', 2, 1100, 'the weight lifted in lb') * KG_PER_LB;
  }
  function lenCm(form, name, lo, hi, label) {
    return units === 'metric' ? range(form, name, lo, hi, label + ' in cm') : range(form, name, Math.round(lo / CM_PER_IN), Math.round(hi / CM_PER_IN), label + ' in inches') * CM_PER_IN;
  }
  function heightCm(form) {
    if (units === 'metric') return range(form, 'height', 120, 230, 'your height in cm');
    var ft = num(form, 'feet'), inch = num(form, 'inches');
    if (isNaN(inch)) inch = 0;
    if (isNaN(ft) || ft < 4 || ft > 7 || inch < 0 || inch >= 12) { setErr(form, 'height', 'Please enter your height in feet (4 to 7) and inches (0 to 11).'); return NaN; }
    return (ft * 12 + inch) * CM_PER_IN;
  }
  function showW(kg, d) { return units === 'metric' ? fmt(kg, d === undefined ? 1 : d) + ' kg' : fmt(kg / KG_PER_LB, d === undefined ? 0 : d) + ' lb'; }
  function adultCheck(form) {
    var a = range(form, 'age', 18, 100, 'an age from 18 to 100');
    var preg = form.querySelector('[data-field="pregnant"]');
    if (preg && preg.checked) return 'preg';
    return a;
  }
  function out(form) { var r = $('#' + form.getAttribute('data-tool') + '-result'); while (r.firstChild) r.removeChild(r.firstChild); return r; }
  function big(r, value, unit, label) {
    r.appendChild(el('p', 'rlabel', label));
    var b = el('p', 'cx-big', value); if (unit) { b.appendChild(el('small', null, unit)); } r.appendChild(b);
  }
  function para(r, text, cls) { r.appendChild(el('p', cls || null, text)); }
  function table(r, head, rows) {
    var t = el('table', 'tt'); var tr = el('tr'); head.forEach(function (h) { tr.appendChild(el('th', null, h)); }); var th = el('thead'); th.appendChild(tr); t.appendChild(th);
    var tb = el('tbody'); rows.forEach(function (row) { var x = el('tr'); row.forEach(function (c) { x.appendChild(el('td', null, c)); }); tb.appendChild(x); }); t.appendChild(tb); r.appendChild(t);
  }
  function stop(r, msg) { para(r, msg); }

  var MIFFLIN = function (sex, kg, cm, age) { return 10 * kg + 6.25 * cm - 5 * age + (sex === 'male' ? 5 : -161); };
  var ACT = { sedentary: 1.2, light: 1.375, moderate: 1.55, very: 1.725, extra: 1.9 };

  var TOOLS = {
    protein: function (f) {
      var kg = weightKg(f); var goal = pick(f, 'goal');
      if (!goal) setErr(f, 'goal', 'Please choose a goal.');
      if (isNaN(kg) || !goal) return;
      var G = { general: [0.8, 0.8, 'Healthy adult who does little exercise'], active: [1.2, 1.6, 'Regular exercise or sport'], muscle: [1.6, 2.2, 'Building muscle with strength training'], cut: [1.8, 2.2, 'Losing fat while strength training'], older: [1.0, 1.2, 'Adults over 65 (more if training)'] }[goal];
      var lo = kg * G[0], hi = kg * G[1];
      var r = out(f);
      big(r, lo === hi ? fmt(lo) : fmt(lo) + '–' + fmt(hi), 'g / day', 'Your daily protein target');
      para(r, G[2] + ': ' + (G[0] === G[1] ? G[0] : G[0] + '–' + G[1]) + ' g of protein per kg of body weight a day.');
      var meals = [3, 4].map(function (m) { return m + ' meals: about ' + fmt(lo / m) + (lo === hi ? '' : '–' + fmt(hi / m)) + ' g each'; });
      para(r, 'Split it up. ' + meals.join(' · ') + '.');
      table(r, ['Food', 'Protein (approx.)'], [
        ['2 large eggs', '12 g'], ['1 cup (250 ml) milk', '8 g'], ['1 cup cooked dal or lentils', '18 g'],
        ['100 g cooked chicken breast', '31 g'], ['100 g paneer', '18 g'], ['1 cup cooked chana or rajma', '15 g'], ['1 scoop whey protein', '24 g']
      ]);
      if (goal !== 'general') para(r, 'Have kidney disease or diabetes? Ask your doctor before raising protein.', 'muted');
    },
    orm: function (f) {
      var kg = liftKg(f); var reps = range(f, 'reps', 1, 12, 'reps from 1 to 12');
      if (isNaN(kg) || isNaN(reps)) return;
      var ep = reps === 1 ? kg : kg * (1 + reps / 30);
      var br = reps === 1 ? kg : kg * 36 / (37 - reps);
      var orm = (ep + br) / 2;
      var r = out(f);
      big(r, units === 'metric' ? fmt(orm, 1) : fmt(orm / KG_PER_LB), units === 'metric' ? 'kg' : 'lb', 'Estimated one-rep max');
      para(r, 'Epley formula: ' + showW(ep) + ' · Brzycki formula: ' + showW(br) + '. We show the average.');
      var rows = [[100, '1'], [95, '2'], [90, '3–4'], [85, '5–6'], [80, '7–8'], [75, '9–10'], [70, '11–12'], [65, '13–15'], [60, '16–20'], [50, 'Warm-up']];
      table(r, ['% of 1RM', 'Weight', 'Reps you could do'], rows.map(function (x) { return [x[0] + '%', showW(orm * x[0] / 100), x[1]]; }));
      para(r, 'Estimates are most accurate from sets of 2–10 reps. Test a true 1RM only with good technique and a spotter.', 'muted');
    },
    bodyfat: function (f) {
      var sex = pick(f, 'sex'); if (!sex) setErr(f, 'sex', 'Please choose male or female.');
      var h = heightCm(f), waist = lenCm(f, 'waist', 50, 200, 'your waist'), neck = lenCm(f, 'neck', 20, 70, 'your neck');
      var hip = sex === 'female' ? lenCm(f, 'hip', 60, 200, 'your hips') : 0;
      if (!sex || isNaN(h) || isNaN(waist) || isNaN(neck) || isNaN(hip)) return;
      var bf;
      if (sex === 'male') {
        if (waist - neck <= 0) { setErr(f, 'waist', 'Waist must be bigger than neck.'); return; }
        bf = 495 / (1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(h)) - 450;
      } else {
        if (waist + hip - neck <= 0) { setErr(f, 'waist', 'Please check your measurements.'); return; }
        bf = 495 / (1.29579 - 0.35004 * Math.log10(waist + hip - neck) + 0.22100 * Math.log10(h)) - 450;
      }
      var r = out(f);
      if (bf < 2 || bf > 60) { stop(r, 'These measurements give a result outside what the formula can estimate. Please measure again with a soft tape, following the steps below.'); return; }
      big(r, fmt(bf, 1), '% body fat', 'Estimated body fat (US Navy method)');
      var M = [[6, 'Essential fat'], [14, 'Athletic'], [18, 'Fit'], [25, 'Average'], [999, 'Above average']];
      var F = [[14, 'Essential fat'], [21, 'Athletic'], [25, 'Fit'], [32, 'Average'], [999, 'Above average']];
      var band = (sex === 'male' ? M : F).filter(function (x) { return bf < x[0]; })[0][1];
      para(r, 'Category: ' + band + ' (American Council on Exercise ranges).');
      var kg = num(f, 'weight');
      if (!isNaN(kg) && kg > 0) {
        var wkg = units === 'metric' ? kg : kg * KG_PER_LB;
        para(r, 'Fat mass about ' + showW(wkg * bf / 100) + ' · lean mass about ' + showW(wkg * (1 - bf / 100)) + '.');
      }
      para(r, 'Tape methods are usually within a few percentage points of lab methods. Use the same method each month to track change.', 'muted');
    },
    deficit: function (f) {
      var age = adultCheck(f); var sex = pick(f, 'sex'); if (!sex) setErr(f, 'sex', 'Please choose male or female.');
      var kg = weightKg(f), cm = heightCm(f), act = pick(f, 'activity');
      if (!act) setErr(f, 'activity', 'Please choose your activity level.');
      var r;
      if (age === 'preg') { r = out(f); stop(r, 'We do not give calorie targets during pregnancy or breastfeeding. Please ask your doctor or midwife.'); return; }
      if (isNaN(age) || !sex || isNaN(kg) || isNaN(cm) || !act) return;
      var tdee = MIFFLIN(sex, kg, cm, age) * ACT[act];
      var floor = sex === 'male' ? 1500 : 1200;
      r = out(f);
      big(r, fmt(Math.round(tdee / 10) * 10), 'kcal / day', 'Maintenance calories');
      var rows = [['Mild', 250], ['Moderate', 500], ['Faster', 750]].map(function (x) {
        var t = Math.max(floor, tdee - x[1]); var d = tdee - t; var wk = d * 7 / 7700;
        return [x[0], fmt(Math.round(t / 10) * 10) + ' kcal', d <= 0 ? '—' : '≈ ' + (units === 'metric' ? fmt(wk, 2) + ' kg' : fmt(wk / KG_PER_LB, 1) + ' lb') + ' / week'];
      });
      table(r, ['Plan', 'Eat about', 'Expected loss'], rows);
      if (tdee - 750 < floor) para(r, 'Some targets were capped at ' + floor + ' kcal, a common minimum without medical supervision.', 'muted');
      para(r, 'Most people do best with the mild or moderate plan, high protein and strength training 2–3 times a week. Real loss varies: check your weekly average weight for 2–3 weeks, then adjust.');
      para(r, 'Estimate only. If you have a medical condition or a history of eating disorders, please get advice from a doctor or dietitian first.', 'muted');
    },
    water: function (f) {
      var sex = pick(f, 'sex'); if (!sex) setErr(f, 'sex', 'Please choose an option.');
      var mins = range(f, 'exercise', 0, 300, 'minutes of exercise from 0 to 300');
      var hot = pick(f, 'climate');
      if (!sex || isNaN(mins)) return;
      var total = sex === 'male' ? 2.5 : sex === 'female' ? 2.0 : 2.25;
      var drinks = total * 0.8;
      var ex = mins / 60 * 0.6;
      var heat = hot === 'hot' ? 0.5 : 0;
      var tot = drinks + ex + heat;
      var r = out(f);
      big(r, fmt(tot, 1), 'litres / day', 'Water to drink (approx.)');
      table(r, ['Part', 'Litres'], [
        ['Baseline from drinks (about 80% of EFSA total water)', fmt(drinks, 1)],
        ['Extra for ' + mins + ' min of exercise', fmt(ex, 1)],
        ['Extra for hot weather', fmt(heat, 1)]
      ]);
      para(r, 'About ' + fmt(tot * 4) + ' glasses of 250 ml. The rest of your water comes from food like dal, rice, fruit and vegetables.');
      para(r, 'Pale yellow urine is a simple sign you are drinking enough. People with heart or kidney conditions may need to limit fluids: follow your doctor.', 'muted');
    },
    ideal: function (f) {
      var sex = pick(f, 'sex'); if (!sex) setErr(f, 'sex', 'Please choose male or female.');
      var cm = heightCm(f);
      if (!sex || isNaN(cm)) return;
      var inch = cm / CM_PER_IN, over = Math.max(0, inch - 60), m = sex === 'male';
      var F = [
        ['Robinson (1983)', m ? 52 + 1.9 * over : 49 + 1.7 * over],
        ['Miller (1983)', m ? 56.2 + 1.41 * over : 53.1 + 1.36 * over],
        ['Devine (1974)', m ? 50 + 2.3 * over : 45.5 + 2.3 * over],
        ['Hamwi (1964)', m ? 48 + 2.7 * over : 45.5 + 2.2 * over]
      ];
      var hm = cm / 100, lo = 18.5 * hm * hm, hi = 24.9 * hm * hm, slo = 18.5 * hm * hm, shi = 22.9 * hm * hm;
      var r = out(f);
      big(r, units === 'metric' ? fmt(lo) + '–' + fmt(hi) : fmt(lo / KG_PER_LB) + '–' + fmt(hi / KG_PER_LB), units === 'metric' ? 'kg' : 'lb', 'Healthy weight range (BMI 18.5–24.9)');
      para(r, 'For people of South Asian background, some health bodies use a lower upper limit (BMI 23), which is ' + showW(slo, 0) + '–' + showW(shi, 0) + ' at your height.');
      table(r, ['Formula', 'Ideal weight'], F.map(function (x) { return [x[0], showW(x[1])]; }));
      if (inch < 60) para(r, 'These formulas were designed for people 5 ft (152 cm) and taller, so they are less reliable at your height.', 'muted');
      para(r, 'These are rough guides from height alone. Muscle, frame size and age all change what is healthy for you.', 'muted');
    }
  };

  function setUnits(u) {
    units = u; body.setAttribute('data-units', u);
    $all('form[data-tool]').forEach(function (f) { clearErrs(f); var r = out(f); r.appendChild(el('p', 'cx-empty', 'Units changed. Enter your numbers again and press Calculate.')); });
  }
  $all('input[name="units"]').forEach(function (x) { x.addEventListener('change', function () { if (x.checked) setUnits(x.value); }); });
  var c = $('input[name="units"]:checked'); if (c) units = c.value; body.setAttribute('data-units', units);

  $all('form[data-tool]').forEach(function (f) {
    f.addEventListener('submit', function (ev) { ev.preventDefault(); clearErrs(f); TOOLS[f.getAttribute('data-tool')](f); var r = $('#' + f.getAttribute('data-tool') + '-result'); if (r && r.querySelector('.cx-big') && window.innerWidth < 760) r.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    f.addEventListener('reset', function () { clearErrs(f); var r = out(f); r.appendChild(el('p', 'cx-empty', 'Your result will appear here.')); });
    $all('[data-field="sex"]', f).forEach(function (x) { x.addEventListener('change', function () { $all('[data-female]', f).forEach(function (n) { n.style.display = x.value === 'female' ? '' : 'none'; }); }); });
  });
})();
