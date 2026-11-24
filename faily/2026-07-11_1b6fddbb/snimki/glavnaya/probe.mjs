import puppeteer from "puppeteer-core";

const CHROME = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";
const URL = "file:///mnt/user-data/uploads/complex-atlas.html";

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: "new",
  args: [
    "--no-sandbox", "--disable-setuid-sandbox",
    "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
    "--disable-dev-shm-usage", "--window-size=1400,900",
  ],
});
const page = await browser.newPage();
await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 1 });

const errs = [];
page.on("pageerror", (e) => errs.push("pageerror: " + e.message));
page.on("console", (m) => { if (m.type() === "error") errs.push("console.error: " + m.text()); });

await page.goto(URL, { waitUntil: "load", timeout: 60000 });
await new Promise((r) => setTimeout(r, 800)); // let boot + setMode settle

// In-page describer: summarize interactive controls inside a container.
const describe = (sel) =>
  page.evaluate((sel) => {
    const root = document.querySelector(sel);
    if (!root) return { missing: sel };
    const out = [];
    const seenSeg = new Set();
    root.querySelectorAll("button, select, input, textarea").forEach((el) => {
      const tag = el.tagName.toLowerCase();
      // label: nearest preceding .row label / text
      const labOf = (e) => {
        let n = e;
        for (let i = 0; i < 4 && n; i++) {
          n = n.parentElement;
          if (!n) break;
          const lab = n.querySelector(":scope > .lab, :scope > label, :scope > .row-label, :scope > .name");
          if (lab && lab.textContent.trim()) return lab.textContent.trim();
        }
        return "";
      };
      if (tag === "select") {
        out.push({
          kind: "select",
          label: labOf(el) || el.title || "",
          value: el.value,
          options: [...el.options].map((o) => o.textContent.trim() + (o.value !== o.textContent.trim() ? " {" + o.value + "}" : "")),
        });
      } else if (tag === "input") {
        const t = el.type;
        if (t === "range") {
          out.push({ kind: "slider", label: labOf(el) || el.title || el.getAttribute("aria-label") || "", min: el.min, max: el.max, step: el.step, value: el.value });
        } else if (t === "checkbox" || t === "radio") {
          out.push({ kind: t, label: labOf(el) || el.title || el.nextSibling?.textContent?.trim() || "", checked: el.checked });
        } else {
          out.push({ kind: "input(" + t + ")", label: labOf(el) || el.placeholder || el.title || "", value: el.value });
        }
      } else if (tag === "textarea") {
        out.push({ kind: "textarea", label: labOf(el) || el.placeholder || "", value: el.value.slice(0, 60) });
      } else { // button
        const txt = (el.textContent || "").replace(/\s+/g, " ").trim();
        // group segmented buttons (data-mode-independent): collapse buttons that share a parent .seg
        const segParent = el.closest(".seg, [role='tablist'], .segmented");
        if (segParent && segParent !== root) {
          const key = "seg:" + [...segParent.children].indexOf(el.parentElement) + ":" + (labOf(el) || "");
          const gid = segParent;
          if (!seenSeg.has(gid)) {
            seenSeg.add(gid);
            const opts = [...segParent.querySelectorAll("button")].map((b) => {
              const bt = b.textContent.replace(/\s+/g, " ").trim();
              const on = b.getAttribute("aria-selected") === "true" || b.getAttribute("aria-pressed") === "true" || b.classList.contains("on") || b.classList.contains("active");
              return bt + (on ? " ◄" : "");
            });
            out.push({ kind: "segmented", label: labOf(el) || "", options: opts });
          }
        } else {
          const on = el.getAttribute("aria-pressed") === "true" || el.classList.contains("on");
          out.push({ kind: "button", text: txt, title: el.title || "", pressed: on || undefined });
        }
      }
    });
    return { count: out.length, controls: out };
  }, sel);

const modes = ["phase", "analysis", "conformal", "fractal", "sphere", "surface", "compare"];
const report = { boot_errors: errs.slice(0, 20), modes: {} };

for (const m of modes) {
  await page.click(`.mode-tab[data-mode="${m}"]`);
  await new Promise((r) => setTimeout(r, 350));
  const modeName = await page.$eval("#mode-name", (e) => e.textContent.trim()).catch(() => "");
  const hint = await page.$eval("#hint", (e) => e.textContent.trim()).catch(() => "");
  report.modes[m] = {
    modeName, hint,
    formulaBar: await describe("#formula-bar"),
    panel: await describe("#panel"),
    toolbar: await describe("#stage-toolbar"),
  };
}

// Settings drawer
await page.click("#btn-settings");
await new Promise((r) => setTimeout(r, 300));
report.settings = await describe("#settings-drawer");

// Templates popover (open from phase mode)
await page.click(`.mode-tab[data-mode="phase"]`);
await new Promise((r) => setTimeout(r, 250));
const tmplCats = await page.evaluate(() => {
  const btn = document.querySelector("#btn-templates");
  if (!btn) return null;
  btn.click();
  const pop = document.querySelector("#templates-pop");
  if (!pop) return null;
  // categories
  const cats = [...pop.querySelectorAll("*")].filter((e) => e.children.length === 0 && /[а-яё]/i.test(e.textContent) && e.textContent.length < 40);
  return {
    catButtons: [...pop.querySelectorAll("button")].slice(0, 60).map((b) => b.textContent.replace(/\s+/g, " ").trim()).filter(Boolean),
  };
});
report.templatesPopover = tmplCats;

// current hash after interaction
report.currentHash = await page.evaluate(() => location.hash.slice(0, 120));

console.log(JSON.stringify(report, null, 2));
await browser.close();
