"""Cited persons in HWPh: names are set in small caps, which the text layer turns into capitals
(KANT, G. W. F. HEGEL, THOMAS VON AQUIN, CH. de MONTESQUIEU). Python 3.8+, stdlib only."""
import collections, re, unicodedata

UP = "A-ZÄÖÜÉÈÊÀÂÎÔÛÇÑÆŒØÅ"
CAPW = "[" + UP + "][" + UP + "'’\\-]+"                     # a word in capitals, at least 2 letters
INIT = "(?:[" + UP + "][A-Za-z" + UP + "]{0,2}\\.\\s?-?\\s?)"      # J.  CH.  CHR.  TH.  PS.-
PART = "(?:von|van|de|da|di|du|der|den|la|le|of|zu|y|ibn|ben|al-|d'|d’|ten|dei|del|degli|vom)"
NAME_RE = re.compile(
    "(?<![\\w.])(" + INIT + "*" + "(?:" + CAPW + "\\.?(?:\\s" + PART + "(?:\\s" + PART + ")?\\s|\\s(?=[" + UP + "]{2})|/|\\s?-\\s?)?)*"
    + CAPW + "\\.?)(?![\\w])")

ROMAN = re.compile(r"^[IVXLC]+\.?$")
# sigla of editions, series and institutions that are set in capitals too
SIGLA = set("""MPL MPG MEW MEGA REZ SU KU NT AT WG VS RGG SVF CSEL CCL CCSL CAG DK GA HWP HWPH SC PL PG
MA DDR USA UNO NSDAP SPD KPD BRD UdSSR SS SA NS EKD ABGR KW KSA KGW WW GW SW AA LA WA HA JA
PAR ZS ZTHK ZPHF PHJB ARSP ADB NDB DNB BGPHMA LTHK THWNT TRE HWBPH RAC PRE GCS CIL EA SEP OED
ZEITSCHR FRG PHIL MS MSS CD LP EU NRF UNESCO NATO WHO UN KG AG GMBH TV DNA RNA EDV IQ ZK OO
FS HG HRSG ED EDS ÜBERS ANM VGL SPÄTER DIES DERS EBD ORIG LIB CAP ART DIST QU SENT TH PS CH CHR
OPP OP OPERA OEUVRES WERKE SCHRIFTEN""".split())
PARTICLES = {"von", "van", "de", "da", "di", "du", "der", "den", "la", "le", "of", "zu", "y", "ibn",
             "ben", "d'", "d’", "ten", "dei", "del", "degli", "vom"}

def raw_mentions(text):
    """-> list of (raw name, position) found in a text"""
    out = []
    for m in NAME_RE.finditer(text):
        s = m.group(1).strip(" -")
        for part in s.split("/"):                 # DIELS/KRANZ -> two names
            part = part.strip(" -")
            if part:
                out.append((part, m.start()))
    return out

def split_name(raw):
    """'G. W. F. HEGELS' -> (initials 'GWF', core 'HEGELS'); drops trailing roman numerals"""
    s = re.sub(r"\s+", " ", raw.replace("’", "'")).strip()
    s = re.sub(r"(?:\s+[IVX]+\.?)+$", "", s)
    m = re.match("^(" + INIT + "*)(.*)$", s)
    inits, core = m.group(1), m.group(2).strip()
    letters = "".join(t[0] for t in re.findall(r"[" + UP + r"][A-Za-z" + UP + r"]{0,2}\.", inits))
    if inits.strip().startswith("PS.") or core.startswith("PS.-"):
        core = "PS.-" + core.replace("PS.-", "").strip(" -")
        letters = letters.replace("P", "", 1)
    return letters, core

def valid_core(core):
    words = [w for w in re.split(r"[\s\-]+", core) if w and w.lower() not in PARTICLES]
    caps = [w for w in words if re.match("[" + UP + "]{2}", w)]
    if not caps:
        return False
    if len(caps) == 1:
        w = caps[0].rstrip(".")
        if ROMAN.match(w) or w in SIGLA or len(w) <= 2:
            return False
        if len(w) == 3 and "." not in caps[0]:
            return False              # three-letter capitals are almost always sigla (MEW, RGG)
    return True

def title(core):
    """'THOMAS VON AQUIN' -> 'Thomas von Aquin', "d'HOLBACH" -> "d'Holbach", 'PS.-DIONYSIUS' -> 'Ps.-Dionysius'"""
    def tw(w):
        if w.lower() in PARTICLES:
            return w.lower()
        if w.startswith(("d'", "D'")):
            return "d'" + tw(w[2:])
        return "-".join(p[:1] + p[1:].lower() for p in w.split("-"))
    return " ".join(tw(w) for w in core.split(" "))

def initials_display(raw_inits_form):
    return raw_inits_form

class Normalizer:
    """Maps raw capitals to persons.
    key = CORE (genitive -s removed, abbreviations expanded) + '|' + initials when initials tell people apart
    (J. G. FICHTE vs I. H. FICHTE); bare mentions go to the dominant initialled variant."""
    def __init__(self, raws):
        # raws: Counter of raw strings
        self.raws = raws
        cores = collections.Counter()
        by_core_inits = collections.defaultdict(collections.Counter)
        forms = collections.defaultdict(collections.Counter)
        for raw, n in raws.items():
            ini, core = split_name(raw)
            if not valid_core(core):
                continue
            cores[core] += n
            by_core_inits[core][ini] += n
            forms[(core, ini)][raw] += n
        self.cores = cores
        # genitive: KANTS -> KANT when KANT itself is attested
        self.core_map = {}
        for core in cores:
            c = core
            if c.endswith("S") and c[:-1] in cores and cores[c[:-1]] >= 2:
                c = c[:-1]
            elif c.endswith("'") and c[:-1] in cores:
                c = c[:-1]
            self.core_map[core] = c
        # abbreviations: ARIST. -> ARISTOTELES (unique frequent completion)
        full = [c for c in cores if not c.endswith(".")]
        for core in cores:
            if core.endswith(".") and " " not in core:
                pre = core[:-1]
                cands = [c for c in full if c.startswith(pre) and len(c) > len(pre) and cores[c] >= 5]
                if cands:
                    best = max(cands, key=lambda c: cores[c])
                    if cores[best] >= 0.7 * sum(cores[c] for c in cands):
                        self.core_map[core] = best
        # bare first word of a dominant multi-word name: THOMAS -> THOMAS VON AQUIN
        multi = collections.defaultdict(collections.Counter)
        for c in full:
            if " " in c:
                multi[c.split(" ")[0]][c] += cores[c]
        for head, cnt in multi.items():
            if head in cores and self.core_map.get(head, head) == head:
                best, bn = cnt.most_common(1)[0]
                if bn >= 0.8 * sum(cnt.values()) and bn >= 10:
                    self.core_map[head] = best
        # merge initials per canonical core
        canon_inits = collections.defaultdict(collections.Counter)
        for core, inits in by_core_inits.items():
            for ini, n in inits.items():
                canon_inits[self.core_map[core]][ini] += n
        self.inits_map = {}
        for core, inits in canon_inits.items():
            named = {i: n for i, n in inits.items() if i}
            dominant = max(named, key=named.get) if named else ""
            total_named = sum(named.values())
            distinct = [i for i, n in named.items() if n >= max(3, 0.1 * total_named)]
            for ini in inits:
                if not ini:
                    # bare: to the dominant variant if it clearly dominates, else stay bare
                    self.inits_map[(core, ini)] = dominant if (not named or named[dominant] >= 0.6 * total_named) else ""
                elif len(distinct) <= 1:
                    self.inits_map[(core, ini)] = dominant
                else:
                    # several people share the surname: keep the initials, fold rare/partial ones into
                    # the variant they are a prefix of
                    if ini in distinct:
                        self.inits_map[(core, ini)] = ini
                    else:
                        tgt = [d for d in distinct if d.startswith(ini) or ini.startswith(d)]
                        self.inits_map[(core, ini)] = max(tgt, key=named.get) if tgt else dominant
        # display names
        self.display = {}
        disp_votes = collections.defaultdict(collections.Counter)
        for (core, ini), fs in forms.items():
            key = self.key_for(core, ini)
            if key:
                for raw, n in fs.items():
                    disp_votes[key][raw] += n
        for key, votes in disp_votes.items():
            ccore, cini = key.split("|")
            # prefer a form with the key's initials, written out in full
            best = None
            for raw, n in votes.most_common():
                ini, core = split_name(raw)
                if ini == cini and not core.endswith(".") and self.core_map.get(core) == ccore and core == ccore:
                    best = raw
                    break
            if best is None:
                best = ccore
            ini_part = re.match("^(" + INIT + "*)", best).group(1)
            ini_part = re.sub(r"\s+", " ", ini_part).strip()
            self.display[key] = ((ini_part.title().replace("Chr.", "Chr.") + " ") if ini_part else "") + title(ccore)

    def key_for(self, core, ini):
        if core not in self.core_map:
            return None
        c = self.core_map[core]
        return c + "|" + self.inits_map.get((c, ini), ini)

    def key(self, raw):
        ini, core = split_name(raw)
        if core not in self.core_map:
            return None
        return self.key_for(core, ini)

def fold_name(s):
    d = unicodedata.normalize("NFD", s)
    return "".join(c for c in d if not unicodedata.combining(c)).lower().replace("ß", "ss")
