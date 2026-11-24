// Скрипт проверки корректности обработки второй порции связей

const fs = require('fs');

console.log('=== ПРОВЕРКА ОБРАБОТКИ СВЯЗЕЙ (ПОРЦИЯ 2) ===\n');

// Исходные связи из документа пользователя
const originalRelations = [
    // ФОМА
    { source: "actual_being", target: "essence_existence", type: "consequence", weight: 2 },
    { source: "accidents", target: "essence_existence", type: "consequence", weight: 2 },
    { source: "analogy", target: "essence_existence", type: "consequence", weight: 2 },
    { source: "analogy", target: "real_distinction", type: "consequence", weight: 2 },
    { source: "natural_law", target: "five_ways", type: "consequence", weight: 2 },
    { source: "intellectualism", target: "five_ways", type: "consequence", weight: 2 },
    { source: "real_distinction", target: "actual_being", type: "consequence", weight: 3 },
    { source: "thomistic_synthesis", target: "essence_existence", type: "consequence", weight: 2 },
    { source: "participatio", target: "analogy", type: "consequence", weight: 2 },
    { source: "intellectualism", target: "natural_law", type: "presuppose", weight: 3 },
    { source: "real_distinction", target: "essence_existence", type: "presuppose", weight: 3 },
    { source: "thomistic_synthesis", target: "intellectualism", type: "presuppose", weight: 2 },
    { source: "essence_existence", target: "five_ways", type: "presuppose", weight: 3 },
    { source: "natural_law", target: "thomistic_synthesis", type: "apply", weight: 2 },
    { source: "intellectualism", target: "essence_existence", type: "condition", weight: 2 },
    { source: "real_distinction", target: "participatio", type: "condition", weight: 2 },
    { source: "real_distinction", target: "five_ways", type: "instrument", weight: 2 },
    { source: "participatio", target: "essence_existence", type: "mediate", weight: 2 },

    // ДУНС СКОТ
    { source: "voluntarism_scotus", target: "haecceitas", type: "influence", weight: 2 },
    { source: "infinity_scotus", target: "univocity_being", type: "presuppose", weight: 3 },
    { source: "common_nature", target: "formal_distinction", type: "presuppose", weight: 2 },
    { source: "univocity_being", target: "formal_distinction", type: "presuppose", weight: 3 },
    { source: "formal_distinction", target: "haecceitas", type: "instrument", weight: 3 },
    { source: "haecceitas", target: "common_nature", type: "complement", weight: 3 },

    // КУЗАНЕЦ
    { source: "possest", target: "coincidentia_oppositorum", type: "consequence", weight: 3 },
    { source: "maximum_minimum", target: "possest", type: "presuppose", weight: 2 },
    { source: "docta_ignorantia", target: "coincidentia_oppositorum", type: "presuppose", weight: 3 },
    { source: "coincidentia_oppositorum", target: "maximum_minimum", type: "exemplify", weight: 3 },
    { source: "enigma_cusanus", target: "docta_ignorantia", type: "instrument", weight: 2 },
    { source: "contraction", target: "maximum_minimum", type: "mediate", weight: 2 },

    // БЭКОН
    { source: "idols", target: "idols_tribe", type: "exemplify", weight: 2 },
    { source: "idols", target: "idols_cave", type: "exemplify", weight: 2 },
    { source: "idols", target: "idols_marketplace", type: "exemplify", weight: 2 },
    { source: "idols", target: "idols_theatre", type: "exemplify", weight: 2 },
    { source: "induction", target: "new_organon", type: "instrument", weight: 2 },
    { source: "knowledge_power", target: "new_organon", type: "culminate", weight: 2 },
    { source: "idols", target: "knowledge_power", type: "limit", weight: 2 },

    // ДЕКАРТ
    { source: "innate_ideas", target: "res_cogitans", type: "consequence", weight: 2 },
    { source: "method", target: "dualism", type: "consequence", weight: 2 },
    { source: "method", target: "clear_distinct", type: "consequence", weight: 2 },
    { source: "cogito", target: "infinite_idea", type: "consequence", weight: 2 },
    { source: "res_cogitans", target: "res_extensa", type: "internal_contradiction", weight: 3, bidirectional: true },
    { source: "dualism", target: "res_cogitans", type: "presuppose", weight: 3 },
    { source: "clear_distinct", target: "innate_ideas", type: "condition", weight: 3 },
    { source: "infinite_idea", target: "innate_ideas", type: "exemplify", weight: 2 },
    { source: "infinite_idea", target: "clear_distinct", type: "exemplify", weight: 2 },
    { source: "cogito", target: "clear_distinct", type: "exemplify", weight: 2 },
    { source: "method", target: "cogito", type: "instrument", weight: 3 },
    { source: "cogito", target: "dualism", type: "emerge_from", weight: 3 },

    // СПИНОЗА
    { source: "attributes", target: "modes", type: "consequence", weight: 3 },
    { source: "determinism", target: "substance_spinoza", type: "consequence", weight: 3 },
    { source: "intellectual_love", target: "substance_spinoza", type: "consequence", weight: 3 },
    { source: "intellectual_love", target: "deus_sive_natura", type: "consequence", weight: 3 },
    { source: "conatus", target: "modes", type: "consequence", weight: 3 },
    { source: "conatus", target: "adequate_ideas", type: "consequence", weight: 2 },
    { source: "deus_sive_natura", target: "determinism", type: "consequence", weight: 3 },
    { source: "natura_naturans", target: "substance_spinoza", type: "consequence", weight: 2 },
    { source: "natura_naturata", target: "modes", type: "consequence", weight: 2 },
    { source: "natura_naturans", target: "attributes", type: "consequence", weight: 2 },
    { source: "attributes", target: "substance_spinoza", type: "presuppose", weight: 3 },
    { source: "deus_sive_natura", target: "substance_spinoza", type: "presuppose", weight: 3 },
    { source: "natura_naturans", target: "natura_naturata", type: "presuppose", weight: 3, bidirectional: true },
    { source: "attributes", target: "deus_sive_natura", type: "condition", weight: 2 },
    { source: "natura_naturans", target: "deus_sive_natura", type: "exemplify", weight: 3 },
    { source: "natura_naturata", target: "deus_sive_natura", type: "exemplify", weight: 2 },
    { source: "adequate_ideas", target: "intellectual_love", type: "instrument", weight: 3 },
    { source: "substance_spinoza", target: "modes", type: "emerge_from", weight: 3 },

    // ЛОКК
    { source: "primary_qualities", target: "secondary_qualities", type: "oppose", weight: 3, bidirectional: true },
    { source: "substance_locke", target: "simple_ideas", type: "consequence", weight: 2 },
    { source: "tabula_rasa", target: "property_theory", type: "consequence", weight: 2 },
    { source: "tabula_rasa", target: "reflection", type: "consequence", weight: 2 },
    { source: "tabula_rasa", target: "social_contract_locke", type: "consequence", weight: 1 },
    { source: "personal_identity", target: "property_theory", type: "presuppose", weight: 2 },
    { source: "personal_identity", target: "government_consent", type: "presuppose", weight: 2 },
    { source: "social_contract_locke", target: "property_theory", type: "presuppose", weight: 3 },
    { source: "social_contract_locke", target: "government_consent", type: "presuppose", weight: 3 },
    { source: "primary_qualities", target: "substance_locke", type: "presuppose", weight: 2 },
    { source: "personal_identity", target: "social_contract_locke", type: "condition", weight: 2 },
    { source: "reflection", target: "personal_identity", type: "condition", weight: 3 },
    { source: "government_consent", target: "property_theory", type: "condition", weight: 2 },
    { source: "tabula_rasa", target: "simple_ideas", type: "condition", weight: 3 },
    { source: "reflection", target: "complex_ideas", type: "instrument", weight: 2 },
    { source: "government_consent", target: "social_contract_locke", type: "instrument", weight: 3 },
    { source: "personal_identity", target: "complex_ideas", type: "emerge_from", weight: 2 },
    { source: "simple_ideas", target: "complex_ideas", type: "emerge_from", weight: 3 },
    { source: "reflection", target: "simple_ideas", type: "emerge_from", weight: 3 },

    // ЛЕЙБНИЦ
    { source: "apperception", target: "petites_perceptions", type: "oppose", weight: 2, bidirectional: true },
    { source: "possible_worlds", target: "monads", type: "consequence", weight: 2 },
    { source: "possible_worlds", target: "preestablished", type: "consequence", weight: 2 },
    { source: "sufficient_reason", target: "preestablished", type: "consequence", weight: 2 },
    { source: "sufficient_reason", target: "monads", type: "consequence", weight: 2 },
    { source: "best_worlds", target: "monads", type: "consequence", weight: 2 },
    { source: "petites_perceptions", target: "monads", type: "consequence", weight: 2 },
    { source: "preestablished", target: "theodicy", type: "consequence", weight: 2 },
    { source: "identity_indiscernibles", target: "sufficient_reason", type: "consequence", weight: 3 },
    { source: "identity_indiscernibles", target: "perception_monad", type: "consequence", weight: 2 },
    { source: "possible_worlds", target: "best_worlds", type: "presuppose", weight: 3 },
    { source: "perception_monad", target: "monads", type: "presuppose", weight: 3 },
    { source: "petites_perceptions", target: "identity_indiscernibles", type: "presuppose", weight: 2 },
    { source: "monads", target: "preestablished", type: "presuppose", weight: 3 },
    { source: "continuity", target: "preestablished", type: "presuppose", weight: 2 },
    { source: "continuity", target: "monads", type: "presuppose", weight: 2 },
    { source: "continuity", target: "possible_worlds", type: "presuppose", weight: 2 },
    { source: "theodicy", target: "best_worlds", type: "presuppose", weight: 3 },
    { source: "theodicy", target: "sufficient_reason", type: "presuppose", weight: 3 },
    { source: "possible_worlds", target: "sufficient_reason", type: "condition", weight: 3 },
    { source: "perception_monad", target: "preestablished", type: "condition", weight: 3 },
    { source: "sufficient_reason", target: "best_worlds", type: "condition", weight: 3 },
    { source: "theodicy", target: "possible_worlds", type: "condition", weight: 2 },
    { source: "identity_indiscernibles", target: "monads", type: "condition", weight: 3 },
    { source: "apperception", target: "monads", type: "exemplify", weight: 2 },
    { source: "apperception", target: "perception_monad", type: "exemplify", weight: 2 },
    { source: "petites_perceptions", target: "perception_monad", type: "exemplify", weight: 3 },

    // БЕРКЛИ
    { source: "notions", target: "ideas_berkeley", type: "oppose", weight: 2 },
    { source: "immaterialism", target: "ideas_berkeley", type: "consequence", weight: 3 },
    { source: "ideas_berkeley", target: "esse_percipi", type: "presuppose", weight: 3 },
    { source: "notions", target: "spirit", type: "presuppose", weight: 3 },
    { source: "esse_percipi", target: "immaterialism", type: "presuppose", weight: 3 },
    { source: "god_perceiver", target: "esse_percipi", type: "condition", weight: 3 },
    { source: "spirit", target: "esse_percipi", type: "condition", weight: 3 },
    { source: "god_perceiver", target: "spirit", type: "exemplify", weight: 3 },

    // ЮМ
    { source: "is_ought", target: "impressions", type: "consequence", weight: 2 },
    { source: "causality_critique", target: "impressions", type: "consequence", weight: 3 },
    { source: "association", target: "custom", type: "presuppose", weight: 3 },
    { source: "association", target: "causality_critique", type: "condition", weight: 3 },
    { source: "impressions", target: "association", type: "condition", weight: 2 },
    { source: "association", target: "ideas_hume", type: "instrument", weight: 3 },
    { source: "custom", target: "ideas_hume", type: "mediate", weight: 2 },
    { source: "impressions", target: "ideas_hume", type: "emerge_from", weight: 3 },
    { source: "causality_critique", target: "custom", type: "emerge_from", weight: 3 },
    { source: "bundle_theory", target: "impressions", type: "emerge_from", weight: 3 },
];

// Загрузка обработанного файла
const processedFile = '/home/claude/relations_batch2_with_descriptions.js';
const content = fs.readFileSync(processedFile, 'utf8');
const processedRelations = eval(content.replace('const relations =', '').replace(/;$/, ''));

console.log(`Исходный список: ${originalRelations.length} связей`);
console.log(`Обработанный файл: ${processedRelations.length} связей\n`);

// ПРОВЕРКА 1: Полнота обработки
console.log('=== ПРОВЕРКА 1: Полнота обработки ===');

if (originalRelations.length !== processedRelations.length) {
    console.log(`❌ ОШИБКА: Количество связей не совпадает!`);
    console.log(`   Исходных: ${originalRelations.length}`);
    console.log(`   Обработанных: ${processedRelations.length}`);
} else {
    console.log(`✓ Количество связей совпадает: ${processedRelations.length}`);
}

// Создаём карту для поиска
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
    
    if (!processed) return;

    const procRel = processed.relation;
    const origFields = Object.keys(origRel);
    const procFields = Object.keys(procRel);

    // Проверяем сохранность полей
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

    // Проверяем лишние поля
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
    console.log(`\n⚠️  Добавлены дополнительные поля в ${extraFields.length} связях:`);
    extraFields.forEach(({ index, field, relation }) => {
        console.log(`   [${index}] ${relation} - поле: ${field}`);
    });
} else {
    console.log(`✓ Не добавлено лишних полей (только description)`);
}

// ИТОГ
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
    console.log('❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ');
    if (originalRelations.length !== processedRelations.length) {
        console.log(`   • Несовпадение количества связей`);
    }
    if (missingRelations.length > 0) {
        console.log(`   • Не обработано: ${missingRelations.length}`);
    }
    if (changedFields.length > 0) {
        console.log(`   • Изменено полей: ${changedFields.length}`);
    }
    if (missingDescriptions.length > 0) {
        console.log(`   • Без description: ${missingDescriptions.length}`);
    }
}

console.log('\n=== ПРОВЕРКА ЗАВЕРШЕНА ===');
process.exit(allChecksPass ? 0 : 1);
