# Makefile per FT-HPC

# vars
BASEDIR=`pwd`
MANDIR=$(BASEDIR)
OUTDIR=$(MANDIR)/Out

TEXOPTS=-output-directory=$(OUTDIR) --shell-escape
BIBENVS=BIBINPUTS=$(MANDIR) TEXMFOUTPUT=$(OUTDIR)
AUTOPTS=-interaction nonstopmode

ITEM=template_report
# end vars

.PHONY: compile bibcompile compileauto bibcompileauto

default: compile

init:
	mkdir -p $(OUTDIR)

compile: init
	pdflatex $(TEXOPTS) $(MANDIR)/$(ITEM).tex

bibcompile: init
	pdflatex $(TEXOPTS) $(MANDIR)/$(ITEM).tex
	$(BIBENVS) bibtex $(OUTDIR)/$(ITEM).aux
	pdflatex $(TEXOPTS) $(MANDIR)/$(ITEM).tex
	pdflatex $(TEXOPTS) $(MANDIR)/$(ITEM).tex

compileauto: init
	pdflatex $(AUTOPTS) $(TEXOPTS) $(MANDIR)/$(ITEM).tex

bibcompileauto: init
	pdflatex $(AUTOPTS) $(TEXOPTS) $(MANDIR)/$(ITEM).tex
	$(BIBENVS) bibtex $(OUTDIR)/$(ITEM).aux
	pdflatex $(AUTOPTS) $(TEXOPTS) $(MANDIR)/$(ITEM).tex
	pdflatex $(AUTOPTS) $(TEXOPTS) $(MANDIR)/$(ITEM).tex

autocompile: init
	./autocompile.loop.sh $(ITEM).pdf compileauto bibcompileauto

clean:
	echo "Cleaning outfiles..."
	rm $(OUTDIR)/*
	rmdir $(OUTDIR)

#EOF
