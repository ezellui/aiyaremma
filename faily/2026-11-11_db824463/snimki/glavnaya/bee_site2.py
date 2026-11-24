#!/usr/bin/env python3
"""bee_site2.py XMLDIR DOCDIR SITEDIR — the static site.
  index.html            contents: groups -> items (filter), series, guide texts
  items/<n>.<v>.html    one page per item and transcription
  series/<id>.<v>.html  series of items on one page
  intro/<doc>.html      Introduction, User Guide, Read Me of the edition
  persons.html          register of persons with all places
  fields.html           the edition's fields: languages, coded text, cross references, descriptors
  figures/<n>.html      every figure of an item with its descriptor (to check the placement)
  mine.html             own work (bookmarks, highlights, notes)
  search.html           full-text and field search (data: bee_search2.py)
Styles and scripts: assets/ (copied from scripts/assets)."""
import sys, os, json, shutil, html, glob, re, collections
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bee_render as R

E = html.escape
xmldir, docdir, site = sys.argv[1:4]
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = '/home/claude/work'
ITEMS = [l.split()[1] for l in open(f'{WORK}/items.txt')]
series = json.load(open(os.path.join(HERE, 'series.json')))['series']
GROUPS = json.load(open(f'{WORK}/print/fields/groups.json')) if os.path.exists(f'{WORK}/print/fields/groups.json') else {}
for d in ('items', 'series', 'intro', 'figures'):
    os.makedirs(os.path.join(site, d), exist_ok=True)
shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(site, 'assets'), dirs_exist_ok=True)
if os.path.isdir(os.path.join(xmldir, 'img')):
    shutil.copytree(os.path.join(xmldir, 'img'), os.path.join(site, 'img'), dirs_exist_ok=True)
docs = {}
for f in glob.glob(os.path.join(xmldir, '*.xml')):
    r = ET.parse(f).getroot()
    if r.tag == 'item' and r.get('n') in ITEMS:
        docs[(r.get('n'), r.get('version'))] = r
t = R.t


def page(title, body, kind, root='', extra=''):
    return R.shell(title, body, root, kind, {'kind': kind}).replace('</body>', extra + '</body>')


# ---- items
for v in ('norm', 'diplo'):
    seq = [n for n in ITEMS if (n, v) in docs]
    for i, n in enumerate(seq):
        r = docs[(n, v)]
        o = 'diplo' if v == 'norm' else 'norm'
        R.OTHER = f'{n}.{o}.html' if (n, o) in docs else None
        R.OTHER_PAGES = {R.pid(x) for x in docs[(n, o)].iter('pb')} if (n, o) in docs else None
        out = R.render_item(r, seq[i - 1] if i else None, seq[i + 1] if i + 1 < len(seq) else None)
        open(os.path.join(site, 'items', f'{n}.{v}.html'), 'w', encoding='utf-8').write(out)
R.OTHER = R.OTHER_PAGES = None
# ---- series
for s in series:
    for v in ('norm', 'diplo'):
        its = [docs[(n, v)] for n in s['items'] if (n, v) in docs]
        if its:
            out = R.render_series(its, s['title'], s.get('about', ''))
            open(os.path.join(site, 'series', f'{s["id"]}.{v}.html'), 'w', encoding='utf-8').write(out)
# ---- guide texts
guides = [('introduction', 'intro.xml'), ('userguide', 'user.xml'), ('readme', 'readme.xml')]
glinks = []
for name, fn in guides:
    if os.path.exists(os.path.join(docdir, fn)):
        glinks.append((name, ET.parse(os.path.join(docdir, fn)).getroot().get('title')))
for name, fn in guides:
    p = os.path.join(docdir, fn)
    if not os.path.exists(p):
        continue
    d = ET.parse(p).getroot()
    links = [f'<a href="{n2}.html">{E(tt)}</a>' if n2 != name else f'<b>{E(tt)}</b>' for n2, tt in glinks]
    open(os.path.join(site, 'intro', f'{name}.html'), 'w', encoding='utf-8').write(R.render_doc(d, links))


def group(n):
    if n in GROUPS:
        return GROUPS[n]
    return ['manuscripts'] if n[0] == '1' else ['typescripts'] if n[0] == '2' else ['dictations']


def fold(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))


# ---- index (contents)
def row(n):
    r = docs.get((n, 'norm')) or docs.get((n, 'diplo'))
    title = r.get('title', '') if r is not None else ''
    pages = len(r.findall('.//pb')) if r is not None else 0
    links = ' '.join(f'<a href="items/{n}.{v}.html">{t("ver.short_" + v, "normalisiert" if v == "norm" else "diplomatisch")}</a>'
                     for v in ('norm', 'diplo') if (n, v) in docs)
    if os.path.exists(os.path.join(site, 'figures', f'{n}.html')) or any(x.get('src') for x in (docs.get((n, 'norm')) or ET.Element('x')).iter('figure')):
        links += f' <a href="figures/{n}.html" class="muted">{t("tb.figs", "Abbildungen")}</a>'
    return (f'<div class="it" data-k="{E(fold(n + " " + title))}"><span class="n">{E(n)}</span><span class="ttl">{E(title)}</span>'
            f' <span class="muted">{pages} {t("idx.pages", "S.")}</span> {links}</div>')


GNAMES = [('manuscripts', 'Manuskripte'), ('bände', 'davon: Bände'), ('typescripts', 'Typoskripte'), ('dictations', 'Diktate')]
tree = []
for g, de in GNAMES:
    ns = [n for n in ITEMS if g in group(n)]
    if not ns:
        continue
    tree.append(f'<details{" open" if g != "bände" else ""}><summary>{t("grp." + g, de)} <span class="muted">({len(ns)})</span></summary>' +
                ''.join(row(n) for n in ns) + '</details>')
ser = ''.join(f'<div class="it" data-k="{E(fold(s["title"] + " " + " ".join(s["items"])))}"><b>{E(s["title"])}</b> '
              f'<span class="muted">({", ".join(s["items"])})</span> ' +
              ' '.join(f'<a href="series/{s["id"]}.{v}.html">{t("ver.short_" + v, v)}</a>' for v in ('norm', 'diplo')
                       if os.path.exists(os.path.join(site, 'series', f'{s["id"]}.{v}.html'))) + '</div>' for s in series)
guide = ' · '.join(f'<a href="intro/{n}.html">{E(tt)}</a>' for n, tt in glinks)
body = (f'<h1>Wittgenstein\'s Nachlass — The Bergen Electronic Edition (2000)</h1>'
        f'<p class="about">{t("idx.about", "Normalisierte und diplomatische Transkription aller 156 Items; je Item eine Seite, Serien als zusammenhängende Seiten.")}</p>'
        f'<p class="ui">{t("idx.guides", "Zur Edition")}: {guide}</p>'
        f'<form action="search.html" class="ui"><input name="q" class="filter" data-i18n-placeholder="nav.searchph" placeholder="Volltextsuche …"> '
        f'<button>{t("s.go", "Suchen")}</button></form>'
        f'<h2>{t("idx.contents", "Inhalt")}</h2><input class="filter" data-target="#toc" data-i18n-placeholder="idx.filter" placeholder="Items filtern: Nummer oder Titel …">'
        f'<div id="toc" class="toctree">{"".join(tree)}<details open><summary>{t("idx.series", "Serien")} <span class="muted">({len(series)})</span></summary>{ser}</details></div>')
open(os.path.join(site, 'index.html'), 'w', encoding='utf-8').write(R.shell("Wittgenstein's Nachlass", body, '', 'index', {'kind': 'index'}))


# ---- unit anchors: NORM records and DIPLO pages, in the same way as bee_search2.py
def anchors(r, v):
    """yield (element, anchor, label) for the places where persons etc. are found"""
    n = r.get('n')
    if v == 'norm':
        for k, rec in enumerate([x for x in r if x.tag == 'rec']):
            yield rec, f'r-{n}-{k}', rec.get('page', '')
    else:
        cur = (None, f'item-{n}', '')
        stack = []
        for el in r.iter():
            if el.tag == 'pb':
                cur = (el, R.pid(el), el.get('n', ''))
            yield el, cur[1], cur[2]


# ---- persons
pers = collections.defaultdict(lambda: collections.defaultdict(list))   # key -> (n, v) -> [(anchor, label)]
for (n, v), r in docs.items():
    if v == 'norm':
        for rec, a, lab in anchors(r, v):
            for p in rec.iter('person'):
                lst = pers[p.get('key')][(n, v)]
                if not lst or lst[-1][0] != a: lst.append((a, lab))
    else:
        for el, a, lab in anchors(r, v):
            if el.tag == 'person':
                lst = pers[el.get('key')][(n, v)]
                if not lst or lst[-1][0] != a: lst.append((a, lab))
rows = []
for key in sorted(pers, key=lambda k: fold(k)):
    tot = sum(len(x) for x in pers[key].values())
    places = []
    for (n, v) in sorted(pers[key], key=lambda x: (ITEMS.index(x[0]), x[1])):
        ls = pers[key][(n, v)]
        q = 'person:' + re.sub(r'[^\w]+', ' ', key).split()[0] if key.split() else ''
        places.append(f'<div class="ui"><b>{E(n)}</b> <span class="muted">{"N" if v == "norm" else "D"}</span> ' +
                      ' '.join(f'<a href="items/{E(n)}.{v}.html#{E(a)}">{E(lab or "·")}</a>' for a, lab in ls) + '</div>')
    rows.append(f'<details id="{E(key)}" data-k="{E(fold(key))}"><summary>{E(key)} <span class="muted">({tot})</span></summary>{"".join(places)}</details>')
body = (f'<h1>{t("p.title", "Personenregister")}</h1><p class="about">{t("p.about", "Alle im Nachlass genannten Personen in der Normform der Edition, mit allen Stellen (N = normalisiert: Bemerkung, D = diplomatisch: Seite).")}</p>'
        f'<input class="filter" data-target="#plist" data-i18n-placeholder="p.filter" placeholder="Name filtern …"> <span class="muted">{len(pers)}</span>'
        f'<div id="plist" class="ui">{"".join(rows)}</div>'
        '<script>if(location.hash){var d=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(d){d.open=true;d.scrollIntoView();}}</script>')
open(os.path.join(site, 'persons.html'), 'w', encoding='utf-8').write(R.shell('Personen', body, '', 'persons', {'kind': 'persons'}))

# ---- fields
desc = collections.Counter(); kinds = collections.Counter(); langw = collections.defaultdict(collections.Counter)
for (n, v), r in docs.items():
    for x in r.iter():
        if x.tag == 'formula' and x.get('notation'):
            desc[x.get('notation')] += 1
        elif x.tag == 'figure' and x.get('desc'):
            desc[x.get('desc')] += 1
        elif x.tag == 'notation' and x.get('key') and v == 'diplo':
            desc[x.get('key')] += 1
        elif x.tag == 'foreign':
            kinds['lang_' + x.get('lang', '')] += 1
            for w in re.findall(r'[^\W\d_]{3,}', ''.join(x.itertext())):
                langw[x.get('lang', '')][w.lower()] += 1
        elif x.tag == 'hi' and x.get('rend') in ('code', 'coded'):
            kinds['coded'] += 1
        elif x.tag == 'ref':
            kinds['xref'] += 1
        elif x.tag == 'person':
            kinds['person'] += 1
FLD = [('person', 'Personen (Normform)', 'persons.html'), ('lang_en', 'Englisch', None), ('lang_fr', 'Französisch', None),
       ('lang_la', 'Latein', None), ('coded', 'Geheimschrift', None), ('xref', 'Querverweise', None)]
fl = ''.join(f'<tr><td>{t("fld." + k, de)}</td><td class="muted">{kinds.get(k, 0)}</td><td>'
             + (f'<a href="{href}">{t("fld.open", "öffnen")}</a>' if href else
                f'<a href="search.html?f={k}&q=*&v=both">{t("fld.all", "alle Stellen")}</a>') + '</td></tr>' for k, de, href in FLD)
lang = ''.join(f'<details><summary>{t("fld.lang_" + lg, LN)} <span class="muted">({len(langw[lg])} {t("fld.words", "Wörter")})</span></summary><p class="ui">' +
               ' · '.join(f'<a href="search.html?f=lang_{lg}&q={E(w)}&v=both">{E(w)}</a> <span class="muted">{c}</span>' for w, c in langw[lg].most_common(400)) + '</p></details>'
               for lg, LN in (('en', 'Englisch'), ('fr', 'Französisch'), ('la', 'Latein')) if langw[lg])
dl = ''.join(f'<div data-k="{E(fold(d))}"><a href="search.html?f=notation&q={E(chr(34) + d + chr(34))}&v=both">{E(d)}</a> <span class="muted">{c}</span></div>'
             for d, c in sorted(desc.items(), key=lambda x: -x[1]) if len(d) < 140)
body = (f'<h1>{t("fld.title", "Felder der Edition")}</h1><p class="about">{t("fld.about", "Die Edition kennzeichnet Personen, fremdsprachige Stellen, Geheimschrift, Querverweise, Notation und Graphik mit eigenen Feldern; hier sind sie einzeln durchsuchbar.")}</p>'
        f'<table class="ui">{fl}</table><h2>{t("fld.langs", "Fremdsprachige Stellen: Wörter")}</h2>{lang}'
        f'<h2>{t("fld.descr", "Deskriptoren von Notation und Graphik")}</h2><input class="filter" data-target="#dlist" data-i18n-placeholder="fld.filter" placeholder="Deskriptor filtern …"> <span class="muted">{len(desc)}</span>'
        f'<div id="dlist" class="ui" style="columns:2">{dl}</div>')
open(os.path.join(site, 'fields.html'), 'w', encoding='utf-8').write(R.shell('Felder', body, '', 'fields', {'kind': 'fields'}))

# ---- figure review pages
for (n, v), r in docs.items():
    if v != 'norm':
        continue
    rowsf = []; pg = ''
    for e in r.iter():
        if e.tag == 'pb':
            pg = e.get('n', '')
        elif e.tag == 'figure':
            d = E(e.get('desc', '') or '')
            if e.get('src'):
                note = t('figs.unanchored', 'unverankert') if e.get('place') == 'unanchored' else t('figs.beforef', 'vor Formel') if e.get('place') else ''
                rowsf.append(f'<tr><td>{E(pg)}</td><td>{d}</td><td><img src="../{E(e.get("src"))}" style="max-width:600px;background:#fff" loading="lazy"></td><td>{note}</td></tr>')
            else:
                rowsf.append(f'<tr class="muted"><td>{E(pg)}</td><td>{d}</td><td>{t("figs.missing", "— nicht übertragen —")}</td><td></td></tr>')
    if rowsf:
        body = (f'<p><a href="../items/{E(n)}.norm.html">← Item {E(n)}</a></p><h1>{t("figs.title", "Abbildungen")}: Item {E(n)}</h1>'
                f'<table class="ui"><tr><th>{t("figs.page", "Seite")}</th><th>{t("figs.desc", "Beschreibung (BEE)")}</th><th>{t("figs.img", "Bild")}</th><th></th></tr>{"".join(rowsf)}</table>')
        open(os.path.join(site, 'figures', f'{n}.html'), 'w', encoding='utf-8').write(R.shell(f'Abbildungen {n}', body, '../', 'figures', {'kind': 'figures'}))

# ---- my work
body = (f'<h1>{t("mine.title", "Meine Arbeit")}</h1><p class="about">{t("mine.about", "Lesezeichen, Markierungen und Notizen werden nur in diesem Browser gespeichert. Mit „Sichern“ und „Laden“ lassen sie sich als Datei mitnehmen.")}</p>'
        f'<p class="ui"><button type="button" id="exp">{t("mine.export", "In Datei sichern")}</button> <label>{t("mine.import", "Aus Datei laden")}: <input type="file" id="imp" accept=".json"></label></p>'
        f'<h2>{t("mine.bookmarks", "Lesezeichen")}</h2><div id="bm" class="ui"></div>'
        f'<h2>{t("mine.marks", "Markierungen")}</h2><p class="ui">{t("mine.color", "Farbe")}: <select id="mk-color"><option value="">*</option><option>1</option><option>2</option><option>3</option><option>4</option></select> '
        f'<span class="muted">{t("mine.markhint", "Text markieren: auswählen, dann Farbe in der kleinen Leiste wählen; Klick auf eine Markierung: Kommentar (– löscht).")}</span></p><div id="mk" class="ui"></div>'
        f'<h2>{t("mine.notes", "Notizen")}</h2><p class="ui"><select id="nt-list"></select> <button type="button" id="nt-new">{t("mine.new", "neu")}</button> <button type="button" id="nt-del">{t("mine.delete", "löschen")}</button> '
        f'<span class="muted">{t("mine.notehint", "✎ in der Leiste über einer Auswahl fügt den Text mit Quelle in die aktuelle Notiz ein.")}</span></p>'
        f'<textarea id="nt" style="width:100%;height:18em;font:14px/1.5 system-ui,sans-serif"></textarea>')
open(os.path.join(site, 'mine.html'), 'w', encoding='utf-8').write(
    R.shell('Meine Arbeit', body, '', 'mine', {'kind': 'mine'}).replace('</body>', '<script defer src="assets/mine.js"></script></body>'))

# ---- search page (data from bee_search2.py)
body = (f'<h1>{t("s.title", "Suche")}</h1>'
        '<form id="f" class="ui"><p><input type="text" id="q" class="filter" style="width:70%" autocomplete="off" data-i18n-placeholder="s.ph" placeholder="z.B. Familienähnlich*, Sprachspiel NEAR/5 Regel, &quot;Bild der Wirklichkeit&quot;"> '
        f'<button>{t("s.go", "Suchen")}</button></p>'
        f'<p>{t("s.in", "Suchen in")}: <select id="s-field"><option value="">{t("s.f.full", "Volltext")}</option>'
        f'<option value="title">{t("s.f.title", "Titel der Items")}</option><option value="person">{t("fld.person", "Personen (Normform)")}</option>'
        f'<option value="lang_en">{t("fld.lang_en", "Englisch")}</option><option value="lang_fr">{t("fld.lang_fr", "Französisch")}</option><option value="lang_la">{t("fld.lang_la", "Latein")}</option>'
        f'<option value="coded">{t("fld.coded", "Geheimschrift")}</option><option value="xref">{t("fld.xref", "Querverweise")}</option>'
        f'<option value="notation">{t("s.f.notation", "Notation und Graphik (Deskriptoren)")}</option></select> '
        f'{t("s.where", "Bereich")}: <select id="s-scope"></select></p>'
        f'<p><label><input type="radio" name="v" value="norm" checked> {t("s.v.norm", "normalisiert (Bemerkungen)")}</label> '
        f'<label><input type="radio" name="v" value="diplo"> {t("s.v.diplo", "diplomatisch (Seiten)")}</label> '
        f'<label><input type="radio" name="v" value="both"> {t("s.v.both", "beide")}</label> · '
        f'{t("s.years", "Jahre")}: <input id="s-y0" size="4" placeholder="1914"> – <input id="s-y1" size="4" placeholder="1951"> · '
        f'{t("s.show", "Anzeige")}: <select id="s-mode"><option value="items">{t("s.mode.items", "nach Items")}</option><option value="list">{t("s.mode.list", "Stellenliste")}</option></select></p>'
        f'<details><summary class="muted">{t("s.help", "Suchsprache")}</summary><table class="ui">'
        f'<tr><td><code>Satz Bild</code></td><td>{t("s.h.and", "beide Wörter in derselben Einheit")}</td></tr>'
        f'<tr><td><code>Satz OR Bild</code></td><td>{t("s.h.or", "eines der Wörter (auch ODER, |)")}</td></tr>'
        f'<tr><td><code>Satz -Bild</code></td><td>{t("s.h.not", "ohne das zweite Wort (auch NOT, NICHT)")}</td></tr>'
        f'<tr><td><code>"Bild der Wirklichkeit"</code></td><td>{t("s.h.phrase", "genaue Wortfolge")}</td></tr>'
        f'<tr><td><code>Sprachspiel*</code> <code>Br?der</code> <code>*spiel</code></td><td>{t("s.h.mask", "Masken: * beliebig viele, ? genau ein Zeichen")}</td></tr>'
        f'<tr><td><code>Regel NEAR/5 folgen</code></td><td>{t("s.h.near", "höchstens 5 Wörter Abstand (NEAR allein: 20)")}</td></tr>'
        f'<tr><td><code>(Satz OR Bild) Wirklichkeit</code></td><td>{t("s.h.paren", "Klammern")}</td></tr>'
        f'<tr><td><code>person:frege</code> <code>lang_la:*</code> <code>coded:liebe</code></td><td>{t("s.h.field", "ein Feld: person, lang_en, lang_fr, lang_la, coded, notation, xref, title")}</td></tr>'
        f'</table><p class="muted">{t("s.h.fold", "Groß-/Kleinschreibung, Akzente und ß/ss werden nicht unterschieden. Einheit: in der normalisierten Transkription die Bemerkung, in der diplomatischen die Seite.")}</p></details>'
        '<div id="forms"></div></form><div id="r"></div>')
open(os.path.join(site, 'search.html'), 'w', encoding='utf-8').write(
    R.shell('Suche', body, '', 'search', {'kind': 'search'}).replace('</body>', '<script defer src="assets/search.js"></script></body>'))
print(len(docs), 'documents,', len(series), 'series,', len(pers), 'persons,', len(desc), 'descriptors')
