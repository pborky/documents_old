function printRules(rules, info)
% printRules(rules, info, filename)
%-----------------------------------------------------------
% created by Jan Hrdlicka, 16.9.2010
%-----------------------------------------------------------
% this function prints association rules to the textfile.
% Input: 
% rules: Association rules in Mx4 cell array. M is number of the found rules. In the 1st column are antecedents of the rules,
% in the 2nd column are consequents. In the 3rd column is support and in
% the 4th confidence. 
% info: Cell array with strings containing description of each item.

for i = 1:size(rules,1)
    antecedent = rules{i,1};
    consequent = rules{i,2};
    fprintf('(');
    for j = 1:length(antecedent)-1
        ind = antecedent(j);
        fprintf('%s and ',info{ind});
    end
    fprintf('%s)',info{antecedent(end)});
    fprintf('--->  (');
    for j = 1:length(consequent)-1
        ind = consequent(j);
        fprintf('%s and ',info{ind});
    end
    fprintf('%s),  ',info{consequent(end)});
    fprintf('Support = %0.2f',rules{i,3});
    fprintf(', Confidence = %0.2f \n',rules{i,4});
end
