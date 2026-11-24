#!/usr/bin/env node
/**
 * harmonize-eldamo-quenya.js
 * ---------------------------------------------------------------------------
 * Согласует расхождения между русской и английской сборками проекта
 * eldamo-intro-quenya-book. Применяет шесть изменений:
 *
 *   1) RUS: параметрический генератор рамки обложки buildCoverFrame
 *           (вместо чтения статического cover-frame.svg). Донор — ENG.
 *   2) RUS: откат неудавшегося «толчка» висячей буквы словаря
 *           (флаг runtPushFailed, поле headId, блок проверки (C)). Донор — ENG.
 *   3) ENG: усечение колонтитула с отбрасыванием висячих служебных слов и
 *           усечением длинной леммы-префикса — как в RUS, но со списком
 *           АНГЛИЙСКИХ предлогов и союзов.
 *   4) ОБЕ: единый алгоритм извлечения леммы-заголовка в гл.13 — до первого
 *           пробела/скобки/кавычки, с запасным разбором самым длинным
 *           заголовком-префиксом для склеенного pdfjs-случая («minyaadj.»).
 *   5) ENG: вернуть поле x в глобальную карту destinations (как в RUS).
 *   6) RUS: принудительный разрыв страницы перед первой буквой словаря гл.13
 *           (класс dict-letter-open в merge.js + правило в print.css). Донор — ENG.
 *
 * Скрипт ИДЕМПОТЕНТЕН: повторный запуск ничего не меняет. Крупные блоки
 * (#1, #2, #6) переносятся напрямую из английской версии, поэтому обе сборки
 * должны быть доступны.
 *
 * Запуск:
 *   node harmonize-eldamo-quenya.js --rus <path/to/RUS> --eng <path/to/ENG>
 *   node harmonize-eldamo-quenya.js                       # автопоиск рядом
 *   node harmonize-eldamo-quenya.js --dry                 # без записи (превью)
 *   node harmonize-eldamo-quenya.js --verify              # node --check после правок
 *
 * <path> может указывать как на корень проекта (содержит scripts/), так и
 * прямо на каталог scripts/.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// ─── аргументы ──────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
const flag = (name) => {
    const i = argv.indexOf(name);
    return i >= 0 ? (argv[i + 1] || '') : null;
};
const DRY = argv.includes('--dry');
const VERIFY = argv.includes('--verify');

// ─── разрешение путей к scripts/ обеих сборок ───────────────────────────────
function resolveScriptsDir(p) {
    if (!p) return null;
    const abs = path.resolve(p);
    if (fs.existsSync(path.join(abs, 'run.js'))) return abs;            // уже scripts/
    if (fs.existsSync(path.join(abs, 'scripts', 'run.js')))             // корень проекта
        return path.join(abs, 'scripts');
    return abs; // вернём как есть — упадём позже с понятной ошибкой
}
function autodetect(pattern) {
    // ищем каталог *_<LANG>/scripts рядом с cwd
    const here = process.cwd();
    const hit = fs.readdirSync(here, { withFileTypes: true })
        .filter(d => d.isDirectory() && pattern.test(d.name))
        .map(d => path.join(here, d.name, 'scripts'))
        .find(d => fs.existsSync(path.join(d, 'run.js')));
    return hit || null;
}
const RUS = resolveScriptsDir(flag('--rus')) || autodetect(/_RUS$/i);
const ENG = resolveScriptsDir(flag('--eng')) || autodetect(/_ENG$/i);

if (!RUS || !ENG || !fs.existsSync(path.join(RUS, 'run.js')) || !fs.existsSync(path.join(ENG, 'run.js'))) {
    console.error('Не найдены каталоги scripts/ обеих сборок.');
    console.error('Укажите их явно: --rus <путь> --eng <путь>');
    console.error('  RUS =', RUS); console.error('  ENG =', ENG);
    process.exit(2);
}

// ─── файловый слой с буферизацией и идемпотентностью ────────────────────────
const buf = new Map();           // path -> текущий текст
function load(p) {
    if (!buf.has(p)) {
        const t = fs.readFileSync(p, 'utf8');
        if (t.includes('\r')) console.warn('  ! Внимание: CRLF в', p, '— якоря рассчитаны на LF.');
        buf.set(p, t);
    }
    return buf.get(p);
}
function set(p, t) { buf.set(p, t); }

const report = [];
function step(id, desc, fn) {
    try {
        const res = fn();              // 'applied' | 'skipped' | 'noop'
        report.push({ id, desc, status: res });
    } catch (e) {
        report.push({ id, desc, status: 'ERROR', error: e.message });
    }
}

// заменить ровно одно вхождение oldStr на newStr в файле p
function replaceOnce(p, oldStr, newStr) {
    const t = load(p);
    const idx = t.indexOf(oldStr);
    if (idx < 0) throw new Error('якорь не найден в ' + path.basename(p));
    if (t.indexOf(oldStr, idx + 1) >= 0) throw new Error('якорь неоднозначен в ' + path.basename(p));
    set(p, t.slice(0, idx) + newStr + t.slice(idx + oldStr.length));
}

// ─── извлечение блоков-доноров из английской версии ─────────────────────────
function grabFnWithComment(text, sig, endTrim) {
    const ls = text.split('\n');
    const si = ls.findIndex(l => l.includes(sig));
    if (si < 0) throw new Error('донор: не найдена сигнатура ' + sig);
    let start = si;
    while (start > 0 && ls[start - 1].trim().startsWith('//')) start--;
    const ei = ls.findIndex((l, i) => i >= si && l.trim() === endTrim);
    if (ei < 0) throw new Error('донор: не найден конец ' + endTrim);
    return ls.slice(start, ei + 1).join('\n');
}
function grabUntil(text, startNeedle, endNeedle) {           // [start .. end)
    const ls = text.split('\n');
    const si = ls.findIndex(l => l.includes(startNeedle));
    if (si < 0) throw new Error('донор: не найдено начало ' + startNeedle);
    const ei = ls.findIndex((l, i) => i > si && l.includes(endNeedle));
    if (ei < 0) throw new Error('донор: не найден конец ' + endNeedle);
    return ls.slice(si, ei).join('\n');
}
function grabInclusive(text, startNeedle, endNeedle) {       // [start .. end]
    const ls = text.split('\n');
    const si = ls.findIndex(l => l.includes(startNeedle));
    if (si < 0) throw new Error('донор: не найдено начало ' + startNeedle);
    const ei = ls.findIndex((l, i) => i >= si && l.includes(endNeedle));
    if (ei < 0) throw new Error('донор: не найден конец ' + endNeedle);
    return ls.slice(si, ei + 1).join('\n');
}

const RUN_R = path.join(RUS, 'run.js');
const RUN_E = path.join(ENG, 'run.js');
const MRG_R = path.join(RUS, 'merge.js');
const MRG_E = path.join(ENG, 'merge.js');
const CSS_R = path.join(RUS, 'print.css');
const CSS_E = path.join(ENG, 'print.css');

const engRun = load(RUN_E), engMerge = load(MRG_E), engCss = load(CSS_E);

// ════════════════════════════════════════════════════════════════════════════
// #1 — RUS: параметрическая рамка обложки
// ════════════════════════════════════════════════════════════════════════════
step('1a', 'RUS run.js: внедрить IIFE buildCoverFrame (донор ← ENG)', () => {
    const t = load(RUN_R);
    if (t.includes('const buildCoverFrame = (() => {')) return 'skipped';
    const donor = grabFnWithComment(engRun, 'const buildCoverFrame = (() => {', '})();');
    const anchor = "    RUS: { width: '170mm', height: '240mm' }\n};";
    replaceOnce(RUN_R, anchor, anchor + '\n\n' + donor);
    return 'applied';
});
step('1b', "RUS run.js: cover-frame.svg → buildCoverFrame(width,height)", () => {
    const t = load(RUN_R);
    if (t.includes('? buildCoverFrame(parseFloat(pageFormat.width)')) return 'skipped';
    replaceOnce(RUN_R,
        "                ? require('fs').readFileSync(path.resolve(__dirname, 'cover-frame.svg'), 'utf8')",
        "                ? buildCoverFrame(parseFloat(pageFormat.width), parseFloat(pageFormat.height))");
    return 'applied';
});
step('1c', 'RUS run.js: экспорт buildCoverFrame', () => {
    const t = load(RUN_R);
    if (t.includes('PAGE_FORMATS, buildCoverFrame,')) return 'skipped';
    replaceOnce(RUN_R,
        'module.exports = { runPdfMain, PAGE_FORMATS, extractDests,',
        'module.exports = { runPdfMain, PAGE_FORMATS, buildCoverFrame, extractDests,');
    return 'applied';
});

// ════════════════════════════════════════════════════════════════════════════
// #2 — RUS: откат неудавшегося толчка висячей буквы
// ════════════════════════════════════════════════════════════════════════════
step('2a', 'RUS run.js: guard runtPushFailed', () => {
    const t = load(RUN_R);
    if (t.includes('h.dataset.runtPushed || h.dataset.runtPushFailed')) return 'skipped';
    replaceOnce(RUN_R,
        'if (h.dataset.runtPushed) continue;',
        'if (h.dataset.runtPushed || h.dataset.runtPushFailed) continue;');
    return 'applied';
});
step('2b', 'RUS run.js: вернуть headId в объекте moved', () => {
    const t = load(RUN_R);
    if (t.includes('glued: uls.length, unglued, diag, headId: h.id }')) return 'skipped';
    replaceOnce(RUN_R,
        'glued: uls.length, unglued, diag };',
        'glued: uls.length, unglued, diag, headId: h.id };');
    return 'applied';
});
step('2c', 'RUS run.js: блок проверки/отката (C) (донор ← ENG)', () => {
    const t = load(RUN_R);
    if (t.includes('// (C) Проверка результата толчка')) return 'skipped';
    const donor = grabUntil(engRun,
        '// (C) Проверка результата толчка',
        '// Контрольная балансировка ПОСЛЕ КАЖДОГО пуша');
    // вставляем между `await printOnce();` рантфикса и комментарием балансировки
    const anchor = '                await printOnce();\n' +
                   '                // Контрольная балансировка ПОСЛЕ КАЖДОГО пуша (а не после';
    replaceOnce(RUN_R, anchor,
        '                await printOnce();\n' + donor + '\n' +
        '                // Контрольная балансировка ПОСЛЕ КАЖДОГО пуша (а не после');
    return 'applied';
});

// ════════════════════════════════════════════════════════════════════════════
// #3 — ENG: усечение колонтитула со списком АНГЛИЙСКИХ служебных слов
// ════════════════════════════════════════════════════════════════════════════
step('3', 'ENG run.js: fitHeader с отбрасыванием служебных слов (англ. список)', () => {
    const t = load(RUN_E);
    if (t.includes('const HEADER_FN_WORDS')) return 'skipped';

    const oldBlock = String.raw`    // Собирает строку колонтитула «префикс + название» так, чтобы её
    // ширина не превышала maxW. Префикс (номер/«Глава N —») сохраняется
    // всегда; название обрезается по последнему влезающему слову, и
    // добавляется «…». Если не влезает даже первое слово — только префикс.
    const fitHeader = (prefix, rest, size, maxW) => {
        if (!rest) return prefix;
        const full = prefix + ' ' + rest;
        if (font.widthOfTextAtSize(full, size) <= maxW) return full;
        const words = rest.split(/\s+/);
        let acc = '';
        for (let k = 0; k < words.length; k++) {
            const cand = acc ? acc + ' ' + words[k] : words[k];
            if (font.widthOfTextAtSize(prefix + ' ' + cand + '…', size) <= maxW) acc = cand;
            else break;
        }
        return acc ? prefix + ' ' + acc.replace(/,\s*$/, '') + '…' : prefix;
    };`;

    const newBlock = String.raw`    // Закрытый класс служебных слов: висячий хвост перед «…» отбрасываем.
    // Предлоги + сочинительные/подчинительные союзы (английский набор).
    const HEADER_FN_WORDS = new Set([
        // prepositions
        'about','above','across','after','against','along','amid','among','amongst',
        'around','as','at','before','behind','below','beneath','beside','besides',
        'between','betwixt','beyond','by','concerning','despite','down','during',
        'except','for','from','in','inside','into','like','near','of','off','on',
        'onto','opposite','out','outside','over','past','per','regarding','round',
        'since','than','through','throughout','till','to','toward','towards','under',
        'underneath','until','unto','up','upon','versus','via','with','within','without',
        // conjunctions
        'and','or','nor','but','yet','so','both','either','neither','whether',
        'although','though','because','if','unless','while','whilst','whereas',
    ]);
    const headerNorm = (w) => {
        const m = w.toLowerCase().match(/[0-9a-zà-ÿ'’]+(?:-[0-9a-zà-ÿ'’]+)*/u);
        return m ? m[0] : '';
    };
    const dropTrailingFnWords = (words) => {
        const w = words.slice();
        while (w.length && HEADER_FN_WORDS.has(headerNorm(w[w.length - 1]))) w.pop();
        return w;
    };

    // Собирает строку колонтитула «префикс + название» так, чтобы её ширина
    // не превышала maxW. Префикс (номер/«Chapter N —») сохраняется; название
    // усекается по последнему влезающему слову с «…», висячий служебный
    // хвост (предлог/союз) отбрасывается. Если rest пуст, а сам prefix длинный
    // (лемма словаря) — усекается prefix.
    const joinHdr = (p, b) => (p && b) ? p + ' ' + b : (p || b);
    const fitHeader = (prefix, rest, size, maxW) => {
        prefix = (prefix || '').trim();
        rest   = (rest   || '').trim();
        const full = joinHdr(prefix, rest);
        if (font.widthOfTextAtSize(full, size) <= maxW) return full;

        // Нечего сокращать в rest → сокращаем сам prefix (длинная лемма словаря).
        if (!rest) {
            const words = prefix.split(/\s+/);
            let kept = [];
            for (let k = 0; k < words.length; k++) {
                const cand = [...kept, words[k]];
                if (font.widthOfTextAtSize(cand.join(' ') + '…', size) <= maxW) kept = cand;
                else break;
            }
            kept = dropTrailingFnWords(kept);
            const body = kept.join(' ').replace(/,\s*$/, '');
            return body ? body + '…' : '…';
        }

        // Обычный случай: префикс (номер) фикс., название набираем по словам.
        const words = rest.split(/\s+/);
        let kept = [];
        for (let k = 0; k < words.length; k++) {
            const cand = [...kept, words[k]];
            if (font.widthOfTextAtSize(joinHdr(prefix, cand.join(' ')) + '…', size) <= maxW) kept = cand;
            else break;
        }
        kept = dropTrailingFnWords(kept);
        if (!kept.length) return prefix || '…';
        const body = kept.join(' ').replace(/,\s*$/, '');
        return joinHdr(prefix, body) + '…';
    };`;

    replaceOnce(RUN_E, oldBlock, newBlock);
    return 'applied';
});

// ════════════════════════════════════════════════════════════════════════════
// #4 — ОБЕ: единый разбор леммы гл.13 (до пробела/скобки + запасной префикс)
// ════════════════════════════════════════════════════════════════════════════
const UNIFIED_LEMMA = String.raw`                    // Гл.13: ведущая лемма — до первого пробела/скобки/кавычки.
                    // Если из-за склейки pdfjs части речи с леммой («minyaadj.»/
                    // «minyaчисл.») точного совпадения нет — берём самый длинный
                    // заголовок из списка, являющийся префиксом строки.
                    const lead = text.replace(/^[#†*^!\s]+/, '');
                    const cut = lead.match(/^[^\s«»“”"'()\[\]]+/);
                    if (cut) title = titles.get(norm(cut[0])) || null;
                    if (!title) {
                        let best = '';
                        for (const key of titles.keys()) {
                            if (key.length > best.length && lead.startsWith(key)) best = key;
                        }
                        if (best) title = titles.get(best);
                    }`;

step('4-rus', 'RUS run.js: единый разбор леммы гл.13', () => {
    const t = load(RUN_R);
    if (t.includes('ведущая лемма — до первого пробела/скобки/кавычки')) return 'skipped';
    const oldBlock = String.raw`                    // Гл.13: ведущая лемма = максимальный НЕ-кириллический токен
                    // после маркеров #†*^!. pdfjs склеивает лемму с кириллической
                    // частью речи без пробела («minyaчисл.»), поэтому граница —
                    // кириллица/кавычка/скобка/пробел, а не пробел после леммы.
                    const t2 = text.replace(/^[#†*^!\s]+/, '');
                    const lm = t2.match(/^[^\s«»“”"()\u0400-\u04FF]+/);
                    if (lm) title = titles.get(norm(lm[0])) || null;`;
    replaceOnce(RUN_R, oldBlock, UNIFIED_LEMMA);
    return 'applied';
});

step('4-eng', 'ENG run.js: единый разбор леммы гл.13', () => {
    const t = load(RUN_E);
    if (t.includes('ведущая лемма — до первого пробела/скобки/кавычки')) return 'skipped';
    const oldBlock = String.raw`                    const lead = text.replace(/^[#†*^!\s]+/, '');
                    let best = '';
                    for (const key of titles.keys()) {
                        if (key.length > best.length && lead.startsWith(key)) best = key;
                    }
                    if (best) title = titles.get(best);`;
    replaceOnce(RUN_E, oldBlock, UNIFIED_LEMMA);
    // привести верхний комментарий блока к краткому виду (как в RUS),
    // чтобы не оставлять устаревшее описание «longest-prefix».
    const staleComment = String.raw`        // Начала статей в колонке: ведущий текст строки ∈ белый список.
        // Гл.14 — слово в первых «…». Гл.13 — ведущая лемма латиницей; часть
        // речи в EN тоже латиницей и может слипаться с леммой («minyaadj.»),
        // поэтому НЕ режем токен по разделителю, а ищем самый ДЛИННЫЙ
        // заголовок из списка, являющийся префиксом строки (после маркеров
        // #†*^!) — языконезависимо и устойчиво к слипанию.`;
    if (load(RUN_E).includes(staleComment)) {
        replaceOnce(RUN_E, staleComment,
            '        // Начала статей в колонке: ведущий текст строки ∈ белый список.');
    }
    return 'applied';
});

// ════════════════════════════════════════════════════════════════════════════
// #5 — ENG: вернуть поле x в глобальную карту destinations
// ════════════════════════════════════════════════════════════════════════════
step('5', 'ENG run.js: поле x в global destinations', () => {
    const t = load(RUN_E);
    if (t.includes('global[name] = { page: d.page + totalPages, x: d.x, y: d.y }')) return 'skipped';
    replaceOnce(RUN_E,
        'global[name] = { page: d.page + totalPages, y: d.y };',
        'global[name] = { page: d.page + totalPages, x: d.x, y: d.y };');
    // комментарий-сигнатура карты
    const cOld = 'const global = {};   // name -> { page (1-базная, в склейке), y }';
    if (load(RUN_E).includes(cOld)) {
        replaceOnce(RUN_E, cOld,
            'const global = {};   // name -> { page (1-базная, в склейке), x, y }');
    }
    return 'applied';
});

// ════════════════════════════════════════════════════════════════════════════
// #6 — RUS: принудительный разрыв перед первой буквой словаря гл.13
// ════════════════════════════════════════════════════════════════════════════
step('6a', 'RUS merge.js: класс dict-letter-open для гл.13 (донор ← ENG)', () => {
    const t = load(MRG_R);
    if (t.includes('dict-letter-open')) return 'skipped';
    const donor = grabUntil(engMerge, '// Гл.13 (Quenya-глоссарий)', 'outBody.appendChild(section);');
    const anchor =
        '            section.appendChild(outDoc.importNode(child, true));\n' +
        '        }\n' +
        '        outBody.appendChild(section);';
    replaceOnce(MRG_R, anchor,
        '            section.appendChild(outDoc.importNode(child, true));\n' +
        '        }\n' + donor + '\n' +
        '        outBody.appendChild(section);');
    return 'applied';
});
step('6b', 'RUS print.css: правило h2.dict-letter-open (донор ← ENG)', () => {
    const t = load(CSS_R);
    if (t.includes('h2.dict-letter-open')) return 'skipped';
    const donor = grabInclusive(engCss,
        '/* Первая рубрика словаря после обширного введения', '}');
    const anchor = 'h2.dict-letter {\n    page-break-after: avoid;\n    break-after: avoid;\n}';
    replaceOnce(CSS_R, anchor, anchor + '\n\n' + donor);
    return 'applied';
});

// ─── запись ─────────────────────────────────────────────────────────────────
const touched = [];
for (const [p, t] of buf.entries()) {
    const orig = fs.readFileSync(p, 'utf8');
    if (t !== orig) {
        touched.push(p);
        if (!DRY) fs.writeFileSync(p, t);
    }
}

// ─── отчёт ──────────────────────────────────────────────────────────────────
const pad = (s, n) => (s + ' '.repeat(n)).slice(0, n);
const mark = { applied: '✓ ПРИМЕНЕНО', skipped: '· уже было', noop: '· нет', ERROR: '✗ ОШИБКА' };
console.log('\n  RUS scripts:', RUS);
console.log('  ENG scripts:', ENG);
console.log('  Режим:', DRY ? 'DRY-RUN (без записи)' : 'запись', '\n');
console.log('  ' + pad('ID', 8) + pad('Статус', 14) + 'Что');
console.log('  ' + '─'.repeat(78));
let errors = 0;
for (const r of report) {
    if (r.status === 'ERROR') errors++;
    console.log('  ' + pad(r.id, 8) + pad(mark[r.status] || r.status, 14) + r.desc +
        (r.error ? '  — ' + r.error : ''));
}
console.log('  ' + '─'.repeat(78));
console.log('  Файлов ' + (DRY ? 'к изменению' : 'изменено') + ':', touched.length);
touched.forEach(p => console.log('    • ' + p));

// ─── опциональная проверка синтаксиса ───────────────────────────────────────
if (VERIFY && !DRY) {
    console.log('\n  node --check:');
    for (const p of touched.filter(p => p.endsWith('.js'))) {
        try { execFileSync(process.execPath, ['--check', p]); console.log('    ✓', path.basename(p)); }
        catch (e) { console.log('    ✗', path.basename(p), '— синтаксическая ошибка'); errors++; }
    }
}

if (errors) { console.error('\n  Завершено с ошибками:', errors); process.exit(1); }
console.log('\n  Готово.' + (DRY ? ' (изменения не записаны — это превью)' : ''));
