#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Альтернативная политическая карта: суша окрашена по ближайшей столице
(сферическая диаграмма Вороного), ячейки обрезаны по береговой линии.
- заливка    : ячейка Вороного (к какой столице ближе всего)
- толстые    : границы Вороного, только на суше
- тонкие     : реальные границы стран и контуры суши
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import SphericalVoronoi, cKDTree
from shapely.geometry.polygon import orient
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from matplotlib.colors import hsv_to_rgb

NE = "ne"
TGT = "ESRI:54030"                                   # Robinson
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)
inv = Transformer.from_crs(TGT, "EPSG:4326", always_xy=True)

# ---------- данные ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
places    = gpd.read_file(f"{NE}/ne_50m_populated_places.geojson")
caps = places[places["ADM0CAP"] == 1]
lon = caps.geometry.x.to_numpy(); lat = caps.geometry.y.to_numpy()
key = np.round(np.c_[lon, lat], 4)
_, uniq = np.unique(key, axis=0, return_index=True)
lon, lat = lon[uniq], lat[uniq]
ncap = len(lon)
print("столиц-центров:", ncap)

def ll_to_xyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
def xyz_to_ll(p):
    return (np.degrees(np.arctan2(p[...,1], p[...,0])),
            np.degrees(np.arcsin(np.clip(p[...,2], -1, 1))))

pts = ll_to_xyz(lon, lat)
sv = SphericalVoronoi(pts, 1.0, np.zeros(3)); sv.sort_vertices_of_regions()

# ---------- рёбра Вороного -> сегменты (lon/lat), разрез по антимеридиану ----------
edges = set()
for region in sv.regions:
    n = len(region)
    for i in range(n):
        a, b = region[i], region[(i+1) % n]
        edges.add((a, b) if a < b else (b, a))

def slerp(p0, p1, n=64):
    d = np.clip(np.dot(p0, p1), -1, 1); om = np.arccos(d)
    if om < 1e-9: return np.array([p0, p1])
    t = np.linspace(0, 1, n)[:, None]
    return np.sin((1-t)*om)/np.sin(om)*p0 + np.sin(t*om)/np.sin(om)*p1

voro_segments = []
for a, b in edges:
    plon, plat = xyz_to_ll(slerp(sv.vertices[a], sv.vertices[b], 64))
    brk = np.where(np.abs(np.diff(plon)) > 180)[0] + 1
    for piece in np.split(np.c_[plon, plat], brk):
        if len(piece) >= 2:
            x, y = fwd.transform(piece[:, 0], piece[:, 1])
            voro_segments.append(np.c_[x, y])

# ---------- проекция суши + путь обрезки ----------
countries_rob = countries.to_crs(TGT)

def geoms_to_path(geoms):
    V, C = [], []
    for g in geoms:
        if g is None or g.is_empty: continue
        polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
        for poly in polys:
            poly = orient(poly, 1.0)                  # внешний CCW, дырки CW
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords)
                if len(xy) < 3: continue
                code = np.full(len(xy), Path.LINETO); code[0] = Path.MOVETO
                code[-1] = Path.CLOSEPOLY
                V.append(xy); C.append(code)
    return Path(np.vstack(V), np.concatenate(C))

land_path = geoms_to_path(list(countries_rob.geometry))

# ---------- растровая раскраска «ближайшая столица» в проекции Робинсона ----------
# контур мира («яйцо» Робинсона) = меридианы ±180 по широте; экстремум X на экваторе
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]
oy = np.r_[ry, ly[::-1]]
xmin, xmax = lx.min(), rx.max()
ymin, ymax = oy.min(), oy.max()

W = 2800
H = int(round(W * (ymax - ymin) / (xmax - xmin)))
xs = np.linspace(xmin, xmax, W); ys = np.linspace(ymin, ymax, H)
XX, YY = np.meshgrid(xs, ys)
glon, glat = inv.transform(XX.ravel(), YY.ravel())
valid = np.isfinite(glon) & np.isfinite(glat) & (np.abs(glon) <= 180) & (np.abs(glat) <= 90)

tree = cKDTree(pts)
labels = np.full(glon.size, -1, np.int32)
pix_xyz = ll_to_xyz(glon[valid], glat[valid])
labels[valid] = tree.query(pix_xyz)[1]

# палитра: золотое сечение по тону -> различимые пастельные цвета
hue = (np.arange(ncap) * 0.6180339887) % 1.0
sat = 0.42 + 0.18 * ((np.arange(ncap) * 0.123) % 1.0)
val = 0.80 + 0.15 * ((np.arange(ncap) * 0.317) % 1.0)
pal = hsv_to_rgb(np.c_[hue, sat, val])

img = np.zeros((glon.size, 4), np.float32)
m = labels >= 0
img[m, :3] = pal[labels[m]]; img[m, 3] = 1.0
img = img.reshape(H, W, 4)

# ---------- рисуем ----------
OCEAN = "#e9eef2"; BORDER = "#5a6b7a"; VORO = "#11202e"; CAP = "#7a1414"
fig, ax = plt.subplots(figsize=(22, 11.6))
ax.set_axis_off(); ax.set_aspect("equal")
fig.patch.set_facecolor("#f4f1ea")

# океан = рамка мира
ax.fill(ox, oy, color=OCEAN, zorder=0)

# заливка ячеек -> обрезка по суше
im = ax.imshow(img, extent=[xmin, xmax, ymin, ymax], origin="lower",
               interpolation="nearest", zorder=2)
im.set_clip_path(land_path, ax.transData)

# реальные границы стран и контуры суши (тонко)
countries_rob.boundary.plot(ax=ax, color=BORDER, linewidth=0.4, zorder=3)

# границы Вороного (толсто), только на суше
lc = LineCollection(voro_segments, colors=VORO, linewidths=1.7, zorder=4,
                    capstyle="round", joinstyle="round")
ax.add_collection(lc); lc.set_clip_path(land_path, ax.transData)

# столицы
cx, cy = fwd.transform(lon, lat)
ax.scatter(cx, cy, s=6, color=CAP, edgecolor="white", linewidth=0.3, zorder=5)

# рамка мира
ax.plot(ox, oy, color="#9aa7b2", linewidth=1.1, zorder=6)

ax.set_title("«Если бы границы шли по ближайшей столице»\n"
             "заливка и толстые линии — ячейки Вороного (обрезаны по суше) · "
             "тонкие — реальные границы стран",
             color="#23303c", fontsize=15, pad=14)
ax.margins(0.01); plt.tight_layout()

fig.savefig("voronoi_capitals_land.png", dpi=200, facecolor=fig.get_facecolor(),
            bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_capitals_land.svg", facecolor=fig.get_facecolor(),
            bbox_inches="tight", pad_inches=0.15)
print("saved land-clipped PNG + SVG", img.shape)
