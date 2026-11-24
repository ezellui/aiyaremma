# WebGL-рендеринг для эффективной визуализации

Для реализации WebGL-рендеринга требуется добавить альтернативный метод визуализации с использованием Three.js, который будет автоматически задействован для крупных сетей.

## 1. Добавление зависимостей Three.js

Добавьте следующий скрипт в раздел `<head>` после загрузки D3.js:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
```

## 2. Добавление переключателя режимов рендеринга

Добавьте в секцию `.controls-extra` (после строки с `<div class="controls-extra">`) следующий HTML-код:

```html
<div class="rendering-options">
  <label>
    <input type="checkbox" id="use-webgl"> 
    Использовать WebGL (для больших сетей)
  </label>
  <span id="rendering-info" class="info-badge">SVG</span>
</div>
```

## 3. Добавление стилей для элементов управления WebGL

Добавьте в раздел `<style>` следующие CSS-правила:

```css
.rendering-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #e0e0e0;
  border-radius: 3px;
  font-size: 0.8rem;
  color: #333;
}

#webgl-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
  display: none;
}

/* Стиль для предупреждения о производительности */
.performance-warning {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(255, 248, 219, 0.9);
  border: 1px solid #e8d495;
  border-radius: 5px;
  padding: 10px 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 80%;
  text-align: center;
  display: flex;
  align-items: center;
  gap: 8px;
  animation: fadeIn 0.5s ease;
}

.performance-warning .warning-icon {
  font-size: 1.5rem;
  color: #e8a202;
}

.performance-warning .dismiss {
  margin-left: 10px;
  padding: 2px 8px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
```

## 4. Реализация WebGL-рендеринга

Добавьте следующий код в конец файла `<script>`:

```javascript
/**
 * Система WebGL-рендеринга для более эффективной визуализации крупных сетей
 */
class WebGLRenderer {
  constructor(container, data) {
    this.container = container;
    this.data = data;
    this.width = container.clientWidth;
    this.height = container.clientHeight;
    this.initialized = false;
    this.nodeObjects = new Map(); // Для хранения соответствия между узлами данных и объектами Three.js
    this.lineObjects = new Map(); // Для хранения соответствия между связями и объектами Three.js
    
    // Создаем контейнер для WebGL
    this.webglContainer = document.createElement('div');
    this.webglContainer.id = 'webgl-container';
    container.appendChild(this.webglContainer);
    
    // Флаг режима рендеринга
    this.active = false;
  }
  
  /**
   * Инициализирует Three.js-рендерер
   */
  init() {
    if (this.initialized) return;
    
    // Создаем сцену, камеру и рендерер
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xffffff);
    
    this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, 0.1, 1000);
    this.camera.position.z = 500;
    
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.width, this.height);
    this.webglContainer.appendChild(this.renderer.domElement);
    
    // Добавляем элементы управления для камеры
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.25;
    this.controls.screenSpacePanning = true;
    
    // Добавляем свет
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight.position.set(1, 1, 1);
    this.scene.add(directionalLight);
    
    // Создаем группу для всех объектов сети
    this.networkGroup = new THREE.Group();
    this.scene.add(this.networkGroup);
    
    // Флаг инициализации
    this.initialized = true;
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', () => this.handleResize());
    
    // Инициализация системы выделения узлов
    this.setupRaycaster();
  }
  
  /**
   * Настраивает систему определения кликов по объектам
   */
  setupRaycaster() {
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    
    // Обработчик клика мыши для выбора узла
    const renderer = this;
    this.renderer.domElement.addEventListener('click', function(event) {
      // Преобразование координат мыши в нормализованные координаты от -1 до 1
      const rect = renderer.renderer.domElement.getBoundingClientRect();
      renderer.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      renderer.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      // Устанавливаем луч от камеры через точку клика мыши
      renderer.raycaster.setFromCamera(renderer.mouse, renderer.camera);
      
      // Находим пересечения луча с объектами узлов
      const intersects = renderer.raycaster.intersectObjects(renderer.networkGroup.children, true);
      
      if (intersects.length > 0) {
        // Перебираем все пересечения и находим первый узел
        for (const intersection of intersects) {
          const object = intersection.object;
          if (object.userData.type === 'node') {
            // Нашли узел - показываем информацию
            renderer.highlightNode(object);
            const nodeData = object.userData.nodeData;
            showNodeInfo(nodeData);
            break;
          }
        }
      }
    });
    
    // Двойной клик для открытия детальной информации
    this.renderer.domElement.addEventListener('dblclick', function(event) {
      const rect = renderer.renderer.domElement.getBoundingClientRect();
      renderer.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      renderer.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      renderer.raycaster.setFromCamera(renderer.mouse, renderer.camera);
      const intersects = renderer.raycaster.intersectObjects(renderer.networkGroup.children, true);
      
      if (intersects.length > 0) {
        for (const intersection of intersects) {
          const object = intersection.object;
          if (object.userData.type === 'node') {
            const nodeData = object.userData.nodeData;
            showDetailedInfo(nodeData, document.querySelector(".detail-popup"), {links: renderer.data.links});
            break;
          }
        }
      }
    });
  }
  
  /**
   * Выделяет узел и сбрасывает предыдущее выделение
   */
  highlightNode(object) {
    // Сбрасываем все выделения
    this.networkGroup.children.forEach(obj => {
      if (obj.userData.type === 'node') {
        // Восстанавливаем оригинальный цвет и размер
        if (obj.userData.originalMaterial) {
          obj.material = obj.userData.originalMaterial.clone();
        }
        if (obj.userData.originalScale) {
          obj.scale.copy(obj.userData.originalScale);
        }
      }
    });
    
    // Сохраняем оригинальный материал, если еще не сохранен
    if (!object.userData.originalMaterial) {
      object.userData.originalMaterial = object.material.clone();
    }
    if (!object.userData.originalScale) {
      object.userData.originalScale = object.scale.clone();
    }
    
    // Выделяем выбранный узел
    const highlightMaterial = object.material.clone();
    highlightMaterial.emissive = new THREE.Color(0x555555);
    highlightMaterial.emissiveIntensity = 0.5;
    object.material = highlightMaterial;
    
    // Увеличиваем выбранный узел
    object.scale.multiplyScalar(1.3);
  }
  
  /**
   * Обработка изменения размера окна
   */
  handleResize() {
    if (!this.initialized) return;
    
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    
    this.camera.aspect = this.width / this.height;
    this.camera.updateProjectionMatrix();
    
    this.renderer.setSize(this.width, this.height);
  }
  
  /**
   * Отображает данные сети в WebGL
   * @param {Array} nodes - Массив узлов
   * @param {Array} links - Массив связей
   */
  renderNetwork(nodes, links) {
    if (!this.initialized) this.init();
    
    // Очищаем предыдущие данные
    while (this.networkGroup.children.length > 0) {
      this.networkGroup.remove(this.networkGroup.children[0]);
    }
    
    this.nodeObjects.clear();
    this.lineObjects.clear();
    
    // Создаем геометрию для узлов (сфер)
    const defaultNodeSize = 7;
    const nodeGeometry = new THREE.SphereGeometry(defaultNodeSize, 16, 16);
    
    // Добавляем узлы
    nodes.forEach(node => {
      // Определяем цвет узла на основе группы
      const nodeColor = getNodeColor(node.group);
      const color = new THREE.Color(nodeColor);
      
      // Создаем материал с соответствующим цветом
      const material = new THREE.MeshPhongMaterial({ 
        color: color,
        shininess: 60
      });
      
      // Создаем меш для узла
      const nodeMesh = new THREE.Mesh(nodeGeometry, material);
      
      // Устанавливаем позицию узла
      nodeMesh.position.set(
        node.x !== undefined ? node.x - this.width/2 : (Math.random() - 0.5) * 500,
        node.y !== undefined ? node.y - this.height/2 : (Math.random() - 0.5) * 500,
        0
      );
      
      // Добавляем данные узла для интерактивности
      nodeMesh.userData = {
        type: 'node',
        nodeData: node
      };
      
      // Добавляем меш в группу объектов сети
      this.networkGroup.add(nodeMesh);
      
      // Сохраняем соответствие между данными узла и объектом Three.js
      this.nodeObjects.set(node.id, nodeMesh);
      
      // Создаем метку с именем для узла
      this.createNodeLabel(node, nodeMesh);
    });
    
    // Добавляем связи между узлами
    links.forEach(link => {
      // Получаем объекты узлов для данной связи
      const sourceNode = this.nodeObjects.get(link.source.id || link.source);
      const targetNode = this.nodeObjects.get(link.target.id || link.target);
      
      if (sourceNode && targetNode) {
        // Создаем геометрию линии
        const lineGeometry = new THREE.BufferGeometry();
        const lineMaterial = new THREE.LineBasicMaterial({ 
          color: this.getLinkColor(link),
          linewidth: this.getLinkWidth(link),
          transparent: true,
          opacity: 0.8
        });
        
        // Устанавливаем начальные и конечные точки линии
        const points = [
          sourceNode.position.clone(),
          targetNode.position.clone()
        ];
        lineGeometry.setFromPoints(points);
        
        // Создаем линию и добавляем её в группу
        const line = new THREE.Line(lineGeometry, lineMaterial);
        line.userData = {
          type: 'link',
          linkData: link
        };
        
        this.networkGroup.add(line);
        
        // Сохраняем соответствие между данными связи и объектом Three.js
        this.lineObjects.set(link, line);
      }
    });
    
    // Центрируем камеру на группе сети
    const box = new THREE.Box3().setFromObject(this.networkGroup);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = this.camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    
    // Устанавливаем позицию камеры
    this.camera.position.z = cameraZ * 1.5;
    this.controls.update();
    
    // Запускаем анимацию
    this.animate();
  }
  
  /**
   * Создает текстовую метку для узла
   */
  createNodeLabel(node, nodeMesh) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    // Настраиваем стиль текста
    context.font = 'Bold 20px Arial';
    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    
    // Отрисовываем текст
    context.fillText(node.name, 128, 32);
    
    // Создаем текстуру из canvas
    const texture = new THREE.CanvasTexture(canvas);
    
    // Создаем спрайт с текстурой
    const spriteMaterial = new THREE.SpriteMaterial({ 
      map: texture,
      transparent: true
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(100, 25, 1);
    sprite.position.set(nodeMesh.position.x, nodeMesh.position.y + 15, nodeMesh.position.z);
    
    // Добавляем спрайт в группу
    this.networkGroup.add(sprite);
  }
  
  /**
   * Определяет цвет связи на основе её типа
   */
  getLinkColor(link) {
    switch (link.type) {
      case 'acquaintance':
        return 0x4CAF50;
      case 'false':
        return 0xF44336;
      case 'indirect':
        return 0x9E9E9E;
      default:
        return 0x333333;
    }
  }
  
  /**
   * Определяет толщину связи на основе её типа
   */
  getLinkWidth(link) {
    switch (link.type) {
      case 'mutual':
      case 'polemic':
        return 2;
      default:
        return 1;
    }
  }
  
  /**
   * Запускает цикл анимации
   */
  animate() {
    if (!this.active) return;
    
    requestAnimationFrame(() => this.animate());
    
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
  
  /**
   * Активирует WebGL-рендеринг
   */
  activate() {
    this.active = true;
    this.webglContainer.style.display = 'block';
    this.animate();
  }
  
  /**
   * Деактивирует WebGL-рендеринг
   */
  deactivate() {
    this.active = false;
    this.webglContainer.style.display = 'none';
  }
  
  /**
   * Обновляет позиции узлов и связей на основе данных симуляции D3
   */
  updatePositions() {
    if (!this.active || !this.initialized) return;
    
    // Обновляем позиции узлов
    this.nodeObjects.forEach((nodeMesh, nodeId) => {
      const nodeData = nodeMesh.userData.nodeData;
      
      if (nodeData.x !== undefined && nodeData.y !== undefined) {
        nodeMesh.position.set(
          nodeData.x - this.width/2,
          nodeData.y - this.height/2,
          0
        );
        
        // Обновляем также позиции меток
        // Ищем спрайт метки (это следующий объект после узла)
        const index = this.networkGroup.children.indexOf(nodeMesh);
        if (index >= 0 && index + 1 < this.networkGroup.children.length) {
          const nextObj = this.networkGroup.children[index + 1];
          if (nextObj.type === 'Sprite') {
            nextObj.position.set(
              nodeMesh.position.x,
              nodeMesh.position.y + 15,
              nodeMesh.position.z
            );
          }
        }
      }
    });
    
    // Обновляем позиции связей
    this.lineObjects.forEach((line, link) => {
      const sourceNode = this.nodeObjects.get(link.source.id || link.source);
      const targetNode = this.nodeObjects.get(link.target.id || link.target);
      
      if (sourceNode && targetNode) {
        const geometry = line.geometry;
        const positions = geometry.attributes.position.array;
        
        positions[0] = sourceNode.position.x;
        positions[1] = sourceNode.position.y;
        positions[2] = sourceNode.position.z;
        
        positions[3] = targetNode.position.x;
        positions[4] = targetNode.position.y;
        positions[5] = targetNode.position.z;
        
        geometry.attributes.position.needsUpdate = true;
      }
    });
  }
}

/**
 * Функция для автоматического определения необходимости использования WebGL
 * @param {Object} data - Данные сети
 * @returns {boolean} - Нужно ли использовать WebGL
 */
function shouldUseWebGL(data) {
  // Если количество узлов или связей превышает порог, рекомендуем WebGL
  const NODE_THRESHOLD = 100;
  const LINK_THRESHOLD = 200;
  
  const nodeCount = data.nodes.length;
  const linkCount = data.links.length;
  
  return nodeCount > NODE_THRESHOLD || linkCount > LINK_THRESHOLD;
}

/**
 * Показывает предупреждение о производительности
 * @param {string} message - Сообщение предупреждения
 */
function showPerformanceWarning(message) {
  // Проверяем, не показано ли уже предупреждение
  if (document.querySelector('.performance-warning')) return;
  
  const warning = document.createElement('div');
  warning.className = 'performance-warning';
  warning.innerHTML = `
    <span class="warning-icon">⚠️</span>
    <span>${message}</span>
    <button class="dismiss">OK</button>
  `;
  
  document.body.appendChild(warning);
  
  // Обработчик кнопки закрытия
  warning.querySelector('.dismiss').addEventListener('click', () => {
    warning.style.opacity = '0';
    setTimeout(() => warning.remove(), 300);
  });
  
  // Автоматическое скрытие через 10 секунд
  setTimeout(() => {
    if (document.body.contains(warning)) {
      warning.style.opacity = '0';
      setTimeout(() => warning.remove(), 300);
    }
  }, 10000);
}

/**
 * Интегрирует WebGL-рендеринг в приложение
 * @param {Object} network - Объект с компонентами сети
 * @param {Object} data - Данные сети
 */
function integrateWebGLRendering(network, data) {
  // Создаем экземпляр WebGL-рендерера
  const container = document.getElementById('network');
  const webglRenderer = new WebGLRenderer(container, data);
  
  // Добавляем обработчик для переключателя режима рендеринга
  const useWebGLCheckbox = document.getElementById('use-webgl');
  const renderingInfo = document.getElementById('rendering-info');
  
  // Проверяем, нужно ли рекомендовать WebGL
  const shouldUseWebGLRendering = shouldUseWebGL(data);
  
  if (shouldUseWebGLRendering) {
    // Если сеть большая, автоматически включаем WebGL
    useWebGLCheckbox.checked = true;
    showPerformanceWarning('Обнаружена крупная сеть. Автоматически включен режим WebGL для повышения производительности.');
  }
  
  // Инициализируем состояние в зависимости от чекбокса
  if (useWebGLCheckbox.checked) {
    // Инициализируем WebGL и отображаем данные
    webglRenderer.renderNetwork(data.nodes, data.links);
    webglRenderer.activate();
    renderingInfo.textContent = 'WebGL';
    
    // Скрываем SVG-отображение
    d3.select('#network svg').style('display', 'none');
  }
  
  // Обработчик изменения режима рендеринга
  useWebGLCheckbox.addEventListener('change', function() {
    if (this.checked) {
      // Включаем WebGL
      webglRenderer.renderNetwork(data.nodes, data.links);
      webglRenderer.activate();
      renderingInfo.textContent = 'WebGL';
      
      // Скрываем SVG-отображение
      d3.select('#network svg').style('display', 'none');
    } else {
      // Отключаем WebGL и показываем SVG
      webglRenderer.deactivate();
      renderingInfo.textContent = 'SVG';
      
      d3.select('#network svg').style('display', 'block');
    }
  });
  
  // Синхронизируем обновления позиций от симуляции D3 с WebGL
  if (network.simulation) {
    // Добавляем обработчик события tick для обновления WebGL
    const originalTickFunction = network.simulation.on('tick');
    
    network.simulation.on('tick', () => {
      // Вызываем оригинальную функцию tick для обновления SVG
      if (originalTickFunction) {
        originalTickFunction();
      }
      
      // Обновляем позиции в WebGL
      webglRenderer.updatePositions();
    });
  }
  
  // Сохраняем webglRenderer для дальнейшего использования
  network.webglRenderer = webglRenderer;
  
  // Добавляем Three.js OrbitControls (нужно добавить соответствующую библиотеку)
  if (window.THREE) {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/controls/OrbitControls.js';
    document.head.appendChild(script);
  }
}

// Добавьте вызов функции в конец функции integrateComponents
// Найдите функцию integrateComponents и добавьте в её конец:
function integrateComponents(graphData) {
  // Существующий код...
  
  // Добавьте в конец функции:
  integrateWebGLRendering(network, graphData);
}
```

## 5. Добавление тестирования и предупреждений о производительности

Добавьте следующую функцию для автоматического тестирования производительности:

```javascript
/**
 * Тестирует производительность рендеринга
 * @param {Object} network - Объект с компонентами сети
 * @returns {boolean} - Результат теста (true - высокая производительность, false - низкая)
 */
function testRenderingPerformance(network) {
  // Создаем тестовую сцену с множеством объектов для проверки производительности
  const testNodeCount = 200;
  const startTime = performance.now();
  
  // Временно скрываем элементы для теста
  network.svg.style('visibility', 'hidden');
  
  // Создаем временные узлы для теста
  const tempNodes = [];
  for (let i = 0; i < testNodeCount; i++) {
    tempNodes.push({
      id: `test-${i}`,
      name: `Тестовый узел ${i}`,
      x: Math.random() * network.svg.node().clientWidth,
      y: Math.random() * network.svg.node().clientHeight,
      group: 'ancient',
      groupName: 'Тестовая группа'
    });
  }
  
  // Создаем временные связи
  const tempLinks = [];
  for (let i = 0; i < testNodeCount / 2; i++) {
    tempLinks.push({
      source: tempNodes[i],
      target: tempNodes[i + Math.floor(testNodeCount / 2)],
      type: 'influence'
    });
  }
  
  // Создаем временные элементы для теста
  const tempG = network.svg.append('g').attr('class', 'temp-test-group');
  
  // Добавляем узлы
  tempG.selectAll('.temp-node')
    .data(tempNodes)
    .enter()
    .append('circle')
    .attr('class', 'temp-node')
    .attr('r', 5)
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('fill', '#ccc');
  
  // Добавляем связи
  tempG.selectAll('.temp-link')
    .data(tempLinks)
    .enter()
    .append('line')
    .attr('class', 'temp-link')
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y)
    .attr('stroke', '#999');
  
  // Форсируем перерисовку
  tempG.node().getBoundingClientRect();
  
  // Измеряем производительность
  const endTime = performance.now();
  const renderTime = endTime - startTime;
  
  // Удаляем временные элементы
  tempG.remove();
  
  // Восстанавливаем видимость
  network.svg.style('visibility', 'visible');
  
  // Проверяем производительность (если рендеринг занял более 100мс, рекомендуем WebGL)
  return {
    time: renderTime,
    isHighPerformance: renderTime < 100
  };
}

// Интегрируем тест производительности в основную функцию
function integrateComponents(graphData) {
  // Существующий код инициализации...
  
  // Тестируем производительность и показываем рекомендации
  const perfTest = testRenderingPerformance(network);
  const useWebGLCheckbox = document.getElementById('use-webgl');
  
  // Если производительность низкая, рекомендуем WebGL
  if (!perfTest.isHighPerformance && !useWebGLCheckbox.checked) {
    showPerformanceWarning(`Тест производительности: ${Math.round(perfTest.time)}мс. Рекомендуется включить WebGL для улучшения скорости отрисовки.`);
  }
  
  // Продолжение существующего кода...
}
```

Эти изменения добавят возможность использования WebGL для рендеринга больших сетей, что значительно повысит производительность при работе с крупными наборами данных. WebGL-рендеринг будет автоматически рекомендован, если сеть содержит большое количество узлов или связей, а также если тест производительности показывает низкие результаты.
