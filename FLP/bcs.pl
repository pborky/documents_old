% vim: syntax=prolog

female(camilla).
female(diana).
female(elizabeth).
female(louise).
female(sophie).

male(charles).
male(edward).
male(george).
male(harry).
male(james).
male(philip).
male(william).

parent(charles,harry).
parent(charles,william).
parent(diana,harry).
parent(diana,william).
parent(edward,james).
parent(edward,louise).
parent(elizabeth,charles).
parent(elizabeth,edward).
parent(george,elizabeth).
parent(philip,charles).
parent(philip,edward).
parent(sophie,james).
parent(sophie,louise).

wife(camilla,charles).
wife(diana,charles).
wife(elizabeth,philip).
wife(sophie,edward).

%:-[easy].
%:-[hard].

exec_body([]).
exec_body([H|T]) :- call(H), exec_body(T).

add_literal(cl(Head,Body),cl(Head,[X|Body]) ) :- 
    language(F, N),
    functor(X, F, N).

prepend_all(_,[],[]).
prepend_all(E,[H|T],[[E,H]|T2]) :- prepend_all(E,T,T2).

check_neg([[Cl1,Cl2]|_],Body) :-
    exec_body(Body),Cl1=Cl2,!,fail.
check_neg([],_).
check_neg([_|T],Body) :-
    check_neg(T,Body).

check_pos(Body,Cl1,Cl2) :-
    exec_body(Body),Cl1=Cl2.
check_pos([[Cl1,Cl2]|_],Body) :-
    \+check_pos(Body,Cl1,Cl2),!,fail.
check_pos([],_).
check_pos([_|T],Body):-
    check_pos(T,Body).

examples_satisfied(cl(Head,Body)) :-
    findall(Xneg, neg(Xneg), Neg),
    prepend_all(Head,Neg,AllNeg), 
    check_neg(AllNeg,Body),
    findall(Xpos, pos(Xpos), Pos),
    prepend_all(Head,Pos,AllPos), 
    check_pos(AllPos,Body).

listvars([], []).
listvars([H|T], Vars) :-
    allvars(H, HVars), listvars(T, TVars), append(HVars,TVars, Vars).

allvars(T, [T]) :- var(T) , ! .
allvars(T, Vars) :- T =.. [_|Args], listvars(Args,Vars).

permute([H|T], [H|R]) :-
    random(X), X < 0.5, !,permute(T, R).
permute([H|T], R) :-
    !,permute(T, Q),append(Q, [H], R).
permute([], []).

checkrandval(NVars,Rand1,Rand1,RandOut) :-
    random(0,NVars,R2),
    checkrandval(NVars,Rand1,R2,RandOut),!.
checkrandval(_,_,Rand2,Rand2).

randval(NVars,Rand1,Rand2) :-
    N is NVars-1,
    random(0,N,Rand1),
    random(0,N,R2),
    checkrandval(N,Rand1,R2,Rand2).

split([H|List],N,[H|R],E) :- 
    N>0,M is N -1,split(List,M,R,E).
split([H|List],0,List,H).
split([],_,[],[]).

unify_vars(Cl1, Cl2) :-
    copy_term(Cl1,Cl2),
    term_variables(Cl2,Vars2),
    term_variables(Cl1,Vars1),
    length(Vars2,NVars),
    randval(NVars,Rand1,Rand2),
    split(Vars1,Rand1,L,_),
    split(Vars2,Rand2,_,E),
    split(Vars2,Rand1,L,E).

    
