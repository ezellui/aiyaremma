@'
import sqlite3, zlib, re, json
d = sqlite3.connect('hwph.sqlite')
meta = dict(d.execute('select * from meta').fetchall())
print('built:', json.loads(meta['stats'])['built'])
bad = 0
for lemma, h in d.execute('select lemma, html from articles'):
    html = zlib.decompress(h).decode()
    for m in re.finditer(r'<p class="lit"[^>]*>(.*?)</p>', html, re.S):
        if 'class="fn"' in m.group(1):
            bad += 1
print('lit paragraphs with note calls:', bad)
'@ | py -3.8 -