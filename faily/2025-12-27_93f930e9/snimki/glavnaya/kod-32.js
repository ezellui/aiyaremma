/**
 * Обертка для async/await в Express route handlers
 * Автоматически передает ошибки в next()
 */

function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = asyncHandler;