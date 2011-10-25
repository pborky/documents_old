function [Mean,Std,PG] = em(x,nr_groups,labels)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  [Mean,Std,P] = EM(x,nr_groups,P_0,max_nr_it);
%  EM algo for 1-dimensional Gaussian Mixture Model
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  INPUT:
%  x.............data  with  [nr_pts,nr_dim] = size(x)
%  nr_groups.....number of Gaussians
%  labels........class labels
%
%  OUTPUT:
%  Mean..........Mean(i) is the mean of the i-th Gaussian
%  Std...........Std(i) is the standard deviation of the i-th Gaussian
%  PG............PG(i) is the prior probability of the i-th Gaussian
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

max_nr_it = 1000;
nr_pts = length(x);
 
if nr_groups >1  % divide RANGE in equal parts
    if nargin == 2
        P_0 = initialize_em_range_based(x,nr_groups);
    elseif nargin == 3
        P_0 = initialize_em_range_based(x,nr_groups,labels);    % See end of this file
    end
else % only one group: trivial assignment
    P_0 = ones(nr_pts,1);   
end    

P = P_0;
Mean = zeros(nr_groups,1);
Std = ones(nr_groups,1);

green_light = 1;
nr_it = 0;

while (green_light == 1) & (nr_it < max_nr_it) 
	nr_it  = nr_it + 1;
    
    P_new = zeros(size(P));

    for k = 1 : nr_groups 
        PP = P(:,k);
        D = x.* PP;    %  Data weighted with P-matrix
        if sum(P(:,k)) ~=0   % there are datapoints assigned to this group
            mean_grp = sum(D)/sum(PP);
            var_grp = sum(((x - mean_grp).^2).*PP)/sum(PP);  
	        std_grp = sqrt(var_grp);
        else
            mean_grp = 0;
            std_grp = 1;
        end
       
        F =  normpdf(x,mean_grp,std_grp);
        Mean(k,:) = mean_grp;
        Std(k,:) = std_grp(:)';
        P_new(:,k) = F;
    end

    P_old = P;
    P = P_new;
    
    if nargin == 3,
        for i = 1:max(labels),
            fix = zeros(1,size(P,2));
            fix(i) = 1;
            P(labels==i,:) = repmat(fix,  sum(labels==i), 1);
        end
    end

    %  Renormalize
    P_sum = sum(P,2);  PP_sum = P_sum *ones(1,nr_groups);
    
    % Precautions to avoid "divide by zero"
    u_zero = find(P_sum < 10^(-200)); %
    
    if ~isempty(u_zero)
        % create uniform distribution
        Q = zeros(nr_pts,nr_groups);  Q(u_zero,:) = 1/nr_groups;
        N  = ones(nr_pts,nr_groups);  N(u_zero,:)=0;
        PP_sum(u_zero,:) = 1;
        P = (P./PP_sum).*N  + Q;
    else
    	P = P./(sum(P,2)*ones(1,nr_groups));
    end 
end

% 
% PACKAGE RESULTS FOR EXPORT
%===========================

% P is matrix of size [nr_pts,nr_gauss] such that each row contains the
% soft assignment of the corresponding point to the different Gaussian components. 
% By summing over the rows, we get the proportional contribution of each
% Gaussian. 

PG = sum(P,1);
PG = PG'/nr_pts;

return

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function P_0 = initialize_em_range_based(x,nr_groups,labels)

nr_pts = length(x);
P_raw = zeros(nr_pts,nr_groups);

if nargin == 2    
    xrange = range(x);
    dx = xrange/(nr_groups-1);
    ss = 0.5*xrange/(2*(nr_groups-1));

    xc = min(x) + dx*(0:nr_groups-1);

    for j = 1:nr_groups
        P_raw(:,j) = normpdf(x,xc(j),ss);  
    end
elseif nargin == 3
    [Means Stds PGs] = estGauss(x, nr_groups, labels);
    for i = 1:nr_pts
        s = 0;
        for j = 1:nr_groups
            s = s + PGs(j)*normpdf(x(i), Means(j), Stds(j));
        end
        for j = 1:nr_groups
            P_raw(i,j) = PGs(j)*normpdf(x(i), Means(j), Stds(j))/s;
        end
    end
end

%  make sure each row sums to 1:
P_0 = P_raw./(sum(P_raw,2)*ones(1,nr_groups));

if nargin == 3
    for i = 1:nr_groups
        indexes = labels == i;
        P_0(indexes,:) = zeros(sum(indexes),nr_groups);
        P_0(indexes,i) = 1;
    end
end
return

function [Mean,Std,PG] = estGauss(x, nr_groups, labels)
x = x(labels ~= 0);
labels = labels(labels ~= 0);

Mean = zeros(1,nr_groups);
Std = zeros(1,nr_groups);
PG = zeros(1,nr_groups);

for i = 1:nr_groups
    xi = x(labels == i);
    Mean(i) = mean(xi);
    Std(i) = std(xi);
    PG(i) = length(xi)/length(labels);
end

return
