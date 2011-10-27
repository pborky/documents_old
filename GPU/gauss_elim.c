#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>

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

void *GenMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
    
    while (1) {
        struct matrix * mat = getMatrix(MATRIX_DIM+1, MATRIX_DIM);
        srand (time (0));
        generateRandLinEquations(mat);
        payloadput( targ->out, (void*)mat);
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *EchelonMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
    
    while (1) {
        struct matrix * mat = (struct matrix *)payloadget(targ->in);
        getMatrixEchelon(mat);
        payloadput(targ->out, (void*)mat);
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *RankMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
        
    while (1) {
        struct matrix * mat = (struct matrix *)payloadget(targ->in);

        int rka = getMatrixRank(mat, true);     //augmented rank
        int rks = getMatrixRank(mat, false);    //square rank
        
        if (rka <= rks) {
            printf("rk = %d; %% rank of the matrix M\n", rks );
            if (rka < MATRIX_DIM) {
                printf("%% rank < dimension => too many solutions.\n");
            } else {
                payloadput(targ->out, (void*)mat);
            }
        } else {
            printf("rka = %d; %% rank of the augmented matrix M\n", rka );
            printf("rks = %d; %% rank of the square matrix M\n", rks );
            printf("%% rank of augmented matrix != rank of square matrix => no solution.\n");
        }
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *SolveMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
        
    while (1) {
        struct matrix * mat = (struct matrix *)payloadget(targ->in);
        getMatrixDiagonal(mat);
        printMatrix(getMatrixCol(mat, mat->xdim-1), "X", "solution vector");
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); 
}

int main (int argc, char *argv[]) {
    pthread_t * threads = malloc(sizeof(pthread_t)*4);

    struct threadarg * arg = malloc(sizeof(struct threadarg)*4);
    arg[0].tid = 0;
    arg[0].in = NULL;
    arg[0].out = payloadinit();
    arg[1].tid = 1;
    arg[1].in = arg[0].out;
    arg[1].out = payloadinit();
    arg[2].tid = 2;
    arg[2].in = arg[1].out;
    arg[2].out = payloadinit();
    arg[3].tid = 3;
    arg[3].in = arg[2].out;
    arg[3].out = NULL;

    int rc;

    rc = pthread_create(& threads[0], NULL, GenMatricesThread, (void*) & arg[0]);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        exit(-1);
    }
    rc = pthread_create(&threads[1], NULL, EchelonMatricesThread, (void*)&arg[1]);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        exit(-1);
    }
    rc = pthread_create(&threads[2], NULL, RankMatricesThread, (void*)&arg[2]);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        exit(-1);
    }
    rc = pthread_create(&threads[3], NULL, SolveMatricesThread, (void*)&arg[3]);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        exit(-1);
    }
    
    for (int i = 0; i < 4; i++) pthread_join(threads[i], NULL);
    
    pthread_exit(NULL);
}
