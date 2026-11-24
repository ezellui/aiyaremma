#!/usr/bin/env python3
"""Extract country and admin-region boundaries from USER/html-generated webmap assets.

Input  : webmap/assets/{borders.json, borders2.json, countries*.json, ids_real.png, ids_sim*.png}
Output : GeoJSON in WGS84 lon/lat (and the same in source pixel coordinates on request).

Geometry of the source map (recovered by fitting, see README):
  Robinson projection, lon_0 = 0, full width 3200 px = 360 deg,
  scale s = 1600 / X_robin(180 deg)  (~10.63 km/px at the equator),
  top edge = 84 deg N, vector coordinates are pixel-edge coordinates
  (pixel i covers [i, i+1]).

Usage:
  python3 webmap_extract.py <webmap/assets dir> <out dir> [--layer real|sim|sim2] [--pixels]
"""
import argparse
import collections
import json
import os
import sys

import numpy as np
from PIL import Image
from pyproj import Geod, Transformer
from rasterio.features import rasterize, shapes
from rasterio.transform import Affine
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, mapping, shape
from shapely.ops import nearest_points, polygonize_full, transform as shp_transform, unary_union
from shapely.strtree import STRtree

SNAP = 1.5            # px: max gap closed between a loose line end and another line
SLIVER_AREA = 0.35    # px^2: faces smaller than this are merged into a neighbour
SLIVER_THIN = 0.12    # isoperimetric ratio below which a small face counts as a sliver
SLIVER_THIN_AREA = 6  # px^2: ... if also smaller than this
MIX_SHARE = 0.15      # second country share above which a face is split by the id raster
SEGMENT = 2.0         # px: densify before reprojecting, so straight pixel segments bend correctly

GEOD = Geod(ellps="WGS84")


def robinson_pixel_transform(W, H):
    fwd = Transformer.from_crs("EPSG:4326", "+proj=robin +lon_0=0 +datum=WGS84", always_xy=True)
    inv = Transformer.from_crs("+proj=robin +lon_0=0 +datum=WGS84", "EPSG:4326", always_xy=True)
    xr180 = fwd.transform(180.0, 0.0)[0]
    s = (W / 2) / xr180
    y0 = fwd.transform(0.0, 84.0)[1] * s  # equator row measured from the top edge

    def px2ll(x, y, z=None):
        X = (np.asarray(x) - W / 2) / s
        Y = (y0 - np.asarray(y)) / s
        lon, lat = inv.transform(X, Y)
        return np.clip(lon, -180, 180), np.clip(lat, -90, 90)

    def ll2px(lon, lat, z=None):
        X, Y = fwd.transform(lon, lat)
        return W / 2 + np.asarray(X) * s, y0 - np.asarray(Y) * s

    return px2ll, ll2px, s, y0


def decode_ids(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(np.int32)
    return np.where(a[..., 3] == 0, -1, (a[..., 0] << 8) | a[..., 1])


def thinness(p):
    return 4 * np.pi * p.area / (p.length ** 2) if p.length > 0 else 1.0


def build_faces(lines, log):
    geoms = [LineString(l) for l in lines if len(l) >= 2]
    tree = STRtree(geoms)
    bridges = []
    for i, g in enumerate(geoms):
        if g.is_closed:
            continue
        for pt in (g.coords[0], g.coords[-1]):
            P = Point(pt)
            best = None
            for j in tree.query(P.buffer(SNAP)):
                if j == i:
                    continue
                d = geoms[j].distance(P)
                if best is None or d < best[0]:
                    best = (d, j)
            if best and 1e-9 < best[0] <= SNAP:
                q = nearest_points(P, geoms[best[1]])[1]
                bridges.append(LineString([pt, (q.x, q.y)]))
    net = unary_union(geoms + bridges)
    polys, dangles, cuts, invalid = polygonize_full(net)
    faces = list(polys.geoms)
    log(f"  lines {len(geoms)}, snap bridges {len(bridges)}, raw faces {len(faces)}, "
        f"unclosed pieces {len(cuts.geoms)} (total {sum(c.length for c in cuts.geoms):.0f} px)")
    return faces


def face_country_stats(faces, ids):
    fr = rasterize([(p, i + 1) for i, p in enumerate(faces)], out_shape=ids.shape,
                   transform=Affine.identity(), fill=0, dtype="int32")
    m = fr > 0
    key = fr[m].astype(np.int64) * 100000 + (ids[m] + 1)
    u, c = np.unique(key, return_counts=True)
    stats = collections.defaultdict(dict)
    for k, n in zip(u, c):
        stats[int(k // 100000) - 1][int(k % 100000) - 1] = int(n)
    return stats


def raster_country_polys(ids, cid):
    m = (ids == cid).astype(np.uint8)
    return unary_union([shape(g) for g, v in shapes(m, mask=m.astype(bool), transform=Affine.identity()) if v == 1])


def label_and_split(faces, ids, log):
    stats = face_country_stats(faces, ids)
    out = []  # (polygon, country id)
    split = 0
    for i, p in enumerate(faces):
        st = stats.get(i)
        if st:
            land = {k: v for k, v in st.items() if k >= 0}
            tot = sum(st.values())
            lt = sum(land.values())
            if lt < 0.5 * tot:
                continue  # sea / lake face
            ranked = sorted(land.items(), key=lambda kv: -kv[1])
            if len(ranked) > 1 and ranked[1][1] > MIX_SHARE * lt and ranked[1][1] >= 10:
                # a national border is missing from the line set here: cut the face by the id raster
                rest = p
                for cid, n in ranked:
                    if n < 3:
                        continue
                    part = p.intersection(raster_country_polys(ids, cid))
                    if not part.is_empty:
                        for g in getattr(part, "geoms", [part]):
                            if g.geom_type == "Polygon" and g.area > 0:
                                out.append((g, cid))
                        rest = rest.difference(part)
                for g in getattr(rest, "geoms", [rest]):
                    if g.geom_type == "Polygon" and g.area > 0:
                        out.append((g, ranked[0][0]))
                split += 1
                continue
            out.append((p, ranked[0][0]))
        else:
            pt = p.representative_point()
            x, y = int(pt.x), int(pt.y)
            win = ids[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            v = win[win >= 0]
            if len(v) * 2 < win.size:
                # mostly sea around: keep only if it is a closed coastline ring (islet) touching land pixels
                if not len(v):
                    continue
            out.append((p, int(np.bincount(v).argmax())))
    log(f"  land faces {len(out)}, faces cut by raster {split}")
    return out


def merge_slivers(items, log):
    polys = [p for p, _ in items]
    cids = [c for _, c in items]
    alive = [True] * len(polys)
    tree = STRtree(polys)

    def is_sliver(p):
        return p.area < SLIVER_AREA or (p.area < SLIVER_THIN_AREA and thinness(p) < SLIVER_THIN)

    order = sorted(range(len(polys)), key=lambda i: polys[i].area)
    merged = 0
    owner = list(range(len(polys)))

    def find(i):
        while owner[i] != i:
            owner[i] = owner[owner[i]]
            i = owner[i]
        return i

    cur = list(polys)
    for i in order:
        if not alive[i] or not is_sliver(cur[i]):
            continue
        best = None
        for j0 in tree.query(cur[i].buffer(0.05)):
            j = find(int(j0))
            if j == i or not alive[j]:
                continue
            shared = cur[i].boundary.intersection(cur[j].buffer(0.05)).length
            if shared <= 0:
                continue
            score = (cids[j] == cids[i], shared)
            if best is None or score > best[0]:
                best = (score, j)
        if best is None:
            continue  # isolated islet: keep it
        j = best[1]
        cur[j] = unary_union([cur[j], cur[i]]).buffer(0)
        alive[i] = False
        owner[i] = j
        merged += 1
    res = [(cur[i], cids[i]) for i in range(len(cur)) if alive[i]]
    log(f"  slivers merged {merged}, regions left {len(res)}")
    return res


def to_ll(geom, px2ll):
    g = geom.segmentize(SEGMENT) if SEGMENT else geom
    return shp_transform(lambda x, y, z=None: px2ll(x, y), g)


def geod_area_km2(g):
    return abs(GEOD.geometry_area_perimeter(g)[0]) / 1e6


def fc(features):
    return {"type": "FeatureCollection", "features": features}


def write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def round_geom(g, nd):
    return shp_transform(lambda x, y, z=None: (np.round(x, nd), np.round(y, nd)), g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assets")
    ap.add_argument("out")
    ap.add_argument("--layer", choices=["real", "sim", "sim2"], default="real")
    ap.add_argument("--pixels", action="store_true", help="also write pixel-coordinate GeoJSON")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    log = lambda s: print(s, file=sys.stderr)

    meta = json.load(open(os.path.join(a.assets, "meta.json")))
    W, H = meta["W"], meta["H"]
    px2ll, ll2px, s, y0 = robinson_pixel_transform(W, H)

    B = json.load(open(os.path.join(a.assets, "borders.json")))
    if a.layer == "real":
        nat, adm, idsf, cf = B["nat_real"], B["adm_real"], "ids_real.png", "countries.json"
    elif a.layer == "sim":
        nat, adm, idsf, cf = B["nat_sim"], B["adm_sim"], "ids_sim.png", "countries.json"
    else:
        B2 = json.load(open(os.path.join(a.assets, "borders2.json")))
        nat, adm, idsf, cf = B2["nat_sim"], B2["adm_sim"], "ids_sim2.png", "countries2.json"
    C = json.load(open(os.path.join(a.assets, cf)))
    ids = decode_ids(os.path.join(a.assets, idsf))
    sfx = a.layer
    log(f"[{sfx}] W={W} H={H} km/px={1 / s / 1000:.2f} equator_row={y0:.2f}")

    # 1. raw line layers
    for name, lines in [("coast", B["coast"]), ("national", nat), ("admin", adm)]:
        feats = []
        for l in lines:
            if len(l) < 2:
                continue
            g = round_geom(to_ll(LineString(l), px2ll), 5)
            feats.append({"type": "Feature", "properties": {"kind": name}, "geometry": mapping(g)})
        write(os.path.join(a.out, f"lines_{name}_{sfx}.geojson" if name != "coast" else "lines_coast.geojson"), fc(feats))

    # 2. faces of the full line network
    faces = build_faces(B["coast"] + nat + adm, log)
    items = label_and_split(faces, ids, log)
    regions = merge_slivers(items, log)

    # countries present in the id raster only as a few pixels (no coastline ring survived simplification)
    have = {cid for _, cid in regions}
    extra = 0
    for cid in np.unique(ids[ids >= 0]).tolist():
        if cid not in have:
            g = raster_country_polys(ids, cid)
            for part in getattr(g, "geoms", [g]):
                regions.append((part, cid))
                extra += 1
    log(f"  raster-only micro-territories added: {extra} polygons")

    # island flag: the part's whole outline lies on coastline (no admin/national line touches it)
    coast_buf = unary_union([LineString(l) for l in B["coast"] if len(l) >= 2]).buffer(0.25)
    def on_coast_only(p):
        b = p.boundary
        return b.difference(coast_buf).length <= max(1.0, 0.02 * b.length)

    def cprops(cid):
        c = C.get(str(cid), {})
        return {"country_id": cid, "iso_a3": c.get("a3"), "name_ru": c.get("ru"), "name_en": c.get("en")}

    # 3. regions (faces of the admin network; a multi-part region appears as several features)
    regions.sort(key=lambda t: (t[1], -t[0].area))
    rfeats, rfeats_px = [], []
    per_country = collections.Counter()
    for k, (p, cid) in enumerate(regions):
        per_country[cid] += 1
        gl = to_ll(p, px2ll).buffer(0)
        props = {"region_id": k, **cprops(cid), "region_no": per_country[cid],
                 "island": bool(on_coast_only(p)),
                 "area_km2": round(geod_area_km2(gl), 1), "area_px": round(p.area, 2)}
        rfeats.append({"type": "Feature", "properties": props, "geometry": mapping(round_geom(gl, 5))})
        if a.pixels:
            rfeats_px.append({"type": "Feature", "properties": props, "geometry": mapping(round_geom(p, 2))})
    write(os.path.join(a.out, f"regions_{sfx}.geojson"), fc(rfeats))

    # 4. countries = dissolve of regions
    by = collections.defaultdict(list)
    for p, cid in regions:
        by[cid].append(p)
    cfeats, cfeats_px = [], []
    for cid in sorted(by):
        gp = unary_union([q.buffer(0.02) for q in by[cid]]).buffer(-0.02)
        gl = to_ll(gp, px2ll).buffer(0)
        props = {**cprops(cid), "regions": per_country[cid], "area_km2": round(geod_area_km2(gl), 1),
                 "ar_real_src": C.get(str(cid), {}).get("ar_real"), "ar_model_src": C.get(str(cid), {}).get("ar_model")}
        cfeats.append({"type": "Feature", "properties": props, "geometry": mapping(round_geom(gl, 5))})
        if a.pixels:
            cfeats_px.append({"type": "Feature", "properties": props, "geometry": mapping(round_geom(gp, 2))})
    write(os.path.join(a.out, f"countries_{sfx}.geojson"), fc(cfeats))
    if a.pixels:
        write(os.path.join(a.out, f"regions_{sfx}_px.geojson"), fc(rfeats_px))
        write(os.path.join(a.out, f"countries_{sfx}_px.geojson"), fc(cfeats_px))
    log(f"  countries {len(cfeats)}, regions {len(rfeats)}")


if __name__ == "__main__":
    main()
