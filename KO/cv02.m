
addpath(genpath('/home/pborky/workspace/school/KO/scheduling'));

clear;

mapSize = 6;

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
schoptions=schoptionsset('ilpSolver','glpk','solverVerbosity',2);

%spusteni optimalizace z TORSCHE
[xmin,fmin,status,extra] = ilinprog(schoptions,sense,c,A,b,ctype,lb,ub,vartype);

if(status==1)
    disp('Reseni:');
    %xmin(1:mapSize^2)
    [y x] = ind2sub([mapSize mapSize],find(xmin(1:mapSize^2)));
    fprintf('x_%d,%d\n', [x y]');
    
    disp('Hodnota cilove funkce:');
    fmin
    
    disp('Mapa:');
    X = zeros(mapSize);
    X(:) = 'O';
    X(find(xmin(1:mapSize^2))) = '*';
    char(X)
else
    disp('Problem nema reseni!');
end;

%konec souboru