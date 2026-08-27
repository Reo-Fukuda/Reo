import numpy as np, pandas as pd, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from driver import run
from cfa import fit_cfa, alpha, htmt
from scipy.stats import ttest_ind
d = pd.read_csv('../data/study2_public.csv'); a = d[d.attention_1==1].copy()
LP=['loss_prod_1','loss_prod_2','loss_prod_3']; LB=['LOB_item1','LOB_item2','LOB_item3']
IC=['inferred_cost_1','inferred_cost_2','inferred_cost_3']
run("STUDY 2  (focal mediator vs outcome)", a,
    [("Loss of Product Luxuriousness", LP), ("Loss of Brand Luxuriousness", LB)],
    "(3 attention-check failures excluded)")

print("\n--- 3-factor model including Inferred Cost ---")
X = a[LP+LB+IC].astype(float)
m3 = fit_cfa(X.values, [[0,1,2],[3,4,5],[6,7,8]])
m1 = fit_cfa(X.values, [list(range(9))])
for lab,m in [("3-factor",m3),("1-factor",m1)]:
    print(f"{lab}: chi2({m['df']})={m['chi2']:.2f}, p={m['p']:.4f}, CFI={m['cfi']:.3f}, "
          f"TLI={m['tli']:.3f}, RMSEA={m['rmsea']:.3f}, SRMR={m['srmr']:.3f}")
print("alpha Inferred Cost =", round(alpha(a[IC]),3))
print("AVE:", np.round(m3['ave'],3), " CR:", np.round(m3['cr'],3))
ph=m3['phi']; nm=["LossProd","LossBrand","InfCost"]
print("latent correlations:")
for i in range(3):
    for j in range(i+1,3):
        print(f"   r({nm[i]},{nm[j]}) = {ph[i,j]:.3f}")
print("sqrt(AVE):", np.round(np.sqrt(m3['ave']),3))
for i,j,l in [(0,1,'LP-LB'),(0,2,'LP-IC'),(1,2,'LB-IC')]:
    bl=[[0,1,2],[3,4,5],[6,7,8]]
    print(f"HTMT {l} = {htmt(X.values,[bl[i],bl[j]]):.3f}")

print("\n--- Verification of reported manipulation check (S2-4) ---")
ph_, dg = a.loc[a.physical==1, IC].mean(axis=1), a.loc[a.physical==0, IC].mean(axis=1)
t,p = ttest_ind(ph_, dg, equal_var=False)
n1,n2=len(ph_),len(dg); s1,s2=ph_.std(ddof=1),dg.std(ddof=1)
dfw = (s1**2/n1+s2**2/n2)**2/((s1**2/n1)**2/(n1-1)+(s2**2/n2)**2/(n2-1))
sp = np.sqrt(((n1-1)*s1**2+(n2-1)*s2**2)/(n1+n2-2))
print(f"physical M={ph_.mean():.2f} SD={s1:.2f} (n={n1}) | digital M={dg.mean():.2f} SD={s2:.2f} (n={n2})")
print(f"Welch t({dfw:.2f}) = {t:.2f}, p = {p:.3g}, d = {(ph_.mean()-dg.mean())/sp:.2f}")
print("manuscript: M=4.69/3.42, SD=1.32/1.60, t(252.00)=7.16, p<.001, d=0.87")
