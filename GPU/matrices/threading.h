#include <pthread.h>
#include <stdbool.h>

struct threadarg {
    long tid;
    struct payload * in;
    struct payload * out;
};

struct fifo {
    void** table;
    int N,in,out,avl;
};

struct payload {
    void* payload;
    bool isempty;
    pthread_cond_t cond;
    pthread_mutex_t mutex;
};

#ifndef IN_THREADING_C
struct payload * payloadinit(void);
void payloadput(struct payload * pay, void* data);
void * payloadget(struct payload * pay);

struct fifo * fifoinit (int size);
void fifodestroy(struct fifo * f);
int fifoempty(struct fifo * f);
int fifofull(struct fifo * f);
int fifoenter(struct fifo * f, void *next);
void* fifoget(struct fifo * f);

struct payload * queueinit(void);
void queueput(struct payload * pay, void* data);
void * queueget(struct payload * pay);

void createThread(pthread_t * thread, void *(*start_routine)(void*), struct threadarg * arg);
#endif

