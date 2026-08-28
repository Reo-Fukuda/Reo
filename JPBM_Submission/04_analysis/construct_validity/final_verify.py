import pandas as pd, numpy as np, sys
sys.path.insert(0,'.'); sys.path.insert(0,'../analysis')
from process import ols, simple_slope, model4, model7
from cfa import alpha
from scipy.stats import ttest_ind, t as tdist, f as fdist
D='/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/'
LP=['loss_prod_1','loss_prod_2','loss_prod_3']; LB=['LOB_item1','LOB_item2','LOB_item3']
FI=['fail_inf_1','fail_inf_2','fail_inf_3']; IC=['inferred_cost_1','inferred_cost_2','inferred_cost_3']
OK=NG=0
def chk(lab,got,want,tol):
    global OK,NG
    good=abs(got-want)<=tol; OK+= good; NG+= (not good)
    print(f"  {'OK ' if good else 'NG!'} {lab:<40} 再計算={got:>8.3f}  本文={want:>8.3f}")

print("="*74); print("更新後の本文と生データの照合"); print("="*74)
d2=pd.read_csv(D+'corrected/study2_public.csv')
s=d2[(d2.attention_1==1)&(d2.loss_prod_4==6)&(d2.I1==6)].copy()
s['M']=s[LP].mean(axis=1); s['Y']=s[LB].mean(axis=1); s['ICc']=s[IC].mean(axis=1)
print(f"\n[STUDY 2] N={len(s)}"); chk("N",len(s),276,0)
chk("男性比率",100*(s.sex==1).mean(),58.0,0.05)
ph,dg=s.loc[s.physical==1,'ICc'],s.loc[s.physical==0,'ICc']
t,_=ttest_ind(ph,dg,equal_var=False); n1,n2,q1,q2=len(ph),len(dg),ph.std(ddof=1),dg.std(ddof=1)
dfw=(q1**2/n1+q2**2/n2)**2/((q1**2/n1)**2/(n1-1)+(q2**2/n2)**2/(n2-1))
sp=np.sqrt(((n1-1)*q1**2+(n2-1)*q2**2)/(n1+n2-2))
chk("操作チェック 物理M",ph.mean(),4.69,.005); chk("操作チェック デジタルM",dg.mean(),3.41,.005)
chk("  デジタルSD",q2,1.62,.005); chk("  Welch df",dfw,242.14,.01); chk("  t",t,7.12,.005); chk("  d",(ph.mean()-dg.mean())/sp,0.87,.005)
r=model7(s.free_dummy,s.physical,s.M,s.Y,[0,1],B=5000)
chk("交互作用 F(1,272)",r['F'],11.83,.005); chk("index",r['index'],0.83,.005)
for w,nm,bw,sw,tw,lo,hi in [(1,'物理',0.91,0.24,3.85,0.44,1.37),(0,'デジタル',-0.29,0.26,-1.13,-0.79,0.21)]:
    e,se,df=simple_slope(s.free_dummy,s.physical,s.M,w); tc=tdist.ppf(.975,df)
    chk(f"単純傾斜 {nm} b",e,bw,.005); chk("  SE",se,sw,.005); chk("  t",e/se,tw,.005)
    chk("  CI下",e-tc*se,lo,.005); chk("  CI上",e+tc*se,hi,.005)
chk("条件付間接 物理",r['cond'][1]['effect'],0.63,.005); chk("条件付間接 デジタル",r['cond'][0]['effect'],-0.20,.005)
dd=ols(s.Y,[s.free_dummy,s.M]); tc=tdist.ppf(.975,dd['df'])
chk("直接効果 b",dd['b'][1],0.39,.005); chk("  t(273)",dd['b'][1]/dd['se'][1],2.63,.005)
chk("  CI上",dd['b'][1]+tc*dd['se'][1],0.69,.005)
am=ols(s.Y,[s.free_dummy,s.physical,s.free_dummy*s.physical]); red=ols(s.Y,[s.free_dummy,s.physical])
chk("媒介なし F(1,272)",(am['r2']-red['r2'])/(1-am['r2'])*am['df'],19.79,.005)

d3=pd.read_csv(D+'data/study3a_public.csv'); b=d3[(d3.attention_1==1)&(d3.I1==6)].copy()
b['X']=(b.condition==2).astype(float); b['M']=b[FI].mean(axis=1); b['Y']=b[LB].mean(axis=1)
print(f"\n[STUDY 3a] N={len(b)}"); chk("N",len(b),135,0); chk("男性比率",100*(b.sex==1).mean(),61.5,0.05)
ra=ols(b.M,[b.X]); tc=tdist.ppf(.975,ra['df'])
chk("a経路 b",ra['b'][1],-1.17,.005); chk("  t(133)",ra['b'][1]/ra['se'][1],-5.08,.005)
chk("  CI下",ra['b'][1]-tc*ra['se'][1],-1.63,.005); chk("  CI上",ra['b'][1]+tc*ra['se'][1],-0.71,.005)
m=model4(b.X,b.M,b.Y); tc=tdist.ppf(.975,m['b']['df'])
chk("b経路",m['b']['b'][2],0.59,.005); chk("  t(132)",m['b']['b'][2]/m['b']['se'][2],7.11,.005)
chk("  CI下",m['b']['b'][2]-tc*m['b']['se'][2],0.42,.005); chk("  CI上",m['b']['b'][2]+tc*m['b']['se'][2],0.75,.005)
chk("間接効果",m['indirect'],-0.69,.005); chk("直接 b",m['b']['b'][1],0.15,.005)
chk("  直接 t",m['b']['b'][1]/m['b']['se'][1],0.65,.005)
chk("総効果 b",m['c']['b'][1],-0.53,.005); chk("  総 t(133)",m['c']['b'][1]/m['c']['se'][1],-2.07,.005)
g0,g1=b.loc[b.X==0,'monetization_intent'],b.loc[b.X==1,'monetization_intent']
t,_=ttest_ind(g0,g1,equal_var=False); n1,n2,q1,q2=len(g0),len(g1),g0.std(ddof=1),g1.std(ddof=1)
dfw=(q1**2/n1+q2**2/n2)**2/((q1**2/n1)**2/(n1-1)+(q2**2/n2)**2/(n2-1))
chk("monetization n1",n1,70,0); chk("  n2",n2,65,0); chk("  Welch df",dfw,121.33,.01); chk("  t",t,3.38,.005)
print(f"\n[α] S2 LP={alpha(s[LP]):.3f} LOB={alpha(s[LB]):.3f} IC={alpha(s[IC]):.3f} | "
      f"S3a FI={alpha(b[FI]):.3f} LOB={alpha(b[LB]):.3f}  → Appendix範囲 FI .87--.92 / LOB .94--.96")
print("\n"+"="*74); print(f"一致 {OK} / 不一致 {NG}")
