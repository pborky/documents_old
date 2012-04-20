%%% FLP course at CTU 2010/2011, tutorial 1 %%%
%%%      The London Underground example     %%%

connectedS(bond_street,          oxford_circus,        central).
connectedS(oxford_circus,        tottenham_court_road, central).
connectedS(bond_street,          green_park,           jubilee).
connectedS(green_park,           charing_cross,        jubilee).
connectedS(green_park,           piccadilly_circus,    piccadilly).
connectedS(piccadilly_circus,    leicester_square,     piccadilly).
connectedS(green_park,           oxford_circus,        victoria).
connectedS(oxford_circus,        piccadilly_circus,    bakerloo).
connectedS(piccadilly_circus,    charing_cross,        bakerloo).
connectedS(tottenham_court_road, leicester_square,     northern).
connectedS(leicester_square,     charing_cross,        northern).

connected(X,Y,L) :- connectedS(X,Y,L).
connected(X,Y,L) :- connectedS(Y,X,L).

%connected('Mustek', 'Muzeum', 'A').

%connected(tottenham_court_road,  florenc,              central).

nearby(X,Y) :- connected(X,Y,_).
nearby(X,Z) :- connected(X,Y,L), connected(Y,Z,L).

racheable(X,X).
racheable(X,Y) :- connectedS(X,Z,_) , racheable(Z,Y).

journey(X,Y,T) :- connectedS(X,Y,_), T =[] .
journey(X,Y,T) :- connectedS(X,Z,_), journey(Z,Y,U), T = [Z|U].

