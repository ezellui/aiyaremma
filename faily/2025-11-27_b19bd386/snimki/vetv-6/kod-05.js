function openUniversalModal(entityType, data, mode = 'view') {
    // ... существующий код ...
    
    const modeToggleBtn = document.getElementById('modeToggleBtn');
    
    content.innerHTML = html;
    
    // ✅ Управление кнопкой
    if (modeToggleBtn) {
        if (mode === 'view') {
            modeToggleBtn.style.display = 'block';
            
            // Текст в зависимости от типа
            if (entityType === 'philosopher') {
                modeToggleBtn.innerHTML = '✏️ Редактировать философа';
            } else if (entityType === 'concept') {
                modeToggleBtn.innerHTML = '✏️ Редактировать концепцию';
            } else if (entityType === 'connection') {
                modeToggleBtn.innerHTML = '✏️ Редактировать связь';
            }
        } else {
            modeToggleBtn.style.display = 'none';
        }
    }
    
    // ... остальной код ...
}