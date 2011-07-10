# yum install graphviz ImageMagick python-ply
FILE = *.in
TIME = 60
VAMPCMD = vampire -t $(TIME) --proof tptp --output_axiom_names on --mode casc
ECMD = eprover --print-statistics -xAuto -tAuto --cpu-limit=$(TIME) --memory-limit=Auto --tstp-format
ACTION = for i in $(FILE); do echo "% File $$i"; ( cat $$i | ./generator.py $(SPEC) ); done
MSG1 = echo "% Using file(s) $(FILE) and cputime limit is $(TIME).."
MSG2 = echo "% Using file(s) $(FILE).."

vampire: SPEC = tp | $(VAMPCMD)
vampire:
	@$(MSG1)
	@$(ACTION)

eprover: SPEC = tp | $(ECMD)
eprover:
	@$(MSG1)
	@$(ACTION)

graph: SPEC = dot | dot -Tsvg | display &
graph:
	@$(MSG2)
	@$(ACTION)

axioms: SPEC = tp
axioms:
	@$(MSG2)
	@$(ACTION)

