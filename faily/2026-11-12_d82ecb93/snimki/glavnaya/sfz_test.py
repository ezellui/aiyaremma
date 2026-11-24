"""Render test phrases through sfizz_render and measure them (no listening: numbers only).

python3 -I sfz_test.py SFIZZ_RENDER OUT_DIR SSO_ROOT VSCO_SFZ_ROOT
"""
import os
import subprocess
import sys

import mido
import numpy as np
import soundfile as sf

R, OUT, SSO, VS = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
S = os.path.join(SSO, "Sonatina Symphonic Orchestra")


def midi(path, notes, tempo=500000, tpb=480, ccs=()):
    """notes: (start_beats, dur_beats, pitch, vel); ccs: (beat, cc, value)"""
    ev = []
    for s, d, p, v in notes:
        ev.append((int(s * tpb), mido.Message("note_on", note=p, velocity=v)))
        ev.append((int((s + d) * tpb), mido.Message("note_off", note=p, velocity=0)))
    for b, c, val in ccs:
        ev.append((int(b * tpb), mido.Message("control_change", control=c, value=val)))
    ev.sort(key=lambda x: (x[0], x[1].type == "note_on"))
    mf = mido.MidiFile(ticks_per_beat=tpb)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=tempo))
    t = 0
    for at, m in ev:
        tr.append(m.copy(time=at - t))
        t = at
    tr.append(mido.MetaMessage("end_of_track", time=tpb * 4))
    mf.save(path)


def render(sfz, mid, wav):
    r = subprocess.run([R, "--sfz", sfz, "--midi", mid, "--wav", wav, "--use-eot"], capture_output=True, text=True)
    return r.returncode, (r.stderr + r.stdout)[-300:]


def rms_db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def centroid(x, sr):
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / sr)
    return float((sp * f).sum() / (sp.sum() + 1e-12))


def measure(wav, windows):
    y, sr = sf.read(wav)
    m = y.mean(1) if y.ndim > 1 else y
    out = []
    for a, b in windows:
        seg = m[int(a * sr):int(b * sr)]
        out.append((round(rms_db(seg), 1), round(centroid(seg, sr))))
    return round(len(m) / sr, 2), out


tests = {
    # a held note of 20 s (one beat = 0.5 s): does it last, or die at the end of the recording?
    "sso_celli_sustain_20s": (f"{S}/Strings - Notation/Celli Sustain.sfz", [(0, 40, 50, 90)], [(1, 3), (8, 10), (17, 19)]),
    "vsco_cello_sustain_20s": (f"{VS}/CelloEnsSusVib.sfz", [(0, 40, 50, 90)], [(1, 3), (8, 10), (17, 19)]),
    # the same note at three velocities: does the timbre change, not only the loudness?
    "sso_horns_vel": (f"{S}/Brass - Notation/Horns Sustain.sfz", [(0, 4, 53, 30), (6, 4, 53, 80), (12, 4, 53, 127)],
                      [(0.5, 1.8), (3.5, 4.8), (6.5, 7.8)]),
    "vsco_horn_vel": (f"{VS}/FHornSus.sfz", [(0, 4, 53, 30), (6, 4, 53, 80), (12, 4, 53, 127)],
                      [(0.5, 1.8), (3.5, 4.8), (6.5, 7.8)]),
    # a legato line
    "sso_flute_legato": (f"{S}/Woodwinds - Notation/Flute Solo 1 Legato.sfz",
                         [(0, 1.05, 72, 80), (1, 1.05, 74, 80), (2, 1.05, 76, 80), (3, 2, 79, 80)], [(0.2, 2.4)]),
    "sso_choir": (f"{S}/Chorus - Notation/Mixed Chorus.sfz", [(0, 8, 57, 80), (0, 8, 60, 80), (0, 8, 64, 80)], [(0.5, 3.5)]),
    "vsco_timpani": (f"{VS}/Timpani.sfz", [(0, 1, 38, 120), (1, 1, 45, 70)], [(0, 0.4), (0.5, 0.9)]),
}
for name, (sfz, notes, win) in tests.items():
    mid = os.path.join(OUT, name + ".mid")
    wav = os.path.join(OUT, name + ".wav")
    midi(mid, notes)
    rc, log = render(sfz, mid, wav)
    if rc or not os.path.exists(wav):
        print(f"{name:26} FAIL rc={rc} {log.strip()[-200:]}")
        continue
    dur, w = measure(wav, win)
    print(f"{name:26} {dur:6}s  " + "  ".join(f"[{a}-{b}s] {db} dB, centroid {c} Hz" for (a, b), (db, c) in zip(win, w)))
