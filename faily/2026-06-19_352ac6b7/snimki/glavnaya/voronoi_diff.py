#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Графический дифф двух разбиений суши по столицам:
  (A) без ограничений  — ближайшая столица по большому кругу (через воду можно);
  (B) с ограничением    — рост только по суше, фронт встаёт у воды.
Категории суши:
  совпало | сменило столицу | отрезано водой (в B стало белым).
Дополнительно: обе сети границ линиями (старые — красные, новые — тёмные).
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry.polygon import orient
from shapely.geometry import shape as shp_shape
from shapely.ops import unary_union
from rasterio.features import shapes as rio_shapes
from rasterio.transform import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

NE = "ne"; TGT = "ESRI:54030"
fwd = Transformer.from_crs("EPSG:4326", TGT, always_xy=True)
inv = Transformer.from_crs(TGT, "EPSG:4326", always_xy=True)

# ---------- данные ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
places    = gpd.read_file(f"{NE}/ne_50m_populated_places.geojson")
caps = places[places["ADM0CAP"] == 1]
lon = caps.geometry.x.to_numpy(); lat = caps.geometry.y.to_numpy()
_, uniq = np.unique(np.round(np.c_[lon, lat], 4), axis=0, return_index=True)
lon, lat = lon[uniq], lat[uniq]; ncap = len(lon)

def ll_to_xyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
pts = ll_to_xyz(lon, lat)

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

# ---------- сетка ----------
lat_e = np.linspace(-90, 90, 400)
rx, ry = fwd.transform(np.full_like(lat_e, 180), lat_e)
lx, ly = fwd.transform(np.full_like(lat_e, -180), lat_e)
ox = np.r_[rx, lx[::-1]]; oy = np.r_[ry, ly[::-1]]
xmin, xmax = lx.min(), rx.max(); ymin, ymax = oy.min(), oy.max()

W = 3000
H = int(round(W * (ymax - ymin) / (xmax - xmin)))
xs = np.linspace(xmin, xmax, W); ys = np.linspace(ymin, ymax, H)
XX, YY = np.meshgrid(xs, ys)
px = (xmax - xmin) / W
_xform = from_bounds(xmin, ymin, xmax, ymax, W, H)

from rasterio import features
_shapes = [(g, 1) for g in countries_rob.geometry if g and not g.is_empty]
land_mask = features.rasterize(_shapes, out_shape=(H, W), transform=_xform, fill=0).astype(bool)
land_mask = land_mask[::-1]

glon, glat = inv.transform(XX.ravel(), YY.ravel())
glon = glon.reshape(H, W); glat = glat.reshape(H, W)

def xy_to_idx(x, y):
    ix = np.clip(np.round((x - xmin)/(xmax - xmin)*(W-1)).astype(int), 0, W-1)
    iy = np.clip(np.round((y - ymin)/(ymax - ymin)*(H-1)).astype(int), 0, H-1)
    return ix, iy

# ---------- (A) без ограничений: ближайшая столица по сфере ----------
tree_caps = cKDTree(pts)
lab_unc = np.zeros((H, W), np.int32)
valid = land_mask & np.isfinite(glon) & np.isfinite(glat)
lab_unc[valid] = tree_caps.query(ll_to_xyz(glon[valid], glat[valid]))[1] + 1

# ---------- (B) с ограничением: геодезический рост по суше ----------
cx, cy = fwd.transform(lon, lat); cix, ciy = xy_to_idx(cx, cy)
nid = -np.ones((H, W), np.int64)
land_rc = np.argwhere(land_mask); K = land_rc.shape[0]
nid[land_mask] = np.arange(K); land_tree = cKDTree(land_rc)
taken = set(); seed_nodes, seed_labels = [], []
for i in range(ncap):
    iy, ix = ciy[i], cix[i]
    if not land_mask[iy, ix]:
        _, j = land_tree.query([iy, ix]); iy, ix = land_rc[j]
    if (iy, ix) in taken:
        done = False
        for r in range(1, 16):
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    ny, nx = iy+dy, ix+dx
                    if 0 <= ny < H and 0 <= nx < W and land_mask[ny, nx] and (ny, nx) not in taken:
                        iy, ix = ny, nx; done = True; break
                if done: break
            if done: break
    taken.add((iy, ix)); seed_nodes.append(int(nid[iy, ix])); seed_labels.append(i+1)
seed_nodes = np.array(seed_nodes); seed_labels = np.array(seed_labels)

R, C, D = [], [], []; S2 = np.sqrt(2.0)
def link(a, b, w):
    sel = (a >= 0) & (b >= 0)
    R.append(a[sel]); C.append(b[sel]); D.append(np.full(int(sel.sum()), w))
link(nid[:, :-1], nid[:, 1:], 1.0); link(nid[:-1, :], nid[1:, :], 1.0)
link(nid[:-1, :-1], nid[1:, 1:], S2); link(nid[:-1, 1:], nid[1:, :-1], S2)
graph = csr_matrix((np.concatenate(D), (np.concatenate(R), np.concatenate(C))), shape=(K, K))
_, _, src = dijkstra(graph, directed=False, indices=seed_nodes,
                     return_predecessors=True, min_only=True)
lab_of_node = np.zeros(K, np.int32); lab_of_node[seed_nodes] = seed_labels
reach = src >= 0; node_lab = np.zeros(K, np.int32); node_lab[reach] = lab_of_node[src[reach]]
lab_con = np.zeros((H, W), np.int32); lab_con[land_mask] = node_lab

# ---------- категории диффа ----------
cat = np.zeros((H, W), np.uint8)                 # 0 = не суша
same = valid & (lab_con > 0) & (lab_con == lab_unc)
diff = valid & (lab_con > 0) & (lab_con != lab_unc)
lost = land_mask & (lab_con == 0)
cat[same] = 1; cat[diff] = 2; cat[lost] = 3
cat[(cat == 0) & land_mask & (lab_con > 0)] = 1  # редкие краевые пиксели -> «совпало»
print("совпало:", int((cat==1).sum()), "сменило:", int((cat==2).sum()), "отрезано:", int((cat==3).sum()))

COL = {1: "#e9e9e9", 2: "#e76f51", 3: "#2a9d8f"}
rgba = np.zeros((H, W, 4), np.float32)
for k, c in COL.items():
    sel = cat == k
    rgba[sel, :3] = tuple(int(c[i:i+2], 16)/255 for i in (1, 3, 5)); rgba[sel, 3] = 1.0

# ---------- векторизация границ обеих версий ----------
def flatten_lines(geom):
    if geom.is_empty: return []
    t = geom.geom_type
    if t == "LineString": return [geom]
    if t in ("MultiLineString", "GeometryCollection"):
        out = []
        for g in geom.geoms: out += flatten_lines(g)
        return out
    return []
def chaikin(c, it=2):
    c = np.asarray(c, float)
    for _ in range(it):
        if len(c) < 3: break
        p, q = c[:-1], c[1:]
        nw = np.empty((2*len(p), 2)); nw[0::2] = 0.75*p+0.25*q; nw[1::2] = 0.25*p+0.75*q
        c = np.vstack([c[0], nw, c[-1]])
    return c
def vectorize(lab, occ_mask):
    lab_t = np.ascontiguousarray(lab[::-1]); mask_t = np.ascontiguousarray(occ_mask[::-1])
    polys = [shp_shape(g) for g, v in rio_shapes(lab_t, mask=mask_t, transform=_xform, connectivity=8) if v > 0]
    if not polys: return []
    internal = unary_union([p.boundary for p in polys]).difference(
        unary_union(polys).boundary.buffer(px*0.6))
    segs = []
    for ls in flatten_lines(internal):
        cc = np.asarray(ls.simplify(px*1.0).coords)
        if len(cc) >= 2: segs.append(chaikin(cc, 2))
    return segs

segs_unc = vectorize(lab_unc, land_mask)          # старые границы (без ограничений)
segs_con = vectorize(lab_con, lab_con > 0)        # новые границы (по суше)
print("границ старых:", len(segs_unc), "новых:", len(segs_con))

# ---------- рисуем ----------
fig, ax = plt.subplots(figsize=(22, 11.6))
ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")
for L in range(-150, 151, 30):
    gx, gy = fwd.transform(np.full(200, L), np.linspace(-89, 89, 200)); ax.plot(gx, gy, color="#eef1f3", lw=0.5, zorder=0)
for B in range(-60, 61, 30):
    gx, gy = fwd.transform(np.linspace(-179, 179, 400), np.full(400, B)); ax.plot(gx, gy, color="#eef1f3", lw=0.5, zorder=0)

im = ax.imshow(rgba, extent=[xmin, xmax, ymin, ymax], origin="lower", interpolation="nearest", zorder=2)
im.set_clip_path(land_path, ax.transData)

# старые границы (красные, пунктир) и новые (тёмные, сплошные)
lcu = LineCollection(segs_unc, colors="#c81d25", linewidths=0.8, zorder=4,
                     linestyle=(0, (4, 2)), alpha=0.95)
ax.add_collection(lcu); lcu.set_clip_path(land_path, ax.transData)
lcc = LineCollection(segs_con, colors="#1d3557", linewidths=1.2, zorder=5,
                     capstyle="round", joinstyle="round")
ax.add_collection(lcc); lcc.set_clip_path(land_path, ax.transData)

ax.scatter(cx, cy, s=5, color="#5a1010", edgecolor="white", linewidth=0.25, zorder=6)
ax.plot(ox, oy, color="#c2cad1", linewidth=1.1, zorder=1)

legend = [
    Patch(facecolor=COL[1], edgecolor="none", label="совпало (та же столица)"),
    Patch(facecolor=COL[2], edgecolor="none", label="сменило столицу (ближе по суше другая)"),
    Patch(facecolor=COL[3], edgecolor="none", label="отрезано водой (в B → белым)"),
    Line2D([0], [0], color="#1d3557", lw=1.6, label="границы B (рост по суше)"),
    Line2D([0], [0], color="#c81d25", lw=1.4, linestyle=(0, (4, 2)), label="границы A (без ограничений)"),
]
ax.legend(handles=legend, loc="lower left", fontsize=10, frameon=True,
          facecolor="white", edgecolor="#cccccc", framealpha=0.95).set_zorder(10)

ax.set_title("Дифф границ: ближайшая столица по сфере (A) против роста по суше (B)",
             color="#23303c", fontsize=16, pad=14)
ax.margins(0.01); plt.tight_layout()
fig.savefig("voronoi_diff.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
fig.savefig("voronoi_diff.svg", facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("saved diff PNG + SVG")
