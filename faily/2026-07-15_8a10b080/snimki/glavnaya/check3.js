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
  await p.evaluate(()=>{ document.querySelector('[data-m2="sphere"]').click(); });
  await wait(900);

  // все 5 планет
  const planets = ['earth','mars','moon','venus','mercury'];
  const rows = {};
  for (const name of planets) {
    await p.evaluate(n=>{ document.querySelector(`[data-pl="${n}"]`).click(); }, name);
    await wait(950);
    rows[name] = await p.evaluate(()=>({ ready:__t.ready, planet:__t.planet, sea:__t.sea, land:__t.landPct() }));
    await p.screenshot({ path: `/tmp/pl_${name}.png` });
  }

  // вернуться на Землю, уровень моря 0
  await p.evaluate(()=>{ document.querySelector('[data-pl="earth"]').click(); });
  await wait(900);

  // импакт-режим: включить
  await p.evaluate(()=>{ document.getElementById('bImpact').click(); });
  await wait(100);
  const impOn = await p.evaluate(()=>__t.impactMode);

  // перейти в 3D
  await p.evaluate(()=>{ __t.setMode3(); });
  await wait(700);
  const in3d = await p.evaluate(()=>__t.mode);

  // клик по центру глобуса (pointerdown+up без движения) -> удар через рейкаст
  const errBefore = errors.length;
  await p.evaluate(()=>{
    const gl = document.getElementById('gl');
    const r = gl.getBoundingClientRect();
    const cx = r.left + r.width*0.5, cy = r.top + r.height*0.5;
    const opt = b => ({ bubbles:true, cancelable:true, clientX:cx, clientY:cy, pointerId:1, pointerType:'mouse', button:0, buttons:b });
    gl.dispatchEvent(new PointerEvent('pointerdown', opt(1)));
    gl.dispatchEvent(new PointerEvent('pointerup',   opt(0)));
  });
  await wait(300);
  await p.screenshot({ path: '/tmp/impact_3d.png' });
  const errAfterClick = errors.length - errBefore;

  await b.close();
  console.log(JSON.stringify({ rows, impOn, in3d, errAfterClick, errors }, null, 2));
  if (errors.length) process.exit(2);
})().catch(e=>{ console.error('FATAL', e.message); process.exit(1); });
