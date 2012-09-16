FILE = in/*.in
LOGS = log
OUTPUTS = out

TPT = ./generator.py tpt
DOT = ./generator.py dot | tee $(OUTPUTS)/`basename $${i%.in}`.$${i%in}dot
TEX = ./generator.py tex | tee $(OUTPUTS)/`basename $${i%.in}`.tex
UNI = ./generator.py uni

VPROVER = vampire -t 120 --proof tptp --output_axiom_names on --mode casc
EPROVER = eprover --print-statistics --cpu-limit=120 -xAuto -tAuto --memory-limit=Auto --tstp-format
PROVER9 = tptp_to_ladr | prover9 -t 120
MACE4 = tptp_to_ladr | mace4 -t 120 -n 3 -N 10 -b 2000
CONV =  tptp_to_ladr

GRAPH = $(DOT) | display
PDF = $(TEX) | pdflatex -output-directory=$(OUTPUTS)/ >/dev/null && echo "% Output in $(OUTPUTS)/texput.pdf." && evince $(OUTPUTS)/texput.pdf
AXIOMS = $(TPT)
CNF = $(TPT) | eprover --tstp-format --cnf | tee $(OUTPUTS)/$${i%in}cnf

PROVER = for j in tests/run?.tpt.* ; do echo "% File $$j"; echo "Saving log to $(LOGS)/`basename $${i%.in}`_`basename $${j%.tpt*}`.log";  cat $$j | $(SPEC) > $(LOGS)/`basename $${i%.in}`_`basename $${j%.tpt*}`.log; done
#PROVER = for j in tests/run?.tpt ; do echo "% File $$j"; echo "Saving log to $(LOGS)/`basename $${i%.in}`_`basename $${j%.tpt}`.log";  cat $$j | $(SPEC) ; done

ACTION = for i in $(FILE); do echo "% File $$i"; cat $$i | $(SPEC) ; done
ACTION2 = for i in $(FILE); do echo "% File $$i"; cat $$i | $(TPT) && $(PROVER); done

VERIFY =  case $${j\#*.*.} in mace4) $(MACE4);; eprover) $(EPROVER);; prover9) $(PROVER9);; esac

all: init verify

init: 
	@mkdir -p $(LOGS)
	@mkdir -p $(OUTPUTS)

verify: SPEC = $(VERIFY)
verify: init
	@$(ACTION2)

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

l: SPEC = $(CONV)
l:
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

