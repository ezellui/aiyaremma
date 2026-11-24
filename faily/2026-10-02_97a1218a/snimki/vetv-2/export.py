"""K1 decisions.json -> K1-add.json, K1-provenance.json, K1-review.md (заход K1: кандидаты в новые связи).
    python export.py <клон philosphaira> [папка вывода]
Папка вывода по умолчанию — decisions/sources/hwph клона. Имена новых связей вычисляются так же, как в
tools/edit/add_relation_ids.mjs: 'rel_' + sha1(источник \\0 цель \\0 тип)[:12]."""
import collections, hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, 'decisions/sources/hwph')
D = lambda p: json.load(open(os.path.join(REPO, 'app/data', p), encoding='utf-8'))
C = {c['id']: c for c in D('concepts.json')}
P = {p['id']: p['nameRu'] for p in D('philosophers.json')}
R = D('relations.json')
d = json.load(open(os.path.join(HERE, 'decisions.json'), encoding='utf-8'))
rid = lambda a: 'rel_' + hashlib.sha1(f"{a['source']}\0{a['target']}\0{a['type']}".encode()).hexdigest()[:12]
lab = lambda c: f"{C[c]['label']} ({P[C[c]['philosopher']]})"

adds = d['adds']
for k, a in adds.items():
    for x in (a['source'], a['target']):
        assert x in C, (k, x)
    pair = {C[a['source']]['philosopher'], C[a['target']]['philosopher']}
    dup = [r for r in R if {r['source'], r['target']} == {a['source'], a['target']}]
    assert not dup, (k, 'пара концепций уже связана', dup)
os.makedirs(OUT, exist_ok=True)
json.dump({'edits': [{k: a[k] for k in ('source', 'target', 'type', 'weight', 'description')} for a in adds.values()]},
          open(os.path.join(OUT, 'K1-add.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
prov = [dict(kind='relation', id=rid(a), status=a['status'], provenance=a['provenance']) for a in adds.values()]
json.dump({'entries': prov}, open(os.path.join(OUT, 'K1-provenance.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

cs = d['candidates']
vc = collections.Counter(x['verdict'] for x in cs)
st = collections.Counter(a['status'] for a in adds.values())
L = [f"# Кандидаты в новые связи — заход K1 ({d['date']})\n",
     f"Прочитаны все {len(cs)} кандидатов `candidate_relations.json`, посчитанных мостом по данным исходника после всех файлов правок (H1–F2): "
     "две концепции разных философов, чьи статьи HWPh совпадают или связаны перекрёстной ссылкой, и оба философа названы в одном абзаце. "
     "Инструмент — `bridge/read_brief.py --candidates`; при каждом кандидате выписаны уже существующие связи этой пары философов в обе стороны.\n",
     f"Итог: заведено {len(adds)} связей ({vc['add']} кандидатов напрямую, {vc['redirect']} переадресованы к другой концепции той же пары; "
     f"основание — источник {st['sourced']}, основание составителя {st['editorial_reasoning']}); "
     f"пара уже связана — {vc['covered']}; отклонено — {vc['reject']}; ждут ответа автора (AUTHOR-DECISIONS §4) — {vc['author']}.\n",
     'Порядок применения: `add_links` K1-add (вместе с H1/R2/P1-add) → `add_relation_ids` → `set_provenance` K1-provenance; всё — в `apply_all.sh`.\n',
     '## Новые связи (K1-add)\n']
for k, a in adds.items():
    ns = [x['n'] for x in cs if x.get('add') == k]
    L.append(f"- **{rid(a)}: {lab(a['source'])} —{a['type']}/{a['weight']}→ {lab(a['target'])}** — кандидаты № {', '.join(map(str, ns)) if ns else '—'}; "
             f"{'источник' if a['status'] == 'sourced' else 'основание составителя'}: {a['provenance']}")
    L.append(f"  - «{a['description']}»")
names = {'add': 'Заведены', 'redirect': 'Переадресованы', 'author': 'Ждут ответа автора', 'covered': 'Пара уже связана', 'reject': 'Отклонены'}
for v in ('add', 'redirect', 'author', 'covered', 'reject'):
    L.append(f'\n## {names[v]} ({vc[v]})\n')
    L.append('| № | Кандидат | Место HWPh | Почему |\n|---|---|---|---|')
    for x in cs:
        if x['verdict'] == v:
            L.append(f"| {x['n']} | {lab(x['older'])} → {lab(x['younger'])} | {x['cite'].replace('HWPh, ', '')} | {x['note'].replace('|', '/')} |")
open(os.path.join(OUT, 'K1-review.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('связей', len(adds), '| оснований', len(prov), '|', dict(vc))
