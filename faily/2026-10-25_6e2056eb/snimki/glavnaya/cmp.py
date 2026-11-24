import sys, pickle, itertools, collections
sys.path.insert(0, '/root/eldamo_phr')
from shared.interpreter import comparable, is_vowel, phonemes
from shared.sequencer import Sequencer
SP = '/tmp/claude-0/-home-claude/646e4be4-2daf-5c80-8156-dad6592ad30c/scratchpad/'


def origins(e):
    out = list(e.get('starts', ())) + list(e.get('stages', {}).get('p', ())) + list(e.get('stages', {}).get('mp', ()))
    for w in e.get('written_origins', ()):
        if w.upper() != w:
            out.append(w)
    clean = []
    for f in out:
        f = f.replace('-', '').replace('(', '').replace(')', '')
        f = ''.join(ch for ch in f if ch not in '́')
        if f and f not in clean:
            clean.append(f)
    return clean


def joins(a, b):
    yield a + '+' + b
    pa = phonemes(a)
    if pa and is_vowel(pa[-1]):
        yield ''.join(pa[:-1]) + '+' + b


for br in sys.argv[1:] or ['quenya', 'sindarin']:
    data = pickle.load(open(SP + br + '.pkl', 'rb'))
    lex = pickle.load(open(SP + f'lex_{br}.pkl', 'rb'))
    L = {e['id']: e for e in lex}
    D = {d['id']: d for d in data['derivations']}
    seq = Sequencer(data)
    langs = seq.langs
    stats = collections.Counter()
    for e in lex:
        if not (e.get('elements') and e.get('derivations')) or e.get('neo') or len(e['elements']) != 2:
            continue
        els = [L.get(x.get('id')) for x in e['elements']]
        if not all(x and origins(x) for x in els):
            continue
        for did in e['derivations']:
            d = D[did]
            codes = [s['lang'] for s in d['steps'] if s['lang'] in langs]
            if not codes:
                continue
            stats['n'] += 1
            era = langs[codes[0]]['era']
            target = comparable(d['steps'][-1]['after'])
            start = comparable(d['start'])
            cands = []
            for a, b in itertools.product(origins(els[0]), origins(els[1])):
                for j in joins(a, b):
                    if j not in cands:
                        cands.append(j)
            joined = [c for c in cands if comparable(c) == start]
            if joined:
                stats['join_ok'] += 1
            rules = seq.sequence(era, 0, langs[codes[-1]]['stage'])
            preds = []
            for c in (joined or cands)[:6]:
                for v in seq.run(c, rules):
                    preds.append(comparable(v['form']))
            if preds and preds[0] == target:
                stats['pred_main'] += 1
            if target in preds:
                stats['pred_any'] += 1
            ok = target in preds
            if len(sys.argv) > 2 or stats['n'] <= 25:
                print(('OK ' if ok else '-- ') + e['form'], '| start', d['start'], '| cands', cands[:4], '| target', d['steps'][-1]['after'], '| got', preds[:3])
    print(br, dict(stats))
