"""Вырезки к участкам regions61.json и обзорные листы для вычитки по картинке.

    python3 crops61.py ../ocr regions61.json lp1961.json ../out/proof/regions [--sheets sheets]

crops/<id>.png — вырезка участка (строка; найденное место обведено рамкой) или всего положения;
--sheets: склейки по 10–12 участков с подписями «№ | OCR | наш текст» — для просмотра глазами.
"""
import json, os, re, sys, hashlib
from PIL import Image, ImageDraw, ImageFont

OCR, REG, LP, OUT = sys.argv[1:5]
SHEETS = sys.argv[sys.argv.index("--sheets") + 1] if "--sheets" in sys.argv else None
lp = json.load(open(LP))
canon = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "canon.json")))
regs = json.load(open(REG))
os.makedirs(f"{OUT}/crops", exist_ok=True)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
TOP, BOTTOM = 200, 2700
_pg = {}


def page(p):
    if p not in _pg:
        _pg[p] = Image.open(f"{OCR}/pg-{p:03d}.pgm").convert("L")
    return _pg[p]


def rid(r):
    return hashlib.md5(r["key"].encode()).hexdigest()[:10]


def prop_crop(lang, num):
    i = canon.index(num)
    nxt = canon[i + 1] if i + 1 < len(canon) else None
    pg, y = lp[lang]["loc"][num]
    pieces = []
    if nxt and lp[lang]["loc"][nxt][0] == pg:
        pieces.append((pg, y - 25, lp[lang]["loc"][nxt][1] - 10))
    else:
        pieces.append((pg, y - 25, BOTTOM))
        if nxt and lp[lang]["loc"][nxt][0] == pg + 2 and lp[lang]["loc"][nxt][1] - TOP > 40:
            pieces.append((pg + 2, TOP, lp[lang]["loc"][nxt][1] - 10))
    ims = [page(p).crop((60, max(0, a), page(p).width - 60, min(page(p).height, b))) for p, a, b in pieces]
    w = max(i.width for i in ims)
    out = Image.new("L", (w, sum(i.height for i in ims) + 12 * (len(ims) - 1)), 255)
    yy = 0
    for im in ims:
        out.paste(im, (0, yy)); yy += im.height + 12
    return out


def word_crop(r):
    x1, y1, x2, y2 = r["box"]
    im = page(r["page"]).crop((x1, y1, x2, y2)).convert("RGB")
    d = ImageDraw.Draw(im)
    a, b = r["hl"]
    d.rectangle((a - x1, 3, b - x1, im.height - 4), outline=(220, 40, 40), width=3)
    return im


crops = {}
for r in regs:
    r["id"] = rid(r)
    im = word_crop(r) if r["kind"] == "word" else prop_crop(r["lang"], r["num"]).convert("RGB")
    if r["kind"] != "word":
        im = im.resize((im.width * 6 // 10, im.height * 6 // 10))
    im.save(f"{OUT}/crops/{r['id']}.png", optimize=True)
    crops[r["id"]] = im
json.dump(regs, open(REG, "w"), ensure_ascii=False, indent=0)

if SHEETS:
    os.makedirs(SHEETS, exist_ok=True)
    for f in os.listdir(SHEETS):
        os.remove(f"{SHEETS}/{f}")
    for lang in ("de", "en"):
        for kind, per in (("word", 12), ("formula", 1)):
            rr = [r for r in regs if r["lang"] == lang and r["kind"] == kind]
            for s in range(0, len(rr), per):
                part = rr[s:s + per]
                rows = []
                for k, r in enumerate(part):
                    im = crops[r["id"]]
                    if im.width > 1500:
                        im = im.resize((1500, im.height * 1500 // im.width))
                    lab = f"{s + k}  {r['num']}  OCR: {r['ocr']}  |  текст: {r['cur']}" if kind == "word" \
                        else f"{s + k}  {r['num']}"
                    rows.append((lab[:140], im))
                W = max(max(im.width for _, im in rows), 900)
                H = sum(im.height + 34 for _, im in rows)
                sh = Image.new("RGB", (W, H), "white")
                d = ImageDraw.Draw(sh)
                y = 0
                for lab, im in rows:
                    d.text((4, y + 4), lab, fill=(30, 60, 160), font=FONT)
                    sh.paste(im, (0, y + 30)); y += im.height + 34
                sh.save(f"{SHEETS}/{lang}-{kind}-{s:03d}.png")
print(len(regs), "вырезок")
