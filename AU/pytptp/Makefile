FILE = *.in

TPT = ./generator.py tpt | tee tee $${i%in}tptp
DOT = ./generator.py dot | tee tee $${i%in}dot
TEX = ./generator.py tex | tee tee $${i%in}tex
UNI = ./generator.py uni

VPROVER = $(TPT) | vampire -t 120 --proof tptp --output_axiom_names on --mode casc
EPROVER = $(TPT) | eprover --print-statistics -xAuto -tAuto --memory-limit=Auto --tstp-format
PROVER9 = $(TPT) | tptp_to_ladr | prover9
MACE4 = $(TPT) | tptp_to_ladr | mace4 -N 100 -b 2000
GRAPH = $(DOT) | display
PDF = $(TEX) | pdflatex  -output-directory=out/ >/dev/null && echo "% Output in out/texput.pdf." && evince out/texput.pdf
AXIOMS = $(TPT) | tee $${i%in}tptp
CNF = $(TPT) | eprover --tstp-format --cnf | tee $${i%in}cnf

ACTION = for i in $(FILE); do echo "% File $$i"; ( cat $$i | $(SPEC) ); done

all: 4 9 e

e: SPEC = $(EPROVER)
e:
	@$(ACTION)

v: SPEC = $(VPROVER)
v:
	@$(ACTION)

9: SPEC = $(PROVER9)
9:
	@$(ACTION)

4: SPEC = $(MACE4)
4:
	@$(ACTION)

2: SPEC = $(MACE2)
2:
	@$(ACTION)

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
	@$(ACTION)

c: SPEC = $(CNF)
c:
	$(ACTION)

