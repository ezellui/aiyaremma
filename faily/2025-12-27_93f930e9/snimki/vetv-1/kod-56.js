/**
 * Главный роутер API Gateway
 */

const express = require('express');
const router = express.Router();

// Импортируем роуты
const authRoutes = require('./auth');
const conceptRoutes = require('./concepts');
const graphRoutes = require('./graphs');
const thesisRoutes = require('./theses');
const synthesisRoutes = require('./synthesis');
const claudeRoutes = require('./claude');
const nameAnalysisRoutes = require('./name-analysis');
const originRoutes = require('./origin');
const historicalRoutes = require('./historical');
const practicalRoutes = require('./practical');
const dialogueRoutes = require('./dialogue');
const evolutionRoutes = require('./evolution');

// Базовый маршрут
router.get('/', (req, res) => {
  res.json({
    message: 'Philosophy Concepts API Gateway',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      concepts: '/api/concepts',
      graphs: '/api/graphs',
      theses: '/api/theses',
      synthesis: '/api/synthesis',
      claude: '/api/claude',
      nameAnalysis: '/api/name-analysis',
      origin: '/api/origin',
      historical: '/api/historical',
      practical: '/api/practical',
      dialogue: '/api/dialogue',
      evolution: '/api/evolution'
    }
  });
});

// Подключаем роуты
router.use('/auth', authRoutes);
router.use('/concepts', conceptRoutes);
router.use('/graphs', graphRoutes);
router.use('/theses', thesisRoutes);
router.use('/synthesis', synthesisRoutes);
router.use('/claude', claudeRoutes);
router.use('/name-analysis', nameAnalysisRoutes);
router.use('/origin', originRoutes);
router.use('/historical', historicalRoutes);
router.use('/practical', practicalRoutes);
router.use('/dialogue', dialogueRoutes);
router.use('/evolution', evolutionRoutes);

module.exports = router;