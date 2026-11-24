  // Шаг 2. Палеографические сокращения. detectFont использует только
  // classList родителей, не зависит от computed style — работает на
  // template корректно.
  applyAbbreviations(root);
  decorateTituli(root);

  // Шаг 2.5. T.orn guard — блокируем шрифтовую лигатуру t+period
  // на всех t. кроме финального в каждом абзаце. См. секцию
  // T.ORN GUARD в скриптах.
  blockNonFinalTOrn(root);

  // Шаг 3. Translate-source-spans для основного текста ...