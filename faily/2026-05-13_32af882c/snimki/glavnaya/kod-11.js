// Геометрические критерии runt'а — последняя строка абзаца, которая
// палеографически могла бы поместиться в поле страницы (5–6 букв
// или менее по совокупности шрифтов основного текста).
//
// folio-pad-outer = 82 px — буфер поля. Реальный «лечимый» хвост
// меньше, потому что разделяет с маргиналиями и не должен наезжать
// на bounding-line.
//
// Двойной критерий ИЛИ: либо узкая по абсолютной ширине строка
// (~5 букв самого крупного шрифта Uncialis), либо строка <10% от
// предпоследней (для абзацев в любой колонке, в т.ч. с margin-left).
const RUNT_MAX_LINE_WIDTH_PX = 65;
const RUNT_MAX_LINE_FRACTION = 0.10;

function analyzeRunt(p) {
  // ... тот же сбор byLine ...
  
  const last = byLine[byLine.length - 1];
  const penult = byLine[byLine.length - 2];

  const isRunt =
    last.width <= RUNT_MAX_LINE_WIDTH_PX ||
    (last.width / penult.width) < RUNT_MAX_LINE_FRACTION;

  if (!isRunt) return null;
  // ...
}