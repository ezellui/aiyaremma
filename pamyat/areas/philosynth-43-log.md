---
name: philosynth-43-log
description: Журнал беседы 4.3 PhiloSynth (Import Service; ЗАКРЫТА 2026-08-30 целиком, тест 64✓×2, доки пропатчены conv43) — решения, дыры доков, грабли; следующие — Фаза 5 / 6.1
sources: [chat]
aliases: [беседа 4.3, import-service, импорт HTML, ImportPage]
---

Продолжение [[philosynth-42-log]]; проект — [[philosynth]].

## Статус
- Запрос 1 ВЫПОЛНЕН (2026-08-30): typecheck 0, vite build ✓, audit ✓, смоук ядер tests/smoke-43-request1.mjs 33✓×2.
- ВСЕ тестовые запросы протокола ВЫПОЛНЕНЫ (2026-08-30): tests/test-43-requests2-5.mjs — 64✓ ×2 (харнесс test-42: живой сервер + мок Claude SSE + Chromium /opt/pw-browsers; roundtrip export→import с S2-родителем и полным совпадением categories/theses/glossary/логов/lineage; standalone с предупреждениями; IMPORT_INVALID; без embedded state; браузерный R6 — ImportPage через vite, кука setCookie на origin vite).
- Блок завершения ВЫПОЛНЕН (2026-08-30), беседа ЗАКРЫТА: check:integration += 2r/4z/5t (дрейф двойников titleToKey/genealogy клиент↔сервер — нормализация prettier-ключей и linkedom только по импорту, иначе ложные срабатывания; живой importHTML против БД до закрытия пула) → INTEGRATION OK; ревью 04 §2.6 (ФАКТ-пометки, populateFromImport вырожден); долг §12 «Серверный импорт концепт-файлов» ЗАКРЫТ, клиентский остаток заведён за 6.2 (авто-импорт файловых ☑-концепций при сабмите: файл → POST /syntheses/import → участник type='synthesis'; метка в SynthesisForm перевешена TODO(4.3)→TODO(6.2)); incomplete-доля гейта 2.3 вырождена (критичность в warnings ответа, редактирование не блокируется — паритет исходника; за 6.1 остаётся API_KEY-доля); scripts/patch-docs-conv43.py идемпотентен (11 applied → прогон 2 skip): 07 шапка + глава «По факту 4.3» + §12, 04 §2.6, NEXT-CONTEXT глава 4.3, README «Фазы 0–4 завершены». Полный регресс зелёный. После сжатия контекста полнота сверена по первоисточникам репо (транскрипт хранит кириллицу в \u-эскейпах — целевой поиск по нему малопригоден).
- Архив philosynth-service-4.3-final.zip выдан (378 файлов; без node_modules/.git/dist/tsbuildinfo/.env; tsconfig.base.json на месте).

## Сделано (запрос 1)
- shared/types/synthesis.ts += ImportWarning {field, message, critical}.
- server/utils/html-parser.ts += parseDocument/HtmlDocument (полный документ, инвариант «единственная точка linkedom» сохранён); в HtmlElement добавлены closest/outerHTML/innerHTML.
- server/services/import-service.ts (~950 строк): importHTML шаги a–m (syntheses → sections → граф → тезисы/глоссарий → genLog/ctxLog/_genCommon → lineage → mode_results; откат строки syntheses при сбое — единой транзакции нет, saveGraphToDb/saveElementsToDb ведут свои); extractMetadata/validateImportMeta/extractSections/extractEmbeddedState/extractModesFromHTML; серверные копии reconstructGenealogy/normalizeGenealogyNames/restoreCapsulesFromHTML/resolveConceptName (FIX [а-яё]) + titleToKey/TITLE_TO_KEY; маппер логов обоих форматов; 9 адаптаций задокументированы в шапке модуля.
- server/routes/import.ts: POST /syntheses/import (multipart, поле file, лимит 25 МБ, ImportError → 400 IMPORT_INVALID), смонтирован в index.ts после exportRoutes.
- Клиент: api/import.ts (multipart-обёртка с контрактом ApiError — api() JSON-only не годится) + ImportPage.tsx (drag&drop, подтверждение ДО отправки, индетерминированный индикатор, предупреждения ⚠/⚡, redirect на /synthesis/:id).

## Два входных формата (ключевое знание)
- standalone-файл: шапка по id (#docTitle/#docMethod/#footerPhil/#docHeaderExtras), legacy-записи логов с cost/error/полями россыпью/маркерами type через дефис — форма документирована ТОЛЬКО исходником (genEntry [20092], ctxLog.push [8475], saveHTML [18040]).
- экспорт сервиса 4.2: шапка ПО КЛАССАМ без id (.doc-title/.doc-meta-grid), логи с costUsd/errorMessage/metadata/createdAt. Оба пишут version:2.

## Дыры доков (ВСЕ пропатчены scripts/patch-docs-conv43.py, 2026-08-30)
1. Шапка экспорта 4.2 без id — буквальный порт extractMetadata/resolveConceptName на своём же экспорте не работает; протокол адаптацию не оговаривает.
2. .doc-body экспорта несёт якорь sec-{key} и кнопку «▦ Граф» — вместо parentBody.innerHTML взят outerHTML .doc-section (иначе мусор в html_content).
3. reconstructGenealogy: сервис пишет участников type='synthesis', клиентский образец различает только 'concept' — серверная копия принимает оба.
4. Гейт DOC_STATE.incomplete: 2.3 адресовала «6.1/4.3», в тексте 4.3 ни слова, колонки нет — адресация повисла, решить явно.
5. Глубокая генеалогия файла не персистится: lineage — первый слой; файловые родители без записи в БД → warning.
6. Квирк v11: validateImportMeta считает 0 философов критичным — roundtrip легального свободного синтеза всегда даст «критическое» предупреждение (так ведёт себя сам исходник; порт 1:1).
7. Квирк subtitle мета-синтеза: «На основе: Кант + Концепция» сплитится по запятой в один элемент; перекрывается params.phil из embedded state.

## Грабли
- Ветка embeddedState.capsuleHTML в buildDocStateFromImport МЕРТВА для version:2 обеих линий (никто capsuleHTML в state не пишет) — капсула восстанавливается из текста шапки, HTML-форматирование теряется.
- node_modules/.bin/tsx напрямую (npx виснет — грабля 4.2 подтверждена и здесь).

## Тестовые запросы (найдено первым прогоном 59✓/5✗ → исправлено до 64✓)
- НОВАЯ ГРАБЛЯ МОКОВ: задание SUM перечисляет структуру документа («…Критический анализ…») — sum обязан иметь СВОЙ маркер («Точки напряжения») ПЕРЕД веткой /критическ/i, иначе перехватывается (в 4.2 прошло незамеченным — содержимое sum там не проверялось).
- Единственный содержательный фикс import-service: forceDate в toGenLogRow/toCtxLogRow — standalone датирует только маркеры, смешение реальных прошлых дат с fallback-«сейчас» ломало порядок журнала; при неполной датировке ВСЕ записи получают синтетические t0+i (v2 с полными createdAt сохраняет реальные даты).
- Квирк капсулы зафиксирован тестом: sections-row 'capsule' при импорте НЕ создаётся (экспорт не пишет капсулу в тело — паритет исходника); капсула в capsule_html + ключ в sectionOrder. Кандидат в патч доков.
- Мок S2-родителя обязан уметь глоссарий («Глоссарий терминов», таблица «Термин | Принятое определение», маркер «Таблица определений») — validateConceptForMetaSynthesis требует sum/glossary/theses/critique + graph|dialogue + capsule.
- Окружение с нуля: rm nodesource-листов → apt postgresql-16 redis-server; su postgres (createuser philosynth CREATEDB, createdb, CREATE EXTENSION pg_trgm); drizzle-kit migrate; три сида (253/27/18+29); npm i --no-save puppeteer-core postgres одной командой; Chromium 141 в /opt/pw-browsers/chromium-1194 и /opt/google/chrome.

<!-- обновлено: 2026-08-30T21:09:23.320305+00:00 -->
