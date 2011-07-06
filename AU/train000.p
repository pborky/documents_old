
%digraph train000 {
%        a1 -> b [label=1];
%        a2 -> b [label=2];
%        b -> c [label=3];
%        c -> d [label=4];
%        
%        a1 [shape=box];
%        a2 [shape=box];
%        b [shape=box];
%        c [shape=box];
%        d [shape=ellipse];
%
%        rankdir=LR;
%}

% linear ordering
fof(antisymmetry, axiom, ( ![X,Y]: ((less(X,Y) & less(Y,X)) => (X = Y)) )).
fof(transitivity, axiom, ( ![X,Y,Z]: ((less(X,Y) & less(Y, Z)) => less(X, Z)) )).
fof(totality, axiom,     ( ![X,Y]: (less(X,Y) | less(Y,X)) )).
fof(succ, axiom,         ( ![X]: ( (less(X,succ(X))) & (![Y]: (less(Y,X) | less(succ(X), Y))) ) )).
fof(succ_neq, axiom,     ( ![T]: (succ(T) != T) )).
fof(pred, axiom,         ( ![X]: (( (pred(succ(X)) = X) & (succ(pred(X)) = X) )) )).

% behavior of the train movement
fof(ishere_1, axiom, ( ![T]: ( ishere(succ(T),1) <=> ( (ishere(T,1) & ~sem(T,b)) | sem(T,a1) ) ) )).
fof(ishere_2, axiom, ( ![T]: ( ishere(succ(T),2) <=> ( (ishere(T,2) & sem(T,b)) | sem(T,a2) ) ) )).
fof(ishere_3, axiom, ( ![T]: ( ishere(succ(T),3) <=> ( (ishere(T,3) & ~sem(T,c)) | (ishere(T,1) & sem(T,b)) | (ishere(T,2) & ~sem(T,b))) ) )).
fof(ishere_4, axiom, ( ![T]: ( ishere(succ(T),4) <=> ( ishere(T,3) & sem(T,c) ) ) )).

% semaphore control
fof(sem_a1, axiom,  ( ![T]: ( (ishere(T,1) & ~sem(T,b)) => ~sem(T,a1) ) )).
%fof(sem_a1_, axiom, ( ![T]: ( ~sem(T,a1) | sem(T,a1) ) )).
fof(sem_a2, axiom,  ( ![T]: ( (ishere(T,2) & sem(T,b)) => ~sem(T,a2) ) )).
%fof(sem_a2_, axiom, ( ![T]: ( ~sem(T,a2) | sem(T,a2) ) )).
fof(sem_b, axiom,   ( ![T]: ( (~ishere(T,1) & ishere(T,2)) => ~sem(T,b) ) )).
%fof(sem_b_, axiom,  ( ![T]: ( ~sem(T,b) | sem(T,b) ) )).
fof(sem_c, axiom,   ( ![T]: ( ~sem(T,c) ) )).

% collision
fof(col1, axiom, ( ![T]: ( col(succ(T),1) <=> ( ishere(T,1) & ~sem(T,b) & sem(T,a1) ) ) )).
fof(col2, axiom, ( ![T]: ( col(succ(T),2) <=> ( ishere(T,2) & sem(T,b) & sem(T,a2)) ) )).
fof(col3, axiom, ( ![T]: ( col(succ(T),3) <=> ( ishere(T,3) & ~sem(T,c) & ( (ishere(T,1) & sem(T,b)) | (ishere(T,2) & ~sem(T,b)) ) ) ) )).
fof(col4, axiom, ( ![T]: ( ~col(T,4)  ) )).
fof(col, axiom,  ( ![T]: ( col(T,any) <=> (col(T,1) | col(T,2) | col(T,3) | col(T,4) ) ) )).

% query
%fof(query, conjecture, (![T]: ( ~col(T,any) => ~col(succ(T),any) ))).
fof(query, conjecture, ( ![T]: ( ~col(T,any) ) )).
%fof(query, conjecture, (?[T]: ( col(T,any) ))).
