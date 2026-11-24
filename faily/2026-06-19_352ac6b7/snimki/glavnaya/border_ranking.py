#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Рейтинг сухопутных госграниц по отклонению от воронóвской реконструкции (адм-центры).
Каждый участок помечается парой стран; отклонение усредняется по паре.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import SphericalVoronoi, cKDTree
import matplotlib.pyplot as plt
import matplotlib as mpl

NE = "ne"; Re = 6371.0

def llxyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)]
def xyzll(p):
    return (np.degrees(np.arctan2(p[..., 1], p[..., 0])),
            np.degrees(np.arcsin(np.clip(p[..., 2], -1, 1))))
def gc_km(chord):
    return Re * 2 * np.arcsin(np.clip(chord/2, 0, 1))
def hav_km(lo1, la1, lo2, la2):
    p1, q1, p2, q2 = map(np.radians, (lo1, la1, lo2, la2))
    h = np.sin((q2-q1)/2)**2 + np.cos(q1)*np.cos(q2)*np.sin((p2-p1)/2)**2
    return 2*Re*np.arcsin(np.sqrt(np.clip(h, 0, 1)))

# ---------- Вороной по адм-центрам -> межстрановые рёбра -> KDTree ----------
adm = gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm = adm[adm.geometry.notna() & ~adm.geometry.is_empty]
rp = adm.geometry.representative_point()
lon = rp.x.to_numpy(); lat = rp.y.to_numpy(); ac = adm["adm0_a3"].to_numpy().astype(object)
_, u = np.unique(np.round(np.c_[lon, lat], 4), axis=0, return_index=True); u = np.sort(u)
lon, lat, ac = lon[u], lat[u], ac[u]
sv = SphericalVoronoi(llxyz(lon, lat), 1.0, np.zeros(3)); sv.sort_vertices_of_regions()
es = {}
for s, reg in enumerate(sv.regions):
    m = len(reg)
    for i in range(m):
        a, b = reg[i], reg[(i+1) % m]; k = (a, b) if a < b else (b, a); es.setdefault(k, []).append(s)
def slerp(p0, p1, k=24):
    d = np.clip(np.dot(p0, p1), -1, 1); om = np.arccos(d)
    if om < 1e-9: return np.array([p0, p1])
    t = np.linspace(0, 1, k)[:, None]
    return np.sin((1-t)*om)/np.sin(om)*p0 + np.sin(t*om)/np.sin(om)*p1
VL, VB = [], []
for (a, b), ss in es.items():
    if len(ss) >= 2 and ac[ss[0]] != ac[ss[1]]:
        pl, pb = xyzll(slerp(sv.vertices[a], sv.vertices[b])); VL.append(pl); VB.append(pb)
vtree = cKDTree(llxyz(np.concatenate(VL), np.concatenate(VB)))

# ---------- смежные пары стран и их общая граница ----------
cg = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")[["NAME", "NAME_RU", "geometry"]].reset_index(drop=True)
cg["geometry"] = cg.geometry.buffer(0)
sj = gpd.sjoin(cg, cg, predicate="intersects")
cand = set()
for li, ri in zip(sj.index, sj["index_right"]):
    if li < ri: cand.add((li, ri))
print("кандидатных пар:", len(cand))

def flat(geom):
    t = geom.geom_type
    if t == "LineString": return [geom]
    if t in ("MultiLineString", "GeometryCollection"): 
        out=[]
        for g in geom.geoms: out += flat(g)
        return out
    return []

EPS = 0.04
rows = []
for li, ri in cand:
    A = cg.geometry.iloc[li]; B = cg.geometry.iloc[ri]
    try:
        shared = A.boundary.intersection(B.buffer(EPS))
    except Exception:
        continue
    lines = [g for g in flat(shared) if g.length > 0]
    if not lines: continue
    LO, LA = [], []
    for ls in lines:
        n = max(2, int(ls.length / 0.1))
        for t in np.linspace(0, 1, n):
            p = ls.interpolate(t, normalized=True); LO.append(p.x); LA.append(p.y)
    LO = np.array(LO); LA = np.array(LA)
    if LO.size < 2: continue
    dev = gc_km(vtree.query(llxyz(LO, LA))[0])
    # длина границы (км), суммируем по соседним точкам, отбрасывая разрывы между компонентами
    seg = hav_km(LO[:-1], LA[:-1], LO[1:], LA[1:])
    length_km = seg[seg < 80].sum()
    rows.append((cg.NAME_RU.iloc[li], cg.NAME_RU.iloc[ri],
                 cg.NAME.iloc[li], cg.NAME.iloc[ri],
                 length_km, float(np.mean(dev)), float(np.median(dev)), float(np.max(dev))))

import pandas as pd
df = pd.DataFrame(rows, columns=["A_ru", "B_ru", "A_en", "B_en",
                                 "len_km", "mean_km", "median_km", "max_km"])
df = df[df.len_km >= 150].copy()                      # только существенные участки
df["mean_km"] = df.mean_km.round(0); df["median_km"] = df.median_km.round(0)
df["max_km"] = df.max_km.round(0); df["len_km"] = df.len_km.round(0)
df_top = df.sort_values("mean_km", ascending=False).reset_index(drop=True)
df.to_csv("border_deviation_ranking.csv", index=False)
print("пар в рейтинге (длина ≥150 км):", len(df))

print("\n=== ТОП-30 самых отклоняющихся границ (по среднему, км) ===")
print(f"{'#':>2}  {'граница':38s} {'длина':>6} {'сред':>5} {'медиана':>7} {'макс':>5}")
for i, r in df_top.head(30).iterrows():
    name = f"{r.A_ru}–{r.B_ru}"
    print(f"{i+1:>2}  {name[:38]:38s} {r.len_km:6.0f} {r.mean_km:5.0f} {r.median_km:7.0f} {r.max_km:5.0f}")

print("\n=== 12 самых «органических» (минимум среднего, длина ≥400 км) ===")
for i, r in df[df.len_km >= 400].sort_values("mean_km").head(12).reset_index(drop=True).iterrows():
    name = f"{r.A_ru}–{r.B_ru}"
    print(f"{i+1:>2}  {name[:38]:38s} {r.len_km:6.0f} {r.mean_km:5.0f} {r.median_km:7.0f} {r.max_km:5.0f}")

# ---------- столбчатый рейтинг ----------
top = df_top.head(28).iloc[::-1]
fig, ax = plt.subplots(figsize=(13, 12))
cmap = plt.cm.turbo; norm = mpl.colors.Normalize(0, 250)
cols = cmap(norm(top.mean_km.values))
y = np.arange(len(top))
ax.barh(y, top.mean_km.values, color=cols, edgecolor="white", linewidth=0.5)
ax.set_yticks(y); ax.set_yticklabels([f"{a}–{b}" for a, b in zip(top.A_ru, top.B_ru)], fontsize=10)
for yi, (m, mx) in enumerate(zip(top.mean_km.values, top.max_km.values)):
    ax.text(m+3, yi, f"{m:.0f}  (макс {mx:.0f})", va="center", fontsize=8, color="#333")
ax.set_xlabel("среднее отклонение реальной границы от линии Вороного, км")
ax.set_title("Рейтинг сухопутных госграниц по «неорганичности»\n(чем больше — тем дальше реальная линия от шва расселения)",
             fontsize=14, pad=12)
ax.set_xlim(0, max(top.mean_km.max()*1.18, 260))
ax.spines[["top", "right"]].set_visible(False)
ax.margins(y=0.005); plt.tight_layout()
fig.savefig("border_ranking.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2)
fig.savefig("border_ranking.svg", facecolor="white", bbox_inches="tight", pad_inches=0.2)
print("\nsaved CSV + ranking chart")
