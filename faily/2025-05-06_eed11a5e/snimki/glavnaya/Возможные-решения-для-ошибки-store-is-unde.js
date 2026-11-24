// ВАРИАНТ 1: Компонентный подход - передача store через props
// Модифицируйте компонент Sidebar

const Sidebar = {
    props: {
        store: Object // Явно объявляем store как prop
    },
    template: `...`,
    methods: {
        navigateTo(tab) {
            this.store.setActiveTab(tab); // Используем this.store вместо глобального store
        },
        // ... другие методы
    }
};

// При регистрации компонента в Vue:
app.component('sidebar', Sidebar);

// В шаблоне App:
// <sidebar :store="store"></sidebar>

// ВАРИАНТ 2: Использование provide/inject в Vue 3
// В компоненте App:
const App = {
    // ...
    setup() {
        // Предоставляем store всем дочерним компонентам
        Vue.provide('store', store);
        return { store };
    }
};

// В других компонентах:
const Sidebar = {
    // ...
    setup() {
        // Инжектируем store
        const store = Vue.inject('store');
        return { store };
    },
    methods: {
        navigateTo(tab) {
            this.store.setActiveTab(tab);
        }
    }
};

// ВАРИАНТ 3: Проверка на undefined и асинхронную инициализацию
// Проверяем, что store существует перед использованием
methods: {
    navigateTo(tab) {
        if (store) {
            store.setActiveTab(tab);
        } else {
            console.error('Store не инициализирован');
        }
    }
}

// ВАРИАНТ 4: Убедитесь, что Vue.reactive доступен
// Иногда проблема в том, что Vue ещё не полностью инициализирован
// Проверяем, что Vue.reactive доступен:
const store = typeof Vue !== 'undefined' && Vue.reactive ? Vue.reactive({
    // ... содержимое store
}) : {};

// ВАРИАНТ 5: Использование Event Bus для снижения зависимости от store
// Создаем простую шину событий
const eventBus = new Vue();

// В компонентах вместо store.setActiveTab используем:
eventBus.$emit('change-tab', tabName);

// И подписываемся:
eventBus.$on('change-tab', (tabName) => {
    // Обработка
});