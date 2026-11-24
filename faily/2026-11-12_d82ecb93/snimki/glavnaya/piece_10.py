#!/usr/bin/env python3
"""Toccata «Le Fantôme» pour grand orgue — «Призрак Оперы», каким его написал бы Боэльман (≈ 2:30).

Модель — Toccata из «Готической сюиты» Боэльмана: вечное движение шестнадцатыми в мануалах, аккорды каждую долю,
неподвижный минор «дрожит» на полутон (у Боэльмана — нижний сосед квинты), тема гремит в педали, в кульминации —
та же тема в увеличении, в конце пикардийская терция. От «Призрака» — ре минор, стук неподвижного баса, каждый
куплет выше прежнего (d → g, затем a). Тема своя — та же, что в баховском Praeludium d-moll: пара пьес.

  вступление        токката одна; «дрожь»: верхний вздох a–b в правой руке, нижний сосед квинты — в левой
  тема в педали     d → g, полный орган
  голос в тишине    тихий регистр: тема наверху, шестнадцатые в левой, педаль пульсирует восьмыми (g → c)
  тема в педали     на тон выше: a → d
  разработка        голова темы в педали всё выше (g – a – b – c), от тихого к полному; пункт на A, ум. септаккорд,
                    фермата, пассаж вниз
  тема в увеличении кульминация: тема вдвое медленнее под полными аккордами
  кода              каданс, тоническая педаль, плагальный оборот, ре мажор

    python3 -m kit run requests/boellmann-phantom/piece.py --parts
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kit.events import Piece  # noqa: E402

BPM = 126
SPB = 60 / BPM
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6)}
MINOR = (0, 2, 3, 5, 7, 8, 10)


def chord(name, k=0):
    """'Dm', 'A7', 'C#dim7', 'G/B' → (pcs, bass pc, root pc, quality), транспонировано на k"""
    name, _, bass = name.partition("/")
    root = NAMES[name[0]]
    i = 1
    while i < len(name) and name[i] in "b#":
        root += -1 if name[i] == "b" else 1
        i += 1
    q = name[i:]
    pcs = {(root + k + x) % 12 for x in QUAL[q]}
    b = root
    if bass:
        b = NAMES[bass[0]] + sum(-1 if c == "b" else 1 for c in bass[1:])
    return pcs, (b + k) % 12, (root + k) % 12, q


# ===================================================================== тема (своя; та же, что в Praeludium)
# в педали: на три октавы ниже сопрановой записи (a = A1); гармония — под бас (бас каждой доли = звук темы)
SONG = [(-1, .5, 69), (-.5, .5, 69),
        (0, 1.5, 74), (1.5, .5, 73), (2, 1, 74), (3, 1, 76),
        (4, 2, 77), (6, 1, 76), (7, 1, 74),
        (8, 1.5, 72), (9.5, .5, 70), (10, 1, 69), (11, 1, 67),
        (12, 3, 69)]
SEQ = [(-1, .5, 72), (-.5, .5, 72),
       (0, 1.5, 77), (1.5, .5, 76), (2, 1, 77), (3, 1, 79),
       (4, 2, 81), (6, 1, 79), (7, 1, 77),
       (8, 1.5, 79), (9.5, .5, 78), (10, 1, 79), (11, 1, 81),
       (12, 2, 82), (14, 1, 81), (15, 1, 79)]
# каданс темы в басу: es d c b | a b c d(2) | es(2) d(2) | g — в g-moll (относительно d)
PCAD = [(0, 1, 75), (1, 1, 74), (2, 1, 72), (3, 1, 70),
        (4, 1, 69), (5, 1, 70), (6, 1, 72), (7, 1, 74),
        (8, 2, 75), (10, 2, 74),
        (12, 4, 67)]
PSONG_H = ["Dm", "Dm", "Dm", "C/E", "F", "F", "C/E", "Dm", "C", "C7", "F/A", "Gm", "A", "A", "A", "C7"]
PSEQ_H = ["F", "F", "F", "C7/G", "F/A", "F/A", "C7/G", "F", "Gm", "Gm", "Gm", "D7/A", "Gm/Bb", "Gm/Bb", "D/A", "Gm"]
PCAD_H = ["Cm/Eb", "Gm/D", "Cm", "Gm/Bb", "D7/A", "Gm/Bb", "Cm", "D", "Cm/Eb", "Cm/Eb", "D7", "D7", "Gm", "Gm", "Gm", "Gm"]
# та же тема наверху (голос в тишине): гармония — под мелодию (как в Praeludium)
CAD = [(0, 1, 75), (1, 1, 74), (2, 1, 72), (3, 1, 70),
       (4, 1, 69), (5, .5, 70), (5.5, .5, 72), (6, 2, 74),
       (8, 2, 70), (10, 2, 69),
       (12, 4, 67)]
SONG_H = ["Dm", "Dm", "Dm", "A7", "Bb", "Bb", "C", "Gm", "C", "C7", "F", "Gm/Bb", "A", "A", "A", "C7"]
SEQ_H = ["F", "F", "F", "C7", "F", "F", "C", "F", "Gm", "Gm", "Gm", "D7", "Gm", "Gm", "D7", "Gm"]
CAD_H = ["Cm", "Gm", "Cm", "Gm/Bb", "D7", "Gm", "D7", "D7", "Gm/D", "Gm/D", "D7", "D7", "Gm", "Gm", "Gm", "Gm"]


class Org:
    def __init__(self):
        self.p = Piece("Toccata «Le Fantôme» (Призрак Оперы, как написал бы Боэльман)", bpm=BPM, meter=(4, 4),
                       key="D minor", seed=1895)
        self.p.meta["subtitle"] = "pour grand orgue"
        self.p.meta["sends"] = {"organ": 0.5}
        self.prev = {}
        self.slow = []

    def perf(self, beat):
        s = 0.0
        for b0, b1, f in sorted(self.slow):
            if beat <= b0:
                break
            s += (min(beat, b1) - b0) * (f - 1)
        return (beat + s) * SPB

    def n(self, m, beat, dur, staff, reg="org_loud", vel=0.6, legato=0.92, gain=0.5):
        if reg == "org_quiet" and m < 36:
            reg = "org_loud"
        t0, t1 = self.perf(beat), self.perf(beat + dur)
        e = self.p.note(reg, m, t0, max(0.05, (t1 - t0) * legato), vel=vel, gain=gain, release=0.35,
                        pan={"RH": 0.2, "LH": -0.15, "Ped": 0.0}[staff],
                        part=f"Organ {staff}" if staff != "Ped" else "Organ Pedal")
        e["wt"], e["wdur"] = beat * SPB, dur * SPB
        return e

    def voicing(self, harm, k, lo, hi, key, size=3):
        pcs = chord(harm, k)[0]
        cands = []
        for start in range(lo, hi):
            if start % 12 not in pcs:
                continue
            v, m = [start], start
            while len(v) < size:
                m += 1
                if m % 12 in pcs:
                    v.append(m)
            if v[-1] <= hi:
                cands.append(v)
        prev = self.prev.get(key)
        best = cands[len(cands) // 2] if prev is None else min(cands, key=lambda v: sum(abs(a - b) for a, b in zip(v, prev)))
        self.prev[key] = best
        return best

    def toccata(self, beat0, harms, k, tonic, staff="RH", lo=72, hi=88, reg="org_loud", gain=0.5, chords=True,
                clo=53, chi=67, creg=None):
        """вечное движение: на каждую долю — верхний звук аккорда и два нижних (верх, низ, середина, низ);
        на неподвижной гармонии верх третьей доли — верхний сосед по гамме (вздох a–b), а левая рука на второй
        доле опускает квинту на полутон (у Боэльмана — соль–фа-диез–соль). chords: аккорды левой руки каждую долю"""
        scale = {(tonic + 2 + x) % 12 for x in MINOR}
        for j, h in enumerate(harms):
            b = beat0 + j
            bar = (j // 4) * 4
            static = all(harms[min(len(harms) - 1, bar + i)] == h for i in range(4)) and bar + 3 < len(harms)
            v = self.voicing(h, k, lo, hi, staff + "fig" + reg, 3)
            top = v[2]
            if static and j % 4 == 2:
                top = next(x for x in range(top + 1, top + 3) if x % 12 in scale)
            for i, m in enumerate((top, v[0], v[1], v[0])):
                self.n(m, b + i / 4, 0.25, staff, reg, 0.62, legato=0.9, gain=gain * (1.08 if i == 0 else 1.0))
            if chords:
                pcs, _, root, q = chord(h, k)
                c = self.voicing(h, k, clo, chi, "LHch" + (creg or reg), 3)
                if static and j % 4 == 1:
                    fifth = (root + (6 if q.startswith("dim") else 7)) % 12
                    c = [m - 1 if m % 12 == fifth else m for m in c]
                for m in c:
                    self.n(m, b, 1, "LH", creg or reg, 0.6, legato=0.55, gain=gain * 0.95)

    def theme(self, notes, beat0, k, staff="Ped", reg="org_loud", oct=-36, aug=1, gain=0.55, legato=0.9):
        for b, d, m in notes:
            self.n(m + k + oct, beat0 + b * aug, d * aug, staff, reg, 0.7, legato=legato, gain=gain)

    def pulse(self, beat0, harms, k, lo=38, hi=50, reg="org_quiet", gain=0.45):
        """педаль-пульс восьмыми на басу гармонии — тень неподвижного баса «Призрака»"""
        prev = (lo + hi) // 2
        for j, h in enumerate(harms):
            b = chord(h, k)[1]
            m = min((x for x in range(lo, hi + 1) if x % 12 == b), key=lambda x: abs(x - prev))
            prev = m
            for i in range(2):
                self.n(m, beat0 + j + i / 2, 0.5, "Ped", reg, 0.6, legato=0.6, gain=gain * (1.1 if i == 0 else 1.0))


def per_beat(h, n):
    return [h] * n


# ===================================================================== разделы
def intro(o, b0):
    """4 такта: токката одна; Dm, Dm, Gm/D, A7 — последний такт — затакт темы в педали"""
    harms = per_beat("Dm", 8) + per_beat("Gm/D", 4) + per_beat("A7", 4)
    o.toccata(b0, harms, 0, 0)
    return b0 + 16


def pedal_theme(o, b0, k, tonic, gain=0.5):
    """12 тактов: тема в педали d → g (относительно k); над ней токката и аккорды"""
    harms = PSONG_H + PSEQ_H + PCAD_H
    o.theme([x for x in SONG if x[0] < 0], b0, k)  # затакт — в последней доле предыдущего раздела
    o.theme([x for x in SONG if x[0] >= 0], b0, k)
    o.theme(SEQ, b0 + 16, k)
    o.theme(PCAD, b0 + 32, k)
    o.toccata(b0, harms[:16], k, tonic=k, gain=gain)
    o.toccata(b0 + 16, harms[16:], k, tonic=k + 5, gain=gain)
    return b0 + 48


def link(o, b0, harm, k, tonic, reg="org_loud", gain=0.5, pedal=None):
    o.toccata(b0, per_beat(harm, 8), k, tonic, reg=reg, gain=gain)
    if pedal is not None:
        o.n(pedal, b0, 7, "Ped", reg if pedal >= 36 else "org_loud", 0.6, gain=gain * 0.9)
    return b0 + 8


def quiet_voice(o, b0, k):
    """12 тактов, тихий регистр: тема наверху (g), шестнадцатые — в левой руке, педаль пульсирует восьмыми"""
    mel = SONG + [(16 + b, d, m) for b, d, m in SEQ] + [(32 + b, d, m) for b, d, m in CAD]
    harms = SONG_H + SEQ_H + CAD_H
    o.theme(mel, b0, k, staff="RH", reg="org_quiet", oct=0, gain=0.62, legato=0.95)
    o.toccata(b0, harms[:16], k, tonic=k, staff="LH", lo=55, hi=70, reg="org_quiet", gain=0.42, chords=False)
    o.toccata(b0 + 16, harms[16:], k, tonic=k + 5, staff="LH", lo=55, hi=70, reg="org_quiet", gain=0.42, chords=False)
    o.pulse(b0, harms, k)
    return b0 + 48


def development(o, b0):
    """голова темы в педали всё выше: g, a, b, c (по 2 такта), от тихого к полному; пункт на A; фермата"""
    keys = [5, 7, 8, 10]
    for u, kk in enumerate(keys):
        st = b0 + 8 * u
        reg = "org_quiet" if u < 2 else "org_loud"
        g = 0.42 + 0.04 * u
        head = [x for x in SONG if 0 <= x[0] < 4]
        o.theme(head, st, kk, reg=reg if reg == "org_loud" else "org_loud", gain=g + 0.05)
        nxt = keys[u + 1] if u + 1 < len(keys) else None
        harms = ["Dm", "Dm", "Dm", "A7/E"] + ["A7"] * 3 + ["A7" if nxt is None else "X"]
        if nxt is not None:
            harms[7] = None
        hs = [h for h in harms if h not in (None, "X")]
        o.toccata(st, hs, kk, tonic=kk, reg=reg, gain=g, clo=53, chi=67)
        if nxt is not None:  # последняя доля — уже доминанта следующей тональности, в педали затакт
            o.toccata(st + 7, ["A7"], nxt, tonic=nxt, reg=reg, gain=g)
            o.theme([x for x in SONG if x[0] < 0], st + 8, nxt, gain=g + 0.05)
        o.n(69 + kk - 36 - 12 if 69 + kk - 48 >= 33 else 69 + kk - 36, st + 4, 3, "Ped", "org_loud", 0.62, gain=g + 0.05)
    # органный пункт на A: C#dim7 / A7, верх фигурации выше каждый такт
    st = b0 + 32
    for u in range(4):
        h = "C#dim7" if u % 2 == 0 else "A7"
        o.toccata(st + 4 * u, per_beat(h, 4), 0, 0, lo=72 + 2 * u, hi=90 + 2 * u, gain=0.56, clo=52, chi=67)
    o.n(33, st, 16, "Ped", "org_loud", 0.7, gain=0.6)
    o.n(45, st, 16, "Ped", "org_loud", 0.7, gain=0.45)
    # фермата на ум. септаккорде и пассаж вниз по нему, в конце — затакт темы в увеличении
    sf = st + 16
    for m in (33, 45, 52, 55, 58, 61, 64, 67, 70, 73, 76):
        o.n(m, sf, 4, "Ped" if m < 50 else ("LH" if m < 62 else "RH"), "org_loud", 0.72, legato=0.97, gain=0.5)
    run = [x for x in range(94, 57, -1) if x % 12 in (1, 4, 7, 10)][:12]
    for j, m in enumerate(run):
        o.n(m, sf + 4 + j / 4, 0.25, "RH" if m >= 62 else "LH", "org_loud", 0.66, gain=0.55)
    o.slow += [(sf, sf + 4, 1.9), (sf + 4, sf + 7, 1.15)]
    return sf + 8


def augmented(o, b0):
    """8 тактов: тема в педали вдвое медленнее (d), над ней токката и полные аккорды — кульминация"""
    harms = [h for h in PSONG_H for _ in range(2)]
    harms[-2:] = ["A7", "A7"]
    o.theme([x for x in SONG if x[0] < 0], b0, 0, aug=2, gain=0.62)
    o.theme([x for x in SONG if x[0] >= 0], b0, 0, aug=2, gain=0.62)
    o.toccata(b0, harms, 0, 0, gain=0.58, clo=55, chi=69)
    o.toccata(b0, harms, 0, 0, staff="LH", lo=50, hi=64, gain=0.0001, chords=False)  # (только ради голосоведения)
    return b0 + 32


def coda(o, b0):
    """каданс, тоническая педаль, плагальный оборот (g/d – D), пикардийская терция, последний аккорд — широко"""
    bars = ["Dm", "Bb", "Gm/Bb", "A7", "Dm", "Gm/D", "D"]
    peds = [38, 34, 34, 33, 26, 26, 26]
    harms = [h for h in bars for _ in range(4)]
    o.toccata(b0, harms[:16], 0, 0, gain=0.6, clo=55, chi=69)
    o.toccata(b0 + 16, harms[16:24], 0, 0, gain=0.6, clo=55, chi=69)
    # ре мажор: та же фигура в мажоре (верхний сосед — си натуральное: тоника D мажора)
    o.toccata(b0 + 24, harms[24:], 0, 0, gain=0.62, clo=54, chi=69)
    for j, m in enumerate(peds):
        o.n(m, b0 + 4 * j, 4, "Ped", "org_loud", 0.7, legato=0.97 if j >= 4 else 0.9, gain=0.62)
    fin = b0 + 28
    for m in (26, 38, 50, 57, 62, 66, 69, 74, 78, 81, 86):
        o.n(m, fin, 4, "Ped" if m < 50 else ("LH" if m < 62 else "RH"), "org_loud", 0.74, legato=0.98, gain=0.5)
    o.slow += [(fin - 4, fin, 1.15), (fin, fin + 4, 2.0)]
    return fin + 4


def build(ctx):
    o = Org()
    plan = []
    b = 0
    plan.append((b, "Вступление")); b = intro(o, b)
    plan.append((b, "Тема в педали (d → g)")); b = pedal_theme(o, b, 0, 0)
    plan.append((b, "Связка")); b = link(o, b, "Gm", 5, 5, reg="org_quiet", gain=0.45)
    plan.append((b, "Голос в тишине (g → c)")); b = quiet_voice(o, b, 5)
    plan.append((b, "Связка к a-moll")); b = link(o, b, "A7", 7, 7, gain=0.52, pedal=40)
    plan.append((b, "Тема в педали (a → d)")); b = pedal_theme(o, b, 7, 7, gain=0.54)
    plan.append((b, "Разработка")); b = development(o, b)
    plan.append((b, "Тема в увеличении (d)")); b = augmented(o, b)
    plan.append((b, "Кода")); b = coda(o, b)
    for bt, label in plan:
        o.p.mark(o.perf(bt), label)["wt"] = bt * SPB
    o.p.meta["beats"] = b
    return o.p
