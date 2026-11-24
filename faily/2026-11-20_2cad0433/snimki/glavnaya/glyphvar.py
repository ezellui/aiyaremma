"""rev. 0.14: marks raised into the bowl of lambe (and alda).

Lambe's bowl goes below the line, so a mark set under it (the two dots of y, the doubling bar) lies on its stroke.
Alcarin has a doubling bar drawn inside the bowl (uniE051.lambe); the other marks and the other fonts have none.
This module makes such glyphs by raising the plain mark: a synthetic glyph '<mark>.inlambe' is the mark moved up so
that its middle stands in the middle of the bowl, on lambe's bottom axis. The glyph set is wrapped (VarGlyphSet), so
every consumer of glyph names (thickening, type blocks, the page, the document) draws it as any other glyph.

Where the bowl's middle is: on a vertical line through lambe's bottom axis, the gap between the bowl's lowest stroke
and the stroke above it (Alcarin: its own uniE051.lambe gives the height, and the dots follow it)."""
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

SUFFIX = '.inlambe'


class _Shifted:
    def __init__(self, g, dx, dy):
        self.g, self.dx, self.dy = g, dx, dy
        self.width = getattr(g, 'width', 0)

    def draw(self, pen):
        self.g.draw(TransformPen(pen, (1, 0, 0, 1, self.dx, self.dy)))


class VarGlyphSet:
    """A glyph set plus synthetic glyphs: name -> (base name, dx, dy)."""
    def __init__(self, gs, extra=None):
        self.gs = gs
        self.extra = dict(extra or {})

    def add(self, name, base, dx, dy):
        self.extra[name] = (base, dx, dy)

    def __getitem__(self, name):
        if name in self.extra:
            b, dx, dy = self.extra[name]
            return _Shifted(self.gs[b], dx, dy)
        return self.gs[name]

    def __contains__(self, name):
        return name in self.extra or name in self.gs

    def keys(self):
        return list(self.gs.keys()) + list(self.extra)

    def get(self, name, default=None):
        return self[name] if name in self else default


def bounds(gs, name):
    p = BoundsPen(gs)
    gs[name].draw(p)
    return p.bounds


def bowl_middle(gs, lambe, x):
    """y of the middle of lambe's bowl on the vertical through x (font units), or None."""
    from glyphgeom import glyph_geom
    from shapely.geometry import LineString
    g = glyph_geom(gs, lambe)
    b = g.bounds
    cut = g.intersection(LineString([(x, b[1] - 10), (x, b[3] + 10)]))
    segs = []
    for s in getattr(cut, 'geoms', [cut]):
        if s.is_empty or s.length == 0:
            continue
        ys = [p[1] for p in s.coords]
        segs.append((min(ys), max(ys)))
    segs.sort()
    if len(segs) < 2:
        return None
    return 0.5 * (segs[0][1] + segs[1][0])


def raise_into(gs, mark, lambe, x, y_mid=None):
    """dy that puts the middle of `mark` at the middle of lambe's bowl (or at y_mid)."""
    y = bowl_middle(gs, lambe, x) if y_mid is None else y_mid
    if y is None:
        return None
    b = bounds(gs, mark)
    return y - 0.5 * (b[1] + b[3])
