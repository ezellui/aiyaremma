"""rev. 0.10: pictures of the reading from the shuttle for the design document.
Usage: python3 -I readrender.py OUT_DIR (writes OUT_DIR/renders/read_*.png)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageOps
import params as P
import parts as PT
import scenarios as SC
import reader as RD
import geo, render

out = os.path.join(sys.argv[1], 'renders')
os.makedirs(out, exist_ok=True)


def objs(ps, clip=None):
    res = []
    for i, p in enumerate(ps):
        m = p.mesh if clip is None else p.mesh ^ clip
        if m.is_empty():
            continue
        V, F = geo.to_arrays(m)
        res.append((V, F, p.color, i))
    return res


def save(img, name):
    img = ImageOps.expand(img.crop(ImageOps.invert(img.convert('L')).getbbox()), 24, 'white')
    img.save(os.path.join(out, name + '.png'))
    return img


st = SC.cycle_state(145.0, 4, 5)                 # ext. ando read: feelers on their tabs
ps = PT.build(st)
keep = ('code comb', 'comb pin', 'reading', 'feeler', 'read cable end', 'shaft', 'guide rod', 'pulley and detent wheel')
sel = [p for p in ps if p.name.startswith(keep)]
img, _ = render.render(objs(sel), ((260, -300, 420), (10, -45, 250)), W=1800, H=1700)
save(img, 'read_head')

# section along the strike ray (a slab |x| < 1.2 mm), seen from +X
sl = geo.box(-1.2, 1.2, -140, 10, 120, 345)
keep2 = keep + ('shuttle', 'type block', 'shuttle bushing')
sel2 = [p for p in ps if p.name.startswith(keep2)]
img, _ = render.render(objs(sel2, clip=sl), ((600, -45, 240), (0, -45, 240)), W=1700, H=1900, light=(0.7, -0.3, 0.6))
save(img, 'read_cut')

# slides under the followers (sectors hold 7 and 7) and the read cam with its rocker
st2 = PT.State(frames={'B': 7.0, 'C': 7.0}, mem={'B': 7.0, 'C': 7.0}, cycle=145.0)
ps2 = PT.build(st2)
s1 = [p for p in ps2 if p.name.startswith(('read slide', 'memory sleeve', 'memory pawl', 'sector axis'))]
im1, _ = render.render(objs(s1, clip=geo.box(125, 175, -360, -280, -5, 100)), ((420, -560, 200), (150, -330, 40)), W=1400, H=1200)
s2 = [p for p in ps2 if p.name.startswith(('cam read', 'read rocker', 'cycle shaft'))]
im2, _ = render.render(objs(s2, clip=geo.box(40, 80, -60, 30, -5, 50)), ((300, -260, 160), (62, -12, 20)), W=1100, H=1200)
im1 = ImageOps.expand(im1.crop(ImageOps.invert(im1.convert('L')).getbbox()), 16, 'white')
im2 = ImageOps.expand(im2.crop(ImageOps.invert(im2.convert('L')).getbbox()), 16, 'white')
h = max(im1.height, im2.height)
both = Image.new('RGB', (im1.width + im2.width, h), 'white')
both.paste(im1, (0, (h - im1.height) // 2)); both.paste(im2, (im1.width, (h - im2.height) // 2))
both.save(os.path.join(out, 'read_slides.png'))

# a comb as printed (on its edge)
c = RD.comb_print_bed(4)
V, F = geo.to_arrays(c)
img, _ = render.render([(V, F, (200, 120, 160), 0)], ((60, -160, 140), (45, 0, 3)), W=1800, H=900)
save(img, 'read_comb')
print('renders done')
