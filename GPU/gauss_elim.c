#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "matrices.h"
#include "threading.h"

#define NUM_THREADS 1 // počet vytvářených vláken
#define MATRIX_DIM 3 

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

void print(void) {
    
    char name[20];
    struct matrix * mat = getMatrix(MATRIX_DIM+1, MATRIX_DIM);

    printf("%% script in GNU Octave/Matlab format.\n");
    srand (time (0));
    generateRandLinEquations(mat);   
    getMatrixEchelon(mat);
    rankMatrix(mat);
    
    if (mat->rka <= mat->rks) {
        if (mat->rka < MATRIX_DIM) {
            printMatrix(mat->orig, "M", "original");
            printMatrix(mat, "Mt", "triangular form of matrix M");
            printf("rk = %d; %% rank of the matrix M\n", mat->rks );
            printf("%% rank < dimension => too many solutions.\n");
        } else {
            getMatrixDiagonal(mat);
            printMatrix(mat->orig->orig, "M", "original");
            printMatrix(mat->orig, "Mt", "triangular form of matrix M");
            printf("rk = %d; %% rank of the matrix M\n", mat->rks );
            printMatrix(mat->sol, "X", "solution vector");
        }
    } else {
        printMatrix(mat->orig, "M", "original");
        printMatrix(mat, "Mt", "triangular form of matrix M");
        printf("rka = %d; %% rank of the augmented matrix M\n", mat->rka );
        printf("rks = %d; %% rank of the square matrix M\n", mat->rks );
        printf("%% rank of augmented matrix != rank of square matrix => no solution.\n");
    }
}

void *GenMatricesThread(void * threadArg) {
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    printf("%% Thread %ld: start.\n", tid);
    
    while (1) {
        struct matrix * mat = getMatrix(MATRIX_DIM+1, MATRIX_DIM);
        srand (time (0));
        generateRandLinEquations(mat);
        // TODO: put mat somewhere
    }
    
    printf("%% Thread %ld: stop.\n", tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *EchelonMatricesThread(void * threadArg) {
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    printf("%% Thread %ld: start.\n", tid);
    
    while (1) {
        struct matrix * mat; // TODO: get mat from somwhere
        getMatrixEchelon(mat);
        // TODO: put mat somewhere
    }
    
    printf("%% Thread %ld: stop.\n", tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *RankMatricesThread(void * threadArg) {
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    printf("%% Thread %ld: start.\n", tid);
        
    while (1) {
        struct matrix * mat; // TODO: get mat from somwhere

        int rka = getMatrixRank(mat, true);     //augmented rank
        int rks = getMatrixRank(mat, false);    //square rank
        
        if (rka <= rks) {
            printf("rk = %d; %% rank of the matrix M\n", rks );
            if (rka < MATRIX_DIM) {
                printf("%% rank < dimension => too many solutions.\n");
            } else {
                // TODO: put mat somewhere
            }
        } else {
            printf("rka = %d; %% rank of the augmented matrix M\n", rka );
            printf("rks = %d; %% rank of the square matrix M\n", rks );
            printf("%% rank of augmented matrix != rank of square matrix => no solution.\n");
        }
    }
    
    printf("%% Thread %ld: stop.\n", tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *SolveMatricesThread(void * threadArg) {
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    printf("%% Thread %ld: start.\n", tid);
        
    while (1) {
        struct matrix * mat; // TODO: get mat from somwhere
        
        getMatrixDiagonal(mat);
        printMatrix(getMatrixCol(mat, mat->xdim-1), "X", "solution vector");
    }
    
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
