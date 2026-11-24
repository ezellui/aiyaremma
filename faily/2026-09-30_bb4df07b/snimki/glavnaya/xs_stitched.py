"""Имитация готовой вышивки: кресты нитками DMC на канве, обратная игла поверх."""
import sys, numpy as np
from PIL import Image, ImageDraw
import xs_scene as S, xs_back as BK, xs_palette as P

FABRIC = '#f3efe4'


def render(kind, A, B, bs, cs=16, out=None, crop=None):
    img = Image.new('RGB', (S.H * cs, S.H * cs), FABRIC)
    d = ImageDraw.Draw(img)
    w = max(2, int(cs * 0.36))
    col = lambda l: P.hexof(P.CROSS[S.LABELS[l]])
    for j in range(S.H):
        for i in range(S.H):
            x0, y0, x1, y1 = i * cs, j * cs, (i + 1) * cs, (j + 1) * cs
            m = cs * 0.12
            k = kind[j, i]
            if k == 0:
                if S.LABELS[A[j, i]] == 'none':
                    continue
                c = col(A[j, i])
                d.line([(x0 + m, y0 + m), (x1 - m, y1 - m)], fill=c, width=w)
                d.line([(x0 + m, y1 - m), (x1 - m, y0 + m)], fill=c, width=w)
            else:
                tri = ([(x0, y0), (x1, y0), (x0, y1)], [(x1, y0), (x1, y1), (x0, y1)]) if k == 1 else \
                      ([(x0, y0), (x1, y0), (x1, y1)], [(x0, y0), (x1, y1), (x0, y1)])
                for poly, l in zip(tri, (A[j, i], B[j, i])):
                    if S.LABELS[l] != 'none':
                        d.polygon(poly, fill=col(l))
    for lab, ((x0, y0), (x1, y1)) in bs:
        n, strands = P.BACK[lab]
        d.line([(x0 * cs, y0 * cs), (x1 * cs, y1 * cs)], fill=P.hexof(n),
               width=max(1, int(cs * (0.16 if strands == 1 else 0.24))))
    return img


if __name__ == '__main__':
    z = np.load('cells.npz')
    img = render(z['kind'], z['A'], z['B'], BK.backstitch(), cs=16)
    img.save(sys.argv[1])
    img.resize((S.H * 6, S.H * 6), Image.LANCZOS).save(sys.argv[2])
