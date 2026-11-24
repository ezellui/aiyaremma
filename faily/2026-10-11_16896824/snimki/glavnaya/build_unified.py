#!/usr/bin/env python3
"""Build a consistent country/region set from maps/data/world-10m.json:
regions become a clean partition (no overlaps, no slivers between neighbours),
countries are exactly the union of their regions.

Input : out/regions_10m.geojson, out/countries_10m.geojson (from topo2geo.py),
        out/countries_50m.geojson (only for the Vatican, empty in 10m)
Output: <out>/unified_regions.geojson, <out>/unified_countries.geojson

Usage: python3 build_unified.py <topo2geo out dir> <result dir>
"""
import collections
import json
import os
import sys
import warnings

import shapely
from pyproj import Geod
from shapely.geometry import Polygon, mapping, shape
from shapely.strtree import STRtree

warnings.filterwarnings("ignore")
GRID = 1e-6          # deg; all overlay ops snap to this grid
GAP_MAX_KM2 = 5000   # interior holes smaller than this are slivers (the Caspian is ~397 000 km²)
GEOD = Geod(ellps="WGS84")


def km2(g):
    return abs(GEOD.geometry_area_perimeter(g)[0]) / 1e6


def polys(g):
    if g is None or g.is_empty:
        return shapely.Polygon()
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return shapely.union_all([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def shared_len(piece, g):
    return piece.boundary.intersection(g.buffer(1e-6)).length


def load(path):
    return json.load(open(path, encoding="utf-8"))["features"]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    log = lambda s: print(s, file=sys.stderr)

    R = load(os.path.join(src, "regions_10m.geojson"))
    C = load(os.path.join(src, "countries_10m.geojson"))
    C50 = load(os.path.join(src, "countries_50m.geojson"))
    props = [dict(f["properties"]) for f in R]
    geo = [polys(shapely.set_precision(shape(f["geometry"]), GRID)) if f["geometry"] else None for f in R]
    admin = [p["admin"] for p in props]

    # --- Vatican: empty in the 10m data; take the 50m country and carve it out of its neighbour
    vat = next((shape(f["geometry"]) for f in C50 if f["properties"]["name"] == "Vatican" and f["geometry"]), None)
    for i, p in enumerate(props):
        if geo[i] is None and p["admin"] == "Vatican" and vat is not None:
            geo[i] = polys(shapely.set_precision(vat, GRID))
            for j, g in enumerate(geo):
                if j != i and g is not None and g.intersects(geo[i]):
                    geo[j] = polys(g.difference(geo[i], grid_size=GRID))
            log(f"  Vatican taken from countries_50m ({km2(geo[i]):.2f} km²)")

    # --- admin -> country of the 10m countries layer (names differ: ADMIN vs NAME), by overlap
    cg = [(f["properties"]["name"], f.get("id"), shape(f["geometry"])) for f in C if f["geometry"]]
    ctree = STRtree([g for _, _, g in cg])
    by_admin = collections.defaultdict(list)
    for i, g in enumerate(geo):
        if g is not None:
            by_admin[admin[i]].append(g)
    match = {}
    for a, gs in by_admin.items():
        u = shapely.union_all(gs)
        best = None
        for j in ctree.query(u):
            x = u.intersection(cg[j][2]).area
            if best is None or x > best[0]:
                best = (x, j)
        if best and best[0] > 0.5 * u.area:
            match[a] = cg[best[1]]
    country_of_admin = {a: m[2] for a, m in match.items()}

    # --- 1. overlaps: each overlapping piece goes to exactly one region
    idx = [i for i, g in enumerate(geo) if g is not None]
    tree = STRtree([geo[i] for i in idx])
    pairs = set()
    for k, i in enumerate(idx):
        for m in tree.query(geo[i]):
            j = idx[int(m)]
            if j > i:
                pairs.add((i, j))
    n_ov = 0
    ov_km2 = 0.0
    for i, j in sorted(pairs):
        if not geo[i].intersects(geo[j]):
            continue
        piece = polys(geo[i].intersection(geo[j], grid_size=GRID))
        if piece.is_empty or piece.area < 1e-12:
            continue
        for part in getattr(piece, "geoms", [piece]):
            if part.area < 1e-14:
                continue
            win = None
            if admin[i] != admin[j]:
                # border between countries: the detailed 10m country layer decides
                pt = part.representative_point()
                ci, cj = country_of_admin.get(admin[i]), country_of_admin.get(admin[j])
                if ci is not None and ci.contains(pt) and not (cj is not None and cj.contains(pt)):
                    win = i
                elif cj is not None and cj.contains(pt) and not (ci is not None and ci.contains(pt)):
                    win = j
            if win is None:
                # within a country: the region that wraps more of the piece keeps it
                li = shared_len(part, geo[i].difference(part, grid_size=GRID))
                lj = shared_len(part, geo[j].difference(part, grid_size=GRID))
                win = i if li >= lj else j
            lose = j if win == i else i
            geo[lose] = polys(geo[lose].difference(part, grid_size=GRID))
            n_ov += 1
            ov_km2 += km2(part)
    log(f"  overlaps resolved: {n_ov} pieces, {ov_km2:.0f} km²")

    # --- 2. slivers between regions: interior holes of the whole coverage (not the Caspian)
    idx = [i for i, g in enumerate(geo) if g is not None and not g.is_empty]
    whole = shapely.union_all([geo[i] for i in idx], grid_size=GRID)
    holes = [Polygon(r) for p in getattr(whole, "geoms", [whole]) for r in p.interiors]
    tree = STRtree([geo[i] for i in idx])
    n_gap = 0
    gap_km2 = 0.0
    kept = []
    for h in holes:
        a = km2(h)
        if a > GAP_MAX_KM2:
            kept.append(a)
            continue
        best = None
        for m in tree.query(h.buffer(1e-6)):
            i = idx[int(m)]
            L = shared_len(h, geo[i])
            if L > 0 and (best is None or L > best[0]):
                best = (L, i)
        if best:
            geo[best[1]] = polys(shapely.union_all([geo[best[1]], h], grid_size=GRID))
            n_gap += 1
            gap_km2 += a
    log(f"  gaps filled: {n_gap} ({gap_km2:.0f} km²); real holes kept: {[round(x) for x in kept]}")

    # --- 3. output regions
    rfeats = []
    for i, g in enumerate(geo):
        if g is None or g.is_empty:
            continue
        g = shapely.orient_polygons(shapely.make_valid(g), exterior_cw=False)
        p = props[i]
        m = match.get(p["admin"])
        p.update({"region_id": i, "country_name_short": m[0] if m else None,
                  "iso_n3": m[1] if m else None, "area_km2": round(km2(g), 1)})
        rfeats.append({"type": "Feature", "properties": p, "geometry": mapping(g)})

    # --- 4. countries = exact union of their regions
    groups = collections.defaultdict(list)
    for f, i in zip(rfeats, [f["properties"]["region_id"] for f in rfeats]):
        groups[f["properties"]["admin"]].append(i)
    cfeats = []
    for a in sorted(groups):
        ids = groups[a]
        u = shapely.union_all([geo[i] for i in ids], grid_size=GRID)
        u = shapely.orient_polygons(polys(shapely.make_valid(u)), exterior_cw=False)
        m = match.get(a)
        pop = [props[i].get("pop") for i in ids]
        cfeats.append({"type": "Feature", "properties": {
            "admin": a, "name_short": m[0] if m else None, "iso_n3": m[1] if m else None,
            "regions": len(ids), "pop": sum(x for x in pop if x) if any(pop) else None,
            "area_km2": round(km2(u), 1)}, "geometry": mapping(u)})
    for name, feats in [("unified_regions", rfeats), ("unified_countries", cfeats)]:
        with open(os.path.join(dst, name + ".geojson"), "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": feats}, f, ensure_ascii=False, separators=(",", ":"))
    unused = sorted({n for n, _, _ in cg} - {m[0] for m in match.values()})
    log(f"  regions {len(rfeats)}, countries {len(cfeats)}; 10m countries with no regions: {unused}")


if __name__ == "__main__":
    main()
