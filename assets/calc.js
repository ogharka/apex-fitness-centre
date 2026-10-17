/* Fitness Calculators page: wires the forms to ApexCalc (assets/calc-core.js). No network, no storage, no tracking. */
(function () {
  'use strict';
  var C = window.ApexCalc;
  if (!C) return;
  var body = document.body;
  var units = 'metric';

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); if (n.classList) n.classList.remove('stale'); }
  function money(n) { return Number(n).toLocaleString('en-US'); }
  function reduced() { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; }

  // ---------- reading forms ----------
  function field(form, name) { return form.querySelector('[data-field="' + name + '"]'); }
  function val(form, name) { var f = field(form, name); return f ? f.value : ''; }
  function radio(form, name) { var f = form.querySelector('[data-field="' + name + '"]:checked'); return f ? f.value : ''; }
  function checked(form, name) { var f = field(form, name); return !!(f && f.checked); }

  function readRaw(form) {
    return {
      units: units,
      age: val(form, 'age'),
      sex: radio(form, 'sex'),
      weight: val(form, 'weight'),
      height: val(form, 'height'),
      feet: val(form, 'feet'),
      inches: val(form, 'inches'),
      pregnant: checked(form, 'pregnant'),
      activity: val(form, 'activity'),
      manualBmr: val(form, 'manualBmr'),
      calories: val(form, 'calories'),
      proteinPct: val(form, 'proteinPct'),
      carbPct: val(form, 'carbPct'),
      fatPct: val(form, 'fatPct')
    };
  }

  // When an input changes after a result is on screen, say so instead of leaving an out-of-date number looking current.
  function markStale(form) {
    var box = resultBox(form);
    if (!box || box.querySelector('.cx-empty') || box.classList.contains('stale')) return;
    box.classList.add('stale');
    var n = el('div', 'callout stale', 'Your inputs have changed. Press Calculate to refresh this result.');
    n.setAttribute('role', 'status');
    box.insertBefore(n, box.firstChild);
  }

  // ---------- errors ----------
  var ERR_FIELDS = { age: 'age', sex: 'sex', weight: 'weight', height: 'height', activity: 'activity', manualBmr: 'manualBmr', calories: 'calories', proteinPct: 'proteinPct', carbPct: 'carbPct', fatPct: 'fatPct', total: 'total' };

  function clearErrors(form) {
    $all('.err', form).forEach(function (e) { e.hidden = true; e.textContent = ''; });
    $all('[aria-invalid]', form).forEach(function (i) { i.removeAttribute('aria-invalid'); });
  }

  function showErrors(form, errors) {
    var first = null;
    Object.keys(errors).forEach(function (k) {
      var holder = form.querySelector('[data-err="' + k + '"]');
      if (holder) { holder.hidden = false; holder.textContent = errors[k]; }
      var inputs = k === 'height' && units === 'imperial'
        ? [field(form, 'feet'), field(form, 'inches')]
        : k === 'sex' ? $all('[data-field="sex"]', form)
        : k === 'total' ? [field(form, 'proteinPct'), field(form, 'carbPct'), field(form, 'fatPct')]
        : [field(form, k)];
      inputs.forEach(function (i) { if (i) { i.setAttribute('aria-invalid', 'true'); if (!first) first = i; } });
    });
    if (first && first.focus) first.focus();
  }

  // ---------- result helpers ----------
  function resultBox(form) { return $('.res', form.closest('.cx-card')); }

  function addNotes(box, notes) {
    if (!notes || !notes.length) return;
    var ul = el('ul', 'notes');
    notes.forEach(function (n) { ul.appendChild(el('li', '', n)); });
    box.appendChild(ul);
  }

  function addSteps(box, title, steps, extra) {
    var d = el('details');
    d.appendChild(el('summary', '', title));
    var ol = el('ol');
    steps.forEach(function (s) { ol.appendChild(el('li', '', s)); });
    d.appendChild(ol);
    if (extra) d.appendChild(extra);
    box.appendChild(d);
  }

  function callout(box, text) { box.appendChild(el('div', 'callout', text)); box.lastChild.setAttribute('role', 'note'); }

  function revealResult(box) {
    var r = box.getBoundingClientRect();
    // keep the result in view below the sticky header; do nothing if it is already visible
    if (r.top < 80 || r.bottom > window.innerHeight) {
      box.scrollIntoView({ block: r.height > window.innerHeight - 160 ? 'start' : 'nearest', behavior: reduced() ? 'auto' : 'smooth' });
    }
  }

  function empty(box, text) {
    clear(box);
    box.appendChild(el('p', 'cx-empty', text));
  }

  // ---------- BMI ----------
  function renderBmi(form) {
    var box = resultBox(form);
    clearErrors(form);
    var r = C.bmi(readRaw(form));
    if (!r.ok) { empty(box, 'Fill in the highlighted boxes and press Calculate.'); showErrors(form, r.errors); return; }
    clear(box);
    box.appendChild(el('div', 'rlabel', 'Your BMI'));
    var big = el('div', 'cx-big', String(r.display));
    big.appendChild(el('small', '', 'kg/m²'));
    box.appendChild(big);
    if (r.classified) {
      var k = r.categoryKey;
      var cls = k === 'healthy' ? 'b-healthy' : k === 'underweight' ? 'b-under' : k === 'overweight' ? 'b-over' : 'b-obese';
      box.appendChild(el('span', 'badge2 ' + cls, r.category));
      var m = el('div', 'meter'); m.setAttribute('aria-hidden', 'true');
      var pos = Math.max(0, Math.min(1, (r.display - 12) / (40 - 12))) * 100;
      var mk = el('i'); mk.style.left = pos + '%'; m.appendChild(mk); box.appendChild(m);
      var sc = el('div', 'scale'); sc.setAttribute('aria-hidden', 'true');
      [['12', 12], ['18.5', 18.5], ['25', 25], ['30', 30], ['40+', 40]].forEach(function (t) {
        var s = el('span', '', t[0]); s.style.left = ((t[1] - 12) / 28 * 100) + '%'; sc.appendChild(s);
      });
      box.appendChild(sc);
      box.appendChild(el('p', '', 'For your height, a BMI of 18.5 to 24.9 is a weight of about ' + r.healthyRangeText + '.'));
    } else {
      box.appendChild(el('span', 'badge2 b-na', 'No category shown'));
    }
    addNotes(box, r.notes);
    box.appendChild(el('p', 'muted', 'BMI is a rough screening number. It does not measure body fat, and it cannot tell muscle from fat, so a muscular person can have a high BMI while being healthy. It does not diagnose anything.'));
    addSteps(box, 'How this was worked out', r.steps);
    revealResult(box);
  }

  // ---------- BMR ----------
  function renderBmr(form) {
    var box = resultBox(form);
    clearErrors(form);
    var r = C.bmr(readRaw(form));
    if (!r.ok && r.errors) { empty(box, 'Fill in the highlighted boxes and press Calculate.'); showErrors(form, r.errors); return; }
    clear(box);
    if (!r.ok) { box.appendChild(el('div', 'rlabel', 'Not calculated')); callout(box, r.message); return; }
    box.appendChild(el('div', 'rlabel', 'Your estimated BMR'));
    var big = el('div', 'cx-big', r.range ? money(r.lowDisplay) + ' to ' + money(r.highDisplay) : money(r.display));
    big.appendChild(el('small', '', 'kcal/day'));
    box.appendChild(big);
    box.appendChild(el('p', '', r.range
      ? 'This is roughly how many calories your body uses each day just to stay alive at complete rest. With no sex chosen, the midpoint is about ' + money(Math.round(r.value)) + ' kcal.'
      : 'This is roughly how many calories your body uses each day just to stay alive at complete rest, before any movement or exercise.'));
    addNotes(box, r.notes);
    var actions = el('div', 'actions');
    var b = el('button', 'cbtn small ghost', 'Use this in the TDEE calculator');
    b.type = 'button';
    b.addEventListener('click', function () {
      var t = $('#tdee form');
      var f = field(t, 'manualBmr');
      f.value = String(Math.round(r.value));
      var a = field(t, 'age'); if (!a.value) a.value = val(form, 'age');
      toggleBodyDim(t); markStale(t);
      $('#tdee').scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
      setTimeout(function () { field(t, 'activity').focus(); }, 250);
    });
    actions.appendChild(b);
    box.appendChild(actions);
    addSteps(box, 'How this was worked out', r.steps);
    revealResult(box);
  }

  // ---------- TDEE ----------
  function renderTdee(form) {
    var box = resultBox(form);
    clearErrors(form);
    var raw = readRaw(form);
    var r = C.tdee(raw);
    if (!r.ok && r.errors) { empty(box, 'Fill in the highlighted boxes and press Calculate.'); showErrors(form, r.errors); return; }
    clear(box);
    if (!r.ok) { box.appendChild(el('div', 'rlabel', 'Not calculated')); callout(box, r.message); return; }
    box.appendChild(el('div', 'rlabel', 'Estimated daily maintenance calories'));
    var big = el('div', 'cx-big', r.range ? money(r.lowDisplay) + ' to ' + money(r.highDisplay) : money(r.display));
    big.appendChild(el('small', '', 'kcal/day'));
    box.appendChild(big);
    box.appendChild(el('p', '', 'A rough estimate of the calories you burn in a typical day, including your activity level (' + r.activityLabel.split(':')[0].toLowerCase() + ', factor ' + r.factor + '). Eating about this much would tend to keep your weight steady.'));
    addNotes(box, r.notes);

    // table of every activity level using the same BMR
    var rows = C.ACTIVITY, keys = Object.keys(rows);
    var tbl = el('table', 't');
    var cap = el('caption'); cap.className = 'hint'; cap.textContent = 'Same BMR at every activity level'; cap.style.textAlign = 'left';
    tbl.appendChild(cap);
    var hr = el('tr'); ['Activity level', 'Factor', 'kcal/day'].forEach(function (h) { var th = el('th', '', h); th.scope = 'col'; hr.appendChild(th); }); tbl.appendChild(hr);
    keys.forEach(function (k) {
      var rr = C.tdee(Object.assign({}, raw, { activity: k }));
      if (!rr.ok) return;
      var tr = el('tr', k === r.activityKey ? 'cx-on' : '');
      tr.appendChild(el('td', '', rows[k].label.split(':')[0]));
      tr.appendChild(el('td', '', String(rows[k].factor)));
      tr.appendChild(el('td', '', rr.range ? money(rr.lowDisplay) + ' to ' + money(rr.highDisplay) : money(rr.display)));
      tbl.appendChild(tr);
    });
    var actions = el('div', 'actions');
    var b = el('button', 'cbtn small ghost', r.range ? 'Use the midpoint in the macro calculator' : 'Use this in the macro calculator');
    b.type = 'button';
    b.addEventListener('click', function () {
      var m = $('#macros form');
      field(m, 'calories').value = String(Math.round(r.range ? r.value : r.value));
      var a = field(m, 'age'); if (!a.value) a.value = val(form, 'age');
      updateTotal(m); markStale(m);
      $('#macros').scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
      setTimeout(function () { field(m, 'proteinPct').focus(); }, 250);
    });
    actions.appendChild(b);
    box.appendChild(actions);
    var d = el('details');
    d.appendChild(el('summary', '', 'See every activity level'));
    d.appendChild(tbl);
    box.appendChild(d);
    addSteps(box, 'How this was worked out', r.steps);
    box.appendChild(el('p', 'muted', 'This page does not give weight-loss or weight-gain calorie targets. If you want to change your weight, talk to a doctor or registered dietitian who can look at your whole situation.'));
    revealResult(box);
  }

  // ---------- Macros ----------
  function totalOf(form) {
    var p = C.num(val(form, 'proteinPct')), c = C.num(val(form, 'carbPct')), f = C.num(val(form, 'fatPct'));
    var parts = [p, c, f];
    var bad = parts.some(function (x) { return x !== null && isNaN(x); });
    var sum = parts.reduce(function (a, x) { return a + (x && !isNaN(x) ? x : 0); }, 0);
    return { sum: C.round(sum, 4), bad: bad, blank: parts.every(function (x) { return x === null; }) };
  }

  function updateTotal(form) {
    var t = $('[data-total]', form), s = totalOf(form);
    if (!t) return;
    t.className = 'cx-tot';
    if (s.blank) { t.textContent = 'Total: 0% of 100%. Pick a preset or type your percentages.'; return; }
    if (s.bad) { t.textContent = 'Use numbers only for the percentages.'; t.className = 'cx-tot bad'; return; }
    if (s.sum === 100) { t.textContent = 'Total: 100%. Ready to calculate.'; t.className = 'cx-tot good'; return; }
    var diff = C.round(100 - s.sum, 2);
    t.textContent = 'Total: ' + s.sum + '%. ' + (diff > 0 ? 'Add ' + diff + '% more to reach 100%.' : 'Remove ' + Math.abs(diff) + '% to reach 100%.');
    t.className = 'cx-tot bad';
  }

  function renderMacros(form) {
    var box = resultBox(form);
    clearErrors(form);
    var r = C.macros(readRaw(form));
    if (!r.ok && r.errors) { empty(box, 'Fix the highlighted boxes and press Calculate.'); showErrors(form, r.errors); return; }
    clear(box);
    if (!r.ok) { box.appendChild(el('div', 'rlabel', 'Not calculated')); callout(box, r.message); return; }
    box.appendChild(el('div', 'rlabel', 'Your daily macros'));
    var big = el('div', 'cx-big', money(r.calories));
    big.appendChild(el('small', '', 'kcal/day'));
    box.appendChild(big);
    var bar = el('div', 'cx-bar'); bar.setAttribute('aria-hidden', 'true');
    ['protein', 'carbs', 'fat'].forEach(function (k) { var i = el('i'); i.style.width = r.parts[k].pct + '%'; bar.appendChild(i); });
    box.appendChild(bar);
    var grid = el('div', 'mgrid');
    [['protein', 'Protein'], ['carbs', 'Carbohydrate'], ['fat', 'Fat']].forEach(function (d) {
      var p = r.parts[d[0]];
      var c = el('div', 'mcell');
      c.appendChild(el('span', '', d[1]));
      c.appendChild(el('b', '', p.gramsDisplay + ' g'));
      c.appendChild(el('em', '', p.pct + '% = ' + money(p.kcalDisplay) + ' kcal'));
      grid.appendChild(c);
    });
    box.appendChild(grid);
    box.appendChild(el('p', 'muted', 'Grams are worked out with 4 kcal per gram of protein, 4 per gram of carbohydrate and 9 per gram of fat. Food labels round their numbers, so treat the grams as a guide.'));
    addNotes(box, r.notes);
    addSteps(box, 'How this was worked out', r.steps);
    revealResult(box);
  }

  // ---------- units ----------
  function setUnits(u, convert) {
    if (u === units) return;
    var from = units;
    units = u;
    body.setAttribute('data-units', u);
    $all('input[name="units"]').forEach(function (r) { r.checked = r.value === u; });
    if (convert !== false) {
      $all('.cx-card form').forEach(function (form) {
        var w = field(form, 'weight');
        if (w && w.value !== '') {
          var n = C.num(w.value);
          if (n !== null && !isNaN(n) && n > 0) w.value = String(C.round(u === 'imperial' ? C.kgToLb(n) : C.lbToKg(n), 1));
        }
        var h = field(form, 'height'), ft = field(form, 'feet'), inch = field(form, 'inches');
        if (!h || !ft || !inch) return;
        if (u === 'imperial') {
          var cm = C.num(h.value);
          if (cm !== null && !isNaN(cm) && cm > 0) { var s = C.cmToFtIn(cm); ft.value = String(s.ft); inch.value = String(s.inch); }
        } else {
          var f = C.num(ft.value), i = C.num(inch.value);
          if (f !== null && !isNaN(f) && f >= 0) { h.value = String(C.round(C.ftInToCm(f, (i === null || isNaN(i)) ? 0 : i), 1)); }
        }
        clearErrors(form);
      });
    }
    $all('.res').forEach(function (b) { if (!b.querySelector('.cx-empty')) empty(b, 'Units changed. Press Calculate to see your result again.'); });
  }

  // ---------- sharing values between forms (only into empty boxes) ----------
  var SHARED = ['age', 'weight', 'height', 'feet', 'inches'];
  function share(src) {
    var name = src.getAttribute('data-field');
    if (SHARED.indexOf(name) < 0 || src.value === '') return;
    $all('.cx-card form').forEach(function (form) {
      var t = field(form, name);
      if (t && t !== src && (t.value === '' || t.getAttribute('data-auto') === '1')) { t.value = src.value; t.setAttribute('data-auto', '1'); markStale(form); }
    });
    src.removeAttribute('data-auto');
  }
  function shareSex(src) {
    $all('.cx-card form').forEach(function (form) {
      var t = $all('[data-field="sex"]', form);
      if (!t.length || t.indexOf(src) >= 0) return;
      if (!radio(form, 'sex')) { t.forEach(function (r) { if (r.value === src.value) r.checked = true; }); markStale(form); }
    });
  }

  function toggleBodyDim(form) {
    var manual = form.querySelector('[data-field="manualBmr"]');
    var grp = form.querySelector('[data-bodygroup]');
    if (!manual || !grp) return;
    var has = manual.value.trim() !== '';
    grp.style.opacity = has ? '0.45' : '';
    var hint = form.querySelector('[data-manualhint]');
    if (hint) hint.textContent = has ? 'Using your BMR. Sex, weight and height are not needed, so you can leave them empty.' : 'Optional. If you already know your BMR, type it here and skip sex, weight and height.';
  }

  // ---------- wire up ----------
  var renderers = { bmi: renderBmi, bmr: renderBmr, tdee: renderTdee, macros: renderMacros };

  $all('.cx-card form').forEach(function (form) {
    var id = form.closest('.cx-card').id;
    form.addEventListener('submit', function (e) { e.preventDefault(); renderers[id](form); });
    form.addEventListener('reset', function () {
      setTimeout(function () {
        clearErrors(form);
        $all('[data-auto]', form).forEach(function (i) { i.removeAttribute('data-auto'); });
        empty(resultBox(form), 'Your result will appear here.');
        if (id === 'macros') updateTotal(form);
        if (id === 'tdee') toggleBodyDim(form);
      }, 0);
    });
    form.addEventListener('input', function (e) {
      var t = e.target;
      if (t.getAttribute && t.getAttribute('data-field')) { share(t); markStale(form); }
      if (id === 'macros') updateTotal(form);
      if (id === 'tdee') toggleBodyDim(form);
    });
    form.addEventListener('change', function (e) {
      if (e.target.getAttribute && e.target.getAttribute('data-field') === 'sex') { shareSex(e.target); markStale(form); }
      else if (e.target.getAttribute && e.target.getAttribute('data-field')) markStale(form);
    });
  });

  $all('input[name="units"]').forEach(function (r) {
    r.addEventListener('change', function () { if (r.checked) setUnits(r.value); });
  });

  $all('[data-preset]').forEach(function (b) {
    b.addEventListener('click', function () {
      var form = b.closest('form'), p = b.getAttribute('data-preset').split('-');
      field(form, 'proteinPct').value = p[0]; field(form, 'carbPct').value = p[1]; field(form, 'fatPct').value = p[2];
      clearErrors(form); updateTotal(form); markStale(form);
    });
  });

  var m = $('#macros form'); if (m) updateTotal(m);
  var t = $('#tdee form'); if (t) toggleBodyDim(t);
  body.setAttribute('data-units', units);
})();
