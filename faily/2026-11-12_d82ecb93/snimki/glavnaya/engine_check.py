"""Check the SFZ engine: ranges per articulation, pitch of rendered notes vs the plain VSCO sampler, and the
loudness calibration at mezzo-forte (each library scaled to the plain sampler's level, so the balance of the
score stays as it was composed).

python3 engine_check.py MUSIC_DIR OUT_JSON
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, sys.argv[1])
import librosa  # noqa: E402

from sampler import SR, Sampler  # noqa: E402
from sfz_engine import MAP, SfzSampler  # noqa: E402

ARTS = [a for a in MAP["sso"] if a != "timp"]


def f0(y):
    m = y.mean(1)[int(0.25 * SR):int(1.4 * SR)]
    f, v, _ = librosa.pyin(m.astype(np.float32), fmin=25, fmax=4200, sr=SR, frame_length=4096)
    f = f[v] if v.any() else f[~np.isnan(f)]
    return None if len(f) == 0 else float(69 + 12 * np.log2(np.median(f) / 440))


def grab(s, art, midi):
    s.buses.clear()
    s.note(art, midi, 0.0, 1.6, vel=0.6, bus="x", release=0.3)
    return s.buses["x"][:int(2.0 * SR)].copy()


def rms(y):
    return float(np.sqrt((y ** 2).mean()) + 1e-12)


plain = Sampler(4)
libs = {lib: SfzSampler(4, lib) for lib in ("vsco", "sso")}
res = {"ranges": {}, "pitch": [], "calib": {"vsco": {}, "sso": {}}}
t0 = time.time()
for art in ARTS:
    rows = plain.idx[art]
    lo, hi = min(r["note"] for r in rows), max(r["note"] for r in rows)
    for lib, s in libs.items():
        rng = sorted({k for n in MAP[lib][art] for k in s.synth(n).find_range()})
        res["ranges"].setdefault(art, {})[lib] = [rng[0], rng[-1], len(rng)] if rng else None
    res["ranges"][art]["plain"] = [lo, hi]
    # test pitches: inside every range
    mids = [m for m in (lo + (hi - lo) // 4, (lo + hi) // 2) ]
    levels = {"plain": [], "vsco": [], "sso": []}
    for m in mids:
        yp = grab(plain, art, m)
        levels["plain"].append(rms(yp))
        row = {"art": art, "midi": m, "plain": f0(yp)}
        for lib, s in libs.items():
            y = grab(s, art, m)
            levels[lib].append(rms(y))
            row[lib] = f0(y)
        res["pitch"].append(row)
    for lib in libs:
        res["calib"][lib][art] = float(np.exp(np.mean(np.log(levels["plain"])) - np.mean(np.log(levels[lib]))))
    print(f"{art:10} plain {lo}-{hi}  vsco {res['ranges'][art]['vsco']}  sso {res['ranges'][art]['sso']}  "
          f"calib vsco {res['calib']['vsco'][art]:.2f} sso {res['calib']['sso'][art]:.2f}  "
          + "  ".join(f"[{r['midi']}: p {r['plain'] and round(r['plain'],1)} v {r['vsco'] and round(r['vsco'],1)} "
                      f"s {r['sso'] and round(r['sso'],1)}]" for r in res["pitch"][-2:]), flush=True)
print("time", round(time.time() - t0), "s")
json.dump(res, open(sys.argv[2], "w"), indent=1)
