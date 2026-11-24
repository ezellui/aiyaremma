"""What the typist sees of the sheet: rays from the eye to points of the paper around the print point.
A point is hidden if any part of the machine (at the rest pose between strokes) lies on the ray.
Usage: python3 -I visibility.py OUT_JSON GEN_DIR"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import params as P
import parts as PT
import geo

# eye positions of a seated typist (mm, machine coordinates; desk at z = 0, keyboard front edge y ~ -340)
EYES = {'обычная посадка': (0.0, -720.0, 460.0), 'выше и ближе': (0.0, -640.0, 520.0), 'ниже и дальше': (0.0, -780.0, 400.0)}
LS = 1.6 * P.EM                         # line spacing
XS = np.arange(-180.0, 24.0, 3.0)       # along the line, from the print point (x = 0) to the left: text already typed
LINES = list(range(0, 7))               # 0 = the line being typed, 1.. = lines above it
SKIP = {'paper'}


def line_band(k):
    """z range of the letter body (x-height plus ascender share) of line k."""
    zb = P.ZP - 0.18 * P.EM + k * LS
    return zb + 0.05 * P.EM, zb + 0.55 * P.EM


def ray_hits(orig, dirs, tmax, V, F):
    """Moller-Trumbore, vectorised over rays x triangles; returns bool per ray (hit with 1e-6 < t < tmax)."""
    hit = np.zeros(len(dirs), bool)
    v0, v1, v2 = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    e1, e2 = v1 - v0, v2 - v0
    for i0 in range(0, len(dirs), 256):
        d = dirs[i0:i0 + 256][:, None, :]
        p = np.cross(d, e2[None])
        det = (e1[None] * p).sum(-1)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        s = orig[None, None, :] - v0[None]
        u = (s * p).sum(-1) * inv
        q = np.cross(s, e1[None])
        v = (d * q).sum(-1) * inv
        t = (e2[None] * q).sum(-1) * inv
        m = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6) & (t < tmax[i0:i0 + 256, None])
        hit[i0:i0 + 256] = m.any(1)
    return hit


def scene(st, mods=None):
    out = []
    for p in PT.build(st):
        if p.name in SKIP or (mods and mods.get('drop') and mods['drop'](p)):
            continue
        V, F = geo.to_arrays(p.mesh)
        if len(F):
            out.append((p.name, V, F, V.min(0), V.max(0)))
    return out


def analyse(parts, eye):
    eye = np.asarray(eye, float)
    res = {}
    occl = {}
    for k in LINES:
        z0, z1 = line_band(k)
        zs = np.linspace(z0, z1, 3)
        pts = np.array([(x, -0.3, z) for x in XS for z in zs])
        d = pts - eye; L = np.linalg.norm(d, axis=1); d = d / L[:, None]
        hidden = np.zeros(len(pts), bool)
        for name, V, F, lo, hi in parts:
            # slab test against the part's box
            with np.errstate(divide='ignore', invalid='ignore'):
                t1 = (lo[None] - eye[None]) / d; t2 = (hi[None] - eye[None]) / d
            tn = np.nanmax(np.minimum(t1, t2), 1); tf = np.nanmin(np.maximum(t1, t2), 1)
            cand = (tn <= tf) & (tf > 0) & (tn < L) & ~hidden
            if not cand.any():
                continue
            idx = np.nonzero(cand)[0]
            h = ray_hits(eye, d[idx], L[idx] - 0.5, V, F)
            if h.any():
                hidden[idx[h]] = True
                occl[name] = occl.get(name, 0) + int(h.sum())
        hid = hidden.reshape(len(XS), len(zs)).mean(1)          # hidden share of each column of the line
        res[k] = hid
    return res, occl


def summary(res):
    """per line: share of the stretch 0..-150 mm hidden; nearest visible point left of the print point."""
    out = {}
    sel = (XS <= 0) & (XS >= -150)
    for k, hid in res.items():
        vis = hid[sel] < 0.34
        xs = XS[sel]
        first = None
        for x, v in sorted(zip(xs, vis), key=lambda a: -a[0]):
            if v:
                first = float(x); break
        out[k] = dict(hidden=float(hid[sel].mean()), first_visible=first)
    return out


VARIANTS = {}


def variant(name):
    def deco(fn):
        VARIANTS[name] = fn; return fn
    return deco


if __name__ == '__main__':
    outp = sys.argv[1]
    st = PT.State()
    parts = scene(st)
    rep = {}
    for en, eye in EYES.items():
        r, oc = analyse(parts, eye)
        rep[en] = dict(lines=summary(r), occluders=dict(sorted(oc.items(), key=lambda a: -a[1])[:8]),
                       grid={str(k): [round(float(v), 2) for v in r[k]] for k in r})
        print(en, {k: (round(v['hidden'], 2), v['first_visible']) for k, v in rep[en]['lines'].items()})
        print('   ', rep[en]['occluders'])
    json.dump(dict(xs=XS.tolist(), eyes=EYES, rest=rep), open(outp, 'w'), ensure_ascii=False, indent=1)
