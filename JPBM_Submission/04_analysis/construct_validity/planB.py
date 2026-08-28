import pandas as pd, numpy as np, sys
sys.path.insert(0,'.'); sys.path.insert(0,'../analysis')
from process import ols, simple_slope, model4, model7
from cfa import alpha, fit_cfa, htmt
from scipy.stats import ttest_ind, t as tdist
D='/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/'
FI=['fail_inf_1','fail_inf_2','fail_inf_3']; LB=['LOB_item1','LOB_item2','LOB_item3']
LP=['loss_prod_1','loss_prod_2','loss_prod_3']; IC=['inferred_cost_1','inferred_cost_2','inferred_cost_3']

def cmp(name, old, new, dec=3):
    ch = "" if abs(old-new)<5*10**-(dec+1) else "  ←変化"
    print(f"    {name:<38} {old:>9.{dec}f} → {new:>9.{dec}f}{ch}")

# ================= STUDY 2 =================
print("="*92); print("STUDY 2   N = 280 → 276"); print("="*92)
d2=pd.read_csv(D+'corrected/study2_public.csv')
A=d2[d2.attention_1==1].copy()
B=d2[(d2.attention_1==1)&(d2.loss_prod_4==6)&(d2.I1==6)].copy()
for s in (A,B):
    s['M']=s[LP].mean(axis=1); s['Y']=s[LB].mean(axis=1); s['ICc']=s[IC].mean(axis=1)
print(f"  N: {len(A)} → {len(B)}   除外追加: {sorted(set(A.participant_id)-set(B.participant_id))}")
print("\n  [操作チェック S2-4]")
for lab,s in [('old',A),('new',B)]:
    ph,dg=s.loc[s.physical==1,'ICc'],s.loc[s.physical==0,'ICc']
    t,p=ttest_ind(ph,dg,equal_var=False); n1,n2,s1,s2=len(ph),len(dg),ph.std(ddof=1),dg.std(ddof=1)
    dfw=(s1**2/n1+s2**2/n2)**2/((s1**2/n1)**2/(n1-1)+(s2**2/n2)**2/(n2-1))
    sp=np.sqrt(((n1-1)*s1**2+(n2-1)*s2**2)/(n1+n2-2))
    if lab=='old': o=(ph.mean(),s1,dg.mean(),s2,dfw,t,(ph.mean()-dg.mean())/sp)
    else:
        n=(ph.mean(),s1,dg.mean(),s2,dfw,t,(ph.mean()-dg.mean())/sp)
        for i,nm in enumerate(['物理 M','物理 SD','デジタル M','デジタル SD','Welch df','t','d']): cmp(nm,o[i],n[i])
print("\n  [PROCESS Model 7]")
res={}
for lab,s in [('old',A),('new',B)]:
    r=model7(s.free_dummy,s.physical,s.M,s.Y,[0,1],B=5000)
    dd=ols(s.Y,[s.free_dummy,s.M])
    ss={'交互作用 ΔR²':r['dR2'],'  F':r['F'],'index of mod med':r['index']}
    for w,nm in [(1,'物理'),(0,'デジタル')]:
        e,se,df=simple_slope(s.free_dummy,s.physical,s.M,w); tc=tdist.ppf(.975,df)
        ss[f'単純傾斜 {nm} b']=e; ss[f'  SE']=se; ss[f'  t']=e/se
        ss[f'  CI下 {nm}']=e-tc*se; ss[f'  CI上 {nm}']=e+tc*se
        ss[f'条件付間接効果 {nm}']=r['cond'][w]['effect']
    ss['直接効果 b']=dd['b'][1]; ss['  直接 t']=dd['b'][1]/dd['se'][1]
    ss['α LossProd']=alpha(s[LP]); ss['α LOB']=alpha(s[LB]); ss['α InfCost']=alpha(s[IC])
    res[lab]=ss
for k in res['old']: cmp(k,res['old'][k],res['new'][k])

# ================= STUDY 3a =================
print("\n"+"="*92); print("STUDY 3a   N = 138 → 135"); print("="*92)
d3=pd.read_csv(D+'data/study3a_public.csv')
A=d3[d3.attention_1==1].copy(); B=d3[(d3.attention_1==1)&(d3.I1==6)].copy()
for s in (A,B):
    s['X']=(s.condition==2).astype(float); s['M']=s[FI].mean(axis=1); s['Y']=s[LB].mean(axis=1)
print(f"  N: {len(A)} → {len(B)}   除外追加: {sorted(set(A.participant_id)-set(B.participant_id))}")
print(f"  男性比率: {100*(A.sex==1).mean():.1f}% → {100*(B.sex==1).mean():.1f}%")
print("\n  [PROCESS Model 4]")
res={}
for lab,s in [('old',A),('new',B)]:
    m=model4(s.X,s.M,s.Y)
    res[lab]={'b (M→Y)':m['b']['b'][2],'  SE':m['b']['se'][2],'  t':m['b']['b'][2]/m['b']['se'][2],
              '間接効果':m['indirect'],'  BootSE':m['boot_se'],'  CI下':m['ci'][0],'  CI上':m['ci'][1],
              '直接効果 b':m['b']['b'][1],'  直接 t':m['b']['b'][1]/m['b']['se'][1],
              '総効果 b':m['c']['b'][1],'  総 t':m['c']['b'][1]/m['c']['se'][1],
              'α FailureInf':alpha(s[FI]),'α LOB':alpha(s[LB])}
for k in res['old']: cmp(k,res['old'][k],res['new'][k])
