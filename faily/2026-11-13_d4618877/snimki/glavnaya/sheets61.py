"""Контактные листы решений 1961 г. (как в HWPh): out/proof/regions_de.html, regions_en.html.

Строка листа — положение, где детектор (regions61.py) нашёл подозрительное место или где
стоит решение (decisions61.py). Слева — вырезка скана (всё положение), справа — итоговый текст,
отрисованный как в читалке (md.js + KaTeX), и таблица решений «было → стало» с видом решения
(text / sym / tex / texd / fig / emph). Отметки «верно» / «неверно» и заметки хранятся в браузере
и выгружаются в JSON — его можно превратить в новые строки decisions61.py.

    python3 sheets61.py ../ocr lp1961.json ../out/proof
(запускать после build_all.py: нужны pre61_*.json и norm_*.json)
"""
import json, os, re, sys, html, shutil
import decisions61
from PIL import Image

OCR, LP, OUT = sys.argv[1:4]
W = os.path.dirname(os.path.abspath(__file__))
lp = json.load(open(LP))
canon = json.load(open(f"{W}/canon.json"))
regs = json.load(open(f"{W}/regions61.json"))
os.makedirs(f"{OUT}/sheet", exist_ok=True)
for sub in ("katex",):
    shutil.copytree(f"{W}/reader/{sub}", f"{OUT}/{sub}", dirs_exist_ok=True)
shutil.copy(f"{W}/reader/js/md.js", f"{OUT}/md.js")
os.makedirs(f"{OUT}/figs", exist_ok=True)
for f in os.listdir(f"{W}/figs"):
    if "1961" in f:
        shutil.copy(f"{W}/figs/{f}", f"{OUT}/figs/{f}")
TOP, BOTTOM = 200, 2700
NORM = {"de": "tlp_de_1961", "en": "tlp_en_1961_ogden"}


def crop(lang, num):
    i = canon.index(num)
    nxt = canon[i + 1] if i + 1 < len(canon) else None
    pg, y = lp[lang]["loc"][num]
    pieces = []
    if nxt and lp[lang]["loc"][nxt][0] == pg:
        pieces.append((pg, y - 25, lp[lang]["loc"][nxt][1] - 10))
    else:
        pieces.append((pg, y - 25, BOTTOM))
        if nxt and lp[lang]["loc"][nxt][0] == pg + 2 and lp[lang]["loc"][nxt][1] - TOP > 40:
            pieces.append((pg + 2, TOP, lp[lang]["loc"][nxt][1] - 10))
    ims = []
    for p, a, b in pieces:
        im = Image.open(f"{OCR}/pg-{p:03d}.pgm")
        ims.append(im.crop((60, max(0, a), im.width - 60, min(im.height, b))))
    w = max(i.width for i in ims)
    out = Image.new("L", (w, sum(i.height for i in ims) + 12 * (len(ims) - 1)), 255)
    yy = 0
    for im in ims:
        out.paste(im, (0, yy)); yy += im.height + 12
    out = out.resize((w * 55 // 100, out.height * 55 // 100)).point(lambda v: 255 if v > 190 else v)
    name = f"{lang}-{num}.png"
    out.save(f"{OUT}/sheet/{name}", optimize=True)
    return name


def old_str(o):
    return "(положение целиком)" if isinstance(o, re.Pattern) and o.pattern == r"\A.*\Z" else \
        ("/" + o.pattern + "/" if isinstance(o, re.Pattern) else o)


for lang, ed in (("de", decisions61.DE), ("en", decisions61.EN)):
    pre = json.load(open(f"{W}/pre61_{lang}.json"))
    post = json.load(open(f"{W}/norm_{NORM[lang]}.json"))["props"]
    dec = {}
    for e, num, old, new, kind in decisions61.D:
        if e == ed:
            dec.setdefault(num, []).append({"old": old_str(old), "new": new, "kind": kind})
    why = {}
    for r in regs:
        if r["lang"] == lang:
            why.setdefault(r["num"], set()).update(r["why"])
    nums = [n for n in canon if n in dec or n in why or pre[n] != post[n]]
    rows = []
    for n in nums:
        rows.append({"num": n, "img": crop(lang, n), "text": post[n], "dec": dec.get(n, []),
                     "why": sorted(why.get(n, [])), "auto": pre[n] != post[n] and n not in dec})
    title = {"de": "1961 — deutscher Text", "en": "1961 — Ogden’s English"}[lang]
    page = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Контактные листы 1961 ({lang}) — ЛФТ</title>
<link rel="stylesheet" href="katex/katex.min.css"><script src="katex/katex.min.js"></script><script src="md.js"></script>
<style>
body{{margin:0;font:15px/1.5 Georgia,serif;background:#F2F3EF;color:#1D2320}}
header{{position:sticky;top:0;background:#2E5A43;color:#F2F3EF;padding:8px 16px;font:13px system-ui,sans-serif;display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:5}}
header button,header select{{font:inherit}}
.row{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;padding:12px 16px;border-bottom:1px solid #CDD2CA}}
.row.ok{{opacity:.5}} .row.bad{{background:#f7e4e1}}
.scan img{{max-width:100%;border:1px solid #CDD2CA;background:#fff}}
.meta{{font:12px system-ui,sans-serif;color:#56605A;margin-bottom:4px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.num{{font-weight:700;color:#8A6A22;font-size:14px}}
.tag{{border:1px solid #CDD2CA;border-radius:3px;padding:0 4px}}
.text p{{margin:.3em 0}} .text table{{border-collapse:collapse;font-size:13px}} .text td,.text th{{border:1px solid #CDD2CA;padding:1px 5px}}
.text img{{max-width:100%;background:#fff}}
table.dec{{border-collapse:collapse;font:12px/1.35 system-ui,sans-serif;margin:6px 0;width:100%}}
table.dec td{{border-top:1px solid #CDD2CA;padding:2px 4px;vertical-align:top}}
table.dec td.o{{color:#a33;text-decoration:line-through;max-width:40ch;overflow-wrap:anywhere}}
table.dec td.n{{color:#2E5A43;overflow-wrap:anywhere}}
.k{{font-weight:700;color:#357}}
textarea{{width:100%;font:12px system-ui,sans-serif;min-height:2.2em}}
</style></head><body>
<header><b>Контактные листы: {html.escape(title)}</b><span id="cnt"></span>
<select id="only"><option value="">все</option><option value="dec">с решениями</option><option value="auto">только общие правила</option>
<option value="tex">tex</option><option value="sym">sym</option><option value="fig">fig</option><option value="text">text</option></select>
<label><input type="checkbox" id="hide"> скрыть отмеченные</label>
<button id="exp">выгрузить отметки (JSON)</button></header>
<main id="rows"></main>
<script>
const ROWS = {json.dumps(rows, ensure_ascii=False)};
const ED = {json.dumps(ed)}, KEY = 'tlp-sheet-' + ED;
let st = {{}}; try {{ st = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (e) {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(st)); }} catch (e) {{}} }};
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
function draw() {{
  const only = document.getElementById('only').value, hide = document.getElementById('hide').checked;
  let n = 0, ok = 0, bad = 0;
  document.getElementById('rows').innerHTML = ROWS.map(r => {{
    const s = st[r.num] || {{}}; if (s.v === 'ok') ok++; if (s.v === 'bad') bad++;
    if (hide && s.v) return '';
    if (only === 'dec' && !r.dec.length) return '';
    if (only === 'auto' && !r.auto) return '';
    if (['tex', 'sym', 'fig', 'text'].includes(only) && !r.dec.some(d => d.kind === only || (only === 'tex' && d.kind === 'texd'))) return '';
    n++;
    const body = TLPmd.render(r.text, {{fig: name => `<img src="figs/${{ED}}-${{name}}.svg" onerror="this.onerror=null;this.src='figs/${{ED}}-${{name}}.png'" alt="">`}});
    const dec = r.dec.length ? '<table class="dec">' + r.dec.map(d => `<tr><td class="k">${{d.kind}}</td><td class="o">${{esc(d.old)}}</td><td class="n">${{esc(d.new)}}</td></tr>`).join('') + '</table>' : '';
    return `<div class="row ${{s.v || ''}}"><div class="scan"><img loading="lazy" src="sheet/${{r.img}}"></div><div>
      <div class="meta"><span class="num">${{r.num}}</span>${{r.why.map(w => `<span class="tag">${{w}}</span>`).join('')}}
      ${{r.auto ? '<span class="tag">общие правила</span>' : ''}}
      <label><input type="radio" name="v${{r.num}}" data-v="ok" data-n="${{r.num}}" ${{s.v === 'ok' ? 'checked' : ''}}> верно</label>
      <label><input type="radio" name="v${{r.num}}" data-v="bad" data-n="${{r.num}}" ${{s.v === 'bad' ? 'checked' : ''}}> неверно</label></div>
      <div class="text">${{body}}</div>${{dec}}
      <textarea data-note="${{r.num}}" placeholder="что не так / чем заменить">${{esc(s.note || '')}}</textarea></div></div>`;
  }}).join('');
  document.getElementById('cnt').textContent = `показано ${{n}} из ${{ROWS.length}} · верно ${{ok}} · неверно ${{bad}}`;
}}
document.addEventListener('change', e => {{
  const t = e.target;
  if (t.dataset.v) {{ (st[t.dataset.n] = st[t.dataset.n] || {{}}).v = t.dataset.v; save(); draw(); }}
  else if (t.dataset.note) {{ (st[t.dataset.note] = st[t.dataset.note] || {{}}).note = t.value; save(); }}
  else draw();
}});
document.getElementById('exp').onclick = () => {{
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify({{edition: ED, marks: st}}, null, 1)], {{type: 'application/json'}}));
  a.download = `sheet-${{ED}}.json`; a.click();
}};
draw();
</script></body></html>"""
    open(f"{OUT}/regions_{lang}.html", "w").write(page)
    kinds = {}
    for v in dec.values():
        for d in v:
            kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
    print(lang, "строк:", len(rows), "с решениями:", len(dec), "виды:", kinds,
          "только общие правила:", sum(r["auto"] for r in rows))
