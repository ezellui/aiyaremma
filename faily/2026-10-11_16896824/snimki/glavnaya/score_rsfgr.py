#!/usr/bin/env python3
"""Score for the R.S.F.G.R. archive video, timed to the frame plan of the scenario (second version).

Every event has a mood; the mood picks the harmony, the instruments and what happens at the three moments the
picture gives: the change of borders (start of 'trans'), the document on screen (start of 'hold') and the
flight to the next event. On top of the orchestra (VSCO-2 CE) four ideas run through the whole century:

  rot        — the "madness index" grows from 0 in 1920 to 1 in 1997: every Union chord is doubled a little
               out of tune, and the doubling drifts further apart and sinks lower year by year; the awake
               stay perfectly in tune. In 1997, on the last lamp, the rot collapses into a perfect unison;
  spores     — a granular cloud cut from harp, glockenspiel, pizzicato and bubbles, on a quarter-tone
               scale, released on every change of borders; a fungal heartbeat in the bass drum under it;
  rapture    — a cheerful parade march (snare, bass drum, trumpets, glockenspiel, sleigh bells) for the
               Union's festive days, sliding a semitone and going out of tune as the years pass;
  the deep   — inhuman sounds: the Sleeper's breath (a double bass slowed two octaves), an endless falling
               Shepard glissando on the organ when the Funnel widens, sirens, scraped gongs, ring-modulated
               "buzzing" strings for the Mi-Go, Nepalese bells for Urga.

  python3 music/score_rsfgr.py scenario_rsfgr.json music/rsfgr_score.wav
  (samples: VSCO_DIR=/path/to/VSCO-2-CE, default music/VSCO-2-CE)
"""
import argparse
import glob
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))  # the renderer (history.py, render.py) one level up
from history import History  # noqa: E402
from render import FPS, build_plan  # noqa: E402

from sampler import SR, VSCO as V, Sampler, mix  # noqa: E402

MOOD = {
    "growth": ["kronstadt", "siberia", "gobi", "mycelaria", "vistula", "elbe", "danube", "regrowth"],
    "feast": ["union", "fruiting", "mekong", "amazonia"],
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

D = 2
MIN, MAJ, FIFTH = (0, 3, 7), (0, 4, 7), (0, 7)
GROWTH_PROG = [(2, MIN), (10, MAJ), (7, MIN), (9, MAJ), (5, MAJ), (0, MAJ), (2, MIN), (3, MAJ)]
AWAKE_PROG = [(0, MAJ), (7, MAJ), (9, MIN), (5, MAJ)]
REPRESS_PROG = [(7, MIN), (2, MIN), (3, MAJ), (9, (0, 3, 6))]

M1 = f"{V}/Miscellania Raw/Misc 1"
M2 = f"{V}/Miscellania Raw/Misc 2"
P1 = f"{V}/VSCO 1 Percussion"
FX = {
    "alien": sorted(glob.glob(f"{M1}/alien*.wav")),
    "bubbles": sorted(glob.glob(f"{M1}/bubbles*.wav")),
    "siren": sorted(glob.glob(f"{M1}/siren*.wav")),
    "chain": sorted(glob.glob(f"{M1}/chain*.wav")),
    "brick": sorted(glob.glob(f"{M1}/brick*.wav")),
    "glass": sorted(glob.glob(f"{M1}/glass_break*.wav")),
    "metal": sorted(glob.glob(f"{M1}/metal_hit*.wav")),
    "cymbgong": sorted(glob.glob(f"{M1}/cymbgong_weird.wav") + glob.glob(f"{M1}/cymb_gong*.wav")),
    "ambience": sorted(glob.glob(f"{M1}/ambience*.wav")),
    "timpsnare": sorted(glob.glob(f"{M1}/timp*snare*.wav")),
    "nepal": sorted(glob.glob(f"{M2}/NepaleseBells/*.wav")),
    "glock_down": sorted(glob.glob(f"{M2}/glock_glisses/*down*.wav")),
    "glock_up": sorted(glob.glob(f"{M2}/glock_glisses/*up*.wav")),
    "sleigh": sorted(glob.glob(f"{M2}/sleighbell*.wav")),
    "tamb": sorted(glob.glob(f"{M2}/tamb*.wav")),
    "gong_roll": sorted(glob.glob(f"{P1}/varMetal/Gong/gong_roll*.wav")),
    "gong_scrape": sorted(glob.glob(f"{P1}/varMetal/Gong/gong_scrape*.wav")),
    "gong_hit": sorted(glob.glob(f"{P1}/varMetal/Gong/gong_hit_f*.wav")),
    "susp_scrape": sorted(glob.glob(f"{P1}/varMetal/Cymbals/susp/susp_FX_scrape*.wav")),
    "clash": sorted(glob.glob(f"{P1}/varMetal/Cymbals/clash/*.wav")),
    "triangle": sorted(glob.glob(f"{P1}/varMetal/triangle/*/*.wav")),
    "snare": sorted(glob.glob(f"{P1}/drums/snare/drum3_marching/snare3_[fmp]*.wav")),
    "snare_soft": sorted(glob.glob(f"{P1}/drums/snare/drum3_marching/snare3_pp*.wav")),
    "bd": sorted(glob.glob(f"{P1}/drums/bass/bdrum_*.wav")),
    "bd_soft": sorted(glob.glob(f"{P1}/drums/bass/bdrum*_pp*.wav")),
    "guiro": sorted(glob.glob(f"{P1}/varWood/guiro*.wav")),
    "claves": sorted(glob.glob(f"{P1}/varWood/claves*.wav")),
}
SPORE_SRC = (sorted(glob.glob(f"{V}/Strings/Harp/*.wav")) + sorted(glob.glob(f"{V}/Percussion/Glock/*.wav"))
             + sorted(glob.glob(f"{V}/Strings/Violin Section/Pizz/*.wav"))[:12] + FX["bubbles"])
QUARTER = [x / 2 for x in range(-10, 11)]  # quarter-tone scale, ±5 semitones


def in_range(pc, lo, hi, near=None):
    cands = [m for m in range(lo, hi + 1) if m % 12 == pc % 12]
    if not cands:
        return lo
    return cands[0] if near is None else min(cands, key=lambda m: abs(m - near))


class Score:
    def __init__(self, scenario):
        self.h = History(scenario)
        self.plan = build_plan(self.h)
        self.total = len(self.plan) / FPS
        self.s = Sampler(self.total + 4)
        self.rng = random.Random(11)
        self.timeline()
        self.voices = {"cb": 38, "vc": 50, "vla": 57, "vln": 65}
        self.tdrums = [dict(hits=sorted(glob.glob(f"{V}/Percussion/Timpani/Timpani{i}_Hit_*.wav")),
                            rolls=sorted(glob.glob(f"{V}/Percussion/Timpani/Rolls/Timpani{i}_Roll_*.wav")),
                            pitch=p) for i, p in zip(range(1, 6), [29.8, 34.5, 37.3, 40.0, 42.1])]
        self.m = 0.0  # the madness index of the current event

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
            ev.setdefault(e if e is not None else ph, {})[ph] = (a / FPS, (b + 1) / FPS)
        self.ev = ev
        self.n_events = len(self.h.sc["events"])
        self.intro = ev["intro"]["intro"]
        self.outro = ev["outro"]["outro"]

    # -- helpers ------------------------------------------------------------------------------------------------
    def fx(self, kind, t, **kw):
        kw.setdefault("bus", "fx")
        self.s.sample(self.rng.choice(FX[kind]), t, **kw)

    def timp(self, t, root_pc, vel=0.7, roll=None):
        target = in_range(root_pc, 31, 42, 37)
        dr = min(self.tdrums, key=lambda d: abs(d["pitch"] - target))
        shift = max(-3, min(3, target - dr["pitch"]))
        if roll:
            self.s.sample(dr["rolls"][-1 if vel > 0.6 else 0], t, gain=0.55 * vel, pan=-0.1, bus="perc", shift=shift,
                          dur=roll)
        else:
            hits = [h for h in dr["hits"] if f"_v{4 if vel > 0.75 else 3 if vel > 0.45 else 1}_" in h] or dr["hits"]
            self.s.sample(self.rng.choice(hits), t, gain=0.7 * vel, pan=-0.1, bus="perc", shift=shift)

    def rot(self):
        """(detune of the double in semitones, downward drift over a chord) for the current madness index"""
        return 0.05 + 0.32 * self.m, -0.06 - 0.45 * self.m

    def pad(self, t0, t1, chord, vel=0.5, arts=("cb_sus", "vc_sus", "vla_sus", "vln_sus"), gain=0.5, attack=0.8,
            bass_only=False, rotten=True):
        root, iv = chord
        pcs = [(root + i) % 12 for i in iv]
        lanes = [("cb", 28, 41, root % 12, arts[0], -0.35),
                 ("vc", 40, 55, pcs[-1] if len(pcs) > 2 else root, arts[1], -0.15),
                 ("vla", 52, 64, pcs[1] if len(pcs) > 2 else pcs[-1], arts[2], 0.15),
                 ("vln", 62, 76, pcs[0] if len(pcs) > 2 else pcs[-1], arts[3], 0.35)]
        if bass_only:
            lanes = lanes[:2]
        dur = t1 - t0
        det, drift = self.rot() if rotten else (0.0, 0.0)
        for lane, lo, hi, pc, art, pan in lanes:
            m = in_range(pc, lo, hi, self.voices[lane])
            self.voices[lane] = m
            self.s.note(art, m, t0, dur, vel=vel, gain=gain, pan=pan, bus="strings", attack=attack, release=1.4,
                        bend=drift * 0.5)
            if rotten and det > 0.06:  # the double, out of tune, sinking further
                self.s.note(art, m, t0 + 0.05, dur, vel=vel * 0.9, gain=gain * (0.35 + 0.4 * self.m), pan=-pan,
                            bus="strings", attack=attack * 1.3, release=1.4, detune=det, bend=drift)

    def motif(self, t, chord, art="hn_sus", vel=0.6, gain=0.55, octave=None, steps=(0, 7, 8, 7),
              durs=(0.55, 0.55, 0.55, 1.6), bus="brass", rotten=True):
        root, iv = chord
        base = in_range(root, 50, 61, 55) if octave is None else in_range(root, octave, octave + 11)
        st = [9 if (x == 8 and 4 in iv) else x for x in steps]
        det, drift = self.rot() if rotten else (0.0, 0.0)
        tt = t
        for s_, d_ in zip(st, durs):
            self.s.note(art, base + s_, tt, d_ * 0.95, vel=vel, gain=gain, pan=-0.2, bus=bus, release=0.5,
                        bend=drift * 0.6 if d_ > 1.0 else 0.0)
            if rotten and det > 0.12:
                self.s.note(art, base + s_, tt + 0.03, d_ * 0.95, vel=vel * 0.8, gain=gain * 0.5 * self.m, pan=0.25,
                            bus=bus, release=0.5, detune=det)
            tt += d_

    def harp_arp(self, t, chord, n=7, step=0.085, vel=0.5, lo=50, gain=0.5, art="harp"):
        root, iv = chord
        notes, m = [], in_range(root, lo, lo + 11)
        while len(notes) < n:
            for i in iv:
                if len(notes) < n:
                    notes.append(m + i)
            m += 12
        for k, nt in enumerate(notes):
            self.s.note(art, nt, t + k * step, 2.5, vel=vel, gain=gain, pan=0.3, bus="harp", release=1.5)

    def spores(self, t, dur, density=30, gain=0.22):
        """the release of spores: a dense burst thinning out"""
        self.s.grains(SPORE_SRC, t, t + dur, density, gain=gain, bus="spores", pitch=QUARTER,
                      curve=lambda x: (1 - x) ** 2 + 0.05)

    def heartbeat(self, t0, t1, gain=0.35):
        """the mycelium's pulse: a soft bass drum, long-short, irregular"""
        t, k = t0, 0
        while t < t1:
            self.fx("bd_soft", t, gain=gain, pan=0.0, bus="perc")
            self.fx("bd_soft", t + 0.28, gain=gain * 0.6, pan=0.0, bus="perc")
            t += [1.9, 2.3, 1.7, 2.6][k % 4]
            k += 1

    def breath(self, t, dur, gain=0.5):
        """the Sleeper breathes: a double bass two octaves too low, swelling and sinking"""
        self.s.note("cb_sus", 14, t, dur, vel=0.7, gain=gain, pan=-0.1, bus="deep", attack=dur * 0.45,
                    release=2.5, bend=-2.0)
        self.s.note("tba_sus", 17, t + 0.4, dur * 0.8, vel=0.6, gain=gain * 0.6, pan=0.15, bus="deep",
                    attack=dur * 0.4, release=2.0, bend=-1.5, detune=0.3)

    def shepard(self, t0, t1, up=False, gain=0.35, period=7.0):
        """an endless glissando on the organ: overlapping voices gliding three octaves each"""
        t = t0 - period * 0.6
        k = 0
        while t < t1:
            start = 48 if up else 84
            span = 36 if up else -36
            st = max(t, t0)
            cut = st - t
            dur = period * 3 - cut
            if dur > 1:
                self.s.note("org_quiet", start + span * (cut / (period * 3)), st, min(dur, t1 - st + 1.5),
                            vel=0.5, gain=gain, pan=-0.4 + 0.27 * (k % 4), bus="deep",
                            attack=min(period * 1.2, dur * 0.4), release=2.0, bend=span * (1 - cut / (period * 3)))
            t += period
            k += 1

    def buzz(self, t, dur, notes=(76, 80, 84), gain=0.25):
        """the Mi-Go: tremolo violins through a ring modulator — a swarm, not a section"""
        for j, n_ in enumerate(notes):
            self.s.note("vln_trem", n_, t + 0.15 * j, dur, vel=0.5, gain=gain, pan=-0.5 + 0.5 * j, bus="buzz",
                        attack=0.8, release=1.0, ringmod=[53.0, 61.0, 71.0][j % 3], detune=0.25 * (j - 1))

    def march(self, t0, t1, key=10, bpm=116, gain=0.45, sour=0.0, detune=0.0):
        """the parade: a cheerful march in major; 'sour' slides it down a semitone every two bars,
        'detune' puts the second trumpet out of tune"""
        beat = 60.0 / bpm
        tune = [(7, 1), (12, 1), (16, 1), (19, 1), (21, 1.5), (19, .5), (16, 1), (12, 2), (14, 1), (16, 1), (17, 1),
                (14, 1), (19, 3), (None, 1),
                (7, 1), (12, 1), (16, 1), (19, 1), (24, 1.5), (23, .5), (21, 1), (19, 2), (17, 1), (16, 1), (14, 1),
                (11, 1), (12, 3), (None, 1)]
        bass = [0, 7, 0, 7, 5, 0, 7, 7]
        t, bar, slide = t0, 0, 0.0
        while t < t1 - beat:
            for n_, d_ in tune:
                if t >= t1 - beat:
                    break
                if n_ is not None:
                    base = in_range(key, 55, 66) + n_ - 12 - slide
                    self.s.note("tpt_sus", base, t, d_ * beat * 0.9, vel=0.62, gain=gain * 0.75, pan=-0.15,
                                bus="parade", release=0.25)
                    if detune:
                        self.s.note("tpt_sus", base, t + 0.02, d_ * beat * 0.9, vel=0.55, gain=gain * 0.45, pan=0.2,
                                    bus="parade", release=0.25, detune=detune)
                    self.s.note("glock", in_range(n_ + key, 79, 96) - slide, t, 0.6, vel=0.5, gain=gain * 0.35,
                                pan=0.4, bus="harp")
                t += d_ * beat
            bar += 1
            if sour:
                slide += sour
        # percussion: bass drum on 1 and 3, snare on 2 and 4 with a flam, sleigh bells on the offbeats
        t, k = t0, 0
        while t < t1 - beat * 0.5:
            pos = k % 4
            if pos in (0, 2):
                self.fx("bd", t, gain=gain * 0.55, bus="perc")
                root = in_range(key + bass[(k // 2) % 8], 33, 45)
                self.s.note("tba_sus", root, t, beat * 0.8, vel=0.55, gain=gain * 0.6, pan=-0.3, bus="parade",
                            release=0.2)
            else:
                self.fx("snare", t, gain=gain * 0.45, pan=0.1, bus="perc")
                self.s.note("hn_sus", in_range(key + 4, 55, 66), t, beat * 0.5, vel=0.45, gain=gain * 0.35, pan=0.25,
                            bus="parade", release=0.15)
                self.s.note("hn_sus", in_range(key + 7, 55, 66), t, beat * 0.5, vel=0.45, gain=gain * 0.3, pan=0.3,
                            bus="parade", release=0.15)
            self.fx("sleigh", t + beat / 2, gain=gain * 0.18, pan=0.5, bus="perc", dur=0.3)
            t += beat
            k += 1

    def lullaby(self, t, gain=0.4):
        """Lenin's lullaby on the flute, each note sinking as it is held"""
        tt = t
        for n_, d_ in [(77, 1.0), (74, 0.8), (72, 0.8), (69, 2.2)]:
            self.s.note("fl_sus", n_, tt, d_, vel=0.4, gain=gain, pan=0.25, bus="winds", attack=0.15,
                        bend=-0.4 * self.m - 0.1)
            self.s.note("fl_sus", n_, tt + 0.04, d_, vel=0.35, gain=gain * 0.5, pan=-0.25, bus="winds", attack=0.15,
                        detune=0.15 + 0.3 * self.m, bend=-0.6 * self.m - 0.15)
            tt += d_

    # -- the piece ----------------------------------------------------------------------------------------------
    def compose(self):
        S = self.s
        a, _ = self.intro
        b = self.ev[1]["trans"][0] + 0.3
        S.note("org_quiet", 38, a, b - a + 1.0, vel=0.5, gain=0.4, bus="organ", attack=1.5, release=2.0)
        S.note("cb_trem", 38, a + 0.5, b - a, vel=0.4, gain=0.35, pan=-0.3, bus="strings", attack=2.5)
        self.breath(a, b - a + 1.0, gain=0.45)
        self.fx("alien", a + 1.0, gain=0.25, shift=-5, bus="deep", attack=1.0)
        self.fx("glock_down", a + 2.5, gain=0.25, shift=-3, bus="harp")
        self.motif(a + 3.0, (D, MIN), art="hn_mute", vel=0.35, gain=0.35, rotten=False)
        self.heartbeat(a + 4.0, self.ev[2]["trans"][0], gain=0.3)
        gi = ai = ri = 0
        for k in range(1, self.n_events + 1):
            e = self.h.sc["events"][k - 1]
            eid = e.get("id")
            mood = MOOD_OF.get(eid, "growth")
            self.m = max(0.0, min(1.0, (e["year"] - 1920) / 77.0))
            ph = self.ev[k]
            t_fly, t_tr, t_hold = ph["fly"][0], ph["trans"][0], ph["hold"][0]
            t_end = self.ev[k + 1]["trans"][0] + 0.3 if k < self.n_events else self.outro[0] + 0.5
            has_doc = bool(e.get("docs"))
            big = bool(e.get("ops"))
            vortex = bool(e.get("vortex_radius_km"))

            if mood in ("growth", "feast"):
                ch = GROWTH_PROG[gi % len(GROWTH_PROG)]
                gi += 1
                self.pad(t_tr, t_end + 0.6, ch, vel=0.5, gain=0.45)
                self.motif(t_tr, ch, art="hn_sus" if gi % 2 else "tbn_sus", vel=0.62)
                self.timp(t_tr, ch[0], vel=0.75)
                S.note("tba_sus", in_range(ch[0], 29, 40), t_tr, 2.2, vel=0.5, gain=0.4, bus="brass", release=0.8)
                self.spores(t_tr + 0.05, 4.0, density=28 + 25 * self.m, gain=0.2)
                self.heartbeat(t_tr + 1.0, t_end, gain=0.25)
                if mood == "feast":
                    key = [10, 3, 5, 0][gi % 4]
                    self.fx("clash", t_hold, gain=0.3, pan=0.3, bus="perc")
                    self.march(t_hold + 0.1, t_end, key=key, gain=0.42, sour=0.25 * self.m, detune=0.12 + 0.35 * self.m)
                elif has_doc:
                    self.harp_arp(t_hold + 0.2, ch, vel=0.45, gain=0.45)
            elif mood == "lamp":
                ch = (5, MAJ)
                self.pad(t_tr, t_end + 0.6, ch, vel=0.4, gain=0.38)
                S.note("org_quiet", in_range(ch[0], 41, 52), t_tr, t_end - t_tr + 0.5, vel=0.4, gain=0.3, bus="organ",
                       attack=1.0)
                for j in range(14):  # lamps lighting one by one, each a little out of tune
                    S.note("glock", in_range([0, 4, 7, 9][j % 4] + 5, 79, 96), t_tr + 0.2 + j * 0.37, 1.5, vel=0.45,
                           gain=0.28, pan=-0.7 + 0.1 * j, bus="harp", detune=self.rng.uniform(-0.3, 0.3))
                self.s.grains(FX["glass"], t_tr + 0.5, t_hold + 1.5, 12, gain=0.06, bus="spores", pitch=[12, 17, 19, 24])
                self.march(t_hold + 0.2, t_end, key=5, bpm=104, gain=0.36, sour=0.0, detune=0.45)
            elif mood == "sleeper":
                dur = t_end - t_fly + 0.4
                S.note("org_loud" if vortex else "org_quiet", 26, t_fly, dur, vel=0.6, gain=0.45, bus="organ",
                       attack=1.2, release=2.2, bend=-0.3 * self.m)
                S.note("cb_trem", 38, t_fly + 0.2, dur, vel=0.6, gain=0.5, pan=-0.3, bus="strings", attack=1.6)
                S.note("vc_trem", 51, t_tr, t_end - t_tr + 0.6, vel=0.45, gain=0.3, pan=-0.05, bus="strings", attack=1.2,
                       bend=-0.5 * self.m)
                S.note("vla_trem", 52, t_tr + 0.3, t_end - t_tr + 0.4, vel=0.35, gain=0.22, pan=0.2, bus="strings",
                       attack=1.5, detune=0.3 * self.m)
                self.breath(t_fly + 0.3, min(7.0, dur), gain=0.5)
                self.fx("alien", t_tr + 0.4, gain=0.22, shift=-7 + 2 * (k % 3), pan=0.3, bus="deep", attack=0.6)
                if vortex:
                    self.shepard(t_tr - 0.5, t_end, gain=0.3)
                    self.timp(t_tr, D, vel=0.85, roll=t_hold - t_tr + 0.4)
                    self.fx("gong_roll", t_tr - 0.3, gain=0.35, bus="perc", shift=-5, dur=t_hold - t_tr + 2.0)
                    S.note("tba_sus", 26, t_tr + 0.2, 3.0, vel=0.7, gain=0.45, bus="brass", bend=-1.0)
                    S.note("tbn_sus", 39, t_tr + 0.4, 2.6, vel=0.6, gain=0.35, bus="brass", bend=-1.5)
                if eid == "alarm":
                    for j in range(3):
                        self.fx("siren", t_tr + 0.3 + 1.6 * j, gain=0.22, pan=-0.6 + 0.6 * j, shift=-2 * j, bus="fx")
                if eid == "kara":
                    self.fx("bubbles", t_tr + 0.6, gain=0.4, shift=-9, bus="deep")
                    self.fx("bubbles", t_hold + 0.5, gain=0.3, shift=-12, bus="deep")
                if eid == "chamber":
                    self.fx("brick", t_tr, gain=0.35, pan=-0.2, bus="fx")
                if eid == "cylinder":
                    S.note("org_quiet", 62, t_tr - 2.0, 2.2, vel=0.5, gain=0.3, bus="organ", reverse=True)
                    self.fx("gong_scrape", t_hold + 0.4, gain=0.3, bus="fx")
                if eid == "protocol":
                    self.fx("chain", t_tr, gain=0.3, pan=0.3, bus="fx", dur=3.0)
                    self.fx("timpsnare", t_hold, gain=0.45, bus="perc")
                if eid in ("lenin_sleeps", "sprouted", "chamber"):
                    self.lullaby(t_hold + 0.4)
                if eid == "sprouted":  # the voice in the lamps: a trombone wavering without words
                    tt = t_hold + 1.0
                    for j, d_ in enumerate([0.9, 0.5, 1.4, 0.7, 1.8]):
                        S.note("tbn_sus", [45, 46, 44, 45, 43][j], tt, d_, vel=0.4, gain=0.3, pan=-0.3, bus="brass",
                               bend=self.rng.uniform(-0.8, 0.5), attack=0.1)
                        tt += d_ + [0.4, 1.1, 0.4, 4.0][j % 4] * 0.3
                    self.spores(t_tr, 5.0, density=18, gain=0.16)
                if has_doc:
                    S.note("glock", 86, t_hold + 0.2, 2.0, vel=0.3, gain=0.18, pan=0.4, bus="harp", detune=-0.3)
                    S.note("glock", 87, t_hold + 1.4, 2.0, vel=0.25, gain=0.15, pan=0.4, bus="harp", detune=0.2)
            elif mood == "repress":
                ch = REPRESS_PROG[ri % len(REPRESS_PROG)]
                ri += 1
                self.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.32, bass_only=True)
                root = in_range(ch[0], 43, 54)
                pat = [0, 7, 12, 7, 3 if 3 in ch[1] else 4]  # five to the bar: the step that is one too many
                beat = 60 / 132 / 2
                t, j = t_tr, 0
                while t < t_end - 0.1:
                    S.note("vc_pizz" if j % 10 < 5 else "vla_pizz", root + pat[j % 5], t, 0.25,
                           vel=0.55 if j % 5 == 0 else 0.35, gain=0.42, pan=-0.1 if j % 2 else 0.1, bus="strings",
                           release=0.3)
                    if j % 5 == 0:
                        self.fx("claves", t, gain=0.12, pan=0.5, bus="perc")
                    t += beat
                    j += 1
                S.note("tpt_mute", in_range(ch[0] + 1, 62, 73), t_tr, 0.9, vel=0.55, gain=0.3, pan=0.25, bus="brass")
                S.note("bsn_sus", in_range(ch[0], 34, 45), t_tr, t_end - t_tr, vel=0.4, gain=0.3, pan=0.1, bus="winds",
                       attack=0.4, bend=-0.3)
                self.fx("metal", t_tr, gain=0.25, pan=-0.4, bus="fx")
                if eid in ("case1147", "case427"):
                    self.fx("chain", t_tr + 0.5, gain=0.22, pan=0.4, bus="fx", dur=4.0)
                if eid == "case611":
                    self.fx("guiro", t_hold, gain=0.3, bus="fx")
                if has_doc:
                    self.fx("timpsnare", t_hold, gain=0.4, bus="perc")
                    self.fx("susp_scrape", t_hold + 0.5, gain=0.18, bus="fx", dur=3.0)
            elif mood == "school":
                ch = (5, MAJ)
                self.pad(t_tr, t_end + 0.5, ch, vel=0.3, gain=0.28)
                tune = [77, 77, 84, 84, 86, 86, 84, 82, 82, 81, 81, 79, 79, 77]  # the alphabet song, in F
                for j, n_ in enumerate(tune):  # a music box running down: slower, flatter
                    tt = t_tr + sum(0.38 + 0.025 * i for i in range(j))
                    S.note("glock", n_ + 12 if n_ + 12 <= 96 else n_, tt, 0.7, vel=0.4, gain=0.3, pan=0.3, bus="harp",
                           detune=-0.04 * j)
                    S.note("vln_pizz", n_ - 12, tt, 0.3, vel=0.35, gain=0.3, pan=-0.2, bus="strings", detune=-0.03 * j)
                S.note("cl_sus", 64, t_end - 2.5, 2.4, vel=0.3, gain=0.25, bus="winds", bend=-0.6)
            elif mood == "hymn":
                prog = [(D, MIN), (10, MAJ), (7, MIN), (9, MAJ), (D, MIN)]
                seg = (t_end - t_tr) / len(prog)
                self.fx("snare", t_tr - 0.25, gain=0.35, bus="perc")
                for j, ch in enumerate(prog):
                    tt = t_tr + j * seg
                    self.pad(tt, tt + seg + 0.4, ch, vel=0.75, gain=0.55, attack=0.25)
                    pcs = [(ch[0] + i) % 12 for i in ch[1]]
                    for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (40, 52, pcs[2], "tbn_sus"),
                                                             (50, 62, pcs[0], "tbn_sus"), (55, 67, pcs[1], "hn_sus"),
                                                             (60, 70, pcs[2], "hn_sus")]):
                        S.note(art, in_range(pc, lo, hi), tt, seg * 0.96, vel=0.72, gain=0.42, pan=-0.3 + 0.15 * lane,
                               bus="brass", attack=0.05, release=0.6)
                    self.timp(tt, ch[0], vel=0.8 if j in (0, len(prog) - 1) else 0.55)
                self.motif(t_tr, (D, MIN), art="tpt_sus", vel=0.7, gain=0.4, octave=62,
                           steps=(0, 7, 8, 7, 5, 3, 1, 0), durs=[seg / 2] * 8)
                self.fx("clash", t_end - seg, gain=0.35, bus="perc")
                self.spores(t_end - seg, 4.0, density=35, gain=0.2)
            elif mood == "awake":
                ch = AWAKE_PROG[ai % len(AWAKE_PROG)]
                ai += 1
                self.pad(t_tr, t_end + 0.6, ch, vel=0.3, gain=0.25, attack=1.2, rotten=False)
                root = ch[0]
                pcs = [(root + i) % 12 for i in ch[1]]
                S.note("hn_sus", in_range(root, 41, 52), t_tr, t_end - t_tr, vel=0.45, gain=0.32, pan=-0.25,
                       bus="brass", attack=0.6)
                S.note("hn_sus", in_range(root + 7, 48, 59), t_tr + 0.1, t_end - t_tr, vel=0.45, gain=0.3, pan=-0.15,
                       bus="brass", attack=0.6)
                tt = t_tr + 0.4
                for j, pc in enumerate([pcs[0], pcs[1], pcs[2], pcs[1]]):
                    d_ = 1.1 if j < 3 else 2.4
                    S.note("cl_sus", in_range(pc, 60, 71), tt, d_, vel=0.45, gain=0.4, pan=0.1, bus="winds", attack=0.1)
                    S.note("fl_sus", in_range(pc + (4 if 4 in ch[1] else 3), 72, 83), tt, d_, vel=0.4, gain=0.3,
                           pan=0.3, bus="winds", attack=0.1)
                    tt += d_
                # reason keeps time: a steady metronome on the claves, and a clean triangle
                t, j = t_tr, 0
                while t < t_end - 0.2:
                    self.fx("claves", t, gain=0.1 if j % 4 else 0.16, pan=0.5, bus="perc")
                    t += 0.6
                    j += 1
                self.fx("triangle", t_tr, gain=0.25, pan=0.4, bus="perc")
                if eid in ("budapest", "pannonia", "bohemia"):  # the spell breaks
                    self.fx("glass", t_tr - 0.05, gain=0.35, pan=0.2, bus="fx")
                if has_doc:
                    self.harp_arp(t_hold + 0.3, ch, n=6, step=0.11, vel=0.4, lo=55, gain=0.4)
            elif mood == "heresy":
                wt = [D, 4, 6, 8, 10, 0]
                ch = (D, (0, 4, 8))
                self.pad(t_tr, t_end + 0.5, ch, vel=0.35, gain=0.35, bass_only=True)
                self.buzz(t_tr, t_end - t_tr, gain=0.28)
                for j in range(2):
                    self.fx("alien", t_tr + 0.3 + 2.5 * j, gain=0.25, shift=3 - 4 * j, pan=-0.5 + j, bus="deep")
                if eid in ("urga", "altai"):
                    for j in range(4):
                        self.fx("nepal", t_tr + 0.4 + 1.3 * j, gain=0.3, pan=0.4 - 0.25 * j, bus="harp")
                tt = t_tr + 0.6
                for j in range(8):
                    S.note("glock", in_range(wt[(5 - j) % 6], 84, 96), tt, 1.6, vel=0.45, gain=0.3, pan=0.5 - 0.12 * j,
                           bus="harp", detune=0.5 if j % 2 else 0.0)
                    tt += 0.38 + 0.08 * (j % 3)
                if eid == "exodus":  # the flight: a reversed swell and a glissando upward
                    S.note("org_quiet", 74, t_tr - 2.2, 2.3, vel=0.5, gain=0.3, bus="organ", reverse=True)
                    self.fx("glock_up", t_hold, gain=0.3, bus="harp")
                    self.shepard(t_hold, t_end, up=True, gain=0.2, period=5.0)
                if big:
                    self.timp(t_tr, 8, vel=0.5)
                if has_doc:
                    self.harp_arp(t_hold + 0.2, ch, n=9, step=0.06, vel=0.35, lo=62, gain=0.35)
            elif mood == "dry":
                ch = (D, FIFTH)
                self.pad(t_tr, t_end + 0.4, ch, vel=0.3, gain=0.42, bass_only=True, attack=1.5, rotten=False)
                t = t_tr
                while t < t_end - 0.3:
                    S.note("cb_pizz", in_range(D, 26, 38), t, 0.4, vel=0.6, gain=0.7, pan=-0.2, bus="strings")
                    t += 1.6
                self.fx("guiro", t_tr + 0.2, gain=0.25, pan=0.3, bus="fx")
                self.fx("ambience", t_tr, gain=0.25, bus="deep", dur=t_end - t_tr, attack=1.5)
                S.note("fl_sus", 69, t_tr + 0.8, 2.6, vel=0.3, gain=0.3, pan=0.3, bus="winds", attack=0.3)
                S.note("fl_sus", 64, t_tr + 3.6, 2.6, vel=0.25, gain=0.25, pan=0.3, bus="winds", attack=0.3)
                if eid == "salt":  # salt crystals: high glass grains
                    self.s.grains(FX["glass"], t_tr + 0.3, t_end - 0.5, 9, gain=0.07, bus="spores",
                                  pitch=[12, 14, 17, 19, 24])
                if eid == "dry":
                    self.fx("brick", t_hold, gain=0.25, bus="fx")
                self.timp(t_tr, D, vel=0.35)
            elif mood == "final":
                # gather: a rising endless glissando, snare and timpani rolls, a cymbal scraped to the breaking point
                self.shepard(t_fly, t_tr + 0.5, up=True, gain=0.35, period=3.5)
                self.timp(t_fly + 0.3, 9, vel=0.7, roll=t_tr - t_fly - 0.2)
                self.fx("susp_scrape", t_fly, gain=0.25, bus="fx", dur=t_tr - t_fly)
                for lane, (art, m) in enumerate([("cb_trem", 33), ("vc_trem", 45), ("vla_trem", 57), ("vln_trem", 64)]):
                    S.note(art, m, t_fly, t_tr - t_fly + 0.3, vel=0.6, gain=0.35, pan=-0.3 + 0.2 * lane, bus="strings",
                           attack=t_tr - t_fly)
                    S.note(art, m, t_fly, t_tr - t_fly + 0.3, vel=0.6, gain=0.25, pan=0.3 - 0.2 * lane, bus="strings",
                           attack=t_tr - t_fly, detune=0.4)
                prog = [(10, MAJ), (7, MIN), (9, MAJ)]
                seg = (t_hold - t_tr) / len(prog)
                for j, ch in enumerate(prog):  # the chorale at its most out of tune
                    tt = t_tr + j * seg
                    self.pad(tt, tt + seg + 0.4, ch, vel=0.7, gain=0.55, attack=0.3)
                    pcs = [(ch[0] + i) % 12 for i in ch[1]]
                    for lane, (lo, hi, pc, art) in enumerate([(29, 40, ch[0], "tba_sus"), (43, 54, pcs[2], "tbn_sus"),
                                                             (52, 62, pcs[1], "hn_sus"), (57, 68, pcs[0], "hn_sus")]):
                        S.note(art, in_range(pc, lo, hi), tt, seg * 0.97, vel=0.7, gain=0.42, pan=-0.3 + 0.2 * lane,
                               bus="brass", attack=0.05)
                        S.note(art, in_range(pc, lo, hi), tt, seg * 0.97, vel=0.6, gain=0.3, pan=0.3 - 0.2 * lane,
                               bus="brass", attack=0.05, detune=0.45, bend=-0.4)
                # the last lamp: D major, everyone — and for the first time in the century, perfectly in tune
                self.m = 0.0
                ch = (D, MAJ)
                dur = t_end - t_hold + 2.0
                self.pad(t_hold, t_hold + dur, ch, vel=0.85, gain=0.6, attack=0.05, rotten=False)
                for lane, (lo, hi, pc, art) in enumerate([(26, 38, D, "tba_sus"), (38, 50, D, "tbn_sus"),
                                                         (45, 57, 9, "tbn_sus"), (54, 66, 6, "hn_sus"),
                                                         (57, 69, 9, "hn_sus"), (62, 74, D, "tpt_sus"),
                                                         (66, 78, 6, "tpt_sus")]):
                    S.note(art, in_range(pc, lo, hi), t_hold, min(dur, 7.0), vel=0.8, gain=0.4, pan=-0.35 + 0.1 * lane,
                           bus="brass", attack=0.03, release=1.5)
                for n_, g_ in [(26, 0.45), (50, 0.3), (54, 0.28), (57, 0.28)]:
                    S.note("org_loud", n_, t_hold, dur + 3, vel=0.8, gain=g_, bus="organ", release=3.0)
                self.timp(t_hold, D, vel=0.95)
                self.timp(t_hold + 0.02, 9, vel=0.6)
                self.fx("gong_hit", t_hold, gain=0.45, bus="perc")
                self.fx("clash", t_hold, gain=0.4, bus="perc")
                for j, n_ in enumerate([86, 90, 93, 98, 93, 90, 86]):
                    S.note("glock", n_, t_hold + 0.25 + j * 0.3, 2.5, vel=0.45, gain=0.25, pan=0.4 - 0.1 * j, bus="harp")
                self.spores(t_hold + 0.1, 6.0, density=60, gain=0.18)
                self.march(t_hold + 2.0, t_end, key=D, bpm=120, gain=0.4, sour=0.0, detune=0.0)
        # outro: the one mycelium, held, dying away; the heartbeat goes on, slower
        a, b = self.outro
        self.m = 0.0
        self.pad(a, b + 1.0, (D, MAJ), vel=0.4, gain=0.4, attack=1.5, rotten=False)
        S.note("org_quiet", 38, a, b - a + 2.0, vel=0.5, gain=0.4, bus="organ", attack=1.0, release=3.0)
        S.note("org_quiet", 54, a + 0.5, b - a, vel=0.4, gain=0.25, bus="organ", attack=1.5, release=3.0)
        self.harp_arp(a + 1.0, (D, MAJ), n=10, step=0.12, vel=0.35, lo=50, gain=0.35)
        self.motif(a + 3.5, (D, MAJ), art="hn_mute", vel=0.3, gain=0.3, steps=(0, 7, 9, 7), durs=(0.8, 0.8, 0.8, 3.5),
                   rotten=False)
        self.heartbeat(a + 1.0, b - 1.0, gain=0.22)
        self.fx("alien", a + 4.0, gain=0.12, shift=-9, bus="deep", attack=2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("out")
    a = ap.parse_args()
    sc = Score(a.scenario)
    sc.compose()
    sends = {"strings": 0.38, "brass": 0.32, "winds": 0.32, "perc": 0.25, "organ": 0.45, "harp": 0.5,
             "fx": 0.45, "deep": 0.7, "spores": 0.55, "buzz": 0.5, "parade": 0.22}
    gains = {"strings": 0.0, "brass": 1.0, "winds": 7.0, "perc": 2.0, "organ": 0.0, "harp": 9.0,
             "fx": 2.0, "deep": 3.0, "spores": 4.0, "buzz": 0.0, "parade": 1.0}
    for k, b in sc.s.buses.items():
        g = gains.get(k, 0.0)
        print(f"bus {k:8} rms {20 * np.log10(np.sqrt((b ** 2).mean()) + 1e-9) + g:6.1f} dB  "
              f"peak {20 * np.log10(np.abs(b).max() + 1e-9) + g:6.1f} dB")
    mix(sc.s, sends, a.out, sc.total, gains=gains)
    print("written", a.out, round(sc.total, 2), "s")


if __name__ == "__main__":
    main()
