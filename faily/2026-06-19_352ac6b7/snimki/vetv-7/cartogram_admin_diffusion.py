#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Бесшовная (контигуальная) картограмма Гастнера–Ньюмана для ячеек Вороного
админ-центров. Поле плотности населения (KDE по городам) выравнивается диффузией;
узлы сетки протаскиваются по полю скоростей v=-grad(rho)/rho; ячейки переносятся
вместе с сеткой, оставаясь сцеплёнными. Площадь ячейки -> ∝ её населению.
Проекция равновеликая цилиндрическая EPSG:6933.
"""
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from scipy.fft import dctn, idctn
from rasterio import features
from rasterio.transform import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

NE = "ne"; CRS = "EPSG:6933"
fwd = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)

# ---------- экстент мира в равновеликой проекции ----------
lo = np.linspace(-180, 180, 361); la = np.linspace(-85, 85, 171)
LO, LA = np.meshgrid(lo, la); WX, WY = fwd.transform(LO.ravel(), LA.ravel())
xmin, xmax, ymin, ymax = WX.min(), WX.max(), WY.min(), WY.max()
NX = 900; NY = int(round(NX*(ymax-ymin)/(xmax-xmin)))
xs = np.linspace(xmin, xmax, NX); ys = np.linspace(ymin, ymax, NY)
GX, GY = np.meshgrid(xs, ys)                              # (NY,NX) world coords, row=y↑
print(f"сетка {NX}×{NY}")

# ---------- админ-центры (сиды) и их страны ----------
adm = gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm = adm[adm.geometry.notna() & ~adm.geometry.is_empty]
rp = adm.geometry.representative_point()
alon = rp.x.to_numpy(); alat = rp.y.to_numpy()
acode = adm["adm0_a3"].astype("category")
acidx = acode.cat.codes.to_numpy()                       # индекс страны
_, uu = np.unique(np.round(np.c_[alon, alat], 4), axis=0, return_index=True); uu = np.sort(uu)
alon, alat, acidx = alon[uu], alat[uu], acidx[uu]
ax, ay = fwd.transform(alon, alat)
atree = cKDTree(np.c_[ax, ay])
# метка ячейки и страны на каждый пиксель
_, cell = atree.query(np.c_[GX.ravel(), GY.ravel()])
cell = cell.reshape(NY, NX)
country = acidx[cell]                                     # (NY,NX)

# ---------- маска суши ----------
countries = gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson").to_crs(CRS)
xf = from_bounds(xmin, ymin, xmax, ymax, NX, NY)
land = features.rasterize([(g, 1) for g in countries.geometry if g and not g.is_empty],
                          out_shape=(NY, NX), transform=xf, fill=0).astype(bool)[::-1]
print("суша, пикс:", int(land.sum()))

# ---------- поле плотности населения (KDE по городам) ----------
city = gpd.read_file(f"{NE}/ne_10m_populated_places.geojson")
cxw, cyw = fwd.transform(city.geometry.x.to_numpy(), city.geometry.y.to_numpy())
cpop = np.clip(city["POP_MAX"].fillna(0).to_numpy().astype(float), 1.0, None)
ix = np.clip(((cxw-xmin)/(xmax-xmin)*(NX-1)).astype(int), 0, NX-1)
iy = np.clip(((cyw-ymin)/(ymax-ymin)*(NY-1)).astype(int), 0, NY-1)
rho = np.zeros((NY, NX))
np.add.at(rho, (iy, ix), cpop)
rho = ndi.gaussian_filter(rho, sigma=5)
rho += 0.10 * rho.mean()                                 # «пол» — пустое сжимается, но не схлопывается
rho *= (NX*NY)/rho.sum()                                  # нормировка: средняя плотность = 1
print(f"плотность: min {rho.min():.3f} mean {rho.mean():.3f} max {rho.max():.1f}")

# ---------- диффузия Гастнера–Ньюмана: смещения узлов ----------
kx = np.pi*np.arange(NX)/NX; ky = np.pi*np.arange(NY)/NY
K2 = (ky[:, None]**2 + kx[None, :]**2)
A = dctn(rho, type=2, norm="ortho")
def rho_t(t): return idctn(A*np.exp(-K2*t), type=2, norm="ortho")

px = GX.ravel().copy(); py = GY.ravel().copy()           # позиции трассеров (мировые коорд.)
sx = (NX-1)/(xmax-xmin); sy = (NY-1)/(ymax-ymin)         # мир->индекс
def vel(t):
    r = np.maximum(rho_t(t), 1e-4)
    gy, gx = np.gradient(r)                               # в индексных единицах
    vx = -gx/r * sx**-1 * sx   # держим в мировых: см. ниже
    return r, gx, gy
# скорость в МИРОВЫХ координатах: v = -grad_world(rho)/rho; grad_world = grad_index * (index/world)
def interp(F, wx, wy):
    cx = np.clip((wx-xmin)*sx, 0, NX-1.001); cy = np.clip((wy-ymin)*sy, 0, NY-1.001)
    x0 = cx.astype(int); y0 = cy.astype(int); fx = cx-x0; fy = cy-y0
    return (F[y0, x0]*(1-fx)*(1-fy)+F[y0, x0+1]*fx*(1-fy)
            +F[y0+1, x0]*(1-fx)*fy+F[y0+1, x0+1]*fx*fy)
def vfield(t):
    r = np.maximum(rho_t(t), 1e-4)
    gyi, gxi = np.gradient(r)
    vx = -(gxi*sx)/r; vy = -(gyi*sy)/r                   # мировая скорость
    return vx, vy

t = 0.0; dt = 0.15; T = 4.6/max(kx[1], ky[1])**2          # до выравнивания низшей моды
print(f"T_max ≈ {T:.0f}")
nstep = 0
while t < T:
    vx, vy = vfield(t)
    k1x = interp(vx, px, py); k1y = interp(vy, px, py)    # Heun
    midx = px+dt*k1x; midy = py+dt*k1y
    vx2, vy2 = vfield(t+dt)
    k2x = interp(vx2, midx, midy); k2y = interp(vy2, midx, midy)
    px += 0.5*dt*(k1x+k2x); py += 0.5*dt*(k1y+k2y)
    px = np.clip(px, xmin, xmax); py = np.clip(py, ymin, ymax)
    t += dt; dt *= 1.05; nstep += 1
print("шагов:", nstep, "| итоговая неравномерность:",
      round((rho_t(t).max()-rho_t(t).min())/rho_t(t).mean(), 3))

# ---------- рендер: перенос меток на новые позиции узлов ----------
moved = np.c_[px, py]
mtree = cKDTree(moved)
OX = 1500; OY = int(round(OX*(ymax-ymin)/(xmax-xmin)))
oxs = np.linspace(px.min(), px.max(), OX); oys = np.linspace(py.min(), py.max(), OY)
OXX, OYY = np.meshgrid(oxs, oys)
_, nn = mtree.query(np.c_[OXX.ravel(), OYY.ravel()])
cell_o = cell.ravel()[nn].reshape(OY, OX)
ctry_o = country.ravel()[nn].reshape(OY, OX)
land_o = land.ravel()[nn].reshape(OY, OX)

# границы
def edges(lab, both_pos=True):
    b = np.zeros(lab.shape, bool)
    b[:, :-1] |= lab[:, :-1] != lab[:, 1:]; b[1:, :] |= lab[:-1, :] != lab[1:, :]
    return b
admin_b = edges(cell_o) & land_o
ctry_b = ndi.binary_dilation(edges(ctry_o) & land_o, np.ones((2, 2), bool))

# цвета по странам
ncol = country.max()+1
hue = (np.arange(ncol)*0.61803398875) % 1.0
pal = hsv_to_rgb(np.c_[hue, np.full(ncol, 0.45), np.full(ncol, 0.92)])
img = np.ones((OY, OX, 4), np.float32)                    # белый фон
m = land_o
img[m, :3] = pal[ctry_o[m]]; img[m, 3] = 1.0
img[admin_b, :3] = [0.45, 0.5, 0.55]                      # тонкие адм. границы
img[ctry_b, :3] = [0.09, 0.13, 0.18]                      # толстые госграницы

fig, ax_ = plt.subplots(figsize=(26, int(26*OY/OX)+1))
ax_.set_axis_off(); ax_.set_aspect("equal"); fig.patch.set_facecolor("white")
ax_.imshow(img, origin="lower", interpolation="nearest")
ax_.set_title("Бесшовная картограмма населения по ячейкам админ-центров\n"
              "площадь каждой ячейки ∝ её населению (диффузия Гастнера–Ньюмана); цвет — страна",
              color="#23303c", fontsize=19, pad=14)
plt.tight_layout()
fig.savefig("cartogram_admin_diffusion.png", dpi=170, facecolor="white", bbox_inches="tight", pad_inches=0.2)
fig.savefig("cartogram_admin_diffusion.svg", facecolor="white", bbox_inches="tight", pad_inches=0.2)
print("saved diffusion cartogram PNG + SVG")
