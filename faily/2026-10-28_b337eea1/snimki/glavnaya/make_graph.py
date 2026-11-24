#!/usr/bin/env python3
"""The graph of neo-roots.json for the interactive page.

    python make_graph.py neo-roots.json graph_template.html neo-roots-graph.html

Nodes are Eldamo pages (words, primitive forms, roots), keyed by page id; edges go from
the origin to what comes from it (root -> primitive form -> word), with the relation:
deriv, element, combine, see, deprecated, cognate (from the trees of the words) and
merged, filed, rootderiv (from the index of roots). The graph is written as compact JSON
into the template, at the /*GRAPH*/ placeholder, so the page is one self-contained file.
"""
import json
import sys

RELS = ['deriv', 'element', 'combine', 'see', 'deprecated', 'cognate', 'merged', 'filed', 'rootderiv']
KINDS = ['word', 'form', 'protoform', 'root']
WARN = ['deprecated', 'deleted', 'rejected', 'doubtful', 'unglossed', 'early']


def pid(url):
    return url.split('word-')[1].split('.')[0] if url else None


def main(src, template, out):
    doc = json.load(open(src, encoding='utf-8'))
    nodes = {}          # id -> record
    edges = {}          # (from, to, rel) -> record

    def node(i, form, lang, kind, gloss=None):
        n = nodes.get(i)
        if n is None:
            n = nodes[i] = {'f': form, 'l': lang, 'k': kind}
        if gloss and not n.get('g'):
            n['g'] = gloss
        # a page met as a word of the lists stays a word; a root stays a root
        if KINDS.index(kind) > KINDS.index(n['k']) and n['k'] != 'word':
            n['k'] = kind
        return n

    def edge(a, b, rel, written=None, nm=False, uncertain=False):
        key = (a, b, rel)
        e = edges.get(key)
        if e is None:
            e = edges[key] = {}
        if written:
            e.setdefault('w', [])
            for w in written:
                chain = [w['form']] + w.get('intermediate', []) + [w['ref']]
                rec = [w['source'], chain]
                if rec not in e['w']:
                    e['w'].append(rec)
        if nm:
            e['nm'] = 1
        return e

    # the words of the three lists
    for e in doc['words']:
        i = pid(e['url'])
        n = node(i, e['word'], e['lang'], 'word', e['gloss'])
        n['k'] = 'word'
        n['grp'] = e['group']
        n['s'] = e['speech']
        if e.get('rule'):
            n['r'] = e['rule']
        if e.get('uncertain'):
            n['u'] = 1
        if e['group'] == 'nq' and e['spelling'] != e['word']:
            n['sp'] = e['spelling']

    gap_seq = [0]

    def walk(parent_id, t):
        for c in t.get('parts', []) + t.get('from', []):
            ci = pid(c.get('url'))
            if ci is None:                       # an element Eldamo has no page for
                gap_seq[0] += 1
                ci = f"x{gap_seq[0]}"
            node(ci, c['form'], c['lang'], c['kind'], c.get('gloss'))
            edge(ci, parent_id, c['rel'], c.get('written'), nm=bool(c.get('not_matched')))
            walk(ci, c)

    for e in doc['words']:
        walk(pid(e['url']), e.get('tree', {}))

    # the index of roots
    for r in doc['roots']:
        i = pid(r['url'])
        n = node(i, r['form'], r['lang'], 'root', r.get('gloss'))
        n['k'] = 'root'
        n['rec'] = 1 if r['recommended'] else 0
        if r.get('warnings'):
            n['wn'] = [WARN.index(x) for x in r['warnings']]
        if r.get('in_list') is False:
            n['nl'] = 1
        if r.get('see_instead'):
            n['ins'] = [pid(x['url']) for x in r['see_instead']]
        for x in r.get('merged', []):
            xi = pid(x['url'])
            node(xi, x['form'], x['lang'], 'root', x.get('gloss'))
            edge(xi, i, 'merged')
        for x in r.get('filed_here', []):
            xi = pid(x['url'])
            node(xi, x['form'], x['lang'], 'root', x.get('gloss'))
            edge(xi, i, 'filed')
        for x in r.get('derives_from', []):
            xi = pid(x['url'])
            node(xi, x['form'], x['lang'], 'root', x.get('gloss'))
            edge(xi, i, 'rootderiv')
        if r.get('derivative_count'):
            n['dc'] = r['derivative_count']

    ids = list(nodes)
    index = {x: k for k, x in enumerate(ids)}
    graph = {
        'version': doc['source']['eldamo_version'],
        'rels': RELS,
        'kinds': KINDS,
        'warn': WARN,
        'ids': ids,
        'nodes': [nodes[x] for x in ids],
        'edges': [[index[a], index[b], RELS.index(rel)] + ([e] if e else [])
                  for (a, b, rel), e in edges.items()],
    }
    data = json.dumps(graph, ensure_ascii=False, separators=(',', ':'))
    data = data.replace('</', '<\\/')
    page = open(template, encoding='utf-8').read()
    assert '/*GRAPH*/' in page
    page = page.replace('/*GRAPH*/', data, 1)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    from collections import Counter
    print(len(ids), 'nodes', dict(Counter(n['k'] for n in nodes.values())),
          len(edges), 'edges', dict(Counter(r for _, _, r in edges)), f'{len(data) / 1e6:.1f} MB of data')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(2)
    main(*sys.argv[1:4])
