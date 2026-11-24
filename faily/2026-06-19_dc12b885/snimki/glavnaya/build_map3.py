#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'Der krumme Sieg' v3 — весь мир по admin-1, блоки слиты (без внутренних границ),
весь текст немецкий, коридор СССР к Индийскому океану."""
import ijson, json
from shapely.geometry import shape
from shapely import unary_union
from shapely.validation import make_valid
from pyproj import Transformer

# ---- блоки: страны целиком (значение по умолчанию для admin-1 единицы) --------
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

BLOCS=[
 ('reich',  'Großdeutsches Reich',                '#39474f', REICH),
 ('gersph', 'Deutsche Sphäre und Kolonien',        '#8fa8a8', GER_SPHERE),
 ('italy',  'Italienisches Imperium (Mare Nostrum)','#8d9358', ITALY),
 ('japan',  'Japanische Wohlstandssphäre',         '#b3654d', JAPAN),
 ('soviet', 'Sowjetunion',                          '#bf9646', SOVIET),
 ('america','Panamerikanische Union',              '#56649f', AMERICA),
 ('neutral','Neutrale und Blockfreie',             '#c9c4b6', NEUTRAL),
]
COLOR={k:c for k,_,c,_ in BLOCS}
CODE2BLOC={c:k for k,_,_,codes in BLOCS for c in codes}

# ---- правила деления спорных стран по admin-1 --------------------------------
def a_rus(p):
    reg=p.get('region'); nm=p.get('name_en') or p.get('name') or ''
    if reg in ('Central','Northwestern','Volga'): return 'reich'
    if reg in ('Urals','Siberian'): return 'soviet'
    if reg=='Far Eastern': return 'soviet' if nm=='Sakha Republic' else 'japan'
    return 'soviet'
def a_chn(p):
    reg=p.get('region'); nm=p.get('name_en') or p.get('name') or ''
    if reg in ('Northeast China','North China','East China','South Central China'): return 'japan'
    if nm in ('Fujian','Paracel Islands'): return 'japan'
    if reg=='Northwest China': return 'soviet' if nm=='Xinjiang' else 'neutral'
    return 'neutral'                               # Southwest = Freies China + Tibet
SOV_IRN={'Gilan','Mazandaran','Golestan','Ardabil','East Azerbaijan','West Azerbaijan',
 'Zanjan','Qazvin','Semnan','North Khorasan','Razavi Khorasan','South Khorasan','Sistan and Baluchestan'}
def a_irn(p):
    return 'soviet' if (p.get('name_en') or p.get('name') or '') in SOV_IRN else 'neutral'
ITA_FR={'Alpes-Maritimes','Var','Bouches-du-Rhône','Vaucluse','Alpes-de-Haute-Provence',
 'Hautes-Alpes','Drôme','Isère','Savoie','Haute-Savoie','Corse-du-Sud','Haute-Corse'}
AME_FR={'French Guiana','Guadeloupe','Martinique'}
def a_fra(p):
    nm=p.get('name_en') or p.get('name') or ''
    if nm in ITA_FR: return 'italy'
    if nm in AME_FR: return 'america'
    return 'gersph'
JPN_IND={'Andaman and Nicobar Islands','Arunachal Pradesh','Assam','Manipur','Meghalaya',
 'Mizoram','Nagaland','Tripura'}
def a_ind(p):
    return 'japan' if (p.get('name_en') or p.get('name') or '') in JPN_IND else 'neutral'
SPLIT={'RUS':a_rus,'CHN':a_chn,'IRN':a_irn,'FRA':a_fra,'IND':a_ind}

# ---- потоковый сбор admin-1 со всего мира ------------------------------------
def to_float(x):
    return [to_float(i) for i in x] if isinstance(x,list) else float(x)
bloc_geoms={k:[] for k,_,_,_ in BLOCS}
n=0
with open('adm1_10m.geojson','rb') as fh:
    for feat in ijson.items(fh,'features.item'):
        p=feat['properties']; code=p.get('adm0_a3')
        if code in EXCLUDE: continue
        bk= SPLIT[code](p) if code in SPLIT else CODE2BLOC.get(code,'neutral')
        g=feat['geometry']
        geom=shape({'type':g['type'],'coordinates':to_float(g['coordinates'])})
        if not geom.is_valid: geom=make_valid(geom).buffer(0)
        if geom.is_empty: continue
        if geom.bounds[2] < -150: continue          # отбрасываем заворот за 180° (артефакт)
        bloc_geoms[bk].append(geom); n+=1
print('admin-1 единиц обработано:', n)

# ---- слияние блоков (внутренние границы исчезают) ----------------------------
dissolved={}
for k,_,_,_ in BLOCS:
    if bloc_geoms[k]:
        dissolved[k]=unary_union(bloc_geoms[k]).buffer(0).simplify(0.06, preserve_topology=True)
land=unary_union(list(dissolved.values())).buffer(0).simplify(0.06, preserve_topology=True)
print('блоки слиты')

# ---- проекция ----------------------------------------------------------------
T=Transformer.from_crs('EPSG:4326','+proj=robin +lon_0=0 +datum=WGS84',always_xy=True)
def project(lon,lat): return T.transform(lon,lat)
xs=[];ys=[]
for lat in range(-58,86,2):
    for lon in range(-180,181,5):
        x,y=project(lon,lat); xs.append(x); ys.append(y)
MINX,MAXX,MINY,MAXY=min(xs),max(xs),min(ys),max(ys)
W,H=1700,980; PADL,PADT,PADR,PADB=40,150,40,230
def to_svg(x,y): return PADL+(x-MINX)/(MAXX-MINX)*W, PADT+(MAXY-y)/(MAXY-MINY)*H
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
import base64
FRAK=base64.b64encode(open('maguntia.ttf','rb').read()).decode()
TANN=base64.b64encode(open('tannenberg.ttf','rb').read()).decode()
oc=outline()
S=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTW} {TOTH}" font-family="\'Iowan Old Style\',\'Palatino Linotype\',\'Book Antiqua\',Palatino,Georgia,serif">']
S.append('<defs>'
 "<style>"
 f"@font-face{{font-family:'Tannenberg';src:url(data:font/ttf;base64,{TANN}) format('truetype');font-weight:400;font-style:normal;}}"
 f"@font-face{{font-family:'SchwabacherReich';src:url(data:font/ttf;base64,{FRAK}) format('truetype');font-weight:400;font-style:normal;}}"
 ".coast{stroke:#33424a;stroke-width:.55;stroke-opacity:.4;stroke-linejoin:round}"
 ".grat{fill:none;stroke:#aebcc2;stroke-width:.6;stroke-opacity:.45}</style>"
 f'<clipPath id="w"><path d="{oc}"/></clipPath></defs>')
S.append(f'<rect width="{TOTW}" height="{TOTH}" fill="#f4f1ea"/>')
S.append(f'<path d="{oc}" fill="#dbe6ea"/>')
S.append('<g class="grat" clip-path="url(#w)">'+''.join(f'<path d="{p}"/>' for p in grat())+'</g>')
# базовый слой суши (прячет микрозазоры между блоками)
S.append(f'<path d="{geom_d(land)}" fill="#d7d0c2"/>')
# блоки (слитые), границы только между блоками и побережья
for k,_,color,_ in BLOCS:
    if k in dissolved:
        S.append(f'<path d="{geom_d(dissolved[k])}" fill="{color}" class="coast"/>')

# ---- немецкие подписи --------------------------------------------------------
def lab(lon,lat,lines,anc='middle'):
    """lines: (text, size, weight, color, tracking_em, italic) — без обводки, тон заливки."""
    x,y=to_svg(*project(lon,lat)); out=[]; cy=y
    for t,sz,wt,col,tr,it in lines:
        st='font-style:italic' if it else ''
        out.append(f'<text x="{x:.1f}" y="{cy:.1f}" text-anchor="{anc}" font-size="{sz}" '
                   f'font-weight="{wt}" fill="{col}" letter-spacing="{sz*tr:.2f}" style="{st}">{t}</text>')
        cy+=sz*1.16
    return ''.join(out)
L='#e4e9f2'
# великие державы — капитель в разрядку, тон заливки, без обводки
rx,ry=to_svg(*project(40,51))
for i,word in enumerate(('Großdeutsches','Reich')):
    S.append(f'<text x="{rx:.0f}" y="{ry+i*31:.0f}" text-anchor="middle" font-size="31" '
             f'fill="#dde6e8" font-family="\'UnifrakturMaguntia\',\'SchwabacherReich\',serif">{word}</text>')
S.append(lab(96,59,[('SOWJETUNION',22,400,'#4a3410',0.16,False)]))
S.append(lab(-93,44,[('PANAMERIKANISCHE',19,400,'#e4e9f2',0.10,False),('UNION',19,400,'#e4e9f2',0.16,False)]))
S.append(lab(113,14,[('JAPANISCHE SPHÄRE',18,400,'#4e2018',0.13,False)]))
# имперские / региональные
S.append(lab(16,25,[('ITALIENISCHES',15,400,'#2c2f12',0.16,False),('IMPERIUM',15,400,'#2c2f12',0.18,False)]))
S.append(lab(16.5,35.2,[('Mare Nostrum',14,400,'#5f7a86',0.42,True)]))
S.append(lab(22,-2,[('MITTELAFRIKA',16,400,'#1f363a',0.18,False)]))
# второстепенные — курсив
S.append(lab(-60,-16,[('Südamerika',15,400,'#e4e9f2',0.03,True)]))
S.append(lab(101,30,[('Freies China',14,400,'#544e3f',0.03,True)]))
S.append(lab(80,21,[('Freies Indien',14,400,'#544e3f',0.03,True)]))
S.append(lab(47,21,[('Neutraler Orient',13,400,'#5b5546',0.03,True)]))

# ---- заголовок ---------------------------------------------------------------
cx=TOTW/2
S.append(f'<text x="{cx:.0f}" y="62" text-anchor="middle" font-size="40" fill="#26333c" '
         f'letter-spacing="2" font-family="\'Tannenberg\',serif">Der krumme Sieg</text>')
S.append(f'<text x="{cx:.0f}" y="91" text-anchor="middle" font-size="17" font-style="italic" fill="#4a5a62" letter-spacing="1">Die Aufteilung der Welt nach dem Zweiten Weltkrieg · um 1948</text>')

# ---- легенда -----------------------------------------------------------------
ly=PADT+H+46; lx=PADL+30; cw=380
S.append(f'<text x="{lx}" y="{ly-24}" font-size="15" font-weight="700" fill="#1d2a30">Einflusssphären</text>')
for i,(k,name,color,_) in enumerate(BLOCS):
    bx=lx+(i//4)*cw; by=ly+(i%4)*35
    S.append(f'<rect x="{bx}" y="{by-13}" width="22" height="16" fill="{color}" stroke="#27343a" stroke-width=".4"/>')
    S.append(f'<text x="{bx+30}" y="{by}" font-size="14.5" fill="#222">{name}</text>')
S.append(f'<text x="{TOTW-PADR-20}" y="{TOTH-22}" text-anchor="end" font-size="11" fill="#8a8f8a" font-style="italic">Geometrie: Natural Earth admin-1 · Robinson-Projektion · weltweit nach Verwaltungseinheiten aufgeteilt, Binnengrenzen aufgelöst</text>')
S.append('</svg>')
open('crooked_victory.svg','w',encoding='utf-8').write('\n'.join(S))
print('OK', len('\n'.join(S))//1024,'KB')
