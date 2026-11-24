#!/usr/bin/env python3
"""
Stage 1: CSS dead-block removal.

Removes line ranges that contain only CSS rules selecting unused classes,
based on the section-by-section audit from the spec.
"""

# Inclusive line ranges (1-indexed) to remove.
# Order: file is processed line-by-line; ranges are validated as non-overlapping.
RANGES_TO_REMOVE = [
    (225, 238,   ".spread block (РАЗВОРОТ)"),
    (271, 289,   ".folio.page-verso / .folio.page-recto (need only base .folio)"),
    (483, 540,   "GUTTER section (.gutter and its pseudo-elements)"),
    (559, 610,   ".doc-title / .doc-subtitle / .rubric* / .section-break-soft.s1..s4"),
    (656, 656,   "p.no-indent (single line)"),
    (864, 1066,  "МАРГИНАЛИИ + Коеман + Финан + поздняя рука + чернильные кляксы"),
    (1068, 1132, "FOLIO NUMBERS + FOLIATOR HAND + фолиация алхимических листов"),
    (1133, 1276, "CATCHWORDS + INCIPIT FOLIO + UNCIAL PASSAGES"),
    (1277, 1376, "@media узкоэкранная адаптация + PERF-MOBILE (only deals with unused classes)"),
    (1383, 1593, "PATCH KELLS-NOTORN + WORD-SPACE JITTER + RUNT-HANG + выключатели jitter"),
    (1594, 1918, "PATCH TR + PATCH TR3 (двухслойная маргиналия + visually-hidden source-span)"),
    (1919, 2198, "DEDICATORIA + ПАЛЕОГРАФИЧЕСКИЕ АББРЕВИАТУРЫ"),
    (2283, 2323, ".parch-h4 / .parch-h5 / .parch-h6 (keep only h1..h3)"),
    (2325, 2544, "flesh-варианты пергамена (used only hair)"),
    (2606, 2814, "PATCH ALCH + седьмой пергамен hair/flesh + шов/guard"),
    (2815, 3113, "INLINE-RASURA + INTERLINEAR ALCHEMICA + ALCH-MARK"),
    (3114, 3255, "PATCH PROV-* + 6 кодикологических штампов"),
]


def main():
    src_path = "/home/claude/playground_v2.html"
    dst_path = "/home/claude/playground_v2.html"  # in-place

    # Validate ranges
    for i in range(1, len(RANGES_TO_REMOVE)):
        prev_end = RANGES_TO_REMOVE[i - 1][1]
        cur_start = RANGES_TO_REMOVE[i][0]
        if cur_start <= prev_end:
            raise SystemExit(
                f"Overlapping or out-of-order range at index {i}: "
                f"prev ends {prev_end}, cur starts {cur_start}"
            )

    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_before = len(lines)
    removed_total = 0

    # Build set of line numbers to skip (1-indexed)
    skip = set()
    for start, end, _label in RANGES_TO_REMOVE:
        for n in range(start, end + 1):
            skip.add(n)

    out = []
    for i, line in enumerate(lines, start=1):
        if i in skip:
            removed_total += 1
            continue
        out.append(line)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(out)

    print(f"Total lines before: {total_before}")
    print(f"Total lines after:  {len(out)}")
    print(f"Removed:            {removed_total}")
    print()
    print("Removed blocks (line ranges in ORIGINAL file numbering):")
    for start, end, label in RANGES_TO_REMOVE:
        n = end - start + 1
        print(f"  {start:5d}–{end:5d}  ({n:4d} lines)  {label}")


if __name__ == "__main__":
    main()
