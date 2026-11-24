#!/bin/bash
# print_ps.sh OUT.ps [timeout-steps]
# Print the current selection with "Print to file": Wine's PostScript driver writes the job as it is
# (pass B needs this: through CUPS the bitmaps arrive with an empty palette and are lost; in the raw
# PostScript only the palette is empty, the pixel indices are intact). Prints OUT.ps or FAIL-*.
export DISPLAY=${DISPLAY:-:99}
OUT=$1; STEPS=${2:-720}
rm -f "$OUT"
alive() { pgrep -f "BVIEWS.EXE ${NFO:-NORM.NFO}" >/dev/null && ! xdotool search --name 'Program Error|Wine Debugger' >/dev/null 2>&1; }
win() {   # window id by exact title and width test
  for w in $(xdotool search --onlyvisible --name "$1" 2>/dev/null); do
    W=$(xdotool getwindowgeometry --shell $w | grep WIDTH | cut -d= -f2); [ "$W" $2 ] && { echo $w; return; }; done; }
dlg() { win '^Print$' '-gt 300'; }
prog() { win '^Print$' '-le 300'; }
cpu() { local pid=$(pgrep -f "BVIEWS.EXE ${NFO:-NORM.NFO}" | head -1); [ -n "$pid" ] && awk '{print $14+$15}' /proc/$pid/stat 2>/dev/null || echo 0; }
for try in 1 2 3; do
  [ -n "$(dlg)" ] && break
  xdotool key alt+f; sleep 0.8; xdotool key p
  for i in $(seq 1 40); do sleep 0.5; [ -n "$(dlg)" ] && break; done
done
d=$(dlg); [ -z "$d" ] && { xdotool key Escape; echo FAIL-nodialog; exit 1; }
eval $(xdotool getwindowgeometry --shell $d)
xdotool key alt+${RANGE:-s}; sleep 0.4
xdotool mousemove $((X + 284)) $((Y + 72)) click 1; sleep 0.6       # [x] Print to file
xdotool key Return
# the "Output File Name" prompt (a small window with an edit field)
for i in $(seq 1 60); do
  sleep 0.5
  [ -z "$(dlg)" ] && f=$(xdotool getactivewindow 2>/dev/null) && [ "$(xdotool getwindowname $f)" != "Folio Bound VIEWS" ] && break
done
WIN=$(echo "$OUT" | sed 's#/#\\#g'); xdotool type --delay 15 "Z:$WIN"; sleep 0.3; xdotool key Return
for i in $(seq 1 20); do sleep 1; [ -f "$OUT" ] && break; done
[ -f "$OUT" ] || { alive || { echo FAIL-crash; exit 1; }; echo FAIL-nofile; exit 1; }
# done when the progress box is gone, Folio is idle and the file has stopped growing
s=-1; quiet=0
for i in $(seq 1 $STEPS); do
  sleep 5
  alive || { echo FAIL-crash; exit 1; }
  n=$(stat -c%s "$OUT"); c=$(cpu)
  if [ -z "$(prog)" ] && [ "$n" = "$s" ] && [ $((c - ${c0:-0})) -lt 20 ]; then quiet=$((quiet+1)); else quiet=0; fi
  s=$n; c0=$c
  [ $quiet -ge 2 ] && { tail -c 200 "$OUT" | grep -q '%%EOF' && { echo "$OUT"; exit 0; }; }
  [ $quiet -ge 12 ] && { echo FAIL-noeof; exit 1; }
done
echo FAIL-timeout; exit 1
