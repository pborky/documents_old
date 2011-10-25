function [labelsTest] = classify(data, mu, sigma, Prior)
    F = [];
    F(1,:) = Prior(1)*normpdf(data', mu(1), sigma(1));
    F(2,:) = Prior(2)*normpdf(data', mu(2), sigma(2));
    [~,labelsTest] = max(F,[],1);
end
