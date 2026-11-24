"""Units and material constants of the physics checks (spec §3.2, §3.3, §3.5). The model works in mm; the checks work
in SI. Every conversion happens here."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL = os.path.join(ROOT, 'tools', 'model')
GEN = os.path.join(ROOT, 'gen', 'physics')
DATA = os.path.join(ROOT, 'data')
if MODEL not in sys.path:
    sys.path.insert(0, MODEL)

MM = 1e-3                 # m per mm
G = 9.81                  # m/s^2

# densities, g/cm3 (spec §3.3); 'пластик' (two cable sheaths?) and 'сталь+резина' are not in the spec's table:
# 'пластик' is taken as PETG, 'сталь+резина' as steel (a steel roller with a thin rubber skin)
RHO = {'PETG': 1.27, 'PETG серебристый': 1.27, 'сталь': 7.85, 'жесть': 7.85, 'алюминий': 2.70, 'Д16Т': 2.78,
       'латунь': 8.5, 'бронза': 8.8, 'резина': 1.2, 'ПВХ': 1.4, 'пластик': 1.27, 'сталь+резина': 7.85}
PROFILE_2020_KG_M = 0.5   # the 2020 profile is hollow; the model's mesh is a solid bar
PAPER_KG_M2 = 0.08
E_PETG = 2000e6
E_STEEL = 206000e6

# friction and restitution: (min, nom, max) (spec §3.5)
MU = {'petg-petg': (0.25, 0.35, 0.5), 'steel-petg': (0.15, 0.25, 0.35), 'steel-steel': (0.08, 0.12, 0.2),
      'brass-steel': (0.08, 0.12, 0.2), 'rubber': (0.6, 0.8, 1.0), 'linear': (0.002, 0.005, 0.01), 'ball608': (0.001, 0.002, 0.005)}
E_REST = {'petg-petg': (0.3, 0.5, 0.7), 'steel-petg': (0.3, 0.5, 0.7), 'steel-steel': (0.5, 0.7, 0.9), 'rubber': (0.1, 0.2, 0.4)}

METAL = {'сталь', 'жесть', 'алюминий', 'Д16Т', 'латунь', 'бронза', 'сталь+резина'}


def mu_pair(mat_a, mat_b, which=1):
    """Friction coefficient of a pair of materials: which = 0 min, 1 nom, 2 max."""
    a, b = mat_a in METAL, mat_b in METAL
    if 'резина' in (mat_a, mat_b):
        k = 'rubber'
    elif a and b:
        k = 'brass-steel' if {'латунь', 'бронза'} & {mat_a, mat_b} else 'steel-steel'
    elif a or b:
        k = 'steel-petg'
    else:
        k = 'petg-petg'
    return MU[k][which]


# allowable loads on fasteners, N (spec §4.7, guide values)
FASTENER_ALLOW = {'screw M3 + insert': 100.0, 'screw M3': 20.0, 'screw M5 + T-nut': 500.0, 'press': 5.0, 'circlip': 30.0}
