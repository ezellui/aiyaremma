"""Stage 1, manual marking (spec §4.4) written as rules over whole part names, groups and BOM ids -- never over pieces of
names (trap 10). Each rule gives the joint the document intends, its fastener, status and a reference. A rule only
applies to pairs that do not move against each other in the model ('planar_rest' after step C).

Statuses: 'described' -- the document says how it is held (or says that the fastening exists but is not listed);
'missing' -- the document says nothing; the note gives what is usually done."""
import re

FRAME_NOTE = ('main.tex §«Перечень покупного»: «Пружины, крепёж рамы и стыков … в перечень не входят» — крепёж задуман, '
              'но не назван и не построен')


def _bom(p):
    return p['bom'] or ''


def rule(pa, pb):
    """-> dict(type, fastener, status, doc, note) or None."""
    a, b = pa['name'], pb['name']
    ga, gb = pa['group'], pb['group']
    ba, bb = _bom(pa), _bom(pb)
    both = {a, b}
    # --- the case (rev. 0.12)
    if ga == 'case' and gb == 'case':
        if any(n.startswith('case standoff') for n in both):
            return dict(type='rigid', fastener='screw M3 + insert', status='missing', doc='§«Корпус»',
                        note='панель на упоре: «стоят на упорах … ничем не скреплены»; нужен винт М3 со вставкой в панель')
        return dict(type='rigid', fastener='screw M3 + insert', status='described', doc='§«Корпус»: «швы скрепляются накладками на винтах (в модели их нет)»',
                    note='шов панелей: накладка на винтах М3 — не построена')
    if ga == 'case' or gb == 'case':
        o = pa if gb == 'case' else pb
        c = pb if gb == 'case' else pa
        if c['name'].startswith('case standoff') and o['group'] == 'frame':
            return dict(type='rigid', fastener='screw M5 + T-nut', status='described',
                        doc='§«Корпус»: «упоры, привёрнутые в пазы профиля (… винты М5 с Т-гайками — нет)»', note='винт М5 с Т-гайкой не построен')
        if 'pillar' in c['name'] and o['name'].startswith('carriage post'):
            return dict(type='planar_rest', fastener=None, status='described', doc='§«Корпус»: «пилястры … надеты на стойки»',
                        note='надета сверху; от подъёма держит только вес')
        return dict(type='contact_only', fastener=None, status='described', doc='§«Корпус»: «корпус не трогает механизма»',
                    note='касание корпуса с механизмом')
    # --- keys: cap on stem
    if {ga, gb} == {'keys'} and any(n.startswith('cap ') for n in both) and any(n.startswith('stem ') for n in both):
        return dict(type='rigid', fastener='press', status='missing', doc='—', note='колпачок на штоке: обычно посадка с натягом или клей')
    # --- shuttle: type blocks in sockets with an adjusting screw; comb pins pressed into the ring
    if both == {'shuttle'} | ({a, b} - {'shuttle'}) and 'shuttle' in both:
        o = pb if a == 'shuttle' else pa
        if o['name'].startswith('type block'):
            return dict(type='rigid', fastener='screw M3', status='described',
                        doc='§«Литерные блоки и челнок»: «в гнёзда с регулировочным винтом»', note='винт гнезда в модели не построен')
        if o['name'].startswith('comb pin'):
            return dict(type='rigid', fastener='press', status='described', doc='§«Литерные блоки и челнок»: «в кольце штифты сидят с натягом»',
                        note='в модели штифт касается отверстия без натяга')
        if o['name'].startswith('code comb'):
            return dict(type='planar_rest', fastener=None, status='described', doc='§«Чтение»: гребёнка на двух штифтах, «прижим к поясу»',
                        note='прижим к поясу — чем? (держит гребёнку на штифтах по их оси)')
    if any(n.startswith('code comb') for n in both) and any(n.startswith('comb pin') for n in both):
        return dict(type='prismatic_pins', fastener=None, status='described', doc='§«Чтение»: «полоса … на двух стальных штифтах Ø2»',
                    note='гребёнка надета на штифты с зазором: сдвиг вдоль штифтов держит только «прижим к поясу»')
    # --- carriage: plates, bushings, tube, roller -- carriage frame
    if ga == 'carriage' and gb == 'carriage':
        return dict(type='rigid', fastener='screw M3', status='missing', doc='§«Каретка»',
                    note='сборка каретки: в документе нет, чем держатся торцевые стенки, втулки, труба, рейка и упоры полей (обычно винты М3, втулки — в запрессовку)')
    # --- U-frame: everything on the base plate
    if (a == 'U-frame base' or b == 'U-frame base'):
        o = pb if a == 'U-frame base' else pa
        if o['bom'].startswith('MGN12H'):
            return dict(type='rigid', fastener='screw M3', status='described', doc='§«U-образная рама и ползун»: «плита Д16Т на MGN12»',
                        note='каретки MGN12H на винтах М3 (по 4) — в модели нет')
        return dict(type='rigid', fastener='screw M3', status='missing', doc='—',
                    note='деталь на плите узла: крепления нет (обычно винты М3 в резьбу плиты Д16Т)')
    # --- the frame and its posts, brackets, cheeks: 2020 profiles
    fixed = pa['mov'] == 'fixed' and pb['mov'] == 'fixed'
    if fixed:
        prof = {n for n in both if (n.startswith('frame ') or n.startswith('beam ') and not n.startswith('beam post'))}
        if prof:
            return dict(type='rigid', fastener='screw M5 + T-nut', status='described', doc=FRAME_NOTE,
                        note='деталь на профиле 2020: винт М5 с Т-гайкой не построен')
        return dict(type='rigid', fastener='screw M3', status='described', doc=FRAME_NOTE,
                    note='стык неподвижных деталей: вид крепежа не назван')
    # --- moving assemblies whose parts do not move against each other
    if pa['mov'] == pb['mov']:
        if any(n.startswith('selector bar') for n in both) and any(n.startswith('selector rod') for n in both):
            return dict(type='rigid', fastener=None, status='missing', doc='—', note='гнутый стержень выбора на планке: чем держится?')
        if any(n.startswith('bail ') and ' guides ' in n for n in both) and any(n.startswith('tier carriage') for n in both):
            return dict(type='rigid', fastener='press', status='missing', doc='§«Мерные рамки»: «передние прутки висят на кронштейне яруса»',
                        note='как пруток держится в кронштейне яруса — не сказано')
        return dict(type='rigid', fastener=None, status='missing', doc='—', note=f'детали одного движения ({pa["mov"]}) касаются; чем скреплены — нет')
    return None
