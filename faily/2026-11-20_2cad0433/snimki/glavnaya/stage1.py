"""Stage 1 (spec §4.5-4.9): bodies, their path to the ground, mobility (rank of the linearised constraints), statics
under gravity in every attitude (linear programme with slacks), fastener loads and the list of missing fastening.

Bodies are the components of the graph of 'rigid' joints. Three readings of the registry:
  design   -- every rigid joint holds (as the document intends, missing fasteners included);
  declared -- rigid joints that are modeled or described hold; 'missing' ones are plain contacts (the main reading);
  model    -- only fastening that exists in the model's geometry holds.
Two-sided constraints: fastening (inside bodies) and linear guides (MGN12, MGN7, LM8UU) or schematic overlaps of moving
joints; everything else -- pins in bores, levers on axles, parts lying on parts -- is one-sided contact with friction,
from the geometry (contactgeo.py). Usage: python3 -I tools/physics/stage1.py [mode]"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
import meshes as MS
import contactgeo as CG

FLEX_NAMES = {'rotate tape', 'escapement tape', 'ribbon', 'paper', 'bksp link', 'back link', 'mainspring'}
LINEAR = ('MGN12H', 'MGN7H', 'LM8UU')


def is_flex(name):
    return name in FLEX_NAMES or 'spring' in name.split() or name.endswith(' spring')


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def f(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]; a = self.p[a]
        return a

    def u(self, a, b):
        a, b = self.f(a), self.f(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def holds(j, mode):
    if j['type'] != 'rigid':
        return False
    if mode == 'design':
        return True
    if mode == 'declared':
        return j['status'] in ('modeled', 'described')
    return j['status'] == 'modeled'


def bodies(S, J, mode):
    N = len(S.names)
    uf = UF(N)
    for g in J['ground'][1:]:
        uf.u(S.idx[J['ground'][0]], S.idx[g])
    for j in J['joints']:
        if holds(j, mode) and not is_flex(j['a']) and not is_flex(j['b']):
            uf.u(S.idx[j['a']], S.idx[j['b']])
    roots = {}
    body = np.full(N, -1)
    g0 = uf.f(S.idx[J['ground'][0]])
    order = [g0] + [i for i in range(N) if uf.f(i) == i and i != g0]
    for r in order:
        roots[r] = len(roots)
    for i in range(N):
        if not is_flex(S.names[i]):
            body[i] = roots[uf.f(i)]
    return body, len(roots)          # body 0 is the ground


def linear_joint(j, S):
    pa, pb = S.p(j['a']), S.p(j['b'])
    if j['type'] not in ('prismatic', 'revolute', 'cylindrical'):
        return False
    return any((p['bom'] or '').startswith(LINEAR) for p in (pa, pb)) or (j.get('overlap') or 0) > 0.0


def joint_rows(j, S):
    """Rows (w_omega, w_v) in SI of a two-sided joint, as wrenches of unit reactions on body b (minus on a)."""
    ax = j.get('axis') or {}
    d = np.array(ax.get('d', [1, 0, 0]), float); d /= np.linalg.norm(d)
    p = np.array(ax.get('p', S.V[S.idx[j['b']]].mean(0)), float) * U.MM
    e1 = np.cross(d, [1, 0, 0] if abs(d[0]) < 0.9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1)
    rows = []
    tr = {'prismatic': [e1, e2], 'revolute': [d, e1, e2], 'cylindrical': [e1, e2]}[j['type']]
    rot = {'prismatic': [d, e1, e2], 'revolute': [e1, e2], 'cylindrical': [e1, e2]}[j['type']]
    for e in tr:
        rows.append((np.cross(p, e), e))
    for e in rot:
        rows.append((e, np.zeros(3)))
    return rows


def build_contacts(S, J, body, pairs, Tposes=None, key=None, skip_flex=True):
    """Contact points between parts of different bodies: list of dict(i, j, ba, bb, X (m), N, side, mu)."""
    out = []
    jt = {(j['a'], j['b']): j for j in J['joints']}
    for pr in pairs:
        a, b = pr['a'], pr['b']
        if is_flex(a) or is_flex(b):
            continue
        i, k = S.idx[a], S.idx[b]
        if body[i] == body[k]:
            continue
        j = jt.get((a, b)) or jt.get((b, a))
        if j is not None and linear_joint(j, S):
            continue
        tol = max(0.06, pr['gap'] + 0.05)
        Ti = Tposes[i] if Tposes is not None else None
        Tk = Tposes[k] if Tposes is not None else None
        X, Nn, side = CG.patch(S, i, k, tol, Ti, Tk, key)
        if len(X) == 0:
            continue
        mu = U.mu_pair(S.parts[i]['mat'], S.parts[k]['mat'], 0)
        out.append(dict(a=a, b=b, i=i, k=k, X=X * U.MM, N=Nn, side=side, mu=mu, type=(j or {}).get('type')))
    return out


def body_props(S, M, body, nb):
    m = np.zeros(nb); c = np.zeros((nb, 3))
    flexload = {}
    for i, p in enumerate(S.parts):
        mi = M[i]['m']; ci = np.array(M[i]['c'])
        if body[i] < 0:
            flexload[i] = (mi, ci)
            continue
        m[body[i]] += mi; c[body[i]] += mi * ci
    c = c / np.maximum(m, 1e-12)[:, None]
    return m, c, flexload


def flex_hosts(S, body, pairs):
    """Bodies a flexible part (spring, tape, sheet, ribbon) touches: its weight goes onto them, shared equally."""
    h = {}
    for pr in pairs:
        for x, y in ((pr['a'], pr['b']), (pr['b'], pr['a'])):
            if is_flex(x) and not is_flex(y):
                h.setdefault(S.idx[x], set()).add(int(body[S.idx[y]]))
    return h


def generators(contacts, nb, mu_scale=1.0, zero_mu=False, joints=None):
    """Columns of the equilibrium matrix: one-sided generators (n + mu t) >= 0, two-sided rows free.
    Returns (A (6nb x ncol) sparse, lb, meta)."""
    rows, cols, vals, lb, meta = [], [], [], [], []
    col = 0

    def put(bi, w, sgn):
        if bi == 0:
            return
        for q in range(6):
            if w[q] != 0.0:
                rows.append(6 * bi + q); cols.append(col); vals.append(sgn * w[q])

    for ci, c in enumerate(contacts):
        for x, n, s in zip(c['X'], c['N'], c['side']):
            pushed, pusher = (c['i'], c['k']) if s == 0 else (c['k'], c['i'])
            bp, bq = c['bp'][s], c['bq'][s]
            mu = 0.0 if zero_mu else c['mu'] * mu_scale
            e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < 0.9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
            dirs = [n] if mu == 0 else [n + mu * e1, n - mu * e1, n + mu * e2, n - mu * e2]
            for d in dirs:
                w = np.r_[np.cross(x, d), d]
                put(bp, w, +1); put(bq, w, -1)
                lb.append(0.0); meta.append(('c', ci)); col += 1
    for ji, (ba, bb, rws) in enumerate(joints or []):
        for wo, wv in rws:
            w = np.r_[wo, wv]
            put(bb, w, +1); put(ba, w, -1)
            lb.append(-np.inf); meta.append(('j', ji)); col += 1
    A = sp.csc_matrix((vals, (rows, cols)), shape=(6 * nb, col))
    return A, np.array(lb), meta


def solve_statics(A, lb, wext, nb, Lm=0.05):
    """min sum |slack| (moment slack weighted as force at Lm) s.t. A x + s+ - s- = -wext, x >= lb."""
    nrow = 6 * nb
    keep = np.arange(6, nrow)                       # the ground's six rows are not equations
    A = A[keep, :]
    b = -wext[keep]
    n = A.shape[1]; m = len(keep)
    w = np.tile([1 / Lm] * 3 + [1.0] * 3, nb - 1)   # moment rows (N m) -> N at Lm
    I = sp.identity(m, format='csc')
    Aeq = sp.hstack([A, I, -I], format='csc')
    c = np.r_[np.zeros(n), w, w]
    bounds = [(l if np.isfinite(l) else None, None) for l in lb] + [(0, None)] * (2 * m)
    r = linprog(c, A_eq=Aeq, b_eq=b, bounds=bounds, method='highs', options=dict(presolve=True, time_limit=600))
    if r.status != 0:
        return None, None, r
    x = r.x[:n]
    s = (r.x[n:n + m] - r.x[n + m:]).reshape(nb - 1, 6)
    return x, np.vstack([np.zeros(6), s]), r


def gravity_wrench(m, c, nb, gdir, flex=None):
    w = np.zeros(6 * nb)
    g = np.asarray(gdir, float) * U.G
    for b in range(nb):
        F = m[b] * g
        w[6 * b:6 * b + 3] = np.cross(c[b], F); w[6 * b + 3:6 * b + 6] = F
    for (mi, ci, hosts) in (flex or []):
        hs = [h for h in hosts if h >= 0]
        for h in hs:
            F = mi * g / len(hs)
            w[6 * h:6 * h + 3] += np.cross(ci, F); w[6 * h + 3:6 * h + 6] += F
    return w


ATTITUDES = [('рабочее', (0, 0, -1))]
for a in (5, 15):
    s, cth = math.sin(math.radians(a)), math.cos(math.radians(a))
    ATTITUDES += [(f'наклон {a}° вперёд', (0, -s, -cth)), (f'наклон {a}° назад', (0, s, -cth)),
                  (f'наклон {a}° влево', (-s, 0, -cth)), (f'наклон {a}° вправо', (s, 0, -cth))]
s30, c30 = math.sin(math.radians(30)), math.cos(math.radians(30))
ATTITUDES += [('перенос 30° вперёд', (0, -s30, -c30)), ('перенос 30° назад', (0, s30, -c30)), ('перенос 30° влево', (-s30, 0, -c30)),
              ('перенос 30° вправо', (s30, 0, -c30)), ('на боку −x', (-1, 0, 0)), ('на боку +x', (1, 0, 0)),
              ('на передней стенке −y', (0, -1, 0)), ('на задней стенке +y', (0, 1, 0)), ('вверх дном', (0, 0, 1))]


def local_mobility(nb, contacts, joints, c):
    """Free twists of each body with every other body held (normal contact rows as equalities): its nullspace."""
    per = [[] for _ in range(nb)]
    for cc in contacts:
        for x, n, s in zip(cc['X'], cc['N'], cc['side']):
            w = np.r_[np.cross(x, n), n]
            per[cc['bp'][s]].append(w); per[cc['bq'][s]].append(w)
    for ba, bb, rws in joints:
        for wo, wv in rws:
            w = np.r_[wo, wv]
            per[ba].append(w); per[bb].append(w)
    out = []
    for b in range(nb):
        if b == 0:
            out.append([]); continue
        R = np.array(per[b]) if per[b] else np.zeros((0, 6))
        # twist about the body's centre: v(x) = v_c + w x (x - c); row . (w, v0) with v0 = v_c - w x c
        T = np.zeros((6, 6)); T[:3, :3] = np.eye(3); T[3:, :3] = -skew(c[b]).T * -1; T[3:, 3:] = np.eye(3)
        # (w, v0) = M (w, v_c): v0 = v_c - w x c = v_c + c x w
        Mx = np.eye(6); Mx[3:, :3] = skew(c[b])
        Rc = R @ Mx if len(R) else R
        if len(Rc):
            sc = np.r_[np.full(3, 0.05), np.ones(3)]          # rotation scaled to 5 cm
            Us, sv, Vt = np.linalg.svd(Rc * sc, full_matrices=True)
            tol = max(1e-9, 1e-6 * (sv[0] if len(sv) else 1))
            rank = int((sv > tol).sum())
            ns = Vt[rank:] * sc
        else:
            ns = np.eye(6)
        out.append([v / np.linalg.norm(v) for v in ns])
    return out


def skew(a):
    return np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])


def describe_twist(v, c):
    """v = (w, v_c) about the body centre c (m) -> text and numbers."""
    w, u = v[:3], v[3:]
    if np.linalg.norm(w) < 1e-6 * max(1.0, np.linalg.norm(u) / 0.05):
        d = u / np.linalg.norm(u)
        return dict(kind='сдвиг', d=d.round(3).tolist())
    wn = np.linalg.norm(w); d = w / wn
    p = c + np.cross(w, u) / wn ** 2
    h = float(w @ u / wn ** 2)
    return dict(kind='поворот', d=d.round(3).tolist(), p_mm=(p / U.MM).round(1).tolist(), pitch_mm=round(h / U.MM, 2))
