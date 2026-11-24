"""Обратная игла: отрезки между узлами канвы (целые координаты X, Y от 0 до H)."""
import math
import numpy as np
from skimage import measure
import xs_scene as S

HALF = S.HALF


def rot(x, y, k):
    for _ in range(k % 4):
        x, y = -y, x
    return x, y


def poly_segments(pts, closed=True):
    seg = []
    n = len(pts)
    for a in range(n if closed else n - 1):
        p, q = pts[a], pts[(a + 1) % n]
        if p != q:
            seg.append((p, q))
    return seg


def to_abs(seg):
    return [((p[0] + HALF, p[1] + HALF), (q[0] + HALF, q[1] + HALF)) for p, q in seg]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    ab = b - a
    nab = np.hypot(*ab)
    best, idx = -1, 0
    for i in range(1, len(pts) - 1):
        p = np.array(pts[i])
        dist = abs(ab[0] * (p - a)[1] - ab[1] * (p - a)[0]) / nab if nab > 1e-9 else np.hypot(*(p - a))
        if dist > best:
            best, idx = dist, i
    if best > eps:
        return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def snap_poly(pts, eps=0.45):
    s = rdp([tuple(p) for p in pts], eps)
    out = []
    for x, y in s:
        q = (int(round(x)), int(round(y)))
        if not out or out[-1] != q:
            out.append(q)
    return out


def backstitch():
    """Список (метка цвета, отрезок) в абсолютных узлах."""
    res = []

    def add(label, segs):
        for sg in segs:
            res.append((label, sg))

    # красная кромка ромба
    add('red', to_abs(poly_segments([(0, -HALF), (HALF, 0), (0, HALF), (-HALF, 0)])))

    # верёвка: внутренний край и разделители звеньев (тёмно-синие)
    din = S.ROPE_DIN
    add('navy', to_abs(poly_segments([(0, -(HALF - din)), (HALF - din, 0), (0, HALF - din), (-(HALF - din), 0)])))
    for k in range(4):
        for m in range(0, HALF // S.ROPE_W):
            x = m * S.ROPE_W
            p, q = rot(x, x - HALF, k), rot(x, x - HALF + din, k)
            add('navy', to_abs([(p, q)]))

    # огранка самоцветов
    def octa(a, c):
        return [(a, c - a), (c - a, a), (-(c - a), a), (-a, c - a),
                (-a, -(c - a)), (-(c - a), -a), (c - a, -a), (a, -(c - a))]
    out_v, in_v = octa(S.GEM_A, S.GEM_C), octa(S.GEM_IA, S.GEM_IC)
    for (gx, gy), name in S.GEMS:
        lab = 'facet_w' if name == 'white' else 'facet'
        sh = lambda pts: [(gx + x, gy + y) for x, y in pts]
        add(lab, to_abs(poly_segments(sh(out_v))))
        add(lab, to_abs(poly_segments(sh(in_v))))
        add(lab, to_abs([(p, q) for p, q in zip(sh(out_v), sh(in_v))]))

    # камень Троицы: контур восьмиугольника и свинцовые линии витража
    add('facet', to_abs(poly_segments(list(S.STONE_OCT))))
    n = 40
    g = np.linspace(-15, 15, 30 * n + 1)
    X, Y = np.meshgrid(g, g)
    z = (X - 1j * Y) / S.RHO0
    z[np.abs(z) < 1e-9] = 1e-9
    ph = np.degrees(np.angle((z ** 3 + 1j) / z)) % 360
    from matplotlib.path import Path
    octp = Path(np.array(S.STONE_OCT + [S.STONE_OCT[0]]), closed=True)
    leads = set()
    for c, h, name in S.PHASE:
        dd = np.abs((ph - c + 180) % 360 - 180) - h
        for cnt in measure.find_contours(dd, 0.0):
            pts = [(g[0] + p[1] * (g[1] - g[0]), g[0] + p[0] * (g[1] - g[0])) for p in cnt]
            # обрезка: внутри восьмиугольника (с запасом), вне ядра и вне триллиантов
            keep = []
            for x, y in pts:
                ok = octp.contains_point((x, y), radius=-0.6) and math.hypot(x, y) > S.R_CORE + 0.4
                for (hx, hy) in S.TRILL:
                    if abs(x - hx) < 1.4 and abs(y - hy) < 1.4:
                        ok = False
                keep.append(ok)
            run = []
            for p, ok in zip(pts, keep):
                if ok:
                    run.append(p)
                elif len(run) > 3:
                    sp = snap_poly(run); run = []
                    for a, b in zip(sp, sp[1:]):
                        leads.add(tuple(sorted([a, b])))
                else:
                    run = []
            if len(run) > 3:
                sp = snap_poly(run)
                for a, b in zip(sp, sp[1:]):
                    leads.add(tuple(sorted([a, b])))
    add('lead', to_abs(sorted(leads)))

    # кремовый ободок камня
    r = S.R_STONE
    circ = [(r * math.cos(t), r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 361)]
    cp = snap_poly(circ, 0.35)
    add('cream_bs', to_abs(poly_segments(cp[:-1] if cp[0] == cp[-1] else cp)))
    return res


BACK_COLOURS = {'red': '#c9453e', 'navy': '#1b2b64', 'facet': '#eef6f8', 'facet_w': '#9fc4dc',
                'lead': '#eef6f8', 'cream_bs': '#eee9dc'}
