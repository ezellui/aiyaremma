"""Notation out of the events: MIDI (one track per part), MusicXML (quantised, score order, techniques
written as text: pizz., trem., con sord., col legno, harmonics) and a PDF score through LilyPond.

What notation cannot carry is listed in the report instead: detune, glissando inside a note, ring
modulation, reversed notes, raw samples and grain clouds."""
import collections
import os
import shutil
import subprocess

import mido

from .instruments import INSTR

SCORE_ORDER = ["Piccolo", "Flute", "Alto flute", "Oboe", "English horn", "Clarinet", "Bass clarinet", "Bassoon",
               "Contrabassoon", "Horn", "Horns", "Trumpet", "Trombone", "Bass trombone", "Tuba", "Timpani",
               "Glockenspiel", "Crotales", "Xylophone", "Vibraphone", "Marimba", "Tubular bells", "Celesta", "Harp",
               "Piano", "Harpsichord", "Organ", "Choir", "Violin solo", "Violins", "Violas", "Cellos", "Basses"]
GM = {"Piccolo": 72, "Flute": 73, "Alto flute": 73, "Oboe": 68, "English horn": 69, "Clarinet": 71,
      "Bass clarinet": 71, "Bassoon": 70, "Contrabassoon": 70, "Horn": 60, "Horns": 60, "Trumpet": 56, "Trombone": 57,
      "Bass trombone": 57, "Tuba": 58, "Timpani": 47, "Glockenspiel": 9, "Crotales": 9, "Xylophone": 13,
      "Vibraphone": 11, "Marimba": 12, "Tubular bells": 14, "Celesta": 8, "Harp": 46, "Piano": 0, "Harpsichord": 6,
      "Organ": 19, "Choir": 52, "Violin solo": 40, "Violins": 48, "Violas": 48, "Cellos": 48, "Basses": 48}
TECH = {"pizz": "pizz.", "trem": "trem.", "mute": "con sord.", "colleg": "col legno", "harm": "harmonics",
        "harmon": "harmon mute", "spic": "spicc.", "roll": "roll"}


def _order(name):
    return SCORE_ORDER.index(name) if name in SCORE_ORDER else len(SCORE_ORDER)


def parts_of(piece):
    by = collections.defaultdict(list)
    for e in piece.notes():
        by[e["part"]].append(e)
    return dict(sorted(by.items(), key=lambda kv: _order(kv[0])))


def lost(piece):
    """what the notation leaves out"""
    c = collections.Counter()
    for e in piece.events:
        if e["kind"] == "note":
            if e["detune"]:
                c["notes with detune (out-of-tune doubles)"] += 1
            if e["bend"]:
                c["notes with a glissando inside"] += 1
            if e["ringmod"]:
                c["ring-modulated notes"] += 1
            if e["reverse"]:
                c["reversed notes"] += 1
            if not 0 <= round(e["midi"]) <= 127:
                c["notes outside MIDI range"] += 1
        elif e["kind"] in ("sample", "grains"):
            c[{"sample": "raw samples (noises, unpitched percussion)", "grains": "grain clouds"}[e["kind"]]] += 1
    return dict(c)


def to_midi(piece, path, tpb=480):
    mf = mido.MidiFile(ticks_per_beat=tpb)
    tick = lambda t: int(round(t * piece.bpm / 60.0 * tpb))  # noqa: E731
    head = mido.MidiTrack()
    head.append(mido.MetaMessage("track_name", name=piece.title, time=0))
    head.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(piece.bpm), time=0))
    head.append(mido.MetaMessage("time_signature", numerator=piece.meter[0], denominator=piece.meter[1], time=0))
    marks = sorted((tick(e["t"]), e["label"]) for e in piece.events if e["kind"] == "mark")
    last = 0
    for t, lab in marks:
        head.append(mido.MetaMessage("marker", text=str(lab)[:60], time=t - last))
        last = t
    mf.tracks.append(head)
    ch = 0
    for name, notes in parts_of(piece).items():
        if ch == 9:
            ch += 1
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=name, time=0))
        tr.append(mido.Message("program_change", program=GM.get(name, 48), channel=ch % 16, time=0))
        ev = []
        for e in notes:
            m = int(round(e["midi"]))
            if not 0 <= m <= 127:
                continue
            v = max(1, min(127, int(round(1 + 126 * e["vel"]))))
            ev.append((tick(e["t"]), 1, m, v))
            ev.append((max(tick(e["t"]) + 1, tick(e["t"] + e["dur"])), 0, m, 0))
        ev.sort(key=lambda x: (x[0], x[1]))
        last = 0
        for t, on, m, v in ev:
            tr.append(mido.Message("note_on" if on else "note_off", note=m, velocity=v, channel=ch % 16, time=t - last))
            last = t
        mf.tracks.append(tr)
        ch += 1
    mf.save(path)
    return path


def _tech(inst):
    suf = inst.split("_", 1)[1] if "_" in inst else ""
    return TECH.get(suf)


def to_musicxml(piece, path, divisors=(4, 3)):
    from music21 import articulations, chord, expressions, instrument, meter, note, stream, tempo

    q = lambda t: t * piece.bpm / 60.0  # noqa: E731  seconds → quarter lengths
    sc = stream.Score()
    sc.metadata = None
    from music21 import metadata
    sc.metadata = metadata.Metadata(title=piece.title)
    marks = [(q(e["t"]), str(e["label"])) for e in piece.events if e["kind"] == "mark"]
    for k, (name, notes) in enumerate(parts_of(piece).items()):
        part = stream.Part()
        inst = instrument.Instrument()
        inst.partName = name
        inst.partAbbreviation = name[:4] + "."
        part.insert(0, inst)
        # group simultaneous notes (same quantised onset and length) into chords; overlaps are left to music21
        grid = 1.0 / max(divisors)
        groups = collections.defaultdict(list)
        for e in notes:
            m = int(round(e["midi"]))
            if not 21 <= m <= 108:
                continue
            on = round(q(e["t"]) * 12) / 12
            ln = max(0.25, round(q(e["dur"]) * 4) / 4)
            groups[(on, ln, _tech(e["inst"]), e.get("art"))].append(m)
        last_tech = None
        for (on, ln, tech, art), ms in sorted(groups.items()):
            obj = note.Note(ms[0]) if len(set(ms)) == 1 else chord.Chord(sorted(set(ms)))
            obj.quarterLength = ln
            if tech != last_tech:
                txt = tech or ("arco" if last_tech in ("pizz.", "col legno", "spicc.") else
                               "senza sord." if last_tech == "con sord." else "ord." if last_tech else None)
                if txt:
                    part.insert(on, expressions.TextExpression(txt))
                last_tech = tech
            if tech == "trem." or tech == "roll":
                obj.expressions.append(expressions.Tremolo(numberOfMarks=3))
            if art == "staccato" or tech in ("spicc.",):
                obj.articulations.append(articulations.Staccato())
            if art == "accent":
                obj.articulations.append(articulations.Accent())
            part.insert(on, obj)
        if k == 0:
            part.insert(0, tempo.MetronomeMark(number=round(piece.bpm)))
            for on, lab in marks:
                part.insert(on, expressions.RehearsalMark(lab[:24]))
        part.insert(0, meter.TimeSignature(f"{piece.meter[0]}/{piece.meter[1]}"))
        sc.insert(0, part)
    sc = sc.quantize(quarterLengthDivisors=divisors, processOffsets=True, processDurations=True, inPlace=False)
    sc.write("musicxml", fp=path)
    return path


def to_pdf(musicxml, pdf):
    """MusicXML → LilyPond → PDF; returns the PDF path, or None when LilyPond is not installed"""
    if not (shutil.which("musicxml2ly") and shutil.which("lilypond")):
        return None
    base = os.path.splitext(pdf)[0]
    ly = base + ".ly"
    subprocess.run(["musicxml2ly", "--no-beaming", "-o", ly, musicxml], check=True, capture_output=True)
    # a readable score on A4 portrait, small staves
    src = open(ly, encoding="utf-8").read()
    src = src.replace('\\version', '#(set-global-staff-size 14)\n\\version', 1)
    open(ly, "w", encoding="utf-8").write(src)
    r = subprocess.run(["lilypond", "-dno-point-and-click", "-o", base, ly], capture_output=True, text=True)
    return pdf if os.path.exists(pdf) else (r.stderr[-800:] and None)


def export_all(piece, out_dir, pdf=True, max_pdf_seconds=420):
    os.makedirs(out_dir, exist_ok=True)
    slug = "score"
    res = {"midi": to_midi(piece, os.path.join(out_dir, slug + ".mid")), "lost": lost(piece)}
    try:
        res["musicxml"] = to_musicxml(piece, os.path.join(out_dir, slug + ".musicxml"))
        if pdf and piece.end() <= max_pdf_seconds:
            res["pdf"] = to_pdf(res["musicxml"], os.path.join(out_dir, slug + ".pdf"))
    except Exception as ex:  # notation is a by-product: never let it stop the audio
        res["notation_error"] = repr(ex)[:300]
    return res
