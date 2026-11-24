#!/usr/bin/env python3
"""fig_hits.py OUT.jsonl FROM TO — figures of the records with hits, hit by hit.
Folio's Go To <n> in the "records with hits" view puts hit record n at the top of the window, so
the figures of record n are those between the top and the next record marker (scrolling on with
the scroll bar when the record is longer than the window). One JSON line per hit:
  {"h": n, "figs": [{"img", "w", "h", "box": [w, h], "y", "x"} | {"img": null, "box": ...}], "screens": k}
Resumable: hits already in OUT.jsonl are skipped. The window colour must be BG (see fig_capture)."""
import sys, os, io, json, hashlib, subprocess, time
import numpy as np
from PIL import Image
sys.path.insert(0, '/home/claude/scripts')
import fig_capture as F

out, h0, h1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
imgdir = os.path.join(os.path.dirname(os.path.abspath(out)), 'img')
os.makedirs(imgdir, exist_ok=True)
done = set()
if os.path.exists(out):
    for l in open(out):
        try: done.add(json.loads(l)['h'])
        except Exception: pass
log = open(out, 'a')
env = dict(os.environ)


def save(a, c):
    crop = a[c[0]:c[1], c[2]:c[3]]
    buf = io.BytesIO(); Image.fromarray(crop).save(buf, 'PNG'); png = buf.getvalue()
    name = hashlib.md5(png).hexdigest()[:16] + '.png'
    p = os.path.join(imgdir, name)
    if not os.path.exists(p):
        open(p, 'wb').write(png)
    return name


def scroll(a, cut):
    """scroll forward by at most `cut` rows; returns (new screen, rows moved)"""
    target = max(cut - 150, 40); moved = 0; cur = a; clicks = max(1, int(target / 100)); stuck = 0
    while moved < target:
        subprocess.run(['xdotool', 'mousemove', '1257', '952'] + ['click', '1'] * clicks, env=env)
        nxt = F.settle()
        if np.array_equal(cur[:, 30:], nxt[:, 30:]):
            stuck += 1
            if stuck >= 2: break
            continue
        d = F.find_shift(cur, nxt)
        if d is None:
            return nxt, None
        ppc = max(20, d / clicks); moved += d; cur = nxt
        clicks = max(1, int((target - moved) / ppc * 0.7))
    return cur, moved


for h in range(h0, h1 + 1):
    if h in done:
        continue
    subprocess.run(['/home/claude/scripts/goto_rec.sh', str(h)], env=env)
    a = F.settle()
    figs = []; screens = 0; top = 0; done_y = -1; complete = False; first = True
    while screens < 12:
        screens += 1
        H = a.shape[0]
        mk = F.markers(a)
        # the record's own marker is the first one (at the top after Go To); the next ends it
        if first:
            mk = mk[1:] if mk and mk[0][0] < 60 else mk
        end = next((y0 for y0, y1 in mk if top + y0 > done_y + 4), None)
        fg = F.figures(a)
        cut = min([b[0] for b, _ in fg if b[1] >= H - 2] + [H - 2])
        lim = end if end is not None else cut
        for b, c in fg:
            Y = top + b[0]
            if Y <= done_y or b[1] > lim + 2 or b[1] >= H - 2:
                continue
            if c is None:
                figs.append({'img': None, 'box': [int(b[3] - b[2]), int(b[1] - b[0])], 'y': int(Y), 'x': int(b[3])})
            else:
                figs.append({'img': save(a, c), 'w': int(c[3] - c[2]), 'h': int(c[1] - c[0]),
                             'box': [int(b[3] - b[2]), int(b[1] - b[0])], 'y': int(Y), 'x': int(c[2])})
        if end is not None:
            complete = True; break
        done_y = top + cut - 1
        a2, moved = scroll(a, cut)
        if not moved:
            complete = moved == 0; break          # end of the view (or no stitch)
        top += moved; a = a2; first = False
    figs.sort(key=lambda e: (e['y'] + e['box'][1], e['x']))
    log.write(json.dumps({'h': h, 'figs': figs, 'screens': screens, 'complete': complete}) + '\n'); log.flush()
