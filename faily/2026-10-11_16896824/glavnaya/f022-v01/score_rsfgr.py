#!/usr/bin/env python3
"""Score for the R.S.F.G.R. archive video, timed to the frame plan of the scenario.

Every event has a mood; the mood picks the harmony, the instruments and what happens at the three moments the
picture gives: the change of borders (start of 'trans'), the document on screen (start of 'hold') and the flight
to the next event. Themes:
  the Union      — horn/trombone motif D–A–B♭–A over a D-minor pad, timpani on the change of borders;
  the Sleeper    — organ pedal and tremolo double basses, a semitone cluster;
  the repression — pizzicato ostinato, a muted trumpet stab;
  the awake      — a woodwind chorale in C major, open fifths in the horns;
  Yuggoth        — violin tremolo on a whole-tone chord, glockenspiel;
  the dry        — open fifths without a third, single pizzicati, almost silence;
  1997           — every theme gathers into one chorale that resolves to D major when the last lamp lights.

  python3 score_rsfgr.py ../fb/scenario_rsfgr.json out.wav [--from S --to S]
"""
import argparse
import glob
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, "/home/claude/work/fb")
from history import History  # noqa: E402
from render import FPS, build_plan  # noqa: E402

from sampler import SR, Sampler, mix  # noqa: E402

V = "/home/claude/work/samples/VSCO-2-CE"

MOOD = {
    "growth": ["kronstadt", "union", "siberia", "gobi", "mycelaria", "vistula", "elbe", "danube", "fruiting",
               "regrowth", "mekong", "amazonia"],
    "sleeper": ["lenin_sleeps", "voice", "alarm", "chamber", "cylinder", "kara", "sprouted", "protocol"],
    "repress": ["case427", "rassudnik", "act1930", "case611", "case1147", "vessel", "doctrine"],
    "school": ["azbuka"],
    "hymn": ["hymn"],
    "awake": ["sweden", "kremnev", "budapest", "pannonia", "gotland", "waite", "euclid", "bohemia"],
    "heresy": ["urga", "altai", "exodus"],
    "dry": ["drought", "salt", "dry"],
    "lamp": ["receiver"],
    "final": ["stars"],
}
MOOD_OF = {i: m for m, ids in MOOD.items() for i in ids}

D = 2  # pitch class of D
# chords as (root pitch class, intervals)
MIN, MAJ, FIFTH = (0, 3, 7), (0, 4, 7), (0, 7)
GROWTH_PROG = [(2, MIN), (10, MAJ), (7, MIN), (9, MAJ), (5, MAJ), (0, MAJ), (2, MIN), (3, MAJ)]
AWAKE_PROG = [(0, MAJ), (7, MAJ), (9, MIN), (5, MAJ)]
REPRESS_PROG = [(7, MIN), (2, MIN), (3, MAJ), (9, (0, 3, 6))]


def in_range(pc, lo, hi, near=None):
    cands = [m for m in range(lo, hi + 1) if m % 12 == pc % 12]
    if not cands:
        return lo
    if near is None:
        return cands[0]
    return min(cands, key=lambda m: abs(m - near))


class Score:
    def __init__(self, scenario, t_from=0.0, t_to=None):
        self.h = History(scenario)
        self.plan = build_plan(self.h)
        self.total = len(self.plan) / FPS
        self.t_from, self.t_to = t_from, (t_to or self.total)
        self.s = Sampler(self.total + 4)
        self.rng = random.Random(11)
        self.timeline()
        self.voices = {"cb": 38, "vc": 50, "vla": 57, "vln": 65}
        self.tdrums = self.timpani_set()

    # -- the picture's timeline -------------------------------------------------------------------------------
    def timeline(self):
        seg = []
        for k, fr in enumerate(self.plan):
            key = (fr["phase"], fr.get("ev"))
            if not seg or seg[-1][0] != key:
                seg.append([key, k, k])
            else:
                seg[-1][2] = k
        ev = {}
        for (ph, e), a, b in seg:
            if e is None:
                ev.setdefault(ph, {})[ph] = (a / FPS, (b + 1) / FPS)
                continue
            ev.setdefault(e, {})[ph] = (a / FPS, (b + 1) / FPS)
        self.ev = ev
        self.n_events = len(self.h.sc["events"])
        self.intro = ev["intro"]["intro"]
        self.outro = ev["outro"]["outro"]

    def timpani_set(self):
        drums = []
        for i in range(1, 6):
            hits = sorted(glob.glob(f"{V}/Percussion/Timpani/Timpani{i}_Hit_*.wav"))
            rolls = sorted(glob.glob(f"{V}/Percussion/Timpani/Rolls/Timpani{i}_Roll_*.wav"))
            drums.append(dict(hits=hits, rolls=rolls, pitch=[29.8, 34.5, 37.3, 40.0, 42.1][i - 1]))
        return drums

    # -- primitives ---------------------------------------------------------------------------------------------
    def raw(self, path, t, gain=1.0, pan=0.0, bus="perc", shift=0.0, dur=None):
        d = self.s._load(path)
        if shift:
            r = 2 ** (shift / 12)
            pos = np.arange(0, len(d) - 1, r)
            d = np.stack([np.interp(pos, np.arange(len(d)), d[:, c]) for c in range(2)], 1).astype(np.float32)
        if dur is not None:
            k = int(dur * SR)
            if k < len(d):
                tail = min(len(d) - k, int(0.8 * SR))
                d = d[:k + tail].copy()
                d[k:] *= np.linspace(1, 0, tail)[:, None]
        lp, rp = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        y = d * np.array([lp, rp], np.float32) * 1.414 * gain
        s = int(t * SR)
        b = self.s.bus(bus)
        e = min(len(b), s + len(y))
        b[s:e] += y[:e - s]

    def timp(self, t, root_pc, vel=0.7, roll=None):
        # nearest drum to a D2–A2 rendition of the root, retuned
        target = in_range(root_pc, 31, 42, 37)
        dr = min(self.tdrums, key=lambda d: abs(d["pitch"] - target))
        shift = max(-3, min(3, target - dr["pitch"]))
        if roll:
            p = dr["rolls"][-1 if vel > 0.6 else 0]
            self.raw(p, t, gain=0.55 * vel, pan=-0.1, shift=shift, dur=roll)
        else:
            hits = [h for h in dr["hits"] if f"_v{4 if vel > 0.75 else 3 if vel > 0.45 else 1}_" in h] or dr["hits"]
            self.raw(self.rng.choice(hits), t, gain=0.7 * vel, pan=-0.1, shift=shift)

    def pad(self, t0, t1, chord, vel=0.5, arts=("cb_sus", "vc_sus", "vla_sus", "vln_sus"), gain=0.5, attack=0.8,
            bass_only=False):
        root, iv = chord
        pcs = [(root + i) % 12 for i in iv]
        lanes = [("cb", 28, 41, root % 12, arts[0], -0.35), ("vc", 40, 55, pcs[-1] if len(pcs) > 2 else root, arts[1], -0.15),
                 ("vla", 52, 64, pcs[1] if len(pcs) > 2 else pcs[-1], arts[2], 0.15),
                 ("vln", 62, 76, pcs[0] if len(pcs) > 2 else pcs[-1], arts[3], 0.35)]
        if bass_only:
            lanes = lanes[:2]
        dur = t1 - t0
        for lane, lo, hi, pc, art, pan in lanes:
            m = in_range(pc, lo, hi, self.voices[lane])
            self.voices[lane] = m
            self.s.note(art, m, t0, dur, vel=vel, gain=gain, pan=pan, bus="strings", attack=attack, release=1.4)
        return pcs

    def motif(self, t, chord, art="hn_sus", vel=0.6, gain=0.55, octave=None, steps=(0, 7, 8, 7), durs=(0.55, 0.55, 0.55, 1.6)):
        root, iv = chord
        major = 4 in iv
        base = in_range(root, 50, 61, 55) if octave is None else in_range(root, octave, octave + 11)
        st = list(steps)
        if major and 8 in st:
            st = [9 if x == 8 else x for x in st]
        tt = t
        for k, (s_, d_) in enumerate(zip(st, durs)):
            self.s.note(art, base + s_, tt, d_ * 0.95, vel=vel, gain=gain, pan=-0.2, bus="brass", release=0.5)
            tt += d_

    def harp_arp(self, t, chord, n=7, step=0.085, vel=0.5, art="harp", lo=50, gain=0.5, bus="harp"):
        root, iv = chord
        pcs = [(root + i) % 12 for i in iv]
        notes = []
        m = in_range(root, lo, lo + 11)
        while len(notes) < n:
            for i in iv:
                if len(notes) < n:
                    notes.append(m + i)
            m += 12
        for k, nt in enumerate(notes):
            self.s.note(art, nt, t + k * step, 2.5, vel=vel, gain=gain, pan=0.3, bus=bus, release=1.5)

    # -- the whole piece ----------------------------------------------------------------------------------------
    def compose(self):
        S = self.s
        prev = (D, MIN)
        # intro: the Sleeper's pedal, double basses awakening, the motif from far away
        a, b = self.intro
        S.note("org_quiet", 38, a, b - a + 1.6, vel=0.5, gain=0.45, bus="organ", attack=1.5, release=2.0)
        S.note("cb_trem", 38, a + 0.5, b - a + 1.0, vel=0.4, gain=0.35, pan=-0.3, bus="strings", attack=2.5)
        S.note("vc_trem", 45, a + 1.5, b - a, vel=0.35, gain=0.25, pan=-0.1, bus="strings", attack=2.0)
        self.motif(a + 3.0, prev, art="hn_mute", vel=0.35, gain=0.35)
        gi = ai = ri = 0
        for k in range(1, self.n_events + 1):
            e = self.h.sc["events"][k - 1]
            mood = MOOD_OF.get(e.get("id"), "growth")
            ph = self.ev[k]
            t_fly = ph["fly"][0]
            t_tr = ph["trans"][0]
            t_hold = ph["hold"][0]
            t_end = self.ev[k + 1]["fly"][0] if k < self.n_events else self.ev["fly"]["fly"][1] if "fly" in self.ev else ph["hold"][1]
            has_doc = bool(e.get("docs"))
            big = bool(e.get("ops"))
            if mood == "growth":
                ch = GROWTH_PROG[gi % len(GROWTH_PROG)]; gi += 1
                self.pad(t_tr, t_end + 0.6, ch, vel=0.55, gain=0.5)
                self.motif(t_tr, ch, art="hn_sus" if gi % 2 else "tbn_sus", vel=0.62)
                self.timp(t_tr, ch[0], vel=0.75)
                S.note("tba_sus", in_range(ch[0], 29, 40), t_tr, 2.2, vel=0.5, gain=0.4, bus="brass", release=0.8)
                if has_doc:
                    self.harp_arp(t_hold + 0.2, ch, vel=0.45, gain=0.45)
            elif mood == "lamp":
                ch = (5, MAJ)
                self.pad(t_tr, t_end + 0.6, ch, vel=0.45, gain=0.45)
                S.note("org_quiet", in_range(ch[0], 41, 52), t_tr, t_end - t_tr + 0.5, vel=0.4, gain=0.3, bus="organ", attack=1.0)
                for j in range(9):  # lamps lighting one by one
                    S.note("glock", in_range([0, 4, 7, 9][j % 4] + 5, 79, 95), t_tr + 0.3 + j * 0.55, 1.5, vel=0.4, gain=0.25,
                           pan=-0.6 + 0.15 * j, bus="harp")
                self.motif(t_hold + 0.3, ch, art="hn_sus", vel=0.5, gain=0.45)
            elif mood == "sleeper":
                ch = (D, (0, 1, 7))  # the cluster: root, minor second, fifth
                dur = t_end - t_fly + 0.8
                S.note("org_loud" if e.get("vortex_radius_km") else "org_quiet", 26, t_fly, dur, vel=0.6, gain=0.5, bus="organ",
                       attack=1.2, release=2.2)
                S.note("cb_trem", 38, t_fly + 0.2, dur, vel=0.55, gain=0.4, pan=-0.3, bus="strings", attack=1.6)
                S.note("vc_trem", 51, t_tr, t_end - t_tr + 0.6, vel=0.45, gain=0.3, pan=-0.05, bus="strings", attack=1.2)
                S.note("vla_trem", 52, t_tr + 0.3, t_end - t_tr + 0.4, vel=0.35, gain=0.22, pan=0.2, bus="strings", attack=1.5)
                if e.get("vortex_radius_km"):
                    self.timp(t_tr, D, vel=0.85, roll=t_hold - t_tr + 0.4)
                    S.note("tba_sus", 26, t_tr + 0.2, 3.0, vel=0.7, gain=0.45, bus="brass")
                    S.note("tbn_sus", 39, t_tr + 0.4, 2.6, vel=0.6, gain=0.35, bus="brass")
                if e.get("id") in ("lenin_sleeps", "sprouted", "chamber"):
                    # the lullaby: flute over the pedal, descending
                    for j, (n_, d_) in enumerate([(77, 1.0), (74, 0.8), (72, 0.8), (69, 2.0)]):
                        S.note("fl_sus", n_, t_hold + 0.4 + sum(x[1] for x in [(77, 1.0), (74, 0.8), (72, 0.8), (69, 2.0)][:j]), d_,
                               vel=0.35, gain=0.35, pan=0.25, bus="winds", attack=0.15)
                if has_doc:
                    S.note("glock", 86, t_hold + 0.2, 2.0, vel=0.3, gain=0.18, pan=0.4, bus="harp")
                    S.note("glock", 87, t_hold + 1.4, 2.0, vel=0.25, gain=0.15, pan=0.4, bus="harp")
            elif mood == "repress":
                ch = REPRESS_PROG[ri % len(REPRESS_PROG)]; ri += 1
                self.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.32, bass_only=True)
                root = in_range(ch[0], 43, 54)
                pat = [0, 7, 12, 7, 0, 7, 3 if 3 in ch[1] else 4, 7]
                t = t_tr
                beat = 60 / 104 / 2
                j = 0
                while t < t_end - 0.1:
                    S.note("vc_pizz" if j % 8 < 4 else "vla_pizz", root + pat[j % 8], t, 0.25, vel=0.5 if j % 4 == 0 else 0.35,
                           gain=0.42, pan=-0.1 if j % 2 else 0.1, bus="strings", release=0.3)
                    t += beat; j += 1
                S.note("tpt_mute", in_range(ch[0] + 1, 62, 73), t_tr, 0.9, vel=0.55, gain=0.3, pan=0.25, bus="brass")
                S.note("bsn_sus", in_range(ch[0], 34, 45), t_tr, t_end - t_tr, vel=0.4, gain=0.3, pan=0.1, bus="winds", attack=0.4)
                if has_doc:
                    self.timp(t_hold, ch[0], vel=0.4)
            elif mood == "school":
                ch = (5, MAJ)
                self.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.3)
                tune = [72, 72, 79, 79, 81, 81, 79, 77, 77, 76, 76, 74, 74, 72]  # the alphabet song, in F
                tune = [n_ + 5 for n_ in tune]
                for j, n_ in enumerate(tune):
                    S.note("glock", n_ + 12 if n_ + 12 >= 79 else n_ + 24, t_tr + j * 0.42, 0.6, vel=0.35, gain=0.22, pan=0.3,
                           bus="harp")
                    S.note("vln_pizz", n_ - 12 if n_ - 12 >= 55 else n_, t_tr + j * 0.42, 0.3, vel=0.35, gain=0.3, pan=-0.2,
                           bus="strings")
            elif mood == "hymn":
                prog = [(D, MIN), (10, MAJ), (7, MIN), (9, MAJ), (D, MIN)]
                seg = (t_end - t_tr) / len(prog)
                for j, ch in enumerate(prog):
                    tt = t_tr + j * seg
                    self.pad(tt, tt + seg + 0.4, ch, vel=0.75, gain=0.55, attack=0.25)
                    pcs = [(ch[0] + i) % 12 for i in ch[1]]
                    for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (40, 52, pcs[2], "tbn_sus"),
                                                             (50, 62, pcs[0], "tbn_sus"), (55, 67, pcs[1], "hn_sus"),
                                                             (60, 70, pcs[2], "hn_sus")]):
                        S.note(art, in_range(pc, lo, hi), tt, seg * 0.96, vel=0.72, gain=0.42, pan=-0.3 + 0.15 * lane, bus="brass",
                               attack=0.05, release=0.6)
                    self.timp(tt, ch[0], vel=0.8 if j in (0, len(prog) - 1) else 0.55)
                self.motif(t_tr, (D, MIN), art="tpt_sus", vel=0.7, gain=0.4, octave=62,
                           steps=(0, 7, 8, 7, 5, 3, 1, 0), durs=[seg / 2] * 8)
            elif mood == "awake":
                ch = AWAKE_PROG[ai % len(AWAKE_PROG)]; ai += 1
                self.pad(t_tr, t_end + 0.6, ch, vel=0.3, gain=0.25, attack=1.2)
                root = ch[0]
                pcs = [(root + i) % 12 for i in ch[1]]
                S.note("hn_sus", in_range(root, 41, 52), t_tr, t_end - t_tr, vel=0.45, gain=0.32, pan=-0.25, bus="brass", attack=0.6)
                S.note("hn_sus", in_range(root + 7, 48, 59), t_tr + 0.1, t_end - t_tr, vel=0.45, gain=0.3, pan=-0.15, bus="brass",
                       attack=0.6)
                # chorale line: clarinet and flute in thirds
                line = [pcs[0], pcs[1], pcs[2], pcs[1]]
                tt = t_tr + 0.4
                for j, pc in enumerate(line):
                    d_ = 1.1 if j < 3 else 2.4
                    S.note("cl_sus", in_range(pc, 60, 71), tt, d_, vel=0.45, gain=0.4, pan=0.1, bus="winds", attack=0.1)
                    S.note("fl_sus", in_range(pc + (4 if 4 in ch[1] else 3), 72, 83), tt, d_, vel=0.4, gain=0.3, pan=0.3,
                           bus="winds", attack=0.1)
                    tt += d_
                if has_doc:
                    self.harp_arp(t_hold + 0.3, ch, n=6, step=0.11, vel=0.4, lo=55, gain=0.4)
            elif mood == "heresy":
                wt = [D, 4, 6, 8, 10, 0]
                ch = (D, (0, 4, 8))
                self.pad(t_tr, t_end + 0.5, ch, vel=0.25, gain=0.22, bass_only=True)
                for j, pc in enumerate([4, 8, 0]):
                    S.note("vln_trem", in_range(pc, 76, 86), t_tr + 0.2 * j, t_end - t_tr, vel=0.35, gain=0.22,
                           pan=0.2 + 0.15 * j, bus="strings", attack=1.0)
                tt = t_tr + 0.6
                for j in range(8):
                    pc = wt[(5 - j) % 6]
                    S.note("glock", in_range(pc, 84, 96), tt, 1.6, vel=0.35, gain=0.2, pan=0.5 - 0.12 * j, bus="harp")
                    tt += 0.38 + 0.08 * (j % 3)
                S.note("org_quiet", in_range(8, 60, 71), t_tr, t_end - t_tr, vel=0.35, gain=0.2, bus="organ", attack=1.5)
                if big:
                    self.timp(t_tr, 8, vel=0.5)
                if has_doc:
                    self.harp_arp(t_hold + 0.2, ch, n=9, step=0.06, vel=0.35, lo=62, gain=0.35)
            elif mood == "dry":
                ch = (D, FIFTH)
                self.pad(t_tr, t_end + 0.4, ch, vel=0.2, gain=0.22, bass_only=True, attack=1.5)
                t = t_tr
                while t < t_end - 0.3:
                    S.note("cb_pizz", in_range(D, 26, 38), t, 0.4, vel=0.45, gain=0.45, pan=-0.2, bus="strings")
                    t += 1.6
                S.note("fl_sus", 69, t_tr + 0.8, 2.6, vel=0.3, gain=0.3, pan=0.3, bus="winds", attack=0.3)
                S.note("fl_sus", 64, t_tr + 3.6, 2.6, vel=0.25, gain=0.25, pan=0.3, bus="winds", attack=0.3)
                self.timp(t_tr, D, vel=0.35)
            elif mood == "final":
                # gather: tremolo and timpani roll through the flight, a chorale on the change, D major on the lamp
                self.timp(t_fly + 0.3, 9, vel=0.65, roll=t_tr - t_fly - 0.2)
                for lane, (art, m) in enumerate([("cb_trem", 33), ("vc_trem", 45), ("vla_trem", 57), ("vln_trem", 64)]):
                    S.note(art, m, t_fly, t_tr - t_fly + 0.3, vel=0.6, gain=0.35, pan=-0.3 + 0.2 * lane, bus="strings", attack=t_tr - t_fly)
                prog = [(10, MAJ), (7, MIN), (9, MAJ)]
                seg = (t_hold - t_tr) / len(prog)
                for j, ch in enumerate(prog):
                    tt = t_tr + j * seg
                    self.pad(tt, tt + seg + 0.4, ch, vel=0.7, gain=0.55, attack=0.3)
                    pcs = [(ch[0] + i) % 12 for i in ch[1]]
                    for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (43, 54, pcs[2], "tbn_sus"),
                                                             (52, 62, pcs[1], "hn_sus"), (57, 68, pcs[0], "hn_sus")]):
                        S.note(art, in_range(pc, lo, hi), tt, seg * 0.97, vel=0.7, gain=0.42, pan=-0.3 + 0.2 * lane, bus="brass", attack=0.05)
                    S.note("cl_sus", in_range(pcs[0], 64, 75), tt, seg * 0.97, vel=0.5, gain=0.3, pan=0.2, bus="winds")
                    S.note("vln_sus", in_range(pcs[2] if j < 2 else 1, 74, 86), tt, seg, vel=0.6, gain=0.3, pan=0.35, bus="strings")
                # the last lamp: D major, everyone
                ch = (D, MAJ)
                dur = t_end - t_hold + 2.0
                self.pad(t_hold, t_hold + dur, ch, vel=0.85, gain=0.6, attack=0.05)
                for lane, (lo, hi, pc, art) in enumerate([(26, 38, D, "tba_sus"), (38, 50, D, "tbn_sus"), (45, 57, 9, "tbn_sus"),
                                                         (54, 66, 6, "hn_sus"), (57, 69, 9, "hn_sus"), (62, 74, D, "tpt_sus"),
                                                         (66, 78, 6, "tpt_sus")]):
                    S.note(art, in_range(pc, lo, hi), t_hold, min(dur, 7.0), vel=0.8, gain=0.4, pan=-0.35 + 0.1 * lane, bus="brass",
                           attack=0.03, release=1.5)
                S.note("org_loud", 26, t_hold, dur + 3, vel=0.8, gain=0.45, bus="organ", release=3.0)
                S.note("org_loud", 50, t_hold, dur + 3, vel=0.8, gain=0.3, bus="organ", release=3.0)
                S.note("org_loud", 54, t_hold, dur + 3, vel=0.8, gain=0.28, bus="organ", release=3.0)
                S.note("org_loud", 57, t_hold, dur + 3, vel=0.8, gain=0.28, bus="organ", release=3.0)
                self.timp(t_hold, D, vel=0.95)
                self.timp(t_hold + 0.02, 9, vel=0.6)
                for j, n_ in enumerate([86, 90, 93, 98, 93, 90, 86]):
                    S.note("glock", n_, t_hold + 0.25 + j * 0.3, 2.5, vel=0.45, gain=0.25, pan=0.4 - 0.1 * j, bus="harp")
                self.motif(t_hold + 1.8, ch, art="tpt_sus", vel=0.75, gain=0.42, octave=62, steps=(0, 7, 9, 7, 12),
                           durs=(0.6, 0.6, 0.6, 0.6, 3.0))
            prev = ch if mood != "sleeper" else prev
        # outro: the one mycelium, held, dying away
        a, b = self.outro
        self.pad(a, b + 1.0, (D, MAJ), vel=0.4, gain=0.4, attack=1.5)
        S.note("org_quiet", 38, a, b - a + 2.0, vel=0.5, gain=0.4, bus="organ", attack=1.0, release=3.0)
        S.note("org_quiet", 54, a + 0.5, b - a, vel=0.4, gain=0.25, bus="organ", attack=1.5, release=3.0)
        self.harp_arp(a + 1.0, (D, MAJ), n=10, step=0.12, vel=0.35, lo=50, gain=0.35)
        self.motif(a + 3.5, (D, MAJ), art="hn_mute", vel=0.3, gain=0.3, steps=(0, 7, 9, 7), durs=(0.8, 0.8, 0.8, 3.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("out")
    a = ap.parse_args()
    sc = Score(a.scenario)
    sc.compose()
    sends = {"strings": 0.38, "brass": 0.32, "winds": 0.32, "perc": 0.25, "organ": 0.45, "harp": 0.5}
    for k, b in sc.s.buses.items():
        print(f"bus {k:8} rms {20 * np.log10(np.sqrt((b ** 2).mean()) + 1e-9):6.1f} dB  peak {20 * np.log10(np.abs(b).max() + 1e-9):6.1f} dB")
    mix(sc.s, sends, a.out, sc.total)
    print("written", a.out, round(sc.total, 2), "s")


if __name__ == "__main__":
    main()
