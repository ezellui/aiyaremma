"""Stage 1, step A (spec §4.3): candidate pairs at rest -- every pair of parts closer than GAP (FCL on the triangle
BVHs) or overlapping, plus the driving pairs of the contact audit. Writes gen/physics/pairs.json.
Usage: python3 -I tools/physics/candidates.py"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import meshes as MS
import checks

GAP = 0.25        # mm: the spec's 0.1 mm misses pins in printed bores with 0.1..0.2 mm clearance; the gap is recorded


def main():
    t0 = time.time()
    S = MS.Snap()
    N = len(S.names)
    lo, hi = S.lo - GAP, S.hi + GAP
    out = []
    for i in range(N):
        ov = np.all(lo[i + 1:] <= S.hi[i], 1) & np.all(hi[i + 1:] >= S.lo[i], 1)
        for j in np.nonzero(ov)[0] + i + 1:
            g, pa, pb = MS.distance(S, i, j)
            if g > GAP:
                continue
            o = MS.overlap(S, i, j) if g == 0.0 else 0.0
            out.append(dict(a=S.names[i], b=S.names[j], gap=round(g, 4), overlap=round(o, 3), allow=bool(checks.allowed(S.names[i], S.names[j])),
                            pa=[round(float(x), 3) for x in pa], pb=[round(float(x), 3) for x in pb]))
        if i % 100 == 0:
            print(i, len(out), round(time.time() - t0, 1), 's', flush=True)
    import contacts as CT
    have = {(p['a'], p['b']) for p in out} | {(p['b'], p['a']) for p in out}
    extra = 0
    for grp, title, states, pairs in CT.groups():
        for a, b, note in pairs:
            if (a, b) not in have and a in S.idx and b in S.idx:
                g, pa, pb = MS.distance(S, S.idx[a], S.idx[b])
                out.append(dict(a=a, b=b, gap=round(g, 4), overlap=0.0, allow=bool(checks.allowed(a, b)), pa=pa.round(3).tolist(),
                                pb=pb.round(3).tolist(), audit=note))
                have |= {(a, b), (b, a)}; extra += 1
    json.dump(out, open(os.path.join(U.GEN, 'pairs.json'), 'w'), ensure_ascii=False, indent=0)
    print('pairs', len(out), 'audit-only', extra, 'overlapping', sum(p['overlap'] > 0 for p in out),
          'touching (<=0.06)', sum(p['gap'] <= 0.06 for p in out), round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
