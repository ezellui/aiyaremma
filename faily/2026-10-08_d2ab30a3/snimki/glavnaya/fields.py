"""Inventory of text-bearing fields in eldamo-data.xml.

For each element's text content and each attribute: number of occurrences, how many look like
prose (several words), and a few samples. Codes, ids, sources and single words are counted but
not treated as prose.
"""
import collections
import random
import re
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
random.seed(1)

count = collections.Counter()
prose = collections.Counter()
samples = collections.defaultdict(list)
parents = collections.defaultdict(collections.Counter)

word = re.compile(r"[A-Za-z][A-Za-z'’]+")


def is_prose(v):
    words = word.findall(v)
    return len(words) >= 2 and ' ' in v.strip()


def keep(key, v):
    lst = samples[key]
    if len(lst) < 6:
        lst.append(v)
    elif random.random() < 0.002:
        lst[random.randrange(6)] = v


stack = []
for event, el in ET.iterparse(path, events=('start', 'end')):
    if event == 'start':
        stack.append(el.tag)
        continue
    stack.pop()
    parent = stack[-1] if stack else ''
    text = (el.text or '').strip()
    if text:
        key = (el.tag, '#text')
        count[key] += 1
        parents[key][parent] += 1
        if is_prose(text):
            prose[key] += 1
        keep(key, text[:160].replace('\n', ' '))
    for name, value in el.attrib.items():
        key = (el.tag, '@' + name)
        count[key] += 1
        parents[key][parent] += 1
        if is_prose(value):
            prose[key] += 1
            keep(key, value[:160])
        elif len(samples[key]) < 3:
            samples[key].append(value[:60])
    el.clear()

rows = sorted(count, key=lambda k: (-prose[k], -count[k]))
print(f'{"field":<34} {"count":>7} {"prose":>7}  parents / samples')
for key in rows:
    if prose[key] == 0 and key[1] != '#text':
        continue
    par = ', '.join(f'{p}:{n}' for p, n in parents[key].most_common(3))
    print(f'{key[0] + " " + key[1]:<34} {count[key]:>7} {prose[key]:>7}  [{par}]')
    for s in samples[key][:4]:
        print(f'{"":<50}| {s}')
print('\nattributes never prose-like:')
print(', '.join(sorted(f'{k[0]}{k[1]}' for k in count if prose[k] == 0 and k[1] != '#text')))
