"""Links of the machine worked out from the layout parameters (rev. 0.8): selection whiffletrees with latches and
amplifiers, gauge frames on vertical guides, memory sectors on nested sleeves, the W link to the escapement stop,
hammer cocking, the row detent, the ribbon vibrator, the interlocks; strength checks.
Every link that sets a position is a slotted lever driven by a pin on a straight slider ("кулиса"): the output is then
exactly linear in the input, y = (b/a) x, whatever the angle; no small-angle error enters the code.
Usage: python3 -I links.py OUT_JSON"""
import sys, os, json, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import params as P

E_STEEL = 206000.0      # MPa
E_PETG = 2000.0         # MPa
RHO_PETG = 1.27e-3      # g/mm3
RHO_STEEL = 7.85e-3

# ------------------------------------------------------------------------------------------- selection
S = 12.0                # stroke of a latched bit slider (cam lift), mm
SLIDER_W = 4.0          # width of a slider (steel strip 4 x 3 in a printed comb)
MIN_GAP = 9.0           # min distance between slider axes (pins, comb teeth)


def ladder(nbits, x_out, x_min, x_max, step=0.5):
    """Positions (x) of the bit sliders b_i and intermediate nodes n_k of a slider-lever ladder:
    lever k joins node n_{k-1} (n_0 = b_0) and b_k; node n_k divides it in the ratio of the weights
    (n_k = n_{k-1} + (b_k - n_{k-1}) * 2^k / (2^{k+1} - 1)); the last node is the tree output at x_out.
    Chooses b's to maximise the smallest distance between any two sliders."""
    best = None
    grid = np.arange(x_min, x_max + 1e-9, step)
    # search over b_last and the lever lengths backwards from the output (coarse, then the exact solve)
    for bl in grid:
        acc_w = 2 ** nbits - 1
        frac = 2 ** (nbits - 1) / acc_w
        # x_out = n_prev + (bl - n_prev) * frac  ->  n_prev = (x_out - bl * frac) / (1 - frac)
        n_prev = (x_out - bl * frac) / (1 - frac)
        if not (x_min <= n_prev <= x_max):
            continue
        rest = _ladder_back(nbits - 1, n_prev, x_min, x_max, grid)
        for sol in rest:
            xs = sol['b'] + [bl]
            nodes = sol['n'] + [n_prev, x_out]
            allx = sorted(xs + nodes[1:])          # n_0 is b_0
            gap = min(b - a for a, b in zip(allx, allx[1:]))
            if best is None or gap > best[0]:
                best = (gap, xs, nodes)
    gap, xs, nodes = best
    return dict(b=[float(v) for v in xs], n=[float(v) for v in nodes], min_gap=float(gap))


def _ladder_back(nb, x_node, x_min, x_max, grid):
    """All ways to produce node x_node from nb bits (weights 1..2^(nb-1)) on the grid."""
    if nb == 1:
        return [dict(b=[x_node], n=[x_node])]
    out = []
    acc_w = 2 ** nb - 1
    frac = 2 ** (nb - 1) / acc_w
    for bl in grid[::2]:
        n_prev = (x_node - bl * frac) / (1 - frac)
        if not (x_min <= n_prev <= x_max) or abs(bl - x_node) < MIN_GAP:
            continue
        for sol in _ladder_back(nb - 1, n_prev, x_min, x_max, grid):
            out.append(dict(b=sol['b'] + [bl], n=sol['n'] + [n_prev]))
    return out


def node_y(tree, bits, f=1.0):
    """y displacement of every node for the given bits (list of 0/1) at drive phase f (0..1)."""
    y = [S * f * b for b in bits]
    nodes = [y[0]]
    acc = 1
    for k in range(1, len(bits)):
        w = 2 ** k
        nodes.append((acc * nodes[-1] + w * y[k]) / (acc + w))
        acc += w
    return y, nodes


def amplifier(step_out, nbits, offset_steps, a):
    """Second-class lever, pins in slots: input at a from the fulcrum, output at b; the fulcrum rides on a slide
    moved by the drive through the offset lever: y_out = G y_in + (1 - G) y_F, y_F = delta * f."""
    unit = S / (2 ** nbits - 1)
    G = step_out / unit
    b = G * a
    delta = -offset_steps * step_out / (1 - G)      # (1 - G) delta = offset * step
    return dict(unit=unit, G=G, a=a, b=b, delta=delta, offset_ratio=delta / S)


def selection():
    out = {}
    # rotate: output slider (tape) at x = 40; the amplifier lies along X; fulcrum beyond the input
    rot_amp = amplifier(P.TAPE_PER_POS, 4, -(P.NPOS - 1) / 2, a=16.0)
    x_tape = 40.0
    x_F = x_tape + rot_amp['b']
    x_in = x_F - rot_amp['a']
    rot_tree = ladder(4, x_in, 52.0, x_in, step=0.5)
    # angles of the amplifier: worst |y_in - y_F| over codes and drive phase
    worst = 0.0
    for c in range(P.NPOS):
        bits = [(c >> i) & 1 for i in range(4)]
        for f in np.linspace(0, 1, 11):
            _, n = node_y(rot_tree, bits, f)
            worst = max(worst, abs(n[-1] - rot_amp['delta'] * f))
    rot_amp.update(x_F=x_F, x_in=x_in, x_out=x_tape, theta_max=math.degrees(math.atan(worst / rot_amp['a'])),
                   slot_out=rot_amp['b'] * (1 / math.cos(math.atan(worst / rot_amp['a'])) - 1))
    out['rotate'] = dict(tree=rot_tree, amp=rot_amp)
    # lift: rest one row under the top row; output to the fork through a 1:3 slotted crank (fork input at d = 50)
    FORK_R = 150.0; FORK_D = 50.0
    lift_amp = amplifier(P.RH * FORK_D / FORK_R, 3, -P.REST_ROW, a=16.0)
    x_out_l = -40.0
    x_F_l = x_out_l - lift_amp['b']
    x_in_l = x_F_l + lift_amp['a']
    lt = ladder(3, -x_in_l, 52.0, -x_in_l, step=0.5)          # mirror image on the left
    lift_tree = dict(b=[-v for v in lt['b']], n=[-v for v in lt['n']], min_gap=lt['min_gap'])
    worst = 0.0
    for c in range(P.NROWS):
        bits = [(c >> i) & 1 for i in range(3)]
        for f in np.linspace(0, 1, 11):
            _, n = node_y(lift_tree, bits, f)
            worst = max(worst, abs(n[-1] - lift_amp['delta'] * f))
    lift_amp.update(x_F=x_F_l, x_in=x_in_l, x_out=x_out_l, theta_max=math.degrees(math.atan(worst / lift_amp['a'])),
                    fork_r=FORK_R, fork_d=FORK_D, fork_ratio=FORK_R / FORK_D,
                    fork_theta_max=math.degrees(math.atan((P.NROWS - 1 - P.REST_ROW) * P.RH / FORK_R)))
    out['lift'] = dict(tree=lift_tree, amp=lift_amp)
    # check: outputs equal the wanted steps exactly (linear pins in slots)
    errs = []
    for c in range(P.NPOS):
        bits = [(c >> i) & 1 for i in range(4)]
        _, n = node_y(rot_tree, bits, 1.0)
        y = rot_amp['G'] * n[-1] + (1 - rot_amp['G']) * rot_amp['delta']
        errs.append(abs(y - (c - (P.NPOS - 1) / 2) * P.TAPE_PER_POS))
    for c in range(P.NROWS):
        bits = [(c >> i) & 1 for i in range(3)]
        _, n = node_y(lift_tree, bits, 1.0)
        y = lift_amp['G'] * n[-1] + (1 - lift_amp['G']) * lift_amp['delta']
        hub = y * FORK_R / FORK_D
        errs.append(abs(hub - (c - P.REST_ROW) * P.RH))
    out['exact_error'] = max(errs)
    # latch: a pin in the bit slider, lifted 3.5 mm by its pad; the drive bail catches only a raised pin
    out['latch'] = dict(pin_d=3.0, lift=3.5, bail_edge_above_low_pin=1.5, spring_N=0.2,
                        note='pad lever over the selector rod, 18 mm long in Y: the pin stays up over the 12 mm stroke')
    # forces: slider return springs 0.4 N each, lever and pin friction 30 %; the drive bail moves all latched sliders
    F_ret = 0.4
    F_drive_rot = 4 * F_ret * 1.3 + 0.6         # all four bits latched, plus the offset slide
    F_drive_lift = 3 * F_ret * 1.3 + 0.6
    # load on the output: tape slider and the shuttle are moved by the cam through the tree: inertial force of the
    # shuttle reflected to the tape (mean, from the motor model) is carried by the bail, not by the springs
    out['forces'] = dict(F_return=F_ret, F_drive_rot=F_drive_rot, F_drive_lift=F_drive_lift)
    return out


# ------------------------------------------------------------------------------------- gauge frames
LANES = {'R': 110.0, 'O': 115.0, 'N': 120.0, 'W': 135.0, 'B': 140.0, 'C': 145.0}   # side plates, |x|


def frames():
    """Each frame: two steel bars, two side plates (one per side), four vertical guide rods with sleeves.
    Travel is a pure translation; the frame weight is carried by two springs."""
    out = {}
    for i, name in enumerate(P.BAIL_ORDER):
        xa = LANES[name]
        L = 2 * xa + 4
        m_bars = 2 * RHO_STEEL * math.pi * 2.5 ** 2 * L
        m_sides = 2 * RHO_PETG * 0.6 * (66 + 16) * 27 * 4          # two plates, about 0.6 filled
        m = m_bars + m_sides
        travel = {'R': P.TP, 'W': P.K_STEP * (16 - P.W_OFFSET), 'B': P.K_STEP * 8, 'C': P.K_STEP * 9,
                  'O': P.TP, 'N': P.TP}[name]
        F_pre = m * 9.81e-3 + 0.3                                    # holds the weight plus 0.3 N against the stop
        k = 0.15 / travel                                             # N/mm: +0.15 N over the full travel
        out[name] = dict(lane=xa, bar_len=L, mass_g=m, travel=travel, F_pre=F_pre, F_end=F_pre + 0.15, k=k)
    out['guide'] = dict(rod_d=3.0, sleeve_d=6.0, sleeve_len=10.0, clearance=0.05,
                        tilt_mrad=1000 * 0.05 / 66.0)                  # sleeve clearance over the guide spacing
    return out


# ---------------------------------------------------------------------------- memory sectors and the W link
SLEEVE_AXIS = (-322.0, 47.0)          # (y, z) of the nested sleeves, axis along X, above the frame tops
FOLLOW_R = 16.0                        # slotted follower arm: pin on the frame top, slot along the arm


def sectors():
    """Follower arm with a slot over a pin on the frame: tan(theta) = s / r. The ratchet teeth of the sector are at
    theta_k = atan(k / r) for k = 0..n (non-uniform pitch), so tooth k matches k units of travel exactly."""
    out = {}
    R_TEETH = 42.0
    for name, n in (('B', 8), ('C', 9), ('W', 12)):
        th = [math.degrees(math.atan(P.K_STEP * k / FOLLOW_R)) for k in range(n + 1)]
        pitch = [R_TEETH * math.radians(b - a) for a, b in zip(th, th[1:])]
        out[name] = dict(n=n, theta=th, pitch_min=min(pitch), pitch_max=max(pitch), r_teeth=R_TEETH)
    out['sleeves'] = dict(axis=SLEEVE_AXIS, follow_r=FOLLOW_R,
                          tubes='латунные трубки 5/6/7/8 мм (телескопический набор), ось 4 мм')
    # ratchet: a tooth edge at (k - 0.5) units lets the pawl fall behind tooth k when the frame stops at k
    out['ratchet'] = dict(capture=0.5 * P.K_STEP, pawl_spring_N=0.15)
    return out


def escape_link():
    """W frame (live, not the memory) -> the movable stop of the escapement, w teeth for w units.
    Escapement wheel 60 teeth, one per u; the stop arm turns about the wheel axis, 6 deg per u."""
    deg_per_u = 360.0 / 60
    r_a = P.K_STEP / math.radians(deg_per_u)      # attachment radius on the stop arm for 1 mm per u
    ESC = (0.0, 116.05)
    y0 = SLEEVE_AXIS[0]
    rod_y = ESC[1] - r_a
    L1 = rod_y - y0                                # long rod along Y on the left side at x = -172
    L2 = 172.0                                     # rod along X to the stop arm
    # tension rods (return spring at the escapement end); steel 2 mm: stretch under 0.5 N
    A = math.pi * 1.0 ** 2
    stretch = 0.5 * (L1 + L2) / (E_STEEL * A)
    return dict(r_a=r_a, deg_per_u=deg_per_u, base_teeth=P.W_OFFSET, rod_x=-172.0, rod_z=60.0, L1=L1, L2=L2,
                rod_d=2.0, spring_N=0.5, stretch_mm=stretch, bellcranks=2,
                note='тяги работают только на растяжение; обе качалки — кулисы 1:1')


# ------------------------------------------------------------------------------------------- hammer
def hammer():
    """Hammer cocked by its cam over 10..150 deg, released at 160 deg (sharp drop of the cam)."""
    import parts as PT, geo, trimesh
    V, F = geo.to_arrays(PT.hammer_mesh())
    tm = trimesh.Trimesh(V, F, process=False)
    tm.density = RHO_PETG * 0.8 / 1000.0
    yp, zp = P.HAMMER_PIVOT
    c = tm.center_mass
    I_c = tm.moment_inertia[0, 0]
    m = tm.mass                                     # kg
    d2 = (c[1] - yp) ** 2 + (c[2] - zp) ** 2
    I = (I_c + m * d2) * 1e-6 + 2e-7                # kg m2 (+ rubber pad and spring end)
    E = 0.020
    swing = math.radians(18.0)
    r_head = math.hypot(0 - yp, P.ZP - zp) * 1e-3  # m, pivot to the head
    w = math.sqrt(2 * E / I)
    v = w * r_head
    t_flight = swing / (w / 2) if w else 0          # from rest under a roughly constant torque
    # spring: torsion spring on the axle, preload so that the hammer rests on its back stop
    T_mean = E / swing                              # N m over the swing
    k_t = 2 * T_mean / swing * 0.5                  # half the torque is preload
    r_cock = 6.0 / math.degrees(swing) * 180 / math.pi   # cam stroke 6 mm through a cocking arm
    F_cam = T_mean / (r_cock * 1e-3) * 1.4          # peak about 1.4 x mean
    return dict(mass_g=m * 1000, I_kgmm2=I * 1e6, r_head_mm=r_head * 1000, E=E, swing_deg=18.0, v_impact=v,
                t_flight_ms=t_flight * 1000, T_mean_Nmm=T_mean * 1000, k_t_Nmm_per_deg=k_t * 1000 * math.pi / 180,
                r_cock_mm=r_cock, F_cam_N=F_cam, cam_rise=(10, 150), release=160)


# ------------------------------------------------------------------------------------------- row detent
def row_detent():
    """Notches of a comb on the lift fork, at radius rd from the fork pivot; row k printed at tan(theta) = lift / 150."""
    rd = 60.0
    th = [math.degrees(math.atan((k - P.REST_ROW) * P.RH / 150.0)) for k in range(P.NROWS)]
    pitch = [rd * math.radians(b - a) for a, b in zip(th, th[1:])]
    # capture at the hub: half the smallest notch pitch referred to the hub
    cap_hub = min(150.0 / math.cos(math.radians(t)) ** 2 * math.radians(b - t) / 2 for t, b in zip(th, th[1:]))
    return dict(rd=rd, theta=th, pitch_min=min(pitch), pitch_max=max(pitch), capture_hub=cap_hub, wedge_deg=60.0,
                stroke=6.0, cam='второй кулачок фиксаторов на левом конце вала, x = -155')


def ribbon():
    return dict(drop=P.RIBBON_DROP, ratio=P.RIBBON_DROP / 3.0, mass_g=6.0, F_N=0.6, E_mJ=0.6 * P.RIBBON_DROP * 1e-3 * 1000 / 1000)


def interlocks():
    """Ball race under the lever fronts: one lever at a time. Lock bail: from 5 to 345 deg the bail stands in the plane
    between the tabs of the levers that are up and the tab of the lever that is down: the others cannot go down,
    the pressed one cannot come up. Full stroke: a wire pawl on each lever over a fixed two-tooth rack."""
    n_levers = 44 + 3                                # char keys + 2 spaces + shift (the code keys)
    fin = 2.0
    ball = 4.75
    tab_h = 3.0
    travel = P.KEY_TRAVEL
    gap_plane = (tab_h, travel - tab_h)             # free plane between an up tab and the down tab
    return dict(n_levers=n_levers, fin=fin, ball_d=ball, race_slack=fin + 0.3, tab_h=tab_h, plane_clear=gap_plane,
                lock_in=5, lock_out=345, trip_at=15.5, rack_teeth=2)


def strength():
    # gauge frame bar: steel rod 5 mm, simply supported on the side plates, span 276 mm, 0.3 N from a lug mid-span
    d = 5.0; I = math.pi * d ** 4 / 64; L = 276.0; F = 0.3
    d_bar = F * L ** 3 / (48 * E_STEEL * I)
    # key lever: PETG cantilever 60 mm, 3 x 12 mm (height 12), 1 N at the end
    b, h, Lc, Fl = 3.0, 12.0, 60.0, 1.0
    d_lev = Fl * Lc ** 3 / (3 * E_PETG * b * h ** 3 / 12)
    sigma = 120.0 / 20.0
    return dict(d_bar=d_bar, d_lev=d_lev, sigma_type=sigma)


def all_links():
    return dict(selection=selection(), frames=frames(), sectors=sectors(), escape=escape_link(), hammer=hammer(),
                row_detent=row_detent(), ribbon=ribbon(), interlocks=interlocks(), strength=strength())


if __name__ == '__main__':
    res = all_links()
    json.dump(res, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
    for k, v in res.items():
        print(k, json.dumps(v, ensure_ascii=False)[:600])
