// Часть 6: Дополнительные элементы интерфейса и шаблоны экспорта

// === Добавление новых элементов в HTML ===

// Эта функция должна быть вызвана при инициализации
function enhanceUI() {
    // Добавляем панель инструментов для управления графом
    const graphToolbar = `
        <div class="graph-toolbar">
            <button id="undoButton" onclick="handleUndo()" title="Отменить">↩️</button>
            <button id="redoButton" onclick="handleRedo()" title="Повторить">↪️</button>
            <div class="toolbar-separator"></div>
            <button onclick="createConceptVersion()" title="Создать версию">📌</button>
            <button onclick="showVersions()" title="Управление версиями">📚</button>
            <div class="toolbar-separator"></div>
            <button onclick="exportToCSV()" title="Экспорт в CSV">📊</button>
            <button onclick="exportToPDF()" title="Экспорт в PDF">📄</button>
            <button onclick="exportToLatex()" title="Экспорт в LaTeX">📝</button>
        </div>
    `;
    
    // Вставляем панель инструментов перед графом
    const graphContainer = document.getElementById('graphContainer');
    if (graphContainer) {
        graphContainer.insertAdjacentHTML('beforebegin', graphToolbar);
    }
    
    // Добавляем панель управления концепциями
    const conceptPanel = `
        <div class="concept-panel">
            <div class="concept-selector">
                <select id="currentConceptSelect" onchange="selectConcept(this.value)">
                    <option value="">Выберите концепцию</option>
                </select>
                <button onclick="createConcept()" class="create-concept-btn">+</button>
            </div>
            <div id="conceptInfo" class="concept-info" style="display: none;">
                <h3 id="conceptName"></h3>
                <p id="conceptDescription"></p>
                <div class="concept-stats">
                    <span>Категорий: <span id="categoryCount">0</span></span>
                    <span>Связей: <span id="relationCount">0</span></span>
                </div>
                <button onclick="editConceptInfo()" class="edit-btn">Редактировать</button>
            </div>
        </div>
    `;
    
    // Вставляем панель концепций
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        mainContent.insertAdjacentHTML('afterbegin', conceptPanel);
    }
}

// === Дополнительные CSS стили ===

const additionalStyles = `
/* Стили для панели инструментов */
.graph-toolbar {
    display: flex;
    gap: 10px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 5px;
    margin-bottom: 10px;
    align-items: center;
}

.toolbar-separator {
    width: 1px;
    height: 24px;
    background-color: #ddd;
    margin: 0 5px;
}

.graph-toolbar button {
    padding: 5px 10px;
    font-size: 16px;
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.graph-toolbar button:hover {
    background-color: #e8f0fe;
}

.graph-toolbar button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Стили для панели концепций */
.concept-panel {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}

.concept-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.concept-selector select {
    flex: 1;
}

.create-concept-btn {
    width: 40px;
    height: 40px;
    font-size: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.concept-info {
    border-top: 1px solid #eee;
    padding-top: 15px;
}

.concept-stats {
    display: flex;
    gap: 20px;
    margin: 10px 0;
    color: #666;
}

/* Стили для версий */
.versions-list {
    display: grid;
    gap: 15px;
    max-height: 500px;
    overflow-y: auto;
}

.version-item {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
}

.version-item h4 {
    margin: 0 0 10px 0;
    color: var(--primary-color);
}

/* Анимации для SVG графа */
.graph-node-enter {
    animation: nodeEnter 0.5s ease-out;
}

@keyframes nodeEnter {
    from {
        transform: scale(0);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

.graph-link-enter {
    animation: linkEnter 0.5s ease-out;
}

@keyframes linkEnter {
    from {
        stroke-dasharray: 1000;
        stroke-dashoffset: 1000;
    }
    to {
        stroke-dashoffset: 0;
    }
}

/* Стили для экспорта */
.export-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    padding: 20px;
}

.export-option {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
}

.export-option:hover {
    background-color: #f8f9fa;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.export-option i {
    font-size: 32px;
    margin-bottom: 10px;
    color: var(--secondary-color);
}

/* Стили для прогресса */
.progress-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}

.progress-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
}

.progress-bar {
    width: 300px;
    height: 10px;
    background: #eee;
    border-radius: 5px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-bar-fill {
    height: 100%;
    background: var(--secondary-color);
    transition: width 0.3s;
}
`;

// === Функции экспорта ===

// Экспорт в PDF
function exportToPDF() {
    if (!currentConcept) {
        alert('Выберите концепцию для экспорта');
        return;
    }
    
    // Создаем HTML для PDF
    const pdfContent = generatePDFContent();
    
    // Здесь должна быть интеграция с библиотекой для создания PDF
    // Например, jsPDF или html2pdf
    showProgress('Создание PDF...', 100);
    
    setTimeout(() => {
        hideProgress();
        // Симуляция скачивания
        const blob = new Blob([pdfContent], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `concept_${currentConcept.name.replace(/\s+/g, '_')}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
    }, 1500);
}

// Экспорт в LaTeX
function exportToLatex() {
    if (!currentConcept) {
        alert('Выберите концепцию для экспорта');
        return;
    }
    
    const latexContent = generateLatexContent();
    const blob = new Blob([latexContent], { type: 'text/x-tex' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `concept_${currentConcept.name.replace(/\s+/g, '_')}.tex`;
    a.click();
    URL.revokeObjectURL(url);
}

// Генерация содержимого для PDF
function generatePDFContent() {
    const conceptCategories = categories.filter(c => c.conceptId === currentConcept.id);
    const conceptRelations = relations.filter(r => {
        const fromCategory = categories.find(c => c.id === r.from);
        return fromCategory && fromCategory.conceptId === currentConcept.id;
    });
    
    let html = `
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #3498db; }
                .category { margin-bottom: 20px; }
                .relation { margin-left: 20px; }
            </style>
        </head>
        <body>
            <h1>Философская концепция: ${currentConcept.name}</h1>
            <p>Дата создания: ${new Date(currentConcept.createdAt).toLocaleDateString()}</p>
            
            <h2>Категории</h2>
    `;
    
    conceptCategories.forEach(category => {
        html += `
            <div class="category">
                <h3>${category.name}</h3>
                <p><strong>Определение:</strong> ${category.definition}</p>
                <p><strong>Традиции:</strong> ${category.traditions.join(', ')}</p>
                <p><strong>Философы:</strong> ${category.philosophers.join(', ')}</p>
                <p><strong>Метрики:</strong> Центральность: ${category.metrics.centrality}, 
                   Определённость: ${category.metrics.definition}, 
                   Историческая значимость: ${category.metrics.historical}</p>
            </div>
        `;
    });
    
    html += `<h2>Связи</h2>`;
    
    conceptRelations.forEach(relation => {
        const fromCategory = categories.find(c => c.id === relation.from);
        const toCategory = categories.find(c => c.id === relation.to);
        const relationType = relationTypes.find(t => t.id === relation.type);
        
        html += `
            <div class="relation">
                <p>${fromCategory?.name} → ${toCategory?.name}</p>
                <p>Тип: ${relationType?.name}</p>
                <p>${relation.bidirectional ? 'Двунаправленная' : 'Однонаправленная'}</p>
            </div>
        `;
    });
    
    html += `</body></html>`;
    return html;
}

// Генерация LaTeX
function generateLatexContent() {
    const conceptCategories = categories.filter(c => c.conceptId === currentConcept.id);
    const conceptRelations = relations.filter(r => {
        const fromCategory = categories.find(c => c.id === r.from);
        return fromCategory && fromCategory.conceptId === currentConcept.id;
    });
    
    let latex = `\\documentclass[12pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[russian]{babel}
\\usepackage{graphicx}
\\usepackage{tikz}
\\usetikzlibrary{arrows,positioning}

\\title{Философская концепция: ${currentConcept.name}}
\\author{Сервис философских концепций}
\\date{${new Date().toLocaleDateString()}}

\\begin{document}
\\maketitle

\\section{Введение}
Данный документ представляет анализ философской концепции "${currentConcept.name}".

\\section{Категории}
`;
    
    conceptCategories.forEach(category => {
        latex += `
\\subsection{${escapeLatex(category.name)}}
\\textbf{Определение:} ${escapeLatex(category.definition)}\\\\
\\textbf{Традиции:} ${escapeLatex(category.traditions.join(', '))}\\\\
\\textbf{Философы:} ${escapeLatex(category.philosophers.join(', '))}\\\\
\\textbf{Метрики:}
\\begin{itemize}
    \\item Центральность: ${category.metrics.centrality}
    \\item Определённость: ${category.metrics.definition}
    \\item Историческая значимость: ${category.metrics.historical}
\\end{itemize}
`;
    });
    
    latex += `
\\section{Связи}
\\begin{itemize}
`;
    
    conceptRelations.forEach(relation => {
        const fromCategory = categories.find(c => c.id === relation.from);
        const toCategory = categories.find(c => c.id === relation.to);
        const relationType = relationTypes.find(t => t.id === relation.type);
        
        latex += `\\item ${escapeLatex(fromCategory?.name)} $\\rightarrow$ ${escapeLatex(toCategory?.name)} (${escapeLatex(relationType?.name)})
`;
    });
    
    latex += `\\end{itemize}

\\section{Визуализация графа}
\\begin{center}
\\begin{tikzpicture}[node distance=3cm]
`;
    
    // Простая визуализация графа для LaTeX
    conceptCategories.forEach((category, index) => {
        const angle = (index * 360) / conceptCategories.length;
        const radius = 4;
        const x = radius * Math.cos(angle * Math.PI / 180);
        const y = radius * Math.sin(angle * Math.PI / 180);
        
        latex += `\\node[draw,circle] (n${index}) at (${x},${y}) {${escapeLatex(category.name.substring(0, 10))}};
`;
    });
    
    conceptRelations.forEach(relation => {
        const fromIndex = conceptCategories.findIndex(c => c.id === relation.from);
        const toIndex = conceptCategories.findIndex(c => c.id === relation.to);
        
        if (fromIndex !== -1 && toIndex !== -1) {
            latex += `\\draw[->] (n${fromIndex}) -- (n${toIndex});
`;
        }
    });
    
    latex += `\\end{tikzpicture}
\\end{center}

\\end{document}`;
    
    return latex;
}

// Экранирование специальных символов для LaTeX
function escapeLatex(text) {
    if (!text) return '';
    return text
        .replace(/\\/g, '\\textbackslash{}')
        .replace(/[&%$#_{}]/g, '\\$&')
        .replace(/~/g, '\\textasciitilde{}')
        .replace(/\^/g, '\\textasciicircum{}');
}

// === Функции для индикатора прогресса ===

function showProgress(message, percentage) {
    let progressOverlay = document.getElementById('progressOverlay');
    
    if (!progressOverlay) {
        progressOverlay = document.createElement('div');
        progressOverlay.id = 'progressOverlay';
        progressOverlay.className = 'progress-overlay';
        progressOverlay.innerHTML = `
            <div class="progress-content">
                <h3 id="progressMessage">${message}</h3>
                <div class="progress-bar">
                    <div id="progressBarFill" class="progress-bar-fill" style="width: ${percentage}%"></div>
                </div>
                <p id="progressPercentage">${percentage}%</p>
            </div>
        `;
        document.body.appendChild(progressOverlay);
    } else {
        document.getElementById('progressMessage').textContent = message;
        document.getElementById('progressBarFill').style.width = `${percentage}%`;
        document.getElementById('progressPercentage').textContent = `${percentage}%`;
        progressOverlay.style.display = 'flex';
    }
}

function hideProgress() {
    const progressOverlay = document.getElementById('progressOverlay');
    if (progressOverlay) {
        progressOverlay.style.display = 'none';
    }
}

// === Функции для управления концепциями ===

function editConceptInfo() {
    if (!currentConcept) return;
    
    const newName = prompt('Введите новое название концепции:', currentConcept.name);
    const newDescription = prompt('Введите новое описание концепции:', currentConcept.description);
    
    if (newName !== null && newDescription !== null) {
        currentConcept.name = newName;
        currentConcept.description = newDescription;
        saveDatabase();
        updateUI();
        showSuccess('Информация о концепции обновлена');
    }
}

function updateConceptInfo() {
    const conceptInfo = document.getElementById('conceptInfo');
    const conceptName = document.getElementById('conceptName');
    const conceptDescription = document.getElementById('conceptDescription');
    const categoryCount = document.getElementById('categoryCount');
    const relationCount = document.getElementById('relationCount');
    
    if (currentConcept) {
        conceptInfo.style.display = 'block';
        conceptName.textContent = currentConcept.name;
        conceptDescription.textContent = currentConcept.description || 'Описание отсутствует';
        
        const conceptCategories = categories.filter(c => c.conceptId === currentConcept.id);
        const conceptRelations = relations.filter(r => {
            const fromCategory = categories.find(c => c.id === r.from);
            return fromCategory && fromCategory.conceptId === currentConcept.id;
        });
        
        categoryCount.textContent = conceptCategories.length;
        relationCount.textContent = conceptRelations.length;
    } else {
        conceptInfo.style.display = 'none';
    }
}

// === Добавляем стили при инициализации ===

document.addEventListener('DOMContentLoaded', function() {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = additionalStyles;
    document.head.appendChild(styleSheet);
    
    enhanceUI();
});