const puppeteer = require('puppeteer');
const path = require('path');
const exe = '/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const file = 'file://' + path.resolve(process.argv[2]);
const wait = ms => new Promise(r=>setTimeout(r,ms));
const vis = sel => `(getComputedStyle(document.querySelector('${sel}')).display)`;

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

  // --- ЛУЧИ ---
  await p.evaluate(()=>document.querySelector('[data-m2="ray"]').click());
  await wait(500);
  const ray = await p.evaluate(()=>({
    rayParamsVis: getComputedStyle(document.getElementById('rayParams')).display,
    rdeParamsVis: getComputedStyle(document.getElementById('rdeParams')).display,
    shapeOn: document.querySelector('#rayShapeSeg .on')?.dataset.rs,
    shapeCount: document.querySelectorAll('#rayShapeSeg button').length
  }));
  // сменить форму: круг
  await p.evaluate(()=>document.querySelector('#rayShapeSeg [data-rs="circle"]').click());
  await wait(400);
  const rayAfter = await p.evaluate(()=>({ shapeOn: document.querySelector('#rayShapeSeg .on')?.dataset.rs }));
  await p.screenshot({ path: '/tmp/ray_circle.png' });
  // сменить на Синай
  await p.evaluate(()=>document.querySelector('#rayShapeSeg [data-rs="sinai"]').click());
  await wait(400);
  const raySinai = await p.evaluate(()=>({ shapeOn: document.querySelector('#rayShapeSeg .on')?.dataset.rs }));
  await p.screenshot({ path: '/tmp/ray_sinai.png' });

  // --- ЧАСТИЦЫ ---
  await p.evaluate(()=>document.querySelector('[data-m2="part"]').click());
  await wait(600);
  const part = await p.evaluate(()=>({
    partParamsVis: getComputedStyle(document.getElementById('partParams')).display,
    sceneOn: document.querySelector('#ptSceneSeg .on')?.dataset.ps,
    sceneCount: document.querySelectorAll('#ptSceneSeg button').length,
    interCount: document.querySelectorAll('#ptInterSeg button').length
  }));
  // сменить сцену частиц: кристалл
  await p.evaluate(()=>document.querySelector('#ptSceneSeg [data-ps="crystal"]').click());
  await wait(500);
  const partCrystal = await p.evaluate(()=>({ sceneOn: document.querySelector('#ptSceneSeg .on')?.dataset.ps }));
  await p.screenshot({ path: '/tmp/part_crystal.png' });
  // стая (должна открыть ptVicParams)
  await p.evaluate(()=>document.querySelector('#ptSceneSeg [data-ps="flock"]').click());
  await wait(500);
  const partFlock = await p.evaluate(()=>({
    sceneOn: document.querySelector('#ptSceneSeg .on')?.dataset.ps,
    vicVis: getComputedStyle(document.getElementById('ptVicParams')).display
  }));
  await p.screenshot({ path: '/tmp/part_flock.png' });

  await b.close();
  console.log(JSON.stringify({ ray, rayAfter, raySinai, part, partCrystal, partFlock, errors }, null, 2));
  if (errors.length) process.exit(2);
})().catch(e=>{ console.error('FATAL', e.message); process.exit(1); });
