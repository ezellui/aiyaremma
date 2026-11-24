"""Проверка черновика L1 по данным исходника после всех правок (раскладка app/data):
    python check.py <папка с app/data> [--md L1-review.md]
Имена концепций, пары (в обе стороны, с имеющимися и внутри черновика), типы и слой (логические —
внутри системы, исторические и типологические — между системами), bidirectional только у
несимметричных типов, рефлексивные — только самоприменение/самообоснование/противоречие/граница,
у каждой новой концепции — связь внутри своей системы, циклы обоснования внутри системы."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from draft import CONCEPTS, LINKS
D = lambda p: json.load(open(os.path.join(sys.argv[1], 'app/data', p), encoding='utf-8'))
C = {c['id']: c for c in D('concepts.json')}
P = {p['id']: p for p in D('philosophers.json')}
T = {t['id']: t for t in D('relationTypes.json')}
R = D('relations.json')
RUB = {r['id'] for r in D('rubrics.json')}
err, warn = [], []
new = {}
for cid, ph, label, rub, art in CONCEPTS:
    if cid in C: err.append(f'имя занято: {cid}')
    if ph not in P: err.append(f'нет философа {ph}')
    if any(c['philosopher'] == ph and c['label'] == label for c in C.values()): err.append(f'метка занята у {ph}: {label}')
    if set(rub) - RUB: err.append(f'рубрики {cid}: {set(rub) - RUB}')
    new[cid] = dict(id=cid, philosopher=ph, label=label)
ALL = {**C, **new}
REFLEXIVE = {'apply', 'presuppose', 'internal_contradiction', 'limit'}
seen = {}
for r in R:
    seen[frozenset((r['source'], r['target']))] = r
pairs = collections.Counter()
for l in LINKS:
    s, t, ty = l['s'], l['t'], l['type']
    for x in (s, t):
        if x not in ALL: err.append(f'нет концепции {x}')
    if ty not in T: err.append(f'нет типа {ty}'); continue
    if s not in ALL or t not in ALL: continue
    if s not in new and t not in new: err.append(f'связь без новой концепции: {s}→{t}')
    if l['w'] not in (1, 2, 3): err.append(f'вес {s}→{t}')
    same = ALL[s]['philosopher'] == ALL[t]['philosopher']
    layer = T[ty]['layer']
    if layer == 'logical' and not same: err.append(f'логический тип между системами: {s} —{ty}→ {t}')
    if layer in ('historical', 'typological') and same: err.append(f'{layer} внутри системы: {s} —{ty}→ {t}')
    if l.get('bi') and T[ty].get('symmetric'): err.append(f'bidirectional у симметричного типа: {s}→{t}')
    if s == t and ty not in REFLEXIVE: err.append(f'рефлексивная связь недопустимого типа {ty}: {s}')
    k = frozenset((s, t))
    if s != t and k in seen: err.append(f'пара уже связана: {s} —{ty}→ {t}  (есть {seen[k]["source"]} —{seen[k]["type"]}→ {seen[k]["target"]})')
    pairs[k] += 1
    if not same:
        a, b = P[ALL[s]['philosopher']], P[ALL[t]['philosopher']]
        if T[ty].get('temporal') == 'forward' and a['birth'] > b['birth'] + 30:
            warn.append(f'направление против хронологии: {s} ({a["birth"]}) —{ty}→ {t} ({b["birth"]})')
for k, n in pairs.items():
    if n > 1: err.append(f'пара дважды в черновике: {set(k)}')
for cid in new:
    if not any((l['s'] == cid or l['t'] == cid) and ALL[l['s']]['philosopher'] == ALL[l['t']]['philosopher'] and l['s'] != l['t'] for l in LINKS):
        err.append(f'нет связи внутри своей системы: {cid}')
# cycles of grounding inside each system (ground: source -> edge ground->grounded as is; target -> reversed)
edges = collections.defaultdict(set)
for r in R + [dict(source=l['s'], target=l['t'], type=l['type']) for l in LINKS]:
    if r['source'] == r['target'] or r['type'] not in T: continue
    g = T[r['type']].get('ground')
    if not g: continue
    a, b = (r['source'], r['target']) if g == 'source' else (r['target'], r['source'])
    edges[a].add(b)
def cycle_from(start):
    stack, path, onp = [(start, iter(edges[start]))], [start], {start}
    while stack:
        v, it = stack[-1]
        for w in it:
            if w == start: return path + [w]
            if w not in onp and w in edges:
                stack.append((w, iter(edges[w]))); path.append(w); onp.add(w); break
        else:
            stack.pop(); onp.discard(path.pop())
    return None
cyc = set()
for cid in new:
    c = cycle_from(cid)
    if c: cyc.add(' → '.join(c))
for c in sorted(cyc): err.append('цикл обоснования: ' + c)
print(f'концепций {len(new)}, связей {len(LINKS)} (внутри систем {sum(1 for l in LINKS if ALL.get(l["s"],{}).get("philosopher")==ALL.get(l["t"],{}).get("philosopher"))}, '
      f'с местом HWPh {sum(1 for l in LINKS if l.get("hwph"))}, рефлексивных {sum(1 for l in LINKS if l["s"]==l["t"])}, bidirectional {sum(1 for l in LINKS if l.get("bi"))})')
print('типы', dict(collections.Counter(l['type'] for l in LINKS).most_common()))
for e in err: print('✗', e)
for w in warn: print('!', w)
if '--md' in sys.argv:
    out = sys.argv[sys.argv.index('--md') + 1]
    lab = lambda c: f"{ALL[c]['label']} ({P[ALL[c]['philosopher']]['nameRu']})"
    Lx = ['# Новые концепции списка A и их связи — черновик L1 (8 октября 2026)\n',
          'Черновик **без описаний**: состав концепций (список A захода N1, без уже заведённой Amor fati) и связи с типом, весом и основанием выбора. '
          'Описания концепций и связей пишутся после утверждения состава; тогда из `hwph_reader/bridge/review/l1/draft.py` собираются файлы правок. '
          'Семантика — по подсказкам легенды: вес 1 — побочная связь (между системами — косвенный канал или отдалённое родство), 2 — обычная (воздействие, засвидетельствованное текстами), '
          '3 — несущая (без неё понятие не возникло бы или система рассыпается); логические типы — внутри системы, исторические и типологические — между системами; '
          'типологические симметричны и `bidirectional` не получают; рефлексивная связь — самообоснование или самоприменение. '
          'Колонка HWPh заполнена, где словарь утверждает само отношение; пустая — отношение по знанию составителя.\n',
          f'Концепций {len(new)}, связей {len(LINKS)}. Проверка (`check.py`): имена и пары свободны, слой типа соответствует паре, у каждой концепции есть связь внутри своей системы, циклов обоснования нет.\n']
    for cid, ph, label, rub, art in CONCEPTS:
        Lx.append(f"\n## {label} ({P[ph]['nameRu']}) — `{cid}`\n\nHWPh: {art}. Рубрики: {', '.join(rub)}.\n")
        Lx.append('| Связь | Тип/вес | Почему | HWPh |\n|---|---|---|---|')
        for l in LINKS:
            if cid in (l['s'], l['t']):
                Lx.append(f"| {lab(l['s'])} → {lab(l['t'])} | {l['type']}/{l['w']}{' ⇄' if l.get('bi') else ''} | {l['why']} | {l.get('hwph', '')} |")
    open(out, 'w', encoding='utf-8').write('\n'.join(Lx) + '\n')
