"""Stage 2, node C (spec §5.2): the hammer. One rotational degree of freedom about the hammer axle (axis X through
params.HAMMER_PIVOT), integrated with events (solve_ivp, Radau):
  throw  -- the torsion spring (links.json hammer: k_t, mean torque over 18 deg, half of it preload) drives the hammer
            from its rest angle (-18 deg) until its arm meets the spring's stop FREE mm before the sheet;
  flight -- free, gravity and axle friction only;
  blow   -- the face on the sheet + ribbon + type: a Kelvin-Voigt layer, stiffness from the contact time t_c and the
            damping from the restitution e;
  after  -- rebound and free motion; the rest stop at -18 deg is a second layer with restitution e_back.
The cycle angle runs at a constant speed (node B gives the real speed): the release is at 160 deg, the deadline for the
hammer to be back at 200 deg ('back' of params.CYCLE).
Validation (spec §5.5): with links.py's own assumptions (constant torque, no gravity, no friction, I from links.json)
the impact speed and flight time must agree within 3 %. MuJoCo cross-checks the blow (speed in -> speed out, duration).
Usage: python3 -I tools/physics/node_c.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.integrate import solve_ivp
import params as P

LJ = json.load(open(os.path.join(U.ROOT, 'gen', 'links.json')))['hammer']
MJ = json.load(open(os.path.join(U.ROOT, 'gen', 'motor.json')))
MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
YP, ZP_ = P.HAMMER_PIVOT
SWING = math.radians(LJ['swing_deg'])
R_HEAD = LJ['r_head_mm'] * U.MM
FREE = 0.5e-3                       # m: the last free flight of the face before the sheet (spring arm on its stop)
R_AXLE = 2.0e-3                     # 4 mm axle
T_MEAN = LJ['T_mean_Nmm'] * 1e-3
K_T = LJ['k_t_Nmm_per_deg'] * 1e-3 * 180 / math.pi       # N m / rad
T_END = T_MEAN - K_T * SWING / 2                        # torque at the sheet (preload)
DEG_T = {'avg': MJ['pick']['avg'] / 360.0, 'light': MJ['pick']['light'] / 360.0, 'worst': MJ['pick']['worst'] / 360.0}


def hammer_props(f=1.0):
    h = MASS['hammer']
    m = h['m'] * f
    c = np.array(h['c'])                     # at rest (retracted 18 deg)
    d2 = (c[1] - YP * U.MM) ** 2 + (c[2] - ZP_ * U.MM) ** 2
    I = (np.array(h['I'])[0, 0] * f + m * d2) + 2e-7          # + rubber pad and spring end (as links.py)
    rc = c[1:] - np.array([YP, ZP_]) * U.MM                    # (y, z) of the centre from the pivot, at rest
    return m, I, rc


def gravity_torque(theta, m, rc, g=(0, 0, -U.G)):
    """Torque about +X of the weight; theta from rest (positive toward the sheet: rotx +)."""
    c, s = math.cos(theta), math.sin(theta)
    y = rc[0] * c - rc[1] * s; z = rc[0] * s + rc[1] * c
    return y * m * g[2] - z * m * g[1]


def simulate(I, m=0.0, rc=(0.0, 0.0), torque='linear', grav=True, mu=0.0, t_c=0.3e-3, e=0.3, e_back=0.5, deg_t=None,
             t_end=None, free=FREE, back_hold=0.0, rtol=1e-8):
    """Returns dict of outputs. Angles: 0 = rest (retracted), SWING = face on the sheet."""
    meff = I / R_HEAD ** 2
    def layer(e_):
        k = meff * (math.pi / t_c) ** 2
        ln = math.log(max(e_, 1e-6)); z = -ln / math.sqrt(math.pi ** 2 + ln ** 2)
        return k, 2 * z * math.sqrt(k * meff)
    k_s, c_s = layer(e)
    k_b, c_b = layer(e_back)
    th_free = SWING - free / R_HEAD
    deg_t = deg_t or DEG_T['avg']
    t_end = t_end or 40.0 * deg_t                          # 160 -> 200 deg
    def spring(th, phase):
        if phase != 0 or th >= th_free:
            return 0.0
        if torque == 'const':
            return T_MEAN
        return T_END + K_T * (SWING - th)
    def rhs_factory(phase):
        def f(t, y):
            th, w = y
            T = spring(th, phase)
            if grav:
                T += gravity_torque(th, m, rc)
            if back_hold:
                T -= back_hold                              # a light return torque toward rest (requirement study)
            pen = R_HEAD * (th - SWING)
            if pen > 0:
                T -= R_HEAD * max(0.0, k_s * pen + c_s * R_HEAD * w)
            pb = -R_HEAD * th
            if pb > 0:
                T += R_HEAD * max(0.0, k_b * pb - c_b * R_HEAD * w)
            if mu:
                N = m * math.hypot(w * w * math.hypot(*rc), U.G) + abs(T) / 0.01 * 0.0
                T -= math.copysign(mu * N * R_AXLE, w) if abs(w) > 1e-6 else 0.0
            return [w, T / I]
        return f
    # phase 0: throw until th_free; phase 1: everything after
    out = dict(contacts=[], back=[])
    ev_free = lambda t, y: y[0] - th_free; ev_free.terminal = True; ev_free.direction = 1
    s0 = solve_ivp(rhs_factory(0), (0, 0.1), [0.0, 0.0], method='Radau', events=ev_free, rtol=rtol, atol=1e-12, max_step=1e-4)
    t0 = s0.t_events[0][0] if len(s0.t_events[0]) else s0.t[-1]
    y0 = s0.y_events[0][0] if len(s0.t_events[0]) else s0.y[:, -1]
    out['t_throw_ms'] = t0 * 1e3
    ev_in = lambda t, y: y[0] - SWING; ev_in.direction = 1
    ev_out = lambda t, y: y[0] - SWING; ev_out.direction = -1
    ev_bin = lambda t, y: -y[0]; ev_bin.direction = 1
    s1 = solve_ivp(rhs_factory(1), (t0, t_end), y0, method='Radau', events=[ev_in, ev_out, ev_bin], rtol=rtol, atol=1e-12,
                   max_step=2e-6, dense_output=True)
    tin, tout, tb = s1.t_events
    yin = s1.y_events[0]
    if len(tin) == 0:
        out.update(ok=False); return out
    out['v_impact'] = float(yin[0][1] * R_HEAD)
    out['t_flight_ms'] = float(tin[0] * 1e3)
    out['E_impact_mJ'] = float(0.5 * I * yin[0][1] ** 2 * 1e3)
    # contact phase details from the dense solution
    for q, ti in enumerate(tin):
        to = tout[q] if q < len(tout) else t_end
        tt = np.linspace(ti, to, 400)
        Y = s1.sol(tt)
        pen = R_HEAD * (Y[0] - SWING)
        F = np.maximum(0, k_s * pen + c_s * R_HEAD * Y[1])
        out['contacts'].append(dict(t_ms=round(ti * 1e3, 3), v_in=round(float(s1.sol(ti)[1] * R_HEAD), 3),
                                    v_out=round(float(s1.sol(to)[1] * R_HEAD), 3), dur_ms=round((to - ti) * 1e3, 4),
                                    F_max=round(float(F.max()), 2), cycle_deg=round(160 + ti / deg_t, 2)))
    for ti in tb:
        out['back'].append(dict(t_ms=round(ti * 1e3, 2), v_in=round(float(s1.sol(ti)[1] * R_HEAD), 3), cycle_deg=round(160 + ti / deg_t, 2)))
    # rebound: largest retreat after the first contact and when the hammer is last more than 0.1 mm from rest
    if len(tout):
        tt = np.linspace(tout[0], t_end, 4000); Y = s1.sol(tt)
        out['rebound_mm'] = float(R_HEAD * (SWING - Y[0].min()) * 1e3)
        far = np.nonzero(R_HEAD * Y[0] > 0.1e-3)[0]
        out['settled_cycle_deg'] = round(160 + tt[far[-1]] / deg_t, 1) if len(far) and far[-1] < len(tt) - 1 else None
        out['at_200_mm_from_rest'] = float(R_HEAD * Y[0, -1] * 1e3)
    out['second_strike_before_200'] = len(tin) > 1
    out['ok'] = True
    return out


def cam_torque(eta=0.8):
    """Torque of the cocking on the cycle shaft over 10..150 deg (cam 'cock', stroke 6 mm on the arm r_cock)."""
    import parts as PT
    r = LJ['r_cock_mm'] * U.MM
    out = []
    for a in np.arange(10, 160.5, 0.5):
        z = 6e-3 * PT.cam_lift('cock', a)
        dz = 6e-3 * (PT.cam_lift('cock', a + 0.05) - PT.cam_lift('cock', a - 0.05)) / math.radians(0.1)
        th = math.atan2(z, r)
        T = T_END + K_T * th if a < 160 else 0.0          # spring wound by the lever (0 at rest .. 18 deg at 150)
        F = T / r * (1 / math.cos(th) ** 2) if a < 160 else 0.0     # rc tan(phi): the slot
        out.append((float(a), float(F * dz / eta)))
    arr = np.array(out)
    E = float(np.trapezoid(arr[:, 1], np.radians(arr[:, 0])))
    return dict(peak_mNm=float(arr[:, 1].max() * 1e3), at_deg=float(arr[np.argmax(arr[:, 1]), 0]), mean_mNm=float(E / math.radians(140) * 1e3),
                E_mJ=E * 1e3, curve=arr[::10].round(5).tolist())


def mujoco_blow(I, v_in, t_c, e):
    """The blow alone in MuJoCo: a hinge with the hammer's inertia, a sphere at the head radius on a plane
    (solref direct: stiffness and damping per unit effective mass). Returns (v_out, duration)."""
    import mujoco
    meff = I / R_HEAD ** 2
    k = (math.pi / t_c) ** 2
    ln = math.log(e); z = -ln / math.sqrt(math.pi ** 2 + ln ** 2); b = 2 * z * math.sqrt(k)
    xml = f"""<mujoco><option timestep="2e-7" gravity="0 0 0" integrator="RK4" iterations="80"/>
    <worldbody><geom name="sheet" type="plane" pos="0 0 0" size="0.1 0.1 0.01" zaxis="-1 0 0" solref="-{k} -{b}" solimp="0.999 0.9999 0.001" margin="0"/>
    <body name="h" pos="-{R_HEAD} 0 0"><joint name="j" type="hinge" axis="0 0 1" damping="0"/>
    <geom type="sphere" pos="{R_HEAD} 0 0" size="0.0005" mass="1e-9" solref="-{k} -{b}" solimp="0.999 0.9999 0.001"/>
    <inertial pos="0 0 0" mass="{meff}" diaginertia="{I} {I} {I}"/></body></worldbody></mujoco>"""
    mdl = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(mdl)
    d.qpos[0] = -0.0006 / R_HEAD
    d.qvel[0] = v_in / R_HEAD
    t_on = t_off = None; vout = None
    for i in range(int(5e-3 / mdl.opt.timestep)):
        mujoco.mj_step(mdl, d)
        if d.ncon and t_on is None:
            t_on = d.time
        if t_on is not None and not d.ncon and t_off is None:
            t_off = d.time; vout = d.qvel[0] * R_HEAD; break
    return (vout, (t_off - t_on) if t_on and t_off else None)


def lhs(n, k, rng):
    u = (rng.permuted(np.tile(np.arange(n), (k, 1)), axis=1).T + rng.random((n, k))) / n
    return u


def main():
    os.makedirs(U.GEN, exist_ok=True)
    res = {}
    # --- validation with links.py's assumptions
    Il = LJ['I_kgmm2'] * 1e-6
    v1 = simulate(Il, torque='const', grav=False, free=1e-9, e=0.3)
    res['validation'] = dict(links_v=LJ['v_impact'], links_t_ms=LJ['t_flight_ms'], v=v1['v_impact'], t_ms=v1['t_flight_ms'],
                             dv_pct=100 * (v1['v_impact'] / LJ['v_impact'] - 1), dt_pct=100 * (v1['t_flight_ms'] / LJ['t_flight_ms'] - 1))
    v2 = simulate(Il, torque='linear', grav=False, free=1e-9, e=0.3)
    res['validation']['linear_spring'] = dict(v=v2['v_impact'], t_ms=v2['t_flight_ms'],
                                              note='та же энергия, момент пружины линейный (1,5 → 0,5 среднего): полёт короче')
    # --- convergence (rtol) and energy (no damping, no friction, e -> 1)
    a = simulate(Il, torque='linear', grav=False, e=0.3, rtol=1e-8); b = simulate(Il, torque='linear', grav=False, e=0.3, rtol=1e-10)
    res['convergence'] = dict(v=[a['v_impact'], b['v_impact']], F=[a['contacts'][0]['F_max'], b['contacts'][0]['F_max']])
    c = simulate(Il, torque='linear', grav=False, e=0.999, free=1e-9)
    E_sp = (T_END * SWING + 0.5 * K_T * SWING ** 2)
    res['energy'] = dict(E_spring_mJ=E_sp * 1e3, E_impact_mJ=c['E_impact_mJ'], drift_pct=100 * (c['E_impact_mJ'] / (E_sp * 1e3) - 1),
                         v_out_over_in=c['contacts'][0]['v_out'] / c['contacts'][0]['v_in'])
    # --- nominal full physics
    m, I, rc = hammer_props(1.0)
    nom = dict(I=I, m=m, rc=rc, mu=0.25, t_c=0.3e-3, e=0.3, e_back=0.5)
    res['props'] = dict(mass_g=m * 1e3, I_kgmm2=I * 1e6, links_mass_g=LJ['mass_g'], links_I=LJ['I_kgmm2'],
                        gravity_torque_rest_mNm=gravity_torque(0.0, m, rc) * 1e3, gravity_torque_sheet_mNm=gravity_torque(SWING, m, rc) * 1e3,
                        spring_torque_end_mNm=T_END * 1e3, k_t_Nm_rad=K_T)
    for tag, dt in DEG_T.items():
        r = simulate(**nom, deg_t=dt)
        res[f'nominal_{tag}'] = r
    # MuJoCo cross-check of the blow
    r = res['nominal_avg']
    vo, dur = mujoco_blow(I, r['contacts'][0]['v_in'], nom['t_c'], nom['e'])
    res['mujoco_blow'] = dict(v_in=r['contacts'][0]['v_in'], v_out_ode=r['contacts'][0]['v_out'], v_out_mj=vo, dur_ode_ms=r['contacts'][0]['dur_ms'],
                              dur_mj_ms=dur * 1e3 if dur else None)
    # --- one-dimensional slices and Latin hypercube
    grid = dict(f=(0.8, 1.0), mu=(0.15, 0.25, 0.35), t_c=(0.1e-3, 0.3e-3, 0.5e-3), e=(0.1, 0.2, 0.4, 0.7), e_back=(0.3, 0.5, 0.7),
                speed=('light', 'avg', 'worst'))
    sl = {}
    for k_, vals in grid.items():
        rows = []
        for v in vals:
            kw = dict(nom); deg = DEG_T['avg']
            if k_ == 'f':
                kw['m'], kw['I'], kw['rc'] = hammer_props(v)
            elif k_ == 'speed':
                deg = DEG_T[v]
            else:
                kw[k_] = v
            r = simulate(**kw, deg_t=deg)
            rows.append(dict(value=v, v_impact=round(r['v_impact'], 3), F_max=r['contacts'][0]['F_max'], dur_ms=r['contacts'][0]['dur_ms'],
                             n_contacts=len(r['contacts']), second=r['second_strike_before_200'], rebound_mm=round(r.get('rebound_mm', 0), 2),
                             at_200_mm=round(r.get('at_200_mm_from_rest', 0), 2), first_return_deg=r['contacts'][1]['cycle_deg'] if len(r['contacts']) > 1 else None))
        sl[k_] = rows
    res['slices'] = sl
    rng = np.random.default_rng(1)
    X = lhs(200, 6, rng)
    lh = []
    for x in X:
        f = 0.8 + 0.2 * x[0]; mu = 0.15 + 0.2 * x[1]; tc = (0.1 + 0.4 * x[2]) * 1e-3; e = 0.1 + 0.6 * x[3]; eb = 0.3 + 0.4 * x[4]
        deg = DEG_T['light'] + (DEG_T['worst'] - DEG_T['light']) * x[5]
        mm, II, rcc = hammer_props(f)
        r = simulate(II, mm, rcc, mu=mu, t_c=tc, e=e, e_back=eb, deg_t=deg)
        lh.append(dict(f=f, mu=mu, t_c_ms=tc * 1e3, e=e, e_back=eb, deg_ms=deg * 1e3, v=r['v_impact'], F_max=r['contacts'][0]['F_max'],
                       second=r['second_strike_before_200'], n=len(r['contacts'])))
    res['lhs'] = dict(n=len(lh), second_strike=sum(x['second'] for x in lh), v_range=[min(x['v'] for x in lh), max(x['v'] for x in lh)],
                      F_range=[min(x['F_max'] for x in lh), max(x['F_max'] for x in lh)], rows=lh)
    # --- what return torque keeps the hammer off the sheet (requirement): smallest back_hold with no second strike in the LHS corners
    req = []
    for hold in (0.0, 1e-3, 2e-3, 3e-3, 5e-3, 8e-3, 12e-3):
        worst = 0
        for e in (0.1, 0.4, 0.7):
            for eb in (0.3, 0.7):
                for sp in ('light', 'avg'):
                    r = simulate(**dict(nom, e=e, e_back=eb), deg_t=DEG_T[sp], back_hold=hold)
                    worst = max(worst, len(r['contacts']))
        req.append(dict(hold_mNm=hold * 1e3, max_contacts=worst))
    res['return_requirement'] = req
    res['cam_cocking'] = cam_torque()
    # --- the other reading: the spring throws the light cocking lever, whose lip strikes the hammer's tail
    IL = (np.array(MASS['hammer cocking lever']['I'])[0, 0] + MASS['hammer cocking lever']['m'] *
          ((MASS['hammer cocking lever']['c'][1] - YP * U.MM) ** 2 + (MASS['hammer cocking lever']['c'][2] - ZP_ * U.MM) ** 2))
    tr = [(e_, (1 + e_) ** 2 * IL * I / (IL + I) ** 2) for e_ in (0.3, 0.5, 0.7)]
    res['lever_impact_reading'] = dict(I_lever_kgmm2=IL * 1e6, I_hammer_kgmm2=I * 1e6,
                                       energy_share=[dict(e=e_, share=s_, v_hammer=math.sqrt(2 * s_ * 0.02 / I) * R_HEAD) for e_, s_ in tr])
    json.dump(res, open(os.path.join(U.GEN, 'node_c.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    plot(res, nom)
    v = res['validation']
    print(f"validation: v {v['v']:.3f} vs {v['links_v']:.3f} ({v['dv_pct']:+.2f} %), t {v['t_ms']:.3f} vs {v['links_t_ms']:.3f} ms ({v['dt_pct']:+.2f} %)")
    n = res['nominal_avg']
    print('nominal: v', round(n['v_impact'], 3), 'flight', round(n['t_flight_ms'], 2), 'contacts', n['contacts'][:3], 'back', n['back'][:3])
    print('mujoco', res['mujoco_blow'])
    print('LHS second strikes', res['lhs']['second_strike'], '/ 200; F', res['lhs']['F_range'])
    print('return requirement', res['return_requirement'])
    print('cam', {k: v for k, v in res['cam_cocking'].items() if k != 'curve'})
    print('lever reading', res['lever_impact_reading'])


def plot(res, nom):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # angle and contact force over the cycle angle, nominal at the average speed
    I, m, rc = nom['I'], nom['m'], nom['rc']
    deg_t = DEG_T['avg']
    fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    for e, col in ((0.1, '#2a6f97'), (0.3, '#c44536'), (0.7, '#7a7a7a')):
        # re-integrate densely for the picture
        r = simulate(I, m, rc, mu=nom['mu'], t_c=nom['t_c'], e=e, e_back=nom['e_back'], deg_t=deg_t)
        ax[0].plot([160 + c['t_ms'] * 1e-3 / deg_t for c in r['contacts']], [c['F_max'] for c in r['contacts']], 'o', color=col, label=f'e = {e}')
        ax[1].plot([160 + c['t_ms'] * 1e-3 / deg_t for c in r['contacts']], [abs(c['v_in']) for c in r['contacts']], 's-', color=col)
    for a_ in (160, 200):
        for x in ax:
            x.axvline(a_, color='k', lw=0.6, ls=':')
    ax[0].set_ylabel('сила удара, Н'); ax[1].set_ylabel('скорость касания, м/с'); ax[1].set_xlabel('угол циклового вала, °')
    ax[0].legend(fontsize=8); ax[0].set_title('Узел C: касания листа после спуска (160°), средний цикл')
    fig.tight_layout(); fig.savefig(os.path.join(U.GEN, 'node_c_contacts.png'), dpi=130); plt.close(fig)


if __name__ == '__main__':
    main()
