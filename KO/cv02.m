function cv02 (mapSize)

addpath(genpath('/home/pborky/workspace/school/KO/scheduling'));

l = [ 0 0; 0 -1; 0 1; -1 0; 1 0 ];

A = zeros(mapSize^2, mapSize^2);

for i = 1:mapSize,
    for j = 1:mapSize,
        m = (repmat([i j],5,1) + l);
        m = m(min((m > 0) & (m <= mapSize),[],2),:);
        cols = sub2ind([mapSize mapSize], m(:,1), m(:,2));
        rows = repmat(((i-1)*mapSize)+j, size(cols));
        A(sub2ind(size(A), rows, cols)) = 1;
    end;
end;

sense=1;
b = ones(mapSize^2, 1);
A = [A,-2*eye(mapSize^2)];
c = [ones(mapSize^2, 1);zeros(mapSize^2, 1)];
ctype = repmat('E', mapSize^2, 1);
lb = zeros(2*mapSize^2,1);
ub = [ones(mapSize^2,1);2*ones(mapSize^2,1)];
vartype = repmat('I', 2*mapSize^2,1);

%Parametry optimalizace
schoptions=schoptionsset('ilpSolver','glpk','solverVerbosity',0);

%spusteni optimalizace z TORSCHE
[xmin,fmin,status,extra] = ilinprog(schoptions,sense,c,A,b,ctype,lb,ub,vartype);

if(status==1)
    xmin = xmin(1:mapSize^2);
    xmin = reshape(logical(xmin), [mapSize,mapSize]);
    
    fprintf('Tahy:\n');
    %xmin(1:mapSize^2)
    [i j] = ind2sub([mapSize mapSize],find(xmin));
    fprintf('  (%d,%d)\n', [j i]');
    
    fprintf('\nMinimalní počet tahů:\n');
    fprintf('  fmin = %d\n', fmin);

    fprintf('\nMapa:\n');
    c = 'O*';
    c = c(1+xmin);
    fmt = ['  ' repmat('%c',1,mapSize) '\n'];
    fprintf(fmt, c);
    
else
    disp('Problem nema reseni!');
end;

%konec souboru
