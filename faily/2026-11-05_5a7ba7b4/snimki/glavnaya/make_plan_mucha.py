"""Composition plan for the front cover in Mucha's manner, in the generation's own pixels (1024 × 1536, 2:3).
usage: make_plan_mucha.py FONTDIR OUTDIR
writes mucha-plan.svg (with notes) and mucha-plan-clean.svg (blocks only, to attach to the generation)"""
import sys, os, base64, math

fontdir, outdir = sys.argv[1:3]
W, H = 1024, 1536
# trim box inside the generated picture (cover 135.03 × 204.12 mm incl. bleed → 3 mm ≈ 22.6 px)
B = 22.6
SAFE = B + 45                                     # ~6 mm from trim: nothing important outside
DISK = (512, 610, 330)                           # cx, cy, r: the round ornamental disk
RING = (290, 330)                                # band of the disk left plain for the tengwar ring
PLAQUE = (130, 1250, 894, 1450)                  # title plaque
DESK_Y = 1010
LAMP = (640, 800, 760, 1010)
TREE_L, TREE_R = (30, 190), (834, 994)

b64 = lambda fn: base64.b64encode(open(fn, 'rb').read()).decode()
col = dict(bg='#2c3e57', disk='#c9b27c', ring='#e8dcc0', plaque='#e8dcc0', fig='#8a5a44', desk='#6b4a33',
           lamp='#bfe6ff', gold='#c9a043', silver='#c9d3dc', night='#3a4f6e')

def svg(notes):
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    o.append(f'''<defs><style>
@font-face {{ font-family: 'Arnold BocklinC'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))}); }}
@font-face {{ font-family: 'Kurale'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))}); }}
.n {{ font-family: sans-serif; font-size: 22px; fill: #fff; stroke: #000; stroke-width: 3px; paint-order: stroke; }}
</style></defs>''')
    o.append(f'<rect width="{W}" height="{H}" fill="{col["bg"]}"/>')
    # night sky glimpses between the trees
    o.append(f'<rect x="{TREE_L[1]}" y="0" width="{TREE_R[0] - TREE_L[1]}" height="{DESK_Y}" fill="{col["night"]}"/>')
    # the disk with its plain ring
    cx, cy, r = DISK
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col["disk"]}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{(RING[0] + RING[1]) / 2}" fill="none" stroke="{col["ring"]}" stroke-width="{RING[1] - RING[0]}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{RING[0] - 8}" fill="none" stroke="{col["gold"]}" stroke-width="6"/>')
    # the two trees: trunks as side columns, crowns arching over the disk
    for (x0, x1), c in ((TREE_L, col['gold']), (TREE_R, col['silver'])):
        o.append(f'<rect x="{(x0 + x1) / 2 - 28}" y="120" width="56" height="{H - 120}" fill="{c}" opacity="0.95"/>')
    o.append(f'<path d="M110,330 C110,40 420,20 512,150 C604,20 914,40 914,330 L860,330 C860,110 620,110 512,230 C404,110 164,110 164,330 Z" '
             f'fill="url(#g)" opacity="0.95"/>')
    o.insert(2, f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{col["gold"]}"/>'
                f'<stop offset="0.5" stop-color="#e7d7a8"/><stop offset="1" stop-color="{col["silver"]}"/></linearGradient></defs>')
    # Fëanor seated, writing; desk; lamp
    o.append(f'<path d="M420,420 C470,380 560,390 590,450 C610,520 600,560 620,620 C700,700 720,820 700,{DESK_Y} '
             f'L360,{DESK_Y} C340,860 350,700 420,640 C400,560 390,480 420,420 Z" fill="{col["fig"]}"/>')
    o.append(f'<rect x="230" y="{DESK_Y}" width="564" height="150" rx="10" fill="{col["desk"]}"/>')
    lx0, ly0, lx1, ly1 = LAMP
    o.append(f'<polygon points="{(lx0 + lx1) / 2},{ly0} {lx1},{ly0 + 110} {(lx0 + lx1) / 2},{ly1} {lx0},{ly0 + 110}" fill="{col["lamp"]}"/>')
    o.append(f'<circle cx="{(lx0 + lx1) / 2}" cy="{ly0 + 100}" r="120" fill="{col["lamp"]}" opacity="0.25"/>')
    # title plaque
    px0, py0, px1, py1 = PLAQUE
    o.append(f'<path d="M{px0},{py0 + 40} Q{px0},{py0} {px0 + 40},{py0} L{px1 - 40},{py0} Q{px1},{py0} {px1},{py0 + 40} '
             f'L{px1},{py1 - 40} Q{px1},{py1} {px1 - 40},{py1} L{px0 + 40},{py1} Q{px0},{py1} {px0},{py1 - 40} Z" '
             f'fill="{col["plaque"]}" stroke="{col["gold"]}" stroke-width="8"/>')
    if notes:
        o.append(f'<text x="512" y="{py0 + 115}" font-family="Arnold BocklinC" font-size="112" fill="#7a0000" text-anchor="middle">Тенгварь</text>')
        o.append(f'<text x="512" y="{py0 + 170}" font-family="Kurale" font-size="38" fill="#3a2a1a" text-anchor="middle">в картинках и стихах</text>')
        # tengwar ring hint
        o.append(f'<path id="ringp" d="M{cx - (RING[0] + RING[1]) / 2},{cy} a{(RING[0] + RING[1]) / 2},{(RING[0] + RING[1]) / 2} 0 1,1 {RING[0] + RING[1]},0" fill="none"/>')
        o.append(f'<text font-family="serif" font-size="26" fill="#7a0000"><textPath href="#ringp" startOffset="50%" text-anchor="middle">· надпись тенгваром «tengwasse Fëanáro» по кольцу — ставлю вектором ·</textPath></text>')
        o.append(f'<rect x="{B}" y="{B}" width="{W - 2 * B}" height="{H - 2 * B}" fill="none" stroke="#00c000" stroke-width="3"/>')
        o.append(f'<rect x="{SAFE}" y="{SAFE}" width="{W - 2 * SAFE}" height="{H - 2 * SAFE}" fill="none" stroke="#ff2aa0" stroke-width="2" stroke-dasharray="10 8"/>')
        for x, y, t in ((40, 90, 'Лаурелин (золото) — левая колонна'), (560, 90, 'Тельперион (серебро) — правая'),
                        (330, 940, 'Феанор пишет'), (600, 780, 'хрустальная лампа'),
                        (250, 1200, 'стол / книга'), (150, 1240, 'плашка названия: пустая, текст ставлю вектором'),
                        (40, 1520, 'зелёная — обрез, розовая — безопасная зона')):
            o.append(f'<text class="n" x="{x}" y="{y}">{t}</text>')
    o.append('</svg>')
    return '\n'.join(o)

open(os.path.join(outdir, 'mucha-plan.svg'), 'w', encoding='utf-8').write(svg(True))
open(os.path.join(outdir, 'mucha-plan-clean.svg'), 'w', encoding='utf-8').write(svg(False))
print('disk', DISK, 'ring', RING, 'plaque', PLAQUE)
