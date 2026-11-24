"""Stage 1, step B (spec §4.3): the parts of the model at rest and in a sample of states covering every motion; the pose
of each part as a rigid body relative to rest (Kabsch on corresponding vertices, ICP when the mesh changed).

Writes gen/physics/rest.npz (vertices and faces of every part at rest), gen/physics/parts.json (fields of every part),
gen/physics/poses.npz (4x4 pose, residual and method of every part in every state) and gen/physics/states.json.
Usage: python3 -I tools/physics/snapshot.py [--quick]"""
import sys, os, json, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.spatial import cKDTree
import parts as PT, params as P, scenarios as SC, contacts as CT, geo, escape as E


def kabsch(A, B):
    ca, cb = A.mean(0), B.mean(0)
    H = (A - ca).T @ (B - cb)
    Us, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ Us.T))
    R = Vt.T @ np.diag([1, 1, d]) @ Us.T
    t = cb - R @ ca
    res = float(np.abs((A @ R.T + t) - B).max())
    return R, t, res


def icp(A, B, iters=40):
    """Point-to-point ICP of rest vertices A onto state vertices B (both mm); residual = largest nearest-vertex distance
    after the fit, both ways (so a reshaped part does not pass)."""
    tree = cKDTree(B)
    R, t = np.eye(3), B.mean(0) - A.mean(0)
    sub = A if len(A) <= 4000 else A[np.random.default_rng(0).choice(len(A), 4000, replace=False)]
    for _ in range(iters):
        X = sub @ R.T + t
        d, j = tree.query(X)
        R2, t2, _ = kabsch(sub, B[j])
        if np.allclose(R2, R, atol=1e-10) and np.allclose(t2, t, atol=1e-8):
            break
        R, t = R2, t2
    X = A @ R.T + t
    d1, _ = tree.query(X)
    d2, _ = cKDTree(X).query(B)
    return R, t, float(max(d1.max(), d2.max()))


def T44(R, t):
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = t
    return M


def state_list(quick=False):
    """(tag, scenario, State) covering the motions of every scenario and the contact audit (spec §4.3, step B)."""
    out = [('rest', 'rest', PT.State())]
    S = PT.State
    for row in (P.REST_ROW, 0, 3.5, 7):
        for pos in (0, 2.5, 5, 7.5, 10):
            if (pos, row) != (5, P.REST_ROW):
                out.append((f'shuttle pos {pos} row {row}', 'shuttle', S(pos=float(pos), row=float(row))))
    for su in (0, 9, 17):
        for row, hm in ((P.REST_ROW, 0.0), (7, 0.0), (0, 1.0), (7, 1.0)):
            out.append((f'slide {su}u row {row} hammer {hm}', 'slide', S(slide_u=float(su), row=float(row), hammer=hm)))
    for car in np.linspace(P.CAR_X_START, P.CAR_X_END, 7):
        for hm in (0.0, 1.0):
            out.append((f'car {car:.0f} hammer {hm}', 'carriage', S(car=float(car), hammer=hm, slide_u=17 if hm == 0 else 0)))
    keys = PT.key_list()
    for i, k in enumerate(keys):
        tiers = (0, 1) if i % 3 == 0 else (0,)
        for tier in tiers:
            fr = SC.key_frames(k, tier)
            su = P.MARK_REF_U if 'O' in fr else 0.0
            out.append((f"key {k['id']} tier {tier}", 'keys', S(pressed={k['n']: 1.0}, frames=fr, tier=tier, lock=1.0, slide_u=su)))
            if i % 4 == 0 and tier == 0:
                out.append((f"key {k['id']} half", 'keys', S(pressed={k['n']: 0.5}, frames={b: v * 0.5 for b, v in fr.items()},
                                                              tier=tier, slide_u=su * 0.5)))
    for nm, N in (('B', 0.0), ('C', 16.0)):
        other = 'C' if nm == 'B' else 'B'
        for kk in (0, 4, 8):
            for f in (0.4, 1.0):
                out.append((f'mark {nm}={kk} at {f}', 'marks', S(slide_u=(P.MARK_REF_U + kk) * f, frames={'O': 16.0 * f, 'N': N * f},
                                                               mem={nm: float(kk), other: 3.0})))
    step = 30 if quick else 10
    for a in range(0, 360, step):
        for pos_t, row_t in ((0, 0), (10, 7), (4, 5)):
            out.append((f'cycle {a} target {pos_t}/{row_t}', 'cycle', SC.cycle_state(float(a), pos_t, row_t)))
    for a in range(0, 360, 30):
        for lab, pos_t, row_t, kw in (('mark a', 6, 0, dict(lock_read=1.0, slide_u=float(P.MARK_REF_U + 4), frames={'O': 16.0})),
                                      ('space', 5, 0, dict(lock_read=1.0, lock_hammer=1.0, frames={'W': 2.0, 'R': 16.0}))):
            out.append((f'idle {lab} cycle {a}', 'idle', SC.cycle_state(float(a), pos_t, row_t, **kw)))
    import reader as RD
    for m in (0, 4, 10):
        for r_ in (0, 3, 7):
            v = RD.cell_code(m, r_)
            if v is None:
                continue
            feel, fr = RD.read_state(v, 1.0)
            out.append((f'read {m}/{r_ + 1}', 'read', S(pos=float(m), row=float(r_), detent=1.0, feel=feel, frames=fr,
                                                        mem={'B': float(v[1]), 'C': float(v[2])})))
    es = SC.escape_states()
    for i, (st, tag) in enumerate(es):
        if not quick or i % 4 == 0:
            out.append((tag, 'escape', st))
    seen = set()
    for grp, title, states, pairs in CT.groups():
        for tag, st in states:
            if (grp, tag) in seen:
                continue
            seen.add((grp, tag))
            out.append((f'contacts {grp} {tag}', 'contacts', st))
    out.append(('margins L', 'carriage', S(car=P.CAR_X_START)))
    out.append(('margins R', 'carriage', S(car=P.CAR_X_END)))
    out.append(('locks in', 'idle', S(lock_read=1.0, lock_hammer=1.0)))
    out.append(('release 1', 'escape', S(car_release=1.0)))
    out.append(('cock 1', 'cycle', S(cock=1.0)))
    out.append(('ribbon up', 'cycle', S(ribbon=1.0)))
    out.append(('detent in', 'cycle', S(detent=1.0)))
    return out


def state_dict(st):
    d = {}
    for k, v in st.__dict__.items():
        if isinstance(v, dict):
            d[k] = {str(a): b for a, b in v.items()}
        elif isinstance(v, tuple):
            d[k] = list(v)
        else:
            d[k] = v
    return d


def main():
    quick = '--quick' in sys.argv
    os.makedirs(U.GEN, exist_ok=True)
    t0 = time.time()
    rest = PT.build(PT.State())
    print('rest built', round(time.time() - t0, 1), 's', len(rest), flush=True)
    names = [p.name for p in rest]
    assert len(set(names)) == len(names), 'part names must be unique'
    RV, RF = [], []
    for p in rest:
        V, F = geo.to_arrays(p.mesh)
        RV.append(np.asarray(V, float)); RF.append(np.asarray(F, np.int32))
    np.savez_compressed(os.path.join(U.GEN, 'rest.npz'), **{f'v{i}': RV[i] for i in range(len(rest))},
                        **{f'f{i}': RF[i] for i in range(len(rest))})
    meta = [dict(name=p.name, group=p.group, kind=p.kind, bom=p.bom, mat=p.mat, note=p.note, mov=p.mov, nv=len(RV[i]))
            for i, p in enumerate(rest)]
    json.dump(meta, open(os.path.join(U.GEN, 'parts.json'), 'w'), ensure_ascii=False, indent=0)
    states = state_list(quick)
    print('states', len(states), flush=True)
    N = len(rest)
    poses = np.zeros((len(states), N, 4, 4))
    resid = np.full((len(states), N), np.nan)
    method = np.zeros((len(states), N), np.int8)    # 0 same mesh, 1 kabsch, 2 icp, -1 missing
    smeta = []
    idx = {n: i for i, n in enumerate(names)}
    for s, (tag, scen, st) in enumerate(states):
        ps = PT.build(st)
        seen = np.zeros(N, bool)
        for p in ps:
            i = idx.get(p.name)
            if i is None:
                continue
            seen[i] = True
            V, _ = geo.to_arrays(p.mesh); V = np.asarray(V, float)
            A = RV[i]
            if V.shape == A.shape and np.abs(V - A).max() < 1e-9:
                poses[s, i] = np.eye(4); resid[s, i] = 0.0; method[s, i] = 0
                continue
            if V.shape == A.shape:
                R, t, r = kabsch(A, V)
                if r < 1e-3:
                    poses[s, i] = T44(R, t); resid[s, i] = r; method[s, i] = 1
                    continue
            R, t, r = icp(A, V)
            poses[s, i] = T44(R, t); resid[s, i] = r; method[s, i] = 2
        method[s, ~seen] = -1
        smeta.append(dict(tag=tag, scen=scen, state=state_dict(st)))
        if s % 25 == 0:
            print(s, tag, round(time.time() - t0, 1), 's', flush=True)
    np.savez_compressed(os.path.join(U.GEN, 'poses.npz'), poses=poses, resid=resid, method=method)
    json.dump(smeta, open(os.path.join(U.GEN, 'states.json'), 'w'), ensure_ascii=False, indent=0, default=float)
    print('done', round(time.time() - t0, 1), 's')
    bad = resid > 0.02
    for i in np.nonzero(bad.any(0))[0]:
        print('  non-rigid', names[i], int(bad[:, i].sum()), 'states, max', round(float(np.nanmax(resid[:, i])), 3))


if __name__ == '__main__':
    main()
