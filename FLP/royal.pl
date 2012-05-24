% vim: syntax=prolog

%% part 1 
% - done. I`m not scared.

%% part 2
% task 1
%  - done

% task 2 - database
desc(william, 'Prince William of Wales').
desc(harry, 'Prince Henry of Wales').
desc(charles, 'The Prince Charles, Prince of Wales').
desc(diana, 'Diana, Princess of Wales').
desc(camilla, 'Camilla, Duchess of Cornwall').
desc(george, 'George VI of the United Kingdom').
desc(elizabeth, 'Elizabeth II, HM The Queen').
desc(philip, 'Prince Philip, Duke of Edinburgh').
desc(edward, 'The Prince Edward, Earl of Wessex').
desc(sophie, 'Sophie, Countess of Wessex').
desc(louise, 'Princess Louise of Wessex').
desc(james, 'Prince James of Wessex').

male(william).
male(harry).
male(charles).
male(george).
male(philip).
male(edward).
male(james).

female(diana).
female(camilla).
female(elizabeth).
female(sophie).
female(louise).

parent(george,elizabeth).
parent(elizabeth,charles).
parent(elizabeth,edward).
parent(philip,charles).
parent(philip,edward).
parent(sophie,james).
parent(sophie,louise).
parent(edward,james).
parent(edward,louise).
parent(charles,harry).
parent(charles,william).
parent(diana,william).
parent(diana,harry).

wife(camilla,charles).
wife(diana,charles).
wife(elizabeth,philip).
wife(sophie,edward).


% task 3 - basic definitions
husband(H,W) :- wife(W,H).

person(P) :- male(P).
person(P) :- female(P).

mother(M,C) :- female(M),parent(M,C).
father(F,C) :- male(F),parent(F,C).

% task 4 - negation by failure
sibling(S1,S2,P) :- parent(P,S1),parent(P,S2), S1\=S2.

%% part 3 - the hard
% task 1 - Learning task specification
daughter(louise, edward).
daughter(elizabeth, george).
daughter(louise, sophie).

target(daughter,2).

language(parent,2).
language(female,1).

% task 2 - get clauses
body_lit(X) :- language(F, N), functor(X, F, N), call(X).
head_lit(X) :- target(F,N), functor(X, F, N), call(X).

one_clause([], _, []).
one_clause([Hi|Ti], B, [cl(Hi,B)|To]) :- one_clause(Ti,B,To).

all_clauses(X) :- 
    findall(Y, head_lit(Y), HeadLits), 
    findall(Y, body_lit(Y), BodyLits),
    one_clause(HeadLits, BodyLits, X).

% task 3 - anti-unification

lgg_term(X,Y, X, List,List) :- X == Y, !.
lgg_term(X,Y, G, List,[s(X,Y,G)|List]) :- var(X); var(Y).

lgg_term(X,Y, G, List,List) :-
  member(s(A,B,G), List),
  A == X, B == Y, !.

lgg_term(X,Y, G, In,Out) :-
  X =.. [P|Xa], Y =.. [P|Ya],
  lgg_list(Xa,Ya, Ga, In,Out),
  G =.. [P|Ga], !.

lgg_term(X,Y, G, List,[s(X,Y,G)|List]).

% LGG on lists of equal length
lgg_list([],     [],      [],       Lst,Lst).
lgg_list([H1|T1],[H2|T2], [G|Rest], Beg,End):-
  lgg_term(H1,    H2,      G,       Beg,Mid),
  lgg_list(  T1,     T2,     Rest,  Mid,End).


a(_,[],[]).
a(E,[H|T],[[E,H]|T2]) :- a(E,T,T2).

carthesian([],_,[]).
carthesian([H|T],K,C) :- a(H,K,T2), carthesian(T,K,T3), append(T2,T3,C).

filter(Pred,Elem,List,[Elem|List]) :- call(Pred),!.
filter(_,_,List,List).

filter_compat([], []).
filter_compat([H|T], C) :- 
    [X,Y]=H,
    functor(X,F1,A1),
    functor(Y,F2,A2),
    filter([A1,F1]=[A2,F2],H,T2,C),
    filter_compat(T, T2).

lgg_term_all([], [], Out, Out).
lgg_term_all([[H1,H2]|T], [G|T2], Mid, Out) :- lgg_term(H1,H2,G,Mid,Mid2), lgg_term_all(T, T2, Mid2, Out).

lgg_clause(C1,C2,LGG) :- 
    arg(1,C1,H1),
    arg(2,C1,B1),
    arg(1,C2,H2),
    arg(2,C2,B2),
    carthesian(B1,B2,Pairs),
    filter_compat(Pairs,Filtered),
    lgg_term_all(Filtered, GT, [], Mid),
    lgg_term(H1,H2,GH,Mid,_),
    LGG=cl(GH,GT).


lgg2([],[]).
lgg2([X], [X]).
lgg2([C1|[C2|T]],[General|Out]) :- lgg_clause(C1,C2,General), lgg2(T, Out).

lgg(X) :- all_clauses(Clauses), lgg2(Clauses,X), portray_clause(X).


%% part 4 - discussion
% 1. SQL is query languaga designed for the relational database systems. Prolog (or its subset - Datalog) is used as a query language in deductive database systems. Datalog unlike Prolog is insensitive in order of the facts, or rules, it doesn`t contain special predicates like cut, or function symbols. Deductive databases are set-oriented while logic programming languages concentrate on one tuple at a time. SQL language is influenced by deductive database languages but it has less espressivity. It is well suitable for large data processing and has no procedural execution (althught there are some procedural extensions). Prolog, unlikely, is more expressive in terms of fact and rule definitions. It can be used for complex querying or fact dafinition.
% 2. Manualy encoded facts are logical consequencs of clauses obtained by means of generalization, but they are not equivalent since manually encoded clauses or facts are subset of generalized ones.
% 3. Inductive logic programing should be useful to infer clauses from given examples, e.g. to extend incomplete theries.
