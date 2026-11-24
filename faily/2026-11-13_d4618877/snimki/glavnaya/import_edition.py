"""Добавить перевод в готовую папку читалки — без всего конвейера сборки.

    python3 import_edition.py <перевод.md> [--reader ../out/reader] [--remove]

Файл — в простом текстовом формате (описание в edition_text.py; примеры — out/text/*.md,
это четыре нынешние редакции в том же формате). Пишет data/ed/<id>.js и вносит редакцию в
data/manifest.js (повторный запуск с тем же id заменяет её). --remove убирает редакцию.

Чтобы новый перевод попал и в сводку терминов, и в общие проверки, положите файл в
work/editions/ и пересоберите: build_data.py → build_terms.py → build_site.py.
"""
import argparse, json, os, re, sys
import edition_text

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--reader", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "reader"))
ap.add_argument("--remove", action="store_true")
a = ap.parse_args()

DATA = os.path.join(a.reader, "data")


def read_put(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r'^TLP\.put\("([^"]+)",(.*)\);\s*$', s, re.S)
    return json.loads(m.group(2))


def write_put(path, key, obj):
    open(path, "w", encoding="utf-8").write(
        f"TLP.put({json.dumps(key)},{json.dumps(obj, ensure_ascii=False, separators=(',', ':'))});\n")


manifest = read_put(os.path.join(DATA, "manifest.js"))
tree = read_put(os.path.join(DATA, "tree.js"))
x = edition_text.parse(open(a.file, encoding="utf-8").read(), tree["nums"])
ed = x["meta"]["id"]
manifest["editions"] = [e for e in manifest["editions"] if e["id"] != ed]
if a.remove:
    p = os.path.join(DATA, "ed", ed + ".js")
    if os.path.exists(p):
        os.remove(p)
    write_put(os.path.join(DATA, "manifest.js"), "manifest", manifest)
    print("убрана редакция", ed)
    sys.exit()
for e in x["errors"]:
    print("!", e)
m = x["meta"]
manifest["editions"].append({
    "id": ed, "file": f"ed/{ed}.js", "lang": m["lang"], "year": m.get("year", ""), "title": m["title"],
    "short": m["short"], "note": m.get("note", ""), "missing": x["missing"], "cite": m["cite"],
    "comment_label": m.get("comment_label") or None, "has_comments": bool(x["comments"]),
})
write_put(os.path.join(DATA, "ed", ed + ".js"), "ed/" + ed,
          {"texts": x["texts"], "pages": x["pages"], "front": {}, "notes": x["notes"], "comments": x["comments"]})
write_put(os.path.join(DATA, "manifest.js"), "manifest", manifest)
print(f"редакция {ed}: положений {len(x['texts'])}, нет {len(x['missing'])}, комментариев {len(x['comments'])}, "
      f"страниц {len(x['pages'])} → {DATA}")
