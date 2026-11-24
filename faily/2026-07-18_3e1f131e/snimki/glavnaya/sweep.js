const PUP='/home/claude/.npm-global/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer';
const puppeteer=require(PUP);
const path=require('path'), fs=require('fs');
const CHROME='/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome';
const URL='file://'+path.resolve('sim.html');

const fList=[0.014,0.020,0.026,0.030,0.034,0.040,0.048,0.058];
const kList=[0.046,0.052,0.057,0.060,0.062,0.065];
// diffusion sweep at a stationary maze base point
const dBList=[0.15,0.25,0.35,0.45,0.55,0.65,0.75];

const jobs=[];
for(let fi=0;fi<fList.length;fi++) for(let ki=0;ki<kList.length;ki++){
  jobs.push({kind:'fk', fi,ki, f:fList[fi], k:kList[ki], dA:1.0, dB:0.5,
             slug:`fk_${String(fi).padStart(2,'0')}_${String(ki).padStart(2,'0')}`});
}
for(let i=0;i<dBList.length;i++){
  jobs.push({kind:'diff', f:0.030,k:0.057,dA:1.0,dB:dBList[i],
             slug:`df_${String(i).padStart(2,'0')}_dB${dBList[i]}`});
}

const BURN=12000, WIN=350, REPS=4, SEED=42, GRID=128;
const OUT='results.jsonl';
fs.writeFileSync(OUT,''); // truncate

(async()=>{
  const browser=await puppeteer.launch({executablePath:CHROME,headless:'new',
    args:['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();
  await page.goto(URL,{waitUntil:'load'});
  await page.waitForFunction('window.__lab && window.__lab.cpu',{timeout:20000});
  await page.evaluate(()=>{ __lab.cpu(); __lab.stop(); __lab.setSize(128); });
  await new Promise(r=>setTimeout(r,150));
  fs.mkdirSync('shots',{recursive:true});
  console.log('START',new Date().toISOString(),'jobs:',jobs.length);

  let done=0;
  for(const j of jobs){
    const t0=Date.now();
    const r=await page.evaluate((j,BURN,WIN,REPS,SEED)=>__lab.classify(
      {f:j.f,k:j.k,dA:j.dA,dB:j.dB,dt:0.6,noise:0,seedCount:20,seedSize:5,boundary:'toroidal'},
      SEED,BURN,WIN,REPS), j,BURN,WIN,REPS,SEED);
    await page.evaluate(()=>__lab.render());
    await (await page.$('#canvas')).screenshot({path:'shots/'+j.slug+'.png'});
    const rec=Object.assign({slug:j.slug,kind:j.kind,fi:j.fi,ki:j.ki,ms:Date.now()-t0}, r);
    fs.appendFileSync(OUT, JSON.stringify(rec)+'\n');
    done++;
    console.log(`[${done}/${jobs.length}] ${j.slug} f=${j.f} k=${j.k} dB=${j.dB} act=${r.actLast} cov=${r.coverage} intf=${r.interface} (${rec.ms}ms)`);
  }
  console.log('DONE',new Date().toISOString());
  await browser.close();
})().catch(e=>{console.error('FATAL',e);process.exit(1);});
