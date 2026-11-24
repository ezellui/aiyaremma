"""Adds Cyrillic to Accanthis ADF Std (upright styles) by composing existing outlines.
usage: build_cyr.py SRC.otf OUT.otf
"""
import sys
sys.path.insert(0, sys.path[0])
from glyphkit import *

SRC, OUT = sys.argv[1], sys.argv[2]
k = Kit(SRC)
A = lambda c: k.P(c)
WD = lambda c: k.W(c)

# ---------- measurements ----------
H = A('H')
(L0, L1), (R0, R1) = scan(H, 150)
sw = L1 - L0
ext = L0 - H.bounds[0]
lsb = H.bounds[0]
cross = [iv for iv in vscan(H, (L1 + R0) // 2) if 200 < iv[0] < 500][0]
hair = cross[1] - cross[0]
T = A('T')
toph = [iv for iv in vscan(T, int(T.bounds[0]) + 60) if iv[0] > 500][0]
topt = toph[1] - toph[0]           # thickness of top horizontal (T, E arm)
SH = 70 if sw < 100 else 80        # serif+bracket zone height
CAP = 700
mid = (L1 + R0) / 2
print('sw', sw, 'ext', ext, 'hair', hair, 'topt', topt, 'lsb', lsb)

# full stem with all 4 serif quadrants, left stem edge at L0
S = cut(clip(H, -200, -200, mid, 1000), L1, SH, 1000, CAP - SH)

def stem(x0, keep='lt rt lb rb', y0=None, y1=None):
    p = S
    q = {'lb': (-200, -50, L0, SH), 'rb': (L1, -50, 1000, SH),
         'lt': (-200, CAP - SH, L0, 1000), 'rt': (L1, CAP - SH, 1000, 1000)}
    for name, r in q.items():
        if name not in keep.split():
            p = cut(p, *r)
    if y0 is not None:
        p = union(clip(p, -500, y0, 2000, 2000))
    if y1 is not None:
        p = clip(p, -500, -500, 2000, y1)
    return tr(p, dx=x0 - L0)

def hbar(x0, x1, ytop, t):
    return rect(x0, ytop - t, x1, ytop)

def foot(xc):
    """symmetric bottom slab serif centred at xc (taken from H's stem)"""
    lb = clip(S, -200, -50, L0 + 1, SH)
    rb = clip(S, L1 - 1, -50, 1000, SH)
    return union(tr(lb, dx=xc - sw / 2 - L0), tr(rb, dx=xc + sw / 2 - L1))

E = A('E'); Ew = WD('E'); Exmax = E.bounds[2]
Etop = clip(E, -200, 540, 2000, 2000)            # stem top + top arm + serif
Ebot_stem = clip(E, -200, -200, L1, 540)
B = A('B'); Bw = WD('B')
bj = scan(B, 150)  # unused, B stem is ~ H stem
# lower bowl of B: below top of waist band
band = [iv for iv in vscan(B, int((L1 + B.bounds[2]) / 2) - 30) if 250 < iv[0] < 500][0]
Blow = clip(B, L1 - 2, -100, 2000, band[1] + 1)
Bstem_low = clip(B, -200, -200, L1 + 1, band[1] + 1)

def sc_ready(fn):
    return fn

cyr = {}   # name -> (path, width, uni)
def put(uni, path, width):
    cyr['uni%04X' % uni] = (path, width, uni)

alias = {}  # uni -> existing glyph
for a, b in zip('АВЕКМНОРСТХаеорсух', 'ABEKMHOPCTXaeopcyx'):
    alias[ord(a)] = k.cm[ord(b)]
alias[0x401] = 'Edieresis'; alias[0x451] = 'edieresis'

# ---------- capitals (builders take tail depth for descenders) ----------
def G_Ge(tail=-160):
    rb = clip(stem(L0), L1 - 1, -50, L1 + ext + 1, SH)
    return union(Etop, Ebot_stem, rb), Ew - 20

def G_Be(tail=-160):
    return union(Etop, stem(L0, 'lt lb', 300, 600), Bstem_low, Blow), Bw

legw = sw * 0.82
def G_De(tail=-170):
    w = 660
    Rx0 = w - lsb - ext - sw - 10
    rs = stem(Rx0, 'lt rt', y0=hair)
    lx_top, lx_bot = 245, 130
    leg = clip(stroke(lx_top, CAP, lx_bot, 0, legw), -100, 0, 2000, CAP)
    top = hbar(lx_top - legw / 2 - ext * 0.55, Rx0 + sw, CAP, topt)
    base = rect(lsb, 0, w - lsb, hair * 1.05)
    t = hair * 1.35
    dl = poly([(lsb, hair), (lsb + t, hair), (lsb + t * 0.85, tail), (lsb - 6, tail)])
    dr = poly([(w - lsb - t, hair), (w - lsb, hair), (w - lsb + 6, tail), (w - lsb - t * 0.85, tail)])
    return union(rs, leg, top, base, dl, dr), w

def G_Zhe(tail=0):
    K = A('K')
    arms = clip(K, L1, -100, 2000, 2000)
    arms = cut(arms, L1 - 1, -50, L1 + ext + 2, SH)
    arms = cut(arms, L1 - 1, CAP - SH, L1 + ext + 2, 1000)
    a = K.bounds[2] - L1
    left = tr(mirror(arms, 0), dx=lsb + a + L1)       # mirrored arms ending at lsb+a
    cx0 = lsb + a
    right = tr(arms, dx=cx0 + sw - L1)
    return union(left, stem(cx0), right), int(2 * a + sw + 2 * lsb)

def G_Ze(tail=0):
    t3 = A('three'); s = CAP / (t3.bounds[3] - t3.bounds[1])
    p = tr(t3, dy=-t3.bounds[1] * s, sy=s, sx=1.04)
    return p, WD('three') * 1.04

def G_I(tail=0, w=None):
    w = w or WD('H')
    rs = stem(R0)
    hw = hair * 1.55
    d = clip(stroke(L1 + hw / 2 - 18, 0, R0 - hw / 2 + 18, CAP, hw), L0, 0, R1, CAP)
    return union(stem(L0), rs, d), w

br = A('breve')
def G_Ishort(tail=0):
    p, w = G_I()
    bx = (br.bounds[0] + br.bounds[2]) / 2
    return union(p, tr(br, dx=w / 2 - bx, dy=240)), w

def G_El(tail=0):
    w = 630
    Rx0 = w - lsb - ext - sw
    rs = stem(Rx0)
    lx_top, lx_bot = 215, 95
    leg = clip(stroke(lx_top, CAP, lx_bot, 0, legw), -100, 0, 2000, CAP)
    top = hbar(lx_top - legw / 2 - ext * 0.5, Rx0 + sw, CAP, topt)
    return union(rs, leg, top, foot(lx_bot)), w

def G_Pe(tail=0):
    w = WD('H')
    top = hbar(L0 - ext * 0.75, R1 + ext * 0.75, CAP, topt)
    return union(stem(L0, 'lb rb'), stem(R0, 'lb rb'), top), w

def G_U(tail=0):
    y = A('y'); s = CAP / (y.bounds[3] - y.bounds[1])
    return tr(y, dy=-y.bounds[1] * s, sy=s, sx=1.1), WD('y') * 1.1

o = A('o'); ow = WD('o')
def ef_bowl(scale, ycenter, gap):
    p = tr(o, sx=scale, sy=scale)
    cx = (p.bounds[0] + p.bounds[2]) / 2; cy = (p.bounds[1] + p.bounds[3]) / 2
    p = tr(p, dx=-cx, dy=ycenter - cy)
    l = tr(clip(p, -2000, -2000, 0, 2000), dx=-gap / 2)
    r = tr(clip(p, 0, -2000, 2000, 2000), dx=gap / 2)
    return union(l, r)

def G_Ef(tail=0):
    bowl = ef_bowl(1.14, 350, sw)
    half = (bowl.bounds[2] - bowl.bounds[0]) / 2
    cx = half + lsb + 5
    st = stem(cx - sw / 2)
    w = 2 * cx
    return union(tr(bowl, dx=cx), st), w

def G_Tse(tail=-170):
    w = WD('H') + 20
    t = hair * 1.35
    base = rect(L0 - ext, 0, R1 + ext * 0.6, hair * 1.05)
    tl = poly([(R1 + ext * 0.6 - t, hair), (R1 + ext * 0.6, hair), (R1 + ext * 0.6 + 6, tail), (R1 + ext * 0.6 - t * 0.85, tail)])
    return union(stem(L0, 'lt rt lb'), stem(R0, 'lt rt'), base, tl), w

def G_Che(tail=0):
    U = A('U')
    (u0, u1), (u2, u3) = scan(U, 400)
    um = (u1 + u2) / 2
    bowl = clip(U, -200, -100, u2 + 2, 260)
    lift = 290
    bowl = tr(bowl, dx=L0 - u0, dy=lift)
    upper = tr(clip(U, -200, 260 + lift - 2, um, 2000), dx=L0 - u0)
    rx = L0 + (u2 - u0)
    return union(bowl, upper, stem(rx)), rx + sw + ext + lsb

def G_Sha(tail=0, extra=False):
    gap = 205
    xs = [L0, L0 + sw + gap, L0 + 2 * (sw + gap)]
    right = xs[2] + sw
    parts = [stem(x, 'lt rt') for x in xs]
    parts.append(rect(L0 - ext, 0, right + ext, hair * 1.05))
    w = right + ext + lsb
    if extra:
        t = hair * 1.35; xe = right + ext
        parts.append(poly([(xe - t, hair), (xe, hair), (xe + 6, tail), (xe - t * 0.85, tail)]))
        w += 15
    return union(*parts), w

def G_Shcha(tail=-170):
    return G_Sha(tail, extra=True)

def G_Soft(tail=0):
    return union(stem(L0, 'lt rt lb'), Bstem_low, Blow), Bw - 10

def G_Hard(tail=0):
    soft, sw_ = G_Soft()
    soft = cut(soft, -200, CAP - SH, L0, 2000)      # drop top-left serif
    armlen = 150
    tip = clip(E, Exmax - 130, 540, 2000, 2000)
    tip = tr(mirror(tip, 0), dx=Exmax + lsb)          # tip now starts at lsb
    shift = lsb + armlen - L0 + 30
    bar = hbar(lsb + 20, L0 + shift + 5, CAP, topt)
    return union(tip, bar, tr(soft, dx=shift)), sw_ + shift

def G_Yeru(tail=0):
    soft, w1 = G_Soft()
    I = A('I'); Iw = WD('I')
    return union(soft, tr(I, dx=w1 - 25)), w1 - 25 + Iw

def G_E(tail=0):
    C = A('C'); w = WD('C')
    m = mirror(C, w)
    inner = [iv for iv in scan(m, 350)][-1][0]
    return union(m, hbar(w * 0.36, inner + 5, 370, hair)), w

def G_Yu(tail=0):
    O = A('O'); s = 0.86
    Os = tr(O, sx=s)
    ox = L1 + 75 - Os.bounds[0]
    Os = tr(Os, dx=ox)
    olft = scan(Os, 350)[0][0]
    return union(stem(L0), hbar(L1 - 2, olft + 5, 370, hair), Os), Os.bounds[2] + lsb + 5

def G_Ya(tail=0):
    R = A('R'); w = WD('R')
    return mirror(R, w), w

caps = {0x411: G_Be, 0x413: G_Ge, 0x414: G_De, 0x416: G_Zhe, 0x417: G_Ze, 0x418: G_I,
        0x419: G_Ishort, 0x41B: G_El, 0x41F: G_Pe, 0x423: G_U, 0x424: G_Ef, 0x426: G_Tse,
        0x427: G_Che, 0x428: G_Sha, 0x429: G_Shcha, 0x42A: G_Hard, 0x42B: G_Yeru,
        0x42C: G_Soft, 0x42D: G_E, 0x42E: G_Yu, 0x42F: G_Ya}

for u, fn in caps.items():
    p, w = fn()
    put(u, p, w)

# ---------- lowercase: small-cap derived ----------
lc_stem = (lambda iv: iv[1] - iv[0])(scan(A('dotlessi'), 200)[0])
sx = 0.84
dx = max(0, lc_stem - sw * sx)
lc_hair = hair * 0.93
# solve hair*sy + d = lc_hair with sy = (450-d)/700
d = (lc_hair - hair * 450 / CAP) / (1 - hair / CAP)
sy = (450 - d) / CAP
print('smallcap sx', sx, 'sy', round(sy, 3), 'dx', round(dx, 1), 'dy', round(d, 1))

def smallcap(p, w):
    q = tr(p, sx=sx, sy=sy)
    q = union(q, tr(q, dx=dx))
    q = union(q, tr(q, dy=d))
    return q, w * sx + dx

LC_TAIL = -165 / sy
sc_from = {0x431: None, 0x432: 'B', 0x433: G_Ge, 0x434: G_De, 0x436: G_Zhe, 0x437: G_Ze,
           0x438: G_I, 0x43A: 'K', 0x43B: G_El, 0x43C: 'M', 0x43D: 'H', 0x43F: G_Pe,
           0x442: 'T', 0x444: None, 0x446: G_Tse, 0x447: G_Che, 0x448: G_Sha, 0x449: G_Shcha,
           0x44A: G_Hard, 0x44B: G_Yeru, 0x44C: G_Soft, 0x44D: G_E, 0x44E: G_Yu, 0x44F: G_Ya,
           0x439: 'short'}
for u, src in sc_from.items():
    if src is None:
        continue
    if src == 'short':
        p, w = cyr['uni0438'][0], cyr['uni0438'][1]
        bx = (br.bounds[0] + br.bounds[2]) / 2
        put(u, union(p, tr(br, dx=w / 2 - bx, dy=0)), w)
        continue
    if isinstance(src, str):
        p, w = A(src), WD(src)
    else:
        tail = LC_TAIL if src in (G_De, G_Tse, G_Shcha) else 0
        p, w = src(tail)
    q, w2 = smallcap(p, w)
    # descenders scaled with the letter: recheck they reach ~-165
    put(u, q, w2)

# б from the figure six, stretched above the bowl to ascender height
six = A('six')
lo = clip(six, -200, -200, 2000, 300)
s = (760 - 300) / (six.bounds[3] - 300)
hi = tr(clip(six, -200, 299, 2000, 2000), dy=300 - 300 * s, sy=s)
put(0x431, union(lo, hi), WD('six') + 10)

# ф: ascending/descending stem with o halves
l = A('l'); (l0, l1) = scan(l, 300)[0]
p_ = A('p'); (p0, p1) = scan(p_, -100)[0]
pbot = clip(p_, -200, -400, p1 + 80, -150)
bowl = ef_bowl(1.0, 220, l1 - l0)
half = (bowl.bounds[2] - bowl.bounds[0]) / 2
cx = half + 30
stemf = union(tr(clip(l, -200, 0, 2000, 2000), dx=cx - (l0 + l1) / 2),
              rect(cx - (l1 - l0) / 2, -170, cx + (l1 - l0) / 2, 10),
              tr(pbot, dx=cx - (p0 + p1) / 2))
put(0x444, union(tr(bowl, dx=cx), stemf), 2 * cx)

# ---------- write ----------
for name, (p, w, u) in cyr.items():
    k.add(name, p, w, u)
for u, g in alias.items():
    for t in k.font['cmap'].tables:
        if t.isUnicode():
            t.cmap[u] = g
k.save(OUT)
print('glyphs added', len(cyr), 'aliases', len(alias))
