// Браузерная оснастка стенда: Chrome 131 + puppeteer-core, снимки в shots/
import puppeteer from "puppeteer-core";
import { homedir } from "node:os";
import { writeFileSync, mkdirSync } from "node:fs";
export const UI = "http://127.0.0.1:5300";
export const SIM = "http://127.0.0.1:3927";
const CHROME = `${homedir()}/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome`;
export const SHOTS = "/home/claude/lab/shots";
mkdirSync(SHOTS, { recursive: true });
export const shotList = [];
let browser;
export async function launch() {
  browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--lang=ru-RU", "--disable-dev-shm-usage", "--font-render-hinting=none"] });
  return browser;
}
export async function close() { await browser?.close(); }
export async function page(who, { w = 1440, h = 900 } = {}) {
  const ctx = await browser.createBrowserContext();
  const p = await ctx.newPage();
  await p.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
  p.errors = []; p.on("pageerror", (e) => p.errors.push(String(e)));
  p.on("dialog", (d) => { p.lastDialog = d.message(); d.accept(); });
  await p.setExtraHTTPHeaders({ "Accept-Language": "ru-RU,ru;q=0.9" });
  if (who) { const [n, v] = who.cookie.split("="); await p.setCookie({ name: n, value: v, url: UI }); }
  return p;
}
let seq = 0;
export async function shot(p, name, caption, opts = {}) {
  const file = `${String(++seq).padStart(2, "0")}-${name}.png`;
  await new Promise((r) => setTimeout(r, opts.settle ?? 400));
  if (opts.el) { const el = typeof opts.el === "string" ? await p.$(opts.el) : opts.el; if (el) await el.screenshot({ path: `${SHOTS}/${file}` }); else await p.screenshot({ path: `${SHOTS}/${file}` }); }
  else await p.screenshot({ path: `${SHOTS}/${file}`, fullPage: !!opts.full });
  shotList.push({ file, caption, scenario: opts.scenario ?? globalThis.SCENARIO });
  writeFileSync(`${SHOTS}/index.json`, JSON.stringify(shotList, null, 1));
  console.log("  📸", file, "—", caption);
  return file;
}
/** Клик по видимому элементу с текстом (button/a/[role=tab]/label/summary/li) */
export async function clickText(p, text, { sel = "button, a, [role=tab], [role=button], label, summary, li, span, div", exact = false, nth = 0 } = {}) {
  const ok = await p.evaluate((text, sel, exact, nth) => {
    const els = [...document.querySelectorAll(sel)].filter((e) => {
      const t = (e.innerText ?? e.textContent ?? "").trim();
      const r = e.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && (exact ? t === text : t.includes(text));
    });
    // самый «глубокий» подходящий элемент
    const leaf = els.filter((e) => !els.some((o) => o !== e && e.contains(o)));
    const el = leaf[nth] ?? els[nth];
    if (!el) return false;
    el.scrollIntoView({ block: "center" }); el.click(); return true;
  }, text, sel, exact, nth);
  if (!ok) throw new Error(`нет элемента с текстом «${text}»`);
  await new Promise((r) => setTimeout(r, 250));
}
export async function hasText(p, text) { return p.evaluate((t) => document.body.innerText.includes(t), text); }
export async function waitText(p, text, ms = 30000) {
  await p.waitForFunction((t) => document.body.innerText.includes(t), { timeout: ms }, text);
}
export async function sim(cfg) { return (await fetch(SIM + "/__control", { method: "POST", body: JSON.stringify(cfg) })).json(); }
export async function simReset() { return (await fetch(SIM + "/__reset", { method: "POST" })).json(); }
export async function simLog() { return (await fetch(SIM + "/__log")).json(); }
export async function setInput(p, selector, value) {
  await p.evaluate((s, v) => {
    const el = typeof s === "string" ? document.querySelector(s) : s;
    const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, "value").set.call(el, v);
    el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true }));
  }, selector, value);
}
