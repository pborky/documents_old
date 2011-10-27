all: clean gauss_elim
clean:
	if [ -e gauss_elim ]; then rm gauss_elim; fi
	if [ -e gauss_elim.o ]; then rm gauss_elim.o; fi
	if [ -e matrices.o ]; then rm matrices.o; fi
	if [ -e threading.o ]; then rm threading.o; fi
matrices.o:
	cc -c -std=c99 matrices.c -o matrices.o
gauss_elim.o:
	cc -c -std=c99 -lpthread gauss_elim.c -o gauss_elim.o
threading.o:
	cc -c -std=c99 -lpthread threading.c -o threading.o

gauss_elim: matrices.o threading.o gauss_elim.o
	cc gauss_elim.o matrices.o threading.o -o gauss_elim
	if [ -e gauss_elim.o ]; then rm gauss_elim.o; fi
	if [ -e matrices.o ]; then rm matrices.o; fi
	if [ -e threading.o ]; then rm threading.o; fi


