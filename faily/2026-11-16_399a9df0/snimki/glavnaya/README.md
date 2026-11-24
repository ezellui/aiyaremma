# Стенд симуляции PhiloSynth

Клон: /home/claude/USER/philosynth (88f2262). Порты: сервер :3000, симулятор Claude :3927, клиент (vite preview сборки) :5300.

- `./reset-db.sh` — пересоздать БД, миграции, посевы, сбросить Redis, поднять сервер + симулятор + preview.
- `claude-sim.mjs` — симулятор Anthropic Messages API (SSE). Разделы собирает из sample/…html по ЗАДАНИЮ;
  перегенерацию подраздела, таблицу рекомендаций, режимы, обогащения, обоснования — по разметке промпта.
  Сценарии: `POST :3927/__control {"rules":[{"match":"graph","action":"billing|overloaded|auth|cut|max_tokens|slow|hang","times":1}],"stream":{"chunk":220,"intervalMs":45}}`,
  `POST /__reset`, `GET /__log`. Метки в зерне: `[SIM:cut:theses]`. Промпты пишутся в prompts/.
- `api.mjs`, `ui.mjs` — клиент API и браузерная оснастка (Chrome 131, снимки в shots/).
- `s1-create … s8-social.mjs` — сценарии; s1 и s2 кладут id в таблицу lab_ids, остальные их берут.
  Запуск из этой папки: `node s1-create.mjs` и т. д.
- `gallery/` — страница со снимками.
