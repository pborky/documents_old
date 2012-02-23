addpath(genpath('/home/pborky/workspace/school/KO/scheduling'));

blockSize = 3;
blockCount = 3;
mapSize = blockSize*blockCount;

indices = reshape(1:mapSize^2, mapSize, mapSize);

edgelist = [];

for col = 1:mapSize,
    i = indices(1:mapSize,col); 
    edgelist = [edgelist;combnk(i(:),2)];
end;
for row = 1:mapSize,
    i = indices(row,1:mapSize); 
    edgelist = [edgelist;combnk(i(:),2)];
end;
for row = 1:blockSize:mapSize,
    for col = 1:blockSize:mapSize,
        i = indices(row:row+blockSize-1,col:col+blockSize-1); 
        edgelist = [edgelist;combnk(i(:),2)];
    end;
end;

nodepos = zeros(mapSize^2, 3);
for i = 1:mapSize^2,
    nodepos(i,:) = [i, 50*(1+floor((i-1)/mapSize)), 50*(1+mod(i-1, mapSize))];
end;
nodepos = num2cell(nodepos);

M = zeros(mapSize^2);
M(sub2ind(size(M), edgelist(:,1), edgelist(:,2))) = 1;

g = graph('adj', M);
gC = graphcoloring(g);
graphedit(gC, 'movenode', nodepos);
