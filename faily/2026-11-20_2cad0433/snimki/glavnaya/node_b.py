"""Stage 2, node B (spec §5.2): the cycle -- the cycle shaft driven by the spring motor through the governor, the cams
and their roller followers, the selection trees, the shuttle's turn (tape on the pulley) and lift (fork under the
collar; the shuttle lies on the collar), the detents.

Reduced Lagrange model (spec §5.1): one coordinate, the cycle shaft angle phi; every chain follows its cam while the
roller stays on it, so its inertia is reflected through ds/dphi. Along the way the contact force of every one-sided
link is computed:
  * roller on cam: N = F_ret + m_eff (s'' w^2 + s' w') must stay >= 0 (F_ret: what keeps the roller down -- the
    springs and the weights of the chain, reflected to the roller);
  * shuttle on collar (lift): the collar's downward acceleration must not exceed g;
  * rotate tape (pulls only): the tape's tension must stay >= 0 unless the tape is a closed loop.
Where a link would open, the free motion that follows is integrated (the overshoot of the shuttle, the time it lands
again) for the fastest cycles.
Validation (spec §5.5): motor.py's own simulate() on the same characters within 2 %.
Usage: python3 -I tools/physics/node_b.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.integrate import solve_ivp
import params as P

MJ = json.load(open(os.path.join(U.ROOT, 'gen', 'motor.json')))
LJ = json.load(open(os.path.join(U.ROOT, 'gen', 'links.json')))
MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
S_STROKE = 12e-3                     # follower stroke of the rotate and lift cams (parts.CAM_LIFT)
C = P.CYCLE


def cyc(t):
    t = min(max(t, 0.0), 1.0); return t - math.sin(2 * math.pi * t) / (2 * math.pi)


def out_shape(phi):
    """s (0..1), ds/dphi, d2s/dphi2 (per rad) of the 'out' profile (motor.shape and parts.cam_lift('out'))."""
    a0, a1 = C['out']; b0, b1 = C['back']
    if a0 <= phi < a1:
        F = math.radians(a1 - a0); t = (phi - a0) / (a1 - a0)
        return cyc(t), (1 - math.cos(2 * math.pi * t)) / F, 2 * math.pi * math.sin(2 * math.pi * t) / F ** 2
    if a1 <= phi < b0:
        return 1.0, 0.0, 0.0
    if b0 <= phi < b1:
        F = math.radians(b1 - b0); t = (phi - b0) / (b1 - b0)
        return 1 - cyc(t), -(1 - math.cos(2 * math.pi * t)) / F, -2 * math.pi * math.sin(2 * math.pi * t) / F ** 2
    return 0.0, 0.0, 0.0


def chain_masses():
    """Reflected masses of the rotate and lift chains at the follower, per unit target (rad of shuttle turn and m of
    lift per m of follower travel come from the target)."""
    I_rot = MJ['I_rot'] * 1e-6
    m_lift = MJ['m_lift'] * 1e-3
    # the trees' own moving parts ride with ratio ~ 1 to the follower (bit sliders, levers, bail, rod): their masses
    def mg(names):
        return sum(MASS[n]['m'] for n in names if n in MASS)
    rot_own = mg(['cam rod rotate', 'rotate drive bellcrank', 'rotate drive link', 'rotate drive bail', 'rotate amplifier',
                  'rotate fulcrum slide', 'tape slider MGN7H', 'tape clamp'] + [f'rotate bit slider r{k}' for k in (1, 2, 4, 8)] +
                 [f'rotate latch pin r{k}' for k in (1, 2, 4, 8)] + [f'rotate summing lever {k}' for k in (1, 2, 3)] +
                 [f'rotate node slider {k}' for k in (1, 2, 3)])
    lift_own = mg(['cam rod lift', 'lift drive bellcrank', 'lift drive bail', 'lift amplifier', 'lift fulcrum slide', 'lift output slider',
                   'lift output pin', 'lift bellcrank', 'lift push rod', 'lift fork', 'lift collar'] + [f'lift bit slider l{k}' for k in (1, 2, 4)] +
                  [f'lift latch pin l{k}' for k in (1, 2, 4)] + [f'lift summing lever {k}' for k in (1, 2)] + ['lift node slider 2'])
    return I_rot, m_lift, rot_own, lift_own


def target(pos, row):
    th = abs(pos - (P.NPOS - 1) / 2) * P.STEP
    dz = (row - P.REST_ROW) * P.RH * U.MM
    return th, dz


def cycle(tau, cg, th, dz, I_rot, m_lift, J0=4.0e-5, eta=0.8, fric=0.0012, hammer=None, er=(0.0, 0.0), shuttle_follows=True):
    """Integrate one revolution (phi from 0 to 360 deg) as motor.simulate does, but with the explicit cam derivatives;
    returns (t, phi, w, wdot) arrays. hammer: (phi_deg, torque) table for the cocking (node C) or None (motor.py's
    uniform 20 mJ over 0..150 deg)."""
    import motor as MO
    Jsh = I_rot * (th / S_STROKE) ** 2 * S_STROKE ** 2 + m_lift * dz ** 2     # = I th^2 + m dz^2 (per unit s'^2)
    E = 1e-12; t = 0.0; phi = 0.0; dphi = 0.1
    out = []
    s0, d0, _ = out_shape(0.0)
    while phi < 360.0:
        s, d, dd = out_shape(phi)
        J = J0 + Jsh * d * d
        w = math.sqrt(2 * E / J)
        drive = tau - cg * w * w - fric
        if hammer is None:
            if phi < C['strike'] - 10.0:
                drive -= MO.E_HAMMER / math.radians(C['strike'] - 10.0)
        else:
            drive -= float(np.interp(phi, hammer[:, 0], hammer[:, 1], left=0.0, right=0.0))
        if er[0] and MO.READ_OUT[0] <= phi < MO.READ_OUT[1]:
            u = (phi - MO.READ_OUT[0]) / (MO.READ_OUT[1] - MO.READ_OUT[0])
            drive += er[0] / math.radians(MO.READ_OUT[1] - MO.READ_OUT[0]) * (1 - math.cos(2 * math.pi * u))
        if er[1] and MO.READ_WIN[0] <= phi < MO.READ_WIN[1]:
            u = (phi - MO.READ_WIN[0]) / (MO.READ_WIN[1] - MO.READ_WIN[0])
            drive -= er[1] / math.radians(MO.READ_WIN[1] - MO.READ_WIN[0]) * (1 - math.cos(2 * math.pi * u))
        # Lagrange: d/dt (J w) - 1/2 dJ/dphi w^2 = drive  ->  J w' = drive - 1/2 dJ/dphi w^2 ; losses (1 - eta) on the shuttle's
        # kinetic energy transfers as motor.py
        s1, d1, _ = out_shape(phi + dphi)
        J1 = J0 + Jsh * d1 * d1
        dE = drive * math.radians(dphi)
        dK = 0.5 * Jsh * (d1 ** 2 - d ** 2) * w * w
        dE -= (1 - eta) * abs(dK)
        wdot = (drive - 0.5 * (J1 - J) / math.radians(dphi) * w * w) / J
        out.append((t, phi, w, wdot))
        E = max(E + dE, 1e-12)
        w1 = math.sqrt(2 * E / J1)
        t += math.radians(dphi) / max(0.5 * (w + w1), 1e-3)
        phi += dphi
        if t > 5:
            break
    return np.array(out)


def contact_forces(tr, th, dz, I_rot, m_lift, rot_own, lift_own, F_ret_rot, F_ret_lift):
    """Follower forces along the revolution. Returns dict of minima and where they occur, the collar test and the tape."""
    res = {}
    t, phi, w, wd = tr.T
    S = S_STROKE
    k_rot = th / S                 # rad of shuttle per m of follower
    k_lift = dz / S                # m of lift per m of follower
    m_rot = I_rot * k_rot ** 2 + rot_own
    m_lft = m_lift * k_lift ** 2 + lift_own
    Nr, Nl, acc_z, tape = [], [], [], []
    for p, ww, wwd in zip(phi, w, wd):
        s, d, dd = out_shape(p)
        a_f = S * (dd * ww * ww + d * wwd)        # follower acceleration (m/s2), + up
        Nr.append(F_ret_rot + m_rot * a_f)        # cam pushes up with N; the return force pushes down
        Nl.append(F_ret_lift + m_lift * U.G * k_lift + m_lft * a_f)
        acc_z.append(k_lift * a_f)                # collar acceleration
        tape.append(I_rot * k_rot * a_f / (P.PULLEY_R * U.MM))   # tape tension needed (N), sign: + pulls toward the target
    Nr, Nl, acc_z, tape = map(np.array, (Nr, Nl, acc_z, tape))
    res['N_rot_min'] = float(Nr.min()); res['N_rot_min_deg'] = float(phi[np.argmin(Nr)])
    res['N_lift_min'] = float(Nl.min()); res['N_lift_min_deg'] = float(phi[np.argmin(Nl)])
    res['collar_acc_min'] = float(acc_z.min()); res['collar_acc_min_deg'] = float(phi[np.argmin(acc_z)])
    sep = phi[acc_z < -U.G]
    res['collar_separates'] = [float(sep.min()), float(sep.max())] if len(sep) else None
    res['tape_min_N'] = float(tape.min()); res['tape_min_deg'] = float(phi[np.argmin(tape)])
    res['F_ret_rot_needed'] = float(max(0.0, -(Nr - F_ret_rot).min()))
    res['F_ret_lift_needed'] = float(max(0.0, -(Nl - F_ret_lift).min()))
    res['m_rot'] = m_rot; res['m_lift_eff'] = m_lft
    return res, (phi, Nr, Nl, acc_z, tape)


def shuttle_flight(tr, dz):
    """The shuttle leaves the collar when the collar decelerates faster than g (end of the lift, start of the drop):
    its free flight and the angle where it lands on the collar again; overshoot over the target row."""
    t, phi, w, wd = tr.T
    k = dz / S_STROKE
    z = np.array([k * S_STROKE * out_shape(p)[0] for p in phi])
    v = np.array([k * S_STROKE * out_shape(p)[1] * ww for p, ww in zip(phi, w)])
    a = np.array([k * S_STROKE * (out_shape(p)[2] * ww * ww + out_shape(p)[1] * wwd) for p, ww, wwd in zip(phi, w, wd)])
    flights = []
    i = 0
    n = len(t)
    while i < n:
        if a[i] < -U.G and (i == 0 or a[i - 1] >= -U.G):
            t0, z0, v0 = t[i], z[i], v[i]
            j = i + 1
            while j < n:
                zf = z0 + v0 * (t[j] - t0) - 0.5 * U.G * (t[j] - t0) ** 2
                if zf <= z[j]:
                    break
                j += 1
            if j >= n:
                j = n - 1
            tt = np.linspace(t0, t[j], 200)
            zf = z0 + v0 * (tt - t0) - 0.5 * U.G * (tt - t0) ** 2
            zc = np.interp(tt, t, z)
            vland = (v0 - U.G * (t[j] - t0)) - v[j]
            flights.append(dict(leave_deg=float(phi[i]), land_deg=float(phi[j]), gap_max_mm=float((zf - zc).max() * 1e3),
                                over_target_mm=float((zf.max() - dz) * 1e3), v_land=float(vland)))
            i = j
        i += 1
    return flights


def main():
    import motor as MO
    I_rot, m_lift, rot_own, lift_own = chain_masses()
    tau = MJ['tau_C']; cg = (tau - MO.TAU_FRIC) / MO.W_FREE ** 2
    res = dict(I_rot=I_rot, m_lift=m_lift, rot_own_kg=rot_own, lift_own_kg=lift_own, tau=tau, c_gov=cg)
    # --- validation: motor.simulate vs this integration on the same characters
    val = []
    for pos, row, lab in ((0, 7, 'дальняя'), (2, 3, 'средняя'), (5, -1, 'без хода')):
        th, dz = target(pos, row)
        t_mo = MO.simulate(tau, cg, th, dz)[0]
        tr = cycle(tau, cg, th, dz, I_rot, m_lift)
        val.append(dict(target=lab, pos=pos, row=row, t_motor=t_mo, t_here=float(tr[-1, 0]), diff_pct=100 * (tr[-1, 0] / t_mo - 1)))
    res['validation'] = val
    # --- full: the cocking torque from node C, the read work, the worst and the light characters
    nc = json.load(open(os.path.join(U.GEN, 'node_c.json')))
    ham = np.array(nc['cam_cocking']['curve'])
    rows = []
    F_ret_rot = 4 * LJ['selection']['forces']['F_return'] + MASS['cam rod rotate']['m'] * U.G     # slider springs + rod weight
    F_ret_lift = 3 * LJ['selection']['forces']['F_return'] + MASS['cam rod lift']['m'] * U.G
    res['F_ret_known'] = dict(rot=F_ret_rot, lift=F_ret_lift,
                              note='возврат толкателя: пружины ползунов разрядов 0,4 Н × 4 (3) и вес толкателя; приведение 1:1 (допущение)')
    curves = {}
    for pos, row, lab in ((0, 7, 'дальняя (0, 7)'), (10, 7, 'дальняя (10, 7)'), (0, 0, 'поворот (0, 0)'), (5, 7, 'подъём (5, 7)'),
                          (3, 2, 'средняя (3, 2)'), (5, 0, 'пробел (5, 0)')):
        th, dz = target(pos, row)
        for sp, tau_ in (('номинал', tau), ('регулятор без нагрузки', tau)):
            if sp != 'номинал':
                continue
            tr = cycle(tau_, cg, th, dz, I_rot, m_lift, hammer=ham)
            cf, cur = contact_forces(tr, th, dz, I_rot, m_lift, rot_own, lift_own, F_ret_rot, F_ret_lift)
            fl = shuttle_flight(tr, dz)
            rows.append(dict(target=lab, pos=pos, row=row, t_cycle=float(tr[-1, 0]), w_max=float(tr[:, 2].max()), **cf, flights=fl))
            curves[lab] = (tr, cur)
    res['cases'] = rows
    # --- the light cycle speed bound: the governor's free speed (0.18 s) is the fastest the shaft runs
    w_free = MO.W_FREE
    fast = []
    for pos, row, lab in ((0, 7, 'дальняя (0, 7)'), (5, 7, 'подъём (5, 7)'), (0, 0, 'поворот (0, 0)')):
        th, dz = target(pos, row)
        a_rot = I_rot * (th / S_STROKE) ** 2 + rot_own
        a_lft = m_lift * (dz / S_STROKE) ** 2 + lift_own
        dd_max = 2 * math.pi / math.radians(C['out'][1] - C['out'][0]) ** 2
        need_rot = a_rot * S_STROKE * dd_max * w_free ** 2
        need_lift = a_lft * S_STROKE * dd_max * w_free ** 2 - m_lift * U.G * dz / S_STROKE
        fast.append(dict(target=lab, F_ret_rot_needed=need_rot, F_ret_lift_needed=max(0.0, need_lift),
                         collar_acc=dz * dd_max * w_free ** 2))
    res['at_governor_speed'] = fast
    # --- cost of a return spring on the follower: its peak torque on the cycle shaft at s' max
    dmax = 2 / math.radians(C['out'][1] - C['out'][0])
    res['spring_cost'] = [dict(F=F, peak_mNm=F * S_STROKE * dmax * 1e3) for F in (5, 10, 20, 40, 80)]
    # --- cycle time compared with motor.py (criterion: within 15 %)
    res['cycle_vs_motor'] = [dict(target=r['target'], t=r['t_cycle']) for r in rows]
    json.dump(res, open(os.path.join(U.GEN, 'node_b.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    plot(curves)
    for v in val:
        print('validation', v)
    for r in rows:
        print(r['target'], 't', round(r['t_cycle'], 3), 'Nrot min', round(r['N_rot_min'], 2), '@', r['N_rot_min_deg'], 'Nlift min', round(r['N_lift_min'], 2),
              '@', r['N_lift_min_deg'], 'collar sep', r['collar_separates'], 'tape min', round(r['tape_min_N'], 2), 'need rot/lift',
              round(r['F_ret_rot_needed'], 1), round(r['F_ret_lift_needed'], 1), 'flights', r['flights'][:2])
    print('governor speed', fast)
    print('spring cost', res['spring_cost'])


def plot(curves):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(8.5, 8), sharex=True)
    cols = ['#c44536', '#2a6f97', '#7a7a7a', '#e0a030', '#3a8a50', '#8050a0']
    for (lab, (tr, cur)), col in zip(curves.items(), cols):
        phi, Nr, Nl, acc, tape = cur
        ax[0].plot(phi, Nr, color=col, lw=1, label=lab)
        ax[1].plot(phi, Nl, color=col, lw=1)
        ax[2].plot(phi, acc, color=col, lw=1)
    ax[2].axhline(-U.G, color='k', ls='--', lw=0.8)
    for x in ax:
        x.axhline(0, color='k', lw=0.5)
        for a_ in (10, 120, 160, 200, 310):
            x.axvline(a_, color='k', lw=0.4, ls=':')
    ax[0].set_ylabel('ролик поворота, Н'); ax[1].set_ylabel('ролик подъёма, Н'); ax[2].set_ylabel('ускорение кольца, м/с²')
    ax[2].set_xlabel('угол циклового вала, °'); ax[0].legend(fontsize=7, ncol=2)
    ax[0].set_title('Узел B: сила ролика на кулачке (< 0 — отрыв) и ускорение кольца подъёма (< −g — челнок отрывается)')
    fig.tight_layout(); fig.savefig(os.path.join(U.GEN, 'node_b_contacts.png'), dpi=130); plt.close(fig)


if __name__ == '__main__':
    main()
