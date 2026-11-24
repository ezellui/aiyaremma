// Определяем, является ли это существующей сущностью
let isExistingEntity = false;

switch(entityType) {
    case 'philosopher':
        // Философ существует, если передано имя (строка)
        isExistingEntity = data && typeof data === 'string' && data.length > 0;
        break;
    case 'concept':
        // Концепция существует, если есть id
        isExistingEntity = data && data.id;
        break;
    case 'connection':
        // Связь существует, если есть source и target
        isExistingEntity = data && (data.source || data.from) && (data.target || data.to);
        break;
}

// Добавляем кнопку
if (isExistingEntity) {
    html = `<button class="mode-switch-btn" onclick="toggleModalMode()">...</button>` + html;
}