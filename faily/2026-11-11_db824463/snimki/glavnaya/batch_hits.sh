#!/bin/bash
# batch_hits.sh INFOBASE VERSION "QUERY" TOTAL [M] [FROM]
# Pass B: print the records found by QUERY (shown alone in Folio's "records with hits" view), with
# bitmaps on, M records per print job. The end of a job is found by counting changes of the status
# line ("Record: h/TOTAL") while Shift+Ctrl+Down extends the selection paragraph by paragraph.
# Folio is restarted every RESTART jobs (bitmap printing leaks) and after a crash; it goes back with
# Go To <hit number>. Files: OUT/h<first hit>.pdf
export DISPLAY=:99 WINEPREFIX=/home/claude/work/wp WINEDEBUG=-all
NFO=$1; VER=$2; Q=$3; TOTAL=$4; M=${5:-25}; FROM=${6:-1}; RESTART=${RESTART:-6}
S=/home/claude/scripts; OUT=/home/claude/work/print/$VER; mkdir -p $OUT
log() { echo "$(date +%T) $*" >> $OUT/log.txt; }
st() { import -window root -crop 140x15+64+979 rgb:- 2>/dev/null | md5sum | cut -c1-32; }
start() {
  pkill -f print_sel.sh; wineserver -k; sleep 2; $S/env_up.sh $NFO; $S/wait_idle.sh
  xdotool key F2; sleep 2; xdotool type --delay 25 "$Q"; sleep 3; xdotool key Return; sleep 4; $S/wait_idle.sh
  log "started, query $Q"
}
h=$FROM; jobs=0
start
while [ $h -le $TOTAL ]; do
  $S/goto_rec.sh $h; $S/wait_idle.sh
  want=$(( TOTAL - h + 1 < M ? TOTAL - h + 1 : M ))
  if [ $want -lt $M ]; then
    xdotool key shift+ctrl+End; $S/wait_idle.sh       # the last job: to the end
  else
    n=0; prev=$(st); guard=0
    while [ $n -lt $want ] && [ $guard -lt 4000 ]; do
      xdotool key shift+ctrl+Down; sleep 0.25; cur=$(st)
      if [ "$cur" != "$prev" ]; then n=$((n+1)); prev=$cur; fi
      guard=$((guard+1))
    done
  fi
  P=$($S/print_sel.sh 1440); [ -f "$P" ] || P="FAIL-${P:-none}"
  case "$P" in
    FAIL*) log "h$h $P"; start; jobs=0; continue;;
  esac
  f=$(printf "%s/h%05d.pdf" $OUT $h); mv "$P" $f
  log "h$h..$((h+want-1)) pages=$(pdfinfo $f | awk '/Pages/{print $2}') imgs=$(pdfimages -list $f 2>/dev/null | awk 'NR>2 && !($4==18 && $5==16)' | wc -l)"
  h=$((h+want)); jobs=$((jobs+1))
  if [ $jobs -ge $RESTART ]; then start; jobs=0; fi
done
log "END"
