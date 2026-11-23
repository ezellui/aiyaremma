---
name: concepts-omnidirectional
description: Ranatar/philosophical-concepts-omnidirectional — архитектурная спецификация философской платформы, общий предок philosynth и philosphaira
sources: [chat]
aliases: [philosophical-concepts-omnidirectional, omnidirectional, сервис философских концепций]
---

- [stated] Третий репозиторий пользователя рядом с [[philosynth]] и [[philosphaira]]:
  github.com/Ranatar/philosophical-concepts-omnidirectional (последний коммит 15.09.2025)
- [stated] Содержит не код, а проект платформы: README-руководство по развёртыванию,
  philosophy-service-documentation.md, philosophical-concepts-schema.md,
  architecture/ (mermaid-схемы, tsx-прототипы, claude-requests.js, docker-compose)
  и structure/Phase-1 (скелет shared/db/init)
- Замысел: микросервисная платформа из 12 сервисов — пользователи, концепции, графы,
  тезисы, синтез, Claude, анализ названий, определение происхождения, историческая
  контекстуализация, практическое применение, диалогическая интерпретация, эволюция
  концепций; полиглотное хранение PostgreSQL + Neo4j + MongoDB + Redis, RabbitMQ,
  Kubernetes
- Отношение к другим репозиториям: это ЗАМЫСЕЛ ЦЕЛИКОМ, а построенные половины —
  [[philosynth]] (сторона синтеза; ключи разделов sum/graph/glossary/theses/name/
  history/origin/practical/dialogue/evolution/critique = сервисы 4.3–4.14 спецификации)
  и [[philosphaira]] (сторона базы). Объединение двух половин, о котором думает
  пользователь, и есть эта спецификация
- [stated] ПРОИСХОЖДЕНИЕ ИМЁН И ХОД РАБОТЫ: пользователь пытался делать omnidirectional,
  но замысел оказался слишком сложным и остался неосуществлённым. Платформу из этого
  замысла Claude назвал «ФилоСферой» в беседе, где родился [[congress-protocol-pdf]]
  (протокол философского конгресса). От этого имени пошло название проекта
  [[philosphaira]], которым пользователь занялся с октября 2025 года. Около марта
  2026 года он вернулся к omnidirectional и сделал одностраничный HTML с сильно
  упрощённым функционалом — его Claude назвал [[philosynth]]


<!-- обновлено: 2026-09-10T17:14:51.509072+00:00 -->
