xquery version "3.1";
(: Shared functions of the HWPh XQuery pipeline: folding, words, spelling key, base 36, JSON layout. :)
module namespace h = "hwph";

(: ---------------------------------------------------------------- folding
   The search form of every character comes from the database (<fold>), computed by the same code
   the reader uses, so both sides fold identically. One-to-one and deleted characters go through
   translate(); characters that fold to several letters (ß -> ss) are replaced first. :)

declare function h:fold-tables($db as document-node()) as map(*) {
  let $f := $db/hwph/fold/f
  let $single := $f[string-length(@to) eq 1]
  let $deleted := $f[string-length(@to) eq 0]
  return map {
    'from': string-join(($single/@c, $deleted/@c)),
    'to': string-join($single/@to),
    'multi': array { $f[string-length(@to) gt 1] ! [string(@c), string(@to)] },
    'nonword': string($db/hwph/nonword)
  }
};

declare function h:fold($s as xs:string?, $t as map(*)) as xs:string {
  let $m := fold-left($t?multi?*, string($s), function($acc, $p) { replace($acc, $p?1, $p?2, 'q') })
  return translate($m, $t?from, $t?to)
};

(: words of a folded text, as Python's \w+ finds them :)
declare function h:words($folded as xs:string, $t as map(*)) as xs:string* {
  let $blanks := string-join(for $i in 1 to string-length($t?nonword) return ' ')
  return tokenize(normalize-space(translate($folded, $t?nonword, $blanks)), ' ')[. ne '']
};

(: ---------------------------------------------------------------- spelling-tolerant key (hwph_search.skey) :)
declare function h:skey($term as xs:string) as xs:string {
  let $t := replace(replace(replace(replace($term, 'ph', 'f', 'q'), 'th', 't', 'q'), 'rh', 'r', 'q'), 'dt', 't', 'q')
  let $t := replace(replace(replace(replace(replace($t, 'ae', 'a', 'q'), 'oe', 'o', 'q'), 'ue', 'u', 'q'), 'ck', 'k', 'q'), 'tz', 'z', 'q')
  let $t := replace($t, 'ch', '&#xF8FF;', 'q')
  let $t := replace(replace($t, 'c([eiy])', 'z$1'), 'c', 'k', 'q')
  let $t := replace(replace($t, '&#xF8FF;', 'ch', 'q'), 'y', 'i', 'q')
  return replace($t, '(.)\1+', '$1')
};

(: ---------------------------------------------------------------- base 36 :)
declare function h:b36($n as xs:integer) as xs:string {
  if ($n lt 36) then substring('0123456789abcdefghijklmnopqrstuvwxyz', $n + 1, 1)
  else concat(h:b36($n idiv 36), h:b36($n mod 36))
};
