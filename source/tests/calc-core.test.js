const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('../calc-core.js');
const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} is not within ${eps} of ${b}`);

test('unit conversions use exact definitions', () => {
  near(C.lbToKg(1), 0.45359237);
  near(C.kgToLb(0.45359237), 1);
  near(C.inToCm(1), 2.54);
  near(C.ftInToCm(5, 9), 175.26);
  near(C.cmToIn(2.54), 1);
  near(C.kgToLb(C.lbToKg(154.3)), 154.3, 1e-9);
  near(C.cmToIn(C.inToCm(69)), 69, 1e-9);
});

test('cmToFtIn splits and carries correctly', () => {
  assert.deepEqual(C.cmToFtIn(175.26), { ft: 5, inch: 9 });
  assert.deepEqual(C.cmToFtIn(182.88), { ft: 6, inch: 0 });
  // 5 ft 11.97 in rounds to 6 ft 0 in, never "5 ft 12 in"
  assert.deepEqual(C.cmToFtIn(C.ftInToCm(5, 11.97)), { ft: 6, inch: 0 });
});

test('num() reads blanks, junk and numbers', () => {
  assert.equal(C.num(''), null);
  assert.equal(C.num('   '), null);
  assert.equal(C.num(undefined), null);
  assert.ok(Number.isNaN(C.num('abc')));
  assert.ok(Number.isNaN(C.num('1e3')));
  assert.ok(Number.isNaN(C.num('0x10')));
  assert.ok(Number.isNaN(C.num(Infinity)));
  assert.equal(C.num('70.5'), 70.5);
  assert.equal(C.num(' 70 '), 70);
  assert.equal(C.num('-5'), -5);
});

// ---- BMI ----
test('BMI metric: 70 kg, 175 cm = 22.9, healthy range', () => {
  const r = C.bmi({ units: 'metric', age: 30, weight: '70', height: '175' });
  assert.equal(r.ok, true);
  near(r.value, 70 / (1.75 * 1.75));
  assert.equal(r.display, 22.9);
  assert.equal(r.categoryKey, 'healthy');
  assert.equal(r.classified, true);
  assert.equal(r.healthyRangeText, '56.7 to 76.3 kg');
});

test('BMI imperial gives the same answer as the metric equivalent', () => {
  const metric = C.bmi({ units: 'metric', age: 30, weight: C.lbToKg(154).toString(), height: C.ftInToCm(5, 9).toString() });
  const imp = C.bmi({ units: 'imperial', age: 30, weight: '154', feet: '5', inches: '9' });
  near(imp.value, metric.value, 1e-9);
  assert.equal(imp.display, 22.7);
  assert.match(imp.healthyRangeText, / lb$/);
});

test('BMI category boundaries (using the displayed one-decimal value)', () => {
  const cat = (v) => C.bmiCategory(v).key;
  assert.equal(cat(18.4), 'underweight');
  assert.equal(cat(18.5), 'healthy');
  assert.equal(cat(24.9), 'healthy');
  assert.equal(cat(25.0), 'overweight');
  assert.equal(cat(29.9), 'overweight');
  assert.equal(cat(30.0), 'obese1');
  assert.equal(cat(35.0), 'obese2');
  assert.equal(cat(40.0), 'obese3');
});

test('BMI: South Asian note appears from 23', () => {
  const r = C.bmi({ units: 'metric', age: 30, weight: '75', height: '170' }); // 25.95
  assert.ok(r.notes.some((n) => /South Asian/.test(n)));
  const low = C.bmi({ units: 'metric', age: 30, weight: '60', height: '175' }); // 19.6
  assert.equal(low.notes.length, 0);
});

test('BMI is never classified for under 18s', () => {
  const r = C.bmi({ units: 'metric', age: 15, weight: '50', height: '160' });
  assert.equal(r.ok, true);
  assert.equal(r.classified, false);
  assert.equal(r.category, null);
  assert.equal(r.healthyRangeText, undefined);
  assert.match(r.notes[0], /children and teenagers/);
  const adult = C.bmi({ units: 'metric', age: 18, weight: '50', height: '160' });
  assert.equal(adult.classified, true);
});

test('BMI category withheld during pregnancy or breastfeeding', () => {
  const r = C.bmi({ units: 'metric', age: 28, weight: '65', height: '160', pregnant: true });
  assert.equal(r.ok, true);
  assert.equal(r.classified, false);
  assert.match(r.notes[0], /pregnancy or while breastfeeding/);
});

test('BMI validation: blank, zero, negative, text, out of range, divide by zero', () => {
  let r = C.bmi({ units: 'metric', age: '', weight: '', height: '' });
  assert.equal(r.ok, false);
  assert.ok(r.errors.age && r.errors.weight && r.errors.height);
  r = C.bmi({ units: 'metric', age: 30, weight: '70', height: '0' });
  assert.equal(r.ok, false); assert.ok(r.errors.height);
  r = C.bmi({ units: 'metric', age: 30, weight: '-70', height: '175' });
  assert.equal(r.ok, false); assert.ok(r.errors.weight);
  r = C.bmi({ units: 'metric', age: 30, weight: 'seventy', height: '175' });
  assert.equal(r.ok, false); assert.ok(r.errors.weight);
  r = C.bmi({ units: 'metric', age: 30, weight: '70', height: '1.75' }); // metres typed by mistake
  assert.equal(r.ok, false); assert.match(r.errors.height, /between 50 and 250/);
  r = C.bmi({ units: 'metric', age: 30.5, weight: '70', height: '175' });
  assert.equal(r.ok, false); assert.ok(r.errors.age);
  r = C.bmi({ units: 'imperial', age: 30, weight: '154', feet: '0', inches: '0' });
  assert.equal(r.ok, false); assert.ok(r.errors.height);
  r = C.bmi({ units: 'imperial', age: 30, weight: '154', feet: '5', inches: '12' });
  assert.equal(r.ok, false); assert.match(r.errors.height, /less than 12/);
  r = C.bmi({ units: 'imperial', age: 30, weight: '154', feet: '5', inches: '' }); // blank inches = 0
  assert.equal(r.ok, true);
  assert.equal(C.bmiFromMetric(70, 0) !== Infinity, true);
  assert.ok(Number.isNaN(C.bmiFromMetric(70, 0)));
});

// ---- BMR ----
test('BMR male: 80 kg, 180 cm, 30 y = 1780', () => {
  const r = C.bmr({ units: 'metric', age: 30, sex: 'male', weight: '80', height: '180' });
  assert.equal(r.ok, true);
  near(r.value, 10 * 80 + 6.25 * 180 - 5 * 30 + 5);
  assert.equal(r.display, 1780);
});

test('BMR female: 60 kg, 165 cm, 25 y = 1345.25', () => {
  const r = C.bmr({ units: 'metric', age: 25, sex: 'female', weight: '60', height: '165' });
  near(r.value, 600 + 1031.25 - 125 - 161);
  assert.equal(r.display, 1345);
});

test('BMR male and female differ by exactly 166 kcal', () => {
  const a = C.mifflin('male', 70, 170, 40), b = C.mifflin('female', 70, 170, 40);
  near(a - b, 166);
});

test('BMR imperial converts before applying the equation', () => {
  const imp = C.bmr({ units: 'imperial', age: 30, sex: 'male', weight: '176.3696', feet: '5', inches: '10.8661' });
  const metric = C.bmr({ units: 'metric', age: 30, sex: 'male', weight: String(C.lbToKg(176.3696)), height: String(C.ftInToCm(5, 10.8661)) });
  near(imp.value, metric.value, 1e-6);
});

test('BMR "prefer not to say" returns a range with both equations', () => {
  const r = C.bmr({ units: 'metric', age: 30, sex: 'unspecified', weight: '80', height: '180' });
  assert.equal(r.ok, true);
  assert.equal(r.range, true);
  near(r.high - r.low, 166);
  near(r.value, (r.low + r.high) / 2);
  assert.equal(r.lowDisplay, 1614);
  assert.equal(r.highDisplay, 1780);
  assert.ok(r.notes.some((n) => /not to give a sex/.test(n)));
});

test('BMR requires sex choice and body inputs; reports missing data', () => {
  let r = C.bmr({ units: 'metric', age: 30, sex: '', weight: '80', height: '180' });
  assert.equal(r.ok, false); assert.ok(r.errors.sex);
  r = C.bmr({ units: 'metric', age: 30, sex: 'male', weight: '', height: '' });
  assert.ok(r.errors.weight && r.errors.height);
  r = C.bmr({ units: 'metric', age: '', sex: 'male', weight: '80', height: '180' });
  assert.ok(r.errors.age);
});

test('BMR is blocked for under 18s and during pregnancy/breastfeeding', () => {
  let r = C.bmr({ units: 'metric', age: 17, sex: 'male', weight: '60', height: '170' });
  assert.equal(r.ok, false); assert.equal(r.blocked, 'minor'); assert.match(r.message, /18 and over/);
  r = C.bmr({ units: 'metric', age: 30, sex: 'female', weight: '60', height: '165', pregnant: true });
  assert.equal(r.ok, false); assert.equal(r.blocked, 'pregnancy');
  r = C.bmr({ units: 'metric', age: 18, sex: 'male', weight: '60', height: '170' });
  assert.equal(r.ok, true);
});

test('BMR warns outside the age range of the original study', () => {
  const old = C.bmr({ units: 'metric', age: 85, sex: 'male', weight: '70', height: '170' });
  assert.ok(old.notes.some((n) => /less reliable/.test(n)));
  const mid = C.bmr({ units: 'metric', age: 40, sex: 'male', weight: '70', height: '170' });
  assert.equal(mid.notes.length, 0);
});

// ---- TDEE ----
test('TDEE = BMR x activity factor, for every factor', () => {
  const base = { units: 'metric', age: 30, sex: 'male', weight: '80', height: '180' };
  const want = { sedentary: 1.2, light: 1.375, moderate: 1.55, very: 1.725, extra: 1.9 };
  for (const [k, f] of Object.entries(want)) {
    const r = C.tdee({ ...base, activity: k });
    assert.equal(r.ok, true);
    near(r.value, 1780 * f, 1e-9);
    assert.equal(r.factor, f);
  }
  assert.equal(C.tdee({ ...base, activity: 'moderate' }).display, 2759);
});

test('TDEE needs an activity level', () => {
  const r = C.tdee({ units: 'metric', age: 30, sex: 'male', weight: '80', height: '180', activity: '' });
  assert.equal(r.ok, false); assert.ok(r.errors.activity);
});

test('TDEE skip path: known BMR needs no sex, weight or height', () => {
  const r = C.tdee({ units: 'metric', age: 30, manualBmr: '1600', activity: 'light' });
  assert.equal(r.ok, true);
  assert.equal(r.bmrManual, true);
  near(r.value, 1600 * 1.375);
  assert.equal(C.tdee({ units: 'metric', age: 30, manualBmr: 'abc', activity: 'light' }).ok, false);
  assert.equal(C.tdee({ units: 'metric', age: 30, manualBmr: '50', activity: 'light' }).ok, false);
  assert.equal(C.tdee({ units: 'metric', age: 30, manualBmr: '0', activity: 'light' }).ok, false);
});

test('TDEE with no sex given returns a range', () => {
  const r = C.tdee({ units: 'metric', age: 30, sex: 'unspecified', weight: '80', height: '180', activity: 'moderate' });
  assert.equal(r.range, true);
  near(r.high, 1780 * 1.55); near(r.low, 1614 * 1.55);
});

test('TDEE blocked for minors, even with a manual BMR, and in pregnancy', () => {
  let r = C.tdee({ units: 'metric', age: 16, manualBmr: '1600', activity: 'light' });
  assert.equal(r.ok, false); assert.equal(r.blocked, 'minor');
  r = C.tdee({ units: 'metric', age: 16, activity: '' });
  assert.equal(r.blocked, 'minor');
  r = C.tdee({ units: 'metric', age: 30, manualBmr: '1600', activity: 'light', pregnant: true });
  assert.equal(r.blocked, 'pregnancy');
});

// ---- Macros ----
test('Macros: 2000 kcal at 30/40/30 -> 150 g protein, 200 g carbs, 66.7 g fat', () => {
  const r = C.macros({ age: 30, calories: '2000', proteinPct: '30', carbPct: '40', fatPct: '30' });
  assert.equal(r.ok, true);
  near(r.parts.protein.grams, 150);
  near(r.parts.carbs.grams, 200);
  near(r.parts.fat.grams, 600 / 9);
  assert.equal(r.parts.fat.gramsDisplay, 66.7);
  near(r.checkKcal, 2000, 1e-9);
});

test('Macros use 4/4/9 kcal per gram', () => {
  assert.deepEqual(C.KCAL_PER_G, { protein: 4, carbs: 4, fat: 9 });
  const r = C.macros({ age: 25, calories: 1800, proteinPct: 25, carbPct: 50, fatPct: 25 });
  near(r.parts.protein.grams, 112.5); near(r.parts.carbs.grams, 225); near(r.parts.fat.grams, 50);
});

test('Macros must total 100 (floating point safe, decimals allowed)', () => {
  assert.equal(C.macros({ age: 30, calories: 2000, proteinPct: 33.3, carbPct: 33.3, fatPct: 33.4 }).ok, true);
  let r = C.macros({ age: 30, calories: 2000, proteinPct: 30, carbPct: 40, fatPct: 31 });
  assert.equal(r.ok, false); assert.match(r.errors.total, /add up to 100.*101/);
  r = C.macros({ age: 30, calories: 2000, proteinPct: 30, carbPct: 40, fatPct: 29 });
  assert.equal(r.ok, false); assert.equal(r.total, 99);
  assert.equal(C.macros({ age: 30, calories: 2000, proteinPct: 100, carbPct: 0, fatPct: 0 }).ok, true);
});

test('Macros validate calories and percentages; blanks are reported', () => {
  let r = C.macros({ age: 30, calories: '', proteinPct: '', carbPct: '', fatPct: '' });
  assert.equal(r.ok, false);
  assert.ok(r.errors.calories && r.errors.proteinPct && r.errors.carbPct && r.errors.fatPct);
  r = C.macros({ age: 30, calories: '0', proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.ok(r.errors.calories);
  r = C.macros({ age: 30, calories: '200000', proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.ok(r.errors.calories);
  r = C.macros({ age: 30, calories: '2000', proteinPct: '-10', carbPct: 60, fatPct: 50 });
  assert.ok(r.errors.proteinPct);
  r = C.macros({ age: 30, calories: '2000', proteinPct: 'x', carbPct: 60, fatPct: 40 });
  assert.ok(r.errors.proteinPct);
  r = C.macros({ calories: '2000', proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.equal(r.ok, false); assert.ok(r.errors.age);
});

test('Macros: no calorie split for under 18s; very low target gets a caution', () => {
  const m = C.macros({ age: 16, calories: 1500, proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.equal(m.ok, false); assert.equal(m.blocked, 'minor');
  const bad = C.macros({ age: 16, calories: '', proteinPct: '', carbPct: '', fatPct: '' });
  assert.equal(bad.blocked, 'minor');
  const low = C.macros({ age: 30, calories: 900, proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.equal(low.ok, true);
  assert.ok(low.notes.some((n) => /very low/.test(n)));
  const normal = C.macros({ age: 30, calories: 2000, proteinPct: 30, carbPct: 40, fatPct: 30 });
  assert.equal(normal.notes.length, 0);
});

test('Results include readable calculation steps', () => {
  assert.ok(C.bmi({ units: 'metric', age: 30, weight: 70, height: 175 }).steps.length >= 3);
  assert.ok(C.tdee({ units: 'metric', age: 30, sex: 'male', weight: 80, height: 180, activity: 'light' }).steps.some((s) => /TDEE =/.test(s)));
  assert.ok(C.macros({ age: 30, calories: 2000, proteinPct: 30, carbPct: 40, fatPct: 30 }).steps.length === 4);
});

test('Functions never throw on empty or odd input', () => {
  for (const f of [C.bmi, C.bmr, C.tdee, C.macros]) {
    assert.doesNotThrow(() => f());
    assert.doesNotThrow(() => f(null));
    assert.doesNotThrow(() => f({}));
    assert.doesNotThrow(() => f({ age: NaN, weight: Infinity, height: -0, calories: {}, units: 'imperial' }));
  }
});
