"""Stage 1: the full run and its outputs (spec §4.9): gen/physics/stage1.json, stage1_missing.csv, stage1_*.png,
gen/tab_stage1.tex; fills 'axial' of revolute joints in data/joints.json from the mobility.
Usage: python3 -I tools/physics/stage1_run.py"""
import sys, os, json, math, time, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
from scipy.optimize import linprog
import stage1 as S1
import meshes as MS
import classify as CL

SETTLE_ATT = {'рабочее', 'наклон 15° вперёд', 'наклон 15° назад', 'наклон 15° влево', 'наклон 15° вправо',
              'перенос 30° вперёд', 'перенос 30° назад', 'перенос 30° влево', 'перенос 30° вправо', 'вверх дном'}


def symmetric_axis(S, ids, M):
    """Axis of rotational symmetry of a body (two equal principal moments), or None."""
    I = np.zeros((3, 3)); m = 0.0; c = np.zeros(3)
    for i in ids:
        m += M[i]['m']; c += M[i]['m'] * np.array(M[i]['c'])
    c /= max(m, 1e-12)
    for i in ids:
        Ii = np.array(M[i]['I']); ci = np.array(M[i]['c']) - c
        I += Ii + M[i]['m'] * (ci @ ci * np.eye(3) - np.outer(ci, ci)) if np.any(Ii) else 0
    w, v = np.linalg.eigh(I)
    if w[2] <= 0:
        return None
    for k, (p, q) in enumerate(((1, 2), (0, 2), (0, 1))):
        if abs(w[p] - w[q]) <= 0.02 * w[2]:
            return c, v[:, k]
    return None


def harmless(D, b, tw):
    """A spin of a body about its own axis of symmetry (rod, roller, bushing, shaft with its gears)."""
    if tw['kind'] != 'поворот':
        return False
    ids = list(np.nonzero(D['body'] == b)[0])
    sa = symmetric_axis(D['S'], ids, D['M'])
    if sa is None:
        return False
    c, a = sa
    d = np.array(tw['d'])
    if abs(d @ a) < 0.995:
        return False
    p = np.array(tw['p_mm']) * U.MM
    off = (p - c) - ((p - c) @ a) * a
    return bool(np.linalg.norm(off) < 1.5e-3)


def mobility(D):
    mob = S1.local_mobility(D['nb'], D['cont'], D['joints'], D['c'])
    S = D['S']
    out = []
    for b in range(1, D['nb']):
        ids = np.nonzero(D['body'] == b)[0]
        movs = sorted({S.parts[i]['mov'] for i in ids})
        tws = [S1.describe_twist(v, D['c'][b]) for v in mob[b]]
        for t in tws:
            t['harmless'] = harmless(D, b, t)
        fixed = movs == ['fixed']
        extra = [t for t in tws if not t['harmless']] if fixed else []
        out.append(dict(body=b, parts=[S.names[i] for i in ids][:8], nparts=len(ids), mov=movs[:4], dof=len(tws), twists=tws,
                        fixed=fixed, extra=len(extra)))
    return out


def attitudes(D, wsp, settle_set=SETTLE_ATT):
    res = {}
    for name, g in S1.ATTITUDES:
        wg = S1.gravity_wrench(D['m'], D['c'], D['nb'], g, D['flex']) + wsp
        r = S1.local_hold(D, g, wsp)
        r0 = S1.local_hold(D, g, wsp, zero_mu=True)
        bad = [b for b, v in r.items() if not v['ok']]
        fric = [b for b, v in r0.items() if not v['ok'] and r[b]['ok']]
        items = []
        for b in bad:
            it = dict(body=b, parts=S1.body_names(D, b)[:6], mass_g=round(D['m'][b] * 1e3, 2), slack_F=r[b]['slack_F'], slack_M=r[b]['slack_M'])
            if name in settle_set:
                st = S1.settle_iter(D, b, r[b], wg[6 * b:6 * b + 6], g)
                it.update(verdict=st['verdict'], total_mm=st['total_mm'], total_deg=st['total_deg'],
                          path=[[p[0], p[1], p[2], p[3]] for p in st['path']])
            items.append(it)
        res[name] = dict(g=list(g), unheld=items, friction_only=[dict(body=b, parts=S1.body_names(D, b)[:4], mass_g=round(D['m'][b] * 1e3, 2))
                                                                   for b in fric])
        print(D['mode'], name, 'unheld', len(bad), 'friction-only', len(fric), flush=True)
    return res


def fastener_loads(D, J, min_mass=0.015):
    """Load on each fastener of the parts heavier than min_mass (kg) in every attitude: the smallest fastener reaction
    (L1) that holds the part on its contacts (spec §4.7). Moment reactions count as forces at 10 mm."""
    S = D['S']; M = D['M']
    fj = {}
    for j in J['joints']:
        if j['type'] == 'rigid' and j.get('fastener') not in (None, 'print'):
            fj.setdefault(j['a'], []).append(j); fj.setdefault(j['b'], []).append(j)
    by = {}
    for c in D['P']:
        by.setdefault(c['i'], []).append(c); by.setdefault(c['k'], []).append(c)
    out = []
    pmap = {(p['a'], p['b']): p for p in D['pairs']}
    for nm, js in fj.items():
        i = S.idx[nm]
        if M[i]['m'] < min_mass or S1.is_flex(nm):
            continue
        partners = {j['b'] if j['a'] == nm else j['a'] for j in js}
        rows = []
        for c in by.get(i, []):
            for x, n, s in zip(c['X'], c['N'], c['side']):
                if (s == 0 and c['i'] == i) or (s == 1 and c['k'] == i):
                    rows.append((x, n, c['mu']))
                else:
                    rows.append((x, -n, c['mu']))
        fpts = []
        for j in js:
            o = j['b'] if j['a'] == nm else j['a']
            pr = pmap.get((j['a'], j['b'])) or pmap.get((j['b'], j['a']))
            x = (np.array(pr['pa']) + np.array(pr['pb'])) / 2 * U.MM if pr else np.array(M[i]['c'])
            fpts.append((o, j.get('fastener'), j['status'], x))
        worst = {}
        for name, g in S1.ATTITUDES:
            F = M[i]['m'] * U.G * np.asarray(g, float)
            wb = np.r_[np.cross(M[i]['c'], F), F]
            cols, lb, cost = [], [], []
            for x, n, mu in rows:
                e1 = np.cross(n, [1, 0, 0] if abs(n[0]) < 0.9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
                for d in (n + mu * e1, n - mu * e1, n + mu * e2, n - mu * e2):
                    cols.append(np.r_[np.cross(x, d), d]); lb.append(0.0); cost.append(0.0)
            nC = len(cols)
            for o, f, st, x in fpts:
                for q in range(6):
                    e = np.zeros(6)
                    if q < 3:
                        e[q] = 1.0                       # pure moment
                        w = e; cst = 100.0               # N m -> N at 10 mm
                    else:
                        d = np.eye(3)[q - 3]; w = np.r_[np.cross(x, d), d]; cst = 1.0
                    for sg in (1, -1):
                        cols.append(sg * w); lb.append(0.0); cost.append(cst)
            A = np.array(cols).T
            r = linprog(cost, A_eq=A, b_eq=-wb, bounds=[(0, None)] * len(cols), method='highs')
            if r.status != 0:
                continue
            xs = r.x[nC:].reshape(len(fpts), 6, 2)
            for k, (o, f, st, x) in enumerate(fpts):
                v = xs[k, :, 0] - xs[k, :, 1]
                load = float(np.linalg.norm(v[3:]) + 100.0 * np.linalg.norm(v[:3]))
                if load > worst.get(o, (0, ''))[0]:
                    worst[o] = (load, name)
        for o, f, st, x in fpts:
            ld, att = worst.get(o, (0.0, ''))
            allow = U.FASTENER_ALLOW.get(f or '', None)
            if f == 'screw M3' and st != 'modeled':
                allow = U.FASTENER_ALLOW['screw M3']
            out.append(dict(part=nm, to=o, fastener=f, status=st, mass_g=round(M[i]['m'] * 1e3, 1), load_N=round(ld, 3), attitude=att,
                            allow_N=allow, margin=(round(allow / ld, 1) if allow and ld > 1e-9 else None)))
    seen = set(); uniq = []
    for r in sorted(out, key=lambda r: -r['load_N']):
        k = tuple(sorted((r['part'], r['to'])))
        if k in seen:
            continue
        seen.add(k); uniq.append(r)
    return uniq


def gravity_work(D, att_design, springs):
    """Moving bodies held at rest by their weight alone (spec §4.8): held in the working attitude, not held upside down,
    no spring of the list acts on them."""
    S = D['S']
    sp_parts = set()
    for s in springs:
        sp_parts |= {s['a'], s['b']}
        if s.get('part'):
            sp_parts.add(s['part'])
    down = {u['body'] for u in att_design['вверх дном']['unheld']}
    work = {u['body'] for u in att_design['рабочее']['unheld']}
    t15 = {}
    for nm in ('наклон 15° вперёд', 'наклон 15° назад', 'наклон 15° влево', 'наклон 15° вправо'):
        for u in att_design[nm]['unheld']:
            t15.setdefault(u['body'], []).append(nm)
    out = []
    for b in sorted(down - work):
        ids = np.nonzero(D['body'] == b)[0]
        movs = {S.parts[i]['mov'] for i in ids}
        if movs == {'fixed'}:
            continue
        names = [S.names[i] for i in ids]
        if set(names) & sp_parts:
            continue
        # travel of the body over the snapshot's states (largest displacement of its centre)
        c = np.array([D['M'][i]['c'] for i in ids]).mean(0) / U.MM
        dmax = 0.0
        for s in range(len(S.states)):
            T = S.poses[s, ids[0]]
            if S.method[s, ids[0]] < 0:
                continue
            dmax = max(dmax, float(np.linalg.norm(T[:3, :3] @ c + T[:3, 3] - c)))
        h = dmax * U.MM
        mu = 0.25
        t_free = math.sqrt(2 * h / U.G) if h > 0 else 0.0
        out.append(dict(body=b, parts=names[:5], mov=sorted(movs)[:3], travel_mm=round(dmax, 2), t_free_ms=round(t_free * 1e3, 1),
                        t_mu_ms=round(math.sqrt(2 * h / (U.G * (1 - mu))) * 1e3, 1) if h > 0 else 0.0, tilt15_fails=t15.get(b, [])))
    return out


def missing_list(J, att, mob, D):
    rows = []
    for j in J['joints']:
        if j['type'] == 'rigid' and j['status'] in ('missing', 'described') and j.get('fastener') not in (None, 'print') or \
                (j['type'] == 'rigid' and j['status'] == 'missing'):
            rows.append(dict(kind='крепёж стыка', a=j['a'], b=j['b'], status=j['status'], what=j.get('fastener') or '?', doc=j.get('doc', ''),
                             note=j.get('note', '')))
    for u in att['рабочее']['unheld']:
        if u.get('verdict') in ('падает', 'опрокидывается'):
            rows.append(dict(kind='не держится в рабочем положении', a=', '.join(u['parts'][:3]), b=(u['path'][-1][3] or '') if u.get('path') else '',
                             status='missing', what='опора/крепление', doc='', note=f"{u['verdict']}; масса {u['mass_g']} г"))
    for m in mob:
        if m['fixed'] and m['extra']:
            tw = [t for t in m['twists'] if not t['harmless']]
            txt = '; '.join(f"{t['kind']} {t['d']}" for t in tw)
            what = 'стопорные кольца / упоры' if all(t['kind'] == 'сдвиг' for t in tw) else 'крепление'
            rows.append(dict(kind='лишняя степень свободы', a=', '.join(m['parts'][:3]), b='', status='missing', what=what, doc='', note=txt))
    return rows


def render_body(D, b, path, arrow=None, out=None):
    import render as RN, trimesh
    S = D['S']
    ids = list(np.nonzero(D['body'] == b)[0])
    lo = S.lo[ids].min(0); hi = S.hi[ids].max(0); ctr = (lo + hi) / 2; ext = max(np.ptp(np.r_[lo[None], hi[None]], 0).max(), 20)
    box_lo, box_hi = ctr - ext * 1.2, ctr + ext * 1.2
    objs = []
    for k in np.nonzero(np.all(S.lo <= box_hi, 1) & np.all(S.hi >= box_lo, 1))[0]:
        if k in ids or S.parts[k]['group'] == 'case':
            continue
        objs.append((S.V[k], S.F[k], (205, 208, 214), int(k)))
    for k in ids:
        objs.append((S.V[k], S.F[k], (214, 120, 60), int(k)))
    if arrow is not None:
        d = np.asarray(arrow, float); d /= np.linalg.norm(d)
        L = ext * 0.9
        cyl = trimesh.creation.cylinder(radius=ext * 0.03, height=L * 0.7)
        cone = trimesh.creation.cone(radius=ext * 0.08, height=L * 0.3)
        cone.apply_translation((0, 0, L * 0.35))
        ar = trimesh.util.concatenate([cyl, cone])
        from geo import _rot_to
        R = _rot_to(d)
        V = ar.vertices @ R.T + ctr + d * (ext * 0.6 + L * 0.35)
        objs.append((V, ar.faces, (220, 30, 30), 99999))
    eye = ctr + np.array([-1.0, -1.6, 1.1]) * ext * 6
    img, _ = RN.render(objs, (eye, ctr), W=900, H=650)
    img.save(out)


def tex_table(st):
    L = []
    d = st['readings']['design']; dc = st['readings']['declared']
    L.append(f"тел (по замыслу / объявлено / в модели) & {d['nbodies']} / {dc['nbodies']} / {st['readings']['model']['nbodies']} \\\\")
    L.append(f"тел без пути к раме (по замыслу) & {len(d['not_connected'])} \\\\")
    for nm in ('рабочее', 'наклон 15° вперёд', 'наклон 15° назад', 'наклон 15° влево', 'наклон 15° вправо', 'перенос 30° вперёд', 'вверх дном'):
        a = d['attitudes'][nm]
        fall = sum(1 for u in a['unheld'] if u.get('verdict') in ('падает', 'опрокидывается'))
        sett = sum(1 for u in a['unheld'] if u.get('verdict') == 'оседает')
        L.append(f"{nm}: падает или опрокидывается / оседает до упора / только трением & {fall} / {sett} / {len(a['friction_only'])} \\\\")
    mob = st['mobility']
    L.append(f"неподвижных тел с лишней степенью свободы & {sum(1 for m in mob if m['fixed'] and m['extra'])} \\\\")
    fl = st['fastener_loads']
    worst = min((r for r in fl if r['margin']), key=lambda r: r['margin'], default=None)
    if worst:
        L.append(f"крепёж: наименьший запас под весом & {worst['margin']:.0f} ({worst['part'].replace('_', ' ')}) \\\\".replace('.', '{,}'))
    L.append(f"мест «работает весом» & {len(st['gravity_work'])} \\\\")
    L.append(f"строк в списке недостающего крепежа & {st['n_missing']} \\\\")
    return '\n'.join(L) + '\n'


def main():
    t0 = time.time()
    springs = json.load(open(os.path.join(U.DATA, 'springs.json')))['springs']
    base = json.load(open(os.path.join(U.ROOT, 'gen', 'model', 'model.json')))['numbers']
    st = dict(baseline=dict(rest_interferences=base['rest_interferences'], scen=base['scen'], contacts_failed=base['contacts_failed'],
                            strike_failed=base['strike_failed'], parts=base['parts']), readings={})
    shared = {}
    for mode in ('design', 'declared', 'model'):
        D = S1.setup(mode, **shared)
        shared = dict(S=D['S'], J=D['J'], pairs=D['pairs'], P=D['P'], M=D['M'])
        wsp, used, skipped = S1.spring_loads(D, springs)
        rd = dict(nbodies=D['nb'], springs_applied=used, springs_not_applied=skipped,
                  not_connected=[dict(body=b, parts=S1.body_names(D, b)[:5]) for b in S1.connectivity(D)])
        if mode == 'model':
            r = S1.local_hold(D, (0, 0, -1), wsp)
            rd['unheld_work'] = sum(1 for v in r.values() if not v['ok'])
        else:
            rd['attitudes'] = attitudes(D, wsp, SETTLE_ATT if mode == 'design' else {'рабочее'})
        st['readings'][mode] = rd
        if mode == 'design':
            Dd = D
    st['mobility'] = mobility(Dd)
    st['fastener_loads'] = fastener_loads(Dd, Dd['J'])
    st['gravity_work'] = gravity_work(Dd, st['readings']['design']['attitudes'], springs)
    miss = missing_list(Dd['J'], st['readings']['design']['attitudes'], st['mobility'], Dd)
    st['n_missing'] = len(miss)
    # axial retention of the revolute joints (step D) from the mobility of the bodies on both sides
    J = Dd['J']; free_ax = {}
    for m in st['mobility']:
        free_ax[m['body']] = [np.array(t['d']) for t in m['twists'] if t['kind'] == 'сдвиг']
    for j in J['joints']:
        if j['type'] in ('revolute', 'cylindrical') and j.get('axis'):
            d = np.array(j['axis']['d']); d /= np.linalg.norm(d)
            fr = []
            for nm in (j['a'], j['b']):
                b = int(Dd['body'][Dd['S'].idx[nm]]) if not S1.is_flex(nm) else -1
                if b > 0 and any(abs(v @ d) > 0.98 for v in free_ax.get(b, [])):
                    fr.append(nm)
            j['axial'] = 'free: ' + ', '.join(fr) if fr else 'retained (геометрия: упоры у торцов)'
    json.dump(J, open(os.path.join(U.DATA, 'joints.json'), 'w'), ensure_ascii=False, indent=1)
    os.makedirs(U.GEN, exist_ok=True)
    with open(os.path.join(U.GEN, 'stage1_missing.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['kind', 'a', 'b', 'status', 'what', 'doc', 'note']); w.writeheader(); w.writerows(miss)
    # pictures: bodies that fall in the working attitude, and fixed bodies with a free motion
    k = 0
    for u in st['readings']['design']['attitudes']['рабочее']['unheld']:
        if u.get('verdict') in ('падает', 'опрокидывается') and k < 12:
            dvec = u['path'][-1][1] if u['path'] and u['path'][-1][0] == 'сдвиг' else (0, 0, -1)
            fn = os.path.join(U.GEN, f"stage1_fall_{k:02d}.png")
            render_body(Dd, u['body'], None, arrow=dvec, out=fn); u['png'] = os.path.basename(fn); k += 1
    k = 0
    for m in st['mobility']:
        if m['fixed'] and m['extra'] and k < 8:
            tw = [t for t in m['twists'] if not t['harmless']][0]
            fn = os.path.join(U.GEN, f"stage1_dof_{k:02d}.png")
            render_body(Dd, m['body'], None, arrow=tw['d'], out=fn); m['png'] = os.path.basename(fn); k += 1
    st['time_s'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(U.GEN, 'stage1.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    open(os.path.join(U.ROOT, 'gen', 'tab_stage1.tex'), 'w').write(tex_table(st))
    print('stage 1 done', st['time_s'], 's; missing rows', len(miss))


if __name__ == '__main__':
    main()
