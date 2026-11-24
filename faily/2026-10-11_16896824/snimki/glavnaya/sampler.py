"""A small offline sampler over the VSCO-2 CE samples (index.json from index_samples.py).

Notes are placed on stereo buses (float32, 44.1 kHz); each bus has its own reverb send.
Pitch is reached from the nearest recorded note by resampling (at most a few semitones away).
"""
import json
import os
import random

import numpy as np
import soundfile as sf
from scipy.signal import oaconvolve, butter, sosfilt

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))


class Sampler:
    def __init__(self, seconds, seed=7):
        self.idx = json.load(open(os.path.join(HERE, "index.json")))
        self.n = int(seconds * SR) + SR * 12
        self.buses = {}
        self.cache = {}
        self.rng = random.Random(seed)

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((self.n, 2), np.float32)
        return self.buses[name]

    def _load(self, path):
        if path not in self.cache:
            d, sr = sf.read(path, always_2d=True, dtype="float32")
            if d.shape[1] == 1:
                d = np.repeat(d, 2, 1)
            if sr != SR:
                t = np.arange(0, len(d), sr / SR)
                d = np.stack([np.interp(t, np.arange(len(d)), d[:, c]) for c in range(2)], 1).astype(np.float32)
            # trim leading silence (keeps the attack on the beat)
            env = np.abs(d).max(1)
            k = int(np.argmax(env > env.max() * 0.02))
            self.cache[path] = d[max(0, k - 64):]
        return self.cache[path]

    def pick(self, art, midi, vel):
        rows = self.idx[art]
        best = min(abs(r["note"] - midi) for r in rows)
        near = [r for r in rows if abs(r["note"] - midi) == best]
        vels = sorted({r["vel"] for r in near})
        want = vels[min(len(vels) - 1, int(round(vel * (len(vels) - 1))))]
        cand = [r for r in near if r["vel"] == want]
        return self.rng.choice(cand)

    def note(self, art, midi, t, dur, vel=0.6, gain=1.0, pan=0.0, bus="main", attack=0.0, release=0.6,
             detune=0.0):
        r = self.pick(art, midi, vel)
        d = self._load(r["path"])
        ratio = 2 ** ((midi - r["note"] + detune) / 12.0)
        need = int((dur + release) * SR * ratio) + 8
        if need > len(d):  # long note: crossfaded repeats of the body of the sample
            body0, xf = int(0.35 * len(d)), int(0.6 * SR)
            parts = [d]
            total = len(d)
            while total < need:
                seg = d[body0:].copy()
                parts.append(seg)
                total += len(seg) - xf
            out = parts[0]
            for seg in parts[1:]:
                w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
                out = np.concatenate([out[:-xf], out[-xf:] * (1 - w) + seg[:xf] * w, seg[xf:]])
            d = out
        src = d[:need]
        n_out = int(len(src) / ratio)
        pos = np.arange(n_out) * ratio
        y = np.stack([np.interp(pos, np.arange(len(src)), src[:, c]) for c in range(2)], 1).astype(np.float32)
        # envelope
        env = np.ones(n_out, np.float32)
        a = int(attack * SR)
        if a > 1:
            env[:a] = np.linspace(0, 1, a) ** 1.5
        k = int(dur * SR)
        rl = max(1, int(release * SR))
        if k < n_out:
            tail = np.exp(-np.linspace(0, 6, n_out - k)).astype(np.float32)
            env[k:] = tail
        y *= env[:, None]
        g = gain * (0.35 + 0.65 * vel)
        lp, rp = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        y[:, 0] *= g * lp * 1.414
        y[:, 1] *= g * rp * 1.414
        s = int(t * SR)
        b = self.bus(bus)
        e = min(len(b), s + len(y))
        if e > s >= 0:
            b[s:e] += y[:e - s]

    def chord(self, art, notes, t, dur, **kw):
        for i, m in enumerate(notes):
            self.note(art, m, t + 0.012 * i, dur, **kw)


def make_ir(seconds=3.2, seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)).astype(np.float32)
    ir *= np.exp(-6.9 * t / seconds)[:, None]
    sos = butter(2, 4200, "low", fs=SR, output="sos")
    ir = sosfilt(sos, ir, axis=0)
    pre = int(0.022 * SR)
    ir = np.concatenate([np.zeros((pre, 2), np.float32), ir])
    return (ir / np.sqrt((ir ** 2).sum(0))).astype(np.float32)


def mix(sampler, sends, out_path, total_seconds, master_gain_db=-1.0):
    ir = make_ir()
    n = int(total_seconds * SR)
    dry = np.zeros((sampler.n, 2), np.float32)
    wet_in = np.zeros((sampler.n, 2), np.float32)
    for name, b in sampler.buses.items():
        s = sends.get(name, 0.3)
        dry += b * (1 - 0.35 * s)
        wet_in += b * s
    wet = np.stack([oaconvolve(wet_in[:, c], ir[:, c])[:sampler.n] for c in range(2)], 1)
    y = dry + 0.9 * wet
    y = y[:n]
    # gentle bus compression (slow RMS levelling) and peak normalisation
    peak = np.abs(y).max() + 1e-9
    y = y / peak * (10 ** (master_gain_db / 20))
    fade = int(3 * SR)
    y[-fade:] *= np.linspace(1, 0, fade)[:, None]
    sf.write(out_path, y, SR, subtype="PCM_24")
    return y
