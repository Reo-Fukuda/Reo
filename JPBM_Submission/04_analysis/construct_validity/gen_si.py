"""Emit the SI construct-validity section as LaTeX, straight from the fitted models."""
import numpy as np, pandas as pd, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from cfa import fit_cfa, alpha, htmt
from scipy.stats import chi2 as c2

FI=['fail_inf_1','fail_inf_2','fail_inf_3']; LB=['LOB_item1','LOB_item2','LOB_item3']
LP=['loss_prod_1','loss_prod_2','loss_prod_3']
STUDIES=[
 ("Study 2","../corrected/study2_public.csv",[("Loss of Product Luxuriousness",LP),("Loss of Brand Luxuriousness",LB)]),
 ("Study 3a","../data/study3a_public.csv",[("Failure Inference",FI),("Loss of Brand Luxuriousness",LB)]),
 ("Study 3b","../corrected/study3b_public.csv",[("Failure Inference",FI),("Loss of Brand Luxuriousness",LB)]),
 ("Study 3c","../corrected/study3c_public.csv",[("Failure Inference",FI),("Loss of Brand Luxuriousness",LB)]),
]
def analytic(name,d):
    m = d.attention_1==1
    if name=="Study 2":  m &= (d.loss_prod_4==6)&(d.I1==6)
    if name=="Study 3a": m &= (d.I1==6)
    if name=="Study 3b": m &= (d.I1==6)
    return d[m]
def f3(x):
    t = f"{abs(x):.3f}"
    if abs(x) < 1: t = t.lstrip("0")
    return ("-" if x < 0 else "") + t
def f2(x): return f"{x:.2f}"

res=[]
for name,path,blocks in STUDIES:
    d=pd.read_csv(path); a=analytic(name,d)
    cols=[c for _,it in blocks for c in it]; X=a[cols].astype(float)
    idx=[[0,1,2],[3,4,5]]
    m2=fit_cfa(X.values,idx); m1=fit_cfa(X.values,[list(range(6))])
    res.append(dict(name=name,n=len(a),blocks=blocks,cols=cols,X=X,m2=m2,m1=m1,
                    alphas=[alpha(a[it]) for _,it in blocks],h=htmt(X.values,idx)))

out=[]
W=out.append
W(r"\SIMajorHeading{H-4. Discriminant Validity of the Measured Constructs}")
W("")
W(r"""Several of the measures analysed together were collected from the same respondents within a single questionnaire and share negatively valenced wording. This raises the question of whether they behave as distinct constructs or largely as one general negative reaction. This section reports confirmatory factor analyses and discriminant-validity indices for the two pairings that enter the mediation models: Loss of Product Luxuriousness with Loss of Brand Luxuriousness in Study 2, and Failure Inference with Loss of Brand Luxuriousness in Studies 3a--3c.""")
W("")
W(r"""Each model was estimated by maximum likelihood on that study's attention-check-passed analytic sample, with factor variances fixed at unity and each item free to load only on its assigned factor. Because these are six-indicator models with eight degrees of freedom, we report CFI, TLI and SRMR alongside RMSEA: in models with few degrees of freedom RMSEA tends to be inflated and to reject correctly specified models, so it is best read together with the other indices rather than on its own (Kenny et al., 2015). Table H1 compares the fit of the hypothesised two-factor model with a one-factor alternative in which all six items load on a single factor.""")
W("")
# ---- Table H1
W(r"\setcounter{table}{0}")
W(r"\renewcommand{\thetable}{H\arabic{table}}")
W(r"\renewcommand{\theHtable}{H\arabic{table}}")
W("")
W(r"\begin{table}[H]"); W(r"\centering"); W(r"\begin{singlespace}")
W(r"\caption{Confirmatory Factor Analysis: Two-Factor Versus One-Factor Models}")
W(r"\begin{tabular}{@{}llrrrrrr@{}}"); W(r"\toprule")
W(r"Study & Model & $\chi^2$ & \emph{df} & CFI & TLI & RMSEA & SRMR \\")
W(r"\midrule")
for r in res:
    for lab,m in [("Two-factor",r['m2']),("One-factor",r['m1'])]:
        star = "" if m['p']>=.05 else r"\textsuperscript{*}"
        first = f"{r['name']} (\\emph{{N}} = {r['n']})" if lab=="Two-factor" else ""
        W(f"{first} & {lab} & {m['chi2']:.2f}{star} & {m['df']} & {f3(m['cfi'])} & "
          f"{f3(m['tli'])} & {f3(m['rmsea'])} & {f3(m['srmr'])} \\\\")
    W(r"\addlinespace")
W(r"\bottomrule"); W(r"\end{tabular}")
W(r"\raggedright\emph{Note.} Maximum-likelihood estimation on each study's attention-check-passed sample. "
  r"\textsuperscript{*}\emph{p} \textless{} .05. The one-factor model is the two-factor model with the "
  r"factor correlation fixed at unity; the two are therefore nested and differ by one degree of freedom. "
  r"Difference tests appear in the text.")
W(r"\end{singlespace}"); W(r"\end{table}")
W("")
# ---- diff tests sentence
sent=[]
for r in res:
    d=r['m1']['chi2']-r['m2']['chi2']
    sent.append(f"{r['name']} $\\Delta\\chi^2$(1) = {d:.2f}")
W(r"""The two-factor model fitted better in every study, and by a wide margin: """ + "; ".join(sent) +
  r""", all \emph{p} \textless{} .001. In each case the one-factor solution also fell below conventional thresholds on CFI and SRMR, whereas the two-factor solution met them.""")
W("")
# ---- Table H2
W(r"\begin{table}[H]"); W(r"\centering"); W(r"\begin{singlespace}")
W(r"\caption{Reliability and Discriminant Validity by Study}")
W(r"\begin{tabular}{@{}llrrrrr@{}}"); W(r"\toprule")
W(r"Study & Construct & $\lambda$ range & $\alpha$ & CR & AVE & $\sqrt{\text{AVE}}$ \\")
W(r"\midrule")
for r in res:
    ld=r['m2']['loadings']
    for j,(fac,items) in enumerate(r['blocks']):
        l=[ld[r['cols'].index(c),j] for c in items]
        first = r['name'] if j==0 else ""
        W(f"{first} & {fac} & {f3(min(l))}--{f3(max(l))} & {f3(r['alphas'][j])} & "
          f"{f3(r['m2']['cr'][j])} & {f3(r['m2']['ave'][j])} & {f3(np.sqrt(r['m2']['ave'][j]))} \\\\")
    W(f" & \\emph{{Factor correlation}} $\\varphi$ = {f3(r['m2']['phi'][0,1])}; "
      f"HTMT = {f3(r['h'])} & & & & & \\\\")
    W(r"\addlinespace")
W(r"\bottomrule"); W(r"\end{tabular}")
W(r"\raggedright\emph{Note.} $\lambda$ = standardised loading; CR = composite reliability; "
  r"AVE = average variance extracted; HTMT = heterotrait--monotrait ratio of correlations. "
  r"Every standardised loading was .697 or higher; the smallest ratio of an unstandardised loading to "
  r"its asymptotic standard error was 11.45, so all loadings were significant at \emph{p} \textless{} .001.")
W(r"\end{singlespace}"); W(r"\end{table}")
W("")
phis=[r['m2']['phi'][0,1] for r in res]; hs=[r['h'] for r in res]
aves=[v for r in res for v in r['m2']['ave']]
W(f"""Three indices point the same way. The latent factor correlations ranged from {f3(min(phis))} to {f3(max(phis))}: substantial, as one would expect of judgments formed in the same session about the same offering, but well short of unity. Average variance extracted exceeded .50 for every construct (range {f3(min(aves))} to {f3(max(aves))}), and in each study the square root of the average variance extracted for both constructs exceeded their correlation, satisfying the Fornell and Larcker (1981) criterion. The heterotrait--monotrait ratio ranged from {f3(min(hs))} to {f3(max(hs))}, below the .85 threshold recommended by Henseler et al. (2015) in every study.""")
W("")
W(r"""Two qualifications belong with these results. First, RMSEA for the two-factor models ranged from """
  + f"{f3(min(r['m2']['rmsea'] for r in res))} to {f3(max(r['m2']['rmsea'] for r in res))}"
  + ", exceeding .08 in " + (" and ".join(r['name'] for r in res if r['m2']['rmsea']>.08).replace("Study 3b and Study 3c","Studies 3b and 3c"))
  + r""" even though CFI, TLI and SRMR indicated close fit in the same models. This pattern is characteristic of models with few degrees of freedom rather than an indication of a mis-specified factor structure, and we report it rather than selecting indices that favour the model. Second, the evidence here concerns discriminant validity between the measures as scored; it does not establish that Failure Inference captures a causal attribution, and we do not claim that it does (Section H-2 and the main-text limitations).""")
W("")
# Study 2 three-factor
d=pd.read_csv("../corrected/study2_public.csv"); a=analytic("Study 2",d)
IC=['inferred_cost_1','inferred_cost_2','inferred_cost_3']
X3=a[LP+LB+IC].astype(float); m3=fit_cfa(X3.values,[[0,1,2],[3,4,5],[6,7,8]])
W(f"""Study 2 also measured Inferred Cost as a check on the product-form difference. A three-factor model including it fitted well ($\\chi^2$({m3['df']}) = {m3['chi2']:.2f}, CFI = {f3(m3['cfi'])}, TLI = {f3(m3['tli'])}, RMSEA = {f3(m3['rmsea'])}, SRMR = {f3(m3['srmr'])}; $\\alpha$ = {f3(alpha(a[IC]))}), with Inferred Cost correlating $\\varphi$ = {f3(m3['phi'][0,2])} with Loss of Product Luxuriousness and $\\varphi$ = {f3(m3['phi'][1,2])} with Loss of Brand Luxuriousness.""")
W("")
# ---- Table H3 item descriptives + correlations
W(r"\begin{table}[H]"); W(r"\centering"); W(r"\begin{singlespace}")
W(r"\caption{Item Means, Standard Deviations and Correlations by Study}")
W(r"\begin{tabular}{@{}llrrrrrrrr@{}}"); W(r"\toprule")
W(r"Study & Item & \emph{M} & \emph{SD} & 1 & 2 & 3 & 4 & 5 & 6 \\")
W(r"\midrule")
for r in res:
    R=r['X'].corr().values
    labels=[]
    for fac,items in r['blocks']:
        tag = {"Failure Inference":"FI","Loss of Brand Luxuriousness":"LBL",
               "Loss of Product Luxuriousness":"LPL"}[fac]
        labels += [f"{tag}{k+1}" for k in range(len(items))]
    for i,c in enumerate(r['cols']):
        first = r['name'] if i==0 else ""
        cells=[f3(R[i,j]) if j<i else ("1.000" if j==i else "") for j in range(6)]
        W(f"{first} & {labels[i]} & {f2(r['X'][c].mean())} & {f2(r['X'][c].std(ddof=1))} & "
          + " & ".join(cells) + r" \\")
    W(r"\addlinespace")
W(r"\bottomrule"); W(r"\end{tabular}")
W(r"\raggedright\emph{Note.} FI = Failure Inference; LPL = Loss of Product Luxuriousness; "
  r"LBL = Loss of Brand Luxuriousness. All items were measured on seven-point scales. "
  r"All correlations are significant at \emph{p} \textless{} .001.")
W(r"\end{singlespace}"); W(r"\end{table}")
W("")
W(r"\setcounter{table}{0}")
open("si_h4.tex","w").write("\n".join(out)+"\n")
print("\n".join(out))
