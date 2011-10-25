function PlotData(points,labels,titlestring)
% vykresli bodovy graf
%
% Input: 
% points = souradnice bodu ve 2D prostoru (size(num_points,2))
% labels = vektor hodnot 1 nebo 2 urcujicich tridu (size(num_points,1))
% titlestring = nadpis grafu 

clf;
hold on;
title(titlestring);

plot(points(find(labels==1),1), points(find(labels==1),2), 'b*'); 
plot(points(find(labels==2),1), points(find(labels==2),2), 'ro');
