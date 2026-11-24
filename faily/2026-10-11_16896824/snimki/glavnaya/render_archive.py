#!/usr/bin/env python3
"""'Archive' theme for the future-borders renderer: a sepia paper globe in the style of
a period map (Госгрибиздатъ), pre-reform orthography, hatched vassal states, period cities with
mycelial paths, and the scenario's own documents shown as cards from the case file.

  python3 render_archive.py --scenario scenario_rsfgr.json --plan
  python3 render_archive.py --scenario scenario_rsfgr.json --name rsfgr --preview 300 900
  python3 render_archive.py --scenario scenario_rsfgr.json --name rsfgr --workers 2
"""
import argparse
import json
import math
import os
import re
import subprocess
import time
from multiprocessing import Process

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render as RM
from history import History, hex2rgb
from render import FPS, H, SEC, W, basis, build_plan, camera_at, ease, ease_io, unit

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
GX0 = 720

SERIF = "Old Standard TT"
CONDENSED = "Oswald"

PAPER = (226, 214, 186)
OCEAN = (227, 218, 194)
NEUTRAL = (209, 193, 157)
INK = (0.15, 0.12, 0.09)
INK_SOFT = (0.36, 0.30, 0.22)
RED = (0.64, 0.17, 0.12)
CARD = (0.957, 0.929, 0.862)

# country names as they would appear on a map of the 1920s (keys: Natural Earth 'admin')
OLD_NAMES = {
    "Iran": "Персія", "Thailand": "Сіамъ", "Myanmar": "Бирма", "Sri Lanka": "Цейлонъ",
    "Belarus": "Бѣлоруссія", "Moldova": "Бессарабія", "Saudi Arabia": "Аравія", "Turkey": "Турція",
    "Israel": "Палестина", "West Bank": "Палестина", "Gaza Strip": "Палестина", "Jordan": "Трансіорданія",
    "United States of America": "Соединенные Штаты", "United Kingdom": "Великобританія", "China": "Китай",
    "Japan": "Японія", "North Korea": "Корея", "South Korea": "Корея", "Netherlands": "Голландія",
    "India": "Британская Индія", "Pakistan": "Британская Индія", "Bangladesh": "Британская Индія",
    "Laos": "Французскій Индокитай", "Cambodia": "Французскій Индокитай", "Vietnam": "Французскій Индокитай",
    "Indonesia": "Нидерландская Индія", "Democratic Republic of the Congo": "Бельгійское Конго",
    "Czech Republic": "Чехо-Словакія", "Slovakia": "Чехо-Словакія", "Republic of Serbia": "Югославія",
    "Croatia": "Югославія", "Slovenia": "Югославія", "Bosnia and Herzegovina": "Югославія",
    "Montenegro": "Югославія", "Macedonia": "Югославія", "Kosovo": "Югославія",
    "Ireland": "Ирландія", "Philippines": "Филиппины", "Greenland": "Гренландія",
}
VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯйЙ")
CONSONANTS = set("бвгджзклмнпрстфхцчшщБВГДЖЗКЛМНПРСТФХЦЧШЩ")


def old_orth(s):
    """modern Russian -> pre-1918 spelling for map names (і before vowels, final ъ; no ѣ)."""
    s = s.replace("ё", "е").replace("Ё", "Е")

    def word(m):
        w = m.group(0)
        if len(w) <= 4 and w.isupper():
            return w
        w = re.sub(r"[иИ](?=[аеёиоуыэюяйАЕЁИОУЫЭЮЯЙ])", lambda x: "і" if x.group(0) == "и" else "І", w)
        if w[-1] in CONSONANTS:
            w += "Ъ" if w.isupper() else "ъ"
        return w
    return re.sub(r"[А-Яа-яЁё]+", word, s)


def roman(n):
    out = ""
    for v, r in ((50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def fmt_num(p):
    if p >= 1e6:
        return f"{p / 1e6:.1f} милл.".replace(".0 ", " ").replace(".", ",", 1).replace(",милл", " милл")
    if p >= 1e3:
        return f"{p / 1e3:.0f} тыс."
    return f"{int(p)}"


def fmt_versts(km2):
    v = km2 / 1.138  # one square verst = 1.138 km²
    return f"{fmt_num(v)} кв. верстъ"


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


class ArchiveRenderer(RM.Renderer):
    def __init__(self, h):
        self.sc = h.sc
        super().__init__(h)
        self._apply_population()
        cs = self.sc.get("cities", [])
        self.acities = cs
        self.acity_xyz = unit(np.array([c["lon"] for c in cs]), np.array([c["lat"] for c in cs])) if cs else np.zeros((0, 3))
        cx = ((np.array([c["lon"] for c in cs]) + 180) / 360 * self.TW).astype(int) % self.TW if cs else []
        cy = np.clip(((90 - np.array([c["lat"] for c in cs])) / 180 * self.TH).astype(int), 0, self.TH - 1) if cs else []
        self.acity_reg = self.index[cy, cx].astype(np.int64) if cs else np.zeros(0, int)
        self.city_by_name = {c["ru"]: k for k, c in enumerate(cs)}
        self._docs = {}
        self._grat = self._graticule()

    # -- data ---------------------------------------------------------------------------
    def _apply_population(self):
        h = self.h
        spec = self.sc.get("population", {})
        pop = h.pop.astype(np.float64).copy()
        iso_over = spec.get("isos", {})
        for iso, val in iso_over.items():
            m = np.array([x == iso for x in h.iso])
            if m.any():
                base = pop[m].sum()
                pop[m] = pop[m] / base * val if base > 0 else val / m.sum()
        for adm, val in spec.get("admins", {}).items():
            m = np.array([a == adm and i not in iso_over for a, i in zip(h.admin, h.iso)])
            fixed = sum(v for i, v in iso_over.items() if any(a == adm and x == i for a, x in zip(h.admin, h.iso)))
            if m.any() and pop[m].sum() > 0:
                pop[m] *= max(val - fixed, 0) / pop[m].sum()
        h.pop = pop.round().astype(np.int64)

    def is_featured(self, s):
        return self.h.states_by_idx[s]["origin"] == "event"

    def is_core(self, s):
        st = self.h.states_by_idx[s]
        return st["origin"] == "event" and not st.get("hatch")

    def sname(self, s, step):
        full, short = self.h.name(s, step)
        st = self.h.states_by_idx[s]
        if st["origin"] == "base":
            adm = st["id"]
            nm = OLD_NAMES.get(adm) or old_orth(full)
            return nm, nm
        return full, short

    # -- textures -------------------------------------------------------------------------
    def palette(self, step):
        if step not in self._pal:
            conf = self.h.configs[step]
            n = len(conf)
            cols = self.h.palette_rgb(step).astype(np.float32)
            neutral = np.array([not self.is_featured(s) for s in range(len(self.h.states_by_idx))])
            cols[neutral] = NEUTRAL
            hatch = np.array([1.0 if st.get("hatch") else 0.0 for st in self.h.states_by_idx], np.float32)
            P = np.zeros((n + 2, 5), np.float32)
            P[:n, :3] = cols[conf]
            P[:n, 3] = 255
            P[:n, 4] = hatch[conf]
            P[self.SEA, :3] = OCEAN
            P[self.LAKE, :3] = OCEAN
            self._pal[step] = P
        return self._pal[step]

    def _background(self):
        rng = np.random.default_rng(3)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.zeros((H, W, 3), np.float32) + np.array(PAPER, np.float32)
        # low-frequency blotches (paper), static, so it costs nothing to encode
        small = rng.normal(0, 1, (H // 40 + 2, W // 40 + 2)).astype(np.float32)
        blot = np.array(Image.fromarray(small).resize((W, H), Image.BICUBIC))
        img += blot[..., None] * np.array([5.0, 4.5, 3.5])
        fine = rng.normal(0, 1, (H, W)).astype(np.float32)
        img += fine[..., None] * 2.2
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        img *= (1 - 0.22 * np.clip(d - 0.55, 0, 1) ** 1.4)[..., None]
        img = np.clip(img, 0, 255)
        bgra = np.empty((H, W, 4), np.uint8)
        bgra[..., 0] = img[..., 2]
        bgra[..., 1] = img[..., 1]
        bgra[..., 2] = img[..., 0]
        bgra[..., 3] = 255
        return bgra

    def _graticule(self):
        lines = []
        for lon in range(-180, 180, 15):
            lat = np.arange(-80, 80.1, 2.0)
            lines.append(unit(np.full_like(lat, lon), lat))
        for la in range(-75, 76, 15):
            lon = np.arange(-180, 180.1, 2.0)
            lines.append(unit(lon, np.full_like(lon, la)))
        return lines

    # -- globe ------------------------------------------------------------------------------
    def globe(self, frame, lon0, lat0, R, steps, t, dets):
        GX, GY = RM.GX, RM.GY
        f, e, n = (np.asarray(v, np.float32) for v in basis(lon0, lat0))
        x0, x1 = max(0, int(GX - R - 2)), min(W, int(GX + R + 3))
        y0, y1 = max(0, int(GY - R - 2)), min(H, int(GY + R + 3))
        if x0 >= x1 or y0 >= y1:
            return
        if not hasattr(self, "_px"):
            self._px = (np.arange(W, dtype=np.float32) + 0.5, np.arange(H, dtype=np.float32) + 0.5)
        iR = np.float32(1.0 / R)
        u = ((self._px[0][x0:x1] - GX) * iR)[None, :]
        v = ((GY - self._px[1][y0:y1]) * iR)[:, None]
        rho2 = u * u + v * v
        inside = rho2 < 1.0 + 2.0 / R
        full = bool(inside.all())
        if full:
            u = np.broadcast_to(u, rho2.shape).ravel()
            v = np.broadcast_to(v, rho2.shape).ravel()
            rho2 = rho2.ravel()
        else:
            u = np.broadcast_to(u, rho2.shape)[inside]
            v = np.broadcast_to(v, rho2.shape)[inside]
            rho2 = rho2[inside]
        w = np.sqrt(np.maximum(1.0 - rho2, 0.0)).astype(np.float32)
        X = u * e[0] + v * n[0] + w * f[0]
        Y = u * e[1] + v * n[1] + w * f[1]
        Z = u * e[2] + v * n[2] + w * f[2]
        lon = np.degrees(np.arctan2(Y, X))
        lat = np.degrees(np.arcsin(np.clip(Z, -1, 1)))
        PA = self.palette(steps[0])
        P = PA if (steps[1] == steps[0] or t <= 0) else PA * (1 - t) + self.palette(steps[1]) * t
        ids, fw = self.sample_ids(self.index, (lon + 180.0) * np.float32(self.TW / 360.0),
                                  (90.0 - lat) * np.float32(self.TH / 180.0), True)
        c = self.shade_ids(ids, fw, P)
        for d in dets:
            if d is None:
                continue
            b, idx = d["bounds"], d["idx"]
            m = np.nonzero((lon > b[0]) & (lon < b[2]) & (lat > b[1]) & (lat < b[3]))[0]
            if not len(m):
                continue
            dh, dw = idx.shape
            ids2, fw2 = self.sample_ids(idx, (lon[m] - b[0]) * np.float32(dw / (b[2] - b[0])),
                                        (b[3] - lat[m]) * np.float32(dh / (b[3] - b[1])), False)
            c[m] = self.shade_ids(ids2, fw2, P)
        rgb = c[:, :3]
        hatch = c[:, 4]
        if hatch.max() > 0.01:  # geo-anchored diagonal hatching, spacing kept ~10 px at any zoom
            deg_px = 180.0 / (math.pi * R)
            L = math.log2(10.0 * deg_px)
            s0 = 2.0 ** math.floor(L)
            fr_ = L - math.floor(L)
            dcoord = lon * np.cos(np.radians(lat)) + lat
            def stripes(s):
                g = np.mod(dcoord / s, 1.0)
                dist = np.minimum(g, 1 - g) * s / deg_px
                return np.clip(1.3 - dist, 0, 1)
            st = (1 - fr_) * stripes(s0) + fr_ * stripes(2 * s0)
            rgb = rgb * (1 - (0.30 * hatch * st))[:, None]
        L_ = np.array([-0.42, 0.52, 0.74], np.float32)
        L_ /= np.linalg.norm(L_)
        ndl = np.clip(u * L_[0] + v * L_[1] + w * L_[2], 0, 1)
        shade = 0.80 + 0.26 * ndl
        rim = (1 - w) ** 2.5
        rgb = rgb * (shade * (1 - 0.30 * rim))[:, None] + (0.30 * rim)[:, None] * np.array([96, 78, 52], np.float32)
        rgb = np.clip(rgb, 0, 255)
        bgr = rgb[:, ::-1]
        view = frame[y0:y1, x0:x1]
        if full:
            view[..., :3] = bgr.reshape(view.shape[0], view.shape[1], 3).astype(np.uint8)
            return
        a = np.clip((1.0 - np.sqrt(rho2)) * R + 0.5, 0, 1)[:, None]
        sub = view[inside][:, :3].astype(np.float32)
        view[..., :3][inside] = (sub * (1 - a) + bgr * a).astype(np.uint8)

    # -- text helpers -------------------------------------------------------------------------
    def font(self, ctx, size, bold=False, italic=False, face=SERIF):
        ctx.select_font_face(face, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)

    def tw(self, ctx, s, size, bold=False, italic=False, face=SERIF, spacing=0.0):
        self.font(ctx, size, bold, italic, face)
        if not spacing:
            return ctx.text_extents(s).x_advance
        return sum(ctx.text_extents(ch).x_advance for ch in s) + spacing * size * max(len(s) - 1, 0)

    def put(self, ctx, s, x, y, size, rgb=INK, alpha=1.0, bold=False, italic=False, face=SERIF,
            spacing=0.0, halo=None, halo_w=3.0):
        self.font(ctx, size, bold, italic, face)
        ctx.new_path()
        if spacing:
            xx = x
            for ch in s:
                ctx.move_to(xx, y)
                ctx.text_path(ch)
                xx += ctx.text_extents(ch).x_advance + spacing * size
        else:
            ctx.move_to(x, y)
            ctx.text_path(s)
        if halo is not None:
            ctx.set_source_rgba(*halo, 0.75 * alpha)
            ctx.set_line_width(halo_w)
            ctx.stroke_preserve()
        ctx.set_source_rgba(*rgb, alpha)
        ctx.fill()

    def wrap2(self, ctx, s, size, width, bold=False, italic=False):
        words, lines, cur = s.split(), [], ""
        for wd in words:
            nxt = (cur + " " + wd).strip()
            if self.tw(ctx, nxt, size, bold, italic) <= width:
                cur = nxt
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    # -- documents ------------------------------------------------------------------------------
    def doc_surface(self, path, maxw, maxh):
        key = (path, maxw, maxh)
        if key in self._docs:
            return self._docs[key]
        im = Image.open(os.path.join(HERE, path)).convert("RGB")
        sc = min(maxw / im.width, maxh / im.height)
        w, h = int(im.width * sc), int(im.height * sc)
        im = im.resize((w, h), Image.LANCZOS)
        a = np.array(im)
        bgra = np.empty((h, w, 4), np.uint8)
        bgra[..., 0], bgra[..., 1], bgra[..., 2], bgra[..., 3] = a[..., 2], a[..., 1], a[..., 0], 255
        surf = cairo.ImageSurface.create_for_data(memoryview(bgra.copy()), cairo.FORMAT_ARGB32, w, h, w * 4)
        pad = 46
        sh = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
        ImageDraw.Draw(sh).rectangle([pad, pad, pad + w, pad + h], fill=170)
        sh = np.array(sh.filter(ImageFilter.GaussianBlur(16)))
        sb = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
        sb[..., 0] = (sh * 0.10).astype(np.uint8)  # premultiplied dark brown
        sb[..., 1] = (sh * 0.13).astype(np.uint8)
        sb[..., 2] = (sh * 0.18).astype(np.uint8)
        sb[..., 3] = sh
        ssurf = cairo.ImageSurface.create_for_data(memoryview(sb.copy()), cairo.FORMAT_ARGB32, w + 2 * pad,
                                                   h + 2 * pad, (w + 2 * pad) * 4)
        self._docs[key] = (surf, ssurf, w, h, pad)
        return self._docs[key]

    def docs_for_frame(self, fr):
        """(docs, alpha, slide_px) to show on this frame."""
        ph = fr["phase"]
        if ph in ("pre", "trans", "hold") and fr.get("ev"):
            docs = self.h.steps[fr["ev"] - 1]["event"].get("docs", [])
            if docs:
                k = fr.get("evf", 0) / SEC(0.9)
                a = ease(k)
                return docs, a, -720 * (1 - a)
        if ph == "fly" and fr.get("prev_ev"):
            docs = self.h.steps[fr["prev_ev"] - 1]["event"].get("docs", [])
            if docs:
                k = fr["i"] / SEC(0.6)
                if k < 1:
                    return docs, 1 - ease(k), -720 * ease(k)
        if ph == "outro" and self.sc["outro"].get("docs"):
            a = ease(fr["i"] / SEC(1.2))
            return self.sc["outro"]["docs"], a, -720 * (1 - a)
        if ph == "intro" and self.sc["intro"].get("docs"):
            k = fr["i"] / SEC(0.8)
            a = ease(k) * (1 - ease((fr["i"] - fr["n"] + SEC(0.7)) / SEC(0.7)))
            return self.sc["intro"]["docs"], a, -720 * (1 - min(1, ease(k)))
        return [], 0.0, 0.0

    def draw_docs(self, ctx, docs, alpha, slide):
        if not docs or alpha <= 0.01:
            return
        nd = len(docs)
        boxes = {1: [(70, 120, 640, 800, -1.4)], 2: [(40, 96, 470, 600, -3.2), (290, 330, 470, 600, 2.6)]}
        lay = boxes.get(nd, boxes[2])
        last = None
        for k, d in enumerate(docs[:2]):
            x, y, mw, mh, rot = lay[k]
            if d.get("wide"):
                mw, mh = 720, 760
            surf, ssurf, w, h, pad = self.doc_surface(d["file"], mw, mh)
            cx, cy = x + slide + mw / 2, y + h / 2 if nd == 2 else (H - h) / 2 - 10 + h / 2
            if nd == 1:
                cx = x + slide + w / 2
            ctx.save()
            ctx.translate(cx, cy)
            ctx.rotate(math.radians(rot))
            ctx.set_source_surface(ssurf, -w / 2 - pad + 9, -h / 2 - pad + 14)
            ctx.paint_with_alpha(0.75 * alpha)
            ctx.set_source_surface(surf, -w / 2, -h / 2)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint_with_alpha(alpha)
            ctx.restore()
            last = (cx, cy, w, h, d)
        if last:
            cx, cy, w, h, d = last
            cap = " · ".join(dd.get("caption", "") for dd in docs if dd.get("caption"))
            if cap:
                yy = min(H - 92, cy + h / 2 + 34)
                for j, ln in enumerate(self.wrap2(ctx, cap, 16, 640, italic=True)[:2]):
                    self.put(ctx, ln, 70 + slide, yy + j * 20, 16, rgb=INK_SOFT, alpha=alpha, italic=True,
                             halo=(PAPER[0] / 255, PAPER[1] / 255, PAPER[2] / 255), halo_w=4)

    # -- vectors ----------------------------------------------------------------------------------
    def classes(self, step):
        conf = self.h.configs[step]
        l, r = self.left, self.right
        sl = conf[l]
        sr = np.where(r >= 0, conf[np.maximum(r, 0)], -1)
        coast = r < 0
        diff = (~coast) & (sl != sr)
        inner = (~coast) & (sl == sr)
        core = np.array([self.is_core(s) for s in range(len(self.h.states_by_idx))])
        feat = np.array([self.is_featured(s) for s in range(len(self.h.states_by_idx))])
        cl, cr = core[sl], np.where(r >= 0, core[np.maximum(sr, 0)], False)
        fl, fr_ = feat[sl], np.where(r >= 0, feat[np.maximum(sr, 0)], False)
        heavy = diff & (cl | cr)
        medium = diff & ~heavy & (fl | fr_)
        light = diff & ~heavy & ~medium
        return coast, heavy, medium, light, inner

    def great_circle(self, a, b, n=48):
        d = float(np.clip(np.dot(a, b), -1, 1))
        om = math.acos(d)
        if om < 1e-6:
            return np.array([a, b])
        t = np.linspace(0, 1, n)[:, None]
        return (np.sin((1 - t) * om) * a + np.sin(t * om) * b) / math.sin(om)

    def polyline(self, ctx, pts, f, e, n, R):
        GX, GY = RM.GX, RM.GY
        x = GX + R * (pts @ e)
        y = GY - R * (pts @ n)
        w = pts @ f
        pen = False
        for j in range(len(pts)):
            if w[j] > 0.02:
                if pen:
                    ctx.line_to(x[j], y[j])
                else:
                    ctx.move_to(x[j], y[j])
                    pen = True
            else:
                pen = False

    def city_active(self, k, step):
        c = self.acities[k]
        conf = self.h.configs[step]
        reg = self.acity_reg[k]
        if c.get("always"):
            return True
        if reg < len(conf) and self.is_featured(int(conf[reg])):
            return True
        return False

    def draw_mushroom(self, ctx, x, y, s, alpha):
        ctx.new_path()
        ctx.rectangle(x - 0.22 * s, y - 0.1 * s, 0.44 * s, 0.75 * s)
        ctx.set_source_rgba(*INK, alpha)
        ctx.fill()
        ctx.new_path()
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1.0, 0.62)
        ctx.arc(0, 0, 0.62 * s, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.restore()
        ctx.set_source_rgba(*INK, alpha)
        ctx.fill()

    def draw_star(self, ctx, x, y, r, alpha, spiral=True):
        ctx.new_path()
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.42
            px, py = x + rr * math.cos(ang), y + rr * math.sin(ang)
            ctx.line_to(px, py) if k else ctx.move_to(px, py)
        ctx.close_path()
        ctx.set_source_rgba(*RED, alpha)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.3, 0.06, 0.04, alpha)
        ctx.set_line_width(0.8)
        ctx.stroke()
        if spiral:
            ctx.new_path()
            for k in range(60):
                th = k / 59 * 3.2 * math.pi
                rr = 0.06 * r + 0.13 * r * th / math.pi
                px, py = x + rr * math.cos(th), y + rr * math.sin(th) + 0.08 * r
                ctx.line_to(px, py) if k else ctx.move_to(px, py)
            ctx.set_source_rgba(0.98, 0.92, 0.80, alpha)
            ctx.set_line_width(max(0.8, r * 0.07))
            ctx.stroke()

    # -- frame --------------------------------------------------------------------------------------
    def frame(self, fr):
        h = self.h
        docs, dalpha, dslide = self.docs_for_frame(fr)
        RM.GX = GX0 + 250 * dalpha
        GX, GY = RM.GX, RM.GY
        lon0, lat0, zoom = camera_at(fr)
        R = RM.R0 * zoom
        phase = fr["phase"]
        t = 0.0
        sa = sb = fr["step"]
        if phase == "trans":
            sa, sb = fr["step"] - 1, fr["step"]
            t = ease((fr["i"] + 0.5) / fr["n"])
        ev = fr.get("ev")
        dets = [self.detail_for(k) for k in {ev, fr.get("prev_ev")} if k]
        img = self.bg.copy()
        surf = cairo.ImageSurface.create_for_data(memoryview(img), cairo.FORMAT_ARGB32, W, H, W * 4)
        ctx = cairo.Context(surf)
        if R < 2.5 * W:  # soft shadow under the globe
            g = cairo.RadialGradient(GX + 10, GY + 16, R * 0.96, GX + 10, GY + 16, R * 1.09)
            g.add_color_stop_rgba(0, 0.25, 0.18, 0.10, 0.38)
            g.add_color_stop_rgba(1, 0.25, 0.18, 0.10, 0.0)
            ctx.arc(GX + 10, GY + 16, R * 1.09, 0, 2 * math.pi)
            ctx.set_source(g)
            ctx.fill()
        surf.flush()
        self.globe(img, lon0, lat0, R, (sa, sb), t, dets)
        surf.mark_dirty()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if R < 2.5 * W:  # thin rim
            ctx.new_path()
            ctx.arc(GX, GY, R, 0, 2 * math.pi)
            ctx.set_source_rgba(0.30, 0.24, 0.16, 0.55)
            ctx.set_line_width(1.2)
            ctx.stroke()

        f, e, n = (np.asarray(v, np.float32) for v in basis(lon0, lat0))
        # graticule
        ctx.new_path()
        for ln in self._grat:
            self.polyline(ctx, ln, f, e, n, R)
        ctx.set_source_rgba(0.42, 0.34, 0.22, 0.20)
        ctx.set_line_width(0.7)
        ctx.stroke()

        deg_px = 180.0 / (math.pi * R)
        _, xyz, off, brk, has_brk = next(l for l in self.levels if l[0] <= 0.7 * deg_px)
        self._brk, self._has_brk = brk, has_brk
        sx, sy, w = self.project(xyz, f, e, n, R)
        onscreen = (sx > -50) & (sx < W + 50) & (sy > -50) & (sy < H + 50)
        vis_pt = (w > 0.0) & onscreen
        arc_vis = np.maximum.reduceat(vis_pt, off[:-1]).astype(bool) & ~self.seam
        lw = 1.0 + 0.30 * math.log2(max(zoom, 1.0))
        ca, ha, ma, la, ia = self.classes(sa)
        cb, hb, mb, lb, ib = self.classes(sb)
        layers = [(sb, 1.0)] if sa == sb else [(sa, 1 - t), (sb, t)]
        a_in = min(1.0, max(0.0, (zoom - 1.6) / 1.4)) * 0.22
        if a_in > 0.01:
            pth = self.build_path(ctx, arc_vis & (ia | ib) & ~(ha | hb | ma | mb | la | lb), sx, sy, vis_pt, off)
            self.stroke(ctx, pth, 0.55 * lw, (0.40, 0.32, 0.20, a_in))
        pth = self.build_path(ctx, arc_vis & ca, sx, sy, vis_pt, off)
        self.stroke(ctx, pth, 0.85 * lw, (0.30, 0.24, 0.15, 0.70))
        for st_, wgt in layers:
            c_, hv, md, lt, _ = (ca, ha, ma, la, ia) if st_ == sa else (cb, hb, mb, lb, ib)
            if wgt < 0.01:
                continue
            pth = self.build_path(ctx, arc_vis & lt, sx, sy, vis_pt, off)
            self.stroke(ctx, pth, 0.7 * lw, (0.36, 0.29, 0.19, 0.60 * wgt))
            pth = self.build_path(ctx, arc_vis & md, sx, sy, vis_pt, off)
            ctx.set_dash([4 * lw, 3 * lw])
            self.stroke(ctx, pth, 1.1 * lw, (0.18, 0.14, 0.10, 0.80 * wgt))
            ctx.set_dash([])
            pth = self.build_path(ctx, arc_vis & hv, sx, sy, vis_pt, off)
            self.stroke(ctx, pth, 2.1 * lw, (0.10, 0.08, 0.06, 0.92 * wgt))

        # highlight of the changing territory
        hi = 0.0
        if ev and phase in ("pre", "trans", "hold"):
            k = fr.get("evf", 0) / FPS
            st = h.steps[ev - 1]
            hold_s = st["event"].get("hold", 2.4) + st["event"].get("trans", 1.7) + st["event"].get("pre", 0.7)
            hi = min(1.0, ease(k / 0.8)) * (1 - ease((k - (hold_s - 1.2)) / 1.0))
            if not st["changed"].any():
                hi = 0.0
        if hi > 0.01:
            st = h.steps[ev - 1]
            mask = st["changed"]
            ml = mask[self.left]
            mr = np.where(self.right >= 0, mask[np.maximum(self.right, 0)], False)
            pth = self.build_path(ctx, arc_vis & (ml != mr), sx, sy, vis_pt, off)
            pulse = 0.7 + 0.3 * math.sin(fr["frame"] / FPS * 2 * math.pi * 0.8)
            for width, alpha in ((8.0, 0.16), (3.4, 0.40), (1.5, 0.95)):
                self.stroke(ctx, pth, width * lw, (*RED, alpha * hi * pulse))

        self.draw_vortex(ctx, f, e, n, R, fr)
        self.draw_paths(ctx, f, e, n, R, fr)
        taken = self.draw_acities(ctx, f, e, n, R, zoom, fr)
        self.draw_alabels(ctx, f, e, n, R, zoom, fr, sa, sb, t, taken)
        self.draw_docs(ctx, docs, dalpha, dslide)
        self.draw_apanel(ctx, fr)
        self.draw_atimeline(ctx, fr)
        surf.flush()
        return img

    def first_step_of(self, sid):
        for k, st in enumerate(self.h.steps, start=1):
            if self.h.sid.get(sid) in st["targets"]:
                return k
        return 10 ** 6

    def draw_vortex(self, ctx, f, e, n, R, fr):
        vx = self.sc.get("vortex")
        if not vx:
            return
        k0 = self.first_step_of(vx["after_state"])
        step = fr["step"]
        if step < k0:
            return
        a = 1.0
        if step == k0 and fr["phase"] == "trans":
            a = ease((fr["i"] + 0.5) / fr["n"])
        p = unit(vx["lon"], vx["lat"])
        ww = float(p @ f)
        if ww < 0.05:
            return
        x, y = RM.GX + R * float(p @ e), RM.GY - R * float(p @ n)
        rad = vx.get("radius_km", 420) / 6371.0 * R
        g = cairo.RadialGradient(x, y, 0, x, y, rad * 1.3)
        g.add_color_stop_rgba(0, 0.16, 0.13, 0.10, 0.55 * a)
        g.add_color_stop_rgba(0.6, 0.16, 0.13, 0.10, 0.22 * a)
        g.add_color_stop_rgba(1, 0.16, 0.13, 0.10, 0.0)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1.0, max(ww, 0.2))
        ctx.arc(0, 0, rad * 1.3, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source(g)
        ctx.fill()
        ph = (fr["frame"] / FPS * 0.15) % 1.0
        for k in range(6):
            rr = rad * (0.35 + 0.33 * ((k / 6 + ph) % 1.0) * 3.0)
            ctx.new_path()
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1.0, max(ww, 0.2))
            ctx.arc(0, 0, rr, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0.20, 0.16, 0.12, 0.30 * a)
            ctx.set_line_width(0.9)
            ctx.stroke()

    def draw_paths(self, ctx, f, e, n, R, fr):
        step = fr["step"]
        ctx.new_path()
        for a_, b_ in self.sc.get("paths", []):
            ka, kb = self.city_by_name.get(a_), self.city_by_name.get(b_)
            if ka is None or kb is None:
                continue
            if not (self.city_active(ka, step) and self.city_active(kb, step)):
                continue
            pts = self.great_circle(self.acity_xyz[ka], self.acity_xyz[kb])
            self.polyline(ctx, pts, f, e, n, R)
        ctx.set_dash([1.2, 4.0])
        ctx.set_source_rgba(*RED, 0.75)
        ctx.set_line_width(1.6)
        ctx.stroke()
        ctx.set_dash([])

    def draw_acities(self, ctx, f, e, n, R, zoom, fr):
        taken = []
        step = fr["step"]
        ev = fr.get("ev")
        s = 6.0 + 1.0 * math.log2(max(zoom, 1))
        fs = 13 + 1.2 * math.log2(max(zoom, 1))
        caps = {}
        for sidx, st in enumerate(self.h.states_by_idx):
            cap = st.get("capital")
            if cap and st["origin"] == "event" and (self.h.configs[step] == sidx).any():
                caps[cap["ru"]] = cap
        for k, c in enumerate(self.acities):
            if not self.city_active(k, step) and not (ev and c.get("show_on") and ev in c["show_on"]):
                continue
            if c["ru"] in caps:
                continue
            p = self.acity_xyz[k]
            if float(p @ f) < 0.12:
                continue
            x, y = RM.GX + R * float(p @ e), RM.GY - R * float(p @ n)
            if not (0 < x < W and 0 < y < H):
                continue
            if zoom < 1.25 and not c.get("major"):
                continue
            self.draw_mushroom(ctx, x, y, s, 0.9)
            taken.append((x - s, y - s, x + s, y + s))
            if zoom >= 1.25 or c.get("major"):
                self.put(ctx, c["ru"], x + s * 0.9, y + fs * 0.35, fs, rgb=INK, alpha=0.92,
                         halo=(0.93, 0.89, 0.80), halo_w=3.0)
                ww = self.tw(ctx, c["ru"], fs)
                taken.append((x + s * 0.9, y - fs * 0.7, x + s * 0.9 + ww, y + fs * 0.45))
        for nm, cap in caps.items():
            p = unit(cap["lon"], cap["lat"])
            if float(p @ f) < 0.1:
                continue
            x, y = RM.GX + R * float(p @ e), RM.GY - R * float(p @ n)
            if not (0 < x < W and 0 < y < H):
                continue
            big = cap.get("star", False)
            r = (13 if big else 8) + 1.2 * math.log2(max(zoom, 1))
            self.draw_star(ctx, x, y, r, 1.0, spiral=big)
            taken.append((x - r, y - r, x + r, y + r))
            fsz = fs + (5 if big else 1)
            self.put(ctx, nm, x + r + 4, y + fsz * 0.35, fsz, rgb=RED if big else INK, bold=True,
                     halo=(0.94, 0.90, 0.81), halo_w=3.4)
            ww = self.tw(ctx, nm, fsz, bold=True)
            taken.append((x + r + 4, y - fsz * 0.7, x + r + 4 + ww, y + fsz * 0.45))
            if cap.get("note") and zoom >= 1.4:
                self.put(ctx, cap["note"], x + r + 4, y + fsz * 0.35 + fsz, fsz * 0.72, rgb=INK_SOFT, italic=True,
                         halo=(0.94, 0.90, 0.81))
        return taken

    def draw_alabels(self, ctx, f, e, n, R, zoom, fr, sa, sb, t, taken):
        placed = list(taken)
        layers = [(sb, t if sa != sb else 1.0)]
        if sa != sb:
            layers.append((sa, 1 - t))
        targets = set()
        if fr.get("ev") and fr["phase"] in ("pre", "trans", "hold"):
            targets = set(self.h.steps[fr["ev"] - 1]["targets"])
        dock_x = 70 + 660 if fr["phase"] != "fly" else -1
        cands = []
        for step, alpha in layers:
            if alpha < 0.03:
                continue
            for s, (p, area, pop) in self.state_labels(step).items():
                feat = self.is_featured(s)
                size_px = math.sqrt(area) / 6371.0 * R
                prio = (2 if s in targets and step == sb else (1 if feat else 0), size_px * alpha)
                cands.append((prio, s, step, alpha, p, size_px, feat))
        cands.sort(key=lambda c: c[0], reverse=True)
        drawn = 0
        for prio, s, step, alpha, p, size0, feat in cands:
            if drawn > 80:
                break
            anchors = [p] + (self.state_anchors(step, s) if feat else [])
            st = self.h.states_by_idx[s]
            for q in anchors:
                ww = float(q @ f)
                if ww < 0.2:
                    continue
                x, y = RM.GX + R * float(q @ e), RM.GY - R * float(q @ n)
                if not (24 < x < W - 24 and 24 < y < H - 80):
                    continue
                size_px = size0 * (0.4 + 0.6 * ww)
                full, short = self.sname(s, step)
                if feat:
                    caps_ = full.upper()
                    fs = min(26, max(13, size_px / 8))
                    sp = 0.16
                    bold, italic = not st.get("hatch"), bool(st.get("hatch"))
                    col = INK if not st.get("hatch") else INK_SOFT
                    words = caps_.split()
                    lines = [caps_]
                    width = self.tw(ctx, caps_, fs, bold, italic, spacing=sp)
                    if width > max(size_px * 1.5, 220) and len(words) > 1:
                        best = None
                        for kk in range(1, len(words)):
                            a1, a2 = " ".join(words[:kk]), " ".join(words[kk:])
                            wd = max(self.tw(ctx, a1, fs, bold, italic, spacing=sp), self.tw(ctx, a2, fs, bold, italic, spacing=sp))
                            if best is None or wd < best[1]:
                                best = ([a1, a2], wd)
                        lines, width = best
                else:
                    if zoom < 1.3 and size_px < 60:
                        break
                    fs = min(17, max(10.5, size_px / 7))
                    sp = 0.0
                    bold, italic, col = False, True, (0.40, 0.33, 0.24)
                    lines = [full]
                    width = self.tw(ctx, full, fs, False, True)
                    if width > size_px * 1.4:
                        break
                lh = fs * 1.12
                top = y - fs * 0.75 - (len(lines) - 1) * lh / 2
                rect = (x - width / 2 - 4, top - 2, x + width / 2 + 4, top + len(lines) * lh + 2)
                if any(not (rect[2] < q2[0] or rect[0] > q2[2] or rect[3] < q2[1] or rect[1] > q2[3]) for q2 in placed):
                    continue
                if fr["phase"] != "fly" and rect[2] > 1430 and rect[1] < 820:
                    continue
                if rect[0] < dock_x and rect[1] < H - 120 and self._docs_visible:
                    continue
                placed.append(rect)
                drawn += 1
                for kk, ln in enumerate(lines):
                    lw_ = self.tw(ctx, ln, fs, bold, italic, spacing=sp)
                    self.put(ctx, ln, x - lw_ / 2, top + fs * 0.85 + kk * lh, fs, rgb=col, alpha=alpha * 0.95,
                             bold=bold, italic=italic, spacing=sp, halo=(0.93, 0.89, 0.80), halo_w=3.2)
                break

    # -- panel & timeline ---------------------------------------------------------------------------
    def panel_year(self, fr):
        tt = (fr["i"] + 0.5) / fr["n"]
        return fr["year0"] + (fr["year1"] - fr["year0"]) * (ease_io(tt) if fr["phase"] == "fly" else 1.0)

    def pop_label(self, step):
        lab = None
        for k, st in enumerate(self.h.steps, start=1):
            if k <= step and st["event"].get("pop_label"):
                lab = st["event"]["pop_label"]
        return lab

    def union_totals(self, step):
        conf = self.h.configs[step]
        core = np.array([self.is_core(s) for s in range(len(self.h.states_by_idx))])[conf]
        vas = np.array([self.is_featured(s) and not self.is_core(s) for s in range(len(self.h.states_by_idx))])[conf]
        return (int(self.h.pop[core].sum()), float(self.h.area[core].sum()),
                int(self.h.pop[vas].sum()), float(self.h.area[vas].sum()))

    def fmt_people(self, p, step):
        lab = self.pop_label(step)
        if lab:
            return f"{lab} {fmt_num(p)}"
        return f"≈ {fmt_num(p)} душъ"

    def draw_apanel(self, ctx, fr):
        h = self.h
        phase = fr["phase"]
        X, Y, PW = 1436, 52, 436
        year = self.panel_year(fr)
        yi = int(round(year))
        body, alpha = [], 1.0
        tt = (fr["i"] + 0.5) / fr["n"]
        if phase == "intro":
            alpha = ease(fr["i"] / SEC(0.6))
            body = [("title", self.sc["title"]), ("sub", self.sc.get("subtitle", "")), ("text", self.sc["intro"]["text"])]
        elif phase == "outro":
            alpha = ease(fr["i"] / SEC(0.6))
            step = len(h.configs) - 1
            cp, ca, vp, va = self.union_totals(step)
            body = [("title", "Итогъ"), ("text", self.sc["outro"]["text"]),
                    ("stat", "Союзъ"), ("num", f"{self.fmt_people(cp, step)} · {fmt_versts(ca)}"),
                    ("stat", "Вассалаты"), ("num", f"{self.fmt_people(vp, step)} · {fmt_versts(va)}")]
        elif fr.get("ev"):
            st = h.steps[fr["ev"] - 1]
            ev = st["event"]
            if phase == "fly":
                alpha = ease((tt - 0.65) / 0.35)
            body = ([("kind", ev["kind"])] if ev.get("kind") else []) + [("title", ev["title"]), ("text", ev["text"])]
            if phase in ("trans", "hold"):
                k = fr["ev"]
                conf = h.configs[k]
                for s in st["targets"]:
                    pop, area = h.stats(conf, s)
                    body.append(("stat", self.sname(s, k)[0]))
                    body.append(("num", f"{self.fmt_people(pop, k)} · {fmt_versts(area)}"))
                if st["before"] and st["changed"].any():
                    names = []
                    for s in st["before"]:
                        nm = self.sname(s, k - 1)[0]
                        if nm not in names:
                            names.append(nm)
                    body.append(("members", "изъ: " + ", ".join(names)))
                if st["changed"].any():
                    cp, ca, vp, va = self.union_totals(k)
                    line = f"Въ Союзѣ: {self.fmt_people(cp, k)} · {fmt_versts(ca)}"
                    body.append(("total", line))
        elif phase == "fly":
            alpha = 0.0
        if phase == "fly" and fr.get("ev") is None:
            alpha = 0.0
        spec = {"kind": (14, True, False, RED, 0.14), "title": (27, True, False, INK, 0),
                "sub": (17, False, True, INK_SOFT, 0), "text": (18, False, False, INK, 0),
                "stat": (18, True, False, RED, 0), "num": (16, False, False, INK, 0),
                "members": (14.5, False, True, INK_SOFT, 0), "total": (15, True, False, INK_SOFT, 0)}
        gap_after = {"kind": 2, "title": 8, "sub": 4, "text": 8, "stat": 0, "num": 6, "members": 6, "total": 4}
        lines = []
        for kind, s in body:
            fs, bold, italic, col, sp = spec[kind]
            if kind == "kind":
                lines.append((s.upper(), fs, bold, italic, col, sp))
            else:
                for ln in self.wrap2(ctx, s, fs, PW - 44, bold, italic):
                    lines.append((ln, fs, bold, italic, col, sp))
            lines.append(("", gap_after[kind], False, False, INK, 0))
        note = self.sc.get("note", "")
        note_lines = self.wrap2(ctx, note, 12.5, PW - 44, False, True) if note and phase != "fly" else []
        box_h = 188 + sum(l[1] * 1.3 for l in lines) + (len(note_lines) * 16 + 10 if note_lines else 0)
        a = max(alpha, 0.0)
        box_h = box_h if a > 0 else 188
        # card with shadow and double rule
        ctx.new_path()
        ctx.rectangle(X + 7, Y + 10, PW, box_h)
        ctx.set_source_rgba(0.25, 0.18, 0.10, 0.22)
        ctx.fill()
        ctx.new_path()
        ctx.rectangle(X, Y, PW, box_h)
        ctx.set_source_rgba(*CARD, 0.97)
        ctx.fill()
        for inset, lwid in ((8, 1.6), (12, 0.6)):
            ctx.new_path()
            ctx.rectangle(X + inset, Y + inset, PW - 2 * inset, box_h - 2 * inset)
            ctx.set_source_rgba(*INK, 0.75)
            ctx.set_line_width(lwid)
            ctx.stroke()
        hdr = self.sc.get("header", "Р.С.Ф.Г.Р.")
        wh = self.tw(ctx, hdr, 13, True, spacing=0.22)
        self.put(ctx, hdr, X + PW / 2 - wh / 2, Y + 38, 13, rgb=RED, bold=True, spacing=0.22)
        ys = f"{yi}"
        self.put(ctx, ys, X + 24, Y + 128, 84, rgb=RED, face=CONDENSED, bold=True)
        wy = self.tw(ctx, ys, 84, True, face=CONDENSED)
        sp_txt = f"Споролѣтіе {roman(yi - 1920)}" if yi >= 1921 else "канунъ Споролѣтія"
        self.put(ctx, sp_txt, X + 34 + wy, Y + 86, 19, rgb=INK, italic=True)
        cal = self.sc.get("second_calendar")
        if cal and yi >= cal["from"]:
            self.put(ctx, f"{yi - cal['from'] + 1}-й {cal['name']}", X + 34 + wy, Y + 112, 15, rgb=INK_SOFT, italic=True)
        ctx.new_path()
        ctx.move_to(X + 24, Y + 152)
        ctx.line_to(X + PW - 24, Y + 152)
        ctx.set_source_rgba(*RED, 0.8)
        ctx.set_line_width(1.4)
        ctx.stroke()
        yy = Y + 184
        for ln, fs, bold, italic, col, sp in lines:
            if ln:
                self.put(ctx, ln, X + 24, yy + fs * 0.2, fs, rgb=col, alpha=a, bold=bold, italic=italic, spacing=sp)
            yy += fs * 1.3
        for j, ln in enumerate(note_lines):
            self.put(ctx, ln, X + 24, yy + 4 + j * 16, 12.5, rgb=INK_SOFT, alpha=0.9 * a, italic=True)

    def draw_atimeline(self, ctx, fr):
        sc = self.sc
        x0, x1, y = 90, 1830, H - 46
        y0, y1 = sc["start_year"], sc["end_year"]
        X = lambda yr: x0 + (yr - y0) / (y1 - y0) * (x1 - x0)
        year = self.panel_year(fr)
        ctx.new_path()
        ctx.move_to(x0, y)
        ctx.line_to(x1, y)
        ctx.set_source_rgba(*INK, 0.55)
        ctx.set_line_width(1.6)
        ctx.stroke()
        ctx.new_path()
        ctx.move_to(x0, y)
        ctx.line_to(X(year), y)
        ctx.set_source_rgba(*RED, 0.9)
        ctx.set_line_width(3.0)
        ctx.stroke()
        for d in range(y0, y1 + 1, 5):
            ctx.new_path()
            ctx.move_to(X(d), y - 6)
            ctx.line_to(X(d), y + 6)
            ctx.set_source_rgba(*INK, 0.6)
            ctx.set_line_width(1.2)
            ctx.stroke()
            s = str(d)
            self.put(ctx, s, X(d) - self.tw(ctx, s, 14) / 2, y + 26, 14, rgb=INK_SOFT)
        for ev in sc["events"]:
            done = ev["year"] <= year + 1e-6
            ctx.new_path()
            ctx.arc(X(ev["year"]), y, 4.5, 0, 2 * math.pi)
            ctx.set_source_rgba(*(RED if done else (0.55, 0.48, 0.38)), 1)
            ctx.fill()
        self.draw_star(ctx, X(year), y, 11, 1.0, spiral=True)


def render_segment(scen, frames, path):
    h = History(scen)
    r = ArchiveRenderer(h)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    t0 = time.time()
    for k, fr in enumerate(frames):
        img = r.frame(fr)
        p.stdin.write(img.tobytes())
        if k % 100 == 0:
            print(f"  [{os.path.basename(path)}] {k}/{len(frames)} {(time.time() - t0) / (k + 1):.2f} s/frame", flush=True)
    p.stdin.close()
    p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--preview", nargs="*", type=int)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    ap.add_argument("--name", default="archive")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    h = History(a.scenario)
    for wmsg in h.warnings:
        print("WARNING", wmsg)
    plan = build_plan(h)
    print(f"frames {len(plan)} = {len(plan) / FPS:.1f} s")
    if a.plan:
        cur = None
        for fr in plan:
            key = (fr["phase"], fr.get("ev"))
            if key != cur:
                print(f"  {fr['frame']:5d}  {fr['phase']:6s} ev={fr.get('ev')}  {fr['n']} frames")
                cur = key
        return
    if a.preview is not None:
        r = ArchiveRenderer(h)
        for k in a.preview:
            t0 = time.time()
            img = r.frame(plan[k])
            surf = cairo.ImageSurface.create_for_data(memoryview(img), cairo.FORMAT_ARGB32, W, H, W * 4)
            surf.write_to_png(os.path.join(OUT, f"{a.name}_preview_{k:05d}.png"))
            print(f"preview {k} ({plan[k]['phase']}, ev={plan[k].get('ev')}) {time.time() - t0:.2f} s")
        return
    nw = a.workers
    bounds = np.linspace(0, len(plan), nw + 1).astype(int)
    procs, segs = [], []
    for k in range(nw):
        seg = os.path.join(OUT, f"{a.name}_seg_{k}.mp4")
        segs.append(seg)
        pr = Process(target=render_segment, args=(a.scenario, plan[bounds[k]:bounds[k + 1]], seg))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = os.path.join(OUT, f"{a.name}_segs.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    mp4 = os.path.join(OUT, a.name + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", mp4], check=True)
    for s in segs:
        os.remove(s)
    os.remove(lst)
    print("done:", mp4)


if __name__ == "__main__":
    main()
