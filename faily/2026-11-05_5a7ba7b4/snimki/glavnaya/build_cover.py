"""Full cover of the Russian «Тенгварь»: back (from the translated cover PDF) + spine + front (generated art),
with 3 mm bleeds.
usage: build_cover.py FRONT_ART.png BACK_COVER.pdf FONTDIR OUT.pdf [SPINE_MM]
"""
import sys, os
import pymupdf as fz
from PIL import Image

art_fn, back_fn, fontdir, out_fn = sys.argv[1:5]
SPINE = float(sys.argv[5]) if len(sys.argv) > 5 else 6.94

MM = 72 / 25.4
BLEED, PAGE_W, PAGE_H = 3.0, 129.03, 198.12
W = 2 * PAGE_W + SPINE + 2 * BLEED
H = PAGE_H + 2 * BLEED
X_SPINE = BLEED + PAGE_W
X_FRONT = X_SPINE + SPINE

NAVY = (0x16 / 255, 0x23 / 255, 0x5f / 255)
GOLD = (0xd9 / 255, 0xa5 / 255, 0x20 / 255)
SILVER = (0xe4 / 255, 0xe9 / 255, 0xef / 255)
INK = (0.07, 0.07, 0.07)

doc = fz.open()
pg = doc.new_page(width=W * MM, height=H * MM)
R = lambda x0, y0, x1, y1: fz.Rect(x0 * MM, y0 * MM, x1 * MM, y1 * MM)

# ---- back: the translated back cover, vector; white bleed around it
src = fz.open(back_fn)
back_w_pt = PAGE_W * MM
pg.draw_rect(R(0, 0, X_SPINE, H), color=None, fill=(1, 1, 1))
pg.show_pdf_page(R(BLEED, BLEED, X_SPINE, BLEED + PAGE_H), src, 0,
                 clip=fz.Rect(0, 0, back_w_pt, src[0].rect.height))

# ---- spine and front background
pg.draw_rect(R(X_SPINE, 0, W, H), color=None, fill=NAVY)

# ---- front art: fills the height incl. bleeds; cut at the fold so nothing wraps onto the spine
art = Image.open(art_fn).convert('RGB')
iw, ih = art.size
s = H / ih                                   # mm per px
art_w_mm = iw * s
ox = (PAGE_W + 2 * BLEED - art_w_mm) / 2     # art left edge, relative to the front-with-bleeds box
cut_px = int(round((BLEED - ox) / s))        # pixels left of the fold
art_c = art.crop((cut_px, 0, iw, ih))
tmp = out_fn + '.front.png'
art_c.save(tmp)
x_art = X_FRONT + (cut_px * s + ox - BLEED)
pg.insert_image(R(x_art, 0, x_art + art_c.width * s, H), filename=tmp)
os.remove(tmp)

# ---- lettering (vector, real fonts)
boecklin = fz.Font(fontfile=os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))
kurale = fz.Font(fontfile=os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))
pg.insert_font(fontname='boe', fontbuffer=boecklin.buffer)
pg.insert_font(fontname='kur', fontbuffer=kurale.buffer)

def px2mm(px_x, px_y):
    """position in the generated art (px) -> page mm"""
    return X_FRONT - BLEED + ox + px_x * s, px_y * s

def centred(text, font, fname, size_pt, cx_mm, base_mm, color, stroke=None, rotate=0):
    w = font.text_length(text, fontsize=size_pt) / MM
    if rotate == 270:
        pt = fz.Point(cx_mm * MM, (base_mm - w / 2) * MM)
    else:
        pt = fz.Point((cx_mm - w / 2) * MM, base_mm * MM)
    if stroke:
        # outline behind the fill (like paint-order: stroke)
        pg.insert_text(pt, text, fontname=fname, fontsize=size_pt, render_mode=1, color=INK,
                       border_width=stroke / size_pt, rotate=rotate)
    pg.insert_text(pt, text, fontname=fname, fontsize=size_pt, color=color, fill=color, rotate=rotate)

cx, base = px2mm(512, 372)
centred('Тенгварь', boecklin, 'boe', 112 * s * MM, cx, base, GOLD, stroke=2 * 3 * s * MM)
cx, base = px2mm(512, 440)
centred('в картинках и стихах', kurale, 'kur', 38 * s * MM, cx, base, SILVER)

# ---- spine title, running downwards
centred('Тенгварь — стихи на квэнья', kurale, 'kur', 11, X_SPINE + SPINE / 2 - 1.35, H / 2, SILVER, rotate=270)

doc.set_metadata({'title': 'Тенгварь — обложка', 'creator': 'build_cover.py'})
doc.save(out_fn, garbage=3, deflate=True)
print('cover %.2f × %.2f mm; front art %d px wide → %.0f dpi; fold cut %d px' % (W, H, iw, iw / (art_w_mm / 25.4), cut_px))
