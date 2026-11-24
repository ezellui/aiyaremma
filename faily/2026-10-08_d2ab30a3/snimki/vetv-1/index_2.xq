xquery version "3.1";
(: The word index of the static reader, computed from the plain texts of the database:

     data/s/<xx>.js     for every word beginning with the two letters <xx>: the articles it is in and
                        how often in each field (lemma, text, notes, literature, authors) — ranking
     data/p/<xx>.js     the same words: where they stand, in the forms the text writes them — phrases,
                        NEAR and searches with capitals are checked here, in every article
     data/p/<xx>.<k>.js a word with very many places has a file of its own
     data/pdir.js       which words have a file of their own: { "<xx>": [word, …], … }
     data/vocab.js      all words with their counts and spelling keys (wildcards, tolerant search)
     data/meta.js       lemma list, statistics, field lengths for ranking

   data/s/*.js: "word": "aid:c,c,c,c,c aid:…", the article as the difference to the previous one and
   the counts of the five fields, base 36, zeros at the end left out.
   data/p/*.js: "word": [["Form", "aid:pos,pos;pos;;pos aid:…"], …], the article as above, then the
   five fields separated by ';', each a list of word numbers (from 0, as differences, base 36).

   A word is what Python's \w+ finds in the folded text (the database's <fold> and <nonword> tables);
   its form is the same stretch of the text itself (split where <rawsep> says), with capitals and
   accents. The words are done in $parts groups (by their first letter), one after the other, so that
   the memory holds the places of one group at a time.
   Every file is preceded by a line "@@FILE@@ <path>". :)
import module namespace h = "hwph" at "common.xq";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "text";
declare option output:item-separator "";

(: a word whose places take more characters than this gets a file of its own :)
declare variable $heavy as xs:integer external := 60000;
declare variable $parts as xs:integer external := 8;
declare variable $built as xs:string external := format-dateTime(current-dateTime(), '[Y0001]-[M01]-[D01] [H01]:[m01]');

declare variable $db := /hwph;
declare variable $arts := $db/articles/article;
declare variable $t := h:fold-tables(/);
declare variable $sep := string($db/rawsep);
declare variable $sep-blanks := string-join(for $i in 1 to string-length($sep) return ' ');
declare variable $dropped := string-join($db/fold/f[@to = '']/@c);
declare variable $TAB := '&#9;';

declare function local:shard($term as xs:string) as xs:string {
  string-join(string-to-codepoints(substring($term, 1, 2)) ! h:hex(.), '-')
};

declare function local:fields($a as element(article)) as xs:string* {
  (string($a/@lemma), string($a/plain[@part = 'b']), string($a/plain[@part = 'n']),
   string($a/plain[@part = 'l']), string-join($a/authors/author, ' '))
};

(: numbers as differences, base 36 :)
declare function local:deltas($p as xs:integer*) as xs:string {
  string-join(for $i in 1 to count($p) return h:b36($p[$i] - (if ($i eq 1) then 0 else $p[$i - 1])), ',')
};

(: Python writes a float with repr(): always with a decimal point :)
declare function local:float($d as xs:double) as xs:string {
  let $s := string($d) return if (matches($s, '[.eE]')) then $s else concat($s, '.0')
};

(: the rows of one group of words: one per article and form,
   "word TAB form TAB article TAB counts of the five fields TAB places" :)
declare function local:rows($part as xs:integer) as xs:string* {
  for $a in $arts
  let $id := string($a/@id)
  let $fields := local:fields($a)
  return
    for $f at $k in $fields
    let $folded := h:words(h:fold($f, $t), $t)
    let $raw := tokenize(normalize-space(translate($f, $sep, $sep-blanks)), ' ')[translate(., $dropped, '') ne '']
    let $check := if (count($raw) ne count($folded)) then error(xs:QName('h:words'), concat('article ', $id, ' field ', $k,
                    ': the words of the text and of its search form do not match')) else ()
    for $w at $i in $folded
    where string-to-codepoints($w)[1] mod $parts eq $part
    let $r := $raw[$i]
    let $form := if (translate($r, $dropped, '') eq $r) then $r
                 else (replace($r, '^[^\p{L}\p{N}_]+|[^\p{L}\p{N}_]+$', '')[. ne ''], $r)[1]
    let $field := $k
    let $pos := $i - 1
    group by $w, $form
    let $lists := for $n in 1 to 5 return local:deltas(for $j in 1 to count($pos) return if ($field[$j] eq $n) then $pos[$j] else ())
    let $last := max((0, for $s at $n in $lists return if ($s ne '') then $n else 0))
    return string-join(($w, $form, $id, string-join(for $n in 1 to 5 return string(count($field[. eq $n])), ','),
                        string-join(subsequence($lists, 1, $last), ';')), $TAB)
};

(: the words of one group: word TAB docs TAB count TAB spelling key TAB shard TAB counts TAB size TAB places :)
declare function local:words($part as xs:integer) as xs:string* {
  for $r in local:rows($part)
  let $w := substring-before($r, $TAB)
  group by $w
  order by $w
  let $forms :=
    for $x in $r
    let $form := tokenize($x, $TAB)[2]
    group by $form
    order by $form
    let $aids := for $y in $x return xs:integer(tokenize($y, $TAB)[3])
    let $places := for $y in $x return tokenize($y, $TAB)[5]
    return concat('[', h:qs($form), ',"', string-join(
      for $i in 1 to count($aids) return concat(h:b36($aids[$i] - (if ($i eq 1) then 0 else $aids[$i - 1])), ':', $places[$i]), ' '), '"]')
  let $places := concat('[', string-join($forms, ','), ']')
  (: the counts of an article, summed over the forms :)
  let $per-article :=
    for $x in $r
    let $aid := xs:integer(tokenize($x, $TAB)[3])
    let $cs := tokenize($x, $TAB)[4]
    group by $aid
    order by $aid
    let $c := if (count($cs) eq 1) then tokenize($cs, ',') ! xs:integer(.)
              else for $n in 1 to 5 return sum($cs ! xs:integer(tokenize(., ',')[$n]))
    let $last := max(for $x at $n in $c return if ($x gt 0) then $n else 0)
    return concat($aid, ' ', sum($c), ' ', string-join(subsequence($c, 1, $last) ! h:b36(.), ','))
  let $aids := $per-article ! xs:integer(substring-before(., ' '))
  let $counts := string-join(
    for $e at $i in $per-article
    return concat(h:b36($aids[$i] - (if ($i eq 1) then 0 else $aids[$i - 1])), ':', substring-after(substring-after($e, ' '), ' ')), ' ')
  return string-join(($w, string(count($per-article)), string(sum($per-article ! xs:integer(tokenize(., ' ')[2]))),
                      h:skey($w), local:shard($w), $counts, string(string-length($places)), $places), $TAB)
};

declare function local:f($row as xs:string, $i as xs:integer) as xs:string {
  tokenize($row, $TAB)[$i]
};

declare function local:file($path as xs:string, $content as xs:string) as xs:string {
  concat('@@FILE@@ ', $path, '&#10;', $content)
};

declare function local:places-file($path as xs:string, $key as xs:string, $members as xs:string*) as xs:string {
  local:file($path, concat('HWPH.put(', h:qs($key), ',&#10;{', string-join($members, ',&#10;'), '}&#10;);&#10;'))
};

(: the files of one group. Lines for the files made at the end: U+E000 a shard's words with a file of
   their own, U+E001 a word of the vocabulary "word TAB docs TAB count TAB key TAB shard" :)
declare function local:part($part as xs:integer) as xs:string* {
  for $x in local:words($part)
  let $s := local:f($x, 5)
  group by $s
  order by $s
  let $big := $x[xs:integer(local:f(., 7)) gt $heavy]
  let $small := $x[xs:integer(local:f(., 7)) le $heavy]
  return (
    local:file(concat('data/s/', $s, '.js'), h:js(concat('s/', $s), h:o($x ! h:m(local:f(., 1), h:s(local:f(., 6)))))),
    local:places-file(concat('data/p/', $s, '.js'), concat('p/', $s), $small ! concat(h:qs(local:f(., 1)), ':', local:f(., 8))),
    for $b at $k in $big
    return local:places-file(concat('data/p/', $s, '.', $k - 1, '.js'), concat('p/', $s, '.', $k - 1),
                             concat(h:qs(local:f($b, 1)), ':', local:f($b, 8))),
    if (exists($big)) then concat('&#xE000;', h:qs($s), ':[', string-join($big ! h:qs(local:f(., 1)), ','), ']') else (),
    $x ! concat('&#xE001;', string-join(subsequence(tokenize(., $TAB), 1, 5), $TAB))
  )
};

(: the number of words of every field of every article (ranking: field lengths) :)
declare variable $lens as xs:string* :=
  for $a in $arts
  return string-join(($a/@id, local:fields($a) ! string(count(h:words(h:fold(., $t), $t)))), ' ');

declare function local:vocab($terms as xs:string*) as xs:string {
  local:file('data/vocab.js', h:js('vocab', h:o((
    h:m('t', h:a($terms ! h:s(local:f(., 1)))),
    h:m('d', h:a($terms ! h:n(local:f(., 2)))),
    h:m('c', h:a($terms ! h:n(local:f(., 3)))),
    h:m('k', h:a($terms ! h:s(if (local:f(., 4) eq local:f(., 1)) then '' else local:f(., 4))))))))
};

declare function local:meta($terms as xs:string*) as xs:string {
  let $total := sum($lens ! sum(subsequence(tokenize(., ' '), 2) ! xs:integer(.)))
  let $reg-shards := distinct-values($db/register/r ! (if (string(@term-fold) ne '') then local:shard(string(@term-fold)) else '_'))
  return local:file('data/meta.js', h:js('meta', h:o((
    h:m('info', h:o((h:m('engine', h:s('static')),
                     h:m('stats', h:o(($db/json[@name = 'stats']/o/m, h:m('words', h:n(count($terms))))))))),
    h:m('lemmas', h:a(
      for $a in $arts stable order by string($a/@lemma-fold)
      return h:a((h:n($a/@id), h:s($a/@lemma), h:s($a/@band), h:n($a/@col-from), h:s($a/@kind), h:n($a/@col-to))))),
    h:m('n_docs', h:n(count($lens))),
    h:m('avgdl', h:n(local:float(xs:double($total) div count($lens)))),
    h:m('lengths', h:o($lens ! h:mi(xs:integer(tokenize(., ' ')[1]), h:a(subsequence(tokenize(., ' '), 2) ! h:n(.))))),
    h:m('shards', h:a(for $s in distinct-values($terms ! local:f(., 5)) order by $s return h:s($s))),
    h:m('reg_shards', h:a(for $s in $reg-shards order by $s return h:s($s))),
    h:m('built', h:s($built))))))
};

let $all := for $part in 0 to $parts - 1 return local:part($part)
let $terms := sort($all[starts-with(., '&#xE001;')] ! substring(., 2))
return (
  $all[not(starts-with(., '&#xE000;') or starts-with(., '&#xE001;'))],
  local:file('data/pdir.js', concat('HWPH.put("pdir",&#10;{',
    string-join(sort($all[starts-with(., '&#xE000;')]) ! substring(., 2), ',&#10;'), '}&#10;);&#10;')),
  local:vocab($terms),
  local:meta($terms)
)
