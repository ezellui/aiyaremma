const PUP='/home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer';
const puppeteer=require(PUP);
const path=require('path');
const CHROME='/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const URL='file://'+path.resolve('sim.html');

const tests=[
  {name:'maze_029_057', f:0.029,k:0.057},
  {name:'spots_030_062',f:0.030,k:0.062},
  {name:'mitosis_026_061',f:0.026,k:0.061},
  {name:'chaotic_026_051',f:0.026,k:0.051},
];

(async()=>{
  const browser=await puppeteer.launch({executablePath:CHROME,headless:'new',
    args:['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();
  await page.goto(URL,{waitUntil:'load'});
  await page.waitForFunction('window.__lab && window.__lab.cpu',{timeout:20000});
  await page.evaluate(()=>{ __lab.cpu(); __lab.stop(); __lab.setSize(128); });
  await new Promise(r=>setTimeout(r,150));
  console.log('mode:',await page.evaluate(()=>__lab.get()));

  for(const t of tests){
    const t0=Date.now();
    const r=await page.evaluate((t)=>__lab.classify(
      {f:t.f,k:t.k,dA:1.0,dB:0.5,dt:0.6,noise:0,seedCount:20,seedSize:5,boundary:'toroidal'},
      42, 15000, 400, 4), t);
    await page.evaluate(()=>__lab.render());
    await (await page.$('#canvas')).screenshot({path:'c_'+t.name+'.png'});
    console.log(t.name, '('+(Date.now()-t0)+'ms)', JSON.stringify(r));
  }
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
