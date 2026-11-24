#!/usr/bin/env node

/**
 * Универсальный скрипт проверки обработки философских связей
 * 
 * Использование:
 *   node check_relations_universal.js <исходный_файл> <обработанный_файл>
 * 
 * Пример:
 *   node check_relations_universal.js original.js processed.js
 */

const fs = require('fs');
const path = require('path');

// Проверка аргументов
if (process.argv.length < 4) {
    console.error('Ошибка: Недостаточно аргументов');
    console.error('');
    console.error('Использование:');
    console.error('  node check_relations_universal.js <исходный_файл> <обработанный_файл>');
    console.error('');
    console.error('Пример:');
    console.error('  node check_relations_universal.js /path/to/original.js /path/to/processed.js');
    process.exit(1);
}

const originalFile = process.argv[2];
const processedFile = process.argv[3];

// Проверка существования файлов
if (!fs.existsSync(originalFile)) {
    console.error(`❌ Исходный файл не найден: ${originalFile}`);
    process.exit(1);
}

if (!fs.existsSync(processedFile)) {
    console.error(`❌ Обработанный файл не найден: ${processedFile}`);
    process.exit(1);
}

console.log('=== УНИВЕРСАЛЬНАЯ ПРОВЕРКА ОБРАБОТКИ СВЯЗЕЙ ===\n');
console.log(`Исходный файл: ${originalFile}`);
console.log(`Обработанный файл: ${processedFile}\n`);

// Функция извлечения массива relations из файла
function extractRelations(filepath) {
    try {
        const content = fs.readFileSync(filepath, 'utf8');
        
        // Проверяем, является ли файл JS модулем с массивом relations
        if (!content.includes('relations')) {
            throw new Error('Файл не содержит массив relations');
        }
        
        // Извлекаем массив relations
        const relations = eval(content.replace(/const relations\s*=\s*/, '').replace(/;?\s*$/, ''));
        
        if (!Array.isArray(relations)) {
            throw new Error('relations не является массивом');
        }
        
        return relations;
    } catch (error) {
        console.error(`❌ Ошибка при чтении файла ${filepath}:`);
        console.error(`   ${error.message}`);
        process.exit(1);
    }
}

try {
    const originalRelations = extractRelations(originalFile);
    const processedRelations = extractRelations(processedFile);

    console.log(`Количество связей:`);
    console.log(`  Исходный файл: ${originalRelations.length}`);
    console.log(`  Обработанный файл: ${processedRelations.length}\n`);

    // ПРОВЕРКА 1: Полнота обработки
    console.log('=== ПРОВЕРКА 1: Полнота обработки ===');
    
    if (originalRelations.length !== processedRelations.length) {
        console.log(`❌ ОШИБКА: Количество связей не совпадает!`);
        console.log(`   Исходных: ${originalRelations.length}`);
        console.log(`   Обработанных: ${processedRelations.length}`);
        console.log(`   Разница: ${Math.abs(originalRelations.length - processedRelations.length)}`);
    } else {
        console.log(`✓ Количество связей совпадает: ${processedRelations.length}`);
    }

    // Создаём карту для быстрого поиска
    const processedMap = new Map();
    processedRelations.forEach((rel, index) => {
        const key = `${rel.source}|${rel.target}|${rel.type}`;
        processedMap.set(key, { relation: rel, index });
    });

    let missingRelations = [];
    originalRelations.forEach((origRel, index) => {
        const key = `${origRel.source}|${origRel.target}|${origRel.type}`;
        if (!processedMap.has(key)) {
            missingRelations.push({ index, relation: origRel });
        }
    });

    if (missingRelations.length > 0) {
        console.log(`\n❌ Не обработано связей: ${missingRelations.length}`);
        missingRelations.forEach(({ index, relation }) => {
            console.log(`   [${index}] ${relation.source} -> ${relation.target} (${relation.type})`);
        });
    } else {
        console.log(`✓ Все связи присутствуют в обработанном файле`);
    }

    // ПРОВЕРКА 2: Сохранность полей
    console.log('\n=== ПРОВЕРКА 2: Сохранность исходных полей ===');
    
    let changedFields = [];
    let missingDescriptions = [];
    let extraFields = [];

    originalRelations.forEach((origRel, index) => {
        const key = `${origRel.source}|${origRel.target}|${origRel.type}`;
        const processed = processedMap.get(key);
        
        if (!processed) return; // Уже отмечено в проверке 1

        const procRel = processed.relation;
        const origFields = Object.keys(origRel);
        const procFields = Object.keys(procRel);

        // Проверяем каждое поле из оригинала
        for (let field of origFields) {
            if (origRel[field] !== procRel[field]) {
                changedFields.push({
                    index,
                    field,
                    relation: `${origRel.source} -> ${origRel.target}`,
                    original: origRel[field],
                    processed: procRel[field]
                });
            }
        }

        // Проверяем наличие description
        if (!procRel.description) {
            missingDescriptions.push({
                index,
                relation: `${origRel.source} -> ${origRel.target} (${origRel.type})`
            });
        }

        // Проверяем, нет ли лишних полей (кроме description)
        for (let field of procFields) {
            if (field !== 'description' && !origFields.includes(field)) {
                extraFields.push({
                    index,
                    field,
                    relation: `${origRel.source} -> ${origRel.target}`
                });
            }
        }
    });

    if (changedFields.length > 0) {
        console.log(`\n❌ Изменены исходные поля в ${changedFields.length} связях:`);
        changedFields.forEach(({ index, field, relation, original, processed }) => {
            console.log(`   [${index}] ${relation}`);
            console.log(`      Поле: ${field}`);
            console.log(`      Было: ${JSON.stringify(original)}`);
            console.log(`      Стало: ${JSON.stringify(processed)}`);
        });
    } else {
        console.log(`✓ Все исходные поля сохранены без изменений`);
    }

    if (missingDescriptions.length > 0) {
        console.log(`\n❌ Отсутствует поле description в ${missingDescriptions.length} связях:`);
        missingDescriptions.forEach(({ index, relation }) => {
            console.log(`   [${index}] ${relation}`);
        });
    } else {
        console.log(`✓ Поле description добавлено во все связи`);
    }

    if (extraFields.length > 0) {
        console.log(`\n⚠️  Добавлены дополнительные поля (кроме description) в ${extraFields.length} связях:`);
        extraFields.forEach(({ index, field, relation }) => {
            console.log(`   [${index}] ${relation} - поле: ${field}`);
        });
    } else {
        console.log(`✓ Не добавлено лишних полей (только description)`);
    }

    // ИТОГОВАЯ СВОДКА
    console.log('\n=== ИТОГОВАЯ СВОДКА ===');
    const allChecksPass = 
        originalRelations.length === processedRelations.length &&
        missingRelations.length === 0 &&
        changedFields.length === 0 &&
        missingDescriptions.length === 0 &&
        extraFields.length === 0;

    if (allChecksPass) {
        console.log('✓✓✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО ✓✓✓');
        console.log(`   • Обработано связей: ${processedRelations.length}`);
        console.log(`   • Исходные поля: сохранены`);
        console.log(`   • Поле description: добавлено`);
    } else {
        console.log('❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ:');
        if (originalRelations.length !== processedRelations.length) {
            console.log(`   • Количество связей не совпадает`);
        }
        if (missingRelations.length > 0) {
            console.log(`   • Не обработано связей: ${missingRelations.length}`);
        }
        if (changedFields.length > 0) {
            console.log(`   • Изменено исходных полей: ${changedFields.length}`);
        }
        if (missingDescriptions.length > 0) {
            console.log(`   • Отсутствует description: ${missingDescriptions.length}`);
        }
        if (extraFields.length > 0) {
            console.log(`   • Добавлено лишних полей: ${extraFields.length}`);
        }
    }

    console.log('\n=== ПРОВЕРКА ЗАВЕРШЕНА ===');
    process.exit(allChecksPass ? 0 : 1);

} catch (error) {
    console.error('❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ВЫПОЛНЕНИИ ПРОВЕРКИ:');
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
}
