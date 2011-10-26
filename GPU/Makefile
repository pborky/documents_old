all: clean gauss_elim
clean:
	if [ -e gauss_elim ]; then rm gauss_elim; fi
gauss_elim: clean
	cc -o gauss_elim -std=c99 -lpthread gauss_elim.c
