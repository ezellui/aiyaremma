"""Склейка переносов: решаем по словарю, собранному из самого текста.

Строка кончается на «X-», следующая начинается на «Y…».  Если «X-Y» встречается
где-либо внутри строки — дефис настоящий; иначе, если встречается слитное «XY»
или ничего не известно, — это перенос и дефис убирается.
"""
import re
from collections import Counter

WORD = r"[\ẁ-ͯ]+"
HY = re.compile(rf"({WORD})-$")
HEAD = re.compile(rf"^\W*?({WORD})")


class Dehyph:
    def __init__(self):
        self.hyph = Counter()   # x-y внутри строки
        self.solid = Counter()  # слова целиком

    def learn(self, line):
        core = line[:-1] if line.endswith("-") else line
        for m in re.finditer(rf"({WORD})-({WORD})", core):
            self.hyph[(m.group(1).lower(), m.group(2).lower())] += 1
        for w in re.findall(WORD, core):
            self.solid[w.lower()] += 1

    def keep_hyphen(self, left, right):
        l, r = left.lower(), right.lower()
        if self.hyph[(l, r)]:
            return True
        if self.solid[l + r]:
            return False
        # частицы, которые в русском пишутся через дефис
        if r in ("то", "либо", "нибудь", "таки"):
            return True
        return False

    def join(self, lines):
        """Склеить строки одного абзаца."""
        out = ""
        for i, ln in enumerate(lines):
            ln = ln.strip()
            if not out:
                out = ln
                continue
            if out.endswith("-*") and ln.startswith("*"):
                out, ln = out[:-2] + "-", ln[1:]  # перенос внутри курсива
            m = HY.search(out)
            h = HEAD.match(ln)
            if m and h and not out.endswith(" -"):
                if self.keep_hyphen(m.group(1), h.group(1)):
                    out = out + ln
                else:
                    out = out[:-1] + ln
            else:
                out = out + " " + ln
        return re.sub(r"[ \t]+", " ", out).strip()
