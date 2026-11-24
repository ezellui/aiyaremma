"""Единый набор данных читалки: tlp-data.json (и tlp-data.js для открытия с диска).

Берёт нормализованные тексты (norm_*.json, их пишет build_all.py), страницы положений из
выходов парсеров, схемы из figs/ и проверяет:
  * 526 номеров; у каждой редакции отсутствуют только положения из её списка missing;
  * каждая сноска [^…] разрешается в примечание своей редакции;
  * каждая ссылка на схему ![](fig:…) — на существующий файл;
  * каждая формула $…$ / $$…$$ проходит разбор KaTeX (node + reader/katex).

    python3 build_data.py            → ../out/tlp-data.json, ../out/tlp-data.js
"""
import base64, json, os, re, subprocess, sys
import tlp_tree

W = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(W, "..", "out")
canon = json.load(open(f"{W}/canon.json"))
nums, groups = tlp_tree.build(canon)

EDS = [
    ("de1961", "tlp_de_1961", "de", "1961", "Logisch-philosophische Abhandlung (deutscher Text, 1961)", "Deutsch 1961"),
    ("en1961", "tlp_en_1961_ogden", "en", "1961", "Tractatus Logico-Philosophicus, transl. C. K. Ogden (1961)", "Ogden 1961"),
    ("ru2005", "tlp_ru_2005_rudnev", "ru", "2005", "Логико-философский трактат, пер. и коммент. В. Руднева (2005)", "Руднев 2005"),
    ("ru2023", "tlp_ru_2023_korolev", "ru", "2023", "Логико-философский трактат, пер. К. Королева (2023)", "Королев 2023"),
]
CITE = {
    "de1961": "Wittgenstein L. Tractatus Logico-Philosophicus. London: Routledge & Kegan Paul, 1961, S. {p}",
    "en1961": "Wittgenstein L. Tractatus Logico-Philosophicus / Transl. C. K. Ogden. London: Routledge & Kegan Paul, 1961, p. {p}",
    "ru2005": "Витгенштейн Л. Логико-философский трактат / Пер. и коммент. В. Руднева // Витгенштейн Л. Избранные работы. М.: Территория будущего, 2005. С. {p}",
    "ru2023": "Витгенштейн Л. Логико-философский трактат / Пер. К. Королева. М.: КоЛибри, Азбука-Аттикус, 2023. С. {p}",
}
# страница PDF -> страница книги
PAGE_SHIFT = {"de1961": 0, "en1961": 0, "ru2005": 0, "ru2023": -1}

lp = json.load(open(f"{W}/lp1961.json"))
r05 = json.load(open(f"{W}/ru2005.json"))
r23 = json.load(open(f"{W}/ru2023.json"))
pages = {"de1961": lp["de"]["pages"], "en1961": lp["en"]["pages"], "ru2005": r05["pages"], "ru2023": {}}
for e in r23["entries"]:
    pages["ru2023"].setdefault(e["num"], e["page"])

errors = []
data = {"editions": {}, "props": {}, "front": {}, "notes": {}, "figures": {}, "comments": {}}
REF = re.compile(r"(?<![\d.,])([1-7]\.\d{1,5})(?![\d])")
canon_set = set(canon)

for ed, norm, lang, year, title, short in EDS:
    src = json.load(open(f"{W}/norm_{norm}.json"))
    missing = sorted(set(canon) - set(src["props"]), key=tlp_tree.key)
    data["editions"][ed] = {
        "lang": lang, "year": year, "title": title, "short": short, "note": src["note"],
        "missing": missing, "cite": CITE[ed], "comment_label": src.get("comment_label"),
    }
    data["front"][ed] = src.get("front", {})
    data["notes"][ed] = src.get("footnotes", {})
    for num in canon:
        p = data["props"].setdefault(num, {"parent": tlp_tree.parent(num), "groups": groups.get(num, []),
                                            "text": {}, "page": {}})
        if num in src["props"]:
            p["text"][ed] = src["props"][num]
            pg = pages[ed].get(num)
            if pg:
                p["page"][ed] = pg + PAGE_SHIFT[ed]
    if src.get("comments"):
        data["comments"][ed] = [{"covers": c["after"], "text": c["text"]} for c in src["comments"]]

# --- ссылки между положениями (в текстах и комментариях)
refs = {}
for num, p in data["props"].items():
    for ed, t in p["text"].items():
        for m in REF.finditer(t):
            if m.group(1) in canon_set and m.group(1) != num:
                refs.setdefault(num, set()).add(m.group(1))
for ed, cs in data["comments"].items():
    for c in cs:
        own = c["covers"][-1]
        for m in REF.finditer(c["text"]):
            if m.group(1) in canon_set and m.group(1) not in c["covers"]:
                refs.setdefault(own, set()).add(m.group(1))
for num, rs in refs.items():
    data["props"][num]["refs"] = sorted(rs, key=tlp_tree.key)

# --- схемы
for f in sorted(os.listdir(f"{W}/figs")):
    if f.endswith(".png"):
        data["figures"][f[:-4]] = "data:image/png;base64," + base64.b64encode(open(f"{W}/figs/{f}", "rb").read()).decode()

# --- проверки
texts = []   # (где, текст, редакция)
for num, p in data["props"].items():
    for ed, t in p["text"].items():
        texts.append((f"{ed} {num}", t, ed))
for ed, cs in data["comments"].items():
    for c in cs:
        texts.append((f"{ed} комм. к {c['covers'][-1]}", c["text"], ed))
for ed, fr in data["front"].items():
    for k, v in fr.items():
        for t in (v if isinstance(v, list) else [v]):
            if isinstance(t, str):
                texts.append((f"{ed} {k}", t, ed))
for ed, ns in data["notes"].items():
    for k, t in ns.items():
        texts.append((f"{ed} примеч. {k}", t, ed))

for where, t, ed in texts:
    for m in re.finditer(r"\[\^([^\]]+)\]", t):
        if m.group(1) not in data["notes"][ed]:
            errors.append(f"{where}: сноска [^{m.group(1)}] без примечания")
    for m in re.finditer(r"!\[[^\]]*\]\(fig:([^)]+)\)", t):
        if f"{ed}-{m.group(1)}" not in data["figures"]:
            errors.append(f"{where}: нет схемы {ed}-{m.group(1)}")

formulas = []
for where, t, ed in texts:
    t2 = re.sub(r"```.*?```", "", t, flags=re.S)
    for m in re.finditer(r"\$\$(.+?)\$\$", t2, flags=re.S):
        formulas.append([where, m.group(1), True])
    t3 = re.sub(r"\$\$.+?\$\$", "", t2, flags=re.S)
    for m in re.finditer(r"(?<![\\$])\$([^$\n]+?)\$", t3):
        formulas.append([where, m.group(1), False])
js = ("const katex=require(process.argv[1]);const f=JSON.parse(require('fs').readFileSync(0,'utf8'));"
      "for(const [w,t,d] of f){try{katex.renderToString(t,{displayMode:d,throwOnError:true})}"
      "catch(e){console.log(w+': '+e.message)}}")
r = subprocess.run(["node", "-e", js, f"{W}/reader/katex/katex.min.js"], input=json.dumps(formulas),
                   capture_output=True, text=True)
for ln in (r.stdout + r.stderr).strip().splitlines():
    errors.append("KaTeX: " + ln)

for ed, meta in data["editions"].items():
    print(f"{ed}: положений {526 - len(meta['missing'])}, нет {len(meta['missing'])}, "
          f"страниц {sum(1 for p in data['props'].values() if ed in p['page'])}")
print("формул проверено:", len(formulas), "| ссылок между положениями:", sum(len(v) for v in refs.values()),
      "| схем:", len(data["figures"]))
if errors:
    print("ОШИБКИ:", len(errors))
    for e in errors[:40]:
        print("  ", e)
else:
    print("проверки пройдены")

os.makedirs(OUT, exist_ok=True)
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
open(f"{OUT}/tlp-data.json", "w").write(s)
open(f"{OUT}/tlp-data.js", "w").write("window.TLP_DATA=" + s + ";\n")
print("tlp-data.json:", round(len(s.encode()) / 1e6, 2), "МБ")
