"""Stage 2, node F (spec §5.2): the feelers. Each feeler is pushed out by its spring (params.READ_F_SPRING) against its
load (READ_F_LOAD) and drags its receiver through the wire (W: rod Y, the bellcrank, rod X, the stop U; B and C: the
slide and the memory sleeve); the retract bar (read cam 'read', ramps READ_RAMP) lets it go over 118..140 deg and takes
it back from 150 deg. The feeler follows the bar while its spring can accelerate the chain faster than the bar
recedes, then runs free until it meets its tab at READ_C0 + READ_K v. The cycle shaft's speed along the revolution comes
from node B's integration (the same character's targets).
Outputs: the angle where each feeler sits on its tab (criterion: by 145 deg, 5 deg before the bar returns), the bounce
off the tab (criterion: under half a code step, 0.5 mm), the force the feeler's spring would need.
Usage: python3 -I tools/physics/node_f.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import params as P
import node_b as NB

MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
WIRE_G = 0.5e-3          # inner wire of a Bowden cable, ~0.5 g over its run (assumption)


def chain(ch):
    g = lambda n: MASS[n]['m']
    if ch == 'W':
        parts = ['feeler W', 'W wire clamp', 'escapement rod Y', 'W latch rack', 'escapement bellcrank', 'escapement rod X',
                 'escapement stop', 'escapement stop finger', 'escapement tape']
    else:
        parts = [f'feeler {ch}', f'read slide {ch}', f'memory sleeve {ch}']
    return sum(g(n) for n in parts) + WIRE_G, parts


def bar(phi):
    import parts as PT
    return (1.0 - PT.cam_lift('read', phi)) * P.READ_TRAVEL * U.MM


def run(ch, v_code, trace, F_spring=None, F_load=None, e=0.5):
    """trace: (t, phi) of the revolution. Returns arrival angle, speed, bounce."""
    m, _ = chain(ch)
    Fs = P.READ_F_SPRING[ch] if F_spring is None else F_spring
    Fl = P.READ_F_LOAD[ch] if F_load is None else F_load
    a = (Fs - Fl) / m
    x_tab = (P.READ_C0 + P.READ_K * v_code) * U.MM
    t, phi = trace
    i0 = np.searchsorted(phi, P.CYCLE['read'][0] - P.READ_RAMP[0] - 1)
    x = 0.0; v = 0.0
    for k in range(i0, len(t) - 1):
        dt = t[k + 1] - t[k]
        b = bar(phi[k + 1])
        xf = x + v * dt + 0.5 * a * dt * dt
        vf = v + a * dt
        if xf > b:                       # held back by the bar (it recedes slower than the feeler could go)
            vf = (b - x) / dt; xf = b
        if xf >= x_tab:
            v_hit = vf
            reb = (e * v_hit) ** 2 / (2 * a) if a > 0 else float('inf')
            return dict(arrive_deg=float(phi[k + 1]), v_hit=float(v_hit), bounce_mm=float(reb * 1e3), a=a)
        x, v = xf, vf
        if phi[k + 1] > P.CYCLE['read'][1]:
            break
    return dict(arrive_deg=None, short_mm=float((x_tab - x) * 1e3), a=a, reached_mm=float(x * 1e3))


def main():
    import reader as RD
    res = {}
    MO = NB.motor_module()
    I_rot, m_lift, ro, lo = NB.chain_masses()
    tau = NB.MJ['tau_C']; cg = (tau - MO.TAU_FRIC) / MO.W_FREE ** 2
    traces = {}
    for lab, (pos, row) in (('дальняя (0, 7)', (0, 7)), ('средняя (4, 5)', (4, 5)), ('ближняя (5, 0)', (5, 0))):
        th, dz = NB.target(pos, row)
        tr = NB.cycle(tau, cg, th, dz, I_rot, m_lift, er=MO.read_work(None))
        traces[lab] = (tr[:, 0], tr[:, 1])
    # the fastest the shaft can turn through the reading: the governor's free speed
    w = MO.W_FREE
    ph = np.arange(0, 360.01, 0.1); traces['свободный ход регулятора'] = (np.radians(ph) / w, ph)
    res['masses_g'] = {ch: chain(ch)[0] * 1e3 for ch in P.READ_CH}
    rows = []
    for lab, trc in traces.items():
        for ch in P.READ_CH:
            for v in ((4, 8, 12) if ch == 'W' else (0, 4, 8, 9) if ch == 'C' else (0, 4, 8)):
                r = run(ch, v, trc)
                rows.append(dict(cycle=lab, ch=ch, v=v, **r))
    res['rows'] = rows
    # the spring a channel would need to sit on its farthest tab by 145 deg at the governor's free speed
    need = {}
    for ch, vmax in (('W', 12), ('B', 8), ('C', 9)):
        lo_, hi_ = P.READ_F_LOAD[ch], 50.0
        for _ in range(40):
            mid = 0.5 * (lo_ + hi_)
            r = run(ch, vmax, traces['свободный ход регулятора'], F_spring=mid)
            if r['arrive_deg'] is not None and r['arrive_deg'] <= 145.0:
                hi_ = mid
            else:
                lo_ = mid
        need[ch] = dict(F_spring_N=hi_, now=P.READ_F_SPRING[ch])
        lo_, hi_ = P.READ_F_LOAD[ch], 50.0
        for _ in range(40):
            mid = 0.5 * (lo_ + hi_)
            r = run(ch, vmax, traces['средняя (4, 5)'], F_spring=mid)
            if r['arrive_deg'] is not None and r['arrive_deg'] <= 145.0:
                hi_ = mid
            else:
                lo_ = mid
        need[ch]['F_spring_avg_N'] = hi_
    res['spring_needed'] = need
    # extra work of a stronger W spring per character (taken back by the read cam), J
    res['extra_energy_mJ'] = {ch: (need[ch]['F_spring_N'] - P.READ_F_SPRING[ch]) * (P.READ_C0 + P.READ_K * 12) * 1e-3 / 0.8 * 1e3 for ch in need}
    json.dump(res, open(os.path.join(U.GEN, 'node_f.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    for r in rows:
        print(r)
    print('masses', res['masses_g']); print('need', need); print('extra energy', res['extra_energy_mJ'])


if __name__ == '__main__':
    main()
