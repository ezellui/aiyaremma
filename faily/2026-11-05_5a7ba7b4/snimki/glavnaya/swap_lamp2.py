"""Crystal lamp from the intermediate picture into the final one, with its own glow, feathered in.
usage: swap_lamp2.py FINAL.png INTERMEDIATE.png OUT.png
"""
import sys
import numpy as np, cv2
from scipy import ndimage

final_fn, mid_fn, out_fn = sys.argv[1:4]
fin = cv2.imread(final_fn).astype(np.float32)
mid = cv2.imread(mid_fn).astype(np.float32)
H, W = fin.shape[:2]

DY = 1057 - 1101                 # foot of the crystal lamp onto this desk
X0, X1 = 703, 816                # keep clear of Fëanor's fingers (left) and the window frame (right)
Y0, Y1 = 700, 1056               # never below the desk edge

def object_mask(img, box, dark=170):
    x0, y0, x1, y1 = box
    crop = img[y0:y1, x0:x1]
    line = ndimage.binary_dilation(crop.sum(axis=2) < dark, iterations=1)
    lab, n = ndimage.label(~line)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    obj = ndimage.binary_fill_holes(~np.isin(lab, list(border)))
    full = np.zeros(img.shape[:2], bool)
    full[y0:y1, x0:x1] = obj
    return full

lantern = object_mask(fin, (X0, 770, X1, 1058))
crystal = object_mask(mid, (694, 760, 808, 1102))
crystal_here = np.zeros_like(crystal)
crystal_here[:H + DY] = crystal[-DY:]

region = ndimage.binary_dilation(lantern | crystal_here, iterations=10)
clip = np.zeros_like(region); clip[Y0:Y1, X0:X1] = True
region &= clip
alpha = cv2.GaussianBlur(region.astype(np.float32), (0, 0), 4.0)
alpha[~clip] = 0
alpha = np.maximum(alpha, ndimage.binary_dilation(lantern | crystal_here, iterations=3) & clip)  # solid over both lamps

mid_here = np.zeros_like(mid)
mid_here[:H + DY] = mid[-DY:]
out = mid_here * alpha[..., None] + fin * (1 - alpha[..., None])
cv2.imwrite(out_fn, np.clip(out, 0, 255).astype(np.uint8))
left = lantern & ~ndimage.binary_dilation(crystal_here, iterations=3) & (alpha < 0.98)
print('lantern pixels not fully covered:', int(left.sum()))
