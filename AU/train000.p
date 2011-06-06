%   O   O   O
%  >|---|---|--->
%      /
%  >|--
%
% ***
fof(semaphores00, axiom, ( ![T]: semaphore_a1(T) | ~ semaphore_a1(T) )).
fof(semaphores01, axiom, ( ![T]: semaphore_a2(T) | ~ semaphore_a2(T) )).
fof(semaphores02, axiom, ( ![T]: semaphore_b(T) | ~ semaphore_b(T) )).
fof(semaphores03, axiom, ( ![T]: semaphore_c(T) | ~ semaphore_c(T) )).
%
fof(segments00, axiom, ( ![T,X]: segment_in1(T,X) | ~ segment_in1(T,X) )).
fof(segments01, axiom, ( ![T,X]: segment_in2(T,X) | ~ segment_in2(T,X) )).
fof(segments02, axiom, ( ![T,X]: segment_1(T,X) | ~ segment_1(T,X) )).
fof(segments03, axiom, ( ![T,X]: segment_2(T,X) | ~ segment_2(T,X) )).
fof(segments04, axiom, ( ![T,X]: segment_3(T,X) | ~ segment_3(T,X) )).
fof(segments05, axiom, ( ![T,X]: segment_4(T,X) | ~ segment_4(T,X) )).
%
fof(collisions, axiom, ( ![T]: collision(T) | ~ collision(T) )).
% ***
% train on input 1
fof(a00, axiom, ( ![T,Y]:   ( segment_in1(T,Y) & semaphore_a1(T) & segment_1(T,Z) => collision(T) ) )).
fof(a01, axiom, ( ![T,Y,Z]: ( segment_in1(T,Y) & semaphore_a1(T) & ~ segment_1(T,Z) => segment_1(succ(T),Y) ) )).
fof(a02, axiom, ( ![T,Y]:   ( segment_in1(T,Y) & ~ semaphore_a1(T) => segment_in1(succ(T),Y) ) )).
% ***
% train on input 2
fof(a03, axiom, ( ![T,Y]:   ( segment_in2(T,Y) & semaphore_a2(T) & segment_2(T,Z) => collision(T) ) )).
fof(a04, axiom, ( ![T,Y,Z]: ( segment_in2(T,Y) & semaphore_a2(T) & ~ segment_2(T,Z) => segment_2(succ(T),Y) ) )).
fof(a05, axiom, ( ![T,Y]:   ( segment_in2(T,Y) & ~ semaphore_a2(T) => segment_in2(succ(T),Y) ) )).
% ***
% train before split on track 1
fof(a06, axiom, ( ![T,Y]:   ( segment_1(T,Y) & semaphore_b(T) & segment_3(T,Z) => collision(T) ) )).
fof(a07, axiom, ( ![T,Y,Z]: ( segment_1(T,Y) & semaphore_b(T) & ~ segment_3(T,Z) => segment_3(succ(T),Y) ) )).
fof(a08, axiom, ( ![T,Y]:   ( segment_1(T,Y) & ~ semaphore_b(T) => segment_1(succ(T),Y) ) )).
% ***
% train before split on track 2
fof(a09, axiom, ( ![T,Y]:   ( segment_2(T,Y) & ~ semaphore_b(T) & segment_3(T,Z) => collision(T) ) )).
fof(a10, axiom, ( ![T,Y,Z]: ( segment_2(T,Y) & ~ semaphore_b(T) & ~ segment_3(T,Z) => segment_3(succ(T),Y) ) )).
fof(a11, axiom, ( ![T,Y]:   ( segment_2(T,Y) & semaphore_b(T) => segment_2(succ(T),Y) ) )).
% ***
% train on station
fof(a12, axiom, ( ![T,Y]:   ( segment_3(T,Y) & semaphore_c(T) => segment_4(succ(T),Y) ) )).
fof(a13, axiom, ( ![T,Y,Z]: ( segment_3(T,Y) & ~ semaphore_c(T)  => segment_3(succ(T),Y) ) )).
