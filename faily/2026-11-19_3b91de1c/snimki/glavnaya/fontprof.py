"""rev. 0.11: measure any CSUR tengwar font for the TPM-2 shuttle (font sets beside Alcarin).

The machine is the same for every font: em = 1/3", u = em/16, the hammer window and the type blocks are those of
Alcarin, the codes are read from the shuttle (w - 4 in 0..12, b in 0..8, c in 0..9). For another font this module
  * scales its outlines so that its body height equals Alcarin's (the short tengwar's tops, 0.412 em), then, if a
    code or the ink leaves the machine's limits, tries smaller and slightly larger scales (0.80..1.10 of that) and keeps
    the one nearest to 1 that fits;
  * takes the tehta axes and the bottom axes from the font's GPOS mark-to-base anchors (any lookup whose marks
    include the vowel tehtar above, or the dots below);
  * pads carriers narrower than 4 u to w = 4 (the escapement's smallest step), keeping their axis;
  * reports what does not fit.
The result has the layout of data/codes.json (font units normalised to 1000 per em) plus 'scale', 'issues', 'pad'
and 'missing', and a glyph set with the same normalisation (ScaledGlyphSet), so the rest of the chain (gen of the
items, thickening, type blocks, combs, the page) works unchanged.
Usage: python3 -I fontprof.py FONT [FONT ...]      (prints a fit report)"""
import os, sys, json, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
import inventory as inv

ALCARIN_BODY = 0.412                 # em: median top of tinco..ungwe and numen..vilya in Alcarin
# limits of the machine (mm and u, from the Alcarin build: hammer window = Alcarin's ink extents + 0.1 mm)
EM_MM = 25.4 / 3
U_MM = EM_MM / 16
WIN_X = (-0.471, 8.704)              # mm from the hammer axis (parts.hammer_face)
WIN_Z = (-2.850, 6.232)              # mm from the baseline
W_RANGE, B_MAX, C_MAX = (4, 16), 8, 9
MARK_REF_U = 8
TOP_CP = (0xE040, 0xE044, 0xE046, 0xE04A, 0xE04C)
BOT_CP = (0xE045, 0xE043)
# mark key -> codepoint (gen_shuttle.MARK_CP); the variant names are Alcarin's, used when the font has them
MARK_CP = {'a': 0xE040, 'e': 0xE046, 'i': 0xE044, 'o': 0xE04A, 'u': 0xE04C, 'tilde': 0xE052, 'nas': 0xE050,
           'nasW': 0xE050, 'dotb': 0xE045, 'ddotb': 0xE043, 'dbl': 0xE051, 'dblW': 0xE051, 'dblL': 0xE051, 'lsd': 0xE07D}


class _G:
    def __init__(self, g, k):
        self.g, self.k = g, k
        self.width = g.width * k

    def draw(self, pen):
        self.g.draw(TransformPen(pen, (self.k, 0, 0, self.k, 0, 0)))


class ScaledGlyphSet:
    """Glyph set whose outlines are scaled by k (font units -> 1000 per em at the chosen scale)."""
    def __init__(self, gs, k):
        self.gs, self.k = gs, k

    def __getitem__(self, name):
        return _G(self.gs[name], self.k)

    def __contains__(self, name):
        return name in self.gs

    def keys(self):
        return self.gs.keys()


def _markbase(font):
    if 'GPOS' not in font or font['GPOS'].table.LookupList is None:
        return
    for lk in font['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            t = lk.LookupType
            if t == 9:
                t = st.ExtensionLookupType; st = st.ExtSubTable
            if t == 4:
                yield st


def anchors(font, top_marks, bot_marks, lambe_marks=()):
    """Base anchors for the classes of the top / bottom marks, and the mark anchors of every mark glyph."""
    top, bot, botL, mark = {}, {}, {}, {}
    for st in _markbase(font):
        cls_of = {}
        for mi, mr in enumerate(st.MarkArray.MarkRecord):
            g = st.MarkCoverage.glyphs[mi]
            cls_of[g] = mr.Class
            mark.setdefault(g, (mr.MarkAnchor.XCoordinate, mr.MarkAnchor.YCoordinate))
        tc = {cls_of[g] for g in top_marks if g in cls_of}
        bc = {cls_of[g] for g in bot_marks if g in cls_of}
        lc = {cls_of[g] for g in lambe_marks if g in cls_of}
        for bi, bg in enumerate(st.BaseCoverage.glyphs):
            rec = st.BaseArray.BaseRecord[bi]
            for ci, a in enumerate(rec.BaseAnchor):
                if a is None:
                    continue
                xy = (a.XCoordinate, a.YCoordinate)
                if ci in tc: top.setdefault(bg, xy)
                if ci in bc: bot.setdefault(bg, xy)
                if ci in lc: botL.setdefault(bg, xy)
    return top, bot, botL, mark


def _bounds(gs, name):
    p = BoundsPen(gs); gs[name].draw(p); return p.bounds


def raw(path):
    """Font-unit measurements, independent of the scale."""
    f = TTFont(path)
    cm = f.getBestCmap(); gs = f.getGlyphSet(); hm = f['hmtx']; upm = f['head'].unitsPerEm
    if not (0xE000 in cm and 0xE004 in cm):
        return dict(path=path, ok=False, why='не в кодировке CSUR (раскладка Дэна Смита): код литеры нельзя взять по Юникоду')
    tops = [cm[c] for c in TOP_CP if c in cm]
    bots = [cm[c] for c in BOT_CP if c in cm]
    lam = [g for g in ('uniE051.lambe',) if g in gs]
    top, bot, botL, mark = anchors(f, tops, bots, lam)
    if not top:
        return dict(path=path, ok=False, why='в шрифте нет якорей GPOS для техт: оси литер не заданы шрифтом')
    name = f['name'].getDebugName(4) or os.path.basename(path)
    def glyph(cp):
        g = cm.get(cp)
        if g is None or g not in gs:
            return None
        b = _bounds(gs, g)
        return g if b is not None else None
    T = []
    for cp, nm in inv.TENGWAR:
        g = glyph(cp)
        if g is None:
            T.append(dict(cp=cp, name=nm, missing=True)); continue
        T.append(dict(cp=cp, name=nm, glyph=g, adv=hm[g][0], bbox=_bounds(gs, g), top=top.get(g), bot=bot.get(g),
                      botL=botL.get(g)))
    M = []
    for key, gname, kind, role in inv.MARKS:
        g = gname if gname in gs and _bounds(gs, gname) is not None else glyph(MARK_CP[key])
        if g is None:
            M.append(dict(key=key, kind=kind, role=role, missing=True)); continue
        bb = _bounds(gs, g)
        M.append(dict(key=key, glyph=g, kind=kind, role=role, bbox=bb, anchor=mark.get(g, ((bb[0] + bb[2]) / 2, 0)),
                      length=bb[2] - bb[0], variant=g == gname and gname != cm.get(MARK_CP[key])))
    NP = []
    for cp, nm in inv.NUMERALS + inv.PUNCT:
        g = glyph(cp)
        if g is None:
            NP.append(dict(cp=cp, name=nm, missing=True)); continue
        NP.append(dict(cp=cp, name=nm, glyph=g, adv=hm[g][0], bbox=_bounds(gs, g), top=top.get(g)))
    short = [t['bbox'][3] for t in T if not t.get('missing') and (0xE000 <= t['cp'] <= 0xE007 or 0xE010 <= t['cp'] <= 0xE017)]
    body = statistics.median(short) / upm if short else None
    return dict(path=path, ok=True, name=name, upm=upm, gs=gs, T=T, M=M, NP=NP, body=body,
                anchored=sum(1 for t in T if t.get('top')))


def codes_at(R, s):
    """Codes and the fit report at scale s (1 = Alcarin's body height)."""
    k = R['body'] and (ALCARIN_BODY / R['body']) * s * 1000.0 / R['upm']
    U = 1000.0 / 16
    rd = lambda x: int(round(x))
    sc = lambda v: None if v is None else tuple(c * k for c in v)
    D = dict(U=U, UPM=1000, tengwar=[], marks=[], combos=[], numerals=[], punct=[], scale=s, k=k, pad=[], missing=[],
             issues=[])
    mm = EM_MM / 1000.0
    def ink(name, x0_mm, bb):
        """Check the ink of a glyph placed with its origin x0_mm from the hammer axis."""
        if bb is None:
            return
        xa, xb = x0_mm + bb[0] * mm, x0_mm + bb[2] * mm
        za, zb = bb[1] * mm, bb[3] * mm
        if xa < WIN_X[0] - 1e-6 or xb > WIN_X[1] + 1e-6:
            D['issues'].append((name, 'окно X', round(xa, 2), round(xb, 2)))
        if za < WIN_Z[0] - 1e-6 or zb > WIN_Z[1] + 1e-6:
            D['issues'].append((name, 'окно Z', round(za, 2), round(zb, 2)))
    def code(name, adv, top, bot=None, kind='T'):
        tx = top[0] if top else adv / 2
        a = rd(tx / U); b = rd((adv - tx) / U); w = a + b
        if w < W_RANGE[0]:
            D['pad'].append((name, w)); b += W_RANGE[0] - w; w = W_RANGE[0]
        d = rd((bot[0] - tx) / U) if (bot and top) else 0
        c = b - d
        if w > W_RANGE[1]: D['issues'].append((name, 'w', w))
        if kind in ('T', 'C'):
            if b > B_MAX or b < 0: D['issues'].append((name, 'b', b))
            if c > C_MAX or c < 0: D['issues'].append((name, 'c', c))
        return a, b, w, d, tx
    for t in R['T']:
        if t.get('missing'):
            D['missing'].append(t['name']); D['tengwar'].append(dict(cp=t['cp'], name=t['name'], missing=True)); continue
        adv = t['adv'] * k; top, bot = sc(t['top']), sc(t['bot']); bb = sc(t['bbox'])
        a, b, w, d, tx = code(t['name'], adv, top, bot)
        if not top:
            D['issues'].append((t['name'], 'нет якоря', 0))
        ink(t['name'], a * U * mm - tx * mm, bb)
        D['tengwar'].append(dict(cp=t['cp'], name=t['name'], glyph=t['glyph'], adv=adv, bbox=bb, top=top or (tx, 400),
                                 bot=bot or (tx, 0), botL=sc(t.get('botL')), w=w, a=a, b=b,
                                 err_top=(a * U - tx) / U, d_bot=((bot[0] - tx) / U) if bot else 0.0))
    for m in R['M']:
        if m.get('missing'):
            D['missing'].append(m['role']); D['marks'].append(dict(key=m['key'], kind=m['kind'], role=m['role'], missing=True))
            continue
        bb = sc(m['bbox']); an = sc(m['anchor'])
        ink(m['role'], MARK_REF_U * U * mm - an[0] * mm, bb)
        D['marks'].append(dict(key=m['key'], glyph=m['glyph'], kind=m['kind'], role=m['role'], bbox=bb, anchor=an,
                               length=bb[2] - bb[0], variant=m['variant']))
    car = next((t for t in D['tengwar'] if t['cp'] == 0xE02C and not t.get('missing')), None)
    for nm, cps in inv.COMBOS:
        mk = next((m for m in D['marks'] if not m.get('missing') and MARK_CP[m['key']] == cps[1] and not m['variant']), None)
        if car is None or mk is None:
            D['missing'].append(nm); D['combos'].append(dict(name=nm, cps=cps, missing=True)); continue
        tx = car['top'][0]; a = rd(tx / U); w = a + rd((car['adv'] - tx) / U)
        b = w - a
        if w < W_RANGE[0]:
            b += W_RANGE[0] - w; w = W_RANGE[0]
        ink(nm, a * U * mm - mk['anchor'][0] * mm, mk['bbox'])
        D['combos'].append(dict(name=nm, cps=cps, adv=car['adv'], w=w, a=a, b=b, mark=mk['glyph']))
    for t in R['NP']:
        grp = 'numerals' if 0xE070 <= t['cp'] < 0xE080 else 'punct'
        if t.get('missing'):
            D['missing'].append(t['name']); D[grp].append(dict(cp=t['cp'], name=t['name'], missing=True)); continue
        adv = t['adv'] * k; top = sc(t['top']); bb = sc(t['bbox'])
        a, b, w, d, tx = code(t['name'], adv, top, None, kind='N')
        ink(t['name'], a * U * mm - tx * mm, bb)
        D[grp].append(dict(cp=t['cp'], name=t['name'], glyph=t['glyph'], adv=adv, w=w, a=a, b=w - a,
                           has_anchor=top is not None, ax=tx))
    return D


def fit(path, s_try=None):
    """Best scale: the one nearest to 1 (Alcarin's body height) at which every code and every ink fits."""
    R = raw(path)
    if not R['ok']:
        return R, None
    grid = s_try or sorted({round(1.0 - 0.005 * i, 3) for i in range(0, 41)} | {round(1.0 + 0.005 * i, 3) for i in range(1, 21)},
                           key=lambda s: (abs(s - 1.0), -s))
    best = None
    for s in grid:
        D = codes_at(R, s)
        if not D['issues']:
            best = D; break
        if best is None or len(D['issues']) < len(best['issues']):
            best = D
    return R, best


def glyphset(R, D):
    return ScaledGlyphSet(R['gs'], D['k'])


if __name__ == '__main__':
    for p in sys.argv[1:]:
        R, D = fit(p)
        if D is None:
            print(os.path.basename(p), '—', R['why']); continue
        print(f"{os.path.basename(p):32s} {R['name'][:28]:28s} s={D['scale']:.3f} k={D['k']:.3f} issues={len(D['issues'])} "
              f"pad={len(D['pad'])} missing={D['missing']}")
        for i in D['issues'][:8]:
            print('     ', i)
