function getRuntFontMetric(p, runt) {
  // Берём text-node на runt-строке и спрашиваем у computed style
  // font-family и font-size. На основании этого выбираем лимит.
  const samplePoint = document.caretPositionFromPoint(
    runt.lastLineLeft + runt.lastLineWidth / 2,
    runt.lastLineY + 5
  );
  if (!samplePoint) return HARD_MAX_HANG_PX_DEFAULT;

  const el = samplePoint.offsetNode.nodeType === 1
    ? samplePoint.offsetNode
    : samplePoint.offsetNode.parentElement;

  const cs = getComputedStyle(el);
  const fam = cs.fontFamily.toLowerCase();

  if (fam.indexOf('uncialis') !== -1) return 65;
  if (fam.indexOf('remedius') !== -1) return 50;
  if (fam.indexOf('beda') !== -1)     return 45;
  return 50; // Kells default
}