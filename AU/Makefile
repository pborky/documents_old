# yum install graphviz ImageMagick python-ply
FILE = *.in
VAMPCMD = vampire  --proof tptp --output_axiom_names on --mode casc
ECMD = eprover --print-statistics -xAuto -tAuto --cpu-limit=60 --memory-limit=Auto --tstp-format
ACTION = for i in $(FILE); do echo "% File $$i:"; ( cat $$i | ./generator.py $(SPEC) ); done

vampire: SPEC = tp | $(VAMPCMD)
vampire:
	@$(ACTION)

eprover: SPEC = tp | $(ECMD)
eprover:
	@$(ACTION)

graph: SPEC = dot | dot -Tsvg | display &
graph:
	@$(ACTION)

axioms: SPEC = tp
axioms:
	@$(ACTION)

