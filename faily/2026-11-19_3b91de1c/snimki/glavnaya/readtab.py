"""rev. 0.10: tables and numbers of the reading from the shuttle for the design document.
Usage: python3 -I readtab.py GEN_DIR"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
import data as D
import reader as RD

gen = sys.argv[1]
f = lambda x, n=1: f"{x:.{n}f}".replace('.', '{,}').replace('-', '−')

audit = RD.audit()
bad = [a for a in audit if not a['ok']]
M, I = RD.mass_inertia()
MO = json.load(open(os.path.join(gen, 'motor.json')))
json.dump(dict(audit=audit, mass_g=M, I_kgmm2=I), open(os.path.join(gen, 'read.json'), 'w'), ensure_ascii=False, indent=1,
          default=lambda o: o.item() if hasattr(o, 'item') else str(o))

# appendix: every cell with a code
rows = []
lay = D.shuttle_layout()
for m in range(P.NPOS):
    for r in range(P.NROWS):
        v = RD.code_v(lay[r][m])
        if v is None:
            continue
        it = D.ITEMS[lay[r][m]]
        cps = it.get('cps') or []
        glyph = ''.join(f'\\symbol{{"{c:X}}}' for c in cps) if cps else ''
        rf = [RD.face_r(x) for x in v]
        a = next(x for x in audit if x['pos'] == m and x['row'] == r + 1)
        rows.append(f"{m} & {r + 1} & {{\\tgsmall {glyph}}} & {it['label']} & {it['w']} & {v[1]} & {v[2]} & "
                    f"{f(rf[0], 1)} & {f(rf[1], 1)} & {f(rf[2], 1)} & {'да' if a['ok'] else '\\textbf{нет}'}\\\\\n")
open(os.path.join(gen, 'tab_combs.tex'), 'w').write(''.join(rows))

# the channels
rows = []
for ch, name, rng in (('W', 'ширина $w - 4$', (0, 12)), ('B', 'отвод $b$', (1, 8)), ('C', 'отвод $c$', (1, 9))):
    rows.append(f"{ch} & {name} & {rng[0]}--{rng[1]} & {f(RD.face_r(rng[0]))}--{f(RD.face_r(rng[1]))} & "
                f"{f(P.READ_DZ[ch], 1)} & {f(P.READ_F_SPRING[ch], 2)} & {f(P.READ_F_LOAD[ch], 2)}\\\\\n")
open(os.path.join(gen, 'tab_read.tex'), 'w').write(''.join(rows))

nums = dict(rdn=len(audit), rdbad=len(bad), rdmass=f(M, 0), rdI=f(I, 0), rdIrot=f(MO['I_rot'], 0), rdmlift=f(MO['m_lift'], 0),
            rdEavg=f(MO['E_read_avg'] * 1000, 1), rdEmax=f(MO['E_read_max'] * 1000, 1), rdRzero=f(P.READ_R0, 1),
            rdCzero=f(P.READ_C0, 1), rdtravel=f(P.READ_TRAVEL, 1), rdtabw=f(P.TAB_W, 1), rdtabh=f(P.TAB_H, 1),
            rdspine=f(P.COMB_T, 1), rdzread=f(RD.Z_READ, 1), rdrelease=f"{P.CYCLE['read'][0] - P.READ_RAMP[0]:.0f}",
            rdout=f"{P.CYCLE['read'][0]:.0f}", rdin=f"{P.CYCLE['read'][1]:.0f}", rdback=f"{P.CYCLE['read'][1] + P.READ_RAMP[1]:.0f}",
            rdlatch=f"{P.CYCLE['wlatch']:.0f}", rdcam=f(P.READ_TRAVEL / 3, 1))
open(os.path.join(gen, 'read_num.tex'), 'w').write(''.join(f"\\newcommand\\{k}{{{v}}}\n" for k, v in nums.items()))
print('read audit', len(audit), 'failed', len(bad), 'combs', round(M, 1), 'g', round(I, 1), 'kg mm2')
