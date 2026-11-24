"""Replace the lantern in the final illustration with the crystal lamp from the intermediate one.
usage: swap_lamp.py FINAL.png INTERMEDIATE.png OUT.png DEBUG_PREFIX
"""
import sys
import numpy as np, cv2
from scipy import ndimage

final_fn, mid_fn, out_fn, dbg = sys.argv[1:5]
fin = cv2.imread(final_fn)
mid = cv2.imread(mid_fn)

def object_mask(img, box, dark=170):
    """pixels enclosed by the black contour inside box: everything not reachable from the box border"""
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1].astype(int)
    line = crop.sum(axis=2) < dark                 # black contour
    line = ndimage.binary_dilation(line, iterations=1)
    free = ~line
    lab, n = ndimage.label(free)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outside = np.isin(lab, list(border))
    obj = ~outside
    obj = ndimage.binary_fill_holes(obj)
    full = np.zeros(img.shape[:2], bool)
    full[y0:y1, x0:x1] = obj
    return full

# lamp boxes: above the desk line, below the window arch
FIN_BOX = (690, 770, 828, 1058)        # lantern stands on the desk at y≈1057
MID_BOX = (688, 760, 812, 1102)        # crystal lamp stands on the desk at y≈1101
DY = 1057 - 1101

m_fin = object_mask(fin, FIN_BOX)
m_mid = object_mask(mid, MID_BOX)
cv2.imwrite(dbg + 'mask_fin.png', (m_fin * 255).astype(np.uint8))
cv2.imwrite(dbg + 'mask_mid.png', (m_mid * 255).astype(np.uint8))

# 1. remove the lantern: inpaint from the surrounding glow
hole = ndimage.binary_dilation(m_fin, iterations=3)
hole[1056:, :] = False                     # never touch the desk
clean = cv2.inpaint(fin, hole.astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)

# 2. paste the crystal lamp, shifted so that its foot stands on this desk
ys, xs = np.nonzero(m_mid)
alpha = cv2.GaussianBlur(m_mid.astype(np.float32), (3, 3), 0.6)
out = clean.astype(np.float32)
for y, x in zip(ys, xs):
    pass
yy0, yy1 = ys.min(), ys.max() + 1
xx0, xx1 = xs.min(), xs.max() + 1
src = mid[yy0:yy1, xx0:xx1].astype(np.float32)
a = alpha[yy0:yy1, xx0:xx1][..., None]
ty0 = yy0 + DY
out[ty0:ty0 + (yy1 - yy0), xx0:xx1] = src * a + out[ty0:ty0 + (yy1 - yy0), xx0:xx1] * (1 - a)
cv2.imwrite(out_fn, np.clip(out, 0, 255).astype(np.uint8))
print('lamp box mid', (xx0, yy0, xx1, yy1), '-> top', ty0, 'bottom', ty0 + yy1 - yy0, 'removed px', int(hole.sum()))
