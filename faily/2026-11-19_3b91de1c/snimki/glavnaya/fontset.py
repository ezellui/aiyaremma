"""rev. 0.11: build and check one font set of the shuttle: 11 type blocks and 11 code combs.
Usage: TPM_FONT=<id> python3 -I fontset.py OUT_DIR            (id from tools/fontsets.py)

Writes OUT_DIR/<id>/:
  report.json   the fit (scale, padded and shifted cells, shrunk signs, missing signs), the codes of every cell, the
                reading audit (ray casting, as for Alcarin), the ink of every cell against the hammer window (after
                thickening), mass and inertia of the set;
  stl/          type_block_<m>.stl and code_comb_<m>.stl laid on the bed;
  web.json/.bin the blocks and combs at rest in machine coordinates (the page swaps them in), the items of every
                cell and key, the glyph outlines.
Everything else of the machine is the same for all sets; Alcarin's set is the one in the model."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import params as P
import data as D
import typeblocks as TB
import reader as RD
import parts as PT
import geo

out_root = sys.argv[1]
fid = D.FONT_ID
out = os.path.join(out_root, fid)
os.makedirs(os.path.join(out, 'stl'), exist_ok=True)
Q = 0.02

# ---------------------------------------------------------------- codes of the cells and the machine's limits
L = D.shuttle_layout()
cells, bad = [], []
for r in range(P.NROWS):
    for m in range(P.NPOS):
        k = L[r][m]
        if k is None:
            continue
        it = D.ITEMS[k]
        c = dict(row=r + 1, pos=m, key=str(k), label=it['label'], kind=it['kind'], missing=bool(it.get('missing')))
        if it['kind'] in D.ADV:
            c.update(w=it['w'], b=it['b'], c=it['c'])
            ok = 4 <= it['w'] <= 16 and 0 <= it['b'] <= 8 and 0 <= it['c'] <= 9
            if not ok:
                bad.append(c)
        cells.append(c)

# ink after thickening against the hammer window (the face is Alcarin's for every set)
hx0, hx1, hz0, hz1 = PT.hammer_face()
base = P.ZP - 0.18 * P.EM
ext = TB.extents()
win = []
for k, (x0, x1, z0, z1) in ext.items():
    o = dict(key=k, x=[round(x0 * P.U - hx0, 3), round(hx1 - x1 * P.U, 3)], z=[round(base + z0 - hz0, 3), round(hz1 - base - z1, 3)])
    o['ok'] = min(o['x'] + o['z']) >= -0.02
    win.append(o)

# reading: every advancing cell, nine rays per feeler (reader.audit)
aud = RD.audit()
n_bad_read = sum(1 for a in aud if not a['ok'])
mass, inertia = RD.mass_inertia()

# blocks: mass (PETG, solid) and inertia about the shuttle axis
import trimesh
mb = ib = 0.0
for m in range(P.NPOS):
    V, F = geo.to_arrays(TB.block_home(m))
    tm = trimesh.Trimesh(V, F, process=False); tm.density = 1.27e-3
    mb += tm.mass
    c = tm.center_mass; I = tm.moment_inertia
    ib += I[2, 2] + tm.mass * (c[0] ** 2 + (c[1] - P.AXIS_Y) ** 2)

rep = dict(id=fid, name=D.FONTSET['name'], author=D.FONTSET['author'], lic=D.FONTSET['lic'], file=D.FONTSET['file'],
           profile=D.PROFILE, cells=cells, code_bad=bad, window=[w for w in win if not w['ok']],
           window_margin=round(min(min(w['x'] + w['z']) for w in win), 3),
           read=dict(n=len(aud), bad=n_bad_read, fails=[a for a in aud if not a['ok']]),
           combs=dict(mass_g=round(mass, 1), I_kgmm2=round(inertia, 1)), blocks=dict(mass_g=round(mb * 1000, 1) if mb < 1 else round(mb, 1), I_kgmm2=round(ib, 1)),
           ranges=dict(w=[min(c['w'] for c in cells if 'w' in c), max(c['w'] for c in cells if 'w' in c)],
                       b=[min(c['b'] for c in cells if 'b' in c), max(c['b'] for c in cells if 'b' in c)],
                       c=[min(c['c'] for c in cells if 'c' in c), max(c['c'] for c in cells if 'c' in c)]))
rep['ok'] = not bad and not rep['window'] and n_bad_read == 0
json.dump(rep, open(os.path.join(out, 'report.json'), 'w'), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- STL on the bed
for m in range(P.NPOS):
    for nm, mesh in ((f'type_block_{m}', TB.block_print_bed(m)), (f'code_comb_{m}', RD.comb_print_bed(m))):
        V, F = geo.to_arrays(mesh)
        trimesh.Trimesh(V, F, process=False).export(os.path.join(out, 'stl', nm + '.stl'))

# ---------------------------------------------------------------- page data
ps = [p for p in PT.build(PT.State()) if p.name.startswith('type block ') or p.name.startswith('code comb ')]
parts_, geoms, blob = [], [], bytearray()
for p in ps:
    V, F = geo.to_arrays(p.mesh)
    o = V.min(0)
    q = np.round((V - o) / Q).astype(np.int32)
    assert q.max() < 65535
    idx = F.astype(np.uint16 if len(V) < 65536 else np.uint32)
    while len(blob) % 4:
        blob.append(0)
    geoms.append([len(blob), len(V), int(F.size), bool(idx.dtype == np.uint32)])
    blob += q.astype(np.uint16).tobytes()
    while len(blob) % 4:
        blob.append(0)
    blob += idx.tobytes()
    parts_.append(dict(n=p.name, o=[round(float(v), 3) for v in o], geo=len(geoms) - 1))
open(os.path.join(out, 'web.bin'), 'wb').write(bytes(blob))


def item_json(k):
    if k is None:
        return None
    it = D.ITEMS[k]
    d = dict(kind=it['kind'], label=it.get('label', ''), glyph=it.get('glyph'), ax=it.get('ax', 0.0), w=it.get('w', 0))
    if it.get('missing'):
        d['missing'] = True
    if it['kind'] in D.ADV:
        d.update(a=it['a'], b=it['b'], c=it['c'])
        if it['kind'] == 'C':
            d.update(mark=it.get('mark'), max=D.MARK_AX.get(it.get('mark'), 0.0))
    else:
        d.update(below=bool(it.get('below')))
    return d


keys = {}
for r, rw in enumerate(D.ROWS):
    for c, (lo, up) in enumerate(rw):
        n, _ = D.key_slot(r, c)
        keys[n] = dict(lo=item_json(lo), up=item_json(up))
names = set()
for it in D.ITEMS.values():
    for g in (it.get('glyph'), it.get('mark')):
        if g:
            names.add(g)
gs = D.GLYPHSET
paths, bbox = {}, {}
for nm in sorted(names):
    pen = SVGPathPen(gs); gs[nm].draw(pen); paths[nm] = pen.getCommands()
    bp = BoundsPen(gs); gs[nm].draw(bp); bbox[nm] = [round(v) for v in (bp.bounds or (0, 0, 0, 0))]
web = dict(id=fid, name=D.FONTSET['name'], author=D.FONTSET['author'], Q=Q, parts=parts_, geoms=geoms, keys=keys,
           LAYOUT=[[item_json(k) for k in row] for row in L], paths=paths, bbox=bbox,
           info=dict(scale=(D.PROFILE or {}).get('scale', 1.0), missing=(D.PROFILE or {}).get('missing', []),
                     pad=len((D.PROFILE or {}).get('pad', [])), shift=len((D.PROFILE or {}).get('shift', [])),
                     shrunk=(D.PROFILE or {}).get('shrunk', []) if D.PROFILE else [], ok=rep['ok'],
                     read=f"{len(aud) - n_bad_read}/{len(aud)}", ranges=rep['ranges']))
if D.PROFILE:
    web['info']['shrunk'] = [x[0] for x in D.CODES.get('shrunk', [])]
json.dump(web, open(os.path.join(out, 'web.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print(fid, 'ok' if rep['ok'] else 'FAIL', 'read', f"{len(aud) - n_bad_read}/{len(aud)}", 'window margin', rep['window_margin'],
      'codes w/b/c', rep['ranges'], 'combs', rep['combs'], 'blocks', rep['blocks'], len(blob) / 1e6, 'MB')
