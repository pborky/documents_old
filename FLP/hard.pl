% Target predicate:
target(sibling, 2).

% Available body predicates:
language(parent, 2).
language(\=, 2).

% Positive examples:
pos(sibling(harry, william)).
pos(sibling(william, harry)).
pos(sibling(james, louise)).
pos(sibling(charles, edward)).

% Negative examples:
neg(sibling(charles, george)).
neg(sibling(george, charles)).
neg(sibling(george, diana)).
neg(sibling(harry, harry)).
neg(sibling(james, george)).
neg(sibling(diana, philip)).
neg(sibling(elizabeth, camilla)).
neg(sibling(louise, george)).
neg(sibling(sophie, diana)).
