"""rev. 0.9c: contact audit -- the parts that drive one another must touch.

For each driving pair and each state where it must drive, the exact distance between the two meshes (FCL, BVH of the
triangles) and the volume of their overlap (manifold intersection). A pair passes when the gap is at most GAP and the
overlap at most OVL in every listed state. Pins pressed into a part and parts screwed together are not listed: they
are joints, not contacts. Usage: python3 -I contacts.py OUT_JSON OUT_TEX"""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import fcl
import parts as PT, params as P, scenarios as SC, geo, escape as E

GAP = 0.06          # mm: polygon facets of round parts (12..64 segments) leave up to a few hundredths
OVL = 0.10          # mm3


def _co(m):
    V, F = geo.to_arrays(m)
    o = fcl.BVHModel(); o.beginModel(len(V), len(F)); o.addSubModel(np.asarray(V, float), np.asarray(F, np.int32)); o.endModel()
    return fcl.CollisionObject(o, fcl.Transform())


def measure(a, b):
    ov = (a ^ b).volume()
    d = fcl.distance(_co(a), _co(b), fcl.DistanceRequest(), fcl.DistanceResult())
    return max(0.0, float(d)), float(ov)


K = {k['id']: k for k in PT.key_list()}


def keyst(kid, f):
    k = K[kid]; fr = SC.key_frames(k, 0)
    return PT.State(pressed={k['n']: f}, frames={b: v * f for b, v in fr.items()}, slide_u=(P.MARK_REF_U * f if 'O' in fr else 0))


def groups():
    """(group, title, [(state tag, State)], [(a, b, note)])"""
    out = []
    key = 'k24'
    kk = [k for k in PT.key_list() if k['kind'] == 'char' and P.ROW_CODE[k['r']] & 1][0]['id']
    out.append(('keys', 'клавиша → выбор', [(f'{key} {f}', keyst(key, f)) for f in (0.5, 1.0)],
                [(f'stem {key}', f'lever {key}', 'шток → рычаг'), (f'lever {key}', 'column pusher 4', 'рычаг → толкатель столбца'),
                 ('column pusher 4', 'selector bar r4', 'толкатель → планка r4'), ('selector bar r4', 'selector rod r4', 'планка → стержень'),
                 ('selector rod r4', 'rotate latch pin r4', 'стержень → палец защёлки')]))
    out.append(('keys', 'клавиша → выбор', [(f'{kk} 1.0', keyst(kk, 1.0))],
                [(f'lever {kk}', 'selector bar l1', 'рычаг → планка l1'), ('selector bar l1', 'selector rod l1', 'планка → стержень'),
                 ('selector rod l1', 'lift latch pin l1', 'стержень → палец защёлки')]))
    cyc = lambda angs: [(f'{a}°', SC.cycle_state(a, 9, 6)) for a in angs]
    all_a = (0, 60, 90, 105, 120, 150, 190, 205, 230, 300)
    out.append(('cycle', 'кулачки → толкатели', cyc(all_a),
                [('cam rod rotate', 'cam rotate', 'кулачок позиции'), ('cam rod lift', 'cam lift', 'кулачок ряда'),
                 ('cam rod detent', 'cam detent', 'кулачок фиксаторов'), ('cam rod ribbon', 'cam ribbon', 'кулачок ленты')]))
    out.append(('cycle', 'кулачок взвода', cyc((0, 60, 90, 120, 150, 190, 230, 300)), [('cam rod hammer', 'cam hammer', 'кулачок молотка')]))
    out.append(('cycle', 'привод деревьев', cyc(all_a),
                [('cam rod rotate', 'rotate drive bellcrank', 'палец толкателя в пазу качалки'), ('cam rod lift', 'lift drive bellcrank', '—'),
                 ('rotate drive bellcrank', 'rotate drive link', 'качалка → тяга'), ('lift drive bellcrank', 'lift drive bail', 'качалка → ведущая планка'),
                 ('rotate drive bail', 'rotate latch pin r8', 'планка → поднятый палец'), ('rotate drive bail', 'rotate latch pin r1', '—'),
                 ('lift drive bail', 'lift latch pin l2', '—'), ('rotate bit slider r8', 'rotate summing lever 3', 'ползун → рычаг суммы'),
                 ('rotate node slider 3', 'rotate amplifier', 'узел → усилитель'), ('lift output pin', 'lift bellcrank', 'выход → угловой рычаг'),
                 ('lift bellcrank', 'lift push rod', 'угловой рычаг → толкатель вилки'), ('lift push rod', 'lift fork', 'толкатель → вилка'),
                 ('lift fork', 'lift collar', 'вилка → кольцо'), ('lift collar', 'shuttle', 'кольцо → челнок')]))
    out.append(('cycle', 'фиксаторы и лента', cyc(all_a),
                [('cam rod detent', 'detent link', 'толкатель → тяга фиксаторов'), ('detent link', 'detent pawl', 'язык тяги → клин собачки'),
                 ('row detent link', 'row detent roller', 'тяга → ролик ряда'), ('row detent roller', 'row detent wedge', 'ролик → клин ряда'),
                 ('cam rod ribbon', 'ribbon link', 'толкатель → тяга ленты'), ('ribbon link', 'ribbon vibrator', 'тяга → вибратор')]))
    out.append(('cycle', 'фиксатор позиции введён', cyc((120, 150, 185)), [('detent pawl', 'pulley and detent wheel', 'клин в вырезе колеса')]))
    out.append(('cycle', 'взвод молотка', cyc((0, 60, 90, 120, 150, 190, 300)),
                [('cam rod hammer', 'hammer trip link', 'толкатель → тяга взвода'), ('hammer trip link', 'hammer cocking rod', 'тяга → стержень'),
                 ('hammer cocking rod', 'hammer cocking lever', 'палец стержня в пазу рычага взвода')]))
    out.append(('cycle', 'удар', cyc((168,)), [('hammer', 'paper', 'боёк → бумага')]))
    T = 5.053 * math.radians(6.0); car0 = P.CAR_X_START - 60 * T
    back = lambda d: car0 + 5.053 * math.radians(d)
    es = [('покой', PT.State(car=car0)), ('W = 6, U введён', PT.State(car=car0, frames={'W': 6.0}, u_in=True)),
          ('W = 12, ±u = +1', PT.State(car=car0, frames={'W': 12.0}, u_in=True, pm_u=1))]
    out.append(('escape', 'спуск в покое и при наборе', es,
                [('escapement dog', 'escapement wheel and pinion', 'собачка Д на зубе'), ('escapement stop', 'escapement tape', 'лента на барабане U'),
                 ('bksp tail pin', 'bksp rocker', 'палец хвоста в пазу качалки'), ('back tail pin', 'back rocker', '—'),
                 ('bksp rocker', 'bksp link', 'шаровой шарнир'), ('back rocker', 'back link', '—'),
                 ('backspace arm K', 'bksp link', '—'), ('back lever B', 'back link', '—'), ('backspace arm K', 'back lever B', 'K → палец B'),
                 ('memory holding pawl', 'memory ratchet sector', 'собачка M в секторе')]))
    out.append(('escape', 'палец U введён', es[1:], [('escapement stop finger', 'escapement wheel and pinion', 'палец U у зуба')]))
    out.append(('escape', 'M в нуле', es[:1], [('memory lever M', 'memory zero stop', 'M на упоре нуля'), ('back pawl', 'back pawl guard', 'собачка B на щитке')]))
    bk = PT.State(car=back(E.BKSP_DEG - E.B_CATCH), pressed={46: 1.0})
    bl = PT.State(car=back(6 * 8 + E.M_PLAY), pressed={47: 1.0}, esc_mem=8)
    out.append(('escape', 'забой и «назад на литеру»', [('забой', bk), ('назад, w = 8', bl)],
                [('back pawl', 'escapement wheel and pinion', 'собачка B ведёт колесо'), ('bksp tail pin', 'bksp rocker', '—'),
                 ('back tail pin', 'back rocker', '—'), ('backspace arm K', 'back lever B', '—')]))
    out.append(('escape', '«назад на литеру»: клин M', [('назад, w = 8', bl)],
                [('memory coupling wedge', 'escapement wheel and pinion', 'клин M в зубьях (люфт 1,2°)')]))
    return out


def run():
    rows = []
    cache = {}
    for grp, title, states, pairs in groups():
        per = {(a, b): [] for a, b, _ in pairs}
        for tag, st in states:
            key = (grp, tag)
            if key not in cache:
                cache[key] = {p.name: p.mesh for p in PT.build(st)}
            ps = cache[key]
            for a, b, _ in pairs:
                per[(a, b)].append((tag,) + measure(ps[a], ps[b]))
        for a, b, note in pairs:
            r = per[(a, b)]
            gmax = max(x[1] for x in r); gmin = min(x[1] for x in r); omax = max(x[2] for x in r)
            ok = gmax <= GAP and omax <= OVL
            rows.append(dict(group=grp, title=title, a=a, b=b, note=note, n=len(r), gap_min=round(gmin, 3), gap_max=round(gmax, 3),
                             ovl_max=round(omax, 3), ok=bool(ok), worst=max(r, key=lambda x: (x[1], x[2]))[0]))
    return rows


def tex(rows):
    out = []
    last = None
    for r in rows:
        if r['title'] != last:
            out.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{r['title']}}}}} \\\\")
            last = r['title']
        nm = (r['a'] + ' — ' + r['b']).replace('_', '\\_')
        out.append(f"\\texttt{{\\footnotesize {nm}}} & {r['n']} & {r['gap_max']:.3f}".replace('.', '{,}') +
                   f" & {r['ovl_max']:.2f}".replace('.', '{,}') + f" & {'да' if r['ok'] else '\\textbf{нет}'} \\\\")
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    rows = run()
    json.dump(rows, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
    open(sys.argv[2], 'w').write(tex(rows))
    bad = [r for r in rows if not r['ok']]
    print('contacts', len(rows), 'failed', len(bad))
    for r in bad:
        print('  ', r)
