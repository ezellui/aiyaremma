"""Engineering estimates for TPM-2 rev. 0.3.
Usage: python3 -I analysis.py DATA_DIR OUT_DIR
Writes LaTeX table fragments and analysis.json. All inputs that are assumptions are listed in ASSUMPTIONS.
"""
import sys, os, json, math, random

data_dir, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
D = json.load(open(os.path.join(data_dir, 'codes.json')))
INCH = 25.4
POS = 88               # shuttle positions incl. 2 reserves
PITCH_U = 19           # widest cell 16u + 3u gap
ARC_DEG = 118          # Hammond one-piece shuttle arc (source: kbd.news)
ROW_EM = 1.35          # row height on the shuttle in em (glyph extent ~1.02 em + gap)

res = {}

# ---------------- 1. trade study: body size and shuttle geometry ----------------
dot = next(m for m in D['marks'] if m['key'] == 'i')['bbox']
dot_em = (dot[3] - dot[1]) / 1000.0
bow_em = 0.412
rows_opts = [3, 4]
em_opts = [(r'1/4', 0.25), (r'1/5', 0.20), (r'1/6', 1 / 6)]
trade = []
for name, em_in in em_opts:
    em = em_in * INCH; u = em / 16
    for rows in rows_opts:
        per_row = math.ceil(POS / rows)
        arc = per_row * PITCH_U * u
        R = arc / math.radians(ARC_DEG)
        trade.append(dict(em=name, em_mm=em, u=u, rows=rows, per_row=per_row, arc=arc, R=R,
                          height=rows * ROW_EM * em, bow=bow_em * em, dot=dot_em * em, slide=9 * u))
ref = next(t for t in trade if t['em'] == '1/6' and t['rows'] == 4)
for t in trade:
    # shuttle as a thin strip: mass ~ arc * height, inertia ~ mass * R^2
    t['inertia'] = (t['arc'] * t['height'] * t['R'] ** 2) / (ref['arc'] * ref['height'] * ref['R'] ** 2)
res['trade'] = trade
rows = []
for t in trade:
    mark = r'\textbf{' if (t['em'] == '1/6' and t['rows'] == 4) else '{'
    rows.append(mark + f"{t['em']}''}} & {t['em_mm']:.2f} & {t['u']:.3f} & {t['rows']}$\\times${t['per_row']} & "
                f"{t['arc']:.0f} & {t['R']:.0f} & {t['height']:.0f} & {t['inertia']:.1f} & {t['bow']:.2f} & "
                f"{t['dot']:.2f} & {t['slide']:.1f}\\\\\n")
open(os.path.join(out, 'tab_trade.tex'), 'w').write(''.join(rows))

# ---------------- 2. key travel budget ----------------
vals = {'w': [], 'b': [], 'c': []}
for t in D['tengwar']:
    d = round(t['d_bot'])
    vals['w'].append(t['w']); vals['b'].append(t['b']); vals['c'].append(t['b'] - d)
for k in ('numerals', 'punct', 'combos'):
    for t in D[k]:
        vals['w'].append(t['w']); vals['b'].append(t['b']); vals['c'].append(t['b'])
vmax = {k: max(v) for k, v in vals.items()}
RESET_END = 3.5      # mm of key travel to lift the latches (assumption)
MARGIN = 0.5         # mm between end of reset and the first bail pickup
budget = []
for T in (12, 14, 16):
    for k in (0.5, 0.6, 0.7):
        g_first = T - k * max(vmax.values())          # earliest pickup of any measuring bail
        ok = g_first >= RESET_END + MARGIN
        budget.append(dict(T=T, k=k, g_w=T - k * vmax['w'], g_b=T - k * vmax['b'], g_c=T - k * vmax['c'],
                           half=k / 2, ok=ok))
CHOICE = dict(T=14, k=0.6)
res['budget'] = budget; res['choice'] = CHOICE; res['vmax'] = vmax
rows = []
for b in budget:
    sel = (b['T'] == CHOICE['T'] and abs(b['k'] - CHOICE['k']) < 1e-9)
    f = (lambda s: r'\textbf{' + s + '}') if sel else (lambda s: s)
    rows.append(' & '.join(f(x) for x in [f"{b['T']}", f"{b['k']:.1f}", f"{b['g_w']:.1f}", f"{b['g_b']:.1f}",
                                         f"{b['g_c']:.1f}", f"{b['half']:.2f}", 'да' if b['ok'] else 'нет']) + '\\\\\n')
open(os.path.join(out, 'tab_budget.tex'), 'w').write(''.join(rows))

# ---------------- 3. gap tolerance -> probability of a wrong detent ----------------
def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

half = CHOICE['k'] / 2
gap = []
for s in (0.03, 0.05, 0.06, 0.07, 0.10):
    p = 2 * (1 - phi(half / s))
    gap.append(dict(sigma=s, z=half / s, p=p, per_page=p * 3 * 1500))   # ~3 measured values x 1500 slugs/page
res['gap'] = gap
rows = []
for g in gap:
    pp = g['per_page']
    rows.append(f"{g['sigma']:.2f} & $\\pm${3*g['sigma']:.2f} & {g['z']:.1f} & "
                f"{g['p']:.1e} & {pp:.1e}\\\\\n".replace('e-0', 'e-').replace('e+0', 'e+'))
open(os.path.join(out, 'tab_gap.tex'), 'w').write(''.join(rows))

# ---------------- 4. Monte Carlo of mark-to-axis error ----------------
# sigma in mm. 'sys' = fixed per machine and per position/bar; 'rep' = per strike.
ASSUMPTIONS = {
    'shuttle': [
        ('рисунок литеры на челноке', 'sys', 0.010, 'per_glyph'),
        ('рисунок знака на челноке', 'sys', 0.010, 'per_glyph'),
        ('штифт позиции литеры', 'sys', 0.015, 'per_pos'),
        ('штифт позиции знака', 'sys', 0.015, 'per_pos'),
        ('останов челнока на штифте', 'rep', 0.010, 'strike2'),
        ('подача каретки (люфт передачи)', 'rep', 0.015, 'strike'),
        ('упор сектора (фиксатор)', 'sys', 0.010, 'per_value'),
        ('нулевой и рабочий упоры ползуна', 'rep', 0.010, 'strike'),
    ],
    'lever': [
        ('рисунок литеры на рычаге', 'sys', 0.010, 'per_glyph'),
        ('рисунок знака на рычаге', 'sys', 0.010, 'per_glyph'),
        ('выравнивание рычага литеры', 'sys', 0.030, 'per_pos'),
        ('выравнивание рычага знака', 'sys', 0.030, 'per_pos'),
        ('люфт рычага в прорези (0,05 мм на сторону)', 'rep', 0.025, 'strike2'),
        ('подача каретки (люфт передачи)', 'rep', 0.015, 'strike'),
        ('упор сектора (фиксатор)', 'sys', 0.010, 'per_value'),
        ('направляющая салазок', 'sys', 0.020, 'per_sled'),
    ],
}
random.seed(20261110)
NM, NS = 400, 400        # machines x strikes per machine


def mc(name, drop=None):
    errs = []
    for m in range(NM):
        sysv = {}
        for i, (lbl, kind, s, scope) in enumerate(ASSUMPTIONS[name]):
            if kind == 'sys' and i != drop:
                n = {'per_glyph': 90, 'per_pos': 44 if name == 'lever' else 22, 'per_value': 10, 'per_sled': 2}[scope]
                sysv[i] = [random.gauss(0, s) for _ in range(n)]
        for _ in range(NS):
            e = 0.0
            for i, (lbl, kind, s, scope) in enumerate(ASSUMPTIONS[name]):
                if i == drop:
                    continue
                if kind == 'sys':
                    e += random.choice(sysv[i]) * (1 if i % 2 == 0 else -1)
                else:
                    reps = 2 if scope == 'strike2' else 1
                    e += sum(random.gauss(0, s) for _ in range(reps))
            errs.append(abs(e))
    errs.sort()
    q = lambda p: errs[int(p * (len(errs) - 1))]
    return dict(p50=q(0.5), p95=q(0.95), p997=q(0.997), share_01=sum(1 for x in errs if x > 0.1) / len(errs))


mcres = {n: mc(n) for n in ASSUMPTIONS}
sens = {}
for n in ASSUMPTIONS:
    base = mcres[n]['p95']
    sens[n] = []
    for i, a in enumerate(ASSUMPTIONS[n]):
        r = mc(n, drop=i)
        sens[n].append((a[0], base - r['p95']))
res['mc'] = mcres; res['sens'] = sens
rows = []
for n, title in (('shuttle', 'челнок (ред. 0.2–0.3)'), ('lever', 'рычаги и салазки (ред. 0.1)')):
    r = mcres[n]
    rows.append(f"{title} & {r['p50']:.3f} & {r['p95']:.3f} & {r['p997']:.3f} & {100*r['share_01']:.2f}\\,\\%\\\\\n")
open(os.path.join(out, 'tab_mc.tex'), 'w').write(''.join(rows))
rows = []
for n in ('shuttle', 'lever'):
    for (lbl, kind, s, scope), (_, dlt) in zip(ASSUMPTIONS[n], sens[n]):
        rows.append(f"{'челнок' if n == 'shuttle' else 'рычаги'} & {lbl} & {'сист.' if kind == 'sys' else 'случ.'} & "
                    f"{s:.3f} & {max(dlt, 0):.3f}\\\\\n")
    if n == 'shuttle':
        rows.append('\\midrule\n')
open(os.path.join(out, 'tab_assume.tex'), 'w').write(''.join(rows))

json.dump(res, open(os.path.join(out, 'analysis.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({'trade_ref': ref, 'vmax': vmax, 'budget_choice': [b for b in budget if b['T'] == 14 and abs(b['k'] - 0.6) < 1e-9],
                  'gap': gap, 'mc': mcres, 'sens': sens}, ensure_ascii=False, indent=1))
