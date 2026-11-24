function findRuntTailRange(p) {
  // ... сбор text-nodes ...
  
  let startNode = tn;
  let startOff = startOffset;
  let parent = tn.parentNode;
  
  if (parent && parent.classList) {
    // Существующие случаи: .word-wbr, .lastword-no-wbr
    if (parent.classList.contains('word-render') ||
        parent.classList.contains('word-source')) {
      // ... подъём до .word-wbr (как было)
    } else if (parent.classList.contains('lastword-no-wbr')) {
      // ... подъём (как было)
    }
  }

  // НОВОЕ: если стартовый узел всё ещё внутри <em class="uncial-passage">,
  // поднимаемся до самого <em>. Это гарантирует, что runt-hang span
  // окажется либо целиком внутри <em>, либо целиком снаружи —
  // не пересекая его границу и не разрывая uncial-шрифтовый контекст.
  let walker = startNode === tn ? tn.parentNode : startNode;
  while (walker && walker !== p) {
    if (walker.tagName === 'EM' &&
        walker.classList && 
        walker.classList.contains('uncial-passage')) {
      // Стартуем перед всем <em>.
      const emParent = walker.parentNode;
      startNode = emParent;
      startOff = Array.prototype.indexOf.call(
        emParent.childNodes, walker);
      // Прерываем: дальше поднимать не нужно.
      break;
    }
    walker = walker.parentNode;
  }

  const range = document.createRange();
  if (startNode === tn) {
    range.setStart(tn, startOff);
  } else {
    range.setStart(startNode, startOff);
  }
  range.setEnd(p, p.childNodes.length);
  return { range: range };
}