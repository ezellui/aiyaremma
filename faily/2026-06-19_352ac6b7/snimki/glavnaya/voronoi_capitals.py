#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Карта мира + диаграмма Вороного со столицами как центрами ячеек.
- реальные контуры суши и границы стран: тонкие линии
- границы решётки Вороного (на сфере, геодезические): толстые линии
Проекция: Робинсон (ESRI:54030).
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import SphericalVoronoi
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

NE = "ne"
TGT = "ESRI:54030"          # Robinson
to_rob = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)

# ---------- данные ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
places    = gpd.read_file(f"{NE}/ne_50m_populated_places.geojson")
caps = places[places["ADM0CAP"] == 1].copy()

lon = caps.geometry.x.to_numpy()
lat = caps.geometry.y.to_numpy()

# уберём дубли (одинаковые координаты ломают SphericalVoronoi)
key = np.round(np.c_[lon, lat], 4)
_, uniq = np.unique(key, axis=0, return_index=True)
lon, lat = lon[uniq], lat[uniq]
print(f"столиц-центров: {len(lon)}")

# ---------- столицы -> единичная сфера ----------
def ll_to_xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]

def xyz_to_ll(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    return np.degrees(np.arctan2(y, x)), np.degrees(np.arcsin(np.clip(z, -1, 1)))

pts = ll_to_xyz(lon, lat)

sv = SphericalVoronoi(pts, radius=1.0, center=np.array([0., 0., 0.]))
sv.sort_vertices_of_regions()

# ---------- собрать уникальные рёбра решётки ----------
edges = set()
for region in sv.regions:
    n = len(region)
    for i in range(n):
        a, b = region[i], region[(i + 1) % n]
        edges.add((a, b) if a < b else (b, a))
print(f"рёбер Вороного: {len(edges)}")

# ---------- геодезическое уплотнение ребра (slerp) ----------
def slerp(p0, p1, n=64):
    d = np.clip(np.dot(p0, p1), -1.0, 1.0)
    om = np.arccos(d)
    if om < 1e-9:
        return np.array([p0, p1])
    t = np.linspace(0, 1, n)[:, None]
    s0 = np.sin((1 - t) * om) / np.sin(om)
    s1 = np.sin(t * om) / np.sin(om)
    return s0 * p0 + s1 * p1

# рёбра -> сегменты в координатах Робинсона, с разрезом по 180-му меридиану
voro_segments = []
for a, b in edges:
    arc = slerp(sv.vertices[a], sv.vertices[b], n=64)
    plon, plat = xyz_to_ll(arc)
    # разрезаем там, где скачок долготы > 180 (переход через антимеридиан)
    brk = np.where(np.abs(np.diff(plon)) > 180)[0] + 1
    pieces = np.split(np.c_[plon, plat], brk)
    for piece in pieces:
        if len(piece) < 2:
            continue
        x, y = to_rob.transform(piece[:, 0], piece[:, 1])
        voro_segments.append(np.c_[x, y])

# ---------- слои реальной карты в проекции Робинсона ----------
countries_rob = countries.to_crs(TGT)

# рамка мира + графика-сетка
def graticule(step_lon=30, step_lat=30):
    segs = []
    for L in range(-180, 181, step_lon):
        la = np.linspace(-89.9, 89.9, 200)
        x, y = to_rob.transform(np.full_like(la, L), la)
        segs.append(np.c_[x, y])
    for B in range(-60, 61, step_lat):
        lo = np.linspace(-179.9, 179.9, 400)
        x, y = to_rob.transform(lo, np.full_like(lo, B))
        segs.append(np.c_[x, y])
    return segs

def world_outline():
    lo = np.linspace(-180, 180, 400)
    top = np.c_[to_rob.transform(lo, np.full_like(lo, 90))]
    bot = np.c_[to_rob.transform(lo[::-1], np.full_like(lo, -90))]
    return np.vstack([top, bot])

# ---------- рисуем ----------
fig, ax = plt.subplots(figsize=(22, 11.5))
ax.set_axis_off()
ax.set_aspect("equal")

OCEAN = "#0f1726"; LAND = "#1d2a3a"; FRAME = "#39506b"
GRAT  = "#27384d"; BORDER = "#9fb6cf"; VORO = "#ffcf4d"; CAP = "#ff5d4d"

# фон-океан = рамка мира
outline = world_outline()
ax.fill(outline[:, 0], outline[:, 1], color=OCEAN, zorder=0)

# графика-сетка
ax.add_collection(LineCollection(graticule(), colors=GRAT, linewidths=0.5, zorder=1))

# суша
countries_rob.plot(ax=ax, facecolor=LAND, edgecolor="none", zorder=2)

# реальные границы стран + контуры суша (тонко)
countries_rob.boundary.plot(ax=ax, color=BORDER, linewidth=0.45, zorder=3)

# решётка Вороного (толсто)
ax.add_collection(LineCollection(voro_segments, colors=VORO, linewidths=1.7,
                                 zorder=4, capstyle="round", joinstyle="round"))

# столицы
cx, cy = to_rob.transform(lon, lat)
ax.scatter(cx, cy, s=7, color=CAP, edgecolor="#3a0d08", linewidth=0.3, zorder=5)

# рамка мира поверх
ax.plot(outline[:, 0], outline[:, 1], color=FRAME, linewidth=1.2, zorder=6)

ax.set_title("Диаграмма Вороного со столицами мира как центрами ячеек\n"
             "толстые — границы Вороного · тонкие — реальные границы стран и контуры суши",
             color="#d8e3f0", fontsize=15, pad=14)
fig.patch.set_facecolor("#0a0f18")
ax.margins(0.01)
plt.tight_layout()

fig.savefig("voronoi_capitals.png", dpi=200, facecolor=fig.get_facecolor(),
            bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_capitals.svg", facecolor=fig.get_facecolor(),
            bbox_inches="tight", pad_inches=0.15)
print("saved PNG + SVG")
