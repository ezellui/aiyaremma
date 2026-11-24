#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертер HTML-выпуска «Изоморфизмы» -> XeLaTeX с вёрсткой научного журнала.

Использование:
    python3 convert.py izomorfizmy-vypusk-polnyj.html izomorfizmy.tex

Принципы:
  * содержимое не теряется: рендерятся все виды (обложка, предисловие, содержание,
    пять статей, послесловие) со всеми разделами, аннотациями, примечаниями,
    библиографиями и колофонами;
  * отбрасывается только веб-навигация (верхняя панель, пейджеры, кнопки) — это не текст;
  * шрифты Old Standard TT и Spectral подключаются через fontspec из папки fonts/;
  * формулы переносятся как есть (LaTeX-математика внутри $...$ и $$...$$);
  * примечания сохраняются как затекстовые («Примечания») со сверхиндексными отсылками,
    1:1 как в HTML.
"""
import sys, re
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = sys.argv[1] if len(sys.argv) > 1 else 'izomorfizmy-vypusk-polnyj.html'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'izomorfizmy.tex'

soup = BeautifulSoup(open(SRC, encoding='utf-8').read(), 'html.parser')

# ----- акцентные цвета по классам обёрток -----
ACMAP = {'matter': 'matter', 'art-derrida': 'derrida', 'art-leibniz': 'leibniz',
         'art-hegel': 'hegel', 'art-nietzsche': 'nietzsche', 'art-levinas': 'levinas'}
GO2COL = {'derrida': 'Cderrida', 'leibniz': 'Cleibniz', 'hegel': 'Chegel',
          'nietzsche': 'Cnietzsche', 'levinas': 'Clevinas',
          'preface': 'Cmatter', 'contents': 'Cmatter', 'afterword': 'Cmatter'}

# ----- экранирование текста -----
UNI = {'\u00a0': '~', '§': r'\S{}', '↔': r'\(\leftrightarrow\)',
       '⁂': r'{\color{gold}\ding{167}}', '❦': r'{\color{gold}\ding{167}}'}
SPECIAL = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '#': r'\#',
           '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
           '^': r'\textasciicircum{}', '$': r'\$'}

def esc(t):
    out = []
    for ch in t:
        if ch in UNI:
            out.append(UNI[ch])
        elif ch in SPECIAL:
            out.append(SPECIAL[ch])
        else:
            out.append(ch)
    return ''.join(out)

def text_math(t):
    # сохраняем строчную математику $...$ дословно, экранируем остальное
    parts = re.split(r'(\$[^$]*\$)', t)
    res = []
    for p in parts:
        if len(p) >= 2 and p[0] == '$' and p[-1] == '$':
            res.append(p)
        else:
            res.append(esc(p))
    return ''.join(res)

# ----- рекурсивный инлайновый рендер -----
def render_children(node, accent_em=False):
    return ''.join(render_one(c, accent_em) for c in node.children)

def render_one(c, accent_em=False):
    if isinstance(c, NavigableString):
        return text_math(str(c))
    if isinstance(c, Tag):
        return render_tag(c, accent_em)
    return ''

def render_tag(c, accent_em):
    cls = c.get('class') or []
    nm = c.name
    if nm in ('em', 'i') or (nm == 'span' and any(x in cls for x in ('fr', 'lat', 'de', 'term'))):
        inner = render_children(c, accent_em)
        return ('\\emcolor{' + inner + '}') if accent_em else ('\\textit{' + inner + '}')
    if nm in ('strong', 'b'):
        return '\\textbf{' + render_children(c, accent_em) + '}'
    if nm == 'sup' and 'fn' in cls:
        return '\\textsuperscript{' + esc(c.get_text().strip()) + '}'
    if nm == 'br':
        return '\\\\ '
    return render_children(c, accent_em)

# ----- блочные элементы -----
def divider():
    return '\\par\\begin{center}{\\color{gold}\\large\\ding{167}}\\end{center}\\par\n'

def render_sectio(p):
    return '\\begin{center}{\\displayfont\\small\\color{accent}\\spaced{%s}}\\end{center}\n' % esc(p.get_text().strip())

def render_titleblock(div):
    h1 = div.find('h1', class_='title')
    sub = div.find(class_='subtitle')
    by = div.find(class_='byline')
    title = render_children(h1, accent_em=True).strip()
    s = ['\\begin{center}\n']
    s.append('{\\displayfont\\bfseries\\fontsize{25}{29}\\selectfont %s}\\par\\vspace{0.5em}\n' % title)
    if sub:
        s.append('{\\lightfont\\itshape\\large %s}\\par\\vspace{0.7em}\n' % render_children(sub).strip())
    if by:
        s.append('{\\color{accentdeep}\\footnotesize\\spaced{%s}}\\par\n' % esc(by.get_text().strip()))
    s.append('\\end{center}\\vspace{0.4em}\n')
    return ''.join(s)

def render_abstract(div):
    lbl = div.find('span', class_='lbl')
    kw = div.find('div', class_='kw')
    label = lbl.get_text().strip() if lbl else 'Аннотация'
    kwtext = render_children(kw).strip() if kw else ''
    bparts = []
    for c in div.children:
        if isinstance(c, Tag):
            ccls = c.get('class') or []
            if 'lbl' in ccls or 'kw' in ccls:
                continue
        bparts.append(render_one(c))
    body = ''.join(bparts).strip()
    return '\\abstractblock{%s}{%s}{%s}\n' % (esc(label), body, kwtext)

def render_lede(p):
    inner = render_children(p).lstrip()
    if inner and inner[0].isalpha():
        first, rest = inner[0], inner[1:]
        return '\\lettrine[lines=3,findent=2pt,nindent=4pt]{\\dropcap{%s}}{}%s\\par\n' % (first, rest)
    return inner + '\\par\n'

def render_section(sec):
    out = []
    for c in sec.children:
        if isinstance(c, NavigableString):
            s = str(c)
            if '$$' in s:
                for m in re.findall(r'\$\$(.+?)\$\$', s, re.S):
                    out.append('\\[%s\\]\n' % m.strip())
            continue
        if not isinstance(c, Tag):
            continue
        cls = c.get('class') or []
        nm = c.name
        if nm == 'h2':
            num_el = c.find('span', class_='num')
            num = esc(num_el.get_text().strip()) if num_el else ''
            tparts = []
            for cc in c.children:
                if isinstance(cc, Tag) and cc.name == 'span' and 'num' in (cc.get('class') or []):
                    continue
                tparts.append(render_one(cc))
            title = ''.join(tparts).strip()
            out.append('\\artsection{%s}{%s}\n' % (num, title))
        elif nm == 'p' and 'lede' in cls:
            out.append(render_lede(c))
        elif nm in ('div', 'p') and 'pull' in cls:
            out.append('\\begin{pullquoteenv}\\itshape %s\\end{pullquoteenv}\n' % render_children(c).strip())
        elif nm == 'div' and 'divider' in cls:
            out.append(divider())
        elif nm == 'p':
            out.append(render_children(c).strip() + '\\par\n')
    return ''.join(out)

def render_notes(div):
    h3 = div.find('h3')
    label = h3.get_text().strip() if h3 else 'Примечания'
    ol = div.find('ol')
    s = ['\\notessection{%s}\n\\begin{notelist}\n' % esc(label)]
    for li in ol.find_all('li', recursive=False):
        s.append('\\item ' + render_children(li).strip() + '\n')
    s.append('\\end{notelist}\n')
    return ''.join(s)

def render_biblio(div):
    h3 = div.find('h3')
    label = h3.get_text().strip() if h3 else 'Библиография'
    s = ['\\notessection{%s}\n' % esc(label)]
    for p in div.find_all('p', recursive=False):
        s.append('{\\small\\hangindent=1.3em\\hangafter=1\\noindent %s\\par}\n' % render_children(p).strip())
    return ''.join(s)

def render_colophon(p):
    return '\\par\\vspace{1.1em}\\begin{center}\\itshape\\small %s\\end{center}\n' % render_children(p).strip()

def render_explicit(p):
    return '\\par\\vspace{1.4em}\\begin{center}{\\displayfont\\footnotesize\\color{accent}\\spaced{%s}}\\end{center}\n' % esc(p.get_text().strip())

def render_contents_list(ul):
    out = ['\\par\\addvspace{1em}\n']
    for li in ul.find_all('li', recursive=False):
        go = li.get('data-go')
        col = GO2COL.get(go, 'Cmatter')
        num = esc(li.find(class_='ce-num').get_text().strip())
        title = esc(li.find(class_='ce-title').get_text().strip())
        be = li.find(class_='ce-bridge')
        bridge = esc(be.get_text().strip()) if be else ''
        ge = li.find(class_='ce-gloss')
        gloss = esc(ge.get_text().strip()) if ge else ''
        out.append('\\noindent{\\displayfont\\large\\color{%s}%s}\\hspace{0.6em}{\\displayfont\\large %s}' % (col, num, title))
        if bridge:
            out.append(' {\\itshape\\small %s}' % bridge)
        out.append('\\par\n')
        if gloss:
            out.append('{\\small\\color{accentdeep} %s}\\par\n' % gloss)
        out.append('\\vspace{0.7em}\n')
    return ''.join(out)

def render_generic(wrap):
    out = []
    for c in wrap.children:
        if not isinstance(c, Tag):
            continue
        cls = c.get('class') or []
        nm = c.name
        if nm == 'p' and 'sectio' in cls:
            out.append(render_sectio(c))
        elif nm == 'div' and 'titleblock' in cls:
            out.append(render_titleblock(c))
        elif nm == 'div' and 'abstract' in cls:
            out.append(render_abstract(c))
        elif nm == 'section':
            out.append(render_section(c))
        elif nm == 'div' and 'divider' in cls:
            out.append(divider())
        elif nm == 'div' and 'notes' in cls:
            out.append(render_notes(c))
        elif nm == 'div' and 'biblio' in cls:
            out.append(render_biblio(c))
        elif nm == 'p' and 'colophon' in cls:
            out.append(render_colophon(c))
        elif nm == 'p' and 'explicit' in cls:
            out.append(render_explicit(c))
        elif nm == 'ul' and 'contents-list' in cls:
            out.append(render_contents_list(c))
        elif nm == 'p' and 'lede' in cls:
            out.append(render_lede(c))
        elif nm in ('div', 'p') and 'pull' in cls:
            out.append('\\begin{pullquoteenv}\\itshape %s\\end{pullquoteenv}\n' % render_children(c).strip())
        elif nm == 'p':
            out.append(render_children(c).strip() + '\\par\n')
        # pager и прочая навигация — пропускаем
    return ''.join(out)

def render_cover(v):
    cov = v.find(class_='cover')
    venue = esc(cov.find(class_='venue').get_text().strip())
    issuetag = esc(cov.find(class_='issue-tag').get_text().strip())
    h1 = esc(cov.find('h1').get_text().strip())
    csub = esc(cov.find(class_='csub').get_text().strip())
    s = ['\\begin{titlepage}\n\\centering\n\\vspace*{1.8cm}\n']
    s.append('{\\displayfont\\color{accent}\\spaced{%s}}\\par\\vspace{0.5cm}\n' % venue)
    s.append('{\\color{gold}\\rule{3.2cm}{0.4pt}}\\par\\vspace{0.5cm}\n')
    s.append('{\\lightfont\\itshape %s}\\par\\vspace{1.7cm}\n' % issuetag)
    s.append('{\\displayfont\\bfseries\\fontsize{52}{56}\\selectfont %s}\\par\\vspace{0.5cm}\n' % h1)
    s.append('{\\lightfont\\itshape\\Large %s}\\par\\vspace{1.5cm}\n' % csub)
    s.append('\\begin{minipage}{0.88\\textwidth}\n')
    for li in cov.select('.toc-list li'):
        go = li.get('data-go')
        title = esc(li.find(class_='cl-title').get_text().strip())
        bridge = esc(li.find(class_='cl-bridge').get_text().strip())
        col = GO2COL.get(go, 'Cmatter')
        s.append('\\noindent\\textcolor{%s}{\\rule{1.5ex}{1.5ex}}\\hspace{0.7em}{\\displayfont\\large %s}\\hspace{0.5em}{\\itshape\\small %s}\\par\\vspace{0.55em}\n' % (col, title, bridge))
    s.append('\\end{minipage}\n\\vfill\n\\end{titlepage}\n')
    return ''.join(s)

def set_accent(cls):
    n = ACMAP.get(cls, 'matter')
    return '\\colorlet{accent}{C%s}\\colorlet{accentdeep}{Cd%s}\\colorlet{abstractbg}{C%s!7}\n' % (n, n, n)

# ----- преамбула -----
PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage{geometry}
\geometry{paperwidth=176mm,paperheight=250mm,top=22mm,bottom=24mm,inner=24mm,outer=20mm}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setotherlanguage{english}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{xcolor}
\usepackage{mdframed}
\usepackage{lettrine}
\usepackage{pifont}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}

\setmainfont{Spectral}[Path=fonts/,Extension=.ttf,UprightFont=Spectral-Regular,ItalicFont=Spectral-Italic,BoldFont=Spectral-SemiBold,BoldItalicFont=Spectral-SemiBoldItalic]
\newfontfamily\displayfont{Old Standard}[Path=fonts/,Extension=.ttf,UprightFont=OldStandard-Regular,ItalicFont=OldStandard-Italic,BoldFont=OldStandard-Bold,BoldItalicFont=OldStandard-Bold,BoldItalicFeatures={FakeSlant=0.18}]
\newfontfamily\lightfont{Spectral}[Path=fonts/,Extension=.ttf,UprightFont=Spectral-Light,ItalicFont=Spectral-LightItalic]

\definecolor{Cmatter}{HTML}{8A6A2E}\definecolor{Cdmatter}{HTML}{5E4720}
\definecolor{Cderrida}{HTML}{7A1F1C}\definecolor{Cdderrida}{HTML}{5E1715}
\definecolor{Cleibniz}{HTML}{243F63}\definecolor{Cdleibniz}{HTML}{16283F}
\definecolor{Chegel}{HTML}{4A2B5E}\definecolor{Cdhegel}{HTML}{2F1A3D}
\definecolor{Cnietzsche}{HTML}{A3461C}\definecolor{Cdnietzsche}{HTML}{6B2C10}
\definecolor{Clevinas}{HTML}{14595C}\definecolor{Cdlevinas}{HTML}{0B393B}
\definecolor{gold}{HTML}{9A7B3F}
\colorlet{accent}{Cmatter}\colorlet{accentdeep}{Cdmatter}\colorlet{abstractbg}{Cmatter!7}

\newcommand{\spaced}[1]{{\addfontfeature{LetterSpace=8.0}\MakeUppercase{#1}}}
\newcommand{\emcolor}[1]{\textit{\textcolor{accent}{#1}}}
\newcommand{\dropcap}[1]{{\displayfont\bfseries\color{accent}#1}}
\newcommand{\artsection}[2]{\par\addvspace{1.7ex}\noindent{\displayfont\large{\color{accent}\itshape #1}\hspace{0.45em}#2}\par\nobreak\vspace{0.6ex}\noindent}
\newcommand{\notessection}[1]{\par\addvspace{2.0ex}\noindent{\displayfont\footnotesize\color{accent}\spaced{#1}}\par\nobreak\vspace{0.7ex}}

\mdfdefinestyle{abstractstyle}{linewidth=2pt,topline=false,rightline=false,bottomline=false,linecolor=accent,backgroundcolor=abstractbg,innerleftmargin=1em,innerrightmargin=1em,innertopmargin=0.8em,innerbottommargin=0.8em,skipabove=0.8em,skipbelow=1.5em}
\newmdenv[topline=false,rightline=false,bottomline=false,linewidth=1.5pt,linecolor=gold,leftmargin=0.4em,rightmargin=1.4em,innerleftmargin=1em,innertopmargin=0.2em,innerbottommargin=0.2em,skipabove=0.9em,skipbelow=0.9em]{pullquoteenv}
\newcommand{\abstractblock}[3]{\begin{mdframed}[style=abstractstyle]{\displayfont\footnotesize\color{accent}\spaced{#1}}\par\smallskip{\small #2}\par\smallskip{\itshape\footnotesize\color{accentdeep} #3}\end{mdframed}}

\newlist{notelist}{enumerate}{1}
\setlist[notelist]{label={\color{accent}\arabic*.},leftmargin=1.8em,itemsep=0.25em,topsep=0.3em,parsep=0pt}

\setlength{\parindent}{1.1em}
\linespread{1.06}
\frenchspacing
% В этом дистрибутиве не установлены образцы переноса для русского, а XeTeX не умеет
% подгружать их во время выполнения. Поэтому вместо переносов разрешаем растяжение
% межсловных пробелов — строки не вылезают на поля (ценой иногда более «рыхлых» строк).
\tolerance=9999
\hbadness=10000
\setlength{\emergencystretch}{3.2em}

\pagestyle{fancy}\fancyhf{}
\setlength{\headheight}{14pt}
\fancyhead[C]{\footnotesize\itshape Изоморфизмы}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.2pt}

\begin{document}
'''

# ----- сборка -----
views = [v for v in soup.find_all('div') if v.get('class') and 'view' in v.get('class')]
parts = [PREAMBLE]
for v in views:
    classes = v.get('class')
    accent_class = next((c for c in classes if c in ACMAP), 'matter')
    key = (v.get('id') or '').replace('view-', '')
    parts.append(set_accent(accent_class))
    if key == 'cover':
        parts.append(render_cover(v))
        continue
    parts.append('\\clearpage\n')
    wrap = v.find('div', class_='wrap')
    parts.append(render_generic(wrap))
parts.append('\n\\end{document}\n')

open(OUT, 'w', encoding='utf-8').write(''.join(parts))
print('wrote', OUT, '(%d views)' % len(views))
