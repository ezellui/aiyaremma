"use strict";
const A="assets/";
let META, COUNTRIES={}, ENV={};
let W,H, layer="sim";
const idbuf={sim:null, real:null};
let S=1, ox=0, oy=0, selected=null;
const opts={nat:true, int:false, hl:true, env:false};

const $=s=>document.querySelector(s);
const base=$("#base"), bnat=$("#bnat"), bint=$("#bint"), overlay=$("#overlay");
const viewport=$("#viewport"), world=$("#world");

function loadImage(src){return new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=src;});}

async function decodeIds(url){
  const img=await loadImage(url);
  const c=document.createElement("canvas"); c.width=W; c.height=H;
  const cx=c.getContext("2d",{willReadFrequently:true}); cx.drawImage(img,0,0,W,H);
  const d=cx.getImageData(0,0,W,H).data;
  const out=new Int32Array(W*H);
  for(let i=0,p=0;i<W*H;i++,p+=4) out[i]= d[p+3]===0 ? -1 : ((d[p]<<8)|d[p+1]);
  return out;
}

async function init(){
  META=await (await fetch(A+"meta.json")).json();
  COUNTRIES=await (await fetch(A+"countries.json")).json();
  ENV=await (await fetch(A+"envelopes.json")).json();
  W=META.W; H=META.H;
  for(const el of [world]) { el.style.width=W+"px"; el.style.height=H+"px"; }
  overlay.width=W; overlay.height=H;
  base.width=W; base.height=H; bnat.width=W; bnat.height=H; bint.width=W; bint.height=H;
  setLayerImages();
  fitView();
  // декодируем id-буферы обоих слоёв
  idbuf.sim = await decodeIds(A+"ids_sim.png");
  idbuf.real= await decodeIds(A+"ids_real.png");
  bindUI();
}

function setLayerImages(){
  base.src=A+(layer==="sim"?"map_sim.png":"map_real.png");
  bnat.src=A+(layer==="sim"?"bord_sim_nat.png":"bord_real_nat.png");
  bint.src=A+(layer==="sim"?"bord_sim_int.png":"bord_real_int.png");
  bnat.style.display=opts.nat?"block":"none";
  bint.style.display=opts.int?"block":"none";
}

function fitView(){
  const vw=viewport.clientWidth, vh=viewport.clientHeight;
  S=Math.min(vw/W, vh/H); ox=(vw-W*S)/2; oy=(vh-H*S)/2; applyTransform();
}
function applyTransform(){ world.style.transform=`translate(${ox}px,${oy}px) scale(${S})`; }

function toImage(vx,vy){ return [Math.floor((vx-ox)/S), Math.floor((vy-oy)/S)]; }
function idAt(vx,vy){
  const [x,y]=toImage(vx,vy);
  if(x<0||y<0||x>=W||y>=H) return -1;
  const b=idbuf[layer]; return b?b[y*W+x]:-1;
}

function redraw(){
  const cx=overlay.getContext("2d"); cx.clearRect(0,0,W,H);
  if(selected==null) return;
  if(opts.hl){
    const b=idbuf[layer]; const img=cx.createImageData(W,H); const d=img.data;
    for(let i=0,p=0;i<W*H;i++,p+=4){ if(b[i]===selected){ d[p]=255;d[p+1]=255;d[p+2]=255;d[p+3]=110; } }
    cx.putImageData(img,0,0);
  }
  if(opts.env){
    const poly=ENV[selected];
    if(poly){
      cx.lineJoin="round"; cx.lineCap="round";
      cx.beginPath(); cx.moveTo(poly[0][0],poly[0][1]);
      for(let k=1;k<poly.length;k++) cx.lineTo(poly[k][0],poly[k][1]);
      cx.closePath();
      cx.lineWidth=4; cx.strokeStyle="#0c1116"; cx.stroke();
      cx.lineWidth=2; cx.strokeStyle="#ffffff"; cx.stroke();
    }
  }
}

function countPieces(id){
  const b=idbuf[layer]; let n=0; for(let i=0;i<b.length;i++) if(b[i]===id) n++; return n;
}
function showInfo(id){
  const box=$("#info-body");
  if(id<0||!COUNTRIES[id]){ box.innerHTML='<span class="muted">Океан</span>'; return; }
  const c=COUNTRIES[id]; const sw=META.palette[ /* color index unknown here */ 0];
  const hasEnv=!!ENV[id];
  box.innerHTML=
    `<div class="name">${c.ru}</div>`+
    `<div class="row">${c.en} · ${c.a3}</div>`+
    `<div class="row">Слой: ${layer==="sim"?"симуляция":"реальная карта"}</div>`+
    `<div class="pieces">${hasEnv?"огибающая доступна":"огибающая не строится (пересекает море)"}</div>`;
}

function bindUI(){
  document.querySelectorAll('input[name=layer]').forEach(r=>r.addEventListener("change",e=>{
    layer=e.target.value; setLayerImages(); redraw(); showInfo(selected==null?-1:selected);
  }));
  $("#opt-nat").addEventListener("change",e=>{opts.nat=e.target.checked;bnat.style.display=opts.nat?"block":"none";});
  $("#opt-int").addEventListener("change",e=>{opts.int=e.target.checked;bint.style.display=opts.int?"block":"none";});
  $("#opt-hl").addEventListener("change",e=>{opts.hl=e.target.checked;redraw();});
  $("#opt-env").addEventListener("change",e=>{opts.env=e.target.checked;redraw();});
  $("#reset").addEventListener("click",()=>{selected=null;redraw();showInfo(-1);});

  // pan / zoom / click
  let dragging=false,moved=false,sx=0,sy=0,sox=0,soy=0;
  viewport.addEventListener("mousedown",e=>{dragging=true;moved=false;sx=e.clientX;sy=e.clientY;sox=ox;soy=oy;viewport.classList.add("drag");});
  window.addEventListener("mousemove",e=>{
    const r=viewport.getBoundingClientRect();
    if(dragging){
      const dx=e.clientX-sx, dy=e.clientY-sy;
      if(Math.abs(dx)+Math.abs(dy)>3) moved=true;
      ox=sox+dx; oy=soy+dy; applyTransform();
    } else {
      const id=idAt(e.clientX-r.left,e.clientY-r.top);
      $("#hover").textContent = (id>=0&&COUNTRIES[id])?COUNTRIES[id].ru:"—";
    }
  });
  window.addEventListener("mouseup",e=>{
    if(dragging&&!moved){
      const r=viewport.getBoundingClientRect();
      const id=idAt(e.clientX-r.left,e.clientY-r.top);
      selected = id<0?null:id; redraw(); showInfo(id);
    }
    dragging=false; viewport.classList.remove("drag");
  });
  viewport.addEventListener("wheel",e=>{
    e.preventDefault();
    const r=viewport.getBoundingClientRect(); const vx=e.clientX-r.left, vy=e.clientY-r.top;
    const f=e.deltaY<0?1.15:1/1.15; const nS=Math.max(0.1,Math.min(20,S*f));
    ox=vx-(vx-ox)*(nS/S); oy=vy-(vy-oy)*(nS/S); S=nS; applyTransform();
  },{passive:false});
  window.addEventListener("resize",fitView);
}

init();
