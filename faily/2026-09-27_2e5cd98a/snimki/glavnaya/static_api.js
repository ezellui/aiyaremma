/* static_api.js — the answers of hwph_serve.py, computed in the page from the files of data/.
   Written by hwph_export.py next to index.html. A page opened from disk may load scripts but not
   fetch files, so every data file is a script: HWPH.put(key, value). */
"use strict";
(function () {
  const WAIT = new Map(), DATA = new Map();
  window.HWPH = {put(key, value) { DATA.set(key, value); const w = WAIT.get(key); if (w) { w.forEach(f => f(value)); WAIT.delete(key); } }};
  function load(key) {
    if (DATA.has(key)) return Promise.resolve(DATA.get(key));
    return new Promise((ok, bad) => {
      if (WAIT.has(key)) { WAIT.get(key).push(ok); return; }
      WAIT.set(key, [ok]);
      const s = document.createElement('script');
      s.src = 'data/' + key + '.js';
      s.onerror = () => { WAIT.delete(key); bad(new Error('нет файла data/' + key + '.js')); };
      document.head.appendChild(s);
    });
  }
  const loadAll = keys => Promise.all(keys.map(load));

  /* ---------- folding and words: the rules of hwph_common.py ---------- */
  const DROP = new Set('´′`˜¨᾿῾῀΄΅');
  const fc = new Map();
  function foldChar(c) {
    let f = fc.get(c);
    if (f !== undefined) return f;
    if (DROP.has(c)) f = ''; else if (c === 'ß') f = 'ss';
    else f = c.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/ς/g, 'σ').replace(/ı/g, 'i');
    fc.set(c, f); return f;
  }
  function fold(s) { let o = ''; for (const c of s || '') o += foldChar(c); return o; }
  function foldMap(s) {
    let o = '', idx = [], i = 0;
    for (const c of s) { const f = foldChar(c); o += f; for (let k = 0; k < f.length; k++) idx.push(i); i += c.length; }
    return [o, idx];
  }
  const WORD = /[\p{L}\p{N}_]+/gu;
  const words = s => (fold(s).match(WORD) || []);
  const shardOf = t => [...t].slice(0, 2).map(c => c.codePointAt(0).toString(16)).join('-');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  let META = null;
  async function meta() {
    if (!META) {
      META = await load('meta');
      META.byId = new Map(META.lemmas.map(r => [r[0], r]));
      META.fold = new Map(META.lemmas.map(r => [r[0], fold(r[1])]));
      META.shardSet = new Set(META.shards);
      META.regSet = new Set(META.reg_shards);
    }
    return META;
  }

  /* ---------- search index ---------- */
  function decode(str) {                 // "aid:counts aid:counts" with delta ids in base 36
    const out = new Map(); let prev = 0;
    for (const e of str.split(' ')) {
      const [a, c] = e.split(':'); prev += parseInt(a, 36);
      const cnt = [0, 0, 0, 0, 0]; c.split(',').forEach((x, i) => { cnt[i] = parseInt(x, 36); });
      out.set(prev, cnt);
    }
    return out;
  }
  const postCache = new Map();
  async function postingsOf(token, prefix) {
    const key = token + (prefix ? '*' : '');
    if (postCache.has(key)) return postCache.get(key);
    const m = await meta();
    let names;
    if (token.length >= 2) names = [shardOf(token)];
    else names = META.shards.filter(n => n.split('-')[0] === token.codePointAt(0).toString(16));
    names = names.filter(n => m.shardSet.has(n));
    const shards = await loadAll(names.map(n => 's/' + n));
    const res = new Map();
    for (const sh of shards) {
      const terms = prefix ? Object.keys(sh).filter(t => t.startsWith(token)) : (sh[token] ? [token] : []);
      for (const t of terms) for (const [aid, c] of decode(sh[t])) {
        const e = res.get(aid);
        if (!e) res.set(aid, c.slice()); else for (let i = 0; i < 5; i++) e[i] += c[i];
      }
    }
    postCache.set(key, res);
    return res;
  }

  function parseQuery(q) {
    const items = []; let orNext = false; const re = /(-?)"([^"]+)"(\*?)|(\S+)/g; let m;
    while ((m = re.exec(q))) {
      let w, neg, prefix, toks;
      if (m[4] !== undefined) {
        w = m[4]; if (w === 'OR' || w === '|') { orNext = true; continue; }
        neg = w.length > 1 && w[0] === '-'; if (neg) w = w.slice(1);
        prefix = w.endsWith('*'); toks = words(w);
      } else { neg = !!m[1]; prefix = !!m[3]; toks = words(m[2]); }
      if (!toks.length) continue;
      items.push({tokens: toks, prefix, neg, or_before: orNext && items.length > 0});
      orNext = false;
    }
    return items;
  }
  function itemRegex(it) {
    const t = it.tokens.map(x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    if (it.prefix) t[t.length - 1] += '[\\p{L}\\p{N}_]*';
    return '(?<![\\p{L}\\p{N}_])' + t.join('[^\\p{L}\\p{N}_]{1,4}') + '(?![\\p{L}\\p{N}_])';
  }
  function highlightRx(items) {
    const p = items.filter(i => !i.neg).map(itemRegex);
    return p.length ? new RegExp(p.join('|'), 'gu') : null;
  }
  const COLS = ['lemma', 'body', 'notes', 'lit', 'authors'];
  const COLTEXT = {1: 'b', 2: 'n', 3: 'l', 4: 'au'};

  // documents that match one item (all its words; a phrase is checked in the text afterwards)
  async function itemDocs(it, col) {
    const lists = [];
    for (let i = 0; i < it.tokens.length; i++) lists.push(await postingsOf(it.tokens[i], it.prefix && i === it.tokens.length - 1));
    lists.sort((a, b) => a.size - b.size);
    const out = new Map();
    for (const [aid, c] of lists[0]) {
      let ok = true; const sum = c.slice();
      for (let k = 1; k < lists.length && ok; k++) {
        const e = lists[k].get(aid);
        if (!e) ok = false; else for (let i = 0; i < 5; i++) sum[i] = Math.min(sum[i], e[i]);
      }
      if (!ok) continue;
      if (col !== null && !sum[col]) continue;
      out.set(aid, sum);
    }
    return {docs: out, df: lists.map(l => l.size)};
  }
  async function phraseOk(it, aid, col) {
    if (it.tokens.length < 2) return true;
    const m = await meta();
    const rx = new RegExp(itemRegex(it), 'u');
    if (col === 0) return rx.test(fold(m.byId.get(aid)[1]));
    const t = await load('t/' + aid);
    const parts = col !== null ? [t[COLTEXT[col]]] : [t.b, t.n, t.l, t.au, m.byId.get(aid)[1]];
    return parts.some(x => rx.test(fold(x || '')));
  }

  function snippets(text, rx, width, maxn) {
    if (!text || !rx) return [];
    const [folded, idx] = foldMap(text); const hits = []; let m;
    rx.lastIndex = 0;
    while ((m = rx.exec(folded))) { if (!m[0].length) { rx.lastIndex++; continue; } hits.push([m.index, m.index + m[0].length]); }
    if (!hits.length) return [];
    const chosen = [];
    for (const [s, e] of hits) { if (chosen.some(([c]) => Math.abs(s - c) < width * 2)) continue; chosen.push([s, e]); if (chosen.length >= maxn) break; }
    return chosen.map(([s]) => {
      let a = Math.max(0, s - width); const b = Math.min(folded.length, s + width);
      let oa = a < idx.length ? idx[a] : 0; const ob = b - 1 < idx.length ? idx[b - 1] + 1 : text.length;
      while (oa > 0 && !/\s/.test(text[oa - 1]) && s - a < width + 20) { oa--; a--; }
      const ph = hits.filter(([hs, he]) => idx[hs] >= oa && idx[he - 1] < ob).map(([hs, he]) => [idx[hs], idx[he - 1] + 1]);
      let buf = '', pos = oa;
      for (const [hs, he] of ph) { buf += esc(text.slice(pos, hs)) + '<mark>' + esc(text.slice(hs, he)) + '</mark>'; pos = he; }
      buf += esc(text.slice(pos, ob));
      return (oa > 0 ? '… ' : '') + buf.trim() + (ob < text.length ? ' …' : '');
    });
  }
  function countHits(text, rx) {
    if (!text || !rx) return 0;
    rx.lastIndex = 0; const f = fold(text); let n = 0, m;
    while ((m = rx.exec(f))) { if (!m[0].length) { rx.lastIndex++; continue; } n++; }
    return n;
  }

  async function search(p) {
    const q = (p.get('q') || '').trim(), scope = p.get('scope') || 'all', band = p.get('band') || '';
    const offset = +(p.get('offset') || 0), limit = Math.min(+(p.get('limit') || 20), 100);
    const items = parseQuery(q);
    const col = COLS.indexOf(scope) >= 0 ? COLS.indexOf(scope) : null;
    const res = {q, total: 0, items: [], register: []};
    const pos = items.filter(i => !i.neg), neg = items.filter(i => i.neg);
    if (!pos.length) return res;
    const m = await meta();
    // combine: AND between items, OR where the query says so
    let current = null; const groups = [];
    for (const it of pos) {
      const r = await itemDocs(it, col);
      if (it.or_before && current) { current.alts.push({it, r}); } else { current = {alts: [{it, r}]}; groups.push(current); }
    }
    const N = m.n_docs, W = m.weights, k1 = 1.2, bb = 0.75;
    const score = new Map();
    let cand = null;
    for (const g of groups) {
      const union = new Map();
      for (const {r} of g.alts) for (const [aid, c] of r.docs) {
        let s = 0;
        const L = m.lengths[aid] || [1, 1, 1, 1, 1];
        for (let i = 0; i < 5; i++) {
          if (!c[i] || (col !== null && i !== col)) continue;
          const df = Math.max(...r.df), idf = Math.log(1 + (N - df + 0.5) / (df + 0.5));
          s += W[i] * idf * (c[i] * (k1 + 1)) / (c[i] + k1 * (1 - bb + bb * L[i] / Math.max(1, m.avg[i])));
        }
        union.set(aid, (union.get(aid) || 0) + s);
      }
      if (cand === null) cand = union;
      else { const next = new Map(); for (const [a, s] of union) if (cand.has(a)) next.set(a, cand.get(a) + s); cand = next; }
    }
    for (const it of neg) {
      const r = await itemDocs(it, col);
      for (const a of r.docs.keys()) cand.delete(a);
    }
    if (band) for (const a of [...cand.keys()]) if (m.byId.get(a)[2] !== band) cand.delete(a);
    // phrases: verify in the text (cheap words first narrowed the candidates)
    const phrases = pos.filter(i => i.tokens.length > 1);
    let approx = false;
    if (phrases.length) {
      let list = [...cand.keys()];
      if (list.length > 1500) { list.sort((a, b) => cand.get(b) - cand.get(a)); list.slice(1500).forEach(a => cand.delete(a)); list = list.slice(0, 1500); approx = true; }
      for (const a of list) {
        let ok = true;
        for (const g of groups) {
          let any = false;
          for (const {it} of g.alts) if (await phraseOk(it, a, col)) { any = true; break; }
          if (!any) { ok = false; break; }
        }
        if (!ok) cand.delete(a);
      }
    }
    // order: the lemma itself, the articles the register gives for the word, lemma containing it, score
    const first = pos[0].tokens.join(' ');
    const regDst = new Set((await registerRows(first)).filter(r => r[8] === first && r[5] !== 'author' && r[6]).map(r => r[6]));
    const ranked = [...cand.entries()].map(([a, s]) => {
      const lf = m.fold.get(a);
      return [a, lf === first ? 0 : 1, regDst.has(a) ? 0 : 1, lf.indexOf(first) >= 0 ? 0 : 1, -s];
    }).sort((x, y) => x[1] - y[1] || x[2] - y[2] || x[3] - y[3] || x[4] - y[4]);
    res.total = ranked.length;
    if (approx) res.approx = true;
    const rx = highlightRx(items);
    for (const [aid] of ranked.slice(offset, offset + limit)) {
      const t = await load('t/' + aid), L = m.byId.get(aid);
      const texts = {body: t.b, notes: t.n, lit: t.l};
      const hits = {body: countHits(t.b, rx), notes: countHits(t.n, rx), lit: countHits(t.l, rx)};
      const snips = [];
      const order = col === 1 ? ['body'] : col === 2 ? ['notes'] : col === 3 ? ['lit'] : ['body', 'notes', 'lit'];
      for (const k of order) {
        for (const s of snippets(texts[k], rx, 110, 2 - snips.length)) snips.push({where: k, html: s});
        if (snips.length >= 2) break;
      }
      res.items.push({id: aid, lemma: L[1], band: L[2], col_from: L[3], col_to: L[5], authors: t.au ? t.au.split(/(?<=\.)\s(?=[A-ZÄÖÜ])|,\s/).filter(Boolean) : [], hits, snippets: snips});
    }
    if (offset === 0 && (scope === 'all' || scope === 'register') && items.length === 1 && !items[0].neg)
      res.register = await registerLookup(items[0].tokens.join(' '), 40, items[0].prefix);
    return res;
  }

  /* ---------- register ---------- */
  async function registerRows(f) {
    const m = await meta();
    if (!f) return [];
    let names = f.length >= 2 ? [shardOf(f)] : m.reg_shards.filter(n => n.split('-')[0] === f.codePointAt(0).toString(16));
    names = names.filter(n => m.regSet.has(n));
    const sh = await loadAll(names.map(n => 'r/' + n));
    return [].concat(...sh);
  }
  async function registerLookup(term, limit, prefix) {
    const f = fold(term).trim();
    if (!f) return [];
    let rows = (await registerRows(f)).filter(r => r[5] !== 'see' && r[5] !== 'author' && (prefix || true ? r[8].startsWith(f) : r[8] === f));
    if (!prefix) { const exact = rows.filter(r => r[8] === f); if (exact.length) rows = rows; }
    rows.sort((a, b) => (b[8] === f) - (a[8] === f) || (a[8] < b[8] ? -1 : a[8] > b[8] ? 1 : 0));
    return rows.slice(0, limit).map(r => ({term: r[0], target: r[1], qualifier: r[2], band: r[3], col: r[4], kind: r[5], id: r[6], lemma: r[7]}));
  }

  /* ---------- persons and graphs ---------- */
  let G = null;
  async function graph() {
    if (G) return G;
    const [g, persons] = await Promise.all([load('graph'), load('persons')]);
    G = {out: new Map(), inn: new Map(), byArt: new Map(), byPerson: new Map(), mentions: new Map(), P: new Map()};
    for (const [s, d, c] of g.xrefs) {
      if (!G.out.has(s)) G.out.set(s, []); G.out.get(s).push([d, c]);
      if (!G.inn.has(d)) G.inn.set(d, []); G.inn.get(d).push([s, c]);
    }
    for (const r of g.cites) {
      if (!G.byArt.has(r[0])) G.byArt.set(r[0], []); G.byArt.get(r[0]).push(r);
      if (!G.byPerson.has(r[1])) G.byPerson.set(r[1], []); G.byPerson.get(r[1]).push(r);
    }
    for (const r of g.mentions) { if (!G.mentions.has(r[0])) G.mentions.set(r[0], []); G.mentions.get(r[0]).push(r); }
    G.mentions.forEach(l => l.sort((a, b) => b[3] - a[3]));
    for (const p of persons) G.P.set(p[0], {id: p[0], name: p[1], fold: p[2], n_articles: p[3], n_body: p[4], n_notes: p[5], n_lit: p[6], editor: p[7], role: p[8]});
    G.persons = persons;
    return G;
  }
  async function patEntry(pid) { const d = await load('pat/' + Math.floor(pid / 500)); return d[pid] || [null, []]; }

  function cocited(pid, limit, scholars) {
    const mine = (G.byPerson.get(pid) || []).filter(r => r[2] + r[3] > 0);
    const me = mine.length || 1, shared = new Map();
    for (const r of mine) for (const o of G.byArt.get(r[0]) || []) {
      if (o[1] === pid || o[2] + o[3] <= 0) continue;
      const P = G.P.get(o[1]);
      if (!P || P.editor || (!scholars && P.role === 'scholar')) continue;
      shared.set(o[1], (shared.get(o[1]) || 0) + 1);
    }
    const res = [];
    for (const [id, sh] of shared) if (sh >= 2) { const P = G.P.get(id); res.push({id, name: P.name, shared: sh, role: P.role, score: sh / Math.sqrt(me * Math.max(P.n_articles, 1))}); }
    res.sort((a, b) => b.score - a.score);
    return res.slice(0, limit);
  }
  async function person(id, p) {
    const m = await meta(); await graph();
    const P = G.P.get(id); if (!P) throw new Error('Лицо не найдено');
    const [, variants] = await patEntry(id);
    const arts = (G.byPerson.get(id) || []).map(r => { const L = m.byId.get(r[0]); return {id: r[0], lemma: L[1], band: L[2], col: L[3], nb: r[2], nn: r[3], nl: r[4], f: m.fold.get(r[0])}; });
    arts.sort((a, b) => (b.nb + b.nn) - (a.nb + a.nn) || b.nl - a.nl || (a.f < b.f ? -1 : 1));
    const surname = P.name.split(' ').pop();
    const lemmas = surname.length >= 4 ? m.lemmas.filter(r => r[4] === 'article' && m.fold.get(r[0]).indexOf(fold(surname)) >= 0)
      .sort((a, b) => (m.fold.get(a[0]) < m.fold.get(b[0]) ? -1 : 1)).slice(0, 30).map(r => ({id: r[0], lemma: r[1]})) : [];
    return Object.assign({}, P, {variants, articles: arts, cocited: cocited(id, 40, p.get('scholars') === '1'), lemmas});
  }
  async function persons(p) {
    await graph();
    const q = fold((p.get('q') || '').trim()), editors = p.get('editors') === '1', role = p.get('role') || '';
    const limit = Math.min(+(p.get('limit') || 200), 1000), out = [];
    for (const r of G.persons) {
      const P = G.P.get(r[0]);
      if (!editors && P.editor) continue;
      if (q && P.fold.indexOf(q) < 0) continue;
      if (['source', 'mixed', 'scholar'].includes(role) && P.role !== role) continue;
      if (role === 'thinkers' && P.role === 'scholar') continue;
      out.push({id: P.id, name: P.name, n_articles: P.n_articles, b: P.n_body, n: P.n_notes, l: P.n_lit, editor: P.editor, role: P.role});
      if (out.length >= limit) break;
    }
    return out;
  }
  const neighbours = a => [...new Set([...(G.out.get(a) || []).map(x => x[0]), ...(G.inn.get(a) || []).map(x => x[0])])].filter(x => x !== a);
  async function graphArticle(aid, p) {
    const m = await meta(); await graph();
    const depth = p.get('depth') === '2' ? 2 : 1, withP = p.get('persons') !== '0', scholars = p.get('scholars') === '1', cap = 90;
    const level = new Map([[aid, 0]]);
    const first = neighbours(aid); first.forEach(a => { if (!level.has(a)) level.set(a, 1); });
    if (depth === 2) {
      const deg = new Map();
      for (const a of first) for (const b of neighbours(a)) if (!level.has(b)) deg.set(b, (deg.get(b) || 0) + 1);
      [...deg.entries()].sort((x, y) => y[1] - x[1]).slice(0, Math.max(0, cap - level.size)).forEach(([b]) => level.set(b, 2));
    }
    const ids = [...level.keys()], idset = new Set(ids);
    const nodes = ids.filter(a => m.byId.has(a)).map(a => { const L = m.byId.get(a); return {id: 'a' + a, ref: a, kind: 'article', label: L[1], level: level.get(a), sub: 'Bd. ' + L[2] + ', Sp. ' + L[3]}; });
    const links = [];
    for (const s of ids) for (const [d, c] of G.out.get(s) || []) if (idset.has(d) && d !== s) links.push({source: 'a' + s, target: 'a' + d, kind: 'xref', w: c});
    if (withP) {
      let top = (G.byArt.get(aid) || []).filter(r => { const P = G.P.get(r[1]); return P && !P.editor && P.role !== 'scholar' && r[2] + r[3] > 0; })
        .sort((a, b) => (b[2] + b[3]) - (a[2] + a[3]) || G.P.get(b[1]).n_articles - G.P.get(a[1]).n_articles).slice(0, 10).map(r => [r[1], r[2] + r[3]]);
      if (scholars) top = top.concat((G.byArt.get(aid) || []).filter(r => { const P = G.P.get(r[1]); return P && P.role === 'scholar'; })
        .sort((a, b) => (b[2] + b[3] + b[4]) - (a[2] + a[3] + a[4])).slice(0, 8).map(r => [r[1], r[2] + r[3] + r[4]]));
      const pids = new Set(top.map(t => t[0]));
      for (const [pid, n] of top) { const P = G.P.get(pid); nodes.push({id: 'p' + pid, ref: pid, kind: 'person', role: P.role, label: P.name, level: 1, sub: n + ' упом.'}); }
      for (const a of ids.filter(a => level.get(a) <= 1)) for (const r of G.byArt.get(a) || [])
        if (pids.has(r[1]) && r[2] + r[3] + r[4] > 0) links.push({source: 'a' + a, target: 'p' + r[1], kind: 'cite', w: 1});
    }
    return {center: 'a' + aid, nodes, links, depth};
  }
  async function graphPerson(pid, p) {
    await graph();
    const me = G.P.get(pid); if (!me) throw new Error('Лицо не найдено');
    const n = Math.min(+(p.get('n') || 24), 60);
    const co = cocited(pid, n, p.get('scholars') === '1');
    const ids = [pid].concat(co.map(c => c.id)), idset = new Set(ids);
    const pair = new Map();
    const arts = new Set();
    ids.forEach(i => (G.byPerson.get(i) || []).forEach(r => { if (r[2] + r[3] > 0) arts.add(r[0]); }));
    for (const a of arts) {
      const here = (G.byArt.get(a) || []).filter(r => idset.has(r[1]) && r[2] + r[3] > 0).map(r => r[1]).sort((x, y) => x - y);
      for (let i = 0; i < here.length; i++) for (let j = i + 1; j < here.length; j++) { const k = here[i] + ',' + here[j]; pair.set(k, (pair.get(k) || 0) + 1); }
    }
    const nodes = [{id: 'p' + pid, ref: pid, kind: 'person', role: me.role, label: me.name, level: 0, sub: me.n_articles + ' статей'}]
      .concat(co.map(c => ({id: 'p' + c.id, ref: c.id, kind: 'person', role: c.role, label: c.name, level: 1, sub: c.shared + ' общих статей'})));
    const links = [];
    for (const [k, w] of pair) {
      if (w < 2) continue;
      const [a, b] = k.split(',').map(Number);
      const score = w / Math.sqrt(Math.max(G.P.get(a).n_articles, 1) * Math.max(G.P.get(b).n_articles, 1));
      links.push({source: 'p' + a, target: 'p' + b, kind: 'cocite', w, score});
    }
    const centre = links.filter(l => l.source === 'p' + pid || l.target === 'p' + pid);
    const others = links.filter(l => !centre.includes(l)).sort((x, y) => y.score - x.score).slice(0, ids.length * 3);
    return {center: 'p' + pid, nodes, links: centre.concat(others)};
  }
  async function expand(p) {
    const m = await meta(); await graph();
    const node = p.get('node') || '', what = p.get('what') || '', limit = Math.min(+(p.get('limit') || 60), 200), scholars = p.get('scholars') === '1';
    const mm = /^([ap])(\d+)$/.exec(node); if (!mm) throw new Error('узел?');
    const kind = mm[1], ref = +mm[2], items = [];
    let total = 0;
    const art = d => { const L = m.byId.get(d); return {id: 'a' + d, ref: d, kind: 'article', label: L[1], level: 2, sub: 'Bd. ' + L[2] + ', Sp. ' + L[3]}; };
    if (kind === 'a' && what === 'persons') {
      const rows = (G.byArt.get(ref) || []).filter(r => { const P = G.P.get(r[1]); return P && !P.editor && (scholars || (P.role !== 'scholar' && r[2] + r[3] > 0)); })
        .sort((a, b) => (G.P.get(a[1]).role === 'scholar') - (G.P.get(b[1]).role === 'scholar') || (b[2] * 2 + b[3] + b[4]) - (a[2] * 2 + a[3] + a[4]) || G.P.get(b[1]).n_articles - G.P.get(a[1]).n_articles);
      total = rows.length;
      for (const r of rows.slice(0, limit)) {
        const P = G.P.get(r[1]);
        items.push({node: {id: 'p' + P.id, ref: P.id, kind: 'person', role: P.role, label: P.name, level: 2, sub: 'в тексте ' + r[2] + ', в примеч. ' + r[3] + (r[4] ? ', в лит. ' + r[4] : '')},
                    link: {source: node, target: 'p' + P.id, kind: 'cite', w: 1}});
      }
    } else if (kind === 'a' && what === 'concepts') {
      const rows = [], seen = new Set();
      (G.out.get(ref) || []).slice().sort((a, b) => b[1] - a[1]).forEach(([d]) => rows.push([d, 'xref', 'ссылка из статьи']));
      (G.inn.get(ref) || []).forEach(([s]) => rows.push([s, 'xref_in', 'ссылается на статью']));
      (G.mentions.get(ref) || []).forEach(r => rows.push([r[1], 'mention', 'обсуждается в тексте (' + r[2] + ')']));
      const uniq = rows.filter(([d]) => d !== ref && !seen.has(d) && seen.add(d) && m.byId.has(d));
      total = uniq.length;
      for (const [d, how, note] of uniq.slice(0, limit))
        items.push({node: art(d), how, note, link: how === 'xref_in' ? {source: 'a' + d, target: node, kind: 'xref', w: 1} : {source: node, target: 'a' + d, kind: how === 'xref' ? 'xref' : 'mention', w: 1}});
    } else if (kind === 'p' && what === 'articles') {
      const rows = (G.byPerson.get(ref) || []).slice().sort((a, b) => (b[2] * 2 + b[3]) - (a[2] * 2 + a[3]) || b[4] - a[4]);
      total = rows.length;
      for (const r of rows.slice(0, limit))
        items.push({node: art(r[0]), note: 'в тексте ' + r[2] + ', в примеч. ' + r[3] + (r[4] ? ', в лит. ' + r[4] : ''), link: {source: 'a' + r[0], target: node, kind: 'cite', w: 1}});
    } else throw new Error('что раскрывать?');
    return {items, total};
  }
  async function suggest(p) {
    const q = (p.get('q') || '').trim(), f = fold(q);
    if (f.length < 2) return {q, items: []};
    const m = await meta(); await graph();
    const items = [];
    let lem = m.lemmas.filter(r => m.fold.get(r[0]).startsWith(f)).sort((a, b) => m.fold.get(a[0]).length - m.fold.get(b[0]).length).slice(0, 7);
    if (lem.length < 7) lem = lem.concat(m.lemmas.filter(r => m.fold.get(r[0]).indexOf(f) > 0).sort((a, b) => m.fold.get(a[0]).length - m.fold.get(b[0]).length).slice(0, 7 - lem.length));
    lem.forEach(r => items.push({type: 'article', id: r[0], label: r[1], sub: 'Bd. ' + r[2] + ', Sp. ' + r[3]}));
    const per = [];
    for (const r of G.persons) {
      const P = G.P.get(r[0]);
      if (P.editor || P.n_articles < 2) continue;
      if (P.fold.startsWith(f) || P.fold.indexOf(' ' + f) >= 0) per.push(P);
    }
    per.sort((a, b) => (a.role === 'scholar') - (b.role === 'scholar') || b.n_articles - a.n_articles);
    per.slice(0, 5).forEach(P => items.push({type: 'person', id: P.id, label: P.name, role: P.role, sub: P.n_articles + ' статей'}));
    const shown = new Set(items.map(x => x.label)), by = new Map();
    for (const r of await registerRows(f)) {
      if (!r[8].startsWith(f) || !['ref', 'main'].includes(r[5]) || !r[6]) continue;
      if (!by.has(r[8])) by.set(r[8], {term: r[0], id: r[6], lemma: r[7], c: 0});
      by.get(r[8]).c++;
    }
    [...by.entries()].sort((a, b) => a[0].length - b[0].length || (a[0] < b[0] ? -1 : 1)).slice(0, 5).forEach(([, x]) => {
      if (!shown.has(x.term)) items.push({type: 'register', term: x.term, id: x.id, label: x.term, sub: '→ ' + x.lemma + (x.c > 1 ? ' и ещё ' + (x.c - 1) : '')});
    });
    return {q, items};
  }
  const BL = '(?<![\\p{L}\\p{N}])', BR = '(?![\\p{L}\\p{N}])';
  const jsEsc = t => t.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
  async function pattern(p) {
    const m = await meta();
    if (p.get('pid')) {
      await graph();
      const pid = +p.get('pid'), P = G.P.get(pid); if (!P) throw new Error('Лицо не найдено');
      const [src] = await patEntry(pid);
      return {source: src, label: P.name, kind: 'person', id: pid};
    }
    const cid = +p.get('concept'), L = m.byId.get(cid); if (!L) throw new Error('Статья не найдена');
    const parts = L[1].split(/[,;/(]/).map(x => x.trim());
    const forms = [...new Set(parts.filter((h, k) => h && h.length >= 4 && h[0] === h[0].toUpperCase() && h[0] !== h[0].toLowerCase() && (k === 0 || !h.includes(' '))))]
      .sort((a, b) => b.length - a.length).map(f => f.split(/\s+/).map(jsEsc).join('\\s+'));
    return {source: BL + '(?:' + forms.join('|') + ')(?:n|en|s|es|e|er|ern)?' + BR, label: L[1], kind: 'concept', id: cid};
  }

  /* ---------- the same paths the server answers ---------- */
  window.HWPH_API = async function (path) {
    const u = new URL(path, 'http://x/'), p = u.searchParams, r = u.pathname;
    let m;
    if (r === '/api/info') { const mt = await meta(); return Object.assign({}, mt.info, {engine: 'static'}); }
    if (r === '/api/lemmas') { const mt = await meta(); return mt.lemmas.map(x => [x[0], x[1], x[2], x[3], x[4]]); }
    if ((m = /^\/api\/article\/(\d+)$/.exec(r))) return load('a/' + m[1]).catch(() => { throw new Error('Статья не найдена'); });
    if (r === '/api/search') return search(p);
    if (r === '/api/register') return registerLookup(p.get('q') || '', 300, true);
    if ((m = /^\/api\/person\/(\d+)$/.exec(r))) return person(+m[1], p);
    if (r === '/api/persons') return persons(p);
    if ((m = /^\/api\/graph\/a\/(\d+)$/.exec(r))) return graphArticle(+m[1], p);
    if ((m = /^\/api\/graph\/p\/(\d+)$/.exec(r))) return graphPerson(+m[1], p);
    if (r === '/api/expand') return expand(p);
    if (r === '/api/suggest') return suggest(p);
    if (r === '/api/pattern') return pattern(p);
    if (r === '/api/ping') return {ok: true};
    throw new Error('неизвестный запрос ' + r);
  };
})();
