switchTab(tabName, event) {  // ✅ Добавлен параметр event
    // ...
    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
    }
    
    if (event && event.target) {  // ✅ Проверка существования
        event.target.classList.add('active');
    }
    // ...
}