xquery version "3.1";
(: The files of the static reader that cover the whole dictionary, as hwph_export.py writes them:
     data/s/<xx>.js    search index, one file per first two letters of a word
     data/vocab.js     all words with their counts and spelling keys
     data/meta.js      lemma list, statistics, field lengths for ranking
     data/r/<xx>.js    register of vol. 13
     data/graph.js     cross-references, citations, discussed concepts
     data/persons.js   all cited persons
     data/pat/<n>.js   how each person is written, 500 per file
     data/authors.js   subject groups and the register of authors
     data/extras.js    abbreviations, signs, the article list against the articles found
     pages/index.html  the list of article pages
     index.html        the reader (hwph_ui.html with the static API switched on)
   Every file is preceded by a line "@@FILE@@ <path>". :)
import module namespace h = "hwph" at "common.xq";
declare namespace saxon = "http://saxon.sf.net/";
declare namespace map = "http://www.w3.org/2005/xpath-functions/map";
declare namespace array = "http://www.w3.org/2005/xpath-functions/array";
declare option saxon:output "method=text";

declare variable $i18n as xs:string external;
declare variable $ui as xs:string external;                 (: path of hwph_ui.html :)
declare variable $lang as xs:string external := 'ru';
declare variable $built as xs:string external := format-dateTime(current-dateTime(), '[Y0001]-[M01]-[D01] [H01]:[m01]');

declare variable $db := /hwph;
declare variable $arts := $db/articles/article;
declare variable $by-id := map:merge($arts ! map { xs:integer(@id): . });

declare function local:file($path as xs:string, $content as xs:string) as xs:string {
  concat('@@FILE@@ ', $path, '&#10;', $content)
};

declare function local:shard($term as xs:string) as xs:string {
  string-join(string-to-codepoints(substring($term, 1, 2)) ! h:hex(.), '-')
};

(: Python writes a float with repr(): always with a decimal point :)
declare function local:float($d as xs:double) as xs:string {
  let $s := string($d) return if (matches($s, '[.eE]')) then $s else concat($s, '.0')
};

(: ---------------------------------------------------------------- the word index (as index.xq) :)
declare variable $t := h:fold-tables(/);
declare variable $rows :=
  for $a in $arts
  let $fields := (string($a/@lemma), string($a/plain[@part = 'b']), string($a/plain[@part = 'n']),
                  string($a/plain[@part = 'l']), string-join($a/authors/author, ' '))
  let $words := for $f in $fields return [h:words(h:fold($f, $t), $t)]
  return (
    <len id="{$a/@id}">{ string-join($words ! string(count(?*)), ' ') }</len>,
    for $f at $i in $words, $w in $f?*
    let $field := $i
    group by $w
    let $c := for $k in 1 to 5 return count($field[. eq $k])
    let $last := max((0, for $x at $k in $c return if ($x gt 0) then $k else 0))
    return <w t="{$w}" a="{$a/@id}" c="{string-join(subsequence($c, 1, $last) ! h:b36(.), ',')}" n="{sum($c)}"/>
  );
declare variable $terms :=
  for $w in $rows/self::w
  let $term := string($w/@t)
  group by $term
  order by $term
  let $aids := $w/@a ! xs:integer(.)
  return <term t="{$term}" docs="{count($w)}" cnt="{sum($w/@n ! xs:integer(.))}" skey="{h:skey($term)}" shard="{local:shard($term)}"
               post="{string-join(for $i in 1 to count($w)
                                  return h:b36($aids[$i] - (if ($i eq 1) then 0 else $aids[$i - 1])) || ':' || $w[$i]/@c, ' ')}"/>;

declare function local:index-files() as xs:string* {
  for $x in $terms
  let $s := string($x/@shard)
  group by $s
  return local:file(concat('data/s/', $s, '.js'),
                    h:js(concat('s/', $s), h:o($x ! h:m(@t, h:s(@post))))),
  local:file('data/vocab.js', h:js('vocab', h:o((
    h:m('t', h:a($terms ! h:s(@t))),
    h:m('d', h:a($terms ! h:n(@docs))),
    h:m('c', h:a($terms ! h:n(@cnt))),
    h:m('k', h:a($terms ! h:s(if (@skey eq @t) then '' else string(@skey))))))))
};

(: ---------------------------------------------------------------- register :)
declare variable $reg-shards :=
  for $r in $db/register/r
  let $s := if (string($r/@term-fold) ne '') then local:shard(string($r/@term-fold)) else '_'
  group by $s
  return <shard name="{$s}">{$r}</shard>;

declare function local:register-files() as xs:string* {
  for $sh in $reg-shards
  return local:file(concat('data/r/', $sh/@name, '.js'), h:js(concat('r/', $sh/@name), h:a(
    for $r in $sh/r
    return h:a((h:s($r/@term), h:s($r/@target), h:s($r/@qualifier), h:s($r/@band), h:s($r/@col), h:s($r/@kind),
                h:n($r/@dst), h:s(if ($r/@dst) then $by-id(xs:integer($r/@dst))/@lemma else ()), h:s($r/@term-fold))))))
};

(: ---------------------------------------------------------------- meta :)
declare function local:meta() as xs:string {
  let $lens := $rows/self::len
  let $total := sum($lens ! sum(tokenize(., ' ') ! xs:integer(.)))
  return local:file('data/meta.js', h:js('meta', h:o((
    h:m('info', h:o((h:m('engine', h:s('static')), h:m('stats', $db/json[@name = 'stats']/*)))),
    h:m('lemmas', h:a(
      for $a in $arts stable order by string($a/@lemma-fold)
      return h:a((h:n($a/@id), h:s($a/@lemma), h:s($a/@band), h:n($a/@col-from), h:s($a/@kind), h:n($a/@col-to))))),
    h:m('n_docs', h:n(count($lens))),
    h:m('avgdl', h:n(local:float(xs:double($total) div count($lens)))),
    h:m('lengths', h:o($lens ! h:mi(xs:integer(@id), h:a(tokenize(., ' ') ! h:n(.))))),
    h:m('shards', h:a(for $s in distinct-values($terms/@shard) order by $s return h:s($s))),
    h:m('reg_shards', h:a(for $s in $reg-shards/@name order by $s return h:s($s))),
    h:m('built', h:s($built))))))
};

(: ---------------------------------------------------------------- graph, persons, patterns :)
declare function local:graph() as xs:string {
  local:file('data/graph.js', h:js('graph', h:o((
    h:m('xrefs', h:a(
      for $x in $db/xrefs/x[@dst]
      let $src := xs:integer($x/@src), $dst := xs:integer($x/@dst)
      group by $src, $dst
      order by $src, $dst
      return h:a((h:n($src), h:n($dst), h:n(count($x)))))),
    h:m('cites', h:a(
      for $c in $db/cites/c stable order by xs:integer($c/@aid)
      return h:a(($c/@aid, $c/@pid, $c/@n-body, $c/@n-notes, $c/@n-lit) ! h:n(.)))),
    h:m('mentions', h:a(
      for $m in $db/mentions/m
      return h:a(($m/@aid, $m/@dst, $m/@tf, $m/@score) ! h:n(.))))))))
};

declare function local:persons() as xs:string {
  local:file('data/persons.js', h:js('persons', h:a(
    for $p in $db/persons/p
    order by xs:integer($p/@n-articles) descending, xs:integer($p/@id)
    return h:a((h:n($p/@id), h:s($p/@name), h:s($p/@name-fold), h:n($p/@n-articles), h:n($p/@n-body),
                h:n($p/@n-notes), h:n($p/@n-lit), h:n($p/@editor), h:s($p/@role))))))
};

declare function local:patterns() as xs:string* {
  for $p in $db/persons/p
  let $b := xs:integer($p/@id) idiv 500
  group by $b
  order by $b
  return local:file(concat('data/pat/', $b, '.js'), h:js(concat('pat/', $b), h:o(
    $p ! h:mi(xs:integer(@id), h:a((h:s(@pattern), h:from-json(parse-json(@variants))))))))
};

(: ---------------------------------------------------------------- vol. 13: subject groups, authors; extras :)
declare function local:authors() as xs:string {
  local:file('data/authors.js', h:js('authors', h:o((
    h:m('groups', h:a(
      for $g in $db/sgroups/group
      return h:a((h:n($g/@id), h:s($g/@name), h:a(
        for $i in $g/item stable order by xs:integer($i/@pos)
        return h:a((h:n($i/@aid), h:s($i/@label)))))))),
    h:m('authors', h:a(
      for $r in $db/register/r[@kind = 'author']
      return h:a((h:s($r/@term), h:n($r/@dst), h:s($r/@target), h:s($r/@band), h:s($r/@col)))))))))
};

declare function local:extras() as xs:string {
  let $list := $db/article-list/e
  let $listed := $list/@aid ! xs:integer(.)
  return local:file('data/extras.js', h:js('extras', h:o((
    h:m('abbrevs', h:o((
      h:m('abbreviations', h:a(
        for $x in $db/abbrevs/abbrev
        let $sec := xs:integer($x/@sec)
        group by $sec
        order by $sec
        return h:o((h:m('sec', h:n($sec)), h:m('title', h:s($x[1]/@title)), h:m('items', h:a(
          for $i in $x stable order by xs:integer($i/@pos)
          return h:o((h:m('a', h:s($i/@abbr)), h:m('text', h:s($i/@text))))))))),
      h:m('symbols', ($db/json[@name = 'symbols']/*, <a/>)[1])))),
    h:m('checklist', h:o((
      h:m('total', h:n(count($list))),
      h:m('missing', h:a(
        for $e in $list[not(@aid)] stable order by xs:integer($e/@pos)
        return h:o((h:m('lemma', h:s($e/@lemma)), h:m('zh', h:s($e/@zh)), h:m('band', h:s($e/@band)),
                    h:m('col', h:n($e/@col)), h:m('page', h:n($e/@page)))))),
      h:m('not_listed', h:a(
        for $a in $arts[@kind = 'article'][not(xs:integer(@id) = $listed)]
        stable order by number($a/@band), xs:integer($a/@col-from)
        return h:o((h:m('id', h:n($a/@id)), h:m('lemma', h:s($a/@lemma)), h:m('band', h:s($a/@band)),
                    h:m('col', h:n($a/@col-from))))))))))))
};

(: ---------------------------------------------------------------- pages/index.html and the reader :)
declare variable $i18n-src := unparsed-text($i18n);
declare function local:w($key as xs:string) as xs:string {
  let $block := substring-before(substring-after($i18n-src, concat("'", $key, "':")), "&#10;    '")
  let $m := analyze-string($block, concat('(^|[^A-Za-z_])', $lang, ':\s*("([^"]*)"|''([^'']*)'')'))//*:match[1]
  return string(($m//*:group[@nr = 3], $m//*:group[@nr = 4])[1])
};
(: plural forms of a counted word, as Intl.PluralRules chooses them (ru: one/few/many; others: one/other) :)
declare function local:plural($key as xs:string, $n as xs:integer) as xs:string {
  let $block := substring-before(substring-after($i18n-src, concat("'", $key, "':")), "&#10;    '")
  let $forms := substring-before(substring-after($block, concat($lang, ': {')), '}')
  let $k := if ($lang eq 'ru')
            then (if ($n mod 10 eq 1 and $n mod 100 ne 11) then 'one'
                  else if ($n mod 10 ge 2 and $n mod 10 le 4 and not($n mod 100 ge 12 and $n mod 100 le 14)) then 'few' else 'many')
            else (if ($n eq 1 or ($lang eq 'fr' and $n eq 0)) then 'one' else 'other')
  let $m := analyze-string($forms, concat('"?', $k, '"?:\s*("([^"]*)"|''([^'']*)'')'))//*:match[1]
  return replace(string(($m//*:group[@nr = 2], $m//*:group[@nr = 3])[1]), '\{n\}', string($n))
};

declare function local:esc($s as xs:string?) as xs:string {
  replace(replace(replace(replace(string($s), '&amp;', '&amp;amp;', 'q'), '&lt;', '&amp;lt;', 'q'), '&gt;', '&amp;gt;', 'q'), '"', '&amp;quot;', 'q')
};

declare function local:page-index() as xs:string {
  let $items := for $a in $arts stable order by string($a/@lemma-fold)
                return concat('<li><a href="', $a/@id, '.html">', local:esc($a/@lemma), '</a> <span>Bd. ', $a/@band, ', Sp. ', $a/@col-from, '</span></li>')
  return local:file('pages/index.html', concat('<!DOCTYPE html>&#10;<html lang="', $lang, '"><head><meta charset="utf-8">&#10;',
    '<meta name="viewport" content="width=device-width, initial-scale=1">&#10;',
    '<title>HWPh — ', local:w('pages.title'), '</title>&#10;<link rel="stylesheet" href="page.css"></head><body>&#10;',
    '<nav><a class="open" href="../index.html">', local:w('pages.reader'), '</a></nav>&#10;<header><h1>', local:w('pages.title'),
    '</h1><div class="loc">', local:plural('n.articles', count($arts)), '</div></header>&#10;',
    '<ul class="idx" lang="de">&#10;', string-join($items, '&#10;'), '&#10;</ul>&#10;</body></html>&#10;'))
};

declare function local:reader() as xs:string {
  let $src := unparsed-text($ui)
  let $mark := '&lt;script&gt;&#10;"use strict";'
  return local:file('index.html', concat(substring-before($src, $mark),
    '&lt;script&gt;window.HWPH_STATIC = true;&lt;/script&gt;&#10;&lt;script src="static_api.js"&gt;&lt;/script&gt;&#10;', $mark,
    substring-after($src, $mark)))
};

string-join((
  local:index-files(), local:meta(), local:register-files(), local:graph(), local:persons(), local:patterns(),
  local:authors(), local:extras(), local:page-index(), local:reader()
))
