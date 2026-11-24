#!/usr/bin/env python3
"""Mírë Nolmeo v14 — единая структура: центр и периферия v12 в одном масштабе.

Одно поле на весь витраж:
    F(z) = (z^3 + i)/z * (z^8 + R^8)/(R^8 - z^8)
Нули Троицы (z^3 = -i) — триллианты; полюс в начале — белый камень;
восемь нулей z^8 = -R^8 (углы 22.5° + 45°k) — восемь самоцветов v12;
восемь полюсов z^8 = R^8 (углы 45°k) — восемь кристальных лучей v12.
Все знаки одного размера; разметка фазы та же, что в камне v12.
"""
import re, math, cmath, sys
import numpy as np
from skimage import measure

SRC = '/mnt/user-data/uploads/User_elvish_device_v12.svg'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/outputs/User_elvish_device_v14_unified.svg'
RHO = float(sys.argv[2]) if len(sys.argv) > 2 else 66.0      # радиус нулей Троицы, px
RING = float(sys.argv[3]) if len(sys.argv) > 3 else 1.9      # радиус кольца в долях RHO
MARK = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6      # масштаб самоцветов v12 (r=22)

src = open(SRC, encoding='utf-8').read()
src = re.sub(r'<metadata>.*?</metadata>', '', src, flags=re.S)

R_OCT, R_BLACK = 172, 178
RHO_V12 = 22.94
GEM_R = 22 * MARK                    # радиус знака
TRIL = GEM_R / 4.6                   # триллиант v12 ~4.6 в поперечнике от центра
STONE = GEM_R / 11.5 * 1.05          # белый камень v12: чёрное кольцо r=11.5

oct_pts = [(R_OCT * math.sin(math.radians(45 * i)), -R_OCT * math.cos(math.radians(45 * i)))
           for i in range(8)]
oct_str = ' '.join(f'{x:.2f},{y:.2f}' for x, y in oct_pts)

R8 = RING ** 8


def f_old(z):
    return (z ** 3 + 1j) / z


def F(z):
    return (z ** 3 + 1j) / z * (z ** 8 + R8) / (R8 - z ** 8)


CLASSES = [(0, 50, '#b9cae2'), (60, 10, '#a669a6'), (120, 50, '#d8bdc2'),
           (180, 10, '#deb154'), (240, 50, '#b5d7cc'), (300, 10, '#5ea5b4')]
STEP = 0.25
L = 182
xs = np.arange(-L, L + STEP, STEP)
X, Y = np.meshgrid(xs, xs)
Z = (X - 1j * Y) / RHO
Z[np.abs(Z) < 1e-9] = 1e-9
with np.errstate(all='ignore'):
    FF = F(Z)
FF[~np.isfinite(FF)] = 1.0
PH = np.degrees(np.angle(FF)) % 360


def wrapdiff(a, c):
    return (a - c + 180) % 360 - 180


def fmt(v):
    s = f'{v:.2f}'
    return '0.00' if s == '-0.00' else s


paths = []
for c, h, col in CLASSES:
    field = np.pad(h - np.abs(wrapdiff(PH, c)), 1, constant_values=-1.0)
    for cnt in measure.find_contours(field, 0.0):
        if len(cnt) < 8:
            continue
        pts = [(xs[0] + (p[1] - 1) * STEP, xs[0] + (p[0] - 1) * STEP) for p in cnt]
        thin = [pts[0]]
        for p in pts[1:]:
            if math.hypot(p[0] - thin[-1][0], p[1] - thin[-1][1]) >= 0.6:
                thin.append(p)
        if len(thin) < 4:
            continue
        d = 'M' + ' L'.join(f'{fmt(x)},{fmt(y)}' for x, y in thin) + 'Z'
        paths.append(f'  <path d="{d}" fill="{col}" stroke="#eef6f8" stroke-width="1.3" stroke-linejoin="round"/>')


def deriv(g, z, e=1e-6):
    return (g(z + e) - g(z - e)) / (2 * e)


# ---------- триллианты: те же нули, поворот по arg F'(z0)/f'(z0) ----------
trill = re.findall(r'<g class="zero trillion">.*?</g>', src, flags=re.S)
zeros_old = [(0.0, -22.94), (-19.87, 11.47), (19.87, 11.47)]
marks = []
for g, (zx, zy) in zip(trill, zeros_old):
    z0 = complex(zx, -zy) / RHO_V12
    rot = math.degrees(cmath.phase(deriv(F, z0) / deriv(f_old, z0)))
    nx, ny = z0.real * RHO, -z0.imag * RHO
    inner = g[len('<g class="zero trillion">'):-len('</g>')]
    marks.append(f'  <g class="zero trillion" transform="translate({nx:.2f},{ny:.2f}) rotate({rot:.2f}) '
                 f'scale({TRIL:.4f}) translate({-zx:.2f},{-zy:.2f})">{inner}</g>')

# ---------- самоцветы v12 — в нули кольца ----------
gems = re.findall(r'<g transform="rotate\(([\d.]+)\) translate\(0,-123\)">(.*?)</g>', src, flags=re.S)
assert len(gems) == 8
for ang, inner in gems:
    marks.append(f'  <g class="zero gem" transform="rotate({ang}) translate(0,{-RING * RHO:.2f}) '
                 f'scale({MARK})">{inner}</g>')

# ---------- кристальные лучи v12 — в полюса кольца ----------
# луч v12: от r=60 до r=116, середина 88, длина 56, ширина 10
RAY = MARK * 1.15
for k in range(8):
    marks.append(
        f'  <g class="pole ray" transform="rotate({45 * k}) translate(0,{-RING * RHO:.2f}) scale({RAY:.3f})">'
        f'<path d="M0,28 L5,0 L0,-28 L-5,0 Z" fill="#dfeef6" stroke="#9fc4dc" stroke-width="0.8"/>'
        f'<line x1="0" y1="26" x2="0" y2="-26" stroke="#9fc4dc" stroke-width="0.8"/></g>')

# ---------- пары точек v12 (Грей — Скотт): у четырёх главных лучей ----------
for k in range(4):
    for s in (-1, 1):
        marks.append(f'  <circle class="gs-dot" cx="0" cy="{-RING * RHO:.2f}" r="{3.5 * MARK + 0.4:.2f}" fill="#9fd3e0" '
                     f'stroke="#eef6f8" stroke-width="0.6" transform="rotate({90 * k + s * 12})"/>')

# ---------- белый камень v12 — в центральный полюс ----------
wa = src.index('<circle r="11.5"')
wb = src.index('</g>\n</g>\n</svg>')
white_stone = src[wa:wb].rstrip()

head = src[:src.index('<circle cx="340" cy="300" r="180"')]
head = re.sub(r'<title>.*?</title>',
              '<title>Mírë Nolmeo — эльфийский герб User, четырнадцатая редакция: центр и '
              'периферия v12 в одном масштабе — единое поле (z³+i)/z·(z⁸+R⁸)/(R⁸−z⁸); самоцветы в '
              'нулях кольца, кристальные лучи в его полюсах, триллианты в нулях Троицы, белый камень '
              'в центральном полюсе</title>', head, flags=re.S)
head = head.replace(' xmlns:c2pa="http://c2pa.org/manifest"', '')

svg = [head.rstrip(), '<g transform="translate(340,300)">',
       f'  <circle r="{R_BLACK}" fill="#141414" stroke="#eee9dc" stroke-width="3"/>',
       f'  <clipPath id="phaseFieldClip"><polygon points="{oct_str}"/></clipPath>',
       f'  <polygon points="{oct_str}" fill="#eef6f8"/>',
       '  <g class="phase-field" clip-path="url(#phaseFieldClip)">', *paths, '  </g>',
       f'  <polygon points="{oct_str}" fill="none" stroke="#eef6f8" stroke-width="2.5"/>',
       *marks,
       f'  <g class="pole white-stone" transform="scale({STONE:.4f})">', '  ' + white_stone, '  </g>',
       '</g>', '</svg>', '']
open(OUT, 'w', encoding='utf-8').write('\n'.join(svg))
print(OUT, len(paths), 'paths')
