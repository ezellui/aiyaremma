"""Stage 2, node G (spec §5.2): the places where the weight does the work (stage 1, §4.8): each as a one-degree model --
the free return over the travel the snapshot shows, with friction, on a level table and tilted by 15 deg, against the
time the cycle allows. The hammer (node C) is added: its weight pulls it toward the sheet and nothing holds it back.
Usage: python3 -I tools/physics/node_g.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import params as P

S1 = json.load(open(os.path.join(U.GEN, 'stage1.json')))
NC = json.load(open(os.path.join(U.GEN, 'node_c.json')))
MJ = json.load(open(os.path.join(U.ROOT, 'gen', 'motor.json')))


def t_return(h, mu=0.25, tilt=0.0, slope=1.0):
    """Free return over h (m) under g along a vertical guide; tilt reduces the driving component, friction mu on
    the tilt's normal component (a plain estimate: t = sqrt(2 h / (g (cos tilt - mu sin tilt))))."""
    a = U.G * (math.cos(math.radians(tilt)) - mu * math.sin(math.radians(tilt))) * slope
    return math.sqrt(2 * h / a) if a > 0 else None


def main():
    rows = []
    seen = set()
    for g in S1['gravity_work']:
        kind = g['parts'][0].split()[0]
        key = (kind, g['travel_mm'])
        n = sum(1 for x in S1['gravity_work'] if x['parts'][0].split()[0] == kind and x['travel_mm'] == g['travel_mm'])
        if key in seen:
            continue
        seen.add(key)
        h = g['travel_mm'] * U.MM
        if kind == 'cap':
            what = 'клавиши (колпачок со штоком лежит на рычаге): обратно их поднимает рычаг, вниз — только вес'
            window = 'клавиша опускается вместе с рычагом, только пока рычаг давит снизу; вес держит колпачок на рычаге'
        elif kind == 'selector':
            what = 'планка разряда со стержнем: поднимает толкатель столбца, опускается весом'
            window = 'должна лечь до следующего выбора (не раньше возврата клавиши, ~0,1 с)'
        else:
            what = 'коромысло чтения (возвращает трос щупов; весом — только если трос ослаб)'
            window = 'кулачок ведёт его обратно с 150°'
        rows.append(dict(what=what, parts=g['parts'][:2], count=n, travel_mm=g['travel_mm'], t_level_ms=round(t_return(h) * 1e3, 1),
                         t_tilt15_ms=(round(t_return(h, tilt=15.0) * 1e3, 1) if t_return(h, tilt=15.0) else None), fails_tilted=g['tilt15_fails'],
                         window=window))
    n = NC['props']
    rows.append(dict(what='молоток в покое: вес тянет его к листу (момент ' + f"{n['gravity_torque_rest_mNm']:.2f}" + ' мН·м), заднего упора и возврата в модели нет',
                     parts=['hammer'], count=1, travel_mm=round(math.radians(18) * 78.16, 1),
                     t_level_ms=None, t_tilt15_ms=None, fails_tilted=[], window='после удара должен вернуться и стоять до 10° следующего цикла (узел C)'))
    res = dict(rows=rows, note='время свободного возврата по оценке §4.8: t = √(2h/(g(cos α − μ sin α))), μ = 0,25')
    json.dump(res, open(os.path.join(U.GEN, 'node_g.json'), 'w'), ensure_ascii=False, indent=1, default=float)
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
