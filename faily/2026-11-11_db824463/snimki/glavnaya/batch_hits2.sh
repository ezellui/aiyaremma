#!/bin/bash
# batch_hits2.sh INFOBASE VERSION "QUERY" TOTAL [M] [FROM]
# Pass B with adaptive job size. Folio's "records with hits" view shows only the records found by
# QUERY; jobs of up to M records are printed to PostScript (print_ps.sh), the empty palettes are
# replaced (ps_fix.py) and the PDF goes to print/VERSION_B/hNNNNN.pdf.
# Some records crash Folio deterministically while their bitmap is printed: after a crash the job is
# halved and retried; a single record that still crashes is logged UNPRINTABLE and skipped. After a
# success the job size doubles back towards M. Without FROM the run resumes after the last logged job.
export DISPLAY=${DISPLAY:-:97} WINEPREFIX=${WINEPREFIX:-/home/claude/work/wp3} WINEDEBUG=-all
export NFO=$1; VER=$2; Q=$3; TOTAL=$4; MMAX=${5:-20}; RESTART=${RESTART:-8}
S=/home/claude/scripts; OUT=/home/claude/work/print/${VER}_B; PS=/root/PS_$VER; mkdir -p $OUT $PS
log() { echo "$(date +%T) $*" >> $OUT/log.txt; }
st() { import -window root -crop 140x15+64+979 rgb:- 2>/dev/null | md5sum | cut -c1-32; }
start() {
  wineserver -k 2>/dev/null; sleep 2; $S/env_up.sh $NFO; $S/wait_idle.sh
  sleep 5; xdotool key F2; sleep 3; xdotool type --delay 25 "$Q"; sleep 3; xdotool key Return
  sleep 6; $S/wait_idle.sh; sleep 3
  log "started"
}
if [ -n "$6" ]; then h=$6
else  # resume: the hit after the last finished or skipped job
  h=$(grep -oE 'h[0-9]+\.\.[0-9]+ (pages|UNPRINTABLE)' $OUT/log.txt 2>/dev/null | tail -1 | sed -E 's/h[0-9]+\.\.([0-9]+).*/\1/')
  h=$(( ${h:-0} + 1 ))
fi
M=$MMAX; jobs=0
start
while [ $h -le $TOTAL ]; do
  want=$(( TOTAL - h + 1 < M ? TOTAL - h + 1 : M ))
  $S/goto_rec.sh $h; $S/wait_idle.sh
  if [ $((h + want - 1)) -ge $TOTAL ]; then
    xdotool key shift+ctrl+End; $S/wait_idle.sh
  else
    n=0; prev=$(st); guard=0
    while [ $n -lt $want ] && [ $guard -lt 4000 ]; do
      xdotool key shift+ctrl+Down; sleep 0.25; cur=$(st)
      [ "$cur" != "$prev" ] && { n=$((n+1)); prev=$cur; }
      guard=$((guard+1))
    done
  fi
  f=$(printf "%s/h%05d.pdf" $OUT $h); ps=$PS/$(basename $f .pdf).ps
  P=$($S/print_ps.sh $ps 1440)
  if [ "$P" != "$ps" ]; then
    rm -f $ps
    if [ $want -le 1 ]; then
      log "h$h..$h UNPRINTABLE ($P)"; h=$((h+1)); M=$MMAX
    else
      M=$(( want / 2 )); log "h$h ($want) $P -> retry with $M"
    fi
    start; jobs=0; continue
  fi
  python3 $S/ps_fix.py $ps $f >/dev/null 2>>$OUT/err.txt && gzip -f $ps
  log "h$h..$((h+want-1)) pages=$(pdfinfo $f 2>/dev/null | awk '/Pages/{print $2}') imgs=$(pdfimages -list $f 2>/dev/null | awk 'NR>2 && !($4==18 && $5==16)' | wc -l)"
  h=$((h+want)); jobs=$((jobs+1))
  [ $M -lt $MMAX ] && M=$(( M * 2 > MMAX ? MMAX : M * 2 ))
  if [ $jobs -ge $RESTART ]; then start; jobs=0; fi
done
log "END"
