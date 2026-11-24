// Сценарий 9: админка — шаблоны промптов (редактор, плейсхолдеры, версии и дифф), конфиги, каталоги, доступ, почта, тарифы
import { account, sql, sleep } from "./api.mjs";
import * as U from "./ui.mjs";
globalThis.SCENARIO = "9. Админка: промпты, конфиги, доступ, почта, тарифы";
const A = await account("author@lab.local", "password-lab", "Автор стенда");
await sql`update users set role = 'admin' where id = ${A.id}`;
await U.launch(); const p = await U.page(A);
const tab = async (t) => { await p.evaluate((t) => document.querySelector(`[data-testid="tab-${t}"]`)?.click(), t); await sleep(1500); };
await p.goto(U.UI + "/admin/prompts", { waitUntil: "networkidle0" });
await p.waitForSelector('[data-testid="templates-tab"]', { timeout: 20000 });
await sleep(1000);
await U.shot(p, "admin-templates", "Админка: реестр шаблонов промптов — дерево ключей (system, method, level, section…)");
// шаблон раздела: ищем и открываем
await U.setInput(p, '[data-testid="template-search"]', "section.graph");
await sleep(800);
await p.evaluate(() => { const it = [...document.querySelectorAll(".key-tree-item")].find((e) => /section\.graph\.preamble/.test(e.innerText)) ?? document.querySelector(".key-tree-item"); it?.scrollIntoView({ block: "center" }); it?.click(); });
await sleep(1500);
await U.shot(p, "admin-template-editor", "Шаблон раздела графа: тело с плейсхолдерами, фишки переменных, история версий");
// правка: черновик новой версии
const body = await p.$('[data-testid="template-body"]');
if (body) {
  await p.evaluate(() => { const t = document.querySelector('[data-testid="template-body"]'); t.scrollIntoView({ block: "center" }); });
  await body.click(); await p.keyboard.press("End"); await p.keyboard.down("Control"); await p.keyboard.press("End"); await p.keyboard.up("Control");
  await p.keyboard.type("\n\nДополнительно: у каждой категории укажи эпоху её первого появления.");
  await sleep(600);
  await U.shot(p, "admin-template-edited", "Правка шаблона: строка добавлена, проверка плейсхолдеров на лету");
  await p.evaluate(() => document.querySelector('[data-testid="template-save-draft"]')?.click()); await sleep(1800);
  await p.evaluate(() => { const v = document.querySelector('[data-testid="version-list"] .version-item, [data-testid="version-list"] li'); v?.click(); }); await sleep(1200);
  await p.evaluate(() => document.querySelector('[data-testid="diff-view"]')?.scrollIntoView({ block: "center" })); await sleep(500);
  await U.shot(p, "admin-template-diff", "Черновик сохранён новой версией: список версий и построчный дифф с действующей");
}
await tab("configs"); await sleep(500);
await p.evaluate(() => { const it = document.querySelector('[data-testid="configs-tab"] .key-tree-item'); it?.click(); }); await sleep(1500);
await U.shot(p, "admin-configs", "Конфиги: JSON-редактор с проверкой, черновик и активация версии");
await tab("catalogs");
await U.shot(p, "admin-catalogs", "Каталоги таксономии: системные и пользовательские типы категорий и связей");
await tab("access");
await U.shot(p, "admin-access", "Доступ: пользователи, роли, статусы и журнал действий");
await tab("mail");
await U.shot(p, "admin-mail", "Почта: очередь писем, счётчики отправленных, ожидающих и сбойных");
await tab("plans");
await U.shot(p, "admin-plans", "Тарифы: семейства и редакции, цены, квоты, живые подписки");
await p.evaluate(() => document.querySelector('[data-testid="plans-new-family"]')?.click()); await sleep(1000);
await p.evaluate(() => document.querySelector('[data-testid="plan-create-form"]')?.scrollIntoView({ block: "center" }));
await U.shot(p, "admin-plan-new", "Новый тариф: форма с ценой и периодом в одну строку, квотами и открытием для покупки");
console.log("errors", p.errors);
await U.close(); await sql.end();
