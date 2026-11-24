"""Loading the snapshot (snapshot.py) and mesh helpers shared by the stage-1 scripts."""
import os, json
import numpy as np
import units as U


class Snap:
    def __init__(self):
        self.parts = json.load(open(os.path.join(U.GEN, 'parts.json')))
        self.names = [p['name'] for p in self.parts]
        self.idx = {n: i for i, n in enumerate(self.names)}
        z = np.load(os.path.join(U.GEN, 'rest.npz'))
        self.V = [z[f'v{i}'] for i in range(len(self.parts))]
        self.F = [z[f'f{i}'] for i in range(len(self.parts))]
        d = np.load(os.path.join(U.GEN, 'poses.npz'))
        self.poses, self.resid, self.method = d['poses'], d['resid'], d['method']
        self.states = json.load(open(os.path.join(U.GEN, 'states.json')))
        self.lo = np.array([v.min(0) for v in self.V]); self.hi = np.array([v.max(0) for v in self.V])

    def p(self, name):
        return self.parts[self.idx[name]]


_FCL = {}


def fcl_obj(snap, i, T=None):
    import fcl
    if i not in _FCL:
        o = fcl.BVHModel(); o.beginModel(len(snap.V[i]), len(snap.F[i]))
        o.addSubModel(snap.V[i].astype(float), snap.F[i].astype(np.int32)); o.endModel()
        _FCL[i] = o
    if T is None:
        return fcl.CollisionObject(_FCL[i], fcl.Transform())
    return fcl.CollisionObject(_FCL[i], fcl.Transform(T[:3, :3], T[:3, 3]))


def distance(snap, i, j, Ti=None, Tj=None):
    """(gap mm, nearest points) -- gap 0 when the meshes intersect (then see overlap)."""
    import fcl
    req = fcl.DistanceRequest(enable_nearest_points=True); res = fcl.DistanceResult()
    d = fcl.distance(fcl_obj(snap, i, Ti), fcl_obj(snap, j, Tj), req, res)
    return max(0.0, float(d)), np.array(res.nearest_points[0]), np.array(res.nearest_points[1])


def collide(snap, i, j, Ti=None, Tj=None, maxc=200):
    import fcl
    req = fcl.CollisionRequest(num_max_contacts=maxc, enable_contact=True); res = fcl.CollisionResult()
    fcl.collide(fcl_obj(snap, i, Ti), fcl_obj(snap, j, Tj), req, res)
    return res


_MAN = {}


def manifold(snap, i):
    from manifold3d import Manifold, Mesh
    if i not in _MAN:
        _MAN[i] = Manifold(Mesh(vert_properties=snap.V[i].astype(np.float32), tri_verts=snap.F[i].astype(np.uint32)))
    return _MAN[i]


def overlap(snap, i, j):
    return float((manifold(snap, i) ^ manifold(snap, j)).volume())
