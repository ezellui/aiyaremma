"""Full cover of the Russian «Тенгварь» with the back redrawn in the front's night palette.
usage: build_cover2.py FRONT_ART.png ORIG_COVER.pdf COVER_TEXTS.json FONTDIR OUT.pdf STYLE [SPINE_MM] [INSCRIPTION.svgf]
  STYLE: night     — navy back, gold ornament and frame, light text
         parchment — navy back with the cream page (gold-rimmed) carrying the poem, red ornament
"""
import sys, os, json, math, random
import pymupdf as fz
from PIL import Image
import numpy as np

art_fn, orig_fn, texts_fn, fontdir, out_fn, STYLE = sys.argv[1:7]
SPINE = float(sys.argv[7]) if len(sys.argv) > 7 else 6.94
INSCRIPTION = sys.argv[8] if len(sys.argv) > 8 else None

MM = 72 / 25.4
BLEED, PAGE_W, PAGE_H = 3.0, 129.03, 198.12
W = 2 * PAGE_W + SPINE + 2 * BLEED
H = PAGE_H + 2 * BLEED
X_SPINE = BLEED + PAGE_W
X_FRONT = X_SPINE + SPINE

hexc = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
NAVY, GOLD, SILVER, RED = hexc('#16235f'), hexc('#d9a520'), hexc('#e4e9ef'), hexc('#7a0000')
CREAM_TEXT = hexc('#f3ead8')
INK = (0.07, 0.07, 0.07)

doc = fz.open()
pg = doc.new_page(width=W * MM, height=H * MM)
R = lambda x0, y0, x1, y1: fz.Rect(x0 * MM, y0 * MM, x1 * MM, y1 * MM)
orig = fz.open(orig_fn)[0]

def back_pt(x, y):
    """original back-cover point (pt, no bleed) -> this page (pt)"""
    return fz.Point(x + BLEED * MM, y + BLEED * MM)

# ---------------------------------------------------------------- background: one night sky, back to front
pg.draw_rect(R(0, 0, W, H), color=None, fill=NAVY)

def star4(cx, cy, r, color):
    pts = []
    for i in range(8):
        a = math.radians(-90 + i * 45)
        rr = r if i % 2 == 0 else r * 0.28
        pts.append(fz.Point(cx + rr * math.cos(a), cy + rr * math.sin(a)))
    sh = pg.new_shape(); sh.draw_polyline(pts + [pts[0]]); sh.finish(color=None, fill=color, closePath=True); sh.commit()

# a few stars on the back, away from the text block and the ornament (front has its own)
rng = random.Random(7)
txt_box = fz.Rect(back_pt(100, 95), back_pt(300, 445))
orn_box = fz.Rect(back_pt(30, 20), back_pt(85, 460))
placed = 0
while placed < 22:
    x = rng.uniform(8, X_SPINE * MM - 8); y = rng.uniform(8, H * MM - 8)
    p = fz.Point(x, y)
    if STYLE == 'parchment' and fz.Rect(back_pt(14, 14), back_pt(353, 548)).contains(p):
        continue
    if txt_box.contains(p) or orn_box.contains(p):
        continue
    star4(x, y, rng.uniform(1.6, 3.0), SILVER)
    placed += 1

# ---------------------------------------------------------------- the page / frame of the back
panel = fz.Rect(back_pt(22, 22), back_pt(345, 540))
rad = 0.06
if STYLE == 'parchment':
    # cream gradient page like the original, rimmed in gold
    pw, ph = int(panel.width * 4), int(panel.height * 4)
    xs = np.linspace(0, 1, pw)[None, :, None]
    c0, c1 = np.array([255, 237, 207]), np.array([255, 251, 246])
    img = (c0 + (c1 - c0) * xs ** 0.8) * np.ones((ph, 1, 1))
    tmp = out_fn + '.panel.png'
    Image.fromarray(img.astype(np.uint8)).save(tmp)
    sh = pg.new_shape(); sh.draw_rect(panel, radius=rad); sh.finish(color=None, fill=(1, 1, 1)); sh.commit()
    pg.insert_image(panel, filename=tmp)       # square image ...
    os.remove(tmp)
    # ... rounded by navy corner masks
    r = rad * min(panel.width, panel.height)
    for cx, cy, sx, sy in ((panel.x0, panel.y0, 1, 1), (panel.x1, panel.y0, -1, 1),
                           (panel.x0, panel.y1, 1, -1), (panel.x1, panel.y1, -1, -1)):
        sh = pg.new_shape()
        sh.draw_polyline([fz.Point(cx, cy), fz.Point(cx + sx * r, cy)])
        sh.draw_curve(fz.Point(cx + sx * r, cy), fz.Point(cx, cy), fz.Point(cx, cy + sy * r))
        sh.draw_line(fz.Point(cx, cy + sy * r), fz.Point(cx, cy))
        sh.finish(color=None, fill=NAVY, closePath=True); sh.commit()
    sh = pg.new_shape(); sh.draw_rect(panel, radius=rad); sh.finish(color=GOLD, width=1.6, fill=None); sh.commit()
    sh = pg.new_shape(); sh.draw_rect(fz.Rect(panel.x0 + 4, panel.y0 + 4, panel.x1 - 4, panel.y1 - 4), radius=rad * 0.9)
    sh.finish(color=RED, width=0.6, fill=None); sh.commit()
    ORN, TITLE, POEM = RED, INK, INK
else:
    sh = pg.new_shape(); sh.draw_rect(panel, radius=rad); sh.finish(color=GOLD, width=1.4, fill=None); sh.commit()
    ORN, TITLE, POEM = GOLD, GOLD, CREAM_TEXT

# ---------------------------------------------------------------- the ornament (vector, recoloured)
def replay(drawing, dx, dy, color, scale=1.0, ox=0.0, oy=0.0):
    sh = pg.new_shape()
    T = lambda p: fz.Point(ox + (p.x - drawing['rect'].x0) * scale + dx, oy + (p.y - drawing['rect'].y0) * scale + dy)
    for it in drawing['items']:
        if it[0] == 'l':
            sh.draw_line(T(it[1]), T(it[2]))
        elif it[0] == 'c':
            sh.draw_bezier(T(it[1]), T(it[2]), T(it[3]), T(it[4]))
        elif it[0] == 're':
            r_ = it[1]; sh.draw_rect(fz.Rect(T(r_.tl), T(r_.br)))
    sh.finish(color=None, fill=color, even_odd=bool(drawing.get('even_odd')), closePath=True)
    sh.commit()

orn = [d for d in orig.get_drawings() if d.get('fill') and d['fill'][1] == 0 and d['rect'].x1 < 400]
back_orn = [d for d in orn if d['rect'].x1 < 300][0]
spine_orn = [d for d in orn if d['rect'].x0 > 300][0]
replay(back_orn, BLEED * MM, BLEED * MM, ORN, ox=back_orn['rect'].x0, oy=back_orn['rect'].y0)

# ---------------------------------------------------------------- text of the back
underdog = fz.Font(fontfile=os.path.join(fontdir, 'underdog/Underdog-Regular.ttf'))
kurale = fz.Font(fontfile=os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))
boecklin = fz.Font(fontfile=os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))
pg.insert_font(fontname='und', fontbuffer=underdog.buffer)
pg.insert_font(fontname='kur', fontbuffer=kurale.buffer)
pg.insert_font(fontname='boe', fontbuffer=boecklin.buffer)

units = {u['id']: u for u in json.load(open(texts_fn, encoding='utf-8'))['units']}
def ru(uid):
    r = units[uid]['ru'] or units[uid]['en']
    t = r[0] if isinstance(r, list) else r
    return t.replace(' - ', ' — ')
spans = [s for b in orig.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']
         if s['text'].strip() and s['bbox'][0] < 300]
title_span = [s for s in spans if s['size'] > 20][0]
pg.insert_text(back_pt(*title_span['origin']), ru('p001-d02'), fontname='kur', fontsize=24, color=TITLE)
poem_spans = [s for s in spans if s['font'] == 'Grasshopper']
for i, s in enumerate(poem_spans):
    pg.insert_text(back_pt(*s['origin']), ru('p001-d%02d' % (i + 3)), fontname='und', fontsize=12, color=POEM)

# ---------------------------------------------------------------- spine: ornament on top, title below it
sw = SPINE * MM
so = spine_orn['rect']
k = min(1.0, (sw - 2.5) / so.width)
x_sp = X_SPINE * MM + (sw - so.width * k) / 2
replay(spine_orn, 0, 0, GOLD, scale=k, ox=x_sp, oy=(BLEED * MM + so.y0))
title_sp = ru('p001-d01')
fs = 11
tw = kurale.text_length(title_sp, fontsize=fs)
y_start = BLEED * MM + so.y0 + so.height * k + 6
pg.insert_text(fz.Point(X_SPINE * MM + sw / 2 - fs * 0.33, y_start), title_sp, fontname='kur', fontsize=fs,
               color=SILVER, rotate=270)

# ---------------------------------------------------------------- front: art, inscription, lettering
art = Image.open(art_fn).convert('RGB')
iw, ih = art.size
s = H / ih
art_w_mm = iw * s
ox = (PAGE_W + 2 * BLEED - art_w_mm) / 2
cut_px = int(round((BLEED - ox) / s))
art_c = art.crop((cut_px, 0, iw, ih))
tmp = out_fn + '.front.png'
art_c.save(tmp)
x_art = X_FRONT + (cut_px * s + ox - BLEED)
pg.insert_image(R(x_art, 0, x_art + art_c.width * s, H), filename=tmp)
os.remove(tmp)

if INSCRIPTION:
    frag = open(INSCRIPTION).read()
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>'
           % (iw, ih, iw, ih, frag)).encode()
    ins = fz.open(stream=fz.open(stream=svg, filetype='svg').convert_to_pdf(), filetype='pdf')
    x_full = X_FRONT - BLEED + ox
    pg.show_pdf_page(R(x_full, 0, x_full + art_w_mm, H), ins, 0)

def px2mm(px_x, px_y):
    return X_FRONT - BLEED + ox + px_x * s, px_y * s

def centred(text, font, fname, size_pt, cx_mm, base_mm, color, stroke=None):
    w = font.text_length(text, fontsize=size_pt) / MM
    pt = fz.Point((cx_mm - w / 2) * MM, base_mm * MM)
    if stroke:
        pg.insert_text(pt, text, fontname=fname, fontsize=size_pt, render_mode=1, color=INK, border_width=stroke / size_pt)
    pg.insert_text(pt, text, fontname=fname, fontsize=size_pt, color=color)

cx, base = px2mm(512, 372)
centred('Тенгварь', boecklin, 'boe', 112 * s * MM, cx, base, GOLD, stroke=2 * 3 * s * MM)
cx, base = px2mm(512, 440)
centred('в картинках и стихах', kurale, 'kur', 38 * s * MM, cx, base, SILVER)

doc.set_metadata({'title': 'Тенгварь — обложка', 'creator': 'build_cover2.py'})
doc.save(out_fn, garbage=3, deflate=True)
print('cover %.2f × %.2f mm, back style %s' % (W, H, STYLE))
