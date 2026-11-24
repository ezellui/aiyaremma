#!/usr/bin/env python3
"""
hwph2md.py — text layer of the digital HWPh PDF -> Markdown, one file per article.

Layout this is tuned to (the edition in which each PDF page = one printed column):
  * running head at y≈25, 17.1pt: <page> | <lemma> | "HWPh Bd. N, <column>"
  * footer at y≈785, 6pt
  * an article starts at the top of a page with a Times-Bold lemma
  * body 22.8pt, notes and bibliography 19.4pt
  * paragraph = first line indented (x≈51), continuation lines at x≈28
  * author signature: right-aligned 19.4pt line in capitals
  * Greek is set with decomposed diacritics (α’δια′ φορα) and µ (micro sign)

Usage:
  pip install pymupdf
  python3 hwph2md.py book.pdf -o out/                 # whole file
  python3 hwph2md.py book.pdf -o out/ --pages 480-600 # page range (1-based)
  python3 hwph2md.py book.pdf -o out/ --by-volume     # one .md per volume
"""
import argparse, csv, os, re, sys, unicodedata
import pymupdf

HEAD_Y = 50          # everything above is the running head
FOOT_SIZE = 8        # everything smaller is the footer
BODY_X = 28
INDENT_MIN_X = 42    # first-line indent threshold
SIGN_X = 280         # right-aligned signature threshold
HEAD_RE = re.compile(r"HWPh Bd\.\s*([0-9]+\*?)\s*,\s*([0-9]+)")

# ---------- Greek repair ----------
GREEK_DIAC = {
    "’": "\u0313", "᾿": "\u0313",            # smooth breathing
    "‘": "\u0314", "῾": "\u0314",            # rough breathing
    "′": "\u0301", "´": "\u0301",            # acute
    "`": "\u0300",                            # grave
    "˜": "\u0342", "῀": "\u0342",            # circumflex
    "¨": "\u0308",                            # diaeresis
}
GREEK_CHAR = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")

def fix_greek(s: str) -> str:
    s = s.replace("µ", "μ")
    if not GREEK_CHAR.search(s):
        return s
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c in GREEK_DIAC and out and GREEK_CHAR.match(unicodedata.normalize("NFD", out[-1])[0] if out[-1] else " "):
            out.append(GREEK_DIAC[c])
            # the PDF puts a spurious space after an accent inside a word
            if i + 1 < len(s) and s[i + 1] == " " and i + 2 < len(s) and GREEK_CHAR.match(s[i + 2]):
                i += 1
        else:
            out.append(c)
        i += 1
    return unicodedata.normalize("NFC", "".join(out))

# ---------- line assembly ----------
def span_md(s):
    t = s["text"]
    if not t.strip():
        return t
    f = s["font"]
    lead = t[: len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    core = t.strip()
    if "Bold" in f:
        return f"{lead}**{core}**{trail}"
    if "Italic" in f:
        return f"{lead}*{core}*{trail}"
    return t

def line_text(line, markup=True):
    parts, last_x1 = [], None
    for s in line["spans"]:
        t = span_md(s) if markup else s["text"]
        if last_x1 is not None and s["bbox"][0] - last_x1 > 2 and parts and not parts[-1].endswith(" ") and not t.startswith(" "):
            parts.append(" ")
        parts.append(t)
        last_x1 = s["bbox"][2]
    t = "".join(parts)
    t = t.replace("\u0002", "→")
    t = re.sub(r"\*\*\s*\*\*|\*\s*\*(?!\*)", " ", t)      # glue adjacent same-style runs
    t = re.sub(r"[ \t]+", " ", t)
    return fix_greek(t.strip())

def page_lines(page):
    rows = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            sp = [s for s in l["spans"] if s["text"]]
            if not sp:
                continue
            size = max(s["size"] for s in sp)
            y = l["bbox"][1]
            if y < HEAD_Y or size < FOOT_SIZE:
                continue
            rows.append({"x0": l["bbox"][0], "x1": l["bbox"][2], "y": y, "y1": l["bbox"][3],
                         "size": size, "line": {"spans": sp},
                         "bold": "Bold" in sp[0]["font"]})
    # merge fragments that share a baseline (justified lines come word by word)
    rows.sort(key=lambda r: (round(r["y"]), r["x0"]))
    merged = []
    for r in rows:
        if merged and abs(merged[-1]["y"] - r["y"]) < 3:
            m = merged[-1]
            m["line"]["spans"] += r["line"]["spans"]
            m["x1"] = max(m["x1"], r["x1"])
        else:
            merged.append(r)
    for m in merged:
        m["line"]["spans"].sort(key=lambda s: s["bbox"][0])
    return merged

def running_head(page):
    txt = page.get_text("text", clip=pymupdf.Rect(0, 0, page.rect.width, HEAD_Y))
    m = HEAD_RE.search(txt)
    return (m.group(1), int(m.group(2))) if m else (None, None)

# ---------- article model ----------
class Article:
    def __init__(self, lemma, vol, col, pdf_page):
        self.lemma, self.vol = lemma, vol
        self.col_from = self.col_to = col
        self.page_from = self.page_to = pdf_page
        self.blocks = []        # ("p"|"h"|"note"|"gap", text)
        self.authors = []
        self.cur = None         # paragraph being built
        self.section = "body"

    def flush(self):
        if self.cur:
            kind, buf = self.cur
            self.blocks.append((kind, " ".join(buf)))
            self.cur = None

    def add_line(self, text, new_par, kind="p"):
        if new_par or self.cur is None or self.cur[0] != kind:
            self.flush()
            self.cur = (kind, [text])
            return
        buf = self.cur[1]
        prev = buf[-1]
        # dehyphenate: "Wahr-" + "heits" -> "Wahrheits"; keep hyphen before capitals
        if re.search(r"[A-Za-zÄÖÜäöüß]-$", prev) and text[:1].islower():
            buf[-1] = prev[:-1] + text.split(" ", 1)[0]
            rest = text.split(" ", 1)[1] if " " in text else ""
            if rest:
                buf.append(rest)
        else:
            buf.append(text)

    def to_md(self):
        self.flush()
        fm = ["---", f'lemma: "{self.lemma}"', f"band: \"{self.vol}\"",
              f"spalten: {self.col_from}" + (f"–{self.col_to}" if self.col_to != self.col_from else ""),
              f"pdf_seiten: {self.page_from}–{self.page_to}"]
        if self.authors:
            fm.append("autoren: [" + ", ".join(f'"{a}"' for a in self.authors) + "]")
        fm.append("---\n")
        out = ["\n".join(fm), f"# {self.lemma}\n"]
        notes = []
        for kind, t in self.blocks:
            t = re.sub(r"\s+", " ", t).strip()
            if kind == "h":
                out.append(f"## {t.strip('*').rstrip('.')}\n")
            elif kind == "note":
                m = re.match(r"\[(\d+)\]\s*(.*)", t)
                notes.append(f"[^{m.group(1)}]: {m.group(2)}" if m else t)
            elif kind == "gap":
                out.append(f"<!-- {t} -->\n")
            else:
                out.append(t + "\n")
        body = "\n".join(out)
        # turn in-text note calls [12] into footnote refs only if the note exists
        ids = {re.match(r"\[\^(\d+)\]", n).group(1) for n in notes if n.startswith("[^")}
        body = re.sub(r"\[(\d+)\](?!\()", lambda m: f"[^{m.group(1)}]" if m.group(1) in ids else m.group(0), body)
        if notes:
            body += "\n## Anmerkungen\n\n" + "\n".join(notes) + "\n"
        return body

def safe_name(s):
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^\w\-,. ]+", "", s).strip().replace(" ", "_")
    return s[:80] or "untitled"

# ---------- main loop ----------
SECTION_RE = re.compile(r"^\*?(Anmerkungen|Literaturhinweise|Literatur)\.?\*?\s*(.*)$")

def process(pdf, out_dir, first, last, by_volume):
    doc = pymupdf.open(pdf)
    last = min(last or doc.page_count, doc.page_count)
    os.makedirs(out_dir, exist_ok=True)
    index_rows, art = [], None
    vol_files = {}

    def emit(a):
        if a is None:
            return
        md = a.to_md()
        vdir = f"Bd{a.vol.replace('*', 's').zfill(2)}"
        if by_volume:
            fh = vol_files.get(vdir)
            if fh is None:
                fh = vol_files[vdir] = open(os.path.join(out_dir, vdir + ".md"), "w", encoding="utf-8")
            fh.write(md + "\n\n")
            path = vdir + ".md"
        else:
            os.makedirs(os.path.join(out_dir, vdir), exist_ok=True)
            path = os.path.join(vdir, f"{a.col_from:05d}_{safe_name(a.lemma)}.md")
            with open(os.path.join(out_dir, path), "w", encoding="utf-8") as fh:
                fh.write(md)
        index_rows.append([a.lemma, a.vol, a.col_from, a.col_to, a.page_from, a.page_to,
                           "; ".join(a.authors), path])

    for pno in range(first - 1, last):
        page = doc[pno]
        vol, col = running_head(page)
        if vol is None:
            continue                     # front matter / index pages without a running head
        rows = page_lines(page)
        if not rows:
            continue
        top = rows[0]
        if top["bold"] and top["x0"] < INDENT_MIN_X and top["y"] < 120:
            emit(art)
            bold = "".join(s["text"] for s in top["line"]["spans"] if "Bold" in s["font"])
            lemma = fix_greek(re.sub(r"\s+", " ", bold)).strip().rstrip(",")
            art = Article(lemma, vol, col, pno + 1)
            full = line_text(top["line"], markup=False).strip()
            if full == lemma or full.rstrip(",") == lemma:
                rows = rows[1:]          # stand-alone heading line
            # otherwise the lemma is run-in: keep the line, bold stays in markup
        if art is None:
            art = Article("(Vorspann)", vol, col, pno + 1)
        art.col_to, art.page_to = col, pno + 1

        prev_y1, prev_size = None, None
        for r in rows:
            text = line_text(r["line"])
            if not text:
                continue
            small = r["size"] < 21
            # author signature
            if small and r["x0"] > SIGN_X and re.fullmatch(r"[A-ZÄÖÜ][A-ZÄÖÜ .\-'/]+(?:\s*/\s*[A-ZÄÖÜ .\-']+)*", text):
                art.flush()
                art.authors.append(text.title() if text.isupper() else text)
                prev_y1, prev_size = r["y1"], r["size"]
                continue
            lh = r["size"] * 1.15
            gap = prev_y1 is not None and r["y"] - prev_y1 > 3 * lh
            if gap:
                art.flush()
                art.blocks.append(("gap", f"Lücke im Textfluss (Formel/Tabelle/Grafik?), PDF-S. {pno + 1}"))
            m = SECTION_RE.match(text)
            if m and small:
                art.flush()
                name = m.group(1)
                art.section = "notes" if name == "Anmerkungen" else "lit"
                if art.section == "lit":
                    art.blocks.append(("h", "Literaturhinweise"))
                    if m.group(2):
                        art.add_line(m.group(2), True)
                elif m.group(2):
                    art.add_line(m.group(2), True, "note")
                prev_y1, prev_size = r["y1"], r["size"]
                continue
            if art.section == "notes" and small:
                new = bool(re.match(r"\[\d+\]", text))
                art.add_line(text, new, "note")
            else:
                if not small:
                    art.section = "body"
                new = r["x0"] >= INDENT_MIN_X or (prev_size and abs(prev_size - r["size"]) > 1)
                art.add_line(text, new)
            prev_y1, prev_size = r["y1"], r["size"]

        if (pno - first) % 500 == 0:
            print(f"… S. {pno + 1}/{last}  {art.lemma}", file=sys.stderr)

    emit(art)
    for fh in vol_files.values():
        fh.close()
    with open(os.path.join(out_dir, "index.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["lemma", "band", "spalte_von", "spalte_bis", "pdf_von", "pdf_bis", "autoren", "datei"])
        w.writerows(index_rows)
    print(f"fertig: {len(index_rows)} Artikel -> {out_dir}", file=sys.stderr)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", default="hwph_md")
    ap.add_argument("--pages", help="1-based range, e.g. 480-600")
    ap.add_argument("--by-volume", action="store_true")
    a = ap.parse_args()
    f, l = 1, None
    if a.pages:
        f, l = (int(x) for x in a.pages.split("-"))
    process(a.pdf, a.out, f, l, a.by_volume)
