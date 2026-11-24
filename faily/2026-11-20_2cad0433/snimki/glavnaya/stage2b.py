"""Stage 2b (spec §5б): the nodes on the shaft's real law.

For every character of the layout and the space, at every wind of the spring (§5б.5), the law of the revolution comes
from shaft.trace (all the loads at once); the nodes whose criteria stand in cycle degrees or depend on the shaft's speed
run on it through shaft.Clock:
  C  -- the hammer (node_c.simulate): the blow's angle, the rebounds, the face off the sheet by 200 deg, home by 330;
        the cocking rod's following of the fall (node_c.cam_torque, s'' w^2 + s' w');
  D  -- the carriage (node_d.feed_settle): the feed from 200 deg integrated through every rebound until it rests on U's
        finger; it must be settled 3 ms before D drops in (325 deg); the margin stop at the end of the line;
  B  -- the return rollers, the keeper and the closed tape (node_b.contact_forces) on the law;
  F  -- the feelers (node_f.run) on the law;
  E  -- the shaft never stops (w > 0) and the blow on the cycle latch at 360 deg.
Then the phase bands in ms (§5б.7), the Latin hypercube over the shaft's parameters (500), the margin stop, the paper
estimate of the frame and the variants for what fails (§5б.10).
Writes gen/physics/shaft_traces.npz, gen/physics/stage2b.json, gen/physics/stage2b_*.png, gen/tab_stage2b.tex.
Usage: python3 -I tools/physics/stage2b.py [--quick]"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import params as P
import shaft as S
import node_b as NB
import node_c as NC
import node_d as ND
import node_f as NF

C = P.CYCLE
QUICK = '--quick' in sys.argv
GEN = U.GEN
CAR_F = P.CAR_SPRING_N
PHI = np.round(np.arange(0.0, 360.0 + 1e-9, 0.1), 3)
MARGIN = 3.0                 # deg, criterion 1
SEGS = ((0, 30), (118, 145), (155, 175), (160, 200), (200, 325), (325, 360))
CMASS = NC.hammer_props(1.0)
C_NOM = dict(I=CMASS[1], m=CMASS[0], rc=CMASS[2], mu=0.25, t_c=0.3e-3, e=0.3, e_lip=0.3)
D_MASS = ND.masses()
I_ROT, M_LIFT, ROT_OWN, LIFT_OWN = NB.chain_masses()
F_RET_ROT = 4 * S.LJ['selection']['forces']['F_return'] + S.MASS['cam rod rotate']['m'] * U.G
F_RET_LIFT = 3 * S.LJ['selection']['forces']['F_return'] + S.MASS['cam rod lift']['m'] * U.G


def tau_of(M):
    return M * S.ETA_TRAIN / S.RATIO


def M_of(tau):
    return tau * S.RATIO / S.ETA_TRAIN


def tau_min(ch, lo=0.012, hi=0.09, n=20, **kw):
    """The least shaft torque at which the revolution completes for ch (bisection on stall)."""
    if S.trace(ch, wind=M_of(hi), **kw).stall is not None:
        return None
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if S.trace(ch, wind=M_of(mid), **kw).stall is None:
            hi = mid
        else:
            lo = mid
    return hi


# ---------------------------------------------------------------- the nodes on one law


def node_C(ck, ch, kw=None):
    if ch['idle']:
        return dict(idle=True)
    p = dict(C_NOM); p.update(kw or {})
    r = NC.simulate(**p, clock=ck)
    if not r.get('ok'):
        return dict(ok=False)
    c0 = r['contacts'][0]
    return dict(ok=True, impact_deg=c0['cycle_deg'], impact_ms=ck.t(c0['cycle_deg']) * 1e3, v=r['v_impact'], F_max=c0['F_max'],
                n_contacts=len(r['contacts']), last_sheet_deg=r['last_sheet_deg'], after_200=r['sheet_after_200'],
                gap_200_mm=r['gap_200_mm'], home_deg=r['home_deg'], track_mm=r['track_err_mm'],
                bounces_end_deg=r['last_sheet_deg'])


def node_C_follow(ck):
    f = NC.cam_torque(clocks={'law': ck})['follow'][0]
    return dict(min_margin_N=f['min_margin_N'], at_deg=f['at_deg'])


def node_D(ck, ch, k=0.3e6, e=0.2, mu=0.005, drag=0.1, F=CAR_F):
    if ch['w'] <= 0:
        return dict(feed=False)
    m, mw = D_MASS
    fs = ND.feed_settle(F, ch['w'], m, mw, mu=mu, k=k, e=e, drag=drag, t_max=0.3)
    t0 = ck.t(C['feed'][0]); t_dog = ck.t(C['dog'])
    window = t_dog - t0
    if fs['t_settled'] is None:
        return dict(feed=True, settled=False, window_ms=window * 1e3)
    off, after = ND.rebound_at(fs, window)
    return dict(feed=True, settled=True, t_hit_ms=fs['t_hit'] * 1e3, t_settled_ms=fs['t_settled'] * 1e3, window_ms=window * 1e3,
                margin_ms=(window - fs['t_settled']) * 1e3, settle_deg=ck.phi(t0 + fs['t_settled']), rebound_max_u=fs['rebound_max_teeth'],
                off_at_dog_u=off, rebound_after_dog_u=after)


def node_B(tr, ch):
    cf, _ = NB.contact_forces(tr.arr(), ch['th'], ch['dz'], I_ROT, M_LIFT, ROT_OWN, LIFT_OWN, F_RET_ROT, F_RET_LIFT)
    keep = ('main_rotate_max_N', 'main_lift_max_N', 'ret_rotate_max_N', 'ret_lift_max_N', 'ret_rotate_needed_in_relief_N',
            'ret_lift_needed_in_relief_N', 'keeper_max_N', 'tape_branch_min_N', 'tape_branch_max_N', 'slot_friction_rotate_mJ',
            'slot_friction_lift_mJ')
    out = {k: cf[k] for k in keep}
    out['closed'] = (out['ret_rotate_needed_in_relief_N'] <= 0 and out['ret_lift_needed_in_relief_N'] <= 0 and out['tape_branch_min_N'] > 0)
    return out


def node_F(tr, ch):
    import reader as RD
    v = RD.code_v(ch['item']) if not ch['idle'] else None
    if v is None:
        return dict(read=False)
    out = dict(read=True, ch={})
    for c, vv in zip(P.READ_CH, v):
        r = NF.run(c, vv, (tr.t, tr.phi))
        out['ch'][c] = dict(v=vv, arrive_deg=r.get('arrive_deg'), bounce_mm=r.get('bounce_mm'), short_mm=r.get('short_mm'))
    arr = [x['arrive_deg'] for x in out['ch'].values()]
    out['arrive_max_deg'] = None if None in arr else max(arr)
    out['bounce_max_mm'] = max((x['bounce_mm'] or 0.0) for x in out['ch'].values())
    return out


def node_E(tr):
    J_end = S.MO.J0
    w = float(tr.w[-1])
    E = 0.5 * J_end * w * w
    r = 8e-3; m_eq = J_end / r ** 2; v = w * r
    F_pad = v * math.sqrt(0.3e6 * m_eq)
    return dict(w_end=w, E_stop_mJ=E * 1e3, F_pad_N=F_pad, sigma_pad_MPa=F_pad / 18e-6 / 1e6, w_min=float(tr.w[tr.phi > 2].min()),
                w_min_deg=float(tr.phi[tr.phi > 2][np.argmin(tr.w[tr.phi > 2])]))


def criteria(c, d, b, f, e, follow, ch):
    """The seven criteria of §5б.7 (and the cocking rod's following); True / False / None (not applicable)."""
    k = {}
    if ch['idle'] or not c.get('ok'):
        k['1_blow_in_windows'] = None; k['2_off_sheet_200'] = None
    else:
        a = c['impact_deg']
        k['1_blow_in_windows'] = (C['ribbon'][0] + MARGIN <= a <= C['ribbon'][1] - MARGIN) and (C['detent'][0] + MARGIN <= a <= C['detent'][1] - MARGIN)
        k['2_off_sheet_200'] = c['after_200'] == 0 and c['gap_200_mm'] >= 5.0 and (c['home_deg'] or 999) <= 330.0
    k['3_carriage_settled'] = None if not d.get('feed') else bool(d.get('settled') and d['margin_ms'] >= 3.0 and d['off_at_dog_u'] < 1.0)
    k['4_feelers'] = None if not f.get('read') else bool(f['arrive_max_deg'] is not None and f['arrive_max_deg'] <= 145.0 and f['bounce_max_mm'] <= 0.5)
    k['5_links_closed'] = b['closed']
    k['6_shaft_turns'] = True
    k['C_rod_follows'] = None if follow is None else follow['min_margin_N'] >= 0.3
    return k


def run_law(ch, tr, nodes_kw=None):
    ck = tr.clock()
    nk = nodes_kw or {}
    c = node_C(ck, ch, nk.get('C'))
    d = node_D(ck, ch, **nk.get('D', {}))
    b = node_B(tr, ch)
    f = node_F(tr, ch)
    e = node_E(tr)
    fol = node_C_follow(ck) if nk.get('follow', True) else None
    return dict(C=c, D=d, B=b, F=f, E=e, follow=fol, crit=criteria(c, d, b, f, e, fol, ch))


def bands(ch, tr, res):
    ck = tr.clock()
    ms = lambda a: ck.t(a) * 1e3
    b = dict(start=0.0, out_end=ms(120.0), ribbon_end=ms(175.0), detent_out=ms(185.0), off_200=ms(200.0), feed_start=ms(200.0),
             dog=ms(325.0), wlatch=ms(345.0), u_out=ms(350.0), latch=ms(360.0))
    if res['F'].get('read') and res['F']['arrive_max_deg'] is not None:
        b['feelers'] = ms(res['F']['arrive_max_deg'])
    if res['C'].get('ok'):
        b['blow'] = res['C']['impact_ms']
    if res['D'].get('settled'):
        b['carriage_settled'] = b['feed_start'] + res['D']['t_settled_ms']
    return b


def law_row(ch, tr):
    ck = tr.clock()
    return dict(T=tr.T, segs={f'{a}-{b}': tr.seg(a, b) * 1e3 for a, b in SEGS},
                w_at={str(a): ck.w(a) for a in (30, 90, 120, 160, 200, 260, 325, 360)})


# ---------------------------------------------------------------- the whole run


def main():
    t_start = time.time()
    out = dict(spec='§5б', winds={k: v for k, v in S.WINDS.items()}, tau={k: tau_of(v) for k, v in S.WINDS.items()}, c_gov=S.CG_NOM,
               J0=S.MO.J0, notes=[])
    chs = S.characters()
    if QUICK:
        chs = [c for c in chs if c['key'] in ('E007', 'SP')] + [c for c in chs if (c['pos'], c['row']) in ((5, 0), (4, 5))][:2]
    # --- validation (§5б.8)
    v = S.validate()
    out['validation'] = dict(max_same_step_pct=max(abs(r['d_same_pct']) for r in v), rows=v,
                             crawl=[r for r in v if abs(r['d_01_pct']) > 1.0])
    # motor.py's farthest character at its own loads: does it stop?
    ch7 = [c for c in S.characters() if c['key'] == 'E007'][0]
    crawl = []
    for d in (0.25, 0.1, 0.05, 0.02, 0.01):
        tr = S.integrate(ch7, tau=S.MJ['tau_C'], cg=S.CG_NOM, mode='motor', dphi=d, motor_step=True)
        crawl.append(dict(dphi=d, T=tr.T, stall=tr.stall, w_min=float(tr.w[tr.phi > 20].min())))
    out['motor_crawl'] = dict(char='E007 (ungwe, позиция 0, ряд 6)', rows=crawl)
    # regression of C and D on a uniform clock against stage 2's numbers
    jc = json.load(open(os.path.join(GEN, 'node_c.json'))); jd = json.load(open(os.path.join(GEN, 'node_d.json')))
    reg = []
    for tag, dt in NC.DEG_T.items():
        a = NC.simulate(**C_NOM, clock=S.Clock.uniform(dt * 360)); b = jc[f'nominal_{tag}']
        reg.append(dict(node='C', case=tag, d_v=a['v_impact'] - b['v_impact'], d_deg=a['contacts'][0]['cycle_deg'] - b['contacts'][0]['cycle_deg'],
                        d_gap_mm=a['gap_200_mm'] - b['gap_200_mm'], d_home=(a['home_deg'] or 0) - (b['home_deg'] or 0)))
    for r in jd['options']['design']['rows']:
        a = ND.feed(jd['options']['design']['F'], r['w'], *D_MASS, clock=S.Clock.uniform(ND.DEG_T[r['speed']] * 360))
        reg.append(dict(node='D', case=f"w {r['w']} {r['speed']}", d_end=a['end_deg'] - r['end_deg'], d_dog=a['dog_done_deg'] - r['dog_done_deg']))
    out['regression'] = reg
    # energy residual and convergence
    conv = []
    for ch in [c for c in S.characters() if c['key'] in ('E007', 'SP')]:
        a = S.trace(ch, 'mid', dphi=0.1); b = S.trace(ch, 'mid', dphi=0.05)
        ca, cb = run_law(ch, a), run_law(ch, b)
        conv.append(dict(key=ch['key'], T=[a.T, b.T], dT_pct=100 * (b.T / a.T - 1), residual_mJ=a.book['residual'] * 1e3,
                         spring_mJ=a.book['spring'] * 1e3, residual_pct=100 * abs(a.book['residual']) / a.book['spring'],
                         blow=[ca['C'].get('impact_deg'), cb['C'].get('impact_deg')], settle=[ca['D'].get('t_settled_ms'), cb['D'].get('t_settled_ms')]))
    out['convergence'] = conv
    print('validation done', round(time.time() - t_start))
    # --- the least torque per character (stall threshold)
    tm = {}
    for ch in chs:
        tm[ch['key']] = tau_min(ch)
    worst_tau = max(x for x in tm.values() if x is not None)
    out['tau_min'] = dict(by_char=tm, worst=worst_tau, worst_char=max(tm, key=lambda k: tm[k] or 0), M_worst=M_of(worst_tau),
                          M_need=S.MJ['M_need'], ratio_to_tauC=worst_tau / S.MJ['tau_C'])
    winds = dict(S.WINDS)
    winds['M_min'] = M_of(worst_tau * 1.05)          # the least wind at which every character turns, + 5 %
    out['winds']['M_min'] = winds['M_min']; out['tau']['M_min'] = tau_of(winds['M_min'])
    order = ['M_need', 'M_avg', 'M_min', 'mid', 'M_max']
    print('tau_min done', round(time.time() - t_start), 'worst', worst_tau)
    # --- the nominal grid
    rows = []
    TR = np.full((len(chs), len(order), 3, len(PHI)), np.nan)
    for i, ch in enumerate(chs):
        for j, wd in enumerate(order):
            tr = S.trace(ch, winds[wd])
            row = dict(key=ch['key'], label=ch['label'], pos=ch['pos'], row=ch['row'], w=ch['w'], weight=ch['weight'], idle=ch['idle'], wind=wd)
            if tr.stall is not None:
                row.update(stall_deg=tr.stall)
                rows.append(row); continue
            TR[i, j, 0] = np.interp(PHI, tr.phi, tr.t); TR[i, j, 1] = np.interp(PHI, tr.phi, tr.w); TR[i, j, 2] = np.interp(PHI, tr.phi, tr.wd)
            res = run_law(ch, tr)
            row.update(law=law_row(ch, tr), book={k: float(v) * 1e3 for k, v in tr.book.items()}, **res, bands=bands(ch, tr, res))
            rows.append(row)
        if i % 10 == 0:
            print('grid', i, len(chs), round(time.time() - t_start))
    np.savez_compressed(os.path.join(GEN, 'shaft_traces.npz'), phi=PHI, traces=TR, keys=np.array([c['key'] for c in chs]), winds=np.array(order),
                        note='traces[char, wind, (t s, w rad/s, wdot rad/s2), phi 0..360 step 0.1 deg]; NaN where the shaft stops')
    out['grid'] = rows
    out['summary'] = summarize(rows, order, chs)
    print('grid done', round(time.time() - t_start))
    # --- U, D, W: how much the upper estimate moves the margins (§5б.11 p. 6)
    out['udw'] = udw_sensitivity(chs, winds)
    # --- start with speed (§5б.10 p. 6) and the trip of the next key
    out['start'] = start_case(chs, winds)
    # --- the margin stop
    out['margin_stop'] = margin_stop(chs, winds)
    # --- the frame on paper
    out['frame'] = frame_estimate(rows, out['margin_stop'])
    # --- variants for the stall (§5б.10 p. 4)
    out['variants'] = variants(chs, worst_tau)
    print('variants done', round(time.time() - t_start))
    # --- the Latin hypercube
    out['lhs'] = lhs(chs, winds, n=60 if QUICK else 500)
    print('lhs done', round(time.time() - t_start))
    out['time_s'] = time.time() - t_start
    json.dump(out, open(os.path.join(GEN, 'stage2b.json'), 'w'), ensure_ascii=False, indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else bool(x) if isinstance(x, np.bool_) else str(x))
    plots(rows, order, chs, TR, out)
    table(out)
    print_summary(out)


def summarize(rows, order, chs):
    s = {}
    for wd in order:
        rs = [r for r in rows if r['wind'] == wd]
        st = [r for r in rs if 'stall_deg' in r]
        ok = [r for r in rs if 'stall_deg' not in r]
        d = dict(n=len(rs), stalled=len(st), stall_deg=[min((r['stall_deg'] for r in st), default=None), max((r['stall_deg'] for r in st), default=None)])
        if ok:
            W = np.array([r['weight'] for r in ok]); T = np.array([r['law']['T'] for r in ok])
            d['T_avg_s'] = float((W * T).sum() / W.sum()); d['T_min_s'] = float(T.min()); d['T_max_s'] = float(T.max())
            d['cps_avg'] = 1 / d['T_avg_s']
            for k in ('1_blow_in_windows', '2_off_sheet_200', '3_carriage_settled', '4_feelers', '5_links_closed', '6_shaft_turns', 'C_rod_follows'):
                vals = [r['crit'][k] for r in ok if r['crit'][k] is not None]
                d[f'fail_{k}'] = [r['key'] for r in ok if r['crit'][k] is False]
                d[f'n_{k}'] = len(vals)
            bl = [r['C']['impact_deg'] for r in ok if r['C'].get('ok')]
            d['blow_deg'] = [min(bl), max(bl)] if bl else None
            dm = [r['D']['margin_ms'] for r in ok if r['D'].get('settled')]
            d['D_margin_ms'] = [min(dm), max(dm)] if dm else None
            d['D_unsettled'] = [r['key'] for r in ok if r['D'].get('feed') and not r['D'].get('settled')]
            fa = [r['F']['arrive_max_deg'] for r in ok if r['F'].get('read') and r['F']['arrive_max_deg'] is not None]
            d['feelers_deg'] = [min(fa), max(fa)] if fa else None
            d['bounce_max_mm'] = max((r['F']['bounce_max_mm'] for r in ok if r['F'].get('read')), default=None)
            d['gap_200_min_mm'] = min((r['C']['gap_200_mm'] for r in ok if r['C'].get('ok')), default=None)
            d['home_max_deg'] = max((r['C']['home_deg'] or 999 for r in ok if r['C'].get('ok')), default=None)
            d['follow_min_N'] = min(r['follow']['min_margin_N'] for r in ok)
            d['ret_max_N'] = dict(rotate=max(r['B']['ret_rotate_max_N'] for r in ok), lift=max(r['B']['ret_lift_max_N'] for r in ok),
                                  main_rotate=max(r['B']['main_rotate_max_N'] for r in ok), main_lift=max(r['B']['main_lift_max_N'] for r in ok))
            d['keeper_max_N'] = max(r['B']['keeper_max_N'] for r in ok)
            d['tape_branch_N'] = [min(r['B']['tape_branch_min_N'] for r in ok), max(r['B']['tape_branch_max_N'] for r in ok)]
            d['E_stop_mJ'] = max(r['E']['E_stop_mJ'] for r in ok); d['F_pad_N'] = max(r['E']['F_pad_N'] for r in ok)
            d['sigma_pad_MPa'] = max(r['E']['sigma_pad_MPa'] for r in ok)
            d['w_max'] = max(max(r['law']['w_at'].values()) for r in ok)
            d['segs_ms'] = {k: [min(r['law']['segs'][k] for r in ok), max(r['law']['segs'][k] for r in ok)] for k in ok[0]['law']['segs']}
            d['loads_mJ'] = [min(r['book']['loads'] for r in ok), max(r['book']['loads'] for r in ok)]
        s[wd] = d
    return s


def udw_sensitivity(chs, winds):
    pick = [c for c in chs if c['key'] in ('E007', 'SP')] + [c for c in chs if (c['pos'], c['row']) == (5, 0) and not c['idle']][:1]
    rows = []
    for ch in pick:
        for wd in ('M_min', 'M_max'):
            r = {}
            for u in ('none', 'upper'):
                tr = S.trace(ch, winds[wd], udw=u)
                if tr.stall is not None:
                    r[u] = dict(stall=tr.stall); continue
                res = run_law(ch, tr, dict(follow=False))
                r[u] = dict(T=tr.T, D_margin_ms=res['D'].get('margin_ms'), blow=res['C'].get('impact_deg'), feel=res['F'].get('arrive_max_deg'))
            dm = [r[u].get('D_margin_ms') for u in ('none', 'upper')]
            ch_pct = 100 * (dm[1] / dm[0] - 1) if dm[0] and dm[1] else None
            rows.append(dict(key=ch['key'], wind=wd, **r, D_margin_change_pct=ch_pct,
                             T_change_pct=100 * (r['upper'].get('T', 0) / r['none']['T'] - 1) if r['none'].get('T') and r['upper'].get('T') else None))
    tmn = {u: tau_min([c for c in chs if c['key'] == 'E007'][0], udw=u) if any(c['key'] == 'E007' for c in chs) else None for u in ('none', 'upper')}
    return dict(rows=rows, tau_min_E007=tmn)


def start_case(chs, winds):
    """Start with the speed of the previous revolution's end: an upper bound. Is it a working case? The keyboard lock
    holds every lever from 5 to 345 deg (§«Блокировка клавиатуры»); the next key then has to travel 15.5 mm to trip the
    cycle, while the shaft runs the last 15 deg to the latch."""
    A = json.load(open(os.path.join(GEN, 'node_a.json')))
    k = A['буква k24']
    m_eff = k['m_eff_g'] * 1e-3
    F_fing = 3.0
    F_res = max(k['press'][2]['F_static'])           # the key's own resistance near the end of its travel
    t_trip = math.sqrt(2 * 15.5e-3 * m_eff / (F_fing - F_res))
    rows = []
    for ch in [c for c in chs if c['key'] in ('E007', 'SP')] + [c for c in chs if (c['pos'], c['row']) == (5, 0) and not c['idle']][:1]:
        for wd in ('M_min', 'M_max'):
            tr = S.trace(ch, winds[wd])
            if tr.stall is not None:
                continue
            t_last = tr.seg(345.0, 360.0)
            tr2 = S.trace(ch, winds[wd], w0=float(tr.w[-1]))
            r2 = run_law(ch, tr2, dict(follow=False)) if tr2.stall is None else None
            rows.append(dict(key=ch['key'], wind=wd, t_345_360_ms=t_last * 1e3, w_end=float(tr.w[-1]), T_from_run=tr2.T,
                             blow=r2['C'].get('impact_deg') if r2 else None, D_margin_ms=r2['D'].get('margin_ms') if r2 else None,
                             crit=r2['crit'] if r2 else None))
    return dict(key_trip_ms=t_trip * 1e3, finger_N=F_fing, key_resist_N=F_res, lock_deg=(5, 345), rows=rows,
                shaft_always_stops=all(r['t_345_360_ms'] < t_trip * 1e3 for r in rows))


def margin_stop(chs, winds):
    """The right margin stop meets the abutment at the end of the line: the carriage under its spring (4 N) after a
    feed of w units, a printed PETG stop on a printed abutment (no pad): face 5.5 x 3 mm."""
    m, mw = D_MASS
    A = 5.5e-6 * 3e-6 / 1e-6                       # m2
    A = 5.5e-3 * 3e-3
    rows = []
    for k_stop, lab in ((1.5e6, 'печать, мягко'), (5.5e6, 'печать, E·A/L, L = 6 мм')):
        for e in (0.3, 0.5, 0.7):
            k_tooth = k_stop * (ND.R_P / ND.R_T) ** 2      # feed() takes k at the tooth radius
            r = ND.feed(CAR_F, 16, m, mw, k=k_tooth, e=e)
            fs = ND.feed_settle(CAR_F, 16, m, mw, k=k_tooth, e=e, t_max=0.4)
            F_rack = r['F_tooth_N'] * ND.R_T / ND.R_P
            rows.append(dict(k=k_stop, case=lab, e=e, E_mJ=r['E_hit_mJ'], F_N=F_rack, sigma_MPa=F_rack / A / 1e6,
                             rebound_u=fs['rebound_max_teeth'], v_hit=r['v_hit']))
    old = json.load(open(os.path.join(GEN, 'node_d.json'))).get('margin_stop')
    return dict(F=CAR_F, w=16, face_mm2=A * 1e6, rows=rows, stage2_old=old,
                note='отскок от упора меньше зуба рейки (6u) — каретку держит собачка Д; за поле не выходит, если отскок < 6u')


def frame_estimate(rows, ms):
    """§5б.10 p. 5, on paper: the blows against the frame. An impulse J shorter than the frame's period deflects it by
    J / sqrt(k m); k of a 2020 beam between its ends (aluminium, I = 0.69 cm4), m its share of the machine."""
    MASS = S.MASS
    m_total = sum(x['m'] for x in MASS.values())
    blows = []
    ok = [r for r in rows if 'stall_deg' not in r and r['C'].get('ok')]
    F_h = max(r['C']['F_max'] for r in ok)
    blows.append(dict(what='молоток', F_N=F_h, dt_ms=0.3, J=F_h * 0.3e-3))
    blows.append(dict(what='палец U', F_N=134.0, dt_ms=2.0, J=134.0 * 2e-3))
    Fl = max(r['E']['F_pad_N'] for r in ok)
    blows.append(dict(what='защёлка цикла', F_N=Fl, dt_ms=1.0, J=Fl * 1e-3))
    Fm = max(x['F_N'] for x in ms['rows'])
    blows.append(dict(what='упор поля', F_N=Fm, dt_ms=1.0, J=Fm * 1e-3))
    E_al, I_2020 = 70e9, 0.69e-8
    out = []
    for L in (0.3, 0.5):
        k = 48 * E_al * I_2020 / L ** 3
        for b in blows:
            m_eff = 0.5 * 0.5 * L + 1.0              # half the beam (0.5 kg/m) and ~1 kg of the unit on it (assumption)
            d_dyn = b['J'] / math.sqrt(k * m_eff)
            out.append(dict(span_m=L, k_N_per_m=k, **b, d_dyn_mm=min(d_dyn, b['F_N'] / k) * 1e3, d_static_mm=b['F_N'] / k * 1e3))
    return dict(m_model_kg=m_total, rows=out, limit_mm=0.05,
                note='оценка на бумаге: балка 2020 между узлами рамы, импульс короче периода — прогиб J/√(k·m); не более статического F/k')


def variants(chs, worst_tau):
    """§5б.10 p. 4: the shaft stops on the cocking at M_need. The least torque for every variant (over the characters
    that set it: the farthest, the space and the nearest)."""
    import parts as PT
    pick = [c for c in chs if c['key'] in ('E007', 'SP')] + [c for c in chs if (c['pos'], c['row']) in ((5, 0), (0, 0), (10, 7))][:3]
    out = []
    base = {c['key']: tau_min(c) for c in pick}
    out.append(dict(name='как есть', tau_min=max(v for v in base.values() if v), by=base))
    # rod spring lighter: 2.5 -> 1.0 N (the following of the fall must keep >= 0.3 N: checked on the law below)
    save = S.LJ['hammer']['rod_return_N']
    for F in (1.5, 1.0):
        S.LJ['hammer']['rod_return_N'] = F; S._TAB.clear()
        by = {c['key']: tau_min(c) for c in pick}
        trs = [S.trace(c, M_of(max(v for v in by.values() if v) * 1.05)) for c in pick]
        NC.LJ['rod_return_N'] = F
        fol = min(node_C_follow(t.clock())['min_margin_N'] for t in trs if t.stall is None)
        NC.LJ['rod_return_N'] = save
        out.append(dict(name=f'пружина толкателя взвода {F} Н (было 2,5)', tau_min=max(v for v in by.values() if v), by=by, follow_min_N=fol))
    S.LJ['hammer']['rod_return_N'] = save; S._TAB.clear()
    # the ribbon's spring and weight not on the cocking's hump: the ribbon's ramp later (40 deg instead of 80)
    rp = PT.RAMP['ribbon']
    PT.RAMP['ribbon'] = 40.0; S._TAB.clear()
    by = {c['key']: tau_min(c) for c in pick}
    out.append(dict(name='подъём ленты за 40° вместо 80° (115–155°)', tau_min=max(v for v in by.values() if v), by=by,
                    note='угол давления кулачка ленты растёт: проверить (ред. 0.9c держала его ниже 45° на 80°)'))
    PT.RAMP['ribbon'] = rp; S._TAB.clear()
    # both
    S.LJ['hammer']['rod_return_N'] = 1.0; PT.RAMP['ribbon'] = 40.0; S._TAB.clear()
    by = {c['key']: tau_min(c) for c in pick}
    out.append(dict(name='пружина толкателя 1 Н и подъём ленты за 40°', tau_min=max(v for v in by.values() if v), by=by))
    S.LJ['hammer']['rod_return_N'] = save; PT.RAMP['ribbon'] = rp; S._TAB.clear()
    # no U/D/W estimate (lower bound of what the real parts can save)
    by = {c['key']: tau_min(c, udw='none') for c in pick}
    out.append(dict(name='без оценки U, Д, W (нижняя граница)', tau_min=max(v for v in by.values() if v), by=by))
    # the cost of raising tau_C: the spring works from M_max down to M_need' (linear torque over the turns, an assumption)
    Mx = S.SPR['M_max']; Mn = S.MJ['M_need']
    for v in out:
        Mv = M_of(v['tau_min'])
        v['M_need_new'] = Mv
        v['energy_left_pct'] = 100 * (Mx ** 2 - Mv ** 2) / (Mx ** 2 - Mn ** 2) if Mv < Mx else 0.0
    return out


def lhs(chs, winds, n=500):
    rng = np.random.default_rng(25)
    W = np.array([c['weight'] for c in chs]); W = W / W.sum()
    u = (rng.permuted(np.tile(np.arange(n), (10, 1)), axis=1).T + rng.random((n, 10))) / n
    rows = []
    Mlo, Mhi = S.WINDS['M_need'], S.WINDS['M_max']
    for x in u:
        ch = chs[int(np.searchsorted(np.cumsum(W), rng.random()))]
        M = Mlo + (Mhi - Mlo) * x[0]
        kw = dict(cg=S.CG_NOM * (0.8 + 0.4 * x[1]), J0=S.MO.J0 * (0.9 + 0.2 * x[2]), eta=0.7 + 0.2 * x[3], fric=0.5 * 4 ** x[4])
        run = x[5] > 0.5
        tr = S.trace(ch, M, **kw)
        if tr.stall is None and run:
            tr = S.trace(ch, M, w0=float(tr.w[-1]), **kw)
        row = dict(key=ch['key'], M=M, **{k: float(v) for k, v in kw.items()}, run=bool(run))
        if tr.stall is not None:
            row['stall_deg'] = tr.stall; rows.append(row); continue
        nk = dict(C=dict(e=0.1 + 0.6 * x[6], t_c=(0.1 + 0.4 * x[7]) * 1e-3), D=dict(k=10 ** (math.log10(0.15e6) + x[8] * math.log10(4)), e=0.1 + 0.25 * x[9]))
        res = run_law(ch, tr, nk)
        row.update(T=tr.T, crit=res['crit'], blow=res['C'].get('impact_deg'), D_margin_ms=res['D'].get('margin_ms'),
                   feel=res['F'].get('arrive_max_deg'), follow=res['follow']['min_margin_N'], E_stop_mJ=res['E']['E_stop_mJ'],
                   gap_200=res['C'].get('gap_200_mm'))
        rows.append(row)
    ok = [r for r in rows if 'stall_deg' not in r]
    agg = dict(n=n, stalled=len(rows) - len(ok), stall_M_max=max((r['M'] for r in rows if 'stall_deg' in r), default=None),
               M_all_turn=min((r['M'] for r in ok), default=None))
    for k in ('1_blow_in_windows', '2_off_sheet_200', '3_carriage_settled', '4_feelers', '5_links_closed', 'C_rod_follows'):
        agg[f'fail_{k}'] = sum(1 for r in ok if r['crit'][k] is False)
        agg[f'n_{k}'] = sum(1 for r in ok if r['crit'][k] is not None)
    for k in ('1_blow_in_windows', '3_carriage_settled'):
        bad = [r for r in ok if r['crit'][k] is False]
        agg[f'worst_{k}'] = sorted(bad, key=lambda r: r['M'], reverse=True)[:5]
    agg['blow_range'] = [min(r['blow'] for r in ok if r['blow']), max(r['blow'] for r in ok if r['blow'])] if any(r['blow'] for r in ok) else None
    agg['D_margin_min_ms'] = min((r['D_margin_ms'] for r in ok if r['D_margin_ms'] is not None), default=None)
    agg['rows'] = rows
    return agg


def plots(rows, order, chs, TR, out):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cols = {'M_need': '#7a7a7a', 'M_avg': '#b0b0b0', 'M_min': '#2a6f97', 'mid': '#3a8a50', 'M_max': '#c44536'}
    lab = dict(S.WIND_LABEL); lab['M_min'] = 'наименьший рабочий'
    picks = [('SP', 'пробел'), ('near', 'ближняя (5, 0)'), ('mid', 'средняя (4, 5)'), ('E007', 'дальняя (0, 6)')]
    idx = {}
    for i, c in enumerate(chs):
        if c['key'] == 'SP': idx['SP'] = i
        if c['key'] == 'E007': idx['E007'] = i
        if (c['pos'], c['row']) == (5, 0) and not c['idle'] and 'near' not in idx: idx['near'] = i
        if (c['pos'], c['row']) == (4, 5) and 'mid' not in idx: idx['mid'] = i
    fig, ax = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True, sharey=True)
    for a_, (k, name) in zip(ax.flat, picks):
        if k not in idx:
            continue
        i = idx[k]
        for j, wd in enumerate(order):
            if np.isnan(TR[i, j, 1, 0]):
                st = [r for r in rows if r['key'] == chs[i]['key'] and r['wind'] == wd]
                if st and 'stall_deg' in st[0]:
                    a_.axvline(st[0]['stall_deg'], color=cols[wd], ls='--', lw=0.8)
                continue
            a_.plot(PHI, TR[i, j, 1], color=cols[wd], lw=1, label=lab[wd])
        for x in (120, 160, 200, 325, 345):
            a_.axvline(x, color='k', lw=0.3, ls=':')
        a_.set_title(name, fontsize=9)
    ax[1, 0].set_xlabel('угол вала, °'); ax[1, 1].set_xlabel('угол вала, °'); ax[0, 0].set_ylabel('ω, рад/с'); ax[1, 0].set_ylabel('ω, рад/с')
    ax[0, 0].legend(fontsize=7)
    fig.suptitle('Ступень 2б: скорость циклового вала по углу при разных заводах (пунктир — вал встал)', fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(GEN, 'stage2b_omega.png'), dpi=130); plt.close(fig)
    # phase bands of the worst characters at M_min and M_max
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ok = [r for r in rows if 'stall_deg' not in r and r['wind'] in ('M_min', 'M_max')]
    ok.sort(key=lambda r: (r['D'].get('margin_ms') if r['D'].get('settled') else -99))
    sel = ok[:6] + [r for r in ok if r['key'] == 'SP'][:1]
    for y, r in enumerate(sel):
        b = r['bands']
        ax.barh(y, b['latch'], color='#eeeeee', edgecolor='#999999', height=0.6)
        ax.barh(y, b['dog'] - b['feed_start'], left=b['feed_start'], color='#cfe0ee', height=0.6)
        if 'carriage_settled' in b:
            ax.plot([b['carriage_settled']], [y], 'v', color='#2a6f97')
        if 'blow' in b:
            ax.plot([b['blow']], [y], 'o', color='#c44536', ms=4)
        if 'feelers' in b:
            ax.plot([b['feelers']], [y], 's', color='#3a8a50', ms=4)
        ax.plot([b['dog']], [y], '|', color='k', ms=12)
    ax.set_yticks(range(len(sel))); ax.set_yticklabels([f"{r['label']} ({r['pos']}, {r['row']}) {r['wind']}" for r in sel], fontsize=7)
    ax.set_xlabel('время от старта оборота, мс')
    ax.set_title('Полосы событий (худшие по запасу каретки): ● удар, ■ щупы, ▼ каретка успокоилась, | собачка Д (325°); голубое — 200–325°', fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(GEN, 'stage2b_bands.png'), dpi=130); plt.close(fig)
    # margins distributions
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    for wd in ('M_min', 'mid', 'M_max'):
        rs = [r for r in rows if r['wind'] == wd and 'stall_deg' not in r]
        b1 = [min(r['C']['impact_deg'] - (C['ribbon'][0]), (C['ribbon'][1]) - r['C']['impact_deg']) for r in rs if r['C'].get('ok')]
        d3 = [r['D']['margin_ms'] for r in rs if r['D'].get('settled')]
        f4 = [145.0 - r['F']['arrive_max_deg'] for r in rs if r['F'].get('read') and r['F']['arrive_max_deg'] is not None]
        for a_, v in zip(ax, (b1, d3, f4)):
            a_.hist(v, bins=20, alpha=0.5, color=cols[wd], label=lab[wd])
    ax[0].axvline(MARGIN, color='k', lw=0.8); ax[1].axvline(3.0, color='k', lw=0.8); ax[2].axvline(0.0, color='k', lw=0.8)
    ax[0].set_xlabel('удар: запас до края окна ленты, °'); ax[1].set_xlabel('каретка: запас до собачки Д, мс'); ax[2].set_xlabel('щупы: запас до 145°, °')
    ax[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(GEN, 'stage2b_margins.png'), dpi=130); plt.close(fig)


def fmt(x, n=1):
    if x is None:
        return '---'
    return f'{x:.{n}f}'.replace('.', '{,}')


def table(out):
    s = out['summary']
    order = [w for w in ('M_need', 'M_avg', 'M_min', 'mid', 'M_max') if w in s]
    lab = {'M_need': 'конец завода', 'M_avg': 'средний', 'M_min': 'наименьший рабочий', 'mid': '½(ср.\\,+\\,полн.)', 'M_max': 'полный'}
    L = ['\\begin{table}[h]\\centering\\small', '\\caption{Ступень~2б: законы вала и узлы на них по заводам пружины (все знаки и пробел)}\\label{tab:stage2b}',
         '\\begin{tabular}{l' + 'r' * len(order) + '}', '\\toprule',
         'завод & ' + ' & '.join(lab[w] for w in order) + ' \\\\',
         'момент на валу, мН·м & ' + ' & '.join(fmt(out['tau'][w] * 1e3) for w in order) + ' \\\\', '\\midrule']
    def rowv(name, f):
        L.append(name + ' & ' + ' & '.join(f(s[w]) for w in order) + ' \\\\')
    rowv('вал встаёт, знаков', lambda d: str(d['stalled']) + (f" ({fmt(d['stall_deg'][0], 0)}--{fmt(d['stall_deg'][1], 0)}°)" if d['stalled'] else ''))
    rowv('цикл, с: среднее', lambda d: fmt(d.get('T_avg_s'), 3))
    rowv('\\quad быстрее / дольше всех', lambda d: (fmt(d.get('T_min_s'), 3) + ' / ' + fmt(d.get('T_max_s'), 3)) if 'T_min_s' in d else '---')
    rowv('удар, °', lambda d: (fmt(d['blow_deg'][0]) + '--' + fmt(d['blow_deg'][1])) if d.get('blow_deg') else '---')
    rowv('боёк от листа в 200°, мм, не меньше', lambda d: fmt(d.get('gap_200_min_mm')))
    rowv('каретка: запас до Д, мс', lambda d: (fmt(d['D_margin_ms'][0]) + '--' + fmt(d['D_margin_ms'][1])) if d.get('D_margin_ms') else '---')
    rowv('\\quad не успевает (запас < 3 мс)', lambda d: str(len(d.get('fail_3_carriage_settled', []))) if 'T_avg_s' in d else '---')
    rowv('щупы на зубцах, °', lambda d: (fmt(d['feelers_deg'][0]) + '--' + fmt(d['feelers_deg'][1])) if d.get('feelers_deg') else '---')
    rowv('толкатель взвода: запас, Н', lambda d: fmt(d.get('follow_min_N'), 2))
    rowv('обратные ролики, Н (пов. / подъём)', lambda d: (fmt(d['ret_max_N']['rotate'], 0) + ' / ' + fmt(d['ret_max_N']['lift'], 0)) if d.get('ret_max_N') else '---')
    rowv('ветви ленты, Н', lambda d: (fmt(d['tape_branch_N'][0]) + '--' + fmt(d['tape_branch_N'][1])) if d.get('tape_branch_N') else '---')
    rowv('удар о защёлку, мДж', lambda d: fmt(d.get('E_stop_mJ')))
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}']
    open(os.path.join(U.ROOT, 'gen', 'tab_stage2b.tex'), 'w').write('\n'.join(L) + '\n')


def print_summary(out):
    print('tau_min worst', out['tau_min']['worst'], out['tau_min']['worst_char'], 'M', out['tau_min']['M_worst'])
    for wd, d in out['summary'].items():
        print(wd, {k: v for k, v in d.items() if not k.startswith('segs')})
    print('udw', out['udw']); print('start', {k: v for k, v in out['start'].items() if k != 'rows'})
    print('margin stop', out['margin_stop']['rows'])
    print('variants', [(v['name'], round(v['tau_min'] * 1e3, 2), round(v['M_need_new'], 2), round(v['energy_left_pct'], 1)) for v in out['variants']])
    print('lhs', {k: v for k, v in out['lhs'].items() if k not in ('rows',)})


if __name__ == '__main__':
    main()
