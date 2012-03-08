function cv03b (b, ops)

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
bx = [ops,b,b];
A = [   [ones(1,24),zeros(1,24)]
	[A,-eye(24)];
	[A,eye(24)] ];
c = [zeros(24, 1);ones(24, 1)];
ctype = [repmat('L',25,1);repmat('G',24,1)];
lb = zeros(48,1);
ub = inf(48,1);
vartype = repmat('C', 48, 1);

%Parametry optimalizace
schoptions=schoptionsset('ilpSolver','glpk','solverVerbosity',0);

%spusteni optimalizace z TORSCHE
[xmin,fmin,status,extra] = ilinprog(schoptions,sense,c,A,bx,ctype,lb,ub,vartype);

if(status==1),
    j = [];
    for i = 0:7,
        j = [j; [24-i+1:24, 1:24-i]];
    end;
    br = sum(xmin(j'),2);
    subplot(2,1,2); bar ([b',br],1); title('weak');
    fprintf('\nOperator count:\t%d\n', sum(xmin(1:24)));
    %fprintf('\nTotal diff:\t%d\n', sum(abs(br - b')));
    fprintf('\nTotal diff:\t%d\n', sum(xmin(25:end)));
    fprintf('\nx = [');
    fprintf('%2d,', xmin(1:24));
    fprintf(']\n');
    fprintf('\ny = [');
    fprintf('%2d,', xmin(25:end))
    fprintf(']\n');
else
    disp('Problem nema reseni!');
end;

%konec souboru
