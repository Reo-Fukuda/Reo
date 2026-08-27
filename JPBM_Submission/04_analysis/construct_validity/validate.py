import numpy as np, pandas as pd, sys
sys.path.insert(0,'.')
from cfa import fit_cfa
from factor_analyzer import ConfirmatoryFactorAnalyzer, ModelSpecificationParser

d = pd.read_csv('../data/study3a_public.csv')
cols = ['fail_inf_1','fail_inf_2','fail_inf_3','LOB_item1','LOB_item2','LOB_item3']
X = d[cols].astype(float)
spec = ModelSpecificationParser.parse_model_specification_from_dict(
    X, {"FI": cols[:3], "LOB": cols[3:]})
cfa = ConfirmatoryFactorAnalyzer(spec, disp=False)
cfa.fit(X.values)
sd = X.std(ddof=1).values
fa_load = cfa.loadings_
# factor_analyzer fixes factor variances at 1 -> unstandardised loadings; standardise by implied SD
sigma = fa_load @ cfa.factor_varcovs_ @ fa_load.T + np.diag(cfa.error_vars_.ravel())
sdm = np.sqrt(np.diag(sigma))
print("factor_analyzer standardised loadings:")
print(np.round(fa_load / sdm[:,None], 3))
print("factor_analyzer factor corr:", round(cfa.factor_varcovs_[0,1] /
      np.sqrt(cfa.factor_varcovs_[0,0]*cfa.factor_varcovs_[1,1]), 3))
m = fit_cfa(X.values, [[0,1,2],[3,4,5]])
print("\nour standardised loadings:")
print(np.round(m['loadings'],3))
print("our factor corr:", round(m['phi'][0,1],3))

# independent chi-square check via the ML discrepancy at the factor_analyzer solution
S = np.cov(X.values, rowvar=False, ddof=1); n,p = X.shape
F = np.linalg.slogdet(sigma)[1] + np.trace(S@np.linalg.inv(sigma)) - np.linalg.slogdet(S)[1] - p
print("\nchi2 at factor_analyzer solution:", round((n-1)*F,3), " ours:", round(m['chi2'],3))
