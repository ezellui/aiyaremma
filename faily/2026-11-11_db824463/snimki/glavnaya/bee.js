/* Wittgenstein's Nachlass (BEE) — page behaviour: interface language, switches, view settings,
   search hits and colour filters, page jump, own work (bookmarks, highlights, notes) kept in the
   browser (localStorage) with export/import. Works from file:// without a server. */
(function () {
  'use strict';
  var LS = {
    get: function (k, d) { try { var v = localStorage.getItem('bee.' + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('bee.' + k, JSON.stringify(v)); } catch (e) { } }
  };
  var I = window.BEE_I18N || { langs: ['de'], strings: {} };
  function pickLang() {
    var l = LS.get('lang', null); if (l && I.langs.indexOf(l) >= 0) return l;
    var n = (navigator.language || 'de').slice(0, 2); return I.langs.indexOf(n) >= 0 ? n : 'de';
  }
  var LANG = pickLang();
  function t(key, vars) {
    var s = I.strings[key]; var v = s ? (s[LANG] || s.de || s.en || key) : key;
    if (vars) Object.keys(vars).forEach(function (k) { v = v.replace('{' + k + '}', vars[k]); });
    return v;
  }
  window.BEE = { t: t, LS: LS, lang: function () { return LANG; } };
  function applyI18n(root) {
    root = root || document;
    root.querySelectorAll('[data-i18n]').forEach(function (e) { var s = I.strings[e.dataset.i18n]; if (s) e.textContent = t(e.dataset.i18n); });
    root.querySelectorAll('[data-i18n-title]').forEach(function (e) { if (I.strings[e.dataset.i18nTitle]) e.title = t(e.dataset.i18nTitle); });
    root.querySelectorAll('[data-i18n-placeholder]').forEach(function (e) { if (I.strings[e.dataset.i18nPlaceholder]) e.placeholder = t(e.dataset.i18nPlaceholder); });
    document.documentElement.lang = LANG;
  }
  window.BEE.applyI18n = applyI18n;
  var B = document.body, ROOT = B.dataset.root || '';

  /* ---- language switch */
  var ls = document.querySelector('.langs');
  if (ls) I.langs.forEach(function (l) {
    var b = document.createElement('button'); b.textContent = l.toUpperCase(); b.type = 'button';
    if (l === LANG) b.className = 'on';
    b.onclick = function () { LS.set('lang', l); LANG = l; ls.querySelectorAll('button').forEach(function (x) { x.className = x === b ? 'on' : ''; }); applyI18n(); document.dispatchEvent(new Event('bee-lang')); };
    ls.appendChild(b);
  });
  applyI18n();

  /* ---- switches (body classes), remembered */
  document.querySelectorAll('[data-toggle]').forEach(function (c) {
    var k = c.dataset.toggle; c.checked = !!LS.get('toggle.' + k, false); B.classList.toggle(k, c.checked);
    c.addEventListener('change', function () { B.classList.toggle(k, c.checked); LS.set('toggle.' + k, c.checked); });
  });

  /* ---- view settings panel */
  var FONTS = { georgia: "Georgia,'Times New Roman',serif", palatino: "'Palatino Linotype',Palatino,'Book Antiqua',serif", times: "'Times New Roman',Times,serif", sans: 'system-ui,sans-serif' };
  var view = LS.get('view', { font: 'georgia', size: 17, lh: 1.6, justify: false, wide: false, filters: ['', '', '', ''] });
  function applyView() {
    var r = document.documentElement.style;
    r.setProperty('--text-font', FONTS[view.font] || FONTS.georgia); r.setProperty('--text-size', view.size + 'px'); r.setProperty('--lh', view.lh);
    B.classList.toggle('justify', !!view.justify); B.classList.toggle('wide', !!view.wide);
  }
  applyView();
  var vb = document.querySelector('.viewbtn');
  if (vb) {
    var p = document.createElement('div'); p.className = 'panel'; p.id = 'viewpanel';
    p.innerHTML = '<h3 data-i18n="view.title">Ansicht</h3>' +
      '<div class="row"><span data-i18n="view.font">Schrift</span>: <select id="v-font"><option value="georgia">Georgia</option><option value="palatino">Palatino</option><option value="times">Times</option><option value="sans">sans-serif</option></select></div>' +
      '<div class="row"><span data-i18n="view.size">Größe</span>: <input id="v-size" type="range" min="13" max="24" step="1"> <span id="v-size-n"></span></div>' +
      '<div class="row"><span data-i18n="view.lh">Zeilenabstand</span>: <input id="v-lh" type="range" min="1.2" max="2.2" step="0.1"></div>' +
      '<div class="row"><label><input type="checkbox" id="v-just"> <span data-i18n="view.justify">Blocksatz</span></label> <label><input type="checkbox" id="v-wide"> <span data-i18n="view.wide">breiter Satzspiegel</span></label></div>' +
      '<h3 data-i18n="view.filters">Farbfilter</h3><div class="row" data-i18n="view.filterhint">Bis zu vier Wörter, Masken (wort*) oder Wendungen; sie werden auf jeder Seite farbig markiert.</div>' +
      [0, 1, 2, 3].map(function (i) { return '<div class="row"><mark class="f' + (i + 1) + '">&nbsp;&nbsp;</mark> <input class="v-f" data-i="' + i + '" size="24"> <span class="v-fn" data-i="' + i + '"></span></div>'; }).join('') +
      '<div class="row"><button type="button" id="v-print" data-i18n="view.print">Drucken</button> <button type="button" id="v-close" data-i18n="view.close">Schließen</button></div>';
    document.body.appendChild(p); applyI18n(p);
    var $ = function (id) { return document.getElementById(id); };
    $('v-font').value = view.font; $('v-size').value = view.size; $('v-size-n').textContent = view.size + ' px'; $('v-lh').value = view.lh; $('v-just').checked = view.justify; $('v-wide').checked = view.wide;
    p.querySelectorAll('.v-f').forEach(function (e) { e.value = view.filters[+e.dataset.i] || ''; });
    function save() { LS.set('view', view); applyView(); }
    $('v-font').onchange = function () { view.font = this.value; save(); };
    $('v-size').oninput = function () { view.size = +this.value; $('v-size-n').textContent = view.size + ' px'; save(); };
    $('v-lh').oninput = function () { view.lh = +this.value; save(); };
    $('v-just').onchange = function () { view.justify = this.checked; save(); };
    $('v-wide').onchange = function () { view.wide = this.checked; save(); };
    p.querySelectorAll('.v-f').forEach(function (e) { e.onchange = function () { view.filters[+e.dataset.i] = e.value.trim(); save(); applyFilters(); }; });
    $('v-print').onclick = function () { window.print(); };
    $('v-close').onclick = function () { p.classList.remove('open'); };
    vb.onclick = function () { p.classList.toggle('open'); };
  }

  /* ---- matching: words, word*, w?rd, "phrases"; case, accents and ß/ss ignored */
  var CLS = { a: '[aäáàâ]', o: '[oöóòô]', u: '[uüúùû]', e: '[eéèê]', i: '[iíìî]', c: '[cç]', n: '[nñ]', y: '[yý]' };
  function termRe(w) {
    var pre = /\*$/.test(w); w = w.toLowerCase().replace(/\*$/, '');
    var s = '';
    for (var i = 0; i < w.length; i++) {
      var ch = w[i];
      if (ch === '?') { s += '[\\p{L}\\p{N}]'; continue; }
      if (ch === '*') { s += '[\\p{L}\\p{N}]*'; continue; }
      if (ch === 's' && w[i + 1] === 's') { s += '(?:ss|ß)'; i++; continue; }
      if (ch === 'ß') { s += '(?:ss|ß)'; continue; }
      if (/\s/.test(ch)) { s += '[\\s\\u00a0]+'; continue; }
      var base = ch.normalize('NFD').replace(/[̀-ͯ]/g, '');
      s += CLS[base] || base.replace(/[.+^${}()|[\]\\]/g, '\\$&');
    }
    return s + (pre ? '[\\p{L}\\p{N}]*' : '');
  }
  function queryTerms(q) {
    var out = [], m, re = /"([^"]+)"|(\S+)/g;
    while ((m = re.exec(q))) {
      var x = m[1] || m[2];
      if (!m[1] && (/^(OR|ODER|AND|UND|NOT|NICHT|NEAR|NAHE)(\/\d+)?$/i.test(x) || /^-/.test(x))) continue;
      x = x.replace(/^[(+]+|[)]+$/g, '').replace(/^[a-z]+:/i, '');
      if (x.replace(/[*?]/g, '').length >= 1) out.push(x);
    }
    return out;
  }
  function buildRe(terms) {
    if (!terms.length) return null;
    return new RegExp('(?<![\\p{L}\\p{N}])(?:' + terms.map(termRe).join('|') + ')(?![\\p{L}\\p{N}])', 'giu');
  }
  window.BEE.buildRe = buildRe; window.BEE.queryTerms = queryTerms;
  function markIn(el, re, cls) {
    var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: function (n) { return n.parentNode.closest('mark,script,style,.person,.notation,.meta') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; } });
    var nodes = [], x, n = 0; while ((x = w.nextNode())) nodes.push(x);
    nodes.forEach(function (tn) {
      var s = tn.nodeValue, m, last = 0, frag = null; re.lastIndex = 0;
      while ((m = re.exec(s))) {
        if (!m[0]) { re.lastIndex++; continue; }
        frag = frag || document.createDocumentFragment();
        frag.appendChild(document.createTextNode(s.slice(last, m.index)));
        var mk = document.createElement('mark'); if (cls) mk.className = cls; mk.textContent = m[0]; frag.appendChild(mk);
        last = m.index + m[0].length; n++;
      }
      if (frag) { frag.appendChild(document.createTextNode(s.slice(last))); tn.parentNode.replaceChild(frag, tn); }
    });
    return n;
  }
  var main = document.querySelector('main');
  function applyFilters() {
    if (!main) return;
    main.querySelectorAll('mark.f1,mark.f2,mark.f3,mark.f4').forEach(function (m) { m.replaceWith(document.createTextNode(m.textContent)); });
    main.normalize();
    (view.filters || []).forEach(function (f, i) {
      var cnt = 0;
      if (f) { var re = buildRe(queryTerms(f)); if (re) cnt = markIn(main, re, 'f' + (i + 1)); }
      var s = document.querySelector('.v-fn[data-i="' + i + '"]'); if (s) s.textContent = f ? cnt : '';
    });
  }
  if (B.dataset.kind && B.dataset.kind !== 'search') applyFilters();

  /* ---- hits from the search page (?q=… #anchor) */
  var q = new URLSearchParams(location.search).get('q');
  var hits = [], cur = -1;
  function collectHits() { hits = Array.prototype.slice.call(main.querySelectorAll('mark:not([class])')); }
  function go(i) {
    if (!hits.length) return;
    if (cur >= 0 && hits[cur]) hits[cur].classList.remove('cur');
    cur = (i + hits.length) % hits.length; hits[cur].classList.add('cur'); hits[cur].scrollIntoView({ block: 'center' });
    var pos = document.querySelector('.hitpos'); if (pos) pos.textContent = (cur + 1) + ' / ' + hits.length;
  }
  if (q && main) {
    var re = buildRe(queryTerms(q));
    var target = location.hash ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null;
    var scope = [];
    if (target && target.classList.contains('rec')) scope = [target];
    else if (target) { var pp = target.closest('p') || target; for (var k = 0; pp && k < 40; k++, pp = pp.nextElementSibling) scope.push(pp); }
    else scope = [main];
    if (re) scope.forEach(function (el) { markIn(el, re, ''); });
    collectHits();
    if (hits.length) { B.classList.add('has-hits'); go(0); }
    var all = document.querySelector('.hitall');
    if (all) all.onclick = function () { markIn(main, re, ''); collectHits(); go(Math.max(0, hits.indexOf(document.querySelector('mark.cur')))); all.disabled = true; };
    var bn = document.querySelector('.hitnext'), bp = document.querySelector('.hitprev');
    if (bn) bn.onclick = function () { go(cur + 1); }; if (bp) bp.onclick = function () { go(cur - 1); };
  }
  document.addEventListener('keydown', function (e) {
    if (/INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName)) return;
    if (e.key === 'n' && hits.length) { go(cur + 1); e.preventDefault(); }
    else if (e.key === 'N' && hits.length) { go(cur - 1); e.preventDefault(); }
    else if (e.key === '/') { var s = document.querySelector('header.top input[type=search]'); if (s) { s.focus(); e.preventDefault(); } }
  });

  /* ---- go to page */
  var sel = document.querySelector('.gotopage');
  if (sel && main) {
    var pbs = main.querySelectorAll('.pb[id]');
    if (!pbs.length) sel.parentNode.style.display = 'none';
    var frag = document.createDocumentFragment(), o0 = document.createElement('option'); o0.textContent = '…'; frag.appendChild(o0);
    pbs.forEach(function (p) { var o = document.createElement('option'); o.value = p.id; o.textContent = p.textContent; frag.appendChild(o); });
    sel.appendChild(frag);
    sel.onchange = function () { var e = document.getElementById(sel.value); if (e) { e.scrollIntoView({ block: 'start' }); history.replaceState(null, '', '#' + sel.value); } };
  }

  /* ---- own work: bookmarks, highlights, notes */
  var PAGE = location.pathname.split('/').slice(-2).join('/');
  function where() {
    var best = null, y = 120;
    (main ? main.querySelectorAll('.pb[id],.rec[id],h2[id]') : []).forEach(function (e) { var r = e.getBoundingClientRect(); if (r.top < y + 60) best = e; });
    return best;
  }
  function label() {
    var h = document.querySelector('main h1'); return (h ? h.textContent : document.title);
  }
  var bm = document.querySelector('.bmbtn');
  if (bm) bm.onclick = function () {
    var w = where(), list = LS.get('bookmarks', []);
    var anchor = w ? w.id : '', pg = w && w.classList.contains('pb') ? w.textContent : (w && w.querySelector && w.querySelector('.meta') ? w.querySelector('.meta').textContent.split(/\s/)[0] : '');
    list.push({ href: PAGE + (anchor ? '#' + anchor : ''), title: label(), page: pg, ts: Date.now() });
    LS.set('bookmarks', list); bm.textContent = '★ ' + t('tb.bookmarked');
  };
  function source(node) {
    var rec = node && node.parentElement && node.parentElement.closest('.rec'), pbx = null;
    var all = main ? main.querySelectorAll('.pb[id]') : [];
    all.forEach(function (p) { if (node && (p.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING)) pbx = p; });
    return 'BEE, ' + label() + (pbx ? ', S. ' + pbx.textContent : '') + (rec && rec.querySelector('.meta') ? '' : '');
  }
  // highlights: text + 40 characters of context, re-found after a rebuild
  function applyHighlights() {
    if (!main) return;
    var list = LS.get('marks', []).filter(function (m) { return m.page === PAGE; });
    if (!list.length) return;
    var text = '', map = [], w = document.createTreeWalker(main, NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) { map.push([n, text.length]); text += n.nodeValue; }
    list.forEach(function (m) {
      var i = text.indexOf(m.before + m.text + m.after); var off = i >= 0 ? i + m.before.length : text.indexOf(m.text);
      if (off < 0) return;
      wrapRange(map, off, off + m.text.length, m);
    });
  }
  function wrapRange(map, a, b, m) {
    for (var k = 0; k < map.length; k++) {
      var node = map[k][0], st = map[k][1], en = st + node.nodeValue.length;
      if (en <= a || st >= b) continue;
      var s = Math.max(a, st) - st, e = Math.min(b, en) - st;
      var r = document.createRange(); r.setStart(node, s); r.setEnd(node, e);
      var sp = document.createElement('span'); sp.className = 'hl' + m.color; sp.dataset.id = m.id; sp.title = m.comment || '';
      try { r.surroundContents(sp); } catch (x) { }
    }
  }
  var bar = document.createElement('div'); bar.id = 'selbar';
  bar.innerHTML = [1, 2, 3, 4].map(function (c) { return '<button type="button" data-c="' + c + '"><span class="c hl' + c + '"></span></button>'; }).join('') +
    '<button type="button" data-a="note" title="">✎</button><button type="button" data-a="search" title="">⌕</button>';
  document.body.appendChild(bar);
  var lastRange = null;
  document.addEventListener('mouseup', function (e) {
    if (bar.contains(e.target)) return;
    setTimeout(function () {
      var s = window.getSelection();
      if (!main || !s.rangeCount || s.isCollapsed || !main.contains(s.anchorNode)) { bar.style.display = 'none'; return; }
      lastRange = s.getRangeAt(0).cloneRange();
      var r = lastRange.getBoundingClientRect();
      bar.querySelector('[data-a=note]').title = t('sel.note'); bar.querySelector('[data-a=search]').title = t('sel.search');
      bar.style.left = (window.scrollX + r.left) + 'px'; bar.style.top = (window.scrollY + r.top - 34) + 'px'; bar.style.display = 'block';
    }, 10);
  });
  bar.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b || !lastRange) return;
    var txt = lastRange.toString();
    if (b.dataset.c) {
      var full = main.textContent, pre = document.createRange(); pre.setStart(main, 0); pre.setEnd(lastRange.startContainer, lastRange.startOffset);
      var off = pre.toString().length;
      var m = { id: 'm' + Date.now(), page: PAGE, title: label(), text: txt, before: full.slice(Math.max(0, off - 40), off), after: full.slice(off + txt.length, off + txt.length + 40), color: +b.dataset.c, comment: '', ts: Date.now(), src: source(lastRange.startContainer) };
      var list = LS.get('marks', []); list.push(m); LS.set('marks', list);
      var sp = document.createElement('span'); sp.className = 'hl' + m.color; sp.dataset.id = m.id;
      try { lastRange.surroundContents(sp); } catch (x) { location.reload(); }
    } else if (b.dataset.a === 'note') {
      var notes = LS.get('notes', []); if (!notes.length) notes.push({ id: 'n' + Date.now(), text: '', ts: Date.now() });
      var cn = LS.get('curnote', notes[0].id), nt = notes.filter(function (x) { return x.id === cn; })[0] || notes[0];
      nt.text += (nt.text ? '\n\n' : '') + '„' + txt + '“ (' + source(lastRange.startContainer) + ')'; nt.ts = Date.now();
      LS.set('notes', notes); b.textContent = '✓'; setTimeout(function () { b.textContent = '✎'; }, 900);
    } else if (b.dataset.a === 'search') {
      location.href = ROOT + 'search.html?q=' + encodeURIComponent('"' + txt.trim() + '"');
    }
    bar.style.display = 'none'; window.getSelection().removeAllRanges();
  });
  document.addEventListener('click', function (e) {
    var h = e.target.closest('[class^=hl][data-id]'); if (!h || e.target.closest('#selbar')) return;
    var list = LS.get('marks', []), m = list.filter(function (x) { return x.id === h.dataset.id; })[0]; if (!m) return;
    var c = prompt(t('mark.comment'), m.comment || '');
    if (c === null) return;
    if (c === '-') { list = list.filter(function (x) { return x.id !== m.id; }); LS.set('marks', list); h.replaceWith(document.createTextNode(h.textContent)); return; }
    m.comment = c; h.title = c; LS.set('marks', list);
  });
  applyHighlights();

  /* ---- generic list filter (index, persons, fields) */
  document.querySelectorAll('input.filter[data-target]').forEach(function (inp) {
    var box = document.querySelector(inp.dataset.target);
    inp.addEventListener('input', function () {
      var v = inp.value.trim().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
      box.querySelectorAll('[data-k]').forEach(function (e) { e.style.display = !v || e.dataset.k.indexOf(v) >= 0 ? '' : 'none'; });
      if (v) box.querySelectorAll('details').forEach(function (d) { d.open = true; });
    });
  });
})();
