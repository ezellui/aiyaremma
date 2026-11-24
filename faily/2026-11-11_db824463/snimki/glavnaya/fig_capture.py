#!/usr/bin/env python3
"""fig_capture.py OUTDIR [--start-screen N] [--max-screens N]
Pass B by screen: Folio shows the "records with hits" view of the figure query (Graphics | Tables |
Music) with the bitmaps drawn correctly; printing them crashes Folio on some records and loses the
palette. So the view is paged through with PageDown and every screen is cut:
  * a figure = the image right of a hit-highlighted descriptor box (the Graphics field text);
  * the record markers (hidden text, red, left margin) are noted with their position.
Successive screens are stitched by finding the scroll shift, so each figure is taken once, in
document order. Output: OUTDIR/img/<md5>.png and OUTDIR/figs.jsonl, one line per event:
  {"kind":"rec","y":Y}  or  {"kind":"fig","y":Y,"x":X,"img":..,"w":..,"h":..,"box":[w,h]}
with Y the position in the stitched document (pixels)."""
import sys, os, io, json, hashlib, subprocess, time
import numpy as np
from PIL import Image
from scipy import ndimage

DISPLAY = os.environ.get('DISPLAY', ':97')
X0, X1, Y0, Y1 = 60, 1250, 84, 960          # the document area of the window
HL = np.array([48, 150, 250])               # hit highlight


def shot():
    png = subprocess.run(['import', '-window', 'root', 'png:-'], capture_output=True,
                         env=dict(os.environ, DISPLAY=DISPLAY)).stdout
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))[Y0:Y1, X0:X1].copy()


def key(k):
    subprocess.run(['xdotool', 'key', k], env=dict(os.environ, DISPLAY=DISPLAY))


def settle(prev=None):
    """wait until two screenshots agree"""
    a = shot()
    for _ in range(40):
        time.sleep(0.4)
        b = shot()
        if np.array_equal(a, b):
            return b
        a = b
    return a


def find_shift(old, new):
    """rows of `old` reappear `s` pixels higher in `new`; returns s (0 = no movement, None = unknown)"""
    ho = [hash(r.tobytes()) for r in old]
    hn = [hash(r.tobytes()) for r in new]
    blank = hash(np.full_like(old[0], 255).tobytes())
    idx = {}
    for y, h in enumerate(hn):
        if h != blank:
            idx.setdefault(h, []).append(y)
    votes = {}
    for y, h in enumerate(ho):
        if h == blank:
            continue
        for y2 in idx.get(h, ()):
            votes[y - y2] = votes.get(y - y2, 0) + 1
    if not votes:
        return None
    s, n = max(votes.items(), key=lambda kv: kv[1])
    return s if n >= 20 else None


def markers(a):
    """y of record markers: reddish pixels in the left margin"""
    m = a[:, 20:70].astype(int)
    red = (m[..., 0] > 200) & (m[..., 0] - m[..., 1] > 40) & (m[..., 0] - m[..., 2] > 40)
    rows = np.where(red.any(axis=1))[0]
    out = []
    for y in rows:
        if not out or y - out[-1][1] > 3:
            out.append([y, y])
        else:
            out[-1][1] = y
    return [(a_, b_) for a_, b_ in out]


def figures(a):
    """(box, crop-rect) for every highlight box with an image to its right"""
    hl = np.all(a == HL, axis=2)
    lab, n = ndimage.label(hl)
    boxes = [s for s in ndimage.find_objects(lab)]
    boxes = [(s[0].start, s[0].stop, s[1].start, s[1].stop) for s in boxes]
    boxes = [b for b in boxes if b[1] - b[0] >= 8 and b[3] - b[2] >= 15]
    white = np.all(a >= 245, axis=2) | hl
    out = []
    for (y0, y1, x0, x1) in boxes:
        lim = min([b[2] for b in boxes if b[2] >= x1 and b[0] < y1 and b[1] > y0] + [a.shape[1]])
        band = ~white[y0:y1, x1:lim]
        cols = band.any(axis=0)
        xs = np.where(cols)[0]
        if not len(xs) or xs[0] > 30:
            out.append(((y0, y1, x0, x1), None)); continue
        start = xs[0]; end = start; gap = 0
        for x in range(start, len(cols)):
            if cols[x]:
                end = x; gap = 0
            else:
                gap += 1
                if gap >= 8:
                    break
        sub = band[:, start:end + 1]
        rr = np.where(sub.any(axis=1))[0]
        if not len(rr) or rr[-1] - rr[0] < 5:
            out.append(((y0, y1, x0, x1), None)); continue
        out.append(((y0, y1, x0, x1), (y0 + rr[0], y0 + rr[-1] + 1, x1 + start, x1 + end + 1)))
    return out


def main():
    outdir = sys.argv[1]
    max_screens = int(sys.argv[sys.argv.index('--max-screens') + 1]) if '--max-screens' in sys.argv else 100000
    os.makedirs(os.path.join(outdir, 'img'), exist_ok=True)
    log = open(os.path.join(outdir, 'figs.jsonl'), 'a')
    key('ctrl+Home'); time.sleep(2)
    a = settle()
    top = 0                    # document y of screen row 0
    done_y = -1                # everything above this document y has been taken
    seen_rec = set()
    for screen in range(max_screens):
        H = a.shape[0]
        safe = H - 2           # rows below may be cut off
        # boxes touching the bottom edge are left for the next screen
        figs = figures(a)
        cut = min([b[0] for b, _ in figs if b[1] >= safe] + [safe])
        evs = []
        for (y0, y1) in markers(a):
            Y = top + y0
            if y1 < cut and Y > done_y and Y not in seen_rec:
                evs.append((Y, {'kind': 'rec', 'y': Y}))
        for b, c in figs:
            Y = top + b[0]
            if b[1] >= cut or Y <= done_y:
                continue
            if c is None:
                evs.append((Y, {'kind': 'fig', 'y': Y, 'x': int(b[3]), 'img': None, 'box': [int(b[3] - b[2]), int(b[1] - b[0])]}))
                continue
            crop = a[c[0]:c[1], c[2]:c[3]]
            buf = io.BytesIO(); Image.fromarray(crop).save(buf, 'PNG'); png = buf.getvalue()
            name = hashlib.md5(png).hexdigest()[:16] + '.png'
            p = os.path.join(outdir, 'img', name)
            if not os.path.exists(p):
                open(p, 'wb').write(png)
            evs.append((Y, {'kind': 'fig', 'y': Y, 'x': int(c[2]), 'img': name, 'w': int(c[3] - c[2]),
                            'h': int(c[1] - c[0]), 'box': [int(b[3] - b[2]), int(b[1] - b[0])]}))
        evs.sort(key=lambda e: (e[0], e[1].get('x', -1)))
        for Y, e in evs:
            log.write(json.dumps(e) + '\n')
        log.flush()
        done_y = top + cut - 1
        key('Next')
        b_ = settle()
        s = find_shift(a, b_)
        if s is None or s <= 0:
            # no movement: the end, or nothing recognisable to stitch on
            if np.array_equal(a, b_):
                print('end at screen', screen, file=sys.stderr); break
            print('WARN: no stitch at screen', screen, file=sys.stderr)
            log.write(json.dumps({'kind': 'gap', 'y': top + H}) + '\n')
            s = H
        if s < H - cut + 1:
            # the page moved less than needed to show the cut-off box completely: fine, it
            # reappears lower down the stitched coordinate system
            pass
        top += s
        a = b_
        if screen % 20 == 0:
            print(f'screen {screen} top {top}', file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()
