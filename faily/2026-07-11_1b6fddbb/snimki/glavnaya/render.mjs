import puppeteer from "puppeteer-core";
import fs from "fs";

const CHROME = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";
const URL = "file:///mnt/user-data/uploads/complex-atlas.html";
const OUT = "/mnt/user-data/outputs";
fs.mkdirSync(OUT, { recursive: true });

const EXPR = "1/wp(z - round((re(z)+im(z))/2)*(1+i) - round((re(z)-im(z))/2)*(1-i), -47.26818, 0)";

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

// Ensure portrait mode + classic scheme (both default, set explicitly to be safe)
await page.click('.mode-tab[data-mode="phase"]');
await new Promise((r) => setTimeout(r, 300));
await page.evaluate(() => {
  const s = [...document.querySelectorAll("#stage-toolbar select")].find(s => [...s.options].some(o => o.value === "classic"));
  if (s) { s.value = "classic"; s.dispatchEvent(new Event("change", { bubbles: true })); }
});

// Force CPU render path (reliable for custom special functions) via settings drawer
await page.click("#btn-settings");
await new Promise((r) => setTimeout(r, 300));
const cpuClicked = await page.evaluate(() => {
  const btns = [...document.querySelectorAll("#settings-drawer button")];
  const cpu = btns.find(x => /^CPU$/.test(x.textContent.trim()));
  if (cpu) { cpu.click(); return true; }
  return false;
});
await new Promise((r) => setTimeout(r, 200));
// close settings
await page.keyboard.press("Escape");
await new Promise((r) => setTimeout(r, 250));

// Set the formula
await page.$eval("#formula-bar input[type=text]", (el, v) => {
  el.value = v;
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
  el.blur();
  el.dispatchEvent(new Event("change", { bubbles: true }));
}, EXPR);

// Poll until the canvas render settles (signature stable) or timeout
const sig = () => page.evaluate(() => {
  const cv = document.querySelector("#cv-phase");
  if (!cv || !cv.width) return { w: 0, s: -1, v: 0 };
  const g = cv.getContext("2d") || cv.getContext("webgl") ? cv.getContext("2d") : null;
  // Use a downscaled 2d snapshot to compute a signature + variance (works even if source is webgl-backed via drawImage)
  const tmp = document.createElement("canvas"); tmp.width = 64; tmp.height = 64;
  const tc = tmp.getContext("2d");
  tc.drawImage(cv, 0, 0, 64, 64);
  const d = tc.getImageData(0, 0, 64, 64).data;
  let s = 0, sum = 0, sum2 = 0, n = 0;
  for (let i = 0; i < d.length; i += 4) {
    const lum = 0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2];
    s = (s + lum * (i + 1)) % 1e12;
    sum += lum; sum2 += lum*lum; n++;
  }
  const mean = sum/n, varc = sum2/n - mean*mean;
  return { w: cv.width, h: cv.height, s: Math.round(s), v: Math.round(varc) };
});

let prev = null, stable = 0, last = null;
const t0 = Date.now();
while (Date.now() - t0 < 70000) {
  await new Promise((r) => setTimeout(r, 1500));
  const cur = await sig();
  last = cur;
  if (prev && cur.s === prev.s && cur.w === prev.w) { stable++; if (stable >= 2) break; }
  else stable = 0;
  prev = cur;
}

// Probe f at known nodes via readout by simulating pointer over the canvas center-mapped coords?
// Simpler: read back state.expr indirectly through hash, and confirm no compile error text is shown.
const info = await page.evaluate(() => {
  const cv = document.querySelector("#cv-phase");
  const errEl = document.querySelector("#formula-bar .err, #formula-bar .error, .fb-fn .err");
  const inputVal = document.querySelector("#formula-bar input[type=text]")?.value || "";
  return {
    canvasW: cv?.width, canvasH: cv?.height,
    inputVal,
    errText: errEl ? errEl.textContent.trim() : null,
    hash: location.hash.slice(0, 40),
  };
});

// Export PNG exactly as the app's PNG button does: canvas.toDataURL("image/png")
const dataUrl = await page.$eval("#cv-phase", (cv) => cv.toDataURL("image/png"));
const b64 = dataUrl.split(",")[1];
const pngPath = OUT + "/checkerboard_portrait.png";
fs.writeFileSync(pngPath, Buffer.from(b64, "base64"));

// Also capture a full-window screenshot for context (UI + canvas)
await page.screenshot({ path: OUT + "/checkerboard_ui.png" });

console.log(JSON.stringify({
  boot_errors: errs, cpuClicked, renderSettleSig: last, info,
  pngBytes: fs.statSync(pngPath).size,
}, null, 2));
await b.close();
