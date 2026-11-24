#!/usr/bin/env python3
"""Prepare the data cache for the future-borders renderer.

Inputs : maps_extract/unified/unified-10m.topo.json  (countries, regions, cities on shared arcs)
         html-generated/webmap/assets/countries.json (Russian country names by ISO alpha-3)
Output : cache/regions.json  — per region: key, admin, name, pop, label point
         cache/countries.json — admin -> Russian name, ISO codes
         cache/arcs.npz      — arc polylines (lon/lat) and the two regions on their sides
         cache/index.npy     — equirectangular raster W x H of region indices (-1 = sea)
         cache/cities.json
"""
import json
import os
import sys
import warnings

import numpy as np
import pycountry
import shapely
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import shape

warnings.filterwarnings("ignore")
TEX_W, TEX_H = 8192, 4096

HERE = os.path.dirname(os.path.abspath(__file__))
TOPO = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/maps_extract/unified/unified-10m.topo.json"
RU = sys.argv[2] if len(sys.argv) > 2 else "/root/html-generated/webmap/assets/countries.json"
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# Russian names for units the ISO lookup does not resolve (or resolves awkwardly)
RU_FIX = {
    "Gaza Strip": "Сектор Газа", "West Bank": "Западный берег", "Kosovo": "Косово",
    "Northern Cyprus": "Северный Кипр", "Somaliland": "Сомалиленд", "Western Sahara": "Западная Сахара",
    "Caribbean Netherlands": "Карибские Нидерланды", "Coral Sea Islands": "Острова Кораллового моря",
    "Akrotiri Sovereign Base Area": "Акротири", "Dhekelia Sovereign Base Area": "Декелия",
    "Baykonur Cosmodrome": "Байконур", "US Naval Base Guantanamo Bay": "Гуантанамо",
    "Spratly Is.": "Острова Спратли", "Ashmore and Cartier Islands": "Острова Ашмор и Картье",
    "Clipperton Island": "Клиппертон", "Indian Ocean Territories": "Территории в Индийском океане",
    "Siachen Glacier": "Ледник Сиачен", "Antarctica": "Антарктида", "Republic of Serbia": "Сербия",
    "Vatican": "Ватикан", "Aland": "Аланды", "Brazil": "Бразилия",
}


def decode(topo):
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        a = np.cumsum(np.array(arc, dtype=np.int64), axis=0)
        arcs.append(np.c_[a[:, 0] * sx + tx, a[:, 1] * sy + ty])
    return arcs


def ring(arcs, idxs):
    pts = []
    for i in idxs:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.append(a if not pts else a[1:])
    return np.vstack(pts)


def geom(arcs, g):
    t = g["type"]
    if t == "Polygon":
        return {"type": t, "coordinates": [ring(arcs, r).tolist() for r in g["arcs"]]}
    if t == "MultiPolygon":
        return {"type": t, "coordinates": [[ring(arcs, r).tolist() for r in p] for p in g["arcs"]]}
    raise ValueError(t)


def arc_ids(g):
    out = []
    def walk(x):
        if isinstance(x, list):
            for y in x:
                walk(y)
        else:
            out.append(x)
    walk(g["arcs"])
    return out


def main():
    topo = json.load(open(TOPO, encoding="utf-8"))
    arcs = decode(topo)
    R = topo["objects"]["regions"]["geometries"]
    C = topo["objects"]["countries"]["geometries"]

    # --- Russian country names
    ru_by_a3 = {v["a3"]: v["ru"] for v in json.load(open(RU, encoding="utf-8")).values()}
    countries = {}
    for g in C:
        p = g["properties"]
        a3 = None
        if p.get("iso_n3"):
            c = pycountry.countries.get(numeric=str(p["iso_n3"]).zfill(3))
            a3 = c.alpha_3 if c else None
        ru = RU_FIX.get(p["admin"]) or ru_by_a3.get(a3) or p.get("name_short") or p["admin"]
        countries[p["admin"]] = {"ru": ru, "a3": a3, "iso_n3": p.get("iso_n3"), "pop": p.get("pop")}

    # --- regions, label points, arcs sides
    regions = []
    side = [[] for _ in arcs]
    geoms = []
    for k, g in enumerate(R):
        p = g["properties"]
        gg = shape(geom(arcs, g))
        geoms.append(gg)
        big = max(getattr(gg, "geoms", [gg]), key=lambda q: q.area)
        lp = shapely.ops.polylabel(big, 0.05) if big.area > 0.05 else big.representative_point()
        regions.append({"key": p["key"], "admin": p["admin"], "name": p.get("name"), "iso": p.get("iso_3166_2"),
                        "pop": p.get("pop") or 0, "label": [round(lp.x, 4), round(lp.y, 4)], "area_km2": p.get("area_km2")})
        for a in set(i if i >= 0 else ~i for i in arc_ids(g)):
            side[a].append(k)
    left = np.array([s[0] if len(s) > 0 else -1 for s in side], dtype=np.int32)
    right = np.array([s[1] if len(s) > 1 else -1 for s in side], dtype=np.int32)
    bad = sum(1 for s in side if len(s) > 2)
    print(f"regions {len(regions)}, arcs {len(arcs)}, coast arcs {(right < 0).sum()}, arcs with >2 sides {bad}")

    # --- index raster (equirectangular, lon -180..180, lat 90..-90)
    tr = from_bounds(-180, -90, 180, 90, TEX_W, TEX_H)
    order = sorted(range(len(geoms)), key=lambda i: -geoms[i].area)  # small units drawn last
    idx = rasterize(((geoms[i], i) for i in order), out_shape=(TEX_H, TEX_W), transform=tr,
                    fill=-1, dtype="int32", all_touched=False)
    # units too small to own a pixel: stamp their label pixel so they still exist in the texture
    seen = set(np.unique(idx).tolist())
    stamped = 0
    for i, r in enumerate(regions):
        if i not in seen:
            x = int((r["label"][0] + 180) / 360 * TEX_W) % TEX_W
            y = min(TEX_H - 1, int((90 - r["label"][1]) / 180 * TEX_H))
            idx[y, x] = i
            stamped += 1
    print(f"index raster {TEX_W}x{TEX_H}: land px {(idx >= 0).sum()}, sub-pixel units stamped {stamped}")
    np.save(os.path.join(CACHE, "index.npy"), idx.astype(np.int16))

    lens = np.array([len(a) for a in arcs])
    np.savez_compressed(os.path.join(CACHE, "arcs.npz"), xy=np.vstack(arcs).astype(np.float32),
                        lens=lens, left=left, right=right)
    cities = [{"name": g["properties"]["NAME"], "adm0": g["properties"]["ADM0NAME"],
               "admin": g["properties"].get("admin"), "pop": g["properties"]["POP_MAX"],
               "rank": g["properties"]["SCALERANK"],
               "lon": g["coordinates"][0] * topo["transform"]["scale"][0] + topo["transform"]["translate"][0],
               "lat": g["coordinates"][1] * topo["transform"]["scale"][1] + topo["transform"]["translate"][1]}
              for g in topo["objects"]["cities"]["geometries"]]
    for name, obj in [("regions", regions), ("countries", countries), ("cities", cities)]:
        json.dump(obj, open(os.path.join(CACHE, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("countries without a Russian name:", [a for a, v in countries.items() if v["ru"] == a][:40])


if __name__ == "__main__":
    main()
