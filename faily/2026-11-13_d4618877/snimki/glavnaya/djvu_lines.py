"""Строки текстового слоя DjVu с координатами (djvutxt --detail=word).

lines(djvu, page) → [Line]; Line: x0, y0, x1, y1 (y — от верха страницы), h, text, words[(x0, x1, text)].
Кэш разобранных страниц — <djvu>.lines.json рядом с файлом.
"""
import json, os, re, subprocess

TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def _parse(s):
    stack, cur = [], []
    for t in TOK.findall(s):
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t)
    return cur


def _unq(t):
    if t.startswith('"'):
        return bytes(t[1:-1], "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8")
    return t


class Line:
    __slots__ = ("x0", "y0", "x1", "y1", "h", "text", "words")

    def __init__(self, words, H):
        self.words = words
        self.x0 = min(w[0] for w in words); self.x1 = max(w[1] for w in words)
        self.y0 = min(w[2] for w in words); self.y1 = max(w[3] for w in words)
        self.h = self.y1 - self.y0
        self.text = " ".join(w[4] for w in words)

    def __repr__(self):
        return f"<{self.x0},{self.y0} {self.text!r}>"


_cache = {}


def page_count(djvu):
    return int(subprocess.check_output(["djvused", "-e", "n", djvu]).decode())


def lines(djvu, page):
    if djvu not in _cache:
        cp = djvu + ".lines.json"
        _cache[djvu] = json.load(open(cp)) if os.path.exists(cp) else {}
    c = _cache[djvu]
    if str(page) not in c:
        out = subprocess.check_output(["djvutxt", f"--page={page}", "--detail=word", djvu]).decode("utf-8")
        tree = _parse(out)
        res = []
        if tree:
            pg = tree[0]
            H = int(pg[4])

            def walk(node):
                if not isinstance(node, list) or not node:
                    return
                if node[0] == "line":
                    ws = []
                    for w in node[5:]:
                        if isinstance(w, list) and w and w[0] == "word":
                            x0, y0, x1, y1 = map(int, w[1:5]); t = _unq(w[5]).strip()
                            if t:
                                ws.append([x0, x1, H - y1, H - y0, t])
                    if ws:
                        res.append(ws)
                    return
                for ch in node:
                    walk(ch)
            walk(pg)
        c[str(page)] = res
    return [Line(ws, 0) for ws in c[str(page)]]


def save_cache(djvu):
    if djvu in _cache:
        json.dump(_cache[djvu], open(djvu + ".lines.json", "w"), ensure_ascii=False)
