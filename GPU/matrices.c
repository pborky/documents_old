#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define IN_MATRICES_C
#include "matrices.h"

#define EPS 1E-4

struct matrix * getMatrix2(int xdim, int ydim, float * flat) {
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
struct matrix * getMatrix(int xdim, int ydim) {
    return getMatrix2(xdim, ydim, malloc(sizeof(float)*xdim*ydim));
}
int getMatrixSize(struct matrix * mat) {
    return mat->xdim * mat->ydim;
}
void setMatrixField(struct matrix * mat, int x, int y, float value) {
    if (x > mat->xdim || y > mat->ydim || x < 0 || y < 0) {
        printf("ERROR; field index out of bounds.\n");
        exit(-1);
    }
    mat->flat[ x + mat->rows[y] ] = value;
}
float getMatrixField(struct matrix * mat, int x, int y) {
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
}
struct matrix * getMatrixCol(struct matrix * mat, int x) {
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
void swapMatrixRows(struct matrix * mat, int y0, int y1) {
    if (y0 > mat->ydim || y0 < 0 || y1 > mat->ydim || y1 < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    int i = mat->rows[y0];
    mat->rows[y0] = mat->rows[y1];
    mat->rows[y1] = i;
}
void addMatrixRowFactor(struct matrix * mat, int from, int to, float factor, float divisor) {
    if (to > mat->ydim || to < 0 || from > mat->ydim || from < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    for (int i = 0; i < mat->xdim; i++) {
        double a = ((mat->flat[ i + mat->rows[to] ] * divisor) + (mat->flat[ i + mat->rows[from] ]*factor));
        mat->flat[ i + mat->rows[to] ] = (float)(a/(double)divisor);
    }
}
void multMatrixRow(struct matrix * mat, int y, float factor, float divisor) {
    if (y > mat->ydim || y < 0) {
        printf("ERROR; row index out of bounds.\n");
        exit(-1);
    }
    for (int i = 0; i < mat->xdim; i++) {
        double a = (mat->flat[ i + mat->rows[y] ])*factor;
        mat->flat[ i + mat->rows[y] ] = (float)(a/(double)divisor);
    }
}
int getMatrixRank(struct matrix * mat, bool augmented) {
    int rank = 0;
    int xdim = augmented?mat->xdim:(mat->xdim-1);
    for (int y = 0; y < mat->ydim; y++) {
        bool zero = true;
        for (int x = 0; x < xdim; x++) {
            if (fabs(getMatrixField(mat, x, y)) > 0) zero = false;
        }
        if (!zero) rank++;
    }
    return rank;
}


