const puppeteer = require('puppeteer');
const path = require('path');
const exe = '/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const file = 'file://' + path.resolve(process.argv[2] || 'out/wave_lab.html');
const shot = process.argv[3] || '/tmp/wl.png';

(async () => {
  const errors = [];
  const b = await puppeteer.launch({ executablePath: exe, headless: 'new',
    args: ['--no-sandbox','--allow-file-access-from-files','--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1400, height: 900, deviceScaleFactor: 1 });
  p.on('console', m => { if (m.type()==='error') errors.push('[console.error] '+m.text()); });
  p.on('pageerror', e => errors.push('[pageerror] '+e.message));
  await p.goto(file, { waitUntil: 'load' });
  await new Promise(r=>setTimeout(r,300));

  const api = await p.evaluate(()=>({ setModel:typeof setModel, setPlanet:typeof setPlanet, setSeaLevel:typeof setSeaLevel, PLANETS:typeof PLANETS!=='undefined'?Object.keys(PLANETS):null }));

  // включить сферу
  await p.evaluate(()=> setModel('sphere'));
  await new Promise(r=>setTimeout(r,800));   // ждём загрузку карт

  const s0 = await p.evaluate(()=>{
    let land=0; for(let k=0;k<N;k++) if(wall[k]) land++;
    return { ready:planetReady, planet:currentPlanet, sea:seaLevel, N, landPct:+(100*land/N).toFixed(1) };
  });

  // затопить +300 м на Земле (норм = 300/9000)
  await p.evaluate(()=> setSeaLevel(300/9000));
  await new Promise(r=>setTimeout(r,200));
  const sFlood = await p.evaluate(()=>{ let land=0; for(let k=0;k<N;k++) if(wall[k]) land++; return +(100*land/N).toFixed(1); });

  // осушить -500 м
  await p.evaluate(()=> setSeaLevel(-500/9000));
  await new Promise(r=>setTimeout(r,200));
  const sDrain = await p.evaluate(()=>{ let land=0; for(let k=0;k<N;k++) if(wall[k]) land++; return +(100*land/N).toFixed(1); });

  // вернуть 0, снять скрин Земли
  await p.evaluate(()=> setSeaLevel(0));
  await new Promise(r=>setTimeout(r,400));
  await p.screenshot({ path: shot });

  // Марс
  let mars=null;
  try {
    await p.evaluate(()=> setPlanet('mars'));
    await new Promise(r=>setTimeout(r,900));
    mars = await p.evaluate(()=>{ let land=0; for(let k=0;k<N;k++) if(wall[k]) land++;
      return { planet:currentPlanet, sea:seaLevel, landPct:+(100*land/N).toFixed(1) }; });
    await p.screenshot({ path: shot.replace('.png','_mars.png') });
  } catch(e){ errors.push('[mars] '+e.message); }

  await b.close();
  console.log(JSON.stringify({ api, s0, sFlood, sDrain, mars, errors }, null, 2));
  if (errors.length) process.exit(2);
})().catch(e=>{ console.error('FATAL', e.message); process.exit(1); });
