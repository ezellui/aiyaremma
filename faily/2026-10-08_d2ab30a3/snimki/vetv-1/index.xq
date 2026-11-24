xquery version "3.1";
(: The word index of the whole dictionary, as hwph_build.py computes it into the table terms:
   one line per word: term TAB docs TAB count TAB skey TAB postings  (postings as hwph_search.encode),
   then one line per article: '#len' TAB id TAB l0 … l4 (the field lengths used for ranking). :)
import module namespace h = "hwph" at "common.xq";
declare option saxon:output "method=text";
declare namespace saxon = "http://saxon.sf.net/";

let $db := /
let $t := h:fold-tables($db)
let $rows :=
  for $a in $db/hwph/articles/article
  let $fields := (
    string($a/@lemma),
    string($a/plain[@part = 'b']),
    string($a/plain[@part = 'n']),
    string($a/plain[@part = 'l']),
    string-join($a/authors/author, ' '))
  let $words := for $f in $fields return [h:words(h:fold($f, $t), $t)]
  return (
    string-join(('#len', $a/@id, $words ! array:size(.)), '&#9;'),
    (: per article: every word with its counts in the five fields, trailing zeros dropped :)
    for $f at $i in $words, $w in $f?*
    let $field := $i
    group by $w
    let $c := for $k in 1 to 5 return count($field[. eq $k])
    let $last := max((0, for $x at $k in $c return if ($x gt 0) then $k else 0))
    return concat($w, ' ', $a/@id, ' ', string-join(subsequence($c, 1, $last) ! h:b36(.), ','), ' ', sum($c))
  )
return (
  for $r in $rows[not(starts-with(., '#len'))]
  let $term := substring-before($r, ' ')
  group by $term
  order by $term
  let $parts := $r ! tokenize(., ' ')
  let $aids := for $i in 1 to count($r) return xs:integer($parts[($i - 1) * 4 + 2])
  let $post := string-join(
      for $i in 1 to count($r)
      return h:b36($aids[$i] - (if ($i eq 1) then 0 else $aids[$i - 1])) || ':' || $parts[($i - 1) * 4 + 3],
      ' ')
  return string-join(($term, count($r), sum(for $i in 1 to count($r) return xs:integer($parts[$i * 4])),
                      h:skey($term), $post), '&#9;') || '&#10;',
  $rows[starts-with(., '#len')] ! (. || '&#10;')
)
