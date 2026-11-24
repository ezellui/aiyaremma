#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Коалесценция 0.1°: кэш симуляции (.npy), раскраска по ОБЪЕДИНЕНИЮ смежностей
# (реальная карта ∪ симуляция), тонкие серые внутренние границы (вектор).
import numpy as np, heapq, time, sys, json
from collections import defaultdict
import geopandas as gpd, pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window
from rasterio.transform import from_bounds
from scipy.sparse import csr_matrix
from shapely.ops import unary_union
from pyproj import Transformer
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection
def log(*a): print(*a); sys.stdout.flush()

NE="ne"; Re=6371.0; TGT="ESRI:54030"
fwd=Transformer.from_crs("EPSG:4326",TGT,always_xy=True)
def hav(lo1,la1,lo2,la2):
    p1,q1,p2,q2=map(np.radians,(lo1,la1,lo2,la2))
    h=np.sin((q2-q1)/2)**2+np.cos(q1)*np.cos(q2)*np.sin((p2-p1)/2)**2
    return 2*Re*np.arcsin(np.sqrt(np.clip(h,0,1)))
T0=time.time()
LON0,LON1,LAT0,LAT1,RES=-180.,180.,-56.,84.,0.1
nx=int(round((LON1-LON0)/RES)); ny=int(round((LAT1-LAT0)/RES))
tr=from_bounds(LON0,LAT0,LON1,LAT1,nx,ny)
countries=gpd.read_file(f"{NE}/ne_50m_admin_0_countries.geojson")
mask=rasterize(((g,1) for g in countries.geometry if g is not None),out_shape=(ny,nx),
               transform=tr,fill=0,dtype="uint8").astype(bool)
lons=LON0+(np.arange(nx)+0.5)*RES; lats=LAT1-(np.arange(ny)+0.5)*RES
idgrid=np.full((ny,nx),-1,np.int64); rr,cc=np.where(mask); N=rr.size; idgrid[rr,cc]=np.arange(N)
log("сетка: %d узлов суши"%N)

# ---------- кэш симуляции ----------
lab=seedlab=None; countries_list=None
try:
    L=np.load("coal_lab_01.npy"); S=np.load("coal_seed_01.npy"); CL=json.load(open("coal_clist.json"))
    if len(L)==N and len(S)==N:
        lab,seedlab,countries_list=L,S,CL; log("КЭШ загружен — симуляция пропущена")
except Exception as e:
    log("кэша нет (%s) — считаю симуляцию"%e)

if lab is None:
    nlon=lons[cc]; nlat=lats[rr]
    SRC=[];DST=[];WL=[]
    for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
        r2,c2=rr+dr,cc+dc; ok=(r2>=0)&(r2<ny)&(c2>=0)&(c2<nx)
        r2,c2=r2[ok],c2[ok]; a=idgrid[rr[ok],cc[ok]]; b=idgrid[r2,c2]; good=b>=0
        a,b=a[good],b[good]; Lw=hav(lons[cc[ok][good]],lats[rr[ok][good]],lons[c2[good]],lats[r2[good]])
        SRC.append(a);DST.append(b);WL.append(Lw)
    G=csr_matrix((np.concatenate(WL),(np.concatenate(SRC),np.concatenate(DST))),shape=(N,N))
    indptr=G.indptr.astype(np.int64); indices=G.indices.astype(np.int64); data=G.data
    log("граф готов, t=%.0fс"%(time.time()-T0))
    adm=gpd.read_file(f"{NE}/ne_10m_admin_1_states_provinces.geojson")
    adm=adm[adm.geometry.notna()&~adm.geometry.is_empty].reset_index(drop=True)
    rp=adm.geometry.representative_point(); slon=rp.x.to_numpy(); slat=rp.y.to_numpy()
    sc=adm["adm0_a3"].to_numpy().astype(object)
    src=rasterio.open("ghs/GHS_POP_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif")
    Hh,Ww=src.height,src.width; top=src.bounds.top; pixh=(src.bounds.top-src.bounds.bottom)/Hh
    geoms=list(adm.geometry.buffer(0).values); Nadm=len(adm)
    miny=adm.bounds["miny"].to_numpy(); maxy=adm.bounds["maxy"].to_numpy(); popacc=np.zeros(Nadm+1)
    for r0 in range(0,Hh,1024):
        rows=min(1024,Hh-r0); win=Window(0,r0,Ww,rows)
        pop=src.read(1,window=win,out_dtype="float32"); np.nan_to_num(pop,copy=False); pop[pop<0]=0
        sel=np.where((maxy>=top-(r0+rows)*pixh)&(miny<=top-r0*pixh))[0]
        if sel.size==0: continue
        ids=rasterize([(geoms[i],int(i+1)) for i in sel],out_shape=(rows,Ww),
                      transform=src.window_transform(win),fill=0,dtype="int32")
        popacc+=np.bincount(ids.ravel(),weights=pop.ravel().astype("float64"),minlength=Nadm+1)
    region_pop=np.clip(popacc[1:Nadm+1],1000.,None)
    log("зональное население готово, t=%.0fс"%(time.time()-T0))
    from scipy.spatial import cKDTree
    col=np.clip(((slon-LON0)/RES).astype(int),0,nx-1); row=np.clip(((LAT1-slat)/RES).astype(int),0,ny-1)
    seed_node=idgrid[row,col].astype(np.int64)
    landtree=cKDTree(np.c_[nlon,nlat]); bad=np.where(seed_node<0)[0]
    if bad.size:
        dd,nn=landtree.query(np.c_[slon[bad],slat[bad]]); snap=dd<0.5
        seed_node[bad[snap]]=nn[snap]; seed_node[bad[~snap]]=-1
    valid=seed_node>=0; sc=sc[valid]; region_pop=region_pop[valid]; seed_node=seed_node[valid]
    countries_list=sorted(set(adm["adm0_a3"])); cidx0={c:i for i,c in enumerate(countries_list)}
    seed_country=np.array([cidx0[c] for c in sc])
    pix_pop={}; pix_ctry={}
    for p,P,c in zip(seed_node,region_pop,seed_country):
        p=int(p)
        if p in pix_pop: pix_pop[p]+=P
        else: pix_pop[p]=P; pix_ctry[p]=c
    parent=np.arange(N); cpop=np.zeros(N); cctry=np.full(N,-1,np.int32); cver=np.zeros(N,np.int64); cpix={}
    def find(a):
        while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
        return a
    owner=np.full(N,-1,np.int64); ctime=np.zeros(N); seedl=np.full(N,-1,np.int64)
    SP=lambda r: np.sqrt(cpop[r]); h=[]
    for p,P in pix_pop.items():
        cpop[p]=P; cctry[p]=pix_ctry[p]; owner[p]=p; ctime[p]=0.0; cpix[p]=[p]; seedl[p]=p
        sp=np.sqrt(P)
        for k in range(indptr[p],indptr[p+1]): heapq.heappush(h,(data[k]/sp,int(indices[k]),p,p,0))
    def union(a,b):
        ra,rb=find(a),find(b)
        if ra==rb: return ra
        if len(cpix[ra])<len(cpix[rb]): ra,rb=rb,ra
        parent[rb]=ra; cpop[ra]+=cpop[rb]; cver[ra]+=1
        small=cpix.pop(rb); cpix[ra].extend(small); sp=SP(ra)
        for q in small:
            tq=ctime[q]
            for k in range(indptr[q],indptr[q+1]):
                v=indices[k]
                if owner[v]==-1: heapq.heappush(h,(tq+data[k]/sp,int(v),q,ra,cver[ra]))
        return ra
    log("СТАРТ симуляции..."); t0=time.time(); claimed=0; nextlog=300000
    while h:
        t,y,x,rt,ver=heapq.heappop(h)
        if owner[y]!=-1: continue
        best=1e18; broot=-1; bseed=-1
        for k in range(indptr[y],indptr[y+1]):
            nb=indices[k]
            if owner[nb]!=-1:
                r=find(nb); tt=ctime[nb]+data[k]/SP(r)
                if tt<best: best=tt; broot=r; bseed=seedl[nb]
        if broot<0: continue
        if best<t-1e-9: heapq.heappush(h,(best,y,x,broot,0)); continue
        rx=broot; owner[y]=rx; parent[y]=rx; ctime[y]=best; seedl[y]=bseed; claimed+=1; cpix[broot].append(y)
        for k in range(indptr[y],indptr[y+1]):
            v=indices[k]
            if owner[v]==-1: heapq.heappush(h,(best+data[k]/SP(rx),int(v),y,rx,0))
            else:
                rv=find(v)
                if rv!=find(rx) and cctry[rv]==cctry[find(rx)]: rx=union(rx,v)
        if claimed>=nextlog: log("  %d%%"%(100*claimed//N)); nextlog+=300000
    lab=np.array([cctry[find(o)] if o>=0 else -1 for o in owner])
    seedlab=seedl
    np.save("coal_lab_01.npy",lab); np.save("coal_seed_01.npy",seedlab)
    json.dump(countries_list,open("coal_clist.json","w"))
    log("СИМУЛЯЦИЯ ГОТОВА и сохранена, t=%.0fс"%(time.time()-T0))

cidx={c:i for i,c in enumerate(countries_list)}
def to_grid(v,fill=-1): g=np.full((ny,nx),fill,np.int64); g[rr,cc]=v; return g
LGc=to_grid(lab); LGs=to_grid(seedlab)

# ---------- смежности: реальная карта и симуляция (рук + диагонали) ----------
def pairset(LG):
    def pp(a,b):
        m=(a>=0)&(b>=0)&(a!=b); pa=a[m].astype(np.int64); pb=b[m].astype(np.int64)
        return np.minimum(pa,pb)*1000+np.maximum(pa,pb)
    return np.unique(np.concatenate([pp(LG[:,:-1],LG[:,1:]),pp(LG[:-1,:],LG[1:,:]),
                                     pp(LG[:-1,:-1],LG[1:,1:]),pp(LG[:-1,1:],LG[1:,:-1])]))
# реальная карта стран на той же сетке
shapes=[(g,cidx[a]+1) for g,a in zip(countries.geometry,countries.ADM0_A3) if (g is not None and a in cidx)]
RG=rasterize(shapes,out_shape=(ny,nx),transform=tr,fill=0,dtype=np.int32).astype(np.int64)-1
sim_keys=pairset(LGc); real_keys=pairset(RG)
present=set(int(x) for x in np.unique(lab) if x>=0)
def build_adj(keys):
    a=defaultdict(set)
    for kk in keys:
        u,v=int(kk//1000),int(kk%1000)
        if u in present and v in present: a[u].add(v); a[v].add(u)
    return a
sim_adj=build_adj(sim_keys); real_adj=build_adj(real_keys)
uni_adj=build_adj(np.unique(np.concatenate([sim_keys,real_keys])))
def dsatur(adj):
    nodes=sorted(present); deg={n:len(adj.get(n,())) for n in nodes}
    sat={n:set() for n in nodes}; col={}; un=set(nodes)
    while un:
        n=max(un,key=lambda v:(len(sat[v]),deg[v]))
        used={col[w] for w in adj.get(n,()) if w in col}; c=0
        while c in used: c+=1
        col[n]=c
        for w in adj.get(n,()):
            if w not in col: sat[w].add(c)
        un.discard(n)
    return col
col_real=dsatur(real_adj)
viol=sum(1 for kk in sim_keys for u,v in [(int(kk//1000),int(kk%1000))]
         if u in present and v in present and col_real.get(u)==col_real.get(v))
col_uni=dsatur(uni_adj)
log("«только реальная» раскраска: цветов=%d, НАРУШЕНИЙ на симуляции=%d из %d смежностей"
    %(max(col_real.values())+1, viol, len(sim_adj and sim_keys)))
log("раскраска по ОБЪЕДИНЕНИЮ: цветов=%d (нарушений 0 по построению)"%(max(col_uni.values())+1))
ncol=max(col_uni.values())+1
PAL=['#e6332a','#2456c7','#36a93b','#f4c20d','#8e44ad','#ff8c1a','#17a2a2','#e84393',
     '#7f8c2a','#00897b','#5d4037','#546e7a','#c2185b','#fbc02d']
while len(PAL)<ncol: PAL.append('#888888')
cmapN=max(ncol,8)
cidmap=np.zeros(len(countries_list),np.int64)
for n,c in col_uni.items(): cidmap[n]=c
colidx=to_grid(np.where(lab>=0,cidmap[np.clip(lab,0,len(cidmap)-1)],-1))

# ---------- границы как векторные сегменты ----------
def segs_h(maskh):                 # граница между столбцами i,i+1
    rs,ix=np.where(maskh); lon_b=LON0+(ix+1)*RES
    la0=LAT1-rs*RES; la1=LAT1-(rs+1)*RES
    x0,y0=fwd.transform(lon_b,la0); x1,y1=fwd.transform(lon_b,la1)
    return np.stack([np.c_[x0,y0],np.c_[x1,y1]],axis=1)
def segs_v(maskv):                 # граница между строками r,r+1
    rs,ix=np.where(maskv); lat_b=LAT1-(rs+1)*RES
    lo0=LON0+ix*RES; lo1=LON0+(ix+1)*RES
    x0,y0=fwd.transform(lo0,lat_b); x1,y1=fwd.transform(lo1,lat_b)
    return np.stack([np.c_[x0,y0],np.c_[x1,y1]],axis=1)
chh=(LGc[:,:-1]!=LGc[:,1:])&(LGc[:,:-1]>=0)&(LGc[:,1:]>=0)
cvv=(LGc[:-1,:]!=LGc[1:,:])&(LGc[:-1,:]>=0)&(LGc[1:,:]>=0)
shh=(LGs[:,:-1]!=LGs[:,1:])&(LGc[:,:-1]>=0)&(LGc[:,1:]>=0)&~chh
svv=(LGs[:-1,:]!=LGs[1:,:])&(LGc[:-1,:]>=0)&(LGc[1:,:]>=0)&~cvv
nat_segs=np.concatenate([segs_h(chh),segs_v(cvv)],axis=0)
int_segs=np.concatenate([segs_h(shh),segs_v(svv)],axis=0)
log("сегментов: нац=%d, внутр=%d"%(len(nat_segs),len(int_segs)))

# ---------- рендер ----------
lon_e=np.linspace(LON0,LON1,nx+1); lat_e=np.linspace(LAT1,LAT0,ny+1); Xe,Ye=fwd.transform(*np.meshgrid(lon_e,lat_e))
coast=unary_union(list(countries.to_crs(TGT).geometry)).boundary
fig,ax=plt.subplots(figsize=(32,15.5)); ax.set_axis_off(); ax.set_aspect("equal"); fig.patch.set_facecolor("white")
ax.pcolormesh(Xe,Ye,np.ma.masked_less(colidx,0),cmap=ListedColormap(PAL[:cmapN]),vmin=0,vmax=cmapN-1,
              shading="flat",antialiased=False,rasterized=True,zorder=1)
ax.add_collection(LineCollection(int_segs,colors="#7d7d7d",linewidths=0.18,alpha=0.75,zorder=2,rasterized=True))
ax.add_collection(LineCollection(nat_segs,colors="#0c1116",linewidths=0.5,zorder=3,rasterized=True))
gpd.GeoSeries([coast],crs=TGT).plot(ax=ax,color="#0c1116",linewidth=0.4,zorder=4)
rx2,ry2=fwd.transform(np.full(400,180.),np.linspace(-56,84,400)); lx2,ly2=fwd.transform(np.full(400,-180.),np.linspace(-56,84,400))
ax.plot(np.r_[rx2,lx2[::-1]],np.r_[ry2,ly2[::-1]],color="#c2cad1",lw=1.0,zorder=5)
ax.autoscale_view()
ax.set_title("Коалесцентная модель 0.1°: цвета по объединению (реальная карта ∪ симуляция), %d красок;\n"
             "национальные границы — тёмные, внутренние — тонкие серые"%ncol,color="#23303c",fontsize=20,pad=14)
plt.tight_layout()
fig.savefig("voronoi_coalesce_atlas.png",dpi=200,facecolor="white",bbox_inches="tight",pad_inches=0.15)
fig.savefig("voronoi_coalesce_atlas.svg",facecolor="white",bbox_inches="tight",pad_inches=0.15); plt.close(fig)
log("ГОТОВО, t=%.0fс"%(time.time()-T0))
