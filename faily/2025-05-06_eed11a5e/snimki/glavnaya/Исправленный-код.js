// 1. Исправление проблемы "store is undefined"
// Необходимо переместить определение store в самое начало скрипта
// Перед определением всех компонентов

// Глобальное хранилище состояния - должно быть определено ПЕРЕД всеми компонентами
const store = Vue.reactive({
    state: {
        currentUser: null,
        currentConcept: null,
        concepts: [],
        categories: [],
        relationships: [],
        theses: [],
        uiState: {
            activeTab: 'dashboard',
            sidebarOpen: true,
            modalStack: [],
            notifications: []
        }
    },
    
    // Мутации состояния
    setCurrentConcept(concept) {
        this.state.currentConcept = concept;
    },
    
    setActiveTab(tab) {
        this.state.uiState.activeTab = tab;
    },
    
    toggleSidebar() {
        this.state.uiState.sidebarOpen = !this.state.uiState.sidebarOpen;
    },
    
    showModal(component, props = {}) {
        const id = Date.now();
        this.state.uiState.modalStack.push({ id, component, props });
        return id;
    },
    
    closeModal(id) {
        this.state.uiState.modalStack = this.state.uiState.modalStack.filter(m => m.id !== id);
    },
    
    showNotification(message, type = 'info') {
        const id = Date.now();
        this.state.uiState.notifications.push({ id, message, type });
        setTimeout(() => {
            this.state.uiState.notifications = this.state.uiState.notifications.filter(n => n.id !== id);
        }, 3000);
    },
    
    // Асинхронные действия
    async loadConcepts() {
        try {
            this.state.concepts = await db.concepts.toArray();
        } catch (error) {
            console.error('Ошибка загрузки концепций:', error);
            this.showNotification('Ошибка загрузки концепций', 'error');
        }
    },
    
    async createConcept(conceptData) {
        try {
            const id = await db.concepts.add({
                ...conceptData,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                isDeleted: false
            });
            await this.loadConcepts();
            this.showNotification('Концепция создана', 'success');
            return id;
        } catch (error) {
            console.error('Ошибка создания концепции:', error);
            this.showNotification('Ошибка создания концепции', 'error');
        }
    }
});

// 2. Исправление проблемы с регистрацией Service Worker
// Проверяем, что мы работаем по HTTPS или на localhost
if ('serviceWorker' in navigator) {
    // Проверяем, что мы используем https:// или http://localhost
    const isSecureContext = window.location.protocol === 'https:' || 
                            window.location.hostname === 'localhost' ||
                            window.location.hostname === '127.0.0.1';
    
    if (isSecureContext) {
        // Регистрируем Service Worker только в безопасном контексте
        navigator.serviceWorker.register('./service-worker.js')
            .then(registration => {
                console.log('Service Worker зарегистрирован:', registration);
            })
            .catch(error => {
                console.error('Ошибка регистрации Service Worker:', error);
            });
    } else {
        console.warn('Service Worker не может быть зарегистрирован: требуется HTTPS или localhost');
    }
}
