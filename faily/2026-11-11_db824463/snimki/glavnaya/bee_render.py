#!/usr/bin/env python3
"""bee_render.py — HTML for the site: item pages, series pages, guide texts, and the page shell.
Styles and behaviour live in assets/bee.css, assets/bee.js and assets/i18n.js; pages only carry
data-i18n keys (with German text as fallback) so that the interface language can be switched."""
import html, re
import xml.etree.ElementTree as ET

E = html.escape
OTHER = None          # the other transcription of the item (set per page)
OTHER_PAGES = None    # page anchors that exist there
YEAR_ONLY = False     # per item: "1 Jan, YYYY" stands for "only the year is known"
LANGNAME = {'en': 'English', 'fr': 'Français', 'la': 'Latina'}


def t(key, de):
    return f'<span data-i18n="{key}">{E(de)}</span>'


def pid(k):
    return 'p-' + re.sub(r'[^\w.-]', '_', k.get('n', ''))


def pb(k):
    f = k.get('facs')
    tip = f' title="{E(f)}"' if f else ''
    badge = f'<span class="pb" id="{pid(k)}"{tip}>{E(k.get("n", ""))}</span>'
    if OTHER and (OTHER_PAGES is None or pid(k) in OTHER_PAGES):
        badge = f'<a class="pbx" href="{E(OTHER)}#{pid(k)}" data-i18n-title="tb.samepage" title="dieselbe Seite in der anderen Transkription">{badge}</a>'
    return badge


def fdate(d):
    if not d:
        return ''
    parts = []
    for x in d.split(' | '):
        m = re.match(r'^1 Jan, (\d{4})$', x.strip())
        if YEAR_ONLY and m:
            parts.append(f'<span data-i18n-title="date.yearonly" title="nur das Jahr ist bekannt">{m.group(1)}</span>')
        else:
            parts.append(E(x))
    return ' | '.join(parts)


def inline(el, out, root='../'):
    if el.text:
        out.append(E(el.text))
    for k in el:
        tg = k.tag
        if tg == 'hi':
            r = k.get('rend')
            tag = {'b': 'b', 'i': 'i', 'u': 'u', 'sup': 'sup', 'sub': 'sub'}.get(r)
            if tag:
                out.append(f'<{tag}>'); inline(k, out, root); out.append(f'</{tag}>')
            else:
                tip = ' data-i18n-title="t.code" title="Geheimschrift"' if r in ('code', 'coded') else ''
                out.append(f'<span class="{E(r or "")}"{tip}>'); inline(k, out, root); out.append('</span>')
        elif tg == 'ed':
            out.append('<span class="ed">'); inline(k, out, root); out.append('</span>')
        elif tg == 'del':
            out.append('<del>'); inline(k, out, root); out.append('</del>')
        elif tg == 'foreign':
            lg = k.get('lang', '')
            out.append(f'<span class="foreign" lang="{E(lg)}" title="{E(LANGNAME.get(lg, lg))}">'); inline(k, out, root); out.append('</span>')
        elif tg == 'ref':
            tgt = k.get('target')
            if tgt:
                out.append(f'<a class="xref" href="{E(root)}{E(tgt)}" data-i18n-title="t.xref" title="Querverweis">'); inline(k, out, root); out.append('</a>')
            else:
                out.append('<span class="xref">'); inline(k, out, root); out.append('</span>')
        elif tg == 'app':
            rd = [x for x in k if x.tag == 'rdg']
            tip = ' | '.join(''.join(x.itertext()).strip() for x in rd)
            out.append(f'<span class="app" title="{E(tip)}">')
            for x in k:
                out.append(f'<span class="{x.tag}">'); inline(x, out, root); out.append('</span> ' if x.tag == 'rdg' else '</span>')
            out.append('</span>')
        elif tg == 'person':
            key = k.get('key', '')
            out.append(f'<span class="person">[<a href="{E(root)}persons.html#{E(key)}">{E(key)}</a>]</span>')
        elif tg == 'formula':
            n = k.get('notation') or k.get('tex') or ''
            body = []
            inline(k, body, root)
            out.append(f'<code class="f" title="{E(n)}">{"".join(body) or E(k.get("tex", ""))}</code>')
        elif tg == 'figure':
            if k.get('src'):
                out.append(f'<img class="fig" src="{E(root)}{E(k.get("src"))}" alt="{E(k.get("desc", ""))}" title="{E(k.get("desc", ""))}" loading="lazy">')
            else:
                out.append(f'<span class="figmiss" data-i18n-title="t.figmiss" title="Abbildung (nicht übertragen)">{E(k.get("desc", "Abbildung"))}</span>')
        elif tg == 'notation':
            out.append(f'<span class="notation">{E(k.get("key", ""))}</span>')
        elif tg == 'subst':
            out.append('<span class="subst">'); inline(k, out, root); out.append('</span>')
        elif tg == 'add':
            pl = k.get('place', '')
            o, c = ('«', '»') if pl == 'interlinear' else ('‹', '›')
            out.append(f'<span class="add {E(pl)}"><span class="ed">{o}</span>'); inline(k, out, root); out.append(f'<span class="ed">{c}</span></span>')
        elif tg == 'pb':
            out.append(pb(k))
        elif tg == 'date':
            out.append(f'<span class="dt">{fdate(k.get("when", ""))}</span>')
        elif tg == 'lb':
            out.append('<br class="lb">')
        elif tg == 'num':
            out.append(f'<span class="num">{E(k.text or "")}</span>')
        else:
            inline(k, out, root)
        if k.tail:
            out.append(E(k.tail))


def shell(title, body, root='../', bodyclass='', data=None, toolbar=''):
    attrs = ''.join(f' data-{k}="{E(str(v))}"' for k, v in (data or {}).items())
    nav = (f'<nav><a href="{root}index.html">{t("nav.home", "Inhalt")}</a>'
           f'<a href="{root}search.html">{t("nav.search", "Suche")}</a>'
           f'<a href="{root}persons.html">{t("nav.persons", "Personen")}</a>'
           f'<a href="{root}fields.html">{t("nav.fields", "Felder")}</a>'
           f'<a href="{root}intro/introduction.html">{t("nav.intro", "Einführung")}</a>'
           f'<a href="{root}mine.html">{t("nav.mine", "Meine Arbeit")}</a></nav>')
    search = (f'<form action="{root}search.html"><input type="search" name="q" data-i18n-placeholder="nav.searchph" '
              f'placeholder="Volltextsuche …"></form>')
    return (f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{E(title)} — BEE</title><link rel="stylesheet" href="{root}assets/bee.css">'
            f'<script src="{root}assets/i18n.js"></script><script defer src="{root}assets/bee.js"></script></head>'
            f'<body class="{E(bodyclass)}" data-root="{root}"{attrs}>'
            f'<header class="top"><a class="brand" href="{root}index.html">Wittgenstein\'s Nachlass · BEE</a>{nav}'
            f'<span class="sp"></span>{search}<button type="button" class="viewbtn" data-i18n-title="nav.view" title="Ansicht">¶</button>'
            f'<span class="langs"></span></header>{toolbar}<main>{body}</main></body></html>')


def item_toolbar(n, version, prev_n=None, next_n=None, figs=False):
    other = 'diplo' if version == 'norm' else 'norm'
    parts = ['<div class="tb">']
    if OTHER:
        parts.append(f'<a href="{E(OTHER)}">{t("tb.other_" + other, "diplomatisch" if other == "diplo" else "normalisiert")}</a>')
    if figs:
        parts.append(f'<a href="../figures/{E(n)}.html">{t("tb.figs", "Abbildungen")}</a>')
    if prev_n:
        parts.append(f'<a href="{E(prev_n)}.{version}.html" data-i18n-title="tb.prev" title="vorige Einheit">◀ {E(prev_n)}</a>')
    if next_n:
        parts.append(f'<a href="{E(next_n)}.{version}.html" data-i18n-title="tb.next" title="nächste Einheit">{E(next_n)} ▶</a>')
    parts.append(f'<span class="grp">{t("tb.goto", "Seite")} <select class="gotopage"></select></span>')
    parts.append(f'<label><input type="checkbox" data-toggle="alts"> {t("tb.alts", "Alternativen")}</label>')
    parts.append(f'<label><input type="checkbox" data-toggle="persons"> {t("tb.persons", "Personenregister")}</label>')
    parts.append(f'<label><input type="checkbox" data-toggle="descr"> {t("tb.descr", "Deskriptoren")}</label>')
    parts.append(f'<label><input type="checkbox" data-toggle="nohidden"> {t("tb.nohidden", "ohne Randangaben")}</label>')
    parts.append(f'<label><input type="checkbox" data-toggle="langs-on"> {t("tb.langs", "Sprachen zeigen")}</label>')
    if version == 'diplo':
        parts.append(f'<label><input type="checkbox" data-toggle="nolb"> {t("tb.nolb", "ohne Zeilenumbrüche")}</label>')
    parts.append(f'<button type="button" class="bmbtn">☆ {t("tb.bookmark", "Lesezeichen")}</button>')
    parts.append(f'<span class="hits"><button type="button" class="hitprev" data-i18n-title="tb.hitprev" title="voriger Treffer (N)">▲</button>'
                 f'<span class="hitpos"></span><button type="button" class="hitnext" data-i18n-title="tb.hitnext" title="nächster Treffer (n)">▼</button>'
                 f'<button type="button" class="hitall">{t("tb.hitall", "alle markieren")}</button></span>')
    parts.append('</div>')
    return ''.join(parts)


def render_body(item, root='../'):
    global YEAR_ONLY
    n = item.get('n'); title = item.get('title', '')
    ds = [d for e in item.iter() for d in ((e.get('date') or e.get('when') or '').split(' | ')) if d]
    YEAR_ONLY = bool(ds) and sum(1 for d in ds if d.startswith('1 Jan,')) >= 0.5 * len(ds)
    rk = 0
    out = [f'<h1 id="item-{E(n)}">Item {E(n)} {E(title)}</h1>']
    resp = [(key, de, item.get(a)) for key, de, a in (('t.transcr', 'Transkription', 'transcribers'),
                                                        ('t.proof', 'Korrektur', 'proofreaders')) if item.get(a)]
    if resp:
        out.append('<p class="resp">' + ' · '.join(f'{t(key, de)}: {E(v)}' for key, de, v in resp) + '</p>')
    for el in item:
        if el.tag == 'pb':
            out.append(f'<p class="pbl">{pb(el)}</p>')
        elif el.tag == 'date':
            out.append(f'<p><span class="dt">{fdate(el.get("when", ""))}</span></p>')
        elif el.tag == 'rec':
            meta = E(el.get('page', '')) + ('<br>' + fdate(el.get('date')) if el.get('date') else '')
            out.append(f'<div class="rec" id="r-{E(n)}-{rk}"><span class="meta">{meta}</span>')
            rk += 1
            for p in el:
                if p.tag == 'pb':
                    out.append(f'<p class="pbl">{pb(p)}</p>'); continue
                if p.tag == 'date':
                    out.append(f'<p><span class="dt">{fdate(p.get("when", ""))}</span></p>'); continue
                cls = p.get('rend')
                buf = []
                inline(p, buf, root)
                out.append(f'<p{" class=" + chr(34) + cls + chr(34) if cls else ""}>{"".join(buf)}</p>')
            out.append('</div>')
    notes = [x for x in item.iter('note')]
    if notes:
        out.append(f'<section class="notes"><h2>{t("t.popups", "Anmerkungen der Edition (Popup-Notizen, ohne Ankerstelle)")}</h2><ol>')
        for x in notes:
            out.append(f'<li>{E(x.text or "")}</li>')
        out.append('</ol></section>')
    return out


def render_item(item, prev_n=None, next_n=None):
    v = item.get('version'); n = item.get('n')
    figs = v == 'norm' and any(x.get('src') for x in item.iter('figure'))
    body = ''.join(render_body(item))
    return shell(f'Item {n} {item.get("title", "")}', body, '../', v, {'item': n, 'version': v, 'kind': 'item'},
                 item_toolbar(n, v, prev_n, next_n, figs))


def render_series(items, title, about=''):
    v = items[0].get('version')
    parts = [f'<h1 class="series">{E(title)}</h1>']
    if about:
        parts.append(f'<p class="about">{E(about)}</p>')
    parts.append('<nav class="toc">' + ' · '.join(f'<a href="#item-{E(i.get("n"))}">{E(i.get("n"))}</a>' for i in items) + '</nav>')
    for it in items:
        parts.extend(render_body(it))
    global OTHER
    OTHER = None
    tb = item_toolbar('', v)
    return shell(title, ''.join(parts), '../', v, {'version': v, 'kind': 'series'}, tb)


def render_doc(doc, toc_links):
    """guide texts: <doc> with <head>, <p>, <table><row><cell>, <notes>"""
    out = [f'<h1>{E(doc.get("title", ""))}</h1>']
    heads = []
    body = []
    k = 0
    for el in doc:
        if el.tag == 'head':
            k += 1
            heads.append((k, el.text or ''))
            body.append(f'<h2 id="h{k}">{E(el.text or "")}</h2>')
        elif el.tag == 'p':
            buf = []; inline(el, buf, '../')
            cls = el.get('rend')
            body.append(f'<p{" class=" + chr(34) + cls + chr(34) if cls else ""}>{"".join(buf)}</p>')
        elif el.tag == 'table':
            rows = []
            for r in el:
                cells = []
                for c in r:
                    buf = []; inline(c, buf, '../'); cells.append(f'<td>{"".join(buf)}</td>')
                rows.append('<tr>' + ''.join(cells) + '</tr>')
            body.append('<table class="doc">' + ''.join(rows) + '</table>')
        elif el.tag == 'notes':
            body.append(f'<section class="notes"><h2>{t("t.docnotes", "Anmerkungen")}</h2><ol>' +
                        ''.join(f'<li>{E(x.text or "")}</li>' for x in el) + '</ol></section>')
    out.append('<p class="about">' + ' · '.join(toc_links) + '</p>')
    if heads:
        out.append('<nav class="toc">' + ' · '.join(f'<a href="#h{i}">{E(h)}</a>' for i, h in heads) + '</nav>')
    out.extend(body)
    return shell(doc.get('title', ''), ''.join(out), '../', 'doc', {'kind': 'doc'})
