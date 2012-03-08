function cv03a (b)

addpath(genpath('/home/pborky/workspace/school/KO/scheduling'));

A = zeros(24, 24);

for i = 1:24,
    if i<=7,
        A(sub2ind(size(A),repmat([i], 1, 8), [(17+i):24,1:i])) = 1;
    else
        A(sub2ind(size(A),repmat([i], 1, 8), (i+(-7:0)))) = 1;
    end;
end;

sense=1;
c = ones(24, 1);
ctype = repmat('G', 24, 1);
lb = zeros(24,1);
ub = inf(24,1);
vartype = repmat('C', 24, 1);

%Parametry optimalizace
schoptions=schoptionsset('ilpSolver','glpk','solverVerbosity',0);

%spusteni optimalizace z TORSCHE
[xmin,fmin,status,extra] = ilinprog(schoptions,sense,c,A,b,ctype,lb,ub,vartype);

if(status==1)
    j = [];
    for i = 0:7,
        j = [j; [24-i+1:24, 1:24-i]];
    end;
    br = sum(xmin(j'),2);
    subplot(2,1,1); bar ([b',br],1); title('strict');
    fprintf('\nOperator count:\t%d\n', sum(xmin(1:24)));
    fprintf('\nTotal diff:\t%d\n', sum(abs(br - b')));
    fprintf('\nx = [');
    fprintf('%2d,', xmin(1:24));
    fprintf(']\n');
else
    disp('Problem nema reseni!');
end;

%konec souboru
