#!/usr/bin/env python3
"""Draped layer 'Алтайская межа' (1953) for the R.S.F.G.R. globe: the schism between the Great Mycelium of R'lyeh
and the heretical Yuggothian mycelium of Urga (the former Gobi vassal, i.e. Mongolia).

Output (out/overlay/):
  altai_border_1953.png      equirectangular RGBA, 8192x4096, lon -180..180 left to right, lat 90..-90 top to bottom,
                             transparent background — drapes over any globe texture of that layout
  altai_border_1953.geojson  the same content as vectors: both claim lines, the disputed strip, markers, labels

Geometry: the real Union-Mongolia boundary (shared arcs of the region set, west of 100.5° E) is taken as the
axis; R'lyeh's claim is offset into Mongolia (bulging round Uvs Nuur), Urga's claim is offset into the Union
(bulging round the Chuya steppe and Kosh-Agach). Both taper to zero at the peak Tabyn-Bogdo-Ola, where the two
markers No. 1 stand together. Offsets vary smoothly (deterministic noise) so the lines look hand-drawn.
Labels are pre-stretched by 1/cos(lat) so that they look undistorted on the globe.
"""
import json
import math
import os

import cairo
import numpy as np
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.ops import linemerge, transform as shp_transform, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "overlay")
CACHE = os.path.join(HERE, "cache")
REGIONS_GEOJSON = os.path.join(HERE, "..", "maps_extract", "unified", "unified_regions.geojson")
W, H = 8192, 4096
SERIF = "Old Standard TT"
LON_MAX = 100.5        # the Altai section of the boundary (Altai and Tuva); further east is not part of this межа

INK = (0.16, 0.13, 0.10)
RED = (0.66, 0.16, 0.11)
VIOLET = (0.42, 0.24, 0.55)
PAPER = (0.96, 0.93, 0.85)

# claim offsets in km as a function of longitude: (lon, km) control points, interpolated linearly
RED_OFFSET = [(87.8, 0), (88.4, 18), (89.5, 30), (90.8, 34), (91.8, 62), (92.6, 82), (93.6, 76), (94.6, 40),
              (96.0, 32), (97.5, 44), (98.8, 30), (100.0, 14), (100.5, 0)]
VIOLET_OFFSET = [(87.8, 0), (88.2, 46), (88.8, 92), (89.5, 88), (90.2, 44), (91.5, 26), (93.0, 30), (94.5, 22),
                 (96.0, 38), (97.4, 30), (99.0, 24), (100.0, 12), (100.5, 0)]
N_MARKERS = 12
LABELS = [  # text, lon, lat, size px (at equator; stretched by 1/cos lat), style
    ("СПОРНАЯ ПОЛОСА", 90.6, 50.05, 17, "caps_ink"),
    ("СПОРНАЯ ПОЛОСА", 96.3, 50.55, 17, "caps_ink"),
    ("межа по притязанію Р'льеха", 93.4, 49.25, 19, "italic_red"),
    ("межа по притязанію Урги", 89.6, 51.05, 19, "italic_violet"),
    ("Табынъ-Богдо-Ола", 86.2, 49.05, 17, "italic_ink"),
    ("оз. Убса-норъ", 92.75, 50.33, 15, "italic_ink"),
    ("Чуйская степь", 88.75, 50.12, 15, "italic_ink"),
    ("Межа не утверждена. Въ архивъ.", 95.5, 47.4, 30, "red_hand"),
]


def to_px(lon, lat):
    return (np.asarray(lon) + 180.0) / 360.0 * W, (90.0 - np.asarray(lat)) / 180.0 * H


def boundary_axis():
    """the Union-Mongolia boundary west of LON_MAX as one ordered line (west to east), lon/lat."""
    regions = json.load(open(os.path.join(CACHE, "regions.json"), encoding="utf-8"))
    a = np.load(os.path.join(CACHE, "arcs.npz"))
    xy, lens, left, right = a["xy"].astype(float), a["lens"], a["left"], a["right"]
    off = np.r_[0, np.cumsum(lens)]
    adm = [r["admin"] for r in regions]
    parts = []
    for k in range(len(lens)):
        l, r = left[k], right[k]
        if r < 0 or {adm[l], adm[r]} != {"Russia", "Mongolia"}:
            continue
        seg = xy[off[k]:off[k + 1]]
        if seg[:, 0].min() > LON_MAX:
            continue
        parts.append(LineString(seg))
    line = linemerge(unary_union(parts))
    if line.geom_type == "MultiLineString":  # keep the longest connected piece
        line = max(line.geoms, key=lambda g: g.length)
    c = np.asarray(line.coords)
    if c[0, 0] > c[-1, 0]:
        c = c[::-1]
    c = c[c[:, 0] <= LON_MAX + 1e-9]
    return c


def mongolia_polygon():
    feats = json.load(open(REGIONS_GEOJSON, encoding="utf-8"))["features"]
    return unary_union([shapely.geometry.shape(f["geometry"]) for f in feats if f["properties"]["admin"] == "Mongolia"])


def interp(ctrl, lon):
    xs, ys = zip(*ctrl)
    return np.interp(lon, xs, ys)


def offset_line(axis_m, lon_axis, ctrl, side_sign, wobble_seed):
    """offset an ordered metric polyline by a lon-dependent distance (km) to one side, with smooth wobble."""
    n = len(axis_m)
    d = np.gradient(axis_m, axis=0)
    t = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    nrm = np.stack([-t[:, 1], t[:, 0]], 1)
    k = 25  # smooth the normals so offsets do not kink at the zig-zags of the boundary
    ker = np.ones(k) / k
    nrm = np.stack([np.convolve(np.pad(nrm[:, j], (k // 2, k // 2), mode="edge"), ker, "valid")[:n] for j in (0, 1)], 1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    rng = np.random.default_rng(wobble_seed)
    wob = np.convolve(rng.normal(0, 1, n + 60), np.ones(60) / 60, "valid")[:n]
    wob /= max(np.abs(wob).max(), 1e-9)
    dist_km = interp(ctrl, lon_axis) * (1 + 0.18 * wob)
    return axis_m + side_sign * nrm * dist_km[:, None] * 1000.0


def put_text(ctx, text, lon, lat, size, style, angle=0.0):
    stretch = 1.0 / max(math.cos(math.radians(lat)), 0.2)
    slant = cairo.FONT_SLANT_ITALIC if "italic" in style or "hand" in style else cairo.FONT_SLANT_NORMAL
    weight = cairo.FONT_WEIGHT_BOLD if style in ("caps_ink", "red_hand") else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(SERIF, slant, weight)
    ctx.set_font_size(size)
    spacing = 0.2 * size if style.startswith("caps") else 0.0
    ext = [ctx.text_extents(ch).x_advance for ch in text]
    tw = sum(ext) + spacing * (len(text) - 1)
    col = {"caps_ink": INK, "italic_ink": INK, "italic_red": RED, "italic_violet": VIOLET, "red_hand": RED}[style]
    x, y = to_px(lon, lat)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(stretch, 1.0)
    cx = -tw / 2
    ctx.new_path()
    for ch, adv in zip(text, ext):
        ctx.move_to(cx, size * 0.35)
        ctx.text_path(ch)
        cx += adv + spacing
    ctx.set_source_rgba(*PAPER, 0.85)
    ctx.set_line_width(3.0)
    ctx.stroke_preserve()
    ctx.set_source_rgba(*col, 0.95)
    ctx.fill()
    ctx.restore()


def draw_line(ctx, lonlat, rgb, width, alpha=0.95, dash=None):
    x, y = to_px(lonlat[:, 0], lonlat[:, 1])
    ctx.new_path()
    ctx.move_to(x[0], y[0])
    for k in range(1, len(x)):
        ctx.line_to(x[k], y[k])
    if dash:
        ctx.set_dash(dash)
    ctx.set_source_rgba(*rgb, alpha)
    ctx.set_line_width(width)
    ctx.stroke()
    ctx.set_dash([])


def markers_along(lonlat, n):
    seg = np.r_[0, np.cumsum(np.hypot(np.diff(lonlat[:, 0]) * np.cos(np.radians(lonlat[:-1, 1])), np.diff(lonlat[:, 1])))]
    targets = np.linspace(0, seg[-1], n)
    return np.stack([np.interp(targets, seg, lonlat[:, 0]), np.interp(targets, seg, lonlat[:, 1])], 1)


def draw_marker(ctx, lon, lat, num, rgb, dx_px, dy_px):
    stretch = 1.0 / math.cos(math.radians(lat))
    x, y = to_px(lon, lat)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(stretch, 1.0)
    ctx.new_path()
    ctx.move_to(0, -7)
    ctx.line_to(6.5, 5)
    ctx.line_to(-6.5, 5)
    ctx.close_path()
    ctx.set_source_rgba(*PAPER, 0.95)
    ctx.fill_preserve()
    ctx.set_source_rgba(*rgb, 1.0)
    ctx.set_line_width(1.8)
    ctx.stroke()
    ctx.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(13)
    s = str(num)
    tw = ctx.text_extents(s).x_advance
    ctx.new_path()
    ctx.move_to(dx_px - tw / 2, dy_px + 4)
    ctx.text_path(s)
    ctx.set_source_rgba(*PAPER, 0.85)
    ctx.set_line_width(2.6)
    ctx.stroke_preserve()
    ctx.set_source_rgba(*rgb, 1.0)
    ctx.fill()
    ctx.restore()


def main():
    os.makedirs(OUT, exist_ok=True)
    axis = boundary_axis()
    to_m = Transformer.from_crs("EPSG:4326", "+proj=aeqd +lat_0=50 +lon_0=93 +datum=WGS84", always_xy=True)
    to_ll = Transformer.from_crs("+proj=aeqd +lat_0=50 +lon_0=93 +datum=WGS84", "EPSG:4326", always_xy=True)
    # resample the axis every ~3 km so offsets and markers are even
    ax_m = np.stack(to_m.transform(axis[:, 0], axis[:, 1]), 1)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ax_m, axis=0), axis=1))]
    s = np.arange(0, seg[-1], 3000.0)
    ax_m = np.stack([np.interp(s, seg, ax_m[:, 0]), np.interp(s, seg, ax_m[:, 1])], 1)
    lon_axis = np.asarray(to_ll.transform(ax_m[:, 0], ax_m[:, 1])[0])

    # which side is Mongolia: test a point a little to the left of the axis midpoint
    mong = shp_transform(lambda x, y, z=None: to_m.transform(x, y), mongolia_polygon())
    mid = len(ax_m) // 2
    tvec = ax_m[mid + 1] - ax_m[mid - 1]
    left = np.array([-tvec[1], tvec[0]]) / np.linalg.norm(tvec)
    mong_side = 1.0 if mong.contains(Point(*(ax_m[mid] + left * 20000))) else -1.0

    red_m = offset_line(ax_m, lon_axis, RED_OFFSET, mong_side, 1953)          # R'lyeh claims into Mongolia
    vio_m = offset_line(ax_m, lon_axis, VIOLET_OFFSET, -mong_side, 3591)      # Urga claims into the Union
    red = np.stack(to_ll.transform(red_m[:, 0], red_m[:, 1]), 1)
    vio = np.stack(to_ll.transform(vio_m[:, 0], vio_m[:, 1]), 1)
    strip = shapely.make_valid(Polygon(np.vstack([red, vio[::-1]]))).buffer(0)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    # 1. disputed strip: pale wash + cross-hatching, red one way, violet the other
    ctx.save()
    ctx.new_path()
    for poly in getattr(strip, "geoms", [strip]):
        if poly.geom_type != "Polygon":
            continue
        c = np.asarray(poly.exterior.coords)
        x, y = to_px(c[:, 0], c[:, 1])
        ctx.move_to(x[0], y[0])
        for k in range(1, len(x)):
            ctx.line_to(x[k], y[k])
        ctx.close_path()
    ctx.set_source_rgba(*PAPER, 0.35)
    ctx.fill_preserve()
    ctx.clip()
    x0, y0 = to_px(84.0, 54.0)
    x1, y1 = to_px(102.0, 45.0)
    for rgb, sgn in ((RED, 1), (VIOLET, -1)):
        ctx.new_path()
        for xx in np.arange(x0 - (y1 - y0), x1 + (y1 - y0), 5.0):
            ctx.move_to(xx, y0)
            ctx.line_to(xx + sgn * (y1 - y0), y1)
        ctx.set_source_rgba(*rgb, 0.55)
        ctx.set_line_width(0.9)
        ctx.stroke()
    ctx.restore()

    # 2. the two claim lines (a faint dotted trace of the actual boundary between them)
    draw_line(ctx, axis, INK, 0.8, 0.45, dash=[1.5, 4])
    draw_line(ctx, red, RED, 3.2)
    draw_line(ctx, vio, VIOLET, 3.2)

    # 3. markers 1..N on each line, both No. 1 at the peak
    red_mk = markers_along(red, N_MARKERS)
    vio_mk = markers_along(vio, N_MARKERS)
    for k, (lo, la) in enumerate(red_mk):
        draw_marker(ctx, lo, la, k + 1, RED, 0, 19 if k else 20)
    for k, (lo, la) in enumerate(vio_mk):
        draw_marker(ctx, lo, la, k + 1, VIOLET, 0 if k else -14, -12 if k else -10)

    # 4. labels
    feats = []
    for text, lo, la, size, style in LABELS:
        put_text(ctx, text, lo, la, size, style, angle=-0.12 if style == "red_hand" else 0.0)
        feats.append({"type": "Feature", "properties": {"kind": "label", "text": text, "style": style},
                      "geometry": {"type": "Point", "coordinates": [lo, la]}})

    surf.flush()
    png = os.path.join(OUT, "altai_border_1953.png")
    surf.write_to_png(png)

    rnd = lambda arr: [[round(float(a), 4), round(float(b), 4)] for a, b in arr]
    feats += [
        {"type": "Feature", "properties": {"kind": "boundary_axis", "note": "actual Union-Mongolia boundary"},
         "geometry": {"type": "LineString", "coordinates": rnd(axis)}},
        {"type": "Feature", "properties": {"kind": "claim", "side": "R'lyeh", "ru": "межа по притязанію Р'льеха"},
         "geometry": {"type": "LineString", "coordinates": rnd(red)}},
        {"type": "Feature", "properties": {"kind": "claim", "side": "Urga", "ru": "межа по притязанію Урги"},
         "geometry": {"type": "LineString", "coordinates": rnd(vio)}},
        {"type": "Feature", "properties": {"kind": "disputed_strip", "ru": "спорная полоса"},
         "geometry": mapping(shapely.set_precision(strip, 1e-4))},
    ]
    for side, mk in (("R'lyeh", red_mk), ("Urga", vio_mk)):
        for k, (lo, la) in enumerate(mk):
            feats.append({"type": "Feature", "properties": {"kind": "marker", "side": side, "no": k + 1},
                          "geometry": {"type": "Point", "coordinates": [round(float(lo), 4), round(float(la), 4)]}})
    meta = {"title": "Алтайская межа. Протокольная карта смѣшанной разграничительной комиссіи, 1953 г.",
            "projection": "equirectangular, lon -180..180, lat 90..-90", "size": [W, H]}
    with open(os.path.join(OUT, "altai_border_1953.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "properties": meta, "features": feats}, f, ensure_ascii=False)
    km2 = abs(shapely.area(shp_transform(lambda x, y, z=None: to_m.transform(x, y), strip))) / 1e6
    print(png, "axis points", len(axis), "strip km2", round(km2))


if __name__ == "__main__":
    main()
