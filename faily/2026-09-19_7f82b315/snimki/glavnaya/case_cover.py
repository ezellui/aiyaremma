#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Переплётная крышка (твёрдый переплёт, прямой корешок) для «Во времена великанов».

Печатается ОДНА сторона: изнанку крышки закрывают форзацы.

По горизонтали, слева направо:
  загиб | задняя сторонка | расстав | отстав (корешок) | расстав | передняя сторонка | загиб
По вертикали:
  загиб | сторонка (блок + 2 канта) | загиб

Все размеры ниже — типовые для 7БЦ при картоне 2 мм. У переплётчика почти наверняка
свой шаблон: цифры BOARD_MM, JOINT_MM, TURN_IN_MM и толщину блока взять у него —
скрипт пересчитает лист целиком.

Полосы обложки (стр. 1 и 120 книжного PDF) ставятся на сторонки вплотную к краю
у корешка: так рельс с кружками глав (5,6 мм от корешкового края полосы) остаётся
на картоне, а не уходит в паз расстава. Всё, чего полосе не хватает до края листа
(канты, загиб, остаток ширины сторонки), наращивается зеркальной укладкой её же
краёв (edges.py); расстав и отстав заливаются переходом между корешковыми краями
двух полос, как корешок мягкой обложки.
"""
import os, sys
import pikepdf
from pikepdf import Name, Dictionary, Array
import numpy as np
from edges import Edges, jpeg
from cover_spine import spine_text_pdf, _img, INK   # надпись на корешке — та же

SRC = 'Vo_vremena_velikanov_kniga_ed.pdf'   # полная книга: стр. 1 — лицо, стр. 120 — задник
FRONT_PAGE, BACK_PAGE = 1, 120
MM = 72.0 / 25.4

# --- книжный блок -------------------------------------------------------------
LEAVES = 60             # 120 стр. блока
BLOCK_CALIPER = 0.10    # мм на лист (мелованная 115 г/м² ≈ 0,09–0,10)
ENDPAPER_CALIPER = 0.18 # форзацная бумага 140–170 г/м²
ENDPAPER_LEAVES = 4     # два сфальцованных форзаца, у корешка по 2 листа
SPINE_EXTRA = 1.0       # нитки + корешковый материал (марля, бумажная полоска)

# --- крышка --------------------------------------------------------------------
BOARD_MM = 2.0          # толщина переплётного картона
KANT_MM = 3.0           # кант: выступ сторонки над блоком сверху, снизу, с переднего края
BOARD_SETBACK_MM = 3.0  # на сколько сторонка не доходит до корешка блока
JOINT_MM = 7.0          # расстав (паз шарнира) между сторонкой и отставом
TURN_IN_MM = 15.0       # загиб на изнанку, считая от кромки картона
MARGIN_MM = 12.0        # поле под метки вокруг листа
MARK_GAP_MM, MARK_LEN_MM = 3.0, 5.0

SHEETS = {'A3': (420.0, 297.0), 'SRA3': (450.0, 320.0)}


def block_thickness():
    return LEAVES * BLOCK_CALIPER + ENDPAPER_LEAVES * ENDPAPER_CALIPER + SPINE_EXTRA


def geometry(block_w_mm, block_h_mm, block_t_mm=None):
    t = block_thickness() if block_t_mm is None else block_t_mm
    g = dict(
        block_t=t,
        board_w=block_w_mm + KANT_MM - BOARD_SETBACK_MM,
        board_h=block_h_mm + 2 * KANT_MM,
        spine=t + 2 * BOARD_MM,                    # отстав
        wrap=TURN_IN_MM + BOARD_MM,                # загиб + обхват кромки картона
    )
    g['w'] = 2 * g['wrap'] + 2 * g['board_w'] + 2 * JOINT_MM + g['spine']
    g['h'] = 2 * g['wrap'] + g['board_h']
    # x-координаты (мм, от левого края листа крышки)
    x = g['wrap']
    g['x_back'] = x;              x += g['board_w']
    g['x_joint1'] = x;            x += JOINT_MM
    g['x_spine'] = x;             x += g['spine']
    g['x_joint2'] = x;            x += JOINT_MM
    g['x_front'] = x;             x += g['board_w']
    g['y_board'] = g['wrap']
    return g


def _pad_page(a, px_mm, top, bottom, left, right):
    """Нарастить растр полосы на заданные мм зеркальной укладкой."""
    P = lambda v: max(0, int(round(v * px_mm)))
    t, b, l, r = P(top), P(bottom), P(left), P(right)
    out = a
    # np.pad 'symmetric' не умеет шире самого массива — наращиваем по кускам
    def grow(arr, n, axis, before):
        while n > 0:
            k = min(n, arr.shape[axis] - 1)
            pw = [(0, 0)] * 3
            pw[axis] = (k, 0) if before else (0, k)
            arr = np.pad(arr, pw, mode='symmetric')
            n -= k
        return arr
    out = grow(out, t, 0, True); out = grow(out, b, 0, False)
    out = grow(out, l, 1, True); out = grow(out, r, 1, False)
    return out, (t, b, l, r)


def build_case(out_path, block_t_mm=None, sheet=None, marks=True):
    src = pikepdf.open(SRC)
    ed = Edges(SRC)
    mb = [float(v) for v in src.pages[0].MediaBox]
    pw, ph = mb[2] - mb[0], mb[3] - mb[1]
    g = geometry(pw / MM, ph / MM, block_t_mm)
    W, H = g['w'] * MM, g['h'] * MM
    if sheet:
        mw, mh = sheet[0] * MM, sheet[1] * MM
        assert mw >= W and mh >= H, f"крышка {g['w']:.1f}×{g['h']:.1f} мм не влезает в лист {sheet}"
    else:
        mw, mh = W + 2 * MARGIN_MM * MM, H + 2 * MARGIN_MM * MM
    ox, oy = (mw - W) / 2, (mh - H) / 2        # левый нижний угол крышки на листе

    out = pikepdf.Pdf.new()
    res_x, ops = Dictionary(), []
    px_mm = ed.px_mm
    # полоса на сторонке: по вертикали по центру (кант сверху и снизу),
    # по горизонтали вплотную к корешковому краю сторонки
    y_page = g['y_board'] + KANT_MM
    extra_w = g['board_w'] - pw / MM                  # остаток ширины сторонки у переднего края
    vert = g['wrap'] + KANT_MM                        # сколько нарастить сверху и снизу

    placements = [
        # (стр., x полосы в мм, нарастить слева, справа)
        (BACK_PAGE, g['x_back'] + extra_w, g['wrap'] + extra_w, 0.0),
        (FRONT_PAGE, g['x_front'], 0.0, extra_w + g['wrap']),
    ]
    # 1) растровая подложка сторонок: полоса + наращивание до краёв листа
    for n, (pg, x_mm, grow_l, grow_r) in enumerate(placements):
        a = ed.arr(pg)
        big, (t, b, l, r) = _pad_page(a, px_mm, vert, vert, grow_l, grow_r)
        data, iw, ih = jpeg(big)
        nm = Name(f'/Ib{n}')
        res_x[nm] = _img(out, data, iw, ih)
        x0 = ox + (x_mm - grow_l) * MM
        y0 = oy + (y_page - vert) * MM
        ops.append(f'q {iw / px_mm * MM:.3f} 0 0 {ih / px_mm * MM:.3f} {x0:.3f} {y0:.3f} cm {nm} Do Q')

    # 2) расстав + отстав + расстав: переход между корешковыми краями полос
    mid_mm = 2 * JOINT_MM + g['spine']
    fill = ed.spine_fill(BACK_PAGE, FRONT_PAGE, mid_mm)
    fill, _ = _pad_page(fill, px_mm, vert, vert, 0, 0)
    data, iw, ih = jpeg(fill)
    res_x[Name('/ImMid')] = _img(out, data, iw, ih)
    ops.append(f'q {mid_mm * MM:.3f} 0 0 {ih / px_mm * MM:.3f} '
               f'{ox + g["x_joint1"] * MM:.3f} {oy + (y_page - vert) * MM:.3f} cm /ImMid Do Q')

    # 3) векторные полосы поверх — чёткий текст и рисунок
    for n, (pg, x_mm, _, _) in enumerate(placements):
        fx = pikepdf.Page(src.pages[pg - 1]).as_form_xobject()
        nm = Name(f'/Fx{n}')
        res_x[nm] = out.copy_foreign(src.make_indirect(fx))
        ops.append(f'q 1 0 0 1 {ox + x_mm * MM:.3f} {oy + y_page * MM:.3f} cm {nm} Do Q')

    # 4) надпись на отставе: по центру высоты сторонки
    txt_path, size_t, size_a = spine_text_pdf(g['spine'] * MM, g['board_h'] * MM, 'case_spine_text.pdf')
    tp = pikepdf.open(txt_path)
    fx = pikepdf.Page(tp.pages[0]).as_form_xobject()
    res_x[Name('/FxSpine')] = out.copy_foreign(tp.make_indirect(fx))
    ops.append(f'q 1 0 0 1 {ox + g["x_spine"] * MM:.3f} {oy + g["y_board"] * MM:.3f} cm /FxSpine Do Q')

    # 5) метки: рез по краю крышки; штрихом — кромки картона и отстава; точками — загиб
    if marks:
        ops.append(_marks(ox, oy, W, H, g))

    content = pikepdf.Stream(out, '\n'.join(ops).encode())
    page = Dictionary(
        Type=Name.Page,
        MediaBox=Array([0, 0, mw, mh]),
        TrimBox=Array([ox, oy, ox + W, oy + H]),
        BleedBox=Array([ox, oy, ox + W, oy + H]),   # загиб сам служит вылетом
        Resources=Dictionary(XObject=res_x),
        Contents=out.make_indirect(content),
    )
    out.pages.append(pikepdf.Page(out.make_indirect(page)))
    with out.open_metadata() as m:
        m['dc:title'] = 'Во времена великанов — переплётная крышка'
    out.save(out_path, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    return g, size_t, size_a


def _marks(ox, oy, W, H, g):
    G, L = MARK_GAP_MM * MM, MARK_LEN_MM * MM
    x0, y0, x1, y1 = ox, oy, ox + W, oy + H
    ops = ['q', '0 G', '0.25 w', '[] 0 d']
    seg = lambda ax, ay, bx, by: ops.append(f'{ax:.3f} {ay:.3f} m {bx:.3f} {by:.3f} l S')
    for x in (x0, x1):                                  # рез
        s = -1 if x == x0 else 1
        seg(x, y0 - G, x, y0 - G - L); seg(x, y1 + G, x, y1 + G + L)
        seg(x + s * G, y0, x + s * (G + L), y0); seg(x + s * G, y1, x + s * (G + L), y1)
    ops.append('[2 2] 0 d')                             # кромки картона и отстава
    xs = [g['x_back'], g['x_joint1'], g['x_spine'], g['x_joint2'],
          g['x_front'], g['x_front'] + g['board_w']]
    for xm in xs:
        x = ox + xm * MM
        seg(x, y0 - G, x, y0 - G - L); seg(x, y1 + G, x, y1 + G + L)
    for ym in (g['y_board'], g['y_board'] + g['board_h']):
        y = oy + ym * MM
        seg(x0 - G, y, x0 - G - L, y); seg(x1 + G, y, x1 + G + L, y)
    ops.append('Q')
    return '\n'.join(ops)


if __name__ == '__main__':
    t = float(sys.argv[1]) if len(sys.argv) > 1 else None     # толщина блока, мм (от переплётчика)
    sheet = SHEETS.get(sys.argv[2]) if len(sys.argv) > 2 else None
    os.makedirs('out/kryshka', exist_ok=True)
    tag = f'{t:g}mm' if t else 'raschet'
    p = f'out/kryshka/kryshka_{tag}' + (f'_{sys.argv[2]}' if sheet else '') + '.pdf'
    g, st, sa = build_case(p, t, sheet)
    print(f"блок {g['block_t']:.2f} мм → отстав {g['spine']:.2f} мм; "
          f"сторонка {g['board_w']:.1f}×{g['board_h']:.1f} мм; "
          f"крышка {g['w']:.1f}×{g['h']:.1f} мм")
    print(f'кегль на корешке: название {st:.1f} pt, автор {sa:.1f} pt')
    print(p)
