// ❌ Было
const philosophersSection = document.querySelector('.legend-section');

// ✅ Должно быть
const philContainer = document.getElementById('philosopherFilters');
if (philContainer) {
    philContainer.addEventListener('click', function(event) {
        if (event.shiftKey && !event.target.closest('.legend-item')) {
            event.preventDefault();
            event.stopPropagation();
            openEditPhilosopherModal();
        }
    });
}