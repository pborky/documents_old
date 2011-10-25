function W = BuildEpsilonGraph(S,eps)
% z podobnostni matice vytvori matici sousednosti
% metoda epsilon-okoli -- vypousti hrany s podobnosti mensi nez je prahova
 
% Input: 
% S = matice podobnosti, ctvercova, symetricka
% eps = prahova hodnota epsilon
 

if (size(S,1) ~= size(S,2))
  error('Matice neni ctvercova!')
end
n = size(S,1);
  
% nastav diagonalu na 0
for it=1:n
  S(it,it) = 0; 
end
 
W = (S >= eps) .* S; 
  
   
  
