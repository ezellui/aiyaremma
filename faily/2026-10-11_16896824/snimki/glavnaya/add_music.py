#!/usr/bin/env python3
"""Lay a music track under the rendered video.

  python3 add_music.py video.mp4 track.mp3 out.mp4                 # music from its start
  python3 add_music.py video.mp4 track.mp3 out.mp4 --start 45      # skip the first 45 s of the track
  python3 add_music.py video.mp4 track.mp3 out.mp4 --align-end     # the track's ending lands on the video's end
  python3 add_music.py ... --credit "5 vor 12 by Sascha Ende — ende.app · CC BY 4.0"   # credit line in the last seconds

Fades in and out, normalises loudness to -16 LUFS (EBU R128), copies the video stream untouched
unless a credit line has to be drawn.
"""
import argparse
import json
import subprocess


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("audio")
    ap.add_argument("out")
    ap.add_argument("--start", type=float, default=0.0, help="seconds to skip at the start of the track")
    ap.add_argument("--align-end", action="store_true", help="choose --start so the track ends with the video")
    ap.add_argument("--fade-in", type=float, default=1.5)
    ap.add_argument("--fade-out", type=float, default=3.0)
    ap.add_argument("--credit", default=None, help="attribution text shown over the last seconds")
    ap.add_argument("--credit-seconds", type=float, default=7.0)
    ap.add_argument("--font", default="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    a = ap.parse_args()

    vd, ad = duration(a.video), duration(a.audio)
    start = max(0.0, ad - vd) if a.align_end else a.start
    if start + vd > ad + 0.05:
        print(f"note: the track ({ad:.1f} s from {start:.1f} s) is shorter than the video ({vd:.1f} s); "
              f"the end will be silent")
    fo = max(0.0, vd - a.fade_out)
    af = (f"atrim=start={start:.3f}:duration={vd:.3f},asetpts=PTS-STARTPTS,"
          f"afade=t=in:st=0:d={a.fade_in},afade=t=out:st={fo:.3f}:d={a.fade_out},"
          f"loudnorm=I=-16:TP=-1.5:LRA=11")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-i", a.audio, "-filter_complex", f"[1:a]{af}[a]"]
    if a.credit:
        txt = a.credit.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
        t0 = max(0.0, vd - a.credit_seconds)
        vf = (f"[0:v]drawtext=fontfile={a.font}:text='{txt}':fontsize=22:fontcolor=white@0.85:"
              f"box=1:boxcolor=black@0.45:boxborderw=10:x=(w-text_w)/2:y=h-150:"
              f"alpha='if(lt(t,{t0}),0,min(1,(t-{t0})/0.8))'[v]")
        cmd[-1] = cmd[-1] + ";" + vf
        cmd += ["-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p"]
    else:
        cmd += ["-map", "0:v", "-c:v", "copy"]
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print(f"{a.out}: video {vd:.1f} s, music from {start:.1f} s of {ad:.1f} s")


if __name__ == "__main__":
    main()
