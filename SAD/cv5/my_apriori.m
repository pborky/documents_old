% Funkce implementujici algoritmus apriori
% database... transakcni databaze ve forme booleovske matice, radky
% odpovidaji transakcim, sloupce polozkam
function [frequent_itemsets] = my_apriori(database, min_frequency)
% nalezeni castych mnozin polozek velikosti jedna
candidates = {};
for i = 1:size(database,2)
    candidates{i} = [i];
end
candidates = prune_itemsets(candidates, database, min_frequency);
% promenna frequent_itemsets je cell array obsahujici vystup funkce, tj.
% vsechny caste mnoziny polozek
frequent_itemsets = candidates;

while 1
    candidates = apriori_gen(candidates);
    candidates = prune_itemsets(candidates, database, min_frequency);
    if isempty(candidates), break; end;
    frequent_itemsets = [frequent_itemsets candidates];
end

% funkce Apriori-Gen z prednaskovych slajdu. Vytvari nove "kandidatske"
% mnoziny polozky delky k+1 z polozek delky k. Argument old_itemsets je cell
% array obsahujici caste mnoziny polozek delky k.
function [new_candidates] = apriori_gen(old_itemsets)
candidates_count = length(old_itemsets);
new_candidates = {};
k = 1;
for i = 1:candidates_count
    a = old_itemsets{i};
    for j = (i+1):candidates_count
        b = old_itemsets{j};
        if all(a(1:(end-1)) == b(1:(end-1)))
            new_candidates{k} = [a b(end)];
            k = k+1;
        else
            break;
        end
    end
end
for i = 1:length(new_candidates),
    for j = 1:candidates_count,
        new_candidates{i}
    end;
end;
% Sem pridejte svuj kod pro odstraneni tech "itemsetu" I ze cell-array
% new_candidates takovych, ze existuje "subitemset" I (podmnozina), ktera neni
% obsazena v cell-array old_itemsets (viz prednaska SAD, slajd "APRIORI algoritmus"
% ...

% funkce prune_itemsets odstranuje z cell array itemsets ty mnoziny
% polozek, ktere nejsou caste (pouziva explicitni vypocet relativni
% podpory), itemsers je cell array obsahujici mnoziny castych polozek (vektory cisel)
% database je transakcni databaze (booleovska matice), min_frequency je
% minimalni relativni podpora
function [pruned_itemsets] = prune_itemsets(itemsets, database, min_frequency)
frequencies = compute_frequencies(itemsets, database);
pruned_itemsets = itemsets(frequencies >= min_frequency);
%fprintf('Number of generated patterns: %d\n', length(pruned_itemsets));

% funkce pro vypocet relativni podpory seznamu mnozin polozek
% itemsets je cell array obsahujici mnoziny polozek (vektory cisel) a
% database je transakcni databaze (booleovska matice)
function [frequencies] = compute_frequencies(itemsets, database)
database_length = size(database,1);
itemsets_count = length(itemsets);
frequencies = ones(1,itemsets_count);
for i = 1:itemsets_count
    itemset = itemsets{i};
    frequencies(i) = sum(all(database(:,itemset)==1,2))/database_length;
end