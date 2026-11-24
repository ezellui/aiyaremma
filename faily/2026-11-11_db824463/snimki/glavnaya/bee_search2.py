#!/usr/bin/env python3
"""bee_search2.py XMLDIR SITEDIR — search data for the static site (file:// works, no server).

Units: a record (<rec>) of the normalized version, a page (text between <pb>) of the diplomatic one.
  search/units.js        BEEUNITS(units, items): unit -> [item, version, anchor, label, year];
                         items: n -> [title, group, ...series ids]
  search/ix_<ab>.js      full text: folded word -> base-36 deltas of units (split by first two letters)
  search/fx_<field>.js   field indexes (person, lang_en, lang_fr, lang_la, coded, notation, xref, emend)
  search/tx/<n>.<v>.js   the plain text of the units of one item (context lines, phrases, NEAR)
Words are folded: lower case, accents removed, ß -> ss."""
import sys, os, re, json, unicodedata, collections
import xml.etree.ElementTree as ET

xmldir, site = sys.argv[1], sys.argv[2]
WORK = '/home/claude/work'
ITEMS = [l.split()[1] for l in open(f'{WORK}/items.txt')]
TITLES = {}
for l in open(f'{WORK}/items.txt'):
    p = l.split(None, 2); TITLES[p[1]] = p[2].strip() if len(p) > 2 else ''
SERIES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'series.json')))['series']
GROUPS = json.load(open(f'{WORK}/print/fields/groups.json')) if os.path.exists(f'{WORK}/print/fields/groups.json') else {}
out = os.path.join(site, 'search'); os.makedirs(os.path.join(out, 'tx'), exist_ok=True)
WORD = re.compile(r'[^\W_]+', re.U)
SKIP = {'person', 'notation', 'num'}


def fold(w):
    w = w.lower().replace('ß', 'ss')
    return ''.join(c for c in unicodedata.normalize('NFD', w) if not unicodedata.combining(c))


def plain(el):
    """visible text of an element; <lb/> and <pb/> become spaces"""
    acc = []

    def walk(e):
        if e.tag in SKIP:
            if e.tail: acc.append(e.tail)
            return
        if e.tag in ('lb', 'pb'):
            acc.append(' ')
        if e.text: acc.append(e.text)
        for k in e:
            walk(k)
        if e.tail: acc.append(e.tail)
    if el.text: acc.append(el.text)
    for k in el:
        walk(k)
    return re.sub(r'\s+', ' ', ''.join(acc)).strip()


def year(d):
    m = re.search(r'(\d{4})', d or '')
    return int(m.group(1)) if m else 0


def pid(n):
    return 'p-' + re.sub(r'[^\w.-]', '_', n)


units = []
full = collections.defaultdict(list)
fields = collections.defaultdict(lambda: collections.defaultdict(list))
texts = collections.defaultdict(list)          # "n.v" -> [unit text]
first_unit = {}


def add(index, text, u):
    seen = set()
    for w in WORD.findall(text):
        f = fold(w)
        if len(f) < 2 and not f.isdigit():
            continue
        if f not in seen:
            seen.add(f); index[f].append(u)


def add_fields(el, u):
    for x in el.iter():
        if x.tag == 'person' and x.get('key'):
            add(fields['person'], x.get('key'), u)
        elif x.tag == 'foreign' and x.get('lang') in ('en', 'fr', 'la'):
            add(fields['lang_' + x.get('lang')], plain(x), u)
        elif x.tag == 'hi' and x.get('rend') in ('code', 'coded'):
            add(fields['coded'], plain(x), u)
        elif x.tag == 'ref':
            add(fields['xref'], plain(x), u)
        elif x.tag == 'formula' and x.get('notation'):
            add(fields['notation'], x.get('notation'), u)
        elif x.tag == 'figure' and x.get('desc'):
            add(fields['notation'], x.get('desc'), u)
        elif x.tag == 'notation' and x.get('key'):
            add(fields['notation'], x.get('key'), u)


def unit(n, v, anchor, label, yr, text, el):
    u = len(units)
    units.append([n, v, anchor, label, yr])
    key = f'{n}.{v}'
    first_unit.setdefault(key, u)
    texts[key].append(text)
    add(full, text, u)
    add_fields(el, u)


for n in ITEMS:
    f = os.path.join(xmldir, f'{n}.norm.xml')
    if os.path.exists(f):
        r = ET.parse(f).getroot()
        for k, rec in enumerate([x for x in r if x.tag == 'rec']):
            d = rec.get('date') or ''
            label = rec.get('page', '') + ((' · ' + d) if d else '')
            unit(n, 'norm', f'r-{n}-{k}', label, year(d), plain(rec), rec)
    f = os.path.join(xmldir, f'{n}.diplo.xml')
    if os.path.exists(f):
        r = ET.parse(f).getroot()
        # pages: everything from one <pb> to the next, as a pseudo element
        pages = [[None, ET.Element('page')]]

        def walk(el):
            if el.tag == 'pb':
                pages.append([el.get('n', ''), ET.Element('page')])
                if el.tail:
                    t = ET.SubElement(pages[-1][1], 'seg'); t.text = el.tail
                return
            c = ET.SubElement(pages[-1][1], el.tag, el.attrib)
            c.text = el.text
            for k in el:
                walk(k)
            if el.tail:
                t = ET.SubElement(pages[-1][1], 'seg'); t.text = el.tail
        for k in r:
            walk(k)
        lastyear = 0
        for pg, el in pages:
            txt = plain(el)
            for dt in el.iter('date'):
                lastyear = year(dt.get('when')) or lastyear
            if not txt:
                continue
            unit(n, 'diplo', pid(pg) if pg else f'item-{n}', pg or '', lastyear, txt, el)


def b36(x):
    s = ''
    while True:
        x, r = divmod(x, 36); s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not x: return s


def enc(us):
    prev = 0; o = []
    for u in us:
        o.append(b36(u - prev)); prev = u
    return ','.join(o)


shards = collections.defaultdict(dict)
for w, us in full.items():
    key = re.sub(r'[^a-z0-9]', '_', w[:2]).ljust(2, '_')
    shards[key][w] = enc(us)
for f in os.listdir(out):
    if f.startswith(('ix_', 'fx_')):
        os.remove(os.path.join(out, f))
for key, d in shards.items():
    open(os.path.join(out, f'ix_{key}.js'), 'w', encoding='utf-8').write(
        f'BEEIX({json.dumps(key)},' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
for fld, idx in fields.items():
    open(os.path.join(out, f'fx_{fld}.js'), 'w', encoding='utf-8').write(
        f'BEEFX({json.dumps(fld)},' + json.dumps({w: enc(us) for w, us in idx.items()}, ensure_ascii=False, separators=(',', ':')) + ');')
for key, tx in texts.items():
    open(os.path.join(out, 'tx', f'{key}.js'), 'w', encoding='utf-8').write(
        f'BEETX({json.dumps(key)},{first_unit[key]},' + json.dumps(tx, ensure_ascii=False, separators=(',', ':')) + ');')


def group(n):
    if n in GROUPS:
        return GROUPS[n]
    return ['manuscripts'] if n[0] == '1' else ['typescripts'] if n[0] == '2' else ['dictations']


items_meta = {n: [TITLES.get(n, ''), group(n), [s['id'] for s in SERIES if n in s['items']]] for n in ITEMS}
series_meta = {s['id']: s['title'] for s in SERIES}
open(os.path.join(out, 'units.js'), 'w', encoding='utf-8').write(
    'BEEUNITS(' + json.dumps(units, ensure_ascii=False, separators=(',', ':')) + ',' +
    json.dumps(items_meta, ensure_ascii=False, separators=(',', ':')) + ',' +
    json.dumps(series_meta, ensure_ascii=False) + ',' +
    json.dumps({f: len(v) for f, v in fields.items()}) + ');')
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
print(len(units), 'units,', len(full), 'words,', len(shards), 'shards,', {f: len(v) for f, v in fields.items()},
      round(tot / 1e6, 1), 'MB')
