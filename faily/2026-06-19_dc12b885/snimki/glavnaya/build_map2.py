#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Карта 'Кривой Победы' v2 — деление по административным единицам (Natural Earth
admin-1) для спорных стран; коридор СССР к Индийскому океану через С. Азию и Персию."""
import json
from shapely.geometry import shape
from pyproj import Transformer

ADM0 = json.load(open('ne.geojson'))['features']
ADM1 = json.load(open('adm1_split.geojson'))['features']

# ---- блоки (страны целиком, через admin-0) -----------------------------------
REICH = {'DEU','AUT','CZE','POL','SVN','LUX','EST','LVA','LTU','BLR','UKR','MDA',
         'GEO','ARM','AZE','ALD'}
GER_SPHERE = {'BEL','NLD','NOR','DNK','GBR','SVK','HUN','ROU','BGR','FIN',
              'HRV','BIH','SRB',
              'MAR','DZA','MRT','SAH','SEN','GMB','GNB','GIN','SLE','LBR','CIV','MLI',
              'BFA','GHA','TGO','BEN','NGA','NER','TCD','CMR','CAF','GNQ','GAB','COG',
              'COD','AGO','ZMB','ZWE','MWI','MOZ','TZA','KEN','UGA','RWA','BDI','NAM',
              'BWA','ZAF','LSO','SWZ','MDG','STP','CPV','COM','MUS','SYC'}
ITALY = {'ITA','SMR','VAT','MLT','CYP','CYN','LBY','EGY','TUN','SDN','SDS','ETH',
         'ERI','SOM','SOL','DJI','ALB','GRC','MKD','MNE','KOS'}
JAPAN = {'JPN','KOR','PRK','TWN','HKG','MAC','MMR','THA','KHM','LAO','VNM','MYS',
         'IDN','PHL','BRN','SGP','TLS','PLW','FSM','MHL'}
SOVIET = {'KAZ','UZB','TKM','KGZ','TJK','MNG','AFG'}
AMERICA = {'USA','CAN','MEX','GTM','BLZ','HND','SLV','NIC','CRI','PAN','COL','VEN',
           'ECU','PER','BRA','BOL','PRY','CHL','ARG','URY','GUY','SUR','CUB','DOM',
           'HTI','JAM','BHS','TTO','BRB','GRD','LCA','VCT','DMA','ATG','KNA','PRI',
           'VIR','VGB','CYM','TCA','AIA','MSR','BMU','GRL','ISL','ABW','CUW','SXM',
           'BLM','MAF','SPM','FLK','SGS'}
NEUTRAL = {'ESP','PRT','AND','CHE','LIE','SWE','IRL','TUR','MCO',
           'SAU','YEM','OMN','ARE','QAT','BHR','KWT','IRQ','SYR','JOR','LBN','ISR','PSX',
           'IND','PAK','BGD','NPL','BTN','LKA','MDV','KAS','IOA',
           'AUS','NZL','FJI','VUT','SLB','NCL','PNG','WSM','TON','KIR','TUV','NRU',
           'COK','NIU','PYF','PCN','GUM','MNP','ASM','WLF','IMN','JEY','GGY','FRO','SHN'}
EXCLUDE = {'ATA','ATC','ATF','HMD','IOT','BVT'}
SPLIT   = {'RUS','CHN','IRN','FRA'}           # рисуются по провинциям (admin-1)

BLOCS = [
 ('reich',   'Великогерманский Рейх',              '#39474f', REICH),
 ('gersph',  'Германская сфера и колонии',          '#8fa8a8', GER_SPHERE),
 ('italy',   'Итальянская империя (Mare Nostrum)',  '#8d9358', ITALY),
 ('japan',   'Японская сфера сопроцветания',        '#b3654d', JAPAN),
 ('soviet',  'Советский остаток',                   '#bf9646', SOVIET),
 ('america', 'Панамериканский союз',                '#56649f', AMERICA),
 ('neutral', 'Нейтральные · неприсоединившиеся',    '#c9c4b6', NEUTRAL),
]
COLOR = {k:c for k,_,c,_ in BLOCS}
CODE2BLOC = {c:k for k,_,_,codes in BLOCS for c in codes}

# ---- правила деления провинций (admin-1) -------------------------------------
def assign_rus(p):
    reg=p.get('region'); nm=p.get('name_en') or p.get('name') or ''
    if reg in ('Central','Northwestern','Volga'): return 'reich'
    if reg in ('Urals','Siberian'): return 'soviet'
    if reg=='Far Eastern': return 'soviet' if 'Sakha' in nm else 'japan'
    return 'soviet'

def assign_chn(p):
    reg=p.get('region'); nm=p.get('name_en') or p.get('name') or ''
    if reg in ('Northeast China','North China','East China','South Central China'): return 'japan'
    if nm in ('Fujian','Paracel Islands'): return 'japan'
    if reg=='Southwest China': return 'neutral'              # Свободный Китай + Тибет
    if reg=='Northwest China': return 'soviet' if nm=='Xinjiang' else 'neutral'
    return 'neutral'

SOVIET_IRAN = {'Gilan','Mazandaran','Golestan','Ardabil','East Azerbaijan',
 'West Azerbaijan','Zanjan','Qazvin','Semnan','North Khorasan','Razavi Khorasan',
 'South Khorasan','Sistan and Baluchestan'}
def assign_irn(p):
    nm=p.get('name_en') or p.get('name') or ''
    return 'soviet' if nm in SOVIET_IRAN else 'neutral'

ITALY_FR={'Alpes-Maritimes','Var','Bouches-du-Rhône','Vaucluse',
 'Alpes-de-Haute-Provence','Hautes-Alpes','Drôme','Isère','Savoie','Haute-Savoie',
 'Corse-du-Sud','Haute-Corse'}
AMER_FR={'French Guiana','Guadeloupe','Martinique'}
def assign_fra(p):
    nm=p.get('name_en') or p.get('name') or ''
    if nm in ITALY_FR: return 'italy'
    if nm in AMER_FR: return 'america'
    return 'gersph'

ASSIGN={'RUS':assign_rus,'CHN':assign_chn,'IRN':assign_irn,'FRA':assign_fra}

# ---- сбор геометрий ----------------------------------------------------------
bloc_geoms={k:[] for k,_,_,_ in BLOCS}
def add(bk, geom):
    if geom.is_empty: return
    if not geom.is_valid: geom=geom.buffer(0)
    bloc_geoms[bk].append(geom.simplify(0.05, preserve_topology=True))

for f in ADM0:
    code=f['properties'].get('ADM0_A3')
    if code in EXCLUDE or code in SPLIT: continue
    bk=CODE2BLOC.get(code,'neutral')
    add(bk, shape(f['geometry']))

for f in ADM1:
    code=f['properties'].get('adm0_a3')
    if code not in SPLIT: continue
    bk=ASSIGN[code](f['properties'])
    add(bk, shape(f['geometry']))

# ---- проекция и SVG ----------------------------------------------------------
T=Transformer.from_crs('EPSG:4326','+proj=robin +lon_0=0 +datum=WGS84',always_xy=True)
def project(lon,lat): return T.transform(lon,lat)
xs=[];ys=[]
for lat in range(-58,86,2):
    for lon in range(-180,181,5):
        x,y=project(lon,lat); xs.append(x); ys.append(y)
MINX,MAXX,MINY,MAXY=min(xs),max(xs),min(ys),max(ys)
W,H=1700,980; PADL,PADT,PADR,PADB=40,150,40,230
def to_svg(x,y):
    return PADL+(x-MINX)/(MAXX-MINX)*W, PADT+(MAXY-y)/(MAXY-MINY)*H
def ring(coords):
    pts=[f'{a:.1f},{b:.1f}' for a,b in (to_svg(*project(lo,la)) for lo,la in coords)]
    return 'M'+' L'.join(pts)+' Z' if pts else ''
def geom_d(g):
    out=[]
    polys=g.geoms if g.geom_type.startswith('Multi') else [g]
    for poly in polys:
        if poly.geom_type=='GeometryCollection':
            for q in poly.geoms:
                if q.geom_type=='Polygon':
                    out.append(ring(q.exterior.coords))
                    out+= [ring(r.coords) for r in q.interiors]
            continue
        if poly.geom_type!='Polygon' or poly.is_empty: continue
        out.append(ring(poly.exterior.coords))
        out+=[ring(r.coords) for r in poly.interiors]
    return ' '.join(x for x in out if x)
def grat():
    o=[]
    for lon in range(-180,181,30):
        o.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in (to_svg(*project(lon,la)) for la in range(-58,86,2))))
    for lat in range(-60,91,30):
        o.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in (to_svg(*project(lo,lat)) for lo in range(-180,181,3))))
    return o
def outline():
    pts=[]
    for la in range(-58,86,2): pts.append(to_svg(*project(180,la)))
    for lo in range(180,-181,-2): pts.append(to_svg(*project(lo,85)))
    for la in range(85,-59,-2): pts.append(to_svg(*project(-180,la)))
    for lo in range(-180,181,2): pts.append(to_svg(*project(lo,-58)))
    return 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+' Z'

TOTW,TOTH=PADL+W+PADR,PADT+H+PADB
oc=outline()
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTW} {TOTH}" font-family="Georgia, serif">']
S.append('<defs><style>.bd{stroke:#27343a;stroke-width:.3;stroke-opacity:.42;stroke-linejoin:round}'
         '.grat{fill:none;stroke:#b9c6cc;stroke-width:.6;stroke-opacity:.55}'
         '.lbl{fill:#16232a;font-weight:700;letter-spacing:.4px}.sub{font-style:italic}</style>'
         f'<clipPath id="w"><path d="{oc}"/></clipPath></defs>')
S.append(f'<rect width="{TOTW}" height="{TOTH}" fill="#f4f1ea"/>')
S.append(f'<path d="{oc}" fill="#dce7eb"/>')
S.append('<g class="grat" clip-path="url(#w)">'+''.join(f'<path d="{p}"/>' for p in grat())+'</g>')
for key,name,color,_ in BLOCS:
    if not bloc_geoms[key]: continue
    S.append(f'<g id="bloc-{key}" fill="{color}">'
             +''.join(f'<path class="bd" d="{geom_d(g)}"/>' for g in bloc_geoms[key] if geom_d(g))
             +'</g>')
S.append(f'<path d="{oc}" fill="none" stroke="#5b6f78" stroke-width="1.1"/>')

def lab(lon,lat,t,size=20,sub=None,anc='middle',col='#16232a'):
    x,y=to_svg(*project(lon,lat))
    s=f'<text class="lbl" x="{x:.0f}" y="{y:.0f}" text-anchor="{anc}" font-size="{size}" fill="{col}">{t}</text>'
    if sub: s+=f'<text class="sub" x="{x:.0f}" y="{y+size*0.92:.0f}" text-anchor="{anc}" font-size="{size*0.6:.0f}" fill="{col}">{sub}</text>'
    return s
S.append(lab(34,54,'РЕЙХ',25,'Großdeutsches Reich',col='#e9eef0'))
S.append(lab(92,60,'СОВЕТСКИЙ ОСТАТОК',17,col='#3a2c0f'))
S.append(lab(120,8,'ЯПОНСКАЯ СФЕРА',18,'Сопроцветание',col='#fbeee9'))
S.append(lab(18,21,'ITALIA',16,'Mare Nostrum',col='#2e2f12'))
S.append(lab(21,-4,'Германская',14,'Африка',col='#16242a'))
S.append(lab(-97,41,'ПАНАМЕРИКА',20,'Pan-American Union',col='#eef1f6'))
S.append(lab(-58,-18,'Южная',13,'Америка',col='#eef1f6'))
S.append(lab(99,32,'Свободный',12,'Китай',col='#4a4636'))
S.append(lab(80,21,'Свободная Индия',13,col='#4a4636'))
S.append(lab(46,25,'нейтр. Восток',10,col='#5a5642'))
# коридор СССР к Индийскому океану
ax,ay=to_svg(*project(60.5,26.5)); bx,by=to_svg(*project(62,22))
S.append(f'<path d="M{ax:.0f},{ay:.0f} L{bx:.0f},{by:.0f}" stroke="#7a5a14" stroke-width="2" '
         f'marker-end="url(#arr)"/>')
S.insert(2,'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7a5a14"/></marker></defs>')
S.append(lab(67,18,'выход к Индийскому океану',10.5,anc='start',col='#6a5012'))

cx=TOTW/2
S.append(f'<text x="{cx:.0f}" y="62" text-anchor="middle" font-size="40" font-weight="700" fill="#1d2a30" letter-spacing="1px">КРИВАЯ ПОБЕДА</text>')
S.append(f'<text x="{cx:.0f}" y="92" text-anchor="middle" font-size="18" font-style="italic" fill="#42525a">Раздел мира после Второй мировой войны · ок. 1948 года</text>')
S.append(f'<text x="{cx:.0f}" y="116" text-anchor="middle" font-size="12.5" fill="#6a7780">Границы блоков проведены по реальным административным единицам · ни одна держава не победила до конца</text>')

ly=PADT+H+40; lx=PADL+30; col_w=360
S.append(f'<text x="{lx}" y="{ly-14}" font-size="15" font-weight="700" fill="#1d2a30">Сферы влияния</text>')
for i,(key,name,color,_) in enumerate(BLOCS):
    bx=lx+(i//4)*col_w; by=ly+(i%4)*34
    S.append(f'<rect x="{bx}" y="{by-13}" width="22" height="16" fill="{color}" stroke="#27343a" stroke-width=".4"/>')
    S.append(f'<text x="{bx+30}" y="{by}" font-size="14.5" fill="#222">{name}</text>')
S.append(f'<text x="{TOTW-PADR-20}" y="{TOTH-22}" text-anchor="end" font-size="11" fill="#8a8f8a" font-style="italic">геометрия: Natural Earth admin-0 + admin-1 · проекция Робинсона · деление по областям, краям и останам</text>')
S.append('</svg>')
open('crooked_victory.svg','w',encoding='utf-8').write('\n'.join(S))
print('OK', len('\n'.join(S))//1024,'KB')
