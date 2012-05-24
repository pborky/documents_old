% Target predicate:
target(daughter,2).

% Available body predicates:
language(parent,2).
language(female,1).

% Positive examples:
pos(daughter(louise, edward)).
pos(daughter(louise, sophie)).

% Negative examples:
neg(daughter(louise, elizabeth)).
neg(daughter(diana, charles)).
neg(daughter(harry, diana)).
neg(daughter(diana, sophie)).
