const PUP='/home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer';
const puppeteer=require(PUP);
const path=require('path');
const CHROME='/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const URL='file://'+path.resolve('sim.html');

(async()=>{
  const browser=await puppeteer.launch({
    executablePath:CHROME, headless:'new',
    args:['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
  });
  const page=await browser.newPage();
  page.on('console',m=>{ const t=m.text(); if(t.includes('Ошибка')||t.includes('ERROR')) console.log('[page]',t); });
  await page.goto(URL,{waitUntil:'load'});
  await page.waitForFunction('window.__lab && typeof window.__lab.cpu==="function"',{timeout:20000});

  // force CPU + stop the rAF loop influence (we drive steps manually)
  await page.evaluate(()=>{ __lab.cpu(); __lab.stop(); });
  await new Promise(r=>setTimeout(r,200));
  const mode=await page.evaluate(()=>__lab.get());
  console.log('mode after cpu switch:',mode.useGPU?'GPU':'CPU','isWebGLReady=',mode.isWebGLReady,'size=',mode.size);

  // configure clean init: noise 0, deterministic seeds
  const t0=Date.now();
  const res=await page.evaluate(()=>{
    __lab.set({f:0.029,k:0.057,dA:1.0,dB:0.5,dt:0.6,noise:0,seedCount:20,seedSize:5,boundary:'toroidal'});
    __lab.reseed(42);
    __lab.steps(4000);
    const snap=__lab.snapB();
    __lab.steps(2000);
    const m1=__lab.metrics(snap);
    return {m1};
  });
  const t1=Date.now();
  console.log('4000+2000 steps took',(t1-t0),'ms on size',mode.size);
  console.log('metrics(maze f0.029 k0.057):',JSON.stringify(res.m1));

  __dummy: {}
  // screenshot canvas
  await page.evaluate(()=>__lab.render());
  const canvas=await page.$('#canvas');
  await canvas.screenshot({path:'calib_maze.png'});
  console.log('screenshot saved calib_maze.png');

  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
