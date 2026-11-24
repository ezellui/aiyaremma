"""Detail of candidate editorial fields: per element text, split by parent and by bracketing.

Bracketed text "[...]" is Eldamo's editorial-insertion convention; the script shows how much of
each field is bracketed, unbracketed, or mixed, with samples of each, and checks a few
conventions in glosses (leading *, (lit.), [L.] language tags, '?').
"""
import collections
import random
import re
import sys
import xml.etree.ElementTree as ET

random.seed(7)
path = sys.argv[1]
FIELDS = {'related', 'change', 'correction', 'deriv', 'inflect', 'element', 'cognate', 'notes'}

data = collections.defaultdict(list)          # (tag, parent) -> texts
gloss_kinds = collections.Counter()
gloss_samples = collections.defaultdict(list)
heads = collections.Counter()
head_samples = collections.defaultdict(list)
notes_parents = collections.Counter()

stack = []
for event, el in ET.iterparse(path, events=('start', 'end')):
    if event == 'start':
        stack.append(el)
        continue
    stack.pop()
    parent = stack[-1].tag if stack else ''
    text = (el.text or '').strip()
    if el.tag in FIELDS and text and el.tag != 'notes':
        data[(el.tag, parent)].append(text)
    if el.tag == 'notes':
        notes_parents[parent] += 1
    if el.tag in ('word', 'ref'):
        for attr in ('gloss', 'ngloss'):
            g = el.get(attr)
            if not g:
                continue
            kinds = []
            if g.startswith('*') or ' *' in g or ',*' in g:
                kinds.append('starred *')
            if '(lit.)' in g:
                kinds.append('(lit.)')
            if re.search(r'\[[^\]]*\]', g):
                kinds.append('[bracketed]')
            if re.search(r'\[(?:[ᴹᴱᴺᴸ]?[A-Z][a-z]*\.|[ᴹᴱᴺ]?√|[ᴹᴱᴺ]?✶)\]', g):
                kinds.append('[L.] language tag')
            if '?' in g:
                kinds.append('?')
            if '⚠' in g:
                kinds.append('⚠️')
            for k in kinds or ['plain']:
                key = f'{el.tag} @{attr}: {k}'
                gloss_kinds[key] += 1
                if len(gloss_samples[key]) < 4 and random.random() < 0.05:
                    gloss_samples[key].append(g[:110])
    if el.tag == 'word' and el.get('speech') in ('grammar', 'phonetic-rule', 'phonetic-group', 'phoneme', 'text', 'phrase'):
        sp = el.get('speech')
        v = el.get('v', '')
        prose = len(re.findall(r'[A-Za-z]{2,}', v)) >= 2
        heads[(sp, prose)] += 1
        if prose and len(head_samples[sp]) < 4 and random.random() < 0.05:
            head_samples[sp].append(v[:90])
    el.clear()

print('== notes by parent:', dict(notes_parents))
print('\n== element text fields: bracketed vs plain, by parent')
for (tag, parent), texts in sorted(data.items(), key=lambda x: -len(x[1])):
    br = [t for t in texts if re.fullmatch(r'\[.*\]', t, re.S)]
    mixed = [t for t in texts if '[' in t and t not in br]
    plain = [t for t in texts if '[' not in t]
    print(f'{tag:<11} in {parent:<6} total {len(texts):5}  fully [..] {len(br):4}  mixed {len(mixed):4}  plain {len(plain):5}')
    for label, lst in (('fully', br), ('mixed', mixed), ('plain', plain)):
        if lst:
            picks = random.sample(lst, min(3, len(lst)))
            for p in picks:
                print(f'      {label:<6}| {p[:120]}')
print('\n== gloss conventions')
for k, n in sorted(gloss_kinds.items()):
    print(f'{n:6}  {k}')
    for s in gloss_samples[k][:3]:
        print(f'          | {s}')
print('\n== headwords of non-lexical entries (word @v), prose-like?')
for (sp, prose), n in sorted(heads.items()):
    print(f'{n:6}  {sp:<15} prose={prose}')
for sp, lst in head_samples.items():
    for s in lst[:3]:
        print(f'          {sp:<15}| {s}')
