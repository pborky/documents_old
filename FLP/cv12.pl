% vim:syntax=prolog
:- [library(clpfd)].

alldiff([]).
alldiff([H|T]) :- \+ member(H,T), alldiff(T).

num(X) :- member(X,[1,2,3,4]).

inst([]).
inst([H|T]) :- num(H), inst(T).

sudoku1([[A1,B1,C1,D1],
        [A2,B2,C2,D2],
	[A3,B3,C3,D3],
	[A4,B4,C4,D4]]) :-
  inst([A1,B1,C1,D1]),
  inst([A2,B2,C2,D2]),
  inst([A3,B3,C3,D3]),
  inst([A4,B4,C4,D4]),

  alldiff([A1,B1,C1,D1]),
  alldiff([A2,B2,C2,D2]),
  alldiff([A3,B3,C3,D3]),
  alldiff([A4,B4,C4,D4]),

  alldiff([A1,A2,A3,A4]),
  alldiff([B1,B2,B3,B4]),
  alldiff([C1,C2,C3,C4]),
  alldiff([D1,D2,D3,D4]),

  alldiff([A1,A2,B1,B2]),
  alldiff([A3,A4,B3,B4]),
  alldiff([C1,C2,D1,D2]),
  alldiff([C3,C4,D3,D4]).

sudoku3([[A1,B1,C1,D1],
         [A2,B2,C2,D2],
         [A3,B3,C3,D3],
         [A4,B4,C4,D4]]) :-
  All = [A1,B1,C1,D1,A2,B2,C2,D2,A3,B3,C3,D3,A4,B4,C4,D4],
  All ins 1..4,

  all_different([A1,B1,C1,D1]),
  all_different([A2,B2,C2,D2]), 
  all_different([A3,B3,C3,D3]),
  all_different([A4,B4,C4,D4]),

  all_different([A1,A2,A3,A4]),
  all_different([B1,B2,B3,B4]),
  all_different([C1,C2,C3,C4]),
  all_different([D1,D2,D3,D4]),

  all_different([A1,A2,B1,B2]),
  all_different([A3,A4,B3,B4]),
  all_different([C1,C2,D1,D2]),
  all_different([C3,C4,D3,D4]),

  label(All).

sudoku2([[A1,B1,C1,D1],
        [A2,B2,C2,D2],
	[A3,B3,C3,D3],
	[A4,B4,C4,D4]]) :-

     inst([A1,B1,C1,D1]),
  alldiff([A1,B1,C1,D1]),

     inst([A2,B2,C2,D2]),
  alldiff([A2,B2,C2,D2]),
  alldiff([A1,A2,B1,B2]),
  alldiff([C1,C2,D1,D2]),

     inst([A3,B3,C3,D3]),
  alldiff([A3,B3,C3,D3]),


     inst([A4,B4,C4,D4]),
  alldiff([A4,B4,C4,D4]),
  alldiff([A3,A4,B3,B4]),
  alldiff([C3,C4,D3,D4]),


  alldiff([A1,A2,A3,A4]),
  alldiff([B1,B2,B3,B4]),
  alldiff([C1,C2,C3,C4]),
  alldiff([D1,D2,D3,D4]).
