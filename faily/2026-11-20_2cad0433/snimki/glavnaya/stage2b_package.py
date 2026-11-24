"""Stage 2b, §5б.10: the proposed set of changes checked as a whole -- every character, three winds, the hypercube.

The set (numbers from stage2b_variants.py, rounded up):
  * a governor that caps the speed: a centrifugal brake above 0.25 s per free turn (k 0.05 N m s), the fan kept;
  * the shaft's torque at the end of the wind raised to the least that turns every character (+5 %);
  * the sear lets go at 158 deg (was 160);
  * the carriage spring 6 N (was 4); the closed rotate tape preloaded 16 N (was 10);
  * the cocking rod's spring 3 N (was 2.5);
  * the feelers' springs W 0.95, B 0.70, C 0.70 N (were 0.82, 0.62, 0.66) and an elastomer tip on each feeler (e 0.15);
  * a polyurethane pad on the margin abutment (as on U's finger).
Nothing in the model is changed: the set lives in this script; the decision is the author's (spec §6.4).
Writes gen/physics/stage2b_package.json.
Usage: python3 -I tools/physics/stage2b_package.py"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import params as P
import shaft as S
import stage2b as B
import node_b as NB
import node_c as NC
import node_d as ND

SET = dict(gov_T=0.25, k_brake=0.05, release=158.0, car_F=6.0, tape_N=16.0, rod_N=3.0,
           feelers={'W': 0.95, 'B': 0.70, 'C': 0.70}, e_feeler=0.15, margin_pad=dict(k=0.3e6, e=0.2))
GOV = (2 * math.pi / SET['gov_T'], SET['k_brake'])


def apply():
    S.LJ['hammer']['rod_return_N'] = SET['rod_N']; NC.LJ['rod_return_N'] = SET['rod_N']
    NB.TAPE_PRELOAD = SET['tape_N']
    for c, v in SET['feelers'].items():
        P.READ_F_SPRING[c] = v
    B.E_FEELER = SET['e_feeler']
    S._TAB.clear()
    raw = S.trace
    def tr(ch, wind='M_need', passes=2, **kw):
        kw.setdefault('gov', GOV)
        return raw(ch, wind, passes, **kw)
    S.trace = tr


NODES = dict(C=dict(release=SET['release']), D=dict(F=SET['car_F']))


def main():
    t0 = time.time()
    apply()
    base = json.load(open(os.path.join(U.GEN, 'stage2b.json')))
    chs = S.characters()
    top = sorted(base['tau_min']['by_char'].items(), key=lambda x: -x[1])[:10]
    tm = {k: B.tau_min([c for c in chs if c['key'] == k][0]) for k, _ in top}
    tau_need = max(tm.values()) * 1.05
    winds = dict(M_end=B.M_of(tau_need), mid=0.5 * (B.M_of(tau_need) + S.WINDS['M_max']), M_max=S.WINDS['M_max'])
    out = dict(set=SET, tau_min=tm, tau_end=tau_need, M_end=winds['M_end'], winds=winds,
               energy_left_pct=100 * (S.SPR['M_max'] ** 2 - winds['M_end'] ** 2) / (S.SPR['M_max'] ** 2 - S.MJ['M_need'] ** 2))
    print('tau', tau_need, winds, round(time.time() - t0))
    rows = []
    for ch in chs:
        for wn, M in winds.items():
            tr = S.trace(ch, M)
            row = dict(key=ch['key'], label=ch['label'], pos=ch['pos'], row=ch['row'], w=ch['w'], weight=ch['weight'], idle=ch['idle'], wind=wn)
            if tr.stall is not None:
                row['stall_deg'] = tr.stall; rows.append(row); continue
            res = B.run_law(ch, tr, NODES)
            row.update(law=B.law_row(ch, tr), book={k: float(v) * 1e3 for k, v in tr.book.items()}, **res, bands=B.bands(ch, tr, res))
            rows.append(row)
    out['summary'] = B.summarize(rows, list(winds), chs)
    out['grid'] = rows
    print('grid', round(time.time() - t0))
    # the margin stop with the pad
    m, mw = ND.masses(); ms = []
    for e in (0.1, 0.2, 0.35):
        k_t = SET['margin_pad']['k'] * (ND.R_P / ND.R_T) ** 2
        r = ND.feed(SET['car_F'], 16, m, mw, k=k_t, e=e)
        fs = ND.feed_settle(SET['car_F'], 16, m, mw, k=k_t, e=e, t_max=0.4)
        F = r['F_tooth_N'] * ND.R_T / ND.R_P
        ms.append(dict(e=e, E_mJ=r['E_hit_mJ'], F_N=F, sigma_MPa=F / (5.5e-3 * 3e-3) / 1e6, rebound_u=fs['rebound_max_teeth']))
    out['margin_stop_pad'] = ms
    # U's finger at 6 N
    out['finger_U'] = [dict(w=w, **{k: v for k, v in ND.feed(SET['car_F'], w, m, mw).items() if k in ('E_hit_mJ', 'F_tooth_N', 'sigma_MPa', 't_feed_ms')})
                       for w in (4, 10, 16)]
    # the hypercube (the shaft's parameters, the nodes' contacts), every wind from the end to the full
    lo, hi = winds['M_end'], winds['M_max']
    save = dict(S.WINDS)
    S.WINDS['M_need'] = lo                         # B.lhs samples M between WINDS['M_need'] and WINDS['M_max']
    raw_run = B.run_law
    def rl(ch, tr, nk=None):
        k = dict(nk or {}); k.setdefault('C', {}); k['C'] = dict(k['C'], release=SET['release']); k.setdefault('D', {}); k['D'] = dict(k['D'], F=SET['car_F'])
        return raw_run(ch, tr, k)
    B.run_law = rl
    out['lhs'] = B.lhs(chs, winds, n=200)
    B.run_law = raw_run
    S.WINDS.update(save)
    out['time_s'] = time.time() - t0
    json.dump(out, open(os.path.join(U.GEN, 'stage2b_package.json'), 'w'), ensure_ascii=False, indent=1,
              default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else bool(x) if isinstance(x, np.bool_) else str(x))
    for wd, d in out['summary'].items():
        print(wd, {k: (v if not isinstance(v, list) or len(v) < 6 else len(v)) for k, v in d.items() if not k.startswith(('segs', 'n_'))})
    print('margin pad', ms); print('finger', out['finger_U'])
    print('lhs', {k: v for k, v in out['lhs'].items() if k not in ('rows', 'worst_1_blow_in_windows', 'worst_3_carriage_settled')})


if __name__ == '__main__':
    main()
