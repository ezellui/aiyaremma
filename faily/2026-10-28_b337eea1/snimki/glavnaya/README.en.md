# Roots of Neo-Quenya, Neo-Sindarin and Neo-Primitive Elvish words from Eldamo

*Русская версия: [README.md](README.md).*

`neo-roots.json` gives every word of the lists
[vocabulary-words-nq](https://eldamo.org/content/vocabulary-indexes/vocabulary-words-nq.html),
[vocabulary-words-ns](https://eldamo.org/content/vocabulary-indexes/vocabulary-words-ns.html) and
[vocabulary-words-np](https://eldamo.org/content/vocabulary-indexes/vocabulary-words-np.html) (Eldamo 0.8.13)
its root or set of roots:

| group | words | of which | with roots | through `deprecated`/cognate |
|---|---|---|---|---|
| `nq` Neo-Quenya | 6060 | NQ. 2961, Q. 2058, ᴹQ. 1041 | 5525 | 65 |
| `ns` Neo-Sindarin | 3209 | NS. 1474, S. 1160, N. 575 | 2931 | 128 |
| `np` Neo-Primitive | 1571 | ✶ 969, ᴹ✶ 594, N✶ 8 | 1250 | 8 |

It builds in a few seconds with the Python standard library only (Python 3.8 on Windows 7 will do):

```
python neo_roots.py data/eldamo-data.xml neo-roots.json          # all three groups
python neo_roots.py data/eldamo-data.xml ns-roots.json ns        # one group
python show.py --en neo-roots.json palantír huorn miltë          # entries, one line per root
python show.py --en --tree neo-roots.json palantír               # the derivation tree
python show.py --en --root neo-roots.json LUP LAS¹               # an entry of the root index
```

`data/eldamo-data.xml` is the Eldamo 0.8.13 data model from [pfstrack/eldamo](https://github.com/pfstrack/eldamo)
(`src/data/eldamo-data.xml`), © Paul Strack, CC BY 4.0. Any later version of the same file will do.

## The word lists

The same selection as `vocabulary-index.xq` with `id=nq`, `id=ns` and `id=np`: words of nq, q, mq / ns, s, n /
np, p, mp (the page drops eq, en, g and ep), without `<combine>`, `<deprecated>` or `<see>`, without names,
phrases, grammar, phonetics and roots themselves, not `[unglossed]`, and without `-` or `|` in `@mark`. `spelling`
is the form as the list shows it: normalized for NQ (`c:normalize-spelling`: q → qu, k → c, final -e → -ë), as in
the database for NS and NP.

The NP list holds Primitive Elvish *words* (✶galadā, ✶lassē, ✶-i(n)ki); roots are not part of it, they are the
answer. These words also appear in the NQ and NS trees as primitive forms, but only 716 of the 1571 lie on
someone's path to a root. N√GAWAK (a root Eldamo 0.8.13 marks as a noun, and so lists) gets the rule `self`:
it is its own root.

## The file

```json
{
 "source": {"eldamo_version": "0.8.13", "site": "https://eldamo.org"},
 "groups": {"nq": {"count": 6060, "with_roots": 5525, "by_rule": {…}, "uncertain": 65, …}, "ns": {…}},
 "words": [
  {
   "group": "nq", "word": "tyallas", "spelling": "tyallas", "lang": "nq", "lang_name": "Neo-Quenya",
   "speech": "n", "gloss": "(playing) card", "url": "https://eldamo.org/content/words/word-1340155721.html",
   "rule": "elements",
   "roots": [
    {"form": "TYAL", "lang": "mp", "url": "…", "gloss": "play", "part": 0,
     "via": [{"rel": "element", "lang": "q", "form": "tyal-", "url": "…"},
             {"rel": "combine", "lang": "mq", "form": "tyal-", "url": "…"}]},
    {"form": "LAS¹", "lang": "p", "url": "…", "part": 1, "via": […]}
   ]
  }
 ],
 "roots": [ … ]
}
```

- `roots` — the chosen roots. When a word has several parts (a compound), each root has a `part`: roots with
  different `part` add up (√PAL + √TIR, S. huorn = ᴹ√KHUG + √ORO), roots with the same `part` are alternatives
  (Q. alda: √GAL² / ᴹ√GALAD). Without `part`, all roots are alternatives of one part.
- `via` — the chain from the word to the root: `element`, `deriv` (an intermediate form), `combine` (the same word
  in another conception, merged by Eldamo), `see`, `deprecated`, `cognate`. An empty chain means the word itself
  names the root.
- `same_as` — where Eldamo merges the root itself: the chain of its `<combine>` links and the Neo-Primitive root
  it is filed under (ᴹ√LUB² ≡ √LUB³ ≡ N√LUP). The last item is handy for matching roots of different periods.
- `gaps` — parts without a root, in their place (Q. firya = √PHIR + -ya; suffixes, words without an etymology).
- `also` — roots from lower-ranked sources that are not among the chosen ones; each has a `rule` saying where it
  comes from.
- `rule` — the rule that chose the roots; `uncertain` — the chain goes through `deprecated` or `cognate`.

### The derivation tree (`tree`)

The same chosen roots and gaps as nested blocks: a word's block holds its parts (`parts`, one block per element,
in order) or its alternatives (`from`, different derivations); an element's block holds what it comes from, and
so on down to the root: intermediate form → primitive form → root. An element may have elements of its own.

```
python show.py --en --tree neo-roots.json alda estolië
```
```
q alda (n) 'tree'  rule=deriv
   | deriv: p √GAL²  (direct; the same root also through the primitive form)
   | deriv: p ✶galadā
         written PE17/135.4516: galadā > ʒalaðā > ʒalðā > alda
      | deriv: mp √GALAD
      | deriv: p √GAL²
nq estolië (n) 'camp'  rule=cognate ['cognate']
   cognate: s estolad
      [0] element: s estola-
         [0] element: p √ET  — no root  ✗ not matched: ET
         [1] element: p √TOL
```

A node has `rel` — how it links to the block above (`element`, `deriv`, `combine`, `see`, `deprecated`,
`cognate`); `kind` — `root`, `protoform` (a word of a Primitive Elvish language) or `form` (a word or intermediate
form of another language); `form`, `lang`, `url`, `gloss`; a root also has `same_as`. A gap is `"gap": true`; the
root of a part of a partial cognate whose consonants are not found in the word stays in its place with `gap` and
`not_matched`.

`shortcut: true` marks a root the word names directly when, beside it, a derivation reaches the same root through
an intermediate form. Eldamo often records both paths: Q. ‑(n)dur comes from ✶‑ndūr < √(N)DUR (its own `<deriv>`),
while the reference PE17/152 derives *ndur* straight from DUR. Both paths are kept and the direct one is marked as
a shortcut; 1007 words have one (Q. alda: √GAL² directly and through ✶galadā). The flat `roots` list still has
the root once.

`written` — how the word's own references (not those of its inflected forms) write the link to this node: the form
in the source's spelling (`form`), the place (`source`), the form of the reference (`ref`) and the written
intermediate forms that have no pages of their own (`intermediate`, from the primitive form towards the word, as
Eldamo prints ✶v > i1 > i2 > i3 > word). It is given only when it differs from the node's headword by more than
case, √ or a homonym number.

The root's language is always given (`p` — late √, `mp` — ᴹ√ of the Etymologies, `np` — neo, `ep` — ᴱ√): Eldamo
itself links many late words to ᴹ√ roots (Q. lár < ᴹ√DAR), so filter by it if you want late roots only.

## The root index (`roots`)

The roots of the [roots-np](https://eldamo.org/content/root-indexes/roots-np.html) list — the same selection as
`root-index.xq` with `id=np`: roots of np, p, mp and ep without `<combine>` (1932). Eldamo does not separate the
unrecommended roots in that list; it marks them ⚠️. Here that is `recommended: false` plus `warnings` with Eldamo's
reasons: `deprecated` (replaced, itself or the root its `<see>` names; the replacement is in `see_instead`),
`deleted` (`|`), `rejected` (`-`), `doubtful` (`‽`), `unglossed`, `early` (ᴱ√). 1034 roots are recommended.

```
python show.py --en --root neo-roots.json LUP
np LUP 'hump, lump, fat'  recommended
   filed under it: p LUB³, ep ULUN(T), ep ULUMP
   derives from: np PUL
   nq (3): filiculumpe, ulumpë, ulumpembë
   ns (1): lûb
```

An entry has `form`, `lang`, `url`, `gloss` (and `ngloss` if different), `mark`, the status, and also
`merged` (roots of other conceptions merged into this one by `<combine>`: √LAS¹ holds ᴹ√LAS¹ and ᴱ√LASA),
`filed_under` / `filed_here` (the Neo-Primitive root it is filed under, and the roots filed under it), `see`,
`derives_from` (roots the root itself derives from: ᴹ√GALAD < √GAL²) and `derivatives` — the words of the three
lists that have this root among their chosen roots, by group, as links to their entries (`through` when the word
names a root merged into this one: √LAS¹ also gets the words of ᴹ√LAS¹). Trees and glosses of the words are not
repeated; they are in the word entries by `url`. Roots in `also` do not count as derivations.

1070 roots of the list have derivatives; 107 recommended roots have none (no `derivatives` field) — a ready list
for coining new words.

Six roots the words rely on are not in Eldamo's list; they are added with `in_list: false` and a reason in
`not_listed_because`, so that the index covers every word: `merged_into_word` — Eldamo merged the root not into a
root but into a Primitive Elvish word (ᴹ√LŌ → ✶lō¹, ᴱ√SA → ✶sa, ᴱ√LĒ → ✶dē, ᴹ√AKLA(R) → ✶aklar(a));
`combined_with_itself` — its `<combine>` points to itself (ᴹ√LA), and Eldamo's list loses it;
`not_marked_root` — a root marked as a noun (N√GAWAK).

## The graph (`neo-roots-graph.html`)

An interactive d3 page: nodes are roots, primitive forms and words; arrows go from the source to what derives
from it; colour and line pattern show the kind of link (derivation, element, merged form, stub, replacement,
cognate, and for roots — merging, filing under another root, derivation from a root). The whole graph — 14,037
nodes and 15,404 links, nearly all in one component — is not drawn at once: that would be slow and unreadable.
The page shows a neighbourhood: the chosen word with its tree down to the roots and its nearest derivatives, or a
root with its derivatives two steps deep; double-clicking a node expands its neighbours, and “+N” by a label is
the number of the node's links still hidden. Shortcuts (`shortcut`) are hidden by default so that the path runs
through the intermediate form; a switch in the legend shows them, and the word's card always lists them, marked
“direct”. Each kind of link can be switched off in the legend. The address `#n-<Eldamo page id>` opens a node
directly.

```
python make_graph.py neo-roots.json graph_template.html neo-roots-graph.html --standalone
```

`graph_template.html` is the page itself with the placeholders `/*GRAPH*/` and `/*MESSAGES*/`, where
`make_graph.py` writes the graph (1.7 MB) and the interface catalog; without `--standalone` it produces a page
body for a host that adds its own `<head>`.

The interface is bilingual, Russian and English, as in Quettamin: the catalog `graph_messages.json`
(`key → {ru, en}`, placeholders `{name}`), static markup marked with `data-i18n` and `data-i18n-attr`, everything
else built through `t(key)`. The language is the one last chosen with the button (kept in the browser), else the
browser's language; switching redraws the page in place and keeps the open graph. Eldamo's data (forms, glosses)
are not translated. A new language is one more field in each catalog entry and in the switch.

d3 7.8.5 loads from cdnjs and the fonts from Google Fonts, so the file needs a network connection.

## Rules, by rank

1. **elements** — two or more elements with roots: the roots by part. Elements come from the entry, or, if it has
   none, from one of its references (the one with the same form, else the first). A root a reference names in
   place of an element without an etymology takes that element's place if it begins with the same consonant
   (S. huorn: hû¹ → KHUG); affixes are not filled this way.
2. **deriv** — roots named by the word's derivations: the entry's `<deriv>` and `<deriv source>` inside its
   references (by `@source`, as `c:get-ref`). Roots an intermediate form leads to (✶galadā < ᴹ√GALAD) are added as
   alternatives.
3. **element** — one element with a root, the others are gaps.
4. **intermediate** — only through intermediate forms (Q. lassë < ✶lassē < √LAS¹).
5. **combine** — through words merged into this one (NQ. hlöa ← Q. hlöa < ✶(s)loga < √LOG).
6. **see** — through a stub reference.
7. **deprecated** — through a word this one replaced. Accepted only if it begins with the same consonant
   (b~v~w, k~c~g~h, p~f, t~d~th, n~ñ, rh~r, lh~l) or both forms begin with a vowel, and the consonants of all its
   roots are found in the word. Older forms of the same word pass (ᴱQ. milt → NQ. miltë; N. lhoch → NS. loch,
   N. rhand → NS. rand, N. tofn → NS. tovn), other words do not (NQ. sin → latúcen, Q. engë → né,
   ᴱQ. wara- → psar-, G. cwiliog → S. calen). A root replaced by a word counts as that word's root only if the word
   begins with the same consonant (ᴱ√SINI → ✶sinki — yes, ᴱ√GWAṘA → psar- — no).
8. **cognate** — through cognates (transitively, as the Cognates section); Elvish languages only, and only roots
   whose consonants (at least two) are found in the word; a part of a compound cognate not found in the word is a
   gap with `not_matched`.

The consonant check follows the word's branch: for Sindarin, ch, dh, lh, rh, mh are single sounds, m matches the
labials (lenition m > v), and a velar or y of the root may be missing (medial g, y > i); for Quenya, ngw = ŋg and
gw > w.

To stay careful:

- cognates are not used below the word itself (for elements and intermediate forms), and a cognate's roots found
  through `deprecated` or another cognate do not count;
- a cognate's root goes into `also` only if neither the word nor the cognate is a compound: N. anrand
  (= ann + rand) does not give ᴹQ. randa the root ᴹ√ANAD, S. dagnir does not give Q. nehtar the root √N(D)ER;
- what Tolkien rejected (`-` in `@mark`) does not count unless the word itself is rejected;
- primitive forms written in capitals count as roots: in 0.8.13 N√GAWAK, ᴱ√ƷAWAKA and ᴱ√OWO are marked as nouns;
- cycles (Q. nelquë ↔ quainel) are cut; the result is deterministic.

## Comparison with Quettamin

Up to version 3.10, root resolution in `quettamin/shared/lexicon.py` agreed with this one for 5588 of 6060 NQ
words and 2914 of 3209 NS words (there were no words where only Quettamin found a root). In 3.10 Quettamin adopted
these rules (9696 matches of 9709 by its changelog), and in 3.11 it took the root index and the tree of origin.
Shortcuts (`shortcut`) appeared here later: Quettamin still merges the alternatives of one part by root
(`shared/lexicon.py`, `alts` and the merge in `_root_groups`), so it loses the path through the primitive form
when the root is the same.

Words left without a root are mostly suffixes, pronouns, particles and words for which Eldamo gives no etymology,
neither of their own nor through merged forms (S. rhîw “winter”, Q. fúmë “breath”; the primitive forms ✶tulku,
✶dankĭnā, ✶stama- have only a reference to a source — the root is obvious from the form, but Eldamo does not link
it, and it is not guessed here).
