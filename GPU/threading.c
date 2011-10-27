#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

#define IN_THREADING_C
#include "threading.h"

struct payload * payloadinit(void) {
    struct payload * pay = malloc(sizeof(struct payload));
    pthread_mutex_init(&pay->mutex, NULL);
    pthread_cond_init(&pay->isempty, NULL);
    pthread_cond_init(&pay->isfull, NULL);
}
void payloadput(struct payload * pay, void* data) {
    pthread_mutex_lock( &pay->mutex );
    pthread_cond_wait( &pay->isempty, &pay->mutex );
    pay->payload = data;
    pthread_cond_signal( &pay->isfull );
    pthread_mutex_unlock( &pay->mutex );
}

void * payloadget(struct payload * pay) {
    pthread_mutex_lock( &pay->mutex );
    pthread_cond_wait( &pay->isfull, &pay->mutex );
    void* data = pay->payload;
    pthread_cond_signal( &pay->isempty );
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
/*
int main(int argc,char* argv[]) {
    struct fifo * f = fifoinit(10);
    char * p = "Fooka"; fifoenter(f, (void*) p);
    p = "Fooka2"; fifoenter(f, (void*) p);
    p = "Fooka3"; fifoenter(f, (void*) p);
    p = "Fooka4"; fifoenter(f, (void*) p);

    for (int i = 0; i < 10; i++) {
        if (!fifoempty(f)) {
            printf("%s\n", (char*)fifoget(f));
        } else {
            printf("*** no data\n");
        }
    }

    fifodestroy(f);
}
*/
