"""Swept occupancy of the machine: every part's surface sampled and moved through the snapshot's states, marked on a
2 mm voxel grid. free(box) tells whether a box (mm) stays clear of everything in every state. For placing new
supports. Writes gen/physics/occupancy.npz. Usage: python3 -I tools/physics/occupancy.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import trimesh
import meshes as MS

VOX = 2.0
LO = np.array([-270.0, -420.0, -10.0]); HI = np.array([270.0, 160.0, 420.0])


def build():
    S = MS.Snap()
    shape = np.ceil((HI - LO) / VOX).astype(int)
    occ = np.zeros(shape, bool)
    for i, p in enumerate(S.parts):
        if p['group'] == 'case':
            continue
        tm = trimesh.Trimesh(S.V[i], S.F[i], process=False)
        n = int(min(20000, max(200, tm.area / 1.0)))
        pts = np.r_[tm.sample(n), S.V[i]]
        moves = p['mov'] != 'fixed' and np.any(S.method[:, i] > 0)
        Ts = [np.eye(4)] if not moves else [S.poses[s, i] for s in range(len(S.states)) if S.method[s, i] >= 0]
        for T in Ts:
            X = pts @ T[:3, :3].T + T[:3, 3]
            k = np.floor((X - LO) / VOX).astype(int)
            ok = np.all((k >= 0) & (k < shape), 1)
            occ[k[ok, 0], k[ok, 1], k[ok, 2]] = True
    np.savez_compressed(os.path.join(U.GEN, 'occupancy.npz'), occ=occ, lo=LO, vox=VOX)
    print('occupied voxels', int(occ.sum()), 'of', occ.size)


_O = None


def load():
    global _O
    if _O is None:
        z = np.load(os.path.join(U.GEN, 'occupancy.npz')); _O = (z['occ'], z['lo'], float(z['vox']))
    return _O


def hits(lo, hi, margin=0.5):
    occ, L0, v = load()
    a = np.floor((np.asarray(lo) - margin - L0) / v).astype(int); b = np.ceil((np.asarray(hi) + margin - L0) / v).astype(int)
    a = np.clip(a, 0, np.array(occ.shape) - 1); b = np.clip(b, 1, np.array(occ.shape))
    return int(occ[a[0]:b[0], a[1]:b[1], a[2]:b[2]].sum())


if __name__ == '__main__':
    build()
