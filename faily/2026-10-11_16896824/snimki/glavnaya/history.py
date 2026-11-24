"""Scenario engine: applies the events of scenario.json to the region set and yields
one 'configuration' (region -> state) per step, plus everything the renderer needs to know
about each change (changed regions, involved states, populations, capitals, colours)."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")

# muted map palette (no pure hues), chosen to read well under the globe shading
PALETTE = ["#d9c8a0", "#b9cf9a", "#e3b59a", "#a9c4d6", "#d6a9b8", "#c9b9dc", "#e2d48f", "#a8d1c0",
           "#cfa98a", "#b7b7a1"]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class History:
    def __init__(self, scenario_path):
        self.sc = json.load(open(scenario_path, encoding="utf-8"))
        self.regions = json.load(open(os.path.join(CACHE, "regions.json"), encoding="utf-8"))
        self.countries = json.load(open(os.path.join(CACHE, "countries.json"), encoding="utf-8"))
        a = np.load(os.path.join(CACHE, "arcs.npz"))
        self.arc_left, self.arc_right = a["left"], a["right"]
        self.pop = np.array([r["pop"] or 0 for r in self.regions], dtype=np.int64)
        self.area = np.array([r["area_km2"] or 0 for r in self.regions], dtype=np.float64)
        self.iso = [r["iso"] for r in self.regions]
        self.admin = [r["admin"] for r in self.regions]

        # states: id -> info; initial states are the admin units
        self.states = {}
        self.sid = {}
        for adm in sorted(set(self.admin)):
            self._add_state(adm, {"ru": self.countries.get(adm, {}).get("ru", adm), "short": None,
                                  "capital": None, "created": None, "origin": "base"})
        base = np.array([self.sid[a] for a in self.admin], dtype=np.int32)
        self._color_base(base)

        self.configs = [base]
        self.steps = []  # per event: dict with details
        warnings = []
        cur = base.copy()
        for k, ev in enumerate(self.sc["events"]):
            prev = cur.copy()
            new_states, involved = [], set()
            for op in ev["ops"]:
                if op["op"] in ("new_state", "join"):
                    sel = self._select(op["select"], cur)
                    if not sel.any():
                        warnings.append(f"{ev['year']}: selection of {op} is empty")
                        continue
                    involved |= set(np.unique(cur[sel]).tolist())
                    if op["op"] == "new_state":
                        s = self._add_state(op["id"], {"ru": op["ru"], "short": op.get("short"),
                                                       "capital": op.get("capital"), "created": ev["year"],
                                                       "origin": "event"})
                        new_states.append(s)
                    else:
                        s = self.sid[op["into"]]
                        involved.add(s)
                    cur[sel] = s
                elif op["op"] == "rename":
                    s = self.sid[op["state"]]
                    self.states_by_idx[s]["renames"].append((k, op))
                    involved.add(s)
                    new_states.append(s)
                else:
                    raise ValueError(op["op"])
            changed = cur != prev
            for s in new_states:
                if self.states_by_idx[s].get("color") is None:
                    self.states_by_idx[s]["color"] = self._pick_color(s, cur, prev)
            self.configs.append(cur.copy())
            targets = sorted(set(np.unique(cur[changed]).tolist()) | set(new_states))
            members_before = sorted(set(np.unique(prev[changed]).tolist()))
            self.steps.append({
                "event": ev, "changed": changed, "targets": targets, "before": members_before,
                "renamed": [s for s in new_states if not changed.any() or s not in np.unique(cur[changed])],
            })
        self.warnings = warnings

    # -- states -------------------------------------------------------------------------------
    def _add_state(self, sid, info):
        if not hasattr(self, "states_by_idx"):
            self.states_by_idx = []
        if sid in self.sid:
            raise ValueError(f"duplicate state id {sid}")
        info = dict(info, id=sid, renames=[], color=info.get("color"))
        self.sid[sid] = len(self.states_by_idx)
        self.states_by_idx.append(info)
        return self.sid[sid]

    def _select(self, sel, cur):
        m = np.zeros(len(self.regions), dtype=bool)
        for a in sel.get("admins", []):
            m |= np.array([x == a for x in self.admin])
        isos = set(sel.get("isos", []))
        if isos:
            m |= np.array([x in isos for x in self.iso])
        for s in sel.get("states", []):
            m |= cur == self.sid[s]
        return m

    def neighbours(self, conf):
        l, r = self.arc_left, self.arc_right
        ok = (l >= 0) & (r >= 0)
        a, b = conf[l[ok]], conf[r[ok]]
        d = a != b
        nb = {}
        for x, y in zip(a[d].tolist(), b[d].tolist()):
            nb.setdefault(x, set()).add(y)
            nb.setdefault(y, set()).add(x)
        return nb

    def _color_base(self, conf):
        nb = self.neighbours(conf)
        n = len(self.states_by_idx)
        area = np.bincount(conf, weights=self.area, minlength=n)
        for s in sorted(range(n), key=lambda s: -area[s]):  # big states first get the first colours
            used = {self.states_by_idx[t]["color"] for t in nb.get(s, ())}
            free = [c for c in PALETTE if c not in used] or PALETTE
            # spread colours: pick the least used free colour so far
            cnt = {c: 0 for c in PALETTE}
            for st in self.states_by_idx:
                if st["color"] in cnt:
                    cnt[st["color"]] += 1
            self.states_by_idx[s]["color"] = min(free, key=lambda c: (cnt[c], PALETTE.index(c)))
        ant = self.sid.get("Antarctica")
        if ant is not None:
            self.states_by_idx[ant]["color"] = "#eef2f4"

    def _pick_color(self, s, cur, prev):
        nb = self.neighbours(cur)
        avoid = {self.states_by_idx[t]["color"] for t in nb.get(s, ())}
        # also avoid the colour the area had before, so the change is visible
        mask = cur == s
        if mask.any():
            olds = np.bincount(prev[mask], weights=self.area[mask]).argmax()
            avoid.add(self.states_by_idx[olds]["color"])
        free = [c for c in PALETTE if c not in avoid]
        return (free or PALETTE)[(len(self.states_by_idx) * 3) % len(free or PALETTE)]

    # -- queries for the renderer ---------------------------------------------------------------
    def name(self, s, step):
        """state name as of configuration index `step` (0 = before the first event)."""
        st = self.states_by_idx[s]
        ru, short = st["ru"], st.get("short")
        for k, op in st["renames"]:
            if k < step:
                ru, short = op["ru"], op.get("short", short)
        return ru, (short or ru)

    def color(self, s, step):
        st = self.states_by_idx[s]
        c = st["color"]
        for k, op in st["renames"]:
            if k < step and op.get("color"):
                c = op["color"]
        return c

    def stats(self, conf, s):
        m = conf == s
        return int(self.pop[m].sum()), float(self.area[m].sum())

    def palette_rgb(self, step):
        return np.array([hex2rgb(self.color(s, step)) for s in range(len(self.states_by_idx))], dtype=np.uint8)


if __name__ == "__main__":
    h = History(os.path.join(HERE, "scenario.json"))
    print("states", len(h.states_by_idx), "configs", len(h.configs))
    for w in h.warnings:
        print("WARNING", w)
    for k, st in enumerate(h.steps, start=1):
        ev = st["event"]
        conf = h.configs[k]
        print(f"{ev['year']} {ev['title']}: changed regions {int(st['changed'].sum())}")
        for s in st["targets"]:
            p, a = h.stats(conf, s)
            print(f"    → {h.name(s, k)[0]}: {p / 1e6:.1f} млн, {a / 1e6:.2f} млн км², цвет {h.color(s, k)}")
        if st["before"]:
            print("      из:", ", ".join(h.name(s, k - 1)[0] for s in st["before"]))
    n0 = len(np.unique(h.configs[0])); n1 = len(np.unique(h.configs[-1]))
    print(f"государств/территорий на карте: {n0} → {n1}")
