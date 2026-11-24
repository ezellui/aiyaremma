#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Патч страницы Eldarische Sammlung:
1) правильная восьмилучевая звезда (Фёанора) вместо квадрат+ромб;
2) тег <img> в каждую плитку (с откатом к заглушке при отсутствии файла);
3) полный перекомпонованный каталог из 28 экспонатов по 6 регистрам."""
import io

P = '/home/claude/eldarische_sammlung.html'
src = io.open(P, encoding='utf-8').read()

def one(old, new):
    global src
    assert src.count(old) == 1, f'ожидалось 1 вхождение, найдено {src.count(old)}: {old[:60]!r}'
    src = src.replace(old, new, 1)

# --- 1. ЗВЕЗДА: восьмилучевая лучевая звезда вместо двух наложенных квадратов ---
one(
'''  <symbol id="star" viewBox="0 0 100 100">
    <rect x="30" y="30" width="40" height="40"/>
    <rect x="30" y="30" width="40" height="40" transform="rotate(45 50 50)"/>
  </symbol>''',
'''  <symbol id="star" viewBox="0 0 100 100">
    <path d="M50 2 L55.7 36.1 L83.9 16.1 L63.9 44.3 L98 50 L63.9 55.7 L83.9 83.9 L55.7 63.9 L50 98 L44.3 63.9 L16.1 83.9 L36.1 55.7 L2 50 L36.1 44.3 L16.1 16.1 L44.3 36.1 Z"/>
  </symbol>''')

# --- 2. CSS: overflow на плитке, стили .pimg, .grp; читаемость бейджа поверх фото ---
one(
'''.plate{position:relative;aspect-ratio:4/3;background:
  repeating-linear-gradient(135deg,#edeeec 0 9px,#eaebe9 9px 18px);
  border:1px solid var(--silver);display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;padding:14px}''',
'''.plate{position:relative;overflow:hidden;aspect-ratio:4/3;background:
  repeating-linear-gradient(135deg,#edeeec 0 9px,#eaebe9 9px 18px);
  border:1px solid var(--silver);display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;padding:14px}
.pimg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;z-index:1}''')

one(
'''.plate .pinv{position:absolute;top:9px;left:10px;font:600 11px/1 ui-monospace,Consolas,monospace;
  letter-spacing:.04em;color:var(--oxblood)}''',
'''.plate .pinv{position:absolute;top:9px;left:10px;z-index:2;font:600 11px/1 ui-monospace,Consolas,monospace;
  letter-spacing:.04em;color:var(--oxblood);text-shadow:0 1px 2px rgba(244,244,242,.7)}''')

one(
'''.plate .plink{position:absolute;bottom:9px;left:0;right:0;font-size:11.5px;letter-spacing:.03em}''',
'''.plate .plink{position:absolute;bottom:9px;left:0;right:0;z-index:2;font-size:11.5px;letter-spacing:.03em;text-shadow:0 1px 2px rgba(244,244,242,.7)}
.grp{display:flex;align-items:center;gap:.5em;margin:42px 0 6px;padding-top:18px;border-top:2px solid var(--steel);
  font:600 13px/1.3 -apple-system,"Segoe UI",sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--steel-dk)}
.grp .ic-star{font-size:12px;color:var(--steel);flex:none}'''
)

# ----------------------------------------------------------------------------
# Генератор плиток
def esc(s): return s
def tile(inv, tru, tde, date, desc_ru, desc_de, prov_ru, prov_de,
         orig=None, orig_n=None, note=None):
    slug = inv.lower().replace(' ', '-')
    inv_nb = inv.replace('-', '&#8209;')
    orig_block = ''
    if orig:
        on = ''
        if orig_n:
            on = ('\n          <span class="orig-n"><span lang="ru">%s</span>'
                  '<span lang="de">%s</span></span>' % orig_n)
        orig_block = (
'''        <div class="orig">
          <span class="orig-k"><span lang="ru">Подлинная надпись</span><span lang="de">Originaltext</span></span>
          <p class="orig-t">%s</p>%s
        </div>
''' % (orig, on))
    note_block = ''
    if note:
        note_block = ('        <p class="note"><span lang="ru">%s</span><span lang="de">%s</span></p>\n'
                      % note)
    return (
'''    <article class="item">
      <div class="plate">
        <img class="pimg" src="media/%s.jpg" alt="%s" loading="lazy" onerror="this.style.display='none'">
        <span class="pinv">%s</span>
        <svg class="ic-star"><use href="#star"/></svg>
        <span class="plink"><a href="media/%s.jpg"><span lang="ru">Открыть изображение</span><span lang="de">Abbildung öffnen</span></a></span>
      </div>
      <div class="label">
        <div class="inv"><svg class="ic-star"><use href="#star"/></svg> %s</div>
        <h3 class="serif"><span lang="ru">%s</span><span lang="de">%s</span></h3>
        <div class="date">%s</div>
%s        <p class="desc" lang="ru">%s</p>
        <p class="desc" lang="de">%s</p>
%s        <p class="meta"><span class="meta-k"><span lang="ru">Происхождение:</span><span lang="de">Herkunft:</span></span> <span lang="ru">%s</span><span lang="de">%s</span></p>
      </div>
    </article>
''' % (slug, tru, inv_nb, slug, inv, tru, tde, date, orig_block, desc_ru, desc_de, note_block, prov_ru, prov_de))

def grp(ru, de):
    return ('    <p class="grp"><svg class="ic-star"><use href="#star"/></svg>'
            '<span lang="ru">%s</span><span lang="de">%s</span></p>\n' % (ru, de))

T = []  # сборка каталога

# ===== A. Официальное и репрезентация =====
T.append(grp('Официальное и репрезентация', 'Amtliches und Repräsentation'))
T.append(tile('ES-2074-001', 'Настенная карта «Кривая победа»', 'Wandkarte „Der krumme Sieg“', '2020',
  'Официальное картографическое издание, отражающее миропорядок Урегулирования. Названия даны по-немецки и на квенья. Образец позднего государственного стиля, соединяющего имперскую геральдику с эльфийской орнаментикой; в верхнем картуше — орёл, держащий восьмиконечную звезду.',
  'Amtliche kartographische Ausgabe, die die Weltordnung des Ausgleichs darstellt. Die Benennungen erscheinen deutsch und in Quenya. Ein Beispiel des späten Staatsstils, der imperiale Heraldik mit elbischer Ornamentik verbindet; in der oberen Kartusche der Adler mit achtzackigem Stern.',
  'из оставленных помещений правительственного квартала; поступление 2030-х гг.',
  'aus geräumten Amtsräumen des Regierungsviertels; Zugang in den 2030er Jahren.',
  orig='„Der krumme Sieg — Die Aufteilung der Welt nach dem Zweiten Weltkrieg · um 1948“',
  orig_n=('заголовок фрактурой; титульная строка продублирована тенгваром','Titel in Fraktur; Titelzeile zusätzlich in Tengwar')))
T.append(tile('ES-2076-014', 'Орден Белого Древа', 'Orden des Weißen Baumes', '2010-е / 2010er',
  'Высокая государственная награда. В медальоне — имперский орёл, держащий восьмиконечную звезду Эльдар и ветвь Белого Древа: характерный пример сублимации прежней символики в эльфийскую. Лента в чёрно-оксбладово-серебряных цветах.',
  'Hohe staatliche Auszeichnung. Im Medaillon der Reichsadler, der einen achtzackigen Eldar-Stern und einen Zweig des Weißen Baumes hält — ein bezeichnendes Beispiel der Überführung der früheren Symbolik ins Elbische. Band in Schwarz, Ochsenblutrot und Silber.',
  'антикварный рынок; приобретение 2076 г.', 'Antiquitätenmarkt; Erwerb 2076.',
  orig='„ORDEN DES WEISSEN BAUMES“',
  orig_n=('по краю медальона — круговая надпись тенгваром','am Rand des Medaillons eine umlaufende Tengwar-Inschrift')))
T.append(tile('ES-2077-040', 'Банкнота 50 рейхсмарок с портретом Толкина', '50-Reichsmark-Schein mit dem Bildnis Tolkiens', '2010-е / 2010er',
  'Денежный знак с гравированным портретом Дж. Р. Р. Толкина и подписью «Вернувший Речь»; номинал продублирован тенгваром. Помещение писателя, презиравшего режим, на государственные деньги — характерный пример его посмертного присвоения.',
  'Ein Geldschein mit dem gestochenen Bildnis J. R. R. Tolkiens und der Beischrift „der Wiederbringer der Sprache“; der Nennwert ist in Tengwar wiederholt. Die Setzung des Schriftstellers, der das Regime verachtete, auf das Staatsgeld ist ein bezeichnendes Beispiel seiner postumen Vereinnahmung.',
  'антикварный рынок.', 'Antiquitätenmarkt.',
  orig='„REICHSMARK · 50 · J. R. R. Tolkien — Der Wiederbringer der Sprache“',
  orig_n=('лицевая и оборотная стороны; номинал тенгваром','Vorder- und Rückseite; Nennwert in Tengwar')))
T.append(tile('ES-2080-119', 'Афиша рейхского фильма «Die Rückkehr der Hohen»', 'Filmplakat des Reichsfilms „Die Rückkehr der Hohen“', '2010-е / 2010er',
  'Лобби-кард государственной кинокартины об «эльфийском» прошлом, в монументальном стиле. В отличие от японской афиши (ES-2085-026), это собственное, славящее кино самого режима.',
  'Eine Aushangkarte eines staatlichen Films über die „elbische“ Vorzeit, im monumentalen Stil. Anders als das japanische Plakat (ES-2085-026) ist dies der eigene, verherrlichende Film des Regimes selbst.',
  'из киноархива.', 'aus einem Filmarchiv.',
  orig='„DIE RÜCKKEHR DER HOHEN · Ein Film des Reiches · UFA“'))
T.append(tile('ES-2078-310', 'Псевдофилологическая статья «Об эльдарско-арийском языковом родстве»', 'Pseudophilologischer Aufsatz „Über die eldarisch-arische Sprachverwandtschaft“', '1990-е–2000-е / 1990er–2000er',
  'Научная по виду статья из рейхского журнала, «доказывающая» происхождение квенья из общего арийского праязыка. Образец идеологической псевдонауки, академически оформлявшей присвоение Толкина.',
  'Ein wissenschaftlich aufgemachter Aufsatz aus einer Reichszeitschrift, der die Herkunft des Quenya aus einer gemeinsamen arischen Ursprache „nachweist“. Ein Beispiel ideologischer Pseudowissenschaft, die die Vereinnahmung Tolkiens akademisch verbrämte.',
  'библиотека института.', 'Institutsbibliothek.',
  orig='„Zeitschrift für arische Sprachforschung — Quenya als Urerbe“',
  note=('Тезис несостоятелен: квенья построен Толкином на финской и латинской основе, что прямо противоречит заявленному «арийскому» родству.',
        'Die These ist haltlos: Tolkien bildete das Quenya auf finnischer und lateinischer Grundlage — im direkten Widerspruch zur behaupteten „arischen“ Verwandtschaft.')))
T.append(tile('ES-2079-188', 'Газетная полоса «Die Heimkehr der Hohen Sprache»', 'Zeitungsseite „Die Heimkehr der Hohen Sprache“', '2005',
  'Передовица официальной газеты Рейха, торжественно представляющая принятие Высокой Речи как священное «возвращение». Внутренний, славящий голос режима — прямая пара к зарубежной передовице о тех же событиях (ES-2080-211).',
  'Leitartikel der amtlichen Zeitung des Reiches, der die Annahme der Hohen Sprache als heilige „Heimkehr“ feiert. Die innere, verherrlichende Stimme des Regimes — unmittelbares Gegenstück zum ausländischen Kommentar über dieselben Ereignisse (ES-2080-211).',
  'из газетного архива (микрофильм).', 'aus einem Zeitungsarchiv (Mikrofilm).',
  orig='„DIE HEIMKEHR DER HOHEN SPRACHE — Völkischer Beobachter, Reichsausgabe, 15. September 2005“',
  note=('Заключительный образ статьи — «как некогда Высокие плыли за море на Запад, навстречу негасимому свету» — воспроизводит, по-видимому неосознанно, ту самую гордыню Низвержения Нуменора, против которой предостерегает легендариум.',
        'Das Schlussbild des Artikels — „wie einst die Hohen über das Meer nach Westen fuhren, dem unvergänglichen Lichte entgegen“ — wiederholt, offenbar unbewusst, eben jene Hybris des Untergangs von Númenor, vor der das Legendarium warnt.')))

# ===== B. Повседневное =====
T.append(grp('Повседневное', 'Alltag'))
T.append(tile('ES-2075-052', 'Паспорт рейхсбюргера с «истинным именем»', 'Reichsbürgerpass mit „wahrem Namen“', '2010-е / 2010er',
  'Удостоверение личности, где наряду с данным именем указано «истинное» эльфийское имя с приставками Tar- и Ar-. Показывает проникновение титулатуры в обыденный документооборот.',
  'Ein Ausweis, der neben dem gegebenen Namen den „wahren“ elbischen Namen mit den Vorsilben Tar- und Ar- führt. Er zeigt das Eindringen der Titulatur in den alltäglichen Schriftverkehr.',
  'передан частным лицом.', 'Übergabe durch eine Privatperson.',
  orig='„Gegebener Name: Heinrich Vogel · Wahrer Name: Tar-Voronwë Ar-Mithlond“',
  note=('Приставки Tar- (квенийская, царей-Верных) и Ar- (адунайская, Людей Короля) в исходном легендариуме принадлежат двум враждебным традициям имянаречения; их соединение в одном имени — устойчивая черта эльдаризированной номенклатуры.',
        'Die Vorsilben Tar- (quenya, der treuen Könige) und Ar- (adûnaisch, der „Königsmenschen“) gehören im zugrunde liegenden Legendarium zwei verfeindeten Namenstraditionen an; ihre Verbindung in einem Namen ist ein durchgängiges Merkmal der eldarisierten Nomenklatur.')))
T.append(tile('ES-2078-077', 'Продовольственная карточка времён «Затмения»', 'Lebensmittelkarte aus der Zeit der „Verdüsterung“', '1980-е / 1980er',
  'Карточка нормированного снабжения с тонко исполненным эльфийским орнаментом и заголовком тенгваром. Сочетание изысканного оформления и скудного содержания — наглядное свидетельство нищеты автаркии за красивым шрифтом.',
  'Eine Bezugskarte für rationierte Lebensmittel mit fein ausgeführter elbischer Ornamentik und einer Kopfzeile in Tengwar. Der Gegensatz von edler Gestaltung und kargem Inhalt bezeugt anschaulich die Armut der Autarkie hinter schöner Schrift.',
  'частное дарение.', 'private Schenkung.',
  orig='„Lebensmittelkarte · Großdeutsches Reich · Brot — Fett — Fleisch“'))
T.append(tile('ES-2081-152', 'Набор оловянных солдатиков «Эльфийские рыцари»', 'Zinnfiguren-Satz „Eldar-Ritter“', '2010-е / 2010er',
  'Детский набор фигурок: «эльфийские рыцари» в стилизованной рейхской форме, со звёздами и Белым Древом. Пример проникновения идеологии в игру и быт детства.',
  'Ein Kinderset von Figuren: „Eldar-Ritter“ in stilisierter Reichsuniform, mit Sternen und Weißem Baum. Ein Beispiel für das Eindringen der Ideologie in das kindliche Spiel und den Alltag.',
  'передано частным лицом.', 'Übergabe durch eine Privatperson.',
  orig='„Eldar-Ritter · Zinnfiguren · Reichsspielwaren“'))
T.append(tile('ES-2082-061', 'Рекламный плакат духов «Silmaril»', 'Werbeplakat des Parfüms „Silmaril“', '2010-е / 2010er',
  'Журнальная реклама духов, названных в честь Сильмарилей. Свидетельство позднего декаданса, когда эльфийские имена сделались товарным знаком роскоши.',
  'Eine Zeitschriftenwerbung für ein nach den Silmaril benanntes Parfüm. Ein Zeugnis des späten Dekadenz, als elbische Namen zum Markenzeichen des Luxus wurden.',
  'из журнального архива.', 'aus einem Zeitschriftenarchiv.',
  orig='„SILMARIL · Das Licht, das man trägt · Reichsparfümerie“'))
T.append(tile('ES-2082-062', 'Флакон духов «Silmaril»', 'Flakon des Parfüms „Silmaril“', '2010-е / 2010er',
  'Стеклянный флакон в форме гранёного камня, к рекламе ES-2082-061. Предмет роскоши, обыгрывающий образ пленённого света.',
  'Ein gläserner Flakon in Form eines geschliffenen Steins, zur Werbung ES-2082-061 gehörig. Ein Luxusgegenstand, der das Bild des gefangenen Lichts aufgreift.',
  'антикварный рынок.', 'Antiquitätenmarkt.',
  orig='„SILMARIL“'))
T.append(tile('2031-447', 'Накладные эльфийские уши', 'Aufsteckbare Elbenohren', '2020-е / 2020er',
  'Силиконовые накладные уши, которые представители верхушки носили на государственных приёмах, придавая себе облик бессмертных эльфов. Предмет поздней декадентской поры; сохранены следы тонального грима.',
  'Aufsteckbare Ohren aus Silikon, die Angehörige der Führungsschicht bei Staatsempfängen trugen, um sich das Aussehen der unsterblichen Elben zu geben. Ein Stück der späten dekadenten Zeit; Spuren von Hautton-Schminke erhalten.',
  'ранее в другом собрании; поступление 2031 г., передано в раздел позднее (сохранён исходный номер).',
  'vormals in anderer Sammlung; Zugang 2031, später an die Abteilung überführt (ursprüngliche Nummer beibehalten).',
  orig='„Ohrprothesen, getragen bei einem Staatsempfang · Großdeutsches Reich, 2020er“',
  orig_n=('текст сопроводительной карточки','Text der Begleitkarte')))

# ===== C. Движение и сопротивление =====
T.append(grp('Движение и сопротивление', 'Bewegung und Widerstand'))
T.append(tile('ES-2078-103', 'Листовка кружка изучения тенгвара', 'Flugblatt eines Tengwar-Lesekreises', '1980-е / 1980er',
  'Размноженная на копире уличная листовка ранней, ещё низовой поры движения, задолго до его официального признания. Свидетельство субкультурного происхождения эльдаризма в годы «Затмения».',
  'Ein fotokopiertes Straßenflugblatt aus der frühen, noch von unten getragenen Zeit der Bewegung, lange vor ihrer amtlichen Anerkennung. Ein Zeugnis der subkulturellen Herkunft des Eldarismus in den Jahren der „Verdüsterung“.',
  'частное дарение из личного архива.', 'private Schenkung aus einem Nachlass.',
  orig='„STUDIENKREIS · DIE HOHE SPRACHE (QUENYA) · Lesekreis für Tengwar · jeden Donnerstag 19 Uhr“'))
T.append(tile('ES-2079-201', 'Самиздатский зин эльдаристов «Sternenvolk» (№ 3)', 'Selbstverlegtes Heft der Eldaristen „Sternenvolk“ (Nr. 3)', '1980-е / 1980er',
  'Обложка и разворот любительского журнала 1980-х со статьёй, смешивающей изучение квенья с расовой мистикой. Документ переходной поры, когда низовое увлечение языком срасталось с идеологией; показывает, что движение «снизу» не было лишь безобидным.',
  'Umschlag und Doppelseite einer Amateurzeitschrift der 1980er Jahre mit einem Artikel, der das Quenya-Studium mit Rassenmystik vermengt. Ein Dokument der Übergangszeit, als die Begeisterung von unten mit der Ideologie verwuchs; es zeigt, dass die Bewegung „von unten“ nicht bloß harmlos war.',
  'из личного архива.', 'aus einem Nachlass.',
  orig='„STERNENVOLK · Heft 3 · Vom Geheimnis der Rassen“'))
T.append(tile('ES-2082-300', 'Подпольная листовка с цитатой из «Аккалабет»', 'Untergrund-Flugblatt mit einem Zitat aus der „Akallabêth“', '2020-е / 2020er',
  'Листовка противников режима, обращающая против власти тот самый сюжет о низвержении Нуменора, который эльдаризм читал как героический образец. Редкий пример «верного прочтения» легендариума, ставшего орудием сопротивления.',
  'Ein Flugblatt von Gegnern des Regimes, das die Erzählung vom Untergang Númenors — die der Eldarismus als heroisches Vorbild las — gegen die Macht wendet. Ein seltenes Beispiel der „richtigen Lesart“ des Legendariums als Mittel des Widerstands.',
  'сохранилось за границей; передано в 2082 г.', 'im Ausland erhalten; Übergabe 2082.',
  orig='„AUCH DIES REICH WIRD SINKEN, WIE NÚMENOR VERSANK“',
  orig_n=('ниже — та же строка тенгваром','darunter dieselbe Zeile in Tengwar')))

# ===== D. Взгляд извне =====
T.append(grp('Взгляд извне', 'Außensicht'))
T.append(tile('ES-2080-211', 'Газетная передовица «Berlin’s Rulers Go Elvish»', 'Zeitungskommentar „Berlin’s Rulers Go Elvish“', '2005',
  'Полоса мнений панамериканской газеты — взгляд извне, с недоумением воспринимающий принятие верхушкой Рейха эльфийских имён на Tar-. Ценна как внешнее свидетельство о том, как «Кривую победу» видели за пределами германской сферы.',
  'Eine Meinungsseite einer panamerikanischen Zeitung — eine Außensicht, die die Annahme elbischer Tar-Namen durch die Führung des Reiches mit Befremden verzeichnet. Wertvoll als Zeugnis von außen über die Wahrnehmung des „krummen Sieges“ jenseits der deutschen Sphäre.',
  'из газетного архива (микрофильм).', 'aus einem Zeitungsarchiv (Mikrofilm).',
  orig='„WHAT’S IN A NAME? BERLIN’S RULERS GO ELVISH — The Washington Herald, 6 October 2005“'))
T.append(tile('ES-2080-260', 'Обложка журнала Time «The Elf Reich»', 'Titelblatt der Zeitschrift Time „The Elf Reich“', '2000-е / 2000er',
  'Обложка панамериканского еженедельника, выносящая эльдаризацию Рейха в заголовок для широкой публики. Показывает, как явление вошло в массовое сознание за пределами германской сферы.',
  'Das Titelblatt eines panamerikanischen Wochenmagazins, das die Eldarisierung des Reiches einem breiten Publikum zur Schlagzeile macht. Es zeigt, wie das Phänomen jenseits der deutschen Sphäre ins allgemeine Bewusstsein trat.',
  'из журнального архива.', 'aus einem Zeitschriftenarchiv.',
  orig='„TIME · THE ELF REICH“'))
T.append(tile('ES-2081-303', 'Разведывательный меморандум об эльдаризме (рассекреченный)', 'Geheimdienst-Memorandum über den Eldarismus (freigegeben)', '2000-е / 2000er',
  'Панамериканский аналитический меморандум, трезво разбирающий политическую пользу эльдаризма для режима. Рассекречен после краха; ценен как холодная внешняя оценка изнутри государственного аппарата.',
  'Ein panamerikanisches Lagepapier, das den politischen Nutzen des Eldarismus für das Regime nüchtern analysiert. Nach dem Untergang freigegeben; wertvoll als kühle Außeneinschätzung aus dem Staatsapparat.',
  'рассекреченный фонд.', 'freigegebener Bestand.',
  orig='„CONFIDENTIAL — The Eldarist Turn in Reich Governance · Office of Strategic Assessment“'))
T.append(tile('ES-2083-015', 'Статья «Правды» «Эльфийский маскарад обречённого Рейха»', 'Prawda-Artikel „Die elbische Maskerade des dem Untergang geweihten Reiches“', '2010-е / 2010er',
  'Советская газетная статья, толкующая эльдаризм как признак исторической обречённости режима. Внешнее, идеологически окрашенное свидетельство — пара к карикатуре из «Крокодила».',
  'Ein sowjetischer Zeitungsartikel, der den Eldarismus als Zeichen der historischen Verlorenheit des Regimes deutet. Ein äußeres, ideologisch gefärbtes Zeugnis — Gegenstück zur Karikatur aus dem „Krokodil“.',
  'газетный архив.', 'Zeitungsarchiv.',
  orig='„ПРАВДА · Эльфийский маскарад обречённого Рейха“'))
T.append(tile('ES-2083-014', 'Карикатура из журнала «Крокодил»', 'Karikatur aus der Zeitschrift „Krokodil“', '2010-е / 2010er',
  'Советская сатирическая карикатура: под эльфийским плащом Рейха виден прежний кованый сапог. Внешний, насмешливый взгляд из соперничающей державы, для которой «молящийся эльфам фашизм» — повод для сатиры.',
  'Eine sowjetische Spottkarikatur: unter dem elbischen Mantel des Reiches kommt der alte genagelte Stiefel zum Vorschein. Eine äußere, höhnische Sicht aus der rivalisierenden Macht, der der „den Elben opfernde Faschismus“ Stoff zur Satire bot.',
  'из архива института (Ташкент).', 'aus dem Institutsarchiv (Taschkent).',
  orig='„КРОКОДИЛ · Новое платье Рейха: под эльфийским плащом — всё тот же кованый сапог“'))
T.append(tile('ES-2085-026', 'Афиша аниме-фильма «Сумеречный луч» (Twilight Ray)', 'Filmplakat des Anime „Twilight Ray“', '2025',
  'Японская киноафиша «обратного исекая»: эльфийка из фэнтези-мира попадает в эльдаризированный Рейх. Поп-культурный отклик соперничающей державы, перерабатывающий мрачную самомифологию Рейха в развлекательный сюжет; название почти созвучно «Twilight Reich».',
  'Japanisches Filmplakat eines „umgekehrten Isekai“: eine Elbe aus einer Fantasiewelt gerät in das eldarisierte Reich. Eine popkulturelle Reaktion einer rivalisierenden Macht, die die düstere Selbstmythologie des Reiches zur Unterhaltung verarbeitet; der Titel klingt fast wie „Twilight Reich“.',
  'из японского собрания киноплакатов.', 'aus einer japanischen Plakatsammlung.',
  orig='「黄昏の光芒（トワイライト・レイ）」 · TWILIGHT RAY — 2025',
  orig_n=('текст афиши на японском языке','Plakattext in japanischer Sprache')))

# ===== E. Человеческий масштаб =====
T.append(grp('Человеческий масштаб', 'Menschliches Maß'))
T.append(tile('ES-2086-110', 'Надгробие девочки из семьи колонистов (фотофиксация)', 'Grabstein eines Kolonistenmädchens (Fotodokumentation)', '1970-е / 1970er',
  'Надгробие с эльфийским именем и эпитафией тенгваром — девочке из семьи поселенцев Срединной Африки, погибшей в Африканской смуте. Частная трагедия внутри большого мифа: идеология достигает даже детской могилы.',
  'Ein Grabstein mit elbischem Namen und einer Grabinschrift in Tengwar — für ein Mädchen aus einer Siedlerfamilie Mittelafrikas, das im Mittelafrika-Notstand ums Leben kam. Eine private Tragödie inmitten des großen Mythos: die Ideologie reicht bis ans Kindergrab.',
  'фотофиксация на месте; камень не перемещался.', 'Fotodokumentation vor Ort; der Stein wurde nicht versetzt.',
  orig='„Tar-Elanor · 1968–1976 · Im Sternenland sehen wir uns wieder“',
  orig_n=('имя и эпитафия продублированы тенгваром','Name und Grabspruch zusätzlich in Tengwar')))
T.append(tile('ES-2086-111', 'Снимок из семейного альбома: день рождения', 'Foto aus einem Familienalbum: ein Geburtstag', '1970-е / 1970er',
  'Любительская фотография дня рождения той же девочки: эльфийские украшения, накладные уши на детях. Та же семья, что и у надгробия ES-2086-110, — за несколько лет до гибели.',
  'Eine Amateuraufnahme vom Geburtstag desselben Mädchens: elbischer Schmuck, aufgesteckte Ohren bei den Kindern. Dieselbe Familie wie beim Grabstein ES-2086-110 — wenige Jahre vor dem Tod.',
  'из семейного архива.', 'aus einem Familienarchiv.',
  orig='„Elanors 6. Geburtstag“',
  orig_n=('надпись на обороте снимка','Aufschrift auf der Rückseite')))
T.append(tile('ES-2086-112', 'Полевая открытка-письмо из Срединной Африки', 'Feldpostkarte aus Mittelafrika', '1970-е / 1970er',
  'Открытка с фронта Африканской смуты домой, с обыденными бодрыми строками. Частный голос рядового участника колониальной войны, которую государственная история называла иначе.',
  'Eine Feldpostkarte vom Schauplatz des Mittelafrika-Notstands nach Hause, mit beiläufig zuversichtlichen Zeilen. Die private Stimme eines einfachen Teilnehmers des Kolonialkrieges, den die Staatsgeschichte anders benannte.',
  'из семейного архива.', 'aus einem Familienarchiv.',
  orig='„Feldpost · Mittelafrika · Uns geht es gut. Bald sind wir wieder daheim.“'))
T.append(tile('ES-2087-004', 'Детский рисунок семьи (из заброшенного дворца)', 'Kinderzeichnung der Familie (aus dem verlassenen Palast)', '2020-е / 2020er',
  'Детский рисунок семьи, висевший у рабочего места чиновника и найденный в оставленном правительственном здании. Личная вещь среди опустевшего монументального центра — человеческий след в «проклятом месте».',
  'Eine Kinderzeichnung der Familie, die am Arbeitsplatz eines Beamten hing und im verlassenen Regierungsgebäude gefunden wurde. Ein persönlicher Gegenstand inmitten des entvölkerten monumentalen Zentrums — eine menschliche Spur am „verfluchten Ort“.',
  'из оставленных помещений правительственного квартала.', 'aus geräumten Amtsräumen des Regierungsviertels.',
  orig='„MEINE FAMILIE“',
  orig_n=('подпись детской рукой','von Kinderhand beschriftet')))

# ===== F. Рецепция и посмертие =====
T.append(grp('Рецепция и посмертие', 'Rezeption und Nachleben'))
T.append(tile('TAS-2031-009', 'Соглашение о русском переводе рукописей Толкина', 'Vereinbarung über die russische Übersetzung von Tolkien-Manuskripten', '2015',
  'Межблоковый лицензионный договор: правами на наследие Толкина, как британского автора, распоряжался Рейх, а советский госиздат приобретал право на русский перевод. Документ свидетельствует и об управлении наследием из Рейха, и о параллельном — литературном, а не культовом — прочтении Толкина на русском Востоке.',
  'Ein Lizenzvertrag über die Blockgrenze hinweg: die Rechte am Erbe Tolkiens, eines britischen Autors, verwaltete das Reich, während ein sowjetischer Staatsverlag das Recht auf die russische Übersetzung erwarb. Das Stück bezeugt zugleich die Verwaltung des Erbes durch das Reich und die parallele — literarische, nicht kultische — Lesart Tolkiens im russischen Osten.',
  'из архива Среднеазиатского института (Ташкент).', 'aus dem Archiv des Mittelasiatischen Instituts (Taschkent).',
  orig='„REICHSSTIFTUNG J. R. R. TOLKIEN, Berlin · Госиздат «Художественная литература» · Stockholm 2015“'))
T.append(tile('ES-2084-008', 'Аукционный каталог реликвий Рейха (Цюрих)', 'Auktionskatalog mit Reliquien des Reiches (Zürich)', '2040-е / 2040er',
  'Швейцарский аукционный каталог, продающий знаки и предметы павшего Рейха коллекционерам. Свидетельство послевоенного обращения реликвий — рынка, с которого, среди прочего, поступали и предметы этого собрания.',
  'Ein Schweizer Auktionskatalog, der Insignien und Gegenstände des untergegangenen Reiches an Sammler veräußert. Ein Zeugnis des Nachkriegshandels mit Reliquien — eben jenes Marktes, von dem unter anderem auch Stücke dieser Sammlung stammen.',
  'библиотека института.', 'Institutsbibliothek.',
  orig='„Insignien und Artefakte des untergegangenen Reiches · Auktion · Zürich“'))
T.append(tile('ES-2073-001', 'Каталог выставки «Эльдаризированный Рейх: эстетика катастрофы»', 'Ausstellungskatalog „Das eldarisierte Reich: Ästhetik der Katastrophe“', 'ок. 2073 / um 2073',
  'Каталог первой крупной выставки раздела. Самореферентный экспонат: издание, которым собрание описывает само себя, и одновременно акт музеефикации катастрофы.',
  'Der Katalog der ersten großen Ausstellung der Abteilung. Ein selbstbezügliches Stück: die Publikation, mit der die Sammlung sich selbst beschreibt, und zugleich ein Akt der Musealisierung der Katastrophe.',
  'издание раздела.', 'Veröffentlichung der Abteilung.',
  orig='„Das eldarisierte Reich: Ästhetik der Katastrophe · Ausstellungskatalog“'))

NEW = ''.join(T)

# --- 3. Заменяем весь блок плиток (от первой плитки до закрытия секции) ---
start = '    <!-- 1. Карта -->'
endm  = '  </section>\n\n  <section id="impressum">'
i = src.index(start); j = src.index(endm)
assert src.count(start) == 1 and src.count(endm) == 1
src = src[:i] + NEW + '\n' + src[j:]

io.open(P, 'w', encoding='utf-8').write(src)
print('patched OK; tiles =', sum(1 for _ in range(len(T))) )
print('articles in file =', src.count('<article class="item">'))
