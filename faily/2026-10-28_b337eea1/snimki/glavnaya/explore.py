import sys
from collections import Counter
from lxml import etree

root = etree.parse(sys.argv[1]).getroot()

def lang(el):
    while el is not None:
        if el.get('l'):
            return el.get('l')
        el = el.getparent()

def speech(el):
    while el is not None:
        if el.get('speech'):
            return el.get('speech')
        el = el.getparent()

words = [w for w in root.iter('word') if lang(w) in ('nq', 'q', 'mq', 'eq')]
words = [w for w in words if w.find('combine') is None]
sel = []
for w in words:
    sp = speech(w) or ''
    if sp.endswith('-name') or sp in ('text', 'phrase', 'grammar', 'root') or sp.startswith('phone'):
        continue
    if w.find('deprecated') is not None or w.find('see') is not None:
        continue
    if w.get('gloss') == '[unglossed]':
        continue
    if lang(w) in ('eq', 'en', 'g', 'ep'):
        continue
    m = w.get('mark') or ''
    if '-' in m or '|' in m:
        continue
    sel.append(w)

print('selected', len(sel), Counter(lang(w) for w in sel))
print('no page-id', sum(1 for w in sel if not w.get('page-id')))
print('nested', sum(1 for w in sel if w.getparent().tag == 'word'))
c = Counter()
for w in sel:
    tags = {ch.tag for ch in w}
    for t in tags:
        c['word/' + t] += 1
    for r in w.findall('ref'):
        for ch in r:
            c['ref/' + ch.tag] += 1
print(c.most_common())
# what links nq words carry
for w in sel[:0]:
    pass
