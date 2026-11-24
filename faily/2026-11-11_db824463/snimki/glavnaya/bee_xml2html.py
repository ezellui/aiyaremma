#!/usr/bin/env python3
"""bee_xml2html.py ITEM.norm.xml OUT.html — preview page of one item (for checking the conversion).
Shows the BEE legend: editorial red, last undecided alternative dark (earlier alternatives on hover
and with the 'Alternativen' switch), page anchors with facsimile names, person index, notation."""
import sys, html
import xml.etree.ElementTree as ET

CSS = """
body{margin:0;font:17px/1.6 Georgia,'Times New Roman',serif;color:#1b1b6e;background:#fbfaf7}
header{position:sticky;top:0;background:#fbfaf7ee;border-bottom:1px solid #ddd;padding:.5em 1.2em;font:14px system-ui,sans-serif;color:#444;z-index:2}
header label{margin-left:1.2em}
main{max-width:46em;margin:1.5em auto 4em;padding:0 1.2em}
h1{font:600 22px system-ui,sans-serif;color:#1b1b6e;margin:.2em 0 1em}
.rec{position:relative;margin:.15em 0 .15em 0;padding-left:0}
.rec .meta{position:absolute;left:-7.5em;width:7em;text-align:right;font:11px system-ui,sans-serif;color:#c62828;opacity:.75;top:.35em}
p{margin:.25em 0}
p.right{text-align:right} p.center{text-align:center}
.ed{color:#c62828}
.alt{color:#111}
.pb{display:inline-block;font:600 11px system-ui,sans-serif;color:#c62828;border:1px solid #f0b6b6;border-radius:3px;padding:0 .35em;margin:0 .3em;vertical-align:.15em}
.pbl{margin:1.1em 0 .2em}
.app .rdg{display:none;color:#777;text-decoration:line-through}
body.alts .app .rdg{display:inline}
.app .lem{color:#111;border-bottom:1px dotted #999}
.person{display:none;font:11px system-ui,sans-serif;color:#c62828;margin-left:.2em}
body.persons .person{display:inline}
code.f{font:15px 'DejaVu Sans Mono',monospace;color:#1b1b6e;background:#eef}
.num{font-weight:600;margin-right:.4em}
del{color:#777}
img.fig{max-width:100%;vertical-align:middle}
@media (max-width:900px){.rec .meta{position:static;display:block;text-align:left}}
"""


def inline(el, out):
    if el.text:
        out.append(html.escape(el.text))
    for k in el:
        t = k.tag
        if t == 'hi':
            r = k.get('rend')
            tag = {'b': 'b', 'i': 'i', 'u': 'u', 'sup': 'sup'}.get(r)
            if tag:
                out.append(f'<{tag}>'); inline(k, out); out.append(f'</{tag}>')
            else:
                out.append(f'<span class="{r}">'); inline(k, out); out.append('</span>')
        elif t == 'ed':
            out.append('<span class="ed">'); inline(k, out); out.append('</span>')
        elif t == 'del':
            out.append('<del>'); inline(k, out); out.append('</del>')
        elif t == 'app':
            rd = [x for x in k if x.tag == 'rdg']
            tip = ' | '.join(''.join(x.itertext()).strip() for x in rd)
            out.append(f'<span class="app" title="{html.escape(tip)}">')
            for x in k:
                out.append(f'<span class="{x.tag}">'); inline(x, out); out.append('</span> ' if x.tag == 'rdg' else '</span>')
            out.append('</span>')
        elif t == 'person':
            out.append(f'<span class="person">[{html.escape(k.get("key", ""))}]</span>')
        elif t == 'formula':
            n = k.get('notation') or k.get('tex') or ''
            out.append(f'<code class="f" title="{html.escape(n)}">{html.escape(k.text or k.get("tex", ""))}</code>')
        elif t == 'figure':
            out.append(f'<img class="fig" src="{html.escape(k.get("src"))}" alt="">')
        elif t == 'pb':
            out.append(pb(k))
        elif t == 'num':
            out.append(f'<span class="num">{html.escape(k.text or "")}</span>')
        else:
            inline(k, out)
        if k.tail:
            out.append(html.escape(k.tail))


def pb(k):
    f = k.get('facs')
    tip = f' title="{html.escape(f)}"' if f else ''
    return f'<span class="pb" id="p-{html.escape(k.get("n", "").replace(" ", "_"))}"{tip}>{html.escape(k.get("n", ""))}</span>'


def render(item):
    n = item.get('n'); title = item.get('title', '')
    out = [f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>Item {n} — BEE {item.get("version","")}</title>',
           f'<style>{CSS}</style></head><body>',
           '<header>Wittgenstein\'s Nachlass · BEE 2000 · normalisierte Transkription (Probekonvertierung)'
           '<label><input type="checkbox" onchange="document.body.classList.toggle(\'alts\',this.checked)"> Alternativen</label>'
           '<label><input type="checkbox" onchange="document.body.classList.toggle(\'persons\',this.checked)"> Personenregister</label></header>',
           f'<main><h1>Item {html.escape(n)} {html.escape(title)}</h1>']
    for el in item:
        if el.tag == 'pb':
            out.append(f'<p class="pbl">{pb(el)}</p>')
        elif el.tag == 'rec':
            meta = html.escape(el.get('page', '')) + ('<br>' + html.escape(el.get('date')) if el.get('date') else '')
            out.append(f'<div class="rec"><span class="meta">{meta}</span>')
            for p in el:
                if p.tag == 'pb':
                    out.append(f'<p class="pbl">{pb(p)}</p>'); continue
                cls = p.get('rend')
                buf = []
                inline(p, buf)
                out.append(f'<p{" class=" + chr(34) + cls + chr(34) if cls else ""}>{"".join(buf)}</p>')
            out.append('</div>')
    out.append('</main></body></html>')
    return '\n'.join(out)


if __name__ == '__main__':
    it = ET.parse(sys.argv[1]).getroot()
    open(sys.argv[2], 'w', encoding='utf-8').write(render(it))
