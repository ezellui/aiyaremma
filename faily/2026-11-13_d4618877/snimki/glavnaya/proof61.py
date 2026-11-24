"""Листы вычитки издания 1961 г. (аналог контактных листов HWPh).

Для каждого положения, которое стоит проверить, — кусок скана слева и наш текст справа,
отрисованный так же, как в читалке (md.js + KaTeX). Подозрительные слова подсвечены.
Отметки «проверено» и заметки хранятся в браузере и выгружаются в JSON.

Кого показывать: (1) слова, прочитанные двумя OCR по-разному и отсутствующие в словаре
(witness61.json); (2) формулы и логические знаки; (3) положения с ручными правками (fixes.py).
Ключ --all показывает все 526 положений.

    python3 proof61.py ../ocr lp1961.json ../out/proof [--all]
"""
import json, os, re, sys, unicodedata, html, shutil
from PIL import Image
import fixes

OCR, LP, OUT = sys.argv[1:4]
ALL = "--all" in sys.argv
W = os.path.dirname(os.path.abspath(__file__))
lp = json.load(open(LP))
wit = json.load(open(f"{W}/witness61.json"))
canon = json.load(open(f"{W}/canon.json"))
os.makedirs(f"{OUT}/crops", exist_ok=True)
shutil.copytree(f"{W}/reader/katex", f"{OUT}/katex", dirs_exist_ok=True)
shutil.copy(f"{W}/reader/md.js", f"{OUT}/md.js")
WORD = re.compile(r"[^\W_]+")
FORMULA = re.compile(r"[~⊃∨≡|ξηΩ=]|\$|```|\(p|p\)|\bp\s*\.|\bq\b")
TOP, BOTTOM = 200, 2700        # поле текста на странице скана (пиксели при 300 dpi)


def fold(s):
    s = unicodedata.normalize("NFD", s.replace("ß", "ss"))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def crop(lang, num, nxt):
    """Кусок скана от начала положения до начала следующего (с переходом на след. страницу)."""
    pg, y = lp[lang]["loc"][num]
    pieces = []
    if nxt and lp[lang]["loc"][nxt][0] == pg:
        pieces.append((pg, y - 25, lp[lang]["loc"][nxt][1] - 10))
    else:
        pieces.append((pg, y - 25, BOTTOM))
        if nxt and lp[lang]["loc"][nxt][0] == pg + 2:
            y2 = lp[lang]["loc"][nxt][1]
            if y2 - TOP > 40:
                pieces.append((pg + 2, TOP, y2 - 10))
    ims = []
    for p, a, b in pieces:
        im = Image.open(f"{OCR}/pg-{p:03d}.pgm")
        ims.append(im.crop((60, max(0, a), im.width - 60, min(im.height, b))))
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + 12 * (len(ims) - 1)
    out = Image.new("L", (w, h), 255)
    yy = 0
    for i in ims:
        out.paste(i, (0, yy)); yy += i.height + 12
    out = out.resize((w * 45 // 100, h * 45 // 100))
    out = out.point(lambda v: 255 if v > 190 else v)
    name = f"{lang}-{num}.png"
    out.save(f"{OUT}/crops/{name}", optimize=True)
    return name


for lang, norm, ed in (("de", "tlp_de_1961", "de1961"), ("en", "tlp_en_1961_ogden", "en1961")):
    props = json.load(open(f"{W}/norm_{norm}.json"))["props"]
    figs = sorted(f for f in os.listdir(f"{W}/figs") if f.startswith(ed))
    os.makedirs(f"{OUT}/figs", exist_ok=True)
    for f in figs:
        shutil.copy(f"{W}/figs/{f}", f"{OUT}/figs/{f}")
    touched = {n for e, n, o, w in fixes.FIXES if e == ed}
    rows = []
    for i, num in enumerate(canon):
        text = props[num]
        pg = lp[lang]["loc"][num][0]
        bad = set(wit[lang]["bad_by_page"].get(str(pg), [])) | set(wit[lang]["bad_by_page"].get(str(pg + 2), []))
        sus = sorted({w for w in WORD.findall(re.sub(r"```.*?```|\$[^$]*\$", "", text, flags=re.S)) if fold(w) in bad})
        reasons = []
        if sus:
            reasons.append("ocr")
        if FORMULA.search(text):
            reasons.append("formula")
        if num in touched:
            reasons.append("fixed")
        if not reasons and not ALL:
            continue
        nxt = canon[i + 1] if i + 1 < len(canon) else None
        rows.append({"num": num, "page": pg, "img": crop(lang, num, nxt), "text": text,
                     "sus": sus, "why": reasons})
    title = {"de": "Vorwort-Ausgabe 1961 — deutscher Text", "en": "1961 — Ogden’s English"}[lang]
    page = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Вычитка 1961 ({lang}) — ЛФТ</title>
<link rel="stylesheet" href="katex/katex.min.css"><script src="katex/katex.min.js"></script><script src="md.js"></script>
<style>
body{{margin:0;font:15px/1.5 Georgia,serif;background:#F2F3EF;color:#1D2320}}
header{{position:sticky;top:0;background:#2E5A43;color:#F2F3EF;padding:8px 16px;font-family:system-ui,sans-serif;font-size:13px;display:flex;gap:14px;align-items:center;z-index:5}}
header button,header select{{font:inherit}}
.row{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;padding:12px 16px;border-bottom:1px solid #CDD2CA}}
.row.done{{opacity:.45}}
.scan img{{max-width:100%;border:1px solid #CDD2CA;background:#fff}}
.meta{{font-family:system-ui,sans-serif;font-size:12px;color:#56605A;margin-bottom:4px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.num{{font-weight:700;color:#8A6A22;font-size:14px}}
.tag{{border:1px solid #CDD2CA;border-radius:3px;padding:0 4px}}
.tag.ocr{{border-color:#c66;color:#a33}} .tag.formula{{border-color:#68a;color:#357}} .tag.fixed{{border-color:#8A6A22;color:#8A6A22}}
.text p{{margin:.3em 0}} mark{{background:#f3c6c0}}
.text table{{border-collapse:collapse;font-size:13px}} .text td,.text th{{border:1px solid #CDD2CA;padding:1px 5px}}
.text figure img{{max-width:100%;background:#fff}} pre.scheme{{font-size:12px;overflow:auto}}
textarea{{width:100%;font:12px system-ui,sans-serif;min-height:2.2em}}
</style></head><body>
<header><b>Вычитка: {html.escape(title)}</b><span id="cnt"></span>
<label><input type="checkbox" id="hide"> скрыть проверенные</label>
<select id="only"><option value="">все причины</option><option value="ocr">расхождение двух OCR</option>
<option value="formula">формулы и знаки</option><option value="fixed">ручные правки</option></select>
<button id="exp">выгрузить отметки (JSON)</button></header>
<main id="rows"></main>
<script>
const ROWS = {json.dumps(rows, ensure_ascii=False)};
const LANG = {json.dumps(lang)}, ED = {json.dumps(ed)};
const KEY = 'tlp-proof-' + LANG;
let st = {{}}; try {{ st = JSON.parse(localStorage.getItem(KEY) || '{{}}'); }} catch (e) {{}}
const save = () => {{ try {{ localStorage.setItem(KEY, JSON.stringify(st)); }} catch (e) {{}} }};
const WHY = {{ocr: 'два OCR расходятся', formula: 'формулы', fixed: 'ручная правка'}};
function mark(html, words) {{
  if (!words.length) return html;
  const rx = new RegExp('(?<![\\\\p{{L}}\\\\d])(' + words.map(w => w.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&')).join('|') + ')(?![\\\\p{{L}}\\\\d])', 'gu');
  return html.replace(/>([^<]+)</g, (m, t) => '>' + t.replace(rx, '<mark>$1</mark>') + '<');
}}
function draw() {{
  const hide = document.getElementById('hide').checked, only = document.getElementById('only').value;
  let n = 0, d = 0;
  document.getElementById('rows').innerHTML = ROWS.map(r => {{
    const s = st[r.num] || {{}}; if (s.ok) d++;
    if ((hide && s.ok) || (only && !r.why.includes(only))) return '';
    n++;
    const body = TLPmd.render(r.text, {{fig: name => `<img src="figs/${{ED}}-${{name}}.png" alt="">`}});
    return `<div class="row${{s.ok ? ' done' : ''}}" id="n${{r.num}}"><div class="scan"><img loading="lazy" src="crops/${{r.img}}"></div>
      <div><div class="meta"><span class="num">${{r.num}}</span><span>стр. ${{r.page}}</span>
      ${{r.why.map(w => `<span class="tag ${{w}}">${{WHY[w]}}</span>`).join('')}}
      <label><input type="checkbox" data-ok="${{r.num}}" ${{s.ok ? 'checked' : ''}}> проверено</label></div>
      <div class="text">${{mark('<div>' + body + '</div>', r.sus)}}</div>
      <textarea data-note="${{r.num}}" placeholder="что исправить">${{(s.note || '').replace(/</g, '&lt;')}}</textarea></div></div>`;
  }}).join('');
  document.getElementById('cnt').textContent = `показано ${{n}} из ${{ROWS.length}}, проверено ${{d}}`;
}}
document.addEventListener('change', e => {{
  const ok = e.target.dataset.ok, note = e.target.dataset.note;
  if (ok) {{ (st[ok] = st[ok] || {{}}).ok = e.target.checked; save(); draw(); }}
  if (note) {{ (st[note] = st[note] || {{}}).note = e.target.value; save(); }}
  if (e.target.id === 'hide' || e.target.id === 'only') draw();
}});
document.getElementById('exp').onclick = () => {{
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify({{edition: ED, marks: st}}, null, 1)], {{type: 'application/json'}}));
  a.download = `proof-${{ED}}.json`; a.click();
}};
draw();
</script></body></html>"""
    open(f"{OUT}/proof_{lang}.html", "w").write(page)
    by = {k: sum(1 for r in rows if k in r["why"]) for k in ("ocr", "formula", "fixed")}
    print(lang, "положений в листе:", len(rows), by)
