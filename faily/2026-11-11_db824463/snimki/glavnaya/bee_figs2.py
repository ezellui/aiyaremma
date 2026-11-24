#!/usr/bin/env python3
"""bee_figs2.py SCREEN_DIR HITS_XML_DIR A_XML_DIR OUT_DIR VERSION
Figure placement without relying on the record markers seen on screen (they are missed or doubled
now and then). Both sides are reduced to a sequence of figures in the order of the "records with
hits" view:
  screen  — every captured bitmap, with the number of descriptor characters of the highlighted boxes
            since the previous bitmap (a box is 8 px per character + 16 px);
  text    — every <figure missing="1" desc=…/> placeholder of the text print of the same view, with
            the length of its descriptor (one placeholder may stand for several bitmaps).
A banded dynamic programme matches each placeholder with 1–4 consecutive bitmaps by descriptor
length. Each matched text record is found again in pass A (same item and page, most similar text)
and its placeholder receives the bitmaps. Report: OUT_DIR/figs.VERSION.json."""
import sys, os, json, shutil, difflib, re, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/scripts')
import bee_pdf2xml as B

scr, hitsdir, adir, out, ver = sys.argv[1:6]
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]

# ---- screen sequence (chunk overlaps removed)
chunks = []
for f in sorted(glob.glob(os.path.join(scr, 'figs_*.jsonl'))):
    chunks.append([json.loads(l) for l in open(f)])
Sseq = []
prev_imgs = []
for ev in chunks:
    figs = [e for e in ev if e['kind'] == 'fig']
    imgs = [e['img'] for e in figs if e.get('img')]
    ov = 0
    for k in range(1, min(20, len(prev_imgs), len(imgs)) + 1):
        if prev_imgs[-k:] == imgs[:k]:
            ov = k
    skip = ov
    acc = 0.0
    for e in figs:
        acc += max(0.0, (e['box'][0] - 16) / 8)
        if e.get('img'):
            if skip:
                skip -= 1; acc = 0.0; continue
            Sseq.append((acc, e)); acc = 0.0
    prev_imgs = imgs

# ---- text sequence
def sig(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()[:400]


T = []          # records
Tseq = []       # (chars, record index, placeholder index)
for n in ITEMS:
    f = os.path.join(hitsdir, f'{n}.{ver}.xml')
    if not os.path.exists(f):
        continue
    for rec in ET.parse(f).getroot().iter('rec'):
        phs = [x for x in rec.iter('figure') if x.get('missing')]
        T.append({'item': n, 'page': rec.get('page'), 'sig': sig(rec), 'ph': len(phs)})
        for k, x in enumerate(phs):
            Tseq.append((len(re.sub(r'\s+', ' ', x.get('desc') or '').strip()), len(T) - 1, k))

n, m = len(Sseq), len(Tseq)
rep = {'screen_images': n, 'placeholders': m}


def cost(a, b):
    return min(3.0, abs(a - b) / max(6.0, 0.10 * max(a, b)))


# banded DP over (screen i, text j)
BAND = 400
INF = float('inf')
D = {}
P = {}
D[(0, 0)] = 0.0
GS, GT = 1.4, 1.2
for i in range(n + 1):
    jc = round(i * m / max(n, 1))
    for j in range(max(0, jc - BAND), min(m, jc + BAND) + 1):
        c0 = D.get((i, j), INF)
        if c0 == INF:
            continue
        if i < n:
            c = c0 + GS
            if c < D.get((i + 1, j), INF): D[(i + 1, j)] = c; P[(i + 1, j)] = (i, j, 0)
        if j < m:
            c = c0 + GT
            if c < D.get((i, j + 1), INF): D[(i, j + 1)] = c; P[(i, j + 1)] = (i, j, 0)
        if j < m:
            tot = 0.0
            for k in range(1, 5):
                if i + k > n: break
                tot += Sseq[i + k - 1][0] + (1 if k > 1 else 0)
                c = c0 + cost(tot, Tseq[j][0]) + 0.3 * (k - 1)
                if c < D.get((i + k, j + 1), INF): D[(i + k, j + 1)] = c; P[(i + k, j + 1)] = (i, j, k)
# back-trace
match = {}      # text j -> list of screen indices
i, j = n, m
if (i, j) not in P:
    sys.exit('no path through the band')
while (i, j) != (0, 0):
    pi, pj, k = P[(i, j)]
    if k:
        match[pj] = list(range(pi, pi + k))
    i, j = pi, pj
rep['placeholders_matched'] = len(match)
rep['images_matched'] = sum(len(v) for v in match.values())
rep['mean_cost'] = round(D[(n, m)] / max(1, m), 3)

# ---- pass A
os.makedirs(os.path.join(out, 'img'), exist_ok=True)
docs = {}
for it in ITEMS:
    f = os.path.join(adir, f'{it}.{ver}.xml')
    if os.path.exists(f):
        docs[it] = ET.parse(f).getroot()
recmap = {}
used = set()


def a_record(ti):
    if ti in recmap:
        return recmap[ti]
    t = T[ti]
    root = docs.get(t['item'])
    best = None
    if root is not None:
        cands = [r for r in root.iter('rec') if r.get('page') == t['page'] and id(r) not in used]
        if not cands:
            cands = [r for r in root.iter('rec') if id(r) not in used]
        best = max(cands, key=lambda r: difflib.SequenceMatcher(None, sig(r), t['sig']).quick_ratio(), default=None)
        if best is not None:
            used.add(id(best))
    recmap[ti] = best
    return best


stats = {'placed': 0, 'extra_in_placeholder': 0, 'no_placeholder_in_A': 0, 'no_A_record': 0}
for j in sorted(match):
    _, ti, k = Tseq[j]
    rec = a_record(ti)
    if rec is None:
        stats['no_A_record'] += 1; continue
    phs = [x for x in rec.iter('figure') if x.get('missing') or x.get('ph') is not None]
    for x in phs:
        if x.get('ph') is None:
            x.set('ph', str(phs.index(x)))
    target = next((x for x in phs if x.get('ph') == str(k)), None)
    imgs = [Sseq[i][1] for i in match[j]]
    for e in imgs:
        shutil.copy(os.path.join(scr, 'img', e['img']), os.path.join(out, 'img', e['img']))
    if target is None:
        # A has fewer placeholders here: append after its last figure, or at the end of the record
        stats['no_placeholder_in_A'] += len(imgs)
        ps = rec.findall('p') or [ET.SubElement(rec, 'p')]
        for e in imgs:
            ET.SubElement(ps[-1], 'figure', {'src': 'img/' + e['img'], 'w': str(e['w']), 'h': str(e['h']),
                                             'place': 'unanchored'}).tail = ''
        continue
    parent = {c: p for p in rec.iter() for c in p}
    desc = target.get('desc')
    first = imgs[0]
    target.attrib.clear()
    target.attrib.update({'src': 'img/' + first['img'], 'w': str(first['w']), 'h': str(first['h'])})
    if desc: target.set('desc', desc)
    stats['placed'] += 1
    pa = parent[target]; idx = list(pa).index(target); last = target
    for e in imgs[1:]:
        new = ET.Element('figure', {'src': 'img/' + e['img'], 'w': str(e['w']), 'h': str(e['h'])})
        new.tail = last.tail; last.tail = ''
        idx += 1; pa.insert(idx, new); last = new
        stats['extra_in_placeholder'] += 1
left = 0
for it, root in docs.items():
    for x in root.iter('figure'):
        if 'ph' in x.attrib:
            del x.attrib['ph']
        if x.get('missing'):
            left += 1
    B.indent_blocks(root)
    ET.ElementTree(root).write(os.path.join(out, f'{it}.{ver}.xml'), encoding='utf-8', xml_declaration=True)
src = os.path.join(adir, 'img')
if os.path.isdir(src):
    for fn in os.listdir(src):
        if not os.path.exists(os.path.join(out, 'img', fn)):
            shutil.copy(os.path.join(src, fn), os.path.join(out, 'img', fn))
stats['placeholders_left_in_A'] = left
rep.update(stats)
json.dump(rep, open(os.path.join(out, f'figs.{ver}.json'), 'w'), indent=1)
print(json.dumps(rep))
