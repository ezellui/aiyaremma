"use strict";
const A="assets/";
let META, COUNTRIES={}, ENV={}, RANK={};
let W,H, layer="sim";
const idbuf={sim:null, real:null};
let S=1, ox=0, oy=0, selected=null;
const opts={nat:true, int:false, hl:true, env:false};
const ENVcache={};

// animation state
let arrival=null, baseColor=null, order=null, cumInc=null, totalPix=null, totalLand=0;
let animData=null, pos=0, seekVal=0, playing=false, revealed=null, rafid=0, lastT=0;
const DURATION=14; // секунд на 1x

const $=s=>document.querySelector(s);
const base=$("#base"), bnat=$("#bnat"), bint=$("#bint"), overlay=$("#overlay"), anim=$("#anim");
const viewport=$("#viewport"), world=$("#world");

function loadImage(src){return new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=src;});}
async function imgData(url){
  const img=await loadImage(url); const c=document.createElement("canvas");
  c.width=W;c.height=H; const cx=c.getContext("2d",{willReadFrequently:true});
  cx.drawImage(img,0,0,W,H); return cx.getImageData(0,0,W,H).data;
}
const fmt=n=>Math.round(n).toLocaleString("ru-RU");

async function init(){
  META=await (await fetch(A+"meta.json")).json();
  COUNTRIES=await (await fetch(A+"countries.json")).json();
  ENV=await (await fetch(A+"envelopes.json")).json();
  RANK=await (await fetch(A+"rankings.json")).json();
  W=META.W; H=META.H;
  world.style.width=W+"px"; world.style.height=H+"px";
  for(const el of [overlay,anim]){el.width=W;el.height=H;}
  for(const im of [base,bnat,bint]){im.width=W;im.height=H;}
  setLayerImages(); fitView(); bindUI(); buildAbout();
  // буферы
  const ds=await imgData(A+"ids_sim.png"); idbuf.sim=decodeIds(ds);
  const dr=await imgData(A+"ids_real.png"); idbuf.real=decodeIds(dr);
  // анимация
  baseColor=await imgData(A+"map_sim.png");
  const da=await imgData(A+"arrival_sim.png"); buildAnim(da);
}
function decodeIds(d){const o=new Int32Array(W*H);for(let i=0,p=0;i<W*H;i++,p+=4)o[i]=d[p+3]===0?-1:((d[p]<<8)|d[p+1]);return o;}

function buildAnim(d){
  arrival=new Int32Array(W*H);
  const hist=new Int32Array(65536); totalLand=0;
  for(let i=0,p=0;i<W*H;i++,p+=4){ if(d[p+3]===0){arrival[i]=-1;} else {const q=(d[p]<<8)|d[p+1]; arrival[i]=q; hist[q]++; totalLand++;} }
  cumInc=new Int32Array(65536); let c=0; for(let q=0;q<65536;q++){c+=hist[q];cumInc[q]=c;}
  const off=new Int32Array(65536); let r=0; for(let q=0;q<65536;q++){off[q]=r;r+=hist[q];}
  order=new Int32Array(totalLand);
  for(let i=0;i<W*H;i++){const q=arrival[i]; if(q>=0) order[off[q]++]=i;}
  // итоговые пиксели по странам (sim)
  let maxid=0; for(let i=0;i<W*H;i++){const v=idbuf.sim[i]; if(v>maxid)maxid=v;}
  totalPix=new Int32Array(maxid+1); for(let i=0;i<W*H;i++){const v=idbuf.sim[i]; if(v>=0)totalPix[v]++;}
  revealed=new Int32Array(maxid+1);
  animData=anim.getContext("2d").createImageData(W,H);
  pos=0;
}

function setLayerImages(){
  base.src=A+(layer==="sim"?"map_sim.png":"map_real.png");
  bnat.src=A+(layer==="sim"?"bord_sim_nat.png":"bord_real_nat.png");
  bint.src=A+(layer==="sim"?"bord_sim_int.png":"bord_real_int.png");
  setView();
}
function animActive(){return playing||seekVal>0.5;}
function setView(){
  const av=animActive();
  anim.style.display=av?"block":"none";
  base.style.display=av?"none":"block";
  bnat.style.display=(!av&&opts.nat)?"block":"none";
  bint.style.display=(!av&&opts.int)?"block":"none";
  overlay.style.display=av?"none":"block";
}

function fitView(){const vw=viewport.clientWidth,vh=viewport.clientHeight;S=Math.min(vw/W,vh/H);ox=(vw-W*S)/2;oy=(vh-H*S)/2;applyTransform();}
function applyTransform(){world.style.transform=`translate(${ox}px,${oy}px) scale(${S})`;}
function toImage(vx,vy){return [Math.floor((vx-ox)/S),Math.floor((vy-oy)/S)];}
function idAt(vx,vy){const [x,y]=toImage(vx,vy);if(x<0||y<0||x>=W||y>=H)return -1;const b=idbuf[layer];return b?b[y*W+x]:-1;}

// ---- convex hull helpers (огибающая по запросу) ----
function convexHull(pts){
  pts=pts.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]); const n=pts.length; if(n<3)return pts;
  const cr=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
  const lo=[]; for(const p of pts){while(lo.length>=2&&cr(lo[lo.length-2],lo[lo.length-1],p)<=0)lo.pop();lo.push(p);}
  const hi=[]; for(let i=n-1;i>=0;i--){const p=pts[i];while(hi.length>=2&&cr(hi[hi.length-2],hi[hi.length-1],p)<=0)hi.pop();hi.push(p);}
  lo.pop();hi.pop();return lo.concat(hi);
}
function expandPoly(poly,d){let cx=0,cy=0;for(const p of poly){cx+=p[0];cy+=p[1];}cx/=poly.length;cy/=poly.length;
  return poly.map(([x,y])=>{const dx=x-cx,dy=y-cy,L=Math.hypot(dx,dy)||1;return [x+dx/L*d,y+dy/L*d];});}
function chaikin(poly,it){let P=poly;for(let k=0;k<it;k++){const Q=[],n=P.length;
  for(let i=0;i<n;i++){const a=P[i],b=P[(i+1)%n];Q.push([0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1]]);Q.push([0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1]]);}P=Q;}return P;}
function envelopeFor(id){
  const key=layer+":"+id; if(ENVcache[key]!==undefined)return ENVcache[key];
  let poly=null;
  if(layer==="sim"&&ENV[id]) poly=ENV[id];
  else{
    const b=idbuf[layer]; const pts=[];
    for(let y=0;y<H;y++){let lo=-1,hi=-1;const bb=y*W;
      for(let x=0;x<W;x++){if(b[bb+x]===id){if(lo<0)lo=x;hi=x;}}
      if(lo>=0){pts.push([lo,y]);pts.push([hi,y]);}}
    if(pts.length>=3){let h=convexHull(pts);h=expandPoly(h,4);h=chaikin(h,2);poly=h;}
  }
  ENVcache[key]=poly; return poly;
}

function redraw(){
  const cx=overlay.getContext("2d"); cx.clearRect(0,0,W,H);
  if(selected==null)return;
  if(opts.hl){
    const b=idbuf[layer]; const img=cx.createImageData(W,H); const d=img.data;
    for(let i=0,p=0;i<W*H;i++,p+=4){if(b[i]===selected){d[p]=255;d[p+1]=255;d[p+2]=255;d[p+3]=110;}}
    cx.putImageData(img,0,0);
  }
  if(opts.env){
    const poly=envelopeFor(selected);
    if(poly){cx.lineJoin="round";cx.lineCap="round";cx.beginPath();cx.moveTo(poly[0][0],poly[0][1]);
      for(let k=1;k<poly.length;k++)cx.lineTo(poly[k][0],poly[k][1]);cx.closePath();
      cx.lineWidth=4;cx.strokeStyle="#0c1116";cx.stroke();cx.lineWidth=2;cx.strokeStyle="#fff";cx.stroke();}
  }
}

function showInfo(id){
  const box=$("#info-body");
  if(id<0||!COUNTRIES[id]){box.innerHTML='<span class="muted">Океан</span>';return;}
  const c=COUNTRIES[id]; const d=c.delta, dc=d>=0?"delta-pos":"delta-neg", sign=d>=0?"+":"";
  const env=(layer==="sim"&&ENV[id])?"огибающая (без моря) готова":"огибающая строится по запросу";
  box.innerHTML=
    `<div class="name">${c.ru}</div>`+
    `<div class="row">${c.en} · ${c.a3} · слой: ${layer==="sim"?"симуляция":"реальная"}</div>`+
    `<div class="area"><span>реальная площадь</span><b>${fmt(c.ar_real)} км²</b></div>`+
    `<div class="area"><span>в модели</span><b>${fmt(c.ar_model)} км²</b></div>`+
    `<div class="area"><span>разница</span><b class="${dc}">${sign}${fmt(d)} км²</b></div>`+
    (c.div!=null?`<div class="area"><span>расхождение границ</span><b>${c.div}</b></div>`:"")+
    `<div class="row" style="margin-top:6px">${env}</div>`;
}

// ---------- animation ----------
function clearAnim(){animData.data.fill(0);pos=0;revealed.fill(0);}
function revealTo(target){
  if(target<pos){clearAnim();}
  const d=animData.data, bc=baseColor, ids=idbuf.sim;
  while(pos<target){const i=order[pos],p=i*4;d[p]=bc[p];d[p+1]=bc[p+1];d[p+2]=bc[p+2];d[p+3]=255;
    const cid=ids[i]; if(cid>=0)revealed[cid]++; pos++;}
  anim.getContext("2d").putImageData(animData,0,0);
}
function updateCounter(){
  const el=$("#counter");
  if(selected!=null&&COUNTRIES[selected]&&totalPix[selected]){
    const frac=revealed[selected]/totalPix[selected];
    const km=COUNTRIES[selected].ar_model*frac;
    el.innerHTML=`${COUNTRIES[selected].ru}: <b>${fmt(km)}</b> км² (${Math.round(frac*100)}%)`;
  }else{
    el.textContent=`захвачено суши: ${Math.round(pos/totalLand*100)}%`;
  }
}
function seekToValue(v){seekVal=v;$("#seek").value=v;const q=Math.max(0,Math.min(65535,Math.floor(v)));revealTo(cumInc[q]);updateCounter();setView();}
function frame(ts){
  if(!playing)return;
  if(!lastT)lastT=ts; const dt=(ts-lastT)/1000; lastT=ts;
  const spd=parseFloat($("#speed").value);
  seekVal+=65535/DURATION*spd*dt;
  if(seekVal>=65535){seekVal=65535;seekToValue(seekVal);stop();return;}
  seekToValue(seekVal); rafid=requestAnimationFrame(frame);
}
function play(){
  if(seekVal>=65535){seekVal=0;clearAnim();}
  playing=true; lastT=0; $("#play").textContent="⏸"; setView(); rafid=requestAnimationFrame(frame);
}
function stop(){playing=false;$("#play").textContent="▶";cancelAnimationFrame(rafid);setView();}

function bindUI(){
  document.querySelectorAll('input[name=layer]').forEach(rdo=>rdo.addEventListener("change",e=>{
    layer=e.target.value; setLayerImages(); redraw(); showInfo(selected==null?-1:selected);}));
  $("#opt-nat").addEventListener("change",e=>{opts.nat=e.target.checked;setView();});
  $("#opt-int").addEventListener("change",e=>{opts.int=e.target.checked;setView();});
  $("#opt-hl").addEventListener("change",e=>{opts.hl=e.target.checked;redraw();});
  $("#opt-env").addEventListener("change",e=>{opts.env=e.target.checked;redraw();});
  $("#reset").addEventListener("click",()=>{selected=null;redraw();showInfo(-1);updateCounter();});

  $("#play").addEventListener("click",()=>{playing?stop():play();});
  $("#seek").addEventListener("input",e=>{if(playing)stop();seekToValue(parseFloat(e.target.value));});

  $("#btn-about").addEventListener("click",()=>$("#modal-about").classList.remove("hidden"));
  $("#btn-rank").addEventListener("click",()=>{showRank("delta");$("#modal-rank").classList.remove("hidden");});
  document.querySelectorAll("[data-close]").forEach(b=>b.addEventListener("click",e=>e.target.closest(".modal").classList.add("hidden")));
  document.querySelectorAll(".modal").forEach(m=>m.addEventListener("click",e=>{if(e.target===m)m.classList.add("hidden");}));
  document.querySelectorAll(".tab").forEach(t=>t.addEventListener("click",e=>{
    document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));e.target.classList.add("active");showRank(e.target.dataset.tab);}));

  let dragging=false,moved=false,sx=0,sy=0,sox=0,soy=0;
  viewport.addEventListener("mousedown",e=>{dragging=true;moved=false;sx=e.clientX;sy=e.clientY;sox=ox;soy=oy;viewport.classList.add("drag");});
  window.addEventListener("mousemove",e=>{const r=viewport.getBoundingClientRect();
    if(dragging){const dx=e.clientX-sx,dy=e.clientY-sy;if(Math.abs(dx)+Math.abs(dy)>3)moved=true;ox=sox+dx;oy=soy+dy;applyTransform();}
    else{const id=idAt(e.clientX-r.left,e.clientY-r.top);$("#hover").textContent=(id>=0&&COUNTRIES[id])?COUNTRIES[id].ru:"—";}});
  window.addEventListener("mouseup",e=>{
    if(dragging&&!moved){const r=viewport.getBoundingClientRect();const id=idAt(e.clientX-r.left,e.clientY-r.top);
      selected=id<0?null:id;redraw();showInfo(id);updateCounter();}
    dragging=false;viewport.classList.remove("drag");});
  viewport.addEventListener("wheel",e=>{e.preventDefault();const r=viewport.getBoundingClientRect();const vx=e.clientX-r.left,vy=e.clientY-r.top;
    const f=e.deltaY<0?1.15:1/1.15;const nS=Math.max(0.1,Math.min(20,S*f));ox=vx-(vx-ox)*(nS/S);oy=vy-(vy-oy)*(nS/S);S=nS;applyTransform();},{passive:false});
  window.addEventListener("resize",fitView);
}

function showRank(tab){
  const body=$("#rank-body"); let html='<div class="rank-list">';
  if(tab==="delta"){
    const arr=RANK.delta;
    html+='<div class="rank-row" style="cursor:default;color:#9aa3b2"><span>приобрели / потеряли</span><span class="v">км²</span></div>';
    const top=arr.slice(-15).reverse().concat([{ru:"…",delta:null}]).concat(arr.slice(0,15));
    let rk=1;
    for(const r of top){
      if(r.delta===null){html+='<div class="rank-row" style="cursor:default;justify-content:center;color:#5a6372">⋯</div>';continue;}
      const cls=r.delta>=0?"delta-pos":"delta-neg",s=r.delta>=0?"+":"";
      html+=`<div class="rank-row" data-id="${r.id}"><span><span class="rk">${rk++}</span>${r.ru}</span><span class="v ${cls}">${s}${fmt(r.delta)}</span></div>`;
    }
  }else{
    let rk=1;
    for(const r of RANK.divergence.slice(0,40))
      html+=`<div class="rank-row" data-id="${r.id}"><span><span class="rk">${rk++}</span>${r.ru}</span><span class="v">${r.div}</span></div>`;
  }
  html+="</div>"; body.innerHTML=html;
  body.querySelectorAll(".rank-row[data-id]").forEach(row=>row.addEventListener("click",()=>{
    const id=parseInt(row.dataset.id); selected=id; if(playing)stop(); seekVal=0; setView();
    redraw(); showInfo(id); updateCounter(); $("#modal-rank").classList.add("hidden");
    centerOn(id);
  }));
}
function centerOn(id){
  const b=idbuf[layer]; let minx=W,miny=H,maxx=0,maxy=0,found=false;
  for(let y=0;y<H;y++){const bb=y*W;for(let x=0;x<W;x++){if(b[bb+x]===id){found=true;if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;}}}
  if(!found)return; const cx=(minx+maxx)/2,cy=(miny+maxy)/2;
  const vw=viewport.clientWidth,vh=viewport.clientHeight;
  S=Math.min(8,Math.max(1,Math.min(vw/(maxx-minx+80),vh/(maxy-miny+80))));
  ox=vw/2-cx*S; oy=vh/2-cy*S; applyTransform();
}

function buildAbout(){
  $("#about-text").innerHTML=`
  <p>Карта строится моделью <b>коалесцентного роста</b>. Это ответ на вопрос: если бы границы определялись не историей, а «гравитацией населения» и географией, как бы поделилась суша?</p>
  <h3>Семена</h3>
  <p>В каждый административный центр первого уровня (всего ~4,6 тыс.) сажается «семя». Население каждого региона берётся из реального растра плотности (GHS-POP, 2020), просуммированного по его территории.</p>
  <h3>Скорость фронта ∝ √населения</h3>
  <p>От каждого семени распространяется фронт. Его скорость пропорциональна корню из населения той связной области, к которой фронт принадлежит в данный момент. Чем многолюднее держава, тем быстрее она тянется к новым землям.</p>
  <h3>Слияние (коалесценция)</h3>
  <p>Когда два фронта одной страны соприкасаются, их области <b>сливаются</b>, население складывается, и весь объединённый периметр ускоряется. Так плотные компактные страны быстро «сшивают» себя изнутри и дальше идут наружу почти как единая масса.</p>
  <h3>Конечная скорость проекции</h3>
  <p>Отрезанные куски — острова, эксклавы, дальние окраины за пустотами — не успевают слиться с ядром и растут лишь на своём малом населении. Поэтому огромные разреженные державы (Россия, Канада, Казахстан) теряют дальние рубежи: масса физически не успевает «дотянуться» через пустоту. Это и есть подпись модели — финитная скорость проекции силы.</p>
  <h3>Что вы видите</h3>
  <p>Граница между странами — там, где встретились их фронты. «Реальная карта» показана для сравнения; цвета согласованы — страна сохраняет свой цвет в обоих слоях. Анимация проигрывает рост от семян до готовой карты по сохранённым временам прихода фронта.</p>`;
}

init();
