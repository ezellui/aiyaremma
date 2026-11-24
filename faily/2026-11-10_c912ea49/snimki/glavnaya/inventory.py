# Inventory of slugs for the tengwar typewriter design document.
# kind: T = advancing tengwa, C = advancing combined (carrier + tehta),
#       N = advancing numeral, P = advancing punctuation,
#       DA = dead mark above, DB = dead mark below (fixed), DL = dead mark below (measured length),
#       DX = special dead mark (lambe doubler)
# glyph: codepoints (base first) or a glyph name for marks (to measure variants)

TENGWAR = [
    # primary, tyelle 1..6 (Appendix E grades), 4 temar
    (0xE000, 'tinco'), (0xE001, 'parma'), (0xE002, 'calma'), (0xE003, 'quesse'),
    (0xE004, 'ando'), (0xE005, 'umbar'), (0xE006, 'anga'), (0xE007, 'ungwe'),
    (0xE008, 'thúle'), (0xE009, 'formen'), (0xE00A, 'harma'), (0xE00B, 'hwesta'),
    (0xE00C, 'anto'), (0xE00D, 'ampa'), (0xE00E, 'anca'), (0xE00F, 'unque'),
    (0xE010, 'númen'), (0xE011, 'malta'), (0xE012, 'noldo'), (0xE013, 'nwalme'),
    (0xE014, 'óre'), (0xE015, 'vala'), (0xE016, 'anna'), (0xE017, 'vilya'),
    # extended stems
    (0xE018, 'ext. tinco'), (0xE019, 'ext. parma'), (0xE01A, 'ext. calma'), (0xE01B, 'ext. quesse'),
    (0xE01C, 'ext. ando'), (0xE01D, 'ext. umbar'), (0xE01E, 'ext. anga'), (0xE01F, 'ext. ungwe'),
    # additional
    (0xE020, 'rómen'), (0xE021, 'arda'), (0xE022, 'lambe'), (0xE023, 'alda'),
    (0xE024, 'silme'), (0xE025, 'silme nuquerna'), (0xE026, 'esse'), (0xE027, 'esse nuquerna'),
    (0xE028, 'hyarmen'), (0xE029, 'hwesta sindarinwa'), (0xE02A, 'yanta'), (0xE02B, 'úre'),
    (0xE02C, 'ára (длинный носитель)'), (0xE02D, 'halla'), (0xE02E, 'telco (короткий носитель)'),
    (0xE058, 'sa-rincë (концевой крюк)'),
]

# tehtar used on the machine: (name for doc, glyph name in font, kind, role)
MARKS = [
    ('a', 'uniE040', 'DA', 'три точки — a'),
    ('e', 'uniE046', 'DA', 'акут — e'),
    ('i', 'uniE044', 'DA', 'точка — i'),
    ('o', 'uniE04A', 'DA', 'правый завиток — o*'),
    ('u', 'uniE04C', 'DA', 'левый завиток — u*'),
    ('tilde', 'uniE052', 'DA', 'тильда сверху'),
    ('nas', 'uniE050', 'DL', 'носовая черта, узкая'),
    ('nasW', 'uniE050.wide', 'DL', 'носовая черта, широкая'),
    ('dotb', 'uniE045', 'DB', 'точка снизу'),
    ('ddotb', 'uniE043', 'DB', 'две точки снизу — y'),
    ('dbl', 'uniE051', 'DL', 'черта удвоения, узкая'),
    ('dblW', 'uniE051.wide', 'DL', 'черта удвоения, широкая'),
    ('dblL', 'uniE051.lambe', 'DX', 'черта удвоения для lambe/alda'),
    ('lsd', 'uniE07D', 'DB', 'метка младшего разряда'),
]

COMBOS = [  # long carrier + tehta
    ('ára+a', [0xE02C, 0xE040]), ('ára+e', [0xE02C, 0xE046]), ('ára+i', [0xE02C, 0xE044]),
    ('ára+o', [0xE02C, 0xE04A]), ('ára+u', [0xE02C, 0xE04C]),
]

NUMERALS = [(0xE070 + i, str(i)) for i in range(12)]

PUNCT = [
    (0xE060, 'пуста'), (0xE061, 'двойная пуста'), (0xE065, 'восклицательный'),
    (0xE066, 'вопросительный'), (0xE067, 'скобка'), (0xE06A, 'кавычка открыв.'),
    (0xE06B, 'кавычка закрыв.'),
]
