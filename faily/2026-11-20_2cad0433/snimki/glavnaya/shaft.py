"""Stage 2b (spec §5б): the cycle shaft's law of rotation under all the loads of a revolution at once.

One coordinate, the shaft angle phi from the cycle latch (0) to the latch again (360 deg). As motor.simulate and
node_b.cycle, the integration steps the kinetic energy E = 1/2 J(phi) w^2 over the angle (the Lagrange equation
J w' + 1/2 J' w^2 = tau in energy form):

    dE = [tau_m - c_g w^2 - tau_fr - sum tau_i(phi)] dphi - (1 - eta) |dK_transfer|

  * J(phi) = J0 + (I_rot th^2 + m_lift dz^2) s'^2 (the selection, as motor.py) + the trees' own moving parts and the
    pushers of the cocking, the ribbon and the detent, each m (ds/dphi)^2;
  * tau_m = M_spring * eta_train / ratio (motor.py: M_need gives tau_C exactly);
  * c_g = (tau_C - TAU_FRIC) / W_FREE^2, fixed by the governor (a fan: its drag goes with w^2);
  * tau_i: every load by angle, from its force and profile -- the cocking (node C's spring and lever, the rod's
    spring and weight, the hammer's weight on the lip), the ribbon vibrator and the detent (springs and weights),
    the reading (motor.read_work), the return cams' slot friction (node B, from the forces of the previous pass:
    two passes), the rotate tape's idler, and an upper estimate for U, D and W, which the model gives by positions.
    A load the shaft drives costs tau / eta; a spring that drives the shaft back gives tau * eta.
mode='motor' reproduces motor.simulate (uniform 20 mJ cocking over 0..150 deg, no new loads, the same step rule).

Clock: the law (t, phi, w, w') of one revolution; t(phi), phi(t), w(phi), wdot(phi). Clock.uniform(T) is a shaft
turning at a constant speed (stage 2's assumption), for the regression of the nodes.
Usage: python3 -I tools/physics/shaft.py   (prints the validation against motor.simulate)"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import params as P
import node_b as NB

MJ = NB.MJ
LJ = json.load(open(os.path.join(U.ROOT, 'gen', 'links.json')))
MASS = NB.MASS
MO = NB.motor_module()
C = P.CYCLE
RATIO = MJ['ratio']
ETA_TRAIN = MO.ETA_TRAIN
SPR = MJ['spring']
WINDS = {'M_need': MJ['M_need'], 'M_avg': SPR['M_avg'], 'mid': 0.5 * (SPR['M_avg'] + SPR['M_max']), 'M_max': SPR['M_max']}
WIND_LABEL = {'M_need': 'конец завода (M_need)', 'M_avg': 'средний (M_avg)', 'mid': '½(M_avg + M_max)', 'M_max': 'полный (M_max)'}
CG_NOM = (MJ['tau_C'] - MO.TAU_FRIC) / MO.W_FREE ** 2
GRID = np.round(np.arange(0.0, 360.0 + 1e-9, 0.05), 4)      # the load tables' grid (deg)

# ---------------------------------------------------------------- the characters (motor.py's list: 87 + the space)


def characters():
    """[(key, item, pos, row, th, dz, w)] -- th rad, dz m as motor.chars; pos and row of the shuttle's target; w the
    escapement's feed (units)."""
    import data as D
    out = []
    for th, dz, it in MO.chars:
        pos = int(round(th / P.STEP + (P.NPOS - 1) / 2))
        row = int(round(dz / (P.RH * U.MM) + P.REST_ROW))
        w = 6 if it == 'SP' else int(D.ITEMS[it]['w'])
        lab = 'SP' if it == 'SP' else D.ITEMS[it].get('label', str(it))
        out.append(dict(key=('SP' if it == 'SP' else f'{it:X}'), item=it, label=lab, pos=pos, row=row, th=abs(th), dz=abs(dz), w=w,
                        weight=MO.weight(it), idle=(it == 'SP')))
    return out


# ---------------------------------------------------------------- the loads by angle


def _d(f, a, h=0.05):
    return (f(a + h) - f(a - h)) / math.radians(2 * h)


_TAB = {}


def _lever_tables():
    """Cocking lever angle L(phi) (rad from the hammer's home), its derivative per rad of the shaft; the cocking rod's
    lift z(phi) (m) and z'."""
    if 'lever' not in _TAB:
        import parts as PT
        import node_c as NC
        L = np.array([math.radians(PT.ham_lever_deg(PT.cam_lift('cock', a))) for a in GRID])
        z = np.array([PT.CAM_LIFT['hammer'] * U.MM * PT.cam_lift('cock', a) for a in GRID])
        _TAB['lever'] = (L, np.gradient(L, np.radians(GRID)), z, np.gradient(z, np.radians(GRID)), NC)
    return _TAB['lever']


def _profile(kind, stroke_m):
    import parts as PT
    key = ('prof', kind, stroke_m)
    if key not in _TAB:
        s = np.array([stroke_m * PT.cam_lift(kind, a) for a in GRID])
        _TAB[key] = (s, np.gradient(s, np.radians(GRID)))
    return _TAB[key]


def m(names):
    return sum(MASS[n]['m'] for n in names if n in MASS)


M_COCK_ROD = m(['cam rod hammer', 'hammer cocking rod', 'hammer trip link'])
M_RIBBON = m(['cam rod ribbon', 'ribbon vibrator', 'ribbon link']) + 0.5 * MASS['ribbon']['m']      # the ribbon lifts half the stroke
M_DETENT = m(['cam rod detent', 'detent link'])
F_RIBBON = 0.7          # vibrator's return spring (node H, 'calculated'), N
F_DETENT = 0.6 + 0.5    # detent pawl return (node H) + row detent wedge spring (springs.json); an estimate of the chain
S_RIBBON, S_DETENT = 10e-3, 3e-3        # strokes measured on the model (vibrator 10 mm, detent link 3 mm)
UDW = ((190.0, 'палец U входит'), (325.0, 'собачка Д'), (345.0, 'защёлка W'), (350.0, 'палец U выходит'))
UDW_E = {'upper': 0.3 * 3e-3, 'lower': 0.1 * 2e-3, 'none': 0.0}        # J per movement (spring 0.1..0.3 N x travel 2..3 mm)
IDLER = dict(load_N=2 * NB.TAPE_PRELOAD, r_pin=1.5e-3, r_roller=4e-3, mu={'bearing': 0.005, 'bushing': 0.12})


def load_tables(idle=False, udw='upper', idler='bearing'):
    """Loads by angle on GRID: dict of torque arrays (N m, + = the shaft drives the load; the efficiency is applied
    by the integrator) and the reflected masses of the pushers (kg m2 per (rad)^-2: m s'^2)."""
    key = ('loads', idle, udw, idler)
    if key in _TAB:
        return _TAB[key]
    L, dL, z, dz, NC = _lever_tables()
    T0, K, SW = NC.T0_, NC.K_T, NC.SWING
    m_h, I_h, rc_h = NC.hammer_props(1.0)
    th_pin = 0.25e-3 / NC.R_HEAD
    s0 = C['strike']
    theta = np.zeros_like(GRID)
    for i, a in enumerate(GRID):
        if a < s0:
            theta[i] = 0.0
        elif idle:
            theta[i] = min(L[i], th_pin)                 # the hammer lock: the hammer lies on the pin, the spring stays wound
        elif a < s0 + 8.0:
            theta[i] = min(L[i], SW * (a - s0) / 8.0)    # in flight (8 deg, node C)
        else:
            theta[i] = min(L[i], SW)
    riding = L <= theta + 1e-9
    T_spring = np.where(riding, 0.0, T0 + K * (L - theta))
    G = np.array([NC.gravity_torque(th, m_h, rc_h) for th in theta])
    tau_cock = np.where(riding, -G, T_spring) * dL + (LJ['hammer']['rod_return_N'] + M_COCK_ROD * U.G) * dz
    s_r, ds_r = _profile('ribbon', S_RIBBON)
    s_d, ds_d = _profile('detent', S_DETENT)
    tau_rib = (F_RIBBON + M_RIBBON * U.G) * ds_r
    tau_det = (F_DETENT + M_DETENT * U.G) * ds_d
    tau_udw = np.zeros_like(GRID)
    for a1, _ in UDW:
        a0 = a1 - 10.0
        msk = (GRID >= a0) & (GRID < a1)
        u = (GRID[msk] - a0) / 10.0
        tau_udw[msk] += UDW_E[udw] / math.radians(10.0) * (1 - np.cos(2 * math.pi * u))
    lev_I = MASS['hammer cocking lever']
    r_c = LJ['hammer']['r_cock_mm'] * U.MM
    m_cock = M_COCK_ROD + (np.array(lev_I['I'])[0, 0]) / r_c ** 2
    mass_s2 = m_cock * dz ** 2 + M_RIBBON * ds_r ** 2 + M_DETENT * ds_d ** 2
    mu = IDLER['mu'][idler]
    F_idler = mu * IDLER['load_N'] * IDLER['r_pin'] / IDLER['r_roller']        # drag at the tape, N
    out = dict(cock=tau_cock, ribbon=tau_rib, detent=tau_det, udw=tau_udw, mass_s2=mass_s2, F_idler=F_idler, theta=theta, L=L)
    _TAB[key] = out
    return out


# ---------------------------------------------------------------- the integration


class Trace:
    """One revolution: arrays t, phi (deg), w (rad/s), wdot (rad/s2) and the energy book."""

    def __init__(self, t, phi, w, wd, book, stall=None, meta=None):
        self.t, self.phi, self.w, self.wd = map(np.asarray, (t, phi, w, wd))
        self.book = book; self.stall = stall; self.meta = meta or {}

    @property
    def T(self):
        return float(self.t[-1])

    def arr(self):
        return np.column_stack([self.t, self.phi, self.w, self.wd])

    def clock(self):
        return Clock(self.t, self.phi, self.w, self.wd)

    def seg(self, a0, a1):
        return float(np.interp(a1, self.phi, self.t) - np.interp(a0, self.phi, self.t))


def integrate(ch, M=None, tau=None, cg=None, J0=None, eta=0.8, fric=1.0, w0=0.0, dphi=0.1, mode='full', udw='upper',
              idler='bearing', slot=None, motor_step=False):
    """One revolution of the shaft for character ch (dict of characters()). M: spring torque at the barrel (N m) or
    tau: torque at the shaft; cg: governor coefficient; fric: multiplier of TAU_FRIC (and of the known frictions);
    w0: start speed; slot: (phi grid, torque) of the return cams' slot friction from a previous pass."""
    tau_m = tau if tau is not None else (M if M is not None else MJ['M_need']) * ETA_TRAIN / RATIO
    cg = CG_NOM if cg is None else cg
    J0 = MO.J0 if J0 is None else J0
    th, dz = ch['th'], ch['dz']
    Jsh = MO.I_rot * th ** 2 + MO.m_lift * dz ** 2
    full = mode == 'full'
    if full:
        I_rot, m_lift, rot_own, lift_own = NB.chain_masses()
        J_own = (rot_own + lift_own) * NB.S_STROKE ** 2
        LT = load_tables(idle=ch['idle'], udw=udw, idler=idler)
        er = MO.read_work(None if ch['idle'] else ch['item'])
        tape_k = LT['F_idler'] * P.PULLEY_R * U.MM * th * fric
    else:
        J_own = 0.0
        er = MO.read_work(ch['item']) if mode == 'motor' else (0.0, 0.0)
    fr = MO.TAU_FRIC * fric
    hammer_t = math.radians(C['strike'] - 10.0)

    def shape_d(a):
        return MO.shape(a)[1]

    def J_of(a, d):
        J = J0 + (Jsh + J_own) * d * d
        if full:
            J += float(np.interp(a, GRID, LT['mass_s2']))
        return J

    def J_transfer(a, d):
        return J_of(a, d) - J0

    def load(a, w):
        """Torque the shaft supplies at angle a (+), with the efficiencies applied."""
        x = 0.0
        if full:
            for k in ('cock', 'ribbon', 'detent'):
                v = float(np.interp(a, GRID, LT[k]))
                x += v / eta if v > 0 else v * eta
            x += float(np.interp(a, GRID, LT['udw']))
            x += tape_k * abs(shape_d(a)) / eta
            if slot is not None:
                x += float(np.interp(a, slot[0], slot[1])) * fric
        else:
            if a < C['strike'] - 10.0:
                x += MO.E_HAMMER / hammer_t
        if er[0] and MO.READ_OUT[0] <= a < MO.READ_OUT[1]:
            u = (a - MO.READ_OUT[0]) / (MO.READ_OUT[1] - MO.READ_OUT[0])
            x -= er[0] / math.radians(MO.READ_OUT[1] - MO.READ_OUT[0]) * (1 - math.cos(2 * math.pi * u))
        if er[1] and MO.READ_WIN[0] <= a < MO.READ_WIN[1]:
            u = (a - MO.READ_WIN[0]) / (MO.READ_WIN[1] - MO.READ_WIN[0])
            x += er[1] / math.radians(MO.READ_WIN[1] - MO.READ_WIN[0]) * (1 - math.cos(2 * math.pi * u))
        return x

    book = dict(spring=0.0, governor=0.0, friction=0.0, loads=0.0, transfer=0.0)
    phi = 0.0; t = 0.0
    d_prev = shape_d(0.0)
    J_prev = J_of(0.0, d_prev)
    E = max(0.5 * J_prev * w0 * w0, 1e-12)
    rows = []; stall = None
    dr = math.radians(dphi)
    while phi < 360.0 - 1e-9:
        phi1 = min(phi + dphi, 360.0)
        dr = math.radians(phi1 - phi)
        d1 = shape_d(phi1)
        J1 = J_of(phi1, d1)
        w_prev = math.sqrt(2 * E / J_prev)
        a_ev = phi if (motor_step or not full) else phi + 0.5 * (phi1 - phi)
        Lq = load(a_ev, w_prev)
        drive = tau_m - cg * w_prev ** 2 - fr - Lq
        dE = drive * dr
        dK = 0.5 * (J_transfer(phi1, d1) - J_transfer(phi, d_prev)) * w_prev ** 2
        loss = (1 - eta) * abs(dK)
        book['spring'] += tau_m * dr; book['governor'] += cg * w_prev ** 2 * dr; book['friction'] += fr * dr
        book['loads'] += Lq * dr; book['transfer'] += loss
        if E + dE - loss <= 1e-12 and phi > 1.0:
            stall = phi
            rows.append((t, phi, w_prev, 0.0))
            break
        E = max(E + dE - loss, 1e-12)
        w1 = math.sqrt(2 * E / J1)
        dt = dr / max(0.5 * (w_prev + w1), 1e-3)
        rows.append((t, phi, w_prev, (w1 - w_prev) / dt))
        t += dt
        phi, d_prev, J_prev = phi1, d1, J1
        if t > 5:
            stall = phi; break
    if stall is None:
        w_end = math.sqrt(2 * E / J_prev)
        rows.append((t, 360.0, w_end, rows[-1][3]))
        book['K_end'] = E
        book['K_start'] = max(0.5 * J_of(0.0, shape_d(0.0)) * w0 * w0, 0.0)
        book['residual'] = book['spring'] + book['K_start'] - book['governor'] - book['friction'] - book['loads'] - book['transfer'] - E
    A = np.array(rows)
    return Trace(A[:, 0], A[:, 1], A[:, 2], A[:, 3], book, stall=stall,
                 meta=dict(tau_m=tau_m, cg=cg, J0=J0, eta=eta, fric=fric, w0=w0, mode=mode))


def slot_friction(tr, ch):
    """Return cams' slot friction by angle on the trace (node B's rule, steel on steel 0.12 on the force the beam
    carries); (phi, torque N m)."""
    import parts as PT
    I_rot, m_lift, rot_own, lift_own = NB.chain_masses()
    F_ret_rot = 4 * LJ['selection']['forces']['F_return'] + MASS['cam rod rotate']['m'] * U.G
    F_ret_lift = 3 * LJ['selection']['forces']['F_return'] + MASS['cam rod lift']['m'] * U.G
    cf, (phi, Nr, Nl, acc, tape) = NB.contact_forces(tr.arr(), ch['th'], ch['dz'], I_rot, m_lift, rot_own, lift_own, F_ret_rot, F_ret_lift)
    tau = np.zeros_like(phi)
    for k, N in (('rotate', Nr), ('lift', Nl)):
        if 'psi_' + k not in _TAB:
            _TAB['psi_' + k] = (GRID, np.array([1.0 / math.cos(PT.ret_psi(k, a)) for a in GRID]))
        g, sec = _TAB['psi_' + k]
        dsec = np.abs(np.gradient(sec, np.radians(g)))
        am, ar = PT.ret_arms(k)
        tau += 0.12 * np.maximum(0.0, -np.asarray(N)) * (1 + am / ar) * np.interp(phi, g, dsec) * (am + ar) * 1e-3
    return (phi, tau), cf


def trace(ch, wind='M_need', passes=2, **kw):
    """The law of one revolution with every load: two passes (the slot friction from the first pass's forces)."""
    M = WINDS[wind] if isinstance(wind, str) else wind
    tr = integrate(ch, M=M, **kw)
    cf = None
    for _ in range(passes - 1):
        if tr.stall is not None:
            break
        sl, cf = slot_friction(tr, ch)
        tr = integrate(ch, M=M, slot=sl, **kw)
    tr.meta['wind'] = wind
    return tr


class Clock:
    """t(phi), phi(t), w(phi), wdot(phi) of one revolution (phi in deg, t in s from the start of the revolution)."""

    def __init__(self, t, phi, w, wd):
        self._t = np.asarray(t, float); self._p = np.asarray(phi, float); self._w = np.asarray(w, float); self._wd = np.asarray(wd, float)
        self.T = float(self._t[-1])

    @classmethod
    def uniform(cls, T):
        ph = np.linspace(0.0, 360.0, 3601)
        w = 2 * math.pi / T
        return cls(ph / 360.0 * T, ph, np.full_like(ph, w), np.zeros_like(ph))

    def t(self, phi):
        return np.interp(phi, self._p, self._t) if np.ndim(phi) else float(np.interp(phi, self._p, self._t))

    def phi(self, t):
        return np.interp(t, self._t, self._p) if np.ndim(t) else float(np.interp(t, self._t, self._p))

    def w(self, phi):
        return np.interp(phi, self._p, self._w) if np.ndim(phi) else float(np.interp(phi, self._p, self._w))

    def wdot(self, phi):
        return np.interp(phi, self._p, self._wd) if np.ndim(phi) else float(np.interp(phi, self._p, self._wd))

    def deg_per_s(self, phi):
        return math.degrees(self.w(phi))


def validate():
    """§5б.8 p. 1: mode 'motor' against motor.simulate on every character, the same torque and governor."""
    rows = []
    tau = MJ['tau_C']; cg = CG_NOM
    for ch in characters():
        t_mo = MO.simulate(tau, cg, ch['th'], ch['dz'], er=MO.read_work(ch['item']))[0]
        a = integrate(ch, tau=tau, cg=cg, mode='motor', dphi=0.25, motor_step=True)
        b = integrate(ch, tau=tau, cg=cg, mode='motor', dphi=0.1, motor_step=True)
        rows.append(dict(key=ch['key'], t_motor=t_mo, t_same_step=a.T, t_01=b.T, d_same_pct=100 * (a.T / t_mo - 1), d_01_pct=100 * (b.T / t_mo - 1)))
    return rows


if __name__ == '__main__':
    v = validate()
    print('max |d| same step %', max(abs(r['d_same_pct']) for r in v), ' at 0.1 deg %', max(abs(r['d_01_pct']) for r in v))
    chs = characters()
    for ch in chs[:3] + [c for c in chs if c['idle']]:
        for wd in WINDS:
            tr = trace(ch, wd)
            print(ch['key'], ch['pos'], ch['row'], wd, 'T', round(tr.T, 4), 'stall', tr.stall, 'residual mJ', round(tr.book.get('residual', float('nan')) * 1e3, 4),
                  'w end', round(float(tr.w[-1]), 1), 'loads mJ', round(tr.book['loads'] * 1e3, 1))
