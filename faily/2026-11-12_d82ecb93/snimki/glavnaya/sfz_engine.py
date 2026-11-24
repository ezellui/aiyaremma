"""Notes of the score played through sfizz (the SFZ engine) from either library's own SFZ mapping.

The score keeps calling Sampler.note(art, midi, t, dur, ...); SfzSampler renders each note dry through
libsfizz (filters, loops, envelopes, velocity zones as the library's SFZ defines them) and then applies the
same transformations as the plain sampler: detune, glissando, reverse, ring modulation, envelope, placement.

  LIB=vsco | sso      which library
  VSCO_SFZ_DIR        folder with the VSCO SFZ files (branch SFZ) next to the sample folders
  SSO_DIR             the clone of github.com/peastman/sso
  SFIZZ_LIB           path to libsfizz.so
"""
import collections
import ctypes
import os

import numpy as np

from sampler import SR, Sampler

SFIZZ_LIB = os.environ.get("SFIZZ_LIB", "libsfizz.so")
VSCO_SFZ = os.environ.get("VSCO_SFZ_DIR", "")
SSO = os.path.join(os.environ.get("SSO_DIR", ""), "Sonatina Symphonic Orchestra")

# articulation of the score → SFZ instruments (the first one whose range holds the note is used)
MAP = {
    "vsco": {
        "vln_sus": ["ViolinEnsSusVib"], "vln_trem": ["ViolinEnsTrem"], "vln_pizz": ["ViolinEnsPizz"],
        "vla_sus": ["ViolaEnsSusVib"], "vla_trem": ["ViolaEnsTrem"], "vla_pizz": ["ViolaEnsPizz"],
        "vc_sus": ["CelloEnsSusVib"], "vc_trem": ["CelloEnsTrem"], "vc_pizz": ["CelloEnsPizz"],
        "cb_sus": ["ContrabassSusVB"], "cb_trem": ["ContrabassTrem"], "cb_pizz": ["ContrabassPizz"],
        "hn_sus": ["FHornSus"], "hn_mute": ["FHornMute"], "tbn_sus": ["TromboneSus"], "tba_sus": ["TubaSus"],
        "tpt_sus": ["TrumpetSus"], "tpt_mute": ["TrumpetStraightMuteSus"],
        "fl_sus": ["FluteSusNV"], "ob_sus": ["OboeSusNV"], "cl_sus": ["ClarinetSus"], "bsn_sus": ["BassoonSus"],
        "harp": ["Harp"], "glock": ["Glockenspiel"],
        "org_loud": ["OrganLoud", "OrganLoudPedal"], "org_quiet": ["OrganQuiet", "OrganQuietPedal"],
        "timp": ["Timpani"], "timp_roll": ["TimpaniRolls"],
    },
    "sso": {
        "vln_sus": ["Strings - Notation/1st Violins Sustain"], "vln_trem": ["Strings - Notation/1st Violins Tremolo"],
        "vln_pizz": ["Strings - Notation/1st Violins Pizzicato"],
        "vla_sus": ["Strings - Notation/Violas Sustain"], "vla_trem": ["Strings - Notation/Violas Tremolo"],
        "vla_pizz": ["Strings - Notation/Violas Pizzicato"],
        "vc_sus": ["Strings - Notation/Celli Sustain"], "vc_trem": ["Strings - Notation/Celli Tremolo"],
        "vc_pizz": ["Strings - Notation/Celli Pizzicato"],
        "cb_sus": ["Strings - Notation/Basses Sustain"], "cb_trem": ["Strings - Notation/Basses Tremolo"],
        "cb_pizz": ["Strings - Notation/Basses Pizzicato"],
        "hn_sus": ["Brass - Notation/Horn Solo Sustain (looped)"],
        "hn_mute": ["Brass - Notation/Horn Solo Sustain (looped)"],          # SSO has no muted horn
        "tbn_sus": ["Brass - Notation/Tenor Trombone Solo Sustain (looped)", "Brass - Notation/Bass Trombone Solo Sustain (looped)"],
        "tba_sus": ["Brass - Notation/Tuba Sustain (looped)"],
        "tpt_sus": ["Brass - Notation/Trumpet Solo Sustain (looped)"],
        "tpt_mute": ["Brass - Notation/Trumpet Solo Marcato"],                # SSO has no muted trumpet
        "fl_sus": ["Woodwinds - Notation/Flute Solo 2 Sustain Non-Vibrato"],
        "ob_sus": ["Woodwinds - Notation/Oboe Solo Sustain (looped)"],
        "cl_sus": ["Woodwinds - Notation/Clarinet Solo Sustain (looped)"],
        "bsn_sus": ["Woodwinds - Notation/Bassoon Solo Sustain (looped)",
                    "Woodwinds - Notation/Contrabassoon Solo Sustain (looped)"],
        "harp": ["Concert Harp"], "glock": ["Percussion/Glockenspiel"],
        "org_loud": ["Organ/Organ All Stops", "Organ/Pedal - Violon 16ft"],
        "org_quiet": ["Organ/Swell - Gedact 8ft", "Organ/Pedal - Bourdon 16ft"],
        "timp": ["Percussion/Timpani"],
    },
}


def sfz_path(lib, name):
    return os.path.join(VSCO_SFZ if lib == "vsco" else SSO, name + ".sfz")


class Sfizz:
    """one libsfizz synth with one instrument loaded"""
    _lib = None

    def __init__(self, path):
        if Sfizz._lib is None:
            L = ctypes.CDLL(SFIZZ_LIB)
            L.sfizz_create_synth.restype = ctypes.c_void_p
            for f, args in [("sfizz_free", [ctypes.c_void_p]),
                            ("sfizz_set_sample_rate", [ctypes.c_void_p, ctypes.c_float]),
                            ("sfizz_set_samples_per_block", [ctypes.c_void_p, ctypes.c_int]),
                            ("sfizz_enable_freewheeling", [ctypes.c_void_p]),
                            ("sfizz_all_sound_off", [ctypes.c_void_p]),
                            ("sfizz_send_note_on", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]),
                            ("sfizz_send_note_off", [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]),
                            ("sfizz_render_block", [ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
                                                    ctypes.c_int, ctypes.c_int])]:
                getattr(L, f).argtypes = args
                getattr(L, f).restype = None
            L.sfizz_load_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            L.sfizz_load_file.restype = ctypes.c_bool
            L.sfizz_get_num_regions.argtypes = [ctypes.c_void_p]
            L.sfizz_get_num_regions.restype = ctypes.c_int
            Sfizz._lib = L
        L = self.L = Sfizz._lib
        self.block = 512
        self.s = L.sfizz_create_synth()
        L.sfizz_set_sample_rate(self.s, float(SR))
        L.sfizz_set_samples_per_block(self.s, self.block)
        L.sfizz_enable_freewheeling(self.s)
        if not L.sfizz_load_file(self.s, path.encode()):
            raise RuntimeError("sfizz could not load " + path)
        self.regions = L.sfizz_get_num_regions(self.s)
        self.buf = np.zeros((2, self.block), np.float32)
        fp = ctypes.POINTER(ctypes.c_float)
        self.ptrs = (fp * 2)(self.buf[0].ctypes.data_as(fp), self.buf[1].ctypes.data_as(fp))
        self.range = None

    def render(self, key, vel, hold, total):
        """frames: note on at 0, off after `hold`, `total` frames in all → (total, 2) float32"""
        L = self.L
        L.sfizz_all_sound_off(self.s)
        for _ in range(2):  # flush whatever the reset left
            L.sfizz_render_block(self.s, self.ptrs, 2, self.block)
        out = np.zeros((total, 2), np.float32)
        pos = 0
        on_sent = off_sent = False
        while pos < total:
            if not on_sent:
                L.sfizz_send_note_on(self.s, 0, key, vel)
                on_sent = True
            if not off_sent and hold < pos + self.block:
                L.sfizz_send_note_off(self.s, max(0, hold - pos), key, 0)
                off_sent = True
            L.sfizz_render_block(self.s, self.ptrs, 2, self.block)
            n = min(self.block, total - pos)
            out[pos:pos + n] = self.buf[:, :n].T
            pos += self.block
        return out

    def find_range(self):
        """keys that sound (probe each key once, short)"""
        if self.range is None:
            ok = []
            for k in range(12, 109):
                y = self.render(k, 100, int(0.12 * SR), int(0.25 * SR))
                if np.abs(y).max() > 1e-4:
                    ok.append(k)
            self.range = ok
        return self.range


class SfzSampler(Sampler):
    def __init__(self, seconds, lib, seed=7, calib=None):
        super().__init__(seconds, seed)
        self.lib = lib
        self.synths = {}
        self.ncache = collections.OrderedDict()
        self.calib = calib or {}
        self.notes_rendered = 0

    def synth(self, name):
        if name not in self.synths:
            self.synths[name] = Sfizz(sfz_path(self.lib, name))
        return self.synths[name]

    def choose(self, art, midi):
        """the instrument and the key to play for a wanted pitch (outside the range: nearest key, resampled)"""
        best = None
        for name in MAP[self.lib][art]:
            s = self.synth(name)
            rng = s.find_range()
            if not rng:
                continue
            k = min(rng, key=lambda x: abs(x - midi))
            if best is None or abs(k - midi) < abs(best[1] - midi):
                best = (s, k)
            if abs(k - midi) < 0.5:
                break
        return best

    def dry(self, art, key_synth, key, vel, hold, total):
        ck = (art, id(key_synth), key, vel, hold // 2205, total // 2205)
        if ck in self.ncache:
            self.ncache.move_to_end(ck)
            y = self.ncache[ck]
            if len(y) >= total:
                return y[:total]
        y = key_synth.render(key, vel, hold, total)
        self.notes_rendered += 1
        self.ncache[ck] = y
        while len(self.ncache) > 400:
            self.ncache.popitem(last=False)
        return y

    def note(self, art, midi, t, dur, vel=0.6, gain=1.0, pan=0.0, bus="main", attack=0.0, release=0.6,
             detune=0.0, bend=0.0, ringmod=0.0, reverse=False):
        s, key = self.choose(art, int(round(midi)))
        r0 = 2 ** ((midi - key + detune) / 12.0)
        n_out = int((dur + release) * SR)
        k = int(dur * SR)
        if bend:
            tt = np.minimum(np.arange(n_out) / max(1, k), 1.0)
            ratio = r0 * 2 ** (bend * tt / 12.0)
        else:
            ratio = np.full(n_out, r0)
        pos = np.concatenate([[0.0], np.cumsum(ratio[:-1])])
        need = int(pos[-1]) + 8
        hold = int(pos[min(k, n_out - 1)]) if k < n_out else need
        mvel = max(1, min(127, int(round(1 + 126 * vel))))
        d = self.dry(art, s, key, mvel, hold, need)
        if reverse:
            d = d[::-1].copy()
            # a reversed swell ends where the recording began: drop the silence the reversal brought to the front
            e = np.abs(d).max(1)
            j = int(np.argmax(e > e.max() * 0.01))
            d = np.concatenate([d[j:], np.zeros((j, 2), np.float32)])
        y = np.stack([np.interp(pos, np.arange(len(d)), d[:, c]) for c in range(2)], 1).astype(np.float32)
        if ringmod:
            y *= (0.35 + 0.65 * np.sin(2 * np.pi * ringmod * np.arange(n_out) / SR)).astype(np.float32)[:, None]
        env = np.ones(n_out, np.float32)
        a = min(n_out, int(attack * SR))
        if a > 1:
            env[:a] = np.linspace(0, 1, a) ** 1.5
        if k < n_out:
            env[k:] = np.exp(-np.linspace(0, 6, n_out - k)).astype(np.float32)
        y *= env[:, None]
        self.place(y, t, bus, gain * (0.35 + 0.65 * vel) * self.calib.get(art, 1.0), pan)
