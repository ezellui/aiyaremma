"""Compact view of entries of nq-roots.json: python show.py nq-roots.json form [form...]"""
import json
import sys


def fmt_root(r):
    s = f"{r['lang']} {r['form']}"
    if 'part' in r:
        s = f"[{r['part']}] " + s
    if r.get('via'):
        s += '  ⟵ ' + ' ⟵ '.join(f"{v['rel']}:{v['lang']} {v['form']}" for v in r['via'])
    if r.get('same_as'):
        s += '  ≡ ' + ' ≡ '.join(f"{x['lang']} {x['form']}" for x in r['same_as'])
    if r.get('rule'):
        s += f"  ({r['rule']})"
    return s


def show(e):
    print(f"{e['lang']} {e['word']} ({e['speech']}) '{e['gloss']}'  rule={e['rule']}  {e['url']}")
    for r in e['roots']:
        print('   root', fmt_root(r))
    for r in e.get('gaps', []):
        print('   gap ', fmt_root(r))
    for r in e.get('also', []):
        print('   also', fmt_root(r))


if __name__ == '__main__':
    doc = json.load(open(sys.argv[1], encoding='utf-8'))
    want = set(sys.argv[2:])
    for e in doc['words']:
        if e['word'] in want or e['spelling'] in want:
            show(e)
