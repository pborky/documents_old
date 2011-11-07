#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#define IN_THREADING_C
#include "threading.h"

struct payload * payloadinit(void) {
    struct payload * pay = malloc(sizeof(struct payload));
    pay->isempty = true;
    pthread_mutex_init(&pay->mutex, NULL);
    pthread_cond_init(&pay->cond, NULL);
    return pay;
}
void payloadput(struct payload * pay, void* data) {
    pthread_mutex_lock( &pay->mutex );
    while (!pay->isempty) {
        pthread_cond_wait( &pay->cond, &pay->mutex );
    }

    pay->payload = data;
    pay->isempty = false;

    pthread_cond_signal( &pay->cond );
    pthread_mutex_unlock( &pay->mutex );
}

void * payloadget(struct payload * pay) {
    pthread_mutex_lock( &pay->mutex );
    while (pay->isempty) {
        pthread_cond_wait( &pay->cond, &pay->mutex );
    }

    void* data = pay->payload;
    pay->isempty = true;

    pthread_cond_signal( &pay->cond );
    pthread_mutex_unlock( &pay->mutex );
    return data;
}

/* **************************************************************************************
 * fifo is based on http://akomaenablog.blogspot.com/2008/03/round-fifo-queue-in-c.html */

/*init queue*/
struct fifo * fifoinit (int size) {
    struct fifo * f = malloc(sizeof(struct fifo));
    f->avl = 0;
    f->in = 0;
    f->out = 0;
    f->N = size;
    f->table = (void**)malloc(f->N*sizeof(void*));
    return f;
}
/*    empty queue = 1 else 0*/
int fifoempty(struct fifo * f) {
   return(f->avl==0);
}
/*    full queue = 1 else 0*/
int fifofull(struct fifo * f) {
   return(f->avl==f->N-1);
}
/*free memmory*/
void fifodestroy(struct fifo * f) {
   int i;
   if(!fifoempty(f)) free(f->table);
   else{
        for(i = f->out ; i < f->in; i++){
            free(f->table[i]);
        }
        free(f->table);
   }
}  
/*insert element*/
int fifoenter(struct fifo * f, void *next) {
   if(f->avl==f->N) {return(0);}
   else {
       f->table[f->in]=next;
       f->avl++;
       f->in=(f->in+1)%f->N;
       return(1);
   }
}
/*return next element*/
void* fifoget(struct fifo * f) {
   void* get;
   if (f->avl>0) {
       get=f->table[f->out];
       f->out=(f->out+1)%f->N;
       f->avl--;
       return(get);
   }   
}
/* ************************************************************************************** */

struct payload * queueinit(void) {
    struct payload * pay = malloc(sizeof(struct payload));
    pay->isempty = false;
    pay->payload = (void*) fifoinit(50);
    pthread_mutex_init(&pay->mutex, NULL);
    pthread_cond_init(&pay->cond, NULL);
    return pay;
}
void queueput(struct payload * pay, void* data) {
    pthread_mutex_lock( &pay->mutex );
    while (fifofull((struct fifo *)pay->payload)) {
        pthread_cond_wait( &pay->cond, &pay->mutex );
    }
    fifoenter((struct fifo *)pay->payload, data);
    
    pthread_cond_signal( &pay->cond );
    pthread_mutex_unlock( &pay->mutex );
}

void * queueget(struct payload * pay) {
    pthread_mutex_lock( &pay->mutex );
    while (fifoempty((struct fifo *)pay->payload)) {
        pthread_cond_wait( &pay->cond, &pay->mutex );
    }

    void* data = fifoget((struct fifo *)pay->payload);

    pthread_cond_signal( &pay->cond );
    pthread_mutex_unlock( &pay->mutex );
    return data;
}
void createThread(pthread_t * thread, void *(*start_routine)(void*), struct threadarg * arg) {
    int rc;
    rc = pthread_create(thread, NULL, start_routine, arg);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        exit(-1);
    }
}
