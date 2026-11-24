"""Print an HTML page as readable text: block elements on their own lines, links kept as text."""
import html
import re
import sys

s = open(sys.argv[1], encoding='utf-8').read()
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
s = re.sub(r'<script.*?</script>|<style.*?</style>|<head>.*?</head>', '', s, flags=re.S)
s = re.sub(r'\s+', ' ', s)
s = re.sub(r'<(?:/?(?:p|div|li|tr|h1|h2|h3|dt|dd|hr|table|ul|dl|br)\b[^>]*)>', '\n', s)
s = re.sub(r'</t[dh]>', ' | ', s)
s = re.sub(r'<[^>]+>', '', s)
s = html.unescape(s)
lines = [l.strip() for l in s.split('\n') if l.strip()]
print('\n'.join(lines)[:limit])
