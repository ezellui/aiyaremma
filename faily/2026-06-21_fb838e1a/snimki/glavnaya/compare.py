#!/usr/bin/env python3
# Попиксельная сверка пропатченных PDF против эталонных.
import os, sys, subprocess, glob, shutil, time
import numpy as np
from PIL import Image

DPI = 150
WORK = "/home/claude/work"
ORIG = "/home/claude/orig"
PROG = "/home/claude/pixeldiff_progress.txt"
REPORT = "/home/claude/pixeldiff_report.txt"

def log(msg):
    with open(PROG, "a") as f:
        f.write(msg + "\n")

def pdf_pages(p):
    out = subprocess.check_output(["pdfinfo", p], text=True)
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return None

def render(pdf, outdir):
    os.makedirs(outdir, exist_ok=True)
    subprocess.check_call(["pdftoppm", "-r", str(DPI), "-png", pdf,
                           os.path.join(outdir, "p")],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(os.path.join(outdir, "p-*.png")))

def region(top, bottom, H):
    # классифицируем вертикальное положение bbox по полосам страницы
    t, b = top / H, bottom / H
    tags = []
    if t < 0.10: tags.append("колонтитул(верх)")
    if b > 0.90: tags.append("подвал(низ)")
    if b > 0.12 and t < 0.88: tags.append("тело")
    return ",".join(tags) if tags else "?"

def compare_edition(name, base_pdf, patch_pdf, rep):
    rep.append("\n" + "=" * 70)
    rep.append(f"ИЗДАНИЕ {name}")
    rep.append("=" * 70)
    nb, npp = pdf_pages(base_pdf), pdf_pages(patch_pdf)
    rep.append(f"страниц: эталон={nb}, пропатченный={npp}")
    log(f"[{name}] рендер эталона ({nb} стр.)…")
    bdir = f"/home/claude/_png_{name}_base"
    pdir = f"/home/claude/_png_{name}_patch"
    bfiles = render(base_pdf, bdir)
    log(f"[{name}] рендер пропатченного ({npp} стр.)…")
    pfiles = render(patch_pdf, pdir)
    n = min(len(bfiles), len(pfiles))
    identical = 0
    diffs = []   # (page, frac_all, frac_sig, bbox, region, dim_mismatch)
    for i in range(n):
        a = np.asarray(Image.open(bfiles[i]).convert("RGB"))
        b = np.asarray(Image.open(pfiles[i]).convert("RGB"))
        page = i + 1
        if a.shape != b.shape:
            diffs.append((page, 1.0, 1.0, None, f"размер отличается {a.shape}≠{b.shape}", True))
            continue
        if np.array_equal(a, b):
            identical += 1
        else:
            d = np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2)
            mask_all = d > 0
            mask_sig = d > 24          # порог против шума антиалиасинга
            n_all = int(mask_all.sum())
            n_sig = int(mask_sig.sum())
            H, W = d.shape
            tot = H * W
            ys, xs = np.where(mask_sig if n_sig else mask_all)
            bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
            reg = region(bbox[1], bbox[3], H)
            diffs.append((page, n_all / tot, n_sig / tot, bbox, reg, False))
        if (i + 1) % 50 == 0:
            log(f"[{name}] сверено {i+1}/{n}")
    rep.append(f"сравнено страниц: {n}")
    rep.append(f"  попиксельно ИДЕНТИЧНЫ: {identical}/{n}")
    rep.append(f"  с различиями: {len(diffs)}/{n}")
    if nb != npp:
        rep.append(f"  ВНИМАНИЕ: число страниц различается (хвост {abs(nb-npp)} стр. вне сравнения)")
    if diffs:
        rep.append("  страницы с различиями (порог значимости >24/255 по каналу):")
        for (page, fa, fs, bbox, reg, dim) in diffs:
            if dim:
                rep.append(f"    стр.{page}: {reg}")
            else:
                rep.append(f"    стр.{page}: все_пиксели={fa*100:.3f}%  значимые={fs*100:.3f}%  "
                           f"bbox(px)={bbox}  область={reg}")
    else:
        rep.append("  → все сравненные страницы попиксельно идентичны.")
    shutil.rmtree(bdir, ignore_errors=True)
    shutil.rmtree(pdir, ignore_errors=True)
    return identical, len(diffs), n, nb, npp

def main():
    open(PROG, "w").close()
    rep = []
    t0 = time.time()
    log("старт сверки")
    res = {}
    for name, sub in [("RUS", "eldamo-intro-quenya-book_RUS"),
                      ("ENG", "eldamo-intro-quenya-book_ENG")]:
        base = f"{ORIG}/{sub}/full/eldamo-intro-quenya-full.pdf"
        patch = f"{WORK}/{sub}/full/eldamo-intro-quenya-full.pdf"
        res[name] = compare_edition(name, base, patch, rep)
    rep.append("\n" + "=" * 70)
    rep.append("ИТОГ")
    rep.append("=" * 70)
    for name in ("RUS", "ENG"):
        idn, dn, n, nb, npp = res[name]
        rep.append(f"{name}: идентичны {idn}/{n}, различий {dn}; страниц эталон/патч = {nb}/{npp}")
    rep.append(f"время сверки: {time.time()-t0:.0f} c, DPI={DPI}")
    with open(REPORT, "w") as f:
        f.write("\n".join(rep) + "\n")
    log("ГОТОВО")

if __name__ == "__main__":
    main()
