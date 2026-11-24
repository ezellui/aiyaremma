// Дополнительный подъём для uncial-passage. Если стартовый узел
// всё ещё лежит внутри <em class="uncial-passage">, поднимаемся
// до <em>.
let probeAscender = startNode;
while (probeAscender && probeAscender !== p) {
  if (probeAscender.tagName === 'EM' &&
      probeAscender.classList &&
      probeAscender.classList.contains('uncial-passage')) {
    const emParent = probeAscender.parentNode;
    if (emParent && emParent !== p.parentNode) {
      startNode = emParent;
      startOff = ...;
    }
    break;
  }
  probeAscender = probeAscender.parentNode;
}