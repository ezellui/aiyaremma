"""Parts of the TPM-2 layout model. Every builder returns Part objects in world coordinates for a State.
kind: 'print' (FDM), 'buy' (purchased), 'cut' (cut from stock), 'ref' (paper, ribbon: not made)."""
import math
from dataclasses import dataclass, field
import numpy as np
import params as P
import data as D
import geo
import typeblocks as TB
from geo import box, cbox, cyl, zcyl, union, rotz, rotx

COL = {
    'frame': (175, 180, 188), 'buy': (120, 126, 136), 'steel': (150, 155, 165), 'key': (60, 62, 70),
    'lever': (214, 160, 72), 'plate': (232, 196, 120), 'bail': (96, 150, 200), 'sector': (90, 170, 150),
    'pin': (200, 90, 80), 'uframe': (130, 160, 210), 'shuttle': (210, 180, 130), 'type': (190, 150, 95),
    'drum': (160, 200, 220), 'hammer': (200, 110, 90), 'carriage': (150, 190, 140), 'paper': (248, 248, 240),
    'ribbon': (40, 40, 60), 'esc': (180, 140, 200), 'grub': (70, 70, 80),
}


@dataclass
class State:
    theta: float = None          # shuttle rotation, deg CCW; None -> position 'pos'
    pos: float = 10.5            # shuttle position (fractional allowed); -1.2 = home
    lift_rows: int = 0
    slide_u: float = 0.0         # retraction of the print unit, u (unit moves -X)
    car: float = P.CAR_X_START   # carriage x offset
    pressed: dict = field(default_factory=dict)   # lever n -> fraction 0..1
    frames: dict = field(default_factory=dict)    # bail name -> travel mm (down)
    tier: int = 0
    hammer: float = 0.0          # 0 cocked, 1 striking
    raised_pin: int = None

    def th(self):
        if self.theta is not None:
            return self.theta
        return (self.pos - (P.NPOS - 1) / 2) * P.STEP_DEG

    def slide(self):
        return self.slide_u * P.U

    def lift(self):
        return self.lift_rows * P.RH


@dataclass
class Part:
    name: str
    group: str
    kind: str
    mesh: object
    color: tuple
    bom: str = None          # part type id for the bill of materials
    mat: str = ''
    note: str = ''
    mov: str = 'fixed'       # motion group for checks
    printable: object = None  # callable -> Manifold laid out for printing (print parts)


def lever_x(n):
    return P.X0_KEYS + n * P.LEVER_PITCH


def pin_x(m):
    return P.X0_KEYS + P.PIN_PITCH * m + P.LEVER_PITCH / 2


# ----------------------------------------------------------------------------------------------- keys
def key_list():
    """(id, label, x_key, y_key, keytop_z, lever_n_or_x, kind) for all keys."""
    keys = []
    for r in range(4):
        for c in range(11):
            n, m = D.key_slot(r, c)
            keys.append(dict(id=f'k{r}{c}', label=D.LEGENDS[r][c], x=lever_x(n), y=P.KEY_ROW_Y[r],
                             top=P.KEYTOP_Z[r], lx=lever_x(n), n=n, r=r, c=c, kind='char', w=P.KEYCAP))
    keys.append(dict(id='space4', label='пробел 4u', x=-50, y=P.SPACE_Y, top=88, lx=lever_x(-1), n=-1, r=4, c=0,
                     kind='space', w=90))
    keys.append(dict(id='space6', label='пробел 6u', x=50, y=P.SPACE_Y, top=88, lx=lever_x(44), n=44, r=4, c=1,
                     kind='space', w=90))
    keys.append(dict(id='shift', label='регистр', x=-127, y=P.KEY_ROW_Y[3], top=P.KEYTOP_Z[3], lx=-127, n=-5, r=3,
                     c=-1, kind='service', w=P.KEYCAP))
    keys.append(dict(id='bksp', label='забой', x=127, y=P.KEY_ROW_Y[0], top=P.KEYTOP_Z[0], lx=124, n=46, r=0, c=11,
                     kind='service', w=P.KEYCAP))
    keys.append(dict(id='back', label='назад на литеру', x=127, y=P.KEY_ROW_Y[1], top=P.KEYTOP_Z[1], lx=130, n=47,
                     r=1, c=11, kind='service', w=P.KEYCAP))
    return keys


def lever_angle(k, frac):
    L = P.LEVER_PIVOT_Y - k['y']
    return math.degrees(math.atan2(P.KEY_TRAVEL * frac, L))


def lever_move(mesh, k, frac):
    """Rotate about the pivot (axis X): front goes down, tail goes up."""
    a = lever_angle(k, frac)
    return rotx(mesh, a, P.LEVER_PIVOT_Y, (P.LEVER_Z0 + P.LEVER_Z1) / 2)


def keyboard(st):
    parts = []
    for k in key_list():
        frac = st.pressed.get(k['n'], 0.0)
        dz = -P.KEY_TRAVEL * frac
        w = k['w']
        cap = cbox(k['x'], k['y'], k['top'] - 4, w, 14 if k['kind'] == 'space' else w, 8).translate((0, 0, dz))
        parts.append(Part(f"cap {k['id']}", 'keys', 'print', cap, COL['key'], 'keycap' if k['kind'] != 'space' else 'spacebar',
                          'PETG', mov=f"key{k['n']}"))
        sx = k['lx']
        stem = zcyl(sx, k['y'], P.LEVER_Z1 + 0.2, k['top'] - 8, 2.0, 16).translate((0, 0, dz))
        if abs(sx - k['x']) > 0.1:
            stem = stem + box(min(sx, k['x']) - 2, max(sx, k['x']) + 2, k['y'] - 2, k['y'] + 2, k['top'] - 11, k['top'] - 8).translate((0, 0, dz))
        parts.append(Part(f"stem {k['id']}", 'keys', 'print', stem, COL['key'], 'keystem', 'PETG', mov=f"key{k['n']}"))
    # key comb: guides the stems
    comb = box(-138, 140, P.KEY_ROW_Y[3] - 10, P.KEY_ROW_Y[0] + 9, *P.COMB_Z)
    holes = [zcyl(k['lx'], k['y'], P.COMB_Z[0] - 1, P.COMB_Z[1] + 1, 2.4, 16) for k in key_list() if k['kind'] != 'space']
    comb = comb - union(holes)
    parts.append(Part('key comb', 'keys', 'print', comb, (110, 112, 120), 'comb', 'PETG',
                      note='печатается тремя частями по 95 мм, стыкуется на винтах'))
    # space bar guide: a second, short comb under the space bars
    sc = box(-120, 120, P.SPACE_Y - 9, P.SPACE_Y + 9, *P.COMB_Z) - union(
        [zcyl(k['lx'], k['y'], P.COMB_Z[0] - 1, P.COMB_Z[1] + 1, 2.4, 16) for k in key_list() if k['kind'] == 'space'])
    parts.append(Part('space comb', 'keys', 'print', sc, (110, 112, 120), 'comb_space', 'PETG'))
    return parts


# --------------------------------------------------------------------------------------------- levers
def lever_mesh(k):
    x = k['lx']; t = P.LEVER_T / 2
    y_front = k['y'] - 4
    zc = (P.LEVER_Z0 + P.LEVER_Z1) / 2
    body = box(x - t, x + t, y_front, P.LEVER_TAIL_Y, P.LEVER_Z0, P.LEVER_Z1)
    body = body - cyl((x - 3, P.LEVER_PIVOT_Y, zc), (x + 3, P.LEVER_PIVOT_Y, zc), 2.15, 16)
    if k['kind'] == 'char' and k['n'] % 2 == 0:
        # deck A: notch under the lift bail (only deck B levers lift the shuttle by one row)
        body = body - box(x - 3, x + 3, -6, 6, P.LEVER_Z1 - 7, P.LEVER_Z1 + 1)
    if k['kind'] == 'char' and k['n'] % 2 == 1:
        body = body + box(x - t, x + t, -2, 2, P.LEVER_Z1, P.LEVER_Z1 + 2)       # lift lug
    if k['kind'] != 'char':
        body = body - box(x - 3, x + 3, 6, P.LEVER_TAIL_Y + 1, P.LEVER_Z1 - 7, P.LEVER_Z1 + 1)  # no pin pusher
    return body


def levers(st):
    parts = []
    for k in key_list():
        frac = st.pressed.get(k['n'], 0.0)
        m = lever_move(lever_mesh(k), k, frac)
        parts.append(Part(f"lever {k['id']}", 'levers', 'print', m, COL['lever'], 'lever', 'PETG',
                          mov=f"key{k['n']}", printable=lambda k=k: lay_flat_x(lever_mesh(k))))
    zc = (P.LEVER_Z0 + P.LEVER_Z1) / 2
    parts.append(Part('lever pivot rod', 'levers', 'buy', cyl((-140, P.LEVER_PIVOT_Y, zc), (140, P.LEVER_PIVOT_Y, zc), 2.0, 16),
                      COL['steel'], 'rod4x280', 'сталь', 'пруток 4 мм, 280 мм'))
    for sx in (-148, 148):
        parts.append(Part(f'pivot bracket {sx:+.0f}', 'levers', 'print',
                          box(sx - 6, sx + 6, P.LEVER_PIVOT_Y - 8, P.LEVER_PIVOT_Y + 8, 20, zc + 6) -
                          cyl((sx - 7, P.LEVER_PIVOT_Y, zc), (sx + 7, P.LEVER_PIVOT_Y, zc), 2.05, 16),
                          (110, 112, 120), 'pivot_bracket', 'PETG'))
    return parts


def lay_flat_x(m):
    """Lay a part whose thin direction is X onto the bed (X -> Z)."""
    m = m.rotate((0, 90, 0))
    b = m.bounding_box()
    return m.translate((-b[0], -b[1], -b[2]))


# --------------------------------------------------------------------------------------- code plates
def bar_y(zone, k, tier=0):
    return zone[0] + 4 + P.BAIL_PITCH * k + P.TIER_SHIFT * tier


def plate_lugs(k):
    """[(bail name, tier, gap mm)] for the code plate of key k."""
    if k['kind'] == 'space':
        w = 4 if k['id'] == 'space4' else 6
        return [('R', t, 0.0) for t in (0, 1)] + [('W', t, P.TP - P.K_STEP * (w - P.W_OFFSET)) for t in (0, 1)]
    if k['kind'] != 'char':
        return []
    out = []
    for tier in (0, 1):
        item = D.ROWS[k['r']][k['c']][tier]
        if item is None:
            continue
        it = D.ITEMS[item]
        if it['kind'] in D.ADV:
            out += [('R', tier, 0.0), ('W', tier, P.TP - P.K_STEP * (it['w'] - P.W_OFFSET)),
                    ('B', tier, P.TP - P.K_STEP * it['b']), ('C', tier, P.TP - P.K_STEP * it['c'])]
        else:
            out.append(('O', tier, 0.0))
            if it.get('below'):
                out.append(('N', tier, 0.0))
    return out


GRUBS = [3, 4, 5, 6, 8, 10, 12, 16, 20, 25]


def grub_length(gap):
    prot = P.BOSS_Z[0] - P.BAIL_Z - gap        # visible length below the boss
    for L in GRUBS:
        if prot + 4 <= L <= prot + (P.BOSS_Z[1] - P.BOSS_Z[0]):
            return L, prot
    return None, prot


def plate_zone(k):
    return P.ZONE_A if k['n'] % 2 == 0 else P.ZONE_B


def plate_mesh(k):
    x = k['lx']; zone = plate_zone(k)
    y0, y1 = zone[0] - 2, zone[1] + 2
    ya = k['y']
    bw = P.BOSS_W / 2; st = P.STRAP_T / 2
    m = box(x - bw, x + bw, y0, y1, *P.BOSS_Z)
    if ya > y1:      # strap back to the key along the lever plane, above the other deck's bosses
        m = m + box(x - st, x + st, y1 - 6, ya + 3, P.BOSS_Z[1] + 2.5, P.LEVER_Z1 - 2)
        m = m + box(x - st, x + st, y1 - 6, y1, P.BOSS_Z[0], P.LEVER_Z1 - 2)
        hook_y = ya
    elif ya < y0:
        m = m + box(x - st, x + st, ya - 3, y0 + 6, P.BOSS_Z[1] + 2.5, P.LEVER_Z1 - 2)
        m = m + box(x - st, x + st, y0, y0 + 6, P.BOSS_Z[0], P.LEVER_Z1 - 2)
        hook_y = ya
    else:
        hook_y = ya
    # hanger: tongue into the lever slot at the key position
    m = m + box(x - st, x + st, hook_y - 3, hook_y + 3, P.BOSS_Z[0], P.LEVER_Z0)
    for bail, tier, gap in plate_lugs(k):
        yb = bar_y(zone, P.BAIL_ORDER.index(bail), tier)
        m = m - zcyl(x, yb, P.BOSS_Z[0] - 1, P.BOSS_Z[1] + 1, 1.25, 12)
    return m


def plates(st):
    parts = []
    for k in key_list():
        lugs = plate_lugs(k)
        if not lugs:
            continue
        dz = -P.TP * st.pressed.get(k['n'], 0.0)
        zone = plate_zone(k)
        parts.append(Part(f"plate {k['id']}", 'plates', 'print', plate_mesh(k).translate((0, 0, dz)), COL['plate'],
                          'code_plate', 'PETG', mov=f"key{k['n']}", printable=lambda k=k: lay_flat_x(plate_mesh(k))))
        for bail, tier, gap in lugs:
            L, prot = grub_length(gap)
            yb = bar_y(zone, P.BAIL_ORDER.index(bail), tier)
            ztip = P.BAIL_Z + gap
            g = zcyl(k['lx'], yb, ztip, ztip + L, 1.5, 12).translate((0, 0, dz))
            parts.append(Part(f"grub {k['id']} {bail}{tier}", 'plates', 'buy', g, COL['grub'], f'grubM3x{L}',
                              'сталь', f'установочный винт М3×{L}, плоский конец', mov=f"key{k['n']}"))
    return parts


# --------------------------------------------------------------------------------------------- bails
def bail_mesh(i):
    xa = 113 + 3 * i
    parts = []
    for zone in (P.ZONE_A, P.ZONE_B):
        yb = bar_y(zone, i)
        parts.append(box(-xa - 1, xa + 1, yb - 1.5, yb + 1.5, P.BAIL_Z - 4, P.BAIL_Z))
    ya = bar_y(P.ZONE_A, i); yb_ = bar_y(P.ZONE_B, i)
    for sx in (-xa, xa):
        parts.append(box(sx - 1, sx + 1, yb_ - 1.5, ya + 1.5, P.BAIL_Z - 4, P.BAIL_Z))
        # guide link lugs (parallelogram links to the side brackets)
        parts.append(box(sx - 1, sx + 1, ya - 3, ya + 1.5, P.BAIL_Z - 10, P.BAIL_Z - 4))
        parts.append(box(sx - 1, sx + 1, yb_ - 1.5, yb_ + 3, P.BAIL_Z - 10, P.BAIL_Z - 4))
    return union(parts)


def bails(st):
    parts = []
    for i, name in enumerate(P.BAIL_ORDER):
        dz = -st.frames.get(name, 0.0); dy = P.TIER_SHIFT * st.tier
        parts.append(Part(f'bail {name}', 'bails', 'print', bail_mesh(i).translate((0, dy, dz)), COL['bail'],
                          f'bail_{name}', 'PETG', note='рамка из двух планок и боковин; планки — печать, стыки на винтах',
                          mov=f'bail{name}'))
    # side brackets that carry the parallelogram links
    for sx in (-138, 138):
        b = box(sx - 4, sx + 4, P.ZONE_B[0] - 4, P.ZONE_A[1] + 4, 0, 8)
        parts.append(Part(f'bail bracket {sx:+.0f}', 'bails', 'print', b, (110, 112, 120), 'bail_bracket', 'PETG'))
    return parts


# ------------------------------------------------------------------------------------ memory sectors
SECT_SHAFT = (-338.0, 50.0)      # (y, z), axis along X


def sectors(st):
    parts = []
    y0, z0 = SECT_SHAFT
    parts.append(Part('sector shaft', 'sectors', 'buy', cyl((150, y0, z0), (180, y0, z0), 2.0, 16), COL['steel'],
                      'rod4x40', 'сталь'))
    for j, (name, n) in enumerate((('B', 10), ('C', 10), ('W', 13))):
        x = 156 + 7 * j
        ang = 3.6 * st.frames.get(name, 0.0)
        # sector plate in the YZ plane: teeth on an arc of radius 42 above the shaft
        pts = []
        for i in range(n * 2 + 1):
            a = math.radians(-22 + 44 * i / (n * 2))
            r = 42 if i % 2 == 0 else 39.5
            pts.append((y0 + r * math.sin(a), z0 + r * math.cos(a)))
        pts += [(y0 + 8 * math.sin(math.radians(22)), z0 - 2), (y0 - 8 * math.sin(math.radians(22)), z0 - 2)]
        cs = geo.CrossSection([geo._ccw(pts)])
        plate = cs.extrude(4).rotate((0, 90, 0))   # XY->YZ with x thickness
        # rotate((0,90,0)) maps (x,y,z)->(z,y,-x): profile (y,z) is in local (x,y) -> need remap
        prof = geo.CrossSection([geo._ccw([(p[0], p[1]) for p in pts])])
        m = prof.extrude(4)                         # local x=y_world, y=z_world, z=thickness
        M = np.array([[0, 0, 1, x - 2], [1, 0, 0, 0], [0, 1, 0, 0]], float)
        m = m.transform(M)
        m = m - cyl((x - 3, y0, z0), (x + 3, y0, z0), 2.1, 16)
        # arm to the bail link at r = 15
        m = m + box(x - 2, x + 2, y0 - 2, y0 + 2, z0 - 16, z0)
        m = rotx(m, ang, y0, z0)
        parts.append(Part(f'sector {name}', 'sectors', 'print', m, COL['sector'], f'sector_{name}', 'PETG',
                          mov=f'bail{name}'))
        parts.append(Part(f'latch {name}', 'sectors', 'print',
                          box(x - 2, x + 2, y0 - 3, y0 + 3, z0 + 43, z0 + 56), COL['sector'], 'latch', 'PETG'))
    parts.append(Part('sector bracket', 'sectors', 'print',
                      box(150, 182, y0 - 8, y0 + 8, 20, z0 - 4) + box(150, 154, y0 - 8, y0 + 8, z0 - 4, z0 + 60) +
                      box(150, 182, y0 - 8, y0 + 8, z0 + 56, z0 + 60) - cyl((149, y0, z0), (183, y0, z0), 2.1, 16),
                      (110, 112, 120), 'sector_bracket', 'PETG'))
    return parts


# -------------------------------------------------------------------------------------------- frame
def frame(st):
    parts = []
    X, Y0, Y1, E = P.FRAME_X, P.FRAME_Y0, P.FRAME_Y1, P.EXT
    def ext(name, m, L):
        parts.append(Part(name, 'frame', 'cut', m, COL['frame'], f'2020x{int(round(L))}', 'алюминий',
                          f'профиль 2020, {int(round(L))} мм'))
    ext('frame front', box(-X, X, Y0, Y0 + E, 0, E), 2 * X)
    ext('frame back', box(-X, X, Y1 - E, Y1, 0, E), 2 * X)
    for sx in (-1, 1):
        ext(f'frame side {sx:+d}', box(sx * X - E if sx > 0 else -X, sx * X if sx > 0 else -X + E, Y0 + E, Y1 - E, 0, E), Y1 - Y0 - 2 * E)
    for yr in P.RAIL_Y:
        for sx in (-1, 1):
            x0 = X - E if sx > 0 else -X
            ext(f'beam post {yr:.0f} {sx:+d}', box(x0, x0 + E, yr - E / 2, yr + E / 2, E, P.RAIL_Z - E), P.RAIL_Z - 2 * E)
        ext(f'beam {yr:.0f}', box(-X + E, X - E, yr - E / 2, yr + E / 2, P.RAIL_Z - E, P.RAIL_Z), 2 * X - 2 * E)
        parts.append(Part(f'rail MGN12 {yr:.0f}', 'frame', 'buy', box(-150, 150, yr - 6, yr + 6, P.RAIL_Z, P.RAIL_Z + 8),
                          COL['buy'], 'MGN12_300', 'сталь', 'линейная направляющая MGN12, 300 мм'))
    for (yy, zz), nm in ((P.CAR_RAIL_LO, 'lo'), (P.CAR_RAIL_HI, 'hi')):
        for sx in (-1, 1):
            x0 = X - E if sx > 0 else -X
            ext(f'carriage post {nm} {sx:+d}', box(x0, x0 + E, yy - E / 2, yy + E / 2, E, zz + 10), zz + 10 - E)
        parts.append(Part(f'carriage rod {nm}', 'frame', 'buy', cyl((-X + E, yy, zz), (X - E, yy, zz), 4.0, 24),
                          COL['steel'], 'rod8x460', 'сталь', 'калиброванный пруток 8 мм, 460 мм'))
    # inner cross member under the lever pivot brackets
    ext('frame cross pivot', box(-X + E, X - E, P.LEVER_PIVOT_Y - E / 2, P.LEVER_PIVOT_Y + E / 2, 0, E), 2 * X - 2 * E)
    # ribbon spool posts on the rear beam
    for sx in (-1, 1):
        parts.append(Part(f'ribbon post {sx:+d}', 'frame', 'print', box(sx * 140 - 4, sx * 140 + 4, -24, -16, P.RAIL_Z, 158),
                          (110, 112, 120), 'ribbon_post', 'PETG'))
    return parts


# ------------------------------------------------------------------------------- fixed pin pushers
def pushers(st):
    parts = []
    tail = P.LEVER_TAIL_Y
    for m in range(P.NPOS):
        x = pin_x(m)
        n0, n1 = 2 * m, 2 * m + 1
        ks = {k['n']: k for k in key_list()}
        rise = 0.0
        for n in (n0, n1):
            f = st.pressed.get(n, 0.0)
            if f:
                k = ks[n]; a = math.radians(lever_angle(k, f))
                rise = max(rise, (tail - 3 - P.LEVER_PIVOT_Y) * math.tan(a))
        rise = min(rise, 5.0)   # pins have a hard stop; the rest is taken by the spring in the pusher
        pz = P.LEVER_Z1 + 0.3 + rise
        b = box(x - 4, x + 4, tail - 7, tail - 1, pz, pz + 2.5)
        rod = zcyl(x, tail - 4 - 0, pz + 2.5, 92.5 + rise, 1.5, 12)
        parts.append(Part(f'pusher {m}', 'pins', 'print', b, COL['pin'], 'pusher', 'PETG', mov=f'pin{m}'))
        parts.append(Part(f'push rod {m}', 'pins', 'buy', rod, COL['steel'], 'rod3x30', 'сталь', 'пруток 3 мм', mov=f'pin{m}'))
    comb = box(-112, 112, tail - 10, tail + 2, 78, 81) - union(
        [zcyl(pin_x(m), tail - 4, 77, 82, 1.8, 12) for m in range(P.NPOS)])
    parts.append(Part('pusher comb', 'pins', 'print', comb, (110, 112, 120), 'pusher_comb', 'PETG'))
    for sx in (-118, 118):
        parts.append(Part(f'pusher comb post {sx:+.0f}', 'pins', 'print', box(sx - 4, sx + 4, tail - 10, tail + 2, 20, 81),
                          (110, 112, 120), 'pusher_post', 'PETG'))
    # lift bail above the tails (deck B levers carry lugs)
    parts.append(Part('lift bail', 'pins', 'print', box(-112, -96 + 4.75 * 43 + 8, -3, 3, P.LEVER_Z1 + 2.5, P.LEVER_Z1 + 5.5),
                      (110, 112, 120), 'lift_bail', 'PETG', mov='lift'))
    return parts


# --------------------------------------------------------------------------------------- the U-frame
Y_BAND = P.AXIS_Y + P.DRUM_R                   # straight run leaves the drum here (back tangent)
Y_RET = Y_BAND + 2 * P.PULLEY_R                # return run with the stop slider
Y_PINS = Y_RET + 8.5
X_PULLEY = 121.0
Z_B0 = P.UF_Z + P.UF_T                         # top of the U-frame base


def slider_x(th_deg):
    """Stop slider x (centre of the contact face) for shuttle rotation th (deg CCW)."""
    return P.DRUM_R * math.radians(th_deg)


def uframe(st):
    parts = []; dx = -st.slide()
    T = lambda m: m.translate((dx, 0, 0))
    base = box(-128, 128, -165, 22, P.UF_Z, Z_B0)
    base = base - zcyl(0, P.AXIS_Y, P.UF_Z - 1, Z_B0 + 1, 11.05, 32)
    for m in range(P.NPOS):
        base = base - zcyl(pin_x(m), Y_PINS, P.UF_Z - 1, Z_B0 + 1, 1.6, 12)
    # rear drop to the arm and the arm with the hammer post
    arm = box(-12, 12, 16, 22, P.ARM_Z0, P.UF_Z) + box(-12, 12, 16, P.POST_Y[1], P.ARM_Z0, P.ARM_Z1)
    post = box(-8, 8, *P.POST_Y, P.ARM_Z1, P.HAMMER_PIVOT[1] + 7)
    post = post - cyl((-9, P.HAMMER_PIVOT[0], P.HAMMER_PIVOT[1]), (9, P.HAMMER_PIVOT[0], P.HAMMER_PIVOT[1]), 2.05, 16)
    post = post - box(-4.5, 4.5, P.POST_Y[0] - 1, P.POST_Y[1] + 1, P.HAMMER_PIVOT[1] - 8, P.HAMMER_PIVOT[1] + 8)
    parts.append(Part('U-frame base', 'uframe', 'print', T(base), COL['uframe'], 'uframe_base', 'PETG',
                      note='печатается двумя половинами 128×187, стягивается винтами М4 и профилем снизу',
                      mov='uframe'))
    parts.append(Part('U-frame arm and hammer post', 'uframe', 'print', T(arm + post), COL['uframe'], 'uframe_arm', 'PETG',
                      mov='uframe'))
    for yr in P.RAIL_Y:
        for sx in (-60, 60):
            parts.append(Part(f'MGN12H block {yr:.0f} {sx:+d}', 'uframe', 'buy',
                              T(box(sx - 13.5, sx + 13.5, yr - 13.5, yr + 13.5, P.RAIL_Z + 3, P.UF_Z)), COL['buy'],
                              'MGN12H', 'сталь', 'каретка MGN12H', mov='uframe'))
    # shaft tower with two 608 bearings
    tower = zcyl(0, P.AXIS_Y, 76, P.UF_Z, 16, 48) - zcyl(0, P.AXIS_Y, 75, P.UF_Z + 1, 11.05, 32)
    tower = tower + zcyl(0, P.AXIS_Y, 76, 79, 16, 48)
    tower = tower - zcyl(0, P.AXIS_Y, 75, 80, 4.5, 24)
    parts.append(Part('shaft tower', 'uframe', 'print', T(tower), COL['uframe'], 'tower', 'PETG', mov='uframe'))
    for z in (80.0, P.UF_Z - 1):
        parts.append(Part(f'bearing 608 z{z:.0f}', 'uframe', 'buy', T(zcyl(0, P.AXIS_Y, z, z + 7, 11, 32) - zcyl(0, P.AXIS_Y, z - 1, z + 8, 4.02, 24)),
                          COL['buy'], '608', 'сталь', 'подшипник 608 (8×22×7)', mov='uframe'))
    # stop rail, slider with finger, pins block, pulley
    parts.append(Part('stop rail MGN9', 'uframe', 'buy', T(box(-125, 125, Y_RET - 4.5, Y_RET + 4.5, Z_B0, Z_B0 + 6.5)),
                      COL['buy'], 'MGN9_250', 'сталь', 'линейная направляющая MGN9, 250 мм', mov='uframe'))
    xs = slider_x(st.th())
    sl = box(xs - 15, xs + 5, Y_RET - 10, Y_RET + 10, Z_B0 + 1.5, Z_B0 + 9.5)          # MGN9H block (left of the face)
    parts.append(Part('stop slider MGN9H', 'uframe', 'buy', T(sl), COL['buy'], 'MGN9H', 'сталь', 'каретка MGN9H',
                      mov='slider'))
    finger = box(xs - 8, xs, Y_RET + 3, Y_PINS + 3, P.Z_BAND - 2, P.Z_BAND + 2) + box(xs - 15, xs - 5, Y_RET - 2, Y_RET + 10, Z_B0 + 9.5, P.Z_BAND - 2)
    parts.append(Part('stop finger', 'uframe', 'print', T(finger), COL['pin'], 'finger', 'PETG',
                      note='держатель ленты и упорный палец', mov='slider'))
    pb = box(-110, 110, Y_PINS - 3, Y_PINS + 3, Z_B0, Z_B0 + 4)
    pb = pb - union([zcyl(pin_x(m), Y_PINS, Z_B0 - 1, Z_B0 + 5, 1.55, 12) for m in range(P.NPOS)])
    parts.append(Part('pins block', 'uframe', 'print', T(pb), COL['uframe'], 'pins_block', 'PETG', mov='uframe'))
    for m in range(P.NPOS):
        up = 5.0 if st.raised_pin == m else 0.0
        z0 = P.Z_BAND - 2 - 1 - 20 + up      # pin top 1 mm under the finger at rest
        parts.append(Part(f'stop pin {m}', 'uframe', 'buy', T(zcyl(pin_x(m), Y_PINS, z0, z0 + 20, 1.5, 12)), COL['pin'],
                          'dowel3x20', 'сталь', 'штифт цилиндрический 3×20', mov=f'pin{m}'))
    pul = zcyl(X_PULLEY, (Y_BAND + Y_RET) / 2, P.Z_BAND - 4, P.Z_BAND + 4, P.PULLEY_R - 0.05, 32)
    parts.append(Part('band pulley', 'uframe', 'buy', T(pul), COL['buy'], 'pulley625', 'сталь',
                      'подшипник 625 с печатной ребордой', mov='uframe'))
    parts.append(Part('pulley post', 'uframe', 'print', T(zcyl(X_PULLEY, (Y_BAND + Y_RET) / 2, Z_B0, P.Z_BAND - 4, 4, 24)),
                      COL['uframe'], 'pulley_post', 'PETG', mov='uframe'))
    # band: straight run, wrap and return (0.1 mm steel strip shown 0.4 thick)
    band = box(0, X_PULLEY, Y_BAND, Y_BAND + 0.4, P.Z_BAND - 3, P.Z_BAND + 3) + \
        box(xs, X_PULLEY, Y_RET - 0.4, Y_RET, P.Z_BAND - 3, P.Z_BAND + 3)
    parts.append(Part('band', 'uframe', 'buy', T(band), (60, 60, 70), 'band', 'сталь',
                      'стальная лента 6×0,1 мм (щуп/пружинная лента)', mov='band'))
    # lift fork pivoted at the left, under the shuttle hub
    lz = st.lift()
    fork = fork_mesh()
    ang = math.degrees(math.atan2(lz, 150.0))
    fork = geo.roty(fork, -ang, -150, 124)
    parts.append(Part('lift fork', 'uframe', 'print', T(fork), COL['uframe'], 'lift_fork', 'PETG', mov='lift'))
    parts.append(Part('lift fork bracket', 'uframe', 'print',
                      T(box(-156, -144, P.AXIS_Y - 8, P.AXIS_Y + 8, Z_B0, 128) - cyl((-157, P.AXIS_Y, 124), (-143, P.AXIS_Y, 124), 2.05, 16)
                        + box(-156, -128, P.AXIS_Y - 8, P.AXIS_Y + 8, P.UF_Z, Z_B0)),
                      COL['uframe'], 'fork_bracket', 'PETG', mov='uframe'))
    # hammer
    parts += hammer(st, dx)
    return parts


def fork_mesh():
    z0, z1 = P.BLOCK_BOT - 6 - 6, P.BLOCK_BOT - 6 - 2
    arm = box(-150, -16, P.AXIS_Y - 4, P.AXIS_Y + 4, z0, z1)
    ringp = zcyl(0, P.AXIS_Y, z0, z1, 19, 48) - zcyl(0, P.AXIS_Y, z0 - 1, z1 + 1, 7, 32)
    ringp = ringp - box(0, 30, P.AXIS_Y - 30, P.AXIS_Y + 30, z0 - 1, z1 + 1)   # open fork toward +X
    piv = box(-154, -146, P.AXIS_Y - 6, P.AXIS_Y + 6, z0 - 2, 128) - cyl((-155, P.AXIS_Y, 124), (-145, P.AXIS_Y, 124), 2.05, 16)
    return arm + ringp + piv


def hammer_mesh():
    yp, zp = P.HAMMER_PIVOT
    x0, x1 = P.BLOCK_U0 * P.U, P.BLOCK_U1 * P.U
    head = box(x0, x1, 0.15, 7, P.ZP - 5.0, P.ZP + 5.4)
    arm = cyl((4, yp, zp), (4, 5, P.ZP), 3.2, 16)
    hub = cyl((-4, yp, zp), (4 + 0, yp, zp), 6, 24).translate((0, 0, 0))
    hub = cyl((-4.2, yp, zp), (4.2, yp, zp), 6.5, 24) - cyl((-5, yp, zp), (5, yp, zp), 2.05, 16)
    arm = cyl((0, yp, zp), (4, 6, P.ZP), 3.0, 16)
    return head + arm + hub


def hammer(st, dx):
    yp, zp = P.HAMMER_PIVOT
    ang = -18.0 * (1 - st.hammer)       # cocked: swung back
    h = rotx(hammer_mesh(), -ang, yp, zp).translate((dx, 0, 0))
    return [Part('hammer', 'hammer', 'print', h, COL['hammer'], 'hammer', 'PETG',
                 note='боёк с накладкой из резины 1 мм', mov='hammer'),
            Part('hammer axle', 'hammer', 'buy', cyl((-12 + dx, yp, zp), (12 + dx, yp, zp), 2.0, 16), COL['steel'],
                 'rod4x24', 'сталь', mov='uframe')]


# ---------------------------------------------------------------------------------------- shuttle
def drum_mesh():
    z0, z1 = P.Z_BAND - 3, P.Z_BAND + 3
    rim = geo.sector_xy(0, P.AXIS_Y, P.DRUM_R - 3, P.DRUM_R, -66, 66, z0, z1)
    web = geo.sector_xy(0, P.AXIS_Y, 0, P.DRUM_R - 2, -66, 66, z0, z0 + 3) + zcyl(0, P.AXIS_Y, z0, z0 + 3, 70, 64)
    hub = zcyl(0, P.AXIS_Y, Z_B0 + 1, z1, 14, 48)
    rod_boss = zcyl(0, P.AXIS_Y + 60, z0, z1, 5, 24)
    m = rim + web + hub + rod_boss
    m = m - zcyl(0, P.AXIS_Y, Z_B0, z1 + 1, 4.02, 24) - zcyl(0, P.AXIS_Y + 60, z0 + 1, z1 + 1, 3.0, 16)
    # lightening windows
    for a in (-40, 0, 40):
        m = m - geo.sector_xy(0, P.AXIS_Y, 74, P.DRUM_R - 6, a - 14, a + 14, z0 - 1, z1 + 1)
    return m


def ring_mesh():
    lo = min(-TB.home_angle(m) + math.degrees(math.atan2(P.BLOCK_U0 * P.U, P.R_FACE)) for m in range(P.NPOS))
    hi = max(-TB.home_angle(m) + math.degrees(math.atan2(P.BLOCK_U1 * P.U, P.R_FACE)) for m in range(P.NPOS))
    z0, z1 = P.BLOCK_BOT - 3, P.BLOCK_TOP + 2
    ring = geo.sector_xy(0, P.AXIS_Y, P.RING_R0, P.RING_R1, lo - 1.5, hi + 1.5, z0, z1)
    # pockets for the blocks (bodies grown 0.15 mm)
    pockets = union([TB.block_home(m, with_relief=False) for m in range(P.NPOS)])
    ring = ring - pockets
    # radial screw holes for the adjusting screws
    for m in range(P.NPOS):
        a = TB.home_angle(m)
        xc = (P.BLOCK_U0 + P.BLOCK_U1) / 2 * P.U
        h = cyl((xc, P.AXIS_Y + P.RING_R0 - 1, (z0 + z1) / 2), (xc, P.AXIS_Y + P.RING_R1 + 1, (z0 + z1) / 2), 1.6, 12)
        ring = ring - rotz(h, a, 0, P.AXIS_Y)
    web = zcyl(0, P.AXIS_Y, z0, z0 + 4, 70, 64)
    spokes = union([geo.sector_xy(0, P.AXIS_Y, 60, P.RING_R0 + 1, a - 6, a + 6, z0, z0 + 4) for a in (lo + 8, (lo + hi) / 2, hi - 8)])
    hub = zcyl(0, P.AXIS_Y, z0 - 3, z0 + 11, 13, 48)
    boss = zcyl(0, P.AXIS_Y + 60, z0 - 3, z0 + 11, 6, 24)
    m = ring + web + spokes + hub + boss
    m = m - zcyl(0, P.AXIS_Y, z0 - 4, z0 + 12, 4.1, 24) - zcyl(0, P.AXIS_Y + 60, z0 - 4, z0 + 12, 3.1, 16)
    for a in (-60, 0, 60, 180, 120, -120):
        m = m - geo.sector_xy(0, P.AXIS_Y, 22, 52, a - 20, a + 20, z0 - 1, z0 + 5)
    return m


_cache = {}


def cached(name, fn):
    if name not in _cache:
        _cache[name] = fn()
    return _cache[name]


def shuttle(st):
    parts = []; th = st.th(); dx = -st.slide(); lz = st.lift()
    def T(m, lift=True):
        m = rotz(m, th, 0, P.AXIS_Y)
        return m.translate((dx, 0, lz if lift else 0))
    parts.append(Part('shuttle', 'shuttle', 'print', T(cached('ring', ring_mesh)), COL['shuttle'], 'shuttle', 'PETG',
                      note='кольцо 118°, R 107; хорда около 190 мм — помещается на стол 220×220', mov='shuttle',
                      printable=lambda: cached('ring', ring_mesh)))
    for m in range(P.NPOS):
        parts.append(Part(f'type block {m}', 'shuttle', 'print', T(cached(f'blk{m}', lambda m=m: TB.block_home(m))),
                          COL['type'], f'type_block_{m:02d}', 'PETG', note='литерный блок: 4 литеры, лицом вверх, слой 0,1',
                          mov='shuttle', printable=lambda m=m: TB.block_print_bed(m)))
    parts.append(Part('drum', 'shuttle', 'print', T(cached('drum', drum_mesh), lift=False), COL['drum'], 'drum', 'PETG',
                      note='барабан ленты R 101,1; сектор 132°', mov='drum', printable=lambda: cached('drum', drum_mesh)))
    parts.append(Part('shaft', 'shuttle', 'buy', T(zcyl(0, P.AXIS_Y, 80, 198, 4.0, 24), lift=False), COL['steel'],
                      'shaft8x120', 'сталь', 'вал 8 мм, 120 мм, с лыской', mov='drum'))
    parts.append(Part('guide rod', 'shuttle', 'buy',
                      T(zcyl(0, P.AXIS_Y + 60, P.Z_BAND - 2, 200, 2.95, 16), lift=False), COL['steel'], 'rod6x85', 'сталь',
                      'пруток 6 мм, 85 мм — поводок челнока', mov='drum'))
    parts.append(Part('shuttle bushing', 'shuttle', 'buy',
                      T(zcyl(0, P.AXIS_Y + 60, P.BLOCK_BOT - 6, P.BLOCK_BOT + 8, 4.5, 24) - zcyl(0, P.AXIS_Y + 60, P.BLOCK_BOT - 7, P.BLOCK_BOT + 9, 3.0, 16)),
                      COL['buy'], 'bushing6', 'бронза', 'втулка 6×9×14 с поджимом', mov='shuttle'))
    return parts


# --------------------------------------------------------------------------------------- carriage
def end_plate_profile():
    yl, zl = P.CAR_RAIL_LO; yh, zh = P.CAR_RAIL_HI
    return [(24, zl - 8), (yh + 12, zl - 8), (yh + 12, zh + 12), (yh - 10, zh + 25), (-6, zh + 25),
            (-6, P.ROLLER[1] - 8), (0, P.ROLLER[1] - 12), (0, 145), (24, 135)]


def carriage(st):
    parts = []; xc = st.car
    yl, zl = P.CAR_RAIL_LO; yh, zh = P.CAR_RAIL_HI
    prof = geo.CrossSection([geo._ccw(end_plate_profile())])
    for sx in (-1, 1):
        x = xc + sx * P.CAR_HALF
        m = prof.extrude(6).transform(np.array([[0, 0, 1, x - 3], [1, 0, 0, 0], [0, 1, 0, 0]], float))
        m = m - cyl((x - 4, yl, zl), (x + 4, yl, zl), 4.2, 24) - cyl((x - 4, yh, zh), (x + 4, yh, zh), 4.2, 24)
        parts.append(Part(f'carriage end plate {sx:+d}', 'carriage', 'print', m, COL['carriage'], 'car_end', 'PETG',
                          mov='carriage'))
        for (yy, zz) in ((yl, zl), (yh, zh)):
            bb = cyl((x - 15 * sx - 3 * sx, yy, zz), (x - 3 * sx, yy, zz), 7, 24) - cyl((x - 20 * sx, yy, zz), (x, yy, zz), 4.05, 24)
            parts.append(Part(f'carriage bushing {sx:+d} {zz:.0f}', 'carriage', 'buy', bb, COL['buy'], 'LM8UU', 'сталь',
                              'линейный подшипник LM8UU', mov='carriage'))
    ty, tz, tr = P.TUBE
    tube = cyl((xc - P.CAR_HALF + 3, ty, tz), (xc + P.CAR_HALF - 3, ty, tz), tr, 48) - \
        cyl((xc - P.CAR_HALF + 2, ty, tz), (xc + P.CAR_HALF - 2, ty, tz), tr - 1.5, 48)
    tube = tube - box(xc - 110, xc + 110, ty - 15, ty - 3, tz + 8, tz + 20)     # paper slot (front top)
    parts.append(Part('paper tube', 'carriage', 'cut', tube, COL['carriage'], 'pipe32x230', 'ПВХ',
                      'труба 30 мм (ПВХ или печать), 230 мм, с прорезью', mov='carriage'))
    guide = union([cyl((xc - 110, 24 - 23 * t, 135 + 15 * t), (xc + 110, 24 - 23 * t, 135 + 15 * t), 0.8, 8)
                   for t in np.linspace(0, 1, 9)])
    guide = geo.Manifold.batch_hull([cyl((xc - 110, 24, 135), (xc + 110, 24, 135), 0.8, 8),
                                     cyl((xc - 110, 1.0, 150), (xc + 110, 1.0, 150), 0.8, 8)])
    parts.append(Part('paper guide', 'carriage', 'cut', guide, COL['carriage'], 'guide_sheet', 'жесть',
                      'направляющая бумаги — полоса 0,5 мм', mov='carriage'))
    ry, rz, rr = P.ROLLER
    parts.append(Part('feed roller', 'carriage', 'buy', cyl((xc - P.CAR_HALF + 3, ry, rz), (xc + P.CAR_HALF - 3, ry, rz), rr, 32),
                      (60, 60, 60), 'roller14', 'сталь+резина', 'вал 6 мм с резиновой трубкой 14 мм', mov='carriage'))
    for sx in (-1, 1):
        parts.append(Part(f'pinch roller {sx:+d}', 'carriage', 'buy',
                          cyl((xc + sx * 80 - 6, -3.6, rz), (xc + sx * 80 + 6, -3.6, rz), 3.5, 24), (60, 60, 60), 'pinch7', 'резина',
                          'прижимной ролик 7 мм', mov='carriage'))
    # rack along the back, teeth toward +Y
    rack_y = 110.0
    teeth = []
    pitch = math.pi * 1.0106
    for i in range(int(230 / pitch)):
        x = xc - 115 + i * pitch
        teeth.append(geo.CrossSection([geo._ccw([(x, rack_y - 1.25), (x + pitch * 0.5, rack_y - 1.25),
                                                 (x + pitch * 0.38, rack_y + 1.0), (x + pitch * 0.12, rack_y + 1.0)])]))
    rack = box(xc - 115, xc + 115, rack_y - 7, rack_y - 1.2, P.CAR_RAIL_LO[1] - 2, P.CAR_RAIL_LO[1] + 4)
    rack = rack + geo.CrossSection.batch_boolean(teeth, geo.__dict__['__builtins__']['__import__']('manifold3d').OpType.Add).extrude(6).translate((0, 0, P.CAR_RAIL_LO[1] - 2))
    rack = rack + box(xc - P.CAR_HALF - 3, xc - 115, P.CAR_RAIL_HI[0] + 6, rack_y - 1.2, P.CAR_RAIL_LO[1] - 2, P.CAR_RAIL_LO[1] + 4)
    rack = rack + box(xc + 115, xc + P.CAR_HALF + 3, P.CAR_RAIL_HI[0] + 6, rack_y - 1.2, P.CAR_RAIL_LO[1] - 2, P.CAR_RAIL_LO[1] + 4)
    parts.append(Part('carriage rack', 'carriage', 'print', rack, COL['carriage'], 'rack', 'PETG',
                      note='модуль 1,0106 мм; печатается двумя частями', mov='carriage'))
    # paper: from the guide up past the print line, over the roller onto the rest
    pap = box(xc - 108, xc + 108, 0.0, 0.1, 150, rz)
    pap = pap + box(xc - 108, xc + 108, ry - 0.05, ry + 0.05, rz + rr, rz + rr + 0.1)
    rest = rotx(box(xc - 108, xc + 108, ry, ry + 90, rz + rr, rz + rr + 0.1), 25, ry, rz + rr)
    parts.append(Part('paper', 'paper', 'ref', pap + rest, COL['paper'], None, mov='carriage'))
    parts.append(Part('paper rest', 'carriage', 'print', rotx(box(xc - 100, xc + 100, ry + 6, ry + 80, rz + rr - 2.5, rz + rr - 0.5), 25, ry, rz + rr),
                      COL['carriage'], 'paper_rest', 'PETG', mov='carriage'))
    return parts


# ------------------------------------------------------------------------------------- escapement
ESC = (0.0, 116.05)       # pinion axis (x, y): rack pitch line at y = 110 (+ pitch radius 5.05)


def escapement(st):
    parts = []
    x, y = ESC
    zr = P.CAR_RAIL_LO[1]
    pin = geo.gear_profile(10, 1.0106, x, y).extrude(6).translate((0, 0, zr - 2))
    wheel = geo.ratchet_profile(60, 18.0, 20.5, x, y).extrude(5).translate((0, 0, 66))
    m = pin + wheel + zcyl(x, y, 66, zr - 2, 6, 24)
    m = m - zcyl(x, y, 20, 120, 2.05, 16)
    rot = -math.degrees((st.car - P.CAR_X_START) / 5.053)
    m = rotz(m, rot, x, y)
    parts.append(Part('escapement wheel and pinion', 'esc', 'print', m, COL['esc'], 'esc_wheel', 'PETG',
                      note='колесо 60 зубьев и шестерня z = 10 одной деталью', mov='esc'))
    parts.append(Part('escapement shaft', 'esc', 'buy', zcyl(x, y, 20, zr + 8, 2.0, 16), COL['steel'], 'rod4x80', 'сталь'))
    br = box(x - 12, x + 12, y + 10, y + 14, 20, zr + 10) + box(x - 12, x + 12, y - 4, y + 14, zr + 6, zr + 10)
    br = br + box(x - 12, x + 12, y - 4, y + 14, 50, 54) - zcyl(x, y, 19, 121, 2.1, 16)
    parts.append(Part('escapement bracket', 'esc', 'print', br, (110, 112, 120), 'esc_bracket', 'PETG'))
    # holding dog and movable stop (schematic)
    parts.append(Part('escapement dog', 'esc', 'print', box(x + 21, x + 31, y - 2, y + 2, 66, 71), COL['esc'], 'esc_dog', 'PETG'))
    parts.append(Part('escapement stop', 'esc', 'print', box(x - 31, x - 21, y - 2, y + 2, 66, 71), COL['esc'], 'esc_stop', 'PETG'))
    return parts


# ----------------------------------------------------------------------------------------- ribbon
def ribbon(st):
    parts = []
    for sx in (-1, 1):
        parts.append(Part(f'ribbon spool {sx:+d}', 'ribbon', 'buy', zcyl(sx * 140, -20, 158, 172, 16, 48), (50, 50, 60), 'spool',
                          'пластик', 'катушка ленты 13 мм'))
    strip = box(-128, 128, -0.95, -0.85, P.ZP - 6.5, P.ZP + 6.5)
    parts.append(Part('ribbon', 'ribbon', 'ref', strip, COL['ribbon'], None))
    for sx in (-1, 1):
        parts.append(Part(f'ribbon guide {sx:+d}', 'ribbon', 'print', box(sx * 128 - 2, sx * 128 + 2, -20, -0.5, P.ZP - 8, P.ZP + 8)
                          + box(sx * 128 - 2, sx * 128 + 2, -20, -16, P.RAIL_Z, P.ZP - 8),
                          (110, 112, 120), 'ribbon_guide', 'PETG'))
    return parts


def build(st):
    out = []
    for fn in (frame, keyboard, levers, plates, bails, sectors, pushers, uframe, shuttle, carriage, escapement, ribbon):
        out += fn(st)
    return out
