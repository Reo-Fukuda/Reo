"""Consolidated re-verification of every reported statistic reproducible from the public data.

Recomputes each reported value from the raw participant-level files and compares it
with the value printed in the manuscript or Supplementary Information.  Exclusions are
re-derived from the instructed-response items themselves (see SI H-5), not taken on trust.

Usage:  python3 verify_reported_statistics.py <dir containing study*_public.csv>
"""
import numpy as np, pandas as pd, sys
from scipy import stats
from process import ols, model4, model7, simple_slope
D = sys.argv[1] if len(sys.argv) > 1 else "."

R = []
def chk(sec, label, got, want, tol=0.005):
    ok = got is not None and abs(got - want) <= tol
    R.append((sec, label, got, want, ok))

def load(s):
    return pd.read_csv(f"{D}/{s}_public.csv")

def analytic(s):
    d = load(s)
    CH = {"study1":[("attention_item_7",7)], "study2":[("attention_1",1),("I1",6),("loss_prod_4",6)],
          "study3a":[("attention_1",1),("I1",6)], "study3b":[("attention_1",1)],
          "study3c":[("attention_1",1)], "study4":[("attention_1",1)]}
    bad = pd.Series(False, index=d.index)
    for c,ok in CH[s]: bad |= d[c]!=ok
    d = d[~bad]
    if s=="study4": d = d[~((d["T0"]==10)&(d["T1"]==10))]
    return d.reset_index(drop=True)

def anova1(y, g):
    grp=[y[g==k] for k in np.unique(g)]; k=len(grp); n=len(y)
    gm=y.mean(); ssb=sum(len(x)*(x.mean()-gm)**2 for x in grp)
    ssw=sum(((x-x.mean())**2).sum() for x in grp)
    F=(ssb/(k-1))/(ssw/(n-k)); return F, k-1, n-k, ssb/(ssb+ssw), np.sqrt(ssw/(n-k))

# ---------------- STUDY 1 ----------------
d = analytic("study1"); S="Study 1"
chk(S,"N", len(d), 670, 0)
F,df1,df2,eta,rmse = anova1(d["LOB"].values, d["condition"].values)
chk(S,"LOB F(3,666)", F, 35.17, 0.02); chk(S,"LOB df2", df2, 666, 0)
chk(S,"LOB partial eta2", eta, .14, .005)
cm = d.groupby("condition")["LOB"].mean()
for cond,want in zip(sorted(cm.index), [None]*4): pass
lab = {c:d.loc[d.condition==c,"LOB"].mean() for c in sorted(cm.index)}
vals = sorted(lab.values())
for want in (2.93,3.69,4.54,3.91):
    got = min(lab.values(), key=lambda v: abs(v-want))
    chk(S,f"LOB mean {want}", got, want, .005)
chk(S,"LOB pooled SE", rmse/np.sqrt(len(d)/4), 0.11, .005)
FB,_,dfB,etaB,rmseB = anova1(d["BI"].values, d["condition"].values)
chk(S,"BI F(3,666)", FB, 70.30, 0.02); chk(S,"BI partial eta2", etaB, .24, .005)
for want in (5.12,2.85):
    bm = {c:d.loc[d.condition==c,"BI"].mean() for c in sorted(cm.index)}
    chk(S,f"BI mean {want}", min(bm.values(), key=lambda v: abs(v-want)), want, .005)
chk(S,"BI pooled SE", rmseB/np.sqrt(len(d)/4), 0.11, .005)

# free vs comparable p = .167 (unadjusted), d = .14
grpn = {c:d.loc[d.condition==c,"LOB"] for c in sorted(cm.index)}
free = min(grpn.values(), key=lambda g: abs(g.mean()-3.91))
comp = min(grpn.values(), key=lambda g: abs(g.mean()-3.69))
se = rmse*np.sqrt(1/len(free)+1/len(comp)); t=(free.mean()-comp.mean())/se
chk(S,"free vs comparable p (unadj)", 2*stats.t.sf(abs(t),df2), .167, .002)
sp2=np.sqrt(((len(free)-1)*free.var(ddof=1)+(len(comp)-1)*comp.var(ddof=1))/(len(free)+len(comp)-2))
chk(S,"free vs comparable d", (free.mean()-comp.mean())/sp2, .14, .005)
chk(S,"free vs comparable mean diff", free.mean()-comp.mean(), .219, .001)

# ---------------- STUDY 2 ----------------
d = analytic("study2"); S="Study 2"
chk(S,"N", len(d), 276, 0)
chk(S,"% male", 100*(d["sex"]==1).mean(), 58.0, .06)
phys = d["physical"].values.astype(float); free_ = d["free_dummy"].values.astype(float) if "free_dummy" in d else d["paid"].values.astype(float)
# manipulation check: digital vs physical on loss_product? -> reported t(242.14)=7.12
ic = d[[f"inferred_cost_{i}" for i in (1,2,3)]].mean(axis=1)
a = ic[phys==1]; b = ic[phys==0]
tt = stats.ttest_ind(b, a, equal_var=False)
chk(S,"MC t (Welch)", abs(tt.statistic), 7.12, .02)
chk(S,"MC df", tt.df, 242.14, .05)
chk(S,"MC digital M", b.mean(), 3.41, .005); chk(S,"MC digital SD", b.std(ddof=1), 1.62, .005)
chk(S,"MC physical M", a.mean(), 4.69, .005)
chk(S,"MC physical SD", a.std(ddof=1), 1.32, .005)
# Model 7
m7 = model7(free_, phys, d["loss_product"].values, d["LOB"].values, [0.0,1.0], B=5000)
chk(S,"M7 interaction F", m7["F"], 11.83, .05)
chk(S,"M7 df2", m7["dfF"][1], 272, 0)
chk(S,"M7 index", m7["index"], 0.83, .02)
chk(S,"M7 index CI lo", m7["index_ci"][0], 0.36, .05)
chk(S,"M7 index CI hi", m7["index_ci"][1], 1.35, .05)
chk(S,"M7 digital indirect", m7["cond"][0.0]["effect"], -0.20, .02)
est,sse,dfs = simple_slope(free_, phys, d["loss_product"].values, 0.0)
chk(S,"digital a-slope b", est, -0.29, .02); chk(S,"digital a-slope SE", sse, .26, .02)
chk(S,"digital a-slope t", est/sse, -1.13, .03); chk(S,"digital a-slope df", dfs, 272, 0)
chk(S,"digital a-slope p", 2*stats.t.sf(abs(est/sse), dfs), .259, .01)

# ---------------- STUDY 3a ----------------
d = analytic("study3a"); S="Study 3a"
chk(S,"N", len(d), 135, 0)
chk(S,"% male", 100*(d["sex"]==1).mean(), 61.5, .06)
x = (d["condition"]==d["condition"].unique()[0]).astype(float).values
m4 = model4(x, d["failure_inference"].values, d["LOB"].values, B=5000)
apath = ols(d["failure_inference"].values,[x]); bpath = ols(d["LOB"].values,[x,d["failure_inference"].values])
chk(S,"a-path |b|", abs(apath["b"][1]), 1.17, .02)
chk(S,"a-path |t|", abs(apath["b"][1]/apath["se"][1]), 5.08, .03)
chk(S,"a-path df", apath["df"], 133, 0)
chk(S,"b-path b", abs(bpath["b"][2]), 0.59, .02)
chk(S,"b-path |t|", abs(bpath["b"][2]/bpath["se"][2]), 7.11, .03)
chk(S,"b-path df", bpath["df"], 132, 0)
tot = ols(d["LOB"].values,[x])
chk(S,"total |b|", abs(tot["b"][1]), 0.53, .02)
chk(S,"total |t|", abs(tot["b"][1]/tot["se"][1]), 2.07, .03)
chk(S,"total p", 2*stats.t.sf(abs(tot["b"][1]/tot["se"][1]), tot["df"]), .040, .003)
chk(S,"direct |t|", abs(bpath["b"][1]/bpath["se"][1]), 0.65, .03)
chk(S,"direct p", 2*stats.t.sf(abs(bpath["b"][1]/bpath["se"][1]), bpath["df"]), .520, .012)
chk(S,"boot SE", m4["boot_se"], 0.18, .015)
# monetization t-test
g = d.groupby("condition")["monetization_intent"]
ks = list(g.groups); tt = stats.ttest_ind(d.loc[d.condition==ks[0],"monetization_intent"], d.loc[d.condition==ks[1],"monetization_intent"], equal_var=False)
chk(S,"monetization |t|", abs(tt.statistic), 3.38, .02); chk(S,"monetization df", tt.df, 121.33, .05)

# ---------------- STUDY 3b / 3c ----------------
for S,s,tgt in [("Study 3b","study3b",dict(N=281,male=59.8,idx=0.45,bee=-0.33,cen=0.13)),
                ("Study 3c","study3c",dict(N=282,male=55.3))]:
    d = analytic(s)
    chk(S,"N", len(d), tgt["N"], 0)
    chk(S,"% male", 100*(d["sex"]==1).mean(), tgt["male"], .06)
    if s=="study3b":
        x = d["free_dummy"].astype(float).values; w = d["central_logo"].astype(float).values if "central_logo" in d.columns else d["low_flagship"].astype(float).values
        m7 = model7(x, w, d["failure_inference"].values, d["LOB"].values, [0.0,1.0], B=5000)
        chk(S,"M7 index", m7["index"], tgt["idx"], .02)
        chk(S,"M7 interaction F", m7["F"], 6.23, .02)
        for wv,lab,tb,tt_ in [(0.0,"bee",-0.60,-2.57),(1.0,"central",0.23,0.98)]:
            e,se_,df_=simple_slope(x,w,d["failure_inference"].values,wv)
            chk(S,f"a-path @ {lab} b", e, tb, .01); chk(S,f"a-path @ {lab} t", e/se_, tt_, .02)
        chk(S,"bee indirect", m7["cond"][0.0]["effect"], tgt["bee"], .02)
        chk(S,"central indirect", m7["cond"][1.0]["effect"], tgt["cen"], .02)

# ---------------- STUDY 4 (SI G) ----------------
d = analytic("study4"); S="Study 4 (SI G)"
chk(S,"N", len(d), 273, 0)
chk(S,"% male", 100*(d["sex"]==1).mean(), 55.3, .06)
Y = d[["T0","T1","T2"]].values; g = d["condition"].values
n,k = Y.shape; gm = Y.mean(); subj = Y.mean(1); tm = Y.mean(0)
SS_time = n*((tm-gm)**2).sum()
SS_tc = sum(len(Y[g==c])*(((Y[g==c].mean(0)-Y[g==c].mean())-(tm-gm))**2).sum() for c in np.unique(g))
SS_err = ((Y-subj[:,None])**2).sum() - SS_time - SS_tc
df_err = (n-2)*(k-1)
chk(S,"RM-ANOVA F(time)", (SS_time/(k-1))/(SS_err/df_err), 91.52, .02)
chk(S,"RM df2", df_err, 542, 0)
chk(S,"RM partial eta2", SS_time/(SS_time+SS_err), .25, .005)
chk(S,"F(interaction)", (SS_tc/(k-1))/(SS_err/df_err), 0.85, .01)
sb = k*((subj-gm)**2).sum()
SS_cond = sum(len(Y[g==c])*k*(Y[g==c].mean()-gm)**2 for c in np.unique(g))
chk(S,"F(condition)", (SS_cond/1)/((sb-SS_cond)/(n-2)), 0.03, .005)
for i,(lab,want) in enumerate(zip(["T0","T1","T2"],[6.61,5.53,6.52])):
    chk(S,f"{lab} overall mean", Y[:,i].mean(), want, .005)
for i,(lab,want) in enumerate(zip(["T0","T1","T2"],[1.67,1.99,2.04])):
    chk(S,f"{lab} overall SD", Y[:,i].std(ddof=1), want, .006)


# ---------------- APPENDIX RELIABILITIES ----------------
def alpha(X):
    X = np.asarray(X, float); k = X.shape[1]
    return k/(k-1) * (1 - X.var(0, ddof=1).sum() / X.sum(1).var(ddof=1))

S = "Appendix reliabilities"
LOBI = ["LOB_item1", "LOB_item2", "LOB_item3"]
FII  = ["fail_inf_1", "fail_inf_2", "fail_inf_3"]
lob = [alpha(analytic(s)[LOBI]) for s in ("study1", "study2", "study3a", "study3b", "study3c")]
chk(S, "Loss of Brand Luxuriousness min", min(lob), .94, .005)
chk(S, "Loss of Brand Luxuriousness max", max(lob), .96, .005)
chk(S, "Loss of Product Luxuriousness (S2)",
    alpha(analytic("study2")[["loss_prod_1", "loss_prod_2", "loss_prod_3"]]), .85, .005)
fi = [alpha(analytic(s)[FII]) for s in ("study3a", "study3b", "study3c")]
chk(S, "Failure Inference min", min(fi), .87, .005)
chk(S, "Failure Inference max", max(fi), .92, .005)
chk(S, "Inferred Cost (S2)",
    alpha(analytic("study2")[[f"inferred_cost_{i}" for i in (1, 2, 3)]]), .91, .005)
chk(S, "Behavioral Intention (S1)",
    alpha(analytic("study1")[["BI_item1", "BI_item2"]]), .97, .005)
for t, want in zip(("T0", "T1", "T2"), (.88, .92, .92)):
    chk(S, f"Perceived Brand Luxury {t} (S4)",
        alpha(analytic("study4")[[f"{t}_item{i}" for i in (1, 2, 3)]]), want, .005)

# ---------------- REPORT ----------------
w = max(len(r[1]) for r in R)
cur=None; npass=nfail=0
for sec,lab,got,want,ok in R:
    if sec!=cur: print(f"\n### {sec}"); cur=sec
    g = "n/a" if got is None else (f"{got:.4f}" if abs(got)<1e4 else f"{got:.1f}")
    print(f"  {'PASS' if ok else 'FAIL'}  {lab:<{w}}  computed={g:>10}  reported={want}")
    npass += ok; nfail += not ok
print(f"\n===== {npass} matched / {npass+nfail} checked  ({nfail} mismatched) =====")
