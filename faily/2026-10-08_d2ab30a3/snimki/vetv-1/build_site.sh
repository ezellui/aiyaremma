#!/bin/bash
# The HWPh reader from the Markdown volumes: MD -> XML database -> XQuery -> static site.
#
#   ./build_site.sh <folder with Bd01.md …> [site folder]
#
# Settings (environment): PYTHON (python3), JAVA (java, 8 or newer), SAXON (the Saxon-HE jar, 9.9 or
# newer), XMX (Java heap, 3g), PARTS (groups of the word index, 8), UI_LANG (ru: language of the
# article pages), DB (the XML database, <site folder>.xml).
set -e
SRC=$(cd "$1" && pwd)
OUT=$(mkdir -p "${2:-site}" && cd "${2:-site}" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd)
PYTHON=${PYTHON:-python3}
JAVA=${JAVA:-java}
SAXON=${SAXON:-$HERE/saxon/saxon-he.jar}
XMX=${XMX:-3g}
PARTS=${PARTS:-8}
UI_LANG=${UI_LANG:-ru}
DB=${DB:-$OUT.xml}
T0=$(date +%s)

step() { echo "== $1 ($(( $(date +%s) - T0 )) с)" >&2; }
query() {   # query <file.xq> <stream> [name=value …]
  local q=$1 s=$2; shift 2
  "$JAVA" -Xmx$XMX -cp "$SAXON" net.sf.saxon.Query -s:"$DB" -q:"$HERE/xq/$q" -o:"$s" "$@"
}

step "1. Markdown -> XML: $DB"
"$PYTHON" "$HERE/md2xml.py" "$SRC" -o "$DB"

rm -rf "$OUT" && mkdir -p "$OUT"
step "2. статьи: data/a, data/t, pages"
query article.xq "$OUT.articles" bands='*' lang="$UI_LANG" i18n="$HERE/static/i18n.js"
"$PYTHON" "$HERE/split.py" "$OUT.articles" "$OUT" && rm "$OUT.articles"

step "3. словарный указатель: data/s, data/p, data/vocab.js, data/meta.js"
query index.xq "$OUT.index" parts="$PARTS"
"$PYTHON" "$HERE/split.py" "$OUT.index" "$OUT" && rm "$OUT.index"

step "4. регистр, граф, лица, списки, оглавление, читалка"
query global.xq "$OUT.global" lang="$UI_LANG" i18n="$HERE/static/i18n.js" ui="$HERE/static/hwph_ui.html"
"$PYTHON" "$HERE/split.py" "$OUT.global" "$OUT" && rm "$OUT.global"

step "5. неизменные файлы читалки"
cp "$HERE/static/static_api.js" "$HERE/static/i18n.js" "$OUT/"
cp -r "$HERE/static/katex" "$OUT/katex"
cp "$HERE/static/page.css" "$OUT/pages/page.css"

step "6. manifest.json (список всех файлов для кравлера)"
query manifest.xq "$OUT/manifest.json" site="$OUT"
# the pictures the articles show as PNG (those without a vector version), from the volumes' img/
"$PYTHON" - "$OUT" "$SRC/img" <<'EOF'
import json, os, shutil, sys
out, img = sys.argv[1], sys.argv[2]
files = json.load(open(os.path.join(out, 'manifest.json'), encoding='utf-8'))['files']
for f in files:
    if f.startswith('img/'):
        os.makedirs(os.path.join(out, 'img'), exist_ok=True)
        shutil.copyfile(os.path.join(img, f[4:]), os.path.join(out, f))
have = {os.path.relpath(os.path.join(d, f), out).replace(os.sep, '/') for d, _, fs in os.walk(out) for f in fs}
listed = set(files)
if have != listed:
    print('manifest.json не совпадает с папкой: лишние в папке', sorted(have - listed)[:10], '; нет в папке', sorted(listed - have)[:10], file=sys.stderr)
    sys.exit(1)
size = sum(os.path.getsize(os.path.join(out, f)) for f in files)
print('читалка: %d файлов, %.0f МБ' % (len(files), size / 1e6), file=sys.stderr)
EOF
step "готово: $OUT/index.html"
