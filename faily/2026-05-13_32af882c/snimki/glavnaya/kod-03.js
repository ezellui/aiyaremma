// ═══════════════════════════════════════════════════════════════
// T.ORN GUARD — блокирует шрифтовую лигатуру t+period/colon во
// всех позициях, кроме последней значащей буквы абзаца.
//
// Логика:
//   1. Для каждого <p>, не являющегося маргиналией/рубрикой/colophon
//      (только основной Kells-текст), собираем все позиции 't[.:]'
//      в text-узлах.
//   2. Находим последний text-node с буквенным содержимым в блоке
//      (это и есть «конец абзаца» в смысле текста).
//   3. Среди наших совпадений ищем самое позднее, которое лежит в
//      этом узле И после которого в узле нет других букв. Это —
//      final t.orn, его не трогаем.
//   4. Все остальные совпадения оборачиваем: букву 't' выносим в
//      <span class="no-t-orn">t</span>, точка/двоеточие остаются
//      снаружи. Шейпинг-кластер t+period разорван.
//
// Идёт ДО walkWrapLongWords / walkWbrOnly, чтобы наши обёртки
// существовали в момент walkWbrOnly и были пропущены (как и
// liga-protect — добавляем no-t-orn в skip-листы).
// ═══════════════════════════════════════════════════════════════

const T_ORN_TRIGGERS = { '.': 1, ':': 1 };

// Только <p> в Kells-контексте. Маргиналии исключены полностью
// (не Kells, либо walkJitter всё равно убивает лигатуры). Колофон
// идёт в Remedius — там t.orn нет. Рубрики и doc-title — Uncialis,
// тоже нет GSUB.
function isTOrnRelevant(block) {
  if (block.tagName !== 'P') return false;
  if (block.classList.contains('marginalia')) return false;
  // На случай если <p class="colophon"> когда-нибудь появится:
  if (block.classList.contains('colophon')) return false;
  if (block.classList.contains('later-hand-colophon')) return false;
  return true;
}

function blockNonFinalTOrn(root) {
  const blocks = root.querySelectorAll('p');
  let wrappedCount = 0;
  let preservedCount = 0;

  for (let bi = 0; bi < blocks.length; bi++) {
    const block = blocks[bi];
    if (!isTOrnRelevant(block)) continue;

    // Шаг 1 — собрать все text-nodes и все совпадения t[.:].
    const allTextNodes = [];
    const walker = document.createTreeWalker(
      block, NodeFilter.SHOW_TEXT, null, false
    );
    let n;
    while ((n = walker.nextNode())) allTextNodes.push(n);

    // matches: [{ node, tIndex, punctIndex }]
    const matches = [];
    for (let ni = 0; ni < allTextNodes.length; ni++) {
      const tn = allTextNodes[ni];
      // Пропускаем узлы внутри уже обёрнутых .no-t-orn (idempotence
      // при повторных вызовах — на случай если что-то перестроится).
      if (tn.parentElement &&
          tn.parentElement.classList.contains('no-t-orn')) continue;
      const v = tn.nodeValue;
      if (!v) continue;
      // Сканируем СПРАВА налево, чтобы при последующем wrap'е
      // индексы более ранних совпадений в этом же узле остались
      // валидными (обрабатываем в обратном порядке).
      for (let i = v.length - 2; i >= 0; i--) {
        if (v[i] !== 't' && v[i] !== 'T') continue;
        if (!T_ORN_TRIGGERS[v[i + 1]]) continue;
        // Перед 't' — буква? Если 't' начинает text-node, проверять
        // не нужно: t.orn срабатывает на t+period вне зависимости от
        // контекста слева. Но если слева 'e', GSUB-приоритет отдаст
        // 'e+t→&' раньше, и t.orn не возникнет физически. Можно
        // не оборачивать (микро-оптимизация). Делаем — будет лишний
        // span, но безвредно. Опускаем проверку.
        matches.push({ nodeIdx: ni, tIndex: i, punctIndex: i + 1 });
      }
    }

    if (matches.length === 0) continue;

    // Шаг 2 — найти последний значащий text-node в блоке.
    let lastSigNodeIdx = -1;
    for (let i = allTextNodes.length - 1; i >= 0; i--) {
      const v = allTextNodes[i].nodeValue || '';
      if (/[A-Za-zÀ-ÿĀ-ſ]/.test(v)) {
        lastSigNodeIdx = i;
        break;
      }
    }

    // Шаг 3 — определить, какой match является финальным t.orn.
    // Финальный = в lastSigNode И после него в узле нет других букв
    // (только пунктуация/whitespace). Кодифицируем как индекс в
    // matches (или -1, если нет финального).
    let finalMatchIdx = -1;
    if (lastSigNodeIdx >= 0) {
      const sigContent = allTextNodes[lastSigNodeIdx].nodeValue;
      // matches пишутся в обратном порядке внутри node + node-order;
      // нам нужен match с максимальным (nodeIdx, tIndex). Идём по
      // matches с начала (это уже max-first внутри nodeIdx, но между
      // nodeIdx порядок прямой). Простой линейный поиск:
      let bestIdx = -1;
      let bestNI = -1, bestTI = -1;
      for (let mi = 0; mi < matches.length; mi++) {
        const m = matches[mi];
        if (m.nodeIdx > bestNI ||
            (m.nodeIdx === bestNI && m.tIndex > bestTI)) {
          bestIdx = mi;
          bestNI = m.nodeIdx;
          bestTI = m.tIndex;
        }
      }
      if (bestIdx >= 0 && matches[bestIdx].nodeIdx === lastSigNodeIdx) {
        const m = matches[bestIdx];
        const rest = sigContent.slice(m.punctIndex + 1);
        if (!/[A-Za-zÀ-ÿĀ-ſ]/.test(rest)) {
          finalMatchIdx = bestIdx;
        }
      }
    }

    // Шаг 4 — обернуть все matches, кроме финального.
    // ВАЖНО: внутри одного nodeIdx идём по матчам в порядке убывания
    // tIndex (как и были собраны). Между разными nodeIdx порядок не
    // важен для корректности, но для предсказуемости пройдёмся в
    // обратном порядке вообще.
    for (let mi = matches.length - 1; mi >= 0; mi--) {
      if (mi === finalMatchIdx) {
        preservedCount++;
        continue;
      }
      const m = matches[mi];
      wrapAsNoTOrn(allTextNodes[m.nodeIdx], m.tIndex);
      wrappedCount++;
    }
  }

  if (window.console) {
    console.log(
      '[t.orn-guard] wrapped=' + wrappedCount +
      ' preserved=' + preservedCount
    );
  }
}

// Оборачивает символ в позиции tIndex (single char) в
// <span class="no-t-orn">. Узел разбивается на: text-before +
// span(char) + text-after.
function wrapAsNoTOrn(textNode, tIndex) {
  const v = textNode.nodeValue;
  const before = v.slice(0, tIndex);
  const ch = v[tIndex];
  const after = v.slice(tIndex + 1);

  const parent = textNode.parentNode;
  if (!parent) return;

  const span = document.createElement('span');
  span.className = 'no-t-orn';
  span.textContent = ch;

  if (before.length > 0) {
    parent.insertBefore(document.createTextNode(before), textNode);
  }
  parent.insertBefore(span, textNode);
  if (after.length > 0) {
    parent.insertBefore(document.createTextNode(after), textNode);
  }
  parent.removeChild(textNode);
}