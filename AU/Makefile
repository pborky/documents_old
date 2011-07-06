
TMPFILE = /tmp/$(FILE).tmp

vampire:
	vampire  --proof tptp --output_axiom_names on --mode casc --input_file ${FILE}

eprover:
	eprover --print-statistics -xAuto -tAuto --cpu-limit=60 --memory-limit=Auto --tstp-format ${FILE} 

graph:
	(cat test.in | ./generator.py dot | dot -Tsvg | display) &
	
