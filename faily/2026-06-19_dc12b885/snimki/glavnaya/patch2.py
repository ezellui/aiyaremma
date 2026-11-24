#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Добавление четырёх экспонатов в нужные группы."""
import io
P = '/home/claude/eldarische_sammlung.html'
src = io.open(P, encoding='utf-8').read()

def one(old, new):
    global src
    assert src.count(old) == 1, f'ожидалось 1 вхождение, найдено {src.count(old)}: {old[:70]!r}'
    src = src.replace(old, new, 1)

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
        note_block = ('        <p class="note"><span lang="ru">%s</span><span lang="de">%s</span></p>\n' % note)
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

# --- мундир + винил → в конец группы A (перед заголовком «Повседневное») ---
uniform = tile('ES-2076-090', 'Парадный мундир высшего чина (эльдаризированный)', 'Galauniform eines höchsten Ranges (eldarisiert)', '2010-е / 2010er',
  'Мундир высшего сановника позднего Рейха: строгий военный крой, но с серебряным шитьём, восьмиконечными звёздами и — вместо фуражки — тонким венцом. Зримое выражение того, как имперская форма «переоделась» в эльфийское: власть осталась, сменилась её обрядовая оболочка.',
  'Die Uniform eines höchsten Würdenträgers des späten Reiches: strenger militärischer Schnitt, doch mit Silberstickerei, achtzackigen Sternen und — anstelle der Schirmmütze — einem schmalen Stirnreif. Ein sichtbarer Ausdruck dessen, wie sich die imperiale Form ins Elbische „umkleidete“: die Macht blieb, ihre rituelle Hülle wechselte.',
  'антикварный рынок.', 'Antiquitätenmarkt.',
  orig='„Hofschneiderei · Berlin · Reichsuniform, höchster Rang“',
  orig_n=('на воротнике — шитый тенгваром девиз и восьмиконечная звезда','am Kragen ein in Tengwar gestickter Wahlspruch und ein achtzackiger Stern'))
vinyl = tile('ES-2081-205', 'Конверт пластинки «Chöre der Eldar» (гимны на квенья)', 'Plattenhülle „Chöre der Eldar“ (Hymnen in Quenya)', '2010-е / 2010er',
  'Конверт коллекционного издания хоровых гимнов на квенья, отпечатанного на серебряно-золотом виниле. Парадная, литургическая сторона режима: государственная музыка как обряд. Тексты — на Высокой Речи, с немецким переводом на вкладыше.',
  'Die Hülle einer Sammlerausgabe chorischer Hymnen in Quenya, gepresst auf silbern-goldenem Vinyl. Die feierliche, liturgische Seite des Regimes: Staatsmusik als Ritus. Die Texte stehen in der Hohen Sprache, mit deutscher Übersetzung auf der Beilage.',
  'антикварный рынок.', 'Antiquitätenmarkt.',
  orig='„CHÖRE DER ELDAR · Hymnen in der Hohen Sprache · Reichsschallplatte“',
  orig_n=('заглавие продублировано тенгваром; пометка «серебряно-золотой винил»','Titel zusätzlich in Tengwar; Vermerk „silbern-goldenes Vinyl“'))

anchor_B = '    <p class="grp"><svg class="ic-star"><use href="#star"/></svg><span lang="ru">Повседневное</span><span lang="de">Alltag</span></p>\n'
one(anchor_B, uniform + vinyl + anchor_B)

# --- детская книжка → в конец группы B (перед заголовком «Движение и сопротивление») ---
book = tile('ES-2079-066', 'Детская книжка «Wie die Hohen ihre wahren Namen fanden»', 'Kinderbilderbuch „Wie die Hohen ihre wahren Namen fanden“', '2010-е / 2010er',
  'Богато иллюстрированная детская книга, в сказочной форме объясняющая детям эльфийское «возвращение» и обычай истинных имён. Рядом с оловянными рыцарями (ES-2081-152) — образец того, как идеология входила в детство через красивую сказку.',
  'Ein reich illustriertes Kinderbuch, das den Kindern in Märchenform die elbische „Heimkehr“ und den Brauch der wahren Namen erklärt. Neben den Zinnrittern (ES-2081-152) ein Beispiel dafür, wie die Ideologie über das schöne Märchen in die Kindheit eindrang.',
  'частное дарение.', 'private Schenkung.',
  orig='„Wie die Hohen ihre wahren Namen fanden · Ein Bilderbuch“',
  orig_n=('заглавие продублировано тенгваром','Titel zusätzlich in Tengwar'))
anchor_C = '    <p class="grp"><svg class="ic-star"><use href="#star"/></svg><span lang="ru">Движение и сопротивление</span><span lang="de">Bewegung und Widerstand</span></p>\n'
one(anchor_C, book + anchor_C)

# --- путеводитель → в конец группы D (перед заголовком «Человеческий масштаб») ---
guide = tile('ES-2080-330', 'Иностранный путеводитель по городам и этикету Рейха', 'Ausländischer Reiseführer zu den Städten und Sitten des Reiches', '2000-е–2010-е / 2000er–2010er',
  'Зарубежный путеводитель бедекеровского типа, разъясняющий иностранцу переименованные «истинные» названия городов и правила обращения к сановникам на Tar-. Взгляд извне в практическом регистре: как чужаку вести себя в эльдаризированном Рейхе.',
  'Ein ausländischer Reiseführer nach Art des Baedeker, der dem Fremden die umbenannten „wahren“ Städtenamen und die Anredeformen für Würdenträger mit „Tar-“ erläutert. Eine Außensicht im praktischen Register: wie sich ein Fremder im eldarisierten Reich zu verhalten habe.',
  'библиотека института.', 'Institutsbibliothek.',
  orig='„THE GREATER GERMAN REICH · A Traveller’s Guide to Its Cities and Customs“')
anchor_E = '    <p class="grp"><svg class="ic-star"><use href="#star"/></svg><span lang="ru">Человеческий масштаб</span><span lang="de">Menschliches Maß</span></p>\n'
one(anchor_E, guide + anchor_E)

io.open(P, 'w', encoding='utf-8').write(src)
print('articles in file =', src.count('<article class="item">'))
