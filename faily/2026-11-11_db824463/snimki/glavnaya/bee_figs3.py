#!/usr/bin/env python3
"""bee_figs3.py SCREEN_DIR HITS_XML_DIR A_XML_DIR OUT_DIR VERSION
Second figure pass, for the notation view (query Mathematics | Logic | Set Theory | Notation).
Here most highlighted descriptors stand before notation that is ordinary text; only some stand
before a bitmap. So every descriptor is aligned, not only the bitmaps:
  screen — every highlighted box (8 px per character + 16 px), with the bitmap to its right if any;
  text   — every descriptor of the text print of the same view, in order: <formula notation=…>
           and <figure desc=… missing="1"/> (the descriptor-only placeholders).
A banded dynamic programme matches each text descriptor with 1–4 consecutive boxes (a descriptor
breaks over lines). Placeholders matched to boxes with a bitmap receive it in pass A, where the
same record is found again (item, page, text) and the k-th original figure of the record is the
target; figures already filled (the Graphics pass) are left alone. Report: OUT_DIR/figs3.VERSION.json"""
import sys, os, json, shutil, difflib, re, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/scripts')
import bee_pdf2xml as B

scr, hitsdir, adir, out, ver = sys.argv[1:6]
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]

# ---- screen: all boxes, chunk overlaps removed by the box-width sequence
Sseq = []
prev = []
for f in sorted(glob.glob(os.path.join(scr, 'figs_*.jsonl'))):
    figs = [json.loads(l) for l in open(f)]
    figs = [e for e in figs if e['kind'] == 'fig']
    sig = [(e['box'][0], e.get('img')) for e in figs]
    ov = 0
    for k in range(1, min(40, len(prev), len(sig)) + 1):
        if prev[-k:] == sig[:k]:
            ov = k
    for e in figs[ov:]:
        Sseq.append((max(0.0, (e['box'][0] - 16) / 8), e))
    prev = sig


def sigt(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()[:400]


T = []; Tseq = []
for n in ITEMS:
    f = os.path.join(hitsdir, f'{n}.{ver}.xml')
    if not os.path.exists(f):
        continue
    for rec in ET.parse(f).getroot().iter('rec'):
        T.append({'item': n, 'page': rec.get('page'), 'sig': sigt(rec)})
        k = 0
        for x in rec.iter():
            if x.tag == 'figure':
                Tseq.append((len((x.get('desc') or '').strip()), len(T) - 1, k)); k += 1
            elif x.tag == 'formula' and x.get('notation'):
                Tseq.append((len(x.get('notation').strip()), len(T) - 1, None))

n, m = len(Sseq), len(Tseq)
rep = {'boxes': n, 'descriptors': m, 'bitmaps_seen': sum(1 for _, e in Sseq if e.get('img'))}


def cost(a, b):
    return min(3.0, abs(a - b) / max(4.0, 0.08 * max(a, b)))


BAND = 1200
INF = float('inf')
D = {(0, 0): 0.0}; P = {}
for i in range(n + 1):
    jc = round(i * m / max(n, 1))
    for j in range(max(0, jc - BAND), min(m, jc + BAND) + 1):
        c0 = D.get((i, j), INF)
        if c0 == INF:
            continue
        if i < n:
            c = c0 + 1.3
            if c < D.get((i + 1, j), INF): D[(i + 1, j)] = c; P[(i + 1, j)] = (i, j, 0)
        if j < m:
            c = c0 + 1.3
            if c < D.get((i, j + 1), INF): D[(i, j + 1)] = c; P[(i, j + 1)] = (i, j, 0)
            tot = 0.0
            for k in range(1, 5):
                if i + k > n: break
                tot += Sseq[i + k - 1][0] + (1 if k > 1 else 0)
                c = c0 + cost(tot, Tseq[j][0]) + 0.2 * (k - 1)
                if c < D.get((i + k, j + 1), INF): D[(i + k, j + 1)] = c; P[(i + k, j + 1)] = (i, j, k)
    # keep memory bounded: rows far behind are no longer needed
    if i > 6:
        for j in range(max(0, round((i - 6) * m / max(n, 1)) - BAND), min(m, round((i - 6) * m / max(n, 1)) + BAND) + 1):
            D.pop((i - 6, j), None)
match = {}
i, j = n, m
while (i, j) != (0, 0):
    pi, pj, k = P[(i, j)]
    if k:
        match[pj] = list(range(pi, pi + k))
    i, j = pi, pj
rep['descriptors_matched'] = len(match)

docs = {}
for it in ITEMS:
    f = os.path.join(adir, f'{it}.{ver}.xml')
    if os.path.exists(f):
        docs[it] = ET.parse(f).getroot()
os.makedirs(os.path.join(out, 'img'), exist_ok=True)
recmap, used = {}, set()


def a_record(ti):
    if ti not in recmap:
        t = T[ti]; root = docs.get(t['item']); best = None
        if root is not None:
            cands = [r for r in root.iter('rec') if r.get('page') == t['page'] and id(r) not in used] or \
                    [r for r in root.iter('rec') if id(r) not in used]
            best = max(cands, key=lambda r: difflib.SequenceMatcher(None, sigt(r), t['sig']).quick_ratio(), default=None)
            if best is not None: used.add(id(best))
        recmap[ti] = best
    return recmap[ti]


stats = {'placed': 0, 'already_filled': 0, 'no_target': 0, 'bitmaps_on_text_descriptors': 0}
for j, idx in sorted(match.items()):
    _, ti, k = Tseq[j]
    imgs = [Sseq[i][1] for i in idx if Sseq[i][1].get('img')]
    if not imgs:
        continue
    if k is None:
        stats['bitmaps_on_text_descriptors'] += len(imgs); continue      # notation that is text in A
    rec = a_record(ti)
    if rec is None:
        stats['no_target'] += 1; continue
    figs = [x for x in rec.iter('figure') if not x.get('extra') and not x.get('place')]
    if k >= len(figs):
        stats['no_target'] += 1; continue
    t = figs[k]
    if t.get('src'):
        stats['already_filled'] += 1; continue
    e = imgs[0]
    shutil.copy(os.path.join(scr, 'img', e['img']), os.path.join(out, 'img', e['img']))
    desc = t.get('desc')
    t.attrib.clear(); t.attrib.update({'src': 'img/' + e['img'], 'w': str(e['w']), 'h': str(e['h'])})
    if desc: t.set('desc', desc)
    stats['placed'] += 1
for it, root in docs.items():
    B.indent_blocks(root)
    ET.ElementTree(root).write(os.path.join(out, f'{it}.{ver}.xml'), encoding='utf-8', xml_declaration=True)
src = os.path.join(adir, 'img')
if os.path.isdir(src):
    for fn in os.listdir(src):
        if not os.path.exists(os.path.join(out, 'img', fn)):
            shutil.copy(os.path.join(src, fn), os.path.join(out, 'img', fn))
stats['placeholders_left'] = sum(1 for r in docs.values() for x in r.iter('figure') if x.get('missing'))
rep.update(stats)
json.dump(rep, open(os.path.join(out, f'figs3.{ver}.json'), 'w'), indent=1)
print(json.dumps(rep))
