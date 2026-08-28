import pandas as pd, numpy as np, sys
sys.path.insert(0,'.'); from process import ols
sys.path.insert(0,'../analysis'); from cfa import alpha
from scipy.stats import ttest_ind
D='/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/'
FI=['fail_inf_1','fail_inf_2','fail_inf_3']; LB=['LOB_item1','LOB_item2','LOB_item3']

def model6(X,M1,M2,Y,B=5000,seed=20260828):
    X,M1,M2,Y=(np.asarray(v,float) for v in (X,M1,M2,Y))
    r1=ols(M1,[X]); r2=ols(M2,[X,M1]); r3=ols(Y,[X,M1,M2])
    a1,a2,d21=r1['b'][1],r2['b'][1],r2['b'][2]
    cp,b1,b2=r3['b'][1],r3['b'][2],r3['b'][3]
    rng=np.random.default_rng(seed); n=len(X); B1=[];B2=[];B3=[];TT=[]
    for _ in range(B):
        i=rng.integers(0,n,n)
        q1=ols(M1[i],[X[i]])['b']; q2=ols(M2[i],[X[i],M1[i]])['b']; q3=ols(Y[i],[X[i],M1[i],M2[i]])['b']
        p1=q1[1]*q3[2]; p2=q2[1]*q3[3]; p3=q1[1]*q2[2]*q3[3]
        B1.append(p1);B2.append(p2);B3.append(p3);TT.append(p1+p2+p3)
    f=lambda arr:(np.std(arr,ddof=1),np.percentile(arr,[2.5,97.5]))
    return dict(r1=r1,r2=r2,r3=r3,a1=a1,a2=a2,d21=d21,cp=cp,b1=b1,b2=b2,
                paths={'a1b1':(a1*b1,)+f(B1),'a2b2':(a2*b2,)+f(B2),
                       'a1d21b2':(a1*d21*b2,)+f(B3),'total':(a1*b1+a2*b2+a1*d21*b2,)+f(TT)})

d=pd.read_csv(D+'data/study3a_public.csv')
specs=[("A) 現在の記載 = N=135 (attention_1 & I1==6), 1項目", (d.attention_1==1)&(d.I1==6), False),
       ("B) 修正① N=138 (現行の除外基準), 1項目",              d.attention_1==1,             False),
       ("C) 修正② N=138, 2項目 (monetization_intent + F1)",  d.attention_1==1,             True)]
res={}
for lab,f,two in specs:
    a=d[f].copy()
    a['X']=(a.condition==2).astype(float)
    a['M1']=a[['monetization_intent','F1']].mean(axis=1) if two else a.monetization_intent
    a['M2']=a[FI].mean(axis=1); a['Y']=a[LB].mean(axis=1)
    m=model6(a.X,a.M1,a.M2,a.Y); m['n']=len(a); m['two']=two
    g0,g1=a.loc[a.X==0,'M1'],a.loc[a.X==1,'M1']
    n1,n2,s1,s2=len(g1),len(g0),g1.std(ddof=1),g0.std(ddof=1)
    t,p=ttest_ind(g1,g0,equal_var=False)
    dfw=(s1**2/n1+s2**2/n2)**2/((s1**2/n1)**2/(n1-1)+(s2**2/n2)**2/(n2-1))
    sp=np.sqrt(((n1-1)*s1**2+(n2-1)*s2**2)/(n1+n2-2))
    m['tt']=(g0.mean(),s2,g1.mean(),s1,dfw,abs(t),p,abs(g0.mean()-g1.mean())/sp)
    if two: m['alpha']=alpha(a[['monetization_intent','F1']])
    res[lab]=m

print("="*100); print("SI C / 本文3a  monetization 分析 — 3通りの比較"); print("="*100)
print(f"\n{'':<44}{'A) 記載(N=135)':>18}{'B) N=138 1項目':>18}{'C) N=138 2項目':>18}")
labs=[s[0] for s in specs]
def row(name,fn,fmt="{:>18.3f}"):
    print(f"  {name:<42}" + "".join(fmt.format(fn(res[l])) for l in labs))
row("N",                lambda m:m['n'], "{:>18.0f}")
row("t検定 M (有償条件)", lambda m:m['tt'][0])
row("t検定 M (無償条件)", lambda m:m['tt'][2])
row("Welch t",          lambda m:m['tt'][5])
row("  df",             lambda m:m['tt'][4])
row("  Cohen d",        lambda m:m['tt'][7])
print()
row("a1 (X->M1)",       lambda m:m['a1'])
row("  SE",             lambda m:m['r1']['se'][1])
row("  t",              lambda m:m['a1']/m['r1']['se'][1])
row("a2 (X->M2)",       lambda m:m['a2'])
row("d21 (M1->M2)",     lambda m:m['d21'])
row("  t",              lambda m:m['d21']/m['r2']['se'][2])
row("b1 (M1->Y)",       lambda m:m['b1'])
row("  t",              lambda m:m['b1']/m['r3']['se'][2])
row("b2 (M2->Y)",       lambda m:m['b2'])
row("c' 直接効果",        lambda m:m['cp'])
row("  p",              lambda m:2*(1-abs(np.tanh(9))) if False else m['cp']/m['r3']['se'][1])
print()
row("R2 Model1",        lambda m:m['r1']['r2'])
row("R2 Model2",        lambda m:m['r2']['r2'])
row("R2 Model3",        lambda m:m['r3']['r2'])
print("\n  --- 間接効果 (5,000 bootstrap) ---")
for k,nm in [('a1b1','X->M1->Y (a1b1)'),('a2b2','X->M2->Y (a2b2)'),
             ('a1d21b2','X->M1->M2->Y'),('total','総間接効果')]:
    print(f"  {nm:<42}" + "".join(f"{res[l]['paths'][k][0]:>18.3f}" for l in labs))
    print(f"  {'  95%CI':<42}" + "".join(f"{'['+format(res[l]['paths'][k][2][0],'.2f')+', '+format(res[l]['paths'][k][2][1],'.2f')+']':>18}" for l in labs))
print(f"\n  2項目版の alpha = {res[labs[2]]['alpha']:.3f}")
print("\n  ※ SI C の現行記載: a1=-0.88 a2=-0.93 d21=0.27 b1=-0.17 b2=0.65 c'=0.07")
print("     間接効果: a1b1=0.15[0.00,0.34] a2b2=-0.60[-0.98,-0.28] a1d21b2=-0.15[-0.32,-0.04] 総=-0.61[-1.01,-0.26]")
