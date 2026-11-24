#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Картограмма населения: площадь каждой страны делается пропорциональной её населению.
Неконтигуальная (Olson) — каждая страна масштабируется вокруг своего центроида
коэффициентом sqrt(целевая площадь / нынешняя площадь). Проекция равновеликая
(Equal Earth), иначе сравнение площадей не имеет смысла.
"""
import numpy as np
import geopandas as gpd
from shapely.affinity import scale
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

NE = "ne"
EQ = "EPSG:8857"          # Equal Earth (равновеликая)

c = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
c = c[["NAME", "NAME_RU", "POP_EST", "CONTINENT", "geometry"]].copy()
c["pop"] = c["POP_EST"].astype(float)
c = c[c["pop"] > 1000].to_crs(EQ).reset_index(drop=True)
c["geometry"] = c.geometry.buffer(0)

c["area"] = c.geometry.area
Atot = c["area"].sum(); Ptot = c["pop"].sum()
c["tarea"] = c["pop"] / Ptot * Atot           # целевая площадь ∝ населению (сумма сохраняется)
c["scale"] = np.sqrt(c["tarea"] / c["area"])
print(f"стран: {len(c)} | население всего {Ptot/1e9:.2f} млрд")
big = c.sort_values("scale", ascending=False).head(5)[["NAME", "scale"]]
small = c.sort_values("scale").head(5)[["NAME", "scale"]]
print("сильнее всего растут:", [f'{r.NAME}×{r.scale:.1f}' for _, r in big.iterrows()])
print("сильнее всего ужимаются:", [f'{r.NAME}×{r.scale:.2f}' for _, r in small.iterrows()])

def resize(geom, s):
    return scale(geom, xfact=s, yfact=s, origin=geom.centroid)
c["cart"] = [resize(g, s) for g, s in zip(c.geometry, c["scale"])]

# палитра по континентам
CONT = {"Africa": "#e9c46a", "Asia": "#e76f51", "Europe": "#2a9d8f",
        "North America": "#4a7fb5", "South America": "#a06cd5",
        "Oceania": "#f4a261", "Antarctica": "#b8c4cc", "Seven seas (open ocean)": "#cccccc"}
c["col"] = c["CONTINENT"].map(CONT).fillna("#999999")

fig, ax = plt.subplots(figsize=(26, 13.5))
ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")

# слабый контур реальной карты для ориентира
c.boundary.plot(ax=ax, color="#d8dde2", linewidth=0.4, zorder=1)

cart = gpd.GeoDataFrame(c[["NAME", "col"]], geometry=c["cart"], crs=EQ)
cart.plot(ax=ax, color=c["col"], edgecolor="#1c2733", linewidth=0.4, alpha=0.92, zorder=3)

# легенда по континентам
from matplotlib.patches import Patch
present = [k for k in CONT if (c["CONTINENT"] == k).any() and k != "Seven seas (open ocean)"]
ax.legend(handles=[Patch(facecolor=CONT[k], edgecolor="none", label=k) for k in present],
          loc="lower left", fontsize=11, frameon=True, facecolor="white", edgecolor="#ccc")

ax.set_title("Картограмма населения мира: площадь страны ∝ её населению\n"
             "бледный контур — настоящие очертания; цветом — раздутая/сжатая по населению страна",
             color="#23303c", fontsize=20, pad=14)
ax.margins(0.01); plt.tight_layout()
fig.savefig("population_cartogram.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2)
fig.savefig("population_cartogram.svg", facecolor="white", bbox_inches="tight", pad_inches=0.2)
print("saved cartogram PNG + SVG")
