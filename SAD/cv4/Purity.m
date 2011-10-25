function pur=Purity(labels,clusters)
% vypocita ryzost shlukovani srovnanim se znamou anotaci
% predpoklada prave 2 tridy vzorku
%
% Input: 
% labels = vektor hodnot 1 nebo 2 urcujicich tridu (size(num_points,1))
% points = vektor hodnot 1 nebo 2 urcujicich prislusnost ke shlukum (size(num_points,2))

if size(labels,1)~=size(clusters,1)
  warning('Delka vektoru labels a clusters se lisi.')
end

correct=max(sum(labels==clusters),sum(labels~=clusters));
pur=correct/size(labels,1);