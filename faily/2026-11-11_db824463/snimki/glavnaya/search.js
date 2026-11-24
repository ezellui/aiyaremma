/* Wittgenstein's Nachlass (BEE) — search page.
   Query language (as in the edition's Folio query and the HWPh reader):
     word word        both in one unit (record / page)          word OR word   either (also ODER, |)
     -word, NOT word  without                                   word*  w?rd  *word*   masks
     "a phrase"       the exact sequence                        a NEAR b, a NEAR/5 b   at most n words apart
     ( … )            grouping                                  field:word   person: lang_en: lang_fr: lang_la:
                                                                             coded: notation: xref: title:
   The index gives the candidate units; phrases and NEAR are checked on the units' text. */
(function () {
  'use strict';
  var t = BEE.t, LS = BEE.LS, ROOT = '';
  var UNITS = null, ITEMS = null, SERIES = null, FCOUNT = null, IX = {}, FX = {}, TX = {}, wait = {};
  window.BEEUNITS = function (u, it, se, fc) { UNITS = u; ITEMS = it; SERIES = se; FCOUNT = fc; };
  window.BEEIX = function (k, d) { IX[k] = d; done('ix_' + k); };
  window.BEEFX = function (k, d) { FX[k] = d; done('fx_' + k); };
  window.BEETX = function (k, first, arr) { TX[k] = { first: first, t: arr }; done('tx_' + k); };
  function done(k) { (wait[k] || []).forEach(function (f) { f(); }); delete wait[k]; }
  function load(name, src, ready) {
    if (ready()) return Promise.resolve();
    return new Promise(function (res) {
      if (wait[name]) { wait[name].push(res); return; }
      wait[name] = [res];
      var s = document.createElement('script'); s.src = src; s.onerror = function () { done(name); };
      document.head.appendChild(s);
    });
  }
  function shard(k) { return load('ix_' + k, 'search/ix_' + k + '.js', function () { return !!IX[k]; }).then(function () { IX[k] = IX[k] || {}; return IX[k]; }); }
  function field(f) { return load('fx_' + f, 'search/fx_' + f + '.js', function () { return !!FX[f]; }).then(function () { FX[f] = FX[f] || {}; return FX[f]; }); }
  function text(key) { return load('tx_' + key, 'search/tx/' + key + '.js', function () { return !!TX[key]; }); }
  function fold(w) { return w.toLowerCase().replace(/ß/g, 'ss').normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function skey(w) { var k = w.slice(0, 2).replace(/[^a-z0-9]/g, '_'); while (k.length < 2) k += '_'; return k; }
  function decode(s) { var o = [], p = 0; if (!s) return o; s.split(',').forEach(function (x) { p += parseInt(x, 36); o.push(p); }); return o; }
  var FIELDS = ['person', 'lang_en', 'lang_fr', 'lang_la', 'coded', 'notation', 'xref', 'title'];

  /* ---- parser: OR binds tighter than the blank (AND), as in Folio and HWPh */
  function tokenize(q) {
    var out = [], re = /\s*(\(|\)|"[^"]*"|[^\s()"]+)/g, m;
    while ((m = re.exec(q))) out.push(m[1]);
    return out;
  }
  function parse(q, deffield) {
    var tk = tokenize(q), i = 0;
    function peek() { return tk[i]; }
    function isOr(x) { return x && /^(OR|ODER|\|)$/i.test(x); }
    function isNot(x) { return x && /^(NOT|NICHT)$/i.test(x); }
    function isAnd(x) { return x && /^(AND|UND|&)$/i.test(x); }
    function nearOp(x) { var m = x && /^(NEAR|NAHE)(?:\/(\d+))?$/i.exec(x); return m ? +(m[2] || 20) : 0; }
    function atom() {
      var x = tk[i++]; if (x === undefined) return null;
      if (x === '(') { var e = andExpr(); if (peek() === ')') i++; return e; }
      var neg = false;
      if (isNot(x)) { neg = true; x = tk[i++]; } else if (/^-./.test(x)) { neg = true; x = x.slice(1); }
      if (x === '(') { var g = andExpr(); if (peek() === ')') i++; return neg ? { op: 'not', a: g } : g; }
      var fld = deffield, m = /^([a-z_]+):(.+)$/i.exec(x);
      if (m && FIELDS.indexOf(m[1].toLowerCase()) >= 0) { fld = m[1].toLowerCase(); x = m[2]; }
      var node;
      if (/^".*"$/.test(x)) {
        var ws = x.slice(1, -1).split(/[^\p{L}\p{N}*?]+/u).filter(Boolean);
        node = ws.length > 1 ? { op: 'phrase', words: ws, field: fld } : { op: 'term', w: ws[0] || '', field: fld };
      } else node = { op: 'term', w: x, field: fld };
      return neg ? { op: 'not', a: node } : node;
    }
    function orExpr() {
      var a = atom();
      while (true) {
        if (isOr(peek())) { i++; a = { op: 'or', a: a, b: atom() }; continue; }
        var n = nearOp(peek()); if (n) { i++; a = { op: 'near', a: a, b: atom(), n: n }; continue; }
        break;
      }
      return a;
    }
    function andExpr() {
      var parts = [];
      while (i < tk.length && peek() !== ')') { if (isAnd(peek())) { i++; continue; } var e = orExpr(); if (e) parts.push(e); }
      return parts.length === 1 ? parts[0] : { op: 'and', parts: parts };
    }
    return andExpr();
  }
  function terms(node, acc) {
    acc = acc || [];
    if (!node) return acc;
    if (node.op === 'term' && node.field !== 'title') acc.push(node.w);
    else if (node.op === 'phrase') acc.push(node.words.join(' '));
    else if (node.op === 'not') { }
    else ['a', 'b'].forEach(function (k) { if (node[k]) terms(node[k], acc); }), (node.parts || []).forEach(function (p) { terms(p, acc); });
    return acc;
  }

  /* ---- postings */
  function maskRe(w) { // folded mask -> RegExp over index keys
    return new RegExp('^' + w.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$');
  }
  var FORMS = [];   // index keys a query expanded to: [word, units]
  function keysFor(w, dict) {
    var f = fold(w);
    if (!/[*?]/.test(f)) return dict[f] !== undefined ? [f] : [];
    var re = maskRe(f), out = [];
    for (var k in dict) if (re.test(k)) out.push(k);
    out.sort(function (a, b) { return dict[b].length - dict[a].length; });
    return out.slice(0, 300);
  }
  function allShards() {
    var ks = []; 'abcdefghijklmnopqrstuvwxyz0123456789_'.split('').forEach(function (a) { 'abcdefghijklmnopqrstuvwxyz0123456789_'.split('').forEach(function (b) { ks.push(a + b); }); });
    return Promise.all(ks.map(function (k) { return shard(k); }));
  }
  function termSet(node) {
    var w = node.w; if (!w) return Promise.resolve(new Set());
    if (node.field === 'title') {
      var f = fold(w).replace(/\*/g, ''), s = new Set();
      UNITS.forEach(function (u, i) { if (fold(u[0] + ' ' + ((ITEMS[u[0]] || [])[0] || '')).indexOf(f) >= 0) s.add(i); });
      return Promise.resolve(s);
    }
    var fw = fold(w);
    var src = node.field ? field(node.field).then(function (d) { return [d]; })
      : /^[*?]/.test(fw) ? allShards().then(function () { return Object.keys(IX).map(function (k) { return IX[k]; }); })
        : shard(skey(fw)).then(function (d) { return [d]; });
    return src.then(function (dicts) {
      var s = new Set();
      dicts.forEach(function (d) {
        keysFor(w, d).forEach(function (k) {
          var us = decode(d[k]); FORMS.push([k, us.length, node.field || '']); us.forEach(function (u) { s.add(u); });
        });
      });
      return s;
    });
  }
  function evalNode(node, universe) {
    if (!node) return Promise.resolve(new Set());
    switch (node.op) {
      case 'term': return termSet(node);
      case 'phrase': return Promise.all(node.words.map(function (w) { return termSet({ op: 'term', w: w, field: node.field }); })).then(inter);
      case 'near': return Promise.all([evalNode(node.a), evalNode(node.b)]).then(inter);
      case 'or': return Promise.all([evalNode(node.a), evalNode(node.b)]).then(function (r) { var s = new Set(r[0]); r[1].forEach(function (x) { s.add(x); }); return s; });
      case 'not': return evalNode(node.a).then(function (s) { return { not: s }; });
      case 'and':
        return Promise.all(node.parts.map(function (p) { return evalNode(p); })).then(function (rs) {
          var pos = rs.filter(function (r) { return !r.not; }), neg = rs.filter(function (r) { return r.not; });
          var s = pos.length ? inter(pos) : new Set(UNITS.map(function (_, i) { return i; }));
          neg.forEach(function (n) { n.not.forEach(function (x) { s.delete(x); }); });
          return s;
        });
    }
    return Promise.resolve(new Set());
  }
  function inter(sets) {
    sets = sets.slice().sort(function (a, b) { return a.size - b.size; });
    var out = new Set(); if (!sets.length) return out;
    sets[0].forEach(function (x) { if (sets.every(function (s) { return s.has(x); })) out.add(x); });
    return out;
  }
  function needsText(node) {
    if (!node) return false;
    if (node.op === 'phrase' || node.op === 'near') return true;
    return ['a', 'b'].some(function (k) { return needsText(node[k]); }) || (node.parts || []).some(needsText);
  }
  /* exact checks on the unit text: phrases and NEAR */
  var reCache = {};
  function wordRe(w) { return reCache[w] || (reCache[w] = new RegExp('^' + w.toLowerCase().replace(/ß/g, 'ss').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$')); }
  function words(s) { return (s.match(/[\p{L}\p{N}]+/gu) || []).map(fold); }
  function positions(ws, w) { var re = wordRe(w), o = []; ws.forEach(function (x, i) { if (re.test(x)) o.push(i); }); return o; }
  function check(node, ws) {
    if (!node) return true;
    switch (node.op) {
      case 'term': return node.field ? true : positions(ws, node.w).length > 0;
      case 'phrase': {
        var p0 = positions(ws, node.words[0]);
        return p0.some(function (p) { return node.words.every(function (w, k) { return ws[p + k] && wordRe(w).test(ws[p + k]); }); });
      }
      case 'near': {
        var a = span(node.a, ws), b = span(node.b, ws);
        return a.some(function (x) { return b.some(function (y) { return Math.abs(x - y) <= node.n; }); });
      }
      case 'or': return check(node.a, ws) || check(node.b, ws);
      case 'not': return !check(node.a, ws);
      case 'and': return node.parts.every(function (p) { return check(p, ws); });
    }
    return true;
  }
  function span(node, ws) {
    if (node.op === 'term') return positions(ws, node.w);
    if (node.op === 'phrase') { return positions(ws, node.words[0]).filter(function (p) { return node.words.every(function (w, k) { return ws[p + k] && wordRe(w).test(ws[p + k]); }); }); }
    if (node.op === 'or') return span(node.a, ws).concat(span(node.b, ws));
    return [];
  }
  function unitText(u) { var x = UNITS[u], k = x[0] + '.' + x[1], tx = TX[k]; return tx ? tx.t[u - tx.first] || '' : null; }

  /* ---- UI */
  var $ = function (id) { return document.getElementById(id); };
  var state = { page: 0, hits: [], node: null, raw: '' };
  function filters() {
    return {
      v: document.querySelector('input[name=v]:checked').value, field: $('s-field').value, scope: $('s-scope').value,
      y0: +$('s-y0').value || 0, y1: +$('s-y1').value || 0
    };
  }
  function inScope(u, f) {
    var x = UNITS[u];
    if (f.v !== 'both' && x[1] !== f.v) return false;
    if (f.y0 && (!x[4] || x[4] < f.y0)) return false;
    if (f.y1 && (!x[4] || x[4] > f.y1)) return false;
    if (f.scope) {
      var m = /^(\w+):(.+)$/.exec(f.scope), it = ITEMS[x[0]] || [];
      if (m[1] === 'item' && x[0] !== m[2]) return false;
      if (m[1] === 'group' && (it[1] || []).indexOf(m[2]) < 0) return false;
      if (m[1] === 'series' && (it[2] || []).indexOf(m[2]) < 0) return false;
    }
    return true;
  }
  function run() {
    var raw = $('q').value.trim(), f = filters(); state.raw = raw; state.page = 0;
    LS.set('search.opts', { v: f.v, field: f.field });
    history.replaceState(null, '', '?q=' + encodeURIComponent(raw) + (f.field ? '&f=' + f.field : '') + (f.scope ? '&s=' + encodeURIComponent(f.scope) : '') + (f.v !== 'norm' ? '&v=' + f.v : '') + (f.y0 ? '&y0=' + f.y0 : '') + (f.y1 ? '&y1=' + f.y1 : ''));
    var R = $('r'); if (!raw) { R.innerHTML = ''; $('forms').innerHTML = ''; return; }
    R.innerHTML = '<p class="muted">' + t('s.searching') + '</p>';
    FORMS = [];
    var node = parse(raw, f.field || ''); state.node = node;
    evalNode(node).then(function (set) {
      var hits = [];
      set.forEach(function (u) { if (inScope(u, f)) hits.push(u); });
      hits.sort(function (a, b) { return a - b; });
      if (needsText(node)) return verify(hits, node).then(function (h) { return [h, true]; });
      return [hits, false];
    }).then(function (r) { state.hits = r[0]; state.checked = r[1]; showForms(); show(); });
  }
  function verify(hits, node) {
    var keys = {}; hits.forEach(function (u) { keys[UNITS[u][0] + '.' + UNITS[u][1]] = 1; });
    var ks = Object.keys(keys);
    $('r').innerHTML = '<p class="muted">' + t('s.checking', { n: ks.length }) + '</p>';
    return Promise.all(ks.map(text)).then(function () {
      return hits.filter(function (u) { var s = unitText(u); return s === null || check(node, words(s)); });
    });
  }
  function showForms() {
    var agg = {};
    FORMS.forEach(function (f) { var k = (f[2] ? f[2] + ':' : '') + f[0]; agg[k] = Math.max(agg[k] || 0, f[1]); });
    var ks = Object.keys(agg).sort(function (a, b) { return agg[b] - agg[a]; });
    $('forms').innerHTML = ks.length > 1 ? '<details><summary>' + t('s.forms', { n: ks.length }) + '</summary><p class="ui">' +
      ks.map(function (k) { return '<a href="#" data-w="' + k + '">' + k + '</a> <span class="muted">' + agg[k] + '</span>'; }).join(' · ') + '</p></details>' : '';
    $('forms').querySelectorAll('a[data-w]').forEach(function (a) { a.onclick = function (e) { e.preventDefault(); $('q').value = a.dataset.w; run(); }; });
  }
  var PER = 100;
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function kwic(u, re) {
    var s = unitText(u); if (s === null) return null;
    re.lastIndex = 0; var m = re.exec(s);
    if (!m) return ['', esc(s.slice(0, 90)), ''];
    var a = Math.max(0, m.index - 70), b = Math.min(s.length, m.index + m[0].length + 70);
    return [(a > 0 ? '…' : '') + esc(s.slice(a, m.index)), esc(m[0]), esc(s.slice(m.index + m[0].length, b)) + (b < s.length ? '…' : '')];
  }
  function show() {
    var hits = state.hits, R = $('r'), f = filters(), q = encodeURIComponent(terms(state.node).map(function (x) { return /\s/.test(x) ? '"' + x + '"' : x; }).join(' '));
    var byItem = {}; hits.forEach(function (u) { var k = UNITS[u][0] + '.' + UNITS[u][1]; byItem[k] = (byItem[k] || 0) + 1; });
    var head = '<h2>' + t('s.found', { n: hits.length, m: Object.keys(byItem).length }) + (state.checked ? ' <span class="muted">' + t('s.checked') + '</span>' : '') + '</h2>';
    var list = hits.slice(state.page * PER, (state.page + 1) * PER);
    var keys = {}; list.forEach(function (u) { keys[UNITS[u][0] + '.' + UNITS[u][1]] = 1; });
    R.innerHTML = head + '<p class="muted">' + t('s.loading') + '</p>';
    var mode = $('s-mode').value;
    Promise.all(Object.keys(keys).map(text)).then(function () {
      var re = BEE.buildRe(terms(state.node)) || /$^/;
      var html = head;
      var pages = Math.ceil(hits.length / PER);
      var pager = pages > 1 ? '<p class="ui">' + Array.from({ length: pages }, function (_, i) { return i === state.page ? '<b>' + (i + 1) + '</b>' : '<a href="#" data-p="' + i + '">' + (i + 1) + '</a>'; }).join(' ') + '</p>' : '';
      html += pager;
      if (mode === 'list') {
        html += '<table class="ui kwic"><tr><th>' + t('s.col.item') + '</th><th>' + t('s.col.place') + '</th><th colspan="3">' + t('s.col.context') + '</th></tr>';
        list.forEach(function (u) {
          var x = UNITS[u], k = kwic(u, re) || ['', '', ''], href = 'items/' + x[0] + '.' + x[1] + '.html?q=' + q + '#' + x[2];
          html += '<tr data-u="' + u + '"><td><a href="' + href + '">' + x[0] + '</a> <span class="muted">' + (x[1] === 'norm' ? 'N' : 'D') + '</span></td><td><a href="' + href + '">' + esc(x[3] || '·') + '</a></td><td class="l">' + k[0] + '</td><td class="k">' + k[1] + '</td><td class="r">' + k[2] + '</td></tr>';
        });
        html += '</table><p class="ui"><button type="button" id="s-copy">' + t('s.copy') + '</button></p>';
      } else {
        var cur = '';
        list.forEach(function (u) {
          var x = UNITS[u], key = x[0] + '.' + x[1];
          if (key !== cur) {
            cur = key; var it = ITEMS[x[0]] || [''];
            html += '<h3 class="ui" style="margin:1em 0 .2em">' + x[0] + ' <span class="muted">' + t(x[1] === 'norm' ? 'ver.norm' : 'ver.diplo') + '</span> ' + esc(it[0]) + ' <span class="muted">(' + byItem[key] + ')</span></h3>';
          }
          var k = kwic(u, re), href = 'items/' + x[0] + '.' + x[1] + '.html?q=' + q + '#' + x[2];
          html += '<div class="ui" style="margin-left:1.2em"><a href="' + href + '">' + esc(x[3] || '·') + '</a> ' + (k ? k[0] + '<mark>' + k[1] + '</mark>' + k[2] : '') + '</div>';
        });
      }
      html += pager;
      R.innerHTML = html;
      R.querySelectorAll('a[data-p]').forEach(function (a) { a.onclick = function (e) { e.preventDefault(); state.page = +a.dataset.p; show(); window.scrollTo(0, 0); }; });
      var c = $('s-copy');
      if (c) c.onclick = function () {
        var rows = list.map(function (u) { var x = UNITS[u], k = kwic(u, re) || ['', '', '']; var d = document.createElement('div'); d.innerHTML = k.join(''); return ['BEE', x[0], x[1], x[3], d.textContent].join('\t'); });
        navigator.clipboard && navigator.clipboard.writeText(rows.join('\n')); c.textContent = t('s.copied');
      };
    });
  }
  /* suggestions: titles, persons and words of the index, after two letters */
  var sugBox = null;
  function suggest() {
    var v = $('q').value, m = /(\S+)$/.exec(v); if (!sugBox) { sugBox = document.createElement('datalist'); sugBox.id = 'sug'; document.body.appendChild(sugBox); $('q').setAttribute('list', 'sug'); }
    if (!m || m[1].length < 2 || /[*?"]/.test(m[1])) { sugBox.innerHTML = ''; return; }
    var w = fold(m[1]), pre = v.slice(0, v.length - m[1].length);
    Promise.all([shard(skey(w)), field('person')]).then(function (r) {
      var d = r[0], ps = r[1], out = [];
      Object.keys(d).filter(function (k) { return k.indexOf(w) === 0; }).sort(function (a, b) { return d[b].length - d[a].length; }).slice(0, 12).forEach(function (k) { out.push(pre + k); });
      Object.keys(ps).filter(function (k) { return k.indexOf(w) === 0; }).slice(0, 5).forEach(function (k) { out.push(pre + 'person:' + k); });
      sugBox.innerHTML = out.map(function (x) { return '<option value="' + esc(x) + '">'; }).join('');
    });
  }
  function init() {
    var sc = $('s-scope'), groups = { manuscripts: 1, typescripts: 1, dictations: 1, 'bände': 1 };
    var o = '<option value="">' + t('s.scope.all') + '</option>';
    o += '<optgroup label="' + t('s.scope.groups') + '">' + Object.keys(groups).map(function (g) { return '<option value="group:' + g + '">' + t('grp.' + g) + '</option>'; }).join('') + '</optgroup>';
    o += '<optgroup label="' + t('s.scope.series') + '">' + Object.keys(SERIES).map(function (s) { return '<option value="series:' + s + '">' + esc(SERIES[s]) + '</option>'; }).join('') + '</optgroup>';
    o += '<optgroup label="Items">' + Object.keys(ITEMS).map(function (n) { return '<option value="item:' + n + '">' + n + ' ' + esc(ITEMS[n][0]).slice(0, 60) + '</option>'; }).join('') + '</optgroup>';
    sc.innerHTML = o;
    var P = new URLSearchParams(location.search), opts = LS.get('search.opts', {});
    var v = P.get('v') || opts.v || 'norm'; var r = document.querySelector('input[name=v][value="' + v + '"]'); if (r) r.checked = true;
    $('s-field').value = P.get('f') || ''; sc.value = P.get('s') || ''; $('s-y0').value = P.get('y0') || ''; $('s-y1').value = P.get('y1') || '';
    $('f').onsubmit = function (e) { e.preventDefault(); run(); };
    $('s-mode').value = LS.get('search.mode', 'items');
    $('s-mode').onchange = function () { LS.set('search.mode', this.value); if (state.hits.length) show(); };
    $('q').addEventListener('input', suggest);
    document.addEventListener('bee-lang', function () { init2(); if (state.hits.length) show(); });
    if (P.get('q')) { $('q').value = P.get('q'); run(); }
  }
  function init2() { BEE.applyI18n(); }
  var s = document.createElement('script'); s.src = 'search/units.js'; s.onload = init; document.head.appendChild(s);
})();
