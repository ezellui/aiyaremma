#!/usr/bin/env python3
"""Mírë Nolmeo v13 — центр и периферия v12 меняются местами.

Периферия: фазовый витраж (z^3+i)/z (та же ориентация и та же разметка фазы,
что в камне v12) заполняет восьмиугольник во весь круг; нули — трёхцветные
триллианты. Центр: уменьшенная копия прежнего поля — синий круг в кремово-
голубой оправе, восемь самоцветов, восемь кристальных лучей, пары точек,
в сердцевине — белый камень.
"""
import re, math
import numpy as np
from skimage import measure

SRC = '/mnt/user-data/uploads/User_elvish_device_v12.svg'
OUT = '/mnt/user-data/outputs/User_elvish_device_v13_swap.svg'

src = open(SRC, encoding='utf-8').read()
src = re.sub(r'<metadata>.*?</metadata>', '', src, flags=re.S)

# ---------- геометрия ----------
K = 70 / 168            # масштаб прежнего поля при переносе в центр
R_OCT = 172             # описанный радиус восьмиугольника-витража
R_BLACK = 178           # чёрная оправа витража (бывшее чёрное кольцо камня)
RHO = 118               # радиус нулей (в v12: 22.94 при камне 48)
TRIL = 3.6              # масштаб триллиантов относительно v12
RHO_V12 = 22.94

oct_pts = [(R_OCT * math.sin(math.radians(45 * i)), -R_OCT * math.cos(math.radians(45 * i)))
           for i in range(8)]
oct_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in oct_pts)

# ---------- фазовое поле ----------
# разметка фазы из v12 (установлена замером): три широких бледных сектора по 100°
# и три узкие насыщенные полосы ±10° около 60°, 180°, 300°
CLASSES = [  # (центр, полуширина, цвет)
    (0,   50, '#b9cae2'),
    (60,  10, '#a669a6'),
    (120, 50, '#d8bdc2'),
    (180, 10, '#deb154'),
    (240, 50, '#b5d7cc'),
    (300, 10, '#5ea5b4'),
]
STEP = 0.25
L = 182
xs = np.arange(-L, L + STEP, STEP)
X, Y = np.meshgrid(xs, xs)          # экранные координаты, y вниз
Z = (X - 1j * Y) / RHO
Z[np.abs(Z) < 1e-9] = 1e-9
F = (Z ** 3 + 1j) / Z
PH = np.degrees(np.angle(F)) % 360


def wrapdiff(a, c):
    return (a - c + 180) % 360 - 180


def fmt(v):
    s = f'{v:.2f}'
    return '0.00' if s == '-0.00' else s


paths = []
for c, h, col in CLASSES:
    field = h - np.abs(wrapdiff(PH, c))
    field = np.pad(field, 1, constant_values=-1.0)   # замкнуть контуры по краю
    for cnt in measure.find_contours(field, 0.0):
        if len(cnt) < 8:
            continue
        pts = [(xs[0] + (p[1] - 1) * STEP, xs[0] + (p[0] - 1) * STEP) for p in cnt]
        # прореживание: не чаще 0.6 единицы
        thin = [pts[0]]
        for p in pts[1:]:
            if math.hypot(p[0] - thin[-1][0], p[1] - thin[-1][1]) >= 0.6:
                thin.append(p)
        d = 'M' + ' L'.join(f'{fmt(x)},{fmt(y)}' for x, y in thin) + 'Z'
        paths.append(f'  <path d="{d}" fill="{col}" stroke="#eef6f8" stroke-width="1.4" stroke-linejoin="round"/>')

# ---------- триллианты: переносим из v12 с масштабом ----------
trill = re.findall(r'<g class="zero trillion">.*?</g>', src, flags=re.S)
assert len(trill) == 3
zeros_old = [(0.0, -22.94), (-19.87, 11.47), (19.87, 11.47)]
tril_out = []
for g, (zx, zy) in zip(trill, zeros_old):
    nx, ny = zx / RHO_V12 * RHO, zy / RHO_V12 * RHO
    inner = g[len('<g class="zero trillion">'):-len('</g>')]
    tril_out.append(
        f'  <g class="zero trillion" transform="translate({nx:.2f},{ny:.2f}) scale({TRIL}) '
        f'translate({-zx:.2f},{-zy:.2f})">{inner}</g>')

# ---------- прежняя периферия: лучи, точки, восемь камней ----------
a = src.index('<g transform="translate(340,300)">') + len('<g transform="translate(340,300)">')
b = src.index('<circle r="54"')
ring_block = src[a:b].rstrip()

# прежний центр — белый камень в чёрной оправе (без витража)
wa = src.index('<circle r="11.5"')
wb = src.index('</g>\n</g>\n</svg>')
white_stone = src[wa:wb].rstrip()

# шапка и щит (ромб, кайма, звёзды) — без изменений
head_end = src.index('<circle cx="340" cy="300" r="180"')
head = src[:head_end]
head = re.sub(r'<title>.*?</title>',
              '<title>Mírë Nolmeo — эльфийский герб User, тринадцатая редакция: '
              'центр и периферия v12 поменялись местами — фазовый витраж (z³+i)/z во весь '
              'круг, кольцо восьми самоцветов в сердцевине</title>', head, flags=re.S)
head = head.replace(' xmlns:c2pa="http://c2pa.org/manifest"', '')

svg = [head.rstrip(), '<g transform="translate(340,300)">',
       f'  <circle r="{R_BLACK}" fill="#141414" stroke="#eee9dc" stroke-width="3"/>',
       '  <g class="phase-field">',
       f'  <clipPath id="phaseFieldClip"><polygon points="{oct_str}"/></clipPath>',
       f'  <polygon points="{oct_str}" fill="#eef6f8"/>',
       '  <g clip-path="url(#phaseFieldClip)">',
       *paths,
       '  </g>',
       f'  <polygon points="{oct_str}" fill="none" stroke="#eef6f8" stroke-width="2.5"/>',
       *tril_out,
       '  </g>',
       '  <g class="core">',
       '  <circle r="75" fill="#eee9dc"/>',
       '  <circle r="71.67" fill="#6fa3d0"/>',
       '  <circle r="70" fill="#1b2b64"/>',
       f'  <g transform="scale({K:.5f})">',
       ring_block,
       '  </g>',
       f'  <g transform="scale({54 * K / 11.5 * 0.82:.4f})">',
       '  ' + white_stone,
       '  </g>',
       '  </g>',
       '</g>',
       '</svg>', '']
open(OUT, 'w', encoding='utf-8').write('\n'.join(svg))
print(OUT, len(paths), 'paths')
