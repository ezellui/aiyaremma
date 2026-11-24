// Сценарий 10: кредиты подписки и подписи стоимости по способу оплаты (2026-11-17)
import { account, sql, sleep, waitStatus } from "./api.mjs";
import * as U from "./ui.mjs";
globalThis.SCENARIO = "10. Кредиты и подписи стоимости";
const body = { seed: "свобода как познанная необходимость", philosophers: ["Спиноза", "Гегель", "Маркс"], sections: ["sum", "graph", "glossary", "theses", "history", "name", "critique", "capsule"], method: "dialectical", depth: "standard", synthLevel: "comparative" };

const [starter] = await sql`select id from subscription_plans where name='starter'`;
await sql`update subscription_plans set is_active = true where family in ('starter','pro','academic')`;
const SUB = await account("credits-sub@lab.local", "password-lab", "Подписчик");
const BAL = await account("credits-bal@lab.local", "password-lab", "Плательщик с баланса");
const BYO = await account("credits-byo@lab.local", "password-lab", "Свой ключ");
await sql`delete from user_subscriptions where user_id=${SUB.id}`;
await sql`insert into user_subscriptions (user_id, plan_id, stripe_subscription_id, status, current_period_start, current_period_end, used_credits) values (${SUB.id}, ${starter.id}, ${"sub_lab_" + Date.now()}, 'active', now() - interval '3 days', now() + interval '27 days', 120)`;
await sql`update users set balance_usd = 0 where id=${SUB.id}`;
await BYO.api("POST", "/billing/api-key", { key: "sk-ant-api03-LAB-" + "k".repeat(60) });
for (const u of [SUB, BAL, BYO]) console.log(u.email, (await u.api("GET", "/billing/view")).json);

await U.launch();
// стартовая: тарифы с раскладкой (гость)
{
  const g = await U.page(null);
  await g.goto(U.UI + "/", { waitUntil: "networkidle0" });
  await sleep(800);
  await U.shot(g, "landing-plans", "Стартовая страница: тарифы в кредитах, раскладка «на что хватит» и цена операций", { el: '[data-testid="landing-plans-table"]', settle: 300 });
  const sec = await g.$('[data-testid="landing-plans-table"]');
  const box = await sec?.evaluate((el) => { const s = el.closest("section") ?? el.parentElement; s.scrollIntoView(); const r = s.getBoundingClientRect(); return { x: r.x, y: r.y + window.scrollY, width: r.width, height: r.height }; });
  if (box) await g.screenshot({ path: `${U.SHOTS}/s10-00-landing-section.png`, clip: { ...box, y: box.y - window_scroll(0) } }).catch(() => {});
}
function window_scroll(v) { return v; }

// форма: оценка синтеза у трёх плательщиков
for (const [who, label] of [[SUB, "подписчик"], [BAL, "баланс"], [BYO, "свой ключ"]]) {
  const p = await U.page(who, { w: 1440, h: 1000 });
  await p.goto(U.UI + "/create", { waitUntil: "networkidle0" });
  await sleep(600);
  await U.setInput(p, "textarea", body.seed).catch(() => {});
  await p.waitForSelector('[data-testid="cost-estimate"]', { timeout: 15000 }).catch(() => {});
  await p.waitForFunction(() => !/оценка…/.test(document.querySelector('[data-testid="cost-estimate"]')?.innerText ?? "оценка…"), { timeout: 15000 }).catch(() => {});
  const t = await p.$eval('[data-testid="cost-estimate"]', (e) => e.innerText).catch(() => "—");
  console.log("форма", label, "→", t);
  await p.close();
}

// пауза: обрыв посреди «Тезисов» у трёх плательщиков
async function pausedFor(who) {
  await U.simReset();
  await U.sim({ stream: { chunk: 6000, intervalMs: 0 }, rules: [{ match: "theses", action: "cut", times: 6, fraction: 0.55 }] });
  const r = await who.api("POST", "/syntheses", body);
  const id = r.json.id;
  await waitStatus(id, (s) => s === "paused" || s === "ready" || s === "error", 180000);
  await U.simReset();
  return id;
}
for (const [who, name, cap] of [
  [BYO, "pause-byo", "Пауза при своём ключе: у каждой кнопки полная цена выбора, строка «оставшиеся разделы», подсказка без ложного «дешевле»"],
  [BAL, "pause-balance", "Пауза при оплате с баланса: обрыв — сбой API, доработка без списания"],
  [SUB, "pause-sub", "Пауза у подписчика: доработка без списания кредитов"],
]) {
  const id = await pausedFor(who);
  const p = await U.page(who, { w: 1440, h: 1000 });
  await p.goto(U.UI + "/synthesis/" + id, { waitUntil: "networkidle0" });
  await p.waitForSelector(".pause-modal", { timeout: 20000 }).catch(() => {});
  await sleep(1200);
  await U.shot(p, name, cap, { el: ".pause-modal" });
  console.log(name, (await p.$eval(".pause-modal", (e) => e.innerText).catch(() => "нет модалки")).replace(/\n+/g, " ¶ ").slice(0, 1400));
  console.log("errors", p.errors);
  await p.close();
}

// страница биллинга подписчика: остаток кредитов и тарифы
{
  const p = await U.page(SUB, { w: 1440, h: 1400 });
  await p.goto(U.UI + "/billing", { waitUntil: "networkidle0" });
  await sleep(800);
  await U.shot(p, "billing-sub", "Биллинг подписчика: остаток кредитов", { el: '[data-testid="billing-subscription"]' });
  await p.close();
}
await U.close(); await sql.end();
