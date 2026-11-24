"""Generate LaTeX/TikZ fragments for the tengwar typewriter design document.
Usage: python3 -I gen.py FONT DATA_DIR OUT_DIR
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fontTools.ttLib import TTFont
import inventory as inv
import layout as lay

font_path, data_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
F = TTFont(font_path)
GID = {n: i for i, n in enumerate(F.getGlyphOrder())}
D = json.load(open(os.path.join(data_dir, 'codes.json')))
U = D['U']
cmap = F.getBestCmap()
SPACE_W = 6   # u, wide space
SPACE_N = 4   # u, narrow space

# ---------- item registry ----------
ITEMS = {}
for t in D['tengwar']:
    ITEMS[t['cp']] = dict(kind='T', label=t['name'], w=t['w'], a=t['a'], b=t['b'],
                          d=round(t['d_bot']), dres=t['d_bot'] - round(t['d_bot']),
                          glyph=t['glyph'], ax=t['top'][0], adv=t['adv'], cps=[t['cp']],
                          spl=t['a'] * U - t['top'][0], spr=t['b'] * U - (t['adv'] - t['top'][0]))
for t in D['numerals'] + D['punct']:
    g = t['glyph']; adv = t['adv']
    ax = t['a'] * U if not t['has_anchor'] else None
    # use real anchor when exists
    ITEMS[t['cp']] = dict(kind='N' if t in D['numerals'] else 'P', label=t['name'], w=t['w'], a=t['a'],
                          b=t['b'], d=0, dres=0, glyph=g, ax=None, adv=adv, cps=[t['cp']])
for c in D['combos']:
    car = ITEMS[0xE02C]
    mk = {0xE040: 'uniE040', 0xE046: 'uniE046', 0xE044: 'uniE044', 0xE04A: 'uniE04A', 0xE04C: 'uniE04C'}[c['cps'][1]]
    ITEMS['combo:' + c['name']] = dict(kind='C', label=c['name'], w=c['w'], a=c['a'], b=c['b'], d=0,
                                      dres=0, glyph=car['glyph'], mark=mk, ax=car['ax'], adv=car['adv'],
                                      cps=c['cps'])
for m in D['marks']:
    ITEMS['mark:' + m['key']] = dict(kind=m['kind'], label=m['role'], w=0, a=0, b=0, d=0, glyph=m['glyph'],
                                     ax=m['anchor'][0], adv=0, length=m['length'],
                                     below=m['kind'] in ('DB', 'DL', 'DX'))
# anchors of numerals/punct (when the font has them)
import measure_helpers as mh  # noqa: E402  (small helper, created alongside)
for k, it in ITEMS.items():
    if it['ax'] is None:
        it['ax'] = mh.top_anchor(F, it['glyph'], it['adv'])
    if it['kind'] in ('N', 'P'):
        it['spl'] = it['a'] * U - it['ax']; it['spr'] = it['b'] * U - (it['adv'] - it['ax'])

MARK_CP = {'mark:a': 0xE040, 'mark:e': 0xE046, 'mark:i': 0xE044, 'mark:o': 0xE04A, 'mark:u': 0xE04C,
           'mark:tilde': 0xE052, 'mark:nas': 0xE050, 'mark:nasW': 0xE050, 'mark:dotb': 0xE045,
           'mark:ddotb': 0xE043, 'mark:dbl': 0xE051, 'mark:dblW': 0xE051, 'mark:dblL': 0xE051, 'mark:lsd': 0xE07D}


def gl(name, x=0, y=0, extra=''):
    """TikZ node placing glyph `name` with its origin at (x,y) in font units."""
    return (f"\\node[anchor=base west,inner sep=0pt,outer sep=0pt{extra}] at ({x:.1f},{y:.1f}) "
            f"{{\\TG{{{GID[name]}}}}};\n")


def hexs(cp):
    return f"{cp:04X}"


def item_glyph_inline(key, size='\\tgsmall'):
    """Inline rendering of an item for tables (HarfBuzz shaping, dotted circle for marks)."""
    it = ITEMS[key]
    if it['kind'] in ('T', 'N', 'P'):
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}}}"
    if it['kind'] == 'C':
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}\\symbol{{\"{hexs(it['cps'][1])}}}}}"
    # marks: show on a neutral carrier glyph via direct glyph placement in a tiny tikz
    return (f"{{\\tikz[baseline=0pt,x=\\tgu,y=\\tgu]{{"
            f"\\draw[gray!60,densely dotted] (0,0) -- (0,520);"
            + gl(it['glyph'], -it['ax'], 0) + "}}}")


# ---------- tables ----------
def tex_name(s):
    return s.replace('ú', '\\'+"'"+'{u}') if False else s


def tab_tengwar():
    rows = []
    for t in D['tengwar']:
        it = ITEMS[t['cp']]
        rows.append(f"{item_glyph_inline(t['cp'])} & {t['name']} & {hexs(t['cp'])} & {t['adv']} & "
                    f"{it['w']} & {it['a']} & {it['b']} & {it['d']:+d} & "
                    f"{it['spl']/U:+.2f}/{it['spr']/U:+.2f} & {it['dres']:+.2f}\\\\\n")
    return ''.join(rows)


def tab_others():
    rows = []
    for key in [n['cp'] for n in D['numerals']] + [p['cp'] for p in D['punct']]:
        it = ITEMS[key]
        rows.append(f"{item_glyph_inline(key)} & {it['label']} & {hexs(key)} & {it['adv']} & {it['w']} & "
                    f"{it['a']} & {it['b']}\\\\\n")
    for c in D['combos']:
        key = 'combo:' + c['name']; it = ITEMS[key]
        rows.append(f"{item_glyph_inline(key)} & {c['name']} & 02C+\\ldots & {it['adv']} & {it['w']} & "
                    f"{it['a']} & {it['b']}\\\\\n")
    return ''.join(rows)


def tab_marks():
    rows = []
    kinds = {'DA': 'над осью', 'DB': 'под осью', 'DL': 'под/над, мерная', 'DX': 'особая (lambe)'}
    for m in D['marks']:
        key = 'mark:' + m['key']
        rows.append(f"{item_glyph_inline(key)} & {m['role']} & \\texttt{{{m['glyph'].replace('_', '-')}}} & "
                    f"{kinds[m['kind']]} & {m['length']/U:.1f} & {'да' if ITEMS[key]['below'] else 'нет'}\\\\\n")
    return ''.join(rows)


# ---------- figures ----------
EM_FIG = 26.0  # mm per em in detail figures


def fig_anatomy():
    picks = [0xE000, 0xE004, 0xE009, 0xE00A, 0xE028, 0xE022, 0xE02E]
    s = []
    x0 = 0
    for cp in picks:
        t = next(t for t in D['tengwar'] if t['cp'] == cp); it = ITEMS[cp]
        w = it['w'] * U; ax = it['a'] * U
        # cell
        s.append(f"\\fill[cellfill] ({x0},-330) rectangle ({x0 + w},740);\n")
        s.append(f"\\draw[cellline] ({x0},-330) -- ({x0},740); \\draw[cellline] ({x0 + w},-330) -- ({x0 + w},740);\n")
        # glyph: origin so that the true top anchor sits on the axis
        s.append(gl(it['glyph'], x0 + ax - it['ax'], 0))
        # axes
        s.append(f"\\draw[axisT] ({x0 + ax},-360) -- ({x0 + ax},800);\n")
        bx = x0 + ax + (t['bot'][0] - t['top'][0])
        s.append(f"\\draw[axisB] ({bx},-420) -- ({bx},120);\n")
        s.append(f"\\node[lbl,anchor=north] at ({x0 + w/2},-440) {{{t['name'].split(' (')[0]}}};\n")
        s.append(f"\\node[lbl,anchor=north] at ({x0 + w/2},-560) {{$w{{=}}{it['w']}$, $a{{=}}{it['a']}$}};\n")
        s.append(f"\\node[lbl,anchor=north] at ({x0 + w/2},-680) {{$d{{=}}{it['d']:+d}$}};\n")
        x0 += w + 160
    s.append(f"\\draw[base] (-80,0) -- ({x0 - 80},0);\n")
    return ''.join(s), x0


def slug(key, x0=0, show_dims=True, title=None, mark_on=None):
    """Draw a slug face (print-side view) for item `key` with cell, axis, dims."""
    it = ITEMS[key]; s = []
    if it['kind'] in ('T', 'C', 'N', 'P'):
        w = it['w'] * U; ax = it['a'] * U
        s.append(f"\\draw[slug] ({x0 - 60},-400) rectangle ({x0 + w + 60},820);\n")
        s.append(f"\\fill[cellfill] ({x0},-330) rectangle ({x0 + w},740);\n")
        s.append(gl(it['glyph'], x0 + ax - it['ax'], 0))
        if it['kind'] == 'C':
            mk = it['mark']; s.append(gl(mk, x0 + ax - ITEMS_MARK_AX[mk], 0))
        s.append(f"\\draw[axisT] ({x0 + ax},-460) -- ({x0 + ax},880);\n")
        if it['kind'] == 'T' and it['d']:
            s.append(f"\\draw[axisB] ({x0 + ax + it['d'] * U},-460) -- ({x0 + ax + it['d'] * U},120);\n")
        if show_dims:
            s.append(f"\\draw[dim] ({x0},-520) -- node[lbl,below]{{$a{{=}}{it['a']}$}} ({x0 + ax},-520);\n")
            s.append(f"\\draw[dim] ({x0 + ax},-520) -- node[lbl,below]{{$b{{=}}{it['b']}$}} ({x0 + w},-520);\n")
        width = w
    else:
        width = max(it['length'], 300) + 120
        cx = x0 + width / 2
        s.append(f"\\draw[slug] ({x0 - 60},-400) rectangle ({x0 + width + 60},820);\n")
        if mark_on is not None:
            b = ITEMS[mark_on]
            s.append(gl(b['glyph'], cx - b['ax'], 0, extra=',ghost'))
        s.append(gl(it['glyph'], cx - it['ax'], 0))
        s.append(f"\\draw[axisT] ({cx},-460) -- ({cx},880);\n")
        if show_dims:
            s.append(f"\\node[lbl] at ({cx},-560) {{$w{{=}}0$}};\n")
    if title:
        s.append(f"\\node[lbl,anchor=south] at ({x0 + width/2},900) {{{title}}};\n")
    return ''.join(s), width


ITEMS_MARK_AX = {m['glyph']: m['anchor'][0] for m in D['marks']}


def fig_slug_row(keys, titles, gap=260, mark_on=None):
    s = []; x = 0
    for k, ttl in zip(keys, titles):
        code, w = slug(k, x, title=ttl, mark_on=mark_on)
        s.append(code); x += w + gap
    return ''.join(s)


# ---------- keyboard ----------
def keyboard():
    s = []
    KW, KH, G = 15.0, 15.0, 1.6     # mm
    offs = [0, 7, 10, 14]
    for r, row in enumerate(lay.ROWS):
        for c, (lo, up) in enumerate(row):
            x = offs[r] + c * (KW + G); y = -r * (KH + G)
            kinds = [ITEMS[k]['kind'] if k is not None else None for k in (lo, up)]
            dead_lo = kinds[0] and kinds[0].startswith('D')
            fill = 'keydead' if dead_lo else 'keyadv'
            s.append(f"\\draw[key,fill={fill}] ({x},{y}) rectangle +({KW},{-KH});\n")
            s.append(f"\\node[keyleg] at ({x + 1.6},{y - 1.6}) {{\\texttt{{{lay.LEGENDS[r][c]}}}}};\n")
            for k, pos in ((up, 'up'), (lo, 'lo')):
                if k is None:
                    if pos == 'up':
                        s.append(f"\\node[keyres] at ({x + KW/2},{y - 4.2}) {{резерв}};\n")
                    continue
                yy = y - 5.6 if pos == 'up' else y - 12.2
                s.append(f"\\node[anchor=base,inner sep=0pt,{('keyup' if pos == 'up' else 'keylo')}] at ({x + KW/2},{yy}) {{{key_face(k, pos)}}};\n")
    # function keys
    y = -4 * (KH + G)
    s.append(f"\\draw[key,fill=keyfn] (0,{y}) rectangle +({KW*1.6},{-KH*0.8}); \\node[fnleg] at ({KW*0.8},{y - KH*0.4}) {{РЕГИСТР}};\n")
    s.append(f"\\draw[key,fill=keyfn] ({KW*1.6 + G},{y}) rectangle +({KW*1.3},{-KH*0.8}); \\node[fnleg,align=center] at ({KW*1.6 + G + KW*0.65},{y - KH*0.4}) {{$\\leftarrow$u}};\n")
    sx = KW*2.9 + 2*G
    s.append(f"\\draw[key,fill=keyfn] ({sx},{y}) rectangle +({KW*3.2},{-KH*0.8}); \\node[fnleg] at ({sx + KW*1.6},{y - KH*0.4}) {{ПРОБЕЛ {SPACE_N}u}};\n")
    sx2 = sx + KW*3.2 + G
    s.append(f"\\draw[key,fill=keyfn] ({sx2},{y}) rectangle +({KW*3.2},{-KH*0.8}); \\node[fnleg] at ({sx2 + KW*1.6},{y - KH*0.4}) {{ПРОБЕЛ {SPACE_W}u}};\n")
    sx3 = sx2 + KW*3.2 + G
    s.append(f"\\draw[key,fill=keyfn] ({sx3},{y}) rectangle +({KW*1.3},{-KH*0.8}); \\node[fnleg] at ({sx3 + KW*0.65},{y - KH*0.4}) {{u$\\rightarrow$}};\n")
    sx4 = sx3 + KW*1.3 + G
    s.append(f"\\draw[key,fill=keyfn] ({sx4},{y}) rectangle +({KW*1.9},{-KH*0.8}); \\node[fnleg,align=center] at ({sx4 + KW*0.95},{y - KH*0.4}) {{НАЗАД\\\\НА ЛИТЕРУ}};\n")
    return ''.join(s)


def key_face(k, pos):
    it = ITEMS[k]
    size = '\\tgkeyU' if pos == 'up' else '\\tgkeyL'
    if it['kind'] in ('T', 'N', 'P'):
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}}}"
    if it['kind'] == 'C':
        return f"{{{size}\\symbol{{\"{hexs(it['cps'][0])}}}\\symbol{{\"{hexs(it['cps'][1])}}}}}"
    # dead mark: draw glyph centred with dotted axis
    scale = '\\tgkuU' if pos == 'up' else '\\tgkuL'
    return (f"\\tikz[baseline=0pt,x={scale},y={scale}]{{\\draw[gray!55,densely dotted] (0,-150) -- (0,650);"
            + gl(it['glyph'], -it['ax'], 0).replace('\\TG{', '\\TGk' + ('U' if pos == 'up' else 'L') + '{') + "}")


# ---------- simulation ----------
def simulate(words):
    """words: list of lists of item keys. Returns events + placed glyphs."""
    R = dict(a=0, b=0, d=0)
    X = 0  # carriage print point in u
    events, placed = [], []
    for wi, word in enumerate(words):
        if wi:
            move = R['b'] + SPACE_W
            X += move
            events.append(dict(key='space', move=move, X=X, R=(0, 0, 0), strike=False))
            R = dict(a=0, b=0, d=0)
        for k in word:
            it = ITEMS[k]
            if it['kind'] in ('T', 'C', 'N', 'P'):
                move = R['b'] + it['a']; X += move
                placed.append(('base', k, X))
                R = dict(a=it['a'], b=it['b'], d=it['d'])
                events.append(dict(key=k, move=move, X=X, R=(R['a'], R['b'], R['d']), strike=True))
            else:
                off = R['d'] if it['below'] else 0
                placed.append(('mark', k, X + off))
                events.append(dict(key=k, move=0, X=X, off=off, R=(R['a'], R['b'], R['d']), strike=True))
    X += R['b']
    events.append(dict(key='end', move=R['b'], X=X, R=(0, 0, 0), strike=False))
    return events, placed, X


def render_machine(placed, y=0):
    s = []
    for kind, k, X in placed:
        it = ITEMS[k]
        if kind == 'base':
            s.append(gl(it['glyph'], X * U - it['ax'], y))
            if it['kind'] == 'C':
                s.append(gl(it['mark'], X * U - ITEMS_MARK_AX[it['mark']], y))
        else:
            s.append(gl(it['glyph'], X * U - it['ax'], y))
    return ''.join(s)


def unicode_string(words):
    out = []
    for wi, word in enumerate(words):
        if wi:
            out.append('\\ ')
        for k in word:
            it = ITEMS[k]
            if k in MARK_CP:
                out.append(f"\\symbol{{\"{hexs(MARK_CP[k])}}}")
            else:
                out.extend(f"\\symbol{{\"{hexs(c)}}}" for c in it['cps'])
    return ''.join(out)


def trace_table(events):
    rows = []; n = 0
    for e in events:
        if e['key'] == 'space':
            rows.append(f"— & пробел {SPACE_W}u & $+{e['move']}$ & {e['X']} & 0, 0, 0\\\\\n"); continue
        if e['key'] == 'end':
            rows.append(f"— & (закрытие строки) & $+{e['move']}$ & {e['X']} & —\\\\\n"); continue
        n += 1; it = ITEMS[e['key']]
        what = item_glyph_inline(e['key'])
        kind = {'T': 'тенгва', 'C': 'ára+техта', 'N': 'цифра', 'P': 'знак',
                'DA': 'техта', 'DB': 'подстр. знак', 'DL': 'мерный знак', 'DX': 'особый знак'}[it['kind']]
        mv = f"$+{e['move']}$" if e['move'] else ('0' if not e.get('off') else f"$\\pm{abs(e['off'])}$ (сдвиг $d$)")
        rows.append(f"{n} & {what}\\ {kind} & {mv} & {e['X']} & {e['R'][1]}, {e['R'][2]:+d}, {e['R'][0]}\\\\\n")
    return ''.join(rows)


def fig_trace(words, ref_y=-1250):
    ev, placed, Xend = simulate(words)
    s = [render_machine(placed, 0)]
    s.append(f"\\node[anchor=base west,inner sep=0pt] at (0,{ref_y}) {{\\TGtext{{{unicode_string(words)}}}}};\n")
    # axis ticks of machine strikes
    for kind, k, X in placed:
        if kind == 'base':
            s.append(f"\\draw[axisT,thin] ({X*U},-380) -- ({X*U},-300);\n")
    s.append(f"\\draw[base] (0,0) -- ({Xend*U},0); \\draw[base] (0,{ref_y}) -- ({Xend*U},{ref_y});\n")
    s.append(f"\\node[lbl,anchor=east] at (-60,250) {{машинка}};\n")
    s.append(f"\\node[lbl,anchor=east] at (-60,{ref_y + 250}) {{шрифт}};\n")
    return ''.join(s), ev


# ---------- examples ----------
q = lambda name: name
QUENYA = [
    [0xE02E, 'mark:e', 0xE022, 'mark:e', 0xE010],                       # elen
    [0xE024, 'combo:ára+i', 0xE022, 'mark:a'],                          # síla
    [0xE022, 'combo:ára+u', 0xE011, 'mark:e', 0xE010, 'mark:dbl'],      # lúmenn'
    [0xE02E, 'mark:o', 0xE011, 'mark:e', 0xE00C, 'mark:i', 0xE02E, 'mark:e', 0xE022, 0xE015, 'mark:o'],  # omentielvo
]
SINDARIN = [
    [0xE001, 0xE004, 'mark:e', 0xE02E, 'mark:o'],                       # pedo
    [0xE011, 0xE022, 'mark:e', 'mark:dblL', 0xE010, 'mark:o'],          # mellon
    [0xE02E, 'mark:a'],                                                  # a
    [0xE011, 0xE010, 'mark:i', 'mark:dbl', 0xE02E, 'mark:o'],           # minno
]

files = {
    'tab_tengwar.tex': tab_tengwar(),
    'tab_others.tex': tab_others(),
    'tab_marks.tex': tab_marks(),
    'keyboard.tex': keyboard(),
}
an, _ = fig_anatomy(); files['fig_anatomy.tex'] = an
files['fig_slugs_T.tex'] = fig_slug_row([0xE000, 0xE004, 0xE00A, 0xE028, 0xE02E],
                                        ['узкая', 'широкая', 'ось смещена', 'hyarmen', 'носитель'])
files['fig_slugs_D.tex'] = fig_slug_row(['mark:a', 'mark:e', 'mark:o', 'mark:ddotb', 'mark:dbl', 'mark:dblW', 'mark:dblL'],
                                        ['a', 'e', 'o', 'y', 'удв. узк.', 'удв. шир.', 'удв. lambe'])
files['fig_slugs_C.tex'] = fig_slug_row(['combo:ára+a', 'combo:ára+e', 0xE058, 0xE060, 0xE073],
                                        ['ára+a', 'ára+e', 'sa-rincë', 'пуста', 'цифра 3'])
tq, evq = fig_trace(QUENYA); files['fig_trace_q.tex'] = tq; files['tab_trace_q.tex'] = trace_table(evq)
ts, evs = fig_trace(SINDARIN); files['fig_trace_s.tex'] = ts; files['tab_trace_s.tex'] = trace_table(evs)

# stats for text
st = {}
ts_ = D['tengwar']
st['max_side_err'] = max(max(abs(ITEMS[t['cp']]['spl']), abs(ITEMS[t['cp']]['spr'])) for t in ts_) / U
st['max_dres'] = max(abs(ITEMS[t['cp']]['dres']) for t in ts_)
st['d_hist'] = {}
for t in ts_:
    st['d_hist'][ITEMS[t['cp']]['d']] = st['d_hist'].get(ITEMS[t['cp']]['d'], 0) + 1
st['w_hist'] = {}
for t in ts_:
    st['w_hist'][t['w']] = st['w_hist'].get(t['w'], 0) + 1
st['slots_used'] = sum(1 for row in lay.ROWS for pair in row for k in pair if k is not None)
used = [k for row in lay.ROWS for pair in row for k in pair if k is not None]
st['dups'] = [k for k in set(map(str, used)) if list(map(str, used)).count(k) > 1]
all_items = set(map(str, [t['cp'] for t in ts_] + [n['cp'] for n in D['numerals']] + [p['cp'] for p in D['punct']]
                     + ['combo:' + c['name'] for c in D['combos']] + ['mark:' + m['key'] for m in D['marks']]))
st['missing'] = sorted(all_items - set(map(str, used)))
st['a_max'] = max(it['a'] for it in ITEMS.values()); st['b_max'] = max(it['b'] for it in ITEMS.values())
st['d_range'] = (min(it['d'] for it in ITEMS.values()), max(it['d'] for it in ITEMS.values()))
json.dump(st, open(os.path.join(out, 'stats.json'), 'w'), ensure_ascii=False, indent=1)
for n, c in files.items():
    open(os.path.join(out, n), 'w').write(c)
print(json.dumps(st, ensure_ascii=False))
