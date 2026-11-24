#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Карта отклонения реальной госграницы от реконструкции Вороного (по адм-центрам).
Для каждой точки реальной СУХОПУТНОЙ границы меряем расстояние (большой круг, км)
до ближайшего «межстранового» ребра Вороного. Раскрашиваем границу по отклонению.
Гипотеза: пики совпадут с «начерченными по линейке» и спорными участками.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import SphericalVoronoi, cKDTree
from shapely.ops import unary_union, nearest_points
from shapely.geometry import Point
from pyproj import Transformer
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.collections import LineCollection

NE = "ne"; TGT = "ESRI:54030"; Re = 6371.0
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)

def llxyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
def xyzll(p):
    return (np.degrees(np.arctan2(p[..., 1], p[..., 0])),
            np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1))))
def gc_km(chord):                       # хорда единичной сферы -> км по дуге
    return Re * 2 * np.arcsin(np.clip(chord/2, 0, 1))

# ---------- админ-центры -> сферическая Вороного -> «межстрановые» рёбра ----------
adm = gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm = adm[adm.geometry.notna() & ~adm.geometry.is_empty]
rp = adm.geometry.representative_point()
lon = rp.x.to_numpy(); lat = rp.y.to_numpy(); ctry = adm["adm0_a3"].to_numpy().astype(object)
_, u = np.unique(np.round(np.c_[lon, lat], 4), axis=0, return_index=True); u = np.sort(u)
lon, lat, ctry = lon[u], lat[u], ctry[u]
print("сидов:", len(lon))
sv = SphericalVoronoi(llxyz(lon, lat), 1.0, np.zeros(3)); sv.sort_vertices_of_regions()
edge_seeds = {}
for s, reg in enumerate(sv.regions):
    m = len(reg)
    for i in range(m):
        a, b = reg[i], reg[(i+1) % m]; k = (a, b) if a < b else (b, a)
        edge_seeds.setdefault(k, []).append(s)
def slerp(p0, p1, k=24):
    d = np.clip(np.dot(p0, p1), -1, 1); om = np.arccos(d)
    if om < 1e-9: return np.array([p0, p1])
    t = np.linspace(0, 1, k)[:, None]
    return np.sin((1-t)*om)/np.sin(om)*p0 + np.sin(t*om)/np.sin(om)*p1
VL, VB = [], []
for (a, b), ss in edge_seeds.items():
    if len(ss) >= 2 and ctry[ss[0]] != ctry[ss[1]]:
        pl, pb = xyzll(slerp(sv.vertices[a], sv.vertices[b]))
        VL.append(pl); VB.append(pb)
vlon = np.concatenate(VL); vlat = np.concatenate(VB)
vtree = cKDTree(llxyz(vlon, vlat))
print("точек на рёбрах Вороного-границ:", vlon.size)

# ---------- реальные сухопутные госграницы (география) ----------
cg = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
bounds = unary_union(list(cg.geometry.boundary))
land = unary_union(list(cg.geometry))
coast = land.boundary
real = bounds.difference(coast.buffer(0.02))           # убрать берег -> только межгос. суша
print("готовы реальные сухопутные границы")

def flat(geom):
    t = geom.geom_type
    if t == "LineString": return [geom]
    if t in ("MultiLineString", "GeometryCollection"):
        out = []
        for g in geom.geoms: out += flat(g)
        return out
    return []

# ---------- семплируем границы и считаем отклонение ----------
seg_xy, seg_val, all_dev = [], [], []
for ls in flat(real):
    L = ls.length                                       # в градусах (план lon/lat)
    npts = max(2, int(L / 0.1))                         # шаг ~0.1°
    tt = np.linspace(0, 1, npts)
    P = [ls.interpolate(t, normalized=True) for t in tt]
    lo = np.array([p.x for p in P]); la = np.array([p.y for p in P])
    dch, _ = vtree.query(llxyz(lo, la))
    dev = gc_km(dch); all_dev.append(dev)
    X, Y = fwd.transform(lo, la)
    for i in range(len(lo)-1):
        if abs(lo[i+1]-lo[i]) > 180: continue          # антимеридиан
        seg_xy.append([[X[i], Y[i]], [X[i+1], Y[i+1]]])
        seg_val.append(0.5*(dev[i]+dev[i+1]))
all_dev = np.concatenate(all_dev); seg_val = np.array(seg_val)
for q in (50, 75, 90, 95, 99):
    print(f"  p{q}: {np.percentile(all_dev, q):6.0f} км")
print(f"  max: {all_dev.max():.0f} км  | медиана: {np.median(all_dev):.0f} км")

# ---------- канонические проверки (точку снапим на реальную границу) ----------
checks = {
    "Египет–Ливия (25°E, прямая)": (25.0, 27.0),
    "Египет–Судан (22°N, прямая)": (30.0, 22.0),
    "Ливия–Чад (прямая)":          (18.0, 22.5),
    "Алжир–Ливия (прямая)":        (11.5, 26.0),
    "США–Канада (49-я параллель)": (-104.0, 49.0),
    "Намибия–Ботсвана/Каприви":    (22.0, -18.1),
    "— органические —":            None,
    "Франция–Бельгия":             (4.1, 50.3),
    "Чехия–Австрия":               (15.3, 48.8),
    "Германия–Польша (Одер)":      (14.6, 52.6),
    "Швейцария–Италия (Альпы)":    (8.0, 46.0),
    "Нидерланды–Бельгия":          (4.5, 51.4),
}
print("\nканонические участки (снап на границу), отклонение:")
for nm, c in checks.items():
    if c is None: print(f"  {nm}"); continue
    pt = Point(c)
    np_on, _ = nearest_points(real, pt)
    dch, _ = vtree.query(llxyz(np.array([np_on.x]), np.array([np_on.y])))
    print(f"  {nm:30s} {gc_km(dch[0]):5.0f} км   (снап {np_on.x:.1f},{np_on.y:.1f})")

# ---------- рисуем ----------
countries_rob = cg.to_crs(TGT)
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]; oy = np.r_[ry, ly[::-1]]

CAP = 250.0
cmap = plt.cm.turbo; norm = mpl.colors.Normalize(0, CAP)
fig, ax = plt.subplots(figsize=(26, 13.8))
ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")
countries_rob.plot(ax=ax, facecolor="#f4f2ec", edgecolor="none", zorder=1)
gpd.GeoSeries([coast], crs="EPSG:4326").to_crs(TGT).plot(ax=ax, color="#cdd4da", linewidth=0.5, zorder=2)
# админ-центры (для оценки плотности данных)
ax_cx, ax_cy = fwd.transform(lon, lat)
ax.scatter(ax_cx, ax_cy, s=1.2, color="#9aa6b0", alpha=0.5, zorder=2, linewidths=0)

lc = LineCollection(seg_xy, array=seg_val, cmap=cmap, norm=norm,
                    linewidths=1.8, zorder=4, capstyle="round")
ax.add_collection(lc)
ax.plot(ox, oy, color="#c2cad1", linewidth=1.1, zorder=1)

cb = fig.colorbar(lc, ax=ax, fraction=0.022, pad=0.01, extend="max")
cb.set_label("отклонение реальной границы от линии Вороного, км", fontsize=11)
ax.set_title("Насколько госграницы отклоняются от реконструкции по админ-центрам\n"
             "холодные тона — граница «выросла» из расселения · тёплые — проведена поверх (линейка/река/спор)",
             color="#23303c", fontsize=17, pad=14)
ax.margins(0.005); plt.tight_layout()
fig.savefig("voronoi_deviation.png", dpi=220, facecolor="white", bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_deviation.svg", facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("saved deviation PNG + SVG")
