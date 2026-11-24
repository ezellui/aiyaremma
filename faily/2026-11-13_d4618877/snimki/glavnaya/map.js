/* map.js — карта «Трактата»: радиальное дерево, площадь круга ~ число потомков;
   по желанию — ссылки между положениями (номера в текстах и комментариях) дугами. */
"use strict";
let MAP_REFS = store.get('maprefs', '1') === '1';
function showMap(at) {
  if (at) CUR = at;
  markNav();
  const roots = NUMS.filter(n => !D.props[n].parent);
  const W = 1200, H = 1200, cx = W / 2, cy = H / 2;
  const leaves = {};
  NUMS.slice().reverse().forEach(n => { const k = CHILDREN(n); leaves[n] = k.length ? k.reduce((s, c) => s + leaves[c], 0) : 1; });
  roots.forEach(r => { leaves[r] = Math.max(leaves[r], 24); });   // корням — место для подписи
  const total = roots.reduce((s, r) => s + leaves[r], 0);
  const pos = {};
  const place = (n, a0, depth) => {
    const span = leaves[n] / total * Math.PI * 2;
    const a = a0 + span / 2, r = 70 + depth * 92;
    pos[n] = [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    let s = a0; CHILDREN(n).forEach(c => { place(c, s, depth + 1); s += leaves[c] / total * Math.PI * 2; });
  };
  let acc = 0;
  roots.forEach(r => { place(r, acc, 0); acc += leaves[r] / total * Math.PI * 2; });
  let lines = '', refs = '', dots = '', labels = '';
  const f = v => v.toFixed(1);
  NUMS.forEach(n => {
    const p = D.props[n].parent, [x, y] = pos[n];
    if (p) lines += `<line x1="${f(pos[p][0])}" y1="${f(pos[p][1])}" x2="${f(x)}" y2="${f(y)}" stroke="var(--rule)" stroke-width="1"/>`;
    if (MAP_REFS) (D.props[n].refs || []).forEach(r => {
      const [x2, y2] = pos[r];
      // дуга через точку, сдвинутую к центру — чтобы ссылки не сливались с ветвями дерева
      const mx = (x + x2) / 2, my = (y + y2) / 2, qx = mx + (cx - mx) * .45, qy = my + (cy - my) * .45;
      refs += `<path class="ref" d="M${f(x)},${f(y)} Q${f(qx)},${f(qy)} ${f(x2)},${f(y2)}"><title>${n} → ${r}</title></path>`;
    });
    const rad = 2.2 + Math.sqrt(DESC[n]) * 2.1;
    dots += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(rad)}" fill="${n === CUR ? 'var(--mark-cur)' : 'var(--brass)'}" ${n === CUR ? 'class="hl"' : ''} fill-opacity="${D.props[n].parent ? .75 : 1}" data-n="${n}"><title>${n} ${esc(firstLine(n, lead()))}</title></circle>`;
    if (!D.props[n].parent || DESC[n] >= 8 || n === CUR) labels += `<text x="${f(x + rad + 2)}" y="${f(y + 4)}" font-size="${D.props[n].parent ? 11 : 16}" fill="var(--ink)">${n}</text>`;
  });
  const nrefs = NUMS.reduce((s, n) => s + (D.props[n].refs || []).length, 0);
  view.innerHTML = `<div class="page map"><h2>${t('map.title')}</h2><div class="tree-note">${t('map.note')}</div>
    <div class="ctl"><label><input type="checkbox" id="maprefs" ${MAP_REFS ? 'checked' : ''}> ${esc(t('map.refs', {n: nrefs}))}</label></div>
    <svg viewBox="0 0 ${W} ${H}">${lines}${refs}${dots}${labels}</svg></div>`;
  view.querySelector('svg').addEventListener('click', e => { const n = e.target.dataset && e.target.dataset.n; if (n) location.hash = '#/p/' + n; });
  $('#maprefs').onchange = e => { MAP_REFS = e.target.checked; store.set('maprefs', MAP_REFS ? '1' : '0'); showMap(at); };
  view.scrollTop = 0;
}
