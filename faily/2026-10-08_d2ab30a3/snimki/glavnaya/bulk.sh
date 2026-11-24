#!/bin/bash
# Render word pages: run.sh WEBROOT OUTDIR MODE CODES
D=/tmp/claude-0/-home-claude/7173b229-aa2b-56f5-8c29-d70c9d405cc9/scratchpad/snap
run() {
  WEB=$1; OUT=$2; MODE=$3; CODES=$4
  CP="$D/bulk:$(dirname $(dirname $(dirname $WEB)))/build/classes:$(cut -d: -f2- /tmp/agent-review-a/h/cp.txt)"
  start=$(date +%s)
  java -Xmx3g -cp "$CP" Bulk "$WEB/config/query-configs/word-page.xq" "$CODES" "$OUT/pub-$MODE" $MODE 2 "$WEB" > "$OUT-pub-$MODE.log" 2>&1
  echo "$WEB pub=$MODE done in $(( $(date +%s) - start ))s, files=$(ls "$OUT/pub-$MODE" | wc -l), errors=$(wc -l < "$OUT/pub-$MODE/errors.txt")"
}
run /root/eldamo/src/main/webapp     $D/before/words true  $D/codes-sample.txt
run /root/eldamo-fix/src/main/webapp $D/after/words  true  $D/codes-sample.txt
run /root/eldamo-fix/src/main/webapp $D/after/words  false $D/codes.txt
echo ALL DONE
