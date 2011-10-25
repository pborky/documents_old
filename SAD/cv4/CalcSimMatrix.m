function S=CalcSimMatrix(points,sigma)
% generuje matici podobnosti mezi body
% euklidovska vzdalenost a gaussovsky kernel

% Input: points = souradnice bodu ve 2D prostoru (size(num_points,2))
%        sigma = mira Gaussovskeho sumu, rozptyl v ramci shluku

% default parametry
switch(nargin)
  case 0, error('Chybi souradnice datovych bodu.');
  case 1, sigma=0.5;
end

D=DistEuclidean(points,points);
S = exp(- D / (2 * sigma^2));

function D = DistEuclidean(X,Y)
  if( ~isa(X,'double') || ~isa(Y,'double'))
      error( 'Vstupy musi byt typu double.'); end;
  m = size(X,1); n = size(Y,1);  
  Yt = Y';  
  XX = sum(X.*X,2);        
  YY = sum(Yt.*Yt,1);      
  D = XX(:,ones(1,n)) + YY(ones(1,m),:) - 2*X*Yt;
    

        