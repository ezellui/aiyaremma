#!/usr/bin/env python3
"""Synoptic overlay 'Карта споровыхъ облаковъ на 14 сентября 1947 г.' for the R.S.F.G.R. globe.

Output (out/overlay/):
  spores_1947.png      equirectangular RGBA, 8192x4096, lon -180..180 left to right, lat 90..-90 top to bottom,
                       transparent background — drapes over any globe texture of that layout
  spores_1947.geojson  the same content as vectors (isolines with 'level', fronts, arrows, salt belt, labels)

The field is invented but deterministic: a spore plume from R'lyeh (Kara Sea coast) carried east by the
westerlies over Siberia and Chukotka, across the Bering Strait into Alaska and the Yukon.
Labels are pre-stretched by 1/cos(lat) so that they look undistorted on the globe.
"""
import json
import math
import os

import cairo
import numpy as np
from matplotlib import contour as mcontour  # noqa: F401  (backend-free contour generator below)
from contourpy import contour_generator
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "overlay")
CACHE = os.path.join(HERE, "cache")
W, H = 8192, 4096
LON0 = -20.0          # field is computed on lon' in [LON0, LON0+360) so the plume never crosses the seam
RES = 0.1             # degrees per field cell
SERIF = "Old Standard TT"

INK = (0.16, 0.13, 0.10)
GREEN = (0.30, 0.38, 0.24)
RED = (0.66, 0.16, 0.11)
SALT = (0.97, 0.96, 0.92)

LEVELS = [10, 30, 100, 300, 1000]  # spores per cubic sazhen
PLUME = [  # (lon, lat, intensity, half-width km): the 1947 cloud from R'lyeh to the Yukon
    (74.6, 71.1, 1.00, 420), (88, 70.5, 0.95, 480), (105, 69, 0.90, 560), (122, 67.5, 0.86, 620),
    (140, 67, 0.80, 640), (158, 66.5, 0.74, 640), (172, 66.2, 0.70, 600), (-172, 65.8, 0.66, 560),
    (-160, 65.5, 0.58, 560), (-150, 64.8, 0.50, 560), (-140, 63.8, 0.40, 520), (-131, 62.5, 0.30, 460),
]
BACKGROUND = [  # diffuse spore fields over the Union's mycelia (lon, lat, intensity, radius km)
    (40, 57, 0.30, 900), (58, 60, 0.28, 800), (85, 58, 0.30, 1000), (115, 60, 0.32, 1100),
    (135, 52, 0.24, 700), (65, 46, 0.14, 900), (30, 50, 0.22, 700), (155, 62, 0.30, 700),
]
FRONT = [(-163, 71.5), (-152, 69.5), (-143, 67.0), (-134, 64.6), (-128, 61.8), (-127, 58.6), (-131, 56.0)]
ARROW_PATHS = [  # westerly transport streamlines (lon, lat)
    [(20, 61), (40, 63), (60, 65), (78, 67)],
    [(48, 56), (70, 58), (92, 60), (112, 61.5)],
    [(98, 64), (120, 64.5), (142, 64.8), (162, 65.2)],
    [(150, 60), (165, 62.5), (180, 64.2), (-168, 65.0)],
    [(-176, 67.5), (-162, 66.6), (-150, 65.6), (-139, 64.2)],
    [(60, 50), (82, 51), (104, 52), (124, 52.5)],
]
LABELS = [  # text, lon, lat, size px (at equator; stretched by 1/cos lat), style
    ("ВЕЛИКОЕ ПЛОДОНОШЕНІЕ", 118, 71.4, 34, "caps_green"),
    ("западный переносъ", 62, 52.6, 26, "italic"),
    ("западный переносъ", 125, 56.6, 26, "italic"),
    ("Облако перешло проливъ!", -168, 61.2, 30, "red_hand"),
    ("споровой фронтъ", -122, 66.4, 24, "italic"),
    ("соляной поясъ", 26.5, 64.6, 22, "italic_grey"),
    ("соляной поясъ", 46.5, 36.6, 22, "italic_grey"),
]


def to_px(lon, lat):
    return (np.asarray(lon) + 180.0) / 360.0 * W, (90.0 - np.asarray(lat)) / 180.0 * H


def gc_dist_km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    d = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(d, 0, 1)))


def shifted(lon):
    return (np.asarray(lon) - LON0) % 360.0 + LON0


def build_field():
    lons = LON0 + np.arange(0, 360, RES) + RES / 2
    lats = np.arange(90, -90, -RES) - RES / 2
    LON, LAT = np.meshgrid(lons, lats)
    F = np.zeros_like(LON)
    # plume: densify the control polyline and sum gaussians along it
    pts = []
    for (a, b) in zip(PLUME[:-1], PLUME[1:]):
        la0, la1 = shifted(a[0]), shifted(b[0])
        for t in np.linspace(0, 1, 14, endpoint=False):
            pts.append((la0 + (la1 - la0) * t, a[1] + (b[1] - a[1]) * t,
                        a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t))
    pts.append((shifted(PLUME[-1][0]), *PLUME[-1][1:]))
    box = (LAT > 35) & (LAT < 85)
    for lo, la, amp, wkm in pts:
        d = gc_dist_km(LON[box], LAT[box], lo, la)
        F[box] = np.maximum(F[box], amp * np.exp(-(d / wkm) ** 2))
    for lo, la, amp, rkm in BACKGROUND:
        d = gc_dist_km(LON[box], LAT[box], shifted(lo), la)
        F[box] += amp * np.exp(-(d / rkm) ** 2)
    rng = np.random.default_rng(1947)  # gentle irregularity so the isolines look hand-analysed
    noise = gaussian_filter(rng.normal(0, 1, F.shape), 28)
    noise /= np.abs(noise).max()
    F = F * (1 + 0.22 * noise)
    conc = 2.2 * 10 ** (3.3 * np.clip(F, 0, None)) - 2.2  # log-like scale: core ~ 4000 spores/cu.sazhen
    return lons, lats, conc


def unwrap_lines(coords):
    """lon' in [LON0, LON0+360) -> list of lon/lat lines in [-180, 180], split at the antimeridian."""
    out, cur = [], []
    prev = None
    for lo, la in coords:
        x = ((lo + 180) % 360) - 180
        if prev is not None and abs(x - prev) > 180:
            if len(cur) > 1:
                out.append(cur)
            cur = []
        cur.append([round(float(x), 4), round(float(la), 4)])
        prev = x
    if len(cur) > 1:
        out.append(cur)
    return out


def draw_path_wrapped(ctx, lonlat):
    """lonlat in continuous lon' (may exceed 180): draw at x, x-W and x+W so the seam is covered."""
    lo = np.array([p[0] for p in lonlat])
    la = np.array([p[1] for p in lonlat])
    x, y = to_px(lo, la)
    for off in (-W, 0, W):
        xs = x + off
        if xs.max() < 0 or xs.min() > W:
            continue
        ctx.move_to(xs[0], y[0])
        for k in range(1, len(xs)):
            ctx.line_to(xs[k], y[k])


def put_text(ctx, text, lon, lat, size, style, angle=0.0, anchor="center"):
    stretch = 1.0 / max(math.cos(math.radians(lat)), 0.2)
    slant = cairo.FONT_SLANT_ITALIC if "italic" in style or "hand" in style else cairo.FONT_SLANT_NORMAL
    weight = cairo.FONT_WEIGHT_BOLD if style in ("caps_green", "red_hand") else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(SERIF, slant, weight)
    ctx.set_font_size(size)
    spacing = 0.22 * size if style == "caps_green" else 0.0
    ext = [ctx.text_extents(ch).x_advance for ch in text]
    tw = sum(ext) + spacing * (len(text) - 1)
    x, y = to_px(shifted(lon) if lon > 180 else lon, lat)
    col = {"caps_green": GREEN, "italic": INK, "red_hand": RED, "italic_grey": (0.38, 0.36, 0.33)}[style]
    for off in (-W, 0, W):
        xx = x + off
        if xx < -tw * stretch or xx > W + tw * stretch:
            continue
        ctx.save()
        ctx.translate(xx, y)
        ctx.rotate(angle)
        ctx.scale(stretch, 1.0)
        cx = -tw / 2 if anchor == "center" else 0
        ctx.new_path()
        for ch, adv in zip(text, ext):
            ctx.move_to(cx, size * 0.35)
            ctx.text_path(ch)
            cx += adv + spacing
        ctx.set_source_rgba(0.96, 0.93, 0.85, 0.85)
        ctx.set_line_width(3.2)
        ctx.stroke_preserve()
        ctx.set_source_rgba(*col, 0.95)
        ctx.fill()
        ctx.restore()


def local_dir(lon1, lat1, lon2, lat2):
    """direction (radians, screen coords: x right, y down) of a short step on the equirectangular image,
    corrected so that on the globe it looks like the true bearing."""
    dx = ((lon2 - lon1 + 180) % 360 - 180) * math.cos(math.radians((lat1 + lat2) / 2))
    dy = -(lat2 - lat1)
    return math.atan2(dy, dx)


def salt_belt_lines():
    """borders between the Union of 1947 and the 'salted' neighbours (Finland, Turkey, Persia), from the arc cache."""
    regions = json.load(open(os.path.join(CACHE, "regions.json"), encoding="utf-8"))
    a = np.load(os.path.join(CACHE, "arcs.npz"))
    xy, lens, left, right = a["xy"], a["lens"], a["left"], a["right"]
    off = np.r_[0, np.cumsum(lens)]
    salted = {"Finland", "Turkey", "Iran"}
    union = {"Russia", "Georgia", "Armenia", "Azerbaijan", "Turkmenistan", "Estonia"}
    adm = [r["admin"] for r in regions]
    lines = []
    for k in range(len(lens)):
        l, r = left[k], right[k]
        if r < 0:
            continue
        pair = {adm[l], adm[r]}
        if pair & salted and pair & union and len(pair) == 2:
            lines.append(xy[off[k]:off[k + 1]].astype(float).tolist())
    return lines


def main():
    os.makedirs(OUT, exist_ok=True)
    lons, lats, conc = build_field()
    gen = contour_generator(x=lons, y=lats, z=conc, line_type="Separate", fill_type="OuterOffset")

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    feats = []

    # 1. translucent washes between isolines (darker = denser), hatching in the core
    for k, lv in enumerate(LEVELS):
        polys, offsets = gen.filled(lv, 1e9)
        alpha = 0.06 + 0.055 * k
        for pts, offs in zip(polys, offsets):
            ctx.new_path()
            for s, e in zip(offs[:-1], offs[1:]):
                draw_path_wrapped(ctx, pts[s:e].tolist())
                ctx.close_path()
            ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            ctx.set_source_rgba(*GREEN, alpha)
            ctx.fill()
    hatch_polys, hatch_offs = gen.filled(300, 1e9)
    ctx.save()
    ctx.new_path()
    for pts, offs in zip(hatch_polys, hatch_offs):
        for s, e in zip(offs[:-1], offs[1:]):
            draw_path_wrapped(ctx, pts[s:e].tolist())
            ctx.close_path()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.clip()
    ctx.new_path()
    for x in range(-H, W + H, 9):
        ctx.move_to(x, 0)
        ctx.line_to(x + H * 0.6, H)
    ctx.set_source_rgba(*GREEN, 0.35)
    ctx.set_line_width(1.0)
    ctx.stroke()
    ctx.restore()

    # 2. isolines with level labels
    for lv in LEVELS:
        lines = gen.lines(lv)
        ctx.new_path()
        for ln in lines:
            if len(ln) < 8:
                continue
            draw_path_wrapped(ctx, ln.tolist())
            for part in unwrap_lines(ln.tolist()):
                feats.append({"type": "Feature", "properties": {"kind": "isospore", "level": lv,
                                                                  "unit": "споръ на куб. сажень"},
                              "geometry": {"type": "LineString", "coordinates": part}})
        ctx.set_source_rgba(*INK, 0.78 if lv >= 100 else 0.6)
        ctx.set_line_width(2.4 if lv in (100, 1000) else 1.5)
        ctx.stroke()
        for ln in lines:
            if len(ln) < 60:
                continue
            j = len(ln) // 3
            lo, la = ln[j]
            ang = local_dir(ln[j - 3][0], ln[j - 3][1], ln[j + 3][0], ln[j + 3][1])
            if abs(ang) > math.pi / 2:
                ang += math.pi
            put_text(ctx, str(lv), lo, la, 20, "italic", angle=0.0)

    # 3. westerly transport arrows (black, dashed shaft, solid head)
    for path in ARROW_PATHS:
        dense = []
        for (a, b) in zip(path[:-1], path[1:]):
            la0, la1 = shifted(a[0]), shifted(b[0])
            if la1 < la0:
                la1 += 360
            for t in np.linspace(0, 1, 20, endpoint=False):
                dense.append((la0 + (la1 - la0) * t, a[1] + (b[1] - a[1]) * t))
        last = (shifted(path[-1][0]), path[-1][1])
        if last[0] < dense[-1][0] - 180:
            last = (last[0] + 360, last[1])
        dense.append(last)
        ctx.new_path()
        draw_path_wrapped(ctx, dense)
        ctx.set_dash([14, 9])
        ctx.set_source_rgba(*INK, 0.82)
        ctx.set_line_width(2.6)
        ctx.stroke()
        ctx.set_dash([])
        (lo1, la1), (lo2, la2) = dense[-4], dense[-1]
        ang = local_dir(lo1, la1, lo2, la2)
        stretch = 1.0 / math.cos(math.radians(la2))
        for off in (-W, 0, W):
            x, y = to_px(lo2, la2)
            x += off
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(stretch, 1.0)
            ctx.rotate(ang)
            ctx.new_path()
            ctx.move_to(0, 0)
            ctx.line_to(-30, -12)
            ctx.line_to(-24, 0)
            ctx.line_to(-30, 12)
            ctx.close_path()
            ctx.set_source_rgba(*INK, 0.9)
            ctx.fill()
            ctx.restore()
        for part in unwrap_lines(dense):
            feats.append({"type": "Feature", "properties": {"kind": "transport_arrow"},
                          "geometry": {"type": "LineString", "coordinates": part}})

    # 4. spore front: a heavy line with mushroom caps on the advancing (eastern) side
    fr = [(shifted(lo), la) for lo, la in FRONT]
    dense = []
    for a, b in zip(fr[:-1], fr[1:]):
        for t in np.linspace(0, 1, 30, endpoint=False):
            dense.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    dense.append(fr[-1])
    ctx.new_path()
    draw_path_wrapped(ctx, dense)
    ctx.set_source_rgba(*RED, 0.95)
    ctx.set_line_width(4.0)
    ctx.stroke()
    for k in range(8, len(dense) - 4, 22):
        (lo1, la1), (lo2, la2) = dense[k - 2], dense[k + 2]
        ang = local_dir(lo1, la1, lo2, la2)
        lo, la = dense[k]
        stretch = 1.0 / math.cos(math.radians(la))
        x, y = to_px(lo, la)
        for off in (-W, 0, W):
            ctx.save()
            ctx.translate(x + off, y)
            ctx.scale(stretch, 1.0)
            ctx.rotate(ang - math.pi / 2)  # cap points to the right of the line direction (east)
            ctx.new_path()
            ctx.rectangle(-3, 0, 6, 12)
            ctx.arc(0, 16, 13, 0, math.pi)
            ctx.close_path()
            ctx.set_source_rgba(*RED, 0.95)
            ctx.fill()
            ctx.restore()
    for part in unwrap_lines(dense):
        feats.append({"type": "Feature", "properties": {"kind": "spore_front"},
                      "geometry": {"type": "LineString", "coordinates": part}})

    # 5. salt belt along the borders with the salted neighbours
    rng = np.random.default_rng(7)
    for ln in salt_belt_lines():
        ctx.new_path()
        draw_path_wrapped(ctx, ln)
        ctx.set_source_rgba(*SALT, 0.9)
        ctx.set_line_width(13)
        ctx.stroke()
        ctx.new_path()
        draw_path_wrapped(ctx, ln)
        ctx.set_source_rgba(0.45, 0.43, 0.40, 0.8)
        ctx.set_line_width(1.2)
        ctx.set_dash([2, 6])
        ctx.stroke()
        ctx.set_dash([])
        arr = np.array(ln)
        x, y = to_px(arr[:, 0], arr[:, 1])
        for _ in range(max(2, len(arr) // 2)):
            j = rng.integers(0, len(arr))
            ctx.rectangle(x[j] + rng.normal(0, 4), y[j] + rng.normal(0, 4), 2.2, 2.2)
        ctx.set_source_rgba(0.55, 0.53, 0.50, 0.9)
        ctx.fill()
        feats.append({"type": "Feature", "properties": {"kind": "salt_belt"},
                      "geometry": {"type": "LineString", "coordinates": [[round(p[0], 4), round(p[1], 4)] for p in ln]}})

    # 6. labels
    for text, lo, la, size, style in LABELS:
        put_text(ctx, text, lo, la, size, style)
        feats.append({"type": "Feature", "properties": {"kind": "label", "text": text, "style": style},
                      "geometry": {"type": "Point", "coordinates": [lo, la]}})
    # a red pencil ring round the Bering Strait
    stretch = 1.0 / math.cos(math.radians(65.8))
    for off in (-W, 0, W):
        x, y = to_px(-169.0, 65.8)
        ctx.save()
        ctx.translate(x + off, y)
        ctx.scale(stretch, 1.0)
        ctx.new_path()
        ctx.arc(0, 0, 70, 0.3, 2 * math.pi + 0.9)
        ctx.set_source_rgba(*RED, 0.85)
        ctx.set_line_width(4.5)
        ctx.stroke()
        ctx.restore()

    surf.flush()
    png = os.path.join(OUT, "spores_1947.png")
    surf.write_to_png(png)
    meta = {"title": "Карта споровыхъ облаковъ на 14 сентября 1947 г., 00 ч. 13 м. (Споролѣтіе XXVII)",
            "projection": "equirectangular, lon -180..180, lat 90..-90", "size": [W, H]}
    with open(os.path.join(OUT, "spores_1947.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "properties": meta, "features": feats}, f, ensure_ascii=False)
    print(png, "features", len(feats), "max conc", int(conc.max()))


if __name__ == "__main__":
    main()
