"""rev. 0.14 (physics checks, stage 1): supports and retainers the model lacked.

* base plate: 4 mm plywood under the frame, screwed into the profiles' bottom slots (M5 + T-nuts). Everything that
  stood on z = 0 without anything under it (the cycle bearing blocks, the selector posts, the lock bail guides, the
  ball race, the rocker bracket) now stands on it and is screwed through it from below (M3 into inserts). Windows let
  the side plates of the frames R, O and N go 0.5 mm under z = 0 at full travel.
* comb bridge: the key comb and the space comb lay on the levers; a square bar (Д16Т 6x6) across the front on two
  posts standing on the base plate carries them by four tabs.
* lever pivot rod: it ended 2 mm short of its brackets; it now passes through them and two E-clips (DIN 6799, 3.2)
  hold it outside the brackets."""
import math
import params as P
from geo import box, cyl

PLATE_Z = (-4.0, 0.0)
BAIL_WINDOWS = [(109.0, 120.5), (147.5, 154.5)]       # |x| of the side plates of frames R, O (109..120) and N (148..154)
BRIDGE = dict(x=(-207.0, 206.0), y=(-373.0, -367.0), z=(56.0, 62.0))
POSTS = ((-206.0, -200.0), (199.0, 205.0))
KEY_TABS = ((-138.0, -134.5), (134.5, 138.0))
SPACE_TABS = ((-102.0, -97.0), (97.0, 102.0))
TAB_Z = (60.3, 62.0)


def parts(st, Part, COL):
    out = []
    pl = box(-P.FRAME_X, P.FRAME_X, P.FRAME_Y0, P.FRAME_Y1, *PLATE_Z)
    for x0, x1 in BAIL_WINDOWS:
        for s in (-1, 1):
            a, b = sorted((s * x0, s * x1))
            pl = pl - box(a, b, -391.0, -230.0, PLATE_Z[0] - 1, PLATE_Z[1] + 1)
    out.append(Part('base plate', 'frame', 'cut', pl, (196, 170, 130), 'plywood4_500x525', 'фанера',
                    note='основание: фанера 4 мм под рамой, на винтах М5 с Т-гайками в нижние пазы профиля; детали, стоящие на '
                         'основании, привёрнуты снизу винтами М3 во вставки (ред. 0.14)'))
    out.append(Part('comb bridge', 'keys', 'cut', box(BRIDGE['x'][0], BRIDGE['x'][1], *BRIDGE['y'], *BRIDGE['z']), COL['steel'],
                    'bar6x6x413', 'Д16Т', note='брус гребёнок: квадрат 6×6 мм, на двух стойках; гребёнки клавиш и пробела на лапках, на винтах М3 (ред. 0.14)'))
    for k, (x0, x1) in enumerate(POSTS):
        out.append(Part(f'comb post {-1 if k == 0 else 1:+d}', 'keys', 'print', box(x0, x1, *BRIDGE['y'], 0.0, BRIDGE['z'][0]),
                        (110, 112, 120), 'comb_post', 'PETG', note='стойка бруса гребёнок на основании (ред. 0.14)'))
    for k, (x0, x1) in enumerate(KEY_TABS):
        out.append(Part(f'key comb tab {-1 if k == 0 else 1:+d}', 'keys', 'print', box(x0, x1, BRIDGE['y'][1], -308.0, *TAB_Z),
                        (110, 112, 120), 'comb_tab_key', 'PETG', note='лапка гребёнки клавиш от бруса (ред. 0.14)'))
    for k, (x0, x1) in enumerate(SPACE_TABS):
        out.append(Part(f'space comb tab {-1 if k == 0 else 1:+d}', 'keys', 'print', box(x0, x1, BRIDGE['y'][1], -335.0, *TAB_Z),
                        (110, 112, 120), 'comb_tab_space', 'PETG', note='лапка гребёнки пробела от бруса (ред. 0.14)'))
    zc = (P.LEVER_Z0 + P.LEVER_Z1) / 2
    for s in (-1, 1):
        x0, x1 = sorted((s * 154.0, s * 154.6))
        clip = cyl((x0, P.LEVER_PIVOT_Y, zc), (x1, P.LEVER_PIVOT_Y, zc), 3.6, 24) - cyl((x0 - 1, P.LEVER_PIVOT_Y, zc), (x1 + 1, P.LEVER_PIVOT_Y, zc), 2.0, 16)
        out.append(Part(f'lever pivot clip {s:+d}', 'levers', 'buy', clip, COL['steel'], 'eclip3_2', 'сталь',
                        note='стопорное кольцо DIN 6799 3,2 на оси рычагов (ред. 0.14)'))
    return out
