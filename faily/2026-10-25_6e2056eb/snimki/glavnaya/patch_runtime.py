p = '/root/eldamo_phr/app/runtime.js'
s = open(p).read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new)


rep('''"use strict";
(function () {
const DATA = JSON.parse(document.getElementById('atlas-data').textContent);''', '''"use strict";
// The phonetic reference of Quettamin: sound paths, rules, chains of changes and
// Eldamo's derivations of one branch and conception. Three collapsed sections;
// the data are parsed and drawn only when a section is first opened.
(function () {
const QR = window.QR;
let DATA = null;
const data = () => DATA || (DATA = JSON.parse(document.getElementById('atlas-data').textContent));''')
rep('''const GRADE = DATA.grades || {''', '''const GRADE = {''')
rep('''const THEME_KEY = 'eldamo-atlas-theme';''', '''const THEME_KEY = 'quettamin-theme';''')
rep('''  const B = DATA.branches[name];''', '''  const B = data().branches[name];''')
start = s.index('// ---------- state & routing')
end = s.index('// ---------- sound pickers')
s = s[:start] + '''// ---------- state & routing -------------------------------------------------
const BRANCHES = QR.BRANCHES;
const SECTIONS = { paths: 'ref-paths', rule: 'ref-paths', chains: 'ref-chains', derivations: 'ref-derivations' };
const state = { branch: 'quenya', era: 'late', sel: {}, mode: { from: 'phoneme', to: 'phoneme' }, chainPage: 0, derivPage: 0, drawn: {}, ref: '' };
function writeHash(push) {
  const sel = state.sel[state.branch] || {};
  QR.set({ b: state.branch, era: state.era, from: sel.from, to: sel.to }, push);
}
function ensureSel() {
  const X = index(state.branch);
  if (!state.sel[state.branch]) state.sel[state.branch] = { ...X.B.defaults };
  return X;
}
function route(params) {
  const b = BRANCHES.includes(params.get('b')) ? params.get('b') : state.branch;
  const era = ERAS.includes(params.get('era')) ? params.get('era') : state.era;
  const changed = b !== state.branch || era !== state.era;
  if (b !== state.branch) { state.chainPage = 0; state.derivPage = 0; }
  state.branch = b; state.era = era;
  branchSelect.value = b; $('era-select').value = era;
  const ref = params.get('ref') || '';
  const refKey = ref ? params.toString() : '';
  if (ref && refKey !== state.ref) {
    // an address into the reference: open the section with these parameters
    const X = ensureSel();
    for (const slot of ['from', 'to']) if (params.get(slot)) state.sel[b][slot] = params.get(slot);
    for (const slot of ['from', 'to']) state.mode[slot] = X.phonemes.has(state.sel[b][slot]) ? 'phoneme' : 'cluster';
    if (ref === 'derivations' && params.get('q') != null) { $('deriv-query').value = params.get('q'); state.derivPage = 0; }
    const sec = $(SECTIONS[ref] || 'ref-paths');
    const fresh = state.ref === '' || state.ref.split('&').find(x => x.startsWith('ref=')) !== 'ref=' + ref
      || params.get('id') !== new URLSearchParams(state.ref).get('id') || params.get('q') !== new URLSearchParams(state.ref).get('q');
    state.ref = refKey;
    if (fresh || changed) {
      state.drawn = {};
      sec.open = true;
      renderOpen();
      if (ref === 'rule' && params.get('id')) showRule(params.get('id'));
      sec.scrollIntoView({ block: 'start' });
    }
  } else if (changed) {
    state.drawn = {};
    renderOpen();
  }
  if (!ref) state.ref = '';
}

// ---------- reference header --------------------------------------------------------
const branchSelect = $('branch-select');
branchSelect.replaceChildren(...BRANCHES.map(k => new Option(k === 'quenya' ? 'квенья' : 'синдарин', k)));
branchSelect.addEventListener('change', () => { state.branch = branchSelect.value; state.chainPage = 0; state.derivPage = 0; state.drawn = {}; writeHash(true); renderOpen(); });
$('era-select').addEventListener('change', e => { state.era = e.target.value; state.drawn = {}; writeHash(false); renderOpen(); });
const refSections = () => [$('ref-paths'), $('ref-chains'), $('ref-derivations')];
function updateToggleAll() {
  const allOpen = refSections().every(d => d.open);
  $('ref-toggle-all').textContent = allOpen ? 'Свернуть всё' : 'Развернуть всё';
  $('ref-toggle-all').setAttribute('aria-expanded', String(allOpen));
}
$('ref-toggle-all').addEventListener('click', () => {
  const open = !refSections().every(d => d.open);
  for (const d of refSections()) d.open = open;
});
for (const d of refSections()) d.addEventListener('toggle', () => { updateToggleAll(); if (d.open) renderOpen(); });

// draw the open sections that are not drawn for the current branch and conception
function renderOpen() {
  const key = state.branch + '|' + state.era;
  if ($('ref-paths').open && state.drawn.paths !== key) {
    state.drawn.paths = key;
    const X = ensureSel();
    for (const slot of ['from', 'to']) state.mode[slot] = X.phonemes.has(state.sel[state.branch][slot]) ? 'phoneme' : 'cluster';
    $('branch-path').textContent = `${X.B.title}: ${X.B.path[state.era]}. Правил: ${X.B.stats.rules}, переходов в графе: ${X.B.stats.edges}, формулы воспроизводят ${Math.round(100 * X.B.stats.reproduction_rate)}% засвидетельствованных шагов.`;
    for (const slot of ['from', 'to']) renderPicker(slot);
    $('output').innerHTML = '';
    findPaths();
  }
  if ($('ref-chains').open && state.drawn.chains !== key) { state.drawn.chains = key; renderChains(); }
  if ($('ref-derivations').open && state.drawn.derivations !== key) { state.drawn.derivations = key; renderDerivs(); }
}

''' + s[end:]
rep('''function current(slot) { return state.sel[state.branch][slot]; }''', '''function current(slot) { ensureSel(); return state.sel[state.branch][slot]; }''')
rep('''  if (/^id:/.test(raw)) {
    const id = raw.slice(3).trim();
    list = X.B.derivs.filter(d => d.id === id);
  } else {''', '''  if (/^id:/.test(raw)) {
    const id = raw.slice(3).trim();
    list = X.B.derivs.filter(d => d.id === id);
  } else if (/^w:/.test(raw)) {
    const id = raw.slice(2).trim();
    list = X.B.derivs.filter(d => d.w === id && (showDeleted || !d.del));
  } else {''')
rep('''· <a href="${esc(wordUrl(d.w))}" target="_blank" rel="noopener">статья Eldamo</a></p>''', '''· <a href="${esc(wordUrl(d.w))}" target="_blank" rel="noopener">статья Eldamo</a>${d.w ? ` · <a href="#" data-word="${esc(d.w)}" data-branch="${esc(state.branch)}">открыть слово</a>` : ''}</p>''')
rep('''function ruleLink(X, id) {
  const r = X.B.rules[id];
  return `<a href="${esc(wordUrl(id))}" target="_blank" rel="noopener">${esc(r ? r.n : id)}</a>`;
}''', '''function ruleLink(X, id) {
  const r = X.B.rules[id];
  return `<a href="#" data-rule="${esc(id)}" data-branch="${esc(X.name)}">${esc(r ? r.n : id)}</a> <a href="${esc(wordUrl(id))}" target="_blank" rel="noopener" class="ext" title="Статья Eldamo" aria-label="Статья Eldamo">↗</a>`;
}''')
rep('''    if (kind === 'chain') { state.chainPage = Number(n); renderChains(); $('chains-title').scrollIntoView({ block: 'start' }); }
    else { state.derivPage = Number(n); renderDerivs(); $('derivs-title').scrollIntoView({ block: 'start' }); }''', '''    if (kind === 'chain') { state.chainPage = Number(n); renderChains(); $('ref-chains').scrollIntoView({ block: 'start' }); }
    else { state.derivPage = Number(n); renderDerivs(); $('ref-derivations').scrollIntoView({ block: 'start' }); }''')
rep('''  const d = e.target.closest('[data-deriv]');
  if (d) {
    e.preventDefault();
    $('deriv-query').value = 'id:' + d.dataset.deriv;
    state.derivPage = 0; renderDerivs();
    $('derivations-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

route();
})();''', '''  const d = e.target.closest('[data-deriv]');
  if (d) {
    e.preventDefault();
    $('deriv-query').value = 'id:' + d.dataset.deriv;
    state.derivPage = 0;
    $('ref-derivations').open = true;
    state.drawn.derivations = state.branch + '|' + state.era;
    renderDerivs();
    $('ref-derivations').scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }
  const r = e.target.closest('[data-rule]');
  if (r) {
    e.preventDefault();
    QR.set({ ref: 'rule', id: r.dataset.rule, b: r.dataset.branch || state.branch, q: null }, true);
    return;
  }
  const w = e.target.closest('[data-ref-derivations]');
  if (w) {
    e.preventDefault();
    QR.set({ ref: 'derivations', id: null, q: 'w:' + w.dataset.refDerivations, b: w.dataset.branch || state.branch }, true);
  }
});

// ---------- one rule --------------------------------------------------------------
function showRule(id) {
  let X = index(state.branch);
  if (!X.B.rules[id]) {
    const other = BRANCHES.find(b => data().branches[b].rules[id]);
    if (!other) { $('output').innerHTML = `<div class="empty">Правила ${esc(id)} в справочнике нет.</div>`; return; }
    state.branch = other; branchSelect.value = other; X = index(other);
  }
  const r = X.B.rules[id];
  const lang = X.lang[r.l];
  if ((lang && lang.era !== state.era) || state.drawn.paths !== state.branch + '|' + state.era) {
    if (lang) { state.era = lang.era; $('era-select').value = lang.era; }
    state.drawn = {};
    $('ref-paths').open = true;
    renderOpen();
    QR.set({ b: state.branch, era: state.era }, false);
  }
  const pairs = Object.entries(X.B.pairs).filter(([, p]) => p.r === id);
  const seen = new Set(), words = [];
  for (const [pid] of pairs) for (const [di, si] of X.occ.get(pid) || []) {
    const dv = X.B.derivs[di];
    if (seen.has(dv.id)) continue;
    seen.add(dv.id);
    const s = dv.steps[si], before = si === 0 ? dv.st : dv.steps[si - 1][4];
    words.push(`<li><a href="#" data-deriv="${esc(dv.id)}">${esc(dv.wf || dv.f)}</a> <span class="form">${esc(before)} → ${esc(s[4])}</span></li>`);
  }
  const before = r.b.map(t => X.B.rules[t] ? ruleLink(X, t) : esc(t));
  $('output').innerHTML = `<div class="result-head rule-view"><strong>Правило</strong> · ${esc(lang ? lang.marker + ' ' + (X.B.language_names[r.l] || '') : r.l)}${r.o != null ? ` · порядок ${r.o}` : ''}</div>
    <h3 class="rule-title">${esc(r.n)} <a href="${esc(wordUrl(id))}" target="_blank" rel="noopener" class="small">статья Eldamo ↗</a></h3>
    ${r.f ? `<p>Формула: <code>${esc(r.f[0])} &gt; ${esc(r.f[1])}</code></p>` : ''}
    ${pairs.length ? `<div class="table-scroll"><table class="data"><thead><tr><th>Подформула</th><th>Примеры / воспроизведено</th></tr></thead><tbody>${pairs.map(([, p]) =>
      `<tr><td><code>${esc(p.f)} &gt; ${esc(p.t)}</code>${p.k === 'contextual' ? ' <span class="small muted">контекстная, вне графа</span>' : ''}</td><td>${p.e ? `${p.e} / ${p.ok}` : '—'}</td></tr>`).join('')}</tbody></table></div>` : ''}
    ${before.length ? `<p class="small">Раньше правил: ${before.join('; ')}</p>` : ''}
    ${words.length ? `<p>Засвидетельствовано в деривациях (${words.length}):</p><ol class="steps">${words.slice(0, 40).join('')}</ol>${words.length > 40 ? '<p class="small muted">…</p>' : ''}`
      : '<p class="muted">Воспроизведённых примеров в деривациях нет.</p>'}`;
}

QR.on(route);
window.QREF = { start: () => { route(QR.get()); updateToggleAll(); } };
})();''')
open(p, 'w').write(s)
