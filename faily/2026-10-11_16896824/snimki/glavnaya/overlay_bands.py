#!/usr/bin/env python3
"""Belts along a border, as GeoJSON layers for the globe (drawn by render_archive.py as vector overlays).

  salt_belt_1939   — the Salt Belt: a strip on the waking side of the border between the Union and
                     Finland, Turkey and Persia (state of the map right after the event "salt");
  waite_belt_1963  — the Waite Belt: a chain of space stabilisers on the waking side of the western border
                     of the grafted lands in Europe (state of the map right after the event "waite").

The strip is built in an azimuthal equidistant projection centred on the border, so its width is in km.
Output: overlays/<name>.geojson with features kind = "band" (polygon), "edge" (line: the border itself),
"station" (points of the Waite chain).
"""
import json
import math
import os
import sys
import warnings

import numpy as np
import shapely
from pyproj import Transformer
from shapely.geometry import LineString, Point, mapping, shape
from shapely.ops import linemerge, transform as shp_transform, unary_union

from history import History

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
REGIONS = os.path.join(HERE, "..", "maps_extract", "unified", "unified_regions.geojson")


def border_lines(h, conf, side_a, side_b, lon_box=None):
    """the border arcs between regions whose state is in side_a and regions whose state is in side_b,
    merged into lines; each line comes with the side_a polygon test."""
    a = np.load(os.path.join(HERE, "cache", "arcs.npz"))
    xy, lens, left, right = a["xy"].astype(float), a["lens"], a["left"], a["right"]
    off = np.r_[0, np.cumsum(lens)]
    parts = []
    for k in range(len(lens)):
        l, r = left[k], right[k]
        if r < 0:
            continue
        sl, sr = int(conf[l]), int(conf[r])
        if not ((sl in side_a and sr in side_b) or (sr in side_a and sl in side_b)):
            continue
        seg = xy[off[k]:off[k + 1]]
        if lon_box is not None:
            mid = seg[len(seg) // 2]
            if not (lon_box[0] <= mid[0] <= lon_box[2] and lon_box[1] <= mid[1] <= lon_box[3]):
                continue
        parts.append(LineString(seg))
    if not parts:
        return None
    return linemerge(unary_union(parts))


def side_polygon(h, conf, side_a):
    feats = json.load(open(REGIONS, encoding="utf-8"))["features"]
    keys = {r["key"]: i for i, r in enumerate(h.regions)}
    polys = [shape(f["geometry"]) for f in feats if int(conf[keys[f["properties"]["key"]]]) in side_a]
    return shapely.union_all(polys)


def build(name, scenario, event_id, a_ids, b_pred, width_km, lon_box=None, stations_km=None):
    h = History(scenario)
    step = h.event_step[event_id]
    conf = h.configs[step]
    a_set = {h.sid[x] for x in a_ids if x in h.sid}
    b_set = {s for s in set(np.unique(conf).tolist()) if b_pred(h, s)}
    lines = border_lines(h, conf, a_set, b_set, lon_box)
    if lines is None:
        raise SystemExit(f"{name}: no border found")
    poly_a = side_polygon(h, conf, a_set)
    c = lines.centroid
    to_m = Transformer.from_crs("EPSG:4326", f"+proj=aeqd +lat_0={c.y:.3f} +lon_0={c.x:.3f} +datum=WGS84", always_xy=True)
    to_ll = Transformer.from_crs(f"+proj=aeqd +lat_0={c.y:.3f} +lon_0={c.x:.3f} +datum=WGS84", "EPSG:4326", always_xy=True)
    fwd = lambda g: shp_transform(lambda x, y, z=None: to_m.transform(x, y), g)
    back = lambda g: shp_transform(lambda x, y, z=None: to_ll.transform(x, y), g)
    lines_m = fwd(lines)
    poly_m = fwd(poly_a).buffer(0)
    band_m = lines_m.buffer(width_km * 1000.0, cap_style="flat").intersection(poly_m)
    band_m = shapely.make_valid(band_m).buffer(0)
    feats = [{"type": "Feature", "properties": {"kind": "band", "width_km": width_km},
              "geometry": mapping(shapely.set_precision(back(band_m), 1e-4))},
             {"type": "Feature", "properties": {"kind": "edge"},
              "geometry": mapping(shapely.set_precision(lines, 1e-4))}]
    if stations_km:
        n_st = 0
        for ln in getattr(lines_m, "geoms", [lines_m]):
            L = ln.length
            for s in np.arange(stations_km * 0.5, L, stations_km * 1000.0):
                p = ln.interpolate(s)
                q = ln.interpolate(min(L, s + 500))
                q0 = ln.interpolate(max(0, s - 500))
                tx, ty = q.x - q0.x, q.y - q0.y
                nrm = math.hypot(tx, ty) or 1.0
                nx, ny = -ty / nrm, tx / nrm
                for sgn in (1, -1):
                    cand = Point(p.x + sgn * nx * width_km * 500.0, p.y + sgn * ny * width_km * 500.0)
                    if poly_m.contains(cand):
                        ll = to_ll.transform(cand.x, cand.y)
                        feats.append({"type": "Feature", "properties": {"kind": "station"},
                                      "geometry": {"type": "Point", "coordinates": [round(ll[0], 4), round(ll[1], 4)]}})
                        n_st += 1
                        break
        print(f"  stations: {n_st}")
    os.makedirs(os.path.join(HERE, "overlays"), exist_ok=True)
    out = os.path.join(HERE, "overlays", name + ".geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    km = lines_m.length / 1000.0
    print(f"{out}: border {km:.0f} km, band {band_m.area / 1e6:.0f} km²")


def main():
    scen = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "scenario_rsfgr.json")
    union = lambda h, s: h.states_by_idx[s]["origin"] == "event" and not h.states_by_idx[s].get("side")
    # the Salt Belt: Finland, Turkey and Persia salt their side of the border with the Union
    build("salt_belt_1939", scen, "salt", ["Finland", "Turkey", "Iran"], union, 28.0)
    # the Waite Belt: the waking states of Europe along the western border of the grafted lands
    awake_eu = ["Germany", "Austria", "Hungary", "Italy", "Greece", "Turkey", "Switzerland", "Denmark", "Finland",
                "Norway", "Sweden", "Netherlands", "Belgium", "France", "Luxembourg"]
    build("waite_belt_1963", scen, "waite", awake_eu, union, 16.0, lon_box=(-10, 35, 34, 72), stations_km=55)


if __name__ == "__main__":
    main()
