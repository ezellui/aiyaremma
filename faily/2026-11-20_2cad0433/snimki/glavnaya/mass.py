"""Masses, centres of mass and inertia of the parts (spec §3.3), SI. Fill fraction f of printed parts: 1 for small or
thin-walled parts, FILL_BIG for large ones (as motor.py); the 2020 profiles by their linear mass, not their solid mesh.
Writes gen/physics/mass.json. Usage: python3 -I tools/physics/mass.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import trimesh
import meshes as MS

FILL_BIG = 0.5
BIG_CM3 = 20.0                 # printed parts above 20 cm3 of solid volume count as large (walls are a small share)


def is_profile(p):
    return p['name'] in ('frame front', 'frame back', 'frame side -1', 'frame side +1', 'beam -150', 'beam -20', 'frame cross pivot') \
        or (p['bom'] or '').startswith('ext2020')


def props(S, f_big=FILL_BIG, f_small=1.0):
    out = []
    for i, p in enumerate(S.parts):
        tm = trimesh.Trimesh(S.V[i] * U.MM, S.F[i], process=False)
        vol = abs(float(tm.volume))
        mat = p['mat'] or ''
        if p['kind'] == 'inlay' or mat == '':
            mat = 'PETG'
        rho = U.RHO.get(mat, 1.27) * 1000.0
        f = 1.0
        if mat.startswith('PETG') or mat == 'пластик':
            f = f_big if vol * 1e6 > BIG_CM3 else f_small
        if p['kind'] == 'ref':
            if p['name'] == 'paper':
                ext = S.hi[i] - S.lo[i]
                m = U.PAPER_KG_M2 * float(ext[0] * U.MM) * float(max(ext[1], ext[2]) * U.MM)
            else:
                m = 0.006                     # ribbon in the vibrator (links.json ribbon.mass_g)
            c = (S.V[i].mean(0) * U.MM)
            out.append(dict(m=m, c=c.tolist(), I=np.zeros((3, 3)).tolist(), vol_cm3=vol * 1e6, rho=0, f=0, how='ref'))
            continue
        if is_profile(p):
            L = float((S.hi[i] - S.lo[i]).max() * U.MM)
            m = U.PROFILE_2020_KG_M * L
            tm.density = m / max(vol, 1e-12)
            how = 'profile 0.5 kg/m'
        else:
            tm.density = rho * f
            how = f'rho {rho:.0f} f {f}'
        try:
            c = tm.center_mass; I = tm.moment_inertia
        except Exception:
            c = S.V[i].mean(0) * U.MM; I = np.zeros((3, 3))
        out.append(dict(m=float(tm.mass), c=np.asarray(c).tolist(), I=np.asarray(I).tolist(), vol_cm3=vol * 1e6, rho=rho, f=f, how=how))
    return out


def main():
    S = MS.Snap()
    full = props(S, 1.0, 1.0)
    nom = props(S)
    pm = sum(full[i]['m'] for i, p in enumerate(S.parts) if p['kind'] in ('print', 'inlay') and (p['mat'] or 'PETG').startswith('PETG'))
    cm = sum(full[i]['m'] for i, p in enumerate(S.parts) if p['group'] == 'case')
    mj = json.load(open(os.path.join(U.ROOT, 'gen', 'model', 'model.json')))['numbers']
    tot = sum(x['m'] for x in nom)
    res = dict(print_mass_solid_g=pm * 1e3, model_print_mass_g=mj['print_mass_g'], case_mass_solid_g=cm * 1e3, model_case_mass_g=mj['case_mass_g'],
               total_nominal_kg=tot, parts=[dict(name=p['name'], **nom[i]) for i, p in enumerate(S.parts)],
               solid=[dict(name=p['name'], m=full[i]['m']) for i, p in enumerate(S.parts)])
    json.dump(res, open(os.path.join(U.GEN, 'mass.json'), 'w'), ensure_ascii=False, indent=0)
    print(f"print solid {pm*1e3:.0f} g (model {mj['print_mass_g']}), case solid {cm*1e3:.0f} g (model {mj['case_mass_g']}), total nominal {tot:.2f} kg")
    by = {}
    for i, p in enumerate(S.parts):
        by[p['group']] = by.get(p['group'], 0) + nom[i]['m']
    print({k: round(v * 1e3) for k, v in sorted(by.items(), key=lambda x: -x[1])})


if __name__ == '__main__':
    main()
