xquery version "3.1";
(: The positional word index of the static reader: where in each article every word stands, so that a
   phrase, NEAR and a search with capitals are checked in the index itself instead of in the article
   texts (which a page opened from disk would have to load one by one).

     data/p/<xx>.js     the words beginning with the two letters <xx> (as data/s/<xx>.js)
     data/p/<xx>.<k>.js a word with very many places has a file of its own
     data/pdir.js       which words have a file of their own: { "<xx>": [word, …], … }

   For every word of the index (its search form) the forms it takes in the text, each with its places:
     "word": [["Form", "aid:pos,pos;pos;;pos aid:…"], …]
   An article is given as the difference to the previous one (base 36), then its five fields (lemma,
   text, notes, literature, authors) separated by ';', each a list of word numbers (from 0, as
   differences, base 36). A form is the word as the text writes it (capitals, accents), so that a
   search with capitals needs no article text either. Words are numbered as the index counts them: the
   folded text split by Python's \w+ (the database's <fold>, <nonword>, <rawsep> tables).

   The words are done in $parts groups (by their first letter), one after the other, so that the
   memory holds the places of one group at a time.
   Every file is preceded by a line "@@FILE@@ <path>". :)
import module namespace h = "hwph" at "common.xq";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "text";
declare option output:item-separator "";

(: a word whose places take more characters than this gets a file of its own :)
declare variable $heavy as xs:integer external := 60000;
declare variable $parts as xs:integer external := 8;

declare variable $db := /hwph;
declare variable $t := h:fold-tables(/);
declare variable $sep := string($db/rawsep);
declare variable $sep-blanks := string-join(for $i in 1 to string-length($sep) return ' ');
declare variable $dropped := string-join($db/fold/f[@to = '']/@c);

declare function local:shard($term as xs:string) as xs:string {
  string-join(string-to-codepoints(substring($term, 1, 2)) ! h:hex(.), '-')
};

(: positions as differences, base 36 :)
declare function local:deltas($p as xs:integer*) as xs:string {
  string-join(for $i in 1 to count($p) return h:b36($p[$i] - (if ($i eq 1) then 0 else $p[$i - 1])), ',')
};

(: the rows of one group of words: one per article and form, "word TAB form TAB article TAB places" :)
declare function local:rows($part as xs:integer) as xs:string* {
  for $a in $db/articles/article
  let $id := string($a/@id)
  let $fields := (string($a/@lemma), string($a/plain[@part = 'b']), string($a/plain[@part = 'n']),
                  string($a/plain[@part = 'l']), string-join($a/authors/author, ' '))
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
  group by $id, $w, $form
  let $lists := for $k in 1 to 5 return local:deltas(for $j in 1 to count($pos) return if ($field[$j] eq $k) then $pos[$j] else ())
  let $last := max((0, for $s at $k in $lists return if ($s ne '') then $k else 0))
  return concat($w, '&#9;', $form, '&#9;', $id, '&#9;', string-join(subsequence($lists, 1, $last), ';'))
};

(: the words of one group: word TAB shard TAB size TAB json of its forms :)
declare function local:words($part as xs:integer) as xs:string* {
  for $r in local:rows($part)
  let $w := substring-before($r, '&#9;')
  group by $w
  order by $w
  let $forms :=
    for $x in $r
    let $form := tokenize($x, '&#9;')[2]
    group by $form
    order by $form
    let $aids := for $y in $x return xs:integer(tokenize($y, '&#9;')[3])
    let $places := for $y in $x return tokenize($y, '&#9;')[4]
    return concat('[', h:qs($form), ',"', string-join(
      for $i in 1 to count($aids) return concat(h:b36($aids[$i] - (if ($i eq 1) then 0 else $aids[$i - 1])), ':', $places[$i]), ' '), '"]')
  let $json := concat('[', string-join($forms, ','), ']')
  return string-join(($w, local:shard($w), string(string-length($json)), $json), '&#9;')
};

declare function local:f($row as xs:string, $i as xs:integer) as xs:string {
  tokenize($row, '&#9;')[$i]
};

declare function local:file($path as xs:string, $key as xs:string, $members as xs:string*) as xs:string {
  concat('@@FILE@@ ', $path, '&#10;HWPH.put(', h:qs($key), ',&#10;{', string-join($members, ',&#10;'), '}&#10;);&#10;')
};

(: the files of one group; a line starting with U+E000 lists a shard's words with files of their own :)
declare function local:files($part as xs:integer) as xs:string* {
  for $x in local:words($part)
  let $s := local:f($x, 2)
  group by $s
  order by $s
  let $big := $x[xs:integer(local:f(., 3)) gt $heavy]
  let $small := $x[xs:integer(local:f(., 3)) le $heavy]
  return (
    local:file(concat('data/p/', $s, '.js'), concat('p/', $s), $small ! concat(h:qs(local:f(., 1)), ':', local:f(., 4))),
    for $b at $k in $big
    return local:file(concat('data/p/', $s, '.', $k - 1, '.js'), concat('p/', $s, '.', $k - 1),
                      concat(h:qs(local:f($b, 1)), ':', local:f($b, 4))),
    if (exists($big)) then concat('&#xE000;', h:qs($s), ':[', string-join($big ! h:qs(local:f(., 1)), ','), ']') else ()
  )
};

let $all := for $part in 0 to $parts - 1 return local:files($part)
return (
  $all[not(starts-with(., '&#xE000;'))],
  concat('@@FILE@@ data/pdir.js&#10;HWPH.put("pdir",&#10;{',
         string-join(sort($all[starts-with(., '&#xE000;')]) ! substring(., 2), ',&#10;'), '}&#10;);&#10;')
)
