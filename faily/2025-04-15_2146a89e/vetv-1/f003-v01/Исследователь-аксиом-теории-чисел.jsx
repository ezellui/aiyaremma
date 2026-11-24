import React, { useState, useEffect } from 'react';
import { AlertCircle, Check, ChevronDown, Info } from 'lucide-react';

const NumberTheoryExplorer = () => {
  // Состояние аксиом
  const [axioms, setAxioms] = useState({
    peano: {
      successor: true,
      induction: true,
      noLoops: true,
    },
    algebraic: {
      commutativity: true,
      associativity: true,
      distributivity: true,
      identity: true,
      inverse: true,
    },
    ordering: {
      transitivity: true,
      trichotomy: true,
      wellOrdering: true,
      archimedean: true,
    },
    completeness: {
      supremum: false,
      cauchyConvergence: false,
      dedekindCuts: false,
    }
  });

  // Состояние открытых/закрытых групп аксиом
  const [openGroups, setOpenGroups] = useState({
    peano: true,
    algebraic: true,
    ordering: true,
    completeness: true,
  });

  // Математические множества, которые могут быть сконструированы с данными аксиомами
  const [numberSets, setNumberSets] = useState({
    naturals: true,
    integers: false,
    rationals: false,
    reals: false,
    complex: false,
  });

  // Математические свойства, вытекающие из выбранных аксиом
  const [properties, setProperties] = useState({
    divisibility: false,
    primality: false,
    countability: true,
    density: false,
    completeness: false,
    algebraicClosure: false,
  });

  // Примеры теорем, которые можно доказать или опровергнуть
  const [theorems, setTheorems] = useState({
    infinitePrimes: false,
    fundamentalTheoremArithmetic: false,
    irrationality: false,
    transcendence: false,
    cantorUncountability: false,
  });

  // Переключатель для группы аксиом
  const toggleGroup = (group) => {
    setOpenGroups({
      ...openGroups,
      [group]: !openGroups[group]
    });
  };

  // Переключатель для конкретной аксиомы
  const toggleAxiom = (group, axiom) => {
    setAxioms({
      ...axioms,
      [group]: {
        ...axioms[group],
        [axiom]: !axioms[group][axiom]
      }
    });
  };

  // Обновление свойств чисел в зависимости от выбранных аксиом
  useEffect(() => {
    // Определяем, какие числовые множества можно построить
    const newNumberSets = {
      naturals: axioms.peano.successor && axioms.peano.noLoops,
      integers: axioms.peano.successor && axioms.peano.noLoops && axioms.algebraic.inverse,
      rationals: axioms.peano.successor && axioms.peano.noLoops && axioms.algebraic.inverse && 
                axioms.algebraic.distributivity,
      reals: axioms.peano.successor && axioms.peano.noLoops && axioms.algebraic.inverse && 
             axioms.algebraic.distributivity && (axioms.completeness.supremum || 
             axioms.completeness.cauchyConvergence || axioms.completeness.dedekindCuts),
      complex: axioms.peano.successor && axioms.peano.noLoops && axioms.algebraic.inverse && 
               axioms.algebraic.distributivity && (axioms.completeness.supremum || 
               axioms.completeness.cauchyConvergence || axioms.completeness.dedekindCuts)
    };

    // Определяем свойства, вытекающие из аксиом
    const newProperties = {
      divisibility: axioms.peano.successor && axioms.peano.noLoops,
      primality: axioms.peano.successor && axioms.peano.noLoops,
      countability: true, // Начальное значение, изменится ниже
      density: axioms.ordering.archimedean && 
              (newNumberSets.rationals || newNumberSets.reals),
      completeness: axioms.completeness.supremum || axioms.completeness.cauchyConvergence || 
                   axioms.completeness.dedekindCuts,
      algebraicClosure: newNumberSets.complex,
    };

    // Определяем, какие множества счётны
    if (newNumberSets.reals && axioms.completeness.supremum) {
      newProperties.countability = false; // Вещественные числа несчётны
    } else {
      newProperties.countability = true;  // Остальные множества счётны
    }

    // Определяем, какие теоремы можно доказать
    const newTheorems = {
      infinitePrimes: axioms.peano.induction && newNumberSets.naturals,
      fundamentalTheoremArithmetic: axioms.peano.induction && newNumberSets.naturals,
      irrationality: newNumberSets.reals && !newNumberSets.rationals,
      transcendence: newNumberSets.reals,
      cantorUncountability: newNumberSets.reals && axioms.completeness.supremum,
    };

    setNumberSets(newNumberSets);
    setProperties(newProperties);
    setTheorems(newTheorems);
  }, [axioms]);

  // Описания аксиом
  const axiomDescriptions = {
    peano: {
      successor: "Каждое натуральное число имеет единственного преемника",
      induction: "Принцип математической индукции: если утверждение верно для 0 и из верности для n следует верность для n+1, то оно верно для всех натуральных чисел",
      noLoops: "Никакое число не является своим преемником (нет циклов)"
    },
    algebraic: {
      commutativity: "a + b = b + a и a × b = b × a",
      associativity: "(a + b) + c = a + (b + c) и (a × b) × c = a × (b × c)",
      distributivity: "a × (b + c) = a × b + a × c",
      identity: "Существуют числа 0 и 1: a + 0 = a и a × 1 = a",
      inverse: "Для каждого числа a существует противоположное -a: a + (-a) = 0"
    },
    ordering: {
      transitivity: "Если a < b и b < c, то a < c",
      trichotomy: "Для любых a и b верно только одно: a < b, a = b или a > b",
      wellOrdering: "Любое непустое подмножество натуральных чисел имеет наименьший элемент",
      archimedean: "Для любых a > 0 и b существует натуральное n такое, что n×a > b"
    },
    completeness: {
      supremum: "Любое непустое ограниченное сверху подмножество имеет точную верхнюю грань",
      cauchyConvergence: "Любая последовательность Коши сходится",
      dedekindCuts: "Любое сечение Дедекинда определяет число"
    }
  };

  // Группы аксиом с названиями на русском
  const groupNames = {
    peano: "Аксиомы Пеано",
    algebraic: "Алгебраические аксиомы",
    ordering: "Аксиомы порядка",
    completeness: "Аксиомы полноты"
  };

  // Описания числовых множеств
  const numberSetDescriptions = {
    naturals: "Натуральные числа (ℕ)",
    integers: "Целые числа (ℤ)",
    rationals: "Рациональные числа (ℚ)",
    reals: "Вещественные числа (ℝ)",
    complex: "Комплексные числа (ℂ)"
  };

  // Описания свойств
  const propertyDescriptions = {
    divisibility: "Делимость чисел и теория делимости",
    primality: "Понятие простого числа",
    countability: "Счётность множества",
    density: "Плотность (между любыми двумя числами есть ещё одно)",
    completeness: "Полнота (отсутствие «дырок» в числовой прямой)",
    algebraicClosure: "Алгебраическая замкнутость (все многочлены имеют корни)"
  };

  // Описания теорем
  const theoremDescriptions = {
    infinitePrimes: "Теорема о бесконечности простых чисел",
    fundamentalTheoremArithmetic: "Основная теорема арифметики (о единственности разложения на простые множители)",
    irrationality: "Существование иррациональных чисел (например, √2)",
    transcendence: "Существование трансцендентных чисел (например, π, e)",
    cantorUncountability: "Теорема Кантора о несчётности множества вещественных чисел"
  };

  return (
    <div className="p-4 max-w-4xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">Исследователь аксиом теории чисел</h1>
      <p className="mb-6 text-gray-700">
        Выберите аксиомы, чтобы увидеть, какие числовые множества можно построить и какие свойства они будут иметь.
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Левая колонка: выбор аксиом */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Аксиомы</h2>
          
          {/* Аксиомы по группам */}
          {Object.keys(groupNames).map(groupKey => (
            <div key={groupKey} className="mb-4 border rounded-lg">
              <button 
                className="w-full p-3 text-left font-medium flex justify-between items-center bg-gray-50 rounded-t-lg"
                onClick={() => toggleGroup(groupKey)}
              >
                {groupNames[groupKey]}
                <ChevronDown 
                  className={`transform duration-200 ${openGroups[groupKey] ? 'rotate-180' : ''}`} 
                  size={20} 
                />
              </button>
              
              {openGroups[groupKey] && (
                <div className="p-3 space-y-2">
                  {Object.keys(axioms[groupKey]).map(axiomKey => (
                    <div key={axiomKey} className="flex items-start gap-2">
                      <div className="pt-0.5">
                        <button 
                          className={`w-5 h-5 rounded flex items-center justify-center border ${
                            axioms[groupKey][axiomKey] 
                              ? 'bg-blue-500 text-white border-blue-500' 
                              : 'border-gray-300'
                          }`}
                          onClick={() => toggleAxiom(groupKey, axiomKey)}
                        >
                          {axioms[groupKey][axiomKey] && <Check size={14} />}
                        </button>
                      </div>
                      <div>
                        <label className="cursor-pointer" onClick={() => toggleAxiom(groupKey, axiomKey)}>
                          <span className="font-medium">{axiomKey.charAt(0).toUpperCase() + axiomKey.slice(1)}</span>
                        </label>
                        <p className="text-sm text-gray-600 mt-0.5">
                          {axiomDescriptions[groupKey][axiomKey]}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Правая колонка: результаты */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Следствия выбранных аксиом</h2>
          
          {/* Числовые множества */}
          <div className="mb-6 border rounded-lg">
            <div className="bg-gray-50 p-3 rounded-t-lg font-medium">
              Числовые множества
            </div>
            <div className="p-3">
              {Object.keys(numberSets).map(setKey => (
                <div key={setKey} className="flex items-center gap-2 mb-2">
                  {numberSets[setKey] ? (
                    <Check size={18} className="text-green-500" />
                  ) : (
                    <AlertCircle size={18} className="text-red-400" />
                  )}
                  <div>
                    <span className={numberSets[setKey] ? 'font-medium' : 'text-gray-500'}>
                      {numberSetDescriptions[setKey]}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Свойства */}
          <div className="mb-6 border rounded-lg">
            <div className="bg-gray-50 p-3 rounded-t-lg font-medium">
              Математические свойства
            </div>
            <div className="p-3">
              {Object.keys(properties).map(propKey => (
                <div key={propKey} className="flex items-center gap-2 mb-2">
                  {properties[propKey] ? (
                    <Check size={18} className="text-green-500" />
                  ) : (
                    <AlertCircle size={18} className="text-red-400" />
                  )}
                  <div>
                    <span className={properties[propKey] ? 'font-medium' : 'text-gray-500'}>
                      {propertyDescriptions[propKey]}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Теоремы */}
          <div className="mb-6 border rounded-lg">
            <div className="bg-gray-50 p-3 rounded-t-lg font-medium">
              Доказуемые теоремы
            </div>
            <div className="p-3">
              {Object.keys(theorems).map(theoremKey => (
                <div key={theoremKey} className="flex items-center gap-2 mb-2">
                  {theorems[theoremKey] ? (
                    <Check size={18} className="text-green-500" />
                  ) : (
                    <AlertCircle size={18} className="text-red-400" />
                  )}
                  <div>
                    <span className={theorems[theoremKey] ? 'font-medium' : 'text-gray-500'}>
                      {theoremDescriptions[theoremKey]}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Дополнительная информация */}
          <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg flex items-start gap-2">
            <Info size={20} className="text-blue-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p>Выбирайте или отключайте различные аксиомы, чтобы увидеть, как они влияют на свойства чисел и теоремы, которые можно доказать в рамках получившейся аксиоматической системы.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NumberTheoryExplorer;