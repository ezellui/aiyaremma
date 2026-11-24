"""compare.py REF_DIR NEW_DIR — compare the files of NEW_DIR with those of REF_DIR.

For every file: byte-identical? If not:
  .js  data files: parsed as JSON and compared; 'html' values compared as DOM (see below)
  .html pages:     compared as DOM
DOM comparison: the HTML is parsed (html.parser), character references resolved, attribute order
ignored, adjacent text joined; two files are equal if they give the same sequence of elements,
attributes and text — what a browser builds from them."""
import json, os, sys
from collections import Counter
from html.parser import HTMLParser


class Tokens(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []

    def text(self, t):
        if self.out and self.out[-1][0] == 'T':
            self.out[-1] = ('T', self.out[-1][1] + t)
        else:
            self.out.append(('T', t))

    def handle_starttag(self, tag, attrs):
        self.out.append(('S', tag, tuple(sorted((k, v or '') for k, v in attrs))))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.out.append(('E', tag))

    def handle_endtag(self, tag):
        self.out.append(('E', tag))

    def handle_data(self, d):
        self.text(d)

    def handle_comment(self, d):
        self.out.append(('C', d))

    def handle_decl(self, d):
        self.out.append(('D', d.lower()))


def dom(s):
    p = Tokens()
    p.feed(s)
    p.close()
    return p.out


def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i, x, y
    return min(len(a), len(b)), (a[len(b)] if len(a) > len(b) else None), (b[len(a)] if len(b) > len(a) else None)


def load_js(s):
    body = s[s.index('\n') + 1:s.rindex('\n);')]
    return json.loads(body)


def compare_json(a, b, path=''):
    """list of (path, kind) differences; html strings compared as DOM"""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        if list(a) != list(b):
            out.append((path, 'keys %s != %s' % (list(a), list(b))))
        for k in a:
            if k in b:
                out += compare_json(a[k], b[k], path + '.' + k)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path, 'length %d != %d' % (len(a), len(b)))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += compare_json(x, y, '%s[%d]' % (path, i))
        return out
    if path.endswith('.html') and isinstance(a, str) and isinstance(b, str):
        if a == b:
            return []
        da, db = dom(a), dom(b)
        if da == db:
            return [(path, 'html: same DOM')]
        i, x, y = first_diff(da, db)
        return [(path, 'html: DOM differs at token %d: %r | %r' % (i, x, y))]
    if a != b or type(a) != type(b):
        return [(path, 'value %r != %r' % (str(a)[:80], str(b)[:80]))]
    return []


def main():
    ref, new = sys.argv[1], sys.argv[2]
    stats = Counter()
    examples = {}
    for dp, _, fs in os.walk(new):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), new)
            kind = rel.split(os.sep)[0] + '/' + (rel.split(os.sep)[1] if rel.startswith('data') else '')
            r = os.path.join(ref, rel)
            if not os.path.exists(r):
                stats[(kind, 'missing in ref')] += 1
                continue
            a = open(r, encoding='utf-8').read()
            b = open(os.path.join(new, rel), encoding='utf-8').read()
            if a == b:
                stats[(kind, 'byte-identical')] += 1
                continue
            if rel.endswith('.js'):
                diffs = compare_json(load_js(a), load_js(b))
                real = [d for d in diffs if d[1] != 'html: same DOM']
                if not diffs:
                    stats[(kind, 'same JSON, other layout')] += 1
                elif not real:
                    stats[(kind, 'same JSON, html same DOM')] += 1
                else:
                    stats[(kind, 'DIFFERENT')] += 1
                    for d in real:
                        key = (kind, d[0].split('[')[0] + ' ' + d[1].split(' ')[0])
                        stats[key] += 0
                        examples.setdefault(key, []).append((rel, d))
            else:
                da, db = dom(a), dom(b)
                if da == db:
                    stats[(kind, 'same DOM')] += 1
                else:
                    stats[(kind, 'DIFFERENT')] += 1
                    i, x, y = first_diff(da, db)
                    examples.setdefault((kind, 'dom'), []).append((rel, (i, x, y)))
    for (kind, what), n in sorted(stats.items()):
        if n:
            print('%-10s %-28s %d' % (kind, what, n))
    for key, ex in sorted(examples.items()):
        print('\n##', key, len(ex))
        for rel, d in ex[:4]:
            print('  ', rel, str(d)[:400])


if __name__ == '__main__':
    main()
