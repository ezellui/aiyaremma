// Initialize the application
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Initial worker init
initWorker();

// Setup transformed grid
setupTransformedGrid();

// Initial rendering with a slight delay
setTimeout(renderVisualization, 300);