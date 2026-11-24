"""Check the localization prototype.

1. English: new output vs. baseline, byte-identical or identical up to whitespace.
2. Russian: text nodes that are exactly an English literal of the original templates
   (untranslated interface), and errors.

usage: compare_l10n.py OUT_DIR BASE_QUERY_DIR
"""
import collections
import html
import os
import re
import sys

out, base_q = sys.argv[1:3]
groups = ['words', 'words-pub', 'lang', 'windex', 'lindex']


def norm_ws(s):
    return re.sub(r'\s+', ' ', re.sub(r'>\s+', '>', re.sub(r'\s+<', '<', s))).strip()


print('== English: new vs baseline')
ws_samples = []
for g in groups:
    b, a = f'{out}/eldamo-base-en/{g}', f'{out}/eldamo-en/{g}'
    if not os.path.isdir(b):
        continue
    files = [f for f in os.listdir(b) if f.endswith('.html')]
    same = ws = diff = 0
    diffs = []
    for f in files:
        x = open(f'{b}/{f}', encoding='utf-8').read()
        y = open(f'{a}/{f}', encoding='utf-8').read()
        if x == y:
            same += 1
        elif norm_ws(x) == norm_ws(y):
            ws += 1
            if len(ws_samples) < 3:
                ws_samples.append((g, f))
        else:
            diff += 1
            diffs.append(f)
    print(f'  {g:<10} pages {len(files):4}  identical {same:4}  whitespace-only {ws:3}  DIFFERENT {diff}  {diffs[:5]}')

# English literals of the original templates of the prototype pages
lits = set()
for name in ['word-page.xq', 'language-page.xq', 'language-index.xq', 'word-index.xq']:
    src = open(f'{base_q}/{name}', encoding='utf-8').read()
    src = re.sub(r'\(:.*?:\)', '', src, flags=re.S)
    for m in re.finditer(r'>([^<>{}]*)<', src):
        t = ' '.join(m.group(1).split())
        if re.search(r'[A-Za-z]{3}', t):
            lits.add(t)
    for m in re.finditer(r"'([^'\n]*[A-Za-z]{3}[^'\n]*)'", src):
        t = ' '.join(m.group(1).split())
        if not re.fullmatch(r'[a-z\-]+|[a-z]+\.\w+|.*\.html.*|\.\./.*', t):
            lits.add(t)
# pieces around enclosed expressions: "See", "for discussion." etc.
for t in list(lits):
    for piece in re.split(r'\s*\{[^}]*\}\s*', t):
        if re.search(r'[A-Za-z]{3}', piece):
            lits.add(piece.strip())
technical = {'Eldamo', 'Eldamo :', 'neo', 'class', 'match', 'notes', 'see-from', 'see-instead'}
lits = {l for l in lits if l not in technical and not l.startswith(('[ERROR', '[combine', 'ERROR', '<rule'))}

print('\n== Russian: untranslated interface text and errors')
leftover = collections.Counter()
where = collections.defaultdict(set)
for g in groups:
    d = f'{out}/eldamo-ru/{g}'
    if not os.path.isdir(d):
        continue
    errs = open(f'{d}/errors.txt', encoding='utf-8').read().strip()
    files = [f for f in os.listdir(d) if f.endswith('.html')]
    has_lang = sum(1 for f in files if '<html lang="ru"' in open(f'{d}/{f}', encoding='utf-8').read(400))
    print(f'  {g:<10} pages {len(files):4}  errors {len(errs.splitlines()) if errs else 0}  <html lang="ru"> {has_lang}')
    for f in files:
        s = open(f'{d}/{f}', encoding='utf-8').read()
        s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
        for node in re.findall(r'>([^<>]+)<', s):
            t = ' '.join(html.unescape(node).split()).strip(' ()[]:;,.')
            if t in lits or t + '.' in lits or t + ':' in lits:
                leftover[t] += 1
                where[t].add(g)
if leftover:
    print('  untranslated literal text nodes:')
    for t, n in leftover.most_common(40):
        print(f'    {n:5}  {t!r}  in {sorted(where[t])}')
else:
    print('  no untranslated literal text nodes')
