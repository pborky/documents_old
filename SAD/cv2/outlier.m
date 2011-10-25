%%  ###Outlier values###
clear all
load('outlier_data.mat')



%% Assignment 3:  Remove outliers using k-means

X = data;
m = 10;
th = 1e-100;
R = 100;
nReplicates = 40;

% #### Outlier removal algorithm ####
% IN: 
%       X     : data samples  
%       m     : number of clusters
%       th    : threshold for distrortion
%       R     : maximal number of algorithm steps
%       nReplicates : number of runs of k-means (matlab returns the best partitioning)
% OUT:
%       X     : data samples without outliers

% init
i = 0;
outliers = [];
while(1)    
    i = i+1;
    % number of samples
    len = size(X,1);
    % find centroids( newC) and partitioning (newP)
    [newP, newC] = kmeans(X,m,'replicates',nReplicates);     
     
    % %%%%%%%%% Zde doplnte kod dle ukolu 3 %%%%%%%%%%%%%    
    newX = X;
    % ### BEGIN of outlier removal code ###
    for ic = 1:m,
        ix = newP==ic;
        if sum(ix) > 1,
            dists = sqrt(sum((X(ix, :) - repmat(newC(ic,:),sum(ix),1)).^2,2));
            [smax, ismax] = max(dists);
            [smin, ismin] = min(dists);
            mu = mean(X(ix, :));
            Sigma = cov(X(ix, :));            
            f = exp(-(X(ismax,:) - mu)*(Sigma\((X(ismax,:) - mu)')));
            if f < th,
                ix = find(ix);
                outliers = [outliers;newX(ix(ismax),:)];
                newP(ix(ismax),:) = NaN;
                newX(ix(ismax),:) = NaN;
                newC(:); %%% no impact?
            end;
        else
            outliers = [outliers;newX(ix,:)];
            newP(ix) = NaN;
            newX(ix,:) = NaN;
            newC(ic,:) = NaN;
            m = m - 1;
        end;
    end;
    newX(max(isnan(newX),[],2),:) = [];
    newP(isnan(newP)) = [];
    newC(max(isnan(newC),[],2),:) = [];
    % END of outlier removal code
    
    % new number of samples
    new_len = size(newX,1);    
    % compute new centers and partitioning    
    X = newX; 
    
    % stop conditions
    if i>R | new_len==len    
        break 
    end        
end
outliers

% compute optimal partitioning on the new data
[P, C, sumd] = kmeans(X, m,'replicates',nReplicates);

figure
subplot(1,2,1)
scatter(X(:,1), X(:,2), ones(size(X,1),1)*10, P)
hold on
scatter(C(:,1), C(:,2), ones(size(C,1),1)*40)
title('Data without outliers')
subplot(1,2,2)
[P, C] = kmeans(data, m);
scatter(data(:,1), data(:,2), ones(size(data,1),1)*10, P)
title('Data with outliers')

figure
subplot(1,2,1)
scatter(X(:,1), X(:,2))
title('Data without outliers (multivariate approach)');
subplot(1,2,2)
boxplot(X)


