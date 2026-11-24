"""rev. 0.14: pack the project tree into a zip that unpacks everywhere (Android, Windows, macOS).

Usage: python3 tools/pack.py <project dir> <out.zip>

Before writing, every path is checked:
  * no two paths that differ only in letter case (Android shared storage, Windows and macOS
    are case-insensitive: the second file would overwrite the first or the extraction fails);
  * ASCII only (archivers without UTF-8 support garble or reject the names);
  * no characters forbidden on FAT/exFAT/NTFS, no trailing dot or space, components <= 255 bytes.
Any violation stops the packing.  __pycache__ is left out.
"""
import os, re, sys, zipfile, collections

BAD = re.compile(r'[<>:"|?*\\\x00-\x1f]')


def collect(root):
    base = os.path.dirname(os.path.abspath(root))
    out = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x != '__pycache__')
        for f in sorted(fs):
            if f.endswith('.pyc'):
                continue
            p = os.path.join(d, f)
            out.append((p, os.path.relpath(p, base).replace(os.sep, '/')))
    return out


def problems(names):
    err = []
    low = collections.defaultdict(list)
    for n in names:
        low[n.lower()].append(n)
        for part in n.split('/'):
            if not part.isascii():
                err.append(f'не ASCII: {n}')
            if BAD.search(part):
                err.append(f'запрещённый символ: {n}')
            if part.endswith(('.', ' ')):
                err.append(f'точка или пробел в конце: {n}')
            if len(part.encode()) > 255:
                err.append(f'слишком длинное имя: {n}')
    for v in low.values():
        if len(v) > 1:
            err.append('различаются только регистром: ' + ', '.join(v))
    return err


def main(root, out):
    files = collect(root)
    err = problems([a for _, a in files])
    if err:
        print('\n'.join(err[:40]))
        raise SystemExit(f'{len(err)} неподходящих имён — архив не записан')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p, a in files:
            z.write(p, a)
    with zipfile.ZipFile(out) as z:
        bad = z.testzip()
    if bad:
        raise SystemExit(f'испорчен при записи: {bad}')
    print(f'{out}: {len(files)} файлов, {os.path.getsize(out) / 1e6:.1f} МБ, имена проверены')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
