"""Stage 2, node A (spec §5.2): the key. One coordinate x, the key's travel (0..16 mm, lever ratio 1 at the key): the
cap and stem, the plate under the key, the lever (its inertia about the pivot reflected to the key, its weight's
moment), the frames the key's plate drives (letter: R; dead mark: O and N, plus the O link's spring; space: R and W)
with their springs (links.json frames: F_pre, k for both springs) and weights. Finger force: a trapezoid 0 -> F in
20 ms, held 60 ms, off in 10 ms (F = 1, 2, 3 N), or a tap at 0.3 m/s. Stops: the full stroke (16 mm) and the rest
(frames on their rest stops) are elastic contacts with restitution e. Integrated with events (solve_ivp).
Outputs: time to the full stroke, force on the finger along the stroke, the return time, cap bounce.
Usage: python3 -I tools/physics/node_a.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.integrate import solve_ivp
import params as P

MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
LJ = json.load(open(os.path.join(U.ROOT, 'gen', 'links.json')))
TRAVEL = P.KEY_TRAVEL * U.MM
PIV = np.array([P.LEVER_PIVOT_Y, (P.LEVER_Z0 + P.LEVER_Z1) / 2]) * U.MM


def key_chain(kid, frames):
    cap, stem, lev, pl = (MASS[f'cap {kid}'], MASS[f'stem {kid}'], MASS[f'lever {kid}'], MASS[f'plate {kid}'])
    L = abs(cap['c'][1] - PIV[0])                                     # key to pivot along Y
    lc = np.array(lev['c'][1:]) - PIV
    I_lev = np.array(lev['I'])[0, 0] + lev['m'] * (lc @ lc)
    grubs = sum(MASS[n]['m'] for n in MASS if n.startswith(f'grub {kid} '))
    m_direct = cap['m'] + stem['m'] + pl['m'] + grubs
    m_eff = m_direct + I_lev / L ** 2
    W_down = (m_direct + lev['m'] * (-lc[0]) / L) * U.G             # weight at the key (the lever's centre lies in front)
    fr = []
    for f in frames:
        d = LJ['frames'][f]
        mf = sum(MASS[n]['m'] for n in MASS if n.startswith(f'bail {f} ') and 'spring' not in n)
        fr.append(dict(name=f, m=mf, F_pre=d['F_pre'], k=d['k'] * 1e3, W=mf * U.G))
    return dict(L=L, m_eff=m_eff, W_down=W_down, frames=fr, I_lev=I_lev)


def simulate(ch, F=2.0, tap=None, mu_guide=0.35, F_lat=0.05, e_bot=0.5, e_top=0.5, extra_ret=0.0, O_spring=False, t_end=0.4):
    m = ch['m_eff'] + sum(f['m'] for f in ch['frames'])
    k_stop = m * (math.pi / 1e-3) ** 2               # stops: 1 ms contact
    def cst(e):
        ln = math.log(e); z = -ln / math.sqrt(math.pi ** 2 + ln ** 2); return 2 * z * math.sqrt(k_stop * m)
    c_bot, c_top = cst(e_bot), cst(e_top)
    fric = mu_guide * F_lat                          # the stem in its comb, the frames' sleeves (lateral load ~F_lat)
    def finger(t):
        if tap is not None:
            return 0.0
        if t < 0.02: return F * t / 0.02
        if t < 0.08: return F
        if t < 0.09: return F * (0.09 - t) / 0.01
        return 0.0
    def rhs(t, y):
        x, v = y
        f = finger(t) + ch['W_down']                  # down = +x
        for fr in ch['frames']:
            f -= fr['F_pre'] + fr['k'] * x - fr['W']
        if O_spring:
            f -= LJ['stops']['F_spring'][0] if x > 2e-3 else 0.0
        f -= extra_ret
        if abs(v) > 1e-5:
            f -= math.copysign(fric, v)
        if x > TRAVEL:
            f -= k_stop * (x - TRAVEL) + c_bot * v if k_stop * (x - TRAVEL) + c_bot * v > 0 else 0.0
        if x < 0:
            f += max(0.0, -k_stop * x - c_top * v)
        return [v, f / m]
    v0 = tap if tap is not None else 0.0
    s = solve_ivp(rhs, (0, t_end), [0.0, v0], method='Radau', max_step=5e-5, rtol=1e-8, atol=1e-11, dense_output=True)
    t, x, v = s.t, s.y[0], s.y[1]
    out = dict(F=F, tap=tap)
    full = np.nonzero(x >= 15.5e-3)[0]
    out['t_trip_ms'] = float(t[full[0]] * 1e3) if len(full) else None          # 15.5 mm: the cycle trips
    bot = np.nonzero(x >= TRAVEL)[0]
    out['t_full_ms'] = float(t[bot[0]] * 1e3) if len(bot) else None
    rel = 0.09 if tap is None else 0.0
    after = t > rel
    back = np.nonzero(after & (x <= 0.0))[0]
    out['t_return_ms'] = float((t[back[0]] - rel) * 1e3) if len(back) else None
    if len(back):
        k0 = back[0]
        out['bounce_mm'] = float(max(0.0, -x[k0:].min()) * 1e3)                 # under the rest: the stop's give
        out['rebound_mm'] = float(x[k0 + 5:].max() * 1e3) if k0 + 5 < len(x) else 0.0     # down again after the stop
    out['x_max_mm'] = float(x.max() * 1e3)
    # static force on the finger along the stroke (press, slow)
    xs = np.linspace(0, TRAVEL, 9)
    out['F_static'] = [round(float(sum(fr['F_pre'] + fr['k'] * xx - fr['W'] for fr in ch['frames']) - ch['W_down'] + extra_ret +
                                   (LJ['stops']['F_spring'][0] if O_spring and xx > 2e-3 else 0.0) + fric), 3) for xx in xs]
    out['trace'] = [t[::max(1, len(t) // 300)].tolist(), (x[::max(1, len(t) // 300)] * 1e3).tolist()]
    return out


def main():
    res = {}
    cases = (('буква k24', 'k24', ('R',), False), ('буква k10', 'k10', ('R',), False), ('мёртвый k38', 'k38', ('O', 'N'), True),
             ('пробел 6u', 'space6', ('R', 'W'), False))
    for lab, kid, frs, osp in cases:
        ch = key_chain(kid, frs)
        rows = []
        for F in (1.0, 2.0, 3.0):
            rows.append({k: v for k, v in simulate(ch, F=F, O_spring=osp).items() if k != 'trace'})
        tap = {k: v for k, v in simulate(ch, tap=0.3, O_spring=osp).items() if k != 'trace'}
        net_up = sum(f['F_pre'] - f['W'] for f in ch['frames']) - ch['W_down']
        # the extra return force for a 0.1 s return (with friction at its maximum)
        need = None
        for ex in np.arange(0.0, 1.5, 0.02):
            r = simulate(ch, F=2.0, O_spring=osp, extra_ret=float(ex), mu_guide=0.5)
            if r['t_return_ms'] is not None and r['t_return_ms'] <= 100.0:
                need = float(ex); break
        sens = []
        for mu in (0.25, 0.35, 0.5):
            for e in (0.3, 0.7):
                r = simulate(ch, F=2.0, O_spring=osp, mu_guide=mu, e_top=e, e_bot=e)
                sens.append(dict(mu=mu, e=e, t_return_ms=r['t_return_ms'], rebound_mm=r.get('rebound_mm')))
        res[lab] = dict(m_eff_g=(ch['m_eff'] + sum(f['m'] for f in ch['frames'])) * 1e3, key_weight_N=ch['W_down'],
                        frames=[f['name'] for f in ch['frames']], net_return_at_rest_N=net_up, press=rows, tap=tap,
                        extra_return_for_100ms_N=need, sensitivity=sens)
        print(lab, 'm', round(res[lab]['m_eff_g'], 1), 'g; net return', round(net_up, 3), 'N;', [(r['F'], r['t_full_ms'], r['t_return_ms'], r.get('rebound_mm')) for r in rows],
              'tap', tap['t_full_ms'], tap['t_return_ms'], 'need extra', need)
    json.dump(res, open(os.path.join(U.GEN, 'node_a.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for (lab, kid, frs, osp), col in zip(cases, ('#c44536', '#2a6f97', '#3a8a50', '#e0a030')):
        r = simulate(key_chain(kid, frs), F=2.0, O_spring=osp)
        ax.plot(np.array(r['trace'][0]) * 1e3, r['trace'][1], color=col, label=lab)
    ax.axhline(16, color='k', lw=0.5, ls=':'); ax.axvline(90, color='k', lw=0.5, ls=':'); ax.axvline(190, color='k', lw=0.5, ls='--')
    ax.set_xlabel('время, мс'); ax.set_ylabel('ход клавиши, мм'); ax.invert_yaxis(); ax.legend(fontsize=8)
    ax.set_title('Узел A: нажатие 2 Н (20/60/10 мс) и возврат; штрих — 0,1 с после отпускания')
    fig.tight_layout(); fig.savefig(os.path.join(U.GEN, 'node_a_key.png'), dpi=130); plt.close(fig)


if __name__ == '__main__':
    main()
