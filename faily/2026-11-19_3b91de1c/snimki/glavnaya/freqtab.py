"""rev. 0.11: keystroke frequencies from the books (gen/freq.json) for the document: macros and two tables.
Usage: python3 -I freqtab.py GEN_DIR"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import layout as lay
import inventory as inv

gen = sys.argv[1]
F = json.load(open(os.path.join(gen, 'freq.json')))
N = F['n']; SP = F['spaces']
cnt = {eval(k): v for k, v in F['items'].items()}
names = {cp: nm for cp, nm in inv.TENGWAR + inv.NUMERALS + inv.PUNCT}
names.update({'mark:' + k: role.split(' — ')[0] for k, g, kind, role in inv.MARKS})
names.update({'combo:' + nm: nm for nm, _ in inv.COMBOS})
pct = lambda v: 100.0 * v / N
f1 = lambda x: f'{x:.1f}'.replace('.', '{,}')
f2 = lambda x: f'{x:.2f}'.replace('.', '{,}')

row = {(r, t): 0 for r in range(4) for t in (0, 1)}
kind = {}
for r, rw in enumerate(lay.ROWS):
    for c, pair in enumerate(rw):
        for t, it in enumerate(pair):
            if it is None:
                continue
            row[(r, t)] += cnt.get(it, 0)
up = sum(v for (r, t), v in row.items() if t)
isT = lambda k: isinstance(k, int) and k < 0xE060
isP = lambda k: isinstance(k, int) and 0xE060 <= k < 0xE070
isN = lambda k: isinstance(k, int) and 0xE070 <= k < 0xE080
upper = [pair[1] for rw in lay.ROWS for pair in rw if pair[1] is not None]
lower = [pair[0] for rw in lay.ROWS for pair in rw if pair[0] is not None]
up_T = sum(cnt.get(k, 0) for k in upper if isT(k))
up_C = sum(cnt.get(k, 0) for k in upper if isinstance(k, str) and k.startswith('combo:'))
up_P = sum(cnt.get(k, 0) for k in upper if isP(k))
up_M = sum(cnt.get(k, 0) for k in upper if isinstance(k, str) and k.startswith('mark:'))
lo_N = sum(cnt.get(k, 0) for k in lower if isN(k))
dead = sum(v for k, v in cnt.items() if isinstance(k, str) and k.startswith('mark:'))
# variant: punctuation of the number row down, the numerals up
var_up = up - up_P + lo_N
rank_upT = sorted((k for k in upper if isT(k)), key=lambda k: -cnt.get(k, 0))
rank_loT = sorted((k for k in lower if isT(k)), key=lambda k: cnt.get(k, 0))
mac = dict(fqN=f'{N:,}'.replace(',', '\\,'), fqSP=f1(100.0 * SP / (N + SP)), fqUp=f1(pct(up)), fqUpT=f1(pct(up_T)), fqUpC=f1(pct(up_C)),
           fqUpP=f1(pct(up_P)), fqUpM=f1(pct(up_M)), fqLoN=f2(pct(lo_N)), fqVarUp=f1(pct(var_up)), fqDead=f1(pct(dead)),
           fqRowA=f1(pct(row[(2, 0)] + row[(2, 1)])), fqRowB=f1(pct(row[(3, 0)] + row[(3, 1)])),
           fqRowC=f1(pct(row[(1, 0)] + row[(1, 1)])), fqRowD=f1(pct(row[(0, 0)] + row[(0, 1)])),
           fqUpTop=', '.join(f'{names[k]} {f2(pct(cnt.get(k, 0)))}' for k in rank_upT[:6]),
           fqLoBot=', '.join(f'{names[k]} {f2(pct(cnt.get(k, 0)))}' for k in rank_loT[:6]))
open(os.path.join(gen, 'freq_num.tex'), 'w').write(''.join(f'\\newcommand\\{k}{{{v}}}\n' for k, v in mac.items()))
# table: the rows and registers
rn = ['цифры и знаки', 'верхний буквенный', 'основной (с техтами)', 'нижний']
rows = []
for r in (2, 3, 1, 0):
    rows.append(f"{rn[r]} & {lay.ROW_CODE[r] + 1} / {lay.ROW_CODE[r] + 5} & {f1(pct(row[(r, 0)]))} & {f1(pct(row[(r, 1)]))} & {f1(pct(row[(r, 0)] + row[(r, 1)]))}\\\\\n")
open(os.path.join(gen, 'tab_freq_rows.tex'), 'w').write(''.join(rows))
# table: the 24 most frequent signs
top = sorted(cnt.items(), key=lambda a: -a[1])[:24]
cells = [f"{names.get(k, str(k))} & {f2(pct(v))}" for k, v in top]
half = (len(cells) + 1) // 2
tr = []
for i in range(half):
    a = cells[i]; b = cells[i + half] if i + half < len(cells) else ' & '
    tr.append(f"{i + 1} & {a} & {i + half + 1} & {b}\\\\\n")
open(os.path.join(gen, 'tab_freq_top.tex'), 'w').write(''.join(tr))
print(mac)
