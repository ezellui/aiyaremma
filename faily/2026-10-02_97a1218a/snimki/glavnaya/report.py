"""C1 decisions.json -> decisions/sources/hwph/<TAG>-review.md

    python report.py <клон philosphaira> C1 [дата]
"""
import json, os, sys, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO, TAG = sys.argv[1], sys.argv[2]
DATE = sys.argv[3] if len(sys.argv) > 3 else ''
D = lambda p: json.load(open(os.path.join(REPO, 'app/data', p), encoding='utf-8'))
order = [c['id'] for c in D('concepts.json')]
C = {c['id']: c for c in D('concepts.json')}
P = {p['id']: p['nameRu'] for p in D('philosophers.json')}
porder = [p['id'] for p in D('philosophers.json')]
d = json.load(open(os.path.join(HERE, 'decisions.json'), encoding='utf-8'))
d.sort(key=lambda x: (porder.index(C[x['id']]['philosopher']), order.index(x['id'])))
vc = collections.Counter(x['verdict'] for x in d)
done_ph = sorted({C[x['id']]['philosopher'] for x in d}, key=porder.index)
lab = lambda i: f"{C[i]['label']} ({P[C[i]['philosopher']]})"
esc = lambda s: (s or '—').replace('|', '/').replace('\n', ' ')
L = []; w = L.append
w(f'# Основания концепций ΦilosΦaira по HWPh — заход {TAG}{" (" + DATE + ")" if DATE else ""}\n')
w(f'Разобрано концепций: {len(d)} из {len(order)} — все концепции {len(done_ph)} философов, '
  f'от «{P[done_ph[0]]}» до «{P[done_ph[-1]]}» в порядке базы. '
  f'Источник — {vc["sourced"]}, основание составителя с опорой на HWPh — {vc["editorial_reasoning"]}, '
  f'HWPh не подтверждает — {vc["not_supported"]}, описание расходится с HWPh — {vc["description_proposal"]}.\n')
w('«Источник» ставился, если HWPh излагает учение так же, хотя бы в ядре; место называется статьёй и колонками, '
  'за «Там:» — первоисточник, который HWPh при этом приводит. Где HWPh подтверждает лишь часть или только называет '
  'учение, стоит «основание» с указанием, что именно говорит HWPh; где подтверждена одна фраза полного описания — '
  'сноска на неё. Сопоставление концепции со статьёй, сделанное мостом, проверялось заново: верная статья указана '
  'в основании, неверные сопоставления перечислены ниже.\n')
w(f'Применение: `node tools/edit/set_provenance.mjs decisions/sources/hwph/{TAG}-provenance.json`. '
  'Связи и описания заход не меняет; сборка и приёмка — по порядку проекта.\n')
w('## Нужно решение автора\n')
w('### Описание расходится с HWPh\n')
for x in d:
    if x['verdict'] == 'description_proposal': w(f"- **{x['id']}: {lab(x['id'])}** — {x['note']}")
w('\n### Оговорки (основание поставлено или не поставлено, но описание спорно)\n')
for x in d:
    if 'ОГОВОРКА' in x.get('note', ''): w(f"- **{x['id']}: {lab(x['id'])}** — {x['note']}")
w('\n## Сопоставления моста, оказавшиеся неверными или неполными\n')
w('Поправки для `concept_de.py`; в основании уже стоит верная статья.\n')
for x in d:
    n = x.get('note', '')
    if re.search(r'мост (сопоставил|не нашёл|дал корпус|нашёл только|статьи не нашёл)|фильтр имени', n):
        w(f"- {x['id']}: {lab(x['id'])} — {n}")
for title, keys in (('Источник подтверждён', ('sourced',)),
                    ('Основание составителя с опорой на HWPh', ('editorial_reasoning',)),
                    ('HWPh не подтверждает (оставлено как есть)', ('not_supported',))):
    w(f'\n## {title}\n')
    w('| Концепция | Основание | Что говорит HWPh |\n|---|---|---|')
    for x in d:
        if x['verdict'] in keys:
            fn = '; '.join(f"сноска к «…{f['after'][-40:]}»: {f['text']}" for f in x.get('footnotes', []))
            w(f"| {x['id']}: {lab(x['id'])} | {esc(x.get('provenance'))}{' — ' + esc(fn) if fn else ''} | {esc(x.get('note'))} |")
open(os.path.join(REPO, 'decisions/sources/hwph', f'{TAG}-review.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('строк', len(L))
