---
name: philosophy-graph-archive-run
description: Разворачивание архива philosophy_graph в присланном виде — окружение автора НА МЕСТЕ, две настоящие мины, полная приёмка сошлась; читать перед любой работой с архивом
sources: [chat]
aliases: [архив проекта, philosophy_graph_project_tar.xz, запуск архива, окружение приёмки]
---

Продолжение [[philosophy-graph-probes]]. Устройство проекта — там и в [[philosophy-graph-modules]].

## ЗАХОД 2026-08-17: АРХИВ ПРИСЛАН В БЕСЕДУ
- [stated] Пользователь прислал philosophy_graph_project_tar.xz (868 КБ, 184 файла) и
  попросил разобраться в файловой структуре, документации и порядке работы
- [stated] Затем одёрнул: «а у тебя в окружении есть chrome 131, надо поискать
  тщательнее» — и был прав, см. ниже
- ЧИТАТЬ В ТАКОМ ПОРЯДКЕ: ОБЗОР.md (единственный полный; разделы 13 «что каждый файл
  делает» и 14 «что запускать при каждом изменении») → module-ops.md (перестановки) →
  split-README.md (устройство сборки и мины) → история-правок.md (заходы после
  разбивки) → module-spec-v2.md и три карты как справочники, не для чтения подряд

## ОКРУЖЕНИЕ АВТОРА ЗДЕСЬ ЕСТЬ ЦЕЛИКОМ — И Я ЕГО НЕ НАШЁЛ С ПЕРВОГО РАЗА
- Chrome 131.0.6778.204 лежит РОВНО ТАМ, где написано в ОБЗОР.md:
  /home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome
  (ещё и chrome-headless-shell той же версии). puppeteer 23.11.1 — тоже ровно там:
  /home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer
- МОЯ ОШИБКА: искал через `ls ~/.cache/puppeteer`, а HOME здесь /root, не /home/claude.
  Тильда разошлась с буквальным путём — и я объявил окружение чужим.
  ПРАВИЛО: путь из документации проверять БУКВАЛЬНО, как записан, а не своим сокращением
- ВТОРАЯ ОШИБКА, ХУЖЕ ПЕРВОЙ: подставил Chromium 141 из playwright, получил расхождение
  css_probe во всех шести состояниях — и ОБЪЯСНИЛ его («эталон привязан к выпуску
  браузера, переутверждать при переезде — норма»). Объяснение было правдоподобным и
  ложным: на настоящем Chrome 131 css_probe даёт 6 из 6. То есть я нарушил собственное
  правило проекта — прежде чем звать расхождение чем бы то ни было, убедиться, что
  сравниваются одинаковые стороны. Подмена браузера и есть разные стороны
- НИКАКИХ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ НЕ НУЖНО, кроме TREE и KEYS: умолчания CHROME и
  PUPPETEER в приборах верны. TREE=<проект>/split и KEYS=<проект>/handler_keys.json
  нужны sweep_all, потому что его умолчания указывают в /home/claude/build/src

## ДВЕ НАСТОЯЩИЕ МИНЫ (третья была моей выдумкой)
1) split.mjs:533 копирует d3 из ЗАШИТОГО '/home/claude/node_modules/d3/dist/d3.min.js'
   — ни довода, ни переменной. Лечение: ln -sfn <проект>/node_modules /home/claude/node_modules
2) remap.mjs «собрать» зовёт check_modules.mjs БЕЗ пути к дереву, тот падает на
   умолчании '/home/claude/build/src'. Падает ПОСЛЕ семи успешных шагов, уже снеся
   старое дерево (первый шаг делает rmSync) — потому перед первым прогоном ОБЯЗАТЕЛЬНО
   сохранять копию split/
3) serve.sh держит переменную с КИРИЛЛИЧЕСКИМ именем (ЗДЕСЬ=…) — bash её не принимает,
   сервер молча не поднимается, curl отвечает 000. Обход: setsid python3 tools/serve.py
   8711 split. Мина известная (записана в памяти как урок), но в самом файле осталась

## ПОЛНАЯ ПРИЁМКА СОШЛАСЬ, ИЗ АРХИВА, БЕЗ ЕДИНОЙ ПРАВКИ ПРОЕКТА
- npm install по закреплённым версиям встал без правок
- ЦЕПОЧКА ИЗ СЕМИ ШАГОВ руками с явными доводами (split → delegate static → delegate
  dyn → rig → unbridge → prune_imports → split_css) дала дерево, СОВПАВШЕЕ С АРХИВНЫМ
  ПОБАЙТОВО (diff -r пуст). 98 модулей, S:84, MET:33, VIEWS:6; призрачных ввозов убрано
  66 в 18 модулях; склейка стилей знак в знак
- check_modules 104 файла, 0/0; layers ввозы 0; bridge_debt 0/0/0/0; maps_fresh — все
  четыре карты свежие
- assert_probe 137/137; sweep_all 302/302 (447 снимков, 135 обработчиков, ошибок 0);
  compare 83/83; probe6 28/28; probe7 13/13; probe8 15/15; css_probe 6/6 — ВСЕ ШЕСТЬ
  ЭТАЛОНОВ СОШЛИСЬ ТОЧНО, ни один не пришлось переутверждать
- ВРЕМЯ: sweep_all — три части примерно по 2–4 минуты каждая, в один заход не влезает
  по пределу времени команды. Часть 3 гонять фоном (nohup … &) и ждать отдельно

## КОМАНДА ЗАПУСКА, КОТОРАЯ РАБОТАЕТ ЗДЕСЬ
```
ln -sfn <проект>/node_modules /home/claude/node_modules      # ради split.mjs:533
cp -r split /tmp/split_ref                                    # remap.mjs снесёт дерево
node tools/split.mjs split philosophy_graph_v3.html assign_names.json globals_map_v3.json
node tools/delegate.mjs split static ; node tools/delegate.mjs split dyn
node tools/rig.mjs split ; node tools/unbridge.mjs split
node tools/prune_imports.mjs split ; node tools/split_css.mjs split
node tools/check_modules.mjs split                            # путь ОБЯЗАТЕЛЕН
python3 tools/make_ref.py philosophy_graph_v3.html split
setsid python3 tools/serve.py 8711 split &                    # НЕ serve.sh
export TREE=<проект>/split KEYS=<проект>/handler_keys.json    # CHROME/PUPPETEER не нужны
node tools/assert_probe.mjs index.html
node tools/<прибор>.mjs run index.html /tmp/sn/<прибор>.json
node tools/baseline.mjs проверить <прибор> /tmp/sn/<прибор>.json
```


<!-- обновлено: 2026-08-17T05:51:22.339163+00:00 -->
