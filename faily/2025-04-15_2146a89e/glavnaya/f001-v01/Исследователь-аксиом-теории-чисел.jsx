import React, { useState, useEffect } from 'react';

const NumberTheoryAxiomExplorer = () => {
  // Состояния для отслеживания выбранных аксиом
  const [selectedAxioms, setSelectedAxioms] = useState({
    peano: true,
    closure: false,
    commutativity: false,
    associativity: false,
    distributivity: false,
    identity: false,
    inverse: false,
    wellOrdering: false,
    completeness: false,
    leastUpperBound: false
  });

  // Состояние для отслеживания выбранной числовой системы
  const [numberSystem, setNumberSystem] = useState('natural');

  // Определения аксиом
  const axiomDefinitions = {
    peano: 'Аксиомы Пеано: 1) 0 — натуральное число; 2) У каждого натурального числа есть единственный последователь; 3) 0 не является последователем никакого натурального числа; 4) Разные натуральные числа имеют разных последователей; 5) Если некоторое множество содержит 0 и содержит последователя любого своего элемента, то это множество содержит все натуральные числа (принцип математической индукции).',
    closure: 'Замкнутость: Для любых двух чисел a и b из нашего множества, их сумма и произведение также принадлежат этому множеству.',
    commutativity: 'Коммутативность: Для любых чисел a и b: a + b = b + a и a × b = b × a.',
    associativity: 'Ассоциативность: Для любых чисел a, b и c: (a + b) + c = a + (b + c) и (a × b) × c = a × (b × c).',
    distributivity: 'Дистрибутивность: Для любых чисел a, b и c: a × (b + c) = (a × b) + (a × c).',
    identity: 'Существование нейтральных элементов: Существует число 0, такое что a + 0 = a для любого числа a. Существует число 1, такое что a × 1 = a для любого числа a.',
    inverse: 'Существование обратных элементов: Для каждого числа a существует число -a такое, что a + (-a) = 0. Для каждого ненулевого числа a существует число 1/a такое, что a × (1/a) = 1.',
    wellOrdering: 'Принцип полной индукции: Любое непустое подмножество натуральных чисел имеет наименьший элемент.',
    completeness: 'Полнота: Любая непустая ограниченная сверху последовательность имеет точную верхнюю грань.',
    leastUpperBound: 'Аксиома наименьшей верхней грани: Всякое непустое подмножество чисел, ограниченное сверху, имеет точную верхнюю грань.'
  };

  // Числовые системы и их требуемые аксиомы
  const numberSystems = {
    natural: {
      name: 'Натуральные числа (ℕ)',
      requiredAxioms: ['peano', 'wellOrdering'],
      description: 'Натуральные числа (1, 2, 3, ...) являются базовой числовой системой, построенной на аксиомах Пеано.',
      operations: ['сложение', 'умножение'],
      properties: [
        'Замкнутость относительно сложения и умножения',
        'Дискретность',
        'Принцип математической индукции применим'
      ]
    },
    integer: {
      name: 'Целые числа (ℤ)',
      requiredAxioms: ['peano', 'closure', 'commutativity', 'associativity', 'identity', 'inverse'],
      description: 'Целые числа (..., -2, -1, 0, 1, 2, ...) расширяют натуральные числа, добавляя отрицательные числа.',
      operations: ['сложение', 'вычитание', 'умножение'],
      properties: [
        'Замкнутость относительно сложения, вычитания и умножения',
        'Не замкнуты относительно деления',
        'Образуют кольцо с единицей'
      ]
    },
    rational: {
      name: 'Рациональные числа (ℚ)',
      requiredAxioms: ['closure', 'commutativity', 'associativity', 'distributivity', 'identity', 'inverse'],
      description: 'Рациональные числа (дроби вида p/q, где p и q - целые, q≠0) расширяют целые числа, позволяя деление.',
      operations: ['сложение', 'вычитание', 'умножение', 'деление'],
      properties: [
        'Замкнутость относительно четырех арифметических операций (кроме деления на ноль)',
        'Плотность: между любыми двумя рациональными числами есть еще одно рациональное число',
        'Образуют поле'
      ]
    },
    real: {
      name: 'Действительные числа (ℝ)',
      requiredAxioms: ['closure', 'commutativity', 'associativity', 'distributivity', 'identity', 'inverse', 'completeness', 'leastUpperBound'],
      description: 'Действительные числа включают рациональные и иррациональные числа, заполняя все точки числовой прямой.',
      operations: ['сложение', 'вычитание', 'умножение', 'деление', 'пределы', 'интегралы'],
      properties: [
        'Полнота: любая ограниченная сверху последовательность имеет супремум',
        'Непрерывность числовой прямой',
        'Существование иррациональных чисел (π, e, √2, ...)',
        'Образуют полное упорядоченное поле'
      ]
    },
    complex: {
      name: 'Комплексные числа (ℂ)',
      requiredAxioms: ['closure', 'commutativity', 'associativity', 'distributivity', 'identity', 'inverse'],
      description: 'Комплексные числа (a + bi, где a и b - действительные числа, i² = -1) расширяют действительные числа, добавляя мнимую единицу i.',
      operations: ['сложение', 'вычитание', 'умножение', 'деление', 'возведение в степень'],
      properties: [
        'Алгебраическая замкнутость: любое полиномиальное уравнение имеет решение',
        'Нет порядка (не определены "больше" и "меньше")',
        'Существование корней из отрицательных чисел',
        'Образуют алгебраически замкнутое поле'
      ]
    }
  };

  // Состояние для отображения текущих выводов
  const [conclusions, setConclusions] = useState([]);

  // Эффект для обновления выводов при изменении выбранных аксиом
  useEffect(() => {
    updateConclusions();
  }, [selectedAxioms, numberSystem]);

  // Функция для обновления выводов
  const updateConclusions = () => {
    let newConclusions = [];
    
    // Проверка совместимости выбранных аксиом
    const incompatibilities = checkIncompatibilities();
    if (incompatibilities.length > 0) {
      setConclusions(incompatibilities);
      return;
    }
    
    // Базовые выводы в зависимости от выбранных аксиом
    if (selectedAxioms.peano) {
      newConclusions.push("Существуют натуральные числа с операцией следования.");
      newConclusions.push("Принцип математической индукции применим.");
    }
    
    if (selectedAxioms.closure) {
      newConclusions.push("Множество замкнуто относительно операций сложения и умножения.");
    }
    
    if (selectedAxioms.commutativity) {
      newConclusions.push("Сложение и умножение коммутативны (порядок операндов не важен).");
    }
    
    if (selectedAxioms.associativity) {
      newConclusions.push("Сложение и умножение ассоциативны (порядок группировки не важен).");
    }
    
    if (selectedAxioms.identity) {
      newConclusions.push("Существуют нейтральные элементы 0 и 1 для сложения и умножения.");
    }
    
    if (selectedAxioms.distributivity) {
      newConclusions.push("Умножение дистрибутивно относительно сложения.");
    }
    
    if (selectedAxioms.inverse) {
      newConclusions.push("Для каждого элемента существует обратный по сложению.");
      newConclusions.push("Для каждого ненулевого элемента существует обратный по умножению.");
    }
    
    if (selectedAxioms.wellOrdering) {
      newConclusions.push("Множество обладает свойством полной индукции.");
    }
    
    if (selectedAxioms.completeness || selectedAxioms.leastUpperBound) {
      newConclusions.push("Множество полно - не содержит 'пробелов' на числовой прямой.");
    }
    
    // Определение типа числовой системы на основе выбранных аксиом
    let identifiedSystem = determineNumberSystem();
    if (identifiedSystem) {
      newConclusions.push(`Выбранные аксиомы характеризуют ${identifiedSystem}.`);
    }
    
    // Проверка на теоремы, которые следуют из выбранных аксиом
    if (selectedAxioms.peano && selectedAxioms.commutativity && selectedAxioms.associativity) {
      newConclusions.push("Теорема: Сложение и умножение натуральных чисел коммутативны и ассоциативны.");
    }
    
    if (selectedAxioms.peano && selectedAxioms.wellOrdering) {
      newConclusions.push("Теорема: Любое непустое подмножество натуральных чисел имеет наименьший элемент.");
    }
    
    if (selectedAxioms.closure && selectedAxioms.commutativity && selectedAxioms.associativity && 
        selectedAxioms.distributivity && selectedAxioms.identity && selectedAxioms.inverse) {
      newConclusions.push("Теорема: Структура является полем.");
    }
    
    if (selectedAxioms.completeness && selectedAxioms.closure && selectedAxioms.commutativity && 
        selectedAxioms.associativity && selectedAxioms.distributivity && selectedAxioms.identity && 
        selectedAxioms.inverse) {
      newConclusions.push("Теорема: Структура является полным полем (таким как действительные числа).");
    }
    
    // Добавление сведений о выбранной числовой системе
    addNumberSystemInfo(newConclusions);
    
    setConclusions(newConclusions);
  };
  
  // Функция для проверки несовместимостей аксиом
  const checkIncompatibilities = () => {
    let issues = [];
    
    // Пример проверки несовместимости
    if (selectedAxioms.completeness && !selectedAxioms.closure) {
      issues.push("Предупреждение: Аксиома полноты обычно требует замкнутости для корректного определения.");
    }
    
    if (selectedAxioms.inverse && !selectedAxioms.identity) {
      issues.push("Предупреждение: Понятие обратного элемента требует наличия нейтрального элемента.");
    }
    
    return issues;
  };
  
  // Функция для определения числовой системы на основе выбранных аксиом
  const determineNumberSystem = () => {
    // Проверяем натуральные числа
    if (selectedAxioms.peano && selectedAxioms.wellOrdering && 
        !selectedAxioms.inverse) {
      return "натуральные числа (ℕ)";
    }
    
    // Проверяем целые числа
    if (selectedAxioms.peano && selectedAxioms.closure && 
        selectedAxioms.commutativity && selectedAxioms.associativity && 
        selectedAxioms.identity && selectedAxioms.inverse && 
        !selectedAxioms.completeness) {
      return "целые числа (ℤ)";
    }
    
    // Проверяем рациональные числа
    if (selectedAxioms.closure && selectedAxioms.commutativity && 
        selectedAxioms.associativity && selectedAxioms.distributivity && 
        selectedAxioms.identity && selectedAxioms.inverse && 
        !selectedAxioms.completeness) {
      return "рациональные числа (ℚ)";
    }
    
    // Проверяем действительные числа
    if (selectedAxioms.closure && selectedAxioms.commutativity && 
        selectedAxioms.associativity && selectedAxioms.distributivity && 
        selectedAxioms.identity && selectedAxioms.inverse && 
        (selectedAxioms.completeness || selectedAxioms.leastUpperBound)) {
      return "действительные числа (ℝ)";
    }
    
    // Если не можем точно определить
    return null;
  };
  
  // Функция добавления информации о выбранной числовой системе
  const addNumberSystemInfo = (conclusions) => {
    const system = numberSystems[numberSystem];
    
    // Проверяем, выбраны ли все необходимые аксиомы
    const missingAxioms = system.requiredAxioms.filter(axiom => !selectedAxioms[axiom]);
    
    if (missingAxioms.length > 0) {
      conclusions.push(`Для системы ${system.name} не хватает следующих аксиом: ${missingAxioms.map(a => a.charAt(0).toUpperCase() + a.slice(1)).join(', ')}`);
    } else {
      conclusions.push(`Выбранная система ${system.name} полностью определена выбранными аксиомами.`);
      conclusions.push(`Основные свойства ${system.name}:`);
      system.properties.forEach(prop => {
        conclusions.push(`- ${prop}`);
      });
    }
  };
  
  // Обработчик изменения аксиомы
  const handleAxiomChange = (axiom) => {
    setSelectedAxioms({
      ...selectedAxioms,
      [axiom]: !selectedAxioms[axiom]
    });
  };
  
  // Обработчик выбора предустановленного набора аксиом
  const handlePresetSelect = (preset) => {
    // Предустановленные наборы аксиом для разных числовых систем
    const presets = {
      natural: {
        peano: true,
        closure: true,
        commutativity: true,
        associativity: true,
        distributivity: true,
        identity: true,
        inverse: false,
        wellOrdering: true,
        completeness: false,
        leastUpperBound: false
      },
      integer: {
        peano: true,
        closure: true,
        commutativity: true,
        associativity: true,
        distributivity: true,
        identity: true,
        inverse: true,
        wellOrdering: true,
        completeness: false,
        leastUpperBound: false
      },
      rational: {
        peano: false,
        closure: true,
        commutativity: true,
        associativity: true,
        distributivity: true,
        identity: true,
        inverse: true,
        wellOrdering: false,
        completeness: false,
        leastUpperBound: false
      },
      real: {
        peano: false,
        closure: true,
        commutativity: true,
        associativity: true,
        distributivity: true,
        identity: true,
        inverse: true,
        wellOrdering: false,
        completeness: true,
        leastUpperBound: true
      },
      complex: {
        peano: false,
        closure: true,
        commutativity: true,
        associativity: true,
        distributivity: true,
        identity: true,
        inverse: true,
        wellOrdering: false,
        completeness: false,
        leastUpperBound: false
      }
    };
    
    setSelectedAxioms(presets[preset]);
    setNumberSystem(preset);
  };

  return (
    <div className="p-4 max-w-6xl mx-auto bg-gray-50 rounded-lg shadow-md">
      <h1 className="text-2xl font-bold text-center mb-6">Исследователь аксиом теории чисел</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-1 bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Предустановленные числовые системы</h2>
          <div className="space-y-2">
            {Object.keys(numberSystems).map((system) => (
              <button
                key={system}
                className={`block w-full text-left px-3 py-2 rounded ${numberSystem === system ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
                onClick={() => handlePresetSelect(system)}
              >
                {numberSystems[system].name}
              </button>
            ))}
          </div>
          
          <h2 className="text-xl font-semibold mt-6 mb-4">Выберите аксиомы</h2>
          <div className="space-y-3">
            {Object.keys(axiomDefinitions).map((axiom) => (
              <div key={axiom} className="flex items-start">
                <input
                  type="checkbox"
                  id={axiom}
                  checked={selectedAxioms[axiom]}
                  onChange={() => handleAxiomChange(axiom)}
                  className="mt-1 mr-2"
                />
                <div>
                  <label htmlFor={axiom} className="font-medium cursor-pointer">
                    {axiom.charAt(0).toUpperCase() + axiom.slice(1)}
                  </label>
                  <p className="text-sm text-gray-600">{axiomDefinitions[axiom]}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="col-span-1 md:col-span-2 bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Система: {numberSystems[numberSystem].name}</h2>
          <p className="mb-4">{numberSystems[numberSystem].description}</p>
          
          <h3 className="text-lg font-medium mb-2">Операции:</h3>
          <p className="mb-4">{numberSystems[numberSystem].operations.join(', ')}</p>
          
          <h2 className="text-xl font-semibold mt-6 mb-4">Выводы и свойства</h2>
          {conclusions.length > 0 ? (
            <ul className="list-disc pl-5 space-y-2">
              {conclusions.map((conclusion, index) => (
                <li key={index} className={conclusion.startsWith('Предупреждение') ? 'text-red-600' : 'text-gray-800'}>
                  {conclusion}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">Выберите аксиомы, чтобы увидеть выводы.</p>
          )}
          
          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h3 className="text-lg font-medium mb-2">Информация о текущей системе:</h3>
            <p><strong>Непрерывность:</strong> {selectedAxioms.completeness || selectedAxioms.leastUpperBound ? 'Да' : 'Нет'}</p>
            <p><strong>Дискретность:</strong> {selectedAxioms.peano && !selectedAxioms.completeness ? 'Да' : 'Нет'}</p>
            <p><strong>Алгебраическая структура:</strong> {
              selectedAxioms.closure && selectedAxioms.commutativity && selectedAxioms.associativity && 
              selectedAxioms.distributivity && selectedAxioms.identity && selectedAxioms.inverse ? 
              'Поле' : (selectedAxioms.closure && selectedAxioms.commutativity && selectedAxioms.associativity && 
                      selectedAxioms.distributivity && selectedAxioms.identity ? 'Кольцо' : 'Не определена')
            }</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NumberTheoryAxiomExplorer;
