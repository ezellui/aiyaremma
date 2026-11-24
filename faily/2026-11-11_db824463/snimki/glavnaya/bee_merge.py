#!/usr/bin/env python3
"""bee_merge.py A_DIR B_DIR OUT_DIR VERSION
Pass A (whole text, no bitmaps) + pass B (records with pictures, bitmaps on) -> merged XML.
A record of B replaces the record of A on the same page with the most similar text (pictures and
descriptors aside). Report: merge.VERSION.json (matched, unmatched B records, A placeholders left)."""
import sys, os, re, glob, json, shutil, difflib
import xml.etree.ElementTree as ET

a_dir, b_dir, out, ver = sys.argv[1:5]
os.makedirs(out, exist_ok=True)


def sig(rec):
    t = ''.join(x for e in rec.iter() if e.tag not in ('figure', 'person') for x in (e.text or '',))
    t = ' '.join(''.join(rec.itertext()).split())
    return re.sub(r'[^\w]', '', t.lower())[:400]


def load(d):
    res = {}
    for f in glob.glob(os.path.join(d, f'*.{ver}.xml')):
        r = ET.parse(f).getroot()
        res[r.get('n')] = (f, r)
    return res


A, B = load(a_dir), load(b_dir)
rep = {'matched': 0, 'unmatched': [], 'placeholders_left': 0, 'figures_in': 0}
for n, (fa, ra) in A.items():
    if n in B:
        recs_a = list(ra.iter('rec'))
        bypage = {}
        for r in recs_a:
            bypage.setdefault(r.get('page'), []).append(r)
        used = set()
        for rb in B[n][1].iter('rec'):
            cands = [r for r in bypage.get(rb.get('page'), []) if id(r) not in used]
            if not cands:
                # the page attribute can differ at page breaks: try all records
                cands = [r for r in recs_a if id(r) not in used]
            sb = sig(rb)
            best, score = None, 0.0
            for r in cands:
                s = difflib.SequenceMatcher(None, sig(r), sb, autojunk=False).ratio()
                if s > score:
                    best, score = r, s
            if best is not None and score >= 0.6:
                used.add(id(best))
                best.clear()
                best.attrib.update(rb.attrib)
                best.text = rb.text
                for k in list(rb):
                    best.append(k)
                rep['matched'] += 1
            else:
                rep['unmatched'].append({'item': n, 'page': rb.get('page'), 'score': round(score, 2),
                                         'text': ' '.join(''.join(rb.itertext()).split())[:120]})
    rep['placeholders_left'] += sum(1 for f in ra.iter('figure') if f.get('missing'))
    rep['figures_in'] += sum(1 for f in ra.iter('figure') if not f.get('missing'))
    ET.indent(ra, space=' ')
    ET.ElementTree(ra).write(os.path.join(out, os.path.basename(fa)), encoding='utf-8', xml_declaration=True)
for d in (a_dir, b_dir):
    if os.path.isdir(os.path.join(d, 'img')):
        shutil.copytree(os.path.join(d, 'img'), os.path.join(out, 'img'), dirs_exist_ok=True)
json.dump(rep, open(os.path.join(out, f'merge.{ver}.json'), 'w'), ensure_ascii=False, indent=1)
print('matched', rep['matched'], 'unmatched', len(rep['unmatched']), 'placeholders left', rep['placeholders_left'],
      'figures', rep['figures_in'])
