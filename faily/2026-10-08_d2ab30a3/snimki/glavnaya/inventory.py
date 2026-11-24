"""Rough inventory of user-visible English text in XQuery files.

Classifies candidates into:
  text   - literal text inside element constructors (<u>Derivatives</u>)
  string - string literals in expressions (' see ', '; see instead:')
  attr   - literal attribute values that are shown (title=, placeholder=, alt=)
Prints per-file counts, totals, distinct strings, and sample lines.
"""
import collections
import os
import re
import sys

root = sys.argv[1]
skip_files = {'test.xq', 'test-bak1.xq', 'test-bak2.xq', 'test-bak3.xq', 'giradeau-diff.xq'}

word = re.compile(r'[A-Za-z]{2,}')
# xpath-ish or technical literals that are not UI text
technical = re.compile(r'^(?:[a-z0-9\-]+|[a-z]{1,4}|[\w\-]+\.(?:html|js|css|xml|xq)|#.*|\.\./.*|https?://.*|'
                       r'[A-Z_]+(?::[A-Z_]+)?|ERROR:.*|\[[a-z]+\]|y|n|true|false)$')
attr_shown = re.compile(r'\b(title|placeholder|alt|value)="([^"{]*[A-Za-z][^"{]*)"')


def strip_comments(s):
    return re.sub(r'\(:.*?:\)', lambda m: ' ' * len(m.group(0)), s, flags=re.S)


per_file = collections.Counter()
kinds = collections.Counter()
distinct = collections.Counter()
samples = collections.defaultdict(list)

for fn in sorted(os.listdir(root)):
    if not fn.endswith('.xq') or fn in skip_files:
        continue
    src = strip_comments(open(os.path.join(root, fn), encoding='utf-8').read())
    src_nohtmlcomments = re.sub(r'<!--.*?-->', '', src, flags=re.S)
    # 1. text between tags, excluding enclosed expressions
    for m in re.finditer(r'>([^<>{}]*)<', src_nohtmlcomments):
        t = ' '.join(m.group(1).split())
        if word.search(t) and not re.search(r'[$():=\[\]]{2,}|\bfor \$|\blet \$|\breturn\b', t):
            kinds['text'] += 1; per_file[fn] += 1; distinct[t] += 1
            if len(samples['text']) < 25: samples['text'].append(f'{fn}: {t}')
    # 2. string literals
    for m in re.finditer(r"'([^'\n]*)'|\"([^\"\n]*)\"", src_nohtmlcomments):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if not word.search(t):
            continue
        st = t.strip()
        if technical.match(st) or '/' in st and ' ' not in st or st.startswith(('../', 'http')):
            continue
        # attribute-value context: handled separately
        before = src_nohtmlcomments[max(0, m.start() - 12):m.start()]
        if re.search(r'\b[\w\-]+=$', before):
            continue
        if re.fullmatch(r'[a-z\-]+(\|[a-z\-]+)*', st):  # lang codes / speech codes
            continue
        kinds['string'] += 1; per_file[fn] += 1; distinct[st] += 1
        if len(samples['string']) < 40: samples['string'].append(f'{fn}: {t!r}')
    # 3. visible attributes
    for m in attr_shown.finditer(src_nohtmlcomments):
        t = m.group(2).strip()
        if technical.match(t) or re.fullmatch(r'[a-z\-|]+', t):
            continue
        kinds['attr'] += 1; per_file[fn] += 1; distinct[t] += 1
        if len(samples['attr']) < 15: samples['attr'].append(f'{fn}: {m.group(1)}="{t}"')

print('per file:')
for fn, n in per_file.most_common():
    print(f'  {n:4}  {fn}')
print('kinds:', dict(kinds), ' total', sum(kinds.values()), ' distinct', len(distinct))
for k in ('text', 'string', 'attr'):
    print(f'\n--- {k} samples')
    for s in samples[k]:
        print('  ', s[:150])
