gaussData = @(mean,sigma,n) (sigma .* randn(1,n)) + mean;
%% 1
data = [gaussData(1.4,3, 500)];
[nn,xx]  = hist(data,20);
nn = nn./sum(nn);
nn = nn./(xx(2)-xx(1));
figure;
bar(xx,nn);
hold on; plot(-10:.1:10,normpdf(-10:.1:10, 1.4,3),'r'); hold off;
hold on; plot(-10:.1:10,normpdf(-10:.1:10, mean(data),std(data)),'g'); hold off;

%% 2
nA = 100; muA = 3; sigmaA = 4;
nB = 100; muB = 15; sigmaB = 2;
data = [gaussData(muA, sigmaA, nA),gaussData(muB, sigmaB, nB)];
PA = nA/(nA+nB);
PB = nA/(nA+nB);
[nn,xx]  = hist(data,20);
nn = nn./(sum(nn).*(xx(2)-xx(1)));
figure;
bar(xx,nn);
yy = PA.*normpdf( -10:.1:20,muA,sigmaA)+PB.*normpdf( -10:.1:20,muB,sigmaB);
hold on; plot(-10:.1:20,yy,'r'); hold off;
[Mean,Std,PG] = em(data',2);
xx = -10:.1:20;
yy = PG(1).*normpdf(xx,Mean(1),Std(1)) + PG(2).*normpdf(xx,Mean(2),Std(2));
hold on; plot(xx,yy,'g'); hold off;

%% 3
nA = 100; muA = 3; sigmaA = 4;
nB = 100; muB = 15; sigmaB = 2;
data = [gaussData(muA, sigmaA, nA),gaussData(muB, sigmaB, nB)];
PA = nA/(nA+nB);
PB = nA/(nA+nB);
p = [.1; .2; .5; 1];
labels = [repmat([1], 4, nA), repmat([2], 4, nB) ];
labels(rand(4,nA+nB)>repmat(p,1,nA+nB)) = 0;
for i = 1:3,
    [nn,xx]  = hist(data,20);
    nn = nn./(sum(nn).*(xx(2)-xx(1)));
    figure;
    bar(xx,nn);
    xx = -10:.1:20;
    yy = PA.*normpdf(xx,muA,sigmaA)+PB.*normpdf(xx,muB,sigmaB);
    hold on; plot(xx,yy,'r'); hold off;
    [Mean,Std,PG] = em(data',2,labels(i,:));
    yy = PG(1).*normpdf(xx,Mean(1),Std(1))+PG(2).*normpdf( xx,Mean(2),Std(2));
    hold on; plot(xx,yy,'g'); hold off;
    P = [];
    P(1) = sum(data(labels(i,:)==1)) ./ sum(data(labels(i,:)>0));
    P(2) = sum(data(labels(i,:)==2)) ./ sum(data(labels(i,:)>0));
    mu = [ mean(data(labels(i,:)==1)), mean(data(labels(i,:)==2)) ];
    sigma = [ std(data(labels(i,:)==1)), std(data(labels(i,:)==2)) ];
    
    yy = P(1).*normpdf(xx,mu(1),sigma(1))+P(2).*normpdf( xx,mu(2),sigma(2));
    hold on; plot(xx,yy,'c'); hold off;
    title(['Semi-supervised, ',num2str(p(i))]);
    p(i)
    errorNaive =  sum(classify(data, mu, sigma, P)~=labels(4,:))/(nA+nB)
    errorEm =  sum((classify(data, Mean, Std, PG)~=labels(4,:)))/(nA+nB)
    
end

