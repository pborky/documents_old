#include <pthread.h> // hlavičkový soubor
#include <stdio.h>
#include <stdlib.h>

#define NUM_THREADS 1 // počet vytvářených vláken
#define MATRIX_DIM 5 

struct matrix {
    float *flat;
    int *rows;
    int xdim;
    int ydim;
};

static struct matrix * getMatrix2(int xdim, int ydim, float * flat) {
    if (xdim < 0 || ydim < 0) {
        printf("ERROR; matrix dimension must be positive integer.\n");
        exit(-1);
    }
    struct matrix * mat = (struct matrix *) malloc(sizeof(struct matrix));
    mat->xdim = xdim;
    mat->ydim = ydim;
    mat->flat = flat;
    mat->rows = malloc(sizeof(int)*ydim);
    
    for (int i = 0, r = 0; i < mat->ydim; i++, r += mat->xdim) {
        mat->rows[i] = r;
    }
    return mat;
}
static struct matrix * getMatrix(int xdim, int ydim) {
    return getMatrix2(xdim, ydim, malloc(sizeof(float)*xdim*ydim));
}
static int getMatrixSize(struct matrix * mat) {
    return mat->xdim * mat->ydim;
}
static void setMatrixField(struct matrix * mat, int x, int y, float value) {
    if (x > mat->xdim || y > mat->ydim || x < 0 || y < 0) {
        printf("ERROR; field index out of bounds.\n");
        exit(-1);
    }
    mat->flat[ x + mat->rows[y] ] = value;
}
static float getMatrixField(struct matrix * mat, int x, int y) {
    if (x > mat->xdim || y > mat->ydim || x < 0 || y < 0) {
        printf("ERROR; field index out of bounds.\n");
        exit(-1);
    }
    return mat->flat[ x + mat->rows[y] ];
}
static struct matrix * getMatrixRow(struct matrix * mat, int y) {
    if (y > mat->ydim || y < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    return getMatrix2(mat->xdim, 1, mat->flat + mat->rows[y]);
}static struct matrix * getMatrixCol(struct matrix * mat, int x) {
    if (x > mat->xdim || x < 0) {
        printf("ERROR; col index out of bounds.\n");
        exit(-1);
    }
    struct matrix * col = getMatrix(1, mat->ydim);
    for (int i = 0; i < col->ydim; i++) {
        setMatrixField(col, 0, i, getMatrixField(mat, x, i));
    }
    return col;
}
static void swapMatrixRows(struct matrix * mat, int y0, int y1) {
    if (y0 > mat->ydim || y0 < 0 || y1 > mat->ydim || y1 < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    int i = mat->rows[y0];
    mat->rows[y0] = mat->rows[y1];
    mat->rows[y1] = i;
}
static void addMatrixRowFactor(struct matrix * mat, int from, int to, float factor) {
    if (to > mat->ydim || to < 0 || from > mat->ydim || from < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    for (int i = 0; i < mat->xdim; i++) {
        mat->flat[ i + mat->rows[to] ] += mat->flat[ i + mat->rows[from] ]*factor;
        if (1E-5 > mat->flat[ i + mat->rows[to] ] && -1E-5 < mat->flat[ i + mat->rows[to] ]) {
            mat->flat[ i + mat->rows[to] ] = 0;
        }
    }
}
static struct matrix * multMatrixRow(struct matrix * mat, int y, float factor) {
    if (y > mat->ydim || y < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    for (int i = 0; i < mat->xdim; i++) {
        mat->flat[ i + mat->rows[y] ] *= factor;
    }
}

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
        mat->flat[i] = i;
    }
}

void getTriangular(struct matrix * mat) {
    for(int i = 0; i < mat->ydim-1; i ++) {
        for (int y = mat->ydim-1; y > i; y--) {
            float f0 = getMatrixField(mat, i, y-1);
            float f1 = getMatrixField(mat, i, y);
            if (f1 == 0) continue;
            if (f0 == 0) {
                swapMatrixRows(mat, y, y-1);
                continue;
            }
            addMatrixRowFactor(mat, y-1, y, -f1/f0);
        }
    }
}

void printMatrix(struct matrix * mat, char * name, char * desc) {
    printf("%s = [ %% %s (matrix in GNU Octave/Matlab format)\n", name, desc);
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

void *PrintThreadID(void *threadArg) { // kód vlákna, funkce je spuštěna po vytvoření vlákna
    long tid = (long)threadArg; // parametr se vždy předává jako ukazatel na void
    
    printf("Thread %ld: start.\n", tid);
    
    char name[20];
    struct matrix * mat = getMatrix(MATRIX_DIM+1, MATRIX_DIM);

    generateIncLinEquations(mat);
    printMatrix(mat, "M", "original");
    
    getTriangular(mat);
    printMatrix(mat, "T", "triangular matrix");
    
    printf("Thread %ld: stop.\n", tid);
    
    pthread_exit(NULL); // ukončení vlákna
}

int main (int argc, char *argv[]) {
    pthread_t threads[NUM_THREADS];// identifikátory vytvořených vláken
    int rc;
    for(long t=0; t<NUM_THREADS; t++) {
        rc = pthread_create(&threads[t], NULL, PrintThreadID, (void *)t);// vytvoření vlákna
        if (rc) {
            printf("ERROR; return code from pthread_create() is %d\n", rc);
            exit(-1);
        }
    }
    pthread_exit(NULL);
}
