import puppeteer from "puppeteer-core";
import fs from "fs";

const CHROME = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";
const URL = "file:///mnt/user-data/uploads/complex-atlas.html";
const OUT = "/mnt/user-data/outputs";

const RE = "sin(pi*x)*cos(pi*y)/(1+cos(pi*x)*cos(pi*y))";
const IM = "-sin(pi*y)/(1+cos(pi*x)*cos(pi*y))";

const b = await puppeteer.launch({
  executablePath: CHROME, headless: "new",
  args: ["--no-sandbox","--disable-setuid-sandbox","--use-gl=swiftshader","--enable-unsafe-swiftshader","--disable-dev-shm-usage","--window-size=1400,1200"],
});
const page = await b.newPage();
await page.setViewport({ width: 1400, height: 1200, deviceScaleFactor: 1 });
const errs = [];
page.on("pageerror", (e) => errs.push("pageerror: " + e.message));
await page.goto(URL, { waitUntil: "load", timeout: 60000 });
await new Promise((r) => setTimeout(r, 700));

// portrait + classic
await page.click('.mode-tab[data-mode="phase"]');
await new Promise((r) => setTimeout(r, 250));
await page.evaluate(() => {
  const s = [...document.querySelectorAll("#stage-toolbar select")].find(s => [...s.options].some(o => o.value === "classic"));
  if (s) { s.value = "classic"; s.dispatchEvent(new Event("change", { bubbles: true })); }
});

// switch to Re/Im(x,y): click the segment button with that label
const switched = await page.evaluate(() => {
  const btns = [...document.querySelectorAll("#formula-bar button")];
  const b = btns.find(x => /Re\/Im/.test(x.textContent));
  if (b) { b.click(); return true; }
  return false;
});
await new Promise((r) => setTimeout(r, 400));

// fill the two inputs (reI first, imI second)
const filled = await page.evaluate(({ re, im }) => {
  const ins = [...document.querySelectorAll("#formula-bar input[type=text]")];
  if (ins.length < 2) return { ok: false, n: ins.length };
  const set = (el, v) => {
    el.value = v;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  };
  set(ins[0], re);
  set(ins[1], im);
  return { ok: true, n: ins.length, v0: ins[0].value, v1: ins[1].value };
}, { re: RE, im: IM });

// poll until render settles
const sig = () => page.evaluate(() => {
  const cv = document.querySelector("#cv-phase");
  if (!cv || !cv.width) return { w: 0, s: -1 };
  const tmp = document.createElement("canvas"); tmp.width = 64; tmp.height = 64;
  const tc = tmp.getContext("2d"); tc.drawImage(cv, 0, 0, 64, 64);
  const d = tc.getImageData(0, 0, 64, 64).data;
  let s = 0;
  for (let i = 0; i < d.length; i += 4) { const l = 0.299*d[i]+0.587*d[i+1]+0.114*d[i+2]; s = (s + l*(i+1)) % 1e12; }
  return { w: cv.width, s: Math.round(s) };
});
let prev = null, stable = 0, last = null;
const t0 = Date.now();
while (Date.now() - t0 < 60000) {
  await new Promise((r) => setTimeout(r, 1400));
  const cur = await sig(); last = cur;
  if (prev && cur.s === prev.s && cur.w === prev.w) { stable++; if (stable >= 2) break; } else stable = 0;
  prev = cur;
}

const info = await page.evaluate(() => {
  const err = document.querySelector("#formula-bar .err");
  const ins = [...document.querySelectorAll("#formula-bar input[type=text]")].map(i => i.value);
  const cv = document.querySelector("#cv-phase");
  return { errText: err ? err.textContent.trim() : null, inputs: ins, w: cv?.width, h: cv?.height, hash: location.hash.slice(0, 30) };
});

const dataUrl = await page.$eval("#cv-phase", (cv) => cv.toDataURL("image/png"));
const pngPath = OUT + "/checkerboard_reim.png";
fs.writeFileSync(pngPath, Buffer.from(dataUrl.split(",")[1], "base64"));
await page.screenshot({ path: OUT + "/checkerboard_reim_ui.png" });

console.log(JSON.stringify({ boot_errors: errs, switched, filled, renderSettle: last, info, pngBytes: fs.statSync(pngPath).size }, null, 2));
await b.close();
