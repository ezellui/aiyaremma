"""Cyrillic for Accanthis italic styles.
Capitals and small-cap-type lowercase: slanted from the upright Cyrillic build;
cursive forms (и й п т ш щ ц д) from the italic Latin.
usage: build_ital.py ITALIC_SRC.otf UPRIGHT_CYR.otf OUT.otf
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphkit import *

SRC, UP, OUT = sys.argv[1:4]
k = Kit(SRC)
u = Kit(UP)
A = k.P; WD = k.W

H = A('H')
s1, s2 = scan(H, 100)[0], scan(H, 600)[0]
SL = (s2[0] - s1[0]) / 500.0
print('slant', SL)

def slant(p):
    return tr(p, skx=SL)

cyr = {}
def put(uni, p, w):
    cyr['uni%04X' % uni] = (p, int(round(w)), uni)

alias = {}
for a, b in zip('АВЕКМНОРСТХаеорсух', 'ABEKMHOPCTXaeopcyx'):
    alias[ord(a)] = k.cm[ord(b)]
alias[0x401] = 'Edieresis'; alias[0x451] = 'edieresis'

# 1. everything Cyrillic from the upright build, slanted
for name, g in u.cm.items():
    if 0x410 <= name <= 0x44F and name not in alias:
        gn = u.cm[name]
        if gn.startswith('uni'):
            put(name, slant(u.P(gn)), u.W(gn))

# 2. cursive replacements
br = A('breve')
def with_breve(p, w):
    bx = (br.bounds[0] + br.bounds[2]) / 2
    pc = (p.bounds[0] + p.bounds[2]) / 2 + SL * 450 * 0.0
    return union(p, tr(br, dx=pc - bx + 20))

uu = A('u')
put(0x438, uu, WD('u'))                             # и
put(0x439, with_breve(uu, WD('u')), WD('u'))        # й
put(0x43F, A('n'), WD('n'))                         # п
put(0x442, A('m'), WD('m'))                         # т
m = A('m'); mw = WD('m')
sha = tr(m, sx=-1, sy=-1, dx=m.bounds[0] + m.bounds[2], dy=m.bounds[1] + m.bounds[3])
put(0x448, sha, mw)                                 # ш

stem_w = (lambda iv: iv[1] - iv[0])(scan(A('dotlessi'), 200)[0])
hair = stem_w * 0.45
def tail(p):
    # right-most stem foot of the letter -> a short descender curling right
    iv = scan(p, 25)[-1]
    x0 = (iv[0] + iv[1]) / 2
    t = bstroke((x0 + 6, 40), (x0 - 4, -60), (x0 - 25, -150), (x0 - 50, -185), stem_w * 0.55, hair * 0.6)
    return union(p, t)
put(0x446, tail(uu), WD('u'))                       # ц
put(0x449, tail(sha), mw)                           # щ

pd = A('partialdiff')
s = 690 / (pd.bounds[3] - pd.bounds[1])
de = tr(pd, sx=s, sy=s, dy=-pd.bounds[1] * s - 10)
put(0x434, de, WD('partialdiff') * s)               # д

for name, (p, w, uni) in cyr.items():
    k.add(name, p, w, uni)
for uni, g in alias.items():
    for t in k.font['cmap'].tables:
        if t.isUnicode():
            t.cmap[uni] = g
k.save(OUT)
print('added', len(cyr))
