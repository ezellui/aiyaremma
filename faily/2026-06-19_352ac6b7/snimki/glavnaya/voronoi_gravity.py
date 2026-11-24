#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мультипликативно взвешенная диаграмма Вороного (Аполлоний/Рейли) по админ-центрам.
Принадлежность пикселя: argmin_i  d_geo(p, center_i) / w_i,  w_i = (рег. город. население)^(1/beta).
Крупные центры «захватывают» больше территории. Переразмечаем админ-ячейки и страны.
Сравнение с невзвешенной (обычной) диаграммой: кто сколько территории выигрывает.
"""
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.path import Path

NE="ne"; Re=6371.0; TGT="ESRI:54030"; BETA=2.0
fwd=Transformer.from_crs("EPSG:4326",TGT,always_xy=True)
def llxyz(lo,la):
    lo,la=np.radians(lo),np.radians(la)
    return np.stack([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)],axis=-1)

# ---------- сетка суши ----------
LON0,LON1,LAT0,LAT1,RES=-180.,180.,-56.,84.,0.3
nx=int(round((LON1-LON0)/RES)); ny=int(round((LAT1-LAT0)/RES))
transform=from_bounds(LON0,LAT0,LON1,LAT1,nx,ny)
countries=gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
landmask=rasterize(((g,1) for g in countries.geometry if g is not None),
                   out_shape=(ny,nx),transform=transform,fill=0,dtype="uint8").astype(bool)
lons=LON0+(np.arange(nx)+0.5)*RES
lats=LAT1-(np.arange(ny)+0.5)*RES            # сверху вниз
LonG,LatG=np.meshgrid(lons,lats)
li,lj=np.where(landmask)
plon=LonG[li,lj]; plat=LatG[li,lj]
pix_xyz=llxyz(plon,plat).astype(np.float32)
print("пикселей суши:",pix_xyz.shape[0])

# ---------- админ-центры + вес = город. население региона ----------
adm=gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm=adm[adm.geometry.notna()&~adm.geometry.is_empty].reset_index(drop=True)
rp=adm.geometry.representative_point()
slon=rp.x.to_numpy(); slat=rp.y.to_numpy(); sc=adm["adm0_a3"].to_numpy().astype(object)
city=gpd.read_file(f"{NE}/ne_10m_populated_places.geojson")[["POP_MAX","geometry"]]
city["POP_MAX"]=city["POP_MAX"].fillna(0)
j=gpd.sjoin(city,adm[["geometry"]],predicate="within",how="inner")
wsum=j.groupby("index_right")["POP_MAX"].sum()
weight=np.full(len(adm),0.0); weight[wsum.index.values]=wsum.values
weight=np.clip(weight,20000.,None)                  # пол для бесгородных регионов
weff=(weight**(1.0/BETA)).astype(np.float32)
seed_xyz=llxyz(slon,slat).astype(np.float32)
# страны -> целочисленные id + цвета
countries_list=sorted(set(sc)); cid_of={c:i for i,c in enumerate(countries_list)}
seed_country=np.array([cid_of[c] for c in sc],dtype=np.int32)
print("центров:",len(slon),"| стран:",len(countries_list),
      "| вес: медиана",int(np.median(weight)),"макс",int(weight.max()))

# ---------- присвоение: взвеш. и невзвеш. (одним проходом) ----------
N=pix_xyz.shape[0]
best_w=np.full(N,1e9,np.float32);  idx_w=np.full(N,-1,np.int32)
best_u=np.full(N,1e9,np.float32);  idx_u=np.full(N,-1,np.int32)
for i in range(len(seed_xyz)):
    dot=pix_xyz@seed_xyz[i]; np.clip(dot,-1.,1.,out=dot)
    ang=np.arccos(dot)                              # геодезическое расстояние (в рад)
    sc_w=ang/weff[i]
    m=sc_w<best_w; best_w[m]=sc_w[m]; idx_w[m]=i
    m=ang<best_u; best_u[m]=ang[m]; idx_u[m]=i
cw=seed_country[idx_w]; cu=seed_country[idx_u]      # страна-победитель на пиксель
print("поглощено центров (0 пикселей во взвеш.):",
      len(slon)-len(np.unique(idx_w)),"из",len(slon))

# ---------- площади и таблица выигрыша ----------
pix_area=(Re**2)*np.cos(np.radians(plat))*np.radians(RES)**2   # км² на пиксель
aw=np.bincount(cw,weights=pix_area,minlength=len(countries_list))
au=np.bincount(cu,weights=pix_area,minlength=len(countries_list))
ru={countries.ADM0_A3.iloc[k]:countries.NAME_RU.iloc[k] for k in range(len(countries))}
name=[ru.get(c,c) for c in countries_list]
tbl=pd.DataFrame({"страна":name,"adm0":countries_list,
                  "невзвеш_млн_км2":au/1e6,"взвеш_млн_км2":aw/1e6})
tbl["дельта_млн_км2"]=tbl.взвеш_млн_км2-tbl.невзвеш_млн_км2
tbl["дельта_%"]=100*(aw-au)/np.where(au>0,au,np.nan)
tbl=tbl.round(3); tbl.to_csv("gravity_area_change.csv",index=False)
top=tbl.sort_values("дельта_млн_км2",ascending=False)
print("\n=== БОЛЬШЕ ВСЕГО ПРИОБРЕЛИ (млн км²) ===")
for _,r in top.head(12).iterrows():
    print(f"  {r.страна:28s} {r.дельта_млн_км2:+6.2f}  ({r.невзвеш_млн_км2:.2f}→{r.взвеш_млн_км2:.2f})")
print("=== БОЛЬШЕ ВСЕГО ПОТЕРЯЛИ ===")
for _,r in top.tail(12).iloc[::-1].iterrows():
    print(f"  {r.страна:28s} {r.дельта_млн_км2:+6.2f}  ({r.невзвеш_млн_км2:.2f}→{r.взвеш_млн_км2:.2f})")

# ---------- растры стран на полную сетку ----------
def to_grid(cvals):
    g=np.full((ny,nx),-1,np.int32); g[li,lj]=cvals; return g
G_w=to_grid(cw); G_u=to_grid(cu)

# цвета стран (золотое сечение по тону)
rng=np.random.default_rng(7); perm=rng.permutation(len(countries_list))
hues=(perm*0.61803398875)%1.0
import matplotlib.colors as mc
palette=np.array([mc.hsv_to_rgb([h,0.45,0.93]) for h in hues])
cmap=ListedColormap(palette)

# рамка/берег/проекция Робинсона через pcolormesh
lon_e=np.linspace(LON0,LON1,nx+1); lat_e=np.linspace(LAT1,LAT0,ny+1)
LoE,LaE=np.meshgrid(lon_e,lat_e)
Xe,Ye=fwd.transform(LoE,LaE)
coast=unary_union(list(countries.to_crs(TGT).geometry)).boundary

def draw(G,title,fname,highlight=None):
    fig,ax=plt.subplots(figsize=(26,12.5)); ax.set_axis_off(); ax.set_aspect("equal")
    fig.patch.set_facecolor("white")
    M=np.ma.masked_less(G,0)
    ax.pcolormesh(Xe,Ye,M,cmap=cmap,vmin=0,vmax=len(countries_list)-1,
                  shading="flat",antialiased=False,zorder=1)
    if highlight is not None:
        H=np.ma.masked_where(~highlight,np.ones_like(G))
        ax.pcolormesh(Xe,Ye,H,cmap=ListedColormap(["#c81e1e"]),shading="flat",zorder=2)
    gpd.GeoSeries([coast],crs=TGT).plot(ax=ax,color="#1d2733",linewidth=0.5,zorder=3)
    rx,ry=fwd.transform(np.full(400,180.),np.linspace(-56,84,400))
    lx,ly=fwd.transform(np.full(400,-180.),np.linspace(-56,84,400))
    ax.plot(np.r_[rx,lx[::-1]],np.r_[ry,ly[::-1]],color="#c2cad1",lw=1.0,zorder=4)
    ax.set_title(title,color="#23303c",fontsize=18,pad=12)
    plt.tight_layout()
    fig.savefig(fname+".png",dpi=170,facecolor="white",bbox_inches="tight",pad_inches=0.15)
    fig.savefig(fname+".svg",facecolor="white",bbox_inches="tight",pad_inches=0.15)
    plt.close(fig)

draw(G_w,"«Справедливые» границы по тяготению (Рейли, β=2): крупные центры захватывают больше\n"
         "ячейка = argmin расстояние/√(город. население региона); страны — объединения ячеек",
     "voronoi_gravity")
# карта изменений: где страна-владелец сменилась
changed=(G_w!=G_u)&(G_w>=0)
draw(G_u,"Те же территории при невзвешенной диаграмме (для сравнения)\n"
         "красным — пиксели, сменившие страну-владельца при переходе к тяготению",
     "voronoi_gravity_change",highlight=changed)
chg_km=pix_area[(cw!=cu)].sum()/1e6
print(f"\nсменили владельца: {100*(cw!=cu).mean():.1f}% суши  (~{chg_km:.1f} млн км²)")
print("saved maps + CSV")
