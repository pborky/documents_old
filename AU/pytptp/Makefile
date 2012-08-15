FILE = in/*.in
LOGS = log
OUTPUTS = out

TPT = ./generator.py tpt && mv *.tpt $(OUTPUTS)
DOT = ./generator.py dot | tee $(OUTPUTS)/$${i%in}dot
TEX = ./generator.py tex | tee $(OUTPUTS)/$${i%in}tex
UNI = ./generator.py uni

VPROVER = vampire -t 30 --proof tptp --output_axiom_names on --mode casc
EPROVER = eprover --print-statistics --cpu-limit=30 -xAuto -tAuto --memory-limit=Auto --tstp-format
PROVER9 = tptp_to_ladr | prover9
MACE4 = tptp_to_ladr | mace4 -N 100 -b 2000

GRAPH = $(DOT) | display
PDF = $(TEX) | pdflatex -output-directory=$(OUTPUTS)/ >/dev/null && echo "% Output in $(OUTPUTS)/texput.pdf." && evince $(OUTPUTS)/texput.pdf
AXIOMS = $(TPT)
CNF = $(TPT) | eprover --tstp-format --cnf | tee $(OUTPUTS)/$${i%in}cnf

PROVER = for j in tests/run?.tpt ; do echo "% File $$j"; echo "Saving log to $(LOGS)/`basename $${i%.in}`_`basename $${j%.tpt}`.log";  $(SPEC) < $$j > $(LOGS)/`basename $${i%.in}`_`basename $${j%.tpt}`.log; done

ACTION = for i in $(FILE); do echo "% File $$i"; cat $$i |$(SPEC) ; done
ACTION2 = for i in $(FILE); do echo "% File $$i"; cat $$i | $(TPT) && $(PROVER); done

all: init a e

init: 
	@mkdir -p $(LOGS)
	@mkdir -p $(OUTPUTS)

e: SPEC = $(EPROVER)
e:
	@$(ACTION2)

v: SPEC = $(VPROVER)
v:
	@$(ACTION2)

9: SPEC = $(PROVER9)
9:
	@$(ACTION2)

4: SPEC = $(MACE4)
4:
	@$(ACTION2)

2: SPEC = $(MACE2)
2:
	@$(ACTION2)

g: SPEC = $(GRAPH)
g:
	@$(ACTION)

p: SPEC = $(PDF)
p:
	@$(ACTION)

u: SPEC = $(UNI)
u:
	@$(ACTION)

a: SPEC = $(TPT)
a:
	$(ACTION)

c: SPEC = $(CNF)
c:
	@$(ACTION)

