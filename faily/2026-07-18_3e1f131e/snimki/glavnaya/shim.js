
        /* ==================== HEADLESS LAB SHIM ==================== */
        (function(){
            function mulberry32(a){ return function(){ a|=0; a=(a+0x6D2B79F5)|0; let t=Math.imul(a^(a>>>15),1|a); t=(t+Math.imul(t^(t>>>7),61|t))^t; return ((t^(t>>>14))>>>0)/4294967296; }; }
            let __seed=1; let __rng=mulberry32(1); const __orig=Math.random;
            const TH=0.2; /* activity/coverage threshold for B */

            function metricsOn(prev){
                const n=size*size; let sum=0,sum2=0,mn=1e9,mx=-1e9,cov=0;
                for(let i=0;i<n;i++){ const v=gridB[i]; sum+=v; sum2+=v*v; if(v<mn)mn=v; if(v>mx)mx=v; if(v>TH)cov++; }
                const mean=sum/n, varr=sum2/n-mean*mean;
                let edges=0;
                for(let y=0;y<size;y++) for(let x=0;x<size;x++){
                    const i=x+y*size; const a=gridB[i]>TH;
                    if(a !== (gridB[((x+1)%size)+y*size]>TH)) edges++;
                    if(a !== (gridB[x+((y+1)%size)*size]>TH)) edges++;
                }
                const interf=edges/n;
                let act=null;
                if(prev){ let d=0; for(let i=0;i<n;i++){ const e=gridB[i]-prev[i]; d+=e<0?-e:e; } act=d/n; }
                return {mean,varr,max:mx,coverage:cov/n,interface:interf,activity:act};
            }

            window.__lab = {
                setSeed(s){ __seed=s>>>0; __rng=mulberry32(__seed); },
                det(on){ Math.random = on ? function(){return __rng();} : __orig; },
                stop(){ running=false; },
                set(p){
                    if('f' in p) feedRate=p.f;
                    if('k' in p) killRate=p.k;
                    if('dA' in p) dA=p.dA;
                    if('dB' in p) dB=p.dB;
                    if('dt' in p) dt=p.dt;
                    if('noise' in p) noiseLevel=p.noise;
                    if('seedCount' in p) seedCount=p.seedCount;
                    if('seedSize' in p) seedSize=p.seedSize;
                    if('boundary' in p) boundaryType=p.boundary;
                },
                get(){ return {feedRate,killRate,dA,dB,dt,noiseLevel,seedCount,seedSize,boundaryType,size,useGPU,isWebGLReady}; },
                cpu(){ if(typeof switchComputeMode==='function' && useGPU){ switchComputeMode('cpu'); } },
                setSize(px){ if(px!==size && typeof resizeGrid==='function'){ running=false; resizeGrid(px); } },
                reseed(seed){ this.setSeed(seed); this.det(true); initGrid(); this.det(false); },
                steps(n){ for(let i=0;i<n;i++) simulate(); },
                render(){ draw(); },
                snapB(){ return Array.from(gridB); },
                size(){ return size; },
                metrics(prev){ return metricsOn(prev); },
                /* Full classification run for one parameter set.
                   burn: settle steps; win: measurement window (steps); reps: # windows.
                   Returns coverage/interface plus a decaying-activity profile. */
                classify(params, seed, burn, win, reps){
                    this.set(params);
                    this.reseed(seed);
                    this.steps(burn);
                    const acts=[];
                    let prev=this.snapB();
                    let last=null;
                    for(let r=0;r<reps;r++){
                        this.steps(win);
                        const m=metricsOn(prev);
                        acts.push(+(m.activity/win).toExponential(3)); /* per-step drift */
                        prev=this.snapB();
                        last=m;
                    }
                    return {
                        f:feedRate,k:killRate,dA,dB,
                        max:+last.max.toFixed(3),
                        coverage:+last.coverage.toFixed(3),
                        interface:+last.interface.toFixed(3),
                        actPerStep:acts,             /* array over windows */
                        actLast:acts[acts.length-1]  /* final per-step drift */
                    };
                }
            };
        })();
