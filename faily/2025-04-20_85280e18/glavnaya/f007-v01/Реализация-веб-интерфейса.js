// frontend/src/components/ConceptGenerator.js (React)
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:3000/api';

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
      set