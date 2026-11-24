#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Решётка Вороного по центрам АДМИНИСТРАТИВНЫХ единиц (штаты/субъекты/департаменты/земли).
- тонкие линии  : рёбра между ячейками ОДНОЙ страны (внутренние адм. границы);
- толстые линии : рёбра между ячейками РАЗНЫХ стран (госграница «всплывает»
                  как внешний контур группы ячеек страны) + береговая линия.
Сферическая Вороного (геодезические дуги), проекция Робинсона, обрезка по суше.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import SphericalVoronoi
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path

NE = "ne"; TGT = "ESRI:54030"
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)

# ---------- данные ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson").to_crs(TGT)
adm = gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm = adm[adm.geometry.notna() & ~adm.geometry.is_empty].copy()

# сид = репрезентативная точка адм. единицы; страна = adm0_a3
rp = adm.geometry.representative_point()
lon = rp.x.to_numpy(); lat = rp.y.to_numpy()
ctry = adm["adm0_a3"].to_numpy().astype(object)
# дедуп совпадающих координат
key = np.round(np.c_[lon, lat], 4)
_, uniq = np.unique(key, axis=0, return_index=True)
uniq = np.sort(uniq)
lon, lat, ctry = lon[uniq], lat[uniq], ctry[uniq]
n = len(lon); print("админ-центров (сидов):", n, "| стран:", len(set(ctry)))

def ll_to_xyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
def xyz_to_ll(p):
    return (np.degrees(np.arctan2(p[..., 1], p[..., 0])),
            np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1))))

sv = SphericalVoronoi(ll_to_xyz(lon, lat), 1.0, np.zeros(3))
sv.sort_vertices_of_regions()

# ---------- рёбра -> какие два сида разделяют ----------
edge_seeds = {}
for s, region in enumerate(sv.regions):
    m = len(region)
    for i in range(m):
        a, b = region[i], region[(i+1) % m]
        k = (a, b) if a < b else (b, a)
        edge_seeds.setdefault(k, []).append(s)

def slerp(p0, p1, k=26):
    d = np.clip(np.dot(p0, p1), -1, 1); om = np.arccos(d)
    if om < 1e-9: return np.array([p0, p1])
    t = np.linspace(0, 1, k)[:, None]
    return np.sin((1-t)*om)/np.sin(om)*p0 + np.sin(t*om)/np.sin(om)*p1

thin, thick = [], []
for (a, b), ss in edge_seeds.items():
    same = (len(ss) >= 2) and (ctry[ss[0]] == ctry[ss[1]])
    plon, plat = xyz_to_ll(slerp(sv.vertices[a], sv.vertices[b]))
    brk = np.where(np.abs(np.diff(plon)) > 180)[0] + 1
    for piece in np.split(np.c_[plon, plat], brk):
        if len(piece) < 2: continue
        x, y = fwd.transform(piece[:, 0], piece[:, 1])
        (thin if same else thick).append(np.c_[x, y])
print("рёбер тонких:", len(thin), "толстых:", len(thick))

# ---------- суша: контур обрезки + береговая линия ----------
def geoms_to_path(geoms):
    V, C = [], []
    for g in geoms:
        if g is None or g.is_empty: continue
        for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
            poly = orient(poly, 1.0)
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords)
                if len(xy) < 3: continue
                code = np.full(len(xy), Path.LINETO); code[0] = Path.MOVETO
                code[-1] = Path.CLOSEPOLY
                V.append(xy); C.append(code)
    return Path(np.vstack(V), np.concatenate(C))
land_path = geoms_to_path(list(countries.geometry))
coast = unary_union(list(countries.geometry)).boundary       # только берег, без внутр. границ

# рамка мира
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]; oy = np.r_[ry, ly[::-1]]

# ---------- рисуем ----------
LAND = "#f5f3ec"; THIN = "#9fb1c0"; THICK = "#152230"
fig, ax = plt.subplots(figsize=(30, 16))
ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")

for L in range(-150, 151, 30):
    gx, gy = fwd.transform(np.full(200, L), np.linspace(-89, 89, 200)); ax.plot(gx, gy, color="#eef1f3", lw=0.5, zorder=0)
for B in range(-60, 61, 30):
    gx, gy = fwd.transform(np.linspace(-179, 179, 400), np.full(400, B)); ax.plot(gx, gy, color="#eef1f3", lw=0.5, zorder=0)

countries.plot(ax=ax, facecolor=LAND, edgecolor="none", zorder=1)

lc_thin = LineCollection(thin, colors=THIN, linewidths=0.28, zorder=2)
ax.add_collection(lc_thin); lc_thin.set_clip_path(land_path, ax.transData)

gpd.GeoSeries([coast], crs=TGT).plot(ax=ax, color=THICK, linewidth=0.9, zorder=3)

lc_thick = LineCollection(thick, colors=THICK, linewidths=1.0, zorder=4,
                          capstyle="round", joinstyle="round")
ax.add_collection(lc_thick); lc_thick.set_clip_path(land_path, ax.transData)

ax.plot(ox, oy, color="#c2cad1", linewidth=1.1, zorder=1)
ax.set_title("Решётка Вороного по центрам административных регионов мира\n"
             "тонкие — границы между ячейками одной страны (адм. деление) · "
             "толстые — между разными странами (госграница) и берег",
             color="#23303c", fontsize=20, pad=16)
ax.margins(0.005); plt.tight_layout()

fig.savefig("voronoi_admin1.png", dpi=250, facecolor="white", bbox_inches="tight", pad_inches=0.2)
fig.savefig("voronoi_admin1.svg", facecolor="white", bbox_inches="tight", pad_inches=0.2)
print("saved admin1 PNG + SVG")
