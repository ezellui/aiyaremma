// ============================================
// Создаём объект linkColors для быстрого доступа к цветам связей
// Используется в функции visualizeMetricBySize() для цвета стрелок
// ============================================
const linkColors = {};
relationTypes.forEach(rt => {
    linkColors[rt.id] = rt.color;
});

console.log('✅ Цвета связей загружены:', Object.keys(linkColors).length, 'типов');