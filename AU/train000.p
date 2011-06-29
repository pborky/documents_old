% ! eprover --print-statistics -xAuto -tAuto --cpu-limit=60 --memory-limit=Auto --tstp-format %
%   O   O   O
%  >|---|---|--->
%   O  /
%  >|--
% 
%     1   3   4
% >a1---b---c---d>
%     2/
% >a2--
%
% sem_a1 - train on input 1 can pass
% sem_a2 - train on input 2 can pass
% sem_b - train on track 1 can pass
% ~ sem_b - train on track 2 can pass
% sem_c - train on track 3 can pass

% linear ordering
fof(antisymmetry, axiom, ( ![X,Y]: ((less(X,Y) & less(Y,X)) => (X = Y)) )).
fof(transitivity, axiom, ( ![X,Y,Z]: ((less(X,Y) & less(Y, Z)) => less(X, Z)) )).
fof(totality, axiom,     ( ![X,Y]: (less(X,Y) | less(Y,X)) )).
fof(succ, axiom,         ( ![X]: ( (less(X,succ(X))) & (![Y]: (less(Y,X) | less(succ(X), Y))) ) )).
fof(succ_neq, axiom,     ( ![T]: (succ(T) != T) )).
fof(pred, axiom,         ( ![X]: (( (pred(succ(X)) = X) & (succ(pred(X)) = X) )) )).

% behavior of the train movement
fof(train_1, axiom,  ( ![T]: ( train(succ(T),1) <=> ( (train(T,1) & ~sem(T,b)) | sem(T,a1) ) ) )).
fof(train_2, axiom,  ( ![T]: ( train(succ(T),2) <=> ( (train(T,2) & sem(T,b)) | sem(T,a2) ) ) )).
fof(train_3, axiom,  ( ![T]: ( train(succ(T),3) <=> ( (train(T,3) & ~sem(T,c)) | (train(T,1) & sem(T,b)) | (train(T,2) & ~sem(T,b))) ) )).
fof(train_4, axiom,  ( ![T]: ( train(succ(T),4) <=> ( train(T,3) & sem(T,c) ) ) )).

% semaphore control
fof(sem_a1, axiom,  ( ![T]: ( (train(T,1) & ~sem(T,b)) => ~sem(T,a1) ) )).
%fof(sem_a1_, axiom, ( ![T]: ( ~sem(T,a1) | sem(T,a1) ) )).
fof(sem_a2, axiom,  ( ![T]: ( (train(T,2) & sem(T,b)) => ~sem(T,a2) ) )).
%fof(sem_a2_, axiom, ( ![T]: ( ~sem(T,a2) | sem(T,a2) ) )).
fof(sem_b, axiom,   ( ![T]: ( (~train(T,1) & train(T,2)) => ~sem(T,b) ) )).
%fof(sem_b_, axiom,  ( ![T]: ( ~sem(T,b) | sem(T,b) ) )).
fof(sem_c, axiom,   ( ![T]: ( sem(T,c) ) )).

% collision
fof(col1, axiom, ( ![T]: ( col(succ(T),1) <=> ( train(T,1) & ~sem(T,b) & sem(T,a1) ) ) )).
fof(col2, axiom, ( ![T]: ( col(succ(T),2) <=> ( train(T,2) & sem(T,b) & sem(T,a2)) ) )).
fof(col3, axiom, ( ![T]: ( col(succ(T),3) <=> ( train(T,3) & ~sem(T,c) & ( (train(T,1) & sem(T,b)) | (train(T,2) & ~sem(T,b)) ) ) ) )).
fof(col4, axiom, ( ![T]: ( ~col(T,4)  ) )).
fof(col, axiom,  ( ![T]: ( col(T,any) <=> (col(T,1) | col(T,2) | col(T,3) | col(T,4) ) ) )).

% query
%fof(query, conjecture, (![T]: ( ~col(T,any) => ~col(succ(T),any) ))).
fof(query, conjecture, ( ![T]: ( ~col(T,any) ) )).
%fof(query, conjecture, (?[T]: ( col(T,any) ))).
