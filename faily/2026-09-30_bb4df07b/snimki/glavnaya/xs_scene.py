"""Mírë Nolmeo (v12 с верёвкой) как сцена в координатах канвы.

Сетка H×H крестов; центр герба — узел канвы (H/2, H/2). Локальные координаты
x, y в крестах от центра, y вниз. Сцена задаёт метку цвета в любой точке;
клетка становится полным крестом или делится по диагонали (3/4 + 1/4).
"""
import math
import numpy as np
from matplotlib.path import Path

H = 168
HALF = H // 2                     # 84: полуось ромба в крестах
U = 540.0 / H                     # единиц SVG v12 на крест (ромб 540 по высоте)

# --- метки и цвета дизайна (hex из v12) ---
DESIGN = {
    'black':  '#141414', 'navy':   '#1b2b64', 'ringblue': '#6fa3d0', 'cream': '#eee9dc',
    'glass':  '#e6f2f8', 'ropeblue': '#6f9cc4', 'star': '#eef6f8', 'ray': '#dfeef6',
    'dot':    '#9fd3e0',
    'blue_d': '#2f5aa8', 'blue_l': '#6f95d6', 'purple_d': '#8e3a8a', 'purple_l': '#c07abb',
    'black_d': '#1b1b20', 'black_l': '#4a4a55', 'red_d': '#9e2a36', 'red_l': '#d25a66',
    'gold_d': '#d99a1e', 'gold_l': '#f2c45a', 'green_d': '#23865a', 'green_l': '#5cc08f',
    'white_d': '#dfe8ee', 'white_l': '#fbfaf5', 'teal_d': '#2e8a9e', 'teal_l': '#7cc4d4',
    'ph_lblue': '#b9cae2', 'ph_purple': '#a669a6', 'ph_pink': '#d8bdc2', 'ph_gold': '#deb154',
    'ph_mint': '#b5d7cc', 'ph_teal': '#5ea5b4',
    'core_lb': '#a9cde6', 'core_white': '#fbfaf5',
}
LABELS = ['none'] + list(DESIGN)
LID = {n: i for i, n in enumerate(LABELS)}

# --- геометрия ---
ROPE_P = 4.0          # период витка в диагональных шагах (на сторону 84 → 21 виток)
ROPE_C = 1.80         # ось верёвки: расстояние от кромки, кресты по нормали
ROPE_A = 0.62         # размах прядей
ROPE_HW = 0.52        # полутолщина пряди

R_CREAM_OUT, R_CREAM_IN, R_RING_IN = 180 / U, 172 / U, 168 / U
STAR_C = 69            # центр угловой звезды — узел (0,−69) и повороты
GEMS = [  # (центр-узел, тёмный, светлый) — порядок и цвета v12
    ((-15, -35), 'blue'), ((15, -35), 'purple'), ((35, -15), 'black'), ((35, 15), 'red'),
    ((15, 35), 'gold'), ((-15, 35), 'green'), ((-35, 15), 'white'), ((-35, -15), 'teal'),
]
GEM_A, GEM_C = 6, 8          # внешний восьмиугольник: |x|,|y|≤6, |x|+|y|≤8
GEM_IA, GEM_IC = 3, 4        # внутренний
DOTS = [(9, -44), (-9, -44), (44, -9), (44, 9), (9, 44), (-9, 44), (-44, 9), (-44, -9)]
R_STONE = 54 / U             # чёрный диск камня
STONE_OCT = [(0, -14), (10, -10), (14, 0), (10, 10), (0, 14), (-10, 10), (-14, 0), (-10, -10)]
RHO0 = 7.0                   # радиус нулей Троицы
R_CORE = 11.5 / U
CORE_LB = 9.6 / U
CORE_W = 4.8 / U
TRILL = {   # центр-узел: (TL, TR, BL, BR)
    (0, -7): ('purple_d', 'teal_d', 'gold_d', 'gold_d'),
    (6, 4): ('teal_d', 'gold_d', 'purple_d', 'purple_d'),
    (-6, 4): ('gold_d', 'purple_d', 'teal_d', 'teal_d'),
}
PHASE = [(0, 50, 'ph_lblue'), (60, 10, 'ph_purple'), (120, 50, 'ph_pink'),
         (180, 10, 'ph_gold'), (240, 50, 'ph_mint'), (300, 10, 'ph_teal')]


def rot_pts(pts, k):
    """Поворот точек на 90°·k по часовой (экран, y вниз)."""
    out = []
    for x, y in pts:
        for _ in range(k % 4):
            x, y = -y, x
        out.append((x, y))
    return out


def star_poly(cx, cy, k):
    s = 1.12 / U   # чуть крупнее v12, чтобы лучи не пропали на сетке
    base = [(0, -15), (3, -3), (15, 0), (3, 3), (0, 15), (-3, 3), (-15, 0), (-3, -3)]
    pts = [(cx + px * s, cy + py * s) for px, py in base]
    return rot_pts(pts, k)


def ray_poly(theta_deg):
    th = math.radians(theta_deg)
    ux, uy = math.sin(th), -math.cos(th)
    nx, ny = -uy, ux
    r0, r1, rm, w = 60 / U, 116 / U, 88 / U, 5 / U
    return [(ux * r0, uy * r0), (ux * rm + nx * w, uy * rm + ny * w),
            (ux * r1, uy * r1), (ux * rm - nx * w, uy * rm - ny * w)]


def in_poly(poly, x, y):
    p = Path(np.array(poly + [poly[0]]), closed=True)
    pts = np.column_stack([x.ravel(), y.ravel()])
    return p.contains_points(pts).reshape(x.shape)


def label_at(x, y):
    """Метки сцены в точках (x, y) — массивы одинаковой формы."""
    lab = np.zeros(x.shape, dtype=np.int16)
    inside = (np.abs(x) + np.abs(y)) < HALF
    lab[inside] = LID['black']

    # верёвка: каждую точку поворачиваем в правую верхнюю четверть
    qx, qy = x.copy(), y.copy()
    for _ in range(3):
        m = ~((qx >= 0) & (qy < 0))
        qx[m], qy[m] = qy[m], -qx[m]
    S = (qx + qy + HALF) / 2.0
    t = (HALF - (qx - qy)) / math.sqrt(2)
    sw = ROPE_A * np.sin(2 * math.pi * S / ROPE_P)
    inA = inside & (np.abs(t - (ROPE_C + sw)) < ROPE_HW)
    inB = inside & (np.abs(t - (ROPE_C - sw)) < ROPE_HW)
    kx = np.rint(S / (ROPE_P / 2)).astype(int)
    a_top = (kx % 2 == 0)
    lab[inB] = LID['ropeblue']
    lab[inA & (~inB | a_top)] = LID['glass']

    for k in range(4):
        cx, cy = rot_pts([(0, -STAR_C)], k)[0]
        lab[in_poly(star_poly(0, -STAR_C, 0) if False else
                    [(px, py) for px, py in rot_pts([(p[0], p[1]) for p in
                     [(0 + q[0], -STAR_C + q[1]) for q in
                      [(px * 1.12 / U, py * 1.12 / U) for px, py in
                       [(0, -15), (3, -3), (15, 0), (3, 3), (0, 15), (-3, 3), (-15, 0), (-3, -3)]]]], k)],
                    x, y)] = LID['star']

    rho = np.hypot(x, y)
    lab[(rho < R_CREAM_OUT)] = LID['cream']
    lab[(rho < R_CREAM_IN)] = LID['ringblue']
    lab[(rho < R_RING_IN)] = LID['navy']

    for th in range(0, 360, 45):
        lab[in_poly(ray_poly(th), x, y)] = LID['ray']

    for dx, dy in DOTS:
        lab[(np.abs(x - dx) < 1) & (np.abs(y - dy) < 1)] = LID['dot']

    for (gx, gy), name in GEMS:
        ax, ay = np.abs(x - gx), np.abs(y - gy)
        lab[(ax < GEM_A) & (ay < GEM_A) & (ax + ay < GEM_C)] = LID[name + '_d']
        lab[(ax < GEM_IA) & (ay < GEM_IA) & (ax + ay < GEM_IC)] = LID[name + '_l']

    lab[rho < R_STONE] = LID['black']
    oct_in = in_poly(STONE_OCT, x, y)
    z = (x - 1j * y) / RHO0
    z[np.abs(z) < 1e-9] = 1e-9
    ph = np.degrees(np.angle((z ** 3 + 1j) / z)) % 360
    for c, h, name in PHASE:
        d = np.abs((ph - c + 180) % 360 - 180)
        lab[oct_in & (d <= h)] = LID[name]

    lab[rho < R_CORE] = LID['black']
    ax, ay = np.abs(x), np.abs(y)
    oct_r = np.maximum(np.maximum(ax, ay) * math.cos(math.pi / 8) + 0,
                       (ax + ay) / math.sqrt(2) * math.cos(math.pi / 8))
    # восьмиугольник «вершиной вверх»: опорная функция по 8 направлениям через 22.5°
    ang = np.arctan2(ay, ax)
    rr = rho * np.cos(((ang + math.pi / 8) % (math.pi / 4)) - math.pi / 8 - math.pi / 8 * 0)
    lab[rr * 0 + rho * np.cos(((np.arctan2(y, x) - math.pi / 8) % (math.pi / 4)) - math.pi / 8)
        < CORE_LB * math.cos(math.pi / 8)] = LID['core_lb']
    lab[rho * np.cos(((np.arctan2(y, x) - math.pi / 8) % (math.pi / 4)) - math.pi / 8)
        < CORE_W * math.cos(math.pi / 8)] = LID['core_white']
    return lab


def classify(n=8):
    """Клетки: (kind, a, b) kind 0 — полный крест метки a; 1 — '/' (верх-лево a, низ-право b);
    2 — '\\' (верх-право a, низ-лево b)."""
    off = (np.arange(n) + 0.5) / n
    U_, V_ = np.meshgrid(off, off)          # U_ — по x, V_ — по y внутри клетки
    ii, jj = np.meshgrid(np.arange(H), np.arange(H))
    X = (ii[:, :, None, None] + U_[None, None]) - HALF
    Y = (jj[:, :, None, None] + V_[None, None]) - HALF
    lab = label_at(X, Y)                     # (H, H, n, n), индексы [j, i, v, u]
    L = len(LABELS)
    flat = lab.reshape(H, H, -1)
    m_ul = (U_ + V_ < 1).ravel(); m_lr = (U_ + V_ > 1).ravel()
    m_ur = (U_ > V_).ravel();     m_ll = (U_ < V_).ravel()

    def mode(mask):
        sub = flat[:, :, mask]
        cnt = np.zeros((H, H, L), dtype=np.int32)
        for li in range(L):
            cnt[..., li] = (sub == li).sum(-1)
        return cnt.argmax(-1), cnt.max(-1) / sub.shape[-1]

    fa, fp = mode(np.ones(n * n, bool))
    a1, p1 = mode(m_ul); b1, q1 = mode(m_lr)
    a2, p2 = mode(m_ur); b2, q2 = mode(m_ll)
    kind = np.zeros((H, H), np.int8); A = fa.copy(); B = fa.copy()
    s1 = np.where(a1 != b1, np.minimum(p1, q1), 0)
    s2 = np.where(a2 != b2, np.minimum(p2, q2), 0)
    use1 = (fp < 0.85) & (s1 >= 0.8) & (s1 >= s2)
    use2 = (fp < 0.85) & (s2 >= 0.8) & (s2 > s1)
    kind[use1] = 1; A[use1] = a1[use1]; B[use1] = b1[use1]
    kind[use2] = 2; A[use2] = a2[use2]; B[use2] = b2[use2]

    for (hx, hy), cols in TRILL.items():   # триллианты — мотив 2×2
        for (dx, dy), c in zip([(-1, -1), (0, -1), (-1, 0), (0, 0)], cols):
            j, i = HALF + hy + dy, HALF + hx + dx
            kind[j, i] = 0; A[j, i] = LID[c]; B[j, i] = LID[c]
    return kind, A, B
