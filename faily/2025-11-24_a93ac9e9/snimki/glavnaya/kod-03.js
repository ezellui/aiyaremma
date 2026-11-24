node.on("click", function(event, d) {
    event.stopPropagation();
    
    // ========== ДОБАВИТЬ В САМОЕ НАЧАЛО ==========
    if (event.shiftKey) {
        if (editMode.graphSelectionMode) {
            handleConceptSelection(d.id);
            return;
        } else if (editMode.pendingConceptSelection.length > 0) {
            const firstConceptId = editMode.pendingConceptSelection[0];
            if (firstConceptId === d.id) {
                // Повторный shift+клик - редактирование
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConceptModal(d.id);
            } else {
                // Клик на другом узле - создание связи
                editMode.pendingConceptSelection = [];
                node.classed('selected', false);
                openEditConnectionModal(firstConceptId, d.id);
            }
            return;
        } else {
            // Первый shift+клик - запоминаем узел
            editMode.pendingConceptSelection = [d.id];
            node.classed('selected', n => n.id === d.id);
            return;
        }
    }
    
    // Отменяем выбор при обычном клике
    if (editMode.pendingConceptSelection.length > 0) {
        editMode.pendingConceptSelection = [];
        node.classed('selected', false);
    }
    // ========== КОНЕЦ ДОБАВЛЕНИЯ ==========
    
    clickCount++;  // Дальше идет существующий код