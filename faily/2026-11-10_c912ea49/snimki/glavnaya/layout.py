# Keyboard layout: 4 rows x 11 keys. Each key = (lower, upper).
# Items: hex codepoint int (tengwa/numeral/punct), 'combo:<name>', 'mark:<key>', None (reserve).
T = lambda x: x
ROWS = [
    # number row: numerals lower, punctuation upper
    [(0xE071, 0xE07B), (0xE072, 0xE060), (0xE073, 0xE061), (0xE074, 0xE065), (0xE075, 0xE066),
     (0xE076, 0xE067), (0xE077, 0xE06A), (0xE078, 0xE06B), (0xE079, 'mark:lsd'), (0xE070, None),
     (0xE07A, None)],
    # upper letter row: tyeller 1-2 and 4, extended stems on shift
    [(0xE000, 0xE018), (0xE001, 0xE019), (0xE002, 0xE01A), (0xE003, 0xE01B), (0xE004, 0xE01C),
     (0xE005, 0xE01D), (0xE00E, 0xE006), (0xE00C, 0xE01E), (0xE00D, 0xE01F), (0xE020, 0xE021),
     (0xE022, 0xE023)],
    # home row: consonants left, vowel tehtar right (shift = long vowel on ára)
    [(0xE008, 0xE026), (0xE009, 0xE029), (0xE00A, 0xE00B), (0xE010, 0xE012), (0xE011, 0xE013),
     ('mark:i', 'combo:ára+i'), ('mark:a', 'combo:ára+a'), ('mark:e', 'combo:ára+e'),
     ('mark:o', 'combo:ára+o'), ('mark:u', 'combo:ára+u'), ('mark:ddotb', 'mark:dotb')],
    # bottom row
    [(0xE014, 0xE007), (0xE015, 0xE017), (0xE016, 0xE02B), (0xE024, 0xE058), (0xE025, 0xE027),
     (0xE028, 0xE02D), (0xE02A, 0xE00F), (0xE02E, 'mark:tilde'), (0xE02C, 'mark:dblL'),
     ('mark:dbl', 'mark:dblW'), ('mark:nas', 'mark:nasW')],
]
# QWERTY legends of the physical positions (for orientation only)
LEGENDS = ['1234567890-', 'qwertyuiop[', 'asdfghjkl;\'', 'zxcvbnm,./\\']
