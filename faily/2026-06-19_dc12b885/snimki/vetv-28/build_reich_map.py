#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Справочная карта европейского Рейха: города с немецким + 'истинным' (квенья) именем.
Заготовка для gpt-image (геометрия + позиции + читаемые подписи)."""
import ijson
from shapely.geometry import shape
from shapely import unary_union
from shapely.validation import make_valid
from pyproj import Transformer

# ---- блоки (из build_map3) ----
REICH={'DEU','AUT','CZE','POL','SVN','LUX','EST','LVA','LTU','BLR','UKR','MDA','GEO','ARM','AZE','ALD'}
GER_SPHERE={'BEL','NLD','NOR','DNK','GBR','SVK','HUN','ROU','BGR','FIN','HRV','BIH','SRB',
 'MAR','DZA','MRT','SAH','SEN','GMB','GNB','GIN','SLE','LBR','CIV','MLI','BFA','GHA','TGO',
 'BEN','NGA','NER','TCD','CMR','CAF','GNQ','GAB','COG','COD','AGO','ZMB','ZWE','MWI','MOZ',
 'TZA','KEN','UGA','RWA','BDI','NAM','BWA','ZAF','LSO','SWZ','MDG','STP','CPV','COM','MUS','SYC'}
ITALY={'ITA','SMR','VAT','MLT','CYP','CYN','LBY','EGY','TUN','SDN','SDS','ETH','ERI','SOM',
 'SOL','DJI','ALB','GRC','MKD','MNE','KOS'}
JAPAN={'JPN','KOR','PRK','TWN','HKG','MAC','MMR','THA','KHM','LAO','VNM','MYS','IDN','PHL',
 'BRN','SGP','TLS','PLW','FSM','MHL'}
SOVIET={'KAZ','UZB','TKM','KGZ','TJK','MNG','AFG'}
AMERICA={'USA','CAN','MEX','GTM','BLZ','HND','SLV','NIC','CRI','PAN','COL','VEN','ECU','PER',
 'BRA','BOL','PRY','CHL','ARG','URY','GUY','SUR','CUB','DOM','HTI','JAM','BHS','TTO','BRB',
 'GRD','LCA','VCT','DMA','ATG','KNA','PRI','VIR','VGB','CYM','TCA','AIA','MSR','BMU','GRL',
 'ISL','ABW','CUW','SXM','BLM','MAF','SPM','FLK','SGS'}
NEUTRAL={'ESP','PRT','AND','CHE','LIE','SWE','IRL','TUR','MCO','SAU','YEM','OMN','ARE','QAT',
 'BHR','KWT','IRQ','SYR','JOR','LBN','ISR','PSX','IND','PAK','BGD','NPL','BTN','LKA','MDV',
 'KAS','IOA','AUS','NZL','FJI','VUT','SLB','NCL','PNG','WSM','TON','KIR','TUV','NRU','COK',
 'NIU','PYF','PCN','GUM','MNP','ASM','WLF','IMN','JEY','GGY','FRO','SHN'}
EXCLUDE={'ATA','ATC','ATF','HMD','IOT','BVT'}
ALLBLOC={}
for s,k in [(REICH,'reich'),(GER_SPHERE,'gersph'),(ITALY,'italy'),(JAPAN,'japan'),
            (SOVIET,'soviet'),(AMERICA,'america'),(NEUTRAL,'neutral')]:
    for c in s: ALLBLOC[c]=k

def a_rus(p):
    reg=p.get('region'); nm=p.get('name_en') or p.get('name') or ''
    if reg in ('Central','Northwestern','Volga'): return 'reich'
    if reg in ('Urals','Siberian'): return 'soviet'
    if reg=='Far Eastern': return 'soviet' if nm=='Sakha Republic' else 'japan'
    return 'soviet'
ITA_FR={'Alpes-Maritimes','Var','Bouches-du-Rhône','Vaucluse','Alpes-de-Haute-Provence',
 'Hautes-Alpes','Drôme','Isère','Savoie','Haute-Savoie','Corse-du-Sud','Haute-Corse'}
AME_FR={'French Guiana','Guadeloupe','Martinique'}
def a_fra(p):
    nm=p.get('name_en') or p.get('name') or ''
    if nm in ITA_FR: return 'italy'
    if nm in AME_FR: return 'america'
    return 'gersph'
SPLIT={'RUS':a_rus,'FRA':a_fra}

def to_float(x):
    return [to_float(i) for i in x] if isinstance(x,list) else float(x)

reich_geoms=[]; land_geoms=[]
with open('adm1_10m.geojson','rb') as fh:
    for feat in ijson.items(fh,'features.item'):
        p=feat['properties']; code=p.get('adm0_a3')
        if code in EXCLUDE: continue
        bk= SPLIT[code](p) if code in SPLIT else ALLBLOC.get(code,'neutral')
        g=feat['geometry']
        geom=shape({'type':g['type'],'coordinates':to_float(g['coordinates'])})
        if not geom.is_valid: geom=make_valid(geom).buffer(0)
        if geom.is_empty: continue
        if geom.bounds[2] < -150: continue
        # окно Европы (+поля) — отбрасываем далёкое, чтобы слияние было лёгким
        minx,miny,maxx,maxy=geom.bounds
        if maxx< -25 or minx>55 or maxy<33 or miny>72: continue
        land_geoms.append(geom)
        if bk=='reich': reich_geoms.append(geom)
print('geoms:', len(land_geoms),'reich:',len(reich_geoms))
land=unary_union(land_geoms).buffer(0).simplify(0.03,preserve_topology=True)
reich=unary_union(reich_geoms).buffer(0).simplify(0.03,preserve_topology=True)

# ---- проекция: LAEA по центру Европы ----
T=Transformer.from_crs('EPSG:4326','+proj=laea +lon_0=14 +lat_0=51 +datum=WGS84',always_xy=True)
def project(lon,lat): return T.transform(lon,lat)

LON0,LON1,LAT0,LAT1=-5,33,44,58
xs=[];ys=[]
for la in [LAT0,(LAT0+LAT1)/2,LAT1]:
    for lo in range(LON0,LON1+1,2):
        x,y=project(lo,la); xs.append(x); ys.append(y)
for lo in [LON0,(LON0+LON1)/2,LON1]:
    for la in range(LAT0,LAT1+1,2):
        x,y=project(lo,la); xs.append(x); ys.append(y)
MINX,MAXX,MINY,MAXY=min(xs),max(xs),min(ys),max(ys)

Wm=1500
Hm=Wm*(MAXY-MINY)/(MAXX-MINX)
PADL,PADR,PADT,PADB=46,46,118,150
def to_svg(x,y): return PADL+(x-MINX)/(MAXX-MINX)*Wm, PADT+(MAXY-y)/(MAXY-MINY)*Hm
def ring(coords):
    pts=[f'{a:.1f},{b:.1f}' for a,b in (to_svg(*project(lo,la)) for lo,la in coords)]
    return 'M'+' L'.join(pts)+' Z' if pts else ''
def geom_d(g):
    out=[]
    polys=g.geoms if g.geom_type.startswith('Multi') else [g]
    for poly in polys:
        if poly.geom_type!='Polygon' or poly.is_empty: continue
        out.append(ring(poly.exterior.coords)); out+=[ring(r.coords) for r in poly.interiors]
    return ' '.join(x for x in out if x)

TOTW,TOTH=PADL+Wm+PADR,PADT+Hm+PADB
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTW:.0f} {TOTH:.0f}" '
   f'font-family="\'Iowan Old Style\',\'Palatino Linotype\',\'Book Antiqua\',Georgia,serif">']
S.append(f'<rect width="{TOTW:.0f}" height="{TOTH:.0f}" fill="#efe9db"/>')
# рамка карты
S.append(f'<rect x="{PADL-10}" y="{PADT-10}" width="{Wm+20:.0f}" height="{Hm+20:.0f}" '
         f'fill="#e3edf0" stroke="#2c3a40" stroke-width="1.4"/>')
S.append(f'<clipPath id="m"><rect x="{PADL-10}" y="{PADT-10}" width="{Wm+20:.0f}" height="{Hm+20:.0f}"/></clipPath>')
S.append(f'<g clip-path="url(#m)">')
# градусная сетка
grat=[]
for lo in range(LON0,LON1+1,5):
    grat.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in (to_svg(*project(lo,la)) for la in range(LAT0,LAT1+1,1))))
for la in range(LAT0,LAT1+1,5):
    grat.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in (to_svg(*project(lo,la)) for lo in range(LON0,LON1+1,1))))
S.append('<g fill="none" stroke="#9fb0b6" stroke-width=".5" stroke-opacity=".5">'
         +''.join(f'<path d="{p}"/>' for p in grat)+'</g>')
# суша: не-Рейх пале, Рейх — выделен
S.append(f'<path d="{geom_d(land)}" fill="#dcd5c5" stroke="#7d8a86" stroke-width=".5" stroke-linejoin="round"/>')
S.append(f'<path d="{geom_d(reich)}" fill="#aebfbf" stroke="#3a4a50" stroke-width=".9" stroke-linejoin="round"/>')
S.append('</g>')

# ---- города: (lon,lat, нем., квенья, anchor, dx, dy) ----
CITIES=[
 (13.40,52.52,'Berlin','Elenmar','R',12,-2,True),
 (9.99,53.55,'Hamburg','Eärosto','R',12,-2,False),
 (9.73,52.37,'Hannover','Tarambar','L',-12,2,False),
 (6.96,50.94,'Köln','Síramar','L',-12,0,False),
 (8.68,50.11,'Frankfurt','Maltambar','L',-12,2,False),
 (9.18,48.78,'Stuttgart','Roccombar','L',-12,2,False),
 (11.58,48.14,'München','Oromar','R',12,4,False),
 (11.08,49.45,'Nürnberg','Ondomar','L',-12,0,False),
 (12.37,51.34,'Leipzig','Aldëamar','L',-12,-2,False),
 (13.74,51.05,'Dresden','Silmamar','R',12,4,False),
 (17.04,51.11,'Breslau','Taurmar','R',12,2,False),
 (14.42,50.09,'Prag','Mindomar','R',12,6,False),
 (16.37,48.21,'Wien','Lindemar','R',12,2,False),
 (20.51,54.71,'Königsberg','Aranorto','R',12,2,False),
]
def dot(lon,lat,cap=False):
    x,y=to_svg(*project(lon,lat))
    if cap:
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="none" stroke="#1f2c32" stroke-width="1.6"/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#1f2c32"/>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="#1f2c32"/>'
for lon,lat,de,qu,anc,dx,dy,cap in CITIES:
    x,y=to_svg(*project(lon,lat))
    S.append(dot(lon,lat,cap))
    ta='end' if anc=='L' else 'start'
    tx=x+dx
    S.append(f'<text x="{tx:.1f}" y="{y+dy-3:.1f}" text-anchor="{ta}" font-size="17" '
             f'font-weight="600" fill="#16222a">{de}</text>')
    S.append(f'<text x="{tx:.1f}" y="{y+dy+14:.1f}" text-anchor="{ta}" font-size="14" '
             f'font-style="italic" fill="#4a5560">{qu}</text>')

# ---- заголовок ----
cx=TOTW/2
S.append(f'<text x="{cx:.0f}" y="52" text-anchor="middle" font-size="30" letter-spacing="1.5" '
         f'fill="#1d2a30">Das Großdeutsche Reich · Europäisches Kernland</text>')
S.append(f'<text x="{cx:.0f}" y="80" text-anchor="middle" font-size="16" font-style="italic" '
         f'fill="#54616a">Städte mit deutschem und wahrem (eldarischem) Namen</text>')

# ---- масштабная линейка (200 км) ----
m_per_px=(MAXX-MINX)/Wm
barkm=200; barpx=barkm*1000/m_per_px
bx0=PADL+30; by0=PADT+Hm+46
S.append(f'<line x1="{bx0:.1f}" y1="{by0:.1f}" x2="{bx0+barpx:.1f}" y2="{by0:.1f}" stroke="#1d2a30" stroke-width="2"/>')
for i in range(3):
    xx=bx0+barpx*i/2
    S.append(f'<line x1="{xx:.1f}" y1="{by0-5:.1f}" x2="{xx:.1f}" y2="{by0+5:.1f}" stroke="#1d2a30" stroke-width="1.4"/>')
S.append(f'<text x="{bx0:.1f}" y="{by0+22:.1f}" font-size="13" fill="#1d2a30">0</text>')
S.append(f'<text x="{bx0+barpx:.1f}" y="{by0+22:.1f}" font-size="13" text-anchor="end" fill="#1d2a30">200 km · Maßstab</text>')

# ---- компас как восьмиконечная звезда ----
cxs,cys=TOTW-110,PADT+Hm+60; R=30; r=11
import math
pts=[]
for i in range(16):
    ang=math.pi/2 - i*math.pi/8
    rad=R if i%2==0 else r
    pts.append(f'{cxs+rad*math.cos(ang):.1f},{cys-rad*math.sin(ang):.1f}')
S.append(f'<polygon points="{" ".join(pts)}" fill="#e3edf0" stroke="#1d2a30" stroke-width="1.3"/>')
S.append(f'<text x="{cxs:.1f}" y="{cys-R-6:.1f}" text-anchor="middle" font-size="13" fill="#1d2a30">N</text>')

S.append('</svg>')
open('reich_cities_map.svg','w').write('\n'.join(S))
print('written reich_cities_map.svg  size', f'{TOTW:.0f}x{TOTH:.0f}')
