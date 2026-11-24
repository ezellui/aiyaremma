"""Общие средства: строки страницы PDF со стилями span-ов (PyMuPDF)."""
import pymupdf

MACRON = "¯"


class Line:
    __slots__ = ("page", "x0", "y0", "x1", "y1", "spans", "size")

    def __init__(self, page, spans):
        self.page = page
        self.spans = sorted(spans, key=lambda s: s["bbox"][0])
        xs = [s["bbox"] for s in self.spans]
        self.x0 = min(b[0] for b in xs)
        self.y0 = min(b[1] for b in xs)
        self.x1 = max(b[2] for b in xs)
        self.y1 = max(b[3] for b in xs)
        main = [s for s in self.spans if s["text"].strip() and not s["flags"] & 1]
        self.size = max((s["size"] for s in main), default=self.spans[0]["size"])

    @property
    def text(self):
        return "".join(s["text"] for s in self.spans)

    def bold(self):
        """Жирный ли основной текст строки (по первому значимому span-у)."""
        for s in self.spans:
            if s["text"].strip() and not s["flags"] & 1:
                return bool(s["flags"] & 16) or "Bold" in s["font"]
        return False

    def __repr__(self):
        return f"<{self.page}:{self.x0:.0f},{self.y0:.0f} {self.text!r}>"


def page_lines(doc, pno, ytol=2.5):
    """Строки страницы: span-ы с близким базовым y склеены в одну строку."""
    d = doc[pno].get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE)
    spans = []
    for b in d["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"] == "":
                    continue
                s = dict(s)
                s["base"] = l["bbox"][3] if not s["flags"] & 1 else None
                spans.append(s)
    # базовая линия: низ bbox для обычного текста; надстрочные — к ближайшей
    norm = [s for s in spans if s["base"] is not None]
    for s in spans:
        if s["base"] is None:
            cy = (s["bbox"][1] + s["bbox"][3]) / 2
            best = min(norm, key=lambda t: abs((t["bbox"][1] + t["bbox"][3]) / 2 - cy) +
                       (0 if t["bbox"][1] - 2 <= cy <= t["bbox"][3] + 2 else 50), default=None)
            s["base"] = best["base"] if best else s["bbox"][3]
    spans.sort(key=lambda s: (s["base"], s["bbox"][0]))
    lines, cur, cb = [], [], None
    for s in spans:
        if cur and abs(s["base"] - cb) > ytol:
            lines.append(Line(pno + 1, cur))
            cur = []
        if not cur:
            cb = s["base"]
        cur.append(s)
    if cur:
        lines.append(Line(pno + 1, cur))
    return lines


def render_spans(spans, footnote_size=7.0, mark_italic=True, fn_fmt="[^{}]"):
    """Span-ы -> текст с разметкой: *курсив*, **жирный**, [^n] для сносок, <sup>."""
    out = []
    for s in spans:
        t = s["text"]
        if not t:
            continue
        if t.strip() == MACRON:
            # надчёркивание над предыдущей буквой (p̄, ξ̄)
            if out:
                out[-1] = out[-1].rstrip() + "̄"
            continue
        if s["flags"] & 1 and s["size"] < footnote_size:
            st = t.strip()
            if st and (st.isdigit() or set(st) <= set("*")):
                out.append(fn_fmt.format(st))
            elif st:
                out.append(f"<sup>{st}</sup>")
            continue
        italic = bool(s["flags"] & 2) or "Ital" in s["font"]
        if italic and mark_italic and t.strip():
            lead = t[: len(t) - len(t.lstrip())]
            trail = t[len(t.rstrip()):]
            out.append(f"{lead}*{t.strip()}*{trail}")
        else:
            out.append(t)
    s = "".join(out)
    s = s.replace("**", "")  # склейка соседних курсивных span-ов: *a**b* -> *ab*
    return s
