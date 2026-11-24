"""Wrap interface text of the prototype pages in c:t / c:tf / c:tn calls.

Every replacement asserts the expected number of occurrences, so a changed upstream file
fails loudly instead of being half-edited.
"""
import re
import sys

ROOT = sys.argv[1]


def edit(name, pairs, regexes=()):
    path = f'{ROOT}/{name}'
    s = open(path, encoding='utf-8', newline='').read()
    assert '\r\n' not in s, name
    for old, new, count in pairs:
        n = s.count(old)
        assert n == count, (name, old, n, count)
        s = s.replace(old, new)
    for pattern, repl, count in regexes:
        s, n = re.subn(pattern, repl, s)
        assert n == count, (name, pattern, n, count)
    open(path, 'w', encoding='utf-8', newline='').write(s)
    print('edited', name)


NAV = [
    ('>Home</a>', ">{c:t('Home')}</a>"),
    ('>Languages</a>', ">{c:t('Languages')}</a>"),
    ('>Search</a>', ">{c:t('Search')}</a>"),
]

# ---------------------------------------------------------------- word-page.xq
edit('word-page.xq', [
    ("declare variable $lang := //language[@id=$l]/@name/string();",
     "declare variable $lang := c:lang-name((//language[@id=$l])[1]);", 1),
    ("let $lang := $neo-lang/@name/string()",
     "let $lang := c:lang-name($neo-lang[1])", 1),
    ("<html>\n<head>", "<html>{c:html-lang()}\n<head>", 1),
    ('>Home</a>', ">{c:t('Home')}</a>", 2),
    ('>Languages</a>', ">{c:t('Languages')}</a>", 2),
    ('>Search</a>', ">{c:t('Search')}</a>", 4),
    ('>← Previous</a>', ">{c:t('← Previous')}</a>", 2),
    ('>Next →</a>', ">{c:t('Next →')}</a>", 2),
    ("(' see ', c:print-word(", "(concat(' ', c:t('see'), ' '), c:print-word(", 2),
    ("(' (Category: ', <a", "(concat(' (', c:t('Category'), ': '), <a", 2),
    ("concat('created by ', $word/@created/string())", "c:t('created by {1}', string($word/@created))", 1),
    ("concat('vetted by ', $word/@vetted/string())", "c:t('vetted by {1}', string($word/@vetted))", 1),
    (">Previous Phrase</a>", ">{c:t('Previous Phrase')}</a>", 1),
    (">Next Phrase</a>", ">{c:t('Next Phrase')}</a>", 1),
    ("""       See {c:print-word(c:get-word($word/see-notes),
       <print-word style="italic" show-lang="y" show-link="y"/>)} for discussion.""",
     """       {c:tf('See {1} for discussion.', <arg>{c:print-word(c:get-word($word/see-notes),
       <print-word style="italic" show-lang="y" show-link="y"/>)}</arg>)}""", 1),
    ("""            <p>See {c:print-word(c:get-word($see-further),
            <print-word style="italic" show-lang="y" show-link="y"/>)} for further discussion.</p>""",
     """            <p>{c:tf('See {1} for further discussion.', <arg>{c:print-word(c:get-word($see-further),
            <print-word style="italic" show-lang="y" show-link="y"/>)}</arg>)}</p>""", 1),
    ("""            <p>See also {c:print-word($see-also,
            <print-word style="italic" show-lang="y" show-link="y"/>)} {c:print-gloss($see-also)}.</p>""",
     """            <p>{c:tf('See also {1}{2}.', (<arg>{c:print-word($see-also,
            <print-word style="italic" show-lang="y" show-link="y"/>)}</arg>, <arg>{c:print-gloss($see-also)}</arg>))}</p>""", 1),
    ("<tr><th colspan=\"10\">Examples ({string($form)})</th></tr>",
     "<tr><th colspan=\"10\">{c:t('Examples ({1})', c:form-labels(string($form)))}</th></tr>", 1),
    ("<p><u>Order ({$word/@order/string()})</u></p>",
     "<p><u>{c:t('Order ({1})', string($word/@order))}</u></p>", 1),
    ("else () } After</td>", "else () }{concat(' ', c:t('After'))}</td>", 1),
    ("'[ERROR:MISLINK] ' else () } Before</td>", "'[ERROR:MISLINK] ' else () }{concat(' ', c:t('Before'))}</td>", 1),
    # compounds summary: plural-aware text, and a language-independent test for it
    ("                ⇒ {count($element-ins)} compounds\n",
     "                {c:tn('⇒ {1} compounds', count($element-ins))}\n", 1),
    ("not(contains(string($print-derivatives), ' compounds'))",
     "not(matches(string($print-derivatives), '⇒\\s*\\d')) (: the compounds summary :)", 1),
    ("<ul><li>⇒ [see above]</li></ul>", "<ul><li>⇒ [{c:t('see above')}]</li></ul>", 1),
    ("text{' for example: '}", "text{concat(' ', c:t('for example:'), ' ')}", 1),
    ("<i>[no change]</i>", "<i>[{c:t('no change')}]</i>", 1),
    # inflection, variant and class codes
    ("then (<a href=\"{$link}\">{$inflection}</a>,", "then (<a href=\"{$link}\">{c:form-label($inflection)}</a>,", 1),
    ("else text { ($inflection), if", "else text { (c:form-label($inflection), if", 1),
    ("concat(' (', $from-ref/inflect/@form, ')')", "concat(' (', c:form-labels(string($from-ref/inflect/@form)), ')')", 1),
    ("<td>{$ref-form}</td>", "<td>{c:form-labels($ref-form)}</td>", 1),
], regexes=[
    # section headings: <u>Derivatives</u> and the like
    (r"<u>([A-Z][A-Za-z ]+)</u>", r"<u>{c:t('\1')}</u>", 19),
])

# ---------------------------------------------------------------- common.xq (shared phrase)
edit('common.xq', [
    ("if ($element/@form) then concat(' (', $element/@form, ')') else ()",
     "if ($element/@form) then concat(' (', c:form-labels(string($element/@form)), ')') else ()", 1),
])

# ---------------------------------------------------------------- language-page.xq
edit('language-page.xq', [
    ("declare variable $lang-name := $lang/@name/string();", "declare variable $lang-name := c:lang-name($lang[1]);", 1),
    ("<html>\n<head>", "<html>{c:html-lang()}\n<head>", 1),
    ('>Home</a>', ">{c:t('Home')}</a>", 1),
    ('>Languages</a>', ">{c:t('Languages')}</a>", 1),
    ("<p>For more information about how this vocabulary list was assembled, see:</p>",
     "<p>{c:t('For more information about how this vocabulary list was assembled, see:')}</p>", 1),
], regexes=[
    (r'(\.html">)(Vocabulary|Roots|Words|Names|Phrases|Grammar|Phonetics|Semantic Categories|Full List of Roots|Full Word List|Neologisms|Deprecated Words)(</a>)',
     r"\1{c:t('\2')}\3", 14),
])

# ---------------------------------------------------------------- language-index.xq
edit('language-index.xq', [
    ("<a href=\"../language-pages/lang-{$lang/@id}.html\"><b>{$lang/@name/string()}</b></a>",
     "<a href=\"../language-pages/lang-{$lang/@id}.html\"><b>{c:lang-name($lang)}</b></a>", 1),
    ("<b><i>{$lang/@name/string()}</i></b>", "<b><i>{c:lang-cat-name($lang)}</i></b>", 1),
    ("<li><b><a href=\"#{$lang-cat/@id/string()}\">{$lang-cat/@name/string()}</a></b></li>",
     "<li><b><a href=\"#{$lang-cat/@id/string()}\">{c:lang-cat-name($lang-cat)}</a></b></li>", 1),
    ("<a name=\"{$lang-cat/@id/string()}\"></a>{$lang-cat/@name/string()}</u>",
     "<a name=\"{$lang-cat/@id/string()}\"></a>{c:lang-cat-name($lang-cat)}</u>", 1),
    ("<title>Eldamo : Language Index</title>", "<title>Eldamo : {c:t('Language Index')}</title>", 1),
    ("<h1>Language Index</h1>", "<h1>{c:t('Language Index')}</h1>", 1),
    ("<html>\n<head>", "<html>{c:html-lang()}\n<head>", 1),
    ('>Home</a>', ">{c:t('Home')}</a>", 1),
    ("<p><b>Unexplained Languages</b></p>", "<p><b>{c:t('Unexplained Languages')}</b></p>", 1),
    ("<p>This page lists the languages", "{c:fragment('language-index-intro', (\n<p>This page lists the languages", 1),
    ("trace the conceptual evolution of individual words in Tolkien’s writing.</p>",
     "trace the conceptual evolution of individual words in Tolkien’s writing.</p>\n))}", 1),
])
# the three intro paragraphs become one sequence argument: separate them with commas
path = f'{ROOT}/language-index.xq'
s = open(path, encoding='utf-8').read()
start = s.index("{c:fragment('language-index-intro'")
end = s.index("))}", start)
block = s[start:end]
block_new = block.replace("</p>\n<p>", "</p>,\n<p>")
assert block_new.count("</p>,\n<p>") == 2, block_new
s = s[:start] + block_new + s[end:]
open(path, 'w', encoding='utf-8', newline='').write(s)

# ---------------------------------------------------------------- word-index.xq
edit('word-index.xq', [
    ("declare variable $lang-name := $lang/@name/string();", "declare variable $lang-name := c:lang-name($lang[1]);", 1),
    ("<html>\n<head>", "<html>{c:html-lang()}\n<head>", 1),
    ("<title>Eldamo : {$lang-name} Words</title>", "<title>Eldamo : {c:t('{1} Words', $lang-name)}</title>", 1),
    ("<h1>{$lang-name} Words</h1>", "<h1>{c:t('{1} Words', $lang-name)}</h1>", 1),
    ('>Home</a>', ">{c:t('Home')}</a>", 1),
    ('>Languages</a>', ">{c:t('Languages')}</a>", 1),
    ("(' see ', c:print-word(", "(concat(' ', c:t('see'), ' '), c:print-word(", 1),
    ("('; see instead:',", "(concat('; ', c:t('see instead:')),", 1),
    ("concat('created by ', $word/@created/string())", "c:t('created by {1}', string($word/@created))", 1),
    ("concat('vetted by ', $word/@vetted/string())", "c:t('vetted by {1}', string($word/@vetted))", 1),
    ("<h3>Unglossed [{count($unglossed)}]</h3>", "<h3>{c:t('Unglossed [{1}]', count($unglossed))}</h3>", 1),
])
