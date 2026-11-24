#!/usr/bin/env python3
"""Attach the cities layer to the unified set: each city gets its region (key) and country (admin)
by point-in-polygon; a point that falls just across a generalised coastline or border goes to the nearest
region of the city's own country (ADM0NAME), within ~20 km (~50 km for a point with no region at all).

Usage: python3 add_cities.py <topo2geo out dir> <unified dir>
"""
import collections
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore")
from shapely.geometry import mapping, shape
from shapely.strtree import STRtree

src, d = sys.argv[1], sys.argv[2]
R = json.load(open(os.path.join(d, "unified_regions.geojson"), encoding="utf-8"))["features"]
cities = json.load(open(os.path.join(src, "cities_10m.geojson"), encoding="utf-8"))["features"]
rg = [shape(f["geometry"]) for f in R]
tree = STRtree(rg)
norm = lambda s: re.sub(r"[^a-z ]", " ", (s or "").lower()).split()
admins = sorted({f["properties"]["admin"] for f in R})
STOP = {"the", "of", "and", "republic", "islands", "island", "s", "a", "r", "sar", "holy", "see", "united", "states"}


def name_match(adm0):
    """admin whose name contains every significant word of the city's ADM0NAME (Vatican (Holy See) -> Vatican)."""
    w = set(norm(adm0)) - STOP
    cands = [a for a in admins if w and w <= set(norm(a))]
    return cands[0] if len(cands) == 1 else None


first, votes = {}, collections.defaultdict(collections.Counter)
for k, f in enumerate(cities):
    hit = [int(i) for i in tree.query(shape(f["geometry"]), predicate="within")]
    first[k] = hit
    if hit:
        votes[f["properties"]["ADM0NAME"]][R[hit[0]]["properties"]["admin"]] += 1
expect = {a: name_match(a) or (votes[a].most_common(1)[0][0] if votes[a] else None)
          for a in {f["properties"]["ADM0NAME"] for f in cities}}

out, missing, moved = [], [], []
for k, f in enumerate(cities):
    pt = shape(f["geometry"])
    hit, how = first[k], "inside"
    want = expect.get(f["properties"]["ADM0NAME"])
    if want and (not hit or R[hit[0]]["properties"]["admin"] != want):
        r = 0.2 if hit else 0.5
        near = [int(i) for i in tree.query(pt.buffer(r)) if R[int(i)]["properties"]["admin"] == want]
        if near:
            j = min(near, key=lambda i: rg[i].distance(pt))
            if hit:
                moved.append(f["properties"]["NAME"])
            hit, how = [j], ("inside" if rg[j].contains(pt) else "nearest_own_country")
    if not hit:
        j = int(tree.nearest(pt))
        if rg[j].distance(pt) <= 0.2:
            hit, how = [j], "nearest"
    p = dict(f["properties"])
    if hit:
        r_ = R[hit[0]]["properties"]
        p.update({"region_key": r_["key"], "region_name": r_["name"], "admin": r_["admin"], "match": how})
    else:
        p.update({"region_key": None, "region_name": None, "admin": None, "match": None})
        missing.append(p["NAME"])
    out.append({"type": "Feature", "properties": p, "geometry": mapping(pt)})
with open(os.path.join(d, "unified_cities.geojson"), "w", encoding="utf-8") as fh:
    json.dump({"type": "FeatureCollection", "features": out}, fh, ensure_ascii=False, separators=(",", ":"))
print(f"cities {len(out)}: {dict(collections.Counter(f['properties']['match'] for f in out))}, unassigned {missing}")
print(f"moved to their own country's region: {moved}")
