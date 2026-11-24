import puppeteer from "puppeteer-core";
const CHROME = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";
const URL = "file:///mnt/user-data/uploads/complex-atlas.html";
const b = await puppeteer.launch({
  executablePath: CHROME, headless: "new",
  args: ["--no-sandbox","--disable-setuid-sandbox","--use-gl=swiftshader","--enable-unsafe-swiftshader","--disable-dev-shm-usage","--window-size=1400,900"],
});
const page = await b.newPage();
await page.setViewport({ width: 1400, height: 900 });
await page.goto(URL, { waitUntil: "load" });
await new Promise(r=>setTimeout(r,700));

// --- Path 1: DOM — set formula via the text input, pick checker scheme, read back state via UI/hash ---
async function setFormula(expr){
  await page.$eval("#formula-bar input[type=text]", (el,v)=>{
    el.value=v;
    el.dispatchEvent(new Event("input",{bubbles:true}));
    el.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true}));
    el.blur();
    el.dispatchEvent(new Event("change",{bubbles:true}));
  }, expr);
  await new Promise(r=>setTimeout(r,500));
}
async function setScheme(val){
  // toolbar color select
  const ok = await page.evaluate((v)=>{
    const sels=[...document.querySelectorAll("#stage-toolbar select")];
    const s=sels.find(s=>[...s.options].some(o=>o.value===v));
    if(!s) return false;
    s.value=v; s.dispatchEvent(new Event("change",{bubbles:true})); return true;
  }, val);
  await new Promise(r=>setTimeout(r,500));
  return ok;
}
await setFormula("z^3 - 1");
const schemeOk = await setScheme("checker-cart");
const roZ = await page.$eval("#ro-fz",e=>e.textContent).catch(()=>"");
const hash1 = await page.evaluate(()=>location.hash.slice(0,60));
// decode hash to confirm expr propagated
const decoded1 = await page.evaluate(()=>{
  const m=location.hash.match(/s=([^&]+)/); if(!m) return null;
  try{return JSON.parse(decodeURIComponent(escape(atob(m[1]))));}catch(e){return "decode-fail";}
});
await page.screenshot({ path:"/home/claude/shot_dom.png" });

// --- Path 2: URL hash — build a state object, base64 it, reload, confirm it applies ---
const target = { expr: "sin(z)/z", mode:"phase", scheme:"phase", branchK:0,
  color:{density:6,falloff:0.4,classicK:1,spokes:12,contrast:2,mono:false},
  view:{cx:0,cy:0,scale:6/1024} };
const hashPayload = await page.evaluate((o)=> "s="+btoa(unescape(encodeURIComponent(JSON.stringify(o)))), target);
await page.goto(URL + "#" + hashPayload, { waitUntil:"load" });
await new Promise(r=>setTimeout(r,800));
const appliedExpr = await page.$eval("#formula-bar input[type=text]", e=>e.value).catch(()=>"(no input)");
const appliedScheme = await page.evaluate(()=>{
  const s=[...document.querySelectorAll("#stage-toolbar select")].find(s=>[...s.options].some(o=>o.value==="phase"));
  return s ? s.value : "(n/a)";
});
await page.screenshot({ path:"/home/claude/shot_hash.png" });

console.log(JSON.stringify({
  path1_DOM: { schemeApplied: schemeOk, f_at_probe_default: roZ, hashPrefix: hash1, decodedExpr: decoded1 && decoded1.expr, decodedScheme: decoded1 && decoded1.scheme },
  path2_HASH: { requestedExpr: target.expr, appliedExpr, appliedScheme }
}, null, 2));
await b.close();
