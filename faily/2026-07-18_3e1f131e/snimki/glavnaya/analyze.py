#!/usr/bin/env python3
import json, os
from PIL import Image, ImageDraw, ImageFont

rows=[json.loads(l) for l in open('results.jsonl') if l.strip()]
fk=[r for r in rows if r['kind']=='fk']
df=[r for r in rows if r['kind']=='diff']

def classify(r):
    cov=r['coverage']; intf=r['interface']; act=r['actLast']
    if cov<0.03: return ('dead','#444')
    if cov>0.95 and intf<0.02: return ('uniform','#3a6')
    if act>2e-5: return ('non-stationary','#e33')
    if act>1e-5: return ('borderline','#e90')
    return ('stationary','#09c')

# structure scale bucket by interface density
def scale(r):
    intf=r['interface']
    if intf<0.02: return '—'
    if intf>=0.15: return 'fine'
    if intf>=0.09: return 'medium'
    return 'coarse'

fList=sorted(set(r['f'] for r in fk))
kList=sorted(set(r['k'] for r in fk))
grid={(r['fi'],r['ki']):r for r in fk}

print('=== (f,k) MAP :  rows=f (top small -> bottom large), cols=k (left small -> right large) ===')
hdr='  f\\k  |'+''.join(f'{k:>8.3f}' for k in kList)
print(hdr); print('-'*len(hdr))
for fi,f in enumerate(fList):
    cells=[]
    for ki,k in enumerate(kList):
        r=grid.get((fi,ki))
        if not r: cells.append('   .   '); continue
        lab,_=classify(r)
        sym={'dead':'die','uniform':'UNI','non-stationary':'OSC','borderline':'brd','stationary':'sta'}[lab]
        cells.append(f'{sym:>8}')
    print(f'{f:>6.3f} |'+''.join(cells))

print('\n=== detail table (f,k) ===')
print(f'{"f":>7}{"k":>7}{"class":>16}{"scale":>8}{"cov":>7}{"intf":>7}{"actLast":>11}')
for r in sorted(fk,key=lambda r:(r['f'],r['k'])):
    lab,_=classify(r)
    print(f'{r["f"]:>7.3f}{r["k"]:>7.3f}{lab:>16}{scale(r):>8}{r["coverage"]:>7.2f}{r["interface"]:>7.3f}{r["actLast"]:>11.2e}')

print('\n=== diffusion sweep (f=0.030,k=0.057, dA=1.0, vary dB) ===')
print(f'{"dB":>6}{"class":>16}{"scale":>8}{"cov":>7}{"intf":>7}{"actLast":>11}')
for r in sorted(df,key=lambda r:r['dB']):
    lab,_=classify(r)
    print(f'{r["dB"]:>6.2f}{lab:>16}{scale(r):>8}{r["coverage"]:>7.2f}{r["interface"]:>7.3f}{r["actLast"]:>11.2e}')

# ---------- montage of (f,k) ----------
def montage(records, cols_key, rows_key, fname, title, cell=150, pad=34, left=64, top=52):
    colvals=sorted(set(r[cols_key] for r in records))
    rowvals=sorted(set(r[rows_key] for r in records))
    W=left+len(colvals)*(cell+pad)+pad
    H=top+len(rowvals)*(cell+pad)+pad
    im=Image.new('RGB',(W,H),'#0a0e14')
    d=ImageDraw.Draw(im)
    try:
        fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',13)
        fntb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
        fntt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
    except: fnt=fntb=fntt=ImageFont.load_default()
    d.text((left,12),title,fill='#e8f4f8',font=fntt)
    byrc={(r[rows_key],r[cols_key]):r for r in records}
    for ci,cv in enumerate(colvals):
        x=left+ci*(cell+pad)+pad
        d.text((x+cell*0.30,top-20),f'{cols_key}={cv:.3f}',fill='#00e5ff',font=fnt)
    for ri,rv in enumerate(rowvals):
        y=top+ri*(cell+pad)+pad
        d.text((6,y+cell*0.45),f'{rows_key}={rv:.3f}',fill='#ff006e',font=fnt)
    for ri,rv in enumerate(rowvals):
        for ci,cv in enumerate(colvals):
            r=byrc.get((rv,cv))
            if not r: continue
            x=left+ci*(cell+pad)+pad; y=top+ri*(cell+pad)+pad
            p='shots/'+r['slug']+'.png'
            if os.path.exists(p):
                thumb=Image.open(p).convert('RGB').resize((cell,cell))
                im.paste(thumb,(x,y))
            lab,col=classify(r)
            d.rectangle([x-2,y-2,x+cell+2,y+cell+2],outline=col,width=3)
            d.text((x+2,y+cell+2),lab,fill=col,font=fnt)
    im.save(fname)
    print('saved',fname,im.size)

montage(fk,'k','f','map_fk.png','Turing / Gray-Scott map: f (feed) down, k (kill) right')
montage(df,'dB','f','map_diff.png','Diffusion sweep: dB (inhibitor diffusion) right  [f=0.030,k=0.057]')
