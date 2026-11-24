#!/usr/bin/env python3
"""
Stage 2: architectural rewrite — three independent filters, overrides,
seeds-per-instance, reseed-all.

Replaces four regions in playground_v2.html (already CSS-cleaned by Stage 1):
  1. SVG-defs of #illumination-aged → three filters
  2. CSS bindings of filter to preview blocks → per-instance bindings
     + adds new CSS for seeds-block and overrides UI
  3. HTML panel <div class="pg-controls">...</div> → adds seeds-grid,
     overrides container, 'current' preset button
  4. <script>...</script> → full rewrite (CONTROLS, resolve, three filters,
     overrides logic, reseed)
"""
import re
import sys
from pathlib import Path


SRC = Path("/home/claude/playground_v2.html")
NEW_SVG_DEFS = Path("/home/claude/new_svg_defs.html").read_text(encoding="utf-8")
NEW_CSS = Path("/home/claude/new_css_bindings.css").read_text(encoding="utf-8")
NEW_HTML = Path("/home/claude/new_html_panel.html").read_text(encoding="utf-8")
NEW_JS = Path("/home/claude/new_js.js").read_text(encoding="utf-8")


def main():
    src = SRC.read_text(encoding="utf-8")
    original_lines = src.count("\n") + 1

    # -------------------------------------------------------------------
    # (1) Replace SVG-defs block.
    # Match: from <svg width="0" height="0" ...> with <defs> containing the
    # single #illumination-aged filter, through its closing </svg>.
    # The block is uniquely identifiable by 'filter id="illumination-aged"'
    # being inside a <svg width="0"> defs.
    # -------------------------------------------------------------------
    svg_defs_pattern = re.compile(
        r'<svg width="0" height="0"[^>]*>\s*\n\s*<defs>\s*\n.*?<filter id="illumination-aged"[^"].*?</filter>\s*\n\s*</defs>\s*\n</svg>',
        re.DOTALL,
    )
    matches = svg_defs_pattern.findall(src)
    if len(matches) != 1:
        print(f"ERROR: expected 1 SVG-defs filter block, found {len(matches)}")
        # Try a more lenient match — print debug info
        if len(matches) == 0:
            idx = src.find('filter id="illumination-aged"')
            print(f"  'filter id=\"illumination-aged\"' at byte {idx}")
            print(f"  Context: ...{src[max(0,idx-80):idx+120]}...")
        sys.exit(1)
    src = svg_defs_pattern.sub(NEW_SVG_DEFS, src, count=1)

    # -------------------------------------------------------------------
    # (2) Replace CSS filter bindings.
    # Replace the block from `/* ═════════════ ПРИМЕНЕНИЕ ФИЛЬТРА` comment
    # through the second filter-related rule (.pg-filter-off ...).
    # -------------------------------------------------------------------
    css_pattern = re.compile(
        r'/\* ═+ ПРИМЕНЕНИЕ ФИЛЬТРА ═+ \*/\s*\nbody\.pg-filter-on-css .*?filter: none !important;\s*\n\}',
        re.DOTALL,
    )
    matches = css_pattern.findall(src)
    if len(matches) != 1:
        print(f"ERROR: expected 1 CSS-binding block, found {len(matches)}")
        sys.exit(1)
    src = css_pattern.sub(NEW_CSS, src, count=1)

    # -------------------------------------------------------------------
    # (3) Replace HTML panel <div class="pg-controls">...</div>.
    # The block is the entire control panel inside pg-layout. We match
    # from `<div class="pg-controls">` through the closing `</div>` that
    # follows `<pre id="pg-dump-out"></pre>`.
    # Simpler match: from `<div class="pg-controls">` through the line
    # containing `<pre id="pg-dump-out">...</pre>` and then `  </div>\n</div>`.
    # -------------------------------------------------------------------
    html_pattern = re.compile(
        r'  <div class="pg-controls">.*?<pre id="pg-dump-out"></pre>\s*\n\s*</div>\s*\n\s*</div>',
        re.DOTALL,
    )
    matches = html_pattern.findall(src)
    if len(matches) != 1:
        print(f"ERROR: expected 1 pg-controls HTML block, found {len(matches)}")
        sys.exit(1)
    # NEW_HTML defines pg-controls (and closes one </div>), so the outer
    # pg-layout </div> needs to be preserved separately. We add it back.
    src = html_pattern.sub(NEW_HTML + "\n</div>", src, count=1)

    # -------------------------------------------------------------------
    # (4) Replace <script>...</script> block (the playground JS).
    # We identify the script block by its starting comment
    # "PLAYGROUND LIVE-UPDATE".
    # -------------------------------------------------------------------
    script_pattern = re.compile(
        r'<script>\s*\n/\* ═+\s*\n\s*PLAYGROUND LIVE-UPDATE.*?</script>',
        re.DOTALL,
    )
    matches = script_pattern.findall(src)
    if len(matches) != 1:
        print(f"ERROR: expected 1 playground <script> block, found {len(matches)}")
        sys.exit(1)
    new_script_block = f"<script>\n{NEW_JS}\n</script>"
    src = script_pattern.sub(lambda m: new_script_block, src, count=1)

    SRC.write_text(src, encoding="utf-8")
    new_lines = src.count("\n") + 1
    print(f"OK. Lines before: {original_lines}, after: {new_lines}")


if __name__ == "__main__":
    main()
