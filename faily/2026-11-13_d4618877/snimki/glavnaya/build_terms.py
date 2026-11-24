"""Сводка терминов между переводами: как передан каждый ключевой немецкий термин в каждой редакции.

Соответствие ищется по положениям: номер — общий ключ всех редакций, поэтому для термина T
известно множество положений P, где T стоит в немецком тексте. Для каждой редакции считаются
основы слов (и пары соседних основ) и выбираются те, что встречаются именно в P: мера —
F1 от точности (доля положений с основой, попавших в P) и полноты (доля P, где основа есть).
Это статистика, а не словарь: верхние кандидаты почти всегда — настоящие соответствия,
ниже бывают попутные слова; в читалке видно число положений у каждого.

    python3 build_terms.py      → ../out/reader/data/terms.js (+ terms.json рядом для просмотра)
"""
import json, os, re, unicodedata
from collections import Counter, defaultdict

W = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(W, "..", "out", "tlp-data.json")))
props = data["props"]

# немецкий термин -> регулярное выражение по свёрнутому слову (целиком)
TERMS = [
    ("Welt", r"welt(en)?"), ("Fall", r"fall"), ("Tatsache", r"tatsache[n]?"), ("Sachverhalt", r"sachverhalt(e|en|es|s)?"),
    ("Sachlage", r"sachlage[n]?"), ("Gegenstand", r"gegenst(a|ae)nd(e|en|es|s)?"), ("Ding", r"ding(e|en|es|s)?"),
    ("Substanz", r"substanz"), ("Form", r"form(en)?"), ("Struktur", r"struktur(en)?"), ("logischer Raum", r"raum(e|es|s)?"),
    ("Bild", r"bild(e|er|ern|es|s)?"), ("abbilden", r"(abbild\w*)"), ("darstellen", r"(darstell\w*|stellt|stellen)"),
    ("Wirklichkeit", r"wirklichkeit"), ("Gedanke", r"gedanke[n]?"), ("Satz", r"s(a|ae)tz(e|es|en)?"),
    ("Elementarsatz", r"elementars(a|ae)tz(e|es|en)?"), ("Satzzeichen", r"satzzeichen[s]?"), ("Zeichen", r"zeichen[s]?"),
    ("Symbol", r"symbol(e|en|s)?"), ("Name", r"name[n]?"), ("Ausdruck", r"ausdr(u|ue)ck(e|en|es|s)?"),
    ("Sinn", r"sinn(e|es|s)?"), ("Bedeutung", r"bedeutung(en)?"), ("Variable", r"variable[n]?"),
    ("Funktion", r"funktion(en)?"), ("Wahrheitsfunktion", r"wahrheitsfunktion(en)?"), ("Operation", r"operation(en)?"),
    ("Wahrheitsmöglichkeit", r"wahrheitsm(o|oe)glichkeit(en)?"), ("Wahrheitsbedingung", r"wahrheitsbedingung(en)?"),
    ("Wahrheitsgrund", r"wahrheitsgr(u|ue)nd(e|en)?"), ("Wahrheitsargument", r"wahrheitsargument(e|en)?"),
    ("Tautologie", r"tautologie[n]?"), ("Kontradiktion", r"kontradiktion(en)?"), ("Wahrscheinlichkeit", r"wahrscheinlichkeit"),
    ("Logik", r"logik"), ("logisch", r"logisch(e|er|es|en|em)?"), ("Mathematik", r"mathematik"), ("Gleichung", r"gleichung(en)?"),
    ("Philosophie", r"philosophie"), ("Sprache", r"sprache"), ("Grenze", r"grenze[n]?"), ("Subjekt", r"subjekt(e|es|s)?"),
    ("Solipsismus", r"solipsismus"), ("Wille", r"wille[n]?"), ("Ethik", r"ethik"), ("Mystische", r"mystische?"),
    ("zeigen", r"(zeig\w*)"), ("sagen", r"(sag\w*)"), ("Naturgesetz", r"naturgesetz(e|es|en)?"), ("Kausalität", r"kausalit(a|ae)t"),
    ("Induktion", r"induktion"), ("Allgemeinheit", r"allgemeinheit"), ("Identität", r"identit(a|ae)t"),
]
DE = "de1961"
TARGETS = [e for e in data["editions"] if e != DE]
STOP = {
    "ru": set("и в во не на что как с со по к ко из у о об от для это то же а но или ли бы же так его ее её их он она оно они мы вы я ты "
              "этот эта эти этого этой этих тот та те того той тех весь вся все всех всего всем быть есть был была было были будет "
              "может могут можно нельзя также только уже еще ещё где когда если то чтобы при между через без над под до после ни "
              "который которая которое которые которого которой которых свой своя свои своего своей себя себе".split()),
    "en": set("the a an and or not of to in on at by for with from as is are was be been it its this that these those which what "
              "who we i one can cannot must may there their they he his all any every no so if then than also only into upon "
              "but do does is are has have had".split()),
}


def fold(s):
    s = unicodedata.normalize("NFD", s.replace("ß", "ss").replace("ё", "е").replace("Ё", "Е"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def plain(md):
    md = re.sub(r"```.*?```|\$\$?[^$]*\$\$?|!\[[^\]]*\]\([^)]*\)|\[\^[^\]]+\]|</?su[pb]>", " ", md or "", flags=re.S)
    return re.sub(r"[*|]", " ", md)


WORD = re.compile(r"[^\W\d_]+")


def stem(w, lang):
    if lang == "ru":
        return w[:5] if len(w) > 5 else w
    if lang == "en":
        w = re.sub(r"(ies)$", "y", w)
        w = re.sub(r"(?<=[^s])s$", "", w)
        return w[:7] if len(w) > 7 else w
    return w


def tokens(md, lang):
    words = [fold(w) for w in WORD.findall(plain(md))]
    words = [w for w in words if len(w) > 1]
    stems = [stem(w, lang) for w in words if w not in STOP.get(lang, ())]
    surf = {}
    for w in words:
        if w not in STOP.get(lang, ()):
            surf.setdefault(stem(w, lang), Counter())[w] += 1
    big = set()
    seq = [(stem(w, lang), w) for w in words]
    for (a, wa), (b, wb) in zip(seq, seq[1:]):
        if wa in STOP.get(lang, ()) or wb in STOP.get(lang, ()):
            continue
        big.add(a + " " + b)
        surf.setdefault(a + " " + b, Counter())[wa + " " + wb] += 1
    return set(stems) | big, surf


nums = list(props)
de_words = {n: [fold(w) for w in WORD.findall(plain(props[n]["text"].get(DE, "")))] for n in nums}
toks, surfs = {}, {}
for ed in TARGETS:
    lang = data["editions"][ed]["lang"]
    toks[ed], surfs[ed] = {}, defaultdict(Counter)
    for n in nums:
        if ed in props[n]["text"]:
            t, s = tokens(props[n]["text"][ed], lang)
            toks[ed][n] = t
            for k, c in s.items():
                surfs[ed][k].update(c)
df = {ed: Counter(x for n in toks[ed] for x in toks[ed][n]) for ed in TARGETS}

out = []
for name, rx in TERMS:
    r = re.compile(rf"^{rx}$")
    P = [n for n in nums if any(r.match(w) for w in de_words[n])]
    if len(P) < 2:
        continue
    row = {"de": name, "rx": rx, "props": P, "render": {}}
    for ed in TARGETS:
        have = [n for n in P if n in toks[ed]]
        if not have:
            continue
        cnt = Counter(x for n in have for x in toks[ed][n])
        cands = []
        for x, c_in in cnt.items():
            if c_in < 2 and len(have) > 3:
                continue
            c_all = df[ed][x]
            if c_all > 0.5 * len(toks[ed]):
                continue
            prec, rec = c_in / c_all, c_in / len(have)
            f1 = 2 * prec * rec / (prec + rec)
            cands.append((f1, x, c_in, c_all))
        cands.sort(reverse=True)
        picked = []
        for f1, x, c_in, c_all in cands:
            if f1 < 0.22 or len(picked) >= 4:
                break
            # пара основ не нужна, если одна её основа уже выбрана с тем же охватом
            if " " in x and any(p["key"] in x.split() and abs(p["n"] - c_in) <= 1 for p in picked):
                continue
            if " " not in x and any(x in p["key"].split() and abs(p["n"] - c_in) <= 1 for p in picked):
                continue
            form = surfs[ed][x].most_common(1)[0][0] if surfs[ed][x] else x
            q = " ".join(s + "*" for s in x.split())
            picked.append({"key": x, "form": form, "q": q, "n": c_in, "all": c_all, "score": round(f1, 2)})
        row["render"][ed] = picked
    out.append(row)

RD = os.path.join(W, "..", "out", "reader", "data")
os.makedirs(RD, exist_ok=True)
payload = {"de": DE, "targets": TARGETS, "terms": out}
open(os.path.join(RD, "terms.js"), "w", encoding="utf-8").write(
    "TLP.put(\"terms\"," + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ");\n")
json.dump(payload, open(os.path.join(W, "terms.json"), "w"), ensure_ascii=False, indent=1)
print("терминов:", len(out))
for row in out[:60]:
    print(f"{row['de']:22s} {len(row['props']):3d} | " + " | ".join(
        ed + ": " + ", ".join(f"{p['form']}({p['n']})" for p in row["render"].get(ed, [])[:3]) for ed in TARGETS))
