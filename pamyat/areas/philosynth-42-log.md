---
name: philosynth-42-log
description: Журнал беседы 4.2 PhiloSynth (Export Service; ЗАКРЫТА 2026-08-29 целиком, тест 76✓×2, доки пропатчены conv42) — решения и грабли; следующая — 4.3
sources: [chat]
aliases: [беседа 4.2, export-service, экспорт документа, export-assets]
---

Продолжение [[philosynth-41-log]]; проект — [[philosynth]].

## Статус
- Запрос 1 выполнен целиком (2026-08-29): typecheck ✓, vite build ✓, audit -w server ✓, смоук чистых ядер ✓.
- Сжатие контекста пришлось на середину запроса 1; ВСЯ пачка модулей написана заново, затем по требованию пользователя сверена с исходником построчно (MMD/JSON/PNG/auditCSS/fnBundle + дифф graph-style/physics с клиентом 1.7 по литералам) — семантических расхождений 0, внесены только пометки дословности (мёртвые es/nx,ny, ветка instanceof Set, MARKER_DEFS на уровне модуля).
- Тестовые запросы 2–6 ЗАКРЫТЫ (2026-08-29): tests/test-42-requests2-6.mjs, 76✓ ×2 прогона. Тест 5 (roundtrip-импорт) неисполним до 4.3 — зафиксирован 404 роута; собственный roundtrip есть первым тестом 4.3, покрытие не теряется.
- [stated] Блок завершения ВЫПОЛНЕН (2026-08-29), беседа ЗАКРЫТА: integration-check += секции 2q/4y/5s (дрейф-контроль graph-style/physics↔клиент 1.7, subtitleForExport↔DocumentHeader; живой конвейер экспорта) — INTEGRATION OK; ревью 04 §2.5 (ФАКТ-пометки + строки filename/reconstruct*); все дыры доков из реестра ниже пропатчены идемпотентным scripts/patch-docs-conv42.py (17 патчей: 07 — шапка/контекст/пп.3b-3c/4d/4g/5b/роуты-пять/тест4→4.3/глава «По факту 4.2»/квирк truncLabel/рёбра §11/оба долга §12 ЗАКРЫТЫ; 04; спека; ContextEntry); NEXT-CONTEXT — глава итогов 4.2 + комплект для 4.3; README — статус «+4.2», покрытие integration-check до 4.1–4.2, «следующая — 4.3».
- Грабля приёмки: npx (npx tsx …) лезет в сеть за реестром и виснет в этом контейнере — в командах приёмки звать node_modules/.bin/tsx напрямую.
- Следующая по графу — беседа 4.3 (Import Service); её первый тест — roundtrip экспортированного HTML. НАЧАТА — журнал [[philosynth-43-log]].

## Сделано (запрос 1)
- scripts/extract-export-assets.mjs (npm run extract:export-assets, идемпотентен) → server/config/export-assets.ts: fnBundle 46 функций buildGraphExportSection + константы + разметка #gmOverlay / #modeOverlay (без .mode-modal-params) + CSS исходника.
- server/services/export/: graph-model (G из БД), graph-style (копия палитр/ролей 1.7, фабрика createGraphStyle на экземпляр — сервер конкурентен), graph-physics, filename (getDocFilename), common (ExportError, loadExportSynthesis, exportFilename), mmd-exporter, json-exporter, png-exporter (node-canvas, вариант a), md-exporter (через html-parser), html-exporter (шапка-зеркало DocumentHeader, embedded state version:2, видимый лог — предвычисленный formatCtxLogHTML, auditCSS).
- server/utils/css-audit.ts; server/services/prompt-reconstruction.ts (4 reconstruct*, async) подключён в log-formatter — все TODO(4.2) сняты.
- routes/export.ts: 5 эндпоинтов GET /syntheses/:id/export/{html,md,mmd,png,json}, Content-Disposition RFC 5987, NO_GRAPH → 400 VALIDATION_ERROR; смонтирован в index.ts.
- Клиент: api/export.ts, меню «⤓ Экспорт» в SynthesisPage, заглушки GraphModal сняты (долг §12 1.7 закрыт), проброшен synthesisId.

## Тесты 2–6 (харнесс и окружение)
- Харнесс по образцу test-41: живой сервер + мок Claude (SSE), НО без vite; браузер — puppeteer-core + Chromium /opt/pw-browsers/chromium-1194/chrome-linux/chrome (кэш ~/.cache/puppeteer пуст).
- Мок графа под тест 2: ровно 8 узлов / 3 кластера, мульти-кластерный узел, рефлексивное и двунаправленные рёбра, роли ядро/генеративная/мост/центральная + синтез/тезис/антитезис.
- mermaid.live заменён тем же движком: npm-пакет mermaid в странице puppeteer (parse+render); CDN three r128/d3 7.8.5 в file://-тесте подменяются локальными копиями тех же версий через перехват запросов (cdnjs вне сетевого allowlist). 3D-canvas Three.js в headless-shell строится (swiftshader).
- Пакеты тестов ставить ОДНОЙ командой: npm i --no-save puppeteer-core postgres mermaid three@0.128.0 d3@7.8.5 — повторный npm i --no-save подчищает ранее поставленные не записанные пакеты.
- Окружение поднималось с нуля: apt update падал из-за протухшего /etc/apt/sources.list.d/nodesource.sources (403, домен вне allowlist) — удалить перед install postgresql-16 redis-server; su вместо sudo; pg_trgm создать заранее под postgres.

## Решения и грабли
- ГРАБЛЯ МОКОВ (важно будущим беседам): моки 2.3/4.1 возвращают разделы БЕЗ каркаса section-num/section-title/doc-content, который сис-промпт требует от настоящей модели — на таком вводе sec2md/saveMD дают пустой MD. Мок 4.2 отдаёт штатный каркас (wrapSection): один .doc-section на раздел, подразделы — div[data-section] внутри doc-content.
- Грабля мока-2: маршрутизацию pickHtml вести от специфичных маркеров («Таблица категорий») ПЕРЕД общим корнем /критическ/ — задание графа упоминает критический анализ и перехватывалось веткой критики (раздел graph получал html критики → 0 категорий).
- Пп. 4d/4g запроса на сервере буквально неисполнимы (нет DOM/живых функций) — ассеты извлекаются из самого исходника; лог — готовый html 2.4.
- reconstruct* async (Registry); config.buildPrompt → renderTemplate(promptKey,{param,context}); участники-концепции сервиса type='synthesis' (не 'concept') — фильтры через isConceptParticipant.
- Квирк exportMMD сохранён: classDef t{N} объявляются, строк «class …» нет (узлы красятся per-node style).
- getDocFilename: paramCode join("") без дефисов — пример «hm-t-2» в комментарии исходника устарел.
- Генеалогия в embedded state — из lineage напрямую без капсул (серверный reconstructGenealogy — 4.3); genealogy участников = null.
- Артефакты прогона отданы пользователю: export-42.html/png/mmd.

## Дыры доков (ВСЕ пропатчены scripts/patch-docs-conv42.py, 2026-08-29)
1. Первый запрос 4.2 в 07 не перечисляет md-exporter и GET /export/md (в списке роутов 4 из 5).
2. filename.ts/getDocFilename не упомянут в запросе.
3. Инверсия 4.2←4.3: тестовый запрос 4 «импортируй через POST /syntheses/import» неисполним (import-service — 4.3); аудит 07-30 её не заметил. Патч: пометить перенос в 4.3 или удалить как дубль — у 4.3 тот же roundtrip первым тестом.
4. Граф §11: нет рёбер 4.2←2.4/4.1/1.7/1.6b; «Контекст» беседы устарел.
5. Пп. 4d/4g неисполнимы буквально (см. выше).
6. reconstruct*: buildPrompt/async/type='synthesis' не отражены в 07.
7. Спека фрагмента 4.2 включает лишние saveLang и reconstructGenealogy (тот — 4.3).
8. Комментарий ContextEntry в shared/types/generation.ts называет статусы 'included'|…, фактически "found".
9. Квирк «truncLabel печатает escape» в шапке 07 преувеличен: "\u2026" — валидный литерал, рендерится «…».
10. Грабля моков (каркас раздела) — кандидат в шапку 07/журнал грабель.


<!-- обновлено: 2026-08-30T03:49:13.360390+00:00 -->
