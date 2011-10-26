#include <pthread.h> // hlavičkový soubor
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "matrices.h"

#define NUM_THREADS 1 // počet vytvářených vláken
#define MATRIX_DIM 3 
#define EPS 1E-8

void generateRandLinEquations(struct matrix * mat) {
    if (mat->xdim != mat->ydim+1) {
        printf("ERROR; matrix not in augmented form.\n");
        exit(-1);
    }
    for (int i = 0; i < getMatrixSize(mat); i++) {
        mat->flat[i] = rand();
    }
}
void generateIncLinEquations(struct matrix * mat) {
    if (mat->xdim != mat->ydim+1) {
        printf("ERROR; matrix not in augmented form.\n");
        exit(-1);
    }
    for (int i = 0; i < getMatrixSize(mat); i++) {
        mat->flat[i] = abs(i-5);
    }
}

void makeEchelon(struct matrix * mat) {
    for(int i = 0; i < mat->ydim-1; i ++) {
        for (int y = mat->ydim-1; y > i; y--) {
            float f0 = getMatrixField(mat, i, y-1);
            float f1 = getMatrixField(mat, i, y);
            if (f1 == 0) continue;
            if (f0 == 0) {
                swapMatrixRows(mat, y, y-1);
                continue;
            }
            addMatrixRowFactor(mat, y-1, y, -f1, f0);
        }
    }
}
void makeDiagonal(struct matrix * mat) {
    for(int i = mat->xdim-2, j = mat->ydim-1; i > 0 && j > 0; i--, j--) {
            float f0 = getMatrixField(mat, i, j);
            if (fabs(f0) == 0) {
                printf("WARNING; foooka!!\n");
                return;
            }
            for(int y = j-1; y >= 0; y--) {
                float f1 = getMatrixField(mat, i, y);
                addMatrixRowFactor(mat, i, y, -f1, f0);
            }
            multMatrixRow(mat, j, 1, f0);
    }
    multMatrixRow(mat, 0, 1, getMatrixField(mat, 0, 0));
}
void printMatrix(struct matrix * mat, char * name, char * desc) {
    printf("%s = [ %% %s\n", name, desc);
    for (int i = 0; i < mat->ydim; i++) {
        for (int j = 0; j < mat->xdim; j++) {
            float f =  getMatrixField(mat, j, i);
            if (j == mat->xdim-1) {
                printf("%f;\n", f);
            } else {
                printf("%f,\t", f);
            }
        }
    }
    printf("];\n");
}

void print(void) {
    
    char name[20];
    struct matrix * mat = getMatrix(MATRIX_DIM+1, MATRIX_DIM);

    printf("%% script in GNU Octave/Matlab format.\n");
    srand (time (0));
    generateRandLinEquations(mat);
    printMatrix(mat, "M", "original");
    
    makeEchelon(mat);
    printMatrix(mat, "Mt", "triangular form of matrix M");
    
    int rka = getMatrixRank(mat, true);     //augmented rank
    int rks = getMatrixRank(mat, false);    //square rank
    
    if (rka <= rks) {
        printf("rk = %d; %% rank of the matrix M\n", rks );
        if (rka < MATRIX_DIM) {
            printf("%% rank < dimension => too many solutions.\n");
        } else {
            makeDiagonal(mat);
            printMatrix(getMatrixCol(mat, mat->xdim-1), "X", "solution vector");
        }
    } else {
        printf("rka = %d; %% rank of the augmented matrix M\n", rka );
        printf("rks = %d; %% rank of the square matrix M\n", rks );
        printf("%% rank of augmented matrix != rank of square matrix => no solution.\n");
    }
}

void *PrintThreadID(void *threadArg) { // kód vlákna, funkce je spuštěna po vytvoření vlákna
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    
    printf("%% Thread %ld: start.\n", tid);
    
    printf("%% Thread %ld: stop.\n", tid);
    
    pthread_exit(NULL); // ukončení vlákna
}

int main (int argc, char *argv[]) {
    /*pthread_t threads[NUM_THREADS];// identifikátory vytvořených vláken
    int rc;
    for(long t=0; t<NUM_THREADS; t++) {
        rc = pthread_create(&threads[t], NULL, PrintThreadID, (void *)t);// vytvoření vlákna
        if (rc) {
            printf("ERROR; return code from pthread_create() is %d\n", rc);
            exit(-1);
        }
    }
    pthread_exit(NULL);*/
    print();
}
