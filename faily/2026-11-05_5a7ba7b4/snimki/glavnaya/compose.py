"""Front cover mockups over the generated illustration.
usage: compose.py GEN.png FONTDIR OUTDIR
A: title on the ribbon, subtitle in the blue field below
B: title large in the blue field, the ribbon kept for a tengwar inscription
"""
import sys, base64, os

gen, fontdir, outdir = sys.argv[1:4]
b64 = lambda fn: base64.b64encode(open(fn, 'rb').read()).decode()

BLEED, PAGE_W, PAGE_H = 3.0, 129.03, 198.12
FW, FH = PAGE_W + 2 * BLEED, PAGE_H + 2 * BLEED          # 135.03 × 204.12 mm
IW, IH = 1024, 1536
S = FH / IH                                             # mm per px: image fills the height
OX = (FW - IW * S) / 2                                  # negative: ~0.5 mm cropped at each side

GOLD, SILVER, RED, NAVY, INK = '#d9a520', '#e4e9ef', '#7a0000', '#16235f', '#111111'

def page(body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
 width="{FW:.2f}mm" height="{FH:.2f}mm" viewBox="0 0 {FW:.2f} {FH:.2f}">
<title>{title}</title>
<defs><style>
@font-face {{ font-family: 'Arnold BocklinC'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))}); }}
@font-face {{ font-family: 'Kurale'; src: url(data:font/ttf;base64,{b64(os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))}); }}
</style>
<path id="ribbon" d="M240,236 Q512,130 784,240"/>
</defs>
<g inkscape:groupmode="layer" inkscape:label="Иллюстрация">
<rect x="0" y="0" width="{FW:.2f}" height="{FH:.2f}" fill="{NAVY}"/>
<image x="{OX:.3f}" y="0" width="{IW * S:.3f}" height="{FH:.3f}" preserveAspectRatio="none"
 xlink:href="data:image/png;base64,{b64(gen)}"/>
</g>
<g inkscape:groupmode="layer" inkscape:label="Надписи" transform="translate({OX:.3f},0) scale({S:.6f})">
{body}
</g>
<g inkscape:groupmode="layer" inkscape:label="Разметка (скрыть)" style="display:inline">
<rect x="{BLEED}" y="{BLEED}" width="{PAGE_W}" height="{PAGE_H}" fill="none" stroke="#00c000" stroke-width="0.3"/>
<rect x="{BLEED + 6}" y="{BLEED + 6}" width="{PAGE_W - 12}" height="{PAGE_H - 12}" fill="none" stroke="#d4007a" stroke-width="0.25" stroke-dasharray="0.8 0.8"/>
</g>
</svg>'''

A = f'''<text font-family="Arnold BocklinC" font-size="56" fill="{RED}" text-anchor="middle">
<textPath xlink:href="#ribbon" startOffset="50%">Тенгварь</textPath></text>
<text x="512" y="352" font-family="Kurale" font-size="40" fill="{GOLD}" text-anchor="middle">в картинках и стихах</text>'''

B = f'''<text x="512" y="372" font-family="Arnold BocklinC" font-size="112" fill="{GOLD}" stroke="{INK}" stroke-width="3"
 paint-order="stroke" text-anchor="middle">Тенгварь</text>
<text x="512" y="440" font-family="Kurale" font-size="38" fill="{SILVER}" text-anchor="middle">в картинках и стихах</text>
<text font-family="Kurale" font-size="22" fill="{RED}" text-anchor="middle" opacity="0.55">
<textPath xlink:href="#ribbon" startOffset="50%">здесь — надпись тенгваром</textPath></text>'''

for name, body, t in (('A', A, 'Тенгварь — лицевая, вариант A'), ('B', B, 'Тенгварь — лицевая, вариант B')):
    open(os.path.join(outdir, f'front-{name}.svg'), 'w', encoding='utf-8').write(page(body, t))
print('mm per px', round(S, 5), 'crop each side mm', round(-OX, 2), 'needed px for 300 dpi',
      round(FW / 25.4 * 300), 'x', round(FH / 25.4 * 300))
