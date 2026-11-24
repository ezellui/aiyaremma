const puppeteer = require('puppeteer');
const path = require('path');
const exe = '/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const file = 'file://' + path.resolve(process.argv[2]);
const shotBase = process.argv[3] || '/tmp/wl';
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

  // активировать сферу через кнопку сцены
  await p.evaluate(()=>{ const el=document.querySelector('[data-m2="sphere"]'); el && el.click(); });
  await wait(1000);
  const s0 = await p.evaluate(()=>({ model:__t.model, planet:__t.planet, ready:__t.ready, sea:__t.sea, land:__t.landPct(), N:__t.N }));

  // ползунок уровня моря: затопить (+300 м = 0.0333) и осушить (-500 м = -0.0556)
  async function setSea(v){ await p.evaluate(v=>{ const s=document.getElementById('sSea'); s.value=v; s.dispatchEvent(new Event('input',{bubbles:true})); }, v); await wait(200); return p.evaluate(()=>__t.landPct()); }
  const landFlood = await setSea(0.0333);
  const landDrain = await setSea(-0.0556);
  await setSea(0);
  await wait(400);
  await p.screenshot({ path: shotBase+'_earth.png' });

  // Марс через кнопку
  await p.evaluate(()=>{ const el=document.querySelector('[data-pl="mars"]'); el && el.click(); });
  await wait(1000);
  const mars = await p.evaluate(()=>({ planet:__t.planet, sea:__t.sea, land:__t.landPct() }));
  // залить Марс до -300 м (норм -300/8000=-0.0375) чтобы появилась вода
  await p.evaluate(()=>{ const s=document.getElementById('sSea'); s.value=-0.0375; s.dispatchEvent(new Event('input',{bubbles:true})); });
  await wait(400);
  const marsFlood = await p.evaluate(()=>__t.landPct());
  await p.screenshot({ path: shotBase+'_mars.png' });

  await b.close();
  console.log(JSON.stringify({ s0, landFlood, landDrain, mars, marsFlood, errors }, null, 2));
  if (errors.length) process.exit(2);
})().catch(e=>{ console.error('FATAL', e.message); process.exit(1); });
