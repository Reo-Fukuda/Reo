"""Construct-validity battery for one study: descriptives, alpha, CFA, AVE/HTMT."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Reo/e99be4da-60e7-5b44-a895-52d93e57bcd5/scratchpad/analysis')
from cfa import fit_cfa, alpha, htmt
from scipy.stats import chi2 as c2, pearsonr

def run(name, df, blocks_named, exclude_note=""):
    cols = [c for _, items in blocks_named for c in items]
    X = df[cols].astype(float)
    idx, k = [], 0
    for _, items in blocks_named:
        idx.append(list(range(k, k + len(items)))); k += len(items)
    print(f"\n{'='*72}\n{name}   N = {len(df)}   {exclude_note}\n{'='*72}")
    print("Item descriptives:")
    for (fac, items), ii in zip(blocks_named, idx):
        for c in items:
            print(f"  {fac:<32s} {c:<16s} M={X[c].mean():5.3f} SD={X[c].std(ddof=1):5.3f}")
    print("\nCronbach's alpha:")
    for (fac, items) in blocks_named:
        print(f"  {fac:<32s} alpha = {alpha(df[items]):.3f}  (k={len(items)})")
    print("\nItem correlations:")
    print(X.corr().round(3).to_string())

    mk = fit_cfa(X.values, idx)
    m1 = fit_cfa(X.values, [list(range(k))])
    for lab, m in [(f"{len(idx)}-factor", mk), ("1-factor", m1)]:
        star = "" if m['p'] > .05 else "*"
        print(f"\n{lab} CFA (converged={m['converged']}): "
              f"chi2({m['df']}) = {m['chi2']:.2f}{star}, p = {m['p']:.4f}")
        print(f"   CFI = {m['cfi']:.3f}  TLI = {m['tli']:.3f}  "
              f"RMSEA = {m['rmsea']:.3f}  SRMR = {m['srmr']:.3f}")
        ld = m['loadings']
        for j, (fac, items) in enumerate(blocks_named if lab != "1-factor" else [("single factor", cols)]):
            jj = j if lab != "1-factor" else 0
            print(f"   {fac}: " + ", ".join(f"{c}={ld[cols.index(c), jj]:.3f}" for c in items))
        print(f"   AVE = {np.round(m['ave'],3)}   CR = {np.round(m['cr'],3)}")

    dchi, ddf = m1['chi2'] - mk['chi2'], m1['df'] - mk['df']
    print(f"\nModel comparison: Dchi2({ddf}) = {dchi:.2f}, p = {1-c2.cdf(dchi,ddf):.3g}")
    if len(idx) == 2:
        r = mk['phi'][0,1]
        print(f"Latent factor correlation r = {r:.3f}")
        print(f"sqrt(AVE) = {np.round(np.sqrt(mk['ave']),3)}  -> Fornell-Larcker "
              f"{'satisfied' if all(np.sqrt(mk['ave']) > abs(r)) else 'NOT satisfied'}")
        h = htmt(X.values, idx)
        print(f"HTMT = {h:.3f}  -> {'below' if h < .85 else 'ABOVE'} the .85 criterion")
    return mk, m1
