"""Схема вышивки крестом герба Mírë Nolmeo: обложка, ключ, листы схемы (PDF, A4)."""
import sys, math, io
from collections import Counter, defaultdict
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import xs_scene as S, xs_back as BK, xs_palette as P, xs_stitched as ST

FD = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV', FD + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', FD + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVS', FD + 'DejaVuSerif.ttf'))
pdfmetrics.registerFont(TTFont('DVSB', FD + 'DejaVuSerif-Bold.ttf'))

SYMBOL = {
    '823': '•', '310': '×', '334': '◆', 'Ecru': '○', '162': '□', '3756': '☆', '3766': '●',
    '797': '▲', '799': '△', '552': '♠', '209': '♣', '553': '♦', '413': '◐', '498': '♥',
    '3832': '♡', '783': '★', '725': '✦', '910': '▼', '913': '▽', '3753': '◇', 'White': '✧',
    '3765': '◉', '598': '◎', '800': '▣', '778': '◑', '3820': '⬢', '3813': '⊕', '597': '⊗',
    '813': '⊞',
}
TILE = 56
W, Hp = A4
MARGIN = 12 * mm
CELL = (W - 2 * MARGIN - 8 * mm) / TILE
CROSSES_PER_SKEIN = 1600     # Аида 14, 2 сложения, с запасом
HOLE_MM = 25.4 / 14


def lum(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def dmc_of(l):
    n = S.LABELS[l]
    return None if n == 'none' else P.CROSS[n]


def load():
    z = np.load('cells.npz')
    return z['kind'], z['A'], z['B'], BK.backstitch()


def counts(kind, A, B):
    full, three = Counter(), Counter()
    roles = defaultdict(set)
    for j in range(S.H):
        for i in range(S.H):
            if kind[j, i] == 0:
                n = dmc_of(A[j, i])
                if n:
                    full[n] += 1; roles[n].add(P.ROLE[S.LABELS[A[j, i]]])
            else:
                for l in (A[j, i], B[j, i]):
                    n = dmc_of(l)
                    if n:
                        three[n] += 1; roles[n].add(P.ROLE[S.LABELS[l]])
    return full, three, roles


def flat_preview(kind, A, B, bs, cs=8):
    img = Image.new('RGB', (S.H * cs, S.H * cs), 'white'); d = ImageDraw.Draw(img)
    col = lambda l: P.hexof(dmc_of(l)) if dmc_of(l) else '#ffffff'
    for j in range(S.H):
        for i in range(S.H):
            x0, y0, x1, y1 = i * cs, j * cs, (i + 1) * cs, (j + 1) * cs
            k = kind[j, i]
            if k == 0:
                d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=col(A[j, i]))
            elif k == 1:
                d.polygon([(x0, y0), (x1, y0), (x0, y1)], fill=col(A[j, i]))
                d.polygon([(x1, y0), (x1, y1), (x0, y1)], fill=col(B[j, i]))
            else:
                d.polygon([(x0, y0), (x1, y0), (x1, y1)], fill=col(A[j, i]))
                d.polygon([(x0, y0), (x1, y1), (x0, y1)], fill=col(B[j, i]))
    for lab, ((x0, y0), (x1, y1)) in bs:
        n, st = P.BACK[lab]
        d.line([(x0 * cs, y0 * cs), (x1 * cs, y1 * cs)], fill=P.hexof(n), width=2 if st == 2 else 1)
    return img


def footer(c, page, total):
    c.setFont('DV', 7.5); c.setFillColor(HexColor('#777777'))
    c.drawString(MARGIN, 8 * mm, 'Mírë Nolmeo — схема вышивки крестом · 168 × 168 крестов')
    c.drawRightString(W - MARGIN, 8 * mm, f'{page} / {total}')
    c.setFillColor(black)


def cover(c, kind, A, B, bs, full, three, page, total):
    c.setFont('DVSB', 24); c.drawString(MARGIN, Hp - 24 * mm, 'Mírë Nolmeo')
    c.setFont('DV', 11)
    c.drawString(MARGIN, Hp - 31 * mm, 'Эльфийский герб · схема вышивки крестом')
    img = flat_preview(kind, A, B, bs, cs=8)
    side = 120 * mm
    x0, y0 = MARGIN, Hp - 38 * mm - side
    c.drawImage(ImageReader(img), x0, y0, side, side)
    # карта листов
    c.setStrokeColor(HexColor('#c0392b')); c.setLineWidth(0.7)
    c.setFont('DVB', 9); c.setFillColor(HexColor('#c0392b'))
    t = side / 3
    for r in range(3):
        for q in range(3):
            c.rect(x0 + q * t, y0 + side - (r + 1) * t, t, t, stroke=1, fill=0)
            c.drawString(x0 + q * t + 1.5 * mm, y0 + side - r * t - 4.5 * mm, str(3 + r * 3 + q))
    c.setFillColor(black)
    # сведения
    tx = x0 + side + 8 * mm
    ty = Hp - 42 * mm
    lines = [
        ('DVB', 'Размер схемы'), ('DV', '168 × 168 крестов (по диагоналям ромба)'), ('DV', ''),
        ('DVB', 'Готовая работа'),
        ('DV', 'Аида 14: 30,5 × 30,5 см'), ('DV', 'Аида 16: 26,7 × 26,7 см'), ('DV', 'Аида 18: 23,7 × 23,7 см'),
        ('DV', ''), ('DVB', 'Ткань'), ('DV', 'Аида 14, белая или экрю,'), ('DV', 'кусок 50 × 50 см'),
        ('DV', '(по 10 см запаса с краёв)'), ('DV', ''),
        ('DVB', 'Стежки'),
        ('DV', f'полных крестов: {sum(full.values())}'), ('DV', f'¾ крестов: {sum(three.values())}'),
        ('DV', f'цветов DMC: {len(set(full) | set(three) | {v[0] for v in P.BACK.values()})}'),
        ('DV', ''), ('DVB', 'Листы схемы'), ('DV', '3–11, по 56 × 56 крестов;'), ('DV', 'карта — красная сетка'),
        ('DV', 'на превью слева'),
    ]
    for f, s in lines:
        c.setFont(f, 9.5); c.drawString(tx, ty, s); ty -= 4.6 * mm
    # фрагмент вышивки
    st = ST.render(kind, A, B, bs, cs=20)
    crop = st.crop((60 * 20, 0, 108 * 20, 26 * 20))
    fy = y0 - 8 * mm - 50 * mm
    c.setFont('DVB', 10); c.drawString(MARGIN, y0 - 6 * mm, 'Как это будет выглядеть: верхний угол в нитках')
    fw = W - 2 * MARGIN
    c.drawImage(ImageReader(crop), MARGIN, fy, fw, fw * crop.height / crop.width)
    footer(c, page, total)


def key_page(c, full, three, roles, bs, page, total):
    c.setFont('DVSB', 16); c.drawString(MARGIN, Hp - 20 * mm, 'Ключ')
    y = Hp - 30 * mm
    c.setFont('DVB', 8)
    cols = [MARGIN, MARGIN + 11 * mm, MARGIN + 25 * mm, MARGIN + 66 * mm, MARGIN + 136 * mm,
            MARGIN + 152 * mm, MARGIN + 168 * mm]
    for x, h in zip(cols, ['', 'DMC', 'Название', 'Где в гербе', 'кресты', '¾', 'мотки']):
        c.drawString(x, y, h)
    y -= 2 * mm; c.setLineWidth(0.4); c.line(MARGIN, y, W - MARGIN, y); y -= 5 * mm
    order = sorted(set(full) | set(three), key=lambda n: -(full[n] + 0.75 * three[n]))
    for n in order:
        hx = P.hexof(n)
        c.setFillColor(HexColor(hx)); c.setStrokeColor(HexColor('#555555')); c.setLineWidth(0.3)
        c.rect(cols[0], y - 1.3 * mm, 6 * mm, 4.6 * mm, stroke=1, fill=1)
        c.setFillColor(white if lum(hx) < 0.5 else black); c.setFont('DV', 8.5)
        c.drawCentredString(cols[0] + 3 * mm, y - 0.2 * mm, SYMBOL[n])
        c.setFillColor(black); c.setFont('DVB', 8.5); c.drawString(cols[1], y, n)
        c.setFont('DV', 8); c.drawString(cols[2], y, P.nameof(n)[:24])
        c.setFont('DV', 7.5); c.drawString(cols[3], y, '; '.join(sorted(roles[n]))[:52])
        c.setFont('DV', 8)
        c.drawRightString(cols[4] + 10 * mm, y, str(full[n]))
        c.drawRightString(cols[5] + 8 * mm, y, str(three[n]) if three[n] else '—')
        sk = max(1, math.ceil((full[n] + 0.75 * three[n]) / CROSSES_PER_SKEIN))
        c.drawRightString(cols[6] + 8 * mm, y, str(sk))
        y -= 5.6 * mm
    # обратная игла
    y -= 3 * mm
    c.setFont('DVSB', 12); c.drawString(MARGIN, y, 'Обратная игла'); y -= 6 * mm
    lens = defaultdict(float)
    for lab, ((x0, y0), (x1, y1)) in bs:
        lens[lab] += math.hypot(x1 - x0, y1 - y0)
    c.setFont('DVB', 8)
    for x, h in zip([MARGIN, MARGIN + 20 * mm, MARGIN + 34 * mm, MARGIN + 75 * mm, MARGIN + 96 * mm, MARGIN + 160 * mm],
                    ['', 'DMC', 'Название', 'сложений', 'Где в гербе', 'длина']):
        c.drawString(x, y, h)
    y -= 2 * mm; c.line(MARGIN, y, W - MARGIN, y); y -= 5 * mm
    for lab in ['red', 'navy', 'facet', 'facet_w', 'cream_bs']:
        if lab not in lens:
            continue
        n, st = P.BACK[lab]
        hx = P.hexof(n)
        c.setStrokeColor(HexColor('#000000') if lum(hx) > 0.6 else HexColor('#ffffff'))
        c.setLineWidth(3.2 if st == 2 else 2.4); c.line(MARGIN, y + 1 * mm, MARGIN + 15 * mm, y + 1 * mm)
        c.setStrokeColor(HexColor(hx)); c.setLineWidth(2.2 if st == 2 else 1.4)
        c.line(MARGIN, y + 1 * mm, MARGIN + 15 * mm, y + 1 * mm)
        c.setFont('DVB', 8.5); c.drawString(MARGIN + 20 * mm, y, n)
        c.setFont('DV', 8); c.drawString(MARGIN + 34 * mm, y, P.nameof(n)[:22])
        c.drawString(MARGIN + 75 * mm, y, str(st))
        c.setFont('DV', 7.5); c.drawString(MARGIN + 96 * mm, y, P.BACK_ROLE[lab])
        c.setFont('DV', 8); c.drawRightString(W - MARGIN, y, f'{lens[lab] * HOLE_MM / 1000:.1f} м')
        y -= 5.6 * mm
    # пояснения
    y -= 4 * mm
    notes = [
        ('DVSB', 11, 'Как читать схему'),
        ('DV', 8.5, 'Клетка с символом — полный крест; нитка в 2 сложения на Аиде 14.'),
        ('DV', 8.5, 'Клетка, разделённая диагональю, — два ¾ креста: каждый треугольник своим цветом'),
        ('DV', 8.5, '(короткий полукрест к углу треугольника и четверть-крест к центру клетки).'),
        ('DV', 8.5, 'На кромке ромба и по внутреннему краю верёвки один треугольник пустой — там ¾ креста одного цвета.'),
        ('DV', 8.5, 'Линии поверх клеток — обратная игла, по узлам канвы; шить после всех крестов.'),
        ('DV', 8.5, 'Красные стрелки на полях листов отмечают середину схемы (84-й столбец и 84-я строка);'),
        ('DV', 8.5, 'удобно начинать от центра: белый камень лежит ровно на центральном узле.'),
        ('DV', 8.5, 'Мотки посчитаны с запасом (≈1600 крестов на моток 8 м); обратной иглы хватит одного мотка.'),
        ('DV', 8.5, 'Если взять чёрную канву, цвет 310 (поле ромба) можно не вышивать.'),
        ('DV', 8.5, 'Цвета ниток подобраны по таблице RGB DMC; оттенки на экране приблизительны.'),
    ]
    for f, sz, s in notes:
        c.setFont(f, sz); c.drawString(MARGIN, y, s); y -= (6 if f == 'DVSB' else 4.4) * mm
    footer(c, page, total)


def chart_page(c, kind, A, B, bs, tr, tc, page, total):
    i0, j0 = tc * TILE, tr * TILE
    i1, j1 = min(i0 + TILE, S.H), min(j0 + TILE, S.H)
    ox = MARGIN + 8 * mm
    oy = Hp - 22 * mm                      # верх сетки
    c.setFont('DVB', 11)
    c.drawString(MARGIN, Hp - 13 * mm, f'Лист {page}')
    c.setFont('DV', 9)
    c.drawString(MARGIN + 18 * mm, Hp - 13 * mm,
                 f'столбцы {i0 + 1}–{i1}, строки {j0 + 1}–{j1}  ·  ряд листов {tr + 1}, колонка {tc + 1}')

    def X(i): return ox + (i - i0) * CELL
    def Y(j): return oy - (j - j0) * CELL

    for j in range(j0, j1):
        for i in range(i0, i1):
            k = kind[j, i]
            x, y = X(i), Y(j + 1)
            if k == 0:
                n = dmc_of(A[j, i])
                if not n:
                    continue
                hx = P.hexof(n)
                c.setFillColor(HexColor(hx)); c.rect(x, y, CELL, CELL, stroke=0, fill=1)
                c.setFillColor(white if lum(hx) < 0.5 else black); c.setFont('DV', CELL * 0.72)
                c.drawCentredString(x + CELL / 2, y + CELL * 0.24, SYMBOL[n])
            else:
                if k == 1:
                    tris = [[(x, y + CELL), (x + CELL, y + CELL), (x, y)], [(x + CELL, y + CELL), (x + CELL, y), (x, y)]]
                else:
                    tris = [[(x, y + CELL), (x + CELL, y + CELL), (x + CELL, y)], [(x, y + CELL), (x + CELL, y), (x, y)]]
                for tri, l in zip(tris, (A[j, i], B[j, i])):
                    n = dmc_of(l)
                    if not n:
                        continue
                    hx = P.hexof(n)
                    p = c.beginPath(); p.moveTo(*tri[0]); p.lineTo(*tri[1]); p.lineTo(*tri[2]); p.close()
                    c.setFillColor(HexColor(hx)); c.drawPath(p, stroke=0, fill=1)
                    cx = sum(t[0] for t in tri) / 3; cy = sum(t[1] for t in tri) / 3
                    c.setFillColor(white if lum(hx) < 0.5 else black); c.setFont('DV', CELL * 0.45)
                    c.drawCentredString(cx, cy - CELL * 0.15, SYMBOL[n])
                c.setStrokeColor(HexColor('#444444')); c.setLineWidth(0.25)
                if k == 1:
                    c.line(x + CELL, y + CELL, x, y)
                else:
                    c.line(x, y + CELL, x + CELL, y)
    # сетка
    for i in range(i0, i1 + 1):
        heavy = i % 10 == 0
        c.setStrokeColor(HexColor('#222222' if heavy else '#9a9a9a')); c.setLineWidth(0.7 if heavy else 0.18)
        c.line(X(i), Y(j0), X(i), Y(j1))
    for j in range(j0, j1 + 1):
        heavy = j % 10 == 0
        c.setStrokeColor(HexColor('#222222' if heavy else '#9a9a9a')); c.setLineWidth(0.7 if heavy else 0.18)
        c.line(X(i0), Y(j), X(i1), Y(j))
    # обратная игла
    for lab, ((x0, y0), (x1, y1)) in bs:
        if max(x0, x1) < i0 or min(x0, x1) > i1 or max(y0, y1) < j0 or min(y0, y1) > j1:
            continue
        n, st = P.BACK[lab]; hx = P.hexof(n)
        c.saveState()
        p = c.beginPath(); p.rect(X(i0), Y(j1), X(i1) - X(i0), Y(j0) - Y(j1)); c.clipPath(p, stroke=0, fill=0)
        c.setLineCap(1)
        c.setStrokeColor(black if lum(hx) > 0.5 else white); c.setLineWidth(2.6 if st == 2 else 1.9)
        c.line(X(x0), Y(y0), X(x1), Y(y1))
        c.setStrokeColor(HexColor(hx)); c.setLineWidth(1.7 if st == 2 else 1.0)
        c.line(X(x0), Y(y0), X(x1), Y(y1))
        c.restoreState()
    # нумерация и середина
    c.setFont('DV', 6.5); c.setFillColor(black)
    for i in range(i0, i1 + 1):
        if i % 10 == 0:
            c.drawCentredString(X(i), Y(j0) + 1.6 * mm, str(i))
    for j in range(j0, j1 + 1):
        if j % 10 == 0:
            c.drawRightString(X(i0) - 1.2 * mm, Y(j) - 0.8 * mm, str(j))
    c.setFillColor(HexColor('#c0392b'))
    if i0 <= S.HALF <= i1:
        xm = X(S.HALF)
        p = c.beginPath(); p.moveTo(xm, Y(j0) + 0.6 * mm); p.lineTo(xm - 1.6 * mm, Y(j0) + 4.6 * mm)
        p.lineTo(xm + 1.6 * mm, Y(j0) + 4.6 * mm); p.close(); c.drawPath(p, stroke=0, fill=1)
        p = c.beginPath(); p.moveTo(xm, Y(j1) - 0.6 * mm); p.lineTo(xm - 1.6 * mm, Y(j1) - 4.6 * mm)
        p.lineTo(xm + 1.6 * mm, Y(j1) - 4.6 * mm); p.close(); c.drawPath(p, stroke=0, fill=1)
    if j0 <= S.HALF <= j1:
        ym = Y(S.HALF)
        p = c.beginPath(); p.moveTo(X(i0) - 0.6 * mm, ym); p.lineTo(X(i0) - 4.6 * mm, ym + 1.6 * mm)
        p.lineTo(X(i0) - 4.6 * mm, ym - 1.6 * mm); p.close(); c.drawPath(p, stroke=0, fill=1)
        p = c.beginPath(); p.moveTo(X(i1) + 0.6 * mm, ym); p.lineTo(X(i1) + 4.6 * mm, ym + 1.6 * mm)
        p.lineTo(X(i1) + 4.6 * mm, ym - 1.6 * mm); p.close(); c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(black)
    # мини-карта листа
    mx, my, ms = W - MARGIN - 14 * mm, Hp - 16 * mm, 4.2 * mm
    for r in range(3):
        for q in range(3):
            c.setFillColor(HexColor('#c0392b') if (r, q) == (tr, tc) else HexColor('#dddddd'))
            c.rect(mx + q * ms, my - r * ms, ms - 0.5 * mm, ms - 0.5 * mm, stroke=0, fill=1)
    c.setFillColor(black)
    footer(c, page, total)


def main(out):
    kind, A, B, bs = load()
    full, three, roles = counts(kind, A, B)
    total = 11
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle('Mírë Nolmeo — схема вышивки крестом'); c.setAuthor('User')
    cover(c, kind, A, B, bs, full, three, 1, total); c.showPage()
    key_page(c, full, three, roles, bs, 2, total); c.showPage()
    pg = 3
    for tr in range(3):
        for tc in range(3):
            chart_page(c, kind, A, B, bs, tr, tc, pg, total); c.showPage(); pg += 1
    c.save()
    print(out, 'full', sum(full.values()), 'three-quarter', sum(three.values()))


if __name__ == '__main__':
    main(sys.argv[1])
