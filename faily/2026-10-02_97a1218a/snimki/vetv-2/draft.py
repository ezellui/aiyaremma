"""Заход L1 — черновик новых концепций списка A (N1) и их связей, БЕЗ описаний.
Описания пишутся после утверждения состава автором; тогда из этого черновика собираются файлы правок
L1-concepts.json и L1-add.json (концепции — через add_concepts.mjs, связи — через add_links.mjs).

Поля связи: s, t, type, w (вес), bi (bidirectional, только для несимметричных типов, когда обращались
обе стороны), hwph (место HWPh, если оно утверждает само отношение; иначе отношение — по знанию
составителя), why (одна строка: почему такой тип и вес).
Рефлексивная связь — s == t (самоприменение, самообоснование, противоречие с собой)."""

CONCEPTS = [
 # id, философ (id), метка, рубрики, статьи HWPh
 ('world_soul_plato', 'plato', 'Мировая душа', ['being', 'absolute'], 'Bd. 12, Sp. 516–521, Art. ‹Weltseele›'),
 ('catharsis', 'aristotle', 'Катарсис', ['aesthetics'], 'Bd. 4, Sp. 784–786, Art. ‹Katharsis›'),
 ('non_contradiction', 'aristotle', 'Закон противоречия', ['knowledge', 'being'], 'Bd. 8, Sp. 1202–1205, Art. ‹Satz vom (ausgeschlossenen) Widerspruch›'),
 ('to_ti_en_einai', 'aristotle', 'Суть бытия', ['being'], 'Bd. 10, Sp. 1310–1314, Art. ‹To ti en einai›'),
 ('illumination', 'augustine', 'Озарение', ['knowledge', 'absolute'], 'Bd. 4, Sp. 582f., Art. ‹Irradiatio›; Bd. 8, Sp. 66f., Art. ‹Rationes aeternae›'),
 ('coniectura', 'cusanus', 'Предположение', ['knowledge', 'method'], 'Bd. 1, Sp. 522–524, Art. ‹Ars coniecturalis›'),
 ('complicatio_explicatio', 'cusanus', 'Свёртывание и развёртывание', ['absolute', 'being'], 'Bd. 1, Sp. 1026–1028, Art. ‹Complicatio/explicatio›'),
 ('characteristica_universalis', 'leibniz', 'Всеобщая характеристика', ['language', 'method'], 'Bd. 1, Sp. 984, Art. ‹Characteristica universalis›'),
 ('appetition', 'leibniz', 'Аппетиция', ['will', 'being'], 'Bd. 1, Sp. 456f., Art. ‹Appétition›'),
 ('truths_reason_fact', 'leibniz', 'Истины разума и истины факта', ['knowledge'], 'Bd. 11, Sp. 869–872, Art. ‹Vernunftwahrheiten/Tatsachenwahrheiten›'),
 ('natural_purpose', 'kant', 'Цель природы', ['being', 'knowledge'], 'Bd. 6, Sp. 658f., Art. ‹Naturzweck›'),
 ('intelligible_character', 'kant', 'Эмпирический и умопостигаемый характер', ['freedom', 'ethics'], 'Bd. 2, Sp. 476f., Art. ‹Empirischer/intelligibler Charakter›'),
 ('kingdom_ends', 'kant', 'Царство целей', ['ethics', 'politics'], 'Bd. 8, Sp. 508–510, Art. ‹Reich der Zwecke›'),
 ('system_needs', 'hegel', 'Система потребностей', ['politics', 'ethics'], 'Bd. 1, Sp. 774, Art. ‹Bedürfnisse, System der›'),
 ('unhappy_consciousness', 'hegel', 'Несчастное сознание', ['consciousness', 'absolute'], 'Bd. 1, Sp. 905f., Art. ‹Bewußtsein, unglückliches›'),
 ('unprethinkable_being', 'schelling', 'Непредмыслимое бытие', ['being', 'absolute'], 'Bd. 11, Sp. 339–341, Art. ‹Unvordenkliche, das›'),
 ('objectification_grades', 'schopenhauer', 'Ступени объективации воли', ['will', 'being'], 'Bd. 6, Sp. 1054, Art. ‹Objektität›'),
 ('contemporaneity', 'kierkegaard', 'Одновременность', ['time', 'absolute'], 'Bd. 3, Sp. 674f., Art. ‹Gleichzeitigkeit›'),
 ('forces_relations_production', 'marx', 'Производительные силы и производственные отношения', ['politics', 'dialectics'], 'Bd. 7, Sp. 1438–1442, Art. ‹Produktionsverhältnisse/Produktivkräfte›'),
 ('descriptive_psychology_dilthey', 'dilthey', 'Описательная психология', ['consciousness', 'method'], 'Bd. 7, Sp. 1653–1655, Art. ‹Psychologie, beschreibende und zergliedernde›'),
 ('worldview_types', 'dilthey', 'Типы мировоззрения', ['knowledge'], 'Bd. 4, Sp. 34f., Art. ‹Idealismus der Freiheit›'),
 ('genealogy', 'nietzsche', 'Генеалогия', ['method', 'ethics'], 'Bd. 3, Sp. 268f., Art. ‹Genealogie›'),
 ('revaluation_values', 'nietzsche', 'Переоценка всех ценностей', ['ethics'], 'Bd. 11, Sp. 105–108, Art. ‹Umwertung aller Werte›'),
 ('primary_secondary_process', 'freud', 'Первичный и вторичный процессы', ['consciousness', 'will'], 'Bd. 9, Sp. 289–291, Art. ‹Sekundärvorgang›; Bd. 7, Sp. 1311–1314, Art. ‹Primärvorgang›'),
 ('meaning_fulfillment', 'husserl', 'Интенция значения и её исполнение', ['consciousness', 'knowledge'], 'Bd. 1, Sp. 759f., Art. ‹Bedeutungserfüllung›; Sp. 760, Art. ‹Bedeutungsintention›; Bd. 5, Sp. 160, Art. ‹Leerintention›'),
 ('categorial_intuition', 'husserl', 'Категориальное созерцание', ['knowledge', 'consciousness'], 'Bd. 1, Sp. 351, Art. ‹Anschauung, kategoriale›'),
 ('time_consciousness', 'husserl', 'Внутреннее сознание времени', ['time', 'consciousness'], 'Bd. 7, Sp. 1529, Art. ‹Protention›; Bd. 3, Sp. 138–140, Art. ‹Gegenwart, lebendige›; Bd. 8, Sp. 931f., Art. ‹Retention›; Bd. 11, Sp. 363f., Art. ‹Urimpression›'),
 ('type_theory', 'russell', 'Теория типов', ['knowledge', 'language'], 'Bd. 10, Sp. 1583–1586, Art. ‹Typentheorie; Typenlogik›'),
 ('three_kinds_knowledge', 'scheler', 'Три вида знания', ['knowledge'], 'Bd. 1, Sp. 938f., Art. ‹Bildungswissen›; Bd. 2, Sp. 719f., Art. ‹Erlösungswissen›; Bd. 3, Sp. 1099f., Art. ‹Herrschaftswissen›; Bd. 5, Sp. 224, Art. ‹Leistungswissen›'),
 ('forms_spirit', 'hartmann', 'Формы духовного бытия', ['being', 'consciousness'], 'Bd. 3, Sp. 206f., Art. ‹Geist, objektivierter›; Sp. 216f., Art. ‹Geistiges Sein›'),
 ('befindlichkeit', 'heidegger', 'Расположенность', ['being', 'consciousness'], 'Bd. 1, Sp. 775, Art. ‹Befindlichkeit›'),
 ('authenticity', 'heidegger', 'Подлинность и неподлинность', ['being', 'freedom'], 'Bd. 2, Sp. 339, Art. ‹Eigentlichkeit/Uneigentlichkeit›'),
 ('history_being', 'heidegger', 'История бытия и забвение бытия', ['being', 'time'], 'Bd. 9, Sp. 258–260, Art. ‹Seinsgeschichte›; Sp. 264f., Art. ‹Seinsvergessenheit›'),
 ('ontological_difference', 'heidegger', 'Онтологическое различие', ['being'], 'Bd. 2, Sp. 236f., Art. ‹Differenz, ontologische›'),
 ('confirmation', 'carnap', 'Подтверждение', ['knowledge', 'method'], 'Bd. 1, Sp. 850, Art. ‹Bestätigung›; Sp. 863, Art. ‹Bewährung›; Bd. 4, Sp. 946f., Art. ‹Konfirmierbar›; Bd. 7, Sp. 1565, Art. ‹Prüfbar›'),
 ('physicalism', 'carnap', 'Физикализм и единство науки', ['knowledge', 'language'], 'Bd. 2, Sp. 400, Art. ‹Einheit der Wissenschaft›; Bd. 7, Sp. 947f., Art. ‹Physikalismus›'),
]

def L(s, t, type, w, why, hwph=None, bi=False):
    return dict(s=s, t=t, type=type, w=w, why=why, **({'hwph': hwph} if hwph else {}), **({'bi': True} if bi else {}))

LINKS = [
 # --- Платон: Мировая душа
 L('world_soul_plato', 'demiurge', 'emerge_from', 2, 'душа космоса устроена демиургом из тождественного, иного и сущности'),
 L('world_soul_plato', 'ideas', 'mediate', 2, 'через душу мира умопостигаемый образец доходит до телесного космоса'),
 L('harmony_spheres', 'world_soul_plato', 'influence', 2, 'душа мира в «Тимее» расчленена по гармоническим отношениям — пифагорейское наследие'),
 L('world_soul_plato', 'world_soul', 'develop', 3, 'Плотин подхватывает понятие под тем же именем: душа мира — «сестра» отдельных душ, отличная от Души-ипостаси', 'Bd. 12, Sp. 517 (Art. ‹Weltseele›)'),
 L('world_soul_plato', 'naturphilosophie', 'influence', 2, 'Шеллинг ссылается на «понятие древних о мировой душе» для начала, связующего неорганическую и органическую природу («Von der Weltseele», 1798)', 'Bd. 12, Sp. 519 (Art. ‹Weltseele›)'),
 # --- Аристотель: Катарсис
 L('catharsis', 'golden_mean', 'instrument', 1, 'очищение сострадания и страха возвращает аффекты к мере — побочная связь поэтики с этикой'),
 L('catharsis', 'mimesis', 'critique', 3, 'определение действия трагедии направлено прежде всего против Платона, видевшего в поэзии угрозу равновесию души', 'Bd. 4, Sp. 785 (Art. ‹Katharsis›)'),
 L('dionysian', 'catharsis', 'critique', 2, 'Ницше отвергает чтение трагедии как разрядки сострадания и страха («Рождение трагедии» § 22; «Сумерки идолов»)'),
 L('catharsis', 'repression', 'influence', 1, '«катартический метод» Брейера и Фрейда назван по Аристотелю (через Я. Бернайса); из него вырастает учение о вытеснении', 'Bd. 5, Art. ‹Methode, kathartische›; Art. ‹Läuterung, Reinigung›'),
 # --- Аристотель: Закон противоречия
 L('non_contradiction', 'logos', 'condition', 3, 'начало, без которого речь ничего не обозначает: кто говорит хоть что-то, уже его принял (Met. Γ 4)'),
 L('non_contradiction', 'non_contradiction', 'presuppose', 3, 'доказать начало нельзя — всякое его отрицание уже его предполагает; отсюда опровергающее, а не прямое доказательство'),
 L('non_contradiction', 'truths_reason_fact', 'develop', 2, 'истины разума держатся на «principe de la contradiction» (Monad. § 31)', 'Bd. 8, Sp. 1203f. (Art. ‹Satz vom Widerspruch›); Bd. 11, Sp. 869f.'),
 L('dialectic', 'non_contradiction', 'critique', 2, '«Contradictio est regula veri»: Гегель оспаривает лишь отрицательную, разграничивающую роль закона', 'Bd. 8, Sp. 1205 (Art. ‹Satz vom Widerspruch›)'),
 # --- Аристотель: Суть бытия
 L('to_ti_en_einai', 'form', 'complement', 2, 'форма — начало бытия вещи, суть бытия — то же, взятое как предмет определения (Met. Z 7: эйдос есть τὸ τί ἦν εἶναι)'),
 L('to_ti_en_einai', 'categories', 'presuppose', 2, 'суть бытия в первичном смысле принадлежит сущности — первой из категорий'),
 L('to_ti_en_einai', 'essence_existence', 'influence', 2, 'Фома толкует формулу через «essentia» и «quidditas» — с большим влиянием на всю передачу понятия', 'Bd. 10, Sp. 1311 (Art. ‹To ti en einai›)'),
 L('to_ti_en_einai', 'potencies', 'influence', 1, 'поздний Шеллинг вписывает формулу в учение о потенциях, читая εἶναι как акт', 'Bd. 10, Sp. 1312f. (Art. ‹To ti en einai›)'),
 # --- Августин: Озарение
 L('illumination', 'faith_reason', 'complement', 2, 'разум доходит до истины лишь в свете, который не сам себе дал'),
 L('anamnesis', 'illumination', 'develop', 3, 'Меноново припоминание переосмыслено как видение в вечных основаниях божественного ума', 'Bd. 8, Sp. 66f. (Art. ‹Rationes aeternae›)'),
 L('illumination', 'participatio', 'develop', 2, 'Фома ограничивает озарение действием деятельного ума, но всякое познание истины остаётся «quaedam illuminatio» — причастием божественной истине', 'Bd. 4, Sp. 582f. (Art. ‹Irradiatio›)'),
 L('illumination', 'truths_reason_fact', 'influence', 1, 'вечные истины коренятся в божественном уме — «области идей», которую признал Августин', 'Bd. 11, Sp. 870 (Art. ‹Vernunftwahrheiten/Tatsachenwahrheiten›)'),
 # --- Кузанский: Предположение
 L('docta_ignorantia', 'coniectura', 'consequence', 3, 'раз точная истина недоступна, всякое положительное знание — предположение; «Об учёном незнании» продолжено «О предположениях»'),
 L('coniectura', 'enigma_cusanus', 'complement', 1, 'предположение и загадка — два способа причастности истине в инаковости'),
 L('coniectura', 'conjecture_refutation', 'typological', 1, 'всё человеческое знание — предположение; сходство постановки без линии передачи'),
 # --- Кузанский: Свёртывание и развёртывание
 L('complicatio_explicatio', 'coincidentia_oppositorum', 'presuppose', 2, 'свёрнутость всего в Боге есть совпадение противоположностей'),
 L('contraction', 'complicatio_explicatio', 'mediate', 2, 'стяжение — способ, которым свёрнутое единство развёрнуто в конечных вещах'),
 L('emanation', 'complicatio_explicatio', 'influence', 2, 'неоплатоническое истечение из Единого переосмыслено как развёртывание свёрнутого'),
 L('foreknowledge_freedom', 'complicatio_explicatio', 'influence', 1, 'шартрские комментаторы Боэция соотносят «свёртывание» с провидением, «развёртывание» с роком (Consolatio IV, pr. 6)', 'Bd. 1, Sp. 1026f. (Art. ‹Complicatio/explicatio›)'),
 L('complicatio_explicatio', 'fold', 'influence', 2, 'Делёз прямо опирается на пару complicatio/explicatio (Кузанский, Бруно) в понятии складки и выражения'),
 # --- Лейбниц: Всеобщая характеристика
 L('characteristica_universalis', 'truths_reason_fact', 'instrument', 2, 'исчисление понятий должно сводить истины разума к тождествам счётом'),
 L('characteristica_universalis', 'begriffsschrift', 'develop', 3, 'Фреге сознательно примыкает к лейбницеву замыслу философского всеобщего языка — но без определительного построения всей системы понятий', 'Bd. 2, Art. ‹Denken›; Bd. 1, Art. ‹Begriffsschrift›'),
 # --- Лейбниц: Аппетиция
 L('appetition', 'perception_monad', 'complement', 3, 'два основных свойства монады: восприятие и стремление к переходу от восприятия к восприятию'),
 L('monads', 'appetition', 'consequence', 2, 'монада без окон меняется только изнутри — отсюда внутреннее начало изменения'),
 L('conatus_hobbes', 'appetition', 'influence', 1, 'ранний Лейбниц перенимает у Гоббса conatus — начальное усилие'),
 L('appetition', 'concrescence', 'influence', 1, 'Уайтхед берёт слово «appetition» для понятийного стремления актуальной единичности'),
 # --- Лейбниц: Истины разума и истины факта
 L('truths_reason_fact', 'sufficient_reason', 'presuppose', 3, 'истины факта держатся на достаточном основании, истины разума — на законе противоречия'),
 L('truths_reason_fact', 'possible_worlds', 'presuppose', 2, 'необходимое истинно во всех возможных мирах, случайное — лишь в избранном'),
 L('synthetic_apriori', 'truths_reason_fact', 'critique', 3, 'Кант требует признать третий род — синтетические знания a priori — сверх двух лейбницевых', 'Bd. 11, Sp. 871f. (Art. ‹Vernunftwahrheiten/Tatsachenwahrheiten›)'),
 L('truths_reason_fact', 'causality_critique', 'typological', 2, 'юмово деление «relations of ideas» / «matters of fact» повторяет лейбницево; прямое заимствование не доказано', 'Bd. 11, Sp. 871f.'),
 L('necessary_aposteriori', 'truths_reason_fact', 'critique', 2, 'Крипке разводит необходимое и априорное, которые деление на истины разума и факта совмещало', 'Bd. 6, Art. ‹Notwendigkeit›; Bd. 4, Art. ‹Kontingenz›'),
 # --- Кант: Цель природы
 L('natural_purpose', 'aesthetic_judgment', 'complement', 2, 'две ветви рефлектирующей способности суждения в третьей «Критике»'),
 L('natural_purpose', 'antinomies', 'exemplify', 1, 'антиномия телеологической способности суждения: механизм и цель'),
 L('natural_purpose', 'naturphilosophie', 'develop', 2, 'организм, у Канта лишь регулятивная мысль, становится у Шеллинга началом самой природы', 'Bd. 2, Art. ‹Eine (das), Einheit›'),
 # --- Кант: Эмпирический и умопостигаемый характер
 L('intelligible_character', 'thing_itself', 'presuppose', 3, 'один поступок обусловлен как явление и свободен как действие вещи в себе'),
 L('intelligible_character', 'antinomies', 'emerge_from', 2, 'пара возникает как разрешение третьей антиномии'),
 L('intelligible_character', 'will_schop', 'develop', 3, 'Шопенгауэр перенимает пару: умопостигаемый характер — воля как вещь в себе в индивиде; прибавляет «приобретённый характер»', 'Bd. 2, Sp. 476f. (Art. ‹Empirischer/intelligibler Charakter›)'),
 # --- Кант: Царство целей
 L('kingdom_ends', 'autonomy', 'presuppose', 3, 'автономия — самозаконодательство отдельного, царство целей — то же для общности', 'Bd. 8, Sp. 508f. (Art. ‹Reich der Zwecke›)'),
 L('kingdom_ends', 'categorical', 'exemplify', 2, 'третья формула нравственного закона'),
 L('best_worlds', 'kingdom_ends', 'influence', 2, 'лейбницево «царство благодати» как моральный мир — прямо названный источник', 'Bd. 8, Sp. 509 (Art. ‹Reich der Zwecke›)'),
 L('two_cities', 'kingdom_ends', 'influence', 1, 'богословский топос града Божия, с которым понятие связано', 'Bd. 8, Sp. 509'),
 # --- Гегель: Система потребностей
 L('system_needs', 'sittlichkeit', 'mediate', 2, 'гражданское общество — средняя ступень нравственности между семьёй и государством'),
 L('system_needs', 'cunning_reason', 'exemplify', 1, 'частные цели, преследуя себя, создают всеобщую связь'),
 L('forces_relations_production', 'system_needs', 'critique', 2, 'для Маркса система потребностей коренится не в желаниях потребителей, а в организации производства', 'Bd. 1, Sp. 774 (Art. ‹Bedürfnisse, System der›)'),
 # --- Гегель: Несчастное сознание
 L('unhappy_consciousness', 'master_slave', 'emerge_from', 2, 'стоицизм, скепсис и несчастное сознание следуют в «Феноменологии» за господством и рабством'),
 L('unhappy_consciousness', 'religious_alienation', 'influence', 2, 'фейербахова критика религии по сути применяет фигуру несчастного сознания', 'Bd. 1, Sp. 906 (Art. ‹Bewußtsein, unglückliches›)'),
 L('unhappy_consciousness', 'despair', 'influence', 1, '«Несчастнейший» в «Или — или» — отдалённая реминисценция', 'Bd. 1, Sp. 906'),
 # --- Шеллинг: Непредмыслимое бытие
 L('philosophy_revelation', 'unprethinkable_being', 'presuppose', 3, 'положительная философия исходит из бытия, которое прежде всякой мысли', 'Bd. 11, Sp. 339f. (Art. ‹Unvordenkliche, das›)'),
 L('unprethinkable_being', 'potencies', 'condition', 2, 'потенции развёртываются из непредмыслимого бытия как его возможности'),
 L('chora', 'unprethinkable_being', 'influence', 1, 'Шеллинг ссылается на платоновскую хору как «предсуществование» беспорядочного начала', 'Bd. 11, Sp. 340 (Art. ‹Unvordenkliche, das›)'),
 # --- Шопенгауэр: Ступени объективации
 L('objectification_grades', 'will_schop', 'presuppose', 3, 'ступени — ступени объективации единой воли'),
 L('aesthetics_schop', 'objectification_grades', 'presuppose', 2, 'созерцание схватывает неизменные ступени — идеи'),
 L('eidos', 'objectification_grades', 'develop', 2, 'неизменные ступени объективации названы платоновскими идеями'),
 # --- Кьеркегор: Одновременность
 L('contemporaneity', 'moment', 'presuppose', 3, 'ученик одновременен Богу во времени в мгновении («Философские крохи»)'),
 L('contemporaneity', 'weltgeist', 'critique', 2, 'понятие полемически обращено против гегелевского опосредования веры историей', 'Bd. 3, Sp. 675 (Art. ‹Gleichzeitigkeit›)'),
 # --- Маркс: Производительные силы и производственные отношения
 L('historical_materialism', 'forces_relations_production', 'presuppose', 3, 'смена способов производства объясняется противоречием сил и отношений'),
 L('base_superstructure', 'forces_relations_production', 'presuppose', 2, 'базис — совокупность производственных отношений, соответствующих ступени сил'),
 L('forces_relations_production', 'class_struggle', 'consequence', 2, 'противоречие сил и отношений выступает борьбой классов'),
 # --- Дильтей: Описательная психология
 L('descriptive_psychology_dilthey', 'geisteswissenschaften', 'condition', 3, 'психологическое основание наук о духе', 'Bd. 7, Sp. 1654 (Art. ‹Psychologie, beschreibende und zergliedernde›)'),
 L('descriptive_psychology_dilthey', 'erlebnis', 'presuppose', 2, 'исходит из непосредственно пережитой целостности душевной жизни'),
 L('descriptive_psychology_dilthey', 'descriptive_psychology', 'typological', 2, 'описательная психология против объясняющей — у обоих в те же годы', 'Bd. 7, Sp. 478f. (Art. ‹Phänomen›); Sp. 1654f.'),
 # --- Дильтей: Типы мировоззрения
 L('worldview_types', 'leben_dilthey', 'emerge_from', 2, 'три типа — три возможности жизненного поведения, заложенные в психической структуре', 'Bd. 4, Sp. 34 (Art. ‹Idealismus der Freiheit›)'),
 L('historical_reason', 'worldview_types', 'consequence', 2, 'историческое сознание открывает неустранимость нескольких типов систем'),
 # --- Ницше: Генеалогия
 L('genealogy', 'will_power', 'presuppose', 2, 'ценность выводится из воли, которая её полагает'),
 L('genealogy', 'revaluation_values', 'instrument', 2, 'разоблачение происхождения ценностей готовит их переоценку'),
 L('genealogy', 'power_knowledge', 'develop', 2, 'Фуко подхватывает генеалогию как метод («Ницше, генеалогия, история», 1971)'),
 L('genealogy', 'id_ego_superego', 'typological', 1, 'вывод совести из обращённого внутрь влечения предвосхищает намерения Фрейда', 'Bd. 3, Sp. 268f. (Art. ‹Genealogie›)'),
 # --- Ницше: Переоценка всех ценностей
 L('revaluation_values', 'god_dead', 'presuppose', 2, 'переоценка — ответ на обесценение высших ценностей'),
 L('revaluation_values', 'ubermensch', 'condition', 2, 'переоценка должна сделать возможным сверхчеловека', 'Bd. 11, Sp. 107 (Art. ‹Umwertung aller Werte›)'),
 L('slave_morality', 'revaluation_values', 'exemplify', 2, 'восстание рабов в морали — первая, историческая переоценка', 'Bd. 11, Sp. 107'),
 L('conatus', 'revaluation_values', 'influence', 2, 'Спиноза, признанный «предшественник», сохраняет слова «добро» и «зло», но переопределяет их через самосохранение', 'Bd. 11, Sp. 106f. (Art. ‹Umwertung aller Werte›)'),
 # --- Фрейд: Первичный и вторичный процессы
 L('primary_secondary_process', 'pleasure_principle', 'presuppose', 2, 'первичный процесс подчинён принципу удовольствия'),
 L('primary_secondary_process', 'reality_principle', 'presuppose', 2, 'вторичный процесс — принципу реальности'),
 L('dream_work', 'primary_secondary_process', 'exemplify', 3, 'сгущение и смещение в сновидении — образец первичного процесса'),
 # --- Гуссерль: Интенция значения и её исполнение
 L('meaning_fulfillment', 'intentionality', 'presuppose', 3, 'пустое подразумевание и наполняющее созерцание — два вида интенции'),
 L('meaning_fulfillment', 'evidence', 'condition', 3, 'очевидность есть переживание совпадения подразумеваемого и данного'),
 L('differance', 'meaning_fulfillment', 'critique', 3, 'Деррида разбирает гуссерлево учение о значении: смысл не может держаться в одиноком присутствии («Голос и феномен»)', 'Bd. 10, Art. ‹Subjekt›'),
 # --- Гуссерль: Категориальное созерцание
 L('categorial_intuition', 'meaning_fulfillment', 'presuppose', 2, 'категориальные формы («есть», «и») тоже исполняются созерцанием'),
 L('categorial_intuition', 'eidetic', 'complement', 2, 'два расширения созерцания за пределы чувственного'),
 L('categorial_intuition', 'sein', 'influence', 3, 'по свидетельству самого Хайдеггера, отсюда он получил почву для вопроса о бытии'),
 L('categorial_intuition', 'apriori', 'critique', 2, 'созерцание не ограничено чувственностью — против кантовского разделения созерцания и рассудка'),
 # --- Гуссерль: Внутреннее сознание времени
 L('time_consciousness', 'constitution', 'condition', 3, 'самый глубокий слой конституирования — первовпечатление, ретенция, протенция', 'Bd. 11, Sp. 363f. (Art. ‹Urimpression›)'),
 L('time_consciousness', 'intentionality', 'presuppose', 2, 'ретенция и протенция — несводимые основные виды интенциональности', 'Bd. 8, Sp. 931f. (Art. ‹Retention›)'),
 L('time_augustine', 'time_consciousness', 'influence', 2, 'Гуссерль начинает лекции о времени с Августина и следует его связи ожидания и «напряжения»', 'Bd. 9, Art. ‹Spannung›'),
 L('time_consciousness', 'duree', 'typological', 1, 'непрерывность живого настоящего и длительность — независимо и в те же годы'),
 L('trace_derrida', 'time_consciousness', 'critique', 2, 'ретенция уже вносит неприсутствие в живое настоящее — присутствие не первично'),
 # --- Рассел: Теория типов
 L('type_theory', 'russell_paradox', 'emerge_from', 3, 'построена для разрешения антиномии', 'Bd. 10, Sp. 1583 (Art. ‹Typentheorie›)'),
 L('showing_saying', 'type_theory', 'critique', 2, 'по «Трактату» (3.331–3.333) теория типов пытается сказать то, что должно показываться, — парадокс исчезает сам'),
 L('type_theory', 'category_mistake', 'influence', 2, 'категории Райла — логические типы, перенесённые на обыденный язык', 'Bd. 4, Art. ‹Kategorienfehler›'),
 # --- Шелер: Три вида знания
 L('three_kinds_knowledge', 'person_scheler', 'presuppose', 2, 'образовательное знание — среда раскрытия личности', 'Bd. 1, Sp. 938f. (Art. ‹Bildungswissen›)'),
 L('three_kinds_knowledge', 'value_hierarchy', 'presuppose', 2, 'порядок видов знания следует порядку ценностей — от полезного к святому'),
 L('three_kinds_knowledge', 'three_stages', 'critique', 3, 'против закона трёх стадий: религиозное, метафизическое и позитивное знание равноисходны', 'Bd. 2, Sp. 719f. (Art. ‹Erlösungswissen›); Bd. 3, Sp. 1100'),
 L('three_kinds_knowledge', 'knowledge_interest', 'typological', 2, 'три вида знания и три познавательных интереса'),
 # --- Гартман: Формы духовного бытия
 L('forms_spirit', 'layers_being', 'presuppose', 3, 'дух — высший слой, несомый низшими'),
 L('forms_spirit', 'strength_height', 'exemplify', 2, 'дух зависим от низших слоёв и всё же свободен над ними'),
 L('objective_spirit', 'forms_spirit', 'develop', 3, 'объективный дух переработан «в гегелевском ключе», к нему прибавлен объективированный', 'Bd. 4, Art. ‹Kunst, Kunstwerk›; Bd. 3, Art. ‹Geist›'),
 L('forms_spirit', 'third_world', 'typological', 2, 'объективированный дух и мир объективного содержания мысли'),
 # --- Хайдеггер: Расположенность
 L('dasein', 'befindlichkeit', 'presuppose', 2, '«Dasein als Befindlichkeit»: экзистенциал наравне с пониманием и речью', 'Bd. 1, Sp. 775 (Art. ‹Befindlichkeit›); Bd. 9, Art. ‹Sprache›'),
 L('befindlichkeit', 'geworfenheit', 'condition', 2, 'в настроении раскрыта брошенность'),
 L('anxiety', 'befindlichkeit', 'influence', 3, 'кьеркегорова тревога становится основным расположением (SuZ § 40)', 'Bd. 1, Art. ‹Angst, Furcht›'),
 # --- Хайдеггер: Подлинность и неподлинность
 L('sein_zum_tode', 'authenticity', 'condition', 3, 'подлинное бытие к смерти — условие подлинной самости'),
 L('das_man', 'authenticity', 'exemplify', 2, 'растворённость в Man — модус неподлинности'),
 L('individual', 'authenticity', 'develop', 2, 'кьеркегоров единичный против толпы переосмыслен нетеологически: решимость не отрывает Dasein от мира', 'Bd. 2, Art. ‹Entscheidung›'),
 L('authenticity', 'bad_faith', 'influence', 2, 'дурная вера у Сартра — переработка неподлинности', 'Bd. 5, Art. ‹Man›'),
 # --- Хайдеггер: История бытия и забвение бытия
 L('history_being', 'aletheia', 'presuppose', 2, 'история бытия — история самоутаивания его истины', 'Bd. 9, Sp. 258–260 (Art. ‹Seinsgeschichte›)'),
 L('history_being', 'kehre', 'emerge_from', 2, 'название позднее, но подготовлено ходом к повороту', 'Bd. 9, Sp. 258'),
 L('history_being', 'will_power', 'critique', 2, 'воля к власти как переворачивание платонизма — конец метафизики и завершённый нигилизм', 'Bd. 9, Sp. 259 (Art. ‹Seinsgeschichte›)'),
 # --- Хайдеггер: Онтологическое различие
 L('ontological_difference', 'sein', 'presuppose', 3, 'бытие — не сущее: различие держится на самом вопросе о бытии'),
 L('history_being', 'ontological_difference', 'presuppose', 2, 'в двоякости бытия и сущего — сама возможность истории бытия', 'Bd. 9, Sp. 258f.'),
 L('ontological_difference', 'differance', 'develop', 2, 'différance названа «старше» онтологического различия — Деррида подхватывает и смещает его'),
 # --- Карнап: Подтверждение
 L('verification_principle', 'confirmation', 'develop', 3, 'понятие подтверждения введено вместо верификации', 'Bd. 1, Sp. 850 (Art. ‹Bestätigung›); Bd. 7, Sp. 1565'),
 L('conjecture_refutation', 'confirmation', 'critique', 3, 'метод предположений и опровержений поставлен на место «гипотезы и индуктивного подтверждения»', 'Bd. 11, Art. ‹Vermutung›; Bd. 4, Sp. 946f.'),
 L('induction', 'confirmation', 'influence', 1, 'индуктивная логика на вероятности-1 — по замыслу Карнапа, та логика индукции, которой искал Бэкон', 'Bd. 4, Sp. 330 (Art. ‹Induktion›)'),
 # --- Карнап: Физикализм и единство науки
 L('physicalism', 'protocol_sentences', 'presuppose', 2, 'спор о протокольных предложениях — спор о физикалистском языке'),
 L('construction_world', 'physicalism', 'develop', 2, 'феноменалистский базис «Построения» сменён физикалистским'),
]
