"""Stage 1 (spec §3.4): the full list of the machine's springs, numbers taken from the code where they are, from the
document's text otherwise; a spring without a number is k = None, status 'missing' (never invented).
Writes data/springs.json (manual edits of 'points' and 'note' survive: the key is the name).
Usage: python3 -I tools/physics/springs.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import params as P

LJ = json.load(open(os.path.join(U.ROOT, 'gen', 'links.json')))
MJ = json.load(open(os.path.join(U.ROOT, 'gen', 'motor.json')))


def sp(name, a, b, kind, k=None, preload=None, travel=None, unit='N/mm', source='', status='described', part=None, note=''):
    return dict(name=name, a=a, b=b, kind=kind, k=k, k_unit=unit, preload=preload, travel=travel, points=None, part=part,
                source=source, status=status, note=note)


def build():
    out = []
    fr = LJ['frames']
    for f in ('R', 'W', 'O', 'N'):
        d = fr[f]
        for s in (-1, +1):
            # links.frames: F_pre, k are for the frame (two springs in parallel): one spring carries half
            out.append(sp(f'bail {f} spring {s:+d}', f'bail {f} side {s:+d}', 'frame base strip (rear guide strip)', 'compression',
                          k=d['k'] / 2, preload=d['F_pre'] / 2, travel=d['travel'], source='links.json frames.' + f + ' (F_pre, k of the frame / 2)',
                          status='modeled', part=f'bail {f} spring {s:+d}', note='5,2×0,5 мм на задней направляющей'))
    st = LJ['stops']
    out.append(sp('slide return spring', 'U-frame base', 'zero stop', 'extension', k=None, preload=st['F_return'], travel=P.SLIDE_MAX,
                  source='links.json stops.F_return (1 N); main.tex «около 1 Н»', status='modeled', part='slide return spring',
                  note='жёсткость не задана'))
    out.append(sp('O rod A spring', 'O rod A rear', 'O rod A front', 'compression', k=0.12, preload=st['F_spring'][0], travel=None,
                  source='links.py stops (F_pre 1,5 Н, k_sp 0,12 Н/мм; до 2,26 Н)', status='modeled', part='O rod A spring'))
    h = LJ['hammer']
    out.append(sp('hammer spring', 'hammer', 'U-frame arm and hammer post', 'torsion', k=h['k_t_Nmm_per_deg'], unit='N*mm/deg',
                  preload=h['T_mean_Nmm'], travel=h['swing_deg'],
                  source='links.json hammer (k_t, T_mean over the 18° swing; энергия 20 мДж)', status='modeled', part='hammer spring',
                  note='preload — средний момент на ходе 18°'))
    s = MJ['spring']
    out.append(sp('mainspring', 'spring barrel', 'barrel arbor', 'spiral (заводная)', k=None, preload=s['M_max'], unit='N*m',
                  source='motor.json spring (M_max 5,12 Н·м, M_avg 1,19 Н·м, 32×0,8 мм, ~6,3 м)', status='modeled', part='mainspring',
                  note='момент по заводу — motor.py; в цикле — на валу tau_C = 17 мН·м'))
    lt = LJ['selection']['latch']
    for b in ('r1', 'r2', 'r4', 'r8'):
        out.append(sp(f'latch pin spring {b}', f'rotate latch pin {b}', 'rotate bit slider ' + b, 'compression', preload=lt['spring_N'],
                      source='links.json selection.latch.spring_N', status='described', note='палец защёлки 3 мм «с пружиной вниз»; пружины в модели нет'))
    for b in ('l1', 'l2', 'l4'):
        out.append(sp(f'latch pin spring {b}', f'lift latch pin {b}', 'lift bit slider ' + b, 'compression', preload=lt['spring_N'],
                      source='links.json selection.latch.spring_N', status='described', note='как у r1..r8'))
    fo = LJ['selection']['forces']
    for t in ('rotate', 'lift'):
        out.append(sp(f'{t} slider return springs', f'{t} bit sliders', 'U-frame base', 'extension', preload=fo['F_return'],
                      source='links.json selection.forces.F_return (0,4 Н на ползун)', status='described',
                      note='возврат ползунов разрядов; в модели нет; жёсткость не задана'))
    for ch in P.READ_CH:
        out.append(sp(f'feeler spring {ch}', f'feeler {ch}', 'reading head', 'compression (long)', k=0.0, preload=P.READ_F_SPRING[ch],
                      source='params.READ_F_SPRING («long, nearly constant over the stroke»)', status='described',
                      note=f'нагрузка щупа {P.READ_F_LOAD[ch]} Н (params.READ_F_LOAD)'))
    out.append(sp('escapement stop return spring', 'escapement stop', 'escapement bracket', 'extension', preload=LJ['escape']['spring_N'],
                  source='links.json escape.spring_N (0,2 Н с ред. 0.10)', status='described', note='возврат упора U в ноль'))
    for m in ('B', 'C'):
        out.append(sp(f'memory pawl spring {m}', f'memory pawl {m}', 'sector bracket', 'flat/torsion', preload=LJ['sectors']['ratchet']['pawl_spring_N'],
                      source='links.json sectors.ratchet.pawl_spring_N; note детали', status='described'))
        out.append(sp(f'sector return spring {m}', f'memory sleeve {m}', 'sector axis', 'torsion', source='main.tex рис. «Сектор памяти»: «пружина возвращает сектор в ноль»',
                      status='missing', note='числа нет нигде'))
    out.append(sp('escapement dog spring', 'escapement dog', 'escapement bracket', 'compression', preload=0.3,
                  source='note детали escapement dog (0,3 Н)', status='described'))
    out.append(sp('back pawl spring', 'back pawl', 'back lever B', 'torsion/flat', preload=0.2, source='note детали back pawl (0,2 Н)', status='described'))
    out.append(sp('bksp link spring', 'bksp link', 'backspace arm K', 'compression (в тяге)', source='note bksp link; main.tex §«Забой»', status='missing',
                  note='«остаток забирает пружина в тяге»; числа нет; подбор по стенду Э2'))
    out.append(sp('back link spring', 'back link', 'back lever B', 'compression (в тяге)', source='note back link; main.tex', status='missing',
                  note='подбор по стенду Э2'))
    out.append(sp('memory lever M return spring', 'memory lever M', 'escapement bracket', 'torsion', source='main.tex §«Спуск»: «пружина M возвращает его на упор нуля»',
                  status='missing', note='подбор по стенду Э2'))
    out.append(sp('memory holding pawl spring', 'memory holding pawl', 'memory lever M', 'flat', source='main.tex: собачка M в храповом секторе', status='missing'))
    out.append(sp('stop carrier spring', 'stop carrier', 'stop carrier rod bracket', 'extension', source='note stop carrier: «пружина к ролику»', status='missing'))
    out.append(sp('carriage drive spring', 'carriage', 'frame back', 'спиральная (двигатель каретки)', source='main.tex §«Спуск»: «пружинный двигатель каретки всё время стремится его повернуть»',
                  status='missing', note='силы нет нигде; ступень 2, узел D даёт требование'))
    out.append(sp('W latch pawl spring', 'W latch pawl', 'W wire bracket', 'flat/torsion', source='contacts: собачка на храповой планке W', status='missing'))
    out.append(sp('pm-u detent spring', 'pm-u detent', 'escapement bellcrank', 'flat', source='деталь pm-u detent (фиксатор эксцентрика ±u)', status='missing'))
    out.append(sp('carriage release key spring', 'carriage release key', 'carriage release bracket', 'torsion', source='main.tex: «Когда клавиша отпущена, пружина собачки вводит её»',
                  status='described', note='возврат — пружиной собачки Д (0,3 Н) через трос'))
    out.append(sp('read lock spring', 'read lock pin', 'read lock guide', '?', source='§«Холостой цикл»', status='missing', note='возврат штыря запора чтения'))
    out.append(sp('hammer lock spring', 'hammer lock pin', 'hammer lock guide', '?', source='§«Холостой цикл»', status='missing', note='возврат штыря запора удара'))
    out.append(sp('key return springs', 'stem *', 'key comb', 'compression', preload=None, source='main.tex §«Усилия»: «буквенным клавишам стоит добавить возвратную пружину (около 0,3 Н)» — рекомендация, не решение',
                  status='missing', note='возврат клавиши сейчас — пружины рамок через пластины; проверить в узле A'))
    out.append(sp('ribbon vibrator return', 'ribbon vibrator', 'ribbon post', '?', preload=LJ['ribbon']['F_N'], source='links.json ribbon.F_N (0,6 Н — сила подъёма)',
                  status='missing', note='возврат вибратора — кулачок или вес? см. §4.8'))
    out.append(sp('cycle stop latch spring', 'cycle stop latch', 'motor plate', '?', source='защёлка цикла', status='missing'))
    out.append(sp('detent pawl return', 'detent pawl', 'U-frame base', '?', source='фиксатор позиции: клин уводит тяга; обратно?', status='missing'))
    return out


def main():
    path = os.path.join(U.DATA, 'springs.json')
    old = {}
    if os.path.exists(path):
        old = {s['name']: s for s in json.load(open(path))['springs']}
    out = build()
    for s in out:
        o = old.get(s['name'])
        if o:
            for k in ('points', 'note'):
                if o.get(k) and o.get('manual'):
                    s[k] = o[k]
    json.dump(dict(version=1, model_revision='0.12', springs=out), open(path, 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(out), Counter(s['status'] for s in out))


if __name__ == '__main__':
    main()
