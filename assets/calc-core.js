/*
 * Apex Fitness Centre - calculator core.
 * Pure functions, no DOM, no network. Used by the page (assets/calc.js) and by the
 * unit tests (tests/calc-core.test.js). Every result carries a `steps` array so the
 * page can show exactly how the number was worked out.
 *
 * Inputs are "raw" form values (strings or numbers). Nothing here throws on bad input:
 * invalid input returns { ok:false, errors:{ field: message } } or { ok:false, blocked:... }.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.ApexCalc = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ---------- constants (exact definitions) ----------
  var KG_PER_LB = 0.45359237;      // international avoirdupois pound
  var CM_PER_IN = 2.54;            // international inch
  var IN_PER_FT = 12;
  var KCAL_PER_G = { protein: 4, carbs: 4, fat: 9 };

  var LIMITS = {
    age:      { min: 1,   max: 120 },
    weightKg: { min: 10,  max: 400 },
    heightCm: { min: 50,  max: 250 },
    calories: { min: 500, max: 10000 },
    bmr:      { min: 500, max: 5000 }
  };

  var ACTIVITY = {
    sedentary: { factor: 1.2,   label: 'Sedentary: little or no exercise, desk job' },
    light:     { factor: 1.375, label: 'Lightly active: light exercise 1 to 3 days a week' },
    moderate:  { factor: 1.55,  label: 'Moderately active: exercise 3 to 5 days a week' },
    very:      { factor: 1.725, label: 'Very active: hard exercise 6 to 7 days a week' },
    extra:     { factor: 1.9,   label: 'Extra active: very hard exercise and a physical job' }
  };

  var BMI_ADULT_MIN_AGE = 18;
  var BMR_MIN_AGE = 18;
  var BMR_VALIDATED_AGE = { min: 19, max: 78 }; // approximate range of the original study

  var MSG = {
    minorBmi: 'Adult BMI categories (underweight, healthy, overweight) are not used for children and teenagers. ' +
      'For under 18s, BMI has to be compared with growth charts for age and sex. A doctor, nurse or dietitian can do this for you.',
    minorEnergy: 'This calculator is for adults aged 18 and over. Energy needs of children and teenagers change as they grow, ' +
      'so we do not give calorie targets for under 18s. Please ask a doctor or registered dietitian.',
    pregnancyBmi: 'BMI categories are not a reliable guide in pregnancy or while breastfeeding, so we do not show one. ' +
      'Please follow the advice of your doctor or midwife.',
    pregnancyEnergy: 'Energy needs change during pregnancy and breastfeeding and these formulas were not designed for them, ' +
      'so we do not show an estimate. Please ask your doctor, midwife or a registered dietitian.'
  };

  // ---------- small helpers ----------
  function round(x, d) {
    var m = Math.pow(10, d || 0);
    return Math.round((x + Number.EPSILON) * m) / m;
  }

  // Returns null for blank, NaN for anything that is not a plain decimal number, otherwise the number.
  function num(v) {
    if (v === null || v === undefined) return null;
    if (typeof v === 'number') return isFinite(v) ? v : NaN;
    var s = String(v).trim();
    if (s === '') return null;
    if (!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(s)) return NaN;
    return Number(s);
  }

  function fmt(x, d) {
    var r = round(x, d === undefined ? 1 : d);
    return String(r);
  }

  // ---------- unit conversion ----------
  function lbToKg(lb) { return lb * KG_PER_LB; }
  function kgToLb(kg) { return kg / KG_PER_LB; }
  function inToCm(i) { return i * CM_PER_IN; }
  function cmToIn(cm) { return cm / CM_PER_IN; }
  function ftInToCm(ft, inch) { return (ft * IN_PER_FT + inch) * CM_PER_IN; }
  function cmToFtIn(cm) {
    var totalIn = cmToIn(cm);
    var ft = Math.floor(totalIn / IN_PER_FT);
    var inch = totalIn - ft * IN_PER_FT;
    // carry if rounding to 1 decimal gives 12
    if (round(inch, 1) >= IN_PER_FT) { ft += 1; inch = 0; }
    return { ft: ft, inch: round(inch, 1) };
  }

  // ---------- input reading and validation ----------
  function readField(raw, key, label, lim, errors, unitLabel, required) {
    var n = num(raw);
    if (n === null) { if (required !== false) errors[key] = 'Enter your ' + label + '.'; return null; }
    if (isNaN(n)) { errors[key] = 'Enter ' + label + ' as a number, for example 70.'; return null; }
    if (n <= 0) { errors[key] = label.charAt(0).toUpperCase() + label.slice(1) + ' must be more than zero.'; return null; }
    if (lim && (n < lim.min || n > lim.max)) {
      errors[key] = label.charAt(0).toUpperCase() + label.slice(1) + ' should be between ' + lim.min + ' and ' + lim.max + (unitLabel ? ' ' + unitLabel : '') + '.';
      return null;
    }
    return n;
  }

  function readAge(raw, errors) {
    var n = num(raw);
    if (n === null) { errors.age = 'Enter your age in years.'; return null; }
    if (isNaN(n)) { errors.age = 'Enter your age as a whole number, for example 28.'; return null; }
    if (n !== Math.floor(n)) { errors.age = 'Enter your age as a whole number of years.'; return null; }
    if (n < LIMITS.age.min || n > LIMITS.age.max) { errors.age = 'Age should be between ' + LIMITS.age.min + ' and ' + LIMITS.age.max + ' years.'; return null; }
    return n;
  }

  function readWeightKg(raw, units, errors) {
    var imperial = units === 'imperial';
    var lim = imperial
      ? { min: round(kgToLb(LIMITS.weightKg.min), 0), max: Math.floor(kgToLb(LIMITS.weightKg.max)) }
      : LIMITS.weightKg;
    var v = readField(raw.weight, 'weight', 'weight', lim, errors, imperial ? 'lb' : 'kg');
    if (v === null) return null;
    return imperial ? lbToKg(v) : v;
  }

  function readHeightCm(raw, units, errors) {
    if (units === 'imperial') {
      var ftN = num(raw.feet), inN = num(raw.inches);
      if (ftN === null) { errors.height = 'Enter your height in feet.'; return null; }
      if (isNaN(ftN) || ftN < 0) { errors.height = 'Enter feet as a number, for example 5.'; return null; }
      if (inN === null) inN = 0;
      if (isNaN(inN) || inN < 0) { errors.height = 'Enter inches as a number, for example 9.'; return null; }
      if (inN >= IN_PER_FT) { errors.height = 'Inches should be less than 12. Use the feet box for whole feet.'; return null; }
      var cm = ftInToCm(ftN, inN);
      if (cm <= 0) { errors.height = 'Height must be more than zero.'; return null; }
      if (cm < LIMITS.heightCm.min || cm > LIMITS.heightCm.max) {
        errors.height = 'Height should be between about 1 ft 8 in and 8 ft 2 in.';
        return null;
      }
      return cm;
    }
    return readField(raw.height, 'height', 'height', LIMITS.heightCm, errors, 'cm');
  }

  function unitsOf(raw) { return raw && raw.units === 'imperial' ? 'imperial' : 'metric'; }
  function isYes(v) { return v === true || v === 'true' || v === 'on' || v === 'yes' || v === 1 || v === '1'; }

  // ---------- BMI ----------
  var BMI_BANDS = [
    { max: 18.5, key: 'underweight', label: 'Underweight' },
    { max: 25,   key: 'healthy',     label: 'Healthy weight range' },
    { max: 30,   key: 'overweight',  label: 'Overweight range' },
    { max: 35,   key: 'obese1',      label: 'Obesity range, class 1' },
    { max: 40,   key: 'obese2',      label: 'Obesity range, class 2' },
    { max: Infinity, key: 'obese3',  label: 'Obesity range, class 3' }
  ];

  function bmiCategory(displayValue) {
    for (var i = 0; i < BMI_BANDS.length; i++) {
      if (displayValue < BMI_BANDS[i].max) return BMI_BANDS[i];
    }
    return BMI_BANDS[BMI_BANDS.length - 1];
  }

  function bmiFromMetric(weightKg, heightCm) {
    var m = heightCm / 100;
    var sq = m * m;
    if (!(sq > 0)) return NaN; // guard against divide by zero
    return weightKg / sq;
  }

  function bmi(raw) {
    raw = raw || {};
    var units = unitsOf(raw), errors = {};
    var age = readAge(raw.age, errors);
    var weightKg = readWeightKg(raw, units, errors);
    var heightCm = readHeightCm(raw, units, errors);
    if (Object.keys(errors).length) return { ok: false, errors: errors };

    var value = bmiFromMetric(weightKg, heightCm);
    if (!isFinite(value)) return { ok: false, errors: { height: 'Height must be more than zero.' } };
    var display = round(value, 1);
    var m = heightCm / 100;
    var res = {
      ok: true, value: value, display: display, age: age, weightKg: weightKg, heightCm: heightCm,
      classified: false, category: null, categoryKey: null, notes: [], steps: []
    };
    res.steps.push('Weight = ' + fmt(weightKg, 2) + ' kg' + (units === 'imperial' ? ' (converted from ' + fmt(kgToLb(weightKg), 1) + ' lb)' : ''));
    res.steps.push('Height = ' + fmt(m, 3) + ' m' + (units === 'imperial' ? ' (converted from ' + fmt(cmToIn(heightCm), 1) + ' in)' : ''));
    res.steps.push('BMI = weight in kg / (height in metres x height in metres) = ' + fmt(weightKg, 2) + ' / (' + fmt(m, 3) + ' x ' + fmt(m, 3) + ') = ' + display);

    if (age < BMI_ADULT_MIN_AGE) {
      res.blockedClass = 'minor';
      res.notes.push(MSG.minorBmi);
      return res;
    }
    if (isYes(raw.pregnant)) {
      res.blockedClass = 'pregnancy';
      res.notes.push(MSG.pregnancyBmi);
      return res;
    }
    var band = bmiCategory(display);
    res.classified = true; res.category = band.label; res.categoryKey = band.key;
    var minKg = 18.5 * m * m, maxKg = 24.9 * m * m;
    res.healthyRange = { minKg: minKg, maxKg: maxKg };
    res.healthyRangeText = units === 'imperial'
      ? fmt(kgToLb(minKg), 1) + ' to ' + fmt(kgToLb(maxKg), 1) + ' lb'
      : fmt(minKg, 1) + ' to ' + fmt(maxKg, 1) + ' kg';
    res.steps.push('Adult categories (WHO): under 18.5 underweight, 18.5 to 24.9 healthy, 25 to 29.9 overweight, 30 and over obesity range. Category uses the BMI rounded to one decimal.');
    if (display >= 23) {
      res.notes.push('Some health bodies suggest lower cut-offs for people of South Asian background: about 23 and above can already carry extra health risk, and 27.5 and above higher risk. Ask your doctor what applies to you.');
    }
    return res;
  }

  // ---------- BMR (Mifflin-St Jeor) ----------
  function mifflin(sex, weightKg, heightCm, age) {
    var base = 10 * weightKg + 6.25 * heightCm - 5 * age;
    return sex === 'male' ? base + 5 : base - 161;
  }

  function readSex(raw, errors) {
    var s = (raw.sex || '').toString().toLowerCase();
    if (s === 'male' || s === 'female' || s === 'unspecified') return s;
    errors.sex = "Choose Male or Female, or choose 'Prefer not to say' to see a range.";
    return null;
  }

  function bmrFromBody(raw, units, ageIn) {
    var errors = {};
    var sex = readSex(raw, errors);
    var weightKg = readWeightKg(raw, units, errors);
    var heightCm = readHeightCm(raw, units, errors);
    if (Object.keys(errors).length) return { ok: false, errors: errors };
    var out = {
      ok: true, sex: sex, weightKg: weightKg, heightCm: heightCm, age: ageIn, notes: [], steps: []
    };
    var inputs = '10 x ' + fmt(weightKg, 2) + ' kg + 6.25 x ' + fmt(heightCm, 1) + ' cm - 5 x ' + ageIn;
    if (sex === 'male') {
      out.value = mifflin('male', weightKg, heightCm, ageIn);
      out.steps.push('Male: ' + inputs + ' + 5 = ' + fmt(out.value, 1) + ' kcal/day');
    } else if (sex === 'female') {
      out.value = mifflin('female', weightKg, heightCm, ageIn);
      out.steps.push('Female: ' + inputs + ' - 161 = ' + fmt(out.value, 1) + ' kcal/day');
    } else {
      var m = mifflin('male', weightKg, heightCm, ageIn), f = mifflin('female', weightKg, heightCm, ageIn);
      out.low = Math.min(m, f); out.high = Math.max(m, f); out.value = (m + f) / 2; out.range = true;
      out.steps.push('Male equation: ' + inputs + ' + 5 = ' + fmt(m, 1) + ' kcal/day');
      out.steps.push('Female equation: ' + inputs + ' - 161 = ' + fmt(f, 1) + ' kcal/day');
      out.steps.push('Midpoint of the two = ' + fmt(out.value, 1) + ' kcal/day. Your real value is likely to sit within or near this range.');
      out.notes.push('You chose not to give a sex, so we show both published equations as a range. The two differ by 166 kcal a day by design.');
    }
    if (ageIn < BMR_VALIDATED_AGE.min || ageIn > BMR_VALIDATED_AGE.max) {
      out.notes.push('The equation was developed with adults of about 19 to 78 years. At your age the estimate is less reliable.');
    }
    return out;
  }

  function energyGate(raw, age) {
    if (age < BMR_MIN_AGE) return { ok: false, blocked: 'minor', message: MSG.minorEnergy };
    if (isYes(raw.pregnant)) return { ok: false, blocked: 'pregnancy', message: MSG.pregnancyEnergy };
    return null;
  }

  function bmr(raw) {
    raw = raw || {};
    var units = unitsOf(raw), errors = {};
    var age = readAge(raw.age, errors);
    if (age === null) return { ok: false, errors: errors };
    var gate = energyGate(raw, age);
    if (gate) return gate;
    var r = bmrFromBody(raw, units, age);
    if (!r.ok) return r;
    r.display = Math.round(r.value);
    if (r.range) { r.lowDisplay = Math.round(r.low); r.highDisplay = Math.round(r.high); }
    return r;
  }

  // ---------- TDEE ----------
  function tdee(raw) {
    raw = raw || {};
    var units = unitsOf(raw), errors = {};
    var age = readAge(raw.age, errors);
    var act = ACTIVITY[raw.activity];
    if (!act) errors.activity = 'Choose how active you are in a normal week.';
    if (age === null || !act) {
      // report as many errors as we can, but still check the other fields if age is fine
      if (age !== null) {
        var g0 = energyGate(raw, age);
        if (g0) return g0;
      }
      return { ok: false, errors: errors };
    }
    var gate = energyGate(raw, age);
    if (gate) return gate;

    var manual = num(raw.manualBmr);
    var base;
    if (manual !== null) {
      if (isNaN(manual) || manual <= 0) return { ok: false, errors: { manualBmr: 'Enter your BMR as a number of calories, for example 1600, or leave it blank.' } };
      if (manual < LIMITS.bmr.min || manual > LIMITS.bmr.max) return { ok: false, errors: { manualBmr: 'BMR should be between ' + LIMITS.bmr.min + ' and ' + LIMITS.bmr.max + ' kcal a day.' } };
      base = { ok: true, value: manual, manual: true, notes: [], steps: ['BMR entered by you = ' + fmt(manual, 0) + ' kcal/day (the Mifflin-St Jeor step was skipped)'] };
    } else {
      base = bmrFromBody(raw, units, age);
      if (!base.ok) return base;
    }
    var f = act.factor;
    var out = {
      ok: true, activityKey: raw.activity, factor: f, activityLabel: act.label, age: age,
      bmrManual: !!base.manual, notes: base.notes.slice(), steps: base.steps.slice()
    };
    out.value = base.value * f;
    out.display = Math.round(out.value);
    out.steps.push('TDEE = BMR x activity factor = ' + fmt(base.value, 1) + ' x ' + f + ' = ' + fmt(out.value, 1) + ' kcal/day');
    if (base.range) {
      out.range = true;
      out.low = base.low * f; out.high = base.high * f;
      out.lowDisplay = Math.round(out.low); out.highDisplay = Math.round(out.high);
      out.steps.push('Range: ' + fmt(base.low, 1) + ' x ' + f + ' = ' + fmt(out.low, 1) + ' to ' + fmt(base.high, 1) + ' x ' + f + ' = ' + fmt(out.high, 1) + ' kcal/day');
    }
    out.notes.push('Activity factors are rounded averages, and real energy use varies from person to person and day to day. Treat this as a starting point, not an exact figure.');
    return out;
  }

  // ---------- Macros ----------
  function macros(raw) {
    raw = raw || {};
    var errors = {};
    var age = readAge(raw.age, errors);
    var cals = readField(raw.calories, 'calories', 'daily calorie target', LIMITS.calories, errors, 'kcal');
    var p = pct(raw.proteinPct, 'proteinPct', 'protein percentage', errors);
    var c = pct(raw.carbPct, 'carbPct', 'carbohydrate percentage', errors);
    var f = pct(raw.fatPct, 'fatPct', 'fat percentage', errors);
    if (age !== null && age < BMR_MIN_AGE) {
      return { ok: false, blocked: 'minor', message: MSG.minorEnergy };
    }
    if (Object.keys(errors).length) return { ok: false, errors: errors };
    var total = round(p + c + f, 4);
    if (total !== 100) {
      return { ok: false, total: total, errors: { total: 'Protein, carbohydrate and fat percentages must add up to 100. They currently add up to ' + fmt(total, 2) + '.' } };
    }
    var out = { ok: true, calories: cals, notes: [], steps: [], parts: {} };
    var defs = [['protein', p, 'Protein'], ['carbs', c, 'Carbohydrate'], ['fat', f, 'Fat']];
    var sumKcal = 0;
    defs.forEach(function (d) {
      var kcal = cals * d[1] / 100;
      var grams = kcal / KCAL_PER_G[d[0]];
      out.parts[d[0]] = { pct: d[1], kcal: kcal, grams: grams, gramsDisplay: round(grams, 1), kcalDisplay: Math.round(kcal) };
      sumKcal += grams * KCAL_PER_G[d[0]];
      out.steps.push(d[2] + ': ' + fmt(cals, 0) + ' x ' + fmt(d[1], 2) + '% = ' + fmt(kcal, 1) + ' kcal, divided by ' + KCAL_PER_G[d[0]] + ' kcal per gram = ' + fmt(grams, 1) + ' g');
    });
    out.checkKcal = sumKcal;
    out.steps.push('Check: the grams add back up to ' + fmt(sumKcal, 1) + ' kcal (protein and carbohydrate 4 kcal/g, fat 9 kcal/g).');
    if (cals < 1200) {
      out.notes.push('A target below 1,200 kcal a day is very low for most adults. Please speak to a doctor or registered dietitian before eating this little.');
    }
    return out;
  }

  function pct(raw, key, label, errors) {
    var n = num(raw);
    if (n === null) { errors[key] = 'Enter the ' + label + ', or 0 if none.'; return null; }
    if (isNaN(n)) { errors[key] = 'Enter the ' + label + ' as a number, for example 30.'; return null; }
    if (n < 0 || n > 100) { errors[key] = 'The ' + label + ' should be between 0 and 100.'; return null; }
    return n;
  }

  return {
    KG_PER_LB: KG_PER_LB, CM_PER_IN: CM_PER_IN, KCAL_PER_G: KCAL_PER_G, LIMITS: LIMITS, ACTIVITY: ACTIVITY,
    BMI_BANDS: BMI_BANDS, MSG: MSG,
    lbToKg: lbToKg, kgToLb: kgToLb, inToCm: inToCm, cmToIn: cmToIn, ftInToCm: ftInToCm, cmToFtIn: cmToFtIn,
    num: num, round: round,
    bmi: bmi, bmiFromMetric: bmiFromMetric, bmiCategory: bmiCategory,
    mifflin: mifflin, bmr: bmr, tdee: tdee, macros: macros
  };
});
