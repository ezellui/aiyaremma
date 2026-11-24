#!/usr/bin/env python3
"""bee_fields.py FIELD_XML_DIR A_DIR OUT_DIR VERSION KIND
Transfer one of the edition's fields into the XML. The field was printed from Folio's "records with
hits" view with Show Hits on, so the field's text is bold and underlined there; FIELD_XML_DIR is that
print converted by bee_pdf2xml.py. For every record (NORM) or page (DIPLO) of the print, the same
unit is found in A_DIR (item + page + text), the bold+underlined stretches are mapped onto its text by
character offsets, and wrapped:
  KIND = la | fr | en   -> <foreign lang="…">
         coded           -> <hi rend="coded">
         xref            -> <ref type="cross">
         emend           -> <hi rend="emend">   (editorial emendation)
Report: OUT_DIR/fields.<VERSION>.<KIND>.json"""
import sys, os, re, json, difflib, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/scripts')
import bee_pdf2xml as B

fdir, adir, out, ver, kind = sys.argv[1:6]
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]
TAG = {'la': ('foreign', {'lang': 'la'}), 'fr': ('foreign', {'lang': 'fr'}), 'en': ('foreign', {'lang': 'en'}),
       'coded': ('hi', {'rend': 'coded'}), 'xref': ('ref', {'type': 'cross'}), 'emend': ('hi', {'rend': 'emend'})}[kind]


def slots(root):
    """text slots in document order: (element, 'text'|'tail', parent)"""
    out = []
    parent = {c: p for p in root.iter() for c in p}

    def walk(e):
        out.append((e, 'text'))
        for k in e:
            walk(k)
            out.append((k, 'tail'))
    walk(root)
    return out, parent


def flat(root):
    sl, parent = slots(root)
    text = []; owner = []
    for i, (e, a) in enumerate(sl):
        s = getattr(e, a) or ''
        text.append(s); owner.extend([i] * len(s))
    return ''.join(text), sl, parent, owner


def hit_spans(rec):
    """character spans of the bold+underlined text"""
    s, sl, parent, owner = flat(rec)
    inside = []
    for i, (e, a) in enumerate(sl):
        anc = e if a == 'text' else parent.get(e)
        b = u = False
        x = anc
        while x is not None:
            if x.tag == 'hi' and x.get('rend') == 'b': b = True
            if x.tag == 'hi' and x.get('rend') == 'u': u = True
            x = parent.get(x)
        inside.append(b and u)
    flags = [inside[o] for o in owner]
    spans = []; i = 0
    while i < len(s):
        if flags[i]:
            j = i
            while j < len(s) and (flags[j] or (s[j] in ' ' and j + 1 < len(s) and flags[j + 1])):
                j += 1
            a, b_ = i, j
            while a < b_ and s[a].isspace(): a += 1
            while b_ > a and s[b_ - 1].isspace(): b_ -= 1
            if b_ - a >= 1:
                spans.append((a, b_))
            i = j
        else:
            i += 1
    return s, spans


def wrap(rec, a, b):
    """wrap characters a..b of rec's text, slot by slot"""
    done = 0
    while True:
        s, sl, parent, owner = flat(rec)
        pos = 0; target = None
        for i, (e, att) in enumerate(sl):
            t = getattr(e, att) or ''
            st, en = pos, pos + len(t)
            pos = en
            if en <= a or st >= b or not t:
                continue
            # skip slots already inside a wrapper of this kind
            anc = e if att == 'text' else parent.get(e)
            x = anc; ok = True
            while x is not None:
                if x.tag == TAG[0] and all(x.get(k) == v for k, v in TAG[1].items()): ok = False; break
                x = parent.get(x)
            if not ok:
                continue
            target = (i, e, att, max(a, st) - st, min(b, en) - st, t)
            break
        if target is None:
            return done
        i, e, att, x0, x1, t = target
        new = ET.Element(TAG[0], dict(TAG[1])); new.text = t[x0:x1]; new.tail = t[x1:]
        if att == 'text':
            e.text = t[:x0]; e.insert(0, new)
        else:
            p = parent[e]; e.tail = t[:x0]; p.insert(list(p).index(e) + 1, new)
        done += 1


def units(root):
    """NORM: records; DIPLO: pages (pb .. pb) as (key, element list) — for DIPLO we work on the
    paragraphs that contain the page's text, so a unit is the run of elements after a <pb>"""
    if ver == 'norm':
        return [(rec.get('page'), rec) for rec in root.iter('rec')]
    return []


def sig(s):
    return re.sub(r'\s+', ' ', s).strip()


stats = {'units': 0, 'spans': 0, 'wrapped': 0, 'unit_not_found': 0, 'span_not_mapped': 0}
A = {}
for n in ITEMS:
    f = os.path.join(adir, f'{n}.{ver}.xml')
    if os.path.exists(f):
        A[n] = ET.parse(f).getroot()
used = set()
for f in sorted(glob.glob(os.path.join(fdir, f'*.{ver}.xml'))):
    froot = ET.parse(f).getroot(); n = froot.get('n')
    if n not in A:
        continue
    if ver == 'norm':
        for rec in froot.iter('rec'):
            s, spans = hit_spans(rec)
            if not spans:
                continue
            stats['units'] += 1; stats['spans'] += len(spans)
            cands = [r for r in A[n].iter('rec') if r.get('page') == rec.get('page')] or list(A[n].iter('rec'))
            best = max(cands, key=lambda r: difflib.SequenceMatcher(None, sig(flat(r)[0]), sig(s)).quick_ratio(), default=None)
            if best is None:
                stats['unit_not_found'] += 1; continue
            ta = flat(best)[0]
            sm = difflib.SequenceMatcher(None, s, ta, autojunk=False)
            blocks = sm.get_matching_blocks()

            def mapo(o):
                for bl in blocks:
                    if bl.a <= o < bl.a + bl.size:
                        return bl.b + (o - bl.a)
                return None
            for a, b in sorted(spans, reverse=True):
                ma, mb = mapo(a), mapo(b - 1)
                if ma is None or mb is None or mb < ma:
                    stats['span_not_mapped'] += 1; continue
                stats['wrapped'] += 1 if wrap(best, ma, mb + 1) else 0
    else:
        # DIPLO: the unit is the page; map within the whole item text by page-local search
        s_all, spans_all = hit_spans(froot)
        ta, *_ = flat(A[n])
        stats['units'] += 1; stats['spans'] += len(spans_all)
        # find each hit by its context (30 characters before and after) in the A text
        for a, b in sorted(spans_all, reverse=True):
            hit = s_all[a:b]; ctx = s_all[max(0, a - 30):a]
            ta = flat(A[n])[0]
            k = ta.find(ctx + hit) if ctx else -1
            if k >= 0:
                k += len(ctx)
            else:
                cands = [m.start() for m in re.finditer(re.escape(hit), ta)]
                if len(cands) != 1:
                    stats['span_not_mapped'] += 1; continue
                k = cands[0]
            stats['wrapped'] += 1 if wrap(A[n], k, k + len(hit)) else 0
os.makedirs(out, exist_ok=True)
for n, root in A.items():
    B.indent_blocks(root)
    ET.ElementTree(root).write(os.path.join(out, f'{n}.{ver}.xml'), encoding='utf-8', xml_declaration=True)
json.dump(stats, open(os.path.join(out, f'fields.{ver}.{kind}.json'), 'w'), indent=1)
print(kind, ver, json.dumps(stats))
