
struct matrix {
    float *flat;
    int *rows;
    int xdim;
    int ydim;
    int rka;
    int rks;
    struct matrix * orig;
    struct matrix * sol;    
};

#ifndef IN_MATRICES_C
struct matrix * getMatrix2(int xdim, int ydim, float * flat);
struct matrix * getMatrix(int xdim, int ydim);
int getMatrixSize(struct matrix * mat);
void setMatrixField(struct matrix * mat, int x, int y, float value);
float getMatrixField(struct matrix * mat, int x, int y);
struct matrix * getMatrixRow(struct matrix * mat, int y);
struct matrix * getMatrixCol(struct matrix * mat, int x);
void swapMatrixRows(struct matrix * mat, int y0, int y1);
void addMatrixRowFactor(struct matrix * mat, int from, int to, float factor, float divisor);
void multMatrixRow(struct matrix * mat, int y, float factor, float divisor);
int getMatrixRank(struct matrix * mat, bool augmented);
void rankMatrix(struct matrix * mat);
void getMatrixEchelon(struct matrix * mat);
void getMatrixDiagonal(struct matrix * mat);
void printMatrix(FILE * f, struct matrix * mat, char * name, char * desc);
void freeMatrix(struct matrix * mat);
#endif
