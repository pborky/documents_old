
list_gt([H|T1], [H|T2]) :- list_gt(T1,T2), !.
list_gt([H1|_], [H2|_]) :- H1 < H2, !.

name_gt(N1, N2) :- name(N1,L1), name(N2,L2), list_gt(L1,L2).

eu(X,Y,Z,M) :- h(X,Y,Z), Z < M, name_gt(X,Y).

topro(M) :- eu(X,Y,Z,M), portray_clause(eu(X,Y,Z)), fail.
todot(M) :- eu(X,Y,Z,M), W is M - Z,
  L is (W / 200) + 1,
  write('  '), write(X), write(' -> '), write(Y), write(' [weight='), write(W), write(',style="setlinewidth('), write(L) ,write(')"]'), nl, fail.

