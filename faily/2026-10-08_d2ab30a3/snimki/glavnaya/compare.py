"""Compare before/after snapshots: count changed pages per group, show sample diffs."""
import difflib
import os
import re
import sys
from collections import Counter, defaultdict

before, after = sys.argv[1], sys.argv[2]
samples = int(sys.argv[3]) if len(sys.argv) > 3 else 2


def group_of(name):
    m = re.match(r'([a-z\-]+?)(?:_|-[a-z]+\.|\.|$)', name)
    if name.startswith('word-'):
        return 'word-page'
    return name.split('_')[0] if '_' in name else name


def lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        text = f.read()
    # split on tags so one-line HTML still yields meaningful diffs
    text = re.sub(r'>\s*<', '>\n<', text)
    return text.splitlines()


changed = defaultdict(list)
missing = []
total = 0
for root, _, files in os.walk(before):
    for fn in files:
        if fn.endswith('.status') or fn == 'errors.txt':
            continue
        rel = os.path.relpath(os.path.join(root, fn), before)
        other = os.path.join(after, rel)
        total += 1
        if not os.path.exists(other):
            missing.append(rel)
            continue
        with open(os.path.join(root, fn), 'rb') as a, open(other, 'rb') as b:
            if a.read() == b.read():
                continue
        changed[(os.path.dirname(rel), group_of(fn))].append(rel)

print(f'compared {total} files, changed {sum(len(v) for v in changed.values())}, missing in after {len(missing)}')
for key in sorted(changed):
    print(f'  {key[0]:<18} {key[1]:<28} {len(changed[key])}')
print()
for key in sorted(changed):
    for rel in changed[key][:samples]:
        a = lines(os.path.join(before, rel))
        b = lines(os.path.join(after, rel))
        diff = [d for d in difflib.unified_diff(a, b, lineterm='', n=0) if not d.startswith(('---', '+++', '@@'))]
        print(f'### {rel} ({len(diff)} diff lines)')
        for d in diff[:12]:
            print('   ', d[:220])
        print()
