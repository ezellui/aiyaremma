---
name: congress-protocol-pdf
description: philosophy_congress_protocol.md и скрипт congress_to_pdf.py — книжный PDF «Протокола XVIII Международного философского конгресса»; что за проект и как устроена сборка
sources: [chat]
aliases: [philosophy_congress_protocol, congress_to_pdf.py, протокол конгресса, ФилоСфера]
---

- [stated] Проект: вымышленный «Протокол XVIII Международного философского конгресса» (заседание о платформе ФилоСфера, 2028) — исходник philosophy_congress_protocol.md, вёрстка скриптом congress_to_pdf.py
- [stated] Скрипт: Python + Paged.js в headless Chromium через Playwright; формат 170×240 мм, шрифты Spectral / Spectral SC / PT Sans, обложки, оглавление с отточиями
- [stated] Точечные правки вёрстки (перенос висячих рубрик, склейка пунктов перечня) хранятся списком идентификаторов в touchup.json рядом со скриптом
- [stated] Правил не только вёрстку, но и сам текст: середины докладов переписаны из перечней в связную речь, доработаны дискуссии и резолюция


<!-- обновлено: 2026-09-10T15:12:07.929027+00:00 -->
