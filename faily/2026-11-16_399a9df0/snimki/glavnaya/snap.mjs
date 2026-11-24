// Снимок вычисленных стилей всех элементов (и ::before/::after) в наборе состояний интерфейса.
// node snap.mjs <tag>  → /home/claude/lab/css/snap-<tag>.json
import { account, sql, sleep } from "../api.mjs";
import * as U from "../ui.mjs";
import { writeFileSync } from "node:fs";
const tag = process.argv[2] ?? "before";
const TARGETS = ["gm-panel-edit-row", "element-summary", "element-delete", "subsection-delete", "discuss-beside", "discuss-compose", "similar-note", "similar-reason-key", "similar-list", "plan-field-row", "members-invite-row", "amount-choice", "app-lang-choice", "genealogy-descendants"];
const A = await account("author@lab.local", "password-lab", "Автор стенда");
await sql`update users set role='admin' where id=${A.id}`;
const ids = Object.fromEntries((await sql`select k, v from lab_ids`).map((r) => [r.k, r.v]));
await U.launch();
const out = {};
async function snap(p, name) {
  await sleep(700);
  const r = await p.evaluate((targets) => {
    const res = {}; const all = document.querySelectorAll("body *");
    const path = (e) => { const a = []; for (; e && e !== document.body; e = e.parentElement) a.unshift(e.tagName + ":" + [...e.parentElement.children].indexOf(e)); return a.join("/"); };
    for (const e of all) {
      const k = path(e);
      for (const pseudo of [null, "::before", "::after"]) {
        const cs = getComputedStyle(e, pseudo);
        if (pseudo && (cs.content === "none" || cs.content === "normal")) continue;
        const o = {}; for (let i = 0; i < cs.length; i++) { const n = cs[i]; o[n] = cs.getPropertyValue(n); }
        res[k + (pseudo ?? "")] = o;
      }
    }
    const cover = Object.fromEntries(targets.map((t) => [t, document.querySelectorAll("." + t).length]));
    return { res, cover };
  }, TARGETS);
  out[name] = r.res;
  console.log(name, Object.keys(r.res).length, "узлов;", Object.entries(r.cover).filter(([, n]) => n).map(([t, n]) => `${t}×${n}`).join(" "));
}
const step = async (name, fn) => { try { await fn(); } catch (e) { console.log("  ! шаг", name, String(e).slice(0, 120)); } };
const p = await U.page(A);
// 1. мета-синтез: древо в шапке, ссылка потомков, похожие внизу
await p.goto(U.UI + "/synthesis/" + ids.s6, { waitUntil: "networkidle0" }); await sleep(1500);
await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); await sleep(800);
await snap(p, "meta-page");
// 2. обсуждение подраздела (панель с полем ввода)
await step("discuss", async () => {
  await p.goto(U.UI + "/synthesis/" + ids.s2, { waitUntil: "networkidle0" }); await sleep(800);
  await p.evaluate(() => { const b = [...document.querySelectorAll("button")].filter((b) => b.innerText.trim() === "◉")[2]; b?.scrollIntoView({ block: "center" }); b?.click(); }); await sleep(1200);
  await snap(p, "discuss");
});
// 3. вкладка участников
await step("members", async () => {
  await p.goto(U.UI + "/synthesis/" + ids.s2, { waitUntil: "networkidle0" }); await sleep(800);
  await p.evaluate(() => document.querySelector('[data-testid="tab-members"]')?.click()); await sleep(1200);
  await snap(p, "members");
});
// 4. правка подраздела по месту → шаг удаления
await step("subsection", async () => {
  await p.goto(U.UI + "/synthesis/" + ids.s1, { waitUntil: "networkidle0" }); await sleep(1000);
  await p.evaluate(() => { const b = document.querySelector(".subsection-edit-btn"); b?.scrollIntoView({ block: "center" }); b?.click(); }); await sleep(1500);
  await snap(p, "subsection-edit");
  await p.evaluate(() => document.querySelector('[data-testid="subsection-delete"]')?.click()); await sleep(800);
  await snap(p, "subsection-delete");
});
// 5. граф: карточка узла и редактор категории
await step("graph", async () => {
  await p.goto(U.UI + "/synthesis/" + ids.s1, { waitUntil: "networkidle0" }); await sleep(800);
  await U.clickText(p, "◈ Граф", { sel: "button" }); await sleep(2500);
  await U.clickText(p, "2D", { sel: "button", exact: true }); await sleep(3500);
  await p.mouse.click(812, 403); await sleep(1200);
  await snap(p, "graph-node");
  await U.clickText(p, "✎ Редактировать", { sel: "button" }); await sleep(1500);
  await snap(p, "category-editor");
});
// 6. биллинг, профиль, админка тарифов
await step("billing", async () => { await p.goto(U.UI + "/billing", { waitUntil: "networkidle0" }); await sleep(1000); await snap(p, "billing"); });
await step("profile", async () => { await p.goto(U.UI + "/profile", { waitUntil: "networkidle0" }); await sleep(1000); await snap(p, "profile"); });
await step("admin", async () => {
  await p.goto(U.UI + "/admin/prompts", { waitUntil: "networkidle0" }); await sleep(1000);
  await U.clickText(p, "Тариф", { sel: "button, [role=tab], a" }).catch(() => {}); await sleep(1200);
  await snap(p, "admin");
});
writeFileSync(`/home/claude/lab/css/snap-${tag}.json`, JSON.stringify(out));
await U.close(); await sql.end();
