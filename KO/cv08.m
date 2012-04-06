function [ img ] = cv08 (sumR, sumC, iters)
    
    n1 = length(sumR);
    n2 = length(sumC);
    I = zeros(n1, n2);
    cp = zeros(n1+n2, n1+n2);
    b = [sumR -sumC]';
    l = zeros(n1+n2, n1+n2);
    u = ones(n1+n2, n1+n2);
    
    for ic = 1:iters,
        [c] = fce(cp, I);
        cp = c;
        g = graph;
        F = g.mincostflow(c,l,u,b); 
        imshow(I)
    end;
    img = I;

    function [c] = fce (cp, I)
        [n1,n2] = size(I);
        c = zeros(n1+n2, n1+n2);
        for row = 1:n1,
            for col = 1:n2,
                if row == 1 || row == n1 || col == 1 || col == n2,
                    continue;
                end;
                if I(row,col) == 1,
                    s = sum(sum(I(row-1:row+1,col-1:col+1)));
                    if s == 1,
                        c(row,col) = 1;
                    elseif s == 2.
                        c(row,col) = .2;
                    elseif s == 3.
                        c(row,col) = .1;
                    end;
                else
                    if (I(row-1,col) == 1 && I(row+1,col) == 1) || (I(row,col-1) == 1 && I(row,col+1) == 1),
                        c(row,col) = -.1;
                    end;
                end;
            end;
            c = c + .5*cp;
        end;
        