/**
 * Главный роутер API Gateway
 */

const express = require('express');
const router = express.Router();

const authRoutes = require('./auth');
const usersRoutes = require('./users');
const conceptsRoutes = require('./concepts');
const graphsRoutes = require('./graphs');
const thesesRoutes = require('./theses');
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
    message: 'Philosophy Concept Platform API Gateway',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      users: '/api/users',
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

// Подключение маршрутов
router.use('/auth', authRoutes);
router.use('/users', usersRoutes);
router.use('/concepts', conceptsRoutes);
router.use('/graphs', graphsRoutes);
router.use('/theses', thesesRoutes);
router.use('/synthesis', synthesisRoutes);
router.use('/claude', claudeRoutes);
router.use('/name-analysis', nameAnalysisRoutes);
router.use('/origin', originRoutes);
router.use('/historical', historicalRoutes);
router.use('/practical', practicalRoutes);
router.use('/dialogue', dialogueRoutes);
router.use('/evolution', evolutionRoutes);

module.exports = router;