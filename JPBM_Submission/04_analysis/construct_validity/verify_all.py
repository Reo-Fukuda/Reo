import pandas as pd, numpy as np, sys
sys.path.insert(0,'.')
from process import model4, model7, ols, simple_slope
from scipy.stats import t as tdist
D='/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/'
OK=[];NG=[]
def chk(label, got, want, tol):
    d=abs(got-want); (OK if d<=tol else NG).append((label,got,want,d))
    print(f"  {'OK ' if d<=tol else 'NG!'} {label:<46} 再計算={got:>8.3f}  記載={want:>8.3f}  差={d:.3f}")

FI=['fail_inf_1','fail_inf_2','fail_inf_3']; LB=['LOB_item1','LOB_item2','LOB_item3']

print("="*82); print("STUDY 3a  (PROCESS Model 4)"); print("="*82)
a=pd.read_csv(D+'data/study3a_public.csv').query('attention_1==1').copy()
a['X']=(a.condition==2).astype(float); a['M']=a[FI].mean(axis=1); a['Y']=a[LB].mean(axis=1)
m=model4(a.X,a.M,a.Y)
chk("b (M->Y)",           m['b']['b'][2], 0.60,0.005); chk("  SE",m['b']['se'][2],0.08,0.005)
chk("  t",                m['b']['b'][2]/m['b']['se'][2], 7.14,0.05)
chk("indirect Effect",    m['indirect'],-0.69,0.005);  chk("  BootSE",m['boot_se'],0.17,0.02)
chk("  CI low",m['ci'][0],-1.05,0.06); chk("  CI high",m['ci'][1],-0.38,0.06)
chk("direct b",           m['b']['b'][1], 0.15,0.005); chk("  t",m['b']['b'][1]/m['b']['se'][1],0.62,0.05)
chk("total b",            m['c']['b'][1],-0.54,0.005); chk("  t",m['c']['b'][1]/m['c']['se'][1],-2.11,0.05)

print("\n"+"="*82); print("STUDY 3b  (PROCESS Model 7, W = central_logo)"); print("="*82)
b=pd.read_csv(D+'corrected/study3b_public.csv').query('attention_1==1').copy()
b['M']=b[FI].mean(axis=1); b['Y']=b[LB].mean(axis=1)
r=model7(b.free_dummy,b.central_logo,b.M,b.Y,[0,1])
chk("interaction dR2",r['dR2'],.02,.005); chk("  F(1,277)",r['F'],6.23,0.05)
for w,name,bw,sw,tw in [(0,'bee',-0.60,0.23,-2.57)]:
    e,s,df=simple_slope(b.free_dummy,b.central_logo,b.M,w)
    chk(f"simple slope ({name})",e,bw,0.005); chk("  SE",s,sw,0.005); chk("  t",e/s,tw,0.05)
print(f"  [参考] M(bee): 無償={b.query('central_logo==0 and free_dummy==1').M.mean():.2f} 有償={b.query('central_logo==0 and free_dummy==0').M.mean():.2f}  記載=3.72 vs 4.31")

print("\n"+"="*82); print("STUDY 3c  (PROCESS Model 7, W = source_official)"); print("="*82)
c=pd.read_csv(D+'corrected/study3c_public.csv').query('attention_1==1').copy()
c['M']=c[FI].mean(axis=1); c['Y']=c[LB].mean(axis=1)
r=model7(c.free_dummy,c.source_official,c.M,c.Y,[0,1])
chk("interaction dR2",r['dR2'],.01,.005); chk("  F(1,278)",r['F'],4.02,0.05)
for w,name,bw,sw,tw,lo,hi in [(0,'news',-0.95,0.23,-4.20,-1.40,-0.50),(1,'official',-0.32,0.22,-1.46,-0.75,0.11)]:
    e,s,df=simple_slope(c.free_dummy,c.source_official,c.M,w)
    chk(f"simple slope ({name})",e,bw,0.005); chk("  SE",s,sw,0.005); chk("  t",e/s,tw,0.05)
    tc=tdist.ppf(.975,df); chk("  CI low",e-tc*s,lo,0.01); chk("  CI high",e+tc*s,hi,0.01)
chk("cond indirect (news)",r['cond'][0]['effect'],-0.76,0.005)
chk("cond indirect (official)",r['cond'][1]['effect'],-0.26,0.005)
chk("index of mod med",r['index'],0.51,0.005)
d=ols(c.Y,[c.free_dummy,c.M]); chk("direct b",d['b'][1],0.38,0.005); chk("  SE",d['se'][1],0.14,0.005)
chk("  t",d['b'][1]/d['se'][1],2.62,0.05)

print("\n"+"="*82); print("STUDY 2  (PROCESS Model 7, W = physical)"); print("="*82)
s2=pd.read_csv(D+'corrected/study2_public.csv').query('attention_1==1').copy()
s2['M']=s2[['loss_prod_1','loss_prod_2','loss_prod_3']].mean(axis=1); s2['Y']=s2[LB].mean(axis=1)
r=model7(s2.free_dummy,s2.physical,s2.M,s2.Y,[0,1])
chk("interaction dR2",r['dR2'],.04,.005); chk("  F(1,276)",r['F'],11.49,0.05)
for w,name,bw,sw,tw,lo,hi in [(1,'physical',0.91,0.23,3.87,0.45,1.37),(0,'digital',-0.26,0.25,-1.02,-0.75,0.24)]:
    e,s,df=simple_slope(s2.free_dummy,s2.physical,s2.M,w)
    chk(f"simple slope ({name})",e,bw,0.005); chk("  SE",s,sw,0.005); chk("  t",e/s,tw,0.05)
    tc=tdist.ppf(.975,df); chk("  CI low",e-tc*s,lo,0.01); chk("  CI high",e+tc*s,hi,0.01)
chk("index of mod med",r['index'],0.80,0.005)
chk("indirect (physical)",r['cond'][1]['effect'],0.63,0.005)
chk("indirect (digital)",r['cond'][0]['effect'],-0.18,0.005)
d=ols(s2.Y,[s2.free_dummy,s2.M]); chk("direct b",d['b'][1],0.39,0.005); chk("  t",d['b'][1]/d['se'][1],2.65,0.05)

print("\n"+"="*82)
print(f"合計: 一致 {len(OK)} / 不一致 {len(NG)}")
if NG:
    print("\n■ 不一致の一覧")
    for l,g,w,d in NG: print(f"   {l:<46} 再計算={g:>8.3f} 記載={w:>8.3f} 差={d:.3f}")
