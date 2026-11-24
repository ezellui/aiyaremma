#!/usr/bin/env python3
"""finish.py SITE IMG — the last step of the build: copies the pictures the articles show as PNG (those
without a vector version) from the volumes' img/ folder, then checks that manifest.json lists exactly
the files of the site."""
import json, os, shutil, sys

out, img = sys.argv[1], sys.argv[2]
files = json.load(open(os.path.join(out, 'manifest.json'), encoding='utf-8'))['files']
for f in files:
    if f.startswith('img/'):
        os.makedirs(os.path.join(out, 'img'), exist_ok=True)
        shutil.copyfile(os.path.join(img, f[4:]), os.path.join(out, *f.split('/')))
have = {os.path.relpath(os.path.join(d, f), out).replace(os.sep, '/') for d, _, fs in os.walk(out) for f in fs}
listed = set(files)
if have != listed:
    print('manifest.json не совпадает с папкой: лишние в папке %s; нет в папке %s'
          % (sorted(have - listed)[:10], sorted(listed - have)[:10]), file=sys.stderr)
    sys.exit(1)
size = sum(os.path.getsize(os.path.join(out, *f.split('/'))) for f in files)
print('читалка: %d файлов, %.0f МБ — все перечислены в manifest.json' % (len(files), size / 1e6), file=sys.stderr)
