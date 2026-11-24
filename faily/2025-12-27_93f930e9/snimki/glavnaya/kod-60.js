/**
 * Пример маршрутов
 */

const express = require('express');
const router = express.Router();
const { asyncHandler } = require('@philos/shared');
const { validateBody, validateParams } = require('../middleware/validate');
const Joi = require('joi');

// Пример контроллера (нужно будет создать)
// const ExampleController = require('../controllers/example.controller');
// const controller = new ExampleController();

// Схемы валидации
const createSchema = Joi.object({
  name: Joi.string().required(),
  description: Joi.string().optional()
});

const updateSchema = Joi.object({
  name: Joi.string().optional(),
  description: Joi.string().optional()
});

const idSchema = Joi.object({
  id: Joi.string().uuid().required()
});

// Маршруты
// router.get('/', asyncHandler(controller.getAll.bind(controller)));
// router.get('/:id', validateParams(idSchema), asyncHandler(controller.getById.bind(controller)));
// router.post('/', validateBody(createSchema), asyncHandler(controller.create.bind(controller)));
// router.put('/:id', validateParams(idSchema), validateBody(updateSchema), asyncHandler(controller.update.bind(controller)));
// router.delete('/:id', validateParams(idSchema), asyncHandler(controller.delete.bind(controller)));

module.exports = router;