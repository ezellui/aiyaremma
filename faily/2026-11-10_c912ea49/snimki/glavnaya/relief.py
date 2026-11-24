"""rev. 0.9c: debossed reliefs on printed parts.

* part numbers: the part's running number, debossed 0.6 mm into its top face (in print orientation) or, if the top
  has no room, into the face on the bed (mirrored, so it reads from below); at least 1.5 mm of solid stays under the
  text; text 3.5..6 mm high (PT Sans Bold); a part with no flat room for 3.5 mm digits gets no number;
* key legends: the key's glyphs debossed into the cap top: the lower register large (lower left), the upper small
  (upper right); service keys get a symbol (DejaVu Sans Bold), the space bars "4u" / "6u".
Text outlines come from the fonts as shapely geometry; strokes of the tengwar are thickened to 0.8 mm at their size
(thicken.slug_geometry), so a 0.4 mm nozzle can form every groove."""
import os, pickle, math
import numpy as np
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon, box as sbox
from shapely.ops import unary_union
from shapely.prepared import prep
from manifold3d import Manifold, CrossSection, OpType
import params as P
import data as D
import geo
from glyphgeom import glyph_geom
from thicken import slug_geometry

FONTS = os.path.join(D.ROOT, 'fonts')
SANS = os.path.join(FONTS, 'PT_Sans-Web-Bold.ttf')
SYM = os.path.join(FONTS, 'DejaVuSans-Bold.ttf')
DEPTH = 0.6            # deboss depth
FLOOR = 1.5            # solid left under the text
MARGIN = 0.8           # text to the face's edge
HEIGHTS = (6.0, 5.0, 4.0, 3.5)
CACHE = os.path.join(D.ROOT, 'gen', 'model_cache')
_fonts = {}


def _font(path):
    if path not in _fonts:
        f = TTFont(path)
        _fonts[path] = (f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm, f)
    return _fonts[path]


def text_geom(text, path=SANS, height=5.0, cap=True):
    """Outline of a string, y up, origin at the left of the baseline; `height` is the height of the digits (cap
    height) or, with cap=False, of the em."""
    gs, cmap, upm, f = _font(path)
    x = 0.0; out = []
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        g = glyph_geom(gs, name)
        if g is not None and not g.is_empty:
            out.append(affinity.translate(g, x, 0))
        x += gs[name].width
    g = unary_union(out) if out else None
    if g is None:
        return None
    if cap:
        b = _font(path)[1].get(ord('0'))
        ref = glyph_geom(gs, b).bounds[3] if b else upm * 0.7
    else:
        ref = upm
    s = height / ref
    return affinity.scale(g, s, s, origin=(0, 0)).buffer(0)


def tengwar_geom(item, em, pmin=0.8):
    """Glyphs of a keyboard item (as on the shuttle, not mirrored), y up, in mm at em size `em`, strokes >= pmin."""
    key = f'kcap_{item}_{em:.2f}_{pmin}'.replace(':', '-').replace('+', 'p').replace('/', '_')
    fn = os.path.join(CACHE, key + '.pkl')
    if os.path.exists(fn):
        return pickle.load(open(fn, 'rb'))
    import typeblocks as TB
    s = em / 1000.0
    gs = []
    for gname, x0 in TB.item_glyphs(item):
        g = slug_geometry(D.GLYPHSET, gname, em, pmin)[0]
        gs.append(affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), x0 * em / P.EM, 0))
    g = unary_union(gs).buffer(0) if gs else None
    pickle.dump(g, open(fn, 'wb'))
    return g


def fit_box(g, x0, y0, x1, y1, anchor='c'):
    """Scale g down (never up) to fit the box and place it at the anchor (c = centre, ll / ur = corners)."""
    b = g.bounds; w, h = b[2] - b[0], b[3] - b[1]
    s = min(1.0, (x1 - x0) / max(w, 1e-6), (y1 - y0) / max(h, 1e-6))
    g = affinity.scale(g, s, s, origin=(b[0], b[1]))
    b = g.bounds; w, h = b[2] - b[0], b[3] - b[1]
    if anchor == 'll':
        tx, ty = x0, y0
    elif anchor == 'ur':
        tx, ty = x1 - w, y1 - h
    else:
        tx, ty = (x0 + x1 - w) / 2, (y0 + y1 - h) / 2
    return affinity.translate(g, tx - b[0], ty - b[1])


def cut_top(mesh, g, ztop, depth=DEPTH):
    """Deboss the 2D shape g (x, y in model coordinates) into the face at z = ztop."""
    if g is None or g.is_empty:
        return mesh
    cs = geo.shapely_to_cs(g)
    tool = cs.extrude(depth + 1.0).translate((0, 0, ztop - depth))
    return mesh - tool


def _slice(mesh, z):
    polys = mesh.slice(z).to_polygons()
    rings = [Polygon(p) for p in polys if len(p) >= 3]
    if not rings:
        return None
    # even-odd: outer rings and holes
    g = None
    for r in sorted(rings, key=lambda r: -abs(r.area)):
        r = r.buffer(0)
        g = r if g is None else g.symmetric_difference(r)
    return g


def _place(region, text_by_h):
    """Find a place for the text inside region (shapely); returns the placed geometry or None."""
    if region is None or region.is_empty:
        return None
    from shapely.ops import polylabel
    pr = prep(region)
    parts = list(region.geoms) if isinstance(region, MultiPolygon) else [region]
    parts = sorted(parts, key=lambda p: -p.area)[:4]
    for h in HEIGHTS:
        t = text_by_h(h)
        for rot in (0, 90):
            tg = affinity.rotate(t, rot, origin=(0, 0))
            b = tg.bounds; w, hh = b[2] - b[0], b[3] - b[1]
            for p in parts:
                if p.area < w * hh:
                    continue
                c = polylabel(p, 0.2)
                cands = [(c.x, c.y)]
                pb = p.bounds
                for gx in np.arange(pb[0] + w / 2, pb[2] - w / 2 + 1e-6, 1.0):
                    for gy in np.arange(pb[1] + hh / 2, pb[3] - hh / 2 + 1e-6, 1.0):
                        cands.append((gx, gy))
                cands.sort(key=lambda q: (q[0] - c.x) ** 2 + (q[1] - c.y) ** 2)
                for cx, cy in cands[:400]:
                    pl = affinity.translate(tg, cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)
                    if pr.contains(pl.envelope.buffer(0.2)) or pr.contains(pl.buffer(0.3)):
                        return pl
    return None


def number_part(mesh, n):
    """Deboss the number n into a part already in print orientation (on the bed, z >= 0).
    Returns (mesh, where) with where in ('top', 'bottom', None)."""
    label = str(n)
    lo, hi = np.array(mesh.bounding_box()).reshape(2, 3)
    ztop, zbot = hi[2], lo[2]
    if ztop - zbot < DEPTH + FLOOR + 0.2:
        return mesh, None
    def region(z_face, z_floor):
        a = _slice(mesh, z_face); b = _slice(mesh, z_floor)
        if a is None or b is None:
            return None
        r = a.intersection(b).buffer(-MARGIN)
        return None if r.is_empty else r
    # top face
    r = region(ztop - 0.05, ztop - DEPTH - FLOOR)
    pl = _place(r, lambda h: text_geom(label, SANS, h))
    if pl is not None:
        return cut_top(mesh, pl, ztop), 'top'
    # the face on the bed: the text is mirrored so it reads from below
    r = region(zbot + 0.05, zbot + DEPTH + FLOOR)
    pl = _place(r, lambda h: affinity.scale(text_geom(label, SANS, h), -1, 1, origin=(0, 0)))
    if pl is not None:
        cs = geo.shapely_to_cs(pl)
        return mesh - cs.extrude(DEPTH + 1.0).translate((0, 0, zbot - 1.0)), 'bottom'
    return mesh, None


# ------------------------------------------------------------------ key legends
SERVICE = {'shift': '⇧', 'bksp': '⌫', 'back': '⟲', 'space4': '4u', 'space6': '6u'}


def key_legend(k, top_z):
    """2D legend of key k (dict from parts.key_list) in model x, y, for the cap top at height top_z."""
    w = k['w']; d = 14.0 if k['kind'] == 'space' else w
    x0, x1 = k['x'] - w / 2 + 1.6, k['x'] + w / 2 - 1.6
    y0, y1 = k['y'] - d / 2 + 1.6, k['y'] + d / 2 - 1.6
    if k['kind'] == 'char':
        lo, up = D.ROWS[k['r']][k['c']]
        gs = []
        if lo is not None:
            g = tengwar_geom(lo, 9.0)
            if g is not None and not g.is_empty:
                gs.append(fit_box(g, x0, y0, x0 + 9.5, y0 + 9.5, 'll'))
        if up is not None:
            g = tengwar_geom(up, 5.5)
            if g is not None and not g.is_empty:
                gs.append(fit_box(g, x1 - 5.5, y1 - 5.5, x1, y1, 'ur'))
        return unary_union(gs) if gs else None
    sym = SERVICE.get(k['id'])
    if sym is None:
        return None
    if k['kind'] == 'space':
        g = text_geom(sym, SANS, 6.0)
    else:
        g = text_geom(sym, SYM, 11.0, cap=False)
    return fit_box(g, x0, y0, x1, y1, 'c') if g is not None else None
