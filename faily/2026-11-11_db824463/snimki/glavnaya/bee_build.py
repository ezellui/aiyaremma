#!/usr/bin/env python3
"""bee_build.py VERSION OUTDIR [--items 101,213]  — printed segments -> one XML per item.

Segments are print/VERSION/s<start>_<part>.pdf. A later segment (a restart after a crash) starts at
an item heading and replaces everything from that item on. For each item we take the latest segment
that contains its heading, and pass to bee_pdf2xml its PDFs from the one with the heading to the one
with the next item's heading (or to the end of the segment).
"""
import argparse, collections, glob, json, os, re, subprocess, sys
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = [l.split()[1] for l in open('/home/claude/work/items.txt')]


def headings(pdf, cache):
    if pdf in cache:
        return cache[pdf]
    found = []
    for page in pymupdf.open(pdf):
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(s['text'] for s in l['spans']).strip()
                if max((s['size'] for s in l['spans']), default=0) >= 13 and t.startswith('Item '):
                    w = t.split()
                    if len(w) > 1 and w[1] in ITEMS:
                        found.append(w[1])
    cache[pdf] = found
    return found


def plan(version):
    d = f'/home/claude/work/print/{version}'
    cpath = os.path.join(d, 'headings.json')
    cache = json.load(open(cpath)) if os.path.exists(cpath) else {}
    segs = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(d, 's*_*.pdf'))):
        m = re.match(r's(\d+)_(\d+)\.pdf$', os.path.basename(f))
        segs[int(m.group(1))].append(f)
    where = {}                                       # item -> (segment start, [pdfs])
    for start in sorted(segs):                       # later segments override earlier ones
        files = segs[start]
        hs = [(i, h) for i, f in enumerate(files) for h in headings(f, cache)]
        for k, (i, h) in enumerate(hs):
            nxt = hs[k + 1][0] if k + 1 < len(hs) else len(files) - 1
            complete = k + 1 < len(hs) or start == max(segs)
            if ITEMS.index(h) + 1 >= start:
                where[h] = (start, files[i:nxt + 1], complete)
        # an override: items from this segment's start on that it did not reach are dropped
        for h in list(where):
            if ITEMS.index(h) + 1 >= start and where[h][0] < start and h not in [x for _, x in hs]:
                del where[h]
    json.dump(cache, open(cpath, 'w'))
    return where


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('version'); ap.add_argument('out')
    ap.add_argument('--items')
    a = ap.parse_args()
    where = plan(a.version)
    todo = a.items.split(',') if a.items else [i for i in ITEMS if i in where]
    report = {}
    for it in todo:
        if it not in where:
            report[it] = 'missing'; continue
        start, files, complete = where[it]
        cmd = [sys.executable, '-I', os.path.join(HERE, 'bee_pdf2xml.py'), '--fonts', '/home/claude/iso',
               '--symbol', '/home/claude/work/wp/drive_c/windows/Fonts/symbol.ttf', '--out', a.out,
               '--only', it, '--version', a.version] + files
        r = subprocess.run(cmd, capture_output=True, text=True)
        report[it] = {'segment': start, 'pdfs': len(files), 'complete': complete,
                      'result': (r.stdout.strip().splitlines() or [r.stderr[-300:]])[-1]}
        print(it, report[it]['result'][:150], flush=True)
    json.dump(report, open(os.path.join(a.out, f'build.{a.version}.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
