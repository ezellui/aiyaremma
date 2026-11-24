#!/usr/bin/env python3
"""bee_figs_diplo.py NORM_DIR DIPLO_DIR OUT_DIR
The diplomatic printout marks a figure only by its descriptor (<notation key="Vierecke; Quadrat"/>);
the bitmaps are the same as in the normalized version. Each figure of the normalized XML (with
src, after bee_figs.py) is attached to the diplomatic descriptor with the same text on the same
facsimile page (pb/@facs), in order. Report: OUT_DIR/figs.diplo.json."""
import sys, os, json, shutil, re
import xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/scripts')
import bee_pdf2xml as B

ndir, ddir, out = sys.argv[1:4]
os.makedirs(os.path.join(out, 'img'), exist_ok=True)
norm = lambda s: re.sub(r'\W+', ' ', s or '').strip().lower()
stats = {'figures_norm': 0, 'attached': 0, 'unattached_norm': 0}
unused = []
for f in sorted(os.listdir(ddir)):
    m = re.match(r'(.+)\.diplo\.xml$', f)
    if not m:
        continue
    n = m.group(1)
    droot = ET.parse(os.path.join(ddir, f)).getroot()
    nf = os.path.join(ndir, f'{n}.norm.xml')
    if os.path.exists(nf):
        figs = {}
        facs = None
        for el in ET.parse(nf).getroot().iter():
            if el.tag == 'pb' and el.get('facs'):
                facs = el.get('facs')
            elif el.tag == 'figure' and el.get('src'):
                figs.setdefault(facs, []).append([norm(el.get('desc')), el, False])
                stats['figures_norm'] += 1
        parent = {c: p for p in droot.iter() for c in p}
        facs = None
        for el in list(droot.iter()):
            if el.tag == 'pb' and el.get('facs'):
                facs = el.get('facs')
            elif el.tag == 'notation' and el.get('key'):
                k = norm(el.get('key'))
                if len(k) < 4:
                    continue
                for cand in figs.get(facs, []):
                    if cand[2]:
                        continue
                    d = cand[0]
                    if d and (d == k or k in d or d in k):
                        cand[2] = True
                        src = cand[1]
                        new = ET.Element('figure', {a: v for a, v in src.attrib.items() if a in ('src', 'w', 'h', 'desc')})
                        pa = parent[el]; i = list(pa).index(el)
                        new.tail = el.tail; el.tail = ''
                        pa.insert(i + 1, new); parent[new] = pa
                        fn = os.path.join(ndir, src.get('src'))
                        if os.path.exists(fn):
                            shutil.copy(fn, os.path.join(out, 'img', os.path.basename(fn)))
                        stats['attached'] += 1
                        break
        for lst in figs.values():
            for d, el, used in lst:
                if not used:
                    stats['unattached_norm'] += 1; unused.append((n, d, el.get('src')))
    B.indent_blocks(droot)
    ET.ElementTree(droot).write(os.path.join(out, f), encoding='utf-8', xml_declaration=True)
src = os.path.join(ddir, 'img')
if os.path.isdir(src):
    for fn in os.listdir(src):
        shutil.copy(os.path.join(src, fn), os.path.join(out, 'img', fn))
stats['unattached_sample'] = unused[:30]
json.dump(stats, open(os.path.join(out, 'figs.diplo.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in stats.items() if k != 'unattached_sample'}))
