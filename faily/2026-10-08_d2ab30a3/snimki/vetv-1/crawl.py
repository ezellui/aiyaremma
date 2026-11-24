#!/usr/bin/env python3
"""
crawl.py — collects the HWPh reader from a server into a folder (the step Eldamo's crawler does).

    python crawl.py http://127.0.0.1:8000/ hwph-site [--jobs 8]

Reads manifest.json (written by xq/manifest.xq), fetches every file it lists and then checks that the
pages link only to files of the list. Python 3.8+, standard library only.

To serve a reader folder for a test:  python -m http.server 8000 --directory <folder>
"""
import argparse, concurrent.futures, json, os, re, sys, time, urllib.parse, urllib.request


def fetch(base, rel, out, tries=3):
    url = urllib.parse.urljoin(base, urllib.parse.quote(rel))
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            break
        except Exception as e:                    # a busy server: try again a little later
            if k == tries - 1:
                return rel, None, str(e)
            time.sleep(1 + k)
    path = os.path.join(out, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return rel, len(data), None


LINK = re.compile(r'''(?:href|src)="([^"#?:]+)(?:[#?][^"]*)?"''')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base', help='адрес читалки, например http://127.0.0.1:8000/')
    ap.add_argument('out', help='папка, куда собрать файлы')
    ap.add_argument('--jobs', type=int, default=8, help='одновременных запросов (по умолчанию 8)')
    a = ap.parse_args()
    base = a.base if a.base.endswith('/') else a.base + '/'
    t0 = time.time()
    with urllib.request.urlopen(urllib.parse.urljoin(base, 'manifest.json'), timeout=60) as r:
        manifest = json.loads(r.read().decode('utf-8'))
    files = manifest['files']
    failed, total = [], 0
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as pool:
        for i, (rel, size, err) in enumerate(pool.map(lambda rel: fetch(base, rel, a.out), files)):
            if err:
                failed.append((rel, err))
            else:
                total += size
            if (i + 1) % 1000 == 0:
                print('… %d/%d' % (i + 1, len(files)), file=sys.stderr)
    # every link of the pages must point at a file of the list
    have = set(files)
    dangling = set()
    for rel in files:
        if rel.endswith('.html'):
            text = open(os.path.join(a.out, *rel.split('/')), encoding='utf-8').read()
            here = os.path.dirname(rel)
            for link in LINK.findall(text):
                target = os.path.normpath(os.path.join(here, link)).replace(os.sep, '/')
                if target not in have:
                    dangling.add((rel, link))
    print('собрано %d файлов из %d (%.0f МБ) за %.0f с' % (len(files) - len(failed), len(files), total / 1e6, time.time() - t0),
          file=sys.stderr)
    for rel, err in failed[:20]:
        print('  не получен:', rel, err, file=sys.stderr)
    for rel, link in sorted(dangling)[:20]:
        print('  ссылка мимо списка:', rel, '->', link, file=sys.stderr)
    sys.exit(1 if failed or dangling else 0)


if __name__ == '__main__':
    main()
