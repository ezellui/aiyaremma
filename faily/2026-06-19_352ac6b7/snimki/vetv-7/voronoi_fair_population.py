#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«Справедливые» границы: каждая столица получает РАВНУЮ долю населения,
а не ближайшую землю. Capacity-constrained Voronoi (диаграмма мощности /
полудискретный оптимальный транспорт): веса столиц подбираются двойственным
восхождением так, чтобы у каждой ячейки была равная людская масса.
Население — города Natural Earth (POP_MAX). Метрика — плоскость Робинсона.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from shapely.geometry.polygon import orient
from rasterio import features
from rasterio.transform import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.colors import hsv_to_rgb

NE = "ne"; TGT = "ESRI:54030"
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)

# ---------- столицы (сиды) и города (атомы населения) ----------
pl = gpd.read_file(f"{NE}/ne_50m_populated_places.geojson")
caps = pl[pl["ADM0CAP"] == 1]
clon = caps.geometry.x.to_numpy(); clat = caps.geometry.y.to_numpy()
_, u = np.unique(np.round(np.c_[clon, clat], 4), axis=0, return_index=True); u = np.sort(u)
clon, clat = clon[u], clat[u]; N = len(clon)
cap_x, cap_y = fwd.transform(clon, clat); capxy = np.c_[cap_x, cap_y]

city = gpd.read_file(f"{NE}/ne_10m_populated_places.geojson")
mlon = city.geometry.x.to_numpy(); mlat = city.geometry.y.to_numpy()
pop = np.clip(city["POP_MAX"].fillna(0).to_numpy().astype(float), 1.0, None)
mx, my = fwd.transform(mlon, mlat); cityxy = np.c_[mx, my]
M = len(pop); target = pop.sum() / N
print(f"столиц {N} | городов {M} | равная доля ≈ {target/1e6:.1f} млн (городского)")

ctree = cKDTree(capxy)
# полная матрица квадратов расстояний город×столица (M×N мало)
D2 = ((cityxy**2).sum(1)[:, None] + (capxy**2).sum(1)[None, :] - 2*cityxy@capxy.T)
Sref = np.median(D2.min(axis=1))                         # масштаб шага весов

def spread(mass):
    return (f"{mass.min()/1e6:4.1f}..{mass.max()/1e6:5.1f} млн "
            f"(p10 {np.percentile(mass,10)/1e6:.1f}, p50 {np.percentile(mass,50)/1e6:.1f}, "
            f"p90 {np.percentile(mass,90)/1e6:.1f})")

# обычный Вороной (w=0) для сравнения
m0 = np.bincount(np.argmin(D2, axis=1), weights=pop, minlength=N)
print("обычный Вороной:        ", spread(m0))

# ---------- двойственное восхождение (балансировка масс) ----------
w = np.zeros(N); eta = 1.0
for it in range(2000):
    win = np.argmin(D2 - w, axis=1)
    mass = np.bincount(win, weights=pop, minlength=N)
    w += eta * Sref * (target - mass) / target
    w -= w.mean(); eta *= 0.9985
    if it % 250 == 0 or it == 1999:
        print(f"  it{it:4d}  {spread(mass)}")
print("после балансировки:     ", spread(mass))

# ---------- сетка, маска суши, назначение пикселей по диаграмме мощности ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson").to_crs(TGT)
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]; oy = np.r_[ry, ly[::-1]]
xmin, xmax = lx.min(), rx.max(); ymin, ymax = oy.min(), oy.max()
Wd = 2400; Hd = int(round(Wd*(ymax-ymin)/(xmax-xmin)))
xs = np.linspace(xmin, xmax, Wd); ys = np.linspace(ymin, ymax, Hd)
XX, YY = np.meshgrid(xs, ys)
_xf = from_bounds(xmin, ymin, xmax, ymax, Wd, Hd)
land = features.rasterize([(g, 1) for g in countries.geometry if g and not g.is_empty],
                          out_shape=(Hd, Wd), transform=_xf, fill=0).astype(bool)[::-1]

pj = np.c_[XX[land], YY[land]]
cap2 = (capxy**2).sum(1)
plabel = np.empty(pj.shape[0], np.int32)
for a in range(0, pj.shape[0], 200000):                  # чанками: argmin по всем столицам
    b = pj[a:a+200000]
    d2b = (b**2).sum(1)[:, None] + cap2[None, :] - 2*b@capxy.T
    plabel[a:a+200000] = np.argmin(d2b - w, axis=1)
labels = np.zeros((Hd, Wd), np.int32); labels[land] = plabel + 1

def geoms_to_path(geoms):
    V, C = [], []
    for g in geoms:
        if g is None or g.is_empty: continue
        for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
            poly = orient(poly, 1.0)
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords)
                if len(xy) < 3: continue
                cc = np.full(len(xy), Path.LINETO); cc[0] = Path.MOVETO; cc[-1] = Path.CLOSEPOLY
                V.append(xy); C.append(cc)
    return Path(np.vstack(V), np.concatenate(C))
land_path = geoms_to_path(list(countries.geometry))

# границы ячеек (тонко) + заливка
def bound(lab):
    b = np.zeros(lab.shape, bool)
    b[:, :-1] |= (lab[:, :-1] != lab[:, 1:]) & (lab[:, :-1] > 0) & (lab[:, 1:] > 0)
    b[:-1, :] |= (lab[:-1, :] != lab[1:, :]) & (lab[:-1, :] > 0) & (lab[1:, :] > 0)
    return ndi.binary_dilation(b, np.ones((2, 2), bool))
bnd = bound(labels)

hue = (np.arange(N)*0.61803398875) % 1.0
sat = 0.40 + 0.2*((np.arange(N)*0.13) % 1.0); val = 0.82 + 0.13*((np.arange(N)*0.31) % 1.0)
pal = hsv_to_rgb(np.c_[hue, sat, val])
rgba = np.zeros((Hd, Wd, 4), np.float32)
occ = labels > 0
rgba[occ, :3] = pal[labels[occ]-1]; rgba[occ, 3] = 1.0
rgba[bnd, :3] = [0.10, 0.13, 0.18]; rgba[bnd, 3] = 1.0

# ---------- рисуем ----------
fig, ax = plt.subplots(figsize=(24, 12.6)); ax.set_axis_off(); ax.set_aspect("equal")
fig.patch.set_facecolor("white")
ax.fill(ox, oy, color="#eef1f4", zorder=0)
im = ax.imshow(rgba, extent=[xmin, xmax, ymin, ymax], origin="lower", interpolation="nearest", zorder=2)
im.set_clip_path(land_path, ax.transData)
ax.scatter(cap_x, cap_y, s=7, color="#5a1010", edgecolor="white", linewidth=0.3, zorder=5)
ax.plot(ox, oy, color="#c2cad1", linewidth=1.1, zorder=1)
ax.set_title("«Справедливые» границы: каждая столица — равная доля населения\n"
             "ячейки равны по числу людей (не по площади): плотное дробится, пустое раздувается",
             color="#23303c", fontsize=18, pad=14)
ax.margins(0.005); plt.tight_layout()
fig.savefig("voronoi_fair_population.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_fair_population.svg", facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("saved fair-population PNG + SVG")
