
TMPFILE = /tmp/$(FILE).tmp

vampire:
	vampire  --proof tptp --output_axiom_names on --mode casc --input_file ${FILE}

eprover:
	eprover --print-statistics -xAuto -tAuto --cpu-limit=60 --memory-limit=Auto --tstp-format ${FILE} 

graph:
	t=`cat $(FILE) | python generator.py`; echo $$(expr "$${t//%/}" : '.*\(digraph[^{]*{[^}]*}\)' ) | dot -Tsvg -o$(TMPFILE)
	( eog $(TMPFILE); rm $(TMPFILE) ) &
