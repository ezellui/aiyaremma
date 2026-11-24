const puppeteer = require('puppeteer');
const path = require('path');
const exe = '/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const file = 'file://' + path.resolve(process.argv[2]);
const wait = ms => new Promise(r=>setTimeout(r,ms));

(async () => {
  const errors = [];
  const b = await puppeteer.launch({ executablePath: exe, headless: 'new',
    args: ['--no-sandbox','--allow-file-access-from-files','--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1400, height: 900 });
  p.on('console', m => { if (m.type()==='error') errors.push('[err] '+m.text()); });
  p.on('pageerror', e => errors.push('[pageerr] '+e.message));
  await p.goto(file, { waitUntil: 'load' });
  await wait(300);

  // --- регрессия: обычная сфера всё ещё работает ---
  await p.evaluate(()=>document.querySelector('[data-m2="sphere"]').click());
  await wait(900);
  const sph = await p.evaluate(()=>({ model:__t.model, panelVis:__t.panelVis, land:__t.landPct(), ready:__t.ready }));

  // пресеты на сфере
  async function preset(cmd){ await p.evaluate(c=>{ document.querySelector(`#seaPresets [data-sea="${c}"]`).click(); }, cmd); await wait(250); return p.evaluate(()=>({ land:__t.landPct(), sea:__t.sea, label:__t.seaLabel() })); }
  const pMinus = await preset('-100');
  const pPlus  = await preset('+100');
  const pMax   = await preset('max');
  const pReset = await preset('reset');

  // --- мелкая вода на сфере ---
  await p.evaluate(()=>document.querySelector('[data-m2="swater"]').click());
  await wait(500);
  const swFlat = await p.evaluate(()=>({ model:__t.model, swSphere:__t.swSphere, panelVis:__t.panelVis }));
  // включить геометрию сферы
  await p.evaluate(()=>document.getElementById('bSwSph').click());
  await wait(1000);
  const swSph = await p.evaluate(()=>({ swSphere:__t.swSphere, panelVis:__t.panelVis, planet:__t.planet, land:__t.landPct(), water:__t.waterPct() }));
  // двигаем уровень моря в swater+swSphere
  await p.evaluate(()=>{ const s=document.getElementById('sSea'); s.value=0.05; s.dispatchEvent(new Event('input',{bubbles:true})); });
  await wait(300);
  const swFlood = await p.evaluate(()=>({ land:__t.landPct(), water:__t.waterPct() }));
  await p.evaluate(()=>{ const s=document.getElementById('sSea'); s.value=-0.08; s.dispatchEvent(new Event('input',{bubbles:true})); });
  await wait(300);
  const swDrain = await p.evaluate(()=>({ land:__t.landPct(), water:__t.waterPct() }));
  // смена планеты в swater+swSphere (Марс)
  await p.evaluate(()=>document.querySelector('[data-pl="mars"]').click());
  await wait(1000);
  const swMars = await p.evaluate(()=>({ planet:__t.planet, land:__t.landPct(), water:__t.waterPct() }));
  // однородный океан
  await p.evaluate(()=>document.querySelector('[data-pl="uniform"]').click());
  await wait(500);
  const swUniform = await p.evaluate(()=>({ planetMode:__t.planetMode, water:__t.waterPct() }));
  await p.screenshot({ path: '/tmp/sw_sphere.png' });

  await b.close();
  console.log(JSON.stringify({ sph, pMinus, pPlus, pMax, pReset, swFlat, swSph, swFlood, swDrain, swMars, swUniform, errors }, null, 2));
  if (errors.length) process.exit(2);
})().catch(e=>{ console.error('FATAL', e.message); process.exit(1); });
