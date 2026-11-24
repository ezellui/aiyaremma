// frontend/src/components/ConceptGenerator.js (React)
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:3000/api';

// Компонент для отображения информации о концепции
const ConceptCard = ({ concept, isSelected, onSelect }) => {
  return (
    <div 
      className={`concept-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(concept.id)}
    >
      <h3>{concept.name}</h3>
      <p>{concept.description}</p>
      <div className="concept-meta">
        <span>Источник: {concept.source}</span>
        {concept.authors && concept.authors.length > 0 && (
          <span>Авторы: {concept.authors.join(', ')}</span>
        )}
      </div>
    </div>
  );
};

export default ConceptGenerator;
};

// Компонент для отображения сгенерированной концепции
const GeneratedConceptView = ({ concept }) => {
  return (
    <div className="generated-concept">
      <h2>{concept.name}</h2>
      <div className="concept-description">
        <h3>Описание</h3>
        <p>{concept.description}</p>
      </div>
      
      <div className="concept-theses">
        <h3>Ключевые тезисы</h3>
        <ul>
          {concept.theses.map((thesis, index) => (
            <li key={thesis.id}>
              <p>{thesis.content}</p>
              {thesis.keywords.length > 0 && (
                <div className="thesis-keywords">
                  Ключевые слова: {thesis.keywords.join(', ')}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      
      <div className="concept-meta">
        <p>Создано: {new Date(concept.creationDate).toLocaleDateString()}</p>
        <p>Автор: {concept.authors.join(', ')}</p>
        <p>Источник: {concept.source}</p>
      </div>
    </div>
  );
};

const ConceptGenerator = () => {
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedConcepts, setSelectedConcepts] = useState([]);
  const [generationParams, setGenerationParams] = useState({
    additionalRequirements: '',
    style: ''
  });
  const [currentRequest, setCurrentRequest] = useState(null);
  const [generatedConcept, setGeneratedConcept] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const [error, setError] = useState(null);

  // Загрузка списка концепций при монтировании компонента
  useEffect(() => {
    fetchConcepts();
  }, []);

  // Опрос статуса запроса, если есть активный запрос
  useEffect(() => {
    if (currentRequest && currentRequest.status === 'processing') {
      const interval = setInterval(() => {
        checkRequestStatus(currentRequest.requestId);
      }, 5000); // Проверяем каждые 5 секунд
      
      setPollingInterval(interval);
      
      return () => clearInterval(interval);
    } else if (pollingInterval && currentRequest && currentRequest.status !== 'processing') {
      clearInterval(pollingInterval);
    }
  }, [currentRequest]);

  // Загрузка списка концепций
  const fetchConcepts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/concepts`);
      setConcepts(response.data);
      setLoading(false);
    } catch (err) {
      setError('Ошибка при загрузке списка концепций');
      setLoading(false);
      console.error(err);
    }
  };
  
  // Рендеринг компонента
  return (
    <div className="concept-generator">
      <h1>Генератор философских концепций</h1>
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Закрыть</button>
        </div>
      )}
      
      {/* Отображение результата генерации */}
      {generatedConcept && (
        <div className="result-section">
          <h2>Сгенерированная концепция</h2>
          <GeneratedConceptView concept={generatedConcept} />
          <button onClick={handleReset}>Создать новую концепцию</button>
        </div>
      )}
      
      {/* Форма генерации */}
      {!generatedConcept && (
        <div className="generation-form">
          <div className="concept-selection">
            <h2>Выберите концепции для комбинирования</h2>
            
            {loading ? (
              <p>Загрузка концепций...</p>
            ) : (
              <div className="concept-grid">
                {concepts.map(concept => (
                  <ConceptCard 
                    key={concept.id}
                    concept={concept}
                    isSelected={selectedConcepts.includes(concept.id)}
                    onSelect={handleConceptSelection}
                  />
                ))}
              </div>
            )}
            
            <div className="selected-count">
              Выбрано концепций: {selectedConcepts.length}
              {selectedConcepts.length < 2 && (
                <p className="selection-hint">Выберите минимум 2 концепции для комбинирования</p>
              )}
            </div>
          </div>
          
          <div className="generation-parameters">
            <h2>Параметры генерации</h2>
            
            <div className="form-group">
              <label htmlFor="additionalRequirements">Дополнительные требования:</label>
              <textarea
                id="additionalRequirements"
                name="additionalRequirements"
                value={generationParams.additionalRequirements}
                onChange={handleParamChange}
                placeholder="Укажите дополнительные требования к генерируемой концепции..."
                rows={4}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="style">Стилистические предпочтения:</label>
              <textarea
                id="style"
                name="style"
                value={generationParams.style}
                onChange={handleParamChange}
                placeholder="Укажите предпочтительный стиль изложения..."
                rows={4}
              />
            </div>
            
            <button 
              onClick={handleGenerateClick} 
              disabled={selectedConcepts.length < 2 || loading || (currentRequest && currentRequest.status === 'processing')}
              className="generate-button"
            >
              {currentRequest && currentRequest.status === 'processing' 
                ? 'Генерация...' 
                : 'Сгенерировать концепцию'}
            </button>
          </div>
          
          {/* Индикатор прогресса */}
          {currentRequest && currentRequest.status === 'processing' && (
            <div className="processing-indicator">
              <p>Идёт генерация новой концепции...</p>
              <div className="progress-bar">
                <div className="progress-animation"></div>
              </div>
              <p>Это может занять несколько минут</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
    }
  };

  // Проверка статуса запроса на генерацию
  const checkRequestStatus = async (requestId) => {
    try {
      const response = await axios.get(`${API_URL}/requests/${requestId}`);
      
      setCurrentRequest({
        ...response.data.request,
        requestId
      });
      
      if (response.data.request.status === 'completed' && response.data.result) {
        setGeneratedConcept(response.data.result);
        clearInterval(pollingInterval);
      } else if (response.data.request.status === 'error') {
        setError(`Ошибка при генерации: ${response.data.request.error || 'Неизвестная ошибка'}`);
        clearInterval(pollingInterval);
      }
    } catch (err) {
      console.error('Ошибка при проверке статуса запроса:', err);
    }
  };

  // Обработка выбора концепции
  const handleConceptSelection = (conceptId) => {
    setSelectedConcepts(prev => {
      // Если концепция уже выбрана, удаляем её
      if (prev.includes(conceptId)) {
        return prev.filter(id => id !== conceptId);
      } else {
        // Иначе добавляем
        return [...prev, conceptId];
      }
    });
  };
  
  // Сброс текущего состояния генерации
  const handleReset = () => {
    setSelectedConcepts([]);
    setGenerationParams({
      additionalRequirements: '',
      style: ''
    });
    setCurrentRequest(null);
    setGeneratedConcept(null);
    setError(null);
  };

  // Обработка изменения параметров генерации
  const handleParamChange = (e) => {
    const { name, value } = e.target;
    setGenerationParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Отправка запроса на генерацию
  const handleGenerateClick = async () => {
    if (selectedConcepts.length < 2) {
      setError('Выберите не менее двух концепций для комбинирования');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post(`${API_URL}/generate`, {
        selectedConcepts,
        generationParams,
        userId: 'user-123' // В реальном приложении ID пользователя из системы аутентификации
      });
      
      setCurrentRequest({
        requestId: response.data.requestId,
        status: 'processing'
      });
      
      setLoading(false);
    } catch (err) {
      setError('Ошибка при отправке запроса на генерацию');
      setLoading(false);
      console.error(err);