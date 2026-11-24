"""Approximate keystroke frequencies of the TPM layout for Elvish text.
A small transcriber (tehta mode: a vowel sign sits on the consonant before it, otherwise on a carrier;
long vowels on ára; doubled consonants with the doubling bar) is run over a sample of names and phrases.
The result is approximate; it is used to order the shuttle rows and to weight the cycle times.
Usage: python3 -I freq.py OUT_JSON"""
import sys, os, json, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import layout as lay

# names and short phrases from the legendarium (proper names; no running text is reproduced)
SAMPLE = """
elen sila lumenn omentielvo  pedo mellon a minno  namarie  aiya earendil elenion ancalima
elendil isildur anarion earendil elrond elros galadriel celeborn lothlorien valinor iluvatar manwe varda
elbereth gilthoniel feanor fingolfin finarfin finrod fingon turgon maedhros maglor celegorm curufin
silmarilli laurelin telperion tirion taniquetil arda ainur valar maiar eldar quendi noldor vanyar teleri
sindar nandor doriath gondolin nargothrond beleriand mithrandir aragorn arwen undomiel luthien tinuviel
beren melkor morgoth sauron angband thangorodrim numenor anduril narsil minas tirith osgiliath gondor
arnor ithilien rohan imladris nenya vilya narya anduin mordor orodruin ered luin hithlum dorthonion
nevrast vinyamar alqualonde tol eressea avallone eldamar aman ulmo aule yavanna nienna orome vana nessa
tulkas mandos lorien este vaire irmo namo olorin curumo aiwendil nolofinwe finwe miriel indis ingwe olwe
elwe thingol melian idril tuor maeglin ecthelion glorfindel gil galad cirdan oropher thranduil legolas
amroth nimrodel celebrian elladan elrohir estel elessar telcontar earnur meneldil tarannon atanatari
edain hador beor haleth hurin turin nienor morwen rian huor tuor dior elwing nimloth lindon eriador
""".split()


def norm(w):
    w = w.lower().replace('ë', 'e').replace('ä', 'a').replace('’', '')
    return w


ITEM = {}            # item key -> (keyboard row r, column c, tier)
for r, rw in enumerate(lay.ROWS):
    for c, pair in enumerate(rw):
        for tier, it in enumerate(pair):
            if it is not None and it not in ITEM:
                ITEM[it] = (r, c, tier)

T = {'tinco': 0xE000, 'parma': 0xE001, 'calma': 0xE002, 'quesse': 0xE003, 'ando': 0xE004, 'umbar': 0xE005, 'anga': 0xE006,
     'ungwe': 0xE007, 'thule': 0xE008, 'formen': 0xE009, 'harma': 0xE00A, 'hwesta': 0xE00B, 'anto': 0xE00C, 'ampa': 0xE00D,
     'anca': 0xE00E, 'unque': 0xE00F, 'numen': 0xE010, 'malta': 0xE011, 'noldo': 0xE012, 'nwalme': 0xE013, 'ore': 0xE014,
     'vala': 0xE015, 'anna': 0xE016, 'vilya': 0xE017, 'romen': 0xE020, 'arda': 0xE021, 'lambe': 0xE022, 'alda': 0xE023,
     'silme': 0xE024, 'silme_n': 0xE025, 'esse': 0xE026, 'hyarmen': 0xE028, 'yanta': 0xE02A, 'ure': 0xE02B,
     'ara': 0xE02C, 'telco': 0xE02E}
CONS = [('nqu', 'unque'), ('ngw', 'ungwe'), ('qu', 'quesse'), ('nw', 'nwalme'), ('nd', 'ando'), ('mb', 'umbar'),
        ('ng', 'anga'), ('nt', 'anto'), ('mp', 'ampa'), ('nc', 'anca'), ('ld', 'alda'), ('rd', 'arda'), ('ss', 'esse'),
        ('th', 'thule'), ('dh', 'anto'), ('ch', 'harma'), ('hw', 'hwesta'), ('ph', 'formen'),
        ('t', 'tinco'), ('p', 'parma'), ('c', 'quesse'), ('k', 'quesse'), ('d', 'ando'), ('b', 'umbar'), ('g', 'anga'),
        ('f', 'formen'), ('h', 'hyarmen'), ('n', 'numen'), ('m', 'malta'), ('v', 'vala'), ('w', 'vilya'), ('y', 'anna'),
        ('l', 'lambe'), ('s', 'silme'), ('z', 'esse'), ('x', 'quesse'), ('j', 'anga'), ('r', 'romen')]
VOW = 'aeiou'


def transcribe(word):
    """-> list of layout item keys in typing order."""
    w = unicodedata.normalize('NFD', norm(word))
    toks = []
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in VOW:
            long_ = i + 1 < len(w) and w[i + 1] == '́'
            toks.append(('V', ch, long_)); i += 2 if long_ else 1; continue
        if not ch.isalpha():
            i += 1; continue
        for s, name in CONS:
            if w.startswith(s, i):
                toks.append(('C', name)); i += len(s); break
        else:
            i += 1
    out = []
    last_cons = False            # previous output is a consonant without a vowel sign yet
    prev = None
    for k, t in enumerate(toks):
        if t[0] == 'C':
            name = t[1]
            if name == 'romen' and (k + 1 >= len(toks) or toks[k + 1][0] != 'V'):
                name = 'ore'
            if prev and prev[0] == 'C' and prev[1] == name:          # doubled consonant
                out.append('mark:dblL' if name == 'lambe' else 'mark:dbl'); prev = t; continue
            out.append(T[name]); last_cons = True
        else:
            v, long_ = t[1], t[2]
            if long_:
                out.append('combo:ára+' + v); last_cons = False
            elif last_cons:
                out.append('mark:' + v); last_cons = False
            else:
                out.append(T['telco']); out.append('mark:' + v); last_cons = False
        prev = t
    return out


if __name__ == '__main__':
    counts = {}
    n = 0
    for w in SAMPLE:
        for it in transcribe(w):
            if it not in ITEM:
                continue
            counts[repr(it)] = counts.get(repr(it), 0) + 1; n += 1
    rows = {}
    for k, v in counts.items():
        r, c, tier = ITEM[eval(k)]
        rows[f'{r},{tier}'] = rows.get(f'{r},{tier}', 0) + v
    res = dict(n=n, words=len(SAMPLE), items=counts, rows={k: v / n for k, v in sorted(rows.items(), key=lambda a: -a[1])})
    json.dump(res, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
    print(n, 'keystrokes;', {k: round(v, 3) for k, v in res['rows'].items()})
