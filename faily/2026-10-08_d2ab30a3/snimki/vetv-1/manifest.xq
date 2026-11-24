xquery version "3.1";
(: manifest.json — every file of the static reader, for a crawler that collects the reader from a
   server. The pages link to one another, but most data files are loaded by computed names (the search
   index by the first letters of a word, an article by its number), so a crawler cannot find them by
   following links; it reads this list.

   The names come from the database (articles, persons, register, pictures) and from the two files of
   the index that say which index files exist (data/meta.js: shards; data/pdir.js: words with a file
   of their own) — run after the other queries, with $site the folder (or file: URI) of the reader. :)
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "text";

declare variable $site as xs:string external;
declare variable $db := /hwph;

declare variable $base as xs:string :=
  let $s := translate($site, '\', '/')
  let $s := if (ends-with($s, '/')) then $s else concat($s, '/')
  return if (starts-with($s, 'file:')) then $s else if (starts-with($s, '/')) then concat('file://', $s) else concat('file:///', $s);

declare function local:text($path as xs:string) as xs:string {
  unparsed-text(resolve-uri($path, $base), 'utf-8')
};

(: the strings of a JSON array written under "key": in a data file (pretty layout, may span lines) :)
declare function local:array($text as xs:string, $key as xs:string) as xs:string* {
  let $a := substring-before(substring-after($text, concat('"', $key, '":[')), ']')
  return analyze-string($a, '"([^"]*)"')//*:group[@nr = 1] ! string(.)
};

declare function local:q($s as xs:string) as xs:string {
  concat('"', replace(replace($s, '\', '\\', 'q'), '"', '\"', 'q'), '"')
};

let $meta := local:text('data/meta.js')
let $pdir-text := local:text('data/pdir.js')
let $pdir := parse-json(substring-before(substring-after($pdir-text, '&#10;'), '&#10;);'))
let $ids := $db/articles/article/@id ! string(.)
let $files := (
  'index.html', 'static_api.js', 'i18n.js', 'manifest.json',
  (: katex: everything the folder holds :)
  for $u in uri-collection(concat(resolve-uri('katex/', $base), '?recurse=yes'))
  return substring-after(string($u), $base),
  distinct-values($db/articles/article/html//*:img/@src[starts-with(., 'img/')] ! string(.)),
  'pages/index.html', 'pages/page.css', $ids ! concat('pages/', ., '.html'),
  ('meta', 'vocab', 'pdir', 'graph', 'persons', 'authors', 'extras') ! concat('data/', ., '.js'),
  $ids ! concat('data/a/', ., '.js'), $ids ! concat('data/t/', ., '.js'),
  for $s in local:array($meta, 'shards')
  return (concat('data/s/', $s, '.js'), concat('data/p/', $s, '.js'),
          for $k in 1 to (if (map:contains($pdir, $s)) then array:size($pdir($s)) else 0)
          return concat('data/p/', $s, '.', $k - 1, '.js')),
  local:array($meta, 'reg_shards') ! concat('data/r/', ., '.js'),
  distinct-values($db/persons/p ! (xs:integer(@id) idiv 500)) ! concat('data/pat/', ., '.js')
)
let $sorted := sort($files)
return concat('{"count":', count($sorted), ',&#10;"files":[&#10;', string-join($sorted ! local:q(.), ',&#10;'), '&#10;]}&#10;')
