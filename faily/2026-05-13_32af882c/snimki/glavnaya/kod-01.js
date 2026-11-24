const recentDev = [];
const WINDOW = 8;          // примерно слов в строке кодекса
const PULL_K = 0.6;        // насколько сильно тянем назад

function wrapSpace() {
  if (!SPACE_JITTER_ENABLED) return document.createTextNode(' ');
  
  let w = (spaceRand() + spaceRand()) * 0.5;
  
  // Сумма отклонений по последним WINDOW пробелам
  let dev = 0;
  for (const d of recentDev) dev += d;
  
  // Если уже накоплено отклонение — корректируем
  w = Math.max(0, Math.min(1, w - dev * PULL_K / WINDOW));
  
  recentDev.push(w - 0.5);
  if (recentDev.length > WINDOW) recentDev.shift();
  
  const sp = document.createElement('span');
  sp.className = 'ws';
  sp.style.cssText = '--w:' + w.toFixed(3);
  sp.appendChild(document.createTextNode(' '));
  return sp;
}