/**
 * Общая часть инструментов локализации: мастер-таблица, имена ключей,
 * подстановки, поиск вызовов tl() в коде.
 *
 * Мастер-таблица packages/shared/i18n/strings.json — единственный файл,
 * который правят руками (переводчик — через export/import):
 *
 *   { "meta": {…},
 *     "strings": {
 *       "catalog.synthesisCard.author": {"ru":"Автор: {authorName}","en":"Author: {authorName}","de":null,
 *          "from":{"en":"Автор: {authorName}"},"draft":["en"],"params":{"authorName":"synthesis.authorName"},
 *          "where":["client/src/components/catalog/SynthesisCard.tsx:212"]},
 *       … } }
 *
 *   from[lang]  — русский текст, с которого сделан перевод: разошёлся с ru —
 *                 перевод устарел;
 *   draft       — языки, где перевод черновой (не вычитан переводчиком);
 *   params      — подстановки и выражения за ними (справка переводчику);
 *   data        — строка из данных (общие константы, сиды БД): в коде нет
 *                 вызова tl(), export не считает её исчезнувшей;
 *   static      — строка вычисляется при импорте модуля: при смене языка
 *                 сама не обновится, нужна ручная переделка;
 *   obsolete    — ключа больше нет в коде (export помечает, --prune удаляет).
 */

import ts from "typescript";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

export const FN = "tl";
export const FN_MODULE = "@philosynth/shared/i18n/t";
export const TABLE_PATH = "packages/shared/i18n/strings.json";
export const LANGS = ["ru", "en", "de"];
export const NAMES_PATH = "scripts/i18n/names.json";

/* ───────────── Имена ключей ───────────── */

/** names.json: [[ns, ru, leaf|null, enDraft|null], …]; leaf null — строка
 *  не интерфейсная (промпт, образец, сопоставитель) и в таблицу не идёт. */
export function loadNames(root) {
  const list = JSON.parse(fs.readFileSync(path.join(root, NAMES_PATH), "utf8"));
  const map = new Map();
  for (const [ns, ru, leaf, en] of list) map.set(`${ns}\u0000${ru}`, { leaf, en });
  return map;
}

/** Ключ записи описи: сначала пространство имён файла, затем common. */
export function resolveName(names, ns, entry) {
  const own = names.get(`${ns}\u0000${entry.text}`);
  if (own) return own.leaf ? { key: `${ns}.${own.leaf}`, en: own.en } : { exclude: true };
  if (!entry.args) {
    const common = names.get(`common\u0000${entry.text}`);
    if (common?.leaf) return { key: `common.${common.leaf}`, en: common.en };
  }
  return null;
}

/* ───────────── Подстановки ───────────── */

const NOISE = new Set([
  "toFixed", "toLocaleString", "join", "map", "filter", "length", "String", "Number",
  "Math", "round", "floor", "ceil", "as", "number", "string", "new", "Set", "size", "trim",
  "toUpperCase", "toLowerCase", "replace", "slice", "ru", "RU", "const", "true", "false",
  "null", "undefined", "typeof", "of", "in", "r", "m", "n", "s", "f", "e", "x", "v", "i", "k",
]);

/** Имена подстановок по выражениям: synthesis.authorName → authorName,
 *  response.status → status, (cost as number).toFixed(4) → cost. */
export function paramNames(args) {
  const used = new Map();
  return args.map((expr) => {
    const ids = (expr.match(/[A-Za-z_$][\w$]*/g) ?? []).filter((w) => !NOISE.has(w) && !/^[A-Z_]+$/.test(w));
    let name = ids.at(-1) ?? "value";
    if (/\.length\b/.test(expr) && !/count$/i.test(name)) name += "Count";
    name = name.replace(/^[A-Z]/, (c) => c.toLowerCase()).replace(/^\$/, "");
    const n = (used.get(name) ?? 0) + 1;
    used.set(name, n);
    return n === 1 ? name : `${name}${n}`;
  });
}

/** {0},{1} → {имя}. */
export function toNamed(text, names) {
  return text.replace(/\{(\d+)\}/g, (w, i) => (names[+i] !== undefined ? `{${names[+i]}}` : w));
}

/** Множество подстановок {имя} в тексте (для сверки перевода). */
export function placeholderSet(text) {
  return [...new Set((text ?? "").match(/\{[A-Za-z_$][\w$]*\}/g) ?? [])].sort().join(",");
}

/* ───────────── Мастер-таблица ───────────── */

const FIELD_ORDER = ["ru", ...LANGS.filter((l) => l !== "ru"), "from", "draft", "params", "note", "data", "static", "obsolete", "where"];

export function readTable(root, p = TABLE_PATH) {
  const abs = path.isAbsolute(p) ? p : path.join(root, p);
  if (!fs.existsSync(abs)) return { meta: {}, strings: {} };
  return JSON.parse(fs.readFileSync(abs, "utf8"));
}

function orderEntry(e) {
  const o = {};
  for (const k of FIELD_ORDER) if (e[k] !== undefined) o[k] = e[k];
  for (const k of Object.keys(e)) if (!(k in o)) o[k] = e[k];
  return o;
}

/** Запись: meta развёрнуто, строки — по одной на строку файла, ключи по алфавиту. */
export function writeTable(abs, table) {
  const keys = Object.keys(table.strings).sort();
  const lines = ["{", `  "meta": ${JSON.stringify(table.meta, null, 2).replace(/\n/g, "\n  ")},`, `  "strings": {`];
  keys.forEach((k, i) => {
    lines.push(`    ${JSON.stringify(k)}: ${JSON.stringify(orderEntry(table.strings[k]))}${i < keys.length - 1 ? "," : ""}`);
  });
  lines.push("  }", "}", "");
  fs.writeFileSync(abs, lines.join("\n"));
}

/** Перевод устарел: русский текст сменился после перевода. */
export function isStale(e, lang) {
  return e[lang] != null && e.from?.[lang] !== undefined && e.from[lang] !== e.ru;
}

export const hashText = (s) => crypto.createHash("sha1").update(s).digest("hex").slice(0, 8);

/* ───────────── Вызовы tl() в коде ───────────── */

const CODE_DIRS = ["client/src", "server", "packages/shared", "scripts"];

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (!["node_modules", "dist", "build", "i18n"].includes(e.name) || p.includes("packages/shared/i18n") === false && e.name !== "i18n") {
        if (!["node_modules", "dist", "build"].includes(e.name)) walk(p, out);
      }
    } else if (/\.(tsx?|mts)$/.test(e.name) && !/\.d\.ts$/.test(e.name)) out.push(p);
  }
  return out;
}

const strValue = (n) =>
  n && (ts.isStringLiteral(n) || ts.isNoSubstitutionTemplateLiteral(n)) ? n.text : null;

/**
 * Все вызовы tl("key", "ru", {…}) в коде.
 * → { calls: Map<key, {ru, where[], params[]}>, problems: [] }
 * Ключ и русский текст обязаны быть литералами; иначе — problem.
 */
export function scanCalls(root) {
  const calls = new Map();
  const problems = [];
  for (const dir of CODE_DIRS) {
    for (const abs of walk(path.join(root, dir))) {
      const rel = path.relative(root, abs).split(path.sep).join("/");
      if (rel === "packages/shared/i18n/t.ts") continue;
      const src = fs.readFileSync(abs, "utf8");
      if (!src.includes(`${FN}(`)) continue;
      const sf = ts.createSourceFile(abs, src, ts.ScriptTarget.Latest, true,
        abs.endsWith("x") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
      (function v(n) {
        if (ts.isCallExpression(n) && ts.isIdentifier(n.expression) && n.expression.text === FN) {
          const line = sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;
          const key = strValue(n.arguments[0]);
          const ru = strValue(n.arguments[1]);
          if (key == null || ru == null) {
            problems.push(`${rel}:${line}: ключ и русский текст tl() должны быть строковыми литералами`);
          } else {
            const params = [];
            const p = n.arguments[2];
            if (p && ts.isObjectLiteralExpression(p)) {
              for (const prop of p.properties) if (prop.name) params.push(prop.name.getText(sf));
            }
            const prev = calls.get(key);
            if (prev && prev.ru !== ru) problems.push(`${rel}:${line}: ключ ${key} уже встречался с другим русским текстом (${prev.where[0]})`);
            if (prev) prev.where.push(`${rel}:${line}`);
            else calls.set(key, { ru, where: [`${rel}:${line}`], params });
          }
        }
        ts.forEachChild(n, v);
      })(sf);
    }
  }
  return { calls, problems };
}
