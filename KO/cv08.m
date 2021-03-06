function [ I ] = cv08 (sumR, sumC, iters)
    
    nR = length(sumR);
    nC = length(sumC);
    I = zeros(nR, nC);
    cp = zeros(nR+nC, nR+nC);
    b = [sumR -sumC]';
    l = zeros(nR+nC, nR+nC);
    u = [ zeros(nR), ones(nR,nC);
          zeros(nC,nR), zeros(nC) ];
    imx = ceil(sqrt(iters));
    imy = ceil(iters/imx);
    for ic = 1:iters
        [c] = fce(cp, I);
        cp = c;
        g = graph;
        F = g.mincostflow(c,l,u,b);
        I = ceil(F(1:nR,nR+1:nR+nC));
        subplot(imx, imy, ic);
        imagesc(logical(I));
        colormap(gray);
        axis off;
        axis square;
        title(sprintf('%d',ic));
    end;

    function [c] = fce (cp, I)
        [nR,nC] = size(I);
        c = zeros(nR+nC, nR+nC);
        for row = 2:nR-1,
            for col = 2:nC-1,
                if I(row,col) == 1,
                    s = sum(sum(I(row-1:row+1,col-1:col+1)));
                    if s == 1,
                        c(row,col+nR) = 1;
                    elseif s == 2,
                        c(row,col+nR) = .2;
                    elseif s == 3,
                        c(row,col+nR) = .1;
                    end;
                else
                    if (sum(I([row-1,row+1],col)) == 2) || (sum(I(row,[col-1,col+1])) == 2),
                        c(row,col+nR) = -.1;
                    end;
                end;
            end;
        end;
        c = c + .5*cp;
        
