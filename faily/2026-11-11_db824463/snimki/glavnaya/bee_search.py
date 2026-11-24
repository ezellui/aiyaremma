#!/usr/bin/env python3
"""bee_search.py XMLDIR SITEDIR — full-text search for the static site (works from file://, no server).
Units: a record (<rec>) of the normalized version, a page (between <pb>) of the diplomatic version.
Words are folded (lower case, ä→a, ß→ss …). The index is split by the first two letters of a word
into SITEDIR/search/ix_<ab>.js; a query loads only the shards it needs (as <script>, so that
file:// works). Each shard: word -> base-36 deltas of unit numbers. units.js: unit -> [item, version,
anchor, label]. search.html: AND of words, word* for prefixes, "…" for phrases (checked on the page)."""
import sys, os, re, json, unicodedata, collections
import xml.etree.ElementTree as ET

xmldir, site = sys.argv[1], sys.argv[2]
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]
TITLES = {l.split(None, 2)[1]: (l.split(None, 2)[2].strip() if len(l.split(None, 2)) > 2 else '') for l in open('/home/claude/work/items.txt')}
out = os.path.join(site, 'search'); os.makedirs(out, exist_ok=True)

SKIP = {'person', 'notation', 'num'}            # index keys and descriptors are not text
WORD = re.compile(r'[^\W_]+', re.U)


def fold(w):
    w = w.lower().replace('ß', 'ss')
    return ''.join(c for c in unicodedata.normalize('NFD', w) if not unicodedata.combining(c))


def text(el, acc):
    if el.tag in SKIP:
        if el.tail: acc.append(el.tail)
        return
    if el.tag == 'app':                       # undecided alternatives: all readings are searchable
        pass
    if el.text: acc.append(el.text)
    for k in el:
        text(k, acc)
    if el.tail: acc.append(el.tail)


def pid(n):
    return 'p-' + re.sub(r'[^\w.-]', '_', n)


units = []
post = collections.defaultdict(list)


def add(words_src, unit):
    seen = set()
    for w in WORD.findall(words_src):
        f = fold(w)
        if len(f) < 2 or f.isdigit() and len(f) > 6:
            continue
        if f not in seen:
            seen.add(f); post[f].append(unit)


for n in ITEMS:
    f = os.path.join(xmldir, f'{n}.norm.xml')
    if os.path.exists(f):
        r = ET.parse(f).getroot()
        for k, rec in enumerate([x for x in r if x.tag == 'rec']):
            acc = []; text(rec, acc)
            label = rec.get('page', '') + ((' · ' + rec.get('date')) if rec.get('date') else '')
            units.append([n, 'norm', f'r-{n}-{k}', label])
            add(' '.join(acc), len(units) - 1)
    f = os.path.join(xmldir, f'{n}.diplo.xml')
    if os.path.exists(f):
        r = ET.parse(f).getroot()
        # split the item into pages: the text after each <pb> up to the next one
        cur = {'page': '', 'acc': []}
        pages = []

        def walk(el):
            if el.tag == 'pb':
                pages.append((cur['page'], ' '.join(cur['acc'])))
                cur['page'] = el.get('n', ''); cur['acc'] = []
                if el.tail: cur['acc'].append(el.tail)
                return
            if el.tag in SKIP:
                if el.tail: cur['acc'].append(el.tail)
                return
            if el.text: cur['acc'].append(el.text)
            for k in el:
                walk(k)
            if el.tail: cur['acc'].append(el.tail)
        walk(r)
        pages.append((cur['page'], ' '.join(cur['acc'])))
        for pg, t in pages:
            if not t.strip():
                continue
            units.append([n, 'diplo', pid(pg) if pg else f'item-{n}', pg])
            add(t, len(units) - 1)


def b36(x):
    s = ''
    while True:
        x, r = divmod(x, 36); s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not x: return s


shards = collections.defaultdict(dict)
for w, us in post.items():
    key = re.sub(r'[^a-z0-9]', '_', w[:2]).ljust(2, '_')
    prev = 0; enc = []
    for u in us:
        enc.append(b36(u - prev)); prev = u
    shards[key][w] = ','.join(enc)
for key, d in shards.items():
    open(os.path.join(out, f'ix_{key}.js'), 'w', encoding='utf-8').write(
        f'BEEIX({json.dumps(key)},' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
open(os.path.join(out, 'units.js'), 'w', encoding='utf-8').write(
    'BEEUNITS(' + json.dumps(units, ensure_ascii=False, separators=(',', ':')) + ',' +
    json.dumps({n: TITLES.get(n, '') for n in ITEMS}, ensure_ascii=False) + ');')

open(os.path.join(site, 'search.html'), 'w', encoding='utf-8').write(r'''<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<title>Suche — Wittgenstein's Nachlass (BEE)</title><style>
body{font:15px/1.5 system-ui,sans-serif;max-width:60em;margin:2em auto;padding:0 1em;color:#222}
input[type=text]{font-size:17px;width:60%;padding:.3em .5em} button{font-size:15px;padding:.3em .9em}
.opts{margin:.5em 0;color:#555} .hint{color:#777;font-size:13px} a{color:#1b1b6e}
.res{margin-top:1.2em} .it{margin-top:1em;font-weight:600} .u{margin-left:1.2em} .u a{margin-right:.8em}
.n{color:#888}</style></head><body>
<p><a href="index.html">Übersicht</a></p>
<h1>Suche</h1>
<form id="f"><input type="text" id="q" placeholder="z.B. Familienähnlichkeit, Sprachspiel*, &quot;Bild der Wirklichkeit&quot;" autofocus>
<button>Suchen</button>
<div class="opts"><label><input type="radio" name="v" value="norm" checked> normalisiert (Bemerkungen)</label>
<label><input type="radio" name="v" value="diplo"> diplomatisch (Seiten)</label>
<label><input type="radio" name="v" value="both"> beide</label>
· Titel: <label><input type="checkbox" id="t" checked> auch Titel der Items durchsuchen</label></div>
<div class="hint">Alle Wörter müssen vorkommen; <code>wort*</code> sucht Anfänge; <code>"…"</code> verlangt die Wortfolge (wird beim Öffnen markiert).
Groß-/Kleinschreibung und Umlaute werden nicht unterschieden (ä = a, ß = ss).</div></form>
<div class="res" id="r"></div>
<script>
var UNITS = null, TITLES = null, IX = {}, waiting = {};
function BEEUNITS(u, t){ UNITS = u; TITLES = t; }
function BEEIX(k, d){ IX[k] = d; if (waiting[k]) { waiting[k].forEach(function(f){ f(); }); delete waiting[k]; } }
function load(src, cb){ var s = document.createElement('script'); s.src = src; s.onload = cb; s.onerror = cb; document.head.appendChild(s); }
function fold(w){ return w.toLowerCase().replace(/ß/g, 'ss').normalize('NFD').replace(/[̀-ͯ]/g, ''); }
function key(w){ var k = w.slice(0, 2).replace(/[^a-z0-9]/g, '_'); while (k.length < 2) k += '_'; return k; }
function shard(k, cb){ if (IX[k]) return cb(); if (waiting[k]) return waiting[k].push(cb); waiting[k] = [cb]; load('search/ix_' + k + '.js', function(){ if (!IX[k]) { IX[k] = {}; BEEIX(k, {}); } }); }
function decode(s){ var out = [], p = 0; s.split(',').forEach(function(x){ p += parseInt(x, 36); out.push(p); }); return out; }
function postings(w, cb){
  var pre = /\*$/.test(w); w = fold(w.replace(/\*$/, ''));
  if (w.length < 2) return cb(null);
  shard(key(w), function(){
    var d = IX[key(w)] || {}, set = new Set();
    if (pre) { for (var k in d) if (k.indexOf(w) === 0) decode(d[k]).forEach(function(u){ set.add(u); }); }
    else if (d[w]) decode(d[w]).forEach(function(u){ set.add(u); });
    cb(set);
  });
}
function run(){
  var raw = document.getElementById('q').value.trim(), v = document.querySelector('input[name=v]:checked').value;
  var R = document.getElementById('r'); if (!raw) { R.innerHTML = ''; return; }
  var words = (raw.match(/"[^"]*"|\S+/g) || []).map(function(x){ return x.replace(/"/g, ''); }).join(' ').split(/[^\p{L}\p{N}*]+/u).filter(function(w){ return w.replace(/\*/g, '').length >= 2; });
  R.textContent = 'Suche …';
  var sets = [], left = words.length;
  if (!left) { R.textContent = 'Bitte mindestens ein Wort mit zwei Buchstaben.'; return; }
  words.forEach(function(w, i){ postings(w, function(s){ sets[i] = s || new Set(); if (--left === 0) show(sets, words, raw, v); }); });
}
function show(sets, words, raw, v){
  sets.sort(function(a, b){ return a.size - b.size; });
  var hits = [...sets[0]].filter(function(u){ return sets.every(function(s){ return s.has(u); }) && (v === 'both' || UNITS[u][1] === v); });
  var R = document.getElementById('r'), q = encodeURIComponent(raw.replace(/"/g, ''));
  var html = '';
  if (document.getElementById('t').checked) {
    var fw = words.map(function(w){ return fold(w.replace(/\*$/, '')); });
    var tt = Object.keys(TITLES).filter(function(n){ var t = fold(n + ' ' + TITLES[n]); return fw.every(function(w){ return t.indexOf(w) >= 0; }); });
    if (tt.length) html += '<h2>Titel</h2>' + tt.map(function(n){ return '<div class="u"><a href="items/' + n + '.norm.html">' + n + '</a> ' + TITLES[n] + '</div>'; }).join('');
  }
  html += '<h2>Texte: ' + hits.length + (hits.length === 1 ? ' Stelle' : ' Stellen') + (hits.length > 2000 ? ' (die ersten 2000)' : '') + '</h2>';
  var by = {}, order = [];
  hits.slice(0, 2000).forEach(function(u){ var x = UNITS[u], k = x[0] + '.' + x[1]; if (!by[k]) { by[k] = []; order.push(k); } by[k].push(x); });
  order.forEach(function(k){
    var x0 = by[k][0];
    html += '<div class="it">' + x0[0] + ' <span class="n">' + (x0[1] === 'norm' ? 'normalisiert' : 'diplomatisch') + '</span> ' + (TITLES[x0[0]] || '') + ' <span class="n">(' + by[k].length + ')</span></div><div class="u">' +
      by[k].map(function(x){ return '<a href="items/' + x[0] + '.' + x[1] + '.html?q=' + q + '#' + x[2] + '">' + (x[3] || '·') + '</a>'; }).join('') + '</div>';
  });
  R.innerHTML = html;
}
load('search/units.js', function(){});
document.getElementById('f').onsubmit = function(e){ e.preventDefault(); if (!UNITS) { setTimeout(run, 300); return; } run(); };
var q0 = new URLSearchParams(location.search).get('q'); if (q0) { document.getElementById('q').value = q0; setTimeout(function wait(){ UNITS ? run() : setTimeout(wait, 200); }, 50); }
</script></body></html>''')
tot = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
print(len(units), 'units,', len(post), 'words,', len(shards), 'shards,', round(tot / 1e6, 1), 'MB')
