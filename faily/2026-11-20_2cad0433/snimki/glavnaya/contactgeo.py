"""Contact patches between two parts (spec §4.7: points within a tolerance of the other mesh, normals of the nearest
faces, thinned to the extreme points of each normal cluster). Works on the rest meshes moved by 4x4 poses (mm)."""
import numpy as np
import trimesh
from scipy.spatial import ConvexHull

_TM = {}


def tm_at(S, i, T=None, key=None):
    k = (i, key)
    if k not in _TM:
        V = S.V[i] if T is None else S.V[i] @ T[:3, :3].T + T[:3, 3]
        _TM[k] = trimesh.Trimesh(V, S.F[i], process=False)
    return _TM[k]


def clear_cache():
    _TM.clear()


def _one_way(Va, mb, tol, lo, hi):
    sel = np.all(Va >= lo - tol, 1) & np.all(Va <= hi + tol, 1)
    X = Va[sel]
    if len(X) == 0:
        return np.zeros((0, 3)), np.zeros((0, 3))
    cp, d, tri = trimesh.proximity.closest_point(mb, X)
    ok = d <= tol
    if not ok.any():
        return np.zeros((0, 3)), np.zeros((0, 3))
    n = mb.face_normals[tri[ok]]
    return X[ok], n


def thin(X, N, per=6, cos_tol=0.94):
    """Cluster the normals; keep up to `per` extreme points of each cluster's patch (2D hull in the tangent plane)."""
    out_x, out_n = [], []
    used = np.zeros(len(X), bool)
    order = np.argsort(-np.abs(N[:, 2]))
    for k in order:
        if used[k]:
            continue
        grp = (~used) & (N @ N[k] > cos_tol)
        used |= grp
        Xg = X[grp]; n = N[grp].mean(0); n /= np.linalg.norm(n)
        e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < 0.9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
        P2 = np.c_[(Xg - Xg.mean(0)) @ e1, (Xg - Xg.mean(0)) @ e2]
        idx = np.arange(len(Xg))
        if len(Xg) > 3 and np.ptp(P2[:, 0]) > 1e-6 and np.ptp(P2[:, 1]) > 1e-6:
            try:
                idx = ConvexHull(P2).vertices
            except Exception:
                idx = np.arange(len(Xg))
        if len(idx) > per:
            idx = idx[np.linspace(0, len(idx) - 1, per).astype(int)]
        for q in idx:
            out_x.append(Xg[q]); out_n.append(n)
    return np.array(out_x).reshape(-1, 3), np.array(out_n).reshape(-1, 3)


def patch(S, i, j, tol, Ti=None, Tj=None, key=None):
    """Contact points of the pair: (X, N, side) -- force +f N on part i's body at X when side == 0, on j's when side == 1;
    N points from the pushing part into the pushed one."""
    mi, mj = tm_at(S, i, Ti, key), tm_at(S, j, Tj, key)
    lo_i, hi_i = mi.bounds; lo_j, hi_j = mj.bounds
    Xa, Na = _one_way(mi.vertices, mj, tol, lo_j, hi_j)       # i's vertices on j: j pushes i along j's outward normal
    Xb, Nb = _one_way(mj.vertices, mi, tol, lo_i, hi_i)
    Xa, Na = thin(Xa, Na) if len(Xa) else (Xa, Na)
    Xb, Nb = thin(Xb, Nb) if len(Xb) else (Xb, Nb)
    X = np.r_[Xa, Xb]; N = np.r_[Na, Nb]; side = np.r_[np.zeros(len(Xa), int), np.ones(len(Xb), int)]
    return X, N, side
