nr_vowel([],0).
nr_vowel([H|T],Y) :- H=a,!,nr_vowel(T,X),Y is X+1.
nr_vowel([H|T],Y) :- H=e,!,nr_vowel(T,X),Y is X+1.
nr_vowel([H|T],Y) :- H=i,!,nr_vowel(T,X),Y is X+1.
nr_vowel([H|T],Y) :- H=o,!,nr_vowel(T,X),Y is X+1.
nr_vowel([H|T],Y) :- H=u,!,nr_vowel(T,X),Y is X+1.
nr_vowel([_|T],X) :- nr_vowel(T,X).

transpose_vec([],[]).
transpose_vec([H|T],[[H]|R]) :- transpose_vec(T,R).

append_all(X, [], X).
append_all([H1|T1],[H2|T2], [H3|T3]) :- append(H1,H2,H3), append_all(T1,T2,T3).

transpose([],[]).
transpose([H|T], Rest) :-  transpose_vec(H,R), transpose(T,RR),append_all(R,RR,Rest).
