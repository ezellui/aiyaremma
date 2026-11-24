"""Stage 1, steps B-D (spec §4.3): the relative motion of every candidate pair over the snapshot's states, its joint
type, the geometric basis of every 'rigid', axes of revolute joints and their axial retention.
Writes data/joints.json; records with source 'manual' are kept as they are, and an automatic record is not written
for a pair that has a manual one. Usage: python3 -I tools/physics/classify.py"""
import sys, os, json, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U
import numpy as np
import meshes as MS

DEFORM_RES = 0.02          # mm, rigid-body residual (spec)
RESHAPE_STATES = 0.05      # parts reshaped in more than 5 % of states are 'deformable'; fewer: those states are skipped
ROD_RE = re.compile(r'(\brod\b|\bpin\b|shaft|axle|\baxis\b|arbor|\bscrew\b)')


def inlay_owner(name, names):
    """Parts that belong to another part of the same print (spec §4.3, step A; trap 11)."""
    if name.endswith(' inlay'):
        return name[:-6] if name[:-6] in names else None
    if name == 'case device plaque':
        return 'case top tower -1'
    m = re.match(r'case (pillar base|pillar capital|finial) ([+-]1)$', name)
    if m:
        return f'case pillar {m.group(2)}'
    return None


def deformable(S):
    """Parts the model deforms (springs, tapes, sheet, ribbon, wires) or rebuilds with another length (variable levers)."""
    bad = S.resid > DEFORM_RES
    frac = bad.mean(0)
    dfm = {S.names[i] for i in np.nonzero(frac > RESHAPE_STATES)[0]}
    for i, p in enumerate(S.parts):
        if p['kind'] == 'ref' or 'spring' in p['name'] or p['name'] == 'mainspring':
            dfm.add(p['name'])
    return dfm, bad


def rel_motion(S, i, j, skip):
    """Relative pose of j in i's frame over the states (rest world coordinates), states where either is reshaped skipped."""
    Ms = []
    for s in range(len(S.states)):
        if skip[s, i] or skip[s, j] or S.method[s, i] < 0 or S.method[s, j] < 0:
            continue
        Ms.append(np.linalg.inv(S.poses[s, i]) @ S.poses[s, j])
    return np.array(Ms)


def rot_axis(R):
    c = (np.trace(R) - 1) / 2
    ang = math.acos(max(-1.0, min(1.0, c)))
    if ang < 1e-9:
        return 0.0, np.zeros(3)
    w = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    n = np.linalg.norm(w)
    if n < 1e-9:               # 180 deg
        e, v = np.linalg.eigh((R + np.eye(3)) / 2)
        return ang, v[:, -1]
    return ang, w / n


def classify(Ms, ang_tol=1e-4, t_tol=2e-3):
    """('rigid'|'revolute'|'prismatic'|'cylindrical'|'general', axis dict, range dict)."""
    if len(Ms) == 0:
        return 'rigid', None, {}
    angs, axes, ts = [], [], []
    for M in Ms:
        a, w = rot_axis(M[:3, :3]); angs.append(a); axes.append(w); ts.append(M[:3, 3])
    angs = np.array(angs); ts = np.array(ts)
    if angs.max() < ang_tol and np.linalg.norm(ts, axis=1).max() < t_tol:
        return 'rigid', None, {}
    if angs.max() < ang_tol:
        U_, sv, Vt = np.linalg.svd(ts, full_matrices=False)
        d = Vt[0]
        if sv[1] / max(1.0, math.sqrt(len(ts))) < 0.02 or (len(sv) > 1 and sv[1] < 0.02 * sv[0] and sv[1] < 0.05):
            proj = ts @ d
            return 'prismatic', dict(d=d.tolist()), dict(travel=[float(proj.min()), float(proj.max())])
        return 'general', None, dict(trans=float(np.linalg.norm(ts, axis=1).max()))
    big = angs > ang_tol
    W = np.array(axes)[big]
    d = W[np.argmax(angs[big])]
    W = W * np.sign(W @ d)[:, None]
    if np.max(np.linalg.norm(np.cross(W, d), axis=1)) > 0.02:
        return 'general', None, dict(ang=float(np.degrees(angs.max())))
    d = W.mean(0); d /= np.linalg.norm(d)
    pts, axial = [], []
    for M, a in zip(Ms, angs):
        t = M[:3, 3]; ta = float(t @ d); axial.append(ta)
        if a > 1e-3:
            R = M[:3, :3]
            p, *_ = np.linalg.lstsq(np.eye(3) - R, t - ta * d, rcond=None)
            pts.append(p - (p @ d) * d)
    if not pts:      # tiny rotations only: treat as revolute through the centre
        return 'general', None, dict(ang=float(np.degrees(angs.max())))
    pts = np.array(pts); p0 = np.median(pts, 0)
    spread = float(np.linalg.norm(pts - p0, axis=1).max())
    if spread > 0.3:
        return 'general', None, dict(ang=float(np.degrees(angs.max())), spread=spread)
    axial = np.array(axial)
    rng = dict(ang=[float(np.degrees(-angs.max())), float(np.degrees(angs.max()))], axis_spread=spread)
    if np.abs(axial).max() > 0.05:
        rng['axial'] = [float(axial.min()), float(axial.max())]
        return 'cylindrical', dict(p=p0.tolist(), d=d.tolist()), rng
    return 'revolute', dict(p=p0.tolist(), d=d.tolist()), rng


def is_rod(p):
    return bool(ROD_RE.search(p['name'])) or (p['bom'] or '').startswith(('rod', 'pin', 'shaft'))


def basis_rigid(pa, pb, pr, owners):
    """Geometric basis of a pair that does not move (spec §4.3, step C): (type, fastener, status, why)."""
    na, nb = pa['name'], pb['name']
    if owners.get(na) == nb or owners.get(nb) == na:
        return 'rigid', 'print', 'modeled', 'одна печать (вставка или часть корпусной детали)'
    for p in (pa, pb):
        if (p['bom'] or '').startswith(('grubM', 'screw')):
            return 'rigid', 'screw M3', 'modeled', 'винт в модели'
    if pr['overlap'] > 0.0:
        rod = pa if is_rod(pa) else pb if is_rod(pb) else None
        if rod is not None:
            return 'rigid', 'press', 'modeled', f'{rod["name"]} в отверстии с натягом (пересечение {pr["overlap"]} мм³)'
        return 'rigid', 'press', 'modeled', f'пересечение {pr["overlap"]} мм³ (запрессовка или вклейка по замыслу)'
    txt = ' '.join([pa['note'] or '', pb['note'] or '']).lower()
    for kw, f in (('винт', 'screw'), ('клей', 'glue'), ('вклеен', 'glue'), ('приклеен', 'glue'), ('запрессов', 'press'),
                  ('приверн', 'screw'), ('т-гайк', 'screw M5 + T-nut'), ('м5', 'screw M5 + T-nut'), ('м3', 'screw M3')):
        if kw in txt:
            return 'planar_rest', f, 'described', f'в примечании: «{kw}»'
    return 'planar_rest', None, 'missing', 'стоит касанием, крепления нет ни в модели, ни в примечании'


def main():
    S = MS.Snap()
    pairs = json.load(open(os.path.join(U.GEN, 'pairs.json')))
    names = set(S.names)
    owners = {n: inlay_owner(n, names) for n in S.names}
    owners = {k: v for k, v in owners.items() if v}
    dfm, skip = deformable(S)
    import contacts as CT
    audit = {}
    for grp, title, states, prs in CT.groups():
        for a, b, note in prs:
            audit[(a, b)] = audit[(b, a)] = note
    path = os.path.join(U.DATA, 'joints.json')
    manual = []
    if os.path.exists(path):
        manual = [j for j in json.load(open(path))['joints'] if j.get('source') == 'manual']
    mkeys = {(j['a'], j['b']) for j in manual} | {(j['b'], j['a']) for j in manual}
    joints = []
    # the frame is one ground body (its pairs are checked separately -- spec §4.3 A)
    ground = ['frame front', 'frame back', 'frame side -1', 'frame side +1']
    for pr in pairs:
        a, b = pr['a'], pr['b']
        if (a, b) in mkeys:
            continue
        if a in ground and b in ground:
            continue
        pa, pb = S.p(a), S.p(b)
        i, j = S.idx[a], S.idx[b]
        rec = dict(a=a, b=b, gap=pr['gap'], overlap=pr['overlap'], allow=pr['allow'], doc='', note='')
        if a in dfm or b in dfm:
            rec.update(type='flex', source='auto:pose', status='modeled', fastener=None,
                       note='деформируемая деталь модели (пружина, лента, лист, трос, рычаг переменной длины)')
            joints.append(rec); continue
        Ms = rel_motion(S, i, j, skip)
        typ, ax, rng = classify(Ms)
        rec.update(range=rng)
        if typ == 'rigid':
            t, f, st, why = basis_rigid(pa, pb, pr, owners)
            rec.update(type=t, fastener=f, status=st, source='auto:geom', basis=why)
        elif typ in ('revolute', 'cylindrical', 'prismatic'):
            rec.update(type=typ, axis=ax, fastener=None, status='modeled', source='auto:pose')
            if pr['overlap'] > 0.5 and typ != 'prismatic':
                rec['note'] = f'ось с пересечением {pr["overlap"]} мм³ — посадка с натягом при подвижном соединении?'
        else:
            k = 'cam' if (a, b) in audit else 'contact_only'
            rec.update(type=k, fastener=None, status='modeled', source='auto:pose')
        if (a, b) in audit:
            rec['audit'] = audit[(a, b)]
        joints.append(rec)
    for n, o in owners.items():
        if not any({j['a'], j['b']} == {n, o} for j in joints):
            joints.append(dict(a=n, b=o, type='rigid', fastener='print', status='modeled', source='auto:geom', gap=None, overlap=None,
                               basis='одна печать', doc='§«Корпус»', note=''))
    joints = manual + joints
    out = dict(version=1, model_revision='0.12', ground=ground, deformable=sorted(dfm), bodies_override={}, joints=joints)
    json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print('joints', len(joints), Counter(j['type'] for j in joints))
    print('status', Counter((j['type'], j['status']) for j in joints))


if __name__ == '__main__':
    main()
