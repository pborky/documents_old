%addpath(genpath('/home/peterb/workspace/school/KO/scheduling'));
%% A
%load prague.mat

%% B
% Algoritmus dijkstra pre dany uzol vrati pole najmensich vzdialenoosti od ostatnych.
% (najkratsie cesty). Maximalny prvok v tomto zozname predtavuje najvzdialenejsi uzol.
% Zaujima nas uzol s najmensou vzdialenostou do najvzdialenejsieho uzla.

%% search
dst=[];
for i = 1:86, [ma,in] = max(g.dijkstra(i)); dst = [dst;ma,in]; end;

%% result C
[mi,in] = min(dst(:,1));
fprintf('\n****\nukol c1: %d\nukol c2: %f\n****\n', [in,mi]);