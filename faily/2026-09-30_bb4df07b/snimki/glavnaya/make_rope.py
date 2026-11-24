#!/usr/bin/env python3
"""v12 с каймой-верёвкой: две пряди перевиваются вдоль ромба, над/под чередуются.

Ось верёвки — ромб со скруглёнными углами; на каждой четверти целое число витков,
скрещение прядей стоит точно в вершине каждого угла, поэтому кайма переходит
в себя при повороте на 90°.
Аргументы: src.svg out.svg [N AMP WIDTH RC RAXIS]
"""
import re, sys, math
import numpy as np

src, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 20            # витков на четверть
AMP = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0       # размах пряди от оси
W = float(sys.argv[5]) if len(sys.argv) > 5 else 3.4         # толщина пряди
RC = float(sys.argv[6]) if len(sys.argv) > 6 else 12.0       # радиус скругления угла
RAXIS = float(sys.argv[7]) if len(sys.argv) > 7 else 257.0   # полуось ромба-оси

CX, CY = 340.0, 300.0
COL_A, COL_B = '#e6f2f8', '#6f9cc4'   # стеклянная и голубая пряди
EDGE, EDGE_W = '#1b2b64', 0.9
DS = 0.15                             # шаг выборки оси

V = [np.array(p) for p in [(CX, CY - RAXIS), (CX + RAXIS, CY), (CX, CY + RAXIS), (CX - RAXIS, CY)]]


def unit(v):
    return v / np.linalg.norm(v)


# --- ось: обход по часовой (на экране), старт в середине дуги верхнего угла ---
pts = []
for i in range(4):
    vp, v, vn = V[i - 1], V[i], V[(i + 1) % 4]
    din, dout = unit(v - vp), unit(vn - v)
    t1 = v - din * RC                     # угол 90°: касательные отрезки = RC
    inward = unit(dout - din)
    c = v + inward * RC * math.sqrt(2)    # центр дуги
    a1 = math.atan2(*(t1 - c)[::-1])
    t2 = v + dout * RC
    a2 = math.atan2(*(t2 - c)[::-1])
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    n_arc = max(8, int(abs(da) * RC / DS))
    for j in range(n_arc):
        a = a1 + da * j / n_arc
        pts.append(c + RC * np.array([math.cos(a), math.sin(a)]))
    t1n = vn - dout * RC
    n_lin = int(np.linalg.norm(t1n - t2) / DS)
    for j in range(n_lin):
        pts.append(t2 + (t1n - t2) * j / n_lin)
P = np.array(pts)
seg = np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1)
S = np.concatenate([[0], np.cumsum(seg)])
L = S[-1]
s_apex = (math.pi / 2) * RC / 2           # середина первой дуги
lam = L / (4 * N)


def axis(s):
    s = (s + s_apex) % L
    i = np.searchsorted(S, s, side='right') - 1
    i = np.clip(i, 0, len(P) - 1)
    f = (s - S[i]) / max(seg[i], 1e-9)
    p0, p1 = P[i], P[(i + 1) % len(P)]
    p = p0 + (p1 - p0) * f
    tng = unit(p1 - p0)
    return p, np.array([-tng[1], tng[0]])


def strand_pts(sign, s0, s1, step=0.5):
    out = []
    for s in np.arange(s0, s1 + 1e-9, step):
        p, n = axis(s)
        out.append(p + n * sign * AMP * math.sin(2 * math.pi * s / lam))
    return out


def d_of(ps, close=False):
    d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in ps)
    return d + ('Z' if close else '')


def stroke(d, col):
    return (f'<path d="{d}" fill="none" stroke="{EDGE}" stroke-width="{W + 2 * EDGE_W:.2f}" '
            f'stroke-linecap="butt" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{W:.2f}" '
            f'stroke-linecap="butt" stroke-linejoin="round"/>')


parts = [stroke(d_of(strand_pts(+1, 0, L - 0.5), True), COL_A),
         stroke(d_of(strand_pts(-1, 0, L - 0.5), True), COL_B)]
# прядь B лежит сверху всюду; на каждом втором скрещении поверх кладём отрезок пряди A
half = lam / 2
for m in range(0, 8 * N, 2):
    sc = m * half
    parts.append(stroke(d_of(strand_pts(+1, sc - 0.42 * half, sc + 0.42 * half, 0.3)), COL_A))
rope = '<g class="glass-rope">\n  ' + '\n  '.join(parts) + '\n</g>'

s = open(src, encoding='utf-8').read()
s = re.sub(r'<metadata>.*?</metadata>', '', s, flags=re.S)
s = s.replace(' xmlns:c2pa="http://c2pa.org/manifest"', '')
old = re.findall(r'<polygon points="340,40 600,300 340,560 80,300"[^>]*/>\n', s)
assert len(old) == 3, len(old)
s = s.replace(old[0], rope + '\n', 1)
for o in old[1:]:
    s = s.replace(o, '', 1)
s = re.sub(r'<title>(.*?)</title>',
           lambda m: '<title>' + m.group(1) + '; кайма — переплетённая стеклянная верёвка</title>',
           s, count=1, flags=re.S)
open(out, 'w', encoding='utf-8').write(s)
print(out, f'L={L:.1f} lambda={lam:.2f} crossings={8 * N}')
