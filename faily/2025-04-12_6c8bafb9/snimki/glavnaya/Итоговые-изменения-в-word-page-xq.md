
# Внесенные изменения в файл word-page.xq

На основе предоставленных файлов `word-page.txt` и `code-changes.txt`, я внес следующие изменения в код для обеспечения правильного перевода грамматических форм:

## 1. Добавлены вспомогательные функции для перевода форм и вариантов

```xquery
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

declare function local:normalize-and-translate-with-forms($mark as xs:string?, $form as xs:string?, $variant as xs:string?) as xs:string {
    let $translated-form := if ($form) then c:print-inflect-value($form) else ()
    let $translated-variant := if ($variant) then c:print-inflect-value($variant) else ()
    return normalize-space(concat($mark, ' ', $translated-form, ' ', $translated-variant))
};
```

## 2. Модифицирована функция `local:print-inflections`

```xquery
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
```

## 3. Заменены вызовы функции на главной странице слова

Заменены оба вхождения:
```xquery
{if ($word/class/@form) then (' (', local:print-inflections($word, normalize-space(concat($word/class/@mark, $word/class/@form, ' ', $word/class/@variant))), ') ') else ()}
```

на:
```xquery
{if ($word/class/@form) then (' (', local:print-inflections($word, local:normalize-and-translate-with-forms($word/class/@mark, $word/class/@form, $word/class/@variant)), ') ') else ()}
```

## 4. Модифицирован код вывода вариантов форм в таблицах

```xquery
<tr><th colspan="10">Примеры ({c:print-inflect-value(string($form))})</th></tr>
```

и

```xquery
let $variants := $ref/*[name()=$from]/normalize-space(replace(replace(concat(' ', c:print-inflect-value(@form), ' ', c:print-inflect-value(@variant), ' '), ' ', '  '), concat(' ', replace(c:print-inflect-value($omit), ' ', '  '), ' '), ''))
```

## 5. Заменен код для корректного отображения формы в ссылках

```xquery
{if ($from-ref/inflect/@form) then concat(' (', c:print-inflect-value($from-ref/inflect/@form), ')') else () }
```

## 6. Модифицирован код для отображения форм элементов составных слов

```xquery
if ($has-forms) then <td>{local:print-inflections($element-word, c:print-inflect-value(string($form)))}</td> else (),
```

## Результат

Благодаря этим изменениям, все формы и варианты теперь будут правильно переводиться с английского на русский язык с использованием существующей функции `c:print-inflect-value` из файла `common.xq`.
