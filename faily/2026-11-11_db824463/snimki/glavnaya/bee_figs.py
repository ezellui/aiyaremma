#!/usr/bin/env python3
"""bee_figs.py SCREEN_DIR HITS_XML_DIR A_XML_DIR OUT_DIR VERSION
Put the figures captured from the screen (fig_capture.py) into the pass-A XML.

  SCREEN_DIR/figs.jsonl   record markers and figures, in the order of the "records with hits" view
  HITS_XML_DIR            the same view printed as text (no bitmaps) and converted: gives, record by
                          record, item, page and the figure placeholders, in the same order
  A_XML_DIR               the full text (pass A), one XML per item

Screen records and hit records are aligned (1:1 when the counts agree, otherwise by dynamic
programming on the number of figures); each hit record is found again in pass A (same item and page,
most similar text) and its <figure missing="1"/> placeholders receive the images in order. Extra
images go after the last placeholder; images of a record without placeholder are appended to it with
place="unanchored". Report: OUT_DIR/figs.VERSION.json."""
import sys, os, json, shutil, difflib, re
import xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/scripts')
import bee_pdf2xml as B

scr, hitsdir, adir, out, ver = sys.argv[1:6]
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]

# ---- screen records
ev = [json.loads(l) for l in open(os.path.join(scr, 'figs.jsonl'))]
marks = sorted(e['y'] for e in ev if e['kind'] == 'rec')
S = [[] for _ in marks]
import bisect
for e in ev:
    if e['kind'] != 'fig':
        continue
    bottom = e['y'] + e['box'][1]
    k = bisect.bisect_right(marks, bottom) - 1
    S[max(k, 0)].append(e)
for s in S:
    s.sort(key=lambda e: (e['y'] + e['box'][1], e['x']))      # reading order: by line (bottom), then x


def sig(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()[:400]


# ---- hit records (text print of the same view)
T = []
for n in ITEMS:
    f = os.path.join(hitsdir, f'{n}.{ver}.xml')
    if not os.path.exists(f):
        continue
    for rec in ET.parse(f).getroot().iter('rec'):
        T.append({'item': n, 'page': rec.get('page'), 'sig': sig(rec),
                  'ph': len([x for x in rec.iter('figure') if x.get('missing')])})

nimg = [sum(1 for e in s if e.get('img')) for s in S]
rep = {'screen_records': len(S), 'hit_records': len(T), 'screen_images': sum(nimg)}

# ---- align S and T
if len(S) == len(T):
    pairs = list(range(len(S)))
    rep['alignment'] = '1:1'
else:
    # DP: match cost |images - placeholders| (capped), gap cost 1.5
    n, m = len(S), len(T)
    INF = 1e18
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    P = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] == INF:
                continue
            if i < n and j < m:
                c = D[i][j] + min(abs(nimg[i] - T[j]['ph']), 3)
                if c < D[i + 1][j + 1]: D[i + 1][j + 1] = c; P[i + 1][j + 1] = (i, j)
            if i < n and D[i][j] + 1.5 < D[i + 1][j]: D[i + 1][j] = D[i][j] + 1.5; P[i + 1][j] = (i, j)
            if j < m and D[i][j] + 1.5 < D[i][j + 1]: D[i][j + 1] = D[i][j] + 1.5; P[i][j + 1] = (i, j)
    pairs = [None] * n
    i, j = n, m
    while (i, j) != (0, 0):
        pi, pj = P[i][j]
        if pi == i - 1 and pj == j - 1:
            pairs[i - 1] = j - 1
        i, j = pi, pj
    rep['alignment'] = 'dp'
    rep['screen_unmatched'] = sum(1 for p in pairs if p is None)

# ---- pass A
os.makedirs(os.path.join(out, 'img'), exist_ok=True)
docs = {}
for n in ITEMS:
    f = os.path.join(adir, f'{n}.{ver}.xml')
    if os.path.exists(f):
        docs[n] = ET.parse(f).getroot()
stats = {'placed': 0, 'extra': 0, 'unanchored': 0, 'no_A_record': 0, 'unmatched_screen': 0,
         'placeholders_left': 0}
used = set()
for i, s in enumerate(S):
    imgs = [e for e in s if e.get('img')]
    if not imgs:
        continue
    j = pairs[i]
    if j is None:
        stats['unmatched_screen'] += len(imgs); continue
    t = T[j]
    root = docs.get(t['item'])
    if root is None:
        stats['no_A_record'] += len(imgs); continue
    cands = [r for r in root.iter('rec') if r.get('page') == t['page'] and id(r) not in used]
    if not cands:
        cands = [r for r in root.iter('rec') if id(r) not in used]
    best = max(cands, key=lambda r: difflib.SequenceMatcher(None, sig(r), t['sig']).quick_ratio(), default=None)
    if best is None:
        stats['no_A_record'] += len(imgs); continue
    used.add(id(best))
    phs = [x for x in best.iter('figure') if x.get('missing')]
    parent = {c: p for p in best.iter() for c in p}
    for k, e in enumerate(imgs):
        shutil.copy(os.path.join(scr, 'img', e['img']), os.path.join(out, 'img', e['img']))
        attrs = {'src': 'img/' + e['img'], 'w': str(e['w']), 'h': str(e['h'])}
        if k < len(phs):
            ph = phs[k]
            desc = ph.get('desc')
            ph.attrib.clear(); ph.attrib.update(attrs)
            if desc: ph.set('desc', desc)
            stats['placed'] += 1
        elif phs:
            last = phs[-1]; pa = parent[last]
            idx = list(pa).index(last)
            new = ET.Element('figure', attrs); new.tail = last.tail; last.tail = ''
            pa.insert(idx + 1, new); phs.append(new); parent[new] = pa
            stats['extra'] += 1
        else:
            ps = best.findall('p') or [ET.SubElement(best, 'p')]
            new = ET.SubElement(ps[-1], 'figure', dict(attrs, place='unanchored')); new.tail = ''
            stats['unanchored'] += 1
for root in docs.values():
    stats['placeholders_left'] += sum(1 for x in root.iter('figure') if x.get('missing'))
for n, root in docs.items():
    B.indent_blocks(root)
    ET.ElementTree(root).write(os.path.join(out, f'{n}.{ver}.xml'), encoding='utf-8', xml_declaration=True)
    src = os.path.join(adir, 'img')
    if os.path.isdir(src):
        for fn in os.listdir(src):
            if not os.path.exists(os.path.join(out, 'img', fn)):
                shutil.copy(os.path.join(src, fn), os.path.join(out, 'img', fn))
rep.update(stats)
json.dump(rep, open(os.path.join(out, f'figs.{ver}.json'), 'w'), indent=1)
print(json.dumps(rep))
