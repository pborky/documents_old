fof(anTisymmetry,axiom, ( ! [U,V] : ( ( less(U,V) & less(V,U) ) => U = V ) )).
fof(transitivity,axiom, ( ! [U,V,W] : ( ( less(U,V) & less(V,W) ) => less(U,W) ) )).
fof(totality,axiom,     ( ! [U,V] : ( less(U,V) | less(V,U) ) )).
fof(succ,axiom,         ( ! [U] : ( less(U,succ(U)) & ! [V] : ( less(V,U) | less(succ(U),V) ) ) )).
%   O   O   O
%  >|---|---|--->
%      /
%  >|--
%
% ***
%fof(semaphores00, axiom, ( ![T]: semaphore_a1(T) | ~ semaphore_a1(T) )).
%fof(semaphores01, axiom, ( ![T]: semaphore_a2(T) | ~ semaphore_a2(T) )).
%fof(semaphores02, axiom, ( ![T]: semaphore_b(T) | ~ semaphore_b(T) )).
%fof(semaphores03, axiom, ( ![T]: semaphore_c(T) | ~ semaphore_c(T) )).
%
%fof(segments00, axiom, ( ![T]: segment_in1(T) | ~ segment_in1(T) )).
%fof(segments01, axiom, ( ![T]: segment_in2(T) | ~ segment_in2(T) )).
%fof(segments02, axiom, ( ![T]: segment_1(T) | ~ segment_1(T) )).
%fof(segments03, axiom, ( ![T]: segment_2(T) | ~ segment_2(T) )).
%fof(segments04, axiom, ( ![T]: segment_3(T) | ~ segment_3(T) )).
%fof(segments05, axiom, ( ![T]: segment_4(T) | ~ segment_4(T) )).
%
%fof(collisions, axiom, ( ![T]: collision(T) | ~ collision(T) )).
% ***
% train on input 1
fof(a00, axiom, ( ![T]: ((segment_in1(T) & semaphore_a1(T) & segment_1(T) & ~ semaphore_b(T)) => collision(succ(T)) ) )).
fof(a01, axiom, ( ![T]: ((segment_in1(T) & semaphore_a1(T) & ( ~ segment_1(T) | semaphore_b(T) )) => segment_1(succ(T)) ) )).
fof(a02, axiom, ( ![T]: ((segment_in1(T) & ~ semaphore_a1(T)) => segment_in1(succ(T)) ) )).
% ***
% train on input 2
fof(a03, axiom, ( ![T]: ((segment_in2(T) & semaphore_a2(T) & segment_2(T) & semaphore_b(T)) => collision(succ(T)) ) )).
fof(a04, axiom, ( ![T]: ((segment_in2(T) & semaphore_a2(T) & ( ~segment_2(T) | ~semaphore_b(T))) => segment_2(succ(T)) ) )).
fof(a05, axiom, ( ![T]: ((segment_in2(T) & ~ semaphore_a2(T)) => segment_in2(succ(T)) ) )).
% ***
% train before split on track 1
fof(a06, axiom, ( ![T]:   ( (segment_1(T) & semaphore_b(T) & segment_3(T) & ~ semaphore_c(T)) => collision(succ(T)) ) )).
fof(a07, axiom, ( ![T]: ( (segment_1(T) & semaphore_b(T) & ( ~ segment_3(T) | semaphore_c(T))) => segment_3(succ(T)) ) )).
fof(a08, axiom, ( ![T]:   ( (segment_1(T) & ~ semaphore_b(T)) => segment_1(succ(T)) ) )).
% ***
% train before split on track 2
fof(a09, axiom, ( ![T]:   ( (segment_2(T) & ~ semaphore_b(T) & segment_3(T) & ~ semaphore_c(T)) => collision(succ(T)) ) )).
fof(a10, axiom, ( ![T]: ( (segment_2(T) & ~ semaphore_b(T) & (~ segment_3(T) | semaphore_c(T))) => segment_3(succ(T)) ) )).
fof(a11, axiom, ( ![T]:   ( (segment_2(T) & semaphore_b(T)) => segment_2(succ(T)) ) )).
% ***
% train on station
fof(a12, axiom, ( ![T]:   ( (segment_3(T) & semaphore_c(T)) => segment_4(succ(T)) ) )).
fof(a13, axiom, ( ![T]: ( (segment_3(T) & ~ semaphore_c(T))  => segment_3(succ(T)) ) )).
% ***
fof(a14, axiom, ( ![T]: semaphore_c(T) )).
fof(a15, axiom, ( ![T]: ( segment_1(T) => ~ semaphore_a1(T) ) & ( ~ segment_1(T) => semaphore_a1(T) ) )).
fof(a16, axiom, ( ![T]: ( segment_2(T) => ~ semaphore_a2(T) ) & ( ~ segment_2(T) => semaphore_a2(T) ) )).
fof(a16, axiom, ( ![T]: ((segment_1(T) => semaphore_b(T))) & ((segment_1(T) & segment_2(T)) => ~semaphore_b(T)) )).

% ***
fof(a17, axiom, ( segment_in1(t) )).
fof(a18, axiom, ( segment_in2(t) )).
fof(a19, axiom, ( segment_1(t) )).
fof(a20, axiom, ( segment_2(t) )).
fof(a21, axiom, ( segment_3(t) )).
fof(a22, axiom, ( segment_4(t) )).
%fof(a23, axiom, ( semaphore_a1(t) )).
%fof(a24, axiom, ( semaphore_a2(t) )).
%fof(a25, axiom, ( semaphore_b(t) )).
%fof(a25, axiom, ( semaphore_c(t) )).


fof(c00, conjecture, ( ?[T]: collision(T) )).




