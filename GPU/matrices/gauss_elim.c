#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>

#include "matrices.h"
#include "threading.h"

#define NUM_THREADS 5 // počet vytvářených vláken
#define MATRIX_DIM 10
#define FILE_NAME "data.log"

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
        void* m = queueget(targ->in);
        getMatrixEchelon((struct matrix *)m);
        queueput(targ->out, m);
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *RankMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
        
    while (1) {
        void* m = queueget(targ->in);
        struct matrix * mat = (struct matrix *)m;
        rankMatrix(mat);
        
        int rka = mat->rka; 
        int rks = mat->rks; 
        
        if (rka <= rks) {
            if (rka < MATRIX_DIM) {
                freeMatrix(mat);
            } else {
                getMatrixDiagonal(mat);
                payloadput(targ->out, m);
            }
        } else {
            freeMatrix(mat);
        }
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); // ukončení vlákna
}

void *SolveMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
    int i = 0;
    FILE * f = fopen(FILE_NAME, "w");
    while (1) {
        void* m = payloadget(targ->in);
        struct matrix * mat = (struct matrix *)m;
        fprintf(f, "%%%%\n\n%%%% Solution %d.\n", i++);
        char name [100];
        sprintf(name, "M%d", i);
        printMatrix(f, mat->orig->orig, name, "Original matrix");
        sprintf(name, "X%d", i);
        printMatrix(f, getMatrixCol(mat, mat->xdim-1), name, "solution vector");
        freeMatrix(mat);
    }
    
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); 
}

void *MasterMatricesThread(void * arg) {
    struct threadarg * targ = (struct threadarg *)arg;
    printf("%% Thread %ld: start.\n", targ->tid);
    
    while (1) {
        queueput(targ->out, payloadget(targ->in));
    }
   
    printf("%% Thread %ld: stop.\n", targ->tid);
    pthread_exit(NULL); 
}

int main (int argc, char *argv[]) {
    struct threadarg * arg = malloc(sizeof(struct threadarg)*5);
    for (int i = 0; i < 4; i++) arg[i].tid = i;
    arg[0].in = NULL;
    arg[3].out = NULL;
    arg[0].out = arg[4].in = payloadinit();
    arg[4].out = arg[1].in = queueinit();
    arg[1].out = arg[2].in = queueinit();
    arg[2].out = arg[3].in = payloadinit();
    
    pthread_t * threads = malloc(sizeof(pthread_t)*(5+NUM_THREADS));
    createThread(& threads[0], GenMatricesThread, & arg[0]);
    createThread(& threads[2], RankMatricesThread, & arg[2]);
    createThread(& threads[3], SolveMatricesThread, & arg[3]);
    // producer
    createThread(& threads[4], MasterMatricesThread, & arg[4]);
    // one default consumer
    createThread(& threads[1], EchelonMatricesThread, & arg[1]);
    //generate more consumer threads
    for (int i = 0; i < NUM_THREADS; i++) createThread(& threads[5+i], EchelonMatricesThread, & arg[1]);
    
    // wait for threads stop
    for (int i = 0; i < (5+NUM_THREADS); i++) pthread_join(threads[i], NULL);
    
    free(threads);
    free(arg);
    
    pthread_exit(NULL);
}
