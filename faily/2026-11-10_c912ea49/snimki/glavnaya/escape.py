"""rev. 0.9c: the escapement with backspace, back-a-letter and the +-u lever (section "Забой и назад на литеру").

Plan view, angles CCW from +X about the wheel axis ESC; the wheel's forward turn (carriage spring, carriage -X) is
CCW. The wheel is a ratchet of 60 teeth, 10 mm thick: lower tier z 66..71, upper tier 71..76. Every tooth has a radial
face that looks CCW (at angles 6k + rot) and a slope rising CCW from the root (r 18) to the tip (r 20.5).

* holding dog D: a radial slider at 90 deg (back); its tip sits in the gap CCW of a face and touches it, so the wheel
  cannot go forward; it rides up the slopes when the wheel goes back.
* movable stop U: a drum (r 9.55, steel tape from the W link: exactly 6 deg per unit) with an arm and a finger in the
  lower tier at 186 + 6 (w - 4 + pm) deg; out of mesh (lowered 6 mm) at rest, it comes in for the release.
* +-u lever: an arm on the shaft under U; its pad is U's zero stop, three notches move it by -6 / 0 / +6 deg.
* back arm B: above the wheel; a pawl in the upper tier, held out of the teeth at rest by a guard; two ball studs at
  r 13 for the links. Turning CW, the pawl drops in after 0.6 deg, meets a face at 1.2 deg and turns the wheel back.
* memory arm M: above B; it carries a coupling wedge (upper tier) and a holding pawl in a fixed ratchet sector. On a
  release the wedge couples M to the wheel, so M goes forward with it by 6 w; the holding pawl keeps it there. For
  back-a-letter the wedge couples M again and the holding pawl lets go: the wheel goes back with M until M meets its
  zero stop, that is by 6 w (plus 1.2 deg of the wedge's play, so the dog falls in; the wheel comes forward onto it).
* rockers: the tails of the backspace and back-a-letter levers carry pins in slots of two rockers on one shaft
  (y 30, z 50.5); their lower arms pull two links with ball ends to B's studs. The backspace rocker meets a stop after
  1.4 teeth of B; the back-a-letter link has a spring for the rest of the stroke."""
import math
import numpy as np
from shapely.geometry import Polygon
from shapely import affinity
import params as P
import geo
from geo import box, cyl, zcyl, union, rotz

ESC = (0.0, 116.05)
TEETH = 60
PITCH = 360.0 / TEETH
R_ROOT, R_TIP = 18.0, 20.5
Z_W = (66.0, 76.0)                 # wheel
Z_LO, Z_UP = (66.0, 71.0), (71.0, 76.0)
TH_D = 90.0                        # dog
TH_U0 = 162.0                      # U finger at w = 0 (the rest is at 4 teeth: 186 deg)
TH_B = 0.0                         # face that B's pawl meets
B_CATCH = 1.2                      # deg of B before its pawl meets the face
B_DROP = 0.6                       # deg of B before the guard lets the pawl in
TH_M = 102.0                       # M at zero (memory 0)
M_PLAY = 1.2                       # play of the coupling wedge (deg)
Z_B = (76.5, 79.5)
Z_M = (80.0, 83.0)
Z_UD = (56.5, 59.5)                # U drum
Z_PM = (54.2, 56.2)                # +-u arm
R_DRUM = 9.549                     # 6 deg per unit (0.529 mm... per mm of the W link: 1 unit = 1 mm)
STUD = {'bksp': (13.0, 48.0), 'back': (13.0, 62.0)}     # (r, deg) of B's ball studs at rest
STUD_Z = Z_B[1] + 2.0
ROCK = dict(y=30.0, z=50.5, x={'bksp': (119.4, 122.2), 'back': (131.8, 134.6)}, r_in=9.0, r_out={'bksp': 6.0, 'back': 32.0})
TAIL_PIN = dict(y=21.0, z=50.5)
BKSP_DEG = 1.4 * PITCH


def slope_r(da):
    """Radius of the tooth surface da deg CCW of a face (0 <= da < 6)."""
    return R_ROOT + (R_TIP - R_ROOT) * (da % PITCH) / PITCH


def wheel_profile(rot):
    """The wheel's outline (shapely) at rotation rot (deg)."""
    pts = []
    for k in range(TEETH):
        a0 = math.radians(k * PITCH + rot); a1 = math.radians((k + 1) * PITCH + rot)
        pts.append((ESC[0] + R_ROOT * math.cos(a0), ESC[1] + R_ROOT * math.sin(a0)))
        pts.append((ESC[0] + R_TIP * math.cos(a1 - 1e-3), ESC[1] + R_TIP * math.sin(a1 - 1e-3)))
    return Polygon(pts)


def P2(r, a):
    a = math.radians(a)
    return (ESC[0] + r * math.cos(a), ESC[1] + r * math.sin(a))


def tip_shape(face, play=0.0, r_out=23.5, w_cw=4.0, w_ccw=6.0):
    """Tip that fills the gap CCW of the face at angle `face`: its CW edge on the face (touching), its underside
    0.2 mm over the slope, shifted CCW by `play` deg; above the tooth tips it widens."""
    pts = [P2(R_ROOT + 0.35, face), P2(20.75, face), P2(20.75, face - w_cw), P2(r_out, face - w_cw), P2(r_out, face + w_ccw),
           P2(20.75, face + w_ccw)]
    n = 24
    for i in range(n + 1):
        th = face + w_ccw - (w_ccw - play) * i / n
        r = max(R_ROOT + 0.35, slope_r(th - face - play) + 0.2) if th - face - play >= 0 else R_ROOT + 0.35
        r = min(r, 20.75)
        pts.append(P2(r, th))
    return Polygon(pts).buffer(0)


def extrude(g, z0, z1):
    return geo.shapely_to_cs(g).extrude(z1 - z0).translate((0, 0, z0))


def wheel_rot(st):
    return -math.degrees((st.car - P.CAR_X_START) / 5.053)


def b_angle(st):
    """B's CW turn (deg) from the two keys: backspace 1.4 teeth; back-a-letter to M's zero stop (6 w + play)."""
    fb = st.pressed.get(46, 0.0); fk = st.pressed.get(47, 0.0)
    w = st.esc_mem
    return max(BKSP_DEG * fb, (B_CATCH + PITCH * w + M_PLAY) * fk)


def dog_lift(rot):
    """Radial lift of the dog so its tip clears the wheel at rotation rot (0 at a whole tooth)."""
    tip = tip_shape(TH_D)
    wp = wheel_profile(rot)
    lo, hi = 0.0, 3.0
    if tip.intersection(wp).area < 1e-5:
        return 0.0
    for _ in range(20):
        mid = (lo + hi) / 2
        if affinity.translate(tip, 0, mid).intersection(wp).area < 1e-5:
            hi = mid
        else:
            lo = mid
    return hi


def parts(st, Part, COL, cached):
    x, y = ESC
    zr = P.CAR_RAIL_LO[1]
    out = []
    rot = wheel_rot(st)
    # ---- wheel and pinion
    def wheel():
        pin = geo.gear_profile(10, 1.0106, x, y).extrude(6).translate((0, 0, zr - 2))
        w = geo.ratchet_profile(TEETH, R_ROOT, R_TIP, x, y).extrude(Z_W[1] - Z_W[0]).translate((0, 0, Z_W[0]))
        m = pin + w + zcyl(x, y, Z_W[0], zr - 2, 6, 24)
        return m - zcyl(x, y, 20, 120, 2.05, 16)
    out.append(Part('escapement wheel and pinion', 'esc', 'print', rotz(cached('escw', wheel), rot, x, y), COL['esc'], 'esc_wheel', 'PETG',
                    note='храповое колесо 60 зубьев толщиной 10 мм (два этажа) и шестерня z = 10 одной деталью', mov='esc'))
    out.append(Part('escapement shaft', 'esc', 'buy', zcyl(x, y, 20, zr + 8, 2.0, 16), COL['steel'], 'rod4x80', 'сталь'))
    # ---- bracket: base on the frame's back beam, a post on +X (front right), plates at 50..54 and 98..102,
    # the dog's guide at the back and the memory sector's hanger
    pp = P2(31.0, -40.0)
    br = box(x - 12, x + 34, y - 6, y + 34, 20, 24)
    br = br + box(pp[0] - 3, pp[0] + 3, pp[1] - 3, pp[1] + 3, 20, 102)
    br = br + box(x - 12, pp[0] + 3, y - 6, y + 34, 50, 54) - zcyl(x, y, 49, 55, 6.5, 32)
    top = box(x - 12, pp[0] + 3, pp[1] - 3, y + 34, 98, 102)
    br = br + top
    br = br + box(x - 12, x - 6, y + 28, y + 34, 20, 102)                                 # back left post
    br = br + box(x + 6, x + 12, y + 28, y + 34, 20, 102)                                 # back right post
    # dog guide: a channel along +Y at the back, between the posts (z 64..78)
    br = br + box(x - 6, x - 2.2, y + 24, y + 28, 64, 78) + box(x + 2.2, x + 6, y + 24, y + 28, 64, 78)
    br = br - zcyl(x, y, 19, 121, 2.1, 16)
    out.append(Part('escapement bracket', 'esc', 'print', br, (110, 112, 120), 'esc_bracket', 'PETG',
                    note='кронштейн спуска: стойка на +X, задние стойки с направляющей собачки, плиты 50 и 98 мм',
                    printable=lambda br=br: geo_split(br)))
    # ---- holding dog: a radial slider at 90 deg
    lift = dog_lift(rot % PITCH if abs((rot % PITCH) - PITCH) > 1e-6 else 0.0)
    dg = extrude(tip_shape(TH_D, r_out=23.5, w_cw=1.6, w_ccw=2.0), Z_W[0] + 0.5, Z_W[1] - 0.5)
    dg = dg + box(x - 2.0, x + 2.0, y + 23.0, y + 27.6, Z_W[0] + 0.5, Z_W[1] - 0.5)
    out.append(Part('escapement dog', 'esc', 'print', dg.translate((0, lift, 0)), COL['esc'], 'esc_dog', 'PETG',
                    note='держащая собачка: ползун в направляющей сзади колеса, пружина 0,3 Н', mov='escdog'))
    # ---- U: drum, arm and finger; the tape from the W link; lug for the zero stop
    s_w = st.frames.get('W', 0.0)
    th_u = TH_U0 + PITCH * (4 + s_w + st.pm_u)
    drop = 0.0 if st.u_in else -6.0
    def ustop():
        d = zcyl(x, y, *Z_UD, R_DRUM, 64) + zcyl(x, y, Z_UD[1], Z_UD[1] + 3.0, 6.0, 32)
        arm = box(x, x + 21.5, y - 2.0, y + 2.0, *Z_UD)
        lug = box(x + 6.0, x + 12.5, y - 3.0, y, Z_UD[1], Z_UD[1] + 3.0)     # CW edge at 0 deg in this frame
        f = extrude(tip_shape(0.0, r_out=22.5, w_cw=1.5, w_ccw=2.5), Z_UD[0], Z_LO[1])
        return (d + arm + lug + f) - zcyl(x, y, Z_UD[0] - 1, Z_UD[1] + 4, 2.05, 16)
    um = rotz(cached('escU', ustop), th_u, x, y).translate((0, 0, drop))
    # the lug in this frame sits at 0 deg + its arm at th_u: rotate the lug to th_u - 180 is done by the frame above
    out.append(Part('escapement stop', 'esc', 'print', um, COL['esc'], 'esc_stop', 'PETG',
                    note='переставной упор U: барабан R 9,55 мм под ленту от тяги W (6° на единицу), палец в нижнем этаже',
                    mov='followW'))
    # tape: from the rod's end (x -2, y + R) over the drum's top, wrapped CW to its anchor
    a_top = 90.0
    wrap = union([box(x - 2.0, x, y + R_DRUM, y + R_DRUM + 0.1, Z_UD[0] + 0.5, Z_UD[1] - 0.5)] +
                 [geo.sector_xy(x, y, R_DRUM, R_DRUM + 0.1, -30.0 + PITCH * (4 + s_w + st.pm_u), a_top, Z_UD[0] + 0.5, Z_UD[1] - 0.5)])
    out.append(Part('escapement tape', 'esc', 'buy', wrap, (60, 60, 70), 'tape', 'сталь', 'лента 0,1 мм от тяги W к барабану U',
                    mov='followW'))
    # ---- +-u lever: arm on the shaft under U; pad = U's zero stop; three notches
    th_pad = th_u - PITCH * s_w        # U at rest: its lug's CW edge (th_u + 0 in U's frame) meets the pad
    def pmarm():
        h = zcyl(x, y, *Z_PM, 5.0, 32) - zcyl(x, y, Z_PM[0] - 1, Z_PM[1] + 1, 2.05, 16)
        a = box(x, x + 33.0, y - 2.0, y + 2.0, *Z_PM)
        pad = box(x + 6.0, x + 12.5, y, y + 3.0, Z_PM[0], Z_UD[1] + 3.0) - zcyl(x, y, Z_PM[0] - 1, Z_UD[1] + 4, 9.8, 48)
        bump = zcyl(x + 33.0, y, Z_PM[0], Z_PM[1], 1.5, 16)
        return h + a + pad + bump
    pm = rotz(cached('escPM', pmarm), th_pad, x, y)
    out.append(Part('pm-u lever', 'esc', 'print', pm, (200, 160, 60), 'pmu_lever', 'PETG',
                    note='рычажок ±u: упор нуля U в трёх положениях (−6°, 0, +6°)', mov='pmu'))
    ntch = geo.sector_xy(x, y, 33.0, 37.0, th_pad - PITCH * st.pm_u - 10.0, th_pad - PITCH * st.pm_u + 10.0, Z_PM[0], Z_PM[1])
    for k in (-1, 0, 1):
        c = P2(33.0, th_pad - PITCH * st.pm_u + PITCH * k)
        ntch = ntch - zcyl(c[0], c[1], Z_PM[0] - 1, Z_PM[1] + 1, 1.5, 16)
    out.append(Part('pm-u detent plate', 'esc', 'print', ntch, (110, 112, 120), 'pmu_plate', 'PETG',
                    note='гребёнка рычажка ±u: три выреза'))
    # ---- B: hub on the wheel hub, crank with two ball studs, pawl arm; the pawl and its guard
    beta = b_angle(st)
    def barm():
        h = zcyl(x, y, *Z_B, 9.5, 48) - zcyl(x, y, Z_B[0] - 1, Z_B[1] + 1, 6.1, 32)
        cr = geo.sector_xy(x, y, 8.0, 15.5, 40.0, 70.0, *Z_B)
        pa = geo.sector_xy(x, y, 8.0, 28.0, 8.0, 18.0, *Z_B)
        m = h + cr + pa
        for r, a in STUD.values():
            c = P2(r, a)
            m = m + zcyl(c[0], c[1], Z_B[1], STUD_Z, 0.9, 12) + geo.Manifold.sphere(1.6, 16).translate((c[0], c[1], STUD_Z))
        pv = P2(25.0, 13.0)
        m = m + zcyl(pv[0], pv[1], Z_UP[0] + 0.5, Z_B[0], 1.0, 12)
        return m
    out.append(Part('back lever B', 'esc', 'print', rotz(cached('escB', barm), -beta, x, y), COL['esc'], 'esc_back_lever', 'PETG',
                    note='рычаг B над колесом: собачка в верхнем этаже, два шаровых пальца R 13 мм', mov='backB'))
    pv = P2(25.0, 13.0)
    def bpawl():
        t = extrude(tip_shape(TH_B + B_CATCH, play=1.4, r_out=22.5, w_cw=1.0, w_ccw=2.0), Z_UP[0] + 0.5, Z_UP[1] - 0.3)
        body = geo.Manifold.batch_hull([zcyl(pv[0], pv[1], Z_UP[0] + 0.5, Z_UP[1] - 0.3, 2.2, 16),
                                        zcyl(*P2(21.6, TH_B + B_CATCH + 0.5), Z_UP[0] + 0.5, Z_UP[1] - 0.3, 1.0, 12)])
        tail = geo.Manifold.batch_hull([zcyl(pv[0], pv[1], Z_UP[0] + 0.5, Z_UP[1] - 0.3, 2.2, 16),
                                        zcyl(*P2(27.5, 21.0), Z_UP[0] + 0.5, Z_UP[1] - 0.3, 1.2, 12)])
        return (t + body + tail) - zcyl(pv[0], pv[1], Z_UP[0], Z_UP[1], 1.05, 12)
    if beta < B_DROP:
        # lifted by the guard: the tip clears the tooth tips (0.3 mm)
        lift_a = 0.3 / math.hypot(*(np.subtract(P2(19.4, TH_B + B_CATCH), pv))) * 180 / math.pi
        bp = rotz(cached('escBP', bpawl), lift_a, pv[0], pv[1])
    else:
        bp = cached('escBP', bpawl)
    out.append(Part('back pawl', 'esc', 'print', rotz(bp, -beta, x, y), COL['esc'], 'esc_back_pawl', 'PETG',
                    note='собачка B на пальце рычага, пружина 0,2 Н', mov='backB'))
    g = geo.sector_xy(x, y, 28.8, 31.0, 20.0, 27.0, Z_UP[0] + 0.5, Z_UP[1] - 0.3)
    g = g + box(P2(30, 23.5)[0] - 1.5, P2(30, 23.5)[0] + 1.5, P2(30, 23.5)[1] - 1.5, P2(30, 23.5)[1] + 1.5, Z_UP[0] + 0.5, 98.0)
    out.append(Part('back pawl guard', 'esc', 'print', g, (110, 112, 120), 'esc_guard', 'PETG',
                    note='щиток: держит собачку B вне зубьев в покое'))
    # ---- M: memory arm, coupling wedge, holding pawl; fixed sector and zero stop
    m_ang = TH_M + PITCH * st.esc_mem - max(0.0, beta - B_CATCH - M_PLAY) * (1.0 if st.pressed.get(47, 0.0) > 0 else 0.0)
    coupled = st.pressed.get(47, 0.0) > 0 or st.m_couple
    def marm():
        h = zcyl(x, y, *Z_M, 9.5, 48) - zcyl(x, y, Z_M[0] - 1, Z_M[1] + 1, 6.1, 32)
        a = geo.sector_xy(x, y, 8.0, 27.0, -5.0, 4.0, *Z_M)
        hp = zcyl(*P2(26.0, 2.5), Z_M[0], Z_M[1], 1.0, 12)
        return h + a + hp
    out.append(Part('memory lever M', 'esc', 'print', rotz(cached('escM', marm), m_ang, x, y), COL['esc'], 'esc_memory', 'PETG',
                    note='рычаг памяти M: помнит ширину последней литеры (6w°)', mov='escM'))
    def mwedge():
        t = extrude(tip_shape(0.0, play=M_PLAY, r_out=22.5, w_cw=1.5, w_ccw=2.5), Z_UP[0] + 0.5, Z_M[0] - 0.2)
        return t
    wz = 0.0 if coupled else 5.0
    out.append(Part('memory coupling wedge', 'esc', 'print', rotz(cached('escMW', mwedge), m_ang, x, y).translate((0, 0, wz)),
                    COL['esc'], 'esc_wedge', 'PETG', note='клин сцепления M с колесом (люфт 1,2°)', mov='escM'))
    def mpawl():
        return geo.sector_xy(x, y, 26.4, 28.3, 2.0, 4.0, *Z_M) + zcyl(*P2(26.0, 2.5), Z_M[0], Z_M[1], 1.4, 12) - \
            zcyl(*P2(26.0, 2.5), Z_M[0] - 1, Z_M[1] + 1, 1.05, 12)
    out.append(Part('memory holding pawl', 'esc', 'print', rotz(cached('escMP', mpawl), m_ang, x, y), COL['esc'], 'esc_mpawl', 'PETG',
                    note='собачка удержания M в неподвижном храповом секторе', mov='escM'))
    def msector():
        s = geo.sector_xy(x, y, 28.3, 31.0, TH_M - 3.0, TH_M + 16 * PITCH + 8.0, *Z_M)
        for k in range(18):
            a = TH_M + PITCH * k + 4.0
            s = s - geo.Manifold.batch_hull([zcyl(*P2(28.3, a - 2.0), Z_M[0] - 1, Z_M[1] + 1, 0.05, 6),
                                             zcyl(*P2(28.3, a), Z_M[0] - 1, Z_M[1] + 1, 0.05, 6),
                                             zcyl(*P2(29.0, a), Z_M[0] - 1, Z_M[1] + 1, 0.05, 6)])
        c = P2(29.6, TH_M + 50.0)
        s = s + box(c[0] - 1.5, c[0] + 1.5, c[1] - 1.5, c[1] + 1.5, Z_M[1], 98.0)
        zs = P2(16.0, TH_M - 6.5)
        s = s + zcyl(zs[0], zs[1], Z_M[0], 98.0, 1.5, 16)
        return s
    out.append(Part('memory ratchet sector', 'esc', 'print', cached('escMS', msector), (110, 112, 120), 'esc_msector', 'PETG',
                    note='неподвижный храповой сектор M (шаг 6°) с упором нуля M, подвешен к верхней плите'))
    # ---- rockers, tail pins, links
    for key, n in (('bksp', 46), ('back', 47)):
        f = st.pressed.get(n, 0.0)
        k = {'y': P.KEY_ROW_Y[0] if key == 'bksp' else P.KEY_ROW_Y[1]}
        a_lev = math.atan2(P.KEY_TRAVEL * f, P.LEVER_PIVOT_Y - k['y'])
        zc = (P.LEVER_Z0 + P.LEVER_Z1) / 2
        ty, tz = TAIL_PIN['y'], TAIL_PIN['z']
        yy = P.LEVER_PIVOT_Y + (ty - P.LEVER_PIVOT_Y) * math.cos(a_lev) - (tz - zc) * math.sin(a_lev)
        zz = zc + (ty - P.LEVER_PIVOT_Y) * math.sin(a_lev) + (tz - zc) * math.cos(a_lev)
        x0, x1 = ROCK['x'][key]
        xl = (122.5, 125.5) if key == 'bksp' else (128.5, 131.5)
        px0, px1 = (x0 - 0.3, xl[0]) if key == 'bksp' else (xl[1], x1 + 0.3)
        out.append(Part(f'{key} tail pin', 'levers', 'buy', cyl((px0, yy, zz), (px1, yy, zz), 1.2, 12), COL['steel'], 'pin2x8', 'сталь',
                        'палец в хвосте рычага', mov=f'key{n}'))
        phi = math.atan2(zz - ROCK['z'], ROCK['y'] - yy)          # the input arm points -Y; the pin rises
        if key == 'bksp':
            phi = min(phi, bksp_phi_stop())
        ro = ROCK['r_out'][key]
        rk = cyl((x0, ROCK['y'], ROCK['z']), (x1, ROCK['y'], ROCK['z']), 3.0, 16)
        rk = rk + box(x0, x1, ROCK['y'] - ROCK['r_in'] - 3.5, ROCK['y'], ROCK['z'] - 2.5, ROCK['z'] + 2.5) - \
            box(x0 - 1, x1 + 1, ROCK['y'] - ROCK['r_in'] - 2.5, ROCK['y'] - ROCK['r_in'] + 2.5, ROCK['z'] - 1.2, ROCK['z'] + 1.2)
        rk = rk + box(x0, x1, ROCK['y'] - 2.0, ROCK['y'] + 2.0, ROCK['z'] - ro - 2.0, ROCK['z'])
        rk = rk - cyl((x0 - 1, ROCK['y'], ROCK['z']), (x1 + 1, ROCK['y'], ROCK['z']), 1.55, 12)
        ball = geo.Manifold.sphere(1.6, 16).translate(((x0 + x1) / 2, ROCK['y'], ROCK['z'] - ro))
        rk = rk + ball + cyl(((x0 + x1) / 2, ROCK['y'], ROCK['z'] - ro), (x0 if key == 'bksp' else x1, ROCK['y'], ROCK['z'] - ro), 0.9, 12)
        rk = geo.rotx(rk, -math.degrees(phi), ROCK['y'], ROCK['z']) if hasattr(geo, 'rotx') else rk
        out.append(Part(f'{key} rocker', 'esc', 'print', rk, COL['esc'], f'rocker_{key}', 'PETG',
                        note=f'качалка {"забоя" if key == "bksp" else "«назад на литеру»"}: плечи {ROCK["r_in"]:.0f} и {ro:.0f} мм',
                        mov=f'rock{key}'))
        # link: ball socket at both ends; the length is fixed at rest, the back-a-letter link has a spring
        rb = ((x0 + x1) / 2, ROCK['y'] - ro * math.sin(phi) * 0 + ro * math.sin(-phi) * 0, 0)
        ry_ = ROCK['y'] + ro * math.sin(-phi) * -1.0 if False else ROCK['y'] - ro * math.sin(phi)
        rz_ = ROCK['z'] - ro * math.cos(phi)
        A = np.array([(x0 + x1) / 2, ry_, rz_])
        sr, sa = STUD[key]
        B = np.array(list(P2(sr, sa - beta)) + [STUD_Z])
        lk = cyl(tuple(A), tuple(B), 0.75, 8) + geo.Manifold.sphere(2.2, 16).translate(tuple(A)) + geo.Manifold.sphere(2.2, 16).translate(tuple(B))
        lk = lk - geo.Manifold.sphere(1.6, 16).translate(tuple(A)) - geo.Manifold.sphere(1.6, 16).translate(tuple(B))
        out.append(Part(f'{key} link', 'esc', 'buy', lk, COL['steel'], 'ball_link', 'сталь',
                        'тяга 1,5 мм с шаровыми наконечниками' + (' и пружиной' if key == 'back' else ''), mov=f'rock{key}'))
    # rocker shaft and its bracket; the backspace stop
    out.append(Part('rocker shaft', 'esc', 'buy', cyl((117.5, ROCK['y'], ROCK['z']), (137.0, ROCK['y'], ROCK['z']), 1.5, 12),
                    COL['steel'], 'rod3x20', 'сталь'))
    rb = box(114.5, 117.5, ROCK['y'] - 4, ROCK['y'] + 4, 0.0, ROCK['z'] + 4) + box(137.0, 140.0, ROCK['y'] - 4, ROCK['y'] + 4, 0.0, ROCK['z'] + 4)
    rb = rb + box(114.5, 140.0, ROCK['y'] - 4, ROCK['y'] + 4, 0.0, 4.0)
    rb = rb - cyl((114, ROCK['y'], ROCK['z']), (141, ROCK['y'], ROCK['z']), 1.55, 12)
    # stop of the backspace rocker: a pad that its output arm meets
    sy, sz = stop_pad()
    rb = rb + box(119.4, 122.2, sy - 1.5, sy, sz - 6, sz + 1) + box(117.5, 119.4, sy - 1.5, sy, 0.0, sz + 1)
    out.append(Part('rocker bracket', 'esc', 'print', rb, (110, 112, 120), 'rocker_bracket', 'PETG',
                    note='стойки качалок забоя и «назад на литеру» с упором забоя'))
    return out


def geo_split(m):
    return m


def bksp_phi_stop():
    """Rocker angle at which B has turned 1.4 teeth (found from the link geometry)."""
    return _bksp_phi()[0]


_cache = {}


def _link_len(key):
    ro = ROCK['r_out'][key]
    A = np.array([sum(ROCK['x'][key]) / 2, ROCK['y'], ROCK['z'] - ro])
    sr, sa = STUD[key]
    B = np.array(list(P2(sr, sa)) + [STUD_Z])
    return float(np.linalg.norm(B - A))


def rocker_for_beta(key, beta):
    """Rocker angle that turns B by beta with a rigid link."""
    L = _link_len(key); ro = ROCK['r_out'][key]
    sr, sa = STUD[key]
    B = np.array(list(P2(sr, sa - beta)) + [STUD_Z])
    xm = sum(ROCK['x'][key]) / 2
    lo, hi = 0.0, 1.2
    for _ in range(60):
        mid = (lo + hi) / 2
        A = np.array([xm, ROCK['y'] - ro * math.sin(mid), ROCK['z'] - ro * math.cos(mid)])
        if np.linalg.norm(B - A) < L:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _bksp_phi():
    if 'b' not in _cache:
        _cache['b'] = (rocker_for_beta('bksp', BKSP_DEG),)
    return _cache['b']


def stop_pad():
    """Where the backspace rocker's output arm (its back face) stands at the stop."""
    phi = bksp_phi_stop(); ro = ROCK['r_out']['bksp']
    y = ROCK['y'] - (ro + 2.0) * math.sin(phi) - 2.0 * math.cos(phi)
    z = ROCK['z'] - (ro + 2.0) * math.cos(phi) + 2.0 * math.sin(phi)
    return y, z


def summary():
    """Numbers for the document."""
    tail = P.KEY_TRAVEL * (TAIL_PIN['y'] - P.LEVER_PIVOT_Y) / (P.LEVER_PIVOT_Y - P.KEY_ROW_Y[1])
    phi_full = math.atan2(tail, ROCK['r_in'])
    out = {}
    for key in ('bksp', 'back'):
        need = BKSP_DEG if key == 'bksp' else B_CATCH + 16 * PITCH + M_PLAY
        out[key] = dict(rock_need=math.degrees(rocker_for_beta(key, need)), rock_full=math.degrees(phi_full), beta_need=need,
                        link=_link_len(key))
    return dict(tail=tail, **out)
