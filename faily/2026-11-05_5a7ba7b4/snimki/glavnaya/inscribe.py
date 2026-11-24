"""Tengwar inscription laid along a quadratic curve, as plain SVG paths (no font needed to view or print).
Shaping by HarfBuzz, so tehtar sit where the font's GPOS puts them.
usage: inscribe.py FONT.ttf TEXT SIZE P0x,P0y C_x,C_y P1x,P1y DY COLOR OUT.svg_fragment
  DY: baseline offset below the curve (in the curve's units); TEXT in the font's own encoding (Glaemscribe output)
"""
import sys, math
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

font_fn, text, size = sys.argv[1], sys.argv[2], float(sys.argv[3])
P0, C, P1 = [tuple(map(float, a.split(','))) for a in sys.argv[4:7]]
DY, color, out_fn = float(sys.argv[7]), sys.argv[8], sys.argv[9]

blob = hb.Blob.from_file_path(font_fn)
face = hb.Face(blob)
hbfont = hb.Font(face)
upem = face.upem
buf = hb.Buffer()
buf.add_str(text)
buf.guess_segment_properties()
hb.shape(hbfont, buf, {'kern': True, 'liga': True, 'mark': True, 'mkmk': True})
tt = TTFont(font_fn)
gs = tt.getGlyphSet()
order = tt.getGlyphOrder()
k = size / upem

# glyph placements on a straight baseline (font units -> curve units)
placed = []
x = 0.0
for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
    placed.append((order[info.codepoint], info.cluster, x + pos.x_offset, pos.y_offset, pos.x_advance))
    x += pos.x_advance
total = x * k

# the curve, sampled for arc length
def q(t):
    return ((1 - t) ** 2 * P0[0] + 2 * (1 - t) * t * C[0] + t * t * P1[0],
            (1 - t) ** 2 * P0[1] + 2 * (1 - t) * t * C[1] + t * t * P1[1])
N = 2000
pts = [q(i / N) for i in range(N + 1)]
cum = [0.0]
for a, b in zip(pts, pts[1:]):
    cum.append(cum[-1] + math.dist(a, b))
L = cum[-1]
def at(s):
    s = max(0.0, min(L, s))
    lo, hi = 0, N
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if cum[mid] <= s else (lo, mid)
    f = (s - cum[lo]) / max(cum[hi] - cum[lo], 1e-9)
    p = (pts[lo][0] + (pts[hi][0] - pts[lo][0]) * f, pts[lo][1] + (pts[hi][1] - pts[lo][1]) * f)
    ang = math.atan2(pts[hi][1] - pts[lo][1], pts[hi][0] - pts[lo][0])
    return p, ang

start = (L - total) / 2
# one frame per cluster: the base glyph's middle decides position and rotation of the whole cluster (tehtar follow)
clusters = {}
for name, cl, gx, gy, adv in placed:
    clusters.setdefault(cl, []).append((name, gx, gy, adv))
paths = []
for cl, items in clusters.items():
    base_x = items[0][1]
    span = max(sum(a for *_, a in items), 1)
    s_mid = start + (base_x + span / 2) * k
    (px, py), ang = at(s_mid)
    ca, sa = math.cos(ang), math.sin(ang)
    for name, gx, gy, adv in items:
        pen = SVGPathPen(gs)
        # local: font units, y up -> curve units, y down; origin at the cluster middle on the baseline
        lx0 = (start + gx * k) - s_mid
        # x' = px + ca*(lx) - sa*(ly) ; y' = py + sa*(lx) + ca*(ly), with lx = lx0 + fx*k, ly = DY - (gy + fy)*k
        a, b = ca * k, sa * k
        c, d = sa * k, -ca * k
        e = px + ca * lx0 - sa * (DY - gy * k)
        f = py + sa * lx0 + ca * (DY - gy * k)
        gs[name].draw(TransformPen(pen, (a, b, c, d, e, f)))
        dd = pen.getCommands()
        if dd:
            paths.append(dd)
open(out_fn, 'w').write('<g fill="%s">\n%s\n</g>\n' % (color, '\n'.join('<path d="%s"/>' % p for p in paths)))
print('glyphs %d, length %.1f of curve %.1f' % (len(placed), total, L))
