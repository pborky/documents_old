function [s, Cmax] = bratleyAlg(p, r, d, UB, open, closed)

%Inicializuj s, Cmax, odhadni UB pokud je prazdne (1.volani)
s = [];
Cmax = [];
if isempty(open) && isempty(closed),
    open = 1:length(p);
    closed= [];
end;
if isempty(UB)
    UB = max(d(open));
end

%Podminka 1
if min(r+p > d)
    return          %Toto vetveni nevede k pripustnemu rozvrhu
end

%Spocti c
c = 0;
for j = closed,
    c = max(r(j),c)+p(j);
end

LB = max(max(min(r(open)),c)+sum(p(open)),max(r(open)+p(open)));

%Podminka 2
if LB > UB,
    return          %Toto vetveni nevede k pripustnemu rozvrhu
end

%Vetvi kazdy vrchol na prislusny pocet dalsich
for i = open,
    c = max(c,r(i))+p(i);
    
    %Pokud uz zbyva jen jedna uloha
    if length(open) == 1,
        %Spocti s, Cmax a aktualizuj UB
        s = [];
        pp = [];
        for j = [closed,i],
            if isempty(s),
                s = [r(j)];
                pp = [p(j)];
            else
                s = [s, max(max(s+pp),r(j)) ];
                pp = [pp,p(j)];
            end;
        end;
        s = [closed,i];
        Cmax = c;
        UB = max(d(open(open ~= i)));
        
    %Pokud je jeste treba dal vetvit
    else
        %Vyres podproblem rekurzivnim volanim s upravenymi vstupy (treba s vyuzitim delky castecneho reseni ;-) )
        [ss,cc] = bratleyAlg(p, r, d, UB, open(open ~= i), [closed,i]);
            
        %Pokud byl podproblem vyresen
        if ~isempty(ss) && (isempty(Cmax) || (cc < Cmax)),
            %Spoj reseni podproblemu s aktualnim prirazenim ve vrcholu
            s = ss;
            Cmax = cc;
            UB = max(d(open(open ~= i)));
        end
    end
end