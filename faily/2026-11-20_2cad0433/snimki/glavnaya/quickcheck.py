"""Quick interference check of chosen parts against everything else over a sample of states (the same rule as
checks.py: overlap > 0.05 mm3 and the pair not in ALLOW). For iterating on model changes before the full build.
Usage: python3 -I tools/physics/quickcheck.py NAME_PREFIX [NAME_PREFIX ...] [--fast]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import parts as PT, params as P, scenarios as SC, checks


def states(fast=False):
    out = [('rest', PT.State())]
    step = 30 if fast else 10
    for a in range(0, 360, step):
        for pt, rt in ((0, 0), (10, 7), (0, 7), (10, 0), (4, 5)):
            out.append((f'cycle {a} {pt}/{rt}', SC.cycle_state(float(a), pt, rt)))
    for a in range(0, 360, 30):
        out.append((f'idle space {a}', SC.cycle_state(float(a), 5, 0, lock_read=1.0, lock_hammer=1.0, frames={'W': 2.0, 'R': 16.0})))
        out.append((f'idle mark {a}', SC.cycle_state(float(a), 6, 0, lock_read=1.0, slide_u=float(P.MARK_REF_U + 4), frames={'O': 16.0})))
    for su in (0, 9, 17):
        for pos in (0, 5, 10):
            for row, hm in ((P.REST_ROW, 0.0), (7, 0.0), (0, 1.0), (7, 1.0)):
                out.append((f'slide {su} {pos} {row} {hm}', PT.State(pos=pos, slide_u=su, row=row, hammer=hm)))
    for car in np.linspace(P.CAR_X_START, P.CAR_X_END, 5):
        out.append((f'car {car:.0f}', PT.State(car=float(car))))
    for k in PT.key_list()[::5]:
        fr = SC.key_frames(k, 0)
        out.append((f"key {k['id']}", PT.State(pressed={k['n']: 1.0}, frames=fr, lock=1.0)))
    return out


def main():
    pref = [a for a in sys.argv[1:] if not a.startswith('--')]
    fast = '--fast' in sys.argv
    bad = {}
    for tag, st in states(fast):
        ps = PT.build(st)
        mine = [p for p in ps if any(p.name.startswith(x) for x in pref)]
        rest = [p for p in ps if p not in mine]
        bm = checks.bboxes(mine); br = checks.bboxes(rest)
        for i, a in enumerate(mine):
            ov = np.all(br[:, :3] < bm[i, 3:] - 0.05, 1) & np.all(br[:, 3:] > bm[i, :3] + 0.05, 1)
            for j in np.nonzero(ov)[0]:
                b = rest[j]
                if checks.allowed(a.name, b.name):
                    continue
                v = (a.mesh ^ b.mesh).volume()
                if v > 0.05:
                    k = (a.name, b.name)
                    if k not in bad or v > bad[k][0]:
                        bad[k] = (round(v, 2), tag)
        for i, a in enumerate(mine):
            for j in range(i + 1, len(mine)):
                b = mine[j]
                if a.mov == b.mov or checks.allowed(a.name, b.name):
                    continue
                v = (a.mesh ^ b.mesh).volume()
                if v > 0.05:
                    k = (a.name, b.name)
                    if k not in bad or v > bad[k][0]:
                        bad[k] = (round(v, 2), tag)
    print('parts checked:', sorted({p.name for p in mine})[:40])
    print('interferences:', len(bad))
    for k, v in sorted(bad.items(), key=lambda x: -x[1][0])[:60]:
        print('  ', k, v)


if __name__ == '__main__':
    main()
