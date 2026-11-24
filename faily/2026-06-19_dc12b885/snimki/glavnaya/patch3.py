#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит регистра: описания делаем нейтральными, толкования — в примечания."""
import io
P = '/home/claude/eldarische_sammlung.html'
src = io.open(P, encoding='utf-8').read()

def one(old, new):
    global src
    assert src.count(old) == 1, f'!= 1 ({src.count(old)}): {old[:70]!r}'
    src = src.replace(old, new, 1)

def desc(old_ru, old_de, new_ru, new_de, note=None):
    o = '        <p class="desc" lang="ru">%s</p>\n        <p class="desc" lang="de">%s</p>\n' % (old_ru, old_de)
    n = '        <p class="desc" lang="ru">%s</p>\n        <p class="desc" lang="de">%s</p>\n' % (new_ru, new_de)
    if note:
        n += '        <p class="note"><span lang="ru">%s</span><span lang="de">%s</span></p>\n' % note
    one(o, n)

# банкнота — иронию в примечание
desc('Денежный знак с гравированным портретом Дж. Р. Р. Толкина и подписью «Вернувший Речь»; номинал продублирован тенгваром. Помещение писателя, презиравшего режим, на государственные деньги — характерный пример его посмертного присвоения.',
     'Ein Geldschein mit dem gestochenen Bildnis J. R. R. Tolkiens und der Beischrift „der Wiederbringer der Sprache“; der Nennwert ist in Tengwar wiederholt. Die Setzung des Schriftstellers, der das Regime verachtete, auf das Staatsgeld ist ein bezeichnendes Beispiel seiner postumen Vereinnahmung.',
     'Денежный знак с гравированным портретом Дж. Р. Р. Толкина и подписью «Вернувший Речь»; номинал продублирован тенгваром.',
     'Ein Geldschein mit dem gestochenen Bildnis J. R. R. Tolkiens und der Beischrift „der Wiederbringer der Sprache“; der Nennwert ist in Tengwar wiederholt.',
     note=('Помещение Толкина — автора, относившегося к национал-социализму с неприязнью, — на государственные деньги приводят как пример его посмертного присвоения режимом.',
           'Die Setzung Tolkiens — eines Autors, der dem Nationalsozialismus ablehnend gegenüberstand — auf das Staatsgeld wird als Beispiel seiner postumen Vereinnahmung durch das Regime angeführt.'))

# псевдофилология — снять «псевдонауку» из описания (вердикт уже в примечании)
desc('Научная по виду статья из рейхского журнала, «доказывающая» происхождение квенья из общего арийского праязыка. Образец идеологической псевдонауки, академически оформлявшей присвоение Толкина.',
     'Ein wissenschaftlich aufgemachter Aufsatz aus einer Reichszeitschrift, der die Herkunft des Quenya aus einer gemeinsamen arischen Ursprache „nachweist“. Ein Beispiel ideologischer Pseudowissenschaft, die die Vereinnahmung Tolkiens akademisch verbrämte.',
     'Статья из рейхского журнала, по форме научная, «доказывающая» происхождение квенья из общего арийского праязыка.',
     'Ein wissenschaftlich aufgemachter Aufsatz aus einer Reichszeitschrift, der die Herkunft des Quenya aus einer gemeinsamen arischen Ursprache „nachweist“.')

# мундир — тезис в примечание
desc('Мундир высшего сановника позднего Рейха: строгий военный крой, но с серебряным шитьём, восьмиконечными звёздами и — вместо фуражки — тонким венцом. Зримое выражение того, как имперская форма «переоделась» в эльфийское: власть осталась, сменилась её обрядовая оболочка.',
     'Die Uniform eines höchsten Würdenträgers des späten Reiches: strenger militärischer Schnitt, doch mit Silberstickerei, achtzackigen Sternen und — anstelle der Schirmmütze — einem schmalen Stirnreif. Ein sichtbarer Ausdruck dessen, wie sich die imperiale Form ins Elbische „umkleidete“: die Macht blieb, ihre rituelle Hülle wechselte.',
     'Мундир высшего сановника позднего Рейха: строгий военный крой с серебряным шитьём, восьмиконечными звёздами и — вместо фуражки — тонким венцом.',
     'Die Uniform eines höchsten Würdenträgers des späten Reiches: strenger militärischer Schnitt mit Silberstickerei, achtzackigen Sternen und — anstelle der Schirmmütze — einem schmalen Stirnreif.',
     note=('Сохранение военного кроя при эльфийской отделке и венце приводят как пример того, что эльдаризация сменила обрядовую оболочку власти, не затронув её устройства.',
           'Die Beibehaltung des militärischen Schnitts bei elbischer Ausstattung und Stirnreif wird als Beispiel dafür angeführt, dass die Eldarisierung die rituelle Hülle der Macht wechselte, ohne ihren Bau zu berühren.'))

# продкарточка — снять «нищету за красивым шрифтом»
desc('Карточка нормированного снабжения с тонко исполненным эльфийским орнаментом и заголовком тенгваром. Сочетание изысканного оформления и скудного содержания — наглядное свидетельство нищеты автаркии за красивым шрифтом.',
     'Eine Bezugskarte für rationierte Lebensmittel mit fein ausgeführter elbischer Ornamentik und einer Kopfzeile in Tengwar. Der Gegensatz von edler Gestaltung und kargem Inhalt bezeugt anschaulich die Armut der Autarkie hinter schöner Schrift.',
     'Карточка нормированного снабжения с тонко исполненным эльфийским орнаментом и заголовком тенгваром. Изысканное оформление контрастирует со скудостью нормируемого пайка.',
     'Eine Bezugskarte für rationierte Lebensmittel mit fein ausgeführter elbischer Ornamentik und einer Kopfzeile in Tengwar. Die edle Gestaltung steht im Gegensatz zur Kargheit der zugeteilten Ration.')

# реклама Silmaril — снять «декаданс»
desc('Журнальная реклама духов, названных в честь Сильмарилей. Свидетельство позднего декаданса, когда эльфийские имена сделались товарным знаком роскоши.',
     'Eine Zeitschriftenwerbung für ein nach den Silmaril benanntes Parfüm. Ein Zeugnis des späten Dekadenz, als elbische Namen zum Markenzeichen des Luxus wurden.',
     'Журнальная реклама духов, названных в честь Сильмарилей. Пример позднего периода, когда эльфийские имена использовались как товарный знак предметов роскоши.',
     'Eine Zeitschriftenwerbung für ein nach den Silmaril benanntes Parfüm. Ein Beispiel der späten Zeit, als elbische Namen als Markenzeichen für Luxusgüter dienten.')

# уши — снять «декадентской поры»
one('придавая себе облик бессмертных эльфов. Предмет поздней декадентской поры; сохранены следы тонального грима.',
    'придавая себе облик бессмертных эльфов. Предмет позднего периода Рейха; сохранены следы тонального грима.')
one('um sich das Aussehen der unsterblichen Elben zu geben. Ein Stück der späten dekadenten Zeit; Spuren von Hautton-Schminke erhalten.',
    'um sich das Aussehen der unsterblichen Elben zu geben. Ein Stück der späten Zeit des Reiches; Spuren von Hautton-Schminke erhalten.')

# оловянные рыцари — снять «проникновение идеологии»
desc('Детский набор фигурок: «эльфийские рыцари» в стилизованной рейхской форме, со звёздами и Белым Древом. Пример проникновения идеологии в игру и быт детства.',
     'Ein Kinderset von Figuren: „Eldar-Ritter“ in stilisierter Reichsuniform, mit Sternen und Weißem Baum. Ein Beispiel für das Eindringen der Ideologie in das kindliche Spiel und den Alltag.',
     'Детский набор фигурок: «эльфийские рыцари» в стилизованной рейхской форме, со звёздами и Белым Древом. Предмет детского обихода эпохи.',
     'Ein Kinderset von Figuren: „Eldar-Ritter“ in stilisierter Reichsuniform, mit Sternen und Weißem Baum. Ein Gegenstand des kindlichen Alltags der Epoche.')

# детская книжка — снять «идеология входила в детство через сказку»
desc('Богато иллюстрированная детская книга, в сказочной форме объясняющая детям эльфийское «возвращение» и обычай истинных имён. Рядом с оловянными рыцарями (ES-2081-152) — образец того, как идеология входила в детство через красивую сказку.',
     'Ein reich illustriertes Kinderbuch, das den Kindern in Märchenform die elbische „Heimkehr“ und den Brauch der wahren Namen erklärt. Neben den Zinnrittern (ES-2081-152) ein Beispiel dafür, wie die Ideologie über das schöne Märchen in die Kindheit eindrang.',
     'Богато иллюстрированная детская книга, в сказочной форме излагающая детям эльфийское «возвращение» и обычай истинных имён. Вместе с оловянными рыцарями (ES-2081-152) относится к предметам детского обихода эпохи.',
     'Ein reich illustriertes Kinderbuch, das den Kindern in Märchenform die elbische „Heimkehr“ und den Brauch der wahren Namen darlegt. Zusammen mit den Zinnrittern (ES-2081-152) zählt es zu den Gegenständen des kindlichen Alltags der Epoche.')

# зин — снять «не было лишь безобидным»
one('когда низовое увлечение языком срасталось с идеологией; показывает, что движение «снизу» не было лишь безобидным.',
    'когда низовое увлечение языком срасталось с идеологией.')
one('als die Begeisterung von unten mit der Ideologie verwuchs; es zeigt, dass die Bewegung „von unten“ nicht bloß harmlos war.',
    'als die Begeisterung von unten mit der Ideologie verwuchs.')

# листовка-Аккалабет — «верное прочтение» в примечание
desc('Листовка противников режима, обращающая против власти тот самый сюжет о низвержении Нуменора, который эльдаризм читал как героический образец. Редкий пример «верного прочтения» легендариума, ставшего орудием сопротивления.',
     'Ein Flugblatt von Gegnern des Regimes, das die Erzählung vom Untergang Númenors — die der Eldarismus als heroisches Vorbild las — gegen die Macht wendet. Ein seltenes Beispiel der „richtigen Lesart“ des Legendariums als Mittel des Widerstands.',
     'Листовка противников режима, обращающая против власти сюжет о низвержении Нуменора, который эльдаризм истолковывал как героический образец. Редкое сохранившееся свидетельство подпольной агитации.',
     'Ein Flugblatt von Gegnern des Regimes, das die Erzählung vom Untergang Númenors — die der Eldarismus als heroisches Vorbild las — gegen die Macht wendet. Ein seltenes erhaltenes Zeugnis der Untergrundagitation.',
     note=('Листовку рассматривают как прочтение легендариума, противоположное официальному: предостережение о гибели от гордыни обращено против власти, видевшей в том же сюжете образец.',
           'Das Flugblatt gilt als eine dem amtlichen entgegengesetzte Lesart des Legendariums: die Warnung vor dem Untergang durch Hybris wird gegen die Macht gewendet, die in derselben Erzählung ein Vorbild sah.'))

# надгробие — снять патетику
desc('Надгробие с эльфийским именем и эпитафией тенгваром — девочке из семьи поселенцев Срединной Африки, погибшей в Африканской смуте. Частная трагедия внутри большого мифа: идеология достигает даже детской могилы.',
     'Ein Grabstein mit elbischem Namen und einer Grabinschrift in Tengwar — für ein Mädchen aus einer Siedlerfamilie Mittelafrikas, das im Mittelafrika-Notstand ums Leben kam. Eine private Tragödie inmitten des großen Mythos: die Ideologie reicht bis ans Kindergrab.',
     'Надгробие с эльфийским именем и эпитафией тенгваром — девочке из семьи поселенцев Срединной Африки, погибшей в Африканской смуте. Эльфийское имянаречение и письмо тенгвар распространялись и на частные, в том числе детские, погребения.',
     'Ein Grabstein mit elbischem Namen und einer Grabinschrift in Tengwar — für ein Mädchen aus einer Siedlerfamilie Mittelafrikas, das im Mittelafrika-Notstand ums Leben kam. Elbische Namensgebung und Tengwar-Schrift erstreckten sich auch auf private, darunter kindliche, Bestattungen.')

# полевая открытка — снять реплику, факт в примечание
desc('Открытка с фронта Африканской смуты домой, с обыденными бодрыми строками. Частный голос рядового участника колониальной войны, которую государственная история называла иначе.',
     'Eine Feldpostkarte vom Schauplatz des Mittelafrika-Notstands nach Hause, mit beiläufig zuversichtlichen Zeilen. Die private Stimme eines einfachen Teilnehmers des Kolonialkrieges, den die Staatsgeschichte anders benannte.',
     'Открытка с театра Африканской смуты домой, с обыденными бодрыми строками. Частное свидетельство рядового участника колониальной кампании.',
     'Eine Feldpostkarte vom Schauplatz des Mittelafrika-Notstands nach Hause, mit beiläufig zuversichtlichen Zeilen. Ein privates Zeugnis eines einfachen Teilnehmers des Kolonialfeldzugs.',
     note=('«Африканской смутой» официально именовались колониальные войны Рейха в Срединной Африке.',
           'Als „Mittelafrika-Notstand“ wurden amtlich die Kolonialkriege des Reiches in Mittelafrika bezeichnet.'))

# детский рисунок — снять «человеческий след в проклятом месте»
desc('Детский рисунок семьи, висевший у рабочего места чиновника и найденный в оставленном правительственном здании. Личная вещь среди опустевшего монументального центра — человеческий след в «проклятом месте».',
     'Eine Kinderzeichnung der Familie, die am Arbeitsplatz eines Beamten hing und im verlassenen Regierungsgebäude gefunden wurde. Ein persönlicher Gegenstand inmitten des entvölkerten monumentalen Zentrums — eine menschliche Spur am „verfluchten Ort“.',
     'Детский рисунок семьи, висевший у рабочего места чиновника и найденный в оставленном правительственном здании. Один из частных предметов, оставшихся в покинутых помещениях правительственного квартала.',
     'Eine Kinderzeichnung der Familie, die am Arbeitsplatz eines Beamten hing und im verlassenen Regierungsgebäude gefunden wurde. Einer der privaten Gegenstände, die in den geräumten Amtsräumen des Regierungsviertels zurückblieben.')

# Правило в «Принципах отбора»
one('<strong>Контекст вместо любования.</strong> Предметы показываются с пояснением, а не как святыни; экспонирование исключает культовое прочтение.',
    '<strong>Контекст вместо любования.</strong> Предметы показываются с пояснением, а не как святыни; экспонирование исключает культовое прочтение. Описание предмета нейтрально; толкования и оценки вынесены в примечания.')
one('<strong>Einordnung statt Verehrung.</strong> Stücke werden erläutert, nicht als Reliquien gezeigt; die Präsentation schließt eine kultische Lesart aus.',
    '<strong>Einordnung statt Verehrung.</strong> Stücke werden erläutert, nicht als Reliquien gezeigt; die Präsentation schließt eine kultische Lesart aus. Die Beschreibung ist sachlich gehalten; Deutungen und Wertungen stehen in den Anmerkungen.')

io.open(P, 'w', encoding='utf-8').write(src)
print('notes total =', src.count('<p class="note">'))
print('articles =', src.count('<article class="item">'))
