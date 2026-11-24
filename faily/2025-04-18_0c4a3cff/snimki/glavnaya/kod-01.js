// Функция для добавления действия в историю
const addToHistory = useCallback((nodesCurrent, edgesCurrent) => {
  if (ignoreHistoryUpdate) return;
  
  // Создаем полные глубокие копии для предотвращения проблем ссылок
  const nodesDeepCopy = JSON.parse(JSON.stringify(nodesCurrent));
  const edgesDeepCopy = JSON.parse(JSON.stringify(edgesCurrent));
  
  // Обрезаем историю если мы находимся не в конце (случай Undo и нового действия)
  const newHistory = history.slice(0, historyIndex + 1);
  
  // Добавляем новое состояние
  newHistory.push({
    nodes: nodesDeepCopy,
    edges: edgesDeepCopy
  });
  
  // Если история слишком длинная, удаляем старые записи
  if (newHistory.length > 30) {
    newHistory.shift();
  }
  
  setHistory(newHistory);
  setHistoryIndex(newHistory.length - 1);
}, [history, historyIndex, ignoreHistoryUpdate]);