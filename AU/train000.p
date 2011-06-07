%   O   O   O
%  >|---|---|--->
%      /
%  >|--
% 
%     1   3   4
% >a1---b---c---d>
%     2/
% >a2--
%
% semaphore_a1 - train on input 1 can pass
% semaphore_a2 - train on input 2 can pass
% semaphore_b - train on track 1 can pass
% ~ semaphore_b - train on track 2 can pass
% semaphore_c - train on track 3 can pass

% ***
% ordering
fof(anTisymmetry,axiom, ( ! [U,V] : ( ( less(U,V) & less(V,U) ) => U = V ) )).
fof(transitivity,axiom, ( ! [U,V,W] : ( ( less(U,V) & less(V,W) ) => less(U,W) ) )).
fof(totality,axiom,     ( ! [U,V] : ( less(U,V) | less(V,U) ) )).
fof(succ,axiom,         ( ! [U] : ( less(U,succ(U)) & ! [V] : ( less(V,U) | less(succ(U),V) ) ) )).

% ***
% train on input 1
fof(seg01, axiom, ( ![T]: ((segment_in1(T) & semaphore_a1(T)) => segment_1(succ(T)) ) )).
fof(seg02, axiom, ( ![T]: ((segment_in1(T) & ~ semaphore_a1(T)) => segment_in1(succ(T)) ) )).
% ***
% train on input 2
fof(seg04, axiom, ( ![T]: ((segment_in2(T) & semaphore_a2(T)) => segment_2(succ(T)) ) )).
fof(seg05, axiom, ( ![T]: ((segment_in2(T) & ~ semaphore_a2(T)) => segment_in2(succ(T)) ) )).
% ***
% train before split on track 1
fof(seg07, axiom, ( ![T]: ((segment_1(T) & semaphore_b(T)) => segment_3(succ(T)) ) )).
fof(seg08, axiom, ( ![T]: ((segment_1(T) & ~ semaphore_b(T)) => segment_1(succ(T)) ) )).
% ***
% train before split on track 2
fof(seg09, axiom, ( ![T]: ((segment_2(T) & ~ semaphore_b(T)) => segment_3(succ(T)) ) )).
fof(seg10, axiom, ( ![T]: ((segment_2(T) & semaphore_b(T)) => segment_2(succ(T)) ) )).
% ***
% train at the station
fof(seg12, axiom, ( ![T]: ((segment_3(T) & semaphore_c(T)) => segment_4(succ(T)) ) )).
fof(seg13, axiom, ( ![T]: ((segment_3(T) & ~ semaphore_c(T))  => segment_3(succ(T)) ) )).

% are these obsolete?
fof(seg03, axiom, ( ![T]: (~((segment_in1(T) & semaphore_a1(T)) | (segment_1(T) & ~ semaphore_b(T)) ) => ~ segment_1(succ(T)) ) )).
fof(seg06, axiom, ( ![T]: (~((segment_in2(T) & semaphore_a2(T)) | (segment_2(T) & semaphore_b(T)) ) => ~ segment_2(succ(T)) ) )).
fof(seg11, axiom, ( 
        ![T]: (~((segment_1(T) & semaphore_b(T)) | (segment_2(T) & ~ semaphore_b(T)) | (segment_3(T) & ~ semaphore_c(T))) => ~ segment_3(succ(T)) ) 
)).


% ***
% collisions
fof(col00, axiom, ( ![T]: ((segment_in1(T) & semaphore_a1(T) & segment_1(T) & ~ semaphore_b(T)) => collision_1(succ(T)) ) )).
fof(col01, axiom, ( ![T]: ((~ segment_in1(T) | ~ semaphore_a1(T) | ~ segment_1(T) | semaphore_b(T)) => ~ collision_1(succ(T)) ) )).

fof(col02, axiom, ( ![T]: ((segment_in2(T) & semaphore_a2(T) & segment_2(T) & semaphore_b(T)) => collision_2(succ(T)) ) )).
fof(col03, axiom, ( ![T]: ((~ segment_in2(T) | ~ semaphore_a2(T) | ~ segment_2(T) | ~ semaphore_b(T)) => ~ collision_2(succ(T)) ) )).

fof(col04, axiom, ( ![T]: ((segment_1(T) & semaphore_b(T) & segment_3(T) & ~ semaphore_c(T)) => collision_3(succ(T)) ) )).
fof(col05, axiom, ( ![T]: ((~ segment_1(T) | ~ semaphore_b(T) | ~ segment_3(T) | semaphore_c(T)) => ~ collision_3(succ(T)) ) )).

fof(col06, axiom, ( ![T]: ((segment_2(T) & ~ semaphore_b(T) & segment_3(T) & ~ semaphore_c(T)) => collision_3(succ(T)) ) )).
fof(col07, axiom, ( ![T]: ((~ segment_2(T) | semaphore_b(T) | ~ segment_3(T) | semaphore_c(T)) => ~ collision_3(succ(T)) ) )).

% ***
% semaphore controll
fof(a14, axiom, ( ![T]: semaphore_c(T) )).
fof(a15, axiom, ( ![T]: ( segment_1(T) => ~ semaphore_a1(T) ) & ( ~ segment_1(T) => semaphore_a1(T) ) )).
fof(a16, axiom, ( ![T]: ( segment_2(T) => ~ semaphore_a2(T) ) & ( ~ segment_2(T) => semaphore_a2(T) ) )).
fof(a16, axiom, ( ![T]: ((segment_1(T) => semaphore_b(T))) & ((segment_1(T) & segment_2(T)) => ~semaphore_b(T)) )).

% ***
% initial conditions
fof(a17, axiom, ( segment_in1(t) )).
fof(a18, axiom, ( segment_in2(t) )).
fof(a19, axiom, ( segment_1(t) )).
fof(a20, axiom, ( segment_2(t) )).
fof(a21, axiom, ( segment_3(t) )).
fof(a22, axiom, ( segment_4(t) )).


% ***
fof(c00, conjecture, ( ?[T]: collision(T) )).
