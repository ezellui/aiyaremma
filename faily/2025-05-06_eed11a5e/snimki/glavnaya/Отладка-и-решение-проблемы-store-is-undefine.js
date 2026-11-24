// 1. Добавьте в начало скрипта отладочный код для проверки порядка инициализации
console.log('Vue доступен:', typeof Vue !== 'undefined');

// 2. Проверьте порядок выполнения кода
console.log('Начало скрипта');

// Добавьте после объявления store:
const store = Vue.reactive({
    // ... существующий код ...
});
console.log('Store инициализирован:', store);

// 3. В компоненте Sidebar (или том, где возникает ошибка)
const Sidebar = {
    // ... существующий код ...
    mounted() {
        console.log('Sidebar mounted, store доступен:', typeof store !== 'undefined');
        
        // Существующий код...
        lucide.createIcons();
    },
    // ... остальной код ...
};

// 4. Проблема может быть в обращении к store из шаблона компонента
// Исправление: используйте функции вместо прямого обращения к store
// Например, в шаблоне вместо:
// v-for="concept in store.state.concepts"
// Используйте:
// v-for="concept in getConcepts()"

// Добавьте в компонент метод:
methods: {
    getConcepts() {
        return store?.state?.concepts || [];
    }
}

// 5. Возможное решение - глобальный миксин для всех компонентов
const app = Vue.createApp(App);

// Добавьте глобальный миксин перед регистрацией компонентов:
app.mixin({
    data() {
        return {
            globalStore: store
        };
    }
});

// Затем в шаблонах используйте globalStore вместо store:
// v-for="concept in globalStore.state.concepts"

// 6. Если проблема возникает при использовании _renderList,
// это может быть связано с тем, как Vue компилирует шаблоны.
// Используйте computed свойства:

computed: {
    conceptsList() {
        return store?.state?.concepts || [];
    }
}

// И затем в шаблоне:
// v-for="concept in conceptsList"

// 7. Добавьте проверку перед монтированием приложения:
// В самом конце файла перед app.mount('#app')
if (typeof store === 'undefined') {
    console.error('КРИТИЧЕСКАЯ ОШИБКА: store не определен перед монтированием приложения');
} else {
    console.log('Store готов к использованию при монтировании');
    app.mount('#app');
}