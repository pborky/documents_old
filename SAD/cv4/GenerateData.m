function [x,y]=GenerateData(num,classProb,variance)
% generuje vstupni data, body ve dvojrozmernem prostoru
% jde o dva shluky tvorici pulmesice

% Input: num = celkovy pocet datovych bodu
%        classProb = pravdepodobnosti prislusnosti bodu ke shlukum (vektor o dvou polozkach)
%        variance = mira Gaussovskeho sumu, rozptyl v ramci shluku

% default parametry
switch(nargin)
  case 0, num=100; classProb=[0.5,0.5]; variance=0.04;
  case 1, classProb=[0.5,0.5]; variance=0.04;
  case 2, variance=0.04;
end

% kontrola psti prislusnosti ke shlukum
if (length(classProb)~=2)
  error('Pravdepodobnosti prislusnosti bodu ke shlukum nejsou dve.');
end
if(sum(classProb)~=1)
  warning('Soucet psti neni 1.');
  if(sum(classProb)~=0)
    classProb=classProb/sum(classProb);
  else
    classProb=[0.5,0.5];
  end
end

% urci pocty prikladu ve shlucich
num = floor(num);  % pokud num neni integer
pos = rand(num,1);
numPtsClasses=zeros(1,2);
numPtsClasses(1)=sum(pos >= 0 & pos<classProb(1));
numPtsClasses(2)=sum(pos >= sum(classProb(1)) & pos<sum(classProb(1:2)));  
  
% generuj datove body
y=zeros(num,1);
num_pos=numPtsClasses(1); num_neg=numPtsClasses(2);
radii=ones(num,1);
phi  =rand(num_pos+num_neg,1).*pi;          

% dva pulmesice
x=zeros(num,2);
for i=1:num_pos
  x(i,1)=radii(i)*cos(phi(i));
  x(i,2)=radii(i)*sin(phi(i));
  y(i,1)=1;
end
for i=num_pos+1:num_neg+num_pos
  x(i,1)=1+radii(i)*cos(phi(i));
  x(i,2)=-radii(i)*sin(phi(i))+0.5;
  y(i,1)=2;
end
% pridej sum 
x=x + sqrt(variance)*randn(num,2);
display(['Pocet bodu ve shluku 1: ',num2str(numPtsClasses(1)),'; ve shluku 2: ',num2str(numPtsClasses(2))]);
          