#include <pthread.h>

struct fifo {
    void** table;
    int N,in,out,avl;
};

struct payload {
    void* payload;
    pthread_cond_t isempty;
    pthread_cond_t isfull;
    pthread_mutex_t mutex;
};

#ifndef IN_THREADING_C
struct payload * payloadinit(void);
void payloadput(struct payload * pay, void* data);
void * payloadget(struct payload * pay);

struct fifo * fifoinit (int size);
void fifodestroy(struct fifo * f);
int fifoempty(struct fifo * f);
int fifoenter(struct fifo * f, void *next);
void* fifoget(struct fifo * f);
#endif

