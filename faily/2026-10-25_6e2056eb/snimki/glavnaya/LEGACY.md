# Наследие в истории git

Прежние методы и их результаты в рабочем дереве больше не лежат, но целиком сохранены в истории. Ниже —
что где лежит и как это достать. Для удобства стоят теги (`git tag -l`); если их нет у вас локально —
`git fetch --tags`.

| Этап | Коммит | Что было |
|---|---|---|
| исследовательский пакет по квенья | `786cedd` | интерпретаторы v2/v3 и контекстный, CSV/GraphML доказательств, критический атлас 101, строгие и текстовые цепочки |
| атлас 139 цепочек | `c8ea762` | 101 + 38 оценённых цепочек, деревья развития и происхождения |
| единый конвейер двух ветвей | `bf4ec6c` | `shared/` для квенья и синдарина, отдельный атлас синдарина, отчёты v3–v8 |
| канонический корпус v10 | `2e12327` | только прямое извлечение с HTML-карточек, архив Eldamo по частям, отчёты v9–v10 |

## Что стоит знать

| Ценность | Где |
|---|---|
| критический атлас 101 (A–X с обоснованием каждой цепочки) | `786cedd:reports/eldamo_critical_101_atlas.md`, `786cedd:data/eldamo_critical_101_atlas.csv` |
| ручной текстовый разбор 19 цепочек | `786cedd:reports/eldamo_textual_chain_report.md`, `786cedd:evidence/eldamo_textual_chain_assessment.csv` |
| строгие цепочки, 1159 точных соединений слов | `786cedd:evidence/eldamo_strict_chain_evidence.csv`, `786cedd:evidence/eldamo_exact_word_joins.csv` |
| 301 фрагмент пояснений о хронологии | `786cedd:evidence/eldamo_order_and_context_clues.csv` |
| старый GraphML (516 рёбер) | `786cedd:evidence/eldamo_sound_graph.graphml` |
| оценки 38 цепочек | `c8ea762:reports/eldamo_38_chain_assessment.md` |
| 123 развёрнутых варианта, сравнение рёбер | `bf4ec6c:branches/quenya/data/legacy_variant_recovery.json`, `bf4ec6c:branches/quenya/data/legacy_edge_comparison.json` |
| каталог шести языков в МФА | `786cedd:catalog/eldamo_six_languages_ipa_catalog.md` |
| отдельный атлас синдарина | `bf4ec6c:branches/sindarin/` |
| HTML-конвейер v10 и его данные | `2e12327:shared/`, `2e12327:branches/` |
| отчёты v7–v10 (JSON) | `2e12327:reports/` (тексты — в `docs/history/`) |
| архив Eldamo 0.8.13 по частям | `2e12327:source/eldamo-0.8.13.parts/` |

```bash
git show 786cedd:reports/eldamo_critical_101_atlas.md > critical_101_atlas.md
mkdir -p legacy/786cedd && git archive 786cedd evidence data reports engine catalog legacy | tar -x -C legacy/786cedd
git worktree add ../eldamo_v10 2e12327          # весь проект v10 рядом
```

Скрипты из `scripts/recovered/` первых коммитов содержат пути `/mnt/data/...` и без правки не запустятся.

Многое из этого теперь проверяется автоматически по `eldamo-data.xml`. Засвидетельствованные деривации
заменили склейку примеров, `order` и `<before>` заменили ручной поиск хронологических указаний. Но
текстовый разбор 19 цепочек и фрагменты пояснений остаются ручной работой, которую новая сборка не
повторяет.
