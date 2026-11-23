---
name: philosynth-51-log
description: Журнал беседы 5.1 PhiloSynth (Element Editor + Versioning, бэкенд; ЗАКРЫТА 2026-09-03 целиком, смоук 40✓ + тест 111✓×2, доки пропатчены conv51) — решения, дыры доков, грабли tsx-спавна; следующие — 5.2 / 5.3 / 6.1
sources: [chat]
aliases: [беседа 5.1, element-editor, element-renderer, element-versioning, Фаза 5]
---

Продолжение [[philosynth-43-log]]; проект — [[philosynth]].

## Статус
- [stated] Пользователь (2026-09-02/03): вести беседу 5.1 по протоколу 07 — каждый запрос протокола обрабатывать ОТДЕЛЬНО, не два сразу; перед началом прочитать 01–05 целиком, 07 (беседа 5.1, §1, §9–12) и NEXT-CONTEXT в частях про 5.1; файл 06 — только разработчику; шаблоны дизайна для фаз 5–6 — docs/fragments-for-conversations/5-6-ui-kit.{css,html,md}.
- Запрос 1 ВЫПОЛНЕН (2026-09-03): typecheck 0, audit чист, tests/smoke-51-request1.mjs 40✓.
- Тестовые запросы R2–R6 ВЫПОЛНЕНЫ одним заходом (2026-09-03): tests/test-51-requests2-6.mjs 111✓ ×2 (живой сервер, PG16+Redis, миграции 0000+0001, три сида). Тестами исправлено: impact считать по ПРЕЖНЕМУ и новому имени; auto-rename расширен на текстовые поля гранулярных строк (theses.formulation/justification, glossary term/definition/extra_columns, categories.definition/origin, edges.description) + капсула — иначе рассинхрон БД↔HTML.
- БЕСЕДА ЗАКРЫТА (2026-09-03): check:integration += 2s/4ab (дрейф-контроль parser↔renderer)/5u → INTEGRATION OK; секция 4o (1.6, запрет не-GET в elements.ts) сужена; check-map-04 0 расхождений; scripts/patch-docs-conv51.py (9 правок, идемпотентен): 07 шапка + «По факту 5.1» + контекст 5.2 + §12 (долги: показ htmlSync.pending в UI → 5.2; парсер глоссария при lang≠Russian → 5.5), 03 §2.4, 04 §4, 05, README; NEXT-CONTEXT глава 5.1; архив philosynth-service-5.1-final.zip (393 файла). typecheck:scripts — 19 предсуществующих ошибок в smoke-31/test-31 (за 3.1). Продолжение — [[philosynth-52-log]].

## Грабли окружения (5.1)
- tsx — обёртка над дочерним node: SIGKILL обёртке оставляет сервер живым на порту, следующий прогон бьёт в СТАРЫЙ код (полчаса ложного «стейла»); спавнить `detached: true` + `process.kill(-pid)`; перед прогонами `ps aux | grep server/index`.
- Redis не переживает паузу между ходами; при живом Redis лимитер 60/мин per-IP ест тест → RATE_LIMIT_HTTP_PER_MINUTE=100000 в env спавна.
- nodesource-источник может лежать отдельным файлом: `grep -rl nodesource /etc/apt/ | xargs rm` перед apt-get update.
- parseTopology требует [data-section="Топология графа"], иначе топологическая таблица не читается; фикстуры тестов наполнять теми же парсерами 1.4 (saveGraphToDb/saveElementsToDb из мок-HTML).

## Сделано
- html-parser.ts += locateDocTable / replaceDocTable (замена ОДНОЙ таблицы внутри data-section с сохранением h4 и прозы; replaced/appended/created) / replaceThesisParagraph.
- element-renderer.ts (пять таблиц, заголовки из текущего HTML приоритетны над Registry; applyElementUpdateToHtml), element-versioning.ts (createVersion max+1, getVersionHistory по synthesis_id, rollbackToVersion → версия 'rollback'), element-editor.ts (update*/deleteCategoryEdge/autoRenameReferences/computeElementImpact/rollbackElement/updateCapsule), routes/elements.ts дополнен всеми эндпоинтами §2.4 + версии/откат/auto-rename/capsule; shared/types/elements.ts += входы PATCH и HtmlSyncInfo.

## Решения (отступления)
- Round-trip побайтно невозможен (парсеры нормализуют); centrality/certainty/strength === 0 парсер читает как 0.5 — квирк исходника, не чинится.
- Ответы PATCH/rollback несут аддитивные version и htmlSync {rendered, patched, pending, sectionMissing}; justification тезиса — точечная правка абзаца, termCategory всегда pending.
- severity: high — имя упомянуто в других разделах/тезисах; low — структурные зависимые; none.
- has_reflexive пересчитывается при смене направления/удалении ребра (+ перерисовка топологии).
- Правки owner-only + 409 при активной генерации.

## Дыры доков (не пропатчены)
- 03 §2.4 без DELETE связи (edge case 5.1 его требует) — добавлен аддитивный DELETE /syntheses/:id/edges/:edgeId.
- 07 5.1 просит spliceSubsectionHtml для врезки таблицы — та заменяет весь div, противоречит п.1; сигнатуры 07 без synthesisId.
- Парсер глоссария 1.4 ищет таблицу по th «термин», не по data-section (ломается при lang ≠ Russian).
- Строка sections 'capsule' есть после генерации, нет после импорта — 03 п.14 не оговаривает.
- 03 §2.2 внутренне противоречив про PATCH /syntheses/:id (extGraphMetrics); чек-лист §10 ссылается на 06 как источник задач.


<!-- обновлено: 2026-09-03T21:13:46.538182+00:00 -->
