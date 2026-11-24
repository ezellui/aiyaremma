#!/usr/bin/env python3
"""
md2tex.py — сборка научной статьи из Markdown в TeX (XeLaTeX).

Рассчитан на разметку, которой написана статья: заголовки двух уровней,
выносные цитаты, одна таблица, сноски вида [^n] с блоком определений
«## Примечания» в конце, полужирный и курсив, нумерованные списки.

Вёрстка: одноколонная, формат 170x240 мм, FreeSerif (кириллица +
политонический греческий), сноски постранично внизу полосы.

Запуск:  python3 md2tex.py apeiron-article.md apeiron-article.tex
"""

import re
import sys

# ---------------------------------------------------------------- преамбула

PREAMBLE = r"""% !TEX program = xelatex
\documentclass[11pt,twoside]{article}

\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{russian}
\setotherlanguages{english,german,french,greek}

\setmainfont{FreeSerif}[
  Path            = /usr/share/fonts/truetype/freefont/,
  Extension       = .ttf,
  UprightFont     = *,
  ItalicFont      = *Italic,
  BoldFont        = *Bold,
  BoldItalicFont  = *BoldItalic,
  Ligatures       = TeX ]

\usepackage[
  paperwidth=170mm, paperheight=240mm,
  inner=25mm, outer=32mm, top=23mm, bottom=27mm,
  headsep=7mm, footskip=13mm ]{geometry}

\usepackage{microtype}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{ragged2e}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage[bottom,hang,flushmargin]{footmisc}
\usepackage[hidelinks]{hyperref}

% -------------------------------------------------- вертикальный ритм
\linespread{1.10}
\setlength{\parindent}{1.2em}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{1.5em}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\frenchspacing

% -------------------------------------------------- заголовки
\titleformat{\section}{\normalfont\large\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{24pt plus 8pt minus 4pt}{10pt}
\titleformat{\subsection}{\normalfont\bfseries}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{15pt plus 5pt minus 3pt}{5pt}

% -------------------------------------------------- колонтитулы
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyhead[LE]{\footnotesize\thepage\hspace{2em}\textit{Порог заимствования}}
\fancyhead[RO]{\footnotesize\textit{\rightmark}\hspace{2em}\thepage}
\fancypagestyle{plain}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}%
  \fancyfoot[C]{\footnotesize\thepage}}

% -------------------------------------------------- сноски
\setlength{\footnotemargin}{1.1em}
\renewcommand{\footnoterule}{\vspace*{6pt}\hrule width 0.28\textwidth height 0.4pt\vspace*{5pt}}
\addtolength{\skip\footins}{4pt}

% -------------------------------------------------- выносная цитата
\renewenvironment{quote}
  {\par\vspace{6pt}\begin{list}{}{%
     \setlength{\leftmargin}{1.6em}\setlength{\rightmargin}{1.0em}%
     \setlength{\listparindent}{1.0em}\setlength{\itemindent}{0pt}%
     \setlength{\parsep}{0pt}\setlength{\topsep}{0pt}}%
   \item\relax\small}
  {\end{list}\vspace{6pt}\par}

% -------------------------------------------------- шапка статьи
\newcommand{\artikeltitel}[1]{%
  \begin{center}
    {\LARGE #1\par}
  \end{center}
  \vspace{10pt}}

\newenvironment{annotatsiya}
  {\begin{list}{}{\setlength{\leftmargin}{1.6em}\setlength{\rightmargin}{1.6em}%
     \setlength{\listparindent}{1.0em}\setlength{\parsep}{4pt}\setlength{\topsep}{0pt}}%
   \item\relax\small}
  {\end{list}\vspace{6pt}}

\newcommand{\razdelitel}{%
  \par\vspace{10pt}\noindent
  \hfill\textasteriskcentered\hspace{1.2em}\textasteriskcentered\hspace{1.2em}\textasteriskcentered\hfill
  \par\vspace{10pt}}

\hypersetup{
  pdftitle  = {Порог заимствования: Chronos apeiros и to apeiron},
  pdfsubject= {История философии},
  pdfkeywords={Анаксимандр; апейрон; Зурван; иранские влияния; генезис греческой философии}}

\begin{document}
\sloppy
"""

POSTAMBLE = "\n\\end{document}\n"

# ------------------------------------------------------------- экранирование

SPECIALS = {
    '\\': r'\textbackslash{}',
    '&':  r'\&',
    '%':  r'\%',
    '$':  r'\$',
    '#':  r'\#',
    '_':  r'\_',
    '{':  r'\{',
    '}':  r'\}',
    '~':  r'\textasciitilde{}',
    '^':  r'\textasciicircum{}',
}


def escape(text):
    return ''.join(SPECIALS.get(ch, ch) for ch in text)


PLACEHOLDER = '\x00%d\x00'


def inline(text, notes, used):
    """Строчная разметка: сноски, полужирный, курсив. Экранирование —
    только для того, что осталось простым текстом."""
    stash = []

    def keep(tex):
        stash.append(tex)
        return PLACEHOLDER % (len(stash) - 1)

    # сноски
    def footnote(m):
        key = m.group(1)
        used.add(key)
        return keep(r'\footnote{%s}' % inline(notes[key], notes, used))

    text = re.sub(r'\[\^(\d+)\]', footnote, text)

    # полужирный и курсив
    text = re.sub(r'\*\*(.+?)\*\*',
                  lambda m: keep(r'\textbf{%s}' % inline(m.group(1), notes, used)),
                  text, flags=re.S)
    text = re.sub(r'(?<![\*\\])\*([^*\n]+?)\*(?!\*)',
                  lambda m: keep(r'\textit{%s}' % inline(m.group(1), notes, used)),
                  text, flags=re.S)

    text = text.replace(r'\*', '*')          # экранированная в md звёздочка
    text = escape(text)
    text = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], text)
    return text


# ------------------------------------------------------------------ таблица

def table(rows, notes, used):
    head = rows[0]
    body = rows[2:]
    ncol = len(head)
    widths = {4: ('p{0.17\\textwidth}', 'p{0.26\\textwidth}',
                  'p{0.22\\textwidth}', 'p{0.25\\textwidth}')}
    spec = ''.join(widths.get(ncol, ['l'] * ncol))
    out = ['\\begin{center}\\footnotesize',
           '\\begin{tabular}{%s}' % spec, '\\toprule']
    out.append(' & '.join(r'\textit{%s}' % inline(c, notes, used) for c in head) + r' \\')
    out.append('\\midrule')
    for r in body:
        r = (r + [''] * ncol)[:ncol]
        out.append(' & '.join(inline(c, notes, used) for c in r) + r' \\[2pt]')
    out += ['\\bottomrule', '\\end{tabular}', '\\end{center}']
    return '\n'.join(out)


# ------------------------------------------------------------------ разбор

def convert(md):
    body, _, notes_raw = md.partition('## Примечания')
    notes = {}
    for m in re.finditer(r'^\[\^(\d+)\]:\s*(.*)$', notes_raw, flags=re.M):
        notes[m.group(1)] = m.group(2).strip()
    used = set()

    lines = body.split('\n')
    out = []
    i = 0
    n = len(lines)
    in_abstract = False

    while i < n:
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        # горизонтальная линейка
        if re.fullmatch(r'-{3,}', s):
            i += 1
            continue

        # заголовки
        if s.startswith('# '):
            out.append(r'\artikeltitel{%s}' % inline(s[2:], notes, used))
            i += 1
            continue
        if s.startswith('## '):
            title = s[3:]
            out.append(r'\section*{%s}' % inline(title, notes, used))
            short = re.sub(r'^\d+\.\s*', '', title)
            out.append(r'\markright{%s}' % inline(short, notes, used))
            i += 1
            continue
        if s.startswith('### '):
            out.append(r'\subsection*{%s}' % inline(s[4:], notes, used))
            i += 1
            continue

        # аннотация и ключевые слова
        if s.startswith('**Аннотация.**'):
            out.append(r'\begin{annotatsiya}')
            out.append(inline(s, notes, used))
            in_abstract = True
            i += 1
            continue
        if s.startswith('**Ключевые слова:**'):
            out.append(inline(s, notes, used))
            if in_abstract:
                out.append(r'\end{annotatsiya}')
                in_abstract = False
            i += 1
            continue

        # выносная цитата
        if s.startswith('> '):
            block = []
            while i < n and (lines[i].strip().startswith('> ') or
                             lines[i].strip() == '>'):
                block.append(lines[i].strip()[1:].strip())
                i += 1
            text = ' '.join(x for x in block if x)
            out.append(r'\begin{quote}%s\end{quote}' % inline(text, notes, used))
            continue

        # таблица
        if s.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            out.append(table(rows, notes, used))
            continue

        # нумерованный список
        if re.match(r'^\d+\.\s', s):
            items = []
            while i < n and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(re.sub(r'^\d+\.\s', '', lines[i].strip()))
                i += 1
            out.append(r'\begin{enumerate}\itemsep2pt')
            for it in items:
                out.append(r'\item %s' % inline(it, notes, used))
            out.append(r'\end{enumerate}')
            continue

        # обычный абзац
        para = []
        while i < n and lines[i].strip() and not re.match(
                r'^(#{1,4} |> |\||\d+\.\s|-{3,}$)', lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(inline(' '.join(para), notes, used))

    missing = set(notes) - used
    if missing:
        sys.stderr.write('не использованы примечания: %s\n'
                         % ', '.join(sorted(missing, key=int)))
    return PREAMBLE + '\n\n'.join(out) + POSTAMBLE


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        md = f.read()
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(convert(md))
    sys.stderr.write('готово: %s\n' % dst)


if __name__ == '__main__':
    main()
