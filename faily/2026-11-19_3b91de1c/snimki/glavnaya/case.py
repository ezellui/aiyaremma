"""rev. 0.12: the case of TPM-2 -- a Noldorin shell around the mechanism.

The shell is a low body on the frame: four walls, a keyboard deck stepped down in front, two towers flanking the
keys, a top deck around the print unit (the court over the shuttle and the pit of the carriage stay open: the typist
sees the shuttle and the sheet as before) and two pillars over the carriage posts. Ornament (all geometric, after
the Noldorin devices: eight- and sixteen-rayed stars, round-headed niches, lozenge chains):
  * walls: a silver plinth band and cornice, an arcade of niches with a star in each (one niche takes the carriage
    release key, one the winding crank's shaft);
  * fascia behind the keys: the inscription in tengwar, set as the machine itself types it (Alcarin, the page's
    transcriber, the machine's own advances), enlarged 1.55 times;
  * the left tower: the owner's device (Mirë Nolmeo, v12) as an inlaid plaque; the right one: a pierced star over
    the spring barrel;
  * the pillars: fluted, with silver bases, capitals and sixteen-rayed star finials.
Every part is in group 'case' and fixed; ornament on a panel is a separate part of kind 'inlay' (silver: printed with
the panel by one filament change at the panel's face, everything above the face is silver), the device's colours are
inlays of the plaque (multi-colour print, one STL per colour with a common origin, see build.py).
Clearances are not designed by hand only: the model's checks run the case against every motion (scenarios.py)."""
import os, json, math
import numpy as np
from shapely.geometry import Polygon, Point, MultiPolygon, box as sbox
from shapely.ops import unary_union
from shapely import affinity
from manifold3d import Manifold
import params as P
import geo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

BODY = (34, 52, 104)          # lapis
SILVER = (206, 212, 222)
PILLAR = (40, 60, 116)

# ------------------------------------------------------------------ main dimensions (mm, machine frame)
T = 4.0                        # wall thickness
XO = 265.0                     # outer face of the side walls (the frame is +-250; the winding gears reach 260)
XI = XO - T
YF = -401.0                    # outer face of the front wall (the frame front is at -395; the release key at -402)
YFI = YF + T
YB0 = 131.0                    # inner face of the back wall (frame back at 130)
YB = YB0 + T
ZK = 78.0                      # top of the keyboard deck (key caps 82..96 at rest)
ZT = 140.0                     # top of the body (the motor's pinion reaches 135)
TD = 3.0                       # deck thickness
YT = -365.0                    # front face of the towers
XT = 139.0                     # inner faces of the towers (key caps reach +-135.5)
YFA = -236.0                   # front face of the fascia (top row of caps ends at -241.5)
COURT = (192.0, -170.0, -10.0)  # open over the print unit: x +-192, y -170..-10
PIT = (216.0, -10.0, 114.0)     # open over the carriage: x +-216, y -10..114
BAY = 46.0                     # half-width of the back bay over the escapement (reaches y 151)
BAY_Y = 158.5
PIL = dict(x=240.0, y=98.0, half=18.0, z0=ZT, z1=282.0, hole=12.0)
H_IN = 0.8                     # height of the silver relief over a face
NICHE_D = 1.2                  # depth of the niches

# ------------------------------------------------------------------ 2D ornament (shapely, local u, v)


def star(cx, cy, R, r_in, n=8, r_short=None, rot=90.0):
    """n long rays of length R (and n short ones of r_short between them, if given); valleys at r_in."""
    pts = []
    k = 2 if r_short is None else 4
    for i in range(n * k):
        a = math.radians(rot + 360.0 * i / (n * k))
        if r_short is None:
            r = R if i % 2 == 0 else r_in
        else:
            r = R if i % 4 == 0 else (r_short if i % 4 == 2 else r_in)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)


def feanor(cx, cy, R):
    """Sixteen-rayed star with a small round heart: eight long rays, eight short."""
    return unary_union([star(cx, cy, R, 0.2 * R, 8, 0.58 * R), Point(cx, cy).buffer(0.16 * R, 24)])


def niche(cx, v0, w, h):
    """Round-headed niche: width w, from v0 up to v0 + h (the head is a half circle)."""
    r = w / 2
    return unary_union([sbox(cx - r, v0, cx + r, v0 + h - r), Point(cx, v0 + h - r).buffer(r, 48)])


def lozenges(u0, u1, v, h, pitch=None):
    """A chain of lozenges of height h along v, joined by a thin rule, with dots between them."""
    pitch = pitch or 1.6 * h
    n = max(1, int((u1 - u0) // pitch))
    du = (u1 - u0 - n * pitch) / 2 + pitch / 2
    out = [sbox(u0, v - 0.35, u1, v + 0.35)]
    for i in range(n):
        c = u0 + du + i * pitch
        out.append(Polygon([(c - 0.42 * pitch, v), (c, v + h / 2), (c + 0.42 * pitch, v), (c, v - h / 2)]))
        if i < n - 1:
            out.append(Point(c + pitch / 2, v).buffer(0.13 * h, 16))
    return unary_union(out)


def frame_rule(g, w=1.0):
    """A thin line along the outline of g."""
    return g.buffer(w / 2).difference(g.buffer(-w / 2))


# ------------------------------------------------------------------ planes: (origin, U, V, N) right-handed
FACES = {
    'front': (np.array([0.0, YF, 0.0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, -1.0, 0])),
    'back': (np.array([0.0, YB, 0.0]), np.array([-1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, 1.0, 0])),
    'right': (np.array([XO, 0.0, 0.0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0]), np.array([1.0, 0, 0])),
    'left': (np.array([-XO, 0.0, 0.0]), np.array([0, -1.0, 0]), np.array([0, 0, 1.0]), np.array([-1.0, 0, 0])),
}


def on_plane(g, face, n0, n1):
    """Extrude the 2D shape g (u, v of the face) between n0 and n1 along the face's outward normal."""
    if g is None or g.is_empty:
        return None
    O, U, V, N = face
    m = geo.shapely_to_cs(g).extrude(n1 - n0)
    M = np.column_stack([U, V, N, O + n0 * N])
    return m.transform(M)


def plane(o, u, v):
    u = np.asarray(u, float); v = np.asarray(v, float)
    return (np.asarray(o, float), u, v, np.cross(u, v))


# ------------------------------------------------------------------ the inscription


def inscription_geom(k=1.55):
    """The inscription as the machine types it, in mm (u along the line, v up, baseline at 0), centred on u = 0."""
    import sys
    sys.path.insert(0, os.path.dirname(HERE))
    from fontTools.ttLib import TTFont
    from items import build_items, ADV
    from glyphgeom import glyph_geom
    import fontsets
    f = TTFont(os.path.join(ROOT, fontsets.BY_ID['alcarin']['file']))
    codes = json.load(open(os.path.join(ROOT, 'data', 'codes.json')))
    items, _ = build_items(codes, f)
    gs = f.getGlyphSet()
    J = json.load(open(os.path.join(ROOT, 'data', 'inscription.json')))
    U = P.U; S = P.EM / f['head'].unitsPerEm
    car = 0.0; mem = dict(b=0, c=0)
    glyphs = []
    for kk in J['items']:
        if kk == ' ':
            car -= 6 * U; mem = dict(b=0, c=0)
            continue
        it = items[kk]
        if it['kind'] in ADV:
            glyphs.append((it['glyph'], it['a'] * U - it['ax'] * S - car))
            if it['kind'] == 'C':
                from items import build_items as _b
                glyphs.append((it['mark'], it['a'] * U - _mark_ax(items, it['mark']) * S - car))
            mem = dict(b=it['b'], c=it['c']); car -= it['w'] * U
        else:
            sl = (mem['c'] if it.get('below') else mem['b']) + P.MARK_REF_U
            glyphs.append((it['glyph'], -sl * U + P.MARK_REF_U * U - it['ax'] * S - car))
    out = []
    for name, x in glyphs:
        g = glyph_geom(gs, name)
        if g is None or g.is_empty:
            continue
        out.append(affinity.translate(affinity.scale(g, S, S, origin=(0, 0)), x, 0))
    g = unary_union(out).buffer(0)
    b = g.bounds
    g = affinity.translate(g, -(b[0] + b[2]) / 2, 0)
    return affinity.scale(g, k, k, origin=(0, 0)), J


def _mark_ax(items, mark):
    for it in items.values():
        if it.get('glyph') == mark and it['kind'] not in ('T', 'C', 'N', 'P'):
            return it['ax']
    return 0.0


# ------------------------------------------------------------------ the device plaque


def device_regions():
    D = json.load(open(os.path.join(ROOT, 'data', 'device', 'device_regions.json')))
    return D


# ------------------------------------------------------------------ parts

_CACHE = {}


def parts():
    if 'parts' not in _CACHE:
        _CACHE['parts'] = _build()
    return list(_CACHE['parts'])


def _build():
    from parts import Part
    out = []

    def add(name, mesh, bom, color=BODY, kind='print', note='', printable=None):
        if mesh is None or mesh.is_empty():
            return
        out.append(Part(name, 'case', kind, mesh, color, bom, 'PETG' if kind == 'print' else '', note, printable=printable))

    # ---------------------------------------------------------------- walls: panels with niches, plinth, cornice
    def wall(face, name, u0, u1, prof, niches, holes=(), medallions=(), cuts=(), bom='case_wall'):
        """prof: list of (u0, u1, v_top) spans; niches: list of (u_centre, v0, w, h); holes: 2D shapes cut through;
        cuts: u positions where the wall is split into printed pieces."""
        O, U, V, N = face
        outline = unary_union([sbox(a, 0.0, b, top) for a, b, top in prof])
        through = unary_union(list(holes)) if holes else None
        sunk = unary_union([niche(*n) for n in niches]) if niches else None
        # silver: plinth band, cornice band (following the top), stars in the niches, medallions
        bands = [sbox(u0, 0.0, u1, 9.0)]
        for a, b, top in prof:
            bands.append(sbox(a, top - 9.0, b, top))
        bands = unary_union(bands).intersection(outline)
        orn = [bands]
        for (cu, v0, w, h) in niches:
            orn.append(star(cu, v0 + h - w / 2, 0.36 * w, 0.12 * w, 8))
            orn.append(frame_rule(niche(cu, v0, w, h).buffer(2.2), 1.0))
        for m_ in medallions:
            orn.append(m_)
        orn = unary_union(orn).intersection(outline)
        if through is not None:
            orn = orn.difference(through.buffer(1.0))
        edges = [u0] + list(cuts) + [u1]
        for i in range(len(edges) - 1):
            cell = sbox(edges[i], -1.0, edges[i + 1], 1000.0)
            pan = outline.intersection(cell)
            if pan.is_empty:
                continue
            body = on_plane(pan, face, -T, 0.0)
            if sunk is not None and not sunk.intersection(cell).is_empty:
                body = body - on_plane(sunk.intersection(cell), face, -NICHE_D, 0.1)
            if through is not None and not through.intersection(cell).is_empty:
                body = body - on_plane(through.intersection(cell).buffer(0), face, -T - 1, 1)
            nm = f'case {name} {i + 1}'
            o_ = orn.intersection(cell)
            inl = on_plane(o_, face, 0.0, H_IN) if not o_.is_empty else None
            # niche stars stand on the niche floor and rise to the same silver level
            if sunk is not None:
                st = unary_union([star(cu, v0 + h - w / 2, 0.36 * w, 0.12 * w, 8) for (cu, v0, w, h) in niches]).intersection(cell)
                if not st.is_empty:
                    stem = on_plane(st, face, -NICHE_D, 0.0)
                    inl = stem if inl is None else inl + stem
            pr = _face_up(face, body, inl)
            add(nm, body, bom, printable=pr, note='стенка корпуса; орнамент — серебром, сменой прутка на высоте лица')
            if inl is not None:
                add(nm + ' inlay', inl, None, SILVER, 'inlay')

    # front wall: x -265..265, top at ZK; niches with the carriage release key in the first one
    key_hole = sbox(-226.0, 29.0, -204.0, 57.0)
    fr_n = [(-215.0 + 43.0 * i, 15.0, 28.0, 48.0) for i in range(11)]
    wall(FACES['front'], 'front wall', -XO, XO, [(-XO, XO, ZK)], fr_n, holes=[key_hole], cuts=[-88.0, 88.0],
         bom='case_front')
    # side walls: front part low (to ZK), the rest to ZT; the right wall takes the barrel arbor and the crank's shaft
    for side in ('right', 'left'):
        face = FACES[side]
        sg = 1.0 if side == 'right' else -1.0           # u = y on the right, u = -y on the left
        prof = [(min(sg * YF, sg * YT), max(sg * YF, sg * YT), ZK), (min(sg * YT, sg * YB), max(sg * YT, sg * YB), ZT)]
        nis = [(sg * (-315.0 + 50.0 * i), 16.0, 30.0, 108.0) for i in range(9)]
        holes = []
        if side == 'right':
            holes = [Point(-265.0, 65.0).buffer(7.0, 32), Point(-265.0, 119.0).buffer(7.5, 32)]
        med = [feanor(sg * (YF + YT) / 2, 40.0, 13.0)]
        cuts = sorted([sg * -222.0, sg * -40.0])
        wall(face, f'{side} wall', min(sg * YF, sg * YB), max(sg * YF, sg * YB), prof, nis, holes, med, cuts,
             bom='case_side')
    # back wall: with the opening of the bay over the escapement
    bk_n = [(c, 16.0, 30.0, 108.0) for c in (-230.0, -180.0, -130.0, -80.0, 80.0, 130.0, 180.0, 230.0)]
    wall(FACES['back'], 'back wall', -XO, XO, [(-XO, -BAY, ZT), (BAY, XO, ZT)], bk_n, cuts=[-150.0, 150.0], bom='case_back')
    # the bay: two cheeks, a back with a great star, a roof
    bf = plane((0.0, BAY_Y, 0.0), (-1, 0, 0), (0, 0, 1))
    bb = sbox(-BAY, 0.0, BAY, ZT)
    body = on_plane(bb, bf, -T, 0.0)
    inl = on_plane(unary_union([sbox(-BAY, 0, BAY, 9.0), sbox(-BAY, ZT - 9.0, BAY, ZT), feanor(0.0, 70.0, 34.0),
                                frame_rule(Point(0, 70).buffer(38.0, 64), 1.4)]), bf, 0.0, H_IN)
    add('case bay back', body, 'case_bay', printable=_face_up(bf, body, inl),
        note='ниша над спуском: спуск выходит за раму назад до 151 мм')
    add('case bay back inlay', inl, None, SILVER, 'inlay')
    for sx in (-1, 1):
        ch = geo.box(sx * BAY - (T if sx > 0 else 0), sx * BAY + (0 if sx > 0 else T), YB, BAY_Y - T, 0.0, ZT)
        add(f'case bay cheek {sx:+d}', ch, 'case_bay_cheek', printable=_lay(ch, 'x'))
    roof = geo.box(-BAY, BAY, YB0, BAY_Y, ZT - TD, ZT)
    add('case bay roof', roof, 'case_bay_roof', printable=_lay(roof, 'z'))

    # ---------------------------------------------------------------- standoffs to the frame (M5 into the T-slots)
    so = []
    for y in (-330.0, -150.0, 40.0):
        for sx in (-1, 1):
            so.append((f'case standoff side {sx:+d} {y:.0f}', geo.box(min(sx * 250.2, sx * XI), max(sx * 250.2, sx * XI), y - 10, y + 10, 4.0, 16.0)))
    for x in (-160.0, 0.0, 160.0):
        so.append((f'case standoff front {x:.0f}', geo.box(x - 10, x + 10, YFI, -395.2, 4.0, 16.0)))
        so.append((f'case standoff back {x if abs(x) > 1 else 100.0:.0f}', geo.box((x if abs(x) > 1 else 100.0) - 10, (x if abs(x) > 1 else 100.0) + 10,
                                                                               130.2, YB0, 4.0, 16.0)))
    for nm, m in so:
        m = m - geo.cyl((0, 0, 0), (0, 0, 0), 0.1) if False else m
        add(nm, m, 'case_standoff', (70, 80, 110), printable=_lay(m, 'z'), note='упор стенки на раму: винт М5 в паз профиля')

    # ---------------------------------------------------------------- keyboard deck: the well and the front strip
    import parts as PT
    caps = [p for p in PT.build(PT.State()) if p.name.startswith('cap ')]
    holes = unary_union([sbox(*np.array(p.mesh.bounding_box())[[0, 1]], *np.array(p.mesh.bounding_box())[[3, 4]]).buffer(1.6, join_style=2)
                         for p in caps])
    well = sbox(-XT, YT, XT, YFA)
    strip = sbox(-XI, YFI, XI, YT)
    kd = unary_union([well, strip]).difference(holes)
    top = plane((0, 0, ZK), (1, 0, 0), (0, 1, 0))
    orn = unary_union([lozenges(-XI + 12, XI - 12, (YFI + YT) / 2, 11.0, 19.0),
                       frame_rule(well.buffer(-4.0), 1.0).difference(holes.buffer(1.0))])
    xs = _free_cut(holes, -4.0, 4.0, YT, YFA)
    for i, (a, b) in enumerate(((-XI - 1, -88.0), (-88.0, 88.0), (88.0, XI + 1))):
        cell = sbox(a, -1000, b, YT)
        _deck_piece(add, f'case keyboard strip {i + 1}', kd.intersection(cell), orn.intersection(cell), top, 'case_kbd_strip')
    for i, (a, b) in enumerate(((-XT - 1, xs), (xs, XT + 1))):
        cell = sbox(a, YT, b, 1000)
        _deck_piece(add, f'case keyboard deck {i + 1}', kd.intersection(cell), orn.intersection(cell), top, 'case_kbd_deck')

    # ---------------------------------------------------------------- towers: fronts with great stars, inner walls
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (XT + 3.0), sx * XI))
        fface = plane((0, YT, 0), (1, 0, 0), (0, 0, 1))
        pan = sbox(x0, ZK, x1, ZT - TD)
        body = on_plane(pan, fface, -T, 0.0)
        cx = (x0 + x1) / 2
        inl = on_plane(unary_union([feanor(cx, (ZK + ZT - TD) / 2, 23.0), frame_rule(Point(cx, (ZK + ZT - TD) / 2).buffer(27.0, 64), 1.4),
                                    sbox(x0, ZT - TD - 5.0, x1, ZT - TD)]), fface, 0.0, H_IN)
        add(f'case tower front {sx:+d}', body, 'case_tower_front', printable=_face_up(fface, body, inl))
        add(f'case tower front {sx:+d} inlay', inl, None, SILVER, 'inlay')
        wi = geo.box(min(sx * XT, sx * (XT + 3.0)), max(sx * XT, sx * (XT + 3.0)), YT + T, YFA + T, ZK, ZT - TD)
        add(f'case tower wall {sx:+d}', wi, 'case_tower_wall', printable=_lay(wi, 'x'))

    # ---------------------------------------------------------------- fascia with the inscription
    ins, J = inscription_geom(1.55)
    b = ins.bounds
    vz = (ZK + ZT - TD) / 2 - (b[1] + b[3]) / 2
    ins = affinity.translate(ins, 0.0, vz)
    fface = plane((0, YFA, 0), (1, 0, 0), (0, 0, 1))
    pan = sbox(-XT, ZK, XT, ZT - TD)
    bi = ins.bounds
    orn = unary_union([ins, sbox(-XT, bi[3] + 5.0, XT, bi[3] + 6.2), sbox(-XT, bi[1] - 6.2, XT, bi[1] - 5.0),
                       star(bi[0] - 11.0, (bi[1] + bi[3]) / 2, 6.5, 2.0, 8), star(bi[2] + 11.0, (bi[1] + bi[3]) / 2, 6.5, 2.0, 8)])
    cut = _gap_cut(ins, 0.0)
    for i, (a, b_) in enumerate(((-XT - 1, cut), (cut, XT + 1))):
        cell = sbox(a, -10, b_, 1000)
        body = on_plane(pan.intersection(cell), fface, -T, 0.0)
        inl = on_plane(orn.intersection(cell), fface, 0.0, H_IN)
        add(f'case fascia {i + 1}', body, 'case_fascia', printable=_face_up(fface, body, inl),
            note='лицо за клавишами: надпись «' + J['text'] + '»')
        add(f'case fascia {i + 1} inlay', inl, None, SILVER, 'inlay')
    _CACHE['inscription'] = dict(text=J['text'], translation=J['translation'], width=round(bi[2] - bi[0], 1),
                                 height=round(bi[3] - bi[1], 1), scale=1.55)

    # ---------------------------------------------------------------- top deck
    tdeck = sbox(-XI, YT + T, XI, YB0)
    tdeck = tdeck.difference(sbox(-XT - 3.0, YT, XT + 3.0, YFA + T))          # over the well (the fascia is under its edge)
    tdeck = tdeck.difference(sbox(-COURT[0], COURT[1], COURT[0], COURT[2]))
    tdeck = tdeck.difference(sbox(-PIT[0], PIT[1], PIT[0], PIT[2]))
    post = lambda sx: sbox(sx * PIL['x'] - PIL['hole'], PIL['y'] - PIL['hole'], sx * PIL['x'] + PIL['hole'], PIL['y'] + PIL['hole'])
    tdeck = tdeck.difference(unary_union([post(-1), post(1)]))
    grille_c = (201.0, (YT + T + YFA + T) / 2)
    dev_c = (-201.0, grille_c[1])
    tdeck = tdeck.difference(Point(*grille_c).buffer(50.0, 96))
    topf = plane((0, 0, ZT), (1, 0, 0), (0, 1, 0))
    orn = unary_union([lozenges(-COURT[0] + 10, COURT[0] - 10, COURT[1] - 8.0, 9.0, 16.0),
                       frame_rule(Point(*grille_c).buffer(55.0, 96), 1.4),
                       frame_rule(Polygon([(dev_c[0], dev_c[1] + 62), (dev_c[0] + 62, dev_c[1]), (dev_c[0], dev_c[1] - 62),
                                           (dev_c[0] - 62, dev_c[1])]), 1.4)]).intersection(tdeck)
    cells = {'tower -1': sbox(-XI - 1, YT, -XT - 3.0, YFA + T), 'tower +1': sbox(XT + 3.0, YT, XI + 1, YFA + T),
             'band -1': sbox(-COURT[0], YFA + T, 0.0, COURT[1]), 'band +1': sbox(0.0, YFA + T, COURT[0], COURT[1]),
             'side -1 a': sbox(-XI - 1, YFA + T, -COURT[0], -121.0), 'side +1 a': sbox(COURT[0], YFA + T, XI + 1, -121.0),
             'side -1 b': sbox(-XI - 1, -121.0, -COURT[0], COURT[2]), 'side +1 b': sbox(COURT[0], -121.0, XI + 1, COURT[2]),
             'pit -1': sbox(-XI - 1, PIT[1], -PIT[0], PIT[2]), 'pit +1': sbox(PIT[0], PIT[1], XI + 1, PIT[2]),
             'back -1': sbox(-XI - 1, PIT[2], -87.0, YB0), 'back 0': sbox(-87.0, PIT[2], 87.0, YB0), 'back +1': sbox(87.0, PIT[2], XI + 1, YB0)}
    for nm, cell in cells.items():
        _deck_piece(add, f'case top {nm}', tdeck.intersection(cell), orn.intersection(cell), topf, 'case_top', z0=ZT - TD)
    # stiffening lips under the free edges (court, pit)
    lips = [geo.box(-COURT[0], COURT[0], COURT[1], COURT[1] + 3.0, ZT - TD - 12.0, ZT - TD)]
    for sx in (-1, 1):
        lips.append(geo.box(min(sx * COURT[0], sx * (COURT[0] + 3.0)), max(sx * COURT[0], sx * (COURT[0] + 3.0)), COURT[1] + 3.0, COURT[2],
                            ZT - TD - 12.0, ZT - TD))
        lips.append(geo.box(min(sx * PIT[0], sx * (PIT[0] + 3.0)), max(sx * PIT[0], sx * (PIT[0] + 3.0)), PIT[1], PIT[2] + 3.0,
                            ZT - TD - 12.0, ZT - TD))
    lips.append(geo.box(-PIT[0], PIT[0], PIT[2], PIT[2] + 3.0, ZT - TD - 12.0, ZT - TD))
    for i, m in enumerate(lips):
        add(f'case lip {i + 1}', m, 'case_lip', printable=_lay(m, 'auto'), note='ребро под свободным краем деки')

    # ---------------------------------------------------------------- the pierced star over the barrel (right tower)
    gx, gy = grille_c
    ring = Point(gx, gy).buffer(54.0, 96).difference(Point(gx, gy).buffer(47.0, 96))
    st = unary_union([feanor(gx, gy, 47.5), ring, sbox(gx - 47.5, gy - 1.2, gx + 47.5, gy + 1.2),
                      sbox(gx - 1.2, gy - 47.5, gx + 1.2, gy + 47.5)])
    g = geo.shapely_to_cs(st).extrude(TD + 1.2).translate((0, 0, ZT - TD))
    add('case star grille', g, 'case_grille', SILVER, printable=_lay(g, 'z'), note='решётка-звезда над барабаном пружины, серебро')

    # ---------------------------------------------------------------- the device plaque (left tower)
    D = device_regions()
    sc = 62.0 / D['half_diagonal']
    lz = Polygon([(0, 270), (270, 0), (0, -270), (-270, 0)])
    base = affinity.translate(affinity.scale(lz, sc, sc, origin=(0, 0)), *dev_c)
    pb = geo.shapely_to_cs(base).extrude(2.4).translate((0, 0, ZT))
    add('case device plaque', pb, 'case_device', (20, 20, 20), printable=_lay(pb, 'z'),
        note='щит с гербом Mírë Nolmeo: многоцветная печать, файлы по цветам в stl/device/')
    for r in D['regions']:
        if r['color'] == '#141414':
            continue                                    # the field of the lozenge is the plaque itself
        polys = [Polygon(p[0], p[1:]).buffer(0) for p in r['polys']]
        g = unary_union(polys)
        g = affinity.translate(affinity.scale(g, sc, sc, origin=(0, 0)), *dev_c)
        h = 0.3 + 0.9 * r['lum']
        m = geo.shapely_to_cs(g).extrude(h).translate((0, 0, ZT + 2.4))
        col = tuple(int(r['color'][i:i + 2], 16) for i in (1, 3, 5))
        add(f'case device {r["color"][1:]}', m, None, col, 'inlay')

    # ---------------------------------------------------------------- pillars over the carriage's posts
    for sx in (-1, 1):
        cx, cy, hf = sx * PIL['x'], PIL['y'], PIL['half']
        shaft = geo.box(cx - hf, cx + hf, cy - hf, cy + hf, PIL['z0'] + 10.0, PIL['z1'])
        shaft = shaft - geo.box(cx - PIL['hole'], cx + PIL['hole'], cy - PIL['hole'], cy + PIL['hole'], 0, PIL['z1'] + 1)
        ix = cx - sx * hf                                     # the inner face (toward the carriage): the rod goes in here
        shaft = shaft - geo.cyl((ix - 8, cy, P.CAR_RAIL_HI[1]), (ix + 8, cy, P.CAR_RAIL_HI[1]), 5.5, 32)
        for f_ in (-1, 1):                                    # flutes on the front and back faces
            for du in (-9.0, 0.0, 9.0):
                shaft = shaft - geo.box(cx + du - 2.0, cx + du + 2.0, cy + f_ * hf - 1.2 if f_ > 0 else cy - hf - 0.1,
                                        cy + hf + 0.1 if f_ > 0 else cy - hf + 1.2, PIL['z0'] + 22.0, PIL['z1'] - 12.0)
        add(f'case pillar {sx:+d}', shaft, 'case_pillar', PILLAR, printable=_lay(shaft, 'z'),
            note='пилястра над стойкой каретки, пустотелая; печатается стоя')
        base_ = geo.box(cx - hf - 3, cx + hf + 3, cy - hf - 3, cy + hf + 3, PIL['z0'], PIL['z0'] + 10.0) - \
            geo.box(cx - PIL['hole'], cx + PIL['hole'], cy - PIL['hole'], cy + PIL['hole'], 0, 400)
        add(f'case pillar base {sx:+d}', base_, 'case_pillar_base', SILVER, printable=_lay(base_, 'z'))
        cap = geo.box(cx - hf - 4, cx + hf + 4, cy - hf - 4, cy + hf + 4, PIL['z1'], PIL['z1'] + 8.0) + \
            geo.box(cx - hf - 1.5, cx + hf + 1.5, cy - hf - 1.5, cy + hf + 1.5, PIL['z1'] + 8.0, PIL['z1'] + 12.0)
        add(f'case pillar capital {sx:+d}', cap, 'case_pillar_cap', SILVER, printable=_lay(cap, 'z'))
        fin_c = PIL['z1'] + 12.0 + 27.0
        fin = on_plane(unary_union([feanor(0.0, 0.0, 27.0), sbox(-6.0, -27.0, 6.0, -20.0)]),
                       plane((cx, cy, fin_c), (1, 0, 0), (0, 0, 1)), -3.0, 3.0)
        add(f'case finial {sx:+d}', fin, 'case_finial', SILVER, printable=_lay(fin, 'y'),
            note='навершие: шестнадцатилучевая звезда')
    return out


# ------------------------------------------------------------------ helpers for the printed pieces


def _face_up(face, body, inlay):
    """Printable: the panel with its silver relief, the decorated face up."""
    O, U, V, N = face
    R = np.column_stack([U, V, N]).T                       # world -> (u, v, n)
    M = np.column_stack([R, -R @ O])

    def f():
        m = body if inlay is None else body + inlay
        return m.transform(M)
    return f


def _lay(m, axis):
    """Printable: the part as it is ('z'), or turned so that its smallest extent ('auto') or the given axis is up."""
    def f():
        b = np.array(m.bounding_box()); d = b[3:] - b[:3]
        ax = {'x': 0, 'y': 1, 'z': 2}.get(axis, int(np.argmin(d)))
        if ax == 0:
            return m.rotate((0, 90, 0))
        if ax == 1:
            return m.rotate((90, 0, 0))
        return m
    return f


def _deck_piece(add, name, g, orn, face, bom, z0=None):
    if g.is_empty:
        return
    O, U, V, N = face
    body = on_plane(g, face, -TD, 0.0)
    o = orn.intersection(g) if orn is not None else None
    inl = on_plane(o, face, 0.0, H_IN) if o is not None and not o.is_empty else None
    add(name, body, bom, printable=_face_up(face, body, inl))
    if inl is not None:
        add(name + ' inlay', inl, None, SILVER, 'inlay')


def _free_cut(holes, a, b, y0, y1):
    """An x in [a, b] where a cut along y does not cross the key holes (else the middle)."""
    for x in np.linspace(0.0, b, 41).tolist() + np.linspace(0.0, a, 41).tolist():
        if not holes.intersects(sbox(x - 0.6, y0, x + 0.6, y1)):
            return float(x)
    best = None
    for x in np.arange(-30.0, 30.0, 0.5):
        if not holes.intersects(sbox(x - 0.6, y0, x + 0.6, y1)):
            if best is None or abs(x) < abs(best):
                best = x
    return float(best if best is not None else 0.0)


def _gap_cut(g, near):
    """An u near `near` where a vertical cut misses the inscription."""
    for d in np.arange(0.0, 60.0, 0.5):
        for x in (near + d, near - d):
            if not g.intersects(sbox(x - 0.8, -1000, x + 0.8, 1000)):
                return float(x)
    return float(near)


def info():
    parts()
    return dict(_CACHE.get('inscription', {}))
