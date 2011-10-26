all: clean gauss_elim
clean:
	if [ -e gauss_elim ]; then rm gauss_elim; fi
	if [ -e gauss_elim.o ]; then rm gauss_elim.o; fi
	if [ -e matrices.o ]; then rm matrices.o; fi
matrices.o:
	cc -c -std=c99 matrices.c -o matrices.o
gauss_elim.o:
	cc -c -std=c99 -lpthread gauss_elim.c -o gauss_elim.o
gauss_elim: matrices.o gauss_elim.o
	cc gauss_elim.o matrices.o -o gauss_elim
	if [ -e gauss_elim.o ]; then rm gauss_elim.o; fi
	if [ -e matrices.o ]; then rm matrices.o; fi

