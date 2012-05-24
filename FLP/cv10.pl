%max(X,Y,X) :- X>=Y.
%max(X,Y,Y) :- Y>X.

%max(X,Y,Z) :- (X>=Y, !,X=Z) ; Y=Z.

max(X,Y,X) :- X>=Y, !.
max(_,Y,Y).

noteq(X,X) :- !, fail.
noteq(_,_).



%listvars(List,_) :- write('listvars: '), write(List), nl, fail.
listvars([], []).
listvars([H|T], Vars) :- allvars(H, HVars), listvars(T, TVars), append(HVars,TVars, Vars).

%allvars(List,_) :- write('allvars: '), write(List), nl, fail.
allvars(T, [T]) :- var(T) , ! .
allvars(T, Vars) :- T =.. [_|Args], listvars(Args,Vars).

