import numpy as np, pandas as pd, sys
sys.path.insert(0,'.')
import cfa as C
from scipy.stats import norm, pearsonr
FI=['fail_inf_1','fail_inf_2','fail_inf_3']; LB=['LOB_item1','LOB_item2','LOB_item3']
LP=['loss_prod_1','loss_prod_2','loss_prod_3']
S=[("Study 2","../data/study2_public.csv",LP+LB),("Study 3a","../data/study3a_public.csv",FI+LB),
   ("Study 3b","../data/study3b_public.csv",FI+LB),("Study 3c","../data/study3c_public.csv",FI+LB)]
minz=[]; minr_p=[]; minlam=[]
for nm,path,cols in S:
    d=pd.read_csv(path); a=d[d.attention_1==1]; X=a[cols].astype(float).values
    n,p=X.shape; Sc=np.cov(X,rowvar=False,ddof=1); blocks=[[0,1,2],[3,4,5]]
    m=C.fit_cfa(X,blocks)
    # refit to recover raw params
    from scipy.optimize import minimize
    nload=6; ncov=1
    sd=np.sqrt(np.diag(Sc))
    x0=np.concatenate([sd*0.7, np.diag(Sc)*0.5, [0.3]])
    bnds=[(None,None)]*6+[(1e-6,None)]*6+[(-0.999,0.999)]
    r=minimize(C._fml,x0,args=(Sc,blocks,2,p),method="L-BFGS-B",bounds=bnds,
               options={"maxiter":20000,"ftol":1e-14,"gtol":1e-12})
    se=C.param_se(r.x,Sc,blocks,2,p,n)
    z=r.x[:6]/se[:6]
    zphi=r.x[12]/se[12]
    R=np.corrcoef(X,rowvar=False); ps=[pearsonr(X[:,i],X[:,j])[1] for i in range(6) for j in range(i+1,6)]
    print(f"{nm}: min |z| loading = {np.min(np.abs(z)):.2f}, phi z = {zphi:.2f}, "
          f"min std loading = {np.min(np.abs(m['loadings'][m['loadings']!=0])):.3f}, "
          f"max corr p = {max(ps):.2e}")
    minz.append(np.min(np.abs(z))); minr_p.append(max(ps))
    minlam.append(np.min(np.abs(m['loadings'][m['loadings']!=0])))
print(f"\nOVERALL: smallest |z| for any loading = {min(minz):.2f} "
      f"(two-sided p = {2*(1-norm.cdf(min(minz))):.2e})")
print(f"smallest standardised loading across all studies = {min(minlam):.3f}")
print(f"largest item-correlation p across all studies = {max(minr_p):.2e}")
