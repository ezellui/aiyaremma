"""Stage 2b, §5б.10: the variants for what fails on the shaft's real law (the choice is the author's, spec §6.4).

Every failure of stage 2b grows with the shaft's speed or comes from its end of wind:
  * the shaft stops on the cocking at M_need (and at M_avg, which is below M_need);
  * with the fan governor (drag ~ w^2) the speed goes with sqrt(torque): the spring's torque changes 2.3 times over the
    working wind, the speed 1.5 times, and the blow, the feed, the feelers, the tape, the cocking rod and the latch
    all depend on it.
The variants here: a governor that caps the speed (a centrifugal brake above w_s) at three settings, and on top of it
the targeted fixes -- the sear's release angle, the carriage spring, the feelers' springs, the tape's preload, the
cocking rod's spring -- each with its number. On a representative set of characters (the extreme positions, rows and
widths, the space) at the least working wind, the middle and the full wind.
Writes gen/physics/stage2b_variants.json.
Usage: python3 -I tools/physics/stage2b_variants.py"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import params as P
import shaft as S
import stage2b as B
import node_c as NC
import node_d as ND
import node_f as NF
import node_b as NB

C = P.CYCLE
K_BRAKE = 0.05          # N m per rad/s above w_s: the brake grips hard (a centrifugal friction governor)


def pick_chars():
    chs = S.characters()
    sel = {}
    def add(c, why):
        sel.setdefault(c['key'], (c, []))[1].append(why)
    add(max(chs, key=lambda c: (c['th'] ** 2 * S.MO.I_rot + c['dz'] ** 2 * S.MO.m_lift)), 'самый тяжёлый выбор')
    add([c for c in chs if c['idle']][0], 'пробел')
    pr = [c for c in chs if not c['idle']]
    add(min(pr, key=lambda c: (c['th'] + c['dz'], -c['w'])), 'самый лёгкий печатающий')
    add(max([c for c in pr if c['th'] < 0.2 and c['dz'] < 0.03], key=lambda c: c['w'], default=pr[0]), 'широкая у покоя')
    for pos in (0, 10):
        cs = [c for c in pr if c['pos'] == pos]
        if cs:
            add(max(cs, key=lambda c: c['dz']), f'позиция {pos}, верхний ряд')
            add(min(cs, key=lambda c: c['dz']), f'позиция {pos}, нижний ряд')
    for c in pr:
        if c['w'] == 0:
            add(c, 'мёртвый знак'); break
    add(max(pr, key=lambda c: c['w']), 'самая широкая')
    mids = [c for c in pr if c['pos'] in (3, 4, 6, 7)]
    for c in sorted(mids, key=lambda c: -c['weight'])[:3]:
        add(c, 'частый знак')
    return [v[0] | dict(why=v[1]) for v in sel.values()]


def summary(rows):
    ok = [r for r in rows if 'stall' not in r]
    d = dict(n=len(rows), stalled=[r['key'] for r in rows if 'stall' in r])
    if not ok:
        return d
    for k in ('1_blow_in_windows', '2_off_sheet_200', '3_carriage_settled', '4_feelers', '5_links_closed', 'C_rod_follows'):
        d[k] = [r['key'] for r in ok if r['res']['crit'][k] is False]
    bl = [r['res']['C']['impact_deg'] for r in ok if r['res']['C'].get('ok')]
    d['blow'] = [min(bl), max(bl)] if bl else None
    dm = [r['res']['D']['margin_ms'] for r in ok if r['res']['D'].get('settled')]
    d['D_margin_ms'] = [min(dm), max(dm)] if dm else None
    fa = [r['res']['F']['arrive_max_deg'] for r in ok if r['res']['F'].get('read')]
    d['feel'] = [min((x for x in fa if x), default=None), max((x for x in fa if x), default=None), sum(1 for x in fa if x is None)] if fa else None
    d['tape_min_N'] = min(r['res']['B']['tape_branch_min_N'] for r in ok)
    d['tape_need_N'] = max(r['res']['B']['tape_branch_max_N'] - NB.TAPE_PRELOAD for r in ok)
    d['ret_max_N'] = max(max(r['res']['B']['ret_rotate_max_N'], r['res']['B']['ret_lift_max_N']) for r in ok)
    d['follow_min_N'] = min(r['res']['follow']['min_margin_N'] for r in ok)
    d['E_stop_mJ'] = max(r['res']['E']['E_stop_mJ'] for r in ok)
    d['T'] = [min(r['T'] for r in ok), max(r['T'] for r in ok)]
    d['w_max'] = max(r['w_max'] for r in ok)
    return d


def run_set(chs, M, gov=None, nodes=None, release=160.0):
    rows = []
    for ch in chs:
        tr = S.trace(ch, M, gov=gov)
        if tr.stall is not None:
            rows.append(dict(key=ch['key'], stall=tr.stall)); continue
        nk = dict(nodes or {})
        cc = dict(nk.get('C', {})); cc['release'] = release; nk['C'] = cc
        res = B.run_law(ch, tr, nk)
        rows.append(dict(key=ch['key'], T=tr.T, w_max=float(tr.w.max()), res=res))
    return rows


def need_carriage_F(chs, M, gov, e=0.2, k=0.3e6):
    """The least carriage spring force with which every character's carriage settles 3 ms before D."""
    out = {}
    m, mw = ND.masses()
    for ch in chs:
        if ch['w'] <= 0:
            continue
        tr = S.trace(ch, M, gov=gov)
        if tr.stall is not None:
            continue
        ck = tr.clock(); window = ck.t(C['dog']) - ck.t(C['feed'][0]) - 3e-3
        lo, hi = 2.0, 40.0
        for _ in range(14):
            mid = math.sqrt(lo * hi)
            fs = ND.feed_settle(mid, ch['w'], m, mw, k=k, e=e, t_max=0.3)
            if fs['t_settled'] is not None and fs['t_settled'] <= window:
                hi = mid
            else:
                lo = mid
        fs = ND.feed_settle(hi, ch['w'], m, mw, k=k, e=e, t_max=0.3)
        r = ND.feed(hi, ch['w'], m, mw, k=k, e=e)
        out[ch['key']] = dict(F=hi, window_ms=window * 1e3 + 3, E_hit_mJ=r['E_hit_mJ'], F_finger_N=r['F_tooth_N'])
    return out


def need_feeler_springs(chs, M, gov):
    """The least spring of each feeler with which it sits on its tab by 145 deg on every law of the set."""
    import reader as RD
    need = {c: P.READ_F_SPRING[c] for c in P.READ_CH}
    for ch in chs:
        if ch['idle']:
            continue
        v = RD.code_v(ch['item'])
        if v is None:
            continue
        tr = S.trace(ch, M, gov=gov)
        if tr.stall is not None:
            continue
        for c, vv in zip(P.READ_CH, v):
            r = NF.run(c, vv, (tr.t, tr.phi), F_spring=need[c])
            if r.get('arrive_deg') is not None and r['arrive_deg'] <= 145.0:
                continue
            lo, hi = need[c], 20.0
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                r = NF.run(c, vv, (tr.t, tr.phi), F_spring=mid)
                if r.get('arrive_deg') is not None and r['arrive_deg'] <= 145.0:
                    hi = mid
                else:
                    lo = mid
            need[c] = hi
    return need


def release_scan(chs, Ms, gov):
    """The sear's release angle: the blow on every law of the set within 158..172 deg (ribbon window with 3 deg)."""
    out = []
    for rel in (148.0, 150.0, 152.0, 154.0, 156.0, 158.0, 160.0):
        bl = []
        for M in Ms:
            for ch in chs:
                if ch['idle']:
                    continue
                tr = S.trace(ch, M, gov=gov)
                if tr.stall is not None:
                    continue
                c = B.node_C(tr.clock(), ch, dict(release=rel))
                if c.get('ok'):
                    bl.append((c['impact_deg'], c['gap_200_mm'], c['after_200']))
        out.append(dict(release=rel, blow=[min(b[0] for b in bl), max(b[0] for b in bl)], gap_200_min=min(b[1] for b in bl),
                        after_200=sum(b[2] for b in bl)))
    return out


def main():
    t0 = time.time()
    chs = pick_chars()
    base = json.load(open(os.path.join(U.GEN, 'stage2b.json')))
    M_min = base['winds']['M_min']
    Ms = dict(M_min=M_min, mid=S.WINDS['mid'], M_max=S.WINDS['M_max'])
    out = dict(chars=[dict(key=c['key'], label=c['label'], pos=c['pos'], row=c['row'], w=c['w'], why=c['why']) for c in chs], winds=Ms,
               k_brake=K_BRAKE)
    govs = {'крыльчатка (как сейчас)': None}
    for Tf in (0.18, 0.22, 0.25):
        govs[f'тормоз с {Tf:.2f} с на свободный оборот'] = (2 * math.pi / Tf, K_BRAKE)
    res = {}
    for gname, gov in govs.items():
        res[gname] = {}
        for wn, M in Ms.items():
            res[gname][wn] = summary(run_set(chs, M, gov=gov))
        print(gname, {w: {k: v for k, v in d.items() if k in ('blow', 'D_margin_ms', 'feel', 'tape_min_N', 'follow_min_N', 'T', 'w_max')} for w, d in res[gname].items()},
              round(time.time() - t0))
    out['governors'] = res
    # targeted fixes on the capping governor at 0.22 s (and 0.18 s)
    fixes = {}
    for gname in ('тормоз с 0.22 с на свободный оборот', 'тормоз с 0.18 с на свободный оборот', 'тормоз с 0.25 с на свободный оборот'):
        gov = govs[gname]
        fx = {}
        fx['release'] = release_scan(chs, list(Ms.values()), gov)
        fx['carriage_F'] = {wn: need_carriage_F(chs, M, gov) for wn, M in Ms.items()}
        fx['carriage_F_e01'] = {wn: need_carriage_F(chs, M, gov, e=0.1) for wn, M in (('M_max', Ms['M_max']),)}
        fs = [need_feeler_springs(chs, M, gov) for M in Ms.values()]
        fx['feeler_springs'] = {c: max(f[c] for f in fs) for c in P.READ_CH}
        sm = res[gname]
        fx['tape_preload_N'] = max(sm[w].get('tape_need_N', 0) for w in sm) + 2.0
        fx['rod_spring_N'] = S.LJ['hammer']['rod_return_N'] - min(sm[w].get('follow_min_N', 0) for w in sm) + 0.3
        fixes[gname] = fx
        print(gname, 'release', fx['release'], 'F', {w: max((v['F'] for v in x.values()), default=None) for w, x in fx['carriage_F'].items()},
              'feelers', fx['feeler_springs'], 'tape', fx['tape_preload_N'], 'rod', fx['rod_spring_N'], round(time.time() - t0))
    out['fixes'] = fixes
    # the stall with a stronger rod spring (the following needs it) -- the least torque
    rod = max(f['rod_spring_N'] for f in fixes.values())
    save = S.LJ['hammer']['rod_return_N']
    S.LJ['hammer']['rod_return_N'] = rod; S._TAB.clear()
    out['tau_min_with_rod'] = dict(rod_N=rod, tau=max(B.tau_min(c) or 0 for c in chs))
    S.LJ['hammer']['rod_return_N'] = save; S._TAB.clear()
    out['time_s'] = time.time() - t0
    json.dump(out, open(os.path.join(U.GEN, 'stage2b_variants.json'), 'w'), ensure_ascii=False, indent=1,
              default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else bool(x) if isinstance(x, np.bool_) else str(x))
    print('tau with rod', out['tau_min_with_rod'], 'time', round(out['time_s']))


if __name__ == '__main__':
    main()
