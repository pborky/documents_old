%my_member(X,L) :- L=[H|_], H=X.
my_member(X,[X|_]).
my_member(X,[_|T]) :- my_member(X,T).

my_select(E, [E|R], R).
my_select(E, [H|T], [H|R]) :- my_select(E, T, R).

my_append(X, [], [X]).
my_append(X, [H|T], [H|R]) :- my_append(X, T, R).

my_reverse([], []).
my_reverse([H|T], R) :- my_reverse(T,Tr), my_append(H, Tr, R) .

my_extend([], X, X).
my_extend([H|Tail], X, [H|Rest]) :- my_extend(Tail, X, Rest).

%my_extend(_,Y,[1,2,3,4,5,6]), my_extend(X,_,Y).
