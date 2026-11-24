FONT=fonts/AlcarinTengwar-Regular.otf
PY=python3 -I
# full chain from the font to the PDF, the STL files and the web page; `make clean all` rebuilds everything
all: main.pdf web

data/codes.json: tools/measure.py tools/inventory.py tools/measure_helpers.py $(FONT)
	$(PY) tools/measure.py $(FONT) data
data/strokes.json: tools/strokes.py data/codes.json
	$(PY) tools/strokes.py $(FONT) data data/strokes.json
gen/analysis.json: data/codes.json tools/analysis.py
	$(PY) tools/analysis.py data gen
gen/analysis_fdm.json: tools/analysis_fdm.py
	$(PY) tools/analysis_fdm.py gen
gen/stats.json: data/codes.json data/strokes.json gen/analysis.json gen/analysis_fdm.json tools/gen_shuttle.py tools/layout.py tools/inventory.py
	$(PY) tools/gen_shuttle.py $(FONT) data gen
gen/fdmsim.json: tools/fdmsim.py data/codes.json
	$(PY) tools/fdmsim.py $(FONT) data gen
gen/fdmsim_thick.json: tools/fdmsim_thick.py tools/thicken.py data/codes.json
	$(PY) tools/fdmsim_thick.py $(FONT) data gen
gen/fdm_panel.png: tools/fdmpanel.py
	$(PY) tools/fdmpanel.py $(FONT) gen/fdm_panel.png
gen/fdm_panel2.png: tools/fdmpanel2.py tools/thicken.py
	$(PY) tools/fdmpanel2.py $(FONT) gen/fdm_panel2.png
stl/stamps.json: gen/stats.json tools/stamps.py tools/thicken.py tools/glyphgeom.py
	$(PY) tools/stamps.py $(FONT) data gen stl
gen/tab_stamps.tex: gen/fdmsim.json stl/stamps.json tools/tables_fdm.py
	$(PY) tools/tables_fdm.py gen stl

gen/model/model.json: gen/stats.json tools/model/*.py
	$(PY) tools/model/build.py gen/model gen
gen/dynamics.json: gen/model/model.json tools/model/dynamics.py
	$(PY) tools/model/dynamics.py gen/model/model.json gen/dynamics.json
gen/motor.json: gen/model/model.json tools/model/motor.py
	$(PY) tools/model/motor.py gen/motor.json
gen/whiffle.json: tools/model/whiffle.py tools/model/params.py
	$(PY) tools/model/whiffle.py gen/whiffle.json
gen/links.json: tools/model/links.py tools/model/params.py
	$(PY) tools/model/links.py gen/links.json
gen/visibility.json: gen/model/model.json tools/model/visibility.py
	$(PY) tools/model/visibility.py gen/visibility.json gen
gen/tab_model_buy.tex: gen/model/model.json gen/dynamics.json gen/motor.json gen/whiffle.json gen/links.json gen/visibility.json tools/model/tables.py
	$(PY) tools/model/tables.py gen

TEX_IN=gen/stats.json gen/fdmsim_thick.json gen/fdm_panel.png gen/fdm_panel2.png gen/tab_stamps.tex gen/tab_model_buy.tex
main.pdf: main.tex preamble.tex $(TEX_IN)
	xelatex -interaction=nonstopmode main.tex >/dev/null; xelatex -interaction=nonstopmode main.tex | grep -E "^!|Output written" || true

gen/web/model.json: gen/model/model.json gen/motor.json tools/model/webexport.py
	mkdir -p gen/web && $(PY) tools/model/webexport.py gen/web/model.json
gen/web/tpm2-model.html: gen/web/model.json tools/web/template.html tools/web/build_page.py
	$(PY) tools/web/build_page.py gen/web/model.json tools/web/template.html gen/web/tpm2-model.html
web: gen/web/tpm2-model.html
stl: stl/stamps.json
model: gen/tab_model_buy.tex

clean:
	find gen -maxdepth 1 -type f -delete; rm -rf gen/model gen/web main.aux main.toc main.out main.pdf
.PHONY: all web stl model clean
