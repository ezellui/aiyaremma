"""Gift-book cover: cloth binding with gold (and silver) stamping, the soft watercolour set into an arched window.
usage: build_cover_cloth.py ART.png ORIG_COVER.pdf COVER_TEXTS.json FONTDIR TENGWAR_FONT TENGWAR_TEXT OUT.pdf [SPINE_MM]
ART: the soft front (1024 × 1536); the window shows its upper part (trees, nimbus, Fëanor, crystal)."""
import sys, os, json, math, subprocess, tempfile
import numpy as np, cv2
import pymupdf as fz
from PIL import Image, ImageDraw

art_fn, orig_fn, texts_fn, fontdir, tfont, ttext, out_fn = sys.argv[1:8]
SPINE = float(sys.argv[8]) if len(sys.argv) > 8 else 6.94
MM = 72 / 25.4
BLEED, PAGE_W, PAGE_H = 3.0, 129.03, 198.12
W = 2 * PAGE_W + SPINE + 2 * BLEED
H = PAGE_H + 2 * BLEED
X_SPINE = BLEED + PAGE_W
X_FRONT = X_SPINE + SPINE
CX = X_FRONT + PAGE_W / 2                       # front centre line
hexc = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
CLOTH = hexc(os.environ.get('CLOTH', '#1d2747'))
GOLD, SILVER, RED, INK = hexc('#d2a64a'), hexc('#cfd5da'), hexc('#7a1a14'), hexc('#3a2616')
tmpd = tempfile.mkdtemp()

doc = fz.open(); pg = doc.new_page(width=W * MM, height=H * MM)
R = lambda x0, y0, x1, y1: fz.Rect(x0 * MM, y0 * MM, x1 * MM, y1 * MM)
P = lambda x, y: fz.Point(x * MM, y * MM)

# ------------------------------------------------------------ cloth
DPI = 220
cw, ch = int(W / 25.4 * DPI), int(H / 25.4 * DPI)
rng = np.random.default_rng(4)
base = np.array(CLOTH, np.float32) * 255
rows = rng.normal(0, 1, (ch, 1)).astype(np.float32)
cols = rng.normal(0, 1, (1, cw)).astype(np.float32)
yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
pitch = 2.6                                      # px per thread at 220 dpi (~0.3 mm)
weave = (np.sin(xx / pitch * math.pi) * np.sin(yy / pitch * math.pi)) * 2.2
threads = cv2.GaussianBlur(rows, (0, 0), 0.6) * 3.0 + cv2.GaussianBlur(cols, (0, 0), 0.6) * 3.0
mottle = cv2.GaussianBlur(rng.normal(0, 1, (ch, cw)).astype(np.float32), (0, 0), 35) * 60
grain = rng.normal(0, 2.2, (ch, cw)).astype(np.float32)
lum = weave + threads + mottle * 0.12 + grain
cloth = np.clip(base[None, None, :] + lum[..., None] * np.array([0.9, 1.0, 1.15]), 0, 255).astype(np.uint8)
Image.fromarray(cloth).save(os.path.join(tmpd, 'cloth.jpg'), quality=92)
pg.insert_image(R(0, 0, W, H), filename=os.path.join(tmpd, 'cloth.jpg'))

# ------------------------------------------------------------ the window with the watercolour
WIN_W, ARCH_R = 84.0, 42.0
Y_APEX, Y_BOT = 33.0, 147.0
Y_SPR = Y_APEX + ARCH_R                          # springing line of the arch
art = Image.open(art_fn).convert('RGB')
iw, ih = art.size
aspect = WIN_W / (Y_BOT - Y_APEX)
cx0, cx1 = 110, iw - 110
cw_px = cx1 - cx0; chh = int(cw_px / aspect)
cy0 = 80
crop = art.crop((cx0, cy0, cx1, cy0 + chh)).resize((int(WIN_W / 25.4 * 400), int((Y_BOT - Y_APEX) / 25.4 * 400)), Image.LANCZOS)
aw, ah = crop.size
mask = Image.new('L', (aw * 4, ah * 4), 0); d = ImageDraw.Draw(mask)
r4 = aw * 4 / 2
d.pieslice((0, 0, aw * 4 - 1, aw * 4 - 1), 180, 360, fill=255)
d.rectangle((0, r4, aw * 4 - 1, ah * 4 - 1), fill=255)
mask = mask.resize((aw, ah), Image.LANCZOS)
crop.putalpha(mask)
crop.save(os.path.join(tmpd, 'win.png'))
pg.insert_image(R(CX - WIN_W / 2, Y_APEX, CX + WIN_W / 2, Y_BOT), filename=os.path.join(tmpd, 'win.png'))

# ------------------------------------------------------------ stamping (vector)
def arch_path(sh, off):
    r = ARCH_R + off
    x0, x1 = CX - r, CX + r
    yb = Y_BOT + off
    sh.draw_line(P(x0, yb), P(x0, Y_SPR))
    k = 0.5523 * r
    sh.draw_bezier(P(x0, Y_SPR), P(x0, Y_SPR - k), P(CX - k, Y_SPR - r), P(CX, Y_SPR - r))
    sh.draw_bezier(P(CX, Y_SPR - r), P(CX + k, Y_SPR - r), P(x1, Y_SPR - k), P(x1, Y_SPR))
    sh.draw_line(P(x1, Y_SPR), P(x1, yb))
    sh.draw_line(P(x1, yb), P(x0, yb))

for off, wdt in ((1.4, 1.6), (3.0, 0.5)):
    sh = pg.new_shape(); arch_path(sh, off); sh.finish(color=GOLD, width=wdt, closePath=True); sh.commit()

def leaf(sh, x, y, ang, L, w):
    dx, dy = math.cos(ang), math.sin(ang); nx, ny = -dy, dx
    tip = (x + dx * L, y + dy * L)
    m = (x + dx * L * 0.45, y + dy * L * 0.45)
    sh.draw_bezier(P(x, y), P(m[0] + nx * w, m[1] + ny * w), P(tip[0] - dx * L * 0.2 + nx * w * 0.4, tip[1] - dy * L * 0.2 + ny * w * 0.4), P(*tip))
    sh.draw_bezier(P(*tip), P(tip[0] - dx * L * 0.2 - nx * w * 0.4, tip[1] - dy * L * 0.2 - ny * w * 0.4), P(m[0] - nx * w, m[1] - ny * w), P(x, y))

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * e for a, b, c, e in zip(p0, p1, p2, p3))

def vine(side, color):
    """a stem rising beside the window from its foot, leaves alternating, a curl at the top"""
    s = -1 if side == 'L' else 1
    xb = CX + s * (ARCH_R + 7.5)
    p0, p1, p2, p3 = (CX + s * (ARCH_R - 6), Y_BOT + 9), (xb + s * 6, Y_BOT + 4), (xb - s * 4, Y_SPR + 30), (xb + s * 1, Y_SPR - 6)
    pts = [bez(p0, p1, p2, p3, t / 200) for t in range(201)]
    sh = pg.new_shape()
    sh.draw_polyline([P(*q) for q in pts]); sh.finish(color=color, width=1.1, closePath=False); sh.commit()
    # curl
    cx_, cy_ = p3[0] - s * 2.6, p3[1]
    sh = pg.new_shape()
    curl = [(cx_ + s * 2.6 * (1 - a / 9) * math.cos(a), cy_ - 2.6 * (1 - a / 9) * math.sin(a)) for a in np.linspace(0, 1.6 * math.pi, 60)]
    sh.draw_polyline([P(*q) for q in curl]); sh.finish(color=color, width=0.9, closePath=False); sh.commit()
    sh = pg.new_shape()
    for i, t in enumerate(np.linspace(0.12, 0.92, 11)):
        x, y = bez(p0, p1, p2, p3, t)
        x2, y2 = bez(p0, p1, p2, p3, t + 0.01)
        tang = math.atan2(y2 - y, x2 - x)
        side_ = 1 if i % 2 == 0 else -1
        L = 6.2 - 2.2 * t
        leaf(sh, x, y, tang + side_ * 0.95, L, L * 0.32)
    sh.finish(color=None, fill=color, closePath=True); sh.commit()
    # blossoms / drops
    sh = pg.new_shape()
    for t in (0.3, 0.62):
        x, y = bez(p0, p1, p2, p3, t)
        sh.draw_circle(P(x + s * 2.4, y + 1.5), 0.75 * MM)
    sh.finish(color=None, fill=color); sh.commit()

vine('L', GOLD)
vine('R', SILVER)

# outer double rule with corner rosettes
I0 = 7.5
def rect_rule(x0, y0, x1, y1, wdt):
    sh = pg.new_shape(); sh.draw_rect(R(x0, y0, x1, y1)); sh.finish(color=GOLD, width=wdt); sh.commit()
fx0, fy0, fx1, fy1 = X_FRONT + I0, BLEED + I0, X_FRONT + PAGE_W - I0, BLEED + PAGE_H - I0
rect_rule(fx0, fy0, fx1, fy1, 1.2)
rect_rule(fx0 + 1.6, fy0 + 1.6, fx1 - 1.6, fy1 - 1.6, 0.4)
def rosette(x, y, r=2.0, color=GOLD):
    sh = pg.new_shape()
    for k in range(8):
        a = k * math.pi / 4
        leaf(sh, x, y, a, r * 1.6, r * 0.5)
    sh.finish(color=None, fill=color, closePath=True); sh.commit()
    sh = pg.new_shape(); sh.draw_circle(P(x, y), r * 0.45 * MM); sh.finish(color=CLOTH, fill=color, width=0.4); sh.commit()
for x, y in ((fx0, fy0), (fx1, fy0), (fx0, fy1), (fx1, fy1)):
    sh = pg.new_shape(); sh.draw_rect(R(x - 3.2, y - 3.2, x + 3.2, y + 3.2)); sh.finish(color=None, fill=CLOTH); sh.commit()
    rosette(x, y, 1.8)

# tengwar around the arch
svgf = os.path.join(tmpd, 'ring.svgf')
R_T = ARCH_R + 6.3
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tengwar', 'inscribe.py'),
                tfont, ttext, '6.6', 'arc:%.3f,%.3f,%.3f,198,342' % (CX, Y_SPR, R_T), '0', '#d2a64a', svgf],
               check=True, env=dict(os.environ, TRACK='0.10'), capture_output=True)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%.3fmm" height="%.3fmm" viewBox="0 0 %.3f %.3f">%s</svg>'
       % (W, H, W, H, open(svgf).read())).encode()
ring = fz.open(stream=fz.open(stream=svg, filetype='svg').convert_to_pdf(), filetype='pdf')
pg.show_pdf_page(R(0, 0, W, H), ring, 0)

# lettering
boe = fz.Font(fontfile=os.path.join(fontdir, 'arnold-bocklinc/Arnold BocklinC.ttf'))
kur = fz.Font(fontfile=os.path.join(fontdir, 'kurale/Kurale-Regular.ttf'))
und = fz.Font(fontfile=os.path.join(fontdir, 'underdog/Underdog-Regular.ttf'))
for n, f in (('boe', boe), ('kur', kur), ('und', und)):
    pg.insert_font(fontname=n, fontbuffer=f.buffer)
def centred(text, font, fname, size, cx, base, color, rotate=0):
    w = font.text_length(text, fontsize=size) / MM
    pg.insert_text(P(cx - w / 2, base), text, fontname=fname, fontsize=size, color=color)
TITLE = os.environ.get('TITLE', 'Тенгварь'); SUB = os.environ.get('SUBTITLE', 'в картинках и стихах')
ts = 88 / (boe.text_length(TITLE, fontsize=1) / MM)        # 88 mm wide
centred(TITLE, boe, 'boe', ts, CX, 177.5, GOLD)
centred(SUB, kur, 'kur', 11.5, CX, 187.5, GOLD)
# small fleuron between window and title
sh = pg.new_shape()
sh.draw_line(P(CX - 14, Y_BOT + 8.5), P(CX - 3, Y_BOT + 8.5)); sh.draw_line(P(CX + 3, Y_BOT + 8.5), P(CX + 14, Y_BOT + 8.5))
sh.finish(color=GOLD, width=0.6); sh.commit()
rosette(CX, Y_BOT + 8.5, 1.3)

# ------------------------------------------------------------ spine
orig = fz.open(orig_fn)[0]
def replay(drawing, color, scale, ox, oy):
    sh = pg.new_shape()
    T = lambda p: fz.Point(ox + (p.x - drawing['rect'].x0) * scale, oy + (p.y - drawing['rect'].y0) * scale)
    for it in drawing['items']:
        if it[0] == 'l': sh.draw_line(T(it[1]), T(it[2]))
        elif it[0] == 'c': sh.draw_bezier(T(it[1]), T(it[2]), T(it[3]), T(it[4]))
    sh.finish(color=None, fill=color, even_odd=bool(drawing.get('even_odd')), closePath=True); sh.commit()
orn = [d_ for d_ in orig.get_drawings() if d_.get('fill') and d_['fill'][1] == 0 and d_['rect'].x1 < 400]
back_orn = [d_ for d_ in orn if d_['rect'].x1 < 300][0]
spine_orn = [d_ for d_ in orn if d_['rect'].x0 > 300][0]
sw = SPINE * MM
so = spine_orn['rect']
k = min(1.0, (sw - 2.5) / so.width)
for y in (BLEED + 6, BLEED + 7.2, BLEED + PAGE_H - 6, BLEED + PAGE_H - 7.2):     # bands, as on a bound spine
    sh = pg.new_shape(); sh.draw_line(P(X_SPINE + 0.8, y), P(X_FRONT - 0.8, y)); sh.finish(color=GOLD, width=0.5); sh.commit()
replay(spine_orn, GOLD, k, X_SPINE * MM + (sw - so.width * k) / 2, (BLEED + 10) * MM)
units = {u['id']: u for u in json.load(open(texts_fn, encoding='utf-8'))['units']}
def ru(uid):
    r_ = units[uid]['ru'] or units[uid]['en']
    t = r_[0] if isinstance(r_, list) else r_
    t = t.replace(' - ', ' — ')
    return t[:-2] + ' —' if t.endswith(' -') else t
SPINE_T = os.environ.get('SPINE_TEXT', ru('p001-d01'))
pg.insert_text(fz.Point(X_SPINE * MM + sw / 2 - 11 * 0.33, (BLEED + 10) * MM + so.height * k + 7), SPINE_T,
               fontname='kur', fontsize=11, color=GOLD, rotate=270)

# ------------------------------------------------------------ back: parchment plaque on the cloth
bp = lambda x, y: fz.Point(x + BLEED * MM, y + BLEED * MM)          # original back-cover pt → page
pl = fz.Rect(bp(26, 24), bp(340, 482))
pw_, ph_ = int(pl.width / 72 * 300), int(pl.height / 72 * 300)
xs = np.linspace(0, 1, pw_)[None, :, None]
c0, c1 = np.array([245, 230, 200]), np.array([250, 240, 220])
par = (c0 + (c1 - c0) * xs ** 0.8) * np.ones((ph_, 1, 1))
par += cv2.GaussianBlur(rng.normal(0, 1, (ph_, pw_)).astype(np.float32), (0, 0), 25)[..., None] * 40 + rng.normal(0, 1.5, (ph_, pw_, 1))
par = Image.fromarray(np.clip(par, 0, 255).astype(np.uint8))
m = Image.new('L', (pw_, ph_), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw_ - 1, ph_ - 1), radius=int(pw_ * 0.04), fill=255)
par.putalpha(m); par.save(os.path.join(tmpd, 'par.png'))
pg.insert_image(pl, filename=os.path.join(tmpd, 'par.png'))
sh = pg.new_shape(); sh.draw_rect(fz.Rect(pl.x0 - 4, pl.y0 - 4, pl.x1 + 4, pl.y1 + 4), radius=0.045); sh.finish(color=GOLD, width=1.2); sh.commit()
sh = pg.new_shape(); sh.draw_rect(fz.Rect(pl.x0 - 7, pl.y0 - 7, pl.x1 + 7, pl.y1 + 7), radius=0.05); sh.finish(color=GOLD, width=0.4); sh.commit()
replay(back_orn, RED, 1.0, BLEED * MM + back_orn['rect'].x0, BLEED * MM + back_orn['rect'].y0 + 6)
spans = [s for b in orig.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['text'].strip() and s['bbox'][0] < 300]
NOTEXT = os.environ.get('NOTEXT') == '1'
if not NOTEXT:
    title_span = [s for s in spans if s['size'] > 20][0]
    pg.insert_text(bp(*title_span['origin']), ru('p001-d02'), fontname='kur', fontsize=24, color=RED)
    for i, s in enumerate([s for s in spans if s['font'] == 'Grasshopper']):
        pg.insert_text(bp(*s['origin']), ru('p001-d%02d' % (i + 3)), fontname='und', fontsize=12, color=INK)
# a small rosette under the plaque
rosette(BLEED + PAGE_W / 2, (pl.y1 + 7) / MM + 7.5, 1.6)

doc.set_metadata({'title': 'Тенгварь — обложка', 'creator': 'build_cover_cloth.py'})
doc.save(out_fn, garbage=3, deflate=True)
print('cloth cover %.2f × %.2f mm' % (W, H))
