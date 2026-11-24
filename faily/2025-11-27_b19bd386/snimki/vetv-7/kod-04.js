function openUniversalModal(entityType, data, mode = 'view') {
    // ... генерация контента ...
    
    content.innerHTML = html;
    
    // ✅ ДОБАВИТЬ ЭТО:
    if (mode === 'view') {
        const editButton = document.createElement('button');
        editButton.className = 'mode-switch-btn';
        editButton.innerHTML = '✏️ Редактировать';
        editButton.onclick = () => toggleModalMode();
        content.insertBefore(editButton, content.firstChild);
    }
    
    // ... остальной код ...
}