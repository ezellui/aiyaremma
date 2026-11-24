"""Stage 2, node H (rev. 0.14): the springs that had no number (data/springs.json, k and preload both empty).

Without a bench a spring cannot be tuned, but its least force can be computed: it must bring its part back over
the part's own travel within the time the machine gives it, against the part's weight, with friction on top.
For every such spring:
  * the part and its travel come from the model's own motions (gen/physics/poses.npz, every state of the sample):
    the farthest pose from rest gives the centroid's travel s, the turn phi and its height change dz;
  * its inertia: m_eff = m + I_c (phi / s)^2 (the turn about the centroid counted on the centroid's path);
  * the time: a part of the cycle gets 30 deg of the fastest cycle (governor's free speed, 0.18 s a turn: 15 ms);
    a pawl must fall between two teeth, 10 % of that (1.5 ms is too short for anything: 5 ms is taken, the pawls
    fall while the tooth passes under them at most a third of a tooth a ms); a part driven by a key gets the key's
    return, 50 ms;
  * F = 2 m_eff s / t^2 + m g max(0, dz / s) (lifting) + friction mu (0.35, PETG) on the force itself;
    the preload written is 1.5 F, rounded up to 0.05 N; never below 0.1 N (a spring has to hold the part on its
    stop against shocks: 3 g on the part, the part's weight times 3).
Writes gen/physics/node_h.json and updates the springs in data/springs.json (status 'calculated', source node H).
Usage: python3 -I tools/physics/node_h.py"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import units as U

CYCLE_FAST = 0.18           # s per turn at the governor's free speed
WIN = {'cycle': 30.0 / 360.0 * CYCLE_FAST, 'pawl': 0.005, 'key': 0.050}
KIND = {'sector return spring B': 'cycle', 'sector return spring C': 'cycle', 'bksp link spring': 'key',
        'back link spring': 'key', 'memory lever M return spring': 'cycle', 'memory holding pawl spring': 'pawl',
        'stop carrier spring': 'cycle', 'W latch pawl spring': 'pawl', 'pm-u detent spring': 'pawl',
        'carriage release key spring': 'key', 'read lock spring': 'cycle', 'hammer lock spring': 'cycle',
        'detent pawl return': 'pawl'}
MU = 0.35


def main():
    parts = json.load(open(os.path.join(U.GEN, 'parts.json')))
    idx = {p['name']: i for i, p in enumerate(parts)}
    P = np.load(os.path.join(U.GEN, 'poses.npz'))['poses']
    MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
    path = os.path.join(U.DATA, 'springs.json')
    SJ = json.load(open(path))
    rows = []
    for sp in SJ['springs']:
        if sp['k'] is not None or sp['preload'] is not None or sp['name'] not in KIND:
            continue
        nm = sp['a']
        if nm.endswith(' (all keys)'):
            nm = nm.split(' (')[0]
        if nm not in idx or nm not in MASS:
            rows.append(dict(name=sp['name'], part=nm, why='детали нет в модели')); continue
        i = idx[nm]; Ps = P[:, i]
        ok = np.isfinite(Ps).all(axis=(1, 2))
        T0 = Ps[0]
        c = np.array(MASS[nm]['c']) / U.MM if max(abs(v) for v in MASS[nm]['c']) < 10 else np.array(MASS[nm]['c'])
        best = (0.0, 0.0, 0.0)
        for k in np.flatnonzero(ok):
            R = Ps[k][:3, :3] @ T0[:3, :3].T
            ck = Ps[k][:3, :3] @ np.linalg.inv(T0[:3, :3]) @ (c - T0[:3, 3]) + Ps[k][:3, 3]
            s = float(np.linalg.norm(ck - c))
            phi = float(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
            if s + 10 * phi > best[0] + 10 * best[1]:
                best = (s, phi, float(ck[2] - c[2]))
        s, phi, dz = best
        m = MASS[nm]['m']; I = np.array(MASS[nm]['I'])
        Ic = float(np.max(np.linalg.eigvalsh(I)))
        if s < 0.05 and phi < 0.01:
            rows.append(dict(name=sp['name'], part=nm, why='деталь в выборке состояний не движется', m_g=m * 1e3)); continue
        s_m = max(s, 0.05) * U.MM
        m_eff = m + Ic * (phi / s_m) ** 2 if s_m > 0 else m
        t = WIN[KIND[sp['name']]]
        F = 2 * m_eff * s_m / t ** 2 + m * U.G * max(0.0, -dz / max(s, 1e-6))      # returning lifts it if it went down
        F *= 1 + MU
        F = max(F, 3 * m * U.G, 0.1 / 1.5)
        pre = math.ceil(1.5 * F / 0.05) * 0.05
        rows.append(dict(name=sp['name'], part=nm, kind=KIND[sp['name']], t_ms=t * 1e3, m_g=m * 1e3, m_eff_g=m_eff * 1e3,
                         travel_mm=s, turn_deg=math.degrees(phi), dz_mm=dz, F_min_N=F, preload_N=pre))
        sp.update(preload=round(pre, 2), status='calculated',
                  source=f"узел H (ред. 0.14): возврат за {t * 1e3:.0f} мс, ход {s:.1f} мм / {math.degrees(phi):.0f}°, "
                         f"m_эфф {m_eff * 1e3:.1f} г; натяг = 1,5 × расчётного минимума",
                  note=(sp.get('note') or '') + ' · число расчётное, уточнить на стенде')
    json.dump(SJ, open(path, 'w'), ensure_ascii=False, indent=1)
    json.dump(dict(rows=rows, windows_ms={k: v * 1e3 for k, v in WIN.items()}, mu=MU), open(os.path.join(U.GEN, 'node_h.json'), 'w'),
              ensure_ascii=False, indent=1, default=float)
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == '__main__':
    main()
