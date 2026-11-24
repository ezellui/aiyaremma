"""C1 decisions.json -> decisions/sources/hwph/<TAG>-provenance.json (kind: concept) for set_provenance.mjs.

    python export.py <клон philosphaira> C1

Проверки: каждая концепция есть в app/data/concepts.json; отрезок сноски `after` встречается
ровно один раз в extendedDescription (сноски у концепции только в полном описании) и ни разу
в кратком; у sourced и editorial_reasoning есть текст основания.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO, TAG = sys.argv[1], sys.argv[2]
C = {c['id']: c for c in json.load(open(os.path.join(REPO, 'app/data/concepts.json'), encoding='utf-8'))}
d = json.load(open(os.path.join(HERE, 'decisions.json'), encoding='utf-8'))
prov, problems = [], []
for x in d:
    if x['verdict'] not in ('sourced', 'editorial_reasoning'): continue
    c = C.get(x['id'])
    if not c: problems.append(f"{x['id']}: концепции нет"); continue
    if not x.get('provenance'): problems.append(f"{x['id']}: нет текста основания")
    ext = c.get('extendedDescription', '')
    for f in x.get('footnotes', []):
        n = ext.count(f['after'])
        if n != 1: problems.append(f"{x['id']}: отрезок сноски в полном описании {n} раз")
        if f['after'] in c.get('description', ''): problems.append(f"{x['id']}: отрезок сноски стоит и в кратком описании")
    e = dict(kind='concept', id=x['id'], status=x['verdict'], provenance=x['provenance'])
    if x.get('footnotes'): e['footnotes'] = x['footnotes']
    prov.append(e)
out = os.path.join(REPO, 'decisions/sources/hwph'); os.makedirs(out, exist_ok=True)
json.dump({'entries': prov}, open(os.path.join(out, f'{TAG}-provenance.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('основания', len(prov), '| сносок', sum(len(e.get('footnotes', [])) for e in prov), '| ошибки:', problems or 'нет')
