function [newAnt, newCon] = newGenerationRules(antecedents,consequents)
%[newAnt, newCon] = newGenerationRules(antecedents,consequents)
%-----------------------------------------------------------
% created by Jan Hrdlicka, 16.9.2010
%-----------------------------------------------------------
%Creates new generation of antecedents and consequents by moving
%antecedents to consequents
newAnt = {};
newCon = {};
for i = 1:size(antecedents,1)
    ant = antecedents{i,1};
    con = consequents{i,1};
    if length(ant)==1
    else   
        for j = 1:length(ant)
            antCand = ant;
            antCand(j) = [];
            newAnt{end+1,1} = antCand;
            conCand = con;
            conCand(end+1) = ant(j);
            conCand = sort(conCand);
            newCon{end+1,1} = conCand;
        end
    end
end