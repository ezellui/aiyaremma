"""Собирает самостоятельную читалку: один HTML-файл, всё внутри (данные, KaTeX со шрифтами,
md.js, i18n.js). Открывается с диска двойным щелчком.

    python3 build_reader.py      → ../out/tlp_reader.html
"""
import base64, os, re

W = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(W, "reader")
OUT = os.path.join(W, "..", "out")

tpl = open(f"{R}/tlp_reader.html", encoding="utf-8").read()

# KaTeX: стили со шрифтами woff2, вклеенными как data:URI (woff и ttf выбрасываются)
css = open(f"{R}/katex/katex.min.css", encoding="utf-8").read()
def font(m):
    name = m.group(1)
    data = base64.b64encode(open(f"{R}/katex/fonts/{name}.woff2", "rb").read()).decode()
    return f'src:url(data:font/woff2;base64,{data}) format("woff2")'
css = re.sub(r'src:url\(fonts/([\w-]+)\.woff2\) format\("woff2"\)(?:,url\([^)]*\) format\("[\w]+"\))*', font, css)
assert "fonts/" not in css, "в стилях KaTeX остались внешние шрифты"

def script(path):
    s = open(path, encoding="utf-8").read().replace("</script", "<\\/script")
    return f"<script>\n{s}\n</script>"

scripts = "\n".join([
    script(f"{R}/katex/katex.min.js"),
    script(f"{R}/i18n.js"),
    script(f"{R}/md.js"),
    script(f"{OUT}/tlp-data.js"),
])
html = tpl.replace("<!--@KATEX_CSS@-->", f"<style>{css}</style>").replace("<!--@SCRIPTS@-->", scripts)
open(f"{OUT}/tlp_reader.html", "w", encoding="utf-8").write(html)
print("tlp_reader.html:", round(len(html.encode()) / 1e6, 2), "МБ")
