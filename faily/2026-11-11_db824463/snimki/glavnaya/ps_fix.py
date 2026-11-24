#!/usr/bin/env python3
"""ps_fix.py IN.ps OUT.pdf — pass B: Wine's PostScript driver writes Folio's palette bitmaps with an
all-black colour table (the DIB_PAL_COLORS lookup fails); the pixel indices are intact and, for the
BEE facsimile drawings, run from black (0) to white (N). Replace every all-zero /Indexed palette by a
grey ramp, then let Ghostscript make the PDF."""
import re, sys, subprocess

src, out = sys.argv[1], sys.argv[2]
s = open(src, 'rb').read()
n_fixed = 0


def ramp(m):
    global n_fixed
    hi = int(m.group(2))
    body = re.sub(rb'\s', b'', m.group(3))
    if body.strip(b'0'):
        return m.group(0)                       # a real palette: keep it
    n_fixed += 1
    vals = b''.join(b'%02x%02x%02x' % ((v := round(i * 255 / max(hi, 1))), v, v) for i in range(hi + 1))
    return m.group(1) + b'<' + vals + b'>'


s = re.sub(rb'(\[/Indexed /DeviceRGB (\d+)\s*)<([0-9a-fA-F\s]*)>', ramp, s)
tmp = out + '.ps'
open(tmp, 'wb').write(s)
r = subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pdfwrite',
                    '-dAutoFilterColorImages=false', '-sColorImageFilter=FlateEncode',
                    '-dAutoFilterGrayImages=false', '-sGrayImageFilter=FlateEncode',
                    '-dDownsampleColorImages=false', '-dDownsampleGrayImages=false',
                    '-sOutputFile=' + out, tmp], capture_output=True)
if r.returncode:
    sys.exit(r.stderr.decode(errors='replace')[-2000:])
import os
os.remove(tmp)
print(out, 'palettes fixed:', n_fixed)
