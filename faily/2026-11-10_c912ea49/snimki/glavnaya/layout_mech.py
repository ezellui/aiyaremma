# Keyboard layout of the mechanical machine (TPM-2).
# Rule: a key lever is either wholly dead (both slugs are marks on a sledge) or wholly advancing.
# Sledge A carries marks above, sledge B marks below.
ROWS = [
    [(0xE071, 0xE07B), (0xE072, 0xE060), (0xE073, 0xE061), (0xE074, 0xE065), (0xE075, 0xE066),
     (0xE076, 0xE067), (0xE077, 0xE06A), (0xE078, 0xE06B), (0xE079, 0xE02D), (0xE070, 0xE01E),
     (0xE07A, 0xE01F)],
    [(0xE000, 0xE018), (0xE001, 0xE019), (0xE002, 0xE01A), (0xE003, 0xE01B), (0xE004, 0xE01C),
     (0xE005, 0xE01D), (0xE00E, 0xE006), (0xE00C, 0xE007), (0xE00D, 0xE00F), (0xE020, 0xE021),
     (0xE022, 0xE023)],
    [(0xE008, 0xE026), (0xE009, 0xE029), (0xE00A, 0xE00B), (0xE010, 0xE012), (0xE011, 0xE013),
     ('mark:i', 'mark:tilde'), ('mark:a', 'mark:nas'), ('mark:e', 'mark:nasW'),
     ('mark:o', None), ('mark:u', None), ('mark:ddotb', 'mark:dotb')],
    [(0xE014, 0xE02B), (0xE015, 0xE017), (0xE024, 0xE058), (0xE025, 0xE027), (0xE016, 'combo:ára+a'),
     (0xE02A, 'combo:ára+e'), (0xE028, 'combo:ára+i'), (0xE02E, 'combo:ára+o'), (0xE02C, 'combo:ára+u'),
     ('mark:dbl', 'mark:dblW'), ('mark:dblL', 'mark:lsd')],
]
LEGENDS = ['1234567890-', 'qwertyuiop[', 'asdfghjkl;\'', 'zxcvbnm,./\\']
# which sledge carries a dead key: by position (row, col)
SLEDGE = {(2, 5): 'A', (2, 6): 'A', (2, 7): 'A', (2, 8): 'A', (2, 9): 'A',
          (2, 10): 'B', (3, 9): 'B', (3, 10): 'B'}
