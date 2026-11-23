---
name: philosynth-23-log
description: Журнал беседы 2.3 PhiloSynth (Edit Modal + Cascade Panel, клиент; ЗАКРЫТА 2026-08-20, тест 60✓×4, доки пропатчены conv23) — решения и грабли
sources: [chat]
aliases: [беседа 2.3, EditModal, CascadePanel, plans/impact, subsection-impact, test-23]
---

## Статус
- [stated] БЕСЕДА ЗАКРЫТА 2026-08-20 (по команде «все запросы блока завершения одним заходом»): типочек/audit/vite build чисты; integration-check расширен блоком 2o/4u (2.3) — INTEGRATION OK; доки пропатчены scripts/patch-docs-conv23.py (14 правок, идемпотентен); глава 2.3 в NEXT-CONTEXT.md; контрольный прогон теста после завершения — 60✓ (итого ×4). Долги §12 беседы (affectedSubs с переформулировкой, бейдж качества, makeSectionCtxDisclosure) отмечены закрытыми в 07
- [stated] Пользователь подтвердил выбор «надёжнее»: тонкие read-only превью-эндпоинты вместо черновик-плана на каждый клик; также одобрены PATCH += extGraphMetrics и двухшаговый workflow «Составить план → Исполнить»

## Реализовано (запрос 1)
- shared/types/edit-plan.ts += DTO: PlanImpactRequest/Response, CascadeImpactDto (+5 суб-DTO), SubsectionImpactRequest/Response, CrossSectionDepDto
- server routes/plans.ts += POST /:id/plans/impact (analyzeImpact + estimatePlanCost по виртуальным confirmed-шагам только выбранных действий — паритет футера, fail-open 0)
- server routes/generation.ts += POST /:id/subsection-impact (buildEditInfra → getIntraDependents → getCrossSecDependents по всем изменяемым с dedup/фильтрами → getAffectedModes(changedSubsections) → estimateSubsectionCost fail-open null; без гейта isGenerationActive; GenerationError NOT_FOUND→404)
- server routes/syntheses.ts PATCH += extGraphMetrics (boolean)
- client api/plans.ts (все обёртки + getPlanImpact/getSubsectionImpact/regenerateSubsection), api/sections.ts += getSectionContext, api/syntheses.ts updateSynthesis += extGraphMetrics
- client hooks/useEditPlan.ts: zustand useEditPlanStore + хук со СВОИМ WS-соединением (доставка plan-событий по userId на все соединения — subscribe не нужен); plan_updated — единственный источник статусов шагов; confirmStep: draft→PATCH, executing→WS confirm_step; section_done/stream_error → onSectionEvent; терминальный статус — по ПЕРЕХОДУ в handleMessage (правка после теста R3, см. «Тесты»)
- client components/edit/: CascadePanel (рендер E1–E5 1:1, covered/exposed по Set), EditSectionCard (бейдж 90/60, деградация <70, secCtx textarea, ленивое превью /context в sec-disclosure, extGraphMetrics для graph, взаимоискл. чекбоксы, кнопки подразделов при >1 из фактических SectionSummary.subsections), SubsectionRegenPanel (превью impact, userNote+includeContent, чекбоксы волны intra+cross, ОЧЕРЕДЬ последовательных POST по section_done, stream_error останавливает, капсула→/regenerate/:key), EditPlanPanel (иконки ◯⟳✓✗−●, каскадные с золотой рамкой, результаты шагов, подтвердить/пропустить), AddSectionPanel, EditModal (сброс при open, secCtx из sections, debounce 400мс + seq-защита impact, карточка структуры structureSections↔sectionOrder null→устарела + Обновить→regen sum/«Структура документа», футер счётчики+стоимость план>impact+«Удаление бесплатно», runLabel по состоянию, controlsDisabled=!!plan, confirm при закрытии на исполнении, блокировка body)
- SynthesisPage: кнопка «✎ Изменить» (disabled при live, оптимистична — SynthesisFull без userId) + <EditModal>
- Долг makeSectionCtxDisclosure закрыт: details.sec-disclosure с secContext в SectionView
- globals.css += порт .edit-*/.cascade-*/.sec-warning-item и родни/@media 768px/@keyframes spin (его не было)

## Дыры доков (в патч при завершении)
- [stated] Одобрено фиксировать: (1) live-каскад без транспорта → закрыт /plans/impact; (2) SubsectionRegenPanel без данных → /subsection-impact; (3) долг affectedSubs неисполним буквально (роут отвечает {ok:true} фоном) → переформулировать на превью; (4) extGraphMetrics некуда писать → PATCH; (5) карточки режимов — TODO(4.1), нет routes/modes; (6) гейты openEditModal (API_KEY/incomplete) — до 6.1/4.3; (7) стоимость футера — серверная оценка вместо клиентской

## Осознанные упрощения (доложить в ревью)
- Каскад «третьей волны» подраздельной перегенерации и каскад режимов не перенесены (нет повторного превью после волны; режимы — 4.1)
- Деградация в EditSectionCard без issues (SectionSummary несёт только score) — отсылка к превью контекста
- Пропуск pending-шага во время исполнения = не подтверждать (PATCH только для draft)

## Грабли
- В globals.css НЕ было @keyframes spin (спиннеры 1.6b — Tailwind animate-spin)
- npm install после клона: удалить prefix= из ~/.npmrc (грабля 0.4)
- POST /:id/plans/impact не коллизирует с /:id/plans/:planId — POST на :planId не существует (GET/PATCH/DELETE есть)

## Тесты R2–R5 (tests/test-23-requests2-5.mjs; 60✓×3, 2026-08-20)
- Харнесс: сервер :3000 (vite-прокси захардкожен) + vite :5199 + PG/Redis + мок Claude из test-22 + puppeteer-core /opt/google/chrome/chrome; PG/Redis НЕ переживают вызовы bash в песочнице — стартовать в той же команде, что и тест; прогоны встык оставляют сирот vite/tsx — pkill перед запуском
- R0 добавлен сверх 07: API-санитария /plans/impact (владелец/403, пустой план→импакт пуст и 0), /subsection-impact, PATCH extGraphMetrics; списки из ответов — эталон для браузерных сверок (конфиги не хардкодятся)
- Два НАЙДЕННЫХ И ПОЧИНЕННЫХ дефекта клиента (сервер был чист — план в БД done): onPlanFinished→store.load() переключал loading → SynthesisPage рендерил спиннер → модалка размонтировалась; ref-дедупликация терминального статуса не переживала ремаунт → бесконечный цикл ремаунтов с парами WS-соединений (close 1006). Починка: (1) терминальный колбэк по ПЕРЕХОДУ статуса внутри handleMessage (не эффектом по состоянию store); (2) неразрушающее обновление reloadSections+applySynthesis вместо store.load
- Грабли теста: статус готового синтеза — "ready" (не "complete"); uppercase-грабля 1.5 повсеместна (.action-btn/.edit-sec-btn/.cascade-title/шапка EditPlanPanel под text-transform) — все текстовые сверки регистронезависимые; консольный шум окружения в фильтр: fonts.googleapis.com 403 (egress-прокси песочницы), /auth/me 401 до входа (×2 StrictMode)
- Фактические данные: downstream graph = glossary+theses+dialogue (07 называл только theses, dialogue — мелочь в патч доков); intra «Таблицы категорий» = Таблица связей, Топология графа, Топологическая таблица; version_sub +2 после очереди из двух подраздельных волн
- Диагностический приём: evaluateOnNewDocument-обёртка window.WebSocket с журналом open/close+stack — мгновенно указала виновника цикла reconnect

## Завершение (2026-08-20)
- integration-check.mts += блок 2o (api/plans 8 экспортов, useEditPlan/Store, 6 компонентов edit/) и 4u (контракты: /plans/impact read-only с владельческим гейтом и без insert + страж от появления POST /:id/plans/:planId; /subsection-impact без isGenerationActive; PATCH extGraphMetrics; переход статуса в useEditPlan; debounce+seq и reloadSections-не-load в EditModal; очередь section_done и капсула-квирк; пороги 90/60 и null≠0; sec-disclosure в SectionView; CSS-классы; запрет browser storage; TODO(2.3) нет). Грабля вставки: срез блока по indexOf упирается в упоминание роута в шапке файла — якоря только по строкам регистрации plansRoutes.post(...)
- patch-docs-conv23.py: 03 §2.2/§2.5/§2.6 (+2 эндпоинта, PATCH-поле), 05 (ФАКТ-пометка edit/), 07 (врезка-ФАКТ о неполноте «Транспорт готов», «⟳ » вместо «✓ изменён», фактический downstream, двухшаговый workflow, три долга §12 закрыты), 04 (ФАКТ-пометки updateLiveCascade/openEditModal/UI подразделовой). Якоря 03 — многострочные точные блоки из спеки
- Ревью карты 04: все клиентские половины §2.4/§2.5 портированы; единственная метка — TODO(4.1) карточек режимов в шапке EditModal; check-map-04: расхождений 0
- Следующая беседа по 07 — 3.1 (Фаза 2 закрыта целиком); контекст для следующих бесед зафиксирован в главе 2.3 NEXT-CONTEXT («Помодульно»). README: абзац беседы 2.3 добавлен, статус «Фазы 0–2 завершены»; архив philosynth_conv23_closed.tar.xz отдан пользователю


<!-- обновлено: 2026-08-20T04:38:24.647821+00:00 -->
