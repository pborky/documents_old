% vim: syntax=prolog

% Pod 100 km:

h(hodonin, brno).
h(jihlava, brno).
h(olomouc, brno).
h(zlin, brno).
h(znojmo, brno).

h(hradec, havlbrod).
h(jihlava, havlbrod).
h(pardubice, havlbrod).
h(znojmo, havlbrod).

h(zlin, hodonin).
h(liberec, hradec).
h(pardubice, hradec).

h(vary, cheb).
h(marianky, cheb).

h(pardubice, jihlava).
h(znojmo, jihlava).

h(marianky, vary).
h(plzen, vary).

h(usti, liberec).
h(plzen, marianky).

h(ostrava, olomouc).

h(praha, plzen).
h(usti, praha).

% Mezi 100 a 150

h(havlbrod, brno).
h(hradec, brno).
h(pardubice, brno).
h(havlbrod, budejovice).
h(jihlava, budejovice).
h(plzen, budejovice).
h(praha, budejovice).
h(znojmo, budejovice).
h(praha, havlbrod).
h(jihlava, hodonin).
h(olomouc, hodonin).
h(znojmo, hodonin).
h(jihlava, hradec).
h(olomouc, hradec).
h(praha, hradec).
h(plzen, cheb).
h(praha, jihlava).
h(praha, vary).
h(usti, vary).
h(pardubice, liberec).
h(praha, liberec).
h(pardubice, olomouc).
h(znojmo, olomouc).
h(zlin, ostrava).
h(praha, pardubice).
h(usti, plzen).

w(X,Y) :- h(X,Y).
w(Y,X) :- h(X,Y).

dfs1(From, Goal, [From,Goal]) :- w(From,Goal).
dfs1(From, Goal, [From|Route]) :- w(From,Node),!,dfs1(Node,Goal,Route).

dfs2(From, Goal, _, [From,Goal]) :- w(From,Goal),!.
dfs2(From, Goal, Closed, [From|Route]) :- 
    w(From,Node),not(member(Node,Closed)),dfs2(Node,Goal,[From|Closed], Route).





