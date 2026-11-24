#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модель ПРИСВОЕНИЯ (конкурентный рост фронтов), а не тяготения.
Многоисточниковый Дейкстра по решётке СУШИ: фронт источника i растёт только из
СВОИХ занятых клеток со скоростью v_i ∝ √(город. население региона); сквозь чужое
занятое пройти нельзя (упёрся — обходит). => каждая ячейка СВЯЗНА, никто не поглощён.
Сравнение с равноскоростным ростом (обычная Вороного с остановкой у воды), scipy.
"""
import numpy as np, heapq, time
import geopandas as gpd, pandas as pd
from shapely.ops import unary_union
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from pyproj import Transformer
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import ListedColormap

NE="ne"; Re=6371.0; TGT="ESRI:54030"; BETA=2.0
fwd=Transformer.from_crs("EPSG:4326",TGT,always_xy=True)
def hav(lo1,la1,lo2,la2):
    p1,q1,p2,q2=map(np.radians,(lo1,la1,lo2,la2))
    h=np.sin((q2-q1)/2)**2+np.cos(q1)*np.cos(q2)*np.sin((p2-p1)/2)**2
    return 2*Re*np.arcsin(np.sqrt(np.clip(h,0,1)))

# ---------- сетка суши ----------
LON0,LON1,LAT0,LAT1,RES=-180.,180.,-56.,84.,0.3
nx=int(round((LON1-LON0)/RES)); ny=int(round((LAT1-LAT0)/RES))
tr=from_bounds(LON0,LAT0,LON1,LAT1,nx,ny)
countries=gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
mask=rasterize(((g,1) for g in countries.geometry if g is not None),
               out_shape=(ny,nx),transform=tr,fill=0,dtype="uint8").astype(bool)
lons=LON0+(np.arange(nx)+0.5)*RES
lats=LAT1-(np.arange(ny)+0.5)*RES
idgrid=np.full((ny,nx),-1,np.int64)
rr,cc=np.where(mask); N=rr.size; idgrid[rr,cc]=np.arange(N)
nlon=lons[cc]; nlat=lats[rr]
print("узлов суши:",N)

# ---------- рёбра 8-связности (векторно по смещениям) ----------
SRC=[];DST=[];W=[]
for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
    r2,c2=rr+dr,cc+dc
    ok=(r2>=0)&(r2<ny)&(c2>=0)&(c2<nx)
    r2,c2=r2[ok],c2[ok]; a=idgrid[rr[ok],cc[ok]]; b=idgrid[r2,c2]
    good=b>=0; a,b=a[good],b[good]
    L=hav(lons[cc[ok][good]],lats[rr[ok][good]],lons[c2[good]],lats[r2[good]])
    SRC.append(a);DST.append(b);W.append(L)
SRC=np.concatenate(SRC);DST=np.concatenate(DST);Wl=np.concatenate(W)
G=csr_matrix((Wl,(SRC,DST)),shape=(N,N))
indptr,indices,data=G.indptr,G.indices,G.data
print("рёбер:",Wl.size)

# ---------- админ-центры -> пиксели, веса/скорости ----------
adm=gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
adm=adm[adm.geometry.notna()&~adm.geometry.is_empty].reset_index(drop=True)
rp=adm.geometry.representative_point(); slon=rp.x.to_numpy(); slat=rp.y.to_numpy()
sc=adm["adm0_a3"].to_numpy().astype(object)
city=gpd.read_file(f"{NE}/ne_10m_populated_places.geojson")[["POP_MAX","geometry"]]
city["POP_MAX"]=city["POP_MAX"].fillna(0)
j=gpd.sjoin(city,adm[["geometry"]],predicate="within",how="inner")
wsum=j.groupby("index_right")["POP_MAX"].sum()
weight=np.full(len(adm),0.0); weight[wsum.index.values]=wsum.values
weight=np.clip(weight,20000.,None); vspeed=np.sqrt(weight)   # v_i ∝ √население

# каждый центр -> ближайший узел суши
col=np.clip(((slon-LON0)/RES).astype(int),0,nx-1)
row=np.clip(((LAT1-slat)/RES).astype(int),0,ny-1)
seed_node=idgrid[row,col].astype(np.int64)
from scipy.spatial import cKDTree
landtree=cKDTree(np.c_[nlon,nlat])
bad=np.where(seed_node<0)[0]              # центр попал на воду (часто субпиксельный остров)
if bad.size:
    dd,nn=landtree.query(np.c_[slon[bad],slat[bad]])
    snap=dd<0.6                           # ближе ~1–2 пикселей — снапим; дальше = остров, отбрасываем
    seed_node[bad[snap]]=nn[snap]; seed_node[bad[~snap]]=-1
valid=seed_node>=0
slon,slat,sc=slon[valid],slat[valid],sc[valid]
vspeed=vspeed[valid]; seed_node=seed_node[valid]
countries_list=sorted(set(adm["adm0_a3"])); cid={c:i for i,c in enumerate(countries_list)}
seed_country=np.array([cid[c] for c in sc])
print("центров после фильтра островов:",len(slon),"| отброшено:",int((~valid).sum()))

# ---------- РАВНОСКОРОСТНОЙ рост (scipy, быстро) ----------
t0=time.time()
uniq,first=np.unique(seed_node,return_index=True)
dist_u,_,srcnode_u=dijkstra(G,directed=False,indices=uniq,min_only=True,return_predecessors=True)
# srcnode_u: для каждого узла — индекс источника-узла; сопоставим админ-центру
node2seed={}
for s in range(len(seed_node)):
    node2seed.setdefault(seed_node[s],s)
adm_u=np.array([node2seed.get(int(sn),-1) for sn in srcnode_u])
cu=np.where(adm_u>=0,seed_country[np.clip(adm_u,0,None)],-1)
print("равноскоростной (scipy) готов за %.1f c"%(time.time()-t0))

# ---------- ВЗВЕШЕННЫЙ конкурентный рост (ручной Дейкстра с переносом источника) ----------
t0=time.time()
INF=1e18
best=np.full(N,INF); fin=np.zeros(N,bool); adm_w=np.full(N,-1,np.int32)
h=[]
collide=0
for s in range(len(seed_node)):
    p=int(seed_node[s])
    if best[p]==0.0: collide+=1; continue          # пиксель уже занят равным соседом
    best[p]=0.0; heapq.heappush(h,(0.0,p,s))
while h:
    t,u,su=heapq.heappop(h)
    if fin[u]: continue
    fin[u]=True; adm_w[u]=su; inv=1.0/vspeed[su]
    for k in range(indptr[u],indptr[u+1]):
        w=indices[k]
        if fin[w]: continue
        nt=t+data[k]*inv
        if nt<best[w]:
            best[w]=nt; heapq.heappush(h,(nt,int(w),su))
cw=np.where(adm_w>=0,seed_country[np.clip(adm_w,0,None)],-1)
print("взвешенный рост готов за %.1f c | слились на сетке: %d центров"%(time.time()-t0,collide))
print("поглощено (0 пикселей):",len(seed_node)-len(np.unique(adm_w[adm_w>=0])),"из",len(seed_node),
      "  (без учёта слипшихся на сетке)")

# ---------- площади ----------
parea=(Re**2)*np.cos(np.radians(nlat))*np.radians(RES)**2
aw=np.bincount(cw[cw>=0],weights=parea[cw>=0],minlength=len(countries_list))
au=np.bincount(cu[cu>=0],weights=parea[cu>=0],minlength=len(countries_list))
ru={countries.ADM0_A3.iloc[k]:countries.NAME_RU.iloc[k] for k in range(len(countries))}
nm=[ru.get(c,c) for c in countries_list]
tbl=pd.DataFrame({"страна":nm,"adm0":countries_list,
                  "равно_млн":au/1e6,"взвеш_млн":aw/1e6,"дельта_млн":(aw-au)/1e6}).round(3)
tbl.to_csv("growth_area_change.csv",index=False)
top=tbl.sort_values("дельта_млн",ascending=False)
print("\n=== БОЛЬШЕ ВСЕГО ПРИОБРЕЛИ при росте ∝√насел. (млн км²) ===")
for _,r in top.head(12).iterrows():
    print(f"  {r.страна:26s} {r.дельта_млн:+6.2f}  ({r.равно_млн:.2f}→{r.взвеш_млн:.2f})")
print("=== БОЛЬШЕ ВСЕГО ПОТЕРЯЛИ ===")
for _,r in top.tail(10).iloc[::-1].iterrows():
    print(f"  {r.страна:26s} {r.дельта_млн:+6.2f}  ({r.равно_млн:.2f}→{r.взвеш_млн:.2f})")
print("\nсменили владельца vs равноскоростной: %.1f%% суши"%(100*(cw!=cu).mean()))

# ---------- рендер ----------
def to_grid(v):
    g=np.full((ny,nx),-1,np.int32); g[rr,cc]=v; return g
Gw=to_grid(cw)
rng=np.random.default_rng(7); perm=rng.permutation(len(countries_list))
hues=(perm*0.61803398875)%1.0
pal=np.array([mc.hsv_to_rgb([hh,0.45,0.93]) for hh in hues]); cmap=ListedColormap(pal)
lon_e=np.linspace(LON0,LON1,nx+1); lat_e=np.linspace(LAT1,LAT0,ny+1)
LoE,LaE=np.meshgrid(lon_e,lat_e); Xe,Ye=fwd.transform(LoE,LaE)
coast=unary_union(list(countries.to_crs(TGT).geometry)).boundary
fig,ax=plt.subplots(figsize=(26,12.5)); ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")
ax.pcolormesh(Xe,Ye,np.ma.masked_less(Gw,0),cmap=cmap,vmin=0,vmax=len(countries_list)-1,shading="flat",antialiased=False,zorder=1)
gpd.GeoSeries([coast],crs=TGT).plot(ax=ax,color="#1d2733",linewidth=0.5,zorder=3)
rx,ry=fwd.transform(np.full(400,180.),np.linspace(-56,84,400)); lx,ly=fwd.transform(np.full(400,-180.),np.linspace(-56,84,400))
ax.plot(np.r_[rx,lx[::-1]],np.r_[ry,ly[::-1]],color="#c2cad1",lw=1.0,zorder=4)
ax.set_title("Границы по модели ПРИСВОЕНИЯ: рост фронтов со скоростью ∝√населения, упор в чужой фронт\n"
             "каждая ячейка связна, ни один город не поглощён (ср. с тяготением)",color="#23303c",fontsize=17,pad=12)
plt.tight_layout()
fig.savefig("voronoi_growth.png",dpi=170,facecolor="white",bbox_inches="tight",pad_inches=0.15)
fig.savefig("voronoi_growth.svg",facecolor="white",bbox_inches="tight",pad_inches=0.15)
print("saved growth map + CSV")
