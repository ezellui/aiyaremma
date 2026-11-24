#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Карта 'Кривой Победы' — альт-исторический раздел мира после победы Оси.
Источник геометрии: Natural Earth 50m admin_0. Проекция: Робинсона."""
import json, math
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from pyproj import Transformer

# ------------------------------------------------------------------ данные
GJ = json.load(open('ne.geojson'))
FEATS = GJ['features']

# ------------------------------------------------------------------ блоки
# Великогерманский Рейх — прямая территория + восточные рейхскомиссариаты
REICH = {
 'DEU','AUT','CZE','POL','SVN','LUX','EST','LVA','LTU','BLR','UKR','MDA',
 'GEO','ARM','AZE','ALD',
}
# Германская сфера — сателлиты, германская конфедерация (вкл. Британию) и колонии
GER_SPHERE = {
 # Европа-сателлиты
 'FRA','BEL','NLD','NOR','DNK','GBR','SVK','HUN','ROU','BGR','FIN',
 'HRV','BIH','SRB',
 # Германская Африка (Миттельафрика + Зап./Юж. Африка)
 'MAR','DZA','MRT','SAH','SEN','GMB','GNB','GIN','SLE','LBR','CIV','MLI',
 'BFA','GHA','TGO','BEN','NGA','NER','TCD','CMR','CAF','GNQ','GAB','COG',
 'COD','AGO','ZMB','ZWE','MWI','MOZ','TZA','KEN','UGA','RWA','BDI','NAM',
 'BWA','ZAF','LSO','SWZ','MDG','STP','CPV','COM','MUS','SYC',
}
# Итальянская империя (Mare Nostrum)
ITALY = {
 'ITA','SMR','VAT','MLT','CYP','CYN',
 'LBY','EGY','TUN','SDN','SDS','ETH','ERI','SOM','SOL','DJI',
 'ALB','GRC','MKD','MNE','KOS',
}
# Японская сфера сопроцветания
JAPAN = {
 'JPN','KOR','PRK','CHN','TWN','HKG','MAC','MMR','THA','KHM','LAO','VNM',
 'MYS','IDN','PHL','BRN','SGP','TLS','PLW','FSM','MHL',
}
# Советский остаток (за Уралом) + приобретения
SOVIET = {'KAZ','UZB','TKM','KGZ','TJK','MNG','AFG'}
# Панамериканский союз (всё Западное полушарие + Гренландия/Исландия)
AMERICA = {
 'USA','CAN','MEX','GTM','BLZ','HND','SLV','NIC','CRI','PAN',
 'COL','VEN','ECU','PER','BRA','BOL','PRY','CHL','ARG','URY','GUY','SUR',
 'CUB','DOM','HTI','JAM','BHS','TTO','BRB','GRD','LCA','VCT','DMA','ATG',
 'KNA','PRI','VIR','VGB','CYM','TCA','AIA','MSR','BMU','GRL','ISL',
 'ABW','CUW','SXM','BLM','MAF','SPM','BHS','FLK','SGS',
}
# Нейтральные / неприсоединившиеся
NEUTRAL = {
 'ESP','PRT','AND','CHE','LIE','SWE','IRL','TUR','MCO',
 'SAU','YEM','OMN','ARE','QAT','BHR','KWT','IRQ','IRN','SYR','JOR','LBN',
 'ISR','PSX',
 'IND','PAK','BGD','NPL','BTN','LKA','MDV','KAS','IOA',
 'AUS','NZL','FJI','VUT','SLB','NCL','PNG','WSM','TON','KIR','TUV','NRU',
 'COK','NIU','PYF','PCN','GUM','MNP','ASM','WLF','IMN','JEY','GGY','FRO',
 'SHN',
}
EXCLUDE = {'ATA','ATC','ATF','HMD','IOT','BVT','SGS','FLK'}  # Антарктида и дальние

BLOCS = [
 ('reich',   'Великогерманский Рейх',        '#39474f', REICH),
 ('gersph',  'Германская сфера и колонии',    '#8fa8a8', GER_SPHERE),
 ('italy',   'Итальянская империя (Mare Nostrum)', '#8d9358', ITALY),
 ('japan',   'Японская сфера сопроцветания',  '#b3654d', JAPAN),
 ('soviet',  'Советский остаток',             '#bf9646', SOVIET),
 ('america', 'Панамериканский союз',          '#56649f', AMERICA),
 ('neutral', 'Нейтральные · неприсоединившиеся', '#c9c4b6', NEUTRAL),
]
CODE2BLOC = {}
for key,_,_,codes in BLOCS:
    for c in codes:
        CODE2BLOC[c] = key

# ------------------------------------------------------------------ разрез России
RUS_BANDS = {  # код блока -> (lon_min, lon_max)
 'reich':  (15, 60),    # европейская Россия / Московия / Кавказ
 'soviet': (60, 120),   # сибирский остаток
 'japan':  (120, 180),  # Дальний Восток
}

# ------------------------------------------------------------------ сбор геометрий по блокам
bloc_geoms = {k: [] for k,_,_,_ in BLOCS}
unassigned = set()

for f in FEATS:
    code = f['properties'].get('ADM0_A3')
    if code in EXCLUDE:
        continue
    geom = shape(f['geometry'])
    if not geom.is_valid:
        geom = geom.buffer(0)
    if code == 'RUS':
        for bk,(lo,hi) in RUS_BANDS.items():
            part = geom.intersection(box(lo, -90, hi, 90))
            if not part.is_empty:
                bloc_geoms[bk].append(part.simplify(0.06, preserve_topology=True))
        continue
    bk = CODE2BLOC.get(code)
    if bk is None:
        unassigned.add(code)
        bk = 'neutral'
    bloc_geoms[bk].append(geom.simplify(0.06, preserve_topology=True))

print('Не распределены (-> нейтральные):', sorted(unassigned))

# ------------------------------------------------------------------ проекция
T = Transformer.from_crs('EPSG:4326', '+proj=robin +lon_0=0 +datum=WGS84', always_xy=True)
def project(lon, lat):
    return T.transform(lon, lat)

# границы карты (по проекции рамки мира, без Антарктиды)
xs, ys = [], []
for lat in range(-58, 86, 2):
    for lon in range(-180, 181, 5):
        x,y = project(lon, lat); xs.append(x); ys.append(y)
MINX,MAXX,MINY,MAXY = min(xs),max(xs),min(ys),max(ys)

W, H = 1700, 980          # внутреннее поле карты
PADL, PADT = 40, 150      # отступы (слева, сверху под заголовок)
PADR, PADB = 40, 230      # справа, снизу (под легенду)
def to_svg(x, y):
    sx = PADL + (x - MINX)/(MAXX-MINX)*W
    sy = PADT + (MAXY - y)/(MAXY-MINY)*H
    return sx, sy

def ring_to_path(coords):
    pts = []
    for lon, lat in coords:
        x,y = project(lon, lat); sx,sy = to_svg(x,y)
        pts.append(f'{sx:.1f},{sy:.1f}')
    if not pts: return ''
    return 'M' + ' L'.join(pts) + ' Z'

def geom_to_d(geom):
    d = []
    polys = geom.geoms if geom.geom_type.startswith('Multi') else [geom]
    for poly in polys:
        if poly.is_empty or poly.geom_type != 'Polygon':
            # GeometryCollection из intersection -> разложить
            if poly.geom_type == 'GeometryCollection':
                for g in poly.geoms:
                    if g.geom_type == 'Polygon':
                        d.append(ring_to_path(g.exterior.coords))
                        for r in g.interiors:
                            d.append(ring_to_path(r.coords))
            continue
        d.append(ring_to_path(poly.exterior.coords))
        for r in poly.interiors:
            d.append(ring_to_path(r.coords))
    return ' '.join(x for x in d if x)

# ------------------------------------------------------------------ графика: графитная сетка
def graticule_paths():
    out = []
    for lon in range(-180, 181, 30):
        pts = [to_svg(*project(lon, lat)) for lat in range(-58, 86, 2)]
        out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts))
    for lat in range(-60, 91, 30):
        pts = [to_svg(*project(lon, lat)) for lon in range(-180, 181, 3)]
        out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts))
    return out

def world_outline():
    pts = []
    for lat in range(-58, 86, 2): pts.append(to_svg(*project(180, lat)))
    for lon in range(180, -181, -2): pts.append(to_svg(*project(lon, 85)))
    for lat in range(85, -59, -2): pts.append(to_svg(*project(-180, lat)))
    for lon in range(-180, 181, 2): pts.append(to_svg(*project(lon, -58)))
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts) + ' Z'

# ------------------------------------------------------------------ SVG
TOTW = PADL + W + PADR
TOTH = PADT + H + PADB
COLOR = {k:c for k,_,c,_ in BLOCS}

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTW} {TOTH}" '
           f'font-family="Georgia, \'Times New Roman\', serif">')
svg.append('<defs><style>'
           '.bd{stroke:#27343a;stroke-width:.35;stroke-opacity:.45;stroke-linejoin:round}'
           '.grat{fill:none;stroke:#b9c6cc;stroke-width:.6;stroke-opacity:.55}'
           '.lbl{fill:#1d2a30;font-weight:700;letter-spacing:.5px}'
           '.sub{fill:#3a4a52}'
           '</style></defs>')

# фон-океан
oc = world_outline()
svg.append(f'<rect x="0" y="0" width="{TOTW}" height="{TOTH}" fill="#f4f1ea"/>')
svg.append(f'<path d="{oc}" fill="#dce7eb"/>')
# сетка (под странами? лучше над океаном, под сушей: рисуем океанскую сетку, затем сушу)
svg.append('<g class="grat" clip-path="url(#world)">')
svg.append(f'<clipPath id="world"><path d="{oc}"/></clipPath>')
for p in graticule_paths():
    svg.append(f'<path d="{p}"/>')
svg.append('</g>')

# суша по блокам
for key,name,color,_ in BLOCS:
    geoms = bloc_geoms[key]
    if not geoms: continue
    svg.append(f'<g id="bloc-{key}" fill="{color}">')
    for g in geoms:
        d = geom_to_d(g)
        if d:
            svg.append(f'<path class="bd" d="{d}"/>')
    svg.append('</g>')

# контур мира поверх
svg.append(f'<path d="{oc}" fill="none" stroke="#5b6f78" stroke-width="1.1"/>')

# ------------------------------------------------------------------ крупные подписи блоков
def place_label(lon, lat, text, size=20, sub=None, anchor='middle', color='#16232a'):
    x,y = to_svg(*project(lon, lat))
    s = f'<text class="lbl" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" ' \
        f'font-size="{size}" fill="{color}">{text}</text>'
    if sub:
        s += f'<text class="sub" x="{x:.0f}" y="{y+size*0.95:.0f}" text-anchor="{anchor}" ' \
             f'font-size="{size*0.6:.0f}" font-style="italic">{sub}</text>'
    return s

svg.append(place_label(28, 52, 'РЕЙХ', 26, 'Großdeutsches Reich', color='#e9eef0'))
svg.append(place_label(86, 8, 'ЯПОНСКАЯ СФЕРА', 19, 'Сопроцветание', color='#fbeee9'))
svg.append(place_label(95, 60, 'СОВЕТСКИЙ ОСТАТОК', 17, color='#3a2c0f'))
svg.append(place_label(20, 20, 'ITALIA', 17, 'Mare Nostrum', color='#2e2f12'))
svg.append(place_label(22, -6, 'Германская', 14, 'Африка', color='#16242a'))
svg.append(place_label(-96, 41, 'ПАНАМЕРИКА', 20, 'Pan-American Union', color='#eef1f6'))
svg.append(place_label(-58, -18, 'Южная', 13, 'Америка', color='#eef1f6'))
svg.append(place_label(79, 22, 'Свободная', 13, 'Индия', color='#3a352a', ))
svg.append(place_label(45, 24, 'нейтральный Восток', 11, color='#5a5642'))

# ------------------------------------------------------------------ заголовок
cx = TOTW/2
svg.append(f'<text x="{cx:.0f}" y="62" text-anchor="middle" font-size="40" '
           f'font-weight="700" fill="#1d2a30" letter-spacing="1px">КРИВАЯ ПОБЕДА</text>')
svg.append(f'<text x="{cx:.0f}" y="92" text-anchor="middle" font-size="18" '
           f'font-style="italic" fill="#42525a">Раздел мира после Второй мировой войны · ок. 1948 года</text>')
svg.append(f'<text x="{cx:.0f}" y="116" text-anchor="middle" font-size="12.5" '
           f'fill="#6a7780">Ни одна держава не победила до конца — и каждая ушла с войны со своей добычей и своей раной</text>')

# ------------------------------------------------------------------ легенда
ly = PADT + H + 40
lx = PADL + 30
svg.append(f'<text x="{lx}" y="{ly-14}" font-size="15" font-weight="700" fill="#1d2a30">Сферы влияния</text>')
col_w = 360
for i,(key,name,color,_) in enumerate(BLOCS):
    row = i % 4; col = i // 4
    bx = lx + col*col_w; by = ly + row*34
    svg.append(f'<rect x="{bx}" y="{by-13}" width="22" height="16" fill="{color}" '
               f'stroke="#27343a" stroke-width=".4"/>')
    svg.append(f'<text x="{bx+30}" y="{by}" font-size="14.5" fill="#222">{name}</text>')

# примечание об источнике
svg.append(f'<text x="{TOTW-PADR-20}" y="{TOTH-22}" text-anchor="end" font-size="11" '
           f'fill="#8a8f8a" font-style="italic">геометрия: Natural Earth 50m · проекция Робинсона · '
           f'границы России рассечены по 60° и 120° в.д.</text>')

svg.append('</svg>')

open('/home/claude/crooked_victory.svg','w',encoding='utf-8').write('\n'.join(svg))
print('OK -> crooked_victory.svg  (', len('\n'.join(svg))//1024, 'KB )')
