HTML = izomorfizmy-vypusk-polnyj.html
TEX  = izomorfizmy.tex
PDF  = izomorfizmy.pdf

all: $(PDF)

$(TEX): $(HTML) convert.py
	python3 convert.py $(HTML) $(TEX)

$(PDF): $(TEX)
	xelatex -interaction=nonstopmode $(TEX)
	xelatex -interaction=nonstopmode $(TEX)

clean:
	rm -f *.aux *.log *.out *.toc

.PHONY: all clean
