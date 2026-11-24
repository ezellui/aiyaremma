"""Items of the layout (advancing characters, dead marks) from measured codes (data/codes.json or fontprof.codes_at).
rev. 0.11: shared by gen_shuttle.py (the document) and model/data.py (the model, any font set)."""
BELOW_MARKS = {'dotb', 'ddotb', 'dbl', 'dblW', 'dblL', 'lsd'}
MARK_CP = {'mark:a': 0xE040, 'mark:e': 0xE046, 'mark:i': 0xE044, 'mark:o': 0xE04A, 'mark:u': 0xE04C,
           'mark:tilde': 0xE052, 'mark:nas': 0xE050, 'mark:nasW': 0xE050, 'mark:dotb': 0xE045,
           'mark:ddotb': 0xE043, 'mark:dbl': 0xE051, 'mark:dblW': 0xE051, 'mark:dblL': 0xE051, 'mark:lsd': 0xE07D}
ADV = ('T', 'C', 'N', 'P')
VOWEL_KEY = {0xE040: 'a', 0xE046: 'e', 0xE044: 'i', 0xE04A: 'o', 0xE04C: 'u'}
# a character missing from a font: its cell has no glyph and the code of a narrow blank (the key types 4 u of space)
BLANK = dict(w=4, a=0, b=0, d=0, c=0, glyph=None, ax=0.0, adv=0.0)

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


def build_items(D, F=None):
    """-> ITEMS (key -> dict), MARK_AX (mark glyph -> anchor x). D: codes; F: the TTFont (Alcarin: anchors of the
    numerals and punctuation, which data/codes.json does not keep)."""
    U = D['U']
    ITEMS = {}
    for t in D['tengwar']:
        if t.get('missing'):
            ITEMS[t['cp']] = dict(kind='T', label=t['name'], cps=[t['cp']], missing=True, **BLANK); continue
        d = round(t['d_bot'])
        ITEMS[t['cp']] = dict(kind='T', label=t['name'], w=t['w'], a=t['a'], b=t['b'], d=d, c=t['b'] - d,
                              glyph=t['glyph'], ax=t['top'][0], adv=t['adv'], cps=[t['cp']],
                              spl=t['a'] * U - t['top'][0], spr=t['b'] * U - (t['adv'] - t['top'][0]))
    for grp, kind in (('numerals', 'N'), ('punct', 'P')):
        for t in D[grp]:
            if t.get('missing'):
                ITEMS[t['cp']] = dict(kind=kind, label=t['name'], cps=[t['cp']], missing=True, **BLANK); continue
            if 'ax' in t:
                ax = t['ax']
            else:
                import measure_helpers as mh
                ax = mh.top_anchor(F, t['glyph'], t['adv'])
            ITEMS[t['cp']] = dict(kind=kind, label=t['name'], w=t['w'], a=t['a'], b=t['b'], d=0, c=t['b'],
                                  glyph=t['glyph'], ax=ax, adv=t['adv'], cps=[t['cp']])
    MARK_AX = {m['glyph']: m['anchor'][0] for m in D['marks'] if not m.get('missing')}
    vowel = {m['key']: m['glyph'] for m in D['marks'] if not m.get('missing')}
    car = ITEMS[0xE02C]
    for c in D['combos']:
        if c.get('missing') or car.get('missing'):
            ITEMS['combo:' + c['name']] = dict(kind='C', label=c['name'], cps=c['cps'], missing=True, mark=None, **BLANK)
            continue
        mk = c.get('mark') or vowel[VOWEL_KEY[c['cps'][1]]]
        ITEMS['combo:' + c['name']] = dict(kind='C', label=c['name'], w=c['w'], a=c['a'], b=c['b'], d=0, c=c['b'],
                                          glyph=car['glyph'], mark=mk, ax=car['ax'], adv=car['adv'], cps=c['cps'])
    for m in D['marks']:
        if m.get('missing'):
            ITEMS['mark:' + m['key']] = dict(kind=m['kind'], label=m['role'], w=0, glyph=None, ax=0.0, length=0.0,
                                             below=m['key'] in BELOW_MARKS, missing=True)
            continue
        ITEMS['mark:' + m['key']] = dict(kind=m['kind'], label=m['role'], w=0, glyph=m['glyph'],
                                         ax=m['anchor'][0], length=m['length'], below=m['key'] in BELOW_MARKS)
    return ITEMS, MARK_AX
