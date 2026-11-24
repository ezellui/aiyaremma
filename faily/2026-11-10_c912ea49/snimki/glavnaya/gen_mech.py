"""Generate LaTeX/TikZ fragments for the fully mechanical tengwar typewriter (TPM-2).
Usage: python3 -I gen_mech.py FONT DATA_DIR OUT_DIR

Model: an advancing slug prints with the LEFT edge of its cell at the print point; the carriage
then feeds w. Dead marks sit on two sledges displaced back by b (marks above) or c = b - d
(marks below); the sledges are set by the last advancing key and held by a latch (memory).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
import inventory as inv
import layout_mech as lay

font_path, data_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
F = TTFont(font_path)
GID = {n: i for i, n in enumerate(F.getGlyphOrder())}
D = json.load(open(os.path.join(data_dir, 'codes.json')))
U = D['U']
SPACE_W, SPACE_N = 6, 4
BELOW_MARKS = {'dotb', 'ddotb', 'dbl', 'dblW', 'dblL', 'lsd'}

import measure_helpers as mh

ITEMS = {}
for t in D['tengwar']:
    d = round(t['d_bot'])
    ITEMS[t['cp']] = dict(kind='T', label=t['name'], w=t['w'], a=t['a'], b=t['b'], d=d, c=t['b'] - d,
                          glyph=t['glyph'], ax=t['top'][0], adv=t['adv'], cps=[t['cp']],
                          spl=t['a'] * U - t['top'][0], spr=t['b'] * U - (t['adv'] - t['top'][0]))
for t in D['numerals'] + D['punct']:
    ax = mh.top_anchor(F, t['glyph'], t['adv'])
    ITEMS[t['cp']] = dict(kind='N' if t in D['numerals'] else 'P', label=t['name'], w=t['w'], a=t['a'],
                          b=t['b'], d=0, c=t['b'], glyph=t['glyph'], ax=ax, adv=t['adv'], cps=[t['cp']])
MARK_AX = {m['glyph']: m['anchor'][0] for m in D['marks']}
for c in D['combos']:
    car = ITEMS[0xE02C]
    mk = {0xE040: 'uniE040', 0xE046: 'uniE046', 0xE044: 'uniE044', 0xE04A: 'uniE04A', 0xE04C: 'uniE04C'}[c['cps'][1]]
    ITEMS['combo:' + c['name']] = dict(kind='C', label=c['name'], w=c['w'], a=c['a'], b=c['b'], d=0, c=c['b'],
                                      glyph=car['glyph'], mark=mk, ax=car['ax'], adv=car['adv'], cps=c['cps'])
for m in D['marks']:
    ITEMS['mark:' + m['key']] = dict(kind=m['kind'], label=m['role'], w=0, glyph=m['glyph'],
                                     ax=m['anchor'][0], length=m['length'], below=m['key'] in BELOW_MARKS)
MARK_CP = {'mark:a': 0xE040, 'mark:e': 0xE046, 'mark:i': 0xE044, 'mark:o': 0xE04A, 'mark:u': 0xE04C,
           'mark:tilde': 0xE052, 'mark:nas': 0xE050, 'mark:nasW': 0xE050, 'mark:dotb': 0xE045,
           'mark:ddotb': 0xE043, 'mark:dbl': 0xE051, 'mark:dblW': 0xE051, 'mark:dblL': 0xE051, 'mark:lsd': 0xE07D}
ADV = ('T', 'C', 'N', 'P')


def hexs(cp):
    return f"{cp:04X}"


def gl(name, x=0, y=0, extra=''):
    return (f"\\node[anchor=base west,inner sep=0pt,outer sep=0pt{extra}] at ({x:.1f},{y:.1f}) "
            f"{{\\TG{{{GID[name]}}}}};\n")


def inline(key, size='\\tgsmall'):
    it = ITEMS[key]
    if it['kind'] in ('T', 'N', 'P'):
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}}}"
    if it['kind'] == 'C':
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}\\symbol{{\"{hexs(it['cps'][1])}}}}}"
    return ("{\\tikz[baseline=0pt,x=\\tgu,y=\\tgu]{\\draw[gray!60,densely dotted] (0,0) -- (0,520);"
            + gl(it['glyph'], -it['ax'], 0) + "}}")


# ---------- validation of the layout ----------
used = [k for row in lay.ROWS for pair in row for k in pair if k is not None]
assert len(used) == len(set(map(str, used))), 'duplicate slugs'
for r, row in enumerate(lay.ROWS):
    for c, pair in enumerate(row):
        kinds = {ITEMS[k]['kind'] in ADV for k in pair if k is not None}
        assert len(kinds) == 1, f'mixed dead/advancing key at {r},{c}'
        if kinds == {False}:
            sl = lay.SLEDGE[(r, c)]
            for k in pair:
                if k is not None:
                    assert ITEMS[k]['below'] == (sl == 'B'), f'mark {k} on wrong sledge'
        else:
            assert (r, c) not in lay.SLEDGE

# ---------- simulation ----------

def simulate_mech(words):
    X = 0          # print point on the paper = left edge of the next cell (u)
    SA = SB = 0    # sledge displacements (u)
    ev, placed = [], []
    for wi, word in enumerate(words):
        if wi:
            X += SPACE_W; SA = SB = 0
            ev.append(dict(key='space', X=X, SA=SA, SB=SB, hit=None))
        for k in word:
            it = ITEMS[k]
            if it['kind'] in ADV:
                hit = X
                placed.append(('base', k, X + it['a']))       # axis position on the paper
                X += it['w']; SA, SB = it['b'], it['c']
                ev.append(dict(key=k, X=X, SA=SA, SB=SB, hit=hit, feed=it['w']))
            else:
                off = SB if it['below'] else SA
                hit = X - off
                placed.append(('mark', k, hit))
                ev.append(dict(key=k, X=X, SA=SA, SB=SB, hit=hit, sled='B' if it['below'] else 'A'))
    return ev, placed, X


def simulate_tpm1(words):
    """Reference: the electromechanical TPM-1 model (axial slugs, deferred phase)."""
    R = dict(a=0, b=0, d=0); X = 0; placed = []
    for wi, word in enumerate(words):
        if wi:
            X += R['b'] + SPACE_W; R = dict(a=0, b=0, d=0)
        for k in word:
            it = ITEMS[k]
            if it['kind'] in ADV:
                X += R['b'] + it['a']; placed.append(('base', k, X)); R = dict(a=it['a'], b=it['b'], d=it['d'])
            else:
                placed.append(('mark', k, X + (R['d'] if it['below'] else 0)))
    return placed


def render(placed, y=0):
    s = []
    for kind, k, X in placed:
        it = ITEMS[k]
        s.append(gl(it['glyph'], X * U - it['ax'], y))
        if kind == 'base' and it['kind'] == 'C':
            s.append(gl(it['mark'], X * U - MARK_AX[it['mark']], y))
    return ''.join(s)


def ustring(words):
    out = []
    for wi, word in enumerate(words):
        if wi:
            out.append('\\ ')
        for k in word:
            if k in MARK_CP:
                out.append(f"\\symbol{{\"{hexs(MARK_CP[k])}}}")
            else:
                out.extend(f"\\symbol{{\"{hexs(c)}}}" for c in ITEMS[k]['cps'])
    return ''.join(out)


def fig_trace(words, ref_y=-1250):
    ev, placed, Xend = simulate_mech(words)
    ref = simulate_tpm1(words)
    assert [(a, str(b), c) for a, b, c in placed] == [(a, str(b), c) for a, b, c in ref], 'TPM-2 != TPM-1'
    s = [render(placed, 0)]
    s.append(f"\\node[anchor=base west,inner sep=0pt] at (0,{ref_y}) {{\\TGtext{{{ustring(words)}}}}};\n")
    for e in ev:
        if e['key'] not in ('space',) and e['hit'] is not None:
            col = 'axisred' if e.get('feed') else ('sledA' if e.get('sled') == 'A' else 'sledB')
            s.append(f"\\draw[{col},thick] ({e['hit']*U},-380) -- ({e['hit']*U},-290);\n")
    s.append(f"\\draw[base] (0,0) -- ({Xend*U},0); \\draw[base] (0,{ref_y}) -- ({Xend*U},{ref_y});\n")
    s.append(f"\\node[lbl,anchor=east] at (-60,250) {{ТПМ-2}};\n")
    s.append(f"\\node[lbl,anchor=east] at (-60,{ref_y + 250}) {{шрифт}};\n")
    return ''.join(s), ev


def trace_table(ev):
    rows = []; n = 0
    for e in ev:
        if e['key'] == 'space':
            rows.append(f"— & пробел {SPACE_W}u & — & {e['X']} & 0 / 0\\\\\n"); continue
        n += 1; it = ITEMS[e['key']]
        kind = {'T': 'тенгва', 'C': 'ára+техта', 'N': 'цифра', 'P': 'знак'}.get(it['kind'])
        if kind:
            rows.append(f"{n} & {inline(e['key'])}\\ {kind} & {e['hit']} & {e['X']} & {e['SA']} / {e['SB']}\\\\\n")
        else:
            sl = e['sled']
            rows.append(f"{n} & {inline(e['key'])}\\ знак ({sl}) & {e['hit']} & {e['X']} & {e['SA']} / {e['SB']}\\\\\n")
    return ''.join(rows)


# ---------- figures ----------

def slug_adv(key, x0, title):
    it = ITEMS[key]; w = it['w'] * U; ax = it['a'] * U; s = []
    s.append(f"\\draw[slug] ({x0 - 60},-400) rectangle ({x0 + w + 60},820);\n")
    s.append(f"\\fill[cellfill] ({x0},-330) rectangle ({x0 + w},740);\n")
    s.append(gl(it['glyph'], x0 + ax - it['ax'], 0))
    if it['kind'] == 'C':
        s.append(gl(it['mark'], x0 + ax - MARK_AX[it['mark']], 0))
    s.append(f"\\draw[axisT,thin,draw=ink!35] ({x0 + ax},-330) -- ({x0 + ax},760);\n")
    s.append(f"\\draw[ppoint] ({x0},-470) -- ({x0},900);\n")
    s.append(f"\\draw[dim] ({x0},-540) -- ({x0 + w},-540);\n")
    s.append(f"\\node[lbl,anchor=north] at ({x0 + w/2},-570) {{$w{{=}}{it['w']}$}};\n")
    s.append(f"\\node[lbl,anchor=north] at ({x0 + w/2},-700) {{$b{{=}}{it['b']}$, $c{{=}}{it['c']}$}};\n")
    s.append(f"\\node[lbl,anchor=south] at ({x0 + w/2},930) {{{title}}};\n")
    return ''.join(s), w


def slug_dead(key, x0, title):
    it = ITEMS[key]; width = max(it['length'], 300) + 120; cx = x0 + width / 2; s = []
    s.append(f"\\draw[slug,fill={'sledB' if it['below'] else 'sledA'}!12] ({x0 - 60},-400) rectangle ({x0 + width + 60},820);\n")
    s.append(gl(it['glyph'], cx - it['ax'], 0))
    s.append(f"\\draw[ppoint] ({cx},-470) -- ({cx},900);\n")
    s.append(f"\\node[lbl,anchor=north] at ({cx},-570) {{салазки {'B' if it['below'] else 'A'}}};\n")
    s.append(f"\\node[lbl,anchor=south] at ({cx},930) {{{title}}};\n")
    return ''.join(s), width


def row(items, gap=260):
    s = []; x = 0
    for k, ttl in items:
        f = slug_adv if ITEMS[k]['kind'] in ADV else slug_dead
        code, w = f(k, x, ttl); s.append(code); x += w + gap
    return ''.join(s)


def fig_geometry():
    """Three moments for 'tinco + e + y-dots': strike letter, feed w, strike marks from sledges."""
    t = ITEMS[0xE000]; e = ITEMS['mark:e']; y2 = ITEMS['mark:ddotb']
    s = []; w = t['w'] * U; ax = t['a'] * U
    # paper cell
    s.append(f"\\fill[cellfill] (0,-330) rectangle ({w},740);\n")
    s.append(gl(t['glyph'], ax - t['ax'], 0))
    s.append(gl(e['glyph'], ax - e['ax'], 0))
    bx = (t['w'] - t['c']) * U
    s.append(gl(y2['glyph'], bx - y2['ax'], 0))
    s.append(f"\\draw[base] (-400,0) -- ({w + 900},0);\n")
    # moments
    s.append(f"\\draw[ppoint] (0,-420) -- (0,880); \\node[lbl,anchor=south,text=axisred] at (0,890) {{1}};\n")
    s.append(f"\\draw[ppoint] ({w},-420) -- ({w},880); \\node[lbl,anchor=south,text=axisred] at ({w},890) {{2}};\n")
    s.append(f"\\draw[sledA,thick,dash pattern=on 4pt off 2pt] ({ax},300) -- ({ax},880); \\node[lbl,anchor=south,text=sledA] at ({ax},890) {{3}};\n")
    s.append(f"\\draw[sledB,thick,dash pattern=on 4pt off 2pt] ({bx},-420) -- ({bx},60); \\node[lbl,anchor=north,text=sledB] at ({bx},-430) {{4}};\n")
    s.append(f"\\draw[dim] (0,-640) -- node[lbl,below]{{подача $w{{=}}{t['w']}$}} ({w},-640);\n")
    s.append(f"\\draw[dim,draw=sledA] ({ax},620) -- node[lbl,above,text=sledA]{{$b{{=}}{t['b']}$}} ({w},620);\n")
    s.append(f"\\draw[dim,draw=sledB] ({bx},-250) -- node[lbl,below,text=sledB,pos=0.5]{{$c{{=}}{t['c']}$}} ({w},-250);\n")
    return ''.join(s)


# ---------- keyboard ----------

def esc(c):
    return {'\\': '\\textbackslash{}', "'": '\\textquotesingle{}', '[': '{[}'}.get(c, c)


def key_face(k, pos):
    it = ITEMS[k]
    size = '\\tgkeyU' if pos == 'up' else '\\tgkeyL'
    if it['kind'] in ('T', 'N', 'P'):
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}}}"
    if it['kind'] == 'C':
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}\\symbol{{\"{hexs(it['cps'][1])}}}}}"
    scale = '\\tgkuU' if pos == 'up' else '\\tgkuL'
    return (f"\\tikz[baseline=0pt,x={scale},y={scale}]{{\\draw[gray!55,densely dotted] (0,-150) -- (0,650);"
            + gl(it['glyph'], -it['ax'], 0).replace('\\TG{', '\\TGk' + ('U' if pos == 'up' else 'L') + '{') + "}")


def keyboard():
    s = []; KW, KH, G = 12.4, 14.0, 1.3; offs = [0, 4, 6, 9]
    for r, rw in enumerate(lay.ROWS):
        for c, (lo, up) in enumerate(rw):
            x = offs[r] + c * (KW + G); y = -r * (KH + G)
            sl = lay.SLEDGE.get((r, c))
            fill = {'A': 'sledA!18', 'B': 'sledB!18'}.get(sl, 'keyadv')
            s.append(f"\\draw[key,fill={fill}] ({x},{y}) rectangle +({KW},{-KH});\n")
            s.append(f"\\node[keyleg] at ({x + KW - 1.0},{y - 1.2}) {{\\texttt{{{esc(lay.LEGENDS[r][c])}}}}};\n")
            for k, pos in ((up, 'up'), (lo, 'lo')):
                if k is None:
                    if pos == 'up':
                        s.append(f"\\node[keyres] at ({x + KW*0.4},{y - 3.6}) {{резерв}};\n")
                    continue
                yy = y - 4.6 if pos == 'up' else y - 10.9
                xx = x + (KW*0.32 if pos == 'up' else KW*0.6)
                s.append(f"\\node[anchor=base,inner sep=0pt,{('keyup' if pos == 'up' else 'keylo')}] at ({xx},{yy}) {{{key_face(k, pos)}}};\n")
    y = -4 * (KH + G)
    def fk(x, wdt, txt):
        s.append(f"\\draw[key,fill=keyfn] ({x},{y}) rectangle +({wdt},{-KH*0.8}); \\node[fnleg,align=center] at ({x + wdt/2},{y - KH*0.4}) {{{txt}}};\n")
        return x + wdt + G
    x = fk(0, KW*1.6, 'РЕГИСТР'); x = fk(x, KW*1.3, 'ЗАБОЙ\\\\1u'); x = fk(x, KW*3.2, f'ПРОБЕЛ {SPACE_N}u')
    x = fk(x, KW*3.2, f'ПРОБЕЛ {SPACE_W}u'); x = fk(x, KW*1.3, '$\\pm$u'); fk(x, KW*1.9, 'НАЗАД\\\\НА ЛИТЕРУ')
    return ''.join(s)


# ---------- tables ----------

def tab_codes():
    rows = []
    for t in D['tengwar']:
        it = ITEMS[t['cp']]
        rows.append(f"{inline(t['cp'])} & {t['name']} & {hexs(t['cp'])} & {it['w']} & {it['a']} & {it['b']} & "
                    f"{it['d']:+d} & {it['c']}\\\\\n")
    for key in [n['cp'] for n in D['numerals']] + [p['cp'] for p in D['punct']] + ['combo:' + c['name'] for c in D['combos']]:
        it = ITEMS[key]
        rows.append(f"{inline(key)} & {it['label']} & {hexs(key) if isinstance(key, int) else '02C+…'} & {it['w']} & "
                    f"{it['a']} & {it['b']} & {it['d']:+d} & {it['c']}\\\\\n")
    return ''.join(rows)


QUENYA = [
    [0xE02E, 'mark:e', 0xE022, 'mark:e', 0xE010],
    [0xE024, 'combo:ára+i', 0xE022, 'mark:a'],
    [0xE022, 'combo:ára+u', 0xE011, 'mark:e', 0xE010, 'mark:dbl'],
    [0xE02E, 'mark:o', 0xE011, 'mark:e', 0xE00C, 'mark:i', 0xE02E, 'mark:e', 0xE022, 0xE015, 'mark:o'],
]
SINDARIN = [
    [0xE001, 0xE004, 'mark:e', 0xE02E, 'mark:o'],
    [0xE011, 0xE022, 'mark:e', 'mark:dblL', 0xE010, 'mark:o'],
    [0xE02E, 'mark:a'],
    [0xE011, 0xE010, 'mark:i', 'mark:dbl', 0xE02E, 'mark:o'],
]

files = {}
files['fig_geometry.tex'] = fig_geometry()
files['fig_slugs_adv.tex'] = row([(0xE000, 'tinco'), (0xE004, 'ando'), (0xE00A, 'harma'), (0xE028, 'hyarmen'),
                                  (0xE02E, 'telco'), ('combo:ára+e', 'ára+e')])
files['fig_slugs_dead.tex'] = row([('mark:a', 'a'), ('mark:e', 'e'), ('mark:nasW', 'нос. шир.'), ('mark:ddotb', 'y'),
                                   ('mark:dbl', 'удв. узк.'), ('mark:dblL', 'удв. lambe')])
files['keyboard.tex'] = keyboard()
files['tab_codes.tex'] = tab_codes()
tq, evq = fig_trace(QUENYA); files['fig_trace_q.tex'] = tq; files['tab_trace_q.tex'] = trace_table(evq)
ts, evs = fig_trace(SINDARIN); files['fig_trace_s.tex'] = ts; files['tab_trace_s.tex'] = trace_table(evs)
for n, c in files.items():
    open(os.path.join(out, n), 'w').write(c)

adv_items = [it for it in ITEMS.values() if it['kind'] in ADV]
st = dict(slots=len(used), w=(min(i['w'] for i in adv_items), max(i['w'] for i in adv_items)),
          b=(min(i['b'] for i in adv_items), max(i['b'] for i in adv_items)),
          c=(min(i['c'] for i in adv_items), max(i['c'] for i in adv_items)),
          w_levels=sorted({i['w'] for i in adv_items}), b_levels=sorted({i['b'] for i in adv_items}),
          c_levels=sorted({i['c'] for i in adv_items}),
          missing=sorted(set(map(str, list(ITEMS))) - set(map(str, used))))
json.dump(st, open(os.path.join(out, 'stats.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(st, ensure_ascii=False))
