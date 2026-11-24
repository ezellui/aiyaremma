#!/bin/bash
# Snapshot every non-word page over HTTP in dev and pub mode.
# usage: snap_http.sh OUTDIR
OUT=$1; mkdir -p "$OUT/dev" "$OUT/pub"
LIST=/tmp/claude-0/-home-claude/7173b229-aa2b-56f5-8c29-d70c9d405cc9/scratchpad/snap/urls.txt
if [ ! -f $LIST ]; then
  awk '{print $1}' /tmp/agent-review-b/urls2.txt | sed 's#^/eldamo/content/##' > $LIST
  grep '^ref-' /tmp/refpages.txt | sed 's#^#references/#' >> $LIST
fi
fetch() {
  mode=$1; u=$2; out=$3
  if [ "$mode" = pub ]; then base=http://localhost:8080/eldamo/pub/content; else base=http://localhost:8080/eldamo/content; fi
  f="$out/$mode/$(echo "$u" | tr '/?&=' '____')"
  code=$(curl -s --noproxy '*' --max-time 600 -o "$f" -w "%{http_code}" "$base/$u")
  echo "$code $u" >> "$out/$mode.status"
}
export -f fetch
rm -f "$OUT"/dev.status "$OUT"/pub.status
# skip the slow/full-dump endpoints in pub mode
xargs -P 4 -I{} bash -c 'fetch dev "{}" '"$OUT" < $LIST
grep -v -E '^(csv|data-model|test|valid|etym|sindarin)' $LIST | xargs -P 4 -I{} bash -c 'fetch pub "{}" '"$OUT"
sort -k2 -o "$OUT/dev.status" "$OUT/dev.status"; sort -k2 -o "$OUT/pub.status" "$OUT/pub.status"
echo "dev: $(wc -l < $OUT/dev.status) pages, non-200: $(grep -vc '^200' $OUT/dev.status)"
echo "pub: $(wc -l < $OUT/pub.status) pages, non-200: $(grep -vc '^200' $OUT/pub.status)"
