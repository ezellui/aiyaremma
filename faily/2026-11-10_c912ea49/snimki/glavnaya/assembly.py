"""rev. 0.9c: assembly sheets -- one exploded view per group of parts, printed parts marked with balloons that carry
the number debossed on the part and used in its STL file name.

The explosion moves every part away from the centre of its group by EXPLODE times its offset (and the group's stacked
parts apart in Z), so the parts keep their relative places; a balloon sits on the visible middle of each numbered
part, pushed out from the sheet's centre with a leader to the part. Usage: called from build.py."""
import os
import numpy as np
from PIL import ImageDraw, ImageFont
import geo, render

TITLES = {'frame': 'Остов', 'keys': 'Клавиши и гребёнки', 'levers': 'Рычаги клавиш', 'plates': 'Кодовые пластины',
          'bails': 'Рамки (мерные планки)', 'sectors': 'Сектора памяти и повторители', 'select': 'Выбор: толкатели, планки, стержни',
          'uframe': 'Печатающий узел: плита, деревья, фиксаторы', 'shuttle': 'Челнок', 'carriage': 'Каретка', 'esc': 'Спуск, забой, «назад на литеру»',
          'ribbon': 'Лента', 'drive': 'Двигатель и цикловой вал', 'hammer': 'Молоток'}
EXPLODE = 0.55
VIEW = ((-0.55, -0.75, 0.62),)           # direction from the target to the eye


def sheet(parts, number_of, font_path, title, out_png, W=2000, H=1500):
    ps = [p for p in parts if not p.mesh.is_empty()]
    if not ps:
        return []
    cs = np.array([np.array(p.mesh.bounding_box()).reshape(2, 3).mean(0) for p in ps])
    C = cs.mean(0)
    objs = []; meta = []
    for i, (p, c) in enumerate(zip(ps, cs)):
        d = (c - C) * EXPLODE
        V, F = geo.to_arrays(p.mesh)
        V = V + d
        num = number_of.get(p.name)
        col = p.color if num is not None or p.kind == 'print' else tuple(int(0.6 * x + 0.4 * 200) for x in p.color)
        objs.append((V, F, col, i)); meta.append((p, num))
    allV = np.concatenate([o[0] for o in objs]); tgt = (allV.min(0) + allV.max(0)) / 2
    span = np.linalg.norm(allV.max(0) - allV.min(0))
    eye = tgt + np.array(VIEW[0]) * span * 2
    img, s, ids = render.render(objs, (tuple(eye), tuple(tgt)), W=W, H=H, margin=0.07, return_ids=True)
    dr = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font_path, 22); fbig = ImageFont.truetype(font_path, 34)
    dr.text((30, 20), title, fill=(30, 30, 30), font=fbig)
    placed = []
    cx, cy = W / 2, H / 2
    used = {}
    for i, (p, num) in enumerate(meta):
        if num is None:
            continue
        ys, xs = np.nonzero(ids == i)
        if len(xs) < 6:
            continue
        k = np.argmin((xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2)
        px, py = float(xs[k]), float(ys[k])
        key = num
        if key in used and np.hypot(px - used[key][0], py - used[key][1]) < 60:
            continue                                     # one balloon per number in the same spot
        used[key] = (px, py)
        v = np.array([px - cx, py - cy]); n = np.linalg.norm(v); v = v / n if n > 1 else np.array([1.0, 0.0])
        bx, by = px + v[0] * 46, py + v[1] * 46
        for _ in range(30):                              # keep balloons apart
            if all(np.hypot(bx - qx, by - qy) > 34 for qx, qy in placed):
                break
            bx += v[0] * 14 + 8; by += v[1] * 14
        bx = min(max(bx, 20), W - 20); by = min(max(by, 60), H - 20)
        placed.append((bx, by))
        dr.line([(px, py), (bx, by)], fill=(60, 60, 60), width=2)
        dr.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(60, 60, 60))
        t = str(num)
        r = 15 if len(t) < 3 else 18
        dr.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 255, 255), outline=(40, 40, 40), width=2)
        tw = dr.textlength(t, font=fnt)
        dr.text((bx - tw / 2, by - 13), t, fill=(20, 20, 20), font=fnt)
    img.save(out_png)
    return sorted({m[1] for m in meta if m[1] is not None})


def sheets(parts, fit_rows, out_dir, font_path):
    os.makedirs(out_dir, exist_ok=True)
    number_of = {}
    for r in fit_rows:
        for nm in r['names']:
            number_of.setdefault(nm, r['num'])
    res = []
    for g, title in TITLES.items():
        gp = [p for p in parts if p.group == g and p.kind != 'ref']
        if not gp:
            continue
        fn = os.path.join(out_dir, f'asm_{g}.png')
        nums = sheet(gp, number_of, font_path, title, fn)
        res.append(dict(group=g, title=title, file=os.path.basename(fn), numbers=nums,
                        buy=sorted({p.bom for p in gp if p.kind != 'print' and p.bom})))
    return res
