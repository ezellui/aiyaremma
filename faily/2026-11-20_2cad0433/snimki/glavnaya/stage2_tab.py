"""Stage 2 summary (spec §5.7): gen/tab_stage2.tex and gen/physics/stage2.json from the nodes' results.
Usage: python3 -I tools/physics/stage2_tab.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U


def L(n):
    return json.load(open(os.path.join(U.GEN, f'node_{n}.json')))


def f(x, d=1):
    return f'{x:.{d}f}'.replace('.', '{,}')


def main():
    C, D, B, A, F, E, G = (L(n) for n in 'cdbafeg')
    rows = []
    v = C['validation']; n = C['nominal_avg']
    sec = n['contacts'][1] if len(n['contacts']) > 1 else None
    rows.append(('C', 'молоток', f"скорость {f(v['v'],2)} / {f(v['links_v'],2)} м/с, полёт {f(v['t_ms'],2)} / {f(v['links_t_ms'],2)} мс",
                 f"удар {f(n['v_impact'],2)} м/с, {f(n['contacts'][0]['F_max'],0)} Н, {f(n['contacts'][0]['dur_ms'],2)} мс; второе касание на {f(sec['cycle_deg'],0)}°"
                 if sec else f"удар {f(n['v_impact'],2)} м/с", 'повторного удара нет', 'нет: ' + f"{C['lhs']['second_strike']} из 200 до 200°"))
    rows.append(('D', 'спуск и каретка', f"подача на зуб {f(D['validation']['rack_per_tooth_mm'],4)} мм = 1\\,u",
                 f"пружина каретки ≥ {f(D['F_required_light'],0)} Н (лёгкий цикл), удар о палец U до {f(max(r['E_hit_mJ'] for r in D['at_required']),0)} мДж, отскок до {f(max(r['rebound_teeth'] for r in D['at_required']),1)} зуба",
                 'подача до 340°, отскок < 1 зуба', 'нет'))
    worst = max(B['cases'], key=lambda r: r['F_ret_lift_needed'])
    vb = max(abs(x['diff_pct']) for x in B['validation'])
    rows.append(('B', 'цикл', f"время цикла как в motor.py: расхождение ≤ {f(vb,2)}\\,\\%",
                 f"ролики отрываются: не хватает {f(max(r['F_ret_rot_needed'] for r in B['cases']),0)} Н (поворот) и {f(worst['F_ret_lift_needed'],0)} Н (подъём); челнок отходит от кольца на {f(max(fl['gap_max_mm'] for r in B['cases'] for fl in r['flights']),1)} мм; лента поворота должна толкать до {f(-min(r['tape_min_N'] for r in B['cases']),1)} Н",
                 'отрыва нет', 'нет'))
    a = A['буква k24']
    rows.append(('A', 'клавиша', '—', f"возврат буквенной {f(a['return_nominal']['t_ms'],0)} мс, отскок от упора {f(a['return_nominal']['bounce_mm'],1)} мм; мёртвая не доходит до спуска при 2 Н",
                 'возврат ≤ 100 мс, дребезг ≤ 0,3 мм', 'нет'))
    w = [r for r in F['rows'] if r['cycle'] == 'средняя (4, 5)' and r['ch'] == 'W']
    rows.append(('F', 'щупы', '—', f"щуп W на среднем цикле доходит до {f(max(r.get('reached_mm', 99) for r in w if r['arrive_deg'] is None),1)} мм из 13; нужна пружина W {f(F['spring_needed']['W']['F_spring_avg_N'],2)}–{f(F['spring_needed']['W']['F_spring_N'],1)} Н (сейчас 0,6)",
                 'на зубце к 145°, отскок < 0,5 мм', 'нет'))
    j = E['J_mesh']
    rows.append(('E', 'двигатель', f"J₀ по сеткам {f(j['total']*1e6,1)} против {f(j['motor_J0']*1e6,0)} кг·мм²·10³",
                 f"лёгкий цикл {f(E['rows'][1]['t_cycle'],2)} с (motor.py {f(E['rows'][0]['t_cycle'],2)}), удар о защёлку {f(E['rows'][1]['E_stop_mJ'],1)} мДж",
                 'удар на защёлке в пределах печати', 'риск'))
    rows.append(('G', 'возвраты весом', '—', f"{len(G['rows'])} мест: клавиши, планки разрядов, коромысло чтения, молоток; на 15° клавиши и планки не возвращаются",
                 'перечислены и проверены', 'только на горизонтальном столе'))
    tex = []
    for r in rows:
        tex.append(' & '.join(r) + ' \\\\')
    open(os.path.join(U.ROOT, 'gen', 'tab_stage2.tex'), 'w').write('\n'.join(tex).replace('%', '\\%') + '\n')
    json.dump(dict(rows=rows), open(os.path.join(U.GEN, 'stage2.json'), 'w'), ensure_ascii=False, indent=1)
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
