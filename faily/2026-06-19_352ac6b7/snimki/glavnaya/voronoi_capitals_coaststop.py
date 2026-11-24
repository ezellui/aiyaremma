#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Рост областей от столиц ОСТАНАВЛИВАЕТСЯ У ВОДЫ.
Геодезическое разрастание по суше (watershed по маске суши):
- столица занимает только связную сушу, до которой можно дойти, не пересекая воду;
- граница между областями — там, где встречаются фронты роста;
- суша, недостижимая ни от одной столицы (Антарктида, Гренландия, Тасмания,
  Хоккайдо, Сицилия, ...), остаётся незанятой -> белая.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry.polygon import orient
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.colors import hsv_to_rgb

NE = "ne"; TGT = "ESRI:54030"
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)
inv = Transformer.from_crs(TGT, "EPSG:4326", always_xy=True)

# ---------- данные ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
places    = gpd.read_file(f"{NE}/ne_50m_populated_places.geojson")
caps = places[places["ADM0CAP"] == 1]
lon = caps.geometry.x.to_numpy(); lat = caps.geometry.y.to_numpy()
_, uniq = np.unique(np.round(np.c_[lon, lat], 4), axis=0, return_index=True)
lon, lat = lon[uniq], lat[uniq]
ncap = len(lon); print("столиц-центров:", ncap)

countries_rob = countries.to_crs(TGT)

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

land_path = geoms_to_path(list(countries_rob.geometry))

# ---------- растровая сетка в проекции Робинсона ----------
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]; oy = np.r_[ry, ly[::-1]]
xmin, xmax = lx.min(), rx.max(); ymin, ymax = oy.min(), oy.max()

W = 3000
H = int(round(W * (ymax - ymin) / (xmax - xmin)))
xs = np.linspace(xmin, xmax, W); ys = np.linspace(ymin, ymax, H)
XX, YY = np.meshgrid(xs, ys)

# маска суши: быстрая растеризация полигонов (rasterio)
from rasterio import features
from rasterio.transform import from_bounds
_xform = from_bounds(xmin, ymin, xmax, ymax, W, H)        # строка 0 = верх (ymax)
_shapes = [(geom, 1) for geom in countries_rob.geometry if geom and not geom.is_empty]
land_mask = features.rasterize(_shapes, out_shape=(H, W), transform=_xform,
                               fill=0, all_touched=False).astype(bool)
land_mask = land_mask[::-1]                                # к сетке с осью y вверх
print("пикселей суши:", int(land_mask.sum()))

def xy_to_idx(x, y):
    ix = np.clip(np.round((x - xmin) / (xmax - xmin) * (W - 1)).astype(int), 0, W-1)
    iy = np.clip(np.round((y - ymin) / (ymax - ymin) * (H - 1)).astype(int), 0, H-1)
    return ix, iy

# ---------- сиды: по пикселю на столицу (привязка к ближайшей суше, без коллизий) ----------
cx, cy = fwd.transform(lon, lat)
cix, ciy = xy_to_idx(cx, cy)

# индексация пикселей суши -> узлы графа
nid = -np.ones((H, W), np.int64)
land_rc = np.argwhere(land_mask)                          # (iy, ix)
K = land_rc.shape[0]
nid[land_mask] = np.arange(K)
land_tree = cKDTree(land_rc)

taken = set()
seed_nodes, seed_labels = [], []
for i in range(ncap):
    iy, ix = ciy[i], cix[i]
    if not land_mask[iy, ix]:                             # прибрежная столица «в воде» из-за растра
        _, j = land_tree.query([iy, ix]); iy, ix = land_rc[j]
    if (iy, ix) in taken:                                 # коллизия микрогосударств -> ближайший свободный
        found = False
        for r in range(1, 16):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    ny, nx = iy + dy, ix + dx
                    if 0 <= ny < H and 0 <= nx < W and land_mask[ny, nx] and (ny, nx) not in taken:
                        iy, ix = ny, nx; found = True; break
                if found: break
            if found: break
    taken.add((iy, ix))
    seed_nodes.append(int(nid[iy, ix])); seed_labels.append(i + 1)
seed_nodes = np.array(seed_nodes); seed_labels = np.array(seed_labels)

# ---------- граф соседних пикселей суши (8-связность, веса 1 и √2) ----------
R, C, D = [], [], []
S2 = np.sqrt(2.0)
def link(a, b, w):
    sel = (a >= 0) & (b >= 0)
    R.append(a[sel]); C.append(b[sel]); D.append(np.full(int(sel.sum()), w))
link(nid[:, :-1],  nid[:, 1:],  1.0)                      # →
link(nid[:-1, :],  nid[1:, :],  1.0)                      # ↓
link(nid[:-1, :-1], nid[1:, 1:], S2)                      # ↘
link(nid[:-1, 1:],  nid[1:, :-1], S2)                     # ↙
graph = csr_matrix((np.concatenate(D),
                    (np.concatenate(R), np.concatenate(C))), shape=(K, K))

# ---------- геодезическое расстояние по суше от ближайшей столицы ----------
dist, _, src = dijkstra(graph, directed=False, indices=seed_nodes,
                        return_predecessors=True, min_only=True)
label_of_node = np.zeros(K, np.int32)
label_of_node[seed_nodes] = seed_labels                   # узел-сид -> метка столицы
reachable = src >= 0
node_lab = np.zeros(K, np.int32)
node_lab[reachable] = label_of_node[src[reachable]]       # метка ближайшего сида

labels = np.zeros((H, W), np.int32)
labels[land_mask] = node_lab
occ = labels > 0
print("занятой суши:", int(occ.sum()), "/ незанятой:", int(land_mask.sum() - occ.sum()))

# ---------- внутренние границы (между разными занятыми областями) ----------
def internal_boundaries(lab):
    b = np.zeros(lab.shape, bool)
    for sl_a, sl_b in [((slice(None), slice(None, -1)), (slice(None), slice(1, None))),
                       ((slice(None, -1), slice(None)), (slice(1, None), slice(None))),
                       ((slice(None, -1), slice(None, -1)), (slice(1, None), slice(1, None))),
                       ((slice(None, -1), slice(1, None)), (slice(1, None), slice(None, -1)))]:
        a, c = lab[sl_a], lab[sl_b]
        d = (a != c) & (a > 0) & (c > 0)
        b[sl_a] |= d; b[sl_b] |= d
    return b

bnd = internal_boundaries(labels)
bnd = ndi.binary_dilation(bnd, np.ones((3, 3), bool), iterations=1)

# ---------- палитра (как в предыдущей карте) ----------
hue = (np.arange(ncap) * 0.6180339887) % 1.0
sat = 0.42 + 0.18 * ((np.arange(ncap) * 0.123) % 1.0)
val = 0.80 + 0.15 * ((np.arange(ncap) * 0.317) % 1.0)
pal = hsv_to_rgb(np.c_[hue, sat, val])

rgba = np.zeros((H, W, 4), np.float32)
m = occ
rgba[m, :3] = pal[labels[m] - 1]; rgba[m, 3] = 1.0
rgba[bnd, :3] = [0.07, 0.10, 0.14]; rgba[bnd, 3] = 1.0     # тёмные границы поверх заливки

# ---------- рисуем ----------
BORDER = "#9aa6b0"; CAP = "#7a1414"
fig, ax = plt.subplots(figsize=(22, 11.6))
ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")

# лёгкая координатная сетка
for L in range(-150, 151, 30):
    gx, gy = fwd.transform(np.full(200, L), np.linspace(-89, 89, 200))
    ax.plot(gx, gy, color="#e7eaee", lw=0.5, zorder=0)
for B in range(-60, 61, 30):
    gx, gy = fwd.transform(np.linspace(-179, 179, 400), np.full(400, B))
    ax.plot(gx, gy, color="#e7eaee", lw=0.5, zorder=0)

im = ax.imshow(rgba, extent=[xmin, xmax, ymin, ymax], origin="lower",
               interpolation="nearest", zorder=2)
im.set_clip_path(land_path, ax.transData)

# тонкие реальные границы стран и контуры суши
countries_rob.boundary.plot(ax=ax, color=BORDER, linewidth=0.4, zorder=3)

ax.scatter(cx, cy, s=6, color=CAP, edgecolor="white", linewidth=0.3, zorder=5)
ax.plot(ox, oy, color="#c2cad1", linewidth=1.1, zorder=1)

ax.set_title("Рост от столиц с остановкой у воды (по суше)\n"
             "цвет — куда дотягивается столица, не пересекая воду · "
             "белое — незанятая суша · тонкие — реальные границы",
             color="#23303c", fontsize=15, pad=14)
ax.margins(0.01); plt.tight_layout()

fig.savefig("voronoi_capitals_coaststop.png", dpi=200, facecolor="white",
            bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_capitals_coaststop.svg", facecolor="white",
            bbox_inches="tight", pad_inches=0.15)
print("saved coast-stop PNG + SVG", rgba.shape)
