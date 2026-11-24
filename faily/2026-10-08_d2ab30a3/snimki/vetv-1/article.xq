xquery version "3.1";
(: Per-article files of the static reader, as hwph_export.py writes them from api_article():
     data/a/<id>.js   the article with everything its right-hand column shows
     data/t/<id>.js   its plain text (snippets, phrases)
     pages/<id>.html  the article as a page of its own
   for the articles of the volumes given in $bands (e.g. "1 1*"); every file is preceded by a line
   "@@FILE@@ <path>" so that one run writes many files. :)
import module namespace h = "hwph" at "common.xq";
declare namespace saxon = "http://saxon.sf.net/";
declare namespace map = "http://www.w3.org/2005/xpath-functions/map";
declare namespace array = "http://www.w3.org/2005/xpath-functions/array";
declare option saxon:output "method=text";

declare variable $bands as xs:string external := '1 1*';
declare variable $i18n as xs:string external;            (: path of i18n.js :)
declare variable $lang as xs:string external := 'ru';

declare variable $db := /hwph;
declare variable $arts := $db/articles/article;
declare variable $by-id := map:merge($arts ! map { xs:integer(@id): . });
declare variable $printed := (for $a in $arts order by xs:integer($a/@pdf-from) return xs:integer($a/@id));
declare variable $printed-pos := map:merge(for $id at $i in $printed return map { $id: $i });

declare function local:index($items as element()*, $key as xs:string) as map(*) {
  map:merge(for $x in $items[@*[name() = $key]] let $k := xs:integer($x/@*[name() = $key]) group by $k return map { $k: $x })
};
declare variable $xref-by-dst := local:index($db/xrefs/x, 'dst');
declare variable $xref-by-src := local:index($db/xrefs/x, 'src');
declare variable $reg-ref-by-dst := local:index($db/register/r[@kind = 'ref'], 'dst');
declare variable $reg-author-by-dst := local:index($db/register/r[@kind = 'author'], 'dst');
declare variable $reg-see-by-term := map:merge(for $r in $db/register/r[@kind = 'see'][@dst] let $k := string($r/@term-fold) group by $k return map { $k: $r });
declare variable $author-articles := map:merge(for $r in $db/register/r[@kind = 'author'] let $k := string($r/@term) group by $k return map { $k: count(distinct-values($r/@dst)) });
declare variable $cites-by-aid := local:index($db/cites/c, 'aid');
declare variable $persons := map:merge($db/persons/p ! map { xs:integer(@id): . });
declare variable $mentions-by-aid := local:index($db/mentions/m, 'aid');
declare variable $items-by-aid := local:index($db/sgroups/group/item, 'aid');

(: ---------------------------------------------------------------- i18n.js, read as hwph_export.i18n_value does :)
declare variable $i18n-src := unparsed-text($i18n);
declare function local:w($key as xs:string) as xs:string {
  let $block := substring-before(substring-after($i18n-src, concat("'", $key, "':")), "&#10;    '")
  let $m := analyze-string($block, concat('(^|[^A-Za-z_])', $lang, ':\s*("([^"]*)"|''([^'']*)'')'))//*:match[1]
  return string(($m//*:group[@nr = 3], $m//*:group[@nr = 4])[1])
};

(: ---------------------------------------------------------------- api_article() :)
declare function local:brief($id as xs:integer?) as element() {
  if (empty($id)) then <null/> else
  let $a := $by-id($id)
  return h:o((h:m('id', h:n($a/@id)), h:m('lemma', h:s($a/@lemma)), h:m('band', h:s($a/@band)), h:m('col', h:n($a/@col-from))))
};

declare function local:links($xs as element(x)*, $key as xs:string, $self as xs:integer) as element(a) {
  h:a(
    for $x in $xs[xs:integer(@*[name() = $key]) ne $self]
    let $other := xs:integer($x/@*[name() = $key])
    group by $other
    let $a := $by-id($other)
    order by string($a/@lemma-fold), $other
    return h:o((h:m('id', h:n($other)), h:m('lemma', h:s($a/@lemma)), h:m('n', h:n(count($x))))))
};

declare function local:max($v as xs:string*) as xs:string? {
  if (empty($v)) then () else (for $x in $v order by $x descending return $x)[1]
};

declare function local:article($a as element(article)) as element(o) {
  let $id := xs:integer($a/@id)
  let $pos := $printed-pos($id)
  let $outlinks := local:links($xref-by-src($id), 'dst', $id)
  let $backlinks := local:links($xref-by-dst($id), 'src', $id)
  let $linked := ($outlinks/o/m[@k = 'id']/n, $backlinks/o/m[@k = 'id']/n) ! xs:integer(.)
  return h:o((
    h:m('id', h:n($id)), h:m('lemma', h:s($a/@lemma)), h:m('band', h:s($a/@band)), h:m('kind', h:s($a/@kind)),
    h:m('col_from', h:n($a/@col-from)), h:m('col_to', h:n($a/@col-to)),
    h:m('pdf_from', h:n($a/@pdf-from)), h:m('pdf_to', h:n($a/@pdf-to)),
    h:m('authors', h:a($a/authors/author ! h:s(.))),
    h:m('n_notes', h:n($a/@n-notes)), h:m('n_chars', h:n($a/@n-chars)),
    h:m('toc', h:a($a/toc/entry ! h:a((h:s(@id), h:s(@label), h:n(@level))))),
    h:m('html', h:s(if ($a/html-raw) then string($a/html-raw) else h:html($a/html/node()))),
    h:m('prev', local:brief(if ($pos gt 1) then $printed[$pos - 1] else ())),
    h:m('next', local:brief($printed[$pos + 1])),
    h:m('backlinks', $backlinks),
    h:m('outlinks', $outlinks),
    h:m('register', h:a(subsequence(
      for $r in $reg-ref-by-dst($id)
      let $k := string($r/@term-fold)
      group by $k
      order by $k
      return h:o((h:m('term', h:s($r[last()]/@term)), h:m('qualifier', h:s(local:max($r/@qualifier))),
                  h:m('band', h:s(local:max($r/@band))), h:m('col', h:s(local:max($r/@col))))), 1, 400))),
    h:m('persons', h:a(subsequence(
      for $c in $cites-by-aid($id)
      let $p := $persons(xs:integer($c/@pid))
      stable order by xs:integer($p/@editor), xs:integer($c/@n-body) + xs:integer($c/@n-notes) descending,
                      xs:integer($c/@n-lit) descending, xs:integer($p/@n-articles) descending
      return h:o((h:m('id', h:n($p/@id)), h:m('name', h:s($p/@name)), h:m('b', h:n($c/@n-body)),
                  h:m('n', h:n($c/@n-notes)), h:m('l', h:n($c/@n-lit)), h:m('editor', h:n($p/@editor)),
                  h:m('role', h:s($p/@role)))), 1, 200))),
    h:m('mentions', h:a(
      for $m in $mentions-by-aid($id)[not(xs:integer(@dst) = $linked)]
      stable order by xs:double($m/@score) descending
      return h:o((h:m('id', h:n($m/@dst)), h:m('lemma', h:s($by-id(xs:integer($m/@dst))/@lemma)), h:m('tf', h:n($m/@tf)))))),
    h:m('see_also', h:a(
      let $rs := $reg-see-by-term(string($a/@lemma-fold))[exists($by-id(xs:integer(@dst)))]
      for $d in distinct-values($rs/@dst ! xs:integer(.))
      return h:o((h:m('id', h:n($d)), h:m('lemma', h:s($by-id($d)/@lemma)))))),
    h:m('groups', h:a(
      for $i in $items-by-aid($id)
      let $g := $i/..
      let $gid := xs:integer($g/@id)
      group by $gid
      order by $gid
      return h:o((h:m('id', h:n($gid)), h:m('name', h:s($g[1]/@name)), h:m('label', h:s(local:min($i/@label))))))),
    h:m('reg_authors', h:a(
      for $r in $reg-author-by-dst($id)
      let $t := string($r/@term)
      group by $t
      order by min($r/xs:integer(@id))
      return h:o((h:m('name', h:s($t)), h:m('n', h:n($author-articles($t))))))) ))
};

declare function local:min($v as xs:string*) as xs:string? {
  if (empty($v)) then () else (for $x in $v order by $x return $x)[1]
};

(: ---------------------------------------------------------------- data/t :)
declare function local:texts($a as element(article)) as element(o) {
  let $cm := $a/colmap
  return h:o((
    h:m('b', h:s(string($a/plain[@part = 'b']))), h:m('n', h:s(string($a/plain[@part = 'n']))),
    h:m('l', h:s(string($a/plain[@part = 'l']))), h:m('au', h:s(string-join($a/authors/author, ' '))),
    h:m('A', h:a($a/authors/author ! h:s(.))),
    h:m('cb', h:from-json(parse-json(($cm/@b, '[]')[1]))),
    h:m('cn', h:from-json(parse-json(($cm/@n, '[]')[1]))),
    h:m('cl', h:from-json(parse-json(($cm/@l, '[]')[1]))) ))
};

(: ---------------------------------------------------------------- pages/<id>.html (write_page, page_body, note_sections) :)
declare function local:esc($s as xs:string?) as xs:string {
  replace(replace(replace(replace(string($s), '&amp;', '&amp;amp;', 'q'), '&lt;', '&amp;lt;', 'q'), '&gt;', '&amp;gt;', 'q'), '"', '&amp;quot;', 'q')
};

declare function local:page-body($html as xs:string) as xs:string {
  let $s := replace($html, 'href="#/a/(\d+)"', 'href="$1.html"')
  let $s := replace($s, '<sup class="fn" data-fn="([^"]+)">([^<]*)</sup>', '<sup class="fn" data-fn="$1"><a href="#fn$1">$2</a></sup>')
  let $s := replace($s, '(<(span|div) class="(m|md)" data-tex="([^"]*)">)(</\2>)', '$1$4$5')
  let $s := replace($s, '(<div class="ocr" data-i18n="art\.ocr">)(</div>)', concat('$1', replace(local:esc(local:w('art.ocr')), '\$', '\\\$'), '$2'))
  let $s := replace($s, 'src="img/', 'src="../img/', 'q')
  return local:note-sections($s)
};

declare function local:later($a as xs:integer*, $b as xs:integer*) as xs:boolean {
  let $n := max((count($a), count($b)))
  let $d := (for $i in 1 to $n
             let $x := (($a[$i], 0)[1]) - (($b[$i], 0)[1])
             where $x ne 0 return $x)[1]
  return exists($d) and $d gt 0
};

(: sections of one paragraph: SEC_PART, SEC_SUB_AFTER_PART, SEC_SUB of hwph_export.py :)
declare function local:section($tx as xs:string, $part as xs:string) as map(*)? {
  let $head := substring($tx, 1, 240)
  let $rp := replace($head, '^([IVX]{1,5})\.\s.*$', '$1', 's')
  let $rp := if ($rp ne $head) then $rp else ''
  let $part := if ($rp ne '') then $rp else $part
  let $sub :=
    if ($rp ne '') then
      let $m := analyze-string($head, '–\s*(\d{1,2}(\.\d{1,2})*)\.\s')//*:match[1]
      return string($m/*:group[@nr = 1])
    else
      let $m := replace($head, '^(\d{1,2}(\.\d{1,2})*)\.\s.*$', '$1', 's')
      return if ($m ne $head) then $m else ''
  return
    if ($rp ne '' or $sub ne '') then
      map { 'label': concat(if ($part ne '') then $part || '.' else '', if ($part ne '' and $sub ne '') then ' ' else '', $sub),
            'title': substring($tx, 1, 90), 'part': $part,
            'num': if ($sub ne '') then tokenize($sub, '\.') ! xs:integer(.) else () }
    else map { 'part': $part }
};

(: walk the paragraphs, carrying part, window, column, previous section and what was found :)
declare function local:walk($paras as xs:string*, $part as xs:string, $col as xs:string,
                            $prev as map(*), $found as map(*)) as map(*) {
  if (empty($paras)) then $found else
  let $inner := $paras[1]
  let $tx := normalize-space(replace(replace($inner, '<[^>]+>', ''), '\s+', ' '))
  let $sec := local:section($tx, $part)
  let $win := if (exists($sec?label)) then $sec else ()
  let $events := analyze-string($inner, '<span class="col" data-col="(\d+)"|<sup class="fn" data-fn="(\d+)-\d+"')//*:match
  let $state := local:events($events, $win, $col, $prev, $found)
  return local:walk(tail($paras), $sec?part, $state?col, $state?prev, $state?found)
};

declare function local:events($events as element()*, $win as map(*)?, $col as xs:string,
                              $prev as map(*), $found as map(*)) as map(*) {
  if (empty($events)) then map { 'col': $col, 'prev': $prev, 'found': $found } else
  let $e := $events[1]
  let $c := string($e/*:group[@nr = 1])
  return
    if ($c ne '') then local:events(tail($events), $win, $c, $prev, $found)
    else
      let $sr := string($e/*:group[@nr = 2])
      return
        if (map:contains($found, $sr)) then local:events(tail($events), $win, $col, $prev, $found)
        else
          let $ok := $win[?part ne $prev?part or local:later(?num, $prev?num)]
          let $hit := ($ok[last()], $win[1])[1]
          return
            if (exists($hit)) then
              local:events(tail($events), $win, $col, map { 'part': $hit?part, 'num': $hit?num },
                           map:put($found, $sr, [$hit?label, $hit?title]))
            else
              local:events(tail($events), $win, $col, $prev,
                           map:put($found, $sr, [if ($col ne '') then 'Sp. ' || $col else '', '']))
};

declare function local:note-sections($html as xs:string) as xs:string {
  let $cut := if (contains($html, '<ol class="notes">')) then string-length(substring-before($html, '<ol class="notes">')) else -1
  return if ($cut lt 0) then $html else
  let $body := substring($html, 1, $cut)
  let $notes := substring($html, $cut + 1)
  let $firsts := distinct-values(analyze-string($notes, '<li id="fn(\d+)-\d+"')//*:match/*:group[@nr = 1]/string())
  return if (count($firsts) lt 2) then $html else
  let $paras := analyze-string($body, '<p(\s[^>]*)?>(.*?)</p>', 's')//*:match/*:group[@nr = 2]/string()
  let $found := local:walk($paras, '', '', map { 'part': '', 'num': () }, map {})
  let $notes2 := local:insert-seps($notes, $firsts, $found)
  return concat($body, $notes2)
};

declare function local:insert-seps($notes as xs:string, $firsts as xs:string*, $found as map(*)) as xs:string {
  if (empty($firsts)) then $notes else
  let $sr := $firsts[1]
  let $f := ($found($sr), ['', ''])[1]
  let $label := $f(1)
  let $title := $f(2)
  let $sep := concat('<li class="nsec"', if ($title ne '') then concat(' title="', local:esc($title), '…"') else '', '>',
                     if ($label ne '') then local:esc($label) else '·', '</li>')
  let $marker := concat('<li id="fn', $sr, '-')
  let $before := substring-before($notes, $marker)
  return local:insert-seps(concat($before, $sep, substring($notes, string-length($before) + 1)), tail($firsts), $found)
};

declare function local:page($art as element(o), $a as element(article)) as xs:string {
  let $f := function-lookup(xs:QName('local:field'), 2)
  let $id := string($a/@id)
  let $lemma := string($a/@lemma)
  let $c1 := string($a/@col-from)
  let $c2 := string($a/@col-to)
  let $loc := concat('Bd. ', $a/@band, ', Sp. ', $c1, if ($c2 ne '' and $c2 ne $c1) then '–' || $c2 else '')
  let $prev := $art/m[@k = 'prev']/o
  let $next := $art/m[@k = 'next']/o
  let $nav := string-join((
      concat('<a href="index.html">', local:w('hdr.menu'), '</a>'),
      if ($prev) then concat('<a href="', $prev/m[@k = 'id'], '.html" rel="prev">← ', local:esc($prev/m[@k = 'lemma']), '</a>') else (),
      if ($next) then concat('<a href="', $next/m[@k = 'id'], '.html" rel="next">', local:esc($next/m[@k = 'lemma']), ' →</a>') else (),
      concat('<a class="open" href="../index.html#/a/', $id, '">', local:w('pages.reader'), '</a>')), ' ')
  let $toc := if (count($a/toc/entry) gt 1)
    then concat('<details class="toc"><summary>', local:w('rail.sections'), '</summary><ol>',
                string-join($a/toc/entry ! concat('<li><a href="#', local:esc(@id), '">', local:esc(@label), '</a></li>')),
                '</ol></details>&#10;') else ''
  let $links := function($k, $title) {
    let $xs := $art/m[@k = $k]/a/o
    return if ($xs) then concat('<h2>', local:w($title), '</h2>',
      string-join($xs ! concat('<a href="', m[@k = 'id'], '.html">', local:esc(m[@k = 'lemma']), '</a>'), ', ')) else () }
  let $groups := $art/m[@k = 'groups']/a/o
  let $foot := string-join((
      $links('see_also', 'rail.see_also'),
      $links('backlinks', 'rail.backlinks'),
      if ($groups) then concat('<h2>', local:w('rail.groups'), '</h2>',
        string-join($groups ! concat(local:esc(m[@k = 'name']), if (m[@k = 'label']/s) then ': ' || local:esc(m[@k = 'label']) else ''), '; ')) else ()), '&#10;')
  let $html := string($art/m[@k = 'html']/s)
  let $math := if (contains($html, 'data-tex="')) then concat(
      '<link rel="stylesheet" href="../katex/katex.min.css"><script defer src="../katex/katex.min.js"></script>&#10;',
      '<script>addEventListener("DOMContentLoaded",function(){if(!window.katex)return;',
      'document.querySelectorAll(".m[data-tex],.md[data-tex]").forEach(function(e){try{katex.render(e.dataset.tex,e,',
      '{displayMode:e.classList.contains("md"),throwOnError:false})}catch(x){}})});</script>&#10;') else ''
  let $au := if ($a/authors/author) then concat('<div class="au">', local:w('hdr.authors'), ': ', local:esc(string-join($a/authors/author, ', ')), '</div>') else ''
  return concat('<!DOCTYPE html>&#10;<html lang="', $lang, '"><head><meta charset="utf-8">&#10;',
    '<meta name="viewport" content="width=device-width, initial-scale=1">&#10;',
    '<title>', local:esc($lemma), ' — HWPh ', $loc, '</title>&#10;<link rel="stylesheet" href="page.css">&#10;', $math, '</head><body>&#10;',
    '<nav>', $nav, '</nav>&#10;<header><h1 lang="de">', local:esc($lemma), '</h1><div class="loc">HWPh, ', $loc, '</div>', $au, '</header>&#10;', $toc,
    '<article lang="de">&#10;', local:page-body($html), '&#10;</article>&#10;<footer>', $foot, '</footer>&#10;</body></html>&#10;')
};

string-join(
  for $a in $arts[@band = tokenize($bands, ' ')]
  let $art := local:article($a)
  return (
    concat('@@FILE@@ data/a/', $a/@id, '.js&#10;', h:js(concat('a/', $a/@id), $art)),
    concat('@@FILE@@ data/t/', $a/@id, '.js&#10;', h:js(concat('t/', $a/@id), local:texts($a))),
    concat('@@FILE@@ pages/', $a/@id, '.html&#10;', local:page($art, $a))
  ))
