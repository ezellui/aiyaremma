import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown, ChevronUp, Plus, Trash, Save, Download, Info, X, Edit, Check, Undo, Redo, ZoomIn, ZoomOut, Move, Maximize, Upload, AlertTriangle, RotateCcw } from 'lucide-react';

const PhilosophyGraph = () => {
  // Основные категории и типы связей из задания
  const categories = [
    'Бытие', 'Сущность', 'Сознание', 'Материя', 'Субстанция', 
    'Субъект', 'Мир', 'Истина', 'Знание', 'Язык', 
    'Знак', 'Время', 'Пространство', 'Свобода', 'Необходимость', 
    'Ценность', 'Трансцендентное', 'Имманентное', 'Единое', 'Множественное',
    'Целое', 'Разрыв'
  ];

  const relationTypes = [
    'Причинность', 'Тождество', 'Дополнение', 'Диалектическое противоречие', 
    'Иерархическая', 'Герменевтическая', 'Репрезентационная', 'Конституирующая', 
    'Эпистемическая', 'Феноменологическая', 'Эволюционная', 'Аксиологическая', 'Телеологическая'
  ];

  // Состояния для хранения данных
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [isAddingNode, setIsAddingNode] = useState(false);
  const [isAddingEdge, setIsAddingEdge] = useState(false);
  const [sourceNode, setSourceNode] = useState(null);
  const [currentConceptName, setCurrentConceptName] = useState('Новая концепция');
  const [conceptDescription, setConceptDescription] = useState('');
  const [savedConcepts, setSavedConcepts] = useState([]);
  const [showHelp, setShowHelp] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [editingConceptName, setEditingConceptName] = useState(false);
  const [editingDescription, setEditingDescription] = useState(false);
  const [customNodeName, setCustomNodeName] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(categories[0]);
  const [customCategory, setCustomCategory] = useState('');
  const [showCustomCategory, setShowCustomCategory] = useState(false);
  const [bidirectional, setBidirectional] = useState(false);
  const [selectedRelationType, setSelectedRelationType] = useState(relationTypes[0]);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNode, setDraggedNode] = useState(null);
  // Флаг для проверки одновременного состояния
  const [activeMode, setActiveMode] = useState(null); // 'node', 'edge', or null
  
  // История действий для Undo/Redo
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [ignoreHistoryUpdate, setIgnoreHistoryUpdate] = useState(false);
  
  // Настройки масштабирования и панорамирования
  const [scale, setScale] = useState(1);
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);
  const [isPanning, setIsPanning] = useState(false);
  const [panStartX, setPanStartX] = useState(0);
  const [panStartY, setPanStartY] = useState(0);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [confirmMessage, setConfirmMessage] = useState('');
  
  // Функция для добавления действия в историю
  const addToHistory = useCallback((nodesCurrent, edgesCurrent) => {
    if (ignoreHistoryUpdate) return;
    
    // Обрезаем историю если мы находимся не в конце (случай Undo и нового действия)
    const newHistory = history.slice(0, historyIndex + 1);
    
    // Добавляем новое состояние
    newHistory.push({
      nodes: JSON.parse(JSON.stringify(nodesCurrent)),
      edges: JSON.parse(JSON.stringify(edgesCurrent))
    });
    
    // Если история слишком длинная, удаляем старые записи
    if (newHistory.length > 30) {
      newHistory.shift();
    }
    
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  }, [history, historyIndex, ignoreHistoryUpdate]);

  // Функция Undo
  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      setIgnoreHistoryUpdate(true);
      const prevState = history[historyIndex - 1];
      setNodes(prevState.nodes);
      setEdges(prevState.edges);
      setHistoryIndex(historyIndex - 1);
      setTimeout(() => setIgnoreHistoryUpdate(false), 0);
    }
  }, [history, historyIndex]);

  // Функция Redo
  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setIgnoreHistoryUpdate(true);
      const nextState = history[historyIndex + 1];
      setNodes(nextState.nodes);
      setEdges(nextState.edges);
      setHistoryIndex(historyIndex + 1);
      setTimeout(() => setIgnoreHistoryUpdate(false), 0);
    }
  }, [history, historyIndex]);

  // Отслеживаем изменения nodes и edges для истории
  useEffect(() => {
    if (!ignoreHistoryUpdate && (nodes.length > 0 || edges.length > 0)) {
      addToHistory(nodes, edges);
    }
  }, [nodes, edges, addToHistory]);

  // Инициализация истории
  useEffect(() => {
    if (history.length === 0 && (nodes.length > 0 || edges.length > 0)) {
      addToHistory(nodes, edges);
    }
  }, [history, nodes, edges, addToHistory]);

  // Цветовая схема для категорий (группируем их по смыслу)
  const categoryColors = {
    'Бытие': '#FF6B6B', 'Сущность': '#FF6B6B', 'Материя': '#FF6B6B', 'Субстанция': '#FF6B6B',
    'Сознание': '#4ECDC4', 'Субъект': '#4ECDC4', 'Знание': '#4ECDC4', 
    'Мир': '#FFD166', 'Пространство': '#FFD166', 'Время': '#FFD166',
    'Истина': '#6B5CA5', 'Язык': '#6B5CA5', 'Знак': '#6B5CA5',
    'Свобода': '#F9F871', 'Необходимость': '#F9F871',
    'Ценность': '#1A535C', 'Трансцендентное': '#1A535C', 'Имманентное': '#1A535C',
    'Единое': '#C06C84', 'Множественное': '#C06C84', 'Целое': '#C06C84',
    'Разрыв': '#E76F51'
  };

  // Функция для получения цвета категории или генерации его для пользовательских категорий
  const getCategoryColor = (category) => {
    return categoryColors[category] || '#AAAAAA';
  };

  // Эффект для инициализации холста
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    
    // Адаптация размера холста к размеру контейнера
    const resizeCanvas = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        canvas.width = width;
        canvas.height = height;
        drawGraph();
      }
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  // Эффект для предотвращения одновременных режимов
  useEffect(() => {
    if (isAddingNode && isAddingEdge) {
      console.warn('Конфликт режимов: попытка активировать два режима одновременно');
      // В случае конфликта приоритет отдаем последнему активированному режиму (activeMode)
      if (activeMode === 'node') {
        setIsAddingEdge(false);
        setSourceNode(null);
      } else if (activeMode === 'edge') {
        setIsAddingNode(false);
        setCustomNodeName('');
        setShowCustomCategory(false);
        setCustomCategory('');
      }
    }
  }, [isAddingNode, isAddingEdge, activeMode]);

  // Перерисовка графа при изменении данных
  useEffect(() => {
    drawGraph();
  }, [nodes, edges, selectedNode, selectedEdge, sourceNode, isDragging]);

  // Функция для рисования графа
  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    // Сохраняем текущую трансформацию
    context.save();
    
    // Применяем масштабирование и смещение
    context.translate(offsetX, offsetY);
    context.scale(scale, scale);
    
    // Рисуем связи
    edges.forEach((edge, index) => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode) {
        // Определяем цвет связи
        context.strokeStyle = selectedEdge === index ? '#FF4757' : '#808080';
        context.lineWidth = selectedEdge === index ? 3/scale : 2/scale;
        
        // Вычисляем координаты
        const startX = sourceNode.x;
        const startY = sourceNode.y;
        const endX = targetNode.x;
        const endY = targetNode.y;
        
        // Рисуем линию
        context.beginPath();
        context.moveTo(startX, startY);
        context.lineTo(endX, endY);
        context.stroke();
        
        // Вычисляем координаты для текста и стрелки
        const dx = endX - startX;
        const dy = endY - startY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const midX = startX + dx * 0.5;
        const midY = startY + dy * 0.5;
        
        // Рисуем текст типа связи
        context.fillStyle = '#000000';
        context.font = `${12/scale}px Arial`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(edge.type, midX, midY - 10/scale);
        
        // Рисуем стрелку на целевом узле
        const arrowSize = 10/scale;
        const arrowX = startX + dx * 0.9;
        const arrowY = startY + dy * 0.9;
        const angle = Math.atan2(dy, dx);
        
        context.beginPath();
        context.moveTo(arrowX, arrowY);
        context.lineTo(
          arrowX - arrowSize * Math.cos(angle - Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        context.lineTo(
          arrowX - arrowSize * Math.cos(angle + Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        context.closePath();
        context.fillStyle = context.strokeStyle;
        context.fill();
        
        // Если связь двунаправленная, рисуем вторую стрелку
        if (edge.bidirectional) {
          const arrowX2 = startX + dx * 0.1;
          const arrowY2 = startY + dy * 0.1;
          
          context.beginPath();
          context.moveTo(arrowX2, arrowY2);
          context.lineTo(
            arrowX2 + arrowSize * Math.cos(angle - Math.PI / 6),
            arrowY2 + arrowSize * Math.sin(angle - Math.PI / 6)
          );
          context.lineTo(
            arrowX2 + arrowSize * Math.cos(angle + Math.PI / 6),
            arrowY2 + arrowSize * Math.sin(angle + Math.PI / 6)
          );
          context.closePath();
          context.fillStyle = context.strokeStyle;
          context.fill();
        }
      }
    });
    
    // Рисуем узлы
    nodes.forEach((node, index) => {
      // Определяем цвет узла
      context.fillStyle = getCategoryColor(node.category);
      
      // Если узел выбран или используется для связи, подсвечиваем его
      if (selectedNode === index || sourceNode === index || (isDragging && draggedNode === index)) {
        context.shadowBlur = 15/scale;
        context.shadowColor = '#2684FF';
      } else {
        context.shadowBlur = 0;
      }
      
      // Рисуем кружок для узла
      context.beginPath();
      context.arc(node.x, node.y, 20/scale, 0, 2 * Math.PI);
      context.fill();
      
      // Сбрасываем тень
      context.shadowBlur = 0;
      
      // Рисуем текст узла
      context.fillStyle = '#000000';
      context.font = `${12/scale}px Arial`;
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillText(node.name, node.x, node.y);
      
      // Рисуем категорию под узлом
      context.font = `${10/scale}px Arial`;
      context.fillText(node.category, node.x, node.y + 30/scale);
    });
    
    // Если пользователь добавляет связь, рисуем временную линию от источника к текущей позиции мыши
    if (isAddingEdge && sourceNode !== null) {
      const source = nodes[sourceNode];
      if (source) {
        context.strokeStyle = '#2684FF';
        context.lineWidth = 2/scale;
        context.setLineDash([5/scale, 5/scale]);
        
        // Преобразуем координаты мыши в координаты канваса с учетом масштаба и смещения
        const mouseCanvasX = (canvas.mouseX - offsetX) / scale;
        const mouseCanvasY = (canvas.mouseY - offsetY) / scale;
        
        context.beginPath();
        context.moveTo(source.x, source.y);
        context.lineTo(mouseCanvasX || source.x + 100, mouseCanvasY || source.y);
        context.stroke();
        
        context.setLineDash([]);
      }
    }
    
    // Восстанавливаем трансформацию
    context.restore();
  };

  // Обработчики мыши
  const handleCanvasMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    canvas.mouseX = e.clientX - rect.left;
    canvas.mouseY = e.clientY - rect.top;
    
    if (isAddingEdge) {
      drawGraph();
    }
    
    if (isDragging && draggedNode !== null) {
      const newNodes = [...nodes];
      // Проверяем, что индекс действителен
      if (draggedNode >= 0 && draggedNode < newNodes.length) {
        // Обновляем позицию с учетом масштаба и смещения
        newNodes[draggedNode].x = (canvas.mouseX - offsetX) / scale;
        newNodes[draggedNode].y = (canvas.mouseY - offsetY) / scale;
        setNodes(newNodes);
      } else {
        // Сбрасываем состояние перетаскивания, если индекс недействителен
        setIsDragging(false);
        setDraggedNode(null);
      }
    }
    
    // Панорамирование
    if (isPanning) {
      const dx = canvas.mouseX - panStartX;
      const dy = canvas.mouseY - panStartY;
      setOffsetX(offsetX + dx);
      setOffsetY(offsetY + dy);
      setPanStartX(canvas.mouseX);
      setPanStartY(canvas.mouseY);
    }
  };

  const handleCanvasMouseDown = (e) => {
    if (editingConceptName || editingDescription) {
      // Если пользователь редактирует текст, игнорируем клики по холсту
      return;
    }
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Сохраняем начальные координаты для панорамирования
    setPanStartX(x);
    setPanStartY(y);
    
    // Проверяем правую кнопку мыши для панорамирования
    if (e.button === 2) {
      e.preventDefault();
      setIsPanning(true);
      return;
    }
    
    // Преобразуем координаты клика с учетом масштаба и смещения
    const canvasX = (x - offsetX) / scale;
    const canvasY = (y - offsetY) / scale;
    
    // Проверяем, кликнул ли пользователь по узлу
    let nodeClicked = false;
    nodes.forEach((node, index) => {
      const distance = Math.sqrt((canvasX - node.x) ** 2 + (canvasY - node.y) ** 2);
      if (distance <= 20 / scale) {
        nodeClicked = true;
        
        if (isAddingEdge && sourceNode !== null) {
          // Завершаем добавление связи
          if (sourceNode !== index) {
            const newEdge = {
              source: nodes[sourceNode].id,
              target: node.id,
              type: selectedRelationType,
              bidirectional: bidirectional
            };
            setEdges([...edges, newEdge]);
          }
          setSourceNode(null);
          setIsAddingEdge(false);
          setActiveMode(null);
        } else if (isAddingEdge) {
          // Начинаем добавление связи
          setSourceNode(index);
        } else {
          // Начинаем перетаскивание или выбираем узел только если не в режиме добавления
          if (!isAddingEdge && !isAddingNode) {
            setIsDragging(true);
            setDraggedNode(index);
            setSelectedNode(index);
            setSelectedEdge(null);
          }
        }
      }
    });
    
    // Проверяем, кликнул ли пользователь по связи
    if (!nodeClicked && !isAddingEdge && !isAddingNode) {
      let edgeClicked = false;
      edges.forEach((edge, index) => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);
        
        if (source && target) {
          // Преобразуем координаты с учетом масштаба
          const sx = source.x;
          const sy = source.y;
          const tx = target.x;
          const ty = target.y;
          
          // Проверяем, находится ли точка достаточно близко к линии
          const A = canvasY - sy;
          const B = sx - canvasX;
          const C = sx * sy - sx * canvasY;
          
          const distance = Math.abs(A * tx + B * ty + C) / Math.sqrt(A * A + B * B);
          
          // Проверяем, находится ли точка между двумя концами линии
          const dotProduct = ((canvasX - sx) * (tx - sx) + (canvasY - sy) * (ty - sy));
          const squaredLength = ((tx - sx) ** 2 + (ty - sy) ** 2);
          
          if (distance < 10 / scale && dotProduct >= 0 && dotProduct <= squaredLength) {
            edgeClicked = true;
            setSelectedEdge(index);
            setSelectedNode(null);
          }
        }
      });
      
      if (!edgeClicked) {
        // Если пользователь кликнул по пустому месту и активен режим добавления узлов
        if (isAddingNode) {
          const newNode = {
            id: nodes.length > 0 ? Math.max(...nodes.map(n => n.id)) + 1 : 0,
            name: customNodeName || 'Узел ' + (nodes.length + 1),
            category: showCustomCategory ? customCategory : selectedCategory,
            x: canvasX,
            y: canvasY
          };
          setNodes([...nodes, newNode]);
          setIsAddingNode(false);
          setActiveMode(null);
          setCustomNodeName('');
          setShowCustomCategory(false);
          setCustomCategory('');
        } else {
          // Снимаем выделение
          setSelectedNode(null);
          setSelectedEdge(null);
        }
      }
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
    setDraggedNode(null);
    setIsPanning(false);
  };
  
  const handleCanvasWheel = (e) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Вычисляем точку, относительно которой будем масштабировать (позиция курсора)
    const x = (mouseX - offsetX) / scale;
    const y = (mouseY - offsetY) / scale;
    
    // Определяем новый масштаб
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.1, Math.min(5, scale * delta));
    
    // Корректируем смещение, чтобы центр масштабирования оставался под курсором
    const newOffsetX = mouseX - x * newScale;
    const newOffsetY = mouseY - y * newScale;
    
    setScale(newScale);
    setOffsetX(newOffsetX);
    setOffsetY(newOffsetY);
  };
  
  const handleCanvasContextMenu = (e) => {
    e.preventDefault(); // Отключаем стандартное контекстное меню
  };, что индекс действителен
      if (draggedNode >= 0 && draggedNode < newNodes.length) {
        newNodes[draggedNode].x = canvas.mouseX;
        newNodes[draggedNode].y = canvas.mouseY;
        setNodes(newNodes);
      } else {
        // Сбрасываем состояние перетаскивания, если индекс недействителен
        setIsDragging(false);
        setDraggedNode(null);
      }
    }
  };

  const handleCanvasMouseDown = (e) => {
    if (editingConceptName || editingDescription) {
      // Если пользователь редактирует текст, игнорируем клики по холсту
      return;
    }
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Проверяем, кликнул ли пользователь по узлу
    let nodeClicked = false;
    nodes.forEach((node, index) => {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
      if (distance <= 20) {
        nodeClicked = true;
        
        if (isAddingEdge && sourceNode !== null) {
          // Завершаем добавление связи
          if (sourceNode !== index) {
            const newEdge = {
              source: nodes[sourceNode].id,
              target: node.id,
              type: selectedRelationType,
              bidirectional: bidirectional
            };
            setEdges([...edges, newEdge]);
          }
          setSourceNode(null);
          setIsAddingEdge(false);
          setActiveMode(null);
        } else if (isAddingEdge) {
          // Начинаем добавление связи
          setSourceNode(index);
        } else {
          // Начинаем перетаскивание или выбираем узел только если не в режиме добавления
          if (!isAddingEdge && !isAddingNode) {
            setIsDragging(true);
            setDraggedNode(index);
            setSelectedNode(index);
            setSelectedEdge(null);
          }
        }
      }
    });
    
    // Проверяем, кликнул ли пользователь по связи
    if (!nodeClicked && !isAddingEdge && !isAddingNode) {
      let edgeClicked = false;
      edges.forEach((edge, index) => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);
        
        if (source && target) {
          // Проверяем, находится ли точка достаточно близко к линии
          const A = y - source.y;
          const B = source.x - x;
          const C = source.x * source.y - source.x * y;
          
          const distance = Math.abs(A * target.x + B * target.y + C) / Math.sqrt(A * A + B * B);
          
          // Проверяем, находится ли точка между двумя концами линии
          const dotProduct = ((x - source.x) * (target.x - source.x) + (y - source.y) * (target.y - source.y));
          const squaredLength = ((target.x - source.x) ** 2 + (target.y - source.y) ** 2);
          
          if (distance < 10 && dotProduct >= 0 && dotProduct <= squaredLength) {
            edgeClicked = true;
            setSelectedEdge(index);
            setSelectedNode(null);
          }
        }
      });
      
      if (!edgeClicked) {
        // Если пользователь кликнул по пустому месту и активен режим добавления узлов
        if (isAddingNode) {
          const newNode = {
            id: nodes.length > 0 ? Math.max(...nodes.map(n => n.id)) + 1 : 0,
            name: customNodeName || 'Узел ' + (nodes.length + 1),
            category: showCustomCategory ? customCategory : selectedCategory,
            x: x,
            y: y
          };
          setNodes([...nodes, newNode]);
          setIsAddingNode(false);
          setActiveMode(null);
          setCustomNodeName('');
          setShowCustomCategory(false);
          setCustomCategory('');
        } else {
          // Снимаем выделение
          setSelectedNode(null);
          setSelectedEdge(null);
        }
      }
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
    setDraggedNode(null);
  };

  // Функция для удаления выбранного элемента
  const handleDelete = () => {
    if (selectedNode !== null) {
      // Удаляем узел и все связанные с ним связи
      const nodeId = nodes[selectedNode].id;
      setNodes(nodes.filter((_, i) => i !== selectedNode));
      setEdges(edges.filter(edge => edge.source !== nodeId && edge.target !== nodeId));
      setSelectedNode(null);
    } else if (selectedEdge !== null) {
      // Удаляем связь
      setEdges(edges.filter((_, i) => i !== selectedEdge));
      setSelectedEdge(null);
    }
  };

  // Функция для сохранения текущей концепции
  const handleSave = () => {
    // Проверяем, что у концепции есть название
    if (!currentConceptName.trim()) {
      alert('Пожалуйста, введите название концепции перед сохранением');
      setEditingConceptName(true);
      return;
    }
    
    // Проверяем, что в концепции есть узлы
    if (nodes.length === 0) {
      alert('Нельзя сохранить пустую концепцию. Добавьте хотя бы один узел');
      return;
    }
    
    const conceptToSave = {
      name: currentConceptName,
      description: conceptDescription,
      nodes: [...nodes],
      edges: [...edges],
      date: new Date().toLocaleDateString()
    };
    
    // Проверяем, не существует ли концепция с таким именем
    const existingIndex = savedConcepts.findIndex(c => c.name === currentConceptName);
    if (existingIndex >= 0) {
      if (window.confirm(`Концепция с названием "${currentConceptName}" уже существует. Заменить?`)) {
        const updatedConcepts = [...savedConcepts];
        updatedConcepts[existingIndex] = conceptToSave;
        setSavedConcepts(updatedConcepts);
      } else {
        return;
      }
    } else {
      setSavedConcepts([...savedConcepts, conceptToSave]);
    }
    
    setShowSaved(true);
  };

  // Функция для загрузки сохраненной концепции
  const handleLoad = (concept) => {
    setNodes(concept.nodes);
    setEdges(concept.edges);
    setCurrentConceptName(concept.name);
    setConceptDescription(concept.description);
    setShowSaved(false);
  };

  // Функция для экспорта концепции в JSON
  const handleExport = () => {
    const conceptData = {
      name: currentConceptName,
      description: conceptDescription,
      nodes: nodes,
      edges: edges
    };
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(conceptData));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", currentConceptName.replace(/\s+/g, '_') + ".json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  // Подготовка информации о выбранном элементе для панели свойств
  const selectedInfo = () => {
    if (selectedNode !== null) {
      const node = nodes[selectedNode];
      return (
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-2">Свойства узла</h3>
          <p><span className="font-semibold">Название:</span> {node.name}</p>
          <p><span className="font-semibold">Категория:</span> {node.category}</p>
          <p><span className="font-semibold">ID:</span> {node.id}</p>
          <div className="mt-4">
            <button 
              className="bg-red-500 text-white px-3 py-1 rounded flex items-center text-sm"
              onClick={handleDelete}
            >
              <Trash size={16} className="mr-1" /> Удалить
            </button>
          </div>
        </div>
      );
    } else if (selectedEdge !== null) {
      const edge = edges[selectedEdge];
      const source = nodes.find(n => n.id === edge.source);
      const target = nodes.find(n => n.id === edge.target);
      
      return (
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-2">Свойства связи</h3>
          <p><span className="font-semibold">Тип:</span> {edge.type}</p>
          <p><span className="font-semibold">От:</span> {source ? source.name : 'Неизвестно'}</p>
          <p><span className="font-semibold">К:</span> {target ? target.name : 'Неизвестно'}</p>
          <p><span className="font-semibold">Двунаправленная:</span> {edge.bidirectional ? 'Да' : 'Нет'}</p>
          <div className="mt-4">
            <button 
              className="bg-red-500 text-white px-3 py-1 rounded flex items-center text-sm"
              onClick={handleDelete}
            >
              <Trash size={16} className="mr-1" /> Удалить
            </button>
          </div>
        </div>
      );
    }
    
    return (
      <div className="p-4 text-center text-gray-500">
        Выберите элемент на схеме для просмотра его свойств
      </div>
    );
  };

  // Легенда категорий
  const categoryLegend = () => (
    <div className="p-4 bg-white rounded-md shadow-md">
      <h3 className="text-lg font-semibold mb-2">Легенда категорий</h3>
      <div className="grid grid-cols-2 gap-2">
        {categories.map(category => (
          <div key={category} className="flex items-center">
            <div 
              className="w-4 h-4 rounded-full mr-2" 
              style={{ backgroundColor: getCategoryColor(category) }}
            ></div>
            <span className="text-sm">{category}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full overflow-hidden bg-gray-100">
      {/* Верхняя панель */}
      <div className="bg-gray-800 text-white p-4 flex items-center justify-between">
        <div className="flex items-center">
          {editingConceptName ? (
            <div className="flex items-center">
              <input 
                type="text" 
                value={currentConceptName} 
                onChange={(e) => setCurrentConceptName(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white mr-2"
              />
              <button 
                onClick={() => setEditingConceptName(false)}
                className="text-green-400"
              >
                <Check size={20} />
              </button>
            </div>
          ) : (
            <div className="flex items-center">
              <h1 className="text-xl font-bold mr-2">{currentConceptName}</h1>
              <button 
                onClick={() => setEditingConceptName(true)}
                className="text-gray-400 hover:text-white"
              >
                <Edit size={16} />
              </button>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            className="bg-blue-600 text-white px-3 py-1 rounded flex items-center text-sm"
            onClick={() => setShowHelp(!showHelp)}
          >
            <Info size={16} className="mr-1" /> Помощь
          </button>
          <button 
            className="bg-green-600 text-white px-3 py-1 rounded flex items-center text-sm"
            onClick={handleSave}
          >
            <Save size={16} className="mr-1" /> Сохранить
          </button>
          <button 
            className="bg-purple-600 text-white px-3 py-1 rounded flex items-center text-sm"
            onClick={handleExport}
          >
            <Download size={16} className="mr-1" /> Экспорт
          </button>
          <button 
            className="bg-amber-600 text-white px-3 py-1 rounded flex items-center text-sm"
            onClick={() => setShowSaved(!showSaved)}
          >
            <ChevronDown size={16} className="mr-1" /> Сохраненные
          </button>
        </div>
      </div>
      
      {/* Панель описания */}
      <div className="bg-gray-200 p-3 flex items-center">
        <div className="font-semibold mr-2">Описание:</div>
        {editingDescription ? (
          <div className="flex-1 flex items-center">
            <input 
              type="text" 
              value={conceptDescription} 
              onChange={(e) => setConceptDescription(e.target.value)}
              className="flex-1 bg-white border border-gray-300 rounded px-2 py-1 mr-2"
              placeholder="Введите описание концепции..."
            />
            <button 
              onClick={() => setEditingDescription(false)}
              className="text-green-600"
            >
              <Check size={20} />
            </button>
          </div>
        ) : (
          <div className="flex-1 flex items-center">
            <span className="text-gray-600 flex-1">
              {conceptDescription || "Нет описания"}
            </span>
            <button 
              onClick={() => setEditingDescription(true)}
              className="text-gray-500 hover:text-gray-800"
            >
              <Edit size={16} />
            </button>
          </div>
        )}
      </div>
      
      {/* Выпадающий список сохраненных концепций */}
      {showSaved && savedConcepts.length > 0 && (
        <div className="bg-white border-b border-gray-300 p-2">
          <h3 className="font-semibold mb-2">Сохраненные концепции:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {savedConcepts.map((concept, index) => (
              <div 
                key={index} 
                className="border border-gray-300 rounded p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => handleLoad(concept)}
              >
                <div className="font-medium">{concept.name}</div>
                <div className="text-sm text-gray-500">
                  {concept.date} • {concept.nodes.length} узлов • {concept.edges.length} связей
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Справка */}
      {showHelp && (
        <div className="bg-white border-b border-gray-300 p-4 relative">
          <button 
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
            onClick={() => setShowHelp(false)}
          >
            <X size={20} />
          </button>
          <h3 className="font-bold text-lg mb-2">Как пользоваться конструктором философских концепций</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-1">Основные функции:</h4>
              <ul className="list-disc list-inside text-sm">
                <li>Добавляйте узлы (философские категории) и связи между ними</li>
                <li>Выбирайте типы связей и задавайте их направление</li>
                <li>Перетаскивайте узлы для удобного расположения на схеме</li>
                <li>Сохраняйте и экспортируйте созданные концепции</li>
                <li>Редактируйте название и описание концепции</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-1">Управление:</h4>
              <ul className="list-disc list-inside text-sm">
                <li>Нажмите "Добавить узел", затем кликните на холст для размещения</li>
                <li>Нажмите "Добавить связь", выберите тип связи, затем последовательно кликните по двум узлам</li>
                <li>Выберите узел и перетащите его по холсту для изменения расположения</li>
                <li>Выберите узел или связь, чтобы увидеть их свойства в правой панели</li>
                <li>Используйте кнопку "Удалить" для удаления выбранного элемента</li>
              </ul>
            </div>
          </div>
          <div className="mt-4">
            <h4 className="font-semibold mb-1">Цветовая схема категорий:</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(categoryColors).filter((value, index, self) => 
                self.findIndex(v => v[1] === value[1]) === index
              ).map(([category, color]) => (
                <div key={color} className="flex items-center">
                  <div 
                    className="w-4 h-4 rounded-full mr-2" 
                    style={{ backgroundColor: color }}
                  ></div>
                  <span className="text-sm">{category}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Основной интерфейс */}
      <div className="flex flex-1 overflow-hidden">
        {/* Левая панель инструментов */}
        <div className="w-64 bg-gray-200 p-4 flex flex-col">
          <h3 className="font-semibold mb-3">Инструменты</h3>
          
          {/* Инструменты работы с узлами */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">Узлы</h4>
            
            {isAddingNode ? (
              <div className="mb-3 p-3 bg-white rounded-md shadow-sm">
                <div className="mb-2">
                  <label className="block text-sm mb-1">Название узла:</label>
                  <input 
                    type="text" 
                    value={customNodeName} 
                    onChange={(e) => setCustomNodeName(e.target.value)}
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    placeholder="Введите название"
                  />
                </div>
                
                <div className="mb-2">
                  <label className="flex items-center text-sm mb-1">
                    <input 
                      type="checkbox" 
                      checked={showCustomCategory}
                      onChange={() => setShowCustomCategory(!showCustomCategory)}
                      className="mr-1"
                    />
                    Своя категория
                  </label>
                  
                  {showCustomCategory ? (
                    <input 
                      type="text" 
                      value={customCategory} 
                      onChange={(e) => setCustomCategory(e.target.value)}
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                      placeholder="Введите категорию"
                    />
                  ) : (
                    <select 
                      className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  )}
                </div>
                
                <div className="flex justify-between mt-2">
                  <button 
                    className="bg-gray-400 text-white px-2 py-1 rounded text-sm"
                    onClick={() => setIsAddingNode(false)}
                  >
                    Отмена
                  </button>
                  <button 
                    className="bg-blue-500 text-white px-2 py-1 rounded text-sm"
                    onClick={() => {
                      const newNode = {
                        id: nodes.length > 0 ? Math.max(...nodes.map(n => n.id)) + 1 : 0,
                        name: customNodeName || 'Узел ' + (nodes.length + 1),
                        category: showCustomCategory ? customCategory : selectedCategory,
                        x: containerRef.current.clientWidth / 2,
                        y: containerRef.current.clientHeight / 2
                      };
                      setNodes([...nodes, newNode]);
                      setIsAddingNode(false);
                      setActiveMode(null);
                      setCustomNodeName('');
                      setShowCustomCategory(false);
                      setCustomCategory('');
                    }}
                  >
                    Создать
                  </button>
                </div>
              </div>
            ) : (
              <button 
                className="bg-blue-500 text-white px-3 py-2 rounded w-full flex items-center justify-center text-sm mb-3"
                onClick={() => {
                  if (isAddingEdge) {
                    setIsAddingEdge(false);
                    setSourceNode(null);
                  }
                  setIsAddingNode(true);
                  setActiveMode('node');
                }}
              >
                <Plus size={16} className="mr-1" /> Добавить узел
              </button>
            )}
            
            {/* Легенда категорий */}
            {categoryLegend()}
          </div>
          
          {/* Инструменты работы со связями */}
          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Связи</h4>
            
            {isAddingEdge ? (
              <div className="mb-3 p-3 bg-white rounded-md shadow-sm">
                <div className="mb-2">
                  <label className="block text-sm mb-1">Тип связи:</label>
                  <select 
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                    value={selectedRelationType}
                    onChange={(e) => setSelectedRelationType(e.target.value)}
                  >
                    {relationTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
                
                <div className="mb-2">
                  <label className="flex items-center text-sm">
                    <input 
                      type="checkbox" 
                      checked={bidirectional}
                      onChange={() => setBidirectional(!bidirectional)}
                      className="mr-1"
                    />
                    Двунаправленная связь
                  </label>
                </div>
                
                <div className="mt-2 text-sm">
                  {sourceNode === null ? (
                    <p>Выберите узел-источник</p>
                  ) : (
                    <p>Выберите узел-назначение</p>
                  )}
                </div>
                
                <div className="flex justify-between mt-2">
                  <button 
                    className="bg-gray-400 text-white px-2 py-1 rounded text-sm"
                    onClick={() => {
                      setIsAddingEdge(false);
                      setActiveMode(null);
                      setSourceNode(null);
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            ) : (
              <button 
                className="bg-green-500 text-white px-3 py-2 rounded w-full flex items-center justify-center text-sm"
                onClick={() => {
                  if (isAddingNode) {
                    setIsAddingNode(false);
                    setCustomNodeName('');
                    setShowCustomCategory(false);
                    setCustomCategory('');
                  }
                  setIsAddingEdge(true);
                  setActiveMode('edge');
                }}
              >
                <Plus size={16} className="mr-1" /> Добавить связь
              </button>
            )}
          </div>
          
          {/* Примеры готовых концепций */}
          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Примеры концепций</h4>
            <div className="bg-white rounded-md shadow-sm p-2">
              <div 
                className="border border-gray-200 rounded p-2 cursor-pointer hover:bg-gray-100 mb-2"
                onClick={() => {
                  // Пример: Онтология Гегеля
                  const hegelNodes = [
                    {id: 0, name: "Бытие", category: "Бытие", x: 300, y: 100},
                    {id: 1, name: "Ничто", category: "Бытие", x: 500, y: 100},
                    {id: 2, name: "Становление", category: "Бытие", x: 400, y: 200},
                    {id: 3, name: "Сущность", category: "Сущность", x: 400, y: 300},
                    {id: 4, name: "Понятие", category: "Сознание", x: 400, y: 400},
                    {id: 5, name: "Идея", category: "Целое", x: 400, y: 500}
                  ];
                  
                  const hegelEdges = [
                    {source: 0, target: 1, type: "Диалектическое противоречие", bidirectional: true},
                    {source: 0, target: 2, type: "Эволюционная", bidirectional: false},
                    {source: 1, target: 2, type: "Эволюционная", bidirectional: false},
                    {source: 2, target: 3, type: "Эволюционная", bidirectional: false},
                    {source: 3, target: 4, type: "Эволюционная", bidirectional: false},
                    {source: 4, target: 5, type: "Телеологическая", bidirectional: false}
                  ];
                  
                  setNodes(hegelNodes);
                  setEdges(hegelEdges);
                  setCurrentConceptName("Диалектическая онтология Гегеля");
                  setConceptDescription("Схематическое представление диалектической системы Гегеля, начинающееся с противоречия бытия и ничто и развивающееся к абсолютной идее");
                }}
              >
                <div className="font-medium">Диалектическая онтология Гегеля</div>
                <div className="text-sm text-gray-500">6 узлов • 6 связей</div>
              </div>
              
              <div 
                className="border border-gray-200 rounded p-2 cursor-pointer hover:bg-gray-100 mb-2"
                onClick={() => {
                  // Пример: Эпистемология Канта
                  const kantNodes = [
                    {id: 0, name: "Вещь-в-себе", category: "Трансцендентное", x: 200, y: 150},
                    {id: 1, name: "Явление", category: "Феномен", x: 400, y: 150},
                    {id: 2, name: "Рассудок", category: "Сознание", x: 400, y: 300},
                    {id: 3, name: "Чувственность", category: "Сознание", x: 200, y: 300},
                    {id: 4, name: "Пространство", category: "Пространство", x: 100, y: 400},
                    {id: 5, name: "Время", category: "Время", x: 300, y: 400},
                    {id: 6, name: "Категории", category: "Знание", x: 500, y: 400}
                  ];
                  
                  const kantEdges = [
                    {source: 0, target: 1, type: "Феноменологическая", bidirectional: false},
                    {source: 3, target: 1, type: "Конституирующая", bidirectional: false},
                    {source: 2, target: 1, type: "Конституирующая", bidirectional: false},
                    {source: 3, target: 4, type: "Конституирующая", bidirectional: false},
                    {source: 3, target: 5, type: "Конституирующая", bidirectional: false},
                    {source: 2, target: 6, type: "Конституирующая", bidirectional: false}
                  ];
                  
                  setNodes(kantNodes);
                  setEdges(kantEdges);
                  setCurrentConceptName("Эпистемология Канта");
                  setConceptDescription("Схема кантовской теории познания с разделением на вещи-в-себе и явления, а также структурой познавательных способностей");
                }}
              >
                <div className="font-medium">Эпистемология Канта</div>
                <div className="text-sm text-gray-500">7 узлов • 6 связей</div>
              </div>
              
              <div 
                className="border border-gray-200 rounded p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => {
                  // Пример: Онтология Хайдеггера
                  const heideggerNodes = [
                    {id: 0, name: "Dasein", category: "Бытие", x: 400, y: 150},
                    {id: 1, name: "Мир", category: "Мир", x: 250, y: 250},
                    {id: 2, name: "Бытие-в-мире", category: "Бытие", x: 400, y: 250},
                    {id: 3, name: "Временность", category: "Время", x: 550, y: 250},
                    {id: 4, name: "Забота", category: "Сознание", x: 400, y: 350},
                    {id: 5, name: "Смерть", category: "Разрыв", x: 250, y: 350},
                    {id: 6, name: "Язык", category: "Язык", x: 550, y: 350},
                    {id: 7, name: "Бытие", category: "Бытие", x: 400, y: 450}
                  ];
                  
                  const heideggerEdges = [
                    {source: 0, target: 2, type: "Конституирующая", bidirectional: false},
                    {source: 1, target: 2, type: "Конституирующая", bidirectional: false},
                    {source: 0, target: 4, type: "Конституирующая", bidirectional: false},
                    {source: 3, target: 0, type: "Конституирующая", bidirectional: false},
                    {source: 5, target: 0, type: "Конституирующая", bidirectional: false},
                    {source: 0, target: 7, type: "Герменевтическая", bidirectional: false},
                    {source: 6, target: 7, type: "Репрезентационная", bidirectional: false}
                  ];
                  
                  setNodes(heideggerNodes);
                  setEdges(heideggerEdges);
                  setCurrentConceptName("Фундаментальная онтология Хайдеггера");
                  setConceptDescription("Схематизация основных концептов фундаментальной онтологии Мартина Хайдеггера, центрированная вокруг Dasein");
                }}
              >
                <div className="font-medium">Фундаментальная онтология Хайдеггера</div>
                <div className="text-sm text-gray-500">8 узлов • 7 связей</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Центральный холст */}
        <div className="flex-1 relative" ref={containerRef}>
          <canvas 
            ref={canvasRef} 
            className="absolute inset-0 w-full h-full"
            onMouseMove={handleCanvasMouseMove}
            onMouseDown={handleCanvasMouseDown}
            onMouseUp={handleCanvasMouseUp}
          ></canvas>
        </div>
        
        {/* Правая панель свойств */}
        <div className="w-64 bg-gray-200 border-l border-gray-300 flex flex-col">
          <div className="p-3 border-b border-gray-300 font-semibold">
            Свойства
          </div>
          
          {selectedInfo()}
        </div>
      </div>
    </div>
  );
};

export default PhilosophyGraph;