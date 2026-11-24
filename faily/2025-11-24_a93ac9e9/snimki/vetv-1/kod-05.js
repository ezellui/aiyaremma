function cancelGraphSelection() {
    editMode.graphSelectionMode = false;
    editMode.graphSelectionTarget = null;
    
    const modal = document.getElementById('editConnectionModal');
    const overlay = document.getElementById('modalOverlay');
    
    document.getElementById('graphSelectionMode').style.display = 'none';
    modal.style.display = 'block';
    overlay.classList.add('show');
}