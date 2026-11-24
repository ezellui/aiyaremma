function swapConnectionConcepts() {
    const sourceInput = document.getElementById('connectionSourceSearch');
    const targetInput = document.getElementById('connectionTargetSearch');
    
    // Меняем значения полей
    const tempValue = sourceInput.value;
    sourceInput.value = targetInput.value;
    targetInput.value = tempValue;
    
    // Меняем ID концепций
    const tempId = editMode.connectionSourceId;
    editMode.connectionSourceId = editMode.connectionTargetId;
    editMode.connectionTargetId = tempId;
}