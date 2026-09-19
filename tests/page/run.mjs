// Behavioral checks for the static tracker, run against the real page in jsdom.
//
// The Python suite parses site/index.html as text, which cannot tell whether a
// renderer still calls the function it greps for. These checks execute the page
// and assert what a reader would actually see, so deleting the runtime half of a
// fix fails here even when the source still mentions it.
//
// Run: node tests/page/run.mjs   (or: uv run pytest tests/test_page_behavior.py)
import { JSDOM, VirtualConsole } from 'jsdom';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SITE = join(dirname(dirname(dirname(fileURLToPath(import.meta.url)))), 'site');

let failures = 0;
let checks = 0;
let suite = '';
const section = name => { suite = name; console.log(`\n== ${name} ==`); };
const check = (name, condition, detail = '') => {
  checks += 1;
  if (condition) return console.log(`  ok   ${name}`);
  failures += 1;
  console.log(`  FAIL ${name}${detail ? `\n         ${detail}` : ''}`);
};

function load() {
  const virtualConsole = new VirtualConsole();
  const pageErrors = [];
  virtualConsole.on('jsdomError', error => pageErrors.push(error.message));
  const html = readFileSync(join(SITE, 'index.html'), 'utf8');
  const dom = new JSDOM(html, {
    runScripts: 'outside-only',
    url: 'https://example.org/expectations/',
    virtualConsole,
    pretendToBeVisual: true,
  });
  const { window } = dom;
  window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
  // Minimal SVG geometry. matrixTransform is the identity, so a mousemove's
  // clientX reads straight through as a plot-space x and the crosshair's
  // nearest-round search behaves as it does in a browser.
  window.SVGElement.prototype.getScreenCTM = () => ({ inverse: () => ({}) });
  window.SVGSVGElement.prototype.createSVGPoint = function () {
    return { x: 0, y: 0, matrixTransform() { return { x: this.x, y: this.y }; } };
  };
  const script = html.match(/<script>([\s\S]*?)<\/script>/g).pop().replace(/^<script>|<\/script>$/g, '');
  // data.js and the page script are both top-level <script> tags and share one
  // script scope in a browser, so they are evaluated together here too.
  window.eval(`${readFileSync(join(SITE, 'data.js'), 'utf8')}\n${script}\nwindow.DATA = DATA;`);
  return { window, pageErrors };
}

const { window, pageErrors } = load();
const DATA = window.DATA;
const $ = id => window.document.getElementById(id);
const tabs = () => [...window.document.querySelectorAll('#tabs button[role="tab"]')];
const selectedTab = () => tabs().find(tab => tab.getAttribute('aria-selected') === 'true');
const note = () => $('chart-note').textContent;
const title = () => $('chart-title').textContent;
const table = () => $('table').textContent;

const go = async hash => {
  window.location.hash = hash;
  window.dispatchEvent(new window.HashChangeEvent('hashchange'));
  await new Promise(resolve => setTimeout(resolve, 0));
};
const press = key => {
  const event = new window.KeyboardEvent('keydown', { key, bubbles: true, cancelable: true });
  $('tabs').dispatchEvent(event);
  return event;
};
// Hover the crosshair. A large negative x selects the earliest round, a large
// positive x the latest, without needing the view's internal scale.
const hover = clientX => {
  const hit = [...window.document.querySelectorAll('#chart rect')]
    .filter(rect => rect.getAttribute('fill') === 'transparent').pop();
  if (!hit) return '';
  hit.dispatchEvent(new window.MouseEvent('mousemove', { clientX, clientY: 100, bubbles: true }));
  return $('tooltip').textContent;
};
// Read the plotted geometry back into data space. The y-axis tick labels carry
// both a value and a y, which gives a linear inverse; the centre line is the
// undashed open path. This is what makes "the line draws q50" checkable rather
// than merely greppable.
const plottedSeries = () => {
  const ticks = [...window.document.querySelectorAll('#chart text')]
    .filter(node => node.getAttribute('text-anchor') === 'end')
    .map(node => ({ y: Number(node.getAttribute('y')) - 4, value: Number.parseFloat(node.textContent) }))
    .filter(tick => Number.isFinite(tick.y) && Number.isFinite(tick.value));
  if (ticks.length < 2) return null;
  const [a, b] = [ticks[0], ticks[ticks.length - 1]];
  const toValue = y => a.value + (y - a.y) * (b.value - a.value) / (b.y - a.y);
  return [...window.document.querySelectorAll('#chart path')]
    .filter(path => path.getAttribute('fill') === 'none' && !path.getAttribute('stroke-dasharray'))
    .map(path => [...path.getAttribute('d').matchAll(/[ML]([-\d.]+),([-\d.]+)/g)]
      .map(match => toValue(Number(match[2]))));
};

const measures = (() => {
  const fields = DATA.fields.measures;
  const at = name => fields.indexOf(name);
  return DATA.measures.map(row => ({
    survey: row[at('survey')], variable: row[at('variable')], concept: row[at('concept')],
    year: row[at('year')], quarter: row[at('quarter')], horizon_class: row[at('horizon_class')],
    q50: row[at('q50')], median: row[at('median')], q25: row[at('q25')], q75: row[at('q75')],
    iqr: row[at('iqr')],
  }));
})();

section('fix 1 — the fragment is re-read after load');
await go('#view=scores&survey=us&variable=PRGDP&horizon=next_year&rounds=q1');
const scoresTitle = title();
check('#view=scores selects the Scores tab', selectedTab()?.dataset.view === 'scores', selectedTab()?.dataset.view);
check('#view=scores renders the CRPS view', scoresTitle === 'CRPS over time', scoresTitle);
await go('#view=fan&survey=us&variable=PRGDP&horizon=next_year&rounds=q1');
check('editing the fragment moves the selected tab', selectedTab()?.dataset.view === 'fan', selectedTab()?.dataset.view);
check('editing the fragment re-renders the chart', title() !== scoresTitle && /pooled median/i.test(title()), title());
await go('#view=decomposition&survey=us&variable=PRUNEMP&horizon=next_year&rounds=all&measure=sd');
check('the fragment also re-applies the selects', $('variable').value === 'PRUNEMP' && $('rounds').value === 'all',
  `${$('variable').value}/${$('rounds').value}`);
check('the note follows the new selection', note().includes('Unemployment rate'), note().slice(0, 60));
await go('#view=calibration');
check('a partial fragment still switches view', selectedTab()?.dataset.view === 'calibration', selectedTab()?.dataset.view);
check('the hash is re-canonicalized after a change', window.location.hash.includes('survey='), window.location.hash);

section('fix 2 — the tab pattern works at runtime, not just in the markup');
check('panel is a tabpanel', $('panel').getAttribute('role') === 'tabpanel');
check('every tab controls the panel', tabs().every(tab => tab.getAttribute('aria-controls') === 'panel'));
check('tablist has an accessible name', !!$('tabs').getAttribute('aria-label'));
const order = tabs().map(tab => tab.dataset.view);
const rovingIsCoherent = () => {
  const focusable = tabs().filter(tab => tab.tabIndex === 0);
  return focusable.length === 1 && focusable[0] === selectedTab();
};
check('roving tabindex follows selection after a hash change', rovingIsCoherent(),
  tabs().map(tab => `${tab.dataset.view}=${tab.tabIndex}`).join(' '));
check('panel is labelled by the selected tab after a hash change',
  $('panel').getAttribute('aria-labelledby') === selectedTab()?.id,
  `${$('panel').getAttribute('aria-labelledby')} vs ${selectedTab()?.id}`);
$('tabs').querySelector('[data-view="term"]').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
check('a click selects that tab', selectedTab()?.dataset.view === 'term', selectedTab()?.dataset.view);
check('roving tabindex follows a click', rovingIsCoherent(), tabs().map(t => `${t.dataset.view}=${t.tabIndex}`).join(' '));
check('panel label follows a click', $('panel').getAttribute('aria-labelledby') === selectedTab()?.id);
check('a click re-renders', title().length > 0, title());
const beforeArrow = selectedTab().dataset.view;
let event = press('ArrowRight');
check('ArrowRight moves to the next tab',
  selectedTab().dataset.view === order[(order.indexOf(beforeArrow) + 1) % order.length], selectedTab().dataset.view);
check('ArrowRight is prevented from scrolling the page', event.defaultPrevented);
check('ArrowRight moves focus to the newly selected tab', window.document.activeElement === selectedTab(),
  window.document.activeElement?.id);
check('roving tabindex follows the keyboard', rovingIsCoherent(), tabs().map(t => `${t.dataset.view}=${t.tabIndex}`).join(' '));
check('panel label follows the keyboard', $('panel').getAttribute('aria-labelledby') === selectedTab().id);
press('ArrowLeft');
check('ArrowLeft returns to the previous tab', selectedTab().dataset.view === beforeArrow, selectedTab().dataset.view);
press('Home');
check('Home selects the first tab', selectedTab().dataset.view === order[0], selectedTab().dataset.view);
press('ArrowLeft');
check('ArrowLeft wraps from the first tab to the last', selectedTab().dataset.view === order.at(-1), selectedTab().dataset.view);
press('ArrowRight');
check('ArrowRight wraps from the last tab to the first', selectedTab().dataset.view === order[0], selectedTab().dataset.view);
press('End');
check('End selects the last tab', selectedTab().dataset.view === order.at(-1), selectedTab().dataset.view);
check('End re-renders too', title().length > 0, title());
check('an unrelated key is ignored', !press('ArrowDown').defaultPrevented);
check('every tab names a view the page can render',
  order.every(view => { const before = selectedTab().dataset.view; $('tabs').querySelector(`[data-view="${view}"]`)
    .dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    const moved = selectedTab().dataset.view === view; if (!moved) console.log(`         inert tab: ${view} (was ${before})`);
    return moved && title().length > 0; }),
  'a tab whose data-view is not a renderer is silently inert');

section('fix 3 — the benchmark note claims only what the code does');
await go('#view=scores&survey=us&variable=PRGDP&horizon=next_year&rounds=q1');
check('the rendered note drops the "information available" claim', !/information available/i.test(note()));
check('the rendered note names target-period completion', /already complete at each forecast round/.test(note()), note());
check('the rendered note says the outcomes are revised', /revised data/.test(note()));

section('fix 4 — historical concepts are named, per view');
const eraCases = [
  ['decomposition', '#view=decomposition&survey=us&variable=PRGDP&horizon=current_year&rounds=all&measure=sd',
    [/nominal GNP growth/, /real GNP growth/, /real GDP growth from 1992 Q1 onward/]],
  ['decomposition (IQR)', '#view=decomposition&survey=us&variable=PRPGDP&horizon=next_year&rounds=all&measure=iqr',
    [/GNP implicit price deflator/, /chain-weighted GDP price index/]],
  ['fan', '#view=fan&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', [/implicit price deflator/]],
  ['calibration', '#view=calibration&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', [/GDP implicit price deflator/]],
  ['scores', '#view=scores&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', [/GDP implicit price deflator/]],
  ['term structure', '#view=term&survey=us&variable=PRPGDP&rounds=all', [/GDP implicit price deflator/]],
];
for (const [name, hash, patterns] of eraCases) {
  await go(hash);
  check(`${name} names its historical concepts`, patterns.every(pattern => pattern.test(note())), note());
}
await go('#view=decomposition&survey=us&variable=PRUNEMP&horizon=next_year&rounds=all&measure=sd');
check('a single-concept variable gets no era sentence', !/changed concept/.test(note()), note());
await go('#view=decomposition&survey=ecb&variable=rgdp&horizon=rolling_1y&rounds=all&measure=sd');
check('an ECB variable gets no era sentence', !/changed concept/.test(note()), note());
await go('#view=overview&concept=growth&compare=next_year&rounds=q1');
check('the overview carries no era sentence', !/changed concept/.test(note()), note());
// The era ranges must describe the rounds actually plotted, not the whole table.
await go('#view=decomposition&survey=us&variable=PRPGDP&horizon=next_year&rounds=all&measure=sd');
const allRoundsNote = note();
await go('#view=decomposition&survey=us&variable=PRPGDP&horizon=next_year&rounds=q1&measure=sd');
check('era ranges track the rounds filter', allRoundsNote !== note() && /1995 Q4/.test(allRoundsNote) && /1995 Q1/.test(note()),
  `all: ...${allRoundsNote.slice(-90)}\n         q1 : ...${note().slice(-90)}`);

section('fix 4 — the tooltip names the concept on exactly the historical rounds');
const tooltipCases = [
  ['decomposition', '#view=decomposition&survey=us&variable=PRGDP&horizon=current_year&rounds=all&measure=sd', /nominal GNP growth/],
  ['fan', '#view=fan&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', /implicit price deflator/],
  ['calibration', '#view=calibration&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', /GDP implicit price deflator/],
  ['scores', '#view=scores&survey=us&variable=PRPGDP&horizon=next_year&rounds=all', /GDP implicit price deflator/],
];
for (const [name, hash, pattern] of tooltipCases) {
  await go(hash);
  const oldest = hover(-1e6);
  check(`${name} tooltip names the concept on an old round`, /Concept/.test(oldest) && pattern.test(oldest), oldest);
  check(`${name} tooltip omits the concept on the newest round`, !/Concept/.test(hover(1e6)), hover(1e6));
}
await go('#view=term&survey=us&variable=PRPGDP&rounds=all');
check('term tooltip lists the concepts it averaged', /Concepts averaged/.test(hover(0)), hover(0));
await go('#view=decomposition&survey=us&variable=PRUNEMP&horizon=next_year&rounds=all&measure=sd');
check('a single-concept variable adds no concept row', !/Concept/.test(hover(-1e6)), hover(-1e6));

section('fix 5 — the fan reports the pooled median everywhere it names one');
await go('#view=fan&survey=us&variable=PRGDP&horizon=next_year&rounds=q1');
const fanRows = measures.filter(row => row.survey === 'us' && row.variable === 'PRGDP'
  && row.horizon_class === 'next_year' && row.quarter === 1).sort((a, b) => a.year - b.year);
const widest = fanRows.reduce((best, row) => Math.abs(row.q50 - row.median) > Math.abs(best.q50 - best.median) ? row : best);
check('the two medians genuinely differ in this series', Math.abs(widest.q50 - widest.median) > 0.05,
  `max gap ${Math.abs(widest.q50 - widest.median).toFixed(3)}pp in ${widest.year}`);
const fmt = value => Number(value).toFixed(2);
const oldestFan = hover(-1e6);
const first = fanRows[0];
check('the tooltip binds "Pooled median" to q50, not the respondent-mean median',
  oldestFan.includes(`Pooled median${fmt(first.q50)}%`), `${oldestFan}\n         expected q50=${fmt(first.q50)} (median=${fmt(first.median)})`);
check('the tooltip reports the respondent-mean median under its own name',
  oldestFan.includes(`Median of respondent means${fmt(first.median)}%`), oldestFan);
const headerCells = [...window.document.querySelectorAll('#table tr')][0];
const firstBodyRow = [...window.document.querySelectorAll('#table tr')][1];
const headers = [...headerCells.children].map(cell => cell.textContent);
const cells = [...firstBodyRow.children].map(cell => cell.textContent);
check('the table has both medians, distinctly named',
  headers.includes('Pooled median') && headers.includes('Median of respondent means'), headers.join(' | '));
check('the table\'s "Pooled median" column holds q50',
  cells[headers.indexOf('Pooled median')] === fmt(first.q50),
  `${cells[headers.indexOf('Pooled median')]} vs q50 ${fmt(first.q50)}`);
check('the table\'s respondent-mean column holds the respondent-mean median',
  cells[headers.indexOf('Median of respondent means')] === fmt(first.median),
  `${cells[headers.indexOf('Median of respondent means')]} vs median ${fmt(first.median)}`);
check('the legend names the pooled median', /pooled median/i.test($('legend').textContent), $('legend').textContent);
// The drawn centre line must be q50. Both candidates always sit inside the band
// (the respondent-mean median never falls outside pooled q25-q75 in this data),
// so containment cannot separate them; invert the plotted geometry and compare
// it to each candidate on the selection where they diverge most.
await go('#view=fan&survey=us&variable=PRGDP&horizon=current_year&rounds=all');
const centreRows = measures.filter(row => row.survey === 'us' && row.variable === 'PRGDP'
  && row.horizon_class === 'current_year').sort((a, b) => a.year - b.year || a.quarter - b.quarter);
const separation = Math.max(...centreRows.map(row => Math.abs(row.q50 - row.median)));
const drawn = plottedSeries();
const centre = drawn && drawn.find(points => points.length === centreRows.length);
const spread = key => centre
  ? Math.max(...centre.map((value, index) => Math.abs(value - centreRows[index][key])))
  : Infinity;
check('the two medians separate enough here to tell the lines apart', separation > 0.5,
  `max |q50 - median| = ${separation.toFixed(3)}pp`);
check('the drawn centre line traces q50', !!centre && spread('q50') < 0.05,
  centre ? `max |drawn - q50| = ${spread('q50').toFixed(4)}` : `no centre line of ${centreRows.length} points`);
check('the drawn centre line is not the respondent-mean median',
  !!centre && spread('median') > separation / 2,
  centre ? `max |drawn - median| = ${spread('median').toFixed(4)}, separation ${separation.toFixed(3)}` : 'no centre line');
// The end label prints one decimal, so it can only distinguish the two medians
// on a selection whose final round separates them there. US PRGDP next year,
// all rounds, ends 2026 Q3 at q50 1.965 against a respondent-mean median of 1.800.
await go('#view=fan&survey=us&variable=PRGDP&horizon=next_year&rounds=all');
const endRows = measures.filter(row => row.survey === 'us' && row.variable === 'PRGDP'
  && row.horizon_class === 'next_year').sort((a, b) => a.year - b.year || a.quarter - b.quarter);
const endOf = endRows.at(-1);
const oneDecimal = value => Number(value).toFixed(1);
const endText = [...window.document.querySelectorAll('#chart text')].map(node => node.textContent);
check('the two medians separate at one decimal in this final round',
  oneDecimal(endOf.q50) !== oneDecimal(endOf.median), `q50 ${oneDecimal(endOf.q50)} vs median ${oneDecimal(endOf.median)}`);
check('the end label reports q50, not the respondent-mean median',
  endText.some(text => text.startsWith(`${oneDecimal(endOf.q50)}%`))
    && !endText.some(text => text.startsWith(`${oneDecimal(endOf.median)}%`)),
  `q50=${oneDecimal(endOf.q50)} median=${oneDecimal(endOf.median)} labels=${JSON.stringify(endText.filter(t => t.includes('%')))}`);

// The end marker is placed from a value but labelled from another expression, so
// the printed text alone cannot tell where the dot sits. Invert its centre too.
// US PRPGDP next year has no ten-year overlay, so the fan draws exactly one
// endpoint marker, and its final round separates the two medians.
await go('#view=fan&survey=us&variable=PRPGDP&horizon=next_year&rounds=all');
const markerRows = measures.filter(row => row.survey === 'us' && row.variable === 'PRPGDP'
  && row.horizon_class === 'next_year').sort((a, b) => a.year - b.year || a.quarter - b.quarter);
const markerOf = markerRows.at(-1);
const axisTicks = [...window.document.querySelectorAll('#chart text')]
  .filter(node => node.getAttribute('text-anchor') === 'end')
  .map(node => ({ y: Number(node.getAttribute('y')) - 4, value: Number.parseFloat(node.textContent) }));
const markers = [...window.document.querySelectorAll('#chart circle')]
  .filter(node => node.getAttribute('r') === '3.5');
const toValue = y => axisTicks[0].value
  + (y - axisTicks[0].y) * (axisTicks.at(-1).value - axisTicks[0].value) / (axisTicks.at(-1).y - axisTicks[0].y);
const markerValue = markers.length === 1 ? toValue(Number(markers[0].getAttribute('cy'))) : NaN;
check('the fan draws exactly one end marker here', markers.length === 1, `${markers.length} markers`);
check('the end marker sits on q50, not the respondent-mean median',
  Math.abs(markerValue - markerOf.q50) < 0.02 && Math.abs(markerValue - markerOf.median) > 0.05,
  `marker ${markerValue.toFixed(3)} vs q50 ${markerOf.q50} / median ${markerOf.median}`);

// The decomposition IQR table sat a respondent-mean median between pooled quartiles.
await go('#view=decomposition&survey=us&variable=PRGDP&horizon=next_year&rounds=q1&measure=iqr');
const iqrHeaders = [...[...window.document.querySelectorAll('#table tr')][0].children].map(cell => cell.textContent);
const iqrCells = [...[...window.document.querySelectorAll('#table tr')][1].children].map(cell => cell.textContent);
const iqrFirst = fanRows[0];
check('the IQR table names its median "Pooled median"', iqrHeaders.includes('Pooled median'), iqrHeaders.join(' | '));
check('the IQR table\'s median column holds q50',
  iqrCells[iqrHeaders.indexOf('Pooled median')] === fmt(iqrFirst.q50),
  `${iqrCells[iqrHeaders.indexOf('Pooled median')]} vs q50 ${fmt(iqrFirst.q50)}`);

section('hostile fragments and an exhaustive render sweep');
for (const bad of ['', '#', '#view=', '#view=nonesuch', '#view=__proto__', '#view=constructor',
                   '#view=toString', '#survey=nope&variable=nope&horizon=nope', '#%%%', '#view=fan&view=scores']) {
  await go(bad);
  const view = selectedTab()?.dataset.view;
  check(`fragment ${JSON.stringify(bad.slice(0, 24))} leaves a renderable view selected`,
    !!view && !!window.document.querySelector(`#tabs button[data-view="${view}"]`) && title().length > 0 && rovingIsCoherent(),
    `view=${view} title=${title()}`);
}
const combos = [...new Set(measures.map(row => `${row.survey}|${row.variable}|${row.horizon_class}`))];
let swept = 0;
const problems = [];
for (const view of ['decomposition', 'fan', 'calibration', 'term', 'scores']) {
  for (const combo of combos) {
    const [survey, variable, horizon] = combo.split('|');
    for (const rounds of ['q1', 'all']) {
      await go(`#view=${view}&survey=${survey}&variable=${variable}&horizon=${horizon}&rounds=${rounds}&measure=sd`);
      swept += 1;
      if (!title()) problems.push(`empty title: ${view} ${combo} ${rounds}`);
      if (/undefined|NaN/.test(title() + note())) problems.push(`undefined/NaN: ${view} ${combo} ${rounds}`);
      // A raw concept id would reach the reader with underscores intact.
      if (/_/.test(note())) problems.push(`raw identifier in note: ${view} ${combo} ${rounds} :: ${note().slice(0, 120)}`);
    }
  }
}
check(`${swept} view x selection combinations render cleanly`, problems.length === 0, problems.slice(0, 5).join('\n         '));
check('no uncaught page errors during the sweep', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | '));

section('the ECB longer-term duplicate-round collapse stays coherent');
await go('#view=fan&survey=ecb&variable=rgdp&horizon=longer_term&rounds=all');
const collapsed = [...window.document.querySelectorAll('#table tr')].slice(1)
  .map(row => [...row.children].map(cell => Number(cell.textContent)))
  .filter(row => row.slice(1, 4).every(Number.isFinite));
check('collapsed rounds render a table', collapsed.length > 0, `${collapsed.length} rows`);
check('the pooled median lies inside pooled q25-q75 on every collapsed round',
  collapsed.every(([, median, q25, q75]) => q25 <= median + 1e-9 && median <= q75 + 1e-9),
  JSON.stringify(collapsed.filter(([, m, a, b]) => !(a <= m + 1e-9 && m <= b + 1e-9)).slice(0, 3)));

console.log(`\n${failures ? `${failures} of ${checks} checks FAILED` : `all ${checks} checks passed`}`);
process.exit(failures ? 1 : 0);
