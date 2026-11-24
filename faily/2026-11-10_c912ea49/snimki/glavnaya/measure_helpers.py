def top_anchor(font, glyph, adv):
    """x of the top mark anchor of `glyph` (lookup 6, class 1) or adv/2 if absent."""
    gpos = font['GPOS'].table
    lk = gpos.LookupList.Lookup[6]
    for st in lk.SubTable:
        cov = st.BaseCoverage.glyphs
        if glyph in cov:
            rec = st.BaseArray.BaseRecord[cov.index(glyph)]
            if len(rec.BaseAnchor) > 1 and rec.BaseAnchor[1] is not None:
                return rec.BaseAnchor[1].XCoordinate
    return adv / 2
