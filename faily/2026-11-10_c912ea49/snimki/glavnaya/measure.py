"""Measure Alcarin Tengwar and derive escapement codes for the typewriter design.

Unit u = em/16 (62.5 font units at UPM 1000).
For every advancing slug: width w (u), axis a (u, from left cell edge to the tehta axis),
b = w - a (from the axis to the right cell edge).
Usage: python3 -I measure.py FONT OUTDIR
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import inventory as inv

font_path, out = sys.argv[1], sys.argv[2]
f = TTFont(font_path)
cmap = f.getBestCmap(); hm = f['hmtx']; gs = f.getGlyphSet()
UPM = f['head'].unitsPerEm
U = UPM / 16.0
gpos = f['GPOS'].table


def bounds(g):
    p = BoundsPen(gs); gs[g].draw(p); return p.bounds


# collect base anchors from lookups 6 (main top/bottom), 7 (lambe-specific bottom)
base_anchor = {}   # glyph -> {'top':(x,y), 'bot':(x,y), 'botL':(x,y)}
mark_anchor = {}   # mark glyph -> (x,y)
for li in (6, 7):
    lk = gpos.LookupList.Lookup[li]
    for st in lk.SubTable:
        for mi, mr in enumerate(st.MarkArray.MarkRecord):
            mark_anchor.setdefault(st.MarkCoverage.glyphs[mi], (mr.MarkAnchor.XCoordinate, mr.MarkAnchor.YCoordinate))
        for bi, bg in enumerate(st.BaseCoverage.glyphs):
            rec = st.BaseArray.BaseRecord[bi]
            for ci, a in enumerate(rec.BaseAnchor):
                if a is None:
                    continue
                key = {(6, 0): 'bot', (6, 1): 'top', (7, 0): 'botL'}[(li, ci)]
                base_anchor.setdefault(bg, {})[key] = (a.XCoordinate, a.YCoordinate)


def r(x):
    return int(round(x))


data = {'U': U, 'UPM': UPM, 'tengwar': [], 'marks': [], 'combos': [], 'numerals': [], 'punct': []}

for cp, name in inv.TENGWAR:
    g = cmap[cp]; adv = hm[g][0]; anc = base_anchor.get(g, {})
    top = anc.get('top', (adv / 2, 400)); bot = anc.get('bot', (adv / 2, 0))
    w = r(adv / U); a = r(top[0] / U); b = w - a
    data['tengwar'].append(dict(cp=cp, name=name, glyph=g, adv=adv, bbox=bounds(g),
                                top=top, bot=bot, botL=anc.get('botL'),
                                w=w, a=a, b=b,
                                err_top=(a * U - top[0]) / U,          # residual of axis vs true top anchor, in u
                                d_bot=(bot[0] - top[0]) / U))          # bottom axis offset from top axis, in u

for key, g, kind, role in inv.MARKS:
    bb = bounds(g); ma = mark_anchor.get(g, ((bb[0] + bb[2]) / 2, 0))
    data['marks'].append(dict(key=key, glyph=g, kind=kind, role=role, bbox=bb, anchor=ma,
                              length=bb[2] - bb[0]))

carrier = cmap[0xE02C]
for name, cps in inv.COMBOS:
    adv = hm[carrier][0]; top = base_anchor[carrier]['top']
    w = r(adv / U); a = r(top[0] / U)
    data['combos'].append(dict(name=name, cps=cps, adv=adv, w=w, a=a, b=w - a))

for cp, name in inv.NUMERALS + inv.PUNCT:
    g = cmap[cp]; adv = hm[g][0]; anc = base_anchor.get(g, {})
    top = anc.get('top', (adv / 2, 400))
    w = max(1, r(adv / U)); a = r(top[0] / U)
    data['numerals' if cp < 0xE080 and cp >= 0xE070 else 'punct'].append(
        dict(cp=cp, name=name, glyph=g, adv=adv, w=w, a=a, b=w - a, has_anchor='top' in anc))

os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'codes.json'), 'w') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)

# console summary
for t in data['tengwar']:
    print(f"{t['cp']:X} {t['name']:28s} adv={t['adv']:4d} w={t['w']:2d} a={t['a']:2d} b={t['b']:2d} "
          f"err={t['err_top']:+.2f} dbot={t['d_bot']:+.2f} topY={t['top'][1]}")
for m in data['marks']:
    print(m['key'], m['glyph'], 'len', m['length'], 'anchor', m['anchor'])
for k in ('combos', 'numerals', 'punct'):
    for t in data[k]:
        print(k, t.get('name'), t['w'], t['a'], t['b'], t.get('has_anchor'))
