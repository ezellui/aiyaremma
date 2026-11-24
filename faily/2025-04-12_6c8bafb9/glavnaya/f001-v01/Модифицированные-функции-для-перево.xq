
(: 1. Главная функция для отображения списка inflections :)
declare function local:print-inflections($ref as element()?, $inflections as xs:string) as node()* {
    let $inflect-list := tokenize($inflections, ' ')
    let $word := $ref/ancestor-or-self::word[1]
    for $inflection at $pos in $inflect-list
    let $translated-inflection := c:print-inflect-value($inflection)
    let $inflect-word := xdb:key($word, 'inflect-table', $inflection)
        [not(@speech) or @speech=c:get-speech($word)]/
        ..[c:get-lang(.) = c:get-lang($word)]
    let $link := if ($inflect-word) then c:to-word-link($inflect-word) else () 
    return
    if ($inflect-word)
    then (<a href="{$link}">{$translated-inflection}</a>, if ($pos = count($inflect-list)) then () else text {' '})
    else text { ($translated-inflection), if ($pos = count($inflect-list)) then () else ' ' }
};

(: 2. Функции для обработки мест, где требуется перевод форм и вариантов :)

(: 2.1 Функция для получения перевода form и variant там, где они используются напрямую :)
declare function local:get-translated-form-variant($form as xs:string?, $variant as xs:string?) as xs:string {
    let $combined := string-join(
        (
            if ($form) then c:print-inflect-value($form) else (),
            if ($variant) then c:print-inflect-value($variant) else ()
        ),
        ' '
    )
    return normalize-space($combined)
};

(: 2.2 Функция для обработки вариантов и форм при нормализации пробелов :)
declare function local:normalize-and-translate-with-forms($mark as xs:string?, $form as xs:string?, $variant as xs:string?) as xs:string {
    let $translated-form := if ($form) then c:print-inflect-value($form) else ()
    let $translated-variant := if ($variant) then c:print-inflect-value($variant) else ()
    return normalize-space(concat($mark, ' ', $translated-form, ' ', $translated-variant))
};

(: 2.3 Функция для отображения вариаций :)
declare function local:print-matching-refs($value as xs:string, $variation-refs as element()*, $pubmode) as element() {
    let $matching-refs := for $i in $variation-refs[c:normalize-for-match(@v)=$value] order by translate($i/@mark, '-', '→') return $i
    return
    <li>{c:print-word($matching-refs[1], <print-word style="bold"/>)}
    {local:print-ref-set($matching-refs,
        <ref-set short-mode="{$pubmode}" show-mark="{$matching-refs[1]/@mark}" show-lang="{c:get-lang($matching-refs[1]/..)}"/>)}</li>
};

(: 3. Функция для отображения примечаний о формах в таблицах :)
declare function local:print-examples($ref as element()?) as node()* {(
    if ($ref/example) then text{' например: '} else (),
    for $example in $ref/example
    let $example-refs := xdb:key($ref, 'ref', $example/@source)
    let $example-ref := $example-refs[1]
    let $show-lang := c:other-lang($ref, $example-ref)
    return (
        if ($example/preceding-sibling::example) then text {', '} else (),
        c:print-word($example-ref, local:print-word-control($show-lang, 'parent')),
        if (not(count($example-refs)=1)) then text {' [ERROR:MISMATCH] '} else (),
        if (not($example/@t)) then c:print-gloss($example-ref) else (),
        if (not($example/@t='transform')) then () else
            let $example-transform-refs := xdb:key($example-ref, 'ref', $example-ref/transform/@source)
            let $example-transform-ref := $example-transform-refs[1]
            let $show-transform-lang := c:other-lang($example-ref, $example-transform-ref)
            return (
                text {' ← '},
                if (not(count($example-transform-refs)=1)) then text {' [ERROR:MISMATCH] '} else (),
                c:print-word($example-transform-ref, local:print-word-control($show-transform-lang))
            ),
        if (not($example/@t='inflect')) then () else
            let $example-inflect-refs := xdb:key($example-ref, 'ref', $example-ref/inflect/@source)
            let $example-inflect-ref := $example-inflect-refs[1]
            let $show-inflect-lang := c:other-lang($example-ref, $example-inflect-ref)
            return (
                text {' ← '},
                if (not(count($example-inflect-refs)=1)) then text {' [ERROR:MISMATCH] '} else (),
                c:print-word($example-inflect-ref, local:print-word-control($show-inflect-lang))
            ),
        if (not($example/@t[starts-with(., 'deriv')])) then () else (
            if ($example-ref/deriv[@source]) then text {' < '} else (),
            c:print-wordlet($example-ref/deriv[1]/@i3, ' &lt; '),
            c:print-wordlet($example-ref/deriv[1]/@i2, ' &lt; '),
            c:print-wordlet($example-ref/deriv[1]/@i1, ' &lt; '),
            for $example-deriv in $example-ref/deriv[@source]
                let $example-deriv-v := $example-deriv/@v
                let $example-deriv-source := $example-deriv/@source/string()
                let $example-deriv-refs := xdb:key($example-ref, 'ref', $example-deriv-source)
                let $example-deriv-ref := $example-deriv-refs[@v=$example-deriv-v][1]
                let $show-deriv-lang := c:other-lang($example-ref, $example-deriv-ref)
            return (
                c:print-word($example-deriv-ref, local:print-word-control($show-deriv-lang, 'parent')),
                if ($example-deriv/following-sibling::deriv) then text {'/'} else ()
            ),
            for $example-deriv in $example-ref/deriv[@from]
            return (
                <span> [&lt; {c:print-word($example-ref/.., <print-word show-link='y'/>)}]</span>
            )
        )
    )
)};
