"""Stage 2, node D (spec §5.2): the escapement and the carriage. The carriage (mass of group 'carriage' + the sheet, the
wheel's inertia reflected through the pinion z = 10, r = 5.053 mm) is pulled by its spring motor (force F: there is
no number in the project -- spring 'carriage drive spring' is 'missing'); the holding dog D is drawn out at 310 deg
(params.CYCLE feed), the wheel turns w teeth until a face meets U's finger (an elastic contact: stiffness of a printed
tooth, restitution e); then D drops in under its 0.3 N spring. Reduced 1-DOF model with events (solve_ivp).
Outputs: feed time for every width, the impact on U's finger (speed, force, energy), the rebound in teeth while D
falls, the smallest F that finishes the feed by 340 deg (10 deg before U is drawn out at 350), the margin stop and the
release. Validation (spec §5.5): the slow kinematic feed is exactly w units (escape.py, params.U).
Usage: python3 -I tools/physics/node_d.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.integrate import solve_ivp
import params as P
import escape as E

MASS = {x['name']: x for x in json.load(open(os.path.join(U.GEN, 'mass.json')))['parts']}
PARTS = {p['name']: p for p in json.load(open(os.path.join(U.GEN, 'parts.json')))}
MJ = json.load(open(os.path.join(U.ROOT, 'gen', 'motor.json')))
R_P = 5.053e-3                        # pinion pitch radius (z = 10, m = 1.0106)
R_T = (E.R_ROOT + E.R_TIP) / 2 * U.MM   # where U's finger meets the face
UNIT = P.U * U.MM
DEG_T = {'free': 0.18 / 360, 'light': MJ['pick']['light'] / 360, 'avg': MJ['pick']['avg'] / 360, 'worst': MJ['pick']['worst'] / 360}
DOG_M = MASS['escapement dog']['m']; DOG_F = 0.3; DOG_TRAVEL = 2.5e-3      # teeth 2.5 mm deep
TOOTH_W = 5e-3                         # finger in one tier of the wheel (5 mm)


def masses(f_print=None, roller='solid'):
    """Carriage mass (kg) by its parts; f_print rescales printed parts; roller 'solid' (model) or 'tube' (hollow steel
    tube 14 x 1 with a 2 mm rubber skin)."""
    m = 0.0
    for n, p in PARTS.items():
        if p['group'] != 'carriage':
            continue
        mi = MASS[n]['m']
        if f_print is not None and p['kind'] == 'print':
            mi = mi / max(MASS[n]['f'], 1e-9) * f_print
        if n == 'feed roller' and roller == 'tube':
            L = 0.23; mi = 7850 * math.pi * (0.005 ** 2 - 0.004 ** 2) * L + 1200 * math.pi * (0.007 ** 2 - 0.005 ** 2) * L
        m += mi
    m += MASS['paper']['m']
    Iw = np.array(MASS['escapement wheel and pinion']['I'])[2, 2]
    return m, Iw / R_P ** 2


def feed(F, w, m, mw, mu=0.005, k=1.5e6, e=0.5, deg_t=DEG_T['avg'], drag=0.1, t_max=0.2):
    """One feed of w units from rest. k: stiffness at the tooth (N/m); returns dict."""
    M = m + mw
    d = w * UNIT
    m_t = M * (R_P / R_T) ** 2                      # reflected to the tooth radius
    k_x = k * (R_T / R_P) ** 2 * (R_P / R_T) ** 2   # the same spring seen at the rack: k (R_T/R_P)^-2 x (R_T/R_P)^2 = k
    # contact at the rack coordinate: force at the tooth Ft = k * delta_t, delta_t = delta_x * R_T / R_P
    kx = k * (R_T / R_P) ** 2
    ln = math.log(e); z = -ln / math.sqrt(math.pi ** 2 + ln ** 2); c = 2 * z * math.sqrt(kx * M)
    fr = mu * m * U.G + drag                         # bushings + dog and finger drag
    def rhs(t, y):
        x, v = y
        a = F - math.copysign(fr, v) if abs(v) > 1e-6 else max(0.0, F - fr)
        pen = x - d
        if pen > 0:
            a -= max(0.0, kx * pen + c * v)
        return [v, a / M]
    def hit(t, y): return y[0] - d
    hit.terminal = True; hit.direction = 1
    s = solve_ivp(rhs, (0, t_max), [0.0, 0.0], method='LSODA', events=hit, rtol=1e-9, atol=1e-12, max_step=1e-4)
    if not len(s.t_events[0]):
        return dict(ok=False)
    t1 = float(s.t_events[0][0]); v1 = float(s.y_events[0][0][1])
    def out_(t, y): return y[0] - d
    out_.terminal = True; out_.direction = -1
    tc = math.pi * math.sqrt(M / kx)
    s2 = solve_ivp(rhs, (t1, t1 + 40 * tc), [d + 1e-12, v1], method='Radau', events=out_, rtol=1e-9, atol=1e-14, max_step=tc / 100,
                   dense_output=True)
    t2 = float(s2.t_events[0][0]) if len(s2.t_events[0]) else float(s2.t[-1])
    tt = np.linspace(t1, t2, 300); Y = s2.sol(tt)
    pen = Y[0] - d; Fx = np.maximum(0, kx * pen + c * Y[1])
    Ft = Fx * R_P / R_T
    v2 = float(s2.y[1, -1])
    # rebound: free motion back against F until it stops (then F brings it in again)
    reb = (v2 ** 2) / (2 * (F + fr) / M) if v2 < 0 else 0.0
    t_dog = math.sqrt(2 * DOG_TRAVEL * DOG_M / max(DOG_F - 0.35 * 0.0, 1e-9))
    pen_max = float(pen.max())
    return dict(ok=True, w=w, t_feed_ms=t1 * 1e3, v_hit=v1, E_hit_mJ=0.5 * M * v1 ** 2 * 1e3, F_tooth_N=float(Ft.max()),
                contact_ms=(t2 - t1) * 1e3, pen_tooth_um=pen_max * R_T / R_P * 1e6, rebound_mm=reb * 1e3, rebound_teeth=reb / UNIT,
                t_dog_ms=t_dog * 1e3, deg=(t1 + (t2 - t1)) / deg_t, end_deg=310 + (t1 + (t2 - t1) + t_dog) / deg_t,
                sigma_MPa=float(Ft.max()) / (TOOTH_W * 1e-3) / 1e6)


def f_min(w, m, mw, deg_t, end=340.0, **kw):
    lo, hi = 0.05, 200.0
    for _ in range(50):
        mid = math.sqrt(lo * hi)
        r = feed(mid, w, m, mw, deg_t=deg_t, **kw)
        if r['ok'] and r['end_deg'] <= end:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    res = {}
    m, mw = masses()
    res['mass'] = dict(carriage_kg=m, wheel_reflected_kg=mw, total=m + mw,
                       parts={n: MASS[n]['m'] for n, p in PARTS.items() if p['group'] == 'carriage'},
                       hollow_roller_kg=masses(roller='tube')[0], f035_kg=masses(0.35)[0], f1_kg=masses(1.0)[0])
    # validation: the slow kinematic feed = w units, teeth of 6 deg (escape.py) and the rack's pitch
    res['validation'] = dict(unit_mm=P.U, rack_per_tooth_mm=2 * math.pi * R_P / E.TEETH * 1e3, deg_per_unit=E.PITCH,
                             err_um=(2 * math.pi * R_P / E.TEETH - UNIT) * 1e6)
    # smallest spring force by width and speed of the cycle
    tab = []
    for w in (4, 8, 12, 16, 17):
        row = dict(w=w)
        for sp in ('worst', 'avg', 'light', 'free'):
            row[f'Fmin_{sp}'] = round(f_min(w, m, mw, DEG_T[sp]), 2)
        tab.append(row)
    res['f_min'] = tab
    Freq = max(r['Fmin_light'] for r in tab)
    res['F_required_light'] = Freq
    res['F_required_avg'] = max(r['Fmin_avg'] for r in tab)
    # behaviour at the required force (light cycle) for every width, nominal contact
    rows = []
    for w in range(4, 18):
        r = feed(Freq, w, m, mw, deg_t=DEG_T['light'])
        rows.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    res['at_required'] = rows
    # sensitivity at the required force, w = 17
    sl = {}
    for key, vals in dict(mu=(0.002, 0.005, 0.01), k=(0.5e6, 1.5e6, 5e6), e=(0.3, 0.5, 0.7), drag=(0.05, 0.1, 0.3)).items():
        sl[key] = []
        for v in vals:
            r = feed(Freq, 17, m, mw, deg_t=DEG_T['light'], **{key: v})
            sl[key].append(dict(value=v, end_deg=round(r['end_deg'], 1), F_tooth=round(r['F_tooth_N'], 1), rebound_teeth=round(r['rebound_teeth'], 3)))
    sl['mass'] = []
    for lab, (mm, mmw) in (('f 0.35', masses(0.35)), ('f 1', masses(1.0)), ('полый валик', masses(roller='tube'))):
        r = feed(Freq, 17, mm, mmw, deg_t=DEG_T['light'])
        sl['mass'].append(dict(value=lab, m=round(mm, 3), end_deg=round(r['end_deg'], 1), F_tooth=round(r['F_tooth_N'], 1)))
    res['slices'] = sl
    # Latin hypercube at the required force
    rng = np.random.default_rng(2); lh = []
    for _ in range(200):
        u = rng.random(6)
        mu = 0.002 + 0.008 * u[0]; k = 10 ** (math.log10(0.5e6) + u[1] * math.log10(10)); e = 0.3 + 0.4 * u[2]; dr = 0.05 + 0.25 * u[3]
        mm, mmw = masses(0.35 + 0.65 * u[4]); w = 4 + int(u[5] * 14)
        r = feed(Freq, w, mm, mmw, mu=mu, k=k, e=e, drag=dr, deg_t=DEG_T['light'])
        lh.append(dict(w=w, mu=mu, k=k, e=e, drag=dr, m=mm, end_deg=r['end_deg'], rebound_teeth=r['rebound_teeth'], F_tooth=r['F_tooth_N']))
    res['lhs'] = dict(n=200, late=sum(x['end_deg'] > 340 for x in lh), skip_tooth=sum(x['rebound_teeth'] >= 0.5 for x in lh),
                      F_tooth_max=max(x['F_tooth'] for x in lh), end_max=max(x['end_deg'] for x in lh))
    # with a lighter carriage (hollow roller) and with a feed window that starts at 200 deg (after the blow)
    mh, mwh = masses(roller='tube')
    res['options'] = dict(
        hollow_roller=dict(m=mh, F_light=max(f_min(w, mh, mwh, DEG_T['light']) for w in (4, 17)),
                           E_hit_mJ=feed(max(f_min(w, mh, mwh, DEG_T['light']) for w in (4, 17)), 17, mh, mwh, deg_t=DEG_T['light'])['E_hit_mJ']),
        window_200=dict(F_light=max(f_min(w, m, mw, DEG_T['light'], end=340.0 + 110) for w in (4, 17))))
    # the margin stop at the end of the line: the carriage meets the abutment after its last feed (same energy as a feed
    # of w units into a stop instead of U's finger) -- the energy and the force on the stop
    r = feed(Freq, 17, m, mw, deg_t=DEG_T['light'], k=3e6)
    res['margin_stop'] = dict(E_mJ=r['E_hit_mJ'], F_N=r['F_tooth_N'] * R_T / R_P)
    # release: the carriage pushed by hand and let go between teeth: D (0.3 N) drops in while the carriage moves under F;
    # it catches when the wheel turns less than one tooth while D falls 2.5 mm
    t_dog = math.sqrt(2 * DOG_TRAVEL * DOG_M / DOG_F)
    s_dog = 0.5 * Freq / (m + mw) * t_dog ** 2
    res['release'] = dict(t_dog_ms=t_dog * 1e3, carriage_moves_mm=s_dog * 1e3, teeth=s_dog / UNIT,
                          whole_tooth=s_dog / UNIT < 1.0)
    # the carriage spring's work per line (hand return) and per character
    res['energy'] = dict(per_unit_mJ=Freq * UNIT * 1e3, per_line_J=Freq * P.LINE_LEN * U.MM, hand_force_N=Freq)
    json.dump(res, open(os.path.join(U.GEN, 'node_d.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    plot(res, m, mw)
    print('mass', res['mass']['total'], 'validation', res['validation'])
    print('Fmin', tab)
    print('at required (light):', [(r['w'], round(r['t_feed_ms'], 1), round(r['end_deg'], 1), round(r['F_tooth_N'], 0), round(r['E_hit_mJ'], 1), round(r['rebound_teeth'], 2)) for r in rows])
    print('lhs', res['lhs']); print('options', res['options']); print('release', res['release']); print('energy', res['energy'])


def plot(res, m, mw):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    w = [r['w'] for r in res['f_min']]
    for sp, col in (('worst', '#7a7a7a'), ('avg', '#2a6f97'), ('light', '#c44536'), ('free', '#e0a030')):
        ax[0].plot(w, [r[f'Fmin_{sp}'] for r in res['f_min']], 'o-', color=col, label=sp)
    ax[0].set_xlabel('ширина литеры w, u'); ax[0].set_ylabel('наименьшая сила пружины каретки, Н'); ax[0].legend(fontsize=8)
    ax[0].set_title('Подача успевает к 340°')
    rows = res['at_required']
    ax[1].plot([r['w'] for r in rows], [r['F_tooth_N'] for r in rows], 's-', color='#c44536', label='сила на зуб, Н')
    ax2 = ax[1].twinx(); ax2.plot([r['w'] for r in rows], [r['E_hit_mJ'] for r in rows], 'o--', color='#2a6f97', label='энергия, мДж')
    ax[1].set_xlabel('w, u'); ax[1].set_ylabel('сила на палец U, Н'); ax2.set_ylabel('энергия удара, мДж')
    ax[1].set_title(f"Удар о палец U при F = {res['F_required_light']:.1f} Н")
    fig.tight_layout(); fig.savefig(os.path.join(U.GEN, 'node_d_feed.png'), dpi=130); plt.close(fig)


if __name__ == '__main__':
    main()
