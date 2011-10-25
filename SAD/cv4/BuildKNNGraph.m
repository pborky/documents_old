function W = BuildKNNGraph(S,k)
% z matice podobnosti vytvoří matici sousednosti orientovaného kNN grafu
% Wij je nenulova pokud uzel j patri mezi k nejblizsich sousedu uzlu i, matice neni symetricka

% Input: 
% S = matice podobnosti, ctvrecova, symetricka, bez negativnich hodnot
% k = parametr propojeni kNN grafu, pocet sousedu

% test spravnosti
if (size(S,1) ~= size(S,2))
  error('Matice neni ctvercova!')
end

n = size(S,1);

% vylouceni smycek
for it=1:n
  S(it,it) = 0; 
end

% vytvor matici sousednosti
W = S; 
for it = 1:n
  % serad body podle podobnosti
  [~,order] = sort(S(it,:), 'descend'); 
  % u vsech bodu, ktere nejsou mezi prvnimi k nuluj matici W
  W(it, order(k+1:end)) = 0;
end

Wt = W';
W(Wt>0) = Wt(Wt>0);

  
