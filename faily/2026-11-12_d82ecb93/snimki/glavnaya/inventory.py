"""Inventory of the two sample libraries: per folder (VSCO) and per SFZ instrument (SSO, VSCO-SFZ).

python3 -I inventory.py VSCO_ROOT SSO_ROOT VSCO_SFZ_DIR OUT_JSON
"""
import collections
import json
import os
import re
import sys

import soundfile as sf

vsco, sso, vsfz, out = sys.argv[1:5]


def wav_stats(root):
    rows = collections.defaultdict(lambda: dict(n=0, dur=[], sr=set(), ch=set()))
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.lower().endswith((".wav", ".flac")):
                continue
            p = os.path.join(dp, f)
            try:
                i = sf.info(p)
            except Exception:
                continue
            key = os.path.relpath(dp, root)
            r = rows[key]
            r["n"] += 1
            r["dur"].append(i.duration)
            r["sr"].add(i.samplerate)
            r["ch"].add(i.channels)
    res = {}
    for k, r in sorted(rows.items()):
        d = sorted(r["dur"])
        res[k] = dict(n=r["n"], dur_min=round(d[0], 2), dur_med=round(d[len(d) // 2], 2), dur_max=round(d[-1], 2),
                      sr=sorted(r["sr"]), ch=sorted(r["ch"]))
    return res


def parse_sfz(path, seen=None):
    """flatten an SFZ file: list of region opcode dicts (with #include and #define)"""
    seen = seen or set()
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"//[^\n]*", "", txt)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    base = os.path.dirname(path)

    def inc(m):
        p = os.path.join(base, m.group(1).replace("\\", "/"))
        if p in seen or not os.path.exists(p):
            return ""
        seen.add(p)
        t = open(p, encoding="utf-8", errors="replace").read()
        return re.sub(r"//[^\n]*", "", t)

    for _ in range(4):
        txt = re.sub(r'#include\s+"([^"]+)"', inc, txt)
    defs = dict(re.findall(r"#define\s+(\$\w+)\s+(\S+)", txt))
    for k in sorted(defs, key=len, reverse=True):
        txt = txt.replace(k, defs[k])
    regions, ctx = [], {"control": {}, "global": {}, "master": {}, "group": {}}
    cur = None
    for tok in re.split(r"(<\w+>)", txt):
        m = re.fullmatch(r"<(\w+)>", tok)
        if m:
            h = m.group(1)
            if cur is not None:
                regions.append(cur)
                cur = None
            if h == "region":
                cur = {}
            elif h in ctx:
                ctx[h] = {}
                if h == "global":
                    ctx["master"] = {}
                    ctx["group"] = {}
                if h == "master":
                    ctx["group"] = {}
                cur_hdr = h
            continue
        kv = dict(re.findall(r"(\w+)=([^\s=][^=]*?)(?=\s+\w+=|\s*$)", tok.strip(), flags=re.S))
        if cur is not None:
            cur.update(kv)
        elif 'cur_hdr' in dir():
            ctx[cur_hdr].update(kv)
        # merge context into region at creation
        if cur is not None and not cur.get("_ctx"):
            full = {}
            for h in ("control", "global", "master", "group"):
                full.update(ctx[h])
            full.update(cur)
            full["_ctx"] = 1
            cur.clear()
            cur.update(full)
    if cur is not None:
        regions.append(cur)
    return regions


NOTES = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}


def key(v):
    if v is None:
        return None
    v = v.strip().lower()
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    m = re.fullmatch(r"([a-g])(#|b)?(-?\d)", v)
    if m:
        return 12 * (int(m.group(3)) + 1) + NOTES[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)
    return None


def sfz_summary(path):
    regs = parse_sfz(path)
    regs = [r for r in regs if "sample" in r]
    if not regs:
        return None
    lo = [key(r.get("lokey", r.get("key"))) for r in regs]
    hi = [key(r.get("hikey", r.get("key"))) for r in regs]
    lo = [x for x in lo if x is not None]
    hi = [x for x in hi if x is not None]
    vel = {(r.get("lovel", "0"), r.get("hivel", "127")) for r in regs}
    centers = {key(r.get("pitch_keycenter", r.get("key"))) for r in regs}
    loops = collections.Counter(r.get("loop_mode", "-") for r in regs)
    rr = {r.get("seq_position") for r in regs if "seq_position" in r} | {r.get("lorand") for r in regs if "lorand" in r}
    sw = {r.get("sw_last") for r in regs if "sw_last" in r}
    trig = collections.Counter(r.get("trigger", "attack") for r in regs)
    ccs = sorted({k for r in regs for k in r if re.match(r"(locc|hicc|amplitude_oncc|amplitude_cc|.*_oncc)\d+", k)})
    return dict(regions=len(regs), lokey=min(lo) if lo else None, hikey=max(hi) if hi else None,
                vel_layers=len(vel), sampled_pitches=len(centers - {None}), rr=len(rr - {None}) or 1,
                keyswitches=len(sw - {None}), loop=dict(loops), triggers=dict(trig), cc=ccs[:12])


res = {"vsco_wav": wav_stats(vsco), "sso_wav": wav_stats(sso)}
res["sso_sfz"] = {}
for dp, _, fs in os.walk(sso):
    for f in sorted(fs):
        if f.endswith(".sfz"):
            p = os.path.join(dp, f)
            try:
                res["sso_sfz"][os.path.relpath(p, sso)] = sfz_summary(p)
            except Exception as e:
                res["sso_sfz"][os.path.relpath(p, sso)] = {"error": str(e)}
res["vsco_sfz"] = {}
for f in sorted(os.listdir(vsfz)):
    if f.endswith(".sfz"):
        res["vsco_sfz"][f] = sfz_summary(os.path.join(vsfz, f))
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print("ok", {k: len(v) for k, v in res.items()})
