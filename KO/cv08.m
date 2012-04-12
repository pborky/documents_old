function [ I ] = cv08 (sumR, sumC, iters)
    
    nR = length(sumR);
    nC = length(sumC);
    I = zeros(nR, nC);
    cp = zeros(nR+nC, nR+nC);
    b = [sumR -sumC]';
    l = zeros(nR+nC, nR+nC);
    u = [ zeros(nR), ones(nR,nC);
          zeros(nC,nR), zeros(nC) ];
    t=' *';
    img = I;
    for ic = 1:iters,
        [c] = fce(cp, I);
        cp = c;
        g = graph;
        F = g.mincostflow(c,l,u,b);
        I = ceil(F(1:nR,nR+1:nR+nC));
	fprintf('iter=%d\n', ic);
        fprintf('change=%d\n',sum(sum(abs(I-img))));
	t(I+1)
	img = I;
    end;
    fprintf('diff: R=%f; C=%f;\n', sum(sumR~=sum(I,1)), sum(sumC'~=sum(I,2)));

    function [c] = fce (cp, I)
        [nR,nC] = size(I);
        c = zeros(nR+nC, nR+nC);
        for row = 1:nR,
            for col = 1:nC,
                if row == 1 || row == nR || col == 1 || col == nC,
                    continue;
                end;
                if I(row,col) == 1,
                    s = sum(sum(I(row-1:row+1,col-1:col+1)));
                    if s == 1,
                        c(row,col+nR) = 1;
                    elseif s == 2.
                        c(row,col+nR) = .2;
                    elseif s == 3.
                        c(row,col+nR) = .1;
                    end;
                else
                    if (I(row-1,col) == 1 && I(row+1,col) == 1) || (I(row,col-1) == 1 && I(row,col+1) == 1),
                        c(row,col+nR) = -.1;
                    end;
                end;
            end;
            c = c + .5*cp;
        end;
        
