ndata = 200;
means = [.55 .45; .55 .45; .55 .45];
covars = [ .005; .01; .02 ];
kernSigma = .32;
%% gen data prepare S
for i =1:length(covars),
    [x,y]=GenerateData(ndata,means(i,:),covars(i,:));
    X(:,:,i) = x; Y(:,i) = y;
    figure;
    PlotData(x,y,sprintf('original data sigma = %f',covars(i,:)));
    S(:,:,i) = CalcSimMatrix(x,kernSigma);
end;
pause
%% kmeans
for i =1:length(covars),
    yy = kmeans(X(:,:,i),2);
    figure;
    PlotData(X(:,:,i),yy,sprintf('k-means sigma = %f',covars(i,:)));
    fprintf('k-menas purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:))
end;
pause
%% (norm.) laplacian from S
for i =1:length(covars),    
    L = CalcLaplacian(S(:,:,i));
    yy = kmeans(L, 2);
    fprintf('laplace purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('laplace sigma = %f',covars(i,:)));
    
    Ln = diag(sum(S(:,:,i)))\L;
    yy = kmeans(Ln, 2);
    fprintf('norm laplace purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('norm.laplace sigma = %f',covars(i,:)));
end;
pause
%% (norm.) laplacian from S cuted by predicate S(i,j) < eps
eps = .45;
for i =1:length(covars),
    Weps = BuildEpsilonGraph(S(:,:,i),eps);
    figure;
    PlotGraph(X(:,:,i),Weps,'Epsilon reduced graph');
    
    L = CalcLaplacian(Weps);
    yy = kmeans(L, 2);
    fprintf('laplace+eps purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('laplace+eps sigma = %f',covars(i,:)));
    
    Ln = diag(sum(Weps))\L;
    yy = kmeans(Ln, 2);
    fprintf('norm laplace+eps purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('norm.laplace+eps sigma = %f',covars(i,:)));
end;
pause
%% (norm.) laplacian from S cuted by k-nearest neighbour
k = 5;
for i =1:length(covars),   
    Wknn = BuildKNNGraph(S(:,:,i), k);
    figure;
    PlotGraph(X(:,:,i),Wknn,'Knn reduced graph');
    
    L = CalcLaplacian(Wknn);
    yy = kmeans(L, 2);
    fprintf('laplace+knn purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('laplace+knn sigma = %f',covars(i,:)));

    Ln = diag(sum(Wknn))\L;
    yy = kmeans(Ln, 2);
    fprintf('norm laplace+knn purity = %f, sigma = %f\n', Purity(Y(:,i),yy), covars(i,:));
    figure;
    PlotData(X(:,:,i),yy,sprintf('norm.laplace+knn sigma = %f',covars(i,:)));
end;

