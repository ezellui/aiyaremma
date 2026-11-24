#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«Индекс навязанности» границы = отклонение / локальный масштаб решётки.
Локальный масштаб = среднее расстояние от точки границы до 3 ближайших адм-центров.
Снимает конфаунд разреженности: остаётся смещение вопреки наличию данных.
"""
import numpy as np
import geopandas as gpd
import pandas as pd
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
def gc_km(chord): return Re * 2 * np.arcsin(np.clip(chord/2, 0, 1))
def hav_km(a, b, c, d):
    p1, q1, p2, q2 = map(np.radians, (a, b, c, d))
    h = np.sin((q2-q1)/2)**2 + np.cos(q1)*np.cos(q2)*np.sin((p2-p1)/2)**2
    return 2*Re*np.arcsin(np.sqrt(np.clip(h, 0, 1)))

# ---------- адм-центры, Вороной, межстрановые рёбра, деревья ----------
adm = gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm = adm[adm.geometry.notna() & ~adm.geometry.is_empty]
rp = adm.geometry.representative_point()
lon = rp.x.to_numpy(); lat = rp.y.to_numpy(); ac = adm["adm0_a3"].to_numpy().astype(object)
_, u = np.unique(np.round(np.c_[lon, lat], 4), axis=0, return_index=True); u = np.sort(u)
lon, lat, ac = lon[u], lat[u], ac[u]
seed_xyz = llxyz(lon, lat)
seedtree = cKDTree(seed_xyz)                                    # все центры (для масштаба)

sv = SphericalVoronoi(seed_xyz, 1.0, np.zeros(3)); sv.sort_vertices_of_regions()
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

def local_scale(lo, la):                                        # среднее до 3 ближайших центров, км
    dch, _ = seedtree.query(llxyz(lo, la), k=3)
    return np.clip(gc_km(dch).mean(axis=1), 10.0, None)         # пол 10 км от деления на ~0

# ---------- смежные пары и общие границы ----------
cg = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")[["NAME", "NAME_RU", "geometry"]].reset_index(drop=True)
cg["geometry"] = cg.geometry.buffer(0)
sj = gpd.sjoin(cg, cg, predicate="intersects")
cand = {(li, ri) for li, ri in zip(sj.index, sj["index_right"]) if li < ri}

def flat(g):
    t = g.geom_type
    if t == "LineString": return [g]
    if t in ("MultiLineString", "GeometryCollection"):
        o = []
        for x in g.geoms: o += flat(x)
        return o
    return []

rows = []
for li, ri in cand:
    A = cg.geometry.iloc[li]; B = cg.geometry.iloc[ri]
    try: shared = A.boundary.intersection(B.buffer(0.04))
    except Exception: continue
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
    sc = local_scale(LO, LA)
    norm = dev / sc
    seg = hav_km(LO[:-1], LA[:-1], LO[1:], LA[1:]); length = seg[seg < 80].sum()
    rows.append((cg.NAME_RU.iloc[li], cg.NAME_RU.iloc[ri], length,
                 float(np.mean(dev)), float(np.mean(sc)), float(np.mean(norm)), float(np.median(norm))))

df = pd.DataFrame(rows, columns=["A_ru", "B_ru", "len_km", "dev_km", "scale_km", "norm_mean", "norm_med"])
df = df[df.len_km >= 150].copy()
for c in ["len_km", "dev_km", "scale_km"]: df[c] = df[c].round(0)
df["norm_mean"] = df.norm_mean.round(2); df["norm_med"] = df.norm_med.round(2)
df = df.sort_values("norm_mean", ascending=False).reset_index(drop=True)
df.to_csv("border_imposedness_index.csv", index=False)
print("пар:", len(df), "| нормир. перцентили:",
      {q: round(np.percentile(df.norm_mean, q), 2) for q in (50, 90, 99)})

print("\n=== ТОП-30 «индекс навязанности» (отклонение / локальный масштаб) ===")
print(f"{'#':>2}  {'граница':40s} {'инд':>4} {'откл,км':>7} {'масшт,км':>8} {'длина':>6}")
for i, r in df.head(30).iterrows():
    print(f"{i+1:>2}  {f'{r.A_ru}–{r.B_ru}'[:40]:40s} {r.norm_mean:4.2f} {r.dev_km:7.0f} {r.scale_km:8.0f} {r.len_km:6.0f}")

print("\n=== 12 самых «органических» по индексу (длина ≥400 км) ===")
for i, r in df[df.len_km >= 400].sort_values("norm_mean").head(12).reset_index(drop=True).iterrows():
    print(f"{i+1:>2}  {f'{r.A_ru}–{r.B_ru}'[:40]:40s} {r.norm_mean:4.2f} {r.dev_km:7.0f} {r.scale_km:8.0f} {r.len_km:6.0f}")

# ---------- диаграмма ----------
top = df.head(28).iloc[::-1]
fig, ax = plt.subplots(figsize=(13.5, 12))
norm = mpl.colors.Normalize(0, max(df.norm_mean.head(28).max(), 1.0))
y = np.arange(len(top))
ax.barh(y, top.norm_mean.values, color=plt.cm.turbo(norm(top.norm_mean.values)),
        edgecolor="white", linewidth=0.5)
ax.set_yticks(y); ax.set_yticklabels([f"{a}–{b}" for a, b in zip(top.A_ru, top.B_ru)], fontsize=10)
for yi, (m, dv) in enumerate(zip(top.norm_mean.values, top.dev_km.values)):
    ax.text(m+0.02, yi, f"{m:.2f}  ({dv:.0f} км)", va="center", fontsize=8, color="#333")
ax.set_xlabel("индекс навязанности = отклонение / локальный масштаб решётки (безразмерный)")
ax.set_title("Рейтинг границ без конфаунда разреженности\n"
             "наверху — линии поперёк плотного симметричного расселения",
             fontsize=14, pad=12)
ax.set_xlim(0, top.norm_mean.max()*1.18)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
fig.savefig("border_imposedness.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2)
fig.savefig("border_imposedness.svg", facecolor="white", bbox_inches="tight", pad_inches=0.2)
print("\nsaved CSV + chart")
