# yum install graphviz ImageMagick python-ply
TMPFILE = /tmp/$(FILE).tmp
FILE = *.in

vampire:
	@vampire  --proof tptp --output_axiom_names on --mode casc --input_file $(FILE)

eprover:
	@eprover --print-statistics -xAuto -tAuto --cpu-limit=60 --memory-limit=Auto --tstp-format $(FILE)

graph:
	@for i in $(FILE); do ( cat $$i | ./generator.py dot | dot -Tsvg | display & ); done

axioms:
	@for i in $(FILE); do echo "% File $$i:"; ( cat $$i | ./generator.py tp ); echo; done
