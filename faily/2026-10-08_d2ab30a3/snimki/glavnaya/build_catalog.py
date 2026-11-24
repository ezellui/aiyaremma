"""Build config/messages/messages-ru.xml and check it covers the prototype pages.

usage: build_catalog.py QUERY_CONFIG_DIR FORM_TOKENS_JSON OUTPUT_XML
"""
import json
import re
import sys
from xml.sax.saxutils import escape, quoteattr

query_dir, tokens_json, output = sys.argv[1:4]

# ------------------------------------------------------------------ interface strings
MSG = {
    # navigation
    'Home': 'Главная',
    'Languages': 'Языки',
    'Search': 'Поиск',
    '← Previous': '← Предыдущее',
    'Next →': 'Следующее →',
    'Previous Phrase': 'Предыдущая фраза',
    'Next Phrase': 'Следующая фраза',
    'Language Index': 'Список языков',
    '{1} Words': '{1}: слова',
    '{1} Names': '{1}: имена',
    '{1} Phrases': '{1}: фразы',
    '{1} Grammar': '{1}: грамматика',
    '{1} Roots': '{1}: корни',
    '{1} Phonetics': '{1}: фонетика',
    # language page
    'Vocabulary': 'Словарь',
    'Roots': 'Корни',
    'Words': 'Слова',
    'Names': 'Имена',
    'Phrases': 'Фразы',
    'Grammar': 'Грамматика',
    'Phonetics': 'Фонетика',
    'Semantic Categories': 'Семантические категории',
    'Full List of Roots': 'Полный список корней',
    'Full Word List': 'Полный список слов',
    'Neologisms': 'Неологизмы',
    'Deprecated Words': 'Нерекомендуемые слова',
    'For more information about how this vocabulary list was assembled, see:':
        'Подробнее о том, как составлен этот словарь, см.:',
    'Unexplained Languages': 'Неописанные языки',
    # word page: section headings
    'Reference': 'Источник',
    'References': 'Источники',
    'Glosses': 'Значения',
    'Variations': 'Варианты',
    'Notes': 'Примечания',
    'Related': 'Связанные слова',
    'Changes': 'Изменения',
    'Inflections': 'Словоизменение',
    'Elements': 'Составные части',
    'Element In': 'Входит в состав',
    'Cognates': 'Родственные слова',
    'Derivations': 'Происхождение',
    'Derivatives': 'Производные',
    'Phonetic Developments': 'Фонетическое развитие',
    'Phonetic Development': 'Фонетические изменения',
    'Phonetic Rule Elements': 'Составляющие фонетического правила',
    'Phonetic Rule Examples': 'Примеры фонетического правила',
    'Applied Derivational Rules': 'Применённые правила словообразования',
    'Order ({1})': 'Очерёдность ({1})',
    'Examples ({1})': 'Примеры ({1})',
    # word page: phrases
    'see': 'см.',
    'see instead:': 'вместо этого см.:',
    'see above': 'см. выше',
    'Category': 'Категория',
    'created by {1}': 'автор: {1}',
    'vetted by {1}': 'проверено: {1}',
    'See {1} for discussion.': 'Обсуждение см. в статье {1}.',
    'See {1} for further discussion.': 'Подробнее см. {1}.',
    'See also {1}{2}.': 'См. также {1}{2}.',
    'for example:': 'например:',
    'no change': 'без изменений',
    'After': 'После',
    'Before': 'До',
    'and': 'и',
    'Unglossed [{1}]': 'Без значения [{1}]',
}

PLURAL = {
    '⇒ {1} compounds': {
        'one': '⇒ {1} сложное слово',
        'few': '⇒ {1} сложных слова',
        'many': '⇒ {1} сложных слов',
    },
}

# ------------------------------------------------------------------ data labels by id
LANGUAGES = {
    'np': 'Неопраэльфийский', 'nq': 'Неоквенья', 'ns': 'Неосиндарин',
    'p': 'Праэльфийский', 'aq': 'Древний квенья', 'q': 'Квенья', 'van': 'Ваньярин',
    'at': 'Древний телерин', 't': 'Телерин', 'os': 'Древний синдарин', 's': 'Синдарин',
    'norths': 'Северный синдарин', 'nan': 'Нандорин', 'av': 'Аварин',
    'ed': 'Языки эдайн', 'pad': 'Праадунайский', 'ad': 'Адунайский', 'wes': 'Вестрон',
    'roh': 'Роханский', 'wos': 'Язык друэдайн', 'dun': 'Дунландский', 'eas': 'Язык вастаков',
    'kh': 'Кхуздул', 'khx': 'Кхуздул (внешний)', 'bs': 'Чёрное наречие', 'val': 'Валарин',
    'ent': 'Энтийский', 'teng': 'Тенгвар', 'cir': 'Кирт', 'sar': 'Сарати', 'un': 'Неизвестный',
    'mp': 'Средний праэльфийский', 'maq': 'Средний древний квенья', 'mq': 'Средний квенья',
    'lin': 'Линдарин', 'on': 'Древний нолдорин', 'n': 'Нолдорин', 'mt': 'Средний телерин',
    'ilk': 'Илькорин/дориатрин', 'dan': 'Данийский/оссириандский', 'lem': 'Лемберин',
    'tal': 'Талиска', 'ep': 'Ранний праэльфийский', 'eq': 'Ранний квенья', 'g': 'Гномский',
    'en': 'Ранний нолдорин', 'et': 'Солосимпи/ранний телерин', 'eilk': 'Ранний илькорин',
}

LANGUAGE_CATS_BY_ID = {
    'neo': 'Сводные (нео-) языки',
    'late': 'Поздний период (1950–1973)',
    'middle': 'Средний период (1930–1950)',
    'early': 'Ранний период (1910–1930)',
}
LANGUAGE_CATS_BY_NAME = {
    'Mannish Languages': 'Языки людей',
    'Other Languages': 'Другие языки',
    'Writing Systems': 'Письменности',
}

# ------------------------------------------------------------------ parts of speech
SPEECH = {
    'n': 'сущ.', 'adj': 'прил.', 'vb': 'гл.', 'adv': 'нареч.', 'pron': 'мест.',
    'prep': 'предл.', 'conj': 'союз', 'interj': 'межд.', 'suf': 'суфф.', 'pref': 'прист.',
    'article': 'арт.', 'particle': 'част.', 'affix': 'афф.',
    'cardinal': 'числ. колич.', 'ordinal': 'числ. поряд.', 'fraction': 'числ. дробн.',
    'root': 'корень',
    'masc-name': 'имя муж.', 'fem-name': 'имя жен.', 'place-name': 'топоним',
    'collective-name': 'собир. имя', 'collective-noun': 'собир. сущ.',
    'proper-name': 'имя собств.', 'family-name': 'родовое имя',
    'grammar': 'грамм.', 'phonetics': 'фонет.',
    '?': '?',
    # not shown, as in English
    'phrase': '', 'text': '', 'phonetic-group': '', 'phoneme': '', 'phonetic-rule': '',
}

# ------------------------------------------------------------------ inflection forms, variants, classes
PERSON = {'1st': '1 л.', '2nd': '2 л.', '3rd': '3 л.'}
NUMBER = {'sg': 'ед. ч.', 'pl': 'мн. ч.', 'dual': 'двойств. ч.'}
QUALIFIER = {
    'masc': 'м. р.', 'fem': 'ж. р.', 'neut': 'ср. р.', 'neuter': 'ср. р.',
    'exclusive': 'эксклюз.', 'inclusive': 'инклюз.',
    'polite': 'вежл.', 'familiar': 'фам.', 'honorific': 'почтит.',
    'remote': 'дальн.', 'reflexive': 'возвр.', 'inanimate': 'неодуш.',
}
PREFIXED = {'poss': 'притяж.', 'prep': 'предл.'}


def person_form(parts):
    """1st-pl-exclusive-poss -> 'притяж. 1 л. мн. ч. эксклюз.'; None if not a person form."""
    if not parts or parts[0] not in PERSON or len(parts) < 2 or parts[1] not in NUMBER:
        return None
    prefix = []
    rest = []
    for p in parts[2:]:
        if p in PREFIXED:
            prefix.append(PREFIXED[p])
        elif p in QUALIFIER:
            rest.append(QUALIFIER[p])
        else:
            return None
    return ' '.join(prefix + [PERSON[parts[0]], NUMBER[parts[1]]] + rest)


def composite(code):
    parts = code.split('-')
    label = person_form(parts)
    if label:
        return label
    if parts[0] == 'with' and parts[-1] in ('object', 'dative'):
        inner = parts[1:-1]
        case = 'с объектом' if parts[-1] == 'object' else 'с дательным'
        if inner == ['abstract']:
            return 'с абстрактным объектом'
        label = person_form(inner)
        if label:
            return f'{case} {label}'
        if len(inner) == 1 and inner[0] in NUMBER:
            return f'{case} {NUMBER[inner[0]]}'
        if len(inner) == 1 and inner[0] in QUALIFIER:
            return f'{case} {QUALIFIER[inner[0]]}'
    m = re.fullmatch(r'([a-z]{1,2})-mutation', code)
    if m and m.group(1) not in ('i',):
        return f'{m.group(1)}-мутация'
    m = re.fullmatch(r'draft-(.+)', code)
    if m and m.group(1) in FORMS:
        return f'{FORMS[m.group(1)]} (черновик)'
    return None


FORMS = {
    # number, person-independent
    'singular': 'ед. ч.', 'plural': 'мн. ч.', 'dual': 'двойств. ч.',
    'class-plural': 'собир. мн. ч.', 'partitive-plural': 'партитивное мн. ч.',
    'er-plural': 'мн. ч. на -er', 'irregular-plural': 'неправильное мн. ч.',
    'irregular-dual': 'неправильное двойств. ч.', 'u-dual': 'двойств. ч. на -u',
    'archaic-strong-plural': 'архаичное сильное мн. ч.', 'archaic-strong-dual': 'архаичное сильное двойств. ч.',
    'archaic-dual-with-glide': 'архаичное двойств. ч. с глайдом',
    'plural-with-linking-consonant': 'мн. ч. с соединительным согласным',
    # gender
    'masc': 'м. р.', 'fem': 'ж. р.', 'neut': 'ср. р.', 'common': 'общ. р.', 'gendered': 'с родовым различием',
    # cases
    'nominative': 'именительный', 'genitive': 'родительный', 'dative': 'дательный',
    'accusative': 'винительный', 'instrumental': 'инструменталис', 'locative': 'локатив',
    'allative': 'аллатив', 'ablative': 'аблатив', 'comitative': 'комитатив',
    'similative': 'симулятив', 'possessive': 'посессив', 'partitive': 'партитив',
    'old-genitive': 'старый родительный', 'a-genitive': 'родительный на -a', 'o-genitive': 'родительный на -o',
    'short-locative': 'краткий локатив', 'r-locative': 'локатив на -r',
    'short-instrumental': 'краткий инструменталис', 'long-dative': 'долгий дательный',
    'n-accusative': 'винительный на -n', 'colloquial-possessive': 'разговорный посессив',
    'possessive-second': 'посессив (второй)',
    'subjective': 'субъектная форма', 'objective': 'объектная форма',
    'normal-and-subjective': 'обычная и субъектная форма',
    'present-subjective': 'субъектная форма наст. вр.',
    'irregular-subjective': 'неправильная субъектная форма',
    'archaic-strong-subjective': 'архаичная сильная субъектная форма',
    'archaic-strong-objective': 'архаичная сильная объектная форма',
    'archaic-objective-with-glide': 'архаичная объектная форма с глайдом',
    'objective-with-syncope': 'объектная форма с синкопой',
    'adjective-in-objective': 'прил. в объектной форме',
    # tense, aspect, mood
    'present': 'наст. вр.', 'past': 'прош. вр.', 'future': 'буд. вр.', 'aorist': 'аорист',
    'perfect': 'перфект', 'pluperfect': 'плюсквамперфект', 'imperfect': 'имперфект',
    'future-perfect': 'буд. перфект', 'present-perfect': 'наст. перфект', 'past-perfect': 'прош. перфект',
    'past-future': 'будущее в прошедшем', 'past-future-perfect': 'буд. перфект в прошедшем',
    'future-future': 'будущее в будущем', 'past-imperfect': 'прош. имперфект',
    'present-imperfect': 'наст. имперфект', 'future-imperfect': 'буд. имперфект',
    'long-perfect': 'долгий перфект', 'long-imperfect': 'долгий имперфект',
    'strong-past': 'сильное прош. вр.', 'weak-past': 'слабое прош. вр.',
    'half-strong-past': 'полусильное прош. вр.', 'strong-perfect': 'сильный перфект',
    'weak-perfect': 'слабый перфект', 'reformed-perfect': 'преобразованный перфект',
    'consuetudinal-past': 'прош. вр. обыкновения', 'continuative-past': 'прош. длительное',
    'continuative-present': 'наст. длительное', 'stative': 'статив',
    'stative-past': 'статив прош. вр.', 'stative-future': 'статив буд. вр.',
    'passive': 'страдат. залог', 'passive-past': 'страдат. прош. вр.',
    'imperative': 'повелит. накл.', 'infixed-imperative': 'инфиксальное повелит. накл.',
    'subjunctive': 'сослагат. накл.', 'past-subjunctive': 'сослагат. накл. прош. вр.',
    'conditional': 'условн. накл.',
    'infinitive': 'инфинитив', 'particular-infinitive': 'частный инфинитив', 'gerund': 'герундий',
    'impersonal': 'безличная форма', 'frequentative': 'многократная форма', 'intensive': 'интенсив',
    'negated': 'отрицательная форма', 'negative': 'отрицание',
    'negative-quasi-participle': 'отрицательное квазипричастие',
    # participles
    'active-participle': 'действ. причастие', 'passive-participle': 'страдат. причастие',
    'past-active-participle': 'действ. причастие прош. вр.',
    'imperfect-participle': 'причастие имперфекта', 'imperfect-passive-participle': 'страдат. причастие имперфекта',
    'perfect-participle': 'причастие перфекта', 'perfect-passive-participle': 'страдат. причастие перфекта',
    'perfective-participle': 'причастие соверш. вида', 'future-participle': 'причастие буд. вр.',
    'future-passive-participle': 'страдат. причастие буд. вр.', 'reflexive-participle': 'возвратное причастие',
    # person forms not covered by the rule
    'reflexive': 'возвратная форма',
    'with-1st-sg-dative': 'с дательным 1 л. ед. ч.',
    'definite': 'определённая форма', 'indefinite': 'неопределённая форма',
    'definite-prep': 'предл. определённая форма', 'definite-plural-prep': 'предл. определённое мн. ч.',
    'no-agreement': 'без согласования', 'adj-agreement': 'согласование прил.',
    'pronoun-prefix': 'местоименный префикс', 'object-suffix-only': 'только объектный суффикс',
    # degree
    'comparative': 'сравнит. степень', 'superlative': 'превосх. степень',
    'diminutive': 'уменьшит. форма', 'diminutive-superlative': 'уменьшит.-превосх. форма',
    'augmentative': 'увеличит. форма',
    # word formation
    'stem': 'основа', 'root': 'корень', 'radical': 'корневая форма', 'affix': 'аффикс',
    'prefix': 'префикс', 'suffix': 'суффикс', 'adjectival': 'адъективная форма',
    'adverbial': 'наречная форма', 'agental': 'имя деятеля', 'agental-formation': 'образование имени деятеля',
    'patronymic': 'патроним', 'extension': 'расширение основы', 'vocalic-extension': 'вокалическое расширение',
    'full-form': 'полная форма', 'complete': 'полная форма', 'shortened': 'сокращённая форма',
    'elided': 'с элизией', 'strengthened': 'усиленная форма', 'assimilated': 'ассимилированная форма',
    'augmentation': 'аугментация', 'augmentless': 'без аугмента', 'inversion': 'инверсия',
    'nasal-infixion': 'носовой инфикс', 'glide-consonant': 'глайд',
    'joining-base-vowel': 'соединительный гласный основы',
    'irregular': 'неправильная форма', 'dialectical': 'диалектная форма', 'draft': 'черновик',
    # sound changes
    'soft-mutation': 'мягкая мутация', 'nasal-mutation': 'носовая мутация',
    'stop-mutation': 'смычная мутация', 'mixed-mutation': 'смешанная мутация',
    'liquid-mutation': 'плавная мутация', 'sibilant-mutation': 'сибилянтная мутация',
    'i-mutation': 'i-умлаут', 'a-fortification': 'a-усиление', 's-fortification': 's-усиление',
    'consonant-doubling': 'удвоение согласного', 'vowel-lengthening': 'удлинение гласного',
    'vowel-suppression': 'выпадение гласного', 'vowel-prefixion': 'префиксация гласного',
    'vowel-suffixion': 'суффиксация гласного', 'prosodic-lengthening': 'просодическое удлинение',
    'subordinate-vowel-variation': 'чередование подчинённого гласного',
    # verb and stem classes
    'class': 'класс', 'basic-verb': 'базовый глагол', 'derived-verb': 'производный глагол',
    'weak-verb': 'слабый глагол', 'irregular-verb': 'неправильный глагол', 'inceptive-verb': 'начинательный глагол',
    'a-verb': 'глагол на -a', 'u-verb': 'глагол на -u',
    'biconsonantal-root': 'двусогласный корень', 'biconsonantal-verb': 'двусогласный глагол',
    'triconsonantal-root': 'трёхсогласный корень', 'triconsonantal-verb': 'трёхсогласный глагол',
    'uniconsonantal-form': 'односогласная форма',
    'ta-formative': 'форматив -ta', 'ya-formative': 'форматив -ya', 'na-formative': 'форматив -na',
    'ta-causative': 'каузатив на -ta', 'ya-causative': 'каузатив на -ya',
    'strong-I': 'сильный I', 'strong-II': 'сильный II', 'weak-I': 'слабый I', 'weak-II': 'слабый II',
    'strong-I-without-syncope': 'сильный I без синкопы', 'talat-stem': 'основа типа talat',
    'declension-B': 'склонение B', 'declension-C': 'склонение C', 'declension-D': 'склонение D',
}

# ------------------------------------------------------------------ longer passages
FRAGMENTS = {
    'language-index-intro': '''<p>На этой странице перечислены языки, вошедшие в лексикон, с разбивкой по периодам.
Внутри каждого периода языки расположены иерархически, по происхождению: дочерние языки идут под более
древними языками, от которых они произошли.</p>
<p>«Сводные», или «нео-», языки собирают слова разных периодов, включая создания поклонников (неологизмы).
Эти «сводные» списки удобнее всего для нового эльфийского письма. Пользоваться ими, однако, стоит осторожно:
в них смешаны слова разных периодов. Период каждого слова указан его пометой языка, кроме того, есть и другие
«<a href="../../general/terminology-and-notations.html#reliability-markers">пометы надёжности</a>», по которым
можно судить о качестве каждого слова.</p>
<p>Остальные языки представлены такими, какими Толкин описывал их в разные периоды жизни: ранний (1910–1930),
средний (1930–1950) и поздний (1950–1973). В них входят только те формы, которые Толкин записал именно в этот
период. Стоит, однако, помнить, что Толкин нередко использовал ранние формы и в поздних работах. Если ранняя
форма не встречается позднее, это ещё не значит, что Толкин перестал считать её верной. Где возможно, лексикон
прослеживает концептуальное развитие отдельных слов в текстах Толкина.</p>''',
}

# ------------------------------------------------------------------ coverage checks
form_tokens = [t for t in json.load(open(tokens_json)) if t]
form_labels = {}
missing_forms = []
for code in form_tokens:
    label = FORMS.get(code) or composite(code)
    if label:
        form_labels[code] = label
    else:
        missing_forms.append(code)
assert not missing_forms, missing_forms

prototype = ['word-page.xq', 'language-page.xq', 'language-index.xq', 'word-index.xq', 'common.xq']
keys = set()
for name in prototype:
    src = open(f'{query_dir}/{name}', encoding='utf-8').read()
    src = re.sub(r'\(:.*?:\)', '', src, flags=re.S)  # comments
    keys |= set(re.findall(r"c:t[fn]?\('((?:[^']|'')*)'", src))
missing = sorted(k for k in keys if k not in MSG and k not in PLURAL)
assert not missing, missing
unused = sorted(k for k in list(MSG) + list(PLURAL) if k not in keys and k != 'Applied Derivational Rules')
print('interface keys used:', len(keys), ' unused catalog entries:', unused)

# ------------------------------------------------------------------ write
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<!--',
       '  Russian interface catalog for Eldamo. See the localization section of common.xq.',
       '  <msg en="..."> keys are the English text of the queries; {1}, {2} are placeholders.',
       '  Inflection, variant and class labels (<form>) are a draft for review.',
       '-->',
       '<messages lang="ru">', '', '  <!-- interface strings -->']
for en, ru in MSG.items():
    out.append(f'  <msg en={quoteattr(en)}>{escape(ru)}</msg>')
for en, forms in PLURAL.items():
    attrs = ' '.join(f'{k}={quoteattr(v)}' for k, v in forms.items())
    out.append(f'  <msg en={quoteattr(en)} {attrs}/>')
out += ['', '  <!-- language names, by language id -->']
for lid, name in LANGUAGES.items():
    out.append(f'  <language id={quoteattr(lid)}>{escape(name)}</language>')
for cid, name in LANGUAGE_CATS_BY_ID.items():
    out.append(f'  <language-cat id={quoteattr(cid)}>{escape(name)}</language-cat>')
for en, name in LANGUAGE_CATS_BY_NAME.items():
    out.append(f'  <language-cat name={quoteattr(en)}>{escape(name)}</language-cat>')
out += ['', '  <!-- parts of speech; an empty label is not shown -->']
for code, label in SPEECH.items():
    out.append(f'  <speech code={quoteattr(code)}>{escape(label)}</speech>')
out += ['', '  <!-- inflection forms, variants and classes -->']
for code in sorted(form_labels):
    out.append(f'  <form code={quoteattr(code)}>{escape(form_labels[code])}</form>')
out += ['', '  <!-- longer passages -->']
for fid, html in FRAGMENTS.items():
    out.append(f'  <fragment id={quoteattr(fid)}>\n{html}\n  </fragment>')
out += ['', '</messages>', '']
open(output, 'w', encoding='utf-8').write('\n'.join(out))
print(f'wrote {output}: {len(MSG) + len(PLURAL)} strings, {len(LANGUAGES)} languages, '
      f'{len(LANGUAGE_CATS_BY_ID) + len(LANGUAGE_CATS_BY_NAME)} language groups, {len(SPEECH)} speech codes, '
      f'{len(form_labels)} forms ({sum(1 for c in form_labels if c not in FORMS)} composed), {len(FRAGMENTS)} fragments')
