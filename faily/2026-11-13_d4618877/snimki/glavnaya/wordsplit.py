"""Расклейка слов, слипшихся при OCR («Weltkann», «nureine», «aconstituent»).

Слово режется надвое, только если его нет в словаре, а одна из половин —
служебное слово из короткого списка, вторая есть в словаре. Так не трогаются
законные немецкие сложные слова (Satzzeichen, Wahrheitsfunktion).
"""
import re
from spellchecker import SpellChecker

FUNC = {
    "de": set("""der die das des dem den ein eine einer eines einem einen und oder aber nicht nur auch
        ist sind war wird werden kann können muss müssen soll sollen darf will hat haben sich es er sie
        wir ich man so wie als wenn dass daß ob zu zum zur in im an am auf aus bei mit von vom nach
        für über unter durch um vor gegen ohne alle alles jede jeder jedes kein keine dies diese dieser
        dieses was wer da dann denn doch noch schon also hier dort sein seine seiner ihr ihre""".split()),
    "en": set("""the a an and or but not of to in on at by for with from as is are was be been it its this
        that these those which what who we i one can cannot must may there their they he his all any
        every no so if then than also only into upon""".split()),
}


class Splitter:
    def __init__(self, lang):
        self.lang = lang
        self.sp = SpellChecker(language=lang)
        self.n = 0

    def known(self, w):
        return w.lower() in self.sp or w.lower() in FUNC[self.lang]

    def split_word(self, w):
        core = re.match(r"^([^\w]*)([\w\-]+?)([^\w]*)$", w)
        if not core:
            return w
        pre, word, post = core.groups()
        if len(word) < 4 or self.known(word) or "-" in word or not word.isalpha():
            return w
        best = None
        for i in range(1, len(word)):
            a, b = word[:i], word[i:]
            fa, fb = a.lower() in FUNC[self.lang], b.lower() in FUNC[self.lang]
            if (fa and self.known(b) and len(b) >= 2) or (fb and self.known(a) and len(a) >= 2):
                score = self.sp.word_frequency[a.lower()] * self.sp.word_frequency[b.lower()]
                if best is None or score > best[0]:
                    best = (score, a, b)
        if not best:
            return w
        self.n += 1
        return f"{pre}{best[1]} {best[2]}{post}"

    def text(self, t):
        out, inpre = [], False
        for ln in t.split("\n"):
            if ln.strip().startswith("```"):
                inpre = not inpre
                out.append(ln)
                continue
            out.append(ln if inpre else " ".join(self.split_word(w) for w in ln.split(" ")))
        return "\n".join(out)
