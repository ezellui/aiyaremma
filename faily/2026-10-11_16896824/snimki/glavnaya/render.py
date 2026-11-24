#!/usr/bin/env python3
"""Render the scenario as a flying-globe video.

  python3 render.py                       # full video -> out/future_borders.mp4 (+ .gif)
  python3 render.py --preview 120 900     # selected frame numbers -> out/preview_*.png
  python3 render.py --plan                # print the timeline only

The globe is an orthographic view. Fills come from an equirectangular texture
(region index raster coloured per configuration); borders, coastlines, cities and labels
are drawn as antialiased vectors over it, so they stay sharp at any zoom.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from multiprocessing import Process

import cairo
import numpy as np

from history import History, hex2rgb

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "out")

W, H, FPS = 1920, 1080, 30
GX, GY, R0 = 720, 540, 430          # globe centre on screen and radius at zoom 1
OCEAN = (28, 58, 92)
LAKE = (44, 84, 122)
ACCENT = (1.0, 0.80, 0.38)
FONT = "Inter"
FONT_DISPLAY = "Inter Display"
SEC = lambda s: int(round(s * FPS))


# ----------------------------------------------------------------------------- maths
def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=-1)


def basis(lon, lat):
    """forward (towards the viewer), east, north unit vectors of a camera looking at lon/lat."""
    f = unit(lon, lat)
    lo, la = math.radians(lon), math.radians(lat)
    e = np.array([-math.sin(lo), math.cos(lo), 0.0])
    n = np.array([-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)])
    return f, e, n


def slerp(a, b, t):
    d = float(np.clip(np.dot(a, b), -1, 1))
    om = math.acos(d)
    if om < 1e-6:
        return a
    return (math.sin((1 - t) * om) * a + math.sin(t * om) * b) / math.sin(om)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def fmt_pop(p):
    if p >= 1e9:
        return f"{p / 1e9:.2f} млрд".replace(".", ",")
    if p >= 1e6:
        return f"{p / 1e6:.1f} млн".replace(".", ",")
    if p >= 1e3:
        return f"{p / 1e3:.0f} тыс."
    return str(int(p))


def fmt_area(a):
    if a >= 1e6:
        return f"{a / 1e6:.2f} млн км²".replace(".", ",")
    if a >= 1e3:
        return f"{a / 1e3:.1f} тыс. км²".replace(".", ",")
    return f"{a:.0f} км²"


# ----------------------------------------------------------------------------- timeline
def build_plan(h):
    sc = h.sc
    frames = []
    cam_prev = sc["intro"]["camera"]
    year_prev = sc["start_year"]

    def add(n, **kw):
        for i in range(n):
            d = dict(kw)
            d["i"] = i
            d["n"] = n
            frames.append(d)

    # intro
    add(SEC(3.2), phase="intro", cam0=cam_prev, cam1=cam_prev, step=0, year0=year_prev, year1=year_prev)
    for k, ev in enumerate(sc["events"], start=1):
        cam = ev["camera"]
        ang = math.acos(float(np.clip(np.dot(unit(*cam_prev[:2]), unit(*cam[:2])), -1, 1)))
        fly = SEC(1.4 + 1.3 * ang / math.pi + 0.15 * abs(math.log(cam[2] / cam_prev[2])))
        add(fly, phase="fly", cam0=cam_prev, cam1=cam, step=k - 1, ev=k, year0=year_prev, year1=ev["year"], ang=ang)
        add(SEC(0.7), phase="pre", cam0=cam, cam1=cam, step=k - 1, ev=k, year0=ev["year"], year1=ev["year"])
        add(SEC(1.7), phase="trans", cam0=cam, cam1=cam, step=k, ev=k, year0=ev["year"], year1=ev["year"])
        add(SEC(2.4), phase="hold", cam0=cam, cam1=cam, step=k, ev=k, year0=ev["year"], year1=ev["year"])
        cam_prev, year_prev = cam, ev["year"]
    oc = sc["outro"]["camera"]
    ang = math.acos(float(np.clip(np.dot(unit(*cam_prev[:2]), unit(*oc[:2])), -1, 1)))
    last = len(sc["events"])
    add(SEC(2.2), phase="fly", cam0=cam_prev, cam1=oc, step=last, ev=None, year0=year_prev, year1=sc["end_year"], ang=ang)
    add(SEC(6.0), phase="outro", cam0=oc, cam1=oc, step=last, year0=sc["end_year"], year1=sc["end_year"])
    for j, f in enumerate(frames):
        f["frame"] = j
    return frames


def camera_at(f):
    t = (f["i"] + 0.5) / f["n"]
    c0, c1 = f["cam0"], f["cam1"]
    if f["phase"] == "fly":
        e = ease_io(t)
        v = slerp(unit(c0[0], c0[1]), unit(c1[0], c1[1]), e)
        lon, lat = math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(np.clip(v[2], -1, 1)))
        lz = (1 - e) * math.log(c0[2]) + e * math.log(c1[2])
        # pull back mid-flight on long hops, like a plane climbing
        bump = 1 + (0.9 * f["ang"] / math.pi + 0.15 * abs(math.log(c1[2] / c0[2]))) * math.sin(math.pi * e)
        return lon, lat, math.exp(lz) / bump
    # slow drift while holding, slower when zoomed in
    drift = 0.0
    if f["phase"] in ("pre", "trans", "hold"):
        base = {"pre": 0, "trans": SEC(0.7), "hold": SEC(2.4)}[f["phase"]]
        drift = (base + f["i"]) / FPS * 0.9 / c1[2]
    if f["phase"] == "outro":
        drift = f["i"] / FPS * 6.0
    if f["phase"] == "intro":
        drift = f["i"] / FPS * 2.5
    return c1[0] + drift, c1[1], c1[2]


# ----------------------------------------------------------------------------- renderer
class Renderer:
    def __init__(self, h):
        self.h = h
        self.index = np.load(os.path.join(CACHE, "index.npy"))
        self.TH, self.TW = self.index.shape
        lk = os.path.join(CACHE, "lakes.npy")
        self.lakes = np.unpackbits(np.load(lk), axis=1)[:, :self.TW].astype(bool) if os.path.exists(lk) else None
        a = np.load(os.path.join(CACHE, "arcs.npz"))
        xy = a["xy"].astype(np.float64)
        self.arc_xyz = unit(xy[:, 0], xy[:, 1]).astype(np.float32)
        self.arc_off = np.r_[0, np.cumsum(a["lens"])]
        self.arc_id = np.repeat(np.arange(len(a["lens"])), a["lens"])
        self.left, self.right = a["left"], a["right"]
        self.reg_label = unit(np.array([r["label"][0] for r in h.regions]), np.array([r["label"][1] for r in h.regions]))
        self.cities = json.load(open(os.path.join(CACHE, "cities.json"), encoding="utf-8"))
        self.city_xyz = unit(np.array([c["lon"] for c in self.cities]), np.array([c["lat"] for c in self.cities]))
        self.city_rank = np.array([c["rank"] for c in self.cities])
        self._tex = {}
        self._labels = {}
        self.bg = self._background()

    # -- textures ------------------------------------------------------------------------
    def texture(self, step):
        if step in self._tex:
            return self._tex[step]
        if len(self._tex) >= 2:
            self._tex.pop(next(iter(self._tex)))
        conf = self.h.configs[step]
        pal = self.h.palette_rgb(step)
        reg_rgb = np.vstack([pal[conf], np.array([OCEAN], dtype=np.uint8)])  # last row = sea
        idx = self.index.astype(np.int32)
        idx[idx < 0] = len(conf)
        tex = np.empty((self.TH, self.TW, 4), dtype=np.uint8)
        tex[..., :3] = reg_rgb[idx]
        tex[..., 3] = np.where(idx < len(conf), 255, 0)
        if self.lakes is not None:
            tex[self.lakes, :3] = LAKE
            tex[self.lakes, 3] = 0
        self._tex[step] = tex
        return tex

    def sample(self, tex, lon, lat):
        x = (lon + 180.0) / 360.0 * self.TW - 0.5
        y = (90.0 - lat) / 180.0 * self.TH - 0.5
        x0 = np.floor(x)
        y0 = np.floor(y)
        fx = (x - x0)[:, None]
        fy = (y - y0)[:, None]
        x0 = x0.astype(np.int64) % self.TW
        x1 = (x0 + 1) % self.TW
        y0 = np.clip(y0.astype(np.int64), 0, self.TH - 1)
        y1 = np.clip(y0 + 1, 0, self.TH - 1)
        c00 = tex[y0, x0].astype(np.float32)
        c10 = tex[y0, x1].astype(np.float32)
        c01 = tex[y1, x0].astype(np.float32)
        c11 = tex[y1, x1].astype(np.float32)
        return (c00 * (1 - fx) + c10 * fx) * (1 - fy) + (c01 * (1 - fx) + c11 * fx) * fy

    def _background(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - GX) ** 2 + (yy - GY) ** 2) / 1400
        top = np.array([16, 24, 40], np.float32)
        bot = np.array([5, 8, 15], np.float32)
        img = top * (1 - d[..., None]).clip(0, 1) + bot * d[..., None].clip(0, 1)
        rng = np.random.default_rng(7)
        for _ in range(900):
            x, y = rng.integers(0, W), rng.integers(0, H)
            b = rng.uniform(60, 200)
            img[y, x] = np.maximum(img[y, x], b)
        bgra = np.empty((H, W, 4), np.uint8)
        bgra[..., 0] = img[..., 2]
        bgra[..., 1] = img[..., 1]
        bgra[..., 2] = img[..., 0]
        bgra[..., 3] = 255
        return bgra

    # -- globe raster ------------------------------------------------------------------------
    def globe(self, frame, lon0, lat0, R, steps, t):
        f, e, n = basis(lon0, lat0)
        x0, x1 = max(0, int(GX - R - 2)), min(W, int(GX + R + 3))
        y0, y1 = max(0, int(GY - R - 2)), min(H, int(GY + R + 3))
        if x0 >= x1 or y0 >= y1:
            return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        u = (xx + 0.5 - GX) / R
        v = (GY - yy - 0.5) / R
        rho2 = u * u + v * v
        inside = rho2 < 1.0 + 2.0 / R
        u, v = u[inside], v[inside]
        rho2 = np.minimum(rho2[inside], 1.0)
        w = np.sqrt(1.0 - rho2)
        P = u[:, None] * e + v[:, None] * n + w[:, None] * f
        lon = np.degrees(np.arctan2(P[:, 1], P[:, 0]))
        lat = np.degrees(np.arcsin(np.clip(P[:, 2], -1, 1)))
        c = self.sample(self.texture(steps[0]), lon, lat)
        if steps[1] != steps[0] and t > 0:
            c2 = self.sample(self.texture(steps[1]), lon, lat)
            c = c * (1 - t) + c2 * t
        rgb, land = c[:, :3], c[:, 3:4] / 255.0
        # lighting: soft Lambert from the upper left, ocean glint, limb darkening, atmosphere
        L = np.array([-0.42, 0.52, 0.74])
        L = L / np.linalg.norm(L)
        ndl = np.clip(u * L[0] + v * L[1] + w * L[2], 0, 1)[:, None]
        Hh = L + np.array([0, 0, 1.0])
        Hh = Hh / np.linalg.norm(Hh)
        spec = (np.clip(u * Hh[0] + v * Hh[1] + w * Hh[2], 0, 1) ** 70)[:, None] * (1 - land) * 110
        shade = 0.50 + 0.62 * ndl
        rgb = rgb * shade + spec
        rim = ((1 - w) ** 3)[:, None]
        rgb = rgb * (1 - 0.45 * rim) + np.array([110, 165, 235], np.float32) * 0.45 * rim
        rgb = np.clip(rgb, 0, 255)
        # antialiased disk edge
        rho = np.sqrt(u * u + v * v)
        a = np.clip((1.0 - rho) * R + 0.5, 0, 1)[:, None]
        view = frame[y0:y1, x0:x1]
        sub = view[inside].astype(np.float32)
        bgr = rgb[:, ::-1]
        sub[:, :3] = sub[:, :3] * (1 - a) + bgr * a
        view[inside] = sub.astype(np.uint8)

    # -- vectors -------------------------------------------------------------------------------
    def project(self, xyz, f, e, n, R):
        u = xyz @ e
        v = xyz @ n
        w = xyz @ f
        return GX + R * u, GY - R * v, w

    def arc_classes(self, step):
        conf = self.h.configs[step]
        l, r = self.left, self.right
        sl = conf[l]
        sr = np.where(r >= 0, conf[np.maximum(r, 0)], -1)
        coast = r < 0
        state = (~coast) & (sl != sr)
        inner = (~coast) & (sl == sr)
        return coast, state, inner

    def draw_arcs(self, ctx, sel, sx, sy, w, vis_pt):
        """append visible pieces of the selected arcs to the current path."""
        for a in np.nonzero(sel)[0]:
            o0, o1 = self.arc_off[a], self.arc_off[a + 1]
            vp = vis_pt[o0:o1]
            if not vp.any():
                continue
            X, Y = sx[o0:o1], sy[o0:o1]
            pen = False
            for j in range(o1 - o0):
                if vp[j]:
                    if pen:
                        ctx.line_to(X[j], Y[j])
                    else:
                        ctx.move_to(X[j], Y[j])
                        pen = True
                else:
                    pen = False

    def state_labels(self, step):
        """label anchor per state: the region label point nearest the area-weighted centre."""
        if step in self._labels:
            return self._labels[step]
        conf = self.h.configs[step]
        out = {}
        area = self.h.area
        for s in np.unique(conf):
            m = np.nonzero(conf == s)[0]
            wts = area[m]
            c = (self.reg_label[m] * wts[:, None]).sum(0)
            if np.linalg.norm(c) < 1e-9:
                c = self.reg_label[m[0]]
            c = c / np.linalg.norm(c)
            big = m[wts >= np.quantile(wts, 0.5)]
            j = big[np.argmax(self.reg_label[big] @ c)]
            out[int(s)] = (self.reg_label[j], float(wts.sum()), int(self.h.pop[m].sum()))
        self._labels[step] = out
        return out

    # -- one frame -------------------------------------------------------------------------------
    def frame(self, fr):
        h = self.h
        lon0, lat0, zoom = camera_at(fr)
        R = R0 * zoom
        phase = fr["phase"]
        t = 0.0
        sa = sb = fr["step"]
        if phase == "trans":
            sa, sb = fr["step"] - 1, fr["step"]
            t = ease((fr["i"] + 0.5) / fr["n"])
        img = self.bg.copy()
        self.globe(img, lon0, lat0, R, (sa, sb), t)

        surf = cairo.ImageSurface.create_for_data(memoryview(img), cairo.FORMAT_ARGB32, W, H, W * 4)
        ctx = cairo.Context(surf)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        # atmosphere halo
        if R < 2.5 * W:
            g = cairo.RadialGradient(GX, GY, R * 0.985, GX, GY, R * 1.10)
            g.add_color_stop_rgba(0, 0.45, 0.68, 1.0, 0.42)
            g.add_color_stop_rgba(1, 0.45, 0.68, 1.0, 0.0)
            ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            ctx.arc(GX, GY, R * 1.10, 0, 2 * math.pi)
            ctx.arc(GX, GY, R * 0.995, 0, 2 * math.pi)
            ctx.set_source(g)
            ctx.fill()
            ctx.set_fill_rule(cairo.FILL_RULE_WINDING)

        f, e, n = basis(lon0, lat0)
        sx, sy, w = self.project(self.arc_xyz, f, e, n, R)
        onscreen = (sx > -50) & (sx < W + 50) & (sy > -50) & (sy < H + 50)
        vis_pt = (w > 0.0) & onscreen
        arc_vis = np.maximum.reduceat(vis_pt, self.arc_off[:-1]).astype(bool)
        lw = 1.0 + 0.32 * math.log2(max(zoom, 1.0))

        ca, sta, ina = self.arc_classes(sa)
        cb, stb, inb = self.arc_classes(sb)
        # internal (admin-1) borders fade in as we zoom
        a_in = min(1.0, max(0.0, (zoom - 1.25) / 1.2)) * 0.30
        if a_in > 0.01:
            ctx.set_line_width(0.6 * lw)
            sel = arc_vis & (ina | inb) & ~(sta | stb)
            ctx.set_source_rgba(0.18, 0.16, 0.14, a_in)
            self.draw_arcs(ctx, sel, sx, sy, w, vis_pt)
            ctx.stroke()
        # coastlines
        ctx.set_line_width(0.75 * lw)
        ctx.set_source_rgba(0.10, 0.20, 0.30, 0.55)
        self.draw_arcs(ctx, arc_vis & ca, sx, sy, w, vis_pt)
        ctx.stroke()
        # state borders: stable ones, fading-out ones, fading-in ones
        for sel, alpha in ((sta & stb, 1.0), (sta & ~stb, 1 - t), (stb & ~sta, t)):
            if alpha <= 0.01:
                continue
            sel = sel & arc_vis
            ctx.set_line_width(2.4 * lw)
            ctx.set_source_rgba(1, 1, 1, 0.22 * alpha)
            self.draw_arcs(ctx, sel, sx, sy, w, vis_pt)
            ctx.stroke()
            ctx.set_line_width(1.05 * lw)
            ctx.set_source_rgba(0.22, 0.17, 0.15, 0.85 * alpha)
            self.draw_arcs(ctx, sel, sx, sy, w, vis_pt)
            ctx.stroke()

        # highlight of the area that changes in this event
        ev = fr.get("ev")
        hi = 0.0
        if ev and phase in ("pre", "trans", "hold"):
            k = fr["i"] / FPS
            if phase == "pre":
                hi = 0.6 * ease(k / 0.5)
            elif phase == "trans":
                hi = 0.6 + 0.4 * ease(k / 0.6)
            else:
                hi = 1.0 - ease((k - 1.6) / 0.8)
            pulse = 0.65 + 0.35 * math.sin((fr["frame"] / FPS) * 2 * math.pi * 0.9)
            st = h.steps[ev - 1]
            mask = st["changed"] if st["changed"].any() else np.isin(h.configs[ev], st["targets"])
            ml = mask[self.left]
            mr = np.where(self.right >= 0, mask[np.maximum(self.right, 0)], False)
            sel = arc_vis & (ml != mr)
            for width, alpha in ((7.0, 0.22), (3.0, 0.5), (1.4, 0.95)):
                ctx.set_line_width(width * lw)
                ctx.set_source_rgba(*ACCENT, alpha * hi * pulse)
                self.draw_arcs(ctx, sel, sx, sy, w, vis_pt)
                ctx.stroke()

        self.draw_cities(ctx, f, e, n, R, zoom, fr)
        self.draw_state_labels(ctx, f, e, n, R, zoom, fr, sa, sb, t)
        self.draw_panel(ctx, fr)
        self.draw_timeline(ctx, fr)
        surf.flush()
        return img

    # -- cities & capitals --------------------------------------------------------------------
    def draw_cities(self, ctx, f, e, n, R, zoom, fr):
        sx, sy, w = self.project(self.city_xyz, f, e, n, R)
        maxrank = 2 if zoom < 1.6 else (4 if zoom < 3 else 7)
        sel = (w > 0.12) & (self.city_rank <= maxrank) & (sx > 0) & (sx < W) & (sy > 0) & (sy < H)
        r = 1.6 + 0.4 * math.log2(max(zoom, 1))
        for j in np.nonzero(sel)[0]:
            ctx.arc(sx[j], sy[j], r, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.75 * min(1, w[j] * 3))
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.1, 0.12, 0.6)
            ctx.set_line_width(0.8)
            ctx.stroke()
        # capitals of the states created in the story
        step = fr["step"]
        for s, st in enumerate(self.h.states_by_idx):
            cap = st.get("capital")
            if not cap or st["origin"] != "event":
                continue
            created = next(k for k, s2 in enumerate(self.h.steps, start=1)
                           if s in s2["targets"] and s2["event"]["year"] == st["created"])
            if step < created:
                continue
            if not (self.h.configs[step] == s).any():
                continue  # absorbed later
            alpha = 1.0
            if fr["phase"] == "trans" and step == created:
                alpha = ease((fr["i"] + 0.5) / fr["n"] * 1.4 - 0.4)
            p = unit(cap["lon"], cap["lat"])
            x, y = GX + R * (p @ e), GY - R * (p @ n)
            if p @ f < 0.1 or not (0 < x < W and 0 < y < H):
                continue
            rr = 4.5 + 0.8 * math.log2(max(zoom, 1))
            ctx.set_source_rgba(0.12, 0.10, 0.10, 0.85 * alpha)
            ctx.arc(x, y, rr + 1.6, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgba(*ACCENT, alpha)
            ctx.arc(x, y, rr, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgba(0.12, 0.10, 0.10, alpha)
            ctx.arc(x, y, rr * 0.38, 0, 2 * math.pi)
            ctx.fill()
            focus = fr.get("ev") and s in self.h.steps[fr["ev"] - 1]["targets"] and fr["phase"] != "fly"
            if zoom >= 1.5 or focus:
                self.text(ctx, cap["ru"], x + rr + 5, y + 5, 15 + (3 if focus else 0), bold=focus,
                          rgb=(1, 1, 1), halo=(0.08, 0.08, 0.1), alpha=alpha)

    # -- labels ---------------------------------------------------------------------------------
    def text(self, ctx, s, x, y, size, bold=False, rgb=(1, 1, 1), halo=None, alpha=1.0, face=None, halo_w=3.2):
        ctx.select_font_face(face or FONT, cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)
        ctx.move_to(x, y)
        ctx.text_path(s)
        if halo is not None:
            ctx.set_source_rgba(*halo, 0.55 * alpha)
            ctx.set_line_width(halo_w)
            ctx.stroke_preserve()
        ctx.set_source_rgba(*rgb, alpha)
        ctx.fill()

    def measure(self, ctx, s, size, bold=False, face=None):
        ctx.select_font_face(face or FONT, cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(size)
        return ctx.text_extents(s).x_advance

    def draw_state_labels(self, ctx, f, e, n, R, zoom, fr, sa, sb, t):
        placed = []
        targets = set()
        befores = set()
        if fr.get("ev") and fr["phase"] in ("pre", "trans", "hold"):
            st = self.h.steps[fr["ev"] - 1]
            targets = set(st["targets"])
            befores = set(st["before"])
        layers = [(sb, t if sa != sb else 1.0)]
        if sa != sb:
            layers.insert(0, (sa, 1 - t))
        for step, alpha in layers:
            if alpha < 0.03:
                continue
            labels = self.state_labels(step)
            cands = []
            for s, (p, area, pop) in labels.items():
                ww = float(p @ f)
                if ww < 0.2:
                    continue
                x, y = GX + R * float(p @ e), GY - R * float(p @ n)
                if not (40 < x < W - 40 and 40 < y < H - 60):
                    continue
                size_px = math.sqrt(area) / 6371.0 * R * (0.4 + 0.6 * ww)
                imp = size_px * (3 if s in targets else 1)
                cands.append((imp, s, x, y, size_px))
            cands.sort(reverse=True)
            for imp, s, x, y, size_px in cands[:60]:
                is_t = s in targets and step == sb
                fs = min(30 if is_t else 22, max(11, size_px / 7))
                full, short = self.h.name(s, step)
                name = full
                tw = self.measure(ctx, name, fs, bold=is_t)
                if tw > size_px * 1.4 and not is_t:
                    name = short
                    tw = self.measure(ctx, name, fs, bold=is_t)
                if tw > size_px * 1.6 and not is_t:
                    continue
                if is_t and tw > 560:
                    name = short
                    tw = self.measure(ctx, name, fs, bold=True)
                rect = (x - tw / 2 - 4, y - fs, x + tw / 2 + 4, y + 6)
                if any(not (rect[2] < q[0] or rect[0] > q[2] or rect[3] < q[1] or rect[1] > q[3]) for q in placed):
                    continue
                if x + tw / 2 > 1430 and fr["phase"] != "fly" and y < 900:
                    continue  # keep clear of the side panel
                placed.append(rect)
                a = alpha * (1.0 if is_t else 0.85)
                if s in befores and step == sa and sa != sb:
                    a = alpha
                self.text(ctx, name, x - tw / 2, y, fs, bold=is_t, rgb=(0.13, 0.12, 0.12),
                          halo=(1, 1, 1), alpha=a, halo_w=3.0)

    # -- side panel & timeline ---------------------------------------------------------------------
    def wrap(self, ctx, s, size, width, bold=False):
        words, lines, cur = s.split(), [], ""
        for wd in words:
            nxt = (cur + " " + wd).strip()
            if self.measure(ctx, nxt, size, bold) <= width:
                cur = nxt
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def draw_panel(self, ctx, fr):
        h = self.h
        phase = fr["phase"]
        X, Y, PW = 1450, 70, 410
        # year counter (always)
        tt = (fr["i"] + 0.5) / fr["n"]
        year = fr["year0"] + (fr["year1"] - fr["year0"]) * (ease_io(tt) if phase == "fly" else 1.0)
        body = []  # list of (kind, text)
        alpha = 1.0
        if phase == "intro":
            alpha = ease(fr["i"] / SEC(0.6))
            body = [("title", h.sc["title"]), ("sub", h.sc["subtitle"]), ("text", h.sc["intro"]["text"])]
        elif phase == "outro":
            alpha = ease(fr["i"] / SEC(0.6))
            n0 = len(np.unique(h.configs[0]))
            n1 = len(np.unique(h.configs[-1]))
            new = [s for s, st in enumerate(h.states_by_idx)
                   if st["origin"] == "event" and (h.configs[-1] == s).any()]
            body = [("title", "Итог"), ("text", h.sc["outro"]["text"]),
                    ("stat", f"Государств и территорий на карте: {n0} → {n1}"),
                    ("members", "Новые государства: " + ", ".join(h.name(s, len(h.configs) - 1)[0] for s in new) + ".")]
        elif fr.get("ev"):
            st = h.steps[fr["ev"] - 1]
            ev = st["event"]
            if phase == "fly":
                alpha = ease((tt - 0.65) / 0.35)
            body = [("title", ev["title"]), ("text", ev["text"])]
            if phase in ("trans", "hold"):
                k = len(h.configs) and fr["ev"]
                conf = h.configs[k]
                for s in st["targets"]:
                    pop, area = h.stats(conf, s)
                    body.append(("stat", h.name(s, k)[0]))
                    body.append(("num", f"население {fmt_pop(pop)} · {fmt_area(area)}"))
                if st["before"] and st["changed"].any():
                    body.append(("members", "из: " + ", ".join(h.name(s, k - 1)[0] for s in st["before"])))
        elif phase == "fly":
            alpha = 0.0
        # fade out at the start of the next flight
        if phase == "fly" and fr.get("ev") is None:
            alpha = 0.0
        # panel box
        lines = []
        for kind, s in body:
            spec = {"title": (31, True, (1, 1, 1)), "sub": (19, False, (0.70, 0.75, 0.82)),
                    "text": (19, False, (0.82, 0.86, 0.91)), "stat": (20, True, ACCENT),
                    "num": (17, False, (0.86, 0.88, 0.92)), "members": (15, False, (0.62, 0.67, 0.74))}[kind]
            for ln in self.wrap(ctx, s, spec[0], PW - 40, spec[1]):
                lines.append((ln, spec))
            lines.append(("", (8 if kind in ("title", "text", "members", "num") else 2, False, (1, 1, 1))))
        box_h = 175 + sum(sp[0] * 1.32 for _, sp in lines)
        a = max(alpha, 0.0)
        ctx.new_path()
        self.round_rect(ctx, X, Y, PW, box_h if a > 0 else 175, 14)
        ctx.set_source_rgba(0.04, 0.07, 0.12, 0.74)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.08)
        ctx.set_line_width(1)
        ctx.stroke()
        self.text(ctx, "ГРАНИЦЫ БУДУЩЕГО", X + 20, Y + 34, 13, bold=True, rgb=(0.55, 0.62, 0.72))
        self.text(ctx, f"{int(round(year))}", X + 18, Y + 140, 104, bold=True, rgb=ACCENT, face=FONT_DISPLAY)
        yy = Y + 186
        for ln, (size, bold, rgb) in lines:
            if ln:
                self.text(ctx, ln, X + 20, yy + size * 0.2, size, bold=bold, rgb=rgb, alpha=a)
            yy += size * 1.32
        self.text(ctx, h.sc.get("note", ""), X + 20, H - 92, 12, rgb=(0.55, 0.6, 0.67), alpha=0.9)

    def round_rect(self, ctx, x, y, w, hh, r):
        ctx.move_to(x + r, y)
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + hh - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + hh - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

    def draw_timeline(self, ctx, fr):
        sc = self.h.sc
        x0, x1, y = 90, 1830, H - 42
        y0, y1 = sc["start_year"], sc["end_year"]
        X = lambda yr: x0 + (yr - y0) / (y1 - y0) * (x1 - x0)
        tt = (fr["i"] + 0.5) / fr["n"]
        year = fr["year0"] + (fr["year1"] - fr["year0"]) * (ease_io(tt) if fr["phase"] == "fly" else 1.0)
        g = cairo.LinearGradient(0, H - 110, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
        ctx.rectangle(0, H - 110, W, 110)
        ctx.set_source(g)
        ctx.fill()
        ctx.set_line_width(2)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.move_to(x0, y)
        ctx.line_to(x1, y)
        ctx.stroke()
        ctx.set_source_rgba(*ACCENT, 0.9)
        ctx.move_to(x0, y)
        ctx.line_to(X(year), y)
        ctx.stroke()
        for d in range(y0, y1 + 1, 10):
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.move_to(X(d), y - 6)
            ctx.line_to(X(d), y + 6)
            ctx.stroke()
            tw = self.measure(ctx, str(d), 13)
            self.text(ctx, str(d), X(d) - tw / 2, y + 24, 13, rgb=(0.7, 0.74, 0.8))
        for k, ev in enumerate(sc["events"], start=1):
            done = ev["year"] <= year + 1e-6
            ctx.arc(X(ev["year"]), y, 5 if done else 4, 0, 2 * math.pi)
            if done:
                ctx.set_source_rgba(*ACCENT, 1)
            else:
                ctx.set_source_rgba(0.6, 0.65, 0.72, 0.8)
            ctx.fill()
        ctx.arc(X(year), y, 8, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.fill()


# ----------------------------------------------------------------------------- driver
def render_segment(scen, frames, path):
    h = History(scen)
    r = Renderer(h)
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
    ap.add_argument("--scenario", default=os.path.join(HERE, "scenario.json"))
    ap.add_argument("--preview", nargs="*", type=int)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    ap.add_argument("--gif-width", type=int, default=640)
    ap.add_argument("--gif-fps", type=int, default=12)
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
        r = Renderer(h)
        for k in a.preview:
            t0 = time.time()
            img = r.frame(plan[k])
            surf = cairo.ImageSurface.create_for_data(memoryview(img), cairo.FORMAT_ARGB32, W, H, W * 4)
            surf.write_to_png(os.path.join(OUT, f"preview_{k:05d}.png"))
            print(f"preview {k} ({plan[k]['phase']}, ev={plan[k].get('ev')}) {time.time() - t0:.2f} s")
        return
    nw = a.workers
    bounds = np.linspace(0, len(plan), nw + 1).astype(int)
    procs, segs = [], []
    for k in range(nw):
        seg = os.path.join(OUT, f"seg_{k}.mp4")
        segs.append(seg)
        pr = Process(target=render_segment, args=(a.scenario, plan[bounds[k]:bounds[k + 1]], seg))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = os.path.join(OUT, "segs.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{s}'\n" for s in segs)
    mp4 = os.path.join(OUT, "future_borders.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", mp4], check=True)
    gif = os.path.join(OUT, "future_borders.gif")
    vf = f"fps={a.gif_fps},scale={a.gif_width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", vf, gif], check=True)
    for s in segs:
        os.remove(s)
    os.remove(lst)
    print("done:", mp4, gif)


if __name__ == "__main__":
    main()
