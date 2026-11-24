"""Compositional plan for the Russian «Тенгварь» cover (back + spine + front), SVG in mm.
usage: make_plan.py OUT.svg BACK.png FONTDIR
"""
import sys, base64, math, os

out, back_png, fontdir = sys.argv[1:4]

def b64(fn):
    return base64.b64encode(open(fn, 'rb').read()).decode()

# ---- geometry (mm)
BLEED = 3.0
PAGE_W, PAGE_H = 129.03, 198.12
SPINE = 6.94                      # current cover; recompute for 96 pp. and the chosen paper
W = 2 * PAGE_W + SPINE + 2 * BLEED
H = PAGE_H + 2 * BLEED
X_BACK = BLEED
X_SPINE = BLEED + PAGE_W
X_FRONT = X_SPINE + SPINE
X_END = X_FRONT + PAGE_W
Y0, Y1 = BLEED, BLEED + PAGE_H
SAFE = 6.0
CX = X_FRONT + PAGE_W / 2          # front axis

# ---- palette: clean tinctures, black contour
NAVY = '#16235f'
GOLD = '#d9a520'
SILVER = '#e4e9ef'
RED = '#7a0000'                  # the red of the back-cover ornament
LAMP = '#5fc8ff'
CREAM = '#fff0d8'
INK = '#111111'
NOTE = '#d4007a'

parts = []
def add(s):
    parts.append(s)

def note(x, y, text, anchor='start', size=2.6):
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="DejaVu Sans, sans-serif" font-size="{size}" '
        f'fill="{NOTE}" text-anchor="{anchor}">{text}</text>')

def leader(x1, y1, x2, y2):
    add(f'<path d="M{x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f}" stroke="{NOTE}" stroke-width="0.25" fill="none"/>'
        f'<circle cx="{x2:.2f}" cy="{y2:.2f}" r="0.6" fill="{NOTE}"/>')

def star(cx, cy, r_major, r_minor, n=8, rot=-90, inner=0.28):
    """star of the House of Fëanor: n long rays and n short rays between them"""
    pts = []
    for i in range(4 * n):
        a = math.radians(rot + i * 360 / (4 * n))
        kind = i % 4
        r = r_major if kind == 0 else (r_minor if kind == 2 else r_major * inner)
        pts.append(f'{cx + r * math.cos(a):.2f},{cy + r * math.sin(a):.2f}')
    return ' '.join(pts)

# ---------------------------------------------------------------- document
add(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
 width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.2f} {H:.2f}">
<title>Тенгварь — схема обложки</title>
<defs>
<style>
@font-face {{ font-family: 'Arnold BocklinC'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))}); }}
@font-face {{ font-family: 'Kurale'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))}); }}
</style>
<radialGradient id="lampglow" cx="0.5" cy="0.5" r="0.5">
 <stop offset="0" stop-color="{LAMP}" stop-opacity="0.85"/><stop offset="1" stop-color="{LAMP}" stop-opacity="0"/>
</radialGradient>
<path id="archtext" d="M{X_FRONT + 22:.2f},{58:.2f} C{X_FRONT + 22:.2f},{24:.2f} {X_END - 22:.2f},{24:.2f} {X_END - 22:.2f},{58:.2f}"/>
</defs>
''')

# ---- layer: background
add('<g inkscape:groupmode="layer" inkscape:label="Фон">')
add(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>')
# back: the current Russian back cover (no bleed in the source, so it sits inside the trim)
add(f'<image x="{X_BACK:.2f}" y="{Y0:.2f}" width="{PAGE_W:.2f}" height="{PAGE_W * 1170 / 762:.2f}" '
    f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{b64(back_png)}"/>')
# spine and front: navy night sky with bleed
add(f'<rect x="{X_SPINE:.2f}" y="0" width="{W - X_SPINE:.2f}" height="{H:.2f}" fill="{NAVY}"/>')
for i in range(26):          # a few stars of Varda
    x = X_FRONT + 8 + (i * 37.3) % (PAGE_W - 16)
    y = 8 + (i * 53.7) % (PAGE_H - 30)
    if 60 < y < 172 and abs(x - CX) < 40:
        continue
    add(f'<polygon points="{star(x, y, 1.2, 0.6, n=4, inner=0.3)}" fill="{SILVER}" opacity="0.8"/>')
add('</g>')

# ---- layer: composition
add('<g inkscape:groupmode="layer" inkscape:label="Композиция">')
# Two Trees as framing columns, branches meeting in an arch over the title
for side, col, name in ((-1, GOLD, 'Laurelin'), (1, SILVER, 'Telperion')):
    tx = CX + side * (PAGE_W / 2 - 13)
    trunk = (f'M{tx - 3.2:.2f},{Y1 - 8:.2f} C{tx - 2.2:.2f},{140} {tx - 4:.2f},{100} {tx - 1.6:.2f},{62} '
             f'L{tx + 1.6:.2f},{62} C{tx + 4:.2f},{100} {tx + 2.2:.2f},{140} {tx + 3.2:.2f},{Y1 - 8:.2f} Z')
    add(f'<path d="{trunk}" fill="{col}" stroke="{INK}" stroke-width="0.7"/>')
    # roots
    add(f'<path d="M{tx - 3.2:.2f},{Y1 - 8:.2f} q{-5 * 1:.2f},3 {-9:.2f},4 M{tx + 3.2:.2f},{Y1 - 8:.2f} q5,3 9,4" '
        f'stroke="{INK}" stroke-width="0.7" fill="none"/>')
    # crown arching to the axis
    add(f'<path d="M{tx:.2f},{64} C{tx:.2f},{22} {CX - side * 4:.2f},{18} {CX:.2f},{13}" '
        f'stroke="{col}" stroke-width="5.5" fill="none" stroke-linecap="round"/>')
    add(f'<path d="M{tx:.2f},{64} C{tx:.2f},{22} {CX - side * 4:.2f},{18} {CX:.2f},{13}" '
        f'stroke="{INK}" stroke-width="0.35" fill="none" stroke-dasharray="1.2 1.2"/>')
    for k in range(9):       # blossoms / leaves along the crown and the trunk
        t = k / 8
        bx = tx + (CX - tx) * (1 - (1 - t) ** 2) + side * 0.0
        by = 64 - 51 * math.sin(t * math.pi / 2) ** 0.8
        add(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="2.1" fill="{col}" stroke="{INK}" stroke-width="0.4"/>')
    for k in range(6):
        add(f'<ellipse cx="{tx + side * (3.5 + (k % 2) * 1.5):.2f}" cy="{75 + k * 17:.2f}" rx="3.2" ry="1.4" '
            f'transform="rotate({side * -30} {tx + side * 4:.2f} {75 + k * 17:.2f})" fill="{col}" stroke="{INK}" stroke-width="0.35"/>')

# inscription band along the inner edge of the arch
add(f'<use xlink:href="#archtext" stroke="{RED}" stroke-width="5.2" fill="none"/>')
add(f'<use xlink:href="#archtext" stroke="{GOLD}" stroke-width="4.2" fill="none"/>')
add(f'<text font-family="Kurale" font-size="2.9" fill="{RED}" letter-spacing="0.35">'
    f'<textPath xlink:href="#archtext" startOffset="50%" text-anchor="middle">'
    f'·  tengwasse Fëanáro  ·  надпись тенгваром  ·</textPath></text>')

# title inside the arch
add(f'<text x="{CX:.2f}" y="51" font-family="Arnold BocklinC" font-size="17" text-anchor="middle" '
    f'fill="{GOLD}" stroke="{INK}" stroke-width="0.45" paint-order="stroke">Тенгварь</text>')
add(f'<text x="{CX:.2f}" y="59" font-family="Kurale" font-size="5" text-anchor="middle" fill="{SILVER}">'
    f'в картинках и стихах</text>')

# central scene panel
px0, px1, py0, py1 = CX - 41, CX + 41, 66, 168
add(f'<path d="M{px0:.2f},{py1:.2f} L{px0:.2f},{py0 + 14:.2f} Q{px0:.2f},{py0:.2f} {CX:.2f},{py0:.2f} '
    f'Q{px1:.2f},{py0:.2f} {px1:.2f},{py0 + 14:.2f} L{px1:.2f},{py1:.2f} Z" fill="#22357f" stroke="{GOLD}" stroke-width="1.4"/>')
# Fëanorian lamp: blue fire in crystal, the light source instead of a halo
lx, ly = CX + 25, 118
add(f'<circle cx="{lx:.2f}" cy="{ly - 6:.2f}" r="26" fill="url(#lampglow)"/>')
add(f'<path d="M{lx - 4:.2f},{ly + 14:.2f} L{lx + 4:.2f},{ly + 14:.2f} L{lx + 2.4:.2f},{ly + 4:.2f} L{lx + 4.2:.2f},{ly - 6:.2f} '
    f'L{lx:.2f},{ly - 13:.2f} L{lx - 4.2:.2f},{ly - 6:.2f} L{lx - 2.4:.2f},{ly + 4:.2f} Z" fill="{SILVER}" stroke="{INK}" stroke-width="0.5"/>')
add(f'<path d="M{lx:.2f},{ly - 9:.2f} q2.6,4 0,7.5 q-2.6,-3.5 0,-7.5 Z" fill="{LAMP}" stroke="{INK}" stroke-width="0.3"/>')
# Fëanor (placeholder silhouette)
fx, fy = CX - 7, 112
add(f'<ellipse cx="{fx:.2f}" cy="{fy - 18:.2f}" rx="6.5" ry="8" fill="{SILVER}" stroke="{INK}" stroke-width="0.6"/>')
add(f'<path d="M{fx - 17:.2f},{146} C{fx - 17:.2f},{118} {fx - 10:.2f},{104} {fx:.2f},{103} '
    f'C{fx + 10:.2f},{104} {fx + 17:.2f},{118} {fx + 17:.2f},{146} Z" fill="{RED}" stroke="{INK}" stroke-width="0.6"/>')
# desk, book (parma), feather (quessë)
add(f'<rect x="{px0 + 4:.2f}" y="146" width="{px1 - px0 - 8:.2f}" height="9" fill="#8a5a1c" stroke="{INK}" stroke-width="0.6"/>')
add(f'<path d="M{fx - 13:.2f},146 Q{fx - 6:.2f},141 {fx:.2f},144 Q{fx + 6:.2f},141 {fx + 13:.2f},146 Z" '
    f'fill="{CREAM}" stroke="{INK}" stroke-width="0.5"/>')
add(f'<path d="M{fx + 4:.2f},144.5 C{fx + 8:.2f},134 {fx + 12:.2f},126 {fx + 20:.2f},119 '
    f'C{fx + 16:.2f},128 {fx + 11:.2f},136 {fx + 4:.2f},144.5 Z" fill="{SILVER}" stroke="{INK}" stroke-width="0.45"/>')

# keystone at the foot: star of the House of Fëanor
sx, sy = CX, 182
add(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="10.5" fill="{NAVY}" stroke="{GOLD}" stroke-width="0.9"/>')
add(f'<polygon points="{star(sx, sy, 9, 5.5)}" fill="{SILVER}" stroke="{INK}" stroke-width="0.35"/>')
add(f'<path d="M{CX - 41:.2f},{171} L{CX + 41:.2f},{171}" stroke="{GOLD}" stroke-width="0.9"/>')

# spine title
add(f'<text transform="translate({X_SPINE + SPINE / 2 + 1.25:.2f},{H / 2:.2f}) rotate(90)" font-family="Kurale" '
    f'font-size="3.9" text-anchor="middle" fill="{SILVER}">Тенгварь — стихи на квэнья</text>')
add('</g>')

# ---- layer: guides and notes
add('<g inkscape:groupmode="layer" inkscape:label="Разметка (скрыть перед печатью)">')
add(f'<rect x="{Y0:.2f}" y="{Y0:.2f}" width="{W - 2 * BLEED:.2f}" height="{PAGE_H:.2f}" fill="none" stroke="#00b000" stroke-width="0.3"/>')
for x in (X_SPINE, X_FRONT):
    add(f'<path d="M{x:.2f},0 L{x:.2f},{H:.2f}" stroke="#00b000" stroke-width="0.3" stroke-dasharray="1.5 1"/>')
for x0 in (X_BACK, X_FRONT):
    add(f'<rect x="{x0 + SAFE:.2f}" y="{Y0 + SAFE:.2f}" width="{PAGE_W - 2 * SAFE:.2f}" height="{PAGE_H - 2 * SAFE:.2f}" '
        f'fill="none" stroke="{NOTE}" stroke-width="0.25" stroke-dasharray="0.8 0.8"/>')
add(f'<path d="M{CX:.2f},{Y0:.2f} L{CX:.2f},{Y1:.2f}" stroke="{NOTE}" stroke-width="0.15" stroke-dasharray="0.5 1.5"/>')
nx = X_END + 2.0
note(X_BACK + 1, H - 0.8, f'обрез (зелёный) {PAGE_W}×{PAGE_H} мм на сторону; вылеты {BLEED} мм; пунктир — безопасное поле {SAFE} мм', size=2.0)
note(X_SPINE + SPINE / 2, 1.9, f'корешок {SPINE} мм — пересчитать', anchor='middle', size=1.9)
add('</g>')

# ---- notes on the front (separate layer)
add('<g inkscape:groupmode="layer" inkscape:label="Подписи схемы">')
labels = [
    (CX - 52, 18, CX - 30, 22, 'Лаурелин: золото', 'end'),
    (CX + 52, 18, CX + 30, 22, 'Тельперион: серебро', 'start'),
    (CX - 52, 33, CX - 34, 36, 'лента-надпись тенгваром', 'end'),
    (CX - 52, 52, CX - 26, 47, 'название: Arnold BocklinC', 'end'),
    (CX + 52, 108, lx + 3, ly - 8, 'феанорова лампа (calma)', 'start'),
    (CX - 52, 100, fx - 8, 104, 'Феанор', 'end'),
    (CX + 52, 132, fx + 15, 125, 'перо (quessë)', 'start'),
    (CX - 52, 143, fx - 9, 144, 'книга (parma)', 'end'),
    (CX + 52, 182, sx + 9, sy, 'звезда дома Феанора', 'start'),
]
for tx_, ty_, ax, ay, t, anchor in labels:
    tx2 = max(X_FRONT + 1.5, min(X_END - 1.5, tx_))
    leader(tx2 + (0.8 if anchor == 'start' else -0.8), ty_ - 0.8, ax, ay)
    add(f'<rect x="{(tx2 - len(t) * 1.25 if anchor == "end" else tx2) - 0.6:.2f}" y="{ty_ - 2.6:.2f}" '
        f'width="{len(t) * 1.25 + 1.2:.2f}" height="3.4" fill="#ffffff" opacity="0.85"/>')
    note(tx2, ty_, t, anchor=anchor, size=2.3)
add('</g>')

# palette swatches under the spine bottom
sw = [('тёмно-синий', NAVY), ('золото', GOLD), ('серебро', SILVER), ('красный задника', RED), ('огонь лампы', LAMP)]
add('<g inkscape:groupmode="layer" inkscape:label="Палитра">')
for i, (n, c) in enumerate(sw):
    x = X_BACK + 4 + i * 24
    add(f'<rect x="{x:.2f}" y="{Y1 - 13:.2f}" width="5" height="5" fill="{c}" stroke="{INK}" stroke-width="0.25"/>')
    add(f'<text x="{x + 6:.2f}" y="{Y1 - 9.6:.2f}" font-family="DejaVu Sans, sans-serif" font-size="2" fill="{INK}">{n}</text>')
add('</g>')

add('</svg>')
open(out, 'w', encoding='utf-8').write('\n'.join(parts))
print('W×H mm', round(W, 2), round(H, 2))
