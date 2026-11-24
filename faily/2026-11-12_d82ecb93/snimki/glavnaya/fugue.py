"""Фуга «Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt» (Tractatus 5.6) — нотный текст.

Тема — по слогам: ударный слог на доле, «Gren-zen» и «mei-ner» — пунктир, «Welt» — итог. Диапазон темы — ровно
октава, и оба «Grenzen» стоят на её краях: первое — на нижнем D, второе — на верхнем D. Тема ни разу не выходит за
свою октаву: язык не выходит за свои границы.

    python3 fugue.py     — печать голосов и проверки
"""
from counterpoint import (Harmony, Key, ch, check, dmap, generate, nm, slots_between, sounding, tmap, transpose)

Dm, Am, F, Gm = Key(2, "minor"), Key(9, "minor"), Key(5, "major"), Key(7, "minor")
Cmaj, Bb = Key(0, "major"), Key(10, "major")

# тема (D минор, от D4): (доля относительно начала такта темы, длительность, высота)
#   Die | GREN-zen MEI-ner SPRA-che be- | DEU-ten die GREN-zen MEI-ner | WELT
SUBJECT = [(-0.5, 0.5, 69),                                                       # Die        A4
           (0, 0.75, 62), (0.75, 0.25, 64), (1, 0.75, 65), (1.75, 0.25, 67),     # Grenzen meiner  D4 — нижняя граница
           (2, 1, 69), (3, 0.5, 70), (3.5, 0.5, 69),                             # Sprache be-
           (4, 1, 73), (5, 0.5, 70), (5.5, 0.5, 67),                             # -deuten die (ум. септаккорд)
           (6, 0.75, 74), (6.75, 0.25, 72), (7, 0.75, 70), (7.75, 0.25, 67),     # Grenzen meiner  D5 — верхняя граница
           (8, 1, 69)]                                                            # Welt       A4
SYLL = ["Die", "Gren-", "zen", "mei-", "ner", "Spra-", "che", "be-", "deu-", "ten", "die", "Gren-", "zen", "mei-",
        "ner", "Welt"]


def subject_harmony(key, B, tonal_from=None):
    """гармония темы: i i6 III VI | V vii°7 i iv | V"""
    h = []
    plan = [(-0.5, 0, "m", 0), (0, 0, "m", 0), (1, 0, "m", 1), (2, 2, "M", 0), (3, 5, "M", 0),
            (4, 4, "M", 0), (5, 6, "d7", 0), (6, 0, "m", 0), (7, 3, "m", 0), (8, 4, "M", 0)]
    for t, deg, q, inv in plan:
        k = tonal_from if (tonal_from is not None and t < 0) else key
        d = deg if not (tonal_from is not None and t < 0) else 0
        h.append((B + t, ch(k, d, q, inv), key))
    return h


def subject(key, B, octave_deg=0):
    """тема в ладу key (D минор → key по ступеням), начало такта темы — доля B"""
    return tmap(SUBJECT, Dm, key, shift=octave_deg, dt=B)


def answer(key_from, B, octave_deg=0):
    """тональный ответ: Die и первое Grenzen меняются местами (V→I, I→V), остальное — в доминанте"""
    dom = Key((key_from.tonic + 7) % 12, key_from.mode)
    notes = tmap(SUBJECT, Dm, dom, shift=octave_deg, dt=B)
    # Die: доминанта лада → тоника (вместо II в доминанте), Grenzen: тоника → доминанта
    t0, d0, m0 = notes[0]
    notes[0] = (t0, d0, m0 - 2)  # E → D (в D миноре)
    return notes


def inversion(B, shift_semis=0):
    """зеркало темы (вокруг D, по ступеням натурального минора), в соль миноре"""
    out = []
    for t, d, m in SUBJECT:
        deg, alt = Dm.degree(m)
        out.append((B + t, d, Dm.pitch(-deg + 0, -alt) - 0 + shift_semis))
    return out


def show(name, line):
    print(name, " ".join(f"{nm(m)}@{t:g}" for t, d, m in line))


if __name__ == "__main__":
    show("subject", subject(Dm, 4))
    show("answer ", answer(Dm, 12, octave_deg=0))
    show("F-dur  ", subject(F, 48))
    show("A-moll ", subject(Am, 80, -7))
    show("inv    ", inversion(64))
